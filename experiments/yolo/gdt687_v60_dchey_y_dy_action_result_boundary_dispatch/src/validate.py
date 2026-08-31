#!/usr/bin/env python3
"""Independently rebuild and validate GDT687/V60."""

from __future__ import annotations

import contextlib
import csv
import hashlib
import importlib.util
import io
import json
import sys
import tempfile
from collections import Counter
from pathlib import Path

sys.dont_write_bytecode = True


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
EXP = ROOT / "experiments/yolo/gdt687_v60_dchey_y_dy_action_result_boundary_dispatch"
ART = EXP / "artifacts"
RUN_PATH = EXP / "src/run.py"
V59_PATH = ROOT / "experiments/yolo/gdt686_v59_dain_daiin_qodaiin_value_head_dispatch/artifacts/V59_51_LINE_READER.tsv"
TARGET_SPECS = EXP / "src/V60_TARGET_DISPATCH_SPECS.tsv"
BOUND_SPECS = EXP / "src/V60_BOUND_DY_SURFACE_SPECS.tsv"


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def int_set(value: str) -> set[int]:
    return {int(item) for item in value.split("|") if item and item != "NONE"}


class Audit:
    def __init__(self) -> None:
        self.checks = 0

    def check(self, condition: bool, label: str) -> None:
        self.checks += 1
        if not condition:
            raise AssertionError(label)


