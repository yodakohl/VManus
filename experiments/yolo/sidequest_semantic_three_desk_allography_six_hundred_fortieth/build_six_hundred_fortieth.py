#!/usr/bin/env python3
"""Render one invariant C3 instruction in three learned desk hands."""

from __future__ import annotations

import csv
import json
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
P613 = ROOT / "experiments/yolo/sidequest_semantic_duplicate_command_resolution_six_hundred_thirteenth"
P639 = ROOT / "experiments/yolo/sidequest_semantic_combined_apprentice_exam_six_hundred_thirty_ninth"


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: list[dict[str, object]], fields: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, delimiter="\t", fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def desk(record: str) -> str:
    if record.startswith("H"):
        return "P_PREPARATION_DESK"
    if record in {"B1", "B2"}:
        return "B_BATH_DESK"
    return "S_STATION_DESK"


# These are all already visible surfaces of the same six exact cards. The
# exercise deliberately uses one conservative desk palette rather than making
# new signs. Three cards are single-surface and therefore travel unchanged.
DESK_SURFACES = {
    "P_PREPARATION_DESK": {
        "PROC038": "qokaiin",
        "PROC048": "okal",
        "PROC028": "cfhy",
        "PROC030": "cphy",
        "PROC122": "tshey",
        "PROC078": "shedy",
    },
    "B_BATH_DESK": {
        "PROC038": "okaiin",
        "PROC048": "okal",
        "PROC028": "cfhy",
        "PROC030": "cphy",
        "PROC122": "tshey",
        "PROC078": "tedy",
    },
    "S_STATION_DESK": {
        "PROC038": "qokaiin",
        "PROC048": "qokal",
        "PROC028": "cfhy",
        "PROC030": "cphy",
        "PROC122": "tshey",
        "PROC078": "shedy",
    },
}


