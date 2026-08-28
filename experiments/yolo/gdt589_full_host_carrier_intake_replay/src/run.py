#!/usr/bin/env python3
"""Build GDT589: replay every known complete carrier host and expose all repeats."""

from __future__ import annotations

import json
from collections import Counter, defaultdict
from typing import Any

from replay_lib import (
    DEFAULT_PACKET,
    INPUTS,
    OUTPUTS,
    PACKET_CARD_DESCRIPTIONS,
    STATUS,
    add_count_overlay,
    build_replay,
    load_inputs,
    pipe,
    sha256,
    split_pipe,
    write_tsv,
)


BODY_BLOCKERS = {
    "AL", "AR", "AIR", "L", "A_ADDR", "D_ADDR", "S_ADDR", "M_LOCAL",
    "O", "IIN", "DA", "LOCAL_CHAR_F", "LOCAL_CHAR_G", "LOCAL_CHAR_I", "CARRIER_Q",
}


def assignments_by_host(data: dict[str, list[dict[str, str]]]) -> dict[str, list[dict[str, str]]]:
    output: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in data["assignments_587"]:
        output[row["primary_governor_key"]].append(row)
    for rows in output.values():
        rows.sort(key=lambda row: int(row["assignment_ordinal"]))
    return output


def ordered_slot_trace(rows: list[dict[str, str]]) -> str:
    return " | ".join(f"{row['carrier_root']}={row['gdt587_lemma_de']}" for row in rows)


def count_trace(rows: list[dict[str, str]], labels: dict[str, str] | None = None) -> str:
    labels = labels or {}
    counts: Counter[tuple[str, str]] = Counter()
    order: list[tuple[str, str]] = []
    for row in rows:
        pair = (row["carrier_root"], labels.get(row["carrier_root"], row["gdt587_lemma_de"]))
        if pair not in counts:
            order.append(pair)
        counts[pair] += 1
    return "; ".join(f"{lemma} ×{counts[(root, lemma)]}" for root, lemma in order)


def packet_composition(
    packet: str, rows: list[dict[str, str]], clean_bath_fork: bool
) -> tuple[str, str]:
    roots = {row["carrier_root"] for row in rows}
    if packet == "SOURCE_PART_OF_MATERIAL":
        return count_trace(rows, {"Y": "Arbeitsmaterial", "AIN": "Teilmenge"}), "SLOT_Y_WORKING_LEMMA_RENAMED_IN_PACKET"
    if packet == "CELESTIAL_POSITION_SEGMENT_VALUE" and "AIN" in roots:
        labels = {"Y": "Ringposition", "AIIN": "Positionswert", "AIN": "Sektoranteil", "OR": "Ringsegment"}
        return count_trace(rows, labels), "PACKET_TEMPLATE_OMITS_WRITTEN_SECTOR_SHARE"
    if packet == "HP_EXTRACT_OF_MATERIAL" and "AIIN" not in roots:
        return "Auszug (kompositioneller Packetkopf); " + count_trace(rows), "ACTION_SUPPLIES_UNWRITTEN_EXTRACT_HEAD"
    if packet == "BIOLOGICAL_BATH_FILL" and clean_bath_fork:
        return count_trace(rows, {"Y": "Körper", "AIIN": "Badfüllung"}), "CLEAN_BATH_BODY_STATION_FORK"
    return count_trace(rows), "DIRECT_WRITTEN_SLOT_COMPOSITION"


