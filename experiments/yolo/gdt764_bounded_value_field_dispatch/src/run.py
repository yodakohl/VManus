#!/usr/bin/env python3
"""Dispatch bounded H1-X-daiin fields and recurrent ol amount orders."""

from __future__ import annotations

import argparse
import csv
import importlib.util
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Iterable

sys.dont_write_bytecode = True


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
BASE_REL = Path("experiments/yolo/gdt764_bounded_value_field_dispatch")
EXP = ROOT / BASE_REL
SRC = EXP / "src"
DEFAULT_ARTIFACTS = EXP / "artifacts"

G763_RUN_REL = Path("experiments/yolo/gdt763_h1_content_vs_record_discriminator/src/run.py")
G763_H1_REL = Path("experiments/yolo/gdt763_h1_content_vs_record_discriminator/artifacts/H1_199_OCCURRENCE_SEQUENCE_ATLAS.tsv")
G763_OL_REL = Path("experiments/yolo/gdt763_h1_content_vs_record_discriminator/artifacts/OL_16_SLOT_FUNCTION_ATLAS.tsv")
G762_OL_REL = Path("experiments/yolo/gdt762_moist_medium_candidate_discrimination/artifacts/OL_AMOUNT_EXPRESSION_CONTACT_ATLAS.tsv")
G760_QUANTITY_REL = Path("experiments/yolo/gdt760_quantity_bilateral_content_attachment/artifacts/QUANTITY_281_EXPRESSION_ATLAS.tsv")
G686_VALUE_REL = Path("experiments/yolo/gdt686_v59_dain_daiin_qodaiin_value_head_dispatch/artifacts/TARGET_955_VALUE_HEAD_CENSUS.tsv")
G711_REPAIR_REL = Path("experiments/yolo/gdt711_v84_active_weak_family_repair/artifacts/V84_181_WEAK_READING_REPAIR_CENSUS.tsv")
G755_HISTORY_REL = Path("experiments/yolo/gdt755_top24_historical_register_crosswalk/src/HISTORICAL_EXPRESSION_BANK.tsv")

TARGET_X = ("qoty", "dal", "qopchdy", "ofchy", "oteody", "chofol")
REPEATED_OL_PATTERNS = ("ol s aiin", "sain ol", "saiin ol", "or aiin ol")
OUTPUT_NAMES = (
    "X_254_EXACT_OCCURRENCE_ATLAS.tsv",
    "X_6_GLOBAL_ROLE_PROFILE.tsv",
    "X_DAIIN_9_EXACT_BIGRAM_ATLAS.tsv",
    "H1_X_DAIIN_5_BOUNDED_FIELD_ATLAS.tsv",
    "DAIIN_LOCAL_AXIS_DISPATCH_SUMMARY.tsv",
    "FIELD_GRAMMAR.tsv",
    "OL_RAW_EXACT_RECURRENCE_AUDIT.tsv",
    "OL_ORDER_ASSOCIATION_PROFILE.tsv",
    "OL_12_REPEAT_ORDER_ATLAS.tsv",
    "OL_REPEAT_ORDER_PROFILE.tsv",
    "OL_HYPOTHESIS_SCORECARD.tsv",
    "HISTORICAL_REGISTER_TEMPLATE_MAP.tsv",
    "BOUNDED_RENDERER_REVISION.tsv",
    "RESULT.json",
)
STATUS = (
    "PARTIAL__254_X_OCCURRENCES__9_EXACT_X_DAIIN_BIGRAMS__"
    "5_H1_X_DAIIN_FIELDS__1_STRONG_1_PROVISIONAL_3_OPEN_H1_AXES__"
    "QOTY_GRADE_III__OTEODY_STAGE_C1__DAL_MEASURE_VALUE_AMOUNT_C1__"
    "QOPCHDY_NOMINAL_OPEN__OFCHY_OPEN__"
    "15_RAW_12_EXACT_OL_ORDERS__HEAD8_OBJECT1_CONTEXT2_BILATERAL1__"
    "POSITIONAL_RECORD_GRAMMAR__ZERO_CONFIRMED_LEXEMES__NO_NEW_PAGE"
)


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load dependency: {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


g763 = load_module("gdt763_builder_for_gdt764", ROOT / G763_RUN_REL)


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: Iterable[dict[str, object]], fields: Iterable[str]) -> None:
    names = list(fields)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=names, delimiter="\t", lineterminator="\n", extrasaction="raise")
        writer.writeheader()
        for row in rows:
            writer.writerow({name: row.get(name, "") for name in names})


def compact(values: Iterable[str]) -> str:
    counts = Counter(values)
    return "|".join(f"{key}:{counts[key]}" for key in sorted(counts)) or "NONE"


