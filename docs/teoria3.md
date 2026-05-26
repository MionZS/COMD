# Teoria 3 — Decisão ML, geometria da constelação e probabilidade de erro

## Como usar este arquivo na defesa

Esta parte responde à pergunta: **como o receptor decide qual símbolo foi transmitido e por que isso leva às curvas de BER?** Aqui o sistema deixa de ser visto como forma de onda no tempo e passa a ser visto como geometria no plano complexo.

Depois do filtro casado e da amostragem, cada símbolo recebido vira um ponto:

$$
r_k=Y_{I,k}+jY_{Q,k}.
$$

A decisão consiste em escolher o ponto ideal da constelação mais próximo de $r_k$.

## 1. Modelo de observação após amostragem

Com sincronismo ideal, filtro casado e AWGN, a amostra recebida pode ser escrita como:

$$
r_k=s_k+w_k,
$$

em que:

- $s_k$ é o símbolo transmitido;
- $w_k$ é o ruído equivalente após demodulação, filtro casado e amostragem;
- $r_k$ é a observação disponível para o decisor.

A constelação recebida é, portanto, uma nuvem de pontos ao redor de cada símbolo ideal. Essa é a interpretação dos gráficos RX e dos heatmaps do notebook.

## 2. Decisão de máxima verossimilhança

Se todos os símbolos são equiprováveis e o ruído é gaussiano com variância igual em todas as direções, a regra de máxima verossimilhança é equivalente à menor distância euclidiana:

$$
\hat{s}_k
=
\arg\min_{s_m\in\mathcal{C}}|r_k-s_m|^2.
$$

No código, isso aparece como:

```python
distances = np.abs(symbols.reshape(-1, 1) - const.reshape(1, -1)) ** 2
idx = np.argmin(distances, axis=1)
```

A razão estatística é que, em AWGN, a densidade condicional $p(r|s_m)$ decai exponencialmente com a distância quadrática entre $r$ e $s_m$:

$$
p(r|s_m)\propto
\exp\left(-\frac{|r-s_m|^2}{2\sigma^2}\right).
$$

Maximizar essa probabilidade é o mesmo que minimizar $|r-s_m|^2$.

## 3. Regiões de decisão

Cada símbolo possui uma região de decisão. Se a amostra recebida cai dentro dessa região, o símbolo é detectado corretamente. Se o ruído desloca a amostra para outra região, ocorre erro de símbolo.

Para PSK, as regiões são setores angulares. A principal vulnerabilidade é o ruído angular, pois todos os pontos têm o mesmo módulo. Conforme $M$ aumenta, o ângulo entre pontos vizinhos diminui:

$$
\Delta\theta=\frac{2\pi}{M}.
$$

Para QAM, as regiões são células retangulares ou semi-infinitas no plano $I/Q$. A vulnerabilidade principal está na distância mínima entre vizinhos horizontais e verticais. Para energia média fixa, aumentar $M$ aproxima os pontos, elevando a BER.

## 4. Distância mínima e robustez

A probabilidade de erro em AWGN está fortemente ligada à distância mínima da constelação:

$$
d_{\min}=\min_{i\neq j}|s_i-s_j|.
$$

Quanto maior $d_{\min}$ em relação ao desvio-padrão do ruído, menor a probabilidade de cruzar uma fronteira de decisão.

Isso explica os resultados esperados:

- BPSK e QPSK são mais robustas;
- 8-PSK e 16-PSK exigem maior $E_b/N_0$;
- 64-QAM é mais sensível que 16-QAM e 4-QAM;
- as curvas de maior $M$ aparecem deslocadas para a direita.

Na defesa, esta é a interpretação central dos gráficos BER: **aumentar a ordem da modulação aumenta eficiência espectral, mas reduz a distância relativa entre símbolos**.

## 5. Função Q

A função $Q$ mede a probabilidade de uma variável gaussiana padrão ultrapassar um limiar:

$$
Q(x)=\frac{1}{\sqrt{2\pi}}\int_x^\infty e^{-u^2/2}\,du.
$$

Ela também pode ser escrita como:

$$
Q(x)=\frac{1}{2}\operatorname{erfc}\left(\frac{x}{\sqrt{2}}\right).
$$

No código, essa forma é implementada com `scipy.special.erfc`:

```python
def qfunc(x):
    return 0.5 * erfc(x / np.sqrt(2))
```

A função $Q$ aparece porque o erro em uma fronteira de decisão é equivalente a perguntar: **qual a probabilidade de uma gaussiana ultrapassar uma distância crítica?**

## 6. BER de BPSK

Para BPSK coerente em AWGN, a BER é exata:

