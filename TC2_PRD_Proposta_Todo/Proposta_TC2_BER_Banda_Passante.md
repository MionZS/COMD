# Proposta - Trabalho Computacional 2

**Disciplina:** TE903/EELT7026 - Comunicação Digital  
**Tema:** Análise comparativa de BER para modulações M-QAM e M-PSK em banda passante sob canal AWGN  
**Autor:** Gabriel Montebeleri  
**Data de entrega:** 21 de maio de 2026

---

## 1. Título Proposto

**Análise Comparativa de Desempenho BER para Modulações M-QAM e M-PSK em Banda Passante sob Canal AWGN**

---

## 2. Resumo da Proposta

Este trabalho propõe a implementação de uma simulação computacional em Python para avaliar a taxa de erro de bit, BER, de diferentes esquemas de modulação digital em banda passante. Serão analisadas modulações M-QAM e M-PSK em um canal com ruído aditivo branco gaussiano, considerando diferentes valores de relação Eb/N0.

A simulação seguirá a cadeia completa de um sistema de comunicação digital: geração de bits aleatórios, mapeamento em símbolos complexos, formatação de pulso, modulação em banda passante, adição de ruído, demodulação coerente, filtragem casada, amostragem, decisão e cálculo da BER.

Os resultados serão apresentados em formato de artigo IEEE, contendo constelações dos símbolos no transmissor e no receptor, além de gráficos comparativos entre BER simulada e curvas teóricas.

---

## 3. Motivação

A BER é uma das métricas mais importantes para avaliar a robustez de sistemas de comunicação digital. Modulações de maior ordem, como 64-QAM ou 16-PSK, aumentam a quantidade de bits transmitidos por símbolo, mas reduzem a distância entre pontos da constelação, tornando o sistema mais sensível ao ruído.

A comparação entre M-QAM e M-PSK permite visualizar o compromisso entre eficiência espectral e desempenho em presença de AWGN. Além disso, a comparação entre pulsos NRZ e RRC permite avaliar o papel da formatação de pulso e do filtro casado na recuperação dos símbolos transmitidos.

---

## 4. Objetivos

### 4.1 Objetivo geral

Simular e comparar o desempenho de modulações M-QAM e M-PSK em banda passante sob canal AWGN, utilizando a BER como métrica principal.

### 4.2 Objetivos específicos

- Implementar modulações M-QAM para b = 2, 4 e 6 bits por símbolo.
- Implementar modulações M-PSK para b = 1, 2, 3 e 4 bits por símbolo.
- Implementar pulsos de transmissão NRZ e RRC com alpha = 0,15.
- Simular o sistema para Eb/N0 = 0, 4, 8, 12, 16, 20 e 24 dB.
- Gerar constelações transmitidas e recebidas após amostragem.
- Calcular BER simulada por Monte Carlo.
- Comparar os resultados simulados com curvas teóricas de BER.
- Redigir relatório final no formato de artigo IEEE.

---

## 5. Metodologia Proposta

### 5.1 Transmissor

O transmissor será iniciado pela geração de uma sequência pseudoaleatória de bits. Esses bits serão agrupados em blocos de tamanho b, de acordo com a modulação analisada. Cada bloco será convertido em um símbolo complexo pertencente à constelação M-QAM ou M-PSK.

As constelações serão normalizadas de modo que a energia média de símbolo seja Ex = 1. Dessa forma, a energia por bit será calculada como Eb = Ex/b.

Após o mapeamento, os símbolos serão submetidos a upsampling e filtrados por um pulso de transmissão NRZ ou por um filtro raiz do cosseno levantado, com fator de roll-off alpha = 0,15.

O sinal em banda base será decomposto em componentes em fase e quadratura. A translação para banda passante será realizada por portadoras ortogonais de frequência fc = 10 Hz.

### 5.2 Canal

O canal será modelado por ruído aditivo branco gaussiano. Para cada valor de Eb/N0, será calculado N0 e, em seguida, a variância do ruído:

```text
sigma_V^2 = N0 / 2
```

O ruído será somado ao sinal transmitido em banda passante.

### 5.3 Receptor

No receptor, será realizada demodulação coerente por multiplicação com as portadoras locais. Em seguida, os ramos em fase e quadratura passarão pelo filtro casado p(Ts - t). Após a filtragem, o sinal será amostrado em t = kTs.

As amostras complexas obtidas após a amostragem serão usadas tanto para plotar as constelações recebidas quanto para realizar a decisão por distância euclidiana mínima.

### 5.4 Cálculo de BER

Os símbolos detectados serão convertidos novamente em bits. A BER será calculada pela razão entre o número de bits errados e o número total de bits transmitidos.

### 5.5 Comparação teórica

As curvas de BER simuladas serão comparadas com expressões teóricas aproximadas para BPSK, M-PSK e M-QAM quadrada. Será dada atenção ao uso de codificação Gray, pois as fórmulas teóricas clássicas assumem que símbolos adjacentes diferem por apenas um bit.

---

## 6. Parâmetros de Simulação

| Parâmetro | Valor |
|---|---:|
| fc | 10 Hz |
| os | 4 |
| fs | 40 Hz |
| Ts | 1/fc |
| SPS | 4 |
| Eb/N0 | 0, 4, 8, 12, 16, 20, 24 dB |
| Pulso 1 | NRZ |
| Pulso 2 | RRC, alpha = 0,15 |
| QAM | 4, 16, 64 |
| PSK | 2, 4, 8, 16 |

---

## 7. Resultados Esperados

Espera-se que a BER diminua conforme Eb/N0 aumenta. Também se espera que, para um mesmo Eb/N0, modulações de maior ordem apresentem maior BER, pois possuem pontos mais próximos na constelação.

As constelações recebidas devem apresentar maior dispersão para baixos valores de Eb/N0 e maior concentração em torno dos pontos ideais para altos valores de Eb/N0.

As curvas simuladas devem seguir a tendência das curvas teóricas, admitindo pequenas diferenças devido ao número finito de bits, à discretização temporal, ao mapeamento usado e à normalização dos pulsos.

---

## 8. Estrutura Sugerida do Artigo IEEE

1. Abstract.
2. Index Terms.
3. Introdução.
4. Fundamentação teórica.
5. Metodologia.
6. Resultados numéricos.
7. Discussão.
8. Considerações finais.
9. Referências.

---

## 9. Cronograma

| Etapa | Descrição | Prioridade |
|---|---|---:|
| 1 | Validar cadeia mínima com QPSK/4-QAM e pulso NRZ | Alta |
| 2 | Implementar todas as ordens M-QAM e M-PSK | Alta |
| 3 | Implementar pulso RRC e filtro casado | Alta |
| 4 | Validar BER simulada contra curva teórica | Alta |
| 5 | Rodar simulação final com número elevado de bits | Alta |
| 6 | Gerar figuras finais | Alta |
| 7 | Escrever relatório IEEE | Alta |
| 8 | Revisar consistência entre código, figuras e texto | Alta |

---

## 10. Conclusão da Proposta

A proposta atende ao escopo do Trabalho Computacional 2 ao contemplar a simulação completa do sistema em banda passante, a análise de BER para diferentes modulações digitais, a presença de canal AWGN, a comparação entre pulsos de transmissão e a validação por curvas teóricas. A estrutura prevista permite gerar resultados adequados para discussão em relatório no padrão IEEE.
