import marimo

__generated_with = "0.23.0"
app = marimo.App(
    width="wide",
    layout_file="layouts/trabalho1_comdigital_marimo_copia.slides.json",
)


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
    Tb = mo.ui.number(value=1.0, start=0.1, stop=10.0, step=0.1, label="Tb [s]")
    fs = mo.ui.number(value=10.0, start=2.0, stop=100.0, step=1.0, label="fs [Hz]")
    Nb = mo.ui.number(value=100000, start=1000, stop=500000, step=1000, label="Número de bits")
    seed = mo.ui.number(value=42, start=0, stop=999999, step=1, label="Seed")

    mo.hstack([Tb, fs, Nb, seed], justify="start")
    return Nb, Tb, fs, seed


@app.cell
def _(Nb, Tb, fs, np, seed):
    Tb_s = float(Tb.value)
    fs_hz = float(fs.value)
    T = 1.0 / fs_hz
    N = int(round(Tb_s * fs_hz))
    Nb_bits = int(Nb.value)
    rng = np.random.default_rng(int(seed.value))
    bits = rng.integers(0, 2, size=Nb_bits)
    return N, T, Tb_s, bits, fs_hz


@app.cell
def _(N, T, Tb_s, fs_hz, np, welch):
    def encode_bits(bits, scheme):
        if scheme == "polar":
            return np.where(bits == 1, 1.0, -1.0)
        if scheme == "on_off":
            return bits.astype(float)
        if scheme == "bipolar":
            symbols = np.zeros(len(bits), dtype=float)
            current = 1.0
            for i, b in enumerate(bits):
                if b == 1:
                    symbols[i] = current
                    current *= -1.0
            return symbols
        raise ValueError(f"Esquema desconhecido: {scheme}")

    def make_pulse(pulse_name):
        _t = (np.arange(N) - (N - 1) / 2.0) / fs_hz
        if pulse_name == "rect_Tb_2":
            p = (np.abs(_t) <= (Tb_s / 4.0)).astype(float)
        elif pulse_name == "rect_Tb":
            p = (np.abs(_t) <= (Tb_s / 2.0)).astype(float)
        elif pulse_name == "half_sine":
            p = np.zeros(N, dtype=float)
            _mask = np.abs(_t) <= (Tb_s / 2.0)
            p[_mask] = np.cos(np.pi * _t[_mask] / Tb_s)
        else:
            raise ValueError(f"Pulso desconhecido: {pulse_name}")
        return p

    def build_waveform(symbols, pulse):
        x = np.zeros(len(symbols) * N)
        x[::N] = symbols
        # convolution; use full so pulses don't get truncated
        y = np.convolve(x, pulse, mode="full")
        # shift time origin so pulse centers are shown (align with pulse center)
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
        build_waveform,
        encode_bits,
        estimate_first_null_from_pulse,
        make_pulse,
        welch_psd_db,
    )


@app.cell
def _(
    bits,
    build_waveform,
    encode_bits,
    estimate_first_null_from_pulse,
    make_pulse,
    welch_psd_db,
):
    schemes = {
        "polar": "Polar",
        "on_off": "On-Off",
        "bipolar": "Bipolar (AMI)",
    }

    pulses = {
        "rect_Tb_2": r"$\Pi(2t/T_b)$",
        "rect_Tb": r"$\Pi(t/T_b)$",
        "half_sine": r"$\sin(\pi t/T_b)$",
    }

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
    return pulses, results, schemes


@app.cell
def _(Tb_s, plt, pulses, results, schemes):
    NUM_BITS_TO_SHOW = 10
    _max_pulse_width = Tb_s
    _time_margin = 0.08 * _max_pulse_width
    _time_limit = NUM_BITS_TO_SHOW * Tb_s + _time_margin
    _fig, _axes = plt.subplots(3, 3, figsize=(15, 9), sharex=True)

    _scheme_keys = list(schemes.keys())
    _pulse_keys = list(pulses.keys())

    for _i, _scheme in enumerate(_scheme_keys):
        for _j, _pulse_name in enumerate(_pulse_keys):
            _ax = _axes[_i, _j]
            _time = results[_scheme][_pulse_name]["time"]
            _signal = results[_scheme][_pulse_name]["signal"]
            _mask = _time < _time_limit
            _ax.plot(_time[_mask], _signal[_mask], linewidth=1.6)
            _ax.grid(True, alpha=0.35)
            if _i == 0:
                _ax.set_title(pulses[_pulse_name])
            if _j == 0:
                _ax.set_ylabel(f"{schemes[_scheme]}\nAmplitude")
            if _i == 2:
                _ax.set_xlabel("Tempo [s]")

    _fig.suptitle("Códigos de linha no domínio do tempo (0 a 10Tb)")
    plt.tight_layout()
    plt.show()
    return


@app.cell
def _(Tb_s, np, plt):
    _pulse_widths = {
        "rect_Tb_2": Tb_s / 2,
        "rect_Tb": Tb_s,
        "half_sine": Tb_s,
    }
    _pulse_labels = {
        "rect_Tb_2": r"$\Pi(2t/T_b)$",
        "rect_Tb": r"$\Pi(t/T_b)$",
        "half_sine": r"$\sin(\pi t/T_b)$",
    }

    _max_width = max(_pulse_widths.values())
    _x_margin = 0.08 * _max_width
    _x_min = -_max_width / 2.0 - _x_margin
    _x_max = _max_width / 2.0 + _x_margin

    _t = np.linspace(_x_min, _x_max, 1000)
    _pulse_shapes = {
        "rect_Tb_2": (np.abs(_t) <= (_pulse_widths["rect_Tb_2"] / 2.0)).astype(float),
        "rect_Tb": (np.abs(_t) <= (_pulse_widths["rect_Tb"] / 2.0)).astype(float),
        "half_sine": np.where(
            np.abs(_t) <= (_pulse_widths["half_sine"] / 2.0),
            np.cos(np.pi * _t / Tb_s),
            0.0,
        ),
    }

    _fig, _ax = plt.subplots(figsize=(7.2, 3.4))
    for _pulse_key in ["rect_Tb_2", "rect_Tb", "half_sine"]:
        _ax.plot(
            _t,
            _pulse_shapes[_pulse_key],
            linewidth=1.6,
            label=f"p(t)={_pulse_labels[_pulse_key]}",
        )

    _ax.set_xlim(_x_min, _x_max)
    _ax.set_ylim(-0.02, 1.05)
    _ax.set_xlabel("Time (s)")
    _ax.set_ylabel("Amplitude")
    _ax.set_title("TE903 - TRABALHO COMPUTACIONAL 1, ABRIL DE 2026")
    _ax.grid(True, alpha=0.3)
    _ax.legend(loc="lower right")
    plt.tight_layout()
    plt.show()
    return


@app.cell
def _(fs_hz, plt, pulses, results, schemes):
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
            _ax.set_xlim(-fs_hz / 2, fs_hz / 2)
            _ax.set_ylim(-90, 10)

            if _i == 0:
                _ax.set_title(pulses[_pulse_name])
            if _j == 0:
                _ax.set_ylabel(f"{schemes[_scheme]}\nPSD [dB/Hz]")
            if _i == 2:
                _ax.set_xlabel("Frequência [Hz]")

    _fig.suptitle("Densidade espectral de potência via Welch")
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
                    "Sinalização": scheme_label,
                    "Pulso": pulse_label,
                    "Média (indicador DC)": round(data["dc_mean"], 6),
                    "1º nulo estimado [Hz]": round(data["first_null_hz"], 6),
                }
            )

    mo.ui.table(rows)
    return


if __name__ == "__main__":
    app.run()
