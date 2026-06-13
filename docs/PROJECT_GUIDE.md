# Project Guide: The Spread of Gossip in American Schools

## 0. Purpose of this document

This document explains the full coding and modeling part of our Mathematical Modeling capstone project.

The project topic is:

> **The spread of gossip in American schools**

This guide is written for group members who are working on the report, slides, and presentation. It explains:

1. what problem we are modeling;
2. what mathematical model we implemented;
3. how the code is structured;
4. how to set up the environment;
5. how to run the simulations;
6. how to reproduce the results without committing `results/` to GitHub;
7. what outputs to expect;
8. how to explain the empirical/simulation results;
9. how to structure the final report and presentation.

The code implements a network-based simulator for gossip spreading. Students are modeled as nodes in a graph, friendships are modeled as edges, and gossip is modeled as information spreading inside the friendship neighborhood of one target student.

---

# 1. Problem description

## 1.1 What is the real-world problem?

Gossip is a form of information spreading. Unlike a general rumor, gossip is about a specific person. In this project, that person is called the **victim** or **target node**.

The main question is:

> How does a student’s position in a friendship network affect how far and how fast gossip about that student spreads?

This is a mathematical modeling problem because we are not simply describing gossip verbally. We are building a mathematical representation of a school social network, defining measurable quantities, and running simulations.

---

## 1.2 Network representation

A school friendship network is represented as an undirected graph:

```text
G = (V, E)
```

where:

* `V` is the set of students;
* `E` is the set of friendship links;
* each student is a node;
* each friendship is an edge.

Example:

```text
student A -- student B
student B -- student C
student C -- student D
```

means A knows B, B knows C, and C knows D.

---

## 1.3 Gossip vs rumor

A general rumor may spread through the whole network.

Gossip is different because it is about a specific person. The reference model assumes that gossip about a victim is mainly interesting to people who know the victim personally. Therefore, the gossip is restricted to the victim’s friendship neighborhood.

This is the key modeling assumption.

If the victim is node `v`, then the victim’s direct friends are:

```text
N(v)
```

The gossip spreads only among nodes in `N(v)`.

---

# 2. Mathematical model

## 2.1 Important objects

For each simulation:

| Symbol / term | Meaning                                                    |
| ------------- | ---------------------------------------------------------- |
| `G`           | friendship graph                                           |
| `v`           | victim / target student                                    |
| `N(v)`        | set of friends of the victim                               |
| `k`           | degree of the victim, meaning number of friends            |
| `o`           | originator, one friend of the victim who starts the gossip |
| `nf`          | number of victim-friends who eventually hear the gossip    |
| `f`           | spread factor                                              |
| `tau`         | spreading time                                             |

The victim degree is:

```text
k = |N(v)|
```

The spread factor is:

```text
f = nf / k
```

where:

* `nf` is the number of the victim’s friends who eventually hear the gossip;
* `k` is the total number of friends of the victim.

So:

```text
0 <= f <= 1
```

In the model used by the paper, the lowest meaningful value is usually:

```text
f = 1/k
```

because at least the originator knows the gossip.

---

## 2.2 Spreading rule

The simulation works like this:

1. Choose one victim `v`.
2. Find all friends of the victim: `N(v)`.
3. Choose one originator `o` from `N(v)`.
4. The originator starts gossip about `v`.
5. Gossip spreads only among people in `N(v)`.
6. The process continues until no new reachable friend can hear the gossip.

In graph terms, we build the **induced subgraph** on the victim’s friends:

```text
G[N(v)]
```

This graph contains:

* all friends of the victim;
* all friendship edges among those friends.

The gossip can spread from the originator to every node in the same connected component of `G[N(v)]`.

Therefore:

```text
nf = size of connected component containing the originator
```

and:

```text
f = nf / k
```

The spreading time `tau` is the maximum shortest-path distance from the originator to the reached nodes inside `G[N(v)]`.

---

## 2.3 Why this model makes sense

The model captures the idea that gossip about someone spreads through people who know that person.

If the victim’s friends do not know each other, then the gossip cannot spread far.

If the victim’s friends are connected through many paths, then the gossip can spread to many of them.

Therefore, the danger of gossip is not only determined by how many friends the victim has. It also depends on how those friends are connected to each other.

