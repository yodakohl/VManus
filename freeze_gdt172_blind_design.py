#!/usr/bin/env python3
"""Freeze the unchanged GDT171 blind instrument for GDT172."""
from __future__ import annotations
import hashlib, json
from pathlib import Path

R = Path(__file__).resolve().parent
FREEZE = R / "gdt172_source_literal_correction_freeze.json"
PARENT_DESIGN = R / "gdt171_blind_design.json"
PARENT_RUNNER = R / "run_gdt171_blind_instrument.py"
METHOD = R / "GDT172_LITERAL_ESCAPE_CORRECTION_METHOD.md"
OUT = R / "gdt172_blind_design.json"

def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def csha(x): return hashlib.sha256(json.dumps(x, sort_keys=True, ensure_ascii=True, separators=(",", ":")).encode()).hexdigest()

def main():
    parent = json.loads(PARENT_DESIGN.read_text())
    design = {"schema": "GDT172_BLIND_INSTRUMENT_DESIGN_V1", "status": "FROZEN_UNCHANGED_GDT171_INSTRUMENT_BEFORE_LITERAL_SENSITIVITY_PARSE",
              "source_freeze_sha256": sha(FREEZE), "parent_design_sha256": sha(PARENT_DESIGN), "parent_runner_sha256": sha(PARENT_RUNNER), "method_sha256": sha(METHOD),
              "parser_algorithm": "UNCHANGED_GDT170_GDT171_EXACT_SURFACE_CONTRAST_AND_LAYOUT_ASSISTED_RANKS",
              "blind_levels": parent["blind_levels"], "operation_discovery": parent["operation_discovery"],
              "surface_parse_rank": parent["surface_parse_rank"], "annotation_assisted_rank": parent["annotation_assisted_rank"],
              "diagnostics": parent["diagnostics"], "context_smoothing": parent["context_smoothing"],
              "operation_null_worlds": parent["operation_null_worlds"], "alignment_host_panel": parent["alignment_host_panel"],
              "material_change_rules": {"rate_or_information_absolute": 0.05, "gain_sign_change_or_relative_absolute": 0.10, "operation_library_jaccard_below": 0.80, "discrete_zero_nonzero_change_always_report": True},
              "corpus_adaptation": parent["corpus_adaptation"],
              "forbidden_inputs": ["gdt172_sealed_oracle.json.gz", "gdt171_sealed_lexical_lookup.tsv", "build_gdt172_literal_correction.py"],
              "blind_output_freeze_before_oracle_unblinding": True, "no_voynich_tuning": True, "voynich_inputs": 0, "f84_access": False,
              "implementation": {Path(__file__).name: sha(Path(__file__))},
              "claim_ceiling": "Blind synthetic literal-channel sensitivity only; no Voynich word, code value, language, meaning, plaintext, or translation."}
    design["design_content_sha256"] = csha(design)
    OUT.write_text(json.dumps(design, indent=2, sort_keys=True) + "\n")
    print(design["status"])

if __name__ == "__main__": main()
