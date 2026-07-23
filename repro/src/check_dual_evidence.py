"""Independent high-precision checker for claim 1/3 raw CSV evidence."""
from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

import mpmath as mp


def main(root: Path) -> int:
    mp.mp.dps = 90
    c1_rows = list(csv.DictReader((root / "claim_1" / "proximal_cases.csv").open()))
    c1_errors = []
    c1_residuals = []
    for row in c1_rows:
        prev = mp.mpf(row["nu_prev"])
        risk = mp.mpf(row["s"])
        alpha = mp.mpf(row["alpha"])
        observed = mp.mpf(row["closed_form"])
        reference = prev + mp.log(1 + alpha * mp.exp(risk)) - mp.log(
            1 + alpha * mp.exp(prev)
        )
        derivative = (
            1
            - mp.exp(risk - observed)
            + (mp.exp(-prev) - mp.exp(-observed)) / alpha
        )
        c1_errors.append(abs(observed - reference))
        c1_residuals.append(abs(derivative))
    c1_max_error = max(c1_errors)
    c1_max_residual = max(c1_residuals)
    c1_passed = bool(c1_max_error < mp.mpf("5e-14") and c1_max_residual < mp.mpf("5e-11"))

    c3_rows = list(csv.DictReader((root / "claim_3" / "invariant_samples.csv").open()))
    c3_errors = []
    c3_breaches = 0
    for row in c3_rows:
        c0, c1 = mp.mpf(row["c0"]), mp.mpf(row["c1"])
        prev = mp.mpf(row["nu_prev"])
        risk = mp.mpf(row["s"])
        alpha = mp.mpf(row["alpha"])
        observed = mp.mpf(row["nu_new"])
        reference = prev + mp.log(1 + alpha * mp.exp(risk)) - mp.log(
            1 + alpha * mp.exp(prev)
        )
        c3_errors.append(abs(observed - reference))
        if not (c0 - mp.mpf("2e-12") <= observed <= c1 + mp.mpf("2e-12")):
            c3_breaches += 1
        if not (
            min(prev, risk) - mp.mpf("2e-12")
            <= observed
            <= max(prev, risk) + mp.mpf("2e-12")
        ):
            c3_breaches += 1
    c3_max_error = max(c3_errors)
    c3_passed = bool(c3_max_error < mp.mpf("5e-12") and c3_breaches == 0)

    payload = {
        "checker": "mpmath_90_digit_recomputation_from_raw_csv",
        "claim_1": {
            "passed": c1_passed,
            "rows": len(c1_rows),
            "max_formula_abs_error": float(c1_max_error),
            "max_first_order_residual": float(c1_max_residual),
        },
        "claim_3": {
            "passed": c3_passed,
            "rows": len(c3_rows),
            "max_formula_abs_error": float(c3_max_error),
            "breaches": c3_breaches,
        },
    }
    (root / "dual_independent_checker.json").write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n"
    )
    print(json.dumps(payload, sort_keys=True))
    return 0 if c1_passed and c3_passed else 1


if __name__ == "__main__":
    raise SystemExit(main(Path(sys.argv[1])))

