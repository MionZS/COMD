# 05 — Zero-forcing equalization and noise enhancement

After CP removal and FFT, each subcarrier follows

```math
Y[k] = H[k]X[k]+V[k].
```

The zero-forcing equalizer is

```math
E[k] = \\frac{1}{H[k]}.
```

The equalized symbol is

```math
\\hat{X}[k] = \\frac{Y[k]}{H[k]} = X[k] + \\frac{V[k]}{H[k]}.
```

ZF perfectly removes the deterministic channel coefficient if `H[k]` is known and nonzero. However, it does not remove noise. It scales the noise by `1/H[k]`.

## Equalized noise variance

If the FFT-domain noise has variance `sigma_V^2`, then after ZF:

```math
\\mathbb{E}\{|V[k]/H[k]|^2\} = \\frac{\\sigma_V^2}{|H[k]|^2}.
```

Therefore, the effective SNR per carrier is proportional to

```math
\\mathrm{SNR}_{eff,k} \\propto |H[k]|^2.
```

This is why carrier `k=15` has a much worse constellation than carrier `k=10` at the same average SNR.

## ZF is intentionally basic here

ZF is not the best equalizer under noise. MMSE would avoid extreme noise amplification by trading residual distortion for lower noise enhancement. The assignment specifically asks for ZF, so the poor-carrier behavior is expected and should be discussed rather than hidden.

## Validation check

With no AWGN and `N_CP=5`, the maximum numerical error after ZF should be near machine precision:

```math
\\max |\\hat{X}[k]-X[k]| \\approx 10^{-15} \\text{ to } 10^{-13}.
```

If the no-noise error is large, the likely bugs are CP length, convolution indexing, FFT/IFFT axis, or wrong channel FFT length.
