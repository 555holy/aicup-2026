# AI CUP 2026 圍棋作業

## 目標

截止日：2026-11-16。**只做玩家辨識**（2026-11-08 使用者告知作業範圍改變，不用跑棋力預測），完成流程、成功提交並解釋結果。

**排行榜名次不計分，不追求調參。** 作業原文見 `ASSIGNMENT.md`（原文要求兩個子題都做，範圍縮小是使用者告知，報告要寫清楚）。

| 項目 | 分數 | 要交 |
|---|---|---|
| 環境與試跑 | 15 | 環境資訊（GPU、PyTorch 版本）、試跑輸出截圖 |
| 完整訓練 | 25 | train/val 曲線、訓練時間、最佳 epoch 的 val loss |
| 成功提交 | 30 | 排行榜截圖（隊名、Public 分數）、提交的 CSV |
| 小改實驗 | 20 | 改了什麼、改前改後分數、簡短解釋（要重新提交拿分數） |
| 心得與分工 | 10 | 遇到的問題和解法、誰做了什麼 |

要交：3–5 頁報告 PDF（涵蓋上表每一項）、修改後的程式（notebook 或 GitHub 連結）、排行榜截圖、提交 CSV。各項進度記在 `EXPERIMENTS.md`。

## 專案結構

- `rank-prediction.ipynb`、`player-identification.ipynb`：唯一的程式來源，不存輸出。
- `scripts/run_notebook.py`：所有執行都走這支，結果放在 `runs/<run-id>/`。
- `scripts/check_submission.py`：提交檔格式檢查。
- `EXPERIMENTS.md`：目前狀態與每次執行的紀錄。
- `training/`、`tests/`：官方資料，不進 git。作業說放 `dataset/`，但 notebook 讀這兩個路徑，以 notebook 為準。
- Python 環境：`~/venvs/aicup`。
- 遠端：`origin` 是使用者的 private repo，`upstream` 是老師的 repo，不要 push 到 `upstream`。

## 常用指令

```bash
~/venvs/aicup/bin/python scripts/run_notebook.py player-identification.ipynb --mode trial --run-id <名稱>
~/venvs/aicup/bin/python scripts/check_submission.py runs/<名稱>/submission_player.csv
```

## 工作方式

- 回覆用繁體中文，用白話說明。使用者正在學習，名詞要解釋。
- 執行前先說明：輸入、要做什麼、輸出，等使用者同意才開始。
- **必須先經過使用者同意：** 開始完整訓練、commit、push、上傳提交檔、決定小改實驗要改什麼。
- 長時間執行前，先用 `--mode trial` 確認程式沒壞。
- 上傳前必須通過 `scripts/check_submission.py`。
- 每次執行後更新 `EXPERIMENTS.md`，數據要來自 `runs/` 的實際輸出，不能憑估算。
- 不要修改 `training/`、`tests/` 裡的官方資料；不要把密碼或 token 寫進 repo。
- 報告的結論和解釋要使用者自己能講得出來，AI 的協助要如實揭露。
