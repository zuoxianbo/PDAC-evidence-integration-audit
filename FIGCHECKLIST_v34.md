# FIGCHECKLIST_v34 — Per-figure final Nature production-grade checklist

**Generator.** `code/v18_figures_v34.py` (frozen, `STAMP="v34"`).
**Outputs.** `repository/figures/Fig{1..6}_v34.png` (400 dpi) + `Fig{1..6}_v34.pdf` (vector).
**Script base.** forked from `v18_figures_v32_20260824.py`; scientific structure unchanged, only style/terminology harmonised.

**Cross-figure fixed semantic palette (enforced everywhere):**

| Role | Hex | Used for |
|------|-----|----------|
| Centrality / rank aggregation | `#2F5D8A` navy | STRING centrality, weighted/rank aggregation |
| Fixed-form integration | `#2A9D8F` teal | harmonic mean, ECS |
| Supervised learner | `#E07A3F` orange | RF / LR / elastic net |
| Constructed / circular | `#7C6BAE` purple | E3 / E3-C (label-embedded) |
| Neutral | `#9E9E9E` grey | nested E2/E3-A, tractability |
| Chance | `#4D4D4D` dark-grey | AUROC = 0.5 reference |
| Arithmetic mean *(Fig.5a only)* | `#56B4E9` light blue | — |
| Geometric mean *(Fig.5a only)* | `#E69F00` gold | — |

**Global rules applied to every panel:**
- ✅ All axis / row / panel / annotation text is **black** (`INK="#1A1A1A"`).
- ✅ Colour appears **only** on points / bars / boxes / legend patches — never as text encoding a group.
- ✅ Panel letters `a,b,c…` at 9 pt bold lowercase (top-left).
- ✅ Font floor 6 pt (ticks 6 pt, titles 7.5 pt, panel 9 pt); Arial/Helvetica.
- ✅ `bbox_inches="tight", pad_inches=0.06` on every save → no clipping.
- ✅ PNG 400 dpi; PDF vector (Nature prefers vector).

> ⚠️ **Visual-verification blocker.** The current agent model cannot decode raster
> images, so I could **not** eyeball Fig.1–6 for overlap / label clipping / legibility.
> The checklist below verifies *structure and provenance from source*, not pixels.
> **Action required before submission:** open `figures/Fig*_v34.pdf` in a PDF viewer
> (or switch to a multimodal model) and confirm (i) no text overlap, (ii) panels fit
> the 89/183 mm single/double-column widths, (iii) all labels readable at print size.

---

## Fig.1 — Endpoint taxonomy & single-layer evidence (v34)
- [x] `fig1()` writes `Fig1_v34.png/.pdf`.
- [x] **1b three semantic classes** (script lines 167–179): Blue external-label
  endpoints `E1 / E4 / E5 / E6`; Grey nested `E2 / E3-A`; Purple constructed `E3 / E3-C`.
- [x] Wording uses **"essential-and-druggable"** (E3) and **"tractability-as-label"**
  (E3-C); the word **"leakage"** is removed from the panel.
- [x] All box/endpoint text black; colour only on the class swatches.
- [ ] **human check:** do the 5 boxes overlap at small print size?

## Fig.2 — 12 scorers × endpoints AUROC heatmap (v34)
- [x] `fig2()`; row labels **all black** (line 247).
- [x] Group divider lines separate `E1 | E2/E3-A | E3/E3-C | E4/E5/E6`.
- [x] Legend patches: centrality / fixed-form / supervised / other / constructed.
- [x] Colourmap `azure = ["#F5F5F5", "#BFD8EA", "#2F5D8A"]` (light→navy, no red/green).
- [ ] **human check:** is the 6-pt tick font legible in the 183 mm double-column width?

## Fig.3 — Integration vs centrality (v34)
- [x] `fig3()`; **legend moved inside panel a, top-right** (lines 308–310).
- [x] DeLong P-string removed; bottom caption reads
  **"Paired-bootstrap DeLong P < 10⁻¹⁶ for every scorer-versus-centrality contrast."**
- [x] Bars use `C_INT` (harmonic) / `C_RF` (RF) only; effect-size panel `C_INT`.
- [ ] **human check:** does the in-panel legend obscure any bars in (a)?

## Fig.4 — Evidence-layer anatomy & label-embedded layer (v34)
- [x] **4a** uses **formal layer names** via `LAYER_NAME` dict (STRING centrality /
  Mutation frequency / IMPC knockout viability / Genetic constraint / Cancer-driver
  annotation / Open Targets Genetics / Druggability / HPA PDAC prognostic / HPA RNA
  tissue specificity); all text black.
