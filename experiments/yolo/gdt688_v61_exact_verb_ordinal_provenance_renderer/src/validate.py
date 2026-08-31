#!/usr/bin/env python3
"""Independently rebuild and validate GDT688/V61."""

from __future__ import annotations

import csv
import hashlib
import importlib.util
import json
import re
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
EXP = ROOT / "experiments/yolo/gdt688_v61_exact_verb_ordinal_provenance_renderer"
ART = EXP / "artifacts"
RUN_PATH = EXP / "src/run.py"
RULE_PATH = EXP / "src/V61_VERB_RULES.tsv"
V60_PATH = ROOT / "experiments/yolo/gdt687_v60_dchey_y_dy_action_result_boundary_dispatch/artifacts/V60_51_LINE_READER.tsv"


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def int_set(value: str) -> set[int]:
    return {int(item) for item in value.split("|") if item and item != "NONE"}


class Audit:
    def __init__(self) -> None:
        self.checks = 0

    def check(self, condition: bool, label: str) -> None:
        self.checks += 1
        if not condition:
            raise AssertionError(label)


def load_builder():
    spec = importlib.util.spec_from_file_location("gdt688_run", RUN_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load GDT688 builder")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def render(glosses: list[str]) -> str:
    text = ""
    for gloss in glosses:
        if gloss == ";":
            text = text.rstrip(" ,;.") + ";"
        elif gloss == ".":
            text = text.rstrip(" ,;.") + "."
        elif not text:
            text = gloss
        elif text.endswith((";", ".", ":")):
            text += " " + gloss
        else:
            text += "; " + gloss
    if text and not text.endswith("."):
        text += "."
    return text[:1].upper() + text[1:]


def main() -> int:
    audit = Audit()
    generated = {
        "COUNTEREXAMPLE_AUDIT.tsv",
        "GDT688_V61_WORKSHOP_READER.md",
        "LEGACY_ACTION_LEAKAGE_COMPARISON.tsv",
        "V60_BEFORE_116_VERB_PROVENANCE.tsv",
        "V61_10_RERENDERED_LINES.tsv",
        "V61_113_VERB_OCCURRENCE_PROVENANCE.tsv",
        "V61_51_LINE_READER.tsv",
        "V61_51_LINE_VERB_AUDIT.tsv",
        "V61_85_ACTION_POSITION_ARITY.tsv",
    }
    result = json.loads((ART / "RESULT.json").read_text(encoding="utf-8"))
    audit.check(set(result["files"]) == generated, "exact generated inventory")
    for name in [*sorted(generated), "RESULT.json"]:
        audit.check((ART / name).is_file(), f"missing artifact {name}")

    builder = load_builder()
    with tempfile.TemporaryDirectory(prefix="gdt688-rebuild-") as raw_temp:
        rebuilt = Path(raw_temp)
        rebuilt_result = builder.build(rebuilt)
        audit.check(rebuilt_result["status"] == result["status"], "rebuilt status")
        for name in [*sorted(generated), "RESULT.json"]:
            audit.check((ART / name).read_bytes() == (rebuilt / name).read_bytes(), f"byte rebuild {name}")

    rules = read_tsv(RULE_PATH)
    compiled = [(row["canonical_lemma"], re.compile(row["regex"], re.IGNORECASE)) for row in rules]
    audit.check(len(rules) == len({row["canonical_lemma"] for row in rules}) == 32, "32 unique canonical rules")
    audit.check(Counter(row["legacy_relation"] for row in rules) == {
        "UNCHANGED": 26,
        "NARROWED_NO_KUEHLEN_OVERLAP": 1,
        "EXPANDED_SETZE_AN": 1,
        "EXPANDED_SCHLIESSEN": 1,
        "NEW_MISSING_FORM": 1,
        "NARROWED_STELLE_CONTEXT": 1,
        "NARROWED_NO_KUEHLE_COLLISION": 1,
    }, "rule-change inventory")

    v60 = read_tsv(V60_PATH)
    v61 = read_tsv(ART / "V61_51_LINE_READER.tsv")
    changed = read_tsv(ART / "V61_10_RERENDERED_LINES.tsv")
    before = read_tsv(ART / "V60_BEFORE_116_VERB_PROVENANCE.tsv")
    provenance = read_tsv(ART / "V61_113_VERB_OCCURRENCE_PROVENANCE.tsv")
    arity = read_tsv(ART / "V61_85_ACTION_POSITION_ARITY.tsv")
    lines = read_tsv(ART / "V61_51_LINE_VERB_AUDIT.tsv")
    comparison = read_tsv(ART / "LEGACY_ACTION_LEAKAGE_COMPARISON.tsv")
    counterexamples = read_tsv(ART / "COUNTEREXAMPLE_AUDIT.tsv")

    audit.check(len(v60) == len(v61) == len(lines) == 51, "51-line populations")
    audit.check(sum(int(row["token_count"]) for row in v61) == 479, "479 positions preserved")
    audit.check(sum(int(row["action_positions"]) for row in v61) == 85, "85 action positions preserved")
    audit.check(sum(int(row["v61_renderer_revision"]) for row in v61) == 10, "ten renderer revisions")
    audit.check(all(row["v61_provenance_status"] == "ALL_PRACTICAL_VERBS_EXACT_ACTION_ORDINAL" for row in v61), "all lines provenance clean")
    audit.check(Counter(row["v61_reader_mode"] for row in v61) == {
        "ARBEITSGANG": 16,
        "HYBRID_ARBEIT_UND_ZUSTAND": 23,
        "ZUSTANDSLISTE": 6,
        "MENGEN_UND_ZUSTANDSLISTE": 6,
    }, "reader-mode partition")
    audit.check(sum(int(row["v61_verb_occurrences"]) for row in v61) == 113, "113 reader verbs")

    changed_keys: set[str] = set()
    for old, new in zip(v60, v61):
        audit.check(old["locus"] == new["locus"] and old["zl3b_line"] == new["zl3b_line"], "source line identity")
        audit.check(old["literal_token_glosses_de"] == new["literal_token_glosses_de"], f"literal meanings preserved {old['locus']}")
        audit.check(old["action_ordinals"] == new["action_ordinals"] and old["action_surfaces"] == new["action_surfaces"], f"actions preserved {old['locus']}")
        audit.check(new["v60_practical_translation_de"] == old["practical_translation_de"], f"V60 prose retained {old['locus']}")
        expected = render(new["literal_token_glosses_de"].split(" | "))
        audit.check(new["practical_translation_de"] == expected, f"strict source-order render {old['locus']}")
        if old["practical_translation_de"] != new["practical_translation_de"]:
            changed_keys.add(old["locus"])
    audit.check(changed_keys == {
        "f107r.40", "f112r.36", "f113v.3", "f114r.24", "f114v.36",
        "f75r.3", "f80r.17", "f80v.27", "f85r2.5", "f86v6.5",
    }, "exact ten rerendered lines")
    audit.check({row["locus"] for row in changed} == changed_keys, "changed-line artifact exact")
    audit.check(Counter(row["revision_reason"] for row in changed) == {
        "NORMALIZE_RENDERER_SPAN_PROVENANCE": 8,
        "REMOVE_ZERO_SOURCE_VERBS": 2,
    }, "eight normalization and two leak repairs")
    audit.check({row["locus"] for row in changed if row["revision_reason"] == "REMOVE_ZERO_SOURCE_VERBS"} == {"f114v.36", "f75r.3"}, "two leak loci")

    audit.check(len(before) == 116, "116 V60 practical verb occurrences")
    audit.check(Counter(row["provenance_status"] for row in before) == {
        "EXACT_RENDERER_SPAN_TO_ACTION_ORDINAL": 95,
        "ONE_LEXICAL_CANDIDATE_NO_STORED_SPAN": 7,
        "MULTIPLE_LEXICAL_CANDIDATES_NO_STORED_SPAN": 10,
        "ZERO_ACTION_ORDINAL_CANDIDATE": 4,
    }, "V60 before provenance partition")
    audit.check({(row["locus"], row["canonical_lemma"]) for row in before if row["provenance_status"] == "ZERO_ACTION_ORDINAL_CANDIDATE"} == {
        ("f114v.36", "verbinden"), ("f114v.36", "abschließen"),
        ("f75r.3", "trocknen"), ("f75r.3", "bringen"),
    }, "four exact zero-source verbs")

    audit.check(len(provenance) == 113, "113 V61 provenance rows")
    audit.check(all(row["provenance_status"] == "EXACT_RENDERER_SPAN_TO_ACTION_ORDINAL" and row["action_licensed"] == "1" for row in provenance), "all V61 verb rows exact")
    reader_by_locus = {row["locus"]: row for row in v61}
    for row in provenance:
        line = reader_by_locus[row["locus"]]
        start, end = int(row["char_start"]), int(row["char_end"])
        audit.check(line["practical_translation_de"][start:end] == row["matched_text"], f"character span {row['locus']}#{row['occurrence_index']}")
        ordinal = int(row["source_ordinal"])
        audit.check(ordinal in int_set(line["action_ordinals"]), f"licensed ordinal {row['locus']}#{row['occurrence_index']}")
        audit.check(line["zl3b_line"].split()[ordinal - 1] == row["source_surface"], f"surface backprojection {row['locus']}#{row['occurrence_index']}")
        audit.check(line["literal_token_glosses_de"].split(" | ")[ordinal - 1] == row["source_literal_gloss_de"], f"gloss backprojection {row['locus']}#{row['occurrence_index']}")
        matches = [match for lemma, pattern in compiled if lemma == row["canonical_lemma"] for match in pattern.finditer(row["source_literal_gloss_de"])]
        audit.check(bool(matches), f"lemma exists in source gloss {row['locus']}#{row['occurrence_index']}")

    audit.check(len(arity) == 85 and len({(row["locus"], row["ordinal"]) for row in arity}) == 85, "85 unique action arity rows")
    audit.check(Counter(int(row["verb_occurrences"]) for row in arity) == {1: 65, 2: 12, 3: 8}, "action arity 65/12/8")
    audit.check(sum(int(row["verb_occurrences"]) for row in arity) == 113, "arity sums to 113")
    audit.check(all(row["provenance_status"] == "ALL_VERBS_FROM_THIS_EXACT_ACTION_ORDINAL" for row in arity), "arity provenance exact")

    audit.check(len(lines) == 51 and sum(int(row["v61_zero_candidate_verbs"]) if "v61_zero_candidate_verbs" in row else 0 for row in lines) == 0, "line audit complete")
    audit.check(sum(int(row["v60_zero_candidate_verbs"]) for row in lines) == 4, "line audit carries four old zero-source verbs")
    audit.check(all(row["v61_extra_lemmas"] == "NONE" and row["v61_status"] == "ALL_VERBS_EXACT_ACTION_ORDINAL" for row in lines), "zero V61 extra lemmas")
    audit.check([row["phase"] for row in comparison] == ["GDT684_V57", "GDT686_V59", "GDT687_V60", "GDT688_V61"], "comparison phase order")
    audit.check([(int(row["extra_legacy_lemma_line_pairs"]), int(row["lines_with_extra"])) for row in comparison] == [(74, 29), (66, 28), (4, 2), (0, 0)], "leakage 74 to 66 to 4 to zero")
    audit.check([int(row["source_action_positions"]) for row in comparison] == [86, 86, 85, 85], "action totals by phase")
    audit.check(len(counterexamples) == 6, "six counterexample classes")

    f114 = reader_by_locus["f114v.36"]["practical_translation_de"].lower()
    f75 = reader_by_locus["f75r.3"]["practical_translation_de"].lower()
    audit.check(f114.count("nehmen") + f114.count("nimm") == 2, "f114v preserves both take verbs")
    audit.check("verbinden" not in f114 and "abschließen" not in f114, "f114v removes two free verbs")
    audit.check("trocknen" not in f75 and "bringen" not in f75, "f75r removes two free verbs")

    audit.check(result["status"] == "PASS_V61_113_OF_113_PRACTICAL_VERBS_EXACT_ACTION_ORDINAL__LEGACY_LEAKAGE_74_TO_66_TO_4_TO_0", "result status")
    audit.check(result["basis"] == {
        "action_bearing_lines": 39,
        "f84_access": 0,
        "f84r_access": 0,
        "lines": 51,
        "new_pages": 0,
        "non_action_lines": 12,
        "positions": 479,
        "source_action_positions": 85,
        "v60_practical_verb_occurrences": 116,
        "v61_practical_verb_occurrences": 113,
    }, "result basis exact")
    audit.check(result["v60_before"] == {
        "exact_span_to_action_ordinal": 95,
        "legacy_extra_lemma_line_pairs": 4,
        "lines_with_legacy_extra": 2,
        "multiple_lexical_candidates_without_span": 10,
        "one_lexical_candidate_without_span": 7,
        "zero_action_ordinal_candidate": 4,
    }, "result V60 exact")
    audit.check(result["v61"] == {
        "action_position_verb_arity": {"one": 65, "three": 8, "two": 12},
        "action_positions_with_at_least_one_verb": 85,
        "exact_span_to_action_ordinal": 113,
        "four_layer_union": 330,
        "legacy_extra_lemma_line_pairs": 0,
        "lines_with_legacy_extra": 0,
        "mechanical_debt_union": 152,
        "reader_modes": {"hybrid": 23, "quantity_state_list": 6, "state_list": 6, "work": 16},
        "renderer_revised_lines": 10,
        "semantic_card_revisions": 0,
        "strict_debt_positions": 106,
        "unmapped_verbs": 0,
    }, "result V61 exact")
    audit.check("66 was V59" in result["correction"], "stale scope explicitly corrected")
    audit.check("does not prove" in result["claim_ceiling"], "claim ceiling retained")
    audit.check(not any(row["page"].lower().startswith("f84") for row in v61), "sealed pages absent")
    for name, digest in result["files"].items():
        audit.check(sha256(ART / name) == digest, f"hash bound {name}")

    validation = {
        "status": "PASS",
        "checks": audit.checks,
        "byte_rebuilds": len(generated) + 1,
        "lines": 51,
        "positions": 479,
        "action_positions": 85,
        "v60_practical_verbs": 116,
        "v61_practical_verbs": 113,
        "v61_exact_verb_provenance": 113,
        "v61_unmapped_verbs": 0,
        "renderer_revised_lines": 10,
        "legacy_extra_pairs_sequence": [74, 66, 4, 0],
        "sealed_pages_absent": True,
    }
    (ART / "VALIDATION.json").write_text(json.dumps(validation, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(validation, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
