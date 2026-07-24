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

    imported_datasets = set(
        config.get("imported_final_metrics", {}).get("datasets", [])
    )
    run_datasets = set(config.get("run_datasets", config["datasets"]))
    all_datasets = set(config["datasets"])
    source_partition_valid = (
        imported_datasets.isdisjoint(run_datasets)
        and imported_datasets | run_datasets == all_datasets
    )
    expected_rows = sum(
        len(config["taus"])
        * len(config["methods"])
        * len(config["seeds"])
        * (
            1
            if dataset in imported_datasets
            else config["finetune_epochs"] // config["evaluation_every"] + 1
        )
        for dataset in config["datasets"]
    )
    numeric_finite = all(
        np.isfinite(float(row[key]))
        for row in rows
        for key in ("train_objective", "test_pauc")
    )
    keys = [
        (
            row["dataset"],
            float(row["tau"]),
            row["method"],
            int(row["seed"]),
            int(row["epoch"]),
        )
        for row in rows
    ]
    expected_keys = {
        (dataset, float(tau), method, int(seed), epoch)
        for dataset in config["datasets"]
        for tau in config["taus"]
        for method in config["methods"]
        for seed in config["seeds"]
        for epoch in (
            [config["finetune_epochs"]]
            if dataset in imported_datasets
            else range(
                0,
                config["finetune_epochs"] + 1,
                config["evaluation_every"],
            )
        )
    }
    complete = (
        source_partition_valid
        and len(rows) == expected_rows
        and len(set(keys)) == len(keys)
        and set(keys) == expected_keys
        and numeric_finite
    )
    output: dict[str, object] = {
        "checker": "independent_claim6_raw_csv_reduction",
        "mode": config["mode"],
        "rows": len(rows),
        "expected_rows": expected_rows,
        "complete": complete,
        "source_partition_valid": source_partition_valid,
        "imported_final_datasets": sorted(imported_datasets),
        "run_datasets": sorted(run_datasets),
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

    if config["mode"] == "shard":
        methods = {row["method"] for row in rows}
        epochs = {int(row["epoch"]) for row in rows}
        final_rows = [
            {
                "dataset": row["dataset"],
                "tau": float(row["tau"]),
                "method": row["method"],
                "seed": int(row["seed"]),
                "epoch": int(row["epoch"]),
                "train_objective": float(row["train_objective"]),
                "test_pauc": float(row["test_pauc"]),
            }
            for row in rows
            if int(row["epoch"]) == config["finetune_epochs"]
        ]
        passed = (
            complete
            and len(config["seeds"]) == 1
            and methods == set(config["methods"])
            and epochs
            == set(
                range(
                    0,
                    config["finetune_epochs"] + 1,
                    config["evaluation_every"],
                )
            )
            and len(final_rows) == len(config["taus"]) * len(config["methods"])
        )
        output.update(
            {
                "verdict": "SHARD_ONLY",
                "seed": config["seeds"][0] if len(config["seeds"]) == 1 else None,
                "methods_present": sorted(methods),
                "epochs_present": sorted(epochs),
                "final_rows": final_rows,
                "passed": passed,
            }
        )
        print(json.dumps(output, sort_keys=True))
        return 0 if passed else 1

    if not complete:
        output.update({"verdict": "BLOCKED", "passed": False})
        print(json.dumps(output, sort_keys=True))
        return 1

    final_epoch = config["finetune_epochs"]
    grouped: dict[tuple[str, float, int], dict[str, float]] = defaultdict(dict)
    for row in rows:
        if int(row["epoch"]) == final_epoch:
            key = (row["dataset"], float(row["tau"]), int(row["seed"]))
            grouped[key][row["method"]] = float(row["train_objective"])

    settings: dict[str, object] = {}
    pauc_settings: dict[str, object] = {}
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
            pauc_differences = np.array(
                [
                    float(
                        next(
                            row["test_pauc"]
                            for row in rows
                            if row["dataset"] == dataset
                            and float(row["tau"]) == float(tau)
                            and int(row["seed"]) == int(seed)
                            and row["method"] == "SCENT"
                            and int(row["epoch"]) == final_epoch
                        )
                    )
                    - float(
                        next(
                            row["test_pauc"]
                            for row in rows
                            if row["dataset"] == dataset
                            and float(row["tau"]) == float(tau)
                            and int(row["seed"]) == int(seed)
                            and row["method"] == "SOX"
                            and int(row["epoch"]) == final_epoch
                        )
                    )
                    for seed in config["seeds"]
                ]
            )
            pauc_low, pauc_high = paired_interval(pauc_differences)
            if pauc_low > 0:
                pauc_status = "SUPERIOR"
            elif pauc_low >= -margin and pauc_high <= margin:
                pauc_status = "EQUIVALENT"
            elif pauc_high < -margin:
                pauc_status = "INFERIOR"
            else:
                pauc_status = "UNRESOLVED"
            pauc_settings[f"{dataset}:tau={tau}"] = {
                "paired_differences_scent_minus_sox": pauc_differences.tolist(),
                "mean_difference": float(pauc_differences.mean()),
                "bootstrap95": [pauc_low, pauc_high],
                "status": pauc_status,
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
            "secondary_test_pauc_settings": pauc_settings,
            "verdict": verdict,
            "passed": complete,
        }
    )
    print(json.dumps(output, sort_keys=True))
    return 0 if output["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
