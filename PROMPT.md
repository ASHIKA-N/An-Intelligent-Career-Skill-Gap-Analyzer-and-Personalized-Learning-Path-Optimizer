# PROMPT.md — SkillRoute
## Master Build Specification for an AI Coding Agent

> **Project:** SkillRoute — Career Skill-Gap Analysis and Adaptive Learning Recommendation System  
> **Purpose:** Build a complete, credible, locally runnable machine-learning application for an academic ML project.  
> **Primary instruction:** Implement the product and verify it works. Do not merely produce a mockup, a static dashboard, or a collection of disconnected pages.

---

## 1. Your Role and Working Rules

Act as a senior full-stack engineer, applied machine-learning engineer, product designer, and test engineer. Work inside the existing repository if one exists. Inspect it before changing anything.

### Non-negotiable rules

1. Start by inspecting the repository, existing code, package files, environment, and current Git state. Do not overwrite working code without understanding it.
2. Write a short implementation plan and then execute it. Do not stop after presenting the plan.
3. Build a coherent end-to-end product with working navigation, forms, database persistence, trained models, recommendations, and tests.
4. Do not use fake buttons, dead links, placeholder pages, empty charts, hardcoded prediction results, or simulated API success.
5. Never claim a model was trained, a test passed, a file was uploaded, or a record was saved unless that action actually happened.
6. Use deterministic seeds for reproducible training and test fixtures where appropriate.
7. Do not invent model accuracy. Calculate metrics from a real held-out test set and show the evaluation method and sample size.
8. If a real dataset is unavailable, create a clearly labelled synthetic educational dataset and document its limitations. Never describe synthetic records as real students or real placement outcomes.
9. Avoid adding an LLM, paid API, or external service just to make the project appear more advanced. The core product must work locally without an API key.
10. Do not put secrets, API keys, credentials, or personal student information in source control.
11. Make sensible decisions without repeatedly asking the user questions. Record important assumptions in `docs/DECISIONS.md`.
12. Do not copy the source code, branding, text, or exact UI of another product. Use references only to understand workflows and quality expectations.
13. Keep the implementation maintainable: meaningful modules, clear types, validation, error handling, logging, and tests.
14. When a command fails, inspect the error and fix the underlying issue. Do not silently skip it or claim success.
15. If the project is too large to complete in one pass, finish a tested vertical slice first, then proceed in prioritized phases. Do not leave the app in a broken intermediate state.

---

## 2. Product Vision

SkillRoute helps students and early-career learners answer five questions:

- What skills do I currently have?
- What skills does my target role require?
- Which gaps should I address first, and why?
- What should I study and practise next?
- How should my learning plan change after I complete an assessment?

The product must turn a learner profile into an explainable learning plan, then update the plan using new assessment evidence.

### Product differentiator

Do not build only a career-matching form that calculates skill overlap. Build a complete workflow:

**Profile → Evidence → Role requirements → Skill-gap analysis → Prioritized plan → Learning resources → Assessment → Skill update → Adaptive re-planning**

The system must distinguish between:
- A skill claimed by the learner.
- A skill supported by a completed project or assessment.
- A skill inferred by a model.
- A skill requirement defined by the role dataset.

Never present an inference as verified fact.

### Intended users

- Students preparing for internships and graduate roles.
- Learners trying to understand technical skill gaps.
- Project evaluators who need to inspect the actual ML methods and their performance.

### Explicit non-goals for the first version

- No promise that the application can guarantee placement or hiring.
- No automated scraping of job websites without permission.
- No fake live job-market statistics.
- No mandatory paid AI API.
- No real-time multi-user collaboration requirement.
- No unnecessary microservices or complex cloud infrastructure.

---

## 3. Reference Research and Product Inspiration

Review these references for broad product patterns before implementation:

- EduPath example: https://github.com/Shivendra1230/EduPath
- Career Recommendation System example: https://github.com/abhinavxjha/CareerRecommendationSystem
- PathFinder example: https://github.com/VadlaLaxmi26/PathFinder
- scikit-learn getting started: https://scikit-learn.org/stable/getting_started.html
- scikit-learn Pipeline: https://scikit-learn.org/stable/modules/generated/sklearn.pipeline.Pipeline.html