def semantic_environment() -> dict[str, object]:
    training = read_tsv(ROOT / g763.G736_GRID_REL)
    held = read_tsv(ROOT / g763.G737_FORM_REL)
    quantity_rows = read_tsv(ROOT / G760_QUANTITY_REL)
    content_deck = read_tsv(ROOT / g763.G760_DECK_REL)
    state_rows = read_tsv(g763.g762.SRC / "STATE_PAIR_PRIORS.tsv")
    candidate_rows = read_tsv(g763.g762.SRC / "CANDIDATE_PRIORS.tsv")
    manual_rows = read_tsv(g763.SRC / "EXACT_WHOLE_FIELD_PRIORS.tsv")
    head_registry = g763.build_head_registry(training, held)
    amount_positions = g763.amount_position_map(quantity_rows)
    state_map, _, _ = g763.g762.state_maps(state_rows)
    meanings, sources, suspect, _, _ = g763.g762.semantic_inputs(state_rows, candidate_rows)
    context, line_meta, guard = g763.g762.g761.g760.g759.g758.g756.g755.g753.g752.g751.load_context()
    return {
        "context": context, "line_meta": line_meta, "guard": guard,
        "head_registry": head_registry, "amount_positions": amount_positions,
        "state_map": state_map, "content_map": {row["content_surface"]: row for row in content_deck},
        "manual": {row["surface"]: row for row in manual_rows}, "suspect": suspect,
        "meanings": meanings, "sources": sources,
    }


def slot(env: dict[str, object], locus: str, ordinal: int) -> dict[str, object]:
    return g763.slot_record(
        env["context"], locus, ordinal, env["head_registry"], env["amount_positions"],
        env["state_map"], env["content_map"], env["manual"], env["suspect"],
        env["meanings"], env["sources"],
    )


def build_x_occurrences(
    env: dict[str, object], priors: dict[str, dict[str, str]], h1_surfaces: set[str],
) -> list[dict[str, object]]:
    context = env["context"]
    line_meta = env["line_meta"]
    output: list[dict[str, object]] = []
    for locus, line in sorted(context.by_line.items()):
        for index, token in enumerate(line):
            surface = str(token["eva"])
            if surface not in priors or not context.exact[(locus, int(token["token_index"]))]:
                continue
            ordinal = index + 1
            record: dict[str, object] = {
                "x_occurrence_id": f"G764-X{len(output)+1:04d}", "surface": surface,
                "selected_field_type": priors[surface]["selected_field_type"],
                "portable_whole_de": priors[surface]["portable_whole_de"],
                "confidence": priors[surface]["confidence"], "page": str(token["page"]),
                "physical_folio": g763.physical_folio(str(token["page"])), "locus": locus,
                "section": str(token["section"]), "language": str(token["language"]),
                "hand": str(token["hand"]), "ordinal": ordinal, "line_token_count": len(line),
                "line_position": g763.line_position(ordinal, len(line)),
                "paragraph_start_line": line_meta[locus]["paragraph_start"],
                "paragraph_end_line": line_meta[locus]["paragraph_end"],
                "written_line_eva": " ".join(str(item["eva"]) for item in line),
                "component_export_credit": 0,
            }
            for label, offset in (("l2", -2), ("l1", -1), ("r1", 1), ("r2", 2)):
                item = slot(env, locus, ordinal + offset)
                for field in ("surface", "reader_exact", "status", "axes", "roles", "semantic_candidate_de"):
                    record[f"{label}_{field}"] = item[field]
            record["left_is_h1"] = int(str(record["l1_surface"]) in h1_surfaces and int(record["l1_reader_exact"]) == 1)
            record["right_is_exact_daiin"] = int(record["r1_surface"] == "daiin" and int(record["r1_reader_exact"]) == 1)
            output.append(record)
    return output


def build_x_profiles(
    occurrences: list[dict[str, object]], priors: dict[str, dict[str, str]], old_values: list[dict[str, str]],
) -> list[dict[str, object]]:
    output: list[dict[str, object]] = []
    for surface in TARGET_X:
        rows = [row for row in occurrences if row["surface"] == surface]
        old = [row for row in old_values if row["surface"] == "daiin" and row["left_surface"] == surface]
        prior = priors[surface]
        output.append({
            "surface": surface, "reader_exact_occurrences_current_guard": len(rows),
            "pages_current_guard": len({str(row["page"]) for row in rows}),
            "sections": compact(str(row["section"]) for row in rows),
            "line_positions": compact(str(row["line_position"]) for row in rows),
            "paragraph_start_occurrences": sum(str(row["paragraph_start_line"]) == "1" for row in rows),
            "exact_right_daiin_current_guard": sum(int(row["right_is_exact_daiin"]) for row in rows),
            "gdt686_left_of_daiin_all": len(old),
            "gdt686_left_of_daiin_reader_stable": sum(row["triple_reader_token_stable"] == "1" for row in old),
            "selected_field_type": prior["selected_field_type"], "portable_whole_de": prior["portable_whole_de"],
            "portable_x_daiin_de": prior["portable_x_daiin_de"], "confidence": prior["confidence"],
            "evidence_source": prior["evidence_source"], "evidence": prior["evidence"],
            "counterevidence": prior["counterevidence"], "confirmed_lexeme": 0,
            "component_export_credit": 0,
        })
    return output


