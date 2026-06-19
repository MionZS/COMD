# 02 — AWGN, SNR normalization and SER

The channel includes additive white Gaussian noise. In complex baseband, the noise sample can be generated as

```math
w[n] = \\sqrt{\\frac{\\sigma_w^2}{2}}(a[n]+jb[n]),
```

where `a[n]` and `b[n]` are independent standard normal variables. Here `sigma_w^2` means complex noise variance:

```math
\\mathbb{E}\{|w[n]|^2\}=\\sigma_w^2.
```

## SNR convention used in the OFDM simulator

The cleanest convention for this assignment is average received subcarrier SNR before equalization:

```math
\\mathrm{SNR} = \\frac{\\mathbb{E}\{|H[k]X[k]|^2\}}{\\mathbb{E}\{|V[k]|^2\}}.
```

With normalized 16-QAM, `E{|X[k]|^2}=1`. Therefore,

```math
\\mathbb{E}\{|H[k]X[k]|^2\}_{k} = \\frac{1}{N}\\sum_{k=0}^{N-1}|H[k]|^2.
```

For the assigned channel,

```math
\\frac{1}{32}\\sum_{k=0}^{31}|H[k]|^2 = \\sum_n |h[n]|^2 = 1.47.
```

So, for a target SNR in linear scale,

```math
\\sigma_V^2 = \\frac{1.47}{\\mathrm{SNR}_{lin}}.
```

`V[k]` is the FFT-domain noise.

## Time-domain noise with NumPy FFT convention

NumPy uses `ifft` with factor `1/N` and `fft` without factor `1/N`. If noise is added in the time domain after the channel and before CP removal/FFT, then

```math
\\sigma_V^2 = N\\sigma_t^2.
```

Therefore,

```math
\\sigma_t^2 = \\frac{1.47}{N\\,\\mathrm{SNR}_{lin}}
              = \\frac{1.47}{32\\,\\mathrm{SNR}_{lin}}.
```

This is the most common place to make the simulation wrong by a factor of 32.

## SER estimator

For subcarrier `k`, the SER estimate is

```math
\\mathrm{SER}_k = \\frac{N_{err,k}}{N_{sym,k}}.
```

The global average SER over all carriers is

```math
\\mathrm{SER}_{avg} = \\frac{\\sum_k N_{err,k}}{\\sum_k N_{sym,k}}.
```

For the disabled-carrier case, average only over active carriers.

## Interpretation

A zero measured SER at high SNR does not mean the true SER is mathematically zero. It only means no errors were observed in the finite Monte Carlo run. Use semilogy clipping only for plotting, not for the real numerical estimate.
