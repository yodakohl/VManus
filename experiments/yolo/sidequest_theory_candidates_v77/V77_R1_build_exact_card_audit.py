#!/usr/bin/env python3
"""Build the bounded V77 R1 source-first exact-card audit.

The historical source inventory is a frozen input.  This script never reads
Voynich spelling, stems, PAGE_HOST, sound, or any page outside the selected
V73/V74 prose editions.
"""

from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = Path(__file__).resolve().parents[3]
V69 = ROOT / "experiments/yolo/sidequest_theory_candidates_v69/V69_R4_FINAL_173_CARD_DICTIONARY.tsv"
V73 = ROOT / "experiments/yolo/sidequest_theory_candidates_v73/V73_SELECTED_100_EVENT_INTERLINEAR.tsv"
V74 = ROOT / "experiments/yolo/sidequest_theory_candidates_v74/V74_SELECTED_281_EVENT_INTERLINEAR.tsv"
SOURCE = HERE / "V77_R1_SOURCE_FIRST_CODEBOOK_INVENTORY.tsv"
TARGET = HERE / "V77_TARGET_FREEZE.tsv"

SOURCE_SHA256 = "8f2c6afdcdfb2759a10d83c4a4404fabf3448522c8013f46e7418e06e258bfda"
TARGET_SHA256 = "2b5659f9d7cd213fc22842c38e38388061096b9407723628bb82bb0a51ce1dd7"
TOP_N_NONCONTROL = 10
ALLOWED_PAGES = {"f10r", "f11r", "f55v", "f56r", "f81v", "f82r", "f83r"}
SEALED_PAGES = {"f84", "f84r"}

CONTROL = {
    "0275fbf14e07935b0a45": ("TEMPERIEREN?", "MNEMONIC"),
    "276a7c2d74d1143446f4": ("ANWENDEN?", "MNEMONIC"),
    "2f1c5e56e8f0ff459065": ("MASS? + SURFACE_DAIIN_ONLY:VORGABEPARAMETER?", "MIXED"),
    "308e8ea2d5d190c498e8": ("LOKALEN_RELATIONSSLOT_SETZEN", "FORMAL"),
    "7a4bb8136330ee4e6e56": ("ANSATZ?", "MNEMONIC"),
    "7db18b2f0fb7ed0fcfd3": ("SPÜLEN?", "MNEMONIC"),
    "b5df9126607030b95175": ("KLAR?", "MNEMONIC"),
    "b5fcea1eaed06b2f2291": ("STANDARDSLOT_SETZEN", "FORMAL"),
    "dcda95c81a5460feb191": ("AKTIVEN_ARBEITSSTAND_VERKNÜPFEN", "FORMAL"),
    "dd0ecaf5e27d81befffc": ("ZIEL?", "MNEMONIC"),
    "de7321bface5628e35d6": ("ABLASSEN?", "MNEMONIC"),
    "dec401773c1f0347793d": ("VORIGES?", "MNEMONIC"),
    "e0b630cb1b5df5e7105b": ("BEREIT?", "MNEMONIC"),
    "faf321940aed922846a9": ("ANTEIL?", "MNEMONIC"),
}

FROZEN_TOP10 = [
    "b921a237be883a820352",
    "bc4f1f5c006c74a4d26d",
    "6f7ff8287eddf4da9fdb",
    "7d25241b0e56c836372a",
    "1645e612504fcef59ced",
    "4d4559019a961b834aa1",
    "259b2b3b0bf859882e2c",
    "2cc054357a929df85f64",
    "2cc8bb3c2af19607888f",
    "28ffbc88b97772a75f1e",
]

