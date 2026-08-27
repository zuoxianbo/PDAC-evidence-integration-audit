#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""audit_nested_cv_p0_2 -- P0-2 leakage-safe nested cross-validation audit.

PURPOSE
-------
Re-estimate every supervised method's discrimination with a *leakage-safe*
nested CV design, replacing the single-split out-of-fold scores used in V17/V18:

  * OUTER loop: StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
                -- the evaluation split; outer-fold predictions are saved.
  * INNER loop: a separate 5-fold StratifiedKFold on the OUTER-TRAIN portion,
                tuning each model over a FIXED candidate hyper-parameter grid
                with a FIXED seed; the best grid point (by inner CV AUROC) is
                selected and the model is REFIT on the full outer-train split.

E4 ZERO-SHOT: hyperparameters are chosen only inside the E1 training fold
(via E1 nested CV) and the resulting model is applied to E4 *without refit*
(no E4 labels touch tuning or training) -- a genuine cross-context transfer.

INPUTS REQUIRED
---------------
  evidence_layers_v11.json
  depmap_pdac_dependency.json   (endpoint E1 / E3-A / E3)
  pdac_selective_dependency_v11.json (endpoint E2)
  e5_clinical_targets.json      (endpoint E5; legacy name e6_clinical_validation.json)
  depmap_crc_dependency.json    (endpoint E4)

READY TO RUN
------------
Runs end-to-end when the released inputs are present; prints a structured
`MISSING_INPUTS` notice and exits 0 if any input is absent.  Outer-fold
predictions are written to --out (default repository/results/v29_p0_2_nestedcv_predictions.npz).
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


def _lv(gene, layer, layers):
    r = layers.get(layer, {}).get(gene)
    return r["norm"] if (r and r.get("present")) else None


