from unemployment_analysis.cleaning import clean_for_analysis

def test_adds_time_columns(sample_df):
    result = clean_for_analysis(sample_df)
    assert {"year", "month", "year_month"} <= set(result.columns)
    assert result["year"].tolist() == [2019, 2020, 2019, 2020]

def test_invalid_rates_removed(sample_df):
    df = sample_df.copy()
    df.loc[0, "unemployment_rate"] = 120
    result = clean_for_analysis(df)
    assert len(result) == 3
