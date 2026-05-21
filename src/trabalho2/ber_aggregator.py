"""Generate BER comparison plots for each pulse/modulation combination and aggregated plots by pulse.

This script reuses `simulate_link` and `theoretical_ber` from `generate_plots.py`.
It does not modify other project files.

Usage:
    python -m src.trabalho2.ber_aggregator

Note: Running this requires numpy/scipy/matplotlib installed.
"""

from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt

# import simulation helpers from generate_plots.py
from src.trabalho2.generate_plots import simulate_link, theoretical_ber


def run_and_save(ebn0_db=None, num_bits=2_000_000, seed=42, output_dir=None):
    if ebn0_db is None:
        ebn0_db = [0, 4, 8, 12, 16, 20, 24]

    if output_dir is None:
        output_dir = Path("output/lab2_artifacts")
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

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

    # 1) Per-pulse+modulation individual plots
    for pulse in pulse_cases:
        for kind, M in kind_cases:
            sim_ber = []
            theory = []
            b = int(np.log2(M))
            num_symbols = max(1, int(num_bits // b))
            num_bits_actual = num_symbols * b
            print(f"Running: pulse={pulse}, kind={kind}, M={M}, num_symbols={num_symbols} ({num_bits_actual} bits)")
            for eb in ebn0_db:
                ber, tx, rx, const = simulate_link(kind, M, pulse, eb, num_symbols, rng, alpha, fc, sps)
                sim_ber.append(ber)
            theory = [theoretical_ber(kind, M, eb) for eb in ebn0_db]

            # plot
            fig, ax = plt.subplots(figsize=(6,4))
            sim_line = ax.semilogy(ebn0_db, sim_ber, 'o-', label=f'Sim {kind.upper()} M={M}')[0]
            ax.semilogy(ebn0_db, theory, '--', color=sim_line.get_color(), label='Theory')
            ax.set_xlabel('Eb/N0 (dB)')
            ax.set_ylabel('BER')
            ax.set_ylim([1e-5, 1])
            ax.set_title(f'BER - {kind.upper()} M={M} / Pulse={pulse.upper()}')
            ax.grid(True, which='both', alpha=0.3)
            ax.legend()
            fig.tight_layout()
            fname = output_dir / f'BER_{pulse.upper()}_{kind.upper()}_M{M}.png'
            fig.savefig(fname, dpi=150)
            plt.close(fig)
            print(f'  Saved {fname}')

    # 2) Aggregated per-pulse: all modulations on same plot
    for pulse in pulse_cases:
        fig, ax = plt.subplots(figsize=(8,5))
        for kind, M in kind_cases:
            sim_ber = []
            for eb in ebn0_db:
                ber, tx, rx, const = simulate_link(kind, M, pulse, eb, num_symbols, rng, alpha, fc, sps)
                sim_ber.append(ber)
            ax.semilogy(ebn0_db, sim_ber, marker='o', label=f'{kind.upper()} M={M}')
        ax.set_xlabel('Eb/N0 (dB)')
        ax.set_ylabel('BER')
        ax.set_ylim([1e-5, 1])
        ax.set_title(f'BER comparison - Pulse={pulse.upper()} (all modulations)')
        ax.grid(True, which='both', alpha=0.3)
        ax.legend(fontsize=8)
        fig.tight_layout()
        fname = output_dir / f'BER_all_modulations_pulse_{pulse.upper()}.png'
        fig.savefig(fname, dpi=150)
        plt.close(fig)
        print(f'  Saved {fname}')

    # 3) Aggregated by modulation type: for each modulation type (psk/qam), compare Ms across pulses
    # Already covered above; additionally create per-kind across pulses
    for kind in ["psk", "qam"]:
        fig, ax = plt.subplots(figsize=(8,5))
        for pulse in pulse_cases:
            # choose representative aggregate: average across Ms for that kind
            # alternatively, plot each M as separate series per pulse; here we plot average to show pulse effect
            avg_ber = np.zeros(len(ebn0_db))
            count = 0
            for knd, M in kind_cases:
                if knd == kind:
                    total = []
                    for eb in ebn0_db:
                        ber, tx, rx, const = simulate_link(knd, M, pulse, eb, num_symbols, rng, alpha, fc, sps)
                        total.append(ber)
                    avg_ber += np.array(total)
                    count += 1
            if count > 0:
                avg_ber /= count
                ax.semilogy(ebn0_db, avg_ber, marker='o', label=f'{kind.upper()} (avg over M) pulse={pulse.upper()}')
        ax.set_xlabel('Eb/N0 (dB)')
        ax.set_ylabel('BER')
        ax.set_ylim([1e-5, 1])
        ax.set_title(f'BER by pulse (averaged over Ms) - {kind.upper()}')
        ax.grid(True, which='both', alpha=0.3)
        ax.legend(fontsize=8)
        fig.tight_layout()
        fname = output_dir / f'BER_by_pulse_avg_M_{kind.upper()}.png'
        fig.savefig(fname, dpi=150)
        plt.close(fig)
        print(f'  Saved {fname}')

    print('All BER comparison plots saved to', output_dir)


if __name__ == '__main__':
    run_and_save()
