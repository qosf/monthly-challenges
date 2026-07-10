# Validation log

Date: 2026-06-06

## Repository access note

A direct container clone of `qosf/monthly-challenges` failed because DNS
resolution for GitHub was unavailable:

```text
fatal: unable to access 'https://github.com/qosf/monthly-challenges.git/': Could not resolve host: github.com
```

The repository audit therefore used GitHub web/raw views. The generated
notebooks in this package were parsed and executed with `nbformat` and
`nbclient`.

## Clean-environment note

A fresh `.venv` creation succeeded, but `pip install -r requirements.txt` timed
out in this sandbox after downloading wheels and beginning installation. The
partial `.venv` was removed before packaging. Validation below was run in the
base Python environment available in the sandbox, which already had the required
packages installed. A final contributor should re-run the clean-venv commands on
their own machine before submission.

Package versions used for validation:

```text
Python 3.13.5
numpy 2.3.5
matplotlib 3.10.8
stim 1.16.0
pymatching 2.4.0
pytest 9.0.2
nbformat 5.10.4
nbclient 0.10.4
ipykernel 7.2.0
```

## Commands run

```bash
cd /mnt/data/challenge-2026.08-aug
MPLBACKEND=Agg PYTHONDONTWRITEBYTECODE=1 python grader.py
MPLBACKEND=Agg PYTHONDONTWRITEBYTECODE=1 pytest -q grader.py
MPLBACKEND=Agg PYTHONDONTWRITEBYTECODE=1 python - <<'PY'
import time, nbformat
from nbclient import NotebookClient
from pathlib import Path

start = time.perf_counter()
for name in ["challenge-2026.08-aug.ipynb", "challenge-2026.08-aug-solution.ipynb"]:
    t0 = time.perf_counter()
    nb = nbformat.read(name, as_version=4)
    NotebookClient(
        nb,
        timeout=600,
        kernel_name="python3",
        resources={"metadata": {"path": str(Path.cwd())}},
    ).execute()
    if name.endswith("-solution.ipynb"):
        nbformat.write(nb, name)
    print(f"executed {name} in {time.perf_counter() - t0:.2f}s")
print(f"notebook_total_seconds {time.perf_counter() - start:.2f}")
PY
```

## Results

```text
python grader.py
Running grader.py smoke checks...
check_repetition_syndrome passed
check_repetition_decoder passed
check_make_memory_circuit passed
check_build_matching passed
check_sample_and_decode passed
check_logical_failures passed
check_wilson_interval passed
check_zero_noise_pipeline passed
grader.py smoke checks passed

pytest -q grader.py
...                                                                      [100%]
3 passed in 1.30s

Notebook execution
executed challenge-2026.08-aug.ipynb in 3.58s
executed challenge-2026.08-aug-solution.ipynb in 4.39s
notebook_total_seconds 7.97
```

## Notebook and file checks

```text
challenge-2026.08-aug.ipynb
  cells 20
  outputs 0
  output_chars 0
  TODO_count 15
  NotImplementedError_count 12
  private_paths_or_tokens False

challenge-2026.08-aug-solution.ipynb
  cells 18
  outputs 9
  output_chars 100116
  TODO_count 0
  NotImplementedError_count 0
  private_paths_or_tokens False
```

Text files checked: `README.md`, `grader.py`, and `requirements.txt`.

Result: no private paths, API keys, credentials, or private data were used in
package source files or notebook outputs.


