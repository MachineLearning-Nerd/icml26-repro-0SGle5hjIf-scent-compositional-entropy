# Claim 6 limitations and deviations

The authors do not publish the two pretrained checkpoints, their pretraining
script, the three exact seeds, or raw Figure 3 data. This reproduction trains
the paper-specified backbones from scratch and declares its seeds. It therefore
tests the stated protocol rather than reconstructing undisclosed checkpoints.

The paper/code margin discrepancy is material because it changes the absolute
loss scale. The paper-specified margin 0.5 is used. The frozen backbone runs in
evaluation mode; the released fine-tuning script calls `model.train()` and
therefore mutates BatchNorm running statistics despite disabling backbone
gradients.

The paper does not state its evaluation cadence. This reproduction evaluates
the exact objective and pAUC at epochs 0, 10, 20, 30, 40, 50, and 60; training
still executes all 60 epochs.

The two datasets and three CIFAR-100 seeds execute across four evidence-source
CPU jobs because measured combined runtimes exceeded provider windows.
CIFAR-10 final rows remain traceable to the cancelled parent run. Each
CIFAR-100 seed comes from a terminal, independently checked shard. Intermediate
checkpoints remain in their source logs; only the final rows consumed by the
claim checker are copied into the integration artifact.

The empirical result is tied to the declared seeds and the independently
implemented paper protocol. It cannot identify which undisclosed checkpoint,
seed, or implementation detail produced the paper's plotted curve. The verdict
therefore addresses the predefined reproducible claim contract, with this
deviation stated explicitly.
