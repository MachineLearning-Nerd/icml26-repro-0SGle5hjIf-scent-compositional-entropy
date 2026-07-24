"""Render the report figures from committed reproduction evidence."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[2]
ARTIFACTS = ROOT / ".openresearch" / "artifacts"
COLORS = {
    "verified": "#16856a",
    "falsified": "#c44e52",
    "blocked": "#d18f16",
    "neutral": "#475569",
    "paper": "#7c3aed",
}


def style() -> None:
    plt.rcParams.update(
        {
            "figure.dpi": 150,
            "savefig.dpi": 180,
            "font.size": 11,
            "axes.titlesize": 14,
            "axes.labelsize": 11,
            "axes.spines.top": False,
            "axes.spines.right": False,
            "axes.grid": True,
            "grid.alpha": 0.2,
        }
    )


def save(fig: plt.Figure, output: Path, name: str) -> None:
    output.mkdir(parents=True, exist_ok=True)
    fig.tight_layout()
    fig.savefig(output / name, bbox_inches="tight", facecolor="white")
    plt.close(fig)


def paired_results(metric_key: str) -> tuple[list[str], np.ndarray, np.ndarray, np.ndarray]:
    result = json.loads(
        (ARTIFACTS / "claim_6" / "independent_checker_output.json").read_text()
    )
    settings = result[metric_key]
    order = [
        "cifar10:tau=0.05",
        "cifar10:tau=0.1",
        "cifar100:tau=0.05",
        "cifar100:tau=0.1",
    ]
    means = np.array([settings[key]["mean_difference"] for key in order])
    lows = np.array([settings[key]["bootstrap95"][0] for key in order])
    highs = np.array([settings[key]["bootstrap95"][1] for key in order])
    labels = ["CIFAR-10 · τ=.05", "CIFAR-10 · τ=.10", "CIFAR-100 · τ=.05", "CIFAR-100 · τ=.10"]
    return labels, means, lows, highs


def claim6_objective(output: Path) -> None:
    labels, means, lows, highs = paired_results("settings")
    y = np.arange(len(labels))
    fig, ax = plt.subplots(figsize=(10.2, 5.4))
    ax.axvspan(-0.002, 0.002, color="#dbeafe", alpha=0.9, label="predeclared equivalence band")
    ax.axvline(0, color="#111827", linewidth=1)
    colors = [COLORS["falsified"] if low > 0.002 else COLORS["verified"] if high < 0 else COLORS["neutral"] for low, high in zip(lows, highs)]
    for mean, low, high, position, color in zip(means, lows, highs, y, colors):
        ax.errorbar(
            mean,
            position,
            xerr=[[mean - low], [high - mean]],
            fmt="none",
            ecolor=color,
            elinewidth=3,
            capsize=6,
        )
    ax.scatter(means, y, c=colors, s=75, zorder=3)
    for i, mean in enumerate(means):
        ax.annotate(
            f"{mean:+.4f}",
            (mean, i),
            xytext=(8, 0),
            textcoords="offset points",
            ha="left",
            va="center",
            fontsize=10,
        )
    ax.set_yticks(y, labels)
    ax.invert_yaxis()
    ax.set_xlabel("epoch-60 training objective: SCENT − SOX  (lower is better)")
    ax.set_title("The preregistered CIFAR contract is contradicted in one setting")
    ax.legend(loc="lower right", frameon=False)
    save(fig, output, "claim6_objective.png")


def claim6_pauc(output: Path) -> None:
    labels, means, lows, highs = paired_results("secondary_test_pauc_settings")
    y = np.arange(len(labels))
    fig, ax = plt.subplots(figsize=(10.2, 5.2))
    ax.axvline(0, color="#111827", linewidth=1)
    colors = [COLORS["verified"] if low > 0 else COLORS["falsified"] if high < 0 else COLORS["neutral"] for low, high in zip(lows, highs)]
    for mean, low, high, position, color in zip(means, lows, highs, y, colors):
        ax.errorbar(
            mean,
            position,
            xerr=[[mean - low], [high - mean]],
            fmt="none",
            ecolor=color,
            elinewidth=3,
            capsize=6,
        )
    ax.scatter(means, y, c=colors, s=75, zorder=3)
    ax.set_yticks(y, labels)
    ax.invert_yaxis()
    ax.set_xlabel("epoch-60 test pAUC: SCENT − SOX  (higher is better)")
    ax.set_title("Test pAUC is mixed and is secondary to the paper's loss claim")
    save(fig, output, "claim6_pauc.png")


def claim2_rate(output: Path) -> None:
    result = json.loads((ARTIFACTS / "claim_2" / "raw_summary.json").read_text())
    horizons = np.asarray(result["horizons"], dtype=float)
    means = np.asarray(result["mean_gaps"])
    lows = np.asarray(result["ci95_low"])
    highs = np.asarray(result["ci95_high"])
    reference = means[0] * np.sqrt(horizons[0] / horizons)
    fig, ax = plt.subplots(figsize=(8.7, 5.5))
    ax.fill_between(horizons, lows, highs, color=COLORS["verified"], alpha=0.18, label="95% seed interval")
    ax.loglog(horizons, means, "o-", color=COLORS["verified"], linewidth=2.5, label="observed mean gap")
    ax.loglog(horizons, reference, "--", color=COLORS["paper"], linewidth=2, label=r"$T^{-1/2}$ reference")
    ax.set_xlabel("iterations T")
    ax.set_ylabel("expected objective gap")
    ax.set_title(f"Claim 2: observed log–log slope = {result['log_log_slope']:.3f}")
    ax.legend(frameon=False)
    save(fig, output, "claim2_rate.png")


def claim4_kappa(output: Path) -> None:
    frame = pd.read_csv(ARTIFACTS / "claim_4" / "fixed_w_results.csv")
    fig, ax = plt.subplots(figsize=(8.7, 5.5))
    for mu, group in frame.groupby("mu"):
        group = group.sort_values("sample_kappa")
        ax.semilogy(
            group["sample_kappa"],
            group["tail_error_ratio_mean"],
            "o-",
            linewidth=2.2,
            markersize=7,
            label=f"μ={mu:g}",
        )
    ax.axhline(1, color="#111827", linewidth=1, linestyle="--", label="equal tail MSE")
    ax.set_xlabel(r"sample $\kappa = E[z^2]/E[z]^2$")
    ax.set_ylabel("SPMD / SGD tail squared error")
    ax.set_title("Claim 4: κ tracks the fixed-w convergence advantage")
    ax.legend(frameon=False)
    save(fig, output, "claim4_kappa.png")


def verdict_dashboard(output: Path) -> None:
    verdicts = ["VERIFIED", "VERIFIED", "VERIFIED", "VERIFIED", "BLOCKED", "FALSIFIED"]
    colors = [
        COLORS["verified"],
        COLORS["verified"],
        COLORS["verified"],
        COLORS["verified"],
        COLORS["blocked"],
        COLORS["falsified"],
    ]
    fig, ax = plt.subplots(figsize=(10.2, 3.3))
    x = np.arange(1, 7)
    ax.scatter(x, np.zeros_like(x), s=1900, c=colors)
    for claim, verdict in zip(x, verdicts):
        ax.text(claim, 0.16, f"Claim {claim}", ha="center", va="center", fontweight="bold")
        ax.text(claim, 0, verdict, ha="center", va="center", color="white", fontsize=6.5, fontweight="bold")
    ax.set_xlim(0.4, 6.6)
    ax.set_ylim(-0.35, 0.35)
    ax.axis("off")
    ax.set_title("Honest terminal verdicts — no score increase claimed", pad=12)
    save(fig, output, "verdict_dashboard.png")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output",
        type=Path,
        default=ROOT / "reports" / "scent-reproduction" / "images",
    )
    args = parser.parse_args()
    style()
    claim6_objective(args.output)
    claim6_pauc(args.output)
    claim2_rate(args.output)
    claim4_kappa(args.output)
    verdict_dashboard(args.output)


if __name__ == "__main__":
    main()
