#!/usr/bin/env python3
"""Independently rebuild and validate GDT685."""

from __future__ import annotations

import csv
import hashlib
import importlib.util
import json
import sys
import tempfile
from collections import Counter
from pathlib import Path

sys.dont_write_bytecode = True


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
EXP = ROOT / "experiments/yolo/gdt685_v58_ch_sh_t_ol_ansatz_dispatch"
ART = EXP / "artifacts"
RUN_PATH = EXP / "src/run.py"
V57_PATH = ROOT / "experiments/yolo/gdt683_ol_semantic_debt_reconciliation/artifacts/V57_51_LINE_READER.tsv"


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class Audit:
    def __init__(self) -> None:
        self.checks = 0

    def check(self, condition: bool, label: str) -> None:
        self.checks += 1
        if not condition:
            raise AssertionError(label)


def load_builder():
    spec = importlib.util.spec_from_file_location("gdt685_run", RUN_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load GDT685 builder")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main() -> int:
    audit = Audit()
    expected_generated = {
        "TARGET_540_STATE_CELL_CENSUS.tsv",
        "RELATED_57_VALUE_REALIZATIONS.tsv",
        "TARGET_OL_CONTACTS.tsv",
        "SURFACE_STATE_DISPATCH_SUMMARY.tsv",
        "CONTEXT_MODE_SUMMARY.tsv",
        "COMPOSITION_EVIDENCE.tsv",
        "HYPOTHESIS_COMPARISON.tsv",
        "COUNTEREXAMPLE_AUDIT.tsv",
        "V58_51_LINE_READER.tsv",
        "V58_PATCHED_LINES.tsv",
        "V58_TARGET_POSITION_DEBT_DELTA.tsv",
        "V58_DEBT_SUMMARY.tsv",
        "GDT685_V58_STATE_CELL_READER.md",
    }
    result = json.loads((ART / "RESULT.json").read_text(encoding="utf-8"))
    audit.check(set(result["files"]) == expected_generated, "exact generated artifact inventory")
    for name in [*sorted(expected_generated), "RESULT.json"]:
        audit.check((ART / name).is_file(), f"missing artifact {name}")

    builder = load_builder()
    with tempfile.TemporaryDirectory(prefix="gdt685-rebuild-") as raw_temp:
        rebuilt = Path(raw_temp)
        rebuilt_result = builder.build(rebuilt)
        audit.check(rebuilt_result["status"] == result["status"], "rebuilt status")
        for name in [*sorted(expected_generated), "RESULT.json"]:
            audit.check((ART / name).read_bytes() == (rebuilt / name).read_bytes(), f"byte rebuild {name}")

    census = read_tsv(ART / "TARGET_540_STATE_CELL_CENSUS.tsv")
    values = read_tsv(ART / "RELATED_57_VALUE_REALIZATIONS.tsv")
    contacts = read_tsv(ART / "TARGET_OL_CONTACTS.tsv")
    surfaces = read_tsv(ART / "SURFACE_STATE_DISPATCH_SUMMARY.tsv")
    contexts = read_tsv(ART / "CONTEXT_MODE_SUMMARY.tsv")
    evidence = read_tsv(ART / "COMPOSITION_EVIDENCE.tsv")
    hypotheses = read_tsv(ART / "HYPOTHESIS_COMPARISON.tsv")
    counterexamples = read_tsv(ART / "COUNTEREXAMPLE_AUDIT.tsv")
    v58 = read_tsv(ART / "V58_51_LINE_READER.tsv")
    patches = read_tsv(ART / "V58_PATCHED_LINES.tsv")
    debt_delta = read_tsv(ART / "V58_TARGET_POSITION_DEBT_DELTA.tsv")
    debt_summary = read_tsv(ART / "V58_DEBT_SUMMARY.tsv")
    v57 = read_tsv(V57_PATH)

    audit.check(len(census) == 540, "540 target positions")
    audit.check(len({(row["locus"], row["token_index"]) for row in census}) == 540, "540 unique occurrence keys")
    audit.check(Counter(row["surface"] for row in census) == {"chol": 343, "shol": 163, "tol": 34}, "target surface counts")
    audit.check(Counter(row["reader_status"] for row in census) == {"TRIPLE_READER_EXACT": 476, "ZL3B_EXACT__ALTERNATE_READER_VARIANT": 64}, "reader status counts")
    audit.check(all(row["decision"] == "ACCEPT_STATE_CELL__REJECT_UNIVERSAL_ANSATZ_HEAD" for row in census), "one target decision")
    audit.check({row["surface"]: row["default_de"] for row in surfaces} == {"chol": "trocken", "shol": "feucht", "tol": "kalt"}, "state defaults exact")
    audit.check(all(row["ol_function"].endswith("GERMAN_CONTRIBUTION_ZERO_WITH_VISIBLE_CORE") for row in census), "OL carrier contribution explicit")
    audit.check(not any(row["page"].lower().startswith("f84") for row in census), "sealed pages absent")
    audit.check(len({row["page"] for row in census}) == 151, "151-page target union")
    audit.check(Counter(row["section"] for row in census) == {"H": 342, "S": 106, "P": 38, "B": 29, "T": 19, "C": 6}, "target register spread")
    audit.check(Counter(row["line_position"] for row in census) == {"MIDDLE": 477, "FIRST": 54, "LAST": 9}, "target line positions")

    expected_surface_rows = {
        "chol": {"occurrences": 343, "pages": 125, "loci": 297, "reader": 303, "degree": 37, "values": 43, "nonseparate": 6, "free_ol": 7, "bound_ol": 2, "v58": 6},
        "shol": {"occurrences": 163, "pages": 86, "loci": 151, "reader": 146, "degree": 11, "values": 13, "nonseparate": 2, "free_ol": 1, "bound_ol": 0, "v58": 1},
        "tol": {"occurrences": 34, "pages": 25, "loci": 34, "reader": 27, "degree": 1, "values": 1, "nonseparate": 0, "free_ol": 0, "bound_ol": 0, "v58": 1},
    }
    audit.check(len(surfaces) == 3, "three dispatch summary rows")
    for row in surfaces:
        expected = expected_surface_rows[row["surface"]]
        audit.check(int(row["occurrences"]) == expected["occurrences"], f"{row['surface']} occurrences")
        audit.check(int(row["pages"]) == expected["pages"], f"{row['surface']} pages")
        audit.check(int(row["loci"]) == expected["loci"], f"{row['surface']} loci")
        audit.check(int(row["triple_reader_exact_occurrences"]) == expected["reader"], f"{row['surface']} reader exact")
        audit.check(int(row["exact_separate_degree_positions"]) == expected["degree"], f"{row['surface']} degree exact")
        audit.check(int(row["all_value_realizations"]) == expected["values"], f"{row['surface']} value realizations")
        audit.check(int(row["direct_or_fused_value_realizations"]) == expected["nonseparate"], f"{row['surface']} direct/fused")
        audit.check(int(row["free_ol_contacts"]) == expected["free_ol"], f"{row['surface']} free OL contacts")
        audit.check(int(row["reader_bound_ol_contacts"]) == expected["bound_ol"], f"{row['surface']} bound OL contacts")
        audit.check(int(row["v57_positions_revised"]) == expected["v58"], f"{row['surface']} V58 positions")

    audit.check(len(values) == 57, "57 value realizations")
    audit.check(Counter(row["surface"] for row in values) == {"chol": 43, "shol": 13, "tol": 1}, "value realization surfaces")
    audit.check(Counter(row["realization_mode"] for row in values) == {"SEPARATE_D_VALUE": 49, "FUSED_D_VALUE": 5, "DIRECT_A_VALUE": 3}, "value realization modes")
    audit.check(sum(row["visible_part_surface"] != "NONE" for row in values) == 7, "seven visible part value contacts")
    audit.check(sum(row["visible_part_surface"] != "NONE" and row["realization_mode"] == "SEPARATE_D_VALUE" for row in values) == 6, "six exact separate part heads")

    expected_contexts = {
        "PARALLEL_OR_CONTRASTING_QUALITY_CELLS": 79,
        "QUALITY_CELL_NEXT_TO_OL_CONTACT": 10,
        "QUALITY_DEGREE_HEAD_OPEN": 43,
        "QUALITY_DEGREE_WITH_VISIBLE_PART_HEAD": 6,
        "QUALITY_STATE_HEAD_OPEN": 270,
        "QUALITY_WITH_LOCAL_MATERIA_CANDIDATE": 132,
    }
    audit.check(Counter(row["context_mode"] for row in census) == expected_contexts, "context modes exact")
    audit.check({row["context_mode"]: int(row["positions"]) for row in contexts} == expected_contexts, "context summary exact")

    audit.check(len(contacts) == 10, "ten visible target/OL contacts")
    audit.check(Counter(row["contact_class"] for row in contacts) == {"FREE_SEPARATE_OL": 8, "BOUND_READER_COMPOUND": 2}, "eight free and two bound OL contacts")
    audit.check(Counter(row["surface"] for row in contacts) == {"chol": 9, "shol": 1}, "OL contact surface counts")
    bound_keys = {(row["locus"], row["target_token_index"], row["ol_token_index"]) for row in contacts if row["contact_class"] == "BOUND_READER_COMPOUND"}
    audit.check(bound_keys == {("f21r.6", "9", "10"), ("f58r.31", "5", "6")}, "exact reader-bound OL contacts")

    audit.check(len(evidence) == 7, "seven composition evidence rows")
    audit.check(len(hypotheses) == 5, "five ranked hypotheses")
    audit.check(hypotheses[0]["hypothesis"] == "STATE_CELL_WITH_OUTER_OR_INHERITED_HEAD" and hypotheses[0]["disposition"] == "PRIMARY", "state-cell hypothesis primary")
    universal = next(row for row in hypotheses if row["hypothesis"] == "UNIVERSAL_STATE_PLUS_OL_ANSATZ_HEAD")
    audit.check(universal["disposition"].startswith("REJECT_GLOBAL"), "universal Ansatz rejected")
    audit.check(len(counterexamples) == 5, "five counterexample classes")
    audit.check({row["counterexample"] for row in counterexamples} == {"VISIBLE_PART_QUALITY_DEGREE", "FREE_OL_CONTACT", "QUALITY_CELL_RUNS", "E_OL_HEAD_CONTRAST", "ALTERNATE_READER_BOUNDARY"}, "counterexample inventory")

    audit.check(len(v58) == 51, "51 V58 lines")
    audit.check(sum(int(row["token_count"]) for row in v58) == 479, "479 V58 positions")
    audit.check(sum(int(row["action_positions"]) for row in v58) == 86, "86 action licenses preserved")
    audit.check(sum(int(row["v58_semantic_revisions"]) for row in v58) == 8, "eight V58 semantic revisions")
    audit.check(sum(int(row["v58_semantic_revisions"]) > 0 for row in v58) == 7, "seven V58 revised lines")
    audit.check(len(patches) == 7 and sum(int(row["revisions"]) for row in patches) == 8, "patch artifact exact")
    audit.check({row["locus"] for row in patches} == {"f27r.9", "f30r.9", "f80v.35", "f86v3.18", "f86v3.19", "f86v6.5", "f8r.15"}, "exact patched loci")

    old_chunks: dict[tuple[str, int], str] = {}
    new_chunks: dict[tuple[str, int], str] = {}
    surfaces_by_key: dict[tuple[str, int], str] = {}
    for old_row, new_row in zip(v57, v58):
        audit.check(old_row["locus"] == new_row["locus"], "V57/V58 line order preserved")
        tokens = old_row["zl3b_line"].split()
        old_glosses = old_row["literal_token_glosses_de"].split(" | ")
        new_glosses = new_row["literal_token_glosses_de"].split(" | ")
        audit.check(len(tokens) == len(old_glosses) == len(new_glosses), f"V58 alignment {old_row['locus']}")
        for ordinal, (surface, old_gloss, new_gloss) in enumerate(zip(tokens, old_glosses, new_glosses), 1):
            key = (old_row["locus"], ordinal)
            old_chunks[key] = old_gloss
            new_chunks[key] = new_gloss
            surfaces_by_key[key] = surface
    changed = {key for key in old_chunks if old_chunks[key] != new_chunks[key]}
    audit.check(len(changed) == 8, "only eight literal chunks changed")
    audit.check(Counter(surfaces_by_key[key] for key in changed) == {"chol": 6, "shol": 1, "tol": 1}, "changed surface set")
    audit.check(all(new_chunks[key] == {"chol": "trocken", "shol": "feucht", "tol": "kalt"}[surfaces_by_key[key]] for key in changed), "changed state defaults exact")
    audit.check(all(old_chunks[key] == new_chunks[key] for key in old_chunks if key not in changed), "471 literal chunks byte-preserved")
    target_census_keys = {(row["locus"], int(row["token_index"])): row for row in census}
    audit.check(all(target_census_keys[key]["reader_status"] == "TRIPLE_READER_EXACT" for key in changed), "all eight V58 targets reader exact")
    audit.check(not any("Trockengut" in row["practical_translation_de"] or "Feuchtgut" in row["practical_translation_de"] or "Kaltes Gut" in row["practical_translation_de"] for row in v58 if int(row["v58_semantic_revisions"])), "generic target nouns removed from patched prose")

    audit.check(len(debt_delta) == 8, "eight debt deltas")
    audit.check(all(row["old_primary_class"] == "D3_GENERIC_CARRIER" and row["new_primary_class"] == "C2_STATE_WITHOUT_OBJECT" for row in debt_delta), "generic carrier becomes honest state")
    audit.check(all(row["old_strict_card_debt"] == "1" and row["new_strict_card_debt"] == "0" for row in debt_delta), "strict debt removed")
    audit.check(all(row["old_mechanical_debt"] == "1" and row["new_mechanical_debt"] == "1" for row in debt_delta), "mechanical head debt retained")
    audit.check(all(row["new_mechanical_debt_flags"] == "STATE_ONLY_NO_OBJECT" for row in debt_delta), "state-only mechanical flag exact")
    summary_map = {row["metric"]: row for row in debt_summary}
    audit.check((summary_map["strict_card_debt_positions"]["v57_before"], summary_map["strict_card_debt_positions"]["v58_after"]) == ("139", "131"), "strict debt 139 to 131")
    audit.check((summary_map["mechanical_visible_debt_union_positions"]["v57_before"], summary_map["mechanical_visible_debt_union_positions"]["v58_after"]) == ("172", "172"), "mechanical union honest")
    audit.check((summary_map["mechanical_flag_memberships"]["v57_before"], summary_map["mechanical_flag_memberships"]["v58_after"]) == ("194", "186"), "mechanical memberships 194 to 186")
    audit.check(summary_map["mechanical_class:NON_SINGLE_GLOSS"]["v58_after"] == "36", "non-single flags 36")
    audit.check(summary_map["mechanical_class:HARD_GENERIC_CARRIER"]["v58_after"] == "39", "hard generic flags 39")
    audit.check(summary_map["mechanical_class:STATE_ONLY_NO_OBJECT"]["v58_after"] == "73", "state-only flags 73")

    audit.check(result["basis"] == {
        "alternate_reader_variant_occurrences": 64,
        "core_ol_occurrences": 935,
        "core_ol_pages": 167,
        "core_ol_triple_reader_exact_occurrences": 833,
        "exact_separate_degree_target_positions": 49,
        "f84": "FORBIDDEN",
        "f84r": "FORBIDDEN",
        "free_ol_contacts": 8,
        "new_pages_opened": 0,
        "occupied_core_ol_cells": 23,
        "possible_core_ol_cells": 24,
        "reader_bound_ol_contacts": 2,
        "target_occurrences": 540,
        "target_pages_union": 151,
        "triple_reader_exact_occurrences": 476,
        "value_realizations": 57,
        "visible_ol_contacts": 10,
        "visible_part_contacts": 7,
    }, "result basis exact")
    audit.check(result["v58"] == {
        "action_positions": 86,
        "broad_specificity_open_positions_after": 335,
        "four_layer_union_positions_after": 381,
        "lines": 51,
        "lines_revised": 7,
        "mechanical_flag_memberships_after": 186,
        "mechanical_visible_debt_union_positions_after": 172,
        "positions": 479,
        "positions_revised": 8,
        "strict_card_debt_positions_after": 131,
    }, "result V58 exact")
    audit.check(result["decision"]["primary"] == "STATE_CELL_WITH_OUTER_OR_INHERITED_HEAD", "result decision")
    audit.check(result["status"] == "REJECT_UNIVERSAL_ANSATZ_HEAD__PASS_540_STATE_CELL_DISPATCH__V58_EIGHT_GENERIC_HEADS_REMOVED", "result status")
    audit.check("No ingredient" in result["claim_ceiling"] and "no new page" in result["claim_ceiling"], "claim ceiling retained")

    for name, digest in result["files"].items():
        audit.check(sha256(ART / name) == digest, f"hash bound {name}")

    validation = {
        "status": "PASS",
        "checks": audit.checks,
        "byte_rebuilds": len(expected_generated) + 1,
        "target_occurrences": 540,
        "triple_reader_exact_occurrences": 476,
        "core_ol_occurrences": 935,
        "value_realizations": 57,
        "visible_part_contacts": 7,
        "free_ol_contacts": 8,
        "reader_bound_ol_contacts": 2,
        "v58_positions_revised": 8,
        "strict_debt_positions_after": 131,
        "mechanical_debt_union_after": 172,
        "sealed_pages_absent": True,
    }
    (ART / "VALIDATION.json").write_text(
        json.dumps(validation, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(json.dumps(validation, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
