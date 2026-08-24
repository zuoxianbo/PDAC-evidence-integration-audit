#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
aido_fig7.py - 生成 Fig7：AIDO 序列基础模型证据（新端点 E7）

左：AIDO.DNA-300M 线性探针 5-fold CV 的 ROC 曲线（预测 PDAC CRISPR 依赖）
右：9 个候选基因的 AIDO 序列必需性打分（0-1），标注 DepMap 必需性

输出 figures/Fig7.png + Fig7.pdf（300dpi，NCS 4 色方案）
"""
import json
import os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager

ROOT = "/Users/zuoxianbo/Desktop/zuoxb-虚拟科研系统-MAC/outputs/pdac-convergent-evidence-v14"
DATA = os.path.join(ROOT, "data")
FIGD = "/Users/zuoxianbo/Desktop/SCI论文/胰腺癌/figures"

# NCS 4 色方案
C_BASE = "#1F4E79"    # baseline
C_INT = "#2A9D8F"     # integration
C_RF = "#E76F51"      # RF
C_NULL = "#A6A6A6"    # null
C_TR = "#6C63A8"      # transfer / AIDO

plt.rcParams.update({
    "font.family": "Arial",
    "font.size": 6.5,
    "axes.linewidth": 0.6,
    "axes.edgecolor": "#444444",
})


def roc_curve(y_true, y_score):
    from sklearn.metrics import roc_curve, roc_auc_score
    fpr, tpr, _ = roc_curve(y_true, y_score)
    auc = roc_auc_score(y_true, y_score)
    return fpr, tpr, auc


def main():
    ep = json.load(open(os.path.join(DATA, "aido_endpoint.json")))
    pred = json.load(open(os.path.join(DATA, "aido_probe_predictions.json")))

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(7.2, 3.2),
                                   gridspec_kw={"width_ratios": [1.15, 1]})

    # ---- 左：ROC 曲线 ----
    y_true = np.array(pred["y_true"])
    y_score = np.array(pred["y_score"])
    fpr, tpr, auc = roc_curve(y_true, y_score)
    ax1.plot(fpr, tpr, color=C_TR, lw=1.6,
             label=f"AIDO.DNA-300M linear probe (AUROC = {auc:.3f})")
    ax1.plot([0, 1], [0, 1], color=C_NULL, lw=0.8, ls="--", label="chance")
    # 对照：论文单层方法在 E1 上的点（AUROC 值）
    ax1.scatter([0.0], [0.0], s=0)  # placeholder 保持图例
    ax1.set_xlabel("False positive rate")
    ax1.set_ylabel("True positive rate")
    ax1.set_xlim(0, 1); ax1.set_ylim(0, 1)
    ax1.set_aspect("equal")
    ax1.legend(loc="lower right", frameon=False, fontsize=5.8)
    ax1.set_title("a  AIDO sequence probe for PDAC dependency",
                  loc="left", fontsize=6.5, pad=4)

    # ---- 右：候选基因打分 ----
    cand = ep["candidate_comparison"]
    genes = [c["gene"] for c in cand]
    scores = [c["aido_essentiality_score"] for c in cand]
    # 按 AIDO score 上色：>0.5 紫(C_TR) / <=0.5 灰(C_NULL)
    colors = [C_TR if s > 0.5 else C_NULL for s in scores]
    order = np.argsort(scores)[::-1]
    genes = [genes[i] for i in order]
    scores = [scores[i] for i in order]
    colors = [colors[i] for i in order]
    y = np.arange(len(genes))
    ax2.barh(y, scores, color=colors, height=0.62)
    ax2.set_yticks(y)
    ax2.set_yticklabels(genes, fontsize=6)
    ax2.set_xlabel("AIDO essentiality score")
    ax2.set_xlim(0, 1)
    ax2.invert_yaxis()
    ax2.axvline(0.5, color=C_NULL, lw=0.7, ls=":")
    ax2.set_title("b  AIDO scores for the nine candidate genes",
                  loc="left", fontsize=6.5, pad=4)

    fig.subplots_adjust(left=0.09, right=0.98, top=0.9, bottom=0.14,
                        wspace=0.42)
    for ext in ("png", "pdf"):
        out = os.path.join(FIGD, f"Fig7.{ext}")
        fig.savefig(out, dpi=300, bbox_inches="tight", pad_inches=0.06)
        print("saved", out, flush=True)
    print(f"AUROC={auc:.4f}", flush=True)


if __name__ == "__main__":
    main()
