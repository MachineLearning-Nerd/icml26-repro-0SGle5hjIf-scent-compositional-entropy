# Reproduction: SCENT compositional entropic risk minimization

[![Open in molab](https://marimo.io/molab-shield.svg)](https://molab.marimo.io/github/MachineLearning-Nerd/icml26-repro-0SGle5hjIf-scent-compositional-entropy/blob/master/notebooks/scent_reproduction.py)

This CPU-only campaign audits all six judge-selected claims from
*A Geometry-Aware Efficient Algorithm for Compositional Entropic Risk
Minimization* ([arXiv 2602.02877](https://arxiv.org/abs/2602.02877),
[OpenReview 0SGle5hjIf](https://openreview.net/forum?id=0SGle5hjIf)).

The terminal evidence verdicts are **Claims 1–4 VERIFIED, Claim 5 BLOCKED, and
Claim 6 FALSIFIED**. The central CIFAR claim reports SCENT slightly better than
SOX in every setting; Figure 3 extraction gives SCENT−SOX differences between
−0.001284 and −0.000145. We observed +0.027075 on CIFAR-10 at τ=.05, with a
bootstrap 95% interval [0.008164, 0.040712] wholly beyond the predeclared +0.002
equivalence boundary.

The CIFAR protocol uses the paper's full 60-epoch pretraining and 60-epoch
fine-tuning, both datasets, both τ values, and three seeds on Hugging Face
`cpu-upgrade` (8 vCPU, 32 GB, no GPU). Claim 5 was not replaced by a toy:
the required Glint360K/TreeOfLife feature assets were unavailable and exceeded
the local disk budget, so it remains BLOCKED.

Read the [illustrated report](reports/scent-reproduction/report.md) or open the
[self-contained marimo tutorial](notebooks/scent_reproduction.py). The candidate
is published at HF revision `7fcacca041de1f1d591846177267ffb679c0dea7` and is
**awaiting judge**. The latest judge record remains **5/12** at revision
`71993d9a3c56ee16bd8935f11d635988eb494f5b`; no score increase is claimed before
a new live verdict.

## Experiment log

Every formal node uses exactly `uv run --frozen python repro/src/verify_scent.py`.

| Branch / experiment | Purpose or change | Exact run command | Assessment / outcome | Compute |
|---|---|---|---|---|
| `master` | Publication surface | Not run as an experiment (publication surface) | Validated starting SHA `b3a5d897…` | — |
| [`orx/exact-dual-contracts-c1-c3`](https://github.com/MachineLearning-Nerd/icml26-repro-0SGle5hjIf-scent-compositional-entropy/tree/orx/exact-dual-contracts-c1-c3) | Closed form and invariant interval | `uv run --frozen python repro/src/verify_scent.py` | Claims 1 and 3 VERIFIED | local CPU |
| [`orx/asymptotic-rate-calibrated-step`](https://github.com/MachineLearning-Nerd/icml26-repro-0SGle5hjIf-scent-compositional-entropy/tree/orx/asymptotic-rate-calibrated-step) | Theorem-rate and κ contracts | `uv run --frozen python repro/src/verify_scent.py` | Claims 2 and 4 VERIFIED | local CPU |
| [`orx/claim-5-full-scale-feasibility-contract`](https://github.com/MachineLearning-Nerd/icml26-repro-0SGle5hjIf-scent-compositional-entropy/tree/orx/claim-5-full-scale-feasibility-contract) | Exact asset and protocol inventory | `uv run --frozen python repro/src/verify_scent.py` | Claim 5 BLOCKED; no proxy pass | local + HF CPU |
| [`orx/claim-6-full-cifar-protocol`](https://github.com/MachineLearning-Nerd/icml26-repro-0SGle5hjIf-scent-compositional-entropy/tree/orx/claim-6-full-cifar-protocol) | Full CIFAR protocol; completed CIFAR-10 before timeout | `uv run --frozen python repro/src/verify_scent.py` | Partial run retained with pinned provenance | HF `cpu-upgrade` |
| [`seed 79`](https://github.com/MachineLearning-Nerd/icml26-repro-0SGle5hjIf-scent-compositional-entropy/tree/orx/claim-6-cifar-100-seed-79-shard) / [`2024`](https://github.com/MachineLearning-Nerd/icml26-repro-0SGle5hjIf-scent-compositional-entropy/tree/orx/claim-6-cifar-100-seed-2024-shard) / [`2602`](https://github.com/MachineLearning-Nerd/icml26-repro-0SGle5hjIf-scent-compositional-entropy/tree/orx/claim-6-cifar-100-seed-2602-shard) | Three deterministic CIFAR-100 seed shards | `uv run --frozen python repro/src/verify_scent.py` | All 3 terminal shards passed completeness and negative controls | HF `cpu-upgrade` |
| [`orx/claim-6-integrated-cifar-verdict`](https://github.com/MachineLearning-Nerd/icml26-repro-0SGle5hjIf-scent-compositional-entropy/tree/orx/claim-6-integrated-cifar-verdict) | Hash-pinned integration and cumulative regression | `uv run --frozen python repro/src/verify_scent.py` | Claim 6 FALSIFIED; Claims 1–5 regressed | local CPU |

## Run locally

```bash
uv sync --frozen
uv run --frozen python repro/src/verify_scent.py
```

Interactive tutorial:

```bash
uv run marimo edit notebooks/scent_reproduction.py
uv run marimo run notebooks/scent_reproduction.py
```