---

# 3. Project objectives

Our project has five main objectives.

## Objective 1: Reimplement the reference simulator

We implemented the core gossip spreading simulator from the reference model.

The simulator computes:

```text
spread factor f
spreading time tau
```

for many victim nodes and averages the results by victim degree `k`.

---

## Objective 2: Reproduce reference-style behavior on BA networks

The reference compares empirical school networks with artificial network models, especially scale-free networks. We used Barabási–Albert networks as the main artificial model because they create hubs and heterogeneous degrees, which are important in social systems.

We tested:

```text
BA m=3
BA m=5
BA m=7
```

where `m` controls the number of edges each new node forms when entering the network.

---

## Objective 3: Study sensitivity to transmission probability q

The deterministic model assumes gossip always spreads through reachable friendship paths.

We also implemented stochastic versions with transmission probability:

```text
q
```

Two stochastic modes were tested:

| Mode       | Meaning                                                    |
| ---------- | ---------------------------------------------------------- |
| `one_shot` | each informed student gets one chance to transmit gossip   |
| `repeated` | informed students keep trying to transmit gossip over time |

This lets us study how robust the model is when gossip transmission is uncertain.

---

## Objective 4: Compare different network structures

We compared four network types:

```text
BA
ER
WS
School-like SBM
```

This helps answer:

> Is the optimal-degree behavior universal, or does it depend on network topology?

The answer from our simulations is:

> It depends strongly on topology. BA shows the clearest U-shaped curve, while ER and school-like SBM mostly decrease over the observed range, and WS behaves differently because of high clustering and narrow degree range.

---

## Objective 5: Prepare report-ready results

We generated tables and figures for:

1. BA main experiment;
2. one-shot stochastic sensitivity;
3. repeated stochastic sensitivity;
4. network comparison.

These are enough for the report, slides, and presentation.

---

# 4. What are BA, ER, WS, and school-like networks?

## 4.1 BA: Barabási–Albert network

BA means **Barabási–Albert scale-free network**.

It uses preferential attachment:

> New nodes prefer to connect to already popular nodes.

In social terms:

> New students are more likely to become friends with already well-connected students.

Properties:

| Property            | BA                   |
| ------------------- | -------------------- |
| Hubs                | Yes                  |
| Degree distribution | Heavy-tailed         |
| Community structure | Not explicit         |
| Role in project     | Main synthetic model |

BA is important because it creates popular/high-degree students. This is useful for studying gossip because highly connected students can strongly affect spreading.

---

## 4.2 ER: Erdős–Rényi random graph

ER means **Erdős–Rényi random graph**.

Every possible pair of students becomes friends with probability `p`.

In social terms:

> Friendships are formed randomly and independently.

Properties:

| Property            | ER                              |
| ------------------- | ------------------------------- |
| Hubs                | Usually no                      |
| Degree distribution | Concentrated around the average |
| Community structure | No                              |
| Role in project     | Random baseline                 |

ER is not very realistic for schools, but it is a useful baseline. It lets us test whether the BA result is caused simply by random density or by the special scale-free structure.

---

## 4.3 WS: Watts–Strogatz small-world network

WS means **Watts–Strogatz small-world network**.

It starts with local connections and then rewires some edges randomly.

In social terms:

> Students mostly know people in their local circle, but a few links connect distant groups.

Properties:

| Property         | WS                     |
| ---------------- | ---------------------- |
| Hubs             | Usually no             |
| Local clustering | High                   |
| Short paths      | Yes                    |
| Role in project  | Small-world comparison |

WS captures the idea that “friends of my friends are also my friends.” But its degree range is narrow, so it does not reproduce the BA-style optimal-degree curve very well.

---

## 4.4 School-like SBM

SBM means **stochastic block model**.

We divide the school into groups or communities. Students are more likely to be friends inside the same group than across groups.

Parameters:

```text
p_in  = probability of friendship within same group
p_out = probability of friendship across groups
```

Usually:

```text
p_in > p_out
```

Properties:

| Property             | School-like SBM        |
| -------------------- | ---------------------- |
| Hubs                 | Not necessarily        |
| Community structure  | Yes                    |
| Degree heterogeneity | Limited unless tuned   |
| Role in project      | Synthetic school proxy |

