# Claim 2: O(1/sqrt(T)) convergence (Theorem 3.6)


---
<!-- trackio-cell
{"type": "markdown", "id": "cell_0012_a69f38bf", "created_at": "2026-07-31T00:00:00+00:00", "title": "Claim and source audit"}
-->
**Paper claim.** Theorem 3.6 proves SCENT achieves an O(1/sqrt(T)) convergence rate for convex compositional entropic risk minimization objectives of the form log(E[exp(s(w;zeta))]), improving on SCGD's O(1/T^{1/4}) rate (Section 3, Theorem 3.6).

**Source anchor.** Theorem 3.6 and Assumption 3.2, Section 3.1 of
[arXiv:2602.02877](https://arxiv.org/abs/2602.02877) ([ar5iv](https://ar5iv.labs.arxiv.org/html/2602.02877), retrieved 2026-07-31). The
theorem bounds `E[F_CERM(w_bar_T) - F_CERM(w_*)]` by
`||w_1-w_*||^2/(2 eta alpha sqrt(T)) + D_phi(nu_*,nu_0)/(alpha B sqrt(T)) + alpha V / sqrt(T)`
under `eta_t = eta alpha_t`, `alpha_t = alpha/sqrt(T)`, and Assumption 3.2
(s_i convex and differentiable; `s_i(w;zeta) in [c0,c1]`; bounded gradient
second moment).

**Verdict: VERIFIED.**

---
<!-- trackio-cell
{"type": "markdown", "id": "cell_0013_ec7f6d9b", "created_at": "2026-07-31T00:00:00+00:00", "title": "Claim contract"}
-->
### Claim contract

Theorem 3.6 is an **upper bound**, so "decreasing loss" is not a test of it.
The bound is `O(1/sqrt(T))` exactly when `gap * sqrt(T)` stays bounded as `T`
grows, so that is the predicate — with the log-log slope as a secondary check.

| # | Predicate | Rule |
| --- | --- | --- |
| C2.1 | The instance actually satisfies Assumption 3.2 | convexity, differentiability, `s_i in [c0,c1]` and bounded gradient second moment all checked and recorded |
| C2.2 | `w_*` is a true optimum of the convex CERM objective | projected KKT residual < 1e-9 |
| C2.3 | `gap * sqrt(T)` is **bounded** across a 64x horizon sweep | max/first ratio < 2 and the increments shrink |
| C2.4 | Log-log slope of gap vs `T` is consistent with -1/2 | bootstrap 95% CI inside [-0.6, -0.4] |
| C2.5 | Step-size conditions of the theorem hold at every horizon | `alpha_t < e^{-c1}` margin recorded |
| NC | A run violating the single-time-scale coupling is rejected | checker must exit nonzero |

---
<!-- trackio-cell
{"type": "markdown", "id": "cell_0014_5faa59d4", "created_at": "2026-07-31T00:00:00+00:00", "title": "Result"}
-->
### Result

Convex CERM instance: dimension **12**, **96** anchors,
inner support **256**, domain `[-1.0, 1.0]`, measured
`c0 = -1.184616`, `c1 = 1.153704`. Assumption 3.2 holds by
construction and was re-checked: convex/differentiable = **True**,
bounded gradient second moment = **True**.
Reference optimum solved to projected KKT residual
**1.6293e-12**.

**20 seeds at each of 4 horizons (80 runs):**

| T | seeds | mean_gap | ci95 | gap_sqrtT |
| --- | --- | --- | --- | --- |
| 512 | 20 | 0.086734 | [0.086542, 0.086926] | 1.962568 |
| 2048 | 20 | 0.049282 | [0.049218, 0.049345] | 2.230227 |
| 8192 | 20 | 0.025951 | [0.025906, 0.025996] | 2.348830 |
| 32768 | 20 | 0.013150 | [0.013137, 0.013163] | 2.380465 |

`gap * sqrt(T)` rises from **1.9626** to **2.3805** and then flattens — successive
increments **+0.2677, +0.1186, +0.0316** shrink by roughly a factor of 3 each
step, so the product is bounded (max/first ratio
**1.2129**), which is what `O(1/sqrt(T))` asserts.

Log-log slope **-0.4545**, bootstrap 95% CI
**[-0.4550, -0.4540]**.
Step condition held at every horizon (minimum margin **0.2934**).
Independent checker passed = **True**;
negative control rejected = **True**.

---
<!-- trackio-cell
{"type": "markdown", "id": "cell_0015_8559dfc0", "created_at": "2026-07-31T00:00:00+00:00", "title": "Raw data: 80 convergence runs"}
-->
### Raw data (first 20 of 80 runs)

| horizon | seed | objective | optimum | gap | alpha_t | eta_t | step_condition_margin_rho_1 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 512 | 90210 | -0.131532 | -0.218002 | 0.086470 | 0.022097 | 0.088388 | 0.293369 |
| 512 | 90211 | -0.131693 | -0.218002 | 0.086309 | 0.022097 | 0.088388 | 0.293369 |
| 512 | 90212 | -0.131651 | -0.218002 | 0.086352 | 0.022097 | 0.088388 | 0.293369 |
| 512 | 90213 | -0.131891 | -0.218002 | 0.086111 | 0.022097 | 0.088388 | 0.293369 |
| 512 | 90214 | -0.131356 | -0.218002 | 0.086646 | 0.022097 | 0.088388 | 0.293369 |
| 512 | 90215 | -0.131136 | -0.218002 | 0.086867 | 0.022097 | 0.088388 | 0.293369 |
| 512 | 90216 | -0.130896 | -0.218002 | 0.087106 | 0.022097 | 0.088388 | 0.293369 |
| 512 | 90217 | -0.130353 | -0.218002 | 0.087649 | 0.022097 | 0.088388 | 0.293369 |
| 512 | 90218 | -0.131100 | -0.218002 | 0.086902 | 0.022097 | 0.088388 | 0.293369 |
| 512 | 90219 | -0.131748 | -0.218002 | 0.086255 | 0.022097 | 0.088388 | 0.293369 |
| 512 | 90220 | -0.130643 | -0.218002 | 0.087360 | 0.022097 | 0.088388 | 0.293369 |
| 512 | 90221 | -0.131140 | -0.218002 | 0.086862 | 0.022097 | 0.088388 | 0.293369 |
| 512 | 90222 | -0.131226 | -0.218002 | 0.086776 | 0.022097 | 0.088388 | 0.293369 |
| 512 | 90223 | -0.131803 | -0.218002 | 0.086199 | 0.022097 | 0.088388 | 0.293369 |
| 512 | 90224 | -0.131501 | -0.218002 | 0.086501 | 0.022097 | 0.088388 | 0.293369 |
| 512 | 90225 | -0.131478 | -0.218002 | 0.086524 | 0.022097 | 0.088388 | 0.293369 |
| 512 | 90226 | -0.131125 | -0.218002 | 0.086877 | 0.022097 | 0.088388 | 0.293369 |
| 512 | 90227 | -0.131129 | -0.218002 | 0.086873 | 0.022097 | 0.088388 | 0.293369 |
| 512 | 90228 | -0.130694 | -0.218002 | 0.087308 | 0.022097 | 0.088388 | 0.293369 |
| 512 | 90229 | -0.131267 | -0.218002 | 0.086735 | 0.022097 | 0.088388 | 0.293369 |

Full table: [`evidence/claim_2/rate_runs.csv`](https://huggingface.co/spaces/DineshAI/0SGle5hjIf/blob/main/evidence/claim_2/rate_runs.csv) (80 rows).

---
<!-- trackio-cell
{"type": "markdown", "id": "cell_0016_dd35a816", "created_at": "2026-07-31T00:00:00+00:00", "title": "Provenance"}
-->
### Provenance

| Field | Value |
| --- | --- |
| Command | `uv run --frozen python repro/src/verify_rate_kappa.py` |
| Repo Git SHA | `9799451c4aa312bb27e8c246814620257072be98` |
| Seed | `260202877 (per-run seeds 90210+)` |
| Runtime | 27.9 s |
| Environment | Python 3.12.11, numpy 2.5.1, scipy 1.18.0, pinned by `uv.lock`; CPU only |
| Paper source | [ar5iv](https://ar5iv.labs.arxiv.org/html/2602.02877) retrieved 2026-07-31, SHA-256 `00670f81db728e76f35ebee5a56019ee…` |


---
<!-- trackio-cell
{"type": "markdown", "id": "cell_0017_15a30822", "created_at": "2026-07-31T00:00:00+00:00", "title": "Evidence files"}
-->
### Evidence files

| Artifact | Bytes | SHA-256 |
| --- | --- | --- |
| [`evidence/claim_2/claim_contract.json`](https://huggingface.co/spaces/DineshAI/0SGle5hjIf/blob/main/evidence/claim_2/claim_contract.json) | 924 | `f756f966df02f15529597021fbf5b811…` |
| [`evidence/claim_2/source_audit.md`](https://huggingface.co/spaces/DineshAI/0SGle5hjIf/blob/main/evidence/claim_2/source_audit.md) | 666 | `5e3e71f05ee9b0ec0d36b41137decba3…` |
| [`evidence/claim_2/method.md`](https://huggingface.co/spaces/DineshAI/0SGle5hjIf/blob/main/evidence/claim_2/method.md) | 793 | `b67dba25f48bff336f3a2de4b193e20f…` |
| [`evidence/claim_2/rate_runs.csv`](https://huggingface.co/spaces/DineshAI/0SGle5hjIf/blob/main/evidence/claim_2/rate_runs.csv) | 10864 | `f65e65d0ecffe0991910bf73bf993adc…` |
| [`evidence/claim_2/raw_summary.json`](https://huggingface.co/spaces/DineshAI/0SGle5hjIf/blob/main/evidence/claim_2/raw_summary.json) | 1515 | `545265afa5d64de8a394c43dce4c28e5…` |
| [`evidence/claim_2/negative_control.json`](https://huggingface.co/spaces/DineshAI/0SGle5hjIf/blob/main/evidence/claim_2/negative_control.json) | 286 | `d1ef7adcba2bbd5e0a5a99cd0e83507a…` |
| [`evidence/claim_2/EVAL.md`](https://huggingface.co/spaces/DineshAI/0SGle5hjIf/blob/main/evidence/claim_2/EVAL.md) | 1633 | `cfa9aeffb3d92abb7beda33938c12736…` |
| [`evidence/claim_2/limitations.md`](https://huggingface.co/spaces/DineshAI/0SGle5hjIf/blob/main/evidence/claim_2/limitations.md) | 434 | `a0f7cbc2a5c4c7df024de0e652b8a44d…` |
| [`evidence/claim_2/environment.json`](https://huggingface.co/spaces/DineshAI/0SGle5hjIf/blob/main/evidence/claim_2/environment.json) | 417 | `8c11c275d3a3868a040d04ec5d913fd8…` |

Verifier: [`repro/src/verify_rate_kappa.py`](https://huggingface.co/spaces/DineshAI/0SGle5hjIf/blob/main/repro/src/verify_rate_kappa.py) · checker: [`repro/src/check_rate_kappa.py`](https://huggingface.co/spaces/DineshAI/0SGle5hjIf/blob/main/repro/src/check_rate_kappa.py) · [https://github.com/MachineLearning-Nerd/icml26-scent-compositional-entropy](https://github.com/MachineLearning-Nerd/icml26-scent-compositional-entropy)

---
<!-- trackio-cell
{"type": "markdown", "id": "cell_0018_57dde81b", "created_at": "2026-07-31T00:00:00+00:00", "title": "Limitations and deviations"}
-->
### Limitations and deviations

- The rate is verified on a **synthetic convex CERM instance that provably
  satisfies Assumption 3.2**. That is the theorem's exact domain — Theorem 3.6
  is stated for convex problems, so a deep network would be *outside* it — but
  it means this page tests the theorem, not the paper's benchmark results.
- The **comparison to SCGD's O(1/T^{1/4})** is a statement about the tightness of
  a *prior* analysis (Wang et al., 2017), not an empirically falsifiable
  property of SCGD. This page verifies SCENT's own rate and does not claim to
  have measured SCGD's analysis to be loose.
- 20 seeds per horizon; the 95% intervals above are the sampling uncertainty.
