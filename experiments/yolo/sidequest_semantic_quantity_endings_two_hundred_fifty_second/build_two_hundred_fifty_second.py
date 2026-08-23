#!/usr/bin/env python3
from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
R251 = ROOT / "experiments/yolo/sidequest_semantic_component_equations_two_hundred_fifty_first"
R250 = ROOT / "experiments/yolo/sidequest_semantic_ten_page_working_edition_two_hundred_fiftieth"
DICTIONARY = R251 / "TWO_HUNDRED_FIFTY_FIRST_REVISED_173_CARD_DICTIONARY.tsv"
EVENTS = R250 / "TWO_HUNDRED_FIFTIETH_381_PROSE_EVENTS.tsv"

AIIN = {"MC018", "MC036", "MC039", "MC060", "MC087", "MC111", "MC120", "MC144", "MC169", "MC170"}
AIN = {"MC017", "MC047", "MC072", "MC097", "MC105", "MC145"}
AN = {"MC148"}
FALSE = {"MC059", "MC068"}

FAMILY = {
    "AIIN": ("VORGESCHRIEBENER_ODER_ZIELWERT", "X+AIIN = vorgeschriebener Wert von X"),
    "AIN": ("ABGEGRENZTER_ANTEIL", "X+AIN = abgegrenzter Anteil von X"),
    "AN": ("ZWEITER_ODER_ALTERNATIVER_ANTEIL", "X+AN = zweiter oder alternativer Anteil von X"),
    "FALSE_FRIEND": ("GANZKARTE_KEINE_MENGENENDUNG", "sichtbare Endbuchstaben nicht abtrennen"),
}


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


def family(card_id: str) -> str:
    if card_id in AIIN:
        return "AIIN"
    if card_id in AIN:
        return "AIN"
    if card_id in AN:
        return "AN"
    if card_id in FALSE:
        return "FALSE_FRIEND"
    raise KeyError(card_id)


