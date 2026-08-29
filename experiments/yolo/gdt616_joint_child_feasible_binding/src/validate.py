#!/usr/bin/env python3
"""Validate the prospective GDT616 registration without opening later data."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from prepare import OUT as REGISTERED_PATH
from prepare import build, canonical_bytes


ROOT = Path(__file__).resolve().parents[4]
EXP = ROOT / "experiments/yolo/gdt616_joint_child_feasible_binding"
OUTPUT = EXP / "artifacts/REGISTERED_VALIDATION.json"


def sha256(path: Path) -> str:
    value = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            value.update(block)
    return value.hexdigest()


def write_json(path: Path, value: dict) -> None:
    payload = json.dumps(value, indent=2, sort_keys=True) + "\n"
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(payload, encoding="utf-8")
    temporary.replace(path)


def main() -> int:
    checks: list[dict[str, object]] = []

    def check(name: str, condition: bool, detail: object = "") -> None:
        checks.append({"check": name, "pass": bool(condition), "detail": str(detail)})
        if not condition:
            raise AssertionError(f"{name}: {detail}")

    manifest = json.loads((EXP / "experiment.json").read_text(encoding="utf-8"))
    expected = build()
    registered = json.loads(REGISTERED_PATH.read_text(encoding="utf-8"))
    train_path = ROOT / registered["train_substrings"]["path"]
    train = set(train_path.read_text(encoding="ascii").splitlines())

    check("experiment_id", manifest.get("experiment_id") == "GDT616")
    check("registered_status", manifest.get("status") == "REGISTERED_UNSCORED")
    check("sealed_f84", manifest.get("sealed_data", {}).get("f84") == "FORBIDDEN")
    check("sealed_f84r", manifest.get("sealed_data", {}).get("f84r") == "FORBIDDEN")
    check("registration_schema", registered.get("schema") == "gdt616-joint-child-feasible-binding-registration-v1")
    check("registration_byte_exact", REGISTERED_PATH.read_bytes() == canonical_bytes(expected))
    check("merge_count", registered["inventory"]["merge_count"] == 64)
    check("merge_rank_count", len(registered["inventory"]["merge_rank_order"]) == 64)
    check("primitive_count", len(registered["inventory"]["primitive_order"]) == 34)
    check("paid_count", len(registered["inventory"]["paid_output_deck"]) == 8)
    check(
        "paid_roles_4_plus_4",
        sum(row["role"] == "short_card" for row in registered["inventory"]["paid_output_deck"]) == 4
        and sum(row["role"] == "macro_core" for row in registered["inventory"]["paid_output_deck"]) == 4,
    )
    check("train_substring_count", len(train) == 28101)
    check("train_substring_hash", sha256(train_path) == registered["train_substrings"]["sha256"])
    check(
        "paid_outputs_train_exposed",
        all(row["output"] in train for row in registered["inventory"]["paid_output_deck"]),
    )
    equations = registered["recursive_equations"]
    check("child_equation", equations["merge_child"] == "child(m)=eff(left(m))||eff(right(m))")
    check("effective_equation", equations["merge_effective"] == "eff(m)=paid_output(Z[m]) if Z[m]!=NONE else child(m)")
    check("actual_paid_eight", registered["variables"]["actual_paid_locations"] == 8)
    check("no_relaxed_core_hit", registered["variables"]["relaxed_core_hit_variables"] == "FORBIDDEN")
    stage_a = registered["stage_a_fail_fast_hard_constraints"]
    check("all_child_spans_hard", any("child(m) is nonempty" in row for row in stage_a))
    check("paid_child_inequality_hard", any("paid output differs" in row for row in stage_a))
    check("qok_macro_hard", any("rank 7 qok" in row for row in stage_a))
    selection = registered["stage_a_selection"]
    check("stage_a_sat_freezes_nothing", selection["sat_freezes_mapping_or_paid_assignment"] is False)
    check("stage_b_full_domain", selection["stage_b_domain"] == "the complete Stage-A-feasible X+Z space")
    check("raw_support_forbidden", "raw train-substring support count" in selection["forbidden_objectives"])
    check("stage_b_exact_optimum", registered["stage_b_integrated_w0"]["exact_optimality_required"] is True)
    check("three_world_commit", registered["three_world_rule"]["commit"] == "one hash-bound bundle before held or lm_confirm access")
    access = registered["partition_access"]
    check("target_forbidden", access["voynich_target"] == "FORBIDDEN_THROUGHOUT_GDT616")
    check("f84_forbidden", access["f84"] == access["f84r"] == "FORBIDDEN")
    check("held_deferred", access["synthetic_held"].startswith("open exactly once after"))
    check("lm_confirm_deferred", access["lm_confirm"].startswith("open only after"))
    excluded = registered["gdt615_import_policy"]["excluded"]
    check("gdt615_mapping_excluded", "GDT615 Stage-0 selected mapping" in excluded)
    check("gdt615_commit_excluded", "GDT615 mapping commit" in excluded)
    check("direct_input_hashes", all(sha256(ROOT / row["path"]) == row["sha256"] for row in registered["direct_input_hashes"]))
    check("unknown_not_pass", registered["limits"]["unknown_or_timeout_can_pass"] is False)
    check("worker_limit", registered["limits"]["workers_maximum"] == 32)
    check("time_limit", registered["limits"]["wall_clock_seconds_maximum"] == 43200)
    for name in ["PREREGISTRATION.md", "METHOD.md", "README.md", "artifacts/README.md"]:
        check(f"no_todo_{name}", "TODO" not in (EXP / name).read_text(encoding="utf-8"))

    result = {
        "schema": "gdt616-registration-validation-v1",
        "status": "PASS",
        "checks_total": len(checks),
        "checks_passed": sum(bool(row["pass"]) for row in checks),
        "checks": checks,
        "registered_search_sha256": sha256(REGISTERED_PATH),
        "held_or_lm_confirm_opened": False,
        "voynich_target_opened": False,
        "f84_or_f84r_opened": False,
    }
    write_json(OUTPUT, result)
    print(f"GDT616_REGISTRATION_VALIDATION_PASS {result['checks_passed']}/{result['checks_total']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
