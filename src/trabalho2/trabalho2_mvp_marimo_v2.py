import marimo

__generated_with = "0.23.0"
app = marimo.App(width="medium")


@app.cell
def imports_c01():
    import marimo as mo_c01
    import numpy as np_c01
    import matplotlib.pyplot as plt_c01
    from scipy.special import erfc as erfc_c01
    from pathlib import Path as Path_c01
    import math as math_c01

    return Path_c01, erfc_c01, math_c01, mo_c01, np_c01, plt_c01


@app.cell
def title_c02(mo_c01):
    mo_c01.md(r"""
    # Trabalho 2 - MVP em Marimo v2

    Simulacao de **BER para M-PSK/M-QAM em AWGN** com criterio adaptativo:
    acumular um numero minimo de erros por ponto de Eb/N0 e parar ao atingir um teto de bits.

    Esta versao implementa:
    - minimo de 100 erros por ponto;
    - teto de bits por ponto;
    - curvas teoricas no mesmo grafico;
    - cor identica para simulacao e teoria;
    - limpeza da pasta `output/trab2` antes de salvar as figuras.
    """)
    return


@app.cell
def controls_md_c02b(mo_c01):
    mo_c01.md(r"""
    ## Controles

    Ajuste o numero minimo de erros e o teto de bits por ponto.
    """)
    return


@app.cell(hide_code=True)
def ui_sliders_c03(mo_c01):
    min_errors_slider_c03 = mo_c01.ui.number(
        value=100,
        start=10,
        stop=1000,
        step=10,
        label="Minimo de erros por ponto",
    )

    max_bits_slider_c03 = mo_c01.ui.number(
        value=2_000_000,
        start=100_000,
        stop=20_000_000,
        step=100_000,
        label="Teto de bits por ponto",
    )

    seed_slider_c03 = mo_c01.ui.number(
        value=42,
        start=0,
        stop=1000,
        step=1,
        label="Seed do RNG",
    )

    mo_c01.vstack([
        min_errors_slider_c03,
        max_bits_slider_c03,
        seed_slider_c03,
    ])
    return max_bits_slider_c03, min_errors_slider_c03, seed_slider_c03


@app.cell
def params_fixed_c04():
    fc_c04 = 10.0
    sps_c04 = 16
    ebn0_db_c04 = [0, 4, 8, 12, 16, 20, 24]
    kind_cases_c04 = [
        ("psk", 2),
        ("psk", 4),
        ("psk", 8),
        ("psk", 16),
        ("qam", 4),
        ("qam", 16),
        ("qam", 64),
    ]
    pulse_cases_c04 = ["nrz", "rrc"]
    alpha_c04 = 0.15
    return (
        alpha_c04,
        ebn0_db_c04,
        fc_c04,
        kind_cases_c04,
        pulse_cases_c04,
        sps_c04,
    )


@app.cell
def rf01_rng_init_c05(np_c01, seed_slider_c03):
    rng_c05 = np_c01.random.default_rng(int(seed_slider_c03.value))
    return (rng_c05,)


@app.cell
def gray_coding_c06():
    def int_to_gray_c06(n_c06):
        return n_c06 ^ (n_c06 >> 1)

    def gray_to_int_c06(g_c06):
        n_c06 = 0
        while g_c06:
            n_c06 ^= g_c06
            g_c06 >>= 1
        return n_c06

    return gray_to_int_c06, int_to_gray_c06


