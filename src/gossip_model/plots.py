"""Plotting utilities for gossip simulation outputs."""

from __future__ import annotations

from pathlib import Path
from typing import Optional

import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

# Larger font defaults for report/presentation figures.
plt.rcParams.update({
    "font.size": 16,
    "axes.titlesize": 18,
    "axes.labelsize": 16,
    "xtick.labelsize": 14,
    "ytick.labelsize": 14,
    "legend.fontsize": 14,
    "figure.titlesize": 20,
})

def ensure_dir(path: str | Path) -> Path:
    path = Path(path)
    path.mkdir(parents=True, exist_ok=True)
    return path


def plot_spread_factor(
    summary: pd.DataFrame,
    output_path: str | Path,
    *,
    title: str = "Spread factor vs victim degree",
    log_x: bool = True,
) -> None:
    """Save a plot of average spread factor f against victim degree k."""
    output_path = Path(output_path)
    ensure_dir(output_path.parent)

    plt.figure(figsize=(8, 5))
    plt.plot(
        summary["degree"],
        summary["mean_spread_factor"],
        marker="o",
        linewidth=1,
    )
    plt.xlabel("victim degree k")
    plt.ylabel("mean spread factor f")
    plt.title(title)

    if log_x:
        plt.xscale("log")

    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(output_path, dpi=200)
    plt.close()


def plot_spreading_time(
    summary: pd.DataFrame,
    output_path: str | Path,
    *,
    title: str = "Spreading time vs victim degree",
    log_x: bool = True,
) -> None:
    """Save a plot of average spreading time tau against victim degree k."""
    output_path = Path(output_path)
    ensure_dir(output_path.parent)

    plt.figure(figsize=(8, 5))
    plt.plot(
        summary["degree"],
        summary["mean_tau"],
        marker="o",
        linewidth=1,
    )
    plt.xlabel("victim degree k")
    plt.ylabel("mean spreading time tau")
    plt.title(title)

    if log_x:
        plt.xscale("log")

    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(output_path, dpi=200)
    plt.close()


def plot_multi_series(
    all_summary: pd.DataFrame,
    output_path: str | Path,
    *,
    x: str = "degree",
    y: str = "mean_spread_factor",
    series_col: str = "series",
    title: Optional[str] = None,
    y_label: Optional[str] = None,
    log_x: bool = True,
) -> None:
    """Save a multi-line plot comparing several simulations."""
    output_path = Path(output_path)
    ensure_dir(output_path.parent)

    plt.figure(figsize=(8, 5))

    for label, group in all_summary.groupby(series_col):
        group = group.sort_values(x)
        plt.plot(
            group[x],
            group[y],
            marker="o",
            linewidth=1,
            label=str(label),
        )

    plt.xlabel("victim degree k")
    plt.ylabel(y_label or y)

    if title:
        plt.title(title)

    if log_x:
        plt.xscale("log")

    plt.grid(True, alpha=0.3)
    plt.legend()
    plt.tight_layout()
    plt.savefig(output_path, dpi=200)
    plt.close()


def plot_pareto(
    summary: pd.DataFrame,
    pareto: pd.DataFrame,
    output_path: str | Path,
    *,
    title: str = "Multi-objective view: minimize f and tau",
    annotate: bool = False,
    max_labels: int = 6,
) -> None:
    """Save a scatter plot showing the Pareto-efficient degrees."""
    output_path = Path(output_path)
    ensure_dir(output_path.parent)

    plt.figure(figsize=(7, 5))

    plt.scatter(
        summary["mean_spread_factor"],
        summary["mean_tau"],
        alpha=0.6,
        label="degree bins",
    )

    if not pareto.empty:
        plt.scatter(
            pareto["mean_spread_factor"],
            pareto["mean_tau"],
            marker="x",
            s=70,
            label="Pareto front",
        )

        if annotate:
            label_df = pareto.sort_values("degree").copy()

            if len(label_df) > max_labels:
                label_df = label_df.iloc[
                    np.linspace(0, len(label_df) - 1, max_labels).round().astype(int)
                ]

            for _, row in label_df.iterrows():
                plt.annotate(
                    f"k={row['degree']:.1f}",
                    (row["mean_spread_factor"], row["mean_tau"]),
                    textcoords="offset points",
                    xytext=(6, 4),
                    fontsize=9,
                )

    plt.xlabel("mean spread factor f")
    plt.ylabel("mean spreading time tau")
    plt.title(title)
    plt.grid(True, alpha=0.3)
    plt.legend()
    plt.tight_layout()
    plt.savefig(output_path, dpi=200)
    plt.close()