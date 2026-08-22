#!/usr/bin/env python3
"""Build the V69 R4 canonical dual ten-page second edition."""

from __future__ import annotations

import csv
import json
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
V60 = ROOT / "experiments/yolo/sidequest_theory_candidates_v60"
V63 = ROOT / "experiments/yolo/sidequest_theory_candidates_v63"
V64 = ROOT / "experiments/yolo/sidequest_theory_candidates_v64"
V65 = ROOT / "experiments/yolo/sidequest_theory_candidates_v65"
V66 = ROOT / "experiments/yolo/sidequest_theory_candidates_v66"
V67 = ROOT / "experiments/yolo/sidequest_theory_candidates_v67"
V68 = ROOT / "experiments/yolo/sidequest_theory_candidates_v68"


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: list[dict[str, object]], fields: list[str]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, delimiter="\t", fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    # Final exact-card dictionary: no semantic changes after V60.
    dictionary_source = read_tsv(V60 / "V60_SELECTED_173_CARD_DICTIONARY.tsv")
    dictionary = []
    for row in dictionary_source:
        mnemonic = row["ATOMIC_OR_WHOLE_CARD_MNEMONIC"]
        formal = row["strict_control_prompt"]
        if mnemonic != "UNKNOWN" and formal != "NONE":
            control = "MNEMONIC_AND_FORMAL_CHANNELS"
        elif mnemonic != "UNKNOWN":
            control = "EXACT_WORKING_MNEMONIC"
        elif formal != "NONE":
            control = "STRICT_FORMAL_PROMPT_NO_WORD_VALUE"
        else:
            control = "UNKNOWN_EXEMPLAR_WHOLE_CARD"
        out = dict(row)
        out["V69_FINAL_CONTROL_CLASS"] = control
        out["V69_SEMANTIC_CEILING"] = "CREATIVE_MNEMONIC_OR_FORMAL_ROLE_ONLY;NO_LEXEME_CLAIM"
        dictionary.append(out)

    h_med = read_tsv(V64 / "V64_R2_100_EVENT_HERBAL_INTERLINEAR.tsv")
    h_riv = {r["event_serial"]: r for r in read_tsv(V64 / "V64_R3_100_EVENT_PLANT_LEDGER.tsv")}
    b_med = read_tsv(V65 / "V65_R2_281_EVENT_BIO_INTERLINEAR.tsv")
    b_riv = {r["event_serial"]: r for r in read_tsv(V65 / "V65_R3_281_EVENT_WATERWORK_LEDGER.tsv")}
    prose = []
    for row in h_med:
        rival = h_riv[row["event_serial"]]
        prose.append({
            "event_serial": row["event_serial"], "page": row["page"], "locus": row["locus"],
            "record_unit_id": row["record_unit_id"], "field_id": row["field_id"], "statement_id": row["statement_id"],
            "joint_tuple_id": row["joint_tuple_id"], "surface_display_only": row["surface_display_only"],
            "formal_formula_opaque": row["formal_formula_opaque"], "terminal_status": row["terminal_status"],
            "strict_formal_prompt": row["strict_formal_prompt"], "selected_exact_mnemonic": row["selected_exact_mnemonic"],
            "event_template": row["v63_event_template"], "parse_status": row["v63_event_parse_status"],
            "iatromedical_source_segment": row["v64_tagged_source_segment"],
            "practical_source_segment": rival["complete_layered_technical_reading"],
            "content_relation": "COEQUAL_LOCAL_EDITIONS",
            "semantic_ceiling": "EXACT_ID_FORMAL_MNEMONIC_LOCAL_EXPANSION_SEPARATE",
        })
    for row in b_med:
        rival = b_riv[row["event_serial"]]
        prose.append({
            "event_serial": row["event_serial"], "page": row["page"], "locus": row["locus"],
            "record_unit_id": row["record_unit_id"], "field_id": row["field_id"], "statement_id": row["statement_id"],
            "joint_tuple_id": row["joint_tuple_id"], "surface_display_only": row["surface_display_only"],
            "formal_formula_opaque": row["formal_formula_opaque"], "terminal_status": row["terminal_status"],
            "strict_formal_prompt": row["strict_formal_prompt"], "selected_exact_mnemonic": row["selected_v60_exact_mnemonic"],
            "event_template": row["v63_event_template"], "parse_status": row["v63_event_parse_status"],
            "iatromedical_source_segment": row["v65_concrete_default_segment"],
            "practical_source_segment": rival["complete_layered_technical_reading"],
            "content_relation": "COEQUAL_LOCAL_EDITIONS",
            "semantic_ceiling": "EXACT_ID_FORMAL_MNEMONIC_LOCAL_EXPANSION_SEPARATE",
        })
    prose.sort(key=lambda r: int(r["event_serial"]))

    # Fields and statements preserve V63 structure and expose both content editions.
    hmf = {r["field_id"]: r for r in read_tsv(V64 / "V64_R2_20_FIELD_EDITIONS.tsv")}
    hrf = {r["field_id"]: r for r in read_tsv(V64 / "V64_R3_20_FIELD_PLANT_EDITION.tsv")}
    bmf = {r["field_id"]: r for r in read_tsv(V65 / "V65_R2_115_FIELD_EDITIONS.tsv")}
    brf = {r["field_id"]: r for r in read_tsv(V65 / "V65_R3_115_FIELD_WATERWORK_EDITION.tsv")}
    field_base = read_tsv(V63 / "V63_SELECTED_135_FIELD_SLOT_PARSE.tsv")
    fields = []
    for row in field_base:
        if row["field_id"] in hmf:
            medical = hmf[row["field_id"]]["v64_tagged_continuous_field_text"]
            practical = hrf[row["field_id"]]["complete_technical_field_reading"]
        else:
            medical = bmf[row["field_id"]]["v65_tagged_field_interlinear"]
            practical = brf[row["field_id"]]["complete_technical_field_reading"]
        fields.append({
            "field_id": row["field_id"], "record_unit_id": row["record_unit_id"], "page": row["page"],
            "locus": row["locus"], "statement_id": row["statement_id"], "event_count": row["event_count"],
            "event_serials": row["event_serials"], "primary_template": row["primary_template"],
            "licensed_primitive_sequence": row["licensed_primitive_sequence"], "parse_status": row["parse_status"],
            "recognized_event_count": row["recognized_event_count"], "exemplar_only_event_count": row["exemplar_only_event_count"],
            "iatromedical_field_text": medical, "practical_field_text": practical,
            "roundtrip_status": row["roundtrip_status"], "semantic_ceiling": "COEQUAL_LOCAL_EDITIONS_NOT_TEMPLATE_VALUES",
        })

    h_stat = {r["statement_id"]: r for r in read_tsv(V64 / "V64_R3_19_STATEMENT_COMPARISON.tsv")}
    bm_stat = {r["statement_id"]: r for r in read_tsv(V65 / "V65_R2_97_STATEMENT_EDITIONS.tsv")}
    br_stat = {r["statement_id"]: r for r in read_tsv(V65 / "V65_R3_97_STATEMENT_COMPARISON.tsv")}
    statement_base = read_tsv(V63 / "V63_SELECTED_116_STATEMENT_SLOT_PARSE.tsv")
    statements = []
    for row in statement_base:
        sid = row["statement_id"]
        if sid in h_stat:
            medical = h_stat[sid]["complete_iatromedical_comparator"]
            practical = h_stat[sid]["complete_technical_plant_reading"]
            winner = h_stat[sid]["coherence_winner"]
            contradiction = h_stat[sid]["strongest_technical_contradiction"]
        else:
            medical = bm_stat[sid]["v65_tagged_historical_source_clause"]
            practical = br_stat[sid]["complete_technical_waterwork_reading"]
            winner = br_stat[sid]["statement_coherence_winner"]
            contradiction = br_stat[sid]["strongest_technical_contradiction"]
        statements.append({
            "statement_id": sid, "record_unit_id": row["record_unit_id"], "page": row["page"],
            "statement_ordinal_in_record": row["statement_ordinal_in_record"], "constituent_fields": row["constituent_fields"],
            "event_count": row["event_count"], "event_serials": row["event_serials"],
            "primary_template": row["primary_template"], "licensed_primitive_sequence": row["licensed_primitive_sequence"],
            "parse_status": row["parse_status"], "pre_state": row["pre_state"], "post_state": row["post_state"],
            "iatromedical_statement_text": medical, "practical_statement_text": practical,
            "local_comparison": winner, "strongest_practical_contradiction": contradiction,
            "roundtrip_status": row["roundtrip_status"], "semantic_ceiling": "SOURCE_EXPANSIONS_REQUIRE_MASTER_EXEMPLAR",
        })

    # Astro dual edition.
    astro_med = read_tsv(V66 / "V66_R2_395_GROUP_ASTRO_INTERLINEAR.tsv")
    astro_riv = read_tsv(V66 / "V66_R3_395_GROUP_LOOKUP_EDITION.tsv")
    if len(astro_med) != len(astro_riv):
        raise ValueError("Astro source lengths differ")
    astro = []
    for med, riv in zip(astro_med, astro_riv):
        if (med["page"], med["locus"], med["surface_ZL3b"]) != (riv["page"], riv["source_locus"], riv["surface_display_only"]):
            raise ValueError("Astro source alignment differs")
        astro.append({
            "group_serial": med["group_serial"], "diagram_id": riv["diagram_id"], "page": med["page"],
            "locus": med["locus"], "event_index": med["event_index"], "opaque_local_id": riv["local_group_id"],
            "surface_display_only": med["surface_ZL3b"], "local_formal_role": riv["technical_group_role"],
            "iatromedical_local_text": med["default_content_German"],
            "practical_local_text": riv["concrete_technical_function_German"],
            "orientation_status": med["rotation_start_status"], "f68_f69_mapping": "NONE",
            "semantic_ceiling": "PAGE_LOCAL_EXEMPLAR_NOT_WORD_OR_PROSE_CARD",
        })

    # Complete 14-unit dual text.
    hm_units = {r["record_unit_id"]: r for r in read_tsv(V64 / "V64_R2_FIVE_RECORD_EDITIONS.tsv")}
    hr_units = {r["record_unit_id"]: r for r in read_tsv(V64 / "V64_R3_5_RECORD_PLANT_EDITION.tsv")}
    bm_units = {r["record_unit_id"]: r for r in read_tsv(V65 / "V65_R2_SIX_RECORD_EDITIONS.tsv")}
    br_units = {r["record_unit_id"]: r for r in read_tsv(V65 / "V65_R3_6_RECORD_WATERWORK_EDITION.tsv")}
    am_units = {r["diagram_id"]: r for r in read_tsv(V66 / "V66_R2_THREE_DIAGRAM_EDITIONS.tsv")}
    ar_units = {r["diagram_id"]: r for r in read_tsv(V66 / "V66_R3_3_DIAGRAM_TECHNICAL_EDITION.tsv")}
    contradiction_map = {r["unit_id"]: r for r in read_tsv(V68 / "V68_R4_14_UNIT_CONTRADICTION_LEDGER.tsv")}
    units = []
    for uid in ["H1", "H2", "H3", "H4", "H5"]:
        m, r = hm_units[uid], hr_units[uid]
        units.append({
            "unit_id": uid, "page": m["page"], "section": "HERBAL", "title": m["article_title"],
            "iatromedical_complete_text": m["tagged_continuous_german_source_edition"],
            "practical_complete_text": r["complete_technical_plant_article"],
            "content_status": "COEQUAL_CONTENT_FORK", "strongest_practical_contradiction": contradiction_map[uid]["contradiction"],
        })
    for uid in ["B1", "B2", "B3", "B4", "B5", "B6"]:
        m, r = bm_units[uid], br_units[uid]
        units.append({
            "unit_id": uid, "page": m["page"], "section": "BIOLOGICAL", "title": m["edition_title"],
            "iatromedical_complete_text": m["tagged_continuous_german_source_edition"],
            "practical_complete_text": r["complete_technical_waterwork_article"],
            "content_status": "COEQUAL_CONTENT_FORK", "strongest_practical_contradiction": contradiction_map[uid]["contradiction"],
        })
    for uid in ["A1", "A2", "A3"]:
        m, r = am_units[uid], ar_units[uid]
        units.append({
            "unit_id": uid, "page": m["page"], "section": "ASTRO", "title": m["selected_system"],
            "iatromedical_complete_text": m["complete_default_German"],
            "practical_complete_text": r["complete_technical_default_German"],
            "content_status": "COEQUAL_CONTENT_FORK", "strongest_practical_contradiction": contradiction_map[uid]["contradiction"],
        })

    # One common 776-row ledger.
    ledger = []
    for row in prose:
        ledger.append({
            "global_index": len(ledger) + 1, "section": "PROSE", "page": row["page"], "unit_id": row["record_unit_id"],
            "locus": row["locus"], "opaque_identity": row["joint_tuple_id"], "surface_display_only": row["surface_display_only"],
            "formal_role": row["event_template"], "working_mnemonic": row["selected_exact_mnemonic"],
            "iatromedical_text": row["iatromedical_source_segment"], "practical_text": row["practical_source_segment"],
            "source_recovery_without_exemplar": "NO_FULL_SOURCE_RECOVERY",
        })
    for row in astro:
        ledger.append({
            "global_index": len(ledger) + 1, "section": "ASTRO", "page": row["page"], "unit_id": row["diagram_id"],
            "locus": row["locus"], "opaque_identity": row["opaque_local_id"], "surface_display_only": row["surface_display_only"],
            "formal_role": row["local_formal_role"], "working_mnemonic": "PAGE_LOCAL_ONLY",
            "iatromedical_text": row["iatromedical_local_text"], "practical_text": row["practical_local_text"],
            "source_recovery_without_exemplar": "NO_FULL_SOURCE_RECOVERY",
        })

    manual = read_tsv(V67 / "V67_R4_NINE_LESSON_MANUAL.tsv")

    write_tsv(HERE / "V69_R4_FINAL_173_CARD_DICTIONARY.tsv", dictionary, list(dictionary[0]))
    write_tsv(HERE / "V69_R4_FINAL_381_PROSE_EVENT_INTERLINEAR.tsv", prose, list(prose[0]))
    write_tsv(HERE / "V69_R4_FINAL_135_FIELD_EDITION.tsv", fields, list(fields[0]))
    write_tsv(HERE / "V69_R4_FINAL_116_STATEMENT_EDITION.tsv", statements, list(statements[0]))
    write_tsv(HERE / "V69_R4_FINAL_395_ASTRO_GROUPS.tsv", astro, list(astro[0]))
    write_tsv(HERE / "V69_R4_FINAL_776_GROUP_LEDGER.tsv", ledger, list(ledger[0]))
    write_tsv(HERE / "V69_R4_FINAL_14_UNIT_DUAL_TRANSLATION.tsv", units, list(units[0]))
    write_tsv(HERE / "V69_R4_FINAL_9_LESSON_WORKSHOP_MANUAL.tsv", manual, list(manual[0]))

    # Human-readable dual edition generated from the canonical unit table.
    lines = ["# V69 R4 — lesbare duale Zehnseitenedition", "", "Status: kreative Quellenedition; keine Entzifferung.", ""]
    for row in units:
        lines += [f"## {row['unit_id']} — {row['page']}: {row['title']}", "", "**Iatromedizinische Lesefassung**", "", row["iatromedical_complete_text"], "", "**Praktisch-technische Lesefassung**", "", row["practical_complete_text"], "", f"**Stärkster Widerspruch des praktischen Rivals:** {row['strongest_practical_contradiction']}", ""]
    (HERE / "V69_R4_READABLE_DUAL_TEN_PAGE_EDITION.md").write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")

    control_counts = Counter(r["V69_FINAL_CONTROL_CLASS"] for r in dictionary)
    event_counts = Counter(r["parse_status"] for r in prose)
    field_counts = Counter(r["parse_status"] for r in fields)
    statement_counts = Counter(r["parse_status"] for r in statements)
    checks = {
        "dictionary_173": len(dictionary) == 173,
        "prose_381": len(prose) == 381,
        "fields_135": len(fields) == 135,
        "statements_116": len(statements) == 116,
        "astro_395": len(astro) == 395,
        "ledger_776": len(ledger) == 776,
        "units_14": len(units) == 14,
        "manual_lessons_9": len(manual) == 9,
        "exact_event_serials": [int(r["event_serial"]) for r in prose] == list(range(1, 382)),
        "dictionary_occurrences_sum_381": sum(int(r["occurrences"]) for r in dictionary) == 381,
        "control_card_types_14": sum(v for k, v in control_counts.items() if k != "UNKNOWN_EXEMPLAR_WHOLE_CARD") == 14,
        "unknown_card_types_159": control_counts["UNKNOWN_EXEMPLAR_WHOLE_CARD"] == 159,
        "event_status_119_262": sum(v for k, v in event_counts.items() if k != "UNPARSED_EXEMPLAR") == 119 and event_counts["UNPARSED_EXEMPLAR"] == 262,
        "field_status_14_56_65": field_counts == Counter({"UNIQUE": 14, "AMBIGUOUS": 56, "UNPARSED": 65}),
        "statement_status_12_49_55": statement_counts == Counter({"UNIQUE": 12, "AMBIGUOUS": 49, "UNPARSED": 55}),
        "all_dual_text_nonempty": all(r["iatromedical_text"].strip() and r["practical_text"].strip() for r in ledger),
        "no_f68_f69_mapping": all(r["f68_f69_mapping"] == "NONE" for r in astro),
        "no_full_source_without_exemplar": all(r["source_recovery_without_exemplar"] == "NO_FULL_SOURCE_RECOVERY" for r in ledger),
        "no_forbidden_page": all(not r["page"].startswith("f84") for r in ledger),
        "content_parity_explicit": all(r["content_status"] == "COEQUAL_CONTENT_FORK" for r in units),
    }
    payload = {
        "artifact": "V69_R4_CANONICAL_DUAL_SECOND_EDITION",
        "status": "PASS" if all(checks.values()) else "FAIL",
        "counts": {"dictionary": len(dictionary), "prose": len(prose), "fields": len(fields), "statements": len(statements), "astro": len(astro), "ledger": len(ledger), "units": len(units)},
        "dictionary_classes": dict(control_counts),
        "event_parse": dict(event_counts), "field_parse": dict(field_counts), "statement_parse": dict(statement_counts),
        "final_theory": "DOMAIN_NEUTRAL_EXEMPLAR_CARD_REGISTER_WITH_COEQUAL_IATROMEDICAL_AND_PRACTICAL_CONTENT_EDITIONS",
        "checks": checks,
        "interpretive_limit": "This is a complete speculative working edition, not recovered language, sound, plaintext, or translation.",
        "stop_rule": "V69_COMPLETE_NO_V70_AUTOMATIC",
    }
    (HERE / "V69_R4_VALIDATION.json").write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    if payload["status"] != "PASS":
        raise SystemExit(json.dumps(payload, ensure_ascii=False))


if __name__ == "__main__":
    main()
