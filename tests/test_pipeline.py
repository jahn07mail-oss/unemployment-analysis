import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def test_pipeline_creates_reports():
    env = os.environ.copy()
    result = subprocess.run([sys.executable, str(ROOT / "run_project.py")],
                            cwd=ROOT, capture_output=True, text=True, env=env, timeout=120)
    assert result.returncode == 0, result.stdout + "\n" + result.stderr
    assert (ROOT / "reports" / "analysis_report.md").exists()
    assert (ROOT / "reports" / "analysis_summary.json").exists()
    assert (ROOT / "reports" / "figures" / "unemployment_trend.png").exists()
