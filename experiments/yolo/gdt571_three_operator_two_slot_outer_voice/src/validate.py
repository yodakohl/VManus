#!/usr/bin/env python3
"""Independent validation for GDT571's three-operator two-slot outer voice."""

from __future__ import annotations

import csv
import hashlib
import json
import subprocess
from collections import Counter, defaultdict
from pathlib import Path


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
BASE = ROOT / "experiments/yolo/gdt571_three_operator_two_slot_outer_voice"
OUT = BASE / "artifacts"
G570 = ROOT / "experiments/yolo/gdt570_five_fragment_four_join_modifier_voice/artifacts"
G565 = ROOT / "experiments/yolo/gdt565_state_microphrase_template_generator/artifacts"
G557 = ROOT / "experiments/yolo/gdt557_thirty_page_ot_ol_dy_state_grammar/artifacts"
INPUTS = {
    "modifier_states": G570 / "gdt570_1656_modifier_voice_state_clauses.tsv",
    "modifier_events": G570 / "gdt570_5122_modifier_voice_event_edition.tsv",
    "modifier_statements": G570 / "gdt570_793_modifier_voice_statement_edition.tsv",
    "page_profiles": G570 / "gdt570_30_page_modifier_voice_profiles.tsv",
    "template_replay": G565 / "gdt565_1656_template_replay.tsv",
    "renderer_cards": G565 / "gdt565_42_renderer_cards.tsv",
    "sequence_profiles": G557 / "gdt557_marker_sequence_profiles.tsv",
}
ARTIFACTS = {
    "cards": OUT / "gdt571_3_operator_voice_cards.tsv",
    "slots": OUT / "gdt571_2_outer_slot_rules.tsv",
    "sequences": OUT / "gdt571_9_sequence_factorizations.tsv",
    "assignments": OUT / "gdt571_1870_marker_slot_assignments.tsv",
    "changes": OUT / "gdt571_54_changed_outer_clauses.tsv",
    "states": OUT / "gdt571_1656_outer_voice_state_clauses.tsv",
    "events": OUT / "gdt571_5122_outer_voice_event_edition.tsv",
    "statements": OUT / "gdt571_793_outer_voice_statement_edition.tsv",
    "pages": OUT / "gdt571_30_page_outer_voice_profiles.tsv",
    "book": OUT / "GDT571_OUTER_VOICE_THIRTY_PAGE_EDITION.md",
    "result": OUT / "gdt571_result.json",
}
MARKERS = {"OT", "OL", "DY"}
ENTRY = {"OT": "Danach", "OL": "Weiter"}
FOLLOWER = {"OT": "eröffne danach den nächsten Gang", "OL": "führe den Gang weiter", "DY": "schließe den Schritt"}
CURRENT_TAIL = {
    "DY": "schließe den Schritt",
    "OT+DY": "schließe den Schritt",
    "OL+DY": "schließe den Schritt",
    "OT+OL": "weiterführen",
    "OL+OL": "nochmals weiterführen",
    "OL+OT": "danach nächsten Gang eröffnen",
    "DY+OL": "schließe den Schritt; danach weiterführen",
}
EXPECTED_SEQUENCE_COUNTS = Counter({"OL": 619, "DY": 544, "OT": 279, "OT+DY": 86, "OL+DY": 74, "OT+OL": 38, "OL+OL": 14, "DY+OL": 1, "OL+OT": 1})
STATUS = (
    "PASS_3_OPERATOR_CARDS__5_POSITION_REALIZATIONS__2_SLOT_RULES__9_SEQUENCES__"
    "1870_MARKERS__54_FINITE_FOLLOWERS__ZERO_ROOT_CHANGE"
)


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def marker_sequence(recipe: str) -> list[str]:
    return [atom for atom in recipe.split("+") if atom in MARKERS]


def slots(sequence: list[str]) -> tuple[str, list[str]]:
    if sequence[0] in ENTRY:
        return sequence[0], sequence[1:]
    return "NONE", sequence


def expected_clause(current: str, sequence: list[str]) -> str:
    sequence_key = "+".join(sequence)
    entry, followers = slots(sequence)
    if entry != "NONE" and not current.startswith(ENTRY[entry]):
        raise RuntimeError(f"Entry drift in validator: {sequence_key}")
    if not followers:
        return current
    old_suffix = f"; {CURRENT_TAIL[sequence_key]}."
    if not current.endswith(old_suffix):
        raise RuntimeError(f"Tail drift in validator: {sequence_key}")
    new_suffix = "; " + "; ".join(FOLLOWER[marker] for marker in followers) + "."
    return current[: -len(old_suffix)] + new_suffix


