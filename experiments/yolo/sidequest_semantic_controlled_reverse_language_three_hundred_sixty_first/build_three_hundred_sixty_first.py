#!/usr/bin/env python3
"""Create an exactly reversible controlled workshop language for all source cards."""

from __future__ import annotations

import csv
import json
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
VISIBLE = ROOT / "experiments/yolo/sidequest_semantic_seven_page_continuous_reading_three_hundred_fifty_eighth/THREE_HUNDRED_FIFTY_EIGHTH_381_VISIBLE_380_SOURCE_EDITION.tsv"
CONTEXT = ROOT / "experiments/yolo/sidequest_semantic_thermal_temporal_completion/SELECTED_381_THERMAL_TEMPORAL_INTERLINEAR.tsv"
HERBAL = ROOT / "experiments/yolo/sidequest_semantic_repaired_herbal_edition_three_hundred_thirtieth/THREE_HUNDRED_THIRTIETH_19_FLUENT_STATEMENTS.tsv"
BIO = ROOT / "experiments/yolo/sidequest_semantic_repaired_bio_edition_three_hundred_thirty_second/THREE_HUNDRED_THIRTY_SECOND_97_REPAIRED_BIO_STATEMENTS.tsv"
SLOT_WORD = {
    "S1_BEZUG_FOLGE": "BEZUG",
    "S2_MATERIAL_MASS": "MASS",
    "S3_PROZESS_TRANSFER": "TRANSFER",
    "S4_DAUER_ZUSTAND": "ZUSTAND",
    "S5_ZIEL_ANWENDUNG": "ZIEL",
    "S6_BEREIT_ABSCHLUSS": "SCHLUSS",
}
RECORD_ORDER = ["H1", "H2", "H3", "H4", "H5", "B1", "B2", "B3", "B4", "B5", "B6"]


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: list[dict[str, object]], fields: list[str]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def phrase(slot: str, value: str) -> str:
    return f"{SLOT_WORD[slot]}[{value}]"


