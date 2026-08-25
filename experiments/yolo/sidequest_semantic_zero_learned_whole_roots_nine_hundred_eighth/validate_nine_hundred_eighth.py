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
BASE = HERE.parent / "sidequest_semantic_single_learned_whole_root_nine_hundred_seventh"
PFX = "NINE_HUNDRED_EIGHTH"
PFX7 = "NINE_HUNDRED_SEVENTH"
TARGET = "PROC043"
PAGES = {"f10r", "f11r", "f55v", "f56r", "f81v", "f82r", "f83r", "f67r2", "f68r1", "f69v"}

OUTPUTS = {
    "symbols": HERE / f"{PFX}_46_COMPLETE_SYMBOL_DICTIONARY.tsv",
    "patterns": HERE / f"{PFX}_7_CARD_PATTERNS.tsv",
    "rules": HERE / f"{PFX}_14_RENDERER_RULES.tsv",
    "micro": HERE / f"{PFX}_36_FUNCTIONAL_ALLOGRAPHS.tsv",
    "contractions": HERE / f"{PFX}_2_COMPOSITIONAL_CONTRACTIONS.tsv",
    "last": HERE / f"{PFX}_1_LAST_ROOT_COMPOSITION.tsv",
    "dictionary": HERE / f"{PFX}_231_ZERO_WHOLE_ROOT_CARD_DICTIONARY.tsv",
    "marks": HERE / f"{PFX}_437_ZERO_WHOLE_ROOT_INTERLINEAR.tsv",
    "units": HERE / f"{PFX}_118_ZERO_WHOLE_ROOT_UNITS.tsv",
    "page_units": HERE / f"{PFX}_115_DEDUPED_PAGE_UNITS.tsv",
    "cards": HERE / f"{PFX}_6_COMPLETE_JOB_CARDS.tsv",
    "workflow": HERE / f"{PFX}_12_STEP_WORKFLOW.tsv",
    "handbook": HERE / f"{PFX}_ZERO_WHOLE_ROOT_SCRIBE_HANDBOOK.md",
    "edition": HERE / f"{PFX}_TEN_PAGE_WORKING_EDITION.md",
    "report": HERE / f"{PFX}_REPORT.md",
    "summary": HERE / f"{PFX}_BUILD_SUMMARY.json",
}

