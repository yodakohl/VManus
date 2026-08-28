#!/usr/bin/env python3
"""Build GDT594's occurrence-level completion of the 49 Y bath candidates."""

from __future__ import annotations

import csv
import hashlib
import io
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.vmanus_experiment import GuardedTSV  # noqa: E402


EXP = ROOT / "experiments/yolo/gdt594_gdt569_y_bath_occurrence_completion"
ART = EXP / "artifacts"
BATH_PAGES = frozenset({"f75r", "f77r", "f81r", "f81v", "f82r", "f83r"})
STATUS = (
    "PASS_49_Y_OCCURRENCE_COMPLETIONS__17_LOCAL_STATION__2_LOCAL_FLOW__"
    "1_LOCAL_BODY__29_RESET_BODY_FIRST__20_ANAPHORIC__29_DEFINITE__"
    "254_OBJECTS__49_STATEMENTS_CHANGED__44_COLD_DEFAULTS_REMAIN"
)

INPUTS = {
    "gdt593_actions": ROOT / "experiments/yolo/gdt593_gdt569_bath_candidate_promotion/artifacts/gdt593_254_ain_or_completed_bath_actions.tsv",
    "gdt593_statements": ROOT / "experiments/yolo/gdt593_gdt569_bath_candidate_promotion/artifacts/gdt593_793_ain_or_completed_statement_reader.tsv",
    "gdt416_clauses": ROOT / "experiments/yolo/gdt416_owner_local_imperative_sentence_compiler/artifacts/gdt416_4576_imperative_clauses.tsv",
    "gdt515_events": ROOT / "experiments/yolo/gdt515_second_random_four_page_full_admission/artifacts/gdt515_5122_running_event_edition.tsv",
    "gdt559_transitions": ROOT / "experiments/yolo/gdt559_argument_carrier_substitution_grammar/artifacts/gdt559_341_left_controlled_successor_transitions.tsv",
    "gdt569_states": ROOT / "experiments/yolo/gdt569_four_context_carry_voice_frames/artifacts/gdt569_1656_context_voice_state_clauses.tsv",
    "gdt581_aliases": ROOT / "experiments/yolo/gdt581_grammar_content_boundary_audit/artifacts/gdt581_4026_inherited_alias_edges.tsv",
    "gdt581_slots": ROOT / "experiments/yolo/gdt581_grammar_content_boundary_audit/artifacts/gdt581_15889_complete_slot_ledger.tsv",
    "gdt582_defaults": ROOT / "experiments/yolo/gdt582_concrete_stem_default_fill/artifacts/gdt582_15889_complete_default_ledger.tsv",
    "gdt584_hosts": ROOT / "experiments/yolo/gdt584_statement_collocation_polish/artifacts/gdt584_statement_wide_host_phrases.tsv",
    "gdt590_slots": ROOT / "experiments/yolo/gdt590_focused_bath_body_station_adjudication/artifacts/gdt590_1243_adjudicated_slot_replay.tsv",
    "lines": ROOT / "transcription/voynich_zl3b_lines.tsv",
}

OUTPUTS = {
    "candidates": ART / "gdt594_49_y_occurrence_completions.tsv",
    "actions": ART / "gdt594_254_y_completed_bath_actions.tsv",
    "changed_statements": ART / "gdt594_49_y_completed_statements.tsv",
    "statements": ART / "gdt594_793_y_completed_statement_reader.tsv",
    "pages": ART / "gdt594_6_page_profiles.tsv",
    "boundary_cases": ART / "gdt594_2_post_donor_reader_resets.tsv",
    "scope_conflicts": ART / "gdt594_3_host_atom_scope_conflicts.tsv",
    "reader": ART / "GDT594_Y_COMPLETED_BATH_READER.md",
    "result": ART / "gdt594_result.json",
    "validation": ART / "gdt594_validation.json",
}

MANUAL_TWO_WAY = frozenset({
    "G407-E1584", "G407-E1702", "G407-E1776", "G407-E1814",
    "G407-E2788", "G407-E3049", "G407-E3399", "G407-E3556",
    "G407-E3570", "G407-E3673", "G407-E3768",
})
MANUAL_FLOW_OPERATIONAL = frozenset({"G407-E1590", "G407-E2869"})
MANUAL_FRAGMENTED_CONTROL = frozenset({"G407-E3426"})


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def guarded_rows(path: Path, *, selector: str) -> list[dict[str, str]]:
    return list(
        GuardedTSV(
            path,
            selector_column=selector,
            allowed_values=BATH_PAGES,
            forbidden_prefixes=("f84",),
            forbidden_action="skip",
        )
    )


def read_derived_reader(path: Path) -> list[dict[str, str]]:
    """Read a sealed derived reader after rejecting any forbidden page row."""
    with path.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle, delimiter="\t"))
    if any(row["physical_page"].lower().startswith("f84") for row in rows):
        raise RuntimeError("derived GDT593 reader unexpectedly contains f84/f84r")
    return rows


def split_pipe(value: str) -> list[str]:
    return [part for part in value.split("|") if part and part != "NONE"]


def numbered(identifier: str, marker: str) -> int:
    match = re.search(rf"-{re.escape(marker)}(\d+)$", identifier)
    if not match:
        raise RuntimeError(f"invalid {marker} identifier: {identifier}")
    return int(match.group(1))


def locus_line(locus: str) -> int:
    match = re.search(r"\.(\d+)$", locus)
    if not match:
        raise RuntimeError(f"invalid locus: {locus}")
    return int(match.group(1))


