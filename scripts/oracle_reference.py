#!/usr/bin/env python3
"""Verify pinned Oracle references or find component documents without a network call."""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import re
import sys


def verify_vendor(root: Path) -> dict:
    if root.is_symlink():
        raise ValueError("Oracle reference root must not be a symlink")
    lock = json.loads((root / "upstream-lock.json").read_text(encoding="utf-8"))
    if not re.fullmatch(r"[a-f0-9]{40}", lock.get("commit", "")):
        raise ValueError("Oracle references must be pinned to a full commit")
    if lock.get("repository") != "https://github.com/oracle/skills":
        raise ValueError("Unexpected Oracle reference repository")
    expected = lock.get("files", {})
    if not expected or "LICENSE" not in expected:
        raise ValueError("Oracle reference file manifest or license missing")
    actual = set()
    for path in root.rglob("*"):
        if path.is_symlink():
            raise ValueError("Oracle reference tree contains a symlink")
        if path.is_file() and path.relative_to(root).as_posix() != "upstream-lock.json":
            actual.add(path.relative_to(root).as_posix())
    if actual != set(expected):
        raise ValueError("Oracle reference inventory differs from pinned manifest")
    for name, checksum in expected.items():
        relative = Path(name)
        if relative.is_absolute() or ".." in relative.parts:
            raise ValueError("Unsafe Oracle manifest path")
        if hashlib.sha256((root / relative).read_bytes()).hexdigest() != checksum:
            raise ValueError(f"Oracle reference checksum mismatch: {name}")
    return {"status": "PINNED_FILES_VERIFIED", "commit": lock["commit"],
            "apex_release": lock["apex_release"], "files": len(actual)}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("verify", "search"))
    parser.add_argument("--root", type=Path)
    parser.add_argument("--query", default="")
    args = parser.parse_args()
    base = Path(__file__).resolve().parent
    root = args.root or (base.parent / "vendor/oracle-skills")
    if not args.root and not root.exists():
        root = base.parent.parent / ".oracle-apexlang/vendor/oracle-skills"
    try:
        report = verify_vendor(root)
        if args.action == "search":
            if not args.query.strip():
                raise ValueError("search requires --query")
            results = []
            for path in sorted(root.glob("apex/apexlang/*/apexlang-inventory/assets/**/*.md")):
                content = path.read_text(encoding="utf-8")
                if args.query.lower() in content.lower() or args.query.lower() in str(path).lower():
                    results.append({"path": str(path), "heading": content.splitlines()[0],
                                    "metadata": [line for line in content.splitlines()[:12]
                                                 if line.startswith("- ")]})
            report["matches"] = results
        print(json.dumps(report, indent=2))
        return 0
    except (ValueError, OSError, KeyError) as exc:
        print(f"ERROR {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