def main() -> int:
    checks: list[dict[str, object]] = []

    def check(name: str, passed: bool, detail: object = None) -> None:
        checks.append({"check": name, "passed": bool(passed), "detail": detail})

    source_states = read_tsv(INPUTS["modifier_states"])
    source_events = read_tsv(INPUTS["modifier_events"])
    source_statements = read_tsv(INPUTS["modifier_statements"])
    source_pages = read_tsv(INPUTS["page_profiles"])
    replay = read_tsv(INPUTS["template_replay"])
    renderer_cards = read_tsv(INPUTS["renderer_cards"])
    old_profiles = read_tsv(INPUTS["sequence_profiles"])
    cards = read_tsv(ARTIFACTS["cards"])
    slot_rules = read_tsv(ARTIFACTS["slots"])
    sequence_profiles = read_tsv(ARTIFACTS["sequences"])
    assignments = read_tsv(ARTIFACTS["assignments"])
    changes = read_tsv(ARTIFACTS["changes"])
    states = read_tsv(ARTIFACTS["states"])
    events = read_tsv(ARTIFACTS["events"])
    statements = read_tsv(ARTIFACTS["statements"])
    pages = read_tsv(ARTIFACTS["pages"])
    result = json.loads(ARTIFACTS["result"].read_text(encoding="utf-8"))

    check("input_counts", [len(source_states), len(source_events), len(source_statements), len(source_pages), len(replay), len(renderer_cards), len(old_profiles)] == [1656, 5122, 793, 30, 1656, 42, 9])
    check("artifact_counts", [len(cards), len(slot_rules), len(sequence_profiles), len(assignments), len(changes), len(states), len(events), len(statements), len(pages)] == [3, 2, 9, 1870, 54, 1656, 5122, 793, 30])
    sealed_hits = sorted({row.get("physical_page", "") for table in (states, events, statements, pages) for row in table if row.get("physical_page", "").lower() in {"f84", "f84r"}})
    check("sealed_pages_absent", not sealed_hits, sealed_hits)
    check("state_ordinals", [int(row["state_edition_ordinal"]) for row in states] == list(range(1, 1657)))
    check("event_ordinals", [int(row["edition_event_ordinal"]) for row in events] == list(range(1, 5123)))
    check("statement_ordinals", [int(row["edition_statement_ordinal"]) for row in statements] == list(range(1, 794)))
    check("page_ordinals", [int(row["page_ordinal"]) for row in pages] == list(range(1, 31)))
    check("assignment_ordinals", [int(row["assignment_ordinal"]) for row in assignments] == list(range(1, 1871)))
    check("change_ordinals", [int(row["change_ordinal"]) for row in changes] == list(range(1, 55)))

    source_state_by_id = {row["event_id"]: row for row in source_states}
    replay_by_id = {row["event_id"]: row for row in replay}
    state_by_id = {row["event_id"]: row for row in states}
    check("state_keys_exact", len(source_state_by_id) == len(state_by_id) == 1656 and set(source_state_by_id) == set(state_by_id) == set(replay_by_id))
    check("complete_keys_unique", len({row["event_id"] for row in events}) == 5122 and len({row["statement_id"] for row in statements}) == 793)

    derived_sequence_counts: Counter[str] = Counter()
    derived_marker_counts: Counter[str] = Counter()
    derived_slot_counts: Counter[tuple[str, str]] = Counter()
    expected_assignments: list[tuple[object, ...]] = []
    expected_targets: dict[str, str] = {}
    expected_changed: set[str] = set()
    expected_changed_marker_counts: Counter[str] = Counter()
    transformation_errors: list[str] = []
    for source in source_states:
        event_id = source["event_id"]
        sequence = marker_sequence(source["final_context_recipe"])
        sequence_key = "+".join(sequence)
        derived_sequence_counts[sequence_key] += 1
        if replay_by_id[event_id]["state_marker_sequence"] != sequence_key:
            transformation_errors.append(event_id + ":REPLAY_SEQUENCE")
        entry, followers = slots(sequence)
        try:
            target = expected_clause(source["modifier_voice_working_clause_de"], sequence)
        except RuntimeError:
            transformation_errors.append(event_id + ":CLAUSE")
            target = ""
        expected_targets[event_id] = target
        if target != source["modifier_voice_working_clause_de"]:
            expected_changed.add(event_id)
        positions = [index for index, atom in enumerate(source["final_context_recipe"].split("+"), 1) if atom in MARKERS]
        for marker_ordinal, (marker, atom_position) in enumerate(zip(sequence, positions), 1):
            slot = "ENTRY_PREFIX" if entry != "NONE" and marker_ordinal == 1 else "FOLLOWER_SUFFIX"
            phrase = ENTRY[marker] if slot == "ENTRY_PREFIX" else FOLLOWER[marker]
            changed = slot == "FOLLOWER_SUFFIX" and marker in {"OT", "OL"}
            expected_assignments.append((event_id, marker_ordinal, atom_position, marker, slot, phrase, "YES" if changed else "NO"))
            derived_marker_counts[marker] += 1
            derived_slot_counts[(marker, slot)] += 1
            if changed:
                expected_changed_marker_counts[marker] += 1
    check("nine_sequence_counts_exact", derived_sequence_counts == EXPECTED_SEQUENCE_COUNTS, dict(derived_sequence_counts))
    check("marker_counts_exact", derived_marker_counts == Counter({"OL": 761, "DY": 705, "OT": 404}), dict(derived_marker_counts))
    check("slot_counts_exact", derived_slot_counts == Counter({("OL", "ENTRY_PREFIX"): 708, ("DY", "FOLLOWER_SUFFIX"): 705, ("OT", "ENTRY_PREFIX"): 403, ("OL", "FOLLOWER_SUFFIX"): 53, ("OT", "FOLLOWER_SUFFIX"): 1}), {"|".join(k): v for k, v in derived_slot_counts.items()})
    check("transformation_sources_clean", not transformation_errors, transformation_errors[:10])
    check("changed_event_set_size", len(expected_changed) == 54)
    check("changed_marker_counts", expected_changed_marker_counts == Counter({"OL": 53, "OT": 1}), dict(expected_changed_marker_counts))

    actual_assignments = [
        (row["event_id"], int(row["marker_ordinal_in_sequence"]), int(row["recipe_atom_position"]), row["operator"], row["outer_slot"], row["position_realization_de"], row["finite_voice_changed"])
        for row in assignments
    ]
    check("all_1870_assignments_exact", actual_assignments == expected_assignments)
    check("assignment_keys_unique", len({(row["event_id"], row["marker_ordinal_in_sequence"]) for row in assignments}) == 1870)
    check("written_marker_order_preserved", all([row["operator"] for row in assignments if row["event_id"] == event_id] == marker_sequence(source_state_by_id[event_id]["final_context_recipe"]) for event_id in source_state_by_id))

    expected_card_map = {
        "OT": ("DANACH", "Danach", FOLLOWER["OT"], 403, 1, 404, 1),
        "OL": ("FORTSETZEN", "Weiter", FOLLOWER["OL"], 708, 53, 761, 53),
        "DY": ("ABSCHLIESSEN", "NOT_LICENSED", FOLLOWER["DY"], 0, 705, 705, 0),
    }
    card_errors = []
    for row in cards:
        marker = row["operator"]
        observed = (
            row["unchanged_working_value"], row["entry_prefix_realization_de"], row["follower_suffix_realization_de"],
            int(row["entry_assignment_count"]), int(row["follower_assignment_count"]), int(row["total_marker_occurrence_count"]),
            int(row["finite_voice_changed_occurrence_count"]),
        )
        if observed != expected_card_map.get(marker):
            card_errors.append(marker)
    check("three_operator_cards_exact", len(cards) == 3 and not card_errors and {row["operator"] for row in cards} == set(MARKERS), card_errors)
    nonzero_position_cells = sum(int(row["entry_assignment_count"]) > 0 for row in cards) + sum(int(row["follower_assignment_count"]) > 0 for row in cards)
    check("five_position_realizations_exact", nonzero_position_cells == 5, nonzero_position_cells)
    check("two_slot_rules_exact", [(row["outer_slot"], int(row["assignment_count"]), int(row["event_count"])) for row in slot_rules] == [("ENTRY_PREFIX", 1111, 1111), ("FOLLOWER_SUFFIX", 759, 758)])
    check("slot_rule_selectors_exact", slot_rules[0]["selector"] == "FIRST_STATE_MARKER_IF_OT_OR_OL" and slot_rules[1]["selector"] == "EVERY_DY_AND_EVERY_MARKER_AFTER_THE_ENTRY_PREFIX")

    old_profile_by_seq = {row["marker_sequence"]: row for row in old_profiles}
    sequence_errors = []
    for row in sequence_profiles:
        key = row["state_marker_sequence"]
        sequence = key.split("+")
        entry, followers = slots(sequence)
        if (
            int(row["event_count"]) != EXPECTED_SEQUENCE_COUNTS[key]
            or int(row["marker_occurrence_count"]) != EXPECTED_SEQUENCE_COUNTS[key] * len(sequence)
            or row["entry_operator"] != entry
            or row["follower_operator_sequence"] != ("+".join(followers) if followers else "NONE")
            or int(row["event_count"]) != int(old_profile_by_seq[key]["event_count"])
        ):
            sequence_errors.append(key)
    check("nine_sequence_factorizations_exact", len(sequence_profiles) == 9 and not sequence_errors and set(old_profile_by_seq) == {row["state_marker_sequence"] for row in sequence_profiles}, sequence_errors)
    check(
        "no_sequence_specific_card_ids",
        {row["operator_card_id"] for row in cards} == {"GDT571-C01", "GDT571-C02", "GDT571-C03"}
        and all("+" not in row["operator"] for row in cards),
    )

    state_errors = []
    for row in states:
        source = source_state_by_id[row["event_id"]]
        sequence = marker_sequence(source["final_context_recipe"])
        entry, followers = slots(sequence)
        if (
            row["gdt570_modifier_voice_clause_de"] != source["modifier_voice_working_clause_de"]
            or row["outer_voice_working_clause_de"] != expected_targets[row["event_id"]]
            or row["outer_voice_changed"] != ("YES" if row["event_id"] in expected_changed else "NO")
            or row["state_marker_sequence"] != "+".join(sequence)
            or row["entry_operator"] != entry
            or row["follower_operator_sequence"] != ("+".join(followers) if followers else "NONE")
            or row["final_context_recipe"] != source["final_context_recipe"]
            or row["state_atom_alignment"] != source["state_atom_alignment"]
        ):
            state_errors.append(row["event_id"])
    check("all_1656_state_transformations_exact", not state_errors, state_errors[:10])
    check("state_change_partition", Counter(row["outer_voice_changed"] for row in states) == Counter({"NO": 1602, "YES": 54}))
    check("changed_audit_ids_exact", [row["event_id"] for row in changes] == [row["event_id"] for row in states if row["outer_voice_changed"] == "YES"])
    check("changed_sequences_exact", Counter(row["state_marker_sequence"] for row in changes) == Counter({"OT+OL": 38, "OL+OL": 14, "OL+OT": 1, "DY+OL": 1}))
    check("finite_imperative_targets", all(("führe den Gang weiter" in row["after_clause_de"] or "eröffne danach den nächsten Gang" in row["after_clause_de"]) and not row["after_clause_de"].endswith("weiterführen.") and not row["after_clause_de"].endswith("eröffnen.") for row in changes))

    source_event_by_id = {row["event_id"]: row for row in source_events}
    event_errors = []
    nonstate_equal = 0
    for row in events:
        source = source_event_by_id[row["event_id"]]
        target = expected_targets.get(row["event_id"], source["modifier_voice_working_clause_de"])
        if row["gdt570_modifier_voice_clause_de"] != source["modifier_voice_working_clause_de"] or row["outer_voice_working_clause_de"] != target:
            event_errors.append(row["event_id"])
        if row["event_id"] not in expected_targets and row["outer_voice_working_clause_de"] == source["modifier_voice_working_clause_de"]:
            nonstate_equal += 1
    check("all_5122_events_reconstructed", not event_errors, event_errors[:10])
    check("nonstate_byte_unchanged", nonstate_equal == 3466, nonstate_equal)
    check("event_order_exact", [row["event_id"] for row in events] == [row["event_id"] for row in source_events])

    events_by_statement: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in events:
        events_by_statement[row["statement_id"]].append(row)
    source_statement_by_id = {row["statement_id"]: row for row in source_statements}
    statement_errors = []
    changed_statement_ids: set[str] = set()
    for row in statements:
        source = source_statement_by_id[row["statement_id"]]
        local = events_by_statement[row["statement_id"]]
        current = " ".join(event["gdt570_modifier_voice_clause_de"] for event in local)
        target = " ".join(event["outer_voice_working_clause_de"] for event in local)
        changed_count = sum(event["outer_voice_changed"] == "YES" for event in local)
        if changed_count:
            changed_statement_ids.add(row["statement_id"])
        if current != source["modifier_voice_working_reading_de"] or row["gdt570_modifier_voice_reading_de"] != current or row["outer_voice_working_reading_de"] != target or int(row["changed_outer_state_event_count"]) != changed_count or row["event_ids"] != source["event_ids"]:
            statement_errors.append(row["statement_id"])
    check("all_793_statements_reconstructed", not statement_errors, statement_errors[:10])
    check("statement_change_partition", len(changed_statement_ids) == 44 and Counter(row["outer_voice_statement_changed"] for row in statements) == Counter({"NO": 749, "YES": 44}))
    check("statement_order_exact", [row["statement_id"] for row in statements] == [row["statement_id"] for row in source_statements])

    changed_pages = {source_state_by_id[event_id]["physical_page"] for event_id in expected_changed}
    check("page_count_and_order", len(pages) == 30 and [row["physical_page"] for row in pages] == [row["physical_page"] for row in source_pages])
    check("changed_page_count", len(changed_pages) == 24, sorted(changed_pages))
    check("zero_running_pages_retained", {row["physical_page"] for row in pages if int(row["event_count"]) == 0} == {"f69v", "f70v"})
    check("page_marker_total", sum(int(row["state_marker_occurrence_count"]) for row in pages) == 1870)

    expected_metrics = {
        "old_sequence_frame_count": 9,
        "operator_voice_card_count": 3,
        "position_realization_count": 5,
        "outer_slot_rule_count": 2,
        "observed_state_sequence_count": 9,
        "state_marker_occurrence_count": 1870,
        "entry_prefix_assignment_count": 1111,
        "follower_suffix_assignment_count": 759,
        "entryless_state_event_count": 545,
        "single_marker_state_event_count": 1442,
        "multi_marker_state_event_count": 214,
        "finite_follower_changed_occurrence_count": 54,
        "changed_state_event_count": 54,
        "unchanged_state_event_count": 1602,
        "changed_statement_count": 44,
        "unchanged_statement_count": 749,
        "changed_physical_page_count": 24,
        "state_event_count": 1656,
        "nonstate_event_count": 3466,
        "nonstate_byte_unchanged_count": 3466,
        "complete_event_count": 5122,
        "complete_statement_count": 793,
        "complete_page_count": 30,
        "new_pages": 0,
        "new_events": 0,
        "new_statements": 0,
        "new_surfaces": 0,
        "new_recipes": 0,
        "new_root_values": 0,
    }
    check("result_metrics_exact", result.get("metrics") == expected_metrics, result.get("metrics"))
    check("result_status_exact", result.get("status") == STATUS, result.get("status"))
    check("input_hashes_exact", result.get("input_sha256") == {name: sha256(path) for name, path in INPUTS.items()})
    book = ARTIFACTS["book"].read_text(encoding="utf-8")
    check("book_metrics_present", "Events: 5122 · statements: 793 · pages: 30 · changed state clauses: 54." in book)
    check("book_all_pages_once", all(book.count(f"## {row['physical_page']}\n") == 1 for row in pages))
    check("book_all_statements", sum(line[:1].isdigit() and ". " in line for line in book.splitlines()) == 793)

    pre_hashes = {name: sha256(path) for name, path in ARTIFACTS.items() if name != "result"}
    run = subprocess.run(
        ["python3", str(BASE / "src/run.py")],
        cwd=ROOT,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        check=False,
    )
    post_hashes = {name: sha256(path) for name, path in ARTIFACTS.items() if name != "result"}
    check("deterministic_replay_exit", run.returncode == 0, run.stderr[-1000:])
    check("deterministic_artifact_hashes", pre_hashes == post_hashes, {name: (pre_hashes[name], post_hashes[name]) for name in pre_hashes if pre_hashes[name] != post_hashes[name]})
    rerun_result = json.loads(ARTIFACTS["result"].read_text(encoding="utf-8"))
    check("deterministic_result_object", rerun_result == result)

    failed = [row for row in checks if not row["passed"]]
    validation = {
        "status": "PASS" if not failed else "FAIL",
        "check_count": len(checks),
        "passed_count": len(checks) - len(failed),
        "failed_count": len(failed),
        "input_sha256": {name: sha256(path) for name, path in INPUTS.items()},
        "artifact_sha256": {name: sha256(path) for name, path in ARTIFACTS.items()},
        "checks": checks,
    }
    (OUT / "gdt571_validation.json").write_text(json.dumps(validation, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(validation, ensure_ascii=False, indent=2))
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
