# 實驗紀錄

## 目前狀態

- [x] 環境：RTX 5080（16 GB）、Python 3.10.12、PyTorch 2.11.0+cu128
- **範圍：只做玩家辨識**（2026-11-08 作業改成不用跑棋力預測；下面棋力預測的紀錄保留當參考）
- [x] 資料：訓練集 v1.1、玩家辨識測試集（`aicup2026_player_identification_tests_20261030.zip`，2026-11-08 放進 `tests/`，官方範例提交檔通過 `check_submission.py`）
- [x] 資料：**玩家辨識測試集 v2**（`aicup2026_player_identification_v2_tests_20261108_fix_readme.zip`，2026-11-12 放進 `tests/`）：多了新增測試集 `test2_*`／`candidates2_*`，提交改成 4 份共 1,600 列；原測試集 4 個檔和 20261030 版逐位元相同
- [x] 試跑：`trial-player`（2026-11-08 重跑，環境資訊 → 抽特徵 → 訓練 1 epoch → 推論都有執行，提交檔通過檢查）
- [ ] 試跑截圖：`runs/trial-player/player-identification.ipynb`（由使用者截）
- [x] 完整訓練：玩家辨識（`baseline-player`，2026-11-08；它的 800 列提交檔是舊格式，不能上傳，要用 v2 重新推論）
- [ ] 提交 baseline、記錄 Public 分數與排行榜截圖
- [ ] 小改實驗 A（推論時平均向量先縮回長度 1）：`exp-normalize` 是舊格式 800 列，不能上傳，要用 v2 重新推論
- [ ] 報告

## 交接事項

### 下一步：用 v2 測試集重新推論兩次，再上傳（2026-11-12）

11-08 的兩份 800 列提交檔上傳時被 AIdea 擋下（「上傳檔案不合規則」），原因是官方更新了測試集與提交格式。notebook 與 `check_submission.py` 已改成 4 份、1,600 列，下一步用同一個 baseline 模型只跑推論兩次：

- `baseline-v2`：不正規化（baseline）
- `exp-normalize-v2`：`--normalize`（實驗 A）

通過 `check_submission.py` 後由使用者上傳，各自記下 Public 分數並截排行榜圖。v2 的 Public 分數 = 原 Public 400 題與新 Public 400 題的平均。

### 測試集 v2 的內容（新增測試集 `pub2_`／`priv2_`）

- 每份候選庫 600 人、每人 10 局（原測試集是 400 人、每人 100 局），執黑執白約各半。
- 每題查詢 1／2／3／5 局各 100 題（原測試集是 5／10／15／20 局），同一題可能黑白都有。
- 資訊比原測試集少很多，預期分數會比較低。
- 解析檢查：新增測試集的查詢 2,200 盤、候選 12,000 盤全部解析成功，沒有 0 個窗口的棋局；`utils.py` 本來就支援執白。

### 小改實驗 A：比距離前把平均向量縮回長度 1（2026-11-08 使用者決定）

- **改什麼：** 推論時，400 個候選重心和每題的查詢平均向量，先各自除以自己的長度，再算 L2 距離。模型和 baseline 是同一個（`runs/baseline-player/player-trained-models/best_model.pth`），沒有重新訓練。
- **為什麼：** 模型輸出的每個向量長度都是 1，訓練時比的是方向。很多向量取平均後會變短，而且棋風越不一致的人越短；直接比距離時，長度差異會干擾判斷（例：方向相同但比較短的正確答案，距離反而比方向偏掉的錯誤答案遠）。縮回長度 1 後只比方向，和訓練時一致。
- **不保證進步：** 長度可能也帶有「下法穩不穩定」的資訊，丟掉可能有損失，要看 Public 分數。
- **和 baseline 的排名差異（舊版 800 列、還沒有分數，只是看預測改變多少）：** public 400 題中 top_1 不同 48 題、前 5 名名單有變 201 題；private top_1 不同 73 題、名單有變 216 題。

### 完整訓練的實測（baseline-player）

