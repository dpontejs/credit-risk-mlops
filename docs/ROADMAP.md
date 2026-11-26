# credit-risk-mlops — Design & Roadmap

> Status: approved · Created 2026-11-10 · Rescheduled 2026-11-23 · **Moved to AWS 2026-11-26** · Owner: Diego Ponte
> This file is both the project design and the living progress tracker.
> Progress updates: tick the boxes and update the bars at the end of each milestone.

## 1. Intent

A credit default risk system on **AWS** that covers the **full lifecycle of a classical ML
project**: big-data feature engineering, training pipelines, registry, serving, monitoring and
operations. It is Diego's flagship classical-ML portfolio project, aimed at ML Engineer roles at
banks, credit bureaus and big tech (US market as the reference).

**Why:** Diego already trains and registers deep learning models in production (MLflow, champion
promotion, Kubernetes executors, GitLab CI). What he has not done himself — and cannot yet talk
about in interviews — is: Spark at scale, managed cloud ML pipelines (SageMaker), and *operating*
a model in production (monitoring, drift, alerts, rollout/rollback, incidents).

His production work (pathotech, digital pathology) is proprietary and cannot be shown publicly.
This repo is therefore his **public showcase**: the place where a reviewer can actually read the
code behind the experience on his CV.

**What a reviewer should conclude in 5 minutes:** "this person has run an ML system in production,
not just trained a model."

**Why AWS (changed from GCP on 2026-11-26):** AWS is the most used cloud in the target market
(US banks included); the **AWS Certified Machine Learning Engineer – Associate (MLA-C02)** beta
costs US$75 until 2027-01-13; and no cloud resource had been created yet, so switching was free.
The local AWS Emulator (`github.com/aws/aws-emulator`) helps with API-level development and CI,
but does not replace real SageMaker/EMR runs.

## 2. Goals, non-goals, anti-goals

**Goals**
- Pass the **AWS MLA-C02** exam (beta, booked for 2027-01-08) before the project resumes.
- Cover the 9 lifecycle phases below, end to end, running on AWS.
- Finish, alongside the project: the book *Designing Machine Learning Systems* (Chip Huyen), the
  DataCamp **Machine Learning Engineer** track and the DataCamp **Big Data with PySpark** track.
  The book *Construindo Aplicações com Agentes de IA* supports the exam's agent topics and M5.
- One LinkedIn post per completed phase, tying what was built to the book chapter behind it.

**Non-goals**
- GenAI / agents **inside the M0–M3 box**. Explainability there is classical (SHAP,
  reason codes). An explanation agent comes later, as the optional extension M5. (The exam's
  GenAI domain is studied, not built, during the certification sprint.)
- Deep learning. A gradient-boosted model is the right tool for tabular credit data.
- Chasing leaderboard AUC. A solid model with honest evaluation beats a tuned-to-death one.
- Kafka / real-time streaming. Possible future extension (Kinesis + Spark Structured Streaming),
  not part of this roadmap.

**Anti-goals (failure even if it "works")**
- A notebook-driven project with a deployed endpoint and nothing else — that is what every
  portfolio has.
- Infrastructure clicked together in the console that nobody can reproduce.
- Surprise cloud bills.
- Copying course/tutorial code without understanding it — every phase must be explainable in an
  interview, which is what `docs/guide/` is for.

## 3. Constraints

- **Budget:** new AWS accounts get up to US$200 in credits (US$100 at sign-up + up to US$100 from
  console activities). The Free plan blocks EMR/Athena and expires after 6 months, so the project
  uses the **Paid plan**: credits still apply, and charges start silently when they run out.
  AWS Budgets alerts + Cost Anomaly Detection from day one; endpoints and jobs are torn down
  after every demo. The account is created only when cloud work starts in M1 (2027-01-25), so
  the credit clock does not run during local work.
- **Timebox:** certification sprint 2026-11-26 → 2027-01-08 (exam), then the project
  2027-01-11 → 2027-04-04 (M0–M3). History: planned as 90 days ending 2027-02-08; paused on
  2026-11-23 for the end of the semester; on 2026-11-26 the AWS exam took priority and the
  project resumes after it. Daily availability is unpredictable, so dates are targets and tasks
  follow plan order: if a milestone slips, re-plan the next ones instead of silently extending.
- **After M3:** nothing keeps running in the cloud. All resources are destroyed with Terraform;
  the README keeps recorded results (screenshots, metrics, costs) and the system can be stood up
  again on demand.
- **Public repo:** `github.com/dpontejs/credit-risk-mlops`. No secrets, no credentials in git;
  CI authenticates to AWS with GitHub OIDC (an IAM role, no access keys).
