# Challenge 2026.08: Decode the Distance

This is a QOSF monthly challenge package.

## Summary

Participants decode small logical-memory experiments. They generate rotated
surface-code memory circuits with Stim, convert detector error models into
minimum-weight matching decoders with PyMatching, estimate logical failure rates
with Wilson intervals, and stress-test decoder calibration.

The central benchmark is concrete:

```text
For fixed circuit-level noise and shot budget, when does increasing code
 distance reduce the logical error rate?
```

## Files

- `challenge-2026.08-aug.ipynb`: participant notebook with TODOs and public tests.
- `challenge-2026.08-aug-solution.ipynb`: solved reference notebook.
- `grader.py`: deterministic helper functions and public tests.
- `requirements.txt`: runtime and validation dependencies.
- `validation_log.md`: validation commands and results.

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

On Windows, activate with `.venv\Scripts\activate`.

## Validation

```bash
python grader.py
pytest -q grader.py
python - <<'PY'
import nbformat
from nbclient import NotebookClient
for name in ["challenge-2026.08-aug.ipynb", "challenge-2026.08-aug-solution.ipynb"]:
    nb = nbformat.read(name, as_version=4)
    NotebookClient(nb, timeout=600, kernel_name="python3").execute()
    print(f"executed {name}")
PY
```

The default solved notebook should run in under a few minutes on a laptop CPU.
No GPU, cloud account, API key, or quantum hardware is required.

## Suggested scoring

- 15% repetition-code warm-up and binary-array handling.
- 20% valid Stim memory-circuit generation.
- 25% correct detector sampling, PyMatching decoding, and logical-failure counts.
- 15% logical-rate estimates with Wilson intervals.
- 15% distance-scaling benchmark with readable plots.
- 10% decoder-mismatch interpretation and failure-mode discussion.

Hidden tests can vary distances, rounds, bases, probabilities, seeds, shot
counts, and asymmetric noise profiles.


