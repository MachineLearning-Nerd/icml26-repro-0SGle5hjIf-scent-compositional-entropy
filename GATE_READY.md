# Evidence and publication status

## Current scientific result

`MIXED_RESULTS`

- Claims 1–4: scoped contracts pass (`VERIFIED_SCOPED`; C3 is conditional on
  Lemma 3.3 assumptions).
- Claim 5: `BLOCKED`; the exact feature assets and authorized resources are
  insufficient for a faithful two-dataset benchmark.
- Claim 6: `FALSIFIED_FOR_DECLARED_PROTOCOL`; CIFAR-10 at `tau=0.05` contradicts
  the predeclared “SCENT slightly better than SOX” training-objective contract.

## Gate interpretation

`EVIDENCE_RELEASE_GATE = PASSED`

The release contains a contract, producer, raw artifact, verdict, limitation,
and independent check or inventory reduction for every claim. Negative controls
are rejected. This is an evidence-integrity gate, not a claim that all six
paper results pass.

`STRICT_PAPER_CLAIM_GATE = NOT_READY`

The paper-level set is not fully verified because one benchmark is blocked and
one literal comparison is falsified under the declared reproduction protocol.

## Reproduction command

```bash
uv run --frozen python repro/src/verify_scent.py
```

The authoritative outputs are under `.openresearch/artifacts/claim_1/` through
`.openresearch/artifacts/claim_6/`. The root `outputs/verdict.json` is retained
for historical judge regression and is explicitly non-authoritative.

## Historical publication record

The repository records a text-only Hugging Face Space update for
`DineshAI/0SGle5hjIf`:

- candidate revision: `7fcacca041de1f1d591846177267ffb679c0dea7`;
- post-publication readback: `9aec025410a7a2d2eede107d4c874ce51064ce3f`;
- last recorded judge score: `5/12` at
  `71993d9a3c56ee16bd8935f11d635988eb494f5b`;
- no later score increase is claimed by this repository.
