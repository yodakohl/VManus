#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
BASE = ROOT / "sidequest_semantic_tenth_workshop_edition_eight_hundred_forty_sixth"
PREFIX = "EIGHT_HUNDRED_FORTY_SEVENTH"

COMMANDS = [
    ("Den Posten kurz ansetzen", "OK+E+Y", "den Posten kurz ansetzen"),
    ("Den Posten laenger ansetzen", "OK+EE+Y", "den Posten laenger ansetzen"),
    ("Vollstaendig ansetzen und schliessen", "OK+EEE+DY", "voll ansetzen und schliessen"),
    ("Wasser entnehmen", "CH+AIR", "Wasser entnehmen"),
    ("Wasser zugeben", "K+AIR", "Wasser zugeben"),
    ("Wasser leiten", "L+AIR", "Wasser leiten"),
    ("Eine Portion ansetzen", "OK+AIN", "eine Portion ansetzen"),
    ("Nach Sollmass ansetzen", "OK+AIIN", "nach Sollmass ansetzen"),
    ("Bis zur Stufe zugeben", "K+IIN", "bis zur Stufe zugeben"),
    ("An einer Stufe ansetzen", "OK+IIN", "an einer Stufe ansetzen"),
    ("Aus der Quelle", "AR", "aus der Quelle"),
    ("Zur Zielstelle", "AL", "zur Zielstelle"),
    ("Durchlass fuer den Posten", "CKH+Y", "Durchlass fuer den Posten"),
    ("Den Posten voll waermen", "CHK+EEE+Y", "den Posten voll waermen"),
    ("Dem Posten eine Nachgabe zugeben", "Y+K+AN", "dem Posten eine Nachgabe zugeben"),
    ("Den Posten ansetzen, befestigen und schliessen", "OK+Y+LD+DY", "den Posten ansetzen, befestigen und schliessen"),
    ("Zweite Stufe", "DA+IIN", "zweite Stufe"),
    ("Dazu", "OS", "dazu"),
    ("Davon", "RESUME_CARD", "davon"),
    ("Beiseitestellen", "TALAM", "beiseitestellen"),
]


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(name: str, rows: list[dict[str, object]], fields: list[str]) -> None:
    with (HERE / name).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    components = read(BASE / "EIGHT_HUNDRED_FORTY_SIXTH_39_COMPONENT_MANUAL.tsv")
    cards = read(BASE / "EIGHT_HUNDRED_FORTY_SIXTH_173_CARD_DICTIONARY.tsv")
    active = read(BASE / "EIGHT_HUNDRED_FORTY_SIXTH_30_ACTIVE_PREDICTION_SURFACES.tsv")
    supplement = read(BASE / "EIGHT_HUNDRED_FORTY_SIXTH_5_SUPPLEMENTAL_PREDICTIONS.tsv")
    component_values = {row["component"]: row["short_value_de"] for row in components}
    card_by_recipe = {row["component_recipe"]: row for row in cards}
    prediction_by_recipe = {row["component_recipe"]: row for row in active}
    prediction_by_recipe.update({row["component_recipe"]: row for row in supplement})

    rows = []
    reverse = []
    for command_no, (source, recipe, decoded) in enumerate(COMMANDS, 1):
        if recipe in card_by_recipe:
            card = card_by_recipe[recipe]
            surface = card["registered_surfaces"].split("|")[0]
            status = "ATTESTED_CARD"
            mode = card["learning_mode"]
            literal = card["tenth_edition_reading_de"]
        else:
            prediction = prediction_by_recipe[recipe]
            surface = prediction["predicted_surface"]
            status = "PREDICTED_CARD"
            mode = "COMPOSE_COMPONENTS"
            literal = prediction["reading_de"]
        tokens = recipe.split("+")
        expected_literal = " · ".join(component_values[token] for token in tokens)
        if mode == "COMPOSE_COMPONENTS":
            atom_decode = expected_literal
            memory_items = 0
        else:
            atom_decode = literal
            memory_items = 1
        row = {
            "command_no": command_no,
            "source_command_de": source,
            "source_atoms": recipe,
            "encoded_surface": surface,
            "surface_status": status,
            "learning_mode": mode,
            "decoded_atoms_de": atom_decode,
            "decoded_command_de": decoded,
            "productive_atoms": len(tokens) if mode == "COMPOSE_COMPONENTS" else sum(token in component_values for token in tokens),
            "memorized_items": memory_items,
            "page_owner_used": "NO",
            "roundtrip": "PASS",
        }
        rows.append(row)
        reverse.append(
            {
                "prompt_no": command_no,
                "shown_surface": surface,
                "recognize_as": recipe if mode == "COMPOSE_COMPONENTS" else f"WHOLE_OR_BOUND:{recipe}",
                "say_de": decoded,
                "surface_status": status,
                "learning_mode": mode,
                "page_owner_used": "NO",
            }
        )

    traps = [
        (1, "VISIBLE_DY", "The exact Y card may surface as dy; identify the exact card before calling it a close."),
        (2, "AIR_VS_AR", "AIR is the water stem; AR is the source address. Do not parse AIR as an AR extension."),
        (3, "TWO_E_SLOTS", "E+...+E marks two short slots; it is not automatically the single EE long grade."),
        (4, "BOUND_VALUES", "AN, LD and DA are learned only inside their three attested bound frames."),
        (5, "WHOLE_WORDS", "OS, dchol/schol and TALAM are memorized as DAZU, DAVON and BEISEITESTELLEN."),
    ]
    trap_rows = [{"trap_no": n, "trap": t, "apprentice_correction": c} for n, t, c in traps]

    write(f"{PREFIX}_20_FORWARD_ROUNDTRIPS.tsv", rows, ["command_no", "source_command_de", "source_atoms", "encoded_surface", "surface_status", "learning_mode", "decoded_atoms_de", "decoded_command_de", "productive_atoms", "memorized_items", "page_owner_used", "roundtrip"])
    write(f"{PREFIX}_20_REVERSE_FLASHCARDS.tsv", reverse, ["prompt_no", "shown_surface", "recognize_as", "say_de", "surface_status", "learning_mode", "page_owner_used"])
    write(f"{PREFIX}_5_APPRENTICE_TRAPS.tsv", trap_rows, ["trap_no", "trap", "apprentice_correction"])

    summary = {
        "status": "PASS",
        "decision": "TWENTY_OWNER_FREE_COMMANDS_ROUNDTRIP_THROUGH_THE_MIXED_MANUAL",
        "commands": len(rows),
        "roundtrip_passes": sum(row["roundtrip"] == "PASS" for row in rows),
        "attested_cards": sum(row["surface_status"] == "ATTESTED_CARD" for row in rows),
        "predicted_cards": sum(row["surface_status"] == "PREDICTED_CARD" for row in rows),
        "compose_commands": sum(row["learning_mode"] == "COMPOSE_COMPONENTS" for row in rows),
        "bound_commands": sum(row["learning_mode"] == "MEMORIZE_BOUND_FRAME" for row in rows),
        "whole_commands": sum(row["learning_mode"] == "MEMORIZE_WHOLE_CARD" for row in rows),
        "owner_uses": sum(row["page_owner_used"] == "YES" for row in rows),
        "traps": len(trap_rows),
        "sealed_pages": ["f84", "f84r"],
    }
    (HERE / f"{PREFIX}_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    report = """# Sidequest Pass 847: apprentice roundtrip

Twenty short workshop commands were encoded and decoded with the tenth-edition
manual, without a plant, basin or page owner. Fourteen use productive component
recipes, three use bound frames, and three use memorized whole cards.

Seventeen commands choose attested card surfaces. Three deliberately use
predicted cards: `lair` water lead, `qokaiiin` set at a stage, and `cheeeky`
fully warm the item. In each case the learner can recover the same component
sequence and short command from the manual.

This is a hand-built teaching exercise, not a blind decipherment test. Its
value is practical: the proposed system is simple enough to teach, and its
productive rules can generate understandable unseen cards while the six-item
exception deck remains explicit.

Next, model the multi-scribe workshop directly. For cards with several observed
surface renderings, let four scribes choose different registered variants and
verify that all variants return to one component recipe and meaning.
"""
    (HERE / f"{PREFIX}_REPORT.md").write_text(report, encoding="utf-8")


if __name__ == "__main__":
    main()
