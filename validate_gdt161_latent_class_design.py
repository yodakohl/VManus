#!/usr/bin/env python3
"""Independent integrity checks for the frozen GDT161 design."""

from __future__ import annotations

import gzip
import hashlib
import json
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parent
DESIGN = ROOT / "gdt161_latent_class_design.json"
METHOD = ROOT / "GDT161_LATENT_OPERATION_CLASS_METHOD.md"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    d = json.loads(DESIGN.read_text(encoding="utf-8"))
    checks: list[tuple[str, bool]] = []

    def check(name: str, value: bool) -> None:
        checks.append((name, bool(value)))

    check("schema", d["schema"] == "GDT161_LATENT_OPERATION_CLASS_DESIGN_V1")
    check("frozen", d["status"] == "FROZEN_BEFORE_LATENT_CLASS_SCORING")
    check("k_grid", d["k_grid"] == [1, 2, 4, 8, 16, 32])
    check("five_pair_folds", d["pair_cell_folds"] == 5)
    check("five_node_folds", d["operation_folds_per_side"] == 5)
    check("worlds", d["top20_null_worlds"] == 1024)
    for name, expected in d["inputs"].items():
        check("hash_" + name, sha(ROOT / name) == expected)
    with gzip.open(ROOT / "gdt003_structural_fingerprint_corpora.json.gz", "rt", encoding="utf-8") as handle:
        old = json.load(handle)["records"]
    with gzip.open(ROOT / "gdt159_diplomatic_corpora.json.gz", "rt", encoding="utf-8") as handle:
        new = json.load(handle)["records"]
    counts = Counter(str(row["corpus_id"]) for row in old + new)
    check("target_12000", counts[d["target"]] == 12000)
    check("target_12_folds", len({row["fold_id"] for row in old if row["corpus_id"] == d["target"]}) == 12)
    check("comparators_exact", set(d["comparators"]) == {row["corpus_id"] for row in new})
    check("forbids_operation_literal", "operation_literal" in d["forbidden_model_inputs"])
    check("forbids_glyph_identity", "EVA_or_display_glyph_identity" in d["forbidden_model_inputs"])
    check("all_seal_flags_false", all(value is False for value in d["f84r"].values()))
    text = METHOD.read_text(encoding="utf-8")
    check("both_unseen_defined", "both endpoint operations unseen" in text)
    check("top20_loo_null", "leave-one-world-out mean" in text)
    check("claim_ceiling", "cannot establish linguistic morphology" in text)
    failed = [name for name, ok in checks if not ok]
    result = {
        "schema": "GDT161_LATENT_CLASS_DESIGN_VALIDATION_V1",
        "status": "PASS" if not failed else "FAIL",
        "checks_passed": sum(ok for _, ok in checks),
        "checks_total": len(checks),
        "failed": failed,
        "checks": [{"check": name, "pass": ok} for name, ok in checks],
        "design_sha256": sha(DESIGN),
        "method_sha256": sha(METHOD),
    }
    (ROOT / "gdt161_latent_class_design_validation.json").write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    if failed:
        raise SystemExit("FAIL " + ",".join(failed))
    print(f"PASS {result['checks_passed']}/{result['checks_total']}")


if __name__ == "__main__":
    main()
