#!/usr/bin/env python3
"""Independent integrity/capacity validation of the GDT158 source freeze."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def sha(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def csha(value: object) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=True, separators=(",", ":")).encode()).hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--freeze", type=Path, default=ROOT / "gdt158_source_freeze.json")
    parser.add_argument("--output", type=Path, default=ROOT / "gdt158_source_freeze_validation.json")
    args = parser.parse_args()
    result = json.loads(args.freeze.read_text(encoding="utf-8"))
    checks: list[dict[str, object]] = []

    def check(name: str, state: bool) -> None:
        checks.append({"check": name, "pass": bool(state)})

    check("schema", result["schema"] == "GDT158_STRUCTURED_MEDIEVAL_SOURCE_FREEZE_V1")
    check("status", result["status"] == "SOURCE_PANEL_FROZEN_BEFORE_RESIDUAL_SCORING")
    aug = result["sources"]["AUGSBURG_ACCOUNTS_1402_1424"]
    check("augsburg_entries", aug["entries"] == 22071)
    check("augsburg_groups", aug["groups"] == 281557)
    check("augsburg_years", aug["represented_years"] == 18 and sum(aug["year_counts"].values()) == 22071)
    check("augsburg_parents", aug["year_plus_folio_parents"] == 1817)
    nb = result["sources"]["NUREMBERG_LETTERBOOKS_1408_1423"]
    st = result["sources"]["STE1_TECHNICAL_RECIPES_1400_1425"]
    check("nuremberg_capacity", nb == {"groups": 479879, "lines": 48337, "records": 3176})
    check("ste1_capacity", st == {"groups": 111, "lines": 10, "records": 2})
    blind = read(ROOT / "gdt155_blinded_diplomatic.tsv")
    expanded = read(ROOT / "gdt155_unblinded_lines.tsv")
    check("external_line_join", len(blind) == len(expanded) == 48347 and [r["line_id"] for r in blind] == [r["line_id"] for r in expanded])
    check("no_voynich_columns", all(not any("folio" in key.lower() or "locus" in key.lower() for key in row) for row in blind[:1] + expanded[:1]))
    for name, digest in result["inputs"].items():
        if name == "augsburg_workbook":
            check("augsburg_hash_frozen", digest == "bed2ff0e4e427cc8c602893b852a759c26fe91d18e9891a26ba80829360160a1")
        else:
            check("hash_" + name, sha(ROOT / name) == digest)
    for name, digest in result["documents"].items():
        check("hash_" + name, sha(ROOT / name) == digest)
    for name, digest in result["implementation"].items():
        check("hash_" + name, sha(ROOT / name) == digest)
    body = dict(result)
    stored = body.pop("result_content_sha256")
    check("content_hash", csha(body) == stored)
    check("no_retune", result["design"]["nuremberg_channel_retuned"] is False)
    check("f84r_sealed", not any(result["f84r"].values()))
    passed = sum(row["pass"] for row in checks)
    validation = {
        "schema": "GDT158_SOURCE_FREEZE_VALIDATION_V1",
        "status": "PASS" if passed == len(checks) else "FAIL",
        "checks_passed": passed,
        "checks_total": len(checks),
        "checks": checks,
        "freeze_sha256": sha(args.freeze),
        "validator_sha256": sha(Path(__file__)),
    }
    args.output.write_text(json.dumps(validation, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"{validation['status']} {passed}/{len(checks)}")
    if passed != len(checks):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
