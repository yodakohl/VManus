#!/usr/bin/env python3
"""Independent validator for GDT735; intentionally does not import run.py."""
from __future__ import annotations

import csv
import hashlib
import itertools
import json
import shutil
import subprocess
import sys
import tempfile
from collections import Counter
from pathlib import Path

sys.dont_write_bytecode = True


def find_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("repository root not found")


ROOT = find_root(Path(__file__).resolve())
EXP = ROOT / "experiments/yolo/gdt735_historical_semantic_bridge_atlas"
SRC, ART = EXP / "src", EXP / "artifacts"

SCHEMAS = {
    "OPAQUE_96_HEAD_BODY_GRID.tsv": ["bridge_cell_id", "source_experiment", "source_cell_id", "eva_transcription_label", "opaque_head_id", "opaque_source_class", "distributional_subclass", "body", "form", "occurrences", "reader_exact_occurrences", "inherited_body_role_de", "opaque_bridge_reading_de", "literal_head_lexeme", "eva_initial_credit", "relation_credit", "status"],
    "HEAD_FIELD_24_PERMUTATION_DIAGNOSTIC.tsv": ["joint_rank", "mapping_id", "H1_eva_p_field", "H2_eva_s_field", "H3_eva_r_field", "H4_eva_l_field", "target_structural_cells_explained", "structural_fit_rank", "structural_tie_size", "HSR019_tv", "HSR019_rank", "HSR020_tv", "HSR020_rank", "mean_tv", "is_anachronistic_eva_initial_match", "eva_letter_or_initial_credit", "semantic_identification_credit", "status"],
    "HISTORICAL_ENTRY_ATLAS.tsv": ["observation_id", "source_id", "locator", "record_mode", "headword_or_rubric", "observed_slots", "descriptive_slots", "prescriptive_slots", "layout_relation", "evidence_summary", "caveat", "relation_credit", "evidence_tier", "architecture_channel", "voynich_mapping_credit", "one_letter_four_head_code_attested"],
    "HISTORICAL_SOURCE_ARCHITECTURE_MATRIX.tsv": ["source_id", "work", "date_band", "observation_rows", "record_channels", "observed_slots", "descriptive_slots", "prescriptive_slots", "direct_descriptive_observation", "direct_prescriptive_observation", "direct_two_channel_same_source", "actual_four_head_one_letter_code_attested", "voynich_relation_credit", "claim_ceiling"],
    "HISTORICAL_SLOT_CENSUS.tsv": ["slot", "observation_rows", "unique_sources", "source_ids", "descriptive_rows", "prescriptive_rows", "relation_credit"],
    "BRIDGE_MODEL_COMPARISON.tsv": ["model_id", "model_family", "target_96_compatible_cells", "target_literal_head_cells_identified", "historical_actual_four_head_code_sources", "eva_letter_or_initial_credit", "component_export_credit", "literal_lexeme_claim_allowed", "disposition", "reason", "claim_ceiling"],
    "SEMANTIC_BRIDGE_ROLE_DICTIONARY.tsv": ["seed_id", "surface_or_class", "opaque_head_id", "broad_role_family", "working_role_seed", "licensed_rivals", "form_confidence", "semantic_confidence", "literal_lexeme_status", "evidence", "portable_policy", "falsifier", "historical_field_analogy", "eva_letter_or_initial_credit", "component_export_credit", "claim_ceiling"],
    "BRIDGE_DECISION_REGISTER.tsv": ["decision_id", "subject", "decision", "effect", "evidence", "confidence"],
}


class Audit:
    def __init__(self) -> None: self.checks = 0
    def true(self, value: bool, label: str) -> None:
        self.checks += 1
        if not value: raise AssertionError(label)
    def equal(self, got: object, want: object, label: str) -> None:
        self.true(got == want, f"{label}: expected {want!r}, got {got!r}")


def read(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle, delimiter="\t")
        return list(reader.fieldnames or []), list(reader)


def digest(path: Path) -> str: return hashlib.sha256(path.read_bytes()).hexdigest()
def zeros(data: list[dict[str, str]], fields: tuple[str, ...]) -> bool:
    return all(row[field] == "0" for row in data for field in fields)


