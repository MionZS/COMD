import marimo

__generated_with = "0.23.0"
app = marimo.App(width="medium")


@app.cell
def imports_c01():
    import marimo as mo_c01
    import numpy as np_c01
    import matplotlib.pyplot as plt_c01
    from scipy.special import erfc as erfc_c01

    return erfc_c01, mo_c01, np_c01, plt_c01


@app.cell
def title_c02(mo_c01):
    mo_c01.md(r"""
    # Trabalho 2 - MVP em Marimo

    Simulação de **BER para M-PSK/M-QAM em AWGN** conforme PRD e Proposta TC2.

    Cada célula implementa requisitos específicos do PRD (RF##). Use os sliders abaixo para ajustar parâmetros.
    """)
    return ()


@app.cell
def controls_md_c02b(mo_c01):
    mo_c01.md("""
    ## ⚙️ Controles da Simulação

    Ajuste os controles abaixo para configurar a simulação:
    """)
    return ()


@app.cell(hide_code=True)
def ui_sliders_c03(mo_c01):
    """Controles interativos para a simulação (RF01, RF07)."""
    num_bits_target_slider_c03 = mo_c01.ui.number(
        value=2_000_000,
        start=100000,
        stop=10000000,
        step=100000,
        label="📊 Número de bits alvo (RF01)",
    )

    seed_slider_c03 = mo_c01.ui.number(
        value=42,
        start=0,
        stop=1000,
        step=1,
        label="🌱 Seed do RNG",
    )
    mo_c01.vstack([
        num_bits_target_slider_c03,
        seed_slider_c03,
    ])
    return num_bits_target_slider_c03, seed_slider_c03


@app.cell
def params_fixed_c04():
    """
    Parâmetros fixos conforme Proposta TC2.
    """
    fc_c04 = 10.0          # RF08: Frequência portadora
    sps_c04 = 16           # RF12: Amostras por símbolo (match Lab 2: Ns=16, fs=40)
    ebn0_db_c04 = [0, 4, 8, 12, 16, 20, 24]  # RF12: Pontos de simulação (0..24, passo 4)
    # PSK: b = 1..4 bits → M = 2,4,8,16
    # QAM: b = 2,4,6 bits → M = 4,16,64
    kind_cases_c04 = [
        ("psk", 2),
        ("psk", 4),
        ("psk", 8),
        ("psk", 16),
        ("qam", 4),
        ("qam", 16),
        ("qam", 64),
    ]  # RF03, RF04
    pulse_cases_c04 = ["nrz", "rrc"]  # RF07
    alpha_c04 = 0.15  # fixo conforme Proposta 5.4
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
    """
    RF01: Gerador de números aleatórios para sequência pseudoaleatória.
    """
    rng_c05 = np_c01.random.default_rng(int(seed_slider_c03.value))
    return (rng_c05,)


@app.cell
def gray_coding_c06():
    """
    **Codificação Gray (Requisito de Proposta 5.5)**

    Converte índices entre inteiros e Gray code.
    Essencial para fórmulas teóricas de BER (RF15) que assumem símbolos adjacentes 
    diferem por apenas 1 bit.
    """
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
    """
    **RF03 (M-PSK) e RF04 (M-QAM): Construir constelações**
    **RF05: Normalização de energia média = 1**

    Ambas as constelações são normalizadas para média de potência = 1 bit/símbolo.
    """
    def qam_constellation_c07(m_c07):
        m_c07 = int(np_c01.sqrt(m_c07))
        levels_c07 = np_c01.arange(-(m_c07 - 1), m_c07, 2)
        xv_c07, yv_c07 = np_c01.meshgrid(levels_c07, levels_c07[::-1])
        const_c07 = xv_c07.flatten() + 1j * yv_c07.flatten()
        return const_c07 / np_c01.sqrt(np_c01.mean(np_c01.abs(const_c07) ** 2))

    def psk_constellation_c07(m_c07):
        const_c07 = np_c01.exp(1j * 2 * np_c01.pi * np_c01.arange(m_c07) / m_c07)
        return const_c07 / np_c01.sqrt(np_c01.mean(np_c01.abs(const_c07) ** 2))

    return psk_constellation_c07, qam_constellation_c07


