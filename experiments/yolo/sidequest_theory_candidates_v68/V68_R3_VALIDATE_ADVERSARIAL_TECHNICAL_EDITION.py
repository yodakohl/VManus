#!/usr/bin/env python3
"""Validate the V68 R3 full adversarial technical edition."""

from __future__ import annotations

import csv
import hashlib
import re
import subprocess
import sys
from collections import Counter
from pathlib import Path


HERE = Path(__file__).resolve().parent
YOLO = HERE.parent
BUILDER = HERE / "V68_R3_BUILD_ADVERSARIAL_TECHNICAL_EDITION.py"
SOURCE_BASE = YOLO / "sidequest_theory_candidates_v67" / "V67_R3_776_GROUP_ROUNDTRIP_AUDIT.tsv"

FILES = {
    "ledger": (HERE / "V68_R3_776_GROUP_ADVERSARIAL_LEDGER.tsv", 776),
    "units": (HERE / "V68_R3_14_UNIT_TECHNICAL_EDITION.tsv", 14),
    "processes": (HERE / "V68_R3_14_PROCESS_GRAPHS.tsv", 14),
    "costs": (HERE / "V68_R3_28_MODEL_COSTS.tsv", 28),
    "sections": (HERE / "V68_R3_4_SECTION_COMPARISON.tsv", 4),
    "contradictions": (HERE / "V68_R3_14_CONTRADICTIONS.tsv", 14),
}

