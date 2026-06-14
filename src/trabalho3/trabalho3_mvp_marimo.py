import marimo

__generated_with = "0.23.8"
app = marimo.App(width="medium")


@app.cell
def imports_c01():
    """Importa as bibliotecas usadas no app."""
    import marimo as mo
    import matplotlib.pyplot as plt
    import numpy as np
    from pathlib import Path as path
    import shutil
    from scipy.special import erfc

    return erfc, mo, np, path, plt, shutil


@app.cell
def title_c02(mo):
    """Mostra a introducao do trabalho 3."""
    mo.md(
        r"""
    # Trabalho 3 - MVP em Marimo

    Stub inicial para a simulacao de um sistema multicarrier.
    A estrutura segue o mesmo padrao do trabalho 2, mas com foco em OFDM,
    mapeamento por subportadoras, prefixo ciclico e canal AWGN.

    TODOs principais:
    - inserir canal multipercurso
    - adicionar estimacao/equalizacao por piloto
    - comparar diferentes tamanhos de FFT e CP
    """
    )
    return


@app.cell
def params_c03(path):
    """Define os parametros basicos da simulacao."""
    n_fft = 64
    cp_len = 16
    ebn0_points = [0, 4, 8, 12, 16, 20, 24]
    modulation_cases = [("psk", 4), ("psk", 8), ("qam", 4), ("qam", 16)]
    num_bits_target = 200_000
    output_path = path("output/trabalho3_stub")
    return (
        cp_len,
        ebn0_points,
        modulation_cases,
        n_fft,
        num_bits_target,
        output_path,
    )


@app.cell
def gray_code_c04():
    """Cria funcoes auxiliares de codificacao Gray."""

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
def mapping_helpers_c05(gray_to_int, int_to_gray, np):
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
        return np.exp(1j * 2 * np.pi * np.arange(m) / m)

    def bits_to_symbols(bits, kind, m):
        """Mapeia bits para simbolos com Gray coding."""
        b = int(np.log2(m))
        blocks = bits.reshape(-1, b)
        ints = blocks.dot(1 << np.arange(b - 1, -1, -1))
        ints = np.array([int_to_gray(int(x)) for x in ints])
        const = qam_constellation(m) if kind == "qam" else psk_constellation(m)
        return const[ints], const, b

    def symbols_to_bits(symbols, const, b):
        """Decide simbolos por menor distancia e volta para bits."""
        distances = np.abs(symbols.reshape(-1, 1) - const.reshape(1, -1)) ** 2
        idx = np.argmin(distances, axis=1)
        ints = np.array([gray_to_int(int(x)) for x in idx])
        bits = ((ints[:, None] & (1 << np.arange(b - 1, -1, -1))) > 0).astype(int)
        return bits.reshape(-1)

    return bits_to_symbols, symbols_to_bits


@app.cell
def multicarrier_helpers_c06(np):
    """Cria helpers simples para OFDM."""

    def ofdm_modulate(symbols, n_fft, cp_len):
        """Empacota simbolos em blocos OFDM com prefixo ciclico."""
        pad = (-len(symbols)) % n_fft
        if pad:
            symbols = np.concatenate([symbols, np.zeros(pad, dtype=complex)])
        frames = symbols.reshape(-1, n_fft)
        time_domain = np.fft.ifft(frames, axis=1)
        with_cp = np.concatenate([time_domain[:, -cp_len:], time_domain], axis=1)
        return with_cp.reshape(-1)

    def ofdm_demodulate(samples, n_fft, cp_len):
        """Remove o prefixo ciclico e retorna os simbolos por FFT."""
        frame_len = n_fft + cp_len
        pad = (-len(samples)) % frame_len
        if pad:
            samples = np.concatenate([samples, np.zeros(pad, dtype=complex)])
        frames = samples.reshape(-1, frame_len)
        no_cp = frames[:, cp_len:]
        freq_domain = np.fft.fft(no_cp, axis=1)
        return freq_domain.reshape(-1)

    def awgn(signal, ebn0_db, bits_per_symbol, rng):
        """Adiciona ruido branco gaussiano com SNR aproximado."""
        ebn0_lin = 10 ** (ebn0_db / 10)
        snr_lin = ebn0_lin * bits_per_symbol
        signal_power = float(np.mean(np.abs(signal) ** 2))
        noise_power = signal_power / max(snr_lin, 1e-12)
        sigma = np.sqrt(noise_power / 2)
        noise = sigma * (rng.standard_normal(signal.size) + 1j * rng.standard_normal(signal.size))
        return signal + noise

    return awgn, ofdm_demodulate, ofdm_modulate


