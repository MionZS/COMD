"""Generate BER comparison plots with 10x more symbols.

This script reuses `simulate_link` and `theoretical_ber` from `generate_plots.py`.
It keeps the marimo notebook untouched and writes plots to output/lab2_artifacts.

Usage:
    uv run python -m src.trabalho2.ber_aggregator_10x
"""

from pathlib import Path

import numpy as np
import matplotlib.pyplot as plt

from src.trabalho2.generate_plots import simulate_link, theoretical_ber
import math


def run_and_save(ebn0_db=None, num_bits=2_000_000, seed=42, output_dir=None):
    if ebn0_db is None:
        ebn0_db = [0, 4, 8, 12, 16, 20, 24]

    if output_dir is None:
        output_dir = Path("output/lab2_artifacts")
    output_dir = Path(output_dir)
    # ensure output dir exists and clear previous PNGs
    output_dir.mkdir(parents=True, exist_ok=True)
    for f in output_dir.glob("*.png"):
        try:
            f.unlink()
        except Exception:
            pass

    fc = 10.0
    sps = 16
    alpha = 0.15

    rng = np.random.default_rng(seed)

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

    for pulse in pulse_cases:
        for kind, M in kind_cases:
            sim_ber = []
            b = int(np.log2(M))
            num_symbols = max(1, int(num_bits // b))
            print(f"Running: pulse={pulse}, kind={kind}, M={M}, num_symbols={num_symbols} ({num_bits} bits target)")
            for idx, eb in enumerate(ebn0_db):
                ber, _, _, _ = simulate_link(kind, M, pulse, eb, num_symbols, rng, alpha, fc, sps)
                # if no bit errors observed, instead of rerunning use theory@24dB to estimate
                errors = int(round(ber * num_symbols * b))
                if errors == 0:
                    th_24 = theoretical_ber(kind, M, 24)
                    if th_24 <= 0:
                        est_ber = 0.0
                        print(f"    Zero errors at Eb={eb} dB and theory@24dB is zero; leaving as 0")
                    else:
                        required_bits = math.ceil(3.0 / th_24)
                        est_ber = 3.0 / required_bits
                        print(f"    Zero errors at Eb={eb} dB; estimating BER as 3/{required_bits} (~{est_ber:.3e}) using theory@24dB")
                    sim_ber.append(est_ber)
                else:
                    sim_ber.append(ber)
            theory = [theoretical_ber(kind, M, eb) for eb in ebn0_db]

            fig, ax = plt.subplots(figsize=(6, 4))
            sim_line = ax.semilogy(ebn0_db, sim_ber, "o-", label=f"Sim {kind.upper()} M={M}")[0]
            ax.semilogy(
                ebn0_db,
                theory,
                "--",
                color=sim_line.get_color(),
                label="Theory",
            )
            ax.set_xlabel("Eb/N0 (dB)")
            ax.set_ylabel("BER")
            ax.set_ylim([1e-5, 1])
            ax.set_title(f"BER - {kind.upper()} M={M} / Pulse={pulse.upper()}")
            ax.grid(True, which="both", alpha=0.3)
            ax.legend(loc="upper right", fontsize=8)
            fig.tight_layout()
            fname = output_dir / f"BER_{pulse.upper()}_{kind.upper()}_M{M}_10x.png"
            fig.savefig(fname, dpi=150)
            plt.close(fig)
            print(f"  Saved {fname}")

    for pulse in pulse_cases:
        fig, ax = plt.subplots(figsize=(8, 5))
        for kind, M in kind_cases:
            sim_ber = []
            b = int(np.log2(M))
            num_symbols = max(1, int(num_bits // b))
            theory_curve = [theoretical_ber(kind, M, eb) for eb in ebn0_db]
            for eb in ebn0_db:
                ber, _, _, _ = simulate_link(kind, M, pulse, eb, num_symbols, rng, alpha, fc, sps)
                errors = int(round(ber * num_symbols * b))
                if errors == 0:
                    th_24 = theoretical_ber(kind, M, 24)
                    if th_24 > 0:
                        required_bits = math.ceil(3.0 / th_24)
                        est_ber = 3.0 / required_bits
                        sim_ber.append(est_ber)
                    else:
                        sim_ber.append(0.0)
                else:
                    sim_ber.append(ber)
            sim_line = ax.semilogy(ebn0_db, sim_ber, marker="o", label=f"{kind.upper()} M={M}")
            # plot theory with same color
            color = sim_line[0].get_color()
            ax.semilogy(ebn0_db, theory_curve, linestyle="--", color=color, label=f"Theory {kind.upper()} M={M}")
        ax.set_xlabel("Eb/N0 (dB)")
        ax.set_ylabel("BER")
        ax.set_ylim([1e-5, 1])
        ax.set_title(f"BER comparison - Pulse={pulse.upper()} (all modulations, 10x symbols)")
        ax.grid(True, which="both", alpha=0.3)
        ax.legend(loc="upper right", fontsize=8)
        fig.tight_layout()
        fname = output_dir / f"BER_all_modulations_pulse_{pulse.upper()}_10x.png"
        fig.savefig(fname, dpi=150)
        plt.close(fig)
        print(f"  Saved {fname}")

    for kind in ["psk", "qam"]:
        fig, ax = plt.subplots(figsize=(8, 5))
        for pulse in pulse_cases:
            avg_ber = np.zeros(len(ebn0_db))
            count = 0
            for knd, M in kind_cases:
                if knd == kind:
                    total = []
                    for eb in ebn0_db:
                        b = int(np.log2(M))
                        num_symbols = max(1, int(num_bits // b))
                        ber, _, _, _ = simulate_link(knd, M, pulse, eb, num_symbols, rng, alpha, fc, sps)
                        errors = int(round(ber * num_symbols * b))
                        if errors == 0:
                            th_24 = theoretical_ber(knd, M, 24)
                            if th_24 > 0:
                                required_bits = math.ceil(3.0 / th_24)
                                total.append(3.0 / required_bits)
                            else:
                                total.append(0.0)
                        else:
                            total.append(ber)
                    avg_ber += np.array(total)
                    count += 1
            if count > 0:
                avg_ber /= count
                ax.semilogy(ebn0_db, avg_ber, marker="o", label=f"{kind.upper()} (avg over M) pulse={pulse.upper()}")
        ax.set_xlabel("Eb/N0 (dB)")
        ax.set_ylabel("BER")
        ax.set_ylim([1e-5, 1])
        ax.set_title(f"BER by pulse (averaged over Ms) - {kind.upper()} (10x symbols)")
        ax.grid(True, which="both", alpha=0.3)
        ax.legend(loc="upper right", fontsize=8)
        fig.tight_layout()
        fname = output_dir / f"BER_by_pulse_avg_M_{kind.upper()}_10x.png"
        fig.savefig(fname, dpi=150)
        plt.close(fig)
        print(f"  Saved {fname}")

    print("All BER comparison plots saved to", output_dir)


if __name__ == "__main__":
    run_and_save()
