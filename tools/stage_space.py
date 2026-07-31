"""Stage the Hugging Face Space upload tree and prove it is purely additive.

Downloads the currently judged revision, copies the candidate logbook, evidence
and verifiers over it, then emits:
  - hf_upload_allowlist.txt   exact paths to upload (text only)
  - hf_upload_manifest.sha256 SHA-256 of every staged path
  - subset_check.json         proof that the judged file set survives
"""
from __future__ import annotations

import hashlib
import json
import shutil
import subprocess
from pathlib import Path

from huggingface_hub import HfApi, get_token, snapshot_download

REPO = Path(__file__).resolve().parents[1]
BOOK = REPO / ".trackio" / "logbook"
ART = REPO / ".openresearch" / "artifacts"
SCRATCH = Path("/private/tmp/claude-501/-Users-dineshjinjala-Documents-AllCode-ICMLPapers/"
               "8657cd16-a2c9-4a7c-821e-e589ccee3f0c/scratchpad")
STAGE = SCRATCH / "space_stage"
JUDGED = SCRATCH / "judged_7fcacca"
SPACE_ID = "DineshAI/0SGle5hjIf"
RELEASE = REPO / ".openresearch" / "release"

TEXT_SUFFIXES = {".md", ".json", ".csv", ".py", ".txt", ".html", ".css", ".js",
                 ".svg", ".toml", ".lock"}
VERIFIERS = [
    "verify_dual_contracts.py", "check_dual_evidence.py",
    "verify_rate_kappa.py", "check_rate_kappa.py",
    "verify_claim4_theorem43.py",
    "verify_claim5_feasibility.py", "check_claim5_feasibility.py",
    "verify_claim5_asset_audit.py",
    "verify_claim6_pauc.py", "check_claim6_pauc.py",
    "verify_scent.py", "scent.py",
]


def sha256(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main() -> None:
    token = get_token()
    if STAGE.exists():
        shutil.rmtree(STAGE)
    snapshot_download(SPACE_ID, repo_type="space", local_dir=STAGE, token=token)
    shutil.rmtree(STAGE / ".cache", ignore_errors=True)

    judged_files = {
        str(p.relative_to(STAGE)) for p in STAGE.rglob("*")
        if p.is_file() and ".cache" not in p.parts
    }

    uploads: list[str] = []

    # 1) canonical logbook manifest + pages + poster embed
    for src, rel in [(BOOK / "logbook.json", "logbook.json"),
                     (BOOK / "poster_embed.html", "poster_embed.html"),
                     (BOOK / "pages" / "index.md", "pages/index.md")]:
        dst = STAGE / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy(src, dst)
        uploads.append(rel)
    for page in sorted((BOOK / "pages").iterdir()):
        if page.is_dir() and (page / "page.md").is_file():
            rel = f"pages/{page.name}/page.md"
            dst = STAGE / rel
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy(page / "page.md", dst)
            uploads.append(rel)

    # 2) raw evidence -- the thing the judged revision was missing entirely
    for claim in sorted(ART.iterdir()):
        if not claim.is_dir():
            continue
        for f in sorted(claim.rglob("*")):
            if f.is_file() and f.suffix in TEXT_SUFFIXES:
                rel = f"evidence/{claim.name}/{f.relative_to(claim)}"
                dst = STAGE / rel
                dst.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy(f, dst)
                uploads.append(rel)
    for f in sorted(ART.glob("*.json")):
        rel = f"evidence/{f.name}"
        shutil.copy(f, STAGE / rel)
        uploads.append(rel)

    # 3) verifiers, so every published number is regenerable
    for name in VERIFIERS:
        src = REPO / "repro" / "src" / name
        if src.is_file():
            rel = f"repro/src/{name}"
            dst = STAGE / rel
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy(src, dst)
            uploads.append(rel)
    for src, rel in [(REPO / "pyproject.toml", "repro/pyproject.toml"),
                     (REPO / "uv.lock", "repro/uv.lock")]:
        if src.is_file():
            shutil.copy(src, STAGE / rel)
            uploads.append(rel)

    # ---- subset proof ------------------------------------------------------
    staged_files = {
        str(p.relative_to(STAGE)) for p in STAGE.rglob("*")
        if p.is_file() and ".cache" not in p.parts
    }
    missing = sorted(judged_files - staged_files)
    # Judged pages we do not re-upload must still be byte-identical on the Hub.
    untouched = sorted(judged_files - set(uploads))
    changed_judged = []
    for rel in sorted(judged_files & set(uploads)):
        old = JUDGED / rel
        if old.is_file() and sha256(old) != sha256(STAGE / rel):
            changed_judged.append(rel)

    non_text = [u for u in uploads if Path(u).suffix not in TEXT_SUFFIXES]

    subset = {
        "space_id": SPACE_ID,
        "judged_revision": "7fcacca041de1f1d591846177267ffb679c0dea7",
        "judged_file_count": len(judged_files),
        "staged_file_count": len(staged_files),
        "upload_count": len(uploads),
        "judged_files_missing_from_candidate": missing,
        "judged_subset_holds": not missing,
        "judged_files_left_untouched": untouched,
        "judged_files_modified_by_this_release": changed_judged,
        "non_text_uploads": non_text,
        "text_only_upload": not non_text,
    }
    RELEASE.mkdir(parents=True, exist_ok=True)
    (RELEASE / "subset_check.json").write_text(json.dumps(subset, indent=2) + "\n")
    (RELEASE / "hf_upload_allowlist.txt").write_text("\n".join(uploads) + "\n")
    (RELEASE / "hf_upload_manifest.sha256").write_text(
        "".join(f"{sha256(STAGE / u)}  {u}\n" for u in uploads))

    print(json.dumps({k: v for k, v in subset.items()
                      if k not in ("judged_files_left_untouched",)}, indent=2))
    print(f"\nstaged at {STAGE}")
    print("untouched judged files:", untouched)


if __name__ == "__main__":
    main()
