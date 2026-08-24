#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""分段重算 wrapper：逐个 endpoint 跑 benchmark，即时保存，支持断点续传。

复用 v18_recompute.py 的 sections 1-6（数据加载、端点构建、scorer、统计函数），
然后自己写 benchmark 循环，每跑完一个 endpoint 立即写盘，避免长任务被回收。
"""
import json, os, time, sys
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = open(os.path.join(HERE, "v18_recompute.py")).read()
MARK = "# 7. MAIN BENCHMARK"
assert MARK in SRC, "marker not found"
PREFIX = SRC.split(MARK)[0]

ns = {"__name__": "v18_prefix", "__file__": os.path.join(HERE, "v18_recompute.py")}
exec(compile(PREFIX, "v18_recompute.py[sections 1-6]", "exec"), ns)

X = ns["X"]; ENDPOINTS = ns["ENDPOINTS"]; SCORES = ns["SCORES"]
FORMS = ns["FORMS"]; RES = ns["RES"]; N_GENES = ns["N_GENES"]; N_BOOT = ns["N_BOOT"]
supervised_oof = ns["supervised_oof"]; auroc_ci = ns["auroc_ci"]
delta_ci = ns["delta_ci"]; delong_test = ns["delong_test"]
mwu_vs_chance = ns["mwu_vs_chance"]; boot_idx = ns["boot_idx"]
from sklearn.metrics import roc_auc_score, average_precision_score

# 中间结果目录
CHK = os.path.join(RES, "_rerun_checkpoint")
os.makedirs(CHK, exist_ok=True)

# 用 int32 生成 bootstrap 索引（已验证与 int64 产生相同随机数，内存减半 332MB->166MB）
BIDX = ns["RNG"].integers(0, N_GENES, size=(N_BOOT, N_GENES), dtype=np.int32)
print(f"BIDX int32 生成完成，内存 {BIDX.nbytes/1e6:.0f}MB", flush=True)

eps = list(ENDPOINTS.keys())
print(f"共 {len(eps)} 个 endpoint，逐个跑并保存断点", flush=True)

for ep in eps:
    out_path = os.path.join(CHK, f"benchmark_{ep.split()[0].replace('-','_')}.json")
    if os.path.exists(out_path):
        print(f"[跳过] {ep}（已有断点）", flush=True)
        continue
    t0 = time.time()
    y = ENDPOINTS[ep]
    print(f"\n[RUN] {ep} (n_pos={int(y.sum())})", flush=True)

    t_sup = time.time()
    sup = supervised_oof(y)
    print(f"    supervised_oof 完成 {time.time()-t_sup:.1f}s", flush=True)

    allsc = dict(SCORES); allsc.update(sup)
    bench = {}
    for name, s in allsc.items():
        ok = np.isfinite(s)
        try:
            a = float(roc_auc_score(y[ok], s[ok]))
            ap = float(average_precision_score(y[ok], s[ok]))
        except ValueError:
            continue
        lo, hi = auroc_ci(y, s, BIDX)
        bench[name] = {"auroc": a, "auprc": ap, "auroc_ci": [lo, hi],
                       "n_pos": int(y.sum()), "n_eval": int(ok.sum())}

    mwu = {n: mwu_vs_chance(y, s) for n, s in allsc.items()}
    ref = SCORES["STRING centrality"]
    pairs = {}
    for n in ("Random forest", "Harmonic mean", "ECS (multiplicative)",
              "Arithmetic mean", "Druggability", "Logistic regression"):
        if n in allsc:
            r = delong_test(y, allsc[n], ref)
            if r: pairs[f"{n} vs STRING centrality"] = r
    r = delong_test(y, SCORES["Harmonic mean"], SCORES["ECS (multiplicative)"])
    if r: pairs["Harmonic mean vs ECS (multiplicative)"] = r

    dd = {}
    for n in ("Random forest", "Harmonic mean", "ECS (multiplicative)"):
        if n in allsc:
            c = delta_ci(y, allsc[n], ref, BIDX)
            if c: dd[f"{n} - STRING centrality"] = c

    forms = {}
    for fn_name, fn in FORMS.items():
        s = fn(X); ok = np.isfinite(s)
        try:
            a = float(roc_auc_score(y[ok], s[ok]))
        except ValueError:
            continue
        lo, hi = auroc_ci(y, s, BIDX)
        forms[fn_name] = {"auroc": a, "auroc_ci": [lo, hi]}

    best = max(bench.items(), key=lambda kv: kv[1]["auroc"])
    json.dump({"endpoint": ep, "benchmark": bench, "mwu": mwu,
               "delong": pairs, "delta": dd, "forms": forms},
              open(out_path, "w"), indent=1)
    print(f"    [DONE] {ep}  best={best[0]} ({best[1]['auroc']:.3f})  "
          f"总耗时 {time.time()-t0:.1f}s", flush=True)
    import gc
    gc.collect()

print("\n全部 endpoint 完成", flush=True)
