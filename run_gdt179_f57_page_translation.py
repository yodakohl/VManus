#!/usr/bin/env python3
"""Build the post-hoc but explicit f57 page-translation scaffold."""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent
ANCHORS = ROOT / "experiments/semantic_assumptions/results/translation_anchor_human_review_panel_v1.tsv"
SOURCE_FREEZE = ROOT / "gdt179_source_freeze.json"
VISUAL = ROOT / "experiments/semantic_assumptions/results/f57v_ai_visual_description_pilot.json"
LEDGER = ROOT / "experiments/semantic_assumptions/ACTIVE_EXPERIMENT_LEDGER.tsv"
METHOD = ROOT / "GDT179_F57_PAGE_TRANSLATION_METHOD.md"

INVENTORY = ROOT / "gdt179_f57_inscription_inventory.tsv"
DECODER = ROOT / "gdt179_quality_decoder.tsv"
R2 = ROOT / "gdt179_r2_partition.tsv"
PREDICTIONS = ROOT / "gdt179_predictions.tsv"
COUNTER = ROOT / "gdt179_counterexamples.tsv"
RESULT = ROOT / "gdt179_result.json"


QUALITY_BY_LOCUS = {
    "f57v.6": ("N1", "NORTHEAST", "HOT"),
    "f57v.7": ("N1", "SOUTHEAST", "MOIST"),
    "f57v.8": ("N1", "SOUTHWEST", "COLD"),
    "f57v.9": ("N1", "NORTHWEST", "DRY"),
    "f57v.11": ("D1", "NORTHEAST", "HOT"),
    "f57v.12": ("D1", "SOUTHEAST", "MOIST"),
    "f57v.13": ("D1", "SOUTHWEST", "COLD"),
    "f57v.10": ("D1", "NORTHWEST", "DRY"),
}


ELEMENTS = [
    ("TOP", "FIRE", "HOT", "DRY", "f"),
    ("RIGHT", "AIR", "HOT", "MOIST", "f"),
    ("BOTTOM", "WATER", "MOIST", "COLD", "p"),
    ("LEFT", "EARTH", "COLD", "DRY", "p"),
]


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canon(obj: object) -> bytes:
    return (json.dumps(obj, sort_keys=True, indent=2, ensure_ascii=False) + "\n").encode()


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, fields: list[str], rows: list[dict[str, object]]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def all_readings(row: dict[str, str]) -> list[str]:
    return [row[edition] for edition in ("ZL3b_raw", "IT2a_raw", "RF1b_raw")]


def feature_bits(register: str, readings: list[str]) -> tuple[int, int, str]:
    if register == "N1":
        selector_values = [int(value.startswith("ot")) for value in readings]
        selector_name = "STARTS_OT_FIRE_INCIDENCE"
    else:
        selector_values = [int("ok" in value) for value in readings]
        selector_name = "HAS_OK_COMPONENT_WATER_INCIDENCE"
    terminal_values = [int(value.endswith("y")) for value in readings]
    if len(set(selector_values)) != 1 or len(set(terminal_values)) != 1:
        raise AssertionError((register, readings, selector_values, terminal_values))
    return selector_values[0], terminal_values[0], selector_name


def decode_quality(register: str, selector: int, y: int) -> str:
    if register == "N1":
        return {(1, 0): "HOT", (1, 1): "DRY", (0, 0): "COLD", (0, 1): "MOIST"}[(selector, y)]
    return {(0, 0): "HOT", (0, 1): "DRY", (1, 0): "COLD", (1, 1): "MOIST"}[(selector, y)]


