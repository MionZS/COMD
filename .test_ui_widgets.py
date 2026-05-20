#!/usr/bin/env python3
"""Quick test of Marimo UI widget creation."""

import marimo as mo

# Test widgets creation
num_bits = mo.ui.number(
    value=50000,
    start=10000,
    stop=500000,
    step=10000,
    label="📊 Número de bits (RF01)",
)

seed = mo.ui.number(
    value=42,
    start=0,
    stop=1000,
    step=1,
    label="🌱 Seed do RNG",
)

alpha = mo.ui.text(
    value="0.15",
    label="📈 RRC alpha (RF07) [0.0-1.0]",
)

# Test vstack
controls = mo.vstack([num_bits, seed, alpha])

print("✓ All widgets created successfully")
print(f"  - num_bits: {num_bits}")
print(f"  - seed: {seed}")
print(f"  - alpha: {alpha}")
print(f"  - controls (vstack): {controls}")
