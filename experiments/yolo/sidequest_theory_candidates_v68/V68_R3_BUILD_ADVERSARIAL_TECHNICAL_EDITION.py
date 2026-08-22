#!/usr/bin/env python3
"""Build the V68 R3 complete nonmedical adversarial edition."""

from __future__ import annotations

import csv
import re
from collections import Counter, defaultdict
from pathlib import Path


HERE = Path(__file__).resolve().parent
YOLO = HERE.parent
P64 = YOLO / "sidequest_theory_candidates_v64"
P65 = YOLO / "sidequest_theory_candidates_v65"
P66 = YOLO / "sidequest_theory_candidates_v66"
P67 = YOLO / "sidequest_theory_candidates_v67"

SOURCES = {
    "base": P67 / "V67_R3_776_GROUP_ROUNDTRIP_AUDIT.tsv",
    "h_tech_events": P64 / "V64_R3_100_EVENT_PLANT_LEDGER.tsv",
    "h_comparisons": P64 / "V64_R3_19_STATEMENT_COMPARISON.tsv",
    "h_tech_records": P64 / "V64_R3_5_RECORD_PLANT_EDITION.tsv",
    "h_graphs": P64 / "V64_R3_5_RECORD_PROCESS_GRAPHS.tsv",
    "h_costs": P64 / "V64_R3_10_RECORD_MODEL_ASSUMPTION_COSTS.tsv",
    "h_med_events": P64 / "V64_R2_100_EVENT_HERBAL_INTERLINEAR.tsv",
    "h_med_records": P64 / "V64_R2_FIVE_RECORD_EDITIONS.tsv",
    "b_tech_events": P65 / "V65_R3_281_EVENT_WATERWORK_LEDGER.tsv",
    "b_comparisons": P65 / "V65_R3_97_STATEMENT_COMPARISON.tsv",
    "b_tech_records": P65 / "V65_R3_6_RECORD_WATERWORK_EDITION.tsv",
    "b_graphs": P65 / "V65_R3_6_RECORD_PROCESS_STATE_GRAPHS.tsv",
    "b_costs": P65 / "V65_R3_12_RECORD_MODEL_ASSUMPTION_COSTS.tsv",
    "b_med_events": P65 / "V65_R2_281_EVENT_BIO_INTERLINEAR.tsv",
    "b_med_records": P65 / "V65_R2_SIX_RECORD_EDITIONS.tsv",
    "a_tech_groups": P66 / "V66_R3_395_GROUP_LOOKUP_EDITION.tsv",
    "a_tech_diagrams": P66 / "V66_R3_3_DIAGRAM_TECHNICAL_EDITION.tsv",
    "a_algorithms": P66 / "V66_R3_3_LOOKUP_ALGORITHMS.tsv",
    "a_costs": P66 / "V66_R3_6_MODEL_ASSUMPTION_COSTS.tsv",
    "a_med_groups": P66 / "V66_R2_395_GROUP_ASTRO_INTERLINEAR.tsv",
    "a_med_diagrams": P66 / "V66_R2_THREE_DIAGRAM_EDITIONS.tsv",
}

OUT_LEDGER = HERE / "V68_R3_776_GROUP_ADVERSARIAL_LEDGER.tsv"
OUT_UNITS = HERE / "V68_R3_14_UNIT_TECHNICAL_EDITION.tsv"
OUT_PROCESSES = HERE / "V68_R3_14_PROCESS_GRAPHS.tsv"
OUT_COSTS = HERE / "V68_R3_28_MODEL_COSTS.tsv"
OUT_SECTIONS = HERE / "V68_R3_4_SECTION_COMPARISON.tsv"
OUT_CONTRADICTIONS = HERE / "V68_R3_14_CONTRADICTIONS.tsv"

UNIT_ORDER = ("H1", "H2", "H3", "H4", "H5", "B1", "B2", "B3", "B4", "B5", "B6", "A1", "A2", "A3")
PROSE_PAGES = {"f10r", "f11r", "f55v", "f56r", "f81v", "f82r", "f83r"}
ASTRO_PAGES = {"f67r2", "f68r1", "f69v"}

