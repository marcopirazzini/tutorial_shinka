# EVOLVE-BLOCK-START
import numpy as np


def construct_packing():
    """
    Construct an arrangement of 26 non-overlapping circles inside [0,1]^2
    that attempts to maximise the sum of their radii using multiple stochastic
    samplings plus local refinement.
    """
    best_score = -np.inf
    best_centers = None
    best_radii = None
    for extra_seed in range(2):
        centers, radii = _search_with_seed(157 + 61 * extra_seed)
        score = float(np.sum(radii))
        if score > best_score:
            best_score = score
            best_centers = centers
            best_radii = radii
    return best_centers, best_radii


def _search_with_seed(seed: int):
    rng = np.random.default_rng(seed)
    n = 26
    centers = _structured_seed(rng)
    radii = compute_max_radii(centers)
    best_centers = centers.copy()
    best_radii = radii.copy()
    best_score = float(np.sum(best_radii))
    current_centers = centers.copy()
    current_score = best_score

    iterations = 900
    for step in range(iterations):
        temp = 0.08 * (1 - step / iterations) + 0.008
        magnitude = 0.04 * (1 - step / iterations) + 0.006
        candidate = current_centers.copy()
        for _ in range(rng.integers(1, 4)):
            idx = rng.integers(n)
            direction = rng.normal(size=2)
            norm = np.linalg.norm(direction) + 1e-12
            direction /= norm
            candidate[idx] += direction * rng.uniform(0, magnitude)
        if rng.random() < 0.04:
            candidate += rng.normal(scale=0.003, size=candidate.shape)
        candidate = np.clip(candidate, 0.02, 0.98)
        candidate_radii = compute_max_radii(candidate)
        candidate_score = float(np.sum(candidate_radii))
        delta = candidate_score - current_score
        if delta > 1e-9 or rng.random() < np.exp(delta / (temp + 1e-8)):
            current_centers = candidate
            current_score = candidate_score
        if candidate_score > best_score + 1e-12:
            best_score = candidate_score
            best_centers = candidate
            best_radii = candidate_radii

    best_centers, best_radii = _coordinate_refinement(best_centers, best_radii)
    return best_centers, best_radii


def _structured_seed(rng: np.random.Generator) -> np.ndarray:
    xs = np.linspace(0.1, 0.9, 5)
    ys = np.linspace(0.1, 0.9, 5)
    grid = np.array([[x, y] for x in xs for y in ys], dtype=float)
    extra = np.array([[0.5, 0.95]], dtype=float)
    centers = np.vstack((grid, extra))
    jitter = rng.normal(scale=0.012, size=centers.shape)
    centers = np.clip(centers + jitter, 0.03, 0.97)
    return centers


def compute_max_radii(centers: np.ndarray) -> np.ndarray:
    n = centers.shape[0]
    wall_dist = np.minimum.reduce([
        centers[:, 0],
        1.0 - centers[:, 0],
        centers[:, 1],
        1.0 - centers[:, 1]
    ])
    radii = wall_dist.copy()
    if n <= 1:
        return np.maximum(radii, 0.0)
    for _ in range(30):
        diffs = centers[:, None, :] - centers[None, :, :]
        dist_mat = np.hypot(diffs[..., 0], diffs[..., 1])
        new_radii = radii.copy()
        for i in range(n):
            row = dist_mat[i].copy()
            row[i] = np.inf
            limits = row - radii
            limits[i] = np.inf
            candidate_limit = np.min(np.maximum(0.0, limits))
            if not np.isfinite(candidate_limit):
                candidate_limit = wall_dist[i]
            if candidate_limit < new_radii[i]:
                new_radii[i] = candidate_limit
        new_radii = np.minimum(new_radii, wall_dist)
        if np.allclose(new_radii, radii, atol=1e-10):
            radii = new_radii
            break
        radii = new_radii
    return np.maximum(radii, 0.0)


def _coordinate_refinement(centers: np.ndarray, radii: np.ndarray):
    best_centers = centers.copy()
    best_radii = radii.copy()
    best_score = float(np.sum(best_radii))
    n = centers.shape[0]
    for step in (0.016, 0.008, 0.004):
        for _ in range(2):
            improved = False
            for idx in range(n):
                for axis in range(2):
                    for direction in (-1, 1):
                        candidate = best_centers.copy()
                        candidate[idx, axis] = np.clip(
                            candidate[idx, axis] + direction * step, 0.02, 0.98
                        )
                        candidate_radii = compute_max_radii(candidate)
                        candidate_score = float(np.sum(candidate_radii))
                        if candidate_score > best_score + 1e-12:
                            best_score = candidate_score
                            best_centers = candidate
                            best_radii = candidate_radii
                            improved = True
            if not improved:
                break
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
