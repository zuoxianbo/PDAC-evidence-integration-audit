#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
aido_probe_ensemble.py - 多模型集成探针（DNA + 蛋白 embedding 拼接 → 线性/GBM 探针）

读多个 embedding（按基因名对齐），拼接后做 5-fold CV 探针，评估 AUROC，
并对 9 候选基因打分。输出 ensemble_endpoint.json。

用法: python aido_probe_ensemble.py --prefixes aido300m_1024,esm2_150M [--out ensemble_endpoint.json]
"""
import argparse
import json
import os
import numpy as np

ROOT = "/Users/zuoxianbo/Desktop/zuoxb-虚拟科研系统-MAC/outputs/pdac-convergent-evidence-v14"
DATA = os.path.join(ROOT, "data")
CANDIDATES = ["KPNA2", "STAMBP", "ARF6", "RAB7A", "GNG2", "RAB6A", "F3",
              "ITGA2B", "TNFRSF8"]


def bootstrap_ci(y_true, y_score, n_boot=2000, seed=0):
    from sklearn.metrics import roc_auc_score
    rng = np.random.RandomState(seed)
    auroc = roc_auc_score(y_true, y_score)
    idx = np.arange(len(y_true))
    pos_idx = idx[y_true == 1]; neg_idx = idx[y_true == 0]
    vals = []
    for _ in range(n_boot):
        pi = rng.choice(pos_idx, len(pos_idx), replace=True)
        ni = rng.choice(neg_idx, len(neg_idx), replace=True)
        s = np.concatenate([pi, ni])
        vals.append(roc_auc_score(y_true[s], y_score[s]))
    lo, hi = np.percentile(vals, [2.5, 97.5])
    return auroc, lo, hi


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--prefixes", default="aido300m_1024,esm2_150M")
    ap.add_argument("--out", default="ensemble_endpoint.json")
    args = ap.parse_args()
    prefixes = args.prefixes.split(",")

    # 对齐基因名
    blocks = []
    common = None
    for p in prefixes:
        X = np.load(os.path.join(DATA, f"{p}_embeddings.npy"))
        meta = json.load(open(os.path.join(DATA, f"{p}_embeddings_meta.json")))
        d = {g: X[i] for i, g in enumerate(meta["names"])}
        blocks.append((p, d))
        if common is None:
            common = set(meta["names"])
        else:
            common &= set(meta["names"])
    common = sorted(common)
    print(f"[ensemble] {len(common)} 基因对齐 across {prefixes}", flush=True)

    # 标签从第一个 block 的 meta 取
    meta0 = json.load(open(os.path.join(DATA, f"{prefixes[0]}_embeddings_meta.json")))
    name2meta = {g: (meta0["labels"][i], meta0["candidate"][i])
                 for i, g in enumerate(meta0["names"])}

    Xcat = np.hstack([np.stack([blocks[j][1][g] for g in common])
                      for j in range(len(prefixes))]).astype("float32")
    labels = np.array([name2meta[g][0] for g in common])
    cand = np.array([name2meta[g][1] for g in common])
    print(f"[ensemble] X={Xcat.shape}", flush=True)

    from sklearn.linear_model import LogisticRegression
    from sklearn.model_selection import StratifiedKFold, cross_val_predict
    from sklearn.metrics import roc_auc_score, average_precision_score
    from sklearn.preprocessing import StandardScaler

    tm = cand == 0
    X_tr, y_tr = Xcat[tm], labels[tm]
    scaler = StandardScaler(); Xs = scaler.fit_transform(X_tr)
    clf = LogisticRegression(C=1.0, max_iter=3000, class_weight="balanced")
    skf = StratifiedKFold(5, shuffle=True, random_state=42)
    y_pred = cross_val_predict(clf, Xs, y_tr, cv=skf, method="predict_proba")[:, 1]
    auroc, ci_lo, ci_hi = bootstrap_ci(y_tr, y_pred)
    auprc = average_precision_score(y_tr, y_pred)

    clf_full = LogisticRegression(C=1.0, max_iter=3000, class_weight="balanced")
    clf_full.fit(Xs, y_tr)
    cand_scores = {}
    for i, g in enumerate(common):
        if cand[i]:
            x = scaler.transform(Xcat[i:i + 1])
            cand_scores[g] = round(float(clf_full.predict_proba(x)[0, 1]), 4)

    res = {
        "ensemble": prefixes,
        "n_train": int(X_tr.shape[0]),
        "n_pos": int(y_tr.sum()), "n_neg": int((1 - y_tr).sum()),
        "concat_dim": int(Xcat.shape[1]),
        "auroc_cv5": round(auroc, 4),
        "auroc_ci": [round(ci_lo, 4), round(ci_hi, 4)],
        "auprc": round(auprc, 4),
        "candidate_scores": cand_scores,
    }
    json.dump(res, open(os.path.join(DATA, args.out), "w"),
              ensure_ascii=False, indent=2)
    print(f"[ensemble] AUROC={auroc:.4f} CI=[{ci_lo:.4f},{ci_hi:.4f}] "
          f"AUPRC={auprc:.4f}", flush=True)
    print("  candidates:", json.dumps(cand_scores, ensure_ascii=False))


if __name__ == "__main__":
    main()