def dispatch_for(field_type: str) -> tuple[str, str]:
    if field_type == "QUALITY_HEAD":
        return "QUALITY_GRADE_III", "vollständiger Qualitätskopf bestimmt die Gradachse"
    if field_type == "MATERIAL_MEASURE_HEAD":
        return "MATERIAL_MEASURE_VALUE_III", "vollständiger Rohstoff-/Messkopf begrenzt das Feld; Mengenachse bleibt C1-Rivale"
    if field_type == "NOMINAL_FIELD":
        return "NOMINAL_VALUE_III", "exakte Parallelstruktur sichert ein nominales Feld, aber keine Achse"
    if field_type == "RESULT_STAGE_HEAD":
        return "RESULT_STAGE_III", "vollständiger Ergebnis-/Zustandskopf bestimmt lokal eine Stufenachse"
    return "OPEN_VALUE_III", "keine unabhängige Achse; nur Wertzelle III"


def build_x_daiin(
    occurrences: list[dict[str, object]], priors: dict[str, dict[str, str]], old_values: list[dict[str, str]],
) -> list[dict[str, object]]:
    old_map = {(row["locus"], int(row["token_index"])): row for row in old_values if row["surface"] == "daiin"}
    output: list[dict[str, object]] = []
    for occurrence in occurrences:
        if not int(occurrence["right_is_exact_daiin"]):
            continue
        prior = priors[str(occurrence["surface"])]
        dispatch, basis = dispatch_for(prior["selected_field_type"])
        value_ordinal = int(occurrence["ordinal"]) + 1
        old = old_map[(str(occurrence["locus"]), value_ordinal)]
        output.append({
            "x_daiin_id": f"G764-XD{len(output)+1:02d}", "page": occurrence["page"],
            "physical_folio": occurrence["physical_folio"], "locus": occurrence["locus"],
            "section": occurrence["section"], "hand": occurrence["hand"],
            "x_ordinal": occurrence["ordinal"], "x_surface": occurrence["surface"],
            "x_selected_field_type": prior["selected_field_type"], "daiin_ordinal": value_ordinal,
            "daiin_fixed_value": "III", "selected_local_dispatch": dispatch,
            "dispatch_basis": basis, "portable_phrase_de": prior["portable_x_daiin_de"],
            "aggressive_c1_phrase_de": prior["aggressive_c1_x_daiin_de"],
            "phrase_confidence": prior["confidence"], "left_surface": occurrence["l1_surface"],
            "left_is_h1": occurrence["left_is_h1"], "right_surface": occurrence["r2_surface"],
            "right_roles": occurrence["r2_roles"], "previous_gdt686_context_mode": old["global_context_mode"],
            "previous_gdt686_axis": old["global_axis"],
            "previous_gdt686_renderer_de": old["contextual_renderer_de"],
            "written_pattern_eva": f"{occurrence['surface']} daiin",
            "written_line_eva": occurrence["written_line_eva"], "confirmed_plaintext": 0,
            "component_export_credit": 0,
        })
    return output


def build_h1_fields(
    h1_rows: list[dict[str, str]], xd_rows: list[dict[str, object]], priors: dict[str, dict[str, str]],
) -> list[dict[str, object]]:
    xd_map = {(str(row["locus"]), int(row["x_ordinal"])): row for row in xd_rows}
    output: list[dict[str, object]] = []
    for row in h1_rows:
        if row["gapped_x_daiin"] != "1":
            continue
        pair = xd_map[(row["locus"], int(row["ordinal"]) + 1)]
        prior = priors[str(pair["x_surface"])]
        output.append({
            "h1_field_id": f"G764-HF{len(output)+1:02d}", "page": row["page"], "locus": row["locus"],
            "section": row["section"], "hand": row["hand"], "h1_surface": row["surface"],
            "h1_body": row["body"], "h1_record_role": row["record_role"],
            "h1_body_role_de": row["body_role_de"], "x_surface": pair["x_surface"],
            "daiin_fixed_value": "III", "selected_local_dispatch": pair["selected_local_dispatch"],
            "portable_bounded_field_de": f"{row['body_role_de']}: {prior['portable_x_daiin_de']}",
            "aggressive_c1_bounded_field_de": f"{row['body_role_de']}: {prior['aggressive_c1_x_daiin_de']}",
            "field_confidence": prior["confidence"], "x_independent_role_evidence": prior["evidence_source"],
            "x_counterevidence": prior["counterevidence"], "following_surface": pair["right_surface"],
            "following_roles": pair["right_roles"], "paragraph_start_line": row["paragraph_start_line"],
            "paragraph_end_line": row["paragraph_end_line"],
            "written_pattern_eva": f"{row['surface']} {pair['x_surface']} daiin",
            "written_line_eva": row["written_line_eva"], "confirmed_plaintext": 0,
            "component_export_credit": 0,
        })
    return output


