#!/usr/bin/env python3
"""Run gossip simulations on synthetic school-like networks."""

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
from gossip_model.networks import make_school_like_sbm
from gossip_model.plots import plot_pareto, plot_spread_factor, plot_spreading_time
from gossip_model.simulator import simulate_graph


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()

    parser.add_argument("--n", type=int, default=1000)
    parser.add_argument("--groups", type=int, default=8)
    parser.add_argument("--p-in", type=float, default=0.045)
    parser.add_argument("--p-out", type=float, default=0.003)
    parser.add_argument("--realizations", type=int, default=20)
    parser.add_argument("--seed", type=int, default=123)
    parser.add_argument("--min-degree", type=int, default=1)
    parser.add_argument("--log-bins", type=int, default=20)
    parser.add_argument("--output-dir", type=Path, default=Path("results/school_like"))

    return parser.parse_args()


def main() -> None:
    args = parse_args()

    args.output_dir.mkdir(parents=True, exist_ok=True)
    (args.output_dir / "figures").mkdir(exist_ok=True)

    all_victims = []

    for r in range(args.realizations):
        seed = args.seed + r

        print(
            f"Running synthetic school "
            f"realization={r + 1}/{args.realizations}, "
            f"seed={seed}"
        )

        g = make_school_like_sbm(
            n=args.n,
            groups=args.groups,
            p_in=args.p_in,
            p_out=args.p_out,
            seed=seed,
        )

        victims_df = simulate_graph(g, min_degree=args.min_degree)
        victims_df["realization"] = r
        victims_df["network"] = "school_like_sbm"

        all_victims.append(victims_df)

    victims = pd.concat(all_victims, ignore_index=True)

    exact = degree_summary(victims)
    binned = log_bin_summary(
        victims,
        bins=args.log_bins,
        min_degree=args.min_degree,
    )
    pf = pareto_front(binned)

    run_summary = pd.DataFrame([summarize_run("synthetic_school_like", binned)])

    victims.to_csv(args.output_dir / "victim_results.csv", index=False)
    exact.to_csv(args.output_dir / "degree_summary_exact.csv", index=False)
    binned.to_csv(args.output_dir / "degree_summary_logbin.csv", index=False)
    pf.to_csv(args.output_dir / "pareto_front.csv", index=False)
    run_summary.to_csv(args.output_dir / "run_summary.csv", index=False)

    plot_spread_factor(
        binned,
        args.output_dir / "figures" / "school_like_spread_factor.png",
        title="Synthetic school-like network: spread factor vs victim degree",
    )

    plot_spreading_time(
        binned,
        args.output_dir / "figures" / "school_like_spreading_time.png",
        title="Synthetic school-like network: spreading time vs victim degree",
    )

    plot_pareto(
        binned,
        pf,
        args.output_dir / "figures" / "school_like_pareto.png",
        title="Synthetic school-like network: Pareto view of f and tau",
    )

    print("\nRun summary")
    print(run_summary.to_string(index=False))
    print(f"\nSaved results to {args.output_dir}")


if __name__ == "__main__":
    main()