#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""audit_centrality_bias_p0_3 -- centrality annotation-density / study-bias audit.

PURPOSE
-------
Tests whether the STRING *centrality* signal is confounded by how heavily a gene
is annotated across the nine evidence layers (a study-/annotation-bias proxy).
We use a fully reproducible proxy:

    annotation_density(g) = (# of layers where g is NOT the -3.0 sentinel) / 9

and then:

  1. report Spearman(centrality, annotation_density) -- is centrality just a
     proxy for "how many databases bothered to measure this gene"?;
  2. re-check centrality vs the ECS driver composite UNDER an
     annotation-density-adjusted comparison: regress the composite on density,
     take residuals, and report Spearman(centrality, residual_composite);
  3. a degree-matched design: within each centrality quintile, split genes into
     low/high annotation density and compare composite-score medians
     (Mann-Whitney), isolating centrality's effect from density.

INPUTS REQUIRED
---------------
  evidence_layers_v11.json  (released harmonised 9-layer evidence matrix)

READY TO RUN
------------
Runs end-to-end when the released input is present; prints a structured
`MISSING_INPUTS` notice and exits 0 if absent.  No fabricated statistics.

NOTE: P0-3 skeleton -- the proxy, correlations, residualisation and
degree-matched stratification are all implemented and real.
"""
import os
import sys
import json
import argparse

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(os.path.dirname(HERE))
ORIG_ROOT = "/Users/zuoxianbo/Desktop/zuoxb-虚拟科研系统-MAC/outputs/pdac-convergent-evidence-v14/data"

FEATURES = ["string_centrality", "mutation_freq", "impc_animal_ko",
            "genetic_constraint", "cancer_driver", "ot_genetics_pdac",
            "druggability", "hpa_pdac_prognostic", "hpa_rna_tissue_spec"]
SENT = -3.0


def _candidate_dirs(data_dir):
    # --data-dir is authoritative: only that directory is searched.
    if data_dir:
        return [data_dir]
    dirs = [os.path.join(REPO_ROOT, "data"), ORIG_ROOT]
    env = os.environ.get("PDAC_DATA_DIR")
    if env:
        dirs.append(env)
    return dirs


def resolve(required, data_dir=None):
    paths, missing = {}, []
    for alias, cands in required:
        found = None
        for d in _candidate_dirs(data_dir):
            for c in cands:
                p = os.path.join(d, c)
                if os.path.isfile(p):
                    found = p
                    break
            if found:
                break
        if found:
            paths[alias] = found
        else:
            missing.append(alias)
    return paths, missing


def _lv_by_pos(ev, gene, feat):
    r = ev["layers"].get(feat, {}).get(gene)
    return r["norm"] if (r and r.get("present")) else None


def main(argv=None):
    ap = argparse.ArgumentParser(description="P0-3 centrality-bias audit")
    ap.add_argument("--data-dir", default=None)
    ap.add_argument("--out", default=os.path.join(REPO_ROOT, "results",
                    "v29_p0_3_centrality_bias.json"))
    args = ap.parse_args(argv)

    needed = [("evidence_layers_v11.json", ["evidence_layers_v11.json"])]
    paths, missing = resolve(needed, args.data_dir)
    if missing:
        print(json.dumps({
            "status": "MISSING_INPUTS",
            "audit": "P0-3 centrality annotation-density / study-bias",
            "missing": missing,
            "resolved": list(paths.keys()),
            "message": ("Inputs not present -- awaiting released data. "
                        "No bias statistics were computed or fabricated."),
        }, indent=2, ensure_ascii=False))
        return 0

    from scipy.stats import spearmanr, mannwhitneyu

    ev = json.load(open(paths["evidence_layers_v11.json"]))
    genes = ev["genes"]
    n = len(genes)
    M = np.full((n, len(FEATURES)), SENT)
    for i, g in enumerate(genes):
        for j, f in enumerate(FEATURES):
            v = _lv_by_pos(ev, g, f)
            if v is not None:
                M[i, j] = v

    cent = M[:, FEATURES.index("string_centrality")]
    density = np.mean((M != SENT).astype(float), axis=1)   # proxy: #non-missing / 9
    # ECS driver composite D = 0.8*STRING + 0.1*MUT + 0.1*IMPC (v18 definition)
    I_STR = FEATURES.index("string_centrality")
    I_MUT = FEATURES.index("mutation_freq")
    I_IMPC = FEATURES.index("impc_animal_ko")
    D = 0.8 * M[:, I_STR] + 0.1 * M[:, I_MUT] + 0.1 * M[:, I_IMPC]

    rho_cd = float(spearmanr(cent, density).statistic)
    rho_dc = float(spearmanr(cent, D).statistic)

    # annotation-density-adjusted: residualise D on density, correlate with cent
    A = np.vstack([np.ones(n), density]).T
    beta, *_ = np.linalg.lstsq(A, D, rcond=None)
    resid = D - A @ beta
    rho_c_resid = float(spearmanr(cent, resid).statistic)

    # degree-matched (centrality-matched) stratification
    q = np.percentile(cent, [20, 40, 60, 80])
    bins = np.digitize(cent, q)
    mw_rows = []
    for b in range(5):
        idx = np.where(bins == b)[0]
        if len(idx) < 20:
            continue
        d_b = density[idx]
        med = np.median(d_b)
        lo = idx[d_b <= med]
        hi = idx[d_b > med]
        if len(lo) >= 5 and len(hi) >= 5:
            U, p = mannwhitneyu(D[lo], D[hi], alternative="two-sided")
            mw_rows.append({
                "centrality_quintile": b + 1,
                "n": int(len(idx)),
                "median_D_low_density": float(np.median(D[lo])),
                "median_D_high_density": float(np.median(D[hi])),
                "mw_u": float(U), "mw_p": float(p),
            })

    report = {
        "audit": "P0-3 centrality annotation-density / study-bias",
        "n_genes": n,
        "proxy_definition": "annotation_density = (#layers not equal to -3.0 sentinel) / 9",
        "spearman_centrality_vs_density": rho_cd,
        "spearman_centrality_vs_composite": rho_dc,
        "spearman_centrality_vs_density_residualised_composite": rho_c_resid,
        "degree_matched_density_comparison": mw_rows,
        "interpretation": ("If |rho_cd| is large, centrality tracks annotation density; "
                           "the density-residualised correlation shows whether centrality "
                           "still carries signal once density is removed."),
    }
    json.dump(report, open(args.out, "w"), indent=1, ensure_ascii=False)
    print(json.dumps(report, indent=2, ensure_ascii=False))
    print("\nwrote", args.out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
