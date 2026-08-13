# Current status

## Scientific outcome

`MIXED_RESULTS`

| Claim | Status | Short interpretation |
|---|---|---|
| C1 | `VERIFIED_SCOPED` | Stable dual update agrees with proximal optimization and high-precision checks on the declared domain. |
| C2 | `VERIFIED_SCOPED` | A finite convex theorem contract exhibits the predicted rate and satisfies its assumptions. |
| C3 | `VERIFIED_CONDITIONAL` | The SPMD dual invariant holds under the paper’s bounded-risk and initialization premises. |
| C4 | `VERIFIED_SCOPED` | `kappa` and bound-factor identities reproduce; Figure 1 trajectory behavior is separately qualified. |
| C5 | `BLOCKED` | Exact Glint360K/TreeOfLife-10M feature assets are unavailable and the exact workload is not feasible on the authorized host. |
| C6 | `FALSIFIED_FOR_DECLARED_PROTOCOL` | CIFAR-10, `tau=0.05`, contradicts the declared “SCENT slightly better than SOX” training-loss comparison. |

## Evidence gate

`EVIDENCE_RELEASE_GATE = PASSED` because every claim has a terminal artifact,
scope/limitation record, and independent checker or inventory reduction.

`STRICT_PAPER_CLAIM_GATE = NOT_READY` because Claim 5 is blocked and Claim 6
is falsified for the declared reproduction protocol. The historical `5/12`
judge score is retained as provenance; this repository does not claim a new
judge score.

## Main deviations

- The old root verifier uses synthetic proxy checks and writes a historical
  `6/6` output. It is not evidence for the six paper claims.
- Claim 2 is finite empirical evidence for the theorem’s assumptions and rate,
  not a replacement for the mathematical proof.
- Claim 4 uses finite empirical Gaussian samples even though the theorem assumes
  bounded risks; the paper’s Figure 1 also uses Gaussian noise.
- Claim 5 is not downgraded to a synthetic or smaller benchmark.
- Claim 6 uses paper-text margin `0.5`; the released example command omits the
  flag and therefore uses the code default `1.0`. This discrepancy is recorded.
- The authors do not publish the exact paper checkpoints, seeds, or raw Figure 3
  values, so C6 tests a declared reproducible protocol rather than hidden
  training state.

## Reproduction

```bash
uv sync --frozen
uv run --frozen python repro/src/verify_scent.py
```

Claim-specific evidence is authoritative under
`.openresearch/artifacts/claim_1/` through `.openresearch/artifacts/claim_6/`.
