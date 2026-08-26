#!/usr/bin/env python3
"""Compile all 135 fixed microrecords with their strongest support provenance."""

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
BASE = ROOT / "experiments/yolo/gdt484_complete_microrecord_provenance_edition"
OUT = BASE / "artifacts"
G479 = ROOT / "experiments/yolo/gdt479_definitive_local_microrecord_edition/artifacts"
G480 = ROOT / "experiments/yolo/gdt480_microrecord_template_atlas/artifacts"
G481 = ROOT / "experiments/yolo/gdt481_microrecord_fragment_grammar/artifacts"
G482 = ROOT / "experiments/yolo/gdt482_residual_event_component_tiles/artifacts"
G483 = ROOT / "experiments/yolo/gdt483_sodar_exact_running_carrier_closure/artifacts"
RECORDS_IN = G479 / "gdt479_135_definitive_microrecords.tsv"
EVENTS_IN = G479 / "gdt479_183_definitive_local_events.tsv"
TEMPLATES_IN = G480 / "gdt480_135_record_template_assignments.tsv"
COVERAGE_IN = G481 / "gdt481_135_record_fragment_coverage.tsv"
EVENT_FRAGMENTS_IN = G481 / "gdt481_183_event_fragment_assignments.tsv"
SEQUENCES_IN = G482 / "gdt482_183_event_component_sequences.tsv"
CONDITIONED_ATLAS_IN = G482 / "gdt482_model_conditioned_component_fragment_atlas.tsv"
FREE_ATLAS_IN = G482 / "gdt482_model_free_component_fragment_atlas.tsv"
TILES_IN = G482 / "gdt482_45_residual_event_internal_tiles.tsv"
CLOSURE_IN = G483 / "gdt483_45_residual_closure.tsv"
G483_RESULT_IN = G483 / "gdt483_result.json"
EVENT_SUPPORT = OUT / "gdt484_183_event_support_assignments.tsv"
MULTI_EVENT_TILES = OUT / "gdt484_7_multi_event_tail_component_tiles.tsv"
MULTI_RECORD_CLOSURE = OUT / "gdt484_3_multi_event_tail_closure.tsv"
RECORD_EDITION = OUT / "gdt484_135_record_provenance_edition.tsv"
TIER_SUMMARY = OUT / "gdt484_10_provenance_tier_summary.tsv"
PAGE_SUMMARY = OUT / "gdt484_6_page_summary.tsv"
READABLE = OUT / "GDT484_COMPLETE_135_RECORD_PROVENANCE_EDITION.md"
RESULT = OUT / "gdt484_result.json"

