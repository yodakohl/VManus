#!/usr/bin/env python3
from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
BASE = ROOT / "experiments/yolo/sidequest_semantic_vocabulary_granularity_two_hundred_third"
BRIDGE = ROOT / "experiments/yolo/sidequest_semantic_cross_register_bridge_two_hundred_eleventh"
ASTRO = ROOT / "experiments/yolo/sidequest_semantic_astro_surface_transfer/ASTRO_395_SURFACE_PARSE.tsv"
DICT = BASE / "TWO_HUNDRED_THIRD_173_CARD_COMPACT_DICTIONARY.tsv"
EVENTS = BASE / "TWO_HUNDRED_THIRD_381_EVENT_COMPACT_EDITION.tsv"
STATEMENTS = BASE / "TWO_HUNDRED_THIRD_116_STATEMENT_COMPACT_EDITION.tsv"
BRIDGE_CARDS = BRIDGE / "TWO_HUNDRED_ELEVENTH_17_CROSS_REGISTER_CARDS.tsv"

REVISIONS = {
    "MC039": ("Sollwert", "Sollmaß remains the local Herbal/Bio quantity expansion; Astro uses a parameter or table value."),
    "MC119": ("Freigabewert", "Klarlauf remains the local wet-process expansion; Astro uses a read-off or released diagram value."),
}


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(path: Path, rows: list[dict[str, object]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    dictionary = read(DICT)
    events = read(EVENTS)
    statements = read(STATEMENTS)
    astro = read(ASTRO)
    bridge_ids = {row["master_card_id"] for row in read(BRIDGE_CARDS)}
    old_values = {row["master_card_id"]: row["current_value_de"] for row in dictionary}
    surface_map = {
        surface: row["master_card_id"]
        for row in dictionary
        for surface in row["registered_surfaces"].split("|")
    }

    revision_rows: list[dict[str, object]] = []
    for card_id, (new_value, reason) in REVISIONS.items():
        card = next(row for row in dictionary if row["master_card_id"] == card_id)
        revision_rows.append({
            "master_card_id": card_id,
            "master_form": card["master_form"],
            "registered_surfaces": card["registered_surfaces"],
            "old_portable_value_de": card["current_value_de"],
            "new_cross_register_value_de": new_value,
            "herbal_bio_local_expansion_de": "Sollmaß" if card_id == "MC039" else "Klarlauf",
            "astro_local_expansion_de": "Soll-/Parameterwert" if card_id == "MC039" else "abgelesener oder freigegebener Diagrammwert",
            "revision_reason": reason,
        })
        card["current_value_de"] = new_value
    write(OUT / "TWO_HUNDRED_THIRTEENTH_TWO_PORTABLE_REVISIONS.tsv", revision_rows)
    write(OUT / "TWO_HUNDRED_THIRTEENTH_173_CARD_CROSS_REGISTER_DICTIONARY.tsv", dictionary)
    selected = {card_id: value for card_id, (value, _) in REVISIONS.items()}
    for event in events:
        if event["master_card_id"] in selected:
            event["portable_value_de"] = selected[event["master_card_id"]]
    write(OUT / "TWO_HUNDRED_THIRTEENTH_381_EVENT_CROSS_REGISTER_PROSE.tsv", events)
    by_statement: dict[str, list[dict[str, str]]] = defaultdict(list)
    for event in events:
        by_statement[event["statement_id"]].append(event)
    for statement in statements:
        statement["literal_card_reading"] = " | ".join(row["portable_value_de"] for row in by_statement[statement["statement_id"]])
    write(OUT / "TWO_HUNDRED_THIRTEENTH_116_STATEMENT_CROSS_REGISTER_PROSE.tsv", statements)

    group_rows: list[dict[str, object]] = []
    for group in astro:
        card_id = surface_map.get(group["visible_surface"], "NONE")
        is_bridge = card_id in bridge_ids
        current_value = next((row["current_value_de"] for row in dictionary if row["master_card_id"] == card_id), "NONE")
        group_rows.append({
            "group_serial": group["group_serial"],
            "page": group["page"],
            "locus": group["locus"],
            "visible_owner": group["visible_owner"],
            "namespace_id": group["namespace_id"],
            "visible_surface": group["visible_surface"],
            "exact_prose_card_id": card_id,
            "exact_prose_value_de": current_value,
            "is_herbal_bio_bridge_card": "YES" if is_bridge else "NO",
            "astro_local_reading_de": group["existing_astro_reading_de"],
            "cross_register_rule": "PORTABLE_CORE_PLUS_LOCAL_ASTRO_EXPANSION" if is_bridge else "ASTRO_LOCAL_LABEL_OR_NONBRIDGE_PROSE_MATCH",
        })
    write(OUT / "TWO_HUNDRED_THIRTEENTH_395_ASTRO_SURFACE_BRIDGE.tsv", group_rows)

    matches = [row for row in group_rows if row["is_herbal_bio_bridge_card"] == "YES"]
    by_match_card: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in matches:
        by_match_card[str(row["exact_prose_card_id"])].append(row)
    summary_rows: list[dict[str, object]] = []
    for card_id, rows in sorted(by_match_card.items(), key=lambda item: (-len(item[1]), int(item[0][2:]))):
        summary_rows.append({
            "master_card_id": card_id,
            "registered_surfaces_seen": "|".join(dict.fromkeys(str(row["visible_surface"]) for row in rows)),
            "selected_cross_register_value_de": next(row["current_value_de"] for row in dictionary if row["master_card_id"] == card_id),
            "astro_group_count": len(rows),
            "pages": "|".join(dict.fromkeys(str(row["page"]) for row in rows)),
            "loci": "|".join(dict.fromkeys(str(row["locus"]) for row in rows)),
            "first_astro_local_reading_de": rows[0]["astro_local_reading_de"],
            "decision": "ABSTRACT_PORTABLE_VALUE_REVISED" if card_id in REVISIONS else "KEEP_CURRENT_PORTABLE_VALUE_WITH_LOCAL_ASTRO_EXPANSION",
        })
    write(OUT / "TWO_HUNDRED_THIRTEENTH_13_ASTRO_BRIDGE_CARD_SUMMARY.tsv", summary_rows)

    summary = {
        "dictionary_source_sha256": hashlib.sha256(DICT.read_bytes()).hexdigest(),
        "astro_source_sha256": hashlib.sha256(ASTRO.read_bytes()).hexdigest(),
        "cards": len(dictionary),
        "prose_events": len(events),
        "prose_statements": len(statements),
        "astro_groups": len(group_rows),
        "all_prose_surface_matches": sum(row["exact_prose_card_id"] != "NONE" for row in group_rows),
        "bridge_surface_matches": len(matches),
        "bridge_cards_in_astro": len(summary_rows),
        "bridge_matches_by_page": dict(Counter(str(row["page"]) for row in matches)),
        "portable_revisions": len(REVISIONS),
        "distinct_values_before": len(set(old_values.values())),
        "distinct_values_after": len({row["current_value_de"] for row in dictionary}),
        "sealed_pages_accessed": False,
    }
    (OUT / "BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