This model is more school-like than ER because schools naturally have classes, friend groups, clubs, and communities. However, it still does not fully replace real school data.

---

## 4.5 Why not only use real data?

If real friendship data is available, we should use it as the main experiment.

However, synthetic networks are still useful because they explain mechanisms.

Real data answers:

> What happens in the observed school network?

Synthetic data answers:

> Which structural property causes the result?

For example:

| Question                          | Best answered by |
| --------------------------------- | ---------------- |
| What happens in real school data? | Real data        |
| Are hubs important?               | BA               |
| Is random density enough?         | ER               |
| Is local clustering enough?       | WS               |
| Are school communities enough?    | School-like SBM  |

If real data has multiple schools, we should not merge them into one graph. We should simulate each school separately, then aggregate the results.

Correct:

```text
school_1 -> simulate
school_2 -> simulate
school_3 -> simulate
aggregate results
```

Wrong:

```text
merge all schools into one giant graph
```

---

# 5. Code structure

The project uses this structure:

```text
american-gossip-spreading/
│
├── README.md
├── pyproject.toml
│
├── data/
│   └── raw/
│       └── school_edges.csv              # optional real data
│
├── results/                              # generated locally, not pushed to GitHub
│
├── src/
│   └── gossip_model/
│       ├── __init__.py
│       ├── networks.py
│       ├── simulator.py
│       ├── analysis.py
│       └── plots.py
│
├── scripts/
│   ├── run_ba_multi.py
│   ├── run_school_like.py
│   ├── run_sensitivity_q.py
│   ├── run_from_edgelist.py
│   └── run_network_comparison.py
│
└── tests/
    └── test_simulator.py
```

---

# 6. Explanation of each code file

## 6.1 `src/gossip_model/networks.py`

This file creates or loads networks.

Main functions:

| Function                      | Purpose                                         |
| ----------------------------- | ----------------------------------------------- |
| `make_barabasi_albert`        | creates BA scale-free network                   |
| `make_erdos_renyi`            | creates ER random network                       |
| `make_watts_strogatz`         | creates WS small-world network                  |
| `make_school_like_sbm`        | creates synthetic school-like community network |
| `load_edge_list_csv`          | loads real friendship data from CSV             |
| `largest_connected_component` | keeps the largest connected component           |
| `relabel_to_integers`         | converts node labels to clean integer labels    |

Important detail:

For BA, we use a complete graph with `m+1` initial nodes to avoid low-degree initialization artifacts.

---

## 6.2 `src/gossip_model/simulator.py`

This is the core simulator.

Main functions:

| Function                    | Purpose                                     |
| --------------------------- | ------------------------------------------- |
| `simulate_pair`             | simulate one victim-originator pair         |
| `simulate_victim`           | average over all originators for one victim |
| `simulate_graph`            | simulate all victims in one graph           |
| `simulate_pair_stochastic`  | stochastic simulation for one pair          |
| `simulate_graph_stochastic` | stochastic simulation for all victims       |

The deterministic simulator computes:

```text
degree k
reached nodes nf
spread factor f
spreading time tau
```

The stochastic simulator supports:

```text
mode = one_shot
mode = repeated
```

---

## 6.3 `src/gossip_model/analysis.py`

This file summarizes results.

Main functions:

| Function              | Purpose                                    |
| --------------------- | ------------------------------------------ |
| `degree_summary`      | average results by exact victim degree     |
| `log_bin_summary`     | average results by logarithmic degree bins |
| `find_optimal_degree` | find degree where spread factor is minimum |
| `fit_tau_log_law`     | fit tau = A + B log(k)                     |
| `pareto_front`        | compute Pareto-efficient degree bins       |
| `summarize_run`       | create summary row for report table        |

The most important output columns are:

```text
k0
f_min
tau_at_k0
log_A
log_B
log_r2
```

---

## 6.4 `src/gossip_model/plots.py`

This file creates figures.

Main functions:

| Function              | Purpose                              |
| --------------------- | ------------------------------------ |
| `plot_spread_factor`  | plot spread factor vs victim degree  |
| `plot_spreading_time` | plot spreading time vs victim degree |
| `plot_multi_series`   | compare several curves in one figure |
| `plot_pareto`         | create Pareto plot                   |

The most important figures are:

