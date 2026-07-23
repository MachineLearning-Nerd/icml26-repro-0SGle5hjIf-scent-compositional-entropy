# Paper claim anchors

Source: arXiv `2602.02877v2`, hashed in `paper_source.json`. The stable ar5iv
anchors below are recorded so later contracts can distinguish the paper's
statement from the imported judge paraphrase.

## Claim 1

- Section 3, equations (5)–(7), ar5iv anchors `S3.E5`, `S3.E6`, `S3.E7`.
- Lemma 3.1 anchor `S3.Thmtheorem1`; the closed form applies to the scalar
  SPMD argmin with `alpha_t > 0`, stochastic objective
  `exp(s(w_t; zeta_t)-nu)+nu`, and Bregman generator `phi(nu)=exp(-nu)`.
- The numerically reliable log-domain expression is the paragraph at
  `S3.p5.1`. The paper says overflow “can be effectively avoided”; it does not
  quantify a universal floating-point range or compare against an
  “exponential-average baseline” in this lemma.

## Claim 2

- Assumption 3.2 anchor `S3.Thmtheorem2`: for every sampled risk, (i)
  `s_i(.;zeta)` is convex and differentiable; (ii)
  `s_i(w;zeta) in [c0,c1]` for every `w in W,zeta`; and (iii) a finite `G`
  bounds the expected squared gradient at every iteration.
- Theorem 3.6 anchor `S3.Thmtheorem6`, equation (13) anchor `S3.E13`.
  It concerns the averaged iterate and expected CERM objective gap, with
  `eta_t=eta*alpha_t` and horizon-dependent constant
  `alpha_t=alpha/sqrt(T)` satisfying the stated dual-step inequality.
- The `O(1/T^(1/4))` comparison is explicitly to the existing analysis of SCGD
  in Wang et al. (2017), not an empirical lower bound on SCGD trajectories.

## Claim 3

- Lemma 3.3 anchor `S3.Thmtheorem3`.
- Exact quantifier: if `nu_0 in [c0,c1]^n`, then for every `i in [n]` and
  every integer `t >= 1`, the SPMD coordinate update keeps
  `nu_{i,t} in [c0,c1]`; the variance terms are finite.
- This is conditional on Assumption 3.2(ii), not merely on finite inputs.

## Claim 4

- Fixed-`w` problem and `kappa` definition are in Section 4.2, beginning at
  ar5iv anchor `S4.SS2`.
- Theorem 4.3 anchor `S4.Thmtheorem3` gives an SPMD upper bound under bounded
  `s(zeta)`, a particular step size, a feasibility inequality, and sufficiently
  large `T`. Its dominant term is proportional to
  `sqrt((kappa-1)/T)`.
- The comparison to projected SGD is not part of Theorem 4.3. Lemma 4.4 and
  Theorem 4.5 in Section 4.3 give the SGD smoothness and upper bound; the
  following remark compares the *bounds* with ratio
  `1/(|nu_0-nu_*| exp(nu_*-c0))`.
- Figure 1 is a controlled Gaussian experiment; Appendix F.4 says it uses one
  million samples per `(mu,sigma)` combination.

## Claim 5

- Section 5.1 anchors `S5.SS1` and Figure 2 anchor `S5.F3`.
- The datasets are Glint360K (17 million images, about 360K classes) and
  TreeOfLife-10M (10 million images, about 160K species), using released
  ResNet-50 and CLIP ViT-B/16 features respectively.
- All methods use batch size 128, 50 epochs, three random seeds, and tuned
  method-specific hyperparameters. The text says SOX and SCENT are
  consistently better than the other named methods and SCENT is better than
  SOX on the plotted training and validation cross-entropy curves.

## Claim 6

- Section 5.2 anchor `S5.SS2`, Figure 3 anchor `S5.F4`, and Appendix F.4.
- CIFAR-10 and CIFAR-100 are converted to binary tasks; the first half of
  classes are negative, the second half positive, and 80% of positive training
  samples are removed. A ResNet-18 is pretrained for 60 epochs, then its
  backbone is frozen and the classifier is fine-tuned for 60 epochs.
- The paper reports three seeds with error bars and says SCENT is slightly
  better than SOX across both datasets and `tau` values 0.05 and 0.1. The main
  paper figure plots the training CERM surrogate loss; pAUC is the task name,
  but Section 5 does not state a numeric pAUC superiority contract.