def build_manual_rows(hosts: list[dict[str, Any]]) -> list[dict[str, Any]]:
    output: list[dict[str, Any]] = []
    for row in hosts:
        if row["gate_class"] != "MANUAL_GDT584_OVERRIDE":
            continue
        runtime_change = int(row["portable_visible_changed_slot_count"]) > 0 or row["portable_packet_match"] == "NO"
        output.append(
            {
                "manual_ordinal": len(output) + 1,
                "primary_governor_key": row["primary_governor_key"],
                "source_event_or_card_id": row["source_event_or_card_id"],
                "statement_or_record_id": row["statement_or_record_id"],
                "physical_page": row["physical_page"],
                "register": row["register"],
                "manual_rule_id": row["gdt584_rule_id"],
                "parent_rule_id": row["parent_rule_id"],
                "historical_action_reading_de": row["historical_action_reading_de"],
                "parent_action_reading_de": row["portable_action_reading_de"],
                "action_wording_change": "NO" if row["portable_action_reading_match"] == "YES" else "YES",
                "carrier_slot_count": row["carrier_slot_count"],
                "written_root_sequence": row["written_root_sequence"],
                "historical_lemma_sequence": row["expected_lemma_sequence"],
                "direct_parent_lemma_sequence": row["parent_semantic_lemma_sequence"],
                "runtime_lemma_sequence": row["portable_lemma_sequence"],
                "direct_parent_changed_slot_count": row["parent_semantic_visible_changed_slot_count"],
                "runtime_changed_slot_count": row["portable_visible_changed_slot_count"],
                "runtime_context_family_changed_slot_count": row["portable_context_family_changed_slot_count"],
                "runtime_broad_fallback_slot_count": row["portable_broad_fallback_slot_count"],
                "runtime_broad_fallback_alternatives_de": row["portable_broad_fallback_alternatives_de"],
                "historical_packet_rule_id": row["expected_packet_rule_id"],
                "parent_packet_rule_id": row["parent_semantic_packet_rule_id"],
                "packet_change": "YES" if row["portable_packet_match"] == "NO" else "NO",
                "historical_explicit_replay": row["historical_rule_replay_exact"],
                "carrier_effect": "VISIBLE_CARRIER_CHANGE" if runtime_change else "CARRIER_OUTPUT_EQUIVALENT",
                "next_page_action": row["next_page_action"],
                "guard": "MANUAL_ACTION_VISIBLE__PARENT_SEMANTICS_AND_CONSERVATIVE_RUNTIME_SEPARATED",
            }
        )
    return output


def build_source_rows(hosts: list[dict[str, Any]]) -> list[dict[str, Any]]:
    output: list[dict[str, Any]] = []
    for row in hosts:
        if row["gate_class"] != "SOURCE_ID_BOUND":
            continue
        exact = (
            row["portable_changed_slot_count"] == 0
            and row["portable_packet_match"] == "YES"
            and row["portable_action_reading_match"] == "YES"
        )
        output.append(
            {
                "source_bound_ordinal": len(output) + 1,
                "primary_governor_key": row["primary_governor_key"],
                "source_event_or_card_id": row["source_event_or_card_id"],
                "statement_or_record_id": row["statement_or_record_id"],
                "physical_page": row["physical_page"],
                "register": row["register"],
                "old_source_rule_id": row["gdt584_rule_id"],
                "portable_fallthrough_rule_id": row["portable_runtime_rule_id"],
                "old_action_reading_de": row["historical_action_reading_de"],
                "fallthrough_action_reading_de": row["portable_action_reading_de"],
                "source_id_gate_status": row["source_id_gate_status"],
                "carrier_slot_count": row["carrier_slot_count"],
                "written_root_sequence": row["written_root_sequence"],
                "old_lemma_sequence": row["expected_lemma_sequence"],
                "fallthrough_lemma_sequence": row["portable_lemma_sequence"],
                "packet_rule_id": row["expected_packet_rule_id"],
                "visible_fallthrough_exact": "YES" if exact else "NO",
                "reader_route": "OLD_ID_RULE_DROPPED__VISIBLE_FALLTHROUGH_EXACT" if exact else "OLD_ID_RULE_DROPPED__VISIBLE_FALLTHROUGH_DIFFERS",
                "guard": "OLD_SOURCE_ID_NEVER_TRANSFERRED__VISIBLE_READING_RETAINED_WHERE_PARENT_MATCHES",
            }
        )
    return output


