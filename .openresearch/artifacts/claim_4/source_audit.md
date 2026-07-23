# Claim 4 source audit

The imported claim conflates multiple results. Theorem 4.3 is the fixed-`w`
SPMD upper bound, whose dominant term scales as
`sqrt((kappa-1)/T)` under bounded `s` and a specific feasible step size.
Projected SGD is analyzed later in Lemma 4.4 and Theorem 4.5. The following
remark compares the two *upper bounds* by a factor proportional to
`1/(|nu_0-nu_*| exp(nu_*-c0))`.

Figure 1 is a controlled Gaussian mechanism experiment. Appendix F.4 specifies
one million Gaussian samples per mean/variance combination, 3,000 plotted
iterations, SGD step 1, and SPMD log-step -6 for mean -1 and 3 for mean -10.
It does not specify initialization, projection, random seeds, or uncertainty.
This reproduction declares `nu_0=0`, projects SGD to a valid interval
containing both sampled risks and zero, and adds 64 stochastic trajectories.

