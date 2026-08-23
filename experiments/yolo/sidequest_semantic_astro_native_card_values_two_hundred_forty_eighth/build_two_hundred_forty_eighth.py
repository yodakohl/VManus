#!/usr/bin/env python3
from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
SRC = ROOT / "experiments/yolo/sidequest_semantic_astro_curriculum_transfer_two_hundred_forty_seventh"
CARDS = SRC / "TWO_HUNDRED_FORTY_SEVENTH_29_KNOWN_PROSE_CARDS.tsv"
GROUPS = SRC / "TWO_HUNDRED_FORTY_SEVENTH_395_GROUP_ASTRO_MANUAL.tsv"

MAP = {
    "MC002": ("LANGSTUFE_SETZEN", "GRADE_SET", "lange Einwirkzeit ist lokale Nass-Ausführung"),
    "MC007": ("KURZSTUFE_SETZEN", "GRADE_SET", "kurze Einwirkzeit ist lokale Nass-Ausführung"),
    "MC017": ("TEILWERT_ZUGEBEN", "QUANTITY_INPUT", "Anteil bleibt abstrakt portabel"),
    "MC034": ("EINGANGSBEDINGUNG", "INPUT", "Herbal-Zutat ist eine konkrete Eingabe"),
    "MC053": ("DANACH_FORTSETZEN", "ORDER", "Fortgang bleibt portabel"),
    "MC059": ("ABDECK_ODER_TRAEGERFELD", "FIELD_OBJECT", "Prosa-Einlage ist lokale Trägerausführung"),
    "MC063": ("NAECHSTER_LANGSTUFENPOSTEN", "ORDER_GRADE", "Langfolge wird diagrammatisch konkret"),
    "MC067": ("FOLGEPLATZ_UEBERTRAGEN__SCHLUSS", "ORDER_TRANSFER", "Nachtransfer bleibt portabel"),
    "MC095": ("POSITION_LAENGER_HAL TEN".replace(" ", ""), "GRADE_HOLD", "Langhalt wird positionsbezogen"),
    "MC100": ("POSTEN_ZURUECKNEHMEN__SCHLUSS", "RESET_CLOSE", "Herbal-Abkühlen ist Zurücknahme aus Wärme"),
    "MC103": ("POSTEN_SETZEN", "SET", "Prosa-Weiterbearbeitung ist lokale Setzoperation"),
    "MC117": ("PLATZ_BEARBEITEN", "PROCESS", "Bearbeiten bleibt portabel"),
    "MC121": ("DANACH_VOM_AUSGANGSPLATZ", "ORDER_SOURCE", "Folgequelle wird diagrammatischer Ausgang"),
    "MC122": ("PLATZ_KURZ_BEARBEITEN", "PROCESS_GRADE", "Kurzbearbeitung bleibt portabel"),
    "MC140": ("VOLLSTAENDIG_SETZEN__SCHLUSS", "FULL_SET_CLOSE", "Volleinsatz bleibt portabel"),
    "MC159": ("AUFNAHMEFELD_ODER_UMSCHLUSS", "RECEIVER", "Herbal-Gefäß ist lokaler Empfänger"),
}

