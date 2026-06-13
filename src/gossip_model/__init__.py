"""Gossip propagation simulator for school friendship networks."""

from .simulator import (
    GossipResult,
    VictimResult,
    simulate_victim,
    simulate_graph,
    simulate_graph_stochastic,
)

__all__ = [
    "GossipResult",
    "VictimResult",
    "simulate_victim",
    "simulate_graph",
    "simulate_graph_stochastic",
]