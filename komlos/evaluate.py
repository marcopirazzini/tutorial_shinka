"""
Evaluator for Komlós conjecture hard instance search.

Scores matrix constructions based on maximizing the minimum discrepancy:
    min_{x ∈ {-1,+1}^n} ||Ax||_∞

Higher discrepancy = harder case for the conjecture.
The conjecture claims this should be O(1) for unit column vectors,
so finding larger values represents harder instances.
"""

import os
import argparse
import numpy as np
from typing import Dict, Any, List, Optional, Tuple

from shinka.core import run_shinka_eval

N = int(os.environ.get("N", "8"))
NUM_RUNS = int(os.environ.get("NUM_RUNS", "1"))
NUM_WORKERS = int(os.environ.get("NUM_WORKERS", "1"))


def get_experiment_kwargs(run_idx: int) -> dict:
    return {"n": N, "random_seed": int(np.random.randint(0, 2**31))}


def validate_fn(
    result: Tuple[np.ndarray, float, np.ndarray],
) -> Tuple[bool, Optional[str]]:
    if not isinstance(result, tuple) or len(result) != 3:
        return False, "Result should be a tuple of (vectors, cost, signs)"

    vectors, cost, signs = result

    if vectors.ndim != 2:
        return False, f"Vectors should be 2D, got {vectors.ndim}D"

    n = vectors.shape[0]
    if vectors.shape[1] != n:
        return False, f"Expected square matrix, got shape {vectors.shape}"

    if not np.isfinite(cost):
        return False, f"Cost is not finite: {cost}"

    if signs.shape != (n,):
        return False, f"Signs shape should be ({n},), got {signs.shape}"

    if not np.all(np.isin(signs, [-1, 1])):
        return False, "Signs should only contain -1 or +1"

    col_norms = np.linalg.norm(vectors, axis=0)
    if not np.allclose(col_norms, 1.0, atol=1e-6):
        return False, f"Column norms should be 1, got min={col_norms.min():.4f}, max={col_norms.max():.4f}"

    actual_inf_norm = np.abs(vectors @ signs).max()
    if not np.isclose(actual_inf_norm, cost, atol=1e-6):
        return False, f"Reported cost {cost:.6f} doesn't match actual ||Ax||_∞ = {actual_inf_norm:.6f}"

    return True, None


def aggregate_metrics(
    results: List[Tuple[np.ndarray, float, np.ndarray]],
    results_dir: str,
) -> Dict[str, Any]:
    INVALID_PENALTY = -1000.0

    if not results:
        return {
            "combined_score": INVALID_PENALTY,
            "public": {"status": "no_results", "num_runs": 0},
            "private": {},
            "extra_data": {},
            "text_feedback": "no results",
        }

    costs = [r[1] for r in results]
    max_cost = max(costs)
    avg_cost = sum(costs) / len(costs)
    min_cost = min(costs)

    best_idx = costs.index(max_cost)
    best_vectors, _, best_signs = results[best_idx]

    return {
        "combined_score": max_cost,
        "public": {
            "status": "valid",
            "max_discrepancy": max_cost,
            "avg_discrepancy": avg_cost,
            "min_discrepancy": min_cost,
            "n": best_vectors.shape[0],
            "num_runs": len(results),
        },
        "private": {
            "all_costs": costs,
            "best_signs": best_signs.tolist(),
        },
        "extra_data": {},
        "text_feedback": f"max_discrepancy={max_cost:.6f} | avg={avg_cost:.6f} | min={min_cost:.6f}",
    }


def main(program_path: str, results_dir: str) -> None:
    os.makedirs(results_dir, exist_ok=True)
    metrics, correct, error_msg = run_shinka_eval(
        program_path=program_path,
        results_dir=results_dir,
        experiment_fn_name="run_komlos",
        num_runs=NUM_RUNS,
        run_workers=NUM_WORKERS,
        get_experiment_kwargs=get_experiment_kwargs,
        validate_fn=validate_fn,
        aggregate_metrics_fn=lambda results: aggregate_metrics(results, results_dir),
    )
    print("OK" if correct else f"FAILED: {error_msg}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--program_path", required=True)
    parser.add_argument("--results_dir", required=True)
    args = parser.parse_args()
    main(args.program_path, args.results_dir)