- 時間共 124.3 分：抽特徵 24.2 分（999,997 局、0 局解析失敗、13.18 GB、平均 12.9 KB/檔）、訓練 5 輪各約 16.0 分、推論約 20 分（每份測試集的候選庫約 8.6 分）。
- 資源峰值：RAM 9,883 MiB、swap 2,935 MiB、GPU 2,479 MiB，沒有接近自動停止門檻。
- 提早停止的檢查沒有觸發（第 1 輪 train loss 0.4806 < 0.495）。
- `summary.txt` 標示「有未 commit 的修改」：`run_notebook.py` 用 `git status` 判斷，未追蹤的檔案也算在內，當時有未追蹤的 `runs/trial-player-infer/`，EXPERIMENTS.md 也在更新；notebook 和 commit `0076eb8` 相同。
- 機器沒有電池（Windows 偵測不到），接電源時不睡眠也不休眠，不用管蓋螢幕。

### 已知缺口

- 提交用的 CSV 和 `history.csv` 被 `.gitignore` 排除，只存在本機的 `runs/`，要另外保存並繳交。
- repo 是 private，如果用 GitHub 連結繳交程式，要先確認助教看得到。

### 使用者要做或決定的事

- 截試跑圖：`runs/trial-player/player-identification.ipynb`（2026-11-08 重跑的版本，含環境資訊、抽特徵、訓練、推論）。
- 上傳 v2 的兩份提交檔（`baseline-v2`、`exp-normalize-v2`，跑完後），記錄 Public 分數、截排行榜圖。

## 遇到的問題與解法

報告「心得與分工」用。誰做了什麼由使用者自己寫；AI 協助的部分要如實寫進報告。

| 日期 | 問題 | 怎麼發現 | 解法 |
|---|---|---|---|
| 11-07 | 玩家辨識測試集比訓練集晚拿到 | 試跑時 notebook 印出「缺少測試集，跳過推論」 | notebook 改成缺測試集時跳過推論、不讓整份失敗；先做訓練，測試集到了再補推論 |
| 11-08 | 作業範圍改成只做玩家辨識 | 使用者告知 | 棋力預測不再執行，刪掉 `trial-rank`；CLAUDE.md、EXPERIMENTS.md 改成只做玩家辨識（原文要求兩個子題，報告要說明） |
| 11-08 | 舊的兩次試跑各缺一段：一次沒推論、一次沿用舊特徵沒抽取 | 對照作業要求「抽特徵 → 訓練 → 推論都要跑通」，檢查 log 發現 | 刪掉舊試跑和 `trial/`，notebook 加印環境資訊，重跑一次完整試跑 |
| 11-08 | 試跑在推論中途 Kernel died | `summary.txt` 寫 `failed: Kernel died` | 查系統紀錄沒有記憶體不足；推測是對話關閉時背景工作被停掉，改用 tmux 執行後成功 |
| 11-08 | `summary.txt` 把 baseline 標成「有未 commit 的修改」，但 notebook 沒改 | 讀 summary 時發現 | 原因是 `git status` 連未追蹤的檔案也算；先 commit 再執行，之後的試跑就是乾淨的 commit |
| 11-08 | 小改實驗只改推論，但重跑 notebook 會重新訓練約 2 小時 | 規劃小改實驗時發現 | `run_notebook.py` 加 `--infer-weights`：把標了 `train` 標籤的 cell 拿掉，直接載入 baseline 模型，推論約 20 分 |
| 11-12 | 800 列提交檔上傳 AIdea 被擋（「上傳檔案不合規則」），但自己的 `check_submission.py` 顯示通過 | 上傳失敗；先改檔名、換行符號和官方範例一致仍失敗，使用者再提供官方更新說明 PDF | 官方 11-08 更新測試集：多了新增測試集，提交要 4 份、1,600 列。自己寫的檢查工具只會檢查寫進去的舊規則，所以沒抓到。下載 v2 題目包、notebook 推論改成 4 份、`check_submission.py` 改成新規則（用故意做壞的檔案確認會擋下），重新推論 |

## 執行紀錄