def replay(audit: Audit) -> None:
    # A mirror preserves repository-relative paths embedded in RESULT.json.
    with tempfile.TemporaryDirectory(prefix="gdt735-validation-") as raw:
        root = Path(raw)
        (root / ".git").mkdir()
        (root / "AGENTS.md").write_text("# validation mirror\n", encoding="utf-8")
        rel_exp = Path("experiments/yolo/gdt735_historical_semantic_bridge_atlas")
        target_exp = root / rel_exp
        (target_exp / "src").mkdir(parents=True)
        for source in SRC.iterdir():
            if source.is_file() and source.name != "validate.py":
                shutil.copy2(source, target_exp / "src" / source.name)
        dependencies = (
            "experiments/yolo/gdt635_initial_head_same_remainder_swaps/artifacts/CONCRETE_FOUR_HEAD_PARADIGMS.tsv",
            "experiments/yolo/gdt635_initial_head_same_remainder_swaps/artifacts/INITIAL_HEAD_SCOPE_PROFILE.tsv",
            "experiments/yolo/gdt636_residual_four_head_semantics/artifacts/RESIDUAL_76_FORM_GRID.tsv",
        )
        for name in dependencies:
            dest = root / name
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(ROOT / name, dest)
        proc = subprocess.run([sys.executable, str(target_exp / "src/run.py")], cwd=root, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        audit.equal(proc.returncode, 0, f"builder replay ({proc.stderr})")
        names = set(SCHEMAS) | {"RESULT.json"}
        audit.equal({p.name for p in (target_exp / "artifacts").iterdir() if p.is_file()}, names, "replay artifact set")
        for name in sorted(names):
            audit.equal((target_exp / "artifacts" / name).read_bytes(), (ART / name).read_bytes(), f"byte replay {name}")
        audit.equal((target_exp / "REPORT.md").read_bytes(), (EXP / "REPORT.md").read_bytes(), "byte replay REPORT")


def main() -> int:
    a = Audit()
    tables = {}
    for name, schema in SCHEMAS.items():
        fields, data = read(ART / name)
        a.equal(fields, schema, f"schema {name}")
        tables[name] = data

    grid = tables["OPAQUE_96_HEAD_BODY_GRID.tsv"]
    a.equal(len(grid), 96, "grid rows")
    a.equal(len({r["bridge_cell_id"] for r in grid}), 96, "unique cells")
    a.equal(len({r["form"] for r in grid}), 96, "unique forms")
    a.equal(len({r["body"] for r in grid}), 24, "unique bodies")
    a.equal(Counter(r["opaque_head_id"] for r in grid), Counter({"H1": 24, "H2": 24, "H3": 24, "H4": 24}), "head balance")
    a.equal(sum(int(r["occurrences"]) for r in grid), 1166, "occurrences")
    a.equal(sum(int(r["reader_exact_occurrences"]) for r in grid), 875, "reader exact")
    a.true(all(r["literal_head_lexeme"] == "UNRESOLVED" for r in grid), "literal heads unresolved")
    a.true(zeros(grid, ("eva_initial_credit", "relation_credit")), "grid credits zero")

    perms = tables["HEAD_FIELD_24_PERMUTATION_DIAGNOSTIC.tsv"]
    a.equal(len(perms), 24, "permutation rows")
    actual_maps = {(r["H1_eva_p_field"], r["H2_eva_s_field"], r["H3_eva_r_field"], r["H4_eva_l_field"]) for r in perms}
    a.equal(actual_maps, set(itertools.permutations(("PULVIS", "SEMEN", "RADIX", "LIGNUM"))), "all permutations")
    a.equal({int(r["joint_rank"]) for r in perms}, set(range(1, 25)), "joint ranks")
    a.true(all(r["structural_fit_rank"] == "1" and r["structural_tie_size"] == "24" and r["target_structural_cells_explained"] == "96" for r in perms), "structural 1/24 tie")
    invalid = [r for r in perms if r["is_anachronistic_eva_initial_match"] == "1"]
    a.equal(len(invalid), 1, "one invalid initial control")
    a.equal((invalid[0]["joint_rank"], invalid[0]["HSR019_rank"], invalid[0]["HSR020_rank"]), ("20", "20", "20"), "invalid ranks")
    a.true(zeros(perms, ("eva_letter_or_initial_credit", "semantic_identification_credit")), "permutation credits zero")

    _, registry = read(SRC / "HISTORICAL_SOURCE_REGISTRY.tsv")
    _, observations = read(SRC / "HISTORICAL_ENTRY_OBSERVATIONS.tsv")
    _, field_counts = read(SRC / "HISTORICAL_FIELD_COUNTS.tsv")
    _, models_in = read(SRC / "BRIDGE_MODEL_SPECS.tsv")
    _, seeds = read(SRC / "SEMANTIC_ROLE_SEEDS.tsv")
    a.equal((len(registry), len(observations), len(field_counts), len(models_in), len(seeds)), (22, 17, 28, 8, 16), "input deck counts")
    a.true(all(r["relation_credit"] == "0" for r in registry + observations + field_counts), "input historical credits zero")

    atlas = tables["HISTORICAL_ENTRY_ATLAS.tsv"]
    matrix = tables["HISTORICAL_SOURCE_ARCHITECTURE_MATRIX.tsv"]
    slots = tables["HISTORICAL_SLOT_CENSUS.tsv"]
    a.equal(len(atlas), 17, "atlas observations")
    a.true(zeros(atlas, ("relation_credit", "voynich_mapping_credit", "one_letter_four_head_code_attested")), "atlas credits zero")
    a.true(zeros(matrix, ("actual_four_head_one_letter_code_attested", "voynich_relation_credit")), "matrix credits/code count zero")
    a.true(zeros(slots, ("relation_credit",)), "slot credits zero")
    a.equal([r["source_id"] for r in matrix if r["direct_two_channel_same_source"] == "1"], ["HSR010"], "one direct two-channel source")

    models = tables["BRIDGE_MODEL_COMPARISON.tsv"]
    roles = tables["SEMANTIC_BRIDGE_ROLE_DICTIONARY.tsv"]
    a.equal((len(models), len(roles)), (8, 16), "model/role counts")
    a.true(zeros(models, ("historical_actual_four_head_code_sources", "eva_letter_or_initial_credit", "component_export_credit", "literal_lexeme_claim_allowed", "target_literal_head_cells_identified")), "model credits zero")
    a.true(zeros(roles, ("eva_letter_or_initial_credit", "component_export_credit")), "role credits zero")
    dispositions = {r["model_id"]: r["disposition"] for r in models}
    a.equal(dispositions["M01"], "REJECTED_ANACHRONISTIC_NEGATIVE_CONTROL", "M01 rejected")
    a.equal(dispositions["M04"], "SELECTED_HISTORICAL_CONTENT_ARCHITECTURE_PRIOR", "M04 selected")
    a.equal(dispositions["M06"], "SELECTED_GENERAL_ENCODING_ARCHITECTURE", "M06 selected")

    result = json.loads((ART / "RESULT.json").read_text(encoding="utf-8"))
    a.equal(result["target"], {"bodies": 24, "cells": 96, "forms": 96, "occurrences": 1166, "reader_exact_occurrences": 875}, "RESULT target")
    a.equal(result["historical"]["direct_two_channel_sources"], ["HSR010"], "RESULT direct source")
    a.equal(result["historical"]["actual_four_head_one_letter_code_sources"], 0, "RESULT code sources")
    a.equal(result["model_dispositions"], dispositions, "RESULT dispositions")
    a.equal(result["permutation_diagnostic"]["invalid_joint_rank"], 20, "RESULT invalid rank")
    a.equal(result["permutation_diagnostic"]["invalid_source_ranks"], {"HSR019": 20, "HSR020": 20}, "RESULT source ranks")
    claims = {"actual_four_head_one_letter_code_found": False, "eva_labels_are_historical_letters": False, "f84_used": False, "f84r_used": False, "literal_head_lexemes_identified": 0, "new_pages_used": 0, "voynich_glyph_values_identified": 0}
    a.equal(result["claims"], claims, "RESULT claims")
    hashes = {str((ART / name).relative_to(ROOT)): digest(ART / name) for name in SCHEMAS}
    hashes[str((EXP / "REPORT.md").relative_to(ROOT))] = digest(EXP / "REPORT.md")
    a.equal(result["artifact_hashes"], dict(sorted(hashes.items())), "RESULT hashes")
    corpus = "\n".join((ART / n).read_text(encoding="utf-8") for n in SCHEMAS) + (EXP / "REPORT.md").read_text(encoding="utf-8")
    forbidden_fragments = ("/" + "home/", "\\" + "Users\\", "f84.", "f84r.")
    a.true(not any(x in corpus for x in forbidden_fragments), "privacy/sealed references")

    replay(a)
    validation = {
        "schema": "GDT735_INDEPENDENT_VALIDATION_V1", "status": "PASS",
        "checks": a.checks, "builder_replay": "BYTE_IDENTICAL_TSV_REPORT_RESULT",
        "validated_artifact_hashes": ({name: digest(ART / name) for name in sorted(set(SCHEMAS) | {"RESULT.json"})} | {"REPORT.md": digest(EXP / "REPORT.md")}),
    }
    (ART / "VALIDATION.json").write_text(json.dumps(validation, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"checks": a.checks, "status": "PASS"}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
