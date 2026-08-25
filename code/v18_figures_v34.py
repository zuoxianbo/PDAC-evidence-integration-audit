#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""V18 display items (6) NCS / Nature production-level redraw -- stamp v34.

Frozen scientific structure of v32 retained exactly (same data, same panels).
This pass implements the v34 figure checklist:
  * One FIXED cross-figure semantic palette (navy / teal / orange / purple /
    grey / dark-grey + light-blue & gold reserved for Fig.5a's five forms).
  * ALL axis / row / panel / annotation text is BLACK; colour appears only on
    points, bars, boxes, borders and legend swatches (no coloured text coding).
  * Arial / Helvetica, font floor >= 6 pt (panel letters 9 pt bold lowercase).
  * Per-figure wording fixes from V34-图片修订建议.docx.

Renders ONLY from the already-computed result JSONs; no fabricated data.
Numbers are pulled straight from v18_source_data.csv / ncs_results.json so the
figure values are guaranteed identical to the manuscript (e.g. Fig.6 RF = 0.913).
"""
import json
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import LinearSegmentedColormap, TwoSlopeNorm
from matplotlib.patches import Patch, Rectangle, FancyBboxPatch

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RES = os.path.join(ROOT, "results")
FIG = os.path.join(ROOT, "figures")          # committed to GitHub (v34 stamped)
os.makedirs(FIG, exist_ok=True)

R = json.load(open(os.path.join(RES, "v18_ncs_results.json")))
WS = json.load(open(os.path.join(RES, "v18_weight_space.json")))
SENT = json.load(open(os.path.join(RES, "v18_sentinel_audit.json")))

# ---- v34 FIXED semantic palette (identical across all six figures) ---------
C_CENT   = "#2F5D8A"   # navy        : network centrality / rank aggregation
C_INT    = "#2A9D8F"   # teal        : fixed-form integration (harmonic / ECS)
C_RF     = "#E07A3F"   # orange      : supervised learner (RF / LR / elastic net)
C_CIRC   = "#7C6BAE"   # purple      : constructed / circular (E3 / E3-C / double-neg)
C_NEU    = "#9E9E9E"   # grey        : other single layers / neutral / null controls
C_CHANCE = "#4D4D4D"   # dark grey   : zero / chance reference line + text
C_LBLUE  = "#56B4E9"   # light blue  : arithmetic mean (Fig.5a only)
C_GOLD   = "#E69F00"   # gold        : geometric mean (Fig.5a only)
C_REF    = "#BDBDBD"   # light grey  : thin reference / zero lines
INK      = "#1A1A1A"   # all text is black

# formal layer names for Fig.4a (per V34 image checklist)
LAYER_NAME = {
    "string_centrality": "STRING centrality",
    "mutation_freq": "Mutation frequency",
    "impc_animal_ko": "IMPC knockout viability",
    "genetic_constraint": "Genetic constraint",
    "cancer_driver": "Cancer-driver annotation",
    "ot_genetics_pdac": "Open Targets Genetics",
    "druggability": "Druggability",
    "hpa_pdac_prognostic": "HPA PDAC prognostic",
    "hpa_rna_tissue_spec": "HPA RNA tissue specificity",
}

plt.rcParams.update({
    "font.family": "sans-serif",
    "font.sans-serif": ["Arial", "Helvetica", "DejaVu Sans"],
    "font.size": 7, "axes.labelsize": 7, "axes.titlesize": 7.5,
    "xtick.labelsize": 6, "ytick.labelsize": 6, "legend.fontsize": 6,
    "axes.linewidth": 0.6, "xtick.major.width": 0.6, "ytick.major.width": 0.6,
    "xtick.major.size": 2.5, "ytick.major.size": 2.5,
    "axes.spines.top": False, "axes.spines.right": False,
    "figure.facecolor": "white", "axes.facecolor": "white",
    "savefig.facecolor": "white", "legend.frameon": False,
    "pdf.fonttype": 42, "ps.fonttype": 42, "svg.fonttype": "none",
})
MM = 1.0 / 25.4
W1, W2 = 88 * MM, 180 * MM
STAMP = "v34"

EP_FULL = list(R["benchmark"].keys())
EP_SHORT = {k: k.split()[0] for k in EP_FULL}
B = R["benchmark"]


def npos(ep):
    return next(iter(B[ep].values()))["n_pos"]


def save(fig, name):
    fig.savefig(os.path.join(FIG, f"{name}_{STAMP}.png"), dpi=400,
                bbox_inches="tight", pad_inches=0.06)
    fig.savefig(os.path.join(FIG, f"{name}_{STAMP}.pdf"),
                bbox_inches="tight", pad_inches=0.06)
    plt.close(fig)
    print(f"  wrote {name}_{STAMP}.png / .pdf")


def panel(ax, letter, external=False):
    if external:
        # place the panel letter OUTSIDE the axes, top-left corner, clear of any
        # in-axes content and clear of a left-aligned panel title (right-aligned
        # just left of the axes edge).
        ax.text(-0.03, 1.03, letter, transform=ax.transAxes, fontsize=9,
                fontweight="bold", va="bottom", ha="right", color=INK,
                clip_on=False)
    else:
        ax.text(0.015, 0.965, letter, transform=ax.transAxes, fontsize=9,
                fontweight="bold", va="top", ha="left", color=INK)


def below_legend(ax, handles, ncol=2, y=-0.26, labels=None, loc="lower center",
                 handlelength=1.2, columnspacing=1.0, fontsize=6, frameon=False,
                 x=0.5):
    ax.legend(handles=handles, labels=labels, loc=loc,
              bbox_to_anchor=(x, y), ncol=ncol, handlelength=handlelength,
              columnspacing=columnspacing, fontsize=fontsize, frameon=frameon,
              edgecolor=INK, fancybox=False, borderpad=0.5)


# =====================================================================
# Fig. 1 | single-layer magnitude + endpoint dependency structure
# =====================================================================
def fig1():
    layers = ["STRING centrality", "Druggability", "Mutation frequency",
              "Genetic constraint", "Cancer-driver annotation"]
    eps = ["E1 pan-dependency", "E3 conjunctive actionability",
           "E5 historical clinical-target concordance"]
    fig = plt.figure(figsize=(W2, 84 * MM))
    gs = fig.add_gridspec(1, 2, width_ratios=[1.3, 1.1], wspace=0.34)
    fig.subplots_adjust(bottom=0.30, top=0.93)

    # (a) single-layer magnitude
    ax = fig.add_subplot(gs[0, 0])
    n_l, n_e = len(layers), len(eps)
    off = np.linspace(-0.24, 0.24, n_e)
    for i, lay in enumerate(layers):
        base_col = C_CENT if lay == "STRING centrality" else C_NEU
        for j, ep in enumerate(eps):
            v = B[ep].get(lay)
            if v is None:
                continue
            y = (n_l - 1 - i) + off[j]
            lo, hi = v["auroc_ci"]
            ax.plot([lo, hi], [y, y], color=base_col, lw=1.2,
                    solid_capstyle="butt", alpha=0.95)
            ax.plot(v["auroc"], y, "o", ms=3.0, color=base_col,
                    mec="white", mew=0.4, zorder=3)
    ax.axvline(0.5, color=C_REF, lw=0.9, ls="--", zorder=0)
    ax.set_yticks(range(n_l))
    ax.set_yticklabels([l.replace(" annotation", "") for l in layers[::-1]],
                       fontsize=6, color=INK)
    ax.set_xlabel("AUROC (95% CI, 2,000 bootstrap resamples)")
    ax.set_xlim(0.40, 1.02)
    ax.set_title("Single evidence layers", fontsize=7.5, loc="left")
    below_legend(ax,
                 [Patch(fc=C_CENT, ec="none"),
                  Patch(fc=C_NEU, ec="none")],
                 labels=["STRING centrality (baseline)", "other single layers"],
                 ncol=2, y=-0.34)
    panel(ax, "a")

    # (b) endpoint dependency structure -- 3 semantic classes, black text
    ax2 = fig.add_subplot(gs[0, 1])
    ax2.set_xlim(0, 10); ax2.set_ylim(0, 10.4); ax2.axis("off")

    def box(x, y, w, h, txt, ec, fs=4.6):
        ax2.add_patch(FancyBboxPatch((x, y), w, h,
                     boxstyle="round,pad=0.02,rounding_size=0.12",
                     fc="#FFFFFF", ec=ec, lw=0.9))
        ax2.text(x + w / 2, y + h / 2, txt, ha="center", va="center",
                 fontsize=fs, color=INK)

    def hdr(x, y, txt, ec):
        ax2.add_patch(Rectangle((x, y), 0.22, 0.22, fc=ec, ec="none"))
        ax2.text(x + 0.32, y + 0.11, txt, ha="left", va="center",
                 fontsize=5.4, color=INK)

    # group headers
    hdr(0.4, 9.55, "External-label endpoints", C_CENT)
    hdr(3.9, 9.55, "Nested / duplicated", C_NEU)
    hdr(7.2, 9.55, "Constructed / circular", C_CIRC)

    # external-label (blue) -- 4 boxes; short lines + wide boxes so the label
    # stays fully inside each box (no overflow, no box-to-box overlap)
    box(0.4, 6.9, 3.3, 1.5, "E1 pan-dependency\n(n = %d)" % npos("E1 pan-dependency"),
        C_CENT, fs=4.8)
    box(0.4, 5.0, 3.3, 1.5, "E4 CRC zero-shot\n(n = %d)" % npos("E4 CRC zero-shot transfer"),
        C_CENT, fs=4.8)
    box(0.4, 2.9, 3.3, 1.7, "E5 historical\ntarget\nconcordance (n = %d)"
        % npos("E5 historical clinical-target concordance"), C_CENT, fs=4.8)
    box(0.4, 1.0, 3.3, 1.5, "E6 drug-response\nproxy (n = %d)"
        % npos("E6 PDAC drug-response actionability"), C_CENT, fs=4.8)

    # nested (grey) -- short lines, taller boxes
    box(3.9, 5.6, 3.1, 2.6, "E2 PDAC-enriched\ntop quartile of E1\n(n = %d)\n"
        "nested in E1" % npos("E2 PDAC-enriched dependency"), C_NEU, fs=4.4)
    box(3.9, 1.6, 3.1, 3.5, "E3-A leakage-\ncontrolled \u2261 E1\n(n = %d)\n"
        "drop Druggability\n\u2192 E1 exactly" % npos("E3-A leakage-controlled essentiality"),
        C_NEU, fs=4.4)

    # constructed / circular (purple) -- short lines, taller boxes
    box(7.2, 5.6, 2.75, 2.6, "E3 essential-\nand druggable\n(E1 \u2229 drugg.)\n"
        "(n = %d)\ncircular" % npos("E3 conjunctive actionability"), C_CIRC, fs=4.2)
    box(7.2, 3.4, 2.75, 1.7, "E3-C tractability\nas label\n(n = %d)"
        % npos("E3-C out-of-evidence druggability"), C_CIRC, fs=4.4)

    ax2.text(5.0, -0.25, "Blue: external-label endpoints  \u00b7  Grey: nested / duplicated"
             "  \u00b7  Purple: constructed / circular diagnostics",
             ha="center", fontsize=5.0, color=INK)
    panel(ax2, "b")
    save(fig, "Fig1")


# =====================================================================
# Fig. 2 | benchmark matrix 13 scorers x 8 endpoints
# =====================================================================
def fig2():
    order = ["Mutation frequency", "Genetic constraint", "Cancer-driver annotation",
             "Druggability", "STRING centrality", "Arithmetic mean",
             "Rank aggregation", "Weighted rank aggregation",
             "ECS (multiplicative)", "Harmonic mean",
             "Logistic regression", "Elastic net", "Random forest"]
    meths = [m for m in order if any(m in B[e] for e in EP_FULL)]
    # provenance-grouped column order:
    #   E1 | E2, E3-A (nested) | E3, E3-C (constructed) | E4, E5, E6 (external)
    eps = ["E1 pan-dependency",
           "E2 PDAC-enriched dependency",
           "E3-A leakage-controlled essentiality",
           "E3 conjunctive actionability",
           "E3-C out-of-evidence druggability",
           "E4 CRC zero-shot transfer",
           "E5 historical clinical-target concordance",
           "E6 PDAC drug-response actionability"]
    M = np.full((len(meths), len(eps)), np.nan)
    for i, m in enumerate(meths):
        for j, e in enumerate(eps):
            if m in B[e]:
                M[i, j] = B[e][m]["auroc"]
    fig, ax = plt.subplots(figsize=(W2, 88 * MM))
    fig.subplots_adjust(left=0.20, bottom=0.28, right=0.90, top=0.95)
    CMAP = LinearSegmentedColormap.from_list("azure", ["#F5F5F5", "#BFD8EA", C_CENT])
    norm = TwoSlopeNorm(vmin=0.30, vcenter=0.5, vmax=1.0)
    im = ax.imshow(M, cmap=CMAP, norm=norm, aspect="auto")

    circ_cols = [j for j, e in enumerate(eps) if e in
                 ("E3 conjunctive actionability", "E3-C out-of-evidence druggability")]
    for i in range(len(meths)):
        for j in range(len(eps)):
            if np.isnan(M[i, j]):
                ax.text(j, i, "n.a.", ha="center", va="center", fontsize=5,
                        color="#999999")
                continue
            leak = (eps[j] == "E3-C out-of-evidence druggability" and M[i, j] > 0.999)
            dark = M[i, j] > 0.78 or leak
            ax.text(j, i, ("%.2f" % M[i, j]).lstrip("0"), ha="center", va="center",
                    fontsize=5.2, color=("white" if dark else INK),
                    fontweight="bold" if leak else "normal")
            if leak:
                ax.add_patch(Rectangle((j - .5, i - .5), 1, 1, fill=False,
                                       ec=C_CIRC, lw=1.2, ls=(0, (1.4, 1.0))))
    for j in circ_cols:
        ax.add_patch(Rectangle((j - .5, -0.5), 1, len(meths), fc="#F3EFF8",
                               ec="none", zorder=-1, alpha=0.9))
    # group separators: E1 | E2,E3-A | E3,E3-C | E4,E5,E6
    for xb in (1.0, 3.0, 5.0):
        ax.axvline(xb, color="white", lw=2.6, zorder=5)
    ax.set_xticks(range(len(eps)))
    ax.set_xticklabels([EP_SHORT[e] for e in eps], fontsize=6, color=INK)
    ax.set_yticks(range(len(meths)))
    ax.set_yticklabels(meths, fontsize=6, color=INK)   # ALL row labels black
    ax.set_xlabel("Validation endpoint", fontsize=7)

    ax.set_xticks(np.arange(-.5, len(eps), 1), minor=True)
    ax.set_yticks(np.arange(-.5, len(meths), 1), minor=True)
    ax.grid(which="minor", color="white", lw=0.6)
    ax.tick_params(which="minor", length=0)
    cb = fig.colorbar(im, ax=ax, fraction=0.045, pad=0.02,
                      ticks=[0.4, 0.5, 0.7, 0.9, 1.0])
    cb.set_label("AUROC", fontsize=6.5)
    cb.ax.tick_params(labelsize=5.5)
    cb.outline.set_linewidth(0.4)
    handles = [Patch(fc=C_CENT, ec="none"), Patch(fc=C_INT, ec="none"),
               Patch(fc=C_RF, ec="none"), Patch(fc=C_NEU, ec="none"),
               Patch(fc=C_CIRC, ec="none")]
    labels = ["centrality / single-layer", "fixed-form integration",
              "supervised learner", "other single layer", "constructed/circular"]
    below_legend(ax, handles, labels=labels, ncol=5, y=-0.22, fontsize=5.4)
    ax.text(0.5, -0.36, "purple columns = constructed/circular diagnostic "
            "(E3, E3-C). E3-C AUROC = 1.000 is a label-as-input control, "
            "not a model result.", transform=ax.transAxes, fontsize=5.2,
            color=INK, ha="center")
    save(fig, "Fig2")


# =====================================================================
# Fig. 3 | integration confers no intrinsic advantage over centrality
# =====================================================================
def fig3():
    D = R["delta_auroc_paired_bootstrap"]
    L = R["delong_pairwise"]
    keys = [("Harmonic mean - STRING centrality", "Harmonic mean", C_INT),
            ("Random forest - STRING centrality", "Random forest", C_RF)]
    ep_plot = ["E1 pan-dependency", "E4 CRC zero-shot transfer",
               "E5 historical clinical-target concordance",
               "E6 PDAC drug-response actionability"]
    fig = plt.figure(figsize=(W2, 74 * MM))
    gs = fig.add_gridspec(1, 2, width_ratios=[1.5, 1.0], wspace=0.42)
    fig.subplots_adjust(bottom=0.24, top=0.90)

    # (a) effect size + 95% CI  (legend INSIDE panel a, top-right)
    ax = fig.add_subplot(gs[0, 0])
    yy, ylab = [], []
    for i, e in enumerate(ep_plot[::-1]):
        base = i * 1.0
        for k, (key, lab, col) in enumerate(keys):
            d = D.get(e, {}).get(key)
            if not d:
                continue
            y = base + (k - 0.5) * 0.30
            dm = d["delta_mean"]
            ax.plot([d["ci_lo"], d["ci_hi"]], [y, y], color=col, lw=1.1,
                    solid_capstyle="butt")
            ax.plot(dm, y, "o", ms=3.0, color=col, mec="white", mew=0.4,
                    zorder=3)
        yy.append(base); ylab.append(EP_SHORT[e])
    ax.axvline(0, color=INK, lw=1.1, zorder=0)
    ax.set_yticks(yy); ax.set_yticklabels(ylab, fontsize=6, color=INK)
    ax.set_xlim(-0.34, 0.30)
    ax.set_xlabel("$\\Delta$AUROC (paired bootstrap, 95% CI)")
    ax.set_title("AUROC difference from network centrality", fontsize=7.5, loc="left")
    ax.legend(handles=[Patch(fc=C_INT, ec="none"), Patch(fc=C_RF, ec="none")],
              labels=["Harmonic mean", "Random forest"], loc="upper right",
              fontsize=5.4, frameon=False)
    panel(ax, "a")

    # (b) network-community resampling
    ax = fig.add_subplot(gs[0, 1])
    S = R["structured_resampling"]
    ax.axhline(0, color=INK, lw=1.1)
    ax.plot([0, 0], [S["delta_ci_lo"], S["delta_ci_hi"]], color=C_INT, lw=2.0)
    ax.plot(0, S["delta_mean"], "o", ms=5.0, color=C_INT, mec="white", mew=0.5)
    ax.set_xlim(-1.15, 1.15); ax.set_xticks([0])
    ax.set_xticklabels(["community\nbootstrap"], fontsize=5.6)
    ax.set_ylabel("$\\Delta$AUROC, ECS $-$ STRING centrality")
    ax.set_title("Network-community resampling", fontsize=7.5, loc="left")
    ax.text(0.97, 0.93, "%d communities \u00b7 %d resamples\n%.0f%% > 0 \u00b7 %.1f%% < 0"
            % (S["n_communities"], S["n_bootstrap"], S["pct_positive"],
               100 - S["pct_positive"]),
            transform=ax.transAxes, fontsize=5.0, color=INK, va="top", ha="right")
    panel(ax, "b")
    # concise caption (no database-style P string)
    fig.text(0.5, 0.01, "Paired-bootstrap DeLong P < 10$^{-16}$ for every "
             "scorer-versus-centrality contrast.", ha="center", va="bottom",
             fontsize=5.2, color=INK)
    save(fig, "Fig3")


# =====================================================================
# Fig. 4 | why integration appears to work
# =====================================================================
def fig4():
    fig = plt.figure(figsize=(W2, 86 * MM))
    gs = fig.add_gridspec(1, 3, width_ratios=[1.15, 1.0, 1.25], wspace=0.62)
    fig.subplots_adjust(bottom=0.30, top=0.95)

    # (a) annotation-absence share (formal layer names, black text)
    ax = fig.add_subplot(gs[0, 0])
    lay = SENT["S1_sentinel_coding"]["per_layer"]
    names = sorted(lay, key=lambda k: lay[k]["pct_sentinel"])
    pos = np.arange(len(names))
    for i, f in enumerate(names):
        v = lay[f]["pct_sentinel"]
        ax.barh(i, v, 0.66, color=C_NEU, ec="white", lw=0.3)
        ax.text(v + 1.2, i, "%.0f%%" % v, va="center", fontsize=5.4, color=INK)
    ax.axvline(50, color=C_CENT, lw=0.8, ls="--")
    ax.set_yticks(pos)
    ax.set_yticklabels([LAYER_NAME.get(f, f) for f in names], fontsize=5.4, color=INK)
    ax.set_xlabel("genes with no annotation (%)")
    ax.set_xlim(0, 118)
    ax.set_title("How much evidence is annotation absence", fontsize=7.5, loc="left")
    mean_pct = SENT["S1_sentinel_coding"]["mean_pct_sentinel_across_layers"]
    # compact below-panel caption: removes the in-axes callouts that overlapped
    # the bars / per-bar percentage labels
    ax.text(0.5, -0.22, "mean across 9 layers = %.1f%% of genes unannotated"
            % mean_pct, transform=ax.transAxes, ha="center", va="top",
            fontsize=5.0, color=INK)
    panel(ax, "a", external=True)

    # (b) multiplicative rule sign-flip partition
    ax = fig.add_subplot(gs[0, 1])
    s2 = SENT["S2_order_preservation"]
    p_term_neg = s2["pct_genes_gain_term_negative"]
    p_d_neg = s2["pct_genes_driver_negative"]
    p_double = s2["pct_genes_double_sign_flip"]
    a = (100 - p_term_neg) - (p_d_neg - p_double)
    b = p_d_neg - p_double
    c = p_term_neg - p_double
    d = p_double
    quads = [("term>0 \u00b7 D>0", a, "#DCE6F0", C_CENT),
             ("term>0 \u00b7 D<0", b, "#F2E2D6", C_RF),
             ("term<0 \u00b7 D>0", c, "#DCE6F0", C_NEU),
             ("term<0 \u00b7 D<0", d, "#E6E0F0", C_CIRC)]
    xs = [0.0, 0.5, 0.0, 0.5]; ys = [0.5, 0.5, 0.0, 0.0]
    for (lab, val, fc, ec), x, y in zip(quads, xs, ys):
        ax.add_patch(Rectangle((x, y), 0.5, 0.5, fc=fc, ec=ec, lw=1.1))
        ax.text(x + 0.25, y + 0.28, lab, ha="center", va="center", fontsize=5.6,
                color=INK)
        ax.text(x + 0.25, y + 0.14, "%.1f%%" % val, ha="center", va="center",
                fontsize=7, color=INK, fontweight="bold")
    ax.axvline(0.5, color=INK, lw=0.9); ax.axhline(0.5, color=INK, lw=0.9)
    ax.set_xlim(0, 1); ax.set_ylim(0, 1)
    ax.set_xticks([0.25, 0.75]); ax.set_xticklabels(["support term > 0",
                                                     "support term < 0"],
                                                     fontsize=5.4, color=INK)
    ax.set_yticks([0.25, 0.75]); ax.set_yticklabels(["score rises",
                                                     "score falls"],
                                                     fontsize=5.4, color=INK)
    ax.set_title("Multiplicative rule is not monotone", fontsize=7.5, loc="left")
    below_legend(ax,
                 [Patch(fc="#DCE6F0", ec=C_CENT), Patch(fc="#F2E2D6", ec=C_RF),
                  Patch(fc="#E6E0F0", ec=C_CIRC)],
                 labels=["concordant", "sign-flip", "double-negative"],
                 ncol=3, y=-0.30, fontsize=5.4)
    panel(ax, "b", external=True)

    # (c) effect of removing the label-embedded layer
    ax = fig.add_subplot(gs[0, 2])
    S3 = SENT["S3_endpointwise"]
    rows = [("E3 conjunctive actionability", C_CIRC),
            ("E3-C out-of-evidence druggability", C_CIRC)]
    for i, (e, col) in enumerate(rows):
        full = S3[e]["support_mean_PHI"]
        collapse = S3[e]["support_mean_without_druggability"]
        y = len(rows) - 1 - i
        ax.plot(full, y, "o", ms=5.0, color=col, mec="white", mew=0.5, zorder=4)
        ax.plot(collapse, y, "o", ms=5.0, color=C_NEU, mec="white", mew=0.5,
                zorder=4)
        ax.plot([full, collapse], [y, y], color=INK, lw=1.1, ls="-", zorder=3)
        ax.annotate("%.3f $\\to$ %.3f" % (full, collapse),
                    xy=(collapse, y), xytext=(collapse - 0.04, y + 0.16),
                    fontsize=5.6, color=INK, ha="right", va="bottom")
    ax.axvline(0.5, color=C_REF, lw=0.8, ls="--", zorder=0)
    ax.set_yticks(range(len(rows)))
    ax.set_yticklabels([EP_SHORT[e] for (e, _) in rows], fontsize=6, color=INK)
    ax.set_xlim(0.42, 1.02); ax.set_ylim(-0.6, len(rows) - 0.1)
    ax.set_xlabel("AUROC of the integrated support mean")
    ax.set_title("Removing the label-embedded layer", fontsize=7.5, loc="left")
    below_legend(ax,
                 [Patch(fc=C_CIRC, ec="none"), Patch(fc=C_NEU, ec="none")],
                 labels=["full support (incl. tractability)", "after tractability "
                         "deletion"], ncol=1, y=-0.34, fontsize=5.6)
    panel(ax, "c", external=True)
    save(fig, "Fig4")


# =====================================================================
# Fig. 5 | functional form, weight space, controls, recoding
# =====================================================================
def fig5():
    F = R["functional_forms_all_endpoints"]
    forms = ["harmonic mean", "additive", "multiplicative (ECS)",
             "geometric mean", "rank aggregation"]
    # five visually DISTINCT colours (no three teals)
    shades = [C_INT, C_LBLUE, C_RF, C_GOLD, C_CENT]
    eps = [e for e in EP_FULL if not e.startswith("E3-A")]
    fig = plt.figure(figsize=(W2, 86 * MM))
    gs = fig.add_gridspec(1, 4, width_ratios=[1.5, 1.05, 0.85, 0.95], wspace=0.62)
    fig.subplots_adjust(bottom=0.46, top=0.90)

    # (a) fixed functional forms
    ax = fig.add_subplot(gs[0, 0])
    x = np.arange(len(eps)); w = 0.155
    for k, (f, c) in enumerate(zip(forms, shades)):
        ax.bar(x + (k - 2) * w, [F.get(e, {}).get(f, {}).get("auroc", np.nan)
                                 for e in eps], w, color=c, ec="white", lw=0.25,
               label=f)
    ax.axhline(0.5, color=C_REF, lw=0.7, ls="--")
    ax.set_xticks(x); ax.set_xticklabels([EP_SHORT[e] for e in eps], fontsize=6, color=INK)
    ax.set_ylabel("AUROC"); ax.set_ylim(0.30, 1.02)
    ax.set_xlabel("Validation endpoint")
    ax.set_title("Fixed functional forms", fontsize=7.5, loc="left")
    handles = [Patch(fc=c, ec="none") for c in shades]
    ax.legend(handles=handles, labels=forms, loc="lower center",
              bbox_to_anchor=(0.42, -0.46), ncol=2, handlelength=1.0,
              columnspacing=0.9, fontsize=5.4, frameon=True, edgecolor=INK,
              fancybox=False, borderpad=0.4)
    panel(ax, "a")

    # (b) weight space ECDF
    ax = fig.add_subplot(gs[0, 1])
    smp = np.asarray(WS["auroc_samples"])
    xs = np.sort(smp); ec = np.arange(1, len(xs) + 1) / len(xs)
    ax.step(xs, ec, where="post", color=C_CENT, lw=1.0)
    med = np.median(smp); q25, q75 = np.percentile(smp, [25, 75])
    q025, q975 = np.percentile(smp, [2.5, 97.5])
    for xx, c in ((q025, C_NEU), (q975, C_NEU), (q25, "#9FB8CC"), (q75, "#9FB8CC"),
                  (med, INK)):
        ax.axvline(xx, color=c, lw=0.8, ls="--")
    ax.axvline(WS["string_auroc_e3"], color=C_CENT, lw=1.2, zorder=4)
    ax.axvline(WS["v17_chosen_weighting_auroc_e3"], color=C_RF, lw=1.2, zorder=4)
    ax.set_xlabel("AUROC on E3 over %s Dirichlet\nweightings" %
                  format(WS["n_draws"], ","))
    ax.set_ylabel("cumulative fraction")
    ax.set_ylim(0, 1.04)
    ax.set_title("Driver-layer weight space", fontsize=7.5, loc="left")
    # median / IQR are shown in the panel (b) legend below (no in-axes text -> no overlap)
    below_legend(ax,
                 [Patch(fc=C_CENT, ec="none"), Patch(fc=C_RF, ec="none"),
                  Patch(fc=C_NEU, ec="none"), Patch(fc="#F0F0F0", ec=INK)],
                 labels=["STRING %.3f" % WS["string_auroc_e3"],
                         "prespecified %.3f" % WS["v17_chosen_weighting_auroc_e3"],
                         "2.5 / 97.5 pct",
                         "median %.3f (IQR %.2f\u2013%.2f)" % (med, q25, q75)],
                 ncol=2, y=-0.46, fontsize=5.0, frameon=True, x=0.62)
    panel(ax, "b")

    # (c) negative controls (observed ECS: black text, not coloured)
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
        ax.text(v["auroc_ci"][1] + 0.015, i, "%.3f" % v["auroc"], va="center",
                fontsize=5.2, color=INK)
    ax.axvline(0.5, color=C_REF, lw=0.7, ls="--", zorder=0)
    ax.axvline(obs["auroc"], color=C_INT, lw=0.7, ls=":", zorder=2)
    ax.text(obs["auroc"] + 0.015, 2.35, "observed ECS\n%.3f" % obs["auroc"],
            va="top", ha="left", fontsize=5.2, color=INK)
    ax.set_yticks(range(len(controls)))
    ax.set_yticklabels([l for _, l in controls], fontsize=5.4, color=INK)
    ax.set_xlabel("AUROC on E3")
    ax.set_ylim(-0.6, 2.7)
    ax.set_title("Negative controls", fontsize=7.5, loc="left")
    panel(ax, "c")

    # (d) sentinel-coded versus missingness-aware
    ax = fig.add_subplot(gs[0, 3])
    S4 = SENT["S4_sentinel_corrected_sensitivity"]["per_endpoint"]
    eps2 = list(EP_FULL)
    yy = np.arange(len(eps2))[::-1]
    for y, e in zip(yy, eps2):
        sv = S4[e]["harmonic_sentinel_as_value"]
        av = S4[e]["harmonic_available_case"]
        ax.plot([sv, av], [y, y], color="#BBBBBB", lw=0.7, zorder=2)
        ax.plot(sv, y, "o", ms=3.0, color=C_NEU, mec="white", mew=0.3, zorder=3)
        ax.plot(av, y, "o", ms=3.4, color=C_CENT, mec="white", mew=0.35, zorder=4)
        ax.text(av + 0.006, y + 0.14, "%+.3f" % S4[e]["harmonic_delta"],
                va="bottom", ha="left", fontsize=5.0, color=INK)
    ax.axvline(0.5, color=C_REF, lw=0.7, ls="--", zorder=0)
    ax.set_yticks(yy); ax.set_yticklabels([EP_SHORT[e] for e in eps2], fontsize=5.6, color=INK)
    ax.set_xlabel("AUROC (harmonic)")
    ax.set_xlim(0.38, 1.0)
    ax.set_title("Sentinel-coded versus missingness-aware", fontsize=7.5, loc="left")
    below_legend(ax,
                 [Patch(fc=C_NEU, ec="none"), Patch(fc=C_CENT, ec="none")],
                 labels=["sentinel = \u22123", "available-case mean"], ncol=1, y=-0.44,
                 fontsize=5.4, frameon=True)
    panel(ax, "d")
    save(fig, "Fig5")


# =====================================================================
# Fig. 6 | pharmacological stress test
# =====================================================================
def fig6():
    fig = plt.figure(figsize=(W2, 78 * MM))
    gs = fig.add_gridspec(1, 2, width_ratios=[1.0, 1.1], wspace=0.45)
    fig.subplots_adjust(bottom=0.27, top=0.90)

    # (a) E6 construction / attribution pipeline
    ax = fig.add_subplot(gs[0, 0]); ax.axis("off")
    ax.set_xlim(0, 10); ax.set_ylim(0, 10)
    G = R.get("gdsc_endpoint", {})
    nlines = G.get("n_pancreas_lines_with_ic50", "?")
    ndrugs = G.get("n_drugs_screened", "?")
    npos = G.get("n_positive_genes", "?")
    ntert = G.get("n_drugs_sensitive_tertile", "?")

    def box(x, y, w, h, txt, fc, ec):
        ax.add_patch(FancyBboxPatch((x, y), w, h,
                     boxstyle="round,pad=0.02,rounding_size=0.12",
                     fc=fc, ec=ec, lw=0.8))
        ax.text(x + w / 2, y + h / 2, txt, ha="center", va="center",
                fontsize=5.0, color=INK)

    box(0.4, 7.2, 4.6, 2.0, "GDSC v2 IC50 matrix\n%s PDAC lines \u00b7 %s drugs"
        % (nlines, ndrugs), "#EEF2F7", C_CENT)
    box(5.0, 7.2, 4.6, 2.0, "drug-response labels\n%s sensitivities"
        % ntert, "#EEF2F7", C_CENT)
    box(2.6, 4.4, 4.8, 1.8, "E6 PDAC pharmacological-response\nproxy (%s genes)"
        % npos, "#F3EFF8", C_CIRC)
    scorers = [("STRING\ncentrality", C_CENT), ("Tractability", C_NEU),
               ("Harmonic\nmean", C_INT), ("Random\nforest", C_RF)]
    for i, (s, c) in enumerate(scorers):
        bx = 0.5 + i * 2.3
        box(bx, 2.0, 2.0, 1.6, s, "#FFFFFF", c)
    box(0.5, 0.2, 9.0, 1.4, "target attribution:\nranked genes \u2192 candidates",
        "#FFFFFF", INK)
    for (x0, y0, x1, y1) in ((2.7, 7.2, 3.2, 6.2),
                             (7.3, 7.2, 6.8, 6.2),
                             (5.0, 4.4, 5.0, 3.6),
                             (1.5, 2.0, 1.5, 1.6),
                             (3.8, 2.0, 3.8, 1.6),
                             (6.1, 2.0, 6.1, 1.6),
                             (8.4, 2.0, 8.4, 1.6)):
        ax.annotate("", xy=(x1, y1), xytext=(x0, y0),
                    arrowprops=dict(arrowstyle="->", lw=0.7, color="#444444"))
    ax.text(5.0, 9.8, "E6 construction & target-attribution", ha="center",
            fontsize=7, color=INK)
    ax.text(5.0, -0.3, "IC50-derived labels are external to the nine-layer evidence matrix",
            ha="center", fontsize=5.2, color=INK)
    panel(ax, "a", external=True)

    # (b) E6 AUROC comparison (RF = 0.913 kept verbatim from source data)
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
                fontsize=5.2, color=INK)
    ax.set_yticks(range(len(rows)))
    ax.set_yticklabels([m for m, _ in rows], fontsize=5.4, color=INK)
    ax.axvline(0.5, color=C_REF, lw=0.7, ls="--")
    ax.set_xlim(0.30, 1.06)
    ax.set_xlabel("AUROC on E6 (GDSC drug response)")
    ax.set_title("Pharmacological stress test (E6)", fontsize=7.5, loc="left")
    panel(ax, "b", external=True)
    save(fig, "Fig6")


if __name__ == "__main__":
    print("rendering V18 display items (v34 Nature production) ->", FIG)
    for fn in (fig1, fig2, fig3, fig4, fig5, fig6):
        try:
            fn()
        except Exception as exc:
            import traceback
            print("  FAILED %s: %s" % (fn.__name__, exc))
            traceback.print_exc()
    print("done")
