import marimo

__generated_with = "0.23.8"
app = marimo.App(width="medium")


@app.cell
def imports():
    """Importa as bibliotecas usadas no notebook."""
    import marimo as mo
    import matplotlib.pyplot as plt
    import numpy as np
    from pathlib import Path as path
    import shutil
    from scipy.special import erfc

    return erfc, mo, np, path, plt, shutil


@app.cell
def title(mo):
    """Mostra a introducao do notebook."""
    mo.md(r"""
    # Trabalho 2 - MVP em Marimo v3

    Versao simples e direta da simulacao de BER em banda passante.
    Mantem a mesma cadeia matematica do modelo, sem protecoes extras.
    """)
    return ()


@app.cell
def params(path):
    """Define os parametros fixos da simulacao."""
    fc = 10.0
    os = 4
    sps = 16
    alpha = 0.15
    ebn0_points = [0, 4, 8, 12, 16, 20, 24]
    modulation_cases = [("psk", 2), ("psk", 4), ("psk", 8), ("psk", 16), ("qam", 4), ("qam", 16), ("qam", 64)]
    pulse_names = ["nrz", "rrc"]
    num_symbols_target = 20_000
    output_path = path("output/trabalho2_v3")
    return (
        alpha,
        ebn0_points,
        fc,
        modulation_cases,
        num_symbols_target,
        os,
        output_path,
        pulse_names,
        sps,
    )


@app.cell
def gray_code():
    """Cria as funcoes de codificacao Gray."""
    def int_to_gray(n):
        """Converte inteiro binario para Gray."""
        return n ^ (n >> 1)

    def gray_to_int(g):
        """Converte Gray para inteiro binario."""
        n = 0
        while g:
            n ^= g
            g >>= 1
        return n

    return gray_to_int, int_to_gray


@app.cell
def mapping_helpers(gray_to_int, int_to_gray, np):
    """Cria constelacoes e funcoes de mapeamento."""
    def qam_constellation(m):
        """Gera uma constelacao QAM normalizada."""
        side = int(np.sqrt(m))
        levels = np.arange(-(side - 1), side, 2)
        xv, yv = np.meshgrid(levels, levels[::-1])
        const = xv.flatten() + 1j * yv.flatten()
        return const / np.sqrt(np.mean(np.abs(const) ** 2))

    def psk_constellation(m):
        """Gera uma constelacao PSK normalizada."""
        const = np.exp(1j * 2 * np.pi * np.arange(m) / m)
        return const / np.sqrt(np.mean(np.abs(const) ** 2))

    def bits_to_symbols(bits, kind, m):
        """Mapeia bits para simbolos usando Gray coding."""
        b = int(np.log2(m))
        blocks = bits.reshape(-1, b)
        ints = blocks.dot(1 << np.arange(b - 1, -1, -1))
        ints = np.array([int_to_gray(int(x)) for x in ints])
        const = qam_constellation(m) if kind == "qam" else psk_constellation(m)
        return const[ints], const, b

    def symbols_to_bits(symbols, const, b):
        """Decide simbolos e volta para bits."""
        distances = np.abs(symbols.reshape(-1, 1) - const.reshape(1, -1)) ** 2
        idx = np.argmin(distances, axis=1)
        ints = np.array([gray_to_int(int(x)) for x in idx])
        bits = ((ints[:, None] & (1 << np.arange(b - 1, -1, -1))) > 0).astype(int)
        return bits.reshape(-1)

    return bits_to_symbols, symbols_to_bits


@app.cell
def pulse_shape(np):
    """Cria os pulsos de transmissao."""
    def pulse_coeffs(name, alpha, sps):
        """Gera pulso NRZ ou RRC normalizado."""
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
def ber_theory(erfc, np):
    """Calcula a curva teorica de BER."""
    def theoretical_ber(kind, m, ebn0_db):
        """Retorna a BER teorica para QAM ou PSK."""
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
def simulate_link(bits_to_symbols, np, pulse_coeffs, symbols_to_bits):
    """Simula a cadeia transmissor-canal-receptor."""
    def simulate_link(kind, m, pulse_name, ebn0_db, num_symbols, rng, alpha, fc, os, sps):
        """Executa uma simulacao unica para uma combinacao de parametros."""
        bits_tx = rng.integers(0, 2, size=num_symbols * int(np.log2(m)))
        symbols_tx, const, b = bits_to_symbols(bits_tx, kind, m)

        pulse = pulse_coeffs(pulse_name, alpha, sps)
        upsampled = np.zeros(len(symbols_tx) * sps, dtype=complex)
        upsampled[::sps] = symbols_tx
        shaped = np.convolve(upsampled, pulse, mode="full")

        fs = os * fc
        t = np.arange(len(shaped)) / fs
        carrier = 2 * np.pi * fc * t
        tx = np.sqrt(2) * (shaped.real * np.cos(carrier) - shaped.imag * np.sin(carrier))

        ebn0_lin = 10 ** (ebn0_db / 10)
        sigma = np.sqrt(1 / (2 * b * ebn0_lin))
        rx = tx + sigma * rng.standard_normal(tx.size)

        i = np.sqrt(2) * rx * np.cos(carrier)
        q = -np.sqrt(2) * rx * np.sin(carrier)
        bb_rx = i + 1j * q

        mf = pulse[::-1].conj()
        filtered = np.convolve(bb_rx, mf, mode="full")
        offset = len(pulse) - 1
        sample_idx = offset + np.arange(len(symbols_tx)) * sps
        symbols_rx = filtered[sample_idx]

        bits_rx = symbols_to_bits(symbols_rx, const, b)
        ber = np.mean(bits_tx != bits_rx)
        return ber, symbols_tx, symbols_rx, const

    return (simulate_link,)


