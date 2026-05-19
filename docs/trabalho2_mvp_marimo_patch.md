# Patch do MVP em Marimo

Este patch reorganiza o MVP de `src/trabalho2/trabalho2_mvp_marimo.py` para evitar renomeações automáticas e colisões de nomes no Marimo.

## Regras aplicadas

1. Cada célula de código recebeu um nome descritivo com sufixo numérico:
   - `imports_c01`
   - `title_c02`
   - `params_c03`
   - `helpers_c04`
   - `results_c05`
   - `plots_c06`

2. Toda variável criada dentro de uma célula passou a terminar com o mesmo sufixo da célula.
   - Exemplo: `np_c01`, `kind_cases_c03`, `simulate_link_c04`, `results_c05`.

3. As variáveis usadas em outras células são retornadas explicitamente pela célula de origem.

4. O código ficou propositalmente cru e direto, sem `try/except`, sem modularização extra e sem camadas de robustez além do necessário para o MVP.

## Como editar sem quebrar o Marimo

- Se criar uma nova célula, escolha um novo sufixo e aplique ele em todas as variáveis locais.
- Se uma célula depender de algo de outra, essa variável precisa ser retornada pela célula de origem.
- Evite reutilizar nomes sem sufixo entre células.
- Mantenha a ordem de dependência simples: importações, parâmetros, funções auxiliares, simulação, plot.

## O que este MVP entrega

- bits aleatórios
- mapeamento Gray
- modulação PSK/QAM
- pulso NRZ ou RRC
- canal AWGN
- demodulação coerente
- filtro casado
- amostragem
- decisão por menor distância
- BER simulada e teórica
- constelações TX/RX