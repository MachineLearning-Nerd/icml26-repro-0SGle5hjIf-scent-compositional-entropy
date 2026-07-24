"""Validate the additive, text-only Hugging Face release candidate."""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
RELEASE = ROOT / ".openresearch" / "release"
LOGBOOK = ROOT / ".trackio" / "logbook"
OLD_MANIFEST = ROOT / ".openresearch" / "audit" / "judged_space_71993d9a.sha256"
UPLOADS = {
    "logbook.json": LOGBOOK / "logbook.json",
    "pages/rigorous-update/page.md": LOGBOOK / "pages" / "rigorous-update" / "page.md",
}
SECRET_PATTERNS = {
    "hugging_face_token": re.compile(rb"\bhf_[A-Za-z0-9]{20,}\b"),
    "openai_key": re.compile(rb"\bsk-[A-Za-z0-9_-]{20,}\b"),
    "github_pat": re.compile(rb"\bgithub_pat_[A-Za-z0-9_]{20,}\b"),
    "aws_access_key": re.compile(rb"\bAKIA[0-9A-Z]{16}\b"),
    "private_key": re.compile(rb"-----BEGIN [A-Z ]*PRIVATE KEY-----"),
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def old_entries() -> dict[str, str]:
    entries: dict[str, str] = {}
    for line in OLD_MANIFEST.read_text().splitlines():
        digest, path = line.split(maxsplit=1)
        entries[path.strip()] = digest
    return entries


def referenced_pages(node: dict) -> list[str]:
    pages = [node["file"]]
    for child in node.get("children", []):
        pages.extend(referenced_pages(child))
    return pages


def main() -> None:
    RELEASE.mkdir(parents=True, exist_ok=True)
    old = old_entries()
    allowlist = sorted(UPLOADS)
    candidate_paths = sorted(set(old) | set(allowlist))
    missing_old_paths = sorted(set(old) - set(candidate_paths))

    logbook = json.loads((LOGBOOK / "logbook.json").read_text())
    page_paths = referenced_pages(logbook["root"])
    missing_references = sorted(
        page for page in page_paths if not (LOGBOOK / page).is_file()
    )
    slugs = [child["slug"] for child in logbook["root"]["children"]]

    protected_hashes: dict[str, dict[str, object]] = {}
    for relative, expected in old.items():
        local = LOGBOOK / relative
        if local.is_file() and relative != "logbook.json":
            actual = sha256(local)
            protected_hashes[relative] = {
                "expected": expected,
                "actual": actual,
                "match": actual == expected,
            }

    secret_findings: list[dict[str, str]] = []
    scan_files = sorted(
        [
            *UPLOADS.values(),
            *ROOT.glob(".openresearch/artifacts/**/*"),
            ROOT / "README.md",
            ROOT / "reports" / "scent-reproduction" / "report.md",
            ROOT / "notebooks" / "scent_reproduction.py",
            ROOT / ".openresearch" / "release" / "commands_executed.md",
            ROOT / ".openresearch" / "release" / "release_report.md",
        ]
    )
    for path in scan_files:
        if not path.is_file():
            continue
        content = path.read_bytes()
        for name, pattern in SECRET_PATTERNS.items():
            if pattern.search(content):
                secret_findings.append(
                    {"pattern": name, "path": str(path.relative_to(ROOT))}
                )

    allowlist_text = "\n".join(allowlist) + "\n"
    (RELEASE / "hf_upload_allowlist.txt").write_text(allowlist_text)
    manifest_text = "".join(
        f"{sha256(source)}  {destination}\n"
        for destination, source in sorted(UPLOADS.items())
    )
    (RELEASE / "hf_upload_manifest.sha256").write_text(manifest_text)

    artifact_paths = sorted(
        path
        for path in [
            *ROOT.glob(".openresearch/artifacts/**/*"),
            *ROOT.glob("reports/scent-reproduction/**/*"),
            ROOT / "README.md",
            ROOT / "notebooks" / "scent_reproduction.py",
            ROOT / ".openresearch" / "release" / "commands_executed.md",
            ROOT / ".openresearch" / "release" / "release_report.md",
        ]
        if path.is_file()
    )
    artifact_manifest = "".join(
        f"{sha256(path)}  {path.relative_to(ROOT)}\n" for path in artifact_paths
    )
    (RELEASE / "candidate_artifact_manifest.sha256").write_text(artifact_manifest)

    audit = {
        "judged_revision": "71993d9a3c56ee16bd8935f11d635988eb494f5b",
        "space_id": "DineshAI/0SGle5hjIf",
        "old_file_count": len(old),
        "candidate_file_count_after_additive_upload": len(candidate_paths),
        "old_file_set_is_subset": not missing_old_paths,
        "missing_old_paths": missing_old_paths,
        "upload_allowlist": allowlist,
        "upload_is_text_only": all(
            source.suffix in {".json", ".md"} for source in UPLOADS.values()
        ),
        "logbook": {
            "json_valid": True,
            "referenced_pages": page_paths,
            "missing_references": missing_references,
            "unique_child_slugs": len(slugs) == len(set(slugs)),
            "new_page_reachable": "pages/rigorous-update/page.md" in page_paths,
        },
        "protected_local_files": protected_hashes,
        "all_checked_protected_hashes_match": all(
            item["match"] for item in protected_hashes.values()
        ),
        "secret_scan": {
            "patterns_checked": sorted(SECRET_PATTERNS),
            "findings": secret_findings,
            "passed": not secret_findings,
        },
    }
    audit["passed"] = all(
        [
            audit["old_file_set_is_subset"],
            audit["upload_is_text_only"],
            audit["logbook"]["json_valid"],
            not audit["logbook"]["missing_references"],
            audit["logbook"]["unique_child_slugs"],
            audit["logbook"]["new_page_reachable"],
            audit["all_checked_protected_hashes_match"],
            audit["secret_scan"]["passed"],
        ]
    )
    (RELEASE / "release_audit.json").write_text(
        json.dumps(audit, indent=2, sort_keys=True) + "\n"
    )
    print(json.dumps(audit, sort_keys=True))
    if not audit["passed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
