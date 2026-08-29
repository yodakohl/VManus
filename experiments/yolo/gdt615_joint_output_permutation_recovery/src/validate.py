#!/usr/bin/env python3
"""Registration plus published Stage-0 audit for GDT615 (no held reveal)."""

from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter
from pathlib import Path

from z3 import Bool, Or, PbLe, Solver, sat


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
EXP = ROOT / "experiments/yolo/gdt615_joint_output_permutation_recovery"
ART = EXP / "artifacts"


def digest(path: Path) -> str:
    value = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            value.update(block)
    return value.hexdigest()


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def minimum_cover(
    names: list[str], failed: list[str], descendants: dict[str, set[str]]
) -> int:
    variables = {name: Bool(f"registration_hit_{rank:02d}") for rank, name in enumerate(names, 1)}
    for limit in range(len(names) + 1):
        solver = Solver()
        for name in failed:
            solver.add(Or(*(variables[node] for node in descendants[name])))
        solver.add(PbLe([(variables[name], 1) for name in names], limit))
        if solver.check() == sat:
            return limit
    raise AssertionError("finite cover unexpectedly infeasible")


def main() -> int:
    manifest = json.loads((EXP / "experiment.json").read_text(encoding="utf-8"))
    registered = json.loads((ART / "REGISTERED_SEARCH.json").read_text(encoding="utf-8"))
    checks: list[dict[str, object]] = []

    def check(name: str, condition: bool, detail: object = "") -> None:
        checks.append({"check": name, "pass": bool(condition), "detail": str(detail)})
        if not condition:
            raise AssertionError(f"{name}: {detail}")

    check("experiment_id", manifest["experiment_id"] == "GDT615")
    check(
        "status",
        manifest["status"]
        in {
            "REGISTERED_UNSCORED",
            "STAGE0_MAPPING_CERTIFICATE_PASS__STAGE1_NOT_RUN",
            "MAPPING_BOUND_PASS__FULL_WORLD_INFEASIBLE",
        },
    )
    check("sealed_f84", manifest["sealed_data"]["f84"] == "FORBIDDEN")
    check("sealed_f84r", manifest["sealed_data"]["f84r"] == "FORBIDDEN")
    check("no_held_stage0_mount", not registered["partition_access"]["stage0_and_stage1_processes_have_readable_held_mount"])
    check("no_lmb_early_mount", not registered["partition_access"]["stage0_through_stage2_processes_have_readable_lm_confirm_mount"])
    check("no_fallback", registered["search"]["adaptive_fallback"] == "FORBIDDEN")
    check("no_incumbent_pass", not registered["search"]["heuristic_incumbent_can_pass"])

    manifest_hashes = {row["path"]: row["sha256"] for row in manifest["inputs"]}
    for row in registered["registered_inputs"]:
        check(f"manifest_input_{Path(row['path']).name}", manifest_hashes.get(row["path"]) == row["sha256"], row["path"])
        # Held and LM-confirm are hash-bound prospectively but intentionally not
        # opened by this registration validator.
        if row["path"].endswith(("synthetic_held.txt", "lm_confirm.txt")):
            continue
        check(f"input_hash_{Path(row['path']).name}", digest(ROOT / row["path"]) == row["sha256"], row["path"])

    primitive_roles = {row["primitive_id"]: row["role"] for row in registered["primitive_role_assignment"]}
    check("primitive_count", len(primitive_roles) == 34)
    check("primitive_ids_unique", len(primitive_roles) == len(registered["primitive_role_assignment"]))
    role_counts = Counter(primitive_roles.values())
    deck = registered["primitive_output_deck"]
    check("role_sets_match", set(role_counts) == set(deck))
    check("role_deck_counts", all(role_counts[role] == len(cards) for role, cards in deck.items()), role_counts)
    card_ids = [card["card_id"] for cards in deck.values() for card in cards]
    check("card_ids_unique", len(card_ids) == len(set(card_ids)) == 34)
    check("single_null_output", sum(card["output"] == "" for cards in deck.values() for card in cards) == 1)
    paid = registered["paid_output_deck"]
    check("paid_count", len(paid) == 8)
    check("paid_roles_4_plus_4", Counter(row["role"] for row in paid) == {"short_card": 4, "macro_core": 4})

    tree_path = ROOT / "experiments/yolo/gdt608_compositional_stem_orientation/artifacts/merge_tree.tsv"
    tree = read_tsv(tree_path)
    check("merge_count", len(tree) == 64)
    check("merge_ranks", [int(row["rank"]) for row in tree] == list(range(1, 65)))
    leaves: dict[str, list[str]] = {primitive: [primitive] for primitive in primitive_roles}
    descendants: dict[str, set[str]] = {primitive: set() for primitive in primitive_roles}
    known = set(primitive_roles)
    role_min = {role: min(len(card["output"]) for card in cards) for role, cards in deck.items()}
    role_max = {role: max(len(card["output"]) for card in cards) for role, cards in deck.items()}
    for row in tree:
        name, left, right = row["merged"], row["left"], row["right"]
        check(f"topological_children_{row['rank']}", left in known and right in known, f"{left} {right}")
        check(f"unique_merge_{row['rank']}", name not in known, name)
        leaves[name] = leaves[left] + leaves[right]
        descendants[name] = {name} | descendants[left] | descendants[right]
        check(f"leaf_sequence_{row['rank']}", leaves[name] == row["leaf_sequence"].split(), name)
        check(f"leaf_count_{row['rank']}", len(leaves[name]) == int(row["leaf_count"]), name)
        minimum_length = sum(role_min[primitive_roles[leaf]] for leaf in leaves[name])
        maximum_length = sum(role_max[primitive_roles[leaf]] for leaf in leaves[name])
        check(f"nonempty_render_{row['rank']}", minimum_length > 0, name)
        check(f"render_within_registered_substrings_{row['rank']}", maximum_length <= 12, maximum_length)
        known.add(name)

    train_path = ROOT / "experiments/yolo/gdt613_observation_complete_fst34_recovery/artifacts/reference_splits/synthetic_train.txt"
    train_words = train_path.read_text(encoding="ascii").splitlines()
    train_types = set(train_words)
    generated = {
        word[start : start + length]
        for word in train_types
        for length in range(1, min(12, len(word)) + 1)
        for start in range(len(word) - length + 1)
    }
    payload = ("\n".join(sorted(generated, key=lambda value: (len(value), value))) + "\n").encode("ascii")
    table_path = ROOT / registered["registered_train_substrings"]["path"]
    check("train_event_count", len(train_words) == registered["registered_train_substrings"]["source_event_count"])
    check("train_type_count", len(train_types) == registered["registered_train_substrings"]["source_distinct_type_count"])
    check("train_substring_count", len(generated) == registered["registered_train_substrings"]["distinct_substring_count"])
    check("train_substring_payload", table_path.read_bytes() == payload)
    check("train_substring_hash", digest(table_path) == registered["registered_train_substrings"]["sha256"])

    old_model = json.loads((ROOT / "experiments/yolo/gdt614_core_run_macro_recovery/artifacts/REGISTERED_MODEL.json").read_text(encoding="utf-8"))
    rendered = {row["primitive_id"]: row["output"] for row in old_model["primitive_cards"]}
    failed: list[str] = []
    for row in tree:
        name = row["merged"]
        rendered[name] = rendered[row["left"]] + rendered[row["right"]]
        if rendered[name] not in generated:
            failed.append(name)
    train_only_minimum = minimum_cover([row["merged"] for row in tree], failed, descendants)
    negative = registered["negative_control"]
    check("negative_control_supported", 64 - len(failed) == negative["gdt615_train_only_raw_supported_merge_count"])
    check("negative_control_minimum", train_only_minimum == negative["gdt615_train_only_expected_exact_minimum"])
    check("negative_control_still_fails", train_only_minimum > registered["search"]["stage0_core_hit_budget_maximum"])

    result = {
        "schema": "gdt615-registration-validation-v1",
        "status": "PASS",
        "held_or_lm_confirm_opened": False,
        "checks_total": len(checks),
        "checks_passed": sum(bool(row["pass"]) for row in checks),
        "checks": checks,
    }
    (ART / "REGISTERED_VALIDATION.json").write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(f"REGISTERED_VALIDATION_PASS {result['checks_passed']}/{result['checks_total']}")
    stage0_commit = ART / "stage0/STAGE0_MAPPING_COMMIT.json"
    if stage0_commit.is_file():
        from stage0_validate import main as validate_stage0

        status = validate_stage0([])
        if status:
            return status
        stage1_result = ART / "stage1/STAGE1_RESULT.json"
        if stage1_result.is_file():
            from stage1_validate import main as validate_stage1

            return validate_stage1([])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
