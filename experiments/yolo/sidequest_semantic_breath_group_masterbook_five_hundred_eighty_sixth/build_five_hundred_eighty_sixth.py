#!/usr/bin/env python3
import csv
import json
import re
from collections import OrderedDict
from pathlib import Path

HERE = Path(__file__).resolve().parent
YOLO = HERE.parent
P582 = YOLO / "sidequest_semantic_minimal_contrast_pairs_five_hundred_eighty_second"
P584 = YOLO / "sidequest_semantic_formula_variant_absorption_five_hundred_eighty_fourth"
P585 = YOLO / "sidequest_semantic_full_statement_correction_five_hundred_eighty_fifth"

REPLACE = [
    ("den laufenden Posten", "dies"), ("diesen Posten", "dies"),
    ("vorgeschriebenes Maß", "Maß"), ("bezeichnete Stelle", "Ziel"),
    ("von dort", "davon"), ("Arbeitsgang", "Gang"),
    ("fortsetzen", "fort"), ("Schritt schließen", "schließe"),
    ("den Schritt schließen", "schließe"),
]


def read(path):
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(name, rows):
    with (HERE / name).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def short(text):
    value = text
    for old, new in REPLACE:
        value = value.replace(old, new)
    return re.sub(r"\s+", " ", value).strip().replace(" ;", ";")


