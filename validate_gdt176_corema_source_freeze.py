#!/usr/bin/env python3
"""Independent integrity checks for the tracked GDT176 external source freeze."""
from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter
from pathlib import Path


def rows(path: str) -> list[dict[str, str]]:
    with Path(path).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def sha(path: str) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def content_hash(obj: dict[str, object]) -> str:
    clean = dict(obj)
    clean.pop("content_hash", None)
    return hashlib.sha256(json.dumps(clean, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def main() -> None:
    result = json.loads(Path("gdt176_source_freeze.json").read_text())
    manifest = rows("gdt176_corema_collection_manifest.tsv")
    recipes = rows("gdt176_corema_recipe_inventory.tsv")
    roles = rows("gdt176_corema_role_oracle.tsv")
    checks: list[tuple[str, bool]] = []
    checks.append(("status", result["status"] == "EXTERNAL_ROLE_CALIBRATION_SOURCE_FROZEN"))
    checks.append(("six_collections", [r["collection_id"] for r in manifest] == ["b4", "b6", "br1", "bs1", "gr1", "w1"]))
    checks.append(("counts", (len(recipes), len(roles)) == (result["recipe_count"], result["role_element_count"])))
    checks.append(("collection_counts", Counter(r["collection_id"] for r in recipes) == Counter({r["collection_id"]: int(r["recipe_count"]) for r in manifest})))
    checks.append(("role_counts", Counter(r["role"] for r in roles) == Counter(result["role_counts"])))
    recipe_keys = {(r["collection_id"], r["recipe_id"]) for r in recipes}
    checks.append(("role_recipe_join", all((r["collection_id"], r["recipe_id"]) in recipe_keys for r in roles)))
    checks.append(("positive_ordinals", all(int(r["recipe_ordinal"]) > 0 and int(r["element_ordinal"]) > 0 for r in roles)))
    checks.append(("relative_positions", all(0 < float(r["relative_element_position"]) <= 1 for r in roles)))
    checks.append(("source_thresholds", all(int(r["recipe_count"]) >= 30 and int(r["instruction_count"]) >= 30 for r in manifest)))
    checks.append(("output_hashes", all(sha(name) == digest for name, digest in result["outputs"].items())))
    checks.append(("content_hash", content_hash(result) == result["content_hash"]))
    checks.append(("no_voynich", not result["voynich_scored"] and not result["f84r_accessed"]))
    failed = [name for name, ok in checks if not ok]
    validation = {
        "experiment": "GDT176_COREMA_ROLE_SOURCE_FREEZE",
        "status": "PASS" if not failed else "FAIL",
        "checks_passed": sum(ok for _, ok in checks),
        "checks_total": len(checks),
        "failed": failed,
        "result_sha256": sha("gdt176_source_freeze.json"),
    }
    Path("gdt176_source_freeze_validation.json").write_text(json.dumps(validation, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"{validation['status']} {validation['checks_passed']}/{validation['checks_total']}")
    if failed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
