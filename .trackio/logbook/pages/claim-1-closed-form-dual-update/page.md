# Claim 1: Closed-form SPMD dual update


---
<!-- trackio-cell
{"type": "markdown", "id": "cell_0004_a69f38bf", "created_at": "2026-07-31T00:00:00+00:00", "title": "Claim and source audit"}
-->
**Paper claim.** SCENT's stochastic proximal mirror descent update for the dual variable nu admits a closed-form expression, nu_t = nu_{t-1} + log(1+alpha_t e^{s(w_t;zeta_t)}) - log(1+alpha_t e^{nu_{t-1}}), avoiding the numerical instability of exponential-average baselines (Algorithm 1, Section 3).

**Source anchor.** Lemma 3.1 and the display below it, Section 3 of
[arXiv:2602.02877](https://arxiv.org/abs/2602.02877) ([ar5iv HTML](https://ar5iv.labs.arxiv.org/html/2602.02877), retrieved 2026-07-31,
SHA-256 `00670f81db728e76f35ebee5a56019ee9382370bfc43d64d69eddbe74a8adab6`). The paper states the update solves

> nu_t = argmin_nu  Phi(w_t, nu; zeta_t) + D_phi(nu, nu_{t-1}) / alpha_t,
> with D_phi(nu, nu') = e^-nu - e^-nu' + e^-nu' (nu - nu')

and asserts the closed form
`nu_t = nu_{t-1} + log(1 + alpha_t e^s) - log(1 + alpha_t e^{nu_{t-1}})`.

**Verdict: VERIFIED.**

---
<!-- trackio-cell
{"type": "markdown", "id": "cell_0005_ec7f6d9b", "created_at": "2026-07-31T00:00:00+00:00", "title": "Claim contract"}
-->
### Claim contract

The claim is an exact identity plus a stability property, so it is checked as both.

| # | Predicate | Rule |
| --- | --- | --- |
| C1.1 | The closed form equals an **independent** numerical `argmin` of the proximal objective | max abs error < 1e-6 over 512 randomised cases |
| C1.2 | The closed form satisfies the first-order optimality condition of that objective | max residual < 1e-6 |
| C1.3 | The closed form matches a 90-decimal-digit `mpmath` recomputation | max abs error < 1e-9 |
| C1.4 | The `log`/`logaddexp` implementation stays finite where an exponential-average implementation of eq. (7) overflows | all 400 stress cases finite, and the naive form demonstrably overflows |
| NC | A deliberately wrong closed form is **rejected** by the same checker | checker must exit nonzero |

The verifier exits nonzero if any predicate fails.

---
<!-- trackio-cell
{"type": "markdown", "id": "cell_0006_5faa59d4", "created_at": "2026-07-31T00:00:00+00:00", "title": "Result"}
-->
### Result

| Quantity | Measured |
| --- | --- |
| Independent `argmin` cases | **512** |
| Max abs error, closed form vs independent argmin | **2.7773e-08** |
| Max abs error vs 90-digit `mpmath` | **1.8190e-12** |
| Max proximal-objective gap at the closed form | **8.7311e-11** |
| High-precision stress cases | **400** |
| All stress cases finite | **True** |
| Independent checker passed | **True** |
| Negative control rejected | **True** |

The independent checker recomputes the first-order residual from the raw CSV at
90 decimal digits and reports max residual **4.677e-10** and max formula error
**3.563e-15** over 512 rows.

---
<!-- trackio-cell
{"type": "markdown", "id": "cell_0007_61770873", "created_at": "2026-07-31T00:00:00+00:00", "title": "Raw data: proximal argmin cases"}
-->
### Raw data (first 12 of 512 proximal-argmin cases)