def build_axis_summary(xd_rows: list[dict[str, object]]) -> list[dict[str, object]]:
    grouped: defaultdict[str, list[dict[str, object]]] = defaultdict(list)
    for row in xd_rows:
        grouped[str(row["selected_local_dispatch"])].append(row)
    rules = {
        "QUALITY_GRADE_III": "Qualitätskopf + daiin → Grad III",
        "MATERIAL_MEASURE_VALUE_III": "Stoff-/Messkopf + daiin → Wert III; Menge nur C1",
        "NOMINAL_VALUE_III": "nominaler Feldkopf + daiin → Wert III; Achse offen",
        "RESULT_STAGE_III": "Ergebnis-/Zustandskopf + daiin → Stufe III",
        "OPEN_VALUE_III": "opaker Kopf + daiin → Wert III",
    }
    return [{
        "local_dispatch": dispatch, "exact_x_daiin_pairs": len(grouped[dispatch]),
        "h1_x_daiin_pairs": sum(int(row["left_is_h1"]) for row in grouped[dispatch]),
        "x_surfaces": "|".join(sorted({str(row["x_surface"]) for row in grouped[dispatch]})) or "NONE",
        "portable_rule": rules[dispatch], "global_daiin_meaning_selected": 0,
        "component_export_credit": 0,
    } for dispatch in rules]


def build_field_grammar() -> list[dict[str, object]]:
    return [
        {"precedence": 1, "rule_id": "G764-FG1", "pattern": "H1 X daiin", "dispatch": "H1 scopes a record field; it does not determine the daiin axis", "renderer_de": "Eintrags-/Formklasse: X-Feld III", "scope": "FIVE_EXACT_H1_TRIPLES", "component_export_credit": 0},
        {"precedence": 2, "rule_id": "G764-FG2", "pattern": "QUALITY_X daiin", "dispatch": "complete X whole selects grade", "renderer_de": "Qualität, Grad III", "scope": "QOTY_EXACT_BIGRAMS", "component_export_credit": 0},
        {"precedence": 3, "rule_id": "G764-FG3", "pattern": "MATERIAL_MEASURE_X daiin", "dispatch": "complete X whole bounds a measured-material field; axis remains open", "renderer_de": "Stoff-/Messkopf, Wert III; Menge als C1-Rivale", "scope": "DAL_EXACT_BIGRAMS", "component_export_credit": 0},
        {"precedence": 4, "rule_id": "G764-FG4", "pattern": "NOMINAL_X daiin", "dispatch": "parallel field structure selects nominal syntax, not an axis", "renderer_de": "nominales X-Feld, Wert III", "scope": "QOPCHDY_EXACT_BIGRAM", "component_export_credit": 0},
        {"precedence": 5, "rule_id": "G764-FG5", "pattern": "RESULT_STAGE_X daiin", "dispatch": "weak complete-whole prior provisionally selects result stage", "renderer_de": "Zubereitungs-/Ergebnisfeld, Stufe III (C1)", "scope": "OTEODY_EXACT_BIGRAM", "component_export_credit": 0},
        {"precedence": 6, "rule_id": "G764-FG6", "pattern": "OPEN_X daiin", "dispatch": "axis remains open", "renderer_de": "X-Feld, Wert III", "scope": "OFCHY_OR_CHOFOL_EXACT_BIGRAMS", "component_export_credit": 0},
        {"precedence": 7, "rule_id": "G764-FG7", "pattern": "s|or + value", "dispatch": "the complete amount formula, not bare daiin, selects amount", "renderer_de": "Drachmen-/Portionsformel mit austauschbarer Einheit", "scope": "GDT759_GDT760_LICENSED_FORMULAS", "component_export_credit": 0},
    ]


