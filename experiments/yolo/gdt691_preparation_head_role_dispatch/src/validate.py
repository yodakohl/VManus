#!/usr/bin/env python3
"""Independent aggregate, provenance, and byte-replay validator for GDT691."""

from __future__ import annotations

import csv
import hashlib
import json
import os
import re
import subprocess
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
BASE = ROOT / "experiments/yolo/gdt691_preparation_head_role_dispatch"
ART = BASE / "artifacts"
SRC = BASE / "src"
RUN = SRC / "run.py"
SOURCE_NOUNS = ROOT / "experiments/yolo/gdt690_noun_ordinal_provenance_main_apparatus/artifacts/V63_MAIN_NOUN_OCCURRENCE_PROVENANCE.tsv"
QUANTITY_RE = re.compile(
    r"(?:Portion(?:en)?|Maß(?:portion)?|Handvoll|Charge|Teil|Dosen)"
    r"(?:\s+[A-Za-zÄÖÜäöüß-]+){0,2}\s*$",
    re.IGNORECASE,
)
SOURCE_RE = re.compile(r"(?:aus|aus dem|aus Holzrohstoff)\s*$", re.IGNORECASE)


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def independent_role(row: dict[str, str]) -> str:
    prefix = row["token_gloss_de"][:int(row["token_char_start"])].rstrip()
    if prefix.endswith("im"):
        return "LOCATIVE_CONTEXT"
    if (row["noun_surface_de"] != row["canonical_noun_de"] and row["noun_surface_de"].endswith("s")) or SOURCE_RE.search(prefix):
        return "GENITIVE_SOURCE"
    if QUANTITY_RE.search(prefix):
        return "QUANTITY_OBJECT"
    if row["canonical_noun_de"] in {"Ansatz", "Auszug", "Zubereitung"}:
        return "HEAD"
    return "COMPOUND_HEAD"


