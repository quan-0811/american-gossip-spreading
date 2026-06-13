#!/usr/bin/env python3
"""Sensitivity analysis for the transmission probability q."""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

from gossip_model.analysis import log_bin_summary, summarize_run
from gossip_model.networks import make_barabasi_albert, make_school_like_sbm
from gossip_model.plots import plot_multi_series
from gossip_model.simulator import simulate_graph_stochastic


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()

    parser.add_argument("--network", choices=["ba", "school_like"], default="ba")
    parser.add_argument("--n", type=int, default=1500)
    parser.add_argument("--m", type=int, default=5)
    parser.add_argument("--groups", type=int, default=8)
    parser.add_argument("--p-in", type=float, default=0.045)
    parser.add_argument("--p-out", type=float, default=0.003)
    parser.add_argument("--realizations", type=int, default=10)
    parser.add_argument(
        "--q-values",
        type=float,
        nargs="+",
        default=[1.0, 0.8, 0.5, 0.3, 0.1],
    )
    parser.add_argument("--mode", choices=["one_shot", "repeated"], default="one_shot")
    parser.add_argument("--repeats-per-originator", type=int, default=1)
    parser.add_argument("--seed", type=int, default=7)
    parser.add_argument("--log-bins", type=int, default=20)
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("results/sensitivity_q"),
    )

    return parser.parse_args()


def make_graph(args: argparse.Namespace, seed: int):
    if args.network == "ba":
        return make_barabasi_albert(args.n, args.m, seed=seed)

    return make_school_like_sbm(
        n=args.n,
        groups=args.groups,
        p_in=args.p_in,
        p_out=args.p_out,
        seed=seed,
    )


def main() -> None:
    args = parse_args()

    args.output_dir.mkdir(parents=True, exist_ok=True)
    (args.output_dir / "figures").mkdir(exist_ok=True)

    all_victims = []
    all_summaries = []
    table_rows = []

    for q in args.q_values:
        q_frames = []

        for r in range(args.realizations):
            graph_seed = args.seed + 1000 * r
            sim_seed = args.seed + 10_000 * r + int(q * 1000)

            print(
                f"Running q={q}, "
                f"realization={r + 1}/{args.realizations}"
            )

            g = make_graph(args, graph_seed)

            victims_df = simulate_graph_stochastic(
                g,
                q=q,
                mode=args.mode,
                repeats_per_originator=args.repeats_per_originator,
                seed=sim_seed,
            )

            victims_df["realization"] = r
            victims_df["network"] = args.network

            q_frames.append(victims_df)

        q_victims = pd.concat(q_frames, ignore_index=True)
        q_summary = log_bin_summary(q_victims, bins=args.log_bins)

        q_summary["q"] = q
        q_summary["series"] = f"q={q}"

        all_victims.append(q_victims)
        all_summaries.append(q_summary)

        table_rows.append(summarize_run(f"{args.network} q={q}", q_summary))

    victims = pd.concat(all_victims, ignore_index=True)
    summaries = pd.concat(all_summaries, ignore_index=True)
    run_summary = pd.DataFrame(table_rows)

    victims.to_csv(args.output_dir / "victim_results.csv", index=False)
    summaries.to_csv(args.output_dir / "degree_summary_by_q.csv", index=False)
    run_summary.to_csv(args.output_dir / "run_summary.csv", index=False)

    plot_multi_series(
        summaries,
        args.output_dir / "figures" / "spread_factor_by_q.png",
        y="mean_spread_factor",
        title=f"Sensitivity to q ({args.mode}): spread factor",
        y_label="mean spread factor f",
    )

    plot_multi_series(
        summaries,
        args.output_dir / "figures" / "spreading_time_by_q.png",
        y="mean_tau",
        title=f"Sensitivity to q ({args.mode}): spreading time",
        y_label="mean spreading time tau",
    )

    print("\nRun summary")
    print(run_summary.to_string(index=False))
    print(f"\nSaved results to {args.output_dir}")


if __name__ == "__main__":
    main()