def build_ol_raw_audit(env: dict[str, object]) -> list[dict[str, object]]:
    context = env["context"]
    token_patterns = {pattern: pattern.split() for pattern in REPEATED_OL_PATTERNS}
    output: list[dict[str, object]] = []
    for pattern, wanted in token_patterns.items():
        hits: list[tuple[str, str]] = []
        for locus, line in context.by_line.items():
            for start in range(0, len(line) - len(wanted) + 1):
                window = line[start:start + len(wanted)]
                if [str(token["eva"]) for token in window] != wanted:
                    continue
                flags = "".join("1" if context.exact[(locus, int(token["token_index"]))] else "0" for token in window)
                hits.append((locus, flags))
        exact = [(locus, flags) for locus, flags in hits if set(flags) == {"1"}]
        excluded = [(locus, flags) for locus, flags in hits if set(flags) != {"1"}]
        output.append({
            "pattern_eva": pattern, "raw_contiguous_occurrences": len(hits),
            "all_reader_exact_occurrences": len(exact),
            "exact_loci": "|".join(locus for locus, _ in exact),
            "excluded_loci_and_flags": "|".join(f"{locus}:{flags}" for locus, flags in excluded) or "NONE",
            "exclusion_rule": "EVERY_TOKEN_MUST_BE_READER_EXACT",
            "component_export_credit": 0,
        })
    return output


def build_ol_association(quantities: list[dict[str, str]]) -> list[dict[str, object]]:
    specs = (("ol s aiin", "s aiin", "left"), ("sain ol", "sain", "right"), ("saiin ol", "saiin", "right"), ("or aiin ol", "or aiin", "right"))
    output: list[dict[str, object]] = []
    for display, expression, side in specs:
        def eligible(row: dict[str, str]) -> bool:
            return row[f"{side}_reader_exact"] == "1" and row[f"{side}_source_composed_quarantined"] == "0" and row[f"{side}_axis_class"] != "EDGE_OR_NONEXACT"

        target = [row for row in quantities if row["source_expression_eva"] == expression and eligible(row)]
        control = [row for row in quantities if row["source_expression_eva"] != expression and eligible(row)]
        a = sum(row[f"{side}_surface"] == "ol" for row in target)
        b = len(target) - a
        c = sum(row[f"{side}_surface"] == "ol" for row in control)
        d = len(control) - c
        target_rate = a / len(target)
        control_rate = c / len(control)
        output.append({
            "pattern_eva": display, "tested_neighbor_side": side.upper(),
            "ol_in_pattern_slot": a, "eligible_pattern_slots": len(target),
            "ol_in_other_slots": c, "eligible_other_slots": len(control),
            "target_rate": g763.fixed(target_rate), "control_rate": g763.fixed(control_rate),
            "lift": g763.fixed(target_rate / control_rate),
            "odds_ratio": g763.odds_ratio(a, b, c, d),
            "fisher_two_sided_descriptive": g763.fixed(g763.fisher_two_sided(a, b, c, d)),
            "interpretation": "DISTINCTIVE_CONSTRUCTION" if display == "ol s aiin" else "RECURRENT_ORDER_LOCAL_CONTEXT_REQUIRED",
            "component_export_credit": 0,
        })
    return output


def safe_amount_label(pattern: str) -> str:
    return {"s aiin": "Menge III", "sain": "Menge II", "saiin": "Menge III", "or aiin": "Portionsfeld III"}[pattern]


def ol_renderers(row: dict[str, str]) -> tuple[str, str]:
    role = row["selected_slot_function"]
    safe = safe_amount_label(row["amount_expression_eva"])
    concrete = row["amount_candidate_de"]
    if role == "OBJECT_PATIENT":
        return f"Ansatz/Zubereitung, {safe}; Prozess-/Abschlussfeld", f"{concrete} Ansatz/Zubereitung; abseihen/trennen"
    if role == "BILATERAL_AMBIGUOUS":
        return f"ol-Feld — {safe} — ol-Feld; Seitenrollen offen", f"ol-Feld — {concrete} — ol-Feld; Seitenrollen offen"
    if role == "CONTEXT_SECOND_FIELD":
        return f"{safe}; bevorzugter linker Kopf {row['preferred_competitor_surface']}; danach ol-Nebenfeld", f"{concrete}; bevorzugter linker Kopf {row['preferred_competitor_surface']}; danach ol-Nebenfeld"
    if row["expression_line_position"] == "FIRST":
        return f"{safe} — Ansatz/Zubereitung", f"{concrete} Ansatz/Zubereitung"
    if "L" in row["ol_sides_relative_to_amount"].split("|"):
        return f"Ansatz/Zubereitung: {safe}", f"Ansatz/Zubereitung: {concrete}"
    return f"{safe} — Ansatz/Zubereitung", f"{concrete} Ansatz/Zubereitung"