```text
spread factor f vs victim degree k
spreading time tau vs victim degree k
```

---

## 6.5 `scripts/run_ba_multi.py`

Runs the main BA experiment.

We use it to compare:

```text
BA m=3
BA m=5
BA m=7
```

This is our main reference-style simulation.

---

## 6.6 `scripts/run_sensitivity_q.py`

Runs stochastic sensitivity analysis.

It supports:

```text
--mode one_shot
--mode repeated
```

This script is used to test different transmission probabilities:

```text
q = 1.0, 0.8, 0.5, 0.3, 0.1
```

---

## 6.7 `scripts/run_network_comparison.py`

Compares several network models:

```text
BA_m5
ER_avg10
WS_k10_p0.1
School_like_SBM
```

This is our robustness experiment.

---

## 6.8 `scripts/run_from_edgelist.py`

Runs the simulator on real friendship data.

Expected real-data format:

```csv
source,target
student_1,student_2
student_2,student_7
student_7,student_9
```

Optional format with school IDs:

```csv
school_id,source,target
school_001,student_001,student_023
school_001,student_023,student_091
school_002,student_004,student_100
```

If we have multiple schools, the better method is to run each school separately and aggregate results.

---

# 7. Environment setup

We use Conda.

## 7.1 Create environment

```bash
conda create -n ags python=3.11 -y
conda activate ags
```

## 7.2 Install package

From the project root:

```bash
pip install -e ".[dev]"
```

This installs the package in editable mode, so we do not need:

```bash
export PYTHONPATH=$PWD/src
```

## 7.3 Verify installation

```bash
python -c "import gossip_model; print(gossip_model.__file__)"
```

Expected output should point to:

```text
.../src/gossip_model/__init__.py
```

## 7.4 Run tests

```bash
python -m pytest -q
```

Expected:

```text
4 passed
```

If the error says:

```text
ModuleNotFoundError: No module named 'gossip_model'
```

then run:

```bash
pip install -e ".[dev]"
```

again from the project root.

---

# 8. GitHub / repository policy

We should commit:

```text
README.md
pyproject.toml
src/
scripts/
tests/
docs/
```

We should not commit:

```text
results/
__pycache__/
.pytest_cache/
.venv/
.DS_Store
```

Recommended `.gitignore`:

```gitignore
results/
__pycache__/
*.pyc
.pytest_cache/
.DS_Store
.venv/
.env
```

The `results/` folder can be regenerated by running the scripts below.

---

# 9. How to reproduce all final results

The final results were generated using four main commands:

1. BA final experiment;
2. one-shot stochastic sensitivity;
3. repeated stochastic sensitivity;
4. network comparison.

All commands should be run from the project root.

---

## 9.1 Final BA experiment

```bash
python scripts/run_ba_multi.py \
  --n 5000 \
  --realizations 30 \
  --m-values 3 5 7 \
  --output-dir results/ba_final
```

This generates:

```text
results/ba_final/victim_results.csv
results/ba_final/degree_summary_all.csv
results/ba_final/run_summary.csv
results/ba_final/figures/ba_spread_factor_by_m.png
results/ba_final/figures/ba_spreading_time_by_m.png
results/ba_final/figures/ba_m5_pareto.png
```

Print the summary:

```bash
python - <<'PY'
import pandas as pd
df = pd.read_csv("results/ba_final/run_summary.csv")
print(df.to_string(index=False))
PY
```

Expected final summary:

```text
name      degree_min  degree_max   k0        f_min     tau_at_k0  log_A      log_B    log_r2
BA m=3    3.000000    325.00       56.6286   0.030508  0.359913   -1.252226  0.552665 0.705341
BA m=5    5.385408    354.75       43.1808   0.049024  0.518513   -2.859506  1.107913 0.819094
BA m=7    7.000000    346.00       27.8071   0.066279  0.465523   -3.522495  1.356363 0.885061
```

Small numerical differences may happen if the seed or package versions change.

---

## 9.2 Final one-shot q-sensitivity experiment

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

This generates:

```text
results/sensitivity_q_final/run_summary.csv
results/sensitivity_q_final/figures/spread_factor_by_q.png
results/sensitivity_q_final/figures/spreading_time_by_q.png
```

Expected summary:

