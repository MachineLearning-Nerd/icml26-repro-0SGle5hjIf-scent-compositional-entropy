# Final release and publication report

Status: **PUBLISHED — AWAITING JUDGE**

The approved two-file, text-only update was published to the existing Space at
revision `7fcacca041de1f1d591846177267ffb679c0dea7`. The latest judge record
remains 5/12 at the prior revision, so no score increase is claimed.

## Baseline and immutable references

- Paper: arXiv `2602.02877v2`; HTML SHA-256
  `00670f81db728e76f35ebee5a56019ee9382370bfc43d64d69eddbe74a8adab6`;
  source archive SHA-256
  `be5a8c38a06b2476579e48e9036df67c3daf242ad06c6ec949864aebfcd20fba`.
- Validated baseline branch: `master`, starting SHA
  `b3a5d8974775cf428666476ed2820c6d53cdeda9`.
- Baseline judge score: `5/12`.
- Published Hugging Face Head:
  `7fcacca041de1f1d591846177267ffb679c0dea7`.
- Latest Judge Head:
  `71993d9a3c56ee16bd8935f11d635988eb494f5b`.
- Published Space: `DineshAI/0SGle5hjIf`. No second Space exists.

## Experiment tree

The tree used stacked decisions rather than a flat sweep:

1. Freeze and run the validated baseline.
2. Branch exact dual contracts for Claims 1 and 3.
3. Branch rate/κ alternatives, descend onto the calibrated step, and merge the
   strongest cumulative Claims 1–4 node.
4. Descend to the exact Claim 5 feasibility contract.
5. Profile CIFAR transport locally, then use HF cpu-upgrade for the full
   protocol.
6. Retain complete CIFAR-10 rows from the timed full run, partition CIFAR-100
   deterministically into three terminal seed shards, then integrate only
   provenance-bound terminal rows.
7. Descend to the visual release candidate, strengthen the Claim 4 bound-factor
   checker, and promote its terminal outputs to the final publication gate.

The publication candidate branch is `release/final-publication-gate` (renamed
from `orx/final-publication-gate`). Its immediate
scientific parent is release-regression commit
`f2721c483a4705ec777af0be15e3a13119e3a363`.

## Claim verdicts

| Claim | Verdict | Direct result |
|---|---|---|
| 1 | VERIFIED | 512 independent proximal argmins; 400 stress cases; 90-digit checker; negative control rejected |
| 2 | VERIFIED | four horizons × 20 seeds; slope −0.454; bounded √T-scaled gap; theorem step conditions checked |
| 3 | VERIFIED | 33,554,432 unprojected updates across four intervals; zero breaches; negative control rejected |
| 4 | VERIFIED | one million samples per Gaussian setting; κ error ≤0.73%; six bound factors independently recomputed with zero relative error; both controls rejected |
| 5 | BLOCKED | exact assets absent; source/feature storage and 15.97B-visit minimum protocol exceed authorized host; no toy substitution |
| 6 | FALSIFIED | CIFAR-10 τ=.05 objective differences `[0.03234854, 0.00816448, 0.04071236]`; 95% interval `[0.00816448, 0.04071236]` is above +0.002 |

Claim 6 uses 24 endpoint rows: two datasets, two τ values, two methods, and
three seeds. CIFAR-10 τ=.1 is equivalent, CIFAR-100 τ=.05 unresolved, and
CIFAR-100 τ=.1 favors SCENT. Secondary test pAUC is mixed and is not substituted
for the paper's training-loss statement.

## Evidence and reproducibility

- Per-claim evidence: `.openresearch/artifacts/claim_1/` through
  `.openresearch/artifacts/claim_6/`.
- Source and verdict audits: `.openresearch/audit/`.
- Visual report: `reports/scent-reproduction/report.md`.
- Tutorial notebook: `notebooks/scent_reproduction.py`.
- Complete formal command/run record:
  `.openresearch/release/commands_executed.md`.
- Fixed command on every experiment:
  `uv run --frozen python repro/src/verify_scent.py`.
- Environment: Python 3.12, repository-level `.venv`, `pyproject.toml`,
  `.python-version`, and `uv.lock`; no conda, unmanaged pip, or GPU.

The cumulative release regression at commit `f2721c4` is run
`472656ec-77a1-4d7a-affd-b90f9a142b8d`. It passed the rigorous dual,
rate/κ, Claim 5 feasibility, and Claim 6 suites. The historical toy header is
retained only for backward-compatible regression output and is not accepted as
claim evidence.

## Compute and cost

At the 2026-07-24 20:05 IST ledger snapshot:

- Local CPU: 13 runs, approximately 1.03 total wall-clock hours.
- HF cpu-upgrade: 8 runs, approximately 59.80 total wall-clock hours.
- Published rate: $0.03/hour; estimated HF cost: approximately $1.79.
- GPU usage: zero.

The HF total includes failed/cancelled profiling and the superseded continuation
run `1bf04add-3840-44c7-997c-80a23fbbde29`. Its cancellation flag is set, but
the provider still reports it running; it is excluded from scientific evidence.
Actual invoice rounding may differ.

## Protected Space and upload gate

The release audit passes:

- 17/17 judged paths remain a subset of the 18-path additive candidate.
- Every locally mirrored unchanged page/asset matches its judged SHA-256.
- The candidate logbook JSON is valid; all page references exist; the new page
  is reachable.
- The intended upload is text-only and contains no detected secret patterns.

Exact upload allowlist:

```text
logbook.json
pages/rigorous-update/page.md
```

Their exact candidate hashes are in
`.openresearch/release/hf_upload_manifest.sha256`. The full artifact manifest
is `.openresearch/release/candidate_artifact_manifest.sha256`; the machine audit
is `.openresearch/release/release_audit.json`.

## Publication outcome

Explicit approval was received on 2026-07-24. The two allowlisted files were
committed through the Hugging Face API, and their downloaded SHA-256 values
exactly matched `.openresearch/release/hf_upload_manifest.sha256`. The Space
reported the new revision and retained all 17 paths from the judged revision.
The candidate is marked awaiting judge; the prior 5/12 verdict remains the only
live score until the judge evaluates the new Hugging Face revision.
