#!/usr/bin/env python3
"""Compare one fixed source diagram to IDEA129's candidate rule, not to Voynich."""
import hashlib
import json
from pathlib import Path

D = Path(__file__).resolve().parent
source = D / "SOURCE_FIGURES_B.json"
assert hashlib.sha256(source.read_bytes()).hexdigest() == "b5d8f749eee53fef9dad97741c36ab2421669c7a666dbdb26234ee4dcccc755b"
receipt = json.loads(source.read_text())
assert hashlib.sha256((D / "p3.jpg").read_bytes()).hexdigest() == receipt["hashes"]["p3.jpg"]
figures = {q["position"]: q["rows_top_to_bottom"] for q in receipt["p3"]["figures"]}
assert sorted(figures) == list(range(1, 16))
assert all(len(v) == 4 and set(v) <= {1, 2} for v in figures.values())

# This positional interpretation is declared, not supplied by native arrows.
mother_positions = [8, 7, 6, 5]
daughter_positions = [4, 3, 2, 1]
pair_rules = [(8, 7, 12), (6, 5, 11), (4, 3, 10), (2, 1, 9),
              (12, 11, 15), (10, 9, 13), (15, 13, 14)]
checks = []
for row, position in enumerate(daughter_positions):
    expected = [figures[p][row] for p in mother_positions]
    checks.append({"operation": "transpose", "mother_row": row + 1,
                   "inputs": mother_positions, "output": position,
                   "expected": expected, "observed": figures[position],
                   "equal": expected == figures[position]})
for left, right, output in pair_rules:
    expected = [1 if a != b else 2 for a, b in zip(figures[left], figures[right])]
    checks.append({"operation": "parity", "inputs": [left, right], "output": output,
                   "expected": expected, "observed": figures[output],
                   "equal": expected == figures[output]})
assert all(q["equal"] for q in checks), "SOURCE_EXAMPLE_MISMATCH_NO_READING_REPAIR"
result = {
    "status": "ALL_11_CANDIDATE_RULE_RELATIONS_MATCH_FROZEN_SOURCE_READING",
    "source_receipt_sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
    "checks": checks,
    "source_uncertainty": "B flags the bottom-right position15 lower border overlap. Its reading is unchanged; checks involving it remain conditional on that provisional reading.",
    "scope": "One complete early source diagram is consistent with the previously proposed transpose/parity algorithm under the declared physical slot mapping. This does not establish that all medieval prose rules, named figures or intended slot ordering are fully collated; no manuscript target or meaning.",
}
print(json.dumps(result, indent=2))
