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

INTERPRETATIONS = {
    "E021": ("REFERENT_RETURN", "Diesen Posten auf Sollwert setzen und als denselben Posten weiterführen."),
    "E027": ("CONTINUATION_RETURN", "Weiter im selben Ansatz, dann den Fortgang wieder aufnehmen."),
    "E035": ("REFERENT_RETURN", "Diesen Posten durch die Bearbeitungsstufe führen und als denselben Posten halten."),
    "E048": ("REFERENT_RETURN", "Diesen Posten bearbeiten und als denselben Posten weiterführen."),
    "E116": ("VALUE_RETURN", "Den Sollwert während des langen Zieleinsatzes beibehalten."),
    "E133": ("CONTINUATION_RETURN", "Den laufenden Gang kurz wärmen und danach denselben Gang fortsetzen."),
    "E198": ("ACTION_REPEAT_FROM_SOURCE", "Einen Anteil zugeben, davon nehmen und denselben Zugabegang wiederholen."),
    "E232": ("REFERENT_RETURN", "Diesen Bestand auf Sollwert setzen und als denselben Bestand weiterführen."),
    "E376": ("CONTINUATION_RETURN", "Den laufenden Gang auf Sollwert bringen und danach fortsetzen."),
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
    by_statement: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in events:
        by_statement[row["statement_id"]].append(row)
    rows: list[dict[str, object]] = []
    for statement_id, statement_events in by_statement.items():
        for start in range(len(statement_events) - 2):
            a, b, c = statement_events[start:start + 3]
            if a["master_card_id"] != c["master_card_id"]:
                continue
            category, reading = INTERPRETATIONS[a["event_id"]]
            rows.append({
                "aba_id": f"ABA{len(rows) + 1:02d}",
                "statement_id": statement_id,
                "record_unit_id": a["record_unit_id"],
                "page": a["page"],
                "visible_owner": a["visible_owner"],
                "start_event": a["event_id"],
                "outer_master_card_id": a["master_card_id"],
                "middle_master_card_id": b["master_card_id"],
                "visible_window": f"{a['visible_surface']} {b['visible_surface']} {c['visible_surface']}",
                "value_window": f"{a['portable_value_de']} > {b['portable_value_de']} > {c['portable_value_de']}",
                "return_category": category,
                "selected_working_reading_de": reading,
                "outer_identity_exact": "YES",
            })
    write(OUT / "TWO_HUNDRED_TWENTY_FOURTH_NINE_ABA_WINDOWS.tsv", rows)

    construction = [{
        "construction_id": "ABA_RETURN_FRAME",
        "surface_schema": "A B A",
        "workshop_rule_de": "A vor B aktivieren, B anwenden, danach zu exakt demselben A zurückkehren",
        "referent_return_occurrences": sum(row["return_category"] == "REFERENT_RETURN" for row in rows),
        "continuation_return_occurrences": sum(row["return_category"] == "CONTINUATION_RETURN" for row in rows),
        "value_return_occurrences": sum(row["return_category"] == "VALUE_RETURN" for row in rows),
        "action_repeat_occurrences": sum(row["return_category"] == "ACTION_REPEAT_FROM_SOURCE" for row in rows),
        "total_occurrences": len(rows),
        "meaning_de": "äußeren Referenten, Wert oder Gang über die mittlere Spezifikation hinweg beibehalten oder wiederaufnehmen",
    }]
    write(OUT / "TWO_HUNDRED_TWENTY_FOURTH_ABA_CONSTRUCTION_ENTRY.tsv", construction)

    lines = [
        "# A–B–A als Rückkehrrahmen",
        "",
        "Lehrregel: **A aktivieren, B darauf anwenden, danach exakt dasselbe A wiederaufnehmen.**",
        "",
        "Die äußere Karte ist in allen neun Fenstern nicht bloß ähnlich, sondern dieselbe normalisierte Karte. Die Rahmenfunktion kann Referent, laufenden Gang, Sollwert oder wiederholte Handlung erhalten.",
        "",
    ]
    for row in rows:
        lines.extend([
            f"## {row['aba_id']} · {row['statement_id']}",
            "",
            f"`{row['visible_window']}` → **{row['value_window']}**",
            "",
            row["selected_working_reading_de"],
            "",
        ])
    lines.extend([
        "## Konsequenz für Y–AIIN–Y",
        "",
        "Die zwei Y–AIIN–Y-Fälle sind keine isolierte Gleichmengenformel. Sie gehören zu einer größeren Werkstattkonvention: die äußere Karte bleibt über die mittlere Spezifikation aktiv. Lokal kann daraus Gleichbehandlung folgen, doch die allgemeine Bedeutung ist Rückkehr zum selben Referenten.",
    ])
    (OUT / "TWO_HUNDRED_TWENTY_FOURTH_ABA_RETURN_RULE.md").write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")

    summary = {
        "source_sha256": hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
        "statements_scanned": len(by_statement),
        "aba_occurrences": len(rows),
        "distinct_aba_value_patterns": len({row["value_window"] for row in rows}),
        "distinct_outer_cards": len({row["outer_master_card_id"] for row in rows}),
        "pages": sorted({row["page"] for row in rows}),
        "sealed_pages_accessed": False,
    }
    (OUT / "BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
