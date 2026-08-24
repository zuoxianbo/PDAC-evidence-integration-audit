# Supplementary Tables — PDAC evidence-integration audit
**Version stamp:** `v31_20260823_1830`  |  Aligned with manuscript `manuscript_v31_20260823_1830`

All numbers are extracted from the precomputed result files (`v18_ncs_results.json`, `v18_weight_space.json`, `v18_sentinel_audit.json`). No values are fabricated; items requiring the raw third-party inputs are flagged explicitly.

## Supplementary Table 2 — Endpoint provenance and independence matrix

| ID | Endpoint | Positive definition | Positives | Provenance class | Label external to evidence base |
|---|---|---|---|---|---|
| E1 | PDAC-wide dependency | DepMap 23Q2 Chronos gene effect in pancreatic lines below the essentiality threshold | 4584 | external-label | yes |
| E2 | PDAC-enriched dependency | upper quartile of the PDAC-vs-other selectivity statistic among E1 positives | 1147 | non-independent (stratification of E1) | yes (nested in E1) |
| E3 | essential-and-druggable construct | E1 positive AND annotated druggable (conjunctive benchmark construct) | 1159 | constructed/circular | no |
| E3-A | essentiality-only control | E1 positive with the druggability conjunct removed | 4584 | non-independent (identical to E1) | yes (identical to E1) |
| E3-C | circular druggability control | chemical-tractability layer used directly as the label | 5188 | constructed/circular | no |
| E4 | CRC zero-shot transfer | DepMap 23Q2 Chronos gene effect in colorectal lines, scoring not refitted | 4608 | external-label | yes |
| E5 | historical clinical-target concordance | nominal primary target of an agent entering pancreatic-cancer clinical development | 35 | external-label | yes (overlaps tractability) |
| E6 | PDAC drug-response actionability | nominal target of a GDSC compound in the most sensitive tertile across pancreatic lines | 32 | external-label | yes (overlaps tractability) |

The six primary evaluation targets = E1, E4, E5, E6 (external-label) + E3, E3-C (constructed diagnostics). E2 and E3-A are reported for continuity and excluded from independent-endpoint counts.

## Supplementary Table 4 — Full scorer × endpoint AUROC (AUPRC in brackets)

Each cell: AUROC (AUPRC). 95% percentile CIs from 2,000 stratified bootstrap resamples are in `source_data_v31_20260823_1830.csv`.

| Scorer | E1 | E2 | E3 | E3-A | E3-C | E4 | E5 | E6 |
|---|---|---|---|---|---|---|---|---|
| Mutation frequency | 0.499 (0.217) | 0.491 (0.055) | 0.520 (0.058) | 0.499 (0.217) | 0.563 (0.282) | 0.497 (0.218) | 0.702 (0.115) | 0.567 (0.002) |
| Genetic constraint | 0.524 (0.218) | 0.496 (0.051) | 0.559 (0.058) | 0.524 (0.218) | 0.643 (0.310) | 0.530 (0.224) | 0.389 (0.001) | 0.371 (0.001) |
| Cancer-driver annotation | 0.507 (0.225) | 0.506 (0.057) | 0.521 (0.066) | 0.507 (0.225) | 0.511 (0.260) | 0.507 (0.227) | 0.737 (0.035) | 0.635 (0.011) |
| Druggability | 0.507 (0.231) | 0.526 (0.060) | 0.915 (0.260) | 0.507 (0.231) | 1.000 (1.000) | 0.506 (0.232) | 0.808 (0.008) | 0.780 (0.007) |
| STRING centrality | 0.695 (0.399) | 0.601 (0.081) | 0.738 (0.175) | 0.695 (0.399) | 0.620 (0.356) | 0.702 (0.408) | 0.986 (0.135) | 0.910 (0.027) |
| Arithmetic mean | 0.580 (0.253) | 0.561 (0.066) | 0.832 (0.197) | 0.580 (0.253) | 0.874 (0.760) | 0.580 (0.254) | 0.894 (0.137) | 0.732 (0.051) |
| Rank aggregation | 0.533 (0.241) | 0.518 (0.061) | 0.636 (0.094) | 0.533 (0.241) | 0.679 (0.424) | 0.534 (0.242) | 0.854 (0.018) | 0.786 (0.013) |
| Weighted rank aggregation | 0.634 (0.311) | 0.575 (0.073) | 0.835 (0.260) | 0.634 (0.311) | 0.808 (0.641) | 0.638 (0.316) | 0.956 (0.234) | 0.906 (0.105) |
| ECS (multiplicative) | 0.415 (0.179) | 0.469 (0.049) | 0.693 (0.080) | 0.415 (0.179) | 0.717 (0.346) | 0.415 (0.180) | 0.825 (0.009) | 0.705 (0.004) |
| Harmonic mean | 0.575 (0.254) | 0.567 (0.068) | 0.893 (0.245) | 0.575 (0.254) | 0.936 (0.873) | 0.576 (0.255) | 0.941 (0.207) | 0.846 (0.078) |
| Logistic regression | 0.679 (0.338) | 0.603 (0.077) | 0.931 (0.371) | 0.679 (0.338) | 1.000 (1.000) | 0.683 (0.344) | 0.982 (0.291) | 0.910 (0.021) |
| Elastic net | 0.671 (0.327) | 0.594 (0.074) | 0.927 (0.333) | 0.671 (0.327) | 1.000 (1.000) | 0.675 (0.332) | 0.899 (0.168) | 0.481 (0.001) |
| Random forest | 0.750 (0.490) | 0.631 (0.089) | 0.942 (0.486) | 0.750 (0.490) | 1.000 (1.000) | 0.756 (0.499) | 0.942 (0.250) | 0.913 (0.017) |