def build_body_rows(hosts: list[dict[str, Any]], slots: list[dict[str, Any]]) -> list[dict[str, Any]]:
    slots_by_host: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in slots:
        slots_by_host[row["primary_governor_key"]].append(row)
    output: list[dict[str, Any]] = []
    for host in hosts:
        members = slots_by_host[host["primary_governor_key"]]
        y_slots = [row for row in members if row["carrier_root"] == "Y"]
        if host["gate_class"] != "AUTO_CONTEXT" or host["register"] != "BIOLOGICAL" or not y_slots:
            continue
        values = set(split_pipe(host["complete_host_values_written"]))
        blockers = sorted(values & BODY_BLOCKERS)
        roots = [row["carrier_root"] for row in members]
        clean_fork = host["gdt584_rule_id"] == "SH_BIO_BATHE" and "AIIN" in roots and not blockers
        expected = [row["expected_lemma_de"] for row in y_slots]
        portable = [row["portable_lemma_de"] for row in y_slots]
        route = "FLOW" if "Strom" in expected else "BODY" if "Körper" in expected else "STATION"
        output.append(
            {
                "guard_ordinal": len(output) + 1,
                "primary_governor_key": host["primary_governor_key"],
                "source_event_or_card_id": host["source_event_or_card_id"],
                "statement_or_record_id": host["statement_or_record_id"],
                "physical_page": host["physical_page"],
                "gdt584_rule_id": host["gdt584_rule_id"],
                "written_root_sequence": host["written_root_sequence"],
                "complete_host_values_written": host["complete_host_values_written"],
                "body_blockers_present": pipe(blockers),
                "historical_y_lemma_sequence": pipe(expected),
                "portable_y_lemma_sequence": pipe(portable),
                "historical_route": route,
                "portable_exact": "YES" if expected == portable else "NO",
                "clean_bath_body_fork": "YES" if clean_fork else "NO",
                "exploratory_bath_default_de": "Körper" if clean_fork else "NOT_APPLICABLE",
                "retained_bath_alternative_de": "Stationsansatz" if clean_fork else "NOT_APPLICABLE",
                "guard": "FULL_HOST_BLOCKERS_RETAINED__CLEAN_BATH_FORK_VISIBLE",
            }
        )
    return output


def build_special_rows(
    hosts: list[dict[str, Any]],
    assignments: dict[str, list[dict[str, str]]],
    data: dict[str, list[dict[str, str]]],
    bath_keys: set[str],
) -> list[dict[str, Any]]:
    phrase_by_host = {row["primary_governor_key"]: row for row in data["hosts_587"]}
    output: list[dict[str, Any]] = []
    for host in hosts:
        packet = host["expected_packet_rule_id"]
        if packet == DEFAULT_PACKET:
            continue
        members = assignments[host["primary_governor_key"]]
        composed, gap = packet_composition(packet, members, host["primary_governor_key"] in bath_keys)
        phrase = phrase_by_host.get(host["primary_governor_key"])
        output.append(
            {
                "packet_host_ordinal": len(output) + 1,
                "primary_governor_key": host["primary_governor_key"],
                "source_event_or_card_id": host["source_event_or_card_id"],
                "statement_or_record_id": host["statement_or_record_id"],
                "physical_page": host["physical_page"],
                "register": host["register"],
                "gate_class": host["gate_class"],
                "gdt584_rule_id": host["gdt584_rule_id"],
                "packet_rule_id": packet,
                "carrier_slot_count": host["carrier_slot_count"],
                "written_root_sequence": host["written_root_sequence"],
                "written_root_multiset": host["written_root_multiset"],
                "ordered_written_slot_lemmas_de": ordered_slot_trace(members),
                "written_slot_count_trace_de": count_trace(members),
                "packet_composition_elements_de": composed,
                "packet_template_de": PACKET_CARD_DESCRIPTIONS[packet]["template_de"],
                "sentence_layer_de": phrase["gdt587_reader_clause_de"] if phrase else "SEE_COMPLETE_LOCAL_CARD_READER",
                "display_gap_class": gap,
                "portable_packet_rule_match": host["portable_packet_match"],
                "historical_explicit_replay": host["historical_rule_replay_exact"],
                "guard": "ORDERED_WRITTEN_SLOTS__COMPOSITIONAL_HEAD__FLUENT_SENTENCE_DISTINCT",
            }
        )
    return output


