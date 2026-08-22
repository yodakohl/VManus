#!/usr/bin/env python3
"""Validate the V79 R1 manual, three traces, and 19-edge carry audit."""

from __future__ import annotations

import csv
import json
from collections import Counter
from pathlib import Path


HERE = Path(__file__).resolve().parent
MANUAL = HERE / "V79_R1_COMPACT_MANUAL.tsv"
TRACES = HERE / "V79_R1_REQUIRED_TRACES.tsv"
CARRY = HERE / "V79_R1_CARRY_AUDIT.tsv"
ERRORS = HERE / "V79_R1_ERROR_CONTRADICTIONS.tsv"
TRACE_MD = HERE / "V79_R1_REQUIRED_TRACES.md"
SUMMARY = HERE / "V79_R1_BUILD_SUMMARY.json"

ET_CARD = "dcda95c81a5460feb191"
PER_CARD = "b5fcea1eaed06b2f2291"


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh, delimiter="\t"))


def main() -> None:
    manual = read(MANUAL)
    traces = read(TRACES)
    carry = read(CARRY)
    errors = read(ERRORS)
    summary = json.loads(SUMMARY.read_text(encoding="utf-8"))
    checks: dict[str, object] = {}

    checks["manual_steps_16"] = len(manual) == 16 and [int(r["step"]) for r in manual] == list(range(1, 17))
    checks["manual_has_forward_backward_and_checks"] = {r["direction"] for r in manual} >= {"FORWARD", "BACKWARD", "BOTH", "CHECK"}
    carry_rule = next(r for r in manual if r["scope"] == "CARRY")
    checks["carry_rule_is_locus_free"] = "E180" not in carry_rule["instruction"] and "f82r" not in carry_rule["instruction"]
    checks["manual_preserves_semantic_ceiling"] = any(r["scope"] == "SEMANTIC_CEILING" for r in manual)

    trace_counts = Counter(r["trace_id"] for r in traces)
    checks["trace_rows_114"] = len(traces) == 114
    checks["required_trace_counts"] = trace_counts == {
        "TRACE_HERBAL_H2": 24,
        "TRACE_BIO_B2": 62,
        "TRACE_ASTRO_F69_LEFT_28": 28,
    }
    h2 = [r for r in traces if r["trace_id"] == "TRACE_HERBAL_H2"]
    b2 = [r for r in traces if r["trace_id"] == "TRACE_BIO_B2"]
    astro = [r for r in traces if r["trace_id"] == "TRACE_ASTRO_F69_LEFT_28"]
    checks["h2_complete_event_range"] = [r["source_unit"] for r in h2] == [f"E{i:03d}" for i in range(15, 39)]
    checks["b2_complete_event_range"] = [r["source_unit"] for r in b2] == [f"E{i:03d}" for i in range(167, 229)]
    checks["b2_owner_resets_exact"] = {
        r["source_unit"] for r in b2 if r["boundary_before"].startswith("BREAK_VISIBLE_GAP")
    } == {"E189", "E198", "E203", "E212"}
    e180 = next(r for r in b2 if r["source_unit"] == "E180")
    e181 = next(r for r in b2 if r["source_unit"] == "E181")
    checks["e180_e181_exact_same_card"] = e180["exact_identity_order"] == e181["exact_identity_order"] == PER_CARD
    checks["e180_visible_but_source_silent"] = "KEEP_VISIBLE_BUT_SOURCE_SILENT" in e180["forward_copy_instruction"] and "DO_NOT_SPEAK" in e180["backward_literal_recovery"]
    checks["e181_main_per_token"] = e181["backward_literal_recovery"].startswith("PER?")
    checks["astro_slots_l01_l28"] = [r["field_or_slot"] for r in astro] == [f"L{i:02d}" for i in range(1, 29)]
    checks["astro_all_left_namespace"] = {r["statement_or_namespace"] for r in astro} == {"A3_LEFT_WHEEL_ONLY"}
    checks["astro_group_count_33"] = sum(len(r["exact_identity_order"].split("|")) for r in astro) == 33
    checks["all_trace_exact_recovery_pass"] = all(r["exact_identity_recovery"] == "PASS" for r in traces)
    checks["all_trace_boundary_recovery_pass"] = all(r["boundary_recovery"] == "PASS" for r in traces)
    checks["all_trace_with_exemplar_present"] = all(r["semantic_with_exemplar"] for r in traces)
    checks["without_exemplar_never_claims_concrete_meaning"] = all(
        r["semantic_without_exemplar"] in {
            "NO_CONCRETE_SEMANTIC_RECOVERY",
            "ET_CATEGORY_ONLY__FORMAL_LINK_RIVAL_TIED",
            "PER_CATEGORY_ONLY__COMPLEMENT_AND_CHOICE_UNKNOWN",
            "FORMAL_NONWORD_ONLY",
            "LEFT_WHEEL_LOCAL_SLOT_ONLY__NAME_RANK_START_DIRECTION_AND_MEANING_UNKNOWN",
        }
        for r in traces
    )

    checks["carry_transitions_19"] = len(carry) == 19 and [int(r["transition_index"]) for r in carry] == list(range(1, 20))
    confusion = Counter(r["classification"] for r in carry)
    checks["carry_tp1_fp0_fn0_tn18"] = confusion == {"TP": 1, "TN": 18}
    positive = [r for r in carry if r["carry_rule_fires"] == "YES"]
    checks["only_visible_positive_e180_e181"] = len(positive) == 1 and positive[0]["left_event"] == "E180" and positive[0]["right_event"] == "E181"
    checks["positive_conditions_complete"] = all(
        positive[0][field] == "YES"
        for field in ("same_exact_card", "same_owner_without_reset", "same_statement", "no_close")
    )
    checks["owner_reset_blocks_four_transitions"] = sum(r["same_owner_without_reset"] == "NO" for r in carry) == 4
    checks["no_false_positive_or_negative"] = not any(r["classification"] in {"FP", "FN"} for r in carry)

    checks["error_rows_10"] = len(errors) == 10
    checks["error_table_covers_required_scopes"] = {r["scope"] for r in errors} >= {"CARRY", "PER", "ET", "FORMAL", "H2", "B2_OWNER", "ASTRO", "SEMANTICS"}
    trace_md = TRACE_MD.read_text(encoding="utf-8")
    checks["trace_md_has_all_three"] = all(trace_id in trace_md for trace_id in trace_counts)
    checks["no_sealed_page_in_outputs"] = (
        all(r["page"] not in {"f84", "f84r"} and not r["locus"].startswith("f84") for r in traces)
        and all(r["page"] not in {"f84", "f84r"} and not r["left_locus"].startswith("f84") and not r["right_locus"].startswith("f84") for r in carry)
    )
    checks["summary_matches"] = (
        summary["manual_steps"] == len(manual)
        and summary["trace_rows"] == len(traces)
        and summary["carry_transitions"] == len(carry)
        and summary["carry_confusion"] == {"TP": 1, "FP": 0, "FN": 0, "TN": 18}
        and summary["sealed_pages_accessed"] == []
    )
    checks["et_retained_only_provisionally"] = summary["et_decision"] == "RETAIN_PROVISIONAL__FORMAL_LINK_RIVAL_TIED"
    checks["per_retained_only_on_probation"] = summary["per_decision"].startswith("RETAIN_ON_PROBATION__")

    failed = sorted(k for k, value in checks.items() if value is not True)
    validation = {
        "status": "PASS" if not failed else "FAIL",
        "checks": checks,
        "failed_checks": failed,
        "counts": {
            "manual_steps": len(manual),
            "trace_rows": len(traces),
            "h2_events": len(h2),
            "b2_events": len(b2),
            "astro_slots": len(astro),
            "astro_groups": sum(len(r["exact_identity_order"].split("|")) for r in astro),
            "carry_transitions": len(carry),
            "carry_confusion": {k: confusion.get(k, 0) for k in ("TP", "FP", "FN", "TN")},
        },
        "decisions": {
            "ET": summary["et_decision"],
            "PER": summary["per_decision"],
        },
        "scope": {
            "pages_in_traces": sorted({r["page"] for r in traces}),
            "f84": "SEALED_NOT_ACCESSED",
            "f84r": "SEALED_NOT_ACCESSED",
        },
        "ceiling": "APPRENTICE_COPY_AND_READBACK_TEST_NOT_DECIPHERMENT",
    }
    (HERE / "V79_R1_VALIDATION.json").write_text(json.dumps(validation, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    if failed:
        raise SystemExit("validation failed: " + ", ".join(failed))


if __name__ == "__main__":
    main()
