#!/usr/bin/env python3
"""Build GDT588 selection mobility, future intake, and count-safe reader."""

from __future__ import annotations

import json
from collections import Counter, defaultdict
from typing import Any

from transfer_lib import (
    G583_RULES,
    INPUTS,
    MULTIPLICITY_REPAIRS,
    OUTPUTS,
    PACKET_CARD_DESCRIPTIONS,
    PORTABLE_CORE,
    REGISTER_FALLBACK_FORMS,
    ROOT_ORDER,
    STATUS,
    TIER_CELL,
    TIER_EXACT,
    TIER_PRIVATE,
    TIER_REGISTER,
    cell_key,
    classify,
    count_trace_de,
    exact_key,
    lemma_trace,
    mobility_maps,
    other_pages,
    pipe,
    read_tsv,
    register_root_key,
    root_lemma_key,
    root_multiset,
    sha256,
    write_tsv,
)


REGISTER_ORDER = tuple(G583_RULES.REGISTER_ORDER)
TIER_SHORT = {
    TIER_EXACT: "E",
    TIER_CELL: "C",
    TIER_REGISTER: "R",
    TIER_PRIVATE: "P",
}


def requirement(rule: Any) -> str:
    fields: list[str] = []
    for name in (
        "source_ids", "physical_pages_not", "direct_any", "direct_none", "host_any",
        "host_none", "previous_actions", "next_actions",
    ):
        values = getattr(rule, name)
        if values:
            fields.append(f"{name}={','.join(values)}")
    if rule.host_any_groups:
        groups = ["/".join(group) for group in rule.host_any_groups]
        fields.append(f"host_any_groups={'+'.join(groups)}")
    return ";".join(fields) if fields else "REGISTER_AND_ACTION_ROOT_ONLY"


def foreign_example(
    assignments: list[dict[str, str]], row: dict[str, str], tier: str
) -> str:
    page = row["physical_page"]
    if tier == TIER_EXACT:
        candidates = [x for x in assignments if exact_key(x) == exact_key(row) and x["physical_page"] != page]
    elif tier == TIER_CELL:
        candidates = [x for x in assignments if cell_key(x) == cell_key(row) and x["physical_page"] != page]
    elif tier == TIER_REGISTER:
        candidates = [x for x in assignments if register_root_key(x) == register_root_key(row) and x["physical_page"] != page]
    else:
        candidates = [x for x in assignments if root_lemma_key(x) == root_lemma_key(row) and x["physical_page"] != page]
    return candidates[0]["carrier_slot_id"] if candidates else "NONE"


def build_book(statements: list[dict[str, Any]], local: list[dict[str, Any]]) -> str:
    page_order: list[str] = []
    for row in [*statements, *local]:
        page = str(row["physical_page"])
        if page not in page_order:
            page_order.append(page)
    by_statement: dict[str, list[dict[str, Any]]] = defaultdict(list)
    by_local: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in statements:
        by_statement[str(row["physical_page"])].append(row)
    for row in local:
        by_local[str(row["physical_page"])].append(row)
    lines = [
        "# GDT588 — vollständiger mengenfester 30-Seiten-Arbeitsleser", "",
        "Explorative deutsche Leserschicht; kein rekonstruierter Klartext.",
        "Eckige Klammern mit ×2 zählen geschriebene Träger, nicht behauptete reale Objekte.",
    ]
    for page in page_order:
        lines.extend(["", f"## {page}", "", "### Laufende Aussagen", ""])
        if not by_statement[page]:
            lines.append("Keine laufende Aussage auf dieser Seite.")
        for row in by_statement[page]:
            lines.extend([
                f"#### {row['statement_id']} — {row['register']}", "",
                f"Surface: `{row['surface_sequence']}`", "",
                str(row["gdt588_primary_reader_de"]), "",
            ])
        lines.extend(["### Lokale Karten", ""])
        if not by_local[page]:
            lines.append("Keine lokale Karte auf dieser Seite.")
        for row in by_local[page]:
            lines.extend([
                f"#### {row['source_event_id']} — {row['locus']}", "",
                f"Surface: `{row['surface']}`", "",
                str(row["gdt588_primary_reader_de"]), "",
            ])
    return "\n".join(lines).rstrip() + "\n"


