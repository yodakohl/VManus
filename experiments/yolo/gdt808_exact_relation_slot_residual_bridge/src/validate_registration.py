#!/usr/bin/env python3
"""Validate the outcome-aware GDT808 design registration."""

from __future__ import annotations

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
