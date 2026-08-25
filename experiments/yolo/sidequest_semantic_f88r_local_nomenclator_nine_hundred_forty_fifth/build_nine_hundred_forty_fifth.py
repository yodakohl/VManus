#!/usr/bin/env python3
from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
EVENTS = ROOT / "experiments/yolo/sidequest_semantic_integrated_fourteen_page_edition_nine_hundred_thirty_ninth/PASS939_2511_CURRENT_EVENT_INTERLINEAR.tsv"
CLAUSES = ROOT / "experiments/yolo/sidequest_semantic_hybrid_card_retranslation_nine_hundred_forty_fourth/PASS944_354_HYBRID_CARD_CLAUSES.tsv"


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: list[dict[str, object]], fields: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


LABELS = {
    "P912-E2362": ("F88-A", "PREPARATION_HEADING", "OBERES GEFÄSS UND ZUBEREITUNG A"),
    "P912-E2363": ("F88-A", "INGREDIENT", "SCHMALES WURZELBÜNDEL A1"),
    "P912-E2364": ("F88-A", "INGREDIENT", "DUNKLE SPINDELWURZEL A2"),
    "P912-E2365": ("F88-A", "INGREDIENT", "GEBUNDENES HELLWURZELBÜNDEL A3"),
    "P912-E2366": ("F88-A", "INGREDIENT", "DICKE VERZWEIGTE WURZEL A4"),
    "P912-E2367": ("F88-A", "INGREDIENT", "HELLE SCHLINGWURZEL A5"),
    "P912-E2415": ("F88-B", "PREPARATION_HEADING", "MITTLERES GEFÄSS UND ZUBEREITUNG B"),
    "P912-E2416": ("F88-B", "INGREDIENT", "ORANGE VERZWEIGTE WURZEL B1"),
    "P912-E2417": ("F88-B", "INGREDIENT", "DUNKLE HÄNGEWURZEL B2"),
    "P912-E2418": ("F88-B", "INGREDIENT", "GEFASSTE FASERWURZEL B3"),
    "P912-E2419": ("F88-B", "INGREDIENT", "GRÜNES BLATT- ODER FRONDBÜNDEL B4"),
    "P912-E2420": ("F88-B", "INGREDIENT", "GEFLECKTE KNOLLE MIT BLATTZWEIG B5"),
    "P912-E2460": ("F88-C", "PREPARATION_HEADING", "UNTERES GEFÄSS UND ZUBEREITUNG C"),
    "P912-E2461": ("F88-C", "INGREDIENT", "LANGBLÄTTRIGE WURZEL C1"),
    "P912-E2462": ("F88-C", "INGREDIENT", "ZWEITER INNERER POSTEN C2"),
    "P912-E2463": ("F88-C", "INGREDIENT", "RANKENDE WURZEL MIT RUNDBLÄTTERN C3"),
}

RECORDS = [
    {
        "record_id": "F88-A",
        "label_events": "P912-E2362..P912-E2367",
        "prose_events": "P912-E2368..P912-E2414",
        "clauses": "P915-C350",
        "visible_inventory_de": "oberes rotes/grünes Gefäß; fünf einzeln beschriftete Wurzeltypen",
        "continuous_reading_de": "Für die obere Zubereitung die fünf bezeichneten Wurzeln nach ihrer Karte auswählen. Aus jedem verlangten Teil den Ansatz bilden, kurz halten und am Ziel oder im inneren Gefäß weiterarbeiten. Portion und Sollmaß eintragen, den passenden Zug wählen, den Auszug weiterführen und die erste Mischung für den folgenden Eintrag bereitlassen.",
    },
    {
        "record_id": "F88-B",
        "label_events": "P912-E2415..P912-E2420",
        "prose_events": "P912-E2421..P912-E2459",
        "clauses": "P915-C351|P915-C352",
        "visible_inventory_de": "mittleres Deckelgefäß; fünf beschriftete Wurzel-, Knollen- und Blattposten",
        "continuous_reading_de": "Für die mittlere Zubereitung die fünf angegebenen Pflanzenposten nacheinander übernehmen. Den ersten Teil zugeben, bearbeiten und zum nächsten Lauf bringen; diesen Teilgang abschließen. Danach weitere Anteile nach Sollmaß einsetzen, durch den bezeichneten Durchlass führen, länger halten und den gewonnenen Auszug markieren.",
    },
    {
        "record_id": "F88-C",
        "label_events": "P912-E2460..P912-E2463",
        "prose_events": "P912-E2464..P912-E2511",
        "clauses": "P915-C353|P915-C354",
        "visible_inventory_de": "unteres grünes/rotes Gefäß; drei lokale Pflanzen- oder Wurzelposten, einer mit zweiteiligem Etikett",
        "continuous_reading_de": "Für die untere Zubereitung die letzten drei bezeichneten Pflanzenposten verwenden. Aus der Quelle länger einsetzen, den Ansatz auffangen und kurz weiterführen. Danach mehrmals denselben Ansatz fortsetzen, den Auszug durch den Lauf geben, nach Sollmaß halten und den fertigen Posten auf die angegebene Zielstelle verteilen.",
    },
]


