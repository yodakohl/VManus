#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
P986 = ROOT / "experiments/yolo/sidequest_semantic_root_codebook_reconciliation_nine_hundred_eighty_sixth"
IMAGE_URL = "https://collections.library.yale.edu/iiif/2/1037112/full/2000,/0/default.jpg"
IMAGE_SHA256 = "aa266580695fc4a84cd031015c56f51f1b6ce807b6998c6ef4b8b68bae11983b"

LABELS = [
    ("D001", "UPPER_SIX", 1, "blasses vielzehiges Wurzelbündel"),
    ("D002", "UPPER_SIX", 2, "schmale dunkle Spindelwurzel"),
    ("D003", "UPPER_SIX", 3, "gebundenes helles Faserwurzelbündel"),
    ("D004", "UPPER_SIX", 4, "dicke braune verzweigte Knollenwurzel"),
    ("D005", "UPPER_SIX", 5, "heller Knotenkopf mit Schlingwurzeln"),
    ("D006", "UPPER_SIX", 6, "einzelnes lanzettliches Blatt"),
    ("D007", "MIDDLE_SIX", 1, "kräftiger gegabelter Wurzelstock mit Blattkrone"),
    ("D008", "MIDDLE_SIX", 2, "schmale braune Hänge- oder Spindelwurzel"),
    ("D009", "MIDDLE_SIX", 3, "aufrechter grüner gezähnter Pflanzenkörper mit Wurzelbüschel"),
    ("D010", "MIDDLE_SIX", 4, "heller gefasster Faserwurzelstock"),
    ("D011", "MIDDLE_SIX", 5, "gefleckter ovaler Knollen- oder Fruchtkörper"),
    ("D012", "MIDDLE_SIX", 6, "langer Zweig mit paarigen Blättern"),
    ("D013", "LOWER_FOUR", 1, "Wurzelkrone mit roten Wurzeln und gezähnten Blättern"),
    ("D014", "LOWER_FOUR", 2, "kriechender Stock mit rund gezähnten Blättern"),
    ("D015", "LOWER_FOUR", 3, "großer geschichteter heller Wurzel- oder Schnittkörper"),
    ("D016", "LOWER_FOUR", 4, "langer rötlicher Speicherteil mit zwei langen Blättern"),
]

