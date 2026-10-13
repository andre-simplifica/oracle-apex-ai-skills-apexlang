#!/usr/bin/env python3
"""Shared Oracle APEX version and feature-gate helpers."""

from __future__ import annotations

from dataclasses import dataclass
import re


MINIMUM_SUPPORTED = (26, 2)
REVIEWED_RELEASES = {(26, 2)}
MINIMUM_SQLCL = (26, 3)
MINIMUM_ORDS = (26, 3)
DYNAMIC_CONTENT_RETURN_CLOB = (22, 2)
APEX_26_1 = (26, 1)
VERSION_RE = re.compile(
    r"^\s*(?P<major>\d+)\.(?P<minor>\d+)"
    r"(?:\.(?P<patch>\d+))?(?:\.(?P<revision>\d+))?(?:\+\d+)?\s*$"
)


class ApexVersionError(ValueError):
    """Raised when an APEX version cannot be evaluated safely."""


@dataclass(frozen=True, order=True)
class ApexVersion:
    major: int
    minor: int
    patch: int = 0
    revision: int = 0

    @property
    def feature_release(self) -> tuple[int, int]:
        return (self.major, self.minor)

    @property
    def normalized(self) -> str:
        values = [self.major, self.minor, self.patch, self.revision]
        while len(values) > 2 and values[-1] == 0:
            values.pop()
        return ".".join(str(value) for value in values)


def parse_apex_version(value: str) -> ApexVersion:
    match = VERSION_RE.fullmatch(value)
    if not match:
        raise ApexVersionError(
            "APEX version must use numeric release notation such as 26.2 or 26.2.0+3479"
        )
    return ApexVersion(
        int(match.group("major")),
        int(match.group("minor")),
        int(match.group("patch") or 0),
        int(match.group("revision") or 0),
    )


def evaluate_apex_version(value: str) -> dict:
    version = parse_apex_version(value)
    supported = version.feature_release in REVIEWED_RELEASES
    status = ("SUPPORTED_26_2" if supported else
              "UNSUPPORTED" if version.feature_release < MINIMUM_SUPPORTED else
              "REVIEW_REQUIRED")
    return {
        "schema_version": 1,
        "apex_version": version.normalized,
        "feature_release": f"{version.major}.{version.minor}",
        "minimum_supported": "26.2",
        "support_status": status,
        "supported": supported,
        "capabilities": {
            "core_skill_workflows": supported,
            "dynamic_content_return_clob": version.feature_release >= DYNAMIC_CONTENT_RETURN_CLOB,
            "sql_application_export": supported,
            "readable_yaml_export": False,
            "apex_26_1_public_apis": supported,
            "apex_26_2_public_apis": supported,
            "apexlang_product": version.feature_release >= APEX_26_1,
            "apexlang_file_import": supported,
        },
        "policy": {
            "apexlang_operations": "enabled" if supported else "blocked",
            "apexlang_export": supported,
            "apexlang_import": supported,
            "apexlang_generate": supported,
            "apexlang_validate": supported,
        },
        "official_export_formats": ["apexlang"] if supported else [],
        "sql_recovery_formats": ["split-sql", "monolithic-sql"] if supported else [],
        "minimum_sqlcl": "26.3",
        "minimum_ords": "26.3",
        "runtime_verified": False,
    }


def check_tool_version(value: str, minimum: tuple[int, int], label: str) -> None:
    if not re.fullmatch(r"\d+\.\d+(?:\.\d+){0,3}", value):
        raise ApexVersionError(f"{label} version must be a numeric release/build")
    feature_release = tuple(int(part) for part in value.split(".")[:2])
    if feature_release < minimum:
        raise ApexVersionError(f"{label} {value} is below required {minimum[0]}.{minimum[1]}")
