# Source selection map

## Material selected

### User theory notes from `teoria.zip`

Selected:

- `teoria.md`: bit-to-symbol mapping, Gray coding, PSK/QAM constellation geometry, and passband/baseband interpretation.
- `teoria2.md`: AWGN, Eb/N0 relation, coherent demodulation, matched-filter interpretation, and noise as constellation spread.
- `teoria3.md`: detection in signal space, nearest-neighbor decision, BER/SER interpretation, and QAM distance reasoning.
- `teoria4.md`: simulation methodology, statistical convergence, BER/SER caveats, and interpretation of zero observed errors.
- `estrutura_cells_marimo_v2.md`: useful only as notebook-architecture inspiration: modular cells, mapping helpers, and validation flow.

Excluded or secondary:

- `line_coding_walkthrough.md`: useful for previous line-coding work, but not central to OFDM 16-QAM.
- `GUIA_CONTROLES_INTERATIVOS.md`: useful for UI structure, not for communication theory.
- `teoria5.md` and `teoria6.md`: useful general signal-space background, but too broad for the current OFDM deliverable.

### Professor slides from `OneDrive_1_6-18-2026.zip`

Selected:

- Aula 16–17: signal-space detection, QAM constellation interpretation, optimal decision under AWGN.
- Aula 18–19: linearly distorted channels, ISI, multipath, equalization, zero-forcing concepts.
- Aula 20–21: communication channel models, multipath, fading, frequency-selective behavior.
- Aula 22–23: multicarrier modulation, OFDM, DFT/IDFT model, cyclic prefix, channel diagonalization, ZF/MMSE equalization, DMT/bit-loading motivation.
- Aula 9: report-writing recommendations, used only as format guidance.

Secondary:

- Aula 12–13: passband digital systems and QAM background.
- Aula 14–15: AWGN and performance background.

Excluded:

- Probability/processes/line-coding-only classes, except as background.
- Information theory classes, except as distant motivation for bit loading.

### Lathi material from `Lathi - Modern Digital and Analog Communication Systems.zip`

Selected conceptually, not copied:

- Digital communications over linearly distortive channels: multipath, ISI, frequency-selective channels, equalization, ZF/MMSE.
- OFDM/DMT material: cyclic prefix, conversion of convolution into diagonal subchannels, and bit-loading motivation.
- QAM/passband material: complex baseband symbol model and quadrature representation.

The package does not reproduce book text or pages. It only contains derived notes and equations written for this project.

## Why this selection is enough for Project 3

The assignment does not require pulse shaping, passband simulation, synchronization, channel estimation, coding, or adaptive modulation. It asks for a baseband OFDM simulation with a known FIR channel and known equalizer. Therefore, the required theory is narrower:

1. 16-QAM symbols in the complex plane.
2. AWGN and SNR normalization.
3. Multipath FIR channel and frequency-selective fading.
4. OFDM with cyclic prefix.
5. FFT-domain scalar subchannels.
6. ZF equalization and noise enhancement.
7. SER estimation and carrier disabling.