def atom_coordinate(key: str) -> tuple[int, int]:
    """Return written event/atom order from a slot or control governor key."""
    match = re.search(r"(G407-E\d+)@(\d+)", key)
    if not match:
        raise RuntimeError(f"key has no written atom coordinate: {key}")
    return numbered(match.group(1), "E"), int(match.group(2))


def tsv_bytes(rows: list[dict[str, Any]]) -> bytes:
    if not rows:
        raise RuntimeError("refusing to serialize empty TSV")
    stream = io.StringIO(newline="")
    fields = list(rows[0])
    writer = csv.DictWriter(
        stream, fieldnames=fields, delimiter="\t", lineterminator="\n"
    )
    writer.writeheader()
    for row in rows:
        writer.writerow({field: str(row.get(field, "")) for field in fields})
    return stream.getvalue().encode("utf-8")


def write_tsv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(tsv_bytes(rows))


def replace_nth(text: str, old: str, new: str, occurrence: int) -> str:
    starts = [match.start() for match in re.finditer(re.escape(old), text)]
    if occurrence < 1 or occurrence > len(starts):
        raise RuntimeError(
            f"cannot replace occurrence {occurrence}/{len(starts)} of {old!r}"
        )
    start = starts[occurrence - 1]
    return text[:start] + new + text[start + len(old):]


def load_inputs() -> dict[str, list[dict[str, str]]]:
    return {
        "gdt593_actions": guarded_rows(INPUTS["gdt593_actions"], selector="physical_page"),
        "gdt593_statements": read_derived_reader(INPUTS["gdt593_statements"]),
        "gdt416_clauses": guarded_rows(INPUTS["gdt416_clauses"], selector="physical_page"),
        "gdt515_events": guarded_rows(INPUTS["gdt515_events"], selector="physical_page"),
        "gdt559_transitions": guarded_rows(INPUTS["gdt559_transitions"], selector="physical_page"),
        "gdt569_states": guarded_rows(INPUTS["gdt569_states"], selector="physical_page"),
        "gdt581_aliases": guarded_rows(INPUTS["gdt581_aliases"], selector="physical_page"),
        "gdt581_slots": guarded_rows(INPUTS["gdt581_slots"], selector="physical_page"),
        "gdt582_defaults": guarded_rows(INPUTS["gdt582_defaults"], selector="physical_page"),
        "gdt584_hosts": guarded_rows(INPUTS["gdt584_hosts"], selector="physical_page"),
        "gdt590_slots": guarded_rows(INPUTS["gdt590_slots"], selector="physical_page"),
        "lines": guarded_rows(INPUTS["lines"], selector="page"),
    }


def paragraph_by_locus(lines: list[dict[str, str]]) -> dict[str, str]:
    result: dict[str, str] = {}
    material_by_page: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in lines:
        material_by_page[row["page"]].append(row)
    for page, material in material_by_page.items():
        paragraph = 0
        for row in sorted(material, key=lambda item: int(item["line_number"])):
            if row["paragraph_start"] == "1" or paragraph == 0:
                paragraph += 1
            result[row["locus"]] = f"{page}:P{paragraph}"
    return result


def reconstruct_context_witnesses(
    clauses: list[dict[str, str]], target_ids: set[str]
) -> dict[str, dict[str, str]]:
    """Replay the old same-page owner state without calling it object identity."""
    active: dict[tuple[str, str], dict[str, str]] = {}
    witnesses: dict[str, dict[str, str]] = {}
    for row in clauses:
        key = (row["physical_page"], row["owner_de"])
        explicit = split_pipe(row["explicit_argument_roots"])
        if explicit:
            active[key] = {
                "root": explicit[-1],
                "event_id": row["global_running_event_id"],
                "statement_id": row["global_statement_id"],
                "surface": row["surface"],
                "recipe": row["component_recipe"],
                "owner_de": row["owner_de"],
                "clause_de": row["imperative_clause_de"],
            }
        event_id = row["global_running_event_id"]
        if event_id not in target_ids:
            continue
        witness = active.get(key)
        if witness is None or witness["root"] != row["inherited_argument_root"]:
            raise RuntimeError(f"context witness mismatch at {event_id}")
        witnesses[event_id] = witness
    if set(witnesses) != target_ids:
        raise RuntimeError("context witness coverage drift")
    return witnesses


def contextual_class(lemma: str) -> str:
    normalized = lemma.casefold()
    if "strom" in normalized:
        return "FLOW"
    if "körper" in normalized or "koerper" in normalized:
        return "BODY"
    if "station" in normalized:
        return "STATION"
    if "portion" in normalized or "anteil" in normalized:
        return "PORTION"
    if "einheit" in normalized:
        return "BATH_UNIT"
    return "UNRESOLVED_CONTEXT_TYPE"


def manual_reader_disposition(event_id: str) -> tuple[str, str]:
    if event_id in MANUAL_TWO_WAY:
        return (
            "READABLE_TWO_WAY",
            "Arbeitsdefault lesbar; Körper/Station beziehungsweise der lokale Donor bleibt als echte Rivalenlesung sichtbar.",
        )
    if event_id in MANUAL_FLOW_OPERATIONAL:
        return (
            "FLOW_MUST_BE_READ_OPERATIONALLY",
            "Strom bedeutet hier den Durchfluss im Badbetrieb aufrechterhalten, nicht einen Strom als Badegut eintauchen.",
        )
    if event_id in MANUAL_FRAGMENTED_CONTROL:
        return (
            "SURROUNDING_CONTROL_PROSE_FRAGMENTED",
            "Die Körperklausel ist einfach; die wiederholten Arbeitsgangmarker machen den Gesamtpassus unabhängig vom Objekt abgehackt.",
        )
    return (
        "STRAIGHTFORWARD_WORKING_READING",
        "Der gewählte Vorkommensdefault liest sich im vollständigen Werkstattkontext unmittelbar brauchbar.",
    )


