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

The two datasets execute across two CPU jobs because the measured combined
runtime exceeded the first job's 12-hour ceiling. CIFAR-10 final rows are
traceable to the cancelled parent run and cryptographically bound in the
continuation. Intermediate CIFAR-10 checkpoints remain in the parent run log;
only the final rows consumed by the claim checker are copied into the
continuation artifact.
