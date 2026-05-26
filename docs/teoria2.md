# Teoria 2 — Canal AWGN, demodulação coerente e filtro casado

## Como usar este arquivo na defesa

Esta parte responde à pergunta: **o que acontece com o sinal depois que ele sai do transmissor e como o receptor recupera a informação?** O núcleo é mostrar que o canal AWGN adiciona ruído gaussiano, que o receptor coerente traz o sinal de volta para banda base e que o filtro casado é o receptor linear ótimo em AWGN para maximizar a SNR no instante de decisão.

A sequência desta etapa é:

$$
x(t)
\rightarrow
Y(t)=x(t)+V(t)
\rightarrow
\text{demodulação coerente}
\rightarrow
p(T_s-t)
\rightarrow
\text{amostragem}
\rightarrow
Y_{I,k}+jY_{Q,k}.
$$

## 1. Canal AWGN

AWGN significa *Additive White Gaussian Noise*. A palavra **aditivo** indica que o ruído é somado ao sinal; **branco** indica densidade espectral de potência constante; **gaussiano** indica distribuição normal das amostras.

O modelo do canal é:

$$
Y(t)=x(t)+V(t).
$$

A proposta especifica que $V(t)$ deve ter média zero e variância:

$$
\sigma_V^2=\frac{N_0}{2}.
$$

No tempo discreto, a simulação representa esse ruído por amostras independentes:

$$
v[n]\sim\mathcal{N}(0,\sigma_V^2).
$$

A independência entre amostras é a aproximação discreta da ideia de ruído branco. O modelo AWGN é idealizado, mas fundamental: ele isola o efeito do ruído térmico e permite comparar modulações por uma métrica comum, $E_b/N_0$.

## 2. Relação entre $E_b/N_0$, $E_x$ e a variância do ruído

A proposta define:

$$
E_b=\frac{E_x}{b},
$$

em que $E_x$ é a energia média da constelação e $b=\log_2(M)$.

A razão sinal-ruído por bit é:

$$
\gamma_b=\frac{E_b}{N_0}.
$$

Se o valor é dado em dB:

$$
\gamma_b=10^{\frac{(E_b/N_0)_{dB}}{10}}.
$$

Assim:

$$
N_0=\frac{E_b}{\gamma_b}.
$$

E, usando a definição da proposta:

$$
\sigma_V^2=\frac{N_0}{2}
=
\frac{E_b}{2\gamma_b}
=
\frac{E_x}{2b\gamma_b}.
$$

Se a constelação for normalizada para $E_x=1$, então:

$$
\sigma_V^2=\frac{1}{2b\gamma_b}.
$$

Se a constelação não for normalizada, deve-se calcular $E_x$ numericamente. O Marimo v3 faz isso com a média de $|s|^2$ da constelação e usa esse valor na definição do ruído. O ponto de defesa é: **o ruído precisa ser calculado a partir da energia real da constelação usada na simulação**.

## 3. Interpretação física do $E_b/N_0$

O parâmetro $E_b/N_0$ mede quanta energia de bit está disponível em relação ao nível de ruído. Quanto maior $E_b/N_0$, menor a dispersão relativa causada pelo ruído.

Nos gráficos de constelação:

- baixo $E_b/N_0$: nuvens grandes, pontos se misturam e cruzam fronteiras de decisão;
- alto $E_b/N_0$: nuvens estreitas, pontos ficam próximos da constelação ideal;
- modulações com maior $M$: pontos mais próximos, exigindo maior $E_b/N_0$ para a mesma BER.

Essa leitura visual é uma das melhores formas de defender os resultados: a curva BER e a constelação RX estão mostrando o mesmo fenômeno em representações diferentes.

## 4. Demodulação coerente

Depois do canal, o sinal recebido ainda é real e está em banda passante. Para recuperar as componentes $I$ e $Q$, o receptor multiplica o sinal pelas mesmas portadoras usadas no transmissor:

$$
Y_I(t)=\sqrt{2}\,Y(t)\cos(2\pi f_ct),
$$

$$
Y_Q(t)=-\sqrt{2}\,Y(t)\sin(2\pi f_ct).
$$

A demodulação é chamada coerente porque assume que o receptor conhece a frequência e a fase da portadora. Isso é uma hipótese ideal. Em sistemas reais, haveria recuperação de portadora, erro de fase, desvio de frequência e sincronização de símbolo. O TC2 abstrai esses efeitos para focar em BER sob AWGN.

A ortogonalidade entre seno e cosseno permite separar os ramos. Idealmente, após multiplicação e filtragem, os termos cruzados desaparecem ou são rejeitados pela integração/filtro casado, recuperando as componentes $x_I(t)$ e $x_Q(t)$.

## 5. Por que aparece um termo de frequência dupla

Ao multiplicar o sinal recebido pela portadora local, aparecem produtos trigonométricos como:

$$
\cos^2(2\pi f_ct)=\frac{1+\cos(4\pi f_ct)}{2},
$$

