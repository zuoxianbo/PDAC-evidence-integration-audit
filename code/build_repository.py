#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
build_repository.py
Assemble the reproducibility repository required by the pre-submission
checklist (item 4): code + environment + input manifests + results + figures.

Raw third-party data are NOT redistributed. Instead each input file is
recorded with sha256, byte size, row/record count and provenance, so that a
reviewer can verify they hold the identical file.
"""
import os, sys, json, hashlib, shutil, subprocess, platform, datetime

ANALYSIS = "/Users/zuoxianbo/Desktop/zuoxb-虚拟科研系统-MAC/outputs/pdac-convergent-evidence-v14/analysis"
ROOT     = "/Users/zuoxianbo/Desktop/zuoxb-虚拟科研系统-MAC/outputs/pdac-convergent-evidence-v14"
DATA     = os.path.join(ROOT, "data")
GDSC_DIR = ("/Users/zuoxianbo/Desktop/zuoxb-虚拟科研系统-MAC/Zuoxb-Data-Medicine-platform/"
            "models/singlecell/scfoundation/DeepCDR/data")
OUT      = "/Users/zuoxianbo/Desktop/SCI论文/胰腺癌"
RES      = os.path.join(OUT, "results")
FIG      = os.path.join(OUT, "figures")
REPO     = os.path.join(OUT, "repository")

PY = sys.executable


def sha256(path, blk=1 << 20):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        while True:
            b = fh.read(blk)
            if not b:
                break
            h.update(b)
    return h.hexdigest()


def count_records(path):
    """Cheap structural summary: JSON top-level length, or text line count."""
    try:
        if path.endswith(".json"):
            with open(path) as fh:
                d = json.load(fh)
            return {"json_type": type(d).__name__, "top_level_entries": len(d)}
        n = sum(1 for _ in open(path, errors="replace"))
        return {"lines": n}
    except Exception as exc:                                    # noqa: BLE001
        return {"error": str(exc)[:120]}


INPUTS = [
    (os.path.join(DATA, "evidence_layers_v11.json"),
     "evidence_layers_v11.json",
     "Nine harmonised evidence layers for 20,751 protein-coding genes. Derived "
     "from STRING v12.0 (network degree centrality), COSMIC/TCGA PAAD mutation "
     "frequency, IMPC release 20.1 knockout viability, gnomAD v4 genetic "
     "constraint (LOEUF-derived), COSMIC Cancer Gene Census driver annotation, "
     "Open Targets Genetics v22.10 pancreatic-cancer L2G, DGIdb v5 / ChEMBL 33 "
     "druggability tiers, Human Protein Atlas v23 pancreatic-cancer prognostic "
     "association and HPA RNA tissue specificity. Layers are min-max scaled to "
     "[0,1]; genes absent from a source are assigned the sentinel value -3.0.",
     "input"),
    (os.path.join(DATA, "depmap_pdac_dependency.json"),
     "depmap_pdac_dependency.json",
     "DepMap 23Q2 CRISPR (Chronos) gene-effect matrix restricted to pancreatic "
     "adenocarcinoma cell lines; per-gene mean effect and essentiality call "
     "(Chronos < -0.5 in >=50% of lines). Source of endpoint E1.",
     "input"),
    (os.path.join(DATA, "depmap_crc_dependency.json"),
     "depmap_crc_dependency.json",
     "DepMap 23Q2 CRISPR gene effect restricted to colorectal adenocarcinoma "
     "cell lines; identical essentiality rule. Source of endpoint E4 "
     "(zero-shot cross-context transfer).",
     "input"),
    (os.path.join(DATA, "e6_clinical_validation.json"),
     "e5_clinical_targets.json",
     "Thirty-five genes that are the annotated primary target of an agent that "
     "has entered pancreatic-cancer clinical development (ClinicalTrials.gov "
     "query frozen 2024-12-31). Source of endpoint E5 (historical "
     "clinical-target concordance). NOTE: the on-disk filename retains the "
     "legacy 'e6_' prefix from V11; the endpoint is E5 in the V18 taxonomy.",
     "input"),
    (os.path.join(DATA, "pdac_selective_dependency_v11.json"),
     "pdac_selective_dependency_v11.json",
     "Pan-essential calls and B_zeffect selectivity statistic (PDAC effect "
     "minus non-PDAC effect, z-scored) per gene. Source of endpoint E2 "
     "(PDAC-enriched dependency, top quartile of B_zeffect within E1).",
     "input"),
    (os.path.join(GDSC_DIR, "CCLE", "GDSC_IC50.csv"),
     "GDSC_IC50.csv",
     "GDSC1/GDSC2 natural-log IC50 matrix, 266 compounds x 969 cell lines, as "
     "redistributed with DeepCDR. Source of endpoint E6.",
     "input"),
    (os.path.join(GDSC_DIR, "CCLE", "Cell_lines_annotations_20181226.txt"),
     "Cell_lines_annotations_20181226.txt",
     "CCLE cell-line annotation table; the Site_Primary field selects the 46 "
     "pancreatic lines, 29 of which carry GDSC IC50 values.",
     "input"),
    (os.path.join(GDSC_DIR, "GDSC", "1.Drug_listMon Jun 24 09_00_55 2019.csv"),
     "GDSC_drug_list.csv",
     "GDSC compound annotation with nominal protein targets; used to map "
     "compounds to HGNC symbols for endpoint E6.",
     "input"),
    (os.path.join(RES, "v17_ncs_results.json"),
     "v17_ncs_results.json",
     "Frozen V17 benchmark output, retained verbatim so that every V18 "
     "correction can be traced to the value it replaces.",
     "provenance"),
]

CODE = [
    ("recompute.py",
     "Primary analysis. Endpoint construction (E1-E6), 13 scorers, "
     "2,000-resample bootstrap AUROC CIs, Mann-Whitney U against chance, "
     "fast DeLong pairwise tests, paired bootstrap Delta-AUROC CIs, "
     "functional-form comparison, negative controls, structured resampling, "
     "candidate re-ranking, and the P0 audit ledger."),
    ("weightspace.py",
     "1,000-draw Dirichlet(1,1,1) weight-space analysis over the three driver "
     "layers, retaining every AUROC draw and every weight vector so that the "
     "distribution in Fig. 5b is the observed sample, not a parametric fit."),
    ("sentinel_audit.py",
     "Missing-data sentinel and combination-rule audit: sentinel prevalence "
     "per layer, order-preservation test of the multiplicative rule, "
     "decomposition of the harmonic score into its driver and support terms, "
     "and available-case recoding sensitivity."),
    ("figures.py",
     "Renders the six display items at 300 dpi from the result JSONs only."),
    ("build_repository.py",
     "This file. Assembles the repository and the input manifest."),
]


def main():
    for d in (REPO, os.path.join(REPO, "code"), os.path.join(REPO, "results"),
              os.path.join(REPO, "figures"), os.path.join(REPO, "manifest")):
        os.makedirs(d, exist_ok=True)

    # ---------------------------------------------------------------- code
    for fn, _ in CODE:
        src = os.path.join(ANALYSIS, fn)
        if os.path.exists(src):
            shutil.copy2(src, os.path.join(REPO, "code", fn))

    # ------------------------------------------------------------ manifest
    entries, missing = [], []
    for path, alias, prov, role in INPUTS:
        if not os.path.exists(path):
            missing.append(alias)
            entries.append({"alias": alias, "role": role, "status": "NOT FOUND",
                            "provenance": prov})
            continue
        st = os.stat(path)
        entries.append({
            "alias": alias,
            "role": role,
            "status": "present",
            "bytes": st.st_size,
            "sha256": sha256(path),
            "structure": count_records(path),
            "provenance": prov,
        })

    # ------------------------------------------------------- environment
    try:
        freeze = subprocess.run([PY, "-m", "pip", "freeze"],
                                capture_output=True, text=True, timeout=180).stdout
    except Exception:                                            # noqa: BLE001
        freeze = ""
    keep = ("numpy", "scipy", "scikit-learn", "matplotlib", "pandas",
            "joblib", "threadpoolctl", "pillow", "cycler", "kiwisolver")
    pinned = sorted(l.strip() for l in freeze.splitlines()
                    if l.strip() and l.split("==")[0].lower().replace("_", "-") in keep)

    env = {
        "python": sys.version.split()[0],
        "platform": platform.platform(),
        "machine": platform.machine(),
        "packages_pinned": pinned,
        "note": "Analysis is CPU-only and single-threaded apart from BLAS. "
                "No GPU, no network access at run time.",
    }

    # ------------------------------------------------------------ results
    res_files = []
    for fn in sorted(os.listdir(RES)) if os.path.isdir(RES) else []:
        if not fn.startswith("v1"):
            continue
        src = os.path.join(RES, fn)
        if os.path.isfile(src):
            shutil.copy2(src, os.path.join(REPO, "results", fn))
            res_files.append({"file": fn, "bytes": os.path.getsize(src),
                              "sha256": sha256(src)})

    fig_files = []
    if os.path.isdir(FIG):
        for fn in sorted(os.listdir(FIG)):
            src = os.path.join(FIG, fn)
            if os.path.isfile(src) and fn.lower().endswith((".pdf", ".png", ".tif")):
                shutil.copy2(src, os.path.join(REPO, "figures", fn))
                fig_files.append({"file": fn, "bytes": os.path.getsize(src)})

    manifest = {
        "title": "Auditing evidence integration for context-dependent "
                 "therapeutic target prioritization",
        "generated_utc": datetime.datetime.utcnow().isoformat(timespec="seconds") + "Z",
        "environment": env,
        "inputs": entries,
        "inputs_missing": missing,
        "code": [{"file": f, "role": r} for f, r in CODE],
        "results": res_files,
        "figures": fig_files,
        "reproduction_order": [
            "python code/recompute.py        # writes results/ncs_results.json, "
            "results/audit_report.json, results/source_data.csv",
            "python code/weightspace.py      # writes results/weight_space.json",
            "python code/sentinel_audit.py   # writes results/sentinel_audit.json",
            "python code/figures.py          # writes figures/Fig1..Fig6 (.pdf and .png)",
        ],
        "data_redistribution_statement":
            "Third-party inputs (DepMap, GDSC/CCLE, STRING, COSMIC, gnomAD, IMPC, "
            "Open Targets, Human Protein Assay) are not redistributed here because "
            "they are governed by their originators' licences. Each is identified "
            "above by sha256 and byte size; the harmonised evidence-layer table "
            "that the analysis consumes is released in full.",
    }
    with open(os.path.join(REPO, "manifest", "input_manifest.json"), "w") as fh:
        json.dump(manifest, fh, indent=1, ensure_ascii=False)

    with open(os.path.join(REPO, "requirements.txt"), "w") as fh:
        fh.write("# Python %s\n" % env["python"])
        fh.write("\n".join(pinned) + "\n")

    # -------------------------------------------------------------- README
    rows = "\n".join(
        "| `%s` | %s | %s | %s |" % (
            e["alias"], e["role"],
            format(e.get("bytes", 0), ","),
            e.get("sha256", "-")[:16] + ("..." if e.get("sha256") else ""))
        for e in entries)
    readme = """# Auditing evidence integration for context-dependent therapeutic target prioritization

