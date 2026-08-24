# Auditing evidence integration for context-dependent therapeutic target prioritization

Analysis code, environment specification, input manifest, result tables and
display items for the accompanying manuscript (Nature Computational Science).

The study audits whether combining heterogeneous gene-level evidence layers
into a single integrated score improves therapeutic target ranking. The
headline result is negative: fixed-form integration outperforms the strongest
single layer (network centrality) only on endpoints whose labels embed an
input layer.

## Reproducibility status

A **from-scratch clean rerun has been executed** and reproduces every number
in the manuscript to six decimals. See `run_record_v31_20260824.txt` for the
git commit SHA and results-manifest SHA-256. Verification summary:

- 104 benchmark cells (13 scorers × 8 endpoints): maximum absolute difference 0.0
- All headline AUROC/CI, negative controls, functional forms: identical
- Dirichlet weight space (1,000 draws): bit-identical

## Layout

```
code/                     analysis scripts, in execution order
results/                  machine-readable outputs (v18_*.json / csv)
figures/                  the six display items (PNG + PDF, 400 dpi)
extended_data/            Extended Data Figures 1-4 (PNG + PDF)
supplementary/            Supplementary Tables 1-5 + source data
submission_materials/     cover letter, author contributions, competing interests
manuscript.md / .docx     the final manuscript
run_record_v31_20260824.txt   clean-rerun provenance record
```

## Reproducing

```bash
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
python code/v18_recompute.py         # 8-endpoint benchmark -> results/v18_ncs_results.json
python code/v18_weightspace.py       # Dirichlet weight space -> results/v18_weight_space.json
python code/v18_sentinel_audit.py    # sentinel / combination-rule audit -> results/v18_sentinel_audit.json
python code/v18_figures_v31_20260823_1830.py      # 6 display items
python code/v18_ed_figures_v31_20260823_1830.py   # 4 Extended Data figures
```

For large-memory-constrained environments, `code/rerun_segmented.py`
(recomputes the benchmark endpoint-by-endpoint with checkpoint/resume and an
int32 bootstrap index, memory-halved and bit-identical) followed by
`code/rerun_finalize.py` reproduces the same outputs.

Runtime on a 2023 Apple silicon laptop is approximately 90 minutes, dominated
by the 2,000-resample bootstrap confidence intervals. No network access is
required at run time; no GPU is used.

Environment: Python 3.11.9, numpy 1.26.4, scipy 1.17.1, scikit-learn 1.9.0
(`environment_lock_v29_20260823_1718.txt`).

## Inputs

Third-party inputs (DepMap 23Q2, GDSC/CCLE, STRING v12.0, COSMIC, gnomAD,
IMPC, Open Targets Genetics, Human Protein Atlas, ClinicalTrials.gov) are
**not redistributed** here because they are governed by their originators'
licences. Each is identified by SHA-256 and byte size in
`final_input_manifest_v29_20260823_1718.csv`, so identity can be verified
before a rerun. The harmonised nine-layer evidence table and the complete
benchmark outputs are released in full in `results/`.

## Licence

MIT (see `LICENSE`).
