import pandas as pd

def clean_for_analysis(df: pd.DataFrame) -> pd.DataFrame:
    """Return a defensive copy with normalized region/area labels."""
    out = df.copy()
    out["region"] = out["region"].astype(str).str.strip()
    out["area"] = out["area"].astype(str).str.strip()
    out["date"] = pd.to_datetime(out["date"], errors="coerce")
    out["unemployment_rate"] = pd.to_numeric(out["unemployment_rate"], errors="coerce")
    out = out.dropna(subset=["region", "area", "date", "unemployment_rate"])
    out = out[out["unemployment_rate"].between(0, 100)]
    out["year"] = out["date"].dt.year
    out["month"] = out["date"].dt.month
    out["year_month"] = out["date"].dt.to_period("M").astype(str)
    return out.reset_index(drop=True)
