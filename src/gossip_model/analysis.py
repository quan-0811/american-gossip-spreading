"""Analysis helpers for gossip simulation results."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Optional

import numpy as np
import pandas as pd


@dataclass(frozen=True)
class LogFit:
    """Fit result for tau = A + B ln(k)."""

    A: float
    B: float
    r2: float
    n_points: int


def degree_summary(df: pd.DataFrame) -> pd.DataFrame:
    """Average victim-level results by exact victim degree k."""
    if df.empty:
        return pd.DataFrame(
            columns=[
                "degree",
                "n_victims",
                "mean_spread_factor",
                "std_spread_factor",
                "mean_tau",
                "std_tau",
                "mean_reached",
            ]
        )

    grouped = df.groupby("degree", as_index=False).agg(
        n_victims=("victim", "count"),
        mean_spread_factor=("mean_spread_factor", "mean"),
        std_spread_factor=("mean_spread_factor", "std"),
        mean_tau=("mean_tau", "mean"),
        std_tau=("mean_tau", "std"),
        mean_reached=("mean_reached", "mean"),
    )

    grouped["std_spread_factor"] = grouped["std_spread_factor"].fillna(0.0)
    grouped["std_tau"] = grouped["std_tau"].fillna(0.0)

    return grouped.sort_values("degree").reset_index(drop=True)


def log_bin_summary(
    df: pd.DataFrame,
    bins: int = 25,
    min_degree: int = 1,
) -> pd.DataFrame:
    """Average victim-level results in logarithmic degree bins."""
    if df.empty:
        return pd.DataFrame()

    valid = df[df["degree"] >= min_degree].copy()

    if valid.empty:
        return pd.DataFrame()

    k_min = max(min_degree, int(valid["degree"].min()))
    k_max = int(valid["degree"].max())

    if k_min == k_max:
        return degree_summary(valid)

    edges = np.unique(
        np.floor(
            np.logspace(
                np.log10(k_min),
                np.log10(k_max + 1),
                bins + 1,
            )
        ).astype(int)
    )

    if len(edges) < 3:
        return degree_summary(valid)

    valid["degree_bin"] = pd.cut(
        valid["degree"],
        bins=edges,
        include_lowest=True,
        right=False,
    )

    grouped = valid.groupby("degree_bin", observed=True).agg(
        degree=("degree", "mean"),
        n_victims=("victim", "count"),
        mean_spread_factor=("mean_spread_factor", "mean"),
        std_spread_factor=("mean_spread_factor", "std"),
        mean_tau=("mean_tau", "mean"),
        std_tau=("mean_tau", "std"),
        mean_reached=("mean_reached", "mean"),
    )

    grouped = grouped.reset_index(drop=True)
    grouped["std_spread_factor"] = grouped["std_spread_factor"].fillna(0.0)
    grouped["std_tau"] = grouped["std_tau"].fillna(0.0)

    return grouped.sort_values("degree").reset_index(drop=True)


def find_optimal_degree(
    summary: pd.DataFrame,
    *,
    min_victims: int = 3,
) -> Optional[dict]:
    """Find k0 where the average spread factor f is smallest."""
    if summary.empty:
        return None

    candidates = summary[summary["n_victims"] >= min_victims].copy()

    if candidates.empty:
        candidates = summary.copy()

    idx = candidates["mean_spread_factor"].idxmin()
    row = candidates.loc[idx]

    return {
        "k0": float(row["degree"]),
        "f_min": float(row["mean_spread_factor"]),
        "tau_at_k0": float(row["mean_tau"]),
        "n_victims": int(row["n_victims"]),
    }


def fit_tau_log_law(
    summary: pd.DataFrame,
    *,
    min_degree: int = 2,
    min_victims: int = 1,
) -> Optional[LogFit]:
    """Fit tau = A + B ln(k) using degree-summary data."""
    if summary.empty:
        return None

    data = summary[
        (summary["degree"] >= min_degree)
        & (summary["n_victims"] >= min_victims)
        & np.isfinite(summary["mean_tau"])
    ].copy()

    if len(data) < 2:
        return None

    x = np.log(data["degree"].to_numpy(dtype=float))
    y = data["mean_tau"].to_numpy(dtype=float)

    B, A = np.polyfit(x, y, deg=1)

    y_hat = A + B * x

    ss_res = float(np.sum((y - y_hat) ** 2))
    ss_tot = float(np.sum((y - y.mean()) ** 2))

    r2 = 1.0 if ss_tot == 0 else 1.0 - ss_res / ss_tot

    return LogFit(
        A=float(A),
        B=float(B),
        r2=float(r2),
        n_points=int(len(data)),
    )


def pareto_front(
    summary: pd.DataFrame,
    objectives: Iterable[str] = ("mean_spread_factor", "mean_tau"),
) -> pd.DataFrame:
    """Return rows that are non-dominated for minimizing all objectives."""
    if summary.empty:
        return summary.copy()

    obj = list(objectives)
    data = summary.dropna(subset=obj).copy().reset_index(drop=True)

    keep = []
    values = data[obj].to_numpy(dtype=float)

    for i, row in enumerate(values):
        dominated = False

        for j, other in enumerate(values):
            if i == j:
                continue

            if np.all(other <= row) and np.any(other < row):
                dominated = True
                break

        keep.append(not dominated)

    return data.loc[keep].sort_values(obj).reset_index(drop=True)


def summarize_run(name: str, summary: pd.DataFrame) -> dict:
    """Create a compact dictionary for console output and report tables."""
    optimal = find_optimal_degree(summary) or {}
    fit = fit_tau_log_law(summary)

    return {
        "name": name,
        "degree_min": float(summary["degree"].min()) if not summary.empty else np.nan,
        "degree_max": float(summary["degree"].max()) if not summary.empty else np.nan,
        "k0": optimal.get("k0", np.nan),
        "f_min": optimal.get("f_min", np.nan),
        "tau_at_k0": optimal.get("tau_at_k0", np.nan),
        "log_A": fit.A if fit else np.nan,
        "log_B": fit.B if fit else np.nan,
        "log_r2": fit.r2 if fit else np.nan,
        "fit_points": fit.n_points if fit else 0,
    }