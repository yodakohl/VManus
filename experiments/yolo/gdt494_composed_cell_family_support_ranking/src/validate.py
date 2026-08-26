#!/usr/bin/env python3
"""Validate GDT494's transparent family-support ranking."""

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
BASE = ROOT / "experiments/yolo/gdt494_composed_cell_family_support_ranking"
OUT = BASE / "artifacts"
G416 = ROOT / "experiments/yolo/gdt416_owner_local_imperative_sentence_compiler/artifacts"
G493 = ROOT / "experiments/yolo/gdt493_owner_dependent_tr_realization_deck/artifacts"
RUN = BASE / "src/run.py"
CLAUSES_IN = G416 / "gdt416_4576_imperative_clauses.tsv"
COMPOSED_IN = G493 / "gdt493_73_composed_working_cells.tsv"
G493_RESULT_IN = G493 / "gdt493_result.json"
RANKED = OUT / "gdt494_73_ranked_composed_cells.tsv"
TIER_A = OUT / "gdt494_27_tier_a_multihead_cards.tsv"
TIER_B = OUT / "gdt494_19_tier_b_single_head_cards.tsv"
TIER_C = OUT / "gdt494_5_tier_c_tr_pair_only_cards.tsv"
TIER_D = OUT / "gdt494_22_tier_d_cross_register_only_cards.tsv"
NONTR_SUPPORT = OUT / "gdt494_105_same_register_nontr_support_cells.tsv"
PAIR_SUPPORT = OUT / "gdt494_21_same_register_opposite_tr_cells.tsv"
CROSS_REGISTER = OUT / "gdt494_98_same_action_cross_register_cells.tsv"
FRAME_COVERAGE = OUT / "gdt494_11_frame_ranking_coverage.tsv"
REGISTER_COVERAGE = OUT / "gdt494_5_register_ranking_coverage.tsv"
READABLE = OUT / "GDT494_COMPOSED_CELL_FAMILY_SUPPORT_RANKING.md"
RESULT = OUT / "gdt494_result.json"
VALIDATION = OUT / "gdt494_validation.json"
STATUS = "TWENTY_SEVEN_MULTIHEAD_PRIORITY_CARDS__FORTY_SIX_NONTR_SUPPORTED__ALL_SEVENTY_THREE_CROSS_REGISTER_ANCHORED"
TIERS = (
    "A_MULTIHEAD_SAME_REGISTER", "B_SINGLE_NONTR_HEAD",
    "C_OPPOSITE_TR_ONLY", "D_CROSS_REGISTER_ONLY",
)
TIER_ORDER = {tier: index for index, tier in enumerate(TIERS)}
FRAMES = (
    "@ACTION", "@ACTION+AIIN", "@ACTION+AIN", "@ACTION+AL",
    "@ACTION+AL+Y", "@ACTION+CH+E+Y", "@ACTION+CHD+Y",
    "@ACTION+OL", "@ACTION+OR+Y", "@ACTION+Y", "CH+@ACTION",
)
REGISTERS = ("SOURCE_SECTION_T", "HERBAL", "BIOLOGICAL", "CELESTIAL", "PHARMA")
EXPECTED_FRAME = {
    "@ACTION": (4, 2, 2, 0, 0, 4),
    "@ACTION+AIIN": (5, 5, 0, 0, 0, 5),
    "@ACTION+AIN": (7, 3, 4, 0, 0, 7),
    "@ACTION+AL": (6, 3, 3, 0, 0, 6),
    "@ACTION+AL+Y": (8, 1, 3, 0, 4, 4),
    "@ACTION+CH+E+Y": (8, 2, 0, 2, 4, 4),
    "@ACTION+CHD+Y": (7, 0, 1, 0, 6, 1),
    "@ACTION+OL": (5, 4, 1, 0, 0, 5),
    "@ACTION+OR+Y": (8, 2, 0, 2, 4, 4),
    "@ACTION+Y": (7, 5, 2, 0, 0, 7),
    "CH+@ACTION": (8, 0, 3, 1, 4, 4),
}
EXPECTED_REGISTER = {
    "SOURCE_SECTION_T": (19, 8, 4, 1, 6, 13),
    "HERBAL": (13, 8, 1, 2, 2, 11),
    "BIOLOGICAL": (5, 2, 1, 2, 0, 5),
    "CELESTIAL": (19, 5, 8, 0, 6, 13),
    "PHARMA": (17, 4, 5, 0, 8, 9),
}
EXPECTED_TOP = (
    ("T", "BIOLOGICAL"),
    ("R+AL", "CELESTIAL"),
    ("T+AIIN", "CELESTIAL"),
    ("R+AIIN", "CELESTIAL"),
    ("T+AIN", "HERBAL"),
)


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    checks: list[dict[str, object]] = []

    def check(name: str, condition: bool, detail: object = None) -> None:
        checks.append({"name": name, "pass": bool(condition), "detail": detail})

    generated = [RANKED, TIER_A, TIER_B, TIER_C, TIER_D, NONTR_SUPPORT, PAIR_SUPPORT, CROSS_REGISTER, FRAME_COVERAGE, REGISTER_COVERAGE, READABLE, RESULT]
    present = all(path.is_file() for path in generated)
    check("all_outputs_present", present, [path.name for path in generated])
    if not present:
        raise RuntimeError("Run GDT494 builder first")
    before = {path.name: sha256(path) for path in generated}
    completed = subprocess.run([sys.executable, str(RUN)], cwd=ROOT, capture_output=True, text=True, check=False)
    after = {path.name: sha256(path) for path in generated}
    check("builder_exit_zero", completed.returncode == 0, completed.stderr[-1000:])
    check("deterministic_rebuild", before == after, {"before": before, "after": after})

    clauses = read_tsv(CLAUSES_IN)
    source_composed = read_tsv(COMPOSED_IN)
    g493 = json.loads(G493_RESULT_IN.read_text(encoding="utf-8"))
    ranked = read_tsv(RANKED)
    tier_a = read_tsv(TIER_A)
    tier_b = read_tsv(TIER_B)
    tier_c = read_tsv(TIER_C)
    tier_d = read_tsv(TIER_D)
    nontr = read_tsv(NONTR_SUPPORT)
    pairs = read_tsv(PAIR_SUPPORT)
    cross = read_tsv(CROSS_REGISTER)
    frames = read_tsv(FRAME_COVERAGE)
    registers = read_tsv(REGISTER_COVERAGE)
    readable = READABLE.read_text(encoding="utf-8")
    result = json.loads(RESULT.read_text(encoding="utf-8"))
    source_map = {row["realization_cell_id"]: row for row in source_composed}
    clause_index: dict[tuple[str, str], list[dict[str, str]]] = defaultdict(list)
    for row in clauses:
        clause_index[(row["component_recipe"], row["register"])].append(row)
    frame_map = {row["frozen_frame"]: row for row in frames}
    register_map = {row["register"]: row for row in registers}

    check("source_clause_count_4576", len(clauses) == 4576, len(clauses))
    check("source_composed_count_73", len(source_composed) == 73, len(source_composed))
    check("source_g493_status_exact", g493.get("status") == "ONE_HUNDRED_TEN_OWNER_REALIZATIONS__THIRTY_SEVEN_OBSERVED__SEVENTY_THREE_COMPOSED_WORKING")
    check("ranked_count_73", len(ranked) == 73, len(ranked))
    check("tier_a_count_27", len(tier_a) == 27, len(tier_a))
    check("tier_b_count_19", len(tier_b) == 19, len(tier_b))
    check("tier_c_count_5", len(tier_c) == 5, len(tier_c))
    check("tier_d_count_22", len(tier_d) == 22, len(tier_d))
    check("nontr_support_count_105", len(nontr) == 105, len(nontr))
    check("pair_support_count_21", len(pairs) == 21, len(pairs))
    check("cross_support_count_98", len(cross) == 98, len(cross))
    check("frame_count_11", len(frames) == 11, len(frames))
    check("register_count_5", len(registers) == 5, len(registers))

    check("ranked_source_ids_unique", len({row["source_realization_cell_id"] for row in ranked}) == 73)
    check("ranked_sources_complete", {row["source_realization_cell_id"] for row in ranked} == set(source_map))
    check("ranked_global_ranks_exact", [int(row["global_priority_rank"]) for row in ranked] == list(range(1, 74)))
    check("ranked_tier_set_exact", {row["priority_tier"] for row in ranked} == set(TIERS))
    check("ranked_tier_profile_exact", Counter(row["priority_tier"] for row in ranked) == Counter(dict(zip(TIERS, (27, 19, 5, 22)))))
    check("ranked_tier_blocks_ordered", [TIER_ORDER[row["priority_tier"]] for row in ranked] == sorted(TIER_ORDER[row["priority_tier"]] for row in ranked))
    check("ranked_tier_ranks_exact", all([int(row["tier_rank"]) for row in ranked if row["priority_tier"] == tier] == list(range(1, sum(other["priority_tier"] == tier for other in ranked) + 1)) for tier in TIERS))
    check("ranked_top_five_exact", tuple((row["action_recipe"], row["register"]) for row in ranked[:5]) == EXPECTED_TOP)
    check("ranked_recipe_identity_exact", all(row["action_recipe"] == source_map[row["source_realization_cell_id"]]["action_recipe"] and row["frozen_frame"] == source_map[row["source_realization_cell_id"]]["frozen_frame"] and row["register"] == source_map[row["source_realization_cell_id"]]["register"] for row in ranked))
    check("ranked_phrase_identity_exact", all(row["composed_working_phrase_de"] == source_map[row["source_realization_cell_id"]]["display_phrase_de"] for row in ranked))
    check("ranked_traces_identity_exact", all(row["portable_component_trace_de"] == source_map[row["source_realization_cell_id"]]["portable_component_trace_de"] and row["owner_local_slot_trace_de"] == source_map[row["source_realization_cell_id"]]["owner_local_slot_trace_de"] for row in ranked))
    check("ranked_evidence_retained", all(row["evidence_status_retained"] == "COMPOSED_WORKING" and row["composed_working_label_retained"] == "YES" for row in ranked))
    check("ranked_values_old", all(row["all_slot_values_old"] == "YES" for row in ranked))
    check("ranked_no_predictions", all(row["surface_prediction_made"] == "NO" and row["occurrence_prediction_made"] == "NO" for row in ranked))
    check("ranked_state_warnings_exact", all(row["state_warning"] == ("ACTIVE_ARGUMENT_MAY_OVERRIDE_Y_DEFAULT" if row["state_requirement"] == "ACTIVE_ARGUMENT_REQUIRED" else "NONE") for row in ranked))
    check("ranked_state_warning_count_23", sum(row["state_warning"] != "NONE" for row in ranked) == 23)

    tier_logic = True
    reason_logic = True
    for row in ranked:
        n = int(row["same_register_nontr_head_count"])
        opposite = row["opposite_tr_observed"] == "YES"
        expected_tier = "A_MULTIHEAD_SAME_REGISTER" if n >= 2 else "B_SINGLE_NONTR_HEAD" if n == 1 else "C_OPPOSITE_TR_ONLY" if opposite else "D_CROSS_REGISTER_ONLY"
        expected_reason = {
            "A_MULTIHEAD_SAME_REGISTER": "AT_LEAST_TWO_EXACT_NONTR_HEADS_IN_TARGET_REGISTER",
            "B_SINGLE_NONTR_HEAD": "ONE_EXACT_NONTR_HEAD_IN_TARGET_REGISTER",
            "C_OPPOSITE_TR_ONLY": "EXACT_OPPOSITE_TR_HEAD_IN_TARGET_REGISTER_ONLY",
            "D_CROSS_REGISTER_ONLY": "SAME_TARGET_ACTION_OBSERVED_ONLY_IN_OTHER_REGISTERS",
        }[expected_tier]
        tier_logic &= row["priority_tier"] == expected_tier
        reason_logic &= row["priority_reason"] == expected_reason
    check("ranked_tier_logic_exact", tier_logic)
    check("ranked_reason_logic_exact", reason_logic)

    sort_key = lambda row: (
        TIER_ORDER[row["priority_tier"]],
        -int(row["same_register_nontr_head_count"]),
        -int(row["same_register_nontr_event_count"]),
        -(row["opposite_tr_observed"] == "YES"),
        -int(row["same_action_other_register_count"]),
        -int(row["same_action_cross_register_event_count"]),
        row["action_recipe"], row["register"],
    )
    check("ranked_order_recomputed", ranked == sorted(ranked, key=sort_key))
    check("tier_a_exact_subset", tier_a == [row for row in ranked if row["priority_tier"] == "A_MULTIHEAD_SAME_REGISTER"])
    check("tier_b_exact_subset", tier_b == [row for row in ranked if row["priority_tier"] == "B_SINGLE_NONTR_HEAD"])
    check("tier_c_exact_subset", tier_c == [row for row in ranked if row["priority_tier"] == "C_OPPOSITE_TR_ONLY"])
    check("tier_d_exact_subset", tier_d == [row for row in ranked if row["priority_tier"] == "D_CROSS_REGISTER_ONLY"])

    check("nontr_ids_unique", len({row["support_cell_id"] for row in nontr}) == 105)
    check("nontr_keys_unique", len({(row["target_realization_cell_id"], row["alternate_action_root"]) for row in nontr}) == 105)
    check("nontr_roots_exclude_tr", all(row["alternate_action_root"] not in {"T", "R"} for row in nontr))
    check("nontr_exact_recipe", all(row["alternate_action_recipe"] == row["frozen_frame"].replace("@ACTION", row["alternate_action_root"]) for row in nontr))
    check("nontr_source_events_exact", all(int(row["event_count"]) == len(clause_index[(row["alternate_action_recipe"], row["register"])]) > 0 for row in nontr))
    check("nontr_pages_exact", all(set(row["pages"].split("|")) == {source["physical_page"] for source in clause_index[(row["alternate_action_recipe"], row["register"])]} for row in nontr))
    check("nontr_forms_exact", all(set(row["observed_clauses_de"].split(" || ")) == {source["imperative_clause_de"] for source in clause_index[(row["alternate_action_recipe"], row["register"])]} for row in nontr))
    check("nontr_roundtrip_exact", all(row["all_roundtrip_exact"] == "YES" and row["exact_same_register_frame_support"] == "YES" for row in nontr))
    check("nontr_event_total_267", sum(int(row["event_count"]) for row in nontr) == 267)

    check("pair_ids_unique", len({row["support_cell_id"] for row in pairs}) == 21)
    check("pair_keys_unique", len({(row["target_realization_cell_id"], row["alternate_action_root"]) for row in pairs}) == 21)
    check("pair_roots_tr_only", all(row["alternate_action_root"] in {"T", "R"} and row["alternate_action_root"] != row["target_action_root"] for row in pairs))
    check("pair_source_events_exact", all(int(row["event_count"]) == len(clause_index[(row["alternate_action_recipe"], row["register"])]) > 0 for row in pairs))
    check("pair_event_total_39", sum(int(row["event_count"]) for row in pairs) == 39)
    check("pair_roundtrip_exact", all(row["all_roundtrip_exact"] == "YES" and row["exact_same_register_frame_support"] == "YES" for row in pairs))

    check("cross_ids_unique", len({row["cross_register_cell_id"] for row in cross}) == 98)
    check("cross_keys_unique", len({(row["target_realization_cell_id"], row["observed_other_register"]) for row in cross}) == 98)
    check("cross_register_differs", all(row["target_register"] != row["observed_other_register"] for row in cross))
    check("cross_source_events_exact", all(int(row["event_count"]) == len(clause_index[(row["action_recipe"], row["observed_other_register"])]) > 0 for row in cross))
    check("cross_event_total_166", sum(int(row["event_count"]) for row in cross) == 166)
    check("cross_flags_exact", all(row["same_action_and_formal_frame"] == "YES" and row["exact_observed_other_register_cell"] == "YES" for row in cross))

    support_recomputed = True
    for row in ranked:
        target_id = row["source_realization_cell_id"]
        local_nontr = [support for support in nontr if support["target_realization_cell_id"] == target_id]
        local_pairs = [support for support in pairs if support["target_realization_cell_id"] == target_id]
        local_cross = [support for support in cross if support["target_realization_cell_id"] == target_id]
        support_recomputed &= int(row["same_register_nontr_head_count"]) == len(local_nontr)
        support_recomputed &= row["same_register_nontr_roots"] == ("|".join(support["alternate_action_root"] for support in local_nontr) or "NONE")
        support_recomputed &= int(row["same_register_nontr_event_count"]) == sum(int(support["event_count"]) for support in local_nontr)
        support_recomputed &= (row["opposite_tr_observed"] == "YES") == bool(local_pairs)
        support_recomputed &= int(row["opposite_tr_event_count"]) == sum(int(support["event_count"]) for support in local_pairs)
        support_recomputed &= int(row["same_action_other_register_count"]) == len(local_cross)
        support_recomputed &= row["same_action_other_registers"] == "|".join(support["observed_other_register"] for support in local_cross)
        support_recomputed &= int(row["same_action_cross_register_event_count"]) == sum(int(support["event_count"]) for support in local_cross)
    check("ranked_support_counts_recomputed", support_recomputed)
    check("ranked_nontr_target_count_46", sum(int(row["same_register_nontr_head_count"]) > 0 for row in ranked) == 46)
    check("ranked_same_register_target_count_51", sum(row["same_register_family_supported"] == "YES" for row in ranked) == 51)
    check("ranked_cross_anchor_count_73", sum(row["cross_register_same_action_anchored"] == "YES" for row in ranked) == 73)

    frame_fields = ("composed_cell_count", "tier_a_count", "tier_b_count", "tier_c_count", "tier_d_count", "same_register_supported_count")
    check("frame_order_exact", tuple(row["frozen_frame"] for row in frames) == FRAMES)
    check("frame_ids_unique", len({row["frame_id"] for row in frames}) == 11)
    check("frame_profiles_exact", all(tuple(int(frame_map[frame][field]) for field in frame_fields) == EXPECTED_FRAME[frame] for frame in FRAMES))
    check("frame_cross_anchor_complete", all(row["cross_register_anchored_count"] == row["composed_cell_count"] for row in frames))
    register_fields = ("composed_cell_count", "tier_a_count", "tier_b_count", "tier_c_count", "tier_d_count", "same_register_supported_count")
    check("register_order_exact", tuple(row["register"] for row in registers) == REGISTERS)
    check("register_ids_unique", len({row["register_id"] for row in registers}) == 5)
    check("register_profiles_exact", all(tuple(int(register_map[register][field]) for field in register_fields) == EXPECTED_REGISTER[register] for register in REGISTERS))
    check("register_cross_anchor_complete", all(row["cross_register_anchored_count"] == row["composed_cell_count"] for row in registers))

    check("readable_core_counts", "**73/73**" in readable and "**27**" in readable and "**19**" in readable and "**5**" in readable and "**22**" in readable and "**46**" in readable and "**51**" in readable)
    check("readable_all_tiers", all(tier in readable for tier in TIERS))
    check("readable_all_cards", all(row["composed_working_phrase_de"] in readable for row in ranked))
    check("readable_all_frames", all(f"`{frame}`" in readable for frame in FRAMES))
    check("readable_top_examples", "celestial `T+AIIN`" in readable and "Herbal `T/R+CH+E+Y`" in readable)
    check("readable_no_secret_score", "keinen vermischten Geheimscore" in readable)
    check("readable_next_route", "27 Tier-A-Karten" in readable and "KEINE OBERFLÄCHENVORHERSAGE" in readable)

    check("result_status_exact", result.get("status") == STATUS, result.get("status"))
    check("result_tier_counts_exact", (result.get("ranked_composed_cell_count"), result.get("tier_a_count"), result.get("tier_b_count"), result.get("tier_c_count"), result.get("tier_d_count")) == (73, 27, 19, 5, 22))
    check("result_target_counts_exact", (result.get("nontr_supported_target_count"), result.get("same_register_supported_target_count"), result.get("cross_register_anchored_target_count")) == (46, 51, 73))
    check("result_support_counts_exact", (result.get("same_register_nontr_support_cell_count"), result.get("same_register_nontr_support_event_count"), result.get("same_register_opposite_tr_cell_count"), result.get("same_register_opposite_tr_event_count"), result.get("same_action_cross_register_cell_count"), result.get("same_action_cross_register_event_count")) == (105, 267, 21, 39, 98, 166))
    check("result_state_count_23", result.get("state_warning_card_count") == 23)
    check("result_flags_true", result.get("all_composed_labels_retained") is True and result.get("all_slot_values_old") is True)
    check("result_prediction_counts_zero", result.get("surface_prediction_count") == 0 and result.get("occurrence_prediction_count") == 0)
    unchanged = ("meaning_change_count", "wording_change_count", "evidence_status_upgrade_count", "active_model_change_count", "record_boundary_change_count", "surface_change_count", "recipe_change_count", "page_change_count")
    check("result_no_source_changes", all(result.get(key) == 0 for key in unchanged), {key: result.get(key) for key in unchanged})
    check("claim_ceiling_bounded", "every composed label and state warning is retained" in result.get("claim_ceiling", "") and "no occurrence or surface prediction" in result.get("claim_ceiling", ""))

    failed = [row for row in checks if not row["pass"]]
    payload = {
        "status": "PASS" if not failed else "FAIL",
        "checks_passed": len(checks) - len(failed),
        "checks_total": len(checks),
        "failed_checks": [row["name"] for row in failed],
        "checks": checks,
    }
    VALIDATION.write_text(json.dumps(payload, indent=2, ensure_ascii=False, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({key: payload[key] for key in ("status", "checks_passed", "checks_total", "failed_checks")}, indent=2, ensure_ascii=False))
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
