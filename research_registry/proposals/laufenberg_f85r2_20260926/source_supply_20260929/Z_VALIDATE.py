#!/usr/bin/env python3
"""Document-integrity checks only; no new target query or semantic execution."""
import csv
import hashlib
import json
from pathlib import Path

BASE = Path(__file__).resolve().parent
ROOT = BASE.parents[3]
checks = []


def check(name, condition):
    checks.append({"name": name, "pass": bool(condition)})


def read(path):
    return json.loads(path.read_text(encoding="utf-8"))


units = read(BASE / "Z_COMPLETE_UNITS.json")
original = read(BASE / "T_COMPLETE_UNITS.json")
parent = read(ROOT / "experiments/yolo/gdt1023_amulet_complete_typed_assembly/src/SOURCE.json")
sequel = read(ROOT / "research_registry/proposals/raw_f108r_amulet_frozen71_complete_commentary_20260921.json")
for key in ("amulet", "amulet_commentary"):
    check("exact owned copy " + key, units[key] == original[key])
check("original grammar retained", units["old_parent_grammar_contract"] == parent["grammar_contract"])
check("all eleven sequel bindings retained", units["old_commentary_binding_assumptions"] == sequel["new_binding_assumptions"] and len(units["old_commentary_binding_assumptions"]) == 11)
check("exact sequel grammar retained", units["old_commentary_grammar"] == sequel["exact_new_grammar"])
check("71 old parent values", len(units["amulet"]["old_71_guesses"]) == 71)
check("17 old commentary values", len(units["amulet_commentary"]["old_17_additional_guesses"]) == 17)
check("parent values equal primary", units["amulet"]["old_71_guesses"] == parent["lexicon"])
check("commentary values equal primary", units["amulet_commentary"]["old_17_additional_guesses"] == sequel["new_17_lexical_entries"])
check("nine plus four complete clauses", len(units["amulet"]["complete_clauses"]) == 9 and len(units["amulet_commentary"]["complete_clauses"]) == 4)

t = units["amulet"]["target"]
c = units["amulet_commentary"]["target"]
records = [("P12", t["owned_projection"]["records"])]
for reader, key in (("ZL3b", "diplomatic_ZL3b"), ("IT2a", "diplomatic_IT2a")):
    records.append((reader, t[key]["lines"]))
for reader, key in (("ZL3b", "complete_raw_record"), ("IT2a", "alternate_IT2a_complete_record")):
    records.append((reader, c[key]["lines"]))
expected_counts = [84, 84, 83, 33, 32]
observed = []
for (reader, lines), expected in zip(records, expected_counts):
    observed.append(sum(len(line["words"] if "words" in line else line["raw"].split()) for line in lines))
    check("whole count " + reader + " " + lines[0]["locus"], observed[-1] == expected)
check("all316 retained positions", sum(observed) == 316)
check("parent clauses cover whole projection", [w for clause in units["amulet"]["complete_clauses"] for w in clause["raw"].split()] == [w for line in t["owned_projection"]["records"] for w in line["raw"].split()])
check("commentary clauses cover whole ZL record", [w for clause in units["amulet_commentary"]["complete_clauses"] for w in clause["words"]] == [w for line in c["complete_raw_record"]["lines"] for w in line["words"]])
check("all three parent raw gaps retained", len(t["P12_vs_ZL_unbound"]) == 3)
check("rawZL eligibility unchanged", [r["anchor_eligible"] for r in c["complete_raw_record"]["lines"]] == [True, False, False])

selected = {"qokain", "qokaiin", "chkain", "cheedar", "okedy"}
expected_rows = []
for reader, lines in records:
    for line in lines:
        words = line["words"] if "words" in line else line["raw"].split()
        for n, word in enumerate(words, 1):
            if word in selected:
                expected_rows.append({"reader": reader, "locus": line["locus"], "group": str(n), "word": word, "whole_line": " ".join(words)})
with (BASE / "Z_REFERENCE_OCCURRENCES.tsv").open(encoding="utf-8", newline="") as handle:
    rows = list(csv.DictReader(handle, delimiter="\t"))
check("complete selected exact occurrences", rows == expected_rows)
check("no qokain in commentary", not any(r["word"] == "qokain" and r["locus"].startswith("f108r.") for r in rows))
for receipt in read(BASE / "Z_INPUTS.json")["fixed_inputs"]:
    path = ROOT / receipt["path"]
    check("input hash " + receipt["path"], hashlib.sha256(path.read_bytes()).hexdigest() == receipt["sha256"])
result = {"status": "PASS" if all(x["pass"] for x in checks) else "FAIL", "kind": "DOCUMENT_INTEGRITY_ONLY_NOT_SEMANTIC_TEST", "checks": checks, "check_count": len(checks)}
(BASE / "Z_VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(json.dumps({"status": result["status"], "kind": result["kind"], "check_count": len(checks)}))
raise SystemExit(0 if result["status"] == "PASS" else 1)
