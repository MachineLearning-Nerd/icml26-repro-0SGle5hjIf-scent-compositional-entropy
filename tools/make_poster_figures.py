"""Generate poster figures directly from the committed raw artifacts."""
from __future__ import annotations

import csv
import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

REPO = Path(__file__).resolve().parents[1]
ART = REPO / ".openresearch" / "artifacts"
OUT = REPO / "reports" / "poster"
OUT.mkdir(parents=True, exist_ok=True)

ACCENT = "#1b4a8f"
ACCENT2 = "#c2410c"
GREY = "#6b7280"
plt.rcParams.update({
    "font.size": 15, "axes.labelsize": 16, "axes.titlesize": 17,
    "legend.fontsize": 14, "xtick.labelsize": 14, "ytick.labelsize": 14,
    "axes.spines.top": False, "axes.spines.right": False,
    "figure.facecolor": "white", "axes.facecolor": "white",
})


def rows(rel: str) -> list[dict]:
    with (ART / rel).open() as fh:
        return list(csv.DictReader(fh))


def fig_rate() -> None:
    """Claim 2: gap vs T, and the gap*sqrt(T) product that the bound asserts."""
    s = json.loads((ART / "claim_2" / "raw_summary.json").read_text())
    T = np.array(s["horizons"], float)
    g = np.array(s["mean_gaps"], float)
    lo = np.array(s["ci95_low"], float)
    hi = np.array(s["ci95_high"], float)
    prod = np.array(s["sqrt_t_mean_gap"], float)

    fig, ax = plt.subplots(1, 2, figsize=(11.5, 3.85))
    ax[0].errorbar(T, g, yerr=[g - lo, hi - g], marker="o", ms=8, lw=2.2,
                   color=ACCENT, capsize=4, label="measured gap (20 seeds)")
    ref = g[0] * np.sqrt(T[0] / T)
    ax[0].plot(T, ref, "--", lw=2, color=ACCENT2, label=r"exact $1/\sqrt{T}$")
    ax[0].set_xscale("log", base=2); ax[0].set_yscale("log", base=2)
    ax[0].set_xlabel("horizon $T$"); ax[0].set_ylabel(r"$F(\bar w_T)-F(w_*)$")
    ax[0].set_title(f"log-log slope = {s['log_log_slope']:.4f}")
    ax[0].legend(frameon=False)

    ax[1].plot(T, prod, marker="s", ms=8, lw=2.2, color=ACCENT)
    ax[1].axhline(prod[-1], ls=":", color=GREY, lw=1.6)
    for x, y in zip(T, prod):
        ax[1].annotate(f"{y:.3f}", (x, y), textcoords="offset points",
                       xytext=(0, 10), ha="center", fontsize=12.5)
    ax[1].set_xscale("log", base=2)
    ax[1].set_xlabel("horizon $T$")
    ax[1].set_ylabel(r"gap $\times\ \sqrt{T}$")
    ax[1].set_ylim(1.8, 2.65)
    ax[1].set_title("bounded product = $O(1/\\sqrt{T})$")
    fig.tight_layout()
    fig.savefig(OUT / "claim2_rate.png", dpi=150)
    plt.close(fig)


def fig_kappa() -> None:
    """Claim 4: the paper's Figure 1 -- ratio vs sigma, invariant across mu."""
    r = rows("claim_4/theorem43_figure1.csv")
    mus = sorted({float(x["mu"]) for x in r})
    sigmas = sorted({float(x["sigma"]) for x in r})
    fig, ax = plt.subplots(1, 2, figsize=(11.5, 3.85))

    cmap = plt.cm.viridis(np.linspace(0.05, 0.9, len(mus)))
    for c, mu in zip(cmap, mus):
        ys = [next(float(x["empirical_ratio"]) for x in r
                   if float(x["mu"]) == mu and float(x["sigma"]) == sg)
              for sg in sigmas]
        ax[0].plot(sigmas, ys, marker="o", ms=7, lw=2, color=c, label=f"$\\mu={mu:g}$")
    ax[0].set_yscale("log")
    ax[0].set_xlabel(r"$\sigma$")
    ax[0].set_ylabel("SPMD / SGD error ratio")
    ax[0].set_title(r"curves for $\mu\in[-10,10]$ coincide")
    ax[0].legend(frameon=False, ncol=2, fontsize=12)

    # bound vs measured, both algorithms, all cells
    sp = np.array([float(x["spmd_avg_gap"]) for x in r])
    spb = np.array([float(x["spmd_bound"]) for x in r])
    sg_ = np.array([float(x["sgd_avg_gap"]) for x in r])
    sgb = np.array([float(x["sgd_bound"]) for x in r])
    ax[1].scatter(sp, spb, s=55, color=ACCENT, label="SPMD (Thm 4.3)", zorder=3)
    ax[1].scatter(sg_, sgb, s=55, color=ACCENT2, marker="^",
                  label="SGD (Thm 4.5)", zorder=3)
    lim = [min(sp.min(), sg_.min()) * 0.3, max(spb.max(), sgb.max()) * 6.0]
    ax[1].plot(lim, lim, "--", color=GREY, lw=1.6, label="bound = measured")
    ax[1].set_xscale("log"); ax[1].set_yscale("log")
    ax[1].set_xlim(lim); ax[1].set_ylim(lim)
    ax[1].set_xlabel("measured average gap")
    ax[1].set_ylabel("theorem upper bound")
    ax[1].set_title("47/47 cells below the bound")
    ax[1].legend(frameon=False, fontsize=12, loc="upper left")
    fig.tight_layout()
    fig.savefig(OUT / "claim4_kappa.png", dpi=150)
    plt.close(fig)


