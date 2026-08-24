#!/usr/bin/env python3
"""Build one complete B3 commission through the four-desk workshop."""

from __future__ import annotations

import csv
import json
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
P606 = ROOT / "experiments/yolo/sidequest_semantic_short_workshop_dictionary_six_hundred_sixth"
P680 = ROOT / "experiments/yolo/sidequest_semantic_owner_expanded_compact_edition_six_hundred_eightieth"
P690 = ROOT / "experiments/yolo/sidequest_semantic_statement_core_projection_six_hundred_ninetieth"
P692 = ROOT / "experiments/yolo/sidequest_semantic_workshop_floor_plan_six_hundred_ninety_second"

DESK_PRIORITY = [
    "S04_STATE_CONTROL",
    "S03_TRANSFER",
    "S02_PREPARATION_WET",
    "S01_MASTER_CORRECTOR",
]


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(name: str, rows: list[dict[str, object]]) -> None:
    with (HERE / name).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle, delimiter="\t", fieldnames=list(rows[0]), lineterminator="\n"
        )
        writer.writeheader()
        writer.writerows(rows)


def specialist_components(recipe: str) -> list[str]:
    if recipe == "NONE":
        return []
    return recipe.replace("+", " ").split()


def compact_runs(values: list[str]) -> str:
    runs: list[str] = []
    for value in values:
        if not runs or not runs[-1].startswith(value + "×"):
            runs.append(value + "×1")
        else:
            head, count = runs[-1].rsplit("×", 1)
            runs[-1] = f"{head}×{int(count) + 1}"
    return " > ".join(runs)


