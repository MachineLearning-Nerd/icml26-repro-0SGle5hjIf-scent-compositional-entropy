# Output boundary

`outputs/verdict.json` and `outputs/verify_run.log` are retained from the
original six-proxy judge-regression check. They are useful for reproducing the
historical `6/6` synthetic output, but they are **not** the current paper-level
verdict.

Use these authoritative paths instead:

- `.openresearch/artifacts/claim_1/` through `claim_6/` for claim contracts,
  raw evidence, verdicts, and limitations;
- `.openresearch/artifacts/dual_independent_checker.json` for Claims 1 and 3;
- `.openresearch/artifacts/rate_kappa_independent_checker.json` for Claims 2
  and 4;
- `publication_gate.json` for the consolidated status.

The fixed orchestration command is:

```bash
uv run --frozen python repro/src/verify_scent.py
```