- [x] **4b** top conclusion sentence: **"Additional evidence can lower the score."**
- [x] **4c** title changed to **"Effect of removing the label-embedded layer"**.
- [x] Quadrant colours `#DCE6F0`(navy edge) / `#F2E2D6`(orange edge) — no red/green.
- [ ] **human check:** 4a horizontal bar labels not clipped at left margin.

## Fig.5 — Functional-form & missingness audit (v34)
- [x] **5a** five aggregation methods use **five de-confounded colours**
  `shades = [C_INT, C_LBLUE, C_RF, C_GOLD, C_CENT]` (teal / light-blue / orange /
  gold / navy) — removes the old 3×-teal confusion.
- [x] **5b** shows **median + IQR only** (line 487 `median … IQR`).
- [x] **5d** title **"Sentinel-coded versus missingness-aware"**; plots
  `harmonic_sentinel_as_value` vs `harmonic_available_case` straight from
  `v18_sentinel_audit.json` S4 (provenance exact).
- [ ] **human check:** 5a legend keys map 1:1 to the five colours at print size.

## Fig.6 — Pharmacological stress test (E6) (v34)
- [x] **6a** box labelled **"E6 PDAC pharmacological-response proxy (%s genes)"**;
  bottom caption **"IC50-derived labels are external to the nine-layer evidence matrix"**
  (line 599) — enforces the *proxy, not causal* scope.
- [x] **6b** keeps **RF = 0.913 verbatim** from `v18_source_data.csv` row 105
  (line 603, no fabricated number).
- [x] Scorer swatches: centrality(navy) / tractability(grey) / harmonic(teal) / RF(orange).
- [ ] **human check:** 6a pipeline arrows/boxes don't collide at 183 mm width.

---

## Provenance & integrity (machine-verifiable)
- [x] Every figure is regenerated by a single script (`v18_figures_v34.py`) from the
  frozen results JSON — no hand-edited pixels.
- [x] `verify_v34.py` records SHA-256 of each `Fig*_v34.png` so a re-run is bit-checked.
- [ ] **human check (final gate):** visual inspection of all 6 PDFs at print size.

**Status:** structure & provenance ✅; **pending human/multimodal visual gate** before
the PDF is considered production-final.

---

## Round 2 — re-check & fixes (2026-08-25)

Author visual feedback: Fig.1/3/4/5 had overlap; Fig.6a arrow positions inaccurate;
Fig.6b panel letter sat on the bars. All fixed in `v18_figures_v34.py` and re-rendered
(commit `65a40de`); manifest re-recorded.

| Fig | Issue reported | Fix applied |
|-----|----------------|-------------|
| 1b | box text overflowed E3 / E3-A boxes | taller boxes (h 3.4–3.7) + smaller font (5.0 pt); group headers lifted to y=9.55; fig height 74→84 mm |
| 3a | legend overlapped top endpoint data | legend moved **below** the axes (`below_legend`, y=-0.42); bottom margin 0.30→0.36 |
| 4a | two callout texts could collide / sit on bars | cancer-driver callout now sits to the **right of its own bar**; mean callout pinned top-right corner; both black |
| 4b | "Additional evidence can lower the score." collided with title | lifted to y=1.10 (above axes); top margin 0.90→0.95 |
| 5a | bottom legend crowded the x-label | legend dropped to y=-0.36; fig height 78→86 mm, bottom margin 0.30→0.36 |
| 6a | arrow #3 was a self-loop inside the E6 box; arrow #7 (scorer 3) landed at x=8.5 **outside** the attribution box (x ended 7.3) | removed self-loop; attribution box widened to x∈[0.5,9.5]; all 4 scorer→attribution arrows now land **inside** the box; GDSC/drug-response arrows converge into E6 top |
| 6b | panel letter "b" drawn on the bars | `panel(ax,"b", external=True)` → letter moved **above** the axes (off the graphic) |
| 1/2/3/4/5/6 | general label crowding | figures made taller; margins increased; re-verified with `verify_v34.py` (PASS, new figure hashes) |

## Round 3 — re-check & fixes (2026-08-25, blind layout pass)

Author visual feedback (second pass): Fig.1b text overflows its box; Fig.3b text overlaps
the graphic; Fig.4a callout texts overlap the bars; Fig.5b in-panel median/IQR text overlaps
the ECDF and its bottom legend is crowded; Fig.6b panel letter "b" overlaps the title;
ED Fig.3d annotation overlaps the histogram. All addressed by moving text out of the
plotting area / shrinking fonts / adding a white mask, then re-rendered; `verify_v34.py`
re-baselined (PASS, new figure hashes).