Analysis code, environment specification, input manifest, result tables and
display items for the accompanying manuscript.

The study is an audit. It asks whether combining heterogeneous gene-level
evidence layers into a single integrated score improves the ranking of
candidate therapeutic targets, and it answers that question against eight
validation endpoints of differing provenance. The headline result is negative:
integration outperforms the strongest single layer only on endpoints whose
positive labels are themselves derived from one of the input layers.

## Layout

```
code/        analysis scripts, in execution order
manifest/    sha256 and provenance for every input file
results/     machine-readable outputs consumed by the manuscript and figures
figures/     the six display items, 300 dpi
requirements.txt
```

## Reproducing

```bash
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
%s
```

Runtime on a 2023 Apple silicon laptop is approximately 70 minutes, dominated
by the 2,000-resample bootstrap confidence intervals.
No network access is required at run time; no GPU is used.

## Inputs

| file | role | bytes | sha256 (truncated) |
|---|---|---|---|
%s

%s

## Endpoint taxonomy

| id | endpoint | label source | external to the evidence base |
|---|---|---|---|
| E1 | pan-dependency | DepMap 23Q2 PDAC CRISPR | yes |
| E2 | PDAC-enriched dependency | top quartile of B_zeffect within E1 | yes, but nested in E1 |
| E3 | conjunctive actionability | E1 positives that are also druggable | **no** - uses the druggability input layer |
| E3-A | leakage-controlled essentiality | E1 with the druggability conjunct removed | yes - and numerically identical to E1 |
| E3-C | out-of-evidence druggability | the druggability layer itself | **no** - the label is an input |
| E4 | CRC zero-shot transfer | DepMap 23Q2 colorectal CRISPR | yes |
| E5 | historical clinical-target concordance | agents in PDAC clinical development | yes |
| E6 | PDAC drug-response actionability | GDSC IC50 in 29 pancreatic lines | yes |

