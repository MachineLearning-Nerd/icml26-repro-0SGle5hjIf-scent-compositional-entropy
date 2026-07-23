"""Executable contracts for SCENT paper claims 2 and 4."""
from __future__ import annotations

import csv
import json
import math
import os
import platform
import subprocess
import sys
import time
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import psutil
from scipy.optimize import minimize
from scipy.special import logsumexp
from scipy.stats import spearmanr


REPO = Path(__file__).resolve().parents[2]
ROOT = REPO / ".openresearch" / "artifacts"
C2 = ROOT / "claim_2"
C4 = ROOT / "claim_4"
SEED = 260202877


def write_json(path: Path, payload: object) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")


def stable_update(nu_prev: np.ndarray, s: np.ndarray, alpha: float) -> np.ndarray:
    log_alpha = math.log(alpha)
    return (
        nu_prev
        + np.logaddexp(0.0, log_alpha + s)
        - np.logaddexp(0.0, log_alpha + nu_prev)
    )


@dataclass
class CermProblem:
    risks: np.ndarray  # [anchors, inner, dimension]
    offsets: np.ndarray  # [anchors, inner]
    lower: float
    upper: float
    c0: float
    c1: float

    def objective_gradient(self, w: np.ndarray) -> tuple[float, np.ndarray]:
        scores = np.einsum("nqd,d->nq", self.risks, w) + self.offsets
        log_norm = logsumexp(scores, axis=1)
        objective = float(np.mean(log_norm - math.log(scores.shape[1])))
        weights = np.exp(scores - log_norm[:, None])
        gradient = np.mean(np.einsum("nq,nqd->nd", weights, self.risks), axis=0)
        return objective, gradient


def make_problem(rng: np.random.Generator) -> CermProblem:
    n, q, d = 96, 256, 12
    shared = rng.normal(size=d)
    shared /= np.linalg.norm(shared)
    shared *= 0.09
    risks = shared[None, None, :] + rng.normal(
        scale=0.18 / math.sqrt(d), size=(n, q, d)
    )
    offsets = rng.uniform(-0.15, 0.15, size=(n, q))
    lower, upper = -1.0, 1.0
    radius = np.sum(np.abs(risks), axis=2)
    c0 = float(np.min(offsets - radius))
    c1 = float(np.max(offsets + radius))
    return CermProblem(risks, offsets, lower, upper, c0, c1)


def solve_optimum(problem: CermProblem) -> tuple[np.ndarray, float, dict[str, object]]:
    d = problem.risks.shape[2]

    def fun(w: np.ndarray) -> tuple[float, np.ndarray]:
        return problem.objective_gradient(w)

    result = minimize(
        fun,
        np.zeros(d),
        method="L-BFGS-B",
        jac=True,
        bounds=[(problem.lower, problem.upper)] * d,
        options={"ftol": 1e-14, "gtol": 1e-10, "maxiter": 3000, "maxls": 50},
    )
    if not result.success:
        raise RuntimeError(f"exact convex optimum failed: {result.message}")
    optimum, gradient = problem.objective_gradient(result.x)
    projected = np.clip(result.x - gradient, problem.lower, problem.upper)
    kkt_residual = float(np.linalg.norm(result.x - projected))
    return result.x, optimum, {
        "success": bool(result.success),
        "iterations": int(result.nit),
        "objective": optimum,
        "projected_kkt_residual": kkt_residual,
    }


def run_scent(
    problem: CermProblem,
    horizon: int,
    seed: int,
    alpha_constant: float,
    eta_ratio: float,
    batch_size: int,
) -> float:
    rng = np.random.default_rng(seed)
    n, q, d = problem.risks.shape
    w = np.zeros(d)
    w_sum = np.zeros(d)
    nu = np.full(n, (problem.c0 + problem.c1) / 2.0)
    alpha_t = alpha_constant / math.sqrt(horizon)
    eta_t = eta_ratio * alpha_t
    for _ in range(horizon):
        anchors = rng.choice(n, size=batch_size, replace=False)
        inner_dual = rng.integers(q, size=batch_size)
        dual_risk = (
            np.einsum(
                "bd,bd->b",
                problem.risks[anchors, inner_dual],
                np.broadcast_to(w, (batch_size, d)),
            )
            + problem.offsets[anchors, inner_dual]
        )
        nu[anchors] = stable_update(nu[anchors], dual_risk, alpha_t)
        inner_primal = rng.integers(q, size=batch_size)
        primal_a = problem.risks[anchors, inner_primal]
        primal_s = np.einsum("bd,d->b", primal_a, w) + problem.offsets[
            anchors, inner_primal
        ]
        gradient = np.mean(np.exp(primal_s - nu[anchors])[:, None] * primal_a, axis=0)
        w_sum += w
        w = np.clip(w - eta_t * gradient, problem.lower, problem.upper)
    w_bar = w_sum / horizon
    value, _ = problem.objective_gradient(w_bar)
    return value


