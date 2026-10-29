# Model card — SkillRoute 1.0

## Scope and provenance

These models demonstrate reproducible academic ML, not real-world educational or hiring validity. Out-of-scope uses include selection, admissions, employment decisions, certification and promises of educational efficacy. All benchmark records are synthetic, generated locally by skillroute/ml.py with seed 42. Dataset size: 600 independent learners. Generated class counts: developing 217, guided 248, independent 135. Labels are bands of the generated next-score target (<=45, <=70, >70), not externally verified mastery categories.

The synthetic generator combines noisy latent proficiency, Python/statistics features, prior score, project counts and study time using an explicit rule plus Gaussian outcome noise. Models learn this artificial relationship; apparent accuracy cannot establish real generalization. No names or personal identifiers are predictive features. Replacement data requires independent learners, matching labels, valid ranges and a defensible temporal ordering; schema validation alone cannot establish consent or target provenance.

## Shared protocol

Features, in order: Python proficiency 0–5, statistics proficiency 0–5, weekly practice hours 1–80, prior assessment score 0–100, completed project count 0–30. All are intended to be available before the future assessment outcome. Model data rejects missing/non-finite/out-of-range values and duplicate learners/features. No imputation is performed.

Train/test: 450/150, fixed seed 42, stratification by mastery label. Held-out class counts: developing 54, guided 62, independent 34. Transformations fit only on training records, within pipelines. Fixed hyperparameters; no tuning or feature selection against test data. Unique learner IDs prevent learner overlap. Class imbalance and synthetic generation bias remain. No cross-validation-based algorithm selection was performed.

The following values were measured by `.venv\Scripts\python -m skillroute.ml` on 2026-10-28. Full evaluation, reports, confusion matrices and cluster profiles are in `docs/benchmark_metrics.json` (public synthetic run) and the current run's `models/artifacts/metadata.json`. UI retraining may replace current artifacts without changing this documented benchmark.

## Ridge regression

Target: numeric next assessment score, 0–100. StandardScaler → Ridge(alpha=1).

| Held-out metric | Value |
| --- | ---: |
| MAE (score points) | 10.010819 |
| RMSE (score points) | 12.900838 |
| R² | 0.603034 |

R² can be negative on other datasets and is uncertain with small test sets. Unconstrained regression can extrapolate outside 0–100. The app labels inference experimental and does not save it as evidence.

## Logistic regression and decision tree

Target: next assessment's score-derived mastery band. Logistic pipeline: StandardScaler → LogisticRegression(max_iter=1000). Tree pipeline: StandardScaler → DecisionTreeClassifier(max_depth=5, min_samples_leaf=8, random_state=42). Scaling is unnecessary for the tree but retained for a consistent pipeline boundary.

| Held-out metric | Logistic | Tree |
| --- | ---: | ---: |
| Accuracy | 0.706667 | 0.573333 |
| Macro precision | 0.720382 | 0.572623 |
| Macro recall | 0.693490 | 0.560288 |
| Macro F1 | 0.702282 | 0.565257 |
| Weighted F1 | 0.704851 | 0.574150 |

Confusion matrices (rows=true, columns=predicted; developing, guided, independent):

```text
Logistic: [[44, 10, 0], [14, 42, 6], [1, 13, 20]]
Tree:     [[34, 16, 4], [15, 36, 11], [1, 17, 16]]
```

Full class-level precision/recall/F1/support is displayed in Model Lab and saved in metadata. The minority independent class has lower recall; aggregate accuracy obscures this difference. No threshold tuning was performed on held-out data.

## K-Means

No target label; StandardScaler → KMeans(k=3, n_init=10, random_state=42), fit to 450 training feature vectors. Held-out silhouette: **0.197927**, diagnostic sample n=150. This modest separation is descriptive, not predictive accuracy. Training cluster means are shown in Model Lab/metadata; cluster numbers are arbitrary, not ground-truth learner categories. The same held-out subset is used for reporting only, never for fitting or selecting k.

## Tabular Q-learning

Simulated educational environment only. State: three mastery bins, three recent-performance bins, two prerequisite flags; four actions (prerequisite review, weak-skill practice, advancement, mistake review). Q array shape 3×3×2×4; initialized to zero. Alpha .2, gamma .9, epsilon .15; 1,800 training episodes, seed 42, maximum 12 actions per episode. Terminal and step-limit updates omit bootstrapping. Values are saved as JSON; no pickle is used for the policy.

Reward: +2 success, −.5 failure, additional −.5 unsuitable activity, −.1 per-action cost. Success is assumed 80% for the baseline-suitable action and 25% otherwise. The baseline selects foundation review when pending, mistake review for low performance, practice for low mastery, otherwise advance. Both strategies target the same highest-priority eligible roadmap objective in the app. The compact simulation compares activity types, not a realistic multi-skill curriculum.

Evaluation: 200 episodes, unseen seeds 10000–10199, identical starting states and random streams per strategy, maximum 12 steps.

| Policy | Mean episode reward | Standard deviation |
| --- | ---: | ---: |
| Q-learning | 3.6075 | 1.182875 |
| Priority baseline | 3.6075 | 1.182875 |

The learned policy matches the baseline on this evaluation. **No improvement over the baseline was measured.** This environment favors its encoded baseline by construction and cannot establish actual learner gains. Real adaptive efficacy would require ethically collected longitudinal interaction data and a valid study design.

## Reproduce and inspect

```powershell
.\.venv\Scripts\python -m skillroute.ml
.\.venv\Scripts\python -m pytest -q
```

Output: trusted local `models/artifacts/{ridge,logistic,tree,clusters}.joblib`, `q_table.json`, `metadata.json`. Metadata includes version, timestamp, SHA-256 data hash, feature order, seed, splits and metrics. This run's data hash is `84e89a4b8964614389b69c1b7063792d7dbc9bf79b04339cf4cd6f79411ce5f1`. Exact installed package versions are in requirements-lock.txt. Never replace these trusted local artifacts with untrusted serialized models.

Inference caveat: UI features proxy practice time with available weekly study time, latest score with the most recent short quiz (possibly another skill), and default project count to zero because free-text claims are not validated counts. These differ from benchmark measurements. Inferences are labelled, shown separately and never treated as assessment evidence.
