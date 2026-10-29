# Verification — 2026-10-28

Follow-up Windows permissions fix: the user's test run reported 10 passed and 9 setup errors because the shared `%TEMP%/pytest-of-Ashika` folder was inaccessible, plus two cache warnings. `tests/conftest.py` now assigns a unique repository-local `.test-tmp/run-*` directory by default, respecting an explicit `--basetemp`. `pytest.ini` disables the cache provider to avoid the existing cache conflict. After this change, `.\.venv\Scripts\python -m pytest -q` completed with **19 passed in 7.22s**, with no warnings. No shared temporary folders or existing cache files were deleted or had their permissions changed.

Environment: Windows PowerShell, Python 3.14.0, project-local .venv. No hosted API keys were configured or needed. The initial repository was empty except for .git; no user source files were overwritten.

## Executed commands and actual results

| Command | Actual result |
| --- | --- |
| `python -m venv .venv` | Created the project-local environment |
| `.\.venv\Scripts\python -m pip install -r requirements.txt` | Initial sandbox network access failed; approved network retry installed all dependencies successfully |
| `.\.venv\Scripts\python -m pip check` | No broken requirements found |
| `.\.venv\Scripts\python data\build_catalogue.py` | Created the curated JSON catalogue |
| `.\.venv\Scripts\python -m compileall -q app.py skillroute tests data` | Exit 0 |
| Standalone temporary-SQLite workflow script | Profile reload equal; six roadmap objectives; incorrect Python quiz scored 0; evidence persisted; completed objective reopened; one attempt survived reload |
| `.\.venv\Scripts\python -m skillroute.ml` | Exit 0; trained/evaluated all four scikit-learn pipelines and Q policy, generated 600 synthetic records and saved artifacts |
| `.\.venv\Scripts\python -m pytest -q` | **19 passed in 24.63s** |
| `.\.venv\Scripts\python -m streamlit run app.py --server.headless true --server.address 127.0.0.1` | Server started at http://127.0.0.1:8501 |
| `Invoke-WebRequest http://127.0.0.1:8501/_stcore/health -UseBasicParsing` | HTTP 200, body `ok` |
| `git diff --check` | Exit 0 |
| Default-path Streamlit AppTest after CLI training | Overview and Model Lab loaded without errors using the actual seeded default database and CLI-generated 600-record model artifacts |

Two premature test invocations during dependency installation failed at collection because pytest/pandas had not yet installed. After installation completed the full suite passed. No failing tests were skipped or marked expected failures.

## Automated acceptance coverage

- Unit/integration tests verify the priority equation, non-negative gaps, declared missing-value policy, invalid ratings, prerequisite cycles, dependency ordering, completed-objective exclusion, profile/progress/evidence persistence and duplicate attempt protection.
- A deliberately weak assessment updates only assessment-derived proficiency, preserves the claimed rating, reopens a completed topic and changes the roadmap. Historical gap snapshots remain available.
- CSV export is parsed back and required columns checked. Replacement data tests cover small sample counts, missing values, duplicate learners, invalid class labels/ranges/targets and inconsistent score bands.
- Q-learning tests verify the exact Bellman update, terminal handling, reproducibility and valid action choice; evaluation compares 200 seeded episodes per policy in the actual benchmark.
- ML tests fit actual models and independently recompute held-out MAE and classification accuracy. The scaler mean is checked against training-only data.
- Streamlit AppTest opens all ten navigation sections, saves a profile, exercises incomplete-answer validation, submits answers, reloads persisted records, completes an objective, verifies reset confirmation, trains all models through the UI, opens every algorithm result and runs inference.

The live HTTP smoke test confirms the server starts; AppTest executes application logic and controls. No real-browser screenshot, mobile visual review, browser download-click automation or screen-reader audit was performed. Export bytes are verified at service level. Setup was executed in a newly created .venv, but a second clean installation and macOS/Linux execution were not performed.

## Acceptance status and limitations

All core acceptance workflows are implemented and covered by the checks above: first-run seed, persistence, inspectable requirements, deterministic gaps, prerequisite plan, real assessments, saved progress, adaptive changes, real Q-learning/baseline, trained supervised models, held-out metrics, fitted clustering, synthetic-data notices, no hiring guarantees, no API-key dependency and confirmed reset. Documentation includes setup, training and test commands.

This is a local academic prototype. There is no real learner dataset, validated educational efficacy, official certification or hiring model. Resource-format personalization, large question banks, multi-user authentication, production hardening and real-browser accessibility verification remain outside this implementation. The learned Q policy matched the baseline; no advantage was observed.
