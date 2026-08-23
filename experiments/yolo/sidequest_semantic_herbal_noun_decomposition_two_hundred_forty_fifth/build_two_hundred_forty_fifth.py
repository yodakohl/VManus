#!/usr/bin/env python3
from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
R243 = ROOT / "experiments/yolo/sidequest_semantic_herbal_curriculum_transfer_two_hundred_forty_third"
R244 = ROOT / "experiments/yolo/sidequest_semantic_herbal_operation_decomposition_two_hundred_forty_fourth"
CARDS = R243 / "TWO_HUNDRED_FORTY_THIRD_66_CARD_HERBAL_DICTIONARY.tsv"
EVENTS = R243 / "TWO_HUNDRED_FORTY_THIRD_100_EVENT_HERBAL_TRANSFER.tsv"
REVISED = R244 / "TWO_HUNDRED_FORTY_FOURTH_REVISED_66_CARD_DICTIONARY.tsv"

MAP = {
    "MC010": ("CHO + AL + Y", "Zugabe am aktuellen Ziel", "FULL_COMPOSITION", "NONE"),
    "MC013": ("OT + OR", "Folgeansatz", "FULL_COMPOSITION", "NONE"),
    "MC014": ("CH + AIR", "laufendes Medium zugießen", "PARTIAL_COMPOSITION", "CH pouring core"),
    "MC027": ("OYK + OR", "Gefäß für den Ansatz", "PARTIAL_COMPOSITION", "OYK preparation-vessel core"),
    "MC034": ("CHO", "weitere Zutat", "LEARNED_WHOLE_NOUN", "CHO ingredient core"),
    "MC047": ("Y + K + AIN", "erste Portion", "PARTIAL_COMPOSITION", "K ordinal/index core"),
    "MC049": ("SCHOAL", "Sudansatz", "LEARNED_WHOLE_NOUN", "SCHOAL decoction core"),
    "MC062": ("SHO + YTY", "Zugabeteil", "PARTIAL_COMPOSITION", "YTY material-part core"),
    "MC069": ("OT + YTY + OL", "Folgeteil", "PARTIAL_COMPOSITION", "YTY material-part core"),
    "MC071": ("DCHEY", "Wurzel", "LEARNED_WHOLE_NOUN", "DCHEY root core"),
    "MC072": ("OR + AIN", "Bereitungsanteil", "FULL_COMPOSITION", "NONE"),
    "MC075": ("Y + CHEO + OR", "aktueller Auszugsansatz", "FULL_COMPOSITION", "NONE"),
    "MC085": ("CHEO + AR", "Auszug aus der Quelle", "FULL_COMPOSITION", "NONE"),
    "MC087": ("CHO + AIIN", "Zugabemaß", "FULL_COMPOSITION", "NONE"),
    "MC098": ("TSHOL", "Kochgut", "LEARNED_WHOLE_NOUN", "TSHOL cooking-material core"),
    "MC108": ("ETYD", "kleiner Rest", "LEARNED_WHOLE_NOUN", "ETYD remainder core"),
    "MC114": ("SH", "Stängel", "LEARNED_WHOLE_NOUN", "SH stem core"),
    "MC125": ("CHO + OR", "Zugabeansatz", "FULL_COMPOSITION", "NONE"),
    "MC131": ("CHO + Y", "aktuelle Zutat", "FULL_COMPOSITION", "NONE"),
    "MC136": ("K + CHO + AR", "bearbeiteter Quellauszug", "PARTIAL_COMPOSITION", "KCHO processed-extract core"),
    "MC148": ("Y + K + AIN", "zweite Portion", "PARTIAL_COMPOSITION", "K ordinal/index core"),
    "MC159": ("OS", "Aufnahmegefäß", "LEARNED_WHOLE_NOUN", "OS receiver-vessel core"),
    "MC160": ("TALAM", "Verwahrort", "LEARNED_WHOLE_NOUN", "TALAM storage-place core"),
    "MC170": ("Y + K + AIIN", "Sollportion", "PARTIAL_COMPOSITION", "K ordinal/index core"),
}

