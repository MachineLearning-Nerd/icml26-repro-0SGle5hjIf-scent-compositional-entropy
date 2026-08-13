# Claim 5: Extreme classification on Glint360K and TreeOfLife-10M


---
<!-- trackio-cell
{"type": "markdown", "id": "cell_0035_a69f38bf", "created_at": "2026-07-31T00:00:00+00:00", "title": "Claim and source audit"}
-->
**Paper claim.** On extreme classification benchmarks Glint360K and TreeOfLife-10M, SCENT consistently outperforms the SOX, U-max, and BSGD baselines on both training and validation convergence (Section 5, extreme classification experiments).

**Source anchor.** Section 5.1 and Appendix F.4 of [arXiv:2602.02877](https://arxiv.org/abs/2602.02877)
([ar5iv](https://ar5iv.labs.arxiv.org/html/2602.02877), retrieved 2026-07-31). Glint360K: 17M images, 360K classes,
ResNet-50 features. TreeOfLife-10M: 10M images, 160K species, CLIP ViT-B/16
(BioCLIP v1) features. Batch size 128, 50 epochs, SGD optimizer, 3 seeds.

**Verdict: BLOCKED.** Not verified, not falsified, and deliberately **not**
substituted with a proxy.

---
<!-- trackio-cell
{"type": "markdown", "id": "cell_0036_9d34a7cb", "created_at": "2026-07-31T00:00:00+00:00", "title": "Feasibility audit"}
-->
### Why BLOCKED, measured rather than asserted

The judged revision recorded "datasets unavailable and storage insufficient"
without naming what had been searched. This page replaces that with a live,
re-runnable audit of every candidate asset.

**What the protocol needs:**

| dataset | images | feature_dim | source_bytes_gb | min_float32_features_gb |
| --- | --- | --- | --- | --- |
| Glint360K | 17091657 | 512 | 129.9 | 35.0 |
| TreeOfLife-10M | 9533174 | 512 | 1994.6 | 19.5 |

Minimum protocol: **4 methods x 3 seeds x
50 epochs x 2 datasets =
15,974,898,600 example visits** (124,804,200 batch steps at
batch size 128).

**What is actually published (measured live against the Hub):**

| repo | revision | files | size_gb |
| --- | --- | --- | --- |
| [imageomics/TreeOfLife-200M-Embeddings](https://huggingface.co/datasets/imageomics/TreeOfLife-200M-Embeddings) | 820c8e8fb370 | 670 | 345.85 |
| [imageomics/TreeOfLife-10M](https://huggingface.co/datasets/imageomics/TreeOfLife-10M) | 91debffb7146 | 80 | 1994.64 |
| [gaunernst/glint360k-wds-gz](https://huggingface.co/datasets/gaunernst/glint360k-wds-gz) | d0da68fbc62b | 1387 | 129.92 |

**Neither path is open on CPU-only compute:**

1. **Glint360K.** No extracted-feature asset exists on the Hub. The authors'
   pretrained ResNet-50 is distributed through a Google Drive folder, not a Hub
   repo. Producing the features means encoder inference over **17,091,657
   images**, which requires GPU hardware. **GPU is not authorized for this
   campaign**, so this path is closed by policy, not by budget.
2. **TreeOfLife-10M.** The source webdataset is **1,994.6 GB**. Feature
   extraction again needs a GPU.
3. **The one precomputed-embedding asset does not substitute.**
   [`imageomics/TreeOfLife-200M-Embeddings`](https://huggingface.co/datasets/imageomics/TreeOfLife-200M-Embeddings)
   (**345.85 GB**, 666 parquet shards) is real and was not identified by the
   earlier audit — but it embeds **TreeOfLife-200M** (233,055,986 rows), a
   different corpus from the paper's TreeOfLife-10M (9,533,174 images), using
   **BioCLIP-2 at 768-d** rather than the paper's BioCLIP v1 ViT-B/16 at 512-d.
   Its rows are sorted by taxonomic hierarchy, so any affordable shard subset is
   a contiguous taxonomic block; an unbiased 10M-row sample would require
   reading all 345.85 GB.

---
<!-- trackio-cell
{"type": "markdown", "id": "cell_0037_b0b72c72", "created_at": "2026-07-31T00:00:00+00:00", "title": "Scope discipline"}
-->
### Why no proxy result is reported

A reduced taxonomic slice of a different corpus, embedded by a different
backbone, would not test "on Glint360K and TreeOfLife-10M, SCENT consistently
outperforms SOX, U-max and BSGD". Reporting such a run as evidence for or
against this claim would misrepresent its scope, so none is reported.

BLOCKED is a terminal, honest state here: it is **not** a PASS, and it is not
converted into one. The mechanism the extreme-classification experiment relies
on — the SPMD dual update, its boundedness, its rate, and its advantage over an
SGD dual update — is verified independently on Claims 1-4.

---
<!-- trackio-cell
{"type": "markdown", "id": "cell_0038_dd35a816", "created_at": "2026-07-31T00:00:00+00:00", "title": "Provenance"}
-->
### Provenance

| Field | Value |
| --- | --- |
| Command | `python3 repro/src/verify_claim5_asset_audit.py  # Hub metadata probe: needs huggingface_hub, which is outside the pinned numerics venv` |
| Repo Git SHA | `9799451c4aa312bb27e8c246814620257072be98` |
| Seed | `n/a (deterministic Hub metadata probe)` |
| Runtime | 2.2 s |
| Environment | Python 3.12.11, numpy 2.5.1, scipy 1.18.0, pinned by `uv.lock`; CPU only |
| Paper source | [ar5iv](https://ar5iv.labs.arxiv.org/html/2602.02877) retrieved 2026-07-31, SHA-256 `00670f81db728e76f35ebee5a56019ee…` |
| Note | The audit needs `huggingface_hub`, which is outside the pinned numerics venv, so it runs on the system interpreter. It performs no numerical computation. |


---
<!-- trackio-cell
{"type": "markdown", "id": "cell_0039_15a30822", "created_at": "2026-07-31T00:00:00+00:00", "title": "Evidence files"}
-->
### Evidence files

| Artifact | Bytes | SHA-256 |
| --- | --- | --- |
| [`evidence/claim_5/asset_audit.json`](https://huggingface.co/spaces/DineshAI/0SGle5hjIf/blob/main/evidence/claim_5/asset_audit.json) | 5762 | `48bcd28fb9f1fbe53faaed9d9b00c054…` |
| [`evidence/claim_5/raw_asset_inventory.json`](https://huggingface.co/spaces/DineshAI/0SGle5hjIf/blob/main/evidence/claim_5/raw_asset_inventory.json) | 1598 | `817a47b263ce72a4be6f512cee5703ad…` |
| [`evidence/claim_5/claim_contract.json`](https://huggingface.co/spaces/DineshAI/0SGle5hjIf/blob/main/evidence/claim_5/claim_contract.json) | 843 | `65b42864955abd629037871da43c515e…` |
| [`evidence/claim_5/source_audit.md`](https://huggingface.co/spaces/DineshAI/0SGle5hjIf/blob/main/evidence/claim_5/source_audit.md) | 911 | `59d42005ce83cc1bd246bb93ec9b001d…` |
| [`evidence/claim_5/method.md`](https://huggingface.co/spaces/DineshAI/0SGle5hjIf/blob/main/evidence/claim_5/method.md) | 695 | `060f6c37597c0282148e935665cac627…` |
| [`evidence/claim_5/verdict.json`](https://huggingface.co/spaces/DineshAI/0SGle5hjIf/blob/main/evidence/claim_5/verdict.json) | 348 | `10ecfff532d3e9057a4811f0885a4564…` |
| [`evidence/claim_5/independent_checker.json`](https://huggingface.co/spaces/DineshAI/0SGle5hjIf/blob/main/evidence/claim_5/independent_checker.json) | 190 | `99d97152f2c7e5e023d18b9be3ea1b73…` |
| [`evidence/claim_5/negative_control.json`](https://huggingface.co/spaces/DineshAI/0SGle5hjIf/blob/main/evidence/claim_5/negative_control.json) | 106 | `69f3f0543c7da40ff5682811909f2ea9…` |
| [`evidence/claim_5/EVAL.md`](https://huggingface.co/spaces/DineshAI/0SGle5hjIf/blob/main/evidence/claim_5/EVAL.md) | 366 | `6e86895c87c2bebd58b02fcd49d55a64…` |
| [`evidence/claim_5/limitations.md`](https://huggingface.co/spaces/DineshAI/0SGle5hjIf/blob/main/evidence/claim_5/limitations.md) | 598 | `ddcc7f8f2bb3b8995bb67e8a1192c4e0…` |

Verifiers: [`repro/src/verify_claim5_asset_audit.py`](https://huggingface.co/spaces/DineshAI/0SGle5hjIf/blob/main/repro/src/verify_claim5_asset_audit.py), [`repro/src/verify_claim5_feasibility.py`](https://huggingface.co/spaces/DineshAI/0SGle5hjIf/blob/main/repro/src/verify_claim5_feasibility.py) · official code: [https://github.com/Optimization-AI/SCENT/tree/cfbf17925754f18855f26715adeec4773aa0591d](https://github.com/Optimization-AI/SCENT/tree/cfbf17925754f18855f26715adeec4773aa0591d) (`xc/extract_feat.py`, `xc/train.py`) · [https://github.com/MachineLearning-Nerd/icml26-scent-compositional-entropy](https://github.com/MachineLearning-Nerd/icml26-scent-compositional-entropy)

---
<!-- trackio-cell
{"type": "markdown", "id": "cell_0040_f80c4215", "created_at": "2026-07-31T00:00:00+00:00", "title": "What would unblock this"}
-->
### What would unblock this

Any one of: (a) authorization for GPU feature extraction; (b) the authors
publishing the extracted `features.pt`/`labels.pt` tensors referenced in
`xc/README.md`; or (c) a Hub asset carrying BioCLIP v1 512-d embeddings of the
TreeOfLife-10M image set with species labels. Item (b) is the cheapest and would
make the whole experiment CPU-reachable, since `xc/train.py` trains only a linear
classifier on precomputed features.
