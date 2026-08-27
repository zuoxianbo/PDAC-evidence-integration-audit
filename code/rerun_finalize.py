#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""收尾脚本：合并 8 个断点，完成 section 7 finding + section 8/9/10（负对照/重采样/候选/输出）。

RNG 消耗顺序与原始 recompute.py 严格一致（BIDX int32 已验证与 int64 相同），
保证负对照、社区重采样、候选基因的数字精确复现。
"""
import json, os, sys
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = open(os.path.join(HERE, "recompute.py")).read()

# ---- exec sections 1-6 ----
MARK7 = "# 7. MAIN BENCHMARK"
PREFIX = SRC.split(MARK7)[0]
ns = {"__name__": "v18_prefix", "__file__": os.path.join(HERE, "recompute.py")}
exec(compile(PREFIX, "recompute.py[sections 1-6]", "exec"), ns)

# ---- 生成 BIDX（int32，与原始 boot_idx 相同随机数）----
N_GENES = ns["N_GENES"]; N_BOOT = ns["N_BOOT"]
BIDX = ns["RNG"].integers(0, N_GENES, size=(N_BOOT, N_GENES), dtype=np.int32)
ns["BIDX"] = BIDX
print(f"BIDX int32 生成完成 {BIDX.nbytes/1e6:.0f}MB", flush=True)

# ---- 加载断点，重建 benchmark/mwu_tbl/delong_tbl/delta_tbl/forms_tbl ----
CHK = os.path.join(ns["RES"], "_rerun_checkpoint")
benchmark, mwu_tbl, delong_tbl, delta_tbl, forms_tbl = {}, {}, {}, {}, {}
# 用 ENDPOINTS 的原始顺序
for ep in ns["ENDPOINTS"].keys():
    fname = "benchmark_" + ep.split()[0].replace("-", "_") + ".json"
    p = os.path.join(CHK, fname)
    assert os.path.exists(p), f"断点缺失: {p}"
    d = json.load(open(p))
    benchmark[d["endpoint"]] = d["benchmark"]
    mwu_tbl[d["endpoint"]] = d["mwu"]
    delong_tbl[d["endpoint"]] = d["delong"]
    delta_tbl[d["endpoint"]] = d["delta"]
    forms_tbl[d["endpoint"]] = d["forms"]
    print(f"  加载断点 {d['endpoint']}", flush=True)

ns.update({"benchmark": benchmark, "mwu_tbl": mwu_tbl, "delong_tbl": delong_tbl,
           "delta_tbl": delta_tbl, "forms_tbl": forms_tbl})

# ---- exec section 7 finding + section 8/9/10 ----
REST_MARK = "# ---- P0-2 audit records"
assert REST_MARK in SRC, "rest marker not found"
idx = SRC.index(REST_MARK)
line_end = SRC.index("\n", idx)
REST = SRC[line_end + 1:]  # 从 marker 行的下一行开始
exec(compile(REST, "recompute.py[section7-finding + 8/9/10]", "exec"), ns)

print("\n收尾完成", flush=True)
