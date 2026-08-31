#!/usr/bin/env python3
"""Independent validator for GDT690/V63."""

from __future__ import annotations

import csv
import hashlib
import json
import os
import re
import subprocess
import sys
import tempfile
from collections import Counter, defaultdict
from pathlib import Path

sys.dont_write_bytecode = True


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
BASE = ROOT / "experiments/yolo/gdt690_noun_ordinal_provenance_main_apparatus"
ART = BASE / "artifacts"
SRC = BASE / "src"
RUN = SRC / "run.py"
V62 = ROOT / "experiments/yolo/gdt689_v62_bound_dy_sister_endpoint_dispatch/artifacts/V62_51_LINE_READER.tsv"
RULES = SRC / "V63_NOUN_RENDER_RULES.tsv"
LEXICON = SRC / "V63_NOUN_LEXICON.tsv"
NON_NOUN = SRC / "V63_NON_NOUN_ALLOWLIST.tsv"
HISTORICAL = SRC / "HISTORICAL_NOUN_RIVALS.tsv"
WORD_RE = re.compile(r"[A-Za-zÄÖÜäöüß]+(?:-[A-Za-zÄÖÜäöüß]+)*")
HEAD_RE = re.compile(r"^(p|s|r|l).+")
SOURCE_SPECS = [
    ("GDT635", ROOT / "experiments/yolo/gdt635_initial_head_same_remainder_swaps/artifacts/WORKING_DICTIONARY_V12.tsv", "entry", "working_meaning_de"),
    ("GDT636", ROOT / "experiments/yolo/gdt636_residual_four_head_semantics/artifacts/WORKING_DICTIONARY_V13.tsv", "entry", "working_meaning_de"),
    ("GDT635", ROOT / "experiments/yolo/gdt635_initial_head_same_remainder_swaps/artifacts/CONCRETE_FOUR_HEAD_PARADIGMS.tsv", "form", "working_default_de"),
    ("GDT636", ROOT / "experiments/yolo/gdt636_residual_four_head_semantics/artifacts/RESIDUAL_76_FORM_GRID.tsv", "form", "working_default_de"),
    ("GDT685", ROOT / "experiments/yolo/gdt685_v58_ch_sh_t_ol_ansatz_dispatch/artifacts/SURFACE_STATE_DISPATCH_SUMMARY.tsv", "surface", "default_de"),
]
FOCUS = {
    "GUMMI": {"shx"},
    "BLUETE": {"fchoky", "fdar", "shor", "shoral", "ofchedy", "dshor"},
    "WURZEL": {"r", "rr", "raiin", "ram"},
    "CTH_MATERIAL": {"checthy"},
    "RAHMEN": {"qotain", "otain", "otaiin", "okain", "okaiin"},
    "HOLZBINDUNG": {"olkar", "olam"},
}


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def render(glosses: list[str]) -> tuple[str, list[tuple[int, int, str]]]:
    text = ""
    segments: list[list[object]] = []
    for gloss in glosses:
        if gloss in {";", "."}:
            stripped = text.rstrip(" ,;.")
            for segment in segments:
                if int(segment[1]) > len(stripped):
                    segment[1] = len(stripped)
            text = stripped
            start = len(text)
            text += gloss
            segments.append([start, len(text), gloss])
            continue
        text += "" if not text else (" " if text.endswith((";", ".", ":")) else "; ")
        start = len(text)
        text += gloss
        segments.append([start, len(text), gloss])
    if text and not text.endswith("."):
        text += "."
    if text:
        text = text[:1].upper() + text[1:]
    return text, [(int(a), int(b), str(c)) for a, b, c in segments]


def head(surface: str) -> str:
    return "NONE" if surface.startswith("sh") or not HEAD_RE.match(surface) else surface[0]


def source_index() -> dict[str, list[str]]:
    index: dict[str, list[str]] = defaultdict(list)
    for _experiment, path, key_field, gloss_field in SOURCE_SPECS:
        for row in read_tsv(path):
            key = row[key_field]
            if key and not any(mark in key for mark in "/+()"):
                index[key].append(row[gloss_field])
    return index


def source_match(surface: str, gloss: str, index: dict[str, list[str]]) -> str:
    records = index.get(surface, [])
    if gloss in records:
        return "EXACT_GLOSS"
    if records:
        return "EXACT_SURFACE_ONLY"
    if head(surface) != "NONE":
        return "HEAD_ONLY"
    return "NONE"


