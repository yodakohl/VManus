#!/usr/bin/env python3
"""Independent checks for the GDT538 phrase-complete overlay."""

from __future__ import annotations

import csv
import hashlib
import importlib.util
import json
import subprocess
import sys
from collections import Counter
from pathlib import Path


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
BASE = ROOT / "experiments/yolo/gdt538_final_159_phrase_consistency_edition"
OUT = BASE / "artifacts"
SOURCE = (
    ROOT
    / "experiments/yolo/gdt537_seven_route_final_intake_supplement/artifacts"
    / "gdt537_159_final_surface_dictionary.tsv"
)
COMPONENTS = (
    ROOT
    / "experiments/yolo/gdt413_twenty_six_page_semantic_working_edition/artifacts"
    / "gdt413_46_component_working_dictionary.tsv"
)
DICTIONARY = OUT / "gdt538_159_complete_phrase_dictionary.tsv"
ATOMS = OUT / "gdt538_34_atom_phrase_lexicon.tsv"
TEMPLATES = OUT / "gdt538_phrase_template_summary.tsv"
SPECIAL = OUT / "gdt538_7_special_phrase_normalization.tsv"
DELTAS = OUT / "gdt538_one_atom_delta_audit.tsv"
BOOK = OUT / "GDT538_COMPLETE_159_WORKING_PHRASEBOOK.md"
RESULT = OUT / "gdt538_result.json"
VALIDATION = OUT / "gdt538_validation.json"
RUN = BASE / "src/run.py"
CLI = BASE / "src/phrase_surface.py"

PORTABLE = {
    "Y", "OK", "OL", "OT", "AL", "CH", "SH", "AR", "K", "AIIN", "S",
    "CHD", "OR", "L", "T", "AIN", "R", "P", "AIR",
}
LOCAL_ONLY = {"LOCAL_X", "LOCAL_C"}


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def one_edit(left: list[str], right: list[str]) -> tuple[str, str, str] | None:
    if abs(len(left) - len(right)) > 1:
        return None
    if len(left) == len(right):
        different = [i for i, (a, b) in enumerate(zip(left, right)) if a != b]
        if len(different) != 1:
            return None
        index = different[0]
        return "SUBSTITUTE", left[index], right[index]
    if len(left) > len(right):
        inverse = one_edit(right, left)
        if inverse is None:
            return None
        return "DELETE", inverse[2], "NONE"
    for index, atom in enumerate(right):
        if left == right[:index] + right[index + 1 :]:
            return "INSERT", "NONE", atom
    return None


