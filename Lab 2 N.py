# ============================================================
# Simulação de Sistemas de Comunicação Digital
#
# Modulações:
#   - M-QAM
#   - M-PSK
#
# Pulsos:
#   - Retangular (NRZ)
#   - Raised Cosine
#
# Canal:
#   - AWGN
#
# Receptor:
#   - Coerente com filtro casado
#
# Referência de nomenclatura:
#   Lathi - Modern Digital and Analog Communication Systems
# ============================================================

#%% ==========================================================
# Importação das bibliotecas
# =============================================================

import numpy as np
import matplotlib.pyplot as plt
from scipy.special import erfc
import os

#%% ==========================================================
# 1. Parâmetros do sistema
# =============================================================

# ============================================================
# Frequência da portadora
# ============================================================
fc = 10

# ============================================================
# Frequência de amostragem
# ============================================================
fs = 4 * fc

# ============================================================
# Intervalo de amostragem
# Tsamp = 1/fs
# ============================================================
Tsamp = 1 / fs

# ============================================================
# Número de amostras por símbolo
# ============================================================
Ns = 16

# ============================================================
# Intervalo de símbolo
# Ts = Ns * Tsamp
# ============================================================
Ts = Ns * Tsamp

# ============================================================
# Fator de roll-off do Raised Cosine
# ============================================================
alpha = 0.15

# ============================================================
# Span do filtro RC
# ============================================================
N_taps = 6

# ============================================================
# Valores de Eb/N0 em dB
# ============================================================
lista_EbN0_dB = [0, 4, 8, 12, 16, 20, 24]

# ============================================================
# Semente aleatória
# ============================================================
np.random.seed(42)

#%% ==========================================================
# 2. Constelações
# =============================================================

def gerar_constelacao_qam(M):

    # ========================================================
    # Número de níveis por eixo
    # ========================================================
    m = int(np.sqrt(M))

    # ========================================================
    # Níveis da constelação
    # ========================================================
    niveis = np.arange(
        -(m - 1),
        m,
        2,
        dtype=float
    )

    # ========================================================
    # Símbolos complexos da constelação
    # ========================================================
    simbolos_constelacao = np.array([
        complex(i, q)
        for q in niveis
        for i in niveis
    ])

    # ========================================================
    # Normalização:
    # Es = 1
    # ========================================================
    simbolos_constelacao /= np.sqrt(
        np.mean(np.abs(simbolos_constelacao) ** 2)
    )

    return simbolos_constelacao


def gerar_constelacao_psk(M, fase_inicial=0):

    # ========================================================
    # Fases da constelação
    # ========================================================
    fases = (
        2 * np.pi * np.arange(M) / M
        + fase_inicial
    )

    # ========================================================
    # Símbolos M-PSK
    # ========================================================
    simbolos_constelacao = np.exp(1j * fases)

    return simbolos_constelacao

#%% ==========================================================
# 3. Pulsos de transmissão
# =============================================================

def pulso_retangular(Ns):

    # ========================================================
    # Pulso retangular unitário
    # Energia normalizada
    # ========================================================
    p = np.ones(Ns) / np.sqrt(Ns)

    return p


def pulso_raised_cosine(Ns, alpha, N_taps):

    # ========================================================
    # Comprimento do filtro
    # ========================================================
    comprimento = 2 * N_taps * Ns + 1

    # ========================================================
    # Vetor temporal discreto
    # ========================================================
    n = np.arange(comprimento) - N_taps * Ns

    # ========================================================
    # Tempo normalizado
    # ========================================================
    t = n / Ns

    # ========================================================
    # Resposta impulsiva
    # ========================================================
    p = np.zeros(comprimento)

    for i, tempo in enumerate(t):

        # ====================================================
        # Caso t = 0
        # ====================================================
        if tempo == 0:

            p[i] = (
                1
                + alpha * (4 / np.pi - 1)
            )

        # ====================================================
        # Singularidade do RC
        # ====================================================
        elif (
            alpha != 0
            and
            np.isclose(
                abs(tempo),
                1 / (4 * alpha)
            )
        ):

            p[i] = (
                alpha / np.sqrt(2)
            ) * (
                (
                    1 + 2 / np.pi
                ) * np.sin(
                    np.pi / (4 * alpha)
                )
                +
                (
                    1 - 2 / np.pi
                ) * np.cos(
                    np.pi / (4 * alpha)
                )
            )

        # ====================================================
        # Expressão geral do Raised Cosine
        # ====================================================
        else:

            numerador = (
                np.sin(
                    np.pi * tempo * (1 - alpha)
                )
                +
                4 * alpha * tempo
                * np.cos(
                    np.pi * tempo * (1 + alpha)
                )
            )

            denominador = (
                np.pi
                * tempo
                * (
                    1 - (4 * alpha * tempo) ** 2
                )
            )

            p[i] = numerador / denominador

    # ========================================================
    # Normalização da energia:
    # Ep = 1
    # ========================================================
    p /= np.sqrt(np.sum(p ** 2))

    return p

