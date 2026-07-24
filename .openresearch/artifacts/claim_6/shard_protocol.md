# Claim 6 CIFAR-100 shard protocol

The exact CIFAR-100 protocol is partitioned by deterministic fine-tuning seed
because a combined three-seed CPU job did not finish within its provider
window. Each shard repeats the same 60-epoch CIFAR-100 pretraining and runs
both temperatures, both methods, and all 60 fine-tuning epochs for one declared
seed. The fixed repository command and all algorithmic settings remain
unchanged.

A shard reports `SHARD_ONLY`, never `VERIFIED` or `FALSIFIED`. Its independent
checker requires every scheduled checkpoint and rejects a truncated-row
negative control. Only a later integration node may combine provenance-bound
terminal shard rows with the completed CIFAR-10 rows and assign Claim 6's
verdict.
