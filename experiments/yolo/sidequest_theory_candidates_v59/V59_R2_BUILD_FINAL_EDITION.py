#!/usr/bin/env python3
"""Build the final R2 V59 ledgers from already selected, fixed-page artifacts.

This is a sidequest publication helper, not a decipherment runner.  All row
sources that carry page selectors are materialized through the guarded
``vmanus-exp query-tsv`` interface before any non-selector column is parsed.
"""

from __future__ import annotations

import csv
import io
import json
import subprocess
from collections import Counter
from pathlib import Path


OUT_DIR = Path(__file__).resolve().parent
ROOT = OUT_DIR.parents[2]

V49 = ROOT / "experiments/yolo/sidequest_theory_candidates_v49"
V22 = ROOT / "experiments/yolo/sidequest_theory_candidates_v22"

PROSE_PAGES = ("f10r", "f11r", "f55v", "f56r", "f81v", "f82r", "f83r")
ASTRO_PAGES = ("f67r2", "f68r1", "f69v")

FORMAL = {
    "ok": ("SETZEN", "FORMAL_CONTROL_OPERATOR"),
    "ot": ("MARKIEREN", "FORMAL_CONTROL_OPERATOR"),
    "l": ("VERKNUEPFEN", "FORMAL_CONTROL_OPERATOR"),
}
WEAK_HOST = {
    "al": ("AN?", "EXPLORATORY_WEAK_HOST_RELATION"),
    "or": ("BEREITUNG?", "EXPLORATORY_WEAK_WHOLE_HOST_MNEMONIC"),
    "chey": ("TEIL?", "EXPLORATORY_WEAK_WHOLE_HOST_MNEMONIC"),
}
EXACT = {
    "aiin": ("MASS?", "EXPLORATORY_EXACT_CARD_MNEMONIC"),
    "ey": ("KLAR?", "EXPOSED_EXACT_CARD_MNEMONIC_TWO_OF_FOUR_ROLES"),
    "oky": ("VERWENDEN?", "EXPLORATORY_EXACT_CARD_MNEMONIC"),
    "lche": ("ABLASSEN?", "CLOSE_CONFOUNDED_EXACT_CARD_MNEMONIC"),
    "oke": ("SPUELEN?", "CLOSE_CONFOUNDED_EXACT_CARD_MNEMONIC"),
    "cthy": ("BEREIT?", "EXPLORATORY_EXACT_CARD_MNEMONIC"),
    "okeey": ("WARM?", "EXPLORATORY_EXACT_CARD_MNEMONIC"),
    "olor": ("ZUVOR?", "EXPOSED_EXACT_CARD_MNEMONIC_TWO_EVENTS"),
}

UNIT_BY_RECORD = {
    ("f10r", "1"): "H1",
    ("f10r", "2"): "H2",
    ("f11r", "1"): "H3",
    ("f55v", "1"): "H4",
    ("f56r", "1"): "H5",
    ("f81v", "1"): "B1",
    ("f82r", "1"): "B2",
    ("f83r", "1"): "B3",
    ("f83r", "2"): "B4",
    ("f83r", "3"): "B5",
    ("f83r", "4"): "B6",
}
UNIT_BY_ASTRO_PAGE = {"f67r2": "A1", "f68r1": "A2", "f69v": "A3"}

