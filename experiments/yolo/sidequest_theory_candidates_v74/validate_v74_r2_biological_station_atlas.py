#!/usr/bin/env python3
"""Validate completeness, frozen lineage, local ownership, and ceilings of V74 R2."""

from __future__ import annotations

import csv
import hashlib
import json
import re
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
V69 = ROOT / "experiments/yolo/sidequest_theory_candidates_v69"
V70 = ROOT / "experiments/yolo/sidequest_theory_candidates_v70"
V71 = ROOT / "experiments/yolo/sidequest_theory_candidates_v71"
V72 = ROOT / "experiments/yolo/sidequest_theory_candidates_v72"
OUT = ROOT / "experiments/yolo/sidequest_theory_candidates_v74"

SOURCE_EVENTS = V69 / "V69_R4_FINAL_381_PROSE_EVENT_INTERLINEAR.tsv"
SOURCE_FIELDS = V69 / "V69_R4_FINAL_135_FIELD_EDITION.tsv"
SOURCE_CARDS = V69 / "V69_R4_FINAL_173_CARD_DICTIONARY.tsv"
SOURCE_IMAGES = V70 / "V70_SELECTED_TEN_PAGE_IMAGE_REVISION.tsv"
SOURCE_OWNERS = V71 / "V71_SELECTED_OWNER_LEDGER.tsv"
SOURCE_STATEMENTS = V72 / "V72_SELECTED_116_STATEMENTS.tsv"

EVENTS = OUT / "V74_R2_281_BIO_EVENTS.tsv"
FIELDS = OUT / "V74_R2_115_BIO_FIELDS.tsv"
STATEMENTS = OUT / "V74_R2_97_BIO_STATEMENTS.tsv"
RECORDS = OUT / "V74_R2_SIX_CONTINUOUS_RECORDS.tsv"
NOUNS = OUT / "V74_R2_UNSUPPORTED_NOUNS.tsv"
REPORT = OUT / "V74_R2_BIOLOGICAL_STATION_ATLAS_REPORT.md"
BUILDER = OUT / "build_v74_r2_biological_station_atlas.py"
VALIDATION = OUT / "V74_R2_VALIDATION.json"

EXPECTED_RECORD_COUNTS = {"B1": 66, "B2": 62, "B3": 86, "B4": 47, "B5": 11, "B6": 9}
EXPECTED_BREAK_EVENTS = ["189", "198", "203", "212", "239", "248", "264", "291", "338", "356"]
EXPECTED_BREAK_STATEMENTS = {"B2-S012", "B3-S016", "B3-S026", "B4-S015"}
VALID_OWNER_STATUSES = {"DIRECT_VISIBLE", "INHERITED_VISIBLE", "PAGE_OWNER_ONLY", "UNRESOLVED"}
VALID_NOUN_CLASSES = {
    "UNPICTURED_SUBSTANCE_OR_PREPARATION",
    "UNPICTURED_IMPLEMENT",
    "LOCAL_VISIBLE_FORM_FUNCTION_UNCERTAIN",
    "VISIBLE_FIGURE_THERAPEUTIC_STATUS_UNCERTAIN",
    "UNPICTURED_PARAMETER_OR_STATE",
    "UNMARKED_OPERATION_OR_DIRECTION",
}


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def checked(condition: bool, label: str, checks: dict[str, bool]) -> None:
    checks[label] = bool(condition)


def ordered_unique(values: list[str]) -> list[str]:
    return list(dict.fromkeys(values))


def source_exemplar(source: str) -> str:
    match = re.search(r"\[EXEMPLAR:[^:]+:(.*?)\]", source)
    if not match:
        raise ValueError(f"missing frozen V69 exemplar: {source}")
    text = re.sub(r"\s+", " ", match.group(1)).strip()
    text = text[0].upper() + text[1:]
    return text if text.endswith((".", "!", "?")) else text + "."


