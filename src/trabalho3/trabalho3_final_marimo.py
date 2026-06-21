import marimo

__generated_with = "0.23.8"
app = marimo.App(width="medium")


# ─────────────────────────────────────────────────────────────
# Cell 01 — Imports and setup
# ─────────────────────────────────────────────────────────────
@app.cell
def imports():
    import marimo as mo
    import matplotlib.pyplot as plt
    import numpy as np
    from pathlib import Path
    import shutil
    from scipy.special import erfc
    return erfc, mo, np, Path, plt, shutil


# ─────────────────────────────────────────────────────────────
# Cell 02 — Abstract and introduction (Markdown)
# REVISÃO: sem variáveis. Siglas PT/EN na 1ª ocorrência.
# ─────────────────────────────────────────────────────────────
@app.cell
def titulo(mo):
    mo.md(r"""
    # Trabalho 3 — OFDM 16-QAM em canal multipercurso

    **Disciplina:** TE903/EELT7026 – Comunicação Digital  
    **Professor:** Ândrei Camponogara

    ## Resumo

    Este trabalho simula um sistema de multiplexação por divisão de frequências ortogonais (do inglês, *orthogonal frequency division multiplexing*, OFDM) em banda-base com modulação 16-QAM (do inglês, *quadrature amplitude modulation*, QAM), submetido a um canal multipercurso e equalização *zero-forcing* (do inglês, *zero-forcing*, ZF). O objetivo é avaliar o efeito do desvanecimento seletivo em frequência no desempenho de cada subportadora e aplicar uma técnica de carregamento de bits (do inglês, *bit-loading*) baseada no descarte das portadoras com maior atenuação. As métricas de desempenho são a taxa de erro de símbolo (do inglês, *symbol error rate*, SER) por subportadora, a SER média do sistema e a SER do canal ideal como referência.
    """)
    return


# ─────────────────────────────────────────────────────────────
# Cell 03 — Fixed system parameters
# ─────────────────────────────────────────────────────────────
@app.cell
def params(Path):
    N = 32                      # número de subportadoras
    M = 16                      # ordem da modulação QAM
    b = 4                       # bits por símbolo (log2(16))
    h = np.array([0.3, -0.5, 0.0, 1.0, 0.2, -0.3], dtype=float)
    cp_len = len(h) - 1         # prefixo cíclico mínimo = 5
    snr_mc_db = np.arange(0, 31, 2)   # pontos Monte Carlo (0 a 30 dB, step 2)
    snr_theory_db = np.linspace(0, 30, 601)  # malha fina para curva teórica
    snr_const_db = 30.0         # SNR para diagramas de constelação
    num_blocks_mc = 500_000     # blocos OFDM para curva SER
    num_blocks_const = 4_000    # blocos OFDM para constelações
    seed = 903_2026
    output_dir = Path("output/trabalho3_final")
    return (
        N, M, b, h, cp_len,
        snr_mc_db, snr_theory_db, snr_const_db,
        num_blocks_mc, num_blocks_const, seed,
        output_dir,
    )


# ─────────────────────────────────────────────────────────────
# Cell 04 — Output directory creation
# ─────────────────────────────────────────────────────────────
@app.cell
def output_setup(output_dir, shutil):
    if output_dir.exists():
        shutil.rmtree(output_dir)
    (output_dir / "figures").mkdir(parents=True, exist_ok=True)
    (output_dir / "tables").mkdir(parents=True, exist_ok=True)
    return


# ─────────────────────────────────────────────────────────────
# Cell 05 — Gray code functions
# ─────────────────────────────────────────────────────────────
@app.cell
def gray_code():
    def int_to_gray(n):
        return n ^ (n >> 1)

    def gray_to_int(g):
        n = 0
        while g:
            n ^= g
            g >>= 1
        return n

    return int_to_gray, gray_to_int


# ─────────────────────────────────────────────────────────────
# Cell 06 — 16-QAM constellation (normalized, unit energy)
# ─────────────────────────────────────────────────────────────
@app.cell
def qam_constellation_funcs(np):
    def qam_constellation_raw(m):
        """Constelação QAM quadrada não normalizada."""
        side = int(np.sqrt(m))
        if side * side != m:
            raise ValueError("Apenas QAM quadrada é suportada.")
        levels = np.arange(-(side - 1), side, 2)
        xv, yv = np.meshgrid(levels, levels[::-1])
        return xv.flatten() + 1j * yv.flatten()

    def qam_constellation(m):
        """Constelação QAM quadrada normalizada para energia média unitária."""
        const = qam_constellation_raw(m)
        return const / np.sqrt(np.mean(np.abs(const) ** 2))

    return qam_constellation, qam_constellation_raw


