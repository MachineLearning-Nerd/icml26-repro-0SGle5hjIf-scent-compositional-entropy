"""Clean-room SCENT (Stochastic Compositional ENtropic risk minimization) from
"A Geometry-Aware Efficient Algorithm for Compositional Entropic Risk Minimization" (arXiv 2602.02877).
numpy, CPU. SCENT = SPMD on dual ν (φ=e^{-ν} mirror) + SGD on primal w.
c1: ν_t = ν_{t-1} + log(1 + α_t e^{s_t}) (closed-form dual update).
c2: O(1/√T) convergence for convex CERM f(w) = log(E[exp(g(w,ξ))]).
"""
from __future__ import annotations
import numpy as np


def logsumexp(z):
    m = z.max(); return m + np.log(np.sum(np.exp(z - m)))


def scent(X, T, eta, alpha, seed=0):
    """SCENT on f(w) = log(sum_i exp(w.x_i)). Returns (w, nu_history, gaps)."""
    rng = np.random.default_rng(seed); n, d = X.shape
    w = np.zeros(d); nu = np.zeros(n) + 0.1
    gaps = []
    for t in range(T):
        idx = rng.integers(n)
        s = X @ w                                    # all logits
        # c1: closed-form dual update (Bregman prox for phi=exp(-nu))
        nu_new = nu + np.log(1 + alpha * np.exp(s - nu))   # ν_t = ν_{t-1} + log(1 + α e^{s-ν_{t-1}})
        nu_new = np.clip(nu_new, 0, 50)              # c3: bounded (prevent overflow)
        # gradient estimator: z = sum_i exp(s_i - nu_i) * x_i  (the weighted gradient)
        weights = np.exp(s - nu_new)
        weights /= weights.sum() + 1e-12
        z = weights @ X                              # expected gradient under softmax
        w = w - eta / np.sqrt(t + 1) * z             # decreasing step (O(1/sqrt(T)))
        nu = nu_new
        gaps.append(float(logsumexp(X @ w)))
    return w, nu, gaps


def plain_sgd(X, T, eta, seed=0):
    """Vanilla SGD on f(w) = log(sum exp(w.x_i)) (baseline, no dual)."""
    rng = np.random.default_rng(seed); n, d = X.shape
    w = np.zeros(d); gaps = []
    for t in range(T):
        idx = rng.integers(n)
        s = X @ w
        p = np.exp(s); p /= p.sum()
        grad = p @ X                                  # full softmax gradient
        w = w - eta / np.sqrt(t + 1) * grad
        gaps.append(float(logsumexp(X @ w)))
    return w, gaps
