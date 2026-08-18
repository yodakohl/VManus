#!/usr/bin/env python3
"""Freeze the GDT323 global/Currier/register renderer comparison."""
import hashlib
import json
import math
from pathlib import Path

R = Path(__file__).resolve().parent
PANEL = R / "gdt318_frozen_panel.tsv"
SOURCE = R / "gdt278_native_event_inventory.tsv"
G321 = R / "gdt321_result.json"
G322 = R / "gdt322_result.json"
METHOD = R / "GDT323_REGISTER_CONDITIONED_RENDERER_METHOD.md"
DESIGN = R / "gdt323_design.json"


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def canonical_hash(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=True, separators=(",", ":")).encode()).hexdigest()


def main():
    n = 5607
    counts = {"GLOBAL_TWO_RULE": 2, "CURRIER_TWO_RULE": 4, "REGISTER_TWO_RULE": 10}
    design = {
        "schema": "GDT323_REGISTER_CONDITIONED_RENDERER_DESIGN_V1",
        "status": "FROZEN_BEFORE_REGISTER_CONDITIONING_SCORE",
        "panel": "EXACT_GDT318_FROZEN_PANEL",
        "classes": ["NONE", "ch", "che", "d", "q", "s", "sh", "t"],
        "registers": ["HERBAL_A", "HERBAL_B", "OTHER_A", "OTHER_B", "STARS_RECIPE_B"],
        "models": ["CELL", "GLOBAL_TWO_RULE", "CURRIER_TWO_RULE", "REGISTER_TWO_RULE"],
        "effects": ["s_X_line_first", "q_X_prev_dy"],
        "alpha": 0.5,
        "ridge": 10.0,
        "fold": "LEAVE_ONE_PHYSICAL_FOLIO_OUT",
        "parameter_counts": counts,
        "model_selector_bits": math.log2(4),
        "parameter_charge_formula": "K_OVER_2_TIMES_LOG2_N",
        "parameter_charges_bits": {model: count / 2 * math.log2(n) for model, count in counts.items()},
        "selection": "MINIMUM_TOTAL_HELD_BITS_PLUS_PARAMETER_CHARGE_PLUS_MODEL_SELECTOR",
        "direction_gate": "ALL_MEAN_S_AND_Q_COEFFICIENTS_POSITIVE_FOR_SELECTED_CONDITIONED_MODEL",
        "null": {"worlds": 8192, "seed": 32320260818, "strata": "CELL_X_REGISTER", "scope": "FIXED_CROSSFIT_MAX_THREE_ALIGNMENT_DIAGNOSTIC"},
        "claim_ceiling": "Post-exposure magnitude parameterization of the two-rule opaque-cell renderer only; no unseen license prefix morpheme POS meaning sound language plaintext or translation.",
        "f84": {"authorized": False, "opened": False, "parsed": False, "retained": False, "joined": False, "scored": False},
        "inputs": {path.name: sha(path) for path in (PANEL, SOURCE, G321, G322, METHOD)},
        "implementation": {Path(__file__).name: sha(Path(__file__))},
    }
    design["content_sha256"] = canonical_hash(design)
    DESIGN.write_text(json.dumps(design, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"status": design["status"], "models": design["models"]}, sort_keys=True))


if __name__ == "__main__":
    main()
