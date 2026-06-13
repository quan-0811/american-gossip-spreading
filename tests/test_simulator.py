from __future__ import annotations

import networkx as nx

from gossip_model.simulator import (
    simulate_pair,
    simulate_victim,
    simulate_graph_stochastic,
)


def test_isolated_neighbor_subgraph_counts_originator() -> None:
    # Victim 0 has four friends, but those friends do not know each other.
    g = nx.Graph()
    g.add_edges_from(
        [
            (0, 1),
            (0, 2),
            (0, 3),
            (0, 4),
        ]
    )

    result = simulate_pair(g, victim=0, originator=1)

    assert result.degree == 4
    assert result.reached == 1
    assert result.spread_factor == 0.25
    assert result.tau == 0


def test_path_among_neighbors_reaches_everyone() -> None:
    # Victim 0's friends form a path: 1 - 2 - 3 - 4.
    g = nx.Graph()
    g.add_edges_from(
        [
            (0, 1),
            (0, 2),
            (0, 3),
            (0, 4),
            (1, 2),
            (2, 3),
            (3, 4),
        ]
    )

    result = simulate_victim(g, victim=0)

    assert result.degree == 4
    assert result.mean_spread_factor == 1.0
    assert result.mean_tau == 2.5


def test_component_plus_isolate_average() -> None:
    # Victim 0's neighbor subgraph has component {1, 2, 3} and isolated node 4.
    g = nx.Graph()
    g.add_edges_from(
        [
            (0, 1),
            (0, 2),
            (0, 3),
            (0, 4),
            (1, 2),
            (2, 3),
        ]
    )

    result = simulate_victim(g, victim=0)

    assert result.degree == 4
    assert result.mean_reached == 2.5
    assert result.mean_spread_factor == 0.625
    assert result.mean_tau == 1.25


def test_stochastic_q_one_matches_deterministic() -> None:
    g = nx.Graph()
    g.add_edges_from(
        [
            (0, 1),
            (0, 2),
            (0, 3),
            (1, 2),
            (2, 3),
        ]
    )

    df = simulate_graph_stochastic(g, q=1.0, seed=123)
    victim0 = df[df["victim"] == 0].iloc[0]

    assert victim0["degree"] == 3
    assert victim0["mean_spread_factor"] == 1.0