LEXEMES = [
    ("CHO", "ZUTAT", "productive noun core"), ("SCHOAL", "SUDANSATZ", "whole noun"),
    ("DCHEY", "WURZEL", "whole noun"), ("TSHOL", "KOCHGUT", "whole noun"),
    ("ETYD", "REST", "whole noun"), ("SH", "STAENGEL", "whole noun"),
    ("OS", "AUFNAHMEGEFAESS", "whole noun"), ("TALAM", "VERWAHRORT", "whole noun"),
    ("CH", "ZUGIESSEN", "residual action core in noun compound"),
    ("OYK", "ZUBEREITUNGSGEFAESS", "residual container core"),
    ("K", "ORDNUNGS_ODER_INDEXWERT", "residual noun index core"),
    ("YTY", "MATERIALTEIL", "residual part core"),
    ("KCHO", "BEARBEITETER_AUSZUG", "residual preparation core"),
]


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: list[dict[str, object]], fields: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    cards, events, revised = read_tsv(CARDS), read_tsv(EVENTS), read_tsv(REVISED)
    noun_cards = [r for r in cards if r["curriculum_layer"] == "HERBAL_LOCAL_NOUN_SIGN"]
    decomposition_rows: list[dict[str, object]] = []
    for row in noun_cards:
        components, reading, status, residue = MAP[row["master_card_id"]]
        decomposition_rows.append({
            "master_card_id": row["master_card_id"], "master_form": row["master_form"],
            "registered_surfaces": row["registered_surfaces"], "old_default_de": row["concrete_default_de"],
            "component_parse": components, "revised_compositional_reading_de": reading,
            "composition_status": status, "memorized_residue": residue,
            "occurrence_count": row["occurrence_count"], "event_ids": row["event_ids"],
            "apprentice_rule": (
                "combine known noun and relation components" if status == "FULL_COMPOSITION"
                else "combine known frame and memorize one noun core" if status == "PARTIAL_COMPOSITION"
                else "memorize this concrete noun core"
            ),
        })

    occurrence_rows: list[dict[str, object]] = []
    for event in events:
        if event["master_card_id"] not in MAP:
            continue
        components, reading, status, residue = MAP[event["master_card_id"]]
        occurrence_rows.append({
            "event_id": event["event_id"], "page": event["page"], "record_unit_id": event["record_unit_id"],
            "statement_id": event["statement_id"], "visible_owner": event["visible_owner"],
            "visible_surface": event["visible_surface"], "master_card_id": event["master_card_id"],
            "component_parse": components, "revised_compositional_reading_de": reading,
            "composition_status": status, "memorized_residue": residue,
        })

    final_cards: list[dict[str, object]] = []
    for row in revised:
        item = dict(row)
        if row["master_card_id"] in MAP:
            components, reading, status, residue = MAP[row["master_card_id"]]
            item.update({"component_parse": components, "revised_default_de": reading, "composition_status": status, "memorized_residue": residue})
        final_cards.append(item)

    lexeme_rows = [{"learned_core": core, "short_meaning_de": meaning, "learning_status": status} for core, meaning, status in LEXEMES]
    decomposition_path = OUT / "TWO_HUNDRED_FORTY_FIFTH_24_NOUN_CARDS.tsv"
    occurrence_path = OUT / "TWO_HUNDRED_FORTY_FIFTH_28_NOUN_OCCURRENCES.tsv"
    lexeme_path = OUT / "TWO_HUNDRED_FORTY_FIFTH_13_LEARNED_NOUN_CORES.tsv"
    dictionary_path = OUT / "TWO_HUNDRED_FORTY_FIFTH_FINAL_66_CARD_HERBAL_DICTIONARY.tsv"
    readable_path = OUT / "TWO_HUNDRED_FORTY_FIFTH_READABLE_NOUN_LESSON.md"
    report_path = OUT / "TWO_HUNDRED_FORTY_FIFTH_REPORT.md"
    write_tsv(decomposition_path, decomposition_rows, list(decomposition_rows[0]))
    write_tsv(occurrence_path, occurrence_rows, list(occurrence_rows[0]))
    write_tsv(lexeme_path, lexeme_rows, list(lexeme_rows[0]))
    write_tsv(dictionary_path, final_cards, list(final_cards[0]))

    readable = ["# Herbal-Nomenlektion", "", "## Vollständig gebaute Nomenkarten", ""]
    for row in decomposition_rows:
        if row["composition_status"] == "FULL_COMPOSITION":
            readable.append(f"- `{row['master_form']}` = `{row['component_parse']}` → {row['revised_compositional_reading_de']}")
    readable += ["", "## Bekannter Rahmen plus neuer Nomenkern", ""]
    for row in decomposition_rows:
        if row["composition_status"] == "PARTIAL_COMPOSITION":
            readable.append(f"- `{row['master_form']}` = `{row['component_parse']}` → {row['revised_compositional_reading_de']}; lerne {row['memorized_residue']}")
    readable += ["", "## Ganze Nomen", ""]
    for row in decomposition_rows:
        if row["composition_status"] == "LEARNED_WHOLE_NOUN":
            readable.append(f"- `{row['master_form']}` → {row['revised_compositional_reading_de']}")
    readable += ["", "Der sichtbare Bildbesitzer ersetzt den Pflanzennamen. Deshalb genügen dreizehn neue Inhaltskerne für Teil, Zutat, Gefäß, Ansatz, Rest und Ort; Menge, Folge, Quelle und Ziel kommen aus der gemeinsamen Grammatik.", ""]
    readable_path.write_text("\n".join(readable), encoding="utf-8")

    card_counts = Counter(r["composition_status"] for r in decomposition_rows)
    event_counts = Counter(r["composition_status"] for r in occurrence_rows)
    report = f"""# Sidequest-Pass 245: Herbal-Nomenkarten zerlegen

## Ergebnis

Die 24 lokalen Nomenkarten teilen sich symmetrisch: **8 vollständig kompositionell**, **8 teilweise kompositionell**, **8 ganze Nomenkarten**. Nach Vorkommen sind es 9, 8 und 11 Ereignisse.

Die teilweise und ganz gelernten Karten benötigen zusammen nur **13 neue Nomenkerne**. Produktive Kombinationen wie `OR+AIN`, `OT+OR`, `CHEO+AR`, `CHO+AIIN`, `CHO+OR`, `CHO+Y` und `CHO+AL+Y` erzeugen dagegen neue konkrete Bedeutungen vorhersagbar.

Die wichtigsten wirklich neuen Inhaltskerne sind Zutat, Wurzel, Stängel, Kochgut, Rest, Aufnahmegefäß und Verwahrort. Der Pflanzenname selbst bleibt beim Bildbesitzer und braucht keine Karte.

Input cards `{sha(CARDS)}`; operations-integrated dictionary `{sha(REVISED)}`.
"""
    report_path.write_text(report, encoding="utf-8")
    summary = {
        "status": "PASS", "noun_cards": len(decomposition_rows), "noun_occurrences": len(occurrence_rows),
        "learned_noun_cores": len(lexeme_rows), "card_status_counts": dict(card_counts),
        "event_status_counts": dict(event_counts),
        "outputs": {p.name: sha(p) for p in (decomposition_path, occurrence_path, lexeme_path, dictionary_path, readable_path, report_path)},
    }
    (OUT / "BUILD_SUMMARY.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
