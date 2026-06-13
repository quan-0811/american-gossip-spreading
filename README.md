# American Gossip Spreading

Mathematical Modeling capstone project on **the spread of gossip in American school friendship networks**.

The project models a school as a graph:

* student = node
* friendship = edge
* gossip victim = target node
* gossip originator = one friend of the victim

The simulator measures:

* **Spread factor**: `f = nf / k`

  * `k` = number of friends of the victim
  * `nf` = number of victim-friends who hear the gossip
* **Spreading time**: `tau`

  * number of steps needed for gossip to reach all reachable victim-friends

## Project structure

```text
american-gossip-spreading/
├── pyproject.toml
├── README.md
├── src/gossip_model/
│   ├── networks.py
│   ├── simulator.py
│   ├── analysis.py
│   └── plots.py
├── scripts/
│   ├── run_ba_multi.py
│   ├── run_sensitivity_q.py
│   ├── run_network_comparison.py
│   ├── run_school_like.py
│   └── run_from_edgelist.py
├── tests/
│   └── test_simulator.py
├── results/
└── docs/
```


## Setup

```bash
conda create -n ags python=3.11 -y
conda activate ags
pip install -e ".[dev]"
```

Verify installation:

```bash
python -c "import gossip_model; print(gossip_model.__file__)"
```

Run tests:

```bash
python -m pytest -q
```

Expected:

```text
4 passed
```

## Reproduce final experiments

### 1. BA main experiment

```bash
python scripts/run_ba_multi.py \
  --n 5000 \
  --realizations 30 \
  --m-values 3 5 7 \
  --output-dir results/ba_final
```

Main outputs:

```text
results/ba_final/run_summary.csv
results/ba_final/figures/ba_spread_factor_by_m.png
results/ba_final/figures/ba_spreading_time_by_m.png
```

### 2. One-shot stochastic sensitivity

```bash
python scripts/run_sensitivity_q.py \
  --network ba \
  --n 5000 \
  --m 5 \
  --realizations 20 \
  --q-values 1.0 0.8 0.5 0.3 0.1 \
  --mode one_shot \
  --output-dir results/sensitivity_q_final
```

### 3. Repeated stochastic sensitivity

```bash
python scripts/run_sensitivity_q.py \
  --network ba \
  --n 5000 \
  --m 5 \
  --realizations 20 \
  --q-values 1.0 0.8 0.5 0.3 0.1 \
  --mode repeated \
  --output-dir results/sensitivity_q_repeated_final
```

### 4. Network comparison

```bash
python scripts/run_network_comparison.py \
  --n 5000 \
  --realizations 20 \
  --output-dir results/network_comparison
```

This compares:

* BA scale-free network
* ER random graph
* WS small-world graph
* school-like SBM network

## View summaries

```bash
python - <<'PY'
import pandas as pd

paths = [
    "results/ba_final/run_summary.csv",
    "results/sensitivity_q_final/run_summary.csv",
    "results/sensitivity_q_repeated_final/run_summary.csv",
    "results/network_comparison/run_summary.csv",
]

for path in paths:
    print("\n" + path)
    print(pd.read_csv(path).to_string(index=False))
PY
```

## Main findings

1. BA networks show a U-shaped relationship between victim degree `k` and spread factor `f`.
2. There is an intermediate degree `k0` where relative gossip spread is minimized.
3. Denser BA networks have larger minimum spread and lower optimal degree.
4. In one-shot spreading, lower transmission probability `q` makes gossip die earlier.
5. In repeated spreading, lower `q` keeps the final spread similar but increases spreading time.
6. Network comparison shows that the optimal-degree effect depends strongly on topology, especially hubs and degree heterogeneity.

## Real data

If real friendship data is available, place it at:

```text
data/raw/school_edges.csv
```

Expected format:

```csv
source,target
student_1,student_2
student_2,student_7
```

Run:

```bash
python scripts/run_from_edgelist.py \
  --edge-list data/raw/school_edges.csv \
  --source-col source \
  --target-col target \
  --largest-component \
  --output-dir results/real_school
```

If the dataset contains multiple schools, run each school separately and aggregate the results.