def main() -> None:
    HERE.mkdir(parents=True, exist_ok=True)
    event_source = read(P690 / "SIX_HUNDRED_NINETIETH_381_EVENT_CORE_PROJECTION.tsv")
    statement_source = read(P690 / "SIX_HUNDRED_NINETIETH_116_STATEMENT_CORE_PROJECTION.tsv")
    locus_source = read(P606 / "SIX_HUNDRED_SIXTH_381_SHORT_EVENT_EDITION.tsv")
    owner_source = read(P680 / "SIX_HUNDRED_EIGHTIETH_116_COMPACT_OWNER_STATEMENTS.tsv")
    assignments = read(P692 / "SIX_HUNDRED_NINETY_SECOND_26_ROOT_ASSIGNMENTS.tsv")

    role_for_component = {row["component"]: row["scribe_role"] for row in assignments}
    locus_by_event = {row["event_id"]: row for row in locus_source}
    statement_by_id = {row["statement_id"]: row for row in statement_source}
    owner_by_statement = {row["statement_id"]: row for row in owner_source}
    events = [row for row in event_source if row["record"] == "B3"]

    event_rows: list[dict[str, object]] = []
    composite_rows: list[dict[str, object]] = []
    for packet_position, event in enumerate(events, 1):
        components = specialist_components(event["specialist_recipe"])
        roles = sorted({role_for_component[component] for component in components})
        selected_by = next(
            (role for role in DESK_PRIORITY if role in roles), "S01_MASTER_CORRECTOR"
        )
        is_composite = len(roles) > 1
        locus = locus_by_event[event["event_id"]]
        owner = owner_by_statement[event["statement_id"]]
        if selected_by == "S01_MASTER_CORRECTOR":
            action = "Taschenkernkarte auf dem Entwurfsstreifen vormerken."
        elif selected_by == "S02_PREPARATION_WET":
            action = "Ganze Vorbereitungs-/Nasskarte aus dem lokalen Fach waehlen."
        elif selected_by == "S03_TRANSFER":
            action = "Ganze Transferkarte waehlen; fremden Komponentenhinweis mitlesen."
        else:
            action = "Ganze Zustandskarte waehlen; Grad und Schlussform gemeinsam pruefen."
        event_rows.append({
            "packet_position": packet_position,
            "event_id": event["event_id"],
            "locus": locus["locus"],
            "statement_id": event["statement_id"],
            "owner_de": locus["silent_owner_de"],
            "surface": event["surface"],
            "full_recipe": event["full_recipe"],
            "atomic_reading_de": event["full_reading_de"],
            "pocket_core_recipe": event["pocket_core_recipe"],
            "specialist_recipe": event["specialist_recipe"],
            "specialist_roles": "|".join(roles) if roles else "POCKET_CORE_ONLY",
            "selected_by_desk": selected_by,
            "composite_junction_card": "YES" if is_composite else "NO",
            "desk_action_de": action,
            "final_inscription_by": "S01_MASTER_FINAL_COPY",
            "whole_card_rule_de": "Eine sichtbare Karte bleibt ungeteilt; kein Tisch schreibt nur ein Teilzeichen auf Pergament.",
        })
        if is_composite:
            composite_rows.append({
                "event_id": event["event_id"],
                "locus": locus["locus"],
                "statement_id": event["statement_id"],
                "surface": event["surface"],
                "full_recipe": event["full_recipe"],
                "component_desks": "|".join(roles),
                "whole_card_selected_by": selected_by,
                "junction_rule_de": "Der spaetere Arbeitstisch besitzt die ganze Musterkarte; der fruehere Tisch liefert nur den Komponentenhinweis auf dem Entwurfsstreifen.",
            })

    events_by_statement: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in event_rows:
        events_by_statement[str(row["statement_id"])].append(row)
    statement_rows: list[dict[str, object]] = []
    for statement in [row for row in statement_source if row["record"] == "B3"]:
        rows = events_by_statement[statement["statement_id"]]
        desk_counts = Counter(str(row["selected_by_desk"]) for row in rows)
        loci = list(dict.fromkeys(str(row["locus"]) for row in rows))
        owner = owner_by_statement[statement["statement_id"]]
        statement_rows.append({
            "statement_id": statement["statement_id"],
            "loci": "|".join(loci),
            "events": len(rows),
            "owner_de": statement["owner_noun_de"],
            "surface_sequence": statement["surface_sequence"],
            "desk_selection_sequence": compact_runs([str(row["selected_by_desk"]) for row in rows]),
            "master_core_cards": desk_counts["S01_MASTER_CORRECTOR"],
            "preparation_wet_cards": desk_counts["S02_PREPARATION_WET"],
            "transfer_cards": desk_counts["S03_TRANSFER"],
            "state_cards": desk_counts["S04_STATE_CONTROL"],
            "junction_cards": sum(row["composite_junction_card"] == "YES" for row in rows),
            "owner_break_inside_statement": owner["owner_break_inside_statement"],
            "continuous_owner_reading_de": statement["complete_owner_reading_de"],
            "final_copy_rule_de": "Nach allen Auswahlmarken schreibt eine Hand die Oberflaechenfolge ohne Tischgrenze durch.",
        })

    events_by_locus: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in event_rows:
        events_by_locus[str(row["locus"])].append(row)
    locus_rows: list[dict[str, object]] = []
    for locus, rows in events_by_locus.items():
        locus_rows.append({
            "locus": locus,
            "event_range": f"{rows[0]['event_id']}..{rows[-1]['event_id']}",
            "events": len(rows),
            "statements": " ".join(dict.fromkeys(str(row["statement_id"]) for row in rows)),
            "owner_sequence_de": " | ".join(dict.fromkeys(str(row["owner_de"]) for row in rows)),
            "surface_sequence": " ".join(str(row["surface"]) for row in rows),
            "desk_selection_sequence": compact_runs([str(row["selected_by_desk"]) for row in rows]),
            "final_copy_de": "Eine Hand kopiert diese Folge von links nach rechts; das Zeilenende beendet nicht automatisch die Anweisung.",
        })

    handoff_rows = [
        {"step": 1, "packet_from": "ILLUMINATOR_OR_DRAWING_TABLE", "packet_to": "S01_MASTER_CORRECTOR", "packet_content_de": "Gezeichnetes f83r-Blatt plus B3-Musterstreifen.", "action_de": "Fuenf sichtbare Besitzer und zehn Textloci auf dem Streifen adressieren."},
        {"step": 2, "packet_from": "S01_MASTER_CORRECTOR", "packet_to": "S02_PREPARATION_WET", "packet_content_de": "86 Positionsplaetze;39 Kernkarten bereits vorgemerkt.", "action_de": "Fuenf ganze Vorbereitungs-/Nasskarten auswaehlen."},
        {"step": 3, "packet_from": "S02_PREPARATION_WET", "packet_to": "S03_TRANSFER", "packet_content_de": "Kern plus Nassauswahl; drei Kreuzkarten nur als Komponentenhinweis.", "action_de": "25 ganze Transferkarten auswaehlen, darunter drei Nass/Transfer-Kreuzkarten."},
        {"step": 4, "packet_from": "S03_TRANSFER", "packet_to": "S04_STATE_CONTROL", "packet_content_de": "69 von86 Positionen festgelegt; zwei Transfer/Zustand-Kreuzkarten markiert.", "action_de": "17 ganze Zustandskarten auswaehlen, Grade und Endformen pruefen."},
        {"step": 5, "packet_from": "S04_STATE_CONTROL", "packet_to": "S01_MASTER_FINAL_COPY", "packet_content_de": "Vollstaendiger86-Karten-Entwurfsstreifen.", "action_de": "Alle Oberflaechen in einem Zug um die fertigen Bilder kopieren."},
        {"step": 6, "packet_from": "S01_MASTER_FINAL_COPY", "packet_to": "CORRECTION_SHELF", "packet_content_de": "Fertige Seite plus Entwurfsstreifen.", "action_de": "34 Anweisungen ruecklesen; zwei Besitzerwechsel innerhalb laufender Anweisungen pruefen."},
    ]

    write("SIX_HUNDRED_NINETY_THIRD_86_EVENT_DESK_TRACE.tsv", event_rows)
    write("SIX_HUNDRED_NINETY_THIRD_34_STATEMENT_HANDOFFS.tsv", statement_rows)
    write("SIX_HUNDRED_NINETY_THIRD_10_LOCUS_COPY_SHEETS.tsv", locus_rows)
    write("SIX_HUNDRED_NINETY_THIRD_5_COMPOSITE_JUNCTION_CARDS.tsv", composite_rows)
    write("SIX_HUNDRED_NINETY_THIRD_6_PACKET_HANDOFFS.tsv", handoff_rows)

    edition = ["# B3-Werkstattauftrag: vollständige Lesefolge", ""]
    for row in statement_rows:
        edition.extend([
            f"## {row['statement_id']} — {row['loci']}",
            "",
            f"Karten: `{row['surface_sequence']}`",
            "",
            str(row["continuous_owner_reading_de"]),
            "",
            f"Auswahltische: `{row['desk_selection_sequence']}`",
            "",
        ])
    (HERE / "SIX_HUNDRED_NINETY_THIRD_COMPLETE_B3_WORKSHOP_EDITION.md").write_text(
        "\n".join(edition), encoding="utf-8"
    )

    desk_counts = Counter(str(row["selected_by_desk"]) for row in event_rows)
    summary = {
        "status": "PASS",
        "record": "B3",
        "page": "f83r",
        "events": len(event_rows),
        "statements": len(statement_rows),
        "physical_loci": len(locus_rows),
        "visible_owners": len({row["owner_de"] for row in event_rows}),
        "selected_card_counts": dict(desk_counts),
        "composite_junction_cards": len(composite_rows),
        "owner_break_statements": sum(row["owner_break_inside_statement"] == "YES" for row in statement_rows),
        "final_copy_hands": 1,
        "packet_handoffs": len(handoff_rows),
    }
    (HERE / "SIX_HUNDRED_NINETY_THIRD_BUILD_SUMMARY.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


if __name__ == "__main__":
    main()