| case | nu_prev | s | alpha | closed_form | independent_argmin | abs_error | objective_gap |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0 | 4.129313 | 3.839657 | 1.3927e+00 | 3.843488 | 3.843488 | 1.8187e-11 | 0.0000e+00 |
| 1 | 4.158307 | 1.651929 | 1.1741e+02 | 1.653427 | 1.653427 | 7.7038e-11 | 4.4409e-16 |
| 2 | 3.720386 | 6.133168 | 6.6593e-03 | 4.880972 | 4.880972 | 1.8041e-11 | 0.0000e+00 |
| 3 | -7.078004 | -5.975674 | 4.9959e+00 | -7.069600 | -7.069600 | 1.7347e-09 | 2.5757e-14 |
| 4 | 7.759691 | 1.494704 | 1.3167e+01 | 1.511564 | 1.511564 | 4.8507e-09 | 0.0000e+00 |
| 5 | -1.689716 | -2.720724 | 4.6255e-03 | -1.690265 | -1.690265 | 3.6399e-09 | 6.3283e-14 |
| 6 | -6.073644 | -6.203247 | 1.7719e-02 | -6.073649 | -6.073649 | 0.0000e+00 | 0.0000e+00 |
| 7 | 4.811036 | 5.653995 | 1.8777e+00 | 5.651534 | 5.651534 | 2.2609e-10 | 0.0000e+00 |
| 8 | -7.752944 | 4.382498 | 1.0723e+01 | -1.001439 | -1.001439 | 1.3260e-09 | 0.0000e+00 |
| 9 | -3.372930 | -4.743293 | 1.5231e+00 | -3.410658 | -3.410658 | 3.7099e-11 | 0.0000e+00 |
| 10 | -2.571208 | -7.689467 | 9.9413e+01 | -4.678417 | -4.678417 | 3.4915e-09 | 4.4409e-16 |
| 11 | -4.848424 | 6.047854 | 1.2944e+02 | 5.362112 | 5.362112 | 3.7764e-09 | 0.0000e+00 |