def build_ol_orders(
    ol_rows: list[dict[str, str]], contacts: list[dict[str, str]], quantities: list[dict[str, str]],
) -> list[dict[str, object]]:
    contact_map = {row["ol_amount_contact_id"]: row for row in contacts}
    quantity_map = {row["expression_id"]: row for row in quantities}
    output: list[dict[str, object]] = []
    for row in ol_rows:
        pattern = row["amount_expression_eva"]
        if pattern not in {"s aiin", "sain", "saiin", "or aiin"}:
            continue
        contact = contact_map[row["source_contact_id"]]
        quantity = quantity_map[row["expression_id"]]
        sides = row["ol_sides_relative_to_amount"]
        written_pattern = "ol " + pattern if "L" in sides.split("|") else pattern + " ol"
        if sides == "L|R":
            written_pattern = "ol " + pattern + " ol"
        evolved = dict(row)
        evolution = "UNCHANGED_FROM_GDT763"
        if row["source_contact_id"] == "G762-A09":
            evolved["selected_slot_function"] = "HEAD"
            evolved["dispatch_basis"] = "vierfach wiederholtes sain ol setzt den rechten Ganzwortkopf; exakter linker Kandidat bleibt Kontextrivale"
            evolution = "A09_CONTEXT_TO_HEAD_WITH_LEFT_CONTEXT_RIVAL"
        portable_renderer, aggressive_renderer = ol_renderers(evolved)
        output.append({
            "ol_repeat_id": f"G764-OR{len(output)+1:02d}", "source_ol_slot_id": row["ol_slot_id"],
            "page": row["page"], "physical_folio": row["physical_folio"], "locus": row["locus"],
            "section": contact["section"], "hand": contact["hand"], "pattern_eva": written_pattern,
            "amount_expression_eva": pattern, "amount_candidate_de": row["amount_candidate_de"],
            "amount_rivals_de": contact["amount_rivals_de"], "amount_mode": row["amount_mode"],
            "expression_line_position": row["expression_line_position"], "ol_sides_relative_to_amount": sides,
            "position_expected_side": row["position_expected_side"],
            "gdt763_slot_function": row["selected_slot_function"],
            "selected_slot_function": evolved["selected_slot_function"],
            "gdt764_role_evolution": evolution, "dispatch_basis": evolved["dispatch_basis"],
            "preferred_competitor_surface": row["preferred_competitor_surface"],
            "preferred_competitor_reader_exact": row["preferred_competitor_reader_exact"],
            "outside_span_surface": row["outside_span_surface"],
            "outside_span_axis_class": row["outside_span_axis_class"],
            "portable_renderer_de": portable_renderer, "aggressive_c1_renderer_de": aggressive_renderer,
            "specific_oil_identity": 0, "literal_process_selected": 0, "confirmed_plaintext": 0,
            "written_line_eva": quantity["written_line_eva"], "component_export_credit": 0,
        })
    return output


