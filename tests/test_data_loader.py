import pandas as pd
import pytest
from unemployment_analysis.data_loader import load_dataset, normalize_column_name

def test_normalize_column_name():
    assert normalize_column_name(" Estimated Unemployment Rate (%) ") == "estimated unemployment rate (%)"

def test_loads_assignment_csv(tmp_path):
    p = tmp_path / "data.csv"
    pd.DataFrame({
        "Region": [" A ", "B"], " Date": ["31-05-2019", "30-06-2019"],
        " Estimated Unemployment Rate (%)": [3.5, 4.2], "Area": ["Rural", "Urban"]
    }).to_csv(p, index=False)
    df, info = load_dataset(p)
    assert len(df) == 2
    assert df["region"].tolist() == ["A", "B"]
    assert info["rows_after_cleaning"] == 2

def test_empty_rows_and_duplicates_removed(tmp_path):
    p = tmp_path / "data.csv"
    pd.DataFrame([
        {"Region": "A", " Date": "31-05-2019", " Estimated Unemployment Rate (%)": 3.5, "Area": "Rural"},
        {"Region": "A", " Date": "31-05-2019", " Estimated Unemployment Rate (%)": 3.5, "Area": "Rural"},
        {"Region": None, " Date": None, " Estimated Unemployment Rate (%)": None, "Area": None},
    ]).to_csv(p, index=False)
    df, info = load_dataset(p)
    assert len(df) == 1
    assert info["rows_fully_empty_removed"] == 1
    assert info["exact_duplicate_rows_removed"] == 1

def test_missing_file_raises(tmp_path):
    with pytest.raises(FileNotFoundError):
        load_dataset(tmp_path / "missing.csv")

def test_missing_required_column_raises(tmp_path):
    p = tmp_path / "bad.csv"
    pd.DataFrame({"Region": ["A"], "Date": ["31-05-2019"], "Area": ["Rural"]}).to_csv(p, index=False)
    with pytest.raises(ValueError, match="Missing required columns"):
        load_dataset(p)
