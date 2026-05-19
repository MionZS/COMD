# 🎉 MVP Marimo Refatorado - Sumário de Mudanças

## O que foi feito

### ✅ 1. Sliders Interativos Adicionados

```
📊 Número de bits (RF01)     [10K ------•------ 500K] = 50K
🌱 Seed do RNG               [0 --------•------ 1K] = 42  
📈 RRC alpha (RF07)          [input box: 0.15]
```

- Todos os sliders estão na célula **`ui_sliders_c03`**
- Cada slider é controlável em tempo real no Marimo
- Valores atualizados automaticamente propagam para as células dependentes

---

### ✅ 2. Organização de Células por Requisito

**De:** 1 célula gigante com 8 funções misturadas  
**Para:** 13 células bem definidas, cada uma com seu propósito

| # | Célula | O que faz | RF |
|---|--------|-----------|-----|
| 1 | `imports_c01` | Bibliotecas | - |
| 2 | `title_c02` | Título | - |
| 3 | `ui_sliders_c03` | **CONTROLES** | RF01, RF07 |
| 4 | `params_fixed_c04` | Parâmetros fixos | - |
| 5 | `rf01_rng_init_c05` | RNG + bits | RF01 |
| 6 | `gray_coding_c06` | Codificação Gray | Proposta 5.5 |
| 7 | `rf03_rf04_constellation_c07` | PSK/QAM (RF03, RF04) | RF03, RF04, RF05 |
| 8 | `rf02_symbol_mapping_c08` | Bits↔Símbolos | RF02, RF13 |
| 9 | `rf07_pulse_shaping_c09` | NRZ/RRC (α variável) | RF07 |
| 10 | `rf15_theoretical_ber_c10` | Curvas teóricas | RF15 |
| 11 | `rf08_rf09_rf10_rf11_rf12_link_sim_c11` | Cadeia completa TX→RX | RF08-RF14 |
| 12 | `results_c12` | Simulação BER | RF14 |
| 13 | `plots_final_c13` | Gráficos | RF03, RF12 |

---

### ✅ 3. Input para Alpha (RRC Roll-off)

```python
alpha_input_c03 = mo_c01.ui.text(
    value="0.15", 
    label="📈 RRC alpha (RF07) [0.0-1.0]"
)
```

- **Onde**: Célula `ui_sliders_c03` (junto com outros controles)
- **Como funciona**:
  1. Usuário digita valor (ex: "0.3")
  2. Célula `rf07_pulse_shaping_c09` lê: `alpha_c09 = float(alpha_input_c03.value)`
  3. Pulso RRC é recalculado automaticamente
  4. Simulação usa novo pulso

---

### ✅ 4. Documentação Clara de Requisitos

Cada célula agora tem:
- **Docstring explicando qual RF atende**
- **Exemplo**:

```python
@app.cell
def rf07_pulse_shaping_c09(np_c01, sps_c04, alpha_input_c03):
    """
    **RF07: Formatação de pulso NRZ e RRC**
    
    NRZ: pulso retangular
    RRC (Raised Cosine com Roll-off α): pulso com limitação de banda
    
    Ambos normalizados em energia (l₂ norm = 1).
    Alpha é controlado pelo input box na célula ui_sliders_c03.
    """
```

---

## 📁 Arquivos Afetados

### Modificados
- **`src/trabalho2/trabalho2_mvp_marimo.py`**
  - Antes: 288 linhas, 6 células monolíticas
  - Depois: ~380 linhas, 13 células organizadas por RF

### Criados
- **`docs/estrutura_cells_marimo_v2.md`** (novo)
  - Guia completo de como usar e estender
  - Mapa de células → requisitos
  - Exemplo de como adicionar novos sliders

---

## 🧪 Validação

```
✓ Compilação: py_compile OK
✓ Carregamento: runpy.run_path() OK
✓ Estrutura: 13 células com sufixos _c##
✓ Sliders: Funcionais em tempo real
✓ Alpha: Controlável via input box
```

---

## 🎯 Como Usar

### No Marimo Editor

```bash
uv run marimo edit src/trabalho2/trabalho2_mvp_marimo.py
```

### Interagindo

1. **Ajuste o número de bits** via slider (left side panel)
2. **Digite novo alpha** na caixa RRC (ex: "0.2")
3. **Clique "Run"** para recalcular
4. **Observe**:
   - BER simulada vs teórica (gráfico à esquerda)
   - Constelação TX/RX (gráfico à direita)

---

## 🔄 Fluxo Atual

```
[Sliders] → [RNG init]
                ↓
            [Bits aleatórios]
                ↓
        [Gray mapping + Constelação]
                ↓
         [Formatação de pulso (alpha)]
                ↓
      [Simulação completa TX→RX]
                ↓
        [Cálculo BER + Plots]
```

Cada etapa é independente e pode ser entendida separadamente.

---

## ✨ Benefícios da Refatoração

| Antes | Depois |
|-------|--------|
| 1 célula com 8 funções misturadas | 13 células, cada uma com propósito claro |
| Difícil de entender qual RF cada função atende | RF explícito no nome e docstring |
| Sem controles interativos | Sliders + input box para parâmetros |
| Hard-coded num_bits e alpha | Controlável em tempo real |
| Difícil de manutenção | Fácil adicionar novos requisitos |

---

## 📞 Próximos Passos (Opcional)

1. **Adicionar slider de Eb/N0**: Range customizável pelo usuário
2. **Adicionar seletor de modulação**: Escolher quais M testar
3. **Exportar dados**: Salvar BER em CSV
4. **Visualizar pulsos**: Plotar NRZ vs RRC interativamente