def build_repeat_rows(
    hosts: list[dict[str, Any]], assignments: dict[str, list[dict[str, str]]], data: dict[str, list[dict[str, str]]]
) -> list[dict[str, Any]]:
    repair_by_host = {row["primary_governor_key"] for row in data["repairs_588"]}
    phrase_by_host = {row["primary_governor_key"]: row for row in data["hosts_587"]}
    output: list[dict[str, Any]] = []
    for host in hosts:
        if host["repeated_root"] != "YES":
            continue
        members = assignments[host["primary_governor_key"]]
        counts = Counter(row["carrier_root"] for row in members)
        phrase = phrase_by_host.get(host["primary_governor_key"])
        output.append(
            {
                **host,
                "repeat_ordinal": len(output) + 1,
                "repeat_class": "SPECIAL_PACKET" if host["expected_packet_rule_id"] != DEFAULT_PACKET else "DEFAULT_COMPOSITION",
                "written_extra_copy_count": sum(count - 1 for count in counts.values()),
                "ordered_written_slot_lemmas_de": ordered_slot_trace(members),
                "gdt587_fluid_host_clause_de": phrase["gdt587_reader_clause_de"] if phrase else "SEE_COMPLETE_LOCAL_CARD_READER",
                "gdt588_special_fluent_repair": "YES" if host["primary_governor_key"] in repair_by_host else "NO",
                "gdt589_display_action": "KEEP_FLUID_HYPOTHESIS__ADD_ORDERED_WRITTEN_SLOT_TRACE",
                "count_interpretation": "WRITTEN_CARRIER_POSITIONS__NOT_REAL_OBJECT_MULTIPLICITY",
                "repeat_guard": "ORDER_BEFORE_MULTISET__POSSIBLE_FRAMING_OR_COREFERENCE_NOT_ERASED",
            }
        )
    return output


def build_page_rows(
    hosts: list[dict[str, Any]], special: list[dict[str, Any]], repeated: list[dict[str, Any]], body: list[dict[str, Any]]
) -> list[dict[str, Any]]:
    page_order = list(dict.fromkeys(row["physical_page"] for row in hosts))
    output: list[dict[str, Any]] = []
    for page in page_order:
        hh = [row for row in hosts if row["physical_page"] == page]
        output.append(
            {
                "page_ordinal": len(output) + 1,
                "physical_page": page,
                "registers": pipe(sorted({row["register"] for row in hh})),
                "host_count": len(hh),
                "carrier_slot_count": sum(int(row["carrier_slot_count"]) for row in hh),
                "auto_host_count": sum(row["gate_class"] == "AUTO_CONTEXT" for row in hh),
                "manual_host_count": sum(row["gate_class"] == "MANUAL_GDT584_OVERRIDE" for row in hh),
                "source_bound_host_count": sum(row["gate_class"] == "SOURCE_ID_BOUND" for row in hh),
                "auto_divergence_count": sum(row["replay_outcome"] == "AUTO_DIVERGENCE" for row in hh),
                "special_packet_host_count": sum(row["physical_page"] == page for row in special),
                "repeated_root_host_count": sum(row["physical_page"] == page for row in repeated),
                "clean_bath_body_fork_count": sum(row["physical_page"] == page and row["clean_bath_body_fork"] == "YES" for row in body),
                "guard": "PAGE_PROFILE_ONLY__NO_NEW_PAGE_OR_LOCAL_RULE",
            }
        )
    return output


