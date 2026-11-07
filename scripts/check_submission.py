#!/usr/bin/env python
"""上傳前檢查提交檔的格式。只檢查格式，不代表答案正確。

用法：python scripts/check_submission.py <submission.csv> [--tests-dir tests]
通過時結束碼為 0，有錯誤時為 1。子題由欄位名稱自動判斷。
"""
import argparse
import os
import sys

import pandas as pd

LEVELS = {'D', 'C', 'B', 'A', '1D', '2D', '3D', '4D', '5D', '6D'}
TOP_COLS = ['top_%d' % i for i in range(1, 6)]
SPLITS = {'pub_': 'public', 'priv_': 'private'}
EXPECTED_PER_SPLIT = 400
MAX_SHOWN = 20


def split_of(question_id):
    for prefix, split in SPLITS.items():
        if question_id.startswith(prefix):
            return split
    return None


def read_column(path, column):
    return set(pd.read_csv(path, usecols=[column], dtype=str,
                           keep_default_na=False)[column])


def check_questions(df, test_pattern, errors, warnings):
    """檢查題數、前綴、重複，以及題號是否和官方題目檔完全相同。"""
    ids = df['question_id']
    if len(df) != 2 * EXPECTED_PER_SPLIT:
        errors.append('總列數是 %d，應為 %d' % (len(df), 2 * EXPECTED_PER_SPLIT))

    for row, qid in enumerate(ids, 1):
        if split_of(qid) is None:
            errors.append('第 %d 列：%s 沒有 pub_ 或 priv_ 前綴' % (row, qid))
    for qid in ids[ids.duplicated()].unique():
        errors.append('題號重複：%s' % qid)

    for prefix, split in SPLITS.items():
        count = int(ids.str.startswith(prefix).sum())
        if count != EXPECTED_PER_SPLIT:
            errors.append('%s 開頭有 %d 題，應為 %d' % (prefix, count, EXPECTED_PER_SPLIT))

        path = test_pattern % split
        if not os.path.exists(path):
            warnings.append('找不到 %s，未比對 %s 題號' % (path, split))
            continue
        official = read_column(path, 'question_id')
        mine = {q for q in ids if q.startswith(prefix)}
        for qid in sorted(official - mine):
            errors.append('缺題：%s' % qid)
        for qid in sorted(mine - official):
            errors.append('官方題目檔沒有這一題：%s' % qid)


def check_rank(df, tests_dir, errors, warnings):
    check_questions(df, os.path.join(tests_dir, 'rank_prediction_test_%s.csv'),
                    errors, warnings)
    for row, (qid, rank) in enumerate(zip(df['question_id'], df['pred_rank']), 1):
        if rank not in LEVELS:
            errors.append('第 %d 列：%s 的等級 %r 不在 10 個等級內' % (row, qid, rank))


def check_player(df, tests_dir, errors, warnings):
    check_questions(df, os.path.join(tests_dir, 'player_identification_test_%s.csv'),
                    errors, warnings)
    pools = {}
    for split in SPLITS.values():
        path = os.path.join(tests_dir, 'player_identification_candidates_%s.csv' % split)
        if os.path.exists(path):
            pools[split] = read_column(path, 'player_id')
        else:
            warnings.append('找不到 %s，未比對 %s 候選玩家' % (path, split))

    for row, r in enumerate(df.to_dict('records'), 1):
        qid = r['question_id']
        split = split_of(qid)
        picks = [r[c] for c in TOP_COLS]
        if '' in picks:
            errors.append('第 %d 列：%s 有空白人選' % (row, qid))
        if len(set(picks)) != len(picks):
            errors.append('第 %d 列：%s 的 5 個人選有重複' % (row, qid))
        if split is None:
            continue
        prefix = 'pub_p_' if split == 'public' else 'priv_p_'
        for col, player in zip(TOP_COLS, picks):
            if not player:
                continue
            if not player.startswith(prefix):
                errors.append('第 %d 列：%s 的 %s 填了 %s，不屬於 %s 候選池'
                              % (row, qid, col, player, split))
            elif split in pools and player not in pools[split]:
                errors.append('第 %d 列：%s 的 %s 填了 %s，不在 %s 候選庫'
                              % (row, qid, col, player, split))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('submission')
    parser.add_argument('--tests-dir', default='tests')
    args = parser.parse_args()

    df = pd.read_csv(args.submission, dtype=str, keep_default_na=False)
    columns = list(df.columns)
    errors, warnings = [], []
    if columns == ['question_id', 'pred_rank']:
        check_rank(df, args.tests_dir, errors, warnings)
    elif columns == ['question_id'] + TOP_COLS:
        check_player(df, args.tests_dir, errors, warnings)
    else:
        errors.append('欄位不對：%s' % columns)

    for message in warnings:
        print('⚠️  ' + message)
    for message in errors[:MAX_SHOWN]:
        print('❌ ' + message)
    if len(errors) > MAX_SHOWN:
        print('... 還有 %d 個錯誤' % (len(errors) - MAX_SHOWN))
    if errors:
        print('❌ %s 未通過，共 %d 個錯誤' % (args.submission, len(errors)))
        return 1
    if warnings:
        print('⚠️  %s 已檢查的項目都通過，但有項目未比對，請先處理上面的警告'
              % args.submission)
        return 0
    print('✅ %s 通過，可以上傳' % args.submission)
    return 0


if __name__ == '__main__':
    sys.exit(main())