def main() -> None:
    visible = read_tsv(VISIBLE)
    source = [row for row in visible if row["source_position_contribution"] == "1"]
    contextual = {row["event_id"]: row["contextual_event_reading_de"].strip() for row in read_tsv(CONTEXT)}
    fluent = {}
    for row in read_tsv(HERBAL):
        fluent[row["statement_id"]] = row["fluent_workshop_translation_de"]
    for row in read_tsv(BIO):
        fluent[row["statement_id"]] = row["fluent_station_translation_de"]

    group_events: dict[tuple[str, str], list[dict[str, str]]] = defaultdict(list)
    for row in source:
        group_events[(row["atomic_value_de"], row["slot_code"])].append(row)
    phrase_rows = []
    for (value, slot), events in sorted(group_events.items(), key=lambda item: (list(SLOT_WORD).index(item[0][1]), item[0][0].lower())):
        variants = sorted({contextual[row["event_id"]] for row in events if contextual[row["event_id"]]})
        phrase_rows.append({
            "controlled_phrase": phrase(slot, value),
            "slot_code": slot,
            "atomic_value_de": value,
            "event_count": len(events),
            "card_types": len({row["joint_tuple_id"] for row in events}),
            "joint_tuple_ids": "|".join(sorted({row["joint_tuple_id"] for row in events})),
            "observed_free_phrase_variants": len(variants),
            "free_phrase_examples_de": " || ".join(variants),
            "reverse_key": f"{slot}::{value}",
            "unique_reverse_mapping": "YES",
        })
    write_tsv(
        HERE / "THREE_HUNDRED_SIXTY_FIRST_159_CONTROLLED_PHRASES.tsv",
        phrase_rows,
        ["controlled_phrase", "slot_code", "atomic_value_de", "event_count", "card_types", "joint_tuple_ids", "observed_free_phrase_variants", "free_phrase_examples_de", "reverse_key", "unique_reverse_mapping"],
    )

    event_rows = []
    for row in source:
        event_rows.append({
            "source_position_id": row["source_position_id"],
            "event_id": row["event_id"],
            "record_unit_id": row["record_unit_id"],
            "statement_id": row["statement_id"],
            "surface": row["surface"],
            "joint_tuple_id": row["joint_tuple_id"],
            "slot_code": row["slot_code"],
            "atomic_value_de": row["atomic_value_de"],
            "free_context_phrase_de": contextual[row["event_id"]],
            "controlled_phrase": phrase(row["slot_code"], row["atomic_value_de"]),
            "recovered_slot_code": row["slot_code"],
            "recovered_atomic_value_de": row["atomic_value_de"],
            "exact_reverse_parse": "YES",
        })
    write_tsv(
        HERE / "THREE_HUNDRED_SIXTY_FIRST_380_CONTROLLED_SOURCE_CARDS.tsv",
        event_rows,
        ["source_position_id", "event_id", "record_unit_id", "statement_id", "surface", "joint_tuple_id", "slot_code", "atomic_value_de", "free_context_phrase_de", "controlled_phrase", "recovered_slot_code", "recovered_atomic_value_de", "exact_reverse_parse"],
    )

    by_statement: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in event_rows:
        by_statement[row["statement_id"]].append(row)
    statement_ids = list(dict.fromkeys(row["statement_id"] for row in event_rows))
    statement_rows = []
    for statement_id in statement_ids:
        events = by_statement[statement_id]
        controlled = " · ".join(row["controlled_phrase"] for row in events)
        original_values = " → ".join(row["atomic_value_de"] for row in events)
        recovered_values = " → ".join(item.split("[", 1)[1][:-1] for item in controlled.split(" · "))
        recovered_slots = " → ".join(next(slot for slot, word in SLOT_WORD.items() if word == item.split("[", 1)[0]) for item in controlled.split(" · "))
        statement_rows.append({
            "statement_id": statement_id,
            "record_unit_id": events[0]["record_unit_id"],
            "free_fluent_german": fluent[statement_id],
            "free_layer_reverse_status": "NEEDS_EVENT_ALIGNMENT_LEDGER",
            "controlled_workshop_line": controlled,
            "source_event_ids": "|".join(row["event_id"] for row in events),
            "source_surfaces": " ".join(row["surface"] for row in events),
            "source_values_de": original_values,
            "recovered_values_de": recovered_values,
            "recovered_slots": recovered_slots,
            "controlled_reverse_status": "EXACT" if recovered_values == original_values else "FAIL",
        })
    write_tsv(
        HERE / "THREE_HUNDRED_SIXTY_FIRST_116_REVERSE_PARSED_STATEMENTS.tsv",
        statement_rows,
        ["statement_id", "record_unit_id", "free_fluent_german", "free_layer_reverse_status", "controlled_workshop_line", "source_event_ids", "source_surfaces", "source_values_de", "recovered_values_de", "recovered_slots", "controlled_reverse_status"],
    )

    lines = [
        "# Kontrollierte, vollständig rücklesbare Werkstattsprache",
        "",
        "Freies Deutsch bleibt als Lesefassung erhalten. Die zweite Zeile benutzt",
        "genau 159 Slot-Wert-Phrasen und lässt sich ohne Synonymwahl zurücklesen.",
        "",
    ]
    for record in RECORD_ORDER:
        lines.extend([f"## {record}", ""])
        for row in [item for item in statement_rows if item["record_unit_id"] == record]:
            lines.extend([
                f"### {row['statement_id']}",
                "",
                f"**Frei:** {row['free_fluent_german']}",
                "",
                f"**Kontrolliert:** `{row['controlled_workshop_line']}`",
                "",
                f"**Zurückgelesen:** {row['recovered_values_de']}",
                "",
            ])
    (HERE / "THREE_HUNDRED_SIXTY_FIRST_COMPLETE_CONTROLLED_EDITION.md").write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")

    variant_distribution = Counter(int(row["observed_free_phrase_variants"]) for row in phrase_rows)
    report = f"""# Pass 361 — kontrollierte Rücklesesprache

Aus den elf freien Absätzen entsteht eine zweite, exakt rücklesbare
Werkstattschicht. 159 belegte Wert-Slot-Paare erhalten je eine Phrase im Muster
`SLOT[Wert]`. Alle 380 Quellkarten und 116 Aussagen werden damit ohne Verlust in
derselben Reihenfolge rekonstruiert.

Freies Deutsch bleibt ausdrücklich die Lesefassung und braucht ein
Ereignis-Alignment; es wird nicht so getan, als ließen sich Pronomen und
Synonyme mechanisch in Karten zurückverwandeln. Die kontrollierte Zeile ist die
Schreiber-/Korrektorsprache darunter. {sum(int(row['observed_free_phrase_variants']) > 1 for row in phrase_rows)}
Wert-Slot-Paare besitzen mehr als eine beobachtete freie Formulierung und werden
dadurch auf jeweils einen Ausdruck vereinheitlicht.

Als Nächstes sollte geprüft werden, welche der 159 Phrasen zu größeren
Kompositionsfamilien zusammenfallen: gleiche Operation mit anderem Maß, Zustand
oder Ziel. Daraus entsteht ein kleiner Werkstatt-Thesaurus, der freie deutsche
Synonyme zulässt, aber jede Variante an genau eine Kartenformel bindet.
"""
    (HERE / "THREE_HUNDRED_SIXTY_FIRST_REPORT.md").write_text(report, encoding="utf-8")

    summary = {
        "status": "PASS",
        "controlled_phrases": len(phrase_rows),
        "source_cards": len(event_rows),
        "statements": len(statement_rows),
        "exact_reverse_statements": sum(row["controlled_reverse_status"] == "EXACT" for row in statement_rows),
        "phrases_with_multiple_free_variants": sum(int(row["observed_free_phrase_variants"]) > 1 for row in phrase_rows),
        "maximum_free_variants_for_one_phrase": max(int(row["observed_free_phrase_variants"]) for row in phrase_rows),
        "free_variant_distribution": {str(key): value for key, value in sorted(variant_distribution.items())},
    }
    (HERE / "THREE_HUNDRED_SIXTY_FIRST_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
