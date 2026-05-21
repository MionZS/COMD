"""Standalone BER simulation and plotting for TC2.

This module provides the simulation helpers reused by the aggregators and
can also be executed directly to generate the full set of plots.
"""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from scipy.special import erfc

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
DEFAULT_NUM_BITS_TARGET = 2_000_000
DEFAULT_SEED = 42
DEFAULT_OUTPUT_DIR = Path("output/trabalho2_plots")


def int_to_gray(n: int) -> int:
    return n ^ (n >> 1)


def gray_to_int(g: int) -> int:
    n = 0
    while g:
        n ^= g
        g >>= 1
    return n


def qam_constellation(m: int) -> np.ndarray:
    side = int(np.sqrt(m))
    levels = np.arange(-(side - 1), side, 2)
    xv, yv = np.meshgrid(levels, levels[::-1])
    const = xv.flatten() + 1j * yv.flatten()
    return const / np.sqrt(np.mean(np.abs(const) ** 2))


def psk_constellation(m: int) -> np.ndarray:
    const = np.exp(1j * 2 * np.pi * np.arange(m) / m)
    return const / np.sqrt(np.mean(np.abs(const) ** 2))


def bits_to_symbols(bits: np.ndarray, kind: str, m: int):
    b = int(np.log2(m))
    blocks = bits.reshape(-1, b)
    ints = blocks.dot(1 << np.arange(b - 1, -1, -1))
    ints = np.array([int_to_gray(int(x)) for x in ints])
    const = qam_constellation(m) if kind == "qam" else psk_constellation(m)
    return const[ints], const, b


def symbols_to_bits(rx_symbols: np.ndarray, const: np.ndarray, b: int) -> np.ndarray:
    distances = np.abs(rx_symbols.reshape(-1, 1) - const.reshape(1, -1)) ** 2
    idx = np.argmin(distances, axis=1)
    ints = np.array([gray_to_int(int(x)) for x in idx])
    bits = ((ints[:, None] & (1 << np.arange(b - 1, -1, -1))) > 0).astype(int)
    return bits.reshape(-1)


def pulse_coeffs(name: str, alpha: float, sps: int) -> np.ndarray:
    if name == "nrz":
        pulse = np.ones(sps)
    else:
        span = 6
        t = np.arange(-span * sps, span * sps + 1) / sps
        pulse = np.zeros_like(t, dtype=float)
        for i, ti in enumerate(t):
            if ti == 0:
                pulse[i] = 1 - alpha + 4 * alpha / np.pi
            elif abs(abs(4 * alpha * ti) - 1) < 1e-12:
                pulse[i] = (
                    alpha
                    / np.sqrt(2)
                    * ((1 + 2 / np.pi) * np.sin(np.pi / (4 * alpha)) + (1 - 2 / np.pi) * np.cos(np.pi / (4 * alpha)))
                )
            else:
                num = np.sin(np.pi * ti * (1 - alpha)) + 4 * alpha * ti * np.cos(np.pi * ti * (1 + alpha))
                den = np.pi * ti * (1 - (4 * alpha * ti) ** 2)
                pulse[i] = num / den
    return pulse / np.sqrt(np.sum(pulse**2))


def simulate_link(kind: str, m: int, pulse_name: str, ebn0_db: float, num_symbols: int, rng, alpha: float, fc: float, sps: int):
    b = int(np.log2(m))
    bits_tx = rng.integers(0, 2, size=num_symbols * b)
    symbols_tx, const, b = bits_to_symbols(bits_tx, kind, m)

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


def theoretical_ber(kind: str, m: int, ebn0_db: float) -> float:
    ebn0_lin = 10 ** (ebn0_db / 10)
    b = np.log2(m)
    if kind == "qam":
        q = 0.5 * erfc(np.sqrt((3 * b / (m - 1)) * ebn0_lin) / np.sqrt(2))
        return (4 / b) * (1 - 1 / np.sqrt(m)) * q
    if m == 2:
        return 0.5 * erfc(np.sqrt(ebn0_lin))
    q = 0.5 * erfc(np.sqrt(2 * b * ebn0_lin) * np.sin(np.pi / m) / np.sqrt(2))
    return (2 / b) * q


