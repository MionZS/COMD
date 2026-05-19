# PRD - Trabalho Computacional 2

**Disciplina:** TE903/EELT7026 - Comunicação Digital  
**Tema:** Simulação de BER para M-QAM e M-PSK em banda passante com canal AWGN  
**Entrega:** Relatório em formato de artigo IEEE e código Python utilizado para gerar os resultados  
**Prazo:** 21 de maio de 2026  
**Autor:** Gabriel Montebeleri

---

## 1. Contexto

O Trabalho Computacional 2 solicita a simulação da taxa de erro de bit, BER, para sistemas de comunicação digital em banda passante. O sistema deve avaliar modulações M-QAM e M-PSK, considerando ruído aditivo branco gaussiano, AWGN, e comparar os resultados simulados com curvas teóricas de probabilidade de erro.

O sistema segue uma cadeia clássica de comunicação digital: geração de bits, modulação digital, decomposição em componentes em fase e quadratura, formatação de pulso, translação para banda passante, adição de ruído, demodulação coerente, filtragem casada, amostragem, decisão e cálculo da BER.

---

## 2. Objetivo do Produto

Desenvolver uma simulação computacional reprodutível em Python capaz de gerar as figuras e os dados necessários para um relatório IEEE sobre desempenho BER de modulações digitais em canal AWGN.

O produto deve permitir comparar:

- M-QAM com b = 2, 4 e 6 bits por símbolo, isto é, M = 4, 16 e 64.
- M-PSK com b = 1, 2, 3 e 4 bits por símbolo, isto é, M = 2, 4, 8 e 16.
- Pulsos de transmissão NRZ e raiz do cosseno levantado, RRC, com roll-off alpha = 0,15.
- Valores de Eb/N0 iguais a 0, 4, 8, 12, 16, 20 e 24 dB.

---

## 3. Entregáveis

### 3.1 Entregáveis obrigatórios

1. Código Python usado para gerar os resultados.
2. Relatório escrito em formato de artigo IEEE.
3. Figuras das constelações dos símbolos gerados no transmissor.
4. Figuras das constelações dos símbolos coletados no receptor após amostragem.
5. Gráficos comparativos de BER simulada para as diferentes ordens de QAM e PSK.
6. Curvas teóricas de BER nos mesmos gráficos da BER simulada.

### 3.2 Entregáveis de apoio recomendados

1. Arquivo CSV com os valores simulados de BER.
2. Pasta de figuras com nomes rastreáveis.
3. Arquivo README.md com instruções de execução.
4. Ambiente Python documentado em requirements.txt ou pyproject.toml.

---

## 4. Parâmetros do Sistema

| Parâmetro | Valor | Observação |
|---|---:|---|
| fc | 10 Hz | Frequência da portadora |
| os | 4 | Fator de oversampling |
| fs | 40 Hz | fs = os * fc |
| Eb/N0 | 0, 4, 8, 12, 16, 20, 24 dB | Vetor de simulação |
| Pulsos | NRZ e RRC | RRC com alpha = 0,15 |
| M-QAM | 4, 16, 64 | b = 2, 4, 6 |
| M-PSK | 2, 4, 8, 16 | b = 1, 2, 3, 4 |

### 4.1 Hipótese operacional para Ts

O enunciado define fc, fs e os, mas não fixa explicitamente a taxa de símbolos. Para tornar a simulação discreta rastreável, recomenda-se declarar a hipótese:

```text
Ts = 1 / fc
```

Assim:

```text
SPS = fs * Ts = 4
```

Logo, cada símbolo ocupa quatro amostras.

---

## 5. Requisitos Funcionais

### RF01 - Geração de bits

O sistema deve gerar uma sequência aleatória de bits equiprováveis, com valores 0 e 1.

**Critério de aceite:** o vetor de bits deve ter tamanho múltiplo de b para cada modulação testada.

### RF02 - Agrupamento de bits

O sistema deve agrupar os bits em blocos de tamanho b.

**Critério de aceite:** cada bloco deve mapear exatamente um símbolo da constelação.

### RF03 - Mapeamento M-PSK

O sistema deve mapear blocos de b bits em símbolos M-PSK com M = 2^b.

**Critério de aceite:** a constelação deve possuir M pontos distribuídos sobre o círculo unitário.

### RF04 - Mapeamento M-QAM

O sistema deve mapear blocos de b bits em símbolos M-QAM quadrada para M = 4, 16 e 64.

**Critério de aceite:** a constelação deve formar uma grade quadrada normalizada.

### RF05 - Normalização de energia

O sistema deve normalizar a constelação para energia média Ex = 1.

**Critério de aceite:** a média de |s_k|^2 deve ser aproximadamente 1.

### RF06 - Cálculo de Eb

O sistema deve calcular a energia por bit como:

```text
Eb = Ex / b
```

Com Ex = 1, tem-se Eb = 1/b.

### RF07 - Formatação de pulso

O sistema deve implementar dois pulsos de transmissão:

1. NRZ.
2. RRC com alpha = 0,15.

**Critério de aceite:** ambos os pulsos devem ser normalizados em energia discreta.

### RF08 - Modulação em banda passante

O sistema deve gerar o sinal transmitido em banda passante pela expressão:

