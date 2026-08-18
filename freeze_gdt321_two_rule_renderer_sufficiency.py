#!/usr/bin/env python3
"""Freeze the GDT321 two-rule-versus-full architectural comparison."""
import hashlib
import json
import math
from pathlib import Path

R = Path(__file__).resolve().parent
PANEL = R / "gdt318_frozen_panel.tsv"
G318 = R / "gdt318_result.json"
G319 = R / "gdt319_result.json"
G320 = R / "gdt320_result.json"
METHOD = R / "GDT321_TWO_RULE_RENDERER_SUFFICIENCY_METHOD.md"
DESIGN = R / "gdt321_design.json"


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def canonical_hash(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=True, separators=(",", ":")).encode()).hexdigest()


def main():
    event_count = 5607
    design = {
        "schema": "GDT321_TWO_RULE_RENDERER_SUFFICIENCY_DESIGN_V1",
        "status": "FROZEN_BEFORE_TWO_RULE_SCORING",
        "panel": "EXACT_GDT318_FROZEN_PANEL",
        "classes": ["NONE", "ch", "che", "d", "q", "s", "sh", "t"],
        "models": {
            "CELL": {"parameters": []},
            "ROBUST_TWO_RULE": {"parameters": ["s_X_line_first", "q_X_prev_dy"]},
            "FULL_GDT318_ANCHOR": {"parameters": ["all_8_classes_X_line_first", "all_8_classes_X_prev_dy"]},
        },
        "alpha": 0.5, "ridge": 10.0,
        "fold": "LEAVE_ONE_PHYSICAL_FOLIO_OUT",
        "parameter_counts": {"ROBUST_TWO_RULE": 2, "FULL_GDT318_ANCHOR": 16},
        "model_selector_bits": math.log2(3),
        "parameter_charge_formula": "K_OVER_2_TIMES_LOG2_N",
        "parameter_charges_bits": {"ROBUST_TWO_RULE": math.log2(event_count), "FULL_GDT318_ANCHOR": 8 * math.log2(event_count)},
        "null": {"worlds": 8192, "seed": 32120260818, "strata": "CELL_X_REGISTER", "scope": "FIXED_CROSSFIT_MAX_TWO_ALIGNMENT_DIAGNOSTIC"},
        "decision": {"charged_gain_positive": True, "fraction_full_gain_min": 0.5, "positive_powered_sections_min": 2, "positive_coefficients_min_each": 75, "max_two_p_le": 0.05},
        "claim_ceiling": "Two-rule opaque-cell renderer compression only; no unseen license prefix morpheme POS meaning sound language plaintext or translation.",
        "f84": {"authorized": False, "opened": False, "parsed": False, "retained": False, "joined": False, "scored": False},
        "inputs": {path.name: sha(path) for path in (PANEL, G318, G319, G320, METHOD)},
        "implementation": {Path(__file__).name: sha(Path(__file__))},
    }
    design["content_sha256"] = canonical_hash(design)
    DESIGN.write_text(json.dumps(design, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"status": design["status"], "panel_sha256": design["inputs"][PANEL.name]}, sort_keys=True))


if __name__ == "__main__":
    main()
