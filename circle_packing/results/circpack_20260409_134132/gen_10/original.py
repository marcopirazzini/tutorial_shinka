# EVOLVE-BLOCK-START
import numpy as np
from scipy.optimize import minimize, linprog

def compute_optimal_radii(centers):
    """
    Given center coordinates, find radii r_i that maximize sum(r_i)
    subject to:
    1) r_i <= centers[i, 0], r_i <= 1 - centers[i, 0]
    2) r_i <= centers[i, 1], r_i <= 1 - centers[i, 1]
    3) r_i + r_j <= ||c_i - c_j||
    """
    n = centers.shape[0]
    # Costs: minimize -sum(r_i)
    c = -np.ones(n)

    # Boundary constraints: r_i <= dist_to_wall
    bounds = []
    for i in range(n):
        cx, cy = centers[i]
        limit = min(cx, cy, 1.0 - cx, 1.0 - cy)
        bounds.append((0, max(0, limit)))

    # Pairwise constraints: r_i + r_j <= dist_ij
    A_ub = []
    b_ub = []
    for i in range(n):
        for j in range(i + 1, n):
            row = np.zeros(n)
            row[i] = 1
            row[j] = 1
            dist = np.linalg.norm(centers[i] - centers[j])
            A_ub.append(row)
            b_ub.append(dist)

    res = linprog(c, A_ub=A_ub, b_ub=b_ub, bounds=bounds, method='highs')
    if res.success:
        return res.x
    return np.zeros(n)

def construct_packing():
    """
    Uses a multi-start optimization: centers are optimized to maximize sum of radii
    computed by solving a linear program for fixed centers.
    """
    n = 26

    def compute_radii_lp(centers_np):
        return compute_optimal_radii(np.asarray(centers_np))

    def objective(flat_centers):
        centers_now = flat_centers.reshape((n, 2))
        r = compute_radii_lp(centers_now)
        return -float(np.sum(r))

    def generate_seed_centers(seed_id):
        rng = np.random.default_rng(seed_id)
        centers = np.zeros((n, 2))
        centers[0] = [0.5, 0.5]
        for i in range(8):
            angle = 2 * np.pi * i / 8
            centers[i + 1] = [0.5 + 0.28 * np.cos(angle),
                              0.5 + 0.28 * np.sin(angle)]
        for i in range(17):
            angle = 2 * np.pi * i / 17
            centers[i + 9] = [0.5 + 0.44 * np.cos(angle),
                              0.5 + 0.44 * np.sin(angle)]
        centers = np.clip(centers, 0.05, 0.95)
        centers += rng.normal(scale=0.012, size=centers.shape)
        centers = np.clip(centers, 0.05, 0.95)
        return centers

    seed_ids = [101, 202, 303, 404]
    best_centers = None
    best_radii = None
    best_score = -np.inf

    for sid in seed_ids:
        centers_seed = generate_seed_centers(sid)
        res = minimize(objective, centers_seed.flatten(),
                       method='L-BFGS-B',
                       bounds=[(0, 1)] * (2 * n),
                       options={'maxiter': 200, 'ftol': 1e-6, 'gtol': 1e-6})
        centers_candidate = res.x.reshape((n, 2))
        radii_candidate = compute_optimal_radii(centers_candidate)
        score = float(np.sum(radii_candidate))
        if score > best_score:
            best_score = score
            best_centers = centers_candidate
            best_radii = radii_candidate

    return best_centers, best_radii

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