"""
fuzzy_hrm.py
Implementation of the fuzzy graph model in
"Hidden Key Employees in Informal Communication Networks:
 A Fuzzy Graph Model of Key-Person Risk for Human Resource Planning".

Section references (Sec. 3.x, 4.x, Appendix A.x) point to the manuscript.
Only standard libraries plus numpy, pandas and networkx are used.
"""
from __future__ import annotations

import math
import random
from collections import defaultdict

import networkx as nx
import numpy as np
import pandas as pd


# ----------------------------------------------------------------------
# Data loading (Sec. 4.1)
# ----------------------------------------------------------------------
def load_eu_core_temporal(path):
    """SNAP email-Eu-core-temporal: whitespace-separated 'src dst timestamp'."""
    df = pd.read_csv(path, sep=r"\s+", header=None, names=["sender", "receiver", "time"])
    return df


def load_eu_core_departments(path):
    """SNAP email-Eu-core-department-labels: 'node department'."""
    df = pd.read_csv(path, sep=r"\s+", header=None, names=["node", "department"])
    return dict(zip(df.node, df.department))


def link_weights(events, eta=0.0, employees=None):
    """Recency-weighted interaction volume w_uv (Sec. 4.1).

    events: DataFrame with columns sender, receiver, time (one row per recipient).
    eta = 0 gives plain message counts.  Self-messages are dropped; links are undirected.
    employees: optional set V; events involving anyone outside V are dropped (Enron).
    """
    ev = events[events.sender != events.receiver]
    if employees is not None:
        ev = ev[ev.sender.isin(employees) & ev.receiver.isin(employees)]
    T = ev.time.max()
    wt = np.exp(-eta * (T - ev.time.to_numpy(dtype=float))) if eta > 0 else np.ones(len(ev))
    u = np.minimum(ev.sender.to_numpy(), ev.receiver.to_numpy())
    v = np.maximum(ev.sender.to_numpy(), ev.receiver.to_numpy())
    agg = pd.DataFrame({"u": u, "v": v, "w": wt}).groupby(["u", "v"], as_index=False).w.sum()
    return {(a, b): w for a, b, w in agg.itertuples(index=False)}


def eta0(events):
    """eta_0 = 2 ln 2 / H, H = length of the observation window (Sec. 4.1)."""
    H = float(events.time.max() - events.time.min())
    return 2 * math.log(2) / H


# ----------------------------------------------------------------------
# Membership functions (Sec. 4.2)
# ----------------------------------------------------------------------
def lambda0(w):
    """lambda_0 = ln 2 / median of positive w_uv."""
    pos = [x for x in w.values() if x > 0]
    return math.log(2) / float(np.median(pos))


def build_fuzzy_graph(w, lam=None, vertices=None):
    """Return (sigma, mu) with mu keyed by sorted vertex pairs."""
    if lam is None:
        lam = lambda0(w)
    act = defaultdict(float)
    for (a, b), x in w.items():
        act[a] += x
        act[b] += x
    V = set(vertices) if vertices is not None else set(act)
    a_max = max(act.values()) if act else 0.0
    if a_max == 0:  # convention: no interactions
        return {v: 0.0 for v in V}, {}
    sigma = {v: math.log1p(act.get(v, 0.0)) / math.log1p(a_max) for v in V}
    mu = {}
    for (a, b), x in w.items():
        if x > 0:
            mu[(a, b)] = min(sigma[a], sigma[b]) * (1 - math.exp(-lam * x))
    return sigma, mu


# ----------------------------------------------------------------------
# Union-find and maximum spanning forest (Lemma 4.1, Prop. 4.2)
# ----------------------------------------------------------------------
class DSU:
    def __init__(self, items):
        self.p = {x: x for x in items}
        self.s = {x: 1 for x in items}

    def find(self, x):
        p = self.p
        while p[x] != x:
            p[x] = p[p[x]]
            x = p[x]
        return x

    def union(self, a, b):
        a, b = self.find(a), self.find(b)
        if a == b:
            return 0, 0
        if self.s[a] < self.s[b]:
            a, b = b, a
        sa, sb = self.s[a], self.s[b]
        self.p[b] = a
        self.s[a] += sb
        return sa, sb


def sorted_arcs(mu):
    """Arcs in non-increasing order of membership (computed once, reused)."""
    return sorted(((m, a, b) for (a, b), m in mu.items()), reverse=True)


def capacity(V, arcs, removed=frozenset()):
    """Q = sum of CONN over all pairs of V \\ removed (Prop. 4.2).

    arcs: output of sorted_arcs.  Returns (Q, forest_edges).
    """
    Vs = [v for v in V if v not in removed]
    dsu = DSU(Vs)
    Q = 0.0
    forest = []
    for m, a, b in arcs:
        if a in removed or b in removed:
            continue
        sa, sb = dsu.union(a, b)
        if sa:
            Q += m * sa * sb
            forest.append((a, b, m))
    return Q, forest


