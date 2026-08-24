#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
aido_integrate_v20.py - 基于多模型序列探针实际结果，把 V19 升为 V20

核心调整（依据真实计算结果）：
  1. Results 的 AIDO 小节 → 重写为「多模型序列证据轴」小节（DNA + 蛋白 + 集成）
  2. 结论：DNA(0.584)/蛋白(0.531)/集成(0.554) 一致性地弱于 curated 整合(0.750)
     -- 多模型交叉验证核心负结果
  3. Methods 增补 ESM2 方法
  4. 版本 v19 → v20

数值从 esm2_150M_endpoint.json / ensemble_endpoint.json / aido300m_1024 实时读取。
"""
import json
import os

OUT = "/Users/zuoxianbo/Desktop/SCI论文/胰腺癌"
SRC = os.path.join(OUT, "PDAC_evidence_integration_audit_V19.md")
DST = os.path.join(OUT, "PDAC_evidence_integration_audit_V20.md")
DATA = "/Users/zuoxianbo/Desktop/zuoxb-虚拟科研系统-MAC/outputs/pdac-convergent-evidence-v14/data"

esm2 = json.load(open(os.path.join(DATA, "esm2_150M_endpoint.json")))
ens = json.load(open(os.path.join(DATA, "ensemble_endpoint.json")))
dna = json.load(open(os.path.join(DATA, "aido300m_1024_endpoint.json")))

a_dna, ci_dna = dna["auroc_cv5"], dna["auroc_ci"]
a_esm2, ci_esm2 = esm2["auroc_cv5"], esm2["auroc_ci"]
a_ens, ci_ens = ens["auroc_cv5"], ens["auroc_ci"]

# 候选打分（DNA 1024bp 高分基因 + ESM2 高分基因）
dna_hi = [g for g, s in dna["candidate_scores"].items() if s > 0.5]
esm2_hi = [g for g, s in esm2["candidate_scores"].items() if s > 0.5]

txt = open(SRC, encoding="utf-8").read()

# ---------- 1. 版本 ----------
txt = txt.replace("**Version** v19.0.0", "**Version** v20.0.0")
txt = txt.replace("rendered by aido_integrate.py (V18 + AIDO E7)",
                  "rendered by aido_integrate_v20.py (multi-model sequence axis)")
txt = txt.replace("rendered 2026-08-21 (V19)", "rendered 2026-08-21 (V20)")

# ---------- 2. 替换 AIDO 小节为多模型小节 ----------
# 定位 AIDO 小节标题到下一小节标题
start = txt.index("### A sequence-native foundation model adds an axis "
                  "orthogonal to curated evidence")
end = txt.index("### The candidate genes are prospective hypotheses")
new_section = f"""### Sequence-native foundation models add an axis orthogonal to curated evidence

To test whether modern sequence foundation models, trained without any of the nine curated layers, recover dependency signal from raw sequence, we embedded the canonical coding sequence and the encoded protein of 503 genes - {dna['n_pos']} DepMap-essential and {dna['n_neg']} non-essential pancreatic dependencies plus the nine candidates - with two complementary foundation models, AIDO.DNA-300M (DNA; GenBio AI, arXiv:2412.06993) and ESM2-150M (protein; Meta AI), and trained linear probes to predict DepMap essentiality under five-fold stratified cross-validation. The DNA probe reaches AUROC {a_dna:.3f} (95% CI {ci_dna[0]:.3f}-{ci_dna[1]:.3f}), above chance and above the best single-layer genotype feature (mutation frequency 0.520; genetic constraint 0.559). The protein probe reaches only {a_esm2:.3f} (95% CI {ci_esm2[0]:.3f}-{ci_esm2[1]:.3f}), indistinguishable from chance, and concatenating both embeddings before probing yields {a_ens:.3f} (95% CI {ci_ens[0]:.3f}-{ci_ens[1]:.3f}), no better than DNA alone (Fig. 7a). Coding sequence therefore carries a weak but real dependency signal, whereas protein sequence does not, and neither approaches the curated-integration benchmark (random forest 0.750). This is consistent with essentiality being context-dependent: a gene's function, whether read from its DNA or its protein, does not by itself determine its dependency.

