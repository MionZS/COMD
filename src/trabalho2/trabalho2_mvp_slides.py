import marimo

__generated_with = "0.23.8"
app = marimo.App(width="medium")


@app.cell
def imports_c01():
    import marimo as mo
    import numpy as np
    import matplotlib.pyplot as plt
    from scipy.special import erfc

    return erfc, mo, np, plt


@app.cell
def title_c02(mo):
    mo.md(r"""
    # TC2 — Simulação BER de Modulações M-QAM e M-PSK em Banda Passante

    **Disciplina:** TE903/EELT7026 — Comunicação Digital  \\
    **Tema:** Análise de desempenho BER sob canal AWGN  \\
    **Entregáveis:** código Python, constelações, curvas BER e relatório IEEE

    Este notebook organiza a implementação do sistema de comunicação digital em banda passante,
    com foco em modulações, pulsos, filtro casado, e comparação entre BER simulada e teórica.
    """)
    return


@app.cell
def sources_c03(mo):
    mo.md(r"""
    ## Fontes metodológicas usadas

    | Fonte | Aplicação no TC2 |
    |---|---|
    | Enunciado do TC2 | Define modulações, pulsos, $f_c$, $f_s$, $E_b/N_0$, AWGN, constelações e curvas BER. |
    | MathWorks — BER Analysis Techniques | Justifica o critério de pelo menos cerca de 100 erros por ponto de simulação. |
    | MathWorks — BER Analysis App | Justifica o critério de parada por número mínimo de erros ou número máximo de bits. |
    | MathWorks — `berconfint` | Interpreta a BER simulada como estimativa estatística com intervalo de confiança. |
    | SiTime — BER Confidence Calculator | Justifica que zero erros não significa BER exatamente nula. |
    | Marimo Docs | Fundamenta o uso de `mo.md`, LaTeX, widgets, layouts, slides e exportação. |
    """)
    return


@app.cell
def milestones_c04(mo):
    mo.hstack(
        [
            mo.stat(label="Portadora", value="10 Hz", caption=r"$f_c$"),
            mo.stat(label="Amostragem", value="40 Hz", caption=r"$f_s=4f_c$"),
            mo.stat(label="Pulsos", value="NRZ / RRC", caption=r"$\alpha=0.15$"),
            mo.stat(label="Canal", value="AWGN", caption=r"$\sigma_V^2=N_0/2$"),
        ],
        widths="equal",
    )
    return


@app.cell
def complementary_views_md_c05(mo):
    mo.md(r"""
    ## Vistas complementares

    As duas figuras abaixo são intencionalmente estáticas e representativas.
    Elas seguem a mesma ideia do trabalho 1: mostrar a codificação de forma simples
    e destacar como os pulsos aparecem no tempo antes da simulação principal.
    """)
    return


@app.cell
def line_coding_view_c06(np, plt):
    demo_bits = np.array([1, 0, 1, 1, 0, 0, 1, 0, 1, 1, 0, 0], dtype=int)
    samples_per_bit = 40
    line_time = np.arange(len(demo_bits) * samples_per_bit) / samples_per_bit

    nrz_levels = demo_bits.astype(float)
    nrz_waveform = np.repeat(nrz_levels, samples_per_bit)

    line_fig, line_ax = plt.subplots(figsize=(10, 3.8))
    line_ax.step(line_time, nrz_waveform, where="post", linewidth=1.8, label="NRZ unipolar")
    line_ax.set_ylim(-0.2, 1.2)
    line_ax.grid(True, alpha=0.3)
    line_ax.set_ylabel("Nível")
    line_ax.set_xlabel(r"Tempo normalizado por $T_b$")
    line_ax.set_title("Codificação NRZ unipolar usada no projeto")
    line_ax.legend(loc="upper right")
    plt.tight_layout()
    return (line_fig,)


