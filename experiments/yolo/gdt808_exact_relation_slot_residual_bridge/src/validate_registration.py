#!/usr/bin/env python3
"""Validate the outcome-aware GDT808 design registration."""

from __future__ import annotations

import ast
import csv
import hashlib
import json
from pathlib import Path


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
BASE = ROOT / "experiments/yolo/gdt808_exact_relation_slot_residual_bridge"
MANIFEST = BASE / "experiment.json"
OUT = BASE / "artifacts/REGISTERED_VALIDATION.json"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def rows(name: str) -> list[dict[str, str]]:
    with (BASE / "src" / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def literal_assignment(path: Path, name: str) -> object:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    for node in tree.body:
        if isinstance(node, (ast.Assign, ast.AnnAssign)):
            targets = node.targets if isinstance(node, ast.Assign) else [node.target]
            if any(isinstance(target, ast.Name) and target.id == name for target in targets):
                return ast.literal_eval(node.value)
    raise RuntimeError(f"literal assignment absent: {path}:{name}")


def main() -> int:
    checks: list[dict[str, object]] = []

    def check(name: str, condition: bool, detail: object) -> None:
        checks.append({"check": name, "pass": bool(condition), "detail": detail})
        if not condition:
            raise RuntimeError(f"registration check failed: {name}: {detail}")

    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    check("experiment_id", manifest.get("experiment_id") == "GDT808", manifest.get("experiment_id"))
    check(
        "sealed_data",
        manifest.get("sealed_data") == {"f84": "FORBIDDEN", "f84r": "FORBIDDEN"},
        manifest.get("sealed_data"),
    )
    check("status_unscored", "UNSCORED" in manifest.get("status", ""), manifest.get("status"))

    for item in manifest.get("inputs", []):
        path = ROOT / item["path"]
        check(f"input_exists:{item['path']}", path.is_file(), item["path"])
        check(f"input_hash:{item['path']}", sha256(path) == item["sha256"], item["sha256"])

    carrier_rows = rows("CORE_CARRIER_SPECS.tsv")
    core = [row["carrier"] for row in carrier_rows]
    check(
        "core13",
        core == ["ch", "cth", "k", "kch", "ok", "ot", "pch", "qok", "qot", "sh", "t", "tch", "yt"],
        core,
    )
    model_rows = rows("RELATION_MODEL_SPECS.tsv")
    check("eight_relation_models", len(model_rows) == 8, len(model_rows))
    check(
        "within_axis_primary",
        [row["model_id"] for row in model_rows if row["selection_credit"] == "PRIMARY"]
        == ["M01_L_TO_L", "M02_DY_TO_DY"],
        [row["model_id"] for row in model_rows],
    )
    check("four_feature_decks", len(rows("FEATURE_DECK_SPECS.tsv")) == 4, 4)
    control_rows = rows("CONTROL_SPECS.tsv")
    check("label_null_24", control_rows[0]["repetitions"] == "24", control_rows[0])
    check("carrier_null_12", control_rows[1]["repetitions"] == "12", control_rows[1])
    quarantine = {row["identifier"]: row for row in rows("QUARANTINE_SPECS.tsv")}
    raw35 = quarantine["RAW35"]["surfaces_or_rule"].split("|")
    all28 = quarantine["ALL28"]["surfaces_or_rule"].split("|")
    thin9 = quarantine["THIN9"]["surfaces_or_rule"].split("|")
    overlap6 = quarantine["OVERLAP6"]["surfaces_or_rule"].split("|")
    check("raw35", len(raw35) == len(set(raw35)) == 35, len(raw35))
    check("all28", len(all28) == len(set(all28)) == 28, len(all28))
    check("thin9", len(thin9) == len(set(thin9)) == 9, len(thin9))
    check("overlap6", len(overlap6) == len(set(overlap6)) == 6, len(overlap6))
    main_surfaces = {carrier + tail for carrier in raw35 for tail in ("eody", "eol", "edy", "ol")}
    thin_surfaces = {carrier + tail for carrier in thin9 for tail in ("kol", "tal")}
    check("q152", len(main_surfaces | thin_surfaces) == 152, len(main_surfaces | thin_surfaces))
    check("q152_overlap", sorted(main_surfaces & thin_surfaces) == sorted(overlap6), sorted(main_surfaces & thin_surfaces))
    check("rival_rules", len(rows("RIVAL_DECISION_SPECS.tsv")) == 20, 20)
    check("historical_rows", len(rows("HISTORICAL_TOPOLOGY_SPECS.tsv")) == 10, 10)

    run_names = tuple(literal_assignment(BASE / "src/run.py", "OUTPUT_NAMES"))
    validator_names = tuple(literal_assignment(BASE / "src/validate.py", "OUTPUT_NAMES"))
    check("builder_output_inventory_25", len(run_names) == len(set(run_names)) == 25, len(run_names))
    check("builder_validator_output_contract", validator_names == run_names, validator_names)
    implementation = {row["key"]: row["value"] for row in rows("IMPLEMENTATION_SPECS.tsv")}
    required_implementation = {
        "FORM_PARAGRAPH_LOCATION": "paragraph-line FIRST|MIDDLE|LAST|SINGLE plus paragraph-line quartile only; no paragraph line-count or paragraph-line forward/reverse feature",
        "END_CLASS_UNIVERSE": "endings observed outside exact Q152; fixed unchanged for the ED1 rebuild",
        "ED1_REBUILD_SCOPE": "rebuild all four feature decks with Q152 plus ED1 deletion while retaining the primary end-class universe",
        "RECORD_NO_LOCAL_INCREMENT": "PORTABLE_RECORD_OR_FORM_RELATION requires local gain strictly below 0.02",
        "EDGE_PACKET_SCOPE": "emit only same-page distinct-locus base/expanded carrier-axis pairs; expected fixed capacity 19",
        "SCORE_QUANTIZATION": "serialize every held event-score channel to 12 significant decimal digits before metrics and null AUCs",
        "TSV_SCHEMA_GATE": "all row keys must be contained in the declared or first-row schema before projection; later-only fields abort instead of truncating",
    }
    check("implementation_contract_amendments", all(implementation.get(key) == value for key, value in required_implementation.items()), required_implementation)
    manifest_outputs = {item["path"]: item for item in manifest.get("outputs", [])}
    for path in (BASE / "src/run.py", BASE / "src/validate.py"):
        relative = path.relative_to(ROOT).as_posix()
        check(f"runtime_hash_registered:{relative}",
              relative in manifest_outputs and manifest_outputs[relative]["sha256"] == sha256(path),
              manifest_outputs.get(relative))

    payload = {
        "experiment_id": "GDT808",
        "validation_scope": "OUTCOME_AWARE_DESIGN_REGISTRATION_ONLY",
        "status": "PASS",
        "check_count": len(checks),
        "checks": checks,
        "official_scores_built": False,
        "sealed_f84_accessed": False,
        "sealed_f84r_accessed": False,
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"PASS: {len(checks)} GDT808 registration checks")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