def build_ol_profile(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    renderers = {
        "ol s aiin": "Ansatz/Zubereitung: drei lokale Maße",
        "sain ol": "zwei lokale Maße Ansatz/Zubereitung",
        "saiin ol": "drei lokale Maße Ansatz/Zubereitung",
        "or aiin ol": "drei Portionen Ansatz/Zubereitung",
    }
    output: list[dict[str, object]] = []
    for pattern in REPEATED_OL_PATTERNS:
        selected = [row for row in rows if row["pattern_eva"] == pattern or (pattern == "ol s aiin" and row["pattern_eva"] == "ol s aiin ol")]
        output.append({
            "pattern_eva": pattern, "positions": len(selected), "pages": len({str(row["page"]) for row in selected}),
            "slot_functions": compact(str(row["selected_slot_function"]) for row in selected),
            "line_positions": compact(str(row["expression_line_position"]) for row in selected),
            "selected_compositional_role": "CONTENT_PLUS_AMOUNT_ORDER_VARIANT",
            "portable_renderer_de": renderers[pattern],
            "unit_lead_de": "Drachmen" if pattern != "or aiin ol" else "Portionen",
            "unit_identity_fixed": 0, "oil_identity_fixed": 0, "component_export_credit": 0,
        })
    return output


def build_history(rows: list[dict[str, str]]) -> list[dict[str, object]]:
    role_map = {
        "E004": "ingredient/preparation + unit + number",
        "E006": "equal-amount marker + amount field",
        "E010": "quality + third degree",
        "E011": "cold quality + degree",
        "E028": "oil as learned content noun",
    }
    output: list[dict[str, object]] = []
    for row in rows:
        if row["candidate_id"] not in role_map:
            continue
        output.append({
            "historical_candidate_id": row["candidate_id"], "attested_form": row["attested_form"],
            "working_gloss_de": row["working_gloss_de"], "template_role": role_map[row["candidate_id"]],
            "locator": row["locator"], "attestation_scope": row["attestation_scope"],
            "use_in_gdt764": "ARCHITECTURE_ONLY_NO_TARGET_SPELLING",
            "target_mapping_credit": 0, "component_export_credit": 0,
        })
    return output


def build_renderer_revision(h1_fields: list[dict[str, object]], ol_rows: list[dict[str, object]]) -> list[dict[str, object]]:
    output: list[dict[str, object]] = []
    for row in h1_fields:
        output.append({
            "revision_id": f"G764-R{len(output)+1:02d}", "kind": "H1_BOUNDED_FIELD",
            "locus": row["locus"], "written_span_eva": row["written_pattern_eva"],
            "old_renderer_de": "H1-Eintrag; X-Feld; Wert III",
            "new_portable_renderer_de": row["portable_bounded_field_de"],
            "new_aggressive_c1_renderer_de": row["aggressive_c1_bounded_field_de"],
            "evidence": row["x_independent_role_evidence"], "confirmed_plaintext": 0,
        })
    for row in ol_rows:
        output.append({
            "revision_id": f"G764-R{len(output)+1:02d}", "kind": "OL_AMOUNT_ORDER",
            "locus": row["locus"], "written_span_eva": row["pattern_eva"],
            "old_renderer_de": "mengenfähiger Zubereitungs-/Inhaltskopf",
            "new_portable_renderer_de": row["portable_renderer_de"],
            "new_aggressive_c1_renderer_de": row["aggressive_c1_renderer_de"],
            "evidence": row["dispatch_basis"], "confirmed_plaintext": 0,
        })
    return output


def build(output_dir: Path) -> dict[str, object]:
    output_dir.mkdir(parents=True, exist_ok=True)
    priors = {row["surface"]: row for row in read_tsv(SRC / "X_WHOLE_ROLE_PRIORS.tsv")}
    hypotheses = read_tsv(SRC / "OL_HYPOTHESIS_SPECS.tsv")
    h1_rows = read_tsv(ROOT / G763_H1_REL)
    ol_rows = read_tsv(ROOT / G763_OL_REL)
    contacts = read_tsv(ROOT / G762_OL_REL)
    quantities = read_tsv(ROOT / G760_QUANTITY_REL)
    old_values = read_tsv(ROOT / G686_VALUE_REL)
    repair_rows = read_tsv(ROOT / G711_REPAIR_REL)
    history_bank = read_tsv(ROOT / G755_HISTORY_REL)
    env = semantic_environment()

    if tuple(priors) != TARGET_X or len(h1_rows) != 199 or len(ol_rows) != 16 or len(old_values) != 955:
        raise AssertionError("fixed predecessor universe changed")
    dal_repairs = [row for row in repair_rows if row["surface"] == "dal" and row["repair_mode"] == "UNSUPPORTED_QUANTITY_HEAD_REMOVAL"]
    if len(dal_repairs) != 1 or dal_repairs[0]["v84_lexical_core_de"] != "Rohstoff I, abgemessen":
        raise AssertionError("GDT711 dal quantity-head repair changed")
    h1_surfaces = {row["surface"] for row in h1_rows}
    x_occurrences = build_x_occurrences(env, priors, h1_surfaces)
    x_profiles = build_x_profiles(x_occurrences, priors, old_values)
    x_daiin = build_x_daiin(x_occurrences, priors, old_values)
    h1_fields = build_h1_fields(h1_rows, x_daiin, priors)
    axis_summary = build_axis_summary(x_daiin)
    grammar = build_field_grammar()
    ol_raw = build_ol_raw_audit(env)
    ol_association = build_ol_association(quantities)
    ol_orders = build_ol_orders(ol_rows, contacts, quantities)
    ol_profile = build_ol_profile(ol_orders)
    history = build_history(history_bank)
    revisions = build_renderer_revision(h1_fields, ol_orders)

    expected_x = {"qoty": 77, "dal": 147, "qopchdy": 11, "ofchy": 3, "oteody": 15, "chofol": 1}
    if Counter(str(row["surface"]) for row in x_occurrences) != Counter(expected_x):
        raise AssertionError("X exact occurrence census changed")
    if len(x_occurrences) != 254 or len(x_daiin) != 9:
        raise AssertionError("X/daiin universe changed")
    expected_pairs = Counter({"qoty": 3, "dal": 2, "qopchdy": 1, "ofchy": 1, "oteody": 1, "chofol": 1})
    if Counter(str(row["x_surface"]) for row in x_daiin) != expected_pairs:
        raise AssertionError("exact X/daiin pairs changed")
    expected_h1 = Counter({"RESULT_STAGE_III": 1, "QUALITY_GRADE_III": 1, "MATERIAL_MEASURE_VALUE_III": 1, "NOMINAL_VALUE_III": 1, "OPEN_VALUE_III": 1})
    if len(h1_fields) != 5 or Counter(str(row["selected_local_dispatch"]) for row in h1_fields) != expected_h1:
        raise AssertionError("H1 bounded dispatch changed")
    if any(row["x_surface"] == "qopchdy" and "nimm" in str(row["portable_bounded_field_de"]).lower() for row in h1_fields):
        raise AssertionError("foreign qopchdy action license leaked into target")
    if [(row["raw_contiguous_occurrences"], row["all_reader_exact_occurrences"]) for row in ol_raw] != [(5, 4), (5, 4), (3, 2), (2, 2)]:
        raise AssertionError("raw/exact ol recurrence changed")
    expected_association = [(4, 18, 1, 140), (4, 37, 8, 163), (2, 69, 10, 131), (2, 27, 10, 173)]
    if [(row["ol_in_pattern_slot"], row["eligible_pattern_slots"], row["ol_in_other_slots"], row["eligible_other_slots"]) for row in ol_association] != expected_association:
        raise AssertionError("ol association comparison changed")
    expected_ol = Counter({"HEAD": 8, "CONTEXT_SECOND_FIELD": 2, "OBJECT_PATIENT": 1, "BILATERAL_AMBIGUOUS": 1})
    if len(ol_orders) != 12 or Counter(str(row["selected_slot_function"]) for row in ol_orders) != expected_ol:
        raise AssertionError("repeated ol order dispatch changed")
    if [(row["pattern_eva"], row["positions"]) for row in ol_profile] != [("ol s aiin", 4), ("sain ol", 4), ("saiin ol", 2), ("or aiin ol", 2)]:
        raise AssertionError("ol recurrence profile changed")
    if any(str(row["page"]).startswith("f84") for row in x_occurrences + ol_orders):
        raise AssertionError("sealed page entered GDT764")
    if env["guard"] != {"selected": 4137, "skipped_forbidden": 98, "skipped_not_allowed": 1150}:
        raise AssertionError("guarded context changed")

    tables: tuple[list[dict[str, object]] | list[dict[str, str]], ...] = (
        x_occurrences, x_profiles, x_daiin, h1_fields, axis_summary, grammar,
        ol_raw, ol_association, ol_orders, ol_profile, hypotheses, history, revisions,
    )
    for name, rows in zip(OUTPUT_NAMES[:-1], tables):
        if not rows:
            raise AssertionError(f"empty output: {name}")
        write_tsv(output_dir / name, rows, list(rows[0]))

    result = {
        "schema": "GDT764_RESULT_V1", "status": STATUS,
        "scope": {
            "x_surfaces": len(priors), "x_reader_exact_occurrences": len(x_occurrences),
            "x_daiin_exact_pairs": len(x_daiin), "h1_x_daiin_fields": len(h1_fields),
            "raw_ol_order_strings": sum(int(row["raw_contiguous_occurrences"]) for row in ol_raw),
            "repeated_ol_order_positions": len(ol_orders), "historical_template_rows": len(history),
        },
        "h1_value_field_result": {
            "strongly_typed_axes": 1, "provisionally_typed_axes": 1, "open_axes": 3,
            "dispatch": {str(row["h1_surface"]) + " " + str(row["x_surface"]): row["selected_local_dispatch"] for row in h1_fields},
            "selected_grammar": "H1_RECORD_SCOPE__COMPLETE_X_BOUNDS_AXIS_CANDIDATE__DAIIN_VALUE_III",
            "global_daiin_translation": "NOT_SELECTED",
        },
        "ol_result": {
            "pattern_positions": {str(row["pattern_eva"]): row["positions"] for row in ol_profile},
            "slot_functions": dict(Counter(str(row["selected_slot_function"]) for row in ol_orders)),
            "selected_role": "POSITION_DISPATCHED_PREPARATION_CONTENT_HEAD",
            "gdt763_to_gdt764_evolution": "A09_CONTEXT_TO_HEAD_WITH_LEFT_CONTEXT_RIVAL",
            "strongest_span": "ol s aiin oly",
            "strongest_portable_renderer_de": "Ansatz/Zubereitung, Menge III; Prozess-/Abschlussfeld",
            "strongest_aggressive_c1_renderer_de": "drei Drachmen Ansatz/Zubereitung; abseihen/trennen",
            "drachm_lead": "REPLACEABLE_HISTORICAL_UNIT_CANDIDATE", "oil_identity": "UNSELECTED_C0_WHOLE_RIVAL",
        },
        "guard": {"inherited_token_query": env["guard"]},
        "provenance_gates": {"gdt711_dal_quantity_head": "UNSUPPORTED_QUANTITY_HEAD_REMOVAL__PRESERVED"},
        "claim_boundary": {
            "confirmed_lexemes": 0, "confirmed_plaintext_clauses": 0, "confirmed_units": 0,
            "confirmed_substances": 0, "component_values": 0, "new_pages": 0, "new_images": 0,
            "f84_accessed": False, "f84r_accessed": False,
        },
    }
    (output_dir / "RESULT.json").write_text(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_ARTIFACTS)
    args = parser.parse_args()
    result = build(args.output_dir)
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
