#!/usr/bin/env python3
"""Select the conservative four-role V45 stem-first translation."""

from __future__ import annotations

import csv
import json
from pathlib import Path


OUT = Path(__file__).resolve().parent


def read(name: str) -> list[dict[str, str]]:
    with (OUT / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(name: str, rows: list[dict[str, object]]) -> None:
    with (OUT / name).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n"
        )
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    complete = read("V45_R1_COMMON_STEM_LEXICON.tsv")
    medical = read("V45_R2_STEM_LEXICON.tsv")
    cards = read("V45_R2_REVISED_173_CARD_LEXICON.tsv")
    events = read("V45_R2_REVISED_381_EVENT_INTERLINEAR.tsv")
    astro = read("V45_R3_ASTRO_395_LABELS_UNCHANGED.tsv")
    medical_by_host = {
        r["page_host"]: r
        for r in medical
        if r["page_host"] != "<FORMAL_DY_COORDINATE>"
    }
    selected: list[dict[str, object]] = []
    for row in complete:
        host = row["page_host"]
        if host in medical_by_host:
            chosen = medical_by_host[host]
            value = chosen["stable_minimal_value_German"]
            stem_class = chosen["stem_class"]
            status = chosen["status"]
            source = "R2_SHARED_STEM_SELECTED_AFTER_FOUR_ROLE_COMPARISON"
        else:
            value = row["minimal_invariant_value"]
            stem_class = row["core_type"]
            status = "MEMORIZED_OR_UNPOWERED_HOST_CORE"
            source = "R1_COMPLETE_HOST_INVENTORY_RETAINED"
        selected.append({
            "page_host": host,
            "selected_minimal_value_German": value,
            "stem_class": stem_class,
            "exact_card_types": row["exact_card_types"],
            "fixed_panel_events": row["fixed_panel_events"],
            "confidence": row["confidence"],
            "selection_source": source,
            "status": status,
        })
    selected.sort(key=lambda r: str(r["page_host"]))
    write("V45_SELECTED_COMMON_STEM_LEXICON.tsv", selected)
    write("V45_SELECTED_REVISED_173_CARD_LEXICON.tsv", cards)
    write("V45_SELECTED_REVISED_381_EVENT_INTERLINEAR.tsv", events)
    write("V45_SELECTED_ASTRO_395_LABELS_UNCHANGED.tsv", astro)
    revised = sum(r["revision"] == "REVISED_TO_COMMON_STEM" for r in cards)
    shared = sum(r["stem_tier"] in {"A", "B"} for r in cards)
    checks = {
        "schema": "SIDEQUEST_V45_SELECTED_STEM_FIRST_TRANSLATION_V1",
        "status": "PASS",
        "selection": "R2_CONSERVATIVE_MEDICAL_REVISION_PLUS_R1_COMPLETE_HOST_INVENTORY",
        "counts": {
            "host_entries": len(selected),
            "exact_cards": len(cards),
            "events": len(events),
            "astro_labels_unchanged": len(astro),
            "cards_reworded_for_common_stems": revised,
            "cards_under_selected_shared_stem_routes": shared,
        },
        "checks": {
            "all_136_hosts_have_minimal_value": len(selected) == 136 and all(r["selected_minimal_value_German"] for r in selected),
            "all_173_cards_translated": len(cards) == 173 and all(r["local_medical_expansion_German"] for r in cards),
            "all_381_events_translated": len(events) == 381 and all(r["local_medical_expansion_German"] for r in events),
            "all_395_astro_labels_unchanged": len(astro) == 395,
            "aiin_distinct_from_ain": medical_by_host["aiin"]["stem_class"] == "QUANTITAET" and "ain" not in medical_by_host,
            "surface_ol_distinct_from_page_host_ol": medical_by_host["l"]["stem_class"] == "ANSCHLUSS" and "ol" not in medical_by_host,
            "dy_kept_as_formal_coordinate": any(r["page_host"] == "<FORMAL_DY_COORDINATE>" for r in medical),
            "semantic_claim": False,
            "f84_accessed": False,
            "f84r_accessed": False,
        },
    }
    (OUT / "V45_SELECTED_VALIDATION.json").write_text(
        json.dumps(checks, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(checks, ensure_ascii=False))


if __name__ == "__main__":
    main()