```text
q=1.0   k0=44.5505    f_min=0.050837    tau_at_k0=0.549700
q=0.8   k0=44.5505    f_min=0.042000    tau_at_k0=0.430953
q=0.5   k0=68.1373    f_min=0.027132    tau_at_k0=0.410814
q=0.3   k0=84.3077    f_min=0.017829    tau_at_k0=0.289543
q=0.1   k0=296.1818   f_min=0.005641    tau_at_k0=0.355740
```

Interpretation:

* lower `q` gives lower spread factor;
* gossip often dies early;
* smaller spreading time does not mean faster gossip;
* it means the cascade stops earlier.

---

## 9.3 Final repeated q-sensitivity experiment

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

This generates:

```text
results/sensitivity_q_repeated_final/run_summary.csv
results/sensitivity_q_repeated_final/figures/spread_factor_by_q.png
results/sensitivity_q_repeated_final/figures/spreading_time_by_q.png
```

Expected summary:

```text
q=1.0   k0=44.5505    f_min=0.050837    tau_at_k0=0.549700
q=0.8   k0=44.5505    f_min=0.050837    tau_at_k0=0.726731
q=0.5   k0=44.5505    f_min=0.050837    tau_at_k0=1.216486
q=0.3   k0=44.5505    f_min=0.050837    tau_at_k0=2.067630
q=0.1   k0=44.5505    f_min=0.050837    tau_at_k0=6.353491
```

Interpretation:

* spread factor is almost unchanged across `q`;
* spreading time increases strongly as `q` decreases;
* repeated attempts eventually reach the same connected component.

---

## 9.4 Final network comparison experiment

```bash
python scripts/run_network_comparison.py \
  --n 5000 \
  --realizations 20 \
  --output-dir results/network_comparison
```

This generates:

```text
results/network_comparison/run_summary.csv
results/network_comparison/figures/spread_factor_by_network.png
results/network_comparison/figures/spreading_time_by_network.png
```

Expected summary:

```text
name              degree_min  degree_max  k0        f_min     tau_at_k0
BA_m5             5.386630    339.4000    37.6667   0.047818  0.418853
ER_avg10          1.000000    24.5625     24.5625   0.042428  0.040833
School_like_SBM   3.000000    33.7250     33.7250   0.057182  0.672556
WS_k10_p0.1       6.000000    15.0000     15.0000   0.389630  1.322222
```

Interpretation:

* BA shows a clear interior minimum;
* ER and school-like SBM reach minimum at the largest degree bin;
* WS has high spread factor and narrow degree range;
* the optimal-degree effect is not universal;
* network topology matters.

---

# 10. Final result interpretation

## 10.1 Main BA result

The BA final experiment shows a U-shaped relationship between victim degree `k` and spread factor `f`.

For BA:

```text
small k   -> high f
middle k  -> low f
large k   -> high f again
```

This means:

1. Students with very few friends have high relative gossip exposure because one informed friend is already a large fraction of their friendship circle.
2. Students with an intermediate number of friends have the lowest relative gossip spread.
3. Students with very many friends become vulnerable again because their friendship neighborhoods are more likely to be connected through hubs and long paths.

Final BA result:

| BA model |    k0 |  f_min | tau(k0) |
| -------- | ----: | -----: | ------: |
| m=3      | 56.63 | 0.0305 |  0.3599 |
| m=5      | 43.18 | 0.0490 |  0.5185 |
| m=7      | 27.81 | 0.0663 |  0.4655 |

As `m` increases:

```text
network becomes denser
-> friends of the victim are more connected
-> gossip spreads more easily
-> f_min increases
-> optimal degree k0 shifts lower
```

This is the main empirical/simulation result of our project.

---

## 10.2 Spreading time result

The spreading time `tau` generally increases with degree `k`.

This is because higher-degree victims have larger friendship neighborhoods. If gossip can reach more people, it may need more steps to finish spreading.

We fit:

```text
tau = A + B log(k)
```

The final BA fits were:

| BA model |      B |    R^2 |
| -------- | -----: | -----: |
| m=3      | 0.5527 | 0.7053 |
| m=5      | 1.1079 | 0.8191 |
| m=7      | 1.3564 | 0.8851 |

The logarithmic fit is strongest for denser BA networks.

---

