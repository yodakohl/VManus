#!/usr/bin/env python3
"""Replay the corrected source packet; no target or semantic inference."""
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent


def read(name):
    return json.loads((HERE / name).read_text(encoding="utf-8"))


def main():
    old = read("G_SOURCE_RECEIPTS.json")
    correction = read("G_BOUNDARY_CORRECTION_RECEIPTS.json")
    expected = {x["file"]: x["sha256"] for x in old["files"]}
    expected.update({x["file"]: x["sha256"] for x in correction["files"]})
    for name, digest in expected.items():
        assert hashlib.sha256((HERE / name).read_bytes()).hexdigest() == digest, name
    source = read("G_CORRECTED_COMPLETE_PROLOGUE.json")
    proper = source["prologue_proper"]
    headings = source["appended_capitula"]
    assert [x["paragraph"] for x in proper] == list(range(1, 7))
    assert [x["number"] for x in headings] == list(range(1, 13))
    assert all(len(x["clauses"]) == 4 for x in headings)
    assert "unus sit et indiuisus" in proper[3]["text"]
    assert source["closing_admonition"].startswith("Expergiscere proinde")
    assert source["explicit"].startswith("EXPLICIT PROLOGVS, INCIPIT TRACTATVS")
    assert source["diagram_clauses_diplomatically_collated"] is False
    raw = read("G_RAW_ONE_REFERENT_MANY_FRUITS.json")
    assert raw["status"] == "RAW_UNREVIEWED"
    result = {
        "status": "PASS",
        "source_files_hash_checked": len(expected),
        "prologue_proper_paragraphs": len(proper),
        "appended_capitula_groups": len(headings),
        "appended_capitula_clauses": sum(len(x["clauses"]) for x in headings),
        "earlier_boundary_claim_superseded": True,
        "full_diagram_diplomatic_collation": False,
        "target_comparison_executed": False,
        "manuscript_meaning_verified": False,
    }
    (HERE / "G_ROOT_VALIDATION.json").write_text(
        json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