```text
x(t) = sqrt(2) xI(t) cos(2*pi*fc*t) - sqrt(2) xQ(t) sin(2*pi*fc*t)
```

**Critério de aceite:** os ramos I e Q devem ser modulados por portadoras ortogonais.

### RF09 - Canal AWGN

O sistema deve adicionar ruído gaussiano branco de média zero e variância:

```text
sigma_V^2 = N0 / 2
```

com:

```text
N0 = Eb / (Eb/N0)
```

**Critério de aceite:** a variância do ruído deve ser atualizada para cada valor de Eb/N0.

### RF10 - Demodulação coerente

O receptor deve multiplicar o sinal recebido pelas portadoras locais para recuperar os ramos I e Q.

**Critério de aceite:** a demodulação deve usar as mesmas frequências e fases do transmissor.

### RF11 - Filtro casado

O receptor deve aplicar filtro casado:

```text
h(t) = p(Ts - t)
```

No domínio discreto, isso equivale a inverter o pulso no tempo e aplicar conjugação complexa, quando necessário.

**Critério de aceite:** o atraso da filtragem deve ser compensado antes da amostragem.

### RF12 - Amostragem

O receptor deve amostrar o sinal filtrado nos instantes:

```text
t = k Ts
```

**Critério de aceite:** as amostras complexas coletadas devem ser usadas para gerar as constelações recebidas.

### RF13 - Decisão

O sistema deve decidir o símbolo recebido pela menor distância euclidiana até os pontos da constelação ideal.

**Critério de aceite:** cada amostra recebida deve ser associada a exatamente um símbolo válido.

### RF14 - Cálculo de BER

O sistema deve comparar os bits transmitidos e os bits recebidos e calcular:

```text
BER = numero de bits errados / numero de bits transmitidos
```

**Critério de aceite:** a BER deve ser calculada para todas as modulações, pulsos e valores de Eb/N0.

### RF15 - Curvas teóricas

O sistema deve calcular e plotar curvas teóricas de BER junto com as curvas simuladas.

**Critério de aceite:** cada gráfico de BER deve conter pelo menos uma curva simulada e a curva teórica correspondente.

---

## 6. Requisitos Não Funcionais

### RNF01 - Reprodutibilidade

A simulação deve permitir fixar uma seed aleatória.

### RNF02 - Modularidade

O código deve separar transmissor, canal, receptor, decisor, métricas e plotagem.

### RNF03 - Rastreabilidade

As figuras devem ter nomes rastreáveis contendo modulação, ordem M, pulso e valor de Eb/N0 quando aplicável.

### RNF04 - Desempenho

O código deve permitir rodar em modo teste com poucos bits e em modo final com número elevado de bits.

### RNF05 - Clareza acadêmica

As hipóteses adotadas, especialmente a escolha de Ts, devem estar explicitamente declaradas no relatório.

---

## 7. Fórmulas Teóricas de Referência

### 7.1 Função Q

```text
Q(x) = 0,5 erfc(x / sqrt(2))
```

### 7.2 BPSK

```text
Pb = Q(sqrt(2 Eb/N0))
```

### 7.3 M-PSK

Para M >= 4, com mapeamento Gray:

```text
Pb ~= (2/b) Q(sqrt(2 b Eb/N0) sin(pi/M))
```

### 7.4 M-QAM quadrada

Para M-QAM quadrada, com mapeamento Gray:

```text
Pb ~= (4/b)(1 - 1/sqrt(M)) Q(sqrt((3b/(M-1)) Eb/N0))
```

---

## 8. Riscos e Mitigações

| Risco | Impacto | Mitigação |
|---|---|---|
| BER zerada em alto Eb/N0 | Curva sem informação estatística | Aumentar número de bits ou usar parada por número mínimo de erros |
| Curva simulada deslocada da teórica | Erro metodológico aparente | Revisar normalização de constelação, pulso e ruído |
| Mapeamento natural comparado com teoria Gray | BER simulada pode ficar acima da teórica | Implementar Gray coding ou declarar a diferença no relatório |
| Atraso de grupo mal compensado | Constelação recebida distorcida | Validar amostragem após filtro casado |
| RRC com SPS baixo | Resolução temporal limitada | Declarar SPS = 4 conforme hipótese do sistema |
| Ambiguidade de Ts | Questionamento metodológico | Declarar Ts = 1/fc no relatório |

---

## 9. Critérios de Aceite Final

O projeto estará completo quando:

- Todas as modulações exigidas tiverem sido simuladas.
- NRZ e RRC tiverem sido avaliados.
- Todos os valores de Eb/N0 tiverem sido simulados.
- As constelações transmitidas e recebidas tiverem sido geradas.
- As curvas BER simuladas e teóricas estiverem no mesmo gráfico.
- A BER diminuir com o aumento de Eb/N0.
- Modulações de maior ordem apresentarem pior desempenho para o mesmo Eb/N0.
- O relatório IEEE explicar metodologia, hipóteses, resultados e limitações.
- O código entregue for o mesmo utilizado para gerar as figuras do relatório.

---

## 10. Escopo Fora desta Entrega

Este PRD não inclui a implementação do código Python final, pois a implementação será conduzida separadamente. Também não inclui resultados numéricos finais, pois eles dependem da execução da simulação.
