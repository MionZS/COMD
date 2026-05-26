# Teoria 1 — Cadeia de transmissão em banda passante

## Como usar este arquivo na defesa

Esta parte serve para defender a arquitetura completa do simulador. A pergunta central que ela responde é: **como uma sequência de bits vira um sinal real em banda passante e depois entra no canal AWGN?** O ponto mais importante é mostrar que o notebook não é uma coleção de gráficos soltos; ele implementa, bloco a bloco, o diagrama da proposta do TC2: modulação digital, ramos em fase e quadratura, formatação por pulso, translação para banda passante, ruído, receptor coerente, filtro casado, amostragem e decisão.

A ideia operacional é:

$$
\text{bits}
\rightarrow
\text{agrupamento em } b=\log_2(M) \text{ bits}
\rightarrow
\text{mapeamento Gray}
\rightarrow
s_k=a_k+jb_k
\rightarrow
p(t)
\rightarrow
x(t)
\rightarrow
Y(t)
$$

No notebook Marimo v3, essa cadeia aparece em funções separadas: `bits_to_symbols`, `qam_constellation`, `psk_constellation`, `pulse_coeffs` e `simulate_link`. A vantagem didática dessa separação é que cada função corresponde a um bloco do sistema físico.

## 1. Do bit ao símbolo

A modulação digital não transmite necessariamente um bit por vez. Em um esquema $M$-ário, cada símbolo representa $b$ bits, com:

$$
M=2^b
$$

Logo:

$$
b=\log_2(M)
$$

No TC2, isso aparece diretamente nas duas famílias de modulação:

- para $M$-PSK: $b\in\{1,2,3,4\}$, portanto $M\in\{2,4,8,16\}$;
- para $M$-QAM: $b\in\{2,4,6\}$, portanto $M\in\{4,16,64\}$.

Na defesa, uma forma segura de explicar é: **o parâmetro $b$ não é o lado da constelação; é a quantidade de bits agrupados em cada símbolo**. Para 64-QAM, por exemplo, $b=6$, então há $2^6=64$ combinações binárias possíveis. Como a QAM usada é quadrada, esses 64 pontos são organizados como $8\times8$ no plano $I/Q$, pois:

$$
\sqrt{64}=8
$$

ou, de forma equivalente,

$$
2^{b/2}=2^{6/2}=2^3=8.
$$

Isso explica por que cada eixo da 64-QAM possui 8 níveis de amplitude, não 6 níveis e não 3 níveis. Cada eixo recebe 3 bits, e 3 bits selecionam uma entre $2^3=8$ amplitudes possíveis.

## 2. Agrupamento dos bits e ajuste do comprimento

Como cada símbolo carrega exatamente $b$ bits, a quantidade total de bits precisa ser múltipla de $b$. Caso contrário, sobrariam bits incapazes de formar um símbolo completo. O ajuste correto é:

$$
N_{\text{bits,ajustado}}
=
\left\lfloor
\frac{N_{\text{bits,desejado}}}{b}
\right\rfloor b.
$$

Depois disso:

$$
N_{\text{símbolos}}
=
\frac{N_{\text{bits,ajustado}}}{b}.
$$

No notebook Marimo v3, a escolha prática foi simular um número fixo de símbolos por configuração (`num_symbols_target`). Isso implica que o número de bits transmitidos cresce com $b$:

$$
N_{\text{bits}} = N_{\text{símbolos}}b.
$$

Para defesa, há duas formas aceitáveis de apresentar isso. Se o foco for comparabilidade estatística entre modulações, é melhor fixar número de bits. Se o foco for comparar constelações com quantidade semelhante de pontos amostrados em cada gráfico, é razoável fixar número de símbolos. Como a proposta pede “número de bits suficiente para convergência estatística”, a versão mais defensável é registrar, para cada curva, o número real de bits transmitidos e o número de erros observados.

## 3. Mapeamento Gray

Depois do agrupamento, cada bloco binário é convertido em um índice inteiro. Esse índice é então mapeado para uma posição da constelação. O notebook usa Gray coding:

