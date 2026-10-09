#!/usr/bin/env python3
"""Build the bounded V81 R3 Phase-2 audit from explicit frozen inputs only."""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path


BASE = Path(__file__).resolve().parent

SOURCE_INVENTORY = BASE / "V81_R3_SOURCE_INVENTORY.tsv"
SOURCE_FREEZE = BASE / "V81_R3_SOURCE_FREEZE.json"
TARGET_FREEZE = BASE / "V81_TARGET_FREEZE.json"
TARGET_MANIFEST = BASE / "V81_TARGET_MANIFEST.tsv"
TARGET_OCCURRENCES = BASE / "V81_TARGET_OCCURRENCE_PACKET.tsv"
TARGET_STATEMENTS = BASE / "V81_TARGET_AFFECTED_STATEMENTS.tsv"

DECISIONS_OUT = BASE / "V81_R3_PHASE2_DECISIONS.tsv"
OCCURRENCE_AUDIT_OUT = BASE / "V81_R3_PHASE2_OCCURRENCE_AUDIT.tsv"
STATEMENT_REVISIONS_OUT = BASE / "V81_R3_PHASE2_STATEMENT_REVISIONS.tsv"

EXPECTED_HASHES = {
    SOURCE_INVENTORY: "6ac100560aa5d0ebba24494cb513972e02a63b809e9d7fd0e2f251c2ae356ac2",
    SOURCE_FREEZE: "89faaeb866ced5ac12da4c4e1b214470f81fa7bff5076faa16bf077f3c2376ff",
    TARGET_FREEZE: "76b102a61f30ca9aa507a6c42b5315f6c43e75628d19c0ebe10ef835ec44a06d",
    TARGET_MANIFEST: "c2c2ad1bd6418ed7a332d6ed948192f469ce8fd64e6cd4c5c5c87e33b76e2b04",
    TARGET_OCCURRENCES: "b6cc5afd9421a64aaec6644f095160a42f8e7999bd63ea3151a05860dd9896ee",
    TARGET_STATEMENTS: "8a0b627902605ca59a7f25f1d148d1fdc0b00f63e53a1f5617409e0af25ca2b7",
}

ADVISORY = (
    "DISCLOSED_OLD_V77_LINES__DOCUMENTARY_ELIGIBLE__"
    "STRICT_INDEPENDENCE_ADVISORY"
)

CANDIDATES = (
    {
        "candidate_id": "C01_NICCOLO_FORTIBRACCIO",
        "source_entry": "Niccolo Fortibraccio",
        "source_inventory_rows": "SI1_001",
        "atomic_default_de": "NICCOLO FORTIBRACCIO",
        "atomic_category": "NAMED_INDIVIDUAL",
        "contradiction": (
            "No named historical individual is present in the supplied occurrence; "
            "the exact name would invent a person referent."
        ),
        "repair": "INVENT_NAMED_INDIVIDUAL_AND_OVERRIDE_SUPPLIED_CONTEXT",
    },
    {
        "candidate_id": "C02_DUCA_DI_MILANO",
        "source_entry": "Duca di Milano",
        "source_inventory_rows": "SI1_002",
        "atomic_default_de": "HERZOG VON MAILAND",
        "atomic_category": "SPECIFIC_DUCAL_TITLE_AND_PLACE",
        "contradiction": (
            "No Milanese duke, office, or place referent is present in the supplied "
            "occurrence; the title would invent a specific external referent."
        ),
        "repair": "INVENT_DUCAL_MILAN_REFERENT_AND_OVERRIDE_SUPPLIED_CONTEXT",
    },
    {
        "candidate_id": "C03_SERENISSIMUS",
        "source_entry": "Serenissimus",
        "source_inventory_rows": "SI1_003A|SI1_003B|SI1_003C",
        "atomic_default_de": "HÖCHST DURCHLAUCHT",
        "atomic_category": "HONORIFIC",
        "contradiction": (
            "No honorific addressee or high-status person is present in the supplied "
            "occurrence; the honorific would invent an address or title slot."
        ),
        "repair": "INVENT_HONORIFIC_ADDRESSEE_AND_OVERRIDE_SUPPLIED_CONTEXT",
    },
)


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, fieldnames: list[str], rows: list[dict[str, object]]) -> None:
    temporary = path.with_suffix(path.suffix + ".tmp")
    with temporary.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            delimiter="\t",
            fieldnames=fieldnames,
            extrasaction="raise",
            lineterminator="\n",
        )
        writer.writeheader()
        writer.writerows(rows)
    temporary.replace(path)


