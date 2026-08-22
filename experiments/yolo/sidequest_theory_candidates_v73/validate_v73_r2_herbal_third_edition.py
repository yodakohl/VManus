#!/usr/bin/env python3
"""Validate completeness and semantic ceilings of the V73 R2 Herbal edition."""

from __future__ import annotations

import csv
import hashlib
import json
import re
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
V69 = ROOT / "experiments/yolo/sidequest_theory_candidates_v69"
V71 = ROOT / "experiments/yolo/sidequest_theory_candidates_v71"
V72 = ROOT / "experiments/yolo/sidequest_theory_candidates_v72"
OUT = ROOT / "experiments/yolo/sidequest_theory_candidates_v73"

SOURCE_EVENTS = V69 / "V69_R4_FINAL_381_PROSE_EVENT_INTERLINEAR.tsv"
SOURCE_FIELDS = V69 / "V69_R4_FINAL_135_FIELD_EDITION.tsv"
SOURCE_OWNERS = V71 / "V71_SELECTED_OWNER_LEDGER.tsv"
SOURCE_STATEMENTS = V72 / "V72_SELECTED_116_STATEMENTS.tsv"

EVENTS = OUT / "V73_R2_100_HERBAL_EVENTS.tsv"
FIELDS = OUT / "V73_R2_20_HERBAL_FIELDS.tsv"
STATEMENTS = OUT / "V73_R2_19_HERBAL_STATEMENTS.tsv"
ARTICLES = OUT / "V73_R2_FIVE_HERBAL_ARTICLES.tsv"
NOUNS = OUT / "V73_R2_UNSUPPORTED_NOUNS.tsv"
REPORT = OUT / "V73_R2_HERBAL_THIRD_EDITION_REPORT.md"
BUILDER = OUT / "build_v73_r2_herbal_third_edition.py"
VALIDATION = OUT / "V73_R2_VALIDATION.json"


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def checked(condition: bool, label: str, checks: dict[str, bool]) -> None:
    checks[label] = bool(condition)


def ordered_unique(items: list[str]) -> list[str]:
    return list(dict.fromkeys(items))


