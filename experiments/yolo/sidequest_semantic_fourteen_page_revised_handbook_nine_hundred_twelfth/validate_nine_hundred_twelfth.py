#!/usr/bin/env python3
"""Validate the Pass-912 complete revised handbook."""

from __future__ import annotations

import csv
import hashlib
import json
import subprocess
import tempfile
from collections import Counter
from pathlib import Path


BASE = Path(__file__).resolve().parent
OUT = BASE / "PASS912_VALIDATION.json"


def rows(name: str) -> list[dict[str, str]]:
    with (BASE / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


checks: list[dict[str, object]] = []


def check(name: str, condition: bool, detail: object) -> None:
    checks.append({"name": name, "pass": bool(condition), "detail": detail})


def main() -> None:
    events = rows("PASS912_2511_EVENT_INTERLINEAR.tsv")
    dictionary = rows("PASS912_CARD_DICTIONARY.tsv")
    loci = rows("PASS912_464_LOCUS_EDITION.tsv")
    pages = rows("PASS912_FOURTEEN_PAGE_SUMMARY.tsv")
    owners = rows("PASS912_OWNER_BOUND_LABELS.tsv")
    components = rows("PASS912_COMPONENTS.tsv")
    rules = rows("PASS912_SCRIBAL_RULES.tsv")

    check("events_2511", len(events) == 2511, len(events))
    check("event_ids", [row["event_id"] for row in events] == [f"P912-E{i:04d}" for i in range(1, 2512)], "sequential")
    check("pass910_ids_unique", len({row["pass910_event_id"] for row in events}) == 2511, "2511")
    check("dictionary_ids_bound", {row["dictionary_entry_id"] for row in events} == {row["dictionary_entry_id"] for row in dictionary}, len(dictionary))
    check("dictionary_event_sum", sum(int(row["events"]) for row in dictionary) == 2511, sum(int(row["events"]) for row in dictionary))
    check("loci_464", len(loci) == 464, len(loci))
    check("locus_event_sum", sum(int(row["events"]) for row in loci) == 2511, sum(int(row["events"]) for row in loci))
    check("pages_14", len(pages) == 14, len(pages))
    check("page_event_sum", sum(int(row["events"]) for row in pages) == 2511, sum(int(row["events"]) for row in pages))
    check("source_pages_15", len({row["source_page"] for row in events}) == 15, sorted({row["source_page"] for row in events}))
    check("owner_events_198", len(owners) == 198, len(owners))
    check("owner_flags_198", sum(row["owner_binding_required"] == "YES" for row in events) == 198, Counter(row["owner_binding_required"] for row in events))
    check("workshop_repairs_63", sum(row["repair_origin"] == "PASS911_WORKSHOP_CARD" for row in events) == 63, Counter(row["repair_origin"] for row in events))
    check("external_cphy_1", sum(row["repair_origin"] == "PASS911_CPH_EXTERNAL" for row in events) == 1, Counter(row["repair_origin"] for row in events))
    check("cph_12", sum("CPH" in row["component_recipe"].split("+") for row in events) == 12, "12")
    check("components_50", len(components) == 50, len(components))
    check("cph_component", sum(row["component"] == "CPH" for row in components) == 1, "one")
    check("rules_6", len(rules) == 6, len(rules))
    check("no_old_modes", all(row["meaning_mode"] not in {"LOCAL_WORKSHOP_CARD", "LOCAL_NOMENCLATOR"} for row in events), Counter(row["meaning_mode"] for row in events))
    check("no_whole_recipe", all("WHOLE[" not in row["component_recipe"] for row in events), "2511/2511")
    check("all_atomic", all(row["atomic_reading_de"] for row in events), "2511/2511")
    check("all_fluent", all(row["fluent_token_de"] for row in events), "2511/2511")
    check("no_line_sentence_rule", all(row["physical_line_is_sentence_end"] == "NO" for row in loci), "464/464")
    check("sealed_absent_events", all("f84" not in "\t".join(row.values()).lower() for row in events), "sealed")
    check("sealed_absent_outputs", all(
        "f84" not in path.read_text(encoding="utf-8").lower()
        for path in BASE.iterdir()
        if path.is_file() and path.name.startswith("PASS912_") and path.name != OUT.name
    ), "sealed")

    before = {path.name: hashlib.sha256(path.read_bytes()).hexdigest() for path in BASE.iterdir() if path.is_file() and path.name.startswith("PASS912_") and path.name != OUT.name}
    subprocess.run(["python", str(BASE / "build_nine_hundred_twelfth.py")], check=True, cwd=BASE.parents[2])
    after = {path.name: hashlib.sha256(path.read_bytes()).hexdigest() for path in BASE.iterdir() if path.is_file() and path.name.startswith("PASS912_") and path.name != OUT.name}
    check("deterministic_rebuild", before == after, len(before))

    result = {"status": "PASS" if all(row["pass"] for row in checks) else "FAIL", "checks_passed": sum(bool(row["pass"]) for row in checks), "checks_total": len(checks), "checks": checks}
    OUT.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False))
    if result["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
