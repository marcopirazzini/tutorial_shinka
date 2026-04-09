# EVOLVE-BLOCK-START
import numpy as np
from scipy.optimize import linprog

def _generate_initial_centers():
    """
    Generate a deterministic, hexagonally-inspired spread of 26 centers:
      - 1 center
      - 7 around center (inner ring)
      - 18 around center (outer ring)
    Centers are clipped to [0.01, 0.99].
    """
    n = 26
    centers = np.zeros((n, 2))

    centers[0] = np.array([0.5, 0.5])

    # Inner ring: 7 points
    r1 = 0.28
    for i in range(7):
        angle = 2 * np.pi * i / 7.0
        centers[1 + i] = np.array([0.5 + r1 * np.cos(angle),
                                   0.5 + r1 * np.sin(angle)])

    # Outer ring: 18 points
    r2 = 0.46
    for i in range(18):
        angle = 2 * np.pi * i / 18.0
        centers[8 + i] = np.array([0.5 + r2 * np.cos(angle),
                                   0.5 + r2 * np.sin(angle)])

    centers = np.clip(centers, 0.01, 0.99)
    return centers

def _lp_radii_from_centers(centers):
    """
    Given fixed centers, solve an LP to maximize the sum of radii
    under:
      - r_i >= 0
      - r_i <= distance to wall
      - r_i + r_j <= dist(center_i, center_j) for all i<j
    Returns radii as a 1D array of length n.
    If LP fails, falls back to a conservative feasible radii via shrink.
    """
    centers = np.asarray(centers)
    n = centers.shape[0]

    # Distances between centers
    dist = np.zeros((n, n))
    for i in range(n):
        for j in range(i + 1, n):
            d = np.linalg.norm(centers[i] - centers[j])
            dist[i, j] = dist[j, i] = d

    # Wall distances (max possible radius w.r.t walls)
    wall_dist = np.minimum.reduce([
        centers[:, 0], centers[:, 1],
        1.0 - centers[:, 0], 1.0 - centers[:, 1]
    ])
    # Build LP: maximize sum r_i
    # Equivalent to minimize sum (-r_i)
    A_ub = []
    b_ub = []
    # Pairwise non-overlap: r_i + r_j <= dist_ij
    for i in range(n):
        for j in range(i + 1, n):
            row = np.zeros(n)
            row[i] = 1.0
            row[j] = 1.0
            A_ub.append(row)
            b_ub.append(dist[i, j])
    A_ub = np.asarray(A_ub)
    b_ub = np.asarray(b_ub)

    bounds = [(0.0, wall_dist[k]) for k in range(n)]
    c = -np.ones(n)

    try:
        res = linprog(c, A_ub=A_ub, b_ub=b_ub, bounds=bounds, method='highs')
        if res.success:
            radii = res.x
            radii = np.maximum(radii, 0.0)
            return radii
    except Exception:
        pass

    # Fallback if LP fails: a simple guaranteed-feasible radii (shrink until feasible)
    radii = wall_dist.copy()
    for _ in range(5):
        for i in range(n):
            for j in range(i + 1, n):
                dist_ij = dist[i, j]
                if radii[i] + radii[j] > dist_ij:
                    if radii[i] + radii[j] == 0:
                        continue
                    scale = dist_ij / (radii[i] + radii[j])
                    radii[i] *= scale
                    radii[j] *= scale
    radii = np.maximum(radii, 0.0)
    return radii

def _anneal_centers_lp(centers_init):
    """
    Run a lightweight simulated-annealing style optimization:
      - Start from centers_init
      - Repeatedly perturb a randomly chosen center and re-solve radii via LP
      - Accept improvements; occasional stochastic moves to escape local optima
    Returns the best (centers, radii) found.
    """
    centers_best = None
    radii_best = None
    best_sum = -1.0

    n = centers_init.shape[0]
    rng = np.random.default_rng(42)

    # 3 restarts with small perturbations to explore different basins
    for restart in range(3):
        if restart == 0:
            centers_cur = centers_init.copy()
        else:
            centers_cur = centers_init.copy()
            centers_cur += rng.normal(scale=0.04, size=centers_cur.shape)
            centers_cur = np.clip(centers_cur, 0.01, 0.99)

        radii_cur = _lp_radii_from_centers(centers_cur)
        sum_cur = float(np.sum(radii_cur))

        step = 0.12
        T = 0.08  # temperature-like control for acceptance

        for it in range(180):
            i = rng.integers(n)
            dx = rng.uniform(-step, step)
            dy = rng.uniform(-step, step)

            centers_new = centers_cur.copy()
            centers_new[i, 0] = np.clip(centers_new[i, 0] + dx, 0.01, 0.99)
            centers_new[i, 1] = np.clip(centers_new[i, 1] + dy, 0.01, 0.99)

            radii_new = _lp_radii_from_centers(centers_new)
            sum_new = float(np.sum(radii_new))

            delta = sum_new - sum_cur
            if delta > 0 or rng.random() < np.exp(delta / max(1e-9, T)):
                centers_cur = centers_new
                radii_cur = radii_new
                sum_cur = sum_new

            if it % 60 == 0 and it > 0:
                step *= 0.85
                T *= 0.95

        if sum_cur > best_sum:
            best_sum = sum_cur
            centers_best = centers_cur
            radii_best = radii_cur

    return centers_best, radii_best

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
    centers_init = _generate_initial_centers()
    centers_opt, radii_opt = _anneal_centers_lp(centers_init)

    # Safety: clamp and ensure non-negativity
    centers_opt = np.clip(centers_opt, 0.0, 1.0)
    radii_opt = np.maximum(radii_opt, 0.0)

    return centers_opt, radii_opt

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