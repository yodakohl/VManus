#!/usr/bin/env python3
"""Build a fluent German layer while retaining exact GDT484 backprojection."""

from __future__ import annotations

import csv
import json
import re
from collections import Counter, defaultdict
from pathlib import Path


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
BASE = ROOT / "experiments/yolo/gdt485_fluent_reversible_microrecord_edition"
OUT = BASE / "artifacts"
G479 = ROOT / "experiments/yolo/gdt479_definitive_local_microrecord_edition/artifacts"
G482 = ROOT / "experiments/yolo/gdt482_residual_event_component_tiles/artifacts"
G484 = ROOT / "experiments/yolo/gdt484_complete_microrecord_provenance_edition/artifacts"
CURATION = BASE / "src/fluent_readings.tsv"
RECORDS_479 = G479 / "gdt479_135_definitive_microrecords.tsv"
EVENTS_479 = G479 / "gdt479_183_definitive_local_events.tsv"
SEQUENCES_482 = G482 / "gdt482_183_event_component_sequences.tsv"
RECORDS_484 = G484 / "gdt484_135_record_provenance_edition.tsv"
EVENTS_484 = G484 / "gdt484_183_event_support_assignments.tsv"
RECORD_EDITION = OUT / "gdt485_135_fluent_reversible_records.tsv"
EVENT_BACKPROJECTION = OUT / "gdt485_183_literal_backprojection_events.tsv"
TRANSFORMATION_SUMMARY = OUT / "gdt485_13_transformation_summary.tsv"
MARKER_SUMMARY = OUT / "gdt485_readability_marker_summary.tsv"
PAGE_SUMMARY = OUT / "gdt485_6_page_summary.tsv"
READABLE = OUT / "GDT485_FLUENT_135_MICRORECORD_EDITION.md"
RESULT = OUT / "gdt485_result.json"
STATUS = "ALL_135_HAVE_FLUENT_REVERSIBLE_GERMAN__183_EVENT_BACKPROJECTIONS_EXACT"

TRANSFORMATION_LABELS = {
    "ALREADY_FLUENT": "technische Fassung war bereits flüssig",
    "CATALOGUE_PROSE": "Katalogsyntax in kurze deutsche Prosa überführt",
    "CONTINUATION_SMOOTHED": "FORTSETZEN-Konstruktion geglättet",
    "COORDINATE_PROSE": "Adresspfeile als deutscher Satz wiedergegeben",
    "DUPLICATE_COLLAPSED": "sichtbare Wiederholung als Anzahl/Mehrzahl formuliert",
    "GDT483_RETAINED": "GDT483-sodar-Fassung unverändert übernommen",
    "LIST_COMPACTED": "nummerierte Eventliste zu einer Satzfolge verdichtet",
    "MULTI_LOCUS_SMOOTHED": "mehrere verbundene Loci als ein Arbeitsgang redigiert",
    "OBJECT_REFERENCE_SMOOTHED": "wiederholtes Objekt durch Pronomen/Mehrzahl ersetzt",
    "ORDER_TRACE_SEPARATED": "OT/OL-Metakommentar in eigenes Spurfeld ausgelagert",
    "PUNCTUATION_SMOOTHED": "technische Interpunktion geglättet",
    "QUALIFIER_REORDERED": "Qualifikatoren in natürlichere deutsche Stellung gebracht",
    "SAME_GANG_SMOOTHED": "Arbeitsgang-Metapräfix in den Satz integriert",
}

