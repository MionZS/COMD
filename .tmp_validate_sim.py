import numpy as np
from src.trabalho2.generate_plots import simulate_link, theoretical_ber

# Validation case
pulse = 'nrz'
kind = 'psk'
M = 16
b = int(np.log2(M))
num_bits = 2_000_000
num_symbols = max(1, int(num_bits // b))
seed = 42
rng = np.random.default_rng(seed)

ebn0_db = [0,4,8,12,16,20,24]
print(f'Validation case: pulse={pulse}, kind={kind}, M={M}, b={b}, num_symbols={num_symbols}, total_bits={num_symbols*b}')

sim = []
for eb in ebn0_db:
    ber, _, _, _ = simulate_link(kind, M, pulse, eb, num_symbols, rng, 0.15, 10.0, 16)
    sim.append(ber)

th = [theoretical_ber(kind, M, eb) for eb in ebn0_db]

np.set_printoptions(precision=6, suppress=False)
print('Eb/N0 (dB):', ebn0_db)
print('Simulated BER:', np.array(sim))
print('Theoretical BER:', np.array(th))
