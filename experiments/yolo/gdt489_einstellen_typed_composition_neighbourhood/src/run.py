#!/usr/bin/env python3
"""Build a typed composition neighbourhood around EINSTELLEN/T."""

from __future__ import annotations

import csv
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
BASE = ROOT / "experiments/yolo/gdt489_einstellen_typed_composition_neighbourhood"
OUT = BASE / "artifacts"
G428 = ROOT / "experiments/yolo/gdt428_within_class_action_semantic_contrasts/artifacts"
G485 = ROOT / "experiments/yolo/gdt485_fluent_reversible_microrecord_edition/artifacts"
G486 = ROOT / "experiments/yolo/gdt486_fluent_frame_component_contrast_deck/artifacts"
G487 = ROOT / "experiments/yolo/gdt487_model_conditioned_realization_lexicon/artifacts"
G488 = ROOT / "experiments/yolo/gdt488_action_endpoint_single_relaxation_closure/artifacts"
ACTION_FRAMES_IN = G428 / "gdt428_104_direct_substitution_frames.tsv"
EVENTS_IN = G485 / "gdt485_183_literal_backprojection_events.tsv"
CONTRAST_RULES_IN = G486 / "gdt486_29_model_conditioned_contrast_rules.tsv"
LOCAL_EDGES_IN = G487 / "gdt487_13_local_recurrent_edges.tsv"
EINSTELLEN_CARRIERS_IN = G488 / "gdt488_2_einstellen_local_carriers.tsv"
FRAME_ATLAS = OUT / "gdt489_11_tr_composition_frames.tsv"
CONTEXT_WITNESSES = OUT / "gdt489_168_local_context_witnesses.tsv"
LOCAL_CONTACTS = OUT / "gdt489_3_local_einstellen_frame_contacts.tsv"
TYPED_EDGES = OUT / "gdt489_2_typed_einstellen_edges.tsv"
TYPED_CYCLE = OUT / "gdt489_1_typed_einstellen_cycle.tsv"
PAGE_SUPPORT = OUT / "gdt489_6_page_context_support.tsv"
READABLE = OUT / "GDT489_EINSTELLEN_TYPED_COMPOSITION_NEIGHBOURHOOD.md"
RESULT = OUT / "gdt489_result.json"
STATUS = "EINSTELLEN_HAS_TWO_TYPED_COMPOSITION_EDGES__ALL_SIXTEEN_SINGLETONS_CONNECTED"
MEANINGS = {
    "AIIN": "WERT",
    "AIN": "ANTEIL",
    "AL": "ZIELORT",
    "Y": "POSTEN",
    "CH": "NEHMEN",
    "E": "GRAD I",
    "CHD": "BEARBEITEN",
    "OL": "FORTSETZEN",
    "OR": "EINHEIT",
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


def match_positions(parts: list[str], pattern: list[str]) -> list[int]:
    if not pattern or len(pattern) > len(parts):
        return []
    return [index for index in range(len(parts) - len(pattern) + 1) if parts[index:index + len(pattern)] == pattern]


def render_meanings(parts: list[str]) -> str:
    return " · ".join(MEANINGS.get(part, part) for part in parts) if parts else "NONE"


def build_readable(
    frames: list[dict[str, object]],
    contacts: list[dict[str, object]],
    edges: list[dict[str, object]],
    cycles: list[dict[str, object]],
    pages: list[dict[str, object]],
    result: dict[str, object],
) -> str:
    lines = [
        "# GDT489 — EINSTELLEN im typisierten Kompositionsnetz",
        "",
        "GDT489 nimmt die elf exakten GDT428-T/R-Austauschrahmen und fragt zweierlei getrennt: Ist ihr unveränderter Nachbarkontext in den 183 lokalen Events vorhanden? Und berührt ein lokales T-Event tatsächlich den vollständigen T-Teilrahmen? Nur der zweite Befund erzeugt eine Kompositionskante.",
        "",
        f"- T/R-Rahmen: **{result['tr_frame_count']}** mit **{result['external_t_event_count']} T-** und **{result['external_r_event_count']} R-Ereignissen**.",
        f"- Nichtleere Nachbarkontexte: **{result['nonempty_context_frame_count']}**; lokal vorhanden: **{result['locally_supported_context_frame_count']}**.",
        f"- Lokale Kontextzeugen: **{result['local_context_witness_count']}** Rahmen×Event-Zeugen / **{result['local_context_positional_occurrence_count']}** Positionen in **{result['local_context_unique_event_count']}** Events.",
        f"- Nichttriviale lokale T-Rahmenkontakte: **{result['local_t_nonempty_frame_contact_count']}** in zwei Events; daraus **{result['typed_composition_edge_count']}** typisierte Nachbarkanten.",
        "",
        "## Elf T/R-Kompositionsrahmen",
        "",
        "| Rahmen | Nachbarkontext | GDT428 T/R | lokale Kontextzeugen | lokale T-Kontakte | Einordnung |",
        "|---|---|---:|---:|---:|---|",
    ]
    for row in frames:
        lines.append(f"| `{row['frozen_frame']}` | `{row['context_meaning_de']}` | {row['external_t_event_count']}/{row['external_r_event_count']} | {row['local_context_witness_count']} | {row['local_t_nonempty_contact_count']} | `{row['local_support_class']}` |")
    lines.extend([
        "",
        "Neun der zehn nichtleeren Kontexte sind lokal vorhanden. Nur `CHD+Y = BEARBEITEN · POSTEN` fehlt als zusammenhängender Kontext in diesen 183 Events. Ein vorhandener Kontext allein setzt T noch nicht hinein; deshalb werden die sieben bloßen Kontextkontakte nicht zu EINSTELLEN-Kanten hochgestuft.",
        "",
        "## Drei wirkliche lokale T-Rahmenkontakte",
        "",
        "| Event | lokales Rezept | GDT428-Rahmen | Lage | Lesung |",
        "|---|---|---|---|---|",
    ])
    for row in contacts:
        lines.append(f"| `{row['event_id']}` | `{row['working_recipe']}` | `{row['frozen_frame']}` | `{row['contact_class']}` | {row['current_event_reading_de']} |")
    lines.extend([
        "",
        "`G485-E118 CH+T` trifft `CH+@ACTION` als ganzen Event. `G485-E133 CH+T+Y` trägt denselben Rahmen als Präfix und zusätzlich `@ACTION+Y` als Suffix. Damit erscheint EINSTELLEN lokal nicht als freies Einzelwort, sondern mit einem linken Handlungsnachbarn und einem rechten Argumentnachbarn.",
        "",
        "## Zwei typisierte Kompositionskanten",
        "",
        "| Kante | Richtung | lokale Kontakte | GDT428-Rahmen | Rolle |",
        "|---|---|---:|---|---|",
    ])
    for row in edges:
        lines.append(f"| `EINSTELLEN — {row['neighbour_meaning']}` | {row['neighbour_direction']} | {row['local_contact_count']} | `{row['source_frame']}` | `{row['edge_type']}` |")
    lines.extend([
        "",
        "In Werkstattdeutsch ist die beobachtete Form konkret: links „nimm … und stelle … ein“, rechts „… sowie den Posten … stelle beide ein“. Das sind die zwei vorhandenen Lesungen, keine analog ergänzten Sätze.",
        "",
        "## Der letzte Singleton ist typisiert verbunden",
        "",
    ])
    for row in cycles:
        lines.extend([
            f"`{row['cycle_path_de']}`",
            "",
            "Der Weg ist vollständig, aber absichtlich gemischt: Die erste Kante ist Komposition, die zweite eine zweimal wiederkehrende Ersatzkante. Deshalb bleibt `EINSTELLEN ↔ HIER` **kein reiner Ersatzzyklus**. Für die Arbeitslesung ist EINSTELLEN nun dennoch direkt an das alte lokale Netz angebunden, ohne einen Ersatzpartner zu erfinden.",
            "",
        ])
    lines.extend([
        "## Seitenkapazität",
        "",
        "| Seite | Kontextzeugen | Positionen | verschiedene Events | T-Kontakte |",
        "|---|---:|---:|---:|---:|",
    ])
    for row in pages:
        lines.append(f"| {row['physical_page']} | {row['context_witness_count']} | {row['context_positional_occurrence_count']} | {row['context_unique_event_count']} | {row['local_t_contact_count']} |")
    lines.extend([
        "",
        "## Nächster Schritt",
        "",
        "Die beiden echten T-Kompositionskanten können nun in ein kleines vorhersagendes Satzmuster überführt werden: bekannte T-Rahmen mit WERT, ANTEIL, ZIELORT, FORTSETZEN oder POSTEN erhalten nur dann eine konkrete Formulierung, wenn die entsprechende GDT428-T-Seite selbst einen lesbaren Träger liefert. Der fehlende Kontext `CHD+Y` bleibt offen; aus bloßer Nachbarschaft wird kein Satz erfunden.",
        "",
    ])
    return "\n".join(lines)


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    action_frames = read_tsv(ACTION_FRAMES_IN)
    events = read_tsv(EVENTS_IN)
    contrast_rules = read_tsv(CONTRAST_RULES_IN)
    local_edges = read_tsv(LOCAL_EDGES_IN)
    carriers = read_tsv(EINSTELLEN_CARRIERS_IN)
    if (len(action_frames), len(events), len(contrast_rules), len(local_edges), len(carriers)) != (104, 183, 29, 13, 2):
        raise RuntimeError("Input count drift")
    tr_frames = [row for row in action_frames if row["contrast_pair"] == "T~R"]
    if len(tr_frames) != 11:
        raise RuntimeError("Expected eleven T/R frames")

    event_parts = {row["backprojection_id"]: row["working_recipe"].split("+") for row in events}
    context_rows: list[dict[str, object]] = []
    contact_rows: list[dict[str, object]] = []
    frame_rows: list[dict[str, object]] = []
    for frame_number, source in enumerate(tr_frames, 1):
        frame_id = f"G489-F{frame_number:02d}"
        parts = source["frozen_frame"].split("+")
        context = [part for part in parts if part != "@ACTION"]
        t_pattern = ["T" if part == "@ACTION" else part for part in parts]
        r_pattern = ["R" if part == "@ACTION" else part for part in parts]
        local_context: list[dict[str, str]] = []
        context_positions = 0
        if context:
            for event in events:
                positions = match_positions(event_parts[event["backprojection_id"]], context)
                if not positions:
                    continue
                local_context.append(event)
                context_positions += len(positions)
                context_rows.append({
                    "context_witness_id": f"G489-CW{len(context_rows) + 1:03d}",
                    "frame_id": frame_id,
                    "frozen_frame": source["frozen_frame"],
                    "context_recipe": "+".join(context),
                    "context_meaning_de": render_meanings(context),
                    "event_id": event["backprojection_id"],
                    "record_id": event["record_id"],
                    "physical_page": event["physical_page"],
                    "register": event["register"],
                    "active_model": event["active_model"],
                    "surface": event["surface"],
                    "working_recipe": event["working_recipe"],
                    "match_count": len(positions),
                    "match_start_ordinals": "|".join(str(position + 1) for position in positions),
                    "context_is_complete_event_recipe": "YES" if event_parts[event["backprojection_id"]] == context else "NO",
                    "current_event_reading_de": event["current_event_reading_de"],
                    "source_event_preserved": "YES",
                })
        local_t_events: list[dict[str, str]] = []
        local_r_events: list[dict[str, str]] = []
        if context:
            for event in events:
                parts_local = event_parts[event["backprojection_id"]]
                t_positions = match_positions(parts_local, t_pattern)
                r_positions = match_positions(parts_local, r_pattern)
                if t_positions:
                    local_t_events.append(event)
                    contact_rows.append({
                        "contact_id": f"G489-TC{len(contact_rows) + 1:02d}",
                        "frame_id": frame_id,
                        "frozen_frame": source["frozen_frame"],
                        "instantiated_t_frame": "+".join(t_pattern),
                        "context_meaning_de": render_meanings(context),
                        "event_id": event["backprojection_id"],
                        "record_id": event["record_id"],
                        "physical_page": event["physical_page"],
                        "register": event["register"],
                        "surface": event["surface"],
                        "working_recipe": event["working_recipe"],
                        "match_count": len(t_positions),
                        "match_start_ordinals": "|".join(str(position + 1) for position in t_positions),
                        "contact_class": "EXACT_WHOLE_EVENT" if parts_local == t_pattern else "CONTIGUOUS_PARTIAL_FRAME",
                        "current_event_reading_de": event["current_event_reading_de"],
                        "einstellen_cue_visible": "YES" if re.search(r"stell", event["current_event_reading_de"], flags=re.IGNORECASE) else "NO",
                        "external_t_event_count": source["left_event_count"],
                        "external_r_event_count": source["right_event_count"],
                        "edge_type": "COMPOSITION_CONTACT_NOT_REPLACEMENT",
                    })
                if r_positions:
                    local_r_events.append(event)
        if not context:
            support_class = "EMPTY_CONTEXT_ACTION_BASELINE"
        elif local_t_events:
            support_class = "LOCAL_CONTEXT_AND_T_CONTACT"
        elif local_context:
            support_class = "LOCAL_CONTEXT_ONLY"
        else:
            support_class = "ABSENT_LOCAL_CONTEXT"
        frame_rows.append({
            "frame_id": frame_id,
            "frozen_frame": source["frozen_frame"],
            "action_position_ordinal": parts.index("@ACTION") + 1,
            "instantiated_t_frame": "+".join(t_pattern),
            "instantiated_r_frame": "+".join(r_pattern),
            "context_recipe": "+".join(context) if context else "NONE",
            "context_meaning_de": render_meanings(context),
            "context_component_count": len(context),
            "external_t_event_count": source["left_event_count"],
            "external_t_pages": source["left_pages"],
            "external_t_registers": source["left_registers"],
            "external_r_event_count": source["right_event_count"],
            "external_r_pages": source["right_pages"],
            "external_r_registers": source["right_registers"],
            "local_context_witness_count": len(local_context),
            "local_context_positional_occurrence_count": context_positions,
            "local_context_page_count": len({event["physical_page"] for event in local_context}),
            "local_context_pages": "|".join(sorted({event["physical_page"] for event in local_context})) or "NONE",
            "local_context_register_count": len({event["register"] for event in local_context}),
            "local_context_registers": "|".join(sorted({event["register"] for event in local_context})) or "NONE",
            "local_t_nonempty_contact_count": len(local_t_events),
            "local_t_contact_events": "|".join(event["backprojection_id"] for event in local_t_events) or "NONE",
            "local_r_nonempty_contact_count": len(local_r_events),
            "local_r_contact_events": "|".join(event["backprojection_id"] for event in local_r_events) or "NONE",
            "local_support_class": support_class,
            "replacement_edge_created": "NO",
        })

    contact_by_frame: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in contact_rows:
        contact_by_frame[str(row["frozen_frame"])].append(row)
    edge_specs = [
        ("G489-E01", "CH+@ACTION", "CH", "NEHMEN", "BEFORE_EINSTELLEN"),
        ("G489-E02", "@ACTION+Y", "Y", "POSTEN", "AFTER_EINSTELLEN"),
    ]
    edge_rows: list[dict[str, object]] = []
    for edge_id, frame_name, neighbour_root, neighbour_meaning, direction in edge_specs:
        source_frame = next(row for row in frame_rows if row["frozen_frame"] == frame_name)
        local_contacts = contact_by_frame[frame_name]
        edge_rows.append({
            "edge_id": edge_id,
            "source_frame_id": source_frame["frame_id"],
            "source_frame": frame_name,
            "endpoint_root": "T",
            "endpoint_meaning": "EINSTELLEN",
            "neighbour_root": neighbour_root,
            "neighbour_meaning": neighbour_meaning,
            "neighbour_direction": direction,
            "local_contact_count": len(local_contacts),
            "local_contact_ids": "|".join(str(row["contact_id"]) for row in local_contacts),
            "local_event_count": len({str(row["event_id"]) for row in local_contacts}),
            "local_events": "|".join(sorted({str(row["event_id"]) for row in local_contacts})),
            "local_page_count": len({str(row["physical_page"]) for row in local_contacts}),
            "local_pages": "|".join(sorted({str(row["physical_page"]) for row in local_contacts})),
            "local_register_count": len({str(row["register"]) for row in local_contacts}),
            "local_registers": "|".join(sorted({str(row["register"]) for row in local_contacts})),
            "external_t_event_count": source_frame["external_t_event_count"],
            "external_r_event_count": source_frame["external_r_event_count"],
            "observed_readings_de": " || ".join(str(row["current_event_reading_de"]) for row in local_contacts),
            "edge_type": "LOCAL_COMPOSITION_PLUS_EXTERNAL_T_R_SUBSTITUTION_FRAME",
            "replacement_edge": "NO",
            "meaning_change": "NO",
        })

    singleton = next(row for row in contrast_rules if row["rule_id"] == "G486-CR17")
    bridge = next(row for row in local_edges if {row["component_a"], row["component_b"]} == {"HIER", "POSTEN"})
    posten_edge = next(row for row in edge_rows if row["neighbour_meaning"] == "POSTEN")
    cycle_rows = [{
        "cycle_id": "G489-CY01",
        "singleton_rule_id": singleton["rule_id"],
        "singleton_edge": "EINSTELLEN~HIER",
        "cycle_path_de": "EINSTELLEN —KOMPOSITION→ POSTEN —G486 WIEDERKEHRENDER ERSATZ→ HIER —G486 SINGLETON-ERSATZ→ EINSTELLEN",
        "alternate_path_excluding_singleton": "EINSTELLEN → POSTEN → HIER",
        "alternate_path_edge_count": 2,
        "composition_edge_id": posten_edge["edge_id"],
        "composition_source_frame": posten_edge["source_frame"],
        "composition_local_events": posten_edge["local_events"],
        "replacement_bridge_rule_id": bridge["source_rule_id"],
        "replacement_bridge_edge": "POSTEN~HIER",
        "replacement_bridge_pair_count": bridge["pair_count"],
        "edge_type_sequence": "COMPOSITION|RECURRENT_REPLACEMENT",
        "typed_alternate_path_complete": "YES",
        "pure_replacement_cycle": "NO",
        "replacement_endpoint_status": "CAPACITY_LIMITED_RETAINED",
        "dictionary_remap_required": "NO",
    }]

    page_rows: list[dict[str, object]] = []
    contacts_by_page = defaultdict(list)
    contexts_by_page = defaultdict(list)
    for row in contact_rows:
        contacts_by_page[str(row["physical_page"])].append(row)
    for row in context_rows:
        contexts_by_page[str(row["physical_page"])].append(row)
    for page in dict.fromkeys(event["physical_page"] for event in events):
        page_events = [event for event in events if event["physical_page"] == page]
        local_contexts = contexts_by_page[page]
        local_contacts = contacts_by_page[page]
        page_rows.append({
            "physical_page": page,
            "register": page_events[0]["register"],
            "event_count": len(page_events),
            "context_witness_count": len(local_contexts),
            "context_positional_occurrence_count": sum(int(row["match_count"]) for row in local_contexts),
            "context_unique_event_count": len({str(row["event_id"]) for row in local_contexts}),
            "context_frame_count": len({str(row["frame_id"]) for row in local_contexts}),
            "context_frames": "|".join(sorted({str(row["frozen_frame"]) for row in local_contexts})) or "NONE",
            "local_t_contact_count": len(local_contacts),
            "local_t_contact_event_count": len({str(row["event_id"]) for row in local_contacts}),
            "local_t_contact_frames": "|".join(sorted({str(row["frozen_frame"]) for row in local_contacts})) or "NONE",
            "has_context_support": "YES" if local_contexts else "NO",
        })

    if len(frame_rows) != 11 or len(context_rows) != 168 or len(contact_rows) != 3 or len(edge_rows) != 2 or len(cycle_rows) != 1 or len(page_rows) != 6:
        raise RuntimeError("Unexpected composition-neighbourhood counts")
    write_tsv(FRAME_ATLAS, frame_rows)
    write_tsv(CONTEXT_WITNESSES, context_rows)
    write_tsv(LOCAL_CONTACTS, contact_rows)
    write_tsv(TYPED_EDGES, edge_rows)
    write_tsv(TYPED_CYCLE, cycle_rows)
    write_tsv(PAGE_SUPPORT, page_rows)

    result = {
        "status": STATUS,
        "tr_frame_count": len(frame_rows),
        "external_t_event_count": sum(int(row["external_t_event_count"]) for row in frame_rows),
        "external_r_event_count": sum(int(row["external_r_event_count"]) for row in frame_rows),
        "nonempty_context_frame_count": sum(row["context_recipe"] != "NONE" for row in frame_rows),
        "locally_supported_context_frame_count": sum(int(row["local_context_witness_count"]) > 0 for row in frame_rows if row["context_recipe"] != "NONE"),
        "absent_local_context_frame_count": sum(row["local_support_class"] == "ABSENT_LOCAL_CONTEXT" for row in frame_rows),
        "absent_local_context_frames": [row["frozen_frame"] for row in frame_rows if row["local_support_class"] == "ABSENT_LOCAL_CONTEXT"],
        "local_context_witness_count": len(context_rows),
        "local_context_positional_occurrence_count": sum(int(row["match_count"]) for row in context_rows),
        "local_context_unique_event_count": len({str(row["event_id"]) for row in context_rows}),
        "context_support_page_count": sum(row["has_context_support"] == "YES" for row in page_rows),
        "local_einstellen_event_count": len({carrier["event_id"] for carrier in carriers}),
        "local_t_nonempty_frame_contact_count": len(contact_rows),
        "local_t_contact_frame_count": len({str(row["frozen_frame"]) for row in contact_rows}),
        "local_t_contact_event_count": len({str(row["event_id"]) for row in contact_rows}),
        "typed_composition_edge_count": len(edge_rows),
        "typed_composition_neighbours": [row["neighbour_meaning"] for row in edge_rows],
        "typed_alternate_cycle_count": len(cycle_rows),
        "pure_replacement_cycle_added_count": 0,
        "singleton_rule_connected_count_after_gdt489": 16,
        "meaning_change_count": 0,
        "active_model_change_count": 0,
        "record_boundary_change_count": 0,
        "surface_change_count": 0,
        "recipe_change_count": 0,
        "page_change_count": 0,
        "claim_ceiling": "Typed composition-neighbourhood connection over fixed GDT428/GDT485/GDT486/GDT487/GDT488 working meanings; composition and replacement edges remain distinct, with no new meaning, wording, model, boundary, surface, recipe, event, or page.",
    }
    READABLE.write_text(build_readable(frame_rows, contact_rows, edge_rows, cycle_rows, page_rows, result), encoding="utf-8")
    RESULT.write_text(json.dumps(result, indent=2, ensure_ascii=False, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