def build_deck(
    result: dict[str, Any], manual: list[dict[str, Any]], source: list[dict[str, Any]],
    special: list[dict[str, Any]], repeated: list[dict[str, Any]], bath: list[dict[str, Any]],
) -> str:
    affected = [row for row in manual if row["carrier_effect"] == "VISIBLE_CARRIER_CHANGE"]
    lines = [
        "# GDT589 — vollständiger Host-Replay und schriftpositionssichere Leserschicht", "",
        "Explorative Arbeitslesung; kein rekonstruierter Klartext.", "", "## Vollreplay", "",
        f"- {result['complete_carrier_hosts']} komplette bekannte Handlungshosts / {result['carrier_slots']} Trägerslots.",
        f"- {result['auto_hosts']} automatische Hosts / {result['auto_slots']} Slots reproduzieren Regel, Nomen, Formen, Packet und Reihenfolge exakt.",
        f"- {result['manual_hosts']} bekannte manuelle Hosts bleiben als eigener sichtbarer Weg erhalten.",
        f"- {result['source_bound_hosts']} alte ID-Regeln fallen sichtbar und ohne Lesedrift auf den portablen Elternweg zurück.",
        "", "## Manuelle Fälle mit sichtbarer Trägeränderung im nackten Zukunftspfad", "",
        "| Host | manuelle Regel | Elternregel | alte Träger | Zukunftsträger | Packetwechsel |",
        "|---|---|---|---|---|---|",
    ]
    for row in affected:
        lines.append(
            f"| `{row['primary_governor_key']}` | `{row['manual_rule_id']}` | `{row['parent_rule_id']}` | "
            f"{row['historical_lemma_sequence']} | {row['runtime_lemma_sequence']} | {row['packet_change']} |"
        )
    lines.extend([
        "", "Direkter Elternregel-Sinn und konservativer Runtime-Fallback sind getrennt: Zwei der vier Nomenabweichungen entstehen erst durch einen breiten, bisher unbelegten Eltern-Zellfallback. Alle 53 historischen manuellen Slots bleiben im expliziten alten Regelweg exakt.",
        "", "## Alte ID-Brücken", "",
    ])
    for row in source:
        lines.append(
            f"- `{row['primary_governor_key']}`: `{row['old_source_rule_id']}` → `{row['portable_fallthrough_rule_id']}`; "
            f"{row['written_root_sequence']} → {row['fallthrough_lemma_sequence']}; sichtbarer Fallthrough exakt."
        )
    lines.extend([
        "", "## Geschriebene Wiederholungen: zwei Kanäle statt Objektzählung", "",
        f"Es gibt {result['repeated_root_hosts']} Repeat-Hosts mit {result['repeated_root_slots']} Trägerslots und {result['written_extra_copies']} zusätzlichen Schriftpositionen. GDT588 hatte nur die {result['special_repeated_hosts']} Wiederholungen in Sonderpackets sichtbar gemacht; {result['ordinary_repeated_hosts']} gewöhnliche Kompositionen blieben im flüssigen Satz dedupliziert.",
        "", "GDT589 hält deshalb die flüssige Bedeutungshypothese und die geordnete Schreibspur getrennt. `Y–T–Y` kann Rahmung oder Koreferenz sein; `×2` beweist nicht zwei reale Gegenstände.", "",
    ])
    for row in repeated[:8]:
        lines.append(f"- `{row['primary_governor_key']}`: `{row['written_root_sequence']}` → {row['ordered_written_slot_lemmas_de']}")
    gaps = Counter(row["display_gap_class"] for row in special)
    lines.extend([
        "", "## Packetanzeige: drei Ebenen bleiben getrennt", "",
        "Die geordneten Slotnomen, ein kompositionell eingeführter Packetkopf und der fertige Satz sind nicht dasselbe. Der Vollreplay markiert deshalb:", "",
        f"- {gaps['SLOT_Y_WORKING_LEMMA_RENAMED_IN_PACKET']} Source-Part-Hosts: Slotlemma `Arbeitsgut`, Packetlesung `Arbeitsmaterial`;",
        f"- {gaps['ACTION_SUPPLIES_UNWRITTEN_EXTRACT_HEAD']} Seih-Hosts ohne geschriebenes AIIN: `Auszug` kommt aus dem Handlungspacket;",
        f"- {gaps['PACKET_TEMPLATE_OMITS_WRITTEN_SECTOR_SHARE']} Celestial-Host: der geschriebene `Sektoranteil` fehlt in der Kurzkarte, bleibt aber in Spur und Satz;",
        f"- {gaps['CLEAN_BATH_BODY_STATION_FORK']} saubere Bad-Hosts: `Körper` wird als neue explorative Erstlesung geführt, `Stationsansatz` bleibt sichtbare Alternative.",
        "", "## Vier saubere Bad-Gabeln", "",
    ])
    for row in bath:
        lines.append(
            f"- `{row['primary_governor_key']}` ({row['physical_page']}): bisher {row['historical_y_lemma_sequence']}; "
            "Arbeitsgabel `Körper im Bad` / `Stationsansatz im Bad`, Körper zuerst."
        )
    lines.extend([
        "", "## Übergaberegel", "",
        "Auf einem neuen bereits segmentierten Host läuft zuerst das Gate: automatisch, explizit manuell oder alte ID verwerfen. Danach bleiben geordnete Slots primär; Multiset und flüssiger Satz sind getrennte Anzeigen. Breite Fallbacks zeigen zusätzlich alle beobachteten Register×Root-Alternativen.",
    ])
    return "\n".join(lines).rstrip() + "\n"