Use references to understand patterns such as:
- Evidence-informed skill analysis.
- Role requirements and skill-gap views.
- Dependency-aware learning plans.
- Progress tracking and re-planning.
- Model pipelines and proper held-out evaluation.

Do not clone an existing repository. Do not claim features from a reference exist in this project unless they have been implemented and tested. If web access is unavailable, continue using this specification and document that the references were not inspected.

---

## 4. Preferred Technical Stack

First inspect the current repository. If it already has a coherent stack, preserve it unless there is a strong reason to change it.

For a new repository, use the following pragmatic stack:

### Application
- Python 3.11 or 3.12.
- Streamlit for the first working UI.
- Pandas and NumPy for data processing.
- scikit-learn for conventional ML algorithms.
- Plotly for interactive charts.
- SQLite for local persistence.
- SQLAlchemy or a small well-structured repository layer for database access.
- Pydantic for validating structured inputs and outputs where useful.
- pytest for tests.
- joblib for serializing trusted, locally trained scikit-learn models.

### Engineering requirements
- Use a virtual environment.
- Pin or constrain compatible dependency versions in `requirements.txt`.
- Provide `.env.example` only if configuration is needed.
- Keep generated models, database files, caches, uploaded private files, and secrets out of Git unless a small, explicitly public demo artifact is intentionally included.
- Never load untrusted pickle/joblib files.
- Provide Windows PowerShell setup instructions as well as macOS/Linux instructions.
- The core application must function without internet access after dependencies are installed.

Do not add React, a separate API server, Docker, LangChain, or a hosted database by default. Add them only if the existing repository already uses them or there is a demonstrated requirement.

---

## 5. Required User Experience

Create a polished, credible academic product that feels like a small real software product rather than a generic AI-generated template.

### Visual direction

- Product name: SkillRoute.
- Use a restrained professional palette, consistent spacing, readable typography, and a clear hierarchy.
- Avoid excessive gradients, glowing cards, random emoji, oversized headings, fake terminal panels, and decorative elements with no function.
- Use a consistent sidebar or navigation system.
- Use real labels, helper text, validation messages, empty states, loading states, success messages, and error states.
- Tables must be readable and support filtering or sorting where appropriate.
- Charts must have titles, axes, units, legends where necessary, and meaningful tooltips.
- Provide accessible contrast, keyboard-friendly controls, and sensible mobile-width behavior.
- Do not display fabricated user avatars, testimonials, company logos, placement counts, or social proof.
- Avoid a dashboard filled with cards that all display arbitrary percentages.
- Keep text concise and useful. Explain what a result means and what action the learner can take.

### Navigation and pages

Implement these pages or their equivalent in the chosen framework:

1. **Overview**
   - Current target role.
   - Learning objectives completed and remaining.
   - Most important skill gaps.
   - Next recommended action.
   - Recent assessment results.
   - A visible notice when the profile or dataset is only demo/synthetic data.

2. **Learner Profile**
   - Name or nickname (optional).
   - Target role.
   - Experience level.
   - Skills and self-ratings.
   - Weekly study time.
   - Preferred learning style or resource type (optional).
   - Project experience and evidence notes.
   - Validate all values; do not require unnecessary personal data.

3. **Career Roles**
   - Browse curated target roles.
   - View role description, required competencies, importance weights, and prerequisite relationships.
   - At minimum include Software Development Engineer, Data Analyst, Data Scientist, and Machine Learning Engineer.
   - Make role requirements editable through a maintainable data file or admin/editor interface.

4. **Skill Gap Analysis**
   - Compare current estimated skill level with target role requirement.
   - Show current level, target level, gap, requirement weight, confidence/evidence type, and priority.
   - Explain the priority formula in the UI or a help section.
   - Do not confuse self-reported skill ratings with objective test results.

5. **Learning Roadmap**
   - Order topics using prerequisite dependencies and gap priority.
   - Each objective must include learning outcome, estimated effort, prerequisites, resource links, practice task, and completion criteria.
   - Provide controls to mark an objective as started or completed.
   - Persist progress.
   - Never mark a topic complete just because it was recommended.

6. **Assessment / Practice**
   - Include a small set of meaningful, locally stored questions or tasks for selected skills.
   - Support submitting answers, recording results, and showing feedback.
   - Validate answers server-side/in application logic, not only with frontend state.
   - Store attempt date, score, skill, and assessment version.
   - Clearly distinguish assessment performance from an official certification.

