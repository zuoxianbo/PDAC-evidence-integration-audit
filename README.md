# Auditing evidence integration for context-dependent therapeutic target prioritization

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
python code/recompute.py        # writes results/ncs_results.json, results/audit_report.json, results/source_data.csv
python code/weightspace.py      # writes results/weight_space.json
python code/sentinel_audit.py   # writes results/sentinel_audit.json
python code/figures.py          # writes figures/Fig1..Fig6 (.pdf and .png)
```

Runtime on a 2023 Apple silicon laptop is approximately 70 minutes, dominated
by the 2,000-resample bootstrap confidence intervals.
No network access is required at run time; no GPU is used.

## Inputs

| file | role | bytes | sha256 (truncated) |
|---|---|---|---|
| `evidence_layers_v11.json` | input | 11,443,183 | a4cb1a84574e290b... |
| `depmap_pdac_dependency.json` | input | 1,813,670 | 13f629950a0052aa... |
| `depmap_crc_dependency.json` | input | 1,814,400 | 5043490693a25a02... |
| `e5_clinical_targets.json` | input | 3,312 | 9a525599a77393e2... |
| `pdac_selective_dependency_v11.json` | input | 5,294,625 | cdf085e26404f077... |
| `GDSC_IC50.csv` | input | 2,058,983 | 9dad3b047e20b59b... |
| `Cell_lines_annotations_20181226.txt` | input | 335,355 | 77648d1cada2f325... |
| `GDSC_drug_list.csv` | input | 21,781 | b88757dd7aa79792... |
| `v17_ncs_results.json` | provenance | 85,415 | 75c5718032939020... |

Third-party inputs (DepMap, GDSC/CCLE, STRING, COSMIC, gnomAD, IMPC, Open Targets, Human Protein Assay) are not redistributed here because they are governed by their originators' licences. Each is identified above by sha256 and byte size; the harmonised evidence-layer table that the analysis consumes is released in full.

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