def main() -> int:
    checks: list[str] = []
    result = json.loads((ART / "RESULT.json").read_text(encoding="utf-8"))
    assert result["status"] == "PASS_V64_140_ROLE_DISPATCH__35_CONTEXT_RELATIONS_PRESERVED__54_EXACT_RULES_77_TOKEN_REVISIONS"
    checks.append("result_status")

    for relative, digest in result["inputs"].items():
        path = ROOT / relative
        assert path.is_file() and sha256(path) == digest, relative
    checks.append("all_input_hashes")
    for name, digest in result["files"].items():
        path = ART / name
        assert path.is_file() and sha256(path) == digest, name
    checks.append("all_output_hashes")

    source_prep = [row for row in read_tsv(SOURCE_NOUNS) if row["noun_class"] == "PREPARATION"]
    audit = read_tsv(ART / "V63_140_PREPARATION_ROLE_AUDIT.tsv")
    tokens = read_tsv(ART / "V64_479_TOKEN_READER.tsv")
    revisions = read_tsv(ART / "V64_77_TOKEN_REVISIONS.tsv")
    lines = read_tsv(ART / "V64_51_LINE_PRACTICAL_READER.tsv")
    spans = read_tsv(ART / "V64_PREPARATION_OUTPUT_SPANS.tsv")
    verbs = read_tsv(ART / "V64_113_VERB_PRESERVATION.tsv")
    comparisons = read_tsv(ART / "V63_V64_PREPARATION_TERM_COMPARISON.tsv")
    rules = read_tsv(SRC / "V64_EXACT_TOKEN_RULES.tsv")
    rule_uses = read_tsv(ART / "V64_RULE_USE_SUMMARY.tsv")
    historical = read_tsv(ART / "HISTORICAL_PREPARATION_CONTROL.tsv")

    assert len(source_prep) == len(audit) == 140
    assert len(tokens) == 479 and len(revisions) == 77 and len(lines) == 51
    assert len(spans) == 157 and len(verbs) == 113 and len(rules) == 54 and len(rule_uses) == 54
    assert len(historical) == 7
    checks.append("population_51_479_140_77_157_113")

    source_by_pk = {
        (row["locus"], row["token_ordinal"], row["token_char_start"], row["token_char_end"]): row
        for row in source_prep
    }
    audit_by_pk = {
        (row["locus"], row["token_ordinal"], row["token_char_start"], row["token_char_end"]): row
        for row in audit
    }
    assert len(source_by_pk) == len(audit_by_pk) == 140 and set(source_by_pk) == set(audit_by_pk)
    roles = Counter()
    for key, source in source_by_pk.items():
        expected = independent_role(source)
        assert audit_by_pk[key]["mention_role"] == expected
        roles[expected] += 1
    assert roles == {"HEAD": 49, "COMPOUND_HEAD": 34, "LOCATIVE_CONTEXT": 35, "GENITIVE_SOURCE": 15, "QUANTITY_OBJECT": 7}
    checks.append("independent_role_replay_49_34_35_15_7")

    routes = Counter(row["formal_route"] for row in audit)
    assert routes == {"LEARNED_WHOLE_OR_UNEXPORTED": 100, "PROVISIONAL_LOCAL_SCOPE": 30, "GDT652_EXACT_O_PREP_SURFACE": 7, "PRODUCTIVE_HEAD": 3}
    assert sum(row["v64_occurrence_action"] == "EXACT_CONTEXT_RELATION_REWRITE" for row in audit) == 32
    assert sum(row["v64_occurrence_action"] == "KEEP_EXPLICIT_CONTEXT_RELATION" for row in audit) == 3
    checks.append("route_partition_100_30_7_3__context_relation_32_plus_3")

    token_keys = {(row["locus"], int(row["token_ordinal"])) for row in tokens}
    revision_keys = {(row["locus"], int(row["token_ordinal"])) for row in revisions}
    assert len(token_keys) == 479 and len(revision_keys) == 77
    assert sum(int(row["v64_changed"]) for row in tokens) == 77
    assert sum(row["v64_rule_id"] == "P037" for row in revisions) == 1
    assert all(row["v63_token_gloss_de"] != row["v64_token_gloss_de"] for row in revisions)
    checks.append("revision_keys_77__all_exact_rules")

    exact_ids = {row["rule_id"] for row in rules}
    summarized = {row["rule_id"]: int(row["uses"]) for row in rule_uses}
    assert exact_ids == set(summarized)
    assert all(summarized[rule_id] >= 1 for rule_id in exact_ids)
    assert sum(summarized[rule_id] for rule_id in exact_ids) == 77
    checks.append("all_54_exact_rules_used_77")

    assert sum(int(row["v64_changed_token_positions"]) for row in lines) == 77
    assert sum(int(row["token_count"]) for row in lines) == 479
    assert sum(row["v64_practical_translation_de"].count(" im Ansatz") for row in lines) == 3
    assert not any(" im Trockenansatz" in row["v64_practical_translation_de"] for row in lines)
    assert all(not row["page"].startswith("f84") and not row["locus"].startswith("f84") for row in lines)
    checks.append("line_replay_51_479__35_context_relations_preserved__no_f84")

    line_by_locus = {row["locus"]: row for row in lines}
    for span in spans:
        line = line_by_locus[span["locus"]]["v64_practical_translation_de"]
        start, end = int(span["line_char_start"]), int(span["line_char_end"])
        assert line[start:end] == span["matched_term_de"]
        assert (span["locus"], int(span["token_ordinal"])) in token_keys
    assert not any(row["term_class"] == "BAD" for row in spans)
    checks.append("all_157_output_spans_exact_ordinal__bad_zero")

    assert all(row["preserved_exact_ordinal"] == "1" for row in verbs)
    assert all(row["gdt691_additional_verb_form_loss"] == "0" for row in verbs)
    assert sum(int(row["v63_exact_form_present"]) for row in verbs) == 110
    assert sum(int(row["v64_exact_form_present"]) for row in verbs) == 110
    checks.append("all_113_action_ordinals_preserved__exact_forms_110_to_110")

    observed_terms = {
        row["term_class"]: (int(row["v63_occurrences"]), int(row["v64_occurrences"]))
        for row in comparisons
    }
    assert observed_terms == {
        "ANSATZ": (143, 75), "ZUBEREITUNG": (7, 21), "AUSZUG": (1, 32), "ABSUD": (2, 2),
        "MAZERAT": (1, 7), "RUECKSTAND": (0, 0), "TROCKENGUT": (2, 5), "BAD": (0, 0),
        "EXTRAKT": (0, 2), "MASSE": (3, 10), "MISCHUNG": (1, 3),
    }
    checks.append("term_shift_143_to_75__auszug_1_to_32__mazerat_1_to_7__bad_zero")

    assert read_tsv(ART / "HISTORICAL_PREPARATION_CONTROL.tsv") == read_tsv(SRC / "HISTORICAL_PREPARATION_CONTROL.tsv")
    checks.append("historical_control_exact_copy_7")

    with tempfile.TemporaryDirectory(prefix="gdt691-replay-") as temp_name:
        temp = Path(temp_name)
        env = dict(os.environ)
        env["GDT691_OUTPUT_DIR"] = str(temp)
        replay = subprocess.run([sys.executable, str(RUN)], cwd=ROOT, env=env, capture_output=True, text=True, check=True)
        assert replay.stdout.strip()
        expected_names = set(result["files"]) | {"RESULT.json"}
        assert {path.name for path in temp.iterdir()} == expected_names
        for name in expected_names:
            assert (temp / name).read_bytes() == (ART / name).read_bytes(), name
    checks.append("exact_byte_replay_all_generated_files")

    validation = {
        "status": "PASS",
        "experiment": "GDT691",
        "checks": checks,
        "checks_passed": len(checks),
        "result_sha256": sha256(ART / "RESULT.json"),
        "validator_sha256": sha256(Path(__file__).resolve()),
    }
    (ART / "VALIDATION.json").write_text(json.dumps(validation, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(validation, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
