#!/usr/bin/env python3
import csv
import json
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent


def read(name):
    with (HERE / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main():
    unified = read("FIVE_HUNDRED_NINETY_SECOND_776_UNIFIED_WORKSHOP_LEDGER.tsv")
    units = read("FIVE_HUNDRED_NINETY_SECOND_FOURTEEN_UNIT_ARCHITECTURE.tsv")
    pages = read("FIVE_HUNDRED_NINETY_SECOND_TEN_PAGE_ROLES.tsv")
    manual = read("FIVE_HUNDRED_NINETY_SECOND_FIFTEEN_STEP_MANUAL.tsv")
    models = read("FIVE_HUNDRED_NINETY_SECOND_ARCHITECTURE_COMPARISON.tsv")
    checks = {
        "unified776": len(unified) == 776 and [int(row["unified_serial"]) for row in unified] == list(range(1, 777)),
        "section_counts": Counter(row["section"] for row in unified) == Counter({"HERBAL": 100, "BIOLOGICAL": 281, "ASTRO": 395}),
        "page_counts": Counter(row["page"] for row in unified) == Counter({"f10r": 38, "f11r": 17, "f55v": 18, "f56r": 27, "f81v": 66, "f82r": 62, "f83r": 153, "f67r2": 190, "f68r1": 65, "f69v": 140}),
        "unique_source_ids": len({(row["section"], row["local_event_id"]) for row in unified}) == 776,
        "all_values": all(row["portable_or_local_value_de"] and row["complete_local_instruction_de"] for row in unified),
        "units14": len(units) == 14 and set(row["unit_id"] for row in units) == {f"H{i}" for i in range(1, 6)} | {f"B{i}" for i in range(1, 7)} | {f"A{i}" for i in range(1, 4)},
        "unit_groups776": sum(int(row["visible_groups"]) for row in units) == 776,
        "pages10": len(pages) == 10 and len({row["page"] for row in pages}) == 10,
        "page_groups776": sum(int(row["visible_groups"]) for row in pages) == 776,
        "manual15": len(manual) == 15 and [int(row["step"]) for row in manual] == list(range(1, 16)),
        "models3": len(models) == 3 and [int(row["working_rank"]) for row in models] == [1, 2, 3],
        "no_pointer": all(row["explicit_cross_pointer"] == "NO" for row in units),
        "astro_layer_separate": all(row["reader_layer"] == "LOCAL_CELESTIAL_EXEMPLAR_LABEL" for row in unified if row["section"] == "ASTRO"),
        "prose_layer_shared": all(row["reader_layer"] == "SHARED_COMPOSITIONAL_PROSE_GRAMMAR" for row in unified if row["section"] != "ASTRO"),
        "fixed_pages_only": set(row["page"] for row in unified) == {"f10r", "f11r", "f55v", "f56r", "f81v", "f82r", "f83r", "f67r2", "f68r1", "f69v"},
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / "FIVE_HUNDRED_NINETY_SECOND_VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    for key, value in checks.items():
        print(f"{key}\t{'PASS' if value else 'FAIL'}")
    if not all(checks.values()):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
