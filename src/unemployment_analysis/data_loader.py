from pathlib import Path
import pandas as pd

COLUMN_ALIASES = {
    "region": "region",
    "date": "date",
    "frequency": "frequency",
    "estimated unemployment rate (%)": "unemployment_rate",
    "unemployment rate (%)": "unemployment_rate",
    "unemployment_rate": "unemployment_rate",
    "estimated employed": "estimated_employed",
    "estimated labour participation rate (%)": "labour_participation_rate",
    "estimated labor participation rate (%)": "labour_participation_rate",
    "area": "area",
}

REQUIRED = {"region", "date", "unemployment_rate", "area"}

def normalize_column_name(name: str) -> str:
    return " ".join(str(name).strip().lower().split())

def load_dataset(path: str | Path) -> tuple[pd.DataFrame, dict]:
    """Load, normalize, and validate the supplied CSV without modifying it."""
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(
            f"Dataset not found: {path}. Place 'Unemployment in India.csv' in data/raw/."
        )
    try:
        raw = pd.read_csv(path)
    except Exception as exc:
        raise ValueError(f"Could not read CSV file {path}: {exc}") from exc
    raw_shape = list(raw.shape)
    original_columns = [str(c) for c in raw.columns]
    rename = {}
    for col in raw.columns:
        normalized = normalize_column_name(col)
        if normalized in COLUMN_ALIASES:
            rename[col] = COLUMN_ALIASES[normalized]
    df = raw.rename(columns=rename).copy()
    # Strip surrounding whitespace from string fields, including date values.
    for col in df.select_dtypes(include=["object"]).columns:
        df[col] = df[col].map(lambda x: x.strip() if isinstance(x, str) else x)
    missing_required = sorted(REQUIRED - set(df.columns))
    if missing_required:
        raise ValueError(
            f"Missing required columns: {missing_required}. Found columns: {list(df.columns)}"
        )

    blank_rows = int(df.isna().all(axis=1).sum())
    df = df.dropna(how="all").copy()
    duplicates = int(df.duplicated().sum())
    df = df.drop_duplicates().copy()

    df["date"] = pd.to_datetime(df["date"], dayfirst=True, errors="coerce")
    df["unemployment_rate"] = pd.to_numeric(df["unemployment_rate"], errors="coerce")
    if "estimated_employed" in df.columns:
        df["estimated_employed"] = pd.to_numeric(df["estimated_employed"], errors="coerce")
    if "labour_participation_rate" in df.columns:
        df["labour_participation_rate"] = pd.to_numeric(
            df["labour_participation_rate"], errors="coerce"
        )

    before_valid = len(df)
    invalid_date = int(df["date"].isna().sum())
    invalid_rate = int(df["unemployment_rate"].isna().sum())
    # Keep valid observations only; rates outside 0–100 are invalid percentages.
    invalid_range = int(
        ((df["unemployment_rate"] < 0) | (df["unemployment_rate"] > 100)).fillna(False).sum()
    )
    df = df.dropna(subset=["region", "date", "unemployment_rate", "area"]).copy()
    df = df[df["unemployment_rate"].between(0, 100)].copy()
    df["region"] = df["region"].astype(str).str.strip()
    df["area"] = df["area"].astype(str).str.strip()
    df["frequency"] = df["frequency"].astype(str).str.strip() if "frequency" in df.columns else "Unknown"
    if df.empty:
        raise ValueError("No valid observations remain after cleaning.")
    summary = {
        "source_file": path.name,
        "raw_shape": raw_shape,
        "raw_columns": original_columns,
        "rows_fully_empty_removed": blank_rows,
        "exact_duplicate_rows_removed": duplicates,
        "invalid_dates_before_drop": invalid_date,
        "missing_or_non_numeric_unemployment_rates_before_drop": invalid_rate,
        "rates_outside_0_100_removed": invalid_range,
        "rows_before_validity_filter": int(before_valid),
        "rows_after_cleaning": int(len(df)),
        "date_min": df["date"].min().strftime("%Y-%m-%d"),
        "date_max": df["date"].max().strftime("%Y-%m-%d"),
        "regions": sorted(df["region"].dropna().unique().tolist()),
        "areas": sorted(df["area"].dropna().unique().tolist()),
        "unemployment_rate_min": float(df["unemployment_rate"].min()),
        "unemployment_rate_max": float(df["unemployment_rate"].max()),
    }
    return df.sort_values("date").reset_index(drop=True), summary
