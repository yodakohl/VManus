#!/usr/bin/env python3
"""Choose one concrete bath-and-service vocabulary for the six Biological records."""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
UNITS = ROOT / "experiments/yolo/sidequest_semantic_refined_controlled_rewrite_eighty_second_edition/EIGHTY_SECOND_14_REFINED_CONTROLLED_UNITS.tsv"
BINDING = ROOT / "experiments/yolo/sidequest_semantic_refined_controlled_rewrite_eighty_second_edition/EIGHTY_SECOND_776_REFINED_BINDING.tsv"


MODELS = {
    "M1_THERAPEUTIC_BATH_WITH_SERVICE_ANNEX": {
        "FIGURE": "Badende", "BASIN": "Becken", "LIQUID": "Badwasser",
        "ADDITIVE": "Kräuterzusatz", "HEAT": "Badwärme", "DURATION": "Badezeit",
        "TARGET": "Körperstelle", "IMMERSION": "Teilbad", "CLOTH": "Tuch",
        "PASSAGE": "Seihgang", "SERVICE": "Dienststation",
    },
    "M2_PUBLIC_BATHHOUSE_AND_LAUNDRY": {
        "FIGURE": "Badegast", "BASIN": "Bottich", "LIQUID": "Waschwasser",
        "ADDITIVE": "Waschzusatz", "HEAT": "Wärme", "DURATION": "Arbeitszeit",
        "TARGET": "Waschstelle", "IMMERSION": "Tauchgang", "CLOTH": "Tuch",
        "PASSAGE": "Seihgang", "SERVICE": "Dienststation",
    },
    "M3_CLOSED_PROCESS_APPARATUS": {
        "FIGURE": "Werkstück", "BASIN": "Behälter", "LIQUID": "Arbeitsflüssigkeit",
        "ADDITIVE": "Zusatz", "HEAT": "Temperatur", "DURATION": "Dauer",
        "TARGET": "Arbeitsstelle", "IMMERSION": "Tauchgang", "CLOTH": "Filtertuch",
        "PASSAGE": "Filtergang", "SERVICE": "Prozessstation",
    },
}

FIT = {
    "M1_THERAPEUTIC_BATH_WITH_SERVICE_ANNEX": {"B1": (5, 5, 5, 5), "B2": (5, 5, 5, 5), "B3": (5, 4, 5, 4), "B4": (5, 5, 5, 5), "B5": (5, 5, 4, 4), "B6": (5, 5, 4, 4)},
    "M2_PUBLIC_BATHHOUSE_AND_LAUNDRY": {"B1": (5, 5, 4, 4), "B2": (5, 5, 4, 4), "B3": (5, 5, 4, 4), "B4": (5, 5, 4, 4), "B5": (5, 5, 5, 5), "B6": (5, 5, 5, 5)},
    "M3_CLOSED_PROCESS_APPARATUS": {"B1": (3, 4, 3, 2), "B2": (3, 4, 3, 3), "B3": (4, 5, 4, 3), "B4": (4, 5, 4, 4), "B5": (5, 5, 5, 5), "B6": (5, 5, 5, 5)},
}

SELECTED_WORDS = [
    ("BATHER", "Badende", "sichtbarer Mensch im Becken"),
    ("BASIN", "Becken", "sichtbare lokale Bad-/Arbeitsmulde"),
    ("BATH_WATER", "Badwasser", "Flüssigkeit an Figurenstationen"),
    ("HERBAL_ADDITIVE", "Kräuterzusatz", "Zusatz aus dem Pflanzenregister"),
    ("BATH_HEAT", "Badwärme", "Temperatur an Figurenstationen"),
    ("BATH_TIME", "Badezeit", "Dauer an Figurenstationen"),
    ("BODY_TARGET", "Körperstelle", "örtliches Ziel bei sichtbarer Figur"),
    ("PART_BATH", "Teilbad", "lokale Immersion im Einzelbecken"),
    ("CLOTH", "Tuch", "Wasch-, Umschlag- oder Seihträger"),
    ("COMPRESS", "Umschlag", "gehaltenes Tuch an B4"),
    ("STRAINING_PASS", "Seihgang", "Tuch-/Durchlassoperation"),
    ("INLET", "Einlass", "sichtbare oder lokale Zufuhr"),
    ("OUTLET", "Ablauf", "sichtbarer oder lokaler Abzug"),
    ("WATER_RUN", "Wasserlauf", "lokale Verbindung ohne globalen Kreislauf"),
    ("RECEIVER", "Auffangbecken", "örtlicher Empfänger"),
    ("SERVICE_STATION", "Dienststation", "figurenlose B5/B6-Hilfsstation"),
    ("SERVICE_TARGET", "Arbeitsstelle", "örtliches Ziel ohne Figur"),
]

