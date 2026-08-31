#!/usr/bin/env python3
"""Independent replay and structural validation for GDT689/V62."""

from __future__ import annotations

import csv
import importlib.util
import json
import re
import sys
import tempfile
from collections import Counter
from pathlib import Path


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
BASE = ROOT / "experiments/yolo/gdt689_v62_bound_dy_sister_endpoint_dispatch"
ART = BASE / "artifacts"
RUN = BASE / "src/run.py"
VALIDATION = ART / "VALIDATION.json"


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def load_builder():
    sys.dont_write_bytecode = True
    spec = importlib.util.spec_from_file_location("gdt689_run", RUN)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main() -> int:
    checks: list[str] = []

    def check(condition: bool, label: str) -> None:
        assert condition, label
        checks.append(label)

    published = json.loads((ART / "RESULT.json").read_text(encoding="utf-8"))
    builder = load_builder()
    with tempfile.TemporaryDirectory(prefix="gdt689_rebuild_") as temp_name:
        temp_art = Path(temp_name)
        rebuilt = builder.build(temp_art)
        check(rebuilt == published, "result_json_replays_exactly")
        generated = sorted(published["files"])
        check(len(generated) == 15, "fifteen_hashed_primary_artifacts")
        for name in generated + ["RESULT.json"]:
            check((ART / name).read_bytes() == (temp_art / name).read_bytes(), f"byte_replay:{name}")

    inventory = read_tsv(ART / "SURFACE_DY_60_FORM_INVENTORY.tsv")
    positions = read_tsv(ART / "SURFACE_DY_74_POSITION_INVENTORY.tsv")
    semantic = read_tsv(ART / "SISTER_36_HEAD_PRESERVING_COMPARISON.tsv")
    parser_null = read_tsv(ART / "PARSER_EQUIVALENT_NULL_CONTROL.tsv")
    prediction = read_tsv(ART / "V62_37_RULE_PREDICTION_AUDIT.tsv")
    sister_audit = read_tsv(ART / "V48_36_USABLE_SISTER_CLASS_AUDIT.tsv")
    cells = read_tsv(ART / "CORE_REGISTER_PHYSICAL_POSITION_CELLS.tsv")
    grid = read_tsv(ART / "GRID_8_D_BIT_STATE_CONTROLS.tsv")
    class_summary = read_tsv(ART / "V62_CLASS_SUMMARY.tsv")
    revisions = read_tsv(ART / "V62_50_POSITION_REVISIONS.tsv")
    line_revisions = read_tsv(ART / "V62_LINE_REVISIONS.tsv")
    reader = read_tsv(ART / "V62_51_LINE_READER.tsv")
    provenance = read_tsv(ART / "V62_VERB_OCCURRENCE_PROVENANCE.tsv")
    decisions = read_tsv(BASE / "src/V62_DY_SISTER_DECISIONS.tsv")

    check(len(inventory) == len(decisions) == 60, "sixty_surface_inventory")
    check(len({row["surface"] for row in inventory}) == 60, "surface_inventory_unique")
    check(all(row["surface"].endswith("dy") for row in inventory), "all_targets_end_visible_dy")
    check({row["surface"] for row in inventory} == {row["surface"] for row in decisions}, "decision_population_exact")
    check(len(positions) == 74, "seventy_four_positions")
    check(sum(int(row["positions"]) for row in inventory) == 74, "inventory_position_sum")
    check(len({row["locus"] for row in positions}) == 33, "thirty_three_target_lines")
    check(len({row["page"] for row in positions}) == 23, "twenty_three_target_pages")

    pair_counts = Counter(row["pair_status"] for row in inventory)
    check(pair_counts == Counter({
        "REAL_NON_DY_SISTER": 36,
        "PARSER_EQUIVALENT_NULL": 1,
        "NO_REAL_SISTER": 11,
        "VISIBLE_SISTER_WITHOUT_CARD": 10,
        "PARSER_INVALID_PAIR": 1,
        "NESTED_DY_SISTER_EXCLUDED": 1,
    }), "pair_status_partition_36_1_11_10_1_1")
    class_counts = Counter(row["v62_class"] for row in inventory)
    check(class_counts == Counter({
        "RESULT_PARTICIPLE": 25,
        "FIELD_END": 12,
        "UNPAIRED_WHOLE_RETAINED": 22,
        "PAIR_INVALID": 1,
    }), "dispatch_partition_25_12_0_22_1")
    check(len(semantic) == len(sister_audit) == 36 and len(parser_null) == 1, "thirty_six_head_pairs_plus_one_parser_null")
    check(all(row["pair_status"] == "REAL_NON_DY_SISTER" for row in semantic), "semantic_pairs_only_usable")
    check({row["surface"] for row in sister_audit} == {row["surface"] for row in semantic}, "scored_population_exactly_head_preserving_cards")
    check(parser_null[0]["surface"] == "cheody" and parser_null[0]["sister_working_meaning_de"] == "NONE", "cheody_is_parser_null_not_head_pair")

    formal_surfaces = Counter(row["formal_dy_status"] for row in inventory)
    formal_positions = Counter()
    for row in inventory:
        formal_positions[row["formal_dy_status"]] += int(row["positions"])
    check(formal_surfaces == Counter({"FORMAL_DY": 24, "MIXED_FORMAL_DY": 2, "NO_FORMAL_DY": 17, "UNRESOLVED": 17}), "formal_surface_partition_24_2_17_17")
    check(formal_positions == Counter({"FORMAL_DY": 30, "MIXED_FORMAL_DY": 3, "NO_FORMAL_DY": 24, "UNRESOLVED": 17}), "formal_position_partition_30_3_24_17")
    check({row["surface"] for row in inventory if row["formal_dy_status"] == "MIXED_FORMAL_DY"} == {"otedy", "otchdy"}, "mixed_recipe_surfaces_exact")

    by_surface = {row["surface"]: row for row in inventory}
    check(by_surface["cheody"]["derived_one_edit_sister"] == "cheoy", "cheody_cheoy_surface_control")
    check(by_surface["cheody"]["pair_status"] == "PARSER_EQUIVALENT_NULL", "cheody_parser_equivalent_null_status")
    check(by_surface["cheody"]["v62_class"] == "FIELD_END", "cheody_no_semantic_dy_load")
    check(by_surface["cheody"]["gdt516_bound_recipe"] == by_surface["cheody"]["gdt516_sister_recipe"] == "CH+E+O+Y", "cheody_cheoy_same_recipe")
    check(by_surface["dchedy"]["pair_status"] == "PARSER_INVALID_PAIR", "dchedy_dchey_parser_guard")
    check(by_surface["dchedy"]["gdt516_bound_recipe"] == "D_ADDR+CHD+Y", "dchedy_recipe_guard")
    check(by_surface["dchedy"]["gdt516_sister_recipe"] == "CH+E+Y", "dchey_recipe_guard")
    check(by_surface["ypcheddy"]["pair_status"] == "NESTED_DY_SISTER_EXCLUDED", "ypcheddy_nested_guard")
    check(by_surface["ypcheddy"]["derived_one_edit_sister"].endswith("dy"), "ypchedy_not_non_dy_control")

    confusion = Counter((row["v60_target_class"], row["sister_text_class"]) for row in sister_audit)
    check(confusion == Counter({
        ("RESULT", "NONACTION"): 25,
        ("ACTION", "ACTION"): 6,
        ("RESULT", "ACTION"): 3,
        ("ACTION", "NONACTION"): 2,
    }), "sister_class_confusion_25_6_3_2")
    check(sum(row["class_relation"] == "SAME" for row in sister_audit) == 31, "thirty_one_sister_class_matches")

    check(len(prediction) == 37, "thirty_seven_rule_compression_rows")
    for row in prediction:
        predicted = (
            "FIELD_END" if row["same_recipe"] == "1" else
            "FIELD_END" if row["sister_endpoint_before_dy"] == "1" else
            "RESULT_PARTICIPLE"
        )
        check(row["predicted_class"] == predicted, f"mechanical_prediction:{row['surface']}")
        check(row["evaluation_scope"] == "COMPRESSION_AUDIT_NOT_HELD_PREDICTION", f"prediction_scope:{row['surface']}")
    check(sum(row["match"] == "1" for row in prediction) == 36, "mechanical_rule_matches_thirty_six_of_thirty_seven")
    check([row["surface"] for row in prediction if row["match"] == "0"] == ["ychedy"], "ychedy_only_in_sample_override")

    check(len(cells) == 21, "twenty_one_controlled_cells")
    check(len({row["surface"] for row in cells}) == 17, "seventeen_controlled_surfaces")
    check(sum(int(row["bound_v61_positions"]) for row in cells) == 24, "twenty_four_controlled_target_positions")
    check(sum(int(row["sister_v48_positions"]) for row in cells) == 215, "two_hundred_fifteen_control_positions")
    controlled = Counter()
    for row in cells:
        controlled[(row["bound_v60_class"], row["sister_text_class"])] += int(row["bound_v61_positions"])
    check(controlled == Counter({("RESULT", "NONACTION"): 24}), "controlled_confusion_24_result_nonaction")
    check(all(row["position_basis"] == "PHYSICAL_LINE_POSITION" for row in cells), "physical_position_not_mislabeled_statement")

    known_statement = [row for row in positions if row["true_statement_position"] != "UNAVAILABLE"]
    check(len(known_statement) == 7, "seven_true_statement_joins")
    check(Counter(row["true_statement_position"] for row in known_statement) == Counter({"MEDIAL": 3, "FINAL": 3, "INITIAL": 1}), "statement_position_partition_3_3_1")
    check(sum(row["physical_line_position"] == row["true_statement_position"] for row in known_statement) == 3, "three_physical_statement_position_matches")
    check(all(row["statement_position_source"] == "NOT_PUBLICLY_JOINABLE" for row in positions if row["true_statement_position"] == "UNAVAILABLE"), "no_statement_position_imputation")

    check(len(grid) == 8, "eight_grid_controls")
    check(all(row["v62_class"] == "RESULT_PARTICIPLE" for row in grid), "all_grid_controls_selected_resultative")
    check(all(row["surface_d_bit"] == "1" and row["sister_d_bit"] == "0" for row in grid), "grid_d_bit_contrasts")
    check(all(row["evidence"] == "COMPLETE_GDT624_D_BIT_STATE_BINDING__DOES_NOT_IDENTIFY_RESULT_SEMANTICS" for row in grid), "grid_claim_limited_to_d_bit_state_binding")

    expected_summary = {
        "RESULT_PARTICIPLE": (25, 36, 1, 35, 0),
        "FIELD_END": (12, 14, 7, 7, 6),
        "ACTION_TELICITY": (0, 0, 0, 0, 0),
        "PAIR_INVALID": (1, 1, 0, 1, 0),
        "UNPAIRED_WHOLE_RETAINED": (22, 23, 7, 16, 7),
    }
    observed_summary = {
        row["v62_class"]: tuple(int(row[field]) for field in (
            "surfaces", "current_positions", "v60_action_positions",
            "v60_result_positions", "v62_action_positions",
        ))
        for row in class_summary
    }
    check(observed_summary == expected_summary, "class_summary_all_counts_exact")
    check(len(revisions) == 50, "fifty_position_revisions")
    check(len(line_revisions) == 25, "twenty_five_revised_lines")
    preservation_counts = Counter(row["preservation_rule"] for row in revisions)
    check(preservation_counts == Counter({
        "KEEP_SISTER_HEAD_DEGREE_AND_BASE_ACTION__ADD_ONLY_SELECTED_DY_EFFECT": 47,
        "SAME_RECIPE_TARGET_WHOLE_CARD__NO_VISIBLE_D_SEMANTIC_LOAD": 3,
    }), "revision_partition_47_head_plus_3_parser_null")
    check({row["surface"] for row in revisions if row["preservation_rule"].startswith("SAME_RECIPE")} == {"cheody"}, "parser_null_revisions_only_cheody")
    check(any(row["surface"] == "olchdy" and row["action_before"] == "1" and row["action_after"] == "0" for row in revisions), "olchdy_action_demotion")
    check(any(row["surface"] == "dshedy" and row["action_before"] == "1" and row["action_after"] == "0" for row in revisions), "dshedy_action_demotion")
    check(any(row["surface"] == "ychedy" and row["action_before"] == "0" and row["action_after"] == "0" for row in revisions), "ychedy_result_preserved")
    check(by_surface["qoeedy"]["v62_class"] == "FIELD_END", "qoeedy_copies_action_sister_without_dy_load")

    check(len(reader) == 51, "fifty_one_reader_lines")
    check(len({row["locus"] for row in reader}) == 51, "reader_loci_unique")
    check(len({(row["locus"], row["ordinal"], row["surface"]) for row in positions}) == 74, "position_join_keys_unique")
    check(len({(row["locus"], row["occurrence_index"]) for row in provenance}) == 115, "verb_occurrence_keys_unique")
    check(sum(int(row["token_count"]) for row in reader) == 479, "four_hundred_seventy_nine_reader_positions")
    check(sum(int(row["v62_action_positions"]) for row in reader) == 83, "eighty_three_action_positions")
    check(sum(int(row["v62_dy_sister_revisions"]) for row in reader) == 50, "reader_embeds_fifty_revisions")
    check(sum(int(row["v62_verb_occurrences"]) for row in reader) == len(provenance) == 115, "one_hundred_fifteen_exact_verbs")
    reader_by_locus = {row["locus"]: row for row in reader}
    rule_rows = read_tsv(ROOT / "experiments/yolo/gdt688_v61_exact_verb_ordinal_provenance_renderer/src/V61_VERB_RULES.tsv")
    verb_rules = {row["canonical_lemma"]: re.compile(row["regex"], re.IGNORECASE) for row in rule_rows}
    provenance_ordinals: dict[str, set[int]] = {row["locus"]: set() for row in reader}
    for row in provenance:
        line = reader_by_locus[row["locus"]]
        text = line["v62_practical_translation_de"]
        start, end = int(row["char_start"]), int(row["char_end"])
        check(text[start:end] == row["matched_text"], f"verb_span:{row['locus']}:{row['occurrence_index']}")
        ordinal = int(row["source_ordinal"])
        provenance_ordinals[row["locus"]].add(ordinal)
        check(ordinal in {int(value) for value in line["v62_action_ordinals"].split("|") if value != "NONE"}, f"verb_action_ordinal:{row['locus']}:{row['occurrence_index']}")
        check(line["zl3b_line"].split()[ordinal - 1] == row["source_surface"], f"verb_surface:{row['locus']}:{row['occurrence_index']}")
        glosses = line["v62_literal_token_glosses_de"].split(" | ")
        check(len(glosses) == int(line["token_count"]), f"gloss_cardinality:{row['locus']}")
        check(glosses[ordinal - 1] == row["source_literal_gloss_de"], f"verb_source_gloss:{row['locus']}:{row['occurrence_index']}")
        check(row["canonical_lemma"] in verb_rules and verb_rules[row["canonical_lemma"]].fullmatch(row["matched_text"]) is not None, f"verb_regex_replay:{row['locus']}:{row['occurrence_index']}")
        check(row["action_licensed"] == "1" and row["provenance_status"] == "EXACT_V62_RENDERER_SPAN_TO_ACTION_ORDINAL", f"verb_provenance:{row['locus']}:{row['occurrence_index']}")

    for row in reader:
        action_ordinals = {int(value) for value in row["v62_action_ordinals"].split("|") if value != "NONE"}
        check(provenance_ordinals[row["locus"]] == action_ordinals, f"action_provenance_set_exact:{row['locus']}")

    for table in (positions, reader, revisions, line_revisions, provenance):
        for row in table:
            for field in ("page", "locus"):
                value = row.get(field, "").lower()
                check(not value.startswith("f84"), f"sealed_page_absent:{field}:{value or 'empty'}")

    check(published["status"] == "PASS_V62_36_HEAD_SISTERS_PLUS_1_RECIPE_NULL__25_RESULT_12_FIELD_0_TELIC__47_HEAD_PLUS_3_NULL_REVISIONS", "published_status_exact")
    check(published["semantic_debt"] == {"strict": 106, "mechanical_union": 152, "four_layer_union": 330}, "semantic_debt_not_falsely_reduced")
    check(published["sealed_pages_absent"] is True, "sealed_pages_reported_absent")

    payload = {
        "status": "PASS",
        "validator": "GDT689_INDEPENDENT_BYTE_REPLAY_AND_STRUCTURAL_VALIDATOR",
        "checks": len(checks),
        "population": {"surfaces": 60, "positions": 74, "head_pairs": 36, "parser_null_pairs": 1, "revised_positions": 50},
        "reader": {"lines": 51, "positions": 479, "actions": 83, "verbs": 115},
        "formal_dy": {"definite_surfaces": 24, "mixed_surfaces": 2, "non_dy_surfaces": 17, "unresolved_surfaces": 17},
        "sealed_pages_absent": True,
        "byte_replay": "EXACT",
    }
    VALIDATION.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(payload, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
