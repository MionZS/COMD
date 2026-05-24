# Teoria 1 — Cadeia de transmissão em banda passante

## Visão geral

O notebook implementa uma cadeia de comunicação digital completa, da geração dos bits até a estimação da BER. A ideia central é simples: um conjunto de bits é agrupado, mapeado em símbolos complexos, convertido em uma forma de onda em banda passante, corrompido por ruído AWGN, recuperado por demodulação coerente e finalmente decidido por máxima verossimilhança.

A cadeia usada no projeto é:

$$
\text{bits} \rightarrow \text{agrupamento} \rightarrow \text{Gray mapping} \rightarrow \text{constelação}
\rightarrow \text{upsampling} \rightarrow p(t) \rightarrow \text{portadora}
\rightarrow \text{canal AWGN} \rightarrow \text{demodulação coerente}
\rightarrow p(T_s-t) \rightarrow \text{amostragem} \rightarrow \text{decisão ML} \rightarrow \widehat{BER}
$$

Cada bloco resolve uma parte específica do problema. O notebook não apenas simula o sistema, mas também mostra visualmente o efeito de cada etapa sobre a nuvem de símbolos e sobre a curva BER.

## 1. Bits para símbolos

Seja $M$ a ordem da modulação. Cada símbolo carrega $b=\log_2(M)$ bits. Assim, os bits precisam ser agrupados em blocos de tamanho $b$ antes do mapeamento.

Esse agrupamento não é detalhe de implementação: ele define o alfabeto efetivo da modulação. Se $M=16$, então $b=4$ e cada símbolo representa exatamente 4 bits.

A conversão do bloco binário para índice inteiro segue a interpretação posicional usual. Depois disso, o índice é convertido para Gray code. Essa etapa reduz o impacto de erros vizinhos: quando o ruído desloca um ponto para uma vizinhança adjacente da constelação, a quantidade de bits errados tende a ser menor.

## 2. Gray mapping

No Gray mapping, símbolos adjacentes diferem por apenas um bit. Isso é especialmente útil em AWGN, porque os erros mais prováveis são os de vizinhança mais próxima.

Se $\hat a$ é o símbolo detectado e $a$ o símbolo transmitido, um erro de símbolo não precisa virar muitos erros de bit. Por isso, a BER em Gray coding costuma ser bem menor do que seria com um mapeamento arbitrário.

Essa é uma das razões pelas quais as fórmulas teóricas usadas no notebook assumem Gray mapping.

## 3. Constelações PSK e QAM

O projeto usa duas famílias de constelações:

- **M-PSK**: os pontos ficam sobre um círculo, com fase distinta para cada símbolo.
- **M-QAM quadrada**: os pontos formam uma grade em I/Q.

Em ambos os casos, a constelação é normalizada para energia média unitária. Isso é essencial porque as expressões de BER em função de $E_b/N_0$ assumem uma convenção energética consistente.

A normalização remove ambiguidade: a comparação entre modulações passa a refletir geometria e robustez ao ruído, e não apenas escalas artificiais.

## 4. Upsampling e formatação de pulso

Após o mapeamento, o sinal discreto precisa ganhar estrutura temporal. Para isso, cada símbolo é inserido em uma sequência amostrada com $sps$ amostras por símbolo.

Matematicamente, a sequência baseband pode ser escrita como

$$
s(t)=\sum_k a_k\,p(t-kT_s)
$$

onde $a_k$ são os símbolos complexos e $p(t)$ é o pulso de transmissão.

No notebook aparecem dois pulsos:

- **NRZ**: pulso retangular simples;
- **Pulso com roll-off**: forma espectral mais controlada, usada para reduzir espalhamento e aproximar um formato de Nyquist.

A função do pulso é moldar o espectro e controlar a interferência entre símbolos. Um pulso mais estreito no tempo ocupa mais banda; um pulso mais suave no tempo ocupa menos banda.

## 5. Portadora em banda passante

O sinal complexo em banda base é convertido para um sinal real em banda passante por modulação com portadora:

$$
x(t)=\sqrt{2}\,\big(\Re\{s(t)\}\cos(2\pi f_c t)-\Im\{s(t)\}\sin(2\pi f_c t)\big)
$$

Essa etapa leva o sinal para a faixa de transmissão física. Em vez de enviar I/Q diretamente, o sistema real transmite uma forma de onda real centrada em $f_c$.

No notebook, a taxa de amostragem discreta da portadora é definida separadamente de $sps$, justamente para não confundir amostragem por símbolo com amostragem da onda senoidal.

## 6. Por que a normalização importa

Toda a comparação de desempenho fica mais limpa quando a energia média dos símbolos é 1. Nesse caso:

$$
E_s=1,\qquad E_b=\frac{E_s}{b}=\frac{1}{b}
$$

Isso conecta diretamente a simulação ao parâmetro $E_b/N_0$.

Sem essa convenção, a BER simulada poderia mudar apenas porque o sinal foi escalado, e não porque a modulação é mais ou menos robusta.

## Resumo do bloco inicial

Nesta primeira parte da série, o foco está nos blocos de entrada do diagrama:

1. geração de bits;
2. agrupamento em blocos de $b$ bits;
3. Gray mapping;
4. construção da constelação;
5. upsampling;
6. formatação do pulso;
7. modulação em banda passante.

A próxima parte trata do canal, do ruído e da recuperação coerente do sinal.