$$
g = n \oplus (n \gg 1),
$$

onde $\oplus$ representa XOR e $\gg$ representa deslocamento binário para a direita.

A razão física do Gray coding é simples: em AWGN, os erros mais prováveis são erros para símbolos vizinhos, pois o ruído normalmente desloca a amostra recebida para perto do ponto transmitido. Se símbolos vizinhos diferem por apenas um bit, um erro de símbolo tende a gerar apenas um erro de bit. Isso reduz a BER em comparação com mapeamentos arbitrários.

Essa decisão também aproxima melhor a simulação das curvas teóricas usuais de BER para $M$-PSK e $M$-QAM, que normalmente assumem mapeamento Gray ou aproximações baseadas em vizinhos mais próximos.

## 4. Constelações PSK e QAM

O projeto usa duas famílias de constelações.

### 4.1 M-PSK

Na modulação $M$-PSK, todos os pontos têm o mesmo módulo e diferem apenas na fase. A constelação ideal pode ser escrita como:

$$
s_m=e^{j2\pi m/M},\qquad m=0,1,\dots,M-1.
$$

Geometricamente, todos os símbolos estão em uma circunferência. A energia de símbolo é constante, pois:

$$
|s_m|^2=1.
$$

Isso torna a PSK robusta a variações de amplitude, mas, conforme $M$ aumenta, os pontos ficam mais próximos angularmente. Portanto, 16-PSK é mais sensível a ruído de fase e ruído em quadratura do que QPSK.

### 4.2 M-QAM

Na QAM quadrada, os pontos formam uma grade no plano complexo. Para $M=L^2$, os níveis de cada eixo são:

$$
\{-(L-1),-(L-3),\dots,-1,+1,\dots,L-3,L-1\}.
$$

Exemplos:

- 4-QAM: níveis $\{-1,+1\}$ em $I$ e $Q$;
- 16-QAM: níveis $\{-3,-1,+1,+3\}$;
- 64-QAM: níveis $\{-7,-5,-3,-1,+1,+3,+5,+7\}$.

Cada ponto é:

$$
s_m=I_m+jQ_m.
$$

A QAM combina amplitude e fase. Ela é mais eficiente espectralmente porque coloca mais pontos no mesmo plano $I/Q$, mas, ao aumentar $M$, reduz a distância mínima entre pontos vizinhos para uma energia média fixa. Por isso, modulações QAM de ordem maior exigem maior $E_b/N_0$ para manter a mesma BER.

## 5. Energia média da constelação

A proposta define:

$$
E_b=\frac{E_x}{b},
$$

onde $E_x$ é a energia média da constelação. De forma geral:

$$
E_x=\mathbb{E}\{|s_k|^2\}.
$$

Na prática computacional existem duas formas equivalentes de tratar isso:

1. normalizar a constelação para $E_x=1$ e usar $E_b=1/b$;
2. não normalizar a constelação, calcular $E_x$ numericamente e usar $E_b=E_x/b$.

O Marimo v3 usa a segunda lógica para o ruído: calcula `ex = mean(abs(const)**2)` e usa esse valor na variância. Isso é consistente com a proposta, desde que o relatório diga explicitamente que $E_x$ foi calculado a partir da constelação usada na simulação. Para simplificar a defesa, porém, a versão com constelação normalizada é mais fácil de explicar.

## 6. Upsampling e fator `os`

A proposta define:

$$
f_s=os\,f_c,
$$

com:

$$
os=4,
\qquad
f_c=10\ \text{Hz}.
$$

Logo:

$$
f_s=40\ \text{Hz}.
$$

Como a proposta não introduz um parâmetro separado de amostras por símbolo, a implementação mais aderente ao enunciado usa o próprio `os` como fator discreto de upsampling. Assim, cada símbolo é representado por 4 amostras no trem discreto antes da filtragem.

No notebook Marimo v3, isso aparece diretamente em:

```python
upsampled = np.zeros(len(symbols_tx) * os, dtype=complex)
upsampled[::os] = symbols_tx
```

