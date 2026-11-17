# M0 — Foundation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: use superpowers:executing-plans (inline) to implement
> this plan task by task. Steps use checkbox (`- [ ]`) syntax for tracking.
> Work in order; there are no per-task dates (see ROADMAP §3: dates are milestone targets only).

**Goal:** a tested, CI-checked Python package; an EDA that explains every Home Credit table and
join key; and a written GCP project layout that M1 implements with Terraform.

**Architecture:** `src/` layout package `credit_risk`, managed by uv. M0 code is small on purpose:
a table registry (names, grains, keys) plus key-integrity checks. M1's Spark jobs reuse both, and
the EDA notebook calls them. No cloud resources are created in M0.

**Tech stack:** Python 3.12, uv, ruff, mypy, pytest, pre-commit, nbstripout, GitHub Actions,
pandas + pyarrow (EDA), Kaggle CLI via `uvx kaggle`.

**Spec:** `docs/ROADMAP.md` (M0 section, §3 constraints, §4 decisions).

## How we work (learning project)

This is a learning project: speed matters less than Diego understanding every line.
- **Before each task:** Claude explains the concept and the choice in a few lines (what, why, the alternative).
- **During:** Claude writes all the code, in small steps. For the parts that matter (tests, `keys.py`,
  notebook analysis) Claude walks through the code: what each block does, why it is written that way,
  what would break otherwise. Boilerplate/config gets a one-line summary.
- **Before each commit:** Claude summarizes the diff; Diego asks until it is clear. Open questions become
  guide-page notes or exercises.
- Nothing is copied without understanding it (ROADMAP §2 anti-goal). Each "Learn" line says what the task must teach.

## Global constraints

- Code, docs, guide pages and notebooks in English. Commit messages in English, conventional commits without scope (`feat: ...`), no co-author lines.
- Public repo: no data, no secrets, no `kaggle.json` in git; `data/` is gitignored.
- Notebooks are committed **without outputs** (nbstripout); findings go into the guide page.
- Python pinned to 3.12 (`.python-version`); re-check against the Dataproc Serverless runtime in M1.
- One PR per block below (A, B, C). "Done" = pre-commit + CI green.

## Review focus

1. Running the download twice must not re-download or corrupt files (`verify_download` is idempotent).
2. Key checks on an **empty** table: a PK check passes and an FK orphan rate is `0.0`, not a `ZeroDivisionError`.
3. Null keys: a null PK value counts as a violation; a null FK value is reported separately, not as an orphan.
4. Composite grains (`bureau_balance`: `SK_ID_BUREAU` + `MONTHS_BALANCE`) are checked as tuples.
5. A large CSV accidentally staged must be blocked by pre-commit (`check-added-large-files`, 1 MB).

---

## Block A — Repo skeleton + CI (PR 1)

### Task 1: package skeleton with uv

**Learn:** what `pyproject.toml`, `uv.lock` and the `src/` layout each solve; dependency groups.

**Files:** create `pyproject.toml`, `.python-version`, `.gitignore`, `LICENSE` (MIT), `README.md` (stub
that links the ROADMAP), `src/credit_risk/__init__.py`, `tests/test_package.py`.

- [ ] `uv init --package --name credit-risk --python 3.12`, then move the code under `src/credit_risk/`.
- [ ] Dev group: `uv add --dev pytest pytest-cov ruff mypy pre-commit nbstripout pandas-stubs`;
      runtime: `uv add pandas pyarrow`; EDA group: `uv add --group eda jupyterlab matplotlib`.
- [ ] `.gitignore`: `data/`, `.venv/`, `.ipynb_checkpoints/`, `*.parquet`, `*.csv`, `kaggle.json`, `.omc/`.
- [ ] Test `test_version_is_exposed`: `credit_risk.__version__` is a non-empty `str`. Run `uv run pytest` → FAIL, add `__version__ = "0.1.0"` → PASS.
- [ ] Commit: `chore: create package skeleton with uv`.

### Task 2: quality tooling (ruff, mypy, pre-commit)

**Learn:** lint vs format vs type check; how a pre-commit hook works and why it runs locally *and* in CI.

**Files:** modify `pyproject.toml`; create `.pre-commit-config.yaml`.