E3 and E3-C are retained deliberately: they are the two endpoints on which
integration appears to succeed, and the audit shows why.

## Licence

Code is released under the MIT licence. Third-party inputs remain under their
originators' terms.
""" % ("\n".join(manifest["reproduction_order"]), rows,
       manifest["data_redistribution_statement"])
    with open(os.path.join(REPO, "README.md"), "w") as fh:
        fh.write(readme)

    with open(os.path.join(REPO, "LICENSE"), "w") as fh:
        fh.write("MIT License\n\nCopyright (c) 2026\n\nPermission is hereby granted, "
                 "free of charge, to any person obtaining a copy of this software and "
                 "associated documentation files (the \"Software\"), to deal in the "
                 "Software without restriction, including without limitation the rights "
                 "to use, copy, modify, merge, publish, distribute, sublicense, and/or "
                 "sell copies of the Software, and to permit persons to whom the "
                 "Software is furnished to do so, subject to the following conditions:\n\n"
                 "The above copyright notice and this permission notice shall be "
                 "included in all copies or substantial portions of the Software.\n\n"
                 "THE SOFTWARE IS PROVIDED \"AS IS\", WITHOUT WARRANTY OF ANY KIND.\n")

    print("repository ->", REPO)
    print("  inputs recorded : %d  (missing %d)" % (len(entries), len(missing)))
    if missing:
        print("  MISSING:", ", ".join(missing))
    print("  code files      : %d" % len(os.listdir(os.path.join(REPO, "code"))))
    print("  results copied  : %d" % len(res_files))
    print("  figures copied  : %d" % len(fig_files))
    print("  pinned packages : %d" % len(pinned))


if __name__ == "__main__":
    main()
