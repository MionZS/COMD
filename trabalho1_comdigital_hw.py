import marimo

__generated_with = "0.23.0"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo
    import numpy as np
    import matplotlib.pyplot as plt
    from scipy.signal import welch

    return mo, np, plt, welch


@app.cell
def _(mo):
    mo.md(r"""
    # Trabalho Computacional 1 -- Comunicacao Digital

    Este notebook implementa:
    ## Codigos de linha:
    - **Polar**,
    - **On-off**,
    - **Bipolar**;

    ---
    ## Pulsos:
    - \( \Pi(2t/T_b) \) - Meio-pulso retangular,
    - \( \Pi(t/T_b) \) - Pulso retangular,
    - \( \sin(\pi t/T_b) \) - Meia-senoide;

    ---
    ## Analises
    - Graficos no dominio do tempo em \( [0, 10T_b) \);
    - PSDs por **Welch** em dB/Hz.
    """)
    return


@app.cell
def _(mo):
    _msg = mo.md(r"""
    # Definicao de constantes:
    - **Tb = 1**: Intervalo de bit | segundo
    - **fs = 10**: Frequencia de amostragem | hertz
    - **Nb = 10^5**: Numero de bits analisados
    - **N = Tb*fs = 10**: Amostras por bit
    """)
    Tb = 1.0
    fs = 10.0
    T = 1.0 / fs
    Nb = 10**5
    N = int(round(Tb * fs))
    _msg
    return N, Nb, T, Tb, fs