@app.cell
def rf02_symbol_mapping_c08(
    gray_to_int_c06,
    int_to_gray_c06,
    np_c01,
    psk_constellation_c07,
    qam_constellation_c07,
):
    """
    **RF02: Agrupamento de bits em blocos de tamanho b = log₂(M)**

    Mapeia bits → índices → Gray code → símbolos da constelação.
    Usa Gray mapping para alinhamento com fórmulas teóricas (Proposta 5.5).
    """
    def bits_to_symbols_c08(bits_c08, kind_c08, m_c08):
        b_c08 = int(np_c01.log2(m_c08))
        blocks_c08 = bits_c08.reshape(-1, b_c08)
        ints_c08 = blocks_c08.dot(1 << np_c01.arange(b_c08 - 1, -1, -1))
        ints_c08 = np_c01.array([int_to_gray_c06(int(x_c08)) for x_c08 in ints_c08])
        const_c08 = qam_constellation_c07(m_c08) if kind_c08 == "qam" else psk_constellation_c07(m_c08)
        return const_c08[ints_c08], const_c08, b_c08

    def symbols_to_bits_c08(rx_symbols_c08, const_c08, b_c08):
        d_c08 = np_c01.abs(rx_symbols_c08.reshape(-1, 1) - const_c08.reshape(1, -1)) ** 2
        idx_c08 = np_c01.argmin(d_c08, axis=1)
        ints_c08 = np_c01.array([gray_to_int_c06(int(x_c08)) for x_c08 in idx_c08])
        bits_c08 = ((ints_c08[:, None] & (1 << np_c01.arange(b_c08 - 1, -1, -1))) > 0).astype(int)
        return bits_c08.reshape(-1)

    return bits_to_symbols_c08, symbols_to_bits_c08


@app.cell
def rf07_pulse_shaping_c09(alpha_c04, np_c01, sps_c04):
    """
    **RF07: Formatação de pulso NRZ e RRC**

    NRZ: pulso retangular
    RRC (Raised Cosine com Roll-off α): pulso com limitação de banda

    Ambos normalizados em energia (l₂ norm = 1).
    Alpha é controlado pelo input box na célula ui_sliders_c03.
    """
    alpha_c09 = float(alpha_c04)

    def pulse_coeffs_c09(name_c09):
        if name_c09 == "nrz":
            p_c09 = np_c01.ones(sps_c04)
        else:
            span_c09 = 6  # match Lab 2 N.py: N_taps=6
            t_c09 = np_c01.arange(-span_c09 * sps_c04, span_c09 * sps_c04 + 1) / sps_c04
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

    return pulse_coeffs_c09


@app.cell
def rf15_theoretical_ber_c10(erfc_c01, np_c01):
    """
    **RF15: Curvas teóricas de BER**

    Fórmulas da Proposta/PRD com mapeamento Gray:
    - M-PSK: Q(√(2 log₂(M) Eb/N₀) sin(π/M))
    - M-QAM: (4/log₂(M))(1 - 1/√M) Q(√(3 log₂(M) Eb/N₀ / (M-1)))
    """
    def theoretical_ber_c10(kind_c10, m_c10, ebn0_c10):
        ebn0_lin_c10 = 10 ** (ebn0_c10 / 10)
        b_c10 = np_c01.log2(m_c10)
        if kind_c10 == "qam":
            q_c10 = 0.5 * erfc_c01(np_c01.sqrt((3 * b_c10 / (m_c10 - 1)) * ebn0_lin_c10) / np_c01.sqrt(2))
            return (4 / b_c10) * (1 - 1 / np_c01.sqrt(m_c10)) * q_c10
        if m_c10 == 2:
            return 0.5 * erfc_c01(np_c01.sqrt(ebn0_lin_c10))
        q_c10 = 0.5 * erfc_c01(np_c01.sqrt(2 * b_c10 * ebn0_lin_c10) * np_c01.sin(np_c01.pi / m_c10) / np_c01.sqrt(2))
        return (2 / b_c10) * q_c10

    return (theoretical_ber_c10,)


