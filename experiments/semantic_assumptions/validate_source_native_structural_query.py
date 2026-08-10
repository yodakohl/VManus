#!/usr/bin/env python3
"""Independent subprocess validation of the source-native concordance tool."""

from __future__ import annotations

import csv
import hashlib
import json
import re
import subprocess
import sys
from collections import defaultdict
from pathlib import Path


BASE = Path(__file__).resolve().parent
RESULTS = BASE / "results"
SOURCE = RESULTS / "source_native_structural_interlinear_v1.tsv"
SPEC = BASE / "SOURCE_NATIVE_STRUCTURAL_QUERY_SPEC.md"
TOOL = BASE / "query_source_native_structural_reading.py"
OUT = RESULTS / "source_native_structural_query_validation.json"
REPORT = RESULTS / "source_native_structural_query_validation_report.md"
EXPECTED = {
    SOURCE: "95a15329c61a11c1c4dc671b4df2b3482af9d25a1108eadac2f69b066d3785af",
    SPEC: "b9b1a14bf723aacd64de0b8625291ea37534c381e7000795b0651c1dcec5c556",
    TOOL: "6bc525c8b32300e0cac938bcefc1a89b413277f68c4b1122fd3cb6e5d08c1745",
}
TAG_FIELDS = (
    "opening_feature_hits", "closing_feature_hits", "favored_transition_hits",
    "disfavored_transition_hits", "unresolved_transition_hits",
    "favored_path_hits", "longest_opening_path", "longest_path_anywhere",
)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical(value: object) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode()


def query(*args: str) -> dict:
    proc = subprocess.run(
        [sys.executable, str(TOOL), *args, "--format", "json", "--max-loci", "100000"],
        cwd=BASE.parent.parent, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
    )
    if proc.returncode != 0:
        raise AssertionError(f"query failed {args}: {proc.stderr}")
    return json.loads(proc.stdout)


def projection(items: list[dict]) -> list[dict]:
    return [{
        "locus": item["locus"], "page": item["page"],
        "hits": item["hit_group_indices"], "sequence": item["family_sequence"],
    } for item in items]


