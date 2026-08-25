#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from collections import Counter
from pathlib import Path


HERE = Path(__file__).resolve().parent


def read(name: str) -> list[dict[str, str]]:
    with (HERE / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    lexicon = read("PASS980_158_TEACHING_UNIT_CODEBOOK.tsv")
    events = read("PASS980_2511_EVENT_TEACHING_BINDING.tsv")
    ids = {r["teaching_unit_id"] for r in lexicon}
    layers = Counter(r["layer"] for r in lexicon)
    primary = Counter(r["primary_layer"] for r in events)
    referenced = {
        unit
        for row in events
        for field in ("primary_teaching_unit_ids", "mnemonic_common_unit_ids")
        for unit in row[field].split("|") if unit
    }
    checks = {
        "teaching_units_158": len(lexicon) == 158,
        "teaching_unit_ids_unique": len(ids) == 158,
        "base_137": sum(not r["teaching_unit_id"].startswith(("L", "D")) for r in lexicon) == 137,
        "f13_cards_5": layers["F_IMAGE_OWNED_SPECIALIST_CARD"] == 5,
        "f88_labels_16": layers["G_DRUG_LABEL_NOMENCLATOR"] == 16,
        "events_2511": len(events) == 2511,
        "event_ids_unique": len({r["event_id"] for r in events}) == 2511,
        "all_units_resolve": referenced <= ids,
        "all_have_primary_unit": all(r["primary_teaching_unit_ids"] for r in events),
        "all_have_reading": all(r["complete_working_reading_de"] for r in events),
        "old_specialist_events_95": primary["MEMORIZED_SPECIALIST_WHOLE_WORD"] == 95,
        "new_f13_events_5": primary["IMAGE_OWNED_SPECIALIST_CARD"] == 5,
        "f88_label_events_16": primary["DRUG_LABEL_NOMENCLATOR"] == 16,
        "sealed_absent": all("f84" not in r["physical_page"].lower() for r in events),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks, "primary_layers": dict(primary)}
    (HERE / "PASS980_VALIDATION.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    if result["status"] != "PASS":
        raise SystemExit(json.dumps(result, indent=2))
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
