#!/usr/bin/env python3
"""Independently validate the GDT566 complete working prose edition."""

from __future__ import annotations

import csv
import hashlib
import json
import subprocess
import sys
from collections import Counter, defaultdict
from pathlib import Path


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
BASE = ROOT / "experiments/yolo/gdt566_complete_thirty_page_prose_working_edition"
OUT = BASE / "artifacts"
RUNNER = BASE / "src/run.py"
VALIDATION_OUT = OUT / "gdt566_validation.json"
G515 = ROOT / "experiments/yolo/gdt515_second_random_four_page_full_admission/artifacts"
G416 = ROOT / "experiments/yolo/gdt416_owner_local_imperative_sentence_compiler/artifacts"
G539 = ROOT / "experiments/yolo/gdt539_four_page_contextual_statement_edition/artifacts"
G565 = ROOT / "experiments/yolo/gdt565_state_microphrase_template_generator/artifacts"
INPUTS = {
    "navigation_events": G515 / "gdt515_5122_running_event_edition.tsv",
    "page_summary": G515 / "gdt515_30_page_summary.tsv",
    "old_clauses": G416 / "gdt416_4576_imperative_clauses.tsv",
    "old_statements": G416 / "gdt416_715_imperative_statements.tsv",
    "current_clauses": G539 / "gdt539_546_contextual_prose_events.tsv",
    "current_statements": G539 / "gdt539_78_contextual_statements.tsv",
    "state_generator": G565 / "gdt565_1656_template_replay.tsv",
}
ARTIFACTS = {
    "events": OUT / "gdt566_5122_complete_prose_event_edition.tsv",
    "statements": OUT / "gdt566_793_complete_statement_edition.tsv",
    "pages": OUT / "gdt566_30_page_edition_profiles.tsv",
    "modes": OUT / "gdt566_3_statement_mode_profiles.tsv",
    "layers": OUT / "gdt566_3_reading_layer_profiles.tsv",
    "repairs": OUT / "gdt566_10_later_context_recipe_repairs.tsv",
    "book": OUT / "GDT566_COMPLETE_THIRTY_PAGE_PROSE_EDITION.md",
    "result": OUT / "gdt566_result.json",
}
STATUS = (
    "PASS_COMPLETE_5122_EVENT__793_STATEMENT__30_PAGE_WORKING_EDITION__"
    "1656_GENERATED_STATE__3466_OWNER_CONTEXT_NONSTATE__ZERO_REST"
)


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    checks: list[dict[str, object]] = []

    def check(name: str, passed: bool, detail: object = None) -> None:
        checks.append({"check": name, "passed": bool(passed), "detail": detail})

    navigation = read_tsv(INPUTS["navigation_events"])
    page_source = read_tsv(INPUTS["page_summary"])
    old_clauses = read_tsv(INPUTS["old_clauses"])
    old_statements = read_tsv(INPUTS["old_statements"])
    current_clauses = read_tsv(INPUTS["current_clauses"])
    current_statements = read_tsv(INPUTS["current_statements"])
    state_source = read_tsv(INPUTS["state_generator"])
    events = read_tsv(ARTIFACTS["events"])
    statements = read_tsv(ARTIFACTS["statements"])
    pages = read_tsv(ARTIFACTS["pages"])
    modes = read_tsv(ARTIFACTS["modes"])
    layers = read_tsv(ARTIFACTS["layers"])
    repairs = read_tsv(ARTIFACTS["repairs"])
    result = json.loads(ARTIFACTS["result"].read_text(encoding="utf-8"))

    input_counts = [len(navigation), len(page_source), len(old_clauses), len(old_statements),
                    len(current_clauses), len(current_statements), len(state_source)]
    check("input_counts_exact", input_counts == [5122, 30, 4576, 715, 546, 78, 1656], input_counts)
    artifact_counts = [len(events), len(statements), len(pages), len(modes), len(layers), len(repairs)]
    check("artifact_counts_exact", artifact_counts == [5122, 793, 30, 3, 3, 10], artifact_counts)
    all_pages = ({row["physical_page"] for row in navigation} |
                 {row["physical_page"] for row in page_source} |
                 {row["physical_page"] for row in events} |
                 {row["physical_page"] for row in statements} |
                 {row["physical_page"] for row in state_source})
    check("sealed_pages_absent", not all_pages.intersection({"f84", "f84r"}), sorted(all_pages.intersection({"f84", "f84r"})))
    check("navigation_ordinals_exact", [int(row["global_running_ordinal"]) for row in navigation] == list(range(1, 5123)))
    check("edition_event_ordinals_exact", [int(row["edition_event_ordinal"]) for row in events] == list(range(1, 5123)))
    check("edition_statement_ordinals_exact", [int(row["edition_statement_ordinal"]) for row in statements] == list(range(1, 794)))
    check("page_ordinals_exact", [int(row["page_ordinal"]) for row in pages] == list(range(1, 31)))

    old_by_id = {row["global_running_event_id"]: row for row in old_clauses}
    current_by_id = {row["event_id"]: row for row in current_clauses}
    state_by_id = {row["event_id"]: row for row in state_source}
    events_by_id = {row["event_id"]: row for row in events}
    old_statement_by_id = {row["global_statement_id"]: row for row in old_statements}
    current_statement_by_id = {row["statement_id"]: row for row in current_statements}
    statements_by_id = {row["statement_id"]: row for row in statements}
    check("all_input_keys_unique", [len(old_by_id), len(current_by_id), len(state_by_id), len(old_statement_by_id), len(current_statement_by_id)] == [4576, 546, 1656, 715, 78], [len(old_by_id), len(current_by_id), len(state_by_id), len(old_statement_by_id), len(current_statement_by_id)])
    check("edition_keys_unique", len(events_by_id) == 5122 and len(statements_by_id) == 793, [len(events_by_id), len(statements_by_id)])

    navigation_errors = []
    source_errors = []
    expected_event_ids = []
    expected_statement_ids = []
    expected_repairs = []
    expected_cohorts = Counter()
    for nav, event in zip(navigation, events):
        nav_id = nav["global_running_event_id"]
        if nav_id in old_by_id:
            source = old_by_id[nav_id]
            event_id = nav_id
            cohort = "OLD26_GDT416"
            statement_id = source["global_statement_id"]
            final_recipe = source["component_recipe"]
            owner_id = source["owner_de"]
            owner_class = source["owner_class"]
            owner_clause = source["imperative_clause_de"]
            trace = source["portable_back_projection_de"]
            layer = "GDT416_OWNER_CONTEXT"
            roundtrip = source["roundtrip_exact"]
        else:
            event_id = nav["source_event_id"]
            source = current_by_id.get(event_id)
            if source is None:
                navigation_errors.append((nav_id, "missing current source"))
                continue
            cohort = "CURRENT4_GDT539"
            statement_id = source["statement_id"]
            final_recipe = source["final_context_recipe"]
            owner_id = source["owner_id"]
            owner_class = source["content_role"]
            owner_clause = source["contextual_clause_de"]
            trace = source["controlled_order_reading_de"]
            layer = "GDT539_OWNER_CONTEXT"
            roundtrip = "YES" if source["exact_recipe_roundtrip"] == final_recipe else "NO"
        expected_event_ids.append(event_id)
        if statement_id not in expected_statement_ids:
            expected_statement_ids.append(statement_id)
        expected_cohorts[cohort] += 1
        navigation_fields = {
            "navigation_event_id": nav_id,
            "event_id": event_id,
            "cohort": cohort,
            "statement_id": statement_id,
            "physical_page": nav["physical_page"],
            "register": nav["register"],
            "locus": nav["locus"],
            "surface": nav["surface"],
            "gdt515_navigation_recipe": nav["component_recipe"],
        }
        bad = {key: [event[key], value] for key, value in navigation_fields.items() if event[key] != value}
        if bad:
            navigation_errors.append((event_id, bad))
        source_fields = {
            "owner_class_or_role": owner_class,
            "owner_id": owner_id,
            "owner_de": source["owner_de"],
            "final_context_recipe": final_recipe,
            "portable_or_controlled_trace_de": trace,
            "owner_bound_control_clause_de": owner_clause,
            "source_context_layer": layer,
            "source_recipe_roundtrip": roundtrip,
        }
        bad = {key: [event[key], value] for key, value in source_fields.items() if event[key] != value}
        if bad:
            source_errors.append((event_id, bad))
        relation = "SAME" if nav["component_recipe"] == final_recipe else "LATER_CONTEXT_REPAIR"
        if event["recipe_relation_to_gdt515"] != relation:
            source_errors.append((event_id, "recipe relation"))
        if relation == "LATER_CONTEXT_REPAIR":
            expected_repairs.append(event_id)

    check("navigation_identity_exact", not navigation_errors, navigation_errors[:5])
    check("source_context_fields_exact", not source_errors, source_errors[:5])
    check("event_id_order_exact", [row["event_id"] for row in events] == expected_event_ids)
    check("statement_id_order_exact", [row["statement_id"] for row in statements] == expected_statement_ids)
    check("cohort_partition_exact", expected_cohorts == Counter({"OLD26_GDT416": 4576, "CURRENT4_GDT539": 546}), dict(expected_cohorts))
    check("all_source_events_used_once", set(expected_event_ids) == set(old_by_id) | set(current_by_id) and len(expected_event_ids) == len(set(expected_event_ids)))

    state_errors = []
    nonstate_errors = []
    for event_id, event in events_by_id.items():
        state = state_by_id.get(event_id)
        if state is not None:
            expected = {
                "state_status": "STATE_CARD",
                "selected_reading_layer": "GDT565_STATE_GENERATOR",
                "state_replay_status": state["replay_status"],
                "outer_template_id": state["outer_template_id"],
                "structural_template_id": state["structural_template_id"],
                "selected_working_clause_de": state["generated_microphrase_de"],
                "state_atom_alignment": state["written_atom_alignment"],
                "final_context_recipe": state["recipe"],
                "selected_equals_owner_bound": "NO",
            }
            bad = {key: [event[key], value] for key, value in expected.items() if event[key] != value}
            if bad:
                state_errors.append((event_id, bad))
        else:
            expected_layer = "GDT416_OWNER_CONTEXT_NONSTATE" if event["cohort"] == "OLD26_GDT416" else "GDT539_OWNER_CONTEXT_NONSTATE"
            expected = {
                "state_status": "NONSTATE_CARD",
                "selected_reading_layer": expected_layer,
                "state_replay_status": "NOT_APPLICABLE",
                "outer_template_id": "NOT_APPLICABLE",
                "structural_template_id": "NOT_APPLICABLE",
                "selected_working_clause_de": event["owner_bound_control_clause_de"],
                "state_atom_alignment": "NOT_APPLICABLE",
                "selected_equals_owner_bound": "YES",
            }
            bad = {key: [event[key], value] for key, value in expected.items() if event[key] != value}
            if bad:
                nonstate_errors.append((event_id, bad))
    check("state_partition_exact", {row["event_id"] for row in events if row["state_status"] == "STATE_CARD"} == set(state_by_id), len(state_by_id))
    check("all_state_generator_fields_exact", not state_errors, state_errors[:5])
    check("all_nonstate_clauses_unchanged", not nonstate_errors, nonstate_errors[:5])
    check("selected_owner_equality_partition", Counter(row["selected_equals_owner_bound"] for row in events) == Counter({"YES": 3466, "NO": 1656}), dict(Counter(row["selected_equals_owner_bound"] for row in events)))
    normalizations = [row["event_id"] for row in events if row["state_replay_status"] == "EDITORIAL_DOUBLE_ARGUMENT_NORMALIZATION"]
    check("single_named_normalization", normalizations == ["G407-E1000"], normalizations)

    repair_artifact_ids = [row["event_id"] for row in repairs]
    named_repairs = ["G515-E0182", "G515-E0243", "G515-E0253", "G515-E0364", "G515-E0366", "G515-E0410", "G515-E0423", "G515-E0426", "G515-E0437", "G515-E0438"]
    check("ten_later_recipe_repairs_exact", expected_repairs == repair_artifact_ids and expected_repairs == named_repairs, expected_repairs)
    repair_errors = []
    for repair, event_id in zip(repairs, expected_repairs):
        event = events_by_id[event_id]
        expected = {
            "physical_page": event["physical_page"], "surface": event["surface"],
            "gdt515_navigation_recipe": event["gdt515_navigation_recipe"],
            "final_context_recipe": event["final_context_recipe"], "state_status": event["state_status"],
            "selected_reading_layer": event["selected_reading_layer"],
            "repair_status": "EXPLICIT_LATER_CONTEXT_RECIPE_RETAINED",
        }
        bad = {key: [repair[key], value] for key, value in expected.items() if repair[key] != value}
        if bad:
            repair_errors.append((event_id, bad))
    check("recipe_repair_deck_exact", not repair_errors and [int(row["repair_ordinal"]) for row in repairs] == list(range(1, 11)), repair_errors)

    grouped_events: dict[str, list[dict[str, str]]] = defaultdict(list)
    for event in events:
        grouped_events[event["statement_id"]].append(event)
    statement_errors = []
    expected_modes = Counter()
    for statement in statements:
        members = sorted(grouped_events[statement["statement_id"]], key=lambda row: int(row["card_ordinal_in_statement"]))
        source = old_statement_by_id.get(statement["statement_id"]) or current_statement_by_id.get(statement["statement_id"])
        if source is None:
            statement_errors.append((statement["statement_id"], "missing source"))
            continue
        owner_expected = source.get("imperative_reading_de", source.get("contextual_working_reading_de", ""))
        selected = " ".join(row["selected_working_clause_de"] for row in members)
        owner = " ".join(row["owner_bound_control_clause_de"] for row in members)
        state_count = sum(row["state_status"] == "STATE_CARD" for row in members)
        mode = "ALL_STATE" if state_count == len(members) else "NO_STATE" if state_count == 0 else "MIXED_STATE_AND_NONSTATE"
        expected_modes[mode] += 1
        expected = {
            "event_count": str(len(members)), "state_card_count": str(state_count),
            "nonstate_card_count": str(len(members) - state_count), "statement_mode": mode,
            "event_ids": "|".join(row["event_id"] for row in members),
            "surface_sequence": " ".join(row["surface"] for row in members),
            "final_recipe_sequence": " | ".join(row["final_context_recipe"] for row in members),
            "selected_layer_sequence": "|".join(row["selected_reading_layer"] for row in members),
            "selected_working_reading_de": selected,
            "owner_bound_control_reading_de": owner,
            "owner_bound_source_statement_de": owner_expected,
            "owner_bound_source_byte_exact": "YES",
            "selected_equals_owner_bound": "YES" if selected == owner else "NO",
            "end_mode": source["end_mode"],
        }
        bad = {key: [statement[key], value] for key, value in expected.items() if statement[key] != value}
        if owner != owner_expected:
            bad["source_reconstruction"] = [owner, owner_expected]
        if bad:
            statement_errors.append((statement["statement_id"], bad))
    check("all_793_statements_reconstructed", not statement_errors, statement_errors[:3])
    check("all_source_statements_used_once", set(statements_by_id) == set(old_statement_by_id) | set(current_statement_by_id))
    check("statement_mode_partition", expected_modes == Counter({"MIXED_STATE_AND_NONSTATE": 528, "ALL_STATE": 247, "NO_STATE": 18}), dict(expected_modes))
    check("state_touched_statements", sum(int(row["state_card_count"]) > 0 for row in statements) == 775)
    check("statement_event_totals", sum(int(row["event_count"]) for row in statements) == 5122 and sum(int(row["state_card_count"]) for row in statements) == 1656 and sum(int(row["nonstate_card_count"]) for row in statements) == 3466)

    source_pages = {row["physical_page"]: row for row in page_source}
    page_errors = []
    for page in pages:
        source = source_pages.get(page["physical_page"])
        members = [row for row in events if row["physical_page"] == page["physical_page"]]
        page_statements = [row for row in statements if row["physical_page"] == page["physical_page"]]
        if source is None:
            page_errors.append((page["physical_page"], "missing source"))
            continue
        expected = {
            "registers": source["registers"],
            "source_running_event_count": source["running_event_count"],
            "edition_event_count": str(len(members)),
            "source_statement_count": source["statement_count"],
            "edition_statement_count": str(len(page_statements)),
            "state_card_count": str(sum(row["state_status"] == "STATE_CARD" for row in members)),
            "nonstate_card_count": str(sum(row["state_status"] == "NONSTATE_CARD" for row in members)),
            "all_state_statement_count": str(sum(row["statement_mode"] == "ALL_STATE" for row in page_statements)),
            "mixed_statement_count": str(sum(row["statement_mode"] == "MIXED_STATE_AND_NONSTATE" for row in page_statements)),
            "no_state_statement_count": str(sum(row["statement_mode"] == "NO_STATE" for row in page_statements)),
            "normalized_state_card_count": str(sum(row["state_replay_status"] == "EDITORIAL_DOUBLE_ARGUMENT_NORMALIZATION" for row in members)),
            "recipe_repair_count_after_gdt515": str(sum(row["recipe_relation_to_gdt515"] == "LATER_CONTEXT_REPAIR" for row in members)),
            "page_status": "COMPLETE_RUNNING_PAGE" if members else "ZERO_RUNNING_EVENT_PAGE_RETAINED",
            "count_parity": "YES",
        }
        bad = {key: [page[key], value] for key, value in expected.items() if page[key] != value}
        if bad:
            page_errors.append((page["physical_page"], bad))
    check("all_30_page_profiles_exact", not page_errors and set(source_pages) == {row["physical_page"] for row in pages}, page_errors[:3])
    zero_pages = [row["physical_page"] for row in pages if int(row["edition_event_count"]) == 0]
    check("two_zero_running_pages_retained", zero_pages == ["f69v", "f70v"], zero_pages)
    check("running_page_partition", sum(int(row["edition_event_count"]) > 0 for row in pages) == 28 and sum(int(row["edition_event_count"]) == 0 for row in pages) == 2)

    expected_mode_profiles = {
        "ALL_STATE": (247, 280, 280, 0),
        "MIXED_STATE_AND_NONSTATE": (528, 4768, 1376, 3392),
        "NO_STATE": (18, 74, 0, 74),
    }
    mode_lookup = {row["statement_mode"]: row for row in modes}
    mode_fields = ("statement_count", "event_count", "state_card_count", "nonstate_card_count")
    check("mode_profiles_exact", set(mode_lookup) == set(expected_mode_profiles) and all(tuple(int(mode_lookup[key][field]) for field in mode_fields) == value for key, value in expected_mode_profiles.items()), mode_lookup)
    layer_counts = Counter(row["selected_reading_layer"] for row in events)
    layer_lookup = {row["selected_reading_layer"]: row for row in layers}
    expected_layers = Counter({"GDT565_STATE_GENERATOR": 1656, "GDT416_OWNER_CONTEXT_NONSTATE": 3082, "GDT539_OWNER_CONTEXT_NONSTATE": 384})
    check("layer_profiles_exact", layer_counts == expected_layers and set(layer_lookup) == set(layer_counts) and all(int(layer_lookup[key]["event_count"]) == value for key, value in layer_counts.items()), [dict(layer_counts), layer_lookup])
    check("all_selected_and_control_clauses_nonempty", all(row["selected_working_clause_de"] and row["owner_bound_control_clause_de"] for row in events))
    check("all_event_guards_exact", {row["guard"] for row in events} == {"COMPLETE_PROSE_EVENT__SELECTED_AND_OWNER_BOUND_CHANNELS_DISTINCT"})
    check("all_statement_guards_exact", {row["guard"] for row in statements} == {"COMPLETE_STATEMENT__GENERATOR_AND_OWNER_CONTEXT_CHANNELS_RETAINED"})

    expected_result = {
        "admitted_page_count": 30, "running_page_count": 28, "zero_running_page_count": 2,
        "complete_event_count": 5122, "complete_statement_count": 793,
        "state_generator_event_count": 1656, "nonstate_owner_context_event_count": 3466,
        "old_nonstate_event_count": 3082, "current_nonstate_event_count": 384,
        "all_state_statement_count": 247, "mixed_statement_count": 528, "no_state_statement_count": 18,
        "state_touched_statement_count": 775, "owner_bound_statement_byte_exact_count": 793,
        "selected_clause_equals_owner_bound_count": 3466, "selected_clause_differs_owner_bound_count": 1656,
        "gdt565_editorial_normalization_count": 1, "later_context_recipe_repair_count": 10,
        "new_pages": 0, "new_events": 0, "new_statements": 0, "new_surfaces": 0, "new_root_values": 0,
    }
    check("result_metrics_exact", all(result.get(key) == value for key, value in expected_result.items()), {key: result.get(key) for key in expected_result})
    check("result_status_exact", result.get("status") == STATUS, result.get("status"))
    boolean_keys = ("all_events_have_selected_clause", "all_events_have_owner_bound_control", "all_page_counts_match_gdt515")
    check("result_boolean_guards", all(result.get(key) is True for key in boolean_keys), {key: result.get(key) for key in boolean_keys})
    check("input_hashes_exact", result.get("input_sha256") == {name: sha256(path) for name, path in INPUTS.items()}, result.get("input_sha256"))

    book = ARTIFACTS["book"].read_text(encoding="utf-8")
    headings = [line[3:] for line in book.splitlines() if line.startswith("## ")]
    needles = ("5.122 laufenden Karten", "793 Aussagen", "1.656 GDT565-Zustandskarten", "3.082 alte", "384 aktuelle")
    check("book_core_metrics_present", all(needle in book for needle in needles), [needle for needle in needles if needle not in book])
    check("book_contains_all_pages_once", headings == [row["physical_page"] for row in pages], headings)
    check("book_retains_zero_page_notice", book.count("reine Lokalregisterseite") == 2, book.count("reine Lokalregisterseite"))
    check("book_contains_all_statement_ids", all(statement_id in book for statement_id in statements_by_id))

    before = {name: sha256(path) for name, path in ARTIFACTS.items()}
    replay = subprocess.run([sys.executable, str(RUNNER)], cwd=ROOT, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
    after = {name: sha256(path) for name, path in ARTIFACTS.items()}
    check("deterministic_replay_exit", replay.returncode == 0, replay.stderr)
    check("deterministic_artifact_hashes", before == after, {name: [before[name], after[name]] for name in before if before[name] != after[name]})

    payload = {
        "status": "PASS" if all(item["passed"] for item in checks) else "FAIL",
        "check_count": len(checks),
        "passed_count": sum(item["passed"] for item in checks),
        "failed_count": sum(not item["passed"] for item in checks),
        "input_sha256": {name: sha256(path) for name, path in INPUTS.items()},
        "artifact_sha256": {name: sha256(path) for name, path in ARTIFACTS.items()},
        "checks": checks,
    }
    VALIDATION_OUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0 if payload["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