7. **Adaptive Learning**
   - Display the learner state before and after an assessment.
   - Explain why the next recommended action changed.
   - Implement Q-Learning in a small, testable environment, not merely a decorative chart.
   - Show action choices, reward definition, and policy outcome in a transparent way.
   - Include a deterministic baseline strategy for comparison.

8. **Model Lab**
   - Display the models actually implemented and trained.
   - Show the dataset source, target variable, feature list, split strategy, random seed, and evaluation metrics.
   - Allow a learner/evaluator to compare supported algorithms.
   - Show confusion matrix and classification report for classifiers, or MAE/RMSE/R² for regression where appropriate.
   - Do not display fabricated accuracy, fake training duration, or nonexistent model files.
   - Include an explicit warning that educational/demo data does not establish real-world hiring validity.

9. **Progress & Reports**
   - Learning objectives completed.
   - Assessment history.
   - Skill-level changes over time.
   - Current and historical gap summaries.
   - Export a CSV or printable report if implemented; make the export button functional.
   - Never imply that a readiness estimate is a hiring probability.

10. **Settings / About**
    - Explain data storage and reset behavior.
    - Provide an intentional reset-demo-data action with confirmation.
    - Show dataset provenance and limitations.
    - Provide project methodology and model limitations.

If using Streamlit multipage navigation, keep page organization consistent and do not create duplicate navigation systems.

---

## 6. Functional Requirements

### 6.1 Profile and skill input
- Allow users to create or edit a learner profile.
- Use a documented skill-rating scale, such as 0–5:
  - 0 = no exposure.
  - 1 = basic awareness.
  - 2 = can solve guided tasks.
  - 3 = can complete common tasks independently.
  - 4 = can handle complex tasks.
  - 5 = can demonstrate advanced, consistent performance.
- Explain that self-rating is subjective.
- Allow an assessment result to update a skill estimate using a transparent rule.
- Keep self-reported rating and assessment-derived evidence as separate fields.

### 6.2 Role and competency data
Store roles and competencies in structured JSON/CSV or database tables. Avoid burying the entire dataset in UI code.

Each role should include:
- Stable role ID.
- Name and description.
- Skill IDs.
- Target proficiency for each skill.
- Importance weight.
- Prerequisite skill IDs or dependency edges.
- Curated learning resources with title, provider, URL, and relevant skill.
- At least one practical project or validation task.

Seed enough role and skill data to make the demo useful, not a giant unverified list. Start with approximately 4–6 roles and 15–25 reusable skills.

### 6.3 Skill-gap calculation
Implement a documented, deterministic baseline formula.

For skill `s`:
- `current_level(s)` is based on the selected evidence policy.
- `target_level(s)` is the target role requirement.
- `gap(s) = max(0, target_level(s) - current_level(s))`.
- `importance(s)` is a documented non-negative role weight.
- `priority(s)` should combine gap, importance, and prerequisite relevance using a transparent normalized formula.

Normalize scores consistently. Handle missing skill values explicitly; do not silently treat missing data as expert proficiency or as zero unless that policy is stated.

Show the components of the priority score. A user must be able to understand why a skill is prioritized.

### 6.4 Prerequisite-aware roadmap
- Model prerequisites as a directed graph.
- Detect cycles and report invalid role data.
- Respect prerequisites before recommending dependent topics where possible.
- When two skills are available at the same stage, use gap priority as a tie-breaker.
- Avoid duplicate objectives.
- Recompute the roadmap when the target role, skill evidence, available study time, or completed objectives change.
- Explain when a dependency prevents a high-gap skill from being recommended immediately.

### 6.5 Learning resources
- Use a small curated resource catalogue.
- Prefer stable, reputable documentation and learning resources.
- Include source URLs as clickable links.
- Do not invent courses, providers, prices, reviews, or URLs.
- If a resource cannot be verified, mark it as a search suggestion rather than a verified resource.
- Do not scrape websites in the background.

---

## 7. Machine Learning Design

Use real model implementations from scikit-learn or a clearly documented custom algorithm. Do not implement algorithms only as labels in a dropdown.

### 7.1 Core models for the first version

Prioritize these models:

**A. Regression**
- Multiple Linear Regression or Ridge Regression.
- Predict a numeric learning/assessment outcome only when the dataset has a defensible numeric target.
- Evaluate with MAE, RMSE, and R².
- Explain that R² may be negative and may be unreliable on small test sets.
- Do not use a fabricated “placement probability” as the regression target.

**B. Classification**
- Logistic Regression.
- Decision Tree classifier.
- Optional SVM or MLP if data volume and time allow.
- Define the target label explicitly, such as a synthetic assessment mastery category.
- Evaluate with stratified train/test split where suitable, precision, recall, F1-score, confusion matrix, and accuracy.
- Include class balance and test-set size.
- Never use the model to make a real hiring decision.

**C. Clustering**
- K-Means on appropriately scaled skill features.
- Use scaling in a pipeline.
- Show cluster profiles and explain that cluster labels such as “beginner” or “advanced” are interpretations, not ground truth.
- Report a suitable unsupervised diagnostic such as silhouette score only when its assumptions and sample size permit.
- Do not claim clustering predicts an outcome.

**D. Reinforcement Learning**
- Implement a small tabular Q-Learning environment for choosing the next learning action.
- State should include a compact, interpretable representation of current mastery/gap and recent assessment performance.
- Actions should represent feasible next learning activities, such as reviewing a prerequisite, practising a weak skill, or advancing to a harder task.
- Rewards should reflect learning progress and task success, with penalties for repeatedly selecting an unsuitable task or wasting an action.
- Document state discretization, actions, reward function, learning rate, discount factor, exploration policy, and stopping condition.
- Use a fixed seed for reproducible examples.
- Compare the learned policy against a simple baseline, such as highest-priority eligible gap first.
- Do not claim that Q-Learning is “trained on real students” unless genuine, ethically obtained interaction data exists.
- If there is no real interaction dataset, label it as a simulated educational environment and report simulation limitations.

### 7.2 Additional syllabus algorithms
If time allows, add these as optional comparisons:
- Polynomial Regression.
- LASSO and Elastic Net.
- K-Nearest Neighbors.
- Gaussian Naive Bayes.
- SVM with linear or RBF kernel.
- MLPClassifier.
- PCA for visualization.
- Gaussian Mixture Models.
- Bayesian Network only if a reliable, explainable implementation and appropriate dependency are available.

Do not try to include every syllabus algorithm at the expense of correctness. The core system must be sound before optional algorithms are added.

### 7.3 Correct model evaluation
- Split data into training and test sets before fitting transformations or selecting features based on outcomes.
- Put scaling, imputation, and model fitting inside scikit-learn Pipelines where appropriate.
- Fit preprocessing only on training data.
- Use stratification for classification when suitable and possible.
- Use cross-validation for model selection only on training data.
- Do not repeatedly tune against the test set.
- Keep the held-out test set out of preprocessing fit, feature selection, and hyperparameter tuning.
- Avoid target leakage and duplicate learner records crossing splits.
- If multiple records belong to the same simulated learner, use a group-aware split where appropriate.
- Document the target definition, feature provenance, known bias, class imbalance, and limits of generalization.
- Save model metadata with model version, timestamp, features, target, data hash or version, split seed, and evaluation summary.
- Fail with a helpful message if there is insufficient data to train a meaningful model.
- Show “not enough data” instead of displaying a misleading metric.

### 7.4 Feature engineering
Build a dedicated feature-preparation module rather than constructing features inside UI callbacks.

Potential features:
- Current proficiency by skill.
- Difference between current and target proficiency.
- Weighted gap total.
- Number of missing prerequisites.
- Assessment score and previous score change.
- Completed project count or evidence count.
- Weekly available study hours.
- Recent attempts or completion rate, when available.

Only use features available at prediction time. Avoid using post-outcome information to predict an earlier outcome. Do not use name, email, roll number, or other identifying information as predictive features.

### 7.5 Dataset policy
Create a documented data folder, for example:
- `data/roles.json`
- `data/skills.json`
- `data/resources.json`
- `data/demo/learner_assessments.csv`
- `data/README.md`

Synthetic data requirements:
- Mark every synthetic dataset clearly in file names and documentation.
- Use a fixed seed and a documented generation process.
- Generate internally consistent skill profiles and targets.
- Avoid creating labels with a trivial direct formula from the same input features if the purpose is to claim predictive performance.
- If a label is generated from rules, explicitly say the model learns those rules in the synthetic benchmark and does not demonstrate real-world generalization.
- Keep a small, understandable sample dataset for the demonstration.
- Include a way to train on a replacement CSV after validating its schema.
- Validate missing values, invalid ranges, duplicates, and target labels.
- Do not include private student records or scrape personal profiles.

