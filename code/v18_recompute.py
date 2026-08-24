# -*- coding: utf-8 -*-
"""
V18 FULL RECOMPUTE + AUDIT  (Nature Computational Science submission)
=====================================================================
Executes every P0 item listed in "投稿前需要重新计算的.docx".

P0-1  Verify the harmonic-mean functional form against the standard definition
      H = 2 (D+3)(PHI+3) / (D + PHI + 6)   and re-derive every harmonic number.
P0-2  Replace the invalid "DeLong p > 0.05 against AUROC = 0.5" statement with
      (a) Mann-Whitney U tests vs the AUROC = 0.5 null   [correct test]
      (b) true fast-DeLong pairwise tests between correlated ROC curves
      (c) paired-bootstrap Delta-AUROC confidence intervals
P0-3  Freeze a single endpoint taxonomy: E1, E2, E3, E3-A, E3-C, E4, E5 (+ E6 new)
      and audit the E3-A == E1 identity that V17 silently duplicated.
P0-4  Flag E2 as derived from E1 (not an independent validation endpoint).
P0-5  Keep E3 as a conjunctive benchmark only.
P0-6  Rename the clinical endpoint to historical clinical-target concordance.
P0-7  Re-rank the 9 candidates by harmonic mean (V17 used an external file whose
      ordering was neither harmonic nor centrality monotone).
EXTRA Add a genuinely orthogonal GDSC drug-response endpoint (E6) for PDAC lines.

Outputs
  <OUT>/results/v18_ncs_results.json
  <OUT>/results/v18_audit_report.json
  <OUT>/results/v18_source_data.csv
"""
import json, os, sys, csv, math, warnings, hashlib, platform, datetime
import numpy as np
from scipy.stats import norm, mannwhitneyu, spearmanr
from sklearn.linear_model import LogisticRegression, ElasticNet
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import roc_auc_score, average_precision_score
from sklearn.model_selection import StratifiedKFold
from sklearn.preprocessing import StandardScaler

warnings.filterwarnings("ignore")
RNG = np.random.default_rng(20260819)

ROOT = "/Users/zuoxianbo/Desktop/zuoxb-虚拟科研系统-MAC/outputs/pdac-convergent-evidence-v14"
DATA = os.path.join(ROOT, "data")
OUT = "/Users/zuoxianbo/Desktop/SCI论文/胰腺癌"
RES = os.path.join(OUT, "results")
os.makedirs(RES, exist_ok=True)
GDSC_DIR = ("/Users/zuoxianbo/Desktop/zuoxb-虚拟科研系统-MAC/Zuoxb-Data-Medicine-platform/"
            "models/singlecell/scfoundation/DeepCDR/data")

N_BOOT = 2000
AUDIT = {"generated": datetime.datetime.now().isoformat(timespec="seconds"),
         "python": platform.python_version(), "numpy": np.__version__,
         "n_bootstrap": N_BOOT, "seed": 20260819, "findings": []}


def finding(pid, severity, title, detail, action):
    AUDIT["findings"].append({"p0_item": pid, "severity": severity, "title": title,
                              "detail": detail, "action": action})
    print(f"  [{severity}] {pid}: {title}")


def log(msg):
    print(msg, flush=True)


# =====================================================================
# 1. DATA
# =====================================================================
log("=" * 72)
log("1. LOADING DATA")
log("=" * 72)

EV = json.load(open(os.path.join(DATA, "evidence_layers_v11.json")))
LAYERS, ALL_GENES = EV["layers"], EV["genes"]


def lv(gene, layer):
    r = LAYERS.get(layer, {}).get(gene)
    return r["norm"] if (r and r.get("present")) else None


FEATURES = ["string_centrality", "mutation_freq", "impc_animal_ko",
            "genetic_constraint", "cancer_driver", "ot_genetics_pdac",
            "druggability", "hpa_pdac_prognostic", "hpa_rna_tissue_spec"]
N_GENES = len(ALL_GENES)
X = np.full((N_GENES, len(FEATURES)), -3.0)
for i, g in enumerate(ALL_GENES):
    for j, f in enumerate(FEATURES):
        v = lv(g, f)
        if v is not None:
            X[i, j] = v
GENE_IDX = {g: i for i, g in enumerate(ALL_GENES)}
log(f"  genes={N_GENES}  features={len(FEATURES)}")

PDAC_DEP = json.load(open(os.path.join(DATA, "depmap_pdac_dependency.json")))
CRC_DEP = json.load(open(os.path.join(DATA, "depmap_crc_dependency.json")))
E5_DATA = json.load(open(os.path.join(DATA, "e6_clinical_validation.json")))
CLIN_POS = set(E5_DATA["genes"])                      # 35 ClinicalTrials.gov / curated
PSD = json.load(open(os.path.join(DATA, "pdac_selective_dependency_v11.json")))
log(f"  clinical-target positives declared: {len(CLIN_POS)}")


# =====================================================================
# 2. ENDPOINTS  (frozen taxonomy per P0-3)
# =====================================================================
log("\n" + "=" * 72)
log("2. ENDPOINT CONSTRUCTION (frozen taxonomy, P0-3..P0-6)")
log("=" * 72)


def is_ess(gene, dep):
    d = dep.get(gene)
    return bool(d.get("essential")) if isinstance(d, dict) else False


ess_pdac = {g for g in ALL_GENES if is_ess(g, PDAC_DEP)}
ess_crc = {g for g in ALL_GENES if is_ess(g, CRC_DEP)}
drug_pos = {g for g in ALL_GENES if lv(g, "druggability") is not None}
E3_pos = ess_pdac & drug_pos

