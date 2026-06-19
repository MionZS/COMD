# 06 — Bit loading by disabling weak carriers

The assignment asks for an extreme bit-loading strategy: find the five worst carriers and disable them.

For the assigned channel, disable:

```text
k = 14, 15, 16, 17, 18
```

The original system uses all 32 carriers. The disabled-carrier system uses only 27 active carriers.

## What improvement means here

The SER average improves because the worst carriers are no longer included in the average error calculation. These carriers have deep fades, so after ZF their noise clouds are very large and they dominate the total error count.

The improvement is especially visible at medium/high SNR: good carriers become reliable, but deeply faded carriers still have enough noise amplification to produce errors. Removing them prevents the average SER from being dragged down by the spectral notch.

## Important caveat

This implementation is carrier disabling, not full adaptive loading.

Full bit loading would choose different modulation orders and possibly different power levels per subchannel. For example, strong carriers could use 16-QAM or 64-QAM, weak carriers could use QPSK or be disabled, and power could be reallocated under a total-power constraint.

The project asks for the simpler extreme version: remove the five weakest carriers.

## Reporting language

Use precise language:

- Correct: “A SER média calculada sobre as portadoras ativas melhora porque as portadoras em desvanecimento profundo foram removidas.”
- Correct: “O ZF amplifica ruído nas portadoras com baixo |H[k]|.”
- Avoid: “O canal melhorou.” The physical channel did not change.
- Avoid: “Bit-loading completo.” This is carrier disabling, a minimal bit-loading-like strategy.
