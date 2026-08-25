#!/usr/bin/env python3
from __future__ import annotations

import csv
import hashlib
import json
import subprocess
import sys
from collections import Counter
from pathlib import Path


HERE = Path(__file__).resolve().parent
BASE = HERE.parent / "sidequest_semantic_complete_scribe_handbook_nine_hundred_fifth"
PFX = "NINE_HUNDRED_SIXTH"
PFX5 = "NINE_HUNDRED_FIFTH"
TARGETS = {"A3:G046", "A3:G056"}
PAGES = {"f10r", "f11r", "f55v", "f56r", "f81v", "f82r", "f83r", "f67r2", "f68r1", "f69v"}

OUTPUTS = {
    "symbols": HERE / f"{PFX}_47_COMPLETE_SYMBOL_DICTIONARY.tsv",
    "patterns": HERE / f"{PFX}_8_CARD_PATTERNS.tsv",
    "rules": HERE / f"{PFX}_15_RENDERER_RULES.tsv",
    "micro": HERE / f"{PFX}_36_FUNCTIONAL_ALLOGRAPHS.tsv",
    "contractions": HERE / f"{PFX}_2_COMPOSITIONAL_CONTRACTIONS.tsv",
    "dictionary": HERE / f"{PFX}_231_ZERO_WHOLE_CONDITION_CARD_DICTIONARY.tsv",
    "marks": HERE / f"{PFX}_437_ZERO_WHOLE_CONDITION_INTERLINEAR.tsv",
    "units": HERE / f"{PFX}_118_ZERO_WHOLE_CONDITION_UNITS.tsv",
    "page_units": HERE / f"{PFX}_115_DEDUPED_PAGE_UNITS.tsv",
    "cards": HERE / f"{PFX}_6_COMPLETE_JOB_CARDS.tsv",
    "workflow": HERE / f"{PFX}_12_STEP_WORKFLOW.tsv",
    "handbook": HERE / f"{PFX}_COMPLETE_COMPOSITIONAL_SCRIBE_HANDBOOK.md",
    "edition": HERE / f"{PFX}_TEN_PAGE_WORKING_EDITION.md",
    "report": HERE / f"{PFX}_REPORT.md",
    "summary": HERE / f"{PFX}_BUILD_SUMMARY.json",
}

BASE_FILES = {
    "symbols": BASE / f"{PFX5}_48_COMPLETE_SYMBOL_DICTIONARY.tsv",
    "patterns": BASE / f"{PFX5}_8_CARD_PATTERNS.tsv",
    "rules": BASE / f"{PFX5}_15_RENDERER_RULES.tsv",
    "micro": BASE / f"{PFX5}_38_ALLOGRAPH_MICROLEXICON.tsv",
    "dictionary": BASE / f"{PFX5}_231_COMPLETE_CARD_DICTIONARY.tsv",
    "marks": BASE / f"{PFX5}_437_COMPLETE_INTERLINEAR.tsv",
    "units": BASE / f"{PFX5}_118_COMPLETE_UNIT_EDITION.tsv",
    "cards": BASE / f"{PFX5}_6_COMPLETE_JOB_CARDS.tsv",
    "workflow": BASE / f"{PFX5}_12_STEP_WORKFLOW.tsv",
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

    expected_counts = {
        "symbols": 47, "patterns": 8, "rules": 15, "micro": 36,
        "contractions": 2, "dictionary": 231, "marks": 437,
        "units": 118, "page_units": 115, "cards": 6, "workflow": 12,
    }
    for key, value in expected_counts.items():
        check(f"count_{key}_{value}", len(out[key]) == value)

    check("none_placeholder_symbol_removed", "NONE" not in {row["symbol"] for row in out["symbols"]})
    check("symbol_set_is_base_minus_none", {row["symbol"] for row in out["symbols"]} == {row["symbol"] for row in base["symbols"]} - {"NONE"})
    check("all_functional_entries_retained", {row["renderer_microfunction"] for row in out["micro"]} == {row["renderer_microfunction"] for row in base["micro"] if row["entry_class"] != "LOCAL_WHOLE_WORD"})
    check("no_local_whole_micro_entry", all(row["entry_class"] != "LOCAL_WHOLE_WORD" for row in out["micro"]))

    contraction_by_id = {row["identity"]: row for row in out["contractions"]}
    check("contraction_identities_exact", set(contraction_by_id) == TARGETS)
    check("iokeeor_parse_exact", contraction_by_id.get("A3:G046", {}).get("component_recipe") == "OK+EE+OR")
    check("daiial_parse_exact", contraction_by_id.get("A3:G056", {}).get("component_recipe") == "DA+IIN+AL")
    check("contractions_use_no_new_root", all(set(row["component_recipe"].split("+")) <= {item["symbol"] for item in out["symbols"]} for row in out["contractions"]))

    pattern_counts = {row["pattern"]: (int(row["identity_count"]), int(row["mark_count"])) for row in out["patterns"]}
    check("whole_pattern_reduced", pattern_counts["WHOLE_LEXICON"] == (6, 8))
    check("operation_pattern_increased", pattern_counts["OPERATION_INSTRUCTION"] == (76, 136))
    check("state_pattern_increased", pattern_counts["STATE_OR_GRADE"] == (23, 39))
    check("pattern_identity_sum_231", sum(value[0] for value in pattern_counts.values()) == 231)
    check("pattern_mark_sum_437", sum(value[1] for value in pattern_counts.values()) == 437)

    dictionary_by_id = {row["identity"]: row for row in out["dictionary"]}
    base_dictionary_by_id = {row["identity"]: row for row in base["dictionary"]}
    check("dictionary_ids_unique", len(dictionary_by_id) == len(out["dictionary"]))
    check("dictionary_id_set_unchanged", set(dictionary_by_id) == set(base_dictionary_by_id))
    check("dictionary_no_none_recipe", all(row["component_recipe"] != "NONE" for row in out["dictionary"]))
    check("dictionary_no_local_whole_literal", all(row["atomic_root_reading_de"] != "LOKALES GANZWORT" for row in out["dictionary"]))
    check("iokeeor_dictionary_value", dictionary_by_id["A3:G046"]["dictionary_value_de"] == "LANGANSATZ")
    check("daiial_dictionary_value", dictionary_by_id["A3:G056"]["dictionary_value_de"] == "ZWEITE ZIELSTUFE")
    check("target_renderability_compositional", all(dictionary_by_id[identity]["renderability"] == "COMPOSITIONAL_SINGLE_WITH_LOCAL_CONTRACTION" for identity in TARGETS))
    shared_dictionary_fields = list(base["dictionary"][0])
    check(
        "all_229_other_dictionary_rows_unchanged",
        all(
            all(dictionary_by_id[identity][field] == row[field] for field in shared_dictionary_fields)
            for identity, row in base_dictionary_by_id.items() if identity not in TARGETS
        ),
    )

    marks_by_id = {row["order_mark_id"]: row for row in out["marks"]}
    base_marks_by_id = {row["order_mark_id"]: row for row in base["marks"]}
    check("mark_ids_unique", len(marks_by_id) == len(out["marks"]))
    check("mark_id_set_unchanged", set(marks_by_id) == set(base_marks_by_id))
    changed_marks = [row for row in out["marks"] if row["identity"] in TARGETS]
    check("exactly_two_changed_target_marks", len(changed_marks) == 2)
    check("target_mark_recipes_exact", {row["component_recipe"] for row in changed_marks} == {"OK+EE+OR", "DA+IIN+AL"})
    check("all_marks_surface_regenerated", all(row["surface"] == row["predicted_surface"] for row in out["marks"]))
    check("mark_renderability_counts", Counter(row["renderability"] for row in out["marks"]) == Counter({
        "COMPOSITIONAL_SINGLE_ATTESTED_RENDERING": 287,
        "COMPOSITIONAL_FAMILY__ALLOGRAPH_CHOICE": 140,
        "COMPOSITIONAL_SINGLE_WITH_LOCAL_CONTRACTION": 2,
        "MEMORIZED_EXACT_FORM": 8,
    }))
    shared_mark_fields = list(base["marks"][0])
    check(
        "all_435_other_mark_rows_unchanged",
        all(
            all(marks_by_id[mark_id][field] == row[field] for field in shared_mark_fields)
            for mark_id, row in base_marks_by_id.items() if row["identity"] not in TARGETS
        ),
    )

    unit_by_key = {(row["order_id"], row["stage"], row["unit"]): row for row in out["units"]}
    base_unit_by_key = {(row["order_id"], row["stage"], row["unit"]): row for row in base["units"]}
    check("unit_keys_unchanged", set(unit_by_key) == set(base_unit_by_key))
    changed_unit_key = next(key for key in unit_by_key if key[0] == "WH01" and key[2] == "f69v.2")
    target_unit = unit_by_key[changed_unit_key]
    check("condition_unit_has_langansatz", "LANGANSATZ" in target_unit["literal_sequence_de"])
    check("condition_unit_has_second_target_stage", "ZWEITE ZIELSTUFE" in target_unit["literal_sequence_de"])
    check("condition_unit_has_no_local_whole", "LOKALES GANZWORT" not in target_unit["root_reading_sequence_de"])
    unchanged_unit_fields = set(base["units"][0]) - {
        "literal_sequence_de", "root_reading_sequence_de", "speakable_condition_sequence_de",
        "card_pattern_sequence", "slot_signature_sequence", "renderer_skeleton_sequence",
        "renderability_sequence", "microfunction_sequence",
    }
    check(
        "target_unit_only_derived_fields_changed",
        all(target_unit[field] == base_unit_by_key[changed_unit_key][field] for field in unchanged_unit_fields),
    )
    check(
        "all_117_other_units_unchanged",
        all(unit_by_key[key] == row for key, row in base_unit_by_key.items() if key != changed_unit_key),
    )

    page_unit_keys = [(row["page"], row["unit"]) for row in out["page_units"]]
    check("page_unit_keys_unique", len(page_unit_keys) == len(set(page_unit_keys)))
    check("page_set_exact", {row["page"] for row in out["page_units"]} == PAGES)
    check("page_unit_copy_sum_118", sum(int(row["source_unit_copies"]) for row in out["page_units"]) == 118)
    check("only_fixed_pages", {row["page"] for row in out["marks"]} <= PAGES and {row["page"] for row in out["page_units"]} <= PAGES)
    check("sealed_pages_absent", not ({"f84", "f84r"} & ({row["page"] for row in out["marks"]} | {row["page"] for row in out["page_units"]})))

    card_by_order = {row["order_id"]: row for row in out["cards"]}
    base_card_by_order = {row["order_id"]: row for row in base["cards"]}
    check("card_orders_unchanged", set(card_by_order) == set(base_card_by_order))
    check("only_wh01_card_metadata_changed", all(card_by_order[key] == row for key, row in base_card_by_order.items() if key != "WH01"))
    check("wh01_pattern_counts_repaired", "WHOLE_LEXICON:1" in card_by_order["WH01"]["pattern_counts"] and "OPERATION_INSTRUCTION:36" in card_by_order["WH01"]["pattern_counts"] and "STATE_OR_GRADE:9" in card_by_order["WH01"]["pattern_counts"])

    check("workflow_unchanged", out["workflow"] == base["workflow"])
    check("summary_status_pass", summary["status"] == "PASS")
    check("summary_zero_local_wholes", summary["local_condition_whole_words"] == 0)
    check("summary_no_new_roots_or_pages", summary["new_semantic_roots"] == 0 and summary["new_pages"] == 0)
    check("summary_component_recipes_191", summary["component_recipes"] == 191)

    handbook = OUTPUTS["handbook"].read_text(encoding="utf-8")
    edition = OUTPUTS["edition"].read_text(encoding="utf-8")
    check("handbook_teaches_both_contractions", "OK+EE+OR" in handbook and "DA+IIN+AL" in handbook)
    check("edition_has_all_ten_pages", all(f"## {page}:" in edition for page in PAGES))

    before = {key: sha256(path) for key, path in OUTPUTS.items()}
    subprocess.run([sys.executable, str(HERE / "build_nine_hundred_sixth.py")], cwd=HERE.parents[2], check=True)
    after = {key: sha256(path) for key, path in OUTPUTS.items()}
    check("deterministic_rebuild_byte_identical", before == after)

    result = {
        "status": "PASS" if not failures else "FAIL",
        "decision": summary["decision"],
        "checks_passed": sum(checks.values()),
        "checks_total": len(checks),
        "failures": failures,
        "counts": expected_counts,
        "output_sha256": after,
        "checks": checks,
    }
    (HERE / f"{PFX}_VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({key: result[key] for key in ["status", "checks_passed", "checks_total", "failures"]}, ensure_ascii=False, indent=2))
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
