#!/usr/bin/env python3
from __future__ import annotations

import csv
import hashlib
import json
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
SOURCE = ROOT / "experiments/yolo/sidequest_semantic_result_close_integration_two_hundred_twenty_first/TWO_HUNDRED_TWENTY_FIRST_381_EVENT_PROSE.tsv"

DECISIONS = {
    "E020": ("OPEN_SAME_FIELD_PAIR", "PAIR_TWO_REFERENTS", "dieser und dieser Posten", 2),
    "E033": ("OPEN_SAME_FIELD_PAIR", "PAIR_TWO_SETTINGS", "erster und zweiter Ansatz", 2),
    "E137": ("ADJACENT_CLOSED_FIELD_REPEAT", "REPEAT_COMPLETE_OPERATION", "kurz einwirken; zweimal", 2),
    "E143": ("ADJACENT_CLOSED_FIELD_REPEAT", "REPEAT_COMPLETE_OPERATION", "Waschgang; zweimal", 2),
    "E180": ("OPEN_CROSS_LINE_CARRY", "READ_ONCE_CARRY", "bemessen; über die Zeile fortgetragen", 1),
    "E330": ("ADJACENT_CLOSED_FIELD_REPEAT", "REPEAT_COMPLETE_OPERATION", "durchlassen; zweimal", 2),
}


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(path: Path, rows: list[dict[str, object]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    events = read(SOURCE)
    by_record: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in events:
        by_record[row["record_unit_id"]].append(row)
    rows: list[dict[str, object]] = []
    for record, record_events in by_record.items():
        for index in range(len(record_events) - 1):
            first, second = record_events[index:index + 2]
            if first["master_card_id"] != second["master_card_id"]:
                continue
            boundary, rule, reading, source_tokens = DECISIONS[first["event_id"]]
            rows.append({
                "duplicate_id": f"DUP{len(rows) + 1:02d}",
                "record_unit_id": record,
                "page": first["page"],
                "first_event": first["event_id"],
                "second_event": second["event_id"],
                "first_statement": first["statement_id"],
                "second_statement": second["statement_id"],
                "first_field": first["field_id"],
                "second_field": second["field_id"],
                "visible_pair": f"{first['visible_surface']} {second['visible_surface']}",
                "master_card_id": first["master_card_id"],
                "single_card_value_de": first["portable_value_de"],
                "first_terminal": first["terminal_status"],
                "second_terminal": second["terminal_status"],
                "boundary_class": boundary,
                "selected_rule": rule,
                "pair_reading_de": reading,
                "source_token_count": source_tokens,
            })
    write(OUT / "TWO_HUNDRED_TWENTY_SIXTH_SIX_DUPLICATE_PAIRS.tsv", rows)

    rules = [
        {"rule_order": 1, "boundary_class": "OPEN_SAME_FIELD_PAIR", "occurrences": 2, "source_token_rule": "2_VISIBLE_2_SOURCE", "workshop_reading_de": "zwei Posten oder Ansätze derselben Art setzen", "example": "dy chy = dieser und dieser Posten"},
        {"rule_order": 2, "boundary_class": "ADJACENT_CLOSED_FIELD_REPEAT", "occurrences": 3, "source_token_rule": "2_VISIBLE_2_SOURCE", "workshop_reading_de": "den vollständig geschlossenen Arbeitsgang ein zweites Mal ausführen", "example": "qokedy | qokedy = kurz einwirken, zweimal"},
        {"rule_order": 3, "boundary_class": "OPEN_CROSS_LINE_CARRY", "occurrences": 1, "source_token_rule": "2_VISIBLE_1_SOURCE", "workshop_reading_de": "offene Karte am neuen Zeilenanfang wiederholen und nur einmal lesen", "example": "qokaiin / qokaiin = eine fortgetragene Bemessung"},
    ]
    write(OUT / "TWO_HUNDRED_TWENTY_SIXTH_THREE_DUPLICATION_RULES.tsv", rules)

    lines = [
        "# Werkstattgrammatik der unmittelbaren Doppelung",
        "",
        "Die sechs recordintern benachbarten exakten Doppelkarten haben drei lesbare Funktionen, die an ihrer Grenze erkennbar sind.",
        "",
    ]
    for rule in rules:
        lines.extend([
            f"## {rule['rule_order']}. {rule['boundary_class']}",
            "",
            f"Regel: **{rule['workshop_reading_de']}**.",
            "",
            f"Beispiel: `{rule['example']}`.",
            "",
        ])
    lines.append("## Alle sechs Stellen")
    lines.append("")
    for row in rows:
        lines.append(f"- {row['duplicate_id']} {row['first_event']}–{row['second_event']} `{row['visible_pair']}` → {row['pair_reading_de']}")
    lines.extend([
        "",
        "## Folgerung für f10r",
        "",
        "`dy chy taiin shy` beginnt mit einer echten offenen Doppelung derselben Y-Karte. Die konkrete Lesung kann daher lauten: „dieser und dieser Posten; den folgenden auf Sollwert setzen und als aktiven Posten halten“. Die Mehrzahl stammt aus Y–Y, nicht aus AIIN.",
    ])
    (OUT / "TWO_HUNDRED_TWENTY_SIXTH_DUPLICATION_MANUAL.md").write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")

    summary = {
        "source_sha256": hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
        "records_scanned": len(by_record),
        "adjacent_exact_duplicates": len(rows),
        "open_same_field_pairs": sum(row["boundary_class"] == "OPEN_SAME_FIELD_PAIR" for row in rows),
        "closed_field_repeats": sum(row["boundary_class"] == "ADJACENT_CLOSED_FIELD_REPEAT" for row in rows),
        "cross_line_carries": sum(row["boundary_class"] == "OPEN_CROSS_LINE_CARRY" for row in rows),
        "visible_tokens": len(rows) * 2,
        "source_tokens": sum(int(row["source_token_count"]) for row in rows),
        "sealed_pages_accessed": False,
    }
    (OUT / "BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
