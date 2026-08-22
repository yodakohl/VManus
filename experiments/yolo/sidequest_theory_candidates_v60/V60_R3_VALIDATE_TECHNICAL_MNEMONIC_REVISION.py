#!/usr/bin/env python3
"""Validate the V60 R3 11-card / 85-occurrence technical revision."""

from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
V59 = ROOT / "experiments" / "yolo" / "sidequest_theory_candidates_v59"
FILES = {
    "decisions": HERE / "V60_R3_11_CARD_TECHNICAL_DECISIONS.tsv",
    "audit": HERE / "V60_R3_85_OCCURRENCE_AUDIT.tsv",
    "cards": HERE / "V60_R3_REVISED_STRICT_173_CARD_DICTIONARY.tsv",
    "events": HERE / "V60_R3_REVISED_STRICT_381_EVENT_INTERLINEAR.tsv",
}
SOURCE_CARDS = V59 / "V59_R1_FINAL_173_CARD_DICTIONARY.tsv"
SOURCE_EVENTS = V59 / "V59_R1_FINAL_381_PROSE_EVENT_INTERLINEAR.tsv"
VALIDATION = HERE / "V60_R3_VALIDATION.json"
ALLOWED_PAGES = {"f10r", "f11r", "f55v", "f56r", "f81v", "f82r", "f83r"}


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> None:
    source_cards = read_tsv(SOURCE_CARDS)
    source_events = read_tsv(SOURCE_EVENTS)
    decisions = read_tsv(FILES["decisions"])
    audit = read_tsv(FILES["audit"])
    cards = read_tsv(FILES["cards"])
    events = read_tsv(FILES["events"])
    checks: dict[str, bool] = {}

    checks["counts_11_85_173_381"] = (len(decisions), len(audit), len(cards), len(events)) == (11, 85, 173, 381)
    checks["decision_exact_ids_unique"] = len({row["exact_joint_tuple_id"] for row in decisions}) == 11
    checks["audit_rows_unique"] = len({row["event_serial"] for row in audit}) == 85
    checks["source_card_identity_preserved"] = [row["joint_tuple_id"] for row in cards] == [row["joint_tuple_id"] for row in source_cards]
    checks["source_event_identity_preserved"] = all(
        all(new[key] == old[key] for key in ("event_serial", "page", "locus", "record", "record_unit_id", "field_id", "surface", "joint_tuple_id", "formal_formula_opaque", "FORMAL_VALUE", "terminal_status", "strict_control_prompt"))
        for new, old in zip(events, source_events)
    )
    checks["formal_card_layer_preserved"] = all(
        all(new[key] == old[key] for key in ("surface_examples", "occurrences", "pages", "formal_formula_opaque", "FORMAL_VALUE", "strict_control_prompt"))
        for new, old in zip(cards, source_cards)
    )

    decision_by_id = {row["exact_joint_tuple_id"]: row for row in decisions}
    target_ids = set(decision_by_id)
    source_target_events = [row for row in source_events if row["joint_tuple_id"] in target_ids]
    checks["all_85_source_occurrences_audited"] = {row["event_serial"] for row in source_target_events} == {row["event_serial"] for row in audit}
    checks["target_occurrence_sum_85"] = sum(int(row["occurrences_checked"]) for row in decisions) == 85
    source_counts = Counter(row["joint_tuple_id"] for row in source_target_events)
    checks["per_card_occurrence_counts_match"] = all(source_counts[row["exact_joint_tuple_id"]] == int(row["occurrences_checked"]) for row in decisions)

    checks["one_default_per_exact_target_id"] = all(
        {row["ATOMIC_OR_WHOLE_CARD_MNEMONIC"] for row in events if row["joint_tuple_id"] == exact_id}
        == {decision["V60_R3_selected_technical_default"]}
        for exact_id, decision in decision_by_id.items()
    )
    checks["audit_defaults_match_decisions"] = all(
        row["V60_R3_selected_technical_default"] == decision_by_id[row["exact_joint_tuple_id"]]["V60_R3_selected_technical_default"]
        for row in audit
    )
    checks["all_eleven_concrete_not_unknown"] = all(
        row["V60_R3_selected_technical_default"] not in {"UNKNOWN", "UNKNOWN_EXEMPLAR"} for row in decisions
    )
    checks["two_distinct_concrete_rivals_each"] = all(
        row["rival_1"] not in {"", "NONE", "UNKNOWN", "UNKNOWN_EXEMPLAR"}
        and row["rival_2"] not in {"", "NONE", "UNKNOWN", "UNKNOWN_EXEMPLAR"}
        and len({row["V60_R3_selected_technical_default"], row["rival_1"], row["rival_2"]}) == 3
        for row in decisions
    )
    checks["source_class_state_effect_contradiction_complete"] = all(
        row["source_class"].strip() and row["process_state_effect"].strip() and row["strongest_contradiction"].strip()
        for row in decisions
    )
    checks["confidence_bounded"] = all(0.0 < float(row["confidence"]) < 1.0 for row in decisions)

    target_card_rows = [row for row in cards if row["joint_tuple_id"] in target_ids]
    non_target_card_rows = [row for row in cards if row["joint_tuple_id"] not in target_ids]
    target_event_rows = [row for row in events if row["joint_tuple_id"] in target_ids]
    non_target_event_rows = [row for row in events if row["joint_tuple_id"] not in target_ids]
    checks["target_partition_11_cards_85_events"] = (len(target_card_rows), len(target_event_rows)) == (11, 85)
    checks["non_target_unknown_exemplar_162_296"] = (
        len(non_target_card_rows) == 162
        and len(non_target_event_rows) == 296
        and all(row["ATOMIC_OR_WHOLE_CARD_MNEMONIC"] == "UNKNOWN_EXEMPLAR" for row in non_target_card_rows + non_target_event_rows)
    )
    checks["exact_id_binding_only"] = all(row["binding_basis"] == "EXACT_JOINT_TUPLE_ID_ONLY" for row in decisions + audit) and all(
        row["V60_R3_BINDING_BASIS"] == "EXACT_JOINT_TUPLE_ID_ONLY" for row in cards + events
    )
    checks["component_inheritance_forbidden"] = all(row["V60_R3_COMPONENT_INHERITANCE"] == "FORBIDDEN" for row in cards + events)
    checks["no_page_host_column"] = all("page_host" not in key.lower() for table in (decisions, audit, cards, events) for key in table[0])
    checks["physical_line_not_sentence"] = all(row["V60_R3_LINE_STATEMENT_STATUS"] == "PHYSICAL_LINE_NOT_SENTENCE" for row in events)
    checks["page_scope_exact"] = {row["page"] for row in events} == ALLOWED_PAGES
    checks["local_expansions_preserved_nonblank"] = all(row["LOCAL_IATROMEDICAL_EXPANSION"].strip() and row["NONMEDICAL_RIVAL"].strip() for row in cards + events + audit)

    terminal_by_card: dict[str, Counter[str]] = defaultdict(Counter)
    for row in target_event_rows:
        terminal_by_card[row["joint_tuple_id"]][row["terminal_status"]] += 1
    oke_id = next(row["exact_joint_tuple_id"] for row in decisions if row["card"] == "OKE")
    lche_id = next(row["exact_joint_tuple_id"] for row in decisions if row["card"] == "LCHE")
    checks["oke_lche_all_close_confounded"] = terminal_by_card[oke_id] == Counter({"TERMINAL": 8}) and terminal_by_card[lche_id] == Counter({"TERMINAL": 8})
    checks["close_confounded_explicit_in_source_class"] = all(
        "CLOSE_CONFOUNDED" in row["source_class"] for row in decisions if row["card"] in {"OKE", "LCHE"}
    )
    checks["old_mnemonics_match_canonical"] = all(
        row["V59_R1_PREVIOUS_MNEMONIC"] == old["ATOMIC_OR_WHOLE_CARD_MNEMONIC"] for row, old in zip(cards, source_cards)
    ) and all(row["V59_R1_PREVIOUS_MNEMONIC"] == old["ATOMIC_OR_WHOLE_CARD_MNEMONIC"] for row, old in zip(events, source_events))
    checks["all_occurrence_serial_lists_complete"] = all(
        len(row["event_serials_checked"].split(",")) == int(row["occurrences_checked"]) for row in decisions
    )

    failed = [name for name, passed in checks.items() if not passed]
    result = {
        "schema": "V60_R3_EXACT_CARD_TECHNICAL_MNEMONIC_REVISION_V1",
        "status": "PASS" if not failed else "FAIL",
        "counts": {
            "technical_card_decisions": len(decisions),
            "audited_target_occurrences": len(audit),
            "revised_dictionary_cards": len(cards),
            "revised_interlinear_events": len(events),
            "target_cards": len(target_card_rows),
            "target_events": len(target_event_rows),
            "unknown_exemplar_cards": len(non_target_card_rows),
            "unknown_exemplar_events": len(non_target_event_rows),
            "close_confounded_target_events": terminal_by_card[oke_id]["TERMINAL"] + terminal_by_card[lche_id]["TERMINAL"],
        },
        "per_card_occurrences": {row["card"]: int(row["occurrences_checked"]) for row in decisions},
        "checks": checks,
        "failed_checks": failed,
        "source_sha256": {"V59_R1_cards": sha256(SOURCE_CARDS), "V59_R1_events": sha256(SOURCE_EVENTS)},
        "output_sha256": {name: sha256(path) for name, path in FILES.items()},
    }
    VALIDATION.write_text(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if failed:
        raise SystemExit("FAIL: " + ", ".join(failed))
    print("PASS validation")
    print(json.dumps(result["counts"], ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()
