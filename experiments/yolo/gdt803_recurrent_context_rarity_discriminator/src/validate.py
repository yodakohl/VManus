#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import subprocess
from collections import Counter
from pathlib import Path


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
EXP = ROOT / "experiments/yolo/gdt803_recurrent_context_rarity_discriminator"
SRC = EXP / "src"
ART = EXP / "artifacts"
RESULT = ART / "RESULT.json"
VALIDATION = ART / "VALIDATION.json"
REPORT = EXP / "REPORT.md"
FILES = {
    "stable": ART / "GDT803_14_STABLE_CONTEXT_DECK.tsv",
    "occurrences": ART / "GDT803_450_CORE_CONTEXT_OCCURRENCES.tsv",
    "brackets": ART / "GDT803_12_BIDIRECTIONAL_BRACKETS.tsv",
    "controls": ART / "GDT803_7_OUTCOME_BLIND_CONTROL_MATCH.tsv",
    "groups": ART / "GDT803_GROUP_POSITION_POPULATION_CARD.tsv",
    "rarity": ART / "GDT803_RARITY_ENUMERATION.tsv",
    "bracket_enum": ART / "GDT803_BRACKET_ENUMERATION.tsv",
    "matched_pairs": ART / "GDT803_EXACT_MATCHED_EVENT_PAIRS.tsv",
    "identity_pairs": ART / "GDT803_IDENTITY_RARITY_PAIR_ATLAS.tsv",
    "identity": ART / "GDT803_IDENTITY_RARITY_SUMMARY.tsv",
    "styles": ART / "GDT803_STYLE_SENSITIVITY.tsv",
    "passages": ART / "GDT803_EXACT_PASSAGE_CARD.tsv",
    "bridge": ART / "GDT803_FIELD_ROLE_BRIDGE.tsv",
    "candidates": ART / "GDT803_CANDIDATE_ADJUDICATION.tsv",
    "card": ART / "GDT803_STRUCTURAL_CARD.tsv",
}


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def header(path: Path) -> list[str]:
    with path.open(encoding="utf-8", newline="") as handle:
        return next(csv.reader(handle, delimiter="\t"))


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def close(left: float, right: float, tolerance: float = 3e-10) -> bool:
    return math.isclose(left, right, rel_tol=tolerance, abs_tol=1e-13)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--skip-replay", action="store_true")
    args = parser.parse_args()
    checks: list[str] = []

    def check(name: str, condition: bool) -> None:
        assert condition, name
        checks.append(name)

    result = json.loads(RESULT.read_text(encoding="utf-8"))
    unhashed = dict(result)
    content_hash = unhashed.pop("content_hash")
    check("result_content_hash", content_hash == hashlib.sha256(json.dumps(unhashed, sort_keys=True, separators=(",", ":")).encode()).hexdigest())
    for category in ("inputs", "outputs", "implementation"):
        for path, digest in result[category].items():
            check(f"hash:{category}:{path}", sha(ROOT / path) == digest)

    expected_schemas = {
        "occurrences": ["group_id", "side", "context_surface", "occurrence_id", "source_selector", "physical_folio", "locus", "token_index", "stem", "terminal", "masked_target", "left_context", "right_context", "distance_cell", "position4", "population", "page_s", "residual_m_minus_position_stem", "semantic_export_credit"],
        "brackets": ["bracket_id", "occurrence_id", "source_selector", "physical_folio", "locus", "section", "language", "hand", "left_context", "target_surface", "target_stem", "terminal", "right_context", "exact_three_token_span", "full_zl3b_line", "working_construction_de", "null_rival", "semantic_export_credit"],
        "controls": ["group_id", "side", "candidate_surface", "control_surface", "exposure_distance", "candidate_events", "control_events", "candidate_stems", "control_stems", "candidate_folios", "control_folios", "matching_inputs", "outcome_fields_used"],
        "groups": ["group_id", "side", "cohort", "population", "position4", "surfaces", "events", "m_events", "l_events", "stems", "physical_folios", "mean_residual_m_minus_position_stem", "interpretation"],
        "rarity": ["group_id", "side", "nearest_options_per_candidate", "unique_injective_control_sets", "candidate_full_residual", "candidate_cache_rest_residual", "control_mean_full_residual", "control_mean_cache_rest_residual", "controls_at_least_as_l_favouring_both", "ranking_fraction", "interpretation"],
        "bracket_enum": ["candidate_left_surfaces", "candidate_right_surfaces", "candidate_events", "candidate_m", "candidate_stems", "candidate_folios", "matched_control_events", "matched_control_m", "matched_control_stems", "matched_control_folios", "enumerated_left_sets", "enumerated_right_sets", "enumerated_set_pairs", "controls_with_at_least_candidate_events", "nonempty_all_l_controls", "controls_at_least_as_extreme_all_dimensions", "interpretation"],
        "matched_pairs": ["group_id", "side", "population", "pair_ordinal", "stem", "distance_cell", "candidate_occurrence_id", "candidate_folio", "candidate_context", "candidate_terminal", "control_occurrence_id", "control_folio", "control_context", "control_terminal", "pair_outcome", "semantic_export_credit"],
        "identity_pairs": ["side", "stratum_id", "pair_ordinal", "section", "language", "hand", "stem", "distance_cell", "l_occurrence_id", "l_folio", "l_context", "l_exact_score", "l_training_count", "m_occurrence_id", "m_folio", "m_context", "m_exact_score", "m_training_count", "exact_auc", "rarity_auc", "delta_exact_minus_rarity", "semantic_export_credit"],
        "identity": ["side", "real_context_events", "scoreable_events", "raw_cross_folio_pairs", "informative_strata", "same_folio_pair_capacity", "exact_micro_auc", "rarity_micro_auc", "exact_macro_auc", "rarity_macro_auc", "macro_delta", "sign_flips", "exceed_or_equal", "one_sided_add_one_p", "decision"],
        "styles": ["side", "section", "language", "hand", "pairs", "exact_micro_auc", "rarity_micro_auc", "delta_exact_minus_rarity", "interpretation"],
        "passages": ["passage_id", "kind", "group_id", "outcome", "stem", "distance_cell", "candidate_locus", "candidate_span", "candidate_full_line", "control_locus", "control_span", "control_full_line", "note"],
        "bridge": ["side", "context_surface", "core_group", "preexisting_broad_role", "preexisting_working_default_de", "primary_source", "gdt803_context_events", "gdt803_context_m", "bridge_reading", "historical_architecture_rival", "counterevidence", "semantic_credit"],
        "candidates": ["candidate_id", "candidate", "decision", "positive_evidence", "counterevidence", "claim_ceiling"],
        "card": ["card_id", "scope", "structural_tag", "german_display", "left_group", "right_group", "left_events_m", "right_events_m", "double_brackets_m", "confidence", "positive_evidence", "counterevidence", "renderer_license", "terminal_equivalence", "component_export", "semantic_export", "plaintext_value"],
    }
    for name, schema in expected_schemas.items():
        check(f"schema:{name}", header(FILES[name]) == schema)
        rows = read_tsv(FILES[name])
        check(f"no_blank:{name}", all(all(row[field] != "" for field in schema) for row in rows))

    stable = read_tsv(FILES["stable"])
    check("stable_count", len(stable) == 14)
    check("stable_all_25", all(row["eligible_cross_folds"] == "25" for row in stable))
    check("stable_sign", all(float(row["min_beta_context"]) * float(row["max_beta_context"]) > 0 for row in stable))
    check("stable_role_credit_zero", all(row["meaning_credit"].startswith("ZERO") for row in stable))
    check("seven_core", sum(row["core_group"] != "NONE" for row in stable) == 7)
    occurrences = read_tsv(FILES["occurrences"])
    check("occurrence_count", len(occurrences) == 450)
    check("occurrence_group_counts", Counter(row["group_id"] for row in occurrences) == Counter({"LEFT_QOK4": 149, "RIGHT_RESULT3": 301}))
    check("occurrence_m_counts", Counter(row["group_id"] for row in occurrences if row["terminal"] == "m") == Counter({"LEFT_QOK4": 11, "RIGHT_RESULT3": 2}))
    check("occurrence_scope", all(not row["source_selector"].startswith("f84") for row in occurrences))
    check("occurrence_zero_export", all(row["semantic_export_credit"].startswith("ZERO") for row in occurrences))

    brackets = read_tsv(FILES["brackets"])
    check("bracket_count", len(brackets) == 12)
    check("brackets_all_l", {row["terminal"] for row in brackets} == {"l"})
    check("bracket_breadth", (len({row["target_stem"] for row in brackets}), len({row["physical_folio"] for row in brackets})) == (11, 11))
    check("bracket_span_exact", all(row["exact_three_token_span"] in row["full_zl3b_line"] for row in brackets))
    check("bracket_no_f84", all(not row["source_selector"].startswith("f84") for row in brackets))

    controls = read_tsv(FILES["controls"])
    control_map = {(row["side"], row["candidate_surface"]): row["control_surface"] for row in controls}
    check("seven_control_matches", len(controls) == len(control_map) == 7)
    check("control_map", control_map == {
        ("LEFT", "qokeey"): "al", ("LEFT", "qokedy"): "shedy", ("LEFT", "qokeedy"): "shol",
        ("LEFT", "qokain"): "ar", ("RIGHT", "daiin"): "chol", ("RIGHT", "shedy"): "ol", ("RIGHT", "chedy"): "dy",
    })
    check("controls_outcome_blind", all(row["outcome_fields_used"] == "NONE" for row in controls))

    groups = read_tsv(FILES["groups"])
    check("group_rows", len(groups) == 48)
    group_map = {(row["group_id"], row["cohort"], row["population"], row["position4"]): row for row in groups}
    check("group_keys_unique", len(group_map) == 48)
    check("left_full", (group_map[("LEFT_QOK4", "CANDIDATE", "FULL", "ALL")]["events"], group_map[("LEFT_QOK4", "CANDIDATE", "FULL", "ALL")]["m_events"]) == ("149", "11"))
    check("right_full", (group_map[("RIGHT_RESULT3", "CANDIDATE", "FULL", "ALL")]["events"], group_map[("RIGHT_RESULT3", "CANDIDATE", "FULL", "ALL")]["m_events"]) == ("301", "2"))
    check("candidate_residuals_negative", close(float(group_map[("LEFT_QOK4", "CANDIDATE", "FULL", "ALL")]["mean_residual_m_minus_position_stem"]), -0.0894419879227) and close(float(group_map[("RIGHT_RESULT3", "CANDIDATE", "FULL", "ALL")]["mean_residual_m_minus_position_stem"]), -0.0424591828597))
    check("control_residuals_positive", float(group_map[("LEFT_QOK4", "MATCHED_CONTROL", "FULL", "ALL")]["mean_residual_m_minus_position_stem"]) > 0 and float(group_map[("RIGHT_RESULT3", "MATCHED_CONTROL", "FULL", "ALL")]["mean_residual_m_minus_position_stem"]) > 0)

    rarity = read_tsv(FILES["rarity"])
    check("rarity_rows", len(rarity) == 6)
    rarity_map = {(row["side"], row["nearest_options_per_candidate"]): row for row in rarity}
    check("rarity_set_counts", [int(rarity_map[("LEFT", str(k))]["unique_injective_control_sets"]) for k in (5, 8, 10)] == [160, 811, 1595] and [int(rarity_map[("RIGHT", str(k))]["unique_injective_control_sets"]) for k in (5, 8, 10)] == [10, 56, 120])
    check("rarity_zero_extreme", all(row["controls_at_least_as_l_favouring_both"] == "0" for row in rarity))
    bracket_enum = read_tsv(FILES["bracket_enum"])
    check("one_bracket_enum", len(bracket_enum) == 1)
    be = bracket_enum[0]
    check("bracket_candidate_stats", tuple(int(be[field]) for field in ("candidate_events", "candidate_m", "candidate_stems", "candidate_folios")) == (12, 0, 11, 11))
    check("bracket_matched_stats", tuple(int(be[field]) for field in ("matched_control_events", "matched_control_m", "matched_control_stems", "matched_control_folios")) == (4, 1, 4, 4))
    check("bracket_enumeration_capacity", (be["enumerated_left_sets"], be["enumerated_right_sets"], be["enumerated_set_pairs"]) == ("1595", "120", "191400"))
    check("bracket_no_equal_control", be["controls_at_least_as_extreme_all_dimensions"] == "0")

    matched = read_tsv(FILES["matched_pairs"])
    check("matched_pair_rows", len(matched) == 280)
    outcomes = Counter((row["group_id"], row["population"], row["pair_outcome"]) for row in matched)
    check("left_full_pairs", (outcomes[("LEFT_QOK4", "FULL", "SUPPORTS_L")], outcomes[("LEFT_QOK4", "FULL", "REVERSES")], outcomes[("LEFT_QOK4", "FULL", "TIE")]) == (4, 1, 44))
    check("right_full_pairs", (outcomes[("RIGHT_RESULT3", "FULL", "SUPPORTS_L")], outcomes[("RIGHT_RESULT3", "FULL", "REVERSES")], outcomes[("RIGHT_RESULT3", "FULL", "TIE")]) == (3, 0, 99))
    check("matched_cross_folio", all(row["candidate_folio"] != row["control_folio"] for row in matched))

    identity_pairs = read_tsv(FILES["identity_pairs"])
    check("identity_pair_count", len(identity_pairs) == 155)
    check("identity_pair_sides", Counter(row["side"] for row in identity_pairs) == Counter({"LEFT": 107, "RIGHT": 48}))
    check("identity_cross_folio", all(row["l_folio"] != row["m_folio"] for row in identity_pairs))
    identity = read_tsv(FILES["identity"])
    identity_map = {row["side"]: row for row in identity}
    check("identity_two_sides", set(identity_map) == {"LEFT", "RIGHT"})
    check("identity_exact_values", close(float(identity_map["LEFT"]["macro_delta"]), 0.167162698413) and close(float(identity_map["RIGHT"]["macro_delta"]), 0.129273504274))
    check("identity_capacity", (identity_map["LEFT"]["informative_strata"], identity_map["RIGHT"]["informative_strata"], identity_map["LEFT"]["same_folio_pair_capacity"], identity_map["RIGHT"]["same_folio_pair_capacity"]) == ("28", "13", "3", "4"))
    for side, row in identity_map.items():
        check(f"identity_p_formula:{side}", close(float(row["one_sided_add_one_p"]), (int(row["exceed_or_equal"]) + 1) / (int(row["sign_flips"]) + 1)))
        check(f"identity_flip_count:{side}", int(row["sign_flips"]) == int(result["sign_flips"]))
    check("left_identity_selected", identity_map["LEFT"]["decision"] == "DISTRIBUTED_IDENTITY_BEATS_RARITY_LEAD")
    check("right_identity_unresolved", identity_map["RIGHT"]["decision"] == "IDENTITY_LEAD_NOT_RESOLVED")

    styles = read_tsv(FILES["styles"])
    check("style_rows", len(styles) >= 4)
    check("style_sensitivity", min(float(row["delta_exact_minus_rarity"]) for row in styles if row["side"] == "LEFT") < 0 < max(float(row["delta_exact_minus_rarity"]) for row in styles if row["side"] == "LEFT"))
    passages = read_tsv(FILES["passages"])
    check("passage_rows", len(passages) == 21)
    check("counterexample_rows", Counter(row["kind"] for row in passages)["CORE_COUNTEREXAMPLE"] == 13)
    bridge = read_tsv(FILES["bridge"])
    check("bridge_rows", len(bridge) == 14 and sum(row["core_group"] != "NONE" for row in bridge) == 7)
    check("bridge_zero_credit", all(row["semantic_credit"].startswith("ZERO") for row in bridge))
    candidates = {row["candidate_id"]: row for row in read_tsv(FILES["candidates"])}
    check("candidate_ids", set(candidates) == {f"C{i}" for i in range(1, 7)})
    check("candidate_decisions", candidates["C2"]["decision"] == "SELECT_EXPLORATORY_WORKING_CONSTRUCTION" and candidates["C5"]["decision"] == "NOT_USED__PREVIOUSLY_REJECTED" and candidates["C6"]["decision"] == "REJECT_EXPORT")
    card = read_tsv(FILES["card"])
    check("one_structural_card", len(card) == 1)
    check("card_ceiling", card[0]["terminal_equivalence"] == card[0]["component_export"] == card[0]["semantic_export"] == card[0]["plaintext_value"] == "NONE")
    check("card_exact_renderer_only", card[0]["renderer_license"] == "EXACT_ENUMERATED_BRACKETS_AS_WORKING_DISPLAY_ONLY")

    check("result_decision", result["decision"] == "QUALITY_VALUE_BRACKETED_L_SURFACE_WORKING_CONSTRUCTION")
    check("result_counts", (result["stable_context_cards"], result["core_context_surfaces"], result["core_one_sided_occurrences"], result["double_bracket_events"], result["double_bracket_m"]) == (14, 7, 450, 12, 0))
    check("result_zero_semantics", result["semantic_exports"] == result["confirmed_lexemes"] == result["confirmed_plaintext_clauses"] == result["component_exports"] == result["terminal_equivalence_licenses"] == 0)
    check("result_scope", result["new_pages_opened"] == result["new_images_opened"] == 0 and result["f84_or_f84r_accessed"] is False)
    report = REPORT.read_text(encoding="utf-8")
    check("report_not_clothing", "does **not** reuse\nclothing as a meaning" in report)
    check("report_bracket", "12 exact three-token\nbrackets" in report)
    check("report_zero_translation", "Confirmed lexemes, component meanings, plaintext clauses and translations\n  remain zero" in report)

    output_paths = [ROOT / path for path in result["outputs"]] + [RESULT]
    baseline_hashes = {path: sha(path) for path in output_paths}
    replay_count = 0
    if not args.skip_replay:
        for replay in range(2):
            completed = subprocess.run(["python3", str(SRC / "run.py")], cwd=ROOT, check=True,
                                       stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            check(f"replay_exit:{replay + 1}", completed.returncode == 0)
            for path, digest in baseline_hashes.items():
                check(f"replay_hash:{replay + 1}:{path.name}", sha(path) == digest)
            replay_count += 1

    validation = {
        "schema": "GDT803_VALIDATION_V1", "experiment": "GDT803", "status": "PASS",
        "checks": len(checks), "replays": replay_count, "sign_flips": int(result["sign_flips"]),
        "stable_context_cards": len(stable), "core_occurrences": len(occurrences), "double_brackets": len(brackets),
        "sealed_f84_or_f84r_seen": False, "validated_result_hash": sha(RESULT),
        "validated_output_hashes": {path.relative_to(ROOT).as_posix(): sha(path) for path in output_paths if path != RESULT},
    }
    validation["content_hash"] = hashlib.sha256(json.dumps(validation, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    VALIDATION.write_text(json.dumps(validation, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"PASS: {len(checks)} checks; {replay_count} byte-identical replays")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
