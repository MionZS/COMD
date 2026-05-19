import marimo

__generated_with = "0.21.1"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo

    return


@app.cell
def _():
    import numpy as np
    import matplotlib.pyplot as plt
    from scipy.signal import welch

    return np, plt, welch


@app.cell
def _():
    # Parâmetros de simulação

    Tb = 1          # intervalo de pulso 
    fs = 10/Tb      # taxa de 
    T = 1/fs        # intervalo 
    N = int(Tb/T)   # Numero de amostras
    Nb = 10**4      # Numero de bits
    return N, Nb, T, Tb, fs


@app.cell
def _(N, Nb, np):
    # Pulso de transmissao NRZ
    p = np.ones(N)

    ak = np.random.choice([-1, 1], Nb)

    # Preenchimento de zeros (Nb zeros pra cada amostra(N))
    # Sinalizacao polar
    x = np.zeros(N*Nb)
    x[::N] = ak
    y = np.convolve(x,p)        # nomenclatura y p sinal saida vai ser diferente para comunicacao
    return x, y


@app.cell
def _(T, Tb, np, plt, x, y):
    fig, ax = plt.subplots(2,1, figsize=(9,4))

    ax[0].stem(x)
    ax[0].set_xlabel('n (amostras)')
    ax[0].set_ylabel('x[n]')
    ax[0].grid()

    t = np.linspace(0, len(y)*T, len(y))

    ax[1].plot(y)
    ax[1].set_xlabel('t (amostras)')
    ax[1].set_ylabel('x[n]')
    ax[1].grid()

    # Limites do grafico
    ax[0].set_xlim(0,200)
    ax[1].set_xlim(0,20*Tb)

    plt.tight_layout()
    plt.show()
    return


@app.cell
def _(fs, np, welch, y):
    def psd_polar_nrz(f, Tb):
        Sy_f = Tb/4 * np.sinc(f*Tb)**2
        return Sy_f

    # Sy_f = lambda f, Tb: Tb/4 * np.sinc(f*Tb)**2

    ff, Sy_f = welch(y, fs, nperseg=1024, detrend=False, return_onesided=False)

    ff = np.fft.fftshift(ff)
    Sy_f = np.fft.fftshift(Sy_f)
    return Sy_f, ff, psd_polar_nrz


@app.cell
def _(Sy_f, Tb, ff, fs, np, plt, psd_polar_nrz):
    plt.figure()
    f_th = np.linspace(-fs/2, fs/2, 500)
    plt.plot(f_th, 10*np.log10(psd_polar_nrz(f_th, Tb)))
    plt.plot(ff, 10*np.log10(Sy_f))

    plt.ylim(-60, 1)
    plt.grid()

    plt.show()
    return


if __name__ == "__main__":
    app.run()
