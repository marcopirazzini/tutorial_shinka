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
    rng = np.random.default_rng(314159)
    anchors = [
        [0.5, 0.5],
        [0.05, 0.05],
        [0.95, 0.05],
        [0.05, 0.95],
        [0.95, 0.95],
        [0.05, 0.5],
        [0.95, 0.5],
        [0.5, 0.05],
        [0.5, 0.95],
    ]
    centers_list = [np.array(anchor, dtype=float) for anchor in anchors[:n]]
    while len(centers_list) < n:
        current_centers = np.array(centers_list)
        current_radii = compute_max_radii(current_centers)
        best_center = None
        best_score = -1.0
        for _ in range(700):
            candidate = rng.uniform(0.02, 0.98, size=2)
            score = evaluate_candidate(candidate, current_centers, current_radii)
            if score > best_score:
                best_score = score
                best_center = candidate
            if best_score >= 0.06:
                break
        if best_score <= 1e-4:
            base = current_centers[rng.integers(len(current_centers))]
            best_center = np.clip(base + rng.uniform(-0.04, 0.04, size=2), 0.02, 0.98)
        centers_list.append(np.clip(best_center, 0.02, 0.98))
    centers = np.array(centers_list[:n])
    radii = compute_max_radii(centers)
    return centers, radii


def evaluate_candidate(center, centers, radii):
    wall_gap = min(center[0], center[1], 1.0 - center[0], 1.0 - center[1])
    if wall_gap <= 0:
        return -1.0
    gap = wall_gap
    for existing, existing_radius in zip(centers, radii):
        dist = np.linalg.norm(center - existing) - existing_radius
        gap = min(gap, dist)
        if gap <= 0:
            return -1.0
    return gap


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
    for _ in range(12):
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