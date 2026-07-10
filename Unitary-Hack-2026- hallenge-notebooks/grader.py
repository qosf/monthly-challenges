"""Public helpers and tests for the logical-memory decoding challenge.

The tests check interfaces and small invariants. They are transparent so that
participants can debug their own submissions. Maintainers can add hidden tests
with other distances, probabilities, bases, and seeds.
"""

from __future__ import annotations

import math
import re
from typing import Any, Callable

import numpy as np
import pymatching
import stim

NOISE_FIELDS = {
    "before_round_data_depolarization",
    "after_clifford_depolarization",
    "after_reset_flip_probability",
    "before_measure_flip_probability",
}


def as_binary_array(values: Any) -> np.ndarray:
    """Return a one-dimensional uint8 array containing only 0 and 1."""
    arr = np.asarray(values, dtype=np.uint8).reshape(-1)
    if np.any((arr != 0) & (arr != 1)):
        raise ValueError("array must contain only 0/1 values")
    return arr


def reference_repetition_syndrome(error: np.ndarray) -> np.ndarray:
    e = as_binary_array(error)
    if e.size < 2:
        raise ValueError("need at least two data bits")
    return np.bitwise_xor(e[:-1], e[1:]).astype(np.uint8)


def reference_decode_repetition_syndrome(syndrome: np.ndarray) -> np.ndarray:
    s = as_binary_array(syndrome)
    c0 = np.zeros(s.size + 1, dtype=np.uint8)
    for i, bit in enumerate(s):
        c0[i + 1] = c0[i] ^ bit
    c1 = 1 - c0
    return c1.astype(np.uint8) if int(c1.sum()) < int(c0.sum()) else c0.astype(np.uint8)


def make_reference_memory_circuit(distance: int, rounds: int, p: float, basis: str = "z") -> stim.Circuit:
    if basis not in {"x", "z"}:
        raise ValueError("basis must be 'x' or 'z'")
    if distance < 3 or distance % 2 == 0:
        raise ValueError("distance must be an odd integer at least 3")
    if rounds < 1:
        raise ValueError("rounds must be positive")
    if not 0.0 <= p < 0.5:
        raise ValueError("p must be in [0, 0.5)")
    return stim.Circuit.generated(
        f"surface_code:rotated_memory_{basis}",
        distance=distance,
        rounds=rounds,
        before_round_data_depolarization=p,
        after_clifford_depolarization=p,
        after_reset_flip_probability=p,
        before_measure_flip_probability=p,
    )


def replace_detector_error_probabilities(
    model: stim.DetectorErrorModel,
    probability: float = 0.01,
) -> stim.DetectorErrorModel:
    """Return a detector error model with all error probabilities flattened."""
    if not 0.0 <= probability < 0.5:
        raise ValueError("probability must be in [0, 0.5)")
    text = str(model)
    text = re.sub(r"error\([0-9eE+\-.]+\)", f"error({float(probability):.17g})", text)
    return stim.DetectorErrorModel(text)


def detector_error_probabilities(model: stim.DetectorErrorModel) -> np.ndarray:
    """Extract numeric probabilities from error(...) instructions."""
    return np.asarray([float(x) for x in re.findall(r"error\(([^)]*)\)", str(model))], dtype=float)


def reference_build_matching(
    circuit: stim.Circuit,
    *,
    weighted: bool = True,
    uniform_probability: float = 0.01,
) -> pymatching.Matching:
    dem = circuit.detector_error_model(decompose_errors=True)
    if not weighted:
        dem = replace_detector_error_probabilities(dem, probability=uniform_probability)
    return pymatching.Matching.from_detector_error_model(dem)