RECORDS = {
    "B1": "Im gemeinsamen zweireihigen Becken Badwasser mit Kräuterzusatz auf Badwärme bringen. Die Badenden für die Badezeit an der bezeichneten Körperstelle waschen oder im Teilbad halten; danach durch den Seihgang zum Ablauf führen.",
    "B2": "Die fünf sichtbaren Beckenstationen einzeln neu einrichten. Badwasser am Einlass in den örtlichen Wasserlauf geben, Kräuterzusatz und Badwärme einstellen, die Badenden für die Badezeit im Teilbad halten und jede Station getrennt zum Ablauf oder Seihgang führen.",
    "B3": "Die drei Randbecken zuerst einzeln mit Badwasser füllen, waschen, absetzen und ins Auffangbecken abführen. Danach das sichtbar gekoppelte Hauptpaar mit Badwärme, Tuch, Seihgang und örtlichem Ablauf bedienen; die unverbundene Lücke nicht als Wasserlauf lesen.",
    "B4": "Am gekoppelten Hauptpaar ein Tuch in warmes Badwasser tauchen und als Umschlag an der bezeichneten Körperstelle halten. Danach linke und rechte Dienststation getrennt mit Einlass, Wasserlauf, Seihgang, Auffangbecken und Ablauf bedienen.",
    "B5": "An der linken Dienststation Badwasser oder Arbeitswasser auf Wärme bringen, für die örtliche Dauer halten und am Ablauf abführen. Das Ziel bleibt eine Arbeitsstelle, weil keine Figur sie besitzt.",
    "B6": "An der rechten Dienststation Wasser am Einlass in den örtlichen Lauf geben, durch Tuch und Seihgang führen und an der Arbeitsstelle verwenden. Auch hier bleibt der Zweck technisch, solange keine Figur hinzutritt.",
}


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: list[dict[str, object]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    model_rows = []
    for model_id, vocabulary in MODELS.items():
        for slot, value in vocabulary.items():
            model_rows.append({"model_id": model_id, "content_slot": slot, "concrete_value_de": value})
    write_tsv(OUT / "EIGHTY_FOURTH_33_MODEL_VOCABULARY_ROWS.tsv", model_rows)

    comparisons = []
    totals = {model: 0 for model in MODELS}
    for model_id in MODELS:
        for unit_id in ("B1", "B2", "B3", "B4", "B5", "B6"):
            figure, geometry, process, whole_book = FIT[model_id][unit_id]
            total = figure + geometry + process + whole_book
            totals[model_id] += total
            comparisons.append({
                "model_id": model_id,
                "unit_id": unit_id,
                "figure_fit_1_to_5": figure,
                "station_geometry_fit_1_to_5": geometry,
                "process_vocabulary_fit_1_to_5": process,
                "whole_book_fit_1_to_5": whole_book,
                "editorial_fit_total_20": total,
            })
    write_tsv(OUT / "EIGHTY_FOURTH_18_MODEL_RECORD_COMPARISONS.tsv", comparisons)

    words = [
        {"bath_word_id": f"B{index:02d}", "bath_service_slot": slot, "selected_word_de": value, "owner_rule_de": rule, "card_or_root_meaning": "NO__SOURCE_PROGRAM_WORD"}
        for index, (slot, value, rule) in enumerate(SELECTED_WORDS, 1)
    ]
    write_tsv(OUT / "EIGHTY_FOURTH_17_SELECTED_BATH_SERVICE_WORDS.tsv", words)

    source_units = {row["unit_id"]: row for row in read_tsv(UNITS) if row["unit_id"].startswith("B")}
    record_rows = []
    for unit_id in ("B1", "B2", "B3", "B4", "B5", "B6"):
        row = source_units[unit_id]
        record_rows.append({
            "unit_id": unit_id,
            "page": row["page"],
            "group_count": row["group_count"],
            "selected_model": "M1_THERAPEUTIC_BATH_WITH_SERVICE_ANNEX",
            "content_mode": "FIGURE_OWNED_BATH" if unit_id in {"B1", "B2", "B3", "B4"} else "FIGURELESS_SERVICE_STATION",
            "complete_record_reading_de": RECORDS[unit_id],
            "disease_or_anatomical_system": "UNSPECIFIED",
            "global_water_network": "NONE",
            "card_meanings_changed": "NO",
        })
    write_tsv(OUT / "EIGHTY_FOURTH_6_COMPLETE_BATH_SERVICE_RECORDS.tsv", record_rows)

    lookup = {row["unit_id"]: row for row in record_rows}
    bindings = []
    for row in read_tsv(BINDING):
        if row["register"] != "BIOLOGICAL_PROSE":
            continue
        record = lookup[row["finite_source_unit"]]
        bindings.append({
            "unified_serial": row["unified_serial"],
            "page": row["page"],
            "unit_or_locus": row["unit_or_locus"],
            "source_group_identity": row["source_group_identity"],
            "visible_identity": row["visible_identity"],
            "owner": row["owner_or_namespace"],
            "construction": row["construction_or_address"],
            "current_short_reading": row["current_short_reading"],
            "content_mode": record["content_mode"],
            "selected_record_reading_de": record["complete_record_reading_de"],
        })
    write_tsv(OUT / "EIGHTY_FOURTH_281_BATH_SERVICE_BINDING.tsv", bindings)

    analogues = [
        {"analogue": "De balneis Puteolorum tradition", "date": "medieval illustrated tradition", "use_here": "named baths and their virtues; pictures can own bath entries", "url": "https://wellcomecollection.org/works/stbvs45j"},
        {"analogue": "BL Harley MS 3407", "date": "late 14th/early 15th century", "use_here": "women's medicine, recipes and prognostics coexist", "url": "https://searcharchives.bl.uk/catalog/040-002049238"},
        {"analogue": "BL Sloane MS 6", "date": "medieval", "use_here": "instrument tables, cautery diagrams and pictured procedures", "url": "https://searcharchives.bl.uk/catalog/040-002112343"},
        {"analogue": "BL Harley MS 2375", "date": "15th century", "use_here": "herbal, hot/humid baths, clysters, oils and astrology coexist", "url": "https://searcharchives.bl.uk/catalog/040-002048206"},
        {"analogue": "BL Harley MS 2381", "date": "15th century", "use_here": "recipes, waters, plasters, distillation and astrological tables coexist", "url": "https://searcharchives.bl.uk/catalog/040-002048212"},
    ]
    write_tsv(OUT / "EIGHTY_FOURTH_5_HISTORICAL_BATH_ANALOGUES.tsv", analogues)

    doc = ["# Sechs konkrete Bad- und Dienstrecords", ""]
    for row in record_rows:
        doc.extend([f"## {row['unit_id']} · {row['page']}", "", row["complete_record_reading_de"], ""])
    doc.extend([
        "## Gemeinsame Lesung", "",
        "B1-B4 sind figurenbesessene Bad-/Waschstationen. B5-B6 sind",
        "figurenlose Dienststationen derselben Werkstatt. Der technische Apparat ist",
        "daher real, aber er dient lokal dem Bad; er bildet keinen globalen Kreislauf.",
    ])
    (OUT / "EIGHTY_FOURTH_COMPLETE_BATH_SERVICE_BOOK.md").write_text("\n".join(doc).rstrip() + "\n", encoding="utf-8")

    winner = max(totals, key=totals.get)
    report = [
        "# Vierundachtzigste Werkstattfassung: Badbuch mit Dienstschicht", "",
        "## Ergebnis", "",
        f"Three complete Biological vocabularies were applied to all six records. The",
        f"editorial totals are {totals}; {winner} is selected.", "",
        "The concrete model is not pure therapy and not a closed machine. B1-B4 are",
        "figure-owned bath/wash/application records; B5-B6 are figureless inlet, straining",
        "and outlet service stations. This explains why body words belong only where a",
        "visible person owns the station.", "",
        "No disease, organ, pregnancy or global water circuit is introduced. The selected",
        "bath/service words remain source-program content, not card translations.", "",
        "Only the fixed ten pages were used; f84 and f84r remained sealed.",
    ]
    (OUT / "EIGHTY_FOURTH_EDITION_REPORT.md").write_text("\n".join(report).rstrip() + "\n", encoding="utf-8")

    summary = {
        "status": "CONSISTENT",
        "counts": {
            "candidate_models": len(MODELS),
            "model_vocabulary_rows": len(model_rows),
            "model_record_comparisons": len(comparisons),
            "selected_words": len(words),
            "complete_records": len(record_rows),
            "bound_biological_groups": len(bindings),
            "historical_analogues": len(analogues),
        },
        "model_totals": totals,
        "selected_model": winner,
        "sources": {str(path.relative_to(ROOT)): sha256(path) for path in (UNITS, BINDING)},
    }
    (OUT / "BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