## 10.3 One-shot stochastic result

In one-shot mode:

```text
each informed student tries once to transmit gossip
```

As `q` decreases:

```text
spread factor decreases
spreading time also decreases
```

But the lower spreading time does not mean gossip spreads faster.

It means:

```text
gossip dies earlier
```

This is because many transmission attempts fail, and the cascade stops.

---

## 10.4 Repeated stochastic result

In repeated mode:

```text
informed students keep trying to transmit gossip
```

As `q` decreases:

```text
spread factor stays the same
spreading time increases
```

This happens because any `q > 0` can eventually transmit across the same reachable component, but smaller `q` requires more attempts.

This is a very important sensitivity result.

---

## 10.5 Network comparison result

The network comparison shows that the BA model is special.

| Network         | Behavior                                |
| --------------- | --------------------------------------- |
| BA              | clear U-shaped curve                    |
| ER              | mostly decreasing curve                 |
| School-like SBM | mostly decreasing curve                 |
| WS              | high spread factor, narrow degree range |

Conclusion:

> The optimal-degree phenomenon is not universal. It depends on network topology, especially degree heterogeneity and hubs.

---

# 11. Figures to include in report

Use these final figures:

```text
results/ba_final/figures/ba_spread_factor_by_m.png
results/ba_final/figures/ba_spreading_time_by_m.png
results/sensitivity_q_final/figures/spread_factor_by_q.png
results/sensitivity_q_final/figures/spreading_time_by_q.png
results/sensitivity_q_repeated_final/figures/spread_factor_by_q.png
results/sensitivity_q_repeated_final/figures/spreading_time_by_q.png
results/network_comparison/figures/spread_factor_by_network.png
results/network_comparison/figures/spreading_time_by_network.png
```

Optional:

```text
results/ba_final/figures/ba_m5_pareto.png
```

Do not include every Pareto plot. They are less important than the main spread-factor and spreading-time figures.

---

# 12. Suggested report structure

The report should be around 10 pages.

## 12.1 Title

Suggested title:

```text
Mathematical Modeling of Gossip Spreading in American School Friendship Networks
```

---

## 12.2 Abstract

The abstract should briefly state:

1. the problem;
2. the network model;
3. the spread factor and spreading time;
4. the simulations performed;
5. the main result.

Suggested abstract:

```text
This project studies gossip propagation in school friendship networks using a graph-based mathematical model. Students are represented as nodes and friendships as edges. A gossip targets one victim and spreads only among the victim’s direct friends. We reimplemented the reference simulator and measured two quantities: the spread factor, which measures how many of the victim’s friends eventually hear the gossip, and the spreading time, which measures how many steps are needed for the gossip to reach all accessible friends. Simulations were performed on Barabási–Albert scale-free networks, stochastic transmission models, and several comparison networks. The BA simulations show a non-monotonic relationship between victim degree and spread factor, with an intermediate degree minimizing relative gossip spread. Sensitivity analysis shows that the effect of transmission probability depends strongly on whether gossip transmission is one-shot or repeated. Network comparison results show that the optimal-degree phenomenon is topology-dependent and is strongest in heterogeneous networks with hubs.
```

---

## 12.3 Introduction

Include:

* what gossip is;
* why school friendship networks matter;
* why network modeling is suitable;
* project research questions.

Research questions:

```text
1. How does victim degree affect gossip spread?
2. Does an optimal degree k0 exist?
3. How does spreading time depend on degree?
4. How sensitive are results to transmission probability q?
5. Are results robust across network types?
```

---

## 12.4 Reference model

Explain:

* victim;
* originator;
* victim friends;
* induced subgraph;
* spread factor;
* spreading time.

Important equations:

```text
k = |N(v)|
f = nf / k
tau = maximum shortest-path distance inside reached component
```

---

## 12.5 Algorithm

Describe algorithm step-by-step:

```text
For each victim v:
    find N(v)
    build subgraph G[N(v)]
    for each originator o in N(v):
        find connected component of o inside G[N(v)]
        nf = size of component
        f = nf / k
        tau = max shortest-path distance from o to reached nodes
    average f and tau over all originators
average results by victim degree k
```

---

## 12.6 Simulation design

Include four simulation groups:

### Experiment 1: BA main experiment

