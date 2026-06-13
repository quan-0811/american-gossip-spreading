#!/usr/bin/env python3
"""Compare gossip spreading across BA, ER, WS, and school-like networks."""

from __future__ import annotations

import argparse
from pathlib import Path

import networkx as nx
import pandas as pd

from gossip_model.analysis import (
    log_bin_summary,
    pareto_front,
    summarize_run,
)
from gossip_model.networks import (
    make_barabasi_albert,
    make_erdos_renyi,
    make_watts_strogatz,
    make_school_like_sbm,
)
from gossip_model.plots import plot_multi_series, plot_pareto
from gossip_model.simulator import simulate_graph


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()

    parser.add_argument("--n", type=int, default=5000)
    parser.add_argument("--realizations", type=int, default=20)
    parser.add_argument("--seed", type=int, default=2025)
    parser.add_argument("--log-bins", type=int, default=24)
    parser.add_argument("--output-dir", type=Path, default=Path("results/network_comparison"))

    # BA parameter
    parser.add_argument("--ba-m", type=int, default=5)

    # ER parameter.
    # For fair comparison with BA m=5, average degree is about 2m=10,
    # so p approx 10/(n-1).
    parser.add_argument("--er-avg-degree", type=float, default=10.0)

    # WS parameters.
    # k=10 gives similar average degree to BA m=5.
    parser.add_argument("--ws-k", type=int, default=10)
    parser.add_argument("--ws-p", type=float, default=0.1)

    # School-like SBM parameters.
    parser.add_argument("--groups", type=int, default=20)
    parser.add_argument("--p-in", type=float, default=0.04)
    parser.add_argument("--p-out", type=float, default=0.0015)

    return parser.parse_args()


def make_graphs(args: argparse.Namespace, seed: int) -> dict[str, nx.Graph]:
    er_p = args.er_avg_degree / (args.n - 1)

    return {
        f"BA_m{args.ba_m}": make_barabasi_albert(
            n=args.n,
            m=args.ba_m,
            seed=seed,
        ),
        f"ER_avg{args.er_avg_degree:g}": make_erdos_renyi(
            n=args.n,
            p=er_p,
            seed=seed,
        ),
        f"WS_k{args.ws_k}_p{args.ws_p:g}": make_watts_strogatz(
            n=args.n,
            k=args.ws_k,
            p=args.ws_p,
            seed=seed,
        ),
        "School_like_SBM": make_school_like_sbm(
            n=args.n,
            groups=args.groups,
            p_in=args.p_in,
            p_out=args.p_out,
            seed=seed,
        ),
    }


def main() -> None:
    args = parse_args()

    args.output_dir.mkdir(parents=True, exist_ok=True)
    (args.output_dir / "figures").mkdir(exist_ok=True)

    all_victims = []
    all_summaries = []
    table_rows = []

    for r in range(args.realizations):
        seed = args.seed + r

        print(f"Realization {r + 1}/{args.realizations}, seed={seed}")

        graphs = make_graphs(args, seed)

        for name, g in graphs.items():
            print(
                f"  {name}: nodes={g.number_of_nodes()}, "
                f"edges={g.number_of_edges()}, "
                f"avg_degree={2 * g.number_of_edges() / g.number_of_nodes():.2f}"
            )

            victims = simulate_graph(g, min_degree=1)
            victims["network"] = name
            victims["realization"] = r

            all_victims.append(victims)

    victims_df = pd.concat(all_victims, ignore_index=True)

    for name, group in victims_df.groupby("network"):
        summary = log_bin_summary(group, bins=args.log_bins)
        summary["network"] = name
        summary["series"] = name

        all_summaries.append(summary)
        table_rows.append(summarize_run(name, summary))

        pf = pareto_front(summary)
        pf.to_csv(args.output_dir / f"{name}_pareto.csv", index=False)

        plot_pareto(
            summary,
            pf,
            args.output_dir / "figures" / f"{name}_pareto.png",
            title=f"{name}: Pareto view of f and tau",
        )

    summary_all = pd.concat(all_summaries, ignore_index=True)
    run_summary = pd.DataFrame(table_rows)

    victims_df.to_csv(args.output_dir / "victim_results.csv", index=False)
    summary_all.to_csv(args.output_dir / "degree_summary_all.csv", index=False)
    run_summary.to_csv(args.output_dir / "run_summary.csv", index=False)

    plot_multi_series(
        summary_all,
        args.output_dir / "figures" / "spread_factor_by_network.png",
        y="mean_spread_factor",
        title="Network comparison: spread factor vs victim degree",
        y_label="mean spread factor f",
    )

    plot_multi_series(
        summary_all,
        args.output_dir / "figures" / "spreading_time_by_network.png",
        y="mean_tau",
        title="Network comparison: spreading time vs victim degree",
        y_label="mean spreading time tau",
    )

    print("\nRun summary")
    print(run_summary.to_string(index=False))
    print(f"\nSaved results to {args.output_dir}")


if __name__ == "__main__":
    main()