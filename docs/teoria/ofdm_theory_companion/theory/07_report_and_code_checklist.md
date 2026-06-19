# 07 — Report and code validation checklist

## Mandatory project items

- [ ] Plot `|H[k]|` for all `k = 0,...,31`.
- [ ] Explicitly identify the five weakest subchannels.
- [ ] Use 16-QAM.
- [ ] Use `N=32` OFDM subcarriers.
- [ ] Use channel `h[n]=[0.3,-0.5,0,1,0.2,-0.3]^T`.
- [ ] Use cyclic prefix `N_CP=5`.
- [ ] Use ZF equalization in the frequency domain.
- [ ] At SNR = 30 dB, plot equalized constellations for `k=1`, `k=10`, `k=15`.
- [ ] Plot a mixed equalized constellation using all carriers.
- [ ] Plot SER from 0 to 30 dB in semilog scale.
- [ ] Include all 32 individual carrier SER curves.
- [ ] Include ideal-channel SER.
- [ ] Include global average OFDM SER.
- [ ] Disable the five weakest carriers and compare average SER against the original and ideal cases.

## Numerical validation

- [ ] `N_CP = len(h)-1 = 5`.
- [ ] `mean(|H[k]|^2) = sum(|h[n]|^2) = 1.47`.
- [ ] Five worst carriers: `[15, 17, 16, 14, 18]`.
- [ ] Worst set: `{14,15,16,17,18}`.
- [ ] `|H[1]| ≈ 0.7083`.
- [ ] `|H[10]| ≈ 1.7734`.
- [ ] `|H[15]| ≈ 0.2753`.
- [ ] Noiseless OFDM+channel+ZF recovery error near machine precision.

## Common bugs

1. Using `fftshift` and then reporting shifted carrier indices.
2. Using `N_CP=6` instead of the minimum `5`.
3. Adding time-domain noise with variance `1.47/SNR` instead of `1.47/(32*SNR)`.
4. Equalizing before removing the cyclic prefix.
5. Computing `H[k]` with FFT length 6 instead of 32.
6. Comparing equalized symbols to unnormalized constellation points.
7. Averaging disabled-carrier SER over all 32 carriers instead of active carriers only.
8. Calling carrier disabling “full adaptive bit loading”.