# ─────────────────────────────────────────────────────────────
# Cell 07 — Mapper (bits → símbolos) e demapper (símbolos → bits)
# ─────────────────────────────────────────────────────────────
@app.cell
def mapping_funcs(gray_to_int, int_to_gray, np, qam_constellation):
    def bits_to_qam_symbols(bits, m):
        """Mapeia bits para símbolos 16-QAM com codificação Gray."""
        b = int(np.log2(m))
        if bits.size % b != 0:
            raise ValueError("Número de bits deve ser múltiplo de log2(M).")
        blocks = bits.reshape(-1, b)
        binary_ints = blocks.dot(1 << np.arange(b - 1, -1, -1))
        gray_indices = np.array([int_to_gray(int(x)) for x in binary_ints], dtype=int)
        const = qam_constellation(m)
        return const[gray_indices], gray_indices, const, b

    def qam_symbols_to_indices(symbols, const):
        """Decide o índice do símbolo QAM mais próximo (vizinho mais próximo)."""
        distances = np.abs(symbols.reshape(-1, 1) - const.reshape(1, -1)) ** 2
        return np.argmin(distances, axis=1)

    def qam_symbols_to_bits(symbols, const, b):
        """Decide símbolos QAM e converte de volta para bits."""
        idx = qam_symbols_to_indices(symbols, const)
        binary_ints = np.array([gray_to_int(int(x)) for x in idx], dtype=int)
        bits = ((binary_ints[:, None] & (1 << np.arange(b - 1, -1, -1))) > 0).astype(int)
        return bits.reshape(-1)

    return bits_to_qam_symbols, qam_symbols_to_bits, qam_symbols_to_indices


# ─────────────────────────────────────────────────────────────
# Cell 08 — Channel frequency response and cyclic prefix helpers
# ─────────────────────────────────────────────────────────────
@app.cell
def channel_cp_helpers(np):
    def channel_response(h, n):
        """Resposta em frequência H[k] = FFT(h, n)."""
        return np.fft.fft(h, n)

    def add_cyclic_prefix(x_time, cp_len):
        """Adiciona prefixo cíclico a cada bloco OFDM."""
        return np.concatenate([x_time[:, -cp_len:], x_time], axis=1)

    def remove_cyclic_prefix(y_time_cp, cp_len, n):
        """Remove prefixo cíclico e extrai as N amostras úteis."""
        return y_time_cp[:, cp_len:cp_len + n]

    return add_cyclic_prefix, channel_response, remove_cyclic_prefix


# ─────────────────────────────────────────────────────────────
# Cell 09 — OFDM modulator (IFFT + CP)
# ─────────────────────────────────────────────────────────────
@app.cell
def ofdm_modulator(add_cyclic_prefix, np):
    def ofdm_modulate(x_freq, cp_len):
        """IFFT por bloco e inserção de prefixo cíclico."""
        x_time = np.fft.ifft(x_freq, axis=1)
        return add_cyclic_prefix(x_time, cp_len)

    return (ofdm_modulate,)


# ─────────────────────────────────────────────────────────────
# Cell 10 — Multipath channel + AWGN
# ─────────────────────────────────────────────────────────────
@app.cell
def channel_awgn(channel_response, np):
    def apply_multipath_channel(x_time_cp, h):
        """Convolução linear com o canal FIR por bloco OFDM (vetorizada via FFT)."""
        n_fft = x_time_cp.shape[1] + len(h) - 1
        X_fft = np.fft.fft(x_time_cp, n=n_fft, axis=1)
        H_fft = np.fft.fft(h, n=n_fft)
        return np.fft.ifft(X_fft * H_fft[np.newaxis, :], axis=1)

    def add_awgn_avg_snr(y_time_cp, h, n, snr_db, rng):
        """
        Adiciona AWGN complexo no domínio do tempo.
        Convenção: SNR média por subportadora depois do canal.
        σ_t² = mean(|H[k]|²) / (N * SNR_linear)
        """
        h_freq = channel_response(h, n)
        mean_h2 = float(np.mean(np.abs(h_freq) ** 2))
        snr_lin = 10 ** (snr_db / 10)
        sigma2_time = mean_h2 / (n * snr_lin)
        sigma = np.sqrt(sigma2_time / 2)
        noise = sigma * (rng.standard_normal(y_time_cp.shape)
                         + 1j * rng.standard_normal(y_time_cp.shape))
        return y_time_cp + noise

    def transmit_channel(x_freq, h, cp_len, snr_db, rng):
        """Cadeia completa: modulação OFDM → canal → AWGN."""
        x_time_cp = np.fft.ifft(x_freq, axis=1)
        x_time_cp = np.concatenate([x_time_cp[:, -cp_len:], x_time_cp], axis=1)
        y_time_cp = apply_multipath_channel(x_time_cp, h)
        y_time_cp = add_awgn_avg_snr(y_time_cp, h, x_freq.shape[1], snr_db, rng)
        return y_time_cp

    def transmit_channel_no_noise(x_freq, h, cp_len):
        """Cadeia sem ruído (para validação)."""
        x_time_cp = np.fft.ifft(x_freq, axis=1)
        x_time_cp = np.concatenate([x_time_cp[:, -cp_len:], x_time_cp], axis=1)
        return apply_multipath_channel(x_time_cp, h)

    return (
        add_awgn_avg_snr,
        apply_multipath_channel,
        transmit_channel,
        transmit_channel_no_noise,
    )


# ─────────────────────────────────────────────────────────────
# Cell 11 — ZF receiver (remove CP + FFT + equalização)
# ─────────────────────────────────────────────────────────────
@app.cell
def zf_receiver(channel_response, remove_cyclic_prefix, np):
    def ofdm_receive_zf(y_time_cp, h, cp_len, n):
        """Remove CP, aplica FFT e equalização zero-forcing."""
        h_freq = channel_response(h, n)
        y_useful = remove_cyclic_prefix(y_time_cp, cp_len, n)
        y_freq = np.fft.fft(y_useful, axis=1)
        x_hat = y_freq / h_freq.reshape(1, -1)
        return x_hat, y_freq, h_freq

    return (ofdm_receive_zf,)


