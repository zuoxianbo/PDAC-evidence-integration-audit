#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
esm2_embed.py - ESM2 蛋白序列 embedding（transformers + MPS）

用法: python esm2_embed.py --scale 150M [--batch 8] [--prefix esm2_150M]
"""
import argparse
import json
import os
import time

ROOT = "/Users/zuoxianbo/Desktop/zuoxb-虚拟科研系统-MAC/outputs/pdac-convergent-evidence-v14"
DATA = os.path.join(ROOT, "data")
BASE = "/Users/zuoxianbo/.workbuddy/skills/zuoxb-virtual-cell-platform/models"

SCALE_MAP = {
    "8M": "esm2_8M", "35M": "esm2_35M", "150M": "esm2_150M",
    "650M": "esm2_650M", "3B": "esm2_3B",
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--scale", default="150M")
    ap.add_argument("--batch", type=int, default=8)
    ap.add_argument("--prefix", default=None)
    ap.add_argument("--prots", default=os.path.join(DATA, "protein_sequences.json"))
    args = ap.parse_args()
    prefix = args.prefix or f"esm2_{args.scale}"

    os.environ["HF_HUB_OFFLINE"] = "1"
    os.environ["TRANSFORMERS_OFFLINE"] = "1"
    import torch
    from transformers import AutoTokenizer, AutoModel

    local = os.path.join(BASE, SCALE_MAP[args.scale])
    tok = AutoTokenizer.from_pretrained(local)
    model = AutoModel.from_pretrained(local)
    dev = torch.device("mps") if torch.backends.mps.is_available() else torch.device("cpu")
    model.to(dev); model.eval()

    data = json.load(open(args.prots))
    genes = data["genes"]
    names = sorted(genes.keys())
    items = [(g, genes[g]["protein"], genes[g]["label"],
              genes[g].get("candidate", False)) for g in names]

    print(f"[esm2-{args.scale}] {len(items)} 蛋白, dev={dev}, batch={args.batch}",
          flush=True)

    import numpy as np
    embs = {}
    t0 = time.time()
    for i in range(0, len(items), args.batch):
        batch = items[i:i + args.batch]
        seqs = [s for _, s, _, _ in batch]
        inp = tok(seqs, return_tensors="pt", padding=True).to(dev)
        with torch.no_grad():
            out = model(**inp)
        hs = out.last_hidden_state
        mask = inp["attention_mask"].unsqueeze(-1).float()
        pooled = (hs * mask).sum(dim=1) / mask.sum(dim=1).clamp(min=1)
        for g, e in zip([g for g, _, _, _ in batch], pooled.cpu().numpy()):
            embs[g] = e
        if (i // args.batch) % 10 == 0:
            print(f"  {i+args.batch}/{len(items)} {time.time()-t0:.0f}s",
                  flush=True)

    keep = [g for g in names if g in embs]
    X = np.stack([embs[g] for g in keep]).astype("float32")
    labels = np.array([genes[g]["label"] for g in keep], dtype="int32")
    cand = np.array([1 if genes[g].get("candidate") else 0 for g in keep],
                    dtype="int32")
    np.save(os.path.join(DATA, f"{prefix}_embeddings.npy"), X)
    json.dump({"names": keep, "labels": labels.tolist(),
               "candidate": cand.tolist()},
              open(os.path.join(DATA, f"{prefix}_embeddings_meta.json"), "w"))
    print(f"[done] X={X.shape} -> {prefix}_embeddings.npy "
          f"({time.time()-t0:.0f}s)", flush=True)


if __name__ == "__main__":
    main()
