#!/usr/bin/env python3
"""Reproduce the GDT606 historical-capacity mixed-codebook attack."""
from __future__ import annotations

import subprocess
import sys
import tempfile
import hashlib
import json
from pathlib import Path

def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
SRC = Path(__file__).resolve().parent
HERE = SRC.parent
OUT = HERE / "artifacts"


def run(*arguments: str) -> None:
    subprocess.run([sys.executable, *arguments], cwd=ROOT, check=True)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_binding_inventory() -> None:
    source_names = (
        "materialize.py", "build_units.py", "mixed_codebook_attack.py",
        "carrier_stability_audit.py", "run.py", "validate.py",
    )
    artifact_names = (
        "guarded_rows.tsv", "unit_sequences.json", "mixed_attack_result.json",
        "carrier_stability_result.json", "complete_mappings.tsv",
        "primary_unit_stability.tsv", "stable_held_words.tsv",
        "stable_held_fragments.tsv", "positional_word_carrier_audit.tsv",
        "carrier_stable_words.tsv", "carrier_stable_fragments.tsv",
        "held_decodes_latin.tsv", "held_decodes_old_italian.tsv",
        "held_decodes_middle_high_german.tsv",
        "category_stability_all_configs_latin.tsv",
        "category_stability_all_configs_old_italian.tsv",
        "category_stability_all_configs_middle_high_german.tsv",
    )
    inventory = {
        "schema": "gdt606-binding-inventory-v1",
        "decision": "MIXED_CODEBOOK_UNSTABLE_PSEUDOTEXT__STRUCTURAL_WHOLE_WORD_CATEGORY_LEAD",
        "sources": {name: sha256(SRC / name) for name in source_names},
        "artifacts": {name: sha256(OUT / name) for name in artifact_names},
        "sealed_data": {"f84": "FORBIDDEN_AND_ABSENT", "f84r": "FORBIDDEN_AND_ABSENT"},
    }
    (OUT / "binding_inventory.json").write_text(
        json.dumps(inventory, indent=2, sort_keys=True) + "\n"
    )


def main() -> int:
    run(str(SRC / "materialize.py"))
    run(str(SRC / "build_units.py"))
    with tempfile.TemporaryDirectory(prefix="gdt606-references-") as temporary:
        run(
            str(ROOT / "experiments/yolo/gdt604_naibbe_frozen_target_attack/src/fetch_references.py"),
            "--output-dir", temporary,
        )
        run(
            str(SRC / "mixed_codebook_attack.py"),
            "--reference-dir", temporary,
            "--workers", "9",
            "--primary-iterations", "8000",
            "--sensitivity-iterations", "4000",
        )
    run(str(SRC / "carrier_stability_audit.py"))
    write_binding_inventory()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
