#!/usr/bin/env python3
"""Validate V80 R2 completeness, layer separation, and frozen corrections."""

from __future__ import annotations

import csv
import json
import re
from collections import Counter
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]

DICT = HERE / "V80_R2_173_EXACT_CARD_DICTIONARY.tsv"
EVENTS = HERE / "V80_R2_381_PROSE_EVENT_INTERLINEAR.tsv"
FIELDS = HERE / "V80_R2_135_FIELD_EDITION.tsv"
STATEMENTS = HERE / "V80_R2_116_STATEMENT_EDITION.tsv"
ASTRO = HERE / "V80_R2_395_ASTRO_GROUP_EDITION.tsv"
UNIFIED = HERE / "V80_R2_776_UNIFIED_LEDGER.tsv"
MANUAL = HERE / "V80_R2_PERIOD_WORKSHOP_MANUAL.tsv"
CONTRADICTIONS = HERE / "V80_R2_CONTRADICTION_CONFIDENCE_LEDGER.tsv"
READABLE = HERE / "V80_R2_READABLE_TEN_PAGE_EDITION.md"
REPORT = HERE / "V80_R2_HISTORICAL_CANONICAL_THIRD_EDITION_REPORT.md"
RESULT = HERE / "V80_R2_RESULT.json"
OUT = HERE / "V80_R2_VALIDATION.json"

SOURCE_TRANSITIONS = ROOT / "experiments/yolo/sidequest_theory_candidates_v79/V79_SELECTED_19_LINE_TRANSITION_AUDIT.tsv"

ET_CARD = "dcda95c81a5460feb191"
PER_CARD = "b5fcea1eaed06b2f2291"
PARAM_CARD = "2f1c5e56e8f0ff459065"
RELATION_SLOT_CARD = "308e8ea2d5d190c498e8"
LEAD = "A_PRACTITIONER_THERAPEUTIC_IATROMATHEMATICAL_COMPENDIUM"
RIVAL = "B_NATURAL_ARTIFICIAL_CELESTIAL_IMAGE_ATLAS_MODELBOOK"


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh, delimiter="\t"))


def add(checks: list[dict[str, object]], name: str, ok: bool, detail: object) -> None:
    checks.append({"check": name, "pass": bool(ok), "detail": detail})


def split_ids(value: str) -> list[str]:
    return [] if value == "NONE" or not value else value.split("|")