@app.cell
def collect_results(
    alpha,
    ebn0_points,
    fc,
    modulation_cases,
    np,
    num_symbols_target,
    os,
    pulse_names,
    simulate_link,
    sps,
    theoretical_ber,
):
    """Executa todas as simulacoes e organiza os resultados."""
    rng = np.random.default_rng()
    results = {}

    for _pulse_name in pulse_names:
        pulse_results = {}
        for _kind, _m in modulation_cases:
            ber_curve = []
            example_tx = None
            rx_by_ebn0 = []
            example_const = None

            for _ebn0_db in ebn0_points:
                ber, symbols_tx, symbols_rx, _const = simulate_link(_kind, _m, _pulse_name, _ebn0_db, num_symbols_target, rng, alpha, fc, os, sps)
                ber_curve.append(ber)
                rx_by_ebn0.append(symbols_rx)
                if _ebn0_db == ebn0_points[-1]:
                    example_tx = symbols_tx
                    example_const = _const

            pulse_results[(_kind, _m)] = {
                "ber": np.array(ber_curve),
                "theory": np.array([theoretical_ber(_kind, _m, eb) for eb in ebn0_points]),
                "example_tx": example_tx,
                "rx_by_ebn0": rx_by_ebn0,
                "example_const": example_const,
            }
        results[_pulse_name] = pulse_results
    return (results,)


@app.cell
def plot_helpers(output_path, shutil):
    """Prepara a saida e cria os helpers de desenho."""
    if output_path.exists():
        shutil.rmtree(output_path)
    output_path.mkdir(parents=True, exist_ok=True)

    def draw_ideal_reference(ax_c06, const_c06):
        """Desenha os pontos ideais da constelacao."""
        ax_c06.scatter(
            const_c06.real,
            const_c06.imag,
            s=42,
            facecolors="none",
            edgecolors="white",
            linewidths=0.9,
            label="Ideal",
            zorder=3,
        )

    def draw_constellation(ax_c06, points_c06, const_c06, title_c06, color_c06, label_c06):
        """Desenha uma constelacao com referencia ideal."""
        ax_c06.scatter(points_c06.real, points_c06.imag, s=18, alpha=0.65, color=color_c06, label=label_c06)
        draw_ideal_reference(ax_c06, const_c06)
        ax_c06.axhline(0, linewidth=0.8, color="0.35")
        ax_c06.axvline(0, linewidth=0.8, color="0.35")
        ax_c06.grid(True, alpha=0.3)
        ax_c06.set_aspect("equal", adjustable="box")
        ax_c06.set_title(title_c06)
        ax_c06.set_xlabel("I (componente em fase)")
        ax_c06.set_ylabel("Q (componente em quadratura)")

    return draw_constellation, draw_ideal_reference


@app.cell
def plot_ber(
    ebn0_points,
    modulation_cases,
    output_path,
    plt,
    pulse_names,
    results,
):
    """Gera e exibe os graficos de BER."""
    ber_figures = []

    for _pulse_name in pulse_names:
        pulse_path = output_path / _pulse_name.upper()
        ber_path = pulse_path / "ber"
        ber_path.mkdir(parents=True, exist_ok=True)

        fig_ber_c06, ax_ber_c06 = plt.subplots(figsize=(9, 5))
        for _kind, _m in modulation_cases:
            data = results[_pulse_name][(_kind, _m)]
            sim_line = ax_ber_c06.semilogy(ebn0_points, data["ber"], marker="o", linewidth=1.6, label=f"SIM {_kind.upper()} M={_m}")[0]
            ax_ber_c06.semilogy(ebn0_points, data["theory"], linestyle="--", linewidth=1.2, alpha=0.85, color=sim_line.get_color(), label=f"TH {_kind.upper()} M={_m}")
        ax_ber_c06.set_xlabel("Eb/N0 (dB)")
        ax_ber_c06.set_ylabel("BER")
        ax_ber_c06.set_ylim(1e-5, 1)
        ax_ber_c06.set_title(f"BER comparativa - pulso {_pulse_name.upper()}")
        ax_ber_c06.grid(True, which="both", alpha=0.3)
        ax_ber_c06.legend(fontsize=8)
        fig_ber_c06.tight_layout()
        fig_ber_c06.savefig(ber_path / f"BER_{_pulse_name.upper()}.png", dpi=150)
        ber_figures.append(fig_ber_c06)
        plt.show()
        plt.close(fig_ber_c06)
    return ()