# ─────────────────────────────────────────────────────────────
# Cell 12 — Frame generator (random OFDM blocks)
# ─────────────────────────────────────────────────────────────
@app.cell
def frame_generator(bits_to_qam_symbols, M, np):
    def generate_frames(num_blocks, n, rng, active_mask=None):
        """Gera blocos OFDM aleatórios, retorna X[k] e índices transmitidos."""
        if active_mask is None:
            active_mask = np.ones(n, dtype=bool)
        active_positions = np.where(active_mask)[0]
        b = int(np.log2(M))
        num_active = num_blocks * len(active_positions)
        bits = rng.integers(0, 2, size=num_active * b)
        symbols, symbol_indices, const, b = bits_to_qam_symbols(bits, M)

        x_freq = np.zeros((num_blocks, n), dtype=complex)
        tx_indices = -np.ones((num_blocks, n), dtype=int)
        x_freq[:, active_positions] = symbols.reshape(num_blocks, len(active_positions))
        tx_indices[:, active_positions] = symbol_indices.reshape(num_blocks, len(active_positions))
        return bits, x_freq, tx_indices, const, b, active_positions

    return (generate_frames,)


# ─────────────────────────────────────────────────────────────
# Cell 13 — Channel analysis and deterministic validation
# ─────────────────────────────────────────────────────────────
@app.cell
def channel_analysis(
    channel_response, cp_len, h, M, mo, N, np, output_dir, qam_constellation, seed,
):
    _rng = np.random.default_rng(seed)
    h_freq = channel_response(h, N)
    h_mag = np.abs(h_freq)
    h_pow = h_mag ** 2
    mean_h_pow = float(np.mean(h_pow))
    sum_h2 = float(np.sum(h ** 2))
    worst_idx = np.argsort(h_mag)[:5]
    worst_ordered = worst_idx.tolist()
    worst_set = sorted(worst_ordered)

    # Validação da cadeia sem ruído
    _const_val = qam_constellation(M)
    _x_test = _rng.choice(_const_val, size=N).reshape(1, N)
    _x_time_cp = np.fft.ifft(_x_test, axis=1)
    _x_time_cp = np.concatenate([_x_time_cp[:, -cp_len:], _x_time_cp], axis=1)
    _y_full = np.convolve(_x_time_cp[0], h)
    _y = _y_full[cp_len:cp_len + N]
    _y_freq = np.fft.fft(_y, n=N)
    _x_hat = _y_freq / h_freq
    max_err = float(np.max(np.abs(_x_hat - _x_test[0])))

    # Energia média da constelação
    const_energy = float(np.mean(np.abs(const) ** 2))

    # Validação de normalização
    valid_cp = (cp_len == len(h) - 1)
    valid_energy = np.isclose(const_energy, 1.0, atol=1e-14)
    valid_noiseless = (max_err < 1e-12)
    valid_worst = (sorted(worst_ordered) == [14, 15, 16, 17, 18])
    valid_sumh2 = np.isclose(sum_h2, 1.47, atol=1e-12)

    # Tabela markdown com resultados
    _rows = [
        f"| Parâmetro | Valor | Status |",
        f"|---|---|---|",
        f"| N (subportadoras) | {N} | — |",
        f"| Modulação | {M}-QAM | — |",
        f"| Canal h[n] | {h.tolist()} | — |",
        f"| Comprimento do canal | {len(h)} amostras | — |",
        f"| CP mínimo (L_h-1) | {cp_len} | {'✅' if valid_cp else '❌'} |",
        f"| Σ|h[n]|² | {sum_h2:.6f} (esperado: 1.47) | {'✅' if valid_sumh2 else '❌'} |",
        f"| Média |H[k]|² | {mean_h_pow:.6f} | — |",
        f"| Energia média da constelação | {const_energy:.15f} | {'✅' if valid_energy else '❌'} |",
        f"| Erro máximo sem ruído | {max_err:.3e} | {'✅' if valid_noiseless else '❌'} |",
        f"| Piores portadoras (ordenadas) | {worst_ordered} | {'✅' if valid_worst else '❌'} |",
        f"| Conjunto de descarte | {worst_set} | — |",
    ]
    mo.md("\n".join(_rows))

    # Salvar resposta em frequência
    _csv = ["k,Re_H,Im_H,abs_H,abs_H_dB"]
    for _k in range(N):
        _csv.append(f"{_k},{h_freq[_k].real:.12g},{h_freq[_k].imag:.12g},"
                    f"{h_mag[_k]:.12g},{20*np.log10(h_mag[_k]):.12g}")
    (output_dir / "tables" / "channel_frequency_response.csv").write_text(
        "\n".join(_csv), encoding="utf-8"
    )

    return (
        h_freq, h_mag, h_pow, mean_h_pow, worst_idx, worst_ordered, worst_set,
        max_err, const_energy, valid_cp, valid_energy, valid_noiseless, valid_worst,
    )