@app.cell
def _(Nb, mo, np):
    _msg = mo.md("""
    ## Definicao da aleatoriedade:
    - **seed = 42**: Semente para resultados reproduziveis
    - **rng = np.random.default_rng(seed)**: Gerador
    - **bits = rng.integers(0, 2, size=Nb)**: Bits aleatorios
    """)
    seed = 42
    rng = np.random.default_rng(seed)
    bits = rng.integers(0, 2, size=Nb)
    _msg
    return bits


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Definicao de Funcoes
    - *encode_bits(bits, codi)*
    - *make_pulse(pulse_name)*
    - *pulse_train(symbols, pulse)*
    - *welch_psd_db(signal)*
    - *estimate_first_null_from_pulse(pulse)*
    """)
    return


@app.cell
def _(N, T, Tb, fs, np, welch):
    def encode_bits(bits, codi):
        if codi == "polar":
            return np.where(bits == 1, 1.0, -1.0)
        if codi == "on_off":
            return bits.astype(float)
        if codi == "bipolar":
            symbols = np.zeros(len(bits), dtype=float)
            current = 1.0
            for i, b in enumerate(bits):
                if b == 1:
                    symbols[i] = current
                    current *= -1.0
            return symbols
        raise ValueError(f"Codigo desconhecido: {codi}")

    def make_pulse(pulse_name):
        _t = (np.arange(N) - (N - 1) / 2.0) / fs
        if pulse_name == "rect_Tb":
            p = np.where(np.abs(_t) <= (Tb / 2.0), 1.0, 0.0)
        elif pulse_name == "rect_Tb_half":
            p = np.zeros(N, dtype=float)
            _half_len = max(1, N // 2)
            _start = (N - _half_len) // 2
            _end = _start + _half_len
            p[_start:_end] = 1.0
        elif pulse_name == "sine_half":
            p = np.zeros(N, dtype=float)
            _mask = np.abs(_t) <= (Tb / 2.0)
            p[_mask] = np.cos(np.pi * _t[_mask] / Tb)
        else:
            raise ValueError(f"Pulso desconhecido: {pulse_name}")
        return p

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
            fs=fs,
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
        f = np.fft.fftfreq(nfft, d=1 / fs)
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
        pulse_train,
        welch_psd_db,
    )


@app.cell
def _(
    bits,
    encode_bits,
    estimate_first_null_from_pulse,
    make_pulse,
    pulse_train,
    welch_psd_db,
):
    schemes = {
        "polar": "Polar",
        "on_off": "On-Off",
        "bipolar": "Bipolar (AMI)",
    }

    pulses = {
        "rect_Tb_half": r"$\Pi(2t/T_b)$",
        "rect_Tb": r"$\Pi(t/T_b)$",
        "sine_half": r"$\sin(\pi t/T_b)$",
    }

    results = {}
    for _scheme in schemes:
        _symbols = encode_bits(bits, _scheme)
        results[_scheme] = {}
        for _pulse_name in pulses:
            _pulse = make_pulse(_pulse_name)
            _, _signal, _time = pulse_train(_symbols, _pulse)
            _freq, _psd_db = welch_psd_db(_signal)
            results[_scheme][_pulse_name] = {
                "signal": _signal,
                "time": _time,
                "freq": _freq,
                "psd_db": _psd_db,
                "dc_mean": float(_signal.mean()),
                "first_null_hz": estimate_first_null_from_pulse(_pulse),
            }
    return pulses, results, schemes


@app.cell
def _(Tb, plt, pulses, results, schemes):
    NUM_BITS_TO_SHOW = 10
    _max_pulse_width = Tb
    _time_margin = 0.08 * _max_pulse_width
    _time_limit = NUM_BITS_TO_SHOW * Tb + _time_margin
    _fig, _axes = plt.subplots(3, 3, figsize=(15, 9), sharex=True)

    _scheme_keys = list(schemes.keys())
    _pulse_keys = list(pulses.keys())

    for _i, _scheme in enumerate(_scheme_keys):
        for _j, _pulse_name in enumerate(_pulse_keys):
            _ax = _axes[_i, _j]
            _time = results[_scheme][_pulse_name]["time"]
            _signal = results[_scheme][_pulse_name]["signal"]
            _mask = (_time >= 0) & (_time < _time_limit)
            _ax.plot(_time[_mask], _signal[_mask], linewidth=1.6)
            _ax.grid(True, alpha=0.35)
            if _i == 0:
                _ax.set_title(pulses[_pulse_name])
            _ax.set_ylabel(f"{schemes[_scheme]}\nAmplitude")
            if _i == 2:
                _ax.set_xlabel("Tempo [s]")

    _fig.suptitle("Codigos de linha no dominio do tempo (0 a 10Tb)")
    plt.tight_layout()
    plt.show()
    return


@app.cell
def _(Tb, np, plt):
    _pulse_widths = {
        "rect_Tb_half": Tb / 2,
        "rect_Tb": Tb,
        "sine_half": Tb,
    }
    _pulse_labels = {
        "rect_Tb_half": r"$\Pi(2t/T_b)$",
        "rect_Tb": r"$\Pi(t/T_b)$",
        "sine_half": r"$\sin(\pi t/T_b)$",
    }

    _max_width = max(_pulse_widths.values())
    _x_margin = 0.08 * _max_width
    _x_min = -_max_width / 2.0 - _x_margin
    _x_max = _max_width / 2.0 + _x_margin

    _t = np.linspace(_x_min, _x_max, 1000)
    _pulse_shapes = {
        "rect_Tb_half": (np.abs(_t) <= (_pulse_widths["rect_Tb_half"] / 2.0)).astype(float),
        "rect_Tb": (np.abs(_t) <= (_pulse_widths["rect_Tb"] / 2.0)).astype(float),
        "sine_half": np.where(
            np.abs(_t) <= (_pulse_widths["sine_half"] / 2.0),
            np.cos(np.pi * _t / Tb),
            0.0,
        ),
    }

    _fig, _ax = plt.subplots(figsize=(7.2, 3.4))
    for _pulse_key in ["rect_Tb_half", "rect_Tb", "sine_half"]:
        _ax.plot(
            _t,
            _pulse_shapes[_pulse_key],
            linewidth=1.6,
            label=f"p(t)={_pulse_labels[_pulse_key]}",
        )

    _ax.set_xlim(_x_min, _x_max)
    _ax.set_ylim(-0.02, 1.05)
    _ax.set_xlabel("Tempo (s)")
    _ax.set_ylabel("Amplitude")
    _ax.grid(True, alpha=0.3)
    _ax.legend(loc="lower right")
    plt.tight_layout()
    plt.show()
    return


@app.cell
def _(fs, plt, pulses, results, schemes):
    _fig, _axes = plt.subplots(3, 3, figsize=(15, 9), sharex=True, sharey=True)

    _scheme_keys = list(schemes.keys())
    _pulse_keys = list(pulses.keys())

    for _i, _scheme in enumerate(_scheme_keys):
        for _j, _pulse_name in enumerate(_pulse_keys):
            _ax = _axes[_i, _j]
            _freq = results[_scheme][_pulse_name]["freq"]
            _psd_db = results[_scheme][_pulse_name]["psd_db"]
            _ax.plot(_freq, _psd_db, linewidth=1.3)
            _ax.grid(True, alpha=0.35)
            _ax.set_xlim(-fs / 2, fs / 2)
            _ax.set_ylim(-90, 10)

            if _i == 0:
                _ax.set_title(pulses[_pulse_name])
            if _j == 0:
                _ax.set_ylabel(f"{schemes[_scheme]}\nPSD [dB/Hz]")
            if _i == 2:
                _ax.set_xlabel("Frequencia [Hz]")

    _fig.suptitle("Densidade espectral de potencia via Welch")
    plt.tight_layout()
    plt.show()
    return


@app.cell
def _(mo, pulses, results, schemes):
    rows = []
    for scheme_key, scheme_label in schemes.items():
        for pulse_key, pulse_label in pulses.items():
            data = results[scheme_key][pulse_key]
            rows.append(
                {
                    "Sinalizacao": scheme_label,
                    "Pulso": pulse_label,
                    "Media (indicador DC)": round(data["dc_mean"], 6),
                    "1o nulo estimado [Hz]": round(data["first_null_hz"], 6),
                }
            )

    mo.ui.table(rows)
    return


if __name__ == "__main__":
    app.run()