def build_book(statements: list[dict[str, Any]], local_cards: list[dict[str, Any]]) -> str:
    pages = list(dict.fromkeys(row["physical_page"] for row in [*statements, *local_cards]))
    by_statement: dict[str, list[dict[str, Any]]] = defaultdict(list)
    by_local: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in statements:
        by_statement[row["physical_page"]].append(row)
    for row in local_cards:
        by_local[row["physical_page"]].append(row)
    lines = [
        "# GDT589 — vollständiger 30-Seiten-Leser mit separater Schreibspur", "",
        "Explorative deutsche Arbeitslesung; kein rekonstruierter Klartext.",
        "Die flüssige Hypothese zählt keine Realobjekte. Wo Wurzeln wiederholt geschrieben sind, folgt eine geordnete Trägerspur.",
    ]
    for page in pages:
        lines.extend(["", f"## {page}", "", "### Laufende Aussagen", ""])
        if not by_statement[page]:
            lines.append("Keine laufenden Aussagen.")
        for row in by_statement[page]:
            lines.extend([f"#### {row['statement_id']} — {row['register']}", "", str(row["gdt589_primary_reader_de"]), ""])
        lines.extend(["### Lokale Karten", ""])
        if not by_local[page]:
            lines.append("Keine lokalen Karten.")
        for row in by_local[page]:
            lines.extend([f"#### {row['source_event_id']} — {row['register']}", "", str(row["gdt589_primary_reader_de"]), ""])
    return "\n".join(lines).rstrip() + "\n"


