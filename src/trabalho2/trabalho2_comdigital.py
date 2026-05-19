import marimo

__generated_with = "0.23.0"
app = marimo.App(width="medium")


@app.cell
def _():
    # This is a marimo notebook! Importing marimo in a cell is required to use any marimo functionality in code.
    import marimo as mo

    return


@app.cell
def _():
    import numpy as np
    import matplotlib.pyplot as plt
    from scipy.special import erfc
    import os

    return np, os, plt


@app.cell
def _(np, os, plt):
    rng = np.random.default_rng(42)
    OUT_DIR = 'output/trabalho2'
    os.makedirs(OUT_DIR, exist_ok=True)
    plt.rcParams['figure.dpi'] = 120
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
