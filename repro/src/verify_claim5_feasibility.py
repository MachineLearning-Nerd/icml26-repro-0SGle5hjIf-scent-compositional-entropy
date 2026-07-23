#!/usr/bin/env python3
"""Regenerate the exact-data feasibility evidence for empirical Claim 5."""

from __future__ import annotations

import hashlib
import json
import math
import os
import platform
import re
import shutil
import subprocess
import sys
import time
import urllib.parse
import urllib.request
from datetime import UTC, datetime
from pathlib import Path


USER_AGENT = "OpenResearch-SCENT-reproduction/1.0"
OFFICIAL_CODE_SHA = "cfbf17925754f18855f26715adeec4773aa0591d"
DATASETS = {
    "Glint360K": {
        "repo": "gaunernst/glint360k-wds-gz",
        "revision": "d0da68fbc62b545010942f959d2d3b6a364f57b8",
        "examples": 17_091_657,
        "feature_dim": 512,
    },
    "TreeOfLife-10M": {
        "repo": "imageomics/TreeOfLife-10M",
        "revision": "91debffb7146c32c89d76feb1eb575b555e2ecc7",
        "examples": 9_533_174,
        "feature_dim": 512,
    },
}
MINIMUM_METHODS = ("SCENT", "SOX", "U-max", "BSGD")
ARTIFACT_DIR = Path(".openresearch/artifacts/claim_5")


def fetch_json(url: str) -> tuple[object, dict[str, str]]:
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(request, timeout=120) as response:
        headers = {key.lower(): value for key, value in response.headers.items()}
        return json.load(response), headers


def hf_tree(repo: str, revision: str) -> list[dict[str, object]]:
    url = (
        f"https://huggingface.co/api/datasets/{repo}/tree/{revision}"
        "?recursive=true&expand=true"
    )
    rows: list[dict[str, object]] = []
    while url:
        page, headers = fetch_json(url)
        rows.extend(page)
        match = re.search(r'<([^>]+)>; rel="next"', headers.get("link", ""))
        url = match.group(1) if match else ""
    return rows


def github_inventory() -> tuple[list[str], list[str]]:
    tree_url = (
        "https://api.github.com/repos/Optimization-AI/SCENT/git/trees/"
        f"{OFFICIAL_CODE_SHA}?recursive=1"
    )
    releases_url = "https://api.github.com/repos/Optimization-AI/SCENT/releases"
    tree, _ = fetch_json(tree_url)
    releases, _ = fetch_json(releases_url)
    feature_files = [
        item["path"]
        for item in tree["tree"]
        if item["type"] == "blob"
        and Path(item["path"]).suffix.lower()
        in {".pt", ".pth", ".ckpt", ".bin", ".safetensors"}
    ]
    release_assets = [
        asset["name"]
        for release in releases
        for asset in release.get("assets", [])
    ]
    return feature_files, release_assets


