"""Seed program for QML ansatz evolution — unitary approximation.

The EVOLVE-BLOCK contains the ansatz structure (gate types, entanglement
pattern, layer count).  ShinkaEvolve mutates this block across generations.

Everything outside the block is fixed: the training loop, cost function,
and result packaging.
"""

import os

import numpy as np
import pennylane as qml
from scipy.optimize import minimize

N_QUBITS = 4
COUPLING_MAP = [(0, 1), (1, 2), (2, 3)]


# EVOLVE-BLOCK-START
N_PARAMS = 16


def ansatz(params):
    """Parameterized quantum circuit ansatz on 4 qubits.

    CONNECTIVITY CONSTRAINT — linear chain: 0-1-2-3
    Two-qubit gates are ONLY allowed between adjacent qubits:
        (0,1), (1,2), (2,3)

    N_PARAMS must match the number of parameters consumed.
    """
    idx = 0
    # Layer 1: single-qubit rotations + forward entanglement
    for i in range(N_QUBITS):
        qml.RY(params[idx], wires=i)
        idx += 1
    qml.CNOT(wires=[0, 1])
    qml.CNOT(wires=[1, 2])
    qml.CNOT(wires=[2, 3])

    # Layer 2: single-qubit rotations + reverse entanglement
    for i in range(N_QUBITS):
        qml.RY(params[idx], wires=i)
        idx += 1
    qml.CNOT(wires=[2, 3])
    qml.CNOT(wires=[1, 2])
    qml.CNOT(wires=[0, 1])

    # Layer 3: single-qubit rotations
    for i in range(N_QUBITS):
        qml.RY(params[idx], wires=i)
        idx += 1

    # Layer 4: single-qubit rotations
    for i in range(N_QUBITS):
        qml.RY(params[idx], wires=i)
        idx += 1
# EVOLVE-BLOCK-END


# ── Fixed interface (not evolved) ───────────────────────────────────────────────


def run_experiment(target_unitary, seed=0, n_steps=None):
    """Train the ansatz to approximate *target_unitary*.

    Args:
        target_unitary: Complex ndarray of shape (2^N_QUBITS, 2^N_QUBITS).
        seed:           Random seed for parameter initialisation.
        n_steps:        COBYLA iterations.  Falls back to the N_STEPS env-var
                        (default 200).

    Returns:
        dict with keys: fidelity, depth, gate_count, n_params, operations.
    """
    if n_steps is None:
        n_steps = int(os.environ.get("N_STEPS", "200"))

    rng = np.random.default_rng(seed)
    d = 2**N_QUBITS

    # Initialise parameters
    x0 = rng.uniform(0, 2 * np.pi, size=N_PARAMS)

    # Cost: 1 − Hilbert-Schmidt process fidelity
    def cost(params):
        V = qml.matrix(ansatz, wire_order=range(N_QUBITS))(params)
        fid = np.abs(np.trace(target_unitary.conj().T @ V)) ** 2 / d**2
        return 1.0 - np.real(fid)

    # Optimise
    result = minimize(cost, x0, method="COBYLA", options={"maxiter": n_steps})
    final_fidelity = 1.0 - float(result.fun)

    # Extract circuit metadata via tape
    with qml.queuing.AnnotatedQueue() as q:
        ansatz(x0)
    tape = qml.tape.QuantumScript.from_queue(q)

    operations = [(op.name, op.wires.tolist()) for op in tape.operations]
    depth = tape.graph.get_depth() if hasattr(tape.graph, "get_depth") else len(tape)
    gate_count = len(operations)

    return {
        "fidelity": final_fidelity,
        "depth": depth,
        "gate_count": gate_count,
        "n_params": N_PARAMS,
        "operations": operations,
    }
