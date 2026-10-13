#!/usr/bin/env python3
"""Inspect APEXlang, validate offline with SQLcl, and prepare import plans. Never imports."""
from __future__ import annotations
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile

from apex_version import (ApexVersionError, evaluate_apex_version, parse_apex_version,
                          check_tool_version, MINIMUM_SQLCL, MINIMUM_ORDS)


class SourceError(ValueError):
    pass


def quoted(value: str) -> str:
    if not value or re.search(r'[\x00-\x1f"\\;&|`$]', value):
        raise SourceError("Unsupported characters in SQLcl command argument")
    return '"' + value + '"'


def require_release(value: str) -> dict:
    report = evaluate_apex_version(value)
    if not report["supported"]:
        raise SourceError(f"APEX release blocked: {report['support_status']}; minimum/reviewed release is 26.2")
    return report


def files(root: Path) -> dict[str, str]:
    if root.is_symlink() or not root.is_dir():
        raise SourceError("Application root must be a real directory")
    result = {}
    for path in sorted(root.rglob("*")):
        if path.is_symlink():
            raise SourceError("Application source must not contain symlinks")
        if ".git" in path.relative_to(root).parts:
            raise SourceError("Application directory must be below the Git repository root")
        if path.is_file():
            result[path.relative_to(root).as_posix()] = hashlib.sha256(path.read_bytes()).hexdigest()
    return result


def inspect(root: Path, apex_version: str) -> dict:
    target = require_release(apex_version)
    inventory = files(root)
    for required in ("application.apx", ".apex/apexlang.json", "deployments/default.json"):
        if required not in inventory or not (root / required).stat().st_size:
            raise SourceError(f"Missing or empty APEXlang artifact: {required}")
    model = json.loads((root / ".apex/apexlang.json").read_text(encoding="utf-8"))
    source_version = model.get("mmdVersion")
    if not isinstance(source_version, str):
        raise SourceError("Missing mmdVersion in .apex/apexlang.json")
    source = require_release(source_version)
    if source["feature_release"] != target["feature_release"]:
        raise SourceError("Source and target APEX feature releases differ; perform a reviewed re-export")
    pages = sorted(name for name in inventory if name.startswith("pages/") and name.endswith(".apx"))
    if any(len(Path(name).parts) != 2 for name in pages):
        raise SourceError("APEXlang pages must be directly under pages/")
    deployment = json.loads((root / "deployments/default.json").read_text(encoding="utf-8"))
    if not isinstance(deployment, dict):
        raise SourceError("Default deployment must be a JSON object")
    payload = json.dumps(inventory, sort_keys=True).encode()
    return {"status": "STRUCTURE_INSPECTED", "compiler_validated": False,
            "runtime_verified": False, "source_mmd_version": source_version,
            "target_apex_version": target["apex_version"], "pages": pages,
            "files": inventory, "tree_sha256": hashlib.sha256(payload).hexdigest(),
            "generated_artifacts": sorted(x for x in inventory if x.startswith("generated-artifacts/"))}


def sqlcl_binary(explicit: str | None) -> str:
    binary = explicit or os.environ.get("SQLCL_BIN") or shutil.which("sql")
    if not binary or not Path(binary).is_file() or not os.access(binary, os.X_OK):
        raise SourceError("Set SQLCL_BIN to the approved SQLcl launcher or put sql on PATH")
    return str(Path(binary).absolute())


def sqlcl_version(binary: str) -> str:
    process = subprocess.run([binary, "-version"], input="\n", capture_output=True, text=True, timeout=30)
    output = process.stdout + process.stderr
    match = (re.search(r"\bBuild:\s*(\d+\.\d+(?:\.\d+){0,3})", output)
             or re.search(r"SQLcl:\s+Release\s+(\d+\.\d+(?:\.\d+){0,3})", output))
    if process.returncode or not match:
        raise SourceError("Could not verify SQLcl version")
    value = match.group(1)
    check_tool_version(value, MINIMUM_SQLCL, "SQLcl")
    return value


def validate(root: Path, apex_version: str, binary: str, deployment: Path | None = None) -> dict:
    report = inspect(root, apex_version)
    version = sqlcl_version(binary)
    command = "apex validate -input " + quoted(str(root.resolve()))
    if deployment is not None:
        if not deployment.is_file() or deployment.is_symlink():
            raise SourceError("Deployment file is missing or a symlink")
        command += " -deployment " + quoted(str(deployment.resolve()))
    # No saved connection or login string is ever used. Preserve the complete
    # diagnostic locally; compiler messages can quote sensitive source text.
    process = subprocess.run([binary, "/nolog"],
                             input="set define off\n" + command + "\nexit\n",
                             capture_output=True, text=True, timeout=180, cwd=root)
    output = process.stdout + process.stderr
    clean = re.sub(r"\x1b\[[0-9;]*m", "", output)
    succeeded = process.returncode == 0 and bool(re.search(r"(?m)^\s*Validation successful\.?\s*$", clean))
    if re.search(r"(?mi)^\s*(?:ORA-\d+|PLS-\d+|SP2-\d+|Error:|Validation failed)", clean):
        succeeded = False
    with tempfile.NamedTemporaryFile(mode="w", prefix="apexlang-validation-", suffix=".log",
                                     encoding="utf-8", delete=False) as handle:
        handle.write(output)
        log_path = handle.name
    report.update(status="COMPILER_VALIDATED" if succeeded else "COMPILER_FAILED",
                  compiler_validated=succeeded, sqlcl_version=version, diagnostic_log=log_path)
    return report