def _prepare_output_dir(output_dir: Path | str) -> Path:
    path = Path(output_dir)
    path.mkdir(parents=True, exist_ok=True)
    return path


def _build_results(
    ebn0_db: list[int],
    kind_cases: list[tuple[str, int]],
    pulse_cases: list[str],
    num_bits_target: int,
    rng,
    alpha: float,
    fc: float,
    sps: int,
):
    results: dict[str, dict[tuple[str, int], dict[str, np.ndarray]]] = {}
    for pulse_name in pulse_cases:
        pulse_results: dict[tuple[str, int], dict[str, np.ndarray]] = {}
        for kind, m in kind_cases:
            b = int(np.log2(m))
            num_symbols = max(1, num_bits_target // b)
            ber_curve = []
            example_tx = None
            example_rx = None
            example_const = None

            for eb in ebn0_db:
                ber, symbols_tx, symbols_rx, const = simulate_link(kind, m, pulse_name, eb, num_symbols, rng, alpha, fc, sps)
                ber_curve.append(ber)
                if eb == ebn0_db[-1]:
                    example_tx = symbols_tx
                    example_rx = symbols_rx
                    example_const = const

            pulse_results[(kind, m)] = {
                "ber": np.array(ber_curve),
                "theory": np.array([theoretical_ber(kind, m, eb) for eb in ebn0_db]),
                "example_tx": example_tx,
                "example_rx": example_rx,
                "example_const": example_const,
            }
        results[pulse_name] = pulse_results
    return results


def _save_case_plot(output_dir: Path, ebn0_db: list[int], pulse_name: str, kind: str, m: int, data: dict[str, np.ndarray]) -> None:
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))

    sim_line = axes[0].semilogy(ebn0_db, data["ber"], marker="o", label=f"Simulada {kind.upper()} M={m}", linewidth=2)[0]
    axes[0].semilogy(
        ebn0_db,
        data["theory"],
        linestyle="--",
        linewidth=1,
        alpha=0.8,
        color=sim_line.get_color(),
        label="Teórica",
    )
    axes[0].set_xlabel(EBN0_LABEL)
    axes[0].set_ylabel("BER")
    axes[0].set_ylim(BER_YLIM)
    axes[0].grid(True, which="both", alpha=0.3)
    axes[0].legend(loc=LEGEND_LOC, fontsize=9)
    axes[0].set_title(f"BER: {kind.upper()} M={m} / {pulse_name.upper()}", fontsize=11, fontweight="bold")

    tx = data["example_tx"]
    rx = data["example_rx"]
    const = data["example_const"]
    if tx is not None and rx is not None and const is not None:
        axes[1].scatter(tx.real, tx.imag, s=20, label="TX", alpha=0.6, color="blue")
        axes[1].scatter(rx.real, rx.imag, s=20, label="RX", alpha=0.6, color="orange")
        axes[1].scatter(const.real, const.imag, s=150, marker="x", label="Ideal", linewidth=2, color="red")
        axes[1].axis("equal")
        axes[1].legend(fontsize=9)
    else:
        axes[1].text(0.5, 0.5, "No example constellation available", ha="center", va="center")
        axes[1].set_xticks([])
        axes[1].set_yticks([])

    axes[1].set_xlabel("I (componente em fase)")
    axes[1].set_ylabel("Q (componente em quadratura)")
    axes[1].grid(True, alpha=0.3)
    axes[1].set_title(f"Constelação (Eb/N0 = {ebn0_db[-1]} dB)")

    fig.tight_layout()
    fig.savefig(output_dir / f"BER_{pulse_name.upper()}_{kind.upper()}_M{m}.png", dpi=150)
    plt.close(fig)