@app.cell
def rf08_rf09_rf10_rf11_rf12_link_sim_c11(
    alpha_c04,
    fc_c04,
    gray_to_int_c06,
    int_to_gray_c06,
    np_c01,
    psk_constellation_c07,
    qam_constellation_c07,
    rng_c05,
    sps_c04,
):
    """
    **RF08: Modulação banda passante** (OFDM QAM em portadora)
    **RF09: Ruído AWGN** (σ = √(1/(2 b Eb/N₀)))
    **RF10: Demodulação coerente** (multiplica por portadoras locais I e Q)
    **RF11: Filtro casado** (convolução com pulso reverso)
    **RF12: Amostragem** (sampling a t = τ_offset + k Ts, Ts = 1/(M sps))

    Cadeia completa: bits → símbolos → upsampling → formatação de pulso → 
    modulação → AWGN → demodulação → filtro casado → amostragem → decisão → bits
    """
    # Use centralized Gray coding and constellation functions passed from other cells
    def bits_to_symbols_c11(bits_c11, kind_c11, m_c11):
        b_c11 = int(np_c01.log2(m_c11))
        blocks_c11 = bits_c11.reshape(-1, b_c11)
        ints_c11 = blocks_c11.dot(1 << np_c01.arange(b_c11 - 1, -1, -1))
        ints_c11 = np_c01.array([int_to_gray_c06(int(x_c11)) for x_c11 in ints_c11])
        const_c11 = qam_constellation_c07(m_c11) if kind_c11 == "qam" else psk_constellation_c07(m_c11)
        return const_c11[ints_c11], const_c11, b_c11

    def symbols_to_bits_c11(rx_symbols_c11, const_c11, b_c11):
        d_c11 = np_c01.abs(rx_symbols_c11.reshape(-1, 1) - const_c11.reshape(1, -1)) ** 2
        idx_c11 = np_c01.argmin(d_c11, axis=1)
        ints_c11 = np_c01.array([gray_to_int_c06(int(x_c11)) for x_c11 in idx_c11])
        bits_c11 = ((ints_c11[:, None] & (1 << np_c01.arange(b_c11 - 1, -1, -1))) > 0).astype(int)
        return bits_c11.reshape(-1)

    # Inlined pulse shaping
    alpha_c11 = float(alpha_c04)

    def pulse_coeffs_c11(name_c11):
        if name_c11 == "nrz":
            p_c11 = np_c01.ones(sps_c04)
        else:
            span_c11 = 6  # match Lab 2 N.py: N_taps=6
            t_c11 = np_c01.arange(-span_c11 * sps_c04, span_c11 * sps_c04 + 1) / sps_c04
            p_c11 = np_c01.zeros_like(t_c11, dtype=float)
            for i_c11, ti_c11 in enumerate(t_c11):
                if ti_c11 == 0:
                    p_c11[i_c11] = 1 - alpha_c11 + 4 * alpha_c11 / np_c01.pi
                elif abs(abs(4 * alpha_c11 * ti_c11) - 1) < 1e-12:
                    p_c11[i_c11] = (
                        alpha_c11
                        / np_c01.sqrt(2)
                        * (
                            (1 + 2 / np_c01.pi) * np_c01.sin(np_c01.pi / (4 * alpha_c11))
                            + (1 - 2 / np_c01.pi) * np_c01.cos(np_c01.pi / (4 * alpha_c11))
                        )
                    )
                else:
                    num_c11 = np_c01.sin(np_c01.pi * ti_c11 * (1 - alpha_c11)) + 4 * alpha_c11 * ti_c11 * np_c01.cos(
                        np_c01.pi * ti_c11 * (1 + alpha_c11)
                    )
                    den_c11 = np_c01.pi * ti_c11 * (1 - (4 * alpha_c11 * ti_c11) ** 2)
                    p_c11[i_c11] = num_c11 / den_c11
        return p_c11 / np_c01.sqrt(np_c01.sum(p_c11**2))

    # Main link simulation function

    def simulate_link_c11(kind_c11, m_c11, pulse_name_c11, ebn0_db_c11, num_symbols_c11):
        b_c11 = int(np_c01.log2(m_c11))
        bits_tx_c11 = rng_c05.integers(0, 2, size=num_symbols_c11 * b_c11)
        symbols_tx_c11, const_c11, b_c11 = bits_to_symbols_c11(bits_tx_c11, kind_c11, m_c11)

        pulse_c11 = pulse_coeffs_c11(pulse_name_c11)
        upsampled_c11 = np_c01.zeros(len(symbols_tx_c11) * sps_c04, dtype=complex)
        upsampled_c11[::sps_c04] = symbols_tx_c11
        shaped_c11 = np_c01.convolve(upsampled_c11, pulse_c11, mode="full")

        fs_c11 = fc_c04 * sps_c04
        t_c11 = np_c01.arange(len(shaped_c11)) / fs_c11
        carrier_c11 = 2 * np_c01.pi * fc_c04 * t_c11
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

        bits_rx_c11 = symbols_to_bits_c11(symbols_rx_c11, const_c11, b_c11)
        ber_c11 = np_c01.mean(bits_tx_c11 != bits_rx_c11)
        return ber_c11, symbols_tx_c11, symbols_rx_c11, const_c11

    return (simulate_link_c11,)