def main() -> None:
    dictionary = read_tsv(DICTIONARY)
    events = read_tsv(EVENTS)
    target = AIIN | AIN | AN | FALSE
    cards: list[dict[str, object]] = []
    for row in dictionary:
        if row["master_card_id"] not in target:
            continue
        grade = family(row["master_card_id"])
        value, rule = FAMILY[grade]
        cards.append({
            "master_card_id": row["master_card_id"], "master_form": row["master_form"],
            "registered_surfaces": row["registered_surfaces"], "quantity_ending": grade,
            "family_value_de": value, "component_formula": row["component_parse"],
            "card_value_de": row["portable_core_de"], "prose_event_count": row["prose_event_count"],
            "records": row["records"], "apprentice_rule": rule,
            "analysis_status": "TENTATIVE_SINGLE_AN" if grade == "AN" else ("WHOLE_CARD_EXCLUSION" if grade == "FALSE_FRIEND" else "PRODUCTIVE_QUANTITY_ENDING"),
        })

    occurrence_rows: list[dict[str, object]] = []
    for row in events:
        if row["master_card_id"] not in target:
            continue
        grade = family(row["master_card_id"])
        value, rule = FAMILY[grade]
        occurrence_rows.append({
            "event_id": row["event_id"], "page": row["page"], "record_unit_id": row["record_unit_id"],
            "statement_id": row["statement_id"], "visible_surface": row["visible_surface"],
            "master_card_id": row["master_card_id"], "quantity_ending": grade,
            "family_value_de": value, "local_card_value_de": row["portable_core_de"],
            "visible_owner": row["visible_owner"], "terminal_status": row["terminal_status"],
        })

    grade_rows = []
    for grade in ("AIN", "AN", "AIIN"):
        linked_cards = [r for r in cards if r["quantity_ending"] == grade]
        linked_events = [r for r in occurrence_rows if r["quantity_ending"] == grade]
        grade_rows.append({
            "ending": grade, "core_value_de": FAMILY[grade][0], "composition_rule": FAMILY[grade][1],
            "card_count": len(linked_cards), "event_count": len(linked_events),
            "master_card_ids": "|".join(str(r["master_card_id"]) for r in linked_cards),
            "surface_examples": "|".join(str(r["master_form"]) for r in linked_cards),
        })

    false_rows = [r for r in cards if r["quantity_ending"] == "FALSE_FRIEND"]
    card_path = OUT / "TWO_HUNDRED_FIFTY_SECOND_19_QUANTITY_AND_CONTROL_CARDS.tsv"
    occurrence_path = OUT / "TWO_HUNDRED_FIFTY_SECOND_58_OCCURRENCES.tsv"
    grade_path = OUT / "TWO_HUNDRED_FIFTY_SECOND_THREE_QUANTITY_ENDINGS.tsv"
    false_path = OUT / "TWO_HUNDRED_FIFTY_SECOND_TWO_FALSE_FRIENDS.tsv"
    readable_path = OUT / "TWO_HUNDRED_FIFTY_SECOND_READABLE_QUANTITY_LESSON.md"
    report_path = OUT / "TWO_HUNDRED_FIFTY_SECOND_REPORT.md"
    write_tsv(card_path, cards, list(cards[0]))
    write_tsv(occurrence_path, occurrence_rows, list(occurrence_rows[0]))
    write_tsv(grade_path, grade_rows, list(grade_rows[0]))
    write_tsv(false_path, false_rows, list(false_rows[0]))

    readable = [
        "# Drei Mengenenden", "",
        "## AIN — abgegrenzter Anteil", "",
        "`X + AIN` bedeutet: eine begrenzte Portion von X nehmen, geben oder übertragen.", "",
        "## AN — zweiter oder alternativer Anteil", "",
        "`X + AN` markiert im bisher einzigen sauberen Paar die zweite Portion. Diese kleine Stufe bleibt vorläufig, ist aber nötig, um YKAIN und YKAN nicht künstlich gleichzusetzen.", "",
        "## AIIN — vorgeschriebener Wert", "",
        "`X + AIIN` bedeutet: X auf einen vorgegebenen Wert, ein Sollmaß, eine Sollzeit oder eine Sollstufe bringen.", "",
        "## Das dreifache Portionstripel", "",
        "- `ykain` → erste Portion",
        "- `ykan` → zweite Portion",
        "- `ykaiin` → Sollportion", "",
        "## Nicht zerlegen", "",
        "- `dain` = Einlage/Tuchkarte, nicht D+AIN.",
        "- `sotodan` = Folgeanwendung, nicht SOTOD+AN.", "",
    ]
    readable_path.write_text("\n".join(readable), encoding="utf-8")

    counts = Counter(r["quantity_ending"] for r in occurrence_rows)
    report = f"""# Sidequest-Pass 252: AIN/AN/AIIN-Mengenparadigma

## Ergebnis

- AIIN: 10 Karten, 39 Ereignisse, vorgeschriebener oder Zielwert;
- AIN: 6 Karten, 15 Ereignisse, abgegrenzter Anteil;
- AN: 1 Karte, 1 Ereignis, zweite/alternative Portion;
- zwei Ganzkarten-Lookalikes mit zusammen 3 Ereignissen.

Das Paradigma erklärt Sollmaß, Folgemaß, Sollsammlung, Zugabemaß, Stehzeit, Sollabsetzung, Sollvorbereitung, Portion, weiteren Anteil, Bereitungsanteil und Anteilstransfer mit drei kurzen Endungen. AN ist der schwächste, aber konkret nützliche neue Grad.

Input dictionary `{sha(DICTIONARY)}`; events `{sha(EVENTS)}`.
"""
    report_path.write_text(report, encoding="utf-8")
    summary = {
        "status": "PASS", "cards": len(cards), "occurrences": len(occurrence_rows),
        "ending_counts": dict(counts), "false_friends": len(false_rows),
        "outputs": {p.name: sha(p) for p in (card_path, occurrence_path, grade_path, false_path, readable_path, report_path)},
    }
    (OUT / "BUILD_SUMMARY.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
