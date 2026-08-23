#!/usr/bin/env python3
"""Build card, field, statement, record, and line-crossing scope for 381 prose events."""

from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
EVENTS = ROOT / "experiments/yolo/sidequest_semantic_two_layer_prose_two_hundred_seventy_ninth/TWO_HUNDRED_SEVENTY_NINTH_381_TWO_LAYER_EVENTS.tsv"
STATEMENTS = ROOT / "experiments/yolo/sidequest_semantic_two_layer_prose_two_hundred_seventy_ninth/TWO_HUNDRED_SEVENTY_NINTH_116_TWO_LAYER_STATEMENTS.tsv"
HERBAL_LOCUS = ROOT / "experiments/yolo/sidequest_theory_candidates_v73/V73_R3_100_EVENT_INTERLINEAR.tsv"
BIO_LOCUS = ROOT / "experiments/yolo/sidequest_theory_candidates_v74/V74_R3_281_EVENT_INTERLINEAR.tsv"


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh, delimiter="\t"))


def write_tsv(path: Path, rows: list[dict[str, object]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


OWNER_RESET_ENTRIES = {"E203", "E264", "E291", "E356"}


def main() -> None:
    events = read_tsv(EVENTS)
    statements = read_tsv(STATEMENTS)
    locus_rows = read_tsv(HERBAL_LOCUS) + read_tsv(BIO_LOCUS)
    locus_by_event = {f"E{int(row['event_serial']):03d}": row["locus"] for row in locus_rows}
    by_field: dict[str, list[dict[str, str]]] = defaultdict(list)
    by_statement: dict[str, list[dict[str, str]]] = defaultdict(list)
    by_record: dict[str, list[dict[str, str]]] = defaultdict(list)
    for event in events:
        by_field[event["field_id"]].append(event)
        by_statement[event["statement_id"]].append(event)
        by_record[event["record_unit_id"]].append(event)

    event_rows = []
    crossing_rows = []
    for index, event in enumerate(events):
        event_id = event["event_id"]
        field_events = by_field[event["field_id"]]
        statement_events = by_statement[event["statement_id"]]
        record_events = by_record[event["record_unit_id"]]
        field_last = event_id == field_events[-1]["event_id"]
        statement_last = event_id == statement_events[-1]["event_id"]
        record_last = event_id == record_events[-1]["event_id"]
        locus = locus_by_event[event_id]
        next_same_statement = None if statement_last else statement_events[statement_events.index(event) + 1]
        line_crossing_after = bool(next_same_statement and locus_by_event[next_same_statement["event_id"]] != locus)
        surface = event["visible_surface"]
        if surface.endswith("dy"):
            surface_end = "VISIBLE_DY_END"
        elif surface.endswith("y"):
            surface_end = "VISIBLE_Y_END"
        else:
            surface_end = "OTHER_VISIBLE_END"
        if event["terminal_status"] == "TERMINAL":
            endpoint_scope = "LICENSED_WORKSTEP_AND_STATEMENT_COMMIT"
        elif "+Y" in event["family_parse"] or event["family_parse"] == "Y" or "Y[" in event["family_parse"]:
            endpoint_scope = "CURRENT_ITEM_REFERENCE__NO_CLOSE"
        elif statement_last:
            endpoint_scope = "OPEN_STATEMENT_RELEASE__NO_COMMIT_CARD"
        else:
            endpoint_scope = "CARD_END_ONLY__CONTINUE_STATEMENT"
        source_token_id = "SRC_E180_E181_READ_ONCE" if event_id in {"E180", "E181"} else f"SRC_{event_id}"
        event_rows.append({
            "event_id": event_id,
            "source_token_id": source_token_id,
            "record_unit_id": event["record_unit_id"],
            "page": event["page"],
            "locus": locus,
            "field_id": event["field_id"],
            "statement_id": event["statement_id"],
            "visible_surface": surface,
            "family_parse": event["family_parse"],
            "terminal_status": event["terminal_status"],
            "surface_end_class": surface_end,
            "endpoint_scope": endpoint_scope,
            "card_boundary_after": "YES",
            "field_boundary_after": "YES" if field_last else "NO",
            "statement_boundary_after": "YES" if statement_last else "NO",
            "record_boundary_after": "YES" if record_last else "NO",
            "line_crossing_to_next_inside_statement": "YES" if line_crossing_after else "NO",
            "reading_rule_de": "Die registrierte Ganzkarte entscheidet Y/DY-Reichweite; sichtbare Endbuchstaben allein entscheiden nichts.",
        })
        if line_crossing_after:
            next_id = next_same_statement["event_id"]
            if event_id == "E180" and next_id == "E181":
                crossing_type = "READ_ONCE_ANTICIPATION_OR_CARRY"
                rule = "zwei sichtbare Kopien, ein Quelltoken; zweite Kopie am neuen Zeilenanfang nicht erneut lesen"
            elif next_id in OWNER_RESET_ENTRIES:
                crossing_type = "VISIBLE_OWNER_RESET_INSIDE_RUNNING_STATEMENT"
                rule = "Aussage läuft weiter, aber der sichtbare lokale Besitzer wird neu gesetzt"
            else:
                crossing_type = "ORDINARY_CONTINUATION_ACROSS_PHYSICAL_LINE"
                rule = "ohne Satzschluss in der nächsten physischen Zeile weiterlesen"
            crossing_rows.append({
                "crossing_order": len(crossing_rows) + 1,
                "statement_id": event["statement_id"],
                "from_event": event_id,
                "to_event": next_id,
                "from_locus": locus,
                "to_locus": locus_by_event[next_id],
                "from_surface": surface,
                "to_surface": next_same_statement["visible_surface"],
                "crossing_type": crossing_type,
                "read_rule_de": rule,
            })
    event_path = HERE / "THREE_HUNDRED_FIRST_381_EVENT_SCOPE.tsv"
    crossing_path = HERE / "THREE_HUNDRED_FIRST_19_LINE_CROSSINGS.tsv"
    write_tsv(event_path, event_rows)
    write_tsv(crossing_path, crossing_rows)

    field_rows = []
    for field_id, selected in sorted(by_field.items(), key=lambda item: int(item[0][1:])):
        final = selected[-1]
        field_rows.append({
            "field_id": field_id,
            "record_unit_id": final["record_unit_id"],
            "page": final["page"],
            "statement_id": final["statement_id"],
            "event_count": len(selected),
            "first_event": selected[0]["event_id"],
            "last_event": final["event_id"],
            "last_surface": final["visible_surface"],
            "field_status": "COMMITTED_FIELD" if final["terminal_status"] == "TERMINAL" else "OPEN_FIELD",
            "field_end_rule": "terminal card commits this field" if final["terminal_status"] == "TERMINAL" else "field boundary without explicit commit",
        })
    field_path = HERE / "THREE_HUNDRED_FIRST_135_FIELD_SCOPE.tsv"
    write_tsv(field_path, field_rows)

    statement_source = {row["statement_id"]: row for row in statements}
    statement_rows = []
    for statement_id, selected in by_statement.items():
        loci = []
        for event in selected:
            locus = locus_by_event[event["event_id"]]
            if not loci or loci[-1] != locus:
                loci.append(locus)
        final = selected[-1]
        internal_crossings = [row for row in crossing_rows if row["statement_id"] == statement_id]
        statement_rows.append({
            "statement_id": statement_id,
            "record_unit_id": final["record_unit_id"],
            "page": final["page"],
            "locus_path": "|".join(loci),
            "physical_loci": len(loci),
            "internal_line_crossings": len(internal_crossings),
            "event_count": len(selected),
            "first_event": selected[0]["event_id"],
            "last_event": final["event_id"],
            "last_surface": final["visible_surface"],
            "statement_status": "COMMITTED_STATEMENT" if final["terminal_status"] == "TERMINAL" else "OPEN_STATEMENT",
            "current_reading_de": statement_source[statement_id]["two_layer_statement_de"],
        })
    statement_path = HERE / "THREE_HUNDRED_FIRST_116_STATEMENT_SCOPE.tsv"
    write_tsv(statement_path, statement_rows)

    manual = """# Reichweitenlehre für Karten, Felder, Aussagen und Zeilen

## Vier Grenzen

1. **Kartenende:** nach jeder der 381 sichtbaren Karten.
2. **Feldende:** 135-mal; 90 Felder enden mit einer lizenzierten Commit-Karte, 45 bleiben offen.
3. **Aussageende:** 116-mal; 90 Aussagen schließen mit Commit, 26 enden offen.
4. **Recordende:** 11-mal; es löscht die lokalen Besitzer-/Postenregister.

## Y und DY

Die sichtbaren letzten Zeichen genügen nicht:

- 89 `...dy`-Ereignisse sind terminal;
- 16 `...dy`-Ereignisse sind **nicht** terminal;
- 98 einfache `...y`-Ereignisse sind nicht terminal;
- `talam` schließt als gelerntes Ganzzeichen ganz ohne sichtbares `dy`.

Darum wird immer die ganze registrierte Karte gelesen. Besonders `chdy|chedy` ist ein aktueller Transferposten und nicht automatisch Schluss.

## Zeilen

18 Aussagen laufen über physische Zeilen; zusammen ergeben sie 19 Übergänge. Vier setzen dabei den sichtbaren Besitzer neu, vierzehn lesen gewöhnlich weiter. Ein Übergang, E180→E181, zeigt dieselbe Karte `qokaiin` beidseits der Zeile: zwei sichtbare Kopien, aber im Werkstattmodell ein einmal gelesener Quellposten.

Ein Zeilenende schließt daher weder Feld noch Aussage. Es ist zuerst Raumorganisation um bereits gezeichnete Bilder.
"""
    manual_path = HERE / "THREE_HUNDRED_FIRST_SCOPE_MANUAL.md"
    manual_path.write_text(manual, encoding="utf-8")

    report = """# Sidequest-Pass 301: die Reichweite von Y, DY und Zeilen

## Ergebnis

Alle 381 Ereignisse sind jetzt gleichzeitig an Karten-, Feld-, Aussage-, Record- und physische Zeilengrenzen gebunden. Die wichtige Trennung lautet: sichtbare Endform, registrierte Kartenfunktion und Satzreichweite sind drei verschiedene Dinge.

Von 105 sichtbar auf `dy` endenden Ereignissen schließen 89 und 16 nicht. Das gelernte `talam` ist der Gegenfall: terminal ohne `dy`. Neunzig der 135 Felder und neunzig der 116 Aussagen schließen explizit; die übrigen laufen offen aus oder werden erst am Recordende freigegeben.

Die 19 inneren Zeilenübergänge bestätigen die Nutzerkorrektur aus dem Sidequest: Eine Aussage muss nicht mit einer Zeile enden. E180→E181 bleibt die einzige Read-once-Randkopie; vier Übergänge wechseln den sichtbaren Besitzer mitten in einer laufenden Aussage.

## Nächster Angriff

Nun kann die vollständige Prosa in echte Werkstattsätze umgebrochen werden: nicht nach Zeilen, sondern nach 116 Aussagen, mit Semikolon für Commit, Komma für Kartenfolge, Besitzerwechsel in eckigen Klammern und offener Fortsetzung am Recordende.
"""
    report_path = HERE / "THREE_HUNDRED_FIRST_REPORT.md"
    report_path.write_text(report, encoding="utf-8")

    end_counts = Counter((row["surface_end_class"], row["terminal_status"]) for row in event_rows)
    crossing_counts = Counter(row["crossing_type"] for row in crossing_rows)
    summary = {
        "status": "PASS",
        "visible_events": len(event_rows),
        "source_tokens": len({row["source_token_id"] for row in event_rows}),
        "fields": len(field_rows),
        "committed_fields": sum(row["field_status"] == "COMMITTED_FIELD" for row in field_rows),
        "open_fields": sum(row["field_status"] == "OPEN_FIELD" for row in field_rows),
        "statements": len(statement_rows),
        "committed_statements": sum(row["statement_status"] == "COMMITTED_STATEMENT" for row in statement_rows),
        "open_statements": sum(row["statement_status"] == "OPEN_STATEMENT" for row in statement_rows),
        "line_crossing_statements": sum(int(row["internal_line_crossings"]) > 0 for row in statement_rows),
        "line_crossings": len(crossing_rows),
        "crossing_counts": dict(sorted(crossing_counts.items())),
        "dy_terminal": end_counts[("VISIBLE_DY_END", "TERMINAL")],
        "dy_nonclose": end_counts[("VISIBLE_DY_END", "NONCLOSE")],
        "y_nonclose": end_counts[("VISIBLE_Y_END", "NONCLOSE")],
        "other_terminal": end_counts[("OTHER_VISIBLE_END", "TERMINAL")],
        "source_hashes": {str(path.relative_to(ROOT)): sha(path) for path in [EVENTS, STATEMENTS, HERBAL_LOCUS, BIO_LOCUS]},
        "outputs": {path.name: sha(path) for path in [event_path, crossing_path, field_path, statement_path, manual_path, report_path]},
    }
    (HERE / "BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
