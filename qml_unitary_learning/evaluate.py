"""Evaluator for QML ansatz evolution — unitary approximation.

Scoring
-------
    combined_score = mean_fidelity − 0.1 × (mean_depth / 50)

The target unitary is a random 4-qubit circuit on a linear chain
(qubits 0-1-2-3).  It is generated once from TARGET_SEED and reused
for every candidate.

Environment variables (set by the notebook, read by the subprocess):
    TARGET_SEED   seed for the target unitary        (default 42)
    NUM_RUNS      evaluation runs per candidate       (default 3)
    NUM_WORKERS   parallel workers for runs           (default 1)
    N_STEPS       COBYLA iterations per run           (default 200)
"""

import math
import os
from functools import partial

import numpy as np
import pennylane as qml

from shinka.core import run_shinka_eval

# ── Configuration from environment ──────────────────────────────────────────────

TARGET_SEED = int(os.environ.get("TARGET_SEED", "42"))
NUM_RUNS = int(os.environ.get("NUM_RUNS", "3"))
NUM_WORKERS = int(os.environ.get("NUM_WORKERS", "1"))
N_STEPS = int(os.environ.get("N_STEPS", "200"))

N_QUBITS = 4
COUPLING_MAP = {(0, 1), (1, 2), (2, 3)}


# ── Target unitary ──────────────────────────────────────────────────────────────


def generate_target_unitary(seed: int = TARGET_SEED) -> np.ndarray:
    """Random 3-layer circuit on the linear chain → unitary matrix."""
    rng = np.random.default_rng(seed)
    angles = rng.uniform(0, 2 * np.pi, size=24)

    def target_circuit():
        idx = 0
        for _layer in range(3):
            for i in range(N_QUBITS):
                qml.RY(angles[idx], wires=i)
                idx += 1
            for i in range(N_QUBITS):
                qml.RZ(angles[idx], wires=i)
                idx += 1
            qml.CNOT(wires=[0, 1])
            qml.CNOT(wires=[1, 2])
            qml.CNOT(wires=[2, 3])

    return qml.matrix(target_circuit, wire_order=range(N_QUBITS))()


_TARGET_U = generate_target_unitary()


# ── ShinkaEvolve interface ──────────────────────────────────────────────────────


def get_experiment_kwargs(run_index: int) -> dict:
    """Same target for every run; different optimisation seed."""
    return {
        "target_unitary": _TARGET_U,
        "seed": run_index,
        "n_steps": N_STEPS,
    }


def validate_fn(result) -> tuple[bool, str | None]:
    """Reject circuits that violate the linear-chain connectivity."""
    if not isinstance(result, dict):
        return False, f"Expected dict, got {type(result).__name__}"

    fidelity = result.get("fidelity")
    if fidelity is None or math.isnan(fidelity):
        return False, "Fidelity is missing or NaN"

    if result.get("n_params", 0) <= 0:
        return False, f"Invalid parameter count: {result.get('n_params')}"

    for gate_name, wires in result.get("operations", []):
        if len(wires) == 2:
            edge = (min(wires), max(wires))
            if edge not in COUPLING_MAP:
                return False, (
                    f"Connectivity violation: {gate_name} on wires {wires}. "
                    f"Only adjacent pairs allowed: {sorted(COUPLING_MAP)}"
                )
    return True, None


def aggregate_metrics(results: list, results_dir: str) -> dict:
    """Aggregate multi-run results into a single fitness score."""
    fidelities = [r["fidelity"] for r in results]
    depths = [r["depth"] for r in results]
    gate_counts = [r["gate_count"] for r in results]
    n_params = results[0]["n_params"]

    mean_fid = float(np.mean(fidelities))
    std_fid = float(np.std(fidelities))
    mean_depth = float(np.mean(depths))
    mean_gates = float(np.mean(gate_counts))

    combined_score = mean_fid - 0.1 * (mean_depth / 50.0)

    # Text feedback visible to the LLM
    lines = [
        f"Mean fidelity: {mean_fid:.4f} (std: {std_fid:.4f})",
        f"Circuit depth: {mean_depth:.0f}, gate count: {mean_gates:.0f}, params: {n_params}",
    ]
    if mean_fid < 0.5:
        lines.append("Fidelity is low — try more layers or different gate types (RZ, RX).")
    elif mean_fid > 0.9 and mean_depth > 30:
        lines.append("High fidelity but deep — try fewer layers or more efficient entanglement.")
    if std_fid > 0.1:
        lines.append("High variance across seeds — possible trainability issue.")

    np.savez(
        os.path.join(results_dir, "extra.npz"),
        fidelities=np.array(fidelities),
        depths=np.array(depths),
    )

    return {
        "combined_score": combined_score,
        "public": {
            "fidelity_mean": round(mean_fid, 4),
            "fidelity_std": round(std_fid, 4),
            "depth": round(mean_depth, 1),
            "gate_count": round(mean_gates, 1),
            "n_params": n_params,
        },
        "private": {"per_run_fidelities": fidelities},
        "text_feedback": "\n".join(lines),
    }


# ── Entrypoint ──────────────────────────────────────────────────────────────────


def main(program_path: str, results_dir: str) -> None:
    metrics, correct, error_msg = run_shinka_eval(
        program_path=program_path,
        results_dir=results_dir,
        experiment_fn_name="run_experiment",
        num_runs=NUM_RUNS,
        get_experiment_kwargs=get_experiment_kwargs,
        validate_fn=validate_fn,
        aggregate_metrics_fn=partial(aggregate_metrics, results_dir=results_dir),
        run_workers=NUM_WORKERS,
    )
    print("OK" if correct else f"FAILED: {error_msg}")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--program_path", default="initial_program.py")
    parser.add_argument("--results_dir", default="results_test")
    args = parser.parse_args()

    os.makedirs(args.results_dir, exist_ok=True)
    main(args.program_path, args.results_dir)
