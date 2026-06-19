
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
    # Trabalho 3 - OFDM 16-QAM em Marimo

    Simulacao em banda-base de um sistema OFDM com 32 subportadoras, canal multipercurso, prefixo ciclico minimo, equalizacao ZF e carregamento extremo por descarte das piores portadoras.

    Este notebook reaproveita a estrutura do Trabalho 2: funcoes pequenas, simulacao vetorizada, figuras salvas em `output/`, e mapeamento QAM com decisor por vizinho mais proximo.
    """)
    return


@app.cell
def params(np, path):
    """Define os parametros fixos da simulacao."""
    n_subcarriers = 32
    modulation_order = 16
    bits_per_symbol = int(np.log2(modulation_order))
    h = np.array([0.3, -0.5, 0.0, 1.0, 0.2, -0.3], dtype=float)
    cp_len = len(h) - 1
    snr_db_points = np.arange(0, 31, 2)
    snr_constellation_db = 30
    num_ofdm_symbols = 12_000
    num_ofdm_symbols_constellation = 4_000
    rng_seed = 903_2026
    output_path = path("output/trabalho3_ofdm_16qam")

    return (
        bits_per_symbol,
        cp_len,
        h,
        modulation_order,
        n_subcarriers,
        num_ofdm_symbols,
        num_ofdm_symbols_constellation,
        output_path,
        rng_seed,
        snr_constellation_db,
        snr_db_points,
    )


@app.cell
def gray_code():
    """Cria as funcoes de codificacao Gray, aproveitando a ideia do Trabalho 2."""
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
def qam_helpers(gray_to_int, int_to_gray, np):
    """Cria constelacao 16-QAM, mapeamento e decisao por menor distancia."""
    def qam_constellation_raw(m):
        """Gera uma constelacao QAM quadrada sem normalizacao."""
        side = int(np.sqrt(m))
        if side * side != m:
            raise ValueError("Apenas QAM quadrada e suportada nesta simulacao.")
        levels = np.arange(-(side - 1), side, 2)
        xv, yv = np.meshgrid(levels, levels[::-1])
        return xv.flatten() + 1j * yv.flatten()

    def qam_constellation(m):
        """Gera QAM quadrada normalizada para energia media unitaria."""
        const = qam_constellation_raw(m)
        return const / np.sqrt(np.mean(np.abs(const) ** 2))

    def bits_to_qam_symbols(bits, m):
        """Mapeia bits para simbolos QAM usando Gray coding, como no Trabalho 2."""
        b = int(np.log2(m))
        if bits.size % b != 0:
            raise ValueError("O numero de bits deve ser multiplo de log2(M).")
        blocks = bits.reshape(-1, b)
        binary_ints = blocks.dot(1 << np.arange(b - 1, -1, -1))
        gray_indices = np.array([int_to_gray(int(x)) for x in binary_ints], dtype=int)
        const = qam_constellation(m)
        return const[gray_indices], gray_indices, const, b

    def qam_symbols_to_indices(symbols, const):
        """Decide simbolos recebidos pelo indice QAM mais proximo."""
        distances = np.abs(symbols.reshape(-1, 1) - const.reshape(1, -1)) ** 2
        return np.argmin(distances, axis=1)

    def qam_symbols_to_bits(symbols, const, b):
        """Decide simbolos QAM e volta para bits binarios."""
        idx = qam_symbols_to_indices(symbols, const)
        binary_ints = np.array([gray_to_int(int(x)) for x in idx], dtype=int)
        bits = ((binary_ints[:, None] & (1 << np.arange(b - 1, -1, -1))) > 0).astype(int)
        return bits.reshape(-1)

    return bits_to_qam_symbols, qam_constellation, qam_symbols_to_bits, qam_symbols_to_indices


@app.cell
def ofdm_helpers(np):
    """Define transmissor OFDM, canal, ruido e receptor ZF."""
    def channel_response(h, n_subcarriers):
        """Resposta em frequencia H[k] do canal com N pontos."""
        return np.fft.fft(h, n_subcarriers)

    def add_cyclic_prefix(x_time, cp_len):
        """Adiciona prefixo ciclico a cada bloco OFDM."""
        return np.concatenate([x_time[:, -cp_len:], x_time], axis=1)

    def remove_cyclic_prefix(y_time_cp, cp_len, n_subcarriers):
        """Remove prefixo ciclico e corta exatamente N amostras uteis."""
        return y_time_cp[:, cp_len : cp_len + n_subcarriers]

    def ofdm_modulate(x_freq, cp_len):
        """IFFT por bloco e insercao de prefixo ciclico."""
        x_time = np.fft.ifft(x_freq, axis=1)
        return add_cyclic_prefix(x_time, cp_len)

    def apply_multipath_channel(x_time_cp, h):
        """Aplica convolucao linear por bloco OFDM."""
        y = np.array([np.convolve(block, h, mode="full") for block in x_time_cp])
        return y

    def add_awgn_for_average_subcarrier_snr(y_time_cp, h, n_subcarriers, snr_db, rng):
        """
        Adiciona AWGN complexo no tempo.

        Convencao usada: SNR media por subportadora depois do canal.
        Com FFT/IFFT padrao do NumPy, Var{FFT[w]} = N Var{w}.
        Logo: sigma_t^2 = mean(|H[k]|^2) / (N * SNR_linear).
        """
        h_freq = channel_response(h, n_subcarriers)
        mean_h2 = float(np.mean(np.abs(h_freq) ** 2))
        snr_linear = 10 ** (snr_db / 10)
        sigma2_time = mean_h2 / (n_subcarriers * snr_linear)
        noise = np.sqrt(sigma2_time / 2) * (
            rng.standard_normal(y_time_cp.shape) + 1j * rng.standard_normal(y_time_cp.shape)
        )
        return y_time_cp + noise

    def ofdm_channel(x_freq, h, cp_len, snr_db, rng):
        """Transmite blocos OFDM pelo canal multipercurso com AWGN."""
        n_subcarriers = x_freq.shape[1]
        x_time_cp = ofdm_modulate(x_freq, cp_len)
        y_time_cp = apply_multipath_channel(x_time_cp, h)
        y_time_cp = add_awgn_for_average_subcarrier_snr(y_time_cp, h, n_subcarriers, snr_db, rng)
        return y_time_cp

    def ofdm_channel_no_noise(x_freq, h, cp_len):
        """Transmite blocos OFDM pelo canal sem ruido, usado para validacao."""
        x_time_cp = ofdm_modulate(x_freq, cp_len)
        return apply_multipath_channel(x_time_cp, h)

    def ofdm_receive_zf(y_time_cp, h, cp_len, n_subcarriers):
        """Remove CP, aplica FFT e equalizacao zero-forcing."""
        h_freq = channel_response(h, n_subcarriers)
        y_useful = remove_cyclic_prefix(y_time_cp, cp_len, n_subcarriers)
        y_freq = np.fft.fft(y_useful, axis=1)
        x_hat = y_freq / h_freq.reshape(1, -1)
        return x_hat, y_freq, h_freq

    return (
        add_awgn_for_average_subcarrier_snr,
        apply_multipath_channel,
        channel_response,
        ofdm_channel,
        ofdm_channel_no_noise,
        ofdm_modulate,
        ofdm_receive_zf,
    )


@app.cell
def random_frames(bits_to_qam_symbols, modulation_order, np):
    """Gera quadros OFDM aleatorios com todas ou apenas algumas portadoras ativas."""
    def generate_qam_ofdm_frames(num_blocks, n_subcarriers, rng, active_mask=None):
        """Retorna X[k] e os indices QAM transmitidos por subportadora."""
        if active_mask is None:
            active_mask = np.ones(n_subcarriers, dtype=bool)
        active_positions = np.where(active_mask)[0]
        b = int(np.log2(modulation_order))
        num_active_symbols = num_blocks * len(active_positions)
        bits = rng.integers(0, 2, size=num_active_symbols * b)
        symbols, symbol_indices, const, b = bits_to_qam_symbols(bits, modulation_order)

        x_freq = np.zeros((num_blocks, n_subcarriers), dtype=complex)
        tx_indices = -np.ones((num_blocks, n_subcarriers), dtype=int)
        x_freq[:, active_positions] = symbols.reshape(num_blocks, len(active_positions))
        tx_indices[:, active_positions] = symbol_indices.reshape(num_blocks, len(active_positions))
        return bits, x_freq, tx_indices, const, b, active_positions

    return (generate_qam_ofdm_frames,)


@app.cell
def channel_analysis(channel_response, cp_len, h, mo, n_subcarriers, np, output_path, shutil):
    """Calcula resposta do canal, piores portadoras e prepara a pasta de saida."""
    if output_path.exists():
        shutil.rmtree(output_path)
    output_path.mkdir(parents=True, exist_ok=True)

    h_freq = channel_response(h, n_subcarriers)
    h_mag = np.abs(h_freq)
    h_power = h_mag ** 2
    mean_h_power = float(np.mean(h_power))
    worst_carriers = np.argsort(h_mag)[:5]
    worst_carriers_ordered = worst_carriers.tolist()
    disabled_mask = np.ones(n_subcarriers, dtype=bool)
    disabled_mask[worst_carriers] = False

    _csv_lines = ["k,H_real,H_imag,H_abs,H_abs_db"]
    for _k, _hk in enumerate(h_freq):
        _csv_lines.append(f"{_k},{_hk.real:.12g},{_hk.imag:.12g},{abs(_hk):.12g},{20*np.log10(abs(_hk)):.12g}")
    (output_path / "channel_frequency_response.csv").write_text("\n".join(_csv_lines), encoding="utf-8")

    mo.md(f"""
    ## Parametros deterministas do canal

    - Canal: `h[n] = {h.tolist()}`
    - Comprimento do canal: `{len(h)}` amostras
    - Prefixo ciclico minimo: `N_CP = L_h - 1 = {cp_len}`
    - Potencia media do canal no dominio da frequencia: `mean(|H[k]|^2) = {mean_h_power:.6f}`
    - Cinco piores portadoras, em ordem de pior para menos pior: `{worst_carriers_ordered}`
    """)

    return disabled_mask, h_freq, h_mag, h_power, mean_h_power, worst_carriers, worst_carriers_ordered


@app.cell
def validate_chain(
    cp_len,
    generate_qam_ofdm_frames,
    h,
    mo,
    n_subcarriers,
    np,
    ofdm_channel_no_noise,
    ofdm_receive_zf,
    rng_seed,
    worst_carriers_ordered,
):
    """Valida se CP + ZF recuperam exatamente os simbolos sem ruido."""
    _rng = np.random.default_rng(rng_seed)
    _, _x_freq, _, _, _, _ = generate_qam_ofdm_frames(64, n_subcarriers, _rng)
    _y_time_cp = ofdm_channel_no_noise(_x_freq, h, cp_len)
    _x_hat, _, _ = ofdm_receive_zf(_y_time_cp, h, cp_len, n_subcarriers)
    max_noiseless_error = float(np.max(np.abs(_x_hat - _x_freq)))

    mo.md(f"""
    ## Validacao rapida

    - Erro maximo sem ruido apos equalizacao ZF: `{max_noiseless_error:.3e}`
    - Resultado esperado: erro numerico proximo de zero.
    - Piores portadoras usadas no descarte: `{worst_carriers_ordered}`
    """)
    return (max_noiseless_error,)


@app.cell
def ser_theory(erfc, np):
    """Curva teorica aproximada de SER para M-QAM quadrada em canal ideal."""
    def q_function(x):
        return 0.5 * erfc(x / np.sqrt(2))

    def theoretical_ser_square_qam(m, snr_db):
        """
        SER aproximada/exata usual para M-QAM quadrada em AWGN.

        A SNR usada aqui e Es/N0, coerente com simbolos QAM de energia media unitaria.
        """
        snr_linear = 10 ** (np.asarray(snr_db) / 10)
        side = np.sqrt(m)
        q = q_function(np.sqrt(3 * snr_linear / (m - 1)))
        return 1 - (1 - 2 * (1 - 1 / side) * q) ** 2

    return (theoretical_ser_square_qam,)


@app.cell
def simulate_ser(
    cp_len,
    disabled_mask,
    generate_qam_ofdm_frames,
    h,
    modulation_order,
    n_subcarriers,
    np,
    num_ofdm_symbols,
    ofdm_channel,
    ofdm_receive_zf,
    qam_symbols_to_indices,
    rng_seed,
    snr_db_points,
    theoretical_ser_square_qam,
):
    """Executa simulacoes de SER original, por subportadora, ideal e com descarte."""
    ser_per_carrier = np.zeros((len(snr_db_points), n_subcarriers))
    ser_mean_original = np.zeros(len(snr_db_points))
    ser_mean_disabled = np.zeros(len(snr_db_points))
    ser_ideal = theoretical_ser_square_qam(modulation_order, snr_db_points)

    for _i, _snr_db in enumerate(snr_db_points):
        _rng_original = np.random.default_rng(rng_seed + 1000 + int(_snr_db))
        _, _x_freq, _tx_indices, _const, _, _active_positions = generate_qam_ofdm_frames(
            num_ofdm_symbols, n_subcarriers, _rng_original
        )
        _y_time_cp = ofdm_channel(_x_freq, h, cp_len, _snr_db, _rng_original)
        _x_hat, _, _ = ofdm_receive_zf(_y_time_cp, h, cp_len, n_subcarriers)
        _rx_indices = qam_symbols_to_indices(_x_hat.reshape(-1), _const).reshape(num_ofdm_symbols, n_subcarriers)
        _errors = _rx_indices != _tx_indices
        ser_per_carrier[_i, :] = np.mean(_errors, axis=0)
        ser_mean_original[_i] = float(np.mean(_errors))

        _rng_disabled = np.random.default_rng(rng_seed + 5000 + int(_snr_db))
        _, _x_freq_d, _tx_indices_d, _const_d, _, _active_d = generate_qam_ofdm_frames(
            num_ofdm_symbols, n_subcarriers, _rng_disabled, active_mask=disabled_mask
        )
        _y_time_cp_d = ofdm_channel(_x_freq_d, h, cp_len, _snr_db, _rng_disabled)
        _x_hat_d, _, _ = ofdm_receive_zf(_y_time_cp_d, h, cp_len, n_subcarriers)
        _rx_indices_d_active = qam_symbols_to_indices(_x_hat_d[:, _active_d].reshape(-1), _const_d).reshape(num_ofdm_symbols, len(_active_d))
        _errors_d = _rx_indices_d_active != _tx_indices_d[:, _active_d]
        ser_mean_disabled[_i] = float(np.mean(_errors_d))

    _lines = ["SNR_dB,SER_mean_original,SER_mean_disabled,SER_ideal"]
    for _snr, _orig, _disc, _ideal in zip(snr_db_points, ser_mean_original, ser_mean_disabled, ser_ideal):
        _lines.append(f"{_snr},{_orig:.12g},{_disc:.12g},{_ideal:.12g}")

    return ser_ideal, ser_mean_disabled, ser_mean_original, ser_per_carrier


@app.cell
def simulate_constellation_samples(
    cp_len,
    generate_qam_ofdm_frames,
    h,
    n_subcarriers,
    num_ofdm_symbols_constellation,
    ofdm_channel,
    ofdm_receive_zf,
    rng_seed,
    snr_constellation_db,
):
    """Gera amostras equalizadas para os diagramas de constelacao em 30 dB."""
    _rng = np.random.default_rng(rng_seed + 30_000)
    _, x_freq_const, tx_indices_const, const_points, _, _ = generate_qam_ofdm_frames(
        num_ofdm_symbols_constellation, n_subcarriers, _rng
    )
    y_time_cp_const = ofdm_channel(x_freq_const, h, cp_len, snr_constellation_db, _rng)
    x_hat_const, _, _ = ofdm_receive_zf(y_time_cp_const, h, cp_len, n_subcarriers)
    return const_points, tx_indices_const, x_freq_const, x_hat_const


@app.cell
def plot_helpers(np):
    """Funcoes auxiliares para graficos."""
    def safe_ser_for_plot(ser_values, floor):
        """Evita zeros em escala semilog apenas para visualizacao."""
        return np.maximum(ser_values, floor)

    def set_constellation_limits(ax, points, const):
        """Define limites iguais para os eixos I/Q."""
        extent = max(
            float(np.max(np.abs(points.real))),
            float(np.max(np.abs(points.imag))),
            float(np.max(np.abs(const.real))),
            float(np.max(np.abs(const.imag))),
            1.0,
        ) * 1.15
        ax.set_xlim(-extent, extent)
        ax.set_ylim(-extent, extent)
        ax.set_aspect("equal", adjustable="box")

    def draw_constellation(ax, points, const, title):
        """Desenha constelacao recebida e pontos ideais."""
        ax.scatter(points.real, points.imag, s=9, alpha=0.45, label="Equalizado")
        ax.scatter(const.real, const.imag, s=48, facecolors="none", edgecolors="black", linewidths=1.0, label="Ideal")
        ax.axhline(0, linewidth=0.8)
        ax.axvline(0, linewidth=0.8)
        ax.grid(True, alpha=0.3)
        ax.set_title(title)
        ax.set_xlabel("I")
        ax.set_ylabel("Q")
        ax.legend(fontsize=8)
        set_constellation_limits(ax, points, const)

    return draw_constellation, safe_ser_for_plot, set_constellation_limits


@app.cell
def plot_channel(h_mag, n_subcarriers, np, output_path, plt, worst_carriers):
    """Gera grafico de |H[k]| e destaca as cinco piores portadoras."""
    _k = np.arange(n_subcarriers)
    fig, ax = plt.subplots(figsize=(9, 4.8))
    ax.plot(_k, h_mag, marker="o", linewidth=1.5, label="|H[k]|")
    ax.scatter(worst_carriers, h_mag[worst_carriers], s=75, label="5 piores")
    for _carrier in worst_carriers:
        ax.annotate(f"k={int(_carrier)}", (_carrier, h_mag[_carrier]), textcoords="offset points", xytext=(0, 8), ha="center")
    ax.set_xlabel("Subportadora k")
    ax.set_ylabel("Amplitude |H[k]|")
    ax.set_title("Perfil do canal no dominio da frequencia")
    ax.set_xticks(_k)
    ax.grid(True, alpha=0.3)
    ax.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(output_path / "01_channel_magnitude.png", dpi=160)
    plt.show()
    plt.close(fig)
    return


@app.cell
def plot_constellations(
    const_points,
    draw_constellation,
    np,
    output_path,
    plt,
    snr_constellation_db,
    x_hat_const,
):
    """Gera os quatro diagramas de constelacao pedidos."""
    _targets = [1, 10, 15]
    _max_points = 3500

    for _carrier in _targets:
        _points = x_hat_const[:_max_points, _carrier]
        fig, ax = plt.subplots(figsize=(5.4, 5.4))
        draw_constellation(ax, _points, const_points, f"16-QAM equalizada - k={_carrier} - SNR={snr_constellation_db} dB")
        fig.tight_layout()
        fig.savefig(output_path / f"02_constellation_k{_carrier}.png", dpi=160)
        plt.show()
        plt.close(fig)

    _mixed_points = x_hat_const.reshape(-1)
    _rng = np.random.default_rng(12345)
    if _mixed_points.size > 12_000:
        _mixed_points = _rng.choice(_mixed_points, size=12_000, replace=False)

    fig, ax = plt.subplots(figsize=(5.6, 5.6))
    draw_constellation(ax, _mixed_points, const_points, f"16-QAM equalizada - todas as portadoras - SNR={snr_constellation_db} dB")
    fig.tight_layout()
    fig.savefig(output_path / "02_constellation_all_carriers.png", dpi=160)
    plt.show()
    plt.close(fig)
    return


@app.cell
def plot_ser_all_carriers(
    n_subcarriers,
    num_ofdm_symbols,
    output_path,
    plt,
    safe_ser_for_plot,
    ser_ideal,
    ser_mean_original,
    ser_per_carrier,
    snr_db_points,
):
    """Gera grafico de SER: 32 portadoras, canal ideal e media global."""
    _floor = 0.5 / num_ofdm_symbols
    fig, ax = plt.subplots(figsize=(10, 6))
    for _k in range(n_subcarriers):
        ax.semilogy(snr_db_points, safe_ser_for_plot(ser_per_carrier[:, _k], _floor), linewidth=0.8, alpha=0.45)
    ax.semilogy(snr_db_points, safe_ser_for_plot(ser_ideal, 1e-8), "--", linewidth=2.0, label="Canal ideal 16-QAM")
    ax.semilogy(snr_db_points, safe_ser_for_plot(ser_mean_original, _floor / n_subcarriers), marker="o", linewidth=2.0, label="Media OFDM - 32 portadoras")
    ax.set_xlabel("SNR media do canal (dB)")
    ax.set_ylabel("SER")
    ax.set_title("SER por subportadora, SER ideal e SER media do sistema")
    ax.grid(True, which="both", alpha=0.3)
    ax.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(output_path / "03_SER_all_carriers.png", dpi=160)
    plt.show()
    plt.close(fig)
    return


@app.cell
def plot_bit_loading(
    n_subcarriers,
    num_ofdm_symbols,
    output_path,
    plt,
    safe_ser_for_plot,
    ser_ideal,
    ser_mean_disabled,
    ser_mean_original,
    snr_db_points,
    worst_carriers_ordered,
):
    """Gera comparacao entre OFDM original e descarte das cinco piores portadoras."""
    _floor_original = 0.5 / (num_ofdm_symbols * n_subcarriers)
    _floor_disabled = 0.5 / (num_ofdm_symbols * (n_subcarriers - len(worst_carriers_ordered)))

    fig, ax = plt.subplots(figsize=(9, 5.5))
    ax.semilogy(snr_db_points, safe_ser_for_plot(ser_mean_original, _floor_original), marker="o", linewidth=2.0, label="Media original - 32 portadoras")
    ax.semilogy(snr_db_points, safe_ser_for_plot(ser_mean_disabled, _floor_disabled), marker="s", linewidth=2.0, label="Media com descarte - 27 portadoras")
    ax.semilogy(snr_db_points, safe_ser_for_plot(ser_ideal, 1e-8), "--", linewidth=2.0, label="Canal ideal 16-QAM")
    ax.set_xlabel("SNR media do canal (dB)")
    ax.set_ylabel("SER media")
    ax.set_title(f"Bit-loading extremo: descarte de k={worst_carriers_ordered}")
    ax.grid(True, which="both", alpha=0.3)
    ax.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(output_path / "04_SER_bit_loading_discard.png", dpi=160)
    plt.show()
    plt.close(fig)
    return


@app.cell
def write_numeric_report(
    cp_len,
    h,
    h_mag,
    max_noiseless_error,
    mean_h_power,
    n_subcarriers,
    output_path,
    ser_ideal,
    ser_mean_disabled,
    ser_mean_original,
    ser_per_carrier,
    snr_db_points,
    worst_carriers_ordered,
):
    """Salva tabelas numericas para uso no relatorio IEEE."""
    _lines = []
    _lines.append("Trabalho 3 - OFDM 16-QAM - resumo numerico")
    _lines.append("")
    _lines.append(f"N = {n_subcarriers}")
    _lines.append(f"h[n] = {h.tolist()}")
    _lines.append(f"N_CP minimo = {cp_len}")
    _lines.append(f"mean(|H[k]|^2) = {mean_h_power:.12g}")
    _lines.append(f"Erro maximo sem ruido apos ZF = {max_noiseless_error:.12g}")
    _lines.append(f"Piores portadoras = {worst_carriers_ordered}")
    _lines.append("")
    _lines.append("Ganho das piores portadoras:")
    for _k in worst_carriers_ordered:
        _lines.append(f"  k={_k:02d}: |H[k]| = {h_mag[_k]:.12g}")
    _lines.append("")
    _lines.append("SER media:")
    _lines.append("SNR_dB | original | descarte | ideal")
    for _snr, _orig, _disc, _ideal in zip(snr_db_points, ser_mean_original, ser_mean_disabled, ser_ideal):
        _lines.append(f"{_snr:>6} | {_orig:.6e} | {_disc:.6e} | {_ideal:.6e}")
    (output_path / "numeric_report.txt").write_text("\n".join(_lines), encoding="utf-8")

    _csv_lines = ["SNR_dB," + ",".join([f"SER_k{k}" for k in range(n_subcarriers)]) + ",SER_mean_original,SER_mean_disabled,SER_ideal"]
    for _i, _snr in enumerate(snr_db_points):
        _row = [str(_snr)]
        _row += [f"{ser_per_carrier[_i, _k]:.12g}" for _k in range(n_subcarriers)]
        _row += [f"{ser_mean_original[_i]:.12g}", f"{ser_mean_disabled[_i]:.12g}", f"{ser_ideal[_i]:.12g}"]
        _csv_lines.append(",".join(_row))
    (output_path / "ser_results.csv").write_text("\n".join(_csv_lines), encoding="utf-8")
    return


@app.cell
def interpretation(mo, worst_carriers_ordered):
    """Texto tecnico curto para orientar a conclusao do relatorio."""
    mo.md(f"""
    ## Interpretacao para o relatorio

    O canal multipercurso gera desvanecimento seletivo em frequencia: cada subportadora OFDM enxerga um ganho complexo diferente `H[k]`. Como o prefixo ciclico tem comprimento igual a memoria do canal, a convolucao linear vira convolucao circular na janela util do simbolo OFDM. Depois da FFT, o modelo por portadora fica `Y[k] = H[k]X[k] + V[k]`.

    A equalizacao ZF remove o ganho do canal por divisao direta, `X_hat[k] = Y[k]/H[k]`. Isso corrige amplitude e fase, mas amplifica o ruido por `1/|H[k]|`. Portanto, portadoras com `|H[k]|` pequeno apresentam nuvens de constelacao mais espalhadas e SER muito maior. As piores portadoras deste canal sao `{worst_carriers_ordered}`.

    O descarte dessas cinco portadoras e uma forma extrema de bit-loading: em vez de transmitir informacao em subcanais muito ruins, o sistema usa apenas as 27 portadoras restantes. A taxa bruta cai, mas a SER media melhora bastante porque a media deixa de ser arrastada pelas portadoras em desvanecimento profundo.
    """)
    return


if __name__ == "__main__":
    app.run()