```text
N = 5000
realizations = 30
m = 3, 5, 7
```

### Experiment 2: One-shot q-sensitivity

```text
N = 5000
m = 5
realizations = 20
q = 1.0, 0.8, 0.5, 0.3, 0.1
mode = one_shot
```

### Experiment 3: Repeated q-sensitivity

```text
N = 5000
m = 5
realizations = 20
q = 1.0, 0.8, 0.5, 0.3, 0.1
mode = repeated
```

### Experiment 4: Network comparison

```text
BA_m5
ER_avg10
WS_k10_p0.1
School_like_SBM
N = 5000
realizations = 20
```

---

## 12.7 Results

Recommended result order:

1. BA spread factor vs degree;
2. BA spreading time vs degree;
3. one-shot q-sensitivity;
4. repeated q-sensitivity;
5. network comparison.

---

## 12.8 Discussion

Key discussion points:

### Point 1: BA reproduces reference-style behavior

BA shows an interior optimal degree.

### Point 2: Denser networks increase gossip risk

As `m` increases, `f_min` increases and `k0` shifts lower.

### Point 3: Transmission assumption matters

One-shot and repeated spreading behave differently.

### Point 4: Network topology matters

BA shows the optimal-degree effect clearly. ER and school-like SBM do not show a clear interior optimum. WS has high spread because of local clustering.

### Point 5: Real data limitation

The original empirical edge list was not included in the reference material. Therefore, our project uses synthetic networks and robustness comparisons. If real data is available, it should be used as the main experiment.

---

## 12.9 Conclusion

Suggested conclusion:

```text
This project reimplemented a network simulator for gossip spreading in school friendship networks. The model represents students as nodes and friendships as edges, then measures the spread factor and spreading time of gossip about a target student. The BA simulations reproduce the main qualitative behavior of the reference: the spread factor is not monotonic with respect to victim degree and has an intermediate minimum. In the final BA experiment, the optimal degree decreased from about 56.63 for m=3 to about 27.81 for m=7, while the minimum spread factor increased from 0.0305 to 0.0663. This suggests that denser friendship networks make gossip harder to contain. Stochastic simulations show that transmission assumptions are important: in one-shot spreading, lower transmission probability reduces the final spread, while in repeated spreading, lower transmission probability mainly delays the process. Finally, comparison across BA, ER, WS, and school-like networks shows that the optimal-degree phenomenon is not universal but depends strongly on network topology.
```

---

# 13. Suggested slide structure

Use around 10–12 slides.

## Slide 1: Title

```text
The Spread of Gossip in American Schools
```

Include names and course.

---

## Slide 2: Problem motivation

Explain:

* gossip targets one person;
* school friendships form a network;
* question: how far and how fast can gossip spread?

---

## Slide 3: Network model

Show:

```text
student = node
friendship = edge
victim = target node
originator = friend who starts gossip
```

---

## Slide 4: Mathematical quantities

Show:

```text
k = number of victim's friends
nf = number of victim's friends reached
f = nf / k
tau = spreading time
```

---

## Slide 5: Algorithm

Use a flowchart:

```text
Choose victim
-> get victim's friends
-> build neighbor subgraph
-> choose originator
-> find reachable component
-> compute f and tau
```

---

## Slide 6: BA experiment

Show BA spread-factor figure.

Key sentence:

```text
The spread factor is U-shaped and has an optimal degree k0.
```

---

## Slide 7: BA spreading time

Show BA spreading-time figure.

Key sentence:

```text
Spreading time increases approximately logarithmically with degree.
```

---

## Slide 8: Stochastic one-shot sensitivity

Show one-shot q figures.

Key sentence:

```text
Lower q reduces final spread because gossip often dies early.
```

---

## Slide 9: Stochastic repeated sensitivity

Show repeated q figures.

Key sentence:

```text
Repeated attempts keep final spread similar, but lower q greatly increases time.
```

---

## Slide 10: Network comparison

Show network comparison spread-factor figure.

Key sentence:

```text
The optimal-degree behavior is strongest in BA networks and is not universal.
```

---

## Slide 11: Limitations

Mention:

* original real edge list not available;
* synthetic models are simplifications;
* real school data should be run school-by-school if available.

---

## Slide 12: Conclusion

Main conclusion:

