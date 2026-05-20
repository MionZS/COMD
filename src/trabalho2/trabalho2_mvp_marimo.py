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
    return


@app.cell
def controls_md_c02b(mo_c01):
    mo_c01.md("""
    ## ⚙️ Controles da Simulação

    Ajuste os controles abaixo para configurar a simulação:
    """)
    return


@app.cell(hide_code=True)
def ui_sliders_c03(mo_c01):
    """Controles interativos para a simulação (RF01, RF07)."""
    num_bits_slider_c03 = mo_c01.ui.number(
        value=50000,
        start=10000,
        stop=500000,
        step=10000,
        label="📊 Número de bits (RF01)",
    )

    seed_slider_c03 = mo_c01.ui.number(
        value=42,
        start=0,
        stop=1000,
        step=1,
        label="🌱 Seed do RNG",
    )

    alpha_input_c03 = mo_c01.ui.text(
        value="0.15",
        label="📈 RRC alpha (RF07) [0.0-1.0]",
    )

    mo_c01.vstack([
        num_bits_slider_c03,
        seed_slider_c03,
        alpha_input_c03,
    ])

    return num_bits_slider_c03, seed_slider_c03, alpha_input_c03


@app.cell
def params_fixed_c04():
    """
    Parâmetros fixos conforme PRD.
    """
    fc_c04 = 10.0          # RF08: Frequência portadora
    sps_c04 = 4            # RF12: Amostras por símbolo
    ebn0_db_c04 = [0, 4, 8, 12, 16, 20, 24]  # RF12: Pontos de simulação
    kind_cases_c04 = [("psk", 4), ("qam", 16)]  # RF03, RF04
    pulse_cases_c04 = ["nrz", "rrc"]  # RF07
    return ebn0_db_c04, fc_c04, kind_cases_c04, pulse_cases_c04, sps_c04


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
    return int_to_gray_c06, gray_to_int_c06


@app.cell
def rf03_rf04_constellation_c07(np_c01):
    """
    **RF03 (M-PSK) e RF04 (M-QAM): Construir constelações**
    **RF05: Normalização de energia média = 1**

    Ambas as constelações são normalizadas para média de potência = 1 bit/símbolo.
    """
    def qam_constellation_c07(M_c07):
        m_c07 = int(np_c01.sqrt(M_c07))
        levels_c07 = np_c01.arange(-(m_c07 - 1), m_c07, 2)
        xv_c07, yv_c07 = np_c01.meshgrid(levels_c07, levels_c07[::-1])
        const_c07 = xv_c07.flatten() + 1j * yv_c07.flatten()
        return const_c07 / np_c01.sqrt(np_c01.mean(np_c01.abs(const_c07) ** 2))

    def psk_constellation_c07(M_c07):
        const_c07 = np_c01.exp(1j * 2 * np_c01.pi * np_c01.arange(M_c07) / M_c07)
        return const_c07 / np_c01.sqrt(np_c01.mean(np_c01.abs(const_c07) ** 2))
    return qam_constellation_c07, psk_constellation_c07


@app.cell
def rf02_symbol_mapping_c08(np_c01):
    """
    **RF02: Agrupamento de bits em blocos de tamanho b = log₂(M)**

    Mapeia bits → índices → Gray code → símbolos da constelação.
    Usa Gray mapping para alinhamento com fórmulas teóricas (Proposta 5.5).
    """
    # Gray coding functions (inlined to avoid dependency issues)
    def int_to_gray_c08(n_c08):
        return n_c08 ^ (n_c08 >> 1)

    def gray_to_int_c08(g_c08):
        n_c08 = 0
        while g_c08:
            n_c08 ^= g_c08
            g_c08 >>= 1
        return n_c08

    # Constellation functions (inlined to avoid dependency issues)
    def qam_constellation_c08(M_c08):
        m_c08 = int(np_c01.sqrt(M_c08))
        levels_c08 = np_c01.arange(-(m_c08 - 1), m_c08, 2)
        xv_c08, yv_c08 = np_c01.meshgrid(levels_c08, levels_c08[::-1])
        const_c08 = xv_c08.flatten() + 1j * yv_c08.flatten()
        return const_c08 / np_c01.sqrt(np_c01.mean(np_c01.abs(const_c08) ** 2))

    def psk_constellation_c08(M_c08):
        const_c08 = np_c01.exp(1j * 2 * np_c01.pi * np_c01.arange(M_c08) / M_c08)
        return const_c08 / np_c01.sqrt(np_c01.mean(np_c01.abs(const_c08) ** 2))

    def bits_to_symbols_c08(bits_c08, kind_c08, M_c08):
        b_c08 = int(np_c01.log2(M_c08))
        blocks_c08 = bits_c08.reshape(-1, b_c08)
        ints_c08 = blocks_c08.dot(1 << np_c01.arange(b_c08 - 1, -1, -1))
        ints_c08 = np_c01.array([int_to_gray_c08(int(x_c08)) for x_c08 in ints_c08])
        const_c08 = qam_constellation_c08(M_c08) if kind_c08 == "qam" else psk_constellation_c08(M_c08)
        return const_c08[ints_c08], const_c08, b_c08

    def symbols_to_bits_c08(rx_symbols_c08, const_c08, b_c08):
        d_c08 = np_c01.abs(rx_symbols_c08.reshape(-1, 1) - const_c08.reshape(1, -1)) ** 2
        idx_c08 = np_c01.argmin(d_c08, axis=1)
        ints_c08 = np_c01.array([gray_to_int_c08(int(x_c08)) for x_c08 in idx_c08])
        bits_c08 = ((ints_c08[:, None] & (1 << np_c01.arange(b_c08 - 1, -1, -1))) > 0).astype(int)
        return bits_c08.reshape(-1)
    return (
        int_to_gray_c08,
        gray_to_int_c08,
        qam_constellation_c08,
        psk_constellation_c08,
        bits_to_symbols_c08,
        symbols_to_bits_c08,
    )


