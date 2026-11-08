# 作業規定（原文）

使用者於 2026-11-08 提供，以下照原文保存，不修改。範圍調整：使用者告知作業改成只做玩家辨識（見 CLAUDE.md）。

## Steps

1. Get the code and data: git clone https://github.com/AILAB-NDHU/AICup-2026-Tutorial, then download the dataset from the AI CUP website and put it in dataset/.

2. Set up the environment: Python 3.10 and PyTorch (matching your CUDA version), then pip install pandas numpy tqdm scikit-learn matplotlib seaborn webdataset sgfmill. Check that the GPU works with torch.cuda.is_available().

3. Trial run on a small subset: take 1,000 games per rank and train for 1 epoch to make sure feature extraction → training → inference runs end to end without errors, then move to the full data.

4. Full training: run sections 1–3 of each notebook. Feature extraction only needs to run once; adjust BATCH_SIZE to your GPU memory. Keep the train/val curves for every epoch.

5. Build the submission files: use best_model.pth to predict both the public and private test sets, and concatenate them into an 800-row submission_rank.csv and an 800-row submission_player.csv. Keep the pub_ / priv_ prefixes as they are; any missing question makes the whole submission invalid.

6. Submit to the leaderboard: submit under your team account and record the Public score.

7. One small change: for each sub-task, change one thing, run again and submit, e.g. learning rate, number of epochs, number of residual blocks, number of moves used, or how multiple games are aggregated (probability averaging vs. summed log-probabilities). The score does not have to improve, but you must explain the result.

## Deliverables and Grading

Getting the pipeline running, submitting successfully and explaining your work earns most of the points; leaderboard rank does not count for this assignment.

| Item | Points | What to submit |
|---|---|---|
| Environment and trial run | 15 | Environment info (GPU, PyTorch version) and screenshots of the trial-run output |
| Full training | 25 | Train/val curves, training time, val accuracy (or loss) of the best epoch |
| Successful submission | 30 | Leaderboard screenshot (team name and Public score), the submitted CSVs |
| Small-change experiment | 20 | What you changed, before/after scores, a short explanation |
| Reflection and contributions | 10 | Problems you hit and how you solved them, who did what |
| Total | 100 | |

Submit:

- ☐ Short report PDF (3–5 pages, covering every item above)
- ☐ Your modified code (notebooks or a GitHub link)
- ☐ Leaderboard screenshots and submission CSVs
