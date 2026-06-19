# PRD - Simulador OFDM 16-QAM em canal multipercurso

## 1. Objetivo

Construir e validar um simulador em Python de um sistema OFDM em banda-base com modulação 16-QAM, 32 subportadoras, prefixo cíclico mínimo, canal FIR multipercurso e equalização zero-forcing no domínio da frequência. O simulador deve gerar os gráficos e métricas exigidos no Trabalho Computacional 2 de Comunicação Digital.

O produto final não é apenas um script que roda. Ele deve produzir resultados fisicamente interpretáveis: perfil de ganho por subportadora, constelações equalizadas em portadoras específicas, curvas SER por subportadora, SER média do sistema, curva de canal ideal e comparação de desempenho antes/depois do descarte das piores portadoras.

## 2. Entradas fixas do problema

- Modulação: 16-QAM quadrada.
- Número de subportadoras: N = 32.
- Bits por símbolo QAM: b = log2(16) = 4.
- Canal discreto: h[n] = [0.3, -0.5, 0, 1, 0.2, -0.3]^T.
- Ordem do canal: L = len(h) - 1 = 5.
- Prefixo cíclico mínimo: N_CP = 5.
- Equalizador: zero-forcing no domínio da frequência.
- SNR para constelações: 30 dB.
- SNR para curvas SER: 0 a 30 dB.
- Portadoras exigidas para constelação: k = 1, k = 10 e k = 15.

## 3. Fontes teóricas revisadas e uso no projeto

### 3.1 Teoria do zip `teoria.zip`

A parte reaproveitável é: mapeamento Gray, normalização de constelação QAM, relação entre energia de símbolo e ruído, leitura de constelações, SER/BER por Monte Carlo e cuidado estatístico com simulações em alto SNR.

A parte que deve ficar fora deste projeto: códigos de linha, NRZ/RRC como cadeia principal, modulação passabanda, receptor coerente por misturador e filtro casado. O projeto atual é OFDM em banda-base discreta. A física de pulso e portadora pode aparecer apenas como contexto, não como bloco implementado.

### 3.2 Slides do professor

- Aulas 12-13: base de QAM M-ária, constelação 16-QAM e energia média.
- Aulas 18-19: canal multipercurso, ISI, canal seletivo em frequência, equalização ZF e amplificação de ruído.
- Aulas 22-23: OFDM, IFFT/FFT, prefixo cíclico, diagonalização do canal por DFT e equalização por subportadora.
- Aula 9: formato de relatório em estilo IEEE, figuras citadas no texto e interpretação dos resultados.

### 3.3 Lathi

O material do Lathi deve ser usado como apoio conceitual para: canais linearmente distorcidos, equalização, QAM, OFDM, prefixo cíclico e desempenho em canais seletivos. Não é necessário importar derivações longas para o relatório. Use como suporte para justificar as escolhas de modelo e interpretação.

## 4. Convenções obrigatórias de simulação

### 4.1 Indexação das subportadoras

Usar a indexação Python/DFT: k = 0, 1, ..., 31. Não usar `fftshift` para decidir as piores portadoras. `fftshift` pode ser usado em figura alternativa, mas a tabela exigida deve manter a indexação original do enunciado.

### 4.2 Normalização da 16-QAM

A constelação deve ser normalizada para energia média de símbolo unitária:

- níveis brutos: {-3, -1, +1, +3} em I e Q;
- energia média bruta: 10;
- símbolo normalizado: s = (I + jQ) / sqrt(10);
- Es = E{|s|^2} = 1.

Isso simplifica a interpretação da SNR e evita que o ruído dependa artificialmente da escala escolhida para a constelação.

### 4.3 Convenção de SNR recomendada

Definir SNR média como a SNR média pós-canal, antes da equalização, média sobre todas as subportadoras:

SNR_avg = E{|H[k] X[k]|^2}_k / sigma_v^2.

Com Es = 1:

sigma_v^2 = mean(|H[k]|^2) / SNR_linear.

Como mean(|H[k]|^2) = sum(|h[n]|^2) = 1.47, a variância complexa do ruído no domínio da frequência deve ser:

sigma_v^2 = 1.47 / SNR_linear.

