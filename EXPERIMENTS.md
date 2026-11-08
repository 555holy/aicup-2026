# 實驗紀錄

## 目前狀態

- [x] 環境：RTX 5080（16 GB）、Python 3.10.12、PyTorch 2.11.0+cu128
- **範圍：只做玩家辨識**（2026-11-08 作業改成不用跑棋力預測；下面棋力預測的紀錄保留當參考）
- [x] 資料：訓練集 v1.1、玩家辨識測試集（`aicup2026_player_identification_tests_20261030.zip`，2026-11-08 放進 `tests/`，官方範例提交檔通過 `check_submission.py`）
- [ ] 試跑截圖（環境資訊、試跑輸出）
- [ ] 完整訓練：玩家辨識
- [ ] 提交 baseline、記錄 Public 分數與排行榜截圖
- [ ] 小改實驗
- [ ] 報告

## 交接事項

### 下一步：完整訓練（尚未開始）

開始前要等使用者同意，並確認 Windows 已關閉睡眠、筆電接上電源且不蓋螢幕。

```bash
tmux new -d -s train 'cd ~/aicup-2026 && ~/venvs/aicup/bin/python scripts/run_notebook.py rank-prediction.ipynb --mode full --run-id baseline-rank; ~/venvs/aicup/bin/python scripts/run_notebook.py player-identification.ipynb --mode full --run-id baseline-player'
tail -f ~/aicup-2026/runs/baseline-rank/run.log
```

依試跑等比例估算，只能當參考：棋力預測約 3.5 小時；玩家辨識至少 2 小時，也可能因讀取大量小檔案而更久。

跑完要做：更新本檔的執行紀錄、用 `check_submission.py` 檢查提交檔，再由使用者上傳。

### 還沒驗證

- 玩家辨識的推論：沒有測試集，還沒跑過。
- 「第 1 個 epoch 沒學到東西就停止」的檢查：只在完整模式生效，還沒觸發過。
- 完整訓練的實際時間和 RAM 峰值。WSL 上限約 15.6 GB，試跑最高約 10.2 GB。不夠時可調高上限（電腦有 31 GB），但要重啟 WSL。

### 已知缺口

- **還沒有「只跑推論」的方式。** 現在重跑 notebook 會重新訓練，所以玩家辨識補推論和只改推論的小改實驗，都要先補這個功能。
- 提交用的 CSV 和 `history.csv` 被 `.gitignore` 排除，只存在本機的 `runs/`，要另外保存並繳交。
- repo 是 private，如果用 GitHub 連結繳交程式，要先確認助教看得到。

### 使用者要做或決定的事

- 下載玩家辨識的 4 個測試集 CSV。
- 截試跑圖：`runs/trial-rank/rank-prediction.ipynb`、`runs/trial-player/player-identification.ipynb`。
- 決定小改實驗（尚未決定）。建議選不用重新訓練的：棋力預測改用對數機率加總；玩家辨識改變使用的手數。
- 可選：上傳 `runs/trial-rank/submission_rank.csv`，測試隊伍帳號和上傳流程。排行榜沒有提交次數上限。

## 執行紀錄

| Run ID | 子題 | 模式 | Commit | 改了什麼 | 最佳 val | Public | 耗時 | 備註 |
|---|---|---|---|---|---|---|---|---|
| trial-rank | 棋力預測 | trial | 整理前（未 commit） | 每級 1,000 局、1 epoch | val acc 9.00% | — | 1.2 分 | 只驗證流程；RAM 峰值約 10.2 GB、GPU 約 9.5 GB |
| trial-player | 玩家辨識 | trial | 整理前（未 commit） | 每級 1,000 局、200 步 | val loss 0.5268 | — | 0.7 分 | 只驗證流程，推論待測試集；RAM 峰值約 5.4 GB、GPU 約 2.4 GB |

## 和官方 baseline 的差異

- 棋力預測、玩家辨識：程式能切換試跑／完整模式；每個 epoch 存 `history.csv`；訓練前釋放棋譜資料；訓練異常時提早停止。
- 玩家辨識：保留 2% 玩家不參與訓練，用來算 val loss，並用它挑 `best_model.pth`（官方是用 train loss）。
- 訓練集用 v1.1；約 3.6% 棋局（讓 2 子以上）的棋譜沒有擺子紀錄，`utils.py` 也不讀 `HD`，所以重播時棋盤少了讓子。維持官方做法不修改。
