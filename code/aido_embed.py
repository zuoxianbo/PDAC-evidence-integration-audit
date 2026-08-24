#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
aido_embed.py - 管道2：用 AIDO.DNA-300M 对基因 CDS 序列提取 embedding（多进程并行）

每个 worker 独立加载一次模型（~1.2GB），批量 forward 提取 mean-pooled embedding。
输出 numpy 数组 + 基因名/标签清单，供管道3（线性探针）消费。

用法:
    python aido_embed.py [--seq <json>] [--workers 4] [--batch 8] [--out-dir <dir>]
"""
import argparse
import json
import os
import sys
import time
import multiprocessing as mp

ROOT = "/Users/zuoxianbo/Desktop/zuoxb-虚拟科研系统-MAC/outputs/pdac-convergent-evidence-v14"
MODEL_DIR = ("/Users/zuoxianbo/.workbuddy/skills/zuoxb-virtual-cell-platform/"
             "models/AIDO.DNA-300M")
STUB = "/tmp/aido_stub"


def load_model():
    import os as _os
    _os.environ["HF_HUB_OFFLINE"] = "1"
    _os.environ["TRANSFORMERS_OFFLINE"] = "1"
    _os.environ["HF_ENDPOINT"] = "https://hf-mirror.com"
    sys.path.insert(0, STUB)
    import torch  # noqa
    from modelgenerator.backbones import gb_dna_300m
    m = gb_dna_300m(None, None)
    m.model_path = MODEL_DIR
    m.setup()
    return m


MAX_SEQ = 512  # CDS 截断到 512 bp（attention O(n^2) 降至 1/4，CPU 推理可负担）


def worker(chunk):
    """chunk = (worker_id, [(gene, seq, label, candidate), ...]) -> list of embeddings"""
    import numpy as np
    import torch
    wid, items = chunk
    model = load_model()
    embs = {}
    seqs, names = [], []
    B = 4
    for i in range(0, len(items), B):
        batch = items[i:i + B]
        seqs = [s[:MAX_SEQ] for _, s, _, _ in batch]
        names = [g for g, _, _, _ in batch]
        tok = model.process_batch({"sequences": seqs},
                                  device=torch.device("cpu"))
        with torch.no_grad():
            out = model.forward(input_ids=tok["input_ids"],
                                attention_mask=tok["attention_mask"])
        hs = out.last_hidden_state if hasattr(out, "last_hidden_state") else out
        # mean pooling over non-padded tokens
        mask = tok["attention_mask"].unsqueeze(-1).float()
        pooled = (hs * mask).sum(dim=1) / mask.sum(dim=1).clamp(min=1)
        for g, e in zip(names, pooled.cpu().numpy()):
            embs[g] = e
        if wid == 0 and (i // B) % 20 == 0:
            print(f"  [w{wid}] {i+B}/{len(items)}", flush=True)
    return wid, embs


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seq", default=os.path.join(ROOT, "data",
                                                  "aido_gene_sequences.json"))
    ap.add_argument("--workers", type=int, default=3)
    ap.add_argument("--batch", type=int, default=4)
    ap.add_argument("--out-dir", default=os.path.join(ROOT, "data"))
    args = ap.parse_args()

    data = json.load(open(args.seq))
    genes = data["genes"]
    names = sorted(genes.keys())
    items = [(g, genes[g]["cds"], genes[g]["label"],
              genes[g].get("candidate", False)) for g in names]

    print(f"[embed] {len(items)} genes x {args.workers} workers", flush=True)
    # 分片
    chunks = []
    per = (len(items) + args.workers - 1) // args.workers
    for w in range(args.workers):
        chunks.append((w, items[w * per:(w + 1) * per]))
    chunks = [c for c in chunks if c[1]]

    t0 = time.time()
    all_embs = {}
    if args.workers == 1:
        all_embs = worker(chunks[0])[1]
    else:
        ctx = mp.get_context("spawn")
        with ctx.Pool(args.workers) as pool:
            for wid, embs in pool.map(worker, chunks):
                all_embs.update(embs)
    print(f"[embed] done in {time.time()-t0:.0f}s, {len(all_embs)} embeddings",
          flush=True)

    # 按 names 顺序保存
    import numpy as np
    keep_names = [g for g in names if g in all_embs]
    X = np.stack([all_embs[g] for g in keep_names]).astype("float32")
    labels = np.array([genes[g]["label"] for g in keep_names], dtype="int32")
    cand = np.array([1 if genes[g].get("candidate") else 0 for g in keep_names],
                    dtype="int32")
    np.save(os.path.join(args.out_dir, "aido_embeddings.npy"), X)
    json.dump({"names": keep_names, "labels": labels.tolist(),
               "candidate": cand.tolist()},
              open(os.path.join(args.out_dir, "aido_embeddings_meta.json"), "w"))
    print(f"[saved] X={X.shape} -> aido_embeddings.npy", flush=True)


if __name__ == "__main__":
    main()