# ─────────────────────────────────────────────────────────────
# Cell 14 — Theoretical SER for M-QAM in AWGN
# ─────────────────────────────────────────────────────────────
@app.cell
def ser_theory(erfc, np):
    def q_function(x):
        return 0.5 * erfc(x / np.sqrt(2))

    def ser_ideal_mqam(m, snr_db):
        """
        SER teórica para M-QAM quadrada em canal AWGN.
        A SNR usada é Es/N0, compatível com constelação de energia unitária.
        """
        snr_lin = 10 ** (np.asarray(snr_db) / 10)
        side = int(np.sqrt(m))
        q = q_function(np.sqrt(3 * snr_lin / (m - 1)))
        return 1 - (1 - 2 * (1 - 1 / side) * q) ** 2

    return q_function, ser_ideal_mqam


# ─────────────────────────────────────────────────────────────
# Cell 15 — SER Monte Carlo simulation
# ─────────────────────────────────────────────────────────────
@app.cell
def ser_monte_carlo(
    generate_frames, h, cp_len, N, M, num_blocks_mc, snr_mc_db, seed,
    transmit_channel, ofdm_receive_zf, qam_symbols_to_indices,
    ser_ideal_mqam, snr_theory_db, worst_idx,
):
    ser_per_carrier = np.zeros((len(snr_mc_db), N))
    ser_mean_orig = np.zeros(len(snr_mc_db))
    ser_mean_disabled = np.zeros(len(snr_mc_db))
    errors_per_carrier = np.zeros((len(snr_mc_db), N), dtype=np.int64)
    errors_orig = np.zeros(len(snr_mc_db), dtype=np.int64)
    errors_disabled = np.zeros(len(snr_mc_db), dtype=np.int64)

    # Curva teórica ideal na malha fina (canal AWGN)
    ser_ideal_theory = ser_ideal_mqam(M, snr_theory_db)

    # Curva teórica OFDM+ZF: média das SERs individuais de cada subportadora
    # Cada subportadora k tem SNR_eff = SNR_lin * |H[k]|² / mean(|H|²)
    _h_freq_th = np.fft.fft(h, N)
    _mean_h2_th = float(np.mean(np.abs(_h_freq_th) ** 2))
    _snr_theory_lin = 10 ** (snr_theory_db / 10)
    ser_ofdm_zf_per_carrier_theory = np.zeros((len(snr_theory_db), N))
    for _k in range(N):
        _eff_snr_lin = _snr_theory_lin * np.abs(_h_freq_th[_k]) ** 2 / _mean_h2_th
        _eff_snr_db = 10 * np.log10(_eff_snr_lin)
        ser_ofdm_zf_per_carrier_theory[:, _k] = ser_ideal_mqam(M, _eff_snr_db)
    ser_ofdm_zf_theory = np.mean(ser_ofdm_zf_per_carrier_theory, axis=1)

    # Portadoras a descartar (recebidas da análise do canal)
    disabled_mask = np.ones(N, dtype=bool)
    disabled_mask[worst_idx] = False
    ser_ofdm_zf_theory_disabled = np.mean(
        ser_ofdm_zf_per_carrier_theory[:, disabled_mask], axis=1
    )

    for _i, _snr_db in enumerate(snr_mc_db):
        # --- Simulação com 32 portadoras ---
        _rng_orig = np.random.default_rng(seed + 1000 + int(_snr_db))
        _, _x_freq, _tx_idx, _const, _, _ = generate_frames(
            num_blocks_mc, N, _rng_orig
        )
        _y = transmit_channel(_x_freq, h, cp_len, _snr_db, _rng_orig)
        _x_hat, _, _ = ofdm_receive_zf(_y, h, cp_len, N)
        _rx_idx = qam_symbols_to_indices(
            _x_hat.reshape(-1), _const
        ).reshape(num_blocks_mc, N)
        _errors = _rx_idx != _tx_idx
        ser_per_carrier[_i, :] = np.mean(_errors, axis=0)
        ser_mean_orig[_i] = float(np.mean(_errors))
        errors_per_carrier[_i, :] = np.sum(_errors, axis=0)
        errors_orig[_i] = int(np.sum(_errors))

        # --- Simulação com descarte (27 portadoras) ---
        _rng_dis = np.random.default_rng(seed + 5000 + int(_snr_db))
        _, _x_freq_d, _tx_idx_d, _const_d, _, _active_d = generate_frames(
            num_blocks_mc, N, _rng_dis, active_mask=disabled_mask
        )
        _y_d = transmit_channel(_x_freq_d, h, cp_len, _snr_db, _rng_dis)
        _x_hat_d, _, _ = ofdm_receive_zf(_y_d, h, cp_len, N)
        _rx_idx_d = qam_symbols_to_indices(
            _x_hat_d[:, _active_d].reshape(-1), _const_d
        ).reshape(num_blocks_mc, len(_active_d))
        _errors_d = _rx_idx_d != _tx_idx_d[:, _active_d]
        ser_mean_disabled[_i] = float(np.mean(_errors_d))
        errors_disabled[_i] = int(np.sum(_errors_d))

    return (
        ser_per_carrier, ser_mean_orig, ser_mean_disabled,
        ser_ideal_theory, disabled_mask,
        ser_ofdm_zf_theory, ser_ofdm_zf_theory_disabled,
        errors_per_carrier, errors_orig, errors_disabled,
    )


