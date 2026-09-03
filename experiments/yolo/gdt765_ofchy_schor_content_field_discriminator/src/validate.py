#!/usr/bin/env python3
"""Validate and byte-replay GDT765."""

from __future__ import annotations

import csv
import importlib.util
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
EXP = ROOT / "experiments/yolo/gdt765_ofchy_schor_content_field_discriminator"
ART = EXP / "artifacts"


def load_run():
    path = EXP / "src/run.py"
    spec = importlib.util.spec_from_file_location("gdt765_run_for_validation", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load GDT765 builder")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


run = load_run()


def read_tsv(name: str) -> list[dict[str, str]]:
    with (ART / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> int:
    checks = 0

    def check(condition: bool, message: str) -> None:
        nonlocal checks
        checks += 1
        if not condition:
            raise AssertionError(message)

    targets = read_tsv("TARGET_6_EXACT_OCCURRENCE_ATLAS.tsv")
    audit = read_tsv("TARGET_RAW_EXACT_AUDIT.tsv")
    ofch = read_tsv("OFCH_25_EXACT_FAMILY_ATLAS.tsv")
    fchy = read_tsv("FCHY_13_EXACT_FAMILY_ATLAS.tsv")
    profiles = read_tsv("FORMAL_FAMILY_21_WHOLE_PROFILE.tsv")
    chor = read_tsv("CHOR_VALUE_67_PAIR_ATLAS.tsv")
    triples = read_tsv("H_HEAD_X_DAIIN_12_ATLAS.tsv")
    grid = read_tsv("F22R_4_VALUE_GRID.tsv")
    hypotheses = read_tsv("TARGET_HYPOTHESIS_SCORECARD.tsv")
    dictionary = read_tsv("TARGET_WORKING_DICTIONARY_REVISION.tsv")
    renderers = read_tsv("TARGET_6_CONCRETE_RENDERER.tsv")
    reader = read_tsv("F22R4_9_TOKEN_WORKING_READER.tsv")
    cfhy = read_tsv("CFHY_6_EXACT_TRANSITION_AUDIT.tsv")
    history = read_tsv("HISTORICAL_CONTENT_FIELD_COMPARATORS.tsv")
    result = json.loads((ART / "RESULT.json").read_text(encoding="utf-8"))

    check(len(targets) == 6, "target count")
    check(Counter(row["surface"] for row in targets) == Counter({"ofchy": 3, "schor": 3}), "target surfaces")
    check(len({row["target_occurrence_id"] for row in targets}) == 6, "target ids")
    check(all(row["section"] == "H" for row in targets), "targets remain Herbal")
    check(sum(row["paragraph_start_line"] == "1" for row in targets if row["surface"] == "ofchy") == 2, "ofchy paragraph-start geometry")
    check(all(row["line_position"] == "MIDDLE" for row in targets if row["surface"] == "ofchy"), "ofchy medial geometry")
    check(Counter(row["line_position"] for row in targets if row["surface"] == "schor") == Counter({"FIRST": 2, "MIDDLE": 1}), "schor item geometry")
    check(Counter(row["render_channel"] for row in targets) == Counter({"VALUE_FIELD": 2, "FORM_PART_FIELD": 1, "HOT_FRACTION_AMOUNT_FIELD": 1, "ITEM_HEAD": 1, "HOT_DRY_GRADE_FIELD": 1}), "render channels")
    check(all(row["confirmed_plaintext"] == "0" and row["component_export_credit"] == "0" for row in targets), "target claim ceiling")

    check([(row["surface"], int(row["raw_occurrences"]), int(row["reader_exact_occurrences"])) for row in audit] == [("ofchy", 4, 3), ("schor", 3, 3)], "raw/exact target audit")
    check(next(row for row in audit if row["surface"] == "ofchy")["excluded_loci_and_ordinals"] == "f39v.5:14", "nonexact ofchy exclusion")
    check(len(ofch) == 25 and len({row["surface"] for row in ofch}) == 13, "ofch family")
    check(len(fchy) == 13 and len({row["surface"] for row in fchy}) == 8, "fchy family")
    check(len(profiles) == 21, "family profiles")
    check(all(row["family_analogy_only"] == "1" and row["component_export_credit"] == "0" for row in ofch + fchy), "family analogy boundary")

    expected_chor = Counter({"or": 38, "chor": 12, "cthor": 5, "shor": 4, "sor": 4, "schor": 1, "dshor": 1, "qotor": 1, "tchor": 1})
    check(len(chor) == 67 and Counter(row["head_surface"] for row in chor) == expected_chor, "chor value pairs")
    check(sum(row["head_surface"] == "schor" and row["value_surface"] == "daiin" for row in chor) == 1, "single schor-daiin")
    check(len(triples) == 12 and Counter(row["head_id"] for row in triples) == Counter({"H1": 5, "H2": 5, "H4": 2}), "H-X-daiin triples")
    check(sum(row["locus"] == "f22r.4" for row in triples) == 2, "two f22r.4 H triples")
    check(len(grid) == 4 and [row["field_head_surface"] for row in grid] == ["ofchy", "schor", "ol", "dar"], "f22 value grid")
    check(sum(row["gdt765_target"] == "1" for row in grid) == 2, "f22 target cells")

    check(len(hypotheses) == 8 and sum(row["selected"] == "1" for row in hypotheses) == 2, "hypothesis selection")
    check(next(row for row in hypotheses if row["hypothesis_id"] == "OF_CONTENT_NAME")["working_score"] == "11", "ofchy role score")
    check(next(row for row in hypotheses if row["hypothesis_id"] == "SC_PART_ITEM")["working_score"] == "12", "schor role score")
    check(len(dictionary) == 2, "dictionary rows")
    check(next(row for row in dictionary if row["surface"] == "ofchy")["bold_concrete_default_de"] == "Blütenmasse", "ofchy concrete default")
    check(next(row for row in dictionary if row["surface"] == "schor")["bold_concrete_default_de"] == "Blütenstand", "schor concrete default")
    check(all(row["specific_identity_is_replaceable"] == "1" and row["confirmed_lexeme"] == "0" for row in dictionary), "replaceable identities")

    check(len(renderers) == 6, "renderer count")
    check(all(row["scope"] == "THIS_EXACT_OBSERVED_SPAN" and row["confirmed_plaintext"] == "0" for row in renderers), "renderer scope")
    check(len(reader) == 9 and [int(row["ordinal"]) for row in reader] == list(range(1, 10)), "f22 reader coverage")
    check(all(row["local_default_de"] and row["global_export"] == "0" for row in reader), "f22 no empty defaults and no export")
    check(next(row for row in reader if row["surface"] == "cfhy")["local_default_de"] == "Feldwechsel; Fortsetzung", "cfhy structural correction")
    check("Blütenmasse" in reader[0]["bold_line_renderer_de"] and "Blütenstand" in reader[0]["bold_line_renderer_de"], "concrete f22 line")
    check(len({row["bold_line_renderer_de"] for row in reader}) == 1, "single f22 line renderer")
    check(len(cfhy) == 6 and Counter(row["line_position"] for row in cfhy) == Counter({"MIDDLE": 5, "LAST": 1}), "cfhy exact geometry")
    check(all(row["right_is_daiin"] == "0" and row["paragraph_end_line"] == "0" for row in cfhy), "cfhy transition geometry")
    check(all(row["selected_local_role"] == "FIELD_TRANSITION_OR_CONTINUATION" and row["global_export"] == "0" for row in cfhy), "cfhy structural scope")
    check(len(history) == 7 and all(row["target_spelling_credit"] == "0" and row["target_identity_credit"] == "0" for row in history), "historical architecture only")

    check(result["schema"] == "GDT765_RESULT_V1" and result["status"] == run.STATUS, "result schema/status")
    check(result["scope"] == {"target_exact_occurrences": 6, "target_pages": 5, "ofch_prefix_exact_occurrences": 25, "fchy_suffix_exact_occurrences": 13, "chor_value_pairs": 67, "h_head_x_daiin_triples": 12, "f22r_value_grid_fields": 4, "cfhy_transition_occurrences": 6, "historical_comparators": 7}, "result scope")
    check(result["ofchy_result"]["bold_concrete_default_de"] == "Blütenmasse", "result ofchy")
    check(result["schor_result"]["bold_concrete_default_de"] == "Blütenstand", "result schor")
    check(result["schor_result"]["failed_generic_body_transfer_preserved"] is True, "failed transfer preserved")
    check(result["claim_boundary"] == {"component_values": 0, "confirmed_lexemes": 0, "confirmed_plaintext_clauses": 0, "confirmed_substances": 0, "confirmed_units": 0, "f84_accessed": False, "f84r_accessed": False, "new_images": 0, "new_pages": 0}, "result claim boundary")
    check(result["guard"]["inherited_token_query"] == {"selected": 4137, "skipped_forbidden": 98, "skipped_not_allowed": 1150}, "guard")

    for rows in (targets, ofch, fchy, chor, triples, grid, renderers, reader, cfhy):
        for row in rows:
            check(not row.get("page", "").startswith("f84"), "sealed page")
            if "component_export_credit" in row:
                check(row["component_export_credit"] == "0", "component export")

    with tempfile.TemporaryDirectory(prefix="gdt765-replay-") as temp_name:
        replay = Path(temp_name)
        run.build(replay)
        for name in run.OUTPUT_NAMES:
            check((ART / name).read_bytes() == (replay / name).read_bytes(), f"byte replay {name}")

    validation = {
        "schema": "GDT765_VALIDATION_V1",
        "status": "PASS",
        "checks": checks,
        "artifact_tables": 14,
        "byte_identical_outputs": len(run.OUTPUT_NAMES),
        "confirmed_lexemes": 0,
        "component_exports": 0,
        "sealed_f84": "FORBIDDEN_NOT_ACCESSED",
        "sealed_f84r": "FORBIDDEN_NOT_ACCESSED",
        "new_pages": 0,
        "relation_packet_status": "NOT_APPLICABLE_NO_NEW_SCORE_READY_EDGE_PACKET",
    }
    (ART / "VALIDATION.json").write_text(json.dumps(validation, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(validation, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