def nci(V, arcs):
    n = len(V)
    Q, _ = capacity(V, arcs)
    return 2 * Q / (n * (n - 1))


def conn_row(forest_adj, w):
    """CONN_G(w, x) for all x in w's component: min membership on the forest path."""
    row = {w: 1.0}
    stack = [w]
    while stack:
        x = stack.pop()
        for y, m in forest_adj[x]:
            if y not in row:
                row[y] = min(row[x], m)
                stack.append(y)
    del row[w]
    return row


def forest_adjacency(forest):
    adj = defaultdict(list)
    for a, b, m in forest:
        adj[a].append((b, m))
        adj[b].append((a, m))
    return adj


# ----------------------------------------------------------------------
# Departure measures (Def. 3.16, Cor. 4.1, Appendix A.2)
# ----------------------------------------------------------------------
def departure_measures(V, arcs, S, QG=None, adj=None):
    """Return (R(S), T(S)) for a departing set S."""
    S = frozenset(S)
    if QG is None or adj is None:
        QG, forest = capacity(V, arcs)
        adj = forest_adjacency(forest)
    rows = {s: conn_row(adj, s) for s in S}
    own = sum(sum(r.values()) for r in rows.values())
    inner = sum(rows[s].get(t, 0.0) for s in S for t in S if s < t) if len(S) > 1 else 0.0
    Q_surv = QG - own + inner          # inclusion-exclusion (Appendix A.2)
    Q_after, _ = capacity(V, arcs, removed=S)
    tol = 1e-9 * max(QG, 1.0)          # inclusion-exclusion leaves float round-off
    R = (Q_surv - Q_after) / Q_surv if Q_surv > tol else 0.0
    T = (QG - Q_after) / QG if QG > 0 else 0.0
    return max(R, 0.0), T              # max() only guards float round-off


def key_person_scores(V, arcs):
    """KS(w) = R({w}) and T({w}) for every employee (Sec. 4.4, Cor. 4.1)."""
    QG, forest = capacity(V, arcs)
    adj = forest_adjacency(forest)
    ks, tt = {}, {}
    for w in V:
        ks[w], tt[w] = departure_measures(V, arcs, [w], QG, adj)
    return ks, tt


# ----------------------------------------------------------------------
# Structure: bridges, cutvertices, hidden key employees (Sec. 4.4, App. A.3)
# ----------------------------------------------------------------------
def fuzzy_bridges(V, mu, arcs):
    """Lemma A.1: search only forest arcs; e is a bridge iff u,v disconnected in H_mu(e) - e."""
    _, forest = capacity(V, arcs)
    bridges = []
    for a, b, m in forest:
        dsu = DSU(V)
        for m2, x, y in arcs:
            if m2 < m:
                break
            if (x, y) != (a, b):
                dsu.union(x, y)
        if dsu.find(a) != dsu.find(b):
            bridges.append((a, b))
    return bridges


def crisp_graph(V, mu):
    G = nx.Graph()
    G.add_nodes_from(V)
    G.add_edges_from(mu.keys())
    return G


def algorithm1(V, mu):
    """Algorithm 1 (Appendix A.3), used as an independent cross-check."""
    levels = sorted(set(mu.values()), reverse=True)
    B, C = set(), set()
    for t in levels:
        H = nx.Graph()
        H.add_nodes_from(V)
        H.add_edges_from(e for e, m in mu.items() if m >= t)
        for x, y in nx.bridges(H):
            e = (min(x, y), max(x, y))
            if mu[e] == t:
                B.add(e)
        C |= set(nx.articulation_points(H))
    crisp_cut = set(nx.articulation_points(crisp_graph(V, mu)))
    return B, C, C - crisp_cut


def hidden_key_employees(V, mu, ks, p=0.05):
    """All hidden key vertices (Def. 3.13) and the material ones (Def. 3.17).

    Material: hidden key vertices among the top ceil(p*n) of all employees by KS;
    employees tied with the ceil(p*n)-th KS value are all included.
    """
    crisp_cut = set(nx.articulation_points(crisp_graph(V, mu)))
    fuzzy_cut = {w for w in V if ks[w] > 1e-12}
    hidden = fuzzy_cut - crisp_cut
    material = hidden & top_group(ks, p)
    return fuzzy_cut, hidden, material


# ----------------------------------------------------------------------
# Baseline rankings and departure scenarios (Sec. 4.5)
# ----------------------------------------------------------------------
def rank(scores, seed):
    """Descending order; ties broken at random with a fixed seed."""
    rng = random.Random(seed)
    keys = {v: rng.random() for v in scores}
    return sorted(scores, key=lambda v: (-scores[v], keys[v]))


def strategy_scores(V, mu, ks):
    G = crisp_graph(V, mu)
    Gw = nx.Graph()
    Gw.add_nodes_from(V)
    for (a, b), m in mu.items():
        Gw.add_edge(a, b, length=1 / m, weight=m)
    return {
        "S1 Fuzzy KS": ks,
        "S2 Crisp degree": dict(G.degree()),
        "S3 Crisp betweenness": nx.betweenness_centrality(G, normalized=False),
        "S4 Weighted degree": dict(Gw.degree(weight="weight")),
        "S5 Weighted betweenness": nx.betweenness_centrality(Gw, weight="length", normalized=False),
    }


