# Teoria 3 — Decisão ML, geometria da constelação e probabilidade de erro

## Decisão de máxima verossimilhança

Depois da amostragem, o receptor precisa decidir qual símbolo foi transmitido. Como os símbolos são equiprováveis e o ruído é gaussiano, a regra ótima é a **máxima verossimilhança** (ML). Em AWGN, ela coincide com a menor distância euclidiana.

Se $\mathcal A$ é a constelação, então a decisão é

$$
\hat a=\arg\min_{a\in\mathcal A}|z-a|^2
$$

Ou seja: o símbolo detectado é o ponto da constelação mais próximo da amostra recebida.

Essa regra explica por que a visualização RX no notebook é tão útil: a nuvem de pontos e os limites de decisão ficam intuitivos.

## Regiões de decisão

Cada símbolo ocupa uma região do plano complexo. Em PSK, as regiões são setores angulares; em QAM, são células retangulares na grade I/Q.

O ruído é a variável que cruza fronteiras. Quanto maior a distância entre os pontos da constelação, menor a chance de o ruído empurrar uma amostra para a vizinhança errada.

Isso liga geometria e probabilidade: a BER não depende apenas de quantos pontos existem, mas de como eles estão espaçados.

## Função Q e caudas gaussianas

A probabilidade de erro em AWGN é governada pelas caudas da gaussiana. A função $Q$ aparece naturalmente:

$$
Q(x)=\frac{1}{\sqrt{2\pi}}\int_x^{\infty}e^{-u^2/2}\,du
=\frac{1}{2}\operatorname{erfc}\left(\frac{x}{\sqrt{2}}\right)
$$

Ela mede a área da cauda direita de uma gaussiana padrão.

Probabilidades pequenas de erro correspondem a distâncias efetivas grandes em unidades de desvio-padrão.

## BER de BPSK, M-PSK e M-QAM

Para BPSK, a BER exata em AWGN é

$$
P_b=Q\left(\sqrt{2E_b/N_0}\right)
$$

Para $M$-PSK com Gray coding, uma aproximação usual é

$$
P_b\approx\frac{2}{b}Q\left(\sqrt{2b\,E_b/N_0}\,\sin\left(\frac{\pi}{M}\right)\right)
$$

Para QAM quadrada com Gray coding, usa-se

$$
P_b\approx\frac{4}{b}\left(1-\frac{1}{\sqrt{M}}\right)
Q\left(\sqrt{\frac{3b}{M-1}E_b/N_0}\right)
$$

Essas fórmulas capturam a dependência principal entre SNR e desempenho, e são as curvas teóricas comparadas com a simulação.

## Por que Gray coding ajuda na BER

Em um canal com ruído pequeno, o símbolo errado tende a ser um vizinho do símbolo correto. Se vizinhos diferem por apenas um bit, um erro de símbolo normalmente causa apenas um erro de bit.

É por isso que a BER pode ser bem menor que a SER multiplicada ingenuamente por $b$. O mapeamento Gray explora a geometria da constelação para reduzir a penalidade de erros próximos.

## Erro de símbolo versus erro de bit

A SER mede quantas decisões caíram na célula errada da constelação. A BER mede quantos bits efetivamente mudaram.

Em termos probabilísticos, a BER é uma projeção mais fina do desempenho do sistema. Duas modulações podem ter SER parecida, mas BER diferente, porque o custo em bits por erro depende do mapeamento.

## Resumo da decisão

Os últimos blocos do diagrama são:

1. decisão ML;
2. reconstrução dos bits;
3. contagem de erros;
4. cálculo da BER.

Nesta parte, o foco passa da forma de onda para a geometria probabilística da constelação.