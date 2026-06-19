---
description: "Use when: writing or reviewing OFDM simulation notebooks, SER plots, Monte Carlo analysis, or technical reports for TE903/EELT7026. Covers graph standards, text conventions, convergence rules."
applyTo: "src/trabalho3/**"
---

# Review Rules — Trabalho 3 (OFDM 16-QAM)

## Text Conventions

- **Acronyms: define twice.** First occurrence in the abstract: "termo em português (do inglês, *english term*, SIGLA)". Redefine first occurrence in body text the same way.
- **No math in abstract.** No variables, no equations, no `H[k]`, no `SNR`. Pure prose.
- **No math in introduction** unless explicitly defined inline.
- **Acronym example:** "taxa de erro de bit (do inglês, *bit error rate*, BER)" — not just "(BER)".

## Graph Standards

- **No titles.** Never call `ax.set_title()`. The caption (in the report) describes the figure.
- **Theoretical curves: solid line.** Minimum 601 points (step ~0.05 dB) to appear continuous.
- **Monte Carlo: points only.** `linestyle="none"`, never connect-the-dots. Use distinct markers per series.
- **Legends: descriptive, no conclusions.** "Média OFDM — 32 portadoras (Monte Carlo)" not "Média OFDM — pior que o canal ideal".

## SER Curves

- **Theoretical curve must match MC.** Same SNR convention (Es/N₀). For OFDM+ZF, compute per-subcarrier effective SNR:  
  `SNR_k = SNR_lin × |H[k]|² / mean(|H|²)`  
  Average SER_k across active subcarriers = theoretical OFDM+ZF SER.
- **Ideal AWGN curve** is a separate reference (lower bound), not the primary theoretical match.
- **Never say "it's expected the curves don't match."** If they don't match, fix the model or simulation.

## Monte Carlo Convergence

- **Minimum 100 symbol errors per point** for a reliable SER estimate.
- Points with <100 errors are **unconverged** — use hollow/open markers to visually distinguish them from converged points (filled markers).
- Report the convergence threshold in the figure caption or notes.

## Noise Model (OFDM, banda-base)

- Constellation normalized to unit energy: `s = (I + jQ) / sqrt(10)`
- Noise added in time domain: `σ²_t = mean(|H[k]|²) / (N × SNR_lin)`
- Always use `np.fft.fft` / `np.fft.ifft` with consistent normalization.
- CP length = channel memory = `len(h) - 1` = 5.
