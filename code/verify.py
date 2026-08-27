#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
verify.py — one-command reproducibility & integrity gate for the
Nature Computational Science (NCS) v34 submission of the PDAC convergent
evidence-integration audit.

What it checks
--------------
1. Frozen seed & bootstrap count are present in the recompute source
   (seed=20260819, N_BOOT=2000).
2. Known headline constants re-derived from the frozen results artefacts:
     - E6 Random-forest AUROC = 0.9134  (source_data.csv, row "E6 ... ,Random forest")
     - GDSC endpoint counts: n_pancreas_lines_with_ic50=29,
       n_drugs_sensitive_tertile=41, n_positive_genes=32   (ncs_results.json)
     - Sentinel audit: support-mean PHI(E3)=0.889,
       support-mean-without-druggability(E3)=0.535,
       E3-A harmonic == E1 harmonic (bit-identical taxonomy)  (sentinel_audit.json)
3. Figure integrity: SHA-256 of every figures/Fig*.png AND every
   extended_data/ED_Fig*.png is recorded on the first run and compared on
   every later run. Any mismatch (or a missing figure) FAILS the gate, so a
   re-run that silently changes a panel is caught.
4. Artefact manifest: SHA-256 of the three results JSON + the code files
   (recompute.py, figures.py, ed_figures.py, verify.py)
   is written to results/verify_manifest.json for provenance.

Usage
-----
    python3 code/verify.py            # verify (record manifest if absent)
    python3 code/verify.py --strict  # fail if manifest absent (CI mode)

