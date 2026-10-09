#!/usr/bin/env python3
"""Reproduce and validate the append-only GDT600 surface grammar."""

from __future__ import annotations

import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Iterable


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
SRC = Path(__file__).resolve().parent
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

import model  # noqa: E402


CHECKS: list[dict[str, str]] = []


def check(name: str, condition: bool, detail: str = "") -> None:
    CHECKS.append({"check": name, "status": "PASS" if condition else "FAIL", "detail": detail})


def all_equal(values: Iterable[Any], expected: Any) -> bool:
    return all(value == expected for value in values)


def project_rows_exact(
    label: str, source: list[dict[str, str]], rendered: list[dict[str, str]]
) -> None:
    check(f"{label}_row_count", len(source) == len(rendered), f"{len(source)}->{len(rendered)}")
    if not source or len(source) != len(rendered):
        return
    for field in source[0]:
        check(
            f"{label}_old_field_exact__{field}",
            all(left[field] == right.get(field) for left, right in zip(source, rendered)),
            f"field={field}; rows={len(source)}",
        )


def phrase_count(text: str, alternatives: tuple[str, ...]) -> int:
    return sum(text.count(phrase) for phrase in alternatives)


def visible_atom_signature(text: str) -> Counter[str]:
    """Normalize only the wording variants GDT600 is allowed to change."""
    # Q result semantics are protected by the 24-row transition sidecar below;
    # compare the input action here so a more explicit result subject is not
    # mistaken for an added input participant.
    text = text.split("; ", 1)[0]
    signature: Counter[str] = Counter()
    literal_atoms = {
        "MODE_APPLICATION": ("in Anwendungsform",),
        "MODE_FINE": ("in Feinform",),
        "MODE_ALTERNATE": ("in der Alternativform",),
        "MODE_INNER": ("in der Innenform",),
        "MODE_B_VARIANT": ("in der b-Variante",),
        "MODE_G_VARIANT": ("in der g-Variante",),
        "MODE_SECOND_PASS": ("im zweiten Durchgang",),
        "MODE_STATION_KIND": ("in der bezeichneten Stationsart",),
        "FILL": ("bei der angegebenen Füllung", "bei angegebener Füllung"),
        "APPLICATION_STAGE": ("auf der Anwendungsstufe",),
        "BATH_OPERATION": ("im Badbetrieb",),
        "WORK_MAIN": (
            "an der Stations-Hauptstelle", "an der Hauptstelle",
            "an der Haupt- und Arbeitsstelle", "an der Haupt-, Neben- und Arbeitsstelle",
        ),
        "WORK_MIDDLE": ("an der Stations-Mittelstelle", "an der Mittelstelle"),
        "WORK_SIDE": (
            "an der Stations-Nebenstelle", "an der Nebenstelle",
            "an der Neben- und Arbeitsstelle", "Haupt-, Neben- und Arbeitsstelle",
        ),
        "WORK_ACTIVE": (
            "an der Stations-Arbeitsstelle", "an der Arbeitsstelle",
            "an der Haupt- und Arbeitsstelle", "an der Neben- und Arbeitsstelle",
            "an der Haupt-, Neben- und Arbeitsstelle",
        ),
        "WORK_END": ("an der Stations-Endstelle", "an der Endstelle"),
        "SOURCE": (model.SOURCE_RAW, model.SOURCE_CASED, model.SOURCE_CONDITION, model.SOURCE_FRAME),
        "TARGET": (
            model.TARGET_RAW, model.TARGET_DIRECTION, model.TARGET_FLOW_DIRECTION,
            model.TARGET_RECIPIENT, model.TARGET_PURPOSE, model.TARGET_STATIC,
        ),
        "PATH_CONTACT": (model.CONTACT_RAW, model.CONTACT_SHORT),
        "PATH_STATION": (
            "entlang des Stationswegs oder Kanals",
            "entlang des Stationswegs oder des Kanals",
        ),
        "PATH_READING": ("entlang der Lesebahn",),
        "PREVIOUS_WORKSTEP": ("vorangehenden Arbeitsschritt",),
        "NEW_STATION_FRAME": ("Bad- oder Stationsansatz",),
    }
    for atom, alternatives in literal_atoms.items():
        count = phrase_count(text, alternatives)
        if count:
            signature[atom] = count
    # Require a word end: `im Bad` must not match `im Badbetrieb`.
    bath_count = len(re.findall(r"\bim Bad\b", text))
    if bath_count:
        signature["BATH"] = bath_count
    for grade in re.findall(r"(?:auf|bei) Grad (III|II|I)(?!I)", text):
        signature[f"GRADE_{grade}"] += 1
    for grade in re.findall(r"mit der Gradangabe (III|II|I)(?!I)", text):
        signature[f"GRADE_{grade}"] += 1
    for left, right in re.findall(
        r"(?:unter |unter Beachtung der )Gradangaben (III|II|I) und (III|II|I)", text
    ):
        signature[f"GRADE_{left}"] += 1
        signature[f"GRADE_{right}"] += 1

    # FRAME hosts can visibly carry several participants despite their
    # NOT_APPLICABLE primary object column, so protect every stable lemma too.
    lemma_markers = {
        "OBJ_STATION": "Stationsansatz",
        "OBJ_PORTION": "Anwendungsportion",
        "OBJ_BODY_UNIT": "Becken- oder Körpereinheit",
        "OBJ_STATION_UNIT": "Stationseinheit",
        "OBJ_BATH_UNIT": "Badeinheit",
        "OBJ_STATION_BAD_MEASURE": "Stations- oder Badmaß",
        "OBJ_STATION_MEASURE": "Stationsmaß",
        "OBJ_MEASURED_AMOUNT": "abgemessene Menge",
        "OBJ_MEASURE_LABEL": "Maßangabe",
        "OBJ_CONDITION": "Stationsbedingung",
        "OBJ_BODY_PART": "Körperteil",
        "OBJ_PROBE": "Probe",
        "OBJ_FLOW": "Strom",
        "OBJ_BASIN_CONTENT": "Beckeninhalt",
        "OBJ_SUBAMOUNT": "Teilmenge",
        "OBJ_AMOUNT_LABEL": "Mengenangabe",
    }
    for atom, marker in lemma_markers.items():
        count = text.count(marker)
        if count:
            signature[atom] = count
    body_count = len(re.findall(r"\bKörper\b", text))
    if body_count:
        signature["OBJ_BODY"] = body_count
    return signature


