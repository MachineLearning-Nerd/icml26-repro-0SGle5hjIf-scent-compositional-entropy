# Claim 2 evaluation

Verdict: **VERIFIED**

```json
{
  "bootstrap_slope_ci95": [
    -0.454951697922958,
    -0.4540368747922728
  ],
  "ci95_high": [
    0.08692636203117919,
    0.04934546133529754,
    0.025996020920609483,
    0.013163386975446714
  ],
  "ci95_low": [
    0.08654181188177933,
    0.04921760006303095,
    0.025906285647276723,
    0.013137285883027974
  ],
  "horizons": [
    512,
    2048,
    8192,
    32768
  ],
  "independent_checker_passed": true,
  "log_log_slope": -0.4544873280713293,
  "mean_gaps": [
    0.08673408695647926,
    0.049281530699164244,
    0.025951153283943103,
    0.013150336429237344
  ],
  "negative_control_rejected": true,
  "optimum": {
    "iterations": 4,
    "objective": -0.21800214960463773,
    "projected_kkt_residual": 1.6293077997886485e-12,
    "success": true
  },
  "passed": true,
  "problem": {
    "anchors": 96,
    "bounded_gradient_second_moment": true,
    "c0": -1.1846161642123691,
    "c1": 1.1537042587503339,
    "convex_differentiable": true,
    "dimension": 12,
    "domain": [
      -1.0,
      1.0
    ],
    "inner_support": 256
  },
  "runtime_seconds": 373.63645275000454,
  "seeds_per_horizon": 20,
  "sqrt_t_cap_ratio_to_first": 1.212933635730627,
  "sqrt_t_mean_gap": [
    1.9625683535024054,
    2.2302274908564517,
    2.348830267736027,
    2.380465168383543
  ],
  "step_conditions_hold": true,
  "verdict": "VERIFIED",
  "w_star": [
    -1.0,
    -0.3197336681074114,
    -1.0,
    -1.0,
    1.0,
    1.0,
    -1.0,
    -1.0,
    1.0,
    -1.0,
    -1.0,
    1.0
  ]
}
```

See `source_audit.md` and `limitations.md` for exact scope.
