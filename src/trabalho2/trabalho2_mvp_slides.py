import marimo

__generated_with = "0.23.0"
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
    return ()


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
    return ()


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
    return ()


@app.cell(hide_code=True)
def ui_controls_c05(mo):
    modulation = mo.ui.dropdown(options=["QAM", "PSK"], value="QAM", label="Modulação")
    M_select = mo.ui.dropdown(options=[4, 16, 64], value=16, label="Ordem M")
    ebn0_slider = mo.ui.slider(start=0, stop=24, step=1, value=12, label=r"$E_b/N_0$ [dB]")
    n_symbols_slider = mo.ui.slider(start=100, stop=20000, step=100, value=1000, label="Símbolos streamados")
    pulse_select = mo.ui.dropdown(options=["NRZ", "RRC"], value="NRZ", label="Pulso")
    mo.vstack([mo.md("## Controles da simulação"), mo.hstack([modulation, M_select, ebn0_slider, n_symbols_slider, pulse_select], widths="equal")])
    return M_select, ebn0_slider, modulation, n_symbols_slider, pulse_select


@app.cell
def params_c06(M_select, ebn0_slider, mo, n_symbols_slider, np):
    M = int(M_select.value)
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
    return Eb, M, N0, b, ebn0_db, ebn0_linear, n_bits_adjusted, n_bits_desired, n_symbols_adjusted, n_symbols_requested, sigma2_v, sigma_v


@app.cell
def state_md_c07(Eb, M, N0, b, ebn0_db, ebn0_linear, mo, n_bits_adjusted, n_bits_desired, n_symbols_requested, sigma2_v):
    mo.md(
        rf"""
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
        """
    )
    return ()


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
    sigma_v,
):
    rng = np.random.default_rng(42)
    const = get_constellation(modulation.value, M)
    bits = rng.integers(0, 2, size=n_bits_adjusted)
    bits_grouped = bits.reshape(-1, b)
    weights = 2 ** np.arange(b - 1, -1, -1)
    indices = bits_grouped @ weights
    symbols_tx = const[indices]
    noise_complex = rng.normal(0, sigma_v, size=symbols_tx.shape) + 1j * rng.normal(0, sigma_v, size=symbols_tx.shape)
    symbols_rx_preview = symbols_tx + noise_complex
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
    fig, ax = plt.subplots(figsize=(6, 6))
    max_points = min(4000, len(symbols_rx_preview))
    ax.scatter(np.real(symbols_rx_preview[:max_points]), np.imag(symbols_rx_preview[:max_points]), s=8, alpha=0.25, label="Amostras recebidas")
    ax.scatter(np.real(const), np.imag(const), s=80, marker="x", label="Constelação ideal")
    ax.axhline(0, linewidth=0.8)
    ax.axvline(0, linewidth=0.8)
    ax.grid(True, alpha=0.3)
    ax.axis("equal")
    ax.set_title(f"{M}-{modulation.value} | Eb/N0={ebn0_db:.0f} dB | {n_symbols_adjusted} símbolos")
    ax.set_xlabel("Componente em fase I")
    ax.set_ylabel("Componente em quadratura Q")
    ax.legend()
    return (fig,)


@app.cell
def slide_controls_and_figure_c11(M, b, ebn0_db, fig, mo, modulation, n_symbols_adjusted, pulse_select):
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
                    fig,
                ],
                widths=[1, 2],
            ),
        ]
    )
    return ()


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
    return ()


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
    return ()


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
    return ()


@app.cell
def theory_funcs_c15(erfc, np):
    def qfunc(x):
        return 0.5 * erfc(x / np.sqrt(2))

    def ber_theory_psk(ebn0_db, M):
        b = int(np.log2(M))
        ebn0 = 10 ** (np.asarray(ebn0_db) / 10)
        if M == 2:
            return qfunc(np.sqrt(2 * ebn0))
        return (2 / b) * qfunc(np.sqrt(2 * b * ebn0) * np.sin(np.pi / M))

    def ber_theory_qam(ebn0_db, M):
        b = int(np.log2(M))
        ebn0 = 10 ** (np.asarray(ebn0_db) / 10)
        return (
            (4 / b) * (1 - 1 / np.sqrt(M)) * qfunc(np.sqrt((3 * b / (M - 1)) * ebn0))
        )

    return ber_theory_psk, ber_theory_qam, qfunc


@app.cell
def theory_plot_c16(M, ber_theory_psk, ber_theory_qam, ebn0_db, modulation, np, plt):
    ebn0_grid = np.arange(0, 25, 1)
    if modulation.value == "QAM":
        ber_curve = ber_theory_qam(ebn0_grid, M)
        current_ber = ber_theory_qam(np.array([ebn0_db]), M)[0]
    else:
        ber_curve = ber_theory_psk(ebn0_grid, M)
        current_ber = ber_theory_psk(np.array([ebn0_db]), M)[0]

    fig_ber, ax = plt.subplots(figsize=(7, 4))
    ax.semilogy(ebn0_grid, ber_curve, label=f"{M}-{modulation.value} teórica")
    ax.scatter([ebn0_db], [current_ber], s=80, label="Ponto atual")
    ax.grid(True, which="both", alpha=0.3)
    ax.set_xlabel(r"$E_b/N_0$ [dB]")
    ax.set_ylabel("BER teórica")
    ax.set_ylim(1e-8, 1)
    ax.legend()
    return (fig_ber,)


@app.cell
def theory_slide_c17(fig_ber, mo):
    mo.vstack(
        [
            mo.md("## Painel comparativo de curva teórica"),
            fig_ber,
        ]
    )
    return ()

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
    return ()


@app.cell
def pipeline_md_c18(mo):
    mo.md(r"""
    ## Pipeline final do TC2

    O sistema completo implementado no projeto segue a cadeia:

    $$

    	ext{bits}
    \rightarrow
    	ext{mapeamento } M\text{-QAM}/M\text{-PSK}
    \rightarrow
    p(t)
    \rightarrow
    	ext{banda passante}
    \rightarrow
    AWGN
    \rightarrow
    	ext{demodulação coerente}
    \rightarrow
    p(T_s-t)
    \rightarrow
    	ext{amostragem}
    \rightarrow
    	ext{decisão ML}
    \rightarrow
    \widehat{BER}
    $$

    A implementação interativa no Marimo serve como visualização e validação conceitual.

    O código final do TC2 deve executar o pipeline completo em banda passante e salvar:

    - constelações transmitidas;
    - constelações recebidas após amostragem;
    - curvas BER simuladas;
    - curvas BER teóricas;
    - tabelas `.csv` com os resultados.
    """)
    return ()


if __name__ == "__main__":
    app.run()