@app.cell
def rf03_rf04_constellation_c07(np_c01):
    def qam_constellation_c07(M_c07):
        m_c07 = int(np_c01.sqrt(M_c07))
        levels_c07 = np_c01.arange(-(m_c07 - 1), m_c07, 2)
        xv_c07, yv_c07 = np_c01.meshgrid(levels_c07, levels_c07[::-1])
        const_c07 = xv_c07.flatten() + 1j * yv_c07.flatten()
        return const_c07 / np_c01.sqrt(np_c01.mean(np_c01.abs(const_c07) ** 2))

    def psk_constellation_c07(M_c07):
        const_c07 = np_c01.exp(1j * 2 * np_c01.pi * np_c01.arange(M_c07) / M_c07)
        return const_c07 / np_c01.sqrt(np_c01.mean(np_c01.abs(const_c07) ** 2))

    def bits_to_symbols_c07(bits_c07, kind_c07, M_c07, int_to_gray_c06):
        b_c07 = int(np_c01.log2(M_c07))
        blocks_c07 = bits_c07.reshape(-1, b_c07)
        ints_c07 = blocks_c07.dot(1 << np_c01.arange(b_c07 - 1, -1, -1))
        ints_c07 = np_c01.array([int_to_gray_c06(int(x)) for x in ints_c07])
        const_c07 = qam_constellation_c07(M_c07) if kind_c07 == "qam" else psk_constellation_c07(M_c07)
        return const_c07[ints_c07], const_c07, b_c07

    def symbols_to_bits_c07(rx_symbols_c07, const_c07, b_c07, gray_to_int_c06, np_c01):
        d_c07 = np_c01.abs(rx_symbols_c07.reshape(-1, 1) - const_c07.reshape(1, -1)) ** 2
        idx_c07 = np_c01.argmin(d_c07, axis=1)
        ints_c07 = np_c01.array([gray_to_int_c06(int(x)) for x in idx_c07])
        bits_c07 = ((ints_c07[:, None] & (1 << np_c01.arange(b_c07 - 1, -1, -1))) > 0).astype(int)
        return bits_c07.reshape(-1)

    return bits_to_symbols_c07, psk_constellation_c07, qam_constellation_c07, symbols_to_bits_c07


@app.cell
def rf07_pulse_shaping_c09(np_c01):
    def pulse_coeffs_c09(name_c09, alpha_c09, sps_c09):
        if name_c09 == "nrz":
            p_c09 = np_c01.ones(sps_c09)
        else:
            span_c09 = 6
            t_c09 = np_c01.arange(-span_c09 * sps_c09, span_c09 * sps_c09 + 1) / sps_c09
            p_c09 = np_c01.zeros_like(t_c09, dtype=float)
            for i_c09, ti_c09 in enumerate(t_c09):
                if ti_c09 == 0:
                    p_c09[i_c09] = 1 - alpha_c09 + 4 * alpha_c09 / np_c01.pi
                elif abs(abs(4 * alpha_c09 * ti_c09) - 1) < 1e-12:
                    p_c09[i_c09] = (
                        alpha_c09
                        / np_c01.sqrt(2)
                        * (
                            (1 + 2 / np_c01.pi) * np_c01.sin(np_c01.pi / (4 * alpha_c09))
                            + (1 - 2 / np_c01.pi) * np_c01.cos(np_c01.pi / (4 * alpha_c09))
                        )
                    )
                else:
                    num_c09 = np_c01.sin(np_c01.pi * ti_c09 * (1 - alpha_c09)) + 4 * alpha_c09 * ti_c09 * np_c01.cos(
                        np_c01.pi * ti_c09 * (1 + alpha_c09)
                    )
                    den_c09 = np_c01.pi * ti_c09 * (1 - (4 * alpha_c09 * ti_c09) ** 2)
                    p_c09[i_c09] = num_c09 / den_c09
        return p_c09 / np_c01.sqrt(np_c01.sum(p_c09**2))

    return (pulse_coeffs_c09,)


@app.cell
def rf15_theoretical_ber_c10(erfc_c01, np_c01):
    def theoretical_ber_c10(kind_c10, M_c10, ebn0_c10):
        ebn0_lin_c10 = 10 ** (ebn0_c10 / 10)
        b_c10 = np_c01.log2(M_c10)
        if kind_c10 == "qam":
            q_c10 = 0.5 * erfc_c01(np_c01.sqrt((3 * b_c10 / (M_c10 - 1)) * ebn0_lin_c10) / np_c01.sqrt(2))
            return (4 / b_c10) * (1 - 1 / np_c01.sqrt(M_c10)) * q_c10
        if M_c10 == 2:
            return 0.5 * erfc_c01(np_c01.sqrt(ebn0_lin_c10))
        q_c10 = 0.5 * erfc_c01(np_c01.sqrt(2 * b_c10 * ebn0_lin_c10) * np_c01.sin(np_c01.pi / M_c10) / np_c01.sqrt(2))
        return (2 / b_c10) * q_c10

    return (theoretical_ber_c10,)


