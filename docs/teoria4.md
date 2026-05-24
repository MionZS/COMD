# Teoria 4 — BER de Monte Carlo, confiança estatística e leitura dos gráficos

## A BER como estimador estatístico

No notebook, a BER não é obtida por uma fórmula exata do sistema completo, mas por Monte Carlo. O estimador é

$$
\widehat{BER}=\frac{N_{\text{erros}}}{N_{\text{bits}}}
$$

Esse valor é uma variável aleatória, não uma constante. Se a simulação fosse repetida com outra semente de ruído, a estimativa mudaria levemente.

Por isso, a leitura correta da BER precisa sempre considerar variabilidade amostral.

## Por que simular muitos bits

Quando a BER é baixa, erros ficam raros. Se forem simulados poucos bits, é comum obter zero erros por acaso, mesmo quando a BER verdadeira é apenas pequena e não nula.

A incerteza estatística aproximada de um estimador binomial é

$$
\operatorname{Var}(\widehat{BER})\approx\frac{P_b(1-P_b)}{N_{\text{bits}}}
$$

Logo, reduzir a incerteza exige aumentar o número de bits simulados.

## Critério de parada

O notebook usa duas condições práticas para cada ponto de $E_b/N_0$:

- parar quando atingir um número mínimo de erros;
- ou parar quando atingir um teto máximo de bits.

Esse é o compromisso clássico entre custo computacional e qualidade estatística.

Se o SNR é alto, a simulação precisa de mais bits para observar erros suficientes. Se o SNR é baixo, poucos bits já bastam para estabilizar a estimativa.

## Zero erros não significa BER zero

Se nenhum erro aparece em $N$ bits, isso não prova que a BER verdadeira seja zero. Apenas indica que o evento erro não foi observado naquela amostra.

Uma regra prática útil é a chamada *rule of three*: se zero eventos são observados, um limite superior aproximado de 95% para a probabilidade do evento é da ordem de $3/N$.

Ou seja: mesmo sem erros observados, a verdadeira BER pode ser apenas menor do que a capacidade amostral do experimento.

## Interpretação dos gráficos

O notebook salva quatro tipos principais de saída visual:

1. **Curva BER**: compara simulação e teoria em função de $E_b/N_0$;
2. **Constelação TX**: mostra os símbolos ideais transmitidos;
3. **Constelação RX**: mostra a dispersão após canal e decisão parcial;
4. **Heatmap RX**: mostra a densidade de amostras recebidas no plano I/Q.

Cada figura confirma um estágio diferente do diagrama em blocos.

## Efeito dos pulsos

O pulso NRZ tende a gerar uma ocupação espectral mais ampla. Já o pulso com roll-off controla melhor a banda ocupada e deixa a transição mais suave.

Na prática, isso afeta a forma temporal do símbolo, o comportamento do filtro casado e o nível de interferência entre símbolos. A teoria por trás disso é sempre a mesma: tempo mais curto implica espectro mais largo.

## Leitura final do diagrama em blocos

O sistema pode ser entendido como uma sequência de transformações probabilísticas:

1. bits determinísticos entram no transmissor;
2. o mapeamento converte bits em pontos de constelação;
3. o pulso transforma símbolos em forma de onda;
4. a portadora leva o sinal à banda passante;
5. o canal AWGN adiciona ruído gaussiano;
6. o receptor coerente volta para banda base;
7. o filtro casado maximiza a SNR amostrada;
8. a decisão ML escolhe o ponto mais próximo;
9. a BER conta quantos bits sobreviveram;
10. o Monte Carlo repete tudo até a estimativa estabilizar.

## Fechamento

A série completa mostra que o notebook não é apenas uma simulação numérica. Ele implementa, passo a passo, a teoria clássica de comunicação digital em AWGN: codificação Gray, constelações normalizadas, pulse shaping, demodulação coerente, filtro casado, decisão ML e estimação estatística da BER.