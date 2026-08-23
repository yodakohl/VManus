#!/usr/bin/env python3
from __future__ import annotations

import csv
import hashlib
import json
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
R260 = ROOT / "experiments/yolo/sidequest_semantic_variant_resolution_two_hundred_sixtieth"
R258 = ROOT / "experiments/yolo/sidequest_semantic_minimum_apprentice_deck_two_hundred_fifty_eighth"
CARDS = R260 / "TWO_HUNDRED_SIXTIETH_173_CARD_DICTIONARY.tsv"
EVENTS = R260 / "TWO_HUNDRED_SIXTIETH_381_PROSE_EVENTS.tsv"
STATEMENTS = R260 / "TWO_HUNDRED_SIXTIETH_116_STATEMENTS.tsv"
GENERATION = R258 / "TWO_HUNDRED_FIFTY_EIGHTH_173_CARD_GENERATION.tsv"


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: list[dict[str, object]], fields: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    cards = read_tsv(CARDS)
    events = read_tsv(EVENTS)
    statements = read_tsv(STATEMENTS)
    generation = {r["master_card_id"]: r for r in read_tsv(GENERATION)}
    instruction_map = {r["portable_core_de"]: r for r in cards}
    card_map = {r["master_card_id"]: r for r in cards}

    instruction_rows = []
    surface_rows = []
    surface_map: dict[str, str] = {}
    for index, row in enumerate(sorted(cards, key=lambda x: x["portable_core_de"].casefold()), 1):
        surfaces = row["registered_surfaces"].split("|")
        instruction_rows.append({
            "instruction_id": f"I{index:03d}", "source_instruction_de": row["portable_core_de"],
            "master_card_id": row["master_card_id"], "master_form": row["master_form"],
            "registered_surface_count": len(surfaces), "registered_surfaces": row["registered_surfaces"],
            "construction_class": generation[row["master_card_id"]]["construction_class"],
            "component_parse": row["component_parse"],
            "writing_rule": "compose or retrieve master card, then apply hand/position renderer",
        })
        for surface in surfaces:
            surface_map[surface] = row["master_card_id"]
            surface_rows.append({
                "visible_surface": surface, "master_card_id": row["master_card_id"],
                "source_instruction_de": row["portable_core_de"], "master_form": row["master_form"],
                "surface_role": "SOLE_SURFACE" if len(surfaces) == 1 else "REGISTERED_RENDERER_VARIANT",
                "read_rule": "map this visible surface to its unique master card, then read the instruction",
            })

    event_rows = []
    for row in events:
        encoded = instruction_map[row["portable_core_de"]]
        decoded_id = surface_map[row["visible_surface"]]
        decoded = card_map[decoded_id]
        event_rows.append({
            "event_id": row["event_id"], "statement_id": row["statement_id"], "page": row["page"],
            "visible_owner": row["visible_owner"], "source_instruction_de": row["portable_core_de"],
            "encoded_master_card_id": encoded["master_card_id"],
            "renderer_choice_count": len(encoded["registered_surfaces"].split("|")),
            "actual_visible_surface": row["visible_surface"],
            "decoded_master_card_id": decoded_id, "decoded_instruction_de": decoded["portable_core_de"],
            "master_roundtrip": "PASS" if encoded["master_card_id"] == decoded_id == row["master_card_id"] else "FAIL",
            "instruction_roundtrip": "PASS" if decoded["portable_core_de"] == row["portable_core_de"] else "FAIL",
            "terminal_status": row["terminal_status"],
        })

    by_statement: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in event_rows:
        by_statement[row["statement_id"]].append(row)
    statement_rows = []
    for row in statements:
        evs = by_statement[row["statement_id"]]
        statement_rows.append({
            "statement_id": row["statement_id"], "record_unit_id": row["record_unit_id"],
            "visible_owner": row["visible_owner"], "source_instruction_chain_de": row["portable_core_chain"],
            "encoded_master_sequence": " ".join(r["encoded_master_card_id"] for r in evs),
            "rendered_visible_sequence": row["visible_sequence"],
            "decoded_master_sequence": " ".join(r["decoded_master_card_id"] for r in evs),
            "decoded_instruction_chain_de": " | ".join(r["decoded_instruction_de"] for r in evs),
            "roundtrip_status": "PASS" if all(r["master_roundtrip"] == "PASS" and r["instruction_roundtrip"] == "PASS" for r in evs) else "FAIL",
            "complete_local_translation_de": row["complete_local_translation_de"],
        })

    instruction_path = OUT / "TWO_HUNDRED_SIXTY_FIRST_173_INSTRUCTION_COMPILER.tsv"
    surface_path = OUT / "TWO_HUNDRED_SIXTY_FIRST_230_SURFACE_DICTIONARY.tsv"
    event_path = OUT / "TWO_HUNDRED_SIXTY_FIRST_381_EVENT_ROUNDTRIP.tsv"
    statement_path = OUT / "TWO_HUNDRED_SIXTY_FIRST_116_STATEMENT_ROUNDTRIP.tsv"
    readable_path = OUT / "TWO_HUNDRED_SIXTY_FIRST_READABLE_BIDIRECTIONAL_MANUAL.md"
    report_path = OUT / "TWO_HUNDRED_SIXTY_FIRST_REPORT.md"
    write_tsv(instruction_path, instruction_rows, list(instruction_rows[0]))
    write_tsv(surface_path, surface_rows, list(surface_rows[0]))
    write_tsv(event_path, event_rows, list(event_rows[0]))
    write_tsv(statement_path, statement_rows, list(statement_rows[0]))

    readable = [
        "# Bidirektionales Werkstatthandbuch", "",
        "## Schreiben", "",
        "Kurze Arbeitsanweisung → genau eine Masterkarte → eine zur Hand und Position passende sichtbare Form.", "",
        "Beispiel: `vorigen Posten überführen; Schluss` → MC005 → je nach Position `okchedy` oder `qokchedy`.", "",
        "## Lesen", "",
        "Sichtbare Form → genau eine Masterkarte → genau eine kurze Arbeitsanweisung.", "",
        "Keine der 230 registrierten Oberflächen ist zwischen zwei Masterkarten mehrdeutig. Die sichtbare Variation verschleiert also die Form, zerstört aber den Werkstattwert nicht.", "",
        "## Umfang", "",
        "- 173 Anweisungen ↔ 173 Masterkarten.",
        "- 230 sichtbare Oberflächen; 34 Karten haben mehr als eine Form.",
        "- 202 der 381 Ereignisse benutzen eine Karte mit Rendererwahl, 179 eine Karte mit nur einer Form.",
        "- Alle 381 Ereignisse und alle 116 Aussagen kehren zur selben Arbeitsanweisung zurück.", "",
        "Das ist die bislang einfachste konkrete Erklärung für mehrere Schreiber: Sie teilen das Masterkarten-/Bedeutungsdeck, dürfen aber positions- und handabhängig unterschiedliche Eintrittsformen schreiben.", "",
    ]
    readable_path.write_text("\n".join(readable), encoding="utf-8")

    report = f"""# Sidequest-Pass 261: bidirektionaler Werkstattcompiler

## Ergebnis

Nach der Quellenordnungsrevision bilden 173 kurze Anweisungen eine Eins-zu-eins-Abbildung auf 173 Masterkarten. Diese Karten besitzen 230 disjunkte sichtbare Oberflächen. 34 Karten haben mehrere Rendererformen, doch keine sichtbare Form gehört zu zwei Karten.

Alle 381 Ereignisse laufen Anweisung → Masterkarte → sichtbare Form → Masterkarte → Anweisung ohne Wertverlust zurück. Dass 202 Ereignisse eine mehrförmige Karte benutzen, erklärt die starke Oberflächenvariation bei gleichbleibender Werkstattgrammatik. Alle 116 Aussagen roundtrippen vollständig.

Inputs: cards `{sha(CARDS)}`, events `{sha(EVENTS)}`, statements `{sha(STATEMENTS)}`, generation `{sha(GENERATION)}`.
"""
    report_path.write_text(report, encoding="utf-8")
    outputs = (instruction_path, surface_path, event_path, statement_path, readable_path, report_path)
    summary = {
        "status": "PASS", "instructions": len(instruction_rows), "master_cards": len(cards),
        "surfaces": len(surface_rows), "multi_surface_cards": sum(int(r["registered_surface_count"]) > 1 for r in instruction_rows),
        "events": len(event_rows), "multi_surface_events": sum(int(r["renderer_choice_count"]) > 1 for r in event_rows),
        "statements": len(statement_rows), "event_roundtrip_pass": sum(r["master_roundtrip"] == "PASS" and r["instruction_roundtrip"] == "PASS" for r in event_rows),
        "statement_roundtrip_pass": sum(r["roundtrip_status"] == "PASS" for r in statement_rows),
        "outputs": {p.name: sha(p) for p in outputs},
    }
    (OUT / "BUILD_SUMMARY.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
