#!/usr/bin/env python3
"""Source completeness and draft conservation, never meaning confirmation."""
import csv
import hashlib
import json
from collections import Counter
from pathlib import Path
import sys

BASE = Path(__file__).resolve().parent
ROOT = BASE.parents[3]
sys.path.insert(0, str(ROOT))
from tools.word_profiles import ensure_cache, occurrences

direct = json.loads((BASE / "CF_DIRECT_CONTEXTS.json").read_text())
source = json.loads((BASE / "CF_FULL_LEAVES.json").read_text())
result = json.loads((BASE / "CF_RESULT.json").read_text())
ce = json.loads((BASE / "CE_RESULT.json").read_text())
with (BASE / "CF_OCCURRENCE_OBLIGATIONS.tsv").open() as file:
    rows = list(csv.DictReader(file, delimiter="\t"))
conn = ensure_cache(ROOT)
expected = [r for form in ("cthy", "otaiin", "oky") for r in occurrences(conn, form)]
assert len(rows) == len(expected) == direct["obligation_count"] == 941
assert [{k: "" if v is None else str(v) for k, v in r.items()} for r in expected] == rows
assert direct["cache_receipt"]["inputs"]["source_sha256"] == source["source_sha256"]
assert hashlib.sha256((ROOT / source["command"][2]).read_bytes()).hexdigest() == source["source_sha256"]
for name, expected_hash in (("CE_SOURCE.json", direct["ce_source_sha256"]),
                             ("CF_DECISION.md", direct["decision_sha256"]),
                             ("CF_DIRECT_CONTEXTS.json", source["direct_contexts_sha256"])):
    assert hashlib.sha256((BASE / name).read_bytes()).hexdigest() == expected_hash
pairs = {frozenset(p) for p in (("cthy", "otaiin"), ("otaiin", "oky"), ("cthy", "oky"))}
expected_ids = [r["source_group_id"] for r in expected if frozenset((r["ivtff_group_raw"], r["next_literal"])) in pairs]
assert expected_ids == [r["left_id"] for r in direct["edges"]]
assert len(expected_ids) == 10
assert {r["locus"] for r in direct["edges"]} == {"f9r.3", "f9v.3", "f50v.9"}
assert not any({r["left"], r["right"]} == {"cthy", "oky"} for r in direct["edges"])
assert {r["page"] for r in source["rows"]} == {"f9r", "f9v", "f50r", "f50v"}
assert len(source["rows"]) == 1070 and len(source["lines"]) == 129
raw = [r for line in source["lines"] for r in line["groups"]]
assert {r["source_group_id"] for r in raw} == {r["source_group_id"] for r in source["rows"]}
assert len(raw) == len({r["source_group_id"] for r in raw}) == 1070
assert all(not r["page"].startswith("f84") for r in raw + expected)
assert not any(r["ivtff_group_raw"] == "cthy" and r["page"].startswith("f50") for r in raw)
for line in source["lines"]:
    assert [int(r["source_group_index"]) for r in line["groups"]] == list(range(1, len(line["groups"]) + 1))
    assert all(int(r["source_group_count"]) == len(line["groups"]) for r in line["groups"])
assert len(result["models"]) == 4
for model in result["models"]:
    assert len(model["whole_form_assumptions"]) == 7
    assert all(model["whole_form_assumptions"][k] == v for k, v in ce["whole_form_assumptions"].items())
    assert [r["source_group_id"] for r in raw] == [r["source_group_id"] for r in model["positions"]]
    for r, p in zip(raw, model["positions"]):
        assert r["ivtff_group_raw"] == p["raw"]
        assert p["hypothesis"] == model["whole_form_assumptions"].get(p["raw"])
    assert sum(p["hypothesis"] is not None for p in model["positions"]) == model["assumed_positions"] == 57
    assert model["unread_positions"] == 1013
    assert "taiin" not in model["whole_form_assumptions"]
    assert "cthor" not in model["whole_form_assumptions"]
assert result["confirmed_words"] == result["independent_meaning_confirmation_leaves"] == 0
files = sorted(p.name for p in BASE.glob("CF_*") if p.is_file() and p.name != "CF_VALIDATION.json")
receipt = {"status": "PASS_SOURCE_EXHAUSTIVENESS_AND_DRAFT_CONSERVATION_ONLY",
    "meaning_verified": False, "semantic_models_selected": 0,
    "claims_checked": ["941 exact exposed obligations, fixed direct pairs exhaustive", "four complete text sides, raw entities and boundaries conserved", "all four drafts retain unknowns and CE assumptions", "no taiin/cthor alias, zero confirmation"],
    "counts": dict(Counter(r["edition"] for r in source["rows"])),
    "file_sha256": {name: hashlib.sha256((BASE / name).read_bytes()).hexdigest() for name in files}}
(BASE / "CF_VALIDATION.json").write_text(json.dumps(receipt, indent=2) + "\n")
print(receipt["status"], "941 obligations;1070 raw groups;4 unconfirmed drafts")