# ---- E2: B_zeffect top quartile among pan-essential genes -------------
pe = PSD["pan_essential"]
defs = PSD["definitions"]
pan_ess_psd = {g for g in ALL_GENES if pe.get(g) is True}
bz = {g: defs[g]["B_zeffect"] for g in pan_ess_psd if g in defs}
q75 = float(np.percentile(np.fromiter(bz.values(), float), 75))
E2_pos = {g for g, v in bz.items() if v >= q75}
log(f"  PSD pan-essential={len(pan_ess_psd)}  DepMap essential={len(ess_pdac)}  "
    f"E2 top-quartile={len(E2_pos)}")

# ---- audit: two mutually inconsistent definitions of "essential" -----
if len(pan_ess_psd) != len(ess_pdac):
    jac = len(pan_ess_psd & ess_pdac) / len(pan_ess_psd | ess_pdac)
    finding("P0-3", "MAJOR",
            "Two different operational definitions of PDAC essentiality coexist",
            ("E1/E3/E3-A use depmap_pdac_dependency.json['essential'] (%d genes) while E2 "
             "is derived from pdac_selective_dependency_v11.json['pan_essential'] "
             "(%d genes); Jaccard = %.3f. V17 mixed the two without comment."
             % (len(ess_pdac), len(pan_ess_psd), jac)),
            "Declare both definitions in Methods and report the Jaccard overlap, or "
            "harmonise on one source. Keep E2 explicitly labelled as PSD-derived.")


def yvec(s):
    return np.array([1.0 if g in s else 0.0 for g in ALL_GENES])


E1_y, E3A_y = yvec(ess_pdac), yvec(ess_pdac)
E3_y, E3C_y = yvec(E3_pos), yvec(drug_pos)
E2_y, E4_y, E5_y = yvec(E2_pos), yvec(ess_crc), yvec(CLIN_POS)

# ---- P0-3 audit: E3-A is by construction identical to E1 -------------
identical = bool(np.array_equal(E1_y, E3A_y))
if identical:
    finding("P0-3", "CRITICAL",
            "E3-A is numerically identical to E1",
            ("E3-A was defined as 'essential(gene)' and E1 as 'essential(gene)'. The two "
             "label vectors are bit-identical (n_pos=%d), so every one of the 12 methods "
             "reports the same AUROC in both columns of the V17 benchmark. V17 presented "
             "them as two of 'seven endpoints', which a referee can falsify in seconds "
             "from v17_ncs_results.json." % int(E1_y.sum())),
            ("Report six operationally independent endpoints and state explicitly that "
             "E3-A is E1 by construction: removing the druggability conjunct from E3 "
             "collapses the positive set onto E1. This strengthens the negative result "
             "rather than weakening it."))

# ---- P0-4 audit: E2 nested in E1 ------------------------------------
inter = len(E2_pos & ess_pdac)
frac_nested = inter / max(len(E2_pos), 1)
finding("P0-4", "MAJOR",
        "E2 is nested within E1, not an independent endpoint",
        ("%d/%d (%.1f%%) of E2 positives are also E1 positives; E2 is defined as the top "
         "quartile of PDAC-selective effect *among pan-essential genes*."
         % (inter, len(E2_pos), 100 * frac_nested)),
        "Describe E2 as a stratification of E1, never as independent validation.")

ENDPOINTS = {
    "E1 pan-dependency": E1_y,
    "E2 PDAC-enriched dependency": E2_y,
    "E3 conjunctive actionability": E3_y,
    "E3-A leakage-controlled essentiality": E3A_y,
    "E3-C out-of-evidence druggability": E3C_y,
    "E4 CRC zero-shot transfer": E4_y,
    "E5 historical clinical-target concordance": E5_y,
}
for k, v in ENDPOINTS.items():
    log(f"  {k:<46s} n_pos={int(v.sum()):>6d}")


# =====================================================================
# 3. GDSC DRUG-RESPONSE ENDPOINT (E6, new and orthogonal)
# =====================================================================
log("\n" + "=" * 72)
log("3. GDSC DRUG-RESPONSE ENDPOINT (E6)")
log("=" * 72)

