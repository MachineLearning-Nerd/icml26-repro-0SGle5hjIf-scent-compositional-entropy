"""Rigorous executable contracts for SCENT paper claims 1 and 3.

This suite tests the exact scalar SPMD argmin and the Lemma 3.3 interval
invariant. It deliberately does not use the clipping in the legacy toy code.
"""
from __future__ import annotations

import csv
import json
import math
import os
import platform
import subprocess
import sys
import time
from pathlib import Path

import mpmath as mp
import numpy as np
import psutil
from scipy.optimize import minimize_scalar


REPO = Path(__file__).resolve().parents[2]
ROOT = REPO / ".openresearch" / "artifacts"
C1 = ROOT / "claim_1"
C3 = ROOT / "claim_3"
SEED = 260202877


def stable_update(nu_prev: np.ndarray, s: np.ndarray, alpha: np.ndarray) -> np.ndarray:
    """Equation (7) in a stable log-domain form."""
    log_alpha = np.log(alpha)
    return (
        nu_prev
        + np.logaddexp(0.0, log_alpha + s)
        - np.logaddexp(0.0, log_alpha + nu_prev)
    )


def prox_objective(v: float, nu_prev: float, s: float, alpha: float) -> float:
    bregman = (
        math.exp(-v)
        - math.exp(-nu_prev)
        + math.exp(-nu_prev) * (v - nu_prev)
    )
    return math.exp(s - v) + v + bregman / alpha


def write_json(path: Path, payload: object) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")


def git_sha() -> str:
    return subprocess.check_output(
        ["git", "rev-parse", "HEAD"], cwd=REPO, text=True
    ).strip()


def verify_claim_1(rng: np.random.Generator) -> dict[str, object]:
    started = time.perf_counter()
    C1.mkdir(parents=True, exist_ok=True)

    # Moderate cases admit an independent numerical minimization of the exact
    # proximal objective without any overflow.
    n_moderate = 512
    nu_prev = rng.uniform(-8.0, 8.0, n_moderate)
    s = rng.uniform(-8.0, 8.0, n_moderate)
    alpha = np.exp(rng.uniform(-6.0, 6.0, n_moderate))
    closed = stable_update(nu_prev, s, alpha)
    solved = np.empty(n_moderate)
    objective_gap = np.empty(n_moderate)
    for i in range(n_moderate):
        result = minimize_scalar(
            prox_objective,
            args=(float(nu_prev[i]), float(s[i]), float(alpha[i])),
            bracket=(float(closed[i] - 1.0), float(closed[i]), float(closed[i] + 1.0)),
            method="brent",
            options={"xtol": 1e-13, "maxiter": 1000},
        )
        if not result.success:
            raise RuntimeError(f"independent proximal solve failed for case {i}")
        solved[i] = result.x
        objective_gap[i] = prox_objective(
            float(closed[i]), float(nu_prev[i]), float(s[i]), float(alpha[i])
        ) - result.fun

    moderate_error = np.abs(closed - solved)
    with (C1 / "proximal_cases.csv").open("w", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(
            [
                "case",
                "nu_prev",
                "s",
                "alpha",
                "closed_form",
                "independent_argmin",
                "abs_error",
                "objective_gap",
            ]
        )
        for i in range(n_moderate):
            writer.writerow(
                [
                    i,
                    nu_prev[i],
                    s[i],
                    alpha[i],
                    closed[i],
                    solved[i],
                    moderate_error[i],
                    objective_gap[i],
                ]
            )

    # Wide dynamic range: compare the float64 log-domain expression to an
    # 80-digit implementation of the paper's formula.
    stress_values = np.array(
        [-10000.0, -2000.0, -1000.0, -710.0, -100.0, 0.0, 100.0, 710.0, 1000.0, 2000.0, 10000.0]
    )
    stress_rows: list[dict[str, object]] = []
    mp.mp.dps = 80
    for i in range(400):
        prev = float(rng.choice(stress_values) + rng.uniform(-0.25, 0.25))
        risk = float(rng.choice(stress_values) + rng.uniform(-0.25, 0.25))
        log_a = float(rng.uniform(-50.0, 50.0))
        step = math.exp(log_a)
        observed = float(
            stable_update(np.array([prev]), np.array([risk]), np.array([step]))[0]
        )
        reference = (
            mp.mpf(prev)
            + mp.log(1 + mp.mpf(step) * mp.exp(mp.mpf(risk)))
            - mp.log(1 + mp.mpf(step) * mp.exp(mp.mpf(prev)))
        )
        abs_error = abs(mp.mpf(observed) - reference)
        stress_rows.append(
            {
                "case": i,
                "nu_prev": prev,
                "s": risk,
                "alpha": step,
                "stable": observed,
                "mp_reference": mp.nstr(reference, 30),
                "abs_error": float(abs_error),
            }
        )
    with (C1 / "stress_cases.csv").open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(stress_rows[0]))
        writer.writeheader()
        writer.writerows(stress_rows)

    # Negative control: the literal exp/log implementation should be rejected
    # on the same extreme cases because it overflows or becomes NaN.
    prev_neg = np.array([1000.0, -1000.0, 10000.0, -10000.0])
    s_neg = np.array([10000.0, 10000.0, -10000.0, -10000.0])
    a_neg = np.array([1.0, 1e20, 1.0, 1e-20])
    with np.errstate(over="ignore", invalid="ignore", divide="ignore"):
        naive = (
            prev_neg
            + np.log(1.0 + a_neg * np.exp(s_neg))
            - np.log(1.0 + a_neg * np.exp(prev_neg))
        )
    stable_neg = stable_update(prev_neg, s_neg, a_neg)
    negative_rejected = bool((~np.isfinite(naive)).any() and np.isfinite(stable_neg).all())
    write_json(
        C1 / "negative_control.json",
        {
            "control": "naive_exp_then_log",
            "expected": "at least one non-finite result while stable update stays finite",
            "naive": [None if not np.isfinite(v) else float(v) for v in naive],
            "stable": stable_neg.tolist(),
            "rejected_as_expected": negative_rejected,
        },
    )

    max_moderate_error = float(moderate_error.max())
    max_stress_error = float(max(row["abs_error"] for row in stress_rows))
    passed = bool(
        max_moderate_error <= 2e-7
        and float(np.max(np.abs(objective_gap))) <= 1e-10
        and max_stress_error <= 5e-12
        and negative_rejected
    )
    summary = {
        "verdict": "VERIFIED" if passed else "FALSIFIED",
        "passed": passed,
        "moderate_cases": n_moderate,
        "stress_cases": len(stress_rows),
        "max_argmin_abs_error": max_moderate_error,
        "max_objective_gap_abs": float(np.max(np.abs(objective_gap))),
        "max_mp_abs_error": max_stress_error,
        "stable_all_finite": bool(all(math.isfinite(float(row["stable"])) for row in stress_rows)),
        "negative_control_rejected": negative_rejected,
        "runtime_seconds": time.perf_counter() - started,
    }
    write_json(C1 / "raw_summary.json", summary)
    return summary


