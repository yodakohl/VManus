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
ROOT = HERE.parent
PREFIX = "NINE_HUNDRED_FIFTH"
CODEBOOK = ROOT / "sidequest_semantic_mixed_root_codebook_eight_hundred_ninety_ninth"
SLOTS = ROOT / "sidequest_semantic_scribe_slot_grammar_nine_hundredth"
RENDERER = ROOT / "sidequest_semantic_allograph_renderer_nine_hundred_first"
CURRENT = ROOT / "sidequest_semantic_complete_functional_renderer_nine_hundred_fourth"

FILES = {
    "symbols": HERE / f"{PREFIX}_48_COMPLETE_SYMBOL_DICTIONARY.tsv",
    "patterns": HERE / f"{PREFIX}_8_CARD_PATTERNS.tsv",
    "rules": HERE / f"{PREFIX}_15_RENDERER_RULES.tsv",
    "micro": HERE / f"{PREFIX}_38_ALLOGRAPH_MICROLEXICON.tsv",
    "dictionary": HERE / f"{PREFIX}_231_COMPLETE_CARD_DICTIONARY.tsv",
    "marks": HERE / f"{PREFIX}_437_COMPLETE_INTERLINEAR.tsv",
    "units": HERE / f"{PREFIX}_118_COMPLETE_UNIT_EDITION.tsv",
    "page_units": HERE / f"{PREFIX}_115_DEDUPED_PAGE_UNITS.tsv",
    "cards": HERE / f"{PREFIX}_6_COMPLETE_JOB_CARDS.tsv",
    "workflow": HERE / f"{PREFIX}_12_STEP_WORKFLOW.tsv",
    "handbook": HERE / f"{PREFIX}_COMPLETE_SCRIBE_HANDBOOK.md",
    "edition": HERE / f"{PREFIX}_TEN_PAGE_WORKING_EDITION.md",
    "report": HERE / f"{PREFIX}_REPORT.md",
    "summary": HERE / f"{PREFIX}_BUILD_SUMMARY.json",
}

SOURCE = {
    "vocabulary": CODEBOOK / "EIGHT_HUNDRED_NINETY_NINTH_231_MIXED_CODEBOOK_VOCABULARY.tsv",
    "symbols": SLOTS / "NINE_HUNDREDTH_48_GRAMMAR_SYMBOLS.tsv",
    "patterns": SLOTS / "NINE_HUNDREDTH_8_CARD_PATTERNS.tsv",
    "parses": SLOTS / "NINE_HUNDREDTH_231_IDENTITY_SLOT_PARSES.tsv",
    "cues": RENDERER / "NINE_HUNDRED_FIRST_48_SYMBOL_ALLOGRAPHS.tsv",
    "rules": RENDERER / "NINE_HUNDRED_FIRST_15_RENDERER_RULES.tsv",
    "micro": CURRENT / "NINE_HUNDRED_FOURTH_38_COMPLETE_ALLOGRAPH_MICROLEXICON.tsv",
    "marks": CURRENT / "NINE_HUNDRED_FOURTH_437_FUNCTIONALLY_RENDERED_MARKS.tsv",
    "units": CURRENT / "NINE_HUNDRED_FOURTH_118_FUNCTIONALLY_RENDERED_UNITS.tsv",
    "cards": CURRENT / "NINE_HUNDRED_FOURTH_6_FUNCTIONALLY_RENDERED_JOB_CARDS.tsv",
}