UNIT_ORDER = ["H1", "H2", "H3", "H4", "H5", "B1", "B2", "B3", "B4", "B5", "B6", "A1", "A2", "A3"]
ALLOWED_PAGES = {"f10r", "f11r", "f55v", "f56r", "f81v", "f82r", "f83r", "f67r2", "f68r1", "f69v"}
MEDICAL_WORDS = re.compile(
    r"\b(?:Patient(?:in|en)?|Krankheit|Wunde|Heilmittel|Arznei|Therapie|"
    r"Körperteil|Gebärmutter|Magen(?:schmerz)?|Husten|Brusttrank|Diagnose|"
    r"Aderlass|Medizin)\b",
    flags=re.IGNORECASE,
)


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def validate() -> None:
    data = {name: read_tsv(path) for name, (path, _) in FILES.items()}
    for name, (_, expected) in FILES.items():
        require(len(data[name]) == expected, f"{name}: expected {expected}, got {len(data[name])}")

    base = read_tsv(SOURCE_BASE)
    ledger = data["ledger"]
    require(len(base) == 776, "V67 base count")
    require([int(row["combined_group_ordinal"]) for row in ledger] == list(range(1, 777)), "ledger ordinal sequence")
    require({row["page"] for row in ledger} == ALLOWED_PAGES, "new page in ledger")
    require(Counter(row["section_axis"] for row in ledger) == Counter({"HERBAL_MATERIAL": 100, "BIO_PROCESS": 281, "ASTRO_SCHEDULE": 395}), "section coverage")
    require(Counter(row["unit_id"] for row in ledger) == Counter({
        "H1": 14, "H2": 24, "H3": 17, "H4": 18, "H5": 27,
        "B1": 66, "B2": 62, "B3": 86, "B4": 47, "B5": 11, "B6": 9,
        "A1": 190, "A2": 65, "A3": 140,
    }), "unit group coverage")
    for source, row in zip(base, ledger, strict=True):
        require((row["combined_group_ordinal"], row["unit_id"], row["page"], row["source_locus"], row["field_or_local_address"], row["statement_or_locus_unit"], row["opaque_whole_card_or_local_group_key"], row["surface_display_only"]) ==
                (source["combined_group_ordinal"], source["unit_id"], source["page"], source["source_locus"], source["field_or_local_address"], source["statement_or_locus_unit"], source["opaque_whole_card_key"], source["surface_display_only"]), "V67 identity/layout projection")
        require(row["compiler_channel_inherited"] == source["compiler_channel"], "compiler channel changed")
        require(row["formal_roundtrip"] == "PASS", "formal roundtrip failure")
        require(row["complete_local_technical_default"] and row["selected_iatromedical_comparator"], "incomplete dual event reading")
        require(not MEDICAL_WORDS.search(row["complete_local_technical_default"]), f"medical noun in technical event {row['combined_group_ordinal']}")
        require(row["identity_contract"] == "NO_NEW_CARD;EXACT_PROSE_ID_ATOMIC;ASTRO_PAGE_LOCAL;NO_CROSSPAGE_ID", "identity contract")
        require(row["technical_content_status"] == "LOCAL_NONMEDICAL_EXEMPLAR_NOT_CARD_MEANING", "technical local content overclaim")
    require(all(row["fixed_exact_mnemonic"] == "NONE;ASTRO_LOCAL_ONLY" and row["strict_formal_prompt"] == "NONE;NO_PROSE_PROMPT" for row in ledger[381:]), "Prose card imported into Astro")

    units = data["units"]
    require([row["unit_id"] for row in units] == UNIT_ORDER, "unit order")
    require(sum(int(row["group_count"]) for row in units) == 776, "unit group sum")
    require(sum(int(row["locus_count"]) for row in units) == 199, "unit locus sum")
    require(sum(int(row["field_count"].split(";", 1)[0]) for row in units) == 135, "unit field sum")
    require(sum(int(row["statement_count"].split(";", 1)[0]) for row in units) == 116, "unit statement sum")
    require(all(row["technical_default_complete_German"] and row["selected_iatromedical_comparator_complete_German"] for row in units), "incomplete unit text")
    require(all(not MEDICAL_WORDS.search(row["technical_default_complete_German"]) for row in units), "medical noun in technical unit text")
    require(all(row["teachability"] == "SAME_V67_MASTER_EXEMPLAR_COMPILER;FORMAL_776_PASS;STANDALONE_SOURCE_0" for row in units), "asymmetric teachability")
    require(all(row["content_contract"] == "COMPLETE_LOCAL_EDITION;NO_NEW_CARD;TECHNICAL_NOUNS_LOCAL;MEDICAL_COMPARATOR_SEPARATE" for row in units), "unit layer contract")

    processes = data["processes"]
    require([row["unit_id"] for row in processes] == UNIT_ORDER, "process coverage")
    require(sum(int(row["group_coverage"]) for row in processes) == 776, "process group coverage")
    require(all(row["deterministic_process_graph"] and row["execution_rule"] and row["output_or_final_state"] for row in processes), "incomplete process graph")
    require(all(row["cross_unit_contract"] == "MATERIAL_PROCESS_SCHEDULE_IS_EDITORIAL_AXIS_ONLY;NO_VISIBLE_CROSS_UNIT_POINTER" for row in processes), "invented cross-unit workflow pointer")
    require(all(row["graph_status"] == "COMPLETE_LOCAL_EXEMPLAR_PROCESS_NOT_CARD_SEMANTICS" for row in processes), "graph semantic overclaim")

    costs = data["costs"]
    require(Counter(row["model_role"] for row in costs) == Counter({"TECHNICAL_RIVAL": 14, "IATROMEDICAL_COMPARATOR": 14}), "cost symmetry")
    require(Counter(row["section_axis"] for row in costs) == Counter({"HERBAL_MATERIAL": 10, "BIO_PROCESS": 12, "ASTRO_SCHEDULE": 6}), "cost section rows")
    require(all(row["comparability_contract"] == "SYMMETRIC_ONLY_WITHIN_ORIGINAL_SECTION_RUBRIC;CROSS_SECTION_RAW_SUM_REPORTED_BUT_NOT_DECISIVE" for row in costs), "cost comparability absent")
    section_model_cost = Counter()
    section_model_raw = Counter()
    for row in costs:
        key = (row["section_axis"], row["model_role"])
        section_model_cost[key] += int(row["weighted_cost"])
        section_model_raw[key] += int(row["raw_assumption_instance_count"])
    require(section_model_cost == Counter({
        ("HERBAL_MATERIAL", "TECHNICAL_RIVAL"): 113,
        ("HERBAL_MATERIAL", "IATROMEDICAL_COMPARATOR"): 107,
        ("BIO_PROCESS", "TECHNICAL_RIVAL"): 597,
        ("BIO_PROCESS", "IATROMEDICAL_COMPARATOR"): 587,
        ("ASTRO_SCHEDULE", "TECHNICAL_RIVAL"): 50,
        ("ASTRO_SCHEDULE", "IATROMEDICAL_COMPARATOR"): 137,
    }), "weighted section costs")
    require(sum(value for (section, role), value in section_model_raw.items() if role == "TECHNICAL_RIVAL") == 689, "technical raw assumptions")
    require(sum(value for (section, role), value in section_model_raw.items() if role == "IATROMEDICAL_COMPARATOR") == 744, "medical raw assumptions")

    sections = data["sections"]
    require([row["section_axis"] for row in sections] == ["HERBAL_MATERIAL", "BIO_PROCESS", "ASTRO_SCHEDULE", "RAW_TOTAL_NONCOMPARABLE"], "section order")
    expected_section = {
        "HERBAL_MATERIAL": ("100", "8", "5", "6", "71", "113", "107", "12", "12"),
        "BIO_PROCESS": ("281", "13", "25", "59", "191", "597", "587", "10", "14"),
        "ASTRO_SCHEDULE": ("395", "0", "0", "0", "395", "50", "137", "12", "13"),
        "RAW_TOTAL_NONCOMPARABLE": ("776", "21", "30", "65", "657", "760", "831", "34", "39"),
    }
    for row in sections:
        require((row["group_count"], row["technical_local_wins"], row["medical_local_wins"], row["ties"], row["local_exemplar_only_group_burden_each_model"], row["technical_weighted_cost"], row["medical_weighted_cost"], row["technical_ordinal_total"], row["medical_ordinal_total"]) == expected_section[row["section_axis"]], f"section metrics {row['section_axis']}")
    total = sections[-1]
    require(total["within_section_cost_winner"] == "RAW_TECHNICAL_760_LT_MEDICAL_831_BUT_INVALID_AS_GLOBAL_WIN", "raw total caveat")
    require(total["section_verdict"] == "IATROMEDICAL_NARROW_INTEGRATED_CONTENT_LEAD;TECHNICAL_RIVAL_FULL_AND_ARCHITECTURALLY_EQUAL", "final adjudication")

    contradictions = data["contradictions"]
    require([row["unit_id"] for row in contradictions] == UNIT_ORDER, "contradiction coverage")
    require(all(row["strongest_technical_contradiction"] and row["strongest_iatromedical_contradiction_or_nonmedical_rival"] for row in contradictions), "missing held contradiction")
    require(all(row["unresolved_contract"] == "FORMAL_LAYER_DOES_NOT_DECIDE_DOMAIN;BOTH_COMPLETE_CONTENTS_ARE_EXEMPLAR_EXPANSIONS" for row in contradictions), "contradiction asymmetry")

    before = {name: digest(path) for name, (path, _) in FILES.items()}
    subprocess.run([sys.executable, str(BUILDER)], cwd=HERE, check=True, stdout=subprocess.DEVNULL)
    after = {name: digest(path) for name, (path, _) in FILES.items()}
    require(before == after, "builder is not byte-deterministic")

    print("PASS V68 R3 validator")
    print("units=14 groups=776 processes=14 contradictions=14 costs=28")
    print("sections=Herbal:100 Bio:281 Astro:395; formal_roundtrip=776/776")
    print("local_comparisons=technical:21 medical:30 ties:65; exemplar_burden_each=657")
    print("within_section_costs=H:113/107 B:597/587 A:50/137 technical/medical")
    print("raw_total=760/831 NONCOMPARABLE; ordinal=34/39; deterministic_rebuild=PASS")


if __name__ == "__main__":
    validate()
