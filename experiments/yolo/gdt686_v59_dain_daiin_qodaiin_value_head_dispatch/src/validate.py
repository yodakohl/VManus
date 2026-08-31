#!/usr/bin/env python3
"""Independently rebuild and validate GDT686."""

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
EXP = ROOT / "experiments/yolo/gdt686_v59_dain_daiin_qodaiin_value_head_dispatch"
ART = EXP / "artifacts"
RUN_PATH = EXP / "src/run.py"
V58_PATH = ROOT / "experiments/yolo/gdt685_v58_ch_sh_t_ol_ansatz_dispatch/artifacts/V58_51_LINE_READER.tsv"
PATCH_PATH = EXP / "src/V59_VALUE_PATCH_SPECS.tsv"


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
    spec = importlib.util.spec_from_file_location("gdt686_run", RUN_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load GDT686 builder")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def aligned_chunks(text: str) -> list[str]:
    return (text[:-1] if text.endswith(".") else text).split(" · ")


def main() -> int:
    audit = Audit()
    generated = {
        "TARGET_955_VALUE_HEAD_CENSUS.tsv",
        "SURFACE_VALUE_DISPATCH_SUMMARY.tsv",
        "DIRECT_AXIS_EVIDENCE_SUMMARY.tsv",
        "QODAIIN_41_CONTEXT_AUDIT.tsv",
        "COMPOSITION_EVIDENCE.tsv",
        "HYPOTHESIS_COMPARISON.tsv",
        "COUNTEREXAMPLE_AUDIT.tsv",
        "V59_51_LINE_READER.tsv",
        "V59_PATCHED_LINES.tsv",
        "V59_TARGET_POSITION_DEBT_DELTA.tsv",
        "V59_DEBT_SUMMARY.tsv",
        "GDT686_V59_LOCAL_VALUE_READER.md",
    }
    result = json.loads((ART / "RESULT.json").read_text(encoding="utf-8"))
    audit.check(set(result["files"]) == generated, "exact generated inventory")
    for name in [*sorted(generated), "RESULT.json"]:
        audit.check((ART / name).is_file(), f"missing artifact {name}")

    builder = load_builder()
    with tempfile.TemporaryDirectory(prefix="gdt686-rebuild-") as raw_temp:
        rebuilt = Path(raw_temp)
        rebuilt_result = builder.build(rebuilt)
        audit.check(rebuilt_result["status"] == result["status"], "rebuilt status")
        for name in [*sorted(generated), "RESULT.json"]:
            audit.check((ART / name).read_bytes() == (rebuilt / name).read_bytes(), f"byte rebuild {name}")

    census = read_tsv(ART / "TARGET_955_VALUE_HEAD_CENSUS.tsv")
    surfaces = read_tsv(ART / "SURFACE_VALUE_DISPATCH_SUMMARY.tsv")
    axes = read_tsv(ART / "DIRECT_AXIS_EVIDENCE_SUMMARY.tsv")
    qod = read_tsv(ART / "QODAIIN_41_CONTEXT_AUDIT.tsv")
    evidence = read_tsv(ART / "COMPOSITION_EVIDENCE.tsv")
    hypotheses = read_tsv(ART / "HYPOTHESIS_COMPARISON.tsv")
    counterexamples = read_tsv(ART / "COUNTEREXAMPLE_AUDIT.tsv")
    v59 = read_tsv(ART / "V59_51_LINE_READER.tsv")
    patches = read_tsv(ART / "V59_PATCHED_LINES.tsv")
    debt_delta = read_tsv(ART / "V59_TARGET_POSITION_DEBT_DELTA.tsv")
    debt_summary = read_tsv(ART / "V59_DEBT_SUMMARY.tsv")
    specs = read_tsv(PATCH_PATH)
    v58 = read_tsv(V58_PATH)

    audit.check(len(census) == 955, "955 target positions")
    audit.check(len({(row["locus"], row["token_index"]) for row in census}) == 955, "955 unique positions")
    audit.check(Counter(row["surface"] for row in census) == {"dain": 193, "daiin": 721, "qodaiin": 41}, "surface counts")
    audit.check(sum(int(row["triple_reader_token_stable"]) for row in census) == 785, "785 triple-reader exact")
    audit.check(len({row["page"] for row in census}) == 174, "174-page union")
    audit.check(len({row["locus"] for row in census}) == 810, "810-locus union")
    audit.check(not any(row["page"].lower().startswith("f84") for row in census), "sealed pages absent")
    audit.check(Counter(row["line_position"] for row in census) == {"FIRST": 183, "MIDDLE": 628, "LAST": 144}, "line positions")
    audit.check(Counter(row["section"] for row in census) == {"H": 554, "S": 196, "B": 100, "P": 55, "T": 38, "C": 12}, "register spread")
    audit.check(all(row["decision"] == "VALUE_LEVEL_FIXED__AXIS_BY_VISIBLE_OR_KEYED_HEAD" for row in census), "one census decision")

    expected_modes = {
        "DIRECT_QUALITY_GRADE": 75,
        "DIRECT_PART_OR_MATERIAL_AMOUNT": 53,
        "BARE_OL_VALUE_AXIS_OPEN": 11,
        "D_VALUE_OUTER_HEAD_OPEN": 775,
        "QOD_HEAD_AXIS_OPEN": 41,
    }
    audit.check(Counter(row["global_context_mode"] for row in census) == expected_modes, "global axis partition")
    audit.check({row["context_mode"]: int(row["positions"]) for row in axes} == expected_modes, "axis summary partition")
    audit.check({row["context_mode"]: row["axis"] for row in axes} == {
        "DIRECT_QUALITY_GRADE": "GRADE",
        "DIRECT_PART_OR_MATERIAL_AMOUNT": "AMOUNT",
        "BARE_OL_VALUE_AXIS_OPEN": "OPEN",
        "D_VALUE_OUTER_HEAD_OPEN": "OPEN",
        "QOD_HEAD_AXIS_OPEN": "OPEN",
    }, "axis labels")

    audit.check(len(surfaces) == 3, "three surface summaries")
    expected_surfaces = {
        "dain": (193, 90, 182, 149, 46, 120, 27, 11, 5, 3, 174),
        "daiin": (721, 169, 638, 602, 136, 469, 116, 64, 48, 8, 601),
        "qodaiin": (41, 25, 40, 34, 1, 39, 1, 0, 0, 0, 41),
    }
    for row in surfaces:
        observed = tuple(int(row[field]) for field in (
            "occurrences", "pages", "loci", "triple_reader_exact_occurrences",
            "line_first", "line_middle", "line_last", "direct_quality_grade",
            "direct_part_or_material_amount", "bare_ol_axis_open", "outer_or_qod_head_open",
        ))
        audit.check(observed == expected_surfaces[row["surface"]], f"surface summary {row['surface']}")

    audit.check(len(qod) == 41, "41 qod audit rows")
    audit.check(len({(row["locus"], row["token_index"]) for row in qod}) == 41, "qod keys unique")
    audit.check(sum(int(row["reader_exact"]) for row in qod) == 34, "34 qod reader exact")
    audit.check(sum(int(row["split_normalized"]) for row in qod) == 36, "36 qod split normalized")
    audit.check(next(row for row in qod if row["locus"] == "f86v3.25")["reader_boundary"] == "RF1B_QOD_AIIN_SPLIT", "qod aiin boundary")
    audit.check(next(row for row in qod if row["locus"] == "f95r2.1")["reader_boundary"] == "RF1B_QO_DAIIN_SPLIT", "qo daiin boundary")
    audit.check(all(row["global_dispatch"] == "QOD_VALUE_III__HEAD_AND_AXIS_OPEN" for row in qod), "qod globally open")

    audit.check(len(evidence) == 6, "six evidence rows")
    audit.check(len(hypotheses) == 5, "five hypotheses")
    audit.check(hypotheses[0]["hypothesis"] == "ORDERED_VALUE_LEVEL_PLUS_VISIBLE_OR_KEYED_HEAD" and hypotheses[0]["disposition"] == "PRIMARY", "head dispatch primary")
    audit.check(all(row["disposition"].startswith("REJECT_GLOBAL") for row in hypotheses if row["hypothesis"].startswith("UNIVERSAL_")), "both universal axes rejected")
    audit.check(len(counterexamples) == 5, "five counterexample classes")

    audit.check(len(specs) == 11, "eleven patch specs")
    audit.check(Counter(row["axis"] for row in specs) == {"GRADE": 4, "AMOUNT": 7}, "four grade seven amount specs")
    audit.check(Counter(row["confidence"] for row in specs) == {"AMBER": 10, "GREEN": 1}, "working confidence distribution")
    audit.check(len(v59) == 51, "51 V59 lines")
    audit.check(sum(int(row["token_count"]) for row in v59) == 479, "479 V59 positions")
    audit.check(sum(int(row["action_positions"]) for row in v59) == 86, "86 actions preserved")
    audit.check(sum(int(row["v59_semantic_revisions"]) for row in v59) == 11, "eleven V59 revisions")
    audit.check(sum(int(row["v59_semantic_revisions"]) > 0 for row in v59) == 10, "ten revised lines")
    audit.check(len(patches) == 10 and sum(int(row["revisions"]) for row in patches) == 11, "patch table exact")
    audit.check({row["locus"] for row in patches} == {"f10r.2", "f112v.10", "f116r.12", "f56r.6", "f76v.10", "f83v.12", "f86v3.13", "f86v6.5", "f88r.19", "f8r.15"}, "exact patched loci")

    changed_literals = set()
    changed_aligned = set()
    old_literals = {}
    new_literals = {}
    surface_by_key = {}
    for old_row, new_row in zip(v58, v59):
        audit.check(old_row["locus"] == new_row["locus"], "V58/V59 order preserved")
        tokens = old_row["zl3b_line"].split()
        old_lit = old_row["literal_token_glosses_de"].split(" | ")
        new_lit = new_row["literal_token_glosses_de"].split(" | ")
        old_al = aligned_chunks(old_row["aligned_line_de"])
        new_al = aligned_chunks(new_row["aligned_line_de"])
        audit.check(len(tokens) == len(old_lit) == len(new_lit) == len(old_al) == len(new_al), f"line alignment {old_row['locus']}")
        for ordinal, (surface, before_lit, after_lit, before_al, after_al) in enumerate(zip(tokens, old_lit, new_lit, old_al, new_al), 1):
            key = (old_row["locus"], ordinal)
            old_literals[key] = before_lit
            new_literals[key] = after_lit
            surface_by_key[key] = surface
            if before_lit != after_lit:
                changed_literals.add(key)
            if before_al != after_al:
                changed_aligned.add(key)
    spec_keys = {(row["locus"], int(row["ordinal"])) for row in specs}
    audit.check(changed_literals == spec_keys, "only eleven literal positions changed")
    audit.check(changed_aligned == spec_keys, "only eleven aligned positions changed")
    audit.check(Counter(surface_by_key[key] for key in changed_literals) == {"dain": 3, "daiin": 7, "qodaiin": 1}, "changed surfaces exact")
    audit.check(all("/" not in new_literals[key] and " oder " not in new_literals[key] for key in changed_literals), "no slash alternative remains")
    audit.check(all(old_literals[key] == new_literals[key] for key in old_literals if key not in spec_keys), "468 literal positions preserved")

    audit.check(len(debt_delta) == 11, "eleven debt delta rows")
    audit.check(Counter(row["new_axis"] for row in debt_delta) == {"GRADE": 4, "AMOUNT": 7}, "debt axes exact")
    audit.check(all(row["old_strict_card_debt"] == "1" and row["new_strict_card_debt"] == "0" for row in debt_delta), "strict debt removed")
    audit.check(Counter(row["old_mechanical_debt"] for row in debt_delta) == {"1": 9, "0": 2}, "nine old mechanical debts")
    audit.check(all(row["new_mechanical_debt"] == "0" and row["new_specificity_open"] == "0" for row in debt_delta), "local axes close mechanical and broad debt")
    summary = {row["metric"]: row for row in debt_summary}
    expected_debt = {
        "strict_card_debt_positions": (131, 120),
        "mechanical_visible_debt_union_positions": (172, 163),
        "mechanical_flag_memberships": (186, 177),
        "broad_specificity_open_positions": (335, 324),
        "four_layer_union_with_low_confidence_positions": (381, 370),
        "mechanical_class:NON_SINGLE_GLOSS": (36, 27),
    }
    for metric, pair in expected_debt.items():
        audit.check((int(summary[metric]["v58_before"]), int(summary[metric]["v59_after"])) == pair, f"debt summary {metric}")

    audit.check(result["basis"] == {
        "bare_ol_axis_open_positions": 11,
        "d_head_occurrences": 914,
        "d_outer_head_open_positions": 775,
        "direct_part_or_material_amount_positions": 53,
        "direct_quality_grade_positions": 75,
        "f84": "FORBIDDEN",
        "f84r": "FORBIDDEN",
        "new_pages_opened": 0,
        "qod_head_axis_open_positions": 41,
        "qod_head_occurrences": 41,
        "qod_reader_exact_positions": 34,
        "qod_split_normalized_positions": 36,
        "target_loci_union": 810,
        "target_occurrences": 955,
        "target_pages_union": 174,
        "triple_reader_exact_occurrences": 785,
    }, "result basis exact")
    audit.check(result["v59"] == {
        "action_positions": 86,
        "amount_bindings": 7,
        "broad_specificity_open_positions_after": 324,
        "four_layer_union_positions_after": 370,
        "grade_bindings": 4,
        "lines": 51,
        "lines_revised": 10,
        "mechanical_flag_memberships_after": 177,
        "mechanical_visible_debt_union_positions_after": 163,
        "positions": 479,
        "positions_revised": 11,
        "positions_without_current_debt_or_confidence_flag": 109,
        "strict_card_debt_positions_after": 120,
    }, "result V59 exact")
    audit.check(result["status"] == "PASS_955_VALUE_HEAD_CENSUS__REJECT_UNIVERSAL_AXIS__V59_FOUR_GRADES_SEVEN_AMOUNTS", "result status")
    audit.check("no value token invents an operation" in result["claim_ceiling"] and "no ingredient" in result["claim_ceiling"], "claim ceiling retained")
    for name, digest in result["files"].items():
        audit.check(sha256(ART / name) == digest, f"hash bound {name}")

    validation = {
        "status": "PASS",
        "checks": audit.checks,
        "byte_rebuilds": len(generated) + 1,
        "target_occurrences": 955,
        "triple_reader_exact_occurrences": 785,
        "direct_quality_grade_positions": 75,
        "direct_part_or_material_amount_positions": 53,
        "qod_head_axis_open_positions": 41,
        "v59_positions_revised": 11,
        "v59_grade_bindings": 4,
        "v59_amount_bindings": 7,
        "strict_debt_positions_after": 120,
        "mechanical_debt_union_after": 163,
        "sealed_pages_absent": True,
    }
    (ART / "VALIDATION.json").write_text(json.dumps(validation, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(validation, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
