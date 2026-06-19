# OFDM 16-QAM — Theory Companion

Pacote de teoria selecionada para o Trabalho Computacional 3 de Comunicação Digital.

Este zip não é uma cópia dos PDFs/slides/livro. Ele é uma síntese técnica própria, organizada para sustentar o código Marimo e o relatório IEEE. A intenção é deixar claro quais partes da teoria são realmente usadas no projeto: 16-QAM, AWGN/SNR, canal multipercurso, OFDM, prefixo cíclico, equalização ZF, SER por subportadora e descarte das piores portadoras.

## Conteúdo

- `theory/01_qam_gray_detection.md`: 16-QAM, Gray coding e decisão por vizinho mais próximo.
- `theory/02_awgn_snr_ser.md`: AWGN, normalização de SNR e SER.
- `theory/03_multipath_frequency_selective_channel.md`: canal FIR, seletividade em frequência e subcanais ruins.
- `theory/04_ofdm_cyclic_prefix_fft_model.md`: modelo OFDM discreto, IFFT/FFT e prefixo cíclico mínimo.
- `theory/05_zf_equalization_noise_enhancement.md`: equalização zero-forcing e amplificação de ruído.
- `theory/06_bit_loading_carrier_disabling.md`: descarte das cinco piores portadoras.
- `theory/07_report_and_code_checklist.md`: checklist de validação do notebook e do relatório.
- `latex_snippets/`: trechos em LaTeX reutilizáveis no relatório.
- `tables/`: tabelas determinísticas do canal.
- `figures/channel_gain_reference.png`: figura de referência para o perfil |H[k]|.
- `validation/compute_ofdm_constants.py`: script para regenerar as constantes/tabelas.
- `source_notes/source_selection.md`: mapa das fontes selecionadas e excluídas.

## Constantes centrais

- N = 32 subportadoras.
- Canal: h[n] = [0.3, -0.5, 0, 1, 0.2, -0.3].
- Comprimento do canal: 6 amostras.
- Prefixo cíclico mínimo: N_CP = 5.
- Soma de energia do canal: sum |h[n]|² = 1.470000.
- Cinco piores portadoras, em ordem: [15, 17, 16, 14, 18].

## Regra de ouro da simulação

Com a convenção NumPy (`ifft` com fator 1/N e `fft` sem fator 1/N), se a SNR média for definida no domínio da frequência depois do canal e antes da equalização, use:

```text
sigma_v^2 = mean(|H[k]|^2) / SNR_linear = 1.47 / SNR_linear
sigma_t^2 = sigma_v^2 / N = 1.47 / (32*SNR_linear)
```

`Sigma_v^2` é a variância complexa por subportadora no domínio da frequência. `Sigma_t^2` é a variância complexa por amostra no domínio do tempo.
