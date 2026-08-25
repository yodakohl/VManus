#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
import subprocess
from collections import Counter
from pathlib import Path


HERE = Path(__file__).resolve().parent
PREFIX = "EIGHT_HUNDRED_SEVENTY_SECOND"


def read(name: str) -> list[dict[str, str]]:
    with (HERE / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    subprocess.run(["python", str(HERE / "build_eight_hundred_seventy_second.py")], check=True)
    owners = read(f"{PREFIX}_4_PICTURE_OWNER_SIGILS.tsv")
    grammar = read(f"{PREFIX}_3_PART_PRODUCT_NAME_GRAMMAR.tsv")
    products = read(f"{PREFIX}_19_INTERNAL_PRODUCTS.tsv")
    events = read(f"{PREFIX}_100_EVENT_PRODUCT_BINDING.tsv")
    links = read(f"{PREFIX}_6_EXACT_INTERNAL_SUPPLY_LINKS.tsv")
    summary = json.loads((HERE / f"{PREFIX}_BUILD_SUMMARY.json").read_text(encoding="utf-8"))
    checks = {
        "four_owners": len(owners) == 4 and {row["owner_sigil"] for row in owners} == {"A", "B", "C", "D"},
        "three_part_grammar": len(grammar) == 3 and {row["element"] for row in grammar} == {"OWNER_SIGIL", "PRODUCT_FAMILY", "LOCAL_ORDINAL"},
        "nineteen_products": len(products) == 19 and len({row["product_handle"] for row in products}) == 19 and len({row["statement_id"] for row in products}) == 19,
        "all_events": len(events) == 100 and len({row["event_id"] for row in events}) == 100 and all(row["product_handle"] for row in events),
        "event_products_exist": {row["product_handle"] for row in events} == {row["product_handle"] for row in products},
        "six_links": len(links) == 6 and {row["how_record"] for row in links} == {"B1", "B2", "B3", "B4", "B5", "B6"},
        "four_slots": {row["what_slot"]: row["internal_product_handle"] for row in links} == {"P1": "A.G2", "P2": "B.X2", "P3": "C.W2", "P4": "D.P1"},
        "no_species_needed": all(row["external_species_name"] == "UNNAMED" for row in owners) and all(row["external_plant_or_product_name"] == "UNNAMED" for row in products) and all(row["external_species_required_for_workshop_use"] == "NO" for row in links),
        "one_full_master_left": summary["master_values_fully_missing_after"] == 1 and summary["book_internal_product_identity_recovered"] is True,
        "no_new_words": summary["new_voynich_word_meanings"] == 0,
        "sealed_pages": summary["sealed_pages"] == ["f84", "f84r"] and not any("f84" in " ".join(row.values()).lower() for row in owners + grammar + products + events + links),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / f"{PREFIX}_VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if result["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
