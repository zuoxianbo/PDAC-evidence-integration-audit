#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
fetch_proteins.py - 获取基因完整蛋白序列（Ensembl REST，多线程）

复用 aido_gene_sequences.json 里的 transcript 信息，经 /sequence/id/{tid}?type=protein
获取完整蛋白序列（不截断）。输出 protein_sequences.json。

用法: python fetch_proteins.py [--seq aido_gene_sequences.json] [--workers 12]
"""
import argparse
import json
import os
import re
import time
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed

ROOT = "/Users/zuoxianbo/Desktop/zuoxb-虚拟科研系统-MAC/outputs/pdac-convergent-evidence-v14"
DATA = os.path.join(ROOT, "data")
ENSEMBL = "https://rest.ensembl.org"
MAX_LEN = 1024  # 蛋白序列截断到 1024 aa（ESM2 可处理更长，但截断控制成本）


def http_get(url, timeout=25):
    req = urllib.request.Request(url, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read().decode("utf-8")


def fetch_one(gene, tid):
    try:
        tid_no_ver = tid.split(".")[0]
        fa = http_get(f"{ENSEMBL}/sequence/id/{tid_no_ver}?type=protein&"
                      "content-type=text/x-fasta")
        seq = "".join(fa.split("\n")[1:]).strip().upper() if fa.startswith(">") \
            else fa.strip().upper()
        seq = re.sub(r"[^ACDEFGHIKLMNPQRSTVWY]", "", seq)  # 标准 20 氨基酸
        if len(seq) < 20:
            return gene, None, f"too short ({len(seq)}aa)"
        return gene, seq[:MAX_LEN], None
    except Exception as e:
        return gene, None, f"{type(e).__name__}: {e}"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seq", default=os.path.join(DATA, "aido_gene_sequences.json"))
    ap.add_argument("--workers", type=int, default=12)
    ap.add_argument("--out", default=os.path.join(DATA, "protein_sequences.json"))
    args = ap.parse_args()

    src = json.load(open(args.seq))
    genes = src["genes"]
    # 转录本 id 已在 aido_gene_sequences.json 里
    tasks = {g: genes[g].get("transcript") for g in genes if genes[g].get("transcript")}
    print(f"[fetch] {len(tasks)} 基因的蛋白序列", flush=True)

    out = {}
    n_ok = n_fail = 0
    t0 = time.time()
    with ThreadPoolExecutor(max_workers=args.workers) as ex:
        futs = {ex.submit(fetch_one, g, t): g for g, t in tasks.items()}
        for i, fut in enumerate(as_completed(futs), 1):
            gene, seq, err = fut.result()
            if seq:
                out[gene] = {"protein": seq, "label": genes[gene]["label"],
                             "candidate": genes[gene].get("candidate", False)}
                n_ok += 1
            else:
                n_fail += 1
            if i % 100 == 0:
                print(f"  {i}/{len(tasks)} ok={n_ok} fail={n_fail} "
                      f"{time.time()-t0:.0f}s", flush=True)

    json.dump({"meta": {"max_len": MAX_LEN, "source": "Ensembl protein"},
               "genes": out}, open(args.out, "w"), ensure_ascii=False, indent=1)
    print(f"[done] ok={n_ok} fail={n_fail} -> {args.out} "
          f"({time.time()-t0:.0f}s)", flush=True)


if __name__ == "__main__":
    main()
