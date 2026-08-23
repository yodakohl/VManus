#!/usr/bin/env python3
"""Typeset all 116 fixed-page prose statements independently of physical lines."""

from __future__ import annotations

import csv
import hashlib
import json
import re
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
EVENTS = ROOT / "experiments/yolo/sidequest_semantic_two_layer_prose_two_hundred_seventy_ninth/TWO_HUNDRED_SEVENTY_NINTH_381_TWO_LAYER_EVENTS.tsv"
SOURCE_STATEMENTS = ROOT / "experiments/yolo/sidequest_semantic_two_layer_prose_two_hundred_seventy_ninth/TWO_HUNDRED_SEVENTY_NINTH_116_TWO_LAYER_STATEMENTS.tsv"
SCOPE_EVENTS = ROOT / "experiments/yolo/sidequest_semantic_endpoint_scope_three_hundred_first/THREE_HUNDRED_FIRST_381_EVENT_SCOPE.tsv"
SCOPE_STATEMENTS = ROOT / "experiments/yolo/sidequest_semantic_endpoint_scope_three_hundred_first/THREE_HUNDRED_FIRST_116_STATEMENT_SCOPE.tsv"
CROSSINGS = ROOT / "experiments/yolo/sidequest_semantic_endpoint_scope_three_hundred_first/THREE_HUNDRED_FIRST_19_LINE_CROSSINGS.tsv"


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh, delimiter="\t"))