def load_builder():
    spec = importlib.util.spec_from_file_location("gdt687_run", RUN_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load GDT687 builder")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main() -> int:
    audit = Audit()
    generated = {
        "BOUND_DY_60_SURFACE_DISPATCH.tsv",
        "COUNTEREXAMPLE_AUDIT.tsv",
        "DCHEY_15_OCCURRENCE_SCOPE_CENSUS.tsv",
        "DY_705_CLOSURE_PRIOR.tsv",
        "GDT687_V60_SCOPE_READER.md",
        "HYPOTHESIS_COMPARISON.tsv",
        "V60_40_PATCHED_LINES.tsv",
        "V60_51_LINE_READER.tsv",
        "V60_95_POSITION_DEBT_DELTA.tsv",
        "V60_95_POSITION_SCOPE_DISPATCH.tsv",
        "V60_DEBT_SUMMARY.tsv",
        "Y_270_CONTEXT_PRIOR.tsv",
        "Y_DY_DISTINCTION_PRIOR.tsv",
    }
    result = json.loads((ART / "RESULT.json").read_text(encoding="utf-8"))
    audit.check(set(result["files"]) == generated, "exact generated inventory")
    for name in [*sorted(generated), "RESULT.json"]:
        audit.check((ART / name).is_file(), f"missing artifact {name}")

    builder = load_builder()
    with tempfile.TemporaryDirectory(prefix="gdt687-rebuild-") as raw_temp:
        rebuilt = Path(raw_temp)
        builder.ART = rebuilt
        with contextlib.redirect_stdout(io.StringIO()):
            code = builder.main()
        audit.check(code == 0, "builder exit")
        for name in [*sorted(generated), "RESULT.json"]:
            audit.check((ART / name).read_bytes() == (rebuilt / name).read_bytes(), f"byte rebuild {name}")

    targets = read_tsv(ART / "V60_95_POSITION_SCOPE_DISPATCH.tsv")
    dchey = read_tsv(ART / "DCHEY_15_OCCURRENCE_SCOPE_CENSUS.tsv")
    bound = read_tsv(ART / "BOUND_DY_60_SURFACE_DISPATCH.tsv")
    y_prior = read_tsv(ART / "Y_270_CONTEXT_PRIOR.tsv")
    dy_prior = read_tsv(ART / "DY_705_CLOSURE_PRIOR.tsv")
    distinction = read_tsv(ART / "Y_DY_DISTINCTION_PRIOR.tsv")
    v59 = read_tsv(V59_PATH)
    v60 = read_tsv(ART / "V60_51_LINE_READER.tsv")
    patched = read_tsv(ART / "V60_40_PATCHED_LINES.tsv")
    debt_delta = read_tsv(ART / "V60_95_POSITION_DEBT_DELTA.tsv")
    debt_summary = read_tsv(ART / "V60_DEBT_SUMMARY.tsv")
    hypotheses = read_tsv(ART / "HYPOTHESIS_COMPARISON.tsv")
    counterexamples = read_tsv(ART / "COUNTEREXAMPLE_AUDIT.tsv")
    bound_specs = read_tsv(BOUND_SPECS)
    target_specs = read_tsv(TARGET_SPECS)

    keys = {(row["locus"], int(row["ordinal"])) for row in targets}
    audit.check(len(targets) == len(keys) == 95, "95 unique current target positions")
    audit.check(len(target_specs) == 21 and len(bound_specs) == 60, "complete keyed source decks")
    audit.check(len({row["locus"] for row in targets}) == 40, "40 target lines")
    audit.check(Counter(row["target_family"] for row in targets) == {
        "BOUND_DY": 74, "DCHEY": 14, "NAKED_Y": 4, "FREE_DY": 3,
    }, "exact target-family partition")
    action = [row for row in targets if row["dispatch_class"].startswith("ACTION_")]
    nominal = [row for row in targets if row["dispatch_class"].startswith("NOMINAL_")]
    reference = [row for row in targets if row["dispatch_class"] == "RIGHT_REFERENCE"]
    boundary = [row for row in targets if row["dispatch_class"] in {"CLAUSE_STOP", "LINE_STOP"}]
    audit.check((len(action), len(nominal), len(reference), len(boundary)) == (24, 64, 3, 4), "24/64/3/4 dispatch")
    audit.check(Counter(row["confidence"] for row in targets) == {"HIGH": 85, "AMBER": 10}, "target confidence partition")
    audit.check(not any(row["page"].lower().startswith("f84") for row in targets), "sealed target pages absent")
    audit.check(all(row["surface"] == "dy" and row["v60_literal_gloss_de"] in {";", "."} for row in targets if row["target_family"] == "FREE_DY"), "free dy is punctuation only")
    audit.check(all(row["action_licensed_before"] == "0" for row in targets if row["target_family"] in {"FREE_DY", "NAKED_Y"}), "free y/dy never action licensed")
    audit.check(Counter(row["dispatch_class"] for row in targets if row["target_family"] == "NAKED_Y") == {"RIGHT_REFERENCE": 3, "LINE_STOP": 1}, "three y references and one stop")
    audit.check(all(row["dy_contribution"] == "ACTION_FROM_WHOLE__DY_ONLY_ENDPOINT" for row in targets if row["target_family"] == "BOUND_DY" and row["dispatch_class"].startswith("ACTION_")), "bound actions licensed by whole")
    audit.check(all(row["dy_contribution"] == "FINISHED_ENDPOINT_NOT_NEW_VERB" for row in targets if row["target_family"] == "BOUND_DY" and row["dispatch_class"].startswith("NOMINAL_")), "bound nominal dy marks endpoint")
    bound_targets = [row for row in targets if row["target_family"] == "BOUND_DY"]
    audit.check((sum(row["dispatch_class"].startswith("ACTION_") for row in bound_targets), sum(row["dispatch_class"].startswith("NOMINAL_") for row in bound_targets)) == (15, 59), "bound dy 15 actions 59 results")
    qody = next(row for row in targets if row["surface"] == "qody")
    audit.check(qody["locus"] == "f105r.2" and qody["ordinal"] == "13", "one keyed qody")
    audit.check(qody["action_licensed_before"] == "1" and qody["dispatch_class"] == "NOMINAL_FINISHED_RESULT_STATE", "qody dy-only action demoted")
    audit.check(qody["v60_literal_gloss_de"] == "fertige Zubereitung", "qody concrete result")
    audit.check(all("abschließ" not in row["v60_literal_gloss_de"].lower() and "geschlossen" not in row["v60_literal_gloss_de"].lower() for row in targets), "no target creates spoken close verb")

    current_dchey = [row for row in targets if row["target_family"] == "DCHEY"]
    audit.check((sum(row["dispatch_class"].startswith("ACTION_") for row in current_dchey), sum(row["dispatch_class"].startswith("NOMINAL_") for row in current_dchey)) == (9, 5), "current dchey 9 actions 5 results")
    audit.check(len(dchey) == len({(row["locus"], row["ordinal"]) for row in dchey}) == 15, "15 global dchey occurrences")
    audit.check(Counter(row["dispatch_class"] for row in dchey) == {
        "ACTION_DRY_MEASURED_PORTION_TO_MIDDLE": 10,
        "NOMINAL_FINISHED_MIDDLE_DRY_PORTION": 5,
    }, "global dchey 10 actions 5 results")
    audit.check(Counter(row["reader_support"] for row in dchey) == {"BOTH_EXACT": 13, "ONE_EXACT": 2}, "dchey alternate-reader support")
    audit.check(sum(row["page"] == "f81r" for row in dchey) == 1, "one global-only f81r source")

    audit.check(len(bound) == 60, "60 bound-dy surface summaries")
    audit.check(sum(int(row["positions"]) for row in bound) == 74, "74 bound-dy positions")
    audit.check(sum(int(row["action_positions"]) for row in bound) == 15, "15 bound-dy action positions")
    audit.check(sum(int(row["result_positions"]) for row in bound) == 59, "59 bound-dy result positions")
    audit.check(next(row for row in bound if row["surface"] == "qody")["action_positions"] == "0", "qody absent from bound actions")
    audit.check(sum(int(row["occurrences"]) for row in y_prior) == 270 and len(y_prior) == 8, "270-position eight-class y prior")
    audit.check(len(dy_prior) == 1 and dy_prior[0]["occurrence_count"] == "705", "705 formal-DY prior")
    audit.check(dy_prior[0]["v60_bound_action_positions"] == "15" and dy_prior[0]["v60_bound_result_positions"] == "59" and dy_prior[0]["v60_free_boundary_positions"] == "3", "DY prior remains separately labeled")
    audit.check(len(distinction) == 4, "four GDT559 distinction classes")
    audit.check(all(row["v60_use"] in {"Y_ARGUMENT_OR_REFERENCE", "DY_ENDPOINT_CONTROL"} for row in distinction), "Y and DY remain distinct")

    audit.check(len(v59) == len(v60) == 51, "51-line reader preserved")
    audit.check(sum(int(row["token_count"]) for row in v60) == 479, "479 token positions preserved")
    audit.check(sum(int(row["v60_semantic_revisions"]) for row in v60) == 95, "95 revisions recorded")
    audit.check(sum(int(row["v60_semantic_revisions"]) > 0 for row in v60) == 40, "40 revised lines recorded")
    audit.check(sum(int(row["action_positions"]) for row in v59) == 86, "V59 had 86 action licenses")
    audit.check(sum(int(row["action_positions"]) for row in v60) == 85, "V60 has 85 action licenses")
    changed_literal: set[tuple[str, int]] = set()
    expected_changed = {(row["locus"], int(row["ordinal"])) for row in targets if row["v59_literal_gloss_de"] != row["v60_literal_gloss_de"]}
    for old, new in zip(v59, v60):
        audit.check(old["locus"] == new["locus"] and old["zl3b_line"] == new["zl3b_line"], "line order and source preserved")
        tokens = old["zl3b_line"].split()
        old_glosses = old["literal_token_glosses_de"].split(" | ")
        new_glosses = new["literal_token_glosses_de"].split(" | ")
        audit.check(len(tokens) == len(old_glosses) == len(new_glosses), f"token alignment {old['locus']}")
        for ordinal, (before, after) in enumerate(zip(old_glosses, new_glosses), 1):
            if before != after:
                changed_literal.add((old["locus"], ordinal))
        old_actions = int_set(old["action_ordinals"])
        new_actions = int_set(new["action_ordinals"])
        if old["locus"] == "f105r.2":
            audit.check(old_actions - new_actions == {13} and new_actions - old_actions == set(), "only qody action removed")
        else:
            audit.check(old_actions == new_actions, f"actions preserved {old['locus']}")
    audit.check(changed_literal == expected_changed and len(changed_literal) == 94, "exactly 94 changed literal strings")
    audit.check(all(key in keys for key in changed_literal), "no non-target literal changed")
    audit.check(len(patched) == 40 and all(row["v59_practical_translation_de"] != row["v60_practical_translation_de"] for row in patched), "40 practical lines rerendered")
    patched_by_locus = {row["locus"]: row for row in patched}
    audit.check("fertigstellen" not in patched_by_locus["f105r.2"]["v60_practical_translation_de"].lower(), "qody no longer says fertigstellen")
    audit.check("posten schließen" not in patched_by_locus["f26r.2"]["v60_practical_translation_de"].lower(), "free dy no longer says Posten schließen")
    audit.check("abschließen" not in patched_by_locus["f86v3.18"]["v60_practical_translation_de"].lower(), "nominal dy line no longer says abschließen")

    audit.check(len(debt_delta) == 95, "95 debt-delta rows")
    audit.check(sum(int(row["strict_cleared"]) for row in debt_delta) == 14, "14 strict debts cleared")
    audit.check(sum(int(row["mechanical_memberships_cleared"]) for row in debt_delta) == 15, "15 mechanical memberships cleared")
    audit.check(sum(int(row["specificity_cleared"]) for row in debt_delta) == 39, "39 specificity debts cleared")
    audit.check(sum(int(row["four_layer_position_cleared"]) for row in debt_delta) == 40, "40 four-layer positions cleared")
    audit.check(Counter(row["remaining_debt"] for row in debt_delta) == {"NONE": 72, "STATE_ONLY_NO_OBJECT": 22, "LOW_CONFIDENCE": 1}, "remaining target debt visible")
    summary = {row["metric"]: (int(row["v59_before"]), int(row["v60_after"])) for row in debt_summary}
    audit.check(summary == {
        "strict_card_debt_positions": (120, 106),
        "mechanical_visible_debt_union_positions": (163, 152),
        "mechanical_flag_memberships": (177, 162),
        "broad_specificity_open_positions": (324, 285),
        "four_layer_union_with_low_confidence_positions": (370, 330),
        "without_current_debt_or_confidence_signal": (109, 149),
    }, "V59 to V60 debt summary exact")
    audit.check(len(hypotheses) == 7 and sum(row["decision"] == "SELECT" for row in hypotheses) == 2, "two selected dispatch hypotheses")
    audit.check(len(counterexamples) >= 6, "counterexample deck present")

    audit.check(result["status"] == "PASS_95_POSITION_SCOPE_DISPATCH__V60_24_ACTION_64_RESULT_3_REFERENCE_4_BOUNDARY", "result status")
    audit.check(result["basis"] == {
        "bound_dy_positions": 74,
        "dchey_current_positions": 14,
        "dchey_global_positions_including_f81r_source": 15,
        "dy_family_current_positions": 77,
        "f84_access": 0,
        "f84r_access": 0,
        "formal_dy_prior_occurrences": 705,
        "free_dy_positions": 3,
        "global_naked_y_prior_positions": 270,
        "naked_y_current_positions": 4,
        "new_pages": 0,
        "target_lines": 40,
        "target_positions": 95,
        "v59_lines": 51,
        "v59_positions": 479,
        "y_dy_joint_formal_cards": 28,
    }, "result basis exact")
    audit.check(result["dispatch"] == {
        "action_positions": 24,
        "bound_dy_actions": 15,
        "bound_dy_results": 59,
        "dchey_actions_global": 10,
        "dchey_results_global": 5,
        "finished_result_or_state_positions": 64,
        "right_reference_positions": 3,
        "structural_boundary_positions": 4,
    }, "result dispatch exact")
    audit.check(result["v60"] == {
        "broad_specificity_after": 285,
        "clean_positions_after": 149,
        "four_layer_union_after": 330,
        "lines_revised": 40,
        "mechanical_debt_union_after": 152,
        "mechanical_memberships_after": 162,
        "positions_revised": 95,
        "remaining_low_confidence_targets": 1,
        "remaining_state_without_object_targets": 22,
        "source_action_positions_after": 85,
        "source_action_positions_before": 86,
        "strict_debt_positions_after": 106,
    }, "result V60 exact")
    audit.check("Exploratory replaceable workshop renderer" in result["claim_ceiling"], "exploratory claim ceiling retained")
    for name, digest in result["files"].items():
        audit.check(sha256(ART / name) == digest, f"hash bound {name}")

    validation = {
        "status": "PASS",
        "checks": audit.checks,
        "byte_rebuilds": len(generated) + 1,
        "v60_positions": 479,
        "target_positions": 95,
        "target_lines": 40,
        "action_positions": 24,
        "finished_result_or_state_positions": 64,
        "right_reference_positions": 3,
        "structural_boundary_positions": 4,
        "source_action_positions_after": 85,
        "strict_debt_positions_after": 106,
        "mechanical_debt_union_after": 152,
        "four_layer_union_after": 330,
        "sealed_pages_absent": True,
    }
    (ART / "VALIDATION.json").write_text(json.dumps(validation, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(validation, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
