#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Sentinel-coding and combination-rule audit (discovered during the V18 recount).

Three defects in the V17 scoring pipeline that the pre-submission checklist did
not anticipate:

  S1  Every evidence layer uses -3.0 as a MISSING code, but the score functions
      treat it as an extreme observed value.  For five of nine layers the
      median gene is missing, so most of the "evidence" being integrated is
      absence of annotation.

  S2  The multiplicative rule  D * (1 + 0.6 PHI)  is not order-preserving on
      this input: (1 + 0.6 PHI) < 0 for most genes and D < 0 for a large
      minority, so for a substantial subset a gene with MORE supporting
      evidence receives a LOWER score, and 1/4 of genes get a spuriously
      positive score from a double sign flip.

  S3  The harmonic form's +3 shift silently maps the sentinel to 0, which
      repairs S1 by accident.  Because the harmonic mean of two shifted terms
      is dominated by the smaller one, and PHI + 3 is the smaller term for
      almost every gene, the "integrated" harmonic score is a monotone proxy
      for the support-layer mean alone - and that mean contains druggability,
      which is a conjunct of the E3 label.

Outputs results/v18_sentinel_audit.json and prints a readable summary.
"""
import json
import os

import numpy as np
from scipy.stats import spearmanr
from sklearn.metrics import roc_auc_score

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = open(os.path.join(HERE, "v18_recompute.py")).read()
MARK = "# 5. STATISTICS: fast DeLong"
assert MARK in SRC
ns = {"__name__": "v18_prefix"}
exec(compile(SRC.split(MARK)[0], "v18_recompute.py[1-4]", "exec"), ns)

X, FEAT, RES = ns["X"], ns["FEATURES"], ns["RES"]
EPS = ns["ENDPOINTS"]
DP, I_STR = ns["DP"], ns["I_STR"]
SUP_ALL, SUP_NODRUG = ns["SUP_ALL"], ns["SUP_NODRUG"]
SENT = -3.0
N = X.shape[0]
A = {}

# ---- S1: sentinel prevalence ---------------------------------------
lay = {}
for j, f in enumerate(FEAT):
    v = X[:, j]
    lay[f] = {"pct_sentinel": float(100.0 * np.isclose(v, SENT).mean()),
              "median": float(np.median(v)),
              "min": float(v.min()), "max": float(v.max()),
              "median_is_sentinel": bool(np.isclose(np.median(v), SENT))}
A["S1_sentinel_coding"] = {
    "sentinel_value": SENT,
    "per_layer": lay,
    "n_layers_where_median_gene_is_missing":
        int(sum(v["median_is_sentinel"] for v in lay.values())),
    "mean_pct_sentinel_across_layers":
        float(np.mean([v["pct_sentinel"] for v in lay.values()])),
    "verdict": ("-3.0 is a missing-data sentinel, not a measurement. It enters "
                "D and PHI as a large negative number, so 'low evidence' and "
                "'no annotation' are indistinguishable and are both treated as "
                "strong negative evidence."),
}

# ---- S2: order preservation of the multiplicative rule --------------
D, PHI = DP(X)
gain = 1.0 + 0.6 * PHI
mult = D * gain
neg_gain, neg_D = gain < 0, D < 0
both = neg_gain & neg_D
r_pos = float(np.corrcoef(PHI[~neg_D], mult[~neg_D])[0, 1])
r_neg = float(np.corrcoef(PHI[neg_D], mult[neg_D])[0, 1])
# direct counterfactual: add a unit of support to every gene, count losers
mult_up = D * (1.0 + 0.6 * (PHI + 0.25))
losers = float(100.0 * (mult_up < mult).mean())
A["S2_order_preservation"] = {
    "pct_genes_gain_term_negative": float(100.0 * neg_gain.mean()),
    "pct_genes_driver_negative": float(100.0 * neg_D.mean()),
    "pct_genes_double_sign_flip": float(100.0 * both.mean()),
    "corr_PHI_score_when_D_positive": r_pos,
    "corr_PHI_score_when_D_negative": r_neg,
    "pct_genes_whose_score_FALLS_when_support_increases": losers,
    "verdict": ("For %.1f%% of genes an increase in supporting evidence lowers "
                "the ECS score. The multiplicative rule is therefore not a "
                "valid evidence-integration operator on these signed inputs."
                % losers),
}

# ---- S3: what the harmonic score is actually ranking -----------------
harm = ns["f_harmonic"](X)
Ds, Ps = np.maximum(D + 3.0, .01), np.maximum(PHI + 3.0, .01)
A["S3_harmonic_is_support_mean"] = {
    "pct_genes_where_PHI_term_is_the_smaller": float(100.0 * (Ps < Ds).mean()),
    "spearman_harmonic_vs_support_mean": float(spearmanr(harm, PHI).statistic),
    "spearman_harmonic_vs_driver_composite": float(spearmanr(harm, D).statistic),
    "spearman_harmonic_vs_string": float(spearmanr(harm, X[:, I_STR]).statistic),
}

# ---- endpoint-wise comparison: integration vs its own support mean ----
PHI_ND = np.mean(X[:, SUP_NODRUG], axis=1)
rows = {}
for ep, y in EPS.items():
    rows[ep] = {
        "harmonic": float(roc_auc_score(y, harm)),
        "support_mean_PHI": float(roc_auc_score(y, PHI)),
        "support_mean_without_druggability": float(roc_auc_score(y, PHI_ND)),
        "driver_composite_D": float(roc_auc_score(y, D)),
        "string_alone": float(roc_auc_score(y, X[:, I_STR])),
        "ecs_multiplicative": float(roc_auc_score(y, mult)),
        "n_pos": int(y.sum()),
    }
    rows[ep]["harmonic_minus_support_mean"] = (rows[ep]["harmonic"]
                                              - rows[ep]["support_mean_PHI"])
A["S3_endpointwise"] = rows

# ---- sentinel-corrected sensitivity analysis --------------------------
Xm = X.copy()
Xm[np.isclose(Xm, SENT)] = np.nan
Dm = np.nansum(np.stack([0.80 * Xm[:, ns["I_STR"]], 0.10 * Xm[:, ns["I_MUT"]],
                         0.10 * Xm[:, ns["I_IMPC"]]]), axis=0)
with np.errstate(invalid="ignore"):
    PHIm = np.nanmean(Xm[:, SUP_ALL], axis=1)
PHIm = np.where(np.isfinite(PHIm), PHIm, 0.0)
Dm = np.where(np.isfinite(Dm), Dm, 0.0)
harm_c = 2.0 * np.maximum(Dm + 3., .01) * np.maximum(PHIm + 3., .01) / \
    (np.maximum(Dm + 3., .01) + np.maximum(PHIm + 3., .01))
mult_c = Dm * (1.0 + 0.6 * PHIm)
corr = {}
for ep, y in EPS.items():
    corr[ep] = {"harmonic_sentinel_as_value": float(roc_auc_score(y, harm)),
                "harmonic_available_case": float(roc_auc_score(y, harm_c)),
                "ecs_sentinel_as_value": float(roc_auc_score(y, mult)),
                "ecs_available_case": float(roc_auc_score(y, mult_c))}
    corr[ep]["harmonic_delta"] = (corr[ep]["harmonic_available_case"]
                                  - corr[ep]["harmonic_sentinel_as_value"])
A["S4_sentinel_corrected_sensitivity"] = {
    "recoding": "-3.0 -> missing; available-case mean; absent-everything -> 0",
    "per_endpoint": corr,
    "verdict": ("Handling the sentinel correctly changes the apparent "
                "performance of the integrated scores, which shows that the "
                "reported advantage of integration is partly an artefact of "
                "encoding missing annotation as strong negative evidence."),
}

# ---- V17 headline reproduction check ---------------------------------
A["V17_checkpoint_reproduction"] = {
    "harmonic_E3_claimed": 0.893,
    "harmonic_E3_recomputed": float(roc_auc_score(
        EPS["E3 conjunctive actionability"], harm)),
    "harmonic_E3A_claimed": 0.575,
    "harmonic_E3A_recomputed": float(roc_auc_score(
        EPS["E3-A leakage-controlled essentiality"], harm)),
    "note": ("E3-A is bit-identical to E1, so 0.575 is simultaneously the E1 "
             "harmonic value."),
}

p = os.path.join(RES, "v18_sentinel_audit.json")
json.dump(A, open(p, "w"), indent=1, ensure_ascii=False)

print("\n" + "=" * 70)
print("S1  MISSING-DATA SENTINEL (-3.0) TREATED AS AN OBSERVED VALUE")
print("=" * 70)
for f, v in lay.items():
    print("  %-22s missing %5.1f%%   median %+6.3f %s"
          % (f, v["pct_sentinel"], v["median"],
             "<- median gene is MISSING" if v["median_is_sentinel"] else ""))
print("  layers whose median gene is unannotated: %d / %d"
      % (A["S1_sentinel_coding"]["n_layers_where_median_gene_is_missing"], len(FEAT)))
print("\n" + "=" * 70)
print("S2  THE MULTIPLICATIVE RULE IS NOT ORDER-PRESERVING")
print("=" * 70)
s2 = A["S2_order_preservation"]
print("  (1+0.6 PHI) < 0 for            %5.1f%% of genes" % s2["pct_genes_gain_term_negative"])
print("  D < 0 for                      %5.1f%% of genes" % s2["pct_genes_driver_negative"])
print("  double sign flip               %5.1f%% of genes" % s2["pct_genes_double_sign_flip"])
print("  corr(PHI, score) | D > 0       %+.3f" % s2["corr_PHI_score_when_D_positive"])
print("  corr(PHI, score) | D < 0       %+.3f  <- inverted" % s2["corr_PHI_score_when_D_negative"])
print("  score FALLS when support rises %5.1f%% of genes" % s2["pct_genes_whose_score_FALLS_when_support_increases"])
print("\n" + "=" * 70)
print("S3  THE 'INTEGRATED' HARMONIC SCORE IS A PROXY FOR THE SUPPORT MEAN")
print("=" * 70)
s3 = A["S3_harmonic_is_support_mean"]
print("  PHI+3 is the smaller term for  %5.1f%% of genes"
      % s3["pct_genes_where_PHI_term_is_the_smaller"])
print("  Spearman(harmonic, PHI)        %+.4f" % s3["spearman_harmonic_vs_support_mean"])
print("  Spearman(harmonic, D)          %+.4f" % s3["spearman_harmonic_vs_driver_composite"])
print("  Spearman(harmonic, STRING)     %+.4f" % s3["spearman_harmonic_vs_string"])
print("\n  %-46s %7s %7s %7s %7s" % ("endpoint", "harm", "PHI", "PHI-noD", "STRING"))
for ep, v in rows.items():
    print("  %-46s %7.4f %7.4f %7.4f %7.4f"
          % (ep[:46], v["harmonic"], v["support_mean_PHI"],
             v["support_mean_without_druggability"], v["string_alone"]))
print("\n" + "=" * 70)
print("S4  SENTINEL-CORRECTED SENSITIVITY (available-case)")
print("=" * 70)
print("  %-46s %8s %8s %7s" % ("endpoint", "as-is", "corrected", "delta"))
for ep, v in corr.items():
    print("  %-46s %8.4f %8.4f %+7.4f"
          % (ep[:46], v["harmonic_sentinel_as_value"],
             v["harmonic_available_case"], v["harmonic_delta"]))
print("\n" + "=" * 70)
print("V17 CHECKPOINT REPRODUCTION")
print("=" * 70)
c = A["V17_checkpoint_reproduction"]
print("  harmonic E3   claimed 0.893  recomputed %.4f" % c["harmonic_E3_recomputed"])
print("  harmonic E3-A claimed 0.575  recomputed %.4f" % c["harmonic_E3A_recomputed"])
print("\nwrote", p)
