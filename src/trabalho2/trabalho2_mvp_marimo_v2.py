import marimo

__generated_with = "0.23.0"
app = marimo.App(width="medium")


@app.cell
def imports_c01():
    import marimo as mo
    import matplotlib.pyplot as plt
    import math
    import numpy as np
    from pathlib import Path as path
    from scipy.special import erfc

    return math, mo, np, path, plt, erfc


@app.cell
def title_c02(mo):
    mo.md(r"""
    # Trabalho 2 - MVP em Marimo v2

    Simulacao de BER em banda passante sob AWGN com criterio adaptativo.

    Esta versao gera e salva figuras em `output/trab2`.
    """)
    return ()


@app.cell
def controls_md_c02b(mo):
    mo.md(r"""
    ## Controles

    Ajuste o minimo de erros por ponto, o teto de bits e a seed.
    """)
    return ()


@app.cell(hide_code=True)
def ui_sliders_c03(mo):
    min_errors_slider = mo.ui.number(value=100, start=10, stop=1000, step=10, label="Minimo de erros por ponto")
    max_bits_slider = mo.ui.number(value=2_000_000, start=100_000, stop=20_000_000, step=100_000, label="Teto de bits por ponto")
    seed_slider = mo.ui.number(value=42, start=0, stop=1000, step=1, label="Seed do RNG")
    mo.vstack([min_errors_slider, max_bits_slider, seed_slider])
    return min_errors_slider, max_bits_slider, seed_slider


@app.cell
def params_fixed_c04():
    fc = 10.0
    sps = 16
    alpha = 0.15
    ebn0_db = [0, 4, 8, 12, 16, 20, 24]
    kind_cases = [("psk", 2), ("psk", 4), ("psk", 8), ("psk", 16), ("qam", 4), ("qam", 16), ("qam", 64)]
    pulse_cases = ["nrz", "rrc"]
    return alpha, ebn0_db, fc, kind_cases, pulse_cases, sps


@app.cell
def rng_c05(np, seed_slider):
    rng = np.random.default_rng(int(seed_slider.value))
    return (rng,)


@app.cell
def gray_coding_c06():
    def int_to_gray(n):
        return n ^ (n >> 1)

    def gray_to_int(g):
        n = 0
        while g:
            n ^= g
            g >>= 1
        return n

    return gray_to_int, int_to_gray


@app.cell
def constellation_helpers_c07(np):
    def qam_constellation(m):
        side = int(np.sqrt(m))
        levels = np.arange(-(side - 1), side, 2)
        xv, yv = np.meshgrid(levels, levels[::-1])
        const = xv.flatten() + 1j * yv.flatten()
        return const / np.sqrt(np.mean(np.abs(const) ** 2))

    def psk_constellation(m):
        const = np.exp(1j * 2 * np.pi * np.arange(m) / m)
        return const / np.sqrt(np.mean(np.abs(const) ** 2))

    def bits_to_symbols(bits, kind, m, int_to_gray):
        b = int(np.log2(m))
        blocks = bits.reshape(-1, b)
        ints = blocks.dot(1 << np.arange(b - 1, -1, -1))
        ints = np.array([int_to_gray(int(x)) for x in ints])
        const = qam_constellation(m) if kind == "qam" else psk_constellation(m)
        return const[ints], const, b

    def symbols_to_bits(symbols, const, b, gray_to_int):
        distances = np.abs(symbols.reshape(-1, 1) - const.reshape(1, -1)) ** 2
        idx = np.argmin(distances, axis=1)
        ints = np.array([gray_to_int(int(x)) for x in idx])
        bits = ((ints[:, None] & (1 << np.arange(b - 1, -1, -1))) > 0).astype(int)
        return bits.reshape(-1)

    return (bits_to_symbols, psk_constellation, qam_constellation, symbols_to_bits,)


@app.cell
def pulse_shapes_c09(np):
    def pulse_coeffs(name, alpha, sps):
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
                    pulse[i] = alpha / np.sqrt(2) * ((1 + 2 / np.pi) * np.sin(np.pi / (4 * alpha)) + (1 - 2 / np.pi) * np.cos(np.pi / (4 * alpha)))
                else:
                    num = np.sin(np.pi * ti * (1 - alpha)) + 4 * alpha * ti * np.cos(np.pi * ti * (1 + alpha))
                    den = np.pi * ti * (1 - (4 * alpha * ti) ** 2)
                    pulse[i] = num / den
        return pulse / np.sqrt(np.sum(pulse ** 2))

    return (pulse_coeffs,)