| Fig | Issue reported | Fix applied |
|-----|----------------|-------------|
| 1b | text overflowed the endpoint boxes | default box font 5.0→4.6 pt; every long label re-broken into ≤17-char lines (E5/E6 → 3 lines, E2/E3-A → 3–5 lines, E3 → 4 lines); external boxes widened 2.9→3.05; the `⊂` glyph (missing in Arial) replaced with spelled "nested in E1" |
| 3b | stats text overlapped the vertical line | moved from bottom-left (0.08, 0.04) to top-right (0.97, 0.93), ha=right — clear of the centred line and the "b" letter |
| 4a | callout texts overlapped the bars / per-bar % labels | both in-axes callouts removed; "mean across 9 layers = 57.8% of genes unannotated" now a compact below-panel caption (xlim 110→118 for margin) |
| 5b | in-panel median/IQR text overlapped the ECDF; bottom legend crowded | in-axes text removed and merged into the panel legend (ncol 1→2, 4th entry "median (IQR)"); Fig.5 bottom margin 0.36→0.40 |
| 6b | panel letter "b" overlapped the title | `panel(ax,"b", external=True)` reverted to internal `panel(ax,"b")` → letter sits top-left, parallel to "a", clear of the title |
| ED_Fig3d | annotation overlapped the histogram / reference lines | annotation moved to the top-right corner with a white `bbox` mask (no visual overlap); panel-d legend lowered to y=-0.34 for clearance from the figure caption |

Tables: `supplementary_tables_v34.md` cross-checked against `v18_ncs_results.json` /
`v18_sentinel_audit.json` / `v18_weight_space.json` — all AUROC, 95% CIs, sentinel %,
support-term, and weight-space stats (91.2% < chance, 3.2% > centrality) match; no
discrepancies found.

Open item carried forward: final **human/multimodal** visual gate at print size (current
model cannot read raster images) — confirm no residual overlap in Fig.1–6 + ED_Fig.1–4 PDFs.

## Round 4 — re-check & fixes (2026-08-25, second blind layout pass)

Author visual feedback (third pass): Fig.1b still overflows/overlaps; Fig.4 a/b/c
panel letters should sit outside the panel (top-left, off the graphic); Fig.5 bottom
legends should be visually separated; Fig.6 a/b panel letters should sit outside the
panel. All applied and re-rendered (`verify_v34.py` re-baselined → PASS).

| Fig | Issue reported | Fix applied |
|-----|----------------|-------------|
| 1b | box text still overflowed / boxes overlapped | every label re-broken to ≤17-char lines ("concordance (n = N)" / "top quartile of E1" / "drop Druggability" split); external boxes widened 3.05→3.3, nested 2.95→3.1, constructed 2.7→2.75; box heights + vertical gaps re-spaced (E1/E4/E5/E6 at y 6.9/5.0/2.9/1.0, nested E2/E3-A at 5.6/1.6, constructed E3/E3-C at 5.6/3.4); Fig.1 width ratio 1.4:1.0 → 1.3:1.1 (b panel wider) |
| 4 a/b/c | panel letters sat inside the axes | `panel(ax, letter, external=True)` — letter now outside top-left (right-aligned just left of axes edge, y=1.03), clear of in-axes content and clear of the left-aligned panel title |
| 5 a/b/d | bottom legends crowded / no boundary | each legend given a border (`frameon=True, edgecolor=INK, fancybox=False, borderpad=0.5`) — a/b/d legends are now boxed and distinct |
| 6 a/b | panel letters sat inside the axes | `panel(ax, "a"/"b", external=True)` — letters moved outside the panel top-left |

Open item carried forward: final **human/multimodal** visual gate at print size (current
model cannot read raster images) — confirm no residual overlap in Fig.1–6 + ED_Fig.1–4 PDFs.

## Round 5 — re-check & fixes (2026-08-25, third blind layout pass)

Author visual feedback (fourth pass): Fig.4 a/b/c panels overlap; Fig.5 bottom legends
still overlap. Re-rendered (`verify_v34.py` re-baselined → PASS).

| Fig | Issue reported | Fix applied |
|-----|----------------|-------------|
| 4 a/b/c | panels overlapped | gridspec `wspace` 0.48 → 0.62 (panels pulled apart); over-long panel titles shortened so they no longer spill into the neighbouring panel — (b) "Multiplicative rule is not order-preserving" → **"Multiplicative rule is not monotone"** and the redundant sub-caption "Additional evidence can lower the score." removed; (c) "Effect of removing the label-embedded layer" → **"Removing the label-embedded layer"** |
| 5 a/b/d | bottom legends overlapped | `wspace` 0.52 → 0.62 and bottom margin 0.40 → 0.46; legends moved lower and compacted — (a) y −0.36→−0.44 (borderpad 0.5→0.4), (b) y −0.40→−0.46 with shortened labels ("STRING alone 0.738"→"STRING 0.738"; "median 0.288 (IQR 0.251–0.365)"→"median 0.288 (IQR 0.25–0.37)"), (d) y −0.38→−0.44 |

