#!/usr/bin/env python3
"""Build Pass 709: terse owner/material/work/grade/target/endpoint dockets."""

from __future__ import annotations

import csv
import json
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
P700 = ROOT / "experiments/yolo/sidequest_semantic_apprentice_manual_seven_hundredth"
P704 = ROOT / "experiments/yolo/sidequest_semantic_statement_phrasebook_seven_hundred_fourth"


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(name: str, rows: list[dict[str, object]]) -> None:
    with (HERE / name).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, delimiter="\t", fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


DOCKETS = [
    ("D01", "PLANT", "BILDTEIL", "MASS", "ANSETZEN", "-", "-", "DIES", "PROC009|PROC008", "Vorgeschriebenes Mass; diesen Pflanzenteil ansetzen."),
    ("D02", "PLANT", "ZUTAT", "-", "ANSATZ BILDEN", "-", "-", "OFFEN", "PROC056|PROC016", "Diese Zutat nehmen; daraus den Ansatz bereithalten."),
    ("D03", "PLANT", "BILDTEIL", "-", "WASCHEN HALTEN", "LANG", "-", "DIES", "PROC084|PROC031", "Waschgang; diesen Pflanzenteil laenger darin halten."),
    ("D04", "PLANT", "BILDTEIL", "-", "AUSWRINGEN ABSETZEN", "-", "-", "SCHLUSS", "PROC028|PROC078", "Diesen Teil auswringen; absetzen und schliessen."),
    ("D05", "BASIN", "ANSATZ", "MASS", "ANSETZEN", "-", "ZIEL", "OFFEN", "PROC009|PROC048", "Vorgeschriebenes Mass; den Ansatz an der Beckenstelle ansetzen."),
    ("D06", "BASIN", "LAUF", "MASS", "WEITERLEITEN UMSETZEN", "-", "-", "OFFEN", "PROC147|PROC150", "Nach Mass weiterleiten; den Lauf umsetzen."),
    ("D07", "BASIN", "STATIONSPOSTEN", "-", "WAERMEN", "KURZ", "-", "SCHLUSS", "PROC083|PROC041", "Diesen Stationsposten kurz waermen; den Gang schliessen."),
    ("D08", "PLANT", "ZUTAT", "PORTION", "ZUDOSIEREN", "-", "-", "DIES", "PROC156|PROC035", "Eine Portion; diese Zutat zudosieren."),
    ("D09", "BASIN", "BADEPOSTEN", "-", "HALTEN", "LANG", "ZIEL", "SCHLUSS", "PROC031|PROC127", "Diesen Badeposten laenger halten; an der Zielstelle schliessen."),
    ("D10", "APPARATUS", "LEITUNGSPOSTEN", "-", "DURCHLASS WEITER", "-", "-", "SCHLUSS", "PROC075|PROC108", "Diesen Posten durch den Durchlass fuehren; weiterleiten und schliessen."),
    ("D11", "PLANT", "ANSATZ", "-", "KUEHLEN", "-", "ZIEL", "DIES", "PROC172", "Diesen Ansatz an der bezeichneten Stelle kuehlen."),
    ("D12", "APPARATUS", "LEITUNGSPOSTEN", "MASS", "WEITERLEITEN", "-", "-", "FORTSETZEN", "PROC009|PROC167", "Vorgeschriebenes Mass; weiterleiten und fortfahren."),
]


OWNER_TEXT = {
    "PLANT": "abgebildete Pflanze/Pflanzenteil",
    "BASIN": "lokale Becken- oder Badestation",
    "APPARATUS": "lokale Leitungs-/Gefaeßstation",
}


def role(card: dict[str, str]) -> str:
    if card["card_class"] == "MEMORIZED_WHOLE_COMMAND":
        return "WHOLE_COMMAND"
    final = card["component_recipe"].split("+")[-1]
    return {
        "DY": "CLOSE_STEP", "Y": "CURRENT_ITEM", "AIN": "QUANTITY_STAGE",
        "AIIN": "QUANTITY_STAGE", "IIN": "QUANTITY_STAGE", "AN": "QUANTITY_STAGE",
        "DA": "QUANTITY_STAGE", "AL": "TARGET", "AR": "SOURCE", "AIR": "FLOW",
        "OR": "PREPARATION", "OL": "CONTINUE", "S": "BOUND_RESULT",
    }.get(final, "OPEN_ACTION")