def build_deck(result: dict[str, Any], repairs: list[dict[str, Any]]) -> str:
    lines = [
        "# GDT588 — Übertragungsdeck der konkreten Trägerlesungen", "",
        "## Das kurze Ergebnis", "",
        "Von 1.243 konkreten GDT587-Trägerstellen besitzen 970 dieselbe strenge Auswahl auf einer anderen Seite.",
        "Weitere 146 behalten am selben Handlung×Root-Fach dasselbe Nomen; nur Packetform oder Begleitroots unterscheiden sich.",
        "Damit sind 1.116/1.243 konkrete Handlungsnomen bereits seitenübergreifend getragen.", "",
        "| Stufe | Stellen |", "|---|---:|",
        f"| exakte Auswahl auf anderer Seite | {result['tier_counts'][TIER_EXACT]} |",
        f"| gleiches Handlung×Root-Nomen | {result['tier_counts'][TIER_CELL]} |",
        f"| nur Register×Root anderswo | {result['tier_counts'][TIER_REGISTER]} |",
        f"| im Register seitenprivat | {result['tier_counts'][TIER_PRIVATE]} |", "",
        "Typen sind deutlich spröder: 103/268 strenge Auswahltypen, aber 970/1.243 konkrete Stellen wandern über Seiten.",
        "Bei strikter Trennung von laufendem Text und lokalen Karten lautet die Staffel 942/152/135/14.", "",
        "## Zukunftsbrücke", "",
        "Der ausführbare Weg nimmt nur einen bereits segmentierten vollständigen Host an. Von 38 Regelkarten sind 27 automatisch kontextuell, zwei an alte Quell-IDs gebunden und neun bewusste GDT584-Sonderlesungen.",
        "Die 220 deklarierbaren Auto-Regel×Register×Root-Fächer zerfallen in 111 beobachtete Fächer, 53 registerinvariante Fallbacks und 56 breite, aber nie leere Defaults.",
        "Körper bleibt hostabhängig: Relation, Form und Adresse können dieselbe SH+Y-Oberform von Körper auf Stationsansatz zurücksetzen.", "",
        "## Packet- und Mengenreparatur", "",
        "Die acht Spezialpacketregeln liegen an 74 Hosts. Derselbe Root-Multiset-Typ steht für 55 Hosts auf einer anderen Seite; 19 Formen bleiben lokal.",
        "Dreizehn flüssige GDT587-Sätze hatten wiederholte geschriebene Roots zusammengezogen. Die exakte Spur war vollständig; GDT588 macht die Wiederholung nun im Leser als ×2 hörbar.", "",
    ]
    for row in repairs:
        lines.append(
            f"- **{row['reader_unit_id']}**: {row['gdt587_reader_clause_de']} → {row['gdt588_count_safe_clause_de']}"
        )
    lines.extend([
        "", "## Grenze", "",
        "Keine neue Seite, Oberfläche, Segmentierung, Wurzel oder Namenslesung wurde hinzugefügt. Fremdseitenstütze ist praktische Provenienz, keine unabhängige Entzifferungsbestätigung.",
    ])
    return "\n".join(lines).rstrip() + "\n"


