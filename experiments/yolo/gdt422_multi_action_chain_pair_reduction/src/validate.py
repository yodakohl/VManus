#!/usr/bin/env python3
"""Validate GDT422 long-chain reduction."""

from __future__ import annotations

import csv
import json
import subprocess
from pathlib import Path


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
BASE = ROOT / "experiments/yolo/gdt422_multi_action_chain_pair_reduction"
OUT = BASE / "artifacts"


def read_tsv(name: str) -> list[dict[str, str]]:
    with (OUT / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> int:
    tracked = [
        OUT / "gdt422_110_long_action_chain_inventory.tsv",
        OUT / "gdt422_168_long_chain_occurrences.tsv",
        OUT / "gdt422_11_pair_gap_adjudications.tsv",
        OUT / "gdt422_3_chain_length_summary.tsv",
        OUT / "LONG_ACTION_CHAIN_WORKSHOP_RULES.md",
        OUT / "gdt422_result.json",
    ]
    before = {path: path.read_bytes() for path in tracked}
    subprocess.run(["python3", str(BASE / "src/run.py")], cwd=ROOT, check=True, capture_output=True, text=True)
    after = {path: path.read_bytes() for path in tracked}

    chains = read_tsv("gdt422_110_long_action_chain_inventory.tsv")
    occurrences = read_tsv("gdt422_168_long_chain_occurrences.tsv")
    gaps = read_tsv("gdt422_11_pair_gap_adjudications.tsv")
    lengths = read_tsv("gdt422_3_chain_length_summary.tsv")
    result = json.loads((OUT / "gdt422_result.json").read_text(encoding="utf-8"))

    repair_counts = {rule: sum(row["repair_rule"] == rule for row in gaps) for rule in {row["repair_rule"] for row in gaps}}
    checks = {
        "chain_recipes_110": len(chains) == 110,
        "chain_occurrences_168": len(occurrences) == 168,
        "chain_recipe_keys_unique": len({row["component_recipe"] for row in chains}) == 110,
        "occurrence_ids_unique": len({row["global_running_event_id"] for row in occurrences}) == 168,
        "length_rows_3": len(lengths) == 3 and {row["action_count"] for row in lengths} == {"3", "4", "5"},
        "length_type_distribution": {row["action_count"]: int(row["recipe_type_count"]) for row in lengths} == {"3": 98, "4": 11, "5": 1},
        "length_event_distribution": {row["action_count"]: int(row["event_count"]) for row in lengths} == {"3": 156, "4": 11, "5": 1},
        "fully_pair_covered_99": sum(row["reduction_status"] == "ALL_ADJACENT_PAIRS_ATTESTED" for row in chains) == 99,
        "repaired_11": sum(row["reduction_status"] != "ALL_ADJACENT_PAIRS_ATTESTED" for row in chains) == 11,
        "gaps_11": len(gaps) == 11,
        "repair_distribution": repair_counts == {
            "PEER_ACTION_CHUNK_BREAK": 2,
            "REPEATED_ACTION_SCOPE": 2,
            "R_POSITIONAL_TOPOLOGY_NOT_ORDINARY_PAIR": 2,
            "VISIBLE_SLOT_BOUNDARY_SPLITS_CHAIN": 5,
        },
        "no_irreducible_chain_card": all(row["new_chain_card_required"] == "NO" for row in chains) and all(row["irreducible_new_chain_card"] == "NO" for row in gaps),
        "all_occurrences_in_inventory": {row["component_recipe"] for row in occurrences} <= {row["component_recipe"] for row in chains},
        "no_forbidden_page": all("f84" not in path.read_text(encoding="utf-8").lower() for path in tracked),
        "no_new_pages": result["new_pages"] == 0,
        "no_dictionary_revisions": result["dictionary_revisions"] == 0,
        "deterministic_rebuild": before == after,
    }
    failed = [name for name, passed in checks.items() if not passed]
    validation = {
        "status": "PASS" if not failed else "FAIL",
        "check_count": len(checks),
        "failure_count": len(failed),
        "checks": checks,
    }
    (OUT / "gdt422_validation.json").write_text(json.dumps(validation, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(validation, ensure_ascii=False, indent=2))
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
