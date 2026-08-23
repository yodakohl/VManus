#!/usr/bin/env python3
"""Validate coverage and attachment coherence of the workshop clause pass."""

from __future__ import annotations

import csv
import json
import subprocess
import sys
from collections import Counter
from pathlib import Path


HERE = Path(__file__).resolve().parent


def read(name: str) -> list[dict[str, str]]:
    with (HERE / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> int:
    events = read("COMPLETE_381_ATTACHED_EVENTS.tsv")
    units = read("FUSION_UNITS.tsv")
    statements = read("COMPLETE_116_ATTACHED_STATEMENTS.tsv")
    profiles = read("CARD_CONTEXT_PROFILES.tsv")
    summary = json.loads((HERE / "BUILD_SUMMARY.json").read_text(encoding="utf-8"))
    checks: list[dict[str, object]] = []

    def add(name: str, passed: bool, detail: object) -> None:
        checks.append({"check": name, "pass": bool(passed), "detail": detail})

    add("event_count", len(events) == 381, len(events))
    add("event_ids_unique", len({row["event_id"] for row in events}) == 381, "381 expected")
    add("event_serial_complete", [int(row["event_serial"]) for row in events] == list(range(1, 382)), "1..381")
    add("statement_count", len(statements) == 116, len(statements))
    add("statement_ids_unique", len({row["statement_id"] for row in statements}) == 116, "116 expected")
    add("card_profiles", len(profiles) == 173, len(profiles))
    add("record_count", len({row["record_unit_id"] for row in statements}) == 11, "11 expected")
    add("fusion_unit_count", len(units) == summary["fusion_units"], len(units))
    add("each_event_has_host", all(row["attachment_host_event_id"] for row in events), "nonempty")
    event_ids = {row["event_id"] for row in events}
    add("all_hosts_exist", all(row["attachment_host_event_id"] in event_ids for row in events), "all host IDs present")
    self_hosts = {row["event_id"] for row in events if row["attachment_direction"] == "SELF"}
    add("unit_hosts_match", {row["host_event_id"] for row in units} == self_hosts, f"{len(self_hosts)} hosts")
    add("unit_members_sum", sum(int(row["member_event_count"]) for row in units) == 381, sum(int(row["member_event_count"]) for row in units))
    add("statement_event_sum", sum(int(row["event_count"]) for row in statements) == 381, sum(int(row["event_count"]) for row in statements))
    add("statement_units_sum", sum(int(row["fusion_unit_count"]) for row in statements) == len(units), len(units))
    add("all_readings_nonempty", all(row["continuous_workshop_reading_de"].strip() for row in statements), "nonempty")
    add("all_skeletons_nonempty", all(row["attachment_skeleton_de"].strip() for row in statements), "nonempty")
    dchol = [row for row in events if row["master_card_id"] == "MC142"]
    add("dchol_count", len(dchol) == 2, len(dchol))
    add("dchol_corrected", all(row["corrected_semantic_atoms"] == "DCHOL" for row in dchol), [row["corrected_semantic_atoms"] for row in dchol])
    add("no_free_dch", all("DCH" not in row["corrected_semantic_atoms"].split("+") for row in events), "DCH absent")
    add("role_total", sum(summary["role_counts"].values()) == 381, summary["role_counts"])
    add("direction_total", sum(summary["direction_counts"].values()) == 381, summary["direction_counts"])
    add("sealed_absent", all("f84" not in "\t".join(row.values()).lower() for table in (events, units, statements, profiles) for row in table), "sealed tokens absent")

    products = [
        "COMPLETE_381_ATTACHED_EVENTS.tsv", "FUSION_UNITS.tsv",
        "COMPLETE_116_ATTACHED_STATEMENTS.tsv", "CARD_CONTEXT_PROFILES.tsv",
        "ELEVEN_RECORD_ATTACHMENT_EDITION.md", "CLAUSE_ATTACHMENT_REPORT.md", "BUILD_SUMMARY.json",
    ]
    before = {name: (HERE / name).read_bytes() for name in products}
    subprocess.run([sys.executable, str(HERE / "build_clause_attachment.py")], check=True, cwd=HERE.parents[3])
    after = {name: (HERE / name).read_bytes() for name in products}
    add("deterministic_rebuild", before == after, "all bytes identical")

    failures = [item for item in checks if not item["pass"]]
    result = {
        "status": "PASS" if not failures else "FAIL", "pass_count": len(checks) - len(failures),
        "fail_count": len(failures), "checks": checks,
    }
    (HERE / "VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"{result['status']}: {result['pass_count']}/{len(checks)} checks")
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