def unique(rows: list[dict[str, str]], field: str) -> list[str]:
    return list(dict.fromkeys(row[field] for row in rows))


def occurrence_rival(row: dict[str, str]) -> str:
    readback = row["autonomous_operational_readback"]
    if readback != "OPAQUE_EXACT_CARD__EXEMPLAR_VALUE_UNKNOWN":
        return readback
    if row["terminal_status"] == "TERMINAL":
        return "CLOSE_OR_TERMINAL_OPERATION"
    return "OWNER_RECORD_LOCAL_EXEMPLAR_OR_OPAQUE_EXACT_CARD"


def verify_inputs() -> None:
    for path, expected in EXPECTED_HASHES.items():
        actual = sha256(path)
        if actual != expected:
            raise SystemExit(f"frozen input hash mismatch: {path.name}: {actual}")

    source_rows = read_tsv(SOURCE_INVENTORY)
    if len(source_rows) != 5:
        raise SystemExit("R3 source inventory must contain exactly five sign rows")
    if {row["exact_source_language_entry"] for row in source_rows} != {
        "Niccolo Fortibraccio",
        "Duca di Milano",
        "Serenissimus",
    }:
        raise SystemExit("unexpected R3 source entry panel")

    source_freeze = json.loads(SOURCE_FREEZE.read_text(encoding="utf-8"))
    if source_freeze["inventory"]["sha256"] != EXPECTED_HASHES[SOURCE_INVENTORY]:
        raise SystemExit("source freeze does not bind the expected inventory")
    if not source_freeze["protocol_incident"]["occurred"]:
        raise SystemExit("old-V77-line advisory was lost")

    target_freeze = json.loads(TARGET_FREEZE.read_text(encoding="utf-8"))
    if target_freeze["source_freeze_hashes"]["R3"] != EXPECTED_HASHES[SOURCE_FREEZE]:
        raise SystemExit("target freeze does not bind the R3 source freeze")
    if target_freeze["source_inventory_hashes"]["R3"] != EXPECTED_HASHES[SOURCE_INVENTORY]:
        raise SystemExit("target freeze does not bind the R3 source inventory")
    if target_freeze["seals"] != {
        "f84": "SEALED_NOT_ACCESSED",
        "f84r": "SEALED_NOT_ACCESSED",
    }:
        raise SystemExit("sealed-page gate failed")


