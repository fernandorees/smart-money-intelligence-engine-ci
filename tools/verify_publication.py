"""Fail closed on unexpected public paths or mismatched SHA-256 digests."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "publication_manifest.json"
KNOWN = {
    "README.md",
    ".github/workflows/synthetic.yml",
    "fixtures/fictional_disclosure.json",
    "tests/test_synthetic_fixture.py",
    "tools/verify_publication.py",
}


def validate():
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    if manifest.get("schema_version") != 1 or set(manifest.get("files", {})) != KNOWN:
        raise ValueError("Missing, unexpected or malformed manifest entries")
    seen = set()
    for path in ROOT.rglob("*"):
        rel = path.relative_to(ROOT)
        if rel.parts[0] == ".git":
            continue
        if path.is_symlink():
            raise ValueError("Unexpected symbolic link: " + str(rel))
        if path.is_file():
            seen.add(rel.as_posix())
    if seen != KNOWN | {"publication_manifest.json"}:
        raise ValueError("Unexpected or missing public paths: " + repr(sorted(seen)))
    for rel, expected in manifest["files"].items():
        if not isinstance(expected, str) or len(expected) != 64:
            raise ValueError("Invalid SHA-256: " + rel)
        actual = hashlib.sha256((ROOT / rel).read_bytes()).hexdigest()
        if actual != expected:
            raise ValueError("Hash mismatch: " + rel)
    print("SYNTHETIC_PUBLIC_ALLOWLIST_VALIDATED")


if __name__ == "__main__":
    validate()
