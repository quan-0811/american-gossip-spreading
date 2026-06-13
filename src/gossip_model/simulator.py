"""Core gossip-spreading simulator."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Literal, Optional

import networkx as nx
import numpy as np
import pandas as pd

TransmissionMode = Literal["one_shot", "repeated"]


@dataclass(frozen=True)
class GossipResult:
    """Result for one victim-originator pair."""

    victim: int
    originator: int
    degree: int
    reached: int
    spread_factor: float
    tau: int


@dataclass(frozen=True)
class VictimResult:
    """Result averaged over all originators of one victim."""

    victim: int
    degree: int
    mean_reached: float
    mean_spread_factor: float
    mean_tau: float
    n_originators: int


def _neighbor_subgraph(g: nx.Graph, victim: int) -> tuple[list[int], nx.Graph]:
    """Return victim's neighbors and the subgraph induced by those neighbors."""
    neighbors = list(g.neighbors(victim))
    return neighbors, g.subgraph(neighbors).copy()


def simulate_pair(
    g: nx.Graph,
    victim: int,
    originator: int,
    *,
    count_originator: bool = True,
) -> GossipResult:
    """Simulate deterministic gossip for one victim-originator pair.

    count_originator=True follows the topic paper's definition: if the
    originator cannot spread the gossip further, the spread factor is 1/k.
    """
    if victim not in g:
        raise ValueError(f"victim {victim!r} is not in graph.")

    if originator not in g[victim]:
        raise ValueError("originator must be a direct neighbor of the victim.")

    neighbors, h = _neighbor_subgraph(g, victim)
    k = len(neighbors)

    if k == 0:
        return GossipResult(victim, originator, 0, 0, 0.0, 0)

    if originator not in h:
        reached_nodes = set()
        tau = 0
    else:
        reached_nodes = nx.node_connected_component(h, originator)

        if len(reached_nodes) <= 1:
            tau = 0
        else:
            distances = nx.single_source_shortest_path_length(h, originator)
            tau = max(distances[node] for node in reached_nodes)

    reached = len(reached_nodes)

    if not count_originator and reached == 1:
        reached = 0

    return GossipResult(
        victim=int(victim),
        originator=int(originator),
        degree=int(k),
        reached=int(reached),
        spread_factor=float(reached / k),
        tau=int(tau),
    )


def simulate_victim(
    g: nx.Graph,
    victim: int,
    *,
    count_originator: bool = True,
) -> VictimResult:
    """Average deterministic gossip over all originators of one victim."""
    if victim not in g:
        raise ValueError(f"victim {victim!r} is not in graph.")

    neighbors = list(g.neighbors(victim))
    k = len(neighbors)

    if k == 0:
        return VictimResult(
            victim=int(victim),
            degree=0,
            mean_reached=0.0,
            mean_spread_factor=0.0,
            mean_tau=0.0,
            n_originators=0,
        )

    pair_results = [
        simulate_pair(
            g,
            victim,
            originator,
            count_originator=count_originator,
        )
        for originator in neighbors
    ]

    return VictimResult(
        victim=int(victim),
        degree=int(k),
        mean_reached=float(np.mean([r.reached for r in pair_results])),
        mean_spread_factor=float(np.mean([r.spread_factor for r in pair_results])),
        mean_tau=float(np.mean([r.tau for r in pair_results])),
        n_originators=int(k),
    )


def simulate_graph(
    g: nx.Graph,
    *,
    victims: Optional[Iterable[int]] = None,
    min_degree: int = 1,
    count_originator: bool = True,
) -> pd.DataFrame:
    """Run deterministic gossip for many victims and return one row per victim."""
    if victims is None:
        victims = list(g.nodes())

    rows = []

    for victim in victims:
        degree = g.degree(victim)

        if degree < min_degree:
            continue

        result = simulate_victim(
            g,
            victim,
            count_originator=count_originator,
        )
        rows.append(result.__dict__)

    return pd.DataFrame(rows)