- [ ] ruff: `line-length = 100`, `target-version = "py312"`, rules `E,F,I,B,UP,SIM,PD,N`; `ruff format`.
- [ ] mypy: `strict = true` on `src/`; tests not type-checked.
- [ ] pytest: `testpaths = ["tests"]`, `addopts = "--cov=credit_risk --cov-report=term-missing"`.
- [ ] pre-commit hooks: `ruff` + `ruff-format`, `mypy` (local hook via `uv run`), `nbstripout`,
      `check-added-large-files --maxkb=1024`, `detect-private-key`, `end-of-file-fixer`, `trailing-whitespace`.
- [ ] Verify: `uv run pre-commit install && uv run pre-commit run --all-files` → all Passed.
      Then stage a fake 2 MB file and check that the commit is blocked (Review focus 5), and delete it.
- [ ] Commit: `chore: configure ruff, mypy and pre-commit`.

### Task 3: GitHub Actions CI

**Learn:** workflow → job → step; why `--locked`; reading a failing run's logs.

**Files:** create `.github/workflows/ci.yml`.

- [ ] Triggers: `push` to `main`, `pull_request`. Single job on `ubuntu-latest`:
      `astral-sh/setup-uv` (cache on) → `uv sync --locked --all-groups` → `uv run ruff check` →
      `uv run ruff format --check` → `uv run mypy src` → `uv run pytest`.
- [ ] Diego creates the public repo `dpontejs/credit-risk-mlops` (`gh repo create ... --public --source . --push`): it is outward-facing, so he runs it himself.
- [ ] Open PR 1 from `m0/skeleton`; CI green. Enable branch protection on `main` (CI required).
- [ ] Commit: `ci: run lint, type checks and tests on GitHub Actions`.

## Block B — Home Credit data + EDA (PR 2)

### Task 4: table registry and key checks (TDD)

**Learn:** red → green → refactor; grain, primary key and foreign key in a relational dataset. Claude walks through each test and what it protects.

**Files:** create `src/credit_risk/data/__init__.py`, `src/credit_risk/data/tables.py`,
`src/credit_risk/data/keys.py`, `tests/data/test_tables.py`, `tests/data/test_keys.py`.

**Interfaces (produces):**
- `Table` (frozen dataclass): `name: str`, `file: str`, `grain: tuple[str, ...]`, `foreign_keys: dict[str, str]` (column → parent table name), `grain_is_unique: bool`.
- `TABLES: dict[str, Table]`: one entry per Kaggle CSV (8 tables; `HomeCredit_columns_description.csv` is docs, not a table).
- `check_primary_key(df: pd.DataFrame, columns: Sequence[str]) -> KeyReport`
- `check_foreign_key(child: pd.DataFrame, parent: pd.DataFrame, column: str, parent_column: str) -> FkReport`
- `KeyReport(rows: int, duplicates: int, nulls: int)` with `.ok`; `FkReport(rows: int, nulls: int, orphans: int)` with `.orphan_rate: float`.

- [ ] Tests for the registry: `test_registry_has_all_kaggle_tables` (set of names == the 8 tables:
      `application_train`, `application_test`, `bureau`, `bureau_balance`, `previous_application`,
      `POS_CASH_balance`, `credit_card_balance`, `installments_payments`);
      `test_every_foreign_key_points_to_a_registered_table`;
      `test_bureau_balance_grain_is_composite` (`grain == ("SK_ID_BUREAU", "MONTHS_BALANCE")`).
- [ ] Tests for keys, with small in-memory frames: `test_pk_detects_duplicates`, `test_pk_composite_grain`,
      `test_pk_null_counts_as_violation`, `test_fk_orphan_rate`, `test_fk_null_is_not_orphan`,
      `test_checks_on_empty_frames` (Review focus 2–4).
- [ ] Run → FAIL; implement; run → PASS. Start the registry with *expected* grains; the EDA (Task 6)
      confirms or corrects `grain_is_unique` (e.g. `installments_payments` may not have a unique grain).
- [ ] Commit: `feat: add table registry and key checks`.

### Task 5: data download

**Learn:** config through environment variables; idempotent scripts; keeping credentials out of a public repo.

**Files:** create `src/credit_risk/data/paths.py`, `scripts/download_home_credit.sh`, `tests/data/test_paths.py`.

**Interfaces:** `data_dir() -> Path` (env `CREDIT_RISK_DATA_DIR`, default `<repo>/data/raw`);
`missing_files(directory: Path) -> list[str]` (expected files from `TABLES`, missing ones sorted).