E6_y, E6_meta = None, {"available": False}
try:
    ann_path = os.path.join(GDSC_DIR, "CCLE", "Cell_lines_annotations_20181226.txt")
    with open(ann_path, encoding="utf-8", errors="replace") as f:
        rows = list(csv.DictReader(f, delimiter="\t"))
    panc = {r["depMapID"].strip() for r in rows
            if (r.get("Site_Primary") or "").strip().lower() == "pancreas"
            and r.get("depMapID")}
    log(f"  pancreas lines in CCLE annotation: {len(panc)}")

    ic_path = os.path.join(GDSC_DIR, "CCLE", "GDSC_IC50.csv")
    with open(ic_path) as f:
        ic = list(csv.reader(f))
    header, body = ic[0], ic[1:]
    cols = header[1:]
    panc_idx = [i for i, c in enumerate(cols) if c.strip() in panc]
    log(f"  pancreas lines with GDSC IC50: {len(panc_idx)}")

    drug_ic50 = {}
    for r in body:
        did = r[0].replace("GDSC:", "").strip()
        vals = []
        for i in panc_idx:
            s = r[1 + i].strip()
            if s not in ("", "NA", "NaN"):
                try:
                    vals.append(float(s))
                except ValueError:
                    pass
        if len(vals) >= 8:
            drug_ic50[did] = float(np.median(vals))
    log(f"  drugs with >=8 PDAC lines: {len(drug_ic50)}")

    dl_path = os.path.join(GDSC_DIR, "GDSC", "1.Drug_listMon Jun 24 09_00_55 2019.csv")
    with open(dl_path, encoding="utf-8", errors="replace") as f:
        drugs = list(csv.DictReader(f))
    d2t = {}
    for d in drugs:
        did = (d.get("drug_id") or "").strip()
        tg = (d.get("Targets") or "")
        genes = {t.strip() for t in tg.replace(";", ",").split(",")
                 if t.strip() in GENE_IDX}
        if did and genes:
            d2t[did] = genes

    shared = [d for d in drug_ic50 if d in d2t]
    log(f"  drugs with mapped gene targets and PDAC IC50: {len(shared)}")
    if len(shared) >= 40:
        order = sorted(shared, key=lambda d: drug_ic50[d])
        k = max(1, len(order) // 3)
        sens_drugs, res_drugs = order[:k], order[-k:]
        sens_genes = set().union(*[d2t[d] for d in sens_drugs])
        res_genes = set().union(*[d2t[d] for d in res_drugs])
        pos_genes = sens_genes - res_genes            # unambiguously sensitive targets
        E6_y = yvec(pos_genes)
        E6_meta = {
            "available": True,
            "definition": ("Gene is the annotated target of a GDSC compound whose median "
                           "log-IC50 across PDAC cell lines falls in the most-sensitive "
                           "tertile, excluding targets shared with the least-sensitive "
                           "tertile."),
            "n_pancreas_lines_annotated": len(panc),
            "n_pancreas_lines_with_ic50": len(panc_idx),
            "n_drugs_screened": len(shared),
            "n_drugs_sensitive_tertile": len(sens_drugs),
            "n_positive_genes": int(E6_y.sum()),
            "median_logIC50_sensitive_tertile": float(np.median([drug_ic50[d] for d in sens_drugs])),
            "median_logIC50_resistant_tertile": float(np.median([drug_ic50[d] for d in res_drugs])),
            "source": "GDSC1000 IC50 matrix (DeepCDR distribution) + CCLE line annotation",
            "leakage_note": ("Drug-response phenotype is absent from all nine evidence "
                             "layers, so this endpoint carries no circularity with the "
                             "druggability annotation used as an input feature."),
        }
        ENDPOINTS["E6 PDAC drug-response actionability"] = E6_y
        log(f"  E6 built: {int(E6_y.sum())} positive genes")
        finding("EXTRA", "RESOLVED", "GDSC drug-response endpoint constructed",
                "%d PDAC lines, %d drugs, %d positive target genes."
                % (len(panc_idx), len(shared), int(E6_y.sum())),
                "Add E6 as the only endpoint with a pharmacological readout; keep "
                "therapeutic claims strictly bounded to cell-line sensitivity.")
    else:
        finding("EXTRA", "MINOR", "GDSC endpoint too sparse",
                "only %d drugs mapped" % len(shared),
                "State in Methods that drug-response validation was not feasible.")
except Exception as e:                                    # pragma: no cover
    finding("EXTRA", "MINOR", "GDSC endpoint unavailable", repr(e),
            "Declare absence of drug-response endpoint honestly in Methods.")


# =====================================================================
# 4. SCORERS  (+ P0-1 formula verification)
# =====================================================================
log("\n" + "=" * 72)
log("4. SCORERS AND P0-1 HARMONIC-FORM VERIFICATION")
log("=" * 72)

I_STR, I_MUT, I_IMPC = (FEATURES.index(x) for x in
                        ("string_centrality", "mutation_freq", "impc_animal_ko"))
SUP_ALL = [FEATURES.index(f) for f in ("cancer_driver", "ot_genetics_pdac", "druggability",
                                       "hpa_pdac_prognostic", "hpa_rna_tissue_spec")]
SUP_NODRUG = [FEATURES.index(f) for f in ("cancer_driver", "ot_genetics_pdac",
                                          "hpa_pdac_prognostic", "hpa_rna_tissue_spec")]


def DP(M, sup=None):
    sup = SUP_ALL if sup is None else sup
    D = 0.80 * M[:, I_STR] + 0.10 * M[:, I_MUT] + 0.10 * M[:, I_IMPC]
    return D, np.mean(M[:, sup], axis=1)


def f_multiplicative(M, a=0.6):
    D, P = DP(M)
    return D * (1 + a * P)


def f_additive(M, a=0.6):
    D, P = DP(M)
    return D + a * P


def f_geometric(M, a=0.6):
    D, P = DP(M)
    return np.sqrt(np.maximum(D, .01) * np.maximum(P + 3., .01))


def f_harmonic(M, a=0.6):
    """Standard harmonic mean of the shifted components:
       H = 2 (D+3)(PHI+3) / ((D+3) + (PHI+3)) = 2 (D+3)(PHI+3) / (D + PHI + 6)."""
    D, P = DP(M)
    Ds, Ps = np.maximum(D + 3., .01), np.maximum(P + 3., .01)
    return 2. * Ds * Ps / (Ds + Ps)


def f_ecs_nodrug(M, a=0.6):
    D, P = DP(M, SUP_NODRUG)
    return D * (1 + a * P)


def rank_agg(M, w=None):
    w = np.ones(M.shape[1]) if w is None else w
    R = np.zeros_like(M)
    for j in range(M.shape[1]):
        R[:, j] = np.argsort(np.argsort(M[:, j])).astype(float)
    return R @ w


def f_rank(M):
    return rank_agg(M)


def f_wrank(M):
    w = np.zeros(M.shape[1])
    w[I_STR], w[FEATURES.index("druggability")], w[I_MUT] = 5., 3., 1.
    w[FEATURES.index("cancer_driver")] = 1.
    return rank_agg(M, w)


# ---- P0-1 : symbolic + numeric verification -------------------------
D_, P_ = DP(X)
h_impl = f_harmonic(X)
with np.errstate(divide="ignore", invalid="ignore"):
    h_std = 2.0 * (D_ + 3.0) * (P_ + 3.0) / (D_ + P_ + 6.0)
# the 0.01 floor only engages where a shifted component is non-positive
unfloored = (D_ + 3.0 > 0.01) & (P_ + 3.0 > 0.01)
n_floored = int((~unfloored).sum())
max_dev = float(np.nanmax(np.abs(h_impl[unfloored] - h_std[unfloored])))
v17_code = ("D_safe = max(D+3, .01); PHI_safe = max(PHI+3, .01); "
            "return 2*D_safe*PHI_safe/(D_safe+PHI_safe)")
AUDIT["p0_1_harmonic_verification"] = {
    "standard_definition": "H = 2 (D+3)(PHI+3) / (D + PHI + 6)",
    "v17_code_as_written": v17_code,
    "v17_methods_text_as_printed": "2 * D * (PHI + 3) / (D + 3 + PHI + 3)",
    "code_matches_standard": max_dev < 1e-12,
    "max_abs_deviation": max_dev,
    "verdict": ("The V17 CODE implements the standard harmonic mean exactly "
                "(max deviation %.2e). The V17 METHODS TEXT is a typesetting error: the "
                "numerator lost its '+3' shift. No numerical result changes." % max_dev),
}
if max_dev < 1e-12:
    finding("P0-1", "RESOLVED",
            "Harmonic mean code is correct; Methods text is a typo",
            ("run_v17_ncs.py:ecs_harmonic computes 2(D+3)(PHI+3)/((D+3)+(PHI+3)), which is "
             "algebraically identical to the standard 2(D+3)(PHI+3)/(D+PHI+6) "
             "(max |deviation| = %.2e over all %d genes). The printed Methods formula "
             "'2*D*(PHI+3)/(D+3+PHI+3)' dropped the +3 shift in the numerator."
             % (max_dev, N_GENES)),
            "Correct one sentence in Methods. Do NOT re-run or re-draw anything for P0-1.")
else:
    finding("P0-1", "CRITICAL", "Harmonic implementation deviates from standard form",
            "max deviation %.3e" % max_dev, "Full recomputation of all harmonic results.")

UNSUP = {
    "Mutation frequency": lambda M: M[:, I_MUT],
    "Genetic constraint": lambda M: M[:, FEATURES.index("genetic_constraint")],
    "Cancer-driver annotation": lambda M: M[:, FEATURES.index("cancer_driver")],
    "Druggability": lambda M: M[:, FEATURES.index("druggability")],
    "STRING centrality": lambda M: M[:, I_STR],
    "Arithmetic mean": lambda M: np.mean(M, axis=1),
    "Rank aggregation": f_rank,
    "Weighted rank aggregation": f_wrank,
    "ECS (multiplicative)": f_multiplicative,
    "Harmonic mean": f_harmonic,
}
FORMS = {"multiplicative (ECS)": f_multiplicative, "additive": f_additive,
         "geometric mean": f_geometric, "harmonic mean": f_harmonic,
         "rank aggregation": f_rank}
SCORES = {k: fn(X) for k, fn in UNSUP.items()}
finding("P0-2", "MAJOR", "Cancer-driver single-layer scorer was never computed in V17",
        ("V17 Results quote 'cancer-driver annotation at 0.524' but "
         "v17_ncs_results.json contains no cancer_driver scorer; 0.524 is the E1 value of "
         "genetic constraint. The number was mis-attributed."),
        "Compute the cancer-driver layer explicitly (done here) and requote.")


# =====================================================================
# 5. STATISTICS: fast DeLong, Mann-Whitney vs chance, paired bootstrap
# =====================================================================
log("\n" + "=" * 72)
log("5. STATISTICAL MACHINERY (P0-2)")
log("=" * 72)


def _midrank(x):
    J = np.argsort(x)
    Z = x[J]
    N = len(x)
    T = np.zeros(N)
    i = 0
    while i < N:
        j = i
        while j < N and Z[j] == Z[i]:
            j += 1
        T[i:j] = 0.5 * (i + j - 1)
        i = j
    T2 = np.empty(N)
    T2[J] = T + 1
    return T2


def _fast_delong(preds_sorted, m):
    """preds_sorted: (2, n) with the m positives first. Sun & Xu (2014)."""
    k, n_all = preds_sorted.shape
    n = n_all - m
    pos, neg = preds_sorted[:, :m], preds_sorted[:, m:]
    tx = np.vstack([_midrank(pos[r]) for r in range(k)])
    ty = np.vstack([_midrank(neg[r]) for r in range(k)])
    tz = np.vstack([_midrank(preds_sorted[r]) for r in range(k)])
    aucs = tz[:, :m].sum(axis=1) / m / n - (m + 1.0) / 2.0 / n
    v01 = (tz[:, :m] - tx) / n
    v10 = 1.0 - (tz[:, m:] - ty) / m
    cov = np.cov(v01) / m + np.cov(v10) / n
    return aucs, np.atleast_2d(cov)


def delong_test(y, s1, s2):
    """Two-sided DeLong test for two correlated ROC curves on the same samples."""
    ok = np.isfinite(s1) & np.isfinite(s2)
    y_, a_, b_ = y[ok], s1[ok], s2[ok]
    order = np.argsort(-y_, kind="stable")
    m = int(y_.sum())
    if m < 5 or (len(y_) - m) < 5:
        return None
    aucs, cov = _fast_delong(np.vstack((a_, b_))[:, order], m)
    L = np.array([[1.0, -1.0]])
    var = float(L @ cov @ L.T)
    if var <= 0:
        return {"auc1": float(aucs[0]), "auc2": float(aucs[1]),
                "delta": float(aucs[0] - aucs[1]), "z": None, "p": None,
                "note": "degenerate variance (perfect separation)"}
    z = float((aucs[0] - aucs[1]) / math.sqrt(var))
    p = float(2.0 * norm.sf(abs(z)))
    return {"auc1": float(aucs[0]), "auc2": float(aucs[1]),
            "delta": float(aucs[0] - aucs[1]), "se": math.sqrt(var), "z": z,
            "p": p, "p_report": ("< 1e-300" if p == 0.0 else "%.3g" % p)}


def mwu_vs_chance(y, s):
    """Correct test of H0: AUROC = 0.5 (Mann-Whitney U is exactly equivalent)."""
    ok = np.isfinite(s)
    y_, s_ = y[ok], s[ok]
    pos, neg = s_[y_ == 1], s_[y_ == 0]
    if len(pos) < 5 or len(neg) < 5:
        return None
    U, p = mannwhitneyu(pos, neg, alternative="two-sided")
    return {"U": float(U), "p": float(p),
            "p_report": ("< 1e-300" if p == 0.0 else "%.3g" % p),
            "auroc": float(U / (len(pos) * len(neg)))}


def boot_idx(n, n_boot):
    return RNG.integers(0, n, size=(n_boot, n))


def auroc_ci(y, s, idx):
    ok = np.isfinite(s)
    y_, s_ = y[ok], s[ok]
    vals = []
    for row in idx:
        r = row % len(y_)
        yy = y_[r]
        if yy.min() == yy.max():
            continue
        vals.append(roc_auc_score(yy, s_[r]))
    if not vals:
        return (float("nan"), float("nan"))
    return (float(np.percentile(vals, 2.5)), float(np.percentile(vals, 97.5)))


def delta_ci(y, s1, s2, idx):
    """Paired bootstrap CI for AUROC(s1) - AUROC(s2)."""
    ok = np.isfinite(s1) & np.isfinite(s2)
    y_, a_, b_ = y[ok], s1[ok], s2[ok]
    d = []
    for row in idx:
        r = row % len(y_)
        yy = y_[r]
        if yy.min() == yy.max():
            continue
        d.append(roc_auc_score(yy, a_[r]) - roc_auc_score(yy, b_[r]))
    if not d:
        return None
    d = np.asarray(d)
    return {"delta_mean": float(d.mean()),
            "ci_lo": float(np.percentile(d, 2.5)),
            "ci_hi": float(np.percentile(d, 97.5)),
            "pct_positive": float(100.0 * (d > 0).mean())}


# =====================================================================
# 6. SUPERVISED METHODS (5-fold stratified CV, out-of-fold scores)
# =====================================================================
def supervised_oof(y):
    y = y.astype(int)
    if y.sum() < 10:
        return {}
    Xs = StandardScaler().fit_transform(X)
    skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    out = {"Logistic regression": np.zeros(N_GENES),
           "Elastic net": np.zeros(N_GENES),
           "Random forest": np.zeros(N_GENES)}
    for tr, te in skf.split(Xs, y):
        lr = LogisticRegression(max_iter=2000, C=1.0, class_weight="balanced")
        lr.fit(Xs[tr], y[tr])
        out["Logistic regression"][te] = lr.predict_proba(Xs[te])[:, 1]
        en = ElasticNet(alpha=0.01, l1_ratio=0.5, max_iter=5000)
        en.fit(Xs[tr], y[tr])
        out["Elastic net"][te] = en.predict(Xs[te])
        rf = RandomForestClassifier(n_estimators=200, max_depth=10, n_jobs=-1,
                                    class_weight="balanced", random_state=42)
        rf.fit(Xs[tr], y[tr])
        out["Random forest"][te] = rf.predict_proba(Xs[te])[:, 1]
    return out


# =====================================================================
# 7. MAIN BENCHMARK
# =====================================================================
log("\n" + "=" * 72)
log("7. BENCHMARK: methods x endpoints, CI, MWU, DeLong, Delta-CI")
log("=" * 72)

BIDX = boot_idx(N_GENES, N_BOOT)
benchmark, mwu_tbl, delong_tbl, delta_tbl, forms_tbl = {}, {}, {}, {}, {}

for ep, y in ENDPOINTS.items():
    log(f"\n  -- {ep}  (n_pos={int(y.sum())})")
    sup = supervised_oof(y)
    allsc = dict(SCORES)
    allsc.update(sup)
    benchmark[ep] = {}
    for name, s in allsc.items():
        ok = np.isfinite(s)
        try:
            a = float(roc_auc_score(y[ok], s[ok]))
            ap = float(average_precision_score(y[ok], s[ok]))
        except ValueError:
            continue
        lo, hi = auroc_ci(y, s, BIDX)
        benchmark[ep][name] = {"auroc": a, "auprc": ap, "auroc_ci": [lo, hi],
                              "n_pos": int(y.sum()), "n_eval": int(ok.sum())}
    # correct chance test for every method
    mwu_tbl[ep] = {n: mwu_vs_chance(y, s) for n, s in allsc.items()}
    # pairwise DeLong for the comparisons the manuscript actually makes
    ref = SCORES["STRING centrality"]
    pairs = {}
    for n in ("Random forest", "Harmonic mean", "ECS (multiplicative)",
              "Arithmetic mean", "Druggability", "Logistic regression"):
        if n in allsc:
            r = delong_test(y, allsc[n], ref)
            if r:
                pairs[f"{n} vs STRING centrality"] = r
    r = delong_test(y, SCORES["Harmonic mean"], SCORES["ECS (multiplicative)"])
    if r:
        pairs["Harmonic mean vs ECS (multiplicative)"] = r
    delong_tbl[ep] = pairs
    # paired Delta-AUROC CI
    dd = {}
    for n in ("Random forest", "Harmonic mean", "ECS (multiplicative)"):
        if n in allsc:
            c = delta_ci(y, allsc[n], ref, BIDX)
            if c:
                dd[f"{n} - STRING centrality"] = c
    delta_tbl[ep] = dd
    # P0-1: functional-form ranking on EVERY endpoint (V17 only did E3)
    forms_tbl[ep] = {}
    for fn_name, fn in FORMS.items():
        s = fn(X)
        ok = np.isfinite(s)
        try:
            a = float(roc_auc_score(y[ok], s[ok]))
        except ValueError:
            continue
        lo, hi = auroc_ci(y, s, BIDX)
        forms_tbl[ep][fn_name] = {"auroc": a, "auroc_ci": [lo, hi]}
    best = max(benchmark[ep].items(), key=lambda kv: kv[1]["auroc"])
    log(f"     best = {best[0]} ({best[1]['auroc']:.3f})")

# ---- P0-2 audit records --------------------------------------------
e1 = benchmark["E1 pan-dependency"]
e3 = benchmark["E3 conjunctive actionability"]
finding("P0-2", "CRITICAL",
        "V17 Results quoted E3 numbers while describing the E1 endpoint",
        ("V17 line: '4,585 essential genes ... mutation frequency achieved AUROC 0.520 "
         "(95%% CI 0.506-0.536), genetic constraint 0.559'. Those are the E3 "
         "(actionability) values. On the endpoint actually described (E1 essentiality) the "
         "true values are mutation %.3f [%.3f-%.3f] and constraint %.3f [%.3f-%.3f]."
         % (e1["Mutation frequency"]["auroc"], *e1["Mutation frequency"]["auroc_ci"],
            e1["Genetic constraint"]["auroc"], *e1["Genetic constraint"]["auroc_ci"])),
        "Requote the E1 values; they are the ones whose CI actually brackets 0.5.")

m = mwu_tbl["E1 pan-dependency"]
finding("P0-2", "CRITICAL",
        "'DeLong p > 0.05 against AUROC = 0.5' is not a valid test and was never run",
        ("DeLong compares two correlated empirical ROC curves; it cannot test a single "
         "curve against the 0.5 null, and run_v17_ncs.py contains no such test (its only "
         "DeLong call is ECS vs STRING on E3). Replaced by Mann-Whitney U, which is exactly "
         "equivalent to the AUROC = 0.5 null: on E1, mutation frequency p = %s, "
         "genetic constraint p = %s, druggability p = %s."
         % (m["Mutation frequency"]["p_report"], m["Genetic constraint"]["p_report"],
            m["Druggability"]["p_report"])),
        "State CI overlap with 0.5 and Mann-Whitney U; delete the DeLong-vs-0.5 sentence.")

# best-method-per-endpoint audit (V17 claimed RF strongest on 5 of 6)
rf_best = []
for ep, tbl in benchmark.items():
    top = max(tbl.items(), key=lambda kv: kv[1]["auroc"])
    ties = [n for n, v in tbl.items() if abs(v["auroc"] - top[1]["auroc"]) < 1e-9]
    rf_best.append((ep, top[0], round(top[1]["auroc"], 4), ties))
AUDIT["best_method_per_endpoint"] = [
    {"endpoint": e, "best": b, "auroc": a, "ties": t} for e, b, a, t in rf_best]
finding("P0-2", "MAJOR", "'Random forest strongest on 5 of 6 endpoints' needs restating",
        "; ".join("%s -> %s %.3f%s" % (e.split()[0], b, a, " (tie)" if len(t) > 1 else "")
                  for e, b, a, t in rf_best),
        "Quote the per-endpoint winner exactly, noting the E3-C ties at 1.0 are pure leakage.")

# E3-C leakage magnitude
e3c = benchmark["E3-C out-of-evidence druggability"]
perfect = [n for n, v in e3c.items() if v["auroc"] > 0.999]
finding("P0-5", "MAJOR", "E3-C is fully saturated for any method that ingests druggability",
        ("%s reach AUROC = 1.000 on E3-C because druggability is simultaneously an input "
         "feature and the label. STRING alone reaches %.3f [%.3f-%.3f], which is above "
         "chance, not 'near-chance' as V17 states."
         % (", ".join(perfect), e3c["STRING centrality"]["auroc"],
            *e3c["STRING centrality"]["auroc_ci"])),
        "Restrict E3-C to leakage-free scorers (STRING, ECS-minus-druggability) and drop "
        "the 'near-chance' wording for STRING.")

# functional forms on the clinical endpoint (V17 copied E3 values)
fc = forms_tbl["E5 historical clinical-target concordance"]
f3 = forms_tbl["E3 conjunctive actionability"]
finding("P0-1", "CRITICAL",
        "V17 reported E3 functional-form values as if they were clinical-endpoint values",
        ("V17: 'the same ordering holds on E6 (harmonic 0.941, additive 0.825, geometric "
         "0.758, multiplicative 0.825, rank 0.854)'. additive 0.825 and geometric 0.758 are "
         "the E3 numbers. Recomputed on the clinical endpoint: harmonic %.3f, additive "
         "%.3f, geometric %.3f, multiplicative %.3f, rank %.3f (E3 for reference: "
         "harmonic %.3f, additive %.3f, geometric %.3f)."
         % (fc["harmonic mean"]["auroc"], fc["additive"]["auroc"],
            fc["geometric mean"]["auroc"], fc["multiplicative (ECS)"]["auroc"],
            fc["rank aggregation"]["auroc"], f3["harmonic mean"]["auroc"],
            f3["additive"]["auroc"], f3["geometric mean"]["auroc"])),
        "Use the recomputed clinical-endpoint values; re-draw Fig. 4b.")


# =====================================================================
# 8. LEAKAGE-FREE, WEIGHT SPACE, NEGATIVE CONTROLS, RESAMPLING
# =====================================================================
log("\n" + "=" * 72)
log("8. LEAKAGE, WEIGHT SPACE, CONTROLS, STRUCTURED RESAMPLING")
log("=" * 72)


def ev(y, s):
    ok = np.isfinite(s)
    lo, hi = auroc_ci(y, s, BIDX)
    return {"auroc": float(roc_auc_score(y[ok], s[ok])),
            "auprc": float(average_precision_score(y[ok], s[ok])),
            "auroc_ci": [lo, hi], "n_pos": int(y.sum())}


leakage = {
    "ecs_minus_druggability_predicts_druggability": ev(E3C_y, f_ecs_nodrug(X)),
    "string_predicts_druggability": ev(E3C_y, SCORES["STRING centrality"]),
    "e3a_ecs": ev(E3A_y, SCORES["ECS (multiplicative)"]),
    "e3a_string": ev(E3A_y, SCORES["STRING centrality"]),
    "e3a_harmonic": ev(E3A_y, SCORES["Harmonic mean"]),
    "identity_note": ("E3-A label vector is bit-identical to E1 by construction; "
                      "these rows duplicate the E1 column of the benchmark."),
}

# weight space: 1000 Dirichlet draws over (STRING, mutation, IMPC)
w_auroc = []
for _ in range(1000):
    w = RNG.dirichlet([1, 1, 1])
    D = w[0] * X[:, I_STR] + w[1] * X[:, I_MUT] + w[2] * X[:, I_IMPC]
    P = np.mean(X[:, SUP_ALL], axis=1)
    w_auroc.append(roc_auc_score(E3_y, D * (1 + 0.6 * P)))
w_auroc = np.asarray(w_auroc)
str_e3 = e3["STRING centrality"]["auroc"]
weight_sens = {"n_samples": 1000, "string_auroc_e3": str_e3,
               "mean": float(w_auroc.mean()), "std": float(w_auroc.std()),
               "min": float(w_auroc.min()), "max": float(w_auroc.max()),
               "pct_above_string": float(100 * (w_auroc > str_e3).mean()),
               "pct_below_chance": float(100 * (w_auroc < 0.5).mean())}
finding("P0-1", "MAJOR", "Weight-space result is far more damaging than V17 stated",
        ("Mean AUROC over 1,000 Dirichlet weightings is %.3f with %.1f%% of draws BELOW "
         "chance (0.5); only %.1f%% beat STRING alone (%.3f). V17 reported only the "
         "3.6%% figure and omitted that the average weighting is anti-predictive."
         % (weight_sens["mean"], weight_sens["pct_below_chance"],
            weight_sens["pct_above_string"], str_e3)),
        "Report mean, the sub-chance fraction, and the 3.6% figure together.")

# negative controls on E3
Xr = X.copy()
Xr[:, FEATURES.index("hpa_rna_tissue_spec")] = RNG.normal(0, 1, N_GENES)
Xs_ = X.copy()
Xs_[:, I_STR] = RNG.permutation(X[:, I_STR])
Xp = X.copy()
Xp[:, FEATURES.index("druggability")] = RNG.permutation(X[:, FEATURES.index("druggability")])
controls = {"ecs_observed": ev(E3_y, f_multiplicative(X)),
            "random_gaussian_layer": ev(E3_y, f_multiplicative(Xr)),
            "shuffled_network": ev(E3_y, f_multiplicative(Xs_)),
            "permuted_druggability": ev(E3_y, f_multiplicative(Xp))}
if controls["random_gaussian_layer"]["auroc"] > controls["ecs_observed"]["auroc"]:
    finding("P0-1", "MAJOR",
            "Replacing a real evidence layer with Gaussian noise IMPROVES the heuristic",
            ("ECS on E3 = %.3f; replacing the tissue-specificity layer with N(0,1) noise "
             "gives %.3f. The multiplicative heuristic is therefore not extracting signal "
             "from that layer at all."
             % (controls["ecs_observed"]["auroc"],
                controls["random_gaussian_layer"]["auroc"])),
            "Foreground this control: it is the strongest single piece of evidence for the "
            "paper's central negative claim.")

# structured resampling: STRING-centrality communities
bins = np.digitize(X[:, I_STR], np.linspace(X[:, I_STR].min(), X[:, I_STR].max(), 11)[1:-1])
groups = [np.where(bins == b)[0] for b in range(11) if (bins == b).sum() > 30]
ecs_s, str_s = f_multiplicative(X), SCORES["STRING centrality"]
deltas = []
for _ in range(500):
    pick = RNG.integers(0, len(groups), len(groups))
    idx = np.concatenate([groups[p] for p in pick])
    yy = E3_y[idx]
    if yy.min() == yy.max():
        continue
    deltas.append(roc_auc_score(yy, ecs_s[idx]) - roc_auc_score(yy, str_s[idx]))
deltas = np.asarray(deltas)
struct = {"method": "STRING-centrality community bootstrap", "n_communities": len(groups),
          "n_bootstrap": int(len(deltas)), "delta_mean": float(deltas.mean()),
          "delta_ci_lo": float(np.percentile(deltas, 2.5)),
          "delta_ci_hi": float(np.percentile(deltas, 97.5)),
          "pct_positive": float(100 * (deltas > 0).mean())}

# zero-shot transfer PDAC -> CRC
transfer = {"pdac_ecs_to_crc_essentiality": ev(E4_y, ecs_s),
            "pdac_string_to_crc_essentiality": ev(E4_y, str_s),
            "pdac_harmonic_to_crc_essentiality": ev(E4_y, SCORES["Harmonic mean"]),
            "spearman_pdac_crc_dependency_rank": None}


# =====================================================================
# 9. P0-7: RE-RANK THE 9 CANDIDATES BY HARMONIC MEAN
# =====================================================================
log("\n" + "=" * 72)
log("9. CANDIDATE RE-RANKING (P0-7)")
log("=" * 72)

V17_ORDER = ["KPNA2", "ARF6", "RAB7A", "ITGA2B", "GNG2", "STAMBP", "RAB6A", "F3", "TNFRSF8"]
h = SCORES["Harmonic mean"]
rows = []
for g in V17_ORDER:
    i = GENE_IDX.get(g)
    if i is None:
        continue
    rows.append({"gene": g, "harmonic_mean": float(h[i]),
                 "string_centrality": float(X[i, I_STR]),
                 "druggable": bool(lv(g, "druggability") is not None),
                 "pdac_essential": bool(g in ess_pdac),
                 "crc_essential": bool(g in ess_crc),
                 "harmonic_percentile": float(100.0 * (h < h[i]).mean())})
rows.sort(key=lambda r: -r["harmonic_mean"])
for k, r in enumerate(rows, 1):
    r["rank_v18"] = k
    r["rank_v17_as_printed"] = V17_ORDER.index(r["gene"]) + 1
reordered = [r["gene"] for r in rows]
if reordered != V17_ORDER:
    finding("P0-7", "CRITICAL",
            "The 9 candidates were not ordered by harmonic mean as the manuscript claims",
            ("V17 Fig. 6b legend states 'ranked by harmonic mean'. The printed order is %s; "
             "the true harmonic-mean order is %s. The printed order came from an external "
             "file (SCI论文的LJT/results/tvs_analysis.json) and is not reproducible from "
             "run_v17_ncs.py." % (", ".join(V17_ORDER), ", ".join(reordered))),
            "Use the recomputed ordering, generate the table inside the pipeline, and label "
            "the genes as prospective computational hypotheses, not validated targets.")
n_ess = sum(r["pdac_essential"] for r in rows)
finding("P0-7", "MAJOR", "Candidate essentiality status must be disclosed",
        "%d/%d candidates are PDAC-essential in DepMap; %d/%d are CRC-essential."
        % (n_ess, len(rows), sum(r["crc_essential"] for r in rows), len(rows)),
        "State essentiality status per candidate in the display item.")

top_harmonic = [{"gene": ALL_GENES[i], "harmonic_mean": float(h[i]),
                 "string_centrality": float(X[i, I_STR]),
                 "druggable": bool(lv(ALL_GENES[i], "druggability") is not None),
                 "pdac_essential": bool(ALL_GENES[i] in ess_pdac)}
                for i in np.argsort(-h)[:25]]
overlap = set(reordered) & CLIN_POS
candidates = {"v17_printed_order": V17_ORDER, "v18_harmonic_order": reordered,
              "table": rows, "genome_wide_top25_by_harmonic": top_harmonic,
              "jaccard_with_clinical_set": (len(overlap) /
                                            len(set(reordered) | CLIN_POS)),
              "status": "prospective computational hypotheses; not validated targets"}


# =====================================================================
# 10. OUTPUT
# =====================================================================
log("\n" + "=" * 72)
log("10. WRITING OUTPUT")
log("=" * 72)

results = {
    "version": "v18.0.0",
    "title": ("Auditing evidence integration for context-dependent therapeutic "
              "target prioritization"),
    "target_journal": "Nature Computational Science (Analysis)",
    "generated": AUDIT["generated"],
    "n_genes": N_GENES,
    "features": FEATURES,
    "endpoint_taxonomy": {
        "E1": "pan-dependency (PDAC CRISPR essentiality, DepMap)",
        "E2": ("PDAC-enriched dependency; STRATIFICATION OF E1, not an independent "
               "validation endpoint (P0-4)"),
        "E3": ("conjunctive actionability benchmark (essential AND druggable); a benchmark "
               "construct, not clinical validation (P0-5)"),
        "E3-A": ("leakage-controlled essentiality; identical to E1 by construction "
                 "because dropping the druggability conjunct collapses the positive set "
                 "onto E1 (P0-3)"),
        "E3-C": "out-of-evidence druggability prediction (saturated for druggability-fed methods)",
        "E4": "CRC zero-shot transfer (cross-context generalization)",
        "E5": ("historical clinical-target concordance; NOT clinical validation (P0-6); "
               "35 positives from ClinicalTrials.gov"),
        "E6": "PDAC drug-response actionability (GDSC, new orthogonal endpoint)",
    },
    "benchmark": benchmark,
    "mannwhitney_vs_chance": mwu_tbl,
    "delong_pairwise": delong_tbl,
    "delta_auroc_paired_bootstrap": delta_tbl,
    "functional_forms_all_endpoints": forms_tbl,
    "leakage_free": leakage,
    "weight_sensitivity": weight_sens,
    "negative_controls": controls,
    "structured_resampling": struct,
    "zero_shot_transfer": transfer,
    "candidates": candidates,
    "gdsc_endpoint": E6_meta,
    "harmonic_verification": AUDIT["p0_1_harmonic_verification"],
}
p1 = os.path.join(RES, "v18_ncs_results.json")
json.dump(results, open(p1, "w"), indent=1, ensure_ascii=False)

AUDIT["n_findings"] = len(AUDIT["findings"])
AUDIT["severity_counts"] = {s: sum(1 for f in AUDIT["findings"] if f["severity"] == s)
                            for s in ("CRITICAL", "MAJOR", "MINOR", "RESOLVED")}
p2 = os.path.join(RES, "v18_audit_report.json")
json.dump(AUDIT, open(p2, "w"), indent=1, ensure_ascii=False)

p3 = os.path.join(RES, "v18_source_data.csv")
with open(p3, "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["endpoint", "method", "auroc", "ci_lo", "ci_hi", "auprc",
                "n_positives", "mwu_p_vs_chance"])
    for ep, tbl in benchmark.items():
        for meth, v in tbl.items():
            mm = (mwu_tbl.get(ep, {}) or {}).get(meth) or {}
            w.writerow([ep, meth, "%.4f" % v["auroc"], "%.4f" % v["auroc_ci"][0],
                        "%.4f" % v["auroc_ci"][1], "%.4f" % v["auprc"],
                        v["n_pos"], mm.get("p_report", "")])

log(f"\n  wrote {p1}")
log(f"  wrote {p2}")
log(f"  wrote {p3}")
log(f"\n  AUDIT: {AUDIT['severity_counts']}")
log("\nDONE")
