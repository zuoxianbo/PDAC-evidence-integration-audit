#!/usr/bin/env bash
# ===========================================================================
# run_final_rerun.sh
# One-command smoke-test wrapper for the PDAC evidence-integration audit.
# Part of the PDAC evidence-integration audit repository.
#
# WHAT IT DOES
#   1. Gates on raw-input presence (refuses with a clear message if absent,
#      so no silent partial run can occur).
#   2. Runs the pipeline in order:
#        recompute.py       -> results/ncs_results.json,
#                                  results/audit_report.json,
#                                  results/source_data.csv
#        weightspace.py     -> results/weight_space.json
#        sentinel_audit.py  -> results/sentinel_audit.json
#        figures.py         -> figures/Fig1..Fig6 (.pdf and .png)
#   3. Writes a run record (git commit SHA + results-manifest sha256) to
#      run_record.txt.
#
# HONESTY CAVEAT (IMPORTANT)
#   The raw third-party inputs are NOT redistributed in this repo (see
#   final_input_manifest.csv and the manifest's
#   data_redistribution_statement). This script therefore REFUSES to run
#   unless every required input is present in IN_DIR.
#
#   ADDITIONAL CAVEAT — HARDCODED PATHS (not edited here, by design):
#     code/recompute.py hardcodes ROOT / OUT / GDSC_DIR to a different
#     author machine:
#       ROOT = /Users/zuoxianbo/Desktop/zuoxb-虚拟科研系统-MAC/outputs/pdac-convergent-evidence-v14
#       OUT  = /Users/zuoxianbo/Desktop/SCI论文/胰腺癌
#       GDSC_DIR = /Users/zuoxianbo/Desktop/zuoxb-虚拟科研系统-MAC/Zuoxb-Data-Medicine-platform/models/singlecell/scfoundation/DeepCDR/data
#     This wrapper does NOT modify that file. For a real clean rerun you MUST
#     EITHER place the released inputs so those paths resolve, OR patch the
#     four path constants in recompute.py to point at IN_DIR / OUT_DIR.
#     The input-presence gate below is what prevents a silent partial run.
# ===========================================================================

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Override with:  IN_DIR=/path/to/inputs OUT_DIR=/path/to/out ./run_final_rerun_*.sh
IN_DIR="${IN_DIR:-$REPO_ROOT/data}"
OUT_DIR="${OUT_DIR:-$REPO_ROOT}"

# Required raw inputs (sha256 / byte sizes in final_input_manifest.csv)
REQUIRED_INPUTS=(
  evidence_layers_v11.json
  depmap_pdac_dependency.json
  depmap_crc_dependency.json
  e5_clinical_targets.json
  pdac_selective_dependency_v11.json
  GDSC_IC50.csv
  Cell_lines_annotations_20181226.txt
  GDSC_drug_list.csv
)

echo "== PDAC audit final rerun  =="
echo "Repo root : $REPO_ROOT"
echo "IN_DIR    : $IN_DIR"
echo "OUT_DIR   : $OUT_DIR"

# ---------------------------------------------------------------------------
# 1) GATE — refuse if any required raw input is missing.
# ---------------------------------------------------------------------------
missing=0
for f in "${REQUIRED_INPUTS[@]}"; do
  if [[ ! -f "$IN_DIR/$f" ]]; then
    echo "MISSING INPUT: $IN_DIR/$f" >&2
    missing=1
  fi
done
if [[ $missing -eq 1 ]]; then
  echo "" >&2
  echo "REFUSAL: one or more raw inputs are missing. The pipeline was NOT run." >&2
  echo "Raw inputs are not redistributed per licence. Obtain them from the" >&2
  echo "originating sources, place them in IN_DIR, then re-run this script." >&2
  echo "Current IN_DIR='$IN_DIR' (override: IN_DIR=/path/to/inputs). See" >&2
  echo "REPRODUCIBILITY.md for the full data-source list." >&2
  exit 1
fi
echo "All ${#REQUIRED_INPUTS[@]} required raw inputs present at IN_DIR. Proceeding."

# ---------------------------------------------------------------------------
# 2) Record provenance placeholders.
# ---------------------------------------------------------------------------
COMMIT_SHA="$(git -C "$REPO_ROOT" rev-parse HEAD 2>/dev/null || echo PLACEHOLDER_COMMIT_SHA)"
RUN_START="$(date -u +%Y-%m-%dT%H:%M:%SZ)"

# ---------------------------------------------------------------------------
# 3) Run the pipeline, in order. (Assumes recompute.py paths are resolved;
#    see the HARDCODED PATHS caveat above.)
# ---------------------------------------------------------------------------
python "$REPO_ROOT/code/recompute.py"        # -> results/ncs_results.json, audit_report.json, source_data.csv
python "$REPO_ROOT/code/weightspace.py"      # -> results/weight_space.json
python "$REPO_ROOT/code/sentinel_audit.py"   # -> results/sentinel_audit.json
python "$REPO_ROOT/code/figures.py"          # -> figures/Fig1..Fig6 (.pdf and .png)

# ---------------------------------------------------------------------------
# 4) Write the run record: commit SHA + results-manifest sha256.
# ---------------------------------------------------------------------------
MANIFEST_HASH="$(cat \
  "$REPO_ROOT/results/ncs_results.json" \
  "$REPO_ROOT/results/audit_report.json" \
  "$REPO_ROOT/results/source_data.csv" \
  "$REPO_ROOT/results/sentinel_audit.json" \
  "$REPO_ROOT/results/weight_space.json" \
  | shasum -a 256 | awk '{print $1}')"

RUN_END="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
cat > "$REPO_ROOT/run_record.txt" <<EOF
PDAC audit final rerun record 
git_commit_sha: $COMMIT_SHA
run_start_utc:  $RUN_START
run_end_utc:    $RUN_END
results_manifest_sha256: $MANIFEST_HASH
NOTE: This record is authoritative only after a clean rerun with the released
      raw inputs present. In the current repository the raw inputs are absent,
      so this file is produced ONLY when the input gate above passes.
EOF

echo "== Done. Record written to run_record.txt =="
echo "git_commit_sha=$COMMIT_SHA"
echo "results_manifest_sha256=$MANIFEST_HASH"
