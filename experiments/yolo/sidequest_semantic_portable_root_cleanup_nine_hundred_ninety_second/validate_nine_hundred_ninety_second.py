#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent


def read(name: str) -> list[dict[str, str]]:
    with (HERE / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    roots = read("PASS992_53_CLEAN_PORTABLE_ROOTS.tsv")
    codebook = read("PASS992_159_CODEBOOK.tsv")
    events = read("PASS992_2511_EVENT_INTERLINEAR.tsv")
    audit = read("PASS992_ROOT_PORTABILITY_AUDIT.tsv")
    codebook_by_id = {row["teaching_unit_id"]: row for row in codebook}
    root_by_id = {row["root_id"]: row for row in roots}
    s_events = [row for row in events if "R-S_ADDR" in row["primary_teaching_unit_ids"].split("|")]
    checks = {
        "roots_53": len(roots) == 53 and len(root_by_id) == 53,
        "codebook_159": len(codebook) == 159,
        "events_2511": len(events) == 2511 and len({row["event_id"] for row in events}) == 2511,
        "audit_53": len(audit) == 53,
        "all_roots_one_token": all(" " not in row["atomic_meaning_de"] for row in roots),
        "all_roots_have_content_occurrence": all(int(row["content_occurrences"]) > 0 for row in audit),
        "one_revision": sum(row["revision_status"] != "KEEP" for row in audit) == 1,
        "s_addr_sonderort": root_by_id["R-S_ADDR"]["atomic_meaning_de"] == "SONDERORT"
        and codebook_by_id["R-S_ADDR"]["spoken_value_de"] == "SONDERORT",
        "s_addr_two_events": len(s_events) == 2,
        "f83_not_sternort": all("STERNORT" not in row["complete_working_reading_de"] for row in s_events if row["physical_page"] == "f83r"),
        "f67_sternstelle_allowed": all("STERNSTELLE" in row["complete_working_reading_de"] for row in s_events if row["physical_page"] == "f67r2"),
        "sealed_absent": all("f84" not in row["physical_page"].lower() for row in events),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / "PASS992_VALIDATION.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    if result["status"] != "PASS":
        raise SystemExit(json.dumps(result, indent=2))
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