def json_bytes(value: Any) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8")


def main() -> int:
    inputs = model.load_inputs()
    built = model.build(inputs)
    hosts = built["hosts"]
    actions = built["actions"]
    statements = built["statements"]
    source_hosts = sorted(inputs["hosts"], key=lambda row: int(row["host_ordinal_global"]))
    source_actions = sorted(inputs["actions"], key=lambda row: int(row["complete_action_ordinal"]))
    source_statements = sorted(inputs["statements"], key=lambda row: int(row["statement_ordinal"]))

    check("fixed_page_set", {row["physical_page"] for row in hosts} == set(model.PAGES))
    check("forbidden_f84_absent", not any(row["physical_page"].startswith("f84") for row in hosts))
    check("host_count_2272", len(hosts) == 2272)
    check("action_count_1443", len(actions) == 1443)
    check("statement_count_313", len(statements) == 313)
    check("changed_host_count_1142", sum(row["gdt600_surface_changed"] == "YES" for row in hosts) == 1142)
    check("changed_action_count_955", sum(row["gdt600_surface_changed"] == "YES" for row in actions) == 955)
    check("changed_statement_count_298", sum(int(row["gdt600_changed_host_count"]) > 0 for row in statements) == 298)

    root_profile = Counter(row["action_root"] for row in hosts)
    expected_roots = Counter({
        "CONTROL": 676, "FRAME": 153, "SH": 300, "OK": 285, "CHD": 199,
        "CH": 196, "K": 159, "S": 104, "T": 93, "P": 55, "R": 52,
    })
    check("complete_host_root_profile", root_profile == expected_roots, str(dict(root_profile)))
    check("action_root_population_1443", sum(root_profile[root] for root in model.ACTION_ROOTS) == 1443)
    check("frame_population_153", root_profile["FRAME"] == 153)
    check("control_population_676", root_profile["CONTROL"] == 676)
    check("paragraph_boundary_count_412", sum(row["paragraph_boundary"] == "PARAGRAPH_AFTER" for row in hosts) == 412)
    check("paragraph_total_419", sum(int(row["gdt600_paragraph_count"]) for row in statements) == 419)
    check("paragraph_counts_preserved", all_equal((row["gdt600_paragraph_count_preserved"] for row in statements), "YES"))
    check("host_ordinals_unique_ordered", [int(row["host_ordinal_global"]) for row in hosts] == sorted({int(row["host_ordinal_global"]) for row in hosts}))
    check("action_ordinals_unique_ordered", [int(row["complete_action_ordinal"]) for row in actions] == list(range(1, 1444)))
    check("statement_ordinals_unique_ordered", [int(row["statement_ordinal"]) for row in statements] == list(range(1, 314)))

    # This creates one executable check for every inherited column, not merely
    # a summary hash.  Object, source, state, page, root and segment fields are
    # therefore all protected row by row.
    project_rows_exact("hosts", source_hosts, hosts)
    project_rows_exact("actions", source_actions, actions)
    project_rows_exact("statements", source_statements, statements)

    host_by_ordinal = {row["host_ordinal_global"]: row for row in hosts}
    new_action_fields = (
        "gdt600_surface_clause_de", "gdt600_surface_changed", "gdt600_rule_ids",
        "gdt600_modifier_reordered", "gdt600_modifier_order_before",
        "gdt600_modifier_order_after", "gdt600_q_result_clause_de",
        "gdt600_q_followup", "gdt600_q_result_source_key",
        "gdt600_surface_reference_mode", "gdt600_source_relation",
        "gdt600_target_relation", "gdt600_grade_relation", "gdt600_guard",
    )
    for field in new_action_fields:
        check(
            f"action_host_join_exact__{field}",
            all(row[field] == host_by_ordinal[row["host_ordinal_global"]][field] for row in actions),
        )

    by_statement: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in hosts:
        by_statement[row["statement_id"]].append(row)
    rebuilt_reader_ok = rebuilt_paragraph_ok = rebuilt_changes_ok = True
    for statement in statements:
        rows = sorted(by_statement[statement["statement_id"]], key=lambda row: int(row["host_ordinal_in_statement"]))
        reader, paragraph_count = model.compose_paragraphs(rows, "gdt600_surface_clause_de")
        rebuilt_reader_ok &= reader == statement["gdt600_surface_reader_de"]
        rebuilt_paragraph_ok &= paragraph_count == int(statement["gdt600_paragraph_count"])
        rebuilt_changes_ok &= sum(row["gdt600_surface_changed"] == "YES" for row in rows) == int(statement["gdt600_changed_host_count"])
    check("statement_reader_rebuild_exact", rebuilt_reader_ok)
    check("statement_paragraph_rebuild_exact", rebuilt_paragraph_ok)
    check("statement_changed_hosts_rebuild_exact", rebuilt_changes_ok)

    atom_mismatches = []
    for old, new in zip(source_hosts, hosts):
        before = visible_atom_signature(old["gdt599_complete_clause_de"])
        after = visible_atom_signature(new["gdt600_surface_clause_de"])
        if before != after:
            atom_mismatches.append({
                "host": old["host_ordinal_global"], "key": old["primary_governor_key"],
                "before": dict(before), "after": dict(after),
            })
    check("nonverbal_visible_atom_multiset_preserved_2272_of_2272", not atom_mismatches, json.dumps(atom_mismatches[:5], ensure_ascii=False))

    # Auxiliary populations remain live and are not silently dismissed.
    project_rows_exact("aiin_passthrough", inputs["aiin_bindings"], built["aiin_passthrough"])
    project_rows_exact("propagation_passthrough", inputs["propagation"], built["propagation_passthrough"])
    project_rows_exact("local_card_passthrough", inputs["local_cards"], built["local_passthrough"])
    project_rows_exact("manual_review_passthrough", inputs["manual_reviews"], built["manual_review_passthrough"])
    project_rows_exact("review_queue_passthrough", inputs["review_queue"], built["reviews"])
    check("aiin_count_46", len(built["aiin_passthrough"]) == 46)
    check("propagation_count_3", len(built["propagation_passthrough"]) == 3)
    check("local_card_count_40", len(built["local_passthrough"]) == 40)
    check("manual_review_count_40", len(built["manual_review_passthrough"]) == 40)
    check("review_queue_count_125", len(built["reviews"]) == 125)
    check("reviews_not_dismissed", all_equal((row["semantic_review_status"] for row in built["reviews"]), "RETAINED__SURFACE_PASS_DOES_NOT_DISMISS_OBJECT_OR_SOURCE_REVIEW"))

    flow_eligible = {
        row["primary_governor_key"] for row in inputs["replay"]
        if model.flow_generalization_eligible(row)
    }
    flow_rows = built["flow_generalizations"]
    check("flow_generalization_count_7", len(flow_rows) == 7)
    check("flow_generalization_predicate_recovers_exact_7", len(flow_eligible) == 7 and {row["primary_governor_key"] for row in flow_rows} == flow_eligible)
    check("flow_generalization_predicate_ignores_manual_ids", all(
        model.flow_generalization_eligible({**row, "manual_override_id": "NONE"})
        for row in inputs["replay"] if row["primary_governor_key"] in flow_eligible
    ))
    check("flow_inherited_counterexample_excluded", "ACTION:G407-E3568@3:CH" not in flow_eligible)
    check("flow_generalization_contact_visible", all_equal((row["contact_or_line_visible"] for row in flow_rows), "YES"))
    check("flow_generalization_result_flow", all_equal((row["final_object_class"] for row in flow_rows), "FLOW"))
    check("flow_generalization_object_unchanged", all_equal((row["gdt600_status"] for row in flow_rows), "SUBSUMED_BY_ONE_RULE__OBJECT_UNCHANGED"))
    check("remaining_manual_count_4", len(built["manual_remaining"]) == 4)
    check("remaining_manual_ids", {row["review_id"] for row in built["manual_remaining"]} == {"W01", "W02", "W10", "W11"})

    condition_source = {"ACTION:G407-E3162@4:T", "ACTION:G407-E3569@1:T"}
    condition_target = {
        "ACTION:G407-E2698@1:T", "ACTION:G407-E3543@2:T",
        "ACTION:G407-E3592@1:T", "ACTION:G407-E3795@2:T",
    }
    condition_rows = built["condition_relations"]
    check("condition_relation_count_6", len(condition_rows) == 6)
    check("condition_source_exact_2", {row["primary_governor_key"] for row in condition_rows if row["relation_class"] == "SOURCE"} == condition_source)
    check("condition_target_exact_4", {row["primary_governor_key"] for row in condition_rows if row["relation_class"] == "TARGET"} == condition_target)
    check("condition_prepolished_count_3", sum(row["already_polished_in_gdt599"] == "YES" for row in condition_rows) == 3)
    check("condition_source_wording", all(model.SOURCE_CONDITION in row["gdt600_clause_de"] for row in condition_rows if row["relation_class"] == "SOURCE"))
    check("condition_target_wording", all(model.TARGET_PURPOSE in row["gdt600_clause_de"] for row in condition_rows if row["relation_class"] == "TARGET"))

    bounded = built["bounded_right"]
    preview_expected = {
        "ACTION:G407-E3331@1:CH": ("DEFAULT:P:PORTION", "ACTION:G407-E3331@2:P"),
        "ACTION:G407-E3458@1:CH": ("DEFAULT:P:PORTION", "ACTION:G407-E3458@3:P"),
        "ACTION:G407-E3469@1:R": ("DEFAULT:CH:STATION", "ACTION:G407-E3469@2:CH"),
        "ACTION:G407-E3689@1:SH": ("DEFAULT:CH:STATION", "ACTION:G407-E3689@2:CH"),
        "ACTION:G407-E3690@1:SH": ("DEFAULT:CH:STATION", "ACTION:G407-E3690@2:CH"),
    }
    previews = [row for row in bounded if row["gdt600_provenance_route"] == "T06B_RIGHT_ROOT_DEFAULT_PREVIEW"]
    retained = [row for row in bounded if row["gdt600_provenance_route"] == "T06A_RIGHT_RETAINED_COMPLETED"]
    check("bounded_right_total_21", len(bounded) == 21)
    check("bounded_right_retained_16", len(retained) == 16)
    check("bounded_right_preview_5", len(previews) == 5)
    check("bounded_right_preview_seed_map", {row["primary_governor_key"]: (row["causal_source_pointer"], row["preview_host_pointer"]) for row in previews} == preview_expected)
    check("bounded_right_preview_seed_layer", all_equal((row["preview_completion_layer"] for row in previews), "ROOT_DEFAULT_PREVIEW_SEED"))
    check("bounded_right_retained_source", all(row["causal_source_pointer"] == row["preview_host_pointer"] for row in retained))
    check("bounded_right_object_unchanged", all_equal((row["object_changed"] for row in bounded), "NO"))

    q_rows = built["q_grammar"]
    q_inputs = {row["primary_governor_key"]: row for row in inputs["q_transitions"]}
    q_by_event = {model.q_event_id(key): key for key in q_inputs}
    action_by_key = {row["primary_governor_key"]: row for row in actions}
    check("q_population_24", len(q_rows) == 24)
    check("q_key_population_exact", {row["primary_governor_key"] for row in q_rows} == set(q_inputs))
    check("q_transition_fields_preserved", all(
        row["result_object_class"] == q_inputs[row["primary_governor_key"]]["result_object_class"]
        and row["result_object_lemma_de"] == q_inputs[row["primary_governor_key"]]["result_object_lemma_de"]
        and row["commit_order"] == q_inputs[row["primary_governor_key"]]["commit_order"]
        for row in q_rows
    ))
    check("q_results_all_station", all_equal((row["result_object_class"] for row in q_rows), "STATION"))
    check("q_result_lowercase", all(row["gdt600_result_clause_de"][:1].islower() for row in q_rows))
    check("q_result_declares_new_approach", all("gilt nun als neuer Bad- oder Stationsansatz" in row["gdt600_result_clause_de"] for row in q_rows))
    check("q_action_one_semicolon", all(action_by_key[row["primary_governor_key"]]["gdt600_surface_clause_de"].count("; ") == 1 for row in q_rows))
    check("q_takeover_removed", all("übernimm" not in action_by_key[row["primary_governor_key"]]["gdt600_surface_clause_de"] for row in q_rows))
    check("q_input_then_result_exact", all(
        action_by_key[row["primary_governor_key"]]["gdt600_surface_clause_de"]
        == row["gdt600_input_clause_de"] + "; " + row["gdt600_result_clause_de"]
        for row in q_rows
    ))
    q_specials = {
        "ACTION:G407-E2630@1:OK": "der vorbereitete Stationsansatz",
        "ACTION:G407-E3377@4:S": "die ausgewählte Einheit",
        "ACTION:G407-E3490@3:K": "das Ergebnis der Zuführung",
        "ACTION:G407-E3559@3:CH": "der Ablauf",
    }
    check("q_specific_result_nouns", all(q_specials[key] in action_by_key[key]["gdt600_q_result_clause_de"] for key in q_specials))

    expected_followups = {}
    for row in source_actions:
        resolved = model.resolve_q_source(row["source_pointer"], q_inputs, q_by_event)
        if resolved != "NONE" and row["primary_governor_key"] != resolved:
            expected_followups[row["primary_governor_key"]] = resolved
    followups = built["q_followups"]
    check("q_followup_count_7", len(followups) == 7)
    check("q_followup_exact_resolved_map", {row["primary_governor_key"]: row["resolved_q_source_key"] for row in followups} == expected_followups)
    check("q_followup_alias_count_2", sum(row["q_source_pointer"].startswith(("CARRY:", "HANDOFF:")) for row in followups) == 2)
    check("q_followup_new_demonstrative", all("diesen neuen Stationsansatz" in row["gdt600_clause_de"] for row in followups))
    check("q_followup_old_np_removed", all("denselben Stationsansatz" not in row["gdt600_clause_de"] for row in followups))

    # Repeat scope ignores OL/frame hosts but stops at OT/new-workstep controls.
    expected_repeats: list[tuple[str, str, int]] = []
    previous_action = None
    current_statement = ""
    barrier = False
    intervening = 0
    for row in source_hosts:
        if row["statement_id"] != current_statement:
            current_statement = row["statement_id"]
            previous_action = None
            barrier = False
            intervening = 0
        if row["action_root"] in model.ACTION_ROOTS:
            if previous_action and not barrier and row["gdt599_complete_clause_de"] == previous_action["gdt599_complete_clause_de"]:
                expected_repeats.append((row["primary_governor_key"], previous_action["primary_governor_key"], intervening))
            previous_action = row
            barrier = False
            intervening = 0
        elif previous_action:
            intervening += 1
            if row["action_root"] == "CONTROL" and row["gdt599_complete_clause_de"].startswith("Beginne danach"):
                barrier = True
    repeats = built["repeats"]
    check("repeat_count_18", len(repeats) == len(expected_repeats) == 18)
    check("repeat_exact_pairs_scope", [(row["primary_governor_key"], row["previous_governor_key"], int(row["intervening_host_count"])) for row in repeats] == expected_repeats)
    check("repeat_cross_host_count_3", sum(int(row["intervening_host_count"]) > 0 for row in repeats) == 3)
    check("repeat_again_marker", all(" erneut" in row["gdt600_repeat_clause_de"] for row in repeats))
    check("repeat_ot_barrier", "ACTION:G407-E3708@2:CHD" not in {row["primary_governor_key"] for row in repeats})

    expected_control_repeats: list[tuple[str, str]] = []
    previous_host = None
    for row in source_hosts:
        if (
            previous_host is not None
            and row["statement_id"] == previous_host["statement_id"]
            and row["action_root"] == previous_host["action_root"] == "CONTROL"
            and row["gdt599_complete_clause_de"] == previous_host["gdt599_complete_clause_de"]
        ):
            expected_control_repeats.append((row["primary_governor_key"], previous_host["primary_governor_key"]))
        previous_host = row
    control_repeats = built["control_repeats"]
    check("control_repeat_count_34", len(control_repeats) == len(expected_control_repeats) == 34)
    check("control_repeat_exact_pairs", [(row["primary_governor_key"], row["previous_governor_key"]) for row in control_repeats] == expected_control_repeats)
    check("control_repeat_kind_profile", Counter(row["control_repeat_kind"] for row in control_repeats) == Counter({"OL_REPEAT_SAME_WORKSTEP": 27, "OT_REPEAT_NEXT_WORKSTEP": 7}))
    check("control_ol_repeat_surface", all(row["gdt600_repeat_clause_de"] == "Fahre erneut im selben Arbeitsgang fort" for row in control_repeats if row["control_repeat_kind"] == "OL_REPEAT_SAME_WORKSTEP"))
    check("control_ot_repeat_surface", all(row["gdt600_repeat_clause_de"] == "Beginne danach einen weiteren Arbeitsgang" for row in control_repeats if row["control_repeat_kind"] == "OT_REPEAT_NEXT_WORKSTEP"))

    probes = [row for row in actions if row["object_lemma_de"] == "Probe"]
    bodypart = [row for row in hosts if "R18_BODY_PART_GENDER" in row["gdt600_rule_ids"]]
    check("probe_population_2", len(probes) == 2)
    check("probe_first_indefinite", sum("eine Probe" in row["gdt600_surface_clause_de"] for row in probes) == 1)
    check("probe_followup_demonstrative", sum("diese Probe" in row["gdt600_surface_clause_de"] for row in probes) == 1)
    check("probe_sampling_word_order", action_by_key["ACTION:G407-E2616@3:CH"]["gdt600_surface_clause_de"] == "Entnimm an der Arbeitsstelle über Kontakt oder Leitung eine Probe am selben Körperteil")
    check("bodypart_gender_once", len(bodypart) == 1)
    check("bodypart_neuter_removed", not any("dasselbe Körperteil" in row["gdt600_surface_clause_de"] for row in hosts))

    # Explicit grade scope: non-T governors use a process condition, T-linked
    # frames expose an Einstellung, and unbound frames become neutral rather
    # than silently inheriting a T/non-T interpretation.
    grade_scope_ok = True
    for old, new in zip(source_hosts, hosts):
        old_on = len(re.findall(r"auf Grad (?:III|II|I)(?!I)", old["gdt599_complete_clause_de"]))
        new_on = len(re.findall(r"auf Grad (?:III|II|I)(?!I)", new["gdt600_surface_clause_de"]))
        if model.explicit_process_grade(old):
            grade_scope_ok &= new_on == 0
        elif old["action_root"] == "FRAME" and old_on:
            if model.frame_has_t_governor(old):
                grade_scope_ok &= new["gdt600_surface_clause_de"].count("mit Einstellung auf Grad") == old_on
            else:
                grade_scope_ok &= new["gdt600_surface_clause_de"].count("mit der Gradangabe") == old_on
    check("grade_relation_scope_explicit", grade_scope_ok)
    t_frame_keys = {
        "ACTION_CHAIN:G407-E1740:T", "ACTION_CHAIN:G407-E2421:T",
        "ACTION_CHAIN:G407-E2620:T", "ACTION_CHAIN:G407-E2784:T",
        "ACTION_CHAIN:G407-E3200:CH+T",
    }
    check("t_and_mixed_frame_grades_explicit", all("mit Einstellung auf Grad" in next(row for row in hosts if row["primary_governor_key"] == key)["gdt600_surface_clause_de"] for key in t_frame_keys))
    check("neutral_frame_grade_count_49", sum(row["gdt600_grade_relation"] == "NEUTRAL_FRAME_GRADE" for row in hosts) == 49)
    check("target_grade_count_34", sum(row["gdt600_grade_relation"] == "TARGET_GRADE" for row in hosts) == 34)
    check("process_grade_count_485", sum(row["gdt600_grade_relation"] == "PROCESS_CONDITION" for row in hosts) == 485)
    check("surface_grade_relation_recomputed", all(row["gdt600_grade_relation"] == model.grade_relation(old, row["gdt600_surface_clause_de"]) for old, row in zip(source_hosts, hosts)))

    check("surface_source_relation_recomputed", all(row["gdt600_source_relation"] == model.source_relation(row["gdt600_surface_clause_de"]) for row in hosts))
    check("surface_target_relation_recomputed", all(row["gdt600_target_relation"] == model.target_relation(row["gdt600_surface_clause_de"]) for row in hosts))
    check("source_relation_profile_exact", Counter(row["gdt600_source_relation"] for row in hosts) == Counter({"NONE": 2174, "ORIGIN": 89, "FRAME_ORIGIN": 7, "CONDITION_SOURCE": 2}))
    check("target_relation_profile_exact", Counter(row["gdt600_target_relation"] for row in hosts) == Counter({"NONE": 2159, "PURPOSE": 63, "STATIC_LOCATION": 20, "RECIPIENT": 14, "DIRECTION": 12, "FLOW_DIRECTION": 4}))
    check("surface_reference_profile_exact", Counter(row["gdt600_surface_reference_mode"] for row in hosts) == Counter({
        "INHERITED_DEFINITE": 1085, "INHERITED_ANAPHORIC": 349,
        "INHERITED_NOT_APPLICABLE": 829, "DEMONSTRATIVE_NEW_Q_RESULT": 7,
        "INDEFINITE_INTRODUCTION": 1, "DEMONSTRATIVE_ANAPHORIC": 1,
    }))
    check("surface_reference_overrides_exact_9", sum(not row["gdt600_surface_reference_mode"].startswith("INHERITED_") for row in hosts) == 9)

    modifier_orders = {modifier_id: order for modifier_id, order, _phrase in model.MODIFIER_SPECS}
    modifier_counter_ok = True
    modifier_rank_ok = True
    for row in hosts:
        if row["gdt600_modifier_reordered"] != "YES":
            continue
        before_ids = row["gdt600_modifier_order_before"].split("|")
        after_ids = row["gdt600_modifier_order_after"].split("|")
        modifier_counter_ok &= Counter(before_ids) == Counter(after_ids)
        ranks = [modifier_orders[modifier_id] for modifier_id in after_ids]
        modifier_rank_ok &= ranks == sorted(ranks)
    check("modifier_reorder_count_378", sum(row["gdt600_modifier_reordered"] == "YES" for row in hosts) == 378)
    check("modifier_id_multiset_preserved", modifier_counter_ok)
    check("modifier_rank_monotonic", modifier_rank_ok)
    check("badbetrieb_not_parsed_as_bath", all(
        "BATH" not in row["gdt600_modifier_order_before"].split("|")
        for row in hosts if "im Badbetrieb" in row["gdt599_complete_clause_de"]
    ))
    source_mode_rows = [
        row for row in hosts
        if model.SOURCE_CASED in row["gdt600_surface_clause_de"]
        and "in Anwendungsform" in row["gdt600_surface_clause_de"]
    ]
    check("origin_before_application_mode_count_8", len(source_mode_rows) == 8)
    check("origin_precedes_application_mode", all(
        row["gdt600_surface_clause_de"].index(model.SOURCE_CASED)
        < row["gdt600_surface_clause_de"].index("in Anwendungsform")
        for row in source_mode_rows
    ))
    check("peer_mode_coordination_count_4", sum("R21_PEER_MODE_COORDINATION" in row["gdt600_rule_ids"] for row in hosts) == 4)
    check("peer_mode_stacks_zero", not any(
        "in Anwendungsform in Feinform" in row["gdt600_surface_clause_de"]
        or "in Anwendungsform in der Innenform" in row["gdt600_surface_clause_de"]
        for row in hosts
    ))
    check("t_stage_grade_surface", action_by_key["ACTION:G407-E2585@3:T"]["gdt600_surface_clause_de"].startswith("Temperiere den Stationsansatz auf der Anwendungsstufe bis auf Grad I"))
    check("t_cooling_surface", action_by_key["ACTION:G407-E3013@4:T"]["gdt600_surface_clause_de"] == "Lass denselben Stationsansatz anschließend an der Arbeitsstelle auf Grad II abkühlen")

    rule_counts = Counter()
    for row in hosts:
        if row["gdt600_rule_ids"] != "NONE":
            rule_counts.update(row["gdt600_rule_ids"].split("|"))
    expected_rule_counts = Counter({
        "R01_CH_LINE_FLOW_GENERALIZATION": 7,
        "R02_CH_OBJECT_VALENCY": 168,
        "R03_OK_PREPARE": 234,
        "R04_CONDITION_SOURCE": 2,
        "R05_CONDITION_TARGET": 4,
        "R06_SOURCE_CASE": 96,
        "R07_TARGET_VALENCY": 109,
        "R08_CONTACT_SHORT": 146,
        "R09_WORKSITE_SHORT": 140,
        "R10_PROCESS_GRADE": 485,
        "R11_MULTI_GRADE": 2,
        "R12_MODIFIER_ORDER": 378,
        "R13_FRAME_COMPLETE": 153,
        "R14_Q_RESULT_STATE": 24,
        "R15_Q_FOLLOWUP_NEW": 7,
        "R16_REPEAT_AGAIN": 18,
        "R17_PROBE_REFERENCE": 2,
        "R18_BODY_PART_GENDER": 1,
        "R19_K_SOURCE_VALENCY": 10,
        "R20_FRAME_GRADE_SCOPE": 54,
        "R21_PEER_MODE_COORDINATION": 4,
        "R22_CONTROL_REPEAT": 34,
        "R23_T_STAGE_GRADE": 1,
        "R24_T_COOLING_ORDER": 1,
    })
    check("renderer_rule_profile_exact", rule_counts == expected_rule_counts, str(dict(sorted(rule_counts.items()))))
    check("all_24_rules_used", set(rule_counts) == set(model.RULE_SPECS))
    check("rule_sidecar_matches_hosts", {row["rule_id"]: int(row["occurrence_count"]) for row in built["rules"]} == dict(rule_counts))

    frames = [row for row in hosts if row["action_root"] == "FRAME"]
    check("all_153_frames_complete", len(frames) == 153 and all("R13_FRAME_COMPLETE" in row["gdt600_rule_ids"] for row in frames))
    check("all_frames_keep_workstep_atom", sum("vorangehenden Arbeitsschritt" in row["gdt600_surface_clause_de"] for row in frames) == 153)
    check("frame_object_imperatives_10", sum(row["gdt600_surface_clause_de"].startswith("Verwende ") for row in frames) == 10)
    check("frame_modifier_imperatives_143", sum(row["gdt600_surface_clause_de"].startswith("Führe ") for row in frames) == 143)
    check("frame_grade_scope_count_54", sum("R20_FRAME_GRADE_SCOPE" in row["gdt600_rule_ids"] for row in frames) == 54)
    check("frame_fragment_zero", not any("Verwende für den vorangehenden Arbeitsschritt" in row["gdt600_surface_clause_de"] for row in hosts))
    check("ch_double_verb_zero", not any("Entnimm oder lass" in row["gdt600_surface_clause_de"] for row in hosts))
    check("ok_double_verb_zero", not any("Beschicke oder bereite" in row["gdt600_surface_clause_de"] for row in hosts))
    check("r_broad_reading_retained_52", sum("Kennzeichne oder prüfe" in row["gdt600_surface_clause_de"] for row in hosts) == 52)
    check("raw_source_zero", not any(model.SOURCE_RAW in row["gdt600_surface_clause_de"] for row in hosts))
    check("raw_target_zero", not any(model.TARGET_RAW in row["gdt600_surface_clause_de"] for row in hosts))
    check("verbose_contact_zero", not any(model.CONTACT_RAW in row["gdt600_surface_clause_de"] for row in hosts))
    check("explicit_process_on_grade_zero", not any(
        model.explicit_process_grade(row)
        and re.search(r"auf Grad (?:III|II|I)(?!I)", row["gdt600_surface_clause_de"])
        for row in hosts
    ))

    # Object-conditioned valency cells found by the independent reader audit.
    ch_channel = action_by_key["ACTION:G407-E3247@3:CH"]["gdt600_surface_clause_de"]
    check("ch_station_channel_is_outflow", ch_channel.startswith("Lass den Stationsansatz") and ch_channel.endswith(" ab"))
    check("ch_nonflow_target_is_purpose", all(
        model.TARGET_PURPOSE in action_by_key[key]["gdt600_surface_clause_de"]
        for key in ("ACTION:G407-E1441@1:CH", "ACTION:G407-E2581@1:CH")
    ))
    check("k_nonbody_targets_dative_14", sum(
        row["action_root"] == "K" and row["object_class"] != "BODY"
        and model.TARGET_RECIPIENT in row["gdt600_surface_clause_de"] for row in actions
    ) == 14)
    check("k_body_target_direction_once", model.TARGET_DIRECTION in action_by_key["ACTION:G407-E2927@3:K"]["gdt600_surface_clause_de"] and not action_by_key["ACTION:G407-E2927@3:K"]["gdt600_surface_clause_de"].endswith(" ein"))
    check("k_source_only_completed_10", sum("R19_K_SOURCE_VALENCY" in row["gdt600_rule_ids"] and row["gdt600_surface_clause_de"].endswith(" heran") for row in actions) == 10)
    check("p_target_is_purpose", all(
        model.TARGET_PURPOSE in row["gdt600_surface_clause_de"]
        for row in actions if row["action_root"] == "P" and model.TARGET_RAW in row["gdt599_complete_clause_de"]
    ))
    check("t_target_is_purpose", all(
        model.TARGET_PURPOSE in row["gdt600_surface_clause_de"]
        for row in actions if row["action_root"] == "T" and model.TARGET_RAW in row["gdt599_complete_clause_de"]
    ))
    check("frame_target_is_static", all(
        model.TARGET_STATIC in row["gdt600_surface_clause_de"]
        for row in frames if model.TARGET_RAW in row["gdt599_complete_clause_de"]
    ))

    surfaces = [row["gdt600_surface_clause_de"] for row in hosts]
    check("surface_nonempty", all(surface.strip() for surface in surfaces))
    check("surface_no_tabs_newlines", all("\t" not in surface and "\n" not in surface and "\r" not in surface for surface in surfaces))
    check("surface_no_double_spaces", all("  " not in surface for surface in surfaces))
    check("surface_no_double_commas", all(",," not in surface for surface in surfaces))
    check("surface_no_empty_semicolon", all("; ;" not in surface for surface in surfaces))
    check("surface_semicolon_only_q", all(("; " in row["gdt600_surface_clause_de"]) == ("R14_Q_RESULT_STATE" in row["gdt600_rule_ids"]) for row in hosts))
    check("surface_no_dangling_linkword", not any(re.search(r"\b(?:und|oder|von|zur|für|über|bei)[.;]?$", surface) for surface in surfaces))
    flat_modifier = re.compile(
        r"(?:,|\bund\b)\s+(?:bei Grad|auf Grad|im Bad|an der (?:Haupt|Mittel|Neben|Arbeits|End)stelle|"
        r"aus der Ausgangsstation|über Kontakt|zur Zielstation|für die Zielstation|entlang des Stationswegs)"
    )
    check("surface_no_flat_modifier_coordination", not any(flat_modifier.search(surface) for surface in surfaces))
    duplicate_particle = re.compile(r"\b(vor|zu|ein|an|aus|um|ab|heran|heraus|aufrecht)\s+\1\b")
    check("surface_no_duplicate_particles", not any(duplicate_particle.search(surface) for surface in surfaces))

    before_quality = built["result"]["quality_before"]
    after_quality = built["result"]["quality_after"]
    check("quality_before_q_followups_7", before_quality["old_q_followup"] == 7)
    check("quality_after_named_defects_zero", all(value == 0 for value in after_quality.values()), str(after_quality))
    check("result_object_invariance_1443", built["result"]["unchanged_object_count"] == 1443)
    check("result_source_invariance_1443", built["result"]["unchanged_source_pointer_count"] == 1443)
    check("result_q_invariance_24", built["result"]["unchanged_q_transition_count"] == 24)

    page_hosts = Counter(row["physical_page"] for row in source_hosts)
    page_actions = Counter(row["physical_page"] for row in source_actions)
    page_statements = Counter(row["physical_page"] for row in source_statements)
    check("page_profile_count_6", len(built["pages"]) == 6)
    check("page_profile_order", tuple(row["physical_page"] for row in built["pages"]) == model.PAGES)
    check("page_host_counts", all(int(row["host_count"]) == page_hosts[row["physical_page"]] for row in built["pages"]))
    check("page_action_counts", all(int(row["action_count"]) == page_actions[row["physical_page"]] for row in built["pages"]))
    check("page_statement_counts", all(int(row["statement_count"]) == page_statements[row["physical_page"]] for row in built["pages"]))
    check("reader_313_statement_heads", sum(line.startswith("### G407-S") for line in built["reader"].splitlines()) == 313)
    check("reader_6_page_heads", sum(line.startswith("## f") for line in built["reader"].splitlines()) == 6)

    # Rebuild every generated artifact from memory and compare bytes.
    for name, path in model.OUTPUTS.items():
        if name == "validation":
            continue
        if name == "reader":
            expected = built["reader"].encode("utf-8")
        elif name == "result":
            expected = json_bytes(built["result"])
        else:
            expected = model.tsv_bytes(built[name])
        check(f"artifact_byte_reproduction__{name}", path.is_file() and path.read_bytes() == expected, path.name)

    expected_names = {path.name for path in model.OUTPUTS.values()} | {"README.md"}
    current_names = {path.name for path in model.ARTIFACTS.iterdir() if path.is_file()} | {model.OUTPUTS["validation"].name}
    check("artifact_allowlist_exact", current_names == expected_names, str(sorted(current_names ^ expected_names)))

    failures = [row for row in CHECKS if row["status"] == "FAIL"]
    validation = {
        "experiment_id": "GDT600",
        "status": (
            f"PASS_{len(CHECKS)}_CHECKS__COMPLETE_OBJECT_SURFACE_GRAMMAR_REPRODUCED"
            if not failures else f"FAIL_{len(failures)}_OF_{len(CHECKS)}_CHECKS"
        ),
        "check_count": len(CHECKS),
        "pass_count": len(CHECKS) - len(failures),
        "fail_count": len(failures),
        "guard": model.GUARD,
        "checks": CHECKS,
    }
    model.OUTPUTS["validation"].write_bytes(json_bytes(validation))
    print(json.dumps({
        "status": validation["status"], "checks": validation["check_count"],
        "failures": [row["check"] for row in failures],
    }, ensure_ascii=False, sort_keys=True))
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