def main() -> None:
    source_events = [row for row in read_tsv(SOURCE_EVENTS) if int(row["event_serial"]) <= 100]
    source_fields = [
        row for row in read_tsv(SOURCE_FIELDS)
        if row["field_id"].startswith("F") and int(row["field_id"][1:]) <= 20
    ]
    source_owners = {
        row["unit_id"]: row for row in read_tsv(SOURCE_OWNERS)
        if row["unit_kind"] == "PROSE_FIELD" and row["section"] == "HERBAL"
    }
    source_statements = [
        row for row in read_tsv(SOURCE_STATEMENTS)
        if row["record_unit_id"].startswith("H")
    ]
    events = read_tsv(EVENTS)
    fields = read_tsv(FIELDS)
    statements = read_tsv(STATEMENTS)
    articles = read_tsv(ARTICLES)
    nouns = read_tsv(NOUNS)
    report = REPORT.read_text(encoding="utf-8")

    checks: dict[str, bool] = {}
    checked(len(events) == 100, "exactly_100_event_rows", checks)
    checked(len(fields) == 20, "exactly_20_field_rows", checks)
    checked(len(statements) == 19, "exactly_19_statement_rows", checks)
    checked(len(articles) == 5, "exactly_5_article_rows", checks)
    checked([row["event_serial"] for row in events] == [str(i) for i in range(1, 101)], "event_serials_exact_and_ordered", checks)
    checked([row["field_id"] for row in fields] == [f"F{i:03d}" for i in range(1, 21)], "field_ids_exact_and_ordered", checks)
    checked([row["statement_id"] for row in statements] == [row["statement_id"] for row in source_statements], "statement_ids_match_v72_central", checks)
    checked([row["record_unit_id"] for row in articles] == ["H1", "H2", "H3", "H4", "H5"], "five_record_articles_exact", checks)
    checked({row["page"] for row in events} == {"f10r", "f11r", "f55v", "f56r"}, "only_four_fixed_herbal_pages", checks)
    checked(all(row["record_unit_id"] in {"H1", "H2", "H3", "H4", "H5"} for row in events), "only_five_herbal_records", checks)

    source_by_serial = {row["event_serial"]: row for row in source_events}
    literal_exact = True
    owner_exact = True
    for row in events:
        source = source_by_serial[row["event_serial"]]
        literal = row["exact_literal_card_formal_exemplar_layer"]
        if row["joint_tuple_id"] != source["joint_tuple_id"] or f"[OPAQUE_CARD:{source['joint_tuple_id']}]" not in literal:
            literal_exact = False
        expected_owner = source_owners[row["field_id"]]
        if row["whole_plant_owner"] != expected_owner["selected_visible_owner"]:
            owner_exact = False
        if row["owner_status"] != expected_owner["owner_status"] or row["owner_confidence"] != expected_owner["confidence"]:
            owner_exact = False
        if f"[OWNER:{expected_owner['selected_visible_owner']}]" not in literal:
            owner_exact = False
        mnemonic = source["selected_exact_mnemonic"]
        prompt = source["strict_formal_prompt"]
        if mnemonic != "UNKNOWN" and f"[CARD:{mnemonic}]" not in literal:
            literal_exact = False
        if mnemonic == "UNKNOWN" and re.search(r"\[CARD:[^\]]+\]", literal):
            literal_exact = False
        if prompt != "NONE" and f"[FORMAL:{prompt}]" not in literal:
            literal_exact = False
        if prompt == "NONE" and "[FORMAL:" in literal:
            literal_exact = False
        if "[CONTEXT_EXEMPLAR:" not in literal:
            literal_exact = False
        if (source["terminal_status"] == "TERMINAL") != ("[CLOSE]" in literal):
            literal_exact = False
    checked(literal_exact, "exact_card_mnemonic_formal_exemplar_and_close_layers", checks)
    checked(owner_exact, "v71_whole_plant_owners_exact", checks)
    checked(all(row["owner_status"] == "PAGE_OWNER_ONLY" and row["whole_plant_owner"].startswith("WHOLE_") for row in events), "every_event_has_unidentified_whole_plant_owner", checks)

    checked(all(row["concrete_german_meaning_in_context"].strip().endswith((".", "!", "?")) for row in events), "every_event_has_concrete_punctuated_german_context", checks)
    checked(all(0.15 <= float(row["meaning_in_context_confidence"]) <= 0.55 for row in events), "event_confidences_bounded", checks)
    checked(all(row["strongest_alternative"].startswith("Technischer Pflanzenmaterial-Rivale:") for row in events), "every_event_has_one_concrete_alternative", checks)
    checked(all(row["strongest_contradiction"].strip() for row in events), "every_event_has_contradiction", checks)
    checked(all(row["unsupported_nouns"].strip() for row in events), "every_event_has_explicit_noun_audit", checks)

    by_field: dict[str, list[dict[str, str]]] = defaultdict(list)
    by_statement: dict[str, list[dict[str, str]]] = defaultdict(list)
    by_record: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in events:
        by_field[row["field_id"]].append(row)
        by_statement[row["statement_id"]].append(row)
        by_record[row["record_unit_id"]].append(row)
    field_source_by_id = {row["field_id"]: row for row in source_fields}
    field_membership = all(
        row["event_serials"] == field_source_by_id[row["field_id"]]["event_serials"]
        and row["event_serials"] == "|".join(e["event_serial"] for e in by_field[row["field_id"]])
        for row in fields
    )
    checked(field_membership, "field_event_membership_exact_v69", checks)
    statement_source_by_id = {row["statement_id"]: row for row in source_statements}
    statement_membership = all(
        row["constituent_fields"] == statement_source_by_id[row["statement_id"]]["constituent_fields"]
        and row["event_serials"] == statement_source_by_id[row["statement_id"]]["event_serials"]
        and row["event_serials"] == "|".join(e["event_serial"] for e in by_statement[row["statement_id"]])
        for row in statements
    )
    checked(statement_membership, "statement_event_and_field_membership_exact_v72", checks)
    checked(next(row for row in statements if row["statement_id"] == "H5-S001")["constituent_fields"] == "F014|F015", "h5_s001_cross_field_continuation_retained", checks)

    all_article_events = [
        serial
        for row in articles
        for serial in re.findall(r"E(\d+)=", row["event_alignment"])
    ]
    checked(all_article_events == [str(i) for i in range(1, 101)], "article_alignment_covers_each_event_once_in_order", checks)
    article_membership = all(
        row["event_serials"] == "|".join(e["event_serial"] for e in by_record[row["record_unit_id"]])
        and row["event_bound_continuous_text"] == " ".join(e["concrete_german_meaning_in_context"] for e in by_record[row["record_unit_id"]])
        and row["fluent_article"].strip()
        and row["historical_source_structure"].strip()
        for row in articles
    )
    checked(article_membership, "five_articles_complete_and_event_bound", checks)
    checked(articles[0]["whole_plant_owner"] == articles[1]["whole_plant_owner"] and articles[0]["page"] == articles[1]["page"] == "f10r", "h1_h2_same_f10r_whole_plant_owner_explicit", checks)

    noun_members: dict[str, list[str]] = defaultdict(list)
    for row in events:
        if row["unsupported_nouns"] != "NONE":
            for noun in row["unsupported_nouns"].split("|"):
                noun_members[noun].append(row["event_serial"])
    noun_table = {row["unsupported_noun"]: row for row in nouns}
    checked(set(noun_table) == set(noun_members), "unsupported_noun_inventory_complete", checks)
    checked(all(noun_table[n]["event_serials"].split("|") == ids for n, ids in noun_members.items()), "unsupported_noun_event_bindings_exact", checks)
    checked(all(row["support_class"] in {
        "VISIBLE_PART_BUT_EVENT_BINDING_UNSUPPORTED",
        "UNPICTURED_MEDICAL_OR_USE_NOUN",
        "UNPICTURED_QUANTITATIVE_OR_TEMPORAL_NOUN",
        "UNPICTURED_MATERIAL_IMPLEMENT_OR_MEDIUM",
        "UNPICTURED_RECIPE_STATE_OR_OPERATION_NOUN",
    } for row in nouns), "unsupported_noun_classes_valid", checks)

    semantic_text = "\n".join(
        [row["concrete_german_meaning_in_context"] for row in events]
        + [row["third_edition_field_text"] for row in fields]
        + [row["third_edition_statement_text"] for row in statements]
        + [row["fluent_article"] for row in articles]
    )
    withdrawn_species = re.compile(r"Teufelsabbiss|Duftveilchen|Veilchen|Bärlauch|Sonnentau|Allium|Wegerich|Alraune", re.I)
    checked(not withdrawn_species.search(semantic_text), "plant_species_remain_open", checks)
    checked(not re.search(r"\b(prefix|suffix|PAGE_HOST|EVA|Lautwert|Stammwert|Morphem)\b", semantic_text, re.I), "no_sound_spelling_stem_or_component_inference", checks)
    checked(not any(row["page"].casefold().startswith("f84") for row in events), "f84_and_f84r_absent_from_data", checks)
    checked(all("surface" not in key.casefold() for key in events[0]), "no_surface_spelling_column", checks)

    report_event_ids = set(re.findall(r"E(\d+)", report))
    checked({"1", "17", "44", "69", "98"}.issubset(report_event_ids), "report_contains_five_literal_traces", checks)
    checked(all(f"### {r} —" in report for r in ("H1", "H2", "H3", "H4", "H5")), "report_contains_five_full_articles", checks)
    checked(all(f"| F{i:03d} |" in report for i in range(1, 21)), "report_walks_all_20_fields", checks)
    checked("keine Entzifferung" in report and "Pflanzenarten" in report, "report_states_interpretation_ceiling", checks)

    supported_events = sum(row["v69_support_class"] != "UNKNOWN_EXEMPLAR_WHOLE_CARD" for row in events)
    checked(supported_events == 29, "exactly_29_parser_supported_herbal_events_retained", checks)

    artifacts = [EVENTS, FIELDS, STATEMENTS, ARTICLES, NOUNS, REPORT, BUILDER, Path(__file__)]
    validation = {
        "status": "PASS" if all(checks.values()) else "FAIL",
        "checks": checks,
        "counts": {
            "events": len(events),
            "fields": len(fields),
            "statements": len(statements),
            "articles": len(articles),
            "records": len(set(row["record_unit_id"] for row in events)),
            "pages": len(set(row["page"] for row in events)),
            "unsupported_noun_types": len(nouns),
            "parser_supported_events": supported_events,
            "support_class_distribution": dict(sorted(Counter(row["v69_support_class"] for row in events).items())),
        },
        "sealed": {"f84": True, "f84r": True},
        "sha256": {path.name: hashlib.sha256(path.read_bytes()).hexdigest() for path in artifacts},
    }
    VALIDATION.write_text(json.dumps(validation, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(validation, ensure_ascii=False, indent=2))
    if validation["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
