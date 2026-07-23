# Claim 1 method

1. Evaluate the paper's log-domain formula on 512 seeded moderate cases.
2. Independently minimize the exact proximal objective with Brent's method.
3. Evaluate 400 seeded stress cases spanning values from -10,000 to 10,000 and
   compare to an 80-digit `mpmath` implementation.
4. Run a separate 90-digit checker from raw CSV data.
5. Require a naive `exp`-then-`log` implementation to become non-finite on the
   deliberate overflow control while the stable implementation remains finite.

The verifier exits nonzero if any required predicate fails.

