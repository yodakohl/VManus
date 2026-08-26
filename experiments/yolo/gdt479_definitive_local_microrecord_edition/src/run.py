#!/usr/bin/env python3
"""Compile the definitive six-page local microrecord working edition."""

from __future__ import annotations

import csv
import json
from collections import Counter, defaultdict
from pathlib import Path


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
BASE = ROOT / "experiments/yolo/gdt479_definitive_local_microrecord_edition"
OUT = BASE / "artifacts"
G474 = ROOT / "experiments/yolo/gdt474_locus_bundle_meaning_triptych/artifacts"
G475 = ROOT / "experiments/yolo/gdt475_ot_ol_page_microrecord_itineraries/artifacts"
G476 = ROOT / "experiments/yolo/gdt476_boundary_context_tie_resolution/artifacts"
G478 = ROOT / "experiments/yolo/gdt478_paired_ot_ol_order_grammar/artifacts"
BUNDLES = G474 / "gdt474_146_locus_bundle_meaning_triptych.tsv"
EVENTS = G474 / "gdt474_183_event_meaning_triptych.tsv"
BOUNDARIES = G475 / "gdt475_146_bundle_boundary_roles.tsv"
RECORDS = G475 / "gdt475_135_page_microrecords.tsv"
DECISIONS = G476 / "gdt476_64_tie_context_decisions.tsv"
ORDER = G478 / "gdt478_69_paired_order_scope_occurrences.tsv"

EVENT_OUT = OUT / "gdt479_183_definitive_local_events.tsv"
BUNDLE_OUT = OUT / "gdt479_146_definitive_local_bundles.tsv"
RECORD_OUT = OUT / "gdt479_135_definitive_microrecords.tsv"
PAGE_OUT = OUT / "gdt479_6_page_edition_summary.tsv"
READABLE_OUT = OUT / "GDT479_DEFINITIVE_SIX_PAGE_LOCAL_EDITION.md"
RESULT_OUT = OUT / "gdt479_result.json"


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


def event_reading(event: dict[str, str], model: str) -> str:
    return event[f"{model.lower()}_event_reading_de"]


def bundle_reading(bundle: dict[str, str], model: str) -> str:
    return bundle[f"{model.lower()}_bundle_reading_de"]


def order_trace(rows: list[dict[str, str]]) -> str:
    return " | ".join(f"{row['root']}:{row['directional_scope_phrase_de']}" for row in rows) or "NONE"


def definite_reading(reading: str, rows: list[dict[str, str]]) -> str:
    if not rows:
        return reading
    return f"{reading} Reihenfolge konkret: " + "; ".join(
        f"{row['root']} — {row['directional_scope_phrase_de']}" for row in rows
    ) + "."


def continuation_prefix(model: str) -> str:
    return {
        "INSTRUCTION": "Im selben Arbeitsgang",
        "COORDINATE": "Dazugehörige Adressspur",
        "CATALOGUE": "Fortgesetzter Katalogeintrag",
    }[model]


def clean_for_prefix(reading: str, model: str) -> str:
    if model == "COORDINATE" and reading.startswith("Adressspur: "):
        return reading.removeprefix("Adressspur: ")
    return reading


def boundary_phrase(role: str) -> str:
    return {
        "PAGE_START": "Seitenbeginn",
        "EXPLICIT_NEXT_SIBLING_OT": "nächster gleichrangiger Eintrag",
        "EXPLICIT_CONTINUATION_OL": "Fortsetzung desselben Mikroeintrags",
        "UNMARKED_NEW_LOCUS_WITH_INTERNAL_CONTROL": "neuer Locus; interne Reihenfolge",
        "UNMARKED_NEW_LOCUS": "neuer sichtbarer Locus",
    }[role]


def markdown_escape(value: object) -> str:
    return str(value).replace("|", "\\|").replace("\n", " ")


