# EVOLVE-BLOCK-START
import numpy as np
import scipy.linalg as sp

def construct_vectors(n:int=8):
    """
    Construct n vectors in n dimensions and organize them as columns of a n x n matrix.
    The goal is construct vectors that are hard for Komlos conjecture, i.e. the for all signs x in {-1,+1}^n, ||Ax||_\infty is as large as possible
    """
    vectors = np.random.standard_normal((n,n))
    return normalize(vectors)


# EVOLVE-BLOCK-END

import numpy as np
import scipy.linalg as sp
from itertools import product

def normalize(vectors):
    return vectors / sp.norm(vectors, axis=0)

def discrepancy(vectors):
    """
    Compute min_{x ∈ {-1,+1}^n} ||Ax||_∞ via brute force.
    Only feasible for small n (say n ≤ 20).
    """
    vectors = normalize(vectors)
    n = vectors.shape[1]
    min_val = np.inf
    best_x = None

    for signs in product([-1, 1], repeat=n):
        x = np.array(signs)
        val = np.abs(vectors @ x).max()
        if val < min_val:
            min_val = val
            best_x = x

    return min_val, best_x

def run_komlos(n: int = 8, random_seed: int | None = None):
    if random_seed is not None:
        np.random.seed(random_seed)
    vectors = construct_vectors(n)
    cost, signs = discrepancy(vectors)
    return vectors, cost, signs
