#!/usr/bin/env python3
"""Validate the atomic-default dictionary."""

from __future__ import annotations

import csv
import json
from pathlib import Path


OUT = Path(__file__).resolve().parent


def rows(name: str) -> list[dict[str, str]]:
    with (OUT / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    components = rows("HUNDRED_FIRST_44_ATOMIC_COMPONENTS.tsv")
    dictionary = rows("HUNDRED_FIRST_173_ATOMIC_DICTIONARY.tsv")
    revisions = rows("HUNDRED_FIRST_REVISED_DEFAULTS.tsv")
    events = rows("HUNDRED_FIRST_381_EVENT_ATOMIC_INTERLINEAR.tsv")
    component_map = {row["atom"]: row["atomic_default_de"] for row in components}
    checks = {
        "components_44": len(components) == 44,
        "component_atoms_unique": len(component_map) == 44,
        "cards_173": len(dictionary) == 173,
        "events_381": len(events) == 381,
        "dictionary_ids_unique": len({row["master_card_id"] for row in dictionary}) == 173,
        "atomic_defaults_exact": all(row["atomic_default_de"] == "+".join(component_map[atom] for atom in row["semantic_atoms"].split("+")) for row in dictionary),
        "max_four_atomic_units": max(int(row["atomic_unit_count"]) for row in dictionary) <= 4,
        "no_sentence_punctuation": all(not any(mark in row["atomic_default_de"] for mark in ";,.:") for row in dictionary),
        "event_dictionary_agreement": all(next(row["atomic_default_de"] for row in dictionary if row["master_card_id"] == event["master_card_id"]) == event["atomic_default_de"] for event in events),
        "taiin_not_ty": all(event["semantic_atoms"] == "AIIN" for event in events if event["visible_surface"] == "taiin"),
        "revisions_nonempty": len(revisions) > 0,
        "sealed_absent": all("f84" not in "\t".join(row.values()).lower() for row in events),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (OUT / "VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if result["status"] != "PASS":
        raise SystemExit(json.dumps(result, ensure_ascii=False, indent=2))
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