A strong academic demo explains the difference between:
1. The deterministic skill-gap engine, which can work from curated role requirements.
2. The supervised models, which learn from labelled examples.
3. The Q-Learning component, which learns a policy within a defined environment.

Do not disguise deterministic rules as machine learning.

---

## 8. Q-Learning: Required Implementation Detail

Create a small standalone module and tests.

Suggested structure:
- `state`: coarse skill mastery level, most recent assessment band, and whether prerequisite work is pending.
- `actions`: `review_prerequisite`, `practice_weak_skill`, `advance_skill`, and `review_mistakes`.
- `reward`: positive for demonstrated improvement and successful completion; modest negative reward for an unsuitable or repeated action; neutral or small cost for time-consuming actions.
- `Q[state, action]`: tabular values initialized consistently.
- Epsilon-greedy action selection during training.
- Bellman update:
  `Q(s, a) = Q(s, a) + alpha * (r + gamma * max_a_prime Q(s_prime, a_prime) - Q(s, a))`
  Use the terminal-state variant without a future-state value when the episode ends.
- Document the meaning of `alpha`, `gamma`, and `epsilon`.
- Seed random number generators.
- Save learned values using a safe, documented format such as JSON or NumPy's non-pickle format.
- Add tests proving that the Q-value update is correct, terminal transitions are handled, and the selected action belongs to the allowed action set.
- Compare against the deterministic priority baseline over multiple seeded simulation episodes.
- Report the reward definition and evaluation procedure, not just a reward chart.
- Make clear that simulated reward improvement does not establish real educational efficacy.

---

## 9. Suggested Project Structure

Adapt this to the existing repository rather than forcing a restructure.

```text
skillroute/
├── app.py
├── requirements.txt
├── README.md
├── PROMPT.md
├── .gitignore
├── .env.example
├── data/
│   ├── README.md
│   ├── roles.json
│   ├── skills.json
│   ├── resources.json
│   └── demo/
│       └── learner_assessments.csv
├── models/
│   ├── __init__.py
│   ├── train.py
│   ├── evaluate.py
│   ├── predict.py
│   └── artifacts/
│       └── .gitkeep
├── skillroute/
│   ├── __init__.py
│   ├── config.py
│   ├── schemas.py
│   ├── database.py
│   ├── repositories/
│   ├── services/
│   │   ├── profile_service.py
│   │   ├── gap_analysis.py
│   │   ├── roadmap.py
│   │   ├── assessment.py
│   │   └── reporting.py
│   ├── ml/
│   │   ├── features.py
│   │   ├── pipelines.py
│   │   ├── metrics.py
│   │   └── model_registry.py
│   └── reinforcement/
│       ├── environment.py
│       ├── q_learning.py
│       └── baseline.py
├── pages/
│   ├── 1_Profile.py
│   ├── 2_Career_Roles.py
│   ├── 3_Skill_Gaps.py
│   ├── 4_Learning_Roadmap.py
│   ├── 5_Assessments.py
│   ├── 6_Adaptive_Learning.py
│   ├── 7_Model_Lab.py
│   ├── 8_Progress.py
│   └── 9_About.py
├── tests/
│   ├── test_gap_analysis.py
│   ├── test_roadmap.py
│   ├── test_database.py
│   ├── test_features.py
│   ├── test_ml_training.py
│   ├── test_metrics.py
│   ├── test_q_learning.py
│   └── test_data_validation.py
└── docs/
    ├── ARCHITECTURE.md
    ├── DATA_DICTIONARY.md
    ├── MODEL_CARD.md
    ├── DECISIONS.md
    └── DEMO_SCRIPT.md
```

Do not create empty files just to match this tree. Every created module should have a real responsibility.

---

## 10. Database and Persistence

Use SQLite for the local first version.

Minimum logical entities:
- `learner_profiles`
- `learner_skills`
- `skill_evidence`
- `roles`
- `role_requirements`
- `learning_objectives`
- `learner_objective_progress`
- `assessment_attempts`
- `model_runs` or `model_metadata`