def run() -> dict:
    checks = 0
    for path, expected in EXPECTED.items():
        assert sha(path) == expected
        checks += 1
    with SOURCE.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle, delimiter="\t"))
    assert len(rows) == 23281
    assert len({row["consensus_group_id"] for row in rows}) == 23281
    checks += 2
    loci: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        loci[row["locus"]].append(row)
    for values in loci.values():
        values.sort(key=lambda row: int(row["group_index"]))
    assert len(loci) == 3572
    checks += 1

    cases = [
        ("all", (), lambda row: True, None),
        ("exact_DAQKA", ("--surface-regex", "^DAQKA$"), lambda row: row["family_surface"] == "DAQKA", None),
        ("internal_DAQK_first", ("--contains", "DAQK", "--position", "FIRST"), lambda row: "DAQK" in row["family_surface"] and row["factual_position"] == "FIRST", None),
        ("exact_member", ("--member-regex", "^D1 A1 Q1 K1 A2$"), lambda row: any(value == "D1 A1 Q1 K1 A2" for value in (row["zl_sta_codes"], row["it_sta_codes"], row["rf_sta_codes"])), None),
        ("drawing_boundary", ("--boundary-regex", "DRAWING_INTERRUPTION"), lambda row: "DRAWING_INTERRUPTION" in row["left_boundary_profile"] or "DRAWING_INTERRUPTION" in row["right_boundary_profile"], None),
        ("favored_AQ_path", ("--tag-regex", "(^|;)AQ(;|$)"), lambda row: bool(re.search(r"(^|;)AQ(;|$)", ";".join(row[field] for field in TAG_FIELDS))), None),
        ("circle_block_labels", ("--page-regex", r"^f(6[7-9]|7[0-3])", "--scope", "DIAGNOSTIC_NONPROSE", "--kind", "L"), lambda row: True, lambda first: bool(re.search(r"^f(6[7-9]|7[0-3])", first["page"])) and first["grammar_scope"] == "DIAGNOSTIC_NONPROSE" and first["kind"] == "L"),
    ]
    summaries = {}
    for name, args, row_filter, locus_filter in cases:
        expected_items = []
        expected_groups = 0
        for locus, locus_rows in loci.items():
            if locus_filter and not locus_filter(locus_rows[0]):
                continue
            hits = [int(row["group_index"]) for row in locus_rows if row_filter(row)]
            if not hits:
                continue
            expected_groups += len(hits)
            expected_items.append({"locus": locus, "page": locus_rows[0]["page"], "hits": hits, "sequence": " ".join(row["family_surface"] for row in locus_rows)})
        actual = query(*args)
        actual_items = projection(actual["matches"])
        assert actual_items == expected_items
        assert actual["metadata"]["matching_loci"] == len(expected_items)
        assert actual["metadata"]["matching_groups"] == expected_groups
        assert actual["metadata"]["returned_loci"] == len(expected_items)
        assert actual["metadata"]["truncated"] is False
        checks += 4 + len(expected_items)
        summaries[name] = {
            "loci": len(expected_items), "groups": expected_groups,
            "projection_sha256": hashlib.sha256(canonical(expected_items)).hexdigest(),
        }

    pattern = re.compile(r"DAQKA BAG")
    expected_items = []
    expected_groups = 0
    for locus, locus_rows in loci.items():
        surfaces = [row["family_surface"] for row in locus_rows]
        sequence = " ".join(surfaces)
        matches = list(pattern.finditer(sequence))
        if not matches:
            continue
        offset = 0
        spans = []
        for index, surface in enumerate(surfaces, 1):
            spans.append((index, offset, offset + len(surface)))
            offset += len(surface) + 1
        hits = sorted({index for match in matches for index, start, end in spans if start < match.end() and end > match.start()})
        expected_groups += len(hits)
        expected_items.append({"locus": locus, "page": locus_rows[0]["page"], "hits": hits, "sequence": sequence})
    actual = query("--locus-sequence-regex", "DAQKA BAG")
    assert projection(actual["matches"]) == expected_items
    assert actual["metadata"]["matching_loci"] == len(expected_items)
    assert actual["metadata"]["matching_groups"] == expected_groups
    checks += 3 + len(expected_items)
    summaries["cross_group_DAQKA_BAG"] = {
        "loci": len(expected_items), "groups": expected_groups,
        "projection_sha256": hashlib.sha256(canonical(expected_items)).hexdigest(),
    }

    text_proc = subprocess.run(
        [sys.executable, str(TOOL), "--surface-regex", "^DAQKA$", "--max-loci", "1"],
        cwd=BASE.parent.parent, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
    )
    assert text_proc.returncode == 0 and "*" in text_proc.stdout and "Concordance hits only" in text_proc.stdout
    checks += 1
    bad_regex = subprocess.run([sys.executable, str(TOOL), "--surface-regex", "["], cwd=BASE.parent.parent, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    assert bad_regex.returncode != 0 and "invalid surface regular expression" in bad_regex.stderr
    checks += 1
    bad_limit = subprocess.run([sys.executable, str(TOOL), "--max-loci", "-1"], cwd=BASE.parent.parent, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    assert bad_limit.returncode != 0 and "must be nonnegative" in bad_limit.stderr
    checks += 1

    return {
        "experiment": "SOURCE_NATIVE_STRUCTURAL_QUERY_VALIDATION",
        "status": "PASS_INDEPENDENT_SUBPROCESS_CONCORDANCE_VALIDATION",
        "checks": checks, "source_groups": len(rows), "source_loci": len(loci),
        "query_cases": summaries, "input_sha256": {path.name: sha(path) for path in EXPECTED},
        "mutation_guards": {"invalid_regex_rejected": True, "negative_limit_rejected": True},
        "english_glosses": 0,
        "claim_ceiling": "Validated concordance infrastructure only; no word, morpheme, sound, POS, meaning, plaintext, language, cipher, or translation.",
    }


def main() -> None:
    result = run()
    OUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    REPORT.write_text(
        "# Source-native structural query validation\n\n"
        f"Status: **{result['status']}**.\n\n"
        f"Independent subprocess reconstruction passed **{result['checks']:,}** checks over **{result['source_groups']:,}** groups and **{result['source_loci']:,}** loci. It validates whole-form, internal-fragment, cross-group-sequence, exact-member, lossy-EVA-capable, structural-tag, separator, and metadata filtering while rejecting malformed queries.\n\n"
        "This is fast zero-gloss concordance infrastructure. Search hits are not words, morphemes, sounds, POS labels, meanings, plaintext, language, cipher, or translation.\n",
        encoding="utf-8",
    )
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
