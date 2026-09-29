#!/usr/bin/env python3
"""Check the complete lexical account, not the manual semantic derivation."""
import csv
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    result = json.loads((HERE / "T_PROVENANCE_RESULT.json").read_text())
    parent_path = ROOT / result["parent"]
    assert digest(parent_path) == result["parent_sha256"]
    parent = json.loads(parent_path.read_text())
    with (HERE / "T_PROVENANCE_ALL_GROUPS.tsv").open() as handle:
        rows = list(csv.DictReader(handle, delimiter="\t"))
    expected = []
    summaries = []
    changed = 0
    for unit in parent["units"]:
        unknown = []
        count = 0
        fused = 0
        for block in unit["blocks"]:
            for group in block["groups"]:
                old = group["analyses"]
                new = [a for a in old if a["parts"] != ["saiin"]]
                raw = group["raw"]
                changed += old != new
                count += 1
                fused += raw == "saiin"
                if raw == "saiin":
                    assert new == [{"parts": ["s", "aiin"], "tags": ["ALSO", "OF"]}]
                else:
                    assert new == old
                if not new:
                    unknown.append({"source_id": group["source_id"], "raw": raw})
                account = ("NO_LEXICAL_ANALYSIS" if not new else
                           "C0_DERIVED_ALSO_OF_SCOPE_REQUIRED" if raw == "saiin" else
                           "INHERITED_ALTERNATIVES_NO_NEW_SEMANTIC_VALIDATION")
                expected.append({
                    "unit": unit["id"], "reader": unit["reader"],
                    "source_status": unit["source_status"], "block": block["id"],
                    "source_id": group["source_id"], "locus": group["locus"],
                    "raw": raw, "anchor_eligible": "" if group["anchor_eligible"] is None
                    else str(group["anchor_eligible"]),
                    "old_analyses": old, "v1_analyses": new, "account": account,
                })
        summaries.append({"unit": unit["id"], "groups": count, "saiin_groups": fused,
                          "unbound": unknown, "meaning_test": False})
    for row in rows:
        for key in ("old_analyses", "v1_analyses"):
            row[key] = json.loads(row[key])
    assert rows == expected
    assert len(rows) == 316 and changed == 4
    assert summaries == result["units"]
    assert len(parent["lexicon"]) == len(parent["inventory"]) == 88
    assert parent["lexicon"]["saiin"]["tag"] == "ALTERNATIVELY"
    assert result["combined_atomic_inventory"] == {"before": 88, "after": 87}
    original = json.loads((ROOT / "experiments/yolo/gdt1023_amulet_complete_typed_assembly/src/SOURCE.json").read_text())
    assert len(original["lexicon"]) == 71
    assert result["original_atomic_inventory"] == {"before": 71, "after": 70}
    assert result["removed_atomic_values"] == ["saiin=ALTERNATIVELY"]
    assert result["new_atomic_word_values"] == result["confirmed_words"] == 0
    assert result["independent_meaning_confirmation"] == 0
    assert result["new_fixed_test"] is False
    assert len(result["new_grammar_costs"]) == 7
    names = ["T_ROOT_DECISION.md", "T_PROVENANCE_RULE.md", "T_PROVENANCE_REPORT.md",
             "T_PROVENANCE_RESULT.json", "T_PROVENANCE_ALL_GROUPS.tsv"]
    output = {"status": "PASS_DOCUMENT_AND_LEXICAL_ACCOUNTING_ONLY", "groups": len(rows),
              "whole_units": len(summaries), "changed_saiin_records": changed,
              "unbound_by_unit": {s["unit"]: len(s["unbound"]) for s in summaries},
              "semantic_rules_executed": False, "new_manuscript_query": False,
              "independent_meaning_confirmation": 0,
              "files": {name: digest(HERE / name) for name in names}}
    (HERE / "T_PROVENANCE_VALIDATION.json").write_text(json.dumps(output, indent=2) + "\n")
    print(json.dumps({k: v for k, v in output.items() if k != "files"}))


if __name__ == "__main__":
    main()
