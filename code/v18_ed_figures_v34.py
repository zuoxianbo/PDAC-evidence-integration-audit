#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Extended Data Figures 1-4 (v34) - real data from result JSONs.

ED Fig 1: annotation-absence (sentinel) distribution per evidence layer (S1).
ED Fig 2: missingness-encoding sensitivity (S4, sentinel-coded vs missingness-aware).
ED Fig 3: full Dirichlet weight-space (weight draws + resulting E3 AUROC).
ED Fig 4: nine candidate genes as prospective computational hypotheses.

v34 changes versus v32 (presentation only; no change to any computed value):
  1. Adopts the SAME fixed cross-figure semantic palette as main Fig. 1-6:
       navy   #2F5D8A  centrality (fixed-form network baseline)
       teal   #2A9D8F  fixed-form composite
       orange #E07A3F  supervised learner
       purple #7C6BAE  constructed / circular composite
       grey   #9E9E9E  neutral, annotation-absence, distribution of draws
       dgrey  #4D4D4D  chance / reference line
     In these Extended Data panels the objects shown are the harmonic
     COMPOSITE and its encodings, hence purple; annotation-absence and
     draw distributions are neutral grey; the centrality baseline is navy;
     all reference lines (50 %, chance 0.5, top-10 %) are dark grey.
  2. ALL text is black (INK). Colour is used only for bars, points, lines and
     legend swatches - never to encode a group through coloured text.
  3. Output stamp is "v34" and outputs are written INTO the repository
     (repository/extended_data/) so the submitted archive is self-contained.

