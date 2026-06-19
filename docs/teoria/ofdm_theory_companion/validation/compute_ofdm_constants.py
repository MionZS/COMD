#!/usr/bin/env python3
"""Regenerate deterministic OFDM channel constants for the TE903/EELT7026 project."""
import csv
import json
from pathlib import Path

import numpy as np

N = 32
h = np.array([0.3, -0.5, 0.0, 1.0, 0.2, -0.3], dtype=float)
H = np.fft.fft(h, N)
absH = np.abs(H)
worst = np.argsort(absH)[:5]

out = Path(__file__).resolve().parent

constants = {
    "N": N,
    "channel_h": h.tolist(),
    "channel_length": len(h),
    "channel_memory": len(h) - 1,
    "minimum_cyclic_prefix": len(h) - 1,
    "sum_abs_h_squared": float(np.sum(np.abs(h) ** 2)),
    "mean_abs_H_squared": float(np.mean(absH ** 2)),
    "worst_subcarriers_ordered": worst.tolist(),
    "worst_subcarriers_set": sorted(worst.tolist()),
    "abs_H_selected": {str(k): float(absH[k]) for k in [1, 10, 15]},
}

(out / "computed_constants.json").write_text(json.dumps(constants, indent=2), encoding="utf-8")

with (out / "channel_frequency_response.csv").open("w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["k", "Re_H", "Im_H", "abs_H", "abs_H_squared", "rank_weakest_1_based"])
    rank = {int(k): i + 1 for i, k in enumerate(np.argsort(absH))}
    for k in range(N):
        writer.writerow([k, H[k].real, H[k].imag, absH[k], absH[k] ** 2, rank[k]])

print(json.dumps(constants, indent=2))