def _save_aggregate_plot(output_dir: Path, ebn0_db: list[int], pulse_name: str, results: dict[tuple[str, int], dict[str, np.ndarray]]) -> None:
    fig, ax = plt.subplots(figsize=(9, 5))
    for (kind, m), data in results.items():
        sim_line = ax.semilogy(ebn0_db, data["ber"], marker="o", linewidth=1.5, label=f"SIM {kind.upper()} M={m}")[0]
        ax.semilogy(
            ebn0_db,
            data["theory"],
            linestyle="--",
            linewidth=1.2,
            alpha=0.85,
            color=sim_line.get_color(),
            label=f"TH {kind.upper()} M={m}",
        )
    ax.set_xlabel(EBN0_LABEL)
    ax.set_ylabel("BER")
    ax.set_ylim(BER_YLIM)
    ax.set_title(f"BER comparativa - pulso {pulse_name.upper()} (todas as modulações)")
    ax.grid(True, which="both", alpha=0.3)
    ax.legend(loc=LEGEND_LOC, fontsize=8)
    fig.tight_layout()
    fig.savefig(output_dir / f"BER_all_modulations_pulse_{pulse_name.upper()}.png", dpi=150)
    plt.close(fig)


def _save_average_by_pulse_plot(output_dir: Path, ebn0_db: list[int], kind: str, pulse_cases: list[str], results: dict[str, dict[tuple[str, int], dict[str, np.ndarray]]]) -> None:
    fig, ax = plt.subplots(figsize=(8, 5))
    for pulse_name in pulse_cases:
        avg_ber = np.zeros(len(ebn0_db), dtype=float)
        count = 0
        for (case_kind, _), data in results[pulse_name].items():
            if case_kind != kind:
                continue
            avg_ber += data["ber"]
            count += 1
        if count > 0:
            avg_ber /= count
            ax.semilogy(ebn0_db, avg_ber, marker="o", label=f"{kind.upper()} (avg over M) pulse={pulse_name.upper()}")
    ax.set_xlabel(EBN0_LABEL)
    ax.set_ylabel("BER")
    ax.set_ylim(BER_YLIM)
    ax.set_title(f"BER by pulse (averaged over Ms) - {kind.upper()}")
    ax.grid(True, which="both", alpha=0.3)
    ax.legend(loc=LEGEND_LOC, fontsize=8)
    fig.tight_layout()
    fig.savefig(output_dir / f"BER_by_pulse_avg_M_{kind.upper()}.png", dpi=150)
    plt.close(fig)


def main() -> None:
    fc = DEFAULT_FC
    sps = DEFAULT_SPS
    alpha = DEFAULT_ALPHA
    ebn0_db = DEFAULT_EBN0_DB
    num_bits_target = DEFAULT_NUM_BITS_TARGET
    rng = np.random.default_rng(DEFAULT_SEED)
    output_dir = _prepare_output_dir(DEFAULT_OUTPUT_DIR)

    print("Running simulations...")
    results = _build_results(ebn0_db, DEFAULT_KIND_CASES, DEFAULT_PULSE_CASES, num_bits_target, rng, alpha, fc, sps)

    print("\nGenerating and saving figures...")
    for pulse_name in DEFAULT_PULSE_CASES:
        for kind, m in DEFAULT_KIND_CASES:
            _save_case_plot(output_dir, ebn0_db, pulse_name, kind, m, results[pulse_name][(kind, m)])
        _save_aggregate_plot(output_dir, ebn0_db, pulse_name, results[pulse_name])

    for kind in ["psk", "qam"]:
        _save_average_by_pulse_plot(output_dir, ebn0_db, kind, DEFAULT_PULSE_CASES, results)

    print("All plots saved to", output_dir)


if __name__ == "__main__":
    main()