def bootstrap_slopes(gaps: np.ndarray, horizons: np.ndarray, rng: np.random.Generator) -> np.ndarray:
    # gaps shape [horizon, seed]
    slopes = np.empty(2000)
    n_seeds = gaps.shape[1]
    x = np.log(horizons)
    for i in range(slopes.size):
        selected = rng.integers(n_seeds, size=n_seeds)
        means = np.maximum(np.mean(gaps[:, selected], axis=1), 1e-15)
        slopes[i] = np.polyfit(x, np.log(means), 1)[0]
    return slopes


def verify_claim_2(rng: np.random.Generator) -> dict[str, object]:
    started = time.perf_counter()
    C2.mkdir(parents=True, exist_ok=True)
    problem = make_problem(rng)
    w_star, f_star, optimum = solve_optimum(problem)
    horizons = np.array([512, 2048, 8192, 32768], dtype=int)
    seeds = np.arange(20, dtype=int) + 90210
    alpha_constant = 0.5
    eta_ratio = 0.5
    batch_size = 32
    gaps = np.empty((len(horizons), len(seeds)))
    rows: list[dict[str, object]] = []
    for h_idx, horizon in enumerate(horizons):
        alpha_t = alpha_constant / math.sqrt(int(horizon))
        condition_margin = math.exp(-problem.c1) - alpha_t
        for s_idx, seed in enumerate(seeds):
            value = run_scent(
                problem,
                int(horizon),
                int(seed + 100000 * h_idx),
                alpha_constant,
                eta_ratio,
                batch_size,
            )
            gap = max(value - f_star, 0.0)
            gaps[h_idx, s_idx] = gap
            rows.append(
                {
                    "horizon": int(horizon),
                    "seed": int(seed),
                    "objective": value,
                    "optimum": f_star,
                    "gap": gap,
                    "alpha_t": alpha_t,
                    "eta_t": eta_ratio * alpha_t,
                    "step_condition_margin_rho_1": condition_margin,
                }
            )
    with (C2 / "rate_runs.csv").open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)

    means = gaps.mean(axis=1)
    ses = gaps.std(axis=1, ddof=1) / math.sqrt(gaps.shape[1])
    ci_low = np.maximum(means - 2.093 * ses, 0.0)
    ci_high = means + 2.093 * ses
    slopes = bootstrap_slopes(gaps, horizons, rng)
    slope_mean = float(np.polyfit(np.log(horizons), np.log(np.maximum(means, 1e-15)), 1)[0])
    slope_ci = [float(np.quantile(slopes, 0.025)), float(np.quantile(slopes, 0.975))]
    normalized = np.sqrt(horizons) * means
    normalized_cap_ratio = float(normalized.max() / max(normalized[0], 1e-15))
    step_conditions_hold = bool(
        all(alpha_constant / math.sqrt(int(t)) < math.exp(-problem.c1) for t in horizons)
    )

    initial, _ = problem.objective_gradient(np.zeros(problem.risks.shape[2]))
    initial_gap = initial - f_star
    negative_gaps = np.full_like(horizons, initial_gap, dtype=float)
    negative_slope = float(
        np.polyfit(np.log(horizons), np.log(negative_gaps), 1)[0]
    )
    negative_rejected = bool(
        negative_slope > -0.05
        and not (negative_gaps[-1] < 0.8 * negative_gaps[0])
    )
    write_json(
        C2 / "negative_control.json",
        {
            "control": "zero_primal_step",
            "horizons": horizons.tolist(),
            "gaps": negative_gaps.tolist(),
            "log_log_slope": negative_slope,
            "rejected_as_expected": negative_rejected,
        },
    )

    passed = bool(
        optimum["projected_kkt_residual"] < 1e-7
        and step_conditions_hold
        and slope_ci[1] <= -0.20
        and ci_high[-1] < ci_low[0]
        and normalized_cap_ratio <= 3.0
        and negative_rejected
    )
    summary = {
        "verdict": "VERIFIED" if passed else "FALSIFIED",
        "passed": passed,
        "problem": {
            "anchors": int(problem.risks.shape[0]),
            "inner_support": int(problem.risks.shape[1]),
            "dimension": int(problem.risks.shape[2]),
            "domain": [problem.lower, problem.upper],
            "c0": problem.c0,
            "c1": problem.c1,
            "convex_differentiable": True,
            "bounded_gradient_second_moment": True,
        },
        "optimum": optimum,
        "w_star": w_star.tolist(),
        "horizons": horizons.tolist(),
        "seeds_per_horizon": len(seeds),
        "mean_gaps": means.tolist(),
        "ci95_low": ci_low.tolist(),
        "ci95_high": ci_high.tolist(),
        "sqrt_t_mean_gap": normalized.tolist(),
        "sqrt_t_cap_ratio_to_first": normalized_cap_ratio,
        "log_log_slope": slope_mean,
        "bootstrap_slope_ci95": slope_ci,
        "step_conditions_hold": step_conditions_hold,
        "negative_control_rejected": negative_rejected,
        "runtime_seconds": time.perf_counter() - started,
    }
    write_json(C2 / "raw_summary.json", summary)
    return summary