def main() -> int:
    checks: list[str] = []
    result = json.loads((ART / "RESULT.json").read_text(encoding="utf-8"))
    assert result["status"] == "PASS_V63_ALL_MAIN_NOUNS_EXACT_ORDINAL__ONE_MAIN_HEAD_PLUS_RIVAL_APPARATUS"
    checks.append("result_status")

    for relative, digest in result["inputs"].items():
        path = ROOT / relative
        assert path.is_file() and sha256(path) == digest, relative
    checks.append("all_input_hashes")
    for name, digest in result["files"].items():
        assert (ART / name).is_file() and sha256(ART / name) == digest, name
    checks.append("all_output_hashes")

    v62_rows = read_tsv(V62)
    token_rows = read_tsv(ART / "V63_479_TOKEN_NOUN_BINDING.tsv")
    line_rows = read_tsv(ART / "V63_51_LINE_MAIN_AND_APPARATUS.tsv")
    noun_rows = read_tsv(ART / "V63_MAIN_NOUN_OCCURRENCE_PROVENANCE.tsv")
    source_noun_rows = read_tsv(ART / "V62_SOURCE_NOUN_OCCURRENCE_AUDIT.tsv")
    rules = read_tsv(RULES)
    rule_by_surface = {row["surface"]: row for row in rules}
    line_by_locus = {row["locus"]: row for row in line_rows}
    token_by_key = {(row["locus"], int(row["token_ordinal"])): row for row in token_rows}
    assert len(v62_rows) == len(line_rows) == 51 and len(token_rows) == len(token_by_key) == 479
    assert len(rule_by_surface) == len(rules) == 72
    checks.extend(["population_51_479", "rule_deck_72_unique"])

    noun_by_form: dict[str, dict[str, str]] = {}
    for row in read_tsv(LEXICON):
        for form in row["normalized_forms"].split("|"):
            assert form not in noun_by_form
            noun_by_form[form] = row
    non_noun: set[str] = set()
    for row in read_tsv(NON_NOUN):
        for form in row["normalized_forms"].split("|"):
            assert form not in non_noun
            non_noun.add(form)
    assert not (set(noun_by_form) & non_noun)
    checks.append("word_classes_disjoint")

    expected_main_nouns: set[tuple[object, ...]] = set()
    expected_source_nouns: set[tuple[object, ...]] = set()
    used_rules: Counter[str] = Counter()
    source_matches: Counter[str] = Counter()
    head_counts: Counter[str] = Counter()
    focus_counts: Counter[str] = Counter()
    index = source_index()
    word_types_seen: set[str] = set()

    for source_line in v62_rows:
        assert not source_line["page"].startswith("f84") and not source_line["locus"].startswith("f84")
        tokens = source_line["zl3b_line"].split()
        before = source_line["v62_literal_token_glosses_de"].split(" | ")
        assert len(tokens) == len(before) == int(source_line["token_count"])
        after: list[str] = []
        for ordinal, (surface, gloss) in enumerate(zip(tokens, before), 1):
            rule = rule_by_surface.get(surface)
            if rule:
                assert rule["expected_v62_gloss_de"] == gloss
                new_gloss = rule["main_gloss_de"]
                used_rules[rule["rule_id"]] += 1
            else:
                new_gloss = gloss
            after.append(new_gloss)
            output = token_by_key[(source_line["locus"], ordinal)]
            assert output["surface"] == surface and output["v62_token_gloss_de"] == gloss
            assert output["v63_main_token_gloss_de"] == new_gloss
            match = source_match(surface, gloss, index)
            assert output["upstream_source_match"] == match
            source_matches[match] += 1
            if head(surface) != "NONE":
                assert output["productive_initial_head"] == head(surface)
                head_counts[head(surface)] += 1
            families = [name for name, values in FOCUS.items() if surface in values]
            assert len(families) <= 1
            if families:
                assert output["focus_family"] == families[0]
                focus_counts[families[0]] += 1
            else:
                assert output["focus_family"] == "NONE"

        before_text, before_segments = render(before)
        after_text, after_segments = render(after)
        line_output = line_by_locus[source_line["locus"]]
        assert line_output["zl3b_line"] == source_line["zl3b_line"]
        assert line_output["v62_practical_translation_de"] == before_text
        assert line_output["v63_main_translation_de"] == after_text
        for ordinal, (surface, old_gloss, new_gloss) in enumerate(zip(tokens, before, after), 1):
            for phase, gloss, text, segment, target in (
                ("V62_SOURCE", old_gloss, before_text, before_segments[ordinal - 1], expected_source_nouns),
                ("V63_MAIN", new_gloss, after_text, after_segments[ordinal - 1], expected_main_nouns),
            ):
                start, _end, _ = segment
                for word in WORD_RE.finditer(gloss):
                    normalized = word.group(0).casefold()
                    word_types_seen.add(normalized)
                    assert normalized in noun_by_form or normalized in non_noun, (phase, normalized)
                    if normalized not in noun_by_form:
                        continue
                    line_start, line_end = start + word.start(), start + word.end()
                    actual = text[line_start:line_end]
                    assert actual.casefold() == word.group(0).casefold()
                    lex = noun_by_form[normalized]
                    target.add((source_line["locus"], ordinal, line_start, line_end, actual.casefold(), normalized,
                                lex["canonical_noun_de"], lex["noun_class"], lex["content_status"]))

    assert set(used_rules) == {row["rule_id"] for row in rules}
    assert sum(used_rules.values()) == 104
    assert source_matches == {"EXACT_GLOSS": 49, "EXACT_SURFACE_ONLY": 45, "HEAD_ONLY": 25, "NONE": 360}
    assert head_counts == {"l": 19, "s": 9, "p": 5, "r": 3}
    assert focus_counts == {"HOLZBINDUNG": 20, "RAHMEN": 12, "BLUETE": 8, "WURZEL": 4, "GUMMI": 1, "CTH_MATERIAL": 1}
    checks.extend(["all_rules_used_104_positions", "source_join_49_45_25_360", "productive_heads_36", "focus_counts_46"])

    actual_main_nouns = {
        (row["locus"], int(row["token_ordinal"]), int(row["line_char_start"]), int(row["line_char_end"]),
         row["noun_surface_de"].casefold(), row["normalized_form"], row["canonical_noun_de"],
         row["noun_class"], row["content_status"])
        for row in noun_rows
    }
    actual_source_nouns = {
        (row["locus"], int(row["token_ordinal"]), int(row["line_char_start"]), int(row["line_char_end"]),
         row["noun_surface_de"].casefold(), row["normalized_form"], row["canonical_noun_de"],
         row["noun_class"], row["content_status"])
        for row in source_noun_rows
    }
    assert len(actual_main_nouns) == len(noun_rows) == len(expected_main_nouns) == 725
    assert len(actual_source_nouns) == len(source_noun_rows) == len(expected_source_nouns) == 773
    assert actual_main_nouns == expected_main_nouns and actual_source_nouns == expected_source_nouns
    assert not any(row["content_status"] == "APPARATUS_ONLY" for row in noun_rows)
    assert sum(row["content_status"] == "APPARATUS_ONLY" for row in source_noun_rows) == 40
    checks.extend(["main_noun_exact_set_725", "source_noun_exact_set_773", "apparatus_meta_40_to_0"])

    assert len({(row["locus"], row["token_ordinal"]) for row in noun_rows}) == 459
    assert not any("/" in row["v63_main_token_gloss_de"] or " oder " in row["v63_main_token_gloss_de"] for row in token_rows)
    assert sum("/" in row["v62_token_gloss_de"] or " oder " in row["v62_token_gloss_de"] for row in token_rows) == 21
    assert sum(row["surface"] in {"chol", "shol", "tol"} for row in token_rows) == 8
    assert not any(row["surface"] in {"chol", "shol", "tol"} for row in noun_rows)
    checks.extend(["noun_bearing_positions_459", "alternatives_21_to_0", "state_null_8_to_0_nouns"])

    assert read_tsv(ART / "HISTORICAL_NOUN_RIVALS.tsv") == read_tsv(HISTORICAL)
    assert len(read_tsv(HISTORICAL)) == 12
    checks.append("historical_rivals_exact_copy_12")

    with tempfile.TemporaryDirectory(prefix="gdt690-replay-") as temp_name:
        temp = Path(temp_name)
        env = dict(os.environ)
        env["GDT690_OUTPUT_DIR"] = str(temp)
        env["PYTHONDONTWRITEBYTECODE"] = "1"
        replay = subprocess.run([sys.executable, str(RUN)], cwd=ROOT, env=env, check=True, capture_output=True, text=True)
        assert replay.stdout.strip()
        for name in [*result["files"], "RESULT.json"]:
            assert (temp / name).read_bytes() == (ART / name).read_bytes(), name
    checks.append("exact_byte_replay")

    payload = {
        "status": "PASS",
        "checks": checks,
        "check_count": len(checks),
        "sealed_pages_absent": True,
        "lines": 51,
        "token_positions": 479,
        "main_noun_occurrences": 725,
        "noun_bearing_positions": 459,
        "changed_token_positions": 92,
        "source_match_counts": dict(source_matches),
        "focus_positions": dict(focus_counts),
        "byte_replay": True,
    }
    (ART / "VALIDATION.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(payload, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
