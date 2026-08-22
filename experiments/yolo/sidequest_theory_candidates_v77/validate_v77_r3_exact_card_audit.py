#!/usr/bin/env python3
"""Validate the frozen-source, bounded-target V77 R3 audit."""

from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter
from pathlib import Path


HERE = Path(__file__).resolve().parent
V69 = HERE.parent / "sidequest_theory_candidates_v69"
OUT = HERE / "V77_R3_VALIDATION.json"
SOURCE_HASH = "375aee41178e7c333a6bf43b479d5fd400e62524be0d919c26160892de2881fa"
TARGET_HASH = "2b5659f9d7cd213fc22842c38e38388061096b9407723628bb82bb0a51ce1dd7"


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


checks: list[dict[str, object]] = []


def check(name: str, condition: bool, detail: object) -> None:
    checks.append({"check": name, "pass": bool(condition), "detail": detail})


def main() -> None:
    source_path = HERE / "V77_R3_FROZEN_SOURCE_INVENTORY.tsv"
    target_path = HERE / "V77_TARGET_FREEZE.tsv"
    source = read_tsv(source_path)
    target = read_tsv(target_path)
    decisions = read_tsv(HERE / "V77_R3_DECISION_TABLE.tsv")
    occurrences = read_tsv(HERE / "V77_R3_OCCURRENCE_AUDIT.tsv")
    withdrawals = read_tsv(HERE / "V77_R3_WITHDRAWALS.tsv")
    summary = json.loads((HERE / "V77_R3_BUILD_SUMMARY.json").read_text(encoding="utf-8"))
    freeze = json.loads((HERE / "V77_R3_SOURCE_FREEZE.json").read_text(encoding="utf-8"))
    report = (HERE / "V77_R3_TECHNICAL_ATTESTATION_REPORT.md").read_text(encoding="utf-8")
    cards = {r["joint_tuple_id"]: r for r in read_tsv(V69 / "V69_R4_FINAL_173_CARD_DICTIONARY.tsv")}
    all_events = read_tsv(V69 / "V69_R4_FINAL_381_PROSE_EVENT_INTERLINEAR.tsv")

    check("source_hash", sha(source_path) == SOURCE_HASH, sha(source_path))
    check("source_freeze_hash", freeze["inventory_sha256"] == SOURCE_HASH, freeze["inventory_sha256"])
    check("source_preopening_hash_retained", "2025a22b09cee35252ddcdf4c361f9ec13b3afa64b56bb2fa06527d303bca1e4" in freeze["post_opening_mechanical_amendment"], freeze["post_opening_mechanical_amendment"])
    check("source_rows_37", len(source) == 37, len(source))
    check("source_ids_unique", len({r["source_entry_id"] for r in source}) == 37, len({r["source_entry_id"] for r in source}))
    check("source_order_complete", [int(r["source_order"]) for r in source] == list(range(1, 38)), [r["source_order"] for r in source[:3]])
    check("source_dates_in_window", all(1370 <= int(r["key_date"]) <= 1450 for r in source), sorted({r["key_date"] for r in source}))
    required_source = ["exact_source_language_entry", "opaque_code_or_sign", "historical_key_identity", "archive_shelfmark", "key_date", "dated_correspondence_or_context", "edition_location", "facsimile_location", "codebook_type", "full_citation", "stable_source_locator", "source_pdf_sha256", "transcription_confidence"]
    check("source_required_fields", all(all(r[field].strip() for field in required_source) for r in source), required_source)
    check("source_no_card_binding", all(r["voynich_binding_at_freeze"] == "NOT_REVEALED" for r in source), "37/37")
    check("source_no_anonymous_tuple_ids", not any("joint_tuple" in key.lower() for key in source[0]), list(source[0]))
    check("source_stable_url", all(r["stable_source_locator"].startswith("https://archive.org/") for r in source), source[0]["stable_source_locator"])

    check("target_hash", sha(target_path) == TARGET_HASH, sha(target_path))
    check("target_rows_24", len(target) == 24, len(target))
    check("target_controls_14", sum(r["selection_class"] == "V69_REUSABLE_CONTROL" for r in target) == 14, Counter(r["selection_class"] for r in target))
    check("target_noncontrols_10", sum(r["selection_class"] == "TOP10_RECURRENT_NONCONTROL" for r in target) == 10, Counter(r["selection_class"] for r in target))
    check("target_occurrences_197", sum(int(r["occurrences"]) for r in target) == 197, sum(int(r["occurrences"]) for r in target))
    controls = {cid for cid, row in cards.items() if row["V69_FINAL_CONTROL_CLASS"] != "UNKNOWN_EXEMPLAR_WHOLE_CARD"}
    ranked = sorted((row for row in cards.values() if row["V69_FINAL_CONTROL_CLASS"] == "UNKNOWN_EXEMPLAR_WHOLE_CARD"), key=lambda row: (-int(row["occurrences"]), row["joint_tuple_id"]))[:10]
    check("target_exact_controls", controls == {r["joint_tuple_id"] for r in target if r["selection_class"] == "V69_REUSABLE_CONTROL"}, sorted(controls))
    check("target_frequency_only_top10", [r["joint_tuple_id"] for r in ranked] == [r["joint_tuple_id"] for r in target if r["selection_class"] == "TOP10_RECURRENT_NONCONTROL"], [r["joint_tuple_id"] for r in ranked])

    check("decision_rows_24", len(decisions) == 24, len(decisions))
    check("decision_order_matches_target", [r["joint_tuple_id"] for r in decisions] == [r["joint_tuple_id"] for r in target], "exact")
    check("decision_all_complete", all(all(value.strip() for value in row.values()) for row in decisions), "no blanks")
    check("zero_attested_categories", all(r["codebook_attested_category"] == "NO" for r in decisions), Counter(r["codebook_attested_category"] for r in decisions))
    check("portable_class_counts", Counter(r["portable_dictionary_decision"] for r in decisions) == Counter({"EXEMPLAR_VALUE_UNKNOWN": 21, "FORMAL_LABEL_NOT_WORD": 3}), Counter(r["portable_dictionary_decision"] for r in decisions))
    check("formal_channel_count_4", sum(r["formal_channel_decision"] == "FORMAL_LABEL_NOT_WORD" for r in decisions) == 4, sum(r["formal_channel_decision"] == "FORMAL_LABEL_NOT_WORD" for r in decisions))
    check("no_source_matches", all(r["exact_source_match_ids"] == "NONE" and r["exact_source_entry"] == "NONE" and r["exact_source_code"] == "NONE" for r in decisions), "24/24")
    check("all_false_friend_audited", all(r["false_friend_audit"] for r in decisions), "24/24")
    check("all_confound_audited", all(r["close_or_placement_confound"] for r in decisions), "24/24")
    check("all_polyfunction_audited", all(r["whole_card_polyfunctionality_stress"] for r in decisions), "24/24")

    check("occurrence_rows_197", len(occurrences) == 197, len(occurrences))
    check("occurrence_ids_unique", len({r["audit_occurrence_id"] for r in occurrences}) == 197, len({r["audit_occurrence_id"] for r in occurrences}))
    check("event_serials_unique", len({r["event_serial"] for r in occurrences}) == 197, len({r["event_serial"] for r in occurrences}))
    check("occurrences_complete", all(all(value.strip() for value in row.values()) for row in occurrences), "no blanks")
    target_counts = {r["joint_tuple_id"]: int(r["occurrences"]) for r in target}
    observed_counts = Counter(r["joint_tuple_id"] for r in occurrences)
    check("occurrence_counts_match_manifest", observed_counts == Counter(target_counts), observed_counts)
    expected_serials = {e["event_serial"] for e in all_events if e["joint_tuple_id"] in target_counts}
    check("complete_selected_occurrences", {r["event_serial"] for r in occurrences} == expected_serials, len(expected_serials))
    allowed_pages = {"f10r", "f11r", "f55v", "f56r", "f81v", "f82r", "f83r"}
    check("occurrence_pages_allowed", {r["page"] for r in occurrences} <= allowed_pages, sorted({r["page"] for r in occurrences}))
    check("sealed_pages_absent", not ({"f84", "f84r"} & {r["page"] for r in occurrences}), sorted({r["page"] for r in occurrences}))
    check("no_page_host_column", all("page_host" not in key.lower() for key in occurrences[0]) and all("page_host" not in key.lower() for key in decisions[0]), [*decisions[0], *occurrences[0]])
    check("terminal_selected_count", sum(r["terminal_status"] == "TERMINAL" for r in occurrences) == 45, sum(r["terminal_status"] == "TERMINAL" for r in occurrences))
    handle_by_id = {r["joint_tuple_id"]: r["legacy_mnemonic_handle"] for r in decisions}
    for handle in ("SPÜLEN?", "ABLASSEN?"):
        ids = {cid for cid, h in handle_by_id.items() if h == handle}
        rows = [r for r in occurrences if r["joint_tuple_id"] in ids]
        check(f"{handle}_all_terminal", len(rows) == 8 and all(r["terminal_status"] == "TERMINAL" for r in rows), len(rows))

    check("withdrawal_rows_15", len(withdrawals) == 15, len(withdrawals))
    check("withdrawal_mnemonics_11", sum(r["channel_type"] == "LEGACY_MNEMONIC" for r in withdrawals) == 11, Counter(r["channel_type"] for r in withdrawals))
    check("withdrawal_formal_4", sum(r["channel_type"] == "FORMAL_PROMPT" for r in withdrawals) == 4, Counter(r["channel_type"] for r in withdrawals))
    check("withdrawal_replacements", all(r["replacement"] in {"EXEMPLAR_VALUE_UNKNOWN", "FORMAL_LABEL_NOT_WORD"} for r in withdrawals), Counter(r["replacement"] for r in withdrawals))

    check("summary_decision", summary["decision"] == "ZERO_PORTABLE_WORDS__11_MNEMONICS_TO_UNKNOWN__4_FORMAL_CHANNELS_NONWORD", summary["decision"])
    check("summary_sealed", summary["sealed"] == ["f84", "f84r"], summary["sealed"])
    check("summary_forbidden_zero", all(value == 0 for value in summary["forbidden_feature_use"].values()), summary["forbidden_feature_use"])
    for name, expected in summary["output_sha256"].items():
        check(f"hash_{name}", sha(HERE / name) == expected, sha(HERE / name))

    for phrase in (
        "ZERO_PORTABLE_WORDS__11_MNEMONICS_TO_UNKNOWN__4_FORMAL_CHANNELS_NONWORD",
        "37 wirkliche",
        "24 Identitaeten und 197/381",
        "8/8 terminal",
        "45/197",
        "FORMAL_LABEL_NOT_WORD",
        "EXEMPLAR_VALUE_UNKNOWN",
        "f84 und f84r blieben versiegelt",
    ):
        check(f"report_{phrase[:24]}", phrase in report, phrase)

    passed = sum(item["pass"] for item in checks)
    payload = {
        "round": "V77_R3",
        "status": "PASS" if passed == len(checks) else "FAIL",
        "checks_passed": passed,
        "checks_total": len(checks),
        "scope": {"source_entries": len(source), "cards": len(decisions), "occurrences": len(occurrences), "withdrawal_channels": len(withdrawals)},
        "decision": summary["decision"],
        "checks": checks,
    }
    OUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({key: payload[key] for key in ("round", "status", "checks_passed", "checks_total", "scope", "decision")}, ensure_ascii=False, indent=2))
    if payload["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