BATCHES = [
    {
        "batch_id": "UPPER_SIX",
        "visible_vessel_owner_de": "oberes hohes rot-grünes Vorrats-/Ansatzgefäß",
        "label_count": "6",
        "label_ids": "D001|D002|D003|D004|D005|D006",
        "prose_clause_ids": "P915-C350",
        "continuous_batch_reading_de": "Sechs bezeichnete Drogenposten der oberen Reihe auswählen, portionsweise in den oberen Gefäßansatz geben, kurz vorbereiten und den entstehenden Auszug zur nächsten Aufnahme leiten.",
    },
    {
        "batch_id": "MIDDLE_SIX",
        "visible_vessel_owner_de": "mittleres rot-grünes Vorrats-/Ansatzgefäß",
        "label_count": "6",
        "label_ids": "D007|D008|D009|D010|D011|D012",
        "prose_clause_ids": "P915-C351|P915-C352",
        "continuous_batch_reading_de": "Sechs bezeichnete Drogenposten der mittleren Reihe für einen zweiten Ansatz wählen, nach Sollmaß zugeben, mehrfach fortführen, durch den Auszugsweg leiten und länger halten.",
    },
    {
        "batch_id": "LOWER_FOUR",
        "visible_vessel_owner_de": "unteres kleineres rot-grünes Vorrats-/Ansatzgefäß",
        "label_count": "4",
        "label_ids": "D013|D014|D015|D016",
        "prose_clause_ids": "P915-C353|P915-C354",
        "continuous_batch_reading_de": "Vier bezeichnete Drogenposten der unteren Reihe wählen, aus dem Vorrat nehmen, länger ansetzen, nach Sollmaß fortführen und die letzte Gefäßcharge schließen.",
    },
]


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(path: Path, rows: list[dict[str, str]], fields: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    codebook = read(P986 / "PASS986_159_RECONCILED_CODEBOOK.tsv")
    events = read(P986 / "PASS986_2511_RECONCILED_EVENT_INTERLINEAR.tsv")
    codebook_by_id = {row["teaching_unit_id"]: row for row in codebook}
    event_by_unit = {
        unit_id: [row for row in events if unit_id in row["primary_teaching_unit_ids"].split("|")]
        for unit_id, _, _, _ in LABELS
    }

    label_rows = []
    for unit_id, batch_id, position, visual_class in LABELS:
        unit = codebook_by_id[unit_id]
        matched = event_by_unit[unit_id]
        event = matched[0]
        label_rows.append(
            {
                "teaching_unit_id": unit_id,
                "event_id": event["event_id"],
                "locus": event["locus"],
                "surface": event["surface"],
                "batch_id": batch_id,
                "position_in_batch": str(position),
                "visual_role": "INGREDIENT_LABEL",
                "cautious_visible_material_class_de": visual_class,
                "spoken_local_name_de": unit["spoken_value_de"],
                "species_name": "NONE",
                "textual_batch_heading": "NONE__VESSEL_IS_SILENT_BATCH_OWNER",
                "image_url": IMAGE_URL,
                "image_sha256": IMAGE_SHA256,
            }
        )

    write(HERE / "PASS988_16_F88R_VISUAL_INGREDIENT_LABELS.tsv", label_rows, list(label_rows[0]))
    write(HERE / "PASS988_THREE_SILENT_VESSEL_BATCHES.tsv", BATCHES, list(BATCHES[0]))
    summary = {
        "status": "PASS",
        "ingredient_labels": len(label_rows),
        "silent_vessel_batches": len(BATCHES),
        "batch_shape": [sum(row["batch_id"] == batch["batch_id"] for row in label_rows) for batch in BATCHES],
        "species_names": 0,
        "textual_batch_headings": 0,
    }
    (HERE / "PASS988_BUILD_SUMMARY.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")

    report = """# Pass 988 — f88r: sechzehn Zutaten, drei stumme Gefäßköpfe

## Bildkorrektur

Das Originalbild zeigt drei hohe Gefäße und unmittelbar daneben drei Reihen
einzeln gezeichneter Materialkörper. Die erste Schriftgruppe jeder Reihe steht
über oder neben dem ersten Materialkörper, nicht als sichere Überschrift am
Gefäß. Die bessere Zuordnung lautet daher:

- obere Reihe: sechs Zutatenetiketten;
- mittlere Reihe: sechs Zutatenetiketten;
- untere Reihe: vier Zutatenetiketten;
- die drei Gefäße selbst sind die stummen Besitzer der drei Chargen.

Damit werden die sechzehn gelernten Karten nicht künstlich in dreizehn Wörter
plus drei Textüberschriften zerlegt. Alle sechzehn bleiben lokale Namen oder
Klassencodes für sichtbare Drogenposten.

## Was die Bilder erlauben

Die Körper lassen sich vorsichtig als Faserwurzel, Spindelwurzel,
Knollenwurzel, Schlingwurzel, Einzelblatt, Blattzweig, Wurzelkrone oder
Speicherteil beschreiben. Das genügt für eine Werkstattlesung. Kein Bild trägt
einen sicheren botanischen Artnamen, und kein Etikett wird deshalb als
lateinischer Pflanzenname ausgegeben.

## Arbeitslesung

> Wähle in jeder der drei Reihen die bezeichneten Drogenposten. Gib sie in der
> vorgesehenen Folge und Menge in das benachbarte Gefäß, führe den Ansatz nach
> der anschließenden Prosa aus und behandle jede Reihe als eigene Charge.

Die Seite ist damit die klarste Brücke des Buches: lokale gelernte Stoffnamen
oben, produktive Mengen-, Ansatz-, Halte-, Leit- und Schlusskarten darunter.
"""
    (HERE / "PASS988_REPORT.md").write_text(report, encoding="utf-8")


if __name__ == "__main__":
    main()
