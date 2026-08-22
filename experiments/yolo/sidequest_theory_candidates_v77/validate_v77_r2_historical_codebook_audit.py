#!/usr/bin/env python3
"""Validate completeness and no-promotion gates for the V77 R2 audit."""

from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter
from pathlib import Path


HERE = Path(__file__).resolve().parent


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_tsv(name: str) -> list[dict]:
    with (HERE / name).open(encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh, delimiter="\t"))


def check(condition: bool, message: str, checks: list[dict]) -> None:
    checks.append({"check": message, "status": "PASS" if condition else "FAIL"})
    if not condition:
        raise AssertionError(message)


def main() -> None:
    checks: list[dict] = []
    required = [
        "V77_R2_HISTORICAL_SOURCE_CORPUS.tsv",
        "V77_R2_HISTORICAL_ENTRY_INVENTORY.tsv",
        "V77_R2_SOURCE_FREEZE.json",
        "V77_R2_FREQUENCY_CANDIDATE_FREEZE.tsv",
        "V77_R2_FREQUENCY_CANDIDATE_FREEZE.json",
        "V77_R2_CARD_DECISIONS.tsv",
        "V77_R2_OCCURRENCE_AUDIT.tsv",
        "V77_R2_WITHDRAWALS.tsv",
        "V77_R2_ATTESTED_CARD_ROWS.tsv",
        "V77_R2_RESULT.json",
        "V77_R2_HISTORICAL_CODEBOOK_REPORT.md",
        "build_v77_r2_historical_codebook_audit.py",
        "validate_v77_r2_historical_codebook_audit.py",
    ]
    check(all((HERE / name).is_file() for name in required), "all required R2 artifacts exist", checks)

    sources = read_tsv("V77_R2_HISTORICAL_SOURCE_CORPUS.tsv")
    entries = read_tsv("V77_R2_HISTORICAL_ENTRY_INVENTORY.tsv")
    source_freeze = json.loads((HERE / "V77_R2_SOURCE_FREEZE.json").read_text(encoding="utf-8"))
    check(len(sources) == 6, "six real 1379-1442 source objects are frozen", checks)
    check(len(entries) == 48, "48 exact historical entry-code rows are frozen", checks)
    check(
        sha256(HERE / "V77_R2_HISTORICAL_SOURCE_CORPUS.tsv") == source_freeze["historical_source_corpus_sha256"],
        "source corpus hash matches source-first freeze",
        checks,
    )
    check(
        sha256(HERE / "V77_R2_HISTORICAL_ENTRY_INVENTORY.tsv") == source_freeze["historical_entry_inventory_sha256"],
        "entry inventory hash matches source-first freeze",
        checks,
    )
    mandatory_entry_fields = [
        "exact_source_language_entry",
        "opaque_code_or_sign",
        "historical_key_identity",
        "archive_shelfmark",
        "date_or_dated_correspondence",
        "facsimile_or_edition_location",
        "codebook_type",
        "citation",
        "stable_locator",
        "transcription_confidence",
        "granularity_ceiling",
    ]
    check(
        all(all(row.get(field, "").strip() for field in mandatory_entry_fields) for row in entries),
        "every admitted historical row has all mandatory documentary fields",
        checks,
    )
    check(
        all(row["admission_status"] == "ADMITTED_EXACT_HISTORICAL_ENTRY" for row in entries),
        "entry inventory contains no conjectural or OCR-only row",
        checks,
    )
    check(
        sum(int(row["admitted_entry_count"]) for row in sources) == len(entries),
        "source-level admitted counts equal inventory rows",
        checks,
    )
    check(
        source_freeze["card_tables_read_by_this_phase"] == []
        and not source_freeze["desired_word_search_performed"]
        and not source_freeze["ordinary_recipe_prose_admitted"],
        "source phase records no card-table query, desired-word search, or recipe attestation",
        checks,
    )

    target = read_tsv("V77_TARGET_FREEZE.tsv")
    candidates = read_tsv("V77_R2_FREQUENCY_CANDIDATE_FREEZE.tsv")
    candidate_freeze = json.loads((HERE / "V77_R2_FREQUENCY_CANDIDATE_FREEZE.json").read_text(encoding="utf-8"))
    check(len(target) == len(candidates) == 24, "authoritative bounded target has exactly 24 cards", checks)
    check(
        [row["joint_tuple_id"] for row in target] == [row["joint_tuple_id"] for row in candidates],
        "R2 candidate order and identities exactly match central target freeze",
        checks,
    )
    check(sum(int(row["occurrences"]) for row in target) == 197, "central target requires exactly 197 occurrences", checks)
    check(
        candidate_freeze["features_read_for_extra_selection"] == ["joint_tuple_id", "occurrences"]
        and candidate_freeze["semantic_columns_read_for_extra_selection"] == [],
        "noncontrols were frequency-selected without semantic fields",
        checks,
    )

    decisions = read_tsv("V77_R2_CARD_DECISIONS.tsv")
    occurrences = read_tsv("V77_R2_OCCURRENCE_AUDIT.tsv")
    withdrawals = read_tsv("V77_R2_WITHDRAWALS.tsv")
    attestations = read_tsv("V77_R2_ATTESTED_CARD_ROWS.tsv")
    check(len(decisions) == 24, "one final decision exists for every target card", checks)
    check(len(occurrences) == 197, "all 197 target occurrences are audited", checks)
    target_counts = {row["joint_tuple_id"]: int(row["occurrences"]) for row in target}
    audited_counts = Counter(row["anonymous_exact_card_id"] for row in occurrences)
    check(dict(audited_counts) == target_counts, "per-card occurrence counts exactly match target freeze", checks)
    allowed_pages = {"f10r", "f11r", "f55v", "f56r", "f81v", "f82r", "f83r"}
    check({row["page"] for row in occurrences} <= allowed_pages, "occurrence audit uses only fixed Herbal/Biological pages", checks)
    check(
        all(row["historical_attestation_status"] == "NONE_IN_FROZEN_SOURCE_INVENTORY" for row in occurrences),
        "no occurrence is silently promoted by context",
        checks,
    )
    check(len(withdrawals) == 11, "all eleven exposed mnemonic handles are withdrawn", checks)
    check(all(row["replacement"] == "EXEMPLAR_VALUE_UNKNOWN" for row in withdrawals), "every mnemonic withdrawal has the required unknown replacement", checks)
    status_counts = Counter(row["final_decision"] for row in decisions)
    check(
        status_counts == Counter({"EXEMPLAR_VALUE_UNKNOWN": 21, "FORMAL_LABEL_NOT_WORD": 3}),
        "decisions contain 21 unknown values and three explicit formal nonwords",
        checks,
    )
    check(
        sum(row["formal_channel_final_status"] == "FORMAL_LABEL_NOT_WORD" for row in decisions) == 4,
        "four pre-existing formal channels remain explicitly nonword, including the MASS-card channel",
        checks,
    )
    check(len(attestations) == 0, "header-only attestation file confirms zero admitted card words", checks)

    result = json.loads((HERE / "V77_R2_RESULT.json").read_text(encoding="utf-8"))
    check(result["decision"] == "NO_V77_R2_CARD_WORD_ATTESTED", "result endpoint is strict documentary failure", checks)
    check(
        result["formal_only_cards"] == 3 and result["formal_labels_retained_as_nonwords"] == 4,
        "result separates three formal-only cards from four formal nonword channels",
        checks,
    )
    check(result["target_manifest_sha256"] == sha256(HERE / "V77_TARGET_FREEZE.tsv"), "result seals authoritative target hash", checks)
    check(result["card_decisions_sha256"] == sha256(HERE / "V77_R2_CARD_DECISIONS.tsv"), "result seals card decisions", checks)
    check(result["occurrence_audit_sha256"] == sha256(HERE / "V77_R2_OCCURRENCE_AUDIT.tsv"), "result seals occurrence audit", checks)
    check(result["withdrawals_sha256"] == sha256(HERE / "V77_R2_WITHDRAWALS.tsv"), "result seals withdrawals", checks)
    check(
        not result["ordinary_recipe_prose_used_as_attestation"]
        and not result["surface_similarity_used"]
        and not result["desired_word_search_used"],
        "forbidden attestation shortcuts are absent",
        checks,
    )
    check(not result["f84_opened"] and not result["f84r_opened"], "f84 and f84r remain sealed", checks)

    report = (HERE / "V77_R2_HISTORICAL_CODEBOOK_REPORT.md").read_text(encoding="utf-8")
    check("No exact V77 card word is documentarily attested" in report, "report states the principal failure plainly", checks)
    check("unavoidably already visible" in report, "report discloses routing-level prior exposure", checks)
    check("not proof" in report, "report distinguishes failure to attest from historical absence", checks)

    validation = {
        "experiment": "V77_R2",
        "status": "PASS",
        "check_count": len(checks),
        "checks": checks,
        "validated_counts": {
            "sources": len(sources),
            "historical_entries": len(entries),
            "cards": len(decisions),
            "occurrences": len(occurrences),
            "withdrawals": len(withdrawals),
            "attested_card_words": len(attestations),
        },
        "f84_opened": False,
        "f84r_opened": False,
    }
    (HERE / "V77_R2_VALIDATION.json").write_text(
        json.dumps(validation, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(json.dumps({"status": "PASS", "checks": len(checks)}, sort_keys=True))


if __name__ == "__main__":
    main()
