# Auditing evidence integration for context-dependent therapeutic target prioritization

Analysis code, environment specification, input manifest, result tables and
display items for the accompanying manuscript (Nature Computational Science).

The study audits whether combining heterogeneous gene-level evidence layers
into a single integrated score improves therapeutic target ranking. The
headline result is negative: fixed-form integration outperforms the strongest
single layer (network centrality) only on endpoints whose labels embed an
input layer.

## Reproducibility status (v34)

A **from-scratch clean rerun has been executed** and reproduces every number
in the manuscript to six decimals. The frozen v34 commit records the git SHA and
the results-manifest SHA-256 in `results/verify_v34_manifest.json`, produced by the
one-command gate `python code/verify_v34.py`. Verification summary:

- 104 benchmark cells (12 scorers × 7 named + E6 endpoints): maximum absolute difference 0.0
- All headline AUROC/CI, negative controls, functional forms: identical
- E6 Random-forest AUROC = 0.9134 (verified against `v18_source_data.csv`)
- Sentinel audit S3: support-mean Φ(E3) = 0.889, without-druggability(E3) = 0.535,
  E3-A harmonic ≡ E1 harmonic (bit-identical taxonomy)
- Every `figures/Fig*_v34.png` is SHA-256 recorded and re-checked on each run

Run `python code/verify_v34.py` to re-run the full integrity gate (stdlib only,
no third-party packages required).

## Layout

```
code/                     analysis scripts, in execution order
  v18_recompute.py            endpoint taxonomy + 12×endpoint benchmark, CI, MWU, DeLong, Δ-CI
  v18_sentinel_audit.py       missing-data sentinel & combination-rule audit (S1–S4)
  v18_figures_v34.py          the six Nature display items (Fig1–6_v34, PNG+PDF)
  v18_ed_figures_v32_20260824.py  Extended Data Figures 1-4
  verify_v34.py               one-command reproducibility & integrity gate (stdlib only)
results/                  machine-readable outputs (v18_*.json / csv) + verify_v34_manifest.json
figures/                  the six display items (Fig1–6_v34.png + .pdf, 400 dpi)
extended_data/            Extended Data Figures 1-4 (PNG + PDF)
supplementary/            Supplementary Tables 1-5 + source data
submission_materials/     cover letter, author contributions, competing interests
AUDIT_v34.md              last-pass audit of the 5 submission-critical routines
STATS_v34.md              final statistical & methodological consistency check
FIGCHECKLIST_v34.md       per-figure Nature production-grade checklist
REPRODUCIBILITY_v34.md    reproducibility protocol & provenance
manuscript.md / .docx     the final manuscript
```

## Reproducing

```bash
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
python code/v18_recompute.py         # endpoint taxonomy + 12×endpoint benchmark -> results/v18_ncs_results.json
python code/v18_weightspace.py       # Dirichlet weight space -> results/v18_weight_space.json
python code/v18_sentinel_audit.py    # sentinel / combination-rule audit -> results/v18_sentinel_audit.json
python code/v18_figures_v34.py        # 6 Nature display items -> figures/Fig1–6_v34.png/.pdf
python code/v18_ed_figures_v32_20260824.py   # 4 Extended Data figures
python code/verify_v34.py             # one-command integrity gate -> results/verify_v34_manifest.json
```

For large-memory-constrained environments, `code/rerun_segmented.py`
(recomputes the benchmark endpoint-by-endpoint with checkpoint/resume and an
int32 bootstrap index, memory-halved and bit-identical) followed by
`code/rerun_finalize.py` reproduces the same outputs.

Runtime on a 2023 Apple silicon laptop is approximately 90 minutes, dominated
by the 2,000-resample bootstrap confidence intervals. No network access is
required at run time; no GPU is used.

Environment: Python 3.11.9, numpy 1.26.4, scipy 1.17.1, scikit-learn 1.9.0
(`environment_lock_v32_20260824.txt`).

## Inputs

Third-party inputs (DepMap 23Q2, GDSC/CCLE, STRING v12.0, COSMIC, gnomAD,
IMPC, Open Targets Genetics, Human Protein Atlas, ClinicalTrials.gov) are
**not redistributed** here because they are governed by their originators'
licences. Each is identified by SHA-256 and byte size in
`final_input_manifest_v32_20260824.csv`, so identity can be verified before a
rerun. The harmonised nine-layer evidence table and the complete benchmark
outputs are released in full in `results/`.

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

MIT (see `LICENSE`). Third-party inputs remain under their originators' terms.