OWNER_BY_UNIT = {
    "H1": "PICTURED_SKABIOSA_OR_DEVILS_BIT_LIKE_PLANT__IMAGE_HYPOTHESIS",
    "H2": "SAME_PICTURED_F10R_PLANT__RECORD_CONTINUITY_HYPOTHESIS",
    "H3": "PICTURED_SMALL_SHADE_PLANT__VIOLET_LEAD",
    "H4": "PICTURED_BROAD_LEAF_HERB__ALLIUM_OR_PLANTAIN",
    "H5": "PICTURED_GLANDULAR_WETLAND_HERB__SUNDEW_LEAD",
    "B1": "PICTURED_LOWER_BASIN_AND_RUNS",
    "B2": "PICTURED_FIGURE_BASIN_OR_COMPONENT_STATION",
    "B3": "PICTURED_MULTISTAGE_BASIN_RUN_AND_FIGURE_SYSTEM",
    "B4": "PICTURED_WARM_FOLLOWUP_RUN_OR_BODY_STATION",
    "B5": "PICTURED_SHORT_TRANSFER_PATH",
    "B6": "PICTURED_OPENING_AND_TARGET_STATION",
}


def guarded_rows(path: Path, selector: str, allow: tuple[str, ...], columns: list[str], expected: int):
    cmd = [
        str(ROOT / "vmanus-exp"),
        "query-tsv",
        str(path),
        "--selector",
        selector,
    ]
    for value in allow:
        cmd.extend(["--allow", value])
    cmd.extend(["--columns", ",".join(columns), "--forbid-prefix", "f84"])
    proc = subprocess.run(cmd, cwd=ROOT, check=True, capture_output=True, text=True)
    stdout_lines = proc.stdout.splitlines()
    stderr_lines = proc.stderr.splitlines()
    stat_lines = [line for line in stderr_lines + stdout_lines if line.startswith("GUARD_STATS ")]
    if len(stat_lines) != 1:
        raise RuntimeError(f"missing guard statistics for {path}")
    stats = json.loads(stat_lines[0][len("GUARD_STATS ") :])
    if stats["selected"] != expected or stats["skipped_forbidden"] != 0:
        raise RuntimeError(f"guard mismatch for {path}: {stats}")
    data_lines = [line for line in stdout_lines if not line.startswith("GUARD_STATS ")]
    return list(csv.DictReader(io.StringIO("\n".join(data_lines) + "\n"), delimiter="\t")), stats


def direct_rows(path: Path):
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, fieldnames: list[str], rows: list[dict[str, str]]):
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def selection(page_host: str):
    if page_host in FORMAL:
        value, status = FORMAL[page_host]
        return "FORMAL_CONTROL", value, status, value, "", ""
    if page_host in WEAK_HOST:
        value, status = WEAK_HOST[page_host]
        return "WEAK_HOST_MNEMONIC", value, status, "", value, ""
    if page_host in EXACT:
        value, status = EXACT[page_host]
        return "EXACT_CARD_MNEMONIC", value, status, "", "", value
    return "UNKNOWN_EXEMPLAR_TAIL", "UNKNOWN", "UNKNOWN_EXEMPLAR_TAIL", "", "", ""


def tier_a_prompt(surface: str, formal_formula: str):
    if surface == "daiin":
        return "VORGABEPARAMETER?"
    if formal_formula == "SET(<ARG_AIIN>)":
        return "STANDARDSLOT_SETZEN"
    if formal_formula == "SET(<ARG_AL>)":
        return "LOKALEN_RELATIONSSLOT_SETZEN"
    if formal_formula == "FRAME_O(LINK)":
        return "AKTIVEN_ARBEITSSTAND_VERKNUEPFEN"
    return ""


def update_atomic_sequence(raw: str):
    replace = {
        "SETZEN": "SETZEN",
        "MARKIEREN": "MARKIEREN",
        "VERKNÜPFEN": "VERKNUEPFEN",
        "VERKNUEPFEN": "VERKNUEPFEN",
        "ZU": "AN?",
        "BIS": "UNKNOWN",
        "ANSATZ": "BEREITUNG?",
        "ANTEIL": "TEIL?",
        "MASS": "MASS?",
        "FERTIG": "KLAR?",
        "NUTZEN": "VERWENDEN?",
        "ABLASS": "ABLASSEN?",
        "SPÜLEN": "SPUELEN?",
        "BEREIT": "BEREIT?",
        "LAUWARM": "WARM?",
        "VERBINDUNG": "UNKNOWN",
        "VORIGES": "ZUVOR?",
        "UNBEKANNT": "UNKNOWN",
    }
    return [replace.get(token.strip(), token.strip()) for token in raw.split("|")]


