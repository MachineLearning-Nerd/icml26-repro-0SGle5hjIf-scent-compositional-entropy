# Claim 2 source audit

Theorem 3.6 concerns the expected CERM objective gap of the averaged primal
iterate under Assumption 3.2. It requires convex differentiable risks, a compact
bounded-risk domain, bounded expected squared gradients,
`eta_t = eta * alpha_t`, and the horizon-dependent constant
`alpha_t = alpha/sqrt(T)` satisfying the stated dual-step inequality.

The paper's `O(T^-1/4)` sentence describes the existing *analysis* of SCGD from
Wang et al. (2017); it is not an empirical lower bound saying every SCGD run
must exhibit that slope. This contract tests SCENT's theorem and does not
replace that literature statement with an unfair empirical race.

