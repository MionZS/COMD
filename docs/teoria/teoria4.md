# Teoria 4 — BER de Monte Carlo, confiança estatística e leitura dos gráficos

## Como usar este arquivo na defesa

Esta parte responde à pergunta: **como saber se os resultados simulados são confiáveis?** Aqui o foco é estatístico. A BER simulada não é uma verdade exata: ela é uma estimativa obtida por repetição de experimentos aleatórios.

A defesa deve deixar claro que:

1. a BER é calculada por contagem de erros;
2. a confiabilidade depende da quantidade de bits e erros observados;
3. BER igual a zero não significa ausência real de erro;
4. as curvas devem ser lidas junto com constelações e número de erros.

## 1. BER como estimador de Monte Carlo

A BER simulada é:

$$
\widehat{BER}=\frac{N_{\text{erros}}}{N_{\text{bits}}}.
$$

Esse valor é um estimador estatístico. Se a simulação for repetida com outra semente de bits ou de ruído, a BER estimada pode mudar. A variação será pequena se houver muitos bits e muitos erros observados; será grande se houver poucos erros.

O modelo estatístico é binomial. Cada bit detectado pode ser interpretado como um ensaio com probabilidade de erro $P_b$. Para $N$ bits:

$$
N_{\text{erros}}\sim\text{Binomial}(N,P_b).
$$

Logo:

$$
\mathbb{E}[\widehat{BER}]=P_b,
$$

mas a variância aproximada é:

$$
\operatorname{Var}(\widehat{BER})
=\frac{P_b(1-P_b)}{N}.
$$

Quando $P_b$ é pequeno, a variância relativa pode ser grande se $N$ não for suficientemente alto.

## 2. Por que altos valores de $E_b/N_0$ são difíceis

Em alto $E_b/N_0$, a BER verdadeira pode ser muito pequena. Por exemplo, se:

$$
P_b=10^{-5},
$$

então a cada 100 mil bits esperamos, em média, apenas 1 erro. Uma simulação com 20 mil bits pode observar zero erros por acaso.

Por isso, quando a curva simulada chega abruptamente em zero, isso não significa que o sistema ficou perfeito. Significa que, naquele tamanho de amostra, nenhum erro foi observado.

Essa é exatamente a razão pela qual a proposta pede número de bits suficiente para observar convergência estatística, especialmente em altos valores de $E_b/N_0$.

## 3. Critério de parada por erros mínimos

A prática recomendada em simulações BER é não usar apenas número fixo de símbolos. O ideal é usar um critério duplo:

$$
N_{\text{erros}}\geq N_{\text{erros,min}}
$$

ou

$$
N_{\text{bits}}\geq N_{\text{bits,max}}.
$$

A documentação da MathWorks recomenda simular dados suficientes para produzir pelo menos cerca de 100 erros para obter resultados de taxa de erro mais precisos. Portanto, um critério prático é:

$$
N_{\text{erros,min}}=100.
$$

No código, isso ficaria assim:

```python
MIN_ERRORS = 100
MAX_BITS = 2_000_000

total_errors = 0
total_bits = 0

while total_errors < MIN_ERRORS and total_bits < MAX_BITS:
    # gerar bits
    # transmitir pelo sistema
    # detectar bits
    # acumular erros e bits
    pass

ber = total_errors / total_bits
```

O Marimo v3 atual usa número fixo de símbolos. Para defesa, é importante reconhecer isso como uma simplificação computacional. A versão metodologicamente mais forte é a adaptativa por erros mínimos.

## 4. Zero erros e a rule of three

Se nenhum erro é observado em $N$ bits, não se deve reportar simplesmente “BER = 0” como se fosse valor físico. Uma interpretação estatística comum é a *rule of three*: com zero eventos observados, um limite superior aproximado de 95% para a probabilidade do evento é:

$$
P_b \lesssim \frac{3}{N}.
$$

Exemplo: se foram transmitidos $N=10^6$ bits e nenhum erro foi observado, pode-se dizer que a BER está, aproximadamente, abaixo de:

$$
3\times10^{-6}
$$

com cerca de 95% de confiança. Isso é muito diferente de dizer que a BER é exatamente zero.

## 5. O que registrar junto com a BER

Para tornar o trabalho auditável, cada ponto da curva deve idealmente guardar:

- modulação;
- ordem $M$;
- pulso;
- $E_b/N_0$;
- número de bits transmitidos;
- número de erros observados;
- BER simulada;
- BER teórica;
- motivo de parada: erros mínimos ou teto de bits.

Um CSV final poderia ter colunas:

```text
modulation,M,b,pulse,EbN0_dB,bits,errors,BER_sim,BER_theory,stop_reason
```

Isso responde diretamente a possíveis críticas sobre convergência estatística.

## 6. Leitura das curvas BER

Os gráficos BER devem ser lidos em escala logarítmica no eixo vertical. O padrão esperado é:

