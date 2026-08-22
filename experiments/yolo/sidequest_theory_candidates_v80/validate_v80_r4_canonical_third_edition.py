#!/usr/bin/env python3
"""Validate the V80 R4 canonical third-edition release."""

from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter
from pathlib import Path


HERE = Path(__file__).resolve().parent


def rows(name: str) -> list[dict[str, str]]:
    with (HERE / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


cards = rows("V80_R4_CANONICAL_173_CARD_DICTIONARY.tsv")
events = rows("V80_R4_CANONICAL_381_PROSE_EVENT_INTERLINEAR.tsv")
fields = rows("V80_R4_CANONICAL_135_FIELD_EDITION.tsv")
statements = rows("V80_R4_CANONICAL_116_STATEMENT_EDITION.tsv")
astro = rows("V80_R4_CANONICAL_395_ASTRO_GROUP_EDITION.tsv")
unified = rows("V80_R4_CANONICAL_776_UNIFIED_LEDGER.tsv")
manual = rows("V80_R4_CANONICAL_WORKSHOP_MANUAL.tsv")
contradictions = rows("V80_R4_CANONICAL_CONTRADICTION_LEDGER.tsv")
summary = json.loads((HERE / "V80_R4_BUILD_SUMMARY.json").read_text(encoding="utf-8"))
readable = (HERE / "V80_R4_COMPLETE_TEN_PAGE_READABLE_EDITION.md").read_text(encoding="utf-8")

card_ids = {row["joint_tuple_id"] for row in cards}
event_ids = {row["event_id"] for row in events}
event_serials = {int(row["event_serial"]) for row in events}
page_set = {row["page"] for row in unified}
expected_pages = {"f10r", "f11r", "f55v", "f56r", "f67r2", "f68r1", "f69v", "f81v", "f82r", "f83r"}


def exploded(rows_in: list[dict[str, str]], field: str) -> list[int]:
    values: list[int] = []
    for row in rows_in:
        values.extend(int(value) for value in row[field].split("|") if value)
    return values


field_events = exploded(fields, "event_serials")
statement_events = exploded(statements, "event_serials")
category_counts = Counter(row["operational_class"] for row in cards)
astro_page_counts = Counter(row["page"] for row in astro)
et_rows = [row for row in cards if row["joint_tuple_id"] == "dcda95c81a5460feb191"]
per_rows = [row for row in cards if row["joint_tuple_id"] == "b5fcea1eaed06b2f2291"]
event_map = {row["event_id"]: row for row in events}

checks = {
    "cards_173": len(cards) == 173,
    "cards_unique": len(card_ids) == 173,
    "dictionary_category_counts": category_counts == {
        "OPAQUE_EXEMPLAR_CARD": 169,
        "FORMAL_NONWORD_CHANNEL": 2,
        "FORMAL_LINK_OR_SLOT": 1,
        "FORMAL_RELATION_OR_ENTRY_MARK_WITH_ENTRY_BIAS": 1,
    },
    "dictionary_no_productive_components": all(row["productive_component_claim"] == "NONE" for row in cards),
    "dictionary_no_sound_language_claim": all(row["sound_language_pos_morphology_claim"] == "NONE" for row in cards),
    "et_optional_only": len(et_rows) == 1 and et_rows[0]["optional_historical_master_word"] == "ET?__UND_ODER_AUCH?" and "OPTIONAL" in et_rows[0]["portable_word_status"],
    "per_optional_only": len(per_rows) == 1 and per_rows[0]["optional_historical_master_word"] == "PER?__DURCH_ODER_GEMAESS?" and "OPTIONAL" in per_rows[0]["portable_word_status"],
    "only_two_optional_words": sum(row["optional_historical_master_word"] != "NONE" for row in cards) == 2,
    "events_381": len(events) == 381,
    "events_exact_ids": event_ids == {f"E{i:03d}" for i in range(1, 382)},
    "event_serials_exact": event_serials == set(range(1, 382)),
    "all_event_cards_in_dictionary": {row["joint_tuple_id"] for row in events} <= card_ids,
    "event_source_tokens_380": sum(int(row["source_token_count"]) for row in events) == 380,
    "e180_edge_copy": event_map["E180"]["source_token_count"] == "0" and event_map["E180"]["edge_copy_status"].startswith("ANTICIPATORY"),
    "e181_main_token": event_map["E181"]["source_token_count"] == "1" and event_map["E181"]["edge_copy_status"].startswith("MAIN_SOURCE"),
    "e180_e181_same_card_owner_statement": all(event_map["E180"][key] == event_map["E181"][key] for key in ("joint_tuple_id", "image_owner_id", "statement_id")),
    "cross_line_owner_resets_exact": {event_map[eid]["owner_break_before"] for eid in ("E203", "E264", "E291", "E356")} == {"BREAK_VISIBLE_GAP__RESET_SUBSTANCE_TARGET_DIRECTION"},
    "b2_owner_resets_exact": all(event_map[eid]["owner_break_before"].startswith("BREAK_VISIBLE_GAP") for eid in ("E189", "E198", "E203", "E212")),
    "fields_135": len(fields) == 135,
    "field_ids_exact": {row["field_id"] for row in fields} == {f"F{i:03d}" for i in range(1, 136)},
    "fields_cover_events_once": Counter(field_events) == Counter(range(1, 382)),
    "field_sections_20_115": Counter(row["section"] for row in fields) == {"HERBAL": 20, "BIOLOGICAL": 115},
    "statements_116": len(statements) == 116,
    "statement_ids_unique": len({row["statement_id"] for row in statements}) == 116,
    "statements_cover_events_once": Counter(statement_events) == Counter(range(1, 382)),
    "astro_395": len(astro) == 395,
    "astro_serials_exact": {int(row["group_serial"]) for row in astro} == set(range(1, 396)),
    "astro_page_counts": astro_page_counts == {"f67r2": 190, "f68r1": 65, "f69v": 140},
    "astro_all_local_opaque": all(row["operational_class"] == "LOCAL_OPAQUE_CELESTIAL_LABEL" for row in astro),
    "astro_no_prose_words": all(row["optional_historical_master_word"] == "NONE" for row in astro),
    "astro_no_f68_f69_key": all("NONE" in row["f68_f69_mapping"] for row in astro),
    "unified_776": len(unified) == 776,
    "unified_serial_exact": {int(row["unified_serial"]) for row in unified} == set(range(1, 777)),
    "unified_sections": Counter(row["section"] for row in unified) == {"HERBAL": 100, "BIOLOGICAL": 281, "ASTRO": 395},
    "ten_pages_exact": page_set == expected_pages,
    "manual_16": len(manual) == 16,
    "manual_operational_et": any(row["operation"] == "EMIT_FORMAL_LINK_OR_OPTIONAL_ET" for row in manual),
    "manual_operational_per": any(row["operation"] == "EMIT_FORMAL_RELATION_OR_OPTIONAL_PER" for row in manual),
    "manual_no_old_word_first_operations": not any(row["operation"] in {"EMIT_ET_QUESTIONED", "EMIT_PER_QUESTIONED"} for row in manual),
    "contradictions_15": len(contradictions) == 15,
    "readable_all_pages": all(f"## {page}" in readable for page in expected_pages),
    "readable_all_records": all(f"### Record {record}" in readable for record in ("H1", "H2", "H3", "H4", "H5", "B1", "B2", "B3", "B4", "B5", "B6")),
    "readable_all_astro_loci": sum(line.startswith("- `f67r2.") or line.startswith("- `f68r1.") or line.startswith("- `f69v.") for line in readable.splitlines()) == 142,
    "model_columns_constant": {row["leading_book_model"] for row in unified} == {"ILLUSTRATED_PRACTITIONER_BATH_AND_CELESTIAL_LOOKUP_COMPENDIUM"} and {row["rival_book_model"] for row in unified} == {"NATURALIA_COSMOGRAPHIA_WORKSHOP_MODEL_AND_MEMORY_BOOK"},
    "no_sealed_page_materialized": not any(row["page"].lower().startswith("f84") for row in unified),
    "summary_pass": summary["status"] == "PASS",
    "summary_counts_exact": summary["counts"]["cards"] == 173 and summary["counts"]["unified_groups"] == 776 and summary["counts"]["new_words"] == 0,
    "one_page_theory_present": (HERE / "V80_R4_ONE_PAGE_FINAL_THEORY.md").stat().st_size > 2000,
    "canonical_report_present": (HERE / "V80_R4_CANONICAL_THIRD_EDITION_REPORT.md").stat().st_size > 8000,
}

output_names = [
    "V80_R4_ONE_PAGE_FINAL_THEORY.md",
    "V80_R4_CANONICAL_THIRD_EDITION_REPORT.md",
    "V80_R4_CANONICAL_173_CARD_DICTIONARY.tsv",
    "V80_R4_CANONICAL_381_PROSE_EVENT_INTERLINEAR.tsv",
    "V80_R4_CANONICAL_135_FIELD_EDITION.tsv",
    "V80_R4_CANONICAL_116_STATEMENT_EDITION.tsv",
    "V80_R4_CANONICAL_395_ASTRO_GROUP_EDITION.tsv",
    "V80_R4_CANONICAL_776_UNIFIED_LEDGER.tsv",
    "V80_R4_COMPLETE_TEN_PAGE_READABLE_EDITION.md",
    "V80_R4_CANONICAL_WORKSHOP_MANUAL.tsv",
    "V80_R4_CANONICAL_CONTRADICTION_LEDGER.tsv",
]
checks["summary_output_hashes_current"] = all(summary["output_hashes"].get(name) == sha256(HERE / name) for name in output_names)

result = {
    "schema": "SIDEQUEST_V80_R4_VALIDATION_V1",
    "status": "PASS" if all(checks.values()) else "FAIL",
    "checks": checks,
    "passed": sum(checks.values()),
    "total": len(checks),
    "failed": [key for key, value in checks.items() if not value],
    "counts": summary["counts"],
    "models": summary["models"],
    "seals": summary["seals"],
    "ceiling": summary["ceiling"],
}
(HERE / "V80_R4_VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(f"{result['status']} {result['passed']}/{result['total']}")
raise SystemExit(0 if result["status"] == "PASS" else 1)
