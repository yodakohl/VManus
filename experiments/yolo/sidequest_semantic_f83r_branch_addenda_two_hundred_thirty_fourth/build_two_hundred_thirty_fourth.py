#!/usr/bin/env python3
from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
EVENTS = ROOT / "experiments/yolo/sidequest_semantic_result_close_integration_two_hundred_twenty_first/TWO_HUNDRED_TWENTY_FIRST_381_EVENT_PROSE.tsv"
STATEMENTS = ROOT / "experiments/yolo/sidequest_semantic_result_close_integration_two_hundred_twenty_first/TWO_HUNDRED_TWENTY_FIRST_116_STATEMENT_PROSE.tsv"

FAMILIES = {
    "E362": "TRANSFER_CLOSE", "E363": "TRANSFER_CLOSE", "E364": "TARGET_SETTLE", "E365": "TARGET", "E366": "CONTINUE", "E367": "CONTINUED_OUTPUT", "E368": "TARGET_TRANSFER", "E369": "MEASURE", "E370": "CONTINUE", "E371": "END_STAGE", "E372": "TRANSFER",
    "E373": "COLLECTION_LONG", "E374": "ACTION_SHORT", "E375": "END_TARGET", "E376": "CONTINUE", "E377": "MEASURE", "E378": "CONTINUE", "E379": "INSERT", "E380": "REFERENT", "E381": "END_TARGET",
}

