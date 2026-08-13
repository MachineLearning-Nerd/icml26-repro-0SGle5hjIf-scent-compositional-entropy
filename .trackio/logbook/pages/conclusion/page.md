# Conclusion


---
<!-- trackio-cell
{"type": "markdown", "id": "cell_0049_e39262de", "created_at": "2026-07-31T00:00:00+00:00", "title": "Conclusion"}
-->
## Overall findings

Four of the paper's six headline claims are **VERIFIED** as rigorous numerical
audits conducted under the theorems' own hypotheses and with the step sizes the
theorems themselves prescribe. One is **FALSIFIED** at the paper's full CIFAR
protocol. One is **BLOCKED** by a compute authorization boundary rather than by
any property of the paper.

The theory is the strong part of this paper and it holds up. The three
ingredients that make SCENT work — the closed-form Bregman proximal step, the
interval invariant that step induces, and the `kappa`-controlled advantage over a
Euclidean dual update — each survive a targeted attempt to break them:

- Replacing the `phi(nu) = e^{-nu}` geometry with a plain Euclidean step of the
  same size violates bound (15) (measured gap 8.903 vs bound 3.900).
- Understating `kappa` violates the same bound (0.9919 vs 0.1374), confirming
  `kappa` is genuinely the quantity that controls the rate.
- Bound (15) is not vacuous: its worst-case slack over the measured average gap
  is only **7.04x**.

The empirical side is weaker than the theory. At the paper's own CIFAR-10
`tau=0.05` setting, SOX beats SCENT on the training CERM objective on all three
seeds by a margin an order of magnitude above the predeclared equivalence
threshold, which contradicts "SCENT matches or exceeds the SOX baseline" as a
statement quantified over both datasets and both `tau` values.

## What changed since the judged revision

The judged revision `7fcacca041de1f1d591846177267ffb679c0dea7` scored 6/12. Its
claim pages asserted results ("512 proximal argmins", "33,554,432 updates")
**without publishing the underlying data** — the artifacts existed in the
reproduction repository but were never uploaded to this Space, so no reader
could check them. This revision:

1. Publishes every raw CSV/JSON artifact under `evidence/` and every verifier
   under `repro/src/`, with SHA-256 for each file on the claim page that cites it.
2. Restructures the logbook into the canonical index / executive summary /
   claim-1..6 / conclusion layout.
3. **Rebuilds Claim 4 against the theorem's prescribed step sizes.** The earlier
   run hand-tuned `alpha` per `mu` (`e^-6` vs `e^3`), which tested a different
   algorithm and produced a spurious 93% failure of the Figure 1
   `mu`-invariance. With the prescribed `alpha_t` the invariance holds to 0.37%.
4. Replaces Claim 5's unquantified "datasets unavailable" with a live,
   re-runnable Hub audit that measures every candidate asset, including
   `imageomics/TreeOfLife-200M-Embeddings` (345.85 GB) which the earlier audit
   missed, and explains precisely why it does not substitute.
5. Corrects the `command.txt` provenance in every claim artifact, which had
   pointed at the toy 80x5 `verify_scent.py` script rather than the verifier
   that actually produced the evidence.

## Reproducibility notes

- **One pinned environment** (`pyproject.toml` + `uv.lock`, Python 3.12.11,
  numpy 2.5.1, scipy 1.18.0) is reused for every claim. `uv sync --frozen`
  followed by the per-claim commands reproduces everything.
- **Determinism is verified, not assumed.** Re-running the Claim 1/2/3/4
  verifiers in a freshly synced environment regenerated every raw CSV
  **byte-identically** (after newline normalization); the only field that
  changed was `runtime_seconds`. SHA-256 of each artifact is on its claim page.
- **Every verifier exits nonzero when its evidence fails**, and each carries a
  negative control that is required to fail. A control that turned out *not* to
  discriminate (inflating `alpha` past Theorem 4.3's cap, which speeds SPMD up
  rather than breaking the bound) was removed and replaced rather than reported
  as a pass.
- **No toy result is described as full-scale.** Claims 1-4 are numerical audits
  of theorem statements and are labelled as such; they are not proofs. Claim 6
  is at the paper's full CIFAR protocol. Claim 5 is BLOCKED and no proxy is
  offered in its place.
- Paper text was read from [ar5iv](https://ar5iv.labs.arxiv.org/html/2602.02877) retrieved 2026-07-31, SHA-256
  `00670f81db728e76f35ebee5a56019ee9382370bfc43d64d69eddbe74a8adab6`.

## Preserved evidence from earlier revisions

All pages from the judged revision are retained in this Space and remain
readable:

- [`pages/overview/page.md`](https://huggingface.co/spaces/DineshAI/0SGle5hjIf/blob/main/pages/overview/page.md)
- [`pages/claims/page.md`](https://huggingface.co/spaces/DineshAI/0SGle5hjIf/blob/main/pages/claims/page.md)
- [`pages/evidence/page.md`](https://huggingface.co/spaces/DineshAI/0SGle5hjIf/blob/main/pages/evidence/page.md)
- [`pages/verification-run/page.md`](https://huggingface.co/spaces/DineshAI/0SGle5hjIf/blob/main/pages/verification-run/page.md)
- [`pages/rigorous-update/page.md`](https://huggingface.co/spaces/DineshAI/0SGle5hjIf/blob/main/pages/rigorous-update/page.md)

## Links

- Paper: [arXiv:2602.02877](https://arxiv.org/abs/2602.02877) · [ar5iv HTML](https://ar5iv.labs.arxiv.org/html/2602.02877)
- Official implementation: [https://github.com/Optimization-AI/SCENT/tree/cfbf17925754f18855f26715adeec4773aa0591d](https://github.com/Optimization-AI/SCENT/tree/cfbf17925754f18855f26715adeec4773aa0591d)
- Reproduction repository: [https://github.com/MachineLearning-Nerd/icml26-scent-compositional-entropy](https://github.com/MachineLearning-Nerd/icml26-scent-compositional-entropy)
- This logbook: [https://huggingface.co/spaces/DineshAI/0SGle5hjIf](https://huggingface.co/spaces/DineshAI/0SGle5hjIf)
- Datasets referenced: [imageomics/TreeOfLife-10M](https://huggingface.co/datasets/imageomics/TreeOfLife-10M),
  [imageomics/TreeOfLife-200M-Embeddings](https://huggingface.co/datasets/imageomics/TreeOfLife-200M-Embeddings),
  [gaunernst/glint360k-wds-gz](https://huggingface.co/datasets/gaunernst/glint360k-wds-gz)
