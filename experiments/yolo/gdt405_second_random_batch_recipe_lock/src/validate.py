#!/usr/bin/env python3
"""Validate the prospective GDT405 recipe and parser lock."""

from __future__ import annotations

import csv
import hashlib
import json
import subprocess
from collections import defaultdict
from pathlib import Path


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
HERE = Path(__file__).resolve().parent.parent
OUT = HERE / "artifacts"
RUN = HERE / "src/run.py"
G404 = ROOT / "experiments/yolo/gdt404_random_four_page_factorized_admission/artifacts"
FILES = [
    OUT / "gdt405_426_locked_surface_dictionary.tsv",
    OUT / "gdt405_46_locked_atom_dictionary.tsv",
    OUT / "gdt405_49_amber_microform_lock.tsv",
    OUT / "gdt405_31_locked_parser_factors.tsv",
    OUT / "gdt405_second_batch_slots.tsv",
    OUT / "gdt405_second_batch_protocol.tsv",
    OUT / "gdt405_result.json",
]


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    checks: list[dict[str, object]] = []

    def check(name: str, condition: bool, detail: object) -> None:
        checks.append({"check": name, "pass": bool(condition), "detail": detail})

    subprocess.run(["python3", str(RUN)], cwd=ROOT, check=True, capture_output=True, text=True)
    first = {path.name: sha256(path) for path in FILES}
    subprocess.run(["python3", str(RUN)], cwd=ROOT, check=True, capture_output=True, text=True)
    second = {path.name: sha256(path) for path in FILES}
    check("deterministic_rebuild", first == second, len(FILES))
    check("all_outputs_exist", all(path.is_file() for path in FILES), len(FILES))

    dictionary = read_tsv(FILES[0])
    atoms = read_tsv(FILES[1])
    amber = read_tsv(FILES[2])
    axes = read_tsv(FILES[3])
    slots = read_tsv(FILES[4])
    protocol = read_tsv(FILES[5])
    result = json.loads(FILES[6].read_text(encoding="utf-8"))
    events = read_tsv(G404 / "gdt404_688_event_first_pass.tsv")
    core_source = read_tsv(G404 / "gdt404_core_transfer_summary.tsv")

    by_surface: dict[str, list[dict[str, str]]] = defaultdict(list)
    for event in events:
        by_surface[event["surface"]].append(event)
    check("surface_dictionary_count", len(dictionary) == 426, len(dictionary))
    check("surface_lock_ids", [row["lock_id"] for row in dictionary] == [f"G405-W{i:04d}" for i in range(1, 427)], dictionary[-1]["lock_id"])
    check("surface_inventory_exact", {row["surface"] for row in dictionary} == set(by_surface), len(by_surface))
    check("surface_recipes_exact", all(row["locked_recipe"] == by_surface[row["surface"]][0]["visible_recipe"] for row in dictionary), len(dictionary))
    check("surface_recipe_determinism", all(len({event["visible_recipe"] for event in selected}) == 1 for selected in by_surface.values()), len(by_surface))
    check("surface_counts_exact", all(int(row["gdt404_event_count"]) == len(by_surface[row["surface"]]) for row in dictionary), sum(int(row["gdt404_event_count"]) for row in dictionary))
    check("surface_event_sum", sum(int(row["gdt404_event_count"]) for row in dictionary) == 688, sum(int(row["gdt404_event_count"]) for row in dictionary))
    check("amber_dictionary_count", sum(row["amber_boundary"] == "YES" for row in dictionary) == 49, sum(row["amber_boundary"] == "YES" for row in dictionary))
    check("nonamber_changes_forbidden", all(row["allowed_change"] == "NONE" for row in dictionary if row["amber_boundary"] == "NO"), 377)
    check("all_core_retuning_forbidden", all("CORE_RETUNE" in row["forbidden_change"] for row in dictionary), len(dictionary))

    check("atom_dictionary_count", len(atoms) == 46, len(atoms))
    check("atom_inventory_exact", {row["atom"] for row in atoms} == {row["atom"] for row in core_source}, len(atoms))
    core_value = {row["atom"]: row["working_value_de"] for row in core_source}
    check("atom_values_byte_locked", all(row["locked_working_value_de"] == core_value[row["atom"]] for row in atoms), len(atoms))
    check("atom_retuning_forbidden", all(row["retuning_allowed"] == "NO" for row in atoms), len(atoms))

    check("amber_lock_count", len(amber) == 49, len(amber))
    check("amber_surface_match", {row["surface"] for row in amber} == {row["surface"] for row in dictionary if row["amber_boundary"] == "YES"}, len(amber))
    locked_recipe = {row["surface"]: row["locked_recipe"] for row in dictionary}
    check("amber_primary_recipe_locked", all(row["primary_locked_recipe"] == locked_recipe[row["surface"]] for row in amber), len(amber))
    check("amber_no_new_atom_gate", all("NEW_ATOM" in row["failure_gate"] for row in amber), len(amber))

    check("axis_lock_count", len(axes) == 31, len(axes))
    check("axis_partition", {row["axis"] for row in axes} == {"SCOPE_SELECTOR", "ATTACHMENT_GEOMETRY", "ACTION_HEAD", "R_TOPOLOGY", "DUPLICATE_MODE"}, sorted({row["axis"] for row in axes}))
    check("axis_new_values_forbidden", all(row["new_value_allowed"] == "NO" for row in axes), len(axes))
    check("slot_count", len(slots) == 4 and all(row["release_status"] == "UNRELEASED" for row in slots), len(slots))
    check("protocol_count", len(protocol) == 12, len(protocol))
    check("protocol_has_hard_stops", {row["operation"] for row in protocol} >= {"STOP_ON_BOUNDARY", "STOP_ON_RETUNE", "MAX_LOOKAHEAD_ONE"}, sorted({row["operation"] for row in protocol}))

    check("result_status", result["status"] == "SECOND_RANDOM_BATCH_LOCK_READY", result["status"])
    check("result_counts", [result["locked_surface_count"], result["locked_atom_count"], result["locked_parser_factor_count"], result["amber_microform_count"]] == [426, 46, 31, 49], [result["locked_surface_count"], result["locked_atom_count"], result["locked_parser_factor_count"], result["amber_microform_count"]])
    input_hashes_ok = all((ROOT / path).is_file() and sha256(ROOT / path) == digest for path, digest in result["input_hashes"].items())
    check("input_hashes_bound", input_hashes_ok, len(result["input_hashes"]))
    text = "\n".join(path.read_text(encoding="utf-8") for path in FILES)
    check("no_sealed_page_token", "f84" not in text.lower(), "0 expected")
    check("no_private_absolute_path", str(ROOT) not in text, "0 expected")

    failed = [row for row in checks if not row["pass"]]
    validation = {
        "experiment_id": "GDT405",
        "status": "PASS" if not failed else "FAIL",
        "check_count": len(checks),
        "passed_count": len(checks) - len(failed),
        "failed_count": len(failed),
        "checks": checks,
        "deterministic_hashes": second,
    }
    (OUT / "gdt405_validation.json").write_text(
        json.dumps(validation, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps({key: validation[key] for key in ("status", "check_count", "passed_count", "failed_count")}, sort_keys=True))
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
