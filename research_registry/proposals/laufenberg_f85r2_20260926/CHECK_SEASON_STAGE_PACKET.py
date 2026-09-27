#!/usr/bin/env python3
"""Read-only literal audit of the frozen IDEA595 packet; NOT a semantic executor.

Scope is exactly the already-admitted 473-row GDT1042 projection. No mixed raw
data, lookup, spelling normalization, alignment repair or target acquisition.
Run with Python 3 from any directory. JSON goes to stdout; exit 1 means a literal
or inventory mismatch. PASS does not validate meanings, grammar or source fit.
"""

import collections
import csv
import hashlib
import json
from pathlib import Path


BASE = Path(__file__).resolve().parent
REPO = BASE.parents[2]
SOURCE = REPO / "experiments/yolo/gdt1042_f85r2_source_program_surface_census/artifacts/native_groups.tsv"
FIELDS = [
    "edition", "block", "locus", "source_group_id", "source_group_index",
    "source_group_count", "within_line_position", "paragraph_start",
    "paragraph_end", "left_separator", "right_separator", "ivtff_group_raw",
]
FREEZE_SHA = "49b604c9781ea6d5e75102173ad1ab54cd7ca3e63530e3ff2b76e856b709d984"
READERS = ["ZL3b", "IT2a", "RF1b"]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_tsv(path):
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle, delimiter="\t")
        return reader.fieldnames, list(reader)