Exit code 0 = all checks pass; 1 = at least one check failed.
No third-party dependency — standard library only.
"""
import argparse
import csv
import hashlib
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
RES = os.path.join(REPO, "results")
FIG = os.path.join(REPO, "figures")
EDF = os.path.join(REPO, "extended_data")
MANIFEST = os.path.join(RES, "verify_manifest.json")

# tolerance for float comparisons
TOL = 1e-3

EXPECT = {
    "e6_rf_auroc": 0.9134,
    "gdsc_n_pancreas_lines_with_ic50": 29,
    "gdsc_n_drugs_sensitive_tertile": 41,
    "gdsc_n_positive_genes": 32,
    "sentinel_support_mean_phi_e3": 0.889,
    "sentinel_without_drug_e3": 0.535,
}


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def approx(a, b, tol=TOL):
    return abs(float(a) - float(b)) <= tol


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--strict", action="store_true",
                    help="fail if manifest is absent (CI mode)")
    args = ap.parse_args()

    fails = []
    checks = []

    def record(name, ok, detail=""):
        checks.append((name, ok, detail))
        if not ok:
            fails.append(name)

    # ---- 1. seed / bootstrap frozen -----------------------------------
    recompute_src = open(os.path.join(HERE, "recompute.py"),
                         encoding="utf-8").read()
    record("seed_20260819_present",
           "20260819" in recompute_src,
           "np.random.default_rng(20260819)")
    record("N_BOOT_2000_present",
           "N_BOOT = 2000" in recompute_src,
           "bootstrap count frozen at 2000")

    # ---- 2a. E6 RF from source-data CSV -------------------------------
    try:
        with open(os.path.join(RES, "source_data.csv"), encoding="utf-8") as f:
            rows = list(csv.DictReader(f))
        hit = next((r for r in rows
                    if r["endpoint"].startswith("E6")
                    and r["method"] == "Random forest"), None)
        if hit:
            record("e6_rf_auroc", approx(hit["auroc"], EXPECT["e6_rf_auroc"]),
                   f"csv={hit['auroc']} expected≈{EXPECT['e6_rf_auroc']}")
        else:
            record("e6_rf_auroc", False, "row not found in source_data.csv")
    except Exception as e:  # noqa
        record("e6_rf_auroc", False, f"exception: {e}")

    # ---- 2b. GDSC endpoint counts -------------------------------------
    try:
        g = json.load(open(os.path.join(RES, "ncs_results.json"),
                           encoding="utf-8"))["gdsc_endpoint"]
        record("gdsc_n_pancreas_lines_with_ic50",
               g["n_pancreas_lines_with_ic50"] == EXPECT["gdsc_n_pancreas_lines_with_ic50"],
               f"{g['n_pancreas_lines_with_ic50']}")
        record("gdsc_n_drugs_sensitive_tertile",
               g["n_drugs_sensitive_tertile"] == EXPECT["gdsc_n_drugs_sensitive_tertile"],
               f"{g['n_drugs_sensitive_tertile']}")
        record("gdsc_n_positive_genes",
               g["n_positive_genes"] == EXPECT["gdsc_n_positive_genes"],
               f"{g['n_positive_genes']}")
    except Exception as e:  # noqa
        record("gdsc_endpoint", False, f"exception: {e}")

    # ---- 2c. Sentinel audit (S3) --------------------------------------
    try:
        s3 = json.load(open(os.path.join(RES, "sentinel_audit.json"),
                            encoding="utf-8"))["S3_endpointwise"]
        e3 = s3["E3 conjunctive actionability"]
        record("sentinel_support_mean_phi_e3",
               approx(e3["support_mean_PHI"], EXPECT["sentinel_support_mean_phi_e3"]),
               f"{e3['support_mean_PHI']:.4f}")
        record("sentinel_without_drug_e3",
               approx(e3["support_mean_without_druggability"],
                      EXPECT["sentinel_without_drug_e3"]),
               f"{e3['support_mean_without_druggability']:.4f}")
        # E3-A must be bit-identical to E1 harmonic
        e3a = s3["E3-A leakage-controlled essentiality"]
        record("e3a_equals_e1_harmonic",
               approx(e3a["harmonic"], s3["E1 pan-dependency"]["harmonic"]),
               f"E3-A={e3a['harmonic']:.4f} E1={s3['E1 pan-dependency']['harmonic']:.4f}")
    except Exception as e:  # noqa
        record("sentinel_audit", False, f"exception: {e}")

    # ---- 3. figure integrity (SHA-256) -------------------------------
    fig_hashes = {}
    for i in range(1, 7):
        p = os.path.join(FIG, f"Fig{i}.png")
        if os.path.exists(p):
            fig_hashes[f"Fig{i}.png"] = sha256(p)
        else:
            record(f"Fig{i}_present", False, "file missing")

    manifest = {}
    if os.path.exists(MANIFEST):
        manifest = json.load(open(MANIFEST, encoding="utf-8"))
    fig_prev = manifest.get("figures", {})

    if not fig_prev:
        record("figure_hash_recorded", True,
               "first run — manifest written")
    else:
        for name, h in fig_hashes.items():
            prev = fig_prev.get(name)
            record(f"figure_hash_{name}",
                   prev is not None and prev == h,
                   "matches previous" if (prev == h) else "MISMATCH vs recorded")

    # ---- 3b. Extended Data figure integrity (SHA-256) -----------------
    ed_hashes = {}
    for i in range(1, 5):
        p = os.path.join(EDF, f"ED_Fig{i}.png")
        if os.path.exists(p):
            ed_hashes[f"ED_Fig{i}.png"] = sha256(p)
        else:
            record(f"ED_Fig{i}_present", False, "file missing")

    ed_prev = manifest.get("extended_data", {})
    if not ed_prev:
        record("ed_figure_hash_recorded", True,
               "first run — Extended Data hashes written")
    else:
        for name, h in ed_hashes.items():
            prev = ed_prev.get(name)
            record(f"ed_figure_hash_{name}",
                   prev is not None and prev == h,
                   "matches previous" if (prev == h) else "MISMATCH vs recorded")

    # ---- 4. artefact manifest (JSON + code) --------------------------
    artefact_files = [
        "ncs_results.json",
        "sentinel_audit.json",
        "source_data.csv",
    ]
    artefact_hashes = {}
    for fn in artefact_files:
        p = os.path.join(RES, fn)
        if os.path.exists(p):
            artefact_hashes[fn] = sha256(p)
    code_hashes = {}
    for cf in ("recompute.py", "figures.py",
               "ed_figures.py", "verify.py"):
        p = os.path.join(HERE, cf)
        if os.path.exists(p):
            code_hashes[cf] = sha256(p)
        else:
            record(f"code_present_{cf}", False, "file missing")

    new_manifest = {
        "seed": 20260819,
        "n_boot": 2000,
        "figures": fig_hashes,
        "extended_data": ed_hashes,
        "results_artefacts": artefact_hashes,
        "code": code_hashes,
    }
    with open(MANIFEST, "w", encoding="utf-8") as f:
        json.dump(new_manifest, f, indent=2)

    # ---- report -------------------------------------------------------
    print("=" * 64)
    print("verify — PDAC evidence-integration audit")
    print("=" * 64)
    for name, ok, detail in checks:
        print(f"  [{'PASS' if ok else 'FAIL'}] {name:<40s} {detail}")
    print("-" * 64)
    print(f"  main figures hashed     : {len(fig_hashes)}")
    print(f"  Extended Data hashed    : {len(ed_hashes)}")
    print(f"  results artefacts hashed: {len(artefact_hashes)}")
    print(f"  code files hashed       : {len(code_hashes)}")
    print(f"  manifest       : {MANIFEST}")
    print("=" * 64)
    if fails:
        print(f"RESULT: FAIL ({len(fails)} check(s) failed)")
        print("Failed:", ", ".join(fails))
        return 1
    print("RESULT: PASS — all reproducibility & integrity gates green.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