Supervised learners (logistic regression, elastic net, random forest) use out-of-fold predictions from five-fold stratified cross-validation. Learners on E3/E3-C are circular by construction and reported for completeness.

### Supplementary Table 4 (continued) — Primary pairwise contrasts vs STRING centrality

| Endpoint | Comparison | ΔAUROC (95% CI) | DeLong P |
|---|---|---|---|
| E1 | Harmonic mean | -0.120 (-0.129 to -0.110) | 1.81e-141 |
| E1 | Random forest | 0.055 (0.049 to 0.062) | 1.23e-66 |
| E1 | ECS (multiplicative) | -0.280 (-0.294 to -0.265) | < 1e-300 |
| E2 | Harmonic mean | -0.035 (-0.052 to -0.018) | 5.38e-05 |
| E2 | Random forest | 0.030 (0.013 to 0.046) | 0.00033 |
| E2 | ECS (multiplicative) | -0.133 (-0.159 to -0.106) | 4.4e-23 |
| E3 | Harmonic mean | 0.154 (0.141 to 0.168) | 1.68e-115 |
| E3 | Random forest | 0.204 (0.190 to 0.218) | 1.08e-183 |
| E3 | ECS (multiplicative) | -0.046 (-0.062 to -0.029) | 5.45e-08 |
| E3-A | Harmonic mean | -0.120 (-0.129 to -0.110) | 1.81e-141 |
| E3-A | Random forest | 0.055 (0.049 to 0.062) | 1.23e-66 |
| E3-A | ECS (multiplicative) | -0.280 (-0.294 to -0.265) | < 1e-300 |
| E3-C | Harmonic mean | 0.316 (0.308 to 0.324) | < 1e-300 |
| E3-C | Random forest | 0.380 (0.371 to 0.389) | < 1e-300 |
| E3-C | ECS (multiplicative) | 0.097 (0.085 to 0.109) | 2.88e-59 |
| E4 | Harmonic mean | -0.126 (-0.135 to -0.116) | 8.04e-157 |
| E4 | Random forest | 0.054 (0.048 to 0.061) | 2.35e-65 |
| E4 | ECS (multiplicative) | -0.287 (-0.300 to -0.273) | < 1e-300 |
| E5 | Harmonic mean | -0.045 (-0.085 to -0.013) | 0.0167 |
| E5 | Random forest | -0.044 (-0.098 to 0.001) | 0.0813 |
| E5 | ECS (multiplicative) | -0.163 (-0.245 to -0.093) | 3.71e-05 |
| E6 | Harmonic mean | -0.066 (-0.134 to -0.004) | 0.0533 |
| E6 | Random forest | 0.003 (-0.032 to 0.040) | 0.864 |
| E6 | ECS (multiplicative) | -0.208 (-0.330 to -0.087) | 0.000883 |

## Supplementary Table 1 — Audit ledger (P0/P1 items, status and action)