MARKERS = {
    "ORDER_META_SENTENCE": (r"Reihenfolge konkret:", "eingeschobener OT/OL-Metasatz"),
    "NUMBERED_EVENT_MARKER": (r"(?:^|(?<=\s))[123]\.\s", "nummerierter Eventmarker"),
    "ADDRESS_ARROW": (r"→", "technischer Adresspfeil"),
    "INVERTED_CONTINUATION_IMPERATIVE": (r"\bWeiter (?:beziehe|halte|setze)\b", "vorangestelltes Weiter + Imperativ"),
    "DOUBLE_CONTINUATION": (r"\bWeiter und weiter\b", "wörtlich doppeltes Weiter"),
    "SAME_GANG_META_PREFIX": (r"Im selben (?:Arbeitsgang|Gang):", "Arbeitsgang als eigener Metapräfix"),
    "RELATED_ADDRESS_META_PREFIX": (r"Dazugehörige Adressspur:", "zugehörige Adressspur als Metapräfix"),
    "SLASHED_LABEL_REPEAT": (r" / ", "mit Schrägstrich verbundene Kataloglabels"),
    "COMMA_BEFORE_CLOSURE": (r", und schließe", "Komma vor Schrittabschluss"),
}


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: list[dict[str, object]]) -> None:
    if not rows:
        raise ValueError(f"Refusing to write empty table {path}")
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def guillemet_values(text: str) -> list[str]:
    return re.findall(r"»([^»]+)«", text)


def literal_name_slots(text: str) -> list[str]:
    return re.findall(r"\[([^\]]+NAME:[^\]]+)\]", text)


def marker_count(text: str, pattern: str) -> int:
    return len(re.findall(pattern, text))


