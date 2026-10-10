from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

def create_figures(df: pd.DataFrame, output_dir: str | Path) -> list[str]:
    """Create charts with Matplotlib only for broad environment compatibility."""
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    created = []

    fig, ax = plt.subplots(figsize=(8, 5))
    ax.hist(df["unemployment_rate"].dropna(), bins=25, edgecolor="black", alpha=0.8)
    ax.set(title="Distribution of Estimated Unemployment Rate", xlabel="Unemployment rate (%)", ylabel="Count")
    fig.tight_layout()
    path = output_dir / "unemployment_distribution.png"
    fig.savefig(path, dpi=150); plt.close(fig); created.append(str(path))

    monthly = df.assign(month_start=df["date"].dt.to_period("M").dt.to_timestamp()).groupby(
        "month_start", as_index=False)["unemployment_rate"].mean()
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(monthly["month_start"], monthly["unemployment_rate"], marker="o")
    ax.set(title="Average Observed Unemployment Rate Over Time", xlabel="Month", ylabel="Mean unemployment rate (%)")
    fig.autofmt_xdate(); fig.tight_layout()
    path = output_dir / "unemployment_trend.png"
    fig.savefig(path, dpi=150); plt.close(fig); created.append(str(path))

    regional = df.groupby("region", as_index=False)["unemployment_rate"].mean().sort_values("unemployment_rate")
    fig, ax = plt.subplots(figsize=(10, max(6, len(regional) * 0.25)))
    ax.barh(regional["region"], regional["unemployment_rate"])
    ax.set(title="Mean Observed Unemployment Rate by Region", xlabel="Mean unemployment rate (%)", ylabel="Region")
    fig.tight_layout()
    path = output_dir / "regional_comparison.png"
    fig.savefig(path, dpi=150); plt.close(fig); created.append(str(path))

    areas = sorted(df["area"].dropna().unique())
    area_values = [df.loc[df["area"] == area, "unemployment_rate"].dropna().values for area in areas]
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.boxplot(area_values, labels=areas)
    ax.set(title="Unemployment Rate by Area", xlabel="Area", ylabel="Unemployment rate (%)")
    fig.tight_layout()
    path = output_dir / "area_comparison.png"
    fig.savefig(path, dpi=150); plt.close(fig); created.append(str(path))

    numeric = [c for c in ["unemployment_rate", "estimated_employed", "labour_participation_rate"] if c in df.columns]
    if len(numeric) >= 2:
        corr = df[numeric].corr(numeric_only=True)
        fig, ax = plt.subplots(figsize=(7, 5))
        image = ax.imshow(corr.values, vmin=-1, vmax=1, cmap="coolwarm", aspect="auto")
        ax.set_xticks(range(len(numeric)), labels=numeric, rotation=35, ha="right")
        ax.set_yticks(range(len(numeric)), labels=numeric)
        for i in range(len(numeric)):
            for j in range(len(numeric)):
                ax.text(j, i, f"{corr.iloc[i, j]:.2f}", ha="center", va="center")
        fig.colorbar(image, ax=ax, label="Correlation")
        ax.set_title("Correlation Between Numeric Indicators")
        fig.tight_layout()
        path = output_dir / "numeric_correlation_heatmap.png"
        fig.savefig(path, dpi=150); plt.close(fig); created.append(str(path))
    return created
