#!/usr/bin/env python3
"""Independent reconstruction of SME001's complete-page target source."""

from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
SOURCE = HERE / "source_panel.tsv"
ANON = HERE / "anonymous_unit_binding.tsv"
MATRIX = HERE / "anonymous_paragraph_matrix.tsv"
BINDING = HERE / "target_source_binding.tsv"
CAPACITY = HERE / "target_source_capacity.json"
OUT = HERE / "target_source_validation.json"
REPORT = ROOT / "experiments/semantic_assumptions/results/sme001_target_source_validation.md"


def read(path):
    with path.open(encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh, delimiter="\t"))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def informative(rows, field, values, predicate=lambda row: True):
    pages = sorted({row["page"] for row in rows})
    return [page for page in pages if {row[field] for row in rows if row["page"] == page and row[field] in values and predicate(row)} == values]


def main():
    checks = []
    source = {(row["page"], row["star_ordinal"], row["locus"]): row for row in read(SOURCE)}
    anonymous = read(ANON)
    assert len(anonymous) == 170 and len([row for row in anonymous if row["page"] == "f106r"]) == 14
    checks.append("score_blind_full_page_drop")
    rebuilt = []
    for row in anonymous:
        if row["page"] == "f106r":
            continue
        src = source[(row["page"], row["star_ordinal"], row["locus"])]
        rebuilt.append({key: value for key, value in (
            ("unit_id", row["unit_id"]), ("page", row["page"]), ("physical_folio", row["physical_folio"]),
            ("star_ordinal", row["star_ordinal"]), ("locus", row["locus"]), ("rays", src["rays"]), ("tail", src["tail"]),
        )})
    assert len(rebuilt) == 156 and len({row["page"] for row in rebuilt}) == 12 and len({row["physical_folio"] for row in rebuilt}) == 7
    checks.append("target_source_cardinality")
    assert read(BINDING) == rebuilt
    checks.append("binding_exact_rows")
    matrix_ids = {row["unit_id"] for row in read(MATRIX)}
    assert {row["unit_id"] for row in rebuilt} <= matrix_ids
    assert len(matrix_ids) == 170
    checks.append("anonymous_matrix_key_coverage")

    ray = [row for row in rebuilt if row["rays"] in {"7", "8"}]
    assert len(ray) == 149 and Counter(row["rays"] for row in ray) == Counter({"7": 83, "8": 66})
    assert len(informative(rebuilt, "rays", {"7", "8"})) == 12
    checks.append("ray_capacity")
    tail = [row for row in rebuilt if row["tail"] in {"1", "2"}]
    assert len(tail) == 155 and Counter(row["tail"] for row in tail) == Counter({"1": 133, "2": 22})
    assert len(informative(rebuilt, "tail", {"1", "2"})) == 8
    checks.append("tail_capacity")

    maximum = {page: max(int(row["star_ordinal"]) for row in rebuilt if row["page"] == page) for page in {row["page"] for row in rebuilt}}
    strata = {
        "ODD": lambda row: int(row["star_ordinal"]) % 2 == 1,
        "EVEN": lambda row: int(row["star_ordinal"]) % 2 == 0,
        "EARLY": lambda row: int(row["star_ordinal"]) <= maximum[row["page"]] / 2,
        "LATE": lambda row: int(row["star_ordinal"]) > maximum[row["page"]] / 2,
    }
    expected_folios = {"rays": {"ODD": 7, "EVEN": 7, "EARLY": 6, "LATE": 7}, "tail": {"ODD": 5, "EVEN": 4, "EARLY": 4, "LATE": 5}}
    for field, values in (("rays", {"7", "8"}), ("tail", {"1", "2"})):
        for name, predicate in strata.items():
            pages = informative(rebuilt, field, values, predicate)
            assert len({page[:-1] for page in pages}) == expected_folios[field][name]
    checks.append("parity_and_ordinal_strata")

    cap = json.loads(CAPACITY.read_text(encoding="utf-8"))
    assert cap["binding_sha256"] == sha(BINDING)
    assert cap["input_hashes"] == {str(SOURCE.relative_to(ROOT)): sha(SOURCE), str(ANON.relative_to(ROOT)): sha(ANON), str(MATRIX.relative_to(ROOT)): sha(MATRIX)}
    checks.append("hash_bindings")
    sequences = {page: {field: "".join(row[field] for row in rebuilt if row["page"] == page) for field in ("rays", "tail")} for page in sorted({row["page"] for row in rebuilt})}
    assert cap["page_sequences"] == sequences
    checks.append("complete_sequences")
    assert cap["text_feature_values_accessed"] is False and cap["morphology_to_feature_join_performed"] is False
    checks.append("feature_join_absence")
    assert cap["target_result_absent"] is True and not (HERE / "TARGET_RESULT.json").exists()
    checks.append("target_absence")
    assert cap["claim_ceiling"] == "complete-page ray and tail sequence capacity only"
    checks.append("claim_ceiling")
    assert len(checks) == 12
    payload = {"experiment": "SME001", "status": "PASS_12_CHECK_TARGET_SOURCE_RECONSTRUCTION", "checks": checks, "binding_sha256": sha(BINDING), "target_absent": True}
    OUT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    REPORT.write_text("\n".join([
        "# SME001 target-source validation", "", "**PASS — 12/12 independent checks.**", "",
        "Nonimporting code reconstructs the full-page exclusion, all 156 separate morphology bindings, ray/tail capacities, parity and ordinal strata, complete page sequences, hashes, feature-join absence, target absence, and claim ceiling.", "",
        "This validates source capacity only and supplies no morphology association, meaning, lexeme, plaintext, language, or translation.",
    ]) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
