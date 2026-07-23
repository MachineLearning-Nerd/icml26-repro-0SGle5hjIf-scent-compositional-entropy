# Claim 4 limitations

Gaussian distributions are unbounded, whereas Theorem 4.3 assumes bounded
`s`; Figure 1 itself uses Gaussian noise. Each one-million-point empirical
distribution is finite and therefore bounded, but this is not a proof for an
unbounded population. The paper omits initialization, projection, seeds, and
uncertainty for Figure 1, so those choices are declared rather than guessed
silently. Most importantly, the “faster factor” compares theoretical upper
bounds and is not a universal pointwise guarantee that SPMD beats optimally
tuned SGD on every distribution and iteration.

