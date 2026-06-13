"""Network construction and loading utilities."""

from __future__ import annotations

from pathlib import Path
from typing import Optional

import networkx as nx
import pandas as pd


def relabel_to_integers(g: nx.Graph) -> nx.Graph:
    """Return a copy of g whose node labels are consecutive integers."""
    return nx.convert_node_labels_to_integers(g, first_label=0, ordering="sorted")


def largest_connected_component(g: nx.Graph) -> nx.Graph:
    """Keep only the largest connected component."""
    if g.number_of_nodes() == 0:
        return g.copy()

    if nx.is_connected(g):
        return g.copy()

    largest = max(nx.connected_components(g), key=len)
    return g.subgraph(largest).copy()


def make_barabasi_albert(
    n: int,
    m: int,
    seed: Optional[int] = None,
) -> nx.Graph:
    """Create a Barabasi-Albert scale-free graph.

    We use a complete graph with m+1 nodes as the initial graph.
    This avoids low-degree seed artifacts such as degree-1 nodes when m is large.
    """
    if n <= m + 1:
        raise ValueError("n must be larger than m + 1 for a BA network.")

    initial_graph = nx.complete_graph(m + 1)

    g = nx.barabasi_albert_graph(
        n=n,
        m=m,
        seed=seed,
        initial_graph=initial_graph,
    )

    return relabel_to_integers(g)

def make_erdos_renyi(
    n: int,
    p: float,
    seed: Optional[int] = None,
) -> nx.Graph:
    """Create an Erdos-Renyi random graph and keep its largest component."""
    if not 0 <= p <= 1:
        raise ValueError("p must be in [0, 1].")

    g = nx.erdos_renyi_graph(n=n, p=p, seed=seed)
    return relabel_to_integers(largest_connected_component(g))


def make_watts_strogatz(
    n: int,
    k: int,
    p: float,
    seed: Optional[int] = None,
) -> nx.Graph:
    """Create a Watts-Strogatz small-world graph."""
    if k % 2 != 0:
        raise ValueError("k must be even for a Watts-Strogatz graph.")

    if not 0 <= p <= 1:
        raise ValueError("p must be in [0, 1].")

    g = nx.watts_strogatz_graph(n=n, k=k, p=p, seed=seed)
    return relabel_to_integers(largest_connected_component(g))


def make_school_like_sbm(
    n: int = 1000,
    groups: int = 8,
    p_in: float = 0.045,
    p_out: float = 0.003,
    seed: Optional[int] = None,
) -> nx.Graph:
    """Create a synthetic school-like friendship graph.

    The graph has community structure. Students inside the same group are more
    likely to be friends than students from different groups.
    """
    if groups <= 0:
        raise ValueError("groups must be positive.")

    if not 0 <= p_in <= 1:
        raise ValueError("p_in must be in [0, 1].")

    if not 0 <= p_out <= 1:
        raise ValueError("p_out must be in [0, 1].")

    if p_out > p_in:
        raise ValueError("p_out should not exceed p_in for a school-like graph.")

    base = n // groups
    sizes = [base] * groups
    sizes[-1] += n - sum(sizes)

    probs = []
    for i in range(groups):
        row = []
        for j in range(groups):
            row.append(p_in if i == j else p_out)
        probs.append(row)

    g = nx.stochastic_block_model(sizes=sizes, p=probs, seed=seed)
    return relabel_to_integers(largest_connected_component(g))


def load_edge_list_csv(
    path: str | Path,
    source_col: str = "source",
    target_col: str = "target",
    school_col: Optional[str] = None,
    school_id: Optional[str] = None,
) -> nx.Graph:
    """Load an undirected friendship network from a CSV edge list."""
    path = Path(path)

    if not path.exists():
        raise FileNotFoundError(f"Edge-list file not found: {path}")

    df = pd.read_csv(path)

    required = {source_col, target_col}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"Missing required columns: {sorted(missing)}")

    if school_col is not None and school_id is not None:
        if school_col not in df.columns:
            raise ValueError(f"school_col={school_col!r} is not in the CSV.")

        df = df[df[school_col].astype(str) == str(school_id)]

    df = df[[source_col, target_col]].dropna()

    g = nx.from_pandas_edgelist(df, source=source_col, target=target_col)
    g.remove_edges_from(nx.selfloop_edges(g))

    return relabel_to_integers(g)