# Estrutura de Células do MVP Marimo - Versão Refatorada

## 📋 Resumo

O MVP foi reorganizado em **13 células independentes**, cada uma focando em um ou dois requisitos funcionais (RF##) do PRD. Cada célula:
- ✅ Tem nome descritivo com sufixo `_c[##]`
- ✅ Retorna variáveis com sufixo `_c[##]` para evitar colisões no Marimo
- ✅ Inclui docstring explicando qual requisito (RF##) atende
- ✅ Tem dependências declaradas explicitamente nos parâmetros

---

## 🎯 Mapa de Células por Requisito da Proposta

| Célula | Sufixo | Requisitos | Descrição |
|--------|--------|-----------|-----------|
| **imports** | `_c01` | N/A | Imports de bibliotecas (marimo, numpy, matplotlib, scipy) |
| **title** | `_c02` | N/A | Título e intro da simulação |
| **ui_sliders** | `_c03` | RF01, RF07 | **Sliders interativos**: num_bits, seed, alpha (RRC roll-off) |
| **params_fixed** | `_c04` | RF03-RF12 | Parâmetros fixos: fc, sps, Eb/N0, modulações, pulsos |
| **rf01_rng_init** | `_c05` | RF01 | Inicializa RNG com seed controlada pelo slider |
| **gray_coding** | `_c06` | Proposta 5.5 | Funções Gray ↔ inteiros (essencial para teoria) |
| **rf03_rf04_constellation** | `_c07` | RF03, RF04, RF05 | Constrói PSK/QAM normalizadas (energia média = 1) |
| **rf02_symbol_mapping** | `_c08` | RF02, RF13 | Mapeia bits → símbolos (Gray) e vice-versa |
| **rf07_pulse_shaping** | `_c09` | RF07 | Gera NRZ/RRC com alpha do input (controlável) |
| **rf15_theoretical_ber** | `_c10` | RF15 | Curvas teóricas M-PSK/M-QAM (Gray-mapped) |
| **rf08-rf12_link_sim** | `_c11` | RF08-RF14 | **Cadeia completa**: modulação → AWGN → demod → MF → sampling → decisão |
| **results** | `_c12` | RF14 | Loop de Monte Carlo: executa simulação para todas combos |
| **plots_final** | `_c13` | RF03, RF12 | Visualiza BER (simulada vs teórica) + constelações |

---

## 🎮 Controles Interativos (Célula `ui_sliders_c03`)

### Sliders Disponíveis

1. **📊 Número de bits (RF01)**
   - Range: 10.000 → 500.000
   - Padrão: 50.000
   - Impacto: Afeta tamanho da sequência pseudoaleatória e qualidade estatística de BER

2. **🌱 Seed do RNG**
   - Range: 0 → 1.000
   - Padrão: 42
   - Impacto: Reproduzibilidade da sequência aleatória

3. **📈 RRC alpha (RF07) [0.0-1.0]**
   - Input text: "0.15" (padrão)
   - Impacto: Fator de roll-off do pulso RRC
   - ⚠️ Validar: 0 ≤ α ≤ 1

---

## 📊 Fluxo de Dados Entre Células

```
ui_sliders_c03 (controles)
    ↓
rf01_rng_init_c05 (seed) → bits aleatórios
    ↓
rf02_symbol_mapping_c08 (Gray mapping)
    ↓
rf03_rf04_constellation_c07 (PSK/QAM)
    ↓
rf07_pulse_shaping_c09 (NRZ/RRC com alpha)
    ↓
rf08-rf12_link_sim_c11 (transmissor → canal → receptor)
    ↓
results_c12 (BER simulada vs teórica)
    ↓
plots_final_c13 (gráficos)
```

---

## 🔧 Como Adicionar Novos Sliders

Edite a célula `ui_sliders_c03`:

```python
novo_param_slider_c03 = mo_c01.ui.slider(
    value=10,           # valor padrão
    start=1,            # mínimo
    stop=100,           # máximo
    step=1,             # incremento
    label="Descrição (RF##)"
)
```

Depois declare como parâmetro em outra célula:
```python
def minha_funcao_c##(novo_param_slider_c03):
    valor = novo_param_slider_c03.value
```

---

## 🔄 Como o Alpha (RRC) é Controlado

1. **Input box em `ui_sliders_c03`**: `alpha_input_c03 = mo_c01.ui.text(value="0.15", ...)`
2. **Leitura em `rf07_pulse_shaping_c09`**:
   ```python
   alpha_c09 = float(alpha_input_c03.value)
   ```
3. **Aplicação em `pulse_coeffs_c09()`**: Calcula coeficientes RRC com esse alpha
4. **Propagação**: Link simulation (`rf08-rf12_link_sim_c11`) usa os pulsos gerados

---

## ✅ Requisitos Implementados

| RF | Descrição | Célula | Status |
|----|-----------|--------|--------|
| RF01 | Geração de bits pseudoaleatória | c05, c03 | ✅ Com slider |
| RF02 | Agrupamento de bits (b = log₂M) | c08 | ✅ Gray-mapped |
| RF03 | Constelação M-PSK | c07 | ✅ Normalizada |
| RF04 | Constelação M-QAM | c07 | ✅ Normalizada |
| RF05 | Normalização de energia | c07 | ✅ Média = 1 |
| RF06 | Eb = 1/b (implícito) | c11 | ✅ |
| RF07 | Formatação pulso NRZ/RRC | c09 | ✅ Alpha controlável |
| RF08 | Modulação banda passante | c11 | ✅ |
| RF09 | AWGN | c11 | ✅ σ calculado |
| RF10 | Demodulação coerente | c11 | ✅ I/Q demod |
| RF11 | Filtro casado | c11 | ✅ Convolução reversa |
| RF12 | Amostragem | c11 | ✅ Sampling correto |
| RF13 | Decisão (distância mínima) | c08 | ✅ Argmin |
| RF14 | Cálculo BER | c12 | ✅ Monte Carlo |
| RF15 | Curvas teóricas | c10 | ✅ PSK/QAM Gray |

---

## 🧪 Testes Realizados

- ✅ Compilação: `py_compile` passou
- ✅ Carregamento: `runpy.run_path()` retorna "app"
- ✅ Estrutura: 13 células com nomes `_c##` e sufixos
- ✅ Sliders: Funcionam em tempo real no Marimo

---

## 📝 Notas de Desenvolvimento

1. **Nomes de células**: Seguem padrão `[function_purpose]_c[##]`
2. **Variáveis**: Todas retornam com sufixo `_c[##]` para evitar renomeação automática do Marimo
3. **Documentação**: Cada célula tem docstring com RF requirement e breve explicação
4. **Gray Mapping**: Implementado conforme Proposta seção 5.5; obrigatório para fórmulas teóricas
5. **Parâmetros**: Separados em "controles" (ui_sliders) vs "fixos" (params_fixed)

---

## 🚀 Próximas Melhorias

- [ ] Adicionar slider para faixa de Eb/N0
- [ ] Slider para número de síbolos por constelação
- [ ] Exportar resultados em CSV
- [ ] Visualização interativa de pulsos (NRZ vs RRC)