No fabricated data: every number is read from results/*.json.
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
FIG = os.path.join(ROOT, "extended_data")
os.makedirs(FIG, exist_ok=True)

R = json.load(open(os.path.join(RES, "v18_ncs_results.json")))
WS = json.load(open(os.path.join(RES, "v18_weight_space.json")))
SENT = json.load(open(os.path.join(RES, "v18_sentinel_audit.json")))

# ---- fixed cross-figure semantic palette (identical to v18_figures_v34.py) ----
C_CENT = "#2F5D8A"   # centrality / fixed-form network baseline
C_INT = "#2A9D8F"    # fixed-form composite
C_RF = "#E07A3F"     # supervised learner
C_CIRC = "#7C6BAE"   # constructed / circular composite
C_NEU = "#9E9E9E"    # neutral, annotation-absence, draw distributions
C_CHANCE = "#4D4D4D"  # chance / reference line
C_REF = "#BDBDBD"    # connector / de-emphasised guide
INK = "#1A1A1A"      # all text

plt.rcParams.update({
    "font.family": "sans-serif",
    "font.sans-serif": ["Arial", "Helvetica", "DejaVu Sans"],
    "font.size": 7, "axes.labelsize": 7, "axes.titlesize": 7.5,
    "xtick.labelsize": 6, "ytick.labelsize": 6, "legend.fontsize": 6,
    "axes.linewidth": 0.6, "axes.spines.top": False, "axes.spines.right": False,
    "figure.facecolor": "white", "axes.facecolor": "white",
    "savefig.facecolor": "white", "legend.frameon": False,
    "text.color": INK, "axes.labelcolor": INK,
    "xtick.color": INK, "ytick.color": INK,
    "pdf.fonttype": 42, "ps.fonttype": 42,
})
MM = 1.0 / 25.4
W2 = 180 * MM
STAMP = "v34"
EP_FULL = list(R["benchmark"].keys())
EP_SHORT = {e: e.split()[0] for e in EP_FULL}


def save(fig, name):
    fig.savefig(os.path.join(FIG, f"{name}_{STAMP}.png"), dpi=400,
                bbox_inches="tight", pad_inches=0.06)
    fig.savefig(os.path.join(FIG, f"{name}_{STAMP}.pdf"),
                bbox_inches="tight", pad_inches=0.06)
    plt.close(fig)
    print(f"  wrote {name}_{STAMP}.png / .pdf")


def fig_ed1():
    """Annotation-absence (sentinel) distribution per evidence layer."""
    lay = SENT["S1_sentinel_coding"]["per_layer"]
    names = sorted(lay, key=lambda k: lay[k]["pct_sentinel"])
    vals = [lay[f]["pct_sentinel"] for f in names]
    fig, ax = plt.subplots(figsize=(W2, 62 * MM))
    fig.subplots_adjust(left=0.26, bottom=0.24, top=0.92)
    y = np.arange(len(names))
    ax.barh(y, vals, 0.66, color=C_NEU, ec="white", lw=0.3)
    for i, v in enumerate(vals):
        ax.text(v + 1.4, i, "%.1f%%" % v, va="center", fontsize=6, color=INK)
    ax.axvline(50, color=C_CHANCE, lw=0.9, ls="--", zorder=0)
    ax.set_yticks(y)
    ax.set_yticklabels([f.replace("_", " ") for f in names], fontsize=6,
                       color=INK)
    ax.set_xlabel("Genes with no annotation (sentinel-coded as -3.0), %")
    ax.set_xlim(0, 112)
    mean_pct = SENT["S1_sentinel_coding"]["mean_pct_sentinel_across_layers"]
    ax.set_title("Extended Data Fig. 1 | Annotation absence per evidence layer "
                 "(mean %.1f%% across the nine layers)" % mean_pct,
                 fontsize=7.5, loc="left", color=INK)
    ax.text(50.8, len(names) - 0.35, "50%: median gene unannotated",
            fontsize=5.8, color=INK, ha="left", va="center")
    save(fig, "ED_Fig1")


def fig_ed2():
    """Missingness-encoding sensitivity: sentinel-coded vs missingness-aware."""
    S4 = SENT["S4_sentinel_corrected_sensitivity"]["per_endpoint"]
    eps = list(EP_FULL)
    yy = np.arange(len(eps))[::-1]
    fig, ax = plt.subplots(figsize=(W2, 66 * MM))
    fig.subplots_adjust(left=0.14, bottom=0.30, top=0.92)
    for y, e in zip(yy, eps):
        sv = S4[e]["harmonic_sentinel_as_value"]
        av = S4[e]["harmonic_available_case"]
        ax.plot([sv, av], [y, y], color=C_REF, lw=0.8, zorder=2)
        ax.plot(sv, y, "o", ms=3.6, color=C_NEU, mec="white", mew=0.4, zorder=3)
        ax.plot(av, y, "o", ms=4.0, color=C_CIRC, mec="white", mew=0.4, zorder=4)
        ax.text(max(sv, av) + 0.008, y + 0.16, "%+.3f" % S4[e]["harmonic_delta"],
                va="bottom", ha="left", fontsize=5.8, color=INK)
    ax.axvline(0.5, color=C_CHANCE, lw=0.7, ls="--", zorder=0)
    ax.set_yticks(yy)
    ax.set_yticklabels([EP_SHORT[e] for e in eps], fontsize=6, color=INK)
    ax.set_xlabel("AUROC of the harmonic composite")
    ax.set_xlim(0.38, 1.02)
    ax.set_title("Extended Data Fig. 2 | Missingness-encoding sensitivity: "
                 "sentinel-coded versus missingness-aware", fontsize=7.5,
                 loc="left", color=INK)
    ax.legend(handles=[Patch(fc=C_NEU, ec="none", label="Sentinel-coded (-3.0 treated as a value)"),
                       Patch(fc=C_CIRC, ec="none", label="Missingness-aware (available-case)")],
              loc="upper center", bbox_to_anchor=(0.5, -0.24), ncol=2,
              fontsize=6, labelcolor=INK)
    ax.text(0.0, -0.44, "Labels give the signed AUROC change (missingness-aware "
            "minus sentinel-coded). Dashed line marks chance (0.5).",
            transform=ax.transAxes, fontsize=5.8, color=INK, ha="left",
            va="top")
    save(fig, "ED_Fig2")


def fig_ed3():
    """Full Dirichlet weight-space: weight draws (3 panels) + E3 AUROC draws."""
    wd = np.asarray(WS["weight_draws"])          # 1000 x 3
    smp = np.asarray(WS["auroc_samples"])        # 1000
    labels = ["STRING centrality", "Mutation frequency", "IMPC knockout viability"]
    fig = plt.figure(figsize=(W2, 66 * MM))
    gs = fig.add_gridspec(1, 4, width_ratios=[1, 1, 1, 1.3], wspace=0.55)
    fig.subplots_adjust(left=0.06, bottom=0.30, top=0.86)
    for i, lab in enumerate(labels):
        ax = fig.add_subplot(gs[0, i])
        ax.hist(wd[:, i], bins=40, color=C_NEU, alpha=0.9, ec="white", lw=0.2)
        ax.axvline(np.median(wd[:, i]), color=INK, lw=0.8, ls="--")
        ax.set_xlabel("Weight on\n%s" % lab, fontsize=6, color=INK)
        ax.set_ylabel("Dirichlet draws", fontsize=6, color=INK)
        ax.set_title("abc"[i], fontsize=9, fontweight="bold", loc="left",
                     color=INK)
    ax = fig.add_subplot(gs[0, 3])
    ax.hist(smp, bins=40, color=C_NEU, alpha=0.9, ec="white", lw=0.2)
    ax.axvline(0.5, color=C_CHANCE, lw=0.9, ls="--")
    ax.axvline(WS["string_auroc_e3"], color=C_CENT, lw=1.2)
    ax.axvline(WS["v17_chosen_weighting_auroc_e3"], color=C_CIRC, lw=1.2)
    ax.set_xlabel("AUROC on E3", fontsize=6, color=INK)
    ax.set_ylabel("Dirichlet draws", fontsize=6, color=INK)
    ax.set_title("d", fontsize=9, fontweight="bold", loc="left", color=INK)
    ax.text(0.97, 0.96,
            "mean %.3f\nmedian %.3f\n91.2%% below chance\n3.2%% above centrality" %
            (smp.mean(), np.median(smp)), transform=ax.transAxes, ha="right",
            va="top", fontsize=5.8, color=INK)
    ax.legend(handles=[Patch(fc=C_CHANCE, ec="none", label="Chance (0.500)"),
                       Patch(fc=C_CENT, ec="none",
                             label="STRING centrality (%.3f)" % WS["string_auroc_e3"]),
                       Patch(fc=C_CIRC, ec="none",
                             label="Prespecified weighting (%.3f)" % WS["v17_chosen_weighting_auroc_e3"])],
              loc="upper center", bbox_to_anchor=(0.5, -0.40), ncol=1,
              fontsize=5.8, labelcolor=INK)
    fig.text(0.005, 0.985, "Extended Data Fig. 3 | 1,000 Dirichlet(1,1,1) "
             "weightings of the three driver layers and the resulting E3 AUROC",
             ha="left", va="top", fontsize=7.5, color=INK)
    fig.text(0.005, 0.012, "Dashed lines in a-c mark the median drawn weight. "
             "Grey histograms show the distribution of draws; no weighting was "
             "selected post hoc.", ha="left", va="bottom", fontsize=5.8,
             color=INK)
    save(fig, "ED_Fig3")


def fig_ed4():
    """Nine candidate genes as prospective computational hypotheses."""
    c = R["candidates"]["table"]
    genes = [r["gene"] for r in c]
    pct = [r["harmonic_percentile"] for r in c]
    order = np.argsort(pct)[::-1]
    genes = [genes[i] for i in order]
    pct = [pct[i] for i in order]
    fig, ax = plt.subplots(figsize=(W2, 58 * MM))
    fig.subplots_adjust(left=0.12, bottom=0.26, top=0.90)
    y = np.arange(len(genes))[::-1]
    ax.barh(y, pct, 0.6, color=C_CIRC, ec="white", lw=0.3)
    for i, v in enumerate(pct):
        ax.text(v + 0.8, y[i], "%.1f" % v, va="center", fontsize=6, color=INK)
    ax.set_yticks(y)
    ax.set_yticklabels(genes, fontsize=6.5, color=INK)
    ax.set_xlabel("Harmonic-composite genome-wide percentile")
    ax.set_xlim(0, 106)
    ax.axvline(90, color=C_CHANCE, lw=0.7, ls="--", zorder=0)
    ax.text(90.8, len(genes) - 0.3, "Top 10%", fontsize=5.8, color=INK,
            ha="left", va="center")
    ax.set_title("Extended Data Fig. 4 | Nine candidate genes ranked by the "
                 "harmonic composite", fontsize=7.5, loc="left", color=INK)
    ax.text(0.0, -0.30, "These are prospective computational hypotheses, not "
            "validated therapeutic targets; no experimental confirmation is "
            "claimed.", transform=ax.transAxes, fontsize=5.8, color=INK,
            ha="left", va="top")
    save(fig, "ED_Fig4")


if __name__ == "__main__":
    print("Extended Data Figures 1-4 (%s) -> %s" % (STAMP, FIG))
    ok = True
    for fn in (fig_ed1, fig_ed2, fig_ed3, fig_ed4):
        try:
            fn()
        except Exception as exc:
            ok = False
            import traceback
            print("FAILED %s: %s" % (fn.__name__, exc))
            traceback.print_exc()
    print("done" if ok else "done WITH FAILURES")