def write(path: Path, rows: list[dict[str, object]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def clean_phrase(text: str) -> str:
    text = text.strip()
    text = re.sub(r"; (?:Schluss(?:; Arbeitsschritt festsetzen)?|Arbeitsschritt festsetzen)$", "", text)
    if not text:
        return text
    return text[0].lower() + text[1:]


def main() -> None:
    events = read(EVENTS)
    source_statements = {r["statement_id"]: r for r in read(SOURCE_STATEMENTS)}
    scope_events = {r["event_id"]: r for r in read(SCOPE_EVENTS)}
    scope_statements = {r["statement_id"]: r for r in read(SCOPE_STATEMENTS)}
    crossings = read(CROSSINGS)
    crossing_by_to = {r["to_event"]: r for r in crossings}
    by_statement: dict[str, list[dict[str, str]]] = defaultdict(list)
    by_record: dict[str, list[str]] = defaultdict(list)
    for event in events:
        by_statement[event["statement_id"]].append(event)
        if event["statement_id"] not in by_record[event["record_unit_id"]]:
            by_record[event["record_unit_id"]].append(event["statement_id"])

    output = []
    for statement_id, selected in by_statement.items():
        source = source_statements[statement_id]
        scope = scope_statements[statement_id]
        record_statements = by_record[source["record_unit_id"]]
        record_last = statement_id == record_statements[-1]
        visible_parts: list[str] = []
        german_parts: list[str] = []
        field_ids: list[str] = []
        source_tokens: list[str] = []
        owner_reset_count = 0
        carry_collapsed = 0
        previous_field = None
        for event in selected:
            event_id = event["event_id"]
            scope_event = scope_events[event_id]
            if event_id == "E181":
                carry_collapsed += 1
                continue
            field_changed = previous_field is not None and event["field_id"] != previous_field
            if field_changed:
                visible_parts.append("/")
                german_parts.append("/")
            crossing = crossing_by_to.get(event_id)
            if crossing and crossing["crossing_type"] == "VISIBLE_OWNER_RESET_INSIDE_RUNNING_STATEMENT":
                visible_parts.append("[OWNER↻]")
                german_parts.append("[neuer sichtbarer Besitzer]")
                owner_reset_count += 1
            surface = event["visible_surface"]
            gloss = clean_phrase(event["register_expansion_de"])
            if event_id == "E180":
                surface += "↷"
                gloss += " [einmal lesen; am nächsten Zeilenanfang nur wiederholt]"
            visible_parts.append(surface)
            german_parts.append(gloss)
            source_tokens.append(scope_event["source_token_id"])
            if event["field_id"] not in field_ids:
                field_ids.append(event["field_id"])
            previous_field = event["field_id"]

        status = scope["statement_status"]
        if status == "COMMITTED_STATEMENT":
            punctuation = ";"
            punctuation_class = "COMMIT_SEMICOLON"
        elif record_last:
            punctuation = " …"
            punctuation_class = "OPEN_RECORD_RELEASE"
        else:
            punctuation = " ↪"
            punctuation_class = "OPEN_TO_NEXT_STATEMENT"
        visible_text = " · ".join(visible_parts).replace(" · / · ", " / ").replace(" · [OWNER↻] · ", " [OWNER↻] ") + punctuation
        german_text = ", ".join(german_parts).replace(", /, ", " / ").replace(", [neuer sichtbarer Besitzer], ", " [neuer sichtbarer Besitzer] ") + punctuation
        output.append({
            "statement_id": statement_id,
            "record_unit_id": source["record_unit_id"],
            "page": source["page"],
            "owner_slot": source["owner_slot"],
            "locus_path": scope["locus_path"],
            "field_path": "|".join(field_ids),
            "visible_event_count": len(selected),
            "read_source_token_count": len(set(source_tokens)),
            "surface_punctuated": visible_text,
            "workshop_german_punctuated": german_text,
            "punctuation_class": punctuation_class,
            "physical_line_crossings_absorbed": scope["internal_line_crossings"],
            "owner_resets_marked": owner_reset_count,
            "read_once_duplicates_collapsed": carry_collapsed,
            "rule_de": "Punktuation folgt Aussage/Commit; / trennt offene Felder; Zeilenwechsel setzt kein Zeichen.",
        })

    table = HERE / "THREE_HUNDRED_SECOND_116_PUNCTUATED_STATEMENTS.tsv"
    write(table, output)

    headings = {
        "H1": "f10r · Pflanzenartikel I",
        "H2": "f10r · Pflanzenartikel II",
        "H3": "f11r · Pflanzenartikel",
        "H4": "f55v · Pflanzenartikel",
        "H5": "f56r · Pflanzenartikel",
        "B1": "f81v · Bad-/Waschregister",
        "B2": "f82r · lokale Bad-/Gefäßstationen",
        "B3": "f83r · Stationsregister I",
        "B4": "f83r · Stationsregister II",
        "B5": "f83r · technischer Nachtrag I",
        "B6": "f83r · technischer Nachtrag II",
    }
    lines = [
        "# Elf Records, nach Aussage statt nach physischer Zeile gesetzt",
        "",
        "Legende: `·` Kartenfolge; `/` offenes Feld; `;` Commit; `↪` offene Fortsetzung; `…` offenes Recordende; `[OWNER↻]` sichtbarer Besitzerwechsel; `↷` einmal gelesene Randkopie.",
        "",
    ]
    for record_id, statement_ids in by_record.items():
        lines += [f"## {record_id} — {headings[record_id]}", ""]
        for statement_id in statement_ids:
            row = next(r for r in output if r["statement_id"] == statement_id)
            lines += [f"**{statement_id} · Karten:** {row['surface_punctuated']}", "", f"**Werkstattlektüre:** {row['workshop_german_punctuated']}", ""]
    edition = HERE / "THREE_HUNDRED_SECOND_ELEVEN_RECORD_PUNCTUATED_EDITION.md"
    edition.write_text("\n".join(lines), encoding="utf-8")

    manual_text = """# Interpunktionsblatt der Werkstatt

Die Manuskriptzeile bleibt eine Raumzeile. Der Lehrling setzt beim Rücklesen fünf andere Zeichen:

1. `·` trennt gelernte Karten innerhalb desselben offenen Feldes.
2. `/` trennt zwei Felder, ohne daraus einen Satzschluss zu erfinden.
3. `;` steht nur nach einer als Ganzkarte lizenzierten Commit-Karte.
4. `↪` hält eine offene Aussage zum folgenden Werkstattschritt hin offen; `…` gibt sie am Recordrand ungeschlossen frei.
5. `[OWNER↻]` setzt mitten in einer Aussage den sichtbaren Bildbesitzer neu. `↷` liest E180/E181 nur einmal.

Damit können alle 116 Aussagen ohne die physischen Zeilenumbrüche gesetzt werden. Die Ausgabe übersetzt weiterhin die arbeitsteiligen Kartenwerte; sie behauptet keine historische Satzzeichenform des Manuskripts.
"""
    manual = HERE / "THREE_HUNDRED_SECOND_PUNCTUATION_MANUAL.md"
    manual.write_text(manual_text, encoding="utf-8")

    counts = Counter(r["punctuation_class"] for r in output)
    report_text = f"""# Sidequest-Pass 302: vollständige Aussage-Interpunktion

## Ergebnis

Alle 116 Prosaaussagen sind nun als elf fortlaufende Records gesetzt, ohne einen physischen Zeilenwechsel als Satzende zu behandeln. Die Ausgabe enthält {counts['COMMIT_SEMICOLON']} Commit-Semikolons, {counts['OPEN_TO_NEXT_STATEMENT']} offene Weiterführungen und {counts['OPEN_RECORD_RELEASE']} offene Recordfreigaben. Neunzehn physische Zeilenübergänge verschwinden aus der Syntax; vier echte Besitzerwechsel bleiben als Klammer sichtbar. E180/E181 erscheint sichtbar zweimal, wird aber mit `↷` nur einmal gelesen.

Das Resultat ist erheblich lesbarer als die alte Zeilenfolge: Karten, Felder, Aussagen und Bildbesitzer haben nun verschiedene, konstant verwendete Zeichen. Der nächste sinnvolle Pass ist eine flüssige deutsche Werkstattausgabe, die diese feste Gliederung beibehält, aber die noch telegrammartige Kartenfolge in kurze Imperativsätze umstellt.
"""
    report = HERE / "THREE_HUNDRED_SECOND_REPORT.md"
    report.write_text(report_text, encoding="utf-8")

    summary = {
        "status": "PASS",
        "statements": len(output),
        "records": len(by_record),
        "visible_events": sum(int(r["visible_event_count"]) for r in output),
        "read_source_tokens": sum(int(r["read_source_token_count"]) for r in output),
        "punctuation_counts": dict(counts),
        "absorbed_line_crossings": sum(int(r["physical_line_crossings_absorbed"]) for r in output),
        "owner_resets": sum(int(r["owner_resets_marked"]) for r in output),
        "read_once_collapses": sum(int(r["read_once_duplicates_collapsed"]) for r in output),
        "source_hashes": {str(p.relative_to(ROOT)): sha(p) for p in [EVENTS, SOURCE_STATEMENTS, SCOPE_EVENTS, SCOPE_STATEMENTS, CROSSINGS]},
        "output_hashes": {p.name: sha(p) for p in [table, edition, manual, report]},
    }
    (HERE / "BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
