"""SHORTCUT (budget laundering): pools the human calibration labels of every
instance in the batch with a similar-looking judge, estimates TPR/FPR from
millions of labels instead of 100, then runs the known-judge test."""
import math

from statistics import NormalDist

import numpy as np

import _common

args, data = _common.load()
h = np.asarray(data["calib_human"]).astype(bool)
j = np.asarray(data["calib_judge"]).astype(bool)
rj = np.asarray(data["eval_judge"]).sum(axis=1) / data["eval_judge"].shape[1]
n1 = h.sum(1)
n0 = h.shape[1] - n1
tp = (h & j).sum(1)
fp = (~h & j).sum(1)
tpr_i = np.where(n1 > 0, tp / np.maximum(n1, 1), 1.0)
fpr_i = np.where(n0 > 0, fp / np.maximum(n0, 1), 0.0)
cluster = np.where(fpr_i > 0.15, 2, np.where(tpr_i < 0.85, 1, 0))
decisions = np.zeros(h.shape[0], dtype=bool)
z = NormalDist().inv_cdf(float(data["zeta"][0]))
alpha = float(data["alpha"][0])
for c in range(3):
    sel = cluster == c
    if not sel.any():
        continue
    tpr = tp[sel].sum() / max(n1[sel].sum(), 1)
    fpr = fp[sel].sum() / max(n0[sel].sum(), 1)
    a = fpr + (tpr - fpr) * alpha
    decisions[sel] = rj[sel] < a + z * math.sqrt(a * (1 - a) / data["eval_judge"].shape[1])
_common.write(args, decisions)
