# 實驗紀錄

## 目前狀態

- [x] 環境：RTX 5080（16 GB）、Python 3.10.12、PyTorch 2.11.0+cu128
- **範圍：只做玩家辨識**（2026-11-08 作業改成不用跑棋力預測；下面棋力預測的紀錄保留當參考）
- [x] 資料：訓練集 v1.1、玩家辨識測試集（`aicup2026_player_identification_tests_20261030.zip`，2026-11-08 放進 `tests/`，官方範例提交檔通過 `check_submission.py`）
- [ ] 試跑截圖（環境資訊、試跑輸出）
- [x] 完整訓練：玩家辨識（`baseline-player`，2026-11-08，提交檔已通過 `check_submission.py`）
- [ ] 提交 baseline、記錄 Public 分數與排行榜截圖
- [ ] 小改實驗
- [ ] 報告

## 交接事項

### 下一步：上傳 baseline（等使用者上傳）

`runs/baseline-player/submission_player.csv` 已通過 `check_submission.py`，由使用者上傳，記下 Public 分數並截排行榜圖。

### 完整訓練的實測（baseline-player）

- 時間共 124.3 分：抽特徵 24.2 分（999,997 局、0 局解析失敗、13.18 GB、平均 12.9 KB/檔）、訓練 5 輪各約 16.0 分、推論約 20 分（每份測試集的候選庫約 8.6 分）。
- 資源峰值：RAM 9,883 MiB、swap 2,935 MiB、GPU 2,479 MiB，沒有接近自動停止門檻。
- 提早停止的檢查沒有觸發（第 1 輪 train loss 0.4806 < 0.495）。
- `summary.txt` 標示「有未 commit 的修改」：`run_notebook.py` 用 `git status` 判斷，未追蹤的檔案也算在內，當時有未追蹤的 `runs/trial-player-infer/`，EXPERIMENTS.md 也在更新；notebook 和 commit `0076eb8` 相同。
- 機器沒有電池（Windows 偵測不到），接電源時不睡眠也不休眠，不用管蓋螢幕。

### 已知缺口

- **還沒有「只跑推論」的方式。** 現在重跑 notebook 會重新訓練（約 2 小時；特徵已存在會跳過抽取，約省 24 分）。只改推論的小改實驗要先補這個功能，可以直接載入 `runs/baseline-player/player-trained-models/best_model.pth`。
- 提交用的 CSV 和 `history.csv` 被 `.gitignore` 排除，只存在本機的 `runs/`，要另外保存並繳交。
- repo 是 private，如果用 GitHub 連結繳交程式，要先確認助教看得到。

### 使用者要做或決定的事

- 上傳 `runs/baseline-player/submission_player.csv`，記錄 Public 分數、截排行榜圖。
- 截試跑圖：`runs/trial-player/player-identification.ipynb`（2026-11-08 重跑的版本，含環境資訊、抽特徵、訓練、推論）。
- 決定小改實驗（尚未決定）。建議選不用重新訓練的，例如改變推論時使用的手數。

## 執行紀錄

| Run ID | 子題 | 模式 | Commit | 改了什麼 | 最佳 val | Public | 耗時 | 備註 |
|---|---|---|---|---|---|---|---|---|
| trial-rank（已刪除，範圍改變） | 棋力預測 | trial | 整理前（未 commit） | 每級 1,000 局、1 epoch | val acc 9.00% | — | 1.2 分 | 只驗證流程；RAM 峰值約 10.2 GB、GPU 約 9.5 GB |
| trial-player（舊版，已刪除；沒跑推論） | 玩家辨識 | trial | 整理前（未 commit） | 每級 1,000 局、200 步 | val loss 0.5268 | — | 0.7 分 | 只驗證流程，推論待測試集；RAM 峰值約 5.4 GB、GPU 約 2.4 GB |
| trial-player-infer（已刪除；沿用舊特徵沒有抽取） | 玩家辨識 | trial | 0076eb8 | 同 trial-player，加上真實測試集推論 | val loss 0.5268 | 不上傳 | 19.7 分 | 第一次跑通推論：800 列、通過 `check_submission.py`；每份測試集的候選庫約 8.5 分、查詢約 1 分；RAM 峰值約 7.0 GB、GPU 約 2.4 GB |
| baseline-player | 玩家辨識 | full | 0076eb8（EXPERIMENTS.md 有未 commit 修改） | 官方 baseline 設定：5 輪 × 15,000 步，用 val loss 挑模型 | val loss 0.3513（第 5 輪） | 待上傳 | 124.3 分 | 每輪 val loss 0.4662 → 0.3758 → 0.3608 → 0.3537 → 0.3513；800 列、通過 `check_submission.py`；RAM 峰值約 9.7 GB、swap 約 2.9 GB、GPU 約 2.4 GB |

## 和官方 baseline 的差異

- 棋力預測、玩家辨識：程式能切換試跑／完整模式；每個 epoch 存 `history.csv`；訓練前釋放棋譜資料；訓練異常時提早停止。
- 玩家辨識：保留 2% 玩家不參與訓練，用來算 val loss，並用它挑 `best_model.pth`（官方是用 train loss）。
- 訓練集用 v1.1；約 3.6% 棋局（讓 2 子以上）的棋譜沒有擺子紀錄，`utils.py` 也不讀 `HD`，所以重播時棋盤少了讓子。維持官方做法不修改。