def main() -> int:
    source = {name: read_tsv(path) for name, path in INPUTS.items() if path.suffix == ".tsv"}
    assignments = source["assignments_587"]
    actions = source["actions_584"]
    old_hosts = source["hosts_587"]
    old_statements = source["statements_587"]
    old_local = source["local_cards_587"]
    maps = mobility_maps(assignments)
    layer_maps = mobility_maps(assignments, same_layer=True)

    action_count_583 = Counter(row["gdt583_rule_id"] for row in actions)
    action_count_584 = Counter(row["gdt584_rule_id"] for row in actions)
    carrier_count = Counter(row["gdt584_rule_id"] for row in assignments)
    carrier_hosts: dict[str, set[str]] = defaultdict(set)
    for row in assignments:
        carrier_hosts[row["gdt584_rule_id"]].add(row["primary_governor_key"])

    rule_gate: list[dict[str, Any]] = []
    known_g583_ids = {rule.rule_id for rule in G583_RULES.RULES}
    for rule in G583_RULES.RULES:
        gate = "SOURCE_ID_BOUND" if rule.source_ids else "AUTO_CONTEXT"
        rule_gate.append({
            "rule_gate_ordinal": len(rule_gate) + 1,
            "rule_id": rule.rule_id,
            "gate_class": gate,
            "parent_rule_id": rule.rule_id,
            "action_root": rule.root,
            "registers": "|".join(rule.registers),
            "priority": rule.priority,
            "selection_requirements": requirement(rule),
            "old_action_occurrence_count": action_count_583[rule.rule_id],
            "old_carrier_slot_count": carrier_count[rule.rule_id],
            "old_carrier_host_count": len(carrier_hosts[rule.rule_id]),
            "future_runtime_action": (
                "AUTO_SELECT_FROM_COMPLETE_HOST" if gate == "AUTO_CONTEXT"
                else "DO_NOT_REUSE_OLD_SOURCE_ID__FALL_THROUGH_TO_NEXT_RULE"
            ),
            "guard": "FIXED_GDT583_RULE_GATE__NO_NEW_SURFACE_OR_ACTION_SENSE",
        })
    active_manual_ids = sorted(
        rule for rule in ({row["gdt584_rule_id"] for row in actions} - known_g583_ids)
        if carrier_count[rule]
    )
    for manual in active_manual_ids:
        members = [row for row in actions if row["gdt584_rule_id"] == manual]
        parents = {row["gdt583_rule_id"] for row in members}
        if len(parents) != 1:
            raise RuntimeError(f"Manual rule has multiple parents: {manual} {parents}")
        rule_gate.append({
            "rule_gate_ordinal": len(rule_gate) + 1,
            "rule_id": manual,
            "gate_class": "MANUAL_GDT584_OVERRIDE",
            "parent_rule_id": next(iter(parents)),
            "action_root": members[0]["root"],
            "registers": pipe(row["register"] for row in members),
            "priority": "MANUAL_AFTER_GDT583",
            "selection_requirements": "EXPLICIT_MANUAL_CONTEXT_OVERRIDE_REQUIRED",
            "old_action_occurrence_count": action_count_584[manual],
            "old_carrier_slot_count": carrier_count[manual],
            "old_carrier_host_count": len(carrier_hosts[manual]),
            "future_runtime_action": "USE_PARENT_UNLESS_EXPLICIT_MANUAL_OVERRIDE",
            "guard": "OLD_GDT584_OCCURRENCE_READING__NOT_AUTOMATIC_ON_NEW_PAGE",
        })

    fallbacks: list[dict[str, Any]] = []
    for register in REGISTER_ORDER:
        for root in ROOT_ORDER:
            form = REGISTER_FALLBACK_FORMS[(register, root)]
            members = [row for row in assignments if row["register"] == register and row["carrier_root"] == root]
            fallbacks.append({
                "fallback_ordinal": len(fallbacks) + 1,
                "register": register,
                "carrier_root": root,
                "portable_core": PORTABLE_CORE[root],
                "decision": form["decision"],
                "lemma_de": form["lemma"],
                "object_form_de": form["object"],
                "genitive_form_de": form["genitive"],
                "observed_assignment_count": len(members),
                "observed_action_rule_count": len({row["gdt584_rule_id"] for row in members}),
                "observed_lemma_inventory_de": pipe(row["gdt587_lemma_de"] for row in members),
                "guard": "REGISTER_ROOT_FALLBACK_ONLY__NO_UNSEEN_ACTION_CELL_INVENTION",
            })

    future_cells: list[dict[str, Any]] = []
    for register in REGISTER_ORDER:
        rules = sorted(
            [rule for rule in G583_RULES.RULES if not rule.source_ids and register in rule.registers],
            key=lambda rule: (rule.priority, rule.rule_id),
        )
        for rule in rules:
            for root in ROOT_ORDER:
                members = [
                    row for row in assignments
                    if (row["register"], row["gdt584_rule_id"], row["carrier_root"])
                    == (register, rule.rule_id, root)
                ]
                fallback = REGISTER_FALLBACK_FORMS[(register, root)]
                state = "OBSERVED_CELL" if members else fallback["decision"]
                future_cells.append({
                    "matrix_ordinal": len(future_cells) + 1,
                    "register": register,
                    "automatic_gdt583_rule_id": rule.rule_id,
                    "action_root": rule.root,
                    "rule_priority": rule.priority,
                    "carrier_root": root,
                    "portable_core": PORTABLE_CORE[root],
                    "matrix_state": state,
                    "observed_assignment_count": len(members),
                    "observed_host_count": len({row["primary_governor_key"] for row in members}),
                    "observed_page_count": len({row["physical_page"] for row in members}),
                    "observed_pages": pipe(row["physical_page"] for row in members),
                    "observed_lemmas_de": pipe(row["gdt587_lemma_de"] for row in members),
                    "fallback_lemma_de": fallback["lemma"],
                    "fallback_object_form_de": fallback["object"],
                    "fallback_genitive_form_de": fallback["genitive"],
                    "selection_requirements": requirement(rule),
                    "guard": "DECLARED_AUTO_RULE_REGISTER_ROOT_CONTRACT__RUNTIME_STILL_USES_COMPLETE_HOST",
                })

    packet_cards: list[dict[str, Any]] = []
    auto_ids = {rule.rule_id for rule in G583_RULES.RULES if not rule.source_ids}
    for packet, description in PACKET_CARD_DESCRIPTIONS.items():
        members = [row for row in assignments if row["gdt587_packet_rule_id"] == packet]
        packet_cards.append({
            "packet_card_ordinal": len(packet_cards) + 1,
            "gdt587_packet_rule_id": packet,
            "condition": description["condition"],
            "template_de": description["template_de"],
            "multiplicity_fallback": description["fallback"],
            "old_carrier_slot_count": len(members),
            "old_host_count": len({row["primary_governor_key"] for row in members}),
            "old_page_count": len({row["physical_page"] for row in members}),
            "old_pages": pipe(row["physical_page"] for row in members),
            "auto_rule_carrier_slot_count": sum(row["gdt584_rule_id"] in auto_ids for row in members),
            "manual_override_carrier_slot_count": sum(row["gdt584_rule_id"] not in auto_ids for row in members),
            "guard": "PACKET_RULE_PRECEDES_UNOBSERVED_CELL_FALLBACK__PRESERVE_WRITTEN_COUNTS",
        })

    assignment_mobility: list[dict[str, Any]] = []
    for row in assignments:
        page = row["physical_page"]
        tier, tier_pages = classify(row, maps)
        layer_tier, layer_pages = classify(row, layer_maps)
        exact_pages = other_pages(maps["exact_pages"][exact_key(row)], page)
        cell_pages = other_pages(maps["cell_pages"][cell_key(row)], page)
        cell_lemma_pages = other_pages(maps["cell_lemma_pages"][(*cell_key(row), row["gdt587_lemma_de"])], page)
        register_pages = other_pages(maps["register_root_pages"][register_root_key(row)], page)
        register_lemma_pages = other_pages(
            maps["register_lemma_pages"][(*register_root_key(row), row["gdt587_lemma_de"])], page
        )
        root_lemma_pages = other_pages(maps["root_lemma_pages"][root_lemma_key(row)], page)
        assignment_mobility.append({
            "mobility_ordinal": len(assignment_mobility) + 1,
            "carrier_slot_id": row["carrier_slot_id"],
            "primary_governor_key": row["primary_governor_key"],
            "statement_or_record_id": row["statement_or_record_id"],
            "physical_page": page,
            "layer": row["layer"],
            "register": row["register"],
            "gdt584_rule_id": row["gdt584_rule_id"],
            "carrier_root": row["carrier_root"],
            "carrier_root_signature": row["carrier_root_signature"],
            "gdt587_context_family": row["gdt587_context_family"],
            "gdt587_lemma_de": row["gdt587_lemma_de"],
            "gdt587_packet_rule_id": row["gdt587_packet_rule_id"],
            "strict_exact_foreign_page_count": len(exact_pages),
            "strict_exact_foreign_pages": pipe(exact_pages),
            "same_action_root_foreign_page_count": len(cell_pages),
            "same_action_root_foreign_pages": pipe(cell_pages),
            "same_action_root_lemma_foreign_pages": pipe(cell_lemma_pages),
            "same_register_root_foreign_page_count": len(register_pages),
            "same_register_root_foreign_pages": pipe(register_pages),
            "same_register_root_lemma_foreign_pages": pipe(register_lemma_pages),
            "cross_register_same_root_lemma_foreign_pages": pipe(root_lemma_pages),
            "transfer_tier": tier,
            "transfer_tier_short": TIER_SHORT[tier],
            "tier_supporting_pages": pipe(tier_pages),
            "foreign_example_carrier_slot_id": foreign_example(assignments, row, tier),
            "same_layer_transfer_tier": layer_tier,
            "same_layer_supporting_pages": pipe(layer_pages),
            "future_intake_action": {
                TIER_EXACT: "REUSE_EXACT_SELECTION_AND_PACKET",
                TIER_CELL: "REUSE_ACTION_ROOT_LEMMA_REBUILD_PACKET_COUNTS",
                TIER_REGISTER: "USE_REGISTER_ROOT_FALLBACK_UNLESS_CELL_OBSERVED",
                TIER_PRIVATE: "KEEP_CROSS_REGISTER_RIVAL_AND_PORTABLE_CORE",
            }[tier],
            "guard": "FOREIGN_PAGE_PROVENANCE_ONLY__NOT_INDEPENDENT_SEMANTIC_CONFIRMATION",
        })

    selection_groups: dict[tuple[str, ...], list[dict[str, str]]] = defaultdict(list)
    for row in assignments:
        selection_groups[exact_key(row)].append(row)
    selections: list[dict[str, Any]] = []
    for key in sorted(selection_groups):
        members = selection_groups[key]
        row = members[0]
        pages = {x["physical_page"] for x in members}
        selections.append({
            "selection_ordinal": len(selections) + 1,
            "register": row["register"],
            "gdt584_rule_id": row["gdt584_rule_id"],
            "carrier_root": row["carrier_root"],
            "carrier_root_signature": row["carrier_root_signature"],
            "gdt587_context_family": row["gdt587_context_family"],
            "gdt587_lemma_de": row["gdt587_lemma_de"],
            "gdt587_object_form_de": row["gdt587_object_form_de"],
            "gdt587_genitive_form_de": row["gdt587_genitive_form_de"],
            "gdt587_packet_rule_id": row["gdt587_packet_rule_id"],
            "assignment_count": len(members),
            "host_count": len({x["primary_governor_key"] for x in members}),
            "page_count": len(pages),
            "pages": pipe(pages),
            "layer_profile": pipe(x["layer"] for x in members),
            "strict_type_mobility": "MULTI_PAGE" if len(pages) > 1 else "SINGLE_PAGE",
            "example_carrier_slot_ids": "|".join(x["carrier_slot_id"] for x in members[:6]),
            "guard": "OBSERVED_STRICT_SELECTION_SIGNATURE_ONLY",
        })

    assignment_by_slot = {row["carrier_slot_id"]: row for row in assignment_mobility}
    cell_groups: dict[tuple[str, str, str], list[dict[str, str]]] = defaultdict(list)
    for row in assignments:
        cell_groups[cell_key(row)].append(row)
    cells: list[dict[str, Any]] = []
    for key in sorted(cell_groups, key=lambda item: (REGISTER_ORDER.index(item[0]), item[1], ROOT_ORDER[item[2]])):
        members = cell_groups[key]
        tier_counts = Counter(assignment_by_slot[row["carrier_slot_id"]]["transfer_tier"] for row in members)
        pages = {row["physical_page"] for row in members}
        if tier_counts[TIER_EXACT] == len(members):
            profile = "EVERY_ASSIGNMENT_EXACT_OTHER_PAGE"
        elif tier_counts[TIER_EXACT]:
            profile = "PARTIAL_EXACT_OTHER_PAGE"
        elif len(pages) > 1:
            profile = "CROSS_PAGE_CELL_DIFFERENT_SIGNATURES"
        elif tier_counts[TIER_REGISTER]:
            profile = "SINGLE_PAGE_CELL_REGISTER_ROOT_FALLBACK"
        else:
            profile = "TRULY_PAGE_PRIVATE_CELL"
        cells.append({
            "cell_ordinal": len(cells) + 1,
            "register": key[0],
            "gdt584_rule_id": key[1],
            "carrier_root": key[2],
            "portable_core": PORTABLE_CORE[key[2]],
            "assignment_count": len(members),
            "host_count": len({row["primary_governor_key"] for row in members}),
            "page_count": len(pages),
            "pages": pipe(pages),
            "strict_selection_signature_count": len({exact_key(row) for row in members}),
            "selected_lemmas_de": pipe(row["gdt587_lemma_de"] for row in members),
            "carrier_root_signatures": pipe(row["carrier_root_signature"] for row in members),
            "packet_rules": pipe(row["gdt587_packet_rule_id"] for row in members),
            "exact_foreign_assignment_count": tier_counts[TIER_EXACT],
            "same_cell_foreign_assignment_count": tier_counts[TIER_CELL],
            "register_root_fallback_assignment_count": tier_counts[TIER_REGISTER],
            "page_private_assignment_count": tier_counts[TIER_PRIVATE],
            "cell_mobility_profile": profile,
            "example_carrier_slot_ids": "|".join(row["carrier_slot_id"] for row in members[:6]),
            "guard": "OBSERVED_ACTION_ROOT_CELL__NO_UNOBSERVED_MATRIX_FILL",
        })

    by_governor: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in assignments:
        by_governor[row["primary_governor_key"]].append(row)
    for rows in by_governor.values():
        rows.sort(key=lambda row: int(row["assignment_ordinal"]))
    special = {key: rows for key, rows in by_governor.items() if rows[0]["gdt587_packet_rule_id"] != "DEFAULT_GDT584_OBJECT_COMPOSITION"}
    packet_multiset_pages: dict[tuple[str, str], set[str]] = defaultdict(set)
    register_shape_pages: dict[tuple[str, str, str], set[str]] = defaultdict(set)
    ordered_pages: dict[tuple[str, str], set[str]] = defaultdict(set)
    for rows in special.values():
        packet = rows[0]["gdt587_packet_rule_id"]
        multiset = root_multiset(rows)
        sequence = "+".join(row["carrier_root"] for row in rows)
        page = rows[0]["physical_page"]
        packet_multiset_pages[(packet, multiset)].add(page)
        register_shape_pages[(rows[0]["register"], packet, multiset)].add(page)
        ordered_pages[(packet, sequence)].add(page)

    running_host_by_key = {row["primary_governor_key"]: row for row in old_hosts}
    local_by_id = {row["source_event_id"]: row for row in old_local}
    special_hosts: list[dict[str, Any]] = []
    for governor, members in sorted(special.items(), key=lambda item: int(item[1][0]["assignment_ordinal"])):
        row = members[0]
        packet = row["gdt587_packet_rule_id"]
        multiset = root_multiset(members)
        sequence = "+".join(item["carrier_root"] for item in members)
        page = row["physical_page"]
        unit_id = row["statement_or_record_id"] if row["statement_or_record_id"] != "NOT_APPLICABLE" else row["source_event_or_card_id"]
        old_clause = (
            running_host_by_key[governor]["gdt587_reader_clause_de"]
            if governor in running_host_by_key else local_by_id[row["source_event_or_card_id"]]["gdt587_primary_reader_de"]
        )
        counts = Counter(item["carrier_root"] for item in members)
        special_hosts.append({
            "packet_host_ordinal": len(special_hosts) + 1,
            "primary_governor_key": governor,
            "reader_unit_id": unit_id,
            "source_event_or_card_id": row["source_event_or_card_id"],
            "physical_page": page,
            "layer_profile": pipe(item["layer"] for item in members),
            "register": row["register"],
            "gdt584_rule_id": row["gdt584_rule_id"],
            "gdt587_packet_rule_id": packet,
            "written_carrier_slot_count": len(members),
            "distinct_root_count": len(counts),
            "written_root_sequence": sequence,
            "written_root_multiset": multiset,
            "presence_signature": row["carrier_root_signature"],
            "lemma_count_trace": lemma_trace(members, with_counts=True),
            "carrier_count_trace_de": count_trace_de(members),
            "repeated_root": "YES" if any(count > 1 for count in counts.values()) else "NO",
            "packet_multiset_foreign_pages": pipe(other_pages(packet_multiset_pages[(packet, multiset)], page)),
            "ordered_sequence_foreign_pages": pipe(other_pages(ordered_pages[(packet, sequence)], page)),
            "multiset_transfer_status": (
                "SAME_PACKET_MULTISET_OTHER_PAGE"
                if other_pages(packet_multiset_pages[(packet, multiset)], page)
                else "PACKET_MULTISET_PAGE_PRIVATE"
            ),
            "gdt587_reader_clause_de": old_clause,
            "count_safe_action": "REPAIR_FLUENT_CHANNEL" if unit_id in MULTIPLICITY_REPAIRS else "RETAIN_FLUENT_CHANNEL",
            "guard": "ORDERED_WRITTEN_ROOTS_RECONSTRUCTED_FROM_ASSIGNMENT_ROWS__NOT_SET_SIGNATURE",
        })

    shape_groups: dict[tuple[str, str, str], list[dict[str, Any]]] = defaultdict(list)
    for row in special_hosts:
        shape_groups[(row["register"], row["gdt587_packet_rule_id"], row["written_root_multiset"])].append(row)
    special_shapes: list[dict[str, Any]] = []
    for key in sorted(shape_groups):
        members = shape_groups[key]
        pages = {row["physical_page"] for row in members}
        cross_pages = packet_multiset_pages[(key[1], key[2])]
        special_shapes.append({
            "shape_ordinal": len(special_shapes) + 1,
            "register": key[0],
            "gdt587_packet_rule_id": key[1],
            "written_root_multiset": key[2],
            "host_count": len(members),
            "page_count": len(pages),
            "pages": pipe(pages),
            "cross_register_packet_multiset_page_count": len(cross_pages),
            "cross_register_packet_multiset_pages": pipe(cross_pages),
            "ordered_sequence_inventory": pipe(row["written_root_sequence"] for row in members),
            "repeated_root_host_count": sum(row["repeated_root"] == "YES" for row in members),
            "example_host_keys": "|".join(row["primary_governor_key"] for row in members[:5]),
            "guard": "MULTIPLICITY_AWARE_SPECIAL_PACKET_SHAPE",
        })

    special_by_unit: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in special_hosts:
        special_by_unit[row["reader_unit_id"]].append(row)
    repairs: list[dict[str, Any]] = []
    for unit_id, patch in MULTIPLICITY_REPAIRS.items():
        candidates = [
            row for row in special_by_unit[unit_id]
            if row["repeated_root"] == "YES" and patch["old"] in row["gdt587_reader_clause_de"]
        ]
        if len(candidates) != 1:
            raise RuntimeError(f"Repair target host mismatch: {unit_id} ({len(candidates)})")
        host = candidates[0]
        old_clause = host["gdt587_reader_clause_de"]
        old_fragment = patch["old"]
        if old_clause.count(old_fragment) != 1:
            raise RuntimeError(f"Old packet clause mismatch: {unit_id}")
        root_counts = Counter(
            row["carrier_root"] for row in special[host["primary_governor_key"]]
        )
        repairs.append({
            "repair_ordinal": len(repairs) + 1,
            "reader_unit_id": unit_id,
            "primary_governor_key": host["primary_governor_key"],
            "physical_page": host["physical_page"],
            "register": host["register"],
            "gdt587_packet_rule_id": host["gdt587_packet_rule_id"],
            "written_carrier_slot_ids": "|".join(row["carrier_slot_id"] for row in special[host["primary_governor_key"]]),
            "written_root_sequence": host["written_root_sequence"],
            "written_root_multiset": host["written_root_multiset"],
            "carrier_count_trace_de": host["carrier_count_trace_de"],
            "collapsed_written_slot_count": sum(count - 1 for count in root_counts.values() if count > 1),
            "gdt587_reader_clause_de": old_fragment,
            "gdt588_count_safe_clause_de": patch["new"],
            "count_interpretation": "×N_COUNTS_WRITTEN_CARRIERS__NOT_REAL_OBJECTS",
            "guard": "FLUENT_CHANNEL_REPAIR_ONLY__EXACT_LEDGER_AND_TRACE_ALREADY_COMPLETE",
        })

    statements: list[dict[str, Any]] = []
    for source_row in old_statements:
        row: dict[str, Any] = dict(source_row)
        unit_id = row["statement_id"]
        primary = row["gdt587_primary_reader_de"]
        changed = "NO"
        if unit_id in MULTIPLICITY_REPAIRS:
            patch = MULTIPLICITY_REPAIRS[unit_id]
            if primary.count(patch["old"]) != 1:
                raise RuntimeError(f"Statement replacement mismatch: {unit_id}")
            primary = primary.replace(patch["old"], patch["new"], 1)
            changed = "YES"
        row.update({
            "gdt588_base_reader_de": row["gdt587_primary_reader_de"],
            "gdt588_primary_reader_de": primary,
            "gdt588_multiplicity_repair": changed,
            "gdt588_guard": "GDT587_READER_PLUS_EXPLICIT_WRITTEN_CARRIER_MULTIPLICITY",
        })
        statements.append(row)
    local_cards: list[dict[str, Any]] = []
    for source_row in old_local:
        row = dict(source_row)
        unit_id = row["source_event_id"]
        primary = row["gdt587_primary_reader_de"]
        changed = "NO"
        if unit_id in MULTIPLICITY_REPAIRS:
            patch = MULTIPLICITY_REPAIRS[unit_id]
            if primary.count(patch["old"]) != 1:
                raise RuntimeError(f"Local replacement mismatch: {unit_id}")
            primary = primary.replace(patch["old"], patch["new"], 1)
            changed = "YES"
        row.update({
            "gdt588_base_reader_de": row["gdt587_primary_reader_de"],
            "gdt588_primary_reader_de": primary,
            "gdt588_multiplicity_repair": changed,
            "gdt588_guard": "GDT587_READER_PLUS_EXPLICIT_WRITTEN_CARRIER_MULTIPLICITY",
        })
        local_cards.append(row)

    special_by_page: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in special_hosts:
        special_by_page[row["physical_page"]].append(row)
    repairs_by_page = Counter(row["physical_page"] for row in repairs)
    mobility_by_page: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in assignment_mobility:
        mobility_by_page[row["physical_page"]].append(row)
    pages: list[dict[str, Any]] = []
    page_order: list[str] = []
    for row in assignments:
        if row["physical_page"] not in page_order:
            page_order.append(row["physical_page"])
    for page in page_order:
        members = mobility_by_page[page]
        tiers = Counter(row["transfer_tier"] for row in members)
        packets = special_by_page[page]
        pages.append({
            "page_ordinal": len(pages) + 1,
            "physical_page": page,
            "carrier_assignment_count": len(members),
            "exact_selection_other_page_count": tiers[TIER_EXACT],
            "same_action_root_other_page_count": tiers[TIER_CELL],
            "register_root_fallback_count": tiers[TIER_REGISTER],
            "page_private_register_root_count": tiers[TIER_PRIVATE],
            "exact_selection_percent": f"{100 * tiers[TIER_EXACT] / len(members):.2f}",
            "same_action_lemma_or_better_percent": f"{100 * (tiers[TIER_EXACT] + tiers[TIER_CELL]) / len(members):.2f}",
            "special_packet_host_count": len(packets),
            "packet_multiset_foreign_host_count": sum(row["multiset_transfer_status"] == "SAME_PACKET_MULTISET_OTHER_PAGE" for row in packets),
            "multiplicity_repair_count": repairs_by_page[page],
            "readiness_note": (
                "HAS_PAGE_PRIVATE_SOURCE_AIN" if tiers[TIER_PRIVATE]
                else "NO_PAGE_PRIVATE_REGISTER_ROOT"
            ),
            "guard": "OLD_PAGE_PROVENANCE_PROFILE__NO_PAGE_REFIT",
        })

    tier_counts = Counter(row["transfer_tier"] for row in assignment_mobility)
    layer_tier_counts = Counter(row["same_layer_transfer_tier"] for row in assignment_mobility)
    cell_profiles = Counter(row["cell_mobility_profile"] for row in cells)
    packet_transfer = Counter(row["multiset_transfer_status"] for row in special_hosts)
    matrix_counts = Counter(row["matrix_state"] for row in future_cells)
    gate_counts = Counter(row["gate_class"] for row in rule_gate)
    result = {
        "experiment_id": "GDT588",
        "status": STATUS,
        "input_sha256": {name: sha256(path) for name, path in INPUTS.items()},
        "assignment_count": len(assignment_mobility),
        "strict_selection_signature_count": len(selections),
        "mobile_strict_selection_signature_count": sum(row["strict_type_mobility"] == "MULTI_PAGE" for row in selections),
        "tier_counts": dict(tier_counts),
        "same_layer_tier_counts": dict(layer_tier_counts),
        "same_action_root_lemma_or_better": tier_counts[TIER_EXACT] + tier_counts[TIER_CELL],
        "cell_count": len(cells),
        "cell_profile_counts": dict(cell_profiles),
        "rule_gate_count": len(rule_gate),
        "rule_gate_counts": dict(gate_counts),
        "future_cell_matrix_count": len(future_cells),
        "future_cell_matrix_counts": dict(matrix_counts),
        "register_root_fallback_count": len(fallbacks),
        "packet_card_count": len(packet_cards),
        "special_packet_host_count": len(special_hosts),
        "special_packet_carrier_count": sum(int(row["written_carrier_slot_count"]) for row in special_hosts),
        "special_packet_shape_count": len(special_shapes),
        "special_packet_transfer_counts": dict(packet_transfer),
        "repeated_root_special_host_count": sum(row["repeated_root"] == "YES" for row in special_hosts),
        "multiplicity_repair_count": len(repairs),
        "changed_statement_count": sum(row["gdt588_multiplicity_repair"] == "YES" for row in statements),
        "changed_local_card_count": sum(row["gdt588_multiplicity_repair"] == "YES" for row in local_cards),
        "complete_statement_count": len(statements),
        "complete_local_card_count": len(local_cards),
        "page_count": len(pages),
    }
    contract = {
        "experiment_id": "GDT588",
        "input_scope": "already segmented complete carrier host only",
        "required_host_fields": [
            "action_root", "register", "ordered carrier_roots", "direct_tokens", "host_tokens",
            "previous_action", "next_action",
        ],
        "routing_order": [
            "route names and addresses to GDT470/GDT586",
            "select one non-source-bound GDT583 rule from the complete host",
            "apply one of eight known packet rules when its complete condition matches",
            "use an observed action-root cell only for an observed lemma variant",
            "otherwise use a register-invariant root noun",
            "otherwise retain the broad register default",
            "always retain every written carrier and print counts above one",
        ],
        "manual_override_policy": "nine GDT584 carrier-active overrides require an explicit manual flag",
        "unknown_policy": "unknown register or root returns portable POSTEN/WERT/ANTEIL/EINHEIT where available",
        "surface_parser": "NONE",
        "new_pages": "NONE",
        "commands": {
            "complete_host": "python3 experiments/yolo/gdt588_carrier_transfer_readiness_deck/src/read_carrier_host.py --help",
            "manual_fixed_rule": "python3 experiments/yolo/gdt588_carrier_transfer_readiness_deck/src/read_carrier.py --help",
        },
    }

    for name, rows in (
        ("rule_gate", rule_gate), ("fallbacks", fallbacks), ("future_cells", future_cells),
        ("packet_cards", packet_cards), ("assignments", assignment_mobility),
        ("selections", selections), ("cells", cells), ("special_hosts", special_hosts),
        ("special_shapes", special_shapes), ("repairs", repairs), ("pages", pages),
        ("statements", statements), ("local_cards", local_cards),
    ):
        write_tsv(OUTPUTS[name], rows)
    OUTPUTS["book"].write_text(build_book(statements, local_cards), encoding="utf-8")
    OUTPUTS["deck"].write_text(build_deck(result, repairs), encoding="utf-8")
    OUTPUTS["contract"].write_text(json.dumps(contract, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    OUTPUTS["result"].write_text(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
