# Branch audit and rename map

The original repository used `master` plus 20 `orx/*` experiment branches. The
final repository uses descriptive names grouped by purpose. The old names are
recorded here for provenance; they are not intended to remain as remote refs.

## Legacy-to-final map

| Legacy ref | Final ref | What it does |
|---|---|---|
| `master` | `main` | Integrated publication surface and current evidence snapshot |
| `orx/validated-5-12-baseline` | `baseline/validated-5-12` | Pins the judged 5/12 baseline, paper source, and environment |
| `orx/exact-dual-contracts-c1-c3` | `research/dual-contracts-c1-c3` | Builds exact Claims 1 and 3 contracts plus high-precision checking |
| `orx/rate-and-kappa-contracts-c2-c4` | `research/rate-kappa-c2-c4` | Adds initial Claim 2 rate and Claim 4 `kappa` contracts |
| `orx/asymptotic-rate-calibrated-step` | `research/calibrated-rate-step` | Calibrates the admissible asymptotic rate experiment |
| `orx/cumulative-theory-evidence-c1-c4` | `research/cumulative-theory-c1-c4` | Integrates the strongest Claims 1–4 evidence |
| `orx/claim-5-full-scale-feasibility-contract` | `audit/claim-5-feasibility` | Audits exact extreme-classification assets, storage, and workload |
| `orx/claim-6-exact-protocol-cpu-profile` | `audit/claim-6-cifar-profile` | Profiles the exact CIFAR partial-AUC protocol on CPU |
| `orx/claim-6-checksummed-mirror-cpu-profile` | `audit/claim-6-mirror-profile` | Tests checksummed CIFAR acquisition mirrors |
| `orx/claim-6-pinned-cdn-cpu-profile` | `audit/claim-6-pinned-cdn-profile` | Pins and profiles CDN archive acquisition |
| `orx/claim-6-robust-transport-cpu-profile` | `audit/claim-6-robust-transport` | Makes archive transport robust without adding a dependency |
| `orx/claim-6-full-cifar-protocol` | `research/claim-6-full-cifar` | Configures the paper-faithful 60/60-epoch CIFAR protocol |
| `orx/claim-6-cifar-100-continuation` | `research/claim-6-cifar100-continuation` | Preserves complete CIFAR-10 evidence while continuing CIFAR-100 |
| `orx/claim-6-cifar-100-shard-protocol` | `audit/claim-6-cifar100-shard-protocol` | Defines provenance-safe terminal CIFAR-100 seed shards |
| `orx/claim-6-cifar-100-seed-79-shard` | `research/claim-6-cifar100-seed79` | Runs and records the terminal CIFAR-100 seed-79 shard |
| `orx/claim-6-cifar-100-seed-2024-shard` | `research/claim-6-cifar100-seed2024` | Runs and records the terminal CIFAR-100 seed-2024 shard |
| `orx/claim-6-cifar-100-seed-2602-shard` | `research/claim-6-cifar100-seed2602` | Runs and records the terminal CIFAR-100 seed-2602 shard |
| `orx/claim-6-integrated-cifar-verdict` | `release/claim-6-integrated-verdict` | Integrates 24 provenance-bound endpoint rows and the C6 verdict |
| `orx/release-candidate-evidence-and-report` | `release/evidence-candidate` | Packages claim evidence and the forensic release report |
| `orx/final-publication-gate` | `release/final-publication-gate` | Finalizes the release gate and Claim 4 audit |
| `orx/space-evidence-publication` | `release/space-publication` | Records the text-only Hugging Face publication and readback |

There are 21 final branches: `main` plus the 20 supporting refs above. The
seed-79 shard and shard-protocol refs intentionally point to the same historical
tip. The old `master` and `space-evidence-publication` refs also shared their
latest tip; both roles remain explicit in the map.

The three CIFAR-100 seed branches are preserved even though their tips are
independent evidence sources rather than ordinary ancestors of the integrated
publication branch.

## Branch naming rules

- `main` is the only publication/default branch.
- `baseline/*` is for frozen reference state.
- `research/*` is for scientific contracts, calibrations, and terminal runs.
- `audit/*` is for feasibility, transport, and integrity checks.
- `release/*` is for integrated verdicts and publication packaging.
- No new `orx/*` names should be added to the final remote.

## Identity requirement

After normalization, every reachable commit on every final branch must use:

```text
MachineLearning-Nerd <MachineLearning-Nerd@users.noreply.github.com>
```

## Publication checks

After the rename and history normalization, verify:

- repository name `icml26-scent-compositional-entropy`;
- default branch `main`;
- exactly the 21 final branches above;
- no remote `master` or `orx/*` refs;
- README, gate, publication JSON, status, source manifest, audit report, and
  branch audit are reachable from `main`;
- every reachable author and committer identity is the required
  `MachineLearning-Nerd` identity;
- local `main` tracks `origin/main` with a clean worktree.
