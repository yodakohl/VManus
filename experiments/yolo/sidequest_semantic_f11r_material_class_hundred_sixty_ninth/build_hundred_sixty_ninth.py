#!/usr/bin/env python3
from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
EVENTS = ROOT / "experiments/yolo/sidequest_semantic_process_pressure_current_hundred_sixty_fourth/HUNDRED_SIXTY_FOURTH_381_ATOMIC_EVENTS.tsv"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_tsv(path: Path, fieldnames: list[str], rows: list[dict[str, object]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    candidates = [
        {
            "candidate_id": "BLUE_FLOWERING_ASTRINGENT_WASH_HERB",
            "material_class_de": "blau bluehendes adstringierendes Wasch- und Wundkraut",
            "image_fit_0_2": 2,
            "decoct_press_fit_0_2": 2,
            "stand_refilter_fit_0_2": 2,
            "clear_product_fit_0_2": 2,
            "external_station_use_fit_0_2": 2,
            "historical_recipe_fit_0_2": 2,
            "total_0_12": 12,
            "selection": "SELECTED_WORKING_CLASS",
            "concrete_reading_de": "adstringierenden Pflanzenwaschauszug bereiten und an den Zielstellen anwenden",
            "strongest_problem_de": "keine bestimmte Art und keine Wunde sind im Manuskripttext unabhaengig sichtbar",
        },
        {
            "candidate_id": "COOLING_FLOWERING_WASH_HERB",
            "material_class_de": "kuehlendes bluehendes Bad- und Waschkraut",
            "image_fit_0_2": 2,
            "decoct_press_fit_0_2": 1,
            "stand_refilter_fit_0_2": 1,
            "clear_product_fit_0_2": 2,
            "external_station_use_fit_0_2": 2,
            "historical_recipe_fit_0_2": 2,
            "total_0_12": 10,
            "selection": "STRONG_RIVAL",
            "concrete_reading_de": "kuehlendes Bluetenwasser bereiten und zum Waschen oder Baden gebrauchen",
            "strongest_problem_de": "die enge Veilchenanalogie passt nicht sicher zur gezeichneten Gesamtpflanze",
        },
        {
            "candidate_id": "MUCILAGINOUS_SOOTHING_BATH_HERB",
            "material_class_de": "schleimiges beruhigendes Bad- und Auflagekraut",
            "image_fit_0_2": 1,
            "decoct_press_fit_0_2": 2,
            "stand_refilter_fit_0_2": 1,
            "clear_product_fit_0_2": 0,
            "external_station_use_fit_0_2": 2,
            "historical_recipe_fit_0_2": 2,
            "total_0_12": 8,
            "selection": "LIVE_RIVAL",
            "concrete_reading_de": "schleimiges Kraut auskochen ausdruecken und als Bad oder Auflage anwenden",
            "strongest_problem_de": "wiederholtes Klaeren passt schlecht zu einem gewollt schleimigen Produkt",
        },
        {
            "candidate_id": "AROMATIC_FLOWERING_RINSE_HERB",
            "material_class_de": "aromatisches bluehendes Spuelkraut",
            "image_fit_0_2": 2,
            "decoct_press_fit_0_2": 1,
            "stand_refilter_fit_0_2": 1,
            "clear_product_fit_0_2": 2,
            "external_station_use_fit_0_2": 1,
            "historical_recipe_fit_0_2": 1,
            "total_0_12": 8,
            "selection": "LIVE_RIVAL",
            "concrete_reading_de": "aromatischen Spuelauszug aus dem bluehenden Kraut bereiten",
            "strongest_problem_de": "Geruch und aromatische Wirkung sind bildlich nicht beobachtbar",
        },
    ]
    write_tsv(
        OUT / "HUNDRED_SIXTY_NINTH_4_MATERIAL_CLASSES.tsv",
        list(candidates[0]),
        candidates,
    )

    requirements = [
        ("R1", "PICTURED_OWNER", "dichte bluehende Gesamtpflanze", "eine bluehende Krautklasse statt eines unsichtbaren Minerals"),
        ("R2", "DECOCT", "Kochgut und Sudansatz", "wasser- oder weinbasierter Pflanzenauszug"),
        ("R3", "EXPRESS", "Auswringen", "ausgekochtes Pflanzenmaterial wird ausgepresst"),
        ("R4", "SETTLE", "vorgeschriebene Stehzeit", "Trub darf sich absetzen"),
        ("R5", "REFILTER", "Nachseihen", "Auszug wird nach dem Stehen erneut geklaert"),
        ("R6", "CLEAR_PRODUCT", "exakte Karte Klarauszug", "portables klares Zwischenprodukt"),
        ("R7", "TARGET_USE", "B4 bemisst fuehrt und verteilt denselben Klarauszug", "aeussere Wasch- oder Wundanwendung ist einfacher als Trinkgebrauch"),
    ]
    requirement_rows = [
        {
            "requirement_id": rid,
            "process_requirement": name,
            "fixed_page_clue_de": clue,
            "material_consequence_de": consequence,
        }
        for rid, name, clue, consequence in requirements
    ]
    write_tsv(
        OUT / "HUNDRED_SIXTY_NINTH_7_PROCESS_REQUIREMENTS.tsv",
        list(requirement_rows[0]),
        requirement_rows,
    )

    expansions = {
        39: "Nimm das bestimmte Kochgut vom blau bluehenden Waschkraut.",
        40: "Setze daraus den Pflanzenwaschauszug an.",
        41: "Wringe das ausgekochte Kraut aus.",
        42: "Lass die ausgedrueckte Fluessigkeit die vorgeschriebene Zeit stehen.",
        43: "Seihe die abgesetzte Fluessigkeit nochmals.",
        44: "Behalte den klaren Waschauszug.",
        45: "Gib den vorgesehenen Endzusatz bei und schliesse den Zubereitungsschritt.",
        46: "Lege den weiteren Zugabeteil bereit.",
        47: "Nimm vom vorigen klaren Ansatz.",
        48: "Halte diesen Ansatz als laufenden Posten.",
        49: "Bearbeite diesen Anteil weiter.",
        50: "Fuehre denselben Posten fort.",
        51: "Bringe ihn auf das Sollmass.",
        52: "Wechsle zum Folgeposten.",
        53: "Verarbeite den Folgeposten weiter.",
        54: "Halte die Zubereitung bereit.",
        55: "Dies ist der bereitgestellte Auszug fuer die Stationsarbeit.",
    }
    with EVENTS.open(encoding="utf-8", newline="") as handle:
        source_rows = list(csv.DictReader(handle, delimiter="\t"))
    h3_rows = [row for row in source_rows if row["record_unit_id"] == "H3"]
    event_rows = []
    for row in h3_rows:
        serial = int(row["event_serial"])
        event_rows.append(
            {
                "event_serial": serial,
                "statement_id": row["statement_id"],
                "page": row["page"],
                "visible_surface": row["visible_surface"],
                "master_card_id": row["master_card_id"],
                "unchanged_card_value_de": row["card_value_de"],
                "selected_owner_class": "BLUE_FLOWERING_ASTRINGENT_WASH_HERB",
                "material_expansion_de": expansions[serial],
                "dictionary_change": "NO",
            }
        )
    write_tsv(
        OUT / "HUNDRED_SIXTY_NINTH_17_EVENT_F11R_MATERIAL_READING.tsv",
        list(event_rows[0]),
        event_rows,
    )

    sources = [
        {
            "source_id": "S1",
            "historical_witness": "Medieval Welsh Medical Texts recipe collection",
            "date_or_scope": "late-medieval recipe tradition; modern open edition",
            "url": "https://www.ncbi.nlm.nih.gov/books/NBK558248/",
            "mechanism_used_de": "Pflanzen werden gekocht gepresst durch Leinen geseiht aufbewahrt und auf Wunden oder Waschungen angewandt",
            "bounded_use": "PROCESS_ANALOGY_NOT_PLANT_IDENTIFICATION",
        },
        {
            "source_id": "S2",
            "historical_witness": "On Wounds; Irish medical tract witnesses including 1352 and 1436",
            "date_or_scope": "14th-15th century manuscript witnesses",
            "url": "https://celt.ucc.ie/document/T600012/",
            "mechanism_used_de": "Malve und Wermut werden in Wein gekocht; Pflanzenpresssaefte reinigen und waschen Geschwuere",
            "bounded_use": "WOUND_WASH_CLASS_ANALOGY_NOT_EXACT_RECIPE",
        },
        {
            "source_id": "S3",
            "historical_witness": "Macer Floridus violet remedies in a 15th-century Italian manuscript tradition",
            "date_or_scope": "15th century Italian manuscript comparator",
            "url": "https://histmed.collegeofphysicians.org/medieval-monday-13/",
            "mechanism_used_de": "in Pflanzenwasser waschen oder baden und bluehende Kraeuter aeusserlich gegen Schwellungen verwenden",
            "bounded_use": "COOLING_FLOWERING_RIVAL_ONLY_NOT_VIOLET_IDENTIFICATION",
        },
    ]
    write_tsv(
        OUT / "HUNDRED_SIXTY_NINTH_HISTORICAL_SOURCES.tsv",
        list(sources[0]),
        sources,
    )

    summary = {
        "source_events_sha256": sha256(EVENTS),
        "candidate_classes": len(candidates),
        "selected_class": "BLUE_FLOWERING_ASTRINGENT_WASH_HERB",
        "process_requirements": len(requirement_rows),
        "f11r_events": len(event_rows),
        "dictionary_changes": 0,
        "exact_species_claim": False,
        "f84_or_f84r_access": False,
    }
    (OUT / "BUILD_SUMMARY.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
