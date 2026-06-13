#!/usr/bin/env python3
"""Run gossip simulation from a real or prepared friendship edge-list CSV."""

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
from gossip_model.networks import (
    largest_connected_component,
    load_edge_list_csv,
    relabel_to_integers,
)
from gossip_model.plots import plot_pareto, plot_spread_factor, plot_spreading_time
from gossip_model.simulator import simulate_graph


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()

    parser.add_argument("--edge-list", type=Path, required=True)
    parser.add_argument("--source-col", default="source")
    parser.add_argument("--target-col", default="target")
    parser.add_argument("--school-col", default=None)
    parser.add_argument("--school-id", default=None)
    parser.add_argument("--largest-component", action="store_true")
    parser.add_argument("--min-degree", type=int, default=1)
    parser.add_argument("--log-bins", type=int, default=20)
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("results/from_edgelist"),
    )

    return parser.parse_args()


def main() -> None:
    args = parse_args()

    args.output_dir.mkdir(parents=True, exist_ok=True)
    (args.output_dir / "figures").mkdir(exist_ok=True)

    g = load_edge_list_csv(
        args.edge_list,
        source_col=args.source_col,
        target_col=args.target_col,
        school_col=args.school_col,
        school_id=args.school_id,
    )

    if args.largest_component:
        g = relabel_to_integers(largest_connected_component(g))

    print(f"Loaded graph: nodes={g.number_of_nodes()}, edges={g.number_of_edges()}")

    victims = simulate_graph(g, min_degree=args.min_degree)

    exact = degree_summary(victims)
    binned = log_bin_summary(
        victims,
        bins=args.log_bins,
        min_degree=args.min_degree,
    )
    pf = pareto_front(binned)

    run_summary = pd.DataFrame([summarize_run("edge_list", binned)])

    victims.to_csv(args.output_dir / "victim_results.csv", index=False)
    exact.to_csv(args.output_dir / "degree_summary_exact.csv", index=False)
    binned.to_csv(args.output_dir / "degree_summary_logbin.csv", index=False)
    pf.to_csv(args.output_dir / "pareto_front.csv", index=False)
    run_summary.to_csv(args.output_dir / "run_summary.csv", index=False)

    plot_spread_factor(
        binned,
        args.output_dir / "figures" / "spread_factor.png",
        title="Real edge list: spread factor vs victim degree",
    )

    plot_spreading_time(
        binned,
        args.output_dir / "figures" / "spreading_time.png",
        title="Real edge list: spreading time vs victim degree",
    )

    plot_pareto(
        binned,
        pf,
        args.output_dir / "figures" / "pareto.png",
        title="Real edge list: Pareto view of f and tau",
    )

    print("\nRun summary")
    print(run_summary.to_string(index=False))
    print(f"\nSaved results to {args.output_dir}")


if __name__ == "__main__":
    main()