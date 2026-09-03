#!/usr/bin/env python3
"""Validate and byte-replay GDT764."""

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
EXP = ROOT / "experiments/yolo/gdt764_bounded_value_field_dispatch"
ART = EXP / "artifacts"


def load_run():
    path = EXP / "src/run.py"
    spec = importlib.util.spec_from_file_location("gdt764_run_for_validation", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load GDT764 builder")
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

    x_occ = read_tsv("X_254_EXACT_OCCURRENCE_ATLAS.tsv")
    profiles = read_tsv("X_6_GLOBAL_ROLE_PROFILE.tsv")
    pairs = read_tsv("X_DAIIN_9_EXACT_BIGRAM_ATLAS.tsv")
    h1 = read_tsv("H1_X_DAIIN_5_BOUNDED_FIELD_ATLAS.tsv")
    axes = read_tsv("DAIIN_LOCAL_AXIS_DISPATCH_SUMMARY.tsv")
    grammar = read_tsv("FIELD_GRAMMAR.tsv")
    ol_raw = read_tsv("OL_RAW_EXACT_RECURRENCE_AUDIT.tsv")
    ol_association = read_tsv("OL_ORDER_ASSOCIATION_PROFILE.tsv")
    ol = read_tsv("OL_12_REPEAT_ORDER_ATLAS.tsv")
    ol_profile = read_tsv("OL_REPEAT_ORDER_PROFILE.tsv")
    hypotheses = read_tsv("OL_HYPOTHESIS_SCORECARD.tsv")
    history = read_tsv("HISTORICAL_REGISTER_TEMPLATE_MAP.tsv")
    revisions = read_tsv("BOUNDED_RENDERER_REVISION.tsv")
    result = json.loads((ART / "RESULT.json").read_text(encoding="utf-8"))

    check(len(x_occ) == 254, "X occurrence count")
    check(Counter(row["surface"] for row in x_occ) == Counter({"qoty": 77, "dal": 147, "qopchdy": 11, "ofchy": 3, "oteody": 15, "chofol": 1}), "X surface counts")
    check(len({row["x_occurrence_id"] for row in x_occ}) == 254, "X ids")
    check(len(profiles) == 6, "profile count")
    check(len(pairs) == 9, "pair count")
    check(Counter(row["x_surface"] for row in pairs) == Counter({"qoty": 3, "dal": 2, "qopchdy": 1, "ofchy": 1, "oteody": 1, "chofol": 1}), "pair surface counts")
    check(all(row["daiin_fixed_value"] == "III" for row in pairs), "daiin value")
    check(all(row["previous_gdt686_context_mode"] == "D_VALUE_OUTER_HEAD_OPEN" and row["previous_gdt686_axis"] == "OPEN" for row in pairs), "GDT686 predecessor state")
    check(len(h1) == 5 and all(row["paragraph_start_line"] == "1" and row["paragraph_end_line"] == "0" for row in h1), "H1 geometry")
    check(Counter(row["selected_local_dispatch"] for row in h1) == Counter({"RESULT_STAGE_III": 1, "QUALITY_GRADE_III": 1, "MATERIAL_MEASURE_VALUE_III": 1, "NOMINAL_VALUE_III": 1, "OPEN_VALUE_III": 1}), "H1 dispatch")
    check(all("nimm" not in row["portable_bounded_field_de"].lower() and "pulver" not in row["portable_bounded_field_de"].lower() for row in h1), "qopchdy target semantic hygiene")
    check(len(axes) == 5 and sum(int(row["h1_x_daiin_pairs"]) for row in axes) == 5, "axis summary")
    check(len(grammar) == 7 and [int(row["precedence"]) for row in grammar] == list(range(1, 8)), "grammar precedence")
    check(next(row for row in h1 if row["x_surface"] == "dal")["selected_local_dispatch"] == "MATERIAL_MEASURE_VALUE_III", "GDT711 dal quantity-head correction preserved")
    check(next(row for row in h1 if row["x_surface"] == "qopchdy")["selected_local_dispatch"] == "NOMINAL_VALUE_III", "qopchdy nominal field without invented axis")
    check([(int(row["raw_contiguous_occurrences"]), int(row["all_reader_exact_occurrences"])) for row in ol_raw] == [(5, 4), (5, 4), (3, 2), (2, 2)], "ol raw/exact gate")
    check([row["excluded_loci_and_flags"] for row in ol_raw] == ["f82r.16:100", "f116r.6:01", "f112v.6:10", "NONE"], "ol exact exclusions")
    check([(int(row["ol_in_pattern_slot"]), int(row["eligible_pattern_slots"]), int(row["ol_in_other_slots"]), int(row["eligible_other_slots"])) for row in ol_association] == [(4, 18, 1, 140), (4, 37, 8, 163), (2, 69, 10, 131), (2, 27, 10, 173)], "ol association profile")
    check(len(ol) == 12, "ol repeat count")
    check(Counter(row["selected_slot_function"] for row in ol) == Counter({"HEAD": 8, "CONTEXT_SECOND_FIELD": 2, "OBJECT_PATIENT": 1, "BILATERAL_AMBIGUOUS": 1}), "ol role dispatch")
    check(sum(row["gdt764_role_evolution"] == "A09_CONTEXT_TO_HEAD_WITH_LEFT_CONTEXT_RIVAL" for row in ol) == 1, "single ol evolution")
    check(all(row["literal_process_selected"] == "0" for row in ol), "no literal process promotion")
    check(len(ol_profile) == 4 and [(row["pattern_eva"], int(row["positions"])) for row in ol_profile] == [("ol s aiin", 4), ("sain ol", 4), ("saiin ol", 2), ("or aiin ol", 2)], "ol profile")
    check(len(hypotheses) == 5 and sum(row["selected"] == "1" for row in hypotheses) == 1, "ol hypotheses")
    check(len(history) == 5 and all(row["target_mapping_credit"] == "0" for row in history), "historical mapping boundary")
    check(len(revisions) == 17 and Counter(row["kind"] for row in revisions) == Counter({"OL_AMOUNT_ORDER": 12, "H1_BOUNDED_FIELD": 5}), "renderer revisions")
    check(result["schema"] == "GDT764_RESULT_V1" and result["status"] == run.STATUS, "result schema/status")
    check(result["h1_value_field_result"]["strongly_typed_axes"] == 1 and result["h1_value_field_result"]["provisionally_typed_axes"] == 1 and result["h1_value_field_result"]["open_axes"] == 3, "result H1 summary")
    check(result["h1_value_field_result"]["global_daiin_translation"] == "NOT_SELECTED", "no global daiin")
    check(result["provenance_gates"]["gdt711_dal_quantity_head"] == "UNSUPPORTED_QUANTITY_HEAD_REMOVAL__PRESERVED", "GDT711 provenance gate")
    check(result["ol_result"]["oil_identity"] == "UNSELECTED_C0_WHOLE_RIVAL", "oil boundary")
    check(result["ol_result"]["gdt763_to_gdt764_evolution"] == "A09_CONTEXT_TO_HEAD_WITH_LEFT_CONTEXT_RIVAL", "ol result evolution")
    check(result["claim_boundary"] == {"component_values": 0, "confirmed_lexemes": 0, "confirmed_plaintext_clauses": 0, "confirmed_substances": 0, "confirmed_units": 0, "f84_accessed": False, "f84r_accessed": False, "new_images": 0, "new_pages": 0}, "claim boundary")
    check(result["guard"]["inherited_token_query"] == {"selected": 4137, "skipped_forbidden": 98, "skipped_not_allowed": 1150}, "guard")

    for rows in (x_occ, profiles, pairs, h1, axes, grammar, ol_raw, ol_association, ol, ol_profile, hypotheses, history):
        for row in rows:
            if "component_export_credit" in row:
                check(row["component_export_credit"] == "0", "component export")
            page = row.get("page", "")
            check(not page.startswith("f84"), "sealed page")
    for row in pairs:
        check(row["confirmed_plaintext"] == "0", "pair plaintext")
    for row in h1:
        check(row["confirmed_plaintext"] == "0", "H1 plaintext")
    for row in ol:
        check(row["specific_oil_identity"] == "0" and row["confirmed_plaintext"] == "0", "ol identity/plaintext")

    with tempfile.TemporaryDirectory(prefix="gdt764-replay-") as temp_name:
        replay = Path(temp_name)
        run.build(replay)
        for name in run.OUTPUT_NAMES:
            check((ART / name).read_bytes() == (replay / name).read_bytes(), f"byte replay {name}")

    validation = {
        "schema": "GDT764_VALIDATION_V1", "status": "PASS", "checks": checks,
        "artifact_tables": 13, "byte_identical_outputs": len(run.OUTPUT_NAMES),
        "confirmed_lexemes": 0, "component_exports": 0,
        "sealed_f84": "FORBIDDEN_NOT_ACCESSED", "sealed_f84r": "FORBIDDEN_NOT_ACCESSED",
        "new_pages": 0, "relation_packet_status": "NOT_APPLICABLE_NO_NEW_SCORE_READY_EDGE_PACKET",
    }
    (ART / "VALIDATION.json").write_text(json.dumps(validation, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(validation, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