| Run ID | 子題 | 模式 | Commit | 改了什麼 | 最佳 val | Public | 耗時 | 備註 |
|---|---|---|---|---|---|---|---|---|
| trial-rank（已刪除，範圍改變） | 棋力預測 | trial | 整理前（未 commit） | 每級 1,000 局、1 epoch | val acc 9.00% | — | 1.2 分 | 只驗證流程；RAM 峰值約 10.2 GB、GPU 約 9.5 GB |
| trial-player（舊版，已刪除；沒跑推論） | 玩家辨識 | trial | 整理前（未 commit） | 每級 1,000 局、200 步 | val loss 0.5268 | — | 0.7 分 | 只驗證流程，推論待測試集；RAM 峰值約 5.4 GB、GPU 約 2.4 GB |
| trial-player-infer（已刪除；沿用舊特徵沒有抽取） | 玩家辨識 | trial | 0076eb8 | 同 trial-player，加上真實測試集推論 | val loss 0.5268 | 不上傳 | 19.7 分 | 第一次跑通推論：800 列、通過 `check_submission.py`；每份測試集的候選庫約 8.5 分、查詢約 1 分；RAM 峰值約 7.0 GB、GPU 約 2.4 GB |
| baseline-player | 玩家辨識 | full | 0076eb8（EXPERIMENTS.md 有未 commit 修改） | 官方 baseline 設定：5 輪 × 15,000 步，用 val loss 挑模型 | val loss 0.3513（第 5 輪） | 不能上傳（舊格式 800 列） | 124.3 分 | 每輪 val loss 0.4662 → 0.3758 → 0.3608 → 0.3537 → 0.3513；800 列、通過 `check_submission.py`；RAM 峰值約 9.7 GB、swap 約 2.9 GB、GPU 約 2.4 GB |
| trial-player（第一次重跑，中斷） | 玩家辨識 | trial | 4c91d5e | 環境資訊 + 每級 1,000 局、1 epoch（200 步）+ 推論 | val loss 0.5268 | — | 2.7 分 | 推論做到 public 候選 5,120 局時 Kernel died；系統紀錄沒有記憶體不足，當時可用約 7.6 GB；推測是對話關閉時背景工作被停掉，資料夾已刪 |
| trial-player | 玩家辨識 | trial | 4c91d5e | 同上，改在 tmux 執行；`trial/` 先刪掉，抽特徵真的重做 | val loss 0.5268 | 不上傳 | 20.0 分 | 每級抽 1,000 局，濾掉只有 1 局的玩家後剩 8,191 局／2,105 位；抽特徵 0.2 分、0 局解析失敗；推論 800 列、通過 `check_submission.py`；RAM 峰值約 8.2 GB、GPU 約 2.4 GB |
| exp-normalize | 玩家辨識 | full（只推論） | 56ac160 | 實驗 A：推論時重心與查詢平均向量先縮回長度 1（`--normalize`），用 baseline 的 best_model.pth，不重新訓練 | 同 baseline（0.3513） | 不能上傳（舊格式 800 列） | 22.7 分 | 800 列、通過 `check_submission.py`；和 baseline 比 top_1 不同 public 48／private 73 題；RAM 峰值約 6.3 GB、swap 約 1.0 GB、GPU 約 0.8 GB |

## 和官方 baseline 的差異

- 棋力預測、玩家辨識：程式能切換試跑／完整模式；每個 epoch 存 `history.csv`；訓練前釋放棋譜資料；訓練異常時提早停止。
- 玩家辨識：保留 2% 玩家不參與訓練，用來算 val loss，並用它挑 `best_model.pth`（官方是用 train loss）。
- 玩家辨識：可以只跑推論（`--infer-weights`）；小改實驗 A 的正規化是開關（`--normalize`），預設關閉，關閉時和官方相同。
- 訓練集用 v1.1；約 3.6% 棋局（讓 2 子以上）的棋譜沒有擺子紀錄，`utils.py` 也不讀 `HD`，所以重播時棋盤少了讓子。維持官方做法不修改。