def crisp_outcomes(G, S):
    """Share of originally connected surviving pairs now disconnected; largest-component share."""
    comp0 = {v: i for i, c in enumerate(nx.connected_components(G)) for v in c}
    H = G.subgraph([v for v in G if v not in S])
    sizes0 = defaultdict(int)
    for v in H:
        sizes0[comp0[v]] += 1
    pairs0 = sum(s * (s - 1) / 2 for s in sizes0.values())
    comps = list(nx.connected_components(H))
    pairs1 = sum(len(c) * (len(c) - 1) / 2 for c in comps)
    disc = (pairs0 - pairs1) / pairs0 if pairs0 else 0.0
    lcc = max((len(c) for c in comps), default=0) / max(len(H), 1)
    return disc, lcc


def simulate(V, mu, arcs, order, K):
    """Remove the first k employees of `order`, k = 1..K; record all outcomes."""
    QG, forest = capacity(V, arcs)
    adj = forest_adjacency(forest)
    G = crisp_graph(V, mu)
    rows = []
    for k in range(1, K + 1):
        S = order[:k]
        R, T = departure_measures(V, arcs, S, QG, adj)
        disc, lcc = crisp_outcomes(G, set(S))
        rows.append({"k": k, "R": R, "T": T, "disconnected": disc, "lcc_share": lcc})
    return pd.DataFrame(rows)


def run_scenarios(V, mu, ks, wave=0.05, n_random_runs=100, seed=2026):
    """All strategies S1-S6 for one departure wave; returns wave averages (L_S etc.)."""
    arcs = sorted_arcs(mu)
    K = max(1, math.ceil(wave * len(V)))
    out = []
    for name, sc in strategy_scores(V, mu, ks).items():
        df = simulate(V, mu, arcs, rank(sc, seed), K)
        out.append({"strategy": name, **df[["R", "T", "disconnected", "lcc_share"]].mean().to_dict()})
    rng = random.Random(seed)
    Vl = sorted(V)
    rand = []
    for _ in range(n_random_runs):
        order = Vl[:]
        rng.shuffle(order)
        rand.append(simulate(V, mu, arcs, order, K)[["R", "T", "disconnected", "lcc_share"]].mean())
    rd = pd.DataFrame(rand)
    row = {"strategy": "S6 Random (mean)", **rd.mean().to_dict()}
    half = 1.96 * rd.R.std(ddof=1) / math.sqrt(n_random_runs)
    row["CI_low"], row["CI_high"] = rd.R.mean() - half, rd.R.mean() + half   # 95% CI of L_S for S6
    out.append(row)
    res = pd.DataFrame(out).rename(columns={"R": "L_S (mean R)"})
    return res


# ----------------------------------------------------------------------
# Robustness criteria (Sec. 4.6)
# ----------------------------------------------------------------------
def top_group(ks, p=0.05):
    """Top ceil(p*n) employees by KS; everyone tied with the cutoff value is included."""
    m = max(1, math.ceil(p * len(ks)))
    cutoff = sorted(ks.values(), reverse=True)[m - 1]
    return {v for v, x in ks.items() if x >= cutoff - 1e-15}


def jaccard(A, B):
    A, B = set(A), set(B)
    return len(A & B) / len(A | B) if A | B else 1.0


def kendall_positive(ks_a, ks_b):
    """Kendall's tau-b over employees with KS > 0 in at least one of the two settings."""
    from scipy.stats import kendalltau
    pos = [v for v in ks_a if ks_a[v] > 1e-12 or ks_b.get(v, 0.0) > 1e-12]
    if len(pos) < 2:
        return float("nan")
    return kendalltau([ks_a[v] for v in pos], [ks_b.get(v, 0.0) for v in pos]).statistic


def robustness(main, other, tau_min=0.70, jaccard_min=0.50, p=0.05):
    """Compare two settings; each argument is a dict with 'ks' and 'scenarios' (run_scenarios output).

    Returns the three criteria separately: S1 rank, tau, Jaccard, and pass flags.
    """
    order = other["scenarios"].sort_values("L_S (mean R)", ascending=False).strategy.tolist()
    s1_rank = order.index("S1 Fuzzy KS") + 1
    tau = kendall_positive(main["ks"], other["ks"])
    J = jaccard(top_group(main["ks"], p), top_group(other["ks"], p))
    return {"S1_rank": s1_rank, "S1_first": s1_rank == 1,
            "tau_positive": tau, "tau_pass": bool(tau >= tau_min),
            "jaccard_top": J, "jaccard_pass": J >= jaccard_min,
            "top_size_main": len(top_group(main["ks"], p)), "top_size_other": len(top_group(other["ks"], p))}