@app.cell
def simulate_link_c07(bits_to_symbols, np, ofdm_demodulate, ofdm_modulate, symbols_to_bits, awgn):
    """Executa uma simulacao OFDM simplificada."""

    def simulate_link(kind, m, ebn0_db, num_bits_target, n_fft, cp_len, rng):
        """Simula uma cadeia OFDM com canal AWGN e sincronismo ideal.

        TODO: trocar o canal flat por multipercurso e inserir equalizacao.
        """
        b = int(np.log2(m))
        num_bits = int(np.ceil(num_bits_target / b) * b)
        bits_tx = rng.integers(0, 2, size=num_bits)
        symbols_tx, const, b = bits_to_symbols(bits_tx, kind, m)

        tx = ofdm_modulate(symbols_tx, n_fft, cp_len)
        rx = awgn(tx, ebn0_db, b, rng)
        symbols_rx = ofdm_demodulate(rx, n_fft, cp_len)[: len(symbols_tx)]
        bits_rx = symbols_to_bits(symbols_rx, const, b)

        ber = float(np.mean(bits_tx != bits_rx))
        return ber, symbols_tx, symbols_rx, const

    return (simulate_link,)


@app.cell
def collect_results_c08(
    ebn0_points,
    modulation_cases,
    n_fft,
    num_bits_target,
    cp_len,
    simulate_link,
):
    """Executa o bloco principal de simulacao e guarda os resultados."""
    rng = np.random.default_rng()
    results = {}

    for _kind, _m in modulation_cases:
        ber_curve = []
        example_tx = None
        example_rx = None
        example_const = None

        for _ebn0_db in ebn0_points:
            ber, symbols_tx, symbols_rx, const = simulate_link(
                _kind,
                _m,
                _ebn0_db,
                num_bits_target,
                n_fft,
                cp_len,
                rng,
            )
            ber_curve.append(ber)
            example_tx = symbols_tx
            example_rx = symbols_rx
            example_const = const

        results[(_kind, _m)] = {
            "ber": np.array(ber_curve),
            "example_tx": example_tx,
            "example_rx": example_rx,
            "example_const": example_const,
        }
    return (results,)


@app.cell
def plot_helpers_c09(output_path, shutil):
    """Prepara saida e helpers de desenho."""
    if output_path.exists():
        shutil.rmtree(output_path)
    output_path.mkdir(parents=True, exist_ok=True)

    def draw_ideal_reference(ax_c09, const_c09):
        """Desenha os pontos ideais da constelacao."""
        ax_c09.scatter(
            const_c09.real,
            const_c09.imag,
            s=42,
            facecolors="none",
            edgecolors="white",
            linewidths=0.9,
            label="Ideal",
            zorder=3,
        )

    def draw_constellation(ax_c09, points_c09, const_c09, title_c09, color_c09, label_c09):
        """Desenha uma constelacao com referencia ideal."""
        ax_c09.scatter(points_c09.real, points_c09.imag, s=18, alpha=0.65, color=color_c09, label=label_c09)
        draw_ideal_reference(ax_c09, const_c09)
        ax_c09.axhline(0, linewidth=0.8, color="0.35")
        ax_c09.axvline(0, linewidth=0.8, color="0.35")
        ax_c09.grid(True, alpha=0.3)
        ax_c09.set_aspect("equal", adjustable="box")
        ax_c09.set_title(title_c09)
        ax_c09.set_xlabel("I")
        ax_c09.set_ylabel("Q")

    return draw_constellation, draw_ideal_reference


@app.cell
def plot_ber_c10(ebn0_points, modulation_cases, output_path, plt, results):
    """Gera a curva de BER do stub."""
    ber_path = output_path / "ber"
    ber_path.mkdir(parents=True, exist_ok=True)

    fig_ber, ax_ber = plt.subplots(figsize=(9, 5))
    for _kind, _m in modulation_cases:
        data = results[(_kind, _m)]
        ax_ber.semilogy(
            ebn0_points,
            data["ber"],
            marker="o",
            linewidth=1.6,
            label=f"{_kind.upper()} M={_m}",
        )

    ax_ber.set_xlabel("Eb/N0 (dB)")
    ax_ber.set_ylabel("BER")
    ax_ber.set_ylim(1e-5, 1)
    ax_ber.set_title("BER - sistema multicarrier (stub)")
    ax_ber.grid(True, which="both", alpha=0.3)
    ax_ber.legend(fontsize=8)
    fig_ber.tight_layout()
    fig_ber.savefig(ber_path / "BER_MULTICARRIER_STUB.png", dpi=150)
    plt.show()
    plt.close(fig_ber)
    return


@app.cell
def plot_constellation_c11(draw_constellation, output_path, plt, results):
    """Mostra uma constelacao exemplo do link."""
    const_path = output_path / "constellation"
    const_path.mkdir(parents=True, exist_ok=True)

    for (_kind, _m), data in results.items():
        fig_const, ax_const = plt.subplots(figsize=(5.2, 5.2))
        draw_constellation(
            ax_const,
            data["example_rx"],
            data["example_const"],
            f"RX - {_kind.upper()} M={_m}",
            "darkorange",
            "RX",
        )
        ax_const.legend(fontsize=8)
        fig_const.tight_layout()
        fig_const.savefig(const_path / f"CONST_RX_{_kind.upper()}_M{_m}.png", dpi=150)
        plt.show()
        plt.close(fig_const)
    return


if __name__ == "__main__":
    app.run()
