# ICML 2026 reproduction: SCENT compositional entropic risk

This repository audits the paper **A Geometry-Aware Efficient Algorithm for
Compositional Entropic Risk Minimization** by Xiyuan Wei, Linli Zhou, Bokun
Wang, Chih-Jen Lin, and Tianbao Yang.

- Paper: [arXiv:2602.02877v2](https://arxiv.org/abs/2602.02877)
- Paper HTML: [arXiv HTML](https://arxiv.org/html/2602.02877)
- OpenReview: [0SGle5hjIf](https://openreview.net/forum?id=0SGle5hjIf)
- Official implementation: [Optimization-AI/SCENT](https://github.com/Optimization-AI/SCENT)
- Final repository name: `MachineLearning-Nerd/icml26-scent-compositional-entropy`
- Previous repository name: `MachineLearning-Nerd/icml26-repro-0SGle5hjIf-scent-compositional-entropy`

## Result at a glance

The evidence result is **MIXED_RESULTS**. The claim-specific contracts are
machine-checked, independently reduced, and deliberately scoped:

| Paper claim | Evidence verdict | What that means |
|---|---|---|
| C1 — closed-form SPMD dual update | `VERIFIED_SCOPED` | The identity, proximal optimum, high-precision values, and declared finite stress grid agree. |
| C2 — convex `O(1/sqrt(T))` convergence | `VERIFIED_SCOPED` | A finite convex contract satisfies the theorem assumptions and rate predicates; this is not a new proof of the theorem. |
| C3 — dual boundedness | `VERIFIED_CONDITIONAL` | The Lemma 3.3 invariant holds under its bounded-risk and initialization assumptions. |
| C4 — `kappa`-dependent SPMD/SGD comparison | `VERIFIED_SCOPED` | The bound identities and declared Gaussian protocol pass; the empirical trajectory behavior is not a universal guarantee. |
| C5 — extreme-classification benchmark | `BLOCKED` | The exact two-dataset feature pipeline cannot be run faithfully with the available assets and authorized CPU resources. No proxy pass is reported. |
| C6 — SCENT slightly beats SOX on CIFAR | `FALSIFIED_FOR_DECLARED_PROTOCOL` | At CIFAR-10, `tau=0.05`, the paper-text protocol produces a paired training-objective interval above the predeclared equivalence margin. |

The evidence-release gate passes because every claim has a terminal contract
state and the required independent checkers/negative controls pass. That gate
must not be read as “all six paper claims are reproduced.” The overall
scientific result remains four scoped verifications, one blocked claim, and one
falsified literal comparison.

## What the paper does

The paper studies compositional entropic risk minimization (CERM), where each
loss has the form `log(E[exp(s(w; zeta))])`. It rewrites the objective as a
min–min problem over a primal model parameter `w` and dual variables `nu`.
SCENT uses stochastic proximal mirror descent (SPMD) for `nu`, with the
negative-exponential Bregman geometry, and stochastic gradient updates for
`w`.

The paper’s main contributions are:

1. A numerically stable closed-form dual update.
2. An `O(1/sqrt(T))` convergence analysis for convex CERM under stated
   assumptions.
3. A `kappa`-based comparison between SPMD and projected SGD for the fixed-`w`
   dual problem.
4. Experiments on extreme classification, partial AUC, contrastive learning,
   and KL-regularized distributionally robust optimization.

This repository focuses on the six judge-selected claims represented by the
claim artifacts under `.openresearch/artifacts/claim_1/` through
`.openresearch/artifacts/claim_6/`.

## Claim-to-evidence map

Each claim has a contract, source audit, method, limitations, raw evidence,
verdict, and independent reduction where applicable.

| Claim | Paper scope | Evidence producer | Independent checker | Decisive evidence and limitation |
|---|---|---|---|---|
| C1 | Lemma 3.1, equations (5)–(7), and the stable log-domain implementation | `repro/src/verify_dual_contracts.py::verify_claim_1` | `repro/src/check_dual_evidence.py` | 512 proximal argmins, 400 stress cases from `-10000` to `10000`, 90-digit recomputation, and rejected naive `exp`-then-`log` control. Finite declared stress coverage is not a universal hardware guarantee. |
| C2 | Theorem 3.6 under Assumption 3.2 | `repro/src/verify_rate_kappa.py::verify_claim_2` | `repro/src/check_rate_kappa.py` | Four horizons × 20 seeds; slope `-0.454487`; bootstrap 95% slope interval `[-0.454952, -0.454037]`; exact convex optimum with projected KKT residual `1.63e-12`. Finite scaling does not replace the theorem proof. |
| C3 | Lemma 3.3 under bounded-risk and in-range initialization assumptions | `repro/src/verify_dual_contracts.py::verify_claim_3` | `repro/src/check_dual_evidence.py` | 33,554,432 unprojected updates across four intervals, zero interval breaches, and rejected unprojected Euclidean-SGD control. The result is conditional on the lemma’s premises. |
| C4 | Theorems 4.3 and 4.5, their bound-comparison remark, and Figure 1 | `repro/src/verify_rate_kappa.py::verify_claim_4`; supplemental `repro/src/verify_claim4_theorem43.py` | `repro/src/check_rate_kappa.py` | One million Gaussian samples per setting, analytic `kappa` error ≤0.73%, bound-factor recomputation with zero relative error, six settings, and rejected legacy controls. The Gaussian population is unbounded and the observed trajectory ratio is not a universal pointwise guarantee. |
| C5 | Section 5.1 / Figure 2: Glint360K and TreeOfLife-10M extreme classification | `repro/src/verify_claim5_feasibility.py` | `repro/src/check_claim5_feasibility.py` | Exact asset inventory and negative control pass, but no paper-specific extracted features are published; the minimum protocol requires 15,974,898,600 example visits. No synthetic or reduced proxy is substituted. |
| C6 | Section 5.2 / Figure 3: CIFAR-10/100 training CERM objective | `repro/src/verify_claim6_pauc.py` using `repro/config/claim6_pauc.json` | `repro/src/check_claim6_pauc.py` | 24 terminal epoch-60 rows across two datasets, two `tau` values, two methods, and three seeds. CIFAR-10 `tau=0.05` has SCENT−SOX mean `+0.0270751`, bootstrap interval `[+0.0081645,+0.0407124]`, above the `+0.002` equivalence boundary. The result tests the declared protocol, not undisclosed paper checkpoints. |

The fixed orchestration command is:

```bash
uv run --frozen python repro/src/verify_scent.py
```

It also runs the rigorous child suites. The root `outputs/verdict.json` and
`outputs/verify_run.log` retain the original six-proxy judge-regression check;
they are historical compatibility outputs and are **not** the authoritative
paper-level verdict. Use the claim artifacts and `publication_gate.json` for
the current interpretation.

## Branch and experiment history

The original `orx/*` branches record the experiment tree: environment
freezing, exact dual contracts, rate and `kappa` calibration, Claim 5
feasibility, CIFAR acquisition/profiling, deterministic CIFAR-100 shards,
integration, and release publication. The complete legacy-to-final map is in
[`BRANCH_AUDIT.md`](BRANCH_AUDIT.md). The final branch vocabulary is:

- `main`: integrated publication surface and current evidence snapshot.
- `baseline/*`: frozen 5/12 judged baseline.
- `research/*`: theory contracts, rate calibration, full CIFAR protocol, and
  deterministic seed-shard experiments.
- `audit/*`: Claim 5 feasibility, CIFAR transport, and shard protocol audits.
- `release/*`: integrated verdict, release candidate, final gate, and Space
  publication records.

The repository has 21 final branches in total: `main` plus 20 named supporting
branches. Legacy `master` and `orx/*` names are retained only in the audit map
as historical names and are removed from the published remote during cleanup.

## Evidence layout

- `.openresearch/artifacts/claim_1/`–`claim_6/`: contracts, producers,
  checkers, raw CSV/JSON evidence, verdicts, and limitations.
- `.openresearch/audit/`: paper source metadata, stable claim anchors, judged
  baseline snapshot, and live judge record.
- `.openresearch/release/`: release audit, hashes, command record, and
  publication verification.
- `reports/scent-reproduction/report.md`: illustrated claim-by-claim report.
- `notebooks/scent_reproduction.py`: self-contained marimo tutorial that reads
  accepted evidence without rerunning the long CIFAR jobs.
- `GATE_READY.md`: concise publication/evidence status.
- `STATUS.md`: current status and limitations in one place.
- `SOURCE_MANIFEST.md`: paper, code, data, and environment provenance.
- `AUDIT_REPORT.md`: interpretation of every claim and known deviation.
- `outputs/README.md`: boundary between legacy proxy output and authoritative
  claim artifacts.

## Reproduce locally

The environment is pinned to Python 3.12 by `pyproject.toml`,
`.python-version`, and `uv.lock`.

```bash
uv sync --frozen
uv run --frozen python repro/src/verify_scent.py
```

The full CIFAR protocol can require external CPU/HF compute and is represented
by provenance-bound terminal artifacts in this checkout. Profile and shard
modes are not paper verdicts by themselves.

## Citation

```bibtex
@inproceedings{wei2026geometry,
  title     = {A Geometry-Aware Efficient Algorithm for Compositional Entropic Risk Minimization},
  author    = {Wei, Xiyuan and Zhou, Linli and Wang, Bokun and Lin, Chih-Jen and Yang, Tianbao},
  booktitle = {Proceedings of the 43rd International Conference on Machine Learning},
  year      = {2026},
  eprint    = {2602.02877},
  archivePrefix = {arXiv},
  primaryClass  = {cs.LG},
  doi       = {10.48550/arXiv.2602.02877}
}
```

## Thank you

Thank you to Xiyuan Wei, Linli Zhou, Bokun Wang, Chih-Jen Lin, and Tianbao
Yang for developing SCENT, releasing the official implementation, and
documenting the algorithm and experimental protocols. This repository is an
independent reproduction audit by `MachineLearning-Nerd`; it is not an
official release of the paper or its authors. The mixed outcomes and
limitations above are recorded so future work can revisit the blocked assets,
implementation discrepancies, and declared CIFAR protocol fairly.
