#!/usr/bin/env python3
"""Independent validation for GDT695."""

from __future__ import annotations

import csv
import hashlib
import importlib.util
import json
import re
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
EXP = ROOT / "experiments/yolo/gdt695_fixed_v67_clause_realization"
ART = EXP / "artifacts"
RUN = EXP / "src/run.py"
G694 = ROOT / "experiments/yolo/gdt694_residual_fraction_share_migration/artifacts"
G689 = ROOT / "experiments/yolo/gdt689_v62_bound_dy_sister_endpoint_dispatch/artifacts"
RULES = ROOT / "experiments/yolo/gdt688_v61_exact_verb_ordinal_provenance_renderer/src/V61_VERB_RULES.tsv"
POLICY = EXP / "src/V68_CLAUSE_REALIZATION_POLICY.tsv"
STATUS = "PASS_V68_83_ACTION_CLAUSES__92_NOMINAL_BLOCKS__175_TOTAL__115_VERBS__ZERO_WORD_DELTA"
WORD_RE = re.compile(r"[A-Za-zÄÖÜäöüß]+(?:-[A-Za-zÄÖÜäöüß]+)*")


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def words(text: str) -> list[str]:
    return [word.casefold() for word in WORD_RE.findall(text)]


def load_builder():
    spec = importlib.util.spec_from_file_location("gdt695_builder", RUN)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class Audit:
    def __init__(self) -> None:
        self.checks: list[dict[str, object]] = []

    def check(self, condition: bool, name: str) -> None:
        self.checks.append({"check": name, "pass": int(bool(condition))})
        if not condition:
            raise AssertionError(name)