$$
\sin(2\pi f_ct)\cos(2\pi f_ct)=\frac{\sin(4\pi f_ct)}{2}.
$$

Ou seja, o produto contém uma parcela de baixa frequência, que carrega a informação, e uma parcela em torno de $2f_c$. Na implementação, o filtro casado e a amostragem no instante adequado fazem a recuperação discreta da componente útil. Em uma modelagem analógica completa, haveria também filtragem passa-baixas explícita após a multiplicação.

## 6. Filtro casado

O filtro casado é o bloco central do receptor ótimo em AWGN. Se o pulso transmitido é $p(t)$, o filtro casado é:

$$
h(t)=p(T_s-t).
$$

Em tempo discreto, para pulsos reais, isso é implementado como reversão temporal:

```python
mf = pulse[::-1]
```

Para a forma geral complexa:

```python
mf = pulse[::-1].conj()
```

A função do filtro casado não é simplesmente “alisar” o ruído. Ele maximiza a relação sinal-ruído na amostra de decisão. De forma intuitiva, ele correlaciona o sinal recebido com o formato de pulso esperado. Se o pulso correto está presente, a saída tem pico no instante de alinhamento; se há apenas ruído, a contribuição tende a ser menor e aleatória.

## 7. Atraso do filtro e amostragem

A convolução do pulso de transmissão com o filtro casado introduz atraso. Se o pulso discreto tem comprimento $L$, a combinação transmissor + receptor produz um atraso total de:

$$
L-1.
$$

Por isso, o notebook amostra em:

$$
n_k=(L-1)+k\,os.
$$

No código:

```python
offset = len(pulse) - 1
sample_idx = offset + np.arange(len(symbols_tx)) * os
symbols_rx = filtered[sample_idx]
```

Esse detalhe é crítico. Se a amostragem for deslocada, o receptor coleta o símbolo em um ponto em que a contribuição dos vizinhos pode estar presente, criando ISI artificial e piorando a BER. Na defesa, esse é um dos pontos mais importantes para mostrar que o diagrama foi implementado corretamente.

## 8. NRZ versus RRC no filtro casado

Com NRZ, o pulso é retangular e curto. O filtro casado vira outro retângulo invertido. A resposta combinada é triangular, com pico no instante de decisão.

Com RRC, o transmissor usa a raiz do cosseno levantado. O receptor usa o mesmo pulso invertido. A convolução dos dois RRCs forma uma resposta equivalente de cosseno levantado. O objetivo é satisfazer o critério de Nyquist nos instantes de amostragem, reduzindo a interferência intersimbólica.

A defesa curta é:

> O RRC sozinho não é o pulso de Nyquist completo; o par transmissor RRC + receptor RRC forma o cosseno levantado, que tem zeros nos instantes dos símbolos vizinhos.

## 9. Estatística após o filtro casado

Com sincronismo ideal e ruído AWGN, a saída amostrada pode ser modelada como:

$$
r_k=s_k+w_k,
$$

onde $w_k$ é ruído gaussiano equivalente no plano complexo. Por isso, a constelação recebida aparece como nuvens gaussianas ao redor dos pontos ideais. Esse modelo também justifica a decisão por menor distância euclidiana: em ruído gaussiano isotrópico, o ponto mais próximo é o símbolo de maior verossimilhança.

## 10. O que defender nesta seção

Pontos prováveis de pergunta:

1. **Por que $\sigma_V^2=N_0/2$?** Porque o enunciado especifica essa variância para o ruído AWGN real em banda passante.
2. **Como você calcula $N_0$?** A partir de $E_b/N_0$: $N_0=E_b/\gamma_b$.
3. **Por que o filtro casado é $p(T_s-t)$?** Porque ele maximiza a SNR no instante de decisão em AWGN.
4. **Por que amostrar em `len(pulse)-1 + k os`?** Porque esse é o atraso total da combinação filtro de transmissão + filtro casado.
5. **O que o RRC faz?** Controla a banda e, junto com outro RRC no receptor, forma uma resposta de Nyquist.

## Fontes usadas nesta parte

- Enunciado do TC2: modelo AWGN, variância $N_0/2$, filtro casado $p(T_s-t)$ e amostragem em $t=kT_s$.
- Notebook Marimo v3: implementação da modulação passabanda, ruído, demodulação coerente, filtro casado e amostragem.
- Código do colega: comentários detalhados sobre atraso total e índices de amostragem.
- MathWorks, *Bit Error Rate Analysis App*: estrutura BER versus $E_b/N_0$ e comparação simulação/teoria.
- Proakis e Salehi, *Digital Communications*: base teórica de AWGN, filtro casado e decisão ótima.
- Lathi e Ding, *Modern Digital and Analog Communication Systems*: base de modulação passabanda e receptores em comunicação digital.
- Referências sobre RRC/Nyquist: papel do RRC como metade da resposta de cosseno levantado.