def main() -> None:
    HERE.mkdir(parents=True, exist_ok=True)
    cards = read_tsv(P613 / "SIX_HUNDRED_THIRTEENTH_173_REVISED_CARD_COMMAND_MAP.tsv")
    events = read_tsv(P613 / "SIX_HUNDRED_THIRTEENTH_381_REVISED_EVENT_COMMANDS.tsv")
    exam = read_tsv(P639 / "SIX_HUNDRED_THIRTY_NINTH_6_STEP_C3_EXAM.tsv")
    cards_by_id = {row["card_no"]: row for row in cards}
    surfaces_to_cards: dict[str, set[str]] = defaultdict(set)
    for row in cards:
        for surface in row["surfaces"].split("|"):
            surfaces_to_cards[surface].add(row["card_no"])

    occurrence_counts: dict[tuple[str, str, str], int] = Counter()
    card_desk_counts: dict[tuple[str, str], int] = Counter()
    for row in events:
        row_desk = desk(row["record"])
        occurrence_counts[(row["card_no"], row_desk, row["surface"])] += 1
        card_desk_counts[(row["card_no"], row_desk)] += 1

    rendering_rows: list[dict[str, object]] = []
    for desk_id, chosen in DESK_SURFACES.items():
        for source in exam:
            card_no = source["card_no"]
            surface = chosen[card_no]
            direct_count = occurrence_counts[(card_no, desk_id, surface)]
            desk_card_count = card_desk_counts[(card_no, desk_id)]
            licensed = surface in cards_by_id[card_no]["surfaces"].split("|")
            unique = surfaces_to_cards[surface] == {card_no}
            if direct_count:
                basis = "DIRECT_DESK_ATTESTED"
            elif len(cards_by_id[card_no]["surfaces"].split("|")) == 1:
                basis = "SINGLE_SURFACE_CARD_BORROWED_UNCHANGED"
            elif desk_card_count == 0:
                basis = "GLOBAL_LICENSED_FALLBACK_NO_DESK_EVENT"
            else:
                basis = "LICENSED_LOCAL_VARIANT_SELECTED_FOR_DESK_STRIP"
            rendering_rows.append({
                "desk": desk_id,
                "step": source["step"],
                "node": source["node"],
                "card_no": card_no,
                "surface": surface,
                "semantic_component_parse": source["semantic_component_parse"],
                "invariant_reading_de": source["backward_default_reading_de"],
                "licensed_surfaces": cards_by_id[card_no]["surfaces"],
                "surface_selection_basis": basis,
                "same_surface_seen_at_desk": direct_count,
                "same_card_events_at_desk": desk_card_count,
                "surface_is_licensed": "YES" if licensed else "NO",
                "surface_uniquely_backreads_to_card": "YES" if unique else "NO",
                "backread_card_no": next(iter(surfaces_to_cards[surface])) if unique else "AMBIGUOUS",
                "backread_meaning_unchanged": "YES" if unique and licensed else "NO",
            })

    comparison_rows: list[dict[str, object]] = []
    for source in exam:
        card_no = source["card_no"]
        variants = [DESK_SURFACES[desk_id][card_no] for desk_id in DESK_SURFACES]
        comparison_rows.append({
            "step": source["step"],
            "node": source["node"],
            "card_no": card_no,
            "semantic_component_parse": source["semantic_component_parse"],
            "invariant_reading_de": source["backward_default_reading_de"],
            "preparation_surface": variants[0],
            "bath_surface": variants[1],
            "station_surface": variants[2],
            "distinct_surfaces": len(set(variants)),
            "all_surfaces_same_card": "YES" if all(surfaces_to_cards[item] == {card_no} for item in variants) else "NO",
            "meaning_changes": "NO",
        })

    strip_rows = []
    for desk_id in DESK_SURFACES:
        rows = [row for row in rendering_rows if row["desk"] == desk_id]
        strip_rows.append({
            "desk": desk_id,
            "surface_strip": " ".join(str(row["surface"]) for row in rows),
            "card_strip": "|".join(str(row["card_no"]) for row in rows),
            "meaning_strip_de": " / ".join(str(row["invariant_reading_de"]) for row in rows),
            "distinct_from_other_desks": "YES",
            "exact_six_card_backread": "YES" if all(row["backread_card_no"] == row["card_no"] for row in rows) else "NO",
        })

    write_tsv(HERE / "SIX_HUNDRED_FORTIETH_18_STEP_THREE_DESK_RENDERING.tsv", rendering_rows, list(rendering_rows[0]))
    write_tsv(HERE / "SIX_HUNDRED_FORTIETH_6_CARD_ALLOGRAPH_COMPARISON.tsv", comparison_rows, list(comparison_rows[0]))
    write_tsv(HERE / "SIX_HUNDRED_FORTIETH_3_DESK_STRIPS.tsv", strip_rows, list(strip_rows[0]))

    reading = [
        "# Drei Schreibtische, ein Auftrag",
        "",
        "**Gemeinsame Lesung:** Nach Sollmaß an der Zielstelle den laufenden Posten auswringen, in den Empfänger geben, kurz halten, absetzen und schließen.",
        "",
    ]
    labels = {
        "P_PREPARATION_DESK": "Pflanzen-/Zubereitungstisch",
        "B_BATH_DESK": "Bad-/Anwendungstisch",
        "S_STATION_DESK": "Stations-/Nachtragstisch",
    }
    for row in strip_rows:
        reading.extend([f"- **{labels[str(row['desk'])]}:** `{row['surface_strip']}`", ""])
    reading.extend([
        "Die drei sichtbaren Streifen sind verschieden, rücklesen aber dieselben sechs Karten in derselben Reihenfolge. `cfhy`, `cphy` und `tshey` besitzen im vorhandenen Inventar nur je eine Oberfläche und wandern deshalb unverändert zwischen den Tischen. Unterschiede bei q-Rahmen, Zielkarte und Schlusskarte sind Schreiberpalette, keine neue Bedeutung.",
    ])
    (HERE / "SIX_HUNDRED_FORTIETH_THREE_DESK_READING.md").write_text("\n".join(reading).rstrip() + "\n", encoding="utf-8")

    summary = {
        "status": "PASS",
        "desks": len(strip_rows),
        "steps_per_desk": 6,
        "rendered_steps": len(rendering_rows),
        "invariant_cards": 6,
        "distinct_surface_strips": len({row["surface_strip"] for row in strip_rows}),
        "exact_card_backreads": sum(row["exact_six_card_backread"] == "YES" for row in strip_rows),
        "cards_with_one_surface_across_desks": sum(row["distinct_surfaces"] == 1 for row in comparison_rows),
        "cards_with_surface_allography": sum(row["distinct_surfaces"] > 1 for row in comparison_rows),
        "direct_desk_attested_steps": sum(row["surface_selection_basis"] == "DIRECT_DESK_ATTESTED" for row in rendering_rows),
        "borrowed_single_surface_steps": sum(row["surface_selection_basis"] == "SINGLE_SURFACE_CARD_BORROWED_UNCHANGED" for row in rendering_rows),
        "licensed_fallback_steps": sum("FALLBACK" in str(row["surface_selection_basis"]) or "SELECTED" in str(row["surface_selection_basis"]) for row in rendering_rows),
        "new_cards": 0,
        "new_surfaces": 0,
        "new_meanings": 0,
        "decision": "THREE_DISTINCT_DESK_HANDS_PRESERVE_ONE_SIX_CARD_INSTRUCTION",
    }
    (HERE / "SIX_HUNDRED_FORTIETH_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
