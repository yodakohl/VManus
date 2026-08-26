#!/usr/bin/env python3
"""Test one-condition relaxations around GDT487's two action endpoints."""

from __future__ import annotations

import csv
import itertools
import json
import re
from collections import defaultdict
from pathlib import Path


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
BASE = ROOT / "experiments/yolo/gdt488_action_endpoint_single_relaxation_closure"
OUT = BASE / "artifacts"
G485 = ROOT / "experiments/yolo/gdt485_fluent_reversible_microrecord_edition/artifacts"
G486 = ROOT / "experiments/yolo/gdt486_fluent_frame_component_contrast_deck/artifacts"
G487 = ROOT / "experiments/yolo/gdt487_model_conditioned_realization_lexicon/artifacts"
G428 = ROOT / "experiments/yolo/gdt428_within_class_action_semantic_contrasts/artifacts"
RECORDS_IN = G485 / "gdt485_135_fluent_reversible_records.tsv"
EVENTS_IN = G485 / "gdt485_183_literal_backprojection_events.tsv"
STRICT_PAIRS_IN = G486 / "gdt486_48_register_minimal_pairs.tsv"
STRICT_RULES_IN = G486 / "gdt486_29_model_conditioned_contrast_rules.tsv"
LOCAL_EDGES_IN = G487 / "gdt487_13_local_recurrent_edges.tsv"
ACTION_FRAMES_IN = G428 / "gdt428_104_direct_substitution_frames.tsv"
REGISTER_ONLY = OUT / "gdt488_1_register_only_endpoint_pair.tsv"
EVENT_PAIRS = OUT / "gdt488_5_endpoint_event_minimal_pairs.tsv"
NEW_EVENT_PAIRS = OUT / "gdt488_3_new_event_projection_pairs.tsv"
EINSTELLEN_CARRIERS = OUT / "gdt488_2_einstellen_local_carriers.tsv"
CLOSURE_STATUS = OUT / "gdt488_2_endpoint_closure_status.tsv"
CAPACITY = OUT / "gdt488_2_endpoint_relaxation_capacity.tsv"
HALTEN_CYCLE = OUT / "gdt488_1_halten_cycle.tsv"
READABLE = OUT / "GDT488_ACTION_ENDPOINT_SINGLE_RELAXATION_CLOSURE.md"
RESULT = OUT / "gdt488_result.json"
STATUS = "HALTEN_CYCLE_CLOSED__EINSTELLEN_REMAINS_CAPACITY_LIMITED"
ENDPOINTS = {"EINSTELLEN", "HALTEN"}
ACTIONS = {
    "SETZEN", "FORTSETZEN", "NEHMEN", "HALTEN", "GEBEN", "WÄHLEN",
    "BEARBEITEN", "EINSTELLEN", "MARKIEREN", "EINSETZEN",
}
SEMANTIC_CUES = {
    "BAHN": r"Bahn",
    "DANACH": r"Danach|danach|Folgevermerk|Folge-",
    "EINSTELLEN": r"stell",
    "HALTEN": r"halt",
    "HIER": r"bezeichnete[nr]? Stelle|Hier-Vermerk|\bhier\b",
    "SETZEN": r"setz|Ansatz",
    "ZIELORT": r"Ziel",
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


def tokens(event: dict[str, str]) -> list[str]:
    return event["semantic_tokens"].split("|")


def joins(event: dict[str, str]) -> list[str]:
    return [] if event["semantic_separators"] == "NONE" else event["semantic_separators"].split("|")


def render_event(parts: list[str], separators: list[str]) -> str:
    if not parts:
        return "NONE"
    rendered = [parts[0]]
    for separator, part in zip(separators, parts[1:]):
        rendered.extend((" · " if separator == "DOT" else " / ", part))
    return "".join(rendered)


def cue_visible(component: str, reading: str) -> bool:
    pattern = SEMANTIC_CUES.get(component)
    return bool(pattern and re.search(pattern, reading, flags=re.IGNORECASE))


def readable_frame_class(record: dict[str, str], local_events: list[dict[str, str]]) -> str:
    model = record["active_model_sequence"]
    fluent = record["fluent_reading_de"]
    if "|" in model:
        return "MULTI_EVENT_" + model
    if model == "INSTRUCTION":
        head = next((part for event in local_events for part in tokens(event) if part in ACTIONS), "NONE")
        return "INSTRUCTION_" + head
    if model == "CATALOGUE":
        if fluent.startswith("Katalogfolge:"):
            return "CATALOGUE_SEQUENCE"
        if "fortgesetzter Katalogeintrag" in fluent or "Führe den Katalog" in fluent:
            return "CATALOGUE_CONTINUATION"
        return "CATALOGUE_ENTRY"
    if model == "COORDINATE":
        if fluent.startswith(("Die erste", "Drei")):
            return "COORDINATE_MULTI"
        if fluent.startswith("Adressfolge:"):
            return "COORDINATE_SEQUENCE"
        if fluent.startswith("Danach"):
            return "COORDINATE_AFTER"
        return "COORDINATE_PATH"
    return model


def ordered_pair(
    left: dict[str, object],
    right: dict[str, object],
    changed_index: int,
    token_field: str,
) -> tuple[dict[str, object], dict[str, object], str, str]:
    left_value = str(left[token_field][changed_index])
    right_value = str(right[token_field][changed_index])
    if left_value <= right_value:
        return left, right, left_value, right_value
    return right, left, right_value, left_value


def build_readable(
    register_rows: list[dict[str, object]],
    event_rows: list[dict[str, object]],
    new_event_rows: list[dict[str, object]],
    carriers: list[dict[str, object]],
    closure_rows: list[dict[str, object]],
    cycle_rows: list[dict[str, object]],
    result: dict[str, object],
) -> str:
    lines = [
        "# GDT488 — Einmal gelockerte Aktionsendpunkte",
        "",
        "GDT488 lockert am GDT486-Paarbau immer nur eine Sache: entweder darf das Register wechseln, während der komplette Recordrahmen gleich bleibt, oder zwei einzelne Events dürfen aus ihrem größeren Recordrahmen heraus verglichen werden. Modell, Eventseparatoren, Komponentenpositionen und alle nicht gewechselten Komponenten bleiben fest.",
        "",
        f"- Register-only-Paare an den zwei Endpunkten: **{result['register_only_endpoint_pair_count']}**.",
        f"- Exakte Event-Minimalpaare: **{result['endpoint_event_pair_count']}**, davon **{result['new_event_projection_pair_count']}** neu gegenüber GDT486.",
        f"- `HALTEN`: **Zyklus geschlossen**; `EINSTELLEN`: **weiter kapazitätsbegrenzt**.",
        "",
        "## Der neue HALTEN-Zyklus",
        "",
    ]
    for row in cycle_rows:
        lines.extend([
            f"`{row['cycle_path_de']}`",
            "",
            f"Die neue Kante `{row['new_edge_record_pair']}` hält aktives Modell, Satzrahmen, Eventform und alle übrigen Komponenten fest. Nur das Register und damit die Besitzerart wechseln. Die Kante `{row['recurrent_bridge_edge']}` ist bereits {row['recurrent_bridge_pair_count']}fach wiederkehrend.",
            "",
        ])
    lines.extend([
        "### Register-only-Paar",
        "",
        "| Records | Register | Rahmen | Wechsel | Lesungen |",
        "|---|---|---|---|---|",
    ])
    for row in register_rows:
        lines.append(f"| `{row['source_record_id']} ↔ {row['target_record_id']}` | {row['source_register']} → {row['target_register']} | `{row['fluent_frame_class']}` | `{row['component_a']} ↔ {row['component_b']}` | {row['source_fluent_reading_de']} / {row['target_fluent_reading_de']} |")
    lines.extend([
        "",
        "### Neue Eventprojektionen",
        "",
        "| Events | Ort | Wechsel | Wildcard-Rahmen |",
        "|---|---|---|---|",
    ])
    for row in new_event_rows:
        lines.append(f"| `{row['source_event_id']} ↔ {row['target_event_id']}` | {row['source_physical_page']} / {row['target_physical_page']} | `{row['component_a']} ↔ {row['component_b']}` | `{row['wildcard_event_frame']}` |")
    lines.extend([
        "",
        "Damit erscheint HALTEN außer gegen ZIELORT nun auch gegen BAHN sowie auf Eventebene gegen DANACH und SETZEN. Die Eventpaare sind zusätzliche Redaktionskontraste; für den geschlossenen Weg genügt bereits das sauberere Register-only-Paar BAHN ↔ HALTEN.",
        "",
        "## Warum EINSTELLEN offen bleibt",
        "",
        "EINSTELLEN kommt in den 183 Events genau zweimal vor:",
        "",
        "| Event | Seite / Register | Rezept | Kontext | GDT428-Rahmen |",
        "|---|---|---|---|---|",
    ])
    for row in carriers:
        lines.append(f"| `{row['event_id']}` | {row['physical_page']} / {row['register']} | `{row['working_recipe']}` | `{row['action_context_frame']}` | `{row['exact_gdt428_tr_frame']}` |")
    lines.extend([
        "",
        "Der pharmazeutische Träger ist die bekannte GDT486-Kante EINSTELLEN ↔ HIER. Der celestialische Träger wiederholt NEHMEN→EINSTELLEN und trifft mit `CH+@ACTION` sogar einen exakten GDT428-T/R-Rahmen. Er liefert aber keinen zweiten lokalen Austauschpartner. Unter den beiden einmaligen Lockerungen entstehen daher **null** neue EINSTELLEN-Kontraste.",
        "",
        "Das ist kein Bedeutungsproblem: Die Lesung „einstellen“ bleibt zweimal lokal sichtbar und elf externe T/R-Rahmen trennen sie von MARKIEREN. Es fehlt lediglich ein zweiter lokaler Ersatzrahmen.",
        "",
        "## Endstand",
        "",
        "| Endpunkt | lokale Events | strikte GDT486-Kante | neue Kanten | Ergebnis |",
        "|---|---:|---|---|---|",
    ])
    for row in closure_rows:
        lines.append(f"| `{row['endpoint']}` | {row['local_event_count']} | `{row['strict_contrast_partner']}` | `{row['new_contrast_neighbours']}` | `{row['closure_status']}` |")
    lines.extend([
        "",
        "## Nächster Schritt",
        "",
        "HALTEN braucht keine weitere Lockerung. Für EINSTELLEN sollte der Ersatzgraph nicht nochmals verbreitert werden. Stattdessen ist sein bereits vorhandenes Kompositionsumfeld auszubauen: die elf GDT428-T/R-Rahmen nach ihren stabilen Nachbarn WERT, ANTEIL, ZIELORT, FORTSETZEN und POSTEN ordnen und prüfen, welche davon in den 183 lokalen Events bereits als unveränderte Teilrahmen auftauchen.",
        "",
    ])
    return "\n".join(lines)


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    source_records = read_tsv(RECORDS_IN)
    source_events = read_tsv(EVENTS_IN)
    strict_pairs = read_tsv(STRICT_PAIRS_IN)
    strict_rules = read_tsv(STRICT_RULES_IN)
    local_edges = read_tsv(LOCAL_EDGES_IN)
    action_frames = read_tsv(ACTION_FRAMES_IN)
    if (len(source_records), len(source_events), len(strict_pairs), len(strict_rules), len(local_edges), len(action_frames)) != (135, 183, 48, 29, 13, 104):
        raise RuntimeError("Input count drift")

    events_by_record: dict[str, list[dict[str, str]]] = defaultdict(list)
    for event in source_events:
        events_by_record[event["record_id"]].append(event)

    enriched_records: list[dict[str, object]] = []
    for source in source_records:
        row: dict[str, object] = dict(source)
        local_events = events_by_record[source["record_id"]]
        flat_tokens: list[str] = []
        offsets = [0]
        event_joins: list[list[str]] = []
        shape: list[str] = []
        for event in local_events:
            local_tokens = tokens(event)
            flat_tokens.extend(local_tokens)
            offsets.append(len(flat_tokens))
            event_joins.append(joins(event))
            shape.append(f"{len(local_tokens)}:{event['semantic_separators']}")
        row["flat_tokens"] = tuple(flat_tokens)
        row["event_offsets"] = tuple(offsets)
        row["event_joins"] = tuple(tuple(part) for part in event_joins)
        row["event_boundary_shape"] = "||".join(shape)
        row["fluent_frame_class"] = readable_frame_class(source, local_events)
        enriched_records.append(row)

    register_rows: list[dict[str, object]] = []
    for left, right in itertools.combinations(enriched_records, 2):
        if left["register"] == right["register"]:
            continue
        fixed = ("active_model_sequence", "fluent_frame_class", "event_boundary_shape")
        if any(left[field] != right[field] for field in fixed):
            continue
        if len(left["flat_tokens"]) != len(right["flat_tokens"]):
            continue
        differences = [index for index, pair in enumerate(zip(left["flat_tokens"], right["flat_tokens"])) if pair[0] != pair[1]]
        if len(differences) != 1:
            continue
        index = differences[0]
        if str(left["flat_tokens"][index]).startswith("{") or str(right["flat_tokens"][index]).startswith("{"):
            continue
        if not ({str(left["flat_tokens"][index]), str(right["flat_tokens"][index])} & ENDPOINTS):
            continue
        source, target, component_a, component_b = ordered_pair(left, right, index, "flat_tokens")
        wildcard = list(source["flat_tokens"])
        wildcard[index] = "*"
        traces = []
        for event_index, local_joins in enumerate(source["event_joins"]):
            start = source["event_offsets"][event_index]
            stop = source["event_offsets"][event_index + 1]
            traces.append(render_event(wildcard[start:stop], list(local_joins)))
        register_rows.append({
            "relaxed_pair_id": f"G488-RP{len(register_rows) + 1:02d}",
            "relaxed_condition": "REGISTER_ONLY",
            "source_record_id": source["record_id"],
            "target_record_id": target["record_id"],
            "source_physical_page": source["physical_page"],
            "target_physical_page": target["physical_page"],
            "source_register": source["register"],
            "target_register": target["register"],
            "active_model_sequence": source["active_model_sequence"],
            "fluent_frame_class": source["fluent_frame_class"],
            "event_boundary_shape": source["event_boundary_shape"],
            "wildcard_component_frame": " || ".join(traces),
            "changed_flat_component_ordinal": index + 1,
            "component_a": component_a,
            "component_b": component_b,
            "source_surface_sequence": source["surface_sequence"],
            "target_surface_sequence": target["surface_sequence"],
            "source_component_trace_de": source["normalized_component_trace_de"],
            "target_component_trace_de": target["normalized_component_trace_de"],
            "source_fluent_reading_de": source["fluent_reading_de"],
            "target_fluent_reading_de": target["fluent_reading_de"],
            "component_a_cue_visible": "YES" if cue_visible(component_a, str(source["fluent_reading_de"])) else "NO",
            "component_b_cue_visible": "YES" if cue_visible(component_b, str(target["fluent_reading_de"])) else "NO",
            "same_active_model": "YES",
            "same_readable_frame_class": "YES",
            "same_event_boundary_shape": "YES",
            "single_functional_component_delta": "YES",
            "only_register_relaxed": "YES",
        })

    strict_record_pairs = {
        frozenset((row["source_record_id"], row["target_record_id"])): row
        for row in strict_pairs
        if {row["component_a"], row["component_b"]} & ENDPOINTS
    }
    enriched_events: list[dict[str, object]] = []
    for source in source_events:
        row: dict[str, object] = dict(source)
        row["tokens"] = tuple(tokens(source))
        row["joins"] = tuple(joins(source))
        enriched_events.append(row)

    event_rows: list[dict[str, object]] = []
    for left, right in itertools.combinations(enriched_events, 2):
        fixed = ("register", "active_model", "semantic_separators")
        if any(left[field] != right[field] for field in fixed):
            continue
        if len(left["tokens"]) != len(right["tokens"]):
            continue
        differences = [index for index, pair in enumerate(zip(left["tokens"], right["tokens"])) if pair[0] != pair[1]]
        if len(differences) != 1:
            continue
        index = differences[0]
        if str(left["tokens"][index]).startswith("{") or str(right["tokens"][index]).startswith("{"):
            continue
        if not ({str(left["tokens"][index]), str(right["tokens"][index])} & ENDPOINTS):
            continue
        source, target, component_a, component_b = ordered_pair(left, right, index, "tokens")
        wildcard = list(source["tokens"])
        wildcard[index] = "*"
        strict = strict_record_pairs.get(frozenset((str(source["record_id"]), str(target["record_id"]))))
        event_rows.append({
            "event_pair_id": f"G488-EP{len(event_rows) + 1:02d}",
            "projection_class": "GDT486_STRICT_PAIR_SHADOW" if strict else "NEW_EVENT_CONTEXT_PROJECTION",
            "source_event_id": source["backprojection_id"],
            "target_event_id": target["backprojection_id"],
            "source_record_id": source["record_id"],
            "target_record_id": target["record_id"],
            "same_record": "YES" if source["record_id"] == target["record_id"] else "NO",
            "source_physical_page": source["physical_page"],
            "target_physical_page": target["physical_page"],
            "same_page": "YES" if source["physical_page"] == target["physical_page"] else "NO",
            "register": source["register"],
            "active_model": source["active_model"],
            "semantic_separators": source["semantic_separators"],
            "wildcard_event_frame": render_event(wildcard, list(source["joins"])),
            "changed_component_ordinal": index + 1,
            "component_a": component_a,
            "component_b": component_b,
            "source_surface": source["surface"],
            "target_surface": target["surface"],
            "source_working_recipe": source["working_recipe"],
            "target_working_recipe": target["working_recipe"],
            "source_semantic_tokens": source["semantic_tokens"],
            "target_semantic_tokens": target["semantic_tokens"],
            "source_event_reading_de": source["current_event_reading_de"],
            "target_event_reading_de": target["current_event_reading_de"],
            "component_a_cue_visible": "YES" if cue_visible(component_a, str(source["current_event_reading_de"])) else "NO",
            "component_b_cue_visible": "YES" if cue_visible(component_b, str(target["current_event_reading_de"])) else "NO",
            "gdt486_pair_id": strict["pair_id"] if strict else "NONE",
            "single_functional_component_delta": "YES",
            "record_context_only_relaxed": "YES" if not strict else "NO",
        })
    new_event_rows = [dict(row, new_projection_id=f"G488-NP{number:02d}") for number, row in enumerate((row for row in event_rows if row["projection_class"] == "NEW_EVENT_CONTEXT_PROJECTION"), 1)]

    t_frames = {row["frozen_frame"]: row for row in action_frames if row["contrast_pair"] == "T~R"}
    einstellen_events = [row for row in source_events if "EINSTELLEN" in tokens(row)]
    carrier_rows: list[dict[str, object]] = []
    for number, event in enumerate(einstellen_events, 1):
        recipe_parts = event["working_recipe"].split("+")
        action_context = "+".join("@ACTION" if part == "T" else part for part in recipe_parts)
        external = t_frames.get(action_context)
        strict_incidence = [row for row in strict_pairs if event["record_id"] in {row["source_record_id"], row["target_record_id"]} and "EINSTELLEN" in {row["component_a"], row["component_b"]}]
        carrier_rows.append({
            "carrier_id": f"G488-TC{number:02d}",
            "event_id": event["backprojection_id"],
            "record_id": event["record_id"],
            "physical_page": event["physical_page"],
            "register": event["register"],
            "surface": event["surface"],
            "working_recipe": event["working_recipe"],
            "semantic_tokens": event["semantic_tokens"],
            "action_context_frame": action_context,
            "current_event_reading_de": event["current_event_reading_de"],
            "einstellen_cue_visible": "YES" if cue_visible("EINSTELLEN", event["current_event_reading_de"]) else "NO",
            "strict_gdt486_contrast_role": strict_incidence[0]["pair_id"] if strict_incidence else "NONE",
            "exact_gdt428_tr_frame": external["frozen_frame"] if external else "NONE",
            "gdt428_t_event_count": external["left_event_count"] if external else 0,
            "gdt428_r_event_count": external["right_event_count"] if external else 0,
            "independent_local_carrier": "YES",
        })

    halten_events = [row for row in source_events if "HALTEN" in tokens(row)]
    endpoint_counts = {
        endpoint: {
            "strict": sum(endpoint in {row["component_a"], row["component_b"]} for row in strict_pairs),
            "register": sum(endpoint in {str(row["component_a"]), str(row["component_b"])} for row in register_rows),
            "event_total": sum(endpoint in {str(row["component_a"]), str(row["component_b"])} for row in event_rows),
            "event_new": sum(endpoint in {str(row["component_a"]), str(row["component_b"])} for row in new_event_rows),
        }
        for endpoint in sorted(ENDPOINTS)
    }
    capacity_rows = []
    for number, endpoint in enumerate(sorted(ENDPOINTS), 1):
        local = einstellen_events if endpoint == "EINSTELLEN" else halten_events
        counts = endpoint_counts[endpoint]
        capacity_rows.append({
            "capacity_id": f"G488-C{number:02d}",
            "endpoint": endpoint,
            "local_event_count": len(local),
            "local_record_count": len({row["record_id"] for row in local}),
            "local_page_count": len({row["physical_page"] for row in local}),
            "local_pages": "|".join(sorted({row["physical_page"] for row in local})),
            "local_register_count": len({row["register"] for row in local}),
            "local_registers": "|".join(sorted({row["register"] for row in local})),
            "strict_gdt486_pair_count": counts["strict"],
            "register_only_new_pair_count": counts["register"],
            "event_projection_pair_count": counts["event_total"],
            "event_projection_new_pair_count": counts["event_new"],
            "one_relaxation_new_pair_count": counts["register"] + counts["event_new"],
            "capacity_decision": "NEW_CYCLE_CAPACITY" if endpoint == "HALTEN" else "NO_SECOND_LOCAL_CONTRAST_CAPACITY",
        })

    register_edge = next(row for row in register_rows if {row["component_a"], row["component_b"]} == {"BAHN", "HALTEN"})
    bridge_edge = next(row for row in local_edges if {row["component_a"], row["component_b"]} == {"BAHN", "ZIELORT"})
    strict_halten_rule = next(row for row in strict_rules if {row["component_a"], row["component_b"]} == {"HALTEN", "ZIELORT"})
    cycle_rows = [{
        "cycle_id": "G488-HC01",
        "endpoint": "HALTEN",
        "singleton_rule_id": strict_halten_rule["rule_id"],
        "cycle_path_de": "HALTEN —G488 REGISTER_ONLY→ BAHN —G486 RECURRENT→ ZIELORT —G486 SINGLETON→ HALTEN",
        "alternate_path_excluding_singleton": "HALTEN → BAHN → ZIELORT",
        "alternate_path_edge_count": 2,
        "new_edge_id": register_edge["relaxed_pair_id"],
        "new_edge_record_pair": f"{register_edge['source_record_id']}~{register_edge['target_record_id']}",
        "new_edge_relaxed_condition": "REGISTER_ONLY",
        "recurrent_bridge_rule_id": bridge_edge["source_rule_id"],
        "recurrent_bridge_edge": "BAHN~ZIELORT",
        "recurrent_bridge_pair_count": bridge_edge["pair_count"],
        "alternate_path_complete": "YES",
        "dictionary_remap_required": "NO",
    }]

    new_halten_neighbours = sorted({str(row[field]) for row in [*register_rows, *new_event_rows] for field in ("component_a", "component_b") if str(row[field]) != "HALTEN" and "HALTEN" in {str(row["component_a"]), str(row["component_b"])} })
    closure_rows = [
        {
            "endpoint_id": "G488-S01",
            "endpoint": "EINSTELLEN",
            "portable_root": "T",
            "local_event_count": len(einstellen_events),
            "strict_singleton_rule_id": "G486-CR17",
            "strict_contrast_partner": "HIER",
            "new_register_only_pair_count": 0,
            "new_event_projection_pair_count": 0,
            "new_contrast_neighbours": "NONE",
            "exact_external_anchor": "GDT428 T~R ×11",
            "exact_external_carrier_frame_match_count": sum(row["exact_gdt428_tr_frame"] != "NONE" for row in carrier_rows),
            "closure_status": "CAPACITY_LIMITED_ENDPOINT_RETAINED",
            "full_cycle_closed": "NO",
            "meaning_change": "NO",
        },
        {
            "endpoint_id": "G488-S02",
            "endpoint": "HALTEN",
            "portable_root": "SH",
            "local_event_count": len(halten_events),
            "strict_singleton_rule_id": strict_halten_rule["rule_id"],
            "strict_contrast_partner": "ZIELORT",
            "new_register_only_pair_count": endpoint_counts["HALTEN"]["register"],
            "new_event_projection_pair_count": endpoint_counts["HALTEN"]["event_new"],
            "new_contrast_neighbours": "|".join(new_halten_neighbours),
            "exact_external_anchor": "GDT428 SH~CHD ×14",
            "exact_external_carrier_frame_match_count": 0,
            "closure_status": "FULL_ALTERNATE_CYCLE_CLOSED",
            "full_cycle_closed": "YES",
            "meaning_change": "NO",
        },
    ]

    if len(register_rows) != 1 or len(event_rows) != 5 or len(new_event_rows) != 3 or len(carrier_rows) != 2:
        raise RuntimeError("Unexpected endpoint relaxation counts")
    write_tsv(REGISTER_ONLY, register_rows)
    write_tsv(EVENT_PAIRS, event_rows)
    write_tsv(NEW_EVENT_PAIRS, new_event_rows)
    write_tsv(EINSTELLEN_CARRIERS, carrier_rows)
    write_tsv(CLOSURE_STATUS, closure_rows)
    write_tsv(CAPACITY, capacity_rows)
    write_tsv(HALTEN_CYCLE, cycle_rows)

    result = {
        "status": STATUS,
        "record_count": len(source_records),
        "event_count": len(source_events),
        "endpoint_count": 2,
        "einstellen_local_event_count": len(einstellen_events),
        "halten_local_event_count": len(halten_events),
        "register_only_endpoint_pair_count": len(register_rows),
        "endpoint_event_pair_count": len(event_rows),
        "new_event_projection_pair_count": len(new_event_rows),
        "strict_event_shadow_pair_count": sum(row["projection_class"] == "GDT486_STRICT_PAIR_SHADOW" for row in event_rows),
        "halten_new_contrast_neighbour_count": len(new_halten_neighbours),
        "halten_new_contrast_neighbours": new_halten_neighbours,
        "halten_full_cycle_count": 1,
        "einstellen_full_cycle_count": 0,
        "closed_endpoint_count": 1,
        "capacity_limited_endpoint_count": 1,
        "einstellen_exact_gdt428_carrier_frame_match_count": sum(row["exact_gdt428_tr_frame"] != "NONE" for row in carrier_rows),
        "all_pair_meaning_cues_visible": all(row["component_a_cue_visible"] == "YES" and row["component_b_cue_visible"] == "YES" for row in [*register_rows, *event_rows]),
        "meaning_change_count": 0,
        "active_model_change_count": 0,
        "record_boundary_change_count": 0,
        "surface_change_count": 0,
        "recipe_change_count": 0,
        "page_change_count": 0,
        "claim_ceiling": "One-condition relaxation and local capacity result over fixed GDT485/GDT486/GDT487/GDT428 working meanings; no new meaning, invented wording, model, boundary, surface, recipe, event, or page.",
    }
    READABLE.write_text(build_readable(register_rows, event_rows, new_event_rows, carrier_rows, closure_rows, cycle_rows, result), encoding="utf-8")
    RESULT.write_text(json.dumps(result, indent=2, ensure_ascii=False, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