# These exact words are forbidden in the technical default layer.  Medical
# comparator columns remain deliberately separate and are not scanned.
MEDICAL_WORDS = re.compile(
    r"\b(?:Patient(?:in|en)?|Krankheit|Wunde|Heilmittel|Arznei|Therapie|"
    r"Körperteil|Gebärmutter|Magen(?:schmerz)?|Husten|Brusttrank|Diagnose|"
    r"Aderlass|Medizin)\b",
    flags=re.IGNORECASE,
)


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: list[dict[str, str]]) -> None:
    if not rows:
        raise ValueError(f"empty output: {path.name}")
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n", extrasaction="raise")
        writer.writeheader()
        writer.writerows(rows)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def assumption_count(value: str) -> int:
    return sum(int(item.rsplit(":", 1)[1]) for item in value.split("|") if item and item != "NONE")


def model_role(original: str) -> str:
    return "TECHNICAL_RIVAL" if original in {"TECHNICAL_PLANT_REGISTER", "TECHNICAL_WATERWORK", "GENERIC_WORKPLAN"} else "IATROMEDICAL_COMPARATOR"


def section_for(unit_id: str) -> str:
    return "HERBAL_MATERIAL" if unit_id.startswith("H") else "BIO_PROCESS" if unit_id.startswith("B") else "ASTRO_SCHEDULE"


SECTION_SCORE = {
    "HERBAL_MATERIAL": {
        "TECHNICAL_RIVAL": (3, 2, 2, 2, 3),
        "IATROMEDICAL_COMPARATOR": (2, 2, 2, 3, 3),
    },
    "BIO_PROCESS": {
        "TECHNICAL_RIVAL": (1, 2, 2, 2, 3),
        "IATROMEDICAL_COMPARATOR": (3, 3, 2, 3, 3),
    },
    "ASTRO_SCHEDULE": {
        "TECHNICAL_RIVAL": (2, 3, 2, 2, 3),
        "IATROMEDICAL_COMPARATOR": (2, 3, 2, 3, 3),
    },
}