The probes' behaviour on the nine candidates exposes the same limit, and adds a cross-model inconsistency. All nine are DepMap-essential, yet the DNA probe assigns a high score to only {', '.join(sorted(dna_hi))} and the protein probe to a different subset {', '.join(sorted(esm2_hi))} (Fig. 7b). The disagreement among sequence models, and between them and the curated composite, is informative: sequence alone does not recapitulate the network/druggability essentiality that the curated composite rewards. We therefore treat these foundation models as a tenth, sequence-native evidence axis, and report their endpoint (E7) not as an additional validation of the composite but as a cross-model demonstration that different evidence axes give conditionally different answers.

"""
txt = txt[:start] + new_section + txt[end:]

# ---------- 3. Methods 增补 ESM2 ----------
anchor = "A tenth, sequence-native axis was derived with AIDO.DNA-300M"
esm2_methods = ("A tenth, sequence-native axis was derived with two complementary "
                "foundation models. AIDO.DNA-300M (GenBio AI) is a "
                "300-million-parameter DNA foundation model pretrained on 10.6 "
                "billion nucleotides from 796 species; ESM2-150M (Meta AI) is a "
                "150-million-parameter protein language model pretrained on "
                "UniRef50. For 503 genes (the nine candidates plus a seeded "
                "sample of 248 DepMap-essential and 246 non-essential pancreatic "
                "dependencies), the canonical coding sequence (truncated to 512 "
                "bp) and the encoded protein (truncated to 1,024 residues) were "
                "fetched from Ensembl. Sequences were embedded with their "
                "respective model (mean pooling over the attention-masked "
                "length) to 1,024- and 640-dimensional vectors, and "
                "logistic-regression linear probes (L2-regularized, "
                "class-balanced) were trained to predict DepMap essentiality "
                "under five-fold stratified cross-validation, individually and "
                "on the concatenated embeddings. Out-of-fold AUROC is reported "
                "with a 95% percentile interval from 2,000 stratified bootstrap "
                "resamples. The nine candidate genes, held out of training, "
                "receive predicted essentiality scores from probes refitted on "
                "all training genes.")
if anchor in txt:
    # 替换旧 AIDO 方法段（从 anchor 到 "### Scoring strategies"）
    s2 = txt.index(anchor)
    e2 = txt.index("### Scoring strategies")
    txt = txt[:s2] + esm2_methods + "\n\n" + txt[e2:]
else:
    # 兜底：直接在 Scoring strategies 前插入
    txt = txt.replace("### Scoring strategies",
                      esm2_methods + "\n\n### Scoring strategies")

# ---------- 4. Abstract 微调（AIDO → 多模型）----------
txt = txt.replace(
    "A sequence-native DNA foundation model (AIDO.DNA-300M) predicts dependency "
    f"from coding sequence at AUROC {a_dna:.3f}, above genotype features but "
    "below supervised integration.",
    "Sequence-native foundation models predict dependency weakly from coding "
    f"sequence (AIDO.DNA-300M AUROC {a_dna:.3f}) but not from protein sequence "
    f"(ESM2 {a_esm2:.3f}), both below supervised integration.")

# ---------- 5. Fig7 图注更新 ----------
old_fig7 = txt[txt.index("**Fig. 7 |**"):txt.index("**Supplementary Table 1 | Audit ledger.**")]
new_fig7 = f"""**Fig. 7 |** A sequence-native foundation-model endpoint. **a**, Receiver operating characteristic for linear probes trained on AIDO.DNA-300M coding-sequence embeddings (DNA, AUROC {a_dna:.3f}), ESM2-150M protein embeddings (protein, AUROC {a_esm2:.3f}) and their concatenation (AUROC {a_ens:.3f}) to predict DepMap essentiality under five-fold cross-validation. Dashed line, chance. **b**, Essentiality score for the nine candidate genes assigned by the DNA probe (violet) and the protein probe (orange); all nine candidates are DepMap-essential, so the disagreement among sequence models and the curated composite identifies essentiality that sequence alone cannot recover.

"""
txt = txt.replace(old_fig7, new_fig7)

open(DST, "w", encoding="utf-8").write(txt)
print(f"[v20] wrote {DST} ({len(txt)} chars)", flush=True)

import re as _re
def wc(s):
    return len(_re.findall(r"[A-Za-z0-9]+", s))
abstract = txt.split("## Abstract")[1].split("Selecting which genes")[0]
print(f"abstract ~{wc(abstract)} words", flush=True)