def objective_gap(nu: np.ndarray, m: float, nu_star: float) -> np.ndarray:
    return m * np.exp(-nu) + nu - 1.0 - nu_star


def simulate_fixed_w(
    samples: np.ndarray,
    mu: float,
    sigma: float,
    seed: int,
    trajectories: int = 64,
    steps: int = 3000,
) -> tuple[dict[str, object], list[dict[str, object]]]:
    rng = np.random.default_rng(seed)
    z = np.exp(samples)
    m = float(z.mean())
    second = float(np.mean(z * z))
    kappa = second / (m * m)
    nu_star = math.log(m)
    c0 = float(min(samples.min(), 0.0))
    c1 = float(max(samples.max(), 0.0))
    nu_spmd = np.zeros(trajectories)
    nu_sgd = np.zeros(trajectories)
    log_alpha_spmd = -6.0 if mu == -1.0 else 3.0
    alpha_spmd = math.exp(log_alpha_spmd)
    alpha_sgd = 1.0
    trace_rows: list[dict[str, object]] = []
    spmd_tail_per_trajectory = np.zeros(trajectories)
    sgd_tail_per_trajectory = np.zeros(trajectories)
    tail_start = steps // 2
    for t in range(steps):
        picked = samples[rng.integers(samples.size, size=trajectories)]
        nu_spmd = stable_update(nu_spmd, picked, alpha_spmd)
        gradient = 1.0 - np.exp(picked - nu_sgd)
        nu_sgd = np.clip(nu_sgd - alpha_sgd * gradient, c0, c1)
        squared_spmd = (nu_spmd - nu_star) ** 2
        squared_sgd = (nu_sgd - nu_star) ** 2
        if t >= tail_start:
            spmd_tail_per_trajectory += squared_spmd / (steps - tail_start)
            sgd_tail_per_trajectory += squared_sgd / (steps - tail_start)
        if t in (0, 9, 99, 499, 999, 1999, 2999):
            trace_rows.append(
                {
                    "mu": mu,
                    "sigma": sigma,
                    "iteration": t + 1,
                    "spmd_squared_error_mean": float(squared_spmd.mean()),
                    "sgd_squared_error_mean": float(squared_sgd.mean()),
                    "spmd_objective_gap_mean": float(objective_gap(nu_spmd, m, nu_star).mean()),
                    "sgd_objective_gap_mean": float(objective_gap(nu_sgd, m, nu_star).mean()),
                }
            )
    ratio_per_trajectory = spmd_tail_per_trajectory / np.maximum(
        sgd_tail_per_trajectory, 1e-30
    )
    result = {
        "mu": mu,
        "sigma": sigma,
        "sample_size": int(samples.size),
        "trajectories": trajectories,
        "iterations": steps,
        "sample_mean_z": m,
        "sample_kappa": kappa,
        "analytic_gaussian_kappa": math.exp(sigma * sigma),
        "kappa_relative_error": abs(kappa - math.exp(sigma * sigma))
        / math.exp(sigma * sigma),
        "nu_star": nu_star,
        "c0": c0,
        "c1": c1,
        "spmd_log_alpha": log_alpha_spmd,
        "sgd_alpha": alpha_sgd,
        "tail_spmd_squared_error_mean": float(spmd_tail_per_trajectory.mean()),
        "tail_sgd_squared_error_mean": float(sgd_tail_per_trajectory.mean()),
        "tail_error_ratio_mean": float(ratio_per_trajectory.mean()),
        "tail_error_ratio_ci95": [
            float(np.quantile(ratio_per_trajectory, 0.025)),
            float(np.quantile(ratio_per_trajectory, 0.975)),
        ],
        "spmd_better_fraction": float(np.mean(ratio_per_trajectory < 1.0)),
    }
    return result, trace_rows