def main() -> None:
    src = {name: read_tsv(path) for name, path in SOURCES.items()}
    expected = {
        "base": 776, "h_tech_events": 100, "h_comparisons": 19,
        "h_tech_records": 5, "h_graphs": 5, "h_costs": 10,
        "h_med_events": 100, "h_med_records": 5,
        "b_tech_events": 281, "b_comparisons": 97,
        "b_tech_records": 6, "b_graphs": 6, "b_costs": 12,
        "b_med_events": 281, "b_med_records": 6,
        "a_tech_groups": 395, "a_tech_diagrams": 3, "a_algorithms": 3,
        "a_costs": 6, "a_med_groups": 395, "a_med_diagrams": 3,
    }
    for name, count in expected.items():
        require(len(src[name]) == count, f"{name}: expected {count}, got {len(src[name])}")
    require({row["page"] for row in src["base"]} == PROSE_PAGES | ASTRO_PAGES, "base page scope changed")
    require([row["unit_id"] for row in src["base"][:1]] == ["H1"], "base order changed")

    base_by_ordinal = {row["combined_group_ordinal"]: row for row in src["base"]}
    htech = {row["event_serial"]: row for row in src["h_tech_events"]}
    hmed = {row["event_serial"]: row for row in src["h_med_events"]}
    btech = {row["event_serial"]: row for row in src["b_tech_events"]}
    bmed = {row["event_serial"]: row for row in src["b_med_events"]}
    require(set(htech) == set(hmed) == {str(i) for i in range(1, 101)}, "Herbal event keys")
    require(set(btech) == set(bmed) == {str(i) for i in range(101, 382)}, "Bio event keys")
    hcomparison = {row["statement_id"]: row for row in src["h_comparisons"]}
    bcomparison = {row["statement_id"]: row for row in src["b_comparisons"]}

    astro_med_by_key = {
        (row["page"], row["locus"], row["event_index"], row["surface_ZL3b"]): row
        for row in src["a_med_groups"]
    }
    require(len(astro_med_by_key) == 395, "Astro medical key collision")

    ledger_rows: list[dict[str, str]] = []
    for ordinal in range(1, 777):
        base = base_by_ordinal[str(ordinal)]
        unit_id = base["unit_id"]
        if ordinal <= 100:
            tech = htech[str(ordinal)]
            med = hmed[str(ordinal)]
            require((base["page"], base["source_locus"], base["opaque_whole_card_key"], base["surface_display_only"]) ==
                    (tech["page"], tech["locus"], "P:" + tech["joint_tuple_id_opaque"], tech["surface_display_only"]), f"Herbal base drift {ordinal}")
            require((tech["joint_tuple_id_opaque"], tech["surface_display_only"], tech["field_id"], tech["statement_id"]) ==
                    (med["joint_tuple_id"], med["surface_display_only"], med["field_id"], med["statement_id"]), f"Herbal comparator drift {ordinal}")
            comparison = hcomparison[tech["statement_id"]]
            technical_default = tech["complete_layered_technical_reading"]
            medical_default = med["v64_tagged_source_segment"]
            technical_local_source = tech["local_filler_source_class"]
            medical_local_source = med["source_layer_tags"]
            fixed_mnemonic = tech["fixed_exact_mnemonic"]
            formal_prompt = tech["strict_formal_prompt"]
            template = tech["event_template"]
            close = tech["terminal_status"]
            comparison_winner = comparison["coherence_winner"]
            technical_contradiction = comparison["strongest_technical_contradiction"]
        elif ordinal <= 381:
            tech = btech[str(ordinal)]
            med = bmed[str(ordinal)]
            require((base["page"], base["source_locus"], base["opaque_whole_card_key"], base["surface_display_only"]) ==
                    (tech["page"], tech["locus"], "P:" + tech["joint_tuple_id_opaque"], tech["surface_display_only"]), f"Bio base drift {ordinal}")
            require((tech["joint_tuple_id_opaque"], tech["surface_display_only"], tech["field_id"], tech["statement_id"]) ==
                    (med["joint_tuple_id"], med["surface_display_only"], med["field_id"], med["statement_id"]), f"Bio comparator drift {ordinal}")
            comparison = bcomparison[tech["statement_id"]]
            technical_default = tech["complete_layered_technical_reading"]
            medical_default = med["v65_concrete_default_segment"]
            technical_local_source = tech["local_argument_source_class"]
            medical_local_source = "VISIBLE_APPARATUS+BODY_BATH_PATIENT_LAYER+LOCAL_EXEMPLAR"
            fixed_mnemonic = tech["fixed_exact_mnemonic"]
            formal_prompt = tech["strict_formal_prompt"]
            template = tech["event_template"]
            close = tech["terminal_status"]
            comparison_winner = comparison["statement_coherence_winner"]
            technical_contradiction = comparison["strongest_technical_contradiction"]
        else:
            tech = src["a_tech_groups"][ordinal - 382]
            med = astro_med_by_key[(tech["page"], tech["source_locus"], tech["group_index_within_locus"], tech["surface_display_only"])]
            require((base["unit_id"], base["page"], base["source_locus"], base["opaque_whole_card_key"], base["surface_display_only"]) ==
                    (tech["diagram_id"], tech["page"], tech["source_locus"], "A:" + tech["local_group_id"], tech["surface_display_only"]), f"Astro base drift {ordinal}")
            technical_default = tech["concrete_technical_function_German"]
            medical_default = med["default_content_German"]
            technical_local_source = "PAGE_LOCAL_ADDRESS+GENERIC_WORKPLAN_EXEMPLAR"
            medical_local_source = "PAGE_LOCAL_ADDRESS+EXTERNAL_IATROMATHEMATICAL_EXEMPLAR"
            fixed_mnemonic = "NONE;ASTRO_LOCAL_ONLY"
            formal_prompt = "NONE;NO_PROSE_PROMPT"
            template = tech["technical_group_role"]
            close = "NOT_PROSE_CLOSE"
            diagram = next(row for row in src["a_tech_diagrams"] if row["diagram_id"] == unit_id)
            comparison_winner = diagram["cost_winner"] + ";HISTORICAL=" + diagram["historical_fit_winner"]
            technical_contradiction = diagram["strongest_contradiction"]
        require(not MEDICAL_WORDS.search(technical_default), f"medical noun leaked into technical default at {ordinal}: {technical_default}")
        ledger_rows.append({
            "combined_group_ordinal": str(ordinal),
            "unit_id": unit_id,
            "section_axis": section_for(unit_id),
            "page": base["page"],
            "source_locus": base["source_locus"],
            "field_or_local_address": base["field_or_local_address"],
            "statement_or_locus_unit": base["statement_or_locus_unit"],
            "opaque_whole_card_or_local_group_key": base["opaque_whole_card_key"],
            "surface_display_only": base["surface_display_only"],
            "fixed_exact_mnemonic": fixed_mnemonic,
            "strict_formal_prompt": formal_prompt,
            "template_or_diagram_role": template,
            "terminal_or_local_status": close,
            "technical_system": "PLANT_STOCK_AND_ADDITIVE_BATCH" if unit_id.startswith("H") else "WATER_OR_BATHHOUSE_APPARATUS" if unit_id.startswith("B") else "GENERIC_WORKPLAN_LOOKUP",
            "complete_local_technical_default": technical_default,
            "technical_local_noun_source": technical_local_source,
            "selected_iatromedical_comparator": medical_default,
            "medical_local_noun_source": medical_local_source,
            "local_comparison_winner": comparison_winner,
            "strongest_local_technical_contradiction": technical_contradiction,
            "compiler_channel_inherited": base["compiler_channel"],
            "field_and_reflow_contract": base["field_grouping_operation"] + ">" + base["line_reflow_operation"],
            "formal_roundtrip": base["formal_identity_order_layout_roundtrip"],
            "technical_content_status": "LOCAL_NONMEDICAL_EXEMPLAR_NOT_CARD_MEANING",
            "medical_content_status": "SEPARATE_SELECTED_COMPARATOR_NOT_CARD_MEANING",
            "identity_contract": "NO_NEW_CARD;EXACT_PROSE_ID_ATOMIC;ASTRO_PAGE_LOCAL;NO_CROSSPAGE_ID",
        })
    require(len(ledger_rows) == 776, "ledger count")

    htech_record = {row["record_unit_id"]: row for row in src["h_tech_records"]}
    hmed_record = {row["record_unit_id"]: row for row in src["h_med_records"]}
    btech_record = {row["record_unit_id"]: row for row in src["b_tech_records"]}
    bmed_record = {row["record_unit_id"]: row for row in src["b_med_records"]}
    atech_record = {row["diagram_id"]: row for row in src["a_tech_diagrams"]}
    amed_record = {row["diagram_id"]: row for row in src["a_med_diagrams"]}
    hgraph = {row["record_unit_id"]: row for row in src["h_graphs"]}
    bgraph = {row["record_unit_id"]: row for row in src["b_graphs"]}
    aalgorithm = {row["diagram_id"]: row for row in src["a_algorithms"]}

    all_cost_sources = src["h_costs"] + src["b_costs"] + src["a_costs"]
    cost_by_unit_role: dict[tuple[str, str], dict[str, str]] = {}
    cost_rows: list[dict[str, str]] = []
    for row in all_cost_sources:
        unit_id = row.get("record_unit_id") or row["diagram_id"]
        role = model_role(row["model"])
        cost_by_unit_role[(unit_id, role)] = row
    for unit_id in UNIT_ORDER:
        technical = cost_by_unit_role[(unit_id, "TECHNICAL_RIVAL")]
        medical = cost_by_unit_role[(unit_id, "IATROMEDICAL_COMPARATOR")]
        technical_cost = int(technical["weighted_cost"])
        medical_cost = int(medical["weighted_cost"])
        winner = "TECHNICAL_RIVAL" if technical_cost < medical_cost else "IATROMEDICAL_COMPARATOR" if medical_cost < technical_cost else "TIE"
        groups = sum(row["unit_id"] == unit_id for row in ledger_rows)
        for role, source in (("TECHNICAL_RIVAL", technical), ("IATROMEDICAL_COMPARATOR", medical)):
            cost_rows.append({
                "unit_id": unit_id,
                "section_axis": section_for(unit_id),
                "model_role": role,
                "original_model": source["model"],
                "group_count": str(groups),
                "assumption_counts": source["assumption_counts"],
                "raw_assumption_instance_count": str(assumption_count(source["assumption_counts"])),
                "weighted_cost": source["weighted_cost"],
                "weighted_cost_per_group": f"{int(source['weighted_cost']) / groups:.6f}",
                "weight_contract": source.get("weight_contract") or source.get("cost_contract") or "NONE",
                "cost_scope": source.get("cost_scope") or "DIAGRAM_LEVEL_DESCRIPTION_LENGTH",
                "within_unit_cost_winner": winner,
                "comparability_contract": "SYMMETRIC_ONLY_WITHIN_ORIGINAL_SECTION_RUBRIC;CROSS_SECTION_RAW_SUM_REPORTED_BUT_NOT_DECISIVE",
                "interpretation": source["interpretation"],
            })
    require(len(cost_rows) == 28, "cost row count")

    unit_rows: list[dict[str, str]] = []
    process_rows: list[dict[str, str]] = []
    contradiction_rows: list[dict[str, str]] = []
    for unit_id in UNIT_ORDER:
        section = section_for(unit_id)
        unit_ledger = [row for row in ledger_rows if row["unit_id"] == unit_id]
        technical_cost = int(cost_by_unit_role[(unit_id, "TECHNICAL_RIVAL")]["weighted_cost"])
        medical_cost = int(cost_by_unit_role[(unit_id, "IATROMEDICAL_COMPARATOR")]["weighted_cost"])
        if unit_id.startswith("H"):
            tech = htech_record[unit_id]
            med = hmed_record[unit_id]
            graph = hgraph[unit_id]
            technical_text = tech["complete_technical_plant_article"]
            medical_text = med["tagged_continuous_german_source_edition"]
            title = tech["technical_plant_input"] + " -> " + tech["technical_product"]
            fields, statements = tech["field_count"], tech["statement_count"]
            technical_contradiction = tech["strongest_technical_contradiction"]
            medical_contradiction = med["strongest_nonmedical_rival"]
            local_winners = Counter(row["coherence_winner"] for row in src["h_comparisons"] if row["record_unit_id"] == unit_id)
            process_graph = graph["node_path"] + " || " + graph["operation_edge_path"]
            execution_rule = graph["execution_rule"]
            input_slot = tech["technical_plant_input"]
            output_slot = tech["technical_product"]
            page_fit = "VISIBLE_PLANT_OWNER_FITS_BOTH;TECHNICAL_PRODUCT_AND_MEDICAL_USE_BOTH_LOCAL"
            historical = "TECH:PLANT_STOCK_OR_CRAFT_BATCH_REGISTER;MED:MATERIA_MEDICA_ARTICLE"
            technical_verdict = tech["record_coherence_winner"]
        elif unit_id.startswith("B"):
            tech = btech_record[unit_id]
            med = bmed_record[unit_id]
            graph = bgraph[unit_id]
            technical_text = tech["complete_technical_waterwork_article"]
            medical_text = med["tagged_continuous_german_source_edition"]
            title = tech["local_apparatus_inventory"]
            fields, statements = tech["field_count"], tech["statement_count"]
            technical_contradiction = tech["strongest_technical_contradiction"]
            medical_contradiction = med["strongest_contradiction"]
            local_winners = Counter(row["statement_coherence_winner"] for row in src["b_comparisons"] if row["record_unit_id"] == unit_id)
            process_graph = graph["phase_path"] + " || " + graph["local_state_path"]
            execution_rule = graph["deterministic_execution_rule"]
            input_slot = tech["visible_owner_argument"]
            output_slot = graph["final_v62_state"]
            page_fit = "TECH_EXPLAINS_APPARATUS;MEDICAL_HYBRID_ALSO_EXPLAINS_VISIBLE_HUMANS;B5_B6_HAVE_WEAKER_HUMAN_BINDING"
            historical = "TECH:BATHHOUSE_OR_WATERWORK_OPERATIONS;MED:THERAPEUTIC_BALNEOLOGY_PLUS_APPARATUS"
            technical_verdict = tech["record_coherence_winner_by_fixed_cost"]
        else:
            tech = atech_record[unit_id]
            med = amed_record[unit_id]
            graph = aalgorithm[unit_id]
            technical_text = tech["complete_technical_default_German"]
            medical_text = med["complete_default_German"]
            title = tech["technical_formal_role"]
            fields, statements = "0;NOT_PROSE", "0;LOCAL_LOCI"
            technical_contradiction = tech["strongest_contradiction"]
            medical_contradiction = med["strongest_counterevidence"]
            local_winners = Counter()
            process_graph = graph["process_graph"]
            execution_rule = graph["deterministic_algorithm"]
            input_slot = graph["required_input"]
            output_slot = graph["output"]
            page_fit = "BOTH_FIT_VISIBLE_7_12_28_TOPOLOGY;NEITHER_HAS_EXTERNAL_LABEL_KEY"
            historical = "TECH:GENERIC_CALENDAR_OR_WORKPLAN;MED:IATROMATHEMATICAL_ELECTION_AND_LUNAR_STATIONS"
            technical_verdict = tech["cost_winner"] + ";HISTORICAL=" + tech["historical_fit_winner"]
        require(not MEDICAL_WORDS.search(technical_text), f"medical noun in unit technical text: {unit_id}")
        winner_summary = f"TECHNICAL={local_winners['TECHNICAL']};IATROMEDICAL={local_winners['IATROMEDICAL']};TIE={local_winners['TIE']}" if local_winners else "NOT_LOCALLY_SCORED"
        unit_rows.append({
            "unit_id": unit_id,
            "section_axis": section,
            "page": unit_ledger[0]["page"],
            "unit_title_or_inventory": title,
            "group_count": str(len(unit_ledger)),
            "locus_count": str(len({row["source_locus"] for row in unit_ledger})),
            "field_count": fields,
            "statement_count": statements,
            "technical_default_complete_German": technical_text,
            "selected_iatromedical_comparator_complete_German": medical_text,
            "technical_weighted_assumption_cost": str(technical_cost),
            "medical_weighted_assumption_cost": str(medical_cost),
            "local_comparison_summary": winner_summary,
            "page_fit_contract": page_fit,
            "historical_mechanism_comparison": historical,
            "teachability": "SAME_V67_MASTER_EXEMPLAR_COMPILER;FORMAL_776_PASS;STANDALONE_SOURCE_0",
            "model_verdict": technical_verdict,
            "content_contract": "COMPLETE_LOCAL_EDITION;NO_NEW_CARD;TECHNICAL_NOUNS_LOCAL;MEDICAL_COMPARATOR_SEPARATE",
        })
        process_rows.append({
            "unit_id": unit_id,
            "section_axis": section,
            "input_or_owner_slot": input_slot,
            "deterministic_process_graph": process_graph,
            "output_or_final_state": output_slot,
            "execution_rule": execution_rule,
            "field_or_locus_coverage": str(len({row["field_or_local_address"] for row in unit_ledger})),
            "group_coverage": str(len(unit_ledger)),
            "commit_or_lookup_contract": "OBSERVED_PROSE_CLOSE_ONLY" if unit_id.startswith(("H", "B")) else "PAGE_LOCAL_LOOKUP;NO_PROSE_CLOSE",
            "cross_unit_contract": "MATERIAL_PROCESS_SCHEDULE_IS_EDITORIAL_AXIS_ONLY;NO_VISIBLE_CROSS_UNIT_POINTER",
            "graph_status": "COMPLETE_LOCAL_EXEMPLAR_PROCESS_NOT_CARD_SEMANTICS",
        })
        contradiction_rows.append({
            "unit_id": unit_id,
            "section_axis": section,
            "technical_model": "PLANT_STOCK_BATCH" if unit_id.startswith("H") else "WATER_BATHHOUSE_APPARATUS" if unit_id.startswith("B") else "GENERIC_WORKPLAN_LOOKUP",
            "strongest_technical_contradiction": technical_contradiction,
            "strongest_iatromedical_contradiction_or_nonmedical_rival": medical_contradiction,
            "technical_local_loss_count": str(local_winners["IATROMEDICAL"]) if local_winners else "1;UNIT_LEVEL_HELD_CONTRADICTION",
            "medical_local_loss_count": str(local_winners["TECHNICAL"]) if local_winners else "1;UNIT_LEVEL_HELD_CONTRADICTION",
            "weighted_cost_technical_vs_medical": f"{technical_cost}:{medical_cost}",
            "adjudication": technical_verdict,
            "unresolved_contract": "FORMAL_LAYER_DOES_NOT_DECIDE_DOMAIN;BOTH_COMPLETE_CONTENTS_ARE_EXEMPLAR_EXPANSIONS",
        })
    require(len(unit_rows) == len(process_rows) == len(contradiction_rows) == 14, "unit outputs")

    # Section-level quantitative comparison.  Ordinal scores are deliberately
    # frozen and auditable: CONTENT from local wins, PAGE from dominant visible
    # classes, SHARED from cross-section workflow with no direct pointer,
    # HISTORY from the selected genre comparison, TEACH from the V67 compiler.
    section_specs = {
        "HERBAL_MATERIAL": (100, 5, 19, 71, Counter({"TECHNICAL": 8, "IATROMEDICAL": 5, "TIE": 6})),
        "BIO_PROCESS": (281, 6, 97, 191, Counter({"TECHNICAL": 13, "IATROMEDICAL": 25, "TIE": 59})),
        "ASTRO_SCHEDULE": (395, 3, 0, 395, Counter()),
    }
    section_rows: list[dict[str, str]] = []
    overall = defaultdict(int)
    for section, (groups, units, comparisons, exemplar_groups, winners) in section_specs.items():
        section_costs = [row for row in cost_rows if row["section_axis"] == section]
        tech_cost = sum(int(row["weighted_cost"]) for row in section_costs if row["model_role"] == "TECHNICAL_RIVAL")
        med_cost = sum(int(row["weighted_cost"]) for row in section_costs if row["model_role"] == "IATROMEDICAL_COMPARATOR")
        tech_raw = sum(int(row["raw_assumption_instance_count"]) for row in section_costs if row["model_role"] == "TECHNICAL_RIVAL")
        med_raw = sum(int(row["raw_assumption_instance_count"]) for row in section_costs if row["model_role"] == "IATROMEDICAL_COMPARATOR")
        tech_scores = SECTION_SCORE[section]["TECHNICAL_RIVAL"]
        med_scores = SECTION_SCORE[section]["IATROMEDICAL_COMPARATOR"]
        for key, value in (("groups", groups), ("units", units), ("comparisons", comparisons), ("exemplar", exemplar_groups),
                           ("tech_wins", winners["TECHNICAL"]), ("med_wins", winners["IATROMEDICAL"]), ("ties", winners["TIE"]),
                           ("tech_cost", tech_cost), ("med_cost", med_cost), ("tech_raw", tech_raw), ("med_raw", med_raw),
                           ("tech_score", sum(tech_scores)), ("med_score", sum(med_scores))):
            overall[key] += value
        section_rows.append({
            "section_axis": section,
            "unit_count": str(units),
            "group_count": str(groups),
            "local_comparison_count": str(comparisons),
            "technical_local_wins": str(winners["TECHNICAL"]),
            "medical_local_wins": str(winners["IATROMEDICAL"]),
            "ties": str(winners["TIE"]),
            "local_exemplar_only_group_burden_each_model": str(exemplar_groups),
            "technical_raw_assumption_instances": str(tech_raw),
            "medical_raw_assumption_instances": str(med_raw),
            "technical_weighted_cost": str(tech_cost),
            "medical_weighted_cost": str(med_cost),
            "within_section_cost_winner": "TECHNICAL_RIVAL" if tech_cost < med_cost else "IATROMEDICAL_COMPARATOR" if med_cost < tech_cost else "TIE",
            "score_contract": "0-3_EACH:CONTENT_COHERENCE|PAGE_FIT|SHARED_WORKFLOW|HISTORICAL_MECHANISM|TEACHABILITY;ORDINAL_AUDIT_NOT_PROBABILITY",
            "technical_scores_C_P_W_H_T": "|".join(map(str, tech_scores)),
            "medical_scores_C_P_W_H_T": "|".join(map(str, med_scores)),
            "technical_ordinal_total": str(sum(tech_scores)),
            "medical_ordinal_total": str(sum(med_scores)),
            "section_verdict": "TECHNICAL_STATEMENT_LEAD_BUT_MEDICAL_COST_AND_HISTORY_LEAD" if section == "HERBAL_MATERIAL" else "MEDICAL_NARROW_LEAD;TECHNICAL_COMPLETE" if section == "BIO_PROCESS" else "TECHNICAL_FORMAL_COST_LEAD;MEDICAL_HISTORICAL_LEAD",
            "cost_comparability": "VALID_WITHIN_THIS_SECTION_ONLY;DO_NOT_TREAT_RAW_CROSS_SECTION_SUM_AS_COMMON_SCALE",
        })
    section_rows.append({
        "section_axis": "RAW_TOTAL_NONCOMPARABLE",
        "unit_count": str(overall["units"]),
        "group_count": str(overall["groups"]),
        "local_comparison_count": str(overall["comparisons"]),
        "technical_local_wins": str(overall["tech_wins"]),
        "medical_local_wins": str(overall["med_wins"]),
        "ties": str(overall["ties"]),
        "local_exemplar_only_group_burden_each_model": str(overall["exemplar"]),
        "technical_raw_assumption_instances": str(overall["tech_raw"]),
        "medical_raw_assumption_instances": str(overall["med_raw"]),
        "technical_weighted_cost": str(overall["tech_cost"]),
        "medical_weighted_cost": str(overall["med_cost"]),
        "within_section_cost_winner": "RAW_TECHNICAL_760_LT_MEDICAL_831_BUT_INVALID_AS_GLOBAL_WIN",
        "score_contract": "SUM_OF_THREE_DISCLOSED_ORDINAL_SECTION_AUDITS;NOT_EVIDENCE",
        "technical_scores_C_P_W_H_T": "NOT_AGGREGATED_BY_DIMENSION",
        "medical_scores_C_P_W_H_T": "NOT_AGGREGATED_BY_DIMENSION",
        "technical_ordinal_total": str(overall["tech_score"]),
        "medical_ordinal_total": str(overall["med_score"]),
        "section_verdict": "IATROMEDICAL_NARROW_INTEGRATED_CONTENT_LEAD;TECHNICAL_RIVAL_FULL_AND_ARCHITECTURALLY_EQUAL",
        "cost_comparability": "HERBAL_BIO_ASTRO_USE_DIFFERENT_UNITS_AND_WEIGHT_CONTRACTS;RAW_760_VS_831_IS_DISCLOSED_ONLY",
    })

    require((overall["groups"], overall["units"], overall["comparisons"], overall["exemplar"], overall["tech_wins"], overall["med_wins"], overall["ties"]) == (776, 14, 116, 657, 21, 30, 65), "overall comparison counts")
    require((overall["tech_raw"], overall["med_raw"], overall["tech_cost"], overall["med_cost"], overall["tech_score"], overall["med_score"]) == (689, 744, 760, 831, 34, 39), "overall costs/scores")
    require(len(section_rows) == 4, "section output")
    require(all(row["formal_roundtrip"] == "PASS" for row in ledger_rows), "formal roundtrip")
    require(sum(row["section_axis"] == "HERBAL_MATERIAL" for row in ledger_rows) == 100, "Herbal ledger count")
    require(sum(row["section_axis"] == "BIO_PROCESS" for row in ledger_rows) == 281, "Bio ledger count")
    require(sum(row["section_axis"] == "ASTRO_SCHEDULE" for row in ledger_rows) == 395, "Astro ledger count")

    write_tsv(OUT_LEDGER, ledger_rows)
    write_tsv(OUT_UNITS, unit_rows)
    write_tsv(OUT_PROCESSES, process_rows)
    write_tsv(OUT_COSTS, cost_rows)
    write_tsv(OUT_SECTIONS, section_rows)
    write_tsv(OUT_CONTRADICTIONS, contradiction_rows)

    print("PASS V68 R3 build")
    print("units=14 groups=776 sections=100+281+395 processes=14 contradictions=14 costs=28")
    print("local_statement_comparison=technical:21 medical:30 tie:65")
    print("section_costs=H:113/107 B:597/587 A:50/137 technical/medical")
    print("raw_total_noncomparable=760/831; ordinal_audit=34/39 technical/medical")
    print("verdict=TECHNICAL_COMPLETE_BUT_IATROMEDICAL_NARROW_INTEGRATED_CONTENT_LEAD")


if __name__ == "__main__":
    main()
