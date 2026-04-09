# EVOLVE-BLOCK-START
import numpy as np

def construct_packing():
    """
    Construct an arrangement of 26 non-overlapping circles inside [0,1]^2
    that attempts to maximise the sum of their radii.

    Returns
    -------
    centers : np.ndarray, shape (26, 2)
        (x, y) centre coordinates, all in [0,1].
    radii : np.ndarray, shape (26,)
        Radius of each circle (non-negative, satisfying containment + non-overlap).
    """
    n = 26
    centers = np.zeros((n, 2))

    # --- Simple structured initialisation ---
    # Place one circle at the centre
    centers[0] = [0.5, 0.5]

    # 8 circles in an inner ring
    for i in range(8):
        angle = 2 * np.pi * i / 8
        centers[i + 1] = [0.5 + 0.28 * np.cos(angle),
                          0.5 + 0.28 * np.sin(angle)]

    # 17 circles in an outer ring
    for i in range(17):
        angle = 2 * np.pi * i / 17
        centers[i + 9] = [0.5 + 0.44 * np.cos(angle),
                          0.5 + 0.44 * np.sin(angle)]

    # Clip centres safely inside [0, 1]
    centers = np.clip(centers, 0.01, 0.99)

    # Compute maximum valid radii given these centre positions
    radii = compute_max_radii(centers)
    return centers, radii


def compute_max_radii(centers: np.ndarray) -> np.ndarray:
    """
    Given fixed circle centres, compute the largest radii such that:
      - every circle fits inside [0, 1]^2  (radius <= distance to nearest wall)
      - no two circles overlap             (r_i + r_j <= dist(c_i, c_j))

    Uses an iterative shrink-until-feasible approach.

    Parameters
    ----------
    centers : np.ndarray, shape (n, 2)

    Returns
    -------
    radii : np.ndarray, shape (n,)
    """
    n = centers.shape[0]

    # Upper bound from wall distances
    radii = np.array([
        min(cx, cy, 1.0 - cx, 1.0 - cy)
        for cx, cy in centers
    ], dtype=float)

    # Shrink pairwise overlapping radii proportionally (multiple passes for stability)
    for _ in range(5):
        for i in range(n):
            for j in range(i + 1, n):
                dist = np.linalg.norm(centers[i] - centers[j])
                if radii[i] + radii[j] > dist:
                    scale = dist / (radii[i] + radii[j])
                    radii[i] *= scale
                    radii[j] *= scale

    radii = np.maximum(radii, 0.0)
    return radii

# EVOLVE-BLOCK-END


# ── Fixed interface (not evolved) ─────────────────────────────────────────────

def run_packing():
    """
    Main entrypoint called by the evaluator.

    Returns
    -------
    centers      : np.ndarray, shape (26, 2)
    radii        : np.ndarray, shape (26,)
    sum_of_radii : float
    """
    centers, radii = construct_packing()
    sum_of_radii = float(np.sum(radii))
    return centers, radii, sum_of_radii
