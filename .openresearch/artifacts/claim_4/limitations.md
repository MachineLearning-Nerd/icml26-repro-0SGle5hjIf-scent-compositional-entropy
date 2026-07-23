# Claim 4 limitations

Gaussian distributions are unbounded, whereas Theorem 4.3 assumes bounded
`s`; Figure 1 itself uses Gaussian noise. Each one-million-point empirical
distribution is finite and therefore bounded, but this is not a proof for an
unbounded population. The paper omits initialization, projection, seeds, and
uncertainty for Figure 1, so those choices are declared rather than guessed
silently. Most importantly, the “faster factor” compares theoretical upper
bounds and is not a universal pointwise guarantee that SPMD beats optimally
tuned SGD on every distribution and iteration.

The paper's separate qualitative statement that Figure 1's error ratio is
independent of the Gaussian mean is reported numerically, but it does not gate
the verdict for the imported theorem/factor claim. A mismatch on that
sensitivity is a divergence, not evidence for the bound claim.
