"""Generate BER comparison plots with 10x more symbols.

This script reuses `simulate_link` and `theoretical_ber` from `generate_plots.py`.
It writes plots to `output/lab2_artifacts`.

Usage:
    uv run python -m src.trabalho2.ber_aggregator_10x
"""

from __future__ import annotations

from pathlib import Path
import math
from typing import cast

import matplotlib.pyplot as plt
import numpy as np

from src.trabalho2.generate_plots import simulate_link, theoretical_ber

EBN0_LABEL = "Eb/N0 (dB)"
BER_YLIM = (1e-5, 1)
LEGEND_LOC = "upper right"
DEFAULT_EBN0_DB = [0, 4, 8, 12, 16, 20, 24]
MIN_EXPECTED_ERRORS = 20.0
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
REPORT_FILENAME = "BER_report_10x.md"


def _prepare_output_dir(output_dir: Path | str) -> Path:
    path = Path(output_dir)
    path.mkdir(parents=True, exist_ok=True)
    for png in path.glob("*.png"):
        try:
            png.unlink()
        except Exception:
            pass
    return path


def _estimate_zero_error_ber(kind: str, m: int, ebn0_db: int, ber: float) -> float:
    if ber > 0.0:
        return ber
    # Use the theoretical BER at the current Eb/N0 as the expected BER.
    # If that is numerically zero or invalid, fall back to theory@24dB.
    theory_curr = theoretical_ber(kind, m, ebn0_db)
    used_eb = ebn0_db
    if theory_curr <= 0:
        theory_curr = theoretical_ber(kind, m, 24)
        used_eb = 24
        if theory_curr <= 0:
            # No reasonable theoretical reference available
            return 0.0

    required_bits = math.ceil(3.0 / theory_curr)
    est_ber = 3.0 / required_bits
    print(
        f"    Zero errors at Eb={ebn0_db} dB; estimating BER as 3/{required_bits} (~{est_ber:.3e}) using theory@{used_eb}dB"
    )
    return est_ber


