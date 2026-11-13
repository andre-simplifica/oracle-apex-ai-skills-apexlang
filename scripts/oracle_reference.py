#!/usr/bin/env python3
"""Verify pinned Oracle references or find component documents without a network call."""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import re
import sys
import shutil
import tempfile
import unicodedata

from apexlang_tools import inspect, validate, sqlcl_binary, require_release, digest_record, utc_now, write_report
from apex_version import check_tool_version, MINIMUM_SQLCL


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


# Search vocabulary is routing metadata, never an alternate grammar definition.
ALIASES = {
    "relatorio interativo": "interactive report", "relatorios interativos": "interactive report",
    "grade interativa": "interactive grid", "grade editavel": "interactive grid",
    "mestre detalhe": "master detail", "acao dinamica": "dynamic action",
    "acoes dinamicas": "dynamic action", "formulario": "form", "formularios": "form",
    "relatorio": "report", "relatorios": "report", "grafico": "chart", "graficos": "chart",
    "calendario": "calendar", "atualizacao": "refresh", "atualizar": "refresh",
    "filtro": "filter", "filtros": "filter", "botao": "button", "botoes": "button",
    "autorizacao": "authorization", "autenticacao": "authentication", "regiao": "region",
}
STOP_WORDS = {"a", "an", "and", "the", "with", "of", "for", "e", "o", "os", "as", "um", "uma", "com", "de", "do", "da", "para"}


def normalize(value: str) -> str:
    value = re.sub(r"([a-z0-9])([A-Z])", r"\1 \2", value)
    value = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode().lower()
    return " ".join(re.findall(r"[a-z0-9]+", value))


def query_terms(query: str) -> list[str]:
    normalized = normalize(query)
    for phrase, replacement in sorted(ALIASES.items(), key=lambda item: -len(item[0])):
        normalized = re.sub(r"\b" + re.escape(phrase) + r"\b", replacement, normalized)
    return sorted(set(normalized.split()) - STOP_WORDS)


def reference_paths() -> tuple[Path, Path]:
    base = Path(__file__).resolve().parent
    kit = base.parent
    if (kit / "vendor/oracle-skills").is_dir():
        return (kit / "vendor/oracle-skills",
                kit / "skills/oracle-apexlang-dev/references/example-catalog.json")
    project = base.parent.parent
    return (project / ".oracle-apexlang/vendor/oracle-skills",
            project / ".agents/skills/oracle-apexlang-dev/references/example-catalog.json")


def safe_member(root: Path, name: str) -> Path:
    relative = Path(name)
    if relative.is_absolute() or ".." in relative.parts or not relative.parts:
        raise ValueError("Catalog paths must remain inside the pinned Oracle reference")
    path = root / relative
    if path.is_symlink() or not path.resolve().is_relative_to(root.resolve()):
        raise ValueError("Unsafe catalog path")
    return path


def catalog_data(root: Path, catalog_path: Path, release: str) -> dict:
    if catalog_path.is_symlink():
        raise ValueError("Catalog must not be a symlink")
    catalog = json.loads(catalog_path.read_text(encoding="utf-8"))
    lock = json.loads((root / "upstream-lock.json").read_text(encoding="utf-8"))
    if (catalog.get("schema_version") != 1 or catalog.get("apex_release") != release
            or catalog.get("oracle_commit") != lock["commit"] or catalog.get("license") != "UPL-1.0"):
        raise ValueError("Catalog release, license or Oracle pin differs from the reviewed inventory")
    applications = catalog["applications"]
    if not isinstance(applications, dict) or not applications:
        raise ValueError("Catalog needs complete example application contexts")
    for name, application in applications.items():
        if not re.fullmatch(r"[a-z0-9-]+", name):
            raise ValueError("Invalid example application identifier")
        report = inspect(safe_member(root, application["path"]), release)
        if report["source_mmd_version"] != application["mmd_version"]:
            raise ValueError("Example MMD differs from the catalog")
        application["tree_sha256"] = report["tree_sha256"]
    ids: set[str] = set()
    for example in catalog["examples"]:
        if not re.fullmatch(r"[a-z0-9-]+", example["id"]) or example["id"] in ids:
            raise ValueError("Example identifiers must be unique stable slugs")
        ids.add(example["id"])
        application = applications[example["application"]]
        app_root = safe_member(root, application["path"])
        if not example["files"] or not example["dependencies"] or not example["adaptation"]:
            raise ValueError("Examples must declare source, dependencies and adaptation limits")
        for name in example["files"]:
            path = safe_member(app_root, name)
            if not path.is_file() or path.suffix != ".apx":
                raise ValueError("Example source must be an existing pinned APX file")
    return catalog


