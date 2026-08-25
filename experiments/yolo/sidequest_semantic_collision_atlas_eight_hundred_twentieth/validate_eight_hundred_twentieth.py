#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
import subprocess
from collections import Counter
from pathlib import Path


HERE = Path(__file__).resolve().parent


def read(name: str) -> list[dict[str, str]]:
    with (HERE / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    subprocess.run(["python", str(HERE / "build_eight_hundred_twentieth.py")], check=True)
    groups = read("EIGHT_HUNDRED_TWENTIETH_6_COLLISION_GROUPS.tsv")
    profiles = read("EIGHT_HUNDRED_TWENTIETH_19_COMPONENT_PROFILES.tsv")
    audit = read("EIGHT_HUNDRED_TWENTIETH_COMPONENT_EVENT_AUDIT.tsv")
    examples = read("EIGHT_HUNDRED_TWENTIETH_CONTEXT_EXAMPLES.tsv")
    summary = json.loads((HERE / "EIGHT_HUNDRED_TWENTIETH_BUILD_SUMMARY.json").read_text(encoding="utf-8"))
    expected = {"OK", "T", "CHD", "K", "P", "L", "SH", "SHED", "OL", "OT", "OS", "S", "AIN", "AIIN", "IIN", "AR", "CKH", "AL", "SOLK"}
    audit_counts = Counter(row["component"] for row in audit)
    checks = {
        "six_groups_nineteen_components": len(groups) == 6 and len(profiles) == 19 and {row["component"] for row in profiles} == expected,
        "all_kept_distinct": all(row["selected_resolution"] == "KEEP_ALL_MEMBERS_DISTINCT" for row in groups) and all(row["decision"] == "KEEP_DISTINCT" for row in profiles),
        "profile_audit_counts": all(audit_counts[row["component"]] == int(row["events"]) for row in profiles),
        "all_audit_rows_concordant": all(row["component"] in row["component_recipe"].split("+") for row in audit),
        "examples_every_component": {row["component"] for row in examples} == expected,
        "no_empty_values": all(row["short_value_de"] and row["role_boundary"] for row in profiles),
        "summary_matches": summary["groups"] == 6 and summary["components"] == 19 and summary["meaning_merges"] == 0 and summary["meaning_splits"] == 0,
        "sealed_pages": summary["sealed_pages"] == ["f84", "f84r"],
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / "EIGHT_HUNDRED_TWENTIETH_VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if result["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
