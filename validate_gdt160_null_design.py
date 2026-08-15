#!/usr/bin/env python3
"""Independent integrity checks for the frozen GDT160 null design."""

from __future__ import annotations

import gzip
import hashlib
import json
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parent
DESIGN = ROOT / "gdt160_null_design.json"
METHOD = ROOT / "GDT160_COMPATIBILITY_PAIRING_NULL_METHOD.md"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    design = json.loads(DESIGN.read_text(encoding="utf-8"))
    checks: list[tuple[str, bool]] = []

    def check(name: str, value: bool) -> None:
        checks.append((name, bool(value)))

    check("schema", design["schema"] == "GDT160_COMPATIBILITY_PAIRING_NULL_DESIGN_V1")
    check("frozen", design["status"] == "FROZEN_BEFORE_NULL_SCORING")
    check("worlds", design["worlds"] == 1024)
    check("seed", design["seed"] == 1600032026)
    check("three_nulls", design["nulls"] == [
        "RIGHT_LABEL_SWITCH_LENGTH_EXACT",
        "LEFT_LABEL_SWITCH_LENGTH_EXACT",
        "RIGHT_LABEL_SWITCH_RECURRENCE_STRICT",
    ])
    for name, expected in design["inputs"].items():
        check("hash_" + name, sha(ROOT / name) == expected)

    with gzip.open(ROOT / "gdt003_structural_fingerprint_corpora.json.gz", "rt", encoding="utf-8") as handle:
        old = json.load(handle)["records"]
    with gzip.open(ROOT / "gdt159_diplomatic_corpora.json.gz", "rt", encoding="utf-8") as handle:
        new = json.load(handle)["records"]
    counts = Counter(str(row["corpus_id"]) for row in old + new)
    check("target_12000", counts[design["target"]] == 12000)
    check("comparators_exact", set(design["comparators"]) == {row["corpus_id"] for row in new})
    check("comparators_nonempty", all(counts[name] > 0 for name in design["comparators"]))
    target = [row for row in old if row["corpus_id"] == design["target"]]
    check("target_12_folds", len({row["fold_id"] for row in target}) == 12)
    provenance = json.loads((ROOT / "gdt003_structural_fingerprint_source_provenance.json").read_text(encoding="utf-8"))
    target_source = next(row for row in provenance["sources"] if row["corpus_id"] == design["target"])
    check("target_source_explicitly_excludes_f84r", target_source["f84r_retained_or_sampled"] is False)
    check("all_seal_flags_false", all(value is False for value in design["f84r"].values()))
    text = METHOD.read_text(encoding="utf-8")
    check("claim_ceiling", "does not establish linguistic morphology" in text)
    check("incidence_disclosure", "incidence-graph null" in text)
    check("exact_thresholds", "at least three host triplets" in text)

    failed = [name for name, ok in checks if not ok]
    result = {
        "schema": "GDT160_NULL_DESIGN_VALIDATION_V1",
        "status": "PASS" if not failed else "FAIL",
        "checks_passed": sum(ok for _, ok in checks),
        "checks_total": len(checks),
        "failed": failed,
        "checks": [{"check": name, "pass": ok} for name, ok in checks],
        "design_sha256": sha(DESIGN),
        "method_sha256": sha(METHOD),
    }
    (ROOT / "gdt160_null_design_validation.json").write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    if failed:
        raise SystemExit("FAIL " + ",".join(failed))
    print(f"PASS {result['checks_passed']}/{result['checks_total']}")


if __name__ == "__main__":
    main()