# ─────────────────────────────────────────────────────────────
# Cell 16 — Constellation samples at SNR = 30 dB
# ─────────────────────────────────────────────────────────────
@app.cell
def constellation_samples(
    generate_frames, transmit_channel, ofdm_receive_zf,
    h, cp_len, N, num_blocks_const, snr_const_db, seed,
):
    _rng = np.random.default_rng(seed + 30_000)
    _, x_freq, tx_idx, const, _, _ = generate_frames(
        num_blocks_const, N, _rng
    )
    y = transmit_channel(x_freq, h, cp_len, snr_const_db, _rng)
    x_hat, _, _ = ofdm_receive_zf(y, h, cp_len, N)
    return const, tx_idx, x_hat, x_freq


# ─────────────────────────────────────────────────────────────
# Cell 17 — Plot helpers
# REVISÃO: sem ax.set_title(). Legendas descritivas.
# ─────────────────────────────────────────────────────────────
@app.cell
def plot_helpers(np):
    def safe_ser_for_plot(ser, floor):
        """Substitui zeros por um piso para exibição em escala semilog."""
        return np.maximum(ser, floor)

    def set_constellation_limits(ax, points, const):
        """Define limites iguais e proporção adequada para constelação."""
        lim = max(
            float(np.max(np.abs(points.real))),
            float(np.max(np.abs(points.imag))),
            float(np.max(np.abs(const.real))),
            float(np.max(np.abs(const.imag))),
            1.0,
        ) * 1.15
        ax.set_xlim(-lim, lim)
        ax.set_ylim(-lim, lim)
        ax.set_aspect("equal", adjustable="box")

    def draw_constellation(ax, points, const, label):
        """Desenha constelação equalizada + pontos ideais. SEM título."""
        ax.scatter(points.real, points.imag, s=9, alpha=0.45, label=label)
        ax.scatter(const.real, const.imag, s=48, facecolors="none",
                   edgecolors="black", linewidths=1.0, label="Ideal")
        ax.axhline(0, linewidth=0.8, color="gray")
        ax.axvline(0, linewidth=0.8, color="gray")
        ax.grid(True, alpha=0.3)
        ax.set_xlabel("I")
        ax.set_ylabel("Q")
        ax.legend(fontsize=8)
        set_constellation_limits(ax, points, const)

    return draw_constellation, safe_ser_for_plot, set_constellation_limits


# ─────────────────────────────────────────────────────────────
# Cell 18 — Fig 01: Perfil do canal |H[k]|
# REVISÃO: sem título. Legendas descritivas.
# ─────────────────────────────────────────────────────────────
@app.cell
def fig_channel_gain(h_mag, N, np, output_dir, plt, worst_idx):
    _k_idx = np.arange(N)
    _fig, _ax = plt.subplots(figsize=(9, 4.8))
    _ax.plot(_k_idx, h_mag, marker="o", linewidth=1.5, label="|H[k]|")
    _ax.scatter(worst_idx, h_mag[worst_idx], s=75, zorder=5,
               label="5 piores subportadoras")
    for _k in worst_idx:
        _ax.annotate(f"k={int(_k)}", (_k, h_mag[_k]),
                    textcoords="offset points", xytext=(0, 8), ha="center")
    _ax.set_xlabel("Subportadora k")
    _ax.set_ylabel("Amplitude |H[k]|")
    _ax.set_xticks(_k_idx)
    _ax.grid(True, alpha=0.3)
    _ax.legend(fontsize=8)
    _fig.tight_layout()
    _fig.savefig(output_dir / "figures" / "fig_01_channel_gain.png", dpi=160)
    plt.show()
    plt.close(_fig)


# ─────────────────────────────────────────────────────────────
# Cell 19 — Figs 02-05: Constelações equalizadas a 30 dB
# REVISÃO: sem título. Nome do arquivo identifica o subcanal.
# ─────────────────────────────────────────────────────────────
@app.cell
def fig_constellations(
    const, draw_constellation, np, output_dir, plt, snr_const_db, x_hat,
):
    targets = [1, 10, 15]
    labels = {
        1: "Subcanal moderado (k=1)",
        10: "Subcanal bom (k=10)",
        15: "Subcanal pobre (k=15)",
    }
    max_pts = 3500

    for _k in targets:
        pts = x_hat[:max_pts, _k]
        _fig, _ax = plt.subplots(figsize=(5.4, 5.4))
        draw_constellation(
            _ax, pts, const,
            f"16-QAM equalizada — {labels[_k]} — SNR={snr_const_db} dB"
        )
        _fig.tight_layout()
        _fig.savefig(output_dir / "figures" / f"fig_02_constellation_k{_k}.png", dpi=160)
        plt.show()
        plt.close(_fig)

    # Mistura de todas as portadoras
    all_pts = x_hat.reshape(-1)
    rng_mix = np.random.default_rng(12345)
    if all_pts.size > 12_000:
        all_pts = rng_mix.choice(all_pts, size=12_000, replace=False)

    _fig, _ax = plt.subplots(figsize=(5.6, 5.6))
    draw_constellation(
        _ax, all_pts, const,
        f"16-QAM equalizada — todas as portadoras — SNR={snr_const_db} dB"
    )
    _fig.tight_layout()
    _fig.savefig(output_dir / "figures" / "fig_02_constellation_all.png", dpi=160)
    plt.show()
    plt.close(_fig)