```text
Gossip risk depends not only on how many friends a student has, but also on how those friends are connected.
```

---

# 14. Presentation talking points

## 14.1 Simple explanation of spread factor

Say:

```text
If a student has 20 friends and gossip reaches 5 of them, the spread factor is 5/20 = 0.25. So 25% of that student's friendship circle heard the gossip.
```

## 14.2 Simple explanation of U-shape

Say:

```text
For students with very few friends, one gossip source is already a large fraction of their friend group. For students with a medium number of friends, the gossip may reach only a small part of the friend group. But for very popular students, their friends are more connected through the network, so gossip can spread widely again.
```

## 14.3 Simple explanation of one-shot vs repeated

Say:

```text
In one-shot mode, each person only tries once. If they fail, the gossip stops on that edge. In repeated mode, people keep trying, so the gossip eventually reaches the same reachable group, but it takes longer when the probability is low.
```

## 14.4 Simple explanation of network comparison

Say:

```text
BA has popular hub students, ER is random, WS has local clustering, and school-like SBM has groups. Only BA clearly shows the reference-style optimal-degree curve, so hubs and degree heterogeneity appear important.
```

---

# 15. Limitations

Our project has these limitations:

1. We did not have the original empirical American-school edge list.
2. Synthetic networks are simplifications of real school friendship systems.
3. The model assumes gossip only spreads among friends of the victim.
4. The model does not include forgetting, refusal, repeated social meetings, emotional factors, or different probabilities for different students.
5. The stochastic model uses the same probability `q` for all edges.
6. The school-like SBM captures communities but not all real social effects such as popularity, grade structure, or asymmetric friendships.

---

# 16. If real data becomes available

If we obtain real data, it should be placed in:

```text
data/raw/school_edges.csv
```

Minimum format:

```csv
source,target
student_1,student_2
student_2,student_7
```

Better format:

```csv
school_id,source,target
school_001,student_1,student_2
school_001,student_2,student_7
school_002,student_3,student_9
```

If there is only one school:

```bash
python scripts/run_from_edgelist.py \
  --edge-list data/raw/school_edges.csv \
  --source-col source \
  --target-col target \
  --largest-component \
  --output-dir results/real_school
```

If there are multiple schools, we should write or use a script that loops over `school_id`, runs each school separately, and aggregates results.

Real data should become the main experiment, while BA/ER/WS/SBM remain comparison models.

---

# 17. What each group member should do

## Coding member

Responsible for:

```text
src/
scripts/
tests/
README.md
PROJECT_GUIDE.md
```

Also responsible for generating final figures and tables.

---

## Report members

Responsible for:

```text
Introduction
Reference model
Mathematical formulation
Algorithm explanation
Results explanation
Discussion
Conclusion
```

Use this guide and the result tables.

---

## Slide members

Responsible for:

```text
10–12 slide presentation
clear diagrams
main figures
short explanation of results
```

---

## Presenter

Responsible for explaining:

```text
what gossip model is
what f and tau mean
why BA has U-shape
what q-sensitivity shows
why topology matters
```

---

# 18. Final checklist

Before submission, check:

```text
[ ] Code runs from clean Conda environment
[ ] python -m pytest -q passes
[ ] README has setup and run commands
[ ] PROJECT_GUIDE.md explains project
[ ] Report includes model equations
[ ] Report includes algorithm
[ ] Report includes final BA result table
[ ] Report includes q-sensitivity tables
[ ] Report includes network comparison table
[ ] Slides include main figures
[ ] results/ is not pushed to GitHub
[ ] final figures are exported for report/slides
```

---

# 19. Short final summary

This project models gossip spreading as a graph process on school friendship networks. A victim is selected, one friend starts gossip, and the gossip spreads only among the victim’s friends. The main measurements are the spread factor `f` and spreading time `tau`.

The main result is that BA scale-free networks show a U-shaped relationship between victim degree and spread factor. This means there is an intermediate degree where the relative spread of gossip is minimized. Stochastic simulations show that transmission assumptions matter: one-shot spreading can die early, while repeated spreading eventually reaches the same component but takes longer when transmission probability is low. Network comparison shows that the optimal-degree phenomenon is not universal; it depends strongly on network topology, especially hubs and degree heterogeneity.
