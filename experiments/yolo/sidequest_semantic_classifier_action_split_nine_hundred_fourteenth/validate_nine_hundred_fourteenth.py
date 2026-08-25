#!/usr/bin/env python3
"""Validate Pass 914."""

from __future__ import annotations

import csv
import hashlib
import json
import subprocess
from collections import Counter
from pathlib import Path


BASE = Path(__file__).resolve().parent
OUT = BASE / "PASS914_VALIDATION.json"


def rows(name: str) -> list[dict[str, str]]:
    with (BASE / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


checks = []


def check(name: str, condition: bool, detail: object) -> None:
    checks.append({"name": name, "pass": bool(condition), "detail": detail})


def main() -> None:
    events = rows("PASS914_2511_CONTEXTUAL_INTERLINEAR.tsv")
    audit = rows("PASS914_1286_DUAL_USE_EVENT_AUDIT.tsv")
    dual = rows("PASS914_DUAL_COMPONENT_LEXICON.tsv")
    lists = rows("PASS914_F70_F88_LIST_EDITION.tsv")

    check("events_2511", len(events) == 2511, len(events))
    check("event_ids_unique", len({row["event_id"] for row in events}) == 2511, "2511")
    check("audit_1286", len(audit) == 1286, len(audit))
    check("audit_ids_unique", len({row["event_id"] for row in audit}) == len(audit), len(audit))
    check("dual_7", len(dual) == 7, len(dual))
    check("dual_components", {row["component"] for row in dual} == {"O", "OK", "CH", "K", "T", "S", "OR"}, sorted(row["component"] for row in dual))
    check("label_198", sum(row["semantic_channel"] == "LABEL_CLASSIFIER" for row in events) == 198, Counter(row["semantic_channel"] for row in events))
    check("prose_2313", sum(row["semantic_channel"] == "PROSE_ACTION" for row in events) == 2313, Counter(row["semantic_channel"] for row in events))
    check("lists_60", len(lists) == 60, len(lists))
    check("f70_45", sum(row["physical_page"] == "f70v" for row in lists) == 45, Counter(row["physical_page"] for row in lists))
    check("f88_15", sum(row["physical_page"] == "f88r" for row in lists) == 15, Counter(row["physical_page"] for row in lists))
    check("all_contextual", all(row["contextual_reading_de"] for row in events), "2511/2511")
    check("label_owner_first", all(row["concrete_owner_or_name_de"] != "NOT_APPLICABLE" for row in events if row["semantic_channel"] == "LABEL_CLASSIFIER"), "198/198")
    check("prose_no_owner_name", all(row["concrete_owner_or_name_de"] == "NOT_APPLICABLE" for row in events if row["semantic_channel"] == "PROSE_ACTION"), "2313/2313")
    check("component_event_totals", all(int(row["prose_events"]) + int(row["label_events"]) == int(row["total_events"]) for row in dual), "7/7")
    check("sealed_absent", all("f84" not in "\t".join(row.values()).lower() for row in events + lists), "sealed")

    before = {path.name: hashlib.sha256(path.read_bytes()).hexdigest() for path in BASE.glob("PASS914_*") if path.name != OUT.name}
    subprocess.run(["python", str(BASE / "build_nine_hundred_fourteenth.py")], check=True, cwd=BASE.parents[2])
    after = {path.name: hashlib.sha256(path.read_bytes()).hexdigest() for path in BASE.glob("PASS914_*") if path.name != OUT.name}
    check("deterministic_rebuild", before == after, len(before))

    result = {"status": "PASS" if all(row["pass"] for row in checks) else "FAIL", "checks_passed": sum(bool(row["pass"]) for row in checks), "checks_total": len(checks), "checks": checks}
    OUT.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False))
    if result["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