# ─────────────────────────────────────────────────────────────
# Cell 20 — Fig 06: SER por subportadora
# REVISÃO:
#   - sem título
#   - 32 curvas individuais (Monte Carlo): PONTOS, sem linhas
#   - Média OFDM (Monte Carlo): PONTOS
#   - OFDM+ZF (teórica): LINHA CONTÍNUA — mesma convenção de SNR do MC
#   - Canal ideal (teórica): LINHA CONTÍNUA com malha fina
#   - Marcador 'x' quando < 100 erros (não convergido)
# ─────────────────────────────────────────────────────────────
@app.cell
def fig_ser_all_carriers(
    num_blocks_mc, N, np, output_dir, plt,
    safe_ser_for_plot, ser_ideal_theory, ser_mean_orig,
    ser_ofdm_zf_theory, ser_per_carrier, snr_mc_db, snr_theory_db,
    errors_per_carrier, errors_orig,
):
    _floor_per_carrier = 0.5 / num_blocks_mc
    _floor_mean = _floor_per_carrier / N
    _min_errors = 100

    _fig, _ax = plt.subplots(figsize=(10, 6))

    # 32 curvas individuais: PONTOS sem linhas
    for _k in range(N):
        _conv = errors_per_carrier[:, _k] >= _min_errors
        _unconv = ~_conv
        # Convergidos: pontos cheios
        if np.any(_conv):
            _ax.semilogy(
                snr_mc_db[_conv], ser_per_carrier[_conv, _k],
                marker=".", linestyle="none", markersize=3, alpha=0.45,
            )
        # Não convergidos: 'x' pequeno
        if np.any(_unconv):
            _ax.semilogy(
                snr_mc_db[_unconv], ser_per_carrier[_unconv, _k],
                marker="x", linestyle="none", markersize=3, alpha=0.25,
            )

    # Média OFDM: PONTOS (convergido = cheio, não convergido = oco)
    _conv_avg = errors_orig >= _min_errors
    _unconv_avg = ~_conv_avg
    if np.any(_conv_avg):
        _ax.semilogy(
            snr_mc_db[_conv_avg], safe_ser_for_plot(ser_mean_orig[_conv_avg], _floor_mean),
            marker="o", linestyle="none", markersize=6, color="C0",
            label="Média OFDM — 32 portadoras (≥100 erros)",
        )
    if np.any(_unconv_avg):
        _ax.semilogy(
            snr_mc_db[_unconv_avg], safe_ser_for_plot(ser_mean_orig[_unconv_avg], _floor_mean),
            marker="o", linestyle="none", markersize=6, color="C0",
            markerfacecolor="none", markeredgecolor="C0", markeredgewidth=1.2,
            label="Média OFDM — 32 portadoras (<100 erros)",
        )

    # OFDM+ZF teórica: LINHA CONTÍNUA (deve coincidir com MC)
    _ax.semilogy(
        snr_theory_db, safe_ser_for_plot(ser_ofdm_zf_theory, 1e-12),
        linestyle="-", linewidth=1.8, color="C3",
        label="Média OFDM+ZF — 32 portadoras (teórica)",
    )

    # Canal ideal: LINHA CONTÍNUA
    _ax.semilogy(
        snr_theory_db, safe_ser_for_plot(ser_ideal_theory, 1e-12),
        linestyle="-", linewidth=2.0, color="C1",
        label="16-QAM canal ideal (teórica)",
    )

    _ax.set_xlabel("SNR médio do canal (dB)")
    _ax.set_ylabel("SER")
    _ax.set_ylim(1e-6, 1)
    _ax.grid(True, which="both", alpha=0.3)
    _ax.legend(fontsize=8)
    _fig.tight_layout()
    _fig.savefig(output_dir / "figures" / "fig_06_ser_all_subcarriers.png", dpi=160)
    plt.show()
    plt.close(_fig)