Requirements:
- Use stable IDs and appropriate foreign keys.
- Create tables through a repeatable initialization or migration path.
- Use parameterized queries or a safe ORM.
- Validate data before persistence.
- Handle duplicate submissions and update operations sensibly.
- Keep assessment history rather than overwriting every previous result.
- Make demo seed operations idempotent.
- Provide an explicit data reset workflow with a confirmation step.
- Do not silently erase user data when the app starts.
- Handle missing/corrupt database files with a clear, actionable error.
- Never store passwords in plaintext. If authentication is not required for the local prototype, do not build a fake login screen.

---

## 11. Application Reliability and Security

- Validate every user input and uploaded CSV.
- Restrict upload size and accepted file types if file upload is supported.
- Do not execute uploaded files or spreadsheet formulas.
- Escape or safely render user-provided text.
- Do not expose internal stack traces to normal users; log useful details for debugging.
- Avoid global mutable state that mixes learners' data.
- Ensure user-triggered actions persist correctly after page reruns.
- Avoid a hidden dependency on the developer's local file paths.
- Use relative paths resolved from the project root.
- Handle missing model artifacts gracefully; offer a real training action or a clear explanation.
- Use sensible timeouts for any optional network call.
- Keep the default workflow offline-capable.
- Add an appropriate `.gitignore` for virtual environments, caches, local databases, uploaded data, secrets, and generated artifacts.
- Do not claim production-grade privacy or security without a review.

---

## 12. Testing Requirements

Write meaningful tests before declaring the project complete.

### Unit tests
- Gap is never negative.
- Skill priority follows the documented formula.
- Missing values follow the declared policy.
- Role data with circular prerequisites is rejected or reported.
- Roadmap order respects prerequisites.
- Completed objectives do not reappear as incomplete.
- Invalid skill ratings are rejected.
- CSV schema and labels are validated.
- Q-Learning updates match the documented equation.
- Terminal Q-Learning transitions do not bootstrap from future values.
- A model pipeline can fit and predict on a small valid fixture.
- Evaluation metrics are computed from the held-out data.
- Insufficient training data produces a helpful error rather than fabricated output.

### Integration tests
- A learner profile can be created, updated, and loaded from SQLite.
- Skill evidence can be saved and retrieved.
- An assessment submission is recorded.
- Completing an objective persists after reload.
- An assessment result changes the gap analysis only according to the documented evidence-update rule.
- The adaptive recommendation service returns a valid action.
- Report export produces a valid file with expected columns.
- The app starts without a hosted API key.

### UI / smoke tests
- The main page loads.
- Every navigation item opens the correct page.
- Empty-state and validation flows work.
- A complete demo workflow can be performed without editing the source.
- No button is decorative: every visible action has a meaningful effect or is clearly disabled with an explanation.

Run tests and fix failures. Report the exact commands run and their actual results.

---

## 13. Documentation Deliverables

### `README.md`
Include:
- Project purpose and scope.
- Screenshots only if they are actual screenshots of the running application.
- Feature list.
- Architecture overview.
- Technology stack.
- Setup instructions for Windows PowerShell and macOS/Linux.
- How to run the app.
- How to seed data.
- How to train models.
- How to run tests.
- Dataset provenance and limitations.
- Model evaluation approach.
- Known limitations and future work.

### `docs/ARCHITECTURE.md`
Explain data flow, service boundaries, model training/inference separation, persistence, and adaptive learning loop.

### `docs/DATA_DICTIONARY.md`
Document each dataset and database field, units, ranges, missing-value policy, and source.

### `docs/MODEL_CARD.md`
For every trained model, include:
- Intended use.
- Out-of-scope uses.
- Dataset source and whether synthetic.
- Sample count and label distribution.
- Features and target.
- Train/test split and seed.
- Preprocessing.
- Metrics with actual values.
- Known limitations, bias, and leakage checks.
- Reproduction command.

### `docs/DECISIONS.md`
Record material technical decisions and trade-offs.

### `docs/DEMO_SCRIPT.md`
Provide a 3–5 minute demo with one complete learner scenario, including a weak assessment result, the resulting roadmap change, and a Model Lab explanation.

---

## 14. Implementation Phases

Complete these phases in order. Keep the app runnable at the end of each phase.

