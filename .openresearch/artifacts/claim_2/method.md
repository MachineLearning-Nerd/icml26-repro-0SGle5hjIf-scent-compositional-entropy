# Claim 2 method

A finite-support 96-anchor, 256-inner-state, 12-dimensional CERM problem is
constructed so every assumption can be checked exactly. Each risk is affine,
the domain is `[-1,1]^12`, and global `c0,c1` are computed by interval
arithmetic. The exact objective and gradient enumerate all 24,576 inner terms;
L-BFGS-B supplies the reference optimum and a projected KKT check.

SCENT uses independent samples for its dual and primal updates, stochastic
blocks of 32 anchors, the theorem's horizon-dependent constant step, and the
averaged iterate. Twenty deterministic seeds are run at each of four horizons.
Uncertainty is reported with t intervals and a 2,000-resample bootstrap of the
log-log rate. A separate script reduces the raw CSV without trusting the
verifier's summary.

