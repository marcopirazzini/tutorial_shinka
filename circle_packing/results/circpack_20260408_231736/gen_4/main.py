# EVOLVE-BLOCK-START
import numpy as np
from scipy.optimize import minimize

def construct_packing():
    """
    Construct an arrangement of 26 non-overlapping circles inside [0,1]^2.
    Uses multiple restarts with jittered grids and local optimization.
    """
    n = 26
    best_sum = -1.0
    best_centers = None
    best_radii = None

    # Try multiple initializations to find a better global basin
    for seed in range(5):
        np.random.seed(seed)
        centers = initialize_hexagonal_grid(n)
        # Add jitter
        centers += np.random.uniform(-0.02, 0.02, size=centers.shape)
        centers = np.clip(centers, 0.05, 0.95)

        # Optimize positions to maximize the minimum distance between circles/walls
        centers = optimize_positions(centers)
        radii = compute_max_radii(centers)

        current_sum = np.sum(radii)
        if current_sum > best_sum:
            best_sum = current_sum
            best_centers = centers
            best_radii = radii

    return best_centers, best_radii

def optimize_positions(centers):
    """Optimize centers to maximize the space available for circles."""
    n = len(centers)

    def objective(c_flat):
        c = c_flat.reshape((n, 2))
        # We want to maximize the distance between centers and to walls
        # A common proxy is minimizing the energy of a repulsive potential
        dist_sum = 0
        for i in range(n):
            # Wall repulsion
            dist_sum += 1.0 / (c[i, 0]**2) + 1.0 / ((1-c[i, 0])**2)
            dist_sum += 1.0 / (c[i, 1]**2) + 1.0 / ((1-c[i, 1])**2)
            for j in range(i + 1, n):
                d = np.linalg.norm(c[i] - c[j])
                dist_sum += 1.0 / (d**2)
        return dist_sum

    res = minimize(objective, centers.flatten(), method='L-BFGS-B',
                   bounds=[(0.001, 0.999)] * (2*n), options={'maxiter': 100})
    return res.x.reshape((n, 2))


def initialize_hexagonal_grid(n):
    """
    Initialize circle centers using a hexagonal grid pattern with edge bias.
    """
    centers = np.zeros((n, 2))

    # Generate hexagonal grid points
    hex_points = []
    rows = int(np.ceil(np.sqrt(n / 0.866)))  # Hexagonal packing density
    cols = int(np.ceil(n / rows))

    for row in range(rows):
        for col in range(cols):
            if len(hex_points) >= n:
                break
            x = col * 0.5 / cols + 0.05
            y = row * 0.866 / rows + 0.05
            if row % 2 == 1:
                x += 0.25 / cols
            hex_points.append([x, y])

    # Sort by distance to nearest edge (prioritize edges/corners)
    hex_points = np.array(hex_points[:n])
    edge_dist = np.minimum(
        np.minimum(hex_points[:, 0], 1.0 - hex_points[:, 0]),
        np.minimum(hex_points[:, 1], 1.0 - hex_points[:, 1])
    )
    sorted_idx = np.argsort(edge_dist)

    centers = np.clip(hex_points[sorted_idx], 0.01, 0.99)
    return centers


def compute_max_radius_for_circle(idx, centers, radii):
    """
    Compute the maximum radius for circle idx given current positions and radii.
    """
    cx, cy = centers[idx]

    # Distance to walls
    r_wall = min(cx, cy, 1.0 - cx, 1.0 - cy)

    # Distance to other circles
    r_circles = float('inf')
    for j in range(len(radii)):
        if j != idx and radii[j] > 0:
            dist = np.linalg.norm(centers[idx] - centers[j])
            r_circles = min(r_circles, max(0, dist - radii[j]))

    return min(r_wall, r_circles)


>>>>>>> REPLACE

<<<<<<< SEARCH
def compute_max_radii(centers: np.ndarray) -> np.ndarray:
    """
    Given fixed circle centres, compute the largest radii such that:
      - every circle fits inside [0, 1]^2  (radius <= distance to nearest wall)
      - no two circles overlap             (r_i + r_j <= dist(c_i, c_j))

    Uses an iterative shrink-until-feasible approach with improved scaling.

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
    for iteration in range(10):
        for i in range(n):
            for j in range(i + 1, n):
                dist = np.linalg.norm(centers[i] - centers[j])
                if radii[i] + radii[j] > dist + 1e-9:
                    # Proportional shrinking favors smaller circles
                    total = radii[i] + radii[j]
                    scale = (dist - 1e-9) / total
                    radii[i] *= scale
                    radii[j] *= scale

    radii = np.maximum(radii, 0.0)
    return radii
=======
def compute_max_radii(centers: np.ndarray) -> np.ndarray:
    """
    Computes radii by solving a small linear program-like expansion.
    We want to maximize sum(r_i) subject to r_i + r_j <= d_ij and r_i <= wall_dist.
    """
    n = centers.shape[0]

    def obj(r):
        return -np.sum(r)

    wall_dists = np.array([min(c[0], c[1], 1-c[0], 1-c[1]) for c in centers])

    def cons_overlap(r):
        res = []
        for i in range(n):
            for j in range(i + 1, n):
                d = np.linalg.norm(centers[i] - centers[j])
                res.append(d - r[i] - r[j])
        return np.array(res)

    res = minimize(obj, wall_dists * 0.5, method='SLSQP',
                   bounds=[(0, 0.5)] * n,
                   constraints={'type': 'ineq', 'fun': cons_overlap},
                   options={'maxiter': 100})

    # Final safety check and clipping
    radii = np.clip(res.x, 0, wall_dists)
    for i in range(n):
        for j in range(i + 1, n):
            d = np.linalg.norm(centers[i] - centers[j])
            if radii[i] + radii[j] > d:
                shrink = d / (radii[i] + radii[j])
                radii[i] *= shrink
                radii[j] *= shrink
    return radii


def compute_max_radii(centers: np.ndarray) -> np.ndarray:
    """
    Given fixed circle centres, compute the largest radii such that:
      - every circle fits inside [0, 1]^2  (radius <= distance to nearest wall)
      - no two circles overlap             (r_i + r_j <= dist(c_i, c_j))

    Uses an iterative shrink-until-feasible approach with improved scaling.

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
    for iteration in range(10):
        for i in range(n):
            for j in range(i + 1, n):
                dist = np.linalg.norm(centers[i] - centers[j])
                if radii[i] + radii[j] > dist + 1e-9:
                    # Proportional shrinking favors smaller circles
                    total = radii[i] + radii[j]
                    scale = (dist - 1e-9) / total
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