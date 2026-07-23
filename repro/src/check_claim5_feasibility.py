#!/usr/bin/env python3
"""Independent reduction of the raw Claim 5 feasibility inventory."""

from __future__ import annotations

import json
import sys
from pathlib import Path


def blocker_holds(raw: dict[str, object]) -> bool:
    datasets = raw["datasets"]
    largest_source = max(item["source_bytes"] for item in datasets.values())
    return bool(
        largest_source > raw["runtime"]["available_disk_bytes"]
        and not raw["official_scent_release_assets"]
        and not raw["official_scent_feature_files"]
        and not raw["public_extracted_feature_search_matches"]
        and raw["minimum_protocol"]["example_visits"] > 1_000_000_000
        and raw["minimum_protocol"]["datasets"] == 2
        and raw["minimum_protocol"]["methods"] >= 4
        and raw["minimum_protocol"]["seeds"] == 3
        and raw["minimum_protocol"]["epochs"] == 50
    )


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: check_claim5_feasibility.py RAW_INVENTORY.json", file=sys.stderr)
        return 2

    raw = json.loads(Path(sys.argv[1]).read_text())
    expected_revisions = {
        "Glint360K": "d0da68fbc62b545010942f959d2d3b6a364f57b8",
        "TreeOfLife-10M": "91debffb7146c32c89d76feb1eb575b555e2ecc7",
    }
    revision_match = all(
        raw["datasets"][name]["revision"] == revision
        for name, revision in expected_revisions.items()
    )
    size_match = (
        raw["datasets"]["Glint360K"]["source_bytes"] == 129_922_066_070
        and raw["datasets"]["TreeOfLife-10M"]["source_bytes"]
        == 1_994_644_470_866
    )
    blocker = blocker_holds(raw)

    negative = json.loads(json.dumps(raw))
    negative["runtime"]["available_disk_bytes"] = 3_000_000_000_000
    negative["official_scent_feature_files"] = ["features.pt"]
    negative_rejected = not blocker_holds(negative)

    output = {
        "checker": "independent_claim5_raw_inventory_reduction",
        "revision_match": revision_match,
        "size_match": size_match,
        "blocker_holds": blocker,
        "negative_control_rejected": negative_rejected,
        "passed": revision_match and size_match and blocker and negative_rejected,
    }
    print(json.dumps(output, sort_keys=True))
    return 0 if output["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
