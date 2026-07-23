# Claim 5 source audit

Paper source: arXiv `2602.02877v2`, Section 5.1 and Appendix F.4. The source
hashes and stable anchors are recorded in `.openresearch/audit/`.

The paper uses all 17,091,657 Glint360K images and 9,533,174 TreeOfLife-10M
images after feature extraction with the released ResNet-50 and CLIP ViT-B/16
encoders. It trains a bias-free linear classifier for 50 epochs with batch size
128. Every method is run with three random seeds. The exact result statement is
that SOX and SCENT are consistently better than the other methods, and SCENT
performs better than SOX on training and validation cross-entropy curves for
both datasets.

The official repository at commit
`cfbf17925754f18855f26715adeec4773aa0591d` supplies extraction and training
code but does not supply the extracted tensors. Its README instructs the user
to download the raw datasets and create `features.pt` and `labels.pt`.
