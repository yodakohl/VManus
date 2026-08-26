#!/usr/bin/env python3
"""Validate the GDT449 context-robust neighbour deck."""

from __future__ import annotations

import csv
import json
import re
import subprocess
from collections import Counter
from pathlib import Path


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
BASE = ROOT / "experiments/yolo/gdt449_context_robust_neighbor_deck"
OUT = BASE / "artifacts"
GDT448 = ROOT / "experiments/yolo/gdt448_context_conditioned_neighbor_replay/artifacts"


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def expected_class(row: dict[str, str]) -> str:
    green = int(row["green_context_count"])
    amber = int(row["amber_context_count"])
    stop = int(row["stop_context_count"])
    if stop == 0 and amber == 0:
        return "OBSERVED_CONTEXT_ALL_GREEN"
    if stop == 0:
        return "OBSERVED_CONTEXT_ALL_READABLE_WITH_AMBER"
    if green + amber == 0:
        return "OBSERVED_CONTEXT_ALL_STOP"
    return "OBSERVED_CONTEXT_MIXED_READ_STOP"


def main() -> int:
    tracked = [
        OUT / "gdt449_deletion_edge_robustness.tsv",
        OUT / "gdt449_adjacent_swap_edge_robustness.tsv",
        OUT / "gdt449_same_class_substitution_edge_robustness.tsv",
        OUT / "gdt449_target_context_robustness.tsv",
        OUT / "gdt449_mutation_operator_summary.tsv",
        OUT / "gdt449_context_failure_deck.tsv",
        OUT / "gdt449_result.json",
    ]
    before = {path: path.read_bytes() for path in tracked}
    subprocess.run(["python3", str(BASE / "src/run.py")], cwd=ROOT, check=True, capture_output=True, text=True)
    after = {path: path.read_bytes() for path in tracked}

    replay = [
        row
        for path in sorted(GDT448.glob("gdt448_context_neighbor_replay_part*.tsv"))
        for row in read_tsv(path)
    ]
    edges = [row for path in tracked[:3] for row in read_tsv(path)]
    targets = read_tsv(tracked[3])
    operators = read_tsv(tracked[4])
    failures = read_tsv(tracked[5])
    result = json.loads(tracked[6].read_text(encoding="utf-8"))

    edge_classes = Counter(row["observed_context_robustness"] for row in edges)
    target_classes = Counter(row["observed_context_robustness"] for row in targets)
    family_classes = Counter((row["mutation_family"], row["observed_context_robustness"]) for row in edges)
    mixed_edge_ids = {row["neighbor_id"] for row in edges if row["observed_context_robustness"] == "OBSERVED_CONTEXT_MIXED_READ_STOP"}
    mixed_targets = {row["target_recipe"] for row in targets if row["observed_context_robustness"] == "OBSERVED_CONTEXT_MIXED_READ_STOP"}
    output_text = "\n".join(path.read_text(encoding="utf-8") for path in tracked)

    checks = {
        "source_replay_61878_unique": len(replay) == len({row["replay_id"] for row in replay}) == 61878,
        "edge_deck_25576_unique": len(edges) == len({row["neighbor_id"] for row in edges}) == 25576,
        "edge_context_counts_cover_replay": sum(int(row["sampled_context_count"]) for row in edges) == 61878,
        "edge_weight_counts_cover_source_weight": sum(int(row["sampled_occurrence_weight"]) for row in edges) == 65746,
        "edge_decision_counts_internal": all(int(row["green_context_count"]) + int(row["amber_context_count"]) + int(row["stop_context_count"]) == int(row["sampled_context_count"]) for row in edges),
        "edge_weight_counts_internal": all(int(row["green_occurrence_weight"]) + int(row["amber_occurrence_weight"]) + int(row["stop_occurrence_weight"]) == int(row["sampled_occurrence_weight"]) for row in edges),
        "edge_classes_21970_694_10_2902": edge_classes == {"OBSERVED_CONTEXT_ALL_GREEN": 21970, "OBSERVED_CONTEXT_ALL_READABLE_WITH_AMBER": 694, "OBSERVED_CONTEXT_MIXED_READ_STOP": 10, "OBSERVED_CONTEXT_ALL_STOP": 2902},
        "edge_class_logic_exact": all(row["observed_context_robustness"] == expected_class(row) for row in edges),
        "edge_family_classes_exact": family_classes == {
            ("ATOM_DELETION", "OBSERVED_CONTEXT_ALL_GREEN"): 4492,
            ("ATOM_DELETION", "OBSERVED_CONTEXT_ALL_READABLE_WITH_AMBER"): 35,
            ("ATOM_DELETION", "OBSERVED_CONTEXT_MIXED_READ_STOP"): 3,
            ("ATOM_DELETION", "OBSERVED_CONTEXT_ALL_STOP"): 82,
            ("ADJACENT_SWAP", "OBSERVED_CONTEXT_ALL_GREEN"): 3128,
            ("ADJACENT_SWAP", "OBSERVED_CONTEXT_ALL_READABLE_WITH_AMBER"): 55,
            ("ADJACENT_SWAP", "OBSERVED_CONTEXT_ALL_STOP"): 161,
            ("SAME_CLASS_SUBSTITUTION", "OBSERVED_CONTEXT_ALL_GREEN"): 14350,
            ("SAME_CLASS_SUBSTITUTION", "OBSERVED_CONTEXT_ALL_READABLE_WITH_AMBER"): 604,
            ("SAME_CLASS_SUBSTITUTION", "OBSERVED_CONTEXT_MIXED_READ_STOP"): 7,
            ("SAME_CLASS_SUBSTITUTION", "OBSERVED_CONTEXT_ALL_STOP"): 2659,
        },
        "mixed_edge_ids_exact": mixed_edge_ids == {"G447-N08437", "G447-N16029", "G447-N16794", "G447-N19129", "G447-N19159", "G447-N19230", "G447-N19348", "G447-N19405", "G447-N19516", "G447-N25791"},
        "mixed_edges_only_known_context_gaps": all(set(row["stop_factor_rules"].split("|")) <= {"CLOSE:NO_ACTIVE_ACTION", "FOCUS:CHD<-EEE", "FOCUS:R<-EEE"} for row in edges if row["neighbor_id"] in mixed_edge_ids),
        "targets_18381_unique": len(targets) == len({row["target_recipe"] for row in targets}) == 18381,
        "target_unique_contexts_61878": sum(int(row["unique_sampled_context_count"]) for row in targets) == 61878,
        "target_classes_15467_532_10_2372": target_classes == {"OBSERVED_CONTEXT_ALL_GREEN": 15467, "OBSERVED_CONTEXT_ALL_READABLE_WITH_AMBER": 532, "OBSERVED_CONTEXT_MIXED_READ_STOP": 10, "OBSERVED_CONTEXT_ALL_STOP": 2372},
        "target_class_logic_exact": all(row["observed_context_robustness"] == expected_class(row) for row in targets),
        "mixed_targets_exact": mixed_targets == {"D_ADDR+EEE+Y", "E+DY", "EE+DY", "EEE+Y", "OT+EEE+AIIN", "OT+EEE+DY", "OT+EEE+O", "OT+EEE+OR", "OT+EEE+Y", "OT+O+DY"},
        "all_target_identity_routes_single": all(row["target_identity_route"].startswith("IDENTITY_") for row in targets),
        "operators_641_unique": len(operators) == len({(row["mutation_family"], row["source_atom_or_pair"], row["target_atom_or_pair"], row["substitution_class"]) for row in operators}) == 641,
        "operator_edges_cover_25576": sum(int(row["neighbor_edge_count"]) for row in operators) == 25576,
        "operator_class_counts_cover_edges": all(int(row["all_green_edge_count"]) + int(row["all_readable_with_amber_edge_count"]) + int(row["mixed_read_stop_edge_count"]) + int(row["all_stop_edge_count"]) == int(row["neighbor_edge_count"]) for row in operators),
        "failure_deck_98_unique": len(failures) == len({(row["mutation_family"], row["blocked_factor_rule"]) for row in failures}) == 98,
        "failure_deck_all_stop": all(row["instruction"] == "STOP_AND_PRESERVE_STATE" for row in failures),
        "instructions_never_promote_identity": all(row["identity_is_not_inferred_from_robustness"] == "YES" and row["occurrence_is_not_predicted_from_robustness"] == "YES" for row in edges + targets),
        "result_status_exact": result["status"] == "CONTEXT_ROBUSTNESS_DECK_SEPARATES_STABLE_AND_CONTEXT_DEPENDENT_NEIGHBORS",
        "result_counts_exact": result["source_replay_case_count"] == 61878 and result["eligible_neighbor_edge_count"] == 25576 and result["unique_target_recipe_count"] == 18381 and result["mutation_operator_count"] == 641 and result["failure_rule_family_count"] == 98,
        "result_robust_counts_exact": result["edge_robustness_counts"] == dict(sorted(edge_classes.items())) and result["target_robustness_counts"] == dict(sorted(target_classes.items())) and result["edge_all_sampled_contexts_readable_count"] == 22664 and result["target_all_sampled_contexts_readable_count"] == 15999,
        "result_no_expansion": result["target_context_decision_disagreement_count"] == result["identity_promotions"] == result["meaning_revisions"] == result["surface_predictions"] == result["occurrence_predictions"] == result["new_pages"] == 0,
        "no_forbidden_folio_token": re.search(r"(?i)(?<![a-z0-9])f84(?:r|v)?(?![a-z0-9])", output_text) is None,
        "deterministic_rebuild": before == after,
    }
    failed = [name for name, passed in checks.items() if not passed]
    validation = {
        "status": "PASS" if not failed else "FAIL",
        "check_count": len(checks),
        "failure_count": len(failed),
        "failed_checks": failed,
        "checks": checks,
    }
    (OUT / "gdt449_validation.json").write_text(json.dumps(validation, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(validation, ensure_ascii=False, indent=2))
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