| Item | Requirement | Status | Action taken / evidence |
|---|---|---|---|
| P0-1 | E5/E6 source-overlap audit | Script ready, not runtime-run (raw inputs absent) | `code/audit_overlap_p0_1_v29…py`; E6 definition-overlap shown in Fig. 6; full recompute deferred to released inputs. |
| P0-2 | Leakage-safe nested cross-validation | Script ready, not runtime-run | `code/audit_nested_cv_p0_2_v29…py`; protocol described in Methods & Supp. Table 5. |
| P0-3 | Centrality annotation-density / study-bias | Script ready, not runtime-run | `code/audit_centrality_bias_p0_3_v29…py`; ED Fig. 1 drafted; caveat in Discussion. |
| P0-4 | E4 cross-context wording | Fixed in text | 'demonstrates cross-context transfer but not fully independent external validity'. |
| P0-5 | Three-class endpoint distinction | Fixed in text | 'six primary evaluation targets' + 'two non-independent constructs'. |
| P0-6 | Dirichlet full distribution | Real numbers reported | 1,000 draws: mean 0.333, median 0.288, 91.2% below chance, 3.2% exceed centrality (0.738). |
| P0-7 | Final clean rerun / provenance chain | Harness built; cannot execute (raw inputs absent) | `run_final_rerun_v29…sh` + input manifest + environment lock; no fabricated numbers. |
| P1-1 | 'tractability/druggability layer' canonical terminology | Fixed | Throughout Methods/Results. |
| P1-4 | E6 'pharmacological-response proxy' wording | Fixed | Results 'Cross-context transfer…' section. |
| P1-5 | 'cannot be attributed to integration alone' (RF gain) | Fixed | Results, single-layer-vs-integration paragraph. |
| P1-7 | 'Primary contrasts were pre-specified' | Fixed | Methods → Statistics. |
| P1-9 | Fig. 6 redesign; candidates → ED Fig. 4 | Fixed | Fig. 6 = pharmacological stress test (2 panels); candidates in ED Fig. 4. |

## Supplementary Table 3 — Evidence-layer overlap with E5/E6 labels

| Endpoint | Label source | Overlap with tractability/druggability layer | Evidence |
|---|---|---|---|
| E5 | nominal target of agents entering pancreatic clinical development (ClinicalTrials.gov, frozen 2024-12-31) | Yes — clinical development history favours druggable targets | qualitative; exact gene-level overlap deferred to released inputs |
| E6 | nominal target of GDSC compounds in the most sensitive tertile (125 compounds, 29 lines) | Yes — GDSC compounds are, by construction, druggable | qualitative; exact overlap deferred to released inputs |

**Honesty note:** the gene-level overlap counts require the raw E5/E6 target lists and the tractability layer, which are not redistributed in this repository. The qualitative overlap is reported in the manuscript (Results, first section); the quantitative overlap is computed by `code/audit_overlap_p0_1_v29…py` once the inputs are released.

## Supplementary Table 5 — Leakage-safe nested cross-validation protocol

| Component | Specification |
|---|---|
| Outer loop | five-fold stratified CV (seed fixed) |
| Inner loop | three-fold grid search over hyperparameters (fixed candidate grid) |
| Candidates (elastic net) | l1_ratio ∈ {0.1, 0.5, 0.9}; C ∈ {0.01, 0.1, 1.0} |
| Candidates (random forest) | n_estimators ∈ {100, 500}; max_depth ∈ {None, 8, 16} |
| Candidates (logistic regression) | C ∈ {0.01, 0.1, 1.0, 10.0} |
| Evaluation | out-of-fold predictions only; no endpoint used for tuning |
| Circularity guard | learners on E3/E3-C are circular by construction; reported for completeness only |
| Runtime status | protocol specified in `code/audit_nested_cv_p0_2_v29…py`; outer-fold results pending released inputs |

## Key supporting numbers (negative controls, sentinel, weight space)

### Negative controls on E3 (AUROC)
| Control | AUROC (95% CI) |
|---|---|
| observed ECS (multiplicative) | 0.693 (0.684–0.702) |
| replace tissue-specificity with Gaussian noise | 0.780 (0.769–0.792) |
| shuffled network layer | 0.688 (0.676–0.699) |
| permuted druggability | 0.434 (0.417–0.452) |

### Sentinel prevalence per evidence layer (genes with no annotation, %)
| Layer | % sentinel |
|---|---|
| string centrality | 5.44 |
| hpa pdac prognostic | 25.11 |
| genetic constraint | 32.12 |
| mutation freq | 46.00 |
| impc animal ko | 62.33 |
| druggability | 75.00 |
| hpa rna tissue spec | 77.45 |
| ot genetics pdac | 97.59 |
| cancer driver | 98.82 |
| **mean across 9 layers** | **57.76** |

### Support-term AUROC on E3/E3-C with and without the tractability layer
| Endpoint | full support mean | after tractability deletion |
|---|---|---|
| E3 | 0.889 | 0.535 |
| E3-C | 0.968 | 0.534 |