def main() -> int:
    audit = Audit()
    result = json.loads((ART / "RESULT.json").read_text(encoding="utf-8"))
    generated = sorted(result["files"])
    for name in generated:
        audit.check((ART / name).is_file(), f"artifact exists {name}")
        audit.check(sha256(ART / name) == result["files"][name], f"artifact hash {name}")
    for relative, digest in result["inputs"].items():
        path = ROOT / relative
        audit.check(path.is_file() and sha256(path) == digest, f"input hash {relative}")

    builder = load_builder()
    with tempfile.TemporaryDirectory(prefix="gdt695-rebuild-") as raw_temp:
        rebuilt = Path(raw_temp)
        rebuilt_result = builder.build(rebuilt)
        builder.write_json(rebuilt / "RESULT.json", rebuilt_result)
        audit.check(rebuilt_result["status"] == result["status"], "rebuilt status")
        for name in [*generated, "RESULT.json"]:
            audit.check((ART / name).read_bytes() == (rebuilt / name).read_bytes(), f"byte rebuild {name}")

    source_tokens = read_tsv(G694 / "V67_479_TOKEN_ZERO_FRACTION_READER.tsv")
    source_lines = read_tsv(G694 / "V67_51_LINE_ZERO_FRACTION_READER.tsv")
    source_spans = read_tsv(G694 / "V67_3_BOUND_SPANS.tsv")
    v62_lines = read_tsv(G689 / "V62_51_LINE_READER.tsv")
    v62_verbs = read_tsv(G689 / "V62_VERB_OCCURRENCE_PROVENANCE.tsv")
    token_freeze = read_tsv(ART / "V68_479_TOKEN_FREEZE.tsv")
    clauses = read_tsv(ART / "V68_175_CLAUSE_REALIZATIONS.tsv")
    lines = read_tsv(ART / "V68_51_LINE_CLAUSE_READER.tsv")
    actions = read_tsv(ART / "V68_83_ACTION_VERB_MULTISET_AUDIT.tsv")
    verbs = read_tsv(ART / "V68_115_VERB_OCCURRENCE_PROVENANCE.tsv")
    spans = read_tsv(ART / "V68_3_BOUND_SPAN_FREEZE.tsv")
    word_audit = read_tsv(ART / "V68_51_LINE_WORD_SEQUENCE_AUDIT.tsv")
    modes = read_tsv(ART / "V68_MODE_CENSUS.tsv")
    correction = read_tsv(ART / "V61_V62_V67_VERB_BASELINE_CORRECTION.tsv")
    policy = read_tsv(POLICY)

    audit.check(len(source_tokens) == len(token_freeze) == 479, "479 token rows")
    audit.check(len(source_lines) == len(lines) == len(word_audit) == 51, "51 line rows")
    audit.check(len(source_spans) == len(spans) == 3, "three span rows")
    audit.check(len(clauses) == 175, "175 clauses")
    audit.check(Counter(row["clause_type"] for row in clauses) == {"ACTION_CLAUSE": 83, "NOMINAL_BLOCK": 92}, "83 action and 92 nominal clauses")
    audit.check(len(actions) == 83 and len(verbs) == len(v62_verbs) == 115, "83 action audits and 115 verb rows")
    audit.check([tuple(row.values()) for row in policy] == [
        ("P001", "BOUND_SPAN", "GDT694 exact span start", "Keep the complete V67 span text as one indivisible nominal unit.", "1"),
        ("P002", "EXPLICIT_PUNCTUATION_TOKEN", "V67 gloss is semicolon or full stop", "Attach the zero-word marker to the preceding semantic unit; never emit an empty clause.", "2"),
        ("P003", "ACTION_CARD", "Ordinal occurs in GDT689 v62_action_ordinals", "Emit the complete written card as one action clause even when it contains several licensed verbs.", "3"),
        ("P004", "RIGHT_BOUND_INTRODUCER", "One of four exact registered connector positions", "Join the connector by colon to its immediately following nominal or action target.", "4"),
        ("P005", "NOMINAL_BINDING", "Adjacent head and value carry GDT676 decision BIND or BIND_NOMINAL", "Keep both inside one nominal block and place a colon between them.", "5"),
        ("P006", "NOMINAL_RUN", "Maximal consecutive non-action units", "Emit one semicolon-delimited nominal block.", "6"),
        ("P007", "LINE_JOIN", "Between action clauses and nominal blocks", "Place a full stop; never add a connective, object, pronoun or verb.", "7"),
    ], "seven-row policy contract exact")

    audit.check(
        all(
            (source["locus"], source["token_ordinal"], source["surface"], source["v67_token_gloss_de"])
            == (frozen["locus"], frozen["token_ordinal"], frozen["surface"], frozen["v68_token_gloss_de"])
            for source, frozen in zip(source_tokens, token_freeze)
        ),
        "all 479 token identities frozen",
    )
    audit.check(all(row["byte_identical"] == "1" for row in token_freeze), "all token byte flags")
    audit.check(all(
        source["v67_selected_gloss_de"] == frozen["v68_selected_gloss_de"]
        and frozen["v68_byte_identical"] == "1"
        for source, frozen in zip(source_spans, spans)
    ), "all three spans frozen")

    source_line_by_locus = {row["locus"]: row for row in source_lines}
    audit.check(all(
        words(source_line_by_locus[row["locus"]]["v67_translation_de"])
        == words(row["v68_clause_translation_de"])
        for row in lines
    ), "all 51 line word sequences exact")
    audit.check(all(row["v68_content_word_sequence_exact"] == "1" for row in lines), "all line word flags")
    audit.check(all(row["word_sequence_exact"] == "1" for row in word_audit), "all word audits exact")
    audit.check(sum(int(row["content_word_additions"]) + int(row["content_word_deletions"]) + int(row["content_word_reorders"]) for row in word_audit) == 0, "zero content word delta")

    action_keys: set[tuple[str, int]] = set()
    for line in v62_lines:
        ordinals = [] if line["v62_action_ordinals"] == "NONE" else [int(value) for value in line["v62_action_ordinals"].split("|")]
        for ordinal in ordinals:
            action_keys.add((line["locus"], ordinal))
    audit.check(len(action_keys) == 83, "GDT689 supplies 83 live action keys")
    audit.check({(row["locus"], int(row["token_ordinal"])) for row in actions} == action_keys, "action audit keys exact")

    # Reconstruct clause coverage directly from the published table rather than
    # trusting the builder's in-memory position map.
    token_counts = Counter(row["locus"] for row in source_tokens)
    clauses_by_locus: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in clauses:
        clauses_by_locus[row["locus"]].append(row)
    coverage_exact = set(clauses_by_locus) == set(token_counts)
    maximal_nominal = True
    clause_action_contract = True
    clause_action_keys: set[tuple[str, int]] = set()
    for locus, locus_clauses in clauses_by_locus.items():
        locus_clauses.sort(key=lambda row: int(row["clause_id"]))
        expected_start = 1
        previous_type = "NONE"
        for expected_id, row in enumerate(locus_clauses, start=1):
            start, end = int(row["start_ordinal"]), int(row["end_ordinal"])
            coverage_exact = coverage_exact and int(row["clause_id"]) == expected_id
            coverage_exact = coverage_exact and start == expected_start and end >= start
            coverage_exact = coverage_exact and int(row["token_positions"]) == end - start + 1
            ordinals = [] if row["action_ordinals"] == "NONE" else [int(value) for value in row["action_ordinals"].split("|")]
            observed_in_range = {
                (locus, ordinal) for ordinal in range(start, end + 1)
                if (locus, ordinal) in action_keys
            }
            if row["clause_type"] == "ACTION_CLAUSE":
                clause_action_contract = clause_action_contract and len(ordinals) == 1
                clause_action_contract = clause_action_contract and observed_in_range == {(locus, ordinals[0])}
                clause_action_keys.update(observed_in_range)
            else:
                clause_action_contract = clause_action_contract and row["clause_type"] == "NOMINAL_BLOCK"
                clause_action_contract = clause_action_contract and not ordinals and not observed_in_range
                maximal_nominal = maximal_nominal and previous_type != "NOMINAL_BLOCK"
            previous_type = row["clause_type"]
            expected_start = end + 1
        coverage_exact = coverage_exact and expected_start == token_counts[locus] + 1
    audit.check(coverage_exact, "independent clause ranges cover every line exactly once")
    audit.check(clause_action_contract and clause_action_keys == action_keys, "independent one-action-per-action-clause contract")
    audit.check(maximal_nominal, "independent nominal blocks are maximal")
    audit.check(all(row["verb_multiset_exact"] == row["verb_sequence_exact"] == "1" for row in actions), "all action verb sequences exact")
    audit.check(sum(int(row["v67_observed_verb_occurrences"]) for row in actions) == 115, "115 action verb occurrences")
    audit.check(all(row["action_licensed"] == "1" and row["provenance_status"] == "EXACT_V67_TOKEN_SPAN_TO_GDT689_ACTION_ORDINAL" for row in verbs), "all verb spans licensed")

    # Independently scan all 479 V67 token glosses with the frozen GDT688 scanner,
    # but compare the result to GDT689/V62 rather than the superseded V61 counts.
    rule_rows = read_tsv(RULES)
    compiled = [(row["canonical_lemma"], re.compile(row["regex"], re.IGNORECASE)) for row in rule_rows]
    expected: dict[tuple[str, int], list[str]] = defaultdict(list)
    for row in v62_verbs:
        expected[(row["locus"], int(row["source_ordinal"]))].append(row["canonical_lemma"])
    total = 0
    observed_keys: set[tuple[str, int]] = set()
    exact_sequences = True
    for token in source_tokens:
        key = token["locus"], int(token["token_ordinal"])
        found = [
            (match.start(), match.end(), lemma)
            for lemma, pattern in compiled for match in pattern.finditer(token["v67_token_gloss_de"])
        ]
        found.sort()
        actual = [lemma for _, _, lemma in found]
        total += len(actual)
        if actual:
            observed_keys.add(key)
        exact_sequences = exact_sequences and actual == expected.get(key, [])
    audit.check(exact_sequences, "all 479 independent verb sequences exact")
    audit.check(total == 115 and observed_keys == action_keys, "independent 115 verbs only on 83 action keys")

    audit.check(Counter((row["line_mode"], int(row["action_clauses"]), int(row["nominal_blocks"])) for row in modes) == Counter({
        ("ACTION_SEQUENCE", 49, 38): 1,
        ("MIXED_RECORD", 34, 42): 1,
        ("NOMINAL_REGISTER", 0, 6): 1,
        ("QUANTITY_LABEL", 0, 6): 1,
    }), "mode clause census")
    audit.check(sum(
        len(row["binding_ids"].split("|")) for row in clauses if row["binding_ids"] != "NONE"
    ) == 10, "ten inherited binding edges")
    audit.check(sorted(
        intro_id for row in clauses if row["right_bound_intro_ids"] != "NONE"
        for intro_id in row["right_bound_intro_ids"].split("|")
    ) == ["I001", "I002", "I003", "I004"], "four exact right-bound introducers")
    audit.check([row["baseline"] for row in correction] == ["GDT688_V61", "GDT689_V62", "GDT694_V67"], "baseline correction order")
    audit.check(correction[0]["live_for_v67"] == "0" and correction[1]["live_for_v67"] == correction[2]["live_for_v67"] == "1", "V62 baseline authority")
    audit.check(result["status"] == STATUS, "result status")
    audit.check(result["freeze"] == {
        "bound_spans_byte_identical": 3,
        "content_word_additions": 0,
        "content_word_deletions": 0,
        "content_word_reorders": 0,
        "lines_with_exact_content_word_sequence": 51,
        "new_object_carries": 0,
        "token_glosses_byte_identical": 479,
    }, "freeze result exact")
    audit.check(result["verbs"]["expected_occurrences"] == result["verbs"]["observed_occurrences"] == 115, "result verb counts")
    audit.check(result["verbs"]["missing_occurrences"] == result["verbs"]["extra_occurrences"] == result["verbs"]["non_action_position_occurrences"] == 0, "result zero verb errors")
    audit.check(result["basis"]["new_pages"] == result["basis"]["f84_access"] == result["basis"]["f84r_access"] == 0, "sealed and page gates")

    payload = {
        "status": "PASS",
        "checks": len(audit.checks),
        "failed": sum(1 - int(row["pass"]) for row in audit.checks),
        "summary": {
            "tokens": 479, "lines": 51, "clauses": 175,
            "action_clauses": 83, "nominal_blocks": 92,
            "active_verbs": 115, "bound_spans": 3,
            "content_word_delta": 0, "new_pages": 0,
        },
        "audit": audit.checks,
    }
    (ART / "VALIDATION.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
