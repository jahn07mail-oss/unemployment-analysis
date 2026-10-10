# Unemployment Analysis with Python

A reproducible exploratory data analysis project using the assignment dataset **Unemployment in India.csv**. It examines unemployment-rate distributions, monthly changes, regional differences, rural/urban comparisons, and a descriptive comparison around the start of the COVID-19 period.

## Features

- Data validation and cleaning with documented row counts
- Exploratory statistics and charts
- Monthly trend and regional/area summaries
- Descriptive pre-pandemic vs early-COVID comparison where supported
- Explicit caveats for seasonality and causal interpretation
- One-command execution and pytest tests

## Dataset

Place the file at `data/raw/Unemployment in India.csv`. The supplied copy is included in this project ZIP so the project can run immediately. The raw dataset is excluded from Git by default; check its license before publishing it.

Required columns: `Region`, `Date`, `Estimated Unemployment Rate (%)`, and `Area`. Additional columns such as `Estimated Employed` and `Estimated Labour Participation Rate (%)` are used when available.

## Windows / VS Code setup (Python 3.10)

```powershell
py -3.10 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.lock
python run_project.py
```

Run tests:

```powershell
python -m pytest -v
```

## Outputs

Generated files are saved locally under `reports/`:

- `analysis_report.md` — narrative summary and limitations
- `dataset_summary.json`, `cleaning_summary.json`, `analysis_summary.json`
- `monthly_unemployment.csv`, `regional_comparison.csv`, `area_comparison.csv`
- `covid_period_comparison.csv` when both comparison periods exist
- `monthly_pattern_summary.csv`
- `figures/` — distribution, trend, regional and area charts, and numeric correlation heatmap when available

The trained model is not part of this project; this is a descriptive data-analysis project rather than a prediction/classification task.

## Methodology and limitations

The early-COVID comparison uses observations before March 2020 and observations from March through June 2020. This is a descriptive comparison, not a causal estimate. The dataset ends in 2020, so it cannot support claims about later recovery. Its short time span also does not establish recurring annual seasonality. Regional and monthly means are unweighted averages of observed rows, not necessarily population-weighted national estimates.

## GitHub

The `.gitignore` excludes the raw dataset and generated reports by default. If you have confirmed redistribution rights and want to include the dataset or reports, review and adjust `.gitignore` intentionally. Never commit secrets or virtual environments.
