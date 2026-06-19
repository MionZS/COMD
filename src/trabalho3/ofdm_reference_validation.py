"""Reference validation helpers for TE903/EELT7026 OFDM 16-QAM project.
Run with: python ofdm_reference_validation.py
"""
import numpy as np

N = 32
H_TIME = np.array([0.3, -0.5, 0.0, 1.0, 0.2, -0.3], dtype=complex)
N_CP = len(H_TIME) - 1


def qam16_constellation():
    levels = np.array([-3, -1, 1, 3], dtype=float)
    const = np.array([i + 1j*q for q in levels for i in levels], dtype=complex) / np.sqrt(10)
    return const


def nearest_qam16(z, const):
    idx = np.argmin(np.abs(z[..., None] - const[None, :])**2, axis=-1)
    return const[idx]


def ofdm_tx(X):
    x = np.fft.ifft(X, n=N)
    return np.concatenate([x[-N_CP:], x])


def ofdm_rx_no_noise(x_cp):
    y_full = np.convolve(x_cp, H_TIME)
    # Remove CP from the start of the first received block. The useful region is N_CP:N_CP+N.
    y = y_full[N_CP:N_CP + N]
    return np.fft.fft(y, n=N)


def main():
    H = np.fft.fft(H_TIME, n=N)
    abs_H = np.abs(H)
    worst5 = np.argsort(abs_H)[:5]

    print(f"N = {N}")
    print(f"N_CP minimum = {N_CP}")
    print(f"sum |h[n]|^2 = {np.sum(np.abs(H_TIME)**2):.12g}")
    print(f"mean |H[k]|^2 = {np.mean(abs_H**2):.12g}")
    print("Worst 5 k by |H[k]|:", worst5.tolist())
    for k in worst5:
        print(f"  k={k:2d}, |H|={abs_H[k]:.9f}, gain={20*np.log10(abs_H[k]):.3f} dB")

    for k in [1, 10, 15]:
        print(f"Selected k={k:2d}, |H|={abs_H[k]:.9f}, gain={20*np.log10(abs_H[k]):.3f} dB")

    rng = np.random.default_rng(42)
    const = qam16_constellation()
    X = rng.choice(const, size=N)
    Y = ofdm_rx_no_noise(ofdm_tx(X))
    X_hat = Y / H
    max_err = np.max(np.abs(X_hat - X))
    print(f"No-noise full-chain max error = {max_err:.3e}")
    assert max_err < 1e-12, "No-noise OFDM/ZF validation failed"


if __name__ == "__main__":
    main()
