from unemployment_analysis.visualization import create_figures

def test_figures_created(sample_df, tmp_path):
    paths = create_figures(sample_df, tmp_path)
    assert len(paths) >= 4
    assert all(__import__("pathlib").Path(p).exists() for p in paths)
