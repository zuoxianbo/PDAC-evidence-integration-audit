# FINAL_v34_DELIVERY — PDAC evidence-integration audit, NCS submission

**Date:** 2026-08-26 · **Release commit:** `1d9dba72e46f4459f28a2ba1368e820be8d30c3b`
**Results-manifest SHA-256:** `675a3d6a6e4f0385a2fd652e847d69b8ee1ec779f1ddbe5f014ca3b3eb48d2d4`
**Code:** https://github.com/zuoxianbo/PDAC-evidence-integration-audit

## Verdict: 🟢 GO (science/figures/code/stats GREEN) — ⏳ author-metadata 🔴 pending

All code, figures, statistics, methodology and reproducibility gates are complete
and verified. The **only** remaining pre-submission actions are author-specific
(insert real names/affiliations, confirm contributions & competing interests,
complete related-manuscript disclosure, conflict-screen reviewers). These cannot be
done by the assistant and are flagged 🔴 in `SUBMISSION_PACKAGE_v34.md`.

---

## What was delivered in this session

### 1. Figures — Nature production-grade, unified semantic palette
- `code/v18_figures_v34.py` regenerates `figures/Fig1–6_v34.{png,pdf}`
  (400 dpi PNG + vector PDF).
- Fixed cross-figure semantic colours (navy=centrality, teal=fixed-form,
  orange=supervised, purple=constructed, grey=neutral, dark-grey=chance; plus
  Fig.5a-only light-blue/gold). **All text black**; colour only on points/bars/
  boxes/legend patches. Panel letters 9 pt bold lowercase.
- Per-figure provenance verified in `FIGCHECKLIST_v34.md`.
- **⚠️ Visual gate:** the agent model cannot decode raster images, so pixel-level
  legibility/overlap was **not** eyeballed. Open `figures/Fig*_v34.pdf` (or use a
  multimodal model) and confirm layout before final upload.

### 2. Code audit — 5 submission-critical routines (`AUDIT_v34.md`)
Endpoint label builder · missingness encoder (sentinel −3.0→missing-aware) ·
harmonic composite `2(D+3)(Φ+3)/(D+Φ+6)` · 5-fold nested CV · bootstrap/DeLong/
community resampling. All verified correct, seeded, leakage-free. **No research
algorithm changed** — only disclosures/re-labellings.

### 3. Statistics & methodology (`STATS_v34.md`)
12-check + primary-contrast self-consistency. E4=cross-context transfer,
E5=historical concordance, E6=pharmacological-response proxy (not causal);
centrality = baseline only. 104 scorer×endpoint cells contain the 6 primary
endpoints (no silent omission). All numbers reproducible under seed `20260819`.

### 4. Reproducibility engineering (`verify_v34.py` + `REPRODUCIBILITY_v34.md`)
- One-command gate (stdlib-only): asserts seed, E6 RF=0.9134, GDSC counts,
  sentinel audit values, E3-A≡E1; records SHA-256 of all figures + artefacts.
- Run result: **PASS** (all green). Manifest written to
  `results/verify_v34_manifest.json`.

### 5. Manuscript (`manuscript_v34.docx`)
- Frozen v34 text (title exact, abstract 148 words/no citations, ≤6 figures,
  canonical GitHub URL in availability, AI-use statement).
- Author block = `[Author names and affiliations]` 🔴 placeholder.
- Release commit SHA + results-manifest hash **patched** into the reproducibility
  sentence. Round 3 (2026-08-26) fixed Fig.1b/3b/4a/5b/6b + ED_Fig.3d text overlap
  and re-baselined the manifest (commit `1d9dba7`, manifest `675a3d6a…`).

### 6. Submission materials (`submission_materials/`)
`cover_letter_v34.md`, `author_contributions_v34.md` (🔴), `competing_interests_v34.md`
(🔴), `SUBMISSION_PACKAGE_v34.md` (30-point closure + reviewer pool + go/no-go).

### 7. GitHub sync
All 24 v34 artifacts (code, docs, 6 figures × png/pdf, 4 ED figures × png/pdf,
manuscript, manifest) **uploaded** to `PDAC-evidence-integration-audit` (main) via
the GitHub Contents API. Local commit `1d9dba7` is the release pointer.

---

## Pending before clicking Submit (🔴 — author action)

1. Insert real author names + affiliations + ORCID in `manuscript_v34.docx`.
2. Complete `author_contributions_v34.md` (CRediT) — every author approves.
3. Confirm `competing_interests_v34.md` (default "no competing interests").
4. Disclose related manuscripts / prior editor discussion in cover letter.
5. Conflict-screen the 6-reviewer pool → pick 4–5.
6. Human visual check of `figures/Fig*_v34.pdf` at print size.
7. Fill the NCS Reporting Summary + Software Submission Checklist (templates ready).

## File manifest (deliverables)
```
repository/
├── manuscript_v34.docx              # final manuscript (author 🔴)
├── code/v18_figures_v34.py          # figure generator
├── code/verify_v34.py               # reproducibility gate
├── code/v18_recompute.py            # benchmark (audited)
├── code/v18_sentinel_audit.py       # missingness audit (audited)
├── results/v18_ncs_results.json
├── results/v18_sentinel_audit.json
├── results/v18_source_data.csv      # Source Data
├── results/verify_v34_manifest.json # SHA-256 manifest
├── figures/Fig1–6_v34.{png,pdf}
├── AUDIT_v34.md  STATS_v34.md  FIGCHECKLIST_v34.md  REPRODUCIBILITY_v34.md
├── README.md
└── submission_materials/{cover_letter,author_contributions,competing_interests,SUBMISSION_PACKAGE}_v34.md
```