def verify_claim_4(rng: np.random.Generator) -> dict[str, object]:
    started = time.perf_counter()
    C4.mkdir(parents=True, exist_ok=True)
    mus = [-1.0, -10.0]
    sigmas = [0.1, 0.3, 1.0]
    results: list[dict[str, object]] = []
    traces: list[dict[str, object]] = []
    # One million points for every combination, matching Appendix F.4.
    for mu_index, mu in enumerate(mus):
        for sigma_index, sigma in enumerate(sigmas):
            samples = rng.normal(mu, sigma, size=1_000_000)
            result, trace = simulate_fixed_w(
                samples,
                mu,
                sigma,
                SEED + mu_index * 100 + sigma_index,
            )
            results.append(result)
            traces.extend(trace)

    with (C4 / "fixed_w_results.csv").open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(results[0]))
        writer.writeheader()
        writer.writerows(results)
    with (C4 / "fixed_w_traces.csv").open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(traces[0]))
        writer.writeheader()
        writer.writerows(traces)

    monotone_correlations = {}
    high_sigma_better = True
    for mu in mus:
        subset = sorted((r for r in results if r["mu"] == mu), key=lambda r: r["sigma"])
        correlation = float(
            spearmanr(
                [r["sample_kappa"] for r in subset],
                [r["tail_error_ratio_mean"] for r in subset],
            ).statistic
        )
        monotone_correlations[str(mu)] = correlation
        high_sigma_better &= bool(subset[-1]["tail_error_ratio_ci95"][1] < 1.0)
    kappa_accuracy = max(float(r["kappa_relative_error"]) for r in results)
    ratio_by = {(float(r["mu"]), float(r["sigma"])): float(r["tail_error_ratio_mean"]) for r in results}
    mu_relative_differences = [
        abs(ratio_by[(-1.0, sigma)] - ratio_by[(-10.0, sigma)])
        / max((ratio_by[(-1.0, sigma)] + ratio_by[(-10.0, sigma)]) / 2.0, 1e-30)
        for sigma in sigmas
    ]

    # Recompute the bound-factor dependence from Theorem 4.3 / Theorem 4.5
    # on bounded empirical distributions. The proportional factor is the exact
    # expression stated by the paper's comparison remark.
    factor_rows = []
    for result in results:
        nu0 = 0.0
        factor = 1.0 / (
            abs(nu0 - float(result["nu_star"]))
            * math.exp(float(result["nu_star"]) - float(result["c0"]))
        )
        factor_rows.append(
            {
                "mu": result["mu"],
                "sigma": result["sigma"],
                "kappa": result["sample_kappa"],
                "nu_star_minus_c0": float(result["nu_star"]) - float(result["c0"]),
                "spmd_to_sgd_bound_proportional_factor": factor,
            }
        )
    with (C4 / "bound_factors.csv").open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(factor_rows[0]))
        writer.writeheader()
        writer.writerows(factor_rows)

    # Negative control is the legacy repository's wrong variable: it computes
    # a ratio from raw logits rather than z=exp(s). It must not agree with the
    # paper's kappa on the declared Gaussian setting.
    control_samples = rng.normal(-1.0, 1.0, size=1_000_000)
    wrong_kappa = float(
        np.mean(control_samples**2) / max(np.mean(control_samples) ** 2, 1e-30)
    )
    correct_z = np.exp(control_samples)
    correct_kappa = float(np.mean(correct_z**2) / np.mean(correct_z) ** 2)
    negative_rejected = bool(abs(wrong_kappa - correct_kappa) / correct_kappa > 0.1)
    write_json(
        C4 / "negative_control.json",
        {
            "control": "legacy_raw_logit_moment_ratio",
            "wrong_kappa": wrong_kappa,
            "correct_exp_risk_kappa": correct_kappa,
            "rejected_as_expected": negative_rejected,
        },
    )

    passed = bool(
        kappa_accuracy < 0.015
        and all(value <= -0.5 for value in monotone_correlations.values())
        and high_sigma_better
        and max(mu_relative_differences) < 0.50
        and negative_rejected
    )
    summary = {
        "verdict": "VERIFIED" if passed else "FALSIFIED",
        "passed": passed,
        "sample_protocol": "1,000,000 Gaussian points per (mu,sigma), as Appendix F.4",
        "settings": results,
        "max_kappa_relative_error": kappa_accuracy,
        "spearman_kappa_vs_error_ratio": monotone_correlations,
        "sigma_1_spmd_ci_below_sgd": high_sigma_better,
        "mu_invariance_relative_differences": mu_relative_differences,
        "negative_control_rejected": negative_rejected,
        "scope_note": "Theorem 4.3 is the SPMD bound. The SGD factor comes from Theorem 4.5 and the following remark, not Theorem 4.3 alone.",
        "runtime_seconds": time.perf_counter() - started,
    }
    write_json(C4 / "raw_summary.json", summary)
    return summary


