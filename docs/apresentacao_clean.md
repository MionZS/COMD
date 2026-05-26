# Apresentação

Resumo conciso da implementação e do fluxo de simulação usados nos notebooks.

## 1. Objetivo

Documentar as principais funções e o fluxo da simulação: geração de bits, mapeamento em símbolos (Gray), pulse shaping, modulação em portadora, canal AWGN, demodulação e decisão por distância mínima, e cálculo de BER.

## 2. Importações principais

- `marimo` — ferramenta de células/notebook usada no projeto.
- `matplotlib` — geração de figuras.
- `numpy` — operações vetoriais e geração de ruído.
- `scipy.special` — `erfc` para curvas teóricas de BER (Q‑function: $Q(x)=\tfrac{1}{2}\mathrm{erfc}(x/\sqrt{2})$).
- `pathlib` / `shutil` — manipulação de caminhos e arquivos.

## 3. Definições de parâmetros (exemplos)

- `fc = 10.0` — frequência da portadora (Hz, unidade arbitrária consistente com escala).
- `os = 4` — fator de sobreamostragem (samples por símbolo).
- `alpha = 0.15` — roll‑off do filtro RRC.
- `ebn0_points` — lista de pontos de Eb/N0 em dB para simulação.
- `modulation_cases` — lista de modulações (ex.: PSK, QAM) e ordens `M`.
- `num_bits_target` — número alvo de bits por simulação (ex.: 20_000_000).
- `output_path` — pasta onde os artefatos gráficos e numéricos são salvos.

## 4. Codificação Gray (resumo)

- `int_to_gray(n)` — converte inteiro `n` para código Gray via XOR bitwise: `n ^ (n >> 1)`.
- `gray_to_int(g)` — converte Gray de volta para inteiro (iterativo usando XOR progressivo).

Vantagem: ordena símbolos de modo que símbolos adjacentes diferem em apenas 1 bit, reduzindo o impacto de erros de símbolo no BER.

## 5. Constelações e mapeamento

- `qam_constellation(M)` — gera constelação QAM quadrada (valores complexos, centrados em zero).
- `psk_constellation(M)` — gera pontos igualmente espaçados em fase: exp(1j*2π*k/M).
- `bits_to_symbols(bits, M)` — agrupa bits em palavras de `log2(M)`, converte para índices Gray e mapeia para símbolos complexos.
- `symbols_to_bits(rx_symbols, constellation)` — detecção por mínima distância euclidiana; reverte mapeamento Gray e reconstrói o vetor de bits.

## 6. Pulsos de transmissão

- `pulse_coeffs(name, os, alpha)` — retorna o vetor de amostras do pulso.
  - `nrz` — pulso retangular (unipolar/on‑off) com `os` amostras por símbolo.
  - `rrc` — pulso root‑raised cosine com parâmetro `alpha` e extensão adequada.

O formato do pulso altera a forma temporal do sinal transmitido e, após o filtro casado e amostragem, a dispersão da nuvem recebida (e o BER), embora a constelação ideal (símbolo em plane complexo) permaneça a mesma.

## 7. Fluxo da simulação (`simulate_link`)

Fluxo resumido:

```mermaid
flowchart LR
  A[Gerar bits TX] --> B[Mapeamento bits → símbolos (Gray)]
  B --> C[Upsample e Pulse Shaping (convolve)]
  C --> D[Modulação em portadora (I/Q)]
  D --> E[Canal AWGN (adiciona ruído)]
  E --> F[Demodulação coerente]
  F --> G[Filtro casado (convolve com pulso invertido)]
  G --> H[Amostragem e decisão por mínima distância]
  H --> I[Cálculo de BER]
```

Parâmetros principais da função:

- `kind` — tipo de modulação ("psk" / "qam").
- `M` — ordem da modulação (número de símbolos).
- `pulse_name` — "nrz" ou "rrc".
- `ebn0_db` — Eb/N0 em dB.
- `num_symbols` — número de símbolos simulados.
- `rng` — gerador aleatório (seed controlada para reprodutibilidade).
- `alpha`, `fc`, `os` — parâmetros de pulso, portadora e oversampling.

Processamento interno (resumo técnico):

- Gera vetor `bits_tx` e transforma em `symbols_tx` via `bits_to_symbols`.
- Constrói `upsampled` e aplica `np.convolve(upsampled, pulse, mode='full')` → `shaped`.
- Constrói a portadora e gera `tx = sqrt(2) * (Re(shaped)*cos - Im(shaped)*sin)` (forma passante).
- Calcula energia média por bit e deduz `sigma` do ruído a partir de `Eb/N0`.
- `rx = tx + sigma * rng.normal(size=tx.shape)` simula AWGN.
- Demodula em I/Q, aplica filtro casado `np.convolve(bb_rx, pulse[::-1].conj(), mode='full')`.
- Compensa atraso e amostra nos instantes corretos; aplica `symbols_to_bits` para decisão.
- Compara `bits_tx` com `bits_rx` e computa BER (proporção de bits incorretos).

## 8. Observações importantes

- A constelação teórica (posições dos símbolos) não muda com o tipo de pulso; porém o pulso influencia a forma do sinal transmitido no tempo e, após canal e filtragem, a dispersão das estimativas amostradas no receptor.
- `NRZ unipolar` representa o bit 0 como nível 0 (on‑off); `NRZ polar` usa níveis ±A.
- Para estimativas estatisticamente robustas do BER recomendamos usar um `num_bits_target` grande (por exemplo, 20e6) e parar por critério de número mínimo de erros coletados.

## 9. Onde estão as funções

As funções e células principais estão em:

- `src/trabalho2/trabalho2_mvp_marimo_v3.py`
- `src/trabalho2/trabalho2_mvp_slides.py`

---

Se quiser, ajusto o tom (mais didático ou mais técnico), adiciono exemplos rápidos de uso/run, ou gero um diagrama mais detalhado do pipeline.
