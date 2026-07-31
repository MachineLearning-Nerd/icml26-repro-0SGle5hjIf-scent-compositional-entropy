# Claims


---
<!-- trackio-cell
{"type": "markdown", "id": "cell_95578ed4b09d", "created_at": "2026-07-21T17:01:13+00:00", "title": "Claims to reproduce"}
-->
## Claims to reproduce

1. SCENT's stochastic proximal mirror descent update for the dual variable nu admits a closed-form expression, nu_t = nu_{t-1} + log(1+alpha_t e^{s(w_t;zeta_t)}) - log(1+alpha_t e^{nu_{t-1}}), avoiding the numerical instability of exponential-average baselines (Algorithm 1, Section 3).
2. Theorem 3.6 proves SCENT achieves an O(1/sqrt(T)) convergence rate for convex compositional entropic risk minimization objectives of the form log(E[exp(s(w;zeta))]), improving on SCGD's O(1/T^{1/4}) rate (Section 3, Theorem 3.6).
3. Lemma 3.3 proves the dual iterates nu_{i,t} remain bounded within an interval [c0, c1] across all iterations, preventing numerical overflow in the exponential terms (Section 3, Lemma 3.3).
4. Theorem 4.3 shows that for fixed w, SPMD's convergence is characterized by the second-order moment ratio kappa = E[z^2]/E[z]^2, and is provably faster than standard SGD by a factor proportional to 1/e^{(nu*-c0)} (Section 4, Theorem 4.3).
5. On extreme classification benchmarks Glint360K and TreeOfLife-10M, SCENT consistently outperforms the SOX, U-max, and BSGD baselines on both training and validation convergence (Section 5, extreme classification experiments).
6. On partial AUC maximization over CIFAR-10 and CIFAR-100, SCENT matches or exceeds the SOX baseline's performance (Section 5, partial AUC maximization experiments).