def main() -> None:
    events = {row["event_id"]: row for row in read_tsv(EVENTS)}
    clauses = {row["clause_id"]: row for row in read_tsv(CLAUSES)}
    label_rows: list[dict[str, object]] = []
    for event_id, (record, role, value) in LABELS.items():
        row = events[event_id]
        label_rows.append({
            "event_id": event_id,
            "record_id": record,
            "locus": row["locus"],
            "surface": row["surface"],
            "component_recipe": row["component_recipe"],
            "visual_role": role,
            "local_nomenclator_default_de": value,
            "address_reading_de": row["current_compositional_reading_de"],
        })
    write_tsv(OUT / "PASS945_16_F88R_LOCAL_LABELS.tsv", label_rows, list(label_rows[0]))

    record_rows: list[dict[str, object]] = []
    for record in RECORDS:
        clause_ids = record["clauses"].split("|")
        record_rows.append({
            **record,
            "prose_cards": sum(int(clauses[clause]["events"]) for clause in clause_ids),
            "hybrid_clause_readings_de": " || ".join(clauses[clause]["hybrid_card_translation_de"] for clause in clause_ids),
        })
    write_tsv(OUT / "PASS945_3_F88R_PREPARATION_RECORDS.tsv", record_rows, list(record_rows[0]))

    edition = [
        "# f88r — drei Zubereitungsregister",
        "",
        "Das Bild zeigt drei dekorative Gefäße, und jedes Gefäß eröffnet einen eigenen Textblock mit einer eigenen Reihe beschrifteter Wurzeln, Knollen oder Blätter. Die Etiketten werden deshalb als lokale Zutatenkarten gelesen, nicht als Verben.",
        "",
    ]
    by_record = {record["record_id"]: record for record in record_rows}
    for record_id in ["F88-A", "F88-B", "F88-C"]:
        record = by_record[record_id]
        edition.extend([f"## {record_id}", "", str(record["continuous_reading_de"]), "", f"Sichtbar: {record['visible_inventory_de']}.", "", "Etiketten:", ""])
        for label in [row for row in label_rows if row["record_id"] == record_id]:
            edition.append(f"- `{label['surface']}` — {label['local_nomenclator_default_de']}")
        edition.append("")
    (OUT / "PASS945_F88R_COMPLETE_LOCAL_EDITION.md").write_text("\n".join(edition), encoding="utf-8")

    report = """# Pass 945 — f88r wird zum echten Nomenklatorblatt

## Bildlesung

f88r hat drei klar getrennte Einheiten. Jede beginnt links mit einem dekorativen
Gefäß, trägt darüber oder daneben eine Reihe einzeln beschrifteter
Wurzel-/Blattformen und setzt darunter mit einem eigenen Prosablock fort. Die
drei `@Lc`-Etiketten sind daher Zubereitungs- oder Gefäßköpfe; die dreizehn
`@Lf`-Gruppen sind lokale Zutatenkarten. Eine davon besteht aus zwei sichtbaren
Gruppen und bezeichnet plausibel einen zusammengesetzten oder doppelt
adressierten Posten.

## Bedeutungsgewinn

Die 16 Bildgruppen erhalten jetzt konkrete lokale Defaults: Gefäß/Zubereitung A,
B oder C und visuell beschriebene Zutaten A1–C3. Diese Werte müssen nicht als
manuskriptweite Wörter in die 56 Kürzel eingehen. Genau hier sitzt der gelernte
Nomenklator: Die produktive Prosa sagt auswählen, messen, ansetzen, halten,
weiterführen und abschließen; das Bildetikett sagt *welcher* Stoff oder welches
Gefäß gemeint ist.

## Neue Gesamtlesung

Die Seite ist kein einzelnes Rezept und auch kein bloßes Pflanzenalbum. Sie ist
eine kleine pharmazeutische Brücke aus drei bebilderten Zubereitungsregistern.
"""
    (OUT / "PASS945_REPORT.md").write_text(report, encoding="utf-8")
    summary = {"labels": len(label_rows), "records": len(record_rows), "events": 150, "prose_events": sum(int(row["prose_cards"]) for row in record_rows), "outputs": {}}
    for path in sorted(OUT.glob("PASS945_*")):
        summary["outputs"][path.name] = hashlib.sha256(path.read_bytes()).hexdigest()
    (OUT / "PASS945_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