@app.cell
def results_c12(
    ebn0_db_c04,
    kind_cases_c04,
    np_c01,
    num_bits_target_slider_c03,
    pulse_cases_c04,
    simulate_link_c11,
    theoretical_ber_c10,
):
    """
    **RF14: Executa simulação de BER por Monte Carlo**

    Itera sobre todas as combinações (modulação, pulso, Eb/N0) e calcula BER simulada vs teórica.
    """
    results_c12 = {}
    simulate_link_c12 = simulate_link_c11
    theoretical_ber_c12 = theoretical_ber_c10
    num_bits_target_c12 = int(num_bits_target_slider_c03.value)
    import math as math_c12

    for pulse_name_c12 in pulse_cases_c04:
        results_c12[pulse_name_c12] = {}
        for kind_c12, m_c12 in kind_cases_c04:
            ber_curve_c12 = []
            b_c12 = int(np_c01.log2(m_c12))
            num_symbols_c12 = max(1, int(num_bits_target_c12 // b_c12))
            num_bits_actual_c12 = num_symbols_c12 * b_c12
            th_24_c12 = theoretical_ber_c12(kind_c12, m_c12, 24)
            example_tx_c12 = None
            example_rx_c12 = None
            example_const_c12 = None
            for eb_c12 in ebn0_db_c04:
                ber_c12, symbols_tx_c12, symbols_rx_c12, const_c12 = simulate_link_c12(
                    kind_c12,
                    m_c12,
                    pulse_name_c12,
                    eb_c12,
                    num_symbols_c12,
                )
                errors_c12 = int(round(ber_c12 * num_symbols_c12 * b_c12))
                if errors_c12 == 0 and th_24_c12 > 0:
                    required_bits_c12 = math_c12.ceil(3.0 / th_24_c12)
                    ber_curve_c12.append(3.0 / required_bits_c12)
                else:
                    ber_curve_c12.append(ber_c12)
                # store an example constellation at the highest Eb/N0 point
                example_tx_c12 = symbols_tx_c12
                example_rx_c12 = symbols_rx_c12
                example_const_c12 = const_c12
            results_c12[pulse_name_c12][(kind_c12, m_c12)] = {
                "ber": np_c01.array(ber_curve_c12),
                "theory": np_c01.array([theoretical_ber_c12(kind_c12, m_c12, eb_c12) for eb_c12 in ebn0_db_c04]),
                "num_symbols": num_symbols_c12,
                "num_bits_actual": num_bits_actual_c12,
                "example_tx": example_tx_c12,
                "example_rx": example_rx_c12,
                "example_const": example_const_c12,
            }
    return (results_c12,)


@app.cell
def plots_final_c13(
    ebn0_db_c04,
    kind_cases_c04,
    plt_c01,
    pulse_cases_c04,
    results_c12,
):
    """
    **RF03/RF12 Visualização: Gráficos de BER e constelações**

    Esquerda: BER simulada vs teórica em escala semilog para cada modulação/pulso.
    Direita: Constelação transmitida (TX), recebida (RX) e ideal.
    """
    # Create one figure per combination: pulse x (modulation, M)
    for pulse_name_c13 in pulse_cases_c04:
        for kind_name_c13, modulation_order_c13 in kind_cases_c04:
            case_data_c13 = results_c12.get(pulse_name_c13, {}).get((kind_name_c13, modulation_order_c13), None)
            if case_data_c13 is None:
                continue
            _, axes_c13 = plt_c01.subplots(1, 2, figsize=(12, 5))

            # BER plot for this case
            # plot simulation and then theory (theory will use same color)
            sim_line_c13 = axes_c13[0].semilogy(
                ebn0_db_c04,
                case_data_c13["ber"],
                marker="o",
                label=f"Simulada {kind_name_c13.upper()} M={modulation_order_c13}",
                linewidth=2,
            )[0]
            axes_c13[0].semilogy(
                ebn0_db_c04,
                case_data_c13["theory"],
                linestyle="--",
                linewidth=1,
                alpha=0.8,
                color=sim_line_c13.get_color(),
                label="Teórica",
            )
            axes_c13[0].set_xlabel("Eb/N0 (dB)", fontsize=12)
            axes_c13[0].set_ylabel("BER", fontsize=12)
            axes_c13[0].grid(True, which="both", alpha=0.3)
            axes_c13[0].legend(fontsize=9)
            axes_c13[0].set_ylim([1e-5, 1])
            axes_c13[0].set_title(f"BER: {kind_name_c13.upper()} M={modulation_order_c13} / {pulse_name_c13.upper()}", fontsize=11, fontweight="bold")

            # Constellation example (at highest Eb/N0)
            example_tx_c13 = case_data_c13.get("example_tx")
            example_rx_c13 = case_data_c13.get("example_rx")
            example_const_c13 = case_data_c13.get("example_const")
            if example_tx_c13 is None or example_rx_c13 is None or example_const_c13 is None:
                axes_c13[1].text(0.5, 0.5, "No example constellation available", ha="center", va="center")
                axes_c13[1].set_xticks([])
                axes_c13[1].set_yticks([])
            else:
                axc = axes_c13[1]
                # TX: keep visible but smaller
                axc.scatter(example_tx_c13.real, example_tx_c13.imag, s=20, label="TX", alpha=0.6, color="blue")
                # RX: denser, light points (match slides preview)
                axc.scatter(example_rx_c13.real, example_rx_c13.imag, s=8, label="RX", alpha=0.25, color="orange")
                # Ideal constellation: clear 'x' markers
                axc.scatter(example_const_c13.real, example_const_c13.imag, s=80, marker="x", label="Ideal", linewidth=2, color="red")
                axc.axhline(0, linewidth=0.8)
                axc.axvline(0, linewidth=0.8)
                axc.grid(True, alpha=0.3)
                axc.set_xlabel("Componente em fase I", fontsize=12)
                axc.set_ylabel("Componente em quadratura Q", fontsize=12)
                axc.legend(fontsize=9)
                axc.set_title(f"Constelação (Eb/N0 = {ebn0_db_c04[-1]} dB)")
                axc.axis("equal")

            plt_c01.tight_layout()
            plt_c01.show()
    return ()


@app.cell
def plots_aggregate_by_pulse_c14(
    ebn0_db_c04,
    kind_cases_c04,
    plt_c01,
    pulse_cases_c04,
    results_c12,
):
    """
    Comparativos extras de BER: uma figura por pulso com todas as modulações.

    Mantém os gráficos independentes já existentes e adiciona apenas os agregados por pulso.
    """
    from pathlib import Path as Path_c14

    output_dir_c14 = Path_c14("output/lab2_artifacts")
    output_dir_c14.mkdir(parents=True, exist_ok=True)
    for png_c14 in output_dir_c14.glob("*.png"):
        try:
            png_c14.unlink()
        except Exception:
            pass

    for pulse_name_c14 in pulse_cases_c04:
        fig_c14, ax_c14 = plt_c01.subplots(1, 1, figsize=(9, 5))
        for kind_name_c14, modulation_order_c14 in kind_cases_c04:
            case_data_c14 = results_c12.get(pulse_name_c14, {}).get((kind_name_c14, modulation_order_c14), None)
            if case_data_c14 is None:
                continue
            # plot sim then theory using same base color
            sim_line_c14 = ax_c14.semilogy(
                ebn0_db_c04,
                case_data_c14["ber"],
                marker="o",
                linewidth=1.5,
                label=f"SIM {kind_name_c14.upper()} M={modulation_order_c14}",
            )[0]
            ax_c14.semilogy(
                ebn0_db_c04,
                case_data_c14["theory"],
                linestyle="--",
                linewidth=1.2,
                alpha=0.85,
                color=sim_line_c14.get_color(),
                label=f"TH {kind_name_c14.upper()} M={modulation_order_c14}",
            )
        ax_c14.set_xlabel("Eb/N0 (dB)")
        ax_c14.set_ylabel("BER")
        ax_c14.set_ylim([1e-5, 1])
        ax_c14.set_title(f"BER comparativa - pulso {pulse_name_c14.upper()} (todas as modulações)")
        ax_c14.grid(True, which="both", alpha=0.3)
        ax_c14.legend(fontsize=8)
        plt_c01.tight_layout()
        fig_c14.savefig(output_dir_c14 / f"BER_all_modulations_pulse_{pulse_name_c14.upper()}.png", dpi=150)
        plt_c01.show()
    return ()


if __name__ == "__main__":
    app.run()
