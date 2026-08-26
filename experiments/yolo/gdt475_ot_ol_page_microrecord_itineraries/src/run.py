#!/usr/bin/env python3
"""Trace OT/OL over GDT474 bundles and compile six page itineraries."""

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
BASE = ROOT / "experiments/yolo/gdt475_ot_ol_page_microrecord_itineraries"
OUT = BASE / "artifacts"
BUNDLES = ROOT / "experiments/yolo/gdt474_locus_bundle_meaning_triptych/artifacts/gdt474_146_locus_bundle_meaning_triptych.tsv"
EVENTS = ROOT / "experiments/yolo/gdt474_locus_bundle_meaning_triptych/artifacts/gdt474_183_event_meaning_triptych.tsv"
ORDER_PROFILES = ROOT / "experiments/yolo/gdt429_nonaction_core_semantic_contrasts/artifacts/gdt429_10_nonaction_semantic_profiles.tsv"

BOUNDARIES_OUT = OUT / "gdt475_146_bundle_boundary_roles.tsv"
ORDER_OUT = OUT / "gdt475_69_order_occurrence_positions.tsv"
RECORDS_OUT = OUT / "gdt475_135_page_microrecords.tsv"
CHAINS_OUT = OUT / "gdt475_8_cross_locus_continuation_chains.tsv"
PAGES_OUT = OUT / "gdt475_6_page_itinerary_summary.tsv"
READABLE_OUT = OUT / "GDT475_SIX_PAGE_MICRORECORD_ITINERARIES.md"
RESULT_OUT = OUT / "gdt475_result.json"

ORDER_MEANING = {"OT": "DANACH", "OL": "FORTSETZEN"}


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


def event_atoms(event: dict[str, str]) -> list[str]:
    return [] if event["working_recipe"] == "NONE" else event["working_recipe"].split("+")


def order_occurrences(events: list[dict[str, str]]) -> list[tuple[int, int, str]]:
    found: list[tuple[int, int, str]] = []
    for event_index, event in enumerate(events):
        for atom_index, atom in enumerate(event_atoms(event)):
            if atom in ORDER_MEANING:
                found.append((event_index, atom_index, atom))
    return found


def leading_root(events: list[dict[str, str]]) -> str:
    if not events:
        return "NONE"
    atoms = event_atoms(events[0])
    return atoms[0] if atoms else "NONE"


def boundary_role(page_ordinal: int, lead: str, occurrences: list[tuple[int, int, str]]) -> str:
    if page_ordinal == 1:
        return "PAGE_START"
    if lead == "OT":
        return "EXPLICIT_NEXT_SIBLING_OT"
    if lead == "OL":
        return "EXPLICIT_CONTINUATION_OL"
    if occurrences:
        return "UNMARKED_NEW_LOCUS_WITH_INTERNAL_CONTROL"
    return "UNMARKED_NEW_LOCUS"


def boundary_phrase(role: str) -> str:
    return {
        "PAGE_START": "Seitenbeginn",
        "EXPLICIT_NEXT_SIBLING_OT": "Danach: nächster gleichrangiger Eintrag",
        "EXPLICIT_CONTINUATION_OL": "Fortsetzung desselben Mikroregisters",
        "UNMARKED_NEW_LOCUS_WITH_INTERNAL_CONTROL": "Neuer sichtbarer Locus; Reihenfolge bleibt kartenintern",
        "UNMARKED_NEW_LOCUS": "Neuer sichtbarer Locus",
    }[role]


def occurrence_position(event_index: int, atom_index: int) -> str:
    if event_index == 0 and atom_index == 0:
        return "BUNDLE_LEADING"
    if atom_index == 0:
        return "LATER_EVENT_LEADING"
    return "EVENT_INTERNAL"


