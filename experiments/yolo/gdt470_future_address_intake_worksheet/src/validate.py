#!/usr/bin/env python3
"""Validate GDT470 and verify a byte-identical deterministic rebuild."""

from __future__ import annotations

import csv
import hashlib
import json
import subprocess
import sys
from collections import Counter
from pathlib import Path

sys.dont_write_bytecode = True


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
BASE = ROOT / "experiments/yolo/gdt470_future_address_intake_worksheet"
OUT = BASE / "artifacts"
RUN = BASE / "src/run.py"
PREPARE = BASE / "src/prepare_future_address.py"
G466 = ROOT / "experiments/yolo/gdt466_future_address_mixed_dictionary_intake"

REPLAY = OUT / "gdt470_89_supported_unseen_core_replay.tsv"
CONTENT = OUT / "gdt470_4_content_class_stability.tsv"
SHAPES = OUT / "gdt470_11_shell_shape_stability.tsv"
DECISIONS = OUT / "gdt470_7_intake_decision_catalog.tsv"
SLOTS = OUT / "gdt470_four_page_address_slots.tsv"
TEMPLATE = OUT / "gdt470_address_item_template.tsv"
CONTRACT = OUT / "gdt470_future_address_intake_contract.json"
RESULT = OUT / "gdt470_result.json"
VALIDATION = OUT / "gdt470_validation.json"
GENERATED = (REPLAY, CONTENT, SHAPES, DECISIONS, SLOTS, TEMPLATE, CONTRACT, RESULT)

