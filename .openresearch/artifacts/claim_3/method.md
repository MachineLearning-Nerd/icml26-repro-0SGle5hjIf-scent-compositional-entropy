# Claim 3 method

Run 4,096 coordinates for 2,048 iterations on each of four intervals, including
large positive and negative log domains. Steps span `exp(-27)` to `exp(27)`.
The implementation uses equation (7) in log space and performs no clipping or
projection. Every update is checked both against `[c0,c1]` and against the
one-step convex hull of `nu_prev` and `s`.

A separate 90-digit checker recomputes sampled raw rows. The negative control
uses the paper's comparison method—unprojected Euclidean SGD—and must leave the
interval on a constructed valid bounded-risk update.