BASE_FILES = {
    "symbols": BASE / f"{PFX7}_47_COMPLETE_SYMBOL_DICTIONARY.tsv",
    "patterns": BASE / f"{PFX7}_8_CARD_PATTERNS.tsv",
    "rules": BASE / f"{PFX7}_15_RENDERER_RULES.tsv",
    "micro": BASE / f"{PFX7}_36_FUNCTIONAL_ALLOGRAPHS.tsv",
    "contractions": BASE / f"{PFX7}_2_COMPOSITIONAL_CONTRACTIONS.tsv",
    "dictionary": BASE / f"{PFX7}_231_SINGLE_WHOLE_ROOT_CARD_DICTIONARY.tsv",
    "marks": BASE / f"{PFX7}_437_SINGLE_WHOLE_ROOT_INTERLINEAR.tsv",
    "units": BASE / f"{PFX7}_118_SINGLE_WHOLE_ROOT_UNITS.tsv",
    "cards": BASE / f"{PFX7}_6_COMPLETE_JOB_CARDS.tsv",
    "workflow": BASE / f"{PFX7}_12_STEP_WORKFLOW.tsv",
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

    counts = {"symbols": 46, "patterns": 7, "rules": 14, "micro": 36, "contractions": 2,
              "last": 1, "dictionary": 231, "marks": 437, "units": 118,
              "page_units": 115, "cards": 6, "workflow": 12}
    for key, expected in counts.items():
        check(f"count_{key}_{expected}", len(out[key]) == expected)

    check("talam_symbol_removed", "TALAM" not in {row["symbol"] for row in out["symbols"]})
    check("symbol_set_base_minus_talam", {row["symbol"] for row in out["symbols"]} == {row["symbol"] for row in base["symbols"]} - {"TALAM"})
    check("micro_unchanged", out["micro"] == base["micro"])
    check("contractions_unchanged", out["contractions"] == base["contractions"])
    check("workflow_unchanged", out["workflow"] == base["workflow"])

    last = out["last"][0]
    check("last_parse_exact", last["identity"] == TARGET and last["surface"] == "talam" and last["new_parse"] == "T+AL+AM_ADDR")
    check("last_reading_exact", last["atomic_reading_de"] == "BEARBEITEN · ZIELSTELLE · GEGENFELD")

    pattern_counts = {row["pattern"]: (int(row["identity_count"]), int(row["mark_count"])) for row in out["patterns"]}
    check("whole_pattern_removed", "WHOLE_LEXICON" not in pattern_counts)
    check("operation_pattern_absorbs_talam", pattern_counts["OPERATION_INSTRUCTION"] == (77, 137))
    check("pattern_sums_231_437", sum(v[0] for v in pattern_counts.values()) == 231 and sum(v[1] for v in pattern_counts.values()) == 437)
    check("pattern_precedence_contiguous", [int(row["precedence"]) for row in out["patterns"]] == list(range(1, 8)))

    rule_names = [row["renderer_rule"] for row in out["rules"]]
    check("memorized_rule_removed", "MEMORIZED_WHOLE_FORM" not in rule_names)
    check("rule_precedence_contiguous", [int(row["precedence"]) for row in out["rules"]] == list(range(1, 15)))
    rule_by_name = {row["renderer_rule"]: row for row in out["rules"]}
    check("root_copy_covers_all", rule_by_name["ROOT_ORDER_COPY"]["identity_count"] == "231" and rule_by_name["ROOT_ORDER_COPY"]["mark_count"] == "437")

    dictionary = {row["identity"]: row for row in out["dictionary"]}
    base_dictionary = {row["identity"]: row for row in base["dictionary"]}
    check("dictionary_ids_exact", set(dictionary) == set(base_dictionary) and len(dictionary) == 231)
    talam = dictionary[TARGET]
    check("talam_dictionary_parse", talam["component_recipe"] == "T+AL+AM_ADDR" and talam["slot_signature"] == "OPERATION>ADDRESS>ADDRESS")
    check("talam_dictionary_reading", talam["dictionary_value_de"] == "GEGENSTELLE BEARBEITEN" and talam["primary_card_pattern"] == "OPERATION_INSTRUCTION")
    check("no_memorized_dictionary_rows", all(row["renderability"] != "MEMORIZED_EXACT_FORM" for row in out["dictionary"]))
    check("no_whole_dictionary_pattern", all(row["primary_card_pattern"] != "WHOLE_LEXICON" for row in out["dictionary"]))
    shared_dictionary_fields = list(base["dictionary"][0])
    check("other_230_dictionary_rows_unchanged", all(
        all(dictionary[identity][field] == row[field] for field in shared_dictionary_fields)
        for identity, row in base_dictionary.items() if identity != TARGET
    ))

    marks = {row["order_mark_id"]: row for row in out["marks"]}
    base_marks = {row["order_mark_id"]: row for row in base["marks"]}
    check("mark_ids_exact", set(marks) == set(base_marks) and len(marks) == 437)
    target_mark = next(row for row in out["marks"] if row["identity"] == TARGET)
    check("one_talam_mark", sum(row["identity"] == TARGET for row in out["marks"]) == 1)
    check("talam_mark_parse", target_mark["component_recipe"] == "T+AL+AM_ADDR" and target_mark["renderer_skeleton"] == "t-al-am")
    check("talam_mark_root_action", target_mark["reading_action"] == "READ_ROOT_COMPOSITION")
    check("no_memorized_mark", all(row["renderability"] != "MEMORIZED_EXACT_FORM" for row in out["marks"]))
    check("no_whole_read_action", all("WHOLE" not in row["reading_action"] for row in out["marks"]))
    check("surface_prediction_exact", all(row["surface"] == row["predicted_surface"] for row in out["marks"]))
    check("mark_renderability_exact", Counter(row["renderability"] for row in out["marks"]) == Counter({
        "COMPOSITIONAL_SINGLE_ATTESTED_RENDERING": 293,
        "COMPOSITIONAL_FAMILY__ALLOGRAPH_CHOICE": 142,
        "COMPOSITIONAL_SINGLE_WITH_LOCAL_CONTRACTION": 2,
    }))
    check("mark_actions_exact", Counter(row["reading_action"] for row in out["marks"]) == Counter({
        "READ_SHARED_CORE": 251, "READ_ROOT_COMPOSITION": 113, "READ_LOCAL_CONDITION_WORD": 73,
    }))
    shared_mark_fields = list(base["marks"][0])
    check("other_marks_only_unit_sentence_reworded", all(
        all(
            marks[mark_id][field] == row[field]
            for field in shared_mark_fields
            if not (row["order_id"] == "WH04" and row["unit"] == "H4-S002" and field == "unit_fluent_instruction_de")
        )
        for mark_id, row in base_marks.items() if row["identity"] != TARGET
    ))

    unit_by_key = {(row["order_id"], row["unit"]): row for row in out["units"]}
    target_unit = unit_by_key[("WH04", "H4-S002")]
    check("target_unit_new_literal", target_unit["literal_sequence_de"].endswith("GEGENSTELLE BEARBEITEN"))
    check("target_unit_new_sentence", "an der Gegenstelle weiterbearbeiten" in target_unit["front_instruction_de"])
    check("target_unit_new_root_sequence", target_unit["root_reading_sequence_de"].endswith("BEARBEITEN · ZIELSTELLE · GEGENFELD"))
    check("all_unit_whole_counts_zero", all(row["fused_whole_form_marks"] == "0" and row["learned_whole_root_marks"] == "0" for row in out["units"]))
    marks_by_unit: dict[tuple[str, str], list[dict[str, str]]] = defaultdict(list)
    for row in out["marks"]:
        marks_by_unit[(row["order_id"], row["unit"])].append(row)
    check("unit_surfaces_align_marks", all(row["fifth_hand_surface_sequence"].split() == [mark["surface"] for mark in marks_by_unit[(row["order_id"], row["unit"])]] for row in out["units"]))
    check("unit_roots_align_marks", all(row["root_reading_sequence_de"].split(" ; ") == [mark["atomic_root_reading_de"] for mark in marks_by_unit[(row["order_id"], row["unit"])]] for row in out["units"]))

    page_keys = [(row["page"], row["unit"]) for row in out["page_units"]]
    check("page_units_unique", len(page_keys) == len(set(page_keys)))
    check("page_unit_copy_sum_118", sum(int(row["source_unit_copies"]) for row in out["page_units"]) == 118)
    check("page_set_exact", {row["page"] for row in out["page_units"]} == PAGES)
    check("sealed_pages_absent", not ({"f84", "f84r"} & ({row["page"] for row in out["marks"]} | {row["page"] for row in out["page_units"]})))
    check("all_job_whole_counts_zero", all(row["fused_whole_form_marks"] == "0" and row["learned_whole_root_marks"] == "0" and "WHOLE_LEXICON" not in row["pattern_counts"] and "MEMORIZED_EXACT_FORM" not in row["renderer_classes"] for row in out["cards"]))

    check("summary_pass", summary["status"] == "PASS")
    check("summary_zero_whole", summary["learned_whole_roots"] == 0)
    check("summary_35_roots_11_helpers", summary["semantic_roots"] == 35 and summary["helper_signs"] == 11)
    check("summary_7_patterns_14_rules", summary["card_patterns"] == 7 and summary["renderer_rules"] == 14)
    check("summary_no_new_roots_pages", summary["new_roots"] == 0 and summary["new_pages"] == 0)
    check("handbook_states_zero_whole", "kein gelerntes Ganzwort" in OUTPUTS["handbook"].read_text(encoding="utf-8"))
    edition = OUTPUTS["edition"].read_text(encoding="utf-8")
    check("edition_has_ten_pages", all(f"## {page}:" in edition for page in PAGES))

    before = {key: sha256(path) for key, path in OUTPUTS.items()}
    subprocess.run([sys.executable, str(HERE / "build_nine_hundred_eighth.py")], cwd=HERE.parents[2], check=True)
    after = {key: sha256(path) for key, path in OUTPUTS.items()}
    check("deterministic_rebuild", before == after)

    result = {
        "status": "PASS" if not failures else "FAIL", "decision": summary["decision"],
        "checks_passed": sum(checks.values()), "checks_total": len(checks), "failures": failures,
        "counts": counts, "output_sha256": after, "checks": checks,
    }
    (HERE / f"{PFX}_VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({key: result[key] for key in ["status", "checks_passed", "checks_total", "failures"]}, ensure_ascii=False, indent=2))
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
