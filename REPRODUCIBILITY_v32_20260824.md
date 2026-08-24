# Reproducibility — PDAC evidence-integration audit

**Version stamp:** `v32_20260824`

## Status: clean rerun COMPLETE (2026-08-24)

A from-scratch recompute has been executed on the author's machine and
reproduces every number in the manuscript. See `run_record_v32_20260824.txt`:

- **git commit SHA:** `c439c9af42792abb93fe97f505e7efdb40bd8d01`
- **results-manifest SHA-256:** `4aa24440ebddbaf50e4921b71d98bfc37151e94d500ff812f3d290765bb1bb23`

### Verification summary

| Check | Result |
|---|---|
| 104 benchmark cells (13 scorers × 8 endpoints) | maximum absolute difference **0.0** |
| Headline AUROC + CI (E1/E3/E5/E6) | identical to 6 decimals |
| Paired ΔAUROC + DeLong P | identical |
| Negative controls / functional forms | identical |
| Dirichlet weight space (1,000 draws) | **bit-identical** |
| Sentinel audit + 15 findings | identical |

## Environment

`sc-models` venv — Python 3.11.9, numpy 1.26.4, scipy 1.17.1, scikit-learn 1.9.0
(full lock: `environment_lock_v32_20260824.txt`).

## Recompute pipeline

```bash
python code/v18_recompute.py                       # 8-endpoint benchmark
python code/v18_weightspace.py                     # Dirichlet weight space
python code/v18_sentinel_audit.py                  # sentinel / combination-rule audit
python code/v18_figures_v32_20260824.py            # 6 display items
python code/v18_ed_figures_v32_20260824.py         # 4 Extended Data figures
```

For memory-constrained environments the benchmark was executed endpoint-by-endpoint:
`code/rerun_segmented.py` (checkpoint/resume, int32 bootstrap index — bit-identical
to the int64 original, memory halved) followed by `code/rerun_finalize.py`.

## Raw inputs

Eight third-party inputs (DepMap 23Q2, GDSC/CCLE, STRING v12.0, COSMIC, gnomAD,
IMPC, Open Targets Genetics, Human Protein Atlas, ClinicalTrials.gov) are **not
redistributed** here per licence. They are identified by SHA-256 and byte size in
`final_input_manifest_v32_20260824.csv`, so identity can be verified before a
rerun. The harmonised nine-layer evidence table and complete benchmark outputs
are released in full in `results/`.
