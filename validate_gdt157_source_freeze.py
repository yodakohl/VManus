#!/usr/bin/env python3
"""Integrity validator for the pre-score GDT157 causal-channel freeze."""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
FREEZE = ROOT / "gdt157_source_freeze.json"
OUT = ROOT / "gdt157_source_freeze_validation.json"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rows(path: Path):
    with path.open(encoding="utf-8", newline="") as handle:
        yield from csv.DictReader(handle, delimiter="\t")


def main() -> None:
    value = json.loads(FREEZE.read_text(encoding="utf-8"))
    checks: list[dict[str, object]] = []

    def check(name: str, state: bool) -> None:
        checks.append({"check": name, "pass": bool(state)})

    check("schema", value["schema"] == "GDT157_LEARNED_ABBREVIATION_CAUSAL_SOURCE_FREEZE_V1")
    check("status", value["status"] == "FROZEN_BEFORE_GENERATED_DIPLOMATIC_SCORING")
    check("four_outer_books", value["channel"]["outer_folds"] == ["Band2", "Band3", "Band4", "Band5"])
    check("no_voynich_rules", value["channel"]["voynich_specific_rules"] == 0)
    for name, digest in value["inputs"].items():
        check(f"input_hash:{name}", sha(ROOT / name) == digest)
    for name in value["contracts"].values():
        check(f"contract_exists:{name}", (ROOT / name).is_file())

    blind = list(rows(ROOT / "gdt155_blinded_diplomatic.tsv"))
    expanded = list(rows(ROOT / "gdt155_unblinded_lines.tsv"))
    truth = list(rows(ROOT / "gdt155_unblinded_record_truth.tsv"))
    check("line_count_48347", len(blind) == len(expanded) == 48347)
    check("record_truth_3178", len(truth) == 3178)
    check("line_ids_equal", {r["line_id"] for r in blind} == {r["line_id"] for r in expanded})
    check("nuremberg_books_exact", {r["book_or_ms"] for r in blind if r["corpus"] == "NUREMBERG"} == {"Band2", "Band3", "Band4", "Band5"})
    check("no_f84_external_inputs", not any("f84" in str(v).lower() for table in (blind, expanded, truth) for row in table for v in row.values()))
    check("f84_flags_false", all(value["f84r"][key] is False for key in ("opened", "queried", "retained", "joined", "scored")))
    check("zero_voynich_inputs", value["f84r"]["voynich_source_inputs"] == 0)

    result = {
        "schema": "GDT157_LEARNED_ABBREVIATION_CAUSAL_SOURCE_FREEZE_VALIDATION_V1",
        "status": "PASS" if all(item["pass"] for item in checks) else "FAIL",
        "checks": checks,
        "checks_passed": sum(bool(item["pass"]) for item in checks),
        "checks_total": len(checks),
        "freeze_sha256": sha(FREEZE),
        "validator_sha256": sha(Path(__file__)),
    }
    OUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if result["status"] != "PASS":
        raise SystemExit(json.dumps([item for item in checks if not item["pass"]], indent=2))
    print(f"PASS {result['checks_passed']}/{result['checks_total']}")


if __name__ == "__main__":
    main()
