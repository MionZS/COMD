# Teoria 2 — Canal AWGN, demodulação coerente e filtro casado

## O canal AWGN

O canal usado no notebook é o canal AWGN: *Additive White Gaussian Noise*. Ele adiciona ruído gaussiano de média zero ao sinal transmitido, sem alterar sua estrutura determinística.

Em passband, o ruído é modelado como um processo aleatório real com densidade espectral constante. No nível discreto da simulação, isso aparece como amostras independentes de uma variável normal.

Seja $v[n]$ o ruído amostrado. Então:

$$
v[n]\sim\mathcal N(0,\sigma^2)
$$

A variância depende de $N_0$ e de $E_b/N_0$.

## Relação entre $E_b/N_0$ e variância

Como a constelação é normalizada para energia média unitária, temos $E_s=1$ e $E_b=1/b$. Logo:

$$
\gamma_b=\frac{E_b}{N_0}
\quad\Longrightarrow\quad
N_0=\frac{E_b}{\gamma_b}
$$

No modelo passband normalizado, a variância equivalente por componente real do ruído é proporcional a $N_0/2$. Isso leva à forma usada na simulação:

$$
\sigma=\sqrt{\frac{1}{2b\,E_b/N_0}}
$$

Essa expressão mostra um ponto importante de probabilidade: quanto maior o SNR por bit, menor a dispersão da nuvem de pontos recebidos.

## Demodulação coerente

Depois do canal, o receptor precisa voltar da portadora real para a representação em banda base. Isso é feito por demodulação coerente, multiplicando o sinal recebido pelas portadoras locais em fase e em quadratura.

A ideia é projetar o sinal sobre duas funções ortogonais:

$$
I(t)=\sqrt{2}\,r(t)\cos(2\pi f_c t),\qquad Q(t)=-\sqrt{2}\,r(t)\sin(2\pi f_c t)
$$

Depois da integração/filtragem apropriada, a informação complexa é reconstruída como

$$
z(t)=I(t)+jQ(t)
$$

Essa reconstrução depende de sincronismo ideal no notebook. Em um sistema real, erros de fase e frequência degradariam o desempenho.

## Filtro casado

O filtro casado é o bloco mais importante para recuperar sinais em ruído branco. Se o pulso transmitido é $p(t)$, o filtro casado ótimo é

$$
h_{mf}(t)=p(T_s-t)
$$

Ou seja, o pulso é revertido no tempo e deslocado para alinhar o pico de resposta no instante de amostragem.

A razão estatística é profunda: em AWGN, o filtro casado maximiza a relação sinal-ruído na saída no instante de decisão. Ele transforma o problema contínuo de detecção em uma estatística suficiente de menor dimensionalidade.

## Amostragem no instante correto

Depois do filtro casado, o receptor amostra a saída nos instantes associados aos símbolos transmitidos. Se o pulso tem comprimento finito, existe um atraso de grupo discreto que precisa ser compensado.

No notebook, isso aparece como um deslocamento equivalente a $\text{len}(p)-1$, seguido por amostras espaçadas de $sps$ em $sps$.

Esse detalhe é crucial: amostrar um símbolo no instante errado produz ISI artificial e piora a BER mesmo quando o ruído é baixo.

## A estatística após o filtro casado

Com sincronismo ideal, a saída amostrada pode ser modelada como

$$
\hat a_k=a_k+w_k
$$

onde $w_k$ é uma variável gaussiana complexa equivalente. Assim, a decisão passa a ser um problema de geometria probabilística: qual ponto da constelação está mais próximo da observação?

## Resumo do bloco do canal

Os blocos centrais do diagrama são:

1. canal AWGN;
2. demodulação coerente;
3. filtro casado $p(T_s-t)$;
4. amostragem no instante correto.

Nesta etapa, o ponto principal é estatístico: o ruído desloca os pontos em I/Q segundo uma lei gaussiana, e o filtro casado concentra a energia do símbolo no instante de decisão.