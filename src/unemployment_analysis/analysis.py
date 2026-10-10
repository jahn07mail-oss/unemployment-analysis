import pandas as pd

def dataset_summary(df: pd.DataFrame) -> dict:
    rate = df["unemployment_rate"]
    return {
        "observations": int(len(df)),
        "regions_count": int(df["region"].nunique()),
        "areas": sorted(df["area"].dropna().unique().tolist()),
        "date_min": df["date"].min().strftime("%Y-%m-%d"),
        "date_max": df["date"].max().strftime("%Y-%m-%d"),
        "unemployment_rate_mean": round(float(rate.mean()), 4),
        "unemployment_rate_median": round(float(rate.median()), 4),
        "unemployment_rate_std": round(float(rate.std()), 4),
        "unemployment_rate_min": round(float(rate.min()), 4),
        "unemployment_rate_max": round(float(rate.max()), 4),
    }

def monthly_summary(df: pd.DataFrame) -> pd.DataFrame:
    return (df.assign(month_start=df["date"].dt.to_period("M").dt.to_timestamp())
            .groupby("month_start", as_index=False)
            .agg(mean_unemployment_rate=("unemployment_rate", "mean"),
                 median_unemployment_rate=("unemployment_rate", "median"),
                 observations=("unemployment_rate", "size"))
            .sort_values("month_start"))

def regional_summary(df: pd.DataFrame) -> pd.DataFrame:
    return (df.groupby("region", as_index=False)
            .agg(mean_unemployment_rate=("unemployment_rate", "mean"),
                 median_unemployment_rate=("unemployment_rate", "median"),
                 observations=("unemployment_rate", "size"))
            .sort_values("mean_unemployment_rate", ascending=False))

def area_summary(df: pd.DataFrame) -> pd.DataFrame:
    return (df.groupby("area", as_index=False)
            .agg(mean_unemployment_rate=("unemployment_rate", "mean"),
                 median_unemployment_rate=("unemployment_rate", "median"),
                 observations=("unemployment_rate", "size"))
            .sort_values("mean_unemployment_rate", ascending=False))

def covid_period_summary(df: pd.DataFrame) -> tuple[pd.DataFrame, str]:
    """Compare available pre-pandemic (before 2020-03) and early-pandemic observations."""
    d = df.copy()
    d["period"] = pd.NA
    d.loc[d["date"] < pd.Timestamp("2020-03-01"), "period"] = "Pre-pandemic (before Mar 2020)"
    d.loc[(d["date"] >= pd.Timestamp("2020-03-01")) &
          (d["date"] <= pd.Timestamp("2020-06-30")), "period"] = "Early COVID period (Mar-Jun 2020)"
    selected = d.dropna(subset=["period"])
    if selected.empty or selected["period"].nunique() < 2:
        return pd.DataFrame(columns=["period", "mean_unemployment_rate", "observations"]), (
            "COVID comparison unavailable: the dataset does not contain observations in both periods."
        )
    summary = (selected.groupby("period", as_index=False)
               .agg(mean_unemployment_rate=("unemployment_rate", "mean"),
                    observations=("unemployment_rate", "size")))
    pre = summary.loc[summary["period"].str.startswith("Pre-pandemic"), "mean_unemployment_rate"]
    covid = summary.loc[summary["period"].str.startswith("Early COVID"), "mean_unemployment_rate"]
    if len(pre) and len(covid):
        pp = float(covid.iloc[0] - pre.iloc[0])
        message = (f"The unweighted mean observed unemployment rate changed by {pp:.2f} percentage "
                   f"points between the pre-pandemic and early-COVID observations. This is descriptive "
                   f"association, not proof that COVID-19 alone caused the change.")
    else:
        message = "COVID comparison is incomplete because one comparison period is missing."
    return summary, message

def seasonal_summary(df: pd.DataFrame) -> tuple[pd.DataFrame, str]:
    monthly = df.groupby(df["date"].dt.month)["unemployment_rate"].agg(["mean", "count"]).reset_index()
    monthly = monthly.rename(columns={"date": "month", "mean": "mean_unemployment_rate",
                                      "count": "observations"})
    if df["date"].max() - df["date"].min() < pd.Timedelta(days=730):
        note = ("Seasonality is not established: this dataset spans less than two years, so monthly "
                "differences may reflect one-off events rather than a recurring seasonal pattern.")
    else:
        note = ("Monthly averages are descriptive. Confirm recurring seasonality with adequate repeated "
                "cycles and appropriate time-series methods before drawing conclusions.")
    return monthly, note