@app.cell
def rf08_rf09_rf10_rf11_rf12_link_sim_c11(
    bits_to_symbols_c07,
    int_to_gray_c06,
    gray_to_int_c06,
    np_c01,
    pulse_coeffs_c09,
    rng_c05,
    sps_c04,
):
    def simulate_link_stats_c11(
        kind_c11,
        M_c11,
        pulse_name_c11,
        ebn0_db_c11,
        min_errors_c11,
        max_bits_c11,
        fc_c11,
        alpha_c11,
    ):
        b_c11 = int(np_c01.log2(M_c11))
        pulse_c11 = pulse_coeffs_c09(pulse_name_c11, alpha_c11, sps_c04)
        max_symbols_c11 = max(1, max_bits_c11 // b_c11)
        chunk_symbols_c11 = min(50000, max_symbols_c11)
        total_bits_c11 = 0
        total_errors_c11 = 0
        last_symbols_tx_c11 = None
        last_symbols_rx_c11 = None
        last_const_c11 = None
        stop_reason_c11 = "cap"

        while total_errors_c11 < min_errors_c11 and total_bits_c11 < max_bits_c11:
            remaining_symbols_c11 = max_symbols_c11 - (total_bits_c11 // b_c11)
            if remaining_symbols_c11 <= 0:
                break
            current_symbols_c11 = min(chunk_symbols_c11, remaining_symbols_c11)
            bits_tx_c11 = rng_c05.integers(0, 2, size=current_symbols_c11 * b_c11)
            symbols_tx_c11, const_c11, _ = bits_to_symbols_c07(bits_tx_c11, kind_c11, M_c11, int_to_gray_c06)
            upsampled_c11 = np_c01.zeros(len(symbols_tx_c11) * sps_c04, dtype=complex)
            upsampled_c11[::sps_c04] = symbols_tx_c11
            shaped_c11 = np_c01.convolve(upsampled_c11, pulse_c11, mode="full")

            fs_c11 = fc_c11 * sps_c04
            t_c11 = np_c01.arange(len(shaped_c11)) / fs_c11
            carrier_c11 = 2 * np_c01.pi * fc_c11 * t_c11
            tx_c11 = np_c01.sqrt(2) * (shaped_c11.real * np_c01.cos(carrier_c11) - shaped_c11.imag * np_c01.sin(carrier_c11))

            ebn0_lin_c11 = 10 ** (ebn0_db_c11 / 10)
            sigma_c11 = np_c01.sqrt(1 / (2 * b_c11 * ebn0_lin_c11))
            rx_c11 = tx_c11 + sigma_c11 * rng_c05.standard_normal(tx_c11.size)

            i_c11 = np_c01.sqrt(2) * rx_c11 * np_c01.cos(carrier_c11)
            q_c11 = -np_c01.sqrt(2) * rx_c11 * np_c01.sin(carrier_c11)
            bb_rx_c11 = i_c11 + 1j * q_c11

            mf_c11 = pulse_c11[::-1].conj()
            filtered_c11 = np_c01.convolve(bb_rx_c11, mf_c11, mode="full")
            offset_c11 = len(pulse_c11) - 1
            sample_idx_c11 = offset_c11 + np_c01.arange(len(symbols_tx_c11)) * sps_c04
            symbols_rx_c11 = filtered_c11[sample_idx_c11]

            bits_rx_c11 = symbols_to_bits_c07(symbols_rx_c11, const_c11, b_c11, gray_to_int_c06, np_c01)
            errors_c11 = int(np_c01.count_nonzero(bits_tx_c11 != bits_rx_c11))

            total_errors_c11 += errors_c11
            total_bits_c11 += bits_tx_c11.size
            last_symbols_tx_c11 = symbols_tx_c11
            last_symbols_rx_c11 = symbols_rx_c11
            last_const_c11 = const_c11

        if total_errors_c11 >= min_errors_c11:
            stop_reason_c11 = f"{min_errors_c11} erros"
        elif total_bits_c11 >= max_bits_c11:
            stop_reason_c11 = "cap de bits"

        ber_c11 = total_errors_c11 / total_bits_c11 if total_bits_c11 else 0.0
        return {
            "ber": ber_c11,
            "errors": total_errors_c11,
            "bits": total_bits_c11,
            "stop_reason": stop_reason_c11,
            "symbols_tx": last_symbols_tx_c11,
            "symbols_rx": last_symbols_rx_c11,
            "const": last_const_c11,
            "min_errors": min_errors_c11,
            "max_bits": max_bits_c11,
        }

    return (simulate_link_stats_c11,)


@app.cell
def results_c12(
    ebn0_db_c04,
    alpha_c04,
    fc_c04,
    kind_cases_c04,
    min_errors_slider_c03,
    np_c01,
    max_bits_slider_c03,
    pulse_cases_c04,
    simulate_link_stats_c11,
    theoretical_ber_c10,
):
    results_c12 = {}
    example_tx_c12 = None
    example_rx_c12 = None
    example_const_c12 = None

    min_errors_c12 = int(min_errors_slider_c03.value)
    max_bits_c12 = int(max_bits_slider_c03.value)

    for pulse_name_c12 in pulse_cases_c04:
        results_c12[pulse_name_c12] = {}
        for kind_c12, M_c12 in kind_cases_c04:
            ber_curve_c12 = []
            errors_curve_c12 = []
            bits_curve_c12 = []
            for eb_c12 in ebn0_db_c04:
                stats_c12 = simulate_link_stats_c11(
                    kind_c12,
                    M_c12,
                    pulse_name_c12,
                    eb_c12,
                    min_errors_c12,
                    max_bits_c12,
                    fc_c04,
                    alpha_c04,
                )
                ber_curve_c12.append(stats_c12["ber"])
                errors_curve_c12.append(stats_c12["errors"])
                bits_curve_c12.append(stats_c12["bits"])
                results_c12[pulse_name_c12].setdefault((kind_c12, M_c12), {})
                results_c12[pulse_name_c12][(kind_c12, M_c12)][f"stop_{eb_c12}"] = stats_c12["stop_reason"]
                if eb_c12 == ebn0_db_c04[-1]:
                    example_tx_c12 = stats_c12["symbols_tx"]
                    example_rx_c12 = stats_c12["symbols_rx"]
                    example_const_c12 = stats_c12["const"]
            b_c12 = int(np_c01.log2(M_c12))
            num_bits_actual_c12 = max(1, max_bits_c12 // b_c12) * b_c12
            results_c12[pulse_name_c12][(kind_c12, M_c12)] = {
                "ber": np_c01.array(ber_curve_c12),
                "errors": np_c01.array(errors_curve_c12),
                "bits": np_c01.array(bits_curve_c12),
                "theory": np_c01.array([theoretical_ber_c10(kind_c12, M_c12, eb_c12) for eb_c12 in ebn0_db_c04]),
                "num_bits_actual": num_bits_actual_c12,
                "stop_reasons": [results_c12[pulse_name_c12][(kind_c12, M_c12)].get(f"stop_{eb_c12}") for eb_c12 in ebn0_db_c04],
                "example_tx": example_tx_c12,
                "example_rx": example_rx_c12,
                "example_const": example_const_c12,
            }
    return (results_c12,)


@app.cell
def output_dir_c13(Path_c01):
    output_dir_c13 = Path_c01("output/trab2")
    output_dir_c13.mkdir(parents=True, exist_ok=True)
    for png_c13 in output_dir_c13.glob("*.png"):
        try:
            png_c13.unlink()
        except Exception:
            pass
    return (output_dir_c13,)


@app.cell
def plots_final_c13(
    ebn0_db_c04,
    kind_cases_c04,
    plt_c01,
    pulse_cases_c04,
    output_dir_c13,
    results_c12,
):
    for pulse_name_c13 in pulse_cases_c04:
        for kind_c13, M_c13 in kind_cases_c04:
            data = results_c12.get(pulse_name_c13, {}).get((kind_c13, M_c13), None)
            if data is None:
                continue
            fig, axes = plt_c01.subplots(1, 2, figsize=(12, 5))

            sim_line = axes[0].semilogy(
                ebn0_db_c04,
                data["ber"],
                marker="o",
                label=f"Simulada {kind_c13.upper()} M={M_c13}",
                linewidth=2,
            )[0]
            axes[0].semilogy(
                ebn0_db_c04,
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
            stop_summary_c13 = ", ".join(data.get("stop_reasons", []))
            axes[0].set_title(
                f"BER: {kind_c13.upper()} M={M_c13} / {pulse_name_c13.upper()} | {stop_summary_c13}",
                fontsize=11,
                fontweight="bold",
            )

            tx = data.get("example_tx")
            rx = data.get("example_rx")
            const = data.get("example_const")
            if tx is None or rx is None or const is None:
                axes[1].text(0.5, 0.5, "No example constellation available", ha="center", va="center")
                axes[1].set_xticks([])
                axes[1].set_yticks([])
            else:
                axes[1].scatter(tx.real, tx.imag, s=20, label="TX", alpha=0.6, color="blue")
                axes[1].scatter(rx.real, rx.imag, s=20, label="RX", alpha=0.6, color="orange")
                axes[1].scatter(const.real, const.imag, s=150, marker="x", label="Ideal", linewidth=2, color="red")
                axes[1].set_xlabel("I (componente em fase)", fontsize=12)
                axes[1].set_ylabel("Q (componente em quadratura)", fontsize=12)
                axes[1].grid(True, alpha=0.3)
                axes[1].legend(fontsize=9)
                axes[1].set_title(f"Constelação (Eb/N0 = {ebn0_db_c04[-1]} dB)")
                axes[1].axis("equal")

            plt_c01.tight_layout()
            fig_path_c13 = output_dir_c13 / f"BER_{pulse_name_c13.upper()}_{kind_c13.upper()}_M{M_c13}.png"
            fig.savefig(fig_path_c13, dpi=150)
            plt_c01.show()
    return


@app.cell
def plots_aggregate_by_pulse_c14(
    ebn0_db_c04,
    kind_cases_c04,
    plt_c01,
    output_dir_c13,
    pulse_cases_c04,
    results_c12,
):
    for pulse_name_c14 in pulse_cases_c04:
        fig_c14, ax_c14 = plt_c01.subplots(1, 1, figsize=(9, 5))
        for kind_c14, M_c14 in kind_cases_c04:
            data_c14 = results_c12.get(pulse_name_c14, {}).get((kind_c14, M_c14), None)
            if data_c14 is None:
                continue
            sim_line_c14 = ax_c14.semilogy(
                ebn0_db_c04,
                data_c14["ber"],
                marker="o",
                linewidth=1.5,
                label=f"SIM {kind_c14.upper()} M={M_c14}",
            )[0]
            ax_c14.semilogy(
                ebn0_db_c04,
                data_c14["theory"],
                linestyle="--",
                linewidth=1.2,
                alpha=0.85,
                color=sim_line_c14.get_color(),
                label=f"TH {kind_c14.upper()} M={M_c14}",
            )
        ax_c14.set_xlabel("Eb/N0 (dB)")
        ax_c14.set_ylabel("BER")
        ax_c14.set_ylim([1e-5, 1])
        ax_c14.set_title(f"BER comparativa - pulso {pulse_name_c14.upper()} (todas as modulações, status: 100 erros ou cap)")
        ax_c14.grid(True, which="both", alpha=0.3)
        ax_c14.legend(fontsize=8)
        plt_c01.tight_layout()
        fig_c14.savefig(output_dir_c13 / f"BER_all_modulations_pulse_{pulse_name_c14.upper()}.png", dpi=150)
        plt_c01.show()
    return


if __name__ == "__main__":
    app.run()
