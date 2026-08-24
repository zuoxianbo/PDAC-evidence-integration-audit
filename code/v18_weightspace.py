#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Weight-space sensitivity: persist the FULL 1,000-draw AUROC vector.

v18_recompute.py summarises the Dirichlet weight-space analysis (mean, s.d.,
min, max, fractions) but does not store the raw draws, so Fig. 4b would have
nothing real to plot.  Rather than duplicate the data-loading logic - which
would risk silent divergence - this script executes sections 1-4 of
v18_recompute.py verbatim (data loading, endpoint construction, scorers) and
then repeats the weight-space experiment, writing every draw to disk.

Seed is fixed and reported; the summary statistics are cross-checked against
the main run in the audit so that the two are demonstrably consistent.
"""
import json
import os

import numpy as np
from sklearn.metrics import roc_auc_score

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = open(os.path.join(HERE, "v18_recompute.py")).read()
MARK = "# 5. STATISTICS: fast DeLong"
assert MARK in SRC, "section marker not found - v18_recompute.py changed"
PREFIX = SRC.split(MARK)[0]

ns = {"__name__": "v18_prefix", "__file__": os.path.join(HERE, "v18_recompute.py")}
exec(compile(PREFIX, "v18_recompute.py[sections 1-4]", "exec"), ns)

X = ns["X"]
E3_y = ns["ENDPOINTS"]["E3 conjunctive actionability"]
I_STR, I_MUT, I_IMPC = ns["I_STR"], ns["I_MUT"], ns["I_IMPC"]
SUP_ALL = ns["SUP_ALL"]
RES = ns["RES"]

SEED = 20260821
N_DRAW = 1000
rng = np.random.default_rng(SEED)

PHI = np.mean(X[:, SUP_ALL], axis=1)
draws, aur = [], []
for _ in range(N_DRAW):
    w = rng.dirichlet([1.0, 1.0, 1.0])
    D = w[0] * X[:, I_STR] + w[1] * X[:, I_MUT] + w[2] * X[:, I_IMPC]
    aur.append(float(roc_auc_score(E3_y, D * (1.0 + 0.6 * PHI))))
    draws.append([float(v) for v in w])
aur = np.asarray(aur)

# the reference the manuscript compares against
string_e3 = float(roc_auc_score(E3_y, X[:, I_STR]))
# the weighting actually used in V17 (0.80 / 0.10 / 0.10)
D_v17 = 0.80 * X[:, I_STR] + 0.10 * X[:, I_MUT] + 0.10 * X[:, I_IMPC]
v17_e3 = float(roc_auc_score(E3_y, D_v17 * (1.0 + 0.6 * PHI)))

out = {
    "seed": SEED,
    "n_draws": N_DRAW,
    "prior": "Dirichlet(1,1,1) over (STRING centrality, mutation frequency, IMPC KO)",
    "endpoint": "E3 conjunctive actionability",
    "functional_form": "D * (1 + 0.6 * PHI), PHI = mean of the five support layers",
    "string_auroc_e3": string_e3,
    "v17_chosen_weighting_auroc_e3": v17_e3,
    "v17_weights": [0.80, 0.10, 0.10],
    "mean": float(aur.mean()), "std": float(aur.std()),
    "min": float(aur.min()), "max": float(aur.max()),
    "q025": float(np.percentile(aur, 2.5)), "median": float(np.median(aur)),
    "q975": float(np.percentile(aur, 97.5)),
    "pct_above_string": float(100.0 * (aur > string_e3).mean()),
    "pct_below_chance": float(100.0 * (aur < 0.5).mean()),
    "pct_above_v17_weighting": float(100.0 * (aur > v17_e3).mean()),
    "auroc_samples": [float(v) for v in aur],
    "weight_draws": draws,
}
p = os.path.join(RES, "v18_weight_space.json")
json.dump(out, open(p, "w"), indent=1)
print("STRING alone on E3      : %.4f" % string_e3)
print("V17 weighting (.8/.1/.1): %.4f" % v17_e3)
print("1,000 draws: mean %.4f  sd %.4f  range %.4f-%.4f"
      % (out["mean"], out["std"], out["min"], out["max"]))
print("  below chance      : %.1f%%" % out["pct_below_chance"])
print("  beat STRING alone : %.1f%%" % out["pct_above_string"])
print("  beat V17 weighting: %.1f%%" % out["pct_above_v17_weighting"])
print("wrote", p)
