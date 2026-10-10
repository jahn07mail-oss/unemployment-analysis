from pathlib import Path
import json
import sys

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "src"))

from unemployment_analysis.data_loader import load_dataset
from unemployment_analysis.cleaning import clean_for_analysis
from unemployment_analysis.analysis import (
    dataset_summary, monthly_summary, regional_summary, area_summary,
    covid_period_summary, seasonal_summary
)
from unemployment_analysis.visualization import create_figures

def main() -> int:
    data_path = ROOT / "data" / "raw" / "Unemployment in India.csv"
    reports = ROOT / "reports"
    figures = reports / "figures"
    reports.mkdir(exist_ok=True)
    try:
        print("=== Unemployment Analysis with Python ===")
        df, cleaning = load_dataset(data_path)
        df = clean_for_analysis(df)
        print(f"Dataset: {data_path.relative_to(ROOT)}")
        print(f"Raw shape: {cleaning['raw_shape'][0]} rows x {cleaning['raw_shape'][1]} columns")
        print(f"Fully empty rows removed: {cleaning['rows_fully_empty_removed']}")
        print(f"Exact duplicate rows removed: {cleaning['exact_duplicate_rows_removed']}")
        print(f"Rows after cleaning: {len(df)}")
        print(f"Date range: {df['date'].min().date()} to {df['date'].max().date()}")
        print(f"Regions: {df['region'].nunique()} | Areas: {', '.join(sorted(df['area'].unique()))}")
        print(f"Mean unemployment rate: {df['unemployment_rate'].mean():.2f}%")

        summary = dataset_summary(df)
        monthly = monthly_summary(df)
        regional = regional_summary(df)
        area = area_summary(df)
        covid, covid_note = covid_period_summary(df)
        seasonal, seasonal_note = seasonal_summary(df)

        monthly.assign(month_start=monthly["month_start"].dt.strftime("%Y-%m-%d")).to_csv(
            reports / "monthly_unemployment.csv", index=False)
        regional.to_csv(reports / "regional_comparison.csv", index=False)
        area.to_csv(reports / "area_comparison.csv", index=False)
        if not covid.empty:
            covid.to_csv(reports / "covid_period_comparison.csv", index=False)
        seasonal.to_csv(reports / "monthly_pattern_summary.csv", index=False)
        (reports / "dataset_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
        (reports / "cleaning_summary.json").write_text(json.dumps(cleaning, indent=2), encoding="utf-8")

        figures_created = create_figures(df, figures)
        high = regional.iloc[0]
        low = regional.iloc[-1]
        monthly_sorted = monthly.sort_values("mean_unemployment_rate")
        peak = monthly_sorted.iloc[-1]
        trough = monthly_sorted.iloc[0]
        covid_text = covid_note
        covid_table = covid.to_markdown(index=False) if not covid.empty else "Not available for this dataset."
        report = f"""# Unemployment Analysis with Python

## Executive summary

This analysis uses the supplied **Unemployment in India.csv** dataset. It describes the observations available in the file; it does not establish causal effects.

- **Clean observations:** {len(df)}
- **Date coverage:** {df['date'].min().strftime('%B %Y')} to {df['date'].max().strftime('%B %Y')}
- **Regions represented:** {df['region'].nunique()}
- **Overall mean observed unemployment rate:** {df['unemployment_rate'].mean():.2f}%
- **Highest regional mean in this dataset:** {high['region']} ({high['mean_unemployment_rate']:.2f}%)
- **Lowest regional mean in this dataset:** {low['region']} ({low['mean_unemployment_rate']:.2f}%)
- **Highest monthly mean:** {peak['month_start'].strftime('%B %Y')} ({peak['mean_unemployment_rate']:.2f}%)
- **Lowest monthly mean:** {trough['month_start'].strftime('%B %Y')} ({trough['mean_unemployment_rate']:.2f}%)

## Dataset and cleaning

The CSV initially contained {cleaning['raw_shape'][0]} rows and {cleaning['raw_shape'][1]} columns. The pipeline removed {cleaning['rows_fully_empty_removed']} fully empty rows and {cleaning['exact_duplicate_rows_removed']} exact duplicate rows. After date/rate validation, {len(df)} observations remain. The source file was not modified.

Date coverage is limited to {df['date'].min().strftime('%B %Y')} through {df['date'].max().strftime('%B %Y')}. The dataset includes regions and rural/urban area categories.

## Trends over time

Monthly mean values are available in `monthly_unemployment.csv`. In this dataset, the lowest monthly mean was in {trough['month_start'].strftime('%B %Y')} and the highest was in {peak['month_start'].strftime('%B %Y')}. These are unweighted averages of the available rows; they should not be interpreted as population-weighted national estimates.

![Unemployment trend](figures/unemployment_trend.png)

## Regional and area comparisons

Regional averages are provided in `regional_comparison.csv`; area averages are in `area_comparison.csv`. Differences may reflect the observations represented in the file and do not by themselves explain why unemployment differs.

![Regional comparison](figures/regional_comparison.png)

![Area comparison](figures/area_comparison.png)

## COVID-19 period comparison

Comparison periods are defined as:
- Pre-pandemic: observations before 1 March 2020.
- Early COVID period: observations from 1 March through 30 June 2020.

{covid_text}

{covid_table}

This comparison is descriptive. It does not prove that COVID-19 alone caused the observed changes.

## Seasonality

{seasonal_note}

The available period is too short to reliably establish recurring annual seasonality. Monthly variation is reported as descriptive only.

## Policy-relevant considerations

The regional and area summaries can help identify where further investigation may be useful. Before making policy decisions, combine these descriptive findings with longer time series, labour-force denominators, population weights, demographic context, and independent evidence about policy effectiveness. This dataset alone cannot demonstrate that a particular policy will reduce unemployment.

## Limitations

- The file covers only a limited period ending in 2020.
- The analysis uses simple unweighted means of rows unless otherwise stated.
- Duplicate rows were removed only when every field matched exactly.
- Temporal association does not establish causation.
- Seasonal patterns and long-term recovery cannot be reliably inferred from this short window.

## Generated artifacts

{chr(10).join('- `' + str(Path(p).relative_to(ROOT)).replace(chr(92), '/') + '`' for p in figures_created)}
- `reports/dataset_summary.json`
- `reports/cleaning_summary.json`
- `reports/monthly_unemployment.csv`
- `reports/regional_comparison.csv`
- `reports/area_comparison.csv`
- `reports/monthly_pattern_summary.csv`
"""
        (reports / "analysis_report.md").write_text(report, encoding="utf-8")
        analysis_summary = {
            **summary,
            "covid_comparison_note": covid_note,
            "seasonality_note": seasonal_note,
            "top_mean_region": {"region": str(high["region"]), "mean_rate": float(high["mean_unemployment_rate"])},
            "lowest_mean_region": {"region": str(low["region"]), "mean_rate": float(low["mean_unemployment_rate"])},
            "figures_created": [str(Path(p).relative_to(ROOT)).replace("\\", "/") for p in figures_created],
        }
        (reports / "analysis_summary.json").write_text(json.dumps(analysis_summary, indent=2), encoding="utf-8")
        print("\n=== Main findings ===")
        print(f"Mean unemployment rate: {df['unemployment_rate'].mean():.2f}%")
        print(f"Highest regional mean: {high['region']} ({high['mean_unemployment_rate']:.2f}%)")
        print(f"Lowest regional mean: {low['region']} ({low['mean_unemployment_rate']:.2f}%)")
        print(f"COVID comparison: {covid_note}")
        print(f"Seasonality: {seasonal_note}")
        print("\n=== Generated outputs ===")
        print("reports/analysis_report.md")
        print("reports/dataset_summary.json")
        print("reports/cleaning_summary.json")
        print("reports/analysis_summary.json")
        print("reports/monthly_unemployment.csv")
        print("reports/regional_comparison.csv")
        print("reports/area_comparison.csv")
        print("reports/monthly_pattern_summary.csv")
        for item in figures_created:
            print(Path(item).relative_to(ROOT))
        print("\nPipeline completed successfully.")
        return 0
    except (FileNotFoundError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

if __name__ == "__main__":
    raise SystemExit(main())
