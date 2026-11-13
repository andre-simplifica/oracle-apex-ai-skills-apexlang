#!/usr/bin/env python3
"""Inspect and validate APEXlang; prepare and verify offline import plans. Never imports."""
from __future__ import annotations
import argparse
import datetime as dt
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


def utc_now() -> dt.datetime:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0)


def digest_record(value: dict, field: str) -> str:
    payload = {key: item for key, item in value.items() if key != field}
    return hashlib.sha256(json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def timestamp(value: str) -> dt.datetime:
    result = dt.datetime.fromisoformat(value)
    if result.tzinfo is None or result.utcoffset() != dt.timedelta(0):
        raise SourceError("Evidence timestamps must include UTC")
    return result


def parse_compiler_diagnostics(output: str) -> list[dict]:
    """Read SQLcl compiler blocks, exposing locations and safe grammar facts only.

    Unknown messages can contain SQL, credentials or arbitrary source literals;
    their full text stays in the existing private diagnostic log.
    """
    diagnostics: list[dict] = []
    block: dict = {}
    in_values = False

    def flush() -> None:
        if not block or "type" not in block or "message" not in block:
            return
        kind = block["type"]
        if not re.fullmatch(r"[A-Z][A-Z0-9_]{0,79}", kind):
            kind = "COMPILER_ERROR"
        message = block["message"]
        patterns = (
            r"Invalid property: [A-Za-z][A-Za-z0-9_-]*",
            r"Reference not found: @[A-Za-z0-9_-]+",
            r"(?:Invalid LOV required parameter|Missing required parameter(?: \(\d+\))?): "
            r"[A-Za-z][A-Za-z0-9_ .-]{0,150}(?: \([A-Za-z0-9_-]+\))?",
        )
        if not any(re.fullmatch(pattern, message) for pattern in patterns):
            message = "Compiler reported " + kind + "; inspect the private diagnostic log."
        file = block.get("file", "")
        path = Path(file)
        if not file or path.is_absolute() or ".." in path.parts or re.search(r"[\x00-\x1f]", file):
            file = None
        values = list(dict.fromkeys(block.get("valid_values", [])))[:50]
        item = {"file": file, "line": block.get("line", 0), "column": block.get("column", 0),
                "type": kind, "severity": "error", "message": message}
        property_match = re.fullmatch(r"Invalid property: ([A-Za-z][A-Za-z0-9_-]*)", message)
        if not property_match:
            property_match = re.search(r" - ([A-Za-z][A-Za-z0-9_-]*) \([A-Za-z0-9_-]+\)$", message)
        if property_match:
            item["property"] = property_match.group(1)
        if values:
            item["valid_values"] = values
        if values or kind == "INVALID_PROPERTY" or kind.startswith("MISSING_REQUIRED"):
            item["hint"] = "Check this property in the Oracle inventory for the application's reviewed release."
        diagnostics.append(item)

    for raw in re.sub(r"\x1b\[[0-9;]*m", "", output).splitlines():
        line = raw.strip()
        field = re.match(r"^(File|Line|Column|Type|Error):\s*(.*)$", line)
        if field:
            key, value = field.groups()
            if key == "File":
                flush()
                block = {"file": value}
                in_values = False
            elif block:
                if key in ("Line", "Column"):
                    block[key.lower()] = int(value) if re.fullmatch(r"\d{1,8}", value) else 0
                else:
                    block["message" if key == "Error" else "type"] = value
            continue
        if not line:
            flush()
            block = {}
            in_values = False
            continue
        values = re.match(r"^Valid (?:parameters|values|options) are:\s*(.*)$", line, re.I)
        if block and values:
            in_values = True
            block["valid_values"] = []
            value = values.group(1)
        elif block and in_values and line.startswith("-"):
            value = line[1:].strip()
        else:
            if block and "message" in block and not in_values:
                block["message"] += " " + line
            continue
        if re.fullmatch(r"[A-Za-z][A-Za-z0-9_-]{0,99}", value):
            block["valid_values"].append(value)
    flush()
    return diagnostics


def validate(root: Path, apex_version: str, binary: str, deployment: Path | None = None) -> dict:
    report = inspect(root, apex_version)
    version = sqlcl_version(binary)
    effective_deployment = deployment or root / "deployments/default.json"
    if not effective_deployment.is_file() or effective_deployment.is_symlink():
        raise SourceError("Deployment file is missing or a symlink")
    deployment_hash = hashlib.sha256(effective_deployment.read_bytes()).hexdigest()
    command = ("apex validate -input " + quoted(str(root.resolve()))
               + " -deployment " + quoted(str(effective_deployment.resolve())))
    started = utc_now()
    process = subprocess.run([binary, "/nolog", "-e", "set define off", "-e", command],
                             input="", capture_output=True, text=True, timeout=180, cwd=root)
    output = process.stdout + process.stderr
    clean = re.sub(r"\x1b\[[0-9;]*m", "", output)
    diagnostics = parse_compiler_diagnostics(clean)
    for diagnostic in diagnostics:
        if "property" in diagnostic:
            diagnostic["reference_search"] = {"query": diagnostic["property"], "kind": "definition",
                                               "apex_release": require_release(apex_version)["feature_release"]}
    succeeded = process.returncode == 0 and bool(re.search(r"(?m)^\s*Validation successful\.?\s*$", clean))
    if diagnostics or re.search(r"(?mi)^\s*(?:ORA-\d+|PLS-\d+|SP2-\d+|Error:|Validation failed|APEXlang Compile Errors:)", clean):
        succeeded = False
    with tempfile.NamedTemporaryFile(mode="w", prefix="apexlang-validation-", suffix=".log",
                                     encoding="utf-8", delete=False) as handle:
        handle.write(output)
        log_path = handle.name
    if (inspect(root, apex_version)["tree_sha256"] != report["tree_sha256"]
            or hashlib.sha256(effective_deployment.read_bytes()).hexdigest() != deployment_hash):
        raise SourceError("Source or deployment changed during validation; validate a stable candidate")
    report.update(status="COMPILER_VALIDATED" if succeeded else "COMPILER_FAILED",
                  compiler_validated=succeeded, sqlcl_version=version, diagnostic_log=log_path,
                  diagnostics=diagnostics[:100], diagnostic_count=len(diagnostics),
                  diagnostics_truncated=len(diagnostics) > 100,
                  source_root=str(root.resolve()), deployment_path=str(effective_deployment.resolve()),
                  deployment_sha256=deployment_hash, started_at=started.isoformat(),
                  completed_at=utc_now().isoformat(), evidence_schema_version=1)
    report["report_sha256"] = digest_record(report, "report_sha256")
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


PLAN_LIFETIME = dt.timedelta(minutes=30)


def import_plan(args: argparse.Namespace, now: dt.datetime | None = None) -> dict:
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
    created = now or utc_now()
    plan = {"status": "PLAN_ONLY", "executes_database_changes": False,
            "compiler_validated": False, "runtime_verified": False,
            "target": {"app_id": args.app_id, "workspace": args.workspace, "schema": args.schema,
                       "environment": args.environment, "apex_version": args.apex_version},
            "plan_schema_version": 1, "created_at": created.isoformat(),
            "expires_at": (created + PLAN_LIFETIME).isoformat(),
            "source_root": str(root.resolve()), "deployment_path": str(deployment.resolve()),
            "source_mmd_version": candidate["source_mmd_version"],
            "toolchain": {"sqlcl_version": args.sqlcl_version, "ords_version": args.ords_version},
            "allow_app_id_remap": args.allow_app_id_remap,
            "source_sha256": candidate["tree_sha256"], "live_sha256": live["tree_sha256"],
            "baseline_sha256": baseline["tree_sha256"],
            "deployment_sha256": hashlib.sha256(deployment.read_bytes()).hexdigest(),
            "mode": "selected-files" if selected else "complete-application",
            "selected_files": selected, "command": command,
            "required_before_execution": ["confirmed named connection and same-session target identity",
                "explicit import authorization for this target and scope", "owned application/Working Copy coordination",
                "fresh SQL recovery export and reviewed supporting objects", "all dependencies included",
                "successful full-tree compiler validation with this deployment", "recheck drift immediately before import"],
            "required_after_execution": ["import diagnostics checked", "affected metadata re-exported and diff reviewed",
                "functional and authorization canaries", "rollback artifact and exact Git revision recorded"]}

    plan["plan_sha256"] = digest_record(plan, "plan_sha256")
    return plan


def read_record(path: Path) -> dict:
    if path.is_symlink() or not path.is_file():
        raise SourceError("Evidence must be a regular JSON file")
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise SourceError("Evidence must be a JSON object")
    return value


def verify_plan(args: argparse.Namespace, now: dt.datetime | None = None) -> dict:
    """Check caller-supplied snapshots/evidence. Does not authenticate a live target."""
    plan = read_record(args.plan)
    if plan.get("plan_schema_version") != 1 or plan.get("plan_sha256") != digest_record(plan, "plan_sha256"):
        raise SourceError("Plan integrity check failed; generate a new plan")
    current_time = now or utc_now()
    created, expires = timestamp(plan["created_at"]), timestamp(plan["expires_at"])
    if created > current_time or expires - created != PLAN_LIFETIME or current_time >= expires:
        raise SourceError("Plan expired or its validity window is invalid; generate a new plan")
    # Rebuild from independently supplied current scope/target, candidate, baseline
    # and fresh live export. A new live-export directory is allowed; its bytes must agree.
    current = import_plan(args, now=created)
    changed = sorted(key for key in set(plan) | set(current) if plan.get(key) != current.get(key))
    if changed:
        raise SourceError("Plan no longer matches the candidate, target or snapshots: " + ", ".join(changed))
    actual_sqlcl = sqlcl_version(sqlcl_binary(getattr(args, "sqlcl", None)))
    if actual_sqlcl != plan["toolchain"]["sqlcl_version"]:
        raise SourceError("Current SQLcl build differs from the reviewed plan; validate and plan again")
    evidence = read_record(args.validation)
    if (evidence.get("evidence_schema_version") != 1
            or evidence.get("report_sha256") != digest_record(evidence, "report_sha256")
            or evidence.get("status") != "COMPILER_VALIDATED"
            or evidence.get("compiler_validated") is not True
            or evidence.get("diagnostic_count") != 0):
        raise SourceError("A successful, intact full-tree compiler report is required")
    bindings = {"source_root": plan["source_root"], "tree_sha256": plan["source_sha256"],
                "deployment_path": plan["deployment_path"], "deployment_sha256": plan["deployment_sha256"],
                "source_mmd_version": plan["source_mmd_version"],
                "target_apex_version": require_release(args.apex_version)["apex_version"],
                "sqlcl_version": args.sqlcl_version}
    if any(evidence.get(key) != value for key, value in bindings.items()):
        raise SourceError("Compiler report belongs to different sources, deployment, version or SQLcl build")
    if not timestamp(evidence["started_at"]) <= timestamp(evidence["completed_at"]) <= current_time:
        raise SourceError("Compiler report timestamps are inconsistent or in the future")
    return {"status": "PLAN_VERIFIED_OFFLINE", "plan_sha256": plan["plan_sha256"],
            "checked_at": current_time.isoformat(), "expires_at": plan["expires_at"],
            "compiler_validated": True, "executes_database_changes": False,
            "live_identity_verified": False, "authorization_checked": False, "runtime_verified": False,
            "target": plan["target"], "selected_files": plan["selected_files"],
            "required_before_execution": plan["required_before_execution"],
            "evidence_boundary": "Local consistency only; hashes are not signatures or approval. "
                                 "The caller must obtain a fresh export from the confirmed target and "
                                 "verify the saved connection and identity in the executing session."}


def check_output_path(path: Path | None, roots: list[Path]) -> None:
    if path is None:
        return
    if path.exists() or path.is_symlink():
        raise SourceError("Report output already exists; choose a new private report path")
    if any(path.resolve().is_relative_to(root.resolve()) for root in roots):
        raise SourceError("Write reports outside candidate, baseline and live application trees")


def write_report(path: Path, report: dict) -> None:
    descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
        json.dump(report, handle, indent=2)
        handle.write("\n")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="action", required=True)
    for name in ("inspect", "validate", "plan-import", "verify-plan"):
        p = sub.add_parser(name)
        p.add_argument("--root", type=Path, required=True)
        p.add_argument("--apex-version", required=True)
        p.add_argument("--output", type=Path, help="New private JSON report outside the application trees")
        if name == "validate":
            p.add_argument("--sqlcl")
            p.add_argument("--deployment", type=Path)
        if name in ("plan-import", "verify-plan"):
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
        if name == "verify-plan":
            p.add_argument("--plan", type=Path, required=True)
            p.add_argument("--validation", type=Path, required=True)
            p.add_argument("--sqlcl", help="Approved SQLcl launcher; its current build must match the plan")
    args = parser.parse_args()
    try:
        roots = [args.root] + ([args.baseline, args.live] if hasattr(args, "baseline") else [])
        check_output_path(args.output, roots)
        if args.action == "inspect":
            report = inspect(args.root, args.apex_version)
        elif args.action == "validate":
            report = validate(args.root, args.apex_version, sqlcl_binary(args.sqlcl), args.deployment)
        elif args.action == "verify-plan":
            report = verify_plan(args)
        else:
            report = import_plan(args)
        if args.output:
            write_report(args.output, report)
        print(json.dumps(report, indent=2))
        return 1 if report["status"] == "COMPILER_FAILED" else 0
    except (ValueError, OSError, KeyError, TypeError, AttributeError, subprocess.TimeoutExpired) as exc:
        print(f"ERROR {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