#%% ==========================================================
# 4. Canal AWGN e transmissão passabanda
# =============================================================

def transmissao_awgn_passabanda(
    simbolos_tx,
    p,
    Ns,
    EbN0_dB,
    k
):

    quantidade_simbolos = len(simbolos_tx)

    # ========================================================
    # Upsampling
    # ========================================================
    s_baseband = np.zeros(
        quantidade_simbolos * Ns,
        dtype=complex
    )

    # ========================================================
    # Inserção de zeros
    # ========================================================
    s_baseband[::Ns] = simbolos_tx

    # ========================================================
    # Filtragem de transmissão
    # ========================================================
    s_I = np.convolve(
        s_baseband.real,
        p,
        mode='full'
    )

    s_Q = np.convolve(
        s_baseband.imag,
        p,
        mode='full'
    )

    # ========================================================
    # Atraso do filtro
    # ========================================================
    atraso = (len(p) - 1) // 2

    # ========================================================
    # Vetor temporal
    # ========================================================
    t = np.arange(len(s_I)) / fs

    # ========================================================
    # Portadoras ortogonais
    # ========================================================
    portadora_I = (
        np.sqrt(2)
        * np.cos(2 * np.pi * fc * t)
    )

    portadora_Q = (
        np.sqrt(2)
        * np.sin(2 * np.pi * fc * t)
    )

    # ========================================================
    # Sinal passabanda
    #
    # s_i(t) =
    # s_I(t)cos(2πfct) - s_Q(t)sin(2πfct)
    # ========================================================
    s_t = (
        s_I * portadora_I
        -
        s_Q * portadora_Q
    )

    # ========================================================
    # Relação Eb/N0 linear
    # ========================================================
    EbN0 = 10 ** (EbN0_dB / 10)

    # ========================================================
    # Energia por bit
    # ========================================================
    Eb = 1 / k

    # ========================================================
    # Variância do AWGN
    #
    # σ² = Eb / (2Eb/N0)
    # ========================================================
    sigma_n2 = Eb / (2 * EbN0)

    # ========================================================
    # Ruído gaussiano branco
    # ========================================================
    ruido = np.random.normal(
        0,
        np.sqrt(sigma_n2),
        len(s_t)
    )

    # ========================================================
    # Sinal recebido
    # ========================================================
    r_t = s_t + ruido

    #%% ======================================================
    # 5. Receptor coerente
    # =========================================================

    # ========================================================
    # Demodulação coerente
    # ========================================================
    r_I = r_t * portadora_I

    r_Q = r_t * (-portadora_Q)

    # ========================================================
    # Filtro casado
    # ========================================================
    z_I = np.convolve(
        r_I,
        p[::-1],
        mode='full'
    )

    z_Q = np.convolve(
        r_Q,
        p[::-1],
        mode='full'
    )

    # ========================================================
    # Atraso total do sistema
    # ========================================================
    atraso_total = (
        2 * atraso
        if len(p) > Ns
        else (atraso + (Ns - 1) // 2)
    )

    # ========================================================
    # Amostragem ótima
    # ========================================================
    inicio = atraso_total

    amostras_I = z_I[inicio::Ns][:quantidade_simbolos]

    amostras_Q = z_Q[inicio::Ns][:quantidade_simbolos]

    # ========================================================
    # Símbolos recebidos
    # ========================================================
    simbolos_rx = amostras_I + 1j * amostras_Q

    return simbolos_rx

#%% ==========================================================
# 6. Detector ML
# =============================================================

def detector_ml(
    simbolos_rx,
    constelacao
):

    simbolos_rx = np.array(simbolos_rx)

    # ========================================================
    # Distância euclidiana
    # ========================================================
    distancias = np.abs(
        simbolos_rx[:, None]
        -
        constelacao[None, :]
    )

    # ========================================================
    # Detector de mínima distância
    #
    # ŝ = arg min |r - s_k|
    # ========================================================
    indices_rx = np.argmin(
        distancias,
        axis=1
    )

    return indices_rx

#%% ==========================================================
# 7. Contagem de erros
# =============================================================

def calcular_erros_bit(
    indices_tx,
    indices_rx,
    k
):

    erros = 0

    for tx, rx in zip(indices_tx, indices_rx):

        bits_tx = format(tx, f'0{k}b')

        bits_rx = format(rx, f'0{k}b')

        for b_tx, b_rx in zip(bits_tx, bits_rx):

            if b_tx != b_rx:

                erros += 1

    return erros

#%% ==========================================================
# 8. BER teórica
# =============================================================

def funcao_Q(x):

    return 0.5 * erfc(x / np.sqrt(2))


def ber_teorica_mqam(M, EbN0_dB):

    EbN0 = 10 ** (np.array(EbN0_dB) / 10)

    k = np.log2(M)

    m = int(np.sqrt(M))

    # ========================================================
    # BER aproximada para M-QAM
    # ========================================================
    ber = (
        (
            2 * (1 - 1 / m)
        ) / k
    ) * funcao_Q(
        np.sqrt(
            (
                3 * k * EbN0
            ) / (M - 1)
        )
    )

    return ber


def ber_teorica_mpsk(M, EbN0_dB):

    EbN0 = 10 ** (np.array(EbN0_dB) / 10)

    k = np.log2(M)

    # ========================================================
    # BPSK
    # ========================================================
    if M == 2:

        return funcao_Q(
            np.sqrt(2 * EbN0)
        )

    # ========================================================
    # QPSK
    # ========================================================
    elif M == 4:

        return funcao_Q(
            np.sqrt(2 * EbN0)
        )

    # ========================================================
    # M-PSK geral
    # ========================================================
    else:

        ber = (
            2 / k
        ) * funcao_Q(
            np.sqrt(
                2 * k * EbN0
            )
            *
            np.sin(np.pi / M)
        )

        return ber

#%% ==========================================================
# 9. Simulação BER
# =============================================================

def executar_simulacao_ber(
    tipo_modulacao,
    ordens_M,
    tipo_pulso,
    numero_simbolos=50000
):

    resultados_ber = {}

    for M in ordens_M:

        # ====================================================
        # Bits por símbolo
        # ====================================================
        k = int(np.log2(M))

        print(
            f'{tipo_modulacao}-{M}'
            f' ({k} bits/símbolo)'
        )

        # ====================================================
        # Constelação
        # ====================================================
        if tipo_modulacao == 'QAM':

            constelacao = gerar_constelacao_qam(M)

        else:

            constelacao = gerar_constelacao_psk(M)

        # ====================================================
        # Pulso
        # ====================================================
        if tipo_pulso == 'NRZ':

            p = pulso_retangular(Ns)

        else:

            p = pulso_raised_cosine(
                Ns,
                alpha,
                N_taps
            )

        lista_ber = []

        for EbN0_dB in lista_EbN0_dB:

            # ================================================
            # Número de símbolos
            # ================================================
            Nsym = max(
                numero_simbolos,
                200 * M
            )

            # ================================================
            # Símbolos transmitidos
            # ================================================
            indices_tx = np.random.randint(
                0,
                M,
                Nsym
            )

            simbolos_tx = constelacao[indices_tx]

            # ================================================
            # Transmissão
            # ================================================
            simbolos_rx = transmissao_awgn_passabanda(
                simbolos_tx,
                p,
                Ns,
                EbN0_dB,
                k
            )

            # ================================================
            # Detector ML
            # ================================================
            indices_rx = detector_ml(
                simbolos_rx,
                constelacao
            )

            # ================================================
            # Erros de bit
            # ================================================
            numero_erros = calcular_erros_bit(
                indices_tx,
                indices_rx,
                k
            )

            # ================================================
            # BER
            # ================================================
            ber = (
                numero_erros
                /
                (Nsym * k)
            )

            lista_ber.append(
                max(ber, 1e-7)
            )

        resultados_ber[M] = lista_ber

    return resultados_ber

#%% ==========================================================
# 10. Plotagem das constelações
# =============================================================

def plotar_constelacoes(
    tipo_modulacao,
    ordens_M,
    tipo_pulso,
    EbN0_dB=16,
    numero_simbolos=2000
):

    figura, eixos = plt.subplots(
        len(ordens_M),
        2,
        figsize=(10, 4 * len(ordens_M))
    )

    figura.suptitle(
        f'Constelações {tipo_modulacao}'
        f' - Pulso {tipo_pulso}'
        f' - Eb/N0 = {EbN0_dB} dB',
        fontsize=14
    )

    for linha, M in enumerate(ordens_M):

        k = int(np.log2(M))

        # ====================================================
        # Constelação
        # ====================================================
        if tipo_modulacao == 'QAM':

            constelacao = gerar_constelacao_qam(M)

        else:

            constelacao = gerar_constelacao_psk(M)

        # ====================================================
        # Pulso
        # ====================================================
        if tipo_pulso == 'NRZ':

            p = pulso_retangular(Ns)

        else:

            p = pulso_raised_cosine(
                Ns,
                alpha,
                N_taps
            )

        # ====================================================
        # Símbolos transmitidos
        # ====================================================
        indices_tx = np.random.randint(
            0,
            M,
            numero_simbolos
        )

        simbolos_tx = constelacao[indices_tx]

        # ====================================================
        # Transmissão
        # ====================================================
        simbolos_rx = transmissao_awgn_passabanda(
            simbolos_tx,
            p,
            Ns,
            EbN0_dB,
            k
        )

        eixo_tx = eixos[linha, 0]

        eixo_rx = eixos[linha, 1]

        # ====================================================
        # Constelação transmitida
        # ====================================================
        eixo_tx.scatter(
            simbolos_tx.real,
            simbolos_tx.imag,
            s=10,
            alpha=0.5
        )

        eixo_tx.set_title(
            f'{tipo_modulacao}-{M} Transmitido'
        )

        eixo_tx.set_xlabel('In-Phase')

        eixo_tx.set_ylabel('Quadrature')

        eixo_tx.grid(True)

        eixo_tx.set_aspect('equal')

        # ====================================================
        # Constelação recebida
        # ====================================================
        eixo_rx.scatter(
            simbolos_rx.real,
            simbolos_rx.imag,
            s=10,
            alpha=0.5
        )

        eixo_rx.scatter(
            constelacao.real,
            constelacao.imag,
            marker='x',
            s=60
        )

        eixo_rx.set_title(
            f'{tipo_modulacao}-{M} Recebido'
        )

        eixo_rx.set_xlabel('In-Phase')

        eixo_rx.set_ylabel('Quadrature')

        eixo_rx.grid(True)

        eixo_rx.set_aspect('equal')

    plt.tight_layout()

    return figura

#%% ==========================================================
# 11. Plotagem BER
# =============================================================

def plotar_curvas_ber(
    resultados_ber,
    tipo_modulacao,
    ordens_M,
    tipo_pulso
):

    figura, eixo = plt.subplots(
        figsize=(10, 6)
    )

    cores = plt.cm.tab10(
        np.linspace(0, 0.9, len(ordens_M))
    )

    EbN0_continuo = np.linspace(
        0,
        24,
        300
    )

    for M, cor in zip(ordens_M, cores):

        # ====================================================
        # BER simulada
        # ====================================================
        eixo.semilogy(
            lista_EbN0_dB,
            resultados_ber[M],
            'o--',
            color=cor,
            label=f'{tipo_modulacao}-{M} Simulado'
        )

        # ====================================================
        # BER teórica
        # ====================================================
        if tipo_modulacao == 'QAM':

            ber_teorica = ber_teorica_mqam(
                M,
                EbN0_continuo
            )

        else:

            ber_teorica = ber_teorica_mpsk(
                M,
                EbN0_continuo
            )

        eixo.semilogy(
            EbN0_continuo,
            ber_teorica,
            '-',
            color=cor,
            label=f'{tipo_modulacao}-{M} Teórico'
        )

    eixo.set_xlabel(r'$E_b/N_0$ (dB)')

    eixo.set_ylabel('BER')

    eixo.set_title(
        f'BER - {tipo_modulacao}'
        f' - Pulso {tipo_pulso}'
    )

    eixo.grid(True, which='both')

    eixo.legend()

    eixo.set_xlim([0, 24])

    eixo.set_ylim([1e-6, 1])

    plt.tight_layout()

    return figura

#%% ==========================================================
# 12. Execução principal
# =============================================================

if __name__ == '__main__':

    # ========================================================
    # Ordens das modulações
    # ========================================================
    ordens_qam = [4, 16, 64]

    ordens_psk = [2, 4, 8, 16]

    # ========================================================
    # Tipos de pulso
    # ========================================================
    tipos_pulso = ['NRZ', 'RRC']

    # ========================================================
    # Pasta para artefatos gerados (PDFs)
    # ========================================================
    output_dir = os.path.join(os.getcwd(), 'output', 'lab2_artifacts')
    os.makedirs(output_dir, exist_ok=True)

    for tipo_pulso in tipos_pulso:

        print('\n' + '=' * 60)

        print(f'Pulso: {tipo_pulso}')

        print('=' * 60)

        # ====================================================
        # M-QAM
        # ====================================================

        print('\nSimulando M-QAM...\n')

        resultados_qam = executar_simulacao_ber(
            'QAM',
            ordens_qam,
            tipo_pulso,
            numero_simbolos=60000
        )

        # ====================================================
        # Constelações QAM
        # ====================================================
        figura_const_qam = plotar_constelacoes(
            'QAM',
            ordens_qam,
            tipo_pulso,
            EbN0_dB=16
        )

        figura_const_qam.savefig(
            os.path.join(output_dir, f'Constelacoes_QAM_{tipo_pulso}.pdf'),
            bbox_inches='tight'
        )

        plt.close(figura_const_qam)

        # ====================================================
        # BER QAM
        # ====================================================
        figura_ber_qam = plotar_curvas_ber(
            resultados_qam,
            'QAM',
            ordens_qam,
            tipo_pulso
        )

        figura_ber_qam.savefig(
            os.path.join(output_dir, f'BER_QAM_{tipo_pulso}.pdf'),
            bbox_inches='tight'
        )

        plt.close(figura_ber_qam)

        # ====================================================
        # M-PSK
        # ====================================================

        print('\nSimulando M-PSK...\n')

        resultados_psk = executar_simulacao_ber(
            'PSK',
            ordens_psk,
            tipo_pulso,
            numero_simbolos=60000
        )

        # ====================================================
        # Constelações PSK
        # ====================================================
        figura_const_psk = plotar_constelacoes(
            'PSK',
            ordens_psk,
            tipo_pulso,
            EbN0_dB=16
        )

        figura_const_psk.savefig(
            os.path.join(output_dir, f'Constelacoes_PSK_{tipo_pulso}.pdf'),
            bbox_inches='tight'
        )

        plt.close(figura_const_psk)

        # ====================================================
        # BER PSK
        # ====================================================
        figura_ber_psk = plotar_curvas_ber(
            resultados_psk,
            'PSK',
            ordens_psk,
            tipo_pulso
        )

        figura_ber_psk.savefig(
            os.path.join(output_dir, f'BER_PSK_{tipo_pulso}.pdf'),
            bbox_inches='tight'
        )

        plt.close(figura_ber_psk)

    print('\nArquivos PDF gerados com sucesso!')
    print(f'Saved PDFs to: {output_dir}')