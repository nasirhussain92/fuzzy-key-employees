"""
verify.py - checks the implementation against the definitions by brute force.

1. Section 3.6 example: reproduces the published table (R, T, crisp and weighted betweenness).
2. Random fuzzy graphs (with and without tied memberships):
   - Prop. 4.2 / Lemma 4.1: Q(G) from the spanning forest = brute-force sum of CONN
   - Cor. 4.1 / App. A.2:   R(S), T(S) = brute force, for single employees and for sets
   - Prop. 3.2:             KS(w) > 0  <=>  w is a fuzzy cutvertex (Def. 3.12)
   - Lemma A.1 / Prop. 4.3: forest-based fuzzy bridges = Def. 3.11 = Algorithm 1
   - Prop. 4.3(2):          Algorithm 1 cutvertices = {KS > 0}
"""
import itertools
import random

import networkx as nx

import fuzzy_hrm as fh


def conn_brute(V, mu, removed=frozenset(), drop_arc=None):
    """Max-min Floyd-Warshall straight from Def. 3.8."""
    Vs = [v for v in V if v not in removed]
    C = {(a, b): 0.0 for a in Vs for b in Vs}
    for (a, b), m in mu.items():
        if a in removed or b in removed or (a, b) == drop_arc:
            continue
        C[(a, b)] = C[(b, a)] = max(C[(a, b)], m)
    for k in Vs:
        for i in Vs:
            cik = C[(i, k)]
            if cik == 0:
                continue
            for j in Vs:
                c = min(cik, C[(k, j)])
                if c > C[(i, j)]:
                    C[(i, j)] = c
    return C


def pair_sum(C, Vs):
    return sum(C[(a, b)] for a, b in itertools.combinations(sorted(Vs), 2))


def brute_R_T(V, mu, S):
    C0 = conn_brute(V, mu)
    C1 = conn_brute(V, mu, removed=frozenset(S))
    surv = [v for v in V if v not in S]
    Qs, Qa, QG = pair_sum(C0, surv), pair_sum(C1, surv), pair_sum(C0, V)
    return ((Qs - Qa) / Qs if Qs > 0 else 0.0), (QG - Qa) / QG


def brute_cutvertices(V, mu):
    C0 = conn_brute(V, mu)
    out = set()
    for w in V:
        C1 = conn_brute(V, mu, removed={w})
        if any(C1[(x, y)] < C0[(x, y)] - 1e-12 for x in V for y in V if x != w and y != w and x < y):
            out.add(w)
    return out


def brute_bridges(V, mu):
    C0 = conn_brute(V, mu)
    out = set()
    for e in mu:
        C1 = conn_brute(V, mu, drop_arc=e)
        if any(C1[(x, y)] < C0[(x, y)] - 1e-12 for x in V for y in V if x < y):
            out.add(e)
    return out


def random_fuzzy_graph(n, p, rng, ties):
    V = list(range(n))
    sigma = {v: rng.uniform(0.3, 1.0) for v in V}
    mu = {}
    for a, b in itertools.combinations(V, 2):
        if rng.random() < p:
            m = min(sigma[a], sigma[b]) * rng.uniform(0.05, 0.99)
            mu[(a, b)] = round(m, 1) if ties else m
    mu = {e: m for e, m in mu.items() if m > 0}
    return V, mu