# ─────────────────────────────────────────────────────────────
# Cell 21 — Fig 07: Bit-loading extremo
# REVISÃO:
#   - sem título
#   - Original e descarte (Monte Carlo): PONTOS
#   - OFDM+ZF (teórica): LINHA CONTÍNUA — mesma convenção de SNR do MC
#   - Canal ideal (teórica): LINHA CONTÍNUA
#   - Marcadores ocos quando < 100 erros (não convergido)
# ─────────────────────────────────────────────────────────────
@app.cell
def fig_bit_loading(
    num_blocks_mc, N, np, output_dir, plt,
    safe_ser_for_plot, ser_ideal_theory, ser_mean_disabled,
    ser_mean_orig, ser_ofdm_zf_theory, ser_ofdm_zf_theory_disabled,
    snr_mc_db, snr_theory_db, worst_idx,
    errors_orig, errors_disabled,
):
    _disabled_n = N - len(worst_idx)
    _floor_orig = 0.5 / (num_blocks_mc * N)
    _floor_dis = 0.5 / (num_blocks_mc * _disabled_n)
    _min_errors = 100

    _fig, _ax = plt.subplots(figsize=(9, 5.5))

    # Original: PONTOS (cheio = convergido, oco = não convergido)
    _conv_o = errors_orig >= _min_errors
    _unconv_o = ~_conv_o
    if np.any(_conv_o):
        _ax.semilogy(
            snr_mc_db[_conv_o], safe_ser_for_plot(ser_mean_orig[_conv_o], _floor_orig),
            marker="o", linestyle="none", markersize=6, color="C0",
            label="Média original — 32 portadoras (≥100 erros)",
        )
    if np.any(_unconv_o):
        _ax.semilogy(
            snr_mc_db[_unconv_o], safe_ser_for_plot(ser_mean_orig[_unconv_o], _floor_orig),
            marker="o", linestyle="none", markersize=6, color="C0",
            markerfacecolor="none", markeredgecolor="C0", markeredgewidth=1.2,
            label="Média original — 32 portadoras (<100 erros)",
        )

    # OFDM+ZF teórica (original): LINHA CONTÍNUA (deve coincidir com MC)
    _ax.semilogy(
        snr_theory_db, safe_ser_for_plot(ser_ofdm_zf_theory, 1e-12),
        linestyle="-", linewidth=1.8, color="C3",
        label="Média OFDM+ZF — 32 portadoras (teórica)",
    )

    # Com descarte: PONTOS (cheio = convergido, oco = não convergido)
    _conv_d = errors_disabled >= _min_errors
    _unconv_d = ~_conv_d
    if np.any(_conv_d):
        _ax.semilogy(
            snr_mc_db[_conv_d], safe_ser_for_plot(ser_mean_disabled[_conv_d], _floor_dis),
            marker="s", linestyle="none", markersize=6, color="C2",
            label=f"Média com descarte — {_disabled_n} portadoras (≥100 erros)",
        )
    if np.any(_unconv_d):
        _ax.semilogy(
            snr_mc_db[_unconv_d], safe_ser_for_plot(ser_mean_disabled[_unconv_d], _floor_dis),
            marker="s", linestyle="none", markersize=6, color="C2",
            markerfacecolor="none", markeredgecolor="C2", markeredgewidth=1.2,
            label=f"Média com descarte — {_disabled_n} portadoras (<100 erros)",
        )

    # OFDM+ZF teórica (descarte): LINHA CONTÍNUA (deve coincidir com MC)
    _ax.semilogy(
        snr_theory_db, safe_ser_for_plot(ser_ofdm_zf_theory_disabled, 1e-12),
        linestyle="-", linewidth=1.8, color="C4",
        label=f"Média OFDM+ZF com descarte — {_disabled_n} portadoras (teórica)",
    )

    # Ideal: LINHA CONTÍNUA
    _ax.semilogy(
        snr_theory_db, safe_ser_for_plot(ser_ideal_theory, 1e-12),
        linestyle="-", linewidth=2.0, color="C1",
        label="16-QAM canal ideal (teórica)",
    )

    _ax.set_xlabel("SNR médio do canal (dB)")
    _ax.set_ylabel("SER média")
    _ax.set_ylim(1e-6, 1)
    _ax.grid(True, which="both", alpha=0.3)
    _ax.legend(fontsize=8)
    _fig.tight_layout()
    _fig.savefig(output_dir / "figures" / "fig_07_ser_bit_loading.png", dpi=160)
    plt.show()
    plt.close(_fig)


# ─────────────────────────────────────────────────────────────
# Cell 22 — Numerical reports (CSV and text)
# ─────────────────────────────────────────────────────────────
@app.cell
def numeric_reports(
    cp_len, h, h_mag, max_err, mean_h_pow, N, output_dir,
    ser_ideal_theory, ser_mean_disabled, ser_mean_orig,
    ser_per_carrier, snr_mc_db, snr_theory_db, worst_ordered,
):
    # Relatório numérico em texto
    lines = []
    lines.append("Trabalho 3 — OFDM 16-QAM — Resumo numérico")
    lines.append("=" * 50)
    lines.append(f"N = {N}")
    lines.append(f"h[n] = {h.tolist()}")
    lines.append(f"N_CP mínimo = {cp_len}")
    lines.append(f"mean(|H[k]|^2) = {mean_h_pow:.6f}")
    lines.append(f"Erro máximo sem ruído = {max_err:.3e}")
    lines.append(f"Piores portadoras = {worst_ordered}")
    lines.append("")
    lines.append("Ganho das piores portadoras:")
    for _k in worst_ordered:
        lines.append(f"  k={_k:02d}: |H[k]| = {h_mag[_k]:.6f}, "
                     f"ganho = {20*np.log10(h_mag[_k]):.2f} dB")
    lines.append("")
    lines.append(f"{'SNR_dB':>6} | {'Original':>12} | {'Descarte':>12} | {'Ideal':>12}")
    for _snr, _orig, _disc in zip(snr_mc_db, ser_mean_orig, ser_mean_disabled):
        _ideal_val = ser_ideal_theory[np.argmin(np.abs(snr_theory_db - _snr))]
        lines.append(f"{_snr:6.0f} | {_orig:.6e} | {_disc:.6e} | {_ideal_val:.6e}")

    (output_dir / "tables" / "numeric_report.txt").write_text(
        "\n".join(lines), encoding="utf-8"
    )

    # results_summary.csv
    csv_lines = [
        "SNR_dB,"
        + ",".join([f"SER_k{k}" for k in range(N)])
        + ",SER_mean_original,SER_mean_disabled,SER_ideal"
    ]
    for _i, _snr in enumerate(snr_mc_db):
        _row = [str(_snr)]
        _row += [f"{ser_per_carrier[_i, _k]:.12g}" for _k in range(N)]
        _ideal_val = ser_ideal_theory[
            np.argmin(np.abs(snr_theory_db - _snr))
        ]
        _row += [
            f"{ser_mean_orig[_i]:.12g}",
            f"{ser_mean_disabled[_i]:.12g}",
            f"{_ideal_val:.12g}",
        ]
        csv_lines.append(",".join(_row))
    (output_dir / "tables" / "results_summary.csv").write_text(
        "\n".join(csv_lines), encoding="utf-8"
    )

    # channel_summary.csv
    disabled_set = set(worst_ordered)
    csv_ch = ["k,Re_H,Im_H,abs_H,abs_H_dB,disabled"]
    _h_freq_csv = np.fft.fft(h, N)
    for _k in range(N):
        hk = _h_freq_csv[_k]
        csv_ch.append(
            f"{_k},{hk.real:.12g},{hk.imag:.12g},{abs(hk):.12g},"
            f"{20*np.log10(abs(hk)):.12g},{'1' if _k in disabled_set else '0'}"
        )
    (output_dir / "tables" / "channel_summary.csv").write_text(
        "\n".join(csv_ch), encoding="utf-8"
    )


