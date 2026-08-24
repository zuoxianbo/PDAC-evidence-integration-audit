#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
aido_fetch_sequences.py - 管道1：获取基因 CDS 序列（Ensembl REST，多线程并行）

从 depmap_pdac_dependency.json 采样 N 必需 + N 非必需基因，加上 9 个候选基因，
经 Ensembl REST API 获取每个基因 canonical transcript 的 CDS 序列。

用法:
    python aido_fetch_sequences.py [--n-pos 250] [--n-neg 250] [--seed 42] [--out <json>]
"""
import argparse
import json
import os
import re
import sys
import time
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed

ROOT = "/Users/zuoxianbo/Desktop/zuoxb-虚拟科研系统-MAC/outputs/pdac-convergent-evidence-v14"
DATA = os.path.join(ROOT, "data")
DEPMAP = os.path.join(DATA, "depmap_pdac_dependency.json")

CANDIDATES = ["KPNA2", "STAMBP", "ARF6", "RAB7A", "GNG2", "RAB6A", "F3",
              "ITGA2B", "TNFRSF8"]  # V18 harmonic 顺序

ENSEMBL = "https://rest.ensembl.org"
MAX_CDS_LEN = 1024  # 截断到 1024 bp（AIDO.DNA-300M 安全输入长度）


def http_get(url, timeout=25):
    req = urllib.request.Request(url, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read().decode("utf-8")


def fetch_one(gene):
    """返回 (gene, cds_seq or None, transcript or None, error or None)。"""
    try:
        # 1) lookup canonical transcript
        raw = http_get(f"{ENSEMBL}/lookup/symbol/homo_sapiens/{gene}?"
                       "content-type=application/json")
        info = json.loads(raw)
        ct = info.get("canonical_transcript")
        if not ct:
            return gene, None, None, "no canonical_transcript"
        # 2) 去版本号拿 CDS 序列
        ct_no_ver = ct.split(".")[0]
        fa = http_get(f"{ENSEMBL}/sequence/id/{ct_no_ver}?type=cds&"
                      "content-type=text/x-fasta")
        if fa.startswith(">"):
            seq = "".join(fa.split("\n")[1:]).strip().upper()
        else:
            seq = fa.strip().upper()
        seq = re.sub(r"[^ACGT]", "", seq)  # 只保留 ACGT
        if len(seq) < 30:
            return gene, None, ct, f"cds too short ({len(seq)}bp)"
        seq = seq[:MAX_CDS_LEN]  # 截断
        return gene, seq, ct, None
    except Exception as e:
        return gene, None, None, f"{type(e).__name__}: {e}"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n-pos", type=int, default=250)
    ap.add_argument("--n-neg", type=int, default=250)
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--out", default=os.path.join(ROOT, "data",
                                                  "aido_gene_sequences.json"))
    ap.add_argument("--workers", type=int, default=12)
    args = ap.parse_args()

    dep = json.load(open(DEPMAP))
    ess = [g for g, v in dep.items() if (v.get("essential") if isinstance(v, dict) else v)]
    non = [g for g, v in dep.items() if not (v.get("essential") if isinstance(v, dict) else v)]

    rng = __import__("random").Random(args.seed)
    pos = rng.sample(ess, args.n_pos)
    neg = rng.sample(non, args.n_neg)

    targets = {}
    for g in pos:
        targets[g] = {"label": 1}
    for g in neg:
        targets[g] = {"label": 0}
    for g in CANDIDATES:
        if g in dep:
            targets[g] = {"label": 1 if dep[g].get("essential") else 0,
                          "candidate": True}

    print(f"[fetch] 必需={len(pos)} 非必需={len(neg)} 候选={len(CANDIDATES)} "
          f"总={len(targets)} 基因", flush=True)

    out = {}
    n_ok = n_fail = 0
    t0 = time.time()
    with ThreadPoolExecutor(max_workers=args.workers) as ex:
        futs = {ex.submit(fetch_one, g): g for g in targets}
        for i, fut in enumerate(as_completed(futs), 1):
            gene, seq, ct, err = fut.result()
            if seq:
                out[gene] = {"cds": seq, "transcript": ct,
                             "label": targets[gene]["label"],
                             "candidate": targets[gene].get("candidate", False)}
                n_ok += 1
            else:
                n_fail += 1
            if i % 50 == 0:
                print(f"  {i}/{len(targets)} ok={n_ok} fail={n_fail} "
                      f"elapsed={time.time()-t0:.0f}s", flush=True)

    json.dump({"meta": {"n_pos": args.n_pos, "n_neg": args.n_neg,
                        "seed": args.seed, "max_cds_len": MAX_CDS_LEN,
                        "candidates": CANDIDATES},
               "genes": out},
              open(args.out, "w"), ensure_ascii=False, indent=1)
    print(f"[done] ok={n_ok} fail={n_fail} -> {args.out} "
          f"({time.time()-t0:.0f}s)", flush=True)


if __name__ == "__main__":
    main()
