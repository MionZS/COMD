
# COMD

Projeto de simulação BER e notebooks Marimo para o Trabalho 2.

## Estrutura

- `src/trabalho2/` contém os scripts e notebooks executáveis.
- `docs/` concentra a documentação do projeto.
- `TC2_PRD_Proposta_Todo/` guarda os materiais do enunciado e proposta do TC2.
- `output/` é usado para figuras geradas em tempo de execução.

## Entradas úteis

- `docs/SUMARIO_EXECUT_REFATORACAO.md`
- `docs/GUIA_CONTROLES_INTERATIVOS.md`
- `docs/CHANGELOG_v2_refactored.md`
- `docs/estrutura_cells_marimo_v2.md`

## Execução

```bash
uv run python -m src.trabalho2.generate_plots
uv run python -m src.trabalho2.ber_aggregator
uv run python -m src.trabalho2.ber_aggregator_10x
```