def build(inputs: dict[str, list[dict[str, str]]]) -> dict[str, Any]:
    source_actions = inputs["gdt593_actions"]
    source_statements = inputs["gdt593_statements"]
    if len(source_actions) != 254 or len(source_statements) != 793:
        raise RuntimeError("GDT593 population drift")

    candidate_sources = [
        row for row in source_actions
        if row["gdt569_parallel_relation"]
        == "GDT569_SPECIFIC_CANDIDATE_OVER_GENERIC_DEFAULT"
        and row["gdt569_inherited_argument_root"] == "Y"
        and row["gdt593_selection_route"] == "COLD_BATH_OBJECT_DEFAULT"
    ]
    if len(candidate_sources) != 49:
        raise RuntimeError(f"Y candidate population drift: {len(candidate_sources)}")
    target_ids = {row["source_event_id"] for row in candidate_sources}
    if len(target_ids) != 49:
        raise RuntimeError("Y candidate event IDs are not unique")
    witnesses = reconstruct_context_witnesses(inputs["gdt416_clauses"], target_ids)

    alias_by_event: dict[str, dict[str, str]] = {}
    for row in inputs["gdt581_aliases"]:
        if row["event_id"] in target_ids and row["alias_class"] == "OBJECT_ALIAS":
            if row["event_id"] in alias_by_event:
                raise RuntimeError(f"duplicate object alias at {row['event_id']}")
            alias_by_event[row["event_id"]] = row
    if set(alias_by_event) != target_ids:
        raise RuntimeError("GDT581 Y object-alias coverage drift")

    slots_by_event: dict[str, list[dict[str, str]]] = defaultdict(list)
    slots_by_id: dict[str, dict[str, str]] = {}
    for row in inputs["gdt581_slots"]:
        slots_by_event[row["source_event_or_card_id"]].append(row)
        slots_by_id[row["slot_id"]] = row
    defaults_by_slot = {row["slot_id"]: row for row in inputs["gdt582_defaults"]}
    refined_by_slot = {row["carrier_slot_id"]: row for row in inputs["gdt590_slots"]}
    events_by_id = {row["global_running_event_id"]: row for row in inputs["gdt515_events"]}
    states_by_id = {row["event_id"]: row for row in inputs["gdt569_states"]}
    transitions_by_event = {
        row["event_id"]: row for row in inputs["gdt559_transitions"]
    }
    paragraphs = paragraph_by_locus(inputs["lines"])

    hosts_by_statement: dict[str, list[dict[str, str]]] = defaultdict(list)
    host_by_governor: dict[tuple[str, str], dict[str, str]] = {}
    for row in inputs["gdt584_hosts"]:
        hosts_by_statement[row["statement_id"]].append(row)
        key = (row["statement_id"], row["primary_governor_key"])
        if key in host_by_governor:
            raise RuntimeError(f"duplicate GDT584 primary governor: {key}")
        host_by_governor[key] = row
    for rows in hosts_by_statement.values():
        rows.sort(key=lambda item: int(item["host_ordinal_in_statement"]))

    candidates: list[dict[str, Any]] = []
    candidate_by_event: dict[str, dict[str, Any]] = {}
    for source in sorted(candidate_sources, key=lambda row: int(row["bath_action_ordinal"])):
        event_id = source["source_event_id"]
        alias = alias_by_event[event_id]
        witness = witnesses[event_id]
        state = states_by_id.get(event_id)
        target_event = events_by_id[event_id]
        witness_event = events_by_id[witness["event_id"]]
        if state is None or state["argument_carry"] != "YES":
            raise RuntimeError(f"missing GDT569 carry state at {event_id}")
        if state["inherited_argument_root"] != "Y" or alias["inherited_root"] != "Y":
            raise RuntimeError(f"Y root mismatch at {event_id}")

        witness_slots = [
            row for row in slots_by_event[witness["event_id"]]
            if row["layer"] == "RUNNING_ATOM" and row["slot_value"] == "Y"
        ]
        if not witness_slots:
            raise RuntimeError(f"missing written Y witness at {event_id}")
        witness_slot = max(witness_slots, key=lambda row: int(row["slot_position"]))
        default = defaults_by_slot[witness_slot["slot_id"]]
        refinement = refined_by_slot.get(witness_slot["slot_id"])
        witness_lemma = (
            refinement["gdt590_lemma_de"]
            if refinement is not None else default["gdt582_concrete_default_de"]
        )
        witness_meaning_source = (
            "GDT590_EXACT_ACTION_CONDITIONED_WITNESS"
            if refinement is not None else "GDT582_EXACT_WRITTEN_SLOT_WITNESS"
        )
        witness_class = contextual_class(witness_lemma)

        target_host = host_by_governor.get(
            (source["statement_id"], source["primary_governor_key"])
        )
        if target_host is None:
            raise RuntimeError(f"missing target host at {event_id}")
        target_host_ordinal = int(target_host["host_ordinal_in_statement"])
        if target_host["statement_id"] != source["statement_id"]:
            raise RuntimeError(f"target host statement mismatch at {event_id}")

        semantic_boundary_hosts: list[dict[str, str]] = []
        atom_boundary_hosts: list[dict[str, str]] = []
        source_host_ordinal: int | None = None
        source_host_key = "NOT_APPLICABLE"
        source_atom_coordinate = "NOT_APPLICABLE"
        target_atom_coordinate = "NOT_APPLICABLE"
        scope_model_conflict = "NONE"
        if alias["lexical_source_kind"] == "SAME_STATEMENT_EVENT":
            if alias["lexical_source_event_id"] != witness["event_id"]:
                raise RuntimeError(f"canonical source/witness mismatch at {event_id}")
            canonical_source_event_id = alias["lexical_source_event_id"]
            canonical_source_slot_id = (
                f"RUNNING:{canonical_source_event_id}@{alias['lexical_source_atom_position']}"
            )
            canonical_source_slot = slots_by_id.get(canonical_source_slot_id)
            if canonical_source_slot is None:
                raise RuntimeError(f"canonical source slot missing at {event_id}")
            if canonical_source_slot_id != witness_slot["slot_id"]:
                raise RuntimeError(f"canonical source slot/witness mismatch at {event_id}")
            source_host_key = canonical_source_slot["primary_governor_key"]
            source_host = host_by_governor.get((source["statement_id"], source_host_key))
            if source_host is None:
                raise RuntimeError(f"canonical source host missing at {event_id}")
            if source_host["statement_id"] != source["statement_id"]:
                raise RuntimeError(f"canonical source not in target statement at {event_id}")
            source_host_ordinal = int(source_host["host_ordinal_in_statement"])
            if source_host_ordinal >= target_host_ordinal:
                raise RuntimeError(f"canonical source is not leftward at {event_id}")
            semantic_boundary_hosts = [
                row for row in hosts_by_statement[source["statement_id"]]
                if source_host_ordinal
                <= int(row["host_ordinal_in_statement"])
                < target_host_ordinal
                and row["paragraph_boundary"] != "NONE"
            ]
            source_coordinate = atom_coordinate(canonical_source_slot_id)
            target_coordinate = atom_coordinate(source["action_slot_id"])
            source_atom_coordinate = f"E{source_coordinate[0]}@{source_coordinate[1]}"
            target_atom_coordinate = f"E{target_coordinate[0]}@{target_coordinate[1]}"
            all_statement_boundaries = [
                row for row in hosts_by_statement[source["statement_id"]]
                if row["paragraph_boundary"] != "NONE"
            ]
            atom_boundary_hosts = [
                row for row in all_statement_boundaries
                if source_coordinate
                < atom_coordinate(row["primary_governor_key"])
                < target_coordinate
            ]
            if bool(semantic_boundary_hosts) != bool(atom_boundary_hosts):
                scope_model_conflict = (
                    "SEMANTIC_HOST_RESET_BUT_WRITTEN_Y_IS_AT_OR_AFTER_CUT__"
                    "ATOM_ORDER_AND_GDT559_SUCCESSOR_STATE_WIN"
                )
            if atom_boundary_hosts:
                scope_class = "SAME_STATEMENT_READER_RESET"
                reference_span = "SAME_STATEMENT_SOURCE_BEFORE_POST_DONOR_READER_RESET"
                reference_realization = "DEFINITE_BODY_AT_TARGET_AFTER_READER_RESET"
                source_disposition = "CANONICAL_SOURCE_RETAINED_AS_CONTEXT_NOT_OBJECT_IDENTITY"
            else:
                scope_class = "SAME_OBJECT_SCOPE"
                reference_span = "SAME_STATEMENT_VISIBLE_SOURCE_AFTER_LAST_WRITTEN_CUT"
                reference_realization = "ANAPHORIC_SAME_OBJECT_SCOPE"
                source_disposition = (
                    "CANONICAL_WRITTEN_OBJECT_SOURCE_AFTER_ATOM_ORDER_CUT"
                    if scope_model_conflict != "NONE"
                    else "CANONICAL_WRITTEN_OBJECT_SOURCE"
                )
        elif alias["lexical_source_kind"] == "OWNER_DEFAULT":
            canonical_source_event_id = "OWNER"
            canonical_source_slot_id = alias["lexical_source_key"]
            scope_class = "OWNER_DEFAULT_RESET"
            reference_span = "OWNER_DEFAULT_AFTER_STATEMENT_RESET"
            reference_realization = "DEFINITE_BODY_AT_TARGET_AFTER_STATEMENT_RESET"
            source_disposition = "CONTEXT_WITNESS_NOT_OBJECT_SOURCE"
        else:
            raise RuntimeError(f"unexpected alias kind at {event_id}")

        if scope_class == "SAME_OBJECT_SCOPE":
            if witness_class == "STATION":
                object_class = "STATION"
                object_lemma = "Stationsansatz"
                object_form = "denselben Stationsansatz"
                selection_route = "GDT569_Y_LOCAL_STATION_DONOR"
            elif witness_class == "FLOW":
                object_class = "FLOW"
                object_lemma = "Strom"
                object_form = "denselben Strom"
                selection_route = "GDT569_Y_LOCAL_FLOW_DONOR"
            elif witness_class == "BODY":
                object_class = "BODY"
                object_lemma = "Körper"
                object_form = "denselben Körper"
                selection_route = "GDT569_Y_LOCAL_BODY_DONOR"
            else:
                raise RuntimeError(
                    f"local Y donor is neither station, flow, nor body at {event_id}: "
                    f"{witness_lemma!r}"
                )
        else:
            object_class = "BODY"
            object_lemma = "Körper"
            object_form = "den Körper"
            selection_route = "GDT569_Y_RESET_BODY_FIRST"

        old_clause = source["gdt593_completed_clause_de"]
        if source["gdt593_object_form_de"] != "das zu badende Gut":
            raise RuntimeError(f"candidate no longer has neutral Badegut at {event_id}")
        if object_class == "FLOW":
            new_clause = old_clause.replace(
                "das zu badende Gut im Bad", "denselben Strom im Badbetrieb", 1
            )
        else:
            new_clause = old_clause.replace("das zu badende Gut", object_form, 1)
        body_clause = old_clause.replace("das zu badende Gut", "den Körper", 1)
        station_clause = old_clause.replace("das zu badende Gut", "den Stationsansatz", 1)
        flow_clause = old_clause.replace(
            "das zu badende Gut im Bad", "den Strom im Badbetrieb", 1
        )

        event_distance = numbered(event_id, "E") - numbered(witness["event_id"], "E")
        statement_distance = numbered(source["statement_id"], "S") - numbered(witness["statement_id"], "S")
        if event_distance < 1 or statement_distance < 0:
            raise RuntimeError(f"non-prior context witness at {event_id}")
        same_paragraph = paragraphs[witness_event["locus"]] == paragraphs[target_event["locus"]]
        semantic_boundary_keys = "|".join(
            row["primary_governor_key"] for row in semantic_boundary_hosts
        ) or "NONE"
        atom_boundary_keys = "|".join(
            row["primary_governor_key"] for row in atom_boundary_hosts
        ) or "NONE"
        atom_boundary_phrases = "|".join(
            row["gdt584_reader_clause_de"] for row in atom_boundary_hosts
        ) or "NONE"
        if scope_model_conflict != "NONE":
            transition = transitions_by_event.get(witness["event_id"])
            if transition is None:
                raise RuntimeError(f"missing GDT559 conflict transition at {event_id}")
            if (
                transition["last_argument"] != "Y"
                or transition["successor_outcome"]
                != "NEXT_INHERITS_CURRENT_ARGUMENT"
            ):
                raise RuntimeError(f"GDT559 conflict transition drift at {event_id}")
            gdt559_transition_event_id = transition["event_id"]
            gdt559_transition_next_event_id = transition["next_event_id"]
            gdt559_transition_outcome = transition["successor_outcome"]
            gdt559_transition_reading_de = transition["transition_reading_de"]
        else:
            gdt559_transition_event_id = "NOT_APPLICABLE"
            gdt559_transition_next_event_id = "NOT_APPLICABLE"
            gdt559_transition_outcome = "NOT_APPLICABLE"
            gdt559_transition_reading_de = "NOT_APPLICABLE"

        manual_disposition, manual_note = manual_reader_disposition(event_id)
        row = {
            "completion_ordinal": len(candidates) + 1,
            "bath_action_ordinal": source["bath_action_ordinal"],
            "action_slot_id": source["action_slot_id"],
            "target_event_id": event_id,
            "target_statement_id": source["statement_id"],
            "physical_page": source["physical_page"],
            "target_locus": source["locus"],
            "target_paragraph_key": paragraphs[target_event["locus"]],
            "target_primary_governor_key": source["primary_governor_key"],
            "target_host_ordinal_in_statement": target_host_ordinal,
            "target_surface": source["surface"],
            "target_recipe": source["component_recipe"],
            "gdt593_previous_route": source["gdt593_selection_route"],
            "gdt593_previous_class": source["gdt593_object_class"],
            "gdt593_previous_clause_de": old_clause,
            "gdt569_state_edition_ordinal": state["state_edition_ordinal"],
            "gdt569_argument_source_type": state["argument_source_type"],
            "gdt569_inherited_argument_root": state["inherited_argument_root"],
            "gdt569_explicit_argument_phrase_de": state["explicit_argument_phrase_de"],
            "gdt569_carried_argument_phrase_de": state["carried_argument_phrase_de"],
            "retained_gdt569_context_clause_de": state["context_voice_working_clause_de"],
            "gdt581_alias_id": alias["alias_id"],
            "gdt581_lexical_source_kind": alias["lexical_source_kind"],
            "gdt581_lexical_source_key": alias["lexical_source_key"],
            "canonical_source_event_id": canonical_source_event_id,
            "canonical_source_slot_or_key": canonical_source_slot_id,
            "canonical_source_primary_governor_key": source_host_key,
            "canonical_source_host_ordinal_in_statement": (
                source_host_ordinal if source_host_ordinal is not None else "NOT_APPLICABLE"
            ),
            "context_witness_event_id": witness["event_id"],
            "context_witness_statement_id": witness["statement_id"],
            "context_witness_locus": witness_event["locus"],
            "context_witness_paragraph_key": paragraphs[witness_event["locus"]],
            "context_witness_slot_id": witness_slot["slot_id"],
            "context_witness_primary_governor_key": witness_slot["primary_governor_key"],
            "context_witness_surface": witness["surface"],
            "context_witness_recipe": witness["recipe"],
            "context_witness_lemma_de": witness_lemma,
            "context_witness_class": witness_class,
            "context_witness_meaning_source": witness_meaning_source,
            "context_witness_event_distance": event_distance,
            "context_witness_statement_distance": statement_distance,
            "context_witness_line_distance": locus_line(target_event["locus"]) - locus_line(witness_event["locus"]),
            "same_physical_paragraph": "YES" if same_paragraph else "NO",
            "source_written_atom_coordinate": source_atom_coordinate,
            "target_written_atom_coordinate": target_atom_coordinate,
            "semantic_host_reset_count": len(semantic_boundary_hosts),
            "semantic_host_reset_keys": semantic_boundary_keys,
            "intervening_reader_reset_count": len(atom_boundary_hosts),
            "intervening_reader_reset_host_keys": atom_boundary_keys,
            "intervening_reader_reset_phrases_de": atom_boundary_phrases,
            "scope_model_conflict": scope_model_conflict,
            "gdt559_transition_event_id": gdt559_transition_event_id,
            "gdt559_transition_next_event_id": gdt559_transition_next_event_id,
            "gdt559_transition_outcome": gdt559_transition_outcome,
            "gdt559_transition_reading_de": gdt559_transition_reading_de,
            "scope_class": scope_class,
            "reference_span": reference_span,
            "reference_realization": reference_realization,
            "source_disposition": source_disposition,
            "gdt594_selection_route": selection_route,
            "gdt594_object_class": object_class,
            "gdt594_object_lemma_de": object_lemma,
            "gdt594_object_form_de": object_form,
            "gdt594_completed_clause_de": new_clause,
            "retained_gdt593_badegut_clause_de": old_clause,
            "retained_body_alternative_de": (
                "SELECTED_PRIMARY" if object_class == "BODY" else body_clause
            ),
            "retained_station_alternative_de": (
                "SELECTED_PRIMARY" if object_class == "STATION" else station_clause
            ),
            "retained_flow_alternative_de": (
                "SELECTED_PRIMARY" if object_class == "FLOW" else flow_clause
            ),
            "retained_semantic_host_scope_alternative_de": (
                body_clause if scope_model_conflict != "NONE" else "NOT_APPLICABLE"
            ),
            "reader_clause_occurrence_index": "PENDING",
            "manual_reader_disposition": manual_disposition,
            "manual_reader_note_de": manual_note,
            "completion_status": "Y_OCCURRENCE_DEFAULT_COMPLETED",
            "guard": (
                "OCCURRENCE_LEVEL_Y_ONLY__LOCAL_DONOR_OR_RESET_TARGET_DEFAULT__"
                "GDT569_AND_BADEGUT_RIVALS_RETAINED__NO_GLOBAL_Y_LEXEME_OR_NEW_PAGE"
            ),
        }
        candidates.append(row)
        candidate_by_event[event_id] = row

    actions: list[dict[str, Any]] = []
    for source in source_actions:
        candidate = candidate_by_event.get(source["source_event_id"])
        if candidate is None:
            final_class = source["gdt593_object_class"]
            final_lemma = source["gdt593_object_lemma_de"]
            final_form = source["gdt593_object_form_de"]
            final_clause = source["gdt593_completed_clause_de"]
            status = "RETAINED_GDT593_OBJECT"
            route = source["gdt593_selection_route"]
            scope = selected_root = source_kind = source_event = "NOT_APPLICABLE"
            final_relation = source["gdt593_parallel_relation"]
        else:
            final_class = candidate["gdt594_object_class"]
            final_lemma = candidate["gdt594_object_lemma_de"]
            final_form = candidate["gdt594_object_form_de"]
            final_clause = candidate["gdt594_completed_clause_de"]
            status = "COMPLETED_Y_OCCURRENCE_DEFAULT"
            route = candidate["gdt594_selection_route"]
            scope = candidate["scope_class"]
            selected_root = "Y"
            source_kind = candidate["gdt581_lexical_source_kind"]
            source_event = candidate["canonical_source_event_id"]
            final_relation = "GDT569_Y_CONTEXT_RESOLVED_AT_OCCURRENCE_LEVEL"
        actions.append(
            {
                **source,
                "gdt594_object_status": status,
                "gdt594_selected_root": selected_root,
                "gdt594_lexical_source_kind": source_kind,
                "gdt594_canonical_source_event_id": source_event,
                "gdt594_scope_class": scope,
                "gdt594_selection_route": route,
                "gdt594_object_class": final_class,
                "gdt594_object_lemma_de": final_lemma,
                "gdt594_object_form_de": final_form,
                "gdt594_parallel_relation": final_relation,
                "gdt594_completed_clause_de": final_clause,
                "gdt594_clause_changed": "YES" if candidate else "NO",
                "gdt594_guard": (
                    "GDT593_OBJECT_RETAINED_OR_EXACT_Y_OCCURRENCE_COMPLETED__"
                    "SURFACE_SLOT_ROOT_AND_SEGMENTATION_UNCHANGED"
                ),
            }
        )

    source_actions_by_statement: dict[str, list[dict[str, str]]] = defaultdict(list)
    final_actions_by_statement: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for source, final in zip(source_actions, actions):
        source_actions_by_statement[source["statement_id"]].append(source)
        final_actions_by_statement[final["statement_id"]].append(final)
    for rows in source_actions_by_statement.values():
        rows.sort(key=lambda row: (int(row["host_ordinal_in_statement"]), int(row["bath_action_ordinal"])))
    for rows in final_actions_by_statement.values():
        rows.sort(key=lambda row: (int(row["host_ordinal_in_statement"]), int(row["bath_action_ordinal"])))

    candidates_by_statement: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in candidates:
        candidates_by_statement[row["target_statement_id"]].append(row)
    if any(len(rows) != 1 for rows in candidates_by_statement.values()):
        raise RuntimeError("GDT594 expects exactly one Y target in each changed statement")

    statements: list[dict[str, Any]] = []
    changed_statements: list[dict[str, Any]] = []
    for source in source_statements:
        statement_id = source["statement_id"]
        members = candidates_by_statement.get(statement_id, [])
        final_text = source["gdt593_primary_reader_de"]
        changed_slots = "NONE"
        for candidate in members:
            source_action = next(
                row for row in source_actions_by_statement[statement_id]
                if row["source_event_id"] == candidate["target_event_id"]
            )
            occurrence = sum(
                row["gdt593_completed_clause_de"]
                == source_action["gdt593_completed_clause_de"]
                and (
                    int(row["host_ordinal_in_statement"]),
                    int(row["bath_action_ordinal"]),
                )
                <= (
                    int(source_action["host_ordinal_in_statement"]),
                    int(source_action["bath_action_ordinal"]),
                )
                for row in source_actions_by_statement[statement_id]
            )
            final_text = replace_nth(
                final_text,
                source_action["gdt593_completed_clause_de"],
                candidate["gdt594_completed_clause_de"],
                occurrence,
            )
            candidate["reader_clause_occurrence_index"] = occurrence
            changed_slots = candidate["action_slot_id"]
        bath_actions = final_actions_by_statement.get(statement_id, [])
        object_sequence = (
            "|".join(row["gdt594_object_lemma_de"] for row in bath_actions)
            if bath_actions else "NONE"
        )
        row = {
            **source,
            "gdt594_y_completion_count": len(members),
            "gdt594_completed_action_slot_ids": changed_slots,
            "gdt594_bath_object_sequence": object_sequence,
            "gdt594_primary_reader_de": final_text,
            "gdt594_reader_changed": "YES" if members else "NO",
            "gdt594_guard": (
                "ONLY_49_Y_OBJECT_CLAUSES_CHANGED__"
                "744_GDT593_STATEMENTS_BYTE_RETAINED"
            ),
        }
        statements.append(row)
        if members:
            changed_statements.append(row)

    pages: list[dict[str, Any]] = []
    for page in sorted(BATH_PAGES):
        members = [row for row in actions if row["physical_page"] == page]
        changed = [row for row in members if row["gdt594_clause_changed"] == "YES"]
        cards = [row for row in candidates if row["physical_page"] == page]
        pages.append(
            {
                "page_ordinal": len(pages) + 1,
                "physical_page": page,
                "bath_action_count": len(members),
                "y_completion_count": len(changed),
                "scope_profile": json.dumps(
                    dict(sorted(Counter(row["scope_class"] for row in cards).items())),
                    ensure_ascii=False,
                    sort_keys=True,
                ),
                "completion_object_profile": json.dumps(
                    dict(sorted(Counter(row["gdt594_object_class"] for row in cards).items())),
                    ensure_ascii=False,
                    sort_keys=True,
                ),
                "final_object_profile": json.dumps(
                    dict(sorted(Counter(row["gdt594_object_class"] for row in members).items())),
                    ensure_ascii=False,
                    sort_keys=True,
                ),
                "guard": "SIX_ALREADY_ADMITTED_BATH_PAGES_ONLY__NO_F84",
            }
        )

    boundary_cases = [
        row for row in candidates if row["scope_class"] == "SAME_STATEMENT_READER_RESET"
    ]
    scope_conflicts = [
        row for row in candidates if row["scope_model_conflict"] != "NONE"
    ]
    result = {
        "experiment_id": "GDT594",
        "status": STATUS,
        "bath_action_count": len(actions),
        "statement_count": len(statements),
        "candidate_count": len(candidates),
        "changed_statement_count": len(changed_statements),
        "retained_statement_count": len(statements) - len(changed_statements),
        "source_kind_profile": dict(sorted(Counter(row["gdt581_lexical_source_kind"] for row in candidates).items())),
        "scope_profile": dict(sorted(Counter(row["scope_class"] for row in candidates).items())),
        "reference_realization_profile": dict(sorted(Counter(row["reference_realization"] for row in candidates).items())),
        "completion_object_profile": dict(sorted(Counter(row["gdt594_object_class"] for row in candidates).items())),
        "manual_reader_profile": dict(sorted(Counter(row["manual_reader_disposition"] for row in candidates).items())),
        "final_object_profile": dict(sorted(Counter(row["gdt594_object_class"] for row in actions).items())),
        "remaining_cold_bath_object_default_count": sum(
            row["gdt594_selection_route"] == "COLD_BATH_OBJECT_DEFAULT" for row in actions
        ),
        "remaining_gdt569_specific_candidate_count": sum(
            row["gdt569_parallel_relation"]
            == "GDT569_SPECIFIC_CANDIDATE_OVER_GENERIC_DEFAULT"
            and row["gdt594_selection_route"] == "COLD_BATH_OBJECT_DEFAULT"
            for row in actions
        ),
        "same_statement_reader_reset_event_ids": [row["target_event_id"] for row in boundary_cases],
        "semantic_host_reset_event_ids": [
            row["target_event_id"] for row in candidates
            if int(row["semantic_host_reset_count"]) > 0
        ],
        "host_atom_scope_conflict_event_ids": [
            row["target_event_id"] for row in scope_conflicts
        ],
        "physical_paragraph_crossing_event_ids": [
            row["target_event_id"] for row in candidates
            if row["same_physical_paragraph"] == "NO"
        ],
        "context_witness_event_distance_min": min(int(row["context_witness_event_distance"]) for row in candidates),
        "context_witness_event_distance_max": max(int(row["context_witness_event_distance"]) for row in candidates),
        "input_sha256": {name: sha256(path) for name, path in INPUTS.items()},
        "working_rule_de": (
            "Die 49 verbliebenen Y-Badegut-Kandidaten werden ausschließlich auf "
            "Vorkommensebene konkretisiert. Innerhalb desselben sichtbaren Objektsegments "
            "übernimmt das Ziel den exakten Donortyp: siebzehnmal Stationsansatz, "
            "zweimal Strom und einmal Körper. Ein Reset zählt nur, wenn sein geschriebenes "
            "Kontrollatom nach der Y-Quelle steht; dadurch bleiben E1658, E3426 und E3673 "
            "lokal, obwohl die ältere semantische Hostreihenfolge eine Grenze dazwischen "
            "anzeigt. Hinter zwei echten post-donor Readerresets oder 27 Satzresets wird Y "
            "am blockerfreien SH-Badziel körpernah als Körper-first neu gesetzt. "
            "Die GDT569-Kontextfassung, die Stationsalternative und der neutrale "
            "Badegut-Satz bleiben sichtbar. Y wird nicht global zu Körper, Station oder Strom."
        ),
    }
    return {
        "candidates": candidates,
        "actions": actions,
        "changed_statements": changed_statements,
        "statements": statements,
        "pages": pages,
        "boundary_cases": boundary_cases,
        "scope_conflicts": scope_conflicts,
        "result": result,
    }


