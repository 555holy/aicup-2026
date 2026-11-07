#!/usr/bin/env python
"""執行 notebook，邊跑邊保存結果，並記錄資源用量。

用法：python scripts/run_notebook.py <notebook.ipynb> --mode trial|full --run-id <名稱>

輸出都在 runs/<名稱>/：
  <notebook>.ipynb  保留輸出的 notebook，每個 cell 跑完就存一次
  run.log           即時輸出，可用 tail -f 觀看
  resources.csv     每 5 秒一筆的 RAM、swap、GPU 用量
  summary.txt       commit、耗時、資源峰值、結果

可用記憶體連續 15 秒低於門檻時會主動停止，避免整個 WSL 當掉。
"""
import argparse
import os
import subprocess
import sys
import threading
import time

import nbformat
import psutil
from nbclient import NotebookClient

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
SAMPLE_SECONDS = 5
LOW_MEMORY_SAMPLES = 3


class LoggingClient(NotebookClient):
    """把 notebook 的文字輸出同步寫到 log。"""
    log_file = None

    def process_message(self, msg, cell, cell_index):
        if self.log_file is not None:
            if msg['msg_type'] == 'stream':
                self.log_file.write(msg['content']['text'])
                self.log_file.flush()
            elif msg['msg_type'] == 'error':
                self.log_file.write('ERROR %s: %s\n' % (msg['content']['ename'],
                                                        msg['content']['evalue']))
                self.log_file.flush()
        return super().process_message(msg, cell, cell_index)


class Monitor(threading.Thread):
    def __init__(self, path, min_available_mib, log_file):
        super().__init__(daemon=True)
        self.path = path
        self.min_available_mib = min_available_mib
        self.log_file = log_file
        self.halt = threading.Event()
        self.peak_ram = self.peak_swap = self.peak_gpu = 0
        self.stopped_for_memory = False

    def gpu_memory(self):
        try:
            out = subprocess.run(
                ['nvidia-smi', '--query-gpu=memory.used,utilization.gpu',
                 '--format=csv,noheader,nounits'],
                capture_output=True, text=True, timeout=10, check=True).stdout
            used, util = out.strip().splitlines()[0].split(',')
            return int(used), int(util)
        except (OSError, ValueError, IndexError, subprocess.SubprocessError):
            return 0, 0

    def kill_kernel(self):
        for child in psutil.Process().children(recursive=True):
            try:
                child.kill()
            except psutil.NoSuchProcess:
                pass

    def run(self):
        low = 0
        with open(self.path, 'w') as f:
            f.write('time,ram_used_mib,ram_available_mib,swap_used_mib,gpu_mem_mib,gpu_util\n')
            while not self.halt.is_set():
                mem = psutil.virtual_memory()
                available = mem.available // 2**20
                used = (mem.total - mem.available) // 2**20
                swap = psutil.swap_memory().used // 2**20
                gpu, util = self.gpu_memory()
                self.peak_ram = max(self.peak_ram, used)
                self.peak_swap = max(self.peak_swap, swap)
                self.peak_gpu = max(self.peak_gpu, gpu)
                f.write('%s,%d,%d,%d,%d,%d\n' % (time.strftime('%F %T'), used, available,
                                                 swap, gpu, util))
                f.flush()
                low = low + 1 if available < self.min_available_mib else 0
                if low >= LOW_MEMORY_SAMPLES:
                    self.stopped_for_memory = True
                    self.log_file.write('STOP 可用記憶體只剩 %d MiB，主動停止\n' % available)
                    self.log_file.flush()
                    self.kill_kernel()
                    return
                self.halt.wait(SAMPLE_SECONDS)


def git_state():
    run = lambda *a: subprocess.run(['git', *a], cwd=REPO, capture_output=True,
                                    text=True).stdout.strip()
    return run('rev-parse', '--short', 'HEAD'), bool(run('status', '--porcelain'))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('notebook')
    parser.add_argument('--mode', choices=['trial', 'full'], required=True)
    parser.add_argument('--run-id', required=True)
    parser.add_argument('--min-available-mib', type=int, default=800)
    args = parser.parse_args()

    run_dir = os.path.join(REPO, 'runs', args.run_id)
    if os.path.exists(run_dir):
        sys.exit('%s 已存在，請換一個 --run-id，避免覆蓋之前的結果' % run_dir)
    os.makedirs(run_dir)

    source = os.path.join(REPO, args.notebook)
    output = os.path.join(run_dir, os.path.basename(args.notebook))
    nb = nbformat.read(source, as_version=4)

    def save(**_):
        tmp = output + '.tmp'
        nbformat.write(nb, tmp)
        os.replace(tmp, output)

    os.environ['RUN_MODE'] = args.mode
    os.environ['RUN_DIR'] = os.path.relpath(run_dir, REPO)

    commit, dirty = git_state()
    start = time.time()
    status = 'ok'
    with open(os.path.join(run_dir, 'run.log'), 'w') as log_file:
        monitor = Monitor(os.path.join(run_dir, 'resources.csv'),
                          args.min_available_mib, log_file)
        monitor.start()
        client = LoggingClient(nb, timeout=None, kernel_name='python3',
                               resources={'metadata': {'path': REPO}})
        client.log_file = log_file
        client.on_cell_executed = save
        try:
            client.execute()
        except Exception as e:  # 任何失敗都要留下 summary 和已跑完的輸出
            status = 'failed: %s' % str(e).strip().splitlines()[-1][:300]
            log_file.write('FAILED %s\n' % status)
        finally:
            monitor.halt.set()
            monitor.join()
            save()
    if monitor.stopped_for_memory:
        status = 'stopped: low memory'

    minutes = (time.time() - start) / 60
    summary = [
        'notebook: %s' % args.notebook,
        'mode: %s' % args.mode,
        'commit: %s%s' % (commit, ' (有未 commit 的修改)' if dirty else ''),
        'started: %s' % time.strftime('%F %T', time.localtime(start)),
        'minutes: %.1f' % minutes,
        'peak_ram_mib: %d' % monitor.peak_ram,
        'peak_swap_mib: %d' % monitor.peak_swap,
        'peak_gpu_mem_mib: %d' % monitor.peak_gpu,
        'status: %s' % status,
    ]
    with open(os.path.join(run_dir, 'summary.txt'), 'w') as f:
        f.write('\n'.join(summary) + '\n')
    print('\n'.join(summary))
    return 0 if status == 'ok' else 1


if __name__ == '__main__':
    sys.exit(main())
