#!/usr/bin/env python3
"""Run gossip simulations on Barabasi-Albert networks for several m values."""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

from gossip_model.analysis import (
    degree_summary,
    log_bin_summary,
    pareto_front,
    summarize_run,
)
from gossip_model.networks import make_barabasi_albert
from gossip_model.plots import plot_multi_series, plot_pareto
from gossip_model.simulator import simulate_graph


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()

    parser.add_argument("--n", type=int, default=2000)
    parser.add_argument("--m-values", type=int, nargs="+", default=[3, 5, 7])
    parser.add_argument("--realizations", type=int, default=10)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--min-degree", type=int, default=1)
    parser.add_argument("--log-bins", type=int, default=25)
    parser.add_argument("--output-dir", type=Path, default=Path("results/ba_multi"))

    return parser.parse_args()


def main() -> None:
    args = parse_args()

    args.output_dir.mkdir(parents=True, exist_ok=True)
    (args.output_dir / "figures").mkdir(exist_ok=True)

    all_victims = []
    all_summaries = []
    table_rows = []

    for m in args.m_values:
        per_m_victims = []

        for r in range(args.realizations):
            seed = args.seed + 1000 * m + r

            print(
                f"Running BA m={m}, "
                f"realization={r + 1}/{args.realizations}, "
                f"seed={seed}"
            )

            g = make_barabasi_albert(n=args.n, m=m, seed=seed)
            victims_df = simulate_graph(g, min_degree=args.min_degree)

            victims_df["m"] = m
            victims_df["realization"] = r
            victims_df["network"] = "BA"

            per_m_victims.append(victims_df)

        m_victims = pd.concat(per_m_victims, ignore_index=True)

        exact = degree_summary(m_victims)
        binned = log_bin_summary(
            m_victims,
            bins=args.log_bins,
            min_degree=args.min_degree,
        )

        exact["m"] = m
        binned["m"] = m
        exact["series"] = f"m={m}"
        binned["series"] = f"m={m}"

        all_victims.append(m_victims)
        all_summaries.append(binned)

        table_rows.append(summarize_run(f"BA m={m}", binned))

        exact.to_csv(
            args.output_dir / f"ba_m{m}_degree_summary_exact.csv",
            index=False,
        )
        binned.to_csv(
            args.output_dir / f"ba_m{m}_degree_summary_logbin.csv",
            index=False,
        )

    victims = pd.concat(all_victims, ignore_index=True)
    summaries = pd.concat(all_summaries, ignore_index=True)
    run_summary = pd.DataFrame(table_rows)

    victims.to_csv(args.output_dir / "victim_results.csv", index=False)
    summaries.to_csv(args.output_dir / "degree_summary_all.csv", index=False)
    run_summary.to_csv(args.output_dir / "run_summary.csv", index=False)

    plot_multi_series(
        summaries,
        args.output_dir / "figures" / "ba_spread_factor_by_m.png",
        y="mean_spread_factor",
        title="BA networks: spread factor vs victim degree",
        y_label="mean spread factor f",
    )

    plot_multi_series(
        summaries,
        args.output_dir / "figures" / "ba_spreading_time_by_m.png",
        y="mean_tau",
        title="BA networks: spreading time vs victim degree",
        y_label="mean spreading time tau",
    )

    middle_m = args.m_values[len(args.m_values) // 2]
    middle_summary = summaries[summaries["m"] == middle_m].copy()
    pf = pareto_front(middle_summary)

    pf.to_csv(args.output_dir / f"ba_m{middle_m}_pareto_front.csv", index=False)

    plot_pareto(
        middle_summary,
        pf,
        args.output_dir / "figures" / f"ba_m{middle_m}_pareto.png",
        title=f"BA m={middle_m}: Pareto view of f and tau",
    )

    print("\nRun summary")
    print(run_summary.to_string(index=False))
    print(f"\nSaved results to {args.output_dir}")


if __name__ == "__main__":
    main()