Se o ruído for adicionado no tempo usando `np.fft.ifft` e `np.fft.fft` padrão do NumPy, a variância complexa por amostra deve ser:

sigma_t^2 = sigma_v^2 / N = 1.47 / (32 * SNR_linear).

Isso evita o erro clássico de adicionar ruído com potência N vezes maior ou menor depois da FFT.

### 4.4 FFT/IFFT

Usar consistentemente:

```python
x = np.fft.ifft(X, n=N)
Y = np.fft.fft(y, n=N)
H = np.fft.fft(h, n=N)
```

Com essa convenção, após CP suficiente e remoção do CP:

Y[k] = H[k] X[k] + V[k].

## 5. Cálculos determinísticos de validação

### 5.1 Prefixo cíclico mínimo

O canal possui 6 coeficientes, portanto sua memória é L = 5. O prefixo cíclico mínimo que evita ISI entre blocos OFDM é:

N_CP = L = 5.

### 5.2 Ganho em frequência do canal

Calcular:

H[k] = FFT_32{h[n]}.

As cinco piores subportadoras por menor |H[k]| são:

| rank | k | |H[k]| | ganho relativo (dB) |
|---:|---:|---:|---:|
| 1 | 15 | 0.275333 | -11.203 dB |
| 2 | 17 | 0.275333 | -11.203 dB |
| 3 | 16 | 0.300000 | -10.458 dB |
| 4 | 14 | 0.367628 | -8.692 dB |
| 5 | 18 | 0.367628 | -8.692 dB |

Essas são as portadoras a desabilitar no bit-loading extremo: {14, 15, 16, 17, 18}. Em ordem de pior desempenho: [15, 17, 16, 14, 18].

### 5.3 Portadoras da constelação a 30 dB

- k = 10: bom canal, |H[10]| = 1.773379, ganho relativo = +4.976 dB.
- k = 1: canal moderado, |H[1]| = 0.708341, ganho relativo = -2.995 dB.
- k = 15: canal pobre, |H[15]| = 0.275333, ganho relativo = -11.203 dB.

Depois do ZF, o sinal médio volta para os pontos ideais, mas o ruído é multiplicado por 1/H[k]. Portanto, k = 15 deve apresentar nuvem muito mais espalhada que k = 10.

## 6. Requisitos funcionais

### RF01 - Gerar constelação 16-QAM normalizada

O simulador deve mapear grupos de 4 bits em símbolos 16-QAM normalizados com Es = 1. O mapeamento preferido é Gray por eixo. O detector deve usar decisão por vizinho mais próximo.

Critério de aceite: a energia média da constelação gerada deve ser aproximadamente 1 e os pontos devem pertencer ao conjunto (±1 ± j, ±1 ± 3j, ±3 ± j, ±3 ± 3j)/sqrt(10).

### RF02 - Gerar blocos OFDM

O simulador deve organizar símbolos QAM em blocos X_i[k] com N = 32 subportadoras.

Critério de aceite: cada bloco OFDM deve conter exatamente 32 símbolos QAM antes da IFFT.

### RF03 - Aplicar IFFT e prefixo cíclico

O simulador deve converter X_i[k] para x_i[n] por IFFT e inserir prefixo cíclico de 5 amostras copiando as últimas 5 amostras do bloco.

Critério de aceite: o bloco transmitido deve ter 37 amostras: 5 de CP + 32 úteis.

### RF04 - Transmitir pelo canal multipercurso

O simulador deve aplicar convolução linear com h[n]. A cadeia deve preservar a separação por blocos de modo que, após remoção do CP, a relação útil seja equivalente a convolução circular.

Critério de aceite: em simulação sem ruído, após CP, canal, remoção de CP, FFT e ZF, a diferença entre X_hat e X deve ser próxima de erro numérico de máquina.

### RF05 - Adicionar AWGN complexo

O simulador deve adicionar ruído complexo circular gaussiano de média zero. A potência deve obedecer à convenção de SNR adotada e registrada no relatório.

Critério de aceite: para SNR alta e canal ideal, a SER deve cair rapidamente e aproximar a curva teórica/simulada de 16-QAM AWGN.

