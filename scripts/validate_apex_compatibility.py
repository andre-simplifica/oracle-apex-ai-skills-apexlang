#!/usr/bin/env python3
"""Validate Oracle APEX support and feature gates for this skill kit."""

from __future__ import annotations

import argparse
import json
import sys

from apex_version import ApexVersionError, evaluate_apex_version, check_tool_version, MINIMUM_SQLCL, MINIMUM_ORDS


REQUIREMENT_KEYS = {
    "supported-apex": ("capabilities", "core_skill_workflows"),
    "dynamic-content": ("capabilities", "dynamic_content_return_clob"),
    "sql-export": ("capabilities", "sql_application_export"),
    "readable-yaml-export": ("capabilities", "readable_yaml_export"),
    "apex-26.1-public-apis": ("capabilities", "apex_26_1_public_apis"),
    "apex-26.2-public-apis": ("capabilities", "apex_26_2_public_apis"),
    "file-import": ("capabilities", "apexlang_file_import"),
    "apexlang": ("policy", "apexlang_export"),
}


def requirement_available(report: dict, requirement: str) -> bool:
    section, key = REQUIREMENT_KEYS[requirement]
    return bool(report[section][key])


def print_text(report: dict, requirement: str | None) -> None:
    capabilities = report["capabilities"]
    policy = report["policy"]
    print(f"APEX_VERSION {report['apex_version']}")
    print(f"APEX_FEATURE_RELEASE {report['feature_release']}")
    print(f"APEX_MINIMUM_SUPPORTED {report['minimum_supported']}")
    print(f"APEX_SUPPORT {report['support_status']}")
    print("EVIDENCE CALLER_SUPPLIED_NOT_LIVE_VERIFIED")
    print("RUNTIME_VERIFIED NO")
    print("SQLCL_VERSION " + (report["toolchain"]["sqlcl_version"] or "NOT_PROVIDED"))
    print("ORDS_VERSION " + (report["toolchain"]["ords_version"] or "NOT_PROVIDED"))
    print(
        "DYNAMIC_CONTENT_RETURN_CLOB "
        + (
            "AVAILABLE"
            if capabilities["dynamic_content_return_clob"]
            else "UNAVAILABLE"
        )
    )
    print(
        "APEX_26_1_PUBLIC_APIS "
        + ("AVAILABLE" if capabilities["apex_26_1_public_apis"] else "UNAVAILABLE")
    )
    print(
        "READABLE_YAML_EXPORT "
        + ("AVAILABLE" if capabilities["readable_yaml_export"] else "UNAVAILABLE")
    )
    print(
        "APEXLANG_PRODUCT "
        + ("AVAILABLE" if capabilities["apexlang_product"] else "UNAVAILABLE")
    )
    print(f"APEXLANG_SKILL_POLICY {policy['apexlang_operations'].upper()}")
    print(
        "OFFICIAL_EXPORT_FORMATS "
        + (",".join(report["official_export_formats"]) or "NONE")
    )
    if requirement:
        print(
            f"REQUIREMENT {requirement} "
            + ("AVAILABLE" if requirement_available(report, requirement) else "BLOCKED")
        )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apex-version", required=True)
    parser.add_argument("--sqlcl-version")
    parser.add_argument("--ords-version")
    parser.add_argument("--require", choices=tuple(REQUIREMENT_KEYS))
    parser.add_argument("--json", action="store_true", dest="as_json")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    try:
        report = evaluate_apex_version(args.apex_version)
        if args.sqlcl_version:
            check_tool_version(args.sqlcl_version, MINIMUM_SQLCL, "SQLcl")
        if args.ords_version:
            check_tool_version(args.ords_version, MINIMUM_ORDS, "ORDS")
        if args.require in {"apexlang", "file-import"} and not (
            args.sqlcl_version and args.ords_version
        ):
            raise ApexVersionError("APEXlang/file-import requires confirmed --sqlcl-version and --ords-version")
        report["toolchain"] = {
            "sqlcl_version": args.sqlcl_version,
            "ords_version": args.ords_version,
            "evidence": "caller-supplied, not verified live",
            "complete": bool(args.sqlcl_version and args.ords_version),
        }
    except ApexVersionError as exc:
        print(f"ERROR {exc}", file=sys.stderr)
        return 2

    if args.as_json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        print_text(report, args.require)

    if not report["supported"]:
        print("ERROR APEX release is not reviewed by this kit; minimum 26.2, reviewed release 26.2", file=sys.stderr)
        return 2
    if args.require and not requirement_available(report, args.require):
        if args.require == "apexlang":
            reason = "APEXlang is blocked until the release is reviewed"
        else:
            reason = f"Requirement {args.require} is unavailable on APEX {report['apex_version']}"
        print(f"ERROR {reason}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