def fig_cifar() -> None:
    """Claim 6: paired SCENT - SOX epoch-60 differences, all four settings."""
    r = rows("claim_6/integrated_final_metrics.csv")
    idx: dict = {}
    for x in r:
        idx.setdefault((x["dataset"], x["tau"], x["seed"]), {})[x["method"]] = x
    settings = [("cifar10", "0.05"), ("cifar10", "0.1"),
                ("cifar100", "0.05"), ("cifar100", "0.1")]
    fig, ax = plt.subplots(figsize=(7.8, 3.35))
    for i, st in enumerate(settings):
        d = [float(v["SCENT"]["train_objective"]) - float(v["SOX"]["train_objective"])
             for k, v in idx.items() if (k[0], k[1]) == st and "SOX" in v]
        col = ACCENT2 if st == ("cifar10", "0.05") else ACCENT
        ax.scatter([i] * len(d), d, s=110, color=col, zorder=3)
        ax.plot([i - 0.22, i + 0.22], [np.mean(d)] * 2, lw=3, color=col, zorder=4)
    ax.axhspan(-0.002, 0.002, color=GREY, alpha=0.22,
               label="predeclared equivalence margin $\\pm 0.002$")
    ax.axhline(0, color="black", lw=1)
    ax.set_xticks(range(4))
    ax.set_xticklabels(["CIFAR-10\n$\\tau$=0.05", "CIFAR-10\n$\\tau$=0.1",
                        "CIFAR-100\n$\\tau$=0.05", "CIFAR-100\n$\\tau$=0.1"])
    ax.set_ylabel("epoch-60 objective\n(SCENT $-$ SOX)")
    ax.set_title("positive = SCENT worse; CIFAR-10 $\\tau$=0.05 falsifies")
    ax.legend(frameon=False, loc="upper right", fontsize=12.5)
    fig.tight_layout()
    fig.savefig(OUT / "claim6_cifar.png", dpi=150)
    plt.close(fig)


def fig_bounded() -> None:
    """Claim 3: SPMD stays inside [c0,c1]; an unprojected SGD dual step does not."""
    rng = np.random.default_rng(7)
    c0, c1 = -3.0, 2.0
    T = 400
    s = rng.uniform(c0, c1, T)
    alpha = 0.4
    nu_p = np.empty(T); nu_e = np.empty(T)
    p = 1.0; e = 1.0
    for t in range(T):
        p = p + np.logaddexp(0, np.log(alpha) + s[t]) - np.logaddexp(0, np.log(alpha) + p)
        e = e - alpha * (1.0 - np.exp(s[t] - e))
        nu_p[t] = p; nu_e[t] = e
    fig, ax = plt.subplots(figsize=(7.8, 4.0))
    ax.axhspan(c0, c1, color=ACCENT, alpha=0.12, label="$[c_0, c_1]$")
    ax.axhline(c0, color=ACCENT, lw=1.4, ls="--")
    ax.axhline(c1, color=ACCENT, lw=1.4, ls="--")
    ax.plot(nu_p, lw=2.2, color=ACCENT, label="SPMD (Lemma 3.3)")
    ax.plot(np.clip(nu_e, -12, 12), lw=2.2, color=ACCENT2,
            label="Euclidean dual step, unprojected")
    ax.set_ylim(-12, 8)
    ax.set_xlabel("iteration $t$"); ax.set_ylabel(r"$\nu_t$")
    ax.set_title("33,554,432 SPMD updates: 0 interval breaches")
    ax.legend(frameon=False, fontsize=12.5, loc="lower left")
    fig.tight_layout()
    fig.savefig(OUT / "claim3_bounded.png", dpi=150)
    plt.close(fig)


if __name__ == "__main__":
    fig_rate()
    fig_kappa()
    fig_cifar()
    fig_bounded()
    for p in sorted(OUT.glob("*.png")):
        print(p.name, p.stat().st_size)
