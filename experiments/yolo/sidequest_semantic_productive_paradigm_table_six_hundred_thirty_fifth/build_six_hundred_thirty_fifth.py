#!/usr/bin/env python3
"""Extract compact one-dimension paradigms from the existing 173-card deck."""

from __future__ import annotations

import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
CARDS = ROOT / "experiments/yolo/sidequest_semantic_backread_noun_repair_six_hundred_seventeenth/SIX_HUNDRED_SEVENTEENTH_173_SHARP_COMMANDS.tsv"


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: list[dict[str, object]], fields: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, delimiter="\t", fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


CELLS = [
    ("OK_GRADE_ENDPOINT", "OK", "E", "Y", "OK+E+Y", "ANSETZEN KURZ; POSTEN BLEIBT AKTIV"),
    ("OK_GRADE_ENDPOINT", "OK", "EE", "Y", "OK+EE+Y", "ANSETZEN LANG; POSTEN BLEIBT AKTIV"),
    ("OK_GRADE_ENDPOINT", "OK", "E", "DY", "OK+E+DY", "ANSETZEN KURZ; SCHLIESSEN"),
    ("OK_GRADE_ENDPOINT", "OK", "EE", "DY", "OK+EE+DY", "ANSETZEN LANG; SCHLIESSEN"),
    ("OK_GRADE_ENDPOINT", "OK", "EEE", "DY", "OK+EEE+DY", "ANSETZEN VOLL; SCHLIESSEN"),
    ("SH_GRADE_ENDPOINT", "SH", "E", "Y", "SH+E+Y", "KURZ HALTEN; POSTEN BLEIBT AKTIV"),
    ("SH_GRADE_ENDPOINT", "SH", "EE", "Y", "SH+EE+Y", "LANG HALTEN; POSTEN BLEIBT AKTIV"),
    ("SH_GRADE_ENDPOINT", "SH", "E", "DY", "SH+E+DY", "KURZ HALTEN; SCHLIESSEN"),
    ("SH_GRADE_ENDPOINT", "SH", "EE", "DY", "SH+EE+DY", "LANG HALTEN; SCHLIESSEN"),
    ("SOLK_GRADE_ENDPOINT", "SOLK", "E", "Y", "SOLK+E+Y", "KURZ AUFFANGEN; POSTEN BLEIBT AKTIV"),
    ("SOLK_GRADE_ENDPOINT", "SOLK", "EE", "Y", "SOLK+EE+Y", "LANG AUFFANGEN; POSTEN BLEIBT AKTIV"),
    ("SOLK_GRADE_ENDPOINT", "SOLK", "EE", "DY", "SOLK+EE+DY", "LANG AUFFANGEN; SCHLIESSEN"),
    ("CHK_GRADE_ENDPOINT", "CHK", "E", "Y", "CHK+E+Y", "KURZ WAERMEN; POSTEN BLEIBT AKTIV"),
    ("CHK_GRADE_ENDPOINT", "CHK", "EE", "Y", "CHK+EE+Y", "LANG WAERMEN; POSTEN BLEIBT AKTIV"),
    ("CHK_GRADE_ENDPOINT", "CHK", "EE", "DY", "CHK+EE+DY", "LANG WAERMEN; SCHLIESSEN"),
    ("OT_GRADE_ENDPOINT", "OT", "EE", "Y", "OT+EE+Y", "DANACH LANG; POSTEN BLEIBT AKTIV"),
    ("OT_GRADE_ENDPOINT", "OT", "E", "DY", "OT+E+DY", "DANACH KURZ; SCHLIESSEN"),
    ("OT_GRADE_ENDPOINT", "OT", "EE", "DY", "OT+EE+DY", "DANACH LANG; SCHLIESSEN"),
    ("OK_QUANTITY", "OK", "AIN", "NONE", "OK+AIN", "EINE PORTION ANSETZEN"),
    ("OK_QUANTITY", "OK", "AIIN", "NONE", "OK+AIIN", "DAS SOLLMASS ANSETZEN"),
]


MISSING = [
    ("OK_GRADE_ENDPOINT", "OK+EEE+Y", "okeeey|qokeeey", "ANSETZEN VOLL; POSTEN BLEIBT AKTIV"),
    ("SH_GRADE_ENDPOINT", "SH+EEE+Y", "sheeey", "VOLL HALTEN; POSTEN BLEIBT AKTIV"),
    ("SH_GRADE_ENDPOINT", "SH+EEE+DY", "sheeedy", "VOLL HALTEN; SCHLIESSEN"),
    ("SOLK_GRADE_ENDPOINT", "SOLK+E+DY", "solkedy", "KURZ AUFFANGEN; SCHLIESSEN"),
    ("CHK_GRADE_ENDPOINT", "CHK+E+DY", "chkedy|chekedy", "KURZ WAERMEN; SCHLIESSEN"),
    ("OT_GRADE_ENDPOINT", "OT+E+Y", "otey|qotey", "DANACH KURZ; POSTEN BLEIBT AKTIV"),
]


