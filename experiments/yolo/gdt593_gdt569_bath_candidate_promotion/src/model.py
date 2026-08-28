#!/usr/bin/env python3
"""Build GDT593's stable-root AIN/OR bath-object promotion layer."""

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


EXP = ROOT / "experiments/yolo/gdt593_gdt569_bath_candidate_promotion"
ART = EXP / "artifacts"
BATH_PAGES = frozenset({"f75r", "f77r", "f81r", "f81v", "f82r", "f83r"})
STATUS = (
    "PASS_12_STABLE_ROOT_PROMOTIONS__8_AIN_PORTION__4_OR_UNIT__"
    "5_ANAPHORIC_SAME_SCOPE__7_RESET_TYPE_DEFAULTS__"
    "254_OBJECTS__12_STATEMENTS_CHANGED__93_COLD_DEFAULTS_REMAIN"
)

INPUTS = {
    "gdt592_actions": ROOT / "experiments/yolo/gdt592_bath_object_completion/artifacts/gdt592_254_bath_action_objects.tsv",
    "gdt592_statements": ROOT / "experiments/yolo/gdt592_bath_object_completion/artifacts/gdt592_793_bath_object_statement_reader.tsv",
    "gdt416_clauses": ROOT / "experiments/yolo/gdt416_owner_local_imperative_sentence_compiler/artifacts/gdt416_4576_imperative_clauses.tsv",
    "gdt515_events": ROOT / "experiments/yolo/gdt515_second_random_four_page_full_admission/artifacts/gdt515_5122_running_event_edition.tsv",
    "gdt569_states": ROOT / "experiments/yolo/gdt569_four_context_carry_voice_frames/artifacts/gdt569_1656_context_voice_state_clauses.tsv",
    "gdt581_aliases": ROOT / "experiments/yolo/gdt581_grammar_content_boundary_audit/artifacts/gdt581_4026_inherited_alias_edges.tsv",
    "gdt581_slots": ROOT / "experiments/yolo/gdt581_grammar_content_boundary_audit/artifacts/gdt581_15889_complete_slot_ledger.tsv",
    "gdt582_defaults": ROOT / "experiments/yolo/gdt582_concrete_stem_default_fill/artifacts/gdt582_15889_complete_default_ledger.tsv",
    "gdt590_slots": ROOT / "experiments/yolo/gdt590_focused_bath_body_station_adjudication/artifacts/gdt590_1243_adjudicated_slot_replay.tsv",
    "lines": ROOT / "transcription/voynich_zl3b_lines.tsv",
}

OUTPUTS = {
    "promotions": ART / "gdt593_12_ain_or_stable_root_promotions.tsv",
    "actions": ART / "gdt593_254_ain_or_completed_bath_actions.tsv",
    "promoted_statements": ART / "gdt593_12_promoted_statements.tsv",
    "statements": ART / "gdt593_793_ain_or_completed_statement_reader.tsv",
    "pages": ART / "gdt593_6_page_profiles.tsv",
    "reader": ART / "GDT593_AIN_OR_COMPLETED_BATH_READER.md",
    "result": ART / "gdt593_result.json",
    "validation": ART / "gdt593_validation.json",
}

PROMOTION_BY_ROOT = {
    "AIN": {
        "class": "PORTION",
        "anaphoric_lemma": "Anwendungsportion",
        "target_lemma": "Anwendungsportion",
        "anaphoric_form": "dieselbe Anwendungsportion",
        "definite_form": "die Anwendungsportion",
        "route": "GDT569_AIN_PORTION_PROMOTION",
    },
    "OR": {
        "class": "BATH_UNIT",
        "anaphoric_lemma": "Stationseinheit",
        "target_lemma": "Badeinheit",
        "anaphoric_form": "dieselbe Stationseinheit",
        "definite_form": "die Badeinheit",
        "route": "GDT569_OR_UNIT_PROMOTION",
    },
}


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
    """Read GDT592's multiline derived reader after checking its page set."""
    with path.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle, delimiter="\t"))
    if any(row["physical_page"].lower().startswith("f84") for row in rows):
        raise RuntimeError("derived GDT592 reader unexpectedly contains f84/f84r")
    return rows


