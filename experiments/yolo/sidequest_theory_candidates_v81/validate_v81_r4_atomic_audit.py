#!/usr/bin/env python3
"""Validate the bounded R4 V81 source-first audit."""

from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter
from pathlib import Path


HERE = Path(__file__).resolve().parent


def rows(name: str) -> list[dict[str, str]]:
    with (HERE / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    checks: dict[str, bool] = {}
    target = json.loads((HERE / "V81_TARGET_FREEZE.json").read_text(encoding="utf-8"))
    source_freeze = json.loads((HERE / "V81_R4_SOURCE_FREEZE.json").read_text(encoding="utf-8"))
    build = json.loads((HERE / "V81_R4_BUILD_SUMMARY.json").read_text(encoding="utf-8"))
    decisions = rows("V81_R4_30_CARD_DECISIONS.tsv")
    occurrences = rows("V81_R4_FULL_217_OCCURRENCE_AUDIT.tsv")
    statements = rows("V81_R4_94_STATEMENT_REVISIONS.tsv")
    manifest = rows("V81_TARGET_MANIFEST.tsv")

    checks["source_was_frozen_first"] = (
        source_freeze["status"] == "FROZEN_BEFORE_V81_TARGET_MANIFEST"
        and source_freeze["target_manifest_opened"] is False
    )
    checks["target_freeze_pass"] = target["status"] == "PASS__FROZEN_AFTER_FOUR_SOURCE_FIRST_FREEZES"
    checks["target_counts"] = len(manifest) == len(decisions) == 30
    checks["occurrence_count"] = len(occurrences) == 217
    checks["statement_count"] = len(statements) == 94
    checks["target_ids_exact"] = {r["anonymous_target_id"] for r in manifest} == {r["anonymous_target_id"] for r in decisions}
    checks["occurrences_complete"] = Counter(r["anonymous_target_id"] for r in occurrences) == Counter(
        {r["anonymous_target_id"]: int(r["visible_occurrences"]) for r in manifest}
    )
    checks["all_source_rows_checked"] = all(r["source_entries_checked"] == "Papa|et|con|quo" for r in decisions)
    checks["atomic_words_short"] = all(
        r["atomic_german_candidate"] in {"NONE", "UND", "DORTHIN", "WODURCH"}
        and len(r["atomic_german_candidate"].split()) <= 3
        for r in decisions
    )
    checks["only_source_licensed_candidates"] = all(
        r["best_source_entry"] in {"NONE", "et", "quo"} for r in decisions
    )
    checks["one_role_provisional"] = sum("PROVISIONAL_PROMOTION" in r["role_decision"] for r in decisions) == 1
    checks["no_central_promotion"] = all(r["central_status"] == "UNADJUDICATED_ROLE_OUTPUT" for r in decisions)
    checks["full_occurrence_no_surface"] = all(r["surface_or_component_used"] == "FALSE" for r in occurrences)
    checks["decision_no_surface"] = all(r["surface_or_component_used"] == "FALSE" for r in decisions)
    checks["fixed_pages"] = {r["page"] for r in occurrences} <= {"f10r", "f11r", "f55v", "f56r", "f81v", "f82r", "f83r"}
    checks["sealed_absent"] = all(
        not row["page"].lower().startswith("f84") for row in occurrences + statements
    )
    checks["build_pass"] = build["status"] == "PASS" and build["counts"]["central_promotions"] == 0
    checks["bindings_current"] = all(
        sha256(HERE / name) == digest
        for name, digest in build["bindings"].items()
        if name not in {"source_freeze", "source_inventory", "target_freeze"}
    )

    result = {
        "schema": "SIDEQUEST_V81_R4_ATOMIC_AUDIT_VALIDATION_V1",
        "status": "PASS" if all(checks.values()) else "FAIL",
        "checks": checks,
        "passed": sum(checks.values()),
        "total": len(checks),
        "counts": build["counts"],
        "candidate": build["candidate"],
        "strongest_rival": build["strongest_rival"],
        "seals": build["seals"],
    }
    (HERE / "V81_R4_VALIDATION.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(result["status"], f"{result['passed']}/{result['total']}")
    if result["status"] != "PASS":
        for key, value in checks.items():
            if not value:
                print("FAIL", key)
        raise SystemExit(1)


if __name__ == "__main__":
    main()