def main() -> None:
    HERE.mkdir(parents=True, exist_ok=True)
    cards = read_tsv(CARDS)
    by_parse: dict[str, list[dict[str, str]]] = {}
    surfaces = set()
    for card in cards:
        by_parse.setdefault(card["semantic_component_parse"], []).append(card)
        surfaces.update(card["surfaces"].split("|"))

    cell_rows = []
    exact_rows = []
    for family, core, modifier, endpoint, parse, reading in CELLS:
        members = by_parse.get(parse, [])
        cell_rows.append({
            "family_id": family,
            "core": core,
            "modifier": modifier,
            "endpoint": endpoint,
            "semantic_component_parse": parse,
            "cell_reading_de": reading,
            "exact_card_count": len(members),
            "exact_card_nos": "|".join(card["card_no"] for card in members),
            "surfaces": "|".join(surface for card in members for surface in card["surfaces"].split("|")),
            "occurrences": sum(int(card["occurrences"]) for card in members),
            "records": "|".join(sorted({record for card in members for record in card["records"].split("|")})),
        })
        for card in members:
            exact_rows.append({
                "family_id": family,
                "semantic_component_parse": parse,
                "cell_reading_de": reading,
                "card_no": card["card_no"],
                "surfaces": card["surfaces"],
                "standard_command_de": card["standard_command_de"],
                "occurrences": card["occurrences"],
                "records": card["records"],
                "one_dimension_fit": "YES",
            })

    missing_rows = []
    for family, parse, predicted_surfaces, reading in MISSING:
        candidate_surfaces = predicted_surfaces.split("|")
        hits = [surface for surface in candidate_surfaces if surface in surfaces]
        missing_rows.append({
            "family_id": family,
            "predicted_component_parse": parse,
            "predicted_surface_candidates": predicted_surfaces,
            "predicted_short_reading_de": reading,
            "candidate_surface_hits_in_173_card_deck": "|".join(hits) if hits else "NONE",
            "status": "PREDICTED_GAP_NOT_NEW_CARD",
        })

    write_tsv(HERE / "SIX_HUNDRED_THIRTY_FIFTH_20_ATTESTED_PARADIGM_CELLS.tsv", cell_rows, list(cell_rows[0]))
    write_tsv(HERE / "SIX_HUNDRED_THIRTY_FIFTH_22_EXACT_CARD_MEMBERS.tsv", exact_rows, list(exact_rows[0]))
    write_tsv(HERE / "SIX_HUNDRED_THIRTY_FIFTH_6_PREDICTED_GAPS.tsv", missing_rows, list(missing_rows[0]))

    family_counts = {family: sum(row["family_id"] == family for row in cell_rows) for family in sorted({row["family_id"] for row in cell_rows})}
    md = [
        "# Produktive Substitutionstafel",
        "",
        "Sechs kleine Paradigmen sind sauber genug, um vom Lehrling als Komposition statt als Satzglosse gelernt zu werden.",
        "",
        "| Familie | belegte Zellen | Lehrregel |",
        "|---|---:|---|",
        f"| OK Grad x Endpunkt | {family_counts['OK_GRADE_ENDPOINT']} | kurz/lang/voll ansetzen; Y offen, DY geschlossen |",
        f"| SH Grad x Endpunkt | {family_counts['SH_GRADE_ENDPOINT']} | kurz/lang halten; Y offen, DY geschlossen |",
        f"| SOLK Grad x Endpunkt | {family_counts['SOLK_GRADE_ENDPOINT']} | kurz/lang auffangen; Y offen, DY geschlossen |",
        f"| CHK Grad x Endpunkt | {family_counts['CHK_GRADE_ENDPOINT']} | kurz/lang waermen; Y offen, DY geschlossen |",
        f"| OT Grad x Endpunkt | {family_counts['OT_GRADE_ENDPOINT']} | danach kurz/lang; Y offen, DY geschlossen |",
        f"| OK Menge | {family_counts['OK_QUANTITY']} | Portion AIN gegen Sollmass AIIN |",
        "",
        "Die sechs leeren Rasterzellen werden als Vorhersagen notiert, aber nicht dem Woerterbuch hinzugefuegt. Wenn spaeter eine freigegebene Seite eine davon zeigt, hat das Modell einen echten Vorhersagegewinn; bis dahin bleiben es Luecken.",
    ]
    (HERE / "SIX_HUNDRED_THIRTY_FIFTH_APPRENTICE_PARADIGM_TABLE.md").write_text("\n".join(md).rstrip() + "\n", encoding="utf-8")

    summary = {
        "status": "PASS",
        "paradigm_families": len(family_counts),
        "attested_cells": len(cell_rows),
        "exact_card_members": len(exact_rows),
        "member_occurrences": sum(int(row["occurrences"]) for row in exact_rows),
        "predicted_missing_cells": len(missing_rows),
        "predicted_surface_hits_in_current_deck": sum(row["candidate_surface_hits_in_173_card_deck"] != "NONE" for row in missing_rows),
        "new_words": 0,
        "new_cards": 0,
        "new_surfaces": 0,
        "new_pages": 0,
        "decision": "SIX_SMALL_PRODUCTIVE_PARADIGMS_REPLACE_TWENTY_SENTENCE_GLOSSES",
    }
    (HERE / "SIX_HUNDRED_THIRTY_FIFTH_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