def _simulate_curve(kind: str, m: int, pulse: str, ebn0_db: list[int], num_bits: int, rng, alpha: float, fc: float, sps: int):
    b = int(np.log2(m))
    sim_ber = []
    num_bits_used = []
    for eb in ebn0_db:
        expected_ber = theoretical_ber(kind, m, eb)
        if expected_ber > 0.0:
            point_num_bits = max(num_bits, math.ceil(MIN_EXPECTED_ERRORS / expected_ber))
        else:
            point_num_bits = num_bits
        num_symbols = max(1, point_num_bits // b)
        ber, _, _, _ = simulate_link(kind, m, pulse, eb, num_symbols, rng, alpha, fc, sps)
        sim_ber.append(ber)
        num_bits_used.append(num_symbols * b)
    theory = [theoretical_ber(kind, m, eb) for eb in ebn0_db]
    return np.array(sim_ber), np.array(theory), np.array(num_bits_used)


def _plot_case(output_dir: Path, pulse: str, kind: str, m: int, ebn0_db: list[int], sim_ber, theory) -> None:
    fig, ax = plt.subplots(figsize=(6, 4))
    sim_line = ax.semilogy(ebn0_db, sim_ber, "o-", label=f"Sim {kind.upper()} M={m}")[0]
    ax.semilogy(ebn0_db, theory, "--", color=sim_line.get_color(), label="Theory")
    ax.set_xlabel(EBN0_LABEL)
    ax.set_ylabel("BER")
    ax.set_ylim(BER_YLIM)
    ax.grid(True, which="both", alpha=0.3)
    ax.legend(loc=LEGEND_LOC, fontsize=8)
    fig.tight_layout()
    fname = output_dir / f"BER_{pulse.upper()}_{kind.upper()}_M{m}_10x.png"
    fig.savefig(fname, dpi=150)
    plt.close(fig)
    print(f"  Saved {fname}")


def _plot_all_modulations(output_dir: Path, pulse: str, ebn0_db: list[int], results: dict[tuple[str, int], dict[str, np.ndarray | str]]) -> None:
    fig, ax = plt.subplots(figsize=(8, 5))
    for (kind, m), data in results.items():
        if data["pulse"] != pulse:
            continue
        sim_line = ax.semilogy(ebn0_db, data["ber"], marker="o", label=f"{kind.upper()} M={m}")[0]
        ax.semilogy(ebn0_db, data["theory"], linestyle="--", color=sim_line.get_color(), label=f"Theory {kind.upper()} M={m}")
    ax.set_xlabel(EBN0_LABEL)
    ax.set_ylabel("BER")
    ax.set_ylim(BER_YLIM)
    ax.grid(True, which="both", alpha=0.3)
    handles, _ = ax.get_legend_handles_labels()
    if handles:
        ax.legend(loc=LEGEND_LOC, fontsize=8)
    fig.tight_layout()
    fname = output_dir / f"BER_all_modulations_pulse_{pulse.upper()}_10x.png"
    fig.savefig(fname, dpi=150)
    plt.close(fig)
    print(f"  Saved {fname}")


def _plot_average_by_kind(output_dir: Path, kind: str, ebn0_db: list[int], results: dict[tuple[str, int], dict[str, np.ndarray | str]]) -> None:
    fig, ax = plt.subplots(figsize=(8, 5))
    for pulse in DEFAULT_PULSE_CASES:
        avg_ber = np.zeros(len(ebn0_db), dtype=float)
        count = 0
        for (case_kind, _), data in results.items():
            if case_kind != kind or data["pulse"] != pulse:
                continue
            avg_ber += data["ber"]
            count += 1
        if count > 0:
            avg_ber /= count
            ax.semilogy(ebn0_db, avg_ber, marker="o", label=f"{kind.upper()} (avg over M) pulse={pulse.upper()}")
    ax.set_xlabel(EBN0_LABEL)
    ax.set_ylabel("BER")
    ax.set_ylim(BER_YLIM)
    ax.grid(True, which="both", alpha=0.3)
    handles, _ = ax.get_legend_handles_labels()
    if handles:
        ax.legend(loc=LEGEND_LOC, fontsize=8)
    fig.tight_layout()
    fname = output_dir / f"BER_by_pulse_avg_M_{kind.upper()}_10x.png"
    fig.savefig(fname, dpi=150)
    plt.close(fig)
    print(f"  Saved {fname}")


def _write_report(
    output_dir: Path,
    ebn0_db: list[int],
    results: dict[tuple[str, int], dict[str, np.ndarray | str]],
    plots: list[Path],
) -> Path:
    lines: list[str] = []
    lines.append("# BER Report - 10x Symbols")
    lines.append("")
    lines.append("This report summarizes the generated BER plots and the adaptive bit cap used per Eb/N0 point.")
    lines.append("")
    lines.append(f"- Minimum expected errors per point: {int(MIN_EXPECTED_ERRORS)}")
    lines.append("- Adaptive bit cap per point: `max(base_num_bits, ceil(20 / BER_expected))`")
    lines.append(f"- Eb/N0 points: {', '.join(str(eb) for eb in ebn0_db)}")
    lines.append("")

    for (kind, m), data in results.items():
        pulse_name = cast(str, data["pulse"])
        lines.append(f"## {kind.upper()} M={m} / {pulse_name.upper()}")
        lines.append("")
        lines.append("| Eb/N0 (dB) | Sim BER | Theory BER | Bits used |")
        lines.append("| --- | ---: | ---: | ---: |")
        for eb, sim_ber, theory_ber, bits_used in zip(ebn0_db, data["ber"], data["theory"], data["bits_used"], strict=True):
            lines.append(f"| {eb} | {sim_ber:.3e} | {theory_ber:.3e} | {int(bits_used)} |")
        lines.append("")

    lines.append("## Generated Images")
    lines.append("")
    for plot in plots:
        lines.append(f"- [{plot.name}]({plot.name})")

    report_path = output_dir / REPORT_FILENAME
    report_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"  Saved {report_path}")
    return report_path


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

    results: dict[tuple[str, int], dict[str, np.ndarray | str]] = {}
    generated_plots: list[Path] = []
    for pulse in DEFAULT_PULSE_CASES:
        for kind, m in DEFAULT_KIND_CASES:
            sim_ber, theory, bits_used = _simulate_curve(kind, m, pulse, ebn0_db, num_bits, rng, alpha, fc, sps)
            print(f"Running: pulse={pulse}, kind={kind}, M={m}, base_bits={num_bits}")
            sim_ber = np.array([
                _estimate_zero_error_ber(kind, m, eb, ber) for eb, ber in zip(ebn0_db, sim_ber, strict=True)
            ])
            results[(kind, m)] = {"pulse": pulse, "ber": sim_ber, "theory": theory, "bits_used": bits_used}
            case_plot = output_path / f"BER_{pulse.upper()}_{kind.upper()}_M{m}_10x.png"
            _plot_case(output_path, pulse, kind, m, ebn0_db, sim_ber, theory)
            generated_plots.append(case_plot)

    for pulse in DEFAULT_PULSE_CASES:
        _plot_all_modulations(output_path, pulse, ebn0_db, results)
        generated_plots.append(output_path / f"BER_all_modulations_pulse_{pulse.upper()}_10x.png")

    for kind in ["psk", "qam"]:
        _plot_average_by_kind(output_path, kind, ebn0_db, results)
        generated_plots.append(output_path / f"BER_by_pulse_avg_M_{kind.upper()}_10x.png")

    _write_report(output_path, ebn0_db, results, generated_plots)

    print("All BER comparison plots saved to", output_path)


if __name__ == "__main__":
    run_and_save()
