from unemployment_analysis.analysis import (
    dataset_summary, monthly_summary, regional_summary, area_summary,
    covid_period_summary, seasonal_summary
)

def test_dataset_summary(sample_df):
    result = dataset_summary(sample_df)
    assert result["observations"] == 4
    assert result["regions_count"] == 2
    assert result["unemployment_rate_mean"] == 8.5

def test_monthly_summary(sample_df):
    result = monthly_summary(sample_df)
    assert len(result) == 2
    assert "mean_unemployment_rate" in result.columns

def test_regional_and_area_summaries(sample_df):
    assert len(regional_summary(sample_df)) == 2
    assert len(area_summary(sample_df)) == 2

def test_covid_comparison(sample_df):
    result, note = covid_period_summary(sample_df)
    assert len(result) == 2
    assert "not proof" in note

def test_seasonality_caveat(sample_df):
    result, note = seasonal_summary(sample_df)
    assert len(result) > 0
    assert "not established" in note