$$
P_b=Q\left(\sqrt{2\frac{E_b}{N_0}}\right).
$$

Como BPSK tem apenas dois pontos opostos, a decisão é uma comparação de sinal no eixo real. O erro ocorre quando o ruído desloca a amostra para o lado errado do limiar.

Essa expressão é uma referência importante na defesa porque serve como caso mais simples e mais confiável para validar a simulação.

## 7. BER de M-PSK

Para $M$-PSK com Gray coding, uma aproximação usual é:

$$
P_b\approx
\frac{2}{b}
Q\left(
\sqrt{2b\frac{E_b}{N_0}}
\sin\left(\frac{\pi}{M}\right)
\right).
$$

O termo

$$
\sin\left(\frac{\pi}{M}\right)
$$

representa a separação angular entre pontos vizinhos. Conforme $M$ cresce, esse seno diminui, a distância efetiva diminui e a BER aumenta.

Para BPSK, o código trata separadamente, usando a fórmula exata. Para $M>2$, a fórmula é uma aproximação de alto SNR baseada nos vizinhos mais próximos.

## 8. BER de M-QAM quadrada

Para $M$-QAM quadrada com Gray coding, uma aproximação usual é:

$$
P_b\approx
\frac{4}{b}
\left(1-\frac{1}{\sqrt{M}}\right)
Q\left(
\sqrt{\frac{3b}{M-1}\frac{E_b}{N_0}}
\right).
$$

O fator:

$$
1-\frac{1}{\sqrt{M}}
$$

corrige o fato de que pontos internos, de borda e de canto têm números diferentes de vizinhos. O termo:

$$
\frac{3b}{M-1}
$$

vem da relação entre energia média e distância mínima em uma QAM quadrada.

Para defesa, a explicação curta é:

> A fórmula de QAM estima a chance de o ruído cruzar as fronteiras horizontais ou verticais da grade. Ela é aproximada, mas muito boa em SNR moderado e alto com Gray coding.

## 9. SER versus BER

A SER mede a probabilidade de errar o símbolo:

$$
SER=\frac{N_{\text{símbolos errados}}}{N_{\text{símbolos}}}.
$$

A BER mede a fração de bits errados:

$$
BER=\frac{N_{\text{bits errados}}}{N_{\text{bits}}}.
$$

Um erro de símbolo pode causar 1, 2 ou mais bits errados, dependendo do mapeamento. O Gray coding reduz o custo típico de um erro de símbolo. Por isso, não basta olhar apenas para a SER: o trabalho pede explicitamente BER.

## 10. Por que a teoria e a simulação não batem perfeitamente

As curvas teóricas são calculadas com hipóteses ideais:

- AWGN perfeitamente branco;
- sincronismo perfeito;
- constelação ideal;
- Gray coding;
- aproximações por vizinhos mais próximos;
- quantidade infinita de amostras para estimar BER.

A simulação tem limitações:

- número finito de bits;
- discretização do pulso;
- truncamento do RRC;
- amostragem discreta;
- flutuação estatística do Monte Carlo;
- possível BER zerada quando há poucos erros.

Portanto, o esperado não é coincidência absoluta ponto a ponto, mas sim a mesma tendência: queda da BER com $E_b/N_0$ e pior desempenho para ordens maiores.

## 11. O que defender nesta seção

Pontos prováveis de pergunta:

1. **Por que ML vira menor distância?** Porque o ruído é gaussiano e símbolos são equiprováveis.
2. **Por que a função Q aparece?** Porque o erro é a cauda de uma gaussiana ultrapassando uma fronteira.
3. **Por que Gray coding melhora a BER?** Porque erros vizinhos causam menos bits errados.
4. **Por que 64-QAM piora?** Porque a distância mínima relativa entre pontos diminui.
5. **Por que teoria e simulação podem divergir?** Por aproximações teóricas, truncamento de pulso e Monte Carlo finito.

## Fontes usadas nesta parte

- Enunciado do TC2: exigência de curvas teóricas e BER simulada.
- Notebook Marimo v3: implementação do decisor por distância mínima, Gray coding e curvas teóricas.
- Código do colega: detector ML e funções de BER teórica.
- MathWorks, *Bit Error Rate Analysis Techniques*: validação por comparação com estatísticas teóricas.
- QAMpy: uso prático de `erfc`/função Q e funções teóricas em Python.
- Proakis e Salehi, *Digital Communications*: decisão ótima, AWGN, PSK/QAM e aproximações de erro.
- Lathi e Ding, *Modern Digital and Analog Communication Systems*: espaço de sinais e probabilidade de erro.