def reference_sample_and_decode(
    circuit: stim.Circuit,
    matching: pymatching.Matching,
    shots: int,
    seed: int,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    if shots <= 0:
        raise ValueError("shots must be positive")
    sampler = circuit.compile_detector_sampler(seed=seed)
    detector_events, observable_flips = sampler.sample(shots, separate_observables=True)
    predictions = matching.decode_batch(detector_events)
    return detector_events, observable_flips, predictions


def reference_logical_failures(predictions: np.ndarray, observable_flips: np.ndarray) -> np.ndarray:
    pred = np.asarray(predictions, dtype=np.uint8)
    obs = np.asarray(observable_flips, dtype=np.uint8)
    if pred.ndim == 1:
        pred = pred[:, None]
    if obs.ndim == 1:
        obs = obs[:, None]
    if pred.shape != obs.shape:
        raise ValueError(f"shape mismatch: {pred.shape} != {obs.shape}")
    return np.any(pred != obs, axis=1)


def reference_wilson_interval(
    failures: int,
    shots: int,
    z: float = 1.959963984540054,
) -> tuple[float, float, float]:
    if shots <= 0:
        raise ValueError("shots must be positive")
    if failures < 0 or failures > shots:
        raise ValueError("failures must be between 0 and shots")
    phat = failures / shots
    denom = 1.0 + z * z / shots
    center = (phat + z * z / (2.0 * shots)) / denom
    radius = z * math.sqrt((phat * (1.0 - phat) + z * z / (4.0 * shots)) / shots) / denom
    return float(phat), float(max(0.0, center - radius)), float(min(1.0, center + radius))


def reference_estimate_logical_error_rate(
    circuit: stim.Circuit,
    shots: int,
    seed: int,
    *,
    decoder_circuit: stim.Circuit | None = None,
    weighted: bool = True,
) -> dict[str, Any]:
    if decoder_circuit is None:
        decoder_circuit = circuit
    matching = reference_build_matching(decoder_circuit, weighted=weighted)
    detector_events, observable_flips, predictions = reference_sample_and_decode(circuit, matching, shots, seed)
    failures = reference_logical_failures(predictions, observable_flips)
    failure_count = int(np.count_nonzero(failures))
    rate, ci_low, ci_high = reference_wilson_interval(failure_count, shots)
    return {
        "shots": int(shots),
        "failures": failure_count,
        "rate": rate,
        "ci_low": ci_low,
        "ci_high": ci_high,
        "num_detectors": int(circuit.num_detectors),
        "num_observables": int(circuit.num_observables),
        "num_qubits": int(circuit.num_qubits),
    }


def check_repetition_syndrome(fn: Callable[[np.ndarray], np.ndarray]) -> str:
    error = np.array([1, 1, 0, 1, 0], dtype=np.uint8)
    expected = np.array([0, 1, 1, 1], dtype=np.uint8)
    actual = as_binary_array(fn(error))
    assert np.array_equal(actual, expected)
    assert np.array_equal(as_binary_array(fn(np.array([0, 0, 0], dtype=np.uint8))), np.array([0, 0], dtype=np.uint8))
    return "check_repetition_syndrome passed"


def check_repetition_decoder(fn: Callable[[np.ndarray], np.ndarray]) -> str:
    cases = [
        np.array([0, 0], dtype=np.uint8),
        np.array([1, 0, 1, 1], dtype=np.uint8),
        np.array([0, 1, 1, 0, 1, 0], dtype=np.uint8),
    ]
    for syndrome in cases:
        correction = as_binary_array(fn(syndrome))
        assert correction.size == syndrome.size + 1
        assert np.array_equal(reference_repetition_syndrome(correction), syndrome)
        reference = reference_decode_repetition_syndrome(syndrome)
        assert int(correction.sum()) == int(reference.sum())
    return "check_repetition_decoder passed"


def check_make_memory_circuit(fn: Callable[[int, int, float, str], stim.Circuit]) -> str:
    circuit = fn(3, 3, 0.001, "z")
    assert isinstance(circuit, stim.Circuit)
    assert circuit.num_detectors == 24
    assert circuit.num_observables == 1
    assert circuit.num_qubits > 0
    noiseless = fn(3, 2, 0.0, "x")
    assert noiseless.num_observables == 1
    return "check_make_memory_circuit passed"


def check_build_matching(fn: Callable[..., pymatching.Matching]) -> str:
    circuit = make_reference_memory_circuit(3, 3, 0.001)
    weighted = fn(circuit, weighted=True)
    unweighted = fn(circuit, weighted=False, uniform_probability=0.01)
    assert isinstance(weighted, pymatching.Matching)
    assert isinstance(unweighted, pymatching.Matching)
    assert weighted.num_detectors == circuit.num_detectors
    assert unweighted.num_detectors == circuit.num_detectors
    return "check_build_matching passed"


def check_sample_and_decode(fn: Callable[..., tuple[np.ndarray, np.ndarray, np.ndarray]]) -> str:
    circuit = make_reference_memory_circuit(3, 3, 0.001)
    matching = reference_build_matching(circuit)
    detectors, observables, predictions = fn(circuit, matching, shots=16, seed=1234)
    detectors = np.asarray(detectors)
    observables = np.asarray(observables)
    predictions = np.asarray(predictions)
    assert detectors.shape == (16, circuit.num_detectors)
    assert observables.shape == (16, circuit.num_observables)
    if predictions.ndim == 1:
        assert predictions.shape == (16,)
    else:
        assert predictions.shape == observables.shape
    return "check_sample_and_decode passed"


def check_logical_failures(fn: Callable[[np.ndarray, np.ndarray], np.ndarray]) -> str:
    pred = np.array([[0], [1], [1], [0]], dtype=np.uint8)
    obs = np.array([[0], [0], [1], [1]], dtype=np.uint8)
    expected = np.array([False, True, False, True])
    actual = np.asarray(fn(pred, obs), dtype=bool)
    assert actual.shape == (4,)
    assert np.array_equal(actual, expected)
    actual_flat = np.asarray(fn(pred.reshape(-1), obs.reshape(-1)), dtype=bool)
    assert np.array_equal(actual_flat, expected)
    return "check_logical_failures passed"


def check_wilson_interval(fn: Callable[..., tuple[float, float, float]]) -> str:
    rate, low, high = fn(5, 10)
    assert abs(rate - 0.5) < 1e-12
    assert 0.23 < low < 0.24
    assert 0.76 < high < 0.77
    rate0, low0, high0 = fn(0, 20)
    assert rate0 == 0.0
    assert low0 == 0.0
    assert 0.0 < high0 < 0.2
    return "check_wilson_interval passed"


def check_zero_noise_pipeline(
    make_circuit_fn: Callable[..., stim.Circuit],
    estimate_fn: Callable[..., dict[str, Any]],
) -> str:
    circuit = make_circuit_fn(3, 3, 0.0, "z")
    result = estimate_fn(circuit, shots=64, seed=99)
    required = {"shots", "failures", "rate", "ci_low", "ci_high", "num_detectors", "num_observables", "num_qubits"}
    assert required.issubset(result.keys())
    assert result["shots"] == 64
    assert result["failures"] == 0
    assert result["rate"] == 0.0
    assert result["ci_low"] == 0.0
    assert result["num_detectors"] == circuit.num_detectors
    assert result["num_observables"] == 1
    return "check_zero_noise_pipeline passed"


def run_smoke_tests() -> None:
    print(check_repetition_syndrome(reference_repetition_syndrome))
    print(check_repetition_decoder(reference_decode_repetition_syndrome))
    print(check_make_memory_circuit(make_reference_memory_circuit))
    print(check_build_matching(reference_build_matching))
    print(check_sample_and_decode(reference_sample_and_decode))
    print(check_logical_failures(reference_logical_failures))
    print(check_wilson_interval(reference_wilson_interval))
    print(check_zero_noise_pipeline(make_reference_memory_circuit, reference_estimate_logical_error_rate))


def test_public_reference_checks() -> None:
    check_repetition_syndrome(reference_repetition_syndrome)
    check_repetition_decoder(reference_decode_repetition_syndrome)
    check_make_memory_circuit(make_reference_memory_circuit)
    check_build_matching(reference_build_matching)
    check_sample_and_decode(reference_sample_and_decode)
    check_logical_failures(reference_logical_failures)
    check_wilson_interval(reference_wilson_interval)
    check_zero_noise_pipeline(make_reference_memory_circuit, reference_estimate_logical_error_rate)


def test_replace_detector_error_probabilities() -> None:
    circuit = make_reference_memory_circuit(3, 3, 0.001)
    model = circuit.detector_error_model(decompose_errors=True)
    flattened = replace_detector_error_probabilities(model, 0.02)
    probs = detector_error_probabilities(flattened)
    assert probs.size > 0
    assert np.allclose(probs, 0.02)


def test_low_noise_logical_rate_is_small() -> None:
    circuit = make_reference_memory_circuit(3, 3, 0.001)
    result = reference_estimate_logical_error_rate(circuit, shots=256, seed=7)
    assert result["rate"] <= 0.2


if __name__ == "__main__":
    print("Running grader.py smoke checks...")
    run_smoke_tests()
    print("grader.py smoke checks passed")