@app.cell
def plot_rx(
    draw_constellation,
    ebn0_points,
    modulation_cases,
    np,
    output_path,
    plt,
    pulse_names,
    results,
):
    """Gera e exibe as constelacoes recebidas."""
    for _pulse_name in pulse_names:
        _pulse_path = output_path / _pulse_name.upper()
        _rx_path = _pulse_path / "rx"
        _rx_path.mkdir(parents=True, exist_ok=True)

        for _kind, _m in modulation_cases:
            _case_data = results[_pulse_name][(_kind, _m)]
            _const = _case_data["example_const"]
            _rx_samples_by_snr = _case_data["rx_by_ebn0"]
            if _const is None:
                continue

            for _ebn0_db, _rx_samples in zip(ebn0_points, _rx_samples_by_snr):
                _extent = max(
                    float(np.max(np.abs(_rx_samples.real))),
                    float(np.max(np.abs(_rx_samples.imag))),
                    float(np.max(np.abs(_const.real))),
                    float(np.max(np.abs(_const.imag))),
                    1.0,
                ) * 1.15

                fig_rx, ax_rx = plt.subplots(figsize=(5.2, 5.2))
                draw_constellation(ax_rx, _rx_samples, _const, f"Recebido - {_kind.upper()} M={_m} - Eb/N0={_ebn0_db} dB", "darkorange", "RX")
                ax_rx.set_xlim(-_extent, _extent)
                ax_rx.set_ylim(-_extent, _extent)
                ax_rx.legend(fontsize=8)
                fig_rx.tight_layout()
                fig_rx.savefig(_rx_path / f"CONST_RX_{_kind.upper()}_M{_m}_EBN0_{_ebn0_db}.png", dpi=150)
                plt.show()
                plt.close(fig_rx)
    return ()


@app.cell
def plot_heatmap(
    draw_ideal_reference,
    ebn0_points,
    modulation_cases,
    np,
    output_path,
    plt,
    pulse_names,
    results,
):
    """Gera e exibe os mapas de calor das constelacoes recebidas."""
    for _pulse_name in pulse_names:
        _pulse_path = output_path / _pulse_name.upper()
        _heatmap_path = _pulse_path / "heatmap"
        _heatmap_path.mkdir(parents=True, exist_ok=True)

        for _kind, _m in modulation_cases:
            _case_data = results[_pulse_name][(_kind, _m)]
            _const = _case_data["example_const"]
            _rx_samples_by_snr = _case_data["rx_by_ebn0"]
            if _const is None:
                continue

            for _ebn0_db, _rx_samples in zip(ebn0_points, _rx_samples_by_snr):
                _extent = max(
                    float(np.max(np.abs(_rx_samples.real))),
                    float(np.max(np.abs(_rx_samples.imag))),
                    float(np.max(np.abs(_const.real))),
                    float(np.max(np.abs(_const.imag))),
                    1.0,
                ) * 1.15

                fig_heat, ax_heat = plt.subplots(figsize=(5.2, 5.2))
                heat = ax_heat.hist2d(
                    _rx_samples.real,
                    _rx_samples.imag,
                    bins=120,
                    range=[[-_extent, _extent], [-_extent, _extent]],
                    cmap="magma",
                )
                draw_ideal_reference(ax_heat, _const)
                ax_heat.axhline(0, linewidth=0.8, color="0.35")
                ax_heat.axvline(0, linewidth=0.8, color="0.35")
                ax_heat.set_aspect("equal", adjustable="box")
                ax_heat.set_xlim(-_extent, _extent)
                ax_heat.set_ylim(-_extent, _extent)
                ax_heat.set_title(f"Heatmap RX - {_kind.upper()} M={_m} - Eb/N0={_ebn0_db} dB")
                ax_heat.set_xlabel("I (componente em fase)")
                ax_heat.set_ylabel("Q (componente em quadratura)")
                fig_heat.colorbar(heat[3], ax=ax_heat, label="Densidade")
                fig_heat.tight_layout()
                fig_heat.savefig(_heatmap_path / f"CONST_HEAT_{_kind.upper()}_M{_m}_EBN0_{_ebn0_db}.png", dpi=150)
                plt.show()
                plt.close(fig_heat)
    return ()


if __name__ == "__main__":
    app.run()