def audit():
    failures = []
    checked = 0

    def check(name, condition, detail=None):
        nonlocal checked
        checked += 1
        if not condition:
            failures.append({"check": name, "detail": detail})

    freeze_path = BASE / "SEASON_STAGE_AUTHOR_FREEZE_RECEIPT.json"
    check("unchanged_freeze_receipt", sha(freeze_path) == FREEZE_SHA)
    freeze = json.loads(freeze_path.read_text(encoding="utf-8"))
    for name, item in freeze["files"].items():
        check("frozen_author_hash", sha(BASE / name) == item["sha256"], name)
    for name, item in freeze["source_receipts"].items():
        check("frozen_dependency_hash", sha(REPO / name) == item["sha256"], name)

    draft = json.loads((BASE / "SEASON_STAGE_AUTHOR_DRAFT.json").read_text(encoding="utf-8"))
    header, source = read_tsv(SOURCE)
    _, tsv = read_tsv(BASE / "SEASON_STAGE_AUTHOR_473_CONSEQUENCES.tsv")
    rows = draft["all473_consequences"]
    lexicon = draft["lexicon"]
    check("source_exact_12_columns", header == FIELDS)
    check("source_473_rows", len(source) == 473)
    for name, candidate in [("JSON", rows), ("TSV", tsv)]:
        check(name + "_row_count", len(candidate) == len(source))
        check(name + "_ordered_original_12field_tuples",
              [tuple(r.get(k) for k in FIELDS) for r in candidate]
              == [tuple(r[k] for k in FIELDS) for r in source])
    check("JSON_TSV_all_fields_equal", rows == tsv)

    by_literal = collections.defaultdict(list)
    by_line = collections.defaultdict(list)
    by_id = {r["source_group_id"]: r for r in source}
    check("unique_source_ids", len(by_id) == len(source))
    for row in source:
        by_literal[row["ivtff_group_raw"]].append(row)
        by_line[(row["edition"], row["locus"])].append(row)
    coverage = {}
    repetitions = {}
    for edition in READERS:
        selected = [r for r in source if r["edition"] == edition]
        counts = collections.Counter(r["ivtff_group_raw"] for r in selected)
        assigned = sum(r["ivtff_group_raw"] in lexicon for r in selected)
        coverage[edition] = {"rows": len(selected), "types": len(counts),
                             "assigned": assigned, "unassigned": len(selected) - assigned}
        check("reader_coverage", {k: coverage[edition][k] for k in
              ["rows", "assigned", "unassigned"]} == draft["reader_counts"][edition], edition)
        repetitions[edition] = {"repeated_types": sum(n > 1 for n in counts.values()),
                                "occurrences": sum(n for n in counts.values() if n > 1),
                                "beyond_first": sum(n - 1 for n in counts.values() if n > 1)}

    for word, entry in lexicon.items():
        actual = by_literal[word]
        check("lexicon_all_occurrences", entry["all_occurrences"] ==
              [r["source_group_id"] for r in actual], word)
        check("lexicon_ZL_occurrences", entry["zl_occurrences"] ==
              [r["source_group_id"] for r in actual if r["edition"] == "ZL3b"], word)
    for row in rows:
        entry = lexicon.get(row["ivtff_group_raw"])
        expected = ((entry["value"], entry["type"], entry["origin"]) if entry else
                    ("UNASSIGNED", "UNKNOWN", "unassigned_literal"))
        check("literal_value_type_origin", tuple(row[k] for k in
              ["assigned_value", "assigned_type", "origin"]) == expected, row["source_group_id"])

    owned_ids = []
    roles = []
    for clause in draft["manual_clauses"]:
        owned_ids.extend(clause["source_ids"])
        roles.extend(clause["ordered_token_roles"])
        check("manual_clause_literal_words", clause["literal_words"] ==
              [by_id[i]["ivtff_group_raw"] for i in clause["source_ids"]], clause["id"])
    expected_zl_ids = [r["source_group_id"] for r in source if r["edition"] == "ZL3b"]
    check("all156_ordered_manual_ids", owned_ids == expected_zl_ids)
    check("all156_ordered_token_role_ids", [r["id"] for r in roles] == expected_zl_ids)
    for role in roles:
        word = by_id[role["id"]]["ivtff_group_raw"]
        entry = lexicon[word]
        check("manual_role_literal_value_type", (role["literal"], role["value"], role["type"])
              == (word, entry["value"], entry["type"]), role["id"])

    morphology = draft["morphology"]
    check("finite_family_declared_domain", morphology["component"] == "qo"
          and morphology["domain"] == ["dar", "daiin"])
    check("finite_family_declared_cuts", morphology["cuts"] ==
          {"qodar": ["qo", "dar"], "qodaiin": ["qo", "daiin"]})
    declared = {r["literal"]: r for r in morphology["all_qo_substring_residuals"]}
    actual_qo = {word for word in by_literal if "qo" in word}
    check("every_qo_literal_once", set(declared) == actual_qo and
          len(declared) == len(morphology["all_qo_substring_residuals"]))
    qo_counts = collections.Counter()
    qo_type_counts = collections.Counter()
    for word in sorted(actual_qo):
        cut = ["qo", word[2:]] if word.startswith("qo") and word[2:] in ["dar", "daiin"] else None
        status = "derived" if cut else "paid_whole_residual" if word in lexicon else "unassigned_alternate_literal"
        expected_ids = [r["source_group_id"] for r in by_literal[word]]
        entry = declared.get(word, {})
        check("qo_cut_status_occurrences", (entry.get("licensed_cut"), entry.get("status"),
              entry.get("all_occurrences")) == (cut, status, expected_ids), word)
        qo_counts[status] += len(expected_ids)
        qo_type_counts[status] += 1
    family = [r for r in source if r["ivtff_group_raw"] in ["dar", "daiin", "qodar", "qodaiin"]]
    expected_family = [{"id": r["source_group_id"], "literal": r["ivtff_group_raw"],
                        "assigned_value": lexicon[r["ivtff_group_raw"]]["value"],
                        "type": lexicon[r["ivtff_group_raw"]]["type"]} for r in family]
    check("bare_roots_and_compounds_all22", expected_family ==
          [{k: r[k] for k in ["id", "literal", "assigned_value", "type"]}
           for r in morphology["all_bare_roots_and_compounds"]])
    for line in draft["alternate_lines"]:
        for edition, literals in line["readers"].items():
            check("complete_alternate_line_literals", literals ==
                  [r["ivtff_group_raw"] for r in by_line[(edition, line["locus"])]],
                  edition + "|" + line["locus"])
    for edition in ["IT2a", "RF1b"]:
        check("exact_unassigned_alternate_ids",
              [r["id"] for r in draft["unassigned_alternate_literals"][edition]] ==
              [r["source_group_id"] for r in source if r["edition"] == edition
               and r["ivtff_group_raw"] not in lexicon], edition)

    return {"status": "PASS_LITERAL_INVENTORY_ONLY" if not failures else "FAIL_LITERAL_INVENTORY",
            "semantic_executor": False, "checks": checked, "failures": failures,
            "coverage": coverage, "repetitions": repetitions,
            "qo_types": dict(qo_type_counts), "qo_occurrences": dict(qo_counts),
            "limits": "No semantic/source-equivalence/grammar verdict. Manual LIKE-direction and alternate-template findings remain in SEASON_STAGE_LITERAL_C_REVIEW.md; this checker does not repair or adjudicate them."}


if __name__ == "__main__":
    result = audit()
    print(json.dumps(result, ensure_ascii=False, indent=2))
    raise SystemExit(1 if result["failures"] else 0)