def selected_path(root: Path, value: str) -> str:
    relative = Path(value)
    if relative.is_absolute() or ".." in relative.parts or not relative.parts:
        raise SourceError("Selected file must be application-relative")
    quoted(value)
    # Intentionally narrower than SQLcl glob support: plans enumerate exact files.
    if any(char in value for char in "*?[]"):
        raise SourceError("Import plans require explicit files, not wildcards")
    parts = tuple(part.lower() for part in relative.parts)
    if relative.suffix.lower() != ".apx" or parts[0] not in ("pages", "shared-components"):
        raise SourceError("File import supports only reviewed page/shared-component APX paths")
    if any(part in ("themes", "theme", "templates", "plugins", "plug-ins", "supporting-objects") for part in parts):
        raise SourceError("Theme/template/plugin/supporting-object changes require a complete reviewed import")
    if not (root / relative).is_file() or (root / relative).is_symlink():
        raise SourceError("Selected file is missing or unsafe; deletion needs a separate reviewed workflow")
    return relative.as_posix()


def import_plan(args: argparse.Namespace) -> dict:
    root = args.root
    candidate = inspect(root, args.apex_version)
    check_tool_version(args.sqlcl_version, MINIMUM_SQLCL, "SQLcl")
    check_tool_version(args.ords_version, MINIMUM_ORDS, "ORDS")
    if args.app_id <= 0:
        raise SourceError("Application ID must be positive")
    baseline = inspect(args.baseline, args.apex_version)
    live = inspect(args.live, args.apex_version)
    if args.files and args.environment == "production":
        raise SourceError("Production requires a complete application import")
    selected = sorted({selected_path(root, value) for value in args.files}) if args.files else []
    # Dependencies can be outside the selected files. Reconcile the whole fresh
    # export instead of silently compiling against a stale shared component.
    compare = set(baseline["files"]) | set(live["files"])
    drift = sorted(name for name in compare if baseline["files"].get(name) != live["files"].get(name))
    if drift:
        raise SourceError("Live changes require reconciliation before planning: " + ", ".join(drift))
    command = ("apex import -input " + quoted(str(root.resolve())) + f" -id {args.app_id}"
               + " -workspace " + quoted(args.workspace) + " -schema " + quoted(args.schema))
    deployment = args.deployment or root / "deployments/default.json"
    if not deployment.is_file() or deployment.is_symlink():
        raise SourceError("A reviewed deployment JSON file is required")
    metadata = json.loads(deployment.read_text(encoding="utf-8"))
    if not isinstance(metadata, dict):
        raise SourceError("Deployment must be an object")
    source_id = metadata.get("app", {}).get("id")
    if source_id is not None and source_id != args.app_id and not args.allow_app_id_remap:
        raise SourceError("Deployment app ID differs; inspect Working Copy/remapping before --allow-app-id-remap")
    for actual, expected, label in (
        (metadata.get("workspace", {}).get("name"), args.workspace, "workspace"),
        (metadata.get("app", {}).get("databaseSession", {}).get("parsingSchema"), args.schema, "schema"),
    ):
        if actual is not None and actual != expected:
            raise SourceError(f"Deployment {label} differs from the requested target")
    command += " -deployment " + quoted(str(deployment.resolve()))
    if selected:
        command += " -files " + " ".join(quoted(str((root / name).resolve())) for name in selected)
    return {"status": "PLAN_ONLY", "executes_database_changes": False,
            "compiler_validated": False, "runtime_verified": False,
            "target": {"app_id": args.app_id, "workspace": args.workspace, "schema": args.schema,
                       "environment": args.environment, "apex_version": args.apex_version},
            "source_sha256": candidate["tree_sha256"], "live_sha256": live["tree_sha256"],
            "deployment_sha256": hashlib.sha256(deployment.read_bytes()).hexdigest(),
            "mode": "selected-files" if selected else "complete-application",
            "selected_files": selected, "command": command,
            "required_before_execution": ["confirmed named connection and same-session target identity",
                "explicit import authorization for this target and scope", "owned application/Working Copy coordination",
                "fresh SQL recovery export and reviewed supporting objects", "all dependencies included",
                "successful full-tree compiler validation with this deployment", "recheck drift immediately before import"],
            "required_after_execution": ["import diagnostics checked", "affected metadata re-exported and diff reviewed",
                "functional and authorization canaries", "rollback artifact and exact Git revision recorded"]}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="action", required=True)
    for name in ("inspect", "validate", "plan-import"):
        p = sub.add_parser(name)
        p.add_argument("--root", type=Path, required=True)
        p.add_argument("--apex-version", required=True)
        if name == "validate":
            p.add_argument("--sqlcl")
            p.add_argument("--deployment", type=Path)
        if name == "plan-import":
            p.add_argument("--sqlcl-version", required=True)
            p.add_argument("--ords-version", required=True)
            p.add_argument("--environment", choices=("development", "test", "production"), required=True)
            p.add_argument("--app-id", type=int, required=True)
            p.add_argument("--workspace", required=True)
            p.add_argument("--schema", required=True)
            p.add_argument("--deployment", type=Path)
            p.add_argument("--allow-app-id-remap", action="store_true")
            p.add_argument("--baseline", type=Path, required=True)
            p.add_argument("--live", type=Path, required=True)
            p.add_argument("--files", nargs="+")
    args = parser.parse_args()
    try:
        if args.action == "inspect":
            report = inspect(args.root, args.apex_version)
        elif args.action == "validate":
            report = validate(args.root, args.apex_version, sqlcl_binary(args.sqlcl), args.deployment)
        else:
            report = import_plan(args)
        print(json.dumps(report, indent=2))
        return 1 if report["status"] == "COMPILER_FAILED" else 0
    except (ValueError, OSError, KeyError, TypeError, AttributeError, subprocess.TimeoutExpired) as exc:
        print(f"ERROR {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
