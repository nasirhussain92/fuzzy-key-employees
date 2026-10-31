"""
make_figures.py - draws the manuscript figures from the files in results/.

Figure 2: key-person score of the fuzzy cutvertices against their number of contacts,
          hidden key members versus crisp articulation points (RQ1).
Figure 3: departure scenarios (RQ3) - (a) mean survivor loss L_S, (b) share of surviving
          connected pairs disconnected, for departure waves of 1%, 5% and 10%.

Run:  python make_figures.py          (writes figures/figure2.png, figures/figure3.png)
Only results files are read; nothing is recomputed.
"""
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
RES = os.path.join(HERE, "results")
OUT = os.path.join(HERE, "figures")

# validated categorical slots (light surface); S6 random baseline is neutral gray
BLUE, ORANGE, AQUA, YELLOW, MAGENTA = "#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4"
GRAY = "#8c8b86"
INK, INK2, GRID = "#0b0b0b", "#52514e", "#e4e3df"
STRATEGY_COLORS = [BLUE, ORANGE, AQUA, YELLOW, MAGENTA, GRAY]
STRATEGY_LABELS = ["S1 Fuzzy KS", "S2 Crisp degree", "S3 Crisp betweenness",
                   "S4 Weighted degree", "S5 Weighted betweenness", "S6 Random (mean)"]

plt.rcParams.update({
    "font.family": "serif",
    "font.serif": ["Liberation Serif", "Times New Roman", "DejaVu Serif"],
    "font.size": 9,
    "axes.edgecolor": INK2,
    "axes.labelcolor": INK,
    "axes.linewidth": 0.6,
    "xtick.color": INK2,
    "ytick.color": INK2,
    "xtick.major.width": 0.6,
    "ytick.major.width": 0.6,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "savefig.dpi": 600,
    "mathtext.fontset": "stix",
    "savefig.bbox": "tight",
})


def figure2():
    d = pd.read_csv(os.path.join(RES, "main_employee_scores.csv"))
    cut = d[d["fuzzy_cutvertex"]]
    hidden = cut[cut["hidden"]]
    crisp = cut[~cut["hidden"]]
    cutoff = d["KS"].sort_values(ascending=False).iloc[int(-(-0.05 * len(d) // 1)) - 1]

    fig, ax = plt.subplots(figsize=(6.3, 3.9))
    ax.grid(True, which="major", color=GRID, linewidth=0.5)
    ax.set_axisbelow(True)
    ax.scatter(hidden["contacts"], hidden["KS"], s=24, marker="o", color=ORANGE,
               edgecolor="white", linewidth=0.6, alpha=0.9, zorder=3,
               label=f"Hidden key member ({len(hidden)})")
    ax.scatter(crisp["contacts"], crisp["KS"], s=30, marker="^", color=BLUE,
               edgecolor="white", linewidth=0.6, alpha=0.95, zorder=4,
               label=f"Crisp articulation point ({len(crisp)})")
    ax.axhline(cutoff, color=INK2, linewidth=0.8, linestyle=(0, (4, 3)), zorder=2)
    ax.text(2.6, cutoff * 1.25, "top 5% of all members by KS", ha="left", va="bottom",
            color=INK2, fontsize=8)
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlabel("Number of contacts (crisp degree, log scale)")
    ax.set_ylabel("Key-person score KS(w) (log scale)")
    ax.legend(loc="lower left", frameon=False, fontsize=8, handletextpad=0.3)
    os.makedirs(OUT, exist_ok=True)
    fig.savefig(os.path.join(OUT, "figure2.png"))
    plt.close(fig)


def figure3():
    waves = [("1%", "K1"), ("5%", "K5"), ("10%", "K10")]
    tabs = {w: pd.read_csv(os.path.join(RES, f"scenarios_main_{k}.csv")) for w, k in waves}
    fig, axes = plt.subplots(1, 2, figsize=(6.6, 3.2))
    panels = [("L_S (mean R)", "(a) Mean survivor loss $L_S$\n(score-aligned outcome)"),
              ("disconnected", "(b) Share of connected pairs disconnected\n(not score-aligned outcome)")]
    width = 0.13
    gap = 0.012
    for ax, (col, title) in zip(axes, panels):
        ax.grid(True, axis="y", color=GRID, linewidth=0.5)
        ax.set_axisbelow(True)
        for g, (w, _) in enumerate(waves):
            t = tabs[w]
            for i, (lab, colr) in enumerate(zip(STRATEGY_LABELS, STRATEGY_COLORS)):
                v = float(t.loc[t["strategy"] == lab, col].iloc[0])
                x = g + (i - 2.5) * (width + gap)
                ax.bar(x, v, width=width, color=colr, edgecolor="white", linewidth=0.4, zorder=3)
                if i == 0:
                    ax.text(x, v, f"{v:.3f}", ha="center", va="bottom", fontsize=6.5, color=INK,
                            rotation=90)
        ax.set_xticks(range(len(waves)))
        ax.set_xticklabels([f"{w} wave" for w, _ in waves])
        ax.set_title(title, fontsize=8.5, color=INK, loc="left")
        ax.tick_params(axis="x", length=0)
        ax.margins(y=0.15)
    handles = [plt.Rectangle((0, 0), 1, 1, color=c) for c in STRATEGY_COLORS]
    fig.legend(handles, STRATEGY_LABELS, loc="lower center", ncol=3, frameon=False, fontsize=8,
               bbox_to_anchor=(0.5, -0.1), handlelength=1.2, columnspacing=1.2)
    fig.tight_layout(w_pad=2.0)
    os.makedirs(OUT, exist_ok=True)
    fig.savefig(os.path.join(OUT, "figure3.png"))
    plt.close(fig)


if __name__ == "__main__":
    figure2()
    figure3()
    print("figures written to", OUT)
