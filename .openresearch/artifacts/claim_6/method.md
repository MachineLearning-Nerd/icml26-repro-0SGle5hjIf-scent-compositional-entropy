# Claim 6 method

The implementation uses torchvision's CIFAR archives and the released SCENT
repository's ImageNet-style ResNet-18 architecture, xavier initialization,
binary construction, balanced positive/negative batches, squared-hinge
surrogate, SCENT and SOX dual updates, and tabled method hyperparameters.
Pretraining and fine-tuning use the paper's 60/60 epoch protocol. All execution
is forced to CPU.

Because the backbone is frozen, each epoch's augmented backbone features are
computed once and shared across method variants for paired fairness. BatchNorm
is kept in evaluation mode; allowing running statistics to change would violate
the paper's statement that the backbone is frozen. Exact unaugmented training
objectives and test pAUC are evaluated before fine-tuning and every 10 epochs
through the epoch-60 endpoint.

The independent checker reduces only raw CSV. Final SCENT-minus-SOX differences
are paired by seed and bootstrapped. A 0.002 absolute equivalence margin was
fixed before running: it is slightly larger than the largest vector-extracted
paper gap (0.0012841), but an order of magnitude smaller than the plot's 0.025
tick spacing.

The first full run completed every CIFAR-10 checkpoint but was cancelled after
8h15m when its 12-hour ceiling became certain to interrupt CIFAR-100. The
continuation imports only the 12 CIFAR-10 epoch-60 rows used by the checker.
Their CSV and provenance JSON are SHA-256 pinned; the source log independently
contained exactly 72/72 unique printed checkpoint rows. CIFAR-100 is executed
live with the unchanged protocol. Splitting execution this way changes neither
the data, model, optimizer, seeds, nor comparison contract.

The paper's exact prose statement concerns training loss, so that remains the
primary verdict metric. Test partial AUC is reduced independently as secondary
evidence and is never substituted for the source claim.