def check_example():
    V = ["a", "b", "c", "d"]
    mu = {("a", "b"): 0.7, ("a", "c"): 0.8, ("b", "c"): 0.5, ("c", "d"): 0.6}
    arcs = fh.sorted_arcs(mu)
    Q, _ = fh.capacity(V, arcs)
    ks, tt = fh.key_person_scores(V, arcs)
    sc = fh.strategy_scores(V, mu, ks)
    print("Section 3.6 example:  Q(G) = %.1f   NCI = %.3f" % (Q, fh.nci(V, arcs)))
    print("  employee  degree  crisp_btw  weighted_btw   R({w})    T({w})")
    for w in V:
        print("  %-8s  %6d  %9.0f  %12.0f  %6.1f%%  %7.1f%%" % (
            w, sc["S2 Crisp degree"][w], sc["S3 Crisp betweenness"][w],
            sc["S5 Weighted betweenness"][w], 100 * ks[w], 100 * tt[w]))
    expected = {"a": (0.158, 0.600), "b": (0.0, 0.500), "c": (0.632, 0.825), "d": (0.0, 0.450)}
    ok = all(abs(ks[w] - r) < 5e-4 and abs(tt[w] - t) < 5e-4 for w, (r, t) in expected.items())
    ok &= sc["S5 Weighted betweenness"]["a"] == 0 and sc["S3 Crisp betweenness"]["a"] == 0
    _, hidden, material = fh.hidden_key_employees(V, mu, ks)
    ok &= hidden == {"a"}
    print("  hidden key vertices:", hidden, "| matches manuscript:", ok)
    return ok


def check_random(trials=150, seed=7):
    rng = random.Random(seed)
    fails = 0
    for t in range(trials):
        ties = t % 2 == 1
        V, mu = random_fuzzy_graph(rng.randint(5, 11), rng.uniform(0.2, 0.7), rng, ties)
        if not mu:
            continue
        arcs = fh.sorted_arcs(mu)
        C0 = conn_brute(V, mu)
        Q, _ = fh.capacity(V, arcs)
        ok = abs(Q - pair_sum(C0, V)) < 1e-9                                  # Prop 4.2
        ks, tt = fh.key_person_scores(V, arcs)
        for w in V:                                                          # Cor 4.1
            r, tb = brute_R_T(V, mu, [w])
            ok &= abs(ks[w] - r) < 1e-9 and abs(tt[w] - tb) < 1e-9
        S = rng.sample(V, 3)                                                 # App. A.2 (sets)
        r, tb = brute_R_T(V, mu, S)
        rs, ts = fh.departure_measures(V, arcs, S)
        ok &= abs(rs - r) < 1e-9 and abs(ts - tb) < 1e-9
        cut = brute_cutvertices(V, mu)
        ok &= cut == {w for w in V if ks[w] > 1e-12}                        # Prop 3.2
        B, C, H = fh.algorithm1(V, mu)
        fb = {tuple(sorted(e)) for e in fh.fuzzy_bridges(V, mu, arcs)}
        ok &= fb == brute_bridges(V, mu) == B                               # Lemma A.1, Prop 4.3(1)
        ok &= C == cut                                                       # Prop 4.3(2)
        if not ok:
            fails += 1
            print("  FAIL in trial", t, "(ties)" if ties else "")
    print("Random fuzzy graphs: %d trials (half with tied memberships), %d failures" % (trials, fails))
    return fails == 0


def check_robustness_helpers():
    """Def. 3.17 tie rule, Jaccard, and tau restricted to KS > 0 (Sec. 4.6)."""
    ks = {i: 0.0 for i in range(40)}
    ks.update({0: 0.9, 1: 0.5, 2: 0.5, 3: 0.2})          # n = 40, p = 5% -> m = 2
    ok = fh.top_group(ks, 0.05) == {0, 1, 2}            # employee 2 tied with the cutoff
    ok &= abs(fh.jaccard({1, 2, 3}, {2, 3, 4}) - 0.5) < 1e-12
    other = dict(ks); other.update({1: 0.2, 3: 0.5})    # swap two positive employees
    tau = fh.kendall_positive(ks, other)                # computed over {0,1,2,3} only
    from scipy.stats import kendalltau
    ref = kendalltau([0.9, 0.5, 0.5, 0.2], [0.9, 0.2, 0.5, 0.5]).statistic
    ok &= abs(tau - ref) < 1e-12
    print("Robustness helpers (tie rule, Jaccard, tau on KS > 0):", "ok" if ok else "FAIL")
    return ok


if __name__ == "__main__":
    a = check_example()
    print()
    b = check_random()
    c = check_robustness_helpers()
    print("\nALL CHECKS PASSED" if a and b and c else "\nSOME CHECKS FAILED")
