# Data dictionary

All timestamps are UTC ISO-8601. All ratings and estimates use proficiency 0–5. Missing self-ratings explicitly use 0; absent assessment evidence falls back to the self-rating. Model data rejects missing values.

## Catalogue

Skills: `id` stable text key; `name` display label; `prerequisites` directed incoming skill IDs; `hours` positive effort estimate; `outcome`, `practice`, `completion` authored objective guidance; `resources` list with title/provider/URL/status; `questions` prompt, choice list, zero-based correct answer index and feedback. Roles: stable `id`, name, description, project, requirements (skill ID, target >0 to 5, weight >0 to 1). Prerequisite cycles and unknown references fail validation.

## SQLite

| Table | Fields and meaning |
| --- | --- |
| learner_profiles | id=1 single local learner; payload JSON: optional nickname <=80 characters, role ID, hours 1–80/week, experience enum, resource preference, project notes <=4000 characters, demo flag, claimed ratings |
| learner_skills | profile_id FK, skill ID, claimed rating 0–5; unique per profile/skill |
| skill_evidence | id attempt token, profile_id FK, skill, level=score/20, created timestamp, kind=assessment |
| roles | id and curated role JSON payload |
| role_requirements | role_id FK, skill, target 0–5, weight 0–1 |
| learning_objectives | skill primary key and curated objective JSON |
| learner_objective_progress | profile_id FK, skill FK, status (not started/started/completed), updated timestamp |
| assessment_attempts | unique id token, profile_id FK, skill, score 0–100 percent correct, version 1.0, created timestamp, before_state and after_state JSON with level |
| gap_history | sequential id, created timestamp, role ID, payload JSON list with skill/current/target/gap/weight/relevance/priority/evidence |
| model_metadata | run UUID, created timestamp, complete UI training metadata JSON; CLI stores metadata in artifacts only |

Assessment history and self-ratings are preserved independently. Evidence kind is never model inference. Project notes are claimed experience, never assessment evidence. Repeated assessment tokens are ignored; distinct intentional retries remain in history. Progress writes update one profile/skill entry. Reset deletes learner data with confirmation, preserving catalogue and model runs.

## ML dataset and artifacts

See data/README.md for every CSV column, unit and range. Five features are python/statistics proficiency, weekly practice hours, prior-score percentage and project count. Future score and its band are targets only. Inference proxies the prior score with the latest available quiz, uses zero if absent, and zero projects because free text cannot establish a project count.

Metadata includes version, UTC timestamp, source, CSV-normalized SHA-256 hash, feature order, seed, split protocol, total/train/test sizes, full/test class balances, metrics, cluster profiles and simulation comparison. Q-table is JSON shape (3 mastery, 3 score, 2 prerequisite, 4 action). Joblib artifacts must be trusted local outputs. Regression scores use assessment points, RMSE/MAE points and R² dimensionless; classifier metrics and silhouette are dimensionless.
