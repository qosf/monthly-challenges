# Probabilistic Error Cancellation (PEC) — QOSF Monthly Challenge

An intermediate challenge on **probabilistic error cancellation**, a quantum error
mitigation method that builds an *unbiased* estimator of an ideal expectation value by
sampling noisy circuits according to a quasiprobability decomposition (Temme, Bravyi &
Gambetta, 2017).

## Summary

Participants implement PEC from its component parts for depolarizing noise, apply it to a
GHZ state-preparation circuit, recover the ideal observable from noisy runs, and measure
the variance/overhead trade-off that makes PEC exact but exponentially costly.

## What's inside

- `pec_challenge.ipynb` — student notebook, 11 sequential exercises.
- `pec_challenge_solved.ipynb` — reference solved notebook.
- `grader.py` — autograder; each `grade_exN(...)` prints PASS/FAIL.
- `requirements.txt` — dependencies.
- `validation_log.txt` — output of the solved notebook (all 11 exercises pass).

Place `grader.py` in the same folder as the notebooks before running the grader cells.

## Task outline

1. GHZ circuit  2. Parity observable  3. Depolarizing noise model
4. Quasiprobability tables  5. Gate counting  6. Sampling overhead γ
7. Pauli insertion  8. One Monte-Carlo sample  9. The PEC estimator
10. End-to-end PEC run  11. Sample complexity

Section 7 (optional, requires `mitiq`) cross-checks the hand-rolled implementation against
the Unitary Foundation's Mitiq library.

## Conventions

- The GHZ circuit is preparation only: `H(0)`, CNOT ladder, then measurements.
- `N_DEMO = 4`: for an ideal GHZ state ⟨Z^⊗n⟩ = (1 + (−1)^n)/2, so even n gives target +1.
- The Aer depolarizing model attaches noise only to `h` and `cx`; sampled Pauli insertions
  (`x`/`y`/`z`) are noiseless, which keeps PEC exactly unbiased.
- `run_pec` is shot-based and returns a dict: `pec_value`, `stderr`, `signed_values`, `gamma`.

## Dependencies

`numpy`, `matplotlib`, `qiskit`, `qiskit-aer`. No GPU, cloud account, API key, or hardware
needed. `mitiq` is optional (Section 7 only).

## AI-use disclosure

Per the unitaryHACK Human-in-the-Loop policy: an LLM was used to help with notebook
structure, theory-section drafting, and review. All solution code and grader logic were
written and verified by the author, who can explain every cell.
