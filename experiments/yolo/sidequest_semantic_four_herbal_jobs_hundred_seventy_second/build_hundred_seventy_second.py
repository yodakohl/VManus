#!/usr/bin/env python3
from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
EVENTS = ROOT / "experiments/yolo/sidequest_semantic_process_pressure_current_hundred_sixty_fourth/HUNDRED_SIXTY_FOURTH_381_ATOMIC_EVENTS.tsv"
CLAUSES = ROOT / "experiments/yolo/sidequest_semantic_process_pressure_current_hundred_sixty_fourth/HUNDRED_SIXTY_FOURTH_116_ATOMIC_CLAUSES.tsv"


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(path: Path, rows: list[dict[str, object]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


JOBS = [
    ("J1", "f10r", "H1|H2", 38, "MULTI_BATCH_ROOT_AND_FLOWER_MOTHER_EXTRACT", "mehrteiliger Grundauszug aus Grundteil und Blueten-/Folgeteil", "Grundteil; Aufnahmegefaess; Zuguss; Folgeteil; wiederholter Ansatz; Sollmass", "liefert einen frischen Grundansatz in mehreren Chargen"),
    ("J2", "f11r", "H3", 17, "CLARIFIED_ASTRINGENT_WASH", "geklaerter adstringierender Waschauszug", "Auskochen; Auswringen; Stehzeit; Nachseihen; Klarauszug", "liefert die klare aeussere Waschcharge"),
    ("J3", "f55v", "H4", 18, "STORED_TWO_PART_PLANT_STOCK", "gekuehlter zweipartiger Pflanzen-Vorratsansatz", "erste und zweite Portion; Abkuehlen; Verwahrort; spaetere Sollportion", "liefert dosierbaren Vorrat fuer Folgezubereitungen"),
    ("J4", "f56r", "H5", 27, "REPEATED_TARGET_APPLICATION_ADDITIVE", "Wirkzusatz fuer wiederholte Zielanwendung", "weitere Zutat; Zielzugabe; einsetzen; Langpassage; erneut einsetzen; Folgeanwendung", "liefert wiederholte kleine Wirkzugaben an bezeichnete Stellen"),
]


CLAUSE_READINGS = {
    "H1-S001": "Nimm den Grundteil der Bildpflanze, bereite einen Anteil im Gefaess vor, giesse Arbeitsfluessigkeit zu und setze den Blueten- oder Folgeteil bis zum Sollmass ein.",
    "H1-S002": "Bearbeite diese erste Charge weiter und halte den fertigen Grundauszug bereit.",
    "H2-S001": "Setze aus dem Grundauszug die naechste Charge an und bringe sie auf das vorgeschriebene Mass.",
    "H2-S002": "Fuehre denselben Ansatz weiter, entnimm davon eine Sollmenge und behalte die Chargenfolge bei.",
    "H2-S003": "Fuehre den Arbeitsansatz durch die naechste Stufe und gib die vorgeschriebene Menge zu.",
    "H5-S001": "Setze den Wirkzusatz an, gib die bestimmte Pflanzensubstanz bis zum Sollmass in die Zielzubereitung und bringe den Folgeansatz an die bezeichnete Stelle.",
    "H5-S002": "Nimm vom vorigen Ansatz einen Anwendungsposten, setze ihn ein und lasse ihn laenger an der Zielstelle einwirken.",
    "H5-S003": "Halte die Stelle, gib weiteren Wirkzusatz bei, bearbeite kurz und setze die Anwendung erneut an.",
    "H5-S004": "Bearbeite die Anwendung weiter, setze den Auszug ein und verteile ihn an der Zielstelle.",
    "H5-S005": "Gib nochmals Wirkzusatz aus dem Quellauszug bei und fuehre die Folgeanwendung aus.",
    "H5-S006": "Wechsle zur naechsten Zielstelle, fuehre den kurzen Arbeitsgang fort und bemiss die neue Portion.",
}


def main() -> None:
    job_rows = [
        {
            "job_id": jid,
            "page": page,
            "record_units": records,
            "event_count": count,
            "selected_job": job,
            "concrete_product_de": product,
            "decisive_chain_de": chain,
            "workshop_role_de": role,
        }
        for jid, page, records, count, job, product, chain, role in JOBS
    ]
    write(OUT / "HUNDRED_SEVENTY_SECOND_4_HERBAL_JOBS.tsv", job_rows)

    clause_source = {row["statement_id"]: row for row in read(CLAUSES)}
    clause_rows = []
    for statement_id, translation in CLAUSE_READINGS.items():
        row = clause_source[statement_id]
        record = row["record_unit_id"]
        job = "MULTI_BATCH_ROOT_AND_FLOWER_MOTHER_EXTRACT" if record in {"H1", "H2"} else "REPEATED_TARGET_APPLICATION_ADDITIVE"
        clause_rows.append(
            {
                "statement_id": statement_id,
                "record_unit_id": record,
                "page": row["page"],
                "selected_job": job,
                "unchanged_atomic_chain_de": row["atomic_card_chain_de"],
                "complete_job_translation_de": translation,
                "terminal_status": row["terminal_status"],
            }
        )
    write(OUT / "HUNDRED_SEVENTY_SECOND_11_NEW_JOB_CLAUSES.tsv", clause_rows)

    event_source = read(EVENTS)
    selected = [row for row in event_source if row["record_unit_id"] in {"H1", "H2", "H5"}]
    clause_map = {row["statement_id"]: row for row in clause_rows}
    event_rows = []
    for row in selected:
        clause = clause_map[row["statement_id"]]
        event_rows.append(
            {
                "event_serial": row["event_serial"],
                "statement_id": row["statement_id"],
                "record_unit_id": row["record_unit_id"],
                "page": row["page"],
                "visible_surface": row["visible_surface"],
                "master_card_id": row["master_card_id"],
                "unchanged_card_value_de": row["card_value_de"],
                "selected_job": clause["selected_job"],
                "complete_clause_translation_de": clause["complete_job_translation_de"],
                "dictionary_change": "NO",
            }
        )
    write(OUT / "HUNDRED_SEVENTY_SECOND_65_EVENT_F10R_F56R_READING.tsv", event_rows)

    source_rows = [
        {
            "source_id": "S1",
            "source": "Tadhg O Cuinn Book of Simple Medicines; completed 1415",
            "url": "https://celt.ucc.ie/document/G600005/",
            "architecture_de": "Pflanzenartikel koennen Name Eigenschaften Teile Zubereitung und mehrere Gebraeuche seriell fuehren",
        },
        {
            "source_id": "S2",
            "source": "UPenn LJS 419; fifteenth-century north-Italian illustrated herbal",
            "url": "https://openn.library.upenn.edu/Data/0001/html/ljs419.html",
            "architecture_de": "ganzseitiges Pflanzenbild und darum gefuehrter Text bilden einen Bildbesitzer mit mehreren Verwendungsabschnitten",
        },
        {
            "source_id": "S3",
            "source": "Medieval Welsh Medical Texts",
            "url": "https://www.ncbi.nlm.nih.gov/books/NBK558248/",
            "architecture_de": "Rezepte trennen Grundstoff Portion Gefaess Zuguss Aufbewahrung und wiederholte aeussere Anwendung",
        },
    ]
    write(OUT / "HUNDRED_SEVENTY_SECOND_HISTORICAL_ARTICLE_ARCHITECTURES.tsv", source_rows)

    summary = {
        "source_events_sha256": hashlib.sha256(EVENTS.read_bytes()).hexdigest(),
        "source_clauses_sha256": hashlib.sha256(CLAUSES.read_bytes()).hexdigest(),
        "herbal_jobs": 4,
        "all_herbal_events": sum(row[3] for row in JOBS),
        "newly_expanded_events": len(event_rows),
        "newly_expanded_clauses": len(clause_rows),
        "dictionary_changes": 0,
        "jobs_distinct": len({row[4] for row in JOBS}) == 4,
        "f84_or_f84r_access": False,
    }
    (OUT / "BUILD_SUMMARY.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