A interpretação defensável é: **o fator de oversampling fornecido pela proposta foi usado diretamente na implementação discreta da forma de onda**. Isso evita introduzir `Ns=16`, que é uma escolha extra e não aparece na proposta.

## 7. Formatação de pulso

Depois do upsampling, a sequência de impulsos discretos precisa ser moldada por um pulso $p(t)$. Em tempo contínuo, a forma de onda complexa em banda base pode ser escrita como:

$$
x_{bb}(t)=\sum_k s_kp(t-kT_s).
$$

Separando $I$ e $Q$:

$$
x_I(t)=\sum_k a_kp(t-kT_s),
$$

$$
x_Q(t)=\sum_k b_kp(t-kT_s).
$$

O TC2 pede dois pulsos:

- NRZ, que é retangular;
- raiz do cosseno levantado, RRC, com $\alpha=0{,}15$.

O pulso NRZ é simples e intuitivo, mas possui lóbulos espectrais relativamente largos. O RRC é mais sofisticado: ele é usado para que o filtro de transmissão e o filtro casado do receptor, quando combinados, formem uma resposta de cosseno levantado, que satisfaz o critério de Nyquist em instantes de amostragem. A literatura de filtros RRC destaca exatamente esse papel: dividir a filtragem entre transmissor e receptor, controlar banda ocupada e evitar ISI nos instantes corretos de decisão.

## 8. Banda base e banda passante

Após a formatação de pulso, o sinal ainda está em banda base complexa:

$$
x_{bb}(t)=x_I(t)+jx_Q(t).
$$

Para transmitir em banda passante, ele é convertido em um sinal real centrado na frequência da portadora. A forma usada no notebook e na proposta é:

$$
x(t)=\sqrt{2}\,x_I(t)\cos(2\pi f_ct)
-
\sqrt{2}\,x_Q(t)\sin(2\pi f_ct).
$$

O fator $\sqrt{2}$ aparece por normalização de potência das funções-base. As funções seno e cosseno são ortogonais ao longo de intervalos apropriados, permitindo transmitir duas componentes independentes no mesmo canal de frequência.

Na defesa, a frase curta é:

> A banda base guarda a informação em coordenadas complexas $I+jQ$; a banda passante transforma essas coordenadas em uma onda real usando portadoras ortogonais em seno e cosseno.

## 9. O que defender nesta seção

Pontos prováveis de pergunta:

1. **Por que $M=2^b$?** Porque $b$ bits geram $2^b$ combinações binárias, e cada combinação vira um símbolo.
2. **Por que 64-QAM tem lado 8?** Porque $64=8\times8$ e $8=2^{6/2}$.
3. **Por que Gray coding?** Porque erros em AWGN tendem a ocorrer entre vizinhos, e Gray reduz o número de bits errados nesses casos.
4. **O que é `os`?** É o fator de oversampling dado na proposta, usado para definir $f_s=osf_c$ e, na implementação mais aderente, também para discretizar os símbolos.
5. **Por que usar RRC?** Para controlar a banda e, junto com o filtro casado, obter uma resposta compatível com o critério de Nyquist.

## Fontes usadas nesta parte

- Enunciado do TC2: parâmetros obrigatórios, diagrama de blocos, modulações, pulsos e ruído.
- Notebook Marimo v3: implementação com `os=4`, Gray coding, constelações, pulsos e modulação passabanda.
- Código do colega: referência de organização por blocos e comentários sobre atraso de filtro.
- MathWorks, *Bit Error Rate Analysis App*: prática de comparar BER simulada com curvas teóricas.
- Proakis e Salehi, *Digital Communications*: base clássica para espaço de sinais, modulação $M$-ária, AWGN e decisão em distância mínima.
- Lathi e Ding, *Modern Digital and Analog Communication Systems*: base de comunicações digitais usada no curso.
- Referências sobre RRC e Nyquist: uso do RRC como filtro de transmissão/recepção para controle de ISI e banda.
