# 01 — 16-QAM, Gray coding and symbol detection

The project uses 16-QAM in complex baseband. Each QAM symbol carries

```math
b = \\log_2 M = \\log_2 16 = 4
```

bits. A square 16-QAM constellation has four levels on each axis:

```math
I,Q \\in \\{-3,-1,+1,+3\\}.
```

The unnormalized constellation has average symbol energy

```math
E_s = \\mathbb{E}\{|I+jQ|^2\} = 10.
```

For simulation, normalize the constellation by `sqrt(10)`:

```math
s_m = \\frac{I_m + jQ_m}{\\sqrt{10}}, \\qquad \\mathbb{E}\{|s_m|^2\}=1.
```

This matters because the noise variance must be compatible with the actual symbol energy used in the simulator.

## Gray coding

Gray coding maps adjacent constellation decisions to bit labels that differ by one bit whenever possible. In AWGN, most errors are nearest-neighbor errors, so Gray coding reduces BER for a given symbol-error pattern.

For this project, Gray coding is less central than SER, because the requested metric is symbol error rate. Still, keeping Gray coding from the previous notebook is good practice and keeps the mapper/demapper compatible with future BER plots.

## Decision rule

After OFDM demodulation and ZF equalization, each received subcarrier symbol is a complex number `X_hat[k]`. The hard decision is nearest-neighbor detection:

```math
\\hat{s} = \\arg\\min_{s_m\\in\\mathcal{S}} |\\hat{x}-s_m|^2.
```

In AWGN with equiprobable symbols, nearest-neighbor detection is the maximum-likelihood detector.

## Implementation notes

- Keep the constellation normalized to unit average energy.
- Do not mix normalized and unnormalized constellations in the SER calculation.
- SER compares symbol indices, not bits.
- BER compares recovered bits and only makes sense if mapper and demapper use the same labeling.
