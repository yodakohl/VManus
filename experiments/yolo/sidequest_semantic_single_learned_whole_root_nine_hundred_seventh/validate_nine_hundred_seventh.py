#!/usr/bin/env python3
from __future__ import annotations

import csv
import hashlib
import json
import subprocess
import sys
from collections import Counter, defaultdict
from pathlib import Path


HERE = Path(__file__).resolve().parent
BASE = HERE.parent / "sidequest_semantic_last_whole_word_composition_nine_hundred_sixth"
PFX = "NINE_HUNDRED_SEVENTH"
PFX6 = "NINE_HUNDRED_SIXTH"
TARGETS = {"A3:G047", "PROC041", "PROC052", "PROC109", "PROC157"}
PAGES = {"f10r", "f11r", "f55v", "f56r", "f81v", "f82r", "f83r", "f67r2", "f68r1", "f69v"}

OUTPUTS = {
    "symbols": HERE / f"{PFX}_47_COMPLETE_SYMBOL_DICTIONARY.tsv",
    "patterns": HERE / f"{PFX}_8_CARD_PATTERNS.tsv",
    "rules": HERE / f"{PFX}_15_RENDERER_RULES.tsv",
    "micro": HERE / f"{PFX}_36_FUNCTIONAL_ALLOGRAPHS.tsv",
    "contractions": HERE / f"{PFX}_2_COMPOSITIONAL_CONTRACTIONS.tsv",
    "whole": HERE / f"{PFX}_1_LEARNED_WHOLE_ROOT.tsv",
    "dictionary": HERE / f"{PFX}_231_SINGLE_WHOLE_ROOT_CARD_DICTIONARY.tsv",
    "marks": HERE / f"{PFX}_437_SINGLE_WHOLE_ROOT_INTERLINEAR.tsv",
    "units": HERE / f"{PFX}_118_SINGLE_WHOLE_ROOT_UNITS.tsv",
    "page_units": HERE / f"{PFX}_115_DEDUPED_PAGE_UNITS.tsv",
    "cards": HERE / f"{PFX}_6_COMPLETE_JOB_CARDS.tsv",
    "workflow": HERE / f"{PFX}_12_STEP_WORKFLOW.tsv",
    "handbook": HERE / f"{PFX}_SINGLE_WHOLE_ROOT_SCRIBE_HANDBOOK.md",
    "edition": HERE / f"{PFX}_TEN_PAGE_WORKING_EDITION.md",
    "report": HERE / f"{PFX}_REPORT.md",
    "summary": HERE / f"{PFX}_BUILD_SUMMARY.json",
}

