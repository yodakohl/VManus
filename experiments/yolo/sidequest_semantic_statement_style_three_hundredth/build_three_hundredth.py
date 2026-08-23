#!/usr/bin/env python3
"""Build a writing-style decision for all 116 prose statements."""

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
SHORTENINGS = ROOT / "experiments/yolo/sidequest_semantic_cross_register_compression_two_hundred_ninety_ninth/TWO_HUNDRED_NINETY_NINTH_2_CLEAN_PROSE_SHORTENINGS.tsv"


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


def main() -> None:
    events = read_tsv(EVENTS)
    statements = read_tsv(STATEMENTS)
    shortening_by_statement = {row["statement_id"]: row for row in read_tsv(SHORTENINGS)}
    by_statement: dict[str, list[dict[str, str]]] = defaultdict(list)
    for event in events:
        by_statement[event["statement_id"]].append(event)

    style_rows = []
    record_counts: dict[str, Counter[str]] = defaultdict(Counter)
    for statement in statements:
        statement_id = statement["statement_id"]
        selected = by_statement[statement_id]
        whole_count = sum(event["family_parse"].startswith("WHOLE_SIGN") for event in selected)
        terminal_count = sum(event["terminal_status"] == "TERMINAL" for event in selected)
        if statement_id in shortening_by_statement:
            style = "COMPACT_ALTERNATIVE_AVAILABLE__VISIBLE_PHRASE_RETAINED"
            compact = shortening_by_statement[statement_id]["hypothetical_compact_card"]
            reason = "A register-shared card covers the exact same adjacent scopes, but the visible two-card phrase remains the manuscript reading."
        elif len(selected) == 1:
            style = "SINGLE_CARD_ALREADY_COMPACT"
            compact = selected[0]["visible_surface"]
            reason = "One registered card already carries the entire statement scope."
        elif whole_count:
            style = "RETAIN_LEARNED_PAYLOAD_WITH_ITS_FRAME"
            compact = "NONE"
            reason = "A learned payload or nomenclator card must remain distinct from the surrounding instruction slots."
        elif terminal_count:
            style = "RETAIN_PROCESS_SEQUENCE_AND_COMMIT_SCOPE"
            compact = "NONE"
            reason = "The final operation/commit closes only its own workstep; fusing earlier cards would blur scope."
        else:
            style = "RETAIN_OPEN_MULTI_SLOT_INSTRUCTION"
            compact = "NONE"
            reason = "The open phrase carries several ordered slots or worksteps and has no exact one-card equivalent."
        record_counts[statement["record_unit_id"]][style] += 1
        style_rows.append({
            "statement_order": len(style_rows) + 1,
            "statement_id": statement_id,
            "record_unit_id": statement["record_unit_id"],
            "page": statement["page"],
            "loci": statement["loci"],
            "owner_slot": statement["owner_slot"],
            "visible_card_count": len(selected),
            "visible_surface_sequence": statement["surface_sequence"],
            "visible_recipe_sequence": statement["family_sequence_de"],
            "current_reading_de": statement["two_layer_statement_de"],
            "whole_sign_cards": whole_count,
            "terminal_cards": terminal_count,
            "style_decision": style,
            "available_compact_card": compact,
            "style_reason_de": reason,
            "hypothetical_card_count_if_compact_used": (len(selected) - 1) if style == "COMPACT_ALTERNATIVE_AVAILABLE__VISIBLE_PHRASE_RETAINED" else len(selected),
            "visible_text_policy": "KEEP_EXACT_VISIBLE_SEQUENCE",
        })
    style_path = HERE / "THREE_HUNDREDTH_116_STATEMENT_WRITING_STYLE.tsv"
    write_tsv(style_path, style_rows)

    record_rows = []
    for record in sorted(record_counts, key=lambda value: (value[0], value)):
        record_statements = [row for row in style_rows if row["record_unit_id"] == record]
        counts = record_counts[record]
        record_rows.append({
            "record_unit_id": record,
            "page": record_statements[0]["page"],
            "statements": len(record_statements),
            "visible_cards": sum(int(row["visible_card_count"]) for row in record_statements),
            "single_card_statements": counts["SINGLE_CARD_ALREADY_COMPACT"],
            "compact_alternatives": counts["COMPACT_ALTERNATIVE_AVAILABLE__VISIBLE_PHRASE_RETAINED"],
            "payload_frame_retained": counts["RETAIN_LEARNED_PAYLOAD_WITH_ITS_FRAME"],
            "process_commit_retained": counts["RETAIN_PROCESS_SEQUENCE_AND_COMMIT_SCOPE"],
            "open_multi_slot_retained": counts["RETAIN_OPEN_MULTI_SLOT_INSTRUCTION"],
            "dominant_style": counts.most_common(1)[0][0],
        })
    record_path = HERE / "THREE_HUNDREDTH_11_RECORD_STYLE_SUMMARY.tsv"
    write_tsv(record_path, record_rows)

    edition_lines = ["# 116 Aussagen mit Werkstattstil", ""]
    current_record = None
    for row in style_rows:
        if row["record_unit_id"] != current_record:
            current_record = row["record_unit_id"]
            edition_lines.extend([f"## {current_record} — {row['page']}", ""])
        compact_text = f"; mögliche Kompaktkarte `{row['available_compact_card']}`" if row["available_compact_card"] != "NONE" and row["style_decision"].startswith("COMPACT_") else ""
        edition_lines.append(f"- **{row['statement_id']}** `{row['visible_surface_sequence']}` — {row['style_decision']}{compact_text}. {row['style_reason_de']}")
    edition_path = HERE / "THREE_HUNDREDTH_COMPLETE_STYLED_PROSE_EDITION.md"
    edition_path.write_text("\n".join(edition_lines) + "\n", encoding="utf-8")

    manual = """# Satzstil der Werkstatt

1. Hat eine Aussage genau eine registrierte Karte, bleibt sie einkartig.
2. Ein gelerntes Ganzzeichen bleibt von seinen Rahmenkarten getrennt.
3. Eine Tätigkeit mit eigenem Abschluss behält ihre vorangehenden Slots als getrennte Karten.
4. Offene Adress-, Mengen- und Prozessslots bleiben als geordnete Phrase stehen.
5. Eine Kompaktkarte ist nur erlaubt, wenn sie exakt dieselben lokalen Slots umfasst.

Auf den 116 Aussagen ergibt das 44 bereits kompakte Einzelkarten, 17 Payload-plus-Rahmen-Folgen, 37 Prozessfolgen mit eigenem Abschluss, 16 offene Mehrslot-Anweisungen und genau zwei verfügbare Kompaktalternativen (`olar`, `saral`).

Die Schreiberregel ist damit keine Pflicht zur maximalen Kürze. Die Kartenfolge macht Reichweite sichtbar; Kürze ist nur dann besser, wenn keine Reichweite verloren geht.
"""
    manual_path = HERE / "THREE_HUNDREDTH_STATEMENT_STYLE_MANUAL.md"
    manual_path.write_text(manual, encoding="utf-8")

    report = """# Sidequest-Pass 300: Satzstil statt bloßes Wörterbuch

## Ergebnis

Alle 116 Prosaaussagen haben nun eine explizite Schreibstilentscheidung. Die Verteilung ist:

- 44 bereits einkartige Aussagen;
- 17 Folgen mit gelerntem Payload/Ganzzeichen und eigenem Rahmen;
- 37 Prozessfolgen, deren Abschluss nur den letzten Arbeitsschritt bindet;
- 16 offene Mehrslot-Anweisungen;
- 2 sichtbare Phrasen mit einer sauberen alternativen Kompaktkarte.

Die hypothetische Maximalkompression würde nur zwei der 381 sichtbaren Karten sparen. Das erklärt, warum ein produktives System dennoch viele kurze Kartenfolgen verwendet: Sie zeigen Besitzer, Slotgrenze und Abschlussreichweite.

## Nächster Angriff

Jetzt wird aus den 116 Stilentscheidungen eine kleine Interpunktionstheorie gebaut: Welche sichtbaren DY-/Y-Ausgänge schließen Karte, Arbeitsschritt oder Aussage, und wie liest der Lehrling Zeilenwechsel ohne sie mit Satzgrenzen zu verwechseln?
"""
    report_path = HERE / "THREE_HUNDREDTH_REPORT.md"
    report_path.write_text(report, encoding="utf-8")

    style_counts = Counter(row["style_decision"] for row in style_rows)
    summary = {
        "status": "PASS",
        "statements": len(style_rows),
        "events": sum(int(row["visible_card_count"]) for row in style_rows),
        "records": len(record_rows),
        "style_counts": dict(sorted(style_counts.items())),
        "clean_compact_cards": sorted(row["available_compact_card"] for row in style_rows if row["style_decision"] == "COMPACT_ALTERNATIVE_AVAILABLE__VISIBLE_PHRASE_RETAINED"),
        "hypothetical_cards_saved": sum(int(row["visible_card_count"]) - int(row["hypothetical_card_count_if_compact_used"]) for row in style_rows if row["style_decision"] == "COMPACT_ALTERNATIVE_AVAILABLE__VISIBLE_PHRASE_RETAINED"),
        "source_hashes": {str(path.relative_to(ROOT)): sha(path) for path in [EVENTS, STATEMENTS, SHORTENINGS]},
        "outputs": {path.name: sha(path) for path in [style_path, record_path, edition_path, manual_path, report_path]},
    }
    (HERE / "BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
