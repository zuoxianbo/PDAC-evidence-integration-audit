#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""V18 display items (6) REDESIGNED per NCS review plan -- stamp v29_20260823_1718.

Re-renders Fig. 1-6 from the ALREADY-COMPUTED results JSONs
(results/v18_ncs_results.json, results/v18_weight_space.json,
results/v18_sentinel_audit.json). Source raw inputs are absent, so only
existing outputs are re-rendered; gaps are marked, never fabricated.

Semantic palette (HEX) -- no rainbow, no red-green:
  C_CENT   #2F5B88  network centrality / baseline
  C_INT    #2A9D8F  fixed-form integration (harmonic/additive/geometric)
  C_RF     #D56A3A  supervised learners (RF / elastic net / logistic)
  C_CIRC   #7A6AA6  constructed / circular endpoints (E3 / E3-C)
  C_NEU    #9E9E9E  neutral / missing / control
  C_CHANCE #555555  chance / axis reference (AUROC = 0.5 dashed)

Conventions: Arial 5-7 pt, >=300 dpi, RGB, tight bbox; vector PDF + PNG.
Note: Fig. 6 main panels are REDESIGNED (stress test + source-overlap
sensitivity). The 9 candidate genes are NOT plotted in main Fig. 6 (they
move to Extended Data Fig. 4); candidate info is read only if present and
is otherwise skipped.
"""
import json
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import LinearSegmentedColormap, TwoSlopeNorm
from matplotlib.patches import Patch, Rectangle, FancyBboxPatch

# ---- output paths --------------------------------------------------------
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RES = os.path.join(ROOT, "results")
FIG = "/Users/zuoxianbo/Desktop/SCI论文/胰腺癌_submission/figures_v29_20260823_1718"
os.makedirs(FIG, exist_ok=True)

R = json.load(open(os.path.join(RES, "v18_ncs_results.json")))
WS = json.load(open(os.path.join(RES, "v18_weight_space.json")))
SENT = json.load(open(os.path.join(RES, "v18_sentinel_audit.json")))

# ---- semantic palette ----------------------------------------------------
C_CENT, C_INT, C_RF, C_CIRC, C_NEU, C_CHANCE = (
    "#2F5B88", "#2A9D8F", "#D56A3A", "#7A6AA6", "#9E9E9E", "#555555")
INK = "#1A1A1A"

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
W1, W2 = 88 * MM, 180 * MM

STAMP = "v29_20260823_1718"

EP_FULL = [k for k in R["benchmark"].keys()]
EP_SHORT = {k: k.split()[0] for k in EP_FULL}
B = R["benchmark"]


def save(fig, name):
    for ext in ("png", "pdf"):
        fig.savefig(os.path.join(FIG, f"{name}_{STAMP}.{ext}"), dpi=400,
                    bbox_inches="tight", pad_inches=0.06)
    plt.close(fig)
    print(f"  wrote {name}_{STAMP}.png / .pdf")


def panel(ax, letter, dx=-0.16, dy=1.06):
    ax.text(dx, dy, letter, transform=ax.transAxes, fontsize=8,
            fontweight="bold", va="top", ha="left")


# =====================================================================
# Fig. 1 | Endpoint provenance: single evidence layers + dependency structure
# =====================================================================
def fig1():
    layers = ["STRING centrality", "Druggability", "Mutation frequency",
              "Genetic constraint", "Cancer-driver annotation"]
    eps = ["E1 pan-dependency", "E3 conjunctive actionability",
           "E5 historical clinical-target concordance"]
    fig = plt.figure(figsize=(W2, 70 * MM))
    gs = fig.add_gridspec(1, 2, width_ratios=[1.45, 1.0], wspace=0.30)

    # (a) single-layer magnitude -- baseline blue + neutral gray only
    ax = fig.add_subplot(gs[0, 0])
    n_l, n_e = len(layers), len(eps)
    off = np.linspace(-0.26, 0.26, n_e)
    for i, lay in enumerate(layers):
        base_col = C_CENT if lay == "STRING centrality" else C_NEU
        for j, ep in enumerate(eps):
            v = B[ep].get(lay)
            if v is None:
                continue
            y = (n_l - 1 - i) + off[j]
            lo, hi = v["auroc_ci"]
            ax.plot([lo, hi], [y, y], color=base_col, lw=1.0,
                    solid_capstyle="butt", alpha=0.95)
            ax.plot(v["auroc"], y, "o", ms=2.8, color=base_col,
                    mec="white", mew=0.35, zorder=3)
    ax.axvline(0.5, color=C_CHANCE, lw=0.8, ls="--", zorder=0)
    ax.set_yticks(range(n_l))
    ax.set_yticklabels([l.replace(" annotation", "") for l in layers[::-1]])
    ax.set_xlabel("AUROC (95% CI, 2,000 bootstrap resamples)")
    ax.set_xlim(0.40, 1.02)
    ax.text(0.5, -0.055, "chance", transform=ax.get_xaxis_transform(),
            ha="center", va="top", fontsize=5, color="#666666")
    ax.legend(handles=[Patch(fc=C_CENT, ec="none", label="STRING centrality "
                             "(network-centrality baseline)"),
                       Patch(fc=C_NEU, ec="none", label="other single "
                             "evidence layers")],
              loc="upper center", bbox_to_anchor=(0.5, -0.20), ncol=1,
              handlelength=1.1, columnspacing=1.1)
    panel(ax, "a", dx=-0.30)

    # (b) dependency structure -- 3 visual classes
    ax2 = fig.add_subplot(gs[0, 1])
    ax2.set_xlim(0, 10); ax2.set_ylim(-2.3, 10.3); ax2.axis("off")
    # -- external-label family (blue) --
    ax2.add_patch(FancyBboxPatch((0.5, 1.5), 8.0, 7.6,
                 boxstyle="round,pad=0.02,rounding_size=0.15",
                 fc="#EEF2F7", ec=C_CENT, lw=0.9))
    ax2.text(4.5, 9.35, "E1 pan-dependency  (n = %d)" %
             B["E1 pan-dependency"]["STRING centrality"]["n_pos"],
             ha="center", fontsize=6, color=C_CENT)
    # E4 / E5 / E6 = external-label, blue outline
    for x0, lab, sub in ((0.4, "E4 CRC", "cross-context\nzero-shot transfer"),
                         (3.6, "E5 / E6", "clinical history /\nGDSC drug response")):
        ax2.add_patch(Rectangle((x0, -1.9), 2.8, 2.2, fc="#FFFFFF", ec=C_CENT,
                                lw=0.7))
        ax2.text(x0 + 1.4, -0.55, lab, ha="center", fontsize=5.5, color=C_CENT)
        ax2.text(x0 + 1.4, -1.35, sub, ha="center", va="center", fontsize=4.8,
                 color="#444444")
    # -- nested / non-independent family (light gray) --
    ax2.add_patch(Rectangle((1.0, 5.2), 3.4, 3.2, fc="#FFFFFF", ec=C_NEU, lw=0.9))
    ax2.text(2.7, 8.1, "E2 PDAC-enriched", ha="center", fontsize=5.5,
             color="#555555")
    ax2.text(2.7, 7.05, "top quartile of E1\n(n = %d)\n[nested in E1]" %
             B["E2 PDAC-enriched dependency"]["STRING centrality"]["n_pos"],
             ha="center", va="center", fontsize=5, color="#444444")
    ax2.add_patch(Rectangle((1.0, 2.0), 7.1, 2.8, fc="#FFFFFF", ec=C_NEU,
                            lw=0.9, ls=(0, (2, 1.4))))
    ax2.text(4.55, 4.35, "E3-A leakage-controlled  $\\equiv$  E1",
             ha="center", fontsize=5.5, color="#555555")
    ax2.text(4.55, 3.1, "dropping the druggability conjunct returns the\n"
             "E1 positive set exactly  [identical to E1 positive set]",
             ha="center", va="center", fontsize=5, color="#444444")
    # -- constructed / circular family (purple) --
    ax2.add_patch(Rectangle((4.8, 5.2), 3.3, 3.2, fc="#F3EFF8", ec=C_CIRC,
                            lw=0.9))
    ax2.text(6.45, 8.1, "E3 conjunctive", ha="center", fontsize=5.5, color=C_CIRC)
    ax2.text(6.45, 7.05, "E1 $\\cap$ druggable\n(n = %d)\n[constructed / circular]" %
             B["E3 conjunctive actionability"]["STRING centrality"]["n_pos"],
             ha="center", va="center", fontsize=5, color="#444444")
    ax2.add_patch(Rectangle((6.8, -1.9), 2.8, 2.2, fc="#F3EFF8", ec=C_CIRC,
                            lw=0.9))
    ax2.text(8.2, -0.55, "E3-C", ha="center", fontsize=5.5, color=C_CIRC)
    ax2.text(8.2, -1.35, "label = input\nlayer (leakage)", ha="center",
             va="center", fontsize=4.8, color="#444444")
    ax2.text(4.5, 10.0, "Endpoint dependency structure", ha="center", fontsize=6.5)
    ax2.text(4.5, -2.1, "blue = external-label · gray = nested / non-independent"
             " · purple = constructed / circular",
             ha="center", fontsize=4.6, color="#666666")
    panel(ax2, "b", dx=-0.02, dy=1.02)
    save(fig, "Fig1")


# =====================================================================
# Fig. 2 | Benchmark matrix, 13 scorers x 8 endpoints (diverging, azure/orange)
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
    fig, ax = plt.subplots(figsize=(W2, 80 * MM))
    # diverging scale centered at 0.5: below chance = light orange, above = light blue
    CMAP = LinearSegmentedColormap.from_list("div", ["#F4CDB0", "#FFFFFF", "#BFD8EA"])
    norm = TwoSlopeNorm(vmin=0.35, vcenter=0.5, vmax=1.0)
    im = ax.imshow(M, cmap=CMAP, norm=norm, aspect="auto")

    circ_cols = [j for j, e in enumerate(EP_FULL)
                 if e.startswith("E3") and ("E3-C" in e or "E3 conjunctive" in e)]
    for i in range(len(meths)):
        for j in range(len(EP_FULL)):
            if np.isnan(M[i, j]):
                ax.text(j, i, "n.a.", ha="center", va="center", fontsize=4.6,
                        color="#888888")
                continue
            leak = (EP_FULL[j].startswith("E3-C") and M[i, j] > 0.999)
            dark = M[i, j] > 0.78 or leak
            ax.text(j, i, ("%.2f" % M[i, j]).lstrip("0"), ha="center", va="center",
                    fontsize=4.9, color=("white" if dark else "#1A1A1A"),
                    fontweight="bold" if leak else "normal")
            if leak:  # E3-C 1.000 = label-as-input control, NOT a model result
                ax.add_patch(Rectangle((j - .5, i - .5), 1, 1, fill=False,
                                       ec=C_CIRC, lw=1.1, ls=(0, (1.4, 1.0))))
    # purple column background for constructed / circular endpoints (E3, E3-C)
    for j in circ_cols:
        ax.add_patch(Rectangle((j - .5, -0.5), 1, len(meths), fc="#F3EFF8",
                               ec="none", zorder=-1, alpha=0.9))
    ax.set_xticks(range(len(EP_FULL)))
    ax.set_xticklabels([EP_SHORT[e] for e in EP_FULL])
    ax.set_yticks(range(len(meths)))
    ax.set_yticklabels(meths)
    ax.set_xlabel("Validation endpoint")

    # row labels colored by scorer FAMILY
    fam = {
        "STRING centrality": C_CENT,
        "Mutation frequency": C_NEU, "Genetic constraint": C_NEU,
        "Cancer-driver annotation": C_NEU, "Druggability": C_NEU,
        "Arithmetic mean": C_INT, "Rank aggregation": C_INT,
        "Weighted rank aggregation": C_INT, "ECS (multiplicative)": C_INT,
        "Harmonic mean": C_INT,
        "Logistic regression": C_RF, "Elastic net": C_RF, "Random forest": C_RF,
    }
    for i, m in enumerate(meths):
        ax.get_yticklabels()[i].set_color(fam.get(m, INK))
    ax.set_xticks(np.arange(-.5, len(EP_FULL), 1), minor=True)
    ax.set_yticks(np.arange(-.5, len(meths), 1), minor=True)
    ax.grid(which="minor", color="white", lw=0.6)
    ax.tick_params(which="minor", length=0)
    cb = fig.colorbar(im, ax=ax, fraction=0.022, pad=0.015,
                      ticks=[0.4, 0.5, 0.7, 0.9, 1.0])
    cb.set_label("AUROC", fontsize=6)
    cb.ax.tick_params(labelsize=5)
    cb.outline.set_linewidth(0.4)
    # caption clarifying E3-C
    ax.text(0.0, -0.155, "purple columns = constructed / circular diagnostic "
            "(E3, E3-C). E3-C AUROC = 1.000 is a label-as-input control "
            "(the druggability label is itself an input layer), not a model result.",
            transform=ax.transAxes, fontsize=4.8, color="#555555")
    save(fig, "Fig2")


# =====================================================================
# Fig. 3 | Integration confers no intrinsic advantage over centrality
# =====================================================================
def fig3():
    D = R["delta_auroc_paired_bootstrap"]
    L = R["delong_pairwise"]
    keys = [("Harmonic mean - STRING centrality", "Harmonic mean", C_INT),
            ("Random forest - STRING centrality", "Random forest", C_RF)]
    ep_plot = ["E1 pan-dependency", "E4 CRC zero-shot transfer",
               "E5 historical clinical-target concordance",
               "E6 PDAC drug-response actionability"]
    fig = plt.figure(figsize=(W2, 64 * MM))
    gs = fig.add_gridspec(1, 2, width_ratios=[1.45, 1.0], wspace=0.46)

    # (a) effect size + 95% CI, no stars; deepen zero line
    ax = fig.add_subplot(gs[0, 0])
    yy, ylab = [], []
    for i, e in enumerate(ep_plot[::-1]):
        base = i * 1.0
        for k, (key, lab, col) in enumerate(keys):
            d = D.get(e, {}).get(key)
            if not d:
                continue
            y = base + (k - 0.5) * 0.32
            dm = d.get("delta_mean", d.get("delta"))
            ax.plot([d["ci_lo"], d["ci_hi"]], [y, y], color=col, lw=0.7,
                    solid_capstyle="butt")
            ax.plot(dm, y, "o", ms=2.8, color=col, mec="white", mew=0.35,
                    zorder=3)
        yy.append(base); ylab.append(EP_SHORT[e])
    ax.axvline(0, color=INK, lw=1.1, zorder=0)          # deepened zero line
    ax.set_yticks(yy); ax.set_yticklabels(ylab)
    ax.set_xlabel("$\\Delta$AUROC = scorer $-$ STRING centrality\n"
                  "(paired bootstrap, 95% CI)")
    ax.legend(handles=[Patch(fc=c, ec="none", label=l) for _, l, c in keys],
              loc="upper center", bbox_to_anchor=(0.5, -0.22), ncol=2,
              handlelength=1.1, columnspacing=1.0)
    ax.text(1.0, 1.03, "effect size + 95% CI (no significance stars)",
            transform=ax.transAxes, ha="right", fontsize=4.6, color="#444444")
    panel(ax, "a", dx=-0.24)

    # (b) network-community resampling -- robustness analysis
    ax = fig.add_subplot(gs[0, 1])
    S = R["structured_resampling"]
    ax.axhline(0, color=INK, lw=1.1)
    ax.plot([0, 0], [S["delta_ci_lo"], S["delta_ci_hi"]], color=C_INT, lw=1.6)
    ax.plot(0, S["delta_mean"], "o", ms=4.2, color=C_INT, mec="white", mew=0.4)
    ax.set_xlim(-1.1, 1.1); ax.set_xticks([0])
    ax.set_xticklabels(["community\nbootstrap"], fontsize=5)
    ax.set_ylabel("$\\Delta$AUROC, ECS $-$ STRING centrality")
    ax.text(0.06, 0.03, "%d STRING-centrality communities\n%d resamples · "
            "%.0f%% > 0 · %.1f%% < 0"
            % (S["n_communities"], S["n_bootstrap"], S["pct_positive"],
               100 - S["pct_positive"]),
            transform=ax.transAxes, fontsize=4.8, color="#444444", va="bottom")
    panel(ax, "b", dx=-0.52)
    ax.text(0.5, -0.30, "b · robustness analysis (network-community resampling)",
            transform=ax.transAxes, ha="center", fontsize=5, color="#333333")

    # caption: DeLong P (primary info moved here, not as stars)
    pnote = "DeLong P (scorer vs STRING centrality): "
    plines = []
    for e in ep_plot:
        parts = []
        for key, lab, _ in keys:
            r = L.get(e, {}).get(key.replace(" - ", " vs "))
            if r:
                parts.append("%s %s=%.1e" % (EP_SHORT[e], lab.split()[0],
                                             max(r["p"], 1e-300)))
        plines.append(" · ".join(parts))
    fig.text(0.5, -0.02, pnote + "  |  " + "   ".join(plines),
             ha="center", fontsize=4.4, color="#555555")
    save(fig, "Fig3")


# =====================================================================
# Fig. 4 | Why integration appears to work
# =====================================================================
def fig4():
    fig = plt.figure(figsize=(W2, 74 * MM))
    gs = fig.add_gridspec(1, 3, width_ratios=[1.15, 1.0, 1.25], wspace=0.46)

    # (a) how much of the evidence base is actually annotation absence
    ax = fig.add_subplot(gs[0, 0])
    lay = SENT["S1_sentinel_coding"]["per_layer"]
    names = sorted(lay, key=lambda k: lay[k]["pct_sentinel"])
    pos = np.arange(len(names))
    for i, f in enumerate(names):
        v = lay[f]["pct_sentinel"]
        ax.barh(i, v, 0.66, color=C_NEU, ec="white", lw=0.3)
        ax.text(v + 1.4, i, "%.0f%%" % v, va="center", fontsize=4.9,
                color="#333333")
    ax.axvline(50, color=C_CENT, lw=0.8, ls="--")
    ax.set_yticks(pos)
    ax.set_yticklabels([f.replace("_", " ") for f in names], fontsize=5)
    ax.set_xlabel("genes with no annotation (%)")
    ax.set_xlim(0, 112)
    ax.text(50, len(names) - 0.35, "median gene\nunannotated", fontsize=4.6,
            color=C_CENT, ha="left", va="center")
    # key annotations OUTSIDE the bars, not stacked inside
    mean_pct = SENT["S1_sentinel_coding"]["mean_pct_sentinel_across_layers"]
    cd_pct = lay["cancer_driver"]["pct_sentinel"]
    ax.text(92, len(names) - 0.75, "cancer driver\n= %.1f%%" % cd_pct,
            va="top", ha="right", fontsize=4.8, color=C_CIRC)
    ax.text(108, 0.15, "mean across\n9 layers = %.1f%%" % mean_pct,
            va="bottom", ha="right", fontsize=4.8, color=C_CIRC)
    panel(ax, "a", dx=-0.52)

    # (b) multiplicative rule is not order preserving -- sign-flip partition
    ax = fig.add_subplot(gs[0, 1])
    s2 = SENT["S2_order_preservation"]
    # real documented proportions -> 4 quadrants (term sign x D sign)
    p_term_neg = s2["pct_genes_gain_term_negative"]            # 84.0
    p_d_neg = s2["pct_genes_driver_negative"]                  # 28.0
    p_double = s2["pct_genes_double_sign_flip"]                # 26.15
    a = (100 - p_term_neg) - (p_d_neg - p_double)              # term+ & D+
    b = p_d_neg - p_double                                     # term+ & D-
    c = p_term_neg - p_double                                  # term- & D+
    d = p_double                                               # term- & D- (double neg)
    quads = [("term > 0 · D > 0", a, "#E3E9EF", C_NEU),
             ("term > 0 · D < 0", b, "#EDE3DA", C_RF),
             ("term < 0 · D > 0", c, "#E3E9EF", C_NEU),
             ("term < 0 · D < 0", d, "#F4CDB0", C_RF)]
    xs = [0.0, 0.5, 0.0, 0.5]; ys = [0.5, 0.5, 0.0, 0.0]
    for (lab, val, fc, ec), x, y in zip(quads, xs, ys):
        ax.add_patch(Rectangle((x, y), 0.5, 0.5, fc=fc, ec=ec, lw=1.0))
        ax.text(x + 0.25, y + 0.5 / 2.0, "%.1f%%" % val, ha="center",
                va="center", fontsize=6.5, color=INK, fontweight="bold")
    ax.axvline(0.5, color=INK, lw=0.9); ax.axhline(0.5, color=INK, lw=0.9)
    ax.set_xlim(0, 1); ax.set_ylim(0, 1)
    ax.set_xticks([0.25, 0.75]); ax.set_xticklabels(["support term > 0",
                                                     "support term < 0"],
                                                     fontsize=4.8)
    ax.set_yticks([0.25, 0.75]); ax.set_yticklabels(["score rises w/ support",
                                                     "score falls w/ support"],
                                                     fontsize=4.8)
    ax.text(0.25, 0.02, "26.2% double-negative region", transform=ax.transAxes,
            ha="center", fontsize=4.6, color=C_RF)
    ax.text(0.02, 0.98, "corr($\\Phi$, ECS): D>0 %+.2f · D<0 %+.2f"
            % (s2["corr_PHI_score_when_D_positive"],
               s2["corr_PHI_score_when_D_negative"]),
            transform=ax.transAxes, va="top", fontsize=4.6, color="#333333")
    ax.set_title("monotonicity violation (schematic partition)",
                 fontsize=5.2, loc="left")
    panel(ax, "b", dx=-0.34)

    # (c) collapse after deleting the label's own (tractability) layer
    ax = fig.add_subplot(gs[0, 2])
    S3 = SENT["S3_endpointwise"]
    rows = [("E3 conjunctive actionability", C_CIRC),
            ("E3-C out-of-evidence druggability", C_CIRC)]
    for i, (e, col) in enumerate(rows):
        full = S3[e]["support_mean_PHI"]
        collapse = S3[e]["support_mean_without_druggability"]
        y = len(rows) - 1 - i
        ax.plot(full, y, "o", ms=4.5, color=col, mec="white", mew=0.4, zorder=4)
        ax.plot(collapse, y, "o", ms=4.5, color=C_NEU, mec="white", mew=0.4,
                zorder=4)
        ax.plot([full, collapse], [y, y], color=INK, lw=1.0, ls="-", zorder=3)
        ax.annotate("%.3f $\\to$ %.3f" % (full, collapse),
                    xy=(collapse, y), xytext=(collapse - 0.02, y + 0.18),
                    fontsize=4.8, color=INK, ha="right", va="bottom")
    ax.axvline(0.5, color=C_CHANCE, lw=0.7, ls="--", zorder=0)
    ax.set_yticks(range(len(rows)))
    ax.set_yticklabels([EP_SHORT[e] for (e, _) in rows])
    ax.set_xlim(0.42, 1.02); ax.set_ylim(-0.6, len(rows) - 0.2)
    ax.set_xlabel("AUROC of the integrated support mean")
    ax.legend(handles=[Patch(fc=C_CIRC, ec="none", label="full support (incl. "
                             "tractability)"),
                       Patch(fc=C_NEU, ec="none", label="after tractability "
                             "deletion")],
              loc="lower left", bbox_to_anchor=(0.0, 1.02), ncol=1,
              handlelength=1.1, fontsize=4.8)
    ax.text(0.98, 0.04, "collapse after deleting\nthe label's own layer",
            transform=ax.transAxes, ha="right", va="bottom", fontsize=4.6,
            color="#333333")
    panel(ax, "c", dx=-0.14)
    save(fig, "Fig4")


# =====================================================================
# Fig. 5 | Sensitivity: functional form, weight space, controls, recoding
# =====================================================================
def fig5():
    F = R["functional_forms_all_endpoints"]
    forms = ["harmonic mean", "additive", "multiplicative (ECS)",
             "geometric mean", "rank aggregation"]
    shades = [C_INT, "#54B3A7", "#7FC8BF", "#A9DBD5", C_CENT]
    eps = [e for e in EP_FULL if not e.startswith("E3-A")]
    fig = plt.figure(figsize=(W2, 74 * MM))
    gs = fig.add_gridspec(1, 4, width_ratios=[1.5, 1.05, 0.85, 0.95], wspace=0.46)

    # (a) fixed functional forms
    ax = fig.add_subplot(gs[0, 0])
    x = np.arange(len(eps)); w = 0.155
    for k, (f, c) in enumerate(zip(forms, shades)):
        ax.bar(x + (k - 2) * w, [F.get(e, {}).get(f, {}).get("auroc", np.nan)
                                 for e in eps], w, color=c, ec="white", lw=0.25,
               label=f)
    ax.axhline(0.5, color=C_CHANCE, lw=0.7, ls="--")
    ax.set_xticks(x); ax.set_xticklabels([EP_SHORT[e] for e in eps])
    ax.set_ylabel("AUROC"); ax.set_ylim(0.30, 1.02)
    ax.set_xlabel("Validation endpoint")
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.235), ncol=3,
              handlelength=1.0, columnspacing=0.9, fontsize=5)
    panel(ax, "a", dx=-0.14)

    # (b) weight space -> ECDF with median / IQR / 2.5-97.5 pct + prespecified + baseline
    ax = fig.add_subplot(gs[0, 1])
    smp = np.asarray(WS["auroc_samples"])
    xs = np.sort(smp); ec = np.arange(1, len(xs) + 1) / len(xs)
    ax.step(xs, ec, where="post", color=C_CENT, lw=1.0)
    med = np.median(smp); q25, q75 = np.percentile(smp, [25, 75])
    q025, q975 = np.percentile(smp, [2.5, 97.5])
    for xx, c, lab in ((q025, C_NEU, "2.5 pct"), (q975, C_NEU, "97.5 pct"),
                       (q25, "#9FB8CC", "IQR"), (q75, "#9FB8CC", "IQR"),
                       (med, INK, "median")):
        ax.axvline(xx, color=c, lw=0.8, ls="--")
    ax.axvline(WS["string_auroc_e3"], color=C_CENT, lw=1.2, zorder=4)
    ax.axvline(WS["v17_chosen_weighting_auroc_e3"], color=C_RF, lw=1.2, zorder=4)
    ax.set_xlabel("AUROC on E3 over %s Dirichlet\nweightings of the driver layers"
                  % format(WS["n_draws"], ","))
    ax.set_ylabel("cumulative fraction of draws")
    ax.set_ylim(0, 1.04)
    ax.text(0.02, 0.97, "median %.3f\nIQR %.3f–%.3f\n2.5–97.5 pct %.3f–%.3f"
            % (med, q25, q75, q025, q975), transform=ax.transAxes, va="top",
            fontsize=4.7, color="#333333")
    ax.legend(handles=[Patch(fc=C_CENT, label="STRING alone %.3f"
                             % WS["string_auroc_e3"]),
                       Patch(fc=C_RF, label="prespecified weighting %.3f"
                             % WS["v17_chosen_weighting_auroc_e3"]),
                       Patch(fc=C_NEU, label="2.5 / 97.5 pct")],
              loc="lower right", fontsize=4.6)
    panel(ax, "b", dx=-0.34)

    # (c) horizontal dot plot for three negative controls (null manipulation)
    ax = fig.add_subplot(gs[0, 2])
    C = R["negative_controls"]
    controls = [("random_gaussian_layer", "Gaussian\nlayer"),
                ("shuffled_network", "shuffled\nnetwork"),
                ("permuted_druggability", "permuted\ndruggability")]
    obs = C["ecs_observed"]
    for i, (k, lab) in enumerate(controls):
        v = C[k]
        ax.plot(v["auroc"], i, "o", ms=4.0, color=C_NEU, mec="white", mew=0.4,
                zorder=4)
        ax.plot(v["auroc_ci"], [i, i], color=INK, lw=0.7, zorder=3)
        ax.text(v["auroc_ci"][1] + 0.012, i, "%.3f" % v["auroc"], va="center",
                fontsize=4.7)
    ax.axvline(0.5, color=C_CHANCE, lw=0.7, ls="--", zorder=0)
    ax.axvline(obs["auroc"], color=C_INT, lw=0.7, ls=":", zorder=2)
    ax.text(obs["auroc"], 2.42, "observed ECS %.3f" % obs["auroc"], rotation=90,
            va="top", ha="right", fontsize=4.3, color=C_INT)
    ax.set_yticks(range(len(controls)))
    ax.set_yticklabels([l for _, l in controls], fontsize=4.8)
    ax.set_xlabel("AUROC on E3")
    ax.set_ylim(-0.6, 2.7)
    panel(ax, "c", dx=-0.46)

    # (d) paired point plot: sentinel-coded vs available-case
    ax = fig.add_subplot(gs[0, 3])
    S4 = SENT["S4_sentinel_corrected_sensitivity"]["per_endpoint"]
    eps2 = [e for e in EP_FULL]
    yy = np.arange(len(eps2))[::-1]
    for y, e in zip(yy, eps2):
        sv = S4[e]["harmonic_sentinel_as_value"]
        av = S4[e]["harmonic_available_case"]
        ax.plot([sv, av], [y, y], color="#BBBBBB", lw=0.7, zorder=2)
        ax.plot(sv, y, "o", ms=3.0, color=C_NEU, mec="white", mew=0.3, zorder=3)
        ax.plot(av, y, "o", ms=3.4, color=C_CENT, mec="white", mew=0.35, zorder=4)
        ax.text(av + 0.006, y + 0.16, "%+.3f" % S4[e]["harmonic_delta"],
                va="bottom", ha="left", fontsize=4.4, color="#333333")
    ax.axvline(0.5, color=C_CHANCE, lw=0.7, ls="--", zorder=0)
    ax.set_yticks(yy); ax.set_yticklabels([EP_SHORT[e] for e in eps2], fontsize=5)
    ax.set_xlabel("AUROC (harmonic) — sentinel-coded vs available-case")
    ax.set_xlim(0.38, 1.0)
    ax.legend(handles=[Patch(fc=C_NEU, ec="none", label="sentinel = -3"),
                       Patch(fc=C_CENT, ec="none", label="available-case")],
              loc="lower right", fontsize=4.6)
    panel(ax, "d", dx=-0.46)
    save(fig, "Fig5")


# =====================================================================
# Fig. 6 REDESIGN | Pharmacological stress test and source-overlap sensitivity
#   (candidate genes moved to Extended Data Fig. 4 -- NOT plotted here)
# =====================================================================
def fig6():
    fig = plt.figure(figsize=(W2, 76 * MM))
    gs = fig.add_gridspec(1, 3, width_ratios=[1.05, 1.1, 1.0], wspace=0.5)

    # (a) E6 endpoint construction / target attribution pipeline
    ax = fig.add_subplot(gs[0, 0]); ax.axis("off")
    ax.set_xlim(0, 10); ax.set_ylim(0, 10)
    G = R.get("gdsc_endpoint", {})
    nlines = G.get("n_pancreas_lines_with_ic50",
                    G.get("n_pancreas_lines_annotated", "?"))
    ndrugs = G.get("n_drugs_screened", "?")
    npos = G.get("n_positive_genes", "?")
    ntert = G.get("n_drugs_sensitive_tertile", "?")

    def box(x, y, w, h, txt, fc, ec, tc):
        ax.add_patch(FancyBboxPatch((x, y), w, h,
                     boxstyle="round,pad=0.02,rounding_size=0.12",
                     fc=fc, ec=ec, lw=0.8))
        ax.text(x + w / 2, y + h / 2, txt, ha="center", va="center",
                fontsize=4.5, color=tc)

    box(0.4, 7.2, 4.6, 2.0, "GDSC v2 IC50 matrix\n%s PDAC lines · %s drugs"
        % (nlines, ndrugs), "#EEF2F7", C_CENT, "#1A1A1A")
    box(5.0, 7.2, 4.6, 2.0, "drug-response labels\n%s sensitivities"
        % ntert, "#EEF2F7", C_CENT, "#1A1A1A")
    box(2.6, 4.4, 4.8, 1.8, "E6 PDAC drug-response actionability\n(%s target genes, "
        "orthogonal endpoint)" % npos, "#F3EFF8", C_CIRC, "#1A1A1A")
    scorers = [("STRING\ncentrality", C_CENT), ("Tractability", C_NEU),
               ("Harmonic\nmean", C_INT), ("Random\nforest", C_RF)]
    for i, (s, c) in enumerate(scorers):
        bx = 0.5 + i * 2.3
        box(bx, 2.0, 2.0, 1.6, s, "#FFFFFF", c, "#1A1A1A")
    box(2.7, 0.2, 4.6, 1.4, "target attribution:\nscore-ranked genes -> candidate "
        "hypotheses", "#FFFFFF", INK, "#1A1A1A")
    # arrows
    for (x0, y0, x1, y1) in ((2.6, 7.2, 4.2, 6.2),
                             (7.4, 7.2, 5.8, 6.2),
                             (5.0, 6.2, 5.0, 4.4),
                             (1.5, 2.0, 1.5, 1.6),
                             (3.8, 2.0, 3.8, 1.6),
                             (6.2, 2.0, 6.2, 1.6),
                             (8.5, 2.0, 8.5, 1.6),
                             (5.0, 1.8, 5.0, 1.6)):
        ax.annotate("", xy=(x1, y1), xytext=(x0, y0),
                    arrowprops=dict(arrowstyle="->", lw=0.7, color="#444444"))
    ax.text(5.0, 9.8, "E6 construction & target-attribution pipeline",
            ha="center", fontsize=6.5)
    ax.text(5.0, -0.3, "leakage-free: IC50 labels are independent of the "
            "evidence layers", ha="center", fontsize=4.4, color="#666666")
    panel(ax, "a", dx=-0.02, dy=1.0)

    # (b) E6 AUROC comparison across scorer families
    ax = fig.add_subplot(gs[0, 1])
    ep6 = "E6 PDAC drug-response actionability"
    keep = ["STRING centrality", "Harmonic mean", "Arithmetic mean",
            "Rank aggregation", "ECS (multiplicative)", "Druggability",
            "Random forest", "Logistic regression", "Elastic net"]
    rows = [(m, B[ep6][m]) for m in keep if m in B[ep6]]
    rows.sort(key=lambda kv: kv[1]["auroc"])
    cmap = {"STRING centrality": C_CENT, "Harmonic mean": C_INT,
            "Arithmetic mean": C_INT, "Rank aggregation": C_INT,
            "ECS (multiplicative)": C_INT, "Druggability": C_NEU,
            "Random forest": C_RF, "Logistic regression": C_RF,
            "Elastic net": C_RF}
    for i, (m, v) in enumerate(rows):
        ax.barh(i, v["auroc"], 0.62, color=cmap.get(m, C_NEU), ec="white", lw=0.3)
        ax.plot(v["auroc_ci"], [i, i], color=INK, lw=0.6)
        ax.text(v["auroc_ci"][1] + 0.012, i, "%.3f" % v["auroc"], va="center",
                fontsize=4.7)
    ax.set_yticks(range(len(rows)))
    ax.set_yticklabels([m for m, _ in rows], fontsize=4.9)
    ax.axvline(0.5, color=C_CHANCE, lw=0.7, ls="--")
    ax.set_xlim(0.30, 1.06)
    ax.set_xlabel("AUROC on E6 (GDSC drug response)")
    panel(ax, "b", dx=-0.46)

    # (c) overlap-excluded sensitivity -- GAP (data not present in regenerated JSON)
    ax = fig.add_subplot(gs[0, 2])
    ax.set_xlim(0, 1); ax.set_ylim(0, 1); ax.axis("off")
    ax.add_patch(FancyBboxPatch((0.05, 0.30), 0.90, 0.40,
                 boxstyle="round,pad=0.02", fc="#F4F4F4", ec=C_NEU, lw=0.8))
    txt = ("SOURCE-OVERLAP SENSITIVITY — DOCUMENTED GAP\n\n"
           "E6 AUROC excluding tractability-overlap genes was not present in "
           "the regenerated v18 results (source raw inputs are absent).\n\n"
           "Per the review plan this panel compares all-E6 vs "
           "tractability-overlap-excluded E6. No value is fabricated here; "
           "render from the recomputed source data when available "
           "(see Extended Data).")
    ax.text(0.5, 0.50, txt, ha="center", va="center", fontsize=4.6,
            color="#444444", wrap=True)
    ax.text(0.5, 0.9, "overlap-excluded sensitivity", ha="center", fontsize=6,
            color=INK)
    panel(ax, "c", dx=-0.46)
    save(fig, "Fig6")


if __name__ == "__main__":
    print("rendering redesigned V18 display items ->", FIG)
    for fn in (fig1, fig2, fig3, fig4, fig5, fig6):
        try:
            fn()
        except Exception as exc:
            import traceback
            print("  FAILED %s: %s" % (fn.__name__, exc))
            traceback.print_exc()
    print("done")