def verify_claim_3(rng: np.random.Generator) -> dict[str, object]:
    started = time.perf_counter()
    C3.mkdir(parents=True, exist_ok=True)
    intervals = [
        (-1000.0, -900.0),
        (-20.0, 10.0),
        (0.0, 0.001),
        (900.0, 1000.0),
    ]
    n = 4096
    steps = 2048
    sampled_rows: list[dict[str, float | int]] = []
    interval_results: list[dict[str, object]] = []
    global_local_breach = 0.0
    for interval_index, (c0, c1) in enumerate(intervals):
        nu = rng.uniform(c0, c1, n)
        nu[0], nu[1] = c0, c1
        min_seen = float(nu.min())
        max_seen = float(nu.max())
        breaches = 0
        for t in range(steps):
            risk = rng.uniform(c0, c1, n)
            if t % 4 == 0:
                risk[0], risk[1] = c0, c1
            step = np.exp(rng.uniform(-27.0, 27.0, n))
            updated = stable_update(nu, risk, step)
            lower = np.minimum(nu, risk)
            upper = np.maximum(nu, risk)
            local_breach = max(
                float(np.max(lower - updated)), float(np.max(updated - upper)), 0.0
            )
            global_local_breach = max(global_local_breach, local_breach)
            breaches += int(np.count_nonzero((updated < c0 - 2e-12) | (updated > c1 + 2e-12)))
            min_seen = min(min_seen, float(updated.min()))
            max_seen = max(max_seen, float(updated.max()))
            if t in (0, steps // 2, steps - 1):
                for j in rng.choice(n, size=16, replace=False):
                    sampled_rows.append(
                        {
                            "interval": interval_index,
                            "step_index": t,
                            "c0": c0,
                            "c1": c1,
                            "nu_prev": float(nu[j]),
                            "s": float(risk[j]),
                            "alpha": float(step[j]),
                            "nu_new": float(updated[j]),
                        }
                    )
            nu = updated
        interval_results.append(
            {
                "c0": c0,
                "c1": c1,
                "coordinates": n,
                "iterations": steps,
                "updates": n * steps,
                "breaches": breaches,
                "min_seen": min_seen,
                "max_seen": max_seen,
            }
        )

    with (C3 / "invariant_samples.csv").open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(sampled_rows[0]))
        writer.writeheader()
        writer.writerows(sampled_rows)

    # Negative control: an unprojected Euclidean SGD dual step has no interval
    # invariant. This is the comparison made immediately after Lemma 3.3.
    c0, c1 = 0.0, 1.0
    nu0, risk, beta = 0.0, 1.0, 10.0
    asgd = nu0 - beta * (1.0 - math.exp(risk - nu0))
    negative_rejected = bool(asgd > c1)
    write_json(
        C3 / "negative_control.json",
        {
            "control": "unprojected_euclidean_sgd_dual_step",
            "c0": c0,
            "c1": c1,
            "nu_0": nu0,
            "s": risk,
            "step_size": beta,
            "nu_1": asgd,
            "rejected_as_expected": negative_rejected,
        },
    )

    total_updates = sum(int(item["updates"]) for item in interval_results)
    total_breaches = sum(int(item["breaches"]) for item in interval_results)
    passed = bool(
        total_breaches == 0
        and global_local_breach <= 2e-12
        and negative_rejected
    )
    summary = {
        "verdict": "VERIFIED" if passed else "FALSIFIED",
        "passed": passed,
        "interval_results": interval_results,
        "total_updates": total_updates,
        "total_interval_breaches": total_breaches,
        "max_one_step_convex_hull_breach": global_local_breach,
        "negative_control_rejected": negative_rejected,
        "runtime_seconds": time.perf_counter() - started,
        "note": "No clipping or projection is used by the SPMD update.",
    }
    write_json(C3 / "raw_summary.json", summary)
    return summary


