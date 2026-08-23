#!/usr/bin/env python3
"""Assemble one compact practical codebook for all ten fixed pages."""

from __future__ import annotations

import csv
import json
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
R80 = ROOT / "experiments/yolo/sidequest_semantic_selected_workshop_eightieth_edition/EIGHTIETH_43_CARD_SOURCE_LICENSES.tsv"
R87 = ROOT / "experiments/yolo/sidequest_semantic_textual_anchor_eighty_seventh_edition/EIGHTY_SEVENTH_776_WORD_PROVENANCE_BINDING.tsv"
R88 = ROOT / "experiments/yolo/sidequest_semantic_master_tail_repair_eighty_eighth_edition/EIGHTY_EIGHTH_REVISED_44_SOURCE_WORDS.tsv"
R89E = ROOT / "experiments/yolo/sidequest_semantic_continuous_translation_eighty_ninth_edition/EIGHTY_NINTH_381_EVENT_STATEMENT_BINDING.tsv"
R93 = ROOT / "experiments/yolo/sidequest_semantic_unified_apprentice_grammar_ninety_third_edition"
R94 = ROOT / "experiments/yolo/sidequest_semantic_astro_apprentice_ninety_fourth_edition"


CARD_TO_PRIMITIVE = {
    "ROOT_AIIN": "MEASURE", "ROOT_AIN": "MATERIAL_ADD", "ROOT_IIN": "MEASURE",
    "ROOT_AL": "TARGET", "ROOT_AR": "PART_SELECT", "ROOT_AIR": "PASS_STRAIN",
    "ROOT_OK": "SET", "ROOT_OL": "CONTINUE", "ROOT_OT": "CONTINUE",
    "ROOT_OR": "SET", "ROOT_Y": "PART_SELECT", "ROOT_E": "GRADE",
    "ROOT_EE": "GRADE", "ROOT_EEE": "GRADE", "ROOT_CLOSE": "CLOSE",
    "ROOT_CHD": "TRANSFER", "ROOT_CTH": "READY", "ROOT_CKH": "PASS_STRAIN",
    "ROOT_CKHE": "PASS_STRAIN", "ROOT_CHK": "HEAT", "ROOT_SHED": "SETTLE",
    "ROOT_SOLK": "COLLECT_STORE", "ROOT_HO": "MATERIAL_ADD",
    "ROOT_CHEO": "COLLECT_STORE", "ROOT_KCH": "CUT_CRUSH",
    "ROOT_TY": "PART_SELECT", "ROOT_SH": "SETTLE", "ROOT_CHEEY": "READY",
    "N01_CFH": "PASS_STRAIN", "N02_CPH": "PASS_STRAIN",
    "N03_PARTITION": "PART_SELECT", "N04_HO": "MATERIAL_ADD",
    "N05_DCHE": "PART_SELECT", "N06_PREV": "CONTINUE", "N07_WASH": "WASH",
    "N08_LDDY": "FASTEN", "N09_SK": "DRAIN", "N10_DAN": "USE_APPLY",
    "N11_DL": "MATERIAL_ADD", "N12_TALAM": "COLLECT_STORE",
    "S01_DAIN": "PASS_STRAIN|MATERIAL_ADD", "S02_ODY": "GRADE|ASTRO_LOCAL_MARK",
    "S03_OS": "OWNER_SELECT",
}


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: list[dict[str, object]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    primitives = read_tsv(R93 / "NINETY_THIRD_20_UNIFIED_SOURCE_PRIMITIVES.tsv")
    rules = read_tsv(R93 / "NINETY_THIRD_12_APPRENTICE_RULES.tsv")
    statement_grammar = read_tsv(R93 / "NINETY_THIRD_116_UNIFIED_STATEMENT_GRAMMAR.tsv")
    cards = read_tsv(R80)
    words = read_tsv(R88)
    astro_rules = read_tsv(R94 / "NINETY_FOURTH_8_ASTRO_APPRENTICE_PRIMITIVES.tsv")
    astro_groups = read_tsv(R94 / "NINETY_FOURTH_395_GROUP_COPY_TRACE.tsv")
    base_binding = read_tsv(R87)
    event_binding = read_tsv(R89E)

    primitive_counts = Counter(part for row in statement_grammar for part in row["unified_primitive_sequence"].split(">"))
    primitive_rows = []
    for row in primitives:
        primitive_rows.append({**row, "prose_occurrence_count": primitive_counts[row["primitive_id"]]})
    write_tsv(OUT / "NINETY_FIFTH_20_PROSE_PRIMITIVES.tsv", primitive_rows)

    card_rows = []
    for row in cards:
        card_rows.append({
            "dictionary_order": row["dictionary_order"], "entry_id": row["entry_id"],
            "entry_kind": row["entry_kind"], "surface_or_pattern": row["surface_or_pattern"],
            "minimal_value_de": row["minimal_value_de"],
            "unified_primitive": CARD_TO_PRIMITIVE[row["entry_id"]],
            "licensed_source_slots": row["licensed_source_slots"],
            "license_rule_de": row["license_rule_de"],
            "memorization_mode": "PRODUCTIVE_COMPOSITION" if row["entry_kind"] == "PRODUCTIVE_ROOT" else "LEARN_EXACT_WHOLE_OR_REGISTER_SPLIT",
        })
    write_tsv(OUT / "NINETY_FIFTH_43_CARD_CODEBOOK.tsv", card_rows)

    word_rows = []
    word_by_unit: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in words:
        word_rows.append({
            "codex_word_id": row["codex_word_id"], "domain": row["domain"],
            "selected_word_de": row["selected_word_de"], "used_units": row["used_units"],
            "primary_anchor": row["primary_anchor"], "working_status": row["working_status"],
            "meaning_scope_de": row["meaning_scope_de"],
        })
        for unit in row["used_units"].split(","):
            word_by_unit[unit].append(row)
    write_tsv(OUT / "NINETY_FIFTH_44_SOURCE_WORDS.tsv", word_rows)
    write_tsv(OUT / "NINETY_FIFTH_8_ASTRO_RULES.tsv", astro_rules)

    statement_by_id = {row["statement_id"]: row for row in statement_grammar}
    event_by_serial = {int(row["event_serial"]): row for row in event_binding}
    astro_by_serial = {381 + int(row["group_serial"]): row for row in astro_groups}
    coverage = []
    for base in base_binding:
        serial = int(base["unified_serial"])
        unit_id = base["unit_id"]
        source_words = word_by_unit[unit_id]
        if serial <= 381:
            event = event_by_serial[serial]
            statement = statement_by_id[event["statement_id"]]
            mode = "COMBINATORIAL_PROSE"
            primitive_sequence = statement["unified_primitive_sequence"]
            local_status = f"STATEMENT={event['statement_id']}"
        else:
            group = astro_by_serial[serial]
            mode = "LOCAL_ASTRO_NOMENCLATOR"
            primitive_sequence = group["locus_primitive_sequence"]
            local_status = f"NAMESPACE={group['local_namespace']}"
        coverage.append({
            "unified_serial": serial, "domain": base["domain"], "page": base["page"],
            "unit_id": unit_id, "local_address": base["local_address"],
            "visible_identity": base["visible_identity"], "compiler_mode": mode,
            "primitive_sequence": primitive_sequence, "local_status": local_status,
            "source_word_ids": ";".join(row["codex_word_id"] for row in source_words),
            "source_words_de": ";".join(row["selected_word_de"] for row in source_words),
            "short_reading": base["short_form_reading"],
        })
    write_tsv(OUT / "NINETY_FIFTH_776_COMPLETE_COVERAGE.tsv", coverage)

    sheet = [
        "# Kompaktes Werkstatt-Codebuch der zehn Seiten", "",
        "## Modus wählen", "",
        "- **PROSA:** Herbal/Bio → Besitzer setzen, Quellenprogramm laden, zwanzig Rollen komponieren, Karte rendern.",
        "- **ASTRO:** Instrument/Namensraum/Platz wählen, opake Gruppen kopieren, nur lokal lesen.", "",
        "## Zwanzig Prosa-Rollen", "",
        "| Rolle | Kurzbedeutung | Karten-/Quellenbasis |", "|---|---|---|",
    ]
    for row in primitive_rows:
        sheet.append(f"| {row['primitive_id']} | {row['source_meaning_de']} | {row['card_or_source_basis']} |")
    sheet.extend(["", "## 43 Karten-/Kürzelwerte", "", "| Eintrag | Form | Wert | Werkstattrolle | Lernart |", "|---|---|---|---|---|"])
    for row in card_rows:
        sheet.append(f"| {row['entry_id']} | {row['surface_or_pattern']} | {row['minimal_value_de']} | {row['unified_primitive']} | {row['memorization_mode']} |")
    sheet.extend(["", "## 44 Quellenwörter", "", "| ID | Register | Wort | Einheiten | Herkunft |", "|---|---|---|---|---|"])
    for row in word_rows:
        sheet.append(f"| {row['codex_word_id']} | {row['domain']} | {row['selected_word_de']} | {row['used_units']} | {row['primary_anchor']} |")
    sheet.extend(["", "## Acht Astro-Regeln", ""])
    for row in astro_rules:
        sheet.append(f"{row['diagram_order']}. **{row['primitive_id']}** — {row['instruction_de']}")
    sheet.extend(["", "## Zwölf Prosa-Schreibregeln", ""])
    for row in rules:
        sheet.append(f"{row['rule_order']}. **{row['rule_id']}** — {row['instruction_de']}")
    (OUT / "NINETY_FIFTH_ONE_SHEET_CODEBOOK.md").write_text("\n".join(sheet).rstrip() + "\n", encoding="utf-8")

    mode_counts = Counter(row["compiler_mode"] for row in coverage)
    anchor_counts = Counter(row["primary_anchor"] for row in word_rows)
    report = [
        "# Fünfundneunzigste Werkstattrunde: kompaktes Gesamtcodebuch", "",
        "## Ergebnis", "",
        "One reference now contains the twenty prose primitives, forty-three card/root",
        "entries, forty-four source words, twelve prose rules and eight Astro rules.",
        "The complete 776-row coverage assigns 381 groups to combinatorial prose and 395",
        "to local Astro nomenclators.", "",
        "The sheet is deliberately asymmetric. A source word can come from a recurring",
        "card, a visible owner, a function class or a local nomenclator. It is not silently",
        "promoted to a phonetic word. This preserves the practical mixed system: productive",
        "abbreviations plus learned whole cards plus source-program words.", "",
        "Only the fixed ten pages were used; f84 and f84r remained sealed.",
    ]
    (OUT / "NINETY_FIFTH_EDITION_REPORT.md").write_text("\n".join(report) + "\n", encoding="utf-8")

    summary = {
        "status": "CONSISTENT", "prose_primitives": len(primitive_rows),
        "card_entries": len(card_rows), "source_words": len(word_rows),
        "prose_rules": len(rules), "astro_rules": len(astro_rules),
        "coverage_rows": len(coverage), "compiler_modes": dict(mode_counts),
        "source_anchor_counts": dict(anchor_counts),
    }
    (OUT / "BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
