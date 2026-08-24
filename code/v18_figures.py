#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""V18 display items (6) for Nature Computational Science Analysis.

Reads results/v18_ncs_results.json produced by v18_recompute.py and renders
Fig. 1-6 under the NCS-compliant visual system:
  baseline / single layer   #1F4E79  deep navy
  integration / harmonic    #2A9D8F  teal
  supervised (random forest)#E76F51  orange
  control / null            #A6A6A6  neutral grey
  cross-context / transfer  #6C63A8  deep violet
No red-green contrasts, no rainbow, no gradients, no 3-D, light background only.
Arial 5-7 pt, >=300 dpi, RGB, vector PDF alongside every PNG.
"""
import json
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import LinearSegmentedColormap, TwoSlopeNorm
from matplotlib.patches import Patch, Rectangle

OUT = "/Users/zuoxianbo/Desktop/SCI论文/胰腺癌"
RES = os.path.join(OUT, "results")
FIG = os.path.join(OUT, "figures")
os.makedirs(FIG, exist_ok=True)
R = json.load(open(os.path.join(RES, "v18_ncs_results.json")))

C_BASE, C_INT, C_RF, C_NULL, C_XCTX = "#1F4E79", "#2A9D8F", "#E76F51", "#A6A6A6", "#6C63A8"
CMAP = LinearSegmentedColormap.from_list("ncs", ["#A6A6A6", "#FFFFFF", C_INT])

plt.rcParams.update({
    "font.family": "sans-serif",
    "font.sans-serif": ["Arial", "Helvetica", "DejaVu Sans"],
    "font.size": 6, "axes.labelsize": 6.5, "axes.titlesize": 7,
    "xtick.labelsize": 5.5, "ytick.labelsize": 5.5, "legend.fontsize": 5.5,
    "axes.linewidth": 0.5, "xtick.major.width": 0.5, "ytick.major.width": 0.5,
    "xtick.major.size": 2, "ytick.major.size": 2,
    "axes.spines.top": False, "axes.spines.right": False,
    "figure.facecolor": "white", "axes.facecolor": "white",
    "savefig.facecolor": "white", "legend.frameon": False,
    "pdf.fonttype": 42, "ps.fonttype": 42, "svg.fonttype": "none",
})
MM = 1.0 / 25.4
W1, W2 = 88 * MM, 180 * MM          # NCS single / double column


def save(fig, name):
    for ext in ("png", "pdf"):
        fig.savefig(os.path.join(FIG, f"{name}.{ext}"), dpi=400,
                    bbox_inches="tight", pad_inches=0.06)
    plt.close(fig)
    print(f"  wrote {name}.png / .pdf")


def panel(ax, letter, dx=-0.16, dy=1.06):
    ax.text(dx, dy, letter, transform=ax.transAxes, fontsize=8,
            fontweight="bold", va="top", ha="left")


EP_FULL = [k for k in R["benchmark"].keys()]
EP_SHORT = {k: k.split()[0] for k in EP_FULL}
B = R["benchmark"]


# =====================================================================
# Fig. 1 | Single evidence layers and the dependency structure of endpoints
# =====================================================================
def fig1():
    layers = ["STRING centrality", "Druggability", "Mutation frequency",
              "Genetic constraint", "Cancer-driver annotation"]
    eps = ["E1 pan-dependency", "E3 conjunctive actionability",
           "E5 historical clinical-target concordance"]
    fig = plt.figure(figsize=(W2, 62 * MM))
    gs = fig.add_gridspec(1, 2, width_ratios=[1.45, 1.0], wspace=0.30)

    ax = fig.add_subplot(gs[0, 0])
    n_l, n_e = len(layers), len(eps)
    off = np.linspace(-0.26, 0.26, n_e)
    cols = [C_BASE, C_INT, C_XCTX]
    for j, ep in enumerate(eps):
        for i, lay in enumerate(layers):
            v = B[ep].get(lay)
            if v is None:
                continue
            y = (n_l - 1 - i) + off[j]
            lo, hi = v["auroc_ci"]
            ax.plot([lo, hi], [y, y], color=cols[j], lw=0.9, solid_capstyle="butt")
            ax.plot(v["auroc"], y, "o", ms=2.8, color=cols[j],
                    mec="white", mew=0.35, zorder=3)
    ax.axvline(0.5, color=C_NULL, lw=0.7, ls="--", zorder=0)
    ax.set_yticks(range(n_l))
    ax.set_yticklabels([l.replace(" annotation", "") for l in layers[::-1]])
    ax.set_xlabel("AUROC (95% CI, 2,000 bootstrap resamples)")
    ax.set_xlim(0.40, 1.02)
    ax.text(0.5, -0.055, "chance", transform=ax.get_xaxis_transform(),
            ha="center", va="top", fontsize=5, color="#666666")
    ax.legend(handles=[Patch(fc=c, ec="none", label=EP_SHORT[e] + " · " +
                             " ".join(e.split()[1:3]))
                       for c, e in zip(cols, eps)],
              loc="upper center", bbox_to_anchor=(0.5, -0.20), ncol=3,
              handlelength=1.1, columnspacing=1.1)
    panel(ax, "a", dx=-0.30)

    ax2 = fig.add_subplot(gs[0, 1])
    ax2.set_xlim(0, 10); ax2.set_ylim(0, 10); ax2.axis("off")
    ax2.add_patch(Rectangle((0.5, 1.3), 8.0, 7.0, fc="#F4F4F4", ec=C_BASE, lw=0.7))
    ax2.text(4.5, 8.55, "E1 pan-dependency  (n = %d)" % B["E1 pan-dependency"]
             ["STRING centrality"]["n_pos"], ha="center", fontsize=6, color=C_BASE)
    ax2.add_patch(Rectangle((1.0, 4.9), 3.4, 3.0, fc="#FFFFFF", ec=C_XCTX, lw=0.7))
    ax2.text(2.7, 7.6, "E2 PDAC-enriched", ha="center", fontsize=5.5, color=C_XCTX)
    ax2.text(2.7, 6.9, "top quartile of E1\n(n = %d)" %
             B["E2 PDAC-enriched dependency"]["STRING centrality"]["n_pos"],
             ha="center", va="center", fontsize=5, color="#444444")
    ax2.add_patch(Rectangle((4.8, 4.9), 3.3, 3.0, fc="#FFFFFF", ec=C_INT, lw=0.7))
    ax2.text(6.45, 7.6, "E3 conjunctive", ha="center", fontsize=5.5, color=C_INT)
    ax2.text(6.45, 6.9, "E1 $\\cap$ druggable\n(n = %d)" %
             B["E3 conjunctive actionability"]["STRING centrality"]["n_pos"],
             ha="center", va="center", fontsize=5, color="#444444")
    ax2.add_patch(Rectangle((1.0, 1.8), 7.1, 2.4, fc="#FFFFFF", ec=C_BASE,
                            lw=0.7, ls=(0, (2, 1.4))))
    ax2.text(4.55, 3.85, "E3-A leakage-controlled  $\\equiv$  E1", ha="center",
             fontsize=5.5, color=C_BASE)
    ax2.text(4.55, 2.75, "removing the druggability conjunct returns the\n"
             "E1 positive set exactly; not an independent endpoint",
             ha="center", va="center", fontsize=5, color="#444444")
    for x0, lab, sub, col in ((0.5, "E3-C", "label = input\nlayer (leakage)", C_NULL),
                              (3.7, "E4 CRC", "cross-context\ntransfer", C_XCTX),
                              (6.9, "E5 / E6", "clinical history /\nGDSC response", C_INT)):
        ax2.add_patch(Rectangle((x0, -0.9), 2.6, 1.7, fc="#FFFFFF", ec=col, lw=0.7))
        ax2.text(x0 + 1.3, 0.45, lab, ha="center", fontsize=5.5, color=col)
        ax2.text(x0 + 1.3, -0.25, sub, ha="center", va="center", fontsize=4.8,
                 color="#444444")
    ax2.text(4.5, 9.6, "Endpoint dependency structure", ha="center", fontsize=6.5)
    ax2.text(4.5, -1.55, "grey = external to the evidence base;  dashed = identical to E1",
             ha="center", fontsize=4.8, color="#666666")
    ax2.set_ylim(-2.0, 10)
    panel(ax2, "b", dx=-0.02, dy=1.02)
    save(fig, "Fig1")


# =====================================================================
# Fig. 2 | Benchmark matrix, 13 scorers x 8 endpoints
# =====================================================================
def fig2():
    order = ["Mutation frequency", "Genetic constraint", "Cancer-driver annotation",
             "Druggability", "STRING centrality", "Arithmetic mean",
             "Rank aggregation", "Weighted rank aggregation",
             "ECS (multiplicative)", "Harmonic mean",
             "Logistic regression", "Elastic net", "Random forest"]
    meths = [m for m in order if any(m in B[e] for e in EP_FULL)]
    M = np.full((len(meths), len(EP_FULL)), np.nan)
    for i, m in enumerate(meths):
        for j, e in enumerate(EP_FULL):
            if m in B[e]:
                M[i, j] = B[e][m]["auroc"]
    fig, ax = plt.subplots(figsize=(W2, 78 * MM))
    norm = TwoSlopeNorm(vmin=0.35, vcenter=0.5, vmax=1.0)
    im = ax.imshow(M, cmap=CMAP, norm=norm, aspect="auto")
    for i in range(len(meths)):
        for j in range(len(EP_FULL)):
            if np.isnan(M[i, j]):
                ax.text(j, i, "n.a.", ha="center", va="center", fontsize=4.6,
                        color="#888888")
                continue
            leak = (EP_FULL[j].startswith("E3-C") and M[i, j] > 0.999)
            ax.text(j, i, ("%.2f" % M[i, j]).lstrip("0"), ha="center", va="center",
                    fontsize=4.9, color="white" if M[i, j] > 0.80 else "#1A1A1A",
                    fontweight="bold" if leak else "normal")
            if leak:
                ax.add_patch(Rectangle((j - .5, i - .5), 1, 1, fill=False,
                                       ec="#1A1A1A", lw=0.8, ls=(0, (1.4, 1.0))))
    ax.set_xticks(range(len(EP_FULL)))
    ax.set_xticklabels([EP_SHORT[e] for e in EP_FULL])
    ax.set_yticks(range(len(meths)))
    ax.set_yticklabels(meths)
    ax.set_xlabel("Validation endpoint")
    for i, m in enumerate(meths):
        if m in ("ECS (multiplicative)", "Harmonic mean"):
            ax.get_yticklabels()[i].set_color(C_INT)
        elif m == "STRING centrality":
            ax.get_yticklabels()[i].set_color(C_BASE)
        elif m in ("Logistic regression", "Elastic net", "Random forest"):
            ax.get_yticklabels()[i].set_color(C_RF)
    ax.set_xticks(np.arange(-.5, len(EP_FULL), 1), minor=True)
    ax.set_yticks(np.arange(-.5, len(meths), 1), minor=True)
    ax.grid(which="minor", color="white", lw=0.6)
    ax.tick_params(which="minor", length=0)
    cb = fig.colorbar(im, ax=ax, fraction=0.022, pad=0.015,
                      ticks=[0.4, 0.5, 0.7, 0.9, 1.0])
    cb.set_label("AUROC", fontsize=6)
    cb.ax.tick_params(labelsize=5)
    cb.outline.set_linewidth(0.4)
    ax.text(0.0, -0.155, "dashed cells, AUROC = 1.000 on E3-C: the label is itself an "
            "input layer (circular by construction)", transform=ax.transAxes,
            fontsize=5, color="#555555")
    save(fig, "Fig2")


# =====================================================================
# Fig. 3 | Integration confers no intrinsic advantage over the best single layer
# =====================================================================
def fig3():
    D = R["delta_auroc_paired_bootstrap"]
    L = R["delong_pairwise"]
    keys = [("Harmonic mean - STRING centrality", "Harmonic mean", C_INT),
            ("ECS (multiplicative) - STRING centrality", "ECS (multiplicative)", C_INT),
            ("Random forest - STRING centrality", "Random forest", C_RF)]
    fig = plt.figure(figsize=(W2, 66 * MM))
    gs = fig.add_gridspec(1, 3, width_ratios=[1.35, 1.0, 0.85], wspace=0.42)

    ax = fig.add_subplot(gs[0, 0])
    ep_plot = [e for e in EP_FULL if not e.startswith("E3-A")]
    yy, ylab = [], []
    for i, e in enumerate(ep_plot[::-1]):
        base = i * 1.0
        for k, (key, lab, col) in enumerate(keys):
            d = D.get(e, {}).get(key)
            if not d:
                continue
            y = base + (k - 1) * 0.235
            dm = d.get("delta_mean", d.get("delta"))
            ax.plot([d["ci_lo"], d["ci_hi"]], [y, y], color=col, lw=0.9)
            ax.plot(dm, y, "o", ms=2.8, color=col, mec="white", mew=0.35,
                    zorder=3)
            if d["ci_lo"] > 0 or d["ci_hi"] < 0:
                ax.plot(dm, y + 0.115, marker="*", ms=2.6, color="#1A1A1A",
                        zorder=4)
        yy.append(base); ylab.append(EP_SHORT[e])
    ax.axvline(0, color="#1A1A1A", lw=0.7)
    ax.set_yticks(yy); ax.set_yticklabels(ylab)
    ax.set_xlabel("$\\Delta$AUROC vs STRING centrality\n(paired bootstrap, 95% CI)")
    ax.legend(handles=[Patch(fc=c, ec="none", label=l) for _, l, c in keys],
              loc="upper center", bbox_to_anchor=(0.5, -0.24), ncol=2,
              handlelength=1.1, columnspacing=1.0)
    ax.text(1.0, 1.02, "$\\star$  CI excludes 0", transform=ax.transAxes,
            ha="right", fontsize=5, color="#444444")
    panel(ax, "a", dx=-0.24)

    ax = fig.add_subplot(gs[0, 1])
    rows = []
    for e in ep_plot:
        for key, lab, col in keys:
            r = L.get(e, {}).get(key.replace(" - ", " vs "))
            if r:
                rows.append((EP_SHORT[e], lab, max(r["p"], 1e-300), col))
    for i, (e, lab, p, col) in enumerate(rows):
        ax.plot([1.0, p], [i, i], color=col, lw=0.7, alpha=0.55)
        ax.plot(p, i, "o", ms=2.6, color=col, mec="white", mew=0.3, zorder=3)
    ax.axvline(0.05, color=C_NULL, lw=0.7, ls="--")
    ax.set_xscale("log")
    ax.set_yticks(range(len(rows)))
    ax.set_yticklabels(["%s · %s" % (e, l.split()[0]) for e, l, _, _ in rows],
                       fontsize=4.7)
    ax.set_xlabel("DeLong $P$ vs STRING centrality")
    ax.invert_yaxis()
    ax.text(0.05, 1.02, "$P$ = 0.05", transform=ax.get_xaxis_transform(),
            ha="center", fontsize=5, color="#666666")
    panel(ax, "b", dx=-0.62)

    ax = fig.add_subplot(gs[0, 2])
    S = R["structured_resampling"]
    ax.axhline(0, color="#1A1A1A", lw=0.7)
    ax.plot([0, 0], [S["delta_ci_lo"], S["delta_ci_hi"]], color=C_INT, lw=1.4)
    ax.plot(0, S["delta_mean"], "o", ms=4.0, color=C_INT, mec="white", mew=0.4)
    W = R["weight_sensitivity"]
    ax.set_xlim(-1.1, 1.1); ax.set_xticks([0])
    ax.set_xticklabels(["community\nbootstrap"], fontsize=5)
    ax.set_ylabel("$\\Delta$AUROC, ECS $-$ STRING")
    ax.text(0.06, 0.03, "%d STRING-centrality communities\n%d resamples · %.0f%% > 0"
            % (S["n_communities"], S["n_bootstrap"], S["pct_positive"]),
            transform=ax.transAxes, fontsize=4.8, color="#444444", va="bottom")
    panel(ax, "c", dx=-0.52)
    save(fig, "Fig3")


SENT = json.load(open(os.path.join(RES, "v18_sentinel_audit.json")))
WS = json.load(open(os.path.join(RES, "v18_weight_space.json")))


# =====================================================================
# Fig. 4 | Why integration appears to work
# =====================================================================
def fig4():
    fig = plt.figure(figsize=(W2, 72 * MM))
    gs = fig.add_gridspec(1, 3, width_ratios=[1.15, 0.95, 1.25], wspace=0.44)

    # (a) how much of the evidence base is actually annotation absence
    ax = fig.add_subplot(gs[0, 0])
    lay = SENT["S1_sentinel_coding"]["per_layer"]
    names = sorted(lay, key=lambda k: lay[k]["pct_sentinel"])
    pos = np.arange(len(names))
    for i, f in enumerate(names):
        v = lay[f]["pct_sentinel"]
        ax.barh(i, v, 0.66, color=C_NULL if v >= 50 else "#C9D6DF",
                ec="white", lw=0.3)
        ax.text(v + 1.4, i, "%.0f%%" % v, va="center", fontsize=4.9,
                color="#333333")
    ax.axvline(50, color=C_BASE, lw=0.7, ls="--")
    ax.set_yticks(pos)
    ax.set_yticklabels([f.replace("_", " ") for f in names], fontsize=5)
    ax.set_xlabel("genes with no annotation (%)")
    ax.set_xlim(0, 112)
    ax.text(50, len(names) - 0.35, "median gene\nunannotated", fontsize=4.6,
            color=C_BASE, ha="left", va="center")
    panel(ax, "a", dx=-0.52)

    # (b) the multiplicative rule is not order preserving
    ax = fig.add_subplot(gs[0, 1])
    s2 = SENT["S2_order_preservation"]
    bars = [("(1 + 0.6$\\Phi$) < 0", s2["pct_genes_gain_term_negative"]),
            ("$D$ < 0", s2["pct_genes_driver_negative"]),
            ("double sign flip", s2["pct_genes_double_sign_flip"]),
            ("score falls when\nsupport increases",
             s2["pct_genes_whose_score_FALLS_when_support_increases"])]
    for i, (lab, v) in enumerate(bars):
        ax.bar(i, v, 0.64, color=C_NULL if i < 3 else C_RF, ec="white", lw=0.3)
        ax.text(i, v + 1.6, "%.0f%%" % v, ha="center", fontsize=5)
    ax.set_xticks(range(len(bars)))
    ax.set_xticklabels([b[0] for b in bars], fontsize=4.6)
    ax.set_ylabel("genes affected (%)")
    ax.set_ylim(0, 100)
    ax.text(0.02, 0.97, "corr($\\Phi$, ECS)\n  $D>0$: %+.2f\n  $D<0$: %+.2f"
            % (s2["corr_PHI_score_when_D_positive"],
               s2["corr_PHI_score_when_D_negative"]),
            transform=ax.transAxes, va="top", fontsize=4.8, color="#333333")
    panel(ax, "b", dx=-0.34)

    # (c) the integrated score is the support mean, and its signal is the label
    ax = fig.add_subplot(gs[0, 2])
    rows = SENT["S3_endpointwise"]
    eps = [e for e in EP_FULL if not e.startswith("E3-A")]
    x = np.arange(len(eps)); w = 0.27
    for k, (key, lab, col) in enumerate(
            (("harmonic", "harmonic (integrated)", C_INT),
             ("support_mean_PHI", "support-layer mean $\\Phi$", "#7FC8BF"),
             ("support_mean_without_druggability",
              "$\\Phi$ minus druggability", C_NULL))):
        ax.bar(x + (k - 1) * w, [rows[e][key] for e in eps], w, color=col,
               ec="white", lw=0.25, label=lab)
    ax.plot(x, [rows[e]["string_alone"] for e in eps], "_", ms=9, mew=1.1,
            color=C_BASE, label="STRING centrality alone")
    ax.axhline(0.5, color="#1A1A1A", lw=0.6, ls="--")
    ax.set_xticks(x); ax.set_xticklabels([EP_SHORT[e] for e in eps])
    ax.set_ylim(0.42, 1.02); ax.set_ylabel("AUROC")
    ax.set_xlabel("Validation endpoint")
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.235), ncol=2,
              handlelength=1.0, columnspacing=1.0, fontsize=5)
    ax.annotate("", xy=(2 + w, rows[eps[2]]["support_mean_without_druggability"]),
                xytext=(2, rows[eps[2]]["support_mean_PHI"]),
                arrowprops=dict(arrowstyle="->", lw=0.6, color="#1A1A1A"))
    ax.text(2 + 0.36, 0.70, "removing the\nlabel's own layer:\n%.3f $\\to$ %.3f"
            % (rows[eps[2]]["support_mean_PHI"],
               rows[eps[2]]["support_mean_without_druggability"]),
            fontsize=4.7, color="#1A1A1A", ha="left", va="center")
    panel(ax, "c", dx=-0.14)
    save(fig, "Fig4")


# =====================================================================
# Fig. 5 | Sensitivity: functional form, weight space, controls, recoding
# =====================================================================
def fig5():
    F = R["functional_forms_all_endpoints"]
    forms = ["harmonic mean", "additive", "multiplicative (ECS)",
             "geometric mean", "rank aggregation"]
    shades = [C_INT, "#54B3A7", "#7FC8BF", "#A9DBD5", C_BASE]
    eps = [e for e in EP_FULL if not e.startswith("E3-A")]
    fig = plt.figure(figsize=(W2, 74 * MM))
    gs = fig.add_gridspec(1, 4, width_ratios=[1.5, 1.05, 0.85, 0.95], wspace=0.46)

    ax = fig.add_subplot(gs[0, 0])
    x = np.arange(len(eps)); w = 0.155
    for k, (f, c) in enumerate(zip(forms, shades)):
        ax.bar(x + (k - 2) * w, [F.get(e, {}).get(f, {}).get("auroc", np.nan)
                                 for e in eps], w, color=c, ec="white", lw=0.25,
               label=f)
    ax.axhline(0.5, color="#1A1A1A", lw=0.6, ls="--")
    ax.set_xticks(x); ax.set_xticklabels([EP_SHORT[e] for e in eps])
    ax.set_ylabel("AUROC"); ax.set_ylim(0.30, 1.02)
    ax.set_xlabel("Validation endpoint")
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.235), ncol=3,
              handlelength=1.0, columnspacing=0.9, fontsize=5)
    panel(ax, "a", dx=-0.14)

    ax = fig.add_subplot(gs[0, 1])
    smp = np.asarray(WS["auroc_samples"])
    ax.hist(smp, bins=40, color="#D3DEE6", ec="white", lw=0.25)
    ax.axvline(0.5, color="#1A1A1A", lw=0.8, ls="--", zorder=3)
    ax.axvline(WS["string_auroc_e3"], color=C_BASE, lw=1.0, zorder=3)
    ax.axvline(WS["v17_chosen_weighting_auroc_e3"], color=C_RF, lw=1.0, zorder=3)
    ax.set_xlabel("AUROC on E3 over %s Dirichlet\nweightings of the driver layers"
                  % format(WS["n_draws"], ","))
    ax.set_ylabel("draws")
    ax.text(0.02, 0.97, "mean %.3f\n%.1f%% below chance\n%.1f%% beat STRING"
            % (WS["mean"], WS["pct_below_chance"], WS["pct_above_string"]),
            transform=ax.transAxes, va="top", fontsize=4.8, color="#333333")
    ax.legend(handles=[Patch(fc=C_BASE, label="STRING alone %.3f"
                             % WS["string_auroc_e3"]),
                       Patch(fc=C_RF, label="chosen weighting %.3f"
                             % WS["v17_chosen_weighting_auroc_e3"]),
                       Patch(fc=C_NULL, label="chance")],
              loc="upper center", bbox_to_anchor=(0.5, -0.235), ncol=1,
              handlelength=1.0, fontsize=4.8)
    panel(ax, "b", dx=-0.34)

    ax = fig.add_subplot(gs[0, 2])
    C = R["negative_controls"]
    labs = [("ecs_observed", "observed", C_INT),
            ("random_gaussian_layer", "Gaussian\nlayer", C_NULL),
            ("shuffled_network", "shuffled\nnetwork", C_NULL),
            ("permuted_druggability", "permuted\ndruggability", C_NULL)]
    for i, (k, lab, col) in enumerate(labs):
        v = C[k]
        ax.bar(i, v["auroc"], 0.62, color=col, ec="white", lw=0.3)
        ax.plot([i, i], v["auroc_ci"], color="#1A1A1A", lw=0.6)
        ax.text(i, v["auroc_ci"][1] + 0.011, "%.3f" % v["auroc"], ha="center",
                fontsize=4.7)
    ax.axhline(0.5, color="#1A1A1A", lw=0.6, ls="--")
    ax.axhline(C["ecs_observed"]["auroc"], color=C_INT, lw=0.55, ls=":", zorder=0)
    ax.set_xticks(range(len(labs)))
    ax.set_xticklabels([l for _, l, _ in labs], fontsize=4.6)
    ax.set_ylabel("AUROC on E3")
    ax.set_ylim(0.40, max(v["auroc_ci"][1] for v in C.values()) + 0.05)
    panel(ax, "c", dx=-0.46)

    ax = fig.add_subplot(gs[0, 3])
    S4 = SENT["S4_sentinel_corrected_sensitivity"]["per_endpoint"]
    eps2 = [e for e in EP_FULL if not e.startswith("E3-A")]
    d = [S4[e]["harmonic_delta"] for e in eps2]
    yy = np.arange(len(eps2))[::-1]
    for y, e, v in zip(yy, eps2, d):
        ax.barh(y, v, 0.6, color=C_XCTX if v > 0 else C_NULL, ec="white", lw=0.3)
        ax.text(v + (0.004 if v > 0 else -0.004), y, "%+.3f" % v,
                va="center", ha="left" if v > 0 else "right", fontsize=4.6)
    ax.axvline(0, color="#1A1A1A", lw=0.7)
    ax.set_yticks(yy); ax.set_yticklabels([EP_SHORT[e] for e in eps2], fontsize=5)
    ax.set_xlabel("$\\Delta$AUROC when the missing-data\nsentinel is recoded as missing")
    ax.set_xlim(-0.075, 0.075)
    panel(ax, "d", dx=-0.46)
    save(fig, "Fig5")


# =====================================================================
# Fig. 6 | Prospective candidates and an orthogonal drug-response endpoint
# =====================================================================
def fig6():
    CD = R["candidates"]
    tab = CD["table"]
    fig = plt.figure(figsize=(W2, 76 * MM))
    gs = fig.add_gridspec(1, 3, width_ratios=[0.85, 1.35, 1.0], wspace=0.55)

    ax = fig.add_subplot(gs[0, 0])
    n = len(tab)
    for r in tab:
        y0, y1 = n - r["rank_v17_as_printed"], n - r["rank_v18"]
        moved = r["rank_v17_as_printed"] != r["rank_v18"]
        ax.plot([0, 1], [y0, y1], color=C_RF if moved else C_NULL,
                lw=0.8 if moved else 0.5, alpha=0.9 if moved else 0.55,
                zorder=2 if moved else 1)
        ax.plot(0, y0, "o", ms=2.4, color=C_NULL, mec="white", mew=0.3, zorder=3)
        ax.plot(1, y1, "o", ms=2.4, color=C_INT, mec="white", mew=0.3, zorder=3)
        ax.text(-0.07, y0, r["gene"], ha="right", va="center", fontsize=4.8)
        ax.text(1.07, y1, r["gene"], ha="left", va="center", fontsize=4.8,
                color=C_RF if moved else "#333333")
    ax.set_xlim(-0.62, 1.62); ax.set_ylim(-0.6, n - 0.4)
    ax.set_xticks([0, 1])
    ax.set_xticklabels(["as printed\nin V17", "recomputed\nharmonic rank"],
                       fontsize=5)
    ax.set_yticks([]); ax.spines["left"].set_visible(False)
    ax.spines["bottom"].set_visible(False)
    ax.tick_params(length=0)
    panel(ax, "a", dx=-0.32)

    ax = fig.add_subplot(gs[0, 1])
    order = sorted(tab, key=lambda r: r["harmonic_percentile"])
    yy = np.arange(len(order))
    for i, r in enumerate(order):
        ax.plot([0, r["harmonic_percentile"]], [i, i], color=C_NULL, lw=0.5,
                zorder=1)
        ax.plot(r["harmonic_percentile"], i, "o", ms=3.2, color=C_INT,
                mec="white", mew=0.35, zorder=3)
    ax.set_yticks(yy)
    ax.set_yticklabels([r["gene"] for r in order], fontsize=5)
    ax.set_xlabel("genome-wide percentile of the harmonic score")
    ax.set_xlim(0, 104)
    for i, r in enumerate(order):
        flags = ("D" if r["druggable"] else "-") + \
                ("E" if r["pdac_essential"] else "-") + \
                ("C" if r["crc_essential"] else "-")
        ax.text(102, i, flags, va="center", ha="right", fontsize=4.6,
                family="monospace", color="#333333")
    ax.text(1.0, 1.03, "D druggable · E PDAC-essential · C CRC-essential",
            transform=ax.transAxes, ha="right", fontsize=4.6, color="#555555")
    ax.text(0.0, -0.20, "prospective computational hypotheses; none is a "
            "validated target", transform=ax.transAxes, fontsize=4.8,
            color="#555555")
    panel(ax, "b", dx=-0.24)

    ax = fig.add_subplot(gs[0, 2])
    ep6 = "E6 PDAC drug-response actionability"
    if ep6 in B:
        keep = ["STRING centrality", "Harmonic mean", "ECS (multiplicative)",
                "Druggability", "Random forest", "Arithmetic mean"]
        rows = [(m, B[ep6][m]) for m in keep if m in B[ep6]]
        rows.sort(key=lambda kv: kv[1]["auroc"])
        cmap = {"STRING centrality": C_BASE, "Harmonic mean": C_INT,
                "ECS (multiplicative)": "#7FC8BF", "Random forest": C_RF,
                "Druggability": C_NULL, "Arithmetic mean": C_NULL}
        for i, (m, v) in enumerate(rows):
            ax.barh(i, v["auroc"], 0.62, color=cmap.get(m, C_NULL), ec="white",
                    lw=0.3)
            ax.plot(v["auroc_ci"], [i, i], color="#1A1A1A", lw=0.6)
            ax.text(v["auroc_ci"][1] + 0.012, i, "%.3f" % v["auroc"],
                    va="center", fontsize=4.7)
        ax.set_yticks(range(len(rows)))
        ax.set_yticklabels([m for m, _ in rows], fontsize=4.9)
        ax.axvline(0.5, color="#1A1A1A", lw=0.6, ls="--")
        ax.set_xlim(0.40, 1.06)
        G = R.get("gdsc_endpoint", {})
        ax.set_xlabel("AUROC on E6 (GDSC drug response)")
        ax.text(0.0, -0.20, "%s PDAC lines · %s compounds · %s target genes"
                % (G.get("n_pdac_lines", "?"), G.get("n_drugs_used", "?"),
                   G.get("n_positive_genes", "?")),
                transform=ax.transAxes, fontsize=4.7, color="#555555")
    panel(ax, "c", dx=-0.46)
    save(fig, "Fig6")


if __name__ == "__main__":
    print("rendering V18 display items ->", FIG)
    for fn in (fig1, fig2, fig3, fig4, fig5, fig6):
        try:
            fn()
        except Exception as exc:
            print("  FAILED %s: %s" % (fn.__name__, exc))
    print("done")
