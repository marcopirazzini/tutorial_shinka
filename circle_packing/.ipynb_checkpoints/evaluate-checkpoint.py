"""
Evaluator for circle_packing_v2: pack 26 non-overlapping circles in [0,1]².
combined_score = sum of radii (higher is better; best known ≈ 2.635)
"""

import os
import argparse
import numpy as np
from typing import Dict, Any, List, Optional, Tuple

from shinka.core import run_shinka_eval

N_CIRCLES = 26
ATOL = 1e-6


def validate_packing(
    run_output: Tuple[np.ndarray, np.ndarray, float],
) -> Tuple[bool, Optional[str]]:
    centers, radii, reported_sum = run_output

    if not isinstance(centers, np.ndarray):
        centers = np.asarray(centers, dtype=float)
    if not isinstance(radii, np.ndarray):
        radii = np.asarray(radii, dtype=float)

    if centers.shape != (N_CIRCLES, 2):
        return False, f"centers.shape={centers.shape}, expected ({N_CIRCLES}, 2)"
    if radii.shape != (N_CIRCLES,):
        return False, f"radii.shape={radii.shape}, expected ({N_CIRCLES},)"
    if not (np.all(np.isfinite(centers)) and np.all(np.isfinite(radii)) and np.isfinite(reported_sum)):
        return False, "Non-finite values in centers, radii, or reported_sum."
    if np.any(radii < 0):
        return False, f"Negative radii at indices {np.where(radii < 0)[0].tolist()}."

    actual_sum = float(np.sum(radii))
    if not np.isclose(actual_sum, reported_sum, atol=ATOL):
        return False, f"sum(radii)={actual_sum:.6f} != reported_sum={reported_sum:.6f}"

    for i, ((x, y), r) in enumerate(zip(centers, radii)):
        if x - r < -ATOL or x + r > 1 + ATOL or y - r < -ATOL or y + r > 1 + ATOL:
            return False, f"Circle {i} (x={x:.4f}, y={y:.4f}, r={r:.4f}) protrudes outside [0,1]²."

    for i in range(N_CIRCLES):
        for j in range(i + 1, N_CIRCLES):
            dist = np.linalg.norm(centers[i] - centers[j])
            if dist < radii[i] + radii[j] - ATOL:
                return False, f"Circles {i} & {j} overlap: dist={dist:.4f}, r_i+r_j={radii[i]+radii[j]:.4f}."

    return True, None


def aggregate_metrics(
    results: List[Tuple[np.ndarray, np.ndarray, float]],
    results_dir: str,
) -> Dict[str, Any]:
    centers, radii, reported_sum = results[0]
    sum_radii = float(np.sum(radii))
    n = len(radii)

    min_gap = min(
        np.linalg.norm(centers[i] - centers[j]) - radii[i] - radii[j]
        for i in range(n) for j in range(i + 1, n)
    )
    wall_slack_min = float(np.min([
        min(cx - r, cy - r, 1.0 - cx - r, 1.0 - cy - r)
        for (cx, cy), r in zip(centers, radii)
    ]))

    np.savez(os.path.join(results_dir, "extra.npz"),
             centers=centers, radii=radii, reported_sum=reported_sum)

    return {
        "combined_score": sum_radii,
        "public": {
            "n_circles": n,
            "sum_radii": round(sum_radii, 6),
            "min_radius": round(float(np.min(radii)), 6),
            "max_radius": round(float(np.max(radii)), 6),
            "min_gap": round(float(min_gap), 6),
            "wall_slack_min": round(wall_slack_min, 6),
            "centers_str": "\n".join(
                f"  [{i:2d}] ({x:.4f}, {y:.4f})" for i, (x, y) in enumerate(centers)
            ),
        },
        "private": {
            "reported_sum_of_radii": float(reported_sum),
            "actual_sum_of_radii": sum_radii,
        },
        "extra_data": {},
        "text_feedback": f"sum_radii={sum_radii:.6f} | min_gap={min_gap:.6f} | wall_slack_min={wall_slack_min:.6f}",
    }


def main(program_path: str, results_dir: str) -> None:
    os.makedirs(results_dir, exist_ok=True)
    metrics, correct, error_msg = run_shinka_eval(
        program_path=program_path,
        results_dir=results_dir,
        experiment_fn_name="run_packing",
        num_runs=1,
        get_experiment_kwargs=lambda i: {}, # This is necessary because otherwise we need "run_packing" to take "seed" as argument.
        validate_fn=validate_packing,
        aggregate_metrics_fn=lambda results: aggregate_metrics(results, results_dir),
    )
    print("OK" if correct else f"FAILED: {error_msg}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--program_path", required=True)
    parser.add_argument("--results_dir", required=True)
    args = parser.parse_args()
    main(args.program_path, args.results_dir)
