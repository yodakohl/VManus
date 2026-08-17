#!/usr/bin/env python3
"""Independent artifact validator for GDT182."""

from __future__ import annotations

import csv
import hashlib
import itertools
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rows(name: str) -> list[dict[str, str]]:
    with (ROOT / name).open(encoding="utf-8") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    checks: list[str] = []
    result = json.loads((ROOT / "gdt182_result.json").read_text())
    predicates = rows("gdt182_predicates.tsv")
    pairs = rows("gdt182_decoder_pairs.tsv")
    shared = rows("gdt182_shared_predicates.tsv")
    null = rows("gdt182_permutation_null.tsv")
    counter = rows("gdt182_counterexamples.tsv")

    assert len(predicates) == 99
    assert sum(row["register"] == "N1" for row in predicates) == 57
    assert sum(row["register"] == "D1" for row in predicates) == 42
    checks.append("predicate_counts")
    assert len(pairs) == 5
    assert sum(row["register"] == "N1" for row in pairs) == 3
    assert sum(row["register"] == "D1" for row in pairs) == 2
    assert sum(int(row["selected_mask_pair_in_gdt179"]) for row in pairs) == 2
    checks.append("decoder_pair_counts")
    assert len(shared) == 7
    equal = [row["predicate"] for row in shared if row["same_mask"] == "1"]
    assert equal == ["END1:y", "HAS1:y"]
    checks.append("shared_axis_aliases")

    assert len(null) == 24
    assert {row["D1_position_permutation"] for row in null} == {"".join(map(str,p)) for p in itertools.permutations(range(4))}
    any_count = sum(int(row["any_common_literal_equal_mask"]) for row in null)
    y_count = sum(int(row["end1_y_equal_mask"]) for row in null)
    assert (any_count, y_count) == (10,4)
    assert abs(float(result["exact_null"]["search_adjusted_p"]) - 10/24) < 1e-12
    assert abs(float(result["exact_null"]["end1_y_descriptive_p"]) - 4/24) < 1e-12
    checks.append("exact_null")
    assert len(counter) == 6
    checks.append("counterexamples")

    for name, digest in result["inputs"].items():
        assert sha(ROOT / name) == digest
        checks.append(f"input:{name}")
    for name, digest in result["outputs"].items():
        assert sha(ROOT / name) == digest
        checks.append(f"output:{name}")
    for name, digest in result["documents"].items():
        assert sha(ROOT / name) == digest
        checks.append(f"document:{name}")
    assert sha(ROOT / "run_gdt182_f57_decoder_multiplicity.py") == result["implementation"]
    checks.append("implementation")
    assert not result["f84r_accessed"]
    checks.append("f84r_seal")

    validation = {"experiment":result["experiment"],"status":"PASS","checks":checks,"checks_passed":len(checks),"result_sha256":sha(ROOT / "gdt182_result.json")}
    (ROOT / "gdt182_validation.json").write_text(json.dumps(validation, sort_keys=True, indent=2) + "\n")
    print(f"PASS {len(checks)}/{len(checks)}")


if __name__ == "__main__":
    main()