@app.cell
def theoretical_ber_c10(erfc, np):
    def theoretical_ber(kind, m, ebn0_db):
        ebn0_lin = 10 ** (ebn0_db / 10)
        b = np.log2(m)
        if kind == "qam":
            q = 0.5 * erfc(np.sqrt((3 * b / (m - 1)) * ebn0_lin) / np.sqrt(2))
            return (4 / b) * (1 - 1 / np.sqrt(m)) * q
        if m == 2:
            return 0.5 * erfc(np.sqrt(ebn0_lin))
        q = 0.5 * erfc(np.sqrt(2 * b * ebn0_lin) * np.sin(np.pi / m) / np.sqrt(2))
        return (2 / b) * q

    return (theoretical_ber,)


@app.cell
def link_simulation_c11(bits_to_symbols, symbols_to_bits, int_to_gray, gray_to_int, np, pulse_coeffs, rng, sps):
    def simulate_link_stats(kind, m, pulse_name, ebn0_db, min_errors, max_bits, fc, alpha, sps, rng_param):
        b = int(np.log2(m))
        pulse = pulse_coeffs(pulse_name, alpha, sps)
        max_symbols = max(1, max_bits // b)
        chunk_symbols = min(50_000, max_symbols)

        total_bits = 0
        total_errors = 0
        last_symbols_tx = None
        last_symbols_rx = None
        last_const = None

        while total_errors < min_errors and total_bits < max_bits:
            remaining_symbols = max_symbols - (total_bits // b)
            if remaining_symbols <= 0:
                break

            current_symbols = min(chunk_symbols, remaining_symbols)
            bits_tx = rng_param.integers(0, 2, size=current_symbols * b)
            symbols_tx, const, _ = bits_to_symbols(bits_tx, kind, m, int_to_gray)

            upsampled = np.zeros(len(symbols_tx) * sps, dtype=complex)
            upsampled[::sps] = symbols_tx
            shaped = np.convolve(upsampled, pulse, mode="full")

            fs = fc * sps
            t = np.arange(len(shaped)) / fs
            carrier = 2 * np.pi * fc * t
            tx = np.sqrt(2) * (shaped.real * np.cos(carrier) - shaped.imag * np.sin(carrier))

            ebn0_lin = 10 ** (ebn0_db / 10)
            sigma = np.sqrt(1 / (2 * b * ebn0_lin))
            rx = tx + sigma * rng_param.standard_normal(tx.size)

            i = np.sqrt(2) * rx * np.cos(carrier)
            q = -np.sqrt(2) * rx * np.sin(carrier)
            bb_rx = i + 1j * q

            mf = pulse[::-1].conj()
            filtered = np.convolve(bb_rx, mf, mode="full")
            offset = len(pulse) - 1
            sample_idx = offset + np.arange(len(symbols_tx)) * sps
            symbols_rx = filtered[sample_idx]

            bits_rx = symbols_to_bits(symbols_rx, const, b, gray_to_int)
            errors = int(np.count_nonzero(bits_tx != bits_rx))

            total_errors += errors
            total_bits += bits_tx.size
            last_symbols_tx = symbols_tx
            last_symbols_rx = symbols_rx
            last_const = const

        stop_reason = "cap de bits" if total_bits >= max_bits else f"{min_errors} erros"
        ber = total_errors / total_bits if total_bits else 0.0
        return {
            "ber": ber,
            "errors": total_errors,
            "bits": total_bits,
            "stop_reason": stop_reason,
            "symbols_tx": last_symbols_tx,
            "symbols_rx": last_symbols_rx,
            "const": last_const,
        }

    return (simulate_link_stats,)


@app.cell
def output_dir_c12(path):
    output_dir = path("output/trab2")
    output_dir.mkdir(parents=True, exist_ok=True)
    for png in output_dir.glob("*.png"):
        try:
            png.unlink()
        except Exception:
            pass
    return (output_dir,)


@app.cell
def results_c13(ebn0_db, alpha, fc, kind_cases, max_bits_slider, min_errors_slider, np, output_dir, pulse_cases, simulate_link_stats, theoretical_ber, sps, rng):
    results = {}
    min_errors = int(min_errors_slider.value)
    max_bits = int(max_bits_slider.value)

    for pulse_name in pulse_cases:
        pulse_results = {}
        for kind, m in kind_cases:
            ber_curve = []
            errors_curve = []
            bits_curve = []
            stop_reasons = []
            example_tx = example_rx = example_const = None

            for eb in ebn0_db:
                stats = simulate_link_stats(kind, m, pulse_name, eb, min_errors, max_bits, fc, alpha, sps, rng)
                ber_curve.append(stats["ber"])
                errors_curve.append(stats["errors"])
                bits_curve.append(stats["bits"])
                stop_reasons.append(stats["stop_reason"])
                if eb == ebn0_db[-1]:
                    example_tx = stats["symbols_tx"]
                    example_rx = stats["symbols_rx"]
                    example_const = stats["const"]

            pulse_results[(kind, m)] = {
                "ber": np.array(ber_curve),
                "errors": np.array(errors_curve),
                "bits": np.array(bits_curve),
                "theory": np.array([theoretical_ber(kind, m, eb) for eb in ebn0_db]),
                "stop_reasons": stop_reasons,
                "example_tx": example_tx,
                "example_rx": example_rx,
                "example_const": example_const,
            }
        results[pulse_name] = pulse_results

    return (results,)


@app.cell
def plot_case_c14(ebn0_db, kind_cases, output_dir, plt, pulse_cases, results):
    xlabel_c14 = "Eb/N0 (dB)"
    legend_loc_c14 = "upper right"
    ylim_c14 = (1e-5, 1)

    for pulse_name_c14 in pulse_cases:
        for kind_c14, m_c14 in kind_cases:
            data_c14 = results[pulse_name_c14][(kind_c14, m_c14)]
            fig_c14, axes_c14 = plt.subplots(1, 2, figsize=(12, 5))

            sim_line_c14 = axes_c14[0].semilogy(ebn0_db, data_c14["ber"], marker="o", linewidth=2, label=f"Simulada {kind_c14.upper()} M={m_c14}")[0]
            axes_c14[0].semilogy(ebn0_db, data_c14["theory"], linestyle="--", linewidth=1, alpha=0.8, color=sim_line_c14.get_color(), label="Teórica")
            axes_c14[0].set_xlabel(xlabel_c14)
            axes_c14[0].set_ylabel("BER")
            axes_c14[0].set_ylim(ylim_c14)
            axes_c14[0].grid(True, which="both", alpha=0.3)
            axes_c14[0].legend(loc=legend_loc_c14, fontsize=9)
            axes_c14[0].set_title(f"BER: {kind_c14.upper()} M={m_c14} / {pulse_name_c14.upper()} | {', '.join(data_c14['stop_reasons'])}", fontsize=11, fontweight="bold")

            tx_c14 = data_c14["example_tx"]
            rx_c14 = data_c14["example_rx"]
            const_c14 = data_c14["example_const"]
            if tx_c14 is not None and rx_c14 is not None and const_c14 is not None:
                axes_c14[1].scatter(tx_c14.real, tx_c14.imag, s=20, label="TX", alpha=0.6, color="blue")
                axes_c14[1].scatter(rx_c14.real, rx_c14.imag, s=20, label="RX", alpha=0.6, color="orange")
                axes_c14[1].scatter(const_c14.real, const_c14.imag, s=150, marker="x", label="Ideal", linewidth=2, color="red")
                axes_c14[1].axis("equal")
                axes_c14[1].legend(fontsize=9)
            else:
                axes_c14[1].text(0.5, 0.5, "No example constellation available", ha="center", va="center")
                axes_c14[1].set_xticks([])
                axes_c14[1].set_yticks([])

            axes_c14[1].set_xlabel("I (componente em fase)")
            axes_c14[1].set_ylabel("Q (componente em quadratura)")
            axes_c14[1].grid(True, alpha=0.3)
            axes_c14[1].set_title(f"Constelação (Eb/N0 = {ebn0_db[-1]} dB)")

            fig_c14.tight_layout()
            fig_c14.savefig(output_dir / f"BER_{pulse_name_c14.upper()}_{kind_c14.upper()}_M{m_c14}.png", dpi=150)
            plt.show()


@app.cell
def plot_aggregate_c15(ebn0_db, kind_cases, output_dir, plt, pulse_cases, results):
    xlabel_c15 = "Eb/N0 (dB)"
    legend_loc_c15 = "upper right"
    ylim_c15 = (1e-5, 1)

    for pulse_name_c15 in pulse_cases:
        fig_c15, ax_c15 = plt.subplots(figsize=(9, 5))
        for kind_c15, m_c15 in kind_cases:
            data_c15 = results[pulse_name_c15][(kind_c15, m_c15)]
            sim_line_c15 = ax_c15.semilogy(ebn0_db, data_c15["ber"], marker="o", linewidth=1.5, label=f"SIM {kind_c15.upper()} M={m_c15}")[0]
            ax_c15.semilogy(ebn0_db, data_c15["theory"], linestyle="--", linewidth=1.2, alpha=0.85, color=sim_line_c15.get_color(), label=f"TH {kind_c15.upper()} M={m_c15}")
        ax_c15.set_xlabel(xlabel_c15)
        ax_c15.set_ylabel("BER")
        ax_c15.set_ylim(ylim_c15)
        ax_c15.set_title(f"BER comparativa - pulso {pulse_name_c15.upper()} (todas as modulações)")
        ax_c15.grid(True, which="both", alpha=0.3)
        ax_c15.legend(loc=legend_loc_c15, fontsize=8)
        fig_c15.tight_layout()
        fig_c15.savefig(output_dir / f"BER_all_modulations_pulse_{pulse_name_c15.upper()}.png", dpi=150)
        plt.show()
    return ()


if __name__ == "__main__":
    app.run()