@app.cell
def pulse_shapes_view_c07(np, plt):
    alpha = 0.15
    span = 6
    pulse_time = np.linspace(-span, span, 1200)

    nrz = np.where(np.abs(pulse_time) <= 0.5, 1.0, 0.0)
    rrc = np.zeros_like(pulse_time)
    for pulse_idx, ti in enumerate(pulse_time):
        if np.isclose(ti, 0.0):
            rrc[pulse_idx] = 1 - alpha + 4 * alpha / np.pi
        elif alpha > 0 and np.isclose(abs(4 * alpha * ti), 1.0):
            rrc[pulse_idx] = alpha / np.sqrt(2) * (
                (1 + 2 / np.pi) * np.sin(np.pi / (4 * alpha))
                + (1 - 2 / np.pi) * np.cos(np.pi / (4 * alpha))
            )
        else:
            numerator = np.sin(np.pi * ti * (1 - alpha)) + 4 * alpha * ti * np.cos(
                np.pi * ti * (1 + alpha)
            )
            denominator = np.pi * ti * (1 - (4 * alpha * ti) ** 2)
            rrc[pulse_idx] = numerator / denominator

    rrc /= np.sqrt(np.trapezoid(rrc ** 2, pulse_time))

    pulse_fig, pulse_ax = plt.subplots(figsize=(10, 4))
    pulse_ax.plot(pulse_time, nrz, linewidth=1.8, label="NRZ")
    pulse_ax.plot(pulse_time, rrc, linewidth=1.8, label=r"RRC ($\alpha=0.15$)")
    pulse_ax.set_xlim(-span, span)
    pulse_ax.set_ylim(-0.3, 1.3)
    pulse_ax.set_xlabel(r"Tempo normalizado por $T_b$")
    pulse_ax.set_ylabel("Amplitude")
    pulse_ax.set_title("Pulsos usados na simulação - visão resumida")
    pulse_ax.grid(True, alpha=0.3)
    pulse_ax.legend()
    plt.tight_layout()
    return (pulse_fig,)


@app.cell
def complementary_views_c08(line_fig, mo, pulse_fig):
    mo.vstack(
        [
            mo.md("## Codificação e pulsos"),
            mo.md(
                "NRZ significa *non-return to zero*: o sinal não volta ao nível zero entre símbolos. "
                "Nesta visualização, o nível lógico baixo é 0 e o alto é 1, então o gráfico mostra "
                "uma codificação NRZ unipolar, também conhecida como on-off."
            ),
            line_fig,
            pulse_fig,
        ]
    )
    return


@app.cell(hide_code=True)
def m_select_c05b(mo, modulation):
    m_options = {"QAM": [4, 16, 64], "PSK": [2, 4, 8, 16]}
    m_default = 16 if modulation.value == "QAM" else 4
    m_select = mo.ui.dropdown(options=m_options[modulation.value], value=m_default, label="Ordem M")
    mo.vstack([mo.md("### Ordem da modulação"), m_select])
    return (m_select,)