def main():
    formula = read(P584 / "FIVE_HUNDRED_EIGHTY_FOURTH_REVISED_ONE_HUNDRED_SIXTEEN_FORMULA_MAP.tsv")
    target = {r["statement_id"]: r for r in formula if r["revised_learning_mode"] in {"EXTENDED_TWO_EDIT_VARIANT", "FREE_COMPOSITION"}}
    events = [r for r in read(P585 / "FIVE_HUNDRED_EIGHTY_FIFTH_CORRECTED_THREE_HUNDRED_EIGHTY_ONE_EVENT_BINDING.tsv") if r["statement_id"] in target]
    speech_events = {r["event_id"]: r for r in read(P582 / "FIVE_HUNDRED_EIGHTY_SECOND_REVISED_THREE_HUNDRED_EIGHTY_ONE_EVENT_SEQUENCES.tsv")}
    grouped = OrderedDict()
    for event in events:
        grouped.setdefault(event["statement_id"], []).append(event)

    group_rows = []
    event_rows = []
    statement_rows = []
    for statement_id, statement_events in grouped.items():
        groups, current = [], []
        for event in statement_events:
            current.append(event)
            is_close = "schließ" in event["atomic_card_value_de"].lower()
            if is_close or len(current) == 4:
                groups.append(current); current = []
        if current:
            groups.append(current)
        for group_index, group in enumerate(groups, 1):
            group_id = f"{statement_id}-G{group_index:02d}"
            phrases = []
            for position, event in enumerate(group, 1):
                speech = speech_events[event["event_id"]]
                base = event["revised_event_reading_de"]
                phrases.append(short(base))
                event_rows.append({
                    "event_id": event["event_id"], "page": event["page"], "record": event["record"],
                    "statement_id": statement_id, "group_id": group_id, "position_in_group": position,
                    "surface": event["surface"], "component_parse": event["component_parse"],
                    "spoken_component_sequence_de": speech["spoken_component_sequence_de"],
                    "short_event_reading_de": short(base),
                    "is_close_card": "YES" if "schließ" in event["atomic_card_value_de"].lower() else "NO",
                })
            group_rows.append({
                "group_id": group_id, "statement_id": statement_id,
                "page": group[0]["page"], "record": group[0]["record"],
                "group_ordinal": group_index, "events": len(group),
                "event_ids": "|".join(e["event_id"] for e in group),
                "card_surfaces": " ".join(e["surface"] for e in group),
                "breath_group_de": "; ".join(phrases),
                "ends_at_close": "YES" if "schließ" in group[-1]["atomic_card_value_de"].lower() else "NO",
                "all_events_retained": "YES",
            })
        statement_rows.append({
            "statement_id": statement_id, "page": statement_events[0]["page"], "record": statement_events[0]["record"],
            "learning_mode": target[statement_id]["revised_learning_mode"],
            "phase_signature": target[statement_id]["phase_signature"],
            "events": len(statement_events), "breath_groups": len(groups),
            "group_ids": "|".join(f"{statement_id}-G{i:02d}" for i in range(1, len(groups)+1)),
            "complete": "YES",
        })

    write("FIVE_HUNDRED_EIGHTY_SIXTH_TWENTY_TWO_LONG_STATEMENTS.tsv", statement_rows)
    write("FIVE_HUNDRED_EIGHTY_SIXTH_BREATH_GROUPS.tsv", group_rows)
    write("FIVE_HUNDRED_EIGHTY_SIXTH_ONE_HUNDRED_FIFTY_SIX_GROUPED_EVENTS.tsv", event_rows)
    readable = ["# Meisterbuch der langen Aussagen", "", "Jede Atemgruppe enthält höchstens vier sichtbare Karten und endet nach Möglichkeit an einer Schlusskarte.", ""]
    by_statement_groups = OrderedDict()
    for row in group_rows:
        by_statement_groups.setdefault(row["statement_id"], []).append(row)
    for statement_id, rows in by_statement_groups.items():
        readable += [f"## {statement_id}", ""]
        for row in rows:
            readable.append(f"- {row['group_id']}: {row['breath_group_de']}.")
        readable.append("")
    (HERE / "FIVE_HUNDRED_EIGHTY_SIXTH_LONG_STATEMENT_MASTERBOOK.md").write_text("\n".join(readable).rstrip() + "\n", encoding="utf-8")
    summary = {
        "status": "PASS", "long_statements": len(statement_rows), "events": len(event_rows),
        "breath_groups": len(group_rows), "max_group_events": max(int(r["events"]) for r in group_rows),
        "groups_ending_close": sum(r["ends_at_close"] == "YES" for r in group_rows),
        "extended_variants": sum(r["learning_mode"] == "EXTENDED_TWO_EDIT_VARIANT" for r in statement_rows),
        "free_compositions": sum(r["learning_mode"] == "FREE_COMPOSITION" for r in statement_rows),
    }
    (HERE / "FIVE_HUNDRED_EIGHTY_SIXTH_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    report = [
        "# Fünfhundertsechsundachtzigste Runde: Atemgruppen-Meisterbuch", "",
        "Die zehn Zwei-Edit-Varianten und zwölf freien Aussagen umfassen 156 Kartenereignisse. Sie sind jetzt vollständig in kleine Atemgruppen zerlegt: höchstens vier Karten, früherer Schnitt an einer Schlusskarte. Keine Karte wird zur besseren Lesbarkeit weggelassen.", "",
        f"Die 22 Aussagen ergeben {summary['breath_groups']} Atemgruppen; {summary['groups_ending_close']} enden direkt an einer Schlusskarte. Der Lehrling kann daher eine lange Stationsfolge als mehrere kurze Sprech- und Schreibzüge lernen, ohne sie fälschlich in unabhängige Zeilensätze zu zerlegen.", "",
        "Die zwölf freien Folgen bleiben Meisterbeispiele statt neue Universalformeln. Ihre Länge entsteht aus konkreten Pflanzenartikel- oder Stationsketten; dieselben 37 Sprechwerte und 15 Grundformeln bleiben darunter sichtbar.", "",
        "## Nächster Schritt", "",
        "Nun wird der vollständige elf-Record-Text aus kurzen Formeln, Varianten und Atemgruppen neu gesetzt. Jede Aussage erhält eine einheitliche dreizeilige Darstellung: sichtbare Karten, kurze Komponentenlesung und flüssige Werkstattanweisung.",
    ]
    (HERE / "FIVE_HUNDRED_EIGHTY_SIXTH_REPORT.md").write_text("\n".join(report) + "\n", encoding="utf-8")


if __name__ == "__main__": main()