- **Language:** code, docs and guide pages in English (same as Diego's other public repos).
- **AI-assisted coding:** this file is the context entry point for coding sessions. Each phase is
  planned in detail only when the previous one is done (what Diego learns changes the next plan).

## 4. Decisions already made

| Topic | Decision |
|---|---|
| Domain / data | Credit default risk, **Home Credit Default Risk** (Kaggle): 7 relational tables, `bureau_balance` ~27M rows, `installments_payments` ~13.6M — large enough to justify Spark. |
| Cloud | **AWS** (SageMaker AI, EMR Serverless, S3, Glue Data Catalog + Athena, CloudWatch). Changed from GCP on 2026-11-26, before any cloud resource existed. |
| Big data | **PySpark**, developed locally, run on EMR Serverless. |
| Model | Gradient boosting (LightGBM or XGBoost) with a logistic-regression baseline. |
| IaC / CI | Terraform + GitHub Actions. |
| Local AWS | AWS Emulator for API-level tests (S3 I/O, resource definitions) where it helps; real AWS for SageMaker/EMR runs. Decided per phase. |
| Explainability | SHAP + per-prediction **reason codes** (mirrors US adverse-action notice requirements). |
| Docs | `docs/guide/NN-<topic>.md` per phase: concepts, decisions, commands, exercises, pitfalls. |
| Terraform timing | *(Claude's call)* From the **first cloud resource** in M1 — no console-clicked infra ever. M3 only completes and documents it. |
| Protected attributes | *(Claude's call)* `CODE_GENDER` and age (`DAYS_BIRTH`) are **excluded from model features** (ECOA) but kept for the fairness audit. Fairness metric: disparate impact ratio + equal-opportunity difference across those groups; promotion thresholds set in Phase 3 from the baseline's numbers. |
| Planning granularity | *(Claude's call)* Detailed plans cover one milestone/phase at a time. Cross-phase decisions (AWS account layout, how time/drift/label delay are simulated) are settled in the **first** phase plan that touches them: layout in M0, simulation in Phase 1. |

## 5. Lifecycle phases

| # | Phase | What gets built |
|---|---|---|
| 1 | Data + PySpark | Raw tables in S3 → Spark aggregations/joins on EMR Serverless → feature table (Parquet in S3, registered in the Glue Data Catalog, queried with Athena). |
| 2 | Data quality | Schema/completeness/range checks (Great Expectations); pipeline stops on bad data. |
| 3 | Experimentation | Baseline vs GBM, tuning, credit metrics (AUC, KS, calibration), fairness by group, tracked in SageMaker managed MLflow. |
| 4 | Training pipeline | SageMaker Pipelines: validate → features → train → evaluate; data and model versioned. |
| 5 | Registry + promotion | SageMaker Model Registry; challenger replaces champion only if it passes automatic gates. |
| 6 | Serving | SageMaker real-time endpoint with a latency SLO (p95 measured) + Batch Transform job. |
| 7 | Monitoring | Feature/prediction drift, performance when labels arrive (SageMaker Model Monitor and/or Evidently), CloudWatch alarms. |
| 8 | Operations | Canary via endpoint deployment guardrails (traffic shifting), rollback, drift-triggered retraining, simulated incidents with runbook + post-mortem. |
| 9 | Engineering | Terraform for all infra, CI/CD, tests, README with architecture, decisions, measured cost and latency. |

## 6. Roadmap

Each phase follows **Study → Build → Done when → Post**.
Book = *Designing Machine Learning Systems*. Agents = *Construindo Aplicações com Agentes de IA*.
MLE = DataCamp ML Engineer track. PS = DataCamp Big Data with PySpark track
(6 courses + 1 bonus project, ~25h — spread across M0, M1 and M3). SB = AWS Skill Builder.
The DataCamp PMLE with Google Cloud track was dropped with the move to AWS.

### MC — AWS ML Engineer Associate (MLA-C02 beta) · 2026-11-26 → exam 2027-01-08
Beta: code ME1-C02, US$75, 85 questions / 170 min (+30 min with the ESL accommodation), no
retake during the beta, last bookable day 2027-01-13 (official). The standard MLA-C02 opens in all
languages on 2027-01-14 (US$150). Domains: data preparation 28%, model and
foundation-model development 24%, deployment and orchestration 24%, operations, monitoring and
security 24%. Project and DataCamp courses are paused until the exam; the book continues.
- **Phase 0 — Diagnosis** (until 2026-12-09, light, during the semester)
  - [x] ESL +30 min accommodation approved (2026-11-26, never expires)
  - [ ] Book ME1-C02 for 2027-01-08 (on 2026-12-01, so the payment falls on the next card bill)
  - [ ] Read the official MLA-C02 exam guide; take SB's free official practice questions cold
  - [ ] SB Exam Prep Plan (ML Engineer Associate), in short sessions
  - [ ] Book ch. 7–9 (deployment, data distribution shifts, continual learning)
- **Phase 1 — Content** (2026-12-10 → 2026-12-24)
  - [ ] Domain 1: Glue, Athena, EMR, Kinesis, Data Wrangler, Feature Store · Book ch. 4–5
  - [ ] Domain 2: SageMaker training (built-in algorithms, script mode, automatic model tuning, MLflow)
  - [ ] Domain 2: Bedrock, RAG, embeddings, fine-tuning, agents · Agents book (relevant chapters)
  - [ ] Domain 3: endpoints, Batch Transform, SageMaker Pipelines, Step Functions / MWAA, CI/CD
  - [ ] Domain 4: Model Monitor, Clarify, CloudWatch, IAM / KMS / VPC, cost
- **Phase 2 — Review** (2026-12-26 → 2027-01-01, normal pace)
  - [ ] SageMaker and Bedrock FAQs; weak spots from the diagnosis
  - [ ] Tutorials Dojo practice exam 1 + review every mistake
- **Phase 3 — Practice exams** (2027-01-02 → 2027-01-07)
  - [ ] SB subscription for 1 month: official practice exam + labs
  - [ ] Tutorials Dojo practice exam 2; target > 80% before the exam
- **Exam:** [ ] 2027-01-08 (reschedule window up to 2027-01-13)
- **Post:** the certification + how the project will use each domain.

### M0 — Foundation · 2026-11-10 → 2027-01-24 (paused 2026-11-18 → 2027-01-10; local only)
- **Study**
  - [x] Book ch. 1–2 (overview, ML systems design)
  - [ ] PS: Introduction to PySpark, Big Data Fundamentals with PySpark
  - [ ] MLE: course 1 (name to confirm), Introduction to Shell, Introduction to Docker, Introduction to MLflow *(quick reviews)*
  - [ ] MLE: MLOps Concepts
- **Build**
  - [ ] Repo skeleton (uv, ruff, pytest, pre-commit), GitHub Actions running tests
  - [ ] Download Home Credit; EDA notebook documenting tables, keys, sizes, target imbalance
  - [ ] AWS account layout written down (implemented in M1)
- **Done when:** CI is green on an empty-but-tested package; EDA explains every table and join key.
- **Post:** why this project, and what I plan to learn.

### M1 — End to end *(first CV-ready version)* · 2027-01-25 → 2027-02-28 (5 weeks)
- **Setup:** [ ] AWS account (Paid plan) + Budgets + Cost Anomaly Detection + Terraform state bucket + GitHub OIDC role
- **Phase 1 — Data + PySpark**
  - Study: [ ] Book ch. 3 · [ ] MLE: ETL and ELT in Python · [ ] PS: Cleaning Data with PySpark, Feature Engineering with PySpark
  - Build: [ ] Spark feature jobs (local + EMR Serverless) · [ ] feature table in S3 + Glue Data Catalog, queryable in Athena
  - Done when: job runs on EMR Serverless from a single command; runtime and cost recorded.
- **Phase 2 — Data quality**
  - Study: [ ] Book ch. 4 · [ ] MLE: Introduction to Data Quality with Great Expectations
  - Build: [ ] expectation suite on raw and feature data · [ ] failing check blocks the pipeline
  - Done when: a deliberately corrupted file makes the pipeline fail with a readable report.
- **Phase 3 — Experimentation**
  - Study: [ ] Book ch. 5–6 · [ ] PS: Machine Learning with PySpark (compare Spark MLlib vs LightGBM)
  - Build: [ ] baseline + GBM · [ ] AUC/KS/calibration report · [ ] runs in SageMaker managed MLflow
  - Done when: model choice is justified in a guide page with numbers.
- **Phase 4 — Training pipeline**
  - Study: [ ] Book ch. 10 · [ ] MLE: Introduction to Data Versioning with DVC
  - Build: [ ] SageMaker Pipeline validate → features → train → evaluate · [ ] dataset/model lineage
  - Done when: one command (or CI trigger) reproduces a trained model from raw data.
- **Phase 5 — Registry + promotion**
  - Study: [ ] MLE: MLOps Deployment and Life Cycling
  - Build: [ ] SageMaker Model Registry · [ ] automatic promotion gates (metric + fairness thresholds)
  - Done when: a worse challenger is rejected automatically, a better one is promoted.
- **Phase 6 — Serving**
  - Study: [ ] Book ch. 7
  - Build: [ ] real-time endpoint · [ ] Batch Transform job · [ ] load test with p95 latency and $/1k predictions
  - Done when: README shows measured p95 and cost; endpoint teardown is one command.
- **Post (one per phase):** what I built + the book chapter behind it.

### M2 — Production · 2027-03-01 → 2027-03-21 (3 weeks)
- **Phase 7 — Monitoring**
  - Study: [ ] Book ch. 8 · [ ] MLE: Monitoring Machine Learning Concepts, Monitoring Machine Learning in Python
  - Build: [ ] simulated production traffic with injected drift and delayed labels · [ ] drift + performance monitors · [ ] CloudWatch alarms
  - Done when: injected drift fires an alarm within a defined window.
- **Phase 8 — Operations**
  - Study: [ ] Book ch. 9 · [ ] MLE: CI/CD for Machine Learning
  - Build: [ ] canary with traffic shifting + rollback · [ ] drift-triggered retraining · [ ] 2+ simulated incidents with runbook and post-mortem
  - Done when: each incident has a timeline, root cause, fix and prevention written up.

### M3 — Polish & responsible AI · 2027-03-22 → 2027-04-04 (2 weeks)
- **Phase 9 — Engineering**
  - Study: [ ] Book ch. 11 · [ ] SB: SageMaker Clarify / responsible AI content
  - Build: [ ] all infra in Terraform · [ ] SHAP reason codes in responses · [ ] fairness report · [ ] final README (architecture diagram, decisions, cost, latency)
- **Remaining track courses**
  - [ ] PS: Building Recommendation Engines with PySpark
  - [ ] MLE / PS: any course not yet ticked (bonus projects optional)
- **Done when:** a stranger can stand the whole system up from the README; `terraform destroy` leaves the bill at zero.

### M5 — Explanation agent *(optional extension)* · 2027-04-05 → 2027-05-02 (4 weeks)
An agent that answers "why was this application scored this way, and what would change it?" for
an analyst or applicant. It **explains, never decides**: the score and reason codes come from the
model (M3); the agent only reads them through tools.
- **Study:** [ ] Agents book · [ ] Book ch. 11 (responsible AI) again
- **Build**
  - [ ] Tools: `get_score(application_id)`, `get_reason_codes(application_id)` (SHAP top-k), `get_feature_context(feature)` (definition + population distribution), `what_if(application_id, changes)` (re-scores via the model)
  - [ ] Guardrails: never cites a protected attribute, never invents a reason not in the SHAP output, declines to give approval advice
  - [ ] Human-in-the-loop: borderline scores are routed to an analyst queue instead of auto-explained
  - [ ] Eval set: faithfulness of each explanation to the SHAP output (LLM-judge + rule checks)
- **Done when:** eval faithfulness ≥ the threshold set at the start of M5; a demo answers 3 real applications end to end.
- **Cost:** M5 runs locally against batch-scored results + stored SHAP values, using a pay-per-token LLM API (Amazon Bedrock). No always-on endpoint.
- **Post:** grounding an LLM on a credit model's explanations without letting it decide.

## 7. Progress

| Milestone | Target end | Status |
|---|---|---|
| MC AWS MLA-C02 | 2027-01-08 (exam) | ◐ in progress |
| M0 Foundation | 2027-01-24 | ◐ paused until 2027-01-11 (skeleton + CI done, PR open) |
| M1 End to end | 2027-02-28 | ☐ not started |
| M2 Production | 2027-03-21 | ☐ not started |
| M3 Polish | 2027-04-04 | ☐ not started |
| M5 Explanation agent *(optional)* | 2027-05-02 | ☐ not started |

Book: 2/11 chapters · MLE track: 0 courses · PySpark track: 0/6 courses · MLA-C02: not booked

## 8. Left to the builder (decided per phase plan)

- Exact feature set and Spark job layout; LightGBM vs XGBoost.
- Serving container: SageMaker prebuilt framework container vs custom FastAPI container.
- SageMaker Model Monitor vs Evidently (or both) for drift.
- How drift and label delay are simulated (Home Credit has no timestamps) — settled in the Phase 1 plan.
- Whether SageMaker Feature Store is used or S3 + Glue Catalog tables suffice.
- Which tests run against the AWS Emulator vs real AWS.
- Package layout, test strategy, guide page breakdown.
