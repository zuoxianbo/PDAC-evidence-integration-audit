# Reproducibility & Provenance — PDAC evidence-integration audit
**Version stamp:** `v29_20260823_1718`
**Linked files:** `final_input_manifest_v29_20260823_1718.csv`, `environment_lock_v29_20260823_1718.txt`, `run_final_rerun_v29_20260823_1718.sh`

---

## 1. Honesty caveat (read first)

**The raw third-party inputs are NOT present in this repository.** They are
governed by the originators' licences and are not redistributed (see
`repository/manifest/input_manifest.json` → `data_redistribution_statement` and
`repository/README.md`). Consequently, **a true clean recompute was NOT executed
as part of preparing this version**. Every number and figure in this submission
is carried forward from the precomputed result JSONs (`v18_ncs_results.json`,
`v18_audit_report.json`, `v18_source_data.csv`, `v18_sentinel_audit.json`,
`v18_weight_space.json`, `v17_ncs_results.json`) and the committed `figures/`
outputs, whose sha256 values were verified on 2026-08-23 against the manifest.

**No numbers were fabricated.** The harness below is built so that, the moment
the released inputs are supplied, a single command regenerates every number and
figure from first principles.

---

## 2. Environment

| Item | Value |
|---|---|
| Python | 3.11.9 (pinned) |
| OS / platform | macOS-26.5.2-x86_64-i386-64bit, x86_64 (Darwin 25.5.0) |
| Compute | CPU-only; single-threaded apart from BLAS. **No GPU.** |
| Network | **None** required at run time |
| Pinned deps | numpy 1.26.4, scikit-learn 1.9.0, matplotlib 3.11.1, scipy 1.17.1, pandas 2.3.3, cycler 0.12.1, joblib 1.5.3, kiwisolver 1.5.0, pillow 12.2.0, threadpoolctl 3.6.0 |

Full lock: `environment_lock_v29_20260823_1718.txt` (captured from `requirements.txt`).

## 3. Expected runtime

Approximately **70 minutes on a single CPU**, dominated by the 2,000-resample
bootstrap confidence intervals in `v18_recompute.py`. No network, no GPU.

## 4. Hardcoded-path note (documented, not edited)

`code/v18_recompute.py` hardcodes `ROOT`, `OUT`, and `GDSC_DIR` to a different
author machine:
- `ROOT = /Users/zuoxianbo/Desktop/zuoxb-虚拟科研系统-MAC/outputs/pdac-convergent-evidence-v14`
- `OUT  = /Users/zuoxianbo/Desktop/SCI论文/胰腺癌`
- `GDSC_DIR = /Users/zuoxianbo/Desktop/zuoxb-虚拟科研系统-MAC/Zuoxb-Data-Medicine-platform/models/singlecell/scfoundation/DeepCDR/data`

This file is **intentionally left untouched**. Before a real rerun you must
either reconcile those paths to the released inputs/outputs or patch the four
path constants. The wrapper refuses to start unless the inputs exist, which
prevents silent partial runs.

## 5. Exact regeneration command

After the released raw inputs are placed in `IN_DIR` (default `repository/data`)
and `v18_recompute.py` paths are resolved:

```bash
cd repository
pip install -r requirements.txt                 # or restore environment_lock_*.txt
chmod +x run_final_rerun_v29_20260823_1718.sh
IN_DIR=/path/to/released/inputs ./run_final_rerun_v29_20260823_1718.sh
```

This runs, in order:
1. `python code/v18_recompute.py`      → `results/v18_ncs_results.json`, `results/v18_audit_report.json`, `results/v18_source_data.csv`
2. `python code/v18_weightspace.py`    → `results/v18_weight_space.json`
3. `python code/v18_sentinel_audit.py` → `results/v18_sentinel_audit.json`
4. `python code/v18_figures.py`        → `figures/Fig1..Fig6` (.pdf + .png)

If any of the 8 raw inputs is missing, the wrapper prints a clear refusal and
exits without running anything.

## 6. Provenance to record AFTER the clean rerun

Before releasing the regenerated artifacts, fill in:

- **Final commit SHA** — `git rev-parse HEAD` at the moment of the clean rerun
  (currently `c439c9a` in this repo; a new commit must be made after rerun).
- **Results-manifest sha256** — written by the wrapper to
  `run_record_v29_20260823_1718.txt` (concatenated sha256 of the five result
  files). This is the single hash that certifies the numeric outputs.

These two values, plus this version stamp, constitute the reproducibility
receipt for the published numbers.

## 7. Inputs required (with identifiers)

Identified by sha256 + byte size in `final_input_manifest_v29_20260823_1718.csv`.
Sources: STRING v12.0, COSMIC/TCGA PAAD, IMPC 20.1, gnomAD v4, Cancer Gene
Census, Open Targets Genetics v22.10, DGIdb v5/ChEMBL 33, Human Protein Atlas
v23, DepMap 23Q2 (PDAC + CRC CRISPR), GDSC/CCLE, DeepCDR GDSC IC50. None are
redistributed here; obtain from the originators and verify sha256 before rerun.
