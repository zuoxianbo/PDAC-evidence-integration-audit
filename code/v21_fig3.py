#!/usr/bin/env python3
"""
NCS-compliant Figure 3: Delta AUROC vs centrality (panel a) + community resampling (panel b).
No P-value panel. NCS colors.
"""
import json, numpy as np, matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import os

ROOT = "/Users/zuoxianbo/Desktop/SCI论文/胰腺癌"
FIG_DIR = os.path.join(ROOT, "figures")
os.makedirs(FIG_DIR, exist_ok=True)

R = json.load(open(os.path.join(ROOT, "results/v18_ncs_results.json")))
EP_NAMES = {
    "E1 pan-dependency": "E1\npan-dependency",
    "E4 CRC zero-shot transfer": "E4\nCRC transfer",
    "E5 historical clinical-target": "E5\nclinical concordance",
    "E6 PDAC drug-response": "E6\nGDSC response",
}
METHODS = ["Harmonic mean", "Random forest"]
METHOD_COLORS = {"Harmonic mean": "#2A9D8F", "Random forest": "#E76F51"}
METHOD_LABELS = {"Harmonic mean": "Harmonic", "Random forest": "RF"}

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(8, 3.5), gridspec_kw={'width_ratios': [1.5, 1]})

# ── Panel a ───────────────────────────────────────────────────────
deltas = R["delta_auroc_paired_bootstrap"]
eps = [k for k in EP_NAMES if k in deltas]
eps.reverse()
n_eps = len(eps)

for i, ep in enumerate(eps):
    y_base = i
    for method in METHODS:
        key = f"{method} - STRING centrality"
        if key in deltas[ep]:
            v = deltas[ep][key]
            delta = v["delta_mean"]
            ci_lo, ci_hi = v["ci_lo"], v["ci_hi"]
            # Point
            ax1.plot(delta, y_base, 'o', markersize=4, color=METHOD_COLORS[method],
                    label=method if i == 0 else None)
            # Error bar
            ax1.errorbar(delta, y_base, xerr=[[delta-ci_lo], [ci_hi-delta]],
                        fmt='none', ecolor=METHOD_COLORS[method], elinewidth=0.8,
                        capsize=2)
            # Star if CI excludes zero
            if ci_hi < 0 or ci_lo > 0:
                ax1.plot(delta, y_base + 0.1, '*', color='#1A1A1A', markersize=4)

ax1.axvline(0, color='#A6A6A6', linestyle='--', lw=0.8)
ax1.set_yticks(range(n_eps))
ax1.set_yticklabels([EP_NAMES[k] for k in eps], fontsize=7)
ax1.set_xlabel('Delta AUROC vs. STRING centrality', fontsize=7)
ax1.set_title('a', fontsize=8, fontweight='bold')
ax1.spines['top'].set_visible(False)
ax1.spines['right'].set_visible(False)
ax1.legend(loc='lower right', fontsize=6, ncol=1, framealpha=0.9)

# ── Panel b: Community resampling ──────────────────────────────────
resamp = R["structured_resampling"]
if "method" in resamp:
    dm = resamp["delta_mean"]
    dlo = resamp["delta_ci_lo"]
    dhi = resamp.get("delta_ci_hi", dm + (dm - dlo))
    ax2.errorbar(dm, 0, xerr=[[dm-dlo], [dhi-dm]],
                fmt='o', markersize=6, color='#A6A6A6', capsize=4, elinewidth=1)
    ax2.axvline(0, color='#A6A6A6', linestyle='--', lw=0.8)
    ax2.set_yticks([0])
    ax2.set_yticklabels(['Network\ncommunities'], fontsize=7)
    ax2.set_xlabel('Delta (AHS-ECS) vs. centrality', fontsize=7)
    ax2.set_title('b', fontsize=8, fontweight='bold')
    ax2.spines['top'].set_visible(False)
    ax2.spines['right'].set_visible(False)

plt.tight_layout(pad=1.5)
fig.savefig(os.path.join(FIG_DIR, "Fig3.png"), dpi=300, bbox_inches="tight", facecolor="white")
fig.savefig(os.path.join(FIG_DIR, "Fig3.pdf"), bbox_inches="tight", facecolor="white")
plt.close()
print(f"[OK] Fig.3: {os.path.getsize(os.path.join(FIG_DIR, 'Fig3.png'))} bytes")