def _one_shot_stochastic_pair(
    h: nx.Graph,
    originator: int,
    q: float,
    rng: np.random.Generator,
) -> tuple[int, int]:
    """Single-attempt stochastic spread inside an induced neighbor subgraph."""
    informed = {originator}
    frontier = {originator}
    tau = 0

    while frontier:
        new_frontier = set()

        for u in frontier:
            for w in h.neighbors(u):
                if w not in informed and rng.random() <= q:
                    informed.add(w)
                    new_frontier.add(w)

        if new_frontier:
            tau += 1

        frontier = new_frontier

    return len(informed), tau


def _repeated_stochastic_pair(
    h: nx.Graph,
    originator: int,
    q: float,
    rng: np.random.Generator,
    max_steps: int,
) -> tuple[int, int]:
    """Repeated-attempt stochastic spread."""
    reachable = nx.node_connected_component(h, originator)
    informed = {originator}
    tau = 0

    while len(informed) < len(reachable) and tau < max_steps:
        newly_informed = set()

        for u in list(informed):
            for w in h.neighbors(u):
                if w in reachable and w not in informed and rng.random() <= q:
                    newly_informed.add(w)

        tau += 1
        informed.update(newly_informed)

    return len(informed), tau


def simulate_pair_stochastic(
    g: nx.Graph,
    victim: int,
    originator: int,
    *,
    q: float,
    mode: TransmissionMode = "one_shot",
    rng: Optional[np.random.Generator] = None,
    count_originator: bool = True,
    max_steps: int = 10_000,
) -> GossipResult:
    """Simulate stochastic gossip for one victim-originator pair."""
    if not 0 <= q <= 1:
        raise ValueError("q must be in [0, 1].")

    if mode not in {"one_shot", "repeated"}:
        raise ValueError("mode must be 'one_shot' or 'repeated'.")

    if rng is None:
        rng = np.random.default_rng()

    if originator not in g[victim]:
        raise ValueError("originator must be a direct neighbor of the victim.")

    neighbors, h = _neighbor_subgraph(g, victim)
    k = len(neighbors)

    if k == 0:
        return GossipResult(victim, originator, 0, 0, 0.0, 0)

    if q == 1.0:
        return simulate_pair(
            g,
            victim,
            originator,
            count_originator=count_originator,
        )

    if q == 0.0:
        reached = 1 if count_originator else 0
        return GossipResult(victim, originator, k, reached, reached / k, 0)

    if mode == "one_shot":
        reached, tau = _one_shot_stochastic_pair(h, originator, q, rng)
    else:
        reached, tau = _repeated_stochastic_pair(
            h,
            originator,
            q,
            rng,
            max_steps,
        )

    if not count_originator and reached == 1:
        reached = 0

    return GossipResult(
        victim=int(victim),
        originator=int(originator),
        degree=int(k),
        reached=int(reached),
        spread_factor=float(reached / k),
        tau=int(tau),
    )


def simulate_graph_stochastic(
    g: nx.Graph,
    *,
    q: float,
    mode: TransmissionMode = "one_shot",
    victims: Optional[Iterable[int]] = None,
    min_degree: int = 1,
    repeats_per_originator: int = 1,
    seed: Optional[int] = None,
    count_originator: bool = True,
    max_steps: int = 10_000,
) -> pd.DataFrame:
    """Run stochastic gossip and return one row per victim."""
    if repeats_per_originator <= 0:
        raise ValueError("repeats_per_originator must be positive.")

    rng = np.random.default_rng(seed)

    if victims is None:
        victims = list(g.nodes())

    rows = []

    for victim in victims:
        neighbors = list(g.neighbors(victim))
        k = len(neighbors)

        if k < min_degree:
            continue

        pair_results = []

        for originator in neighbors:
            for _ in range(repeats_per_originator):
                pair_results.append(
                    simulate_pair_stochastic(
                        g,
                        victim,
                        originator,
                        q=q,
                        mode=mode,
                        rng=rng,
                        count_originator=count_originator,
                        max_steps=max_steps,
                    )
                )

        rows.append(
            {
                "victim": int(victim),
                "degree": int(k),
                "mean_reached": float(np.mean([r.reached for r in pair_results])),
                "mean_spread_factor": float(
                    np.mean([r.spread_factor for r in pair_results])
                ),
                "mean_tau": float(np.mean([r.tau for r in pair_results])),
                "n_originators": int(k),
                "q": float(q),
                "mode": mode,
            }
        )

    return pd.DataFrame(rows)