PAGES = {"f10r", "f11r", "f55v", "f56r", "f81v", "f82r", "f83r", "f67r2", "f68r1", "f69v"}
EXPECTED_ACTIONS = {
    "READ_SHARED_CORE": 251,
    "READ_ROOT_COMPOSITION": 106,
    "READ_LOCAL_CONDITION_WORD": 73,
    "READ_FUSED_WHOLE_WORD": 6,
    "READ_LEARNED_WHOLE_ROOT": 1,
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
    checks: dict[str, bool] = {}
    errors: list[str] = []

    def check(name: str, condition: bool) -> None:
        checks[name] = bool(condition)
        if not condition:
            errors.append(name)

    output = {key: read(path) for key, path in FILES.items() if path.suffix == ".tsv"}
    source = {key: read(path) for key, path in SOURCE.items()}
    summary = json.loads(FILES["summary"].read_text(encoding="utf-8"))

    expected_counts = {
        "symbols": 48,
        "patterns": 8,
        "rules": 15,
        "micro": 38,
        "dictionary": 231,
        "marks": 437,
        "units": 118,
        "page_units": 115,
        "cards": 6,
        "workflow": 12,
    }
    for key, expected in expected_counts.items():
        check(f"count_{key}_{expected}", len(output[key]) == expected)

    check("patterns_byte_rows_match_source", output["patterns"] == source["patterns"])
    check("renderer_rules_byte_rows_match_source", output["rules"] == source["rules"])
    check("microlexicon_byte_rows_match_source", output["micro"] == source["micro"])
    check("unit_rows_match_source", output["units"] == source["units"])
    check("job_card_rows_match_source", output["cards"] == source["cards"])

    symbol_ids = [row["symbol"] for row in output["symbols"]]
    check("symbol_ids_unique", len(symbol_ids) == len(set(symbol_ids)))
    check("symbol_set_matches_source", set(symbol_ids) == {row["symbol"] for row in source["symbols"]})
    cue_by_symbol = {row["symbol"]: row for row in source["cues"]}
    check(
        "symbol_cues_match_source",
        all(
            row["canonical_surface_cue"] == cue_by_symbol[row["symbol"]]["canonical_surface_cue"]
            and row["renderer_instruction"] == cue_by_symbol[row["symbol"]]["renderer_instruction"]
            for row in output["symbols"]
        ),
    )

    dictionary_ids = [row["identity"] for row in output["dictionary"]]
    source_ids = {row["identity"] for row in source["vocabulary"]}
    check("dictionary_ids_unique", len(dictionary_ids) == len(set(dictionary_ids)))
    check("dictionary_identity_set_exact", set(dictionary_ids) == source_ids)
    check("dictionary_marks_sum_437", sum(int(row["marks"]) for row in output["dictionary"]) == 437)
    check("dictionary_no_empty_value", all(row["dictionary_value_de"].strip() for row in output["dictionary"]))
    check("dictionary_no_empty_root_reading", all(row["atomic_root_reading_de"].strip() for row in output["dictionary"]))

    source_marks = source["marks"]
    out_marks = output["marks"]
    source_mark_by_id = {row["order_mark_id"]: row for row in source_marks}
    out_mark_ids = [row["order_mark_id"] for row in out_marks]
    check("mark_ids_unique", len(out_mark_ids) == len(set(out_mark_ids)))
    check("mark_id_set_exact", set(out_mark_ids) == set(source_mark_by_id))
    joined_fields = {
        "order_id": "order_id",
        "page": "page",
        "unit": "unit",
        "surface": "surface",
        "identity": "identity",
        "component_recipe": "component_recipe",
        "slot_signature": "slot_signature",
        "atomic_root_reading_de": "root_reading_de",
        "dictionary_value_de": "concrete_default_de",
        "functional_allograph": "renderer_microfunction",
        "microfunction_trigger_de": "microfunction_trigger_de",
        "owner_or_handle_de": "owner_or_handle_de",
        "renderer_skeleton": "renderer_skeleton",
        "predicted_surface": "predicted_surface",
        "reading_action": "apprentice_action",
    }
    check(
        "interlinear_fields_match_source",
        all(
            all(row[out_field] == source_mark_by_id[row["order_mark_id"]][source_field] for out_field, source_field in joined_fields.items())
            for row in out_marks
        ),
    )
    check("all_surfaces_regenerated_exactly", all(row["surface"] == row["predicted_surface"] for row in out_marks))
    check("mark_action_counts_exact", Counter(row["reading_action"] for row in out_marks) == Counter(EXPECTED_ACTIONS))
    check("mark_pages_exact", {row["page"] for row in out_marks} == PAGES)

    by_identity: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in out_marks:
        by_identity[row["identity"]].append(row)
    dictionary_by_id = {row["identity"]: row for row in output["dictionary"]}
    check(
        "dictionary_value_invariant_with_marks",
        all({mark["dictionary_value_de"] for mark in local} == {dictionary_by_id[identity]["dictionary_value_de"]} for identity, local in by_identity.items()),
    )
    check(
        "dictionary_action_invariant_with_marks",
        all({mark["reading_action"] for mark in local} == {dictionary_by_id[identity]["apprentice_action"]} for identity, local in by_identity.items()),
    )

    source_units = source["units"]
    page_unit_groups: dict[tuple[str, str], list[dict[str, str]]] = defaultdict(list)
    for row in source_units:
        page_unit_groups[(row["page"], row["unit"])].append(row)
    check("source_unique_page_units_115", len(page_unit_groups) == 115)
    check("source_duplicate_surplus_3", sum(len(rows) - 1 for rows in page_unit_groups.values()) == 3)
    check("source_duplicate_groups_3", sum(len(rows) > 1 for rows in page_unit_groups.values()) == 3)
    out_page_unit_keys = [(row["page"], row["unit"]) for row in output["page_units"]]
    check("deduped_page_unit_keys_unique", len(out_page_unit_keys) == len(set(out_page_unit_keys)))
    check("deduped_page_unit_key_set_exact", set(out_page_unit_keys) == set(page_unit_groups))
    check("deduped_page_unit_copy_sum_118", sum(int(row["source_unit_copies"]) for row in output["page_units"]) == 118)
    check("deduped_page_set_exact", {row["page"] for row in output["page_units"]} == PAGES)
    check("every_page_has_units", all(any(row["page"] == page for row in output["page_units"]) for page in PAGES))
    stable_fields = {
        "section": "section",
        "surface_sequence": "fifth_hand_surface_sequence",
        "atomic_root_sequence_de": "root_reading_sequence_de",
        "dictionary_literal_de": "literal_sequence_de",
        "fluent_workshop_reading_de": "front_instruction_de",
        "predicted_surface_sequence": "predicted_surface_sequence",
    }
    check(
        "deduped_unit_content_exact",
        all(
            all(
                len({source_row[source_field] for source_row in page_unit_groups[(row["page"], row["unit"])]}) == 1
                and row[out_field] == page_unit_groups[(row["page"], row["unit"])][0][source_field]
                for out_field, source_field in stable_fields.items()
            )
            for row in output["page_units"]
        ),
    )
    f11 = next(row for row in output["page_units"] if row["page"] == "f11r" and row["unit"] == "H3-S001")
    check("f11_shared_owner_traces_preserved", "WH02:Bildprodukt B.X4" in f11["owner_or_handle_de"] and "WH05:Bildprodukt B.X1" in f11["owner_or_handle_de"])

    workflow_steps = [int(row["step"]) for row in output["workflow"]]
    check("workflow_steps_exact_1_to_12", workflow_steps == list(range(1, 13)))
    check("workflow_stage_unique", len({row["stage"] for row in output["workflow"]}) == 12)

    check("summary_status_pass", summary["status"] == "PASS")
    check("summary_counts_exact", all(summary[key] == value for key, value in {
        "pages": 10,
        "symbols": 48,
        "card_patterns": 8,
        "renderer_rules": 15,
        "allograph_entries": 38,
        "dictionary_identities": 231,
        "marks": 437,
        "units": 118,
        "deduped_page_units": 115,
        "job_cards": 6,
        "workflow_steps": 12,
        "surface_prediction_mismatches": 0,
        "new_pages": 0,
    }.items()))
    check("summary_action_counts_exact", summary["mark_actions"] == EXPECTED_ACTIONS)

    check("handbook_names_current_scope", "36 Bedeutungswurzeln" in FILES["handbook"].read_text(encoding="utf-8"))
    edition_text = FILES["edition"].read_text(encoding="utf-8")
    check("edition_discloses_selection_scope", "Sechs-Auftrags-Auswahl" in edition_text)
    check("edition_has_all_page_headings", all(f"## {page}:" in edition_text for page in PAGES))

    data_page_values = {row.get("page", "") for table in output.values() for row in table if "page" in row}
    check("only_allowed_page_values", data_page_values <= PAGES)
    check("sealed_page_values_absent", not ({"f84", "f84r"} & data_page_values))

    # A fresh rebuild must leave every generated artifact byte-identical.
    before = {key: sha256(path) for key, path in FILES.items()}
    subprocess.run([sys.executable, str(HERE / "build_nine_hundred_fifth.py")], check=True, cwd=HERE.parent.parent.parent)
    after = {key: sha256(path) for key, path in FILES.items()}
    check("deterministic_rebuild_byte_identical", before == after)

    result = {
        "status": "PASS" if not errors else "FAIL",
        "decision": summary["decision"],
        "checks_passed": sum(checks.values()),
        "checks_total": len(checks),
        "errors": errors,
        "counts": expected_counts,
        "output_sha256": after,
        "checks": checks,
    }
    (HERE / f"{PREFIX}_VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({key: result[key] for key in ["status", "checks_passed", "checks_total", "errors"]}, ensure_ascii=False, indent=2))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