CONSISTENCY = {
    "0275fbf14e07935b0a45": ("HIGH_CONTEXTUAL", "all seven Bio occurrences use a tempering expansion; no independent atomic source value"),
    "276a7c2d74d1143446f4": ("BROAD_CONTEXTUAL", "use/application recurs, but route and object vary from internal use to external and bath use"),
    "2f1c5e56e8f0ff459065": ("HIGH_FORMAL_MIXED", "measure/prescription expansion recurs; only the restricted formal channel survives, not MASS as a word"),
    "308e8ea2d5d190c498e8": ("FORMAL_ONLY", "local relation-slot behavior is reusable; it supplies no word value"),
    "7a4bb8136330ee4e6e56": ("BROAD_CONTEXTUAL", "active-post/ansatz continuation recurs, but the object and operation are supplied locally"),
    "7db18b2f0fb7ed0fcfd3": ("HIGH_CONTEXTUAL", "all occurrences receive a rinse expansion in Bio; image and local station supply its arguments"),
    "b5df9126607030b95175": ("MIXED_CONTEXTUAL", "Herbal clear-state and Bio generic test-state expansions do not yield one atomic value"),
    "b5fcea1eaed06b2f2291": ("FORMAL_ONLY", "standard-slot placement recurs; it supplies no word value"),
    "dcda95c81a5460feb191": ("FORMAL_ONLY", "active record-state linkage recurs; it supplies no word value"),
    "dd0ecaf5e27d81befffc": ("BROAD_CONTEXTUAL", "a local target/station is repeatedly supplied by context, not by an attested atomic value"),
    "de7321bface5628e35d6": ("HIGH_CONTEXTUAL", "Bio expansions consistently drain used liquid, but no exact historical entry anchors the card"),
    "dec401773c1f0347793d": ("HIGH_CONTEXTUAL_LOW_SUPPORT", "two occurrences reuse a prior post; support is too small and unattested"),
    "e0b630cb1b5df5e7105b": ("MIXED_CONTEXTUAL", "flowering time, readiness, and generic test-state expansions are not one invariant atomic value"),
    "faf321940aed922846a9": ("HIGH_CONTEXTUAL_LOW_SUPPORT", "two occurrences select a portion; support is too small and unattested"),
    "b921a237be883a820352": ("CONTRADICTORY", "eighteen expansions include fraction, oil, heat, stirring, storage, use, honey, and deictic portion"),
    "bc4f1f5c006c74a4d26d": ("HIGH_CONTEXTUAL", "all twelve Bio expansions mark readiness plus step ending; no historical lexical anchor"),
    "6f7ff8287eddf4da9fdb": ("CONTRADICTORY", "Herbal wringing/settling conflicts with repeated Bio mixing expansions"),
    "7d25241b0e56c836372a": ("BROAD_CONTEXTUAL", "a terminal construction recurs, but bathing, washing, and cloth immersion are supplied locally"),
    "1645e612504fcef59ced": ("HIGH_CONTEXTUAL", "all seven Bio expansions add a measured share to a vessel; no historical lexical anchor"),
    "4d4559019a961b834aa1": ("BROAD_CONTEXTUAL", "same-post linkage recurs, but merging and deictic source readings vary"),
    "259b2b3b0bf859882e2c": ("HIGH_CONTEXTUAL", "all four Bio expansions rinse a used vessel/run and close; no historical lexical anchor"),
    "2cc054357a929df85f64": ("CONTRADICTORY", "one Herbal page assigns collection, crushing, drying, and adding honey to the same card"),
    "2cc8bb3c2af19607888f": ("HIGH_CONTEXTUAL", "all four Bio expansions point through connected runs; no historical lexical anchor"),
    "28ffbc88b97772a75f1e": ("HIGH_CONTEXTUAL", "all three Bio expansions set aside a covered catch vessel and close"),
}


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh, delimiter="\t"))


