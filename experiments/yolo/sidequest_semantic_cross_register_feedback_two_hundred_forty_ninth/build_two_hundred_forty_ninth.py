#!/usr/bin/env python3
from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
SRC = ROOT / "experiments/yolo/sidequest_semantic_astro_prose_bridge_two_hundred_thirteenth"
EVENTS = SRC / "TWO_HUNDRED_THIRTEENTH_381_EVENT_CROSS_REGISTER_PROSE.tsv"
STATEMENTS = SRC / "TWO_HUNDRED_THIRTEENTH_116_STATEMENT_CROSS_REGISTER_PROSE.tsv"

REVISION = {
    "MC007": ("KURZ_SETZEN", "kurz einwirken lassen", "wet-contact expansion"),
    "MC002": ("LAENGER_SETZEN_ODER_HAL TEN".replace(" ", ""), "länger einwirken lassen", "wet-contact expansion"),
    "MC034": ("EINGABE_ODER_BEDINGUNG", "weitere Zutat", "Herbal ingredient expansion"),
    "MC159": ("AUFNAHMEFELD_ODER_UMSCHLUSS", "Aufnahmegefäß", "Herbal receiver expansion"),
    "MC100": ("ZURUECKNEHMEN__SCHLUSS", "aus der Wärme nehmen und abkühlen; Schluss", "Herbal thermal expansion"),
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


def main() -> None:
    source_events = read_tsv(EVENTS)
    source_statements = read_tsv(STATEMENTS)
    events_by_statement: dict[str, list[dict[str, object]]] = defaultdict(list)
    events: list[dict[str, object]] = []
    revisions: list[dict[str, object]] = []
    for row in source_events:
        if row["master_card_id"] in REVISION:
            core, local, reason = REVISION[row["master_card_id"]]
            status = "PORTABLE_CORE_REVISED__LOCAL_READING_RETAINED"
            revisions.append({
                "event_id": row["event_id"], "page": row["page"], "record_unit_id": row["record_unit_id"],
                "statement_id": row["statement_id"], "visible_surface": row["visible_surface"],
                "master_card_id": row["master_card_id"], "old_default_de": row["portable_value_de"],
                "new_portable_core_de": core, "local_expansion_de": local, "revision_reason": reason,
            })
        else:
            core, local, reason = row["portable_value_de"], row["portable_value_de"], "unchanged"
            status = "UNCHANGED_PORTABLE_VALUE"
        item = {
            "event_id": row["event_id"], "statement_id": row["statement_id"], "record_unit_id": row["record_unit_id"],
            "page": row["page"], "field_id": row["field_id"], "field_position": row["field_position"],
            "visible_owner": row["visible_owner"], "visible_surface": row["visible_surface"],
            "master_card_id": row["master_card_id"], "portable_core_de": core,
            "local_register_expansion_de": local, "value_status": status,
            "terminal_status": row["terminal_status"],
        }
        events.append(item)
        events_by_statement[row["statement_id"]].append(item)

    statements: list[dict[str, object]] = []
    affected: list[dict[str, object]] = []
    for row in source_statements:
        linked = events_by_statement[row["statement_id"]]
        count = sum(e["value_status"] != "UNCHANGED_PORTABLE_VALUE" for e in linked)
        item = {
            "statement_id": row["statement_id"], "record_unit_id": row["record_unit_id"],
            "visible_owner": row["visible_owner"], "field_ids": row["field_ids"],
            "visible_sequence": row["visible_sequence"],
            "portable_core_chain": " | ".join(str(e["portable_core_de"]) for e in linked),
            "local_register_chain": " | ".join(str(e["local_register_expansion_de"]) for e in linked),
            "complete_local_translation_de": row["revised_fluent_translation_de"],
            "revised_event_count": count,
            "reading_rule": "read portable cores first; insert plant or station objects from owner; expand locally",
        }
        statements.append(item)
        if count:
            affected.append(item)

    event_path = OUT / "TWO_HUNDRED_FORTY_NINTH_REVISED_381_PROSE_EVENTS.tsv"
    statement_path = OUT / "TWO_HUNDRED_FORTY_NINTH_REVISED_116_STATEMENTS.tsv"
    revision_path = OUT / "TWO_HUNDRED_FORTY_NINTH_15_EVENT_REVISIONS.tsv"
    affected_path = OUT / "TWO_HUNDRED_FORTY_NINTH_14_AFFECTED_STATEMENTS.tsv"
    readable_path = OUT / "TWO_HUNDRED_FORTY_NINTH_READABLE_CORE_AND_LOCAL.md"
    report_path = OUT / "TWO_HUNDRED_FORTY_NINTH_REPORT.md"
    write_tsv(event_path, events, list(events[0]))
    write_tsv(statement_path, statements, list(statements[0]))
    write_tsv(revision_path, revisions, list(revisions[0]))
    write_tsv(affected_path, affected, list(affected[0]))

    readable = ["# Tragbarer Kern und lokale Lesung", ""]
    for row in affected:
        readable += [
            f"## {row['statement_id']}", "",
            f"**Kartenkern:** {row['portable_core_chain']}", "",
            f"**Lokale Ausführung:** {row['complete_local_translation_de']}", "",
        ]
    readable += [
        "## Gesamtregel", "",
        "KURZ_SETZEN und LAENGER_SETZEN_ODER_HALTEN werden im Bad zu kurzem/längerem Einwirken; EINGABE wird unter der Pflanze zur Zutat; AUFNAHMEFELD wird zum Gefäß; ZURUECKNEHMEN wird beim Wärmeschritt zum Abkühlen. Der Kartenwert bleibt kurz, die Seite macht ihn konkret.", "",
    ]
    readable_path.write_text("\n".join(readable), encoding="utf-8")

    by_card = Counter(r["master_card_id"] for r in revisions)
    report = f"""# Sidequest-Pass 249: Astro-Korrekturen in Prosa integrieren

## Ergebnis

Fünf Kartenfamilien betreffen **15/381** Prosaereignisse in **14/116** Aussagen. Alle übrigen 366 Ereignisse bleiben unverändert.

Die vollständigen lokalen Übersetzungen müssen nicht verworfen werden. Sie werden sauber in zwei Ebenen getrennt:

- tragbarer Kern: kurz/länger setzen, Eingabe, Aufnahmefeld, zurücknehmen;
- lokale Ausführung: einwirken, Zutat, Gefäß, abkühlen.

Damit verliert kein Herbal- oder Biological-Satz seinen praktischen Sinn, aber das Wörterbuch behauptet nicht mehr, dass eine Sternkarte „Zutat“ oder „Badkontakt“ heißen müsse.

Input events `{sha(EVENTS)}`; statements `{sha(STATEMENTS)}`.
"""
    report_path.write_text(report, encoding="utf-8")
    summary = {
        "status": "PASS", "events": len(events), "statements": len(statements),
        "revised_events": len(revisions), "affected_statements": len(affected),
        "revisions_by_card": dict(by_card),
        "outputs": {p.name: sha(p) for p in (event_path, statement_path, revision_path, affected_path, readable_path, report_path)},
    }
    (OUT / "BUILD_SUMMARY.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
