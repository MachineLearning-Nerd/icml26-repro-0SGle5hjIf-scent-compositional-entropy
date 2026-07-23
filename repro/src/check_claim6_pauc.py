#!/usr/bin/env python3
"""Independent checker for the raw Claim 6 CIFAR pAUC evidence."""

from __future__ import annotations

import csv
import json
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np


def paired_interval(values: np.ndarray) -> tuple[float, float]:
    rng = np.random.default_rng(260202877)
    draws = rng.choice(values, size=(20_000, len(values)), replace=True).mean(axis=1)
    return tuple(float(value) for value in np.quantile(draws, [0.025, 0.975]))


def main() -> int:
    if len(sys.argv) != 3:
        print("usage: check_claim6_pauc.py CONFIG.json METRICS.csv", file=sys.stderr)
        return 2
    config = json.loads(Path(sys.argv[1]).read_text())
    with Path(sys.argv[2]).open(newline="") as handle:
        rows = list(csv.DictReader(handle))

    expected_rows = (
        len(config["datasets"])
        * len(config["taus"])
        * len(config["methods"])
        * len(config["seeds"])
        * (config["finetune_epochs"] // config["evaluation_every"] + 1)
    )
    numeric_finite = all(
        np.isfinite(float(row[key]))
        for row in rows
        for key in ("train_objective", "test_pauc")
    )
    complete = len(rows) == expected_rows and numeric_finite
    output: dict[str, object] = {
        "checker": "independent_claim6_raw_csv_reduction",
        "mode": config["mode"],
        "rows": len(rows),
        "expected_rows": expected_rows,
        "complete": complete,
    }

    if config["mode"] == "profile":
        methods = {row["method"] for row in rows}
        epochs = {int(row["epoch"]) for row in rows}
        output.update(
            {
                "verdict": "PROFILE_ONLY",
                "methods_present": sorted(methods),
                "epochs_present": sorted(epochs),
                "passed": complete
                and methods == set(config["methods"])
                and epochs == {0, config["finetune_epochs"]},
            }
        )
        print(json.dumps(output, sort_keys=True))
        return 0 if output["passed"] else 1

    final_epoch = config["finetune_epochs"]
    grouped: dict[tuple[str, float, int], dict[str, float]] = defaultdict(dict)
    for row in rows:
        if int(row["epoch"]) == final_epoch:
            key = (row["dataset"], float(row["tau"]), int(row["seed"]))
            grouped[key][row["method"]] = float(row["train_objective"])

    settings: dict[str, object] = {}
    statuses: list[str] = []
    margin = float(config["equivalence_margin"])
    for dataset in config["datasets"]:
        for tau in config["taus"]:
            differences = np.array(
                [
                    grouped[(dataset, float(tau), int(seed))]["SCENT"]
                    - grouped[(dataset, float(tau), int(seed))]["SOX"]
                    for seed in config["seeds"]
                ]
            )
            low, high = paired_interval(differences)
            if high < 0:
                status = "SUPERIOR"
            elif low >= -margin and high <= margin:
                status = "EQUIVALENT"
            elif low > margin:
                status = "INFERIOR"
            else:
                status = "UNRESOLVED"
            statuses.append(status)
            settings[f"{dataset}:tau={tau}"] = {
                "paired_differences_scent_minus_sox": differences.tolist(),
                "mean_difference": float(differences.mean()),
                "bootstrap95": [low, high],
                "status": status,
            }

    if complete and all(status in {"SUPERIOR", "EQUIVALENT"} for status in statuses):
        verdict = "VERIFIED"
    elif complete and any(status == "INFERIOR" for status in statuses):
        verdict = "FALSIFIED"
    else:
        verdict = "BLOCKED"
    output.update(
        {
            "equivalence_margin": margin,
            "settings": settings,
            "verdict": verdict,
            "passed": complete,
        }
    )
    print(json.dumps(output, sort_keys=True))
    return 0 if output["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
