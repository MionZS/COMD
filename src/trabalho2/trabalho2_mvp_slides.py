import marimo

__generated_with = "0.23.0"
app = marimo.App()


@app.cell
def _():
    import marimo as mo
    import numpy as np
    import matplotlib.pyplot as plt
    from scipy.special import erfc

    return mo, np, plt


@app.cell
def _(mo):
    mo.md(r"""
    # TC2 — Simulação BER de Modulações M-QAM e M-PSK em Banda Passante

    **Disciplina:** TE903/EELT7026 — Comunicação Digital  \n
    **Tema:** Análise de desempenho BER sob canal AWGN  \n
    **Entregáveis:** código Python, constelações, curvas BER e relatório IEEE

    Este notebook organiza a implementação do sistema de comunicação digital em banda passante,
    com foco em:

    - modulações $M$-QAM e $M$-PSK;
    - pulsos NRZ e raiz do cosseno levantado;
    - canal AWGN;
    - filtro casado;
    - decisão por distância Euclidiana;
    - comparação entre BER simulada e BER teórica.
    """)
    return


@app.cell
def _(mo):
    mo.md(r"""
    ## Fontes metodológicas usadas

    | Fonte | Aplicação no TC2 |
    |---|---|
    | Enunciado do TC2 | Define modulações, pulsos, $f_c$, $f_s$, $E_b/N_0$, AWGN, constelações e curvas BER. |
    | MathWorks — BER Analysis Techniques | Justifica o critério de pelo menos cerca de 100 erros por ponto de simulação. |
    | MathWorks — BER Analysis App | Justifica o critério de parada por número mínimo de erros ou número máximo de bits. |
    | SiTime — BER Confidence Calculator | Caso de zero erros: regra prática para estimativa de confiança. |
    | Marimo Docs | Uso de `mo.md`, LaTeX, widgets, layouts e exportação. |
    """)
    return


@app.cell
def _(mo):
    # Controles interativos
    modulation = mo.ui.dropdown(
        options=["QAM", "PSK"],
        value="QAM",
        label="Modulação",
    )

    M_select = mo.ui.dropdown(
        options=[4, 16, 64],
        value=16,
        label="Ordem M",
    )

    ebn0_slider = mo.ui.slider(
        start=0,
        stop=24,
        step=1,
        value=12,
        label=r"$E_b/N_0$ [dB]",
    )

    n_symbols_slider = mo.ui.slider(
        start=100,
        stop=20000,
        step=100,
        value=1000,
        label="Símbolos streamados",
    )

    pulse_select = mo.ui.dropdown(
        options=["NRZ", "RRC"],
        value="NRZ",
        label="Pulso",
    )

    mo.vstack([
        mo.md("## Controles da simulação"),
        mo.hstack([modulation, M_select, ebn0_slider, n_symbols_slider, pulse_select], widths="equal"),
    ])
    return M_select, ebn0_slider, modulation, n_symbols_slider


@app.cell
def _(M_select, ebn0_slider, mo, n_symbols_slider, np):
    # Cálculos de parâmetros principais e estatísticas
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
        mo.stat(label=r"$igma_V^2$", value=f"{sigma2_v:.3e}", caption="variância AWGN"),
    ], widths="equal")
    return M, b, ebn0_db, n_bits_adjusted, n_symbols_adjusted, sigma_v


@app.cell
def _(np):
    # Funções de constelação
    def qam_constellation(M: int) -> np.ndarray:
        sqrt_M = int(np.sqrt(M))
        if sqrt_M**2 != M:
            raise ValueError("QAM quadrada exige M quadrado perfeito.")

        levels = np.arange(-(sqrt_M - 1), sqrt_M, 2)
        I, Q = np.meshgrid(levels, levels[::-1])
        const = I.flatten() + 1j * Q.flatten()

        const = const / np.sqrt(np.mean(np.abs(const) ** 2))
        return const

    def psk_constellation(M: int) -> np.ndarray:
        m = np.arange(M)
        const = np.exp(1j * 2 * np.pi * m / M)
        const = const / np.sqrt(np.mean(np.abs(const) ** 2))
        return const

    def get_constellation(modulation: str, M: int) -> np.ndarray:
        if modulation == "QAM":
            return qam_constellation(M)
        if modulation == "PSK":
            return psk_constellation(M)
        raise ValueError("Modulação inválida.")

    return (get_constellation,)


@app.cell
def _(M, b, get_constellation, modulation, n_bits_adjusted, np, sigma_v):
    # Geração de bits e preview didático de constelação pós-ruído
    rng = np.random.default_rng(42)
    constellation = get_constellation(modulation.value, M)
    bits = rng.integers(0, 2, size=n_bits_adjusted)
    bits_grouped = bits.reshape(-1, b)
    weights = 2 ** np.arange(b - 1, -1, -1)
    indices = bits_grouped @ weights
    symbols_tx = constellation[indices]

    # Ruído complexo para visualização didática
    noise_complex = (
        rng.normal(0, sigma_v, size=symbols_tx.shape)
        + 1j * rng.normal(0, sigma_v, size=symbols_tx.shape)
    )

    symbols_rx_preview = symbols_tx + noise_complex
    return constellation, symbols_rx_preview


@app.cell
def _(
    M,
    constellation,
    ebn0_db,
    modulation,
    n_symbols_adjusted,
    np,
    plt,
    symbols_rx_preview,
):
    # Plot interativo da constelação (preview)
    fig, ax = plt.subplots(figsize=(6, 6))
    max_points = min(4000, len(symbols_rx_preview))
    ax.scatter(np.real(symbols_rx_preview[:max_points]), np.imag(symbols_rx_preview[:max_points]), s=8, alpha=0.25, label="Amostras recebidas")
    ax.scatter(np.real(constellation), np.imag(constellation), s=80, marker="x", label="Constelação ideal")
    ax.axhline(0, linewidth=0.8)
    ax.axvline(0, linewidth=0.8)
    ax.grid(True, alpha=0.3)
    ax.axis("equal")
    ax.set_title(f"{M}-{modulation.value} | Eb/N0={ebn0_db:.0f} dB | {n_symbols_adjusted} símbolos")
    ax.set_xlabel("Componente em fase I")
    ax.set_ylabel("Componente em quadratura Q")
    ax.legend()
    fig
    return


@app.cell
def _(mo):
    mo.md(r"""
    ## 3. Convergência estatística da BER

    A BER simulada é uma estimativa de Monte Carlo:

    $$
    \hat{BER}=\frac{N_{\text{erros}}}{N_{\text{bits}}}\n
    $$

    A recomendação prática adotada é simular cada ponto de $E_b/N_0$ até atingir uma das condições:

    $$
    N_{\text{erros}}\geq N_{\text{erros,min}}\n
    $$

    ou

    $$
    N_{\text{bits}}\geq N_{\text{bits,max}}\n
    $$

    com:

    $$
    N_{\text{erros,min}}\approx 100\n
    $$
    """)
    return


@app.cell
def _(mo):
    mo.md(r"""
    ## Pipeline final do TC2

    O sistema completo implementado no projeto segue a cadeia:

    $$
    \text{bits}\rightarrow\text{mapeamento }M\text{-QAM}/M\text{-PSK}\rightarrow p(t)\rightarrow\text{banda passante}\rightarrow AWGN\\
    \rightarrow\text{demodulação coerente}\rightarrow p(T_s-t)\rightarrow\text{amostragem}\rightarrow\text{decisão ML}\rightarrow\widehat{BER}\n
    $$

    A implementação interativa no Marimo serve como visualização e validação conceitual.
    """)
    return


if __name__ == "__main__":
    app.run()