@app.cell
def params_c06(ebn0_slider, m_select, mo, n_symbols_slider, np):
    M = int(m_select.value)
    b = int(np.log2(M))
    n_symbols_requested = int(n_symbols_slider.value)
    n_bits_desired = n_symbols_requested * b
    n_bits_adjusted = (n_bits_desired // b) * b
    n_symbols_adjusted = n_bits_adjusted // b
    ebn0_db = float(ebn0_slider.value)
    ebn0_linear = 10 ** (ebn0_db / 10)
    Ex = 1.0
    Eb = Ex / b
    N0 = Eb / ebn0_linear
    sigma2_v = N0 / 2
    sigma_v = np.sqrt(sigma2_v)
    mo.hstack([
        mo.stat(label="M", value=str(M), caption="ordem da constelação"),
        mo.stat(label="b", value=str(b), caption="bits/símbolo"),
        mo.stat(label="Bits ajustados", value=f"{n_bits_adjusted:,}", caption="múltiplo de b"),
        mo.stat(label="Símbolos", value=f"{n_symbols_adjusted:,}", caption="streamados"),
        mo.stat(label=r"$\sigma_V^2$", value=f"{sigma2_v:.3e}", caption="variância AWGN"),
    ], widths="equal")
    return (
        Eb,
        M,
        N0,
        b,
        ebn0_db,
        ebn0_linear,
        n_bits_adjusted,
        n_bits_desired,
        n_symbols_adjusted,
        n_symbols_requested,
        sigma2_v,
        sigma_v,
    )


@app.cell(hide_code=True)
def ui_controls_c05(mo):
    pulse_select = mo.ui.dropdown(options=["NRZ", "RRC"], value="NRZ", label="Pulso")
    modulation = mo.ui.dropdown(options=["QAM", "PSK"], value="QAM", label="Modulação")
    ebn0_slider = mo.ui.slider(start=0, stop=24, step=1, value=12, label=r"$E_b/N_0$ [dB]")
    n_symbols_slider = mo.ui.slider(start=100, stop=20000, step=100, value=1000, label="Símbolos streamados")
    mo.vstack([mo.md("## Controles da simulação"), mo.hstack([pulse_select, modulation, ebn0_slider, n_symbols_slider], widths="equal")])
    return ebn0_slider, modulation, n_symbols_slider, pulse_select


@app.cell
def state_md_c07(
    Eb,
    M,
    N0,
    b,
    ebn0_db,
    ebn0_linear,
    mo,
    n_bits_adjusted,
    n_bits_desired,
    n_symbols_requested,
    sigma2_v,
):
    mo.md(rf"""
    ## Estado atual da simulação

    $$
    M={M},\qquad b=\log_2(M)={b}
    $$

    $$
    N_{{\text{{símbolos}}}}={n_symbols_requested}
    $$

    $$
    N_{{\text{{bits,desejado}}}}={n_bits_desired},\quad N_{{\text{{bits,ajustado}}}}={n_bits_adjusted}
    $$

    $$
    E_b/N_0={ebn0_db:.0f}\,\text{{dB}},\quad \gamma_b={ebn0_linear:.3f}
    $$

    $$
    E_b={Eb:.3e},\quad N_0={N0:.3e},\quad \sigma_V^2={sigma2_v:.3e}
    $$
    """)
    return


@app.cell
def constellations_c08(np):
    def qam_constellation(M: int) -> np.ndarray:
        side = int(np.sqrt(M))
        if side ** 2 != M:
            raise ValueError("QAM quadrada exige M quadrado perfeito.")
        levels = np.arange(-(side - 1), side, 2)
        I, Q = np.meshgrid(levels, levels[::-1])
        const = I.flatten() + 1j * Q.flatten()
        return const / np.sqrt(np.mean(np.abs(const) ** 2))

    def psk_constellation(M: int) -> np.ndarray:
        m = np.arange(M)
        const = np.exp(1j * 2 * np.pi * m / M)
        return const / np.sqrt(np.mean(np.abs(const) ** 2))

    def get_constellation(modulation: str, M: int) -> np.ndarray:
        if modulation == "QAM":
            return qam_constellation(M)
        if modulation == "PSK":
            return psk_constellation(M)
        raise ValueError("Modulação inválida.")

    return (get_constellation,)


@app.cell
def preview_c09(
    M,
    b,
    get_constellation,
    modulation,
    n_bits_adjusted,
    np,
    pulse_select,
    sigma_v,
):
    rng = np.random.default_rng(42)
    const = get_constellation(modulation.value, M)
    bits = rng.integers(0, 2, size=n_bits_adjusted)
    bits_grouped = bits.reshape(-1, b)
    weights = 2 ** np.arange(b - 1, -1, -1)
    indices = bits_grouped @ weights
    symbols_tx = const[indices]
    os = 4
    fc = 10.0

    def pulse_coeffs(name):
        if name == "nrz":
            pulse = np.ones(os)
        else:
            alpha = 0.15
            span = 6
            t = np.arange(-span * os, span * os + 1) / os
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

    pulse = pulse_coeffs(pulse_select.value.lower())
    upsampled = np.zeros(len(symbols_tx) * os, dtype=complex)
    upsampled[::os] = symbols_tx
    shaped = np.convolve(upsampled, pulse, mode="full")
    fs = os * fc
    t = np.arange(len(shaped)) / fs
    carrier = 2 * np.pi * fc * t
    tx = np.sqrt(2) * (shaped.real * np.cos(carrier) - shaped.imag * np.sin(carrier))
    rx = tx + sigma_v * rng.standard_normal(tx.size)
    i = np.sqrt(2) * rx * np.cos(carrier)
    q = -np.sqrt(2) * rx * np.sin(carrier)
    bb_rx = i + 1j * q
    filtered = np.convolve(bb_rx, pulse[::-1].conj(), mode="full")
    offset = len(pulse) - 1
    sample_idx = offset + np.arange(len(symbols_tx)) * os
    symbols_rx_preview = filtered[sample_idx]
    return const, symbols_rx_preview


@app.cell
def plot_preview_c10(
    M,
    const,
    ebn0_db,
    modulation,
    n_symbols_adjusted,
    np,
    plt,
    symbols_rx_preview,
):
    preview_fig, preview_ax = plt.subplots(figsize=(6, 6))
    max_points = min(4000, len(symbols_rx_preview))
    preview_ax.scatter(np.real(symbols_rx_preview[:max_points]), np.imag(symbols_rx_preview[:max_points]), s=8, alpha=0.25, label="Amostras recebidas")
    preview_ax.scatter(np.real(const), np.imag(const), s=80, marker="x", label="Constelação ideal")
    preview_ax.axhline(0, linewidth=0.8)
    preview_ax.axvline(0, linewidth=0.8)
    preview_ax.grid(True, alpha=0.3)
    preview_ax.axis("equal")
    preview_ax.set_title(f"{M}-{modulation.value} | Eb/N0={ebn0_db:.0f} dB | {n_symbols_adjusted} símbolos")
    preview_ax.set_xlabel("Componente em fase I")
    preview_ax.set_ylabel("Componente em quadratura Q")
    preview_ax.legend()
    return (preview_fig,)


@app.cell
def slide_controls_and_figure_c11(
    M,
    b,
    ebn0_db,
    mo,
    modulation,
    n_symbols_adjusted,
    preview_fig,
    pulse_select,
):
    mo.vstack(
        [
            mo.md(
                rf"""
                ## Marco visual — constelação recebida

                A figura mostra como o ruído AWGN espalha os pontos da constelação.

                - Modulação: **{M}-{modulation.value}**
                - Bits por símbolo: **{b}**
                - Pulso selecionado: **{pulse_select.value}**
                - $E_b/N_0$: **{ebn0_db:.0f} dB**
                - Símbolos streamados: **{n_symbols_adjusted:,}**
                """
            ),
            mo.hstack(
                [
                    mo.vstack(
                        [
                            mo.stat(label="M", value=str(M), caption="pontos da constelação"),
                            mo.stat(label="b", value=str(b), caption="bits por símbolo"),
                            mo.stat(label="SNR", value=f"{ebn0_db:.0f} dB", caption=r"$E_b/N_0$"),
                            mo.stat(label="Símbolos", value=f"{n_symbols_adjusted:,}", caption="streamados"),
                        ]
                    ),
                    preview_fig,
                ],
                widths=[1, 2],
            ),
        ]
    )
    return


@app.cell
def adjust_bits_c12(mo):
    mo.md(r"""
    ## Ajuste do número de bits

    ```python
    def adjust_n_bits(n_bits_desired: int, b: int) -> tuple[int, int]:
        # PONTO-CHAVE:
        # O número de bits precisa ser múltiplo de b,
        # pois cada símbolo carrega exatamente b bits.
        n_bits_adjusted = (n_bits_desired // b) * b

        # PONTO-CHAVE:
        # Depois do ajuste, o número de símbolos é inteiro.
        n_symbols = n_bits_adjusted // b

        return n_bits_adjusted, n_symbols
    ```

    $$
    N_{\text{bits,ajustado}}=\left\lfloor\frac{N_{\text{bits,desejado}}}{b}\right\rfloor b
    $$

    $$
    N_{\text{símbolos}}=\frac{N_{\text{bits,ajustado}}}{b}
    $$
    """)
    mo.callout(
        mo.md(r"""
        O ajuste evita bits "sobrando" no final da sequência.
        """),
        kind="info",
    )
    return


@app.cell
def convergence_md_c13(mo):
    mo.md(r"""
    ## Convergência estatística da BER

    A BER simulada é uma estimativa de Monte Carlo:

    $$
    \widehat{BER}=\frac{N_{\text{erros}}}{N_{\text{bits}}}
    $$

    A recomendação prática adotada é simular cada ponto de $E_b/N_0$ até atingir uma das condições:

    $$
    N_{\text{erros}}\geq N_{\text{erros,min}}
    $$

    ou

    $$
    N_{\text{bits}}\geq N_{\text{bits,max}}
    $$

    com referência prática:

    $$
    N_{\text{erros,min}}\approx 100
    $$
    """)
    mo.md(r"""
    ```python
    MIN_ERRORS = 100
    MAX_BITS = 2_000_000
    total_errors = 0
    total_bits = 0
    while total_errors < MIN_ERRORS and total_bits < MAX_BITS:
        # gera bloco, transmite, detecta
        # atualiza contadores
        pass
    ```
    """)
    return


@app.cell
def theory_md_c14(mo):
    mo.md(r"""
    ## Curvas teóricas de BER

    $$
    Q(x)=\frac{1}{2}\operatorname{erfc}\left(\frac{x}{\sqrt{2}}\right)
    $$

    Para BPSK:

    $$
    P_b = Q\left(\sqrt{2\frac{E_b}{N_0}}\right)
    $$

    Para $M$-PSK (aprox. Gray):

    $$
    P_b\approx\frac{2}{b}Q\left(\sqrt{2b\frac{E_b}{N_0}}\sin\left(\frac{\pi}{M}\right)\right)
    $$

    Para $M$-QAM quadrada (aprox. Gray):

    $$
    P_b\approx\frac{4}{b}\left(1-\frac{1}{\sqrt{M}}\right)Q\left(\sqrt{\frac{3b}{M-1}\frac{E_b}{N_0}}\right)
    $$
    """)
    return


@app.cell
def theory_funcs_c15(erfc, np):
    def qfunc(x):
        return 0.5 * erfc(x / np.sqrt(2))

    def ber_theory_psk(ebn0_db, m):
        b = int(np.log2(m))
        ebn0 = 10 ** (np.asarray(ebn0_db) / 10)
        if m == 2:
            return qfunc(np.sqrt(2 * ebn0))
        return (2 / b) * qfunc(np.sqrt(2 * b * ebn0) * np.sin(np.pi / m))

    def ber_theory_qam(ebn0_db, m):
        b = int(np.log2(m))
        ebn0 = 10 ** (np.asarray(ebn0_db) / 10)
        return (
            (4 / b) * (1 - 1 / np.sqrt(m)) * qfunc(np.sqrt((3 * b / (m - 1)) * ebn0))
        )

    return ber_theory_psk, ber_theory_qam


@app.cell
def theory_plot_c16(
    M,
    ber_theory_psk,
    ber_theory_qam,
    ebn0_db,
    modulation,
    np,
    plt,
):
    _ebn0_grid = np.arange(0, 25, 1)
    if modulation.value == "QAM":
        _ber_curve = ber_theory_qam(_ebn0_grid, M)
        _current_ber = ber_theory_qam(np.array([ebn0_db]), M)[0]
    else:
        _ber_curve = ber_theory_psk(_ebn0_grid, M)
        _current_ber = ber_theory_psk(np.array([ebn0_db]), M)[0]

    _fig_ber, _ax_ber = plt.subplots(figsize=(7, 4))
    _ax_ber.semilogy(_ebn0_grid, _ber_curve, label=f"{M}-{modulation.value} teórica")
    _ax_ber.scatter([ebn0_db], [_current_ber], s=80, label="Ponto atual")
    _ax_ber.grid(True, which="both", alpha=0.3)
    _ax_ber.set_xlabel(r"$E_b/N_0$ [dB]")
    _ax_ber.set_ylabel("BER teórica")
    _ax_ber.set_ylim(1e-8, 1)
    _ax_ber.legend()
    fig_ber = _fig_ber
    return (fig_ber,)


@app.cell
def theory_slide_c17(fig_ber, mo):
    mo.vstack(
        [
            mo.md("## Painel comparativo de curva teórica"),
            fig_ber,
        ]
    )
    return


@app.cell
def stop_report_c18(mo):
    mo.md(r"""
    ## Relatório separado do caso de parada

    O caso de parada **não** é escrito na imagem. Ele aparece neste relatório textual separado.

    Critérios usados na simulação:

    - parar ao atingir o número mínimo de erros por ponto;
    - ou parar ao atingir o teto de bits por ponto.

    Este painel registra o critério aplicado sem poluir a figura principal.
    """)
    return


@app.cell
def pipeline_md_c18(mo):
    mo.vstack(
        [
            mo.md("## Pipeline final do TC2"),
            mo.md(
                "O sistema completo implementado no projeto segue a cadeia abaixo:"
            ),
            mo.md(
                r"""
    $$
    \begin{aligned}
    	ext{bits}
    &\rightarrow \text{mapeamento } M\text{-QAM}/M\text{-PSK}
    \rightarrow p(t)
    \rightarrow \text{banda passante} \\
    &\rightarrow \text{AWGN}
    \rightarrow \text{demodulação coerente}
    \rightarrow p(T_s - t)
    \rightarrow \text{amostragem} \\
    &\rightarrow \text{decisão ML}
    \rightarrow \widehat{\mathrm{BER}}
    \end{aligned}
    $$
    """
            ),
            mo.md(
                "Em palavras, a cadeia parte dos bits, passa pelo mapeamento da constelação, pelo pulso no tempo, pelo canal e pelo receptor coerente, até gerar a BER estimada."
            ),
            mo.md(
                "A implementação interativa no Marimo serve como visualização e validação conceitual."
            ),
            mo.md(
                "O código final do TC2 deve executar o pipeline completo em banda passante e salvar:"
            ),
            mo.md(
                "- constelações transmitidas;\n- constelações recebidas após amostragem;\n- curvas BER simuladas;\n- curvas BER teóricas;\n- tabelas `.csv` com os resultados."
            ),
        ]
    )
    return


if __name__ == "__main__":
    app.run()