def render_sequence(rows: list[dict[str, str]], with_ids: bool) -> str:
    out: list[str] = []
    previous = None
    for row in rows:
        owner = row["local_image_owner"]
        label = row["local_owner_label"]
        if owner != previous:
            if previous is None:
                out.append(f"[[LOKALER BESITZER: {label}]]")
            else:
                previous_label = next(r["local_owner_label"] for r in rows if r["local_image_owner"] == previous)
                out.append(
                    f"[[STATIONSWECHSEL: {previous_label} -> {label}; "
                    "STOFF, ZIEL UND RICHTUNG WERDEN NICHT VERERBT]]"
                )
            previous = owner
        prefix = f"E{row['event_serial']}=" if with_ids else ""
        out.append(prefix + row["concrete_german_meaning_in_context"])
    return " ".join(out)


def main() -> None:
    source_events = [r for r in read_tsv(SOURCE_EVENTS) if 101 <= int(r["event_serial"]) <= 381]
    source_fields = [r for r in read_tsv(SOURCE_FIELDS) if 21 <= int(r["field_id"][1:]) <= 135]
    source_cards = {r["joint_tuple_id"]: r for r in read_tsv(SOURCE_CARDS)}
    source_images = {
        r["page"]: r for r in read_tsv(SOURCE_IMAGES) if r["section"] == "BIOLOGICAL"
    }
    source_owners = {
        r["unit_id"]: r for r in read_tsv(SOURCE_OWNERS)
        if r["unit_kind"] == "PROSE_FIELD" and r["section"] == "BIOLOGICAL"
    }
    source_statements = [r for r in read_tsv(SOURCE_STATEMENTS) if r["record_unit_id"].startswith("B")]

    events = read_tsv(EVENTS)
    fields = read_tsv(FIELDS)
    statements = read_tsv(STATEMENTS)
    records = read_tsv(RECORDS)
    nouns = read_tsv(NOUNS)
    report = REPORT.read_text(encoding="utf-8")

    checks: dict[str, bool] = {}
    checked(len(events) == 281, "exactly_281_event_rows", checks)
    checked(len(fields) == 115, "exactly_115_field_rows", checks)
    checked(len(statements) == 97, "exactly_97_statement_rows", checks)
    checked(len(records) == 6, "exactly_6_record_rows", checks)
    checked(len(nouns) == 32, "exactly_32_unsupported_noun_types", checks)
    checked([r["event_serial"] for r in events] == [str(i) for i in range(101, 382)], "event_serials_101_381_exact_order", checks)
    checked([r["field_id"] for r in fields] == [f"F{i:03d}" for i in range(21, 136)], "field_ids_f021_f135_exact_order", checks)
    checked([r["statement_id"] for r in statements] == [r["statement_id"] for r in source_statements], "statement_ids_match_v72_central_order", checks)
    checked([r["record_unit_id"] for r in records] == [f"B{i}" for i in range(1, 7)], "record_ids_b1_b6_exact_order", checks)
    checked({r["page"] for r in events} == {"f81v", "f82r", "f83r"}, "only_fixed_three_biological_pages", checks)
    checked(Counter(r["record_unit_id"] for r in events) == Counter(EXPECTED_RECORD_COUNTS), "record_event_counts_exact", checks)
    checked(set(source_images) == {"f81v", "f82r", "f83r"}, "v70_image_guards_exact_three_pages", checks)

    source_by_serial = {r["event_serial"]: r for r in source_events}
    literal_exact = True
    owner_exact = True
    image_exact = True
    frozen_context_exact = True
    for row in events:
        src = source_by_serial[row["event_serial"]]
        literal = row["exact_literal_card_formal_exemplar_layer"]
        owner = source_owners[row["field_id"]]
        if any(row[k] != src[k] for k in ("record_unit_id", "page", "locus", "field_id", "statement_id", "joint_tuple_id", "terminal_status")):
            literal_exact = False
        if f"[OPAQUE_CARD:{src['joint_tuple_id']}]" not in literal:
            literal_exact = False
        mnemonic = src["selected_exact_mnemonic"]
        prompt = src["strict_formal_prompt"]
        if (mnemonic != "UNKNOWN") != (f"[CARD:{mnemonic}]" in literal):
            literal_exact = False
        if mnemonic == "UNKNOWN" and "[CARD:" in literal:
            literal_exact = False
        if (prompt != "NONE") != (f"[FORMAL:{prompt}]" in literal):
            literal_exact = False
        if prompt == "NONE" and "[FORMAL:" in literal:
            literal_exact = False
        if "[CONTEXT_EXEMPLAR:" not in literal:
            literal_exact = False
        if (src["terminal_status"] == "TERMINAL") != ("[CLOSE]" in literal):
            literal_exact = False
        if source_cards[src["joint_tuple_id"]]["ATOMIC_OR_WHOLE_CARD_MNEMONIC"] != mnemonic:
            literal_exact = False
        if row["local_image_owner"] != owner["selected_visible_owner"] or f"[OWNER:{owner['selected_visible_owner']}]" not in literal:
            owner_exact = False
        if row["owner_status"] != owner["owner_status"] or row["owner_confidence"] != owner["confidence"]:
            owner_exact = False
        if row["owner_status"] not in VALID_OWNER_STATUSES:
            owner_exact = False
        if row["image_geometry_guard"] != source_images[row["page"]]["selected_geometry"]:
            image_exact = False
        if row["concrete_german_meaning_in_context"] != source_exemplar(src["iatromedical_source_segment"]):
            frozen_context_exact = False
    checked(literal_exact, "exact_v69_opaque_card_mnemonic_formal_and_close_layers", checks)
    checked(owner_exact, "v71_local_owners_status_and_confidence_exact", checks)
    checked(image_exact, "v70_page_geometry_guard_exact", checks)
    checked(frozen_context_exact, "all_context_readings_reuse_frozen_v69_occurrence_exemplars", checks)

    checked(all(r["concrete_german_meaning_in_context"].strip().endswith((".", "!", "?")) for r in events), "all_events_have_concrete_punctuated_german_reading", checks)
    checked(all(0.18 <= float(r["meaning_in_context_confidence"]) <= 0.46 for r in events), "event_context_confidences_bounded", checks)
    checked(all(r["strongest_bathhouse_technical_or_formal_rival"].strip() for r in events), "all_events_have_technical_or_formal_rival", checks)
    checked(all(r["strongest_contradiction"].strip() for r in events), "all_events_have_contradiction", checks)
    checked(all(r["unsupported_nouns"].strip() for r in events), "all_events_have_noun_audit", checks)
    checked(all(r["carry_policy"] == "LOCAL_OWNER_ONLY; NEVER_CARRY_SUBSTANCE_TARGET_OR_DIRECTION_ACROSS_OWNER_BREAK" for r in events), "local_owner_carry_policy_on_every_event", checks)
    checked(all(r["semantic_ceiling"] == "OCCURRENCE_BALNEOLOGICAL_EXEMPLAR_NOT_CARD_STEM_SOUND_LANGUAGE_OR_MEDICAL_FACT" for r in events), "event_semantic_ceiling_exact", checks)

    by_field: dict[str, list[dict[str, str]]] = defaultdict(list)
    by_statement: dict[str, list[dict[str, str]]] = defaultdict(list)
    by_record: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in events:
        by_field[row["field_id"]].append(row)
        by_statement[row["statement_id"]].append(row)
        by_record[row["record_unit_id"]].append(row)

    # The break is derived independently from V71 owner identity, not trusted from output.
    expected_breaks: list[str] = []
    expected_break_labels: list[str] = []
    previous_by_record: dict[str, str] = {}
    break_marking_exact = True
    for row in events:
        owner = source_owners[row["field_id"]]["selected_visible_owner"]
        previous = previous_by_record.get(row["record_unit_id"])
        if previous is None:
            expected = "RECORD_START__RESET_ALL_LOCAL_STATE"
        elif owner != previous:
            expected = "BREAK_VISIBLE_GAP__RESET_SUBSTANCE_TARGET_DIRECTION"
            expected_breaks.append(row["event_serial"])
            expected_break_labels.append(row["statement_id"])
        else:
            expected = "SAME_LOCAL_OWNER__NO_NEW_GEOMETRIC_CLAIM"
        if row["owner_break_before"] != expected:
            break_marking_exact = False
        previous_by_record[row["record_unit_id"]] = owner
    checked(break_marking_exact, "all_owner_breaks_derived_exactly_from_v71", checks)
    checked(expected_breaks == EXPECTED_BREAK_EVENTS, "ten_expected_record_internal_break_events", checks)

    source_field_by_id = {r["field_id"]: r for r in source_fields}
    field_exact = all(
        r["event_serials"] == source_field_by_id[r["field_id"]]["event_serials"]
        and r["event_serials"] == "|".join(e["event_serial"] for e in by_field[r["field_id"]])
        and r["record_unit_id"] == source_field_by_id[r["field_id"]]["record_unit_id"]
        and r["page"] == source_field_by_id[r["field_id"]]["page"]
        and r["locus"] == source_field_by_id[r["field_id"]]["locus"]
        and r["statement_id"] == source_field_by_id[r["field_id"]]["statement_id"]
        and r["v69_template"] == source_field_by_id[r["field_id"]]["primary_template"]
        and r["parse_status"] == source_field_by_id[r["field_id"]]["parse_status"]
        and r["local_image_owner"] == source_owners[r["field_id"]]["selected_visible_owner"]
        for r in fields
    )
    checked(field_exact, "field_membership_metadata_and_owner_exact_v69_v71", checks)

    source_statement_by_id = {r["statement_id"]: r for r in source_statements}
    statement_exact = all(
        r["constituent_fields"] == source_statement_by_id[r["statement_id"]]["constituent_fields"]
        and r["event_serials"] == source_statement_by_id[r["statement_id"]]["event_serials"]
        and r["event_serials"] == "|".join(e["event_serial"] for e in by_statement[r["statement_id"]])
        and r["v72_selected_technical_statement"] == source_statement_by_id[r["statement_id"]]["selected_concrete_paraphrase"]
        and r["line_crossing"] == source_statement_by_id[r["statement_id"]]["line_crossing"]
        for r in statements
    )
    checked(statement_exact, "statement_membership_and_frozen_v72_layer_exact", checks)
    actual_break_statements = {r["statement_id"] for r in statements if r["contains_visible_owner_break"] == "YES"}
    checked(actual_break_statements == EXPECTED_BREAK_STATEMENTS, "four_statement_internal_visible_breaks_exact", checks)
    checked(set(expected_break_labels).issuperset(EXPECTED_BREAK_STATEMENTS), "statement_breaks_supported_by_event_transitions", checks)

    all_record_event_ids = [serial for r in records for serial in re.findall(r"E(\d+)=", r["event_alignment"])]
    checked(all_record_event_ids == [str(i) for i in range(101, 382)], "record_alignment_covers_each_event_once_in_order", checks)
    record_exact = True
    for r in records:
        members = by_record[r["record_unit_id"]]
        owner_sequence = ordered_unique([e["local_image_owner"] for e in members])
        breaks = [e["event_serial"] for e in members if e["owner_break_before"].startswith("BREAK_VISIBLE_GAP")]
        if r["event_serials"] != "|".join(e["event_serial"] for e in members):
            record_exact = False
        if r["field_ids"] != "|".join(ordered_unique([e["field_id"] for e in members])):
            record_exact = False
        if r["statement_ids"] != "|".join(ordered_unique([e["statement_id"] for e in members])):
            record_exact = False
        if r["local_owner_sequence"] != "|".join(owner_sequence):
            record_exact = False
        if r["owner_break_event_serials"] != ("|".join(breaks) if breaks else "NONE"):
            record_exact = False
        if r["continuous_event_bound_reading"] != render_sequence(members, with_ids=False):
            record_exact = False
        if r["event_alignment"] != render_sequence(members, with_ids=True):
            record_exact = False
        if not r["historical_station_article_structure"].strip() or not r["fluent_record_synopsis"].strip():
            record_exact = False
    checked(record_exact, "six_continuous_records_complete_owner_aware_and_event_bound", checks)

    noun_members: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in events:
        if row["unsupported_nouns"] != "NONE__ACTION_ONLY":
            for noun in row["unsupported_nouns"].split("|"):
                noun_members[noun].append(row)
    noun_table = {r["unsupported_noun"]: r for r in nouns}
    checked(set(noun_table) == set(noun_members), "unsupported_noun_inventory_complete", checks)
    noun_bindings_exact = True
    for noun, members in noun_members.items():
        row = noun_table[noun]
        if row["support_class"] not in VALID_NOUN_CLASSES:
            noun_bindings_exact = False
        if row["event_count"] != str(len(members)):
            noun_bindings_exact = False
        if row["event_serials"] != "|".join(m["event_serial"] for m in members):
            noun_bindings_exact = False
        if row["records"] != "|".join(ordered_unique([m["record_unit_id"] for m in members])):
            noun_bindings_exact = False
        if row["pages"] != "|".join(ordered_unique([m["page"] for m in members])):
            noun_bindings_exact = False
        if row["owners"] != "|".join(ordered_unique([m["local_image_owner"] for m in members])):
            noun_bindings_exact = False
    checked(noun_bindings_exact, "unsupported_noun_bindings_and_classes_exact", checks)

    support_counts = Counter(r["v69_source_status"] for r in events)
    expected_support = Counter({
        "UNKNOWN_EXEMPLAR_WHOLE_CARD": 191,
        "EXACT_WORKING_MNEMONIC": 56,
        "STRICT_FORMAL_PROMPT_NO_WORD_VALUE": 29,
        "EXACT_MNEMONIC_AND_STRICT_FORMAL_PROMPT": 5,
    })
    checked(support_counts == expected_support, "v69_support_distribution_exact_90_supported_191_exemplar", checks)
    checked(sum(r["owner_status"] == "UNRESOLVED" for r in events) == 32, "exactly_32_unresolved_owner_events", checks)
    checked(len({r["local_image_owner"] for r in events}) == 16, "exactly_16_local_owner_ids", checks)

    semantic_text = "\n".join(
        [r["concrete_german_meaning_in_context"] for r in events]
        + [r["balneological_field_text"] for r in fields]
        + [r["balneological_statement_text"] for r in statements]
        + [r["fluent_record_synopsis"] + " " + r["continuous_event_bound_reading"] for r in records]
    )
    checked(not re.search(r"\b(PAGE_HOST|EVA|Lautwert|Stammwert|Morphem|Prefix|Suffix)\b", semantic_text, re.I), "no_sound_spelling_stem_or_component_inference", checks)
    checked(not any(r["page"].casefold().startswith("f84") for r in events), "f84_and_f84r_absent_from_data", checks)
    checked(all("surface" not in key.casefold() for key in events[0]), "no_surface_spelling_column", checks)

    checked(all(f"### B{i} —" in report for i in range(1, 7)), "report_contains_six_full_record_readings", checks)
    checked(all(report.count(f"`{sid}`") == 1 for sid in EXPECTED_BREAK_STATEMENTS), "report_lists_each_hard_statement_break_once", checks)
    checked(all(name in report for name in ("Morgan Library", "Biblissima/BnF", "Biblioteca Angelica", "Taccola")), "report_has_compact_historical_source_list", checks)
    checked("keine Entzifferung" in report and "f84 und f84r blieben versiegelt" in report, "report_states_ceiling_and_seal", checks)
    checked("kein seitenweiten Stoff" in report or "keinen seitenweiten Stoff" in report, "report_rejects_pagewide_substance", checks)

    artifacts = [EVENTS, FIELDS, STATEMENTS, RECORDS, NOUNS, REPORT, BUILDER, Path(__file__)]
    validation = {
        "status": "PASS" if all(checks.values()) else "FAIL",
        "checks": checks,
        "counts": {
            "events": len(events),
            "fields": len(fields),
            "statements": len(statements),
            "records": len(records),
            "pages": len({r["page"] for r in events}),
            "local_owner_ids": len({r["local_image_owner"] for r in events}),
            "record_internal_owner_breaks": len(expected_breaks),
            "statement_internal_owner_breaks": len(actual_break_statements),
            "unresolved_owner_events": sum(r["owner_status"] == "UNRESOLVED" for r in events),
            "unsupported_noun_types": len(nouns),
            "parser_or_mnemonic_supported_events": len(events) - support_counts["UNKNOWN_EXEMPLAR_WHOLE_CARD"],
            "pure_exemplar_events": support_counts["UNKNOWN_EXEMPLAR_WHOLE_CARD"],
            "support_distribution": dict(sorted(support_counts.items())),
        },
        "break_events": expected_breaks,
        "break_statements": sorted(actual_break_statements),
        "sealed": {"f84": True, "f84r": True},
        "sha256": {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in artifacts},
    }
    VALIDATION.write_text(json.dumps(validation, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(validation, ensure_ascii=False, indent=2))
    if validation["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