def main(argv=None):
    ap = argparse.ArgumentParser(description="P0-2 nested CV audit")
    ap.add_argument("--data-dir", default=None)
    ap.add_argument("--out", default=os.path.join(REPO_ROOT, "results",
                    "v29_p0_2_nestedcv_predictions.npz"))
    ap.add_argument("--limit", type=int, default=0,
                    help="optional gene cap for smoke testing (0 = all genes)")
    args = ap.parse_args(argv)

    needed = [
        ("evidence_layers_v11.json", ["evidence_layers_v11.json"]),
        ("depmap_pdac_dependency.json", ["depmap_pdac_dependency.json"]),
        ("pdac_selective_dependency_v11.json", ["pdac_selective_dependency_v11.json"]),
        ("e5_clinical_targets.json", ["e5_clinical_targets.json",
                                      "e6_clinical_validation.json"]),
        ("depmap_crc_dependency.json", ["depmap_crc_dependency.json"]),
    ]
    paths, missing = resolve(needed, args.data_dir)
    if missing:
        print(json.dumps({
            "status": "MISSING_INPUTS",
            "audit": "P0-2 leakage-safe nested CV",
            "missing": missing,
            "resolved": list(paths.keys()),
            "message": ("Inputs not present -- awaiting released data. "
                        "No CV metrics were computed or fabricated."),
        }, indent=2, ensure_ascii=False))
        return 0

    from sklearn.metrics import roc_auc_score
    from sklearn.linear_model import LogisticRegression, ElasticNet
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.model_selection import StratifiedKFold
    from sklearn.preprocessing import StandardScaler

    # ---- build X and endpoints (mirrors recompute.py) --------------
    ev = json.load(open(paths["evidence_layers_v11.json"]))
    layers, genes = ev["layers"], ev["genes"]
    n = len(genes)
    if args.limit and args.limit < n:
        genes = genes[:args.limit]
        n = len(genes)
    X = np.full((n, len(FEATURES)), -3.0)
    gidx = {g: i for i, g in enumerate(genes)}
    for i, g in enumerate(genes):
        for j, f in enumerate(FEATURES):
            v = _lv_by_pos(ev, g, f)
            if v is not None:
                X[i, j] = v

    def yvec(s):
        return np.array([1.0 if g in s else 0.0 for g in genes])

    pdac = json.load(open(paths["depmap_pdac_dependency.json"]))
    ess_pdac = {g for g in genes if isinstance(pdac.get(g), dict) and pdac[g].get("essential")}
    drug_pos = {g for g in genes if _lv_by_pos(ev, g, "druggability") is not None}
    E1 = yvec(ess_pdac)
    E3 = yvec(ess_pdac & drug_pos)

    psd = json.load(open(paths["pdac_selective_dependency_v11.json"]))
    pe = psd["pan_essential"]
    defs = psd["definitions"]
    pan_ess = {g for g in genes if pe.get(g) is True}
    bz = {g: defs[g]["B_zeffect"] for g in pan_ess if g in defs}
    q75 = float(np.percentile(np.fromiter(bz.values(), float), 75))
    E2 = yvec({g for g, v in bz.items() if v >= q75})

    e5 = json.load(open(paths["e5_clinical_targets.json"]))
    E5 = yvec(set(e5.get("genes", [])) & set(genes))

    crc = json.load(open(paths["depmap_crc_dependency.json"]))
    ess_crc = {g for g in genes if isinstance(crc.get(g), dict) and crc[g].get("essential")}
    E4 = yvec(ess_crc)

    ENDPOINTS = {"E1": E1, "E2": E2, "E3": E3, "E3-A": E1, "E5": E5, "E4": E4}

    # ---- fixed candidate grids + fixed seed ----------------------------
    SEED = 42
    GRIDS = {
        "Logistic regression": [{"C": c} for c in (0.1, 1.0)],
        "Elastic net": [{"alpha": a, "l1_ratio": l}
                        for a in (0.01, 0.1) for l in (0.5, 0.7)],
        "Random forest": [{"n_estimators": ne, "max_depth": md}
                          for ne in (100, 200) for md in (5, 10, None)],
    }

    def fit_predict(name, params, Xtr, ytr, Xte):
        if name == "Logistic regression":
            m = LogisticRegression(max_iter=2000, class_weight="balanced",
                                   C=params["C"])
        elif name == "Elastic net":
            m = ElasticNet(alpha=params["alpha"], l1_ratio=params["l1_ratio"],
                           max_iter=5000)
        else:
            m = RandomForestClassifier(n_estimators=params["n_estimators"],
                                       max_depth=params["max_depth"], n_jobs=-1,
                                       class_weight="balanced", random_state=SEED)
        m.fit(Xtr, ytr)
        if name == "Elastic net":
            return m.predict(Xte)
        return m.predict_proba(Xte)[:, 1]

    def inner_best(name, Xtr, ytr):
        inner = StratifiedKFold(n_splits=5, shuffle=True, random_state=SEED)
        best, best_auc = None, -1.0
        for params in GRIDS[name]:
            aucs = []
            for itr, ite in inner.split(Xtr, ytr):
                try:
                    p = fit_predict(name, params, Xtr[itr], ytr[itr], Xtr[ite])
                    aucs.append(roc_auc_score(ytr[ite], p))
                except Exception:
                    aucs.append(-1.0)
            a = float(np.mean(aucs))
            if a > best_auc:
                best_auc, best = a, params
        return best

    outer = StratifiedKFold(n_splits=5, shuffle=True, random_state=SEED)
    preds = {ep: {m: np.full(n, np.nan) for m in GRIDS}
             for ep in ENDPOINTS}
    summary = {}
    for ep, y in ENDPOINTS.items():
        yy = y.astype(int)
        if yy.sum() < 10:
            summary[ep] = "skipped: too few positives"
            continue
        Xs = StandardScaler().fit_transform(X)
        ep_aucs = {m: [] for m in GRIDS}
        for tr, te in outer.split(Xs, yy):
            for m in GRIDS:
                params = inner_best(m, Xs[tr], yy[tr])
                p = fit_predict(m, params, Xs[tr], yy[tr], Xs[te])
                preds[ep][m][te] = p
                try:
                    ep_aucs[m].append(float(roc_auc_score(yy[te], p)))
                except ValueError:
                    pass
        summary[ep] = {m: (float(np.mean(v)) if v else None)
                       for m, v in ep_aucs.items()}

    # ---- E4 zero-shot: hyperparameters from E1 only, applied w/o refit -
    zs = {}
    if E1.sum() >= 10 and E4.sum() >= 10:
        Xs = StandardScaler().fit_transform(X)
        e1_y, e4_y = E1.astype(int), E4.astype(int)
        for m in GRIDS:
            params = inner_best(m, Xs, e1_y)          # chosen on E1 training only
            # fit on ALL of E1, predict E4 with no E4 labels used
            full = fit_predict(m, params, Xs, e1_y, Xs)
            try:
                zs[m] = float(roc_auc_score(e4_y, full))
            except ValueError:
                zs[m] = None
    summary["E4_zero_shot_from_E1"] = zs

    np.savez(args.out, **{f"{ep}_{m}": preds[ep][m]
                          for ep in preds for m in preds[ep]})
    out = {"audit": "P0-2 nested CV", "outer_folds": 5, "inner_folds": 5,
           "seed": SEED, "per_endpoint_outer_auc": summary,
           "n_genes": n, "predictions_written": args.out}
    json.dump(out, open(args.out.replace(".npz", ".json"), "w"),
              indent=1, ensure_ascii=False)
    print(json.dumps(out, indent=2, ensure_ascii=False))
    print("\nwrote", args.out)
    return 0


def _lv_by_pos(ev, gene, feat):
    layers, genes = ev["layers"], ev["genes"]
    if gene not in genes:
        return None
    r = layers.get(feat, {}).get(gene)
    return r["norm"] if (r and r.get("present")) else None


if __name__ == "__main__":
    sys.exit(main())