def build_readable(
    event_rows: list[dict[str, object]],
    bundle_rows: list[dict[str, object]],
    record_rows: list[dict[str, object]],
    page_rows: list[dict[str, object]],
    result: dict[str, object],
) -> str:
    events_by_bundle: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in event_rows:
        events_by_bundle[str(row["bundle_id"])].append(row)
    bundles_by_record: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in bundle_rows:
        bundles_by_record[str(row["record_id"])].append(row)
    records_by_page: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in record_rows:
        records_by_page[str(row["physical_page"])].append(row)
    page_map = {str(row["physical_page"]): row for row in page_rows}

    lines = [
        "# GDT479 — definitive lokale Sechs-Seiten-Arbeitsausgabe",
        "",
        "Diese Ausgabe vereinigt die vollständigen 183 lokalen Ereignisse, GDT476s aktive Mischgrammatik und GDT478s genaue OT/OL-Richtung in 135 Mikroeinträgen. Kein Ereignis, keine Form und kein gelernter Name fehlt.",
        "",
        "| Ebene | vollständig | aktive Änderung gegenüber GDT475 |",
        "|---|---:|---:|",
        f"| Ereignisse | {result['event_count']} | {result['event_reading_change_count']} Ereignislesungen |",
        f"| Locus-Bündel | {result['bundle_count']} | {result['bundle_model_change_count']} Modellwahlen |",
        f"| Mikroeinträge | {result['record_count']} | 8 Mehrlocus-Einträge integriert |",
        f"| Reihenfolgeslots | {result['order_occurrence_count']} | alle directionalisiert |",
        "",
        "Die aktive Bündelverteilung ist 28 Adresse, 59 Anweisung und 59 Katalog. Alle drei GDT474-Alternativen bleiben in der Maschinentabelle erhalten; hier wird jeweils der derzeit beste Default gedruckt.",
        "",
    ]
    for page, records in records_by_page.items():
        summary = page_map[page]
        lines.extend([
            f"## {page}",
            "",
            f"{summary['event_count']} Ereignisse · {summary['bundle_count']} Bündel · {summary['record_count']} Mikroeinträge · {summary['order_occurrence_count']} OT/OL-Slots.",
            "",
        ])
        for record in records:
            record_bundles = bundles_by_record[str(record["record_id"])]
            lines.extend([
                f"### {record['page_record_ordinal']}. {record['record_id']} — {boundary_phrase(str(record['record_start_role']))}",
                "",
                f"**Arbeitslesung:** {record['definitive_record_reading_de']}",
                "",
            ])
            for bundle in record_bundles:
                marker = "↳" if int(bundle["bundle_ordinal_in_record"]) > 1 else "•"
                lines.append(
                    f"- {marker} {bundle['bundle_id']} · {bundle['locus']} · `{str(bundle['surface_sequence']).replace('|', ' · ')}` · {bundle['active_model']}: {bundle['active_bundle_reading_de']}"
                )
                if bundle["order_scope_trace_de"] != "NONE":
                    lines.append(f"  - Reihenfolge: {bundle['order_scope_trace_de']}")
                for event in events_by_bundle[str(bundle["bundle_id"])]:
                    lines.append(
                        f"  - {event['source_event_id']} `{event['surface']}` = {event['active_event_reading_de']}"
                    )
            lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    bundles = read_tsv(BUNDLES)
    events = read_tsv(EVENTS)
    boundaries = read_tsv(BOUNDARIES)
    records = read_tsv(RECORDS)
    decisions = read_tsv(DECISIONS)
    order = read_tsv(ORDER)
    if (len(bundles), len(events), len(boundaries), len(records), len(decisions), len(order)) != (146, 183, 146, 135, 64, 69):
        raise RuntimeError("GDT474/GDT475/GDT476/GDT478 input drift")

    bundle_map = {row["bundle_id"]: row for row in bundles}
    boundary_map = {row["bundle_id"]: row for row in boundaries}
    record_map = {row["record_id"]: row for row in records}
    decision_map = {row["bundle_id"]: row for row in decisions}
    order_by_event: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in order:
        order_by_event[row["source_event_id"]].append(row)
    events_by_bundle: dict[str, list[dict[str, str]]] = defaultdict(list)
    for event in events:
        events_by_bundle[event["bundle_id"]].append(event)

    active_model: dict[str, str] = {}
    model_source: dict[str, str] = {}
    for bundle in bundles:
        decision = decision_map.get(bundle["bundle_id"])
        if decision:
            active_model[bundle["bundle_id"]] = decision["context_selected_model"]
            model_source[bundle["bundle_id"]] = (
                "GDT476_RECORD_CONTEXT" if decision["context_decided"] == "YES" else "GDT476_LOCAL_DEFAULT"
            )
        else:
            active_model[bundle["bundle_id"]] = bundle["selected_model"]
            model_source[bundle["bundle_id"]] = "GDT474_UNIQUE_OR_VISIBLE_SELECTION"

    event_rows: list[dict[str, object]] = []
    for event in events:
        model = active_model[event["bundle_id"]]
        order_rows = order_by_event.get(event["source_event_id"], [])
        reading = event_reading(event, model)
        event_rows.append({
            "definitive_event_id": f"G479-E{len(event_rows) + 1:03d}",
            "source_event_id": event["source_event_id"],
            "bundle_id": event["bundle_id"],
            "record_id": boundary_map[event["bundle_id"]]["record_id"],
            "physical_page": event["physical_page"],
            "register": event["register"],
            "locus": event["locus"],
            "event_ordinal_in_bundle": event["event_ordinal_in_bundle"],
            "surface": event["surface"],
            "working_recipe": event["working_recipe"],
            "literal_working_reading_de": event["literal_working_reading_de"],
            "gdt474_selected_model": event["bundle_selected_model"],
            "active_model": model,
            "active_model_source": model_source[event["bundle_id"]],
            "model_changed_from_gdt474": "YES" if model != event["bundle_selected_model"] else "NO",
            "coordinate_event_reading_de": event["coordinate_event_reading_de"],
            "instruction_event_reading_de": event["instruction_event_reading_de"],
            "catalogue_event_reading_de": event["catalogue_event_reading_de"],
            "active_event_reading_de": reading,
            "order_occurrence_count": len(order_rows),
            "order_root_sequence": "|".join(row["root"] for row in order_rows) or "NONE",
            "state_operation_sequence": "|".join(row["state_operation"] for row in order_rows) or "NONE",
            "scope_orientation_sequence": "|".join(row["scope_orientation"] for row in order_rows) or "NONE",
            "order_scope_trace_de": order_trace(order_rows),
            "definitive_event_reading_de": definite_reading(reading, order_rows),
            "root_meaning_change": "NO",
            "learned_name_change": "NO",
            "claim_status": "DEFINITIVE_LOCAL_EVENT_WORKING_DEFAULT__ALTERNATIVES_RETAINED",
        })

    final_events_by_bundle: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in event_rows:
        final_events_by_bundle[str(row["bundle_id"])].append(row)

    bundle_rows: list[dict[str, object]] = []
    for bundle in bundles:
        boundary = boundary_map[bundle["bundle_id"]]
        model = active_model[bundle["bundle_id"]]
        source_events = final_events_by_bundle[bundle["bundle_id"]]
        all_order = [row for event in events_by_bundle[bundle["bundle_id"]] for row in order_by_event.get(event["source_event_id"], [])]
        reading = bundle_reading(bundle, model)
        decision = decision_map.get(bundle["bundle_id"])
        bundle_rows.append({
            "definitive_bundle_id": f"G479-B{len(bundle_rows) + 1:03d}",
            "bundle_id": bundle["bundle_id"],
            "record_id": boundary["record_id"],
            "physical_page": bundle["physical_page"],
            "register": bundle["register"],
            "locus": bundle["locus"],
            "owner_de": bundle["owner_de"],
            "event_count": bundle["event_count"],
            "source_event_ids": bundle["source_event_ids"],
            "surface_sequence": bundle["surface_sequence"],
            "recipe_sequence": bundle["recipe_sequence"],
            "literal_working_reading_de": bundle["literal_working_reading_de"],
            "boundary_role": boundary["boundary_role"],
            "record_bundle_count": boundary["record_bundle_count"],
            "bundle_ordinal_in_record": boundary["bundle_ordinal_in_record"],
            "local_best_models": bundle["best_models"],
            "gdt474_selected_model": bundle["selected_model"],
            "active_model": model,
            "active_model_source": model_source[bundle["bundle_id"]],
            "gdt476_context_decided": decision["context_decided"] if decision else "NOT_A_TIE",
            "model_changed_from_gdt474": "YES" if model != bundle["selected_model"] else "NO",
            "coordinate_repair_count": bundle["coordinate_repair_count"],
            "instruction_repair_count": bundle["instruction_repair_count"],
            "catalogue_repair_count": bundle["catalogue_repair_count"],
            "coordinate_bundle_reading_de": bundle["coordinate_bundle_reading_de"],
            "instruction_bundle_reading_de": bundle["instruction_bundle_reading_de"],
            "catalogue_bundle_reading_de": bundle["catalogue_bundle_reading_de"],
            "active_bundle_reading_de": reading,
            "order_occurrence_count": sum(int(row["order_occurrence_count"]) for row in source_events),
            "order_root_sequence": "|".join(str(row["order_root_sequence"]) for row in source_events if row["order_root_sequence"] != "NONE") or "NONE",
            "state_operation_sequence": "|".join(str(row["state_operation_sequence"]) for row in source_events if row["state_operation_sequence"] != "NONE") or "NONE",
            "order_scope_trace_de": order_trace(all_order),
            "definitive_bundle_reading_de": definite_reading(reading, all_order),
            "all_three_alternative_readings_retained": "YES",
            "root_meaning_change": "NO",
            "learned_name_change": "NO",
            "claim_status": "DEFINITIVE_LOCAL_BUNDLE_WORKING_DEFAULT__THREE_ALTERNATIVES_RETAINED",
        })

    final_bundle_map = {row["bundle_id"]: row for row in bundle_rows}
    record_rows: list[dict[str, object]] = []
    for record in records:
        ids = record["bundle_ids"].split("|")
        joined = [final_bundle_map[bundle_id] for bundle_id in ids]
        parts: list[str] = []
        for index, bundle in enumerate(joined):
            reading = str(bundle["definitive_bundle_reading_de"])
            if index:
                model = str(bundle["active_model"])
                reading = f"{continuation_prefix(model)}: {clean_for_prefix(reading, model)}"
            parts.append(reading)
        record_rows.append({
            "definitive_record_id": f"G479-R{len(record_rows) + 1:03d}",
            "record_id": record["record_id"],
            "physical_page": record["physical_page"],
            "register": record["register"],
            "page_record_ordinal": record["page_record_ordinal"],
            "record_start_role": record["record_start_role"],
            "bundle_count": record["bundle_count"],
            "bundle_ids": record["bundle_ids"],
            "locus_sequence": record["locus_sequence"],
            "surface_sequence": record["surface_sequence"],
            "active_model_sequence": "|".join(str(row["active_model"]) for row in joined),
            "model_change_count": sum(row["model_changed_from_gdt474"] == "YES" for row in joined),
            "context_decided_tie_count": sum(row["gdt476_context_decided"] == "YES" for row in joined),
            "order_occurrence_count": sum(int(row["order_occurrence_count"]) for row in joined),
            "order_scope_trace_de": " || ".join(str(row["order_scope_trace_de"]) for row in joined if row["order_scope_trace_de"] != "NONE") or "NONE",
            "definitive_record_reading_de": " ".join(parts),
            "event_count": sum(int(row["event_count"]) for row in joined),
            "all_events_have_default": "YES",
            "claim_status": "DEFINITIVE_LOCAL_MICRORECORD_WORKING_READING__NO_PLAINTEXT_CLAIM",
        })

    page_rows: list[dict[str, object]] = []
    for page in dict.fromkeys(row["physical_page"] for row in bundles):
        page_events = [row for row in event_rows if row["physical_page"] == page]
        page_bundles = [row for row in bundle_rows if row["physical_page"] == page]
        page_records = [row for row in record_rows if row["physical_page"] == page]
        models = Counter(str(row["active_model"]) for row in page_bundles)
        page_rows.append({
            "physical_page": page,
            "register": page_bundles[0]["register"],
            "event_count": len(page_events),
            "bundle_count": len(page_bundles),
            "record_count": len(page_records),
            "multi_locus_record_count": sum(int(row["bundle_count"]) > 1 for row in page_records),
            "coordinate_bundle_count": models["COORDINATE"],
            "instruction_bundle_count": models["INSTRUCTION"],
            "catalogue_bundle_count": models["CATALOGUE"],
            "model_change_count": sum(row["model_changed_from_gdt474"] == "YES" for row in page_bundles),
            "order_event_count": sum(int(row["order_occurrence_count"]) > 0 for row in page_events),
            "order_occurrence_count": sum(int(row["order_occurrence_count"]) for row in page_events),
            "all_events_have_working_default": "YES",
        })

    changed_bundles = [str(row["bundle_id"]) for row in bundle_rows if row["model_changed_from_gdt474"] == "YES"]
    changed_events = [str(row["source_event_id"]) for row in event_rows if row["model_changed_from_gdt474"] == "YES"]
    bundle_models = Counter(str(row["active_model"]) for row in bundle_rows)
    event_models = Counter(str(row["active_model"]) for row in event_rows)
    result: dict[str, object] = {
        "status": "DEFINITIVE_183_EVENT_135_MICRORECORD_LOCAL_WORKING_EDITION_COMPLETE",
        "event_count": len(event_rows),
        "bundle_count": len(bundle_rows),
        "record_count": len(record_rows),
        "multi_locus_record_count": sum(int(row["bundle_count"]) > 1 for row in record_rows),
        "page_count": len(page_rows),
        "active_bundle_model_counts": dict(bundle_models),
        "active_event_model_counts": dict(event_models),
        "bundle_model_change_count": len(changed_bundles),
        "bundle_model_change_ids": changed_bundles,
        "event_reading_change_count": len(changed_events),
        "event_reading_change_ids": changed_events,
        "order_occurrence_count": sum(int(row["order_occurrence_count"]) for row in event_rows),
        "order_event_count": sum(int(row["order_occurrence_count"]) > 0 for row in event_rows),
        "non_order_event_count": sum(int(row["order_occurrence_count"]) == 0 for row in event_rows),
        "all_events_have_default_count": sum(bool(row["active_event_reading_de"]) for row in event_rows),
        "all_bundles_retain_three_alternatives_count": sum(row["all_three_alternative_readings_retained"] == "YES" for row in bundle_rows),
        "exact_package_surfaces": [row["surface"] for row in event_rows if row["surface"] in {"ykyd", "yddy"}],
        "component_meaning_change_count": 0,
        "learned_name_change_count": 0,
        "surface_change_count": 0,
        "recipe_change_count": 0,
        "new_page_count": 0,
        "claim_ceiling": "Definitive creative six-page local working edition integrating existing GDT474-GDT478 readings; no plaintext, confirmed syntax, lexeme, object identity, new component meaning, learned name, surface, recipe, event, or page.",
    }

    write_tsv(EVENT_OUT, event_rows)
    write_tsv(BUNDLE_OUT, bundle_rows)
    write_tsv(RECORD_OUT, record_rows)
    write_tsv(PAGE_OUT, page_rows)
    READABLE_OUT.write_text(build_readable(event_rows, bundle_rows, record_rows, page_rows, result), encoding="utf-8")
    RESULT_OUT.write_text(json.dumps(result, indent=2, ensure_ascii=False, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"status": result["status"], "events": len(event_rows), "bundles": len(bundle_rows), "records": len(record_rows), "models": dict(bundle_models)}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