### Phase 0 — Inspect and plan
- Inspect repository and Git status.
- Identify existing code and constraints.
- Document architecture decisions.
- Identify missing dependencies and available Python version.
- Do not delete user files.

### Phase 1 — Foundation
- Create project configuration and dependency file.
- Create role/skill/resource schemas and seed data.
- Set up SQLite initialization and repositories.
- Add input validation and core unit tests.
- Build a minimal but polished app shell with navigation.

### Phase 2 — Core product
- Implement profile CRUD.
- Implement role browsing.
- Implement skill-gap calculation.
- Implement prerequisite-aware roadmap.
- Implement persistent progress tracking.
- Add meaningful empty and error states.
- Test the full flow.

### Phase 3 — Assessments and adaptation
- Implement assessment questions and submissions.
- Store assessment history.
- Implement the explicit skill-evidence update policy.
- Implement Q-Learning and deterministic baseline.
- Add policy comparison and tests.
- Show why the next action was selected.

### Phase 4 — Machine learning
- Validate the dataset.
- Build reusable preprocessing pipelines.
- Train core regression/classification/clustering models where their data requirements are met.
- Evaluate them properly.
- Save model artifacts and metadata.
- Build the Model Lab using actual metrics and artifacts.
- Add tests for training, prediction, and insufficient-data handling.

### Phase 5 — UI quality
- Review typography, spacing, layout, labels, charts, tables, and responsiveness.
- Check all controls and navigation.
- Remove placeholder content and decorative fake statistics.
- Improve loading, empty, success, and failure states.
- Test the complete demo scenario.

### Phase 6 — Verification and delivery
- Run unit and integration tests.
- Run linting/type checks if configured.
- Run the app and perform a smoke test.
- Verify setup instructions in a clean environment when feasible.
- Fix all reproducible failures.
- Update README and docs to match the implementation.
- Provide a concise completion report with changed files, features, commands run, test results, and remaining limitations.

---

## 15. Acceptance Criteria — Definition of Done

The project is not complete until all applicable criteria below are satisfied:

- [ ] The application launches locally using documented commands.
- [ ] The first-run experience works with seeded demo data.
- [ ] Learner profile data persists across reloads.
- [ ] Role requirements are stored as data and are inspectable.
- [ ] Skill gaps and priorities are calculated by real, tested logic.
- [ ] Roadmap sequencing respects prerequisites.
- [ ] Assessments accept answers and persist actual attempts.
- [ ] Completing a learning objective changes persisted progress.
- [ ] New assessment evidence can trigger a documented roadmap update.
- [ ] Q-Learning is a real implementation with tested updates and a baseline comparison.
- [ ] At least one supported supervised model is actually trained when enough valid data is present.
- [ ] Model Lab metrics come from the real held-out evaluation, not hardcoded constants.
- [ ] Clustering results, if shown, come from a fitted model and are interpreted cautiously.
- [ ] Synthetic data is explicitly labelled in the UI and documentation.
- [ ] No page claims real placement prediction or guaranteed hiring outcomes.
- [ ] Important features work without any API key.
- [ ] The database reset is deliberate and confirmed.
- [ ] No obvious dead buttons, broken links, fake metrics, or placeholder pages remain.
- [ ] Automated tests pass, or any remaining failure is precisely reported and justified.
- [ ] Setup, model training, evaluation, and test commands are documented.
- [ ] The final report truthfully distinguishes completed features from limitations.

---

## 16. Required Final Response From the Coding Agent

When finished, respond with:

1. **What was implemented** — concise feature summary.
2. **Architecture** — major modules and data flow.
3. **ML methods** — which algorithms are actually implemented, their target variables, and evaluation method.
4. **Dataset** — sources, number of records, and whether synthetic.
5. **How to run** — exact commands for the current environment.
6. **How to train models** — exact command and output location.
7. **How to test** — exact command and actual result.
8. **Important files changed** — paths and purpose.
9. **Known limitations** — honest and specific.
10. **Next steps** — only if necessary.

Do not say “everything works” unless the app was run and the relevant tests were actually executed. If anything remains incomplete, state it plainly.

---

## 17. Start Here

Now inspect the existing repository. Then implement SkillRoute according to this specification, starting with the smallest complete end-to-end workflow. Make real code changes, run the application, test the workflow, and iterate until the acceptance criteria are met. Do not stop at an architecture proposal or a visual mockup.