BASE_FILES = {
    "symbols": BASE / f"{PFX6}_47_COMPLETE_SYMBOL_DICTIONARY.tsv",
    "patterns": BASE / f"{PFX6}_8_CARD_PATTERNS.tsv",
    "rules": BASE / f"{PFX6}_15_RENDERER_RULES.tsv",
    "micro": BASE / f"{PFX6}_36_FUNCTIONAL_ALLOGRAPHS.tsv",
    "contractions": BASE / f"{PFX6}_2_COMPOSITIONAL_CONTRACTIONS.tsv",
    "dictionary": BASE / f"{PFX6}_231_ZERO_WHOLE_CONDITION_CARD_DICTIONARY.tsv",
    "marks": BASE / f"{PFX6}_437_ZERO_WHOLE_CONDITION_INTERLINEAR.tsv",
    "units": BASE / f"{PFX6}_118_ZERO_WHOLE_CONDITION_UNITS.tsv",
    "cards": BASE / f"{PFX6}_6_COMPLETE_JOB_CARDS.tsv",
    "workflow": BASE / f"{PFX6}_12_STEP_WORKFLOW.tsv",
}


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def main() -> int:
    out = {key: read(path) for key, path in OUTPUTS.items() if path.suffix == ".tsv"}
    base = {key: read(path) for key, path in BASE_FILES.items()}
    summary = json.loads(OUTPUTS["summary"].read_text(encoding="utf-8"))
    checks: dict[str, bool] = {}
    failures: list[str] = []

    def check(name: str, condition: bool) -> None:
        checks[name] = bool(condition)
        if not condition:
            failures.append(name)

    counts = {"symbols": 47, "patterns": 8, "rules": 15, "micro": 36, "contractions": 2,
              "whole": 1, "dictionary": 231, "marks": 437, "units": 118,
              "page_units": 115, "cards": 6, "workflow": 12}
    for key, value in counts.items():
        check(f"count_{key}_{value}", len(out[key]) == value)

    check("symbols_same_set", {row["symbol"] for row in out["symbols"]} == {row["symbol"] for row in base["symbols"]})
    check("contractions_unchanged", out["contractions"] == base["contractions"])
    check("workflow_unchanged", out["workflow"] == base["workflow"])
    check("sole_whole_is_talam", out["whole"] == [{
        "identity": "PROC043", "surface": "talam", "root": "TALAM", "meaning_de": "BEISEITESTELLEN",
        "marks": "1", "page": "f55v", "reason_de": "Kein zweiter stabiler Kern zerlegt die Karte kürzer; als einzelnes Werkstattwort lernen.",
    }])

    pattern_counts = {row["pattern"]: (int(row["identity_count"]), int(row["mark_count"])) for row in out["patterns"]}
    expected_patterns = {
        "WHOLE_LEXICON": (1, 1), "CLOSING_INSTRUCTION": (40, 93),
        "ORDERED_INSTRUCTION": (32, 58), "OPERATION_INSTRUCTION": (76, 136),
        "TRANSFER_OR_PATH": (19, 23), "STATE_OR_GRADE": (25, 41),
        "ARGUMENT_OR_ADDRESS": (24, 58), "REFERENT_OR_LABEL": (14, 27),
    }
    check("pattern_counts_exact", pattern_counts == expected_patterns)
    check("pattern_sums_exact", sum(v[0] for v in pattern_counts.values()) == 231 and sum(v[1] for v in pattern_counts.values()) == 437)

    dictionary = {row["identity"]: row for row in out["dictionary"]}
    base_dictionary = {row["identity"]: row for row in base["dictionary"]}
    check("dictionary_ids_exact", set(dictionary) == set(base_dictionary) and len(dictionary) == 231)
    check("only_one_memorized_dictionary_identity", [row["identity"] for row in out["dictionary"] if row["renderability"] == "MEMORIZED_EXACT_FORM"] == ["PROC043"])
    check("all_five_targets_not_memorized", all(dictionary[identity]["renderability"] != "MEMORIZED_EXACT_FORM" for identity in TARGETS))
    check("a3_cheey_reparsed", dictionary["A3:G047"]["component_recipe"] == "SH+EE+Y" and dictionary["A3:G047"]["primary_card_pattern"] == "STATE_OR_GRADE")
    check("ody_reparsed", dictionary["PROC041"]["primary_card_pattern"] == "CLOSING_INSTRUCTION")
    check("cho_reparsed", dictionary["PROC052"]["primary_card_pattern"] == "ARGUMENT_OR_ADDRESS")
    check("oteey_reparsed", dictionary["PROC109"]["primary_card_pattern"] == "ORDERED_INSTRUCTION")
    check("sheey_reparsed", dictionary["PROC157"]["primary_card_pattern"] == "STATE_OR_GRADE")
    shared_dictionary_fields = list(base["dictionary"][0])
    check("other_226_dictionary_rows_unchanged", all(
        all(dictionary[identity][field] == row[field] for field in shared_dictionary_fields)
        for identity, row in base_dictionary.items() if identity not in TARGETS
    ))

    marks = {row["order_mark_id"]: row for row in out["marks"]}
    base_marks = {row["order_mark_id"]: row for row in base["marks"]}
    check("mark_ids_exact", set(marks) == set(base_marks) and len(marks) == 437)
    target_marks = [row for row in out["marks"] if row["identity"] in TARGETS]
    check("seven_target_marks", len(target_marks) == 7)
    check("no_fused_whole_action", all(row["reading_action"] != "READ_FUSED_WHOLE_WORD" for row in out["marks"]))
    check("only_talam_learned_action", [row["identity"] for row in out["marks"] if row["reading_action"] == "READ_LEARNED_WHOLE_ROOT"] == ["PROC043"])
    check("surface_prediction_exact", all(row["surface"] == row["predicted_surface"] for row in out["marks"]))
    expected_mark_renderability = Counter({
        "COMPOSITIONAL_SINGLE_ATTESTED_RENDERING": 292,
        "COMPOSITIONAL_FAMILY__ALLOGRAPH_CHOICE": 142,
        "COMPOSITIONAL_SINGLE_WITH_LOCAL_CONTRACTION": 2,
        "MEMORIZED_EXACT_FORM": 1,
    })
    check("mark_renderability_exact", Counter(row["renderability"] for row in out["marks"]) == expected_mark_renderability)
    check("mark_actions_exact", Counter(row["reading_action"] for row in out["marks"]) == Counter({
        "READ_SHARED_CORE": 251, "READ_ROOT_COMPOSITION": 112,
        "READ_LOCAL_CONDITION_WORD": 73, "READ_LEARNED_WHOLE_ROOT": 1,
    }))
    shared_mark_fields = list(base["marks"][0])
    check("other_430_mark_rows_unchanged", all(
        all(marks[mark_id][field] == row[field] for field in shared_mark_fields)
        for mark_id, row in base_marks.items() if row["identity"] not in TARGETS
    ))

    unit_keys = [(row["order_id"], row["unit"]) for row in out["units"]]
    check("unit_keys_unique", len(unit_keys) == len(set(unit_keys)))
    marks_by_unit: dict[tuple[str, str], list[dict[str, str]]] = defaultdict(list)
    for row in out["marks"]:
        marks_by_unit[(row["order_id"], row["unit"])].append(row)
    check("every_unit_surface_sequence_matches_marks", all(
        row["fifth_hand_surface_sequence"].split() == [mark["surface"] for mark in marks_by_unit[(row["order_id"], row["unit"])]]
        for row in out["units"]
    ))
    check("every_unit_pattern_sequence_matches_dictionary", all(
        row["card_pattern_sequence"].split(" -> ") == [dictionary[mark["identity"]]["primary_card_pattern"] for mark in marks_by_unit[(row["order_id"], row["unit"])]]
        for row in out["units"]
    ))
    check("every_unit_root_sequence_matches_marks", all(
        row["root_reading_sequence_de"].split(" ; ") == [mark["atomic_root_reading_de"] for mark in marks_by_unit[(row["order_id"], row["unit"])]]
        for row in out["units"]
    ))
    check("all_unit_fused_counts_zero", all(row["fused_whole_form_marks"] == "0" for row in out["units"]))
    check("unit_learned_count_sum_one", sum(int(row["learned_whole_root_marks"]) for row in out["units"]) == 1)

    page_keys = [(row["page"], row["unit"]) for row in out["page_units"]]
    check("page_units_unique", len(page_keys) == len(set(page_keys)))
    check("page_unit_copy_sum_118", sum(int(row["source_unit_copies"]) for row in out["page_units"]) == 118)
    check("page_set_exact", {row["page"] for row in out["page_units"]} == PAGES)
    check("sealed_pages_absent", not ({"f84", "f84r"} & ({row["page"] for row in out["marks"]} | {row["page"] for row in out["page_units"]})))

    check("six_job_orders_unique", len({row["order_id"] for row in out["cards"]}) == 6)
    check("job_fused_counts_zero", all(row["fused_whole_form_marks"] == "0" for row in out["cards"]))
    check("job_learned_count_sum_one", sum(int(row["learned_whole_root_marks"]) for row in out["cards"]) == 1)

    general_long = next(row for row in out["micro"] if row["component_recipe"] == "SH+EE+Y" and row["surface"] == "cheey")
    check("general_long_allograph_absorbs_a3", general_long["occurrence_marks"] == "6" and "A3:G047" in general_long["identities"] and "f69v" in general_long["pages"])

    check("summary_pass", summary["status"] == "PASS")
    check("summary_one_whole", summary["learned_whole_roots"] == 1)
    check("summary_recipe_count_190", summary["component_recipes"] == 190)
    check("summary_no_new_roots_pages", summary["new_roots"] == 0 and summary["new_pages"] == 0)
    check("handbook_names_talam_only", "Nur `talam`" in OUTPUTS["handbook"].read_text(encoding="utf-8"))
    edition_text = OUTPUTS["edition"].read_text(encoding="utf-8")
    check("edition_has_all_pages", all(f"## {page}:" in edition_text for page in PAGES))

    before = {key: sha256(path) for key, path in OUTPUTS.items()}
    subprocess.run([sys.executable, str(HERE / "build_nine_hundred_seventh.py")], cwd=HERE.parents[2], check=True)
    after = {key: sha256(path) for key, path in OUTPUTS.items()}
    check("deterministic_rebuild", before == after)

    result = {
        "status": "PASS" if not failures else "FAIL",
        "decision": summary["decision"],
        "checks_passed": sum(checks.values()), "checks_total": len(checks),
        "failures": failures, "counts": counts, "output_sha256": after, "checks": checks,
    }
    (HERE / f"{PFX}_VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({key: result[key] for key in ["status", "checks_passed", "checks_total", "failures"]}, ensure_ascii=False, indent=2))
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
