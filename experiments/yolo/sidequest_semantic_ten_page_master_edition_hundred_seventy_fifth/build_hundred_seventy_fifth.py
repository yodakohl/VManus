#!/usr/bin/env python3
from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
BASE = ROOT / "experiments/yolo/sidequest_semantic_process_pressure_current_hundred_sixty_fourth"
DICT = BASE / "HUNDRED_SIXTY_FOURTH_173_ATOMIC_DICTIONARY.tsv"
EVENTS = BASE / "HUNDRED_SIXTY_FOURTH_381_ATOMIC_EVENTS.tsv"
R169 = ROOT / "experiments/yolo/sidequest_semantic_f11r_material_class_hundred_sixty_ninth/HUNDRED_SIXTY_NINTH_17_EVENT_F11R_MATERIAL_READING.tsv"
R171 = ROOT / "experiments/yolo/sidequest_semantic_f55v_stock_concentrate_hundred_seventy_first/HUNDRED_SEVENTY_FIRST_18_EVENT_F55V_STOCK_READING.tsv"
R172 = ROOT / "experiments/yolo/sidequest_semantic_four_herbal_jobs_hundred_seventy_second/HUNDRED_SEVENTY_SECOND_65_EVENT_F10R_F56R_READING.tsv"
R173 = ROOT / "experiments/yolo/sidequest_semantic_herbal_to_bio_supply_map_hundred_seventy_third/HUNDRED_SEVENTY_THIRD_97_BIO_CLAUSE_SUPPLY_EDITION.tsv"
R174 = ROOT / "experiments/yolo/sidequest_semantic_astro_workshop_appendix_hundred_seventy_fourth/HUNDRED_SEVENTY_FOURTH_395_GROUP_WORKSHOP_APPENDIX.tsv"


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(path: Path, rows: list[dict[str, object]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


UNIT_READINGS = [
    ("H1", "f10r", "HERBAL", 14, "J1", "Grundteil und Blueten-/Folgeteil im Gefaess zum ersten Grundauszug ansetzen"),
    ("H2", "f10r", "HERBAL", 24, "J1", "mehrere Folgechargen aus demselben Grundauszug auf Sollmass weiterfuehren"),
    ("H3", "f11r", "HERBAL", 17, "J2", "adstringierendes Waschkraut auskochen ausdruecken absetzen nachseihen und als Klarauszug bereitstellen"),
    ("H4", "f55v", "HERBAL", 18, "J3", "Pflanzenansatz in zwei Portionen kuehlen verwahren und spaeter dosiert weiterverwenden"),
    ("H5", "f56r", "HERBAL", 27, "J4", "Wirkzusatz bemessen wiederholt einsetzen und zu den Zielanwendungen weiterfuehren"),
    ("B1", "f81v", "BIO", 66, "J1", "frischen Grundauszug im gemeinsamen Becken bemessen temperieren mischen baden und nachspuelen"),
    ("B2", "f82r", "BIO", 62, "J2", "Klarauszug durch mehrere Teilbad- Wasch- und Randstationen fuehren"),
    ("B3", "f83r", "BIO", 86, "J3", "Vorratsansatz portionsweise in Randgefaesse ueberfuehren waermen mischen und bereitstellen"),
    ("B4", "f83r", "BIO", 47, "J2+J4", "Klarauszug und Wirkzusatz durch Einlage Doppelpass Unterlauf und Zielstation fuehren"),
    ("B5", "f83r", "BIO", 11, "J3", "verwahrte Restmischung abziehen kurz erwaermen und an zweiter Oeffnung mischen"),
    ("B6", "f83r", "BIO", 9, "J4", "fertigen Wirkzusatz ohne Kochen durch Tuch geben bemessen und am Ziel einsetzen"),
    ("A1", "f67r2", "ASTRO", 190, "ELIGIBILITY", "mit zwei getrennten Raedern Herstellung und Anwendung auf passende Bedingungen pruefen"),
    ("A2", "f68r1", "ASTRO", 65, "OBSERVATION", "im mehrpaneeligen Atlas die aktuelle lokale Himmelsadresse finden"),
    ("A3", "f69v", "ASTRO", 140, "EXECUTION", "Arbeitsfall Feuchte/Wetter und Licht/Waerme in drei getrennten Raedern einstellen"),
]


LESSONS = [
    (1, "SEITENKLASSE", "Pflanzenbild Figurenstation oder Himmelsinstrument erkennen", "f11r f82r f68r1 korrekt sortieren"),
    (2, "BILDBESITZER", "kleinsten sichtbaren Besitzer zeigen bevor Text gelesen wird", "f83r lokale Stationen nicht vermischen"),
    (3, "GANZKARTE", "laengste gelernte Karte vor einer Stammzerlegung pruefen", "MC119 Klarauszug als Ganzwert erkennen"),
    (4, "KERNGRAMMATIK", "Menge Quelle Ziel Folge Grad und laufenden Posten einsetzen", "Sollmass Anteil dorthin Folge kurz/lang unterscheiden"),
    (5, "FELD UND SATZ", "Feldschluss von Zeilenende und offenem Satz trennen", "einen Satz ueber die naechste physische Zeile weiterlesen"),
    (6, "HERBAL_JOBS", "Grundauszug Klarauszug Vorrat und Wirkzusatz unterscheiden", "vier Pflanzenbilder dem richtigen Job zuordnen"),
    (7, "BIO_STATIONEN", "bei sichtbarem Stationswechsel Stoff Ziel und Richtung loeschen", "B2 an vier Resetstellen neu beginnen"),
    (8, "LIEFERUNG", "Produkt aus dem passenden Herbalartikel als stillen Stationsstoff einsetzen", "f11r Traeger und f56r Zusatz in B4 kombinieren"),
    (9, "ASTRO_ATLAS", "f68 nur als lokale Beobachtungsadresse verwenden", "keine Reihenfolge aus 28 Sternen erfinden"),
    (10, "ASTRO_PRUEFUNG", "f67-Raeder getrennt fuer Herstellung und Anwendung befragen", "keine 12x12-Matrix bauen"),
    (11, "ASTRO_REGELN", "f69-Raeder getrennt fuer Arbeitsfall Feuchte und Licht verwenden", "keine gemeinsame Kreisrichtung erfinden"),
    (12, "KORREKTUR", "Karte Besitzer Feldschluss und lokalen Namensraum rueckwaerts kontrollieren", "falschen Besitzer streichen und aus Meisterexemplar neu kopieren"),
]


def main() -> None:
    dictionary = read(DICT)
    write(OUT / "HUNDRED_SEVENTY_FIFTH_173_CARD_DICTIONARY.tsv", dictionary)

    h3 = {row["event_serial"]: row["material_expansion_de"] for row in read(R169)}
    h4 = {row["event_serial"]: row["product_expansion_de"] for row in read(R171)}
    others = {row["event_serial"]: row["complete_clause_translation_de"] for row in read(R172)}
    bio_clause = {row["statement_id"]: row for row in read(R173)}
    job_for_record = {unit: job for unit, _, _, _, job, _ in UNIT_READINGS if unit.startswith(("H", "B"))}

    prose_rows = []
    for row in read(EVENTS):
        serial = row["event_serial"]
        record = row["record_unit_id"]
        if record == "H3":
            expansion = h3[serial]
        elif record == "H4":
            expansion = h4[serial]
        elif record in {"H1", "H2", "H5"}:
            expansion = others[serial]
        else:
            expansion = bio_clause[row["statement_id"]]["product_supplied_clause_de"]
        prose_rows.append(
            {
                "event_serial": serial,
                "statement_id": row["statement_id"],
                "record_unit_id": record,
                "page": row["page"],
                "visible_surface": row["visible_surface"],
                "master_card_id": row["master_card_id"],
                "atomic_card_value_de": row["card_value_de"],
                "product_or_job": job_for_record[record],
                "complete_workshop_expansion_de": expansion,
                "visible_owner": row["visible_owner"],
                "terminal_status": row["terminal_status"],
            }
        )
    write(OUT / "HUNDRED_SEVENTY_FIFTH_381_PROSE_MASTER_EDITION.tsv", prose_rows)

    astro_rows = read(R174)
    write(OUT / "HUNDRED_SEVENTY_FIFTH_395_ASTRO_MASTER_EDITION.tsv", astro_rows)

    unified = []
    for index, row in enumerate(prose_rows, 1):
        unified.append(
            {
                "unified_order": index,
                "section": "PROSE",
                "page": row["page"],
                "unit_id": row["record_unit_id"],
                "source_id": f"E{int(row['event_serial']):03d}",
                "visible_surface": row["visible_surface"],
                "atomic_or_local_value_de": row["atomic_card_value_de"],
                "page_job": row["product_or_job"],
                "complete_workshop_expansion_de": row["complete_workshop_expansion_de"],
            }
        )
    astro_unit = {"f67r2": "A1", "f68r1": "A2", "f69v": "A3"}
    astro_page_job = {"f67r2": "ELIGIBILITY", "f68r1": "OBSERVATION", "f69v": "EXECUTION"}
    for offset, row in enumerate(astro_rows, 382):
        unified.append(
            {
                "unified_order": offset,
                "section": "ASTRO",
                "page": row["page"],
                "unit_id": astro_unit[row["page"]],
                "source_id": row["source_group_id"],
                "visible_surface": row["visible_surface"],
                "atomic_or_local_value_de": row["concrete_workshop_value_de"],
                "page_job": astro_page_job[row["page"]],
                "complete_workshop_expansion_de": row["concrete_workshop_value_de"],
            }
        )
    write(OUT / "HUNDRED_SEVENTY_FIFTH_776_UNIFIED_MASTER_LEDGER.tsv", unified)

    units = [
        {
            "unit_id": unit,
            "page": page,
            "section": section,
            "group_count": count,
            "product_or_job": job,
            "complete_unit_reading_de": reading,
        }
        for unit, page, section, count, job, reading in UNIT_READINGS
    ]
    write(OUT / "HUNDRED_SEVENTY_FIFTH_14_UNIT_MASTER_SUMMARY.tsv", units)

    lessons = [
        {
            "lesson": lesson,
            "skill": skill,
            "master_instruction_de": instruction,
            "apprentice_test_de": test,
        }
        for lesson, skill, instruction, test in LESSONS
    ]
    write(OUT / "HUNDRED_SEVENTY_FIFTH_12_LESSON_CURRICULUM.tsv", lessons)

    inputs = [DICT, EVENTS, R169, R171, R172, R173, R174]
    summary = {
        "input_sha256": {path.name: hashlib.sha256(path.read_bytes()).hexdigest() for path in inputs},
        "dictionary_cards": len(dictionary),
        "prose_events": len(prose_rows),
        "astro_groups": len(astro_rows),
        "unified_groups": len(unified),
        "units": len(units),
        "pages": len({row["page"] for row in unified}),
        "lessons": len(lessons),
        "f84_or_f84r_access": False,
    }
    (OUT / "BUILD_SUMMARY.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
