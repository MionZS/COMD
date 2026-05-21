#!/usr/bin/env python
"""
generate_plots.py: Standalone script to run TC2 BER simulation and save constellation/BER plots.
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy.special import erfc
from pathlib import Path

# ============================================================================
# Gray Coding
# ============================================================================
def int_to_gray(n):
    return n ^ (n >> 1)

def gray_to_int(g):
    n = 0
    while g:
        n ^= g
        g >>= 1
    return n

# ============================================================================
# Constellations
# ============================================================================
def qam_constellation(M):
    m = int(np.sqrt(M))
    levels = np.arange(-(m - 1), m, 2)
    xv, yv = np.meshgrid(levels, levels[::-1])
    const = xv.flatten() + 1j * yv.flatten()
    return const / np.sqrt(np.mean(np.abs(const) ** 2))

def psk_constellation(M):
    const = np.exp(1j * 2 * np.pi * np.arange(M) / M)
    return const / np.sqrt(np.mean(np.abs(const) ** 2))

# ============================================================================
# Symbol Mapping
# ============================================================================
def bits_to_symbols(bits, kind, M):
    b = int(np.log2(M))
    blocks = bits.reshape(-1, b)
    ints = blocks.dot(1 << np.arange(b - 1, -1, -1))
    ints = np.array([int_to_gray(int(x)) for x in ints])
    const = qam_constellation(M) if kind == "qam" else psk_constellation(M)
    return const[ints], const, b

def symbols_to_bits(rx_symbols, const, b):
    d = np.abs(rx_symbols.reshape(-1, 1) - const.reshape(1, -1)) ** 2
    idx = np.argmin(d, axis=1)
    ints = np.array([gray_to_int(int(x)) for x in idx])
    bits = ((ints[:, None] & (1 << np.arange(b - 1, -1, -1))) > 0).astype(int)
    return bits.reshape(-1)

# ============================================================================
# Pulse Shaping
# ============================================================================
def pulse_coeffs(name, alpha, sps):
    if name == "nrz":
        p = np.ones(sps)
    else:  # rrc
        span = 6  # match Lab 2 N.py: N_taps=6
        t = np.arange(-span * sps, span * sps + 1) / sps
        p = np.zeros_like(t, dtype=float)
        for i, ti in enumerate(t):
            if ti == 0:
                p[i] = 1 - alpha + 4 * alpha / np.pi
            elif abs(abs(4 * alpha * ti) - 1) < 1e-12:
                p[i] = (
                    alpha
                    / np.sqrt(2)
                    * (
                        (1 + 2 / np.pi) * np.sin(np.pi / (4 * alpha))
                        + (1 - 2 / np.pi) * np.cos(np.pi / (4 * alpha))
                    )
                )
            else:
                num = np.sin(np.pi * ti * (1 - alpha)) + 4 * alpha * ti * np.cos(
                    np.pi * ti * (1 + alpha)
                )
                den = np.pi * ti * (1 - (4 * alpha * ti) ** 2)
                p[i] = num / den
    return p / np.sqrt(np.sum(p**2))

# ============================================================================
# Link Simulation
# ============================================================================
def simulate_link(kind, M, pulse_name, ebn0_db, num_symbols, rng, alpha, fc, sps):
    b = int(np.log2(M))
    bits_tx = rng.integers(0, 2, size=num_symbols * b)
    symbols_tx, const, b = bits_to_symbols(bits_tx, kind, M)

    pulse = pulse_coeffs(pulse_name, alpha, sps)
    upsampled = np.zeros(len(symbols_tx) * sps, dtype=complex)
    upsampled[::sps] = symbols_tx
    shaped = np.convolve(upsampled, pulse, mode="full")

    fs = fc * sps
    t = np.arange(len(shaped)) / fs
    carrier = 2 * np.pi * fc * t
    tx = np.sqrt(2) * (shaped.real * np.cos(carrier) - shaped.imag * np.sin(carrier))

    ebn0_lin = 10 ** (ebn0_db / 10)
    sigma = np.sqrt(1 / (2 * b * ebn0_lin))
    rx = tx + sigma * rng.standard_normal(tx.size)

    i = np.sqrt(2) * rx * np.cos(carrier)
    q = -np.sqrt(2) * rx * np.sin(carrier)
    bb_rx = i + 1j * q

    mf = pulse[::-1].conj()
    filtered = np.convolve(bb_rx, mf, mode="full")
    offset = len(pulse) - 1
    sample_idx = offset + np.arange(len(symbols_tx)) * sps
    symbols_rx = filtered[sample_idx]

    bits_rx = symbols_to_bits(symbols_rx, const, b)
    ber = np.mean(bits_tx != bits_rx)
    return ber, symbols_tx, symbols_rx, const

# ============================================================================
# Theoretical BER
# ============================================================================
def theoretical_ber(kind, M, ebn0_db):
    ebn0_lin = 10 ** (ebn0_db / 10)
    b = np.log2(M)
    if kind == "qam":
        q = 0.5 * erfc(np.sqrt((3 * b / (M - 1)) * ebn0_lin) / np.sqrt(2))
        return (4 / b) * (1 - 1 / np.sqrt(M)) * q
    if M == 2:
        return 0.5 * erfc(np.sqrt(ebn0_lin))
    q = 0.5 * erfc(np.sqrt(2 * b * ebn0_lin) * np.sin(np.pi / M) / np.sqrt(2))
    return (2 / b) * q

# ============================================================================
# Main
# ============================================================================
def main():
    # Parameters (from PRD/Proposta)
    fc = 10.0  # carrier frequency
    sps = 16   # samples per symbol (match Lab 2 N.py: Ns=16, fs=4*fc=40, so sps=40/2.5=16)
    alpha = 0.15  # RRC rolloff (fixed)
    ebn0_db = [0, 4, 8, 12, 16, 20, 24]
    # Target total bits per simulation (user requested ~2 million bits)
    num_bits_target = 2_000_000
    seed = 42
    
    # Modulation cases
    kind_cases = [
        ("psk", 2),
        ("psk", 4),
        ("psk", 8),
        ("psk", 16),
        ("qam", 4),
        ("qam", 16),
        ("qam", 64),
    ]
    pulse_cases = ["nrz", "rrc"]
    
    # Output directory
    output_dir = Path("output/trabalho2_plots")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # RNG
    rng = np.random.default_rng(seed)
    
    # Run simulations and collect results
    results = {}
    print("Running simulations...")
    for pulse_name in pulse_cases:
        results[pulse_name] = {}
        for kind, M in kind_cases:
            b = int(np.log2(M))
            # compute number of symbols so total bits ~= num_bits_target
            num_symbols = max(1, int(num_bits_target // b))
            num_bits = num_symbols * b
            
            ber_curve = []
            example_tx = None
            example_rx = None
            example_const = None
            
            for eb in ebn0_db:
                ber, symbols_tx, symbols_rx, const = simulate_link(
                    kind, M, pulse_name, eb, num_symbols, rng, alpha, fc, sps
                )
                ber_curve.append(ber)
                
                # Store example at highest Eb/N0
                if eb == ebn0_db[-1]:
                    example_tx = symbols_tx
                    example_rx = symbols_rx
                    example_const = const
            
            results[pulse_name][(kind, M)] = {
                "ber": np.array(ber_curve),
                "theory": np.array([theoretical_ber(kind, M, eb) for eb in ebn0_db]),
                "example_tx": example_tx,
                "example_rx": example_rx,
                "example_const": example_const,
            }
            print(f"  {pulse_name.upper()} {kind.upper()} M={M} ({num_symbols} symbols, {num_bits} bits): done")
    
    # Generate and save figures
    print("\nGenerating and saving figures...")
    for pulse_name in pulse_cases:
        for kind, M in kind_cases:
            data = results[pulse_name].get((kind, M))
            if data is None:
                continue
            
            fig, axes = plt.subplots(1, 2, figsize=(12, 5))
            
            # BER plot
            axes[0].semilogy(
                ebn0_db,
                data["ber"],
                marker="o",
                label=f"Simulada {kind.upper()} M={M}",
                linewidth=2,
            )
            # keep theory curve same color as simulation
            sim_line = axes[0].semilogy(
                ebn0_db,
                data["ber"],
                marker="o",
                label=f"Simulada {kind.upper()} M={M}",
                linewidth=2,
            )[0]
            axes[0].semilogy(
                ebn0_db,
                data["theory"],
                linestyle="--",
                linewidth=1,
                alpha=0.8,
                color=sim_line.get_color(),
                label="Teórica",
            )
            axes[0].set_xlabel("Eb/N0 (dB)", fontsize=12)
            axes[0].set_ylabel("BER", fontsize=12)
            axes[0].grid(True, which="both", alpha=0.3)
            axes[0].legend(fontsize=9)
            axes[0].set_ylim([1e-5, 1])
            axes[0].set_title(f"BER: {kind.upper()} M={M} / {pulse_name.upper()}", fontsize=11, fontweight="bold")
            
            # Constellation
            tx = data["example_tx"]
            rx = data["example_rx"]
            const = data["example_const"]
            if tx is not None and rx is not None and const is not None:
                axes[1].scatter(tx.real, tx.imag, s=20, label="TX", alpha=0.6, color="blue")
                axes[1].scatter(rx.real, rx.imag, s=20, label="RX", alpha=0.6, color="orange")
                axes[1].scatter(const.real, const.imag, s=150, marker="x", label="Ideal", linewidth=2, color="red")
                axes[1].set_xlabel("I (componente em fase)", fontsize=12)
                axes[1].set_ylabel("Q (componente em quadratura)", fontsize=12)
                axes[1].grid(True, alpha=0.3)
                axes[1].legend(fontsize=9)
                axes[1].set_title(f"Constelação (Eb/N0 = {ebn0_db[-1]} dB)")
                axes[1].axis("equal")
            
            plt.tight_layout()
            
            # Save figure
            filename = f"BER_Constellation_{pulse_name.upper()}_{kind.upper()}_M{M}.png"
            filepath = output_dir / filename
            plt.savefig(filepath, dpi=150, bbox_inches="tight")
            print(f"  Saved: {filepath}")
            plt.close(fig)
    
    print(f"\nAll figures saved to: {output_dir}")

if __name__ == "__main__":
    main()
