#!/usr/bin/env python3
"""Validate counts, scope, source freeze, and semantic ceilings for V77 R1."""

from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = Path(__file__).resolve().parents[3]
SOURCE = HERE / "V77_R1_SOURCE_FIRST_CODEBOOK_INVENTORY.tsv"
TARGET = HERE / "V77_TARGET_FREEZE.tsv"
DECISIONS = HERE / "V77_R1_BOUNDED_CARD_DECISIONS.tsv"
AUDIT = HERE / "V77_R1_FULL_OCCURRENCE_AUDIT.tsv"
WITHDRAWALS = HERE / "V77_R1_WITHDRAWALS.tsv"
SUMMARY = HERE / "V77_R1_BUILD_SUMMARY.json"
V73 = ROOT / "experiments/yolo/sidequest_theory_candidates_v73/V73_SELECTED_100_EVENT_INTERLINEAR.tsv"
V74 = ROOT / "experiments/yolo/sidequest_theory_candidates_v74/V74_SELECTED_281_EVENT_INTERLINEAR.tsv"

SOURCE_SHA256 = "8f2c6afdcdfb2759a10d83c4a4404fabf3448522c8013f46e7418e06e258bfda"
TARGET_SHA256 = "2b5659f9d7cd213fc22842c38e38388061096b9407723628bb82bb0a51ce1dd7"
ALLOWED_PAGES = {"f10r", "f11r", "f55v", "f56r", "f81v", "f82r", "f83r"}
ALLOWED_DEFAULTS = {"EXEMPLAR_VALUE_UNKNOWN", "FORMAL_LABEL_NOT_WORD"}


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh, delimiter="\t"))


def main() -> None:
    checks: dict[str, object] = {}
    checks["source_inventory_hash_frozen"] = hashlib.sha256(SOURCE.read_bytes()).hexdigest() == SOURCE_SHA256
    checks["central_target_hash_frozen"] = hashlib.sha256(TARGET.read_bytes()).hexdigest() == TARGET_SHA256
    source = read(SOURCE)
    targets = read(TARGET)
    decisions = read(DECISIONS)
    audit = read(AUDIT)
    withdrawals = read(WITHDRAWALS)
    events = read(V73) + read(V74)

    required_source = {
        "source_row_id", "key_id", "date", "correspondence_or_key_heading",
        "archive_or_library_location", "codebook_type", "source_entry", "code_or_sign",
        "citation", "precise_locator", "stable_url", "source_sha256",
    }
    checks["source_rows_22"] = len(source) == 22
    checks["two_genuine_keys"] = len({r["key_id"] for r in source}) == 2
    checks["source_mandatory_fields_complete"] = all(all(r.get(k, "").strip() for k in required_source) for r in source)
    checks["source_dates_in_window"] = all(1370 <= int(r["date"]) <= 1450 for r in source)
    checks["source_codes_clear"] = all(r["code_transcription_status"] == "CLEAR_ROMAN_TYPE" for r in source)

    checks["decision_rows_24"] = len(decisions) == 24
    checks["decision_ids_unique"] = len({r["joint_tuple_id"] for r in decisions}) == 24
    checks["decisions_match_central_target_freeze"] = [r["joint_tuple_id"] for r in decisions] == [r["joint_tuple_id"] for r in targets]
    checks["fixed_control_rows_14"] = sum(r["selection_stratum"] == "FROZEN_14_CONTROL" for r in decisions) == 14
    checks["frequency_rows_10"] = sum(r["selection_stratum"] == "TOP10_RECURRENT_NONCONTROL" for r in decisions) == 10
    checks["no_admitted_gloss"] = all(r["proposed_minimal_gloss"] == "NONE_ADMITTED" for r in decisions)
    checks["only_required_fallbacks"] = {r["final_atomic_default"] for r in decisions} <= ALLOWED_DEFAULTS
    checks["four_formal_labels"] = sum(r["final_atomic_default"] == "FORMAL_LABEL_NOT_WORD" for r in decisions) == 4
    checks["twenty_unknown_exemplars"] = sum(r["final_atomic_default"] == "EXEMPLAR_VALUE_UNKNOWN" for r in decisions) == 20
    checks["no_postreveal_source_match"] = all(r["exact_source_match_row_id"] == "NONE" for r in decisions)

    checks["audit_rows_197"] = len(audit) == 197
    checks["audit_serial_complete"] = [int(r["audit_serial"]) for r in audit] == list(range(1, 198))
    checks["audit_pages_bounded"] = {r["page"] for r in audit} <= ALLOWED_PAGES
    checks["f84_f84r_absent"] = not ({r["page"] for r in audit} & {"f84", "f84r"})
    checks["all_audited_cards_decided"] = {r["joint_tuple_id"] for r in audit} == {r["joint_tuple_id"] for r in decisions}
    decision_n = {r["joint_tuple_id"]: int(r["occurrences_in_381_event_panel"]) for r in decisions}
    audit_n = Counter(r["joint_tuple_id"] for r in audit)
    checks["occurrence_counts_match_decisions"] = decision_n == dict(audit_n)
    event_keys = {(r["event_serial"], r["joint_tuple_id"]) for r in events}
    checks["audit_rows_are_selected_source_events"] = all((r["event_serial"], r["joint_tuple_id"]) in event_keys for r in audit)
    checks["audit_defaults_match_decisions"] = all(
        r["portable_atomic_reading_after_v77"] == next(d["final_atomic_default"] for d in decisions if d["joint_tuple_id"] == r["joint_tuple_id"])
        for r in audit
    )

    checks["withdrawal_rows_14"] = len(withdrawals) == 14
    checks["withdrawal_cards_match_controls"] = {
        r["joint_tuple_id"] for r in withdrawals
    } == {
        r["joint_tuple_id"] for r in decisions if r["selection_stratum"] == "FROZEN_14_CONTROL"
    }
    checks["withdrawals_have_replacement"] = all(r["replacement_atomic_default"] in ALLOWED_DEFAULTS for r in withdrawals)

    summary = json.loads(SUMMARY.read_text(encoding="utf-8"))
    checks["summary_counts_match"] = (
        summary["source_inventory_rows"] == len(source)
        and summary["bounded_cards"] == len(decisions)
        and summary["audited_occurrences"] == len(audit)
        and summary["admitted_word_rows"] == 0
    )
    checks["exact_input_event_total"] = len(events) == 381

    failed = sorted(k for k, value in checks.items() if value is not True)
    result = {
        "status": "PASS" if not failed else "FAIL",
        "checks": checks,
        "failed_checks": failed,
        "counts": {
            "source_rows": len(source),
            "decision_rows": len(decisions),
            "audited_occurrences": len(audit),
            "withdrawal_rows": len(withdrawals),
            "input_events": len(events),
        },
        "scope": {
            "pages": sorted({r["page"] for r in audit}),
            "f84": "SEALED_NOT_ACCESSED",
            "f84r": "SEALED_NOT_ACCESSED",
        },
    }
    (HERE / "V77_R1_VALIDATION.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    if failed:
        raise SystemExit("validation failed: " + ", ".join(failed))


if __name__ == "__main__":
    main()