def example_evidence(catalog: dict, path: Path) -> dict:
    if path.is_symlink() or not path.is_file():
        raise ValueError("Compiler evidence for the example catalog is missing")
    evidence = json.loads(path.read_text(encoding="utf-8"))
    if (evidence.get("schema_version") != 1 or evidence.get("apex_release") != catalog["apex_release"]
            or evidence.get("oracle_commit") != catalog["oracle_commit"]
            or evidence.get("evidence_sha256") != digest_record(evidence, "evidence_sha256")):
        raise ValueError("Example compiler evidence integrity or release mismatch")
    if set(evidence["applications"]) != set(catalog["applications"]):
        raise ValueError("Example compiler evidence has a different application set")
    for name, application in catalog["applications"].items():
        record = evidence["applications"][name]
        check_tool_version(record["sqlcl_version"], MINIMUM_SQLCL, "SQLcl")
        if (record.get("compiler_validated") is not True or record.get("runtime_verified") is not False
                or record.get("source_tree_sha256") != application["tree_sha256"]
                or record.get("source_mmd_version") != application["mmd_version"]
                or record.get("scope") != "complete-example-application"):
            raise ValueError("Example compiler evidence does not bind the current complete application")
    return evidence


def verify_catalog(root: Path, catalog_path: Path) -> dict:
    release = require_release(json.loads((root / "upstream-lock.json").read_text())["apex_release"])["feature_release"]
    catalog = catalog_data(root, catalog_path, release)
    example_evidence(catalog, catalog_path.with_name("example-validation.json"))
    return {"examples": len(catalog["examples"]), "applications": len(catalog["applications"]),
            "apex_release": release, "compiler_validated": True, "runtime_verified": False}


def reference_records(root: Path, catalog_path: Path, apex_version: str = "26.2") -> list[dict]:
    release = require_release(apex_version)["feature_release"]
    verified = verify_vendor(root)
    if verified["apex_release"] != release:
        raise ValueError("Requested release differs from the pinned Oracle reference")
    catalog = catalog_data(root, catalog_path, release)
    evidence = example_evidence(catalog, catalog_path.with_name("example-validation.json"))
    assets = root / "apex/apexlang" / release / "apexlang-inventory/assets"
    records = []
    for path in sorted(assets.rglob("*.md")):
        content = path.read_text(encoding="utf-8")
        relative = path.relative_to(assets).as_posix()
        heading = content.splitlines()[0]
        records.append({"id": "oracle:" + release + ":" + relative.removesuffix(".md"),
                        "kind": "definition", "apex_release": release, "heading": heading,
                        "path": str(path), "summary": heading.lstrip("# "),
                        "metadata": [line[:200] for line in content.splitlines()[:12] if line.startswith("- ")][:6],
                        "_search": normalize(relative + " " + content),
                        "_title": normalize(relative + " " + heading)})
    for example in catalog["examples"]:
        application = catalog["applications"][example["application"]]
        context = safe_member(root, application["path"])
        records.append({"id": "example:" + release + ":" + example["id"], "kind": "example",
                        "apex_release": release, "heading": example["title"], "summary": example["description"],
                        "path": str(context / example["files"][0]), "files": example["files"],
                        "application_root": str(context), "dependencies": example["dependencies"],
                        "adaptation": example["adaptation"], "source_mmd_version": application["mmd_version"],
                        "compiler_validated": True, "runtime_verified": False,
                        "readiness": "compiler-validated-reference",
                        "sqlcl_version": evidence["applications"][example["application"]]["sqlcl_version"],
                        "source_url": "https://github.com/oracle/skills/tree/" + catalog["oracle_commit"] + "/" + application["path"],
                        "_search": normalize(" ".join([example["title"], example["description"], *example["keywords"]])),
                        "_title": normalize(example["title"] + " " + " ".join(example["keywords"]))})
    return records


def public_record(record: dict) -> dict:
    return {key: value for key, value in record.items() if not key.startswith("_")}


def search_references(root: Path, catalog: Path, query: str, apex_version: str = "26.2",
                      kind: str = "all", limit: int = 5, offset: int = 0) -> dict:
    if not 1 <= limit <= 20 or offset < 0:
        raise ValueError("Search limit must be 1..20 and offset must be nonnegative")
    terms = query_terms(query)
    if not terms or len(query) > 500:
        raise ValueError("Search needs a nonempty query of at most 500 characters")
    matches = []
    for record in reference_records(root, catalog, apex_version):
        if kind not in ("all", record["kind"]):
            continue
        words = set(record["_search"].split())
        matched = [term for term in terms if term in words]
        if len(matched) * 2 < len(terms):
            continue
        title = set(record["_title"].split())
        score = 20 * len(matched) + 15 * sum(term in title for term in terms)
        if len(matched) == len(terms):
            score += 30
        hit = public_record(record)
        # Search is a compact index; read returns dependencies and adaptation details.
        for key in ("files", "dependencies", "adaptation", "application_root"):
            hit.pop(key, None)
        hit.update(score=score, matched_terms=matched)
        matches.append(hit)
    matches.sort(key=lambda hit: (-hit["score"], hit["id"]))
    end = offset + limit
    return {"status": "REFERENCES_FOUND", "apex_release": require_release(apex_version)["feature_release"],
            "query": query, "total_matches": len(matches), "matches": matches[offset:end],
            "next_offset": end if end < len(matches) else None}


