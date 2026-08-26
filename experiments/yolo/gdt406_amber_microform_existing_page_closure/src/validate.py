#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
import subprocess
from collections import Counter
from pathlib import Path


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
HERE = Path(__file__).resolve().parent.parent
OUT = HERE / "artifacts"


def rows(name: str) -> list[dict[str, str]]:
    with (OUT / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> int:
    subprocess.run(["python3", str(HERE / "src/run.py")], cwd=ROOT, check=True)
    audit = rows("gdt406_49_amber_package_audit.tsv")
    pairs = rows("gdt406_adjacent_package_evidence.tsv")
    candidates = rows("gdt406_candidate_recipe_pressure.tsv")
    clusters = rows("gdt406_amber_risk_clusters.tsv")
    tiers = rows("gdt406_package_support_tiers.tsv")
    result = json.loads((OUT / "gdt406_result.json").read_text(encoding="utf-8"))

    checks: dict[str, bool] = {
        "audit_49": len(audit) == 49,
        "unique_amber_ids": len({r["amber_id"] for r in audit}) == 49,
        "unique_surfaces": len({r["surface"] for r in audit}) == 49,
        "source_events_4576": result["source_events"] == 4576,
        "physical_pages_26": result["admitted_physical_pages"] == 26,
        "running_recipe_pages_24": result["running_recipe_pages"] == 24,
        "local_only_pages_declared": result["local_only_pages_excluded_from_recipe_support"] == ["f69v", "f70v"],
        "all_atoms_locked": all(r["all_atoms_locked"] == "YES" for r in audit),
        "no_promotions": all(r["promotion_status"] == "REMAINS_AMBER__NO_EXACT_RECURRENCE" for r in audit),
        "primary_lock_preserved": all(r["lock_action"] == "KEEP_GDT405_PRIMARY_RECIPE" for r in audit),
        "pair_row_sum": len(pairs) == sum(int(r["adjacent_pair_count"]) for r in audit),
        "candidate_primary_once": all(
            sum(c["candidate_kind"] == "LOCKED_PRIMARY" for c in candidates if c["amber_id"] == r["amber_id"]) == 1
            for r in audit
        ),
        "candidate_groups_complete": {c["amber_id"] for c in candidates} == {r["amber_id"] for r in audit},
        "tier_sum_49": sum(int(r["amber_surface_count"]) for r in tiers) == 49,
        "cluster_nonempty": bool(clusters),
        "no_forbidden_page": not any("f84" in "\t".join(r.values()).lower() for table in (audit, pairs, candidates) for r in table),
        "status_exact": result["status"] == "AMBER_RISK_STRATIFIED__NO_PROMOTIONS_WITHOUT_RECURRENCE",
    }
    tier_counter = Counter(r["package_support_tier"] for r in audit)
    checks["tier_table_matches"] = tier_counter == Counter({r["package_support_tier"]: int(r["amber_surface_count"]) for r in tiers})
    validation = {
        "status": "PASS" if all(checks.values()) else "FAIL",
        "checks": checks,
        "check_count": len(checks),
        "failure_count": sum(not value for value in checks.values()),
    }
    (OUT / "gdt406_validation.json").write_text(json.dumps(validation, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if not all(checks.values()):
        raise SystemExit(json.dumps(validation, indent=2))
    print(json.dumps(validation, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