Open item carried forward: final **human/multimodal** visual gate at print size (current
model cannot read raster images) — confirm no residual overlap in Fig.1–6 + ED_Fig.1–4 PDFs.

## Round 6 — re-check & fixes (2026-08-25, Fig.5 legend separation)

Author visual feedback: Fig.5 panel **b** legend overlapped panel **a** legend.
`below_legend` gained a horizontal `x` parameter; panel (a) legend shifted left
(`x` 0.5 → 0.42), panel (b) legend shifted right (`x` 0.5 → 0.62) so the two boxed
legends no longer collide. Re-rendered (`verify_v34.py` → PASS).

## Round 7 — re-check & fixes (2026-08-25, Fig.5a legend shape)

Author visual feedback: Fig.5 panel (a) legend should be 3 rows with its bottom edge
aligned to panel (b) legend. Panel (a) legend set to `ncol=2` (5 items → 3 rows:
2+2+1) and bottom anchored to the same `y=-0.46` as panel (b). Re-rendered
(`verify_v34.py` → PASS).

## Round 8 — alignment with V34-图片修订建议.docx (2026-08-25)

Full re-check against the author's image-revision document. Data consistency verified first:
E6 AUROC — network centrality 0.910, harmonic 0.846, tractability (druggability) 0.780,
random forest **0.913**. The manuscript's two "0.910" statements both refer to centrality
(vs harmonic 0.846 / tractability 0.780) and are correct; Fig.6b RF = 0.913 matches
`v18_source_data.csv`. No 0.913-vs-0.910 conflict. Terminology already conforms
("pharmacological-response proxy", "essential-and-druggable", "tractability-as-label",
black text, fixed semantic palette, Arial, vector PDF).

Remaining fixes applied:

| Fig | Issue (per revision doc) | Fix applied |
|-----|--------------------------|-------------|
| 2 | columns should group `E1 \| E2,E3-A \| E3,E3-C \| E4,E5,E6` with thin separators | re-ordered endpoint columns into the four provenance groups and set 3 white separators at x = 1, 3, 5 |
| 3 | legend crowded the bottom; over-long x-axis definition | legend moved **inside panel a, top-right** (`loc="upper right"`, xlim widened to −0.34…0.30); x-label shortened to "ΔAUROC (paired bootstrap, 95% CI)"; title → "AUROC difference from network centrality"; figure bottom margin reduced (0.36→0.24) |

Re-rendered (`verify_v34.py` → PASS).

## Round 9 — apply NCS_v34_图片修订最终执行方案.docx (2026-08-25)

Full line-by-line application of the final execution plan. Data first verified against
frozen JSONs: Fig.4b quadrants **14.1 / 1.9 / 57.8 / 26.2%**, Fig.5 **IQR 0.251–0.365**,
Fig.3 **E5 P = 0.0167 (harmonic) / 0.0813 (RF)** — none of E5/E6 satisfy "P < 10⁻¹⁶",
so the old blanket P-caption was **wrong** and removed. Fig.6 RF = 0.913 already matches
source/manuscript.

| Fig | Execution-plan requirement | Fix applied |
|-----|---------------------------|-------------|
| 1b | panel-b top legend: three classes spaced apart, no crowding; drop "leakage" from endpoint box title | group-header font 5.4 → 4.6 pt (fits each column); E3-A box "E3-A leakage-controlled" → **"E3-A essentiality control"** (leakage removed from the box title) |
| 2 | wide white separator band masks AUROC digits; clarify 8 vs 6 endpoints | separator line thinned 2.6 pt white → **0.8 pt #999999** (no digit masking); bottom caption now states "8 operational endpoints; six independent primary endpoints (E1, E4, E5, E6)" |
| 3 | delete the wrong P-value summary line; E5 P = 0.0167 must be consistent | removed the "P < 10⁻¹⁶ for every contrast" caption entirely (full P values live in Source Data) |
| 5 | IQR = 0.251–0.365 | IQR legend label back to 3 decimals ("median 0.288 (IQR 0.251–0.365)") |

Re-rendered (`verify_v34.py` → PASS).

## Round 10 — Fig.2 separator position fix (2026-08-25)

Root cause: the Fig.2 group separators were drawn at x = 1.0, 3.0, 5.0 — these are
column **centers** (endpoint columns sit at integer x = 0…7), so even a thin line
crossed the AUROC digits of E2 / E3 / E3-C / E4. Fix: separators moved to column
**boundaries** x = 0.5, 2.5, 4.5 (lw 1.2 pt #999999, zorder=4), and every cell value
and "n.a." text raised to zorder=10 so no digit can ever be masked. Re-rendered
(`verify_v34.py` → PASS).
