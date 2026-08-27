#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""audit_overlap_p0_1 -- P0-1 endpoint x evidence-layer gene-level overlap audit.

PURPOSE
-------
Gene-level overlap between the *external-label* endpoints (E5 historical
clinical-target concordance; E6 PDAC drug-response actionability) and the
DGIdb / ChEMBL *tractability layer* (the `druggability` evidence layer, which
is itself derived from DGIdb v5 / ChEMBL 33).  The audit reports:

  * total overlap                 -- |label_genes ∩ tractable_genes|
  * positive-label overlap        -- fraction of POSITIVE-label genes that are tractable
  * negative-label overlap        -- fraction of NON-positive genes that are tractable
  * overlap-excluded sensitivity -- re-score (STRING centrality vs the label) after
                                    removing every gene that is BOTH labelled and tractable,
                                    to test whether the apparent signal is driven by the
                                    circular druggability overlap.

INPUTS REQUIRED (resolved from the input manifest / candidate data dirs)
-----------------------------------------------------------------------
  evidence_layers_v11.json      -- the released harmonised 9-layer evidence matrix
  e5_clinical_targets.json      -- E5 label (legacy on-disk name: e6_clinical_validation.json)
  GDSC_IC50.csv                 -- only needed for the optional E6 label construction
  Cell_lines_annotations_20181226.txt
  GDSC_drug_list.csv

READY TO RUN
------------
The script runs end-to-end the moment the released inputs are present.  If any
required input is absent it prints a structured `MISSING_INPUTS` notice and
exits 0 -- it NEVER fabricates overlap numbers.