- BER diminui quando $E_b/N_0$ aumenta;
- modulações de ordem maior têm BER maior para o mesmo $E_b/N_0$;
- PSK de ordem alta degrada rapidamente porque os pontos ficam angularmente próximos;
- QAM de ordem alta exige mais SNR porque a distância mínima da grade diminui;
- curvas simuladas devem acompanhar a tendência teórica, ainda que não coincidam perfeitamente.

No gráfico, a curva teórica serve como referência. A curva simulada é validação computacional. Se houver afastamento grande, os suspeitos principais são: escala do ruído, normalização de energia, instante de amostragem, mapeamento Gray ou número insuficiente de bits.

## 7. Leitura das constelações TX/RX

A constelação TX mostra os símbolos ideais transmitidos. Ela serve para verificar se o mapeamento está correto.

A constelação RX mostra as amostras após canal, demodulação, filtro casado e amostragem. Ela serve para verificar se a cadeia do receptor está funcionando.

Interpretação:

- em baixo $E_b/N_0$, as nuvens RX são largas e sobrepostas;
- em alto $E_b/N_0$, as nuvens ficam concentradas nos pontos ideais;
- se as nuvens estiverem deslocadas, pode haver erro de ganho, fase ou normalização;
- se as nuvens estiverem deformadas ou com cauda estranha, pode haver erro de amostragem ou filtro.

O heatmap RX ajuda a visualizar densidade quando há muitos pontos sobrepostos.

## 8. Efeito dos pulsos nos resultados

O pulso NRZ é simples, mas tem espectro mais largo e resposta combinada menos refinada. O RRC foi incluído justamente para controlar banda e reduzir ISI nos instantes de amostragem quando combinado com o filtro casado.

Em uma simulação ideal AWGN sem limitação de banda severa, a diferença de BER entre NRZ e RRC pode não ser tão dramática quanto a diferença visual/spectral. O papel do RRC aparece melhor quando se discute espectro, ISI e robustez a canais bandlimited.

Na defesa, é importante não prometer que RRC sempre terá BER muito menor em todos os cenários. A afirmação correta é:

> O RRC melhora a conformidade ao critério de Nyquist e controla a banda ocupada; a BER depende também de normalização, sincronismo, ruído e truncamento do filtro.

## 9. Por que alguns pontos simulados ficam abaixo da teoria

Em tese, a curva simulada deve oscilar ao redor da teoria ou ficar próxima dela. Mas, com Monte Carlo finito, pode aparecer ponto abaixo da teoria. Isso não significa que o sistema superou o limite teórico; significa flutuação estatística ou erro de escala.

Também pode ocorrer que a BER simulada tenha piso artificial se o código aplicar `max(ber, 1e-7)` para evitar zero em escala log. Essa prática facilita visualização, mas precisa ser mencionada ou evitada no relatório final. O valor correto deve ser armazenado separadamente.

## 10. Recomendações para a versão final do artigo

Para o artigo, a seção de resultados deve apresentar:

1. descrição do que cada figura mostra antes da figura;
2. captions detalhadas, mas sem análise extensa;
3. curvas BER separadas por família: QAM e PSK;
4. pulsos NRZ e RRC comparados de forma legível;
5. constelações TX e RX em $E_b/N_0$ representativo;
6. tabela com parâmetros de simulação;
7. menção explícita ao número de bits/símbolos e critério estatístico.

Isso responde às críticas recebidas no TC1: parâmetros devem estar em resultados/metodologia, figuras precisam ser descritas, captions precisam ser detalhadas e fontes/citações devem acompanhar afirmações teóricas.

## 11. O que defender nesta seção

Pontos prováveis de pergunta:

1. **Quantos bits são suficientes?** Não existe número universal; usa-se número suficiente para observar erros, tipicamente pelo menos 100 por ponto ou um teto de bits.
2. **BER zero é possível?** Na simulação, sim como observação; fisicamente, deve ser interpretada como limite inferior/ausência de erros observados, não como probabilidade nula.
3. **Por que usar escala log?** Porque BER varia em várias ordens de grandeza.
4. **Por que comparar com teoria?** Para validar escala do ruído, mapeamento e comportamento esperado.
5. **O que comprova que o receptor funciona?** Constelações RX concentradas nos pontos ideais e BER decrescente com $E_b/N_0$.

## Fontes usadas nesta parte

- Enunciado do TC2: exigência de convergência estatística e curvas BER teóricas/simuladas.
- Notebook Marimo v3: geração de curvas BER, constelações RX e heatmaps.
- Notebook Marimo v2/slides: ideia de `MIN_ERRORS` e `MAX_BITS` para parada estatística.
- MathWorks, *Bit Error Rate Analysis Techniques*: recomendação de observar cerca de 100 erros para estimativas de taxa de erro mais precisas.
- MathWorks, `berconfint`: BER como estimativa estatística com intervalo de confiança.
- SiTime, BER Confidence Calculator: interpretação de zero erros e regra prática $3/N$.
- Proakis e Salehi, *Digital Communications*: base clássica de desempenho BER em AWGN.
