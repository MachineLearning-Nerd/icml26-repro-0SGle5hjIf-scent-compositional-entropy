"""Upload the staged allowlist to the Space, then verify every path at the new revision."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

from huggingface_hub import HfApi, get_token, hf_hub_download

REPO = Path(__file__).resolve().parents[1]
RELEASE = REPO / ".openresearch" / "release"
STAGE = Path("/private/tmp/claude-501/-Users-dineshjinjala-Documents-AllCode-ICMLPapers/"
             "8657cd16-a2c9-4a7c-821e-e589ccee3f0c/scratchpad/space_stage")
SPACE_ID = "DineshAI/0SGle5hjIf"


def main() -> None:
    api = HfApi()
    token = get_token()
    allow = RELEASE.joinpath("hf_upload_allowlist.txt").read_text().split()
    want = {line.split("  ", 1)[1]: line.split("  ", 1)[0]
            for line in RELEASE.joinpath("hf_upload_manifest.sha256").read_text().splitlines()}
    before = api.repo_info(SPACE_ID, repo_type="space").sha

    api.upload_folder(
        repo_id=SPACE_ID, repo_type="space", folder_path=str(STAGE),
        allow_patterns=allow, token=token,
        commit_message="Publish raw claim evidence and rebuilt Claim 4 audit",
    )
    after = api.repo_info(SPACE_ID, repo_type="space").sha
    print(json.dumps({"before": before, "after": after, "uploaded": len(allow)}, indent=2))

    bad = []
    for rel, want_sha in want.items():
        p = hf_hub_download(SPACE_ID, rel, repo_type="space", revision=after, token=token)
        got = hashlib.sha256(Path(p).read_bytes()).hexdigest()
        if got != want_sha:
            bad.append({"path": rel, "want": want_sha, "got": got})
    print(json.dumps({"verified_at_revision": after, "checked": len(want),
                      "mismatches": bad, "all_match": not bad}, indent=2))
    (RELEASE / "publish_verification.json").write_text(json.dumps(
        {"before": before, "after": after, "checked": len(want),
         "mismatches": bad, "all_match": not bad}, indent=2) + "\n")


if __name__ == "__main__":
    main()