def write_tsv(path: Path, rows: list[dict[str, object]], fields: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    assert hashlib.sha256(SOURCE.read_bytes()).hexdigest() == SOURCE_SHA256, "source-first inventory changed after freeze"
    assert hashlib.sha256(TARGET.read_bytes()).hexdigest() == TARGET_SHA256, "central target manifest changed after freeze"
    source_rows = read_tsv(SOURCE)
    target_rows = read_tsv(TARGET)
    assert len(source_rows) == 22 and len({r["key_id"] for r in source_rows}) == 2
    assert len(target_rows) == 24

    v69 = {r["joint_tuple_id"]: r for r in read_tsv(V69)}
    herbal = read_tsv(V73)
    bio = read_tsv(V74)
    assert len(herbal) == 100 and len(bio) == 281
    events = herbal + bio
    assert len(events) == 381
    assert {r["page"] for r in events} <= ALLOWED_PAGES
    assert not ({r["page"] for r in events} & SEALED_PAGES)

    frequencies = Counter(r["joint_tuple_id"] for r in events)
    computed_top = [
        card for card, _ in sorted(
            ((card, n) for card, n in frequencies.items() if card not in CONTROL),
            key=lambda item: (-item[1], item[0]),
        )[:TOP_N_NONCONTROL]
    ]
    assert computed_top == FROZEN_TOP10, "frequency-bounded membership changed"
    selected = list(CONTROL) + FROZEN_TOP10
    assert selected == [r["joint_tuple_id"] for r in target_rows], "builder target order differs from central freeze"
    selected_set = set(selected)
    by_card: dict[str, list[dict[str, str]]] = defaultdict(list)
    for event in events:
        if event["joint_tuple_id"] in selected_set:
            by_card[event["joint_tuple_id"]].append(event)
    assert sum(len(rows) for rows in by_card.values()) == 197

    decision_rows: list[dict[str, object]] = []
    decisions: dict[str, str] = {}
    for card in selected:
        old = v69[card]
        rank = (FROZEN_TOP10.index(card) + 1) if card in FROZEN_TOP10 else "NA"
        if card in CONTROL:
            legacy, channel = CONTROL[card]
            stratum = "FROZEN_14_CONTROL"
        else:
            legacy, channel = "NONE", "FREQUENCY_BOUNDED_UNKNOWN"
            stratum = "TOP10_RECURRENT_NONCONTROL"
        final = "FORMAL_LABEL_NOT_WORD" if channel in {"FORMAL", "MIXED"} else "EXEMPLAR_VALUE_UNKNOWN"
        decisions[card] = final
        consistency, consistency_reason = CONSISTENCY[card]
        card_events = by_card[card]
        decision_rows.append({
            "joint_tuple_id": card,
            "selection_stratum": stratum,
            "frequency_rank_within_noncontrol": rank,
            "occurrences_in_381_event_panel": len(card_events),
            "pages": "|".join(sorted({r["page"] for r in card_events})),
            "records": "|".join(sorted({r["record_unit_id"] for r in card_events})),
            "surface_examples_archive_only": old["surface_examples"],
            "legacy_handle_revealed_after_source_freeze": legacy,
            "legacy_channel": channel,
            "v69_control_class": old["V69_FINAL_CONTROL_CLASS"],
            "occurrence_consistency": consistency,
            "occurrence_consistency_reason": consistency_reason,
            "exact_source_match_row_id": "NONE",
            "exact_source_entry": "NONE",
            "historical_key": "NONE_MATCHING_PROPOSED_VALUE",
            "date_and_correspondence": "NONE_MATCHING_PROPOSED_VALUE",
            "archive_location": "NONE_MATCHING_PROPOSED_VALUE",
            "codebook_type": "NONE_MATCHING_PROPOSED_VALUE",
            "code_or_sign": "NONE_MATCHING_PROPOSED_VALUE",
            "citation_and_locator": "NONE_MATCHING_PROPOSED_VALUE",
            "proposed_minimal_gloss": "NONE_ADMITTED",
            "final_atomic_default": final,
            "dictionary_action": (
                "retain only the restricted formal prompt; forbid lexical reading"
                if final == "FORMAL_LABEL_NOT_WORD"
                else "withdraw portable lexical default; obtain content from the local exemplar"
            ),
            "teaching_rule": (
                "copy the exact opaque card and execute only its record-local formal slot instruction"
                if final == "FORMAL_LABEL_NOT_WORD"
                else "copy the exact opaque card; the master exemplar, picture, or oral rubric must supply its local content"
            ),
            "attestation_decision": "NO_PERIOD_ENTRY_CONNECTS_THIS_OPAQUE_CARD_TO_THE_LEGACY_VALUE",
            "semantic_ceiling": "PERIOD_NOMENCLATOR_PRACTICE_ATTESTED;VOYNICH_CARD_IDENTITY_WORD_STEM_SOUND_LANGUAGE_AND_MEANING_NOT_ATTESTED",
        })

    decision_fields = list(decision_rows[0])
    write_tsv(HERE / "V77_R1_BOUNDED_CARD_DECISIONS.tsv", decision_rows, decision_fields)

    occurrence_rows: list[dict[str, object]] = []
    serial = 0
    for event in events:
        card = event["joint_tuple_id"]
        if card not in selected_set:
            continue
        serial += 1
        old = v69[card]
        stratum = "FROZEN_14_CONTROL" if card in CONTROL else "TOP10_RECURRENT_NONCONTROL"
        legacy = CONTROL[card][0] if card in CONTROL else "NONE"
        literal = event.get("exact_literal_card_formal_exemplar_layer", "")
        support = event.get("v69_support_class", event.get("v69_source_status", ""))
        owner = event.get("whole_plant_owner", event.get("local_image_owner", ""))
        consistency, consistency_reason = CONSISTENCY[card]
        occurrence_rows.append({
            "audit_serial": serial,
            "event_serial": event["event_serial"],
            "record_unit_id": event["record_unit_id"],
            "page": event["page"],
            "locus": event["locus"],
            "field_id": event["field_id"],
            "statement_id": event["statement_id"],
            "joint_tuple_id": card,
            "selection_stratum": stratum,
            "surface_examples_archive_only": old["surface_examples"],
            "local_or_page_owner": owner,
            "owner_status": event.get("owner_status", ""),
            "legacy_handle_revealed_after_source_freeze": legacy,
            "legacy_support_class": support,
            "exact_literal_layer_from_selected_edition": literal,
            "legacy_context_expansion": event["concrete_german_meaning_in_context"],
            "occurrence_consistency_class": consistency,
            "occurrence_consistency_reason": consistency_reason,
            "exact_source_match_row_id": "NONE",
            "portable_atomic_reading_after_v77": decisions[card],
            "occurrence_audit_action": (
                "FORMAL_USE_ONLY;DO_NOT_READ_AS_WORD"
                if decisions[card] == "FORMAL_LABEL_NOT_WORD"
                else "CONTEXT_EXEMPLAR_ONLY;DO_NOT_EXPORT_THIS_SENTENCE_AS_CARD_MEANING"
            ),
            "strongest_contradiction_from_selected_edition": event.get("strongest_contradiction", ""),
            "semantic_ceiling": "THIS_ROW_AUDITS_CONTEXTUAL_COHERENCE_ONLY;IT_DOES_NOT_ATTEST_A_WORD_OR_MEANING",
        })
    assert serial == 197
    occurrence_fields = list(occurrence_rows[0])
    write_tsv(HERE / "V77_R1_FULL_OCCURRENCE_AUDIT.tsv", occurrence_rows, occurrence_fields)

    withdrawal_rows: list[dict[str, object]] = []
    for card, (legacy, channel) in CONTROL.items():
        consistency, reason = CONSISTENCY[card]
        if channel == "FORMAL":
            action = "NO_LEXICAL_HANDLE_TO_WITHDRAW;RESTRICT_EXISTING_PROMPT_TO_FORMAL_LABEL_NOT_WORD"
            withdrawn = "ANY_WORD_READING_OF_" + legacy
            replacement = "FORMAL_LABEL_NOT_WORD"
        elif channel == "MIXED":
            action = "WITHDRAW_MASS_AS_WORD;KEEP_SURFACE_DAIIN_ONLY_PROMPT_AS_FORMAL_LABEL_NOT_WORD"
            withdrawn = "MASS?"
            replacement = "FORMAL_LABEL_NOT_WORD"
        else:
            action = "WITHDRAW_AS_PORTABLE_CARD_WORD;ALLOW_ONLY_EXPLICITLY_MARKED_CREATIVE_OCCURRENCE_PARAPHRASE"
            withdrawn = legacy
            replacement = "EXEMPLAR_VALUE_UNKNOWN"
        withdrawal_rows.append({
            "joint_tuple_id": card,
            "legacy_component": withdrawn,
            "legacy_channel": channel,
            "occurrences_audited": len(by_card[card]),
            "occurrence_consistency": consistency,
            "withdrawal_or_restriction": action,
            "replacement_atomic_default": replacement,
            "reason": "no exact 1379 source entry matches or binds the opaque card; " + reason,
            "what_may_remain": (
                "record-local formal production instruction only"
                if replacement == "FORMAL_LABEL_NOT_WORD"
                else "occurrence-specific exemplar expansion visibly marked as creative and nonlexical"
            ),
            "ceiling": "NO_WORD_STEM_SOUND_LANGUAGE_OR_MEANING_CLAIM",
        })
    write_tsv(HERE / "V77_R1_WITHDRAWALS.tsv", withdrawal_rows, list(withdrawal_rows[0]))

    summary = {
        "status": "BUILT",
        "source_inventory_rows": len(source_rows),
        "source_keys": sorted({r["key_id"] for r in source_rows}),
        "source_inventory_sha256": SOURCE_SHA256,
        "target_manifest_sha256": TARGET_SHA256,
        "fixed_control_cards": len(CONTROL),
        "top_n_noncontrol": TOP_N_NONCONTROL,
        "top_noncontrol_cards": FROZEN_TOP10,
        "bounded_cards": len(selected),
        "input_events": len(events),
        "audited_occurrences": serial,
        "formal_label_not_word_cards": sum(d == "FORMAL_LABEL_NOT_WORD" for d in decisions.values()),
        "exemplar_value_unknown_cards": sum(d == "EXEMPLAR_VALUE_UNKNOWN" for d in decisions.values()),
        "admitted_word_rows": 0,
        "pages": sorted({r["page"] for r in events}),
        "sealed_pages_accessed": [],
    }
    (HERE / "V77_R1_BUILD_SUMMARY.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
