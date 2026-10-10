import sys
from pathlib import Path
import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

@pytest.fixture
def sample_df():
    return pd.DataFrame({
        "region": ["A", "A", "B", "B"],
        "date": pd.to_datetime(["2019-01-31", "2020-03-31", "2019-01-31", "2020-03-31"]),
        "unemployment_rate": [5.0, 10.0, 7.0, 12.0],
        "area": ["Rural", "Rural", "Urban", "Urban"],
        "estimated_employed": [100, 90, 80, 70],
        "labour_participation_rate": [50, 48, 45, 43],
    })