def render_reader(built: dict[str, Any]) -> str:
    statements = {row["statement_id"]: row for row in built["statements"]}
    actions_by_statement: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in built["actions"]:
        actions_by_statement[row["statement_id"]].append(row)
    lines = [
        "# GDT594 — vorkommensweise vervollständigter Y-Badeobjekt-Leser",
        "",
        "Die 49 noch neutralen `Y`-Badegut-Stellen erhalten hier ausnahmslos einen "
        "konkreten Arbeitsdefault. Innerhalb desselben Objektsegments wird die sichtbare "
        "Quelle wiederaufgenommen: 17× **derselbe Stationsansatz**, 2× **derselbe Strom** "
        "und 1× **derselbe Körper**. Nach zwei echten post-donor Readerresets oder 27 "
        "Satzresets wird am blockerfreien SH-Badziel **der Körper** neu gesetzt. "
        "Geschriebene Atomfolge hat dabei Vorrang vor rückwärtsgerichteter semantischer "
        "Hostanbindung. Das ist eine Vorkommensregel, kein Wörterbucheintrag "
        "`Y = Körper`. Die alte GDT569-Kontextfassung, Station und Badegut bleiben als "
        "Rivalen in der vollständigen Kartentabelle erhalten.",
        "",
    ]
    for page in sorted(BATH_PAGES):
        lines.extend([f"## {page}", ""])
        statement_ids = list(
            dict.fromkeys(
                row["statement_id"]
                for row in built["actions"]
                if row["physical_page"] == page
            )
        )
        for statement_id in statement_ids:
            members = sorted(
                actions_by_statement[statement_id],
                key=lambda row: int(row["bath_action_ordinal"]),
            )
            trace = " → ".join(
                f"{row['source_event_id']}={row['gdt594_object_lemma_de']}"
                f"[{row['gdt594_selection_route']}]"
                for row in members
            )
            lines.extend(
                [
                    f"### {statement_id}",
                    "",
                    f"Objektspur: `{trace}`",
                    "",
                    statements[statement_id]["gdt594_primary_reader_de"],
                    "",
                ]
            )
    lines.extend(["## Die 49 konkreten Y-Karten", ""])
    for row in built["candidates"]:
        if row["scope_class"] == "SAME_OBJECT_SCOPE":
            provenance = (
                f"lokale Schriftquelle `{row['canonical_source_slot_or_key']}` "
                f"als {row['context_witness_lemma_de']}"
            )
            if row["scope_model_conflict"] != "NONE":
                provenance += "; Atomfolge schlägt die sichtbare Hostgrenzen-Alternative"
        elif row["scope_class"] == "SAME_STATEMENT_READER_RESET":
            provenance = (
                f"Schriftquelle `{row['canonical_source_slot_or_key']}`, aber Reset "
                f"`{row['intervening_reader_reset_host_keys']}`"
            )
        else:
            provenance = (
                f"Besitzer-Default; Kontextzeuge `{row['context_witness_slot_id']}`"
            )
        lines.append(
            f"- `{row['target_event_id']}`: **{row['gdt594_completed_clause_de']}**; "
            f"{provenance}; Badegut-Rivale: "
            f"*{row['retained_gdt593_badegut_clause_de']}*; "
            f"Lesestatus: `{row['manual_reader_disposition']}`."
        )
    lines.extend(
        [
            "",
            "## Verbleibende Reserve",
            "",
            "Nach diesem Pass sind alle 61 spezifischen GDT569-Kandidaten über dem "
            "neutralen Badegut konkretisiert. Übrig bleiben 44 kalte Defaults ohne "
            "solchen spezifischen Y/AIN/OR-Kontext: 17 AIIN-Füllspuren und 27 Fälle ohne "
            "spezifische getragene Wurzel. Diese Reserve braucht eine andere Bedeutungsquelle.",
            "",
        ]
    )
    return "\n".join(lines)


def write_built(built: dict[str, Any]) -> None:
    for name in (
        "candidates",
        "actions",
        "changed_statements",
        "statements",
        "pages",
        "boundary_cases",
        "scope_conflicts",
    ):
        write_tsv(OUTPUTS[name], built[name])
    OUTPUTS["reader"].write_text(render_reader(built), encoding="utf-8")
    OUTPUTS["result"].write_text(
        json.dumps(built["result"], ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
