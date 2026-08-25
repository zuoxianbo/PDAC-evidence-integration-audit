# Submission Package — NCS v34 (consolidated)

**Manuscript:** *Auditing when evidence integration improves therapeutic target prioritization*
**Journal / Type:** *Nature Computational Science* · **Analysis**
**Release commit:** `95b5026eb864ed2a09bdfa1db1836fc90f1ec27d`
**Results-manifest SHA-256:** `44fc3c853f85a9d66e132f1aba69f6897a586d3ff93d1cb0558f9ef758902618`
**Code repo:** https://github.com/zuoxianbo/PDAC-evidence-integration-audit
**Reproducibility gate:** `python code/verify_v34.py` → **PASS**

---

## A. Materials prepared (this package)

| File | Status |
|------|--------|
| `manuscript_v34.docx` | ✅ frozen text; author block = `[Author names and affiliations]` 🔴 placeholder; release SHA + manifest hash patched in |
| `figures/Fig1–6_v34.png` + `.pdf` | ✅ Nature production-grade, unified semantic palette, black text, vector PDF |
| `code/v18_figures_v34.py` | ✅ figure generator |
| `code/verify_v34.py` | ✅ one-command reproducibility & integrity gate (stdlib) |
| `results/v18_ncs_results.json`, `v18_sentinel_audit.json`, `v18_source_data.csv` | ✅ source data |
| `results/verify_v34_manifest.json` | ✅ SHA-256 of figures + artefacts + code |
| `AUDIT_v34.md` / `STATS_v34.md` / `FIGCHECKLIST_v34.md` / `REPRODUCIBILITY_v34.md` | ✅ audit & method docs |
| `submission_materials/cover_letter_v34.md` | ✅ with [bracket] placeholders |
| `submission_materials/author_contributions_v34.md` | 🔴 CRediT template, names pending |
| `submission_materials/competing_interests_v34.md` | 🔴 default "no competing interests", confirm |
| Extended Data Fig.1–4 (`code/v18_ed_figures_v34.py`) | ✅ generated (v34 palette) |
| Supplementary Tables 1–5 + Source Data | ✅ in `results/`, referenced by manuscript |

## B. Suggested reviewers (pool of 6 — pick 4–5 after conflict screen)

1. **Mathew Garnett** — Wellcome Sanger Institute, UK (cancer dependency / GDSC)
2. **Julio Saez-Rodriguez** — EMBL-EBI, UK (multi-omics integration / benchmarking)
3. **Joshua M. Dempster** — Broad Institute, USA (DepMap / CRISPR dependency)
4. **Pengyi Yang** — Univ. of Sydney / CMRI, AU (ML / multimodal integration)
5. **Fabian J. Theis** — Helmholtz Munich, DE (computational biology / method dev.)
6. **Rand Arafeh** — Broad Institute, USA (dependency-map interpretation)

Excluded reviewers: **none by default** — name only on a *documentable* conflict.

## C. Submission-system field map

| Field | Entry |
|-------|-------|
| Journal | Nature Computational Science |
| Content type | Analysis |
| Title | Auditing when evidence integration improves therapeutic target prioritization |
| Abstract | 148 words, no citations (verified) |
| Authors | 🔴 final list (placeholder in manuscript) |
| Keywords | therapeutic target prioritization; evidence integration; benchmark auditing; data leakage; cancer dependency; pancreatic ductal adenocarcinoma; computational biology |
| Cover letter | `cover_letter_v34.md` |
| Main manuscript | `manuscript_v34.docx` |
| Figures | 6 (≤ limit) |
| Source Data | `v18_source_data.csv` + per-figure data |
| Data / Code availability | canonical GitHub URL (in manuscript) |
| AI disclosure | LLM used for language editing / structural revision / consistency checking (in manuscript) |

## D. 30-point checklist — closure status

| # | Check | Status |
|---|-------|--------|
| 1 | Final author list/order approved | 🔴 pending (placeholder) |
| 2 | Affiliations/departments/countries correct | 🔴 pending |
| 3 | Corresponding author email/ORCID confirmed | 🔴 pending |
| 4 | Title exact | ✅ |
| 5 | Content type = Analysis | ✅ |
| 6 | Main text ≤ 3,500 words | ✅ (frozen) |
| 7 | Abstract 100–150 words, no citations | ✅ 148 words, none |
| 8 | ≤ 6 display items | ✅ 6 |
| 9 | Results/Methods subheads; Discussion no subheads | ✅ |
| 10 | References ≤ ~50, traceable | ✅ (frozen) |
| 11 | Intro claims cited | ✅ (frozen) |
| 12 | No Results external-citation substitution | ✅ (frozen) |
| 13 | Discussion citations support claims | ✅ (frozen) |
| 14 | 6 endpoints provenance/independence documented | ✅ (STATS_v34) |
| 15 | E3/E3-C labelled constructed/circular | ✅ |
| 16 | E4 = cross-context transfer, not external validation | ✅ |
| 17 | E5/E6 tractability overlap disclosed | ✅ |
| 18 | Sentinel encoding + missingness audit reproducible | ✅ (verify_v34 PASS) |
| 19 | Nested-CV seed/grid in code | ✅ (audit §4) |
| 20 | Negative controls + community resampling reproducible | ✅ |
| 21 | Figures have legends/units/n | ✅ (FigCHECKLIST) |
| 22 | ED figures + Supp Tables present/cross-referenced | ✅ |
| 23 | Source Data complete/machine-readable | ✅ |
| 24 | Public-data URLs/versions tested | ✅ (canonical repo live) |
| 25 | Code repo reproduces outputs | ✅ (verify_v34 PASS; repo uploaded) |
| 26 | Git SHA + manifest hash in manuscript point to release | ✅ patched to 95b5026 / 44fc3c85 |
| 27 | Data/Code availability consistent with repo | ✅ |
| 28 | Funding/Contributions/Competing/Ethics verified | 🔴 pending author |
| 29 | AI-use disclosure accurate | ✅ (in manuscript) |
| 30 | Cover letter / reviewers / disclosures final | 🔴 pending author |

**GO after** the 🔴 author-metadata items (1–3, 28, 30) are completed. All
science, figures, code, statistics and reproducibility gates are GREEN.

## E. Go / No-Go

| Item | Criterion | Status |
|------|-----------|--------|
| Manuscript | v34 with real authors inserted | GO after 🔴 insertion |
| Core science | No numerical/discrepancy | ✅ GO |
| References | Selective, current | ✅ GO |
| Code | Public + clean rerun verified | ✅ GO (repo live, verify PASS) |
| Reporting Summary | Prepared, consistent | ✅ READY |
| Reviewer pool | 4–5 conflict-checked | 🔴 PENDING author screen |
| Cover letter | Importance + NCS fit + disclosures | ✅ READY w/ placeholders |
| Submission metadata | Match across system/manuscript/code | ✅ after author fill |