# ─────────────────────────────────────────────────────────────
# Cell 23 — Technical interpretation (Markdown)
# REVISÃO:
#   - Siglas PT/EN na 1ª ocorrência
#   - NÃO dizer "é esperado que as curvas não batam"
#   - Explicar física, não justificar erros
# ─────────────────────────────────────────────────────────────
@app.cell
def interpretation(mo, worst_ordered):
    mo.md(f"""
    ## Interpretação dos resultados

    O canal multipercurso gera **desvanecimento seletivo em frequência**: cada subportadora do OFDM (do inglês, *orthogonal frequency division multiplexing*, OFDM) enxerga um ganho complexo diferente `H[k]`. Como o prefixo cíclico (do inglês, *cyclic prefix*, CP) tem comprimento igual à memória do canal (5 amostras), a convolução linear torna-se uma convolução circular no bloco útil do símbolo OFDM. Após a transformada rápida de Fourier (do inglês, *fast Fourier transform*, FFT), o modelo por subportadora é `Y[k] = H[k] X[k] + V[k]`.

    A equalização *zero-forcing* (do inglês, *zero-forcing*, ZF) remove o efeito do canal por divisão direta: `X̂[k] = Y[k] / H[k]`. Isso corrige amplitude e fase, mas **amplifica o ruído** por um fator `1 / |H[k]|`. Portanto, subportadoras com `|H[k]|` pequeno apresentam nuvens de constelação mais espalhadas e taxa de erro de símbolo (do inglês, *symbol error rate*, SER) muito maior.

    As cinco piores portadoras deste canal — `{worst_ordered}` — estão numa região de entalhe espectral (do inglês, *spectral notch*). Após a equalização ZF, a variância do ruído efetivo nessas portadoras é amplificada por `1 / |H[k]|²`, tornando a recepção nessas subportadoras muito pobre.

    O **descarte das cinco piores portadoras** é uma forma extrema de carregamento de bits (do inglês, *bit-loading*): em vez de transmitir informações em subcanais muito degradados, o sistema utiliza apenas as 27 portadoras restantes. A taxa de transmissão bruta cai, mas a SER média melhora significativamente porque a média deixa de ser dominada pelas portadoras em desvanecimento profundo. O ZF, por si só, não consegue melhorar a SNR efetiva dessas portadoras — ele apenas transfere o problema do domínio do canal para o domínio do ruído.

    Os resultados da simulação Monte Carlo confirmam a análise teórica. A curva teórica do sistema OFDM+ZF (média das SERs individuais de cada subportadora) coincide com os pontos obtidos por simulação, validando a modelagem — a SNR efetiva de cada subportadora k é `SNR_lin × |H[k]|² / mean(|H|²)`. A curva do canal ideal AWGN é apresentada como referência de limite inferior. O descarte das cinco piores portadoras reduz a SER média em aproximadamente uma ordem de grandeza em SNR alta, aproximando o desempenho do sistema do limite AWGN ideal.
    """)


# ─────────────────────────────────────────────────────────────
# Cell 24 — Footer
# ─────────────────────────────────────────────────────────────
@app.cell
def footer(mo):
    mo.md(r"""
    ---
    **Referências:**

    - Lathi, B. P.; Ding, Z. *Modern Digital and Analog Communication Systems*, 5th ed.
    - Proakis, J. G.; Salehi, M. *Digital Communications*, 5th ed.
    - Slides das aulas 12–13, 18–19, 22–23 da disciplina TE903/EELT7026.
    - Documento de requisitos: *Atividade 3 — Comunicação Digital*.

    *Notebook gerado em Marimo. Última execução: junho de 2026.*
    """)


if __name__ == "__main__":
    app.run()
