"""
benchmark.py - runs the full pipeline on a synthetic email log of email-Eu-core size
(about 1,000 employees, 42 departments, ~25,000 communicating pairs) and times each step.
Synthetic data only: the numbers show speed and that the pipeline works end to end,
not empirical findings.
"""
import sys
import time

import numpy as np
import pandas as pd

import fuzzy_hrm as fh


def synthetic_log(n=1000, depts=42, pairs=25000, seed=1):
    rng = np.random.default_rng(seed)
    dept = rng.integers(0, depts, n)
    act = rng.lognormal(0, 1.0, n)                     # heavy-tailed activity
    rows, seen = [], set()
    while len(seen) < pairs:
        a = rng.choice(n, p=act / act.sum())
        same = np.flatnonzero(dept == dept[a]) if rng.random() < 0.7 else np.arange(n)
        p = act[same] / act[same].sum()
        b = rng.choice(same, p=p)
        if a == b or (min(a, b), max(a, b)) in seen:
            continue
        seen.add((min(a, b), max(a, b)))
        k = 1 + rng.geometric(0.15)                    # messages on this link
        t = rng.uniform(0, 800 * 86400, k)             # ~800 days, like email-Eu-core-temporal
        rows += [(a, b, x) for x in t]
    return pd.DataFrame(rows, columns=["sender", "receiver", "time"]), dict(enumerate(dept))


def tick(label, t0):
    print("  %-46s %7.1f s" % (label, time.time() - t0))
    sys.stdout.flush()
    return time.time()


if __name__ == "__main__":
    runs = int(sys.argv[1]) if len(sys.argv) > 1 else 100
    t0 = time.time()
    events, dept = synthetic_log()
    t = tick("generate synthetic log (%d emails)" % len(events), t0)
    w = fh.link_weights(events, eta=0.0)
    sigma, mu = fh.build_fuzzy_graph(w, vertices=range(1000))
    V = sorted(sigma)
    arcs = fh.sorted_arcs(mu)
    t = tick("weights + memberships (%d employees, %d arcs)" % (len(V), len(mu)), t)
    print("      lambda0 = %.4f, distinct membership levels |M| = %d" % (fh.lambda0(w), len(set(mu.values()))))
    print("      NCI = %.4f" % fh.nci(V, arcs))
    ks, tt = fh.key_person_scores(V, arcs)
    t = tick("KS and T for all employees (Cor. 4.1)", t)
    fuzzy_cut, hidden, material = fh.hidden_key_employees(V, mu, ks)
    t = tick("fuzzy cutvertices / hidden / material", t)
    print("      fuzzy cutvertices %d, hidden %d, material (top 5%% by KS) %d" % (len(fuzzy_cut), len(hidden), len(material)))
    B = fh.fuzzy_bridges(V, mu, arcs)
    t = tick("fuzzy bridges (Lemma A.1)", t)
    print("      fuzzy bridges %d" % len(B))
    res = fh.run_scenarios(V, mu, ks, wave=0.05, n_random_runs=runs)
    t = tick("departure scenarios S1-S6, K=5%%, N_r=%d" % runs, t)
    pd.set_option("display.width", 140)
    print(res.round(4).to_string(index=False))
    tick("TOTAL", t0)
