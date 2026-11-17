# credit-risk-mlops

Credit default risk system on Google Cloud covering the full lifecycle of a classical ML project:
PySpark feature engineering, data quality, training pipelines, registry, serving, monitoring and
operations. Data: [Home Credit Default Risk](https://www.kaggle.com/competitions/home-credit-default-risk).

> Work in progress. Design and progress tracker: [docs/ROADMAP.md](docs/ROADMAP.md).

## Development

```bash
uv sync --all-groups   # create .venv with runtime, dev and EDA dependencies
uv run pytest          # run the tests
```