def main():
    prose_columns = [
        "page",
        "locus",
        "record",
        "event_index",
        "surface",
        "joint_tuple_id",
        "page_host",
        "formal_formula",
        "atomic_working_value_German",
        "atomic_status",
        "complete_default_German",
    ]
    field_columns = [
        "page",
        "record",
        "locus",
        "field_ordinal",
        "event_count",
        "surface_sequence",
        "formal_sequence",
        "atomic_working_sequence_German",
        "complete_creative_translation_German",
    ]
    astro_columns = [
        "page",
        "locus",
        "record",
        "line",
        "event_index",
        "surface",
        "exact_tuple_id",
        "default_English",
        "source_class",
        "confidence",
        "inheritance_context_rule",
        "ledger_scope",
        "source_event_serial",
    ]

    prose, prose_guard = guarded_rows(
        V49 / "V49_SELECTED_381_EVENT_INTERLINEAR.tsv",
        "page",
        PROSE_PAGES,
        prose_columns,
        381,
    )
    fields, field_guard = guarded_rows(
        V49 / "V49_SELECTED_135_FIELD_TRANSLATION.tsv",
        "page",
        PROSE_PAGES,
        field_columns,
        135,
    )
    astro, astro_guard = guarded_rows(
        V22 / "V22_SELECTED_COMPLETE_TRANSLATION_LEDGER.tsv",
        "page",
        ASTRO_PAGES,
        astro_columns,
        395,
    )
    dictionary = direct_rows(V49 / "V49_SELECTED_173_CARD_DICTIONARY.tsv")
    if len(dictionary) != 173:
        raise RuntimeError(f"dictionary rows: {len(dictionary)} != 173")

    occurrence_count = Counter(row["joint_tuple_id"] for row in prose)
    dictionary_out = []
    dictionary_by_id = {}
    for row in dictionary:
        layer, value, status, formal, weak, exact = selection(row["page_host"])
        out = {
            "joint_tuple_id": row["joint_tuple_id"],
            "page_host": row["page_host"],
            "surface_examples": row["surface_examples"],
            "formal_formula": row["formal_formula"],
            "selected_layer": layer,
            "selected_working_value_German": value,
            "formal_control_German": formal,
            "weak_host_mnemonic_German": weak,
            "exact_card_mnemonic_German": exact,
            "atomic_selection_status": status,
            "strict_tier_a_prompt_scope": (
                "EXACT_SURFACE_DAIIN=>VORGABEPARAMETER?"
                if row["page_host"] == "aiin"
                else tier_a_prompt("", row["formal_formula"])
            ),
            "unknown_exemplar_tail_status": "YES" if layer == "UNKNOWN_EXEMPLAR_TAIL" else "NO",
            "local_source_expansion_German": row["complete_default_German"],
            "local_source_expansion_status": "CONTEXTUAL_SOURCE_DEFAULT_NOT_ATOMIC_READING",
            "image_supplied_owner_status": "NOT_STORED_IN_CARD__BIND_AT_EVENT_UNIT",
            "fixed_occurrences": str(occurrence_count[row["joint_tuple_id"]]),
        }
        dictionary_out.append(out)
        dictionary_by_id[row["joint_tuple_id"]] = out

    dictionary_fields = list(dictionary_out[0])
    write_tsv(OUT_DIR / "V59_R2_FINAL_DICTIONARY.tsv", dictionary_fields, dictionary_out)

    event_out = []
    named_events = 0
    unknown_events = 0
    tier_a_events = 0
    for row in prose:
        unit = UNIT_BY_RECORD[(row["page"], row["record"])]
        card = dictionary_by_id[row["joint_tuple_id"]]
        strict_prompt = tier_a_prompt(row["surface"], row["formal_formula"])
        tier_a_events += int(bool(strict_prompt))
        is_unknown = card["selected_layer"] == "UNKNOWN_EXEMPLAR_TAIL"
        named_events += int(not is_unknown)
        unknown_events += int(is_unknown)
        event_out.append(
            {
                "page": row["page"],
                "locus": row["locus"],
                "record": row["record"],
                "unit_id": unit,
                "event_index": row["event_index"],
                "surface": row["surface"],
                "joint_tuple_id": row["joint_tuple_id"],
                "page_host": row["page_host"],
                "formal_formula": row["formal_formula"],
                "selected_layer": card["selected_layer"],
                "selected_working_value_German": card["selected_working_value_German"],
                "atomic_selection_status": card["atomic_selection_status"],
                "strict_tier_a_control_prompt": strict_prompt,
                "image_supplied_owner": OWNER_BY_UNIT[unit],
                "local_source_expansion_German": row["complete_default_German"],
                "default_status": (
                    "UNKNOWN_EXEMPLAR_TAIL_WITH_CONTEXTUAL_SOURCE_DEFAULT"
                    if is_unknown
                    else f"{card['selected_layer']}_WITH_CONTEXTUAL_SOURCE_DEFAULT"
                ),
                "source_expansion_authority": "V53_OR_V54_UNIT_DEFAULT_SUPERSEDES_EVENT_FLUENCY",
                "rule": "SHORT_CARD_NEVER_INHERITS_THE_SENTENCE_SIZED_LOCAL_EXPANSION",
            }
        )
    write_tsv(OUT_DIR / "V59_R2_381_EVENT_INTERLINEAR.tsv", list(event_out[0]), event_out)

    host_tokens = {"SETZEN", "MARKIEREN", "VERKNUEPFEN", "AN?", "BEREITUNG?", "TEIL?"}
    exact_tokens = {"MASS?", "KLAR?", "VERWENDEN?", "ABLASSEN?", "SPUELEN?", "BEREIT?", "WARM?", "ZUVOR?"}
    field_out = []
    field_pattern_counts = Counter()
    closed_fields = 0
    unknown_field_events = 0
    tier_a_fields = 0
    for row in fields:
        unit = UNIT_BY_RECORD[(row["page"], row["record"])]
        tokens = update_atomic_sequence(row["atomic_working_sequence_German"])
        surfaces = row["surface_sequence"].split()
        formulas = [token.strip() for token in row["formal_sequence"].split("|")]
        if len(surfaces) != len(formulas) or len(surfaces) != int(row["event_count"]):
            raise RuntimeError(f"field sequence length mismatch at {row['page']} {row['locus']}")
        strict_prompts = [tier_a_prompt(surface, formula) for surface, formula in zip(surfaces, formulas)]
        tier_a_fields += int(any(strict_prompts))
        has_host = bool(set(tokens) & host_tokens)
        has_exact = bool(set(tokens) & exact_tokens)
        closed = "CLOSE(" in row["formal_sequence"] or "CLOSE_B3(" in row["formal_sequence"]
        closed_fields += int(closed)
        unknowns = tokens.count("UNKNOWN")
        unknown_field_events += unknowns
        if not has_host and not has_exact:
            pattern = "Q2_TERMINAL_OPAQUE" if closed else "Q1_OPEN_OPAQUE"
        elif has_host and not has_exact:
            pattern = "Q3_HOST_FRAME"
        elif has_exact and not has_host:
            pattern = "Q4_WHOLE_CARD"
        else:
            pattern = "Q5_MIXED_PARATACTIC"
        field_pattern_counts[pattern] += 1
        field_out.append(
            {
                "page": row["page"],
                "record": row["record"],
                "unit_id": unit,
                "locus": row["locus"],
                "field_ordinal": row["field_ordinal"],
                "event_count": row["event_count"],
                "surface_sequence": row["surface_sequence"],
                "formal_sequence": row["formal_sequence"],
                "field_envelope": "NONCLOSE_STAR_PLUS_OPTIONAL_FIELD_FINAL_TERMINAL",
                "field_status": "TERMINAL" if closed else "OPEN",
                "v52_pattern": pattern,
                "selected_anchor_sequence_German": " | ".join(tokens),
                "strict_tier_a_prompt_sequence": " | ".join(prompt or "-" for prompt in strict_prompts),
                "unknown_event_count": str(unknowns),
                "local_source_expansion_German": row["complete_creative_translation_German"],
                "local_expansion_status": "CREATIVE_WHOLE_FIELD_EXPANSION_NOT_COMPOSITIONAL_DECODING",
                "unsupported_nouns_reference": f"{unit}:SEE_V59_R2_FOURTEEN_UNIT_SOURCE_EDITION",
            }
        )
    write_tsv(OUT_DIR / "V59_R2_135_FIELD_EDITION.tsv", list(field_out[0]), field_out)

    astro_owner = {
        "f67r2": "DIAGRAM_POSITION_IN_7_12_CONFIGURATION_SELECTOR",
        "f68r1": "SPATIAL_LOCUS_IN_CENTRE_PLUS_28_CATALOGUE",
        "f69v": "ORDERED_LOCAL_RULE_SLOT_IN_28_CATALOGUE",
    }
    astro_status = {
        "f67r2": "LOCAL_IATROMEDICAL_SELECTOR_EXPANSION_NOT_GROUP_GLOSS",
        "f68r1": "LOCAL_STATION_CATALOGUE_EXPANSION_NOT_GROUP_GLOSS",
        "f69v": "LOCAL_REGIMEN_RULE_EXPANSION_NOT_GROUP_GLOSS",
    }
    astro_out = []
    for row in astro:
        astro_out.append(
            {
                "page": row["page"],
                "locus": row["locus"],
                "unit_id": UNIT_BY_ASTRO_PAGE[row["page"]],
                "record": row["record"],
                "line": row["line"],
                "event_index": row["event_index"],
                "surface": row["surface"],
                "local_exemplar_id": row["exact_tuple_id"],
                "image_or_position_owner": astro_owner[row["page"]],
                "source_level_default_English": row["default_English"],
                "default_status": astro_status[row["page"]],
                "semantic_group_status": "UNKNOWN_LOCAL_EXEMPLAR_LABEL",
                "legacy_source_class": row["source_class"],
                "legacy_confidence": row["confidence"],
                "inheritance_context_rule": row["inheritance_context_rule"],
                "prose_card_value_imported": "NO",
                "direct_f68r1_f69v_mapping": "NONE",
            }
        )
    write_tsv(OUT_DIR / "V59_R2_395_ASTRO_GROUP_LEDGER.tsv", list(astro_out[0]), astro_out)

    unit_rows = direct_rows(OUT_DIR / "V59_R2_FOURTEEN_UNIT_SOURCE_EDITION.tsv")
    unit_register_counts = Counter(row["register"] for row in unit_rows)
    page_event_counts = Counter(row["page"] for row in prose)
    page_astro_counts = Counter(row["page"] for row in astro)
    unique_loci = {page: len({row["locus"] for row in astro if row["page"] == page}) for page in ASTRO_PAGES}
    dictionary_layer_types = Counter(row["selected_layer"] for row in dictionary_out)
    dictionary_layer_events = Counter()
    for row in dictionary_out:
        dictionary_layer_events[row["selected_layer"]] += int(row["fixed_occurrences"])
    expected_field_patterns = {
        "Q1_OPEN_OPAQUE": 8,
        "Q2_TERMINAL_OPAQUE": 44,
        "Q3_HOST_FRAME": 33,
        "Q4_WHOLE_CARD": 26,
        "Q5_MIXED_PARATACTIC": 24,
    }
    validation = {
        "role": "R2_HISTORICAL_MEDICAL_HERBAL_SCRIBE",
        "status": "COMPLETE_SOURCE_LEVEL_WORKING_EDITION_NOT_DECIPHERMENT",
        "counts": {
            "allowed_pages": len(PROSE_PAGES) + len(ASTRO_PAGES),
            "dictionary_cards": len(dictionary_out),
            "prose_events": len(event_out),
            "prose_records": len(UNIT_BY_RECORD),
            "selected_anchor_events": named_events,
            "strict_tier_a_events": tier_a_events,
            "unknown_exemplar_tail_events": unknown_events,
            "prose_fields": len(field_out),
            "open_fields": len(field_out) - closed_fields,
            "terminal_fields": closed_fields,
            "unknown_field_event_sum": unknown_field_events,
            "astro_groups": len(astro_out),
            "astro_loci": sum(unique_loci.values()),
            "visible_groups_total": len(event_out) + len(astro_out),
            "source_units": len(unit_rows),
            "strict_tier_a_fields": tier_a_fields,
        },
        "expected": {
            "allowed_pages": 10,
            "dictionary_cards": 173,
            "prose_events": 381,
            "prose_records": 11,
            "selected_anchor_events": 145,
            "strict_tier_a_events": 45,
            "unknown_exemplar_tail_events": 236,
            "prose_fields": 135,
            "open_fields": 45,
            "terminal_fields": 90,
            "unknown_field_event_sum": 236,
            "astro_groups": 395,
            "astro_loci": 142,
            "visible_groups_total": 776,
            "source_units": 14,
            "strict_tier_a_fields": 35,
        },
        "page_event_counts": dict(sorted(page_event_counts.items())),
        "unit_register_counts": dict(sorted(unit_register_counts.items())),
        "page_astro_group_counts": dict(sorted(page_astro_counts.items())),
        "page_astro_locus_counts": unique_loci,
        "v52_field_pattern_counts": dict(sorted(field_pattern_counts.items())),
        "expected_v52_field_pattern_counts": expected_field_patterns,
        "dictionary_layer_type_counts": dict(sorted(dictionary_layer_types.items())),
        "dictionary_layer_event_counts": dict(sorted(dictionary_layer_events.items())),
        "guards": {
            "v49_event_query": prose_guard,
            "v49_field_query": field_guard,
            "v22_astro_query": astro_guard,
            "forbidden_prefix": "f84",
            "v59_sibling_files_read": 0,
            "new_voynich_pages_opened": 0,
            "f84_accessed": False,
            "f84r_accessed": False,
        },
        "semantic_rules": {
            "short_card_gets_sentence_gloss": False,
            "picture_owner_is_card_value": False,
            "astro_imports_prose_card_value": False,
            "direct_f68r1_f69v_mapping": "NONE",
            "confirmed_lexemes": 0,
            "confirmed_plaintext_clauses": 0,
        },
        "final_content_decision": "IATROMEDICAL_DEFAULT_WITH_DOMAIN_NEUTRAL_FORMAL_ARCHITECTURE_AND_COMPLETE_NONMEDICAL_RIVAL",
    }
    if validation["counts"] != validation["expected"]:
        raise RuntimeError(f"validation mismatch: {validation['counts']} != {validation['expected']}")
    if validation["v52_field_pattern_counts"] != expected_field_patterns:
        raise RuntimeError(
            f"field-pattern mismatch: {validation['v52_field_pattern_counts']} != {expected_field_patterns}"
        )
    with (OUT_DIR / "V59_R2_VALIDATION.json").open("w", encoding="utf-8") as handle:
        json.dump(validation, handle, ensure_ascii=False, indent=2, sort_keys=True)
        handle.write("\n")


if __name__ == "__main__":
    main()