def split_pipe(value: str) -> list[str]:
    return [part for part in value.split("|") if part and part != "NONE"]


def event_number(event_id: str) -> int:
    match = re.search(r"-E(\d+)$", event_id)
    if not match:
        raise RuntimeError(f"invalid event id: {event_id}")
    return int(match.group(1))


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
        "gdt592_actions": guarded_rows(INPUTS["gdt592_actions"], selector="physical_page"),
        "gdt592_statements": read_derived_reader(INPUTS["gdt592_statements"]),
        "gdt416_clauses": guarded_rows(INPUTS["gdt416_clauses"], selector="physical_page"),
        "gdt515_events": guarded_rows(INPUTS["gdt515_events"], selector="physical_page"),
        "gdt569_states": guarded_rows(INPUTS["gdt569_states"], selector="physical_page"),
        "gdt581_aliases": guarded_rows(INPUTS["gdt581_aliases"], selector="physical_page"),
        "gdt581_slots": guarded_rows(INPUTS["gdt581_slots"], selector="physical_page"),
        "gdt582_defaults": guarded_rows(INPUTS["gdt582_defaults"], selector="physical_page"),
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
    """Recover the last written same-owner root; it is not always a legal donor."""
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


def build(inputs: dict[str, list[dict[str, str]]]) -> dict[str, Any]:
    source_actions = inputs["gdt592_actions"]
    source_statements = inputs["gdt592_statements"]
    if len(source_actions) != 254 or len(source_statements) != 793:
        raise RuntimeError("GDT592 population drift")

    candidate_sources = [
        row for row in source_actions
        if row["gdt569_parallel_relation"]
        == "GDT569_SPECIFIC_CANDIDATE_OVER_GENERIC_DEFAULT"
        and row["gdt569_inherited_argument_root"] in PROMOTION_BY_ROOT
    ]
    if len(candidate_sources) != 12:
        raise RuntimeError(f"AIN/OR candidate population drift: {len(candidate_sources)}")
    target_ids = {row["source_event_id"] for row in candidate_sources}
    witnesses = reconstruct_context_witnesses(inputs["gdt416_clauses"], target_ids)

    alias_by_event: dict[str, dict[str, str]] = {}
    for row in inputs["gdt581_aliases"]:
        if row["event_id"] in target_ids and row["alias_class"] == "OBJECT_ALIAS":
            if row["event_id"] in alias_by_event:
                raise RuntimeError(f"duplicate object alias at {row['event_id']}")
            alias_by_event[row["event_id"]] = row
    if set(alias_by_event) != target_ids:
        raise RuntimeError("GDT581 object-alias coverage drift")

    slots_by_event: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in inputs["gdt581_slots"]:
        slots_by_event[row["source_event_or_card_id"]].append(row)
    defaults_by_slot = {row["slot_id"]: row for row in inputs["gdt582_defaults"]}
    refined_by_slot = {row["carrier_slot_id"]: row for row in inputs["gdt590_slots"]}
    events_by_id = {row["global_running_event_id"]: row for row in inputs["gdt515_events"]}
    states_by_id = {row["event_id"]: row for row in inputs["gdt569_states"]}
    paragraphs = paragraph_by_locus(inputs["lines"])

    promotions: list[dict[str, Any]] = []
    promotion_by_event: dict[str, dict[str, Any]] = {}
    for source in sorted(candidate_sources, key=lambda row: int(row["bath_action_ordinal"])):
        event_id = source["source_event_id"]
        root = source["gdt569_inherited_argument_root"]
        promoted = PROMOTION_BY_ROOT[root]
        alias = alias_by_event[event_id]
        state = states_by_id.get(event_id)
        witness = witnesses[event_id]
        if alias["inherited_root"] != root or state is None:
            raise RuntimeError(f"parallel root mismatch at {event_id}")
        if state["inherited_argument_root"] != root or state["argument_carry"] != "YES":
            raise RuntimeError(f"GDT569 carry mismatch at {event_id}")

        witness_slots = [
            row for row in slots_by_event[witness["event_id"]]
            if row["layer"] == "RUNNING_ATOM" and row["slot_value"] == root
        ]
        if not witness_slots:
            raise RuntimeError(f"missing written root witness at {event_id}")
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

        if alias["lexical_source_kind"] == "SAME_STATEMENT_EVENT":
            if alias["lexical_source_event_id"] != witness["event_id"]:
                raise RuntimeError(f"canonical source/witness mismatch at {event_id}")
            canonical_source_event_id = alias["lexical_source_event_id"]
            canonical_source_slot_id = (
                f"RUNNING:{canonical_source_event_id}@{alias['lexical_source_atom_position']}"
            )
            if canonical_source_slot_id != witness_slot["slot_id"]:
                raise RuntimeError(f"canonical source slot mismatch at {event_id}")
            if source["reset_before"] == "NONE":
                reference_span = "SAME_STATEMENT_VISIBLE_SOURCE"
            else:
                reference_span = "SAME_STATEMENT_SOURCE_ACROSS_READER_RESET"
            source_disposition = "CANONICAL_WRITTEN_SOURCE"
        elif alias["lexical_source_kind"] == "OWNER_DEFAULT":
            canonical_source_event_id = "OWNER"
            canonical_source_slot_id = alias["lexical_source_key"]
            reference_span = "OWNER_DEFAULT_WITH_PRIOR_WRITTEN_CONTEXT_WITNESS"
            source_disposition = "CONTEXT_WITNESS_NOT_OBJECT_SOURCE"
        else:
            raise RuntimeError(f"unexpected alias kind at {event_id}")

        if reference_span == "SAME_STATEMENT_VISIBLE_SOURCE":
            object_lemma = promoted["anaphoric_lemma"]
            object_form = promoted["anaphoric_form"]
            reference_realization = "ANAPHORIC_SAME_OBJECT_SCOPE"
        else:
            object_lemma = promoted["target_lemma"]
            object_form = promoted["definite_form"]
            reference_realization = "DEFINITE_TARGET_TYPE_AFTER_RESET"

        witness_event = events_by_id[witness["event_id"]]
        target_event = events_by_id[event_id]
        distance = event_number(event_id) - event_number(witness["event_id"])
        if distance < 1:
            raise RuntimeError(f"non-prior context witness at {event_id}")
        same_paragraph = paragraphs[witness_event["locus"]] == paragraphs[target_event["locus"]]
        old_clause = source["gdt592_completed_clause_de"]
        if source["gdt592_object_form_de"] != "das zu badende Gut":
            raise RuntimeError(f"candidate no longer has neutral Badegut at {event_id}")
        new_clause = old_clause.replace(
            source["gdt592_object_form_de"], object_form, 1
        )
        if root == "OR":
            alternative_form = (
                "die Badeinheit"
                if object_lemma == "Stationseinheit" else "die Stationseinheit"
            )
            same_class_alternative = old_clause.replace(
                "das zu badende Gut", alternative_form, 1
            )
        else:
            same_class_alternative = "NOT_APPLICABLE"

        row = {
            "promotion_ordinal": len(promotions) + 1,
            "bath_action_ordinal": source["bath_action_ordinal"],
            "action_slot_id": source["action_slot_id"],
            "target_event_id": event_id,
            "target_statement_id": source["statement_id"],
            "physical_page": source["physical_page"],
            "target_locus": source["locus"],
            "target_paragraph_key": paragraphs[target_event["locus"]],
            "target_host_ordinal_in_statement": source["host_ordinal_in_statement"],
            "target_surface": source["surface"],
            "target_recipe": source["component_recipe"],
            "target_reset_before": source["reset_before"],
            "gdt592_previous_route": source["object_selection_route"],
            "gdt592_previous_class": source["gdt592_object_class"],
            "gdt592_previous_clause_de": old_clause,
            "gdt569_state_edition_ordinal": state["state_edition_ordinal"],
            "gdt569_argument_source_type": state["argument_source_type"],
            "gdt569_inherited_argument_root": root,
            "gdt569_explicit_argument_phrase_de": state["explicit_argument_phrase_de"],
            "gdt569_carried_argument_phrase_de": state["carried_argument_phrase_de"],
            "gdt581_alias_id": alias["alias_id"],
            "gdt581_lexical_source_kind": alias["lexical_source_kind"],
            "gdt581_lexical_source_key": alias["lexical_source_key"],
            "canonical_source_event_id": canonical_source_event_id,
            "canonical_source_slot_or_key": canonical_source_slot_id,
            "context_witness_event_id": witness["event_id"],
            "context_witness_statement_id": witness["statement_id"],
            "context_witness_locus": witness_event["locus"],
            "context_witness_paragraph_key": paragraphs[witness_event["locus"]],
            "context_witness_slot_id": witness_slot["slot_id"],
            "context_witness_primary_governor_key": witness_slot["primary_governor_key"],
            "context_witness_surface": witness["surface"],
            "context_witness_recipe": witness["recipe"],
            "context_witness_lemma_de": witness_lemma,
            "context_witness_meaning_source": witness_meaning_source,
            "context_witness_event_distance": distance,
            "context_witness_intervening_event_count": distance - 1,
            "same_physical_paragraph": "YES" if same_paragraph else "NO",
            "reference_span": reference_span,
            "reference_realization": reference_realization,
            "source_disposition": source_disposition,
            "gdt593_selection_route": promoted["route"],
            "gdt593_object_class": promoted["class"],
            "gdt593_object_lemma_de": object_lemma,
            "gdt593_object_form_de": object_form,
            "gdt593_completed_clause_de": new_clause,
            "retained_gdt592_badegut_clause_de": old_clause,
            "retained_same_class_alternative_de": same_class_alternative,
            "reader_clause_occurrence_index": "PENDING",
            "promotion_status": "STABLE_ROOT_TARGET_COMPLETION",
            "guard": (
                "OCCURRENCE_LEVEL_AIN_OR_ONLY__OWNER_DEFAULT_NOT_RELABELED_AS_DONOR__"
                "GDT592_RIVAL_RETAINED__NO_NEW_PAGE_ROOT_OR_SEGMENT"
            ),
        }
        promotions.append(row)
        promotion_by_event[event_id] = row

    actions: list[dict[str, Any]] = []
    for source in source_actions:
        promotion = promotion_by_event.get(source["source_event_id"])
        if promotion is None:
            final_class = source["gdt592_object_class"]
            final_lemma = source["gdt592_object_lemma_de"]
            final_form = source["gdt592_object_form_de"]
            final_clause = source["gdt592_completed_clause_de"]
            status = "RETAINED_GDT592_OBJECT"
            route = source["object_selection_route"]
            final_relation = source["gdt569_parallel_relation"]
            root = source_event = source_kind = "NOT_APPLICABLE"
        else:
            final_class = promotion["gdt593_object_class"]
            final_lemma = promotion["gdt593_object_lemma_de"]
            final_form = promotion["gdt593_object_form_de"]
            final_clause = promotion["gdt593_completed_clause_de"]
            status = "PROMOTED_STABLE_AIN_OR_ROOT"
            route = promotion["gdt593_selection_route"]
            final_relation = "GDT569_STABLE_ROOT_PROMOTED_TO_WORKING_OBJECT"
            root = promotion["gdt569_inherited_argument_root"]
            source_event = promotion["canonical_source_event_id"]
            source_kind = promotion["gdt581_lexical_source_kind"]
        actions.append(
            {
                **source,
                "gdt593_object_status": status,
                "gdt593_promoted_root": root,
                "gdt593_lexical_source_kind": source_kind,
                "gdt593_canonical_source_event_id": source_event,
                "gdt593_selection_route": route,
                "gdt593_object_class": final_class,
                "gdt593_object_lemma_de": final_lemma,
                "gdt593_object_form_de": final_form,
                "gdt593_parallel_relation": final_relation,
                "gdt593_completed_clause_de": final_clause,
                "gdt593_clause_changed": "YES" if promotion else "NO",
                "gdt593_guard": (
                    "GDT592_OBJECT_RETAINED_OR_EXACT_AIN_OR_CARD_PROMOTED__"
                    "SURFACE_SLOT_AND_SEGMENTATION_UNCHANGED"
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

    promotions_by_statement = {row["target_statement_id"]: row for row in promotions}
    statements: list[dict[str, Any]] = []
    promoted_statements: list[dict[str, Any]] = []
    for source in source_statements:
        statement_id = source["statement_id"]
        promotion = promotions_by_statement.get(statement_id)
        final_text = source["gdt592_primary_reader_de"]
        promoted_slots = "NONE"
        if promotion is not None:
            source_action = next(
                row for row in source_actions_by_statement[statement_id]
                if row["source_event_id"] == promotion["target_event_id"]
            )
            occurrence = sum(
                row["gdt592_completed_clause_de"]
                == source_action["gdt592_completed_clause_de"]
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
                source_action["gdt592_completed_clause_de"],
                promotion["gdt593_completed_clause_de"],
                occurrence,
            )
            promotion["reader_clause_occurrence_index"] = occurrence
            promoted_slots = promotion["action_slot_id"]
        bath_actions = final_actions_by_statement.get(statement_id, [])
        object_sequence = (
            "|".join(row["gdt593_object_lemma_de"] for row in bath_actions)
            if bath_actions else "NONE"
        )
        row = {
            **source,
            "gdt593_promotion_count": 1 if promotion else 0,
            "gdt593_promoted_action_slot_ids": promoted_slots,
            "gdt593_bath_object_sequence": object_sequence,
            "gdt593_primary_reader_de": final_text,
            "gdt593_reader_changed": "YES" if promotion else "NO",
            "gdt593_guard": (
                "ONLY_12_AIN_OR_OBJECT_CLAUSES_CHANGED__"
                "781_GDT592_STATEMENTS_BYTE_RETAINED"
            ),
        }
        statements.append(row)
        if promotion:
            promoted_statements.append(row)

    pages: list[dict[str, Any]] = []
    for page in sorted(BATH_PAGES):
        members = [row for row in actions if row["physical_page"] == page]
        changed = [row for row in members if row["gdt593_clause_changed"] == "YES"]
        pages.append(
            {
                "page_ordinal": len(pages) + 1,
                "physical_page": page,
                "bath_action_count": len(members),
                "promotion_count": len(changed),
                "promotion_root_profile": json.dumps(
                    dict(sorted(Counter(row["gdt593_promoted_root"] for row in changed).items())),
                    ensure_ascii=False,
                    sort_keys=True,
                ),
                "final_object_profile": json.dumps(
                    dict(sorted(Counter(row["gdt593_object_class"] for row in members).items())),
                    ensure_ascii=False,
                    sort_keys=True,
                ),
                "guard": "SIX_ALREADY_ADMITTED_BATH_PAGES_ONLY__NO_F84",
            }
        )

    result = {
        "experiment_id": "GDT593",
        "status": STATUS,
        "bath_action_count": len(actions),
        "statement_count": len(statements),
        "promotion_count": len(promotions),
        "promoted_statement_count": len(promoted_statements),
        "retained_statement_count": len(statements) - len(promoted_statements),
        "promotion_root_profile": dict(sorted(Counter(row["gdt569_inherited_argument_root"] for row in promotions).items())),
        "promotion_object_profile": dict(sorted(Counter(row["gdt593_object_class"] for row in promotions).items())),
        "source_kind_profile": dict(sorted(Counter(row["gdt581_lexical_source_kind"] for row in promotions).items())),
        "reference_span_profile": dict(sorted(Counter(row["reference_span"] for row in promotions).items())),
        "reference_realization_profile": dict(sorted(Counter(row["reference_realization"] for row in promotions).items())),
        "final_object_profile": dict(sorted(Counter(row["gdt593_object_class"] for row in actions).items())),
        "remaining_cold_bath_object_default_count": sum(
            row["gdt593_selection_route"] == "COLD_BATH_OBJECT_DEFAULT" for row in actions
        ),
        "remaining_y_specific_candidate_count": sum(
            row["gdt569_parallel_relation"]
            == "GDT569_SPECIFIC_CANDIDATE_OVER_GENERIC_DEFAULT"
            and row["gdt569_inherited_argument_root"] == "Y"
            for row in actions
        ),
        "context_witness_event_distance_min": min(int(row["context_witness_event_distance"]) for row in promotions),
        "context_witness_event_distance_max": max(int(row["context_witness_event_distance"]) for row in promotions),
        "input_sha256": {name: sha256(path) for name, path in INPUTS.items()},
        "working_rule_de": (
            "Nur die zwölf neutralen GDT592-Badegut-Fälle mit getragenem AIN oder OR "
            "werden als stabile Typen konkretisiert: AIN zu Anwendungsportion, OR zu "
            "Einheit. Lokales OR übernimmt Stationseinheit, nach Reset wird es am SH-Ziel "
            "zur Badeinheit. Sechs haben eine kanonische gleichsatzinterne Schriftquelle; "
            "bei sechs OWNER_DEFAULT-Fällen bleibt die ältere Schriftstelle nur Kontextzeuge. "
            "Nur fünf Quellen im selben Objektsegment werden anaphorisch als dasselbe "
            "Objekt formuliert; nach Reset wird nur der Typ mit bestimmtem Artikel gesetzt. "
            "Der Badegut-Satz bleibt überall als Rival erhalten; Y wird nicht mitgezogen."
        ),
    }
    return {
        "promotions": promotions,
        "actions": actions,
        "promoted_statements": promoted_statements,
        "statements": statements,
        "pages": pages,
        "result": result,
    }


def render_reader(built: dict[str, Any]) -> str:
    statements = {row["statement_id"]: row for row in built["statements"]}
    actions_by_statement: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in built["actions"]:
        actions_by_statement[row["statement_id"]].append(row)
    lines = [
        "# GDT593 — AIN/OR-vervollständigter Badeobjekt-Leser",
        "",
        "Zwölf zuvor neutrale Badegut-Stellen erhalten hier einen konkreteren Default: "
        "8× `AIN` wird zur **Anwendungsportion**, 4× `OR` zur **Einheit**: lokal "
        "Stationseinheit, nach Reset Badeinheit. "
        "Sechs Fälle besitzen eine gleichsatzinterne Schriftquelle, sechs kommen als "
        "Besitzer-Default aus der GDT569-Kontextspur. Bei den Besitzer-Defaults ist die "
        "letzte geschriebene Stelle nur Kontextzeuge, nicht nachträglich ein lokaler Donor. "
        "Nur fünf Quellen im selben Objektsegment heißen anaphorisch `dieselbe`; nach "
        "einem Reset steht der bestimmte Typ ohne Identitätsbehauptung. "
        "Die alte Badegut-Lesung bleibt in der Promotionstabelle vollständig erhalten.",
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
                f"{row['source_event_id']}={row['gdt593_object_lemma_de']}"
                f"[{row['gdt593_selection_route']}]"
                for row in members
            )
            lines.extend(
                [
                    f"### {statement_id}",
                    "",
                    f"Objektspur: `{trace}`",
                    "",
                    statements[statement_id]["gdt593_primary_reader_de"],
                    "",
                ]
            )
    lines.extend(["## Die zwölf konkreten Karten", ""])
    for row in built["promotions"]:
        source = (
            f"Schriftquelle `{row['canonical_source_slot_or_key']}`"
            if row["gdt581_lexical_source_kind"] == "SAME_STATEMENT_EVENT"
            else f"Besitzer-Default; Kontextzeuge `{row['context_witness_slot_id']}`"
        )
        lines.append(
            f"- `{row['target_event_id']}` ({row['gdt569_inherited_argument_root']}): "
            f"**{row['gdt593_completed_clause_de']}**; {source}; "
            f"Badegut-Rivale: *{row['retained_gdt592_badegut_clause_de']}*."
        )
    lines.extend(
        [
            "",
            "## Nächste Reserve: Y",
            "",
            "49 weitere neutrale Stellen tragen `Y`. Sie werden hier absichtlich noch "
            "nicht global umbenannt: Y kann im konkreten Donorkontext Stationsansatz, "
            "Körper oder Strom sein. Der nächste Pass trennt lokale Donorübernahme von "
            "der körpernahen SH-Bad-Standardlesung.",
            "",
            "Nach diesem Pass bleiben 93 kalte Badegut-Defaults: die 49 Y-Kandidaten "
            "und 44 Stellen ohne spezifische GDT569-Wurzel.",
            "",
        ]
    )
    return "\n".join(lines)


def write_built(built: dict[str, Any]) -> None:
    for name in ("promotions", "actions", "promoted_statements", "statements", "pages"):
        write_tsv(OUTPUTS[name], built[name])
    OUTPUTS["reader"].write_text(render_reader(built), encoding="utf-8")
    OUTPUTS["result"].write_text(
        json.dumps(built["result"], ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
