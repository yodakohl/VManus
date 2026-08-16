#!/usr/bin/env python3
"""Freeze the GDT171 blind use of the unchanged GDT170 surface instrument."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

R = Path(__file__).resolve().parent
SOURCE_FREEZE = R / "gdt171_source_observation_oracle_freeze.json"
PARENT_DESIGN = R / "gdt170_blind_design.json"
PARENT_RUNNER = R / "run_gdt170_blind_instrument.py"
METHOD = R / "GDT171_HISTORICAL_PLAUSIBILITY_INSTRUMENT_METHOD.md"
OUT = R / "gdt171_blind_design.json"


def sha(path: Path) -> str: return hashlib.sha256(path.read_bytes()).hexdigest()
def csha(x) -> str: return hashlib.sha256(json.dumps(x, sort_keys=True, ensure_ascii=True, separators=(",", ":")).encode()).hexdigest()


def main() -> None:
    parent = json.loads(PARENT_DESIGN.read_text())
    design = {"schema": "GDT171_BLIND_INSTRUMENT_DESIGN_V1", "status": "FROZEN_UNCHANGED_GDT170_INSTRUMENT_BEFORE_V2_BLIND_PARSE",
              "source_freeze_sha256": sha(SOURCE_FREEZE), "parent_design_sha256": sha(PARENT_DESIGN),
              "parent_runner_sha256": sha(PARENT_RUNNER), "method_sha256": sha(METHOD),
              "parser_algorithm": "UNCHANGED_GDT170_EXACT_SURFACE_CONTRAST_AND_LAYOUT_ASSISTED_RANKS",
              "blind_levels": parent["blind_levels"], "operation_discovery": parent["operation_discovery"],
              "surface_parse_rank": parent["surface_parse_rank"], "annotation_assisted_rank": parent["annotation_assisted_rank"],
              "diagnostics": parent["diagnostics"], "context_smoothing": parent["context_smoothing"],
              "operation_null_worlds": parent["operation_null_worlds"], "alignment_host_panel": parent["alignment_host_panel"],
              "corpus_adaptation": {"operation_training_scope": "ONE_ANONYMOUS_WORLD_ALL_PARTITIONED_REGISTERS_AND_HANDS",
                                    "held_context_fold": "PHYSICAL_SYNTHETIC_FOLIO",
                                    "register_alignment": "PAIRWISE_REGISTER_GEOMETRY_WITHOUT_GLYPH_IDENTITY",
                                    "no_parameter_change": True},
              "forbidden_inputs": ["gdt171_sealed_oracle.json.gz", "gdt171_sealed_lexical_lookup.tsv", "build_gdt171_historical_controls.py"],
              "blind_output_freeze_before_oracle_unblinding": True, "no_voynich_tuning": True, "voynich_inputs": 0, "f84r_access": False,
              "implementation": {Path(__file__).name: sha(Path(__file__))},
              "claim_ceiling": "Blind synthetic historical-plausibility outputs only; no Voynich word, code value, language, meaning, plaintext, or translation."}
    design["design_content_sha256"] = csha(design); OUT.write_text(json.dumps(design, indent=2, sort_keys=True) + "\n")
    print(design["status"])


if __name__ == "__main__": main()