### RF06 - Equalizar por ZF no domínio da frequência

O simulador deve calcular H[k] = FFT_32{h[n]} e aplicar:

X_hat[k] = Y[k] / H[k].

Critério de aceite: os subcanais com menor |H[k]| devem apresentar maior espalhamento de constelação e maior SER, mesmo após equalização.

### RF07 - Gerar gráfico |H[k]|

O simulador deve plotar |H[k]| para k = 0,...,31 e destacar explicitamente as 5 piores portadoras.

Critério de aceite: o gráfico e/ou tabela devem identificar k = 15, 17, 16, 14 e 18 como piores.

### RF08 - Gerar constelações equalizadas

Com SNR média de 30 dB, o simulador deve gerar quatro gráficos:

1. subcanal k = 1;
2. subcanal k = 10;
3. subcanal k = 15;
4. mistura de todas as subportadoras.

Critério de aceite: k = 10 deve ser visualmente mais concentrado, k = 1 intermediário e k = 15 bem mais disperso. A mistura total deve parecer heterogênea porque combina portadoras com SNRs efetivas diferentes.

### RF09 - Calcular SER por subportadora

Para SNR de 0 a 30 dB, o simulador deve calcular a SER de cada uma das 32 subportadoras:

SER_k = erros_de_símbolo_na_portadora_k / símbolos_transmitidos_na_portadora_k.

Critério de aceite: o gráfico semilog deve conter 32 curvas individuais, a SER média global do OFDM e a curva de canal ideal.

### RF10 - Implementar descarte das 5 piores portadoras

O simulador deve desabilitar as portadoras {14, 15, 16, 17, 18}. Elas não devem entrar na média da SER carregada.

Critério de aceite: o gráfico final deve comparar:

- SER média original com 32 portadoras;
- SER do canal ideal;
- SER média com 27 portadoras ativas.

A curva com descarte deve melhorar muito em médio/alto SNR, porque remove os subcanais que amplificam mais ruído no ZF.

## 7. Requisitos estatísticos

- Usar semente fixa para reprodutibilidade, por exemplo `rng = np.random.default_rng(42)`.
- Para cada ponto de SNR, simular número suficiente de blocos OFDM.
- Evitar conclusões fortes quando SER = 0 em alto SNR; isso pode significar apenas ausência de erro observado.
- Para curvas limpas, usar ao menos dezenas ou centenas de milhares de símbolos por subportadora, ou um critério adaptativo de parada por número mínimo de erros.
- Para plot semilog, substituir zeros por um piso gráfico apenas na visualização, por exemplo `1/(num_symbols + 1)`, mas manter o valor real nos dados exportados.

## 8. Saídas obrigatórias

O projeto deve gerar os seguintes arquivos ou figuras:

1. `fig_01_channel_gain.png`: |H[k]| por subportadora, com as 5 piores destacadas.
2. `fig_02_constellation_k1.png`: constelação equalizada para k = 1 a 30 dB.
3. `fig_03_constellation_k10.png`: constelação equalizada para k = 10 a 30 dB.
4. `fig_04_constellation_k15.png`: constelação equalizada para k = 15 a 30 dB.
5. `fig_05_constellation_all.png`: constelação equalizada misturando todas as portadoras.
6. `fig_06_ser_all_subcarriers.png`: 32 curvas individuais + canal ideal + SER média OFDM.
7. `fig_07_ser_bit_loading.png`: comparação entre média original, ideal e descarte das 5 piores.
8. `results_summary.csv`: tabela com SNR, SER por portadora, SER média, SER ideal e SER com descarte.
9. `channel_summary.csv`: k, H[k], |H[k]|, ganho em dB e flag de portadora descartada.

## 9. Estrutura recomendada do código

```text
main.py
src/
  qam.py              # constelação, mapper, detector
  ofdm.py             # IFFT, CP, FFT, canal, ZF
  metrics.py          # SER, agregações, SNR
  plots.py            # figuras
  validation.py       # testes determinísticos
outputs/
  figures/
  tables/
```

Funções mínimas:

