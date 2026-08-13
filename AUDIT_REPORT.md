# Claim audit report

This report distinguishes what the paper says, what the repository computes,
and what the resulting evidence can support.

## Claim 1 — stable closed-form dual update

The source scope is Lemma 3.1 and equations (5)–(7), not the broader imported
phrase about an “exponential-average baseline.” The producer evaluates the
log-domain SPMD formula, independently minimizes the scalar proximal objective,
and compares 400 extreme cases with high-precision arithmetic. The checker
recomputes raw CSV rows at 90 digits and rejects a deliberately unstable
implementation. Result: `VERIFIED_SCOPED`.

## Claim 2 — convex convergence rate

The source scope is Theorem 3.6 under Assumption 3.2. The contract constructs a
finite convex CERM problem with bounded support and checks its exact reference
optimum, step inequality, four horizons, 20 seeds per horizon, bootstrap rate,
and a no-primal-update negative control. Result: `VERIFIED_SCOPED`. The result
supports the executable contract; it does not turn finite slope estimation into
a proof of the asymptotic theorem.

## Claim 3 — dual boundedness

Lemma 3.3 is conditional: risks must lie in `[c0,c1]` and `nu_0` must start in
that interval. The producer uses the unprojected SPMD update over four intervals
and 33,554,432 updates, then checks interval and one-step convex-hull breaches.
The high-precision checker and an unprojected Euclidean-SGD negative control
agree. Result: `VERIFIED_CONDITIONAL`.

## Claim 4 — `kappa` and SPMD versus SGD

The imported wording compresses Theorem 4.3, Theorem 4.5, the comparison
remark, and Figure 1. The audit separates them. Theorem 4.3 is the SPMD bound;
Theorem 4.5 supplies the projected-SGD comparison bound; the remark compares
those bounds by `1/(|nu_0-nu_*| exp(nu_*-c0))`. The six Gaussian settings match
the analytic `kappa` within 0.73%, the bound identity is independently
recomputed, and both legacy controls are rejected. Result: `VERIFIED_SCOPED`.

The paper’s qualitative Figure 1 trajectory behavior is not universalized.
The supplemental faithful audit records that the empirical SPMD/SGD error ratio
is not monotone in `sigma` beyond `sigma=1` at the tested horizons. That is a
reported deviation, not a failure of the separately scoped bound identities.

## Claim 5 — extreme classification

The exact claim requires Glint360K and TreeOfLife-10M, the paper’s extracted
features/backbones, four named methods, three seeds, and the full 50-epoch
protocol. The inventory found no official extracted feature files. Recreating
the features requires GPU inference over 9.5M–17.1M images; the minimum
float32 feature storage and 15,974,898,600 example visits exceed the authorized
CPU host. A different TreeOfLife corpus/backbone and a reduced shard are
explicitly rejected as proxies. Result: `BLOCKED`, not pass and not failure.

## Claim 6 — CIFAR comparison

The source claim is about epoch-60 training CERM surrogate loss in Figure 3:
SCENT is slightly better than SOX across CIFAR-10/CIFAR-100 and `tau` values
0.05/0.1. The integrated contract uses paper-text margin `0.5`, 60 epochs of
pretraining and 60 epochs of fine-tuning, the declared seeds, paired endpoint
differences, and a `0.002` equivalence boundary.

The 24 final rows are bound to one complete CIFAR-10 parent run and three
terminal CIFAR-100 seed shards. The independent checker accepts all rows and
rejects a truncated-row control. CIFAR-10 at `tau=0.05` has SCENT−SOX mean
`+0.0270751` with a bootstrap interval entirely above `+0.002`; this falsifies
the literal superiority/equivalence contract. The other primary settings are
equivalent, unresolved, or superior, so this is a targeted falsification, not a
claim that SCENT is uniformly worse. Secondary test pAUC results are mixed and
do not replace the paper’s training-loss claim.

## Legacy output boundary

`repro/src/verify_scent.py` still runs the original synthetic six-proxy block so
the old judge regression remains reproducible. Its `outputs/verdict.json` says
`6/6` because those checks only test finite synthetic behavior. The rigorous
child suites run afterward and write the authoritative claim artifacts. Future
readers should start with `publication_gate.json`, this report, and the six
claim directories.