- [ ] Tests: `test_data_dir_respects_env` (monkeypatch), `test_missing_files_lists_absent_tables` (tmp_path with 2 empty CSVs).
- [ ] Script: exits early if `missing_files` is empty; otherwise `uvx kaggle competitions download -c home-credit-default-risk -p "$DIR"` and unzip.
      Requires accepting the competition rules on Kaggle and `~/.kaggle/kaggle.json` (chmod 600, never in the repo).
- [ ] Run it twice: the second run downloads nothing (Review focus 1). Record the size on disk in the guide.
- [ ] Commit: `feat: add Home Credit download script`.

### Task 6: EDA notebook

**Learn:** reading a relational dataset before modelling it; class imbalance; what EDA must hand to feature engineering. Claude explains each finding and the M1 decision it leads to.

**Files:** create `notebooks/01-home-credit-eda.ipynb`.

Sections (each ends with a 1–3 line markdown conclusion):
- [ ] Inventory: rows, columns, size on disk and in memory per table.
- [ ] Join map: for each table, its grain and how it reaches `SK_ID_CURR` (via `SK_ID_BUREAU` / `SK_ID_PREV`),
      using `check_primary_key` / `check_foreign_key`; report orphan rates and rows per parent (min/median/p99/max).
- [ ] Target: `TARGET` rate in `application_train` (expect ~8% positive); why accuracy is useless here, and AUC/KS later.
- [ ] Data issues worth a feature-engineering decision in M1: null rates, sentinels (`DAYS_EMPLOYED == 365243`), train vs test drift on a few columns.
- [ ] Protected attributes: `CODE_GENDER`, `DAYS_BIRTH`: distribution and default rate per group (baseline numbers for the fairness gate, ROADMAP §4).
- [ ] Update `TABLES[...].grain_is_unique` to what the data shows; tests still green.
- [ ] Commit: `docs: add Home Credit EDA notebook`.

### Task 7: guide pages for block B

**Files:** create `docs/guide/00-dev-setup.md`, `docs/guide/01-home-credit-data.md`.

- [ ] `00`: why uv/ruff/mypy/pre-commit, daily commands, pitfalls (lockfile, notebook outputs, large files).
- [ ] `01`: one section per table (what it is, grain, keys, size), a join diagram (Mermaid), the EDA findings,
      plus exercises. Bonus exercise once PySpark course 1 is done: redo the key checks in PySpark local and compare runtime.
- [ ] PR 2 merged with CI green.

## Block C — GCP project layout (PR 3, document only)

### Task 8: write the layout that M1 will implement

**Learn:** GCP resource hierarchy, IAM with service accounts, WIF, and why Terraform state lives in its own bucket.

**Files:** create `docs/guide/02-gcp-layout.md`. No cloud resources: the trial is activated in M1.

Decisions (write them down with the reason for each and the alternative that was rejected):
- [ ] **One project** `credit-risk-mlops-<suffix>`, region `us-central1`. Rejected: dev/prod projects (the trial has a single billing account and a 90-day clock; environments are separated by name prefix + labels).
- [ ] **Buckets:** `<project>-tfstate` (versioned, created by `infra/bootstrap` with local state), `<project>-data` (`raw/`, `features/`), `<project>-artifacts` (pipeline root, models).
- [ ] **BigQuery datasets:** `credit_raw`, `credit_features`, `credit_monitoring`.
- [ ] **Service accounts:** `sa-pipelines` (Vertex + Dataproc), `sa-serving` (endpoint), `sa-ci` (GitHub via Workload Identity Federation, no keys).
- [ ] **Labels** on every resource: `app=credit-risk-mlops`, `phase=<n>`, `ephemeral=true|false` (teardown finds what to delete).
- [ ] **Budget:** US$300 budget with alerts at 25/50/75/90% + email; teardown checklist after every demo.
- [ ] **Terraform layout:** `infra/bootstrap/` (state bucket, APIs) → `infra/main/` (GCS backend, everything else).
- [ ] PR 3 merged.

### Task 9: close M0

- [ ] Tick M0 boxes in `docs/ROADMAP.md`, update §7 progress and counters; mark items done in the `today` MCP.
- [ ] Draft the LinkedIn post (why this project, what I plan to learn), then write the M1 / Phase 1 plan.
- [ ] Commit: `docs: close M0 in the roadmap`.