def occurrence_interpretation(root: str, position: str, page_ordinal: int) -> str:
    if root == "OT":
        if position == "BUNDLE_LEADING" and page_ordinal == 1:
            return "PAGE_INITIAL_FOLLOW_FRAME"
        if position == "BUNDLE_LEADING":
            return "NEXT_SIBLING_RECORD"
        return "NEXT_SIBLING_WITHIN_LOCUS"
    if position == "BUNDLE_LEADING":
        return "CONTINUE_PREVIOUS_RECORD"
    if position == "LATER_EVENT_LEADING":
        return "CONTINUE_WITHIN_LOCUS"
    return "CONTINUE_ACTIVE_CARD_OR_QUALIFIER"


def markdown_escape(value: object) -> str:
    return str(value).replace("|", "\\|").replace("\n", " ")


def build_readable(
    boundary_rows: list[dict[str, object]],
    record_rows: list[dict[str, object]],
    chain_rows: list[dict[str, object]],
    page_rows: list[dict[str, object]],
    result: dict[str, object],
) -> str:
    boundaries_by_record: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in boundary_rows:
        boundaries_by_record[str(row["record_id"])].append(row)
    records_by_page: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in record_rows:
        records_by_page[str(row["physical_page"])].append(row)
    page_summary = {str(row["physical_page"]): row for row in page_rows}

    lines = [
        "# GDT475 — sechs Seiten-Itinerarien des lokalen Mikroregisters",
        "",
        "`OT=DANACH` und `OL=FORTSETZEN` werden hier nicht neu übersetzt, sondern an ihrer tatsächlichen Stelle im Locus-Strom gelesen. OT eröffnet immer ein Ereignis. OL kann ein Folgebündel eröffnen oder innerhalb einer Karte den aktiven Bezug halten.",
        "",
        "| Reihenfolgezeichen | gesamt | Bündelanfang | spätere Karte beginnt | kartenintern |",
        "|---|---:|---:|---:|---:|",
        f"| OT / DANACH | {result['order_position_counts']['OT']['TOTAL']} | {result['order_position_counts']['OT']['BUNDLE_LEADING']} | {result['order_position_counts']['OT']['LATER_EVENT_LEADING']} | {result['order_position_counts']['OT']['EVENT_INTERNAL']} |",
        f"| OL / FORTSETZEN | {result['order_position_counts']['OL']['TOTAL']} | {result['order_position_counts']['OL']['BUNDLE_LEADING']} | {result['order_position_counts']['OL']['LATER_EVENT_LEADING']} | {result['order_position_counts']['OL']['EVENT_INTERNAL']} |",
        "",
        f"Aus 146 sichtbaren Locus-Bündeln entstehen 135 Mikroregister. Elf führende OL-Bündel hängen sich als Fortsetzung an den Vorgänger; sie bilden acht echte Mehrlocus-Ketten.",
        "",
        "## Die acht expliziten Fortsetzungsketten",
        "",
        "| Seite | Register | Loci | Formen | Arbeitslesung |",
        "|---|---|---|---|---|",
    ]
    for row in chain_rows:
        lines.append(
            f"| {row['physical_page']} | {row['record_id']} | {markdown_escape(row['locus_sequence'])} | `{markdown_escape(str(row['surface_sequence']).replace('|', ' · '))}` | {markdown_escape(row['record_reading_de'])} |"
        )
    lines.append("")

    for page, records in records_by_page.items():
        summary = page_summary[page]
        lines.extend([
            f"## {page}",
            "",
            f"{summary['bundle_count']} Locus-Bündel → {summary['record_count']} Mikroregister; {summary['explicit_ot_next_count']} explizite OT-Geschwister, {summary['explicit_ol_continuation_count']} OL-Fortsetzungen und {summary['internal_order_bundle_count']} Bündel mit einem nicht führenden Reihenfolgezeichen.",
            "",
        ])
        for record in records:
            bundled = boundaries_by_record[str(record["record_id"])]
            start = bundled[0]
            lines.extend([
                f"### {record['page_record_ordinal']}. {record['record_id']} — {boundary_phrase(str(start['boundary_role']))}",
                "",
            ])
            for bundle in bundled:
                continuation = "↳ " if int(bundle["bundle_ordinal_in_record"]) > 1 else ""
                lines.append(
                    f"- {continuation}{bundle['locus']} · `{str(bundle['surface_sequence']).replace('|', ' · ')}` · {bundle['selected_model']}: {bundle['selected_bundle_reading_de']}"
                )
            lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    bundles = read_tsv(BUNDLES)
    events = read_tsv(EVENTS)
    profiles = {row["core_root"]: row for row in read_tsv(ORDER_PROFILES)}
    if len(bundles) != 146 or len(events) != 183:
        raise RuntimeError("GDT474 input size drift")
    if {root: profiles[root]["working_meaning_de"] for root in ORDER_MEANING} != ORDER_MEANING:
        raise RuntimeError("OT/OL meaning drift")

    events_by_bundle: dict[str, list[dict[str, str]]] = defaultdict(list)
    for event in events:
        events_by_bundle[event["bundle_id"]].append(event)
    if set(events_by_bundle) != {row["bundle_id"] for row in bundles}:
        raise RuntimeError("Bundle/event join drift")

    bundles_by_page: dict[str, list[dict[str, str]]] = defaultdict(list)
    for bundle in bundles:
        bundles_by_page[bundle["physical_page"]].append(bundle)

    boundary_rows: list[dict[str, object]] = []
    occurrence_rows: list[dict[str, object]] = []
    record_build: list[dict[str, object]] = []
    record_counter = 0
    occurrence_counter = 0

    for page, page_bundles in bundles_by_page.items():
        page_record_ordinal = 0
        active_record_id = ""
        active_record: dict[str, object] | None = None
        previous_bundle_id = "NONE"
        for page_ordinal, bundle in enumerate(page_bundles, start=1):
            bundle_events = events_by_bundle[bundle["bundle_id"]]
            lead = leading_root(bundle_events)
            occurrences = order_occurrences(bundle_events)
            role = boundary_role(page_ordinal, lead, occurrences)
            begins_record = page_ordinal == 1 or lead != "OL"
            if begins_record:
                record_counter += 1
                page_record_ordinal += 1
                active_record_id = f"G475-R{record_counter:03d}"
                active_record = {
                    "record_id": active_record_id,
                    "record_ordinal": record_counter,
                    "physical_page": page,
                    "register": bundle["register"],
                    "page_record_ordinal": page_record_ordinal,
                    "record_start_role": role,
                    "bundle_ids": [],
                    "loci": [],
                    "surfaces": [],
                    "selected_models": [],
                    "selected_readings": [],
                    "boundary_roles": [],
                    "internal_order_roots": [],
                }
                record_build.append(active_record)
            if active_record is None:
                raise RuntimeError("Missing active record")
            active_record["bundle_ids"].append(bundle["bundle_id"])
            active_record["loci"].append(bundle["locus"])
            active_record["surfaces"].append(bundle["surface_sequence"])
            active_record["selected_models"].append(bundle["selected_model"])
            active_record["selected_readings"].append(bundle["selected_bundle_reading_de"])
            active_record["boundary_roles"].append(role)
            active_record["internal_order_roots"].extend(
                root for event_index, atom_index, root in occurrences if not (event_index == 0 and atom_index == 0)
            )

            boundary_rows.append({
                "boundary_id": f"G475-B{int(bundle['bundle_ordinal']):03d}",
                "bundle_id": bundle["bundle_id"],
                "physical_page": page,
                "register": bundle["register"],
                "page_bundle_ordinal": page_ordinal,
                "locus": bundle["locus"],
                "owner_de": bundle["owner_de"],
                "previous_bundle_id": previous_bundle_id,
                "surface_sequence": bundle["surface_sequence"],
                "recipe_sequence": bundle["recipe_sequence"],
                "leading_root": lead,
                "leading_root_meaning_de": ORDER_MEANING.get(lead, "NONE"),
                "order_occurrence_trace": "|".join(f"E{event_index + 1}:A{atom_index + 1}:{root}" for event_index, atom_index, root in occurrences) or "NONE",
                "boundary_role": role,
                "begins_new_record": "YES" if begins_record else "NO",
                "record_id": active_record_id,
                "page_record_ordinal": page_record_ordinal,
                "bundle_ordinal_in_record": len(active_record["bundle_ids"]),
                "selected_model": bundle["selected_model"],
                "selected_bundle_reading_de": bundle["selected_bundle_reading_de"],
                "itinerary_line_de": f"{boundary_phrase(role)} — {bundle['selected_bundle_reading_de']}",
                "claim_status": "ORDER_ROLE_WORKING_READING__NO_ROOT_OR_NAME_CHANGE",
            })

            for event_index, atom_index, root in occurrences:
                occurrence_counter += 1
                event = bundle_events[event_index]
                position = occurrence_position(event_index, atom_index)
                occurrence_rows.append({
                    "order_occurrence_id": f"G475-O{occurrence_counter:03d}",
                    "root": root,
                    "working_meaning_de": ORDER_MEANING[root],
                    "bundle_id": bundle["bundle_id"],
                    "record_id": active_record_id,
                    "physical_page": page,
                    "locus": bundle["locus"],
                    "source_event_id": event["source_event_id"],
                    "surface": event["surface"],
                    "working_recipe": event["working_recipe"],
                    "event_ordinal_in_bundle": event_index + 1,
                    "atom_ordinal_in_event": atom_index + 1,
                    "position_role": position,
                    "stream_interpretation": occurrence_interpretation(root, position, page_ordinal),
                    "component_meaning_change": "NO",
                })
            previous_bundle_id = bundle["bundle_id"]

    bundles_per_record = Counter(row["record_id"] for row in boundary_rows)
    for row in boundary_rows:
        row["record_bundle_count"] = bundles_per_record[str(row["record_id"])]

    record_rows: list[dict[str, object]] = []
    for record in record_build:
        readings = list(record["selected_readings"])
        record_reading = str(readings[0])
        if len(readings) > 1:
            record_reading += " " + " ".join(f"Fortsetzung {index}: {reading}" for index, reading in enumerate(readings[1:], start=1))
        record_rows.append({
            "record_id": record["record_id"],
            "record_ordinal": record["record_ordinal"],
            "physical_page": record["physical_page"],
            "register": record["register"],
            "page_record_ordinal": record["page_record_ordinal"],
            "record_start_role": record["record_start_role"],
            "bundle_count": len(record["bundle_ids"]),
            "bundle_ids": "|".join(record["bundle_ids"]),
            "locus_sequence": "|".join(record["loci"]),
            "surface_sequence": "|".join(record["surfaces"]),
            "selected_model_sequence": "|".join(record["selected_models"]),
            "boundary_role_sequence": "|".join(record["boundary_roles"]),
            "internal_order_root_trace": "|".join(record["internal_order_roots"]) or "NONE",
            "continuation_bundle_count": len(record["bundle_ids"]) - 1,
            "record_chain_class": {1: "SINGLE_LOCUS_RECORD", 2: "TWO_LOCUS_CONTINUATION_CHAIN", 3: "THREE_LOCUS_CONTINUATION_CHAIN"}[len(record["bundle_ids"])],
            "record_reading_de": record_reading,
            "claim_status": "PAGE_ITINERARY_WORKING_RECORD__NO_PLAINTEXT_CLAIM",
        })

    chain_rows: list[dict[str, object]] = []
    for chain_ordinal, row in enumerate((row for row in record_rows if int(row["bundle_count"]) > 1), start=1):
        chain_rows.append({
            "continuation_chain_id": f"G475-C{chain_ordinal:02d}",
            "record_id": row["record_id"],
            "physical_page": row["physical_page"],
            "register": row["register"],
            "bundle_count": row["bundle_count"],
            "bundle_ids": row["bundle_ids"],
            "locus_sequence": row["locus_sequence"],
            "surface_sequence": row["surface_sequence"],
            "selected_model_sequence": row["selected_model_sequence"],
            "explicit_ol_join_count": int(row["bundle_count"]) - 1,
            "record_reading_de": row["record_reading_de"],
        })

    boundary_counts = Counter(str(row["boundary_role"]) for row in boundary_rows)
    position_counts: dict[str, Counter[str]] = {"OT": Counter(), "OL": Counter()}
    for row in occurrence_rows:
        position_counts[str(row["root"])][str(row["position_role"])] += 1
        position_counts[str(row["root"])]["TOTAL"] += 1

    page_rows: list[dict[str, object]] = []
    for page, page_bundles in bundles_by_page.items():
        selected_boundaries = [row for row in boundary_rows if row["physical_page"] == page]
        selected_records = [row for row in record_rows if row["physical_page"] == page]
        selected_occurrences = [row for row in occurrence_rows if row["physical_page"] == page]
        page_rows.append({
            "physical_page": page,
            "register": page_bundles[0]["register"],
            "bundle_count": len(selected_boundaries),
            "event_count": sum(int(row["event_count"]) for row in page_bundles),
            "record_count": len(selected_records),
            "multi_locus_record_count": sum(int(row["bundle_count"]) > 1 for row in selected_records),
            "explicit_ot_next_count": sum(row["boundary_role"] == "EXPLICIT_NEXT_SIBLING_OT" for row in selected_boundaries),
            "explicit_ol_continuation_count": sum(row["boundary_role"] == "EXPLICIT_CONTINUATION_OL" for row in selected_boundaries),
            "unmarked_new_locus_count": sum(str(row["boundary_role"]).startswith("UNMARKED_NEW_LOCUS") for row in selected_boundaries),
            "internal_order_bundle_count": sum(any(not (event_index == 0 and atom_index == 0) for event_index, atom_index, _ in order_occurrences(events_by_bundle[row["bundle_id"]])) for row in page_bundles),
            "ot_occurrence_count": sum(row["root"] == "OT" for row in selected_occurrences),
            "ol_occurrence_count": sum(row["root"] == "OL" for row in selected_occurrences),
            "itinerary_complete": "YES",
        })

    record_size_counts = Counter(int(row["bundle_count"]) for row in record_rows)
    result = {
        "status": "OT_OPENS_EVENTS_AND_NEXT_SIBLINGS__OL_CONTINUES_RECORDS_OR_STAYS_INTERNAL",
        "event_count": len(events),
        "bundle_count": len(boundary_rows),
        "page_count": len(page_rows),
        "order_occurrence_count": len(occurrence_rows),
        "order_position_counts": {
            root: {key: position_counts[root].get(key, 0) for key in ("TOTAL", "BUNDLE_LEADING", "LATER_EVENT_LEADING", "EVENT_INTERNAL")}
            for root in ("OT", "OL")
        },
        "boundary_role_counts": dict(boundary_counts),
        "bundles_with_any_order_control": sum(bool(order_occurrences(events_by_bundle[row["bundle_id"]])) for row in bundles),
        "bundles_with_nonleading_order_control": sum(any(not (event_index == 0 and atom_index == 0) for event_index, atom_index, _ in order_occurrences(events_by_bundle[row["bundle_id"]])) for row in bundles),
        "record_count": len(record_rows),
        "record_size_counts": {str(size): count for size, count in sorted(record_size_counts.items())},
        "multi_locus_continuation_chain_count": len(chain_rows),
        "bundles_in_multi_locus_chains": sum(int(row["bundle_count"]) for row in chain_rows),
        "explicit_ol_continuation_join_count": sum(int(row["explicit_ol_join_count"]) for row in chain_rows),
        "component_meaning_change_count": 0,
        "learned_name_change_count": 0,
        "selected_model_change_count": 0,
        "new_page_count": 0,
        "interpretation": "OT_IS_AN_EVENT_OPENING_SIBLING_OPERATOR__OL_IS_A_CONTINUATION_OPERATOR_AT_RECORD_OR_CARD_SCOPE",
    }

    write_tsv(BOUNDARIES_OUT, boundary_rows)
    write_tsv(ORDER_OUT, occurrence_rows)
    write_tsv(RECORDS_OUT, record_rows)
    write_tsv(CHAINS_OUT, chain_rows)
    write_tsv(PAGES_OUT, page_rows)
    READABLE_OUT.write_text(build_readable(boundary_rows, record_rows, chain_rows, page_rows, result), encoding="utf-8")
    RESULT_OUT.write_text(json.dumps(result, indent=2, ensure_ascii=False, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
