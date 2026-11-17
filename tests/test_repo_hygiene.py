"""Guards for a public repo: data and secrets stay out of git, source code stays in."""

import subprocess
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]


def is_ignored(path: str) -> bool:
    # `git check-ignore -q` exits 0 when the path is ignored, 1 when it is not.
    result = subprocess.run(["git", "check-ignore", "-q", path], cwd=REPO_ROOT, check=False)
    return result.returncode == 0


@pytest.mark.parametrize(
    "path",
    [
        "src/credit_risk/data/tables.py",
        "tests/data/test_keys.py",
        "docs/guide/01-home-credit-data.md",
    ],
)
def test_source_paths_are_tracked(path: str) -> None:
    assert not is_ignored(path)


@pytest.mark.parametrize(
    "path",
    [
        "data/raw/application_train.csv",
        "notebooks/sample.parquet",
        "models/model.pkl",
        "models/model.joblib",
        "extract.csv.gz",
        "features.feather",
        ".env",
        "kaggle.json",
        "sa-key.json",
    ],
)
def test_data_and_secrets_are_ignored(path: str) -> None:
    assert is_ignored(path)