def main() -> None:
    freeze = json.loads(SOURCE_FREEZE.read_text())
    assert freeze["status"] == "SOURCE_COMPARATOR_FROZEN_BEFORE_TARGET_SYNTHESIS"
    assert not freeze["f84r_accessed"]

    anchors = read_tsv(ANCHORS)
    assert not any("f84r" in json.dumps(row) for row in anchors)
    target_rows = {row["physical_locus"]: row for row in anchors if row["anchor_id"] == "F57_TWO_REGISTER_WHEEL"}
    assert set(target_rows) == set(QUALITY_BY_LOCUS)

    decoder_rows: list[dict[str, object]] = []
    for locus, (register, position, expected) in QUALITY_BY_LOCUS.items():
        row = target_rows[locus]
        readings = all_readings(row)
        selector, terminal_y, selector_name = feature_bits(register, readings)
        decoded = decode_quality(register, selector, terminal_y)
        decoder_rows.append(
            {
                "locus": locus,
                "register": register,
                "position": position,
                "ZL3b": readings[0],
                "IT2a": readings[1],
                "RF1b": readings[2],
                "selector_feature": selector_name,
                "selector_bit": selector,
                "terminal_y_bit": terminal_y,
                "decoded_quality": decoded,
                "frozen_position_quality": expected,
                "exact_internal_match": int(decoded == expected),
                "ownership": row["relation_grade"],
                "evidence_status": "POSTHOC_PAGE_LOCAL_ROLE_DECODE",
            }
        )
    decoder_rows.sort(key=lambda row: (str(row["register"]), ["NORTHEAST", "SOUTHEAST", "SOUTHWEST", "NORTHWEST"].index(str(row["position"]))))
    assert sum(int(row["exact_internal_match"]) for row in decoder_rows) == 8
    write_tsv(DECODER, list(decoder_rows[0]), decoder_rows)

    r2_rows: list[dict[str, object]] = []
    for order, (position, element, q1, q2, state) in enumerate(ELEMENTS, 1):
        r2_rows.append(
            {
                "period_order": order,
                "page_position": position,
                "element_role": element,
                "quality_1": q1,
                "quality_2": q2,
                "r2_slot9_state": state,
                "hot_side": int("HOT" in (q1, q2)),
                "cold_side": int("COLD" in (q1, q2)),
                "upper_page_half": int(position in {"TOP", "RIGHT"}),
                "latin_element_noun_gender": "MASCULINE" if element in {"FIRE", "AIR"} else "FEMININE",
                "alias_count": 3,
                "interpretation": "HOT_COLD_OR_GEOMETRY_OR_LATIN_GENDER_UNRESOLVED",
            }
        )
    write_tsv(R2, list(r2_rows[0]), r2_rows)

    inventory_rows: list[dict[str, object]] = [
        {"locus": "f57v.1", "register": "X1", "physical_role": "OUTSIDE_START_LABEL", "surface": "ZL:dairal;IT:dairol;RF:dairol", "candidate_page_role": "TITLE_OR_START_MARKER", "translation_status": "UNTRANSLATED"},
        {"locus": "f57v.2", "register": "R1", "physical_role": "OUTER_CIRCULAR_TEXT", "surface": "OPAQUE_CIRCULAR_SEQUENCE", "candidate_page_role": "COMMENTARY_OR_LEGEND", "translation_status": "UNTRANSLATED"},
        {"locus": "f57v.3", "register": "R2", "physical_role": "FOUR_BY_SEVENTEEN_REPEATED_TABLE", "surface": "FOUR_PERIODS_WITH_STABLE_SLOT9_F_F_P_P", "candidate_page_role": "FOUR_ELEMENT_PROPERTY_TABLE", "translation_status": "PARTIAL_ROLE_READING"},
        {"locus": "f57v.4", "register": "R3", "physical_role": "MIDDLE_CIRCULAR_TEXT", "surface": "OPAQUE_CIRCULAR_SEQUENCE", "candidate_page_role": "COMMENTARY_OR_LEGEND", "translation_status": "UNTRANSLATED"},
        {"locus": "f57v.5", "register": "R4", "physical_role": "INNER_CIRCULAR_TEXT", "surface": "OPAQUE_CIRCULAR_SEQUENCE", "candidate_page_role": "COMMENTARY_OR_LEGEND", "translation_status": "UNTRANSLATED"},
    ]
    for row in decoder_rows:
        inventory_rows.append(
            {
                "locus": row["locus"],
                "register": row["register"],
                "physical_role": "FIGURE_NEAR_LABEL" if row["register"] == "N1" else "INTERFIGURE_RADIAL_TITLE",
                "surface": f"ZL:{row['ZL3b']};IT:{row['IT2a']};RF:{row['RF1b']}",
                "candidate_page_role": f"{row['decoded_quality']}_QUALITY_POSITION",
                "translation_status": "PROVISIONAL_PAGE_LOCAL_ROLE_READING",
            }
        )
    inventory_rows.sort(key=lambda row: int(str(row["locus"]).split(".")[1]))
    assert len(inventory_rows) == 13
    write_tsv(INVENTORY, list(inventory_rows[0]), inventory_rows)

    prediction_rows = [
        {"prediction_id": "P1", "prediction": "A third owned f57-like quality register using the same local code places terminal-y on MOIST and DRY only.", "exposure": "NOT_TESTED_NO_ELIGIBLE_TARGET", "falsifier": "An independently owned same-phase four-quality register with terminal-y on HOT or COLD."},
        {"prediction_id": "P2", "prediction": "A register referenced to FIRE uses its selector on HOT and DRY; a register referenced to WATER uses its selector on MOIST and COLD.", "exposure": "POSTHOC_ON_F57_UNTESTED_ELSEWHERE", "falsifier": "A pre-owned same-system register whose selector fails the reference-element incidence pair."},
        {"prediction_id": "P3", "prediction": "If R2 slot9 is a thermal property column, another readable homologous 4x17 table will align its state boundary with hot-side versus cold-side elements.", "exposure": "UNTESTED", "falsifier": "A readable close homologue binds the corresponding column to a different property or the f/p split fails under secure reading."},
        {"prediction_id": "P4", "prediction": "R1, R3 and R4 should contain page-level legend/commentary functions, not four independently owned lexical element names.", "exposure": "UNTESTED_NO_SEGMENT_OWNERSHIP", "falsifier": "Authorial sector boundaries or a readable homologue establish four owned values in these rings."},
    ]
    write_tsv(PREDICTIONS, list(prediction_rows[0]), prediction_rows)

    counter_rows = [
        {"counterexample_id": "C1", "finding": "All eight semantic labels remain proximity-only rather than authorially connected owners.", "impact": "The quality assignment is a page homology, not a confirmed lexical translation."},
        {"counterexample_id": "C2", "finding": "The two-bit features were discovered after the f57 quality phase was exposed.", "impact": "Eight-of-eight internal fit has no confirmation-level p-value."},
        {"counterexample_id": "C3", "finding": "R2 f/f/p/p is simultaneously hot/cold, upper/lower, and Latin masculine/feminine.", "impact": "The changing glyph cannot be uniquely glossed."},
        {"counterexample_id": "C4", "finding": "Only R2 slot9 is an all-reading-stable changing table column; other apparent columns are invariant or reading-sensitive.", "impact": "The table does not expose a complete property code."},
        {"counterexample_id": "C5", "finding": "The f57v.8/f77v.3 COLD-like surface match exists only in ZL3b and has uncertain ownership.", "impact": "No cross-page COLD lexeme is supported."},
        {"counterexample_id": "C6", "finding": "Previous global transfers of ot/ok/y quality readings failed or were geometry-confounded.", "impact": "The decoder is frozen as f57-local and cannot read prose."},
        {"counterexample_id": "C7", "finding": "R1, R3, R4 and the outside label remain opaque.", "impact": "This is not a complete textual translation even of f57v."},
        {"counterexample_id": "C8", "finding": "f84r remains sealed and contributes no evidence.", "impact": "No final surprise test has been consumed."},
    ]
    write_tsv(COUNTER, list(counter_rows[0]), counter_rows)

    outputs = [INVENTORY, DECODER, R2, PREDICTIONS, COUNTER]
    result = {
        "experiment": "GDT179_F57_PAGE_TRANSLATION_SCAFFOLD",
        "status": "PROVISIONAL_COMPLETE_F57_ROLE_SCAFFOLD_LOCAL_TWO_BIT_QUALITY_DECODER",
        "headline": (
            "Under the independently frozen W.73 phase, f57 admits an exact page-local two-bit "
            "decoder for both four-item quality registers; this is post-hoc, proximity-owned, and not a lexicon."
        ),
        "counts": {
            "page_loci": len(inventory_rows),
            "quality_labels": len(decoder_rows),
            "internal_decoder_matches": sum(int(row["exact_internal_match"]) for row in decoder_rows),
            "registers": 2,
            "r2_periods": 4,
            "r2_stable_changing_columns": 1,
            "untranslated_long_rings": 3,
        },
        "decoder": {
            "N1": "STARTS_OT_FIRE_INCIDENCE x TERMINAL_Y_MOIST_DRY_PAIR",
            "D1": "HAS_OK_COMPONENT_WATER_INCIDENCE x TERMINAL_Y_MOIST_DRY_PAIR",
            "scope": "F57_PAGE_LOCAL_ONLY",
            "selection_status": "POSTHOC_THEORY_GENERATION",
        },
        "r2": {
            "slot9": "f,f,p,p",
            "matched_partition": "HOT_SIDE,HOT_SIDE,COLD_SIDE,COLD_SIDE",
            "unresolved_aliases": ["UPPER_VS_LOWER_PAGE_HALF", "LATIN_MASCULINE_VS_FEMININE_ELEMENT_NAMES"],
        },
        "input_hashes": {
            str(path.relative_to(ROOT)): sha(path)
            for path in [ANCHORS, SOURCE_FREEZE, VISUAL, METHOD]
        },
        "output_hashes": {path.name: sha(path) for path in outputs},
        "implementation_hash": sha(Path(__file__).resolve()),
        "f84r_accessed": False,
        "claim_ceiling": (
            "A complete provisional page-role scaffold and exact local decoder for eight f57 quality-position "
            "inscriptions. No group is a confirmed quality word; no sound, language, prose plaintext, or "
            "manuscript-wide translation follows."
        ),
    }
    RESULT.write_bytes(canon(result))
    print(json.dumps(result["counts"], sort_keys=True))


if __name__ == "__main__":
    main()
