# 🎮 Guia Rápido: Como Usar os Controles Interativos

## Acesso aos Controles

Abra o MVP no Marimo:
```bash
cd d:\Uni\COMD
uv run marimo edit src/trabalho2/trabalho2_mvp_marimo.py
```

Os controles aparecem na célula **`ui_sliders_c03`** (visível logo após o título).

---

## 1️⃣ Slider: Número de Bits (RF01)

```
📊 Número de bits (RF01) [10K ────────•──────── 500K]
```

### O que faz
- Controla o tamanho da sequência pseudoaleatória gerada em RF01
- Mais bits = simulação mais longa, mas BER mais confiável estatisticamente

### Como usar
```
Arrastão slider para a direita  → mais bits  → BER mais estável
Arraste slider para a esquerda  → menos bits → simulação mais rápida
```

### Exemplos práticos
| Valor | Tempo aprox. | Confiabilidade | Caso de uso |
|-------|-------------|----------------|-------------|
| 10.000 | < 5s | Baixa | Testes rápidos |
| 50.000 | ~15s | Média | Default, bom balanço |
| 100.000 | ~30s | Alta | Validação |
| 500.000 | > 2min | Muito Alta | Comparação teórica |

---

## 2️⃣ Slider: Seed do RNG

```
🌱 Seed do RNG [0 ────────•──────── 1000] = 42
```

### O que faz
- Controla a sequência de números aleatórios gerada
- Mesma seed = mesma sequência reproduzível

### Como usar
```
Deixe em 42                → Resultados reproduzíveis (padrão)
Altere para outro número   → Diferentes realizações de AWGN/bits
```

### Por que mudar
- **Teste 1**: Seed=42 → BER simulada
- **Teste 2**: Seed=123 → BER simulada (outra realização)
- **Comparação**: Ambos devem dar resultados próximos se num_bits for grande

---

## 3️⃣ Input Box: RRC Alpha (RF07)

```
📈 RRC alpha (RF07) [0.0-1.0]  [input box: 0.15]
```

### O que faz
- Controla o fator de roll-off (α) do pulso RRC (Raised Cosine)
- Quanto maior α → pulso mais "arredondado" → menos ocupação de banda

### Como usar

**Escrever valor:**
```
1. Clique na caixa de texto
2. Delete valor anterior (0.15)
3. Digite novo valor (ex: 0.25)
4. Pressione Enter
```

### Valores recomendados

| α | Banda | Pulso | Caso |
|---|-------|-------|------|
| 0.0 | Mínima | Muito rígido (brick-wall) | Teórico |
| 0.15 | Padrão | Bom balanço | Default (use este) |
| 0.3 | Normal | Mais suave | Sistemas práticos |
| 0.5 | Larga | Muito suave | Pouca ISI |
| 1.0 | Muito larga | Máximo suavizado | Full Cosine |

### ⚠️ Regra de ouro
```
α = 0.15 é ótimo para a maioria dos casos
Não mude a menos que tenha razão específica
```

### Comparação visual: NRZ vs RRC

```
Ao lado, na célula `plots_final_c13`, você verá dois gráficos:
- Esquerda: BER simulada vs teórica para NRZ e RRC
- Direita: Constelações recebidas

Com α=0.15: RRC deve ter BER melhor (menos ISI)
Com α=0.0:  Ambos próximos (menos diferença)
```

---

## 🔄 Ciclo Completo de Testes

### Teste 1: Validar BER vs Teórico

```
1. Mantenha sliders no default:
   - Número de bits = 50.000
   - Seed = 42
   - Alpha = 0.15

2. Clique "Run" na célula `results_c12`

3. Observe o gráfico à esquerda:
   ✓ Pontos (●) = BER simulada
   ✓ Linhas (--) = BER teórica
   → Devem estar próximos!
```

### Teste 2: Impacto do Alpha

```
1. Execute primeira vez com alpha=0.15
2. Mude para alpha=0.5
3. Veja como RRC melhora (menos ISI)
```

### Teste 3: Reproduzibilidade

```
1. Execute com seed=42
2. Execute novamente com seed=42
   → Resultados idênticos ✓

3. Execute com seed=999
   → Resultados diferentes (mas próximos)
```

---

## 📊 O que Esperar nos Gráficos

### Gráfico de BER (Esquerda)

```
       BER
        1  ──────────────────────  ← Pior BER
       0.1  ───•───•───•───────   ← Simulada (●)
      0.01   ──┬──┬──┬──────     ← Teórica (--)
     0.001   ──────•────────    
    0.0001   ──────────────•─
           0dB  10dB  20dB  ← Eb/N0 (dB)
```

### Gráfico de Constelação (Direita)

```
       Q (quadratura)
        │     RX (●)
      1 │  •    • •        ← Constelação recebida
        │ • •  • • •
      0 ├─────X─────X─     ← Constelação ideal (×)
        │ • •  • • •
     -1 │  •    • •        ← TX (●) menos visível (muitos pontos)
        └─────────────┤
                      I
```

---

## 🆘 Troubleshooting

### Erro: "Não consigo digitar no input box de alpha"
- Certifique-se de clicar **dentro** da caixa de texto
- Feche qualquer modal antes de clicar

### Resultado: "Gráficos não mudam ao mover slider"
- Clique no botão **"Run"** ou pressione **Ctrl+Enter**
- Aguarde alguns segundos (simulação em andamento)

### Resultado: "BER muito alto mesmo com Eb/N0 alto"
- Aumente `num_bits` para melhor estatística
- Verifique se alpha está razoável (não > 1.0)

### Resultado: "Preciso resetar valores"
- Recarregue a página: **F5** ou **Ctrl+R**
- Depois clique "Run" novamente

---

## 💡 Dicas de Uso

✅ **DO**
- Mude um parâmetro por vez
- Sempre clique "Run" após mudança
- Aumente num_bits para comparações de teoria
- Use seed fixo para reproduzibilidade

❌ **DON'T**
- Não mude alpha para valores absurdos (< 0 ou > 2)
- Não rode com num_bits muito grande (< 10K) em máquinas lentas
- Não confie em BER com poucos bits (alta variância)

---

## 📖 Documentação Técnica

- Para entender melhor como cada parâmetro afeta a simulação:
- Ver: `estrutura_cells_marimo_v2.md`
- Seção: "Mapa de Células por Requisito"

---

## ✨ Exemplos de Cenários

### Cenário 1: Validar Codificação Gray
```
1. Deixe tudo padrão
2. Execute
3. Veja se BER simulada ≈ BER teórica
   → Gray working! ✓
```

### Cenário 2: Comparar NRZ vs RRC
```
Lado a lado no gráfico:
- PSK 4 / NRZ (linha azul)
- PSK 4 / RRC (linha laranja)
→ RRC deve estar abaixo (melhor BER) ✓
```

### Cenário 3: Impacto do Roll-off
```
1. Alpha = 0.05 (estreito)
   → BER pior (mais ISI)
   
2. Alpha = 0.15 (padrão)
   → BER melhor (menos ISI)
   
3. Alpha = 0.5 (muito largo)
   → BER melhor (quase sem ISI)
   → Mas usa mais banda!
```

---

**Pronto! Agora você pode explorar a simulação interativamente!** 🚀