sys.path.insert(0, str(BASE / "src"))
from worksheet_lib import WORKSHEET_FIELDS  # noqa: E402


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def tsv_fields(path: Path) -> list[str]:
    with path.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle, delimiter="\t")
        return list(reader.fieldnames or [])


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def cli(*args: str) -> tuple[int, dict[str, object], str]:
    completed = subprocess.run(
        [sys.executable, str(PREPARE), *args],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    return (
        completed.returncode,
        json.loads(completed.stdout) if completed.stdout else {},
        completed.stderr,
    )


def main() -> int:
    checks: list[dict[str, object]] = []

    def check(name: str, condition: bool, detail: str) -> None:
        checks.append({"name": name, "status": "PASS" if condition else "FAIL", "detail": detail})

    source = read_tsv(G466 / "artifacts/gdt466_89_unseen_core_insertion_probes.tsv")
    labels = read_tsv(G466 / "artifacts/gdt466_107_intake_dictionary.tsv")
    replay = read_tsv(REPLAY)
    content = read_tsv(CONTENT)
    shapes = read_tsv(SHAPES)
    decisions = read_tsv(DECISIONS)
    slots = read_tsv(SLOTS)
    template = read_tsv(TEMPLATE)
    contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
    result = json.loads(RESULT.read_text(encoding="utf-8"))

    check("source_count", len(source) == 89, f"observed={len(source)}")
    check("source_all_pass", all(row["probe_pass"] == "YES" for row in source), "89/89")
    check("source_exact_cards_hidden", all(row["exact_known_route_blocked"] == "YES" for row in source), "89/89")
    mutation_ok = all(
        row["synthetic_unseen_surface"]
        == row["source_surface"][: int(row["insertion_index"])] + "x" + row["source_surface"][int(row["insertion_index"]):]
        for row in source
    )
    check("source_mutation_is_one_inserted_x", mutation_ok, "89/89")
    known_surfaces = {row["surface"] for row in labels}
    check("synthetic_forms_are_unseen", all(row["synthetic_unseen_surface"] not in known_surfaces for row in source), "89/89")

    check("replay_count", len(replay) == 89, f"observed={len(replay)}")
    check("replay_source_order", [row["source_probe_id"] for row in replay] == [row["probe_id"] for row in source], "source order exact")
    check("replay_surface_alignment", [row["synthetic_unseen_surface"] for row in replay] == [row["synthetic_unseen_surface"] for row in source], "89 exact")
    check("replay_content_alignment", [row["content_class"] for row in replay] == [row["content_class"] for row in source], "89 exact")
    check("replay_masks", all(row["expected_function_mask"] == row["observed_function_mask"] for row in replay), "89/89")
    check("routes_unchanged", all(row["observed_route"] == old["observed_route"] for row, old in zip(replay, source)), "89/89")
    check("readings_unchanged", all(row["observed_reading_de"] == old["observed_reading_de"] for row, old in zip(replay, source)), "89/89")
    check("channel_signatures_stable", all(row["signature_stable"] == "YES" and row["source_channel_signature"] == row["observed_channel_signature"] for row in replay), "89/89")
    check("ordered_recipes_stable", all(row["recipe_stable"] == "YES" and row["source_ordered_recipe_trace"] == row["observed_ordered_recipe_trace"] for row in replay), "89/89")
    check("tiers_and_ranks_stable", all(row["tier_and_rank_stable"] == "YES" and row["source_recipe_support_tier"] == row["observed_recipe_support_tier"] and row["source_recipe_support_rank"] == row["observed_recipe_support_rank"] for row in replay), "89/89")
    check("shell_ids_stable", all(row["shell_id_stable"] == "YES" and row["source_bounded_shell_id"] == row["observed_bounded_shell_id"] for row in replay), "89/89")
    check("working_readings_stable", all(row["reading_stable"] == "YES" for row in replay), "89/89")
    check("all_replay_pass", all(row["replay_pass"] == "YES" for row in replay), "89/89")

    routes = Counter(row["observed_route"] for row in replay)
    tiers = Counter(row["observed_recipe_support_tier"] for row in replay)
    classes = Counter(row["content_class"] for row in replay)
    shape_counts = Counter(row["shell_shape"] for row in replay)
    check("route_counts", routes == Counter({"CALIBRATED_FUNCTION_SHELL_PLUS_LEARNED_CORE": 87, "WHOLE_LEARNED_OWNER_NAME": 2}), str(routes))
    check("tier_counts", tiers == Counter({"OUTSIDE_BOUNDED_SHELL_ATLAS": 47, "RUNNING_EXACT_RECIPE": 25, "ADDRESS_HYBRID_SHELL_ONLY": 16, "ADDRESS_FULL_FORMULA_ONLY": 1}), str(tiers))
    check("no_composition_only_in_label_derived_probe_set", tiers["COMPOSITION_ONLY"] == 0, str(tiers))
    check("content_class_counts", classes == Counter({"STAR_BEARING_RING_POSITION": 52, "DRUG_OR_INGREDIENT_OBJECT": 30, "BATH_OR_OUTLET_STATION": 5, "PICTURED_PLANT": 2}), str(classes))
    expected_shapes = Counter({
        "SUFFIX": 24,
        "PREFIX": 17,
        "PREFIX+SUFFIX": 10,
        "INTERNAL+SUFFIX": 8,
        "PREFIX+INTERNAL": 8,
        "PREFIX+INTERNAL+SUFFIX": 7,
        "INTERNAL": 5,
        "INTERNAL+INTERNAL": 4,
        "INTERNAL+INTERNAL+SUFFIX": 2,
        "NONE": 2,
        "PREFIX+INTERNAL+INTERNAL": 2,
    })
    check("shape_counts", shape_counts == expected_shapes, str(shape_counts))
    check("shape_count", len(shape_counts) == 11, f"observed={len(shape_counts)}")
    bounded = [row for row in replay if row["bounded_shell_match"] == "YES"]
    check("bounded_match_count", len(bounded) == 17, f"observed={len(bounded)}")
    check("bounded_match_shapes", all(row["shell_shape"] in {"PREFIX+SUFFIX", "PREFIX+INTERNAL+SUFFIX"} for row in bounded), "17/17")
    check("all_two_bounded_shapes_match", all(row["bounded_shell_match"] == "YES" for row in replay if row["shell_shape"] in {"PREFIX+SUFFIX", "PREFIX+INTERNAL+SUFFIX"}), "17/17")
    old_carrier_tiers = {"RUNNING_EXACT_RECIPE", "ADDRESS_FULL_FORMULA_ONLY", "ADDRESS_HYBRID_SHELL_ONLY"}
    check("old_carrier_backed_count", sum(row["observed_recipe_support_tier"] in old_carrier_tiers for row in replay) == 42, "42/89")
    check("all_bounded_matches_have_old_carrier", all(row["observed_recipe_support_tier"] in old_carrier_tiers for row in bounded), "17/17")

    expected_content = {
        "BATH_OR_OUTLET_STATION": (5, 0, 0, 1, 4, 1, 0),
        "DRUG_OR_INGREDIENT_OBJECT": (30, 9, 0, 5, 16, 14, 5),
        "PICTURED_PLANT": (2, 0, 0, 0, 2, 0, 0),
        "STAR_BEARING_RING_POSITION": (52, 16, 1, 10, 25, 27, 12),
    }
    content_tuples = {
        row["content_class"]: tuple(int(row[key]) for key in (
            "probe_count",
            "running_exact_recipe_count",
            "address_full_formula_only_count",
            "address_hybrid_shell_only_count",
            "outside_bounded_shell_atlas_count",
            "old_carrier_backed_count",
            "bounded_shell_match_count",
        ))
        for row in content
    }
    check("content_summary_count", len(content) == 4, f"observed={len(content)}")
    check("content_summary_values", content_tuples == expected_content, str(content_tuples))
    check("content_summary_no_composition", all(int(row["composition_only_count"]) == 0 for row in content), "4/4")
    check("content_summary_stability", all(int(row["all_five_invariants_stable_count"]) == int(row["probe_count"]) == int(row["replay_pass_count"]) for row in content), "4/4")

    check("shape_summary_count", len(shapes) == 11, f"observed={len(shapes)}")
    check("shape_summary_values", {row["shell_shape"]: int(row["probe_count"]) for row in shapes} == dict(expected_shapes), "all 11 shapes")
    check("shape_summary_no_composition", all(int(row["composition_only_count"]) == 0 for row in shapes), "11/11")
    check("shape_summary_stability", all(int(row["all_five_invariants_stable_count"]) == int(row["probe_count"]) == int(row["replay_pass_count"]) for row in shapes), "11/11")
    check("shape_summary_totals", sum(int(row["probe_count"]) for row in shapes) == 89 and sum(int(row["bounded_shell_match_count"]) for row in shapes) == 17, "89 probes; 17 bounded")

    check("decision_count", len(decisions) == 7, f"observed={len(decisions)}")
    check("decision_priorities", [int(row["priority"]) for row in decisions] == list(range(1, 8)), "1..7")
    check("decision_actions_unique", len({row["default_action"] for row in decisions}) == 7, "7/7")
    check("decision_default_complete", all(row["default_action"] and row["meaning_policy"] for row in decisions), "7/7")

    check("page_slot_count", len(slots) == 4, f"observed={len(slots)}")
    check("page_slots_named", [row["page_slot"] for row in slots] == [f"PAGE_SLOT_{index}" for index in range(1, 5)], "four ordered slots")
    check("page_slots_unreleased", all(row["release_status"] == "UNRELEASED" and row["page_id"] == "PENDING_USER_RELEASE" for row in slots), "4/4")
    check("template_empty", template == [], f"rows={len(template)}")
    check("template_schema", tsv_fields(TEMPLATE) == WORKSHEET_FIELDS, f"columns={len(tsv_fields(TEMPLATE))}")

    check("contract_status", contract["status"] == "FUTURE_ADDRESS_INTAKE_WORKSHEET_READY", contract["status"])
    check("contract_slots", contract["page_slots"] == 4 and contract["page_slot_state"] == "UNRELEASED", str(contract))
    check("contract_defaults_every_sequence", contract["all_visible_sequences_receive_a_default"] is True and contract["opaque_default_form"] == "[OWNER_CLASS_NAME:VISIBLE_REMAINDER]", str(contract))
    check("contract_provenance_annotation_only", contract["provenance_is_annotation_only"] is True, str(contract))
    check("contract_manual_capture", len(contract["required_manual_capture"]) == 6, str(contract["required_manual_capture"]))

    code, payload, error = cli(
        "otxainy",
        "STAR_BEARING_RING_POSITION",
        "--page-slot",
        "PAGE_SLOT_1",
        "--item-slot",
        "ITEM_001",
        "--zl3b",
        "otxainy",
        "--rf1b",
        "otxainy",
    )
    check("cli_supported_exit", code == 0, error or "exit 0")
    check("cli_supported_reading", payload.get("working_reading_de") == "DANACH · [STERNSTELLENNAME:x] · ANTEIL · POSTEN", str(payload))
    check("cli_supported_provenance", payload.get("bounded_shell_id") == "G467-S0234" and payload.get("recipe_support_tier") == "ADDRESS_FULL_FORMULA_ONLY" and payload.get("recipe_support_rank") == 86, str(payload))
    check("cli_supported_action", payload.get("intake_action") == "READ_SUPPORTED_FUNCTION_SHELL_KEEP_NAME_CORE" and payload.get("transcription_agreement") == "SUPPLIED_READINGS_AGREE", str(payload))
    code, payload, error = cli("zxqv", "PICTURED_PLANT")
    check("cli_whole_name_exit", code == 0, error or "exit 0")
    check("cli_whole_name_default", payload.get("working_reading_de") == "[PFLANZENNAME:zxqv]" and payload.get("intake_action") == "LEARN_WHOLE_OWNER_BOUND_NAME", str(payload))
    code, payload, error = cli("oiil", "PICTURED_PLANT")
    check("cli_exact_exit", code == 0, error or "exit 0")
    check("cli_exact_priority", payload.get("reader_route") == "EXACT_KNOWN_LABEL" and payload.get("intake_action") == "REUSE_EXACT_LABEL_CARD" and payload.get("working_reading_de") == "[PFLANZENNAME:oiil]", str(payload))

    check("result_status", result["status"] == "MUTATED_NAME_CORES_PRESERVE_READING_AND_PROVENANCE__WORKSHEET_READY", result["status"])
    check("result_replay", result["unseen_core_probe_count"] == result["unseen_core_probe_pass_count"] == 89, str(result))
    check("result_five_invariants", all(result[key] == 89 for key in ("channel_signature_stable_count", "ordered_recipe_stable_count", "support_tier_and_rank_stable_count", "bounded_shell_id_stable_count", "working_reading_stable_count")), str(result))
    check("result_distributions", result["content_class_counts"] == dict(sorted(classes.items())) and result["route_counts"] == dict(sorted(routes.items())) and result["recipe_support_tier_counts"] == dict(sorted(tiers.items())), str(result))
    check("result_support_counts", result["old_recipe_carrier_backed_count"] == 42 and result["bounded_shell_match_count"] == 17 and result["shell_shape_count"] == 11, str(result))
    check("result_slots", result["future_page_slots"] == 4 and result["released_page_slots"] == 0, str(result))
    check("result_claim_ceiling", result["new_pages"] == result["new_channels"] == result["new_component_meanings"] == result["new_surface_predictions"] == result["confirmed_lexemes"] == 0, "no expanded claim")
    check("sealed_pages_absent", all(not value.startswith("f84") for row in slots for value in (row["page_id"],)), "no sealed page")

    before = {path.name: sha256(path) for path in GENERATED}
    completed = subprocess.run([sys.executable, str(RUN)], cwd=ROOT, capture_output=True, text=True, check=False)
    check("deterministic_rebuild_exit", completed.returncode == 0, completed.stderr[-500:] or "exit 0")
    after = {path.name: sha256(path) for path in GENERATED}
    check("deterministic_rebuild_bytes", before == after, "all generated artifact hashes unchanged")

    passed = sum(row["status"] == "PASS" for row in checks)
    failed = len(checks) - passed
    payload = {
        "status": "PASS" if failed == 0 else "FAIL",
        "check_count": len(checks),
        "passed": passed,
        "failed": failed,
        "checks": checks,
    }
    VALIDATION.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": payload["status"], "checks": len(checks), "passed": passed, "failed": failed}, ensure_ascii=False))
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
