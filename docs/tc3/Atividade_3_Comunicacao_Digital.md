# Trabalho Computacional 2

**Disciplina:** TE903/EELT7026 – Comunicação Digital  
**Professor:** Ândrei Camponogara

## Objetivo

Este trabalho computacional propõe a simulação e avaliação de desempenho de um sistema **OFDM** empregando a modulação **16-QAM** em banda-base.

O sistema transmitirá sinais através de um canal dispersivo no tempo, isto é, um canal com **multipercurso**, sujeito a ruído aditivo modelado como processo Gaussiano branco de média zero.

O objetivo é avaliar a qualidade do sinal em cada subcanal, visualizar os efeitos do desvanecimento seletivo em frequência e aplicar uma técnica básica de **bit-loading**, por meio do descarte de portadoras.

## Entrega

A entrega deverá conter:

- Relatório escrito no formato de artigo no padrão IEEE;
- Código em Python utilizado para gerar os resultados.

**Data de entrega:** 25 de junho de 2026.

## Especificações do sistema

A simulação computacional deverá ser desenvolvida adotando as premissas descritas abaixo.

| Parâmetro | Especificação |
|---|---|
| Modulação | 16-QAM |
| Tamanho do bloco OFDM | \(N = 32\) subportadoras |
| Resposta ao impulso do canal | \(h[n] = [0.3, -0.5, 0, 1, 0.2, -0.3]^T\) |
| Prefixo cíclico | Deve ser projetado com o tamanho mínimo para evitar interferência intersimbólica |
| Equalização | Zero-forcing, ZF, no domínio da frequência |

## Atividade

Com base nas especificações acima, desenvolva um script para gerar, transmitir, equalizar os sinais e extrair os fenômenos físicos e estatísticos do sistema. O trabalho deve apresentar os itens solicitados a seguir.

## 1. Perfil do canal no domínio da frequência

Trace o gráfico de amplitude do ganho das subportadoras:

\[
|H[k]|, \quad k = 0, 1, \ldots, N - 1.
\]

Além disso, identifique explicitamente quais são os **5 subcanais com o pior desempenho**, isto é, aqueles com maior atenuação.

## 2. Espalhamento da constelação

Fixe a SNR média do canal em:

\[
\text{SNR} = 30\,\text{dB}.
\]

Em seguida:

- Plote a constelação equalizada, em diagrama de dispersão, para o subcanal 1, considerado canal moderado;
- Plote a constelação equalizada para o subcanal 10, considerado canal bom;
- Plote a constelação equalizada para o subcanal 15, considerado canal pobre;
- Plote um quarto gráfico com as saídas misturadas de todas as portadoras;
- Comente o contraste visual na qualidade da recepção.

## 3. Análise de taxa de erro de símbolo

Em escala semilogarítmica, trace as curvas de **SER**, taxa de erro de símbolo, em função da SNR, variando de:

\[
0\,\text{dB} \leq \text{SNR} \leq 30\,\text{dB}.
\]

O gráfico deve conter:

1. A curva de todas as 32 subportadoras individuais;
2. A curva da SER do canal ideal;
3. A SER média global do sistema OFDM.

## 4. Carregamento de bits: bit-loading extremo

Sabendo que o desempenho médio do OFDM é severamente arrastado para baixo pelas portadoras em desvanecimento profundo, implemente o descarte das **5 piores portadoras** encontradas no item 1.

Em seguida, trace um novo gráfico comparando:

- SER média original, usando todas as 32 portadoras;
- SER do canal ideal;
- Nova SER média com a desabilitação das 5 piores portadoras.

Na conclusão do relatório, explique por que a melhoria obtida é significativa.
