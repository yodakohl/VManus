#!/usr/bin/env python3
"""Independent retained-artifact checks for GDT195."""

import csv
import hashlib
import itertools
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
RESULT = ROOT / "gdt195_result.json"
VALIDATION = ROOT / "gdt195_validation.json"
FILES = [
    ROOT / "gdt195_source_manifest.tsv",
    ROOT / "gdt195_comparator_features.tsv",
    ROOT / "gdt195_homolog_comparison.tsv",
    ROOT / "gdt195_quality_cycle_null.tsv",
    ROOT / "gdt195_predictions.tsv",
    ROOT / "gdt195_counterexamples.tsv",
]
METHOD = ROOT / "GDT195_F77_READABLE_HOMOLOG_METHOD.md"
REPORT = ROOT / "GDT195_F77_READABLE_HOMOLOG_REPORT.md"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def admissible(sequence: tuple[int, ...], mask: tuple[int, ...]) -> bool:
    edges = []
    for left, right, emits in zip(sequence, sequence[1:], mask):
        if emits == 1:
            if (left - right) % 4 not in (1, 3):
                return False
            edges.append(tuple(sorted((left, right))))
        elif left != right:
            return False
    return len(edges) == 4 and set(edges) == {(0, 1), (1, 2), (2, 3), (0, 3)}


def main() -> None:
    result = json.loads(RESULT.read_text(encoding="utf-8"))
    manifest, features, comparison, nulls, predictions, counter = map(read, FILES)
    checks = []

    def ck(name: str, condition: bool) -> None:
        assert condition, name
        checks.append(name)

    ck("status", result["status"] == "ALCHEMICAL_SOURCE_FAMILY_PLAUSIBLE_EXACT_F77_HOMOLOG_NOT_FOUND")
    ck("posthoc_disclosed", result["target_exposure"] == "POSTHOC_SOURCE_FAMILY_AUDIT_OF_EXPOSED_GDT180_TARGET")
    ck("source_count", len(manifest) == 6)
    ck("source_ids_unique", len({x["source_id"] for x in manifest}) == 6)
    ck("authorities", all(x["authority"] in {"OFFICIAL_MANUSCRIPT_DESCRIPTION", "SCHOLARLY_ARTICLE", "OFFICIAL_MANUSCRIPT_CATALOGUE", "OFFICIAL_COLLECTION_CATALOGUE", "UNIVERSITY_MANUSCRIPT_EXHIBIT", "SCHOLARLY_MANUSCRIPT_CATALOGUE"} for x in manifest))
    ck("source_hashes", all(len(x["payload_sha256"]) == 64 for x in manifest))
    ck("facts", len(features) == 8 and all(x["support"] == "SUPPORTED" for x in features))
    ck("fact_sources", {x["source_id"] for x in features} <= {x["source_id"] for x in manifest})
    ck("comparators", len(comparison) == 6)
    ck("comparison_sources", {x["comparator_id"] for x in comparison} == {x["source_id"] for x in manifest})
    ck("exact_homolog_zero", sum(int(x["exact_f77_homolog"]) for x in comparison) == 0)
    ck("repeat_partial_one", sum(int(x["one_repeat_hold"]) for x in comparison) == 1)
    sequences = list(itertools.product(range(4), repeat=6))
    fixed = [s for s in sequences if admissible(s, (1, 1, 0, 1, 1))]
    movable = set()
    for hold in range(5):
        mask = tuple(0 if i == hold else 1 for i in range(5))
        movable.update(s for s in sequences if admissible(s, mask))
    ck("sequence_space", len(sequences) == 4096)
    ck("fixed_eight", len(fixed) == 8)
    ck("movable_forty", len(movable) == 40)
    stored_nulls = {x["metric"]: int(x["value"]) for x in nulls}
    ck("null_values", stored_nulls == {"ALL_SIX_STATE_STRINGS": 4096, "FIXED_OBSERVED_MASK_COMPLETE_CYCLE": 8, "MOVABLE_SINGLE_HOLD_COMPLETE_CYCLE": 40, "RETAINED_COMPARATOR_EXACT_HOMOLOGS": 0})
    ck("result_counts", result["counts"]["fixed_mask_complete_cycles"] == 8 and result["counts"]["movable_hold_complete_cycles"] == 40 and result["counts"]["exact_homologs"] == 0)
    ck("predictions", len(predictions) == 4 and predictions[-1]["status"] == "ACTIVE_REQUIREMENT")
    ck("counterexamples", len(counter) == 6)
    ck("algebraic_dependency", result["interpretation"]["four_element_coverage_independent_evidence"] is False)
    ck("no_translation", result["interpretation"]["f77_state_words_translated"] is False)
    ck("input_hashes", all(result["inputs"][name] == sha(ROOT / name) for name in result["inputs"]))
    ck("output_hashes", all(result["outputs"][p.name] == sha(p) for p in FILES))
    ck("document_hashes", result["documents"] == {METHOD.name: sha(METHOD), REPORT.name: sha(REPORT)})
    ck("implementation_hash", result["implementation"] == sha(ROOT / "run_gdt195_f77_readable_homolog.py"))
    ck("f84_false", result["f84_accessed"] is False)
    ck("no_f84_tabular_payload", all("f84" not in p.read_text(encoding="utf-8").lower() for p in FILES))
    validation = {
        "experiment": "GDT195_VALIDATION",
        "status": "PASS",
        "checks": len(checks),
        "check_names": checks,
        "result_sha256": sha(RESULT),
        "scope": "Independent combinatorial enumeration plus retained source/comparison/hash integrity; external statements remain source claims.",
    }
    VALIDATION.write_text(json.dumps(validation, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print("PASS", len(checks))


if __name__ == "__main__":
    main()
