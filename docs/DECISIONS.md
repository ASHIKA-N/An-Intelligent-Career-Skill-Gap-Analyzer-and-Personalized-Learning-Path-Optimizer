# Implementation plan and decisions

1. Foundation: Python/Streamlit, a curated JSON catalogue, SQLite repository and validated inputs.
2. Core: profile, evidence-aware gaps, dependency ordering and persisted objectives.
3. Adaptation: versioned assessments, explicit evidence updates and seeded tabular Q-learning.
4. ML: independent synthetic learner records; held-out Ridge, logistic/tree classification and scaled K-Means.
5. Verification: service tests, Streamlit AppTest navigation and a complete assessment workflow.

The initial repository contained only .git, with a clean Git status. Python 3.14 is the available interpreter; dependency constraints permit compatible wheels. No existing code was replaced. The attached PROMPT (3).md is copied as PROMPT.md.

This is a single-user local prototype, with no authentication. Self-ratings and project notes remain claims; only locally scored assessments supply assessment evidence. Missing ratings default explicitly to zero. Latest assessment replaces the current estimate (score / 100 * 5), while preserving the self-rating and all attempts. Short quizzes are limited evidence, not certifications.

Completed objectives persist across role changes; assessment weakness can reopen a completed objective for practice without deleting its completion record. Roadmaps use dependency closure, including prerequisite skills outside the role. Study hours determine the estimated schedule. Resource preferences are recorded for learner context; the small catalogue does not yet personalize resource formats.

References inspected: https://github.com/Shivendra1230/EduPath , https://github.com/abhinavxjha/CareerRecommendationSystem , https://github.com/VadlaLaxmi26/PathFinder and scikit-learn getting-started/Pipeline documentation. Used only for workflow and pipeline patterns; no source copied. Core workflow remains offline.
