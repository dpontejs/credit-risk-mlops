# credit-risk-mlops — Design & Roadmap

> Status: approved · Created 2026-11-10 · Owner: Diego Ponte
> This file is both the project design and the living progress tracker.
> Progress updates: tick the boxes and update the bars at the end of each milestone.

## 1. Intent

A credit default risk system on Google Cloud that covers the **full lifecycle of a classical ML
project**: big-data feature engineering, training pipelines, registry, serving, monitoring and
operations. It is Diego's flagship classical-ML portfolio project, aimed at ML Engineer roles at
banks, credit bureaus and big tech (US market as the reference).

**Why:** Diego already trains and registers deep learning models in production (MLflow, champion
promotion, Kubernetes executors, GitLab CI). What he has not done himself — and cannot yet talk
about in interviews — is: Spark at scale, managed cloud ML pipelines (Vertex AI), and *operating*
a model in production (monitoring, drift, alerts, rollout/rollback, incidents).

**What a reviewer should conclude in 5 minutes:** "this person has run an ML system in production,
not just trained a model."

## 2. Goals, non-goals, anti-goals

**Goals**
- Cover the 9 lifecycle phases below, end to end, running on GCP.
- Finish, alongside the project: the book *Designing Machine Learning Systems* (Chip Huyen), the
  DataCamp **Machine Learning Engineer** track, the DataCamp **Professional ML Engineer with
  Google Cloud** track and the DataCamp **Big Data with PySpark** track.
- Be ready for (and ideally pass) the **Google Cloud Professional Machine Learning Engineer** exam.
- One LinkedIn post per completed phase, tying what was built to the book chapter behind it.

**Non-goals**
- GenAI / agents (covered by Diego's other project). Explainability here is classical (SHAP,
  reason codes).
- Deep learning. A gradient-boosted model is the right tool for tabular credit data.
- Chasing leaderboard AUC. A solid model with honest evaluation beats a tuned-to-death one.
- Kafka / real-time streaming. Possible future extension (Pub/Sub + Spark Structured Streaming),
  not part of this roadmap.

**Anti-goals (failure even if it "works")**
- A notebook-driven project with a deployed endpoint and nothing else — that is what every
  portfolio has.
- Infrastructure clicked together in the console that nobody can reproduce.
- Surprise cloud bills.
- Copying course/tutorial code without understanding it — every phase must be explainable in an
  interview, which is what `docs/guide/` is for.

## 3. Constraints

- **Budget:** stay within the GCP free-trial credit (US$300). Budget alert from day one; endpoints
  and clusters are torn down after every demo. **The free trial expires 90 days after activation**,
  so do everything that can run locally first (PySpark local, pipeline code, tests) and activate the
  trial only when cloud work starts in M1 (2026-12-01).
- **Timebox: 90 days, 2026-11-10 → 2027-02-08** (M0–M3), with dated milestones below. Weekly
  hours are unknown, so dates are targets: if a milestone slips, re-plan the next ones instead of
  silently extending. The free trial is activated on **2026-12-01** (start of M1), so it expires
  ~2027-03-01 — three weeks of buffer after M3.
- **After the trial** *(Claude's call, pending Diego's budget answer)*: nothing keeps running in the
  cloud. All resources are destroyed with Terraform; the README keeps recorded results
  (screenshots, metrics, costs) and the system can be stood up again on demand.
- **Public repo:** `github.com/dpontejs/credit-risk-mlops`. No secrets, no credentials in git;
  CI authenticates to GCP via Workload Identity Federation.