TIER_ORDER = (
    "RECURRENT_STRICT_WHOLE_RECORD",
    "RECURRENT_ROLE_WHOLE_RECORD",
    "ALL_EVENTS_STRICT_RECURRENT",
    "PARTIAL_STRICT_EVENT_RECURRENT",
    "ALL_EVENTS_ROLE_RECURRENT",
    "PARTIAL_ROLE_EVENT_RECURRENT",
    "SAME_MODEL_COMPONENT_TILE",
    "MODEL_FREE_COMPONENT_BACKOFF",
    "EXACT_RUNNING_CARRIER",
    "LEARNED_LEXICAL_SLOT",
)
TIER_LABELS = {
    "RECURRENT_STRICT_WHOLE_RECORD": "vollständiger Record wiederholt sich bedeutungsgleich",
    "RECURRENT_ROLE_WHOLE_RECORD": "vollständige Rollenform wiederholt sich",
    "ALL_EVENTS_STRICT_RECURRENT": "alle Events besitzen strikte Parallelträger",
    "PARTIAL_STRICT_EVENT_RECURRENT": "mindestens ein striktes Parallelevent",
    "ALL_EVENTS_ROLE_RECURRENT": "alle Events besitzen Rollenparallelen",
    "PARTIAL_ROLE_EVENT_RECURRENT": "mindestens ein Rollenparallelevent",
    "SAME_MODEL_COMPONENT_TILE": "vollständig aus Komponenten desselben Modells gebaut",
    "MODEL_FREE_COMPONENT_BACKOFF": "vollständig aus modellübergreifend wiederkehrenden Komponenten gebaut",
    "EXACT_RUNNING_CARRIER": "exakte laufende Oberfläche und Rezeptträger",
    "LEARNED_LEXICAL_SLOT": "funktional erklärt; gelernter Name/Familienname bleibt",
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


def span_text(tokens: list[str], separators: list[str], start: int, length: int) -> str:
    pieces = [tokens[start]]
    for index in range(start, start + length - 1):
        pieces.extend((" · " if separators[index] == "DOT" else " / ", tokens[index + 1]))
    return "".join(pieces)


def best_tile(sequence: dict[str, str], atlas: dict[object, dict[str, str]], conditioned: bool) -> tuple[tuple[int, int, int, int], list[dict[str, object]]]:
    tokens = sequence["semantic_tokens"].split("|")
    separators = [] if sequence["semantic_separators"] == "NONE" else sequence["semantic_separators"].split("|")
    event_id = sequence["source_event_id"]
    model = sequence["active_model"]
    dp: dict[int, tuple[tuple[int, int, int, int], list[dict[str, object]]]] = {len(tokens): ((0, 0, 0, 0), [])}
    for start in range(len(tokens) - 1, -1, -1):
        candidates: list[tuple[tuple[int, int, int, int], list[dict[str, object]]]] = []
        for length in range(min(3, len(tokens) - start), 0, -1):
            fragment = span_text(tokens, separators, start, length)
            key: object = (model, fragment) if conditioned else fragment
            support = atlas[key]
            donors = sorted(set(support["event_ids"].split("|")) - {event_id})
            if not donors and length > 1:
                continue
            recurrent = bool(donors)
            tail_score, tail = dp[start + length]
            score = (
                tail_score[0] + (length if recurrent else 0),
                tail_score[1] + (length if recurrent and length > 1 else 0),
                tail_score[2] + (length * length if recurrent else 0),
                tail_score[3] - 1,
            )
            segment = {"start": start, "length": length, "fragment": fragment, "donors": donors, "recurrent": recurrent}
            candidates.append((score, [segment, *tail]))
        dp[start] = max(candidates, key=lambda item: item[0])
    return dp[0]


def tile_class(token_count: int, covered: int, multi: int) -> str:
    if covered < token_count:
        return "LOCAL_TOKEN_REMAINS"
    if multi == token_count:
        return "FULL_RECURRENT_MULTI_FRAGMENT_TILE"
    if multi:
        return "MIXED_RECURRENT_MULTI_PLUS_ATOMS"
    return "RECURRENT_ATOMS_ONLY"


def trace(segments: list[dict[str, object]]) -> str:
    return " + ".join(
        f"[{segment['fragment']} ×{len(segment['donors'])}]" if segment["recurrent"] else f"[LOCAL:{segment['fragment']}]"
        for segment in segments
    )


def support_explanation(tier: str, template: dict[str, str], coverage: dict[str, str], extra: str) -> str:
    if tier == "RECURRENT_STRICT_WHOLE_RECORD":
        return f"Striktes Ganzrecord-Template {template['strict_template_id']} trägt {template['strict_template_record_count']} Records."
    if tier == "RECURRENT_ROLE_WHOLE_RECORD":
        return f"Rollenform {template['role_shape_id']} trägt {template['role_shape_record_count']} Records; der genaue Inhalt bleibt lokal."
    if tier == "ALL_EVENTS_STRICT_RECURRENT":
        return f"Alle {coverage['event_count']} Events besitzen strikte Bedeutungsparallelen."
    if tier == "PARTIAL_STRICT_EVENT_RECURRENT":
        return f"{coverage['recurrent_strict_event_count']}/{coverage['event_count']} Events besitzen strikte Bedeutungsparallelen."
    if tier == "ALL_EVENTS_ROLE_RECURRENT":
        return f"Alle {coverage['event_count']} Events besitzen Rollenparallelen."
    if tier == "PARTIAL_ROLE_EVENT_RECURRENT":
        return f"{coverage['recurrent_role_event_count']}/{coverage['event_count']} Events besitzen Rollenparallelen."
    if tier == "SAME_MODEL_COMPONENT_TILE":
        return "Alle Bedeutungsbausteine haben andere Träger im selben Koordinaten-, Anweisungs- oder Katalogmodell." + (f" {extra}" if extra else "")
    if tier == "MODEL_FREE_COMPONENT_BACKOFF":
        return "Alle Bedeutungsbausteine wiederholen sich; mindestens einer braucht einen markierten Rückgriff auf ein anderes Modell."
    if tier == "EXACT_RUNNING_CARRIER":
        return "`sodar=S+O+DA+R` hat exakte laufende Träger auf f67r2 und f77r."
    if tier == "LEARNED_LEXICAL_SLOT":
        return "Die Funktionsstruktur ist erklärt; lokal bleibt nur ein gelernter Name oder Familienname."
    raise RuntimeError(tier)


def build_readable(records: list[dict[str, object]], tier_rows: list[dict[str, object]], multi_rows: list[dict[str, object]], result: dict[str, object]) -> str:
    lines = [
        "# GDT484 — vollständige 135-Record-Ausgabe mit Herkunftsstufen",
        "",
        "Jeder der 135 GDT479-Mikrorecords behält seine konkrete Lesung und erhält zusätzlich die stärkste bereits vorhandene interne Stütze. Eine niedrigere Stufe bedeutet nicht „unübersetzt“; sie sagt nur, woher die gegenwärtige Arbeitslesung ihre nächste Parallele bekommt.",
        "",
        "| Rang | stärkste Stütze | Records |",
        "|---:|---|---:|",
    ]
    for row in tier_rows:
        lines.append(f"| {row['tier_rank']} | {row['tier_label_de']} | {row['record_count']} |")
    lines.extend([
        "",
        "Die 48 früheren Fragmenttails sind vollständig aufgeteilt: 42 Records haben Komponentenparallelen im selben Modell, drei brauchen nur modellfreien Komponenten-Backoff, `sodar` hat zwei exakte Laufträger, und zwei behalten erwartete gelernte Lexikalslots. Ungeklärte Funktionsreste: **0**.",
        "",
        "## Die drei mehrteiligen Fragmenttails",
        "",
        "| Record | Events | Komponenten | im selben Modell getragen |",
        "|---|---:|---:|---:|",
    ])
    for row in multi_rows:
        lines.append(f"| `{row['record_id']}` · `{row['surface_sequence']}` | {row['event_count']} | {row['total_component_count']} | {row['conditioned_recurrent_component_count']} |")
    lines.extend([
        "",
        "Damit sind auch `ochey|fydy`, `aral|oletal` und `okchshy|qkol|oldam` keine ungeteilten lokalen Sätze: Alle zwanzig ihrer Komponenten besitzen andere Träger im selben aktiven Modell.",
        "",
        "## Alle 135 Records",
        "",
    ])
    current_page = None
    for row in records:
        if row["physical_page"] != current_page:
            current_page = row["physical_page"]
            lines.extend([f"### {current_page} · {row['register']}", ""])
        lines.extend([
            f"#### {row['record_id']} · `{row['surface_sequence']}`",
            "",
            f"- Modellfolge: `{row['active_model_sequence']}`; Events: {row['event_count']}.",
            f"- Herkunftsstufe {row['support_tier_rank']}: **{row['support_tier_label_de']}**.",
            f"- Begründung: {row['support_explanation_de']}",
            f"- Lesung: {row['current_record_reading_de']}",
            "",
        ])
    lines.extend([
        "Die Ausgabe ändert keine Komponente, kein Modell, keine Oberfläche und keine Recordgrenze. Nur die bereits in GDT483 geglättete `sodar`-Paraphrase ersetzt einmal die ältere Wiederholung von „den Eintrag“.",
        "",
    ])
    return "\n".join(lines)


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    records = read_tsv(RECORDS_IN)
    events = read_tsv(EVENTS_IN)
    templates = read_tsv(TEMPLATES_IN)
    coverage = read_tsv(COVERAGE_IN)
    fragments = read_tsv(EVENT_FRAGMENTS_IN)
    sequences = read_tsv(SEQUENCES_IN)
    conditioned_atlas_rows = read_tsv(CONDITIONED_ATLAS_IN)
    free_atlas_rows = read_tsv(FREE_ATLAS_IN)
    tiles = read_tsv(TILES_IN)
    closure = read_tsv(CLOSURE_IN)
    g483_result = json.loads(G483_RESULT_IN.read_text(encoding="utf-8"))
    if tuple(map(len, (records, events, templates, coverage, fragments, sequences, tiles, closure))) != (135, 183, 135, 135, 183, 183, 45, 45):
        raise RuntimeError("Input count drift")

    template_map = {row["record_id"]: row for row in templates}
    coverage_map = {row["record_id"]: row for row in coverage}
    fragment_map = {row["source_event_id"]: row for row in fragments}
    sequence_map = {row["source_event_id"]: row for row in sequences}
    tile_map = {row["source_event_id"]: row for row in tiles}
    closure_map = {row["source_event_id"]: row for row in closure}
    conditioned_atlas = {(row["active_model"], row["semantic_fragment"]): row for row in conditioned_atlas_rows}
    free_atlas = {row["semantic_fragment"]: row for row in free_atlas_rows}
    events_by_record: dict[str, list[dict[str, str]]] = defaultdict(list)
    for event in events:
        events_by_record[event["record_id"]].append(event)

    multi_tail_record_ids = {
        row["record_id"] for row in coverage
        if row["decomposition_class"] == "SINGLETON_FRAGMENT_TAIL" and int(row["event_count"]) > 1
    }
    if multi_tail_record_ids != {"G475-R074", "G475-R084", "G475-R107"}:
        raise RuntimeError("Multi-event residual selection drift")

    multi_event_rows: list[dict[str, object]] = []
    for record in records:
        if record["record_id"] not in multi_tail_record_ids:
            continue
        for event in events_by_record[record["record_id"]]:
            sequence = sequence_map[event["source_event_id"]]
            conditioned_score, conditioned_segments = best_tile(sequence, conditioned_atlas, True)
            free_score, free_segments = best_tile(sequence, free_atlas, False)
            token_count = int(sequence["token_count"])
            multi_event_rows.append({
                "tile_id": f"G484-ME{len(multi_event_rows) + 1:02d}",
                "record_id": record["record_id"],
                "source_event_id": event["source_event_id"],
                "physical_page": event["physical_page"],
                "register": event["register"],
                "active_model": event["active_model"],
                "surface": event["surface"],
                "working_recipe": event["working_recipe"],
                "semantic_tokens": sequence["semantic_tokens"],
                "token_count": token_count,
                "conditioned_recurrent_token_count": conditioned_score[0],
                "conditioned_multi_fragment_token_count": conditioned_score[1],
                "conditioned_tile_class": tile_class(token_count, conditioned_score[0], conditioned_score[1]),
                "conditioned_tile_trace": trace(conditioned_segments),
                "conditioned_local_tokens": "|".join(str(segment["fragment"]) for segment in conditioned_segments if not segment["recurrent"]) or "NONE",
                "free_recurrent_token_count": free_score[0],
                "free_multi_fragment_token_count": free_score[1],
                "free_tile_class": tile_class(token_count, free_score[0], free_score[1]),
                "free_tile_trace": trace(free_segments),
                "definitive_event_reading_de": event["definitive_event_reading_de"],
                "source_meaning_preserved": "YES",
            })
    if len(multi_event_rows) != 7 or any(int(row["conditioned_recurrent_token_count"]) != int(row["token_count"]) for row in multi_event_rows):
        raise RuntimeError("Multi-event component closure failure")

    multi_record_rows: list[dict[str, object]] = []
    for record in records:
        selected = [row for row in multi_event_rows if row["record_id"] == record["record_id"]]
        if not selected:
            continue
        multi_record_rows.append({
            "closure_id": f"G484-MR{len(multi_record_rows) + 1:02d}",
            "record_id": record["record_id"],
            "physical_page": record["physical_page"],
            "register": record["register"],
            "surface_sequence": record["surface_sequence"],
            "event_count": len(selected),
            "event_ids": "|".join(str(row["source_event_id"]) for row in selected),
            "total_component_count": sum(int(row["token_count"]) for row in selected),
            "conditioned_recurrent_component_count": sum(int(row["conditioned_recurrent_token_count"]) for row in selected),
            "conditioned_multi_fragment_component_count": sum(int(row["conditioned_multi_fragment_token_count"]) for row in selected),
            "all_events_conditioned_complete": "YES",
            "event_tile_classes": "|".join(str(row["conditioned_tile_class"]) for row in selected),
            "definitive_record_reading_de": record["definitive_record_reading_de"],
            "source_meaning_preserved": "YES",
        })

    multi_event_map = {str(row["source_event_id"]): row for row in multi_event_rows}
    event_support_rows: list[dict[str, object]] = []
    for event in events:
        fragment = fragment_map[event["source_event_id"]]
        if int(fragment["strict_occurrence_count"]) > 1:
            event_tier = "RECURRENT_STRICT_EVENT"
            detail = f"{fragment['strict_template_id']} ×{fragment['strict_occurrence_count']}"
        elif int(fragment["role_occurrence_count"]) > 1:
            event_tier = "RECURRENT_ROLE_EVENT"
            detail = f"{fragment['role_shape_id']} ×{fragment['role_occurrence_count']}"
        elif event["source_event_id"] in closure_map:
            closed = closure_map[event["source_event_id"]]
            event_tier = closed["gdt483_closure_class"]
            detail = closed["exact_running_donor_ids"] if closed["exact_running_donor_count"] != "0" else closed["remaining_local_lexical_slot"]
            if detail in {"NONE", "LOCAL_COMPONENT_ATLAS"} and event["source_event_id"] in tile_map:
                detail = tile_map[event["source_event_id"]]["free_tile_trace"]
        elif event["source_event_id"] in multi_event_map:
            event_tier = "SAME_MODEL_COMPONENT_TILE"
            detail = str(multi_event_map[event["source_event_id"]]["conditioned_tile_trace"])
        else:
            event_tier = "LOCAL_EVENT_CARRIED_BY_STRONGER_RECORD_SUPPORT"
            detail = "Record-level template or mixed fragment support"
        current_reading = g483_result["preferred_generic_reading_de"] if event["source_event_id"] == g483_result["target_event_id"] else event["definitive_event_reading_de"]
        event_support_rows.append({
            "assignment_id": f"G484-E{len(event_support_rows) + 1:03d}",
            "source_event_id": event["source_event_id"],
            "record_id": event["record_id"],
            "bundle_id": event["bundle_id"],
            "physical_page": event["physical_page"],
            "register": event["register"],
            "active_model": event["active_model"],
            "surface": event["surface"],
            "working_recipe": event["working_recipe"],
            "strict_template_id": fragment["strict_template_id"],
            "strict_occurrence_count": fragment["strict_occurrence_count"],
            "role_shape_id": fragment["role_shape_id"],
            "role_occurrence_count": fragment["role_occurrence_count"],
            "event_support_tier": event_tier,
            "event_support_detail": detail,
            "source_event_reading_de": event["definitive_event_reading_de"],
            "current_event_reading_de": current_reading,
            "reading_refined_by_gdt483": "YES" if event["source_event_id"] == g483_result["target_event_id"] else "NO",
            "provenance_assigned": "YES",
            "source_meaning_preserved": "YES",
        })

    record_rows: list[dict[str, object]] = []
    for record in records:
        template = template_map[record["record_id"]]
        record_coverage = coverage_map[record["record_id"]]
        record_events = events_by_record[record["record_id"]]
        extra = ""
        if int(template["strict_template_record_count"]) > 1:
            tier = TIER_ORDER[0]
        elif int(template["role_shape_record_count"]) > 1:
            tier = TIER_ORDER[1]
        elif record_coverage["all_events_strict_recurrent"] == "YES":
            tier = TIER_ORDER[2]
        elif int(record_coverage["recurrent_strict_event_count"]) > 0:
            tier = TIER_ORDER[3]
        elif record_coverage["all_events_role_recurrent"] == "YES":
            tier = TIER_ORDER[4]
        elif int(record_coverage["recurrent_role_event_count"]) > 0:
            tier = TIER_ORDER[5]
        elif record["record_id"] in multi_tail_record_ids:
            tier = TIER_ORDER[6]
            selected = next(row for row in multi_record_rows if row["record_id"] == record["record_id"])
            extra = f"{selected['conditioned_recurrent_component_count']}/{selected['total_component_count']} Komponenten."
        else:
            if len(record_events) != 1:
                raise RuntimeError(f"Unclassified non-single record {record['record_id']}")
            event_id = record_events[0]["source_event_id"]
            closed = closure_map[event_id]
            if closed["gdt483_closure_class"] == "LOCAL_COMPONENT_RECURRENT":
                interpretation = tile_map[event_id]["residual_interpretation"]
                tier = TIER_ORDER[6] if interpretation == "MODEL_CONDITIONED_RECURRENT" else TIER_ORDER[7]
            elif closed["gdt483_closure_class"] == "EXACT_RUNNING_SURFACE_RECIPE_CARRIER":
                tier = TIER_ORDER[8]
            elif closed["gdt483_closure_class"] == "LEARNED_LEXICAL_SLOT_ONLY":
                tier = TIER_ORDER[9]
            else:
                raise RuntimeError(f"Unknown closure class {closed}")
        current_reading = g483_result["preferred_generic_reading_de"] if record["record_id"] == "G475-R125" else record["definitive_record_reading_de"]
        event_support_ids = "|".join(row["event_support_tier"] for row in event_support_rows if row["record_id"] == record["record_id"])
        record_rows.append({
            "edition_id": f"G484-R{len(record_rows) + 1:03d}",
            "record_id": record["record_id"],
            "physical_page": record["physical_page"],
            "register": record["register"],
            "page_record_ordinal": record["page_record_ordinal"],
            "record_start_role": record["record_start_role"],
            "bundle_count": record["bundle_count"],
            "event_count": record["event_count"],
            "bundle_ids": record["bundle_ids"],
            "surface_sequence": record["surface_sequence"],
            "active_model_sequence": record["active_model_sequence"],
            "strict_template_id": template["strict_template_id"],
            "strict_template_record_count": template["strict_template_record_count"],
            "role_shape_id": template["role_shape_id"],
            "role_shape_record_count": template["role_shape_record_count"],
            "recurrent_strict_event_count": record_coverage["recurrent_strict_event_count"],
            "recurrent_role_event_count": record_coverage["recurrent_role_event_count"],
            "decomposition_class": record_coverage["decomposition_class"],
            "event_support_tiers": event_support_ids,
            "literal_name_slot_count": template["literal_name_slot_count"],
            "support_tier_rank": TIER_ORDER.index(tier) + 1,
            "support_tier": tier,
            "support_tier_label_de": TIER_LABELS[tier],
            "support_explanation_de": support_explanation(tier, template, record_coverage, extra),
            "source_record_reading_de": record["definitive_record_reading_de"],
            "current_record_reading_de": current_reading,
            "reading_refined_by_gdt483": "YES" if record["record_id"] == "G475-R125" else "NO",
            "all_events_have_default": record["all_events_have_default"],
            "provenance_complete": "YES",
            "source_meaning_preserved": "YES",
        })

    tier_counts = Counter(str(row["support_tier"]) for row in record_rows)
    tier_rows: list[dict[str, object]] = []
    for rank, tier in enumerate(TIER_ORDER, 1):
        selected = [row for row in record_rows if row["support_tier"] == tier]
        tier_rows.append({
            "tier_rank": rank,
            "support_tier": tier,
            "tier_label_de": TIER_LABELS[tier],
            "record_count": len(selected),
            "event_count": sum(int(row["event_count"]) for row in selected),
            "page_count": len({str(row["physical_page"]) for row in selected}),
            "register_count": len({str(row["register"]) for row in selected}),
            "record_ids": "|".join(str(row["record_id"]) for row in selected) or "NONE",
            "surface_examples": "|".join(str(row["surface_sequence"]) for row in selected[:12]) or "NONE",
        })

    page_rows: list[dict[str, object]] = []
    for page in dict.fromkeys(str(row["physical_page"]) for row in record_rows):
        selected = [row for row in record_rows if row["physical_page"] == page]
        page_rows.append({
            "physical_page": page,
            "register": selected[0]["register"],
            "record_count": len(selected),
            "event_count": sum(int(row["event_count"]) for row in selected),
            "name_slot_record_count": sum(int(row["literal_name_slot_count"]) > 0 for row in selected),
            "reading_refinement_count": sum(row["reading_refined_by_gdt483"] == "YES" for row in selected),
            **{f"tier_{rank:02d}_count": sum(row["support_tier"] == tier for row in selected) for rank, tier in enumerate(TIER_ORDER, 1)},
            "all_records_have_default": "YES",
            "all_records_have_provenance": "YES",
        })

    expected_tiers = {
        "RECURRENT_STRICT_WHOLE_RECORD": 28,
        "RECURRENT_ROLE_WHOLE_RECORD": 23,
        "ALL_EVENTS_STRICT_RECURRENT": 4,
        "PARTIAL_STRICT_EVENT_RECURRENT": 19,
        "ALL_EVENTS_ROLE_RECURRENT": 6,
        "PARTIAL_ROLE_EVENT_RECURRENT": 7,
        "SAME_MODEL_COMPONENT_TILE": 42,
        "MODEL_FREE_COMPONENT_BACKOFF": 3,
        "EXACT_RUNNING_CARRIER": 1,
        "LEARNED_LEXICAL_SLOT": 2,
    }
    if dict(tier_counts) != expected_tiers:
        raise RuntimeError(f"Tier profile drift: {tier_counts}")

    result: dict[str, object] = {
        "status": "ALL_135_MICRORECORDS_HAVE_READINGS_AND_SUPPORT_PROVENANCE__ZERO_FUNCTIONAL_RESIDUE",
        "record_count": len(record_rows),
        "event_count": len(event_support_rows),
        "page_count": len(page_rows),
        "provenance_tier_count": len(tier_rows),
        "tier_counts": expected_tiers,
        "whole_record_supported_record_count": tier_counts[TIER_ORDER[0]] + tier_counts[TIER_ORDER[1]],
        "event_fragment_supported_record_count": sum(tier_counts[tier] for tier in TIER_ORDER[2:6]),
        "same_model_component_supported_record_count": tier_counts[TIER_ORDER[6]],
        "model_free_component_backoff_record_count": tier_counts[TIER_ORDER[7]],
        "exact_running_carrier_record_count": tier_counts[TIER_ORDER[8]],
        "learned_lexical_slot_record_count": tier_counts[TIER_ORDER[9]],
        "multi_event_tail_record_count": len(multi_record_rows),
        "multi_event_tail_event_count": len(multi_event_rows),
        "multi_event_tail_component_count": sum(int(row["token_count"]) for row in multi_event_rows),
        "multi_event_tail_conditioned_recurrent_component_count": sum(int(row["conditioned_recurrent_token_count"]) for row in multi_event_rows),
        "all_records_have_concrete_default_count": sum(row["all_events_have_default"] == "YES" for row in record_rows),
        "all_records_have_support_provenance_count": sum(row["provenance_complete"] == "YES" for row in record_rows),
        "unexplained_functional_record_count": 0,
        "preferred_fluent_paraphrase_refinement_count": sum(row["reading_refined_by_gdt483"] == "YES" for row in record_rows),
        "refined_record_ids": [row["record_id"] for row in record_rows if row["reading_refined_by_gdt483"] == "YES"],
        "component_meaning_change_count": 0,
        "active_model_change_count": 0,
        "record_boundary_change_count": 0,
        "surface_change_count": 0,
        "recipe_change_count": 0,
        "page_change_count": 0,
        "claim_ceiling": "Support-provenance consolidation of the fixed GDT479 135-record edition using GDT480-GDT483; no new root, component meaning, syntax, plaintext, language, model, boundary, surface, recipe, event, or page.",
    }

    write_tsv(EVENT_SUPPORT, event_support_rows)
    write_tsv(MULTI_EVENT_TILES, multi_event_rows)
    write_tsv(MULTI_RECORD_CLOSURE, multi_record_rows)
    write_tsv(RECORD_EDITION, record_rows)
    write_tsv(TIER_SUMMARY, tier_rows)
    write_tsv(PAGE_SUMMARY, page_rows)
    READABLE.write_text(build_readable(record_rows, tier_rows, multi_record_rows, result), encoding="utf-8")
    RESULT.write_text(json.dumps(result, indent=2, ensure_ascii=False, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "status": result["status"],
        "records": result["record_count"],
        "tiers": expected_tiers,
        "multi_event_tail_components": result["multi_event_tail_component_count"],
        "unexplained_functional_records": result["unexplained_functional_record_count"],
    }, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
