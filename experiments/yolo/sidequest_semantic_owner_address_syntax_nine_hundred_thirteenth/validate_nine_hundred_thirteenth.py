#!/usr/bin/env python3
"""Validate Pass 913."""

from __future__ import annotations

import csv
import hashlib
import json
import subprocess
from collections import Counter
from pathlib import Path


BASE = Path(__file__).resolve().parent
OUT = BASE / "PASS913_VALIDATION.json"


def rows(name: str) -> list[dict[str, str]]:
    with (BASE / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


checks = []


def check(name: str, condition: bool, detail: object) -> None:
    checks.append({"name": name, "pass": bool(condition), "detail": detail})


def main() -> None:
    events = rows("PASS913_198_OWNER_LABEL_EVENTS.tsv")
    loci = rows("PASS913_153_OWNER_LABEL_LOCI.tsv")
    census = rows("PASS913_COMPONENT_ROLE_CENSUS.tsv")
    grammar = rows("PASS913_ADDRESS_GRAMMAR.tsv")
    bridges = rows("PASS913_CROSS_REGISTER_BRIDGES.tsv")

    check("events_198", len(events) == 198, len(events))
    check("event_ids_unique", len({row["event_id"] for row in events}) == 198, len({row["event_id"] for row in events}))
    check("loci_153", len(loci) == 153, len(loci))
    check("locus_groups_198", sum(int(row["groups"]) for row in loci) == 198, sum(int(row["groups"]) for row in loci))
    check("all_owner", all(row["concrete_owner_or_name_de"] for row in events), "198/198")
    check("all_role", all(row["role_family"] for row in events), "198/198")
    check("all_namespace", all(row["namespace"] for row in events), "198/198")
    check("all_recipe", all(row["component_recipe"] for row in events), "198/198")
    check("all_combined", all(row["combined_creative_reading_de"] for row in events), "198/198")
    check("join_total", sum(Counter(row["owner_source"] for row in events).values()) == 198, Counter(row["owner_source"] for row in events))
    check("astro_93", sum(row["owner_source"] == "V75_SELECTED_CELESTIAL_OWNER" for row in events) == 93, Counter(row["owner_source"] for row in events))
    check("f70_60", sum(row["owner_source"] == "PASS909_F70_VISIBLE_OWNER" for row in events) == 60, Counter(row["owner_source"] for row in events))
    check("f75_10", sum(row["owner_source"] == "PASS909_F75_VISIBLE_STATION" for row in events) == 10, Counter(row["owner_source"] for row in events))
    check("f88_16", sum(row["owner_source"] == "PASS909_F88_VISIBLE_INGREDIENT" for row in events) == 16, Counter(row["owner_source"] for row in events))
    check("bio_manual_19", sum(row["owner_source"] == "PASS910_IMAGE_OWNER" for row in events) == 19, Counter(row["owner_source"] for row in events))
    check("grammar_8", len(grammar) == 8, len(grammar))
    check("bridges_8", len(bridges) == 8, len(bridges))
    check("component_census_nonempty", len(census) >= 30, len(census))
    check("ot_al_bridge", next(row for row in bridges if row["bridge"] == "OT_AL")["events"] != "0", next(row for row in bridges if row["bridge"] == "OT_AL")["events"])
    check("sealed_absent", all("f84" not in "\t".join(row.values()).lower() for row in events + loci), "sealed")

    before = {path.name: hashlib.sha256(path.read_bytes()).hexdigest() for path in BASE.glob("PASS913_*") if path.name != OUT.name}
    subprocess.run(["python", str(BASE / "build_nine_hundred_thirteenth.py")], check=True, cwd=BASE.parents[2])
    after = {path.name: hashlib.sha256(path.read_bytes()).hexdigest() for path in BASE.glob("PASS913_*") if path.name != OUT.name}
    check("deterministic_rebuild", before == after, len(before))

    result = {"status": "PASS" if all(row["pass"] for row in checks) else "FAIL", "checks_passed": sum(bool(row["pass"]) for row in checks), "checks_total": len(checks), "checks": checks}
    OUT.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False))
    if result["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