- **Language:** code, docs and guide pages in English (same as Diego's other public repos).
- **AI-assisted coding:** this file is the context entry point for coding sessions. Each phase is
  planned in detail only when the previous one is done (what Diego learns changes the next plan).

## 4. Decisions already made

| Topic | Decision |
|---|---|
| Domain / data | Credit default risk, **Home Credit Default Risk** (Kaggle): 7 relational tables, `bureau_balance` ~27M rows, `installments_payments` ~13.6M — large enough to justify Spark. |
| Cloud | **GCP** (Vertex AI, Dataproc Serverless, BigQuery, GCS, Cloud Monitoring). |
| Big data | **PySpark**, developed locally, run on Dataproc Serverless. |
| Model | Gradient boosting (LightGBM or XGBoost) with a logistic-regression baseline. |
| IaC / CI | Terraform + GitHub Actions. |
| Explainability | SHAP + per-prediction **reason codes** (mirrors US adverse-action notice requirements). |
| Docs | `docs/guide/NN-<topic>.md` per phase: concepts, decisions, commands, exercises, pitfalls. |
| Terraform timing | *(Claude's call)* From the **first cloud resource** in M1 — no console-clicked infra ever. M3 only completes and documents it. |
| Protected attributes | *(Claude's call)* `CODE_GENDER` and age (`DAYS_BIRTH`) are **excluded from model features** (ECOA) but kept for the fairness audit. Fairness metric: disparate impact ratio + equal-opportunity difference across those groups; promotion thresholds set in Phase 3 from the baseline's numbers. |
| Planning granularity | *(Claude's call)* Detailed plans cover one milestone/phase at a time. Cross-phase decisions (GCP project layout, how time/drift/label delay are simulated) are settled in the **first** phase plan that touches them: layout in M0, simulation in Phase 1. |

## 5. Lifecycle phases

| # | Phase | What gets built |
|---|---|---|
| 1 | Data + PySpark | Raw tables in GCS → Spark aggregations/joins → feature table (Parquet + BigQuery). |
| 2 | Data quality | Schema/completeness/range checks (Great Expectations); pipeline stops on bad data. |
| 3 | Experimentation | Baseline vs GBM, tuning, credit metrics (AUC, KS, calibration), fairness by group, tracked in Vertex Experiments. |
| 4 | Training pipeline | Vertex AI Pipelines (KFP): validate → features → train → evaluate; data and model versioned. |
| 5 | Registry + promotion | Vertex Model Registry; challenger replaces champion only if it passes automatic gates. |
| 6 | Serving | Online endpoint with a latency SLO (p95 measured) + batch scoring job. |
| 7 | Monitoring | Feature/prediction drift, performance when labels arrive, alerts in Cloud Monitoring. |
| 8 | Operations | Canary via traffic split, rollback, drift-triggered retraining, simulated incidents with runbook + post-mortem. |
| 9 | Engineering | Terraform for all infra, CI/CD, tests, README with architecture, decisions, measured cost and latency. |

## 6. Roadmap

Each phase follows **Study → Build → Done when → Post**.
Book = *Designing Machine Learning Systems*. MLE = DataCamp ML Engineer track.
GCP = DataCamp PMLE with Google Cloud track. PS = DataCamp Big Data with PySpark track.

### M0 — Foundation · 2026-11-10 → 2026-11-30 (3 weeks, local only)
- **Study**
  - [ ] Book ch. 1–2 (overview, ML systems design)
  - [ ] PS: full track
  - [ ] MLE: course 1 (name to confirm), Introduction to Shell, Introduction to Docker, Introduction to MLflow *(quick reviews)*
  - [ ] MLE: MLOps Concepts
  - [ ] GCP: Build a Certification Study Guide: ACE Exam Prep, Introduction to AI and ML on Google Cloud
- **Build**
  - [ ] Repo skeleton (uv, ruff, pytest, pre-commit), GitHub Actions running tests
  - [ ] Download Home Credit; EDA notebook documenting tables, keys, sizes, target imbalance
  - [ ] GCP project + budget alert + Terraform state bucket *(can wait until M1 to save trial days)*
- **Done when:** CI is green on an empty-but-tested package; EDA explains every table and join key.
- **Post:** why this project, and what I plan to learn.

### M1 — End to end *(first CV-ready version)* · 2026-12-01 → 2027-01-04 (5 weeks, includes holidays)
- **Phase 1 — Data + PySpark**
  - Study: [ ] Book ch. 3 · [ ] MLE: ETL and ELT in Python
  - Build: [ ] Spark feature jobs (local + Dataproc Serverless) · [ ] feature table in BigQuery
  - Done when: job runs on Dataproc from a single command; runtime and cost recorded.
- **Phase 2 — Data quality**
  - Study: [ ] Book ch. 4 · [ ] MLE: Introduction to Data Quality with Great Expectations
  - Build: [ ] expectation suite on raw and feature data · [ ] failing check blocks the pipeline
  - Done when: a deliberately corrupted file makes the pipeline fail with a readable report.
- **Phase 3 — Experimentation**
  - Study: [ ] Book ch. 5–6 · [ ] GCP: MLOps with Vertex AI: Model Evaluation
  - Build: [ ] baseline + GBM · [ ] AUC/KS/calibration report · [ ] runs in Vertex Experiments
  - Done when: model choice is justified in a guide page with numbers.
- **Phase 4 — Training pipeline**
  - Study: [ ] Book ch. 10 · [ ] MLE: Introduction to Data Versioning with DVC · [ ] GCP: MLOps Getting Started, MLOps with Vertex AI: Manage Features
  - Build: [ ] Vertex AI Pipeline validate → features → train → evaluate · [ ] dataset/model lineage
  - Done when: one command (or CI trigger) reproduces a trained model from raw data.
- **Phase 5 — Registry + promotion**
  - Study: [ ] MLE: MLOps Deployment and Life Cycling
  - Build: [ ] Vertex Model Registry · [ ] automatic promotion gates (metric + fairness thresholds)
  - Done when: a worse challenger is rejected automatically, a better one is promoted.
- **Phase 6 — Serving**
  - Study: [ ] Book ch. 7 · [ ] GCP: Production Machine Learning Systems
  - Build: [ ] online endpoint · [ ] batch prediction job · [ ] load test with p95 latency and $/1k predictions
  - Done when: README shows measured p95 and cost; endpoint teardown is one command.
- **Post (one per phase):** what I built + the book chapter behind it.

### M2 — Production · 2027-01-05 → 2027-01-25 (3 weeks)
- **Phase 7 — Monitoring**
  - Study: [ ] Book ch. 8 · [ ] MLE: Monitoring Machine Learning Concepts, Monitoring Machine Learning in Python
  - Build: [ ] simulated production traffic with injected drift and delayed labels · [ ] drift + performance monitors · [ ] alert policies
  - Done when: injected drift fires an alert within a defined window.
- **Phase 8 — Operations**
  - Study: [ ] Book ch. 9 · [ ] MLE: CI/CD for Machine Learning
  - Build: [ ] canary with traffic split + rollback · [ ] drift-triggered retraining · [ ] 2+ simulated incidents with runbook and post-mortem
  - Done when: each incident has a timeline, root cause, fix and prevention written up.

### M3 — Polish & responsible AI · 2027-01-26 → 2027-02-08 (2 weeks)
- **Phase 9 — Engineering**
  - Study: [ ] Book ch. 11 · [ ] GCP: Responsible AI: Fairness & Bias, Interpretability & Transparency, Privacy & Safety
  - Build: [ ] all infra in Terraform · [ ] SHAP reason codes in responses · [ ] fairness report · [ ] final README (architecture diagram, decisions, cost, latency)
- **Remaining track courses**
  - [ ] GCP: MLOps for Generative AI, Create Generative AI Apps on Google Cloud
  - [ ] MLE / GCP: any course not yet ticked (bonus projects optional)
- **Done when:** a stranger can stand the whole system up from the README.

### M4 — PMLE certification · 2027-02-09 → exam by ~2027-03-15 (outside the 90-day box; mostly study, little cloud)
- [ ] Read the official PMLE exam guide; map each section to what the project covered
- [ ] Study the gaps not covered by the project
- [ ] Official sample questions + practice exams
- [ ] Book the exam (US$200, 2h) · [ ] **Pass**
- **Post:** certification + project retrospective.

## 7. Progress

| Milestone | Target end | Status |
|---|---|---|
| M0 Foundation | 2026-11-30 | ☐ not started |
| M1 End to end | 2027-01-04 | ☐ not started |
| M2 Production | 2027-01-25 | ☐ not started |
| M3 Polish | 2027-02-08 | ☐ not started |
| M4 Certification | ~2027-03-15 | ☐ not started |

Book: 0/11 chapters · MLE track: 0 courses · GCP track: 0/11 courses · PySpark track: not started

## 8. Left to the builder (decided per phase plan)

- Exact feature set and Spark job layout; LightGBM vs XGBoost.
- Serving container: Vertex prebuilt vs custom FastAPI container.
- Vertex Model Monitoring vs Evidently (or both) for drift.
- How drift and label delay are simulated (Home Credit has no timestamps) — settled in the Phase 1 plan.
- Whether Vertex Feature Store is used or BigQuery tables suffice.
- Package layout, test strategy, guide page breakdown.
