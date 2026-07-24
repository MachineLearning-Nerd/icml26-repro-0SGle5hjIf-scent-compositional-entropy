# Command record

This file records the commands that define or validate the scientific result.
Read-only orientation commands (`rg`, `sed`, `find`, `git status`, `orx
status/runs/logs`, SQLite ledger reads, and image inspection) do not alter the
result and are represented by their command families rather than every repeated
poll.

## Mandatory startup

```bash
orx skill
orx skill orx-experiment-tree
orx skill orx-evidence
orx skill orx-git
orx skill orx-compute
orx projects --json
orx project view decc0f26-ee51-4d94-bebc-05ccf6bfd9db
orx runs decc0f26-ee51-4d94-bebc-05ccf6bfd9db
git status --short
git branch --show-current
git rev-parse HEAD
git branch -a
df -h
```

Environment inspection printed names only, never values. Paper retrieval used
the explicit User-Agent recorded in `.openresearch/audit/paper_source.json`.
The verdict dataset was filtered by the exact Space id, not by OpenReview id.

## Fixed formal command

Every experiment node inherited this exact command:

```bash
uv run --frozen python repro/src/verify_scent.py
```

The OpenResearch run ledger contains the following terminal or
cancellation-requested executions:

| Run id | Role | Backend | Terminal state at audit |
|---|---|---|---|
| `f96914af-fe7a-4548-bdf3-a893cb340f8d` | validated judged baseline | local CPU | done |
| `70fb32e3-2762-49ac-84e6-7ea3a2b4ac40` | first exact-dual control | local CPU | failed scientifically |
| `5fa123da-f5ff-4eb7-b2c1-0358d9c3315b` | exact dual contracts | local CPU | done |
| `8726a0e7-71bc-45e7-9a9a-38160621ece2` | first rate/κ contract | local CPU | failed scientifically |
| `d2f71d96-27a0-44d6-9c4a-4cae4ed852b5` | calibrated rate contract | local CPU | done |
| `3516bb83-de0b-459e-9e65-7534aae60b53` | cumulative Claims 1–4 | local CPU | done |
| `c87af3cf-87c8-4ddd-bb3e-0c812ddb7fb5` | Claim 5 local feasibility | local CPU | done |
| `6b2bcea0-832e-4721-a62f-c673b13559e7` | Claim 5 HF environment attempt | HF cpu-upgrade | failed environmentally |
| `3005279e-1d22-4d69-a6d0-9fd65545ce5c` | Claim 5 terminal feasibility | HF cpu-upgrade | done |
| `cb02789f-bcda-4b9a-9850-49284820abe9` | canonical CIFAR transport profile | local CPU | cancelled |
| `ec4d9f56-fe5e-484e-8389-70f986838467` | mirror transport profile | local CPU | failed checksum/transport |
| `c66ed394-526c-4b7e-8739-e43b6273bdc3` | pinned CDN profile | local CPU | cancelled |
| `5f880395-02b0-4d5b-82bf-1917ab527c4a` | first robust transport profile | local CPU | cancelled |
| `5e51db82-9c43-44c6-9288-b9e3d60bd66e` | robust transport profile | HF cpu-upgrade | done |
| `292e041e-3234-4b9e-b504-61b4894848c4` | full CIFAR run; complete CIFAR-10 rows | HF cpu-upgrade | cancelled after retained checkpoint set |
| `1bf04add-3840-44c7-997c-80a23fbbde29` | superseded CIFAR-100 continuation | HF cpu-upgrade | cancellation requested; excluded |
| `ed1f67f8-ff8e-4c91-9470-a5dc4e2e6202` | CIFAR-100 seed 79 | HF cpu-upgrade | done |
| `c2303e58-60e5-4448-b791-00efbac360e5` | CIFAR-100 seed 2024 | HF cpu-upgrade | done |
| `7164998a-5c26-42c1-bb26-9c396e1ec1d6` | CIFAR-100 seed 2602 | HF cpu-upgrade | done |
| `6cb58e70-8c1a-421c-8ba1-528c1f6f4e18` | integrated cumulative verdict | local CPU | done |
| `472656ec-77a1-4d7a-affd-b90f9a142b8d` | strengthened Claim 4 and release regression | local CPU | done |

Runs were submitted only with `orx exp run`, monitored with bounded
`orx exp wait ... --timeout 480` calls, and analyzed through `orx logs`.

## Release validation

```bash
uv run --frozen python reports/scent-reproduction/make_figures.py
uv run --frozen marimo check notebooks/scent_reproduction.py
uv run --frozen python repro/src/audit_release.py
```

The visual report was mirrored into the dashboard Files tree under
`project/scent-reproduction/`. No Hugging Face upload command has been run.
