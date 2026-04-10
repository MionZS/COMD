import marimo

__generated_with = "0.23.0"
app = marimo.App(width="medium")


@app.cell
def _(mo):
    mo.md(r"""
    # Trabalho Computacional 1 — Comunicação Digital

    Este notebook implementa:
    ##Códigos de linha:
    - **Polar**,
    - **On-off**,
    - **Bipolar**;

    ---
    ## Pulsos:
    - \( \Pi(2t/T_b) \) - Meio-pulso retangular,
    - \( \Pi(t/T_b) \) - Pulso retangular,
    - \( \sin(\pi t/T_b) \) - Meia-senóide;

    ---
    ## Análises
    - Gráficos no domínio do tempo em \( [0, 10T_b) \);
    - PSDs por **Welch** em dB/Hz.
    """)
    return


@app.cell
def _(mo):
    _msg = mo.md(r"""
    #Definição de constantes:
    - **Tb = 1**: Intervalo de pulso, intervalo de bit para sistemas binários | segundo
    - **fs = 10**: Frequência de amostragem | hertz
    - **Nb = 10^5**: Número de bits a serem gerados/analisados | adimensional
    - **N = Tb*fs = 10**: Amostras na duração do pulso | adimensional
    """)
    Tb = 1                 # Intervalo de pulso, intervalo de bit para sistemas binários | segundo
    fs = 10                # Frequência de amostragem | hertz
    Nb = 10**5             # Número de bits a serem gerados/analisados | adimensional
    N = int(round(Tb*fs))  # Amostras na duração do pulso | adimensional
    _msg
    return N, Nb, Tb


@app.cell
def _(Nb, mo, np):
    _msg = mo.md("""
    ## Definição da aleatoriedade:
    Vamos usar um número fixo garantindo consistência na visualização da codificação de linha
    - **seed = 42**: Número usado como semente de aleatoriedade para resultados reproduzíveis
    - **rng = np.random.default_rng(seed)**: Raíz geradora
    - **bits = rng.integers(0, 2, size=Nb)**: Bits gerados aleatoriamente
    """)
    seed = 42                           # Número usado como semente de aleatoriedade para resultados reproduzíveis
    rng = np.random.default_rng(seed)   # Raíz geradora 
    bits = rng.integers(0, 2, size=Nb)  # Geração dos bits
    _msg
    return (bits,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Definição de Funções
    ### Função de codificação de linha:
    *encode_bits(bits, codi)*: Retorna uma lista de mesmo tamanho do que a lista de bits com a codificação esperada, dentre as 3 codificações relevantes.

    codi = {polar, on_off, bipolar}

    ---

    ### Função de geração de pulso:
    *make_pulse(pulse_name)*: Retorna um dos 3 pulsos escolhidos.

    pulse_name = {rect_Tb, rect_Tb_half, sine_half}

    ---

    ### Função de geração de trem de pulsos:
    *pulse_train(impulses, pulse)*: Recebe os bits gerados e gera uma sequência de pulsos com essa ordem.

    pulse = {make_pulse(rect_Tb), make_pulse(rect_Tb_half), make_pulse(sine_half)}

    ---

    ### Função para calcular PSD com Welch
    *welch_psd_db(signal)*: Retorna a estimação da PSD  do sinal por Welch, ao passar-se o sinal.

    signal pode ser qualquer combinação de codificação de linha com pulso dentre as 9 possíveis.

    ---

    ### Função para estimar o primeiro valor nulo na frequência
    *estimate_null(pulse)*: Dado um pulso, estima-se o primeiro nulo.

    ---
    """)
    return


@app.cell
def _(N, T, Tb, Tb_s, fs_hz, largura_pulso, np, t, welch):
    def encode_bits(bits, codi):
        if codi == "polar":
            return np.where(bits == 1, 1.0, -1.0)
        if codi == "on_off":
            return bits.astype(float)
        if codi =="bipolar":
            symbols = np.zeros(len(bits), dtype=float)
            current = 1.0
            for i, b in enumerate(bits):
                if b == 1:
                    symbols[i] = current
                    current *= -1.0
            return symbols

    def make_pulse(pulse_name):
        _t = (np.arange(N) - (N - 1) / 2.0) / fs_hz
        if pulse_name == "rect_Tb":
            np.where(np.abs(t) <= largura_pulso, Tb/2, 0)
        elif pulse_name == "rect_Tb_half":
            np.where(np.abs(t) <= largura_pulso, (Tb/2)/2, 0)
        elif pulse_name == "sine_half":
            p = np.zeros(N, dtype=float)
            _mask = np.abs(_t) <= (Tb_s / 2.0)
            p[_mask] = np.cos(np.pi * _t[_mask] / Tb_s)
    
    def pulse_train(symbols, pulse):
        x = np.zeros(len(symbols) * N)
        x[::N] = symbols
        y = np.convolve(x, pulse, mode="full")
        t_y = (np.arange(len(y)) - (len(pulse) - 1) / 2.0) * T
        return x, y, t_y

    def welch_psd_db(signal):
        nperseg = min(4096, len(signal))
        f, Syy = welch(
            signal,
            fs=fs_hz,
            nperseg=nperseg,
            return_onesided=False,
            detrend=False,
            scaling="density",
        )
        f = np.fft.fftshift(f)
        Syy = np.fft.fftshift(Syy)
        Syy_db = 10 * np.log10(np.maximum(Syy, 1e-14))
        return f, Syy_db

    def estimate_first_null_from_pulse(pulse):
        nfft = 2**16
        P = np.fft.fft(pulse, n=nfft)
        f = np.fft.fftfreq(nfft, d=1 / fs_hz)
        mask = f >= 0
        f_pos = f[mask]
        P_pos = np.abs(P[mask])
        ref = np.max(P_pos)
        idx = np.where((f_pos > 0) & (P_pos <= ref * 1e-3))[0]
        return float(f_pos[idx[0]]) if len(idx) else float("nan")

    return (
        encode_bits,
        estimate_first_null_from_pulse,
        make_pulse,
        welch_psd_db,
    )


@app.cell
def _(Tb):
    pulse_widths = {
        "rect_Tb_half": Tb / 2,
        "rect_Tb": Tb,
        "sine_half": Tb,
    }
    pulse_labels = {
        "rect_Tb_half": r"$\Pi(2t/T_b)$",
        "rect_Tb": r"$\Pi(t/T_b)$",
        "sine_half": r"$\sin(\pi t/T_b)$",
    }
    return


@app.cell
def _(
    bits,
    build_waveform,
    encode_bits,
    estimate_first_null_from_pulse,
    make_pulse,
    pulses,
    schemes,
    welch_psd_db,
):
    results = {}
    for _scheme in schemes:
        _symbols = encode_bits(bits, _scheme)
        results[_scheme] = {}
        for _pulse_name in pulses:
            _pulse = make_pulse(_pulse_name)
            _, _signal, _time = build_waveform(_symbols, _pulse)
            _freq, _psd_db = welch_psd_db(_signal)
            results[_scheme][_pulse_name] = {
                "signal": _signal,
                "time": _time,
                "freq": _freq,
                "psd_db": _psd_db,
                "dc_mean": float(_signal.mean()),
                "first_null_hz": estimate_first_null_from_pulse(_pulse),
            }
    return


@app.cell
def _():
    import marimo as mo

    return (mo,)


@app.cell
def _():
    import numpy as np
    import matplotlib.pyplot as plt
    import scipy as sp

    return (np,)


if __name__ == "__main__":
    app.run()