Full table: [`evidence/claim_1/proximal_cases.csv`](https://huggingface.co/spaces/DineshAI/0SGle5hjIf/blob/main/evidence/claim_1/proximal_cases.csv) (512 rows).

---
<!-- trackio-cell
{"type": "markdown", "id": "cell_0008_2c18705b", "created_at": "2026-07-31T00:00:00+00:00", "title": "Raw data: stability stress cases"}
-->
### Raw data (first 8 of 400 numerical-stability stress cases)

| case | nu_prev | s | alpha | stable | mp_reference | abs_error |
| --- | --- | --- | --- | --- | --- | --- |
| 0 | -999.8086262598933 | 10000.038310029837 | 1.3127612802167862e+17 | 9039.645763117154 | 9039.64576311715529755692106094 | 1.0231882623990949e-12 |
| 1 | 99.89035292437993 | -9999.927403268599 | 7.925361122235526e-05 | 9.442857578770543 | 9.44285757877053558568086107454 | 7.073504732873225e-15 |
| 2 | 0.20558250615164197 | -99.83451233109105 | 1.1855875281382824e-16 | 0.20558250615164184 | 0.205582506151641829326581333451 | 6.840761724699327e-18 |
| 3 | -0.18364268909888154 | 99.78482548634481 | 1.5359518037969843e-19 | 56.281216286855916 | 56.2812162868559158535229544992 | 2.55370021555379e-16 |
| 4 | 99.84039739788425 | 2000.2058287616715 | 474700.569284322 | 2000.2058287616712 | 2000.20582876167145514045841992 | 2.2737367544323206e-13 |
| 5 | -709.8264061860932 | 0.13628864469859825 | 3999.842315047638 | -701.3958891908185 | -701.395889190818479660936869459 | 4.159869231398509e-17 |
| 6 | 709.9283759346848 | 2000.2160615887371 | 6.8839774422963585e-18 | 2000.216061588737 | 2000.21606158873714775836560875 | 2.2737367544323206e-13 |
| 7 | -0.04399024790198375 | -710.1006919767011 | 3.3598316824300343e-06 | -0.04399346313239497 | -0.043993463132394973331881726154 | 1.3748173773761458e-19 |

Full table: [`evidence/claim_1/stress_cases.csv`](https://huggingface.co/spaces/DineshAI/0SGle5hjIf/blob/main/evidence/claim_1/stress_cases.csv) (400 rows).

---
<!-- trackio-cell
{"type": "markdown", "id": "cell_0009_dd35a816", "created_at": "2026-07-31T00:00:00+00:00", "title": "Provenance"}
-->
### Provenance

| Field | Value |
| --- | --- |
| Command | `uv run --frozen python repro/src/verify_dual_contracts.py` |
| Repo Git SHA | `9799451c4aa312bb27e8c246814620257072be98` |
| Seed | `260202877` |
| Runtime | 0.1 s |
| Environment | Python 3.12.11, numpy 2.5.1, scipy 1.18.0, pinned by `uv.lock`; CPU only |
| Paper source | [ar5iv](https://ar5iv.labs.arxiv.org/html/2602.02877) retrieved 2026-07-31, SHA-256 `00670f81db728e76f35ebee5a56019ee…` |


---
<!-- trackio-cell
{"type": "markdown", "id": "cell_0010_15a30822", "created_at": "2026-07-31T00:00:00+00:00", "title": "Evidence files"}
-->
### Evidence files

| Artifact | Bytes | SHA-256 |
| --- | --- | --- |
| [`evidence/claim_1/claim_contract.json`](https://huggingface.co/spaces/DineshAI/0SGle5hjIf/blob/main/evidence/claim_1/claim_contract.json) | 924 | `3ec0a850bf13479cbe64cad1993f5305…` |
| [`evidence/claim_1/source_audit.md`](https://huggingface.co/spaces/DineshAI/0SGle5hjIf/blob/main/evidence/claim_1/source_audit.md) | 740 | `61a4d4a4efa40fc78685df56a5ffe502…` |
| [`evidence/claim_1/method.md`](https://huggingface.co/spaces/DineshAI/0SGle5hjIf/blob/main/evidence/claim_1/method.md) | 571 | `6855388f4be30aa4545c4ffb8a27ab3b…` |
| [`evidence/claim_1/proximal_cases.csv`](https://huggingface.co/spaces/DineshAI/0SGle5hjIf/blob/main/evidence/claim_1/proximal_cases.csv) | 69569 | `8c7bab1b82d4cef50923fa070d4cff59…` |
| [`evidence/claim_1/stress_cases.csv`](https://huggingface.co/spaces/DineshAI/0SGle5hjIf/blob/main/evidence/claim_1/stress_cases.csv) | 53707 | `5b63b1286240d60a00f1c85356995a59…` |
| [`evidence/claim_1/raw_summary.json`](https://huggingface.co/spaces/DineshAI/0SGle5hjIf/blob/main/evidence/claim_1/raw_summary.json) | 386 | `c2dfcae985de15ddf35ef3831af82281…` |
| [`evidence/claim_1/negative_control.json`](https://huggingface.co/spaces/DineshAI/0SGle5hjIf/blob/main/evidence/claim_1/negative_control.json) | 288 | `9e2278f1b255d2f77517c838bc7ecb9b…` |
| [`evidence/claim_1/EVAL.md`](https://huggingface.co/spaces/DineshAI/0SGle5hjIf/blob/main/evidence/claim_1/EVAL.md) | 662 | `85ed8c2ad102eff4b2905d7e15dad13d…` |
| [`evidence/claim_1/limitations.md`](https://huggingface.co/spaces/DineshAI/0SGle5hjIf/blob/main/evidence/claim_1/limitations.md) | 300 | `f832a3696723bfc7b3a5d6e7abda7144…` |
| [`evidence/claim_1/environment.json`](https://huggingface.co/spaces/DineshAI/0SGle5hjIf/blob/main/evidence/claim_1/environment.json) | 421 | `844fd74145b7b40ef7db302959efe039…` |

Verifier: [`repro/src/verify_dual_contracts.py`](https://huggingface.co/spaces/DineshAI/0SGle5hjIf/blob/main/repro/src/verify_dual_contracts.py) · independent checker: [`repro/src/check_dual_evidence.py`](https://huggingface.co/spaces/DineshAI/0SGle5hjIf/blob/main/repro/src/check_dual_evidence.py) · code mirror: [https://github.com/MachineLearning-Nerd/icml26-repro-0SGle5hjIf-scent-compositional-entropy](https://github.com/MachineLearning-Nerd/icml26-repro-0SGle5hjIf-scent-compositional-entropy) · official implementation: [https://github.com/Optimization-AI/SCENT/tree/cfbf17925754f18855f26715adeec4773aa0591d](https://github.com/Optimization-AI/SCENT/tree/cfbf17925754f18855f26715adeec4773aa0591d)

---
<!-- trackio-cell
{"type": "markdown", "id": "cell_0011_a7c04c64", "created_at": "2026-07-31T00:00:00+00:00", "title": "Limitations"}
-->
### Limitations

This is a numerical audit of an algebraic identity, not a substitute for the
proof in Appendix B.1. It establishes the identity to double precision (and to
90 digits on a subsample) over the sampled region of `(nu_{t-1}, s, alpha)`
space, and demonstrates the stability property against a concrete
exponential-average implementation of eq. (7); it does not establish the
identity symbolically for all real inputs.