def write_eval(claim_dir: Path, claim: int, summary: dict[str, object]) -> None:
    (claim_dir / "EVAL.md").write_text(
        "\n".join(
            [
                f"# Claim {claim} evaluation",
                "",
                f"Verdict: **{summary['verdict']}**",
                "",
                "```json",
                json.dumps(summary, indent=2, sort_keys=True),
                "```",
                "",
                "See `source_audit.md` and `limitations.md` for exact scope.",
            ]
        )
        + "\n"
    )


def main() -> int:
    started = time.perf_counter()
    rng = np.random.default_rng(SEED)
    c2 = verify_claim_2(rng)
    c4 = verify_claim_4(rng)
    command = "uv run --frozen python repro/src/verify_scent.py\n"
    environment = {
        "git_sha": subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=REPO, text=True
        ).strip(),
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
    for claim_dir in (C2, C4):
        (claim_dir / "command.txt").write_text(command)
        write_json(claim_dir / "environment.json", environment)

    checker = subprocess.run(
        [sys.executable, str(Path(__file__).with_name("check_rate_kappa.py")), str(ROOT)],
        cwd=REPO,
        text=True,
        capture_output=True,
    )
    print(checker.stdout, end="")
    if checker.stderr:
        print(checker.stderr, file=sys.stderr, end="")
    checker_payload = json.loads((ROOT / "rate_kappa_independent_checker.json").read_text())
    c2["independent_checker_passed"] = checker_payload["claim_2"]["passed"]
    c4["independent_checker_passed"] = checker_payload["claim_4"]["passed"]
    c2["passed"] = bool(c2["passed"] and c2["independent_checker_passed"])
    c4["passed"] = bool(c4["passed"] and c4["independent_checker_passed"])
    c2["verdict"] = "VERIFIED" if c2["passed"] else "FALSIFIED"
    c4["verdict"] = "VERIFIED" if c4["passed"] else "FALSIFIED"
    write_json(C2 / "raw_summary.json", c2)
    write_json(C4 / "raw_summary.json", c4)
    write_eval(C2, 2, c2)
    write_eval(C4, 4, c4)

    all_passed = bool(c2["passed"] and c4["passed"] and checker.returncode == 0)
    print("\n" + "=" * 78)
    print("RIGOROUS RATE / KAPPA CONTRACT SUMMARY")
    print("=" * 78)
    print(
        f"CLAIM 2 {c2['verdict']}: horizons={c2['horizons']}; "
        f"mean gaps={[f'{x:.3e}' for x in c2['mean_gaps']]}; "
        f"slope={c2['log_log_slope']:.3f}, "
        f"bootstrap95={c2['bootstrap_slope_ci95']}; "
        f"negative control rejected={c2['negative_control_rejected']}"
    )
    print(
        f"CLAIM 4 {c4['verdict']}: max kappa relative error="
        f"{c4['max_kappa_relative_error']:.3e}; "
        f"kappa/error correlations={c4['spearman_kappa_vs_error_ratio']}; "
        f"sigma=1 SPMD better={c4['sigma_1_spmd_ci_below_sgd']}; "
        f"negative control rejected={c4['negative_control_rejected']}"
    )
    print(f"INDEPENDENT CHECKER: {'PASS' if checker.returncode == 0 else 'FAIL'}")
    print(f"RUNTIME_SECONDS={time.perf_counter() - started:.3f}")
    print(f"RIGOROUS_RATE_KAPPA_SUITE={'PASS' if all_passed else 'FAIL'}")
    return 0 if all_passed else 1


if __name__ == "__main__":
    raise SystemExit(main())

