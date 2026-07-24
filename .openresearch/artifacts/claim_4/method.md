# Claim 4 method

For each of the paper's six Gaussian `(mu,sigma)` settings, draw one million
points, compute `z=exp(s)`, estimate `kappa=E[z^2]/E[z]^2`, and compare it with
the analytic log-normal value `exp(sigma^2)`. Run SPMD and projected SGD for
3,000 iterations on 64 stochastic trajectories using the steps reported in
Appendix F.4. Compare tail-averaged squared errors, uncertainty across
trajectories, dependence on kappa, and invariance to mean shifts.

The theorem/SGD-bound comparison factor is also recomputed from every bounded
empirical support. A separate checker reduces raw CSV evidence, independently
recomputes `1/(|nu0-nu*| exp(nu*-c0))`, and requires the factor to decrease as
`nu*-c0` grows. Negative controls repeat the old repository's raw-logit moment
error and omit the exponential term from the bound factor; both must be
rejected.