def build() -> None:
    verify_inputs()

    manifest = read_tsv(TARGET_MANIFEST)
    occurrences = read_tsv(TARGET_OCCURRENCES)
    statements = read_tsv(TARGET_STATEMENTS)

    if len(manifest) != 30 or len(occurrences) != 217 or len(statements) != 94:
        raise SystemExit("central target packet counts changed")

    rank = {row["anonymous_target_id"]: int(row["target_rank"]) for row in manifest}
    by_target: dict[str, list[dict[str, str]]] = {key: [] for key in rank}
    for row in occurrences:
        by_target[row["anonymous_target_id"]].append(row)
    for rows in by_target.values():
        rows.sort(key=lambda item: int(item["occurrence_ordinal"]))

    decision_rows: list[dict[str, object]] = []
    for target in manifest:
        target_id = target["anonymous_target_id"]
        rows = by_target[target_id]
        visible = int(target["visible_occurrences"])
        if len(rows) != visible:
            raise SystemExit(f"occurrence count mismatch for {target_id}")

        readbacks = unique(rows, "autonomous_operational_readback")
        expansions = unique(rows, "master_memorized_source_expansion_de")
        all_terminal = all(row["terminal_status"] == "TERMINAL" for row in rows)
        some_terminal = any(row["terminal_status"] == "TERMINAL" for row in rows)
        nonopaque = [
            item for item in readbacks
            if item != "OPAQUE_EXACT_CARD__EXEMPLAR_VALUE_UNKNOWN"
        ]

        if nonopaque:
            silent_formal = "|".join(nonopaque)
            strongest_rival = silent_formal
        elif all_terminal:
            silent_formal = "AVAILABLE__NO_WORD_REQUIRED"
            strongest_rival = "CLOSE_OR_TERMINAL_OPERATION"
        else:
            silent_formal = "AVAILABLE__NO_WORD_REQUIRED"
            strongest_rival = "OWNER_RECORD_LOCAL_EXEMPLAR_OR_OPAQUE_EXACT_CARD"

        if all_terminal:
            position_close = (
                f"STRONG__ALL_{visible}_OCCURRENCES_TERMINAL__"
                "CLOSE_EXPLAINS_WITHOUT_WORD"
            )
        elif some_terminal:
            position_close = "AVAILABLE__MIXED_TERMINAL_PLACEMENT"
        else:
            position_close = "AVAILABLE__NONCLOSE_POSITIONAL_REUSE"

        record_gate = (
            "PASS__AT_LEAST_TWO_FORMAL_RECORDS"
            if int(target["distinct_records"]) >= 2
            else "FAIL__ONLY_ONE_FORMAL_RECORD"
        )
        candidate_panel = "|".join(
            f"{candidate['candidate_id']}:REJECT"
            for candidate in CANDIDATES
        )
        tested = visible * len(CANDIDATES)

        decision_rows.append(
            {
                "target_rank": target["target_rank"],
                "anonymous_target_id": target_id,
                "joint_tuple_id": target["joint_tuple_id"],
                "visible_occurrences": visible,
                "independent_source_positions": target["independent_source_positions"],
                "distinct_pages": target["distinct_pages"],
                "distinct_records": target["distinct_records"],
                "source_entries_tested": "Niccolo Fortibraccio|Duca di Milano|Serenissimus",
                "source_inventory_rows": "SI1_001|SI1_002|SI1_003A|SI1_003B|SI1_003C",
                "proposed_atomic_defaults_de": (
                    "NICCOLO FORTIBRACCIO|HERZOG VON MAILAND|HÖCHST DURCHLAUCHT"
                ),
                "atomicity_gate": (
                    "PASS__SOURCE_GRANULARITY_ONLY__EACH_DEFAULT_AT_MOST_THREE_WORDS"
                ),
                "exact_historical_pairing_gate": "PASS__THREE_ENTRIES_FIVE_EXACT_SIGNS",
                "compatible_candidate_occurrences": 0,
                "tested_candidate_occurrences": tested,
                "invariant_default_gate": "FAIL__NO_SOURCE_DEFAULT_CONTEXT_COMPATIBLE",
                "at_least_two_records_gate": record_gate,
                "every_occurrence_usable_gate": (
                    f"FAIL__0_OF_{visible}_COMPATIBLE_FOR_EACH_SOURCE_ENTRY"
                ),
                "improved_complete_statements": 0,
                "two_statement_improvement_gate": "FAIL__ZERO_STATEMENTS_IMPROVED",
                "silent_formal_rival": silent_formal,
                "frequency_rival": (
                    "MATCHED__TARGET_SELECTED_BY_FREQUENCY_ONLY__"
                    "REUSE_DOES_NOT_IDENTIFY_A_WORD"
                ),
                "position_close_rival": position_close,
                "owner_exemplar_copy_rival": (
                    f"STRONG__{len(expansions)}_SUPPLIED_EXPANSION_TYPE(S)__"
                    "OWNER_OR_RECORD_LOCAL_READBACK_REQUIRES_NO_PORTABLE_WORD"
                ),
                "strongest_rival": strongest_rival,
                "repair_cost": (
                    f"{tested}_UNLICENSED_REFERENTS_PLUS_{tested}_CONTEXT_OVERRIDES"
                ),
                "candidate_panel_status": candidate_panel,
                "decision": "REJECT",
                "new_portable_word": "NO",
                "retained_default": "|".join(readbacks),
                "exact_rejection_reason": (
                    "All three source entries require a person, specific title/place, or "
                    "honorific referent absent from every supplied occurrence; each mapping "
                    "would invent a referent and overwrite the formal or operational context."
                ),
                "source_freeze_sha256": EXPECTED_HASHES[SOURCE_FREEZE],
                "source_inventory_sha256": EXPECTED_HASHES[SOURCE_INVENTORY],
                "target_freeze_sha256": EXPECTED_HASHES[TARGET_FREEZE],
                "strict_independence_advisory": ADVISORY,
            }
        )

    decision_fields = list(decision_rows[0])
    write_tsv(DECISIONS_OUT, decision_fields, decision_rows)

    occurrence_audit_rows: list[dict[str, object]] = []
    audit_serial = 0
    for target in sorted(manifest, key=lambda item: int(item["target_rank"])):
        target_id = target["anonymous_target_id"]
        for row in by_target[target_id]:
            for candidate in CANDIDATES:
                audit_serial += 1
                occurrence_audit_rows.append(
                    {
                        "audit_row_id": f"OA{audit_serial:04d}",
                        "candidate_id": candidate["candidate_id"],
                        "source_entry": candidate["source_entry"],
                        "source_inventory_rows": candidate["source_inventory_rows"],
                        "atomic_default_de": candidate["atomic_default_de"],
                        "atomic_category": candidate["atomic_category"],
                        "anonymous_target_id": target_id,
                        "occurrence_ordinal": row["occurrence_ordinal"],
                        "event_serial": row["event_serial"],
                        "event_id": row["event_id"],
                        "page": row["page"],
                        "record_unit_id": row["record_unit_id"],
                        "locus": row["locus"],
                        "field_id": row["field_id"],
                        "statement_id": row["statement_id"],
                        "image_owner_id": row["image_owner_id"],
                        "owner_break_before": row["owner_break_before"],
                        "source_position_id": row["source_position_id"],
                        "autonomous_operational_readback": row[
                            "autonomous_operational_readback"
                        ],
                        "formal_nonword_channel": row["formal_nonword_channel"],
                        "master_memorized_selected_token": row[
                            "master_memorized_selected_token"
                        ],
                        "master_memorized_source_expansion_de": row[
                            "master_memorized_source_expansion_de"
                        ],
                        "terminal_status": row["terminal_status"],
                        "line_crossing": row["line_crossing"],
                        "packet_strongest_contradiction": row["strongest_contradiction"],
                        "source_category_referent_observed": "NO",
                        "core_sense_usable": "NO",
                        "statement_improved": "NO",
                        "strongest_rival": occurrence_rival(row),
                        "candidate_contradiction": candidate["contradiction"],
                        "repair_required": candidate["repair"],
                        "occurrence_decision": "REJECT",
                        "source_freeze_sha256": EXPECTED_HASHES[SOURCE_FREEZE],
                        "strict_independence_advisory": ADVISORY,
                    }
                )

    occurrence_fields = list(occurrence_audit_rows[0])
    write_tsv(OCCURRENCE_AUDIT_OUT, occurrence_fields, occurrence_audit_rows)

    statement_rows: list[dict[str, object]] = []
    for row in statements:
        statement_rows.append(
            {
                "statement_id": row["statement_id"],
                "record_unit_id": row["record_unit_id"],
                "page": row["page"],
                "constituent_fields": row["constituent_fields"],
                "physical_lines": row["physical_lines"],
                "visible_event_count": row["visible_event_count"],
                "target_occurrences": row["target_occurrences"],
                "anonymous_targets_in_order": row["anonymous_targets_in_order"],
                "original_operational_formal_order": row["operational_formal_order"],
                "original_optional_master_gloss_order": row[
                    "optional_master_gloss_order"
                ],
                "original_master_memorized_statement_content": row[
                    "master_memorized_statement_content"
                ],
                "rival_statement_content": row["rival_statement_content"],
                "packet_strongest_contradiction": row["strongest_contradiction"],
                "semantic_ceiling": row["semantic_ceiling"],
                "promoted_or_near_targets": "NONE",
                "r3_revision_required": "NO",
                "r3_revised_operational_formal_order": row["operational_formal_order"],
                "r3_revised_continuous_reading_de": row[
                    "master_memorized_statement_content"
                ],
                "r3_revision_status": "UNCHANGED__NO_PROMOTED_OR_NEAR_CANDIDATE",
                "r3_revision_reason": (
                    "No exact Si1 source category passed occurrence invariance or improved "
                    "this statement; retain the supplied reading and semantic ceiling."
                ),
                "source_freeze_sha256": EXPECTED_HASHES[SOURCE_FREEZE],
                "strict_independence_advisory": ADVISORY,
            }
        )

    statement_fields = list(statement_rows[0])
    write_tsv(STATEMENT_REVISIONS_OUT, statement_fields, statement_rows)

    print(
        json.dumps(
            {
                "decisions": len(decision_rows),
                "occurrence_audit_rows": len(occurrence_audit_rows),
                "statement_revisions": len(statement_rows),
                "promoted": 0,
                "near": 0,
                "new_portable_words": 0,
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    build()
