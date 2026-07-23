# Claim 6 source audit

Paper source: arXiv `2602.02877v2`, Section 5.2, Figure 3, Algorithm 4, and
Appendix F.4. CIFAR-10/100 are made binary by mapping the first half of classes
to negative and the second half to positive, then removing 80% of positive
training examples. A ResNet-18 is pretrained for 60 epochs with binary
cross-entropy; its classifier is reset and its backbone frozen before 60
fine-tuning epochs. The paper reports three seeds at tau 0.05 and 0.1.

Released code was audited at SCENT commit
`cfbf17925754f18855f26715adeec4773aa0591d`. The authoritative pAUC inputs used
for this port have SHA-256 hashes:

- `pauc/main.py`: `835bef8616dfdf92f23aabfcd38bbac807ffec67efa59ac1aff0eeeb2f0097e0`
- `pauc/libauc/losses/lsp.py`: `baab978b28f701dd283241d1e386b7616239e358cb91b25ad4e04ec0333850f3`
- `pauc/libauc/models/resnet.py`: `494949f9c7a160d76e54c007f4b228bf135bf9946085f9fc6469861c1dfb1202`
- `pauc/libauc/sampler/sampler.py`: `a2926b3002b84487c4d8ebd5ea2e6662582ac15d4d7233b99262b4868f29aae6`

The repository vendors the required `lsp.py` loss implementation even though
its pAUC README instructs users to install public `libauc==1.2.0`, whose wheel
does not contain that module. The reproduction ports the vendored source
directly instead of silently substituting a different published loss.

The canonical Toronto archive endpoint stalled at 0.0% for 16.5 minutes in
local run `cb02789f-bcda-4b9a-9850-49284820abe9`. The acquisition-only child
uses the open-data records at
`https://scidata.sjtu.edu.cn/records/h0yqt-ta634` (CIFAR-10) and
`https://scidata.sjtu.edu.cn/records/xk2s3-v1e12` (CIFAR-100). The verifier
refuses to continue unless the downloaded archives match torchvision's
canonical MD5 values `c58f30108f718f92721af3b95e74349a` and
`eb9058c3a382ffc7106e4002c42a8d85`, respectively.

The exact prose claim is that SOX and SCENT obtain the best training-loss
results and SCENT is slightly better than SOX. Figure-vector extraction gives
the following epoch-60 SCENT-minus-SOX mean differences:

| Dataset | tau | Difference |
|---|---:|---:|
| CIFAR-10 | 0.05 | -0.0011407 |
| CIFAR-10 | 0.1 | -0.0009193 |
| CIFAR-100 | 0.05 | -0.0012841 |
| CIFAR-100 | 0.1 | -0.0001446 |

The paper says the squared-hinge margin is 0.5. The released example commands
omit `--margin`, whose code default is 1.0; the plotted scale is also consistent
with 1.0. This reproduction follows the paper text and records the released-code
discrepancy rather than silently choosing the default.
