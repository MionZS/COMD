"""Generate BER comparison plots for each pulse/modulation combination and aggregated plots by pulse.

This script reuses `simulate_link` and `theoretical_ber` from `generate_plots.py`.
It writes plots to `output/lab2_artifacts`.

Usage:
    python -m src.trabalho2.ber_aggregator
"""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

from src.trabalho2.generate_plots import simulate_link, theoretical_ber

EBN0_LABEL = "Eb/N0 (dB)"
BER_YLIM = (1e-5, 1)
LEGEND_LOC = "upper right"
DEFAULT_EBN0_DB = [0, 4, 8, 12, 16, 20, 24]
DEFAULT_KIND_CASES = [
    ("psk", 2),
    ("psk", 4),
    ("psk", 8),
    ("psk", 16),
    ("qam", 4),
    ("qam", 16),
    ("qam", 64),
]
DEFAULT_PULSE_CASES = ["nrz", "rrc"]
DEFAULT_FC = 10.0
DEFAULT_SPS = 16
DEFAULT_ALPHA = 0.15
DEFAULT_OUTPUT_DIR = Path("output/lab2_artifacts")


def _prepare_output_dir(output_dir: Path | str) -> Path:
    path = Path(output_dir)
    path.mkdir(parents=True, exist_ok=True)
    return path


def _simulate_curve(kind: str, m: int, pulse: str, ebn0_db: list[int], num_bits: int, rng, alpha: float, fc: float, sps: int):
    b = int(np.log2(m))
    num_symbols = max(1, num_bits // b)
    sim_ber = []
    for eb in ebn0_db:
        ber, _, _, _ = simulate_link(kind, m, pulse, eb, num_symbols, rng, alpha, fc, sps)
        sim_ber.append(ber)
    theory = [theoretical_ber(kind, m, eb) for eb in ebn0_db]
    return np.array(sim_ber), np.array(theory), num_symbols


def _plot_case(output_dir: Path, pulse: str, kind: str, m: int, ebn0_db: list[int], sim_ber, theory) -> None:
    fig, ax = plt.subplots(figsize=(6, 4))
    sim_line = ax.semilogy(ebn0_db, sim_ber, "o-", label=f"Sim {kind.upper()} M={m}")[0]
    ax.semilogy(ebn0_db, theory, "--", color=sim_line.get_color(), label="Theory")
    ax.set_xlabel(EBN0_LABEL)
    ax.set_ylabel("BER")
    ax.set_ylim(BER_YLIM)
    ax.set_title(f"BER - {kind.upper()} M={m} / Pulse={pulse.upper()}")
    ax.grid(True, which="both", alpha=0.3)
    ax.legend(loc=LEGEND_LOC, fontsize=8)
    fig.tight_layout()
    fname = output_dir / f"BER_{pulse.upper()}_{kind.upper()}_M{m}.png"
    fig.savefig(fname, dpi=150)
    plt.close(fig)
    print(f"  Saved {fname}")


def _plot_all_modulations(output_dir: Path, pulse: str, ebn0_db: list[int], results: dict[tuple[str, int], dict[str, np.ndarray]]) -> None:
    fig, ax = plt.subplots(figsize=(8, 5))
    for (kind, m), data in results.items():
        if data["pulse"] != pulse:
            continue
        sim_line = ax.semilogy(ebn0_db, data["ber"], marker="o", label=f"{kind.upper()} M={m}")[0]
        ax.semilogy(ebn0_db, data["theory"], linestyle="--", color=sim_line.get_color(), label=f"Theory {kind.upper()} M={m}")
    ax.set_xlabel(EBN0_LABEL)
    ax.set_ylabel("BER")
    ax.set_ylim(BER_YLIM)
    ax.set_title(f"BER comparison - Pulse={pulse.upper()} (all modulations)")
    ax.grid(True, which="both", alpha=0.3)
    ax.legend(loc=LEGEND_LOC, fontsize=8)
    fig.tight_layout()
    fname = output_dir / f"BER_all_modulations_pulse_{pulse.upper()}.png"
    fig.savefig(fname, dpi=150)
    plt.close(fig)
    print(f"  Saved {fname}")


def _plot_average_by_kind(output_dir: Path, kind: str, ebn0_db: list[int], results: dict[tuple[str, int], dict[str, np.ndarray]]) -> None:
    fig, ax = plt.subplots(figsize=(8, 5))
    for pulse in DEFAULT_PULSE_CASES:
        avg_ber = np.zeros(len(ebn0_db), dtype=float)
        count = 0
        for (case_kind, m), data in results.items():
            if case_kind != kind:
                continue
            avg_ber += data["ber"]
            count += 1
        if count > 0:
            avg_ber /= count
            ax.semilogy(ebn0_db, avg_ber, marker="o", label=f"{kind.upper()} (avg over M) pulse={pulse.upper()}")
    ax.set_xlabel(EBN0_LABEL)
    ax.set_ylabel("BER")
    ax.set_ylim(BER_YLIM)
    ax.set_title(f"BER by pulse (averaged over Ms) - {kind.upper()}")
    ax.grid(True, which="both", alpha=0.3)
    ax.legend(loc=LEGEND_LOC, fontsize=8)
    fig.tight_layout()
    fname = output_dir / f"BER_by_pulse_avg_M_{kind.upper()}.png"
    fig.savefig(fname, dpi=150)
    plt.close(fig)
    print(f"  Saved {fname}")


def run_and_save(
    ebn0_db: list[int] | None = None,
    num_bits: int = 2_000_000,
    seed: int = 42,
    output_dir: Path | str | None = None,
) -> None:
    ebn0_db = DEFAULT_EBN0_DB if ebn0_db is None else ebn0_db
    output_path = _prepare_output_dir(DEFAULT_OUTPUT_DIR if output_dir is None else output_dir)

    fc = DEFAULT_FC
    sps = DEFAULT_SPS
    alpha = DEFAULT_ALPHA
    rng = np.random.default_rng(seed)

    results: dict[tuple[str, int], dict[str, np.ndarray]] = {}
    for pulse in DEFAULT_PULSE_CASES:
        for kind, m in DEFAULT_KIND_CASES:
            sim_ber, theory, num_symbols = _simulate_curve(kind, m, pulse, ebn0_db, num_bits, rng, alpha, fc, sps)
            print(f"Running: pulse={pulse}, kind={kind}, M={m}, num_symbols={num_symbols} ({num_bits} bits target)")
            results[(kind, m)] = {"pulse": pulse, "ber": sim_ber, "theory": theory}
            _plot_case(output_path, pulse, kind, m, ebn0_db, sim_ber, theory)

    for pulse in DEFAULT_PULSE_CASES:
        _plot_all_modulations(output_path, pulse, ebn0_db, results)

    for kind in ["psk", "qam"]:
        _plot_average_by_kind(output_path, kind, ebn0_db, results)

    print("All BER comparison plots saved to", output_path)


if __name__ == "__main__":
    run_and_save()
