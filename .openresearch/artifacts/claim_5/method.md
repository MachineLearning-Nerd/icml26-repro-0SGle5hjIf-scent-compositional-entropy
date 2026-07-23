# Claim 5 method

The verifier queries the Hugging Face dataset tree APIs at recorded immutable
revisions, sums every file size, inventories the exact official SCENT Git tree
and its release assets, and searches Hugging Face for published extracted
feature datasets. It then computes the minimum float32 feature storage and the
minimum number of example visits and batch updates for the requested
four-method comparison.

An independent script reduces only the raw JSON inventory. Its negative
control injects a published feature tensor and 3 TB of free disk; this must
remove the blocker. The suite exits nonzero if revisions, byte counts, blocker
predicates, or the negative control disagree.
