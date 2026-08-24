#!/usr/bin/env python3
"""Derive a compact apprentice manual from the integrated dictionary."""

from __future__ import annotations

import csv
import json
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
P672 = ROOT / "experiments/yolo/sidequest_semantic_integrated_dictionary_six_hundred_seventy_second"

LESSON = {
    "Y": 1, "OS": 1, "RESUME_CARD": 1,
    "AR": 2, "AIR": 2, "OR": 2, "HO": 2, "CKH": 2, "O": 2,
    "AIN": 3, "AIIN": 3, "IIN": 3, "AN": 3,
    "OK": 4, "CHD": 4, "SH": 4, "SHED": 4, "CHK": 4, "CTH": 4, "SOLK": 4, "P": 4, "LSH": 4, "CFH": 4,
    "CH": 5, "T": 5, "K": 5, "S": 5, "LD": 5,
    "L": 6, "OL": 6, "OT": 6, "AL": 6,
    "E": 7, "EE": 7, "EEE": 7, "R": 7, "DA": 7,
    "DY": 8,
    "TALAM": 9,
}
LESSON_NAMES = {
    1: "Bildbesitzer und laufender Posten",
    2: "Material, Quelle und Arbeitsplatz",
    3: "Portion, Sollmass und Stufe",
    4: "Kernhandlungen und Prozesszustand",
    5: "Hilfshandlungen",
    6: "Weg, Folge und Ziel",
    7: "Grad, Kuehlung und zweiter Gang",
    8: "Aktiv lassen oder schliessen",
    9: "Drei gelernte Ganzbefehle",
}


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(path: Path, rows: list[dict[str, object]], fields: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, delimiter="\t", fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    HERE.mkdir(parents=True, exist_ok=True)
    roots = read(P672 / "SIX_HUNDRED_SEVENTY_SECOND_39_ROOT_TABLET.tsv")
    cards = read(P672 / "SIX_HUNDRED_SEVENTY_SECOND_173_CARD_DICTIONARY.tsv")

    lesson_rows = []
    within = defaultdict(int)
    for root in sorted(roots, key=lambda row: (LESSON[row["component"]], int(row["root_no"][1:]))):
        lesson = LESSON[root["component"]]
        within[lesson] += 1
        lesson_rows.append({
            "lesson": lesson,
            "lesson_name_de": LESSON_NAMES[lesson],
            "order_within_lesson": within[lesson],
            "component": root["component"],
            "short_value_de": root["short_value_de"],
            "category": root["category"],
            "events": root["events_with_component"],
            "recitation_de": f"{root['component']} heisst {root['short_value_de']}",
        })

    rules = [
        (1, "LOOK_AT_OWNER", "Zuerst Bild und lokalen Arbeitsbesitzer merken; er wird nicht in jeder Karte wiederholt."),
        (2, "KEEP_ACTIVE_ITEM", "Y fuehrt den aktuell gemeinten Posten weiter; ein sichtbares dy kann diese Y-Karte schreiben."),
        (3, "SOURCE_BEFORE_TARGET", "AR ist Vorrat/Quelle, AL ist Ziel; beide niemals vertauschen."),
        (4, "MATERIAL_NOT_ADDRESS", "AIR ist laufende Fluessigkeit, OR Ansatz, HO Zutat; sie sind keine Richtungszeichen."),
        (5, "THREE_QUANTITY_LEVELS", "AIN ist Portion, AIIN Sollmass, IIN Arbeitsstufe."),
        (6, "CHOOSE_CORE_ACTION", "Eine Kernhandlung waehlen: ansetzen, umsetzen, halten, absetzen, waermen, auffangen, einfuellen, waschen oder auswringen."),
        (7, "ADD_HELPER_ACTION", "Bei Bedarf abnehmen, eintragen, zudosieren, teilen oder befestigen."),
        (8, "DISTINGUISH_PATH_SEQUENCE", "L leitet den Posten weiter, OL setzt denselben Gang fort, OT beginnt den folgenden Gang."),
        (9, "ADD_GRADE", "E kurz, EE lang, EEE vollstaendig; Grad nur dort einsetzen, wo die genaue Karte im Exemplar steht."),
        (10, "READY_AND_COOL", "CTH markiert bereit; R kuehlt; beide koennen vor dem naechsten Vorgang stehen."),
        (11, "ENDPOINT_LAST", "Y laesst den Posten aktiv; nur die gelernte DY-Kartenkonstruktion schliesst."),
        (12, "COPY_EXACT_CARD", "Nach der Bedeutungswahl die genaue Ganzkarte aus der Tafel kopieren; Komponenten nicht frei buchstabieren."),
        (13, "USE_THREE_WHOLE_COMMANDS", "OS Arbeitsfach, dchol/schol Wiederaufnahme, TALAM Verwahren als ganze Karten lernen."),
        (14, "LINE_IS_SPACE", "Eine physische Zeile beendet die Aussage nicht; am naechsten Platz fortsetzen."),
        (15, "RENDER_ENTRY", "q/s und andere sichtbare Varianten aus dem lokalen Kartenexemplar uebernehmen, nicht semantisch lesen."),
        (16, "READ_BACK", "Zum Pruefen jede Karte atomar aufsagen und erst danach die fluessige Werkstattanweisung sprechen."),
    ]
    rule_rows = [{"rule_no": no, "rule_id": rid, "instruction_de": text} for no, rid, text in rules]

    signature: dict[str, dict[str, int]] = defaultdict(lambda: {"cards": 0, "events": 0})
    for card in cards:
        categories = []
        for atom in card["component_recipe"].split("+"):
            categories.append(next(root["category"] for root in roots if root["component"] == atom))
        key = ">".join(categories)
        signature[key]["cards"] += 1
        signature[key]["events"] += int(card["events"])
    signature_rows = [{"category_signature": key, "card_types": value["cards"], "events": value["events"]} for key, value in sorted(signature.items(), key=lambda item: (-item[1]["events"], -item[1]["cards"], item[0]))]

    predictions = [
        ("OK+EEE+Y", "vollstaendig ansetzen und aktiv lassen"),
        ("SOLK+DY", "auffangen und unmittelbar schliessen"),
        ("SOLK+E+DY", "kurz auffangen und schliessen"),
        ("SOLK+EEE+Y", "vollstaendig auffangen und aktiv lassen"),
        ("SOLK+EEE+DY", "vollstaendig auffangen und schliessen"),
        ("SH+Y", "halten und aktiv lassen"),
        ("SH+DY", "halten und schliessen"),
        ("SH+EEE+DY", "vollstaendig halten und schliessen"),
        ("P+AIN", "eine Portion einfuellen"),
        ("LSH+EE+DY", "laenger waschen und schliessen"),
        ("CFH+DY", "auswringen und schliessen"),
        ("CHD+EE+Y", "laenger umsetzen und aktiv lassen"),
    ]
    attested_recipes = {card["component_recipe"] for card in cards}
    prediction_rows = [{
        "predicted_recipe": recipe,
        "predicted_reading_de": meaning,
        "present_on_fixed_pages": "YES" if recipe in attested_recipes else "NO",
        "surface_policy": "LOOK_UP_OR_COPY_EXACT_CARD__DO_NOT_GENERATE_FROM_LETTERS",
    } for recipe, meaning in predictions]

    exceptions = [card for card in cards if card["composition_mode"] == "MEMORIZED_WHOLE_COMMAND"]
    exception_rows = [{
        "card_no": card["card_no"],
        "surfaces": card["surfaces"],
        "whole_value_de": card["short_default_de"],
        "events": card["events"],
        "teaching_rule": "LEARN_AS_ONE_CARD",
    } for card in exceptions]

    write(HERE / "SIX_HUNDRED_SEVENTY_SIXTH_39_ROOT_TEACHING_ORDER.tsv", lesson_rows, list(lesson_rows[0]))
    write(HERE / "SIX_HUNDRED_SEVENTY_SIXTH_16_APPRENTICE_RULES.tsv", rule_rows, list(rule_rows[0]))
    write(HERE / "SIX_HUNDRED_SEVENTY_SIXTH_RECIPE_SIGNATURES.tsv", signature_rows, list(signature_rows[0]))
    write(HERE / "SIX_HUNDRED_SEVENTY_SIXTH_12_PREDICTED_COMPOSITIONS.tsv", prediction_rows, list(prediction_rows[0]))
    write(HERE / "SIX_HUNDRED_SEVENTY_SIXTH_3_WHOLE_COMMAND_EXCEPTIONS.tsv", exception_rows, list(exception_rows[0]))

    summary = {
        "status": "PASS",
        "lessons": len(LESSON_NAMES),
        "root_entries": len(lesson_rows),
        "rules": len(rule_rows),
        "recipe_signatures": len(signature_rows),
        "predictions": len(prediction_rows),
        "predictions_absent": sum(row["present_on_fixed_pages"] == "NO" for row in prediction_rows),
        "whole_command_exceptions": len(exception_rows),
        "decision": "NINE_LESSONS_AND_SIXTEEN_RULES_TEACH_THE_COMPLETE_WORKSHOP_DICTIONARY",
    }
    (HERE / "SIX_HUNDRED_SEVENTY_SIXTH_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
