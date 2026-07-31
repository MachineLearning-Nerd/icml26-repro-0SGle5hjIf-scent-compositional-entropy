# Claim 4: kappa characterises SPMD, and SPMD beats SGD (Theorem 4.3)


---
<!-- trackio-cell
{"type": "markdown", "id": "cell_0026_a69f38bf", "created_at": "2026-07-31T00:00:00+00:00", "title": "Claim and source audit"}
-->
**Paper claim.** Theorem 4.3 shows that for fixed w, SPMD's convergence is characterized by the second-order moment ratio kappa = E[z^2]/E[z]^2, and is provably faster than standard SGD by a factor proportional to 1/e^{(nu*-c0)} (Section 4, Theorem 4.3).

**Source anchor.** Section 4.2-4.3 of [arXiv:2602.02877](https://arxiv.org/abs/2602.02877)
([ar5iv](https://ar5iv.labs.arxiv.org/html/2602.02877), retrieved 2026-07-31): Assumption 4.1, **Theorem 4.3**,
Lemma 4.4, **Theorem 4.5** and the remark that follows it. Setting is the
fixed-`w` problem `min_nu F(nu) = E[z] e^{-nu} + nu`, `z = e^{s(zeta)}`,
queried only through the oracle `Phi(nu;zeta) = z e^{-nu} + nu`, with
`kappa = E[z^2]/(E[z])^2` and `s(zeta) in [c0,c1]`.

**Verdict: VERIFIED**, with one documented deviation from the Figure 1 remark.

---
<!-- trackio-cell
{"type": "markdown", "id": "cell_0027_ec7f6d9b", "created_at": "2026-07-31T00:00:00+00:00", "title": "Claim contract"}
-->
### Claim contract

The previous revision of this reproduction tuned the SPMD step size by hand
(`alpha = e^-6` for `mu=-1`, `e^3` for `mu=-10`). That tests a different
algorithm from the one Theorem 4.3 describes, and it is why the earlier run
reported a spurious 93% failure of `mu`-invariance. **This run uses only the
step sizes the theorems prescribe:**

- Theorem 4.3: `alpha_t = sqrt( D_phi(nu_*,nu_0) m / (2 C T Var(z)) )`, subject
  to `alpha_t <= min( m/(4 C Var(z)), rho e^{-nu_{t-1}} )`, `C = (1+rho)(1+c1-c0)`.
- Theorem 4.5: `alpha' = |nu_0-nu_*| e^{c0} / sqrt(2 T Var(z))`, subject to
  `alpha' <= 1/L = e^{c0}/m`.

`s` is drawn from a **truncated** normal on `[mu-6sigma, mu+6sigma]` so
Assumption 3.2(ii) holds exactly, which also makes `m`, `E[z^2]`, `Var(z)`,
`kappa` and `nu_* = log m` available in **closed form** — every bound is
evaluated against exact constants, never sampling estimates. The theorem holds
"for sufficiently large T", so the minimum admissible horizon is *solved for*
per `sigma` rather than assumed.

| # | Predicate | Rule |
| --- | --- | --- |
| C4.1 | Theorem 4.3 bound (15) holds | measured average gap <= RHS in **every** cell |
| C4.2 | The bound is **not vacuous** | worst RHS/measured ratio < 10 |
| C4.3 | Theorem 4.5 bound holds for projected SGD | measured <= RHS in every cell |
| C4.4 | `kappa` characterises SPMD convergence | Spearman(`sqrt(kappa-1)`, `gap*sqrt(T)`) > 0.9 |
| C4.5 | Rate in `T` at fixed `kappa` is `1/sqrt(T)` | log-log slope in [-0.6,-0.4] |
| C4.6 | Speedup factor identity: `B_spmd/B_sgd = [4 sqrt(C(1-r0+r0 log r0))/|nu_0-nu_*|] e^{-(nu_*-c0)}` | max relative error < 1e-9 |
| C4.7 | That factor is `mu`-invariant (paper Figure 1) | relative spread < 1% within a horizon |
| C4.8 | SPMD empirically beats SGD wherever the bound ratio < 1 | holds in every such cell |
| NC1 | Replacing the Bregman geometry by a plain **Euclidean** step breaks bound (15) | must be violated |
| NC2 | Understating `kappa` (using a `sigma=0.25` `kappa` for a `sigma=2` run) breaks bound (15) | must be violated |

---
<!-- trackio-cell
{"type": "markdown", "id": "cell_0028_5faa59d4", "created_at": "2026-07-31T00:00:00+00:00", "title": "Result"}
-->
### Result

**47 cells** (`mu` in {-10,-5,-1,0,1,5,10} x `sigma` in
{0.25,0.5,1.0,1.5,2.0} plus a horizon sweep), **256
independent trajectories each**. Minimum admissible horizon solved per sigma:
`{'0.25': 1000, '0.5': 1000, '1.0': 1000, '1.5': 6561, '2.0': 43002}`.

| Predicate | Measured | Pass |
| --- | --- | --- |
| C4.1 Theorem 4.3 bound holds, all cells | `True` | yes |
| C4.2 Worst bound/measured slack | **7.039x** | yes (<10) |
| C4.3 Theorem 4.5 bound holds, all cells | `True` | yes |
| C4.4 Spearman(sqrt(kappa-1), gap*sqrt(T)) | **0.9608** | yes (>0.9) |
| C4.5 log-log slopes by sigma | `{'0.25': -0.4954425513567997, '0.5': -0.49607364508977103, '1.0': -0.5255539726893277}` | yes |
| C4.6 Bound-ratio identity max rel. error | **4.1366e-16** | yes |
| C4.7 mu-invariance of the factor | max spread **3.86e-16** | yes |
| C4.8 SPMD wins where predicted | `True` | yes |
| NC1 Euclidean geometry rejected | gap **8.9034** > bound **3.9003** | rejected |
| NC2 Understated kappa rejected | gap **0.9919** > bound **0.1374** | rejected |

`kappa` matches the paper's Gaussian remark `kappa = e^{sigma^2}` to
**2.27%** (the residual is the
6-sigma truncation needed to satisfy Assumption 3.2(ii)).

**C4.2 matters.** An upper bound that exceeds the measured quantity by orders of
magnitude is satisfied by almost anything. Here the worst case is
**7.04x**, so bound (15) is genuinely
binding, and NC1/NC2 show two distinct ways to violate it.

---
<!-- trackio-cell
{"type": "markdown", "id": "cell_0029_014db990", "created_at": "2026-07-31T00:00:00+00:00", "title": "Figure 1: mu-invariance"}
-->
### Paper Figure 1: SPMD/SGD error ratio is mu-invariant

The paper's Figure 1 asserts the SPMD-to-SGD error ratio "decreases as sigma
increases and is independent of mu". The `mu`-independence reproduces sharply:

| sigma | min_ratio | max_ratio | relative_spread |
| --- | --- | --- | --- |
| 0.25 | 0.540399 | 0.542417 | 3.7203e-03 |
| 0.5 | 0.096012 | 0.096228 | 2.2429e-03 |
| 1.0 | 0.011179 | 0.011212 | 2.8624e-03 |
| 1.5 | 0.021521 | 0.021569 | 2.2249e-03 |
| 2.0 | 0.034744 | 0.034830 | 2.4542e-03 |

Across `mu` spanning **-10 to +10** — a factor of `e^20` in `m = E[z]` — the
empirical ratio moves by at most **0.37%**.

Mean empirical ratio by sigma: `{'0.25': 0.541216228201941, '0.5': 0.09614865554078647, '1.0': 0.011193449105320703, '1.5': 0.021549430470581894, '2.0': 0.03477896072818084}`.

---
<!-- trackio-cell
{"type": "markdown", "id": "cell_0030_bc8a2e77", "created_at": "2026-07-31T00:00:00+00:00", "title": "Raw data: Figure 1 grid"}
-->
### Raw data: Figure 1 grid (first 16 of 35 cells)

| mu | sigma | T | kappa | nu_star | c0 | alpha_spmd | alpha_sgd | spmd_avg_gap | spmd_bound | sgd_avg_gap | sgd_bound | empirical_ratio |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| -10.0 | 0.25 | 16000 | 1.0645 | -9.9688 | -11.5000 | 1.0916e+02 | 6.9919e-03 | 3.0729e-03 | 2.1149e-02 | 5.6730e-03 | 1.9283e-02 | 5.4167e-01 |
| -10.0 | 0.5 | 16000 | 1.2840 | -9.8750 | -13.0000 | 4.8170e+01 | 1.3250e-03 | 1.2154e-02 | 7.8951e-02 | 1.2635e-01 | 3.8989e-01 | 9.6191e-02 |
| -10.0 | 1.0 | 16000 | 2.7182 | -9.5000 | -16.0000 | 1.1024e+01 | 3.5264e-05 | 4.7366e-02 | 2.9519e-01 | 4.2248e+00 | 5.3613e+01 | 1.1212e-02 |
| -10.0 | 1.5 | 16000 | 9.4750 | -8.8750 | -19.0000 | 1.9370e+00 | 6.0587e-07 | 1.4810e-01 | 9.2028e-01 | 6.8705e+00 | 6.3974e+03 | 2.1556e-02 |
| -10.0 | 2.0 | 43002 | 53.3594 | -8.0000 | -22.0000 | 1.4160e-01 | 3.9186e-09 | 3.1270e-01 | 1.9576e+00 | 9.0000e+00 | 5.9344e+05 | 3.4744e-02 |
| -5.0 | 0.25 | 16000 | 1.0645 | -4.9688 | -6.5000 | 7.3551e-01 | 6.9919e-03 | 3.0659e-03 | 2.1149e-02 | 5.6734e-03 | 1.9283e-02 | 5.4040e-01 |
| -5.0 | 0.5 | 16000 | 1.2840 | -4.8750 | -8.0000 | 3.2456e-01 | 1.3250e-03 | 1.2128e-02 | 7.8951e-02 | 1.2631e-01 | 3.8989e-01 | 9.6012e-02 |
| -5.0 | 1.0 | 16000 | 2.7182 | -4.5000 | -11.0000 | 7.4282e-02 | 3.5264e-05 | 4.7293e-02 | 2.9519e-01 | 4.2248e+00 | 5.3613e+01 | 1.1194e-02 |
| -5.0 | 1.5 | 16000 | 9.4750 | -3.8750 | -14.0000 | 1.3051e-02 | 6.0587e-07 | 1.4819e-01 | 9.2028e-01 | 6.8705e+00 | 6.3974e+03 | 2.1569e-02 |
| -5.0 | 2.0 | 43002 | 53.3594 | -3.0000 | -17.0000 | 9.5407e-04 | 3.9186e-09 | 3.1289e-01 | 1.9576e+00 | 9.0000e+00 | 5.9344e+05 | 3.4765e-02 |
| -1.0 | 0.25 | 16000 | 1.0645 | -0.9688 | -2.5000 | 1.3471e-02 | 6.9919e-03 | 3.0702e-03 | 2.1149e-02 | 5.6738e-03 | 1.9283e-02 | 5.4112e-01 |
| -1.0 | 0.5 | 16000 | 1.2840 | -0.8750 | -4.0000 | 5.9446e-03 | 1.3250e-03 | 1.2136e-02 | 7.8951e-02 | 1.2631e-01 | 3.8989e-01 | 9.6078e-02 |
| -1.0 | 1.0 | 16000 | 2.7182 | -0.5000 | -7.0000 | 1.3605e-03 | 3.5264e-05 | 4.7277e-02 | 2.9519e-01 | 4.2248e+00 | 5.3613e+01 | 1.1191e-02 |
| -1.0 | 1.5 | 16000 | 9.4750 | 0.1250 | -10.0000 | 2.3904e-04 | 6.0587e-07 | 1.4801e-01 | 9.2028e-01 | 6.8705e+00 | 6.3974e+03 | 2.1543e-02 |
| -1.0 | 2.0 | 43002 | 53.3594 | 1.0000 | -13.0000 | 1.7474e-05 | 3.9186e-09 | 3.1347e-01 | 1.9576e+00 | 9.0000e+00 | 5.9344e+05 | 3.4830e-02 |
| 0.0 | 0.25 | 16000 | 1.0645 | 0.0312 | -1.5000 | 4.9559e-03 | 6.9919e-03 | 3.0753e-03 | 2.1149e-02 | 5.6697e-03 | 1.9283e-02 | 5.4242e-01 |

Full tables: [`theorem43_figure1.csv`](https://huggingface.co/spaces/DineshAI/0SGle5hjIf/blob/main/evidence/claim_4/theorem43_figure1.csv) (35 rows), [`theorem43_scaling.csv`](https://huggingface.co/spaces/DineshAI/0SGle5hjIf/blob/main/evidence/claim_4/theorem43_scaling.csv) (12 rows).

---
<!-- trackio-cell
{"type": "markdown", "id": "cell_0031_022043ba", "created_at": "2026-07-31T00:00:00+00:00", "title": "Raw data: horizon sweep"}
-->
### Raw data: horizon sweep (rate in T)

| mu | sigma | T | kappa | spmd_avg_gap | spmd_bound | sgd_avg_gap | empirical_ratio |
| --- | --- | --- | --- | --- | --- | --- | --- |
| -1.0 | 0.25 | 1000 | 1.0645 | 1.2092e-02 | 8.5120e-02 | 2.2271e-02 | 5.4296e-01 |
| -1.0 | 0.25 | 4000 | 1.0645 | 6.0926e-03 | 4.2385e-02 | 1.1286e-02 | 5.3984e-01 |
| -1.0 | 0.25 | 16000 | 1.0645 | 3.0758e-03 | 2.1149e-02 | 5.6693e-03 | 5.4254e-01 |
| -1.0 | 0.25 | 64000 | 1.0645 | 1.5387e-03 | 1.0564e-02 | 2.8456e-03 | 5.4075e-01 |
| -1.0 | 0.5 | 1000 | 1.2840 | 4.7956e-02 | 3.1725e-01 | 5.0390e-01 | 9.5169e-02 |
| -1.0 | 0.5 | 4000 | 1.2840 | 2.4163e-02 | 1.5814e-01 | 2.5253e-01 | 9.5685e-02 |
| -1.0 | 0.5 | 16000 | 1.2840 | 1.2143e-02 | 7.8951e-02 | 1.2634e-01 | 9.6108e-02 |
| -1.0 | 0.5 | 64000 | 1.2840 | 6.0940e-03 | 3.9445e-02 | 6.3186e-02 | 9.6446e-02 |
| -1.0 | 1.0 | 1000 | 2.7182 | 2.1353e-01 | 1.3535e+00 | 4.4341e+00 | 4.8156e-02 |
| -1.0 | 1.0 | 4000 | 2.7182 | 9.4168e-02 | 5.9095e-01 | 4.3643e+00 | 2.1577e-02 |
| -1.0 | 1.0 | 16000 | 2.7182 | 4.7313e-02 | 2.9519e-01 | 4.2248e+00 | 1.1199e-02 |
| -1.0 | 1.0 | 64000 | 2.7182 | 2.3680e-02 | 1.4753e-01 | 3.9468e+00 | 5.9997e-03 |

---
<!-- trackio-cell
{"type": "markdown", "id": "cell_0032_dd35a816", "created_at": "2026-07-31T00:00:00+00:00", "title": "Provenance"}
-->
### Provenance

| Field | Value |
| --- | --- |
| Command | `uv run --frozen python repro/src/verify_claim4_theorem43.py` |
| Repo Git SHA | `9799451c4aa312bb27e8c246814620257072be98` |
| Seed | `260202877` |
| Runtime | 35.5 s |
| Environment | Python 3.12.11, numpy 2.5.1, scipy 1.18.0, pinned by `uv.lock`; CPU only |
| Paper source | [ar5iv](https://ar5iv.labs.arxiv.org/html/2602.02877) retrieved 2026-07-31, SHA-256 `00670f81db728e76f35ebee5a56019ee…` |


---
<!-- trackio-cell
{"type": "markdown", "id": "cell_0033_15a30822", "created_at": "2026-07-31T00:00:00+00:00", "title": "Evidence files"}
-->
### Evidence files

| Artifact | Bytes | SHA-256 |
| --- | --- | --- |
| [`evidence/claim_4/theorem43_summary.json`](https://huggingface.co/spaces/DineshAI/0SGle5hjIf/blob/main/evidence/claim_4/theorem43_summary.json) | 3708 | `26e667f9ef498dfffc557878325a8686…` |
| [`evidence/claim_4/theorem43_figure1.csv`](https://huggingface.co/spaces/DineshAI/0SGle5hjIf/blob/main/evidence/claim_4/theorem43_figure1.csv) | 14524 | `5c1eced37d32c9ffaefd862cd78d8e17…` |
| [`evidence/claim_4/theorem43_scaling.csv`](https://huggingface.co/spaces/DineshAI/0SGle5hjIf/blob/main/evidence/claim_4/theorem43_scaling.csv) | 5172 | `5fbcfacc69abf75321b7255f54298fe6…` |
| [`evidence/claim_4/theorem43_negative_control_euclidean.csv`](https://huggingface.co/spaces/DineshAI/0SGle5hjIf/blob/main/evidence/claim_4/theorem43_negative_control_euclidean.csv) | 237 | `a81c43aed62234e4d4049c50e043346e…` |
| [`evidence/claim_4/theorem43_negative_control_kappa.csv`](https://huggingface.co/spaces/DineshAI/0SGle5hjIf/blob/main/evidence/claim_4/theorem43_negative_control_kappa.csv) | 705 | `043420bd50b438fbc36a776cd1d86551…` |
| [`evidence/claim_4/claim_contract.json`](https://huggingface.co/spaces/DineshAI/0SGle5hjIf/blob/main/evidence/claim_4/claim_contract.json) | 1155 | `82772cc4cc4f5c2604f90b216d15ed03…` |
| [`evidence/claim_4/source_audit.md`](https://huggingface.co/spaces/DineshAI/0SGle5hjIf/blob/main/evidence/claim_4/source_audit.md) | 853 | `9985439c77b8e51c326d1411a768ebed…` |
| [`evidence/claim_4/method.md`](https://huggingface.co/spaces/DineshAI/0SGle5hjIf/blob/main/evidence/claim_4/method.md) | 861 | `43fb91fcd6e63585f3073f3aa936e7a8…` |
| [`evidence/claim_4/fixed_w_results.csv`](https://huggingface.co/spaces/DineshAI/0SGle5hjIf/blob/main/evidence/claim_4/fixed_w_results.csv) | 1919 | `80ebb637032656d3109433b804615062…` |
| [`evidence/claim_4/bound_factors.csv`](https://huggingface.co/spaces/DineshAI/0SGle5hjIf/blob/main/evidence/claim_4/bound_factors.csv) | 480 | `e7c8317bcaff0003eb17a6c60a2d5f2d…` |
| [`evidence/claim_4/EVAL.md`](https://huggingface.co/spaces/DineshAI/0SGle5hjIf/blob/main/evidence/claim_4/EVAL.md) | 5615 | `560b5b2384f207eca43f35d5557fbd72…` |
| [`evidence/claim_4/limitations.md`](https://huggingface.co/spaces/DineshAI/0SGle5hjIf/blob/main/evidence/claim_4/limitations.md) | 891 | `d4389719003f3d3f4daeb6f4d5c3fd1e…` |

Verifier: [`repro/src/verify_claim4_theorem43.py`](https://huggingface.co/spaces/DineshAI/0SGle5hjIf/blob/main/repro/src/verify_claim4_theorem43.py) · earlier fixed-`w` run: [`repro/src/verify_rate_kappa.py`](https://huggingface.co/spaces/DineshAI/0SGle5hjIf/blob/main/repro/src/verify_rate_kappa.py) · [https://github.com/MachineLearning-Nerd/icml26-repro-0SGle5hjIf-scent-compositional-entropy](https://github.com/MachineLearning-Nerd/icml26-repro-0SGle5hjIf-scent-compositional-entropy)

---
<!-- trackio-cell
{"type": "markdown", "id": "cell_0034_57dde81b", "created_at": "2026-07-31T00:00:00+00:00", "title": "Limitations and deviations"}
-->
### Limitations and deviations

**Deviation (reported, not hidden).** `False` for
"empirical ratio decreases monotonically in sigma". Mean ratios are
`0.5412 (sigma=0.25) -> 0.0961 -> 0.0112 (sigma=1.0) -> 0.0215 -> 0.0348 (sigma=2.0)`:
monotone up to `sigma=1`, then rising. The paper's Figure 1 remark suggests
monotone decrease. This is **not** part of the quantified claim under test —
Theorem 4.3/4.5 concern the *provable bound* ratio, whose identity and
`mu`-invariance verify exactly (C4.6, C4.7) — but it is a real discrepancy with
the figure's qualitative description and is recorded as such. At large `sigma`
the prescribed `alpha` becomes very small, so both methods spend the horizon in
the transient from `nu_0 = c1` toward `nu_*`; the ratio there is not the
asymptotic quantity the remark describes.

**Other scope notes.**
- The `1/e^{nu_*-c0}` factor is a ratio of **upper bounds**, so it is verified
  as an algebraic identity plus a directional empirical check (C4.8), not as a
  measured speedup magnitude. The exact ratio carries a
  `4 sqrt(C(1-r0+r0 log r0))/|nu_0-nu_*|` prefactor that the paper's remark drops.
- `s` is truncated at 6 sigma to satisfy Assumption 3.2(ii); this shifts `kappa`
  from `e^{sigma^2}` by at most 2.27%.
- Fixed `w` only, which is the setting Section 4.2 defines.