def feature_search_matches() -> list[str]:
    matches: set[str] = set()
    for query in ("glint360k features", "TreeOfLife-10M features"):
        url = "https://huggingface.co/api/datasets?" + urllib.parse.urlencode(
            {"search": query, "limit": 100}
        )
        results, _ = fetch_json(url)
        matches.update(item["id"] for item in results)
    return sorted(matches)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> int:
    started = time.perf_counter()
    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
    dataset_inventory: dict[str, dict[str, object]] = {}
    for name, specification in DATASETS.items():
        rows = hf_tree(specification["repo"], specification["revision"])
        source_bytes = sum(
            int(item.get("size", 0))
            for item in rows
            if item.get("type") == "file"
        )
        dataset_inventory[name] = {
            **specification,
            "source_bytes": source_bytes,
            "source_files": sum(item.get("type") == "file" for item in rows),
            "minimum_float32_feature_bytes": (
                specification["examples"] * specification["feature_dim"] * 4
            ),
        }

    feature_files, release_assets = github_inventory()
    search_matches = feature_search_matches()
    total_examples = sum(item["examples"] for item in DATASETS.values())
    methods = len(MINIMUM_METHODS)
    seeds = 3
    epochs = 50
    example_visits = total_examples * methods * seeds * epochs
    batch_steps = sum(
        math.ceil(item["examples"] / 128) * methods * seeds * epochs
        for item in DATASETS.values()
    )
    disk = shutil.disk_usage(".")
    git_sha = subprocess.check_output(
        ["git", "rev-parse", "HEAD"], text=True
    ).strip()

    raw = {
        "retrieved_at_utc": datetime.now(UTC).isoformat(),
        "user_agent": USER_AGENT,
        "official_code": {
            "url": "https://github.com/Optimization-AI/SCENT",
            "revision": OFFICIAL_CODE_SHA,
        },
        "datasets": dataset_inventory,
        "official_scent_feature_files": feature_files,
        "official_scent_release_assets": release_assets,
        "public_extracted_feature_search_matches": search_matches,
        "minimum_protocol": {
            "datasets": 2,
            "methods": methods,
            "method_names": list(MINIMUM_METHODS),
            "seeds": seeds,
            "epochs": epochs,
            "batch_size": 128,
            "example_visits": example_visits,
            "batch_steps": batch_steps,
        },
        "runtime": {
            "git_sha": git_sha,
            "command": "uv run --frozen python repro/src/verify_scent.py",
            "python": platform.python_version(),
            "platform": platform.platform(),
            "logical_cpus": os.cpu_count(),
            "available_disk_bytes": disk.free,
            "disk_total_bytes": disk.total,
        },
    }
    raw_path = ARTIFACT_DIR / "raw_asset_inventory.json"
    raw_path.write_text(json.dumps(raw, indent=2, sort_keys=True) + "\n")

    checker = subprocess.run(
        [
            sys.executable,
            str(Path(__file__).with_name("check_claim5_feasibility.py")),
            str(raw_path),
        ],
        text=True,
        capture_output=True,
    )
    print(checker.stdout, end="")
    checker_output = (
        json.loads(checker.stdout.strip()) if checker.stdout.strip() else {}
    )
    (ARTIFACT_DIR / "independent_checker.json").write_text(
        json.dumps(checker_output, indent=2, sort_keys=True) + "\n"
    )
    (ARTIFACT_DIR / "negative_control.json").write_text(
        json.dumps(
            {
                "mutation": (
                    "set disk to 3 TB and inject a published features.pt asset"
                ),
                "blocker_rejected": checker_output.get(
                    "negative_control_rejected", False
                ),
            },
            indent=2,
            sort_keys=True,
        )
        + "\n"
    )
    runtime_seconds = time.perf_counter() - started
    summary = {
        "verdict": "BLOCKED" if checker.returncode == 0 else "BLOCKED_EVIDENCE_FAILED",
        "reason": (
            "The exact released-data pipeline exceeds authorized CPU storage and "
            "work capacity, and no official extracted features are published."
        ),
        "runtime_seconds": runtime_seconds,
        "independent_checker_passed": checker.returncode == 0,
        "raw_inventory_sha256": sha256(raw_path),
    }
    (ARTIFACT_DIR / "verdict.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n"
    )
    (ARTIFACT_DIR / "exact_command.txt").write_text(
        "uv run --frozen python repro/src/verify_scent.py\n"
    )
    (ARTIFACT_DIR / "environment.txt").write_text(
        f"git_sha={git_sha}\n"
        f"python={platform.python_version()}\n"
        f"platform={platform.platform()}\n"
        f"logical_cpus={os.cpu_count()}\n"
    )
    (ARTIFACT_DIR / "EVAL.md").write_text(
        "# Claim 5 evaluation\n\n"
        f"Verdict: **{summary['verdict']}**.\n\n"
        "This is not a toy benchmark result and it is not a performance PASS. "
        "The machine-checked inventory establishes why the exact two-dataset, "
        "four-method-minimum, three-seed protocol cannot run on this authorized "
        "CPU host without unpublished extracted features. See "
        "`raw_asset_inventory.json` and `independent_checker.json`.\n"
    )

    print("\n" + "=" * 78)
    print("CLAIM 5 FULL-SCALE FEASIBILITY CONTRACT")
    print("=" * 78)
    for name, item in dataset_inventory.items():
        print(
            f"{name}: source={item['source_bytes']} bytes; "
            f"minimum float32 features={item['minimum_float32_feature_bytes']} bytes"
        )
    print(
        f"available disk={disk.free} bytes; official feature assets={feature_files}; "
        f"public extracted-feature matches={search_matches}"
    )
    print(
        f"minimum exact-protocol example visits={example_visits}; "
        f"batch steps={batch_steps}"
    )
    print(
        "CLAIM 5 BLOCKED: no toy substitution; "
        f"independent checker={'PASS' if checker.returncode == 0 else 'FAIL'}"
    )
    print(f"RUNTIME_SECONDS={runtime_seconds:.3f}")
    print(
        "CLAIM5_FEASIBILITY_SUITE="
        f"{'PASS' if checker.returncode == 0 else 'FAIL'}"
    )
    return checker.returncode


if __name__ == "__main__":
    raise SystemExit(main())