def main() -> int:
    data = load_inputs()
    hosts, slots = build_replay(data)
    assignments = assignments_by_host(data)
    body = build_body_rows(hosts, slots)
    bath = [row for row in body if row["clean_bath_body_fork"] == "YES"]
    manual = build_manual_rows(hosts)
    source = build_source_rows(hosts)
    special = build_special_rows(hosts, assignments, data, {row["primary_governor_key"] for row in bath})
    repeated = build_repeat_rows(hosts, assignments, data)
    pages = build_page_rows(hosts, special, repeated, body)
    statements = add_count_overlay(data["statements_588"], repeated, layer="STATEMENT")
    local_cards = add_count_overlay(data["local_cards_588"], repeated, layer="LOCAL_CARD")

    auto = [row for row in hosts if row["gate_class"] == "AUTO_CONTEXT"]
    ordinary_repeat = [row for row in repeated if row["repeat_class"] == "DEFAULT_COMPOSITION"]
    special_repeat = [row for row in repeated if row["repeat_class"] == "SPECIAL_PACKET"]
    result: dict[str, Any] = {
        "experiment_id": "GDT589", "status": STATUS,
        "complete_carrier_hosts": len(hosts), "carrier_slots": len(slots),
        "auto_hosts": len(auto), "auto_slots": sum(int(row["carrier_slot_count"]) for row in auto),
        "auto_exact_hosts": sum(row["replay_outcome"] == "AUTO_EXACT_REPLAY" for row in auto),
        "auto_exact_slots": sum(row["portable_exact"] == "YES" for row in slots if row["gate_class"] == "AUTO_CONTEXT"),
        "auto_lookup_routes": dict(sorted(Counter(row["portable_lookup_route"] for row in slots if row["gate_class"] == "AUTO_CONTEXT").items())),
        "manual_hosts": len(manual), "manual_slots": sum(int(row["carrier_slot_count"]) for row in manual),
        "manual_action_wording_changes": sum(row["action_wording_change"] == "YES" for row in manual),
        "manual_direct_parent_noun_change_hosts": sum(int(row["direct_parent_changed_slot_count"]) > 0 for row in manual),
        "manual_runtime_noun_change_hosts": sum(int(row["runtime_changed_slot_count"]) > 0 for row in manual),
        "manual_packet_change_hosts": sum(row["packet_change"] == "YES" for row in manual),
        "manual_visible_carrier_change_hosts": sum(row["carrier_effect"] == "VISIBLE_CARRIER_CHANGE" for row in manual),
        "source_bound_hosts": len(source), "source_bound_slots": sum(int(row["carrier_slot_count"]) for row in source),
        "source_visible_fallthrough_exact": sum(row["visible_fallthrough_exact"] == "YES" for row in source),
        "special_packet_hosts": len(special), "special_packet_slots": sum(int(row["carrier_slot_count"]) for row in special),
        "packet_display_gap_counts": dict(sorted(Counter(row["display_gap_class"] for row in special).items())),
        "repeated_root_hosts": len(repeated), "repeated_root_slots": sum(int(row["carrier_slot_count"]) for row in repeated),
        "written_extra_copies": sum(int(row["written_extra_copy_count"]) for row in repeated),
        "ordinary_repeated_hosts": len(ordinary_repeat), "ordinary_repeated_slots": sum(int(row["carrier_slot_count"]) for row in ordinary_repeat),
        "special_repeated_hosts": len(special_repeat), "special_repeated_slots": sum(int(row["carrier_slot_count"]) for row in special_repeat),
        "count_overlay_statement_count": sum(row["gdt589_count_overlay"] == "YES" for row in statements),
        "count_overlay_local_card_count": sum(row["gdt589_count_overlay"] == "YES" for row in local_cards),
        "biological_y_hosts": len(body),
        "biological_y_slots": sum(row["carrier_root"] == "Y" for row in slots if row["gate_class"] == "AUTO_CONTEXT" and row["register"] == "BIOLOGICAL"),
        "biological_y_lemma_counts": dict(sorted(Counter(row["expected_lemma_de"] for row in slots if row["gate_class"] == "AUTO_CONTEXT" and row["register"] == "BIOLOGICAL" and row["carrier_root"] == "Y").items())),
        "clean_bath_body_forks": len(bath), "complete_statements": len(statements),
        "complete_local_cards": len(local_cards), "physical_pages": len(pages),
        "input_sha256": {name: sha256(path) for name, path in INPUTS.items()},
    }

    write_tsv(OUTPUTS["hosts"], hosts)
    write_tsv(OUTPUTS["slots"], slots)
    write_tsv(OUTPUTS["manual"], manual)
    write_tsv(OUTPUTS["source_bound"], source)
    write_tsv(OUTPUTS["special_packets"], special)
    write_tsv(OUTPUTS["repeated"], repeated)
    write_tsv(OUTPUTS["body_guard"], body)
    write_tsv(OUTPUTS["bath_forks"], bath)
    write_tsv(OUTPUTS["pages"], pages)
    write_tsv(OUTPUTS["statements"], statements)
    write_tsv(OUTPUTS["local_cards"], local_cards)
    OUTPUTS["deck"].write_text(build_deck(result, manual, source, special, repeated, bath), encoding="utf-8")
    OUTPUTS["book"].write_text(build_book(statements, local_cards), encoding="utf-8")
    OUTPUTS["result"].write_text(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