def import_cli():
    spec = importlib.util.spec_from_file_location("gdt538_phrase_surface", CLI)
    if spec is None or spec.loader is None:
        raise RuntimeError("Cannot import GDT538 phrase reader")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main() -> int:
    source = read_tsv(SOURCE)
    rows = read_tsv(DICTIONARY)
    atom_rows = read_tsv(ATOMS)
    templates = read_tsv(TEMPLATES)
    special = read_tsv(SPECIAL)
    deltas = read_tsv(DELTAS)
    components = {row["atom"]: row for row in read_tsv(COMPONENTS)}
    result = json.loads(RESULT.read_text(encoding="utf-8"))
    checks: list[dict[str, object]] = []

    def check(name: str, condition: bool, detail: object) -> None:
        checks.append({"check": name, "passed": bool(condition), "detail": detail})

    source_by_surface = {row["surface"]: row for row in source}
    by_surface = {row["surface"]: row for row in rows}
    atom_by_name = {row["atom"]: row for row in atom_rows}
    used_atoms = {
        atom for row in rows for atom in row["final_working_recipe"].split("+")
    }

    check("source_row_count", len(source) == 159, len(source))
    check("output_row_count", len(rows) == 159, len(rows))
    check("surface_key_set", set(by_surface) == set(source_by_surface), len(by_surface))
    check("surface_keys_unique", len(by_surface) == len(rows), len(by_surface))
    check(
        "recipes_byte_preserved",
        all(
            row["final_working_recipe"]
            == source_by_surface[row["surface"]]["final_working_recipe"]
            for row in rows
        ),
        len(rows),
    )
    check(
        "literal_readings_byte_preserved",
        all(
            row["literal_reading_de"]
            == source_by_surface[row["surface"]]["literal_reading_de"]
            for row in rows
        ),
        len(rows),
    )
    check(
        "old_phrases_preserved",
        all(
            row["old_working_phrase_de"]
            == source_by_surface[row["surface"]]["working_phrase_de"]
            for row in rows
        ),
        len(rows),
    )
    check(
        "old_inherited_count",
        sum(row["old_working_phrase_de"] == "INHERITED" for row in rows) == 152,
        sum(row["old_working_phrase_de"] == "INHERITED" for row in rows),
    )
    check(
        "no_new_inherited_or_empty",
        all(
            row["canonical_workshop_phrase_de"]
            and row["canonical_workshop_phrase_de"] != "INHERITED"
            for row in rows
        ),
        len(rows),
    )
    check(
        "all_exact_recipe_roundtrips",
        all(row["exact_recipe_roundtrip"] == row["final_working_recipe"] for row in rows),
        len(rows),
    )
    check(
        "all_slots_marked_explicit",
        all(row["all_slots_explicit"] == "YES" for row in rows),
        len(rows),
    )
    check("atom_type_count", len(atom_rows) == 34, len(atom_rows))
    check("atom_inventory_exact", set(atom_by_name) == used_atoms, len(used_atoms))
    check("portable_inventory_count", len(used_atoms & PORTABLE) == 19, len(used_atoms & PORTABLE))
    check("local_only_inventory", LOCAL_ONLY <= used_atoms, sorted(LOCAL_ONLY & used_atoms))
    check(
        "portable_values_byte_locked",
        all(
            atom_by_name[atom]["fixed_value_de"] == components[atom]["working_value_de"]
            for atom in PORTABLE
        ),
        len(PORTABLE),
    )
    check(
        "portable_realizations_unbracketed",
        all("[" not in atom_by_name[atom]["controlled_realization_de"] for atom in PORTABLE),
        len(PORTABLE),
    )
    check(
        "nonportable_realizations_bracketed",
        all(
            atom_by_name[atom]["controlled_realization_de"].startswith("[")
            and atom_by_name[atom]["controlled_realization_de"].endswith("]")
            for atom in used_atoms - PORTABLE
        ),
        len(used_atoms - PORTABLE),
    )
    check(
        "controlled_realizations_unique",
        len({row["controlled_realization_de"] for row in atom_rows}) == len(atom_rows),
        len(atom_rows),
    )

    controlled_ok = 0
    atom_slot_count = 0
    for row in rows:
        atoms = row["final_working_recipe"].split("+")
        atom_slot_count += len(atoms)
        expected = " → ".join(atom_by_name[atom]["controlled_realization_de"] for atom in atoms) + "."
        controlled_ok += expected == row["controlled_order_reading_de"]
    check("controlled_chain_replay", controlled_ok == 159, controlled_ok)
    check("atom_slot_count", atom_slot_count == 640, atom_slot_count)
    check(
        "stored_atom_counts",
        all(int(row["atom_count"]) == len(row["final_working_recipe"].split("+")) for row in rows),
        len(rows),
    )
    check(
        "atom_frequency_replay",
        Counter(
            atom for row in rows for atom in row["final_working_recipe"].split("+")
        )
        == Counter({row["atom"]: int(row["recipe_occurrence_count"]) for row in atom_rows}),
        atom_slot_count,
    )

    check("template_class_count", len(templates) == 8, len(templates))
    check(
        "template_coverage",
        sum(int(row["surface_count"]) for row in templates) == 159,
        sum(int(row["surface_count"]) for row in templates),
    )
    observed_template_counts = Counter(row["phrase_template"] for row in rows)
    check(
        "template_counts_replay",
        observed_template_counts
        == Counter({row["phrase_template"]: int(row["surface_count"]) for row in templates}),
        dict(observed_template_counts),
    )

    check("special_route_count", len(special) == 7, len(special))
    check(
        "special_route_keys",
        {row["surface"] for row in special}
        == {row["surface"] for row in source if row["special_route"] == "YES"},
        sorted(row["surface"] for row in special),
    )
    y_conflicts = [row for row in special if row["old_y_verbalization_conflict"] == "YES"]
    check("special_y_conflict_count", len(y_conflicts) == 4, [row["surface"] for row in y_conflicts])
    check(
        "y_is_fixed_argument",
        components["Y"]["factor_family"] == "ARGUMENT"
        and components["Y"]["working_value_de"] == "POSTEN",
        {
            "factor_family": components["Y"]["factor_family"],
            "working_value_de": components["Y"]["working_value_de"],
        },
    )
    check(
        "special_recipes_unchanged",
        all(row["recipe_changed"] == "NO" and row["root_meaning_changed"] == "NO" for row in special),
        len(special),
    )

    expected_delta_keys: set[tuple[str, str, str, str, str]] = set()
    ordered_rows = list(rows)
    for left_index, left in enumerate(ordered_rows):
        for right in ordered_rows[left_index + 1 :]:
            edit = one_edit(
                left["final_working_recipe"].split("+"),
                right["final_working_recipe"].split("+"),
            )
            if edit is not None:
                expected_delta_keys.add((left["surface"], right["surface"], *edit))
    actual_delta_keys = {
        (
            row["left_surface"], row["right_surface"], row["edit_operation"],
            row["old_atom"], row["new_atom"],
        )
        for row in deltas
    }
    check("one_atom_pair_inventory", actual_delta_keys == expected_delta_keys, len(deltas))
    check("one_atom_pair_count", len(deltas) == 62, len(deltas))
    check(
        "one_atom_effect_labels",
        all(
            row["old_controlled_realization_de"]
            == (atom_by_name[row["old_atom"]]["controlled_realization_de"] if row["old_atom"] != "NONE" else "NONE")
            and row["new_controlled_realization_de"]
            == (atom_by_name[row["new_atom"]]["controlled_realization_de"] if row["new_atom"] != "NONE" else "NONE")
            for row in deltas
        ),
        len(deltas),
    )
    check(
        "one_atom_effects_explicit",
        all(
            row["all_unchanged_slots_byte_identical"] == "YES"
            and row["changed_slot_effect_explicit"] == "YES"
            for row in deltas
        ),
        len(deltas),
    )

    reader = import_cli()
    direct = [reader.exact_phrase_lookup(surface, "PROSE_STREAM", rows) for surface in by_surface]
    check("direct_reader_coverage", all(item is not None for item in direct), len(direct))
    check(
        "direct_reader_recipe_replay",
        all(item["final_recipe"] == by_surface[item["surface"]]["final_working_recipe"] for item in direct),
        len(direct),
    )
    check(
        "direct_reader_phrase_replay",
        all(
            item["canonical_workshop_phrase_de"]
            == by_surface[item["surface"]]["canonical_workshop_phrase_de"]
            for item in direct
        ),
        len(direct),
    )
    check(
        "local_domain_direct_stop",
        reader.exact_phrase_lookup("aiicthy", "LOCAL_RECORD", rows) is None,
        "aiicthy LOCAL_RECORD",
    )
    check(
        "unknown_surface_direct_stop",
        reader.exact_phrase_lookup("not_a_current_surface", "PROSE_STREAM", rows) is None,
        "not_a_current_surface",
    )

    cli_exact = subprocess.run(
        [sys.executable, str(CLI), "--surface", "aiicthy", "--domain", "PROSE_STREAM"],
        cwd=ROOT, check=False, capture_output=True, text=True,
    )
    cli_exact_json = json.loads(cli_exact.stdout)
    check(
        "cli_exact_phrase",
        cli_exact.returncode == 0
        and cli_exact_json["status"] == "GDT538_PHRASE_COMPLETE_PROSE_SURFACE_LOCK"
        and cli_exact_json["final_recipe"] == "AIIN+CH+T+Y",
        cli_exact_json,
    )
    cli_local = subprocess.run(
        [sys.executable, str(CLI), "--surface", "aiicthy", "--domain", "LOCAL_RECORD"],
        cwd=ROOT, check=False, capture_output=True, text=True,
    )
    cli_local_json = json.loads(cli_local.stdout)
    check(
        "cli_local_delegation",
        cli_local.returncode == 0
        and cli_local_json["status"] == "DELEGATED_TO_GDT537_FINAL_RECIPE_LAYER",
        cli_local_json["status"],
    )
    cli_old = subprocess.run(
        [sys.executable, str(CLI), "--surface", "aiin", "--domain", "PROSE_STREAM"],
        cwd=ROOT, check=False, capture_output=True, text=True,
    )
    cli_old_json = json.loads(cli_old.stdout)
    check(
        "cli_old_surface_delegation",
        cli_old.returncode == 0
        and cli_old_json["status"] == "DELEGATED_TO_GDT537_FINAL_RECIPE_LAYER",
        cli_old_json["status"],
    )

    artifact_paths = [DICTIONARY, ATOMS, TEMPLATES, SPECIAL, DELTAS, BOOK, RESULT]
    before = {path.name: digest(path) for path in artifact_paths}
    rerun = subprocess.run(
        [sys.executable, str(RUN)], cwd=ROOT, check=False, capture_output=True, text=True
    )
    after = {path.name: digest(path) for path in artifact_paths}
    check("generator_rerun_exit", rerun.returncode == 0, rerun.stderr or rerun.stdout)
    check("generator_byte_determinism", before == after, after)

    check("result_status", result["status"] == "PASS_ALL_159_HAVE_CANONICAL_PHRASES__Y_RESTORED_AS_ARGUMENT", result["status"])
    check("result_surface_count", result["surface_count"] == 159, result["surface_count"])
    check("result_atom_slot_count", result["atom_slot_count"] == 640, result["atom_slot_count"])
    check("result_no_recipe_change", result["recipe_changes"] == 0, result["recipe_changes"])
    check("result_no_root_change", result["root_meaning_changes"] == 0, result["root_meaning_changes"])
    check("result_no_new_pages", result["new_pages"] == 0, result["new_pages"])

    failed = [row for row in checks if not row["passed"]]
    validation = {
        "status": "PASS" if not failed else "FAIL",
        "check_count": len(checks),
        "passed_count": len(checks) - len(failed),
        "failed_count": len(failed),
        "checks": checks,
    }
    VALIDATION.write_text(
        json.dumps(validation, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(validation, ensure_ascii=False, indent=2))
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
