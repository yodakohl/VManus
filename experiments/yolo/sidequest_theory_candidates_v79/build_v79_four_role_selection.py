#!/usr/bin/env python3
"""Build and validate the selected V79 four-role release."""

from __future__ import annotations

import csv
import hashlib
import json
import shutil
from pathlib import Path


HERE = Path(__file__).resolve().parent


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def tsv_rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


selected_map = {
    "V79_R3_MACHINE_MANUAL.tsv": "V79_SELECTED_MACHINE_MANUAL.tsv",
    "V79_R3_FORWARD_BACKWARD_TRACES.tsv": "V79_SELECTED_FORWARD_BACKWARD_TRACES.tsv",
    "V79_R3_19_TRANSITION_AUDIT.tsv": "V79_SELECTED_19_LINE_TRANSITION_AUDIT.tsv",
    "V79_R2_REPAIR_DECISIONS.tsv": "V79_SELECTED_REPAIR_DECISIONS.tsv",
}
for source_name, target_name in selected_map.items():
    shutil.copyfile(HERE / source_name, HERE / target_name)

manual = tsv_rows(HERE / "V79_SELECTED_MACHINE_MANUAL.tsv")
traces = tsv_rows(HERE / "V79_SELECTED_FORWARD_BACKWARD_TRACES.tsv")
transitions = tsv_rows(HERE / "V79_SELECTED_19_LINE_TRANSITION_AUDIT.tsv")
decisions = tsv_rows(HERE / "V79_SELECTED_REPAIR_DECISIONS.tsv")

role_validations = {
    "R1": json.loads((HERE / "V79_R1_VALIDATION.json").read_text(encoding="utf-8")),
    "R2": json.loads((HERE / "V79_R2_VALIDATION.json").read_text(encoding="utf-8")),
    "R3": json.loads((HERE / "V79_R3_VALIDATION.json").read_text(encoding="utf-8")),
    "R4": json.loads((HERE / "V79_R4_VALIDATION.json").read_text(encoding="utf-8")),
}

checks = {
    "four_role_validations_pass": all(value["status"] == "PASS" for value in role_validations.values()),
    "selected_manual_16_rules": len(manual) == 16,
    "selected_trace_264_rows": len(traces) == 264,
    "selected_transition_19_rows": len(transitions) == 19,
    "read_once_confusion_exact": {
        key: sum(row["classification"] == key for row in transitions)
        for key in ("TP", "FP", "FN", "TN")
    } == {"TP": 1, "FP": 0, "FN": 0, "TN": 18},
    "only_read_once_pair_E180_E181": [
        (row["line_final_event"], row["line_initial_event"])
        for row in transitions
        if row["rule_prediction"] == "ANTICIPATORY_MARGIN_COPY"
    ] == [("E180", "E181")],
    "no_locus_specific_exception": all(row["locus_specific_exception"] == "NO" for row in transitions),
    "four_cross_line_owner_resets": sum(row["same_visible_owner"] == "NO" for row in transitions) == 4,
    "all_selected_traces_roundtrip": all(row["exact_roundtrip"] == "YES" for row in traces),
    "no_semantic_recovery_without_master": all(row["semantic_recovery_without_master"] == "NO" for row in traces),
    "h2_forward_24": sum(row["unit_id"] == "H2" and row["direction"] == "FORWARD" for row in traces) == 24,
    "h4_forward_18": sum(row["unit_id"] == "H4" and row["direction"] == "FORWARD" for row in traces) == 18,
    "b2_forward_62": sum(row["unit_id"] == "B2" and row["direction"] == "FORWARD" for row in traces) == 62,
    "astro_forward_28": sum(row["trace_family"] == "ASTRO_DIRECT_SLOT" and row["direction"] == "FORWARD" for row in traces) == 28,
    "seven_repair_decisions": len(decisions) == 7,
    "et_internal_formal": any(row["issue"] == "ET_QUESTION_MARK_VS_FORMAL_LINK" and row["winner"] == "FORMAL_LINK_AT_INTERNAL_READBACK" for row in decisions),
    "per_internal_formal": any(row["issue"] == "PER_QUESTION_MARK_VS_ENTRY_RESET" and row["winner"] == "FORMAL_RELATION_ENTRY_AT_INTERNAL_READBACK" for row in decisions),
    "no_new_portable_word": not any("NEW_PORTABLE_WORD" in "\t".join(row.values()) for row in decisions),
    "report_exists": (HERE / "V79_FOUR_ROLE_SELECTION.md").stat().st_size > 5000,
}

bound_sources = [
    HERE / "V79_R1_REPORT.md",
    HERE / "V79_R1_VALIDATION.json",
    HERE / "V79_R2_APPRENTICE_WORKFLOW_REPORT.md",
    HERE / "V79_R2_VALIDATION.json",
    HERE / "V79_R3_TECHNICAL_APPRENTICE_REPORT.md",
    HERE / "V79_R3_VALIDATION.json",
    HERE / "V79_R4_CHANCERY_APPRENTICE_AUDIT.md",
    HERE / "V79_R4_VALIDATION.json",
    HERE / "V79_R3_MACHINE_MANUAL.tsv",
    HERE / "V79_R3_FORWARD_BACKWARD_TRACES.tsv",
    HERE / "V79_R3_19_TRANSITION_AUDIT.tsv",
    HERE / "V79_R2_REPAIR_DECISIONS.tsv",
]
selected_outputs = [HERE / target for target in selected_map.values()] + [HERE / "V79_FOUR_ROLE_SELECTION.md"]

result = {
    "schema": "SIDEQUEST_V79_FOUR_ROLE_SELECTION_V1",
    "status": "PASS" if all(checks.values()) else "FAIL",
    "checks": checks,
    "passed": sum(checks.values()),
    "total": len(checks),
    "counts": {
        "manual_rules": len(manual),
        "trace_rows": len(traces),
        "transition_rows": len(transitions),
        "repair_decisions": len(decisions),
        "generic_read_once_matches": 1,
        "visible_owner_resets": 4,
        "new_words": 0,
    },
    "decisions": {
        "system": "EXEMPLAR_NOTATION_FORMALLY_LEARNABLE__CONCRETE_CONTENT_MASTER_DEPENDENT",
        "edge_copy": "LOCAL_ANTICIPATION_CARRY_OR_DITTOGRAPHY__READ_ONCE__ONE_POSITIVE_ONLY",
        "ET_operational": "FORMAL_LINK_OR_SLOT",
        "ET_optional_master_gloss": "ET?__UND_ODER_AUCH?",
        "PER_operational": "FORMAL_RELATION_OR_ENTRY_MARK_WITH_ENTRY_BIAS",
        "PER_optional_master_gloss": "PER?__DURCH_ODER_GEMAESS?",
    },
    "source_hashes": {path.name: sha256(path) for path in bound_sources},
    "selected_hashes": {path.name: sha256(path) for path in selected_outputs},
    "seals": {"f84": "SEALED_NOT_ACCESSED", "f84r": "SEALED_NOT_ACCESSED"},
    "next": "V80_CANONICAL_THIRD_EDITION__THEN_STOP",
}
(HERE / "V79_VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(f"{result['status']} {result['passed']}/{result['total']}")
raise SystemExit(0 if result["status"] == "PASS" else 1)
