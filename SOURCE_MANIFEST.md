# Source and provenance manifest

## Paper

- Title: *A Geometry-Aware Efficient Algorithm for Compositional Entropic Risk
  Minimization*
- Authors: Xiyuan Wei, Linli Zhou, Bokun Wang, Chih-Jen Lin, and Tianbao Yang
- arXiv: [2602.02877v2](https://arxiv.org/abs/2602.02877)
- HTML: [arXiv HTML](https://arxiv.org/html/2602.02877)
- OpenReview: [0SGle5hjIf](https://openreview.net/forum?id=0SGle5hjIf)
- Official code: [Optimization-AI/SCENT](https://github.com/Optimization-AI/SCENT)
- Official code revision audited: `cfbf17925754f18855f26715adeec4773aa0591d`

The retrieved source metadata and hashes are recorded in
`.openresearch/audit/paper_source.json`; claim anchors are recorded in
`.openresearch/audit/paper_claim_anchors.md`.

## Benchmark inputs

### Claim 5

- Glint360K: `gaunernst/glint360k-wds-gz`, revision
  `d0da68fbc62b545010942f959d2d3b6a364f57b8`, 17,091,657 examples,
  129.92 GB raw source.
- TreeOfLife-10M: `imageomics/TreeOfLife-10M`, revision
  `91debffb7146c32c89d76feb1eb575b555e2ecc7`, 9,533,174 examples,
  1.99 TB raw source.
- No official paper-specific extracted feature asset was found at audit time.
- The exact inventory and search results are in
  `.openresearch/artifacts/claim_5/raw_asset_inventory.json` and
  `asset_audit.json`.

### Claim 6

- CIFAR-10 archive: MD5 `c58f30108f718f92721af3b95e74349a` and SHA-256
  `6d958be074577803d12ecdefd02955f39262c83c16fe9348329d7fe0b5c001ce`.
- CIFAR-100 archive: MD5 `eb9058c3a382ffc7106e4002c42a8d85` and SHA-256
  `85cd44d02ba6437773c5bbd22e183051d648de2e7d6b014e1ef29b855ba677a7`.
- Dataset acquisition revisions and terminal run provenance are recorded in
  `.openresearch/artifacts/claim_6/integrated_provenance.json`.

## Environment

- Python: `3.12.11`
- Platform used for the integrated evidence: CPU-only macOS arm64
- Dependencies: `pyproject.toml` and `uv.lock`
- Fixed command: `uv run --frozen python repro/src/verify_scent.py`
- GPU usage: none for the recorded local or Hugging Face CPU evidence

## Publication record

The historical Space publication record is preserved in
`.openresearch/release/`: candidate revision `7fcacca...`, readback revision
`9aec025...`, and last recorded judge revision `71993d9...` with score `5/12`.
Full hashes are in `publication_gate.json` and the release files.
