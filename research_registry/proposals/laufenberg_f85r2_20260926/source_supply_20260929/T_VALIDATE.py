#!/usr/bin/env python3
"""Validate T document receipts only; no semantic execution or corpus access."""
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = Path(__file__).resolve().parents[4]


def read(path):
    return json.loads(path.read_text())


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


receipts = read(HERE / "T_SOURCE_RECEIPTS.json")
for rel, expected in receipts["source_hashes"].items():
    assert digest(ROOT / rel) == expected, rel

units = read(HERE / "T_COMPLETE_UNITS.json")
seed, amulet, graft, sequel = [read(ROOT / p) for p in units["source_paths"]]
checks = [
    (units["seed_rite"]["target"], seed["target"]),
    (units["seed_rite"]["old_30_guesses"], seed["all_30_new_lexical_entries"]),
    (units["seed_rite"]["complete_clauses"], seed["complete_clauses"]),
    (units["seed_rite"]["complete_selected_source"], seed["complete_selected_source"]),
    (units["amulet"]["target"], amulet["target"]),
    (units["amulet"]["old_71_guesses"], amulet["lexicon"]),
    (units["amulet"]["complete_clauses"], amulet["complete_clauses"]),
    (units["amulet"]["complete_selected_source"], amulet["source"]),
    (units["graft"]["target"], graft["exact_target"]),
    (units["graft"]["old_23_guesses"], graft["whole_form_hypotheses"]),
    (units["graft"]["complete_clauses"], graft["complete_clause_partition"]),
    (units["graft"]["historical_source_scope"], graft["historical_source_scope"]),
    (units["amulet_commentary"]["target"], sequel["target"]),
    (units["amulet_commentary"]["complete_clauses"], sequel["complete_new_block_clauses"]),
    (units["amulet_commentary"]["old_17_additional_guesses"], sequel["new_17_lexical_entries"]),
    (units["amulet_commentary"]["source_scope"], sequel["source_scope"]),
]
assert all(a == b for a, b in checks)
assert len(units["seed_rite"]["old_30_guesses"]) == 30
assert len(units["amulet"]["old_71_guesses"]) == 71
graft_words = units["graft"]["old_23_guesses"]
assert len(graft_words["unchanged_nine"]) == 9
assert len(graft_words["new_fourteen"]) == 14
assert not (set(graft_words["unchanged_nine"]) & set(graft_words["new_fourteen"]))
assert len(units["amulet_commentary"]["old_17_additional_guesses"]) == 17

adds = read(HERE / "T_ADD_RECEIPTS.json")
assert len(adds) == 4
assert {json.loads(x["stdout"])["id"] for x in adds} == {
    "IDEA000773", "IDEA000774", "IDEA000775", "IDEA000776"
}
for add in adds:
    assert add["exit_code"] == 0
    proposal = read(ROOT / add["proposal"])
    assert proposal["status"] == "RAW_UNREVIEWED_NOT_SELECTED_NOT_TESTED"
    assert len(proposal["two_discriminating_consequences"]) == 2
    assert proposal["strongest_known_countercases"]
    assert proposal["primary_paths"] and proposal["target_anchors"]
    for rel, expected in proposal["primary_hashes"].items():
        assert digest(ROOT / rel) == expected

files = [p for p in sorted(HERE.glob("T_*")) if p.is_file()
         and p.name != "T_VALIDATION.json"]
# Publication privacy is checked on the exact staged tree by work_preflight;
# this checker verifies source receipts and copied fields only.

result = {
    "status": "PASS_DOCUMENT_INTEGRITY_ONLY",
    "source_hashes_checked": len(receipts["source_hashes"]),
    "exact_structured_field_copies": len(checks),
    "raw_cards": 4,
    "new_target_admissions": 0,
    "semantic_tests_executed": 0,
    "meaning_confirmation": False,
    "files": {str(p.relative_to(ROOT)): digest(p) for p in files},
}
(HERE / "T_VALIDATION.json").write_text(
    json.dumps(result, ensure_ascii=False, indent=2) + "\n"
)
print(json.dumps({k: v for k, v in result.items() if k != "files"}))
