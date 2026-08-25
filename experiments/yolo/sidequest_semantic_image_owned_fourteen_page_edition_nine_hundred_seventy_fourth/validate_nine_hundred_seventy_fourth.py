#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
P971 = ROOT / "experiments/yolo/sidequest_semantic_canonical_compact_workshop_edition_nine_hundred_seventy_first"


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    old_dict = read(P971 / "PASS971_86_ENTRY_DICTIONARY.tsv")
    new_dict = read(HERE / "PASS974_86_ENTRY_REGISTER_EXPANSIONS.tsv")
    pages = read(HERE / "PASS974_14_PAGE_IMAGE_OWNED_EDITION.tsv")
    flow = read(HERE / "PASS974_FOUR_STAGE_BOOK_FLOW.tsv")
    old_values = {r["entry_id"]: r["portable_value_de"] for r in old_dict}
    checks = {
        "dictionary_86": len(new_dict) == 86,
        "dictionary_ids_unchanged": {r["entry_id"] for r in new_dict} == set(old_values),
        "dictionary_values_unchanged": all(old_values[r["entry_id"]] == r["portable_value_de"] for r in new_dict),
        "three_expansions_each": all(r["material_workshop_expansion_de"] and r["station_workshop_expansion_de"] and r["celestial_lookup_expansion_de"] for r in new_dict),
        "pages_14": len(pages) == 14,
        "events_2511": sum(int(r["events"]) for r in pages) == 2511,
        "clauses_354": sum(int(r["prose_clauses"]) for r in pages) == 354,
        "local_501": sum(int(r["local_address_events"]) for r in pages) == 501,
        "page_readings_complete": all(r["complete_working_reading_de"] for r in pages),
        "four_book_stages": len(flow) == 4,
        "all_pages_in_flow": set("|".join(r["pages"] for r in flow).split("|")) == ({r["physical_page"] for r in pages} - {"f70v"}) | {"f70v1", "f70v2"},
        "sealed_absent": all("f84" not in "\t".join(r.values()).lower() for r in new_dict + pages + flow),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / "PASS974_VALIDATION.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    if result["status"] != "PASS":
        raise SystemExit(json.dumps(result, indent=2))
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
