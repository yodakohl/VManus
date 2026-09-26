#!/usr/bin/env python3
"""Check frozen source conservation and occurrence completeness, not meanings."""
import csv
import hashlib
import json
from pathlib import Path

BASE = Path(__file__).resolve().parent
ROOT = BASE.parents[2]
PACKET = BASE / "resemblance_fire_draft"
checks = []


def require(value, name):
    if not value:
        raise AssertionError(name)
    checks.append(name)


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


receipt = json.loads((PACKET / "FREEZE_RECEIPT.json").read_text())
for filename, expected in receipt["files"].items():
    require(digest(PACKET / filename) == expected, "freeze:" + filename)
draft = json.loads((PACKET / "DRAFT.json").read_text())
source = ROOT / "experiments/yolo/gdt1042_f85r2_source_program_surface_census/artifacts/native_groups.tsv"
for filename, expected in draft["input_hashes"].items():
    path = source if filename == "GDT1042/artifacts/native_groups.tsv" else BASE / filename
    require(digest(path) == expected, "input:" + filename)
raw = json.loads((BASE / "ideas/30_resemblance_respect_subject_reference.json").read_text())["design"]
old = draft["frozen_twelve_whole_entries"]
subject_description_pairs = {
    "chepaiin": ("the ELEVENTH_HEAVEN", "ELEVENTH_HEAVEN"),
    "olkaiin": ("the TENTH_HEAVEN", "TENTH_HEAVEN"),
}
for form, value in raw["primitive_whole_values"].items():
    if form in subject_description_pairs:
        # Explicitly reviewed prose-label difference, not a target-form alias.
        require(value["type"] == old[form]["type"] == "Subject"
                and (value["meaning"], old[form]["meaning"]) == subject_description_pairs[form],
                "same fixed subject constant; declared article omission:" + form)
    else:
        require(old[form] == value, "unchanged primitive:" + form)
require(draft["frozen_ot"]["law"] == raw["constructor"]["ot"]["law"], "unchanged ot law")
require(draft["frozen_ot"]["type"] == raw["constructor"]["ot"]["type"], "unchanged ot signature")
require(draft["frozen_ot"]["licensed_literal_derivations_only"] == raw["literal_derivations"], "unchanged derivations")
require(draft["grammar"]["old_productions_unchanged"] == raw["grammar"]["rules"], "unchanged old grammar")
require(len(old) == 12 and len(draft["new_whole_entries"]) == 3, "declared value counts")
require(not (set(old) & set(draft["new_whole_entries"])), "no overwritten old entry")
# This is the hash-checked, exclusively f85r2-owned projection, not a mixed source.
with source.open() as handle:
    rows = list(csv.DictReader(handle, delimiter="\t"))
require(len(rows) == 473, "complete owned projection")
forms = set(old) | set(draft["new_whole_entries"])
expected = [r for r in rows if r["ivtff_group_raw"] in forms]
with (PACKET / "ASSIGNED_OCCURRENCES.tsv").open() as handle:
    observed = list(csv.DictReader(handle, delimiter="\t"))
require(observed == expected, "all and only exact assigned occurrences with full unchanged rows")
local = [r for r in rows if r["edition"] == "ZL3b" and r["locus"] == "f85r2.1" and 8 <= int(r["source_group_index"]) <= 12]
require(" ".join(r["ivtff_group_raw"] for r in local) == draft["target"]["literal"], "literal local span")
require([r["source_group_id"] for r in local] == [r["id"] for r in draft["all_five_occurrences"]], "five source identities owned once")
require(all(r["right_separator"] == "DEFINITE_SPACE" for r in local[:-1]), "four internal literal spaces")
for form, identities in draft["other_occurrence_obligations"]["new_forms_complete_inventory"].items():
    actual = [r["source_group_id"] for r in expected if r["ivtff_group_raw"] == form]
    require(sorted(actual) == sorted(identities), "new-form inventory:" + form)
print(json.dumps({"status": "PASS", "checks": checks, "occurrence_rows": len(observed),
                  "meaning": "frozen integrity and source coverage only; no semantic execution, parser validation or word confirmation"}, indent=2))