@app.cell
def rf07_pulse_shaping_c09(alpha_input_c03, np_c01, sps_c04):
    """
    **RF07: Formatação de pulso NRZ e RRC**

    NRZ: pulso retangular
    RRC (Raised Cosine com Roll-off α): pulso com limitação de banda

    Ambos normalizados em energia (l₂ norm = 1).
    Alpha é controlado pelo input box na célula ui_sliders_c03.
    """
    alpha_c09 = float(alpha_input_c03.value)

    def pulse_coeffs_c09(name_c09):
        if name_c09 == "nrz":
            p_c09 = np_c01.ones(sps_c04)
        else:
            span_c09 = 4
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
    alpha_input_c03,
    fc_c04,
    np_c01,
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
    # Inlined Gray coding
    def int_to_gray_c11(n_c11):
        return n_c11 ^ (n_c11 >> 1)

    def gray_to_int_c11(g_c11):
        n_c11 = 0
        while g_c11:
            n_c11 ^= g_c11
            g_c11 >>= 1
        return n_c11

    # Inlined constellation functions
    def qam_constellation_c11(M_c11):
        m_c11 = int(np_c01.sqrt(M_c11))
        levels_c11 = np_c01.arange(-(m_c11 - 1), m_c11, 2)
        xv_c11, yv_c11 = np_c01.meshgrid(levels_c11, levels_c11[::-1])
        const_c11 = xv_c11.flatten() + 1j * yv_c11.flatten()
        return const_c11 / np_c01.sqrt(np_c01.mean(np_c01.abs(const_c11) ** 2))

    def psk_constellation_c11(M_c11):
        const_c11 = np_c01.exp(1j * 2 * np_c01.pi * np_c01.arange(M_c11) / M_c11)
        return const_c11 / np_c01.sqrt(np_c01.mean(np_c01.abs(const_c11) ** 2))

    # Inlined symbol mapping
    def bits_to_symbols_c11(bits_c11, kind_c11, M_c11):
        b_c11 = int(np_c01.log2(M_c11))
        blocks_c11 = bits_c11.reshape(-1, b_c11)
        ints_c11 = blocks_c11.dot(1 << np_c01.arange(b_c11 - 1, -1, -1))
        ints_c11 = np_c01.array([int_to_gray_c11(int(x_c11)) for x_c11 in ints_c11])
        const_c11 = qam_constellation_c11(M_c11) if kind_c11 == "qam" else psk_constellation_c11(M_c11)
        return const_c11[ints_c11], const_c11, b_c11

    def symbols_to_bits_c11(rx_symbols_c11, const_c11, b_c11):
        d_c11 = np_c01.abs(rx_symbols_c11.reshape(-1, 1) - const_c11.reshape(1, -1)) ** 2
        idx_c11 = np_c01.argmin(d_c11, axis=1)
        ints_c11 = np_c01.array([gray_to_int_c11(int(x_c11)) for x_c11 in idx_c11])
        bits_c11 = ((ints_c11[:, None] & (1 << np_c01.arange(b_c11 - 1, -1, -1))) > 0).astype(int)
        return bits_c11.reshape(-1)

    # Inlined pulse shaping
    alpha_c11 = float(alpha_input_c03.value)

    def pulse_coeffs_c11(name_c11):
        if name_c11 == "nrz":
            p_c11 = np_c01.ones(sps_c04)
        else:
            span_c11 = 4
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

    def simulate_link_c11(kind_c11, M_c11, pulse_name_c11, ebn0_db_c11, num_bits_c11):
        b_c11 = int(np_c01.log2(M_c11))
        bits_tx_c11 = rng_c05.integers(0, 2, size=(num_bits_c11 // b_c11) * b_c11)
        symbols_tx_c11, const_c11, b_c11 = bits_to_symbols_c11(bits_tx_c11, kind_c11, M_c11)

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
    num_bits_slider_c03,
    pulse_cases_c04,
    simulate_link_c11,
    theoretical_ber_c10,
):
    """
    **RF14: Executa simulação de BER por Monte Carlo**

    Itera sobre todas as combinações (modulação, pulso, Eb/N0) e calcula BER simulada vs teórica.
    """
    results_c12 = {}
    example_tx_c12 = None
    example_rx_c12 = None
    example_const_c12 = None

    simulate_link_c12 = simulate_link_c11
    theoretical_ber_c12 = theoretical_ber_c10
    num_bits_c12 = int(num_bits_slider_c03.value)

    for pulse_name_c12 in pulse_cases_c04:
        results_c12[pulse_name_c12] = {}
        for kind_c12, M_c12 in kind_cases_c04:
            ber_curve_c12 = []
            for eb_c12 in ebn0_db_c04:
                ber_c12, symbols_tx_c12, symbols_rx_c12, const_c12 = simulate_link_c12(
                    kind_c12,
                    M_c12,
                    pulse_name_c12,
                    eb_c12,
                    num_bits_c12,
                )
                ber_curve_c12.append(ber_c12)
                if pulse_name_c12 == pulse_cases_c04[0] and kind_c12 == kind_cases_c04[0][0] and eb_c12 == ebn0_db_c04[-1]:
                    example_tx_c12 = symbols_tx_c12
                    example_rx_c12 = symbols_rx_c12
                    example_const_c12 = const_c12
            results_c12[pulse_name_c12][(kind_c12, M_c12)] = {
                "ber": np_c01.array(ber_curve_c12),
                "theory": np_c01.array([theoretical_ber_c12(kind_c12, M_c12, eb_c12) for eb_c12 in ebn0_db_c04]),
            }
    return example_const_c12, example_rx_c12, example_tx_c12, results_c12


@app.cell
def plots_final_c13(
    ebn0_db_c04,
    example_const_c12,
    example_rx_c12,
    example_tx_c12,
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
    fig_c13, axes_c13 = plt_c01.subplots(1, 2, figsize=(12, 5))

    # Gráfico 1: BER
    for kind_c13, M_c13 in kind_cases_c04:
        for pulse_name_c13 in pulse_cases_c04:
            label_c13 = f"{kind_c13.upper()} M={M_c13} / {pulse_name_c13.upper()}"
            axes_c13[0].semilogy(
                ebn0_db_c04, 
                results_c12[pulse_name_c13][(kind_c13, M_c13)]["ber"], 
                marker="o", 
                label=label_c13,
                linewidth=2
            )
            axes_c13[0].semilogy(
                ebn0_db_c04, 
                results_c12[pulse_name_c13][(kind_c13, M_c13)]["theory"], 
                linestyle="--",
                linewidth=1,
                alpha=0.6
            )

    axes_c13[0].set_xlabel("Eb/N0 (dB)", fontsize=12)
    axes_c13[0].set_ylabel("BER", fontsize=12)
    axes_c13[0].grid(True, which="both", alpha=0.3)
    axes_c13[0].legend(fontsize=9, loc="best")
    axes_c13[0].set_title("BER: Simulada (●) vs Teórica (--)", fontsize=11, fontweight="bold")

    # Gráfico 2: Constelações
    axes_c13[1].scatter(example_tx_c12.real, example_tx_c12.imag, s=20, label="TX (símbolo recebido)", alpha=0.6, color="blue")
    axes_c13[1].scatter(example_rx_c12.real, example_rx_c12.imag, s=20, label="RX (após decisão)", alpha=0.6, color="orange")
    axes_c13[1].scatter(example_const_c12.real, example_const_c12.imag, s=150, marker="x", label="Constelação ideal", linewidth=2, color="red")
    axes_c13[1].set_xlabel("I (componente em fase)", fontsize=12)
    axes_c13[1].set_ylabel("Q (componente em quadratura)", fontsize=12)
    axes_c13[1].grid(True, alpha=0.3)
    axes_c13[1].legend(fontsize=9)
    axes_c13[1].set_title(f"Constelações (Eb/N0 = {ebn0_db_c04[-1]} dB)", fontsize=11, fontweight="bold")
    axes_c13[1].axis("equal")

    plt_c01.tight_layout()
    plt_c01.show()
    return


if __name__ == "__main__":
    app.run()
