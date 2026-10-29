# SkillRoute

A Python application for explainable career skill gaps, prerequisite-aware study plans, local assessments and adaptive practice. This is a single-user academic prototype, with real scikit-learn training and a simulated tabular Q-learning environment. It does not predict hiring or guarantee placement.

## Run on Windows PowerShell

```powershell
python -m venv .venv
.\.venv\Scripts\python -m pip install -r requirements.txt
.\.venv\Scripts\python -m skillroute.ml
.\.venv\Scripts\python -m streamlit run app.py
```

## Run on macOS/Linux

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python -m skillroute.ml
.venv/bin/python -m streamlit run app.py
```

Python 3.11+ is intended; the implementation environment uses Python 3.14. Dependencies are constrained in requirements.txt. The core workflow is offline after installation; external learning links naturally need internet. No API key or .env file is required. Default Streamlit address: http://localhost:8501.

`requirements-lock.txt` records exact package versions from the verified Windows/Python 3.14 environment. Use `python -m pip install -r requirements-lock.txt` to reproduce those versions; other Python versions may need the compatible ranges in requirements.txt.

## Features and first run

The first launch initializes SQLite and seeds one explicitly synthetic learner, idempotently. Edit the profile to set a target role, 0–5 self-ratings, study time and project notes. Browse four role profiles and sixteen reusable competencies. Inspect gap components, follow a prerequisite-ordered roadmap, save objective progress, complete a quiz, then inspect changed evidence and adaptive recommendations. Export current gaps and attempts as CSV. Settings offers a confirmed learner-data reset.

Assessment-derived estimates are latest score / 20; self-ratings remain separate. Missing self-ratings explicitly mean 0. A score below 40% reopens a completed objective for practice. Two-question quizzes are formative checks, not reliable certification. Completing an objective alone does not increase skill proficiency. All recommendations are educational guidance.

## Models and data

`python -m skillroute.ml` generates `data/synthetic_assessments.csv` (600 independent synthetic learners, seed 42), trains Ridge regression, logistic regression, decision-tree classification and scaled K-Means, trains tabular Q-learning, and writes trusted local artifacts plus actual evaluation metadata into `models/artifacts/`. The UI can perform the same training and inspect each algorithm. No artifacts are required for profile/gap/roadmap functionality.

Use `python -m skillroute.ml --csv path/to/replacement.csv` to validate and train on a replacement file. The UI accepts CSV up to 2 MB. The schema and provenance policy are in [data/README.md](data/README.md). Do not load third-party joblib/pickle files into the local artifact directory. Inference is experimental, displayed separately, and never modifies skill evidence.

All supervised models use a fixed 75/25 split stratified by score-derived mastery bands, seed 42. Scaling is fit within each pipeline on training data only. Hyperparameters are fixed; there is no tuning against test results. Regression reports MAE, RMSE and R²; classifiers report accuracy, precision, recall, F1 and confusion matrices. Clustering is fit on training features and reports held-out silhouette with cluster profiles. The synthetic generator encodes noisy relationships; these evaluations do not demonstrate generalization to real students. Q-learning is evaluated on 200 unseen simulation seeds against a deterministic strategy under explicitly assumed success probabilities.

## Test

```powershell
.\.venv\Scripts\python -m pytest -q
.\.venv\Scripts\python -m compileall -q app.py skillroute tests
```

On macOS/Linux use `.venv/bin/python`. Tests use temporary databases. They cover formulas, cycles, scheduling, profile/progress persistence, attempts, idempotency, evidence-driven adaptation, CSV export/validation, Q-learning updates, actual held-out metrics and Streamlit navigation/workflow. See docs/VERIFICATION.md for executed commands and results.

Tests create an isolated directory per run under ignored `.test-tmp/`, avoiding permission problems with Windows' shared `pytest-of-Ashika` temporary folder. Pytest's cache is disabled to avoid existing cache permission conflicts. Scratch directories contain only test data and can be removed when no tests are running. An explicit `--basetemp` overrides the default location.

## Architecture and files

`app.py` supplies one sidebar navigation system. `skillroute/catalogue.py` validates `data/catalogue.json`; `core.py` computes gaps and roadmaps; `database.py` owns transactions and persistence; `features.py` validates model inputs; `ml.py` owns training/evaluation/inference; `reinforcement.py` owns the simulation and policy; `reporting.py` creates CSV exports. SQLite stores profiles, claimed skills, assessment evidence, requirements, objectives, progress, attempts, gap snapshots and UI training-run metadata. No authentication is implemented.

See [architecture](docs/ARCHITECTURE.md), [data dictionary](docs/DATA_DICTIONARY.md), [model card](docs/MODEL_CARD.md), [decisions](docs/DECISIONS.md), and [demo script](docs/DEMO_SCRIPT.md).

## Limits

Curated requirements are educational assumptions, not scraped live job requirements. Learning resource URLs are curated public references; current availability is not continuously checked. Project notes remain unverified claims. Preference is recorded, but the initial catalogue contains documentation resources rather than a complete multi-format library. No learned model is validated on real learners. Assessment granularity is coarse, question answers are visible in source, and quizzes are unsuitable for high-stakes testing. Inference uses rough profile proxies (project count defaults to zero) and may extrapolate. This local single-user application has not undergone production privacy/security or real-browser accessibility review. Reset retains model artifacts; remove those manually if retraining is needed.