```python
qam16_constellation(normalized=True)
map_bits_to_qam16(bits)
detect_qam16(symbols)
ofdm_modulate(X, n_cp)
ofdm_demodulate(rx_block, n_cp)
apply_channel(x_cp, h)
add_awgn(x, snr_db, convention)
compute_channel_response(h, N)
zf_equalize(Y, H)
ser_per_subcarrier(X, X_hat_detected)
```

## 10. Testes de validação

### Teste 1 - Energia da constelação

A média de |s|^2 da 16-QAM normalizada deve ser 1.

### Teste 2 - CP mínimo

`n_cp == len(h) - 1 == 5`.

### Teste 3 - Canal sem ruído

Com ruído desligado, a cadeia completa deve recuperar os símbolos transmitidos após ZF, salvo erro numérico.

### Teste 4 - Piores portadoras

A ordenação crescente de |H[k]| deve começar por:

[15, 17, 16, 14, 18].

### Teste 5 - Hierarquia visual das constelações

A 30 dB:

- k = 10 deve ter menor espalhamento;
- k = 1 deve ter espalhamento intermediário;
- k = 15 deve ter maior espalhamento.

### Teste 6 - Curvas SER

As curvas SER devem cair com aumento de SNR. As piores portadoras devem cair mais lentamente. A SER média original deve ser degradada pelas portadoras em desvanecimento profundo.

### Teste 7 - Bit-loading extremo

Após remover {14, 15, 16, 17, 18}, a SER média deve melhorar fortemente em SNR médio/alto. A justificativa técnica é que o ZF remove a distorção multiplicativa, mas transforma o ruído em V[k]/H[k]. Quando |H[k]| é pequeno, a variância de ruído pós-equalização cresce como 1/|H[k]|^2.

## 11. Valores de referência para sanity check

Com h[n] sem normalização:

- sum(|h[n]|^2) = mean(|H[k]|^2) = 1.47.
- |H[1]| = 0.708341.
- |H[10]| = 1.773379.
- |H[15]| = 0.275333.

Com SNR média pós-canal de 30 dB, SNR efetiva relativa das portadoras selecionadas:

- k = 10: cerca de 33.30 dB.
- k = 1: cerca de 25.33 dB.
- k = 15: cerca de 17.12 dB.

Esses valores explicam por que k = 15 ainda pode ter erros visíveis mesmo quando a SNR média do canal é alta.

## 12. Riscos técnicos

1. Erro de normalização de ruído por causa da escala FFT/IFFT do NumPy.
2. Usar CP menor que 5 e introduzir ISI entre blocos.
3. Usar `fftshift` na hora de escolher os piores k e trocar a indexação do enunciado.
4. Comparar SER média com canal ideal sem declarar a convenção de SNR.
5. Reportar SER = 0 como se fosse probabilidade nula, quando pode ser apenas limitação de Monte Carlo.
6. Usar detector incompatível com o mapeamento da constelação.
7. Fazer a média de SER com as portadoras descartadas ainda incluídas como zeros; isso falseia o resultado. A média carregada deve considerar apenas as 27 portadoras ativas.

## 13. Estrutura sugerida do relatório IEEE

1. Resumo: objetivo, sistema OFDM/16-QAM, canal multipercurso, ZF, efeito do desvanecimento e bit-loading.
2. Introdução: problema de canais seletivos em frequência e motivação para OFDM.
3. Modelo do sistema: 16-QAM, OFDM, CP, canal, ruído e ZF.
4. Metodologia: parâmetros, número de blocos, SNR, cálculo de SER e critério de descarte.
5. Resultados:
   - perfil |H[k]|;
   - constelações equalizadas;
   - SER por subportadora;
   - bit-loading extremo.
6. Conclusão: ZF corrige a atenuação complexa, mas amplifica ruído em subcanais fracos; remover portadoras em fade profundo melhora a SER média porque evita transmitir onde a SNR efetiva é muito baixa.

## 14. Definição de pronto

O projeto está pronto quando:

- todos os gráficos exigidos foram gerados;
- as piores portadoras batem com os valores determinísticos do canal;
- a cadeia sem ruído recupera os símbolos;
- a curva ideal serve como referência plausível;
- a curva com descarte melhora a SER média em SNR médio/alto;
- o relatório explica o fenômeno físico, não apenas mostra gráficos.