def write_eval(claim_dir: Path, claim: int, summary: dict[str, object]) -> None:
    lines = [
        f"# Claim {claim} evaluation",
        "",
        f"Verdict: **{summary['verdict']}**",
        "",
        "The verifier returned success only because all contract predicates and",
        "the independent checker passed, while the deliberately invalid negative",
        "control was rejected.",
        "",
        "```json",
        json.dumps(summary, indent=2, sort_keys=True),
        "```",
        "",
        "See `limitations.md` for the scope of this verdict.",
    ]
    (claim_dir / "EVAL.md").write_text("\n".join(lines) + "\n")


def main() -> int:
    started = time.perf_counter()
    rng = np.random.default_rng(SEED)
    c1 = verify_claim_1(rng)
    c3 = verify_claim_3(rng)

    command = "uv run --frozen python repro/src/verify_scent.py\n"
    environment = {
        "git_sha": git_sha(),
        "seed": SEED,
        "python": sys.version,
        "platform": platform.platform(),
        "processor": platform.processor(),
        "logical_cpu_count": psutil.cpu_count(logical=True),
        "physical_cpu_count": psutil.cpu_count(logical=False),
        "memory_bytes": psutil.virtual_memory().total,
        "numpy": np.__version__,
        "scipy": __import__("scipy").__version__,
        "run_command": command.strip(),
    }
    for claim_dir in (C1, C3):
        (claim_dir / "command.txt").write_text(command)
        write_json(claim_dir / "environment.json", environment)

    checker = subprocess.run(
        [sys.executable, str(Path(__file__).with_name("check_dual_evidence.py")), str(ROOT)],
        cwd=REPO,
        text=True,
        capture_output=True,
    )
    print(checker.stdout, end="")
    if checker.stderr:
        print(checker.stderr, file=sys.stderr, end="")
    checker_payload = json.loads((ROOT / "dual_independent_checker.json").read_text())
    c1["independent_checker_passed"] = checker_payload["claim_1"]["passed"]
    c3["independent_checker_passed"] = checker_payload["claim_3"]["passed"]
    c1["passed"] = bool(c1["passed"] and c1["independent_checker_passed"])
    c3["passed"] = bool(c3["passed"] and c3["independent_checker_passed"])
    c1["verdict"] = "VERIFIED" if c1["passed"] else "FALSIFIED"
    c3["verdict"] = "VERIFIED" if c3["passed"] else "FALSIFIED"
    write_json(C1 / "raw_summary.json", c1)
    write_json(C3 / "raw_summary.json", c3)
    write_eval(C1, 1, c1)
    write_eval(C3, 3, c3)

    all_passed = bool(c1["passed"] and c3["passed"] and checker.returncode == 0)
    print("\n" + "=" * 78)
    print("RIGOROUS DUAL CONTRACT SUMMARY")
    print("=" * 78)
    print(
        f"CLAIM 1 {c1['verdict']}: {c1['moderate_cases']} independent argmins; "
        f"{c1['stress_cases']} high-precision stress cases; "
        f"max argmin error={c1['max_argmin_abs_error']:.3e}; "
        f"negative control rejected={c1['negative_control_rejected']}"
    )
    print(
        f"CLAIM 3 {c3['verdict']}: {c3['total_updates']} unprojected SPMD updates; "
        f"interval breaches={c3['total_interval_breaches']}; "
        f"negative control rejected={c3['negative_control_rejected']}"
    )
    print(f"INDEPENDENT CHECKER: {'PASS' if checker.returncode == 0 else 'FAIL'}")
    print(f"RUNTIME_SECONDS={time.perf_counter() - started:.3f}")
    print(f"RIGOROUS_DUAL_SUITE={'PASS' if all_passed else 'FAIL'}")
    return 0 if all_passed else 1


if __name__ == "__main__":
    raise SystemExit(main())