def main() -> None:
    HERE.mkdir(parents=True, exist_ok=True)
    cards = read(P700 / "SEVEN_HUNDREDTH_173_CARD_MANUAL.tsv")
    events = read(P700 / "SEVEN_HUNDREDTH_381_FORWARD_TRACE.tsv")
    role_pairs = read(P704 / "SEVEN_HUNDRED_FOURTH_55_ROLE_BIGRAMS.tsv")
    card_by_no = {row["card_no"]: row for row in cards}
    cards_by_recipe: dict[str, list[str]] = defaultdict(list)
    for card in cards:
        cards_by_recipe[card["component_recipe"]].append(card["card_no"])
    role_support = {(row["left_role"], row["right_role"]): int(row["token_count"]) for row in role_pairs}
    surface_counts: dict[str, Counter[str]] = defaultdict(Counter)
    for event in events:
        surface_counts[event["card_no"]][event["observed_surface"]] += 1

    rows = []
    for docket_id, owner, material, quantity, operation, grade, target, endpoint, sequence, fluent in DOCKETS:
        selected = [card_by_no[number] for number in sequence.split("|")]
        roles = [role(card) for card in selected]
        surfaces = [max(card["surfaces"].split("|"), key=lambda item: (surface_counts[card["card_no"]][item], -len(item), item)) for card in selected]
        master_card_choice = any(len(cards_by_recipe[card["component_recipe"]]) > 1 for card in selected)
        hand_surface_choice = any(len(card["surfaces"].split("|")) > 1 for card in selected)
        rows.append({
            "docket_id": docket_id, "owner_slot": owner, "material_slot": material,
            "quantity_slot": quantity, "operation_slot": operation, "grade_slot": grade,
            "target_slot": target, "endpoint_slot": endpoint,
            "terse_docket": f"BES:{owner} ST:{material} M:{quantity} W:{operation} G:{grade} ORT:{target} E:{endpoint}",
            "owner_supplied_by_image": "YES", "silent_owner_de": OWNER_TEXT[owner],
            "selected_card_sequence": sequence,
            "component_sequence": " | ".join(card["component_recipe"] for card in selected),
            "role_template": ">".join(roles),
            "role_template_support": role_support[(roles[0], roles[1])] if len(roles) == 2 else "SINGLE_CARD",
            "selected_surface_sequence": " ".join(surfaces),
            "master_selects_exact_card_family": "YES" if master_card_choice else "NO",
            "hand_selects_surface_allograph": "YES" if hand_surface_choice else "NO",
            "literal_backreading_de": " ; ".join(card["compact_atomic_reading_de"] for card in selected),
            "fluent_owner_filled_reading_de": fluent,
            "new_card": "NO", "new_surface": "NO",
        })

    write("SEVEN_HUNDRED_NINTH_12_DOCKET_ENCODINGS.tsv", rows)

    layer_rows = [
        {"layer": "L1_OWNER", "supplied_by": "Bild oder lokale Stationszeichnung", "written_in_card_stream": "NO", "example": "Pflanze; Becken; Leitung"},
        {"layer": "L2_WORK_DOCKET", "supplied_by": "Meister oder Vorlagenrand", "written_in_card_stream": "INDIRECT", "example": "Mass; ansetzen; lang; Ziel; Schluss"},
        {"layer": "L3_CARD_FAMILY", "supplied_by": "Kartenbuch/Lehrgedaechtnis", "written_in_card_stream": "YES", "example": "AIIN | OK+Y"},
        {"layer": "L4_SURFACE", "supplied_by": "Hand und Besitzer-Schublade", "written_in_card_stream": "YES", "example": "daiin qoky"},
        {"layer": "L5_BACKREADING", "supplied_by": "Komponenten plus aktiver Besitzer", "written_in_card_stream": "NO", "example": "vorgeschriebenes Mass; diesen Pflanzenteil ansetzen"},
    ]
    write("SEVEN_HUNDRED_NINTH_5_INFORMATION_LAYERS.tsv", layer_rows)

    readable = ["# Zwoelf knappe Werkstattzettel", ""]
    for row in rows:
        readable.extend([
            f"## {row['docket_id']}", "", f"Zettel: `{row['terse_docket']}`", "",
            f"Abschrift: `{row['selected_surface_sequence']}`", "",
            f"Ruecklesung: {row['fluent_owner_filled_reading_de']}", "",
        ])
    (HERE / "SEVEN_HUNDRED_NINTH_12_READABLE_DOCKETS.md").write_text("\n".join(readable), encoding="utf-8")

    summary = {
        "status": "PASS", "dockets": len(rows), "information_layers": len(layer_rows),
        "owners": dict(Counter(row["owner_slot"] for row in rows)),
        "owner_silent": sum(row["owner_supplied_by_image"] == "YES" for row in rows),
        "attested_role_templates": sum(row["role_template_support"] == "SINGLE_CARD" or int(row["role_template_support"]) >= 1 for row in rows),
        "master_card_choice_needed": sum(row["master_selects_exact_card_family"] == "YES" for row in rows),
        "hand_allograph_choice_needed": sum(row["hand_selects_surface_allograph"] == "YES" for row in rows),
        "new_cards": 0, "new_surfaces": 0,
        "decision": "TERSE_OWNER_WORK_DOCKETS_EXPAND_TO_EXISTING_CARDS_SURFACES_AND_FLUENT_BACKREADINGS",
    }
    (HERE / "SEVEN_HUNDRED_NINTH_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