FEEDBACK = [
    ("OKEY", "KURZ_SETZEN", "kurz einwirken", "diagrammatisch kurze Stufe setzen"),
    ("OKEEY", "LAENGER_SETZEN_ODER_HAL TEN".replace(" ", ""), "lange einwirken", "diagrammatisch lange Stufe setzen"),
    ("CHO", "EINGABE_ODER_BEDINGUNG", "weitere Zutat", "Zutat ist Herbal-Eingabe; Astro hat Eingangsbedingung"),
    ("OS", "AUFNAHMEFELD_ODER_UMSCHLUSS", "Aufnahmegefäß", "Gefäß ist Herbal-Empfänger; Astro hat umschließendes Feld"),
    ("ODY", "ZURUECKNEHMEN__SCHLUSS", "abkühlen; Schluss", "Abkühlen ist Herbal-Zurücknahme aus aktivem Wärmezustand"),
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
    cards = read_tsv(CARDS)
    groups = read_tsv(GROUPS)
    revised_cards: list[dict[str, object]] = []
    for row in cards:
        item = dict(row)
        if row["master_card_id"] in MAP:
            value, role, note = MAP[row["master_card_id"]]
            item.update({"diagram_native_value_de": value, "diagram_role": role, "prose_to_diagram_relation": note, "value_scope": "REGISTER_NEUTRAL_CORE_WITH_LOCAL_EXPANSION"})
        else:
            item.update({"diagram_native_value_de": row["portable_value_de"], "diagram_role": "THREE_REGISTER_COMMON_CORE", "prose_to_diagram_relation": "already abstract and portable", "value_scope": "THREE_REGISTER_COMMON"})
        revised_cards.append(item)
    revised_by_id = {r["master_card_id"]: r for r in revised_cards}

    revised_groups: list[dict[str, object]] = []
    for row in groups:
        item = dict(row)
        if row["exact_prose_card_id"] != "NONE":
            card = revised_by_id[row["exact_prose_card_id"]]
            item.update({"portable_card_core_de": card["diagram_native_value_de"], "portable_card_role": card["diagram_role"]})
        else:
            item.update({"portable_card_core_de": "LOCAL_LABEL", "portable_card_role": "ASTRO_NAMESPACE_LABEL"})
        revised_groups.append(item)

    feedback_rows = [{"card_family": family, "new_portable_core_de": core, "old_prose_default_de": old, "cross_register_explanation": explanation} for family, core, old, explanation in FEEDBACK]
    card_path = OUT / "TWO_HUNDRED_FORTY_EIGHTH_29_DIAGRAM_NATIVE_CARDS.tsv"
    group_path = OUT / "TWO_HUNDRED_FORTY_EIGHTH_REVISED_395_GROUP_MANUAL.tsv"
    feedback_path = OUT / "TWO_HUNDRED_FORTY_EIGHTH_FIVE_PROSE_FEEDBACK_REVISIONS.tsv"
    readable_path = OUT / "TWO_HUNDRED_FORTY_EIGHTH_READABLE_DIAGRAM_DICTIONARY.md"
    report_path = OUT / "TWO_HUNDRED_FORTY_EIGHTH_REPORT.md"
    write_tsv(card_path, revised_cards, list(revised_cards[0]))
    write_tsv(group_path, revised_groups, list(revised_groups[0]))
    write_tsv(feedback_path, feedback_rows, list(feedback_rows[0]))

    readable = ["# Diagramm-native Lesung der 29 bekannten Karten", ""]
    for row in revised_cards:
        readable.append(f"- `{row['registered_surfaces_seen']}` = **{row['diagram_native_value_de']}** ({row['diagram_role']})")
    readable += ["", "## Fünf Rückkorrekturen an die Prosa", ""]
    for row in feedback_rows:
        readable.append(f"- `{row['card_family']}`: **{row['new_portable_core_de']}** — {row['cross_register_explanation']}")
    readable += [
        "", "Die Diagramme machen die Karten nicht semantisch leer. Sie zeigen nur, dass der tragbare Kern abstrakter sein muss als die konkrete Nass- oder Pflanzenhandlung. Der Bildbesitzer liefert wieder das fehlende Objekt.", "",
    ]
    readable_path.write_text("\n".join(readable), encoding="utf-8")

    role_counts = Counter(str(r["diagram_role"]) for r in revised_cards)
    report = f"""# Sidequest-Pass 248: diagramm-native Kartenwerte

## Ergebnis

Die sechzehn zusätzlichen Prosekarten werden auf kurze Diagrammfunktionen zurückgeführt: Stufe setzen, Teilwert zugeben, Eingangsbedingung, Trägerfeld, Folgeplatz, Position halten, zurücknehmen, bearbeiten, Ausgangsplatz und Aufnahmefeld. Keine Karte muss im Sternrad wörtlich Wasser, Zutat oder Gefäß bedeuten.

Fünf Prosa-Defaults werden dadurch besser:

- OKEY/OKEEY = kurz/länger setzen oder halten;
- CHO = Eingabe/Bedingung, lokal im Herbal eine Zutat;
- OS = Aufnahmefeld/Umschluss, lokal im Herbal ein Gefäß;
- ODY = zurücknehmen und schließen, lokal im Herbal aus Wärme nehmen/abkühlen.

Das ist die gesuchte Kompositionslogik: dieselbe Karte behält einen kleinen abstrakten Kern, während Bild und Register den konkreten Gegenstand einsetzen.

Input cards `{sha(CARDS)}`; groups `{sha(GROUPS)}`.
"""
    report_path.write_text(report, encoding="utf-8")
    summary = {
        "status": "PASS", "cards": len(revised_cards), "groups": len(revised_groups),
        "additional_cards_revised": len(MAP), "feedback_revisions": len(feedback_rows),
        "role_counts": dict(role_counts),
        "outputs": {p.name: sha(p) for p in (card_path, group_path, feedback_path, readable_path, report_path)},
    }
    (OUT / "BUILD_SUMMARY.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
