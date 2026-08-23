#!/usr/bin/env python3
from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
EVENTS = ROOT / "experiments/yolo/sidequest_semantic_process_pressure_current_hundred_sixty_fourth/HUNDRED_SIXTY_FOURTH_381_ATOMIC_EVENTS.tsv"


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(path: Path, rows: list[dict[str, object]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    candidates = [
        ("STORED_TWO_PART_PLANT_STOCK", "aufbewahrter zweipartiger Pflanzen-Grundansatz", 2, 2, 2, 2, 2, 10, "SELECTED", "Quellauszug teilen abkuehlen verwahren und portionsweise in Folgezubereitungen geben"),
        ("MEDICINAL_OINTMENT_OR_POULTICE_BASE", "verwahrte Salben- oder Auflagengrundlage", 2, 2, 2, 1, 1, 8, "STRONG_RIVAL", "zwei Anteile zu einer haltbaren Auflagengrundlage verarbeiten"),
        ("DYE_OR_TANNING_STOCK", "pflanzlicher Faerbe- oder Gerbgrundansatz", 2, 2, 1, 2, 0, 7, "LIVE_RIVAL", "Pflanzenextrakt portionieren lagern und spaeter in ein Arbeitsbad einsetzen"),
        ("CORDIAL_OR_SYRUP_STOCK", "aufbewahrter Trank- oder Sirupgrundansatz", 1, 2, 2, 2, 0, 7, "LIVE_RIVAL", "konzentrierten Pflanzenauszug in zwei Anteilen lagern und dosieren"),
    ]
    candidate_rows = [
        {
            "candidate_id": cid,
            "product_class_de": name,
            "two_portion_fit_0_2": portion,
            "cooling_fit_0_2": cool,
            "storage_fit_0_2": store,
            "later_dose_fit_0_2": dose,
            "ten_page_purpose_fit_0_2": purpose,
            "total_0_10": total,
            "selection": selection,
            "continuous_function_de": function,
        }
        for cid, name, portion, cool, store, dose, purpose, total, selection, function in candidates
    ]
    write(OUT / "HUNDRED_SEVENTY_FIRST_4_PRODUCT_CLASSES.tsv", candidate_rows)

    clues = [
        ("P1", "FIRST_AND_SECOND_PORTION", "erste Portion plus zweite Portion", "Produkt wird absichtlich geteilt oder zusammengesetzt"),
        ("P2", "COOLING", "Abkuehlen schliesst ersten Schritt", "vorheriger Ansatz war warm verarbeitet"),
        ("P3", "STORAGE", "Sollmass wird zum Verwahrort ueberfuehrt", "Produkt ist haltbarer Vorrat nicht sofortiger Waschlauf"),
        ("P4", "SOURCE_EXTRACT", "Sollportion wird aus Quellauszug genommen", "bereits bereiteter Pflanzenextrakt ist Ausgangsmaterial"),
        ("P5", "LATER_PREPARATION", "Bereitungsanteil wird dorthin in Folgezubereitung eingesetzt", "Vorrat dient als dosierter Zusatz fuer einen spaeteren Arbeitsgang"),
    ]
    clue_rows = [{"clue_id": a, "clue": b, "fixed_card_chain_de": c, "product_consequence_de": d} for a, b, c, d in clues]
    write(OUT / "HUNDRED_SEVENTY_FIRST_5_PRODUCT_CLUES.tsv", clue_rows)

    expansions = {
        56: "Bemiss den warm bereiteten Pflanzen-Grundansatz.",
        57: "Bringe die Gesamtmenge auf das Sollmass.",
        58: "Teile die erste Vorratsportion ab.",
        59: "Teile die zweite Vorratsportion ab.",
        60: "Lass beide Portionen abkuehlen und schliesse den Schritt.",
        61: "Pruefe die verwahrte Menge nochmals gegen das Sollmass.",
        62: "Fuehre die Portion in das Vorratsgefaess ueber.",
        63: "Stelle sie am vorgesehenen Verwahrort ab.",
        64: "Nimm spaeter die vorgeschriebene Vorratsportion.",
        65: "Schoepfe sie aus dem vorhandenen Quellauszug.",
        66: "Arbeite die entnommene Portion laenger durch.",
        67: "Markiere diese Dosis als fertig.",
        68: "Bemiss die Dosis fuer den Folgeansatz.",
        69: "Setze sie an der vorgesehenen Stelle ein.",
        70: "Beginne damit die Folgezubereitung.",
        71: "Fuehre sie als neuen Ansatz.",
        72: "Halte diesen Ansatz als laufenden Posten.",
        73: "Fuege den bereitgestellten Anteil der Zubereitung zu.",
    }
    h4 = [row for row in read(EVENTS) if row["record_unit_id"] == "H4"]
    event_rows = []
    for row in h4:
        serial = int(row["event_serial"])
        event_rows.append(
            {
                "event_serial": serial,
                "statement_id": row["statement_id"],
                "page": row["page"],
                "visible_surface": row["visible_surface"],
                "master_card_id": row["master_card_id"],
                "unchanged_card_value_de": row["card_value_de"],
                "selected_product_class": "STORED_TWO_PART_PLANT_STOCK",
                "product_expansion_de": expansions[serial],
                "dictionary_change": "NO",
            }
        )
    write(OUT / "HUNDRED_SEVENTY_FIRST_18_EVENT_F55V_STOCK_READING.tsv", event_rows)

    sources = [
        {
            "source_id": "S1",
            "source": "Medieval Welsh Medical Texts",
            "url": "https://www.ncbi.nlm.nih.gov/books/NBK558248/",
            "analogy_de": "gekochte Mischungen werden durch Leinen gepresst oder geseiht und zum Aufbewahren in Gefaesse gegeben",
            "use": "STORAGE_AND_PORTION_MECHANISM",
        },
        {
            "source_id": "S2",
            "source": "On Wounds; 14th-15th-century Irish manuscript witnesses",
            "url": "https://celt.ucc.ie/document/T600012/",
            "analogy_de": "Pflanzensaefte und gekochte Mischungen werden als Vorrat bereitet und portionsweise aeusserlich gebraucht",
            "use": "MEDICINAL_STOCK_RIVAL_SUPPORT",
        },
        {
            "source_id": "S3",
            "source": "UPenn LJS 419 illustrated herbal",
            "url": "https://openn.library.upenn.edu/Data/0001/html/ljs419.html",
            "analogy_de": "bebilderte Pflanzenartikel koennen Eigenschaften und Zubereitungen im selben Artikel verbinden",
            "use": "ILLUSTRATED_ARTICLE_ARCHITECTURE",
        },
    ]
    write(OUT / "HUNDRED_SEVENTY_FIRST_HISTORICAL_COMPARATORS.tsv", sources)

    summary = {
        "source_events_sha256": hashlib.sha256(EVENTS.read_bytes()).hexdigest(),
        "candidate_product_classes": 4,
        "selected_product_class": "STORED_TWO_PART_PLANT_STOCK",
        "product_clues": 5,
        "f55v_events": len(event_rows),
        "dictionary_changes": 0,
        "distinct_from_f11r_clear_wash": True,
        "f84_or_f84r_access": False,
    }
    (OUT / "BUILD_SUMMARY.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