def read_reference(root: Path, catalog: Path, identifier: str, apex_version: str = "26.2",
                   offset: int = 0, max_chars: int = 4000, selected_file: str | None = None) -> dict:
    if offset < 0 or not 1 <= max_chars <= 12000:
        raise ValueError("Read size must be 1..12000 characters and offset must be nonnegative")
    records = {item["id"]: item for item in reference_records(root, catalog, apex_version)}
    if identifier not in records:
        raise ValueError("Unknown reference ID for this reviewed release")
    record = records[identifier]
    path = Path(record["path"])
    if selected_file:
        if record["kind"] != "example" or selected_file not in record["files"]:
            raise ValueError("File is not declared by this example")
        path = safe_member(Path(record["application_root"]), selected_file)
    content = path.read_text(encoding="utf-8")
    end = offset + max_chars
    return {**public_record(record), "path": str(path), "content": content[offset:end],
            "offset": offset, "total_chars": len(content), "next_offset": end if end < len(content) else None}


def validate_examples(root: Path, catalog_path: Path, apex_version: str, binary: str) -> dict:
    release = require_release(apex_version)["feature_release"]
    verify_vendor(root)
    catalog = catalog_data(root, catalog_path, release)
    evidence = {"schema_version": 1, "apex_release": release, "oracle_commit": catalog["oracle_commit"],
                "checked_at": utc_now().isoformat(), "applications": {}}
    for name, application in catalog["applications"].items():
        source = safe_member(root, application["path"])
        with tempfile.TemporaryDirectory(prefix="apexlang-example-") as directory:
            candidate = Path(directory) / name
            shutil.copytree(source, candidate)
            result = validate(candidate, release, binary)
        if not result["compiler_validated"]:
            raise ValueError("Example compiler validation failed; private log: " + result["diagnostic_log"])
        if result["tree_sha256"] != application["tree_sha256"]:
            raise ValueError("Example staging source differs from the catalog")
        evidence["applications"][name] = {"compiler_validated": True, "runtime_verified": False,
                                         "scope": "complete-example-application",
                                         "source_tree_sha256": result["tree_sha256"],
                                         "source_mmd_version": result["source_mmd_version"],
                                         "sqlcl_version": result["sqlcl_version"]}
    evidence["evidence_sha256"] = digest_record(evidence, "evidence_sha256")
    return evidence


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("verify", "search", "read", "validate-examples"))
    parser.add_argument("--root", type=Path)
    parser.add_argument("--catalog", type=Path)
    parser.add_argument("--apex-version", default="26.2")
    parser.add_argument("--query", default="")
    parser.add_argument("--kind", choices=("all", "definition", "example"), default="all")
    parser.add_argument("--limit", type=int, default=5)
    parser.add_argument("--offset", type=int, default=0)
    parser.add_argument("--max-chars", type=int, default=4000)
    parser.add_argument("--id")
    parser.add_argument("--file")
    parser.add_argument("--sqlcl")
    parser.add_argument("--output", type=Path, help="New compiler-evidence JSON file; never overwrites a report")
    args = parser.parse_args()
    default_root, default_catalog = reference_paths()
    root, catalog = args.root or default_root, args.catalog or default_catalog
    try:
        require_release(args.apex_version)
        if args.action == "search":
            report = search_references(root, catalog, args.query, args.apex_version, args.kind, args.limit, args.offset)
        elif args.action == "read":
            report = read_reference(root, catalog, args.id, args.apex_version, args.offset, args.max_chars, args.file)
        elif args.action == "validate-examples":
            if args.output and (args.output.exists() or args.output.is_symlink() or args.output.resolve().is_relative_to(root.resolve())):
                raise ValueError("Evidence output must be a new file outside the Oracle vendor tree")
            report = validate_examples(root, catalog, args.apex_version, sqlcl_binary(args.sqlcl))
            if args.output:
                write_report(args.output, report)
        else:
            report = verify_vendor(root)
            if report["apex_release"] != require_release(args.apex_version)["feature_release"]:
                raise ValueError("Pinned and requested Oracle releases differ")
            report["catalog"] = verify_catalog(root, catalog)
        print(json.dumps(report, indent=2, ensure_ascii=False))
        return 0
    except (ValueError, OSError, KeyError, TypeError, AttributeError) as exc:
        print(f"ERROR {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