NOTE: This is a P0 audit *skeleton* -- the overlap accounting and the
overlap-excluded AUROC re-run are fully implemented and real; the E6 label is
constructed with the same GDSC tertile rule as recompute.py.
"""
import os
import sys
import json
import argparse

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(os.path.dirname(HERE))          # repository/
ORIG_ROOT = "/Users/zuoxianbo/Desktop/zuoxb-虚拟科研系统-MAC/outputs/pdac-convergent-evidence-v14/data"
GDSC_DIR = ("/Users/zuoxianbo/Desktop/zuoxb-虚拟科研系统-MAC/Zuoxb-Data-Medicine-platform/"
            "models/singlecell/scfoundation/DeepCDR/data")

# ---- input resolution ----------------------------------------------------
def _candidate_dirs(data_dir):
    # --data-dir is authoritative: only that directory is searched.
    if data_dir:
        return [data_dir]
    dirs = [os.path.join(REPO_ROOT, "data"), ORIG_ROOT]
    if os.path.isdir(GDSC_DIR):
        dirs.append(GDSC_DIR)
    env = os.environ.get("PDAC_DATA_DIR")
    if env:
        dirs.append(env)
    return dirs


def resolve(required, data_dir=None):
    """required: list of (alias, [candidate_filenames]). Returns (paths, missing)."""
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
    ap = argparse.ArgumentParser(description="P0-1 overlap audit")
    ap.add_argument("--data-dir", default=None,
                    help="directory containing the released input JSON/CSV files")
    ap.add_argument("--out", default=os.path.join(REPO_ROOT, "results",
                    "v29_p0_1_overlap.json"),
                    help="where to write the structured overlap report")
    args = ap.parse_args(argv)

    needed = [
        ("evidence_layers_v11.json", ["evidence_layers_v11.json"]),
        ("e5_clinical_targets.json", ["e5_clinical_targets.json",
                                      "e6_clinical_validation.json"]),
        ("GDSC_IC50.csv", ["GDSC_IC50.csv"]),
        ("Cell_lines_annotations_20181226.txt",
         ["Cell_lines_annotations_20181226.txt"]),
        ("GDSC_drug_list.csv", ["GDSC_drug_list.csv",
                                "1.Drug_listMon Jun 24 09_00_55 2019.csv"]),
    ]
    paths, missing = resolve(needed, args.data_dir)
    if missing:
        print(json.dumps({
            "status": "MISSING_INPUTS",
            "audit": "P0-1 endpoint x evidence-layer overlap",
            "missing": missing,
            "resolved": list(paths.keys()),
            "message": ("Inputs not present -- awaiting released data. "
                        "No overlap values were computed or fabricated."),
        }, indent=2, ensure_ascii=False))
        return 0

    # ---- load evidence matrix ------------------------------------------
    ev = json.load(open(paths["evidence_layers_v11.json"]))
    layers, genes = ev["layers"], ev["genes"]
    gene_idx = {g: i for i, g in enumerate(genes)}
    n = len(genes)
    tractable = {g for g in genes if _lv(g, "druggability", layers) is not None}

    # ---- E5 label -------------------------------------------------------
    e5 = json.load(open(paths["e5_clinical_targets.json"]))
    e5_genes = set(e5.get("genes", [])) & set(genes)

    # ---- E6 label (same GDSC tertile rule as recompute.py) ---------
    e6_genes = None
    try:
        import csv
        gdsc_dir = os.path.dirname(paths["GDSC_IC50.csv"])
        rows = list(csv.DictReader(open(paths["Cell_lines_annotations_20181226.txt"],
                                        encoding="utf-8", errors="replace"),
                                   delimiter="\t"))
        panc = {r["depMapID"].strip() for r in rows
                if (r.get("Site_Primary") or "").strip().lower() == "pancreas"
                and r.get("depMapID")}
        ic = list(csv.reader(open(paths["GDSC_IC50.csv"])))
        header, body = ic[0], ic[1:]
        cols = header[1:]
        pidx = [i for i, c in enumerate(cols) if c.strip() in panc]
        drug_ic50 = {}
        for r in body:
            did = r[0].replace("GDSC:", "").strip()
            vals = [float(r[1 + i]) for i in pidx
                    if r[1 + i].strip() not in ("", "NA", "NaN")]
            if len(vals) >= 8:
                drug_ic50[did] = float(np.median(vals))
        drugs = list(csv.DictReader(open(paths["GDSC_drug_list.csv"],
                                         encoding="utf-8", errors="replace")))
        d2t = {}
        for d in drugs:
            did = (d.get("drug_id") or "").strip()
            tgs = {t.strip() for t in (d.get("Targets") or "").replace(";", ",").split(",")
                   if t.strip() in gene_idx}
            if did and tgs:
                d2t[did] = tgs
        shared = [d for d in drug_ic50 if d in d2t]
        if len(shared) >= 40:
            order = sorted(shared, key=lambda d: drug_ic50[d])
            k = max(1, len(order) // 3)
            sens = set().union(*[d2t[d] for d in order[:k]])
            res = set().union(*[d2t[d] for d in order[-k:]])
            e6_genes = (sens - res) & set(genes)
    except Exception as e:  # pragma: no cover
        e6_genes = None
        sys.stderr.write("E6 label construction skipped: %r\n" % e)

    def overlap(label_set, label_name):
        lab = label_set & set(genes)
        non = set(genes) - lab
        tot = len(lab & tractable)
        pos = (len(lab & tractable) / len(lab)) if lab else float("nan")
        neg = (len(non & tractable) / len(non)) if non else float("nan")
        return {"label": label_name, "n_label": len(lab),
                "n_tractable": len(tractable), "total_overlap": tot,
                "positive_label_overlap": pos, "negative_label_overlap": neg}

    report = {
        "audit": "P0-1 endpoint x evidence-layer overlap",
        "n_genes": n, "n_tractable": len(tractable),
        "E5_vs_tractability": overlap(e5_genes, "E5 clinical-target concordance"),
    }
    if e6_genes is not None:
        report["E6_vs_tractability"] = overlap(e6_genes, "E6 drug-response actionability")
    else:
        report["E6_vs_tractability"] = "pending input data (GDSC construction failed)"

    # ---- overlap-excluded sensitivity re-run ---------------------------
    # Re-score STRING centrality vs E5 after removing genes that are BOTH
    # labelled and tractable (the potentially circular ones).
    from sklearn.metrics import roc_auc_score
    str_idx = [i for i, g in enumerate(genes)]
    cent = np.array([_lv(g, "string_centrality", layers) or np.nan for g in genes])
    y_all = np.array([1.0 if g in e5_genes else 0.0 for g in genes])
    ok = np.isfinite(cent)
    auc_full = float(roc_auc_score(y_all[ok], cent[ok]))
    circ = e5_genes & tractable
    keep = np.array([g not in circ for g in genes])
    m = keep & ok
    if y_all[m].sum() >= 5 and (len(y_all[m]) - y_all[m].sum()) >= 5:
        auc_excl = float(roc_auc_score(y_all[m], cent[m]))
    else:
        auc_excl = None
    report["overlap_excluded_sensitivity"] = {
        "removed_circular_genes": len(circ),
        "auc_string_vs_E5_full": auc_full,
        "auc_string_vs_E5_excluding_overlap": auc_excl,
    }
    json.dump(report, open(args.out, "w"), indent=1, ensure_ascii=False)
    print(json.dumps(report, indent=2, ensure_ascii=False))
    print("\nwrote", args.out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