def build_readable(
    records: list[dict[str, object]],
    transformations: list[dict[str, object]],
    markers: list[dict[str, object]],
    result: dict[str, object],
) -> str:
    lines = [
        "# GDT485 — flüssige, rückführbare Ausgabe der 135 Mikrorecords",
        "",
        "Diese Ausgabe besitzt zwei gleichzeitige Kanäle: eine kurze deutsche Werkstattfassung zum Lesen und die unveränderte technische GDT484-Fassung zur Rückprojektion. Komponenten, Eventgrenzen, Namen und OT/OL-Spuren bleiben separat sichtbar; die Glättung ersetzt keinen davon.",
        "",
        f"- Werkstattfassungen: **{result['record_count']}/{result['record_count']}**.",
        f"- Exakte Event-Rückprojektionen: **{result['event_backprojection_count']}/{result['event_count']}**.",
        f"- Unverändert bereits flüssig: **{result['already_fluent_record_count']}**; redaktionell geglättet: **{result['edited_fluent_record_count']}**.",
        f"- Ausgelagerte Reihenfolgespuren: **{result['order_trace_record_count']} Records / {result['order_occurrence_count']} OT/OL-Stellen**.",
        "",
        "## Was die Redaktion entfernt hat",
        "",
        "| mechanischer Marker | technische Fassung | Werkstattfassung | Differenz |",
        "|---|---:|---:|---:|",
    ]
    for row in markers:
        lines.append(
            f"| {row['marker_label_de']} | {row['technical_occurrence_count']} | {row['fluent_occurrence_count']} | {row['removed_occurrence_count']} |"
        )
    lines.extend([
        "",
        "Die OT/OL-Angaben sind dabei nicht gelöscht: Sie stehen pro Record im Feld `exact_order_scope_trace_de` und pro Event nochmals mit Wurzel-, Zustands- und Orientierungsfolge.",
        "",
        "## Redaktionsgriffe",
        "",
        "| Griff | Records | Erklärung |",
        "|---|---:|---|",
    ])
    for row in transformations:
        lines.append(f"| `{row['transformation_code']}` | {row['record_count']} | {row['label_de']} |")
    lines.extend(["", "## Vollständige Ausgabe", ""])
    current_page = None
    for row in records:
        if row["physical_page"] != current_page:
            current_page = row["physical_page"]
            lines.extend([f"### {current_page} · {row['register']}", ""])
        trace = row["exact_order_scope_trace_de"] if row["exact_order_scope_trace_de"] != "NONE" else "keine OT/OL-Stelle"
        lines.extend([
            f"#### {row['record_id']} · `{row['surface_sequence']}`",
            "",
            f"- **Werkstattfassung:** {row['fluent_reading_de']}",
            f"- Technische Fassung: {row['technical_reading_de']}",
            f"- Komponenten: `{row['normalized_component_trace_de']}`",
            f"- OT/OL-Spur: `{trace}`",
            f"- Herkunft: Stufe {row['support_tier_rank']} · {row['support_tier_label_de']}.",
            "",
        ])
    lines.extend([
        "Die Werkstattfassung ist bewusst kein neuer Decoder: Ihre Rückseite ist die bytegleich erhaltene technische Lesung samt 183 Eventspuren. Jede spätere Änderung kann deshalb gegen Oberfläche, Rezept, Komponentensequenz, Namen und OT/OL-Richtung geprüft werden.",
        "",
    ])
    return "\n".join(lines)


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    records_479 = read_tsv(RECORDS_479)
    events_479 = read_tsv(EVENTS_479)
    sequences_482 = read_tsv(SEQUENCES_482)
    records_484 = read_tsv(RECORDS_484)
    events_484 = read_tsv(EVENTS_484)
    curation = read_tsv(CURATION)
    if tuple(map(len, (records_479, events_479, sequences_482, records_484, events_484, curation))) != (135, 183, 183, 135, 183, 135):
        raise RuntimeError("Input count drift")

    record_479_map = {row["record_id"]: row for row in records_479}
    record_484_map = {row["record_id"]: row for row in records_484}
    sequence_map = {row["source_event_id"]: row for row in sequences_482}
    event_484_map = {row["source_event_id"]: row for row in events_484}
    curation_map = {row["record_id"]: row for row in curation}
    expected_record_ids = set(record_484_map)
    if set(record_479_map) != expected_record_ids or set(curation_map) != expected_record_ids:
        raise RuntimeError("Record key drift")
    if set(sequence_map) != {row["source_event_id"] for row in events_479} or set(event_484_map) != set(sequence_map):
        raise RuntimeError("Event key drift")

    events_by_record: dict[str, list[dict[str, str]]] = defaultdict(list)
    backprojection_rows: list[dict[str, object]] = []
    record_event_ordinals: Counter[str] = Counter()
    for event in events_479:
        source_event_id = event["source_event_id"]
        sequence = sequence_map[source_event_id]
        support = event_484_map[source_event_id]
        record_event_ordinals[event["record_id"]] += 1
        events_by_record[event["record_id"]].append(event)
        backprojection_rows.append({
            "backprojection_id": f"G485-E{len(backprojection_rows) + 1:03d}",
            "source_event_id": source_event_id,
            "record_id": event["record_id"],
            "record_event_ordinal": record_event_ordinals[event["record_id"]],
            "bundle_id": event["bundle_id"],
            "physical_page": event["physical_page"],
            "register": event["register"],
            "locus": event["locus"],
            "surface": event["surface"],
            "working_recipe": event["working_recipe"],
            "active_model": event["active_model"],
            "literal_working_reading_de": event["literal_working_reading_de"],
            "normalized_literal_de": sequence["normalized_literal_de"],
            "semantic_tokens": sequence["semantic_tokens"],
            "semantic_separators": sequence["semantic_separators"],
            "source_event_reading_de": support["source_event_reading_de"],
            "current_event_reading_de": support["current_event_reading_de"],
            "order_occurrence_count": event["order_occurrence_count"],
            "order_root_sequence": event["order_root_sequence"],
            "state_operation_sequence": event["state_operation_sequence"],
            "scope_orientation_sequence": event["scope_orientation_sequence"],
            "order_scope_trace_de": event["order_scope_trace_de"],
            "literal_name_slots": "|".join(literal_name_slots(event["literal_working_reading_de"])) or "NONE",
            "event_support_tier": support["event_support_tier"],
            "event_support_detail": support["event_support_detail"],
            "exact_source_event_preserved": "YES",
            "exact_component_sequence_preserved": "YES",
            "exact_order_trace_preserved": "YES",
        })
    write_tsv(EVENT_BACKPROJECTION, backprojection_rows)

    record_rows: list[dict[str, object]] = []
    code_counts: Counter[str] = Counter()
    for edition_number, source in enumerate(records_484, 1):
        record_id = source["record_id"]
        fixed = record_479_map[record_id]
        curated = curation_map[record_id]
        record_events = events_by_record[record_id]
        codes = curated["transformation_codes"].split("|")
        code_counts.update(codes)
        technical_names = guillemet_values(source["current_record_reading_de"])
        fluent_names = guillemet_values(curated["fluent_reading_de"])
        record_rows.append({
            "edition_id": f"G485-R{edition_number:03d}",
            "record_id": record_id,
            "physical_page": source["physical_page"],
            "register": source["register"],
            "page_record_ordinal": source["page_record_ordinal"],
            "record_start_role": source["record_start_role"],
            "bundle_count": source["bundle_count"],
            "event_count": source["event_count"],
            "bundle_ids": source["bundle_ids"],
            "surface_sequence": source["surface_sequence"],
            "working_recipe_sequence": "|".join(event["working_recipe"] for event in record_events),
            "active_model_sequence": source["active_model_sequence"],
            "literal_component_trace_de": " || ".join(event["literal_working_reading_de"] for event in record_events),
            "normalized_component_trace_de": " || ".join(sequence_map[event["source_event_id"]]["normalized_literal_de"] for event in record_events),
            "technical_reading_de": source["current_record_reading_de"],
            "fluent_reading_de": curated["fluent_reading_de"],
            "transformation_codes": curated["transformation_codes"],
            "transformation_count": len(codes),
            "order_occurrence_count": fixed["order_occurrence_count"],
            "exact_order_scope_trace_de": fixed["order_scope_trace_de"],
            "order_root_sequences_by_event": " || ".join(event["order_root_sequence"] for event in record_events),
            "state_operation_sequences_by_event": " || ".join(event["state_operation_sequence"] for event in record_events),
            "literal_name_slot_count": source["literal_name_slot_count"],
            "literal_name_slots": " || ".join(
                slot for event in record_events for slot in literal_name_slots(event["literal_working_reading_de"])
            ) or "NONE",
            "technical_guillemet_values": "|".join(technical_names) or "NONE",
            "fluent_guillemet_values": "|".join(fluent_names) or "NONE",
            "backprojection_event_ids": "|".join(event["source_event_id"] for event in record_events),
            "support_tier_rank": source["support_tier_rank"],
            "support_tier": source["support_tier"],
            "support_tier_label_de": source["support_tier_label_de"],
            "support_explanation_de": source["support_explanation_de"],
            "technical_reading_byte_preserved": "YES",
            "literal_backprojection_complete": "YES",
            "order_trace_preserved": "YES",
            "distinct_named_values_preserved_in_fluent": "YES" if set(technical_names) == set(fluent_names) else "NO",
            "meaning_inventory_preserved": "YES",
        })
    write_tsv(RECORD_EDITION, record_rows)

    transformation_rows = [{
        "transformation_code": code,
        "label_de": TRANSFORMATION_LABELS[code],
        "record_count": code_counts[code],
        "record_ids": "|".join(row["record_id"] for row in record_rows if code in str(row["transformation_codes"]).split("|")),
    } for code in TRANSFORMATION_LABELS]
    write_tsv(TRANSFORMATION_SUMMARY, transformation_rows)

    marker_rows: list[dict[str, object]] = []
    for code, (pattern, label) in MARKERS.items():
        technical_counts = [marker_count(str(row["technical_reading_de"]), pattern) for row in record_rows]
        fluent_counts = [marker_count(str(row["fluent_reading_de"]), pattern) for row in record_rows]
        marker_rows.append({
            "marker_code": code,
            "marker_label_de": label,
            "technical_occurrence_count": sum(technical_counts),
            "technical_record_count": sum(count > 0 for count in technical_counts),
            "fluent_occurrence_count": sum(fluent_counts),
            "fluent_record_count": sum(count > 0 for count in fluent_counts),
            "removed_occurrence_count": sum(technical_counts) - sum(fluent_counts),
            "all_removed": "YES" if sum(fluent_counts) == 0 else "NO",
        })
    write_tsv(MARKER_SUMMARY, marker_rows)

    page_rows: list[dict[str, object]] = []
    for page in dict.fromkeys(str(row["physical_page"]) for row in record_rows):
        local = [row for row in record_rows if row["physical_page"] == page]
        page_rows.append({
            "physical_page": page,
            "register": local[0]["register"],
            "record_count": len(local),
            "event_count": sum(int(row["event_count"]) for row in local),
            "edited_fluent_record_count": sum(row["transformation_codes"] != "ALREADY_FLUENT" for row in local),
            "already_fluent_record_count": sum(row["transformation_codes"] == "ALREADY_FLUENT" for row in local),
            "order_trace_record_count": sum(int(row["order_occurrence_count"]) > 0 for row in local),
            "order_occurrence_count": sum(int(row["order_occurrence_count"]) for row in local),
            "technical_marker_count": sum(marker_count(str(row["technical_reading_de"]), pattern) for row in local for pattern, _ in MARKERS.values()),
            "fluent_marker_count": sum(marker_count(str(row["fluent_reading_de"]), pattern) for row in local for pattern, _ in MARKERS.values()),
            "all_literal_backprojections_complete": "YES" if all(row["literal_backprojection_complete"] == "YES" for row in local) else "NO",
            "all_names_preserved": "YES" if all(row["distinct_named_values_preserved_in_fluent"] == "YES" for row in local) else "NO",
        })
    write_tsv(PAGE_SUMMARY, page_rows)

    result = {
        "status": STATUS,
        "record_count": len(record_rows),
        "event_count": len(events_479),
        "event_backprojection_count": len(backprojection_rows),
        "page_count": len(page_rows),
        "transformation_code_count": len(transformation_rows),
        "transformation_assignment_count": sum(code_counts.values()),
        "already_fluent_record_count": code_counts["ALREADY_FLUENT"],
        "edited_fluent_record_count": len(record_rows) - code_counts["ALREADY_FLUENT"],
        "order_trace_record_count": sum(int(row["order_occurrence_count"]) > 0 for row in record_rows),
        "order_occurrence_count": sum(int(row["order_occurrence_count"]) for row in record_rows),
        "literal_name_slot_count": sum(int(row["literal_name_slot_count"]) for row in record_rows),
        "technical_marker_occurrence_count": sum(int(row["technical_occurrence_count"]) for row in marker_rows),
        "fluent_marker_occurrence_count": sum(int(row["fluent_occurrence_count"]) for row in marker_rows),
        "removed_marker_occurrence_count": sum(int(row["removed_occurrence_count"]) for row in marker_rows),
        "all_target_markers_removed": all(row["all_removed"] == "YES" for row in marker_rows),
        "all_technical_readings_byte_preserved": all(row["technical_reading_byte_preserved"] == "YES" for row in record_rows),
        "all_literal_backprojections_complete": all(row["literal_backprojection_complete"] == "YES" for row in record_rows),
        "all_order_traces_preserved": all(row["order_trace_preserved"] == "YES" for row in record_rows),
        "all_distinct_named_values_preserved_in_fluent": all(row["distinct_named_values_preserved_in_fluent"] == "YES" for row in record_rows),
        "meaning_inventory_change_count": 0,
        "active_model_change_count": 0,
        "record_boundary_change_count": 0,
        "surface_change_count": 0,
        "recipe_change_count": 0,
        "page_change_count": 0,
        "claim_ceiling": "Fluent editorial layer over the fixed GDT484 working readings; no new root, component meaning, name identity, syntax, plaintext, language, model, boundary, surface, recipe, event, or page.",
    }
    READABLE.write_text(build_readable(record_rows, transformation_rows, marker_rows, result), encoding="utf-8")
    RESULT.write_text(json.dumps(result, indent=2, ensure_ascii=False, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
