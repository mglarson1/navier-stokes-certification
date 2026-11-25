#!/usr/bin/env python3
"""Check the small, manifest-bound paper companions. Not a proof replay."""
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]


def check_paper(root):
    manifest = json.loads((root / "REPOSITORY_MANIFEST.json").read_text())
    for name, record in manifest["files"].items():
        path = root / name
        if not path.resolve().is_relative_to(root.resolve()) or path.is_symlink():
            raise ValueError(f"{root.name}: unsafe path: {name}")
        with path.open("rb") as stream:
            digest = hashlib.file_digest(stream, "sha256").hexdigest()
        if path.stat().st_size != record["bytes"] or digest != record["sha256"]:
            raise ValueError(f"{root.name}: changed file: {name}")
    # Generated outputs and local environments are outside this source check.
    return len(manifest["files"])


def main():
    papers = sorted((ROOT / "papers").glob("*/REPOSITORY_MANIFEST.json"))
    if not papers:
        raise ValueError("No paper manifests found")
    for manifest in papers:
        count = check_paper(manifest.parent)
        print(f"PASS {manifest.parent.name}: {count} listed files match its source manifest")
    print("Scope: listed companion source files only, excluding the manifest itself; run each paper's verifier for its evidence checks.")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"SNAPSHOT CHECK FAILED: {exc}", file=sys.stderr)
        sys.exit(1)
