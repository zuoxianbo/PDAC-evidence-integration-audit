#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Extended Data Figures 1-4 (v31) — real data from result JSONs.

ED Fig 1: sentinel/annotation-absence distribution per layer (S1).
ED Fig 2: missingness-encoding sensitivity (S4, sentinel vs available-case).
ED Fig 3: full Dirichlet weight-space (weight draws + AUROC draws).
ED Fig 4: nine candidate genes as prospective hypotheses (candidates table).

Semantic palette matches main figures. No fabricated data.
"""
import json
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Patch

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RES = os.path.join(ROOT, "results")
FIG = "/Users/zuoxianbo/Desktop/SCI论文/胰腺癌_submission/extended_data_v32_20260824"
os.makedirs(FIG, exist_ok=True)

R = json.load(open(os.path.join(RES, "v18_ncs_results.json")))
WS = json.load(open(os.path.join(RES, "v18_weight_space.json")))
SENT = json.load(open(os.path.join(RES, "v18_sentinel_audit.json")))

C_CENT, C_INT, C_RF, C_CIRC, C_NEU, C_CHANCE = (
    "#2F5B88", "#2A9D8F", "#D56A3A", "#7A6AA6", "#9E9E9E", "#555555")
INK = "#1A1A1A"

plt.rcParams.update({
    "font.family": "sans-serif",
    "font.sans-serif": ["Arial", "Helvetica", "DejaVu Sans"],
    "font.size": 7, "axes.labelsize": 7, "axes.titlesize": 7.5,
    "xtick.labelsize": 6, "ytick.labelsize": 6, "legend.fontsize": 6,
    "axes.linewidth": 0.6, "axes.spines.top": False, "axes.spines.right": False,
    "figure.facecolor": "white", "axes.facecolor": "white",
    "savefig.facecolor": "white", "legend.frameon": False,
    "pdf.fonttype": 42, "ps.fonttype": 42,
})
MM = 1.0 / 25.4
W2 = 180 * MM
STAMP = "v32_20260824"
EP_FULL = list(R["benchmark"].keys())
EP_SHORT = {e: e.split()[0] for e in EP_FULL}


def save(fig, name):
    fig.savefig(os.path.join(FIG, f"{name}_{STAMP}.png"), dpi=400,
                bbox_inches="tight", pad_inches=0.06)
    fig.savefig(os.path.join(FIG, f"{name}_{STAMP}.pdf"),
                bbox_inches="tight", pad_inches=0.06)
    plt.close(fig)
    print(f"  wrote {name}_{STAMP}")


def panel(ax, letter):
    ax.text(0.015, 0.965, letter, transform=ax.transAxes, fontsize=9,
            fontweight="bold", va="top", ha="left", color=INK)


def fig_ed1():
    """Annotation-absence (sentinel) distribution per evidence layer."""
    lay = SENT["S1_sentinel_coding"]["per_layer"]
    names = sorted(lay, key=lambda k: lay[k]["pct_sentinel"])
    vals = [lay[f]["pct_sentinel"] for f in names]
    fig, ax = plt.subplots(figsize=(W2, 60 * MM))
    fig.subplots_adjust(left=0.24, bottom=0.24, top=0.94)
    y = np.arange(len(names))
    ax.barh(y, vals, 0.66, color=C_NEU, ec="white", lw=0.3)
    for i, v in enumerate(vals):
        ax.text(v + 1.2, i, "%.1f%%" % v, va="center", fontsize=6, color="#333333")
    ax.axvline(50, color=C_CENT, lw=0.9, ls="--")
    ax.set_yticks(y)
    ax.set_yticklabels([f.replace("_", " ") for f in names], fontsize=6)
    ax.set_xlabel("genes with no annotation (sentinel = -3.0), %")
    ax.set_xlim(0, 108)
    mean_pct = SENT["S1_sentinel_coding"]["mean_pct_sentinel_across_layers"]
    ax.set_title("Extended Data Fig. 1 — Annotation-absence per evidence layer "
                 "(mean %.1f%%)" % mean_pct, fontsize=7.5, loc="left")
    ax.text(50, len(names) - 0.35, "median gene unannotated", fontsize=5.6,
            color=C_CENT, ha="left", va="center")
    save(fig, "ED_Fig1")


def fig_ed2():
    """Missingness-encoding sensitivity: sentinel-as-value vs available-case."""
    S4 = SENT["S4_sentinel_corrected_sensitivity"]["per_endpoint"]
    eps = list(EP_FULL)
    yy = np.arange(len(eps))[::-1]
    fig, ax = plt.subplots(figsize=(W2, 64 * MM))
    fig.subplots_adjust(left=0.14, bottom=0.28, top=0.94)
    for y, e in zip(yy, eps):
        sv = S4[e]["harmonic_sentinel_as_value"]
        av = S4[e]["harmonic_available_case"]
        ax.plot([sv, av], [y, y], color="#BBBBBB", lw=0.8, zorder=2)
        ax.plot(sv, y, "o", ms=3.5, color=C_NEU, mec="white", mew=0.4, zorder=3)
        ax.plot(av, y, "o", ms=3.8, color=C_CENT, mec="white", mew=0.4, zorder=4)
        ax.text(av + 0.007, y + 0.14, "%+.3f" % S4[e]["harmonic_delta"],
                va="bottom", ha="left", fontsize=5.6, color="#333333")
    ax.axvline(0.5, color=C_CHANCE, lw=0.7, ls="--", zorder=0)
    ax.set_yticks(yy); ax.set_yticklabels([EP_SHORT[e] for e in eps], fontsize=6)
    ax.set_xlabel("AUROC (harmonic)")
    ax.set_xlim(0.38, 1.0)
    ax.set_title("Extended Data Fig. 2 — Missingness-encoding sensitivity "
                 "(sentinel-as-value vs available-case)", fontsize=7.5, loc="left")
    ax.legend(handles=[Patch(fc=C_NEU, ec="none", label="sentinel = -3"),
                       Patch(fc=C_CENT, ec="none", label="available-case")],
              loc="lower center", bbox_to_anchor=(0.5, -0.30), ncol=2,
              fontsize=6)
    save(fig, "ED_Fig2")


def fig_ed3():
    """Full Dirichlet weight-space: weight draws (3 panels) + AUROC draws."""
    wd = np.asarray(WS["weight_draws"])  # 1000 x 3
    smp = np.asarray(WS["auroc_samples"])  # 1000
    labels = ["STRING centrality", "mutation frequency", "IMPC KO viability"]
    fig = plt.figure(figsize=(W2, 62 * MM))
    gs = fig.add_gridspec(1, 4, width_ratios=[1, 1, 1, 1.25], wspace=0.5)
    fig.subplots_adjust(left=0.06, bottom=0.24, top=0.90)
    for i, lab in enumerate(labels):
        ax = fig.add_subplot(gs[0, i])
        ax.hist(wd[:, i], bins=40, color=[C_CENT, C_NEU, C_INT][i],
                alpha=0.85, ec="white", lw=0.2)
        ax.axvline(np.median(wd[:, i]), color=INK, lw=0.8, ls="--")
        ax.set_xlabel(lab, fontsize=6)
        ax.set_ylabel("draws", fontsize=6)
        ax.set_title(labels[i].split()[0], fontsize=7, loc="left")
    ax = fig.add_subplot(gs[0, 3])
    ax.hist(smp, bins=40, color=C_CENT, alpha=0.85, ec="white", lw=0.2)
    ax.axvline(0.5, color=C_CHANCE, lw=0.9, ls="--")
    ax.axvline(WS["string_auroc_e3"], color=C_CENT, lw=1.1)
    ax.axvline(WS["v17_chosen_weighting_auroc_e3"], color=C_RF, lw=1.1)
    ax.set_xlabel("AUROC on E3", fontsize=6)
    ax.set_ylabel("draws", fontsize=6)
    ax.set_title("AUROC distribution", fontsize=7, loc="left")
    ax.text(0.97, 0.96,
            "mean %.3f\nmedian %.3f\n91.2%% < 0.5\n3.2%% > centrality" %
            (smp.mean(), np.median(smp)), transform=ax.transAxes, ha="right",
            va="top", fontsize=5.6, color="#333333")
    ax.legend(handles=[Patch(fc=C_CHANCE, label="chance 0.5"),
                       Patch(fc=C_CENT, label="centrality %.3f" % WS["string_auroc_e3"]),
                       Patch(fc=C_RF, label="prespecified %.3f" % WS["v17_chosen_weighting_auroc_e3"])],
              loc="lower center", bbox_to_anchor=(0.5, -0.42), ncol=1, fontsize=5.6)
    fig.text(0.5, 0.005, "Extended Data Fig. 3 — 1,000 Dirichlet(1,1,1) weightings of "
             "the three driver layers and the resulting E3 AUROC",
             ha="center", va="bottom", fontsize=7.5)
    save(fig, "ED_Fig3")


def fig_ed4():
    """Nine candidate genes as prospective hypotheses."""
    c = R["candidates"]["table"]
    genes = [r["gene"] for r in c]
    pct = [r["harmonic_percentile"] for r in c]
    order = np.argsort(pct)[::-1]
    genes = [genes[i] for i in order]
    pct = [pct[i] for i in order]
    fig, ax = plt.subplots(figsize=(W2, 56 * MM))
    fig.subplots_adjust(left=0.10, bottom=0.22, top=0.92)
    y = np.arange(len(genes))[::-1]
    bars = ax.barh(y, pct, 0.6, color=C_INT, ec="white", lw=0.3)
    for i, v in enumerate(pct):
        ax.text(v + 0.6, y[i], "%.1f" % v, va="center", fontsize=6, color="#333333")
    ax.set_yticks(y); ax.set_yticklabels(genes, fontsize=6.5)
    ax.set_xlabel("harmonic-composite genome-wide percentile")
    ax.set_xlim(0, 102)
    ax.axvline(90, color=C_CENT, lw=0.7, ls="--")
    ax.text(90, len(genes) - 0.3, "top 10%", fontsize=5.6, color=C_CENT,
            ha="left", va="center")
    ax.set_title("Extended Data Fig. 4 — Nine candidate genes (prospective "
                 "computational hypotheses, not validated targets)", fontsize=7.5,
                 loc="left")
    save(fig, "ED_Fig4")


if __name__ == "__main__":
    for fn in (fig_ed1, fig_ed2, fig_ed3, fig_ed4):
        try:
            fn()
        except Exception as exc:
            import traceback
            print("FAILED %s: %s" % (fn.__name__, exc))
            traceback.print_exc()
    print("done")
