# 03 — Multipath FIR channel and frequency-selective fading

The assigned discrete channel is

```math
h[n] = [0.3, -0.5, 0, 1, 0.2, -0.3]^T.
```

It has length `L_h = 6`, so its memory is

```math
L_h-1=5.
```

In a single-carrier system, this channel spreads each transmitted symbol across neighboring symbol times, creating intersymbol interference (ISI). In OFDM, the cyclic prefix is used to control this spreading block-by-block.

## Frequency response

For `N=32`, the subcarrier response is

```math
H[k] = \\sum_{n=0}^{5}h[n]e^{-j2\\pi kn/32}, \\qquad k=0,1,\\ldots,31.
```

The channel is frequency-selective because `|H[k]|` is not constant over `k`. Some subcarriers have strong gain; others sit near fades.

## Deterministic weak subchannels

For the assigned channel and `N=32`, the five weakest subcarriers are:

```text
k = 15, 17, 16, 14, 18
```

ordered from weakest to less weak among the five. As a set:

```text
{14, 15, 16, 17, 18}
```

These carriers are clustered because the channel has a spectral notch near the middle of the DFT grid.

## Selected carriers required by the project

- `k=1`: moderate channel, `|H[1]| ≈ 0.7083`.
- `k=10`: good channel, `|H[10]| ≈ 1.7734`.
- `k=15`: poor channel, `|H[15]| ≈ 0.2753`.

After ZF equalization, the visual quality of the constellation is mostly controlled by `1/|H[k]|`. A smaller channel magnitude produces a larger equalized noise cloud.