READINGS = {
    "B5-S001": "Danach den linken Endtransfer abschließen.",
    "B5-S002": "Den nächsten Posten in den linken Endweg einführen; Schluss.",
    "B5-S003": "Am Ziel absetzen und dorthin weiterleiten; den weiteren Abzug zum Ziel übertragen, auf Sollwert bringen, bis zur Endstufe fortsetzen und übergeben.",
    "B6-S001": "Am rechten Endknoten länger sammeln, kurz bearbeiten und zum Endposten weitergeben; auf Sollwert bringen und die Einlage als diesen Posten zum Endziel führen.",
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
    all_events = read(EVENTS)
    addenda = [row for row in all_events if row["record_unit_id"] in {"B5", "B6"}]
    left_parent = [row for row in all_events if row["event_id"] in {f"E{i:03d}" for i in range(338, 356)}]
    right_parent = [row for row in all_events if row["event_id"] in {f"E{i:03d}" for i in range(356, 362)}]
    left_ids = {row["master_card_id"] for row in left_parent}
    right_ids = {row["master_card_id"] for row in right_parent}

    event_rows: list[dict[str, object]] = []
    for row in addenda:
        branch = "LEFT_N6_TO_N8" if row["record_unit_id"] == "B5" else "RIGHT_N7_TO_N9"
        parent_ids = left_ids if row["record_unit_id"] == "B5" else right_ids
        event_rows.append({
            "event_id": row["event_id"],
            "record_unit_id": row["record_unit_id"],
            "statement_id": row["statement_id"],
            "visible_surface": row["visible_surface"],
            "master_card_id": row["master_card_id"],
            "portable_value_de": row["portable_value_de"],
            "component_family": FAMILIES[row["event_id"]],
            "branch_lineage": branch,
            "exact_card_in_parent_branch": "YES" if row["master_card_id"] in parent_ids else "NO",
            "addendum_role": "OPERATIONAL_CONTINUATION" if row["record_unit_id"] == "B5" else "ENDPOINT_SUMMARY",
        })
    write(OUT / "TWO_HUNDRED_THIRTY_FOURTH_TWENTY_ADDENDUM_EVENTS.tsv", event_rows)

    statement_source = {row["statement_id"]: row for row in read(STATEMENTS)}
    statement_rows: list[dict[str, object]] = []
    for statement_id in ("B5-S001", "B5-S002", "B5-S003", "B6-S001"):
        source = statement_source[statement_id]
        rows = [row for row in event_rows if row["statement_id"] == statement_id]
        statement_rows.append({
            "statement_id": statement_id,
            "branch_lineage": rows[0]["branch_lineage"],
            "visible_sequence": source["visible_sequence"],
            "event_ids": "|".join(str(row["event_id"]) for row in rows),
            "literal_card_reading": source["r221_literal_card_reading"],
            "revised_addendum_reading_de": READINGS[statement_id],
        })
    write(OUT / "TWO_HUNDRED_THIRTY_FOURTH_FOUR_REVISED_STATEMENTS.tsv", statement_rows)

    comparison_rows = [
        {
            "addendum": "B5_LEFT",
            "parent_branch": "N6_LEFT_TEMPER_RESULT_DRAIN",
            "addendum_events": 11,
            "exact_parent_card_occurrences": sum(row["exact_card_in_parent_branch"] == "YES" for row in event_rows if row["record_unit_id"] == "B5"),
            "exact_parent_card_ids": "MC039|MC074|MC153",
            "component_continuities": "TRANSFER|TARGET|CONTINUE|OUTPUT|MEASURE|END_STAGE",
            "selected_relation": "LEFT_BRANCH_OPERATIONAL_CONTINUATION",
        },
        {
            "addendum": "B6_RIGHT",
            "parent_branch": "N7_RIGHT_PORTION_DISTRIBUTE_SETTLE",
            "addendum_events": 9,
            "exact_parent_card_occurrences": sum(row["exact_card_in_parent_branch"] == "YES" for row in event_rows if row["record_unit_id"] == "B6"),
            "exact_parent_card_ids": "NONE",
            "component_continuities": "COLLECTION_GRADE|TARGET_TO_END_TARGET|PORTION_TO_MEASURE_AND_INSERT",
            "selected_relation": "RIGHT_BRANCH_ENDPOINT_SUMMARY",
        },
    ]
    write(OUT / "TWO_HUNDRED_THIRTY_FOURTH_LEFT_RIGHT_LINEAGE.tsv", comparison_rows)

    readable = [
        "# B5 und B6 als Lehrlingsnachträge",
        "",
        "## B5 — linker Abschlussweg",
        "",
        "**Danach den linken Endtransfer abschließen. Den nächsten Posten in den linken Endweg einführen. Am Ziel absetzen und dorthin weiterleiten; den weiteren Abzug zum Ziel übertragen, auf Sollwert bringen, bis zur Endstufe fortsetzen und übergeben.**",
        "",
        "B5 ist eine echte Fortsetzung des linken Arms: `weiter`, `Sollwert` und `überführen` sind dieselben Karten wie im Elternzweig; Ziel, Abzug und Endstufe spezialisieren dessen Abschluss.",
        "",
        "## B6 — rechter Abschlussweg",
        "",
        "**Am rechten Endknoten länger sammeln, kurz bearbeiten und zum Endposten weitergeben; auf Sollwert bringen und die Einlage als diesen Posten zum Endziel führen.**",
        "",
        "B6 wiederholt keine exakte N7-Karte. Es verlängert aber dessen Komposition: aus kurzer wird lange Sammlung, aus Ziel wird Endposten/Endziel, und der weitere Anteil wird als Sollwert plus Einlage gebucht. B6 ist daher eine Abschlusszusammenfassung, keine wörtliche Wiederholung.",
        "",
        "Die beiden Nachträge sprechen dafür, dass ein Lehrling die zwei sichtbaren Endarme getrennt adressieren konnte: links eine Folge von Transfer und Abzug, rechts Sammlung und endgültige Zuweisung.",
    ]
    (OUT / "TWO_HUNDRED_THIRTY_FOURTH_READABLE_BRANCH_ADDENDA.md").write_text("\n".join(readable).rstrip() + "\n", encoding="utf-8")

    report = [
        "# Pass 234 — B5/B6 als linke und rechte Nachträge",
        "",
        "Die 20 Ereignisse von B5/B6 teilen sich asymmetrisch. B5 hat vier Vorkommen von drei exakten Karten aus dem linken Elternarm und setzt dessen Transfer-/Abzugslogik fort. B6 hat keine exakte Kartenwiederholung aus N7, übernimmt aber dessen drei semantischen Achsen als graduierte Abschlussfassung.",
        "",
        "Damit wird der Mehrschreiber-Mechanismus konkreter: Ein Nachtrag kann entweder bekannte Karten wiederverwenden (B5) oder dieselbe Slotkomposition mit anderen gelernten Karten füllen (B6). Beide bleiben leicht lehrbar, obwohl sie nicht dasselbe Vokabular benutzen.",
        "",
        "Nächster Schritt: aus der kompletten f83r-Lesung eine kurze Schreiberanweisung rekonstruieren — welche Schritte müsste ein Meister diktieren, damit ein Lehrling genau diese Karte/Owner-Folge erzeugt?",
    ]
    (OUT / "TWO_HUNDRED_THIRTY_FOURTH_REPORT.md").write_text("\n".join(report).rstrip() + "\n", encoding="utf-8")
    summary = {
        "event_source_sha256": hashlib.sha256(EVENTS.read_bytes()).hexdigest(),
        "statement_source_sha256": hashlib.sha256(STATEMENTS.read_bytes()).hexdigest(),
        "events": len(event_rows),
        "statements": len(statement_rows),
        "b5_events": sum(row["record_unit_id"] == "B5" for row in event_rows),
        "b6_events": sum(row["record_unit_id"] == "B6" for row in event_rows),
        "b5_exact_parent_occurrences": comparison_rows[0]["exact_parent_card_occurrences"],
        "b6_exact_parent_occurrences": comparison_rows[1]["exact_parent_card_occurrences"],
        "sealed_pages_accessed": False,
    }
    (OUT / "BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
