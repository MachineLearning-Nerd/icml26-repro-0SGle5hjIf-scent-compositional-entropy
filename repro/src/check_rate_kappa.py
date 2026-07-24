"""Independent checker that derives pass predicates from raw C2/C4 CSV files."""
from __future__ import annotations

import csv
import json
import math
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np
from scipy.stats import spearmanr


def main(root: Path) -> int:
    rate_rows = list(csv.DictReader((root / "claim_2" / "rate_runs.csv").open()))
    by_horizon: dict[int, list[float]] = defaultdict(list)
    margins = []
    for row in rate_rows:
        by_horizon[int(row["horizon"])].append(float(row["gap"]))
        margins.append(float(row["step_condition_margin_rho_1"]))
    horizons = np.array(sorted(by_horizon))
    means = np.array([np.mean(by_horizon[int(t)]) for t in horizons])
    slope = float(np.polyfit(np.log(horizons), np.log(np.maximum(means, 1e-15)), 1)[0])
    normalized = np.sqrt(horizons) * means
    c2_passed = bool(
        slope <= -0.20
        and means[-1] < means[0]
        and normalized.max() <= 3.0 * max(normalized[0], 1e-15)
        and min(margins) > 0
    )

    fixed_rows = list(csv.DictReader((root / "claim_4" / "fixed_w_results.csv").open()))
    by_mu: dict[float, list[dict[str, float]]] = defaultdict(list)
    max_kappa_error = 0.0
    high_sigma = True
    for row in fixed_rows:
        numeric = {
            key: float(row[key])
            for key in (
                "mu",
                "sigma",
                "sample_kappa",
                "kappa_relative_error",
                "tail_error_ratio_mean",
                "nu_star",
                "c0",
            )
        }
        numeric["tail_error_ratio_ci95_high"] = float(
            json.loads(row["tail_error_ratio_ci95"])[1]
        )
        by_mu[numeric["mu"]].append(numeric)
        max_kappa_error = max(max_kappa_error, numeric["kappa_relative_error"])
    correlations = {}
    for mu, rows in by_mu.items():
        rows.sort(key=lambda row: row["sigma"])
        correlations[str(mu)] = float(
            spearmanr(
                [row["sample_kappa"] for row in rows],
                [row["tail_error_ratio_mean"] for row in rows],
            ).statistic
        )
        high_sigma &= rows[-1]["tail_error_ratio_ci95_high"] < 1.0

    factor_rows = list(csv.DictReader((root / "claim_4" / "bound_factors.csv").open()))
    fixed_by_setting = {
        (row["mu"], row["sigma"]): row for row in fixed_rows
    }
    factor_relative_errors = []
    factors_by_mu: dict[float, list[tuple[float, float]]] = defaultdict(list)
    for row in factor_rows:
        source = fixed_by_setting[(row["mu"], row["sigma"])]
        nu_star = float(source["nu_star"])
        c0 = float(source["c0"])
        expected = 1.0 / (abs(nu_star) * math.exp(nu_star - c0))
        observed = float(row["spmd_to_sgd_bound_proportional_factor"])
        factor_relative_errors.append(abs(observed - expected) / max(abs(expected), 1e-30))
        factors_by_mu[float(row["mu"])].append(
            (float(row["nu_star_minus_c0"]), observed)
        )
    factor_monotone = all(
        all(
            right[1] < left[1]
            for left, right in zip(
                sorted(rows),
                sorted(rows)[1:],
            )
        )
        for rows in factors_by_mu.values()
    )
    max_factor_relative_error = max(factor_relative_errors)
    c4_passed = bool(
        max_kappa_error < 0.015
        and all(value <= -0.5 for value in correlations.values())
        and high_sigma
        and len(factor_rows) == len(fixed_rows)
        and max_factor_relative_error < 1e-12
        and factor_monotone
    )

    payload = {
        "checker": "independent_raw_csv_reduction",
        "claim_2": {
            "passed": c2_passed,
            "horizons": horizons.tolist(),
            "mean_gaps": means.tolist(),
            "log_log_slope": slope,
            "sqrt_t_mean_gap": normalized.tolist(),
            "minimum_step_condition_margin": min(margins),
        },
        "claim_4": {
            "passed": c4_passed,
            "rows": len(fixed_rows),
            "max_kappa_relative_error": max_kappa_error,
            "spearman_kappa_vs_error_ratio": correlations,
            "sigma_1_spmd_ci_below_sgd": high_sigma,
            "bound_factor_rows": len(factor_rows),
            "max_bound_factor_relative_error": max_factor_relative_error,
            "bound_factor_decreases_with_nu_star_minus_c0": factor_monotone,
        },
    }
    (root / "rate_kappa_independent_checker.json").write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n"
    )
    print(json.dumps(payload, sort_keys=True))
    return 0 if c2_passed and c4_passed else 1


if __name__ == "__main__":
    raise SystemExit(main(Path(sys.argv[1])))