def main() -> None:
    dictionary = read_tsv(DICT)
    events = read_tsv(EVENTS)
    fields = read_tsv(FIELDS)
    statements = read_tsv(STATEMENTS)
    astro = read_tsv(ASTRO)
    unified = read_tsv(UNIFIED)
    manual = read_tsv(MANUAL)
    contradictions = read_tsv(CONTRADICTIONS)
    source_transitions = read_tsv(SOURCE_TRANSITIONS)
    readable = READABLE.read_text(encoding="utf-8")
    report = REPORT.read_text(encoding="utf-8")
    result = json.loads(RESULT.read_text(encoding="utf-8"))
    checks: list[dict[str, object]] = []

    # Exact cardinalities and identities.
    add(checks, "173_unique_exact_cards", len(dictionary) == len({r["joint_tuple_id"] for r in dictionary}) == 173, len(dictionary))
    add(checks, "381_unique_prose_events", len(events) == len({r["event_id"] for r in events}) == 381, len(events))
    add(checks, "event_ids_are_E001_E381", [r["event_id"] for r in events] == [f"E{i:03d}" for i in range(1, 382)], [events[0]["event_id"], events[-1]["event_id"]])
    add(checks, "135_unique_fields", len(fields) == len({r["field_id"] for r in fields}) == 135, len(fields))
    add(checks, "116_unique_statements", len(statements) == len({r["statement_id"] for r in statements}) == 116, len(statements))
    add(checks, "395_unique_astro_groups", len(astro) == len({r["opaque_local_id"] for r in astro}) == 395, len(astro))
    add(checks, "142_astro_loci", len({(r["page"], r["locus"]) for r in astro}) == 142, len({(r["page"], r["locus"]) for r in astro}))
    add(checks, "776_unique_unified_groups", len(unified) == len({r["unified_id"] for r in unified}) == 776, len(unified))
    add(checks, "776_contradiction_rows", len(contradictions) == 776 and [r["unified_id"] for r in contradictions] == [r["unified_id"] for r in unified], len(contradictions))

    pages = {r["page"] for r in unified}
    expected_pages = {"f10r", "f11r", "f55v", "f56r", "f81v", "f82r", "f83r", "f67r2", "f68r1", "f69v"}
    units = {r["unit_id"] for r in unified}
    expected_units = {"H1", "H2", "H3", "H4", "H5", "B1", "B2", "B3", "B4", "B5", "B6", "A1", "A2", "A3"}
    add(checks, "fixed_exact_ten_pages", pages == expected_pages, sorted(pages))
    add(checks, "exact_fourteen_units", units == expected_units, sorted(units))

    # Dictionary and event frequency agreement.
    card_counts = Counter(r["joint_tuple_id"] for r in events)
    dict_counts = {r["joint_tuple_id"]: int(r["visible_occurrences"]) for r in dictionary}
    add(checks, "dictionary_occurrences_sum_381", sum(dict_counts.values()) == 381, sum(dict_counts.values()))
    add(checks, "dictionary_event_frequencies_exact", dict_counts == dict(card_counts), "MATCH" if dict_counts == dict(card_counts) else "MISMATCH")
    class_counts = Counter(r["autonomous_operational_class"] for r in dictionary)
    add(
        checks,
        "dictionary_exact_operational_partition",
        class_counts == Counter({
            "EXEMPLAR_VALUE_UNKNOWN": 169,
            "FORMAL_PARAMETER_CHANNEL": 1,
            "FORMAL_RELATION_SLOT_CHANNEL": 1,
            "FORMAL_LINK_OR_SLOT": 1,
            "FORMAL_RELATION_OR_ENTRY_MARK_WITH_ENTRY_BIAS": 1,
        }),
        dict(class_counts),
    )
    add(checks, "zero_portable_words", all(r["portable_word_status"].startswith("NO__") for r in dictionary), Counter(r["portable_word_status"] for r in dictionary))
    gloss_cards = {r["joint_tuple_id"] for r in dictionary if r["optional_master_gloss"] != "NONE"}
    add(checks, "only_ET_PER_optional_master_glosses", gloss_cards == {ET_CARD, PER_CARD}, sorted(gloss_cards))
    source_entries = {r["joint_tuple_id"]: r["exact_1414_category_if_any"] for r in dictionary if r["exact_1414_category_if_any"] != "NONE"}
    add(checks, "exact_Fi1_categories_only", source_entries == {ET_CARD: "et", PER_CARD: "per"}, source_entries)
    dict_by_card = {r["joint_tuple_id"]: r for r in dictionary}
    add(
        checks,
        "Fi1_attestation_detail_preserved",
        all("FLORENCE_FI1_1414" in dict_by_card[card]["historical_attestation_detail"] for card in [ET_CARD, PER_CARD]),
        {card: dict_by_card[card]["historical_attestation_detail"] for card in [ET_CARD, PER_CARD]},
    )
    formal_nonwords = {r["joint_tuple_id"] for r in dictionary if r["formal_channel_status"] == "FROZEN_FORMAL_NONWORD_CHANNEL"}
    add(checks, "exact_two_frozen_nonword_cards", formal_nonwords == {PARAM_CARD, RELATION_SLOT_CARD}, sorted(formal_nonwords))

    # Autonomous/event layer separation.
    allowed_event_tokens = {
        "[EXEMPLAR_VALUE_UNKNOWN]",
        "[FORMAL:VORGABEPARAMETER; KEIN_WORT]",
        "[FORMAL:LOKALEN_RELATIONSSLOT_SETZEN; KEIN_WORT]",
        "[FORMAL_LINK]",
        "[FORMAL_RELATION_OR_ENTRY]",
    }
    add(checks, "only_five_autonomous_prose_tokens", {r["autonomous_readback_token"] for r in events} == allowed_event_tokens, sorted({r["autonomous_readback_token"] for r in events}))
    add(checks, "no_ET_PER_text_in_autonomous_tokens", all("ET?" not in r["autonomous_readback_token"] and "PER?" not in r["autonomous_readback_token"] for r in events), "PASS")
    add(checks, "all_prose_content_occurrence_bracketed", all(r["occurrence_bound_exemplar"].startswith("[EXEMPLAR:") for r in events), sum(r["occurrence_bound_exemplar"].startswith("[EXEMPLAR:") for r in events))
    add(
        checks,
        "ET_PER_occurrence_exemplars_semantically_neutralized",
        all("formalen Linkstelle" in r["occurrence_bound_exemplar"] for r in events if r["joint_tuple_id"] == ET_CARD)
        and all(
            "lokale Relation oder Eintragsfunktion" in r["occurrence_bound_exemplar"]
            for r in events if r["joint_tuple_id"] == PER_CARD and r["event_id"] != "E180"
        ),
        {"ET": sum(r["joint_tuple_id"] == ET_CARD for r in events), "PER": sum(r["joint_tuple_id"] == PER_CARD for r in events)},
    )
    add(checks, "all_fields_content_occurrence_bracketed", all(r["occurrence_bound_readable_field"].startswith("[EXEMPLAR:") for r in fields), len(fields))
    add(checks, "all_statements_content_occurrence_bracketed", all(r["occurrence_bound_readable_statement"].startswith("[EXEMPLAR:") for r in statements), len(statements))
    add(checks, "all_astro_content_occurrence_bracketed", all(r["occurrence_bound_exemplar_label"].startswith("[EXEMPLAR:") for r in astro), len(astro))

    event_ids = [r["event_id"] for r in events]
    field_event_ids = [event_id for row in fields for event_id in split_ids(row["visible_event_ids"])]
    statement_event_ids = [event_id for row in statements for event_id in split_ids(row["visible_event_ids"])]
    add(checks, "fields_partition_381_events_once", Counter(field_event_ids) == Counter(event_ids), len(field_event_ids))
    add(checks, "statements_partition_381_events_once", Counter(statement_event_ids) == Counter(event_ids), len(statement_event_ids))
    add(checks, "field_source_counts_380", sum(int(r["source_token_count"]) for r in fields) == 380, sum(int(r["source_token_count"]) for r in fields))
    add(checks, "statement_source_counts_380", sum(int(r["source_token_count"]) for r in statements) == 380, sum(int(r["source_token_count"]) for r in statements))

    by_event = {r["event_id"]: r for r in events}
    e180, e181 = by_event["E180"], by_event["E181"]
    add(
        checks,
        "E180_E181_exact_local_read_once",
        e180["joint_tuple_id"] == e181["joint_tuple_id"] == PER_CARD
        and e180["statement_id"] == e181["statement_id"]
        and e180["image_owner_id"] == e181["image_owner_id"]
        and e180["physical_locus"] != e181["physical_locus"]
        and e180["source_token_count"] == "0" and e181["source_token_count"] == "1",
        {"E180": e180["read_once_status"], "E181": e181["read_once_status"]},
    )
    event_gloss_counts = Counter(
        "ET" if r["joint_tuple_id"] == ET_CARD else "PER"
        for r in events if not r["optional_master_gloss"].startswith("NONE")
    )
    add(
        checks,
        "optional_master_glosses_count_source_tokens_not_visible_copy",
        event_gloss_counts == Counter({"ET": 19, "PER": 8})
        and e180["optional_master_gloss"].startswith("NONE")
        and e181["optional_master_gloss"].startswith("PER?"),
        dict(event_gloss_counts),
    )
    source_tps = [(r["line_final_event"], r["line_initial_event"]) for r in source_transitions if r["classification"] == "TP"]
    add(checks, "central_19_transition_panel_one_positive", len(source_transitions) == 19 and source_tps == [("E180", "E181")], {"n": len(source_transitions), "tp": source_tps})
    add(checks, "prose_source_tokens_380", sum(int(r["source_token_count"]) for r in events) == 380, sum(int(r["source_token_count"]) for r in events))
    add(checks, "unified_source_positions_775", sum(int(r["source_token_count"]) for r in unified) == 775, sum(int(r["source_token_count"]) for r in unified))

    reset_events = [r["event_id"] for r in events if r["visible_owner_reset"].startswith("YES")]
    expected_resets = ["E189", "E198", "E203", "E212", "E239", "E248", "E264", "E291", "E338", "E356"]
    add(checks, "all_ten_Bio_owner_resets", reset_events == expected_resets, reset_events)

    # Astro namespace and no-order/no-join guards.
    namespaces = {r["local_namespace"] for r in astro}
    add(checks, "eleven_frozen_local_astro_namespaces", len(namespaces) == 11, sorted(namespaces))
    add(checks, "all_astro_no_authorial_order_or_cross_locus_join", all(r["order_and_join_status"].startswith("NO_AUTHORIAL_ORDER_OR_CROSS_LOCUS_JOIN") for r in astro), len(astro))
    add(checks, "no_f68_f69_key", all(r["f68_f69_mapping"].startswith("NONE") for r in astro), Counter(r["f68_f69_mapping"] for r in astro))
    add(checks, "no_prose_card_import_to_astro", all(r["prose_card_import"] == "NONE" for r in astro), Counter(r["prose_card_import"] for r in astro))

    # Manual must be formal-first and explicit about memory versus derivation.
    add(checks, "sixteen_workshop_rules", len(manual) == 16 and [int(r["rule_order"]) for r in manual] == list(range(1, 17)), len(manual))
    manual_by_n = {int(r["rule_order"]): r for r in manual}
    add(checks, "manual_ET_row_formal_first", manual_by_n[8]["operation"] == "EMIT_FORMAL_LINK" and manual_by_n[8]["forward_autonomous_output"] == "[FORMAL_LINK]" and manual_by_n[8]["optional_master_gloss"].startswith("ET?"), manual_by_n[8])
    add(checks, "manual_PER_row_formal_first", manual_by_n[9]["operation"] == "EMIT_FORMAL_RELATION_OR_ENTRY" and manual_by_n[9]["forward_autonomous_output"] == "[FORMAL_RELATION_OR_ENTRY]" and manual_by_n[9]["optional_master_gloss"].startswith("PER?"), manual_by_n[9])
    add(checks, "manual_read_once_owner_reset_guard_explicit", "no visible owner reset" in manual_by_n[6]["condition"], manual_by_n[6]["condition"])
    add(checks, "manual_every_rule_memorize_derive_master_explicit", all(r["apprentice_memorizes"] and r["apprentice_derives"] and r["master_exemplar_only"] for r in manual), len(manual))

    # Readable/report coverage and global historical model discipline.
    page_headings = re.findall(r"^### (f\S+)", readable, flags=re.MULTILINE)
    record_headings = re.findall(r"^#### ([HB]\d) ", readable, flags=re.MULTILINE)
    locus_lines = re.findall(r"^- `f(?:67r2|68r1|69v)\.\d+`", readable, flags=re.MULTILINE)
    add(checks, "readable_exact_ten_page_headings", page_headings == ["f10r", "f11r", "f55v", "f56r", "f81v", "f82r", "f83r", "f67r2", "f68r1", "f69v"], page_headings)
    add(checks, "readable_all_eleven_records", record_headings == ["H1", "H2", "H3", "H4", "H5", "B1", "B2", "B3", "B4", "B5", "B6"], record_headings)
    add(checks, "readable_B2_62_visible_61_source", "#### B2 — 62 sichtbare Ereignisse / 61 Quellpositionen" in readable, "PASS")
    add(checks, "readable_all_142_astro_loci", len(locus_lines) == 142, len(locus_lines))
    add(checks, "readable_no_affirmative_kustode", "[KUSTODE:" not in readable and "Standard-Catchword bestätigt" not in readable, "PASS")
    add(checks, "report_exact_global_lead_and_rival", result["leading_historical_purpose"] == LEAD and result["single_global_rival"] == RIVAL and result["purpose_score"] == "236:235__NEAR_TIE", {"lead": result["leading_historical_purpose"], "rival": result["single_global_rival"]})
    add(checks, "report_states_memorized_derived_master_layers", all(text in report for text in ["Memorisiert bzw. konsultiert", "Aus der sichtbaren Instanz abgeleitet", "Nur im Masterexemplar"]), "PASS")
    add(checks, "report_has_all_twelve_frozen_sources", all(f"- S{i:02d}:" in report for i in range(1, 13)), "PASS")
    add(checks, "report_exact_eleven_astro_namespace_statement", "elf im ausgewählten Gruppenledger belegte lokale Namespaces" in report, "PASS")

    # Frozen scope/no-new-material gate.
    add(checks, "result_no_new_meaning_source_or_page", result["new_meanings"] == result["new_sources"] == result["new_pages"] == 0, {k: result[k] for k in ["new_meanings", "new_sources", "new_pages"]})
    add(checks, "result_zero_autonomous_words", result["autonomously_established_words"] == 0, result["autonomously_established_words"])
    add(checks, "only_central_V69_V73_V79_inputs", all("sidequest_theory_candidates_v80" not in path and re.search(r"sidequest_theory_candidates_v(?:69|7[3-9])", path) for path in result["inputs"]), result["inputs"])
    add(checks, "sealed_pages_not_input", all("f84" not in path.lower() for path in result["inputs"]), result["inputs"])
    add(checks, "result_counts_exact", all([
        result["exact_card_types"] == 173,
        result["prose_visible_events"] == 381,
        result["fields"] == 135,
        result["statements"] == 116,
        result["astro_groups"] == 395,
        result["unified_visible_groups"] == 776,
        result["unified_source_positions"] == 775,
    ]), {key: result[key] for key in ["exact_card_types", "prose_visible_events", "fields", "statements", "astro_groups", "unified_visible_groups", "unified_source_positions"]})

    status = "PASS" if all(row["pass"] for row in checks) else "FAIL"
    payload = {
        "experiment": "V80_R2_HISTORICAL_CANONICAL_THIRD_EDITION",
        "status": status,
        "checks_passed": sum(row["pass"] for row in checks),
        "checks_total": len(checks),
        "counts": {
            "cards": len(dictionary), "events": len(events), "fields": len(fields),
            "statements": len(statements), "astro_groups": len(astro),
            "unified": len(unified), "contradictions": len(contradictions),
        },
        "checks": checks,
    }
    OUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if status != "PASS":
        raise SystemExit("FAIL: " + ", ".join(row["check"] for row in checks if not row["pass"]))
    print(f"PASS: {len(checks)}/{len(checks)} checks")


if __name__ == "__main__":
    main()
