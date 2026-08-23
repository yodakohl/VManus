#!/usr/bin/env python3
"""Validate complete coverage of the speakable eleven-record edition."""

from __future__ import annotations

import csv
import json
import subprocess
import sys
from pathlib import Path


HERE = Path(__file__).resolve().parent


def read(name: str) -> list[dict[str, str]]:
    with (HERE / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> int:
    statements = read("COMPLETE_116_SPEAKABLE_STATEMENTS.tsv")
    records = read("RECORD_SUMMARY.tsv")
    checks: list[dict[str, object]] = []

    def add(name: str, passed: bool, detail: object) -> None:
        checks.append({"check": name, "pass": bool(passed), "detail": detail})

    add("statement_count", len(statements) == 116, len(statements))
    add("statement_unique", len({row["statement_id"] for row in statements}) == 116, "116 expected")
    add("record_count", len(records) == 11, len(records))
    add("event_count", sum(len(row["surface_sequence"].split()) for row in statements) == 381, sum(len(row["surface_sequence"].split()) for row in statements))
    add("record_event_count", sum(int(row["event_count"]) for row in records) == 381, sum(int(row["event_count"]) for row in records))
    add("all_translated", all(row["speakable_reading_de"].strip() for row in statements), "nonempty")
    add("all_bound_to_surface", all(row["surface_sequence"].strip() for row in statements), "nonempty")
    add("all_bound_to_atoms", all(row["corrected_atom_chain"].strip() for row in statements), "nonempty")
    add("herbal_hand_edits", sum(row["editorial_mode"] == "HAND_EDITED_HERBAL" for row in statements) == 19, sum(row["editorial_mode"] == "HAND_EDITED_HERBAL" for row in statements))
    add("pages_fixed", {row["page"] for row in statements} == {"f10r", "f11r", "f55v", "f56r", "f81v", "f82r", "f83r"}, sorted({row["page"] for row in statements}))
    add("sealed_absent", all("f84" not in "\t".join(row.values()).lower() for row in statements + records), "sealed tokens absent")

    products = ["COMPLETE_116_SPEAKABLE_STATEMENTS.tsv", "RECORD_SUMMARY.tsv", "SPEAKABLE_ELEVEN_RECORD_EDITION.md", "SPEAKABLE_EDITION_REPORT.md", "BUILD_SUMMARY.json"]
    before = {name: (HERE / name).read_bytes() for name in products}
    subprocess.run([sys.executable, str(HERE / "build_speakable_edition.py")], check=True, cwd=HERE.parents[3])
    after = {name: (HERE / name).read_bytes() for name in products}
    add("deterministic_rebuild", before == after, "all bytes identical")

    failures = [row for row in checks if not row["pass"]]
    result = {"status": "PASS" if not failures else "FAIL", "pass_count": len(checks) - len(failures), "fail_count": len(failures), "checks": checks}
    (HERE / "VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"{result['status']}: {result['pass_count']}/{len(checks)} checks")
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
