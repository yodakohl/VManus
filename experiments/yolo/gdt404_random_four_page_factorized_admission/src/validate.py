#!/usr/bin/env python3
"""Validate the complete GDT404 random-page admission release."""

from __future__ import annotations

import csv
import hashlib
import importlib.util
import json
import subprocess
from collections import Counter, defaultdict
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
PASS1026 = (
    ROOT
    / "experiments/yolo/sidequest_semantic_visible_allograph_resegmentation_one_thousand_twenty_sixth"
    / "PASS1026_3888_CORRECTED_EVENT_LEDGER.tsv"
)

REQUIRED = [
    OUT / "gdt404_95_guarded_source_lines.tsv",
    OUT / "gdt404_image_first_owner_manifest.tsv",
    OUT / "gdt404_random_selection.tsv",
    OUT / "gdt404_688_event_first_pass.tsv",
    OUT / "gdt404_211_new_surface_audit.tsv",
    OUT / "gdt404_one_edit_candidate_detail.tsv",
    OUT / "gdt404_statement_edition.tsv",
    OUT / "gdt404_factorized_attachments.tsv",
    OUT / "gdt404_amber_close_sensitivity.tsv",
    OUT / "gdt404_cross_page_surface_recurrence.tsv",
    OUT / "gdt404_core_transfer_summary.tsv",
    OUT / "gdt404_page_summary.tsv",
    OUT / "gdt404_admission_decisions.tsv",
    OUT / "gdt404_first_pass_summary.json",
    HERE / "FOUR_RANDOM_PAGES_READABLE_CORE_EDITION.md",
]


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_run_module():
    spec = importlib.util.spec_from_file_location("gdt404_run", RUN)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot import GDT404 builder")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main() -> int:
    checks: list[dict[str, object]] = []

    def check(name: str, condition: bool, detail: object) -> None:
        checks.append({"check": name, "pass": bool(condition), "detail": detail})

    subprocess.run(["python3", str(RUN)], cwd=ROOT, check=True, capture_output=True, text=True)
    first_hashes = {path.name: sha256(path) for path in REQUIRED}
    subprocess.run(["python3", str(RUN)], cwd=ROOT, check=True, capture_output=True, text=True)
    second_hashes = {path.name: sha256(path) for path in REQUIRED}
    check("deterministic_rebuild", first_hashes == second_hashes, len(first_hashes))
    check("required_outputs_exist", all(path.is_file() for path in REQUIRED), len(REQUIRED))

    module = load_run_module()
    source = read_tsv(OUT / "gdt404_95_guarded_source_lines.tsv")
    events = read_tsv(OUT / "gdt404_688_event_first_pass.tsv")
    novel = read_tsv(OUT / "gdt404_211_new_surface_audit.tsv")
    statements = read_tsv(OUT / "gdt404_statement_edition.tsv")
    attachments = read_tsv(OUT / "gdt404_factorized_attachments.tsv")
    sensitivity = read_tsv(OUT / "gdt404_amber_close_sensitivity.tsv")
    recurrence = read_tsv(OUT / "gdt404_cross_page_surface_recurrence.tsv")
    cores = read_tsv(OUT / "gdt404_core_transfer_summary.tsv")
    pages = read_tsv(OUT / "gdt404_page_summary.tsv")
    images = read_tsv(OUT / "gdt404_image_first_owner_manifest.tsv")
    decisions = read_tsv(OUT / "gdt404_admission_decisions.tsv")
    summary = json.loads((OUT / "gdt404_first_pass_summary.json").read_text(encoding="utf-8"))

    check("source_line_count", len(source) == 95, len(source))
    check("source_page_values", {row["page"] for row in source} == set(module.SELECTED_VALUES), sorted({row["page"] for row in source}))
    token_sum = sum(int(row["token_count"]) for row in source)
    check("source_token_count", token_sum == 688, token_sum)
    check("event_count", len(events) == 688, len(events))
    check("event_ids_contiguous", [row["event_id"] for row in events] == [f"G404-E{i:04d}" for i in range(1, 689)], events[-1]["event_id"])

    source_sequence = [
        (row["page"], row["locus"], ordinal, surface)
        for row in source
        for ordinal, surface in enumerate(row["eva_clean"].split(), 1)
    ]
    event_sequence = [
        (row["source_page_value"], row["locus"], int(row["card_ordinal_in_line"]), row["surface"])
        for row in events
    ]
    check("source_event_order_exact", source_sequence == event_sequence, len(event_sequence))
    check("unique_surface_count", len({row["surface"] for row in events}) == 426, len({row["surface"] for row in events}))

    recipes_by_surface: dict[str, set[str]] = defaultdict(set)
    for row in events:
        recipes_by_surface[row["surface"]].add(row["visible_recipe"])
    check("one_recipe_per_surface", all(len(values) == 1 for values in recipes_by_surface.values()), len(recipes_by_surface))
    check("all_recipes_nonempty", all(row["visible_recipe"] for row in events), sum(not row["visible_recipe"] for row in events))
    bad_atoms = sorted({atom for row in events for atom in row["visible_recipe"].split("+") if atom not in module.ATOM_VALUE})
    check("fixed_atom_inventory_only", not bad_atoms, bad_atoms)

    old_rows = read_tsv(PASS1026)
    old_recipe: dict[str, set[str]] = defaultdict(set)
    for row in old_rows:
        old_recipe[row["surface"]].add(row["pass1026_recipe"])
    old_recipe_one = {surface: next(iter(values)) for surface, values in old_recipe.items() if len(values) == 1}
    exact_rows = [row for row in events if row["surface_status"] == "EXACT_SURFACE_ONE_RECIPE"]
    check("exact_event_count", len(exact_rows) == 470, len(exact_rows))
    check("exact_surface_count", len({row["surface"] for row in exact_rows}) == 215, len({row["surface"] for row in exact_rows}))
    check("exact_recipes_unchanged", all(old_recipe_one[row["surface"]] == row["visible_recipe"] for row in exact_rows), len(exact_rows))

    status_counts = Counter(row["surface_status"] for row in events)
    check("new_event_partition", status_counts == Counter({"EXACT_SURFACE_ONE_RECIPE": 470, "NEW_VISIBLE_COMPOSITION": 169, "NEW_MICROFORM_OLD_FACTORS": 49}), dict(status_counts))
    novel_counts = Counter(row["selection_status"] for row in novel)
    check("new_surface_partition", len(novel) == 211 and novel_counts == Counter({"NEW_VISIBLE_COMPOSITION": 162, "NEW_MICROFORM_OLD_FACTORS": 49}), {"total": len(novel), **novel_counts})
    check("manual_inventory_exact", {row["surface"] for row in novel} == set(module.MANUAL_NEW_RECIPE), len(module.MANUAL_NEW_RECIPE))
    check("novel_recipe_matches_builder", all(row["selected_recipe"] == module.MANUAL_NEW_RECIPE[row["surface"]] for row in novel), len(novel))
    check("amber_set_exact", {row["surface"] for row in novel if row["selection_status"] == "NEW_MICROFORM_OLD_FACTORS"} == set(module.AMBIGUOUS_NEW), len(module.AMBIGUOUS_NEW))

    statement_events: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in events:
        statement_events[row["statement_id"]].append(row)
    check("statement_count", len(statements) == 88 and len(statement_events) == 88, {"table": len(statements), "event_groups": len(statement_events)})
    check("statement_ids_contiguous", [row["statement_id"] for row in statements] == [f"G404-S{i:03d}" for i in range(1, 89)], statements[-1]["statement_id"])
    statement_alignment = True
    statement_boundary_valid = True
    for statement in statements:
        selected = statement_events[statement["statement_id"]]
        statement_alignment &= (
            len(selected) == int(statement["event_count"])
            and " ".join(row["surface"] for row in selected) == statement["surface_sequence"]
            and [int(row["card_ordinal_in_statement"]) for row in selected] == list(range(1, len(selected) + 1))
        )
        statement_boundary_valid &= len({row["prose_block_id"] for row in selected}) == 1
        last_atoms = selected[-1]["visible_recipe"].split("+")
        if statement["end_mode"] == "LICENSED_DY_CLOSE":
            statement_boundary_valid &= last_atoms[-1] == "DY"
        else:
            statement_boundary_valid &= statement["end_mode"] == "PROSE_BLOCK_OPEN_END"
    check("statement_event_alignment", statement_alignment, sum(int(row["event_count"]) for row in statements))
    check("statement_boundaries_valid", statement_boundary_valid, Counter(row["end_mode"] for row in statements))
    check("statement_close_partition", Counter(row["end_mode"] for row in statements) == Counter({"LICENSED_DY_CLOSE": 78, "PROSE_BLOCK_OPEN_END": 10}), Counter(row["end_mode"] for row in statements))
    check("prose_block_count", len({row["prose_block_id"] for row in events}) == 13, len({row["prose_block_id"] for row in events}))

    expected_focus_keys: list[tuple[str, str, int]] = []
    for row in events:
        seen: Counter[str] = Counter()
        for atom in row["visible_recipe"].split("+"):
            if atom in module.FOCI:
                seen[atom] += 1
                expected_focus_keys.append((row["event_id"], atom, seen[atom]))
    attachment_keys = [
        (row["event_id"], row["focus_core"], int(row["focus_occurrence_ordinal"]))
        for row in attachments
    ]
    check("focus_attachment_count", len(attachments) == 677, len(attachments))
    check("focus_inventory_exact", attachment_keys == expected_focus_keys, len(attachment_keys))
    check("fixed_selector_set", {row["selector_rule"] for row in attachments} == module.FIXED_SELECTORS, sorted({row["selector_rule"] for row in attachments}))
    check("fixed_geometry_set", {row["attachment_geometry"] for row in attachments} == module.FIXED_GEOMETRIES, sorted({row["attachment_geometry"] for row in attachments}))
    check("fixed_head_set", {row["action_core"] for row in attachments} == module.FIXED_HEADS, sorted({row["action_core"] for row in attachments}))
    check("fixed_r_topologies", {row["r_topology"] for row in attachments} == module.FIXED_R_TOPOLOGIES, sorted({row["r_topology"] for row in attachments}))
    check("fixed_duplicate_modes", {row["duplicate_mode"] for row in attachments} == module.FIXED_DUPLICATE_MODES, sorted({row["duplicate_mode"] for row in attachments}))
    check("factorized_all_pass", all(row["factorized_result"] == "PASS_FIXED_FACTORS" for row in attachments), Counter(row["factorized_result"] for row in attachments))
    check("lookahead_at_most_one", max(int(row["lookahead_cards"]) for row in attachments) == 1 and all(int(row["lookahead_cards"]) <= 1 for row in attachments), max(int(row["lookahead_cards"]) for row in attachments))
    check("no_boundary_crossing", all(row["owner_boundary_crossed"] == "NO" and row["statement_boundary_crossed"] == "NO" for row in attachments), len(attachments))
    check("outside_register_support", all(row["selector_supported_outside_register"] == "YES" and row["head_supported_outside_register"] == "YES" for row in attachments), len(attachments))

    event_by_id = {row["event_id"]: row for row in events}
    target_valid = True
    for row in attachments:
        if row["action_core"] == "OWNER":
            target_valid &= row["selected_action_event_id"] == "OWNER"
            continue
        target = event_by_id.get(row["selected_action_event_id"])
        if target is None:
            target_valid = False
            continue
        target_valid &= target["statement_id"] == row["statement_id"]
        atom_ordinal = int(row["selected_action_atom_ordinal"])
        atoms = target["visible_recipe"].split("+")
        target_valid &= 1 <= atom_ordinal <= len(atoms) and atoms[atom_ordinal - 1] == row["action_core"]
    check("target_heads_visible_and_same_statement", target_valid, len(attachments))

    check("ambiguous_close_sensitivity_count", len(sensitivity) == 2, len(sensitivity))
    check("ambiguous_close_sensitivity_stays_fixed", all(row["merged_factorized_result"] == "PASS_FIXED_FACTORS" for row in sensitivity), len(sensitivity))
    check("cross_page_recurrence_count", len(recurrence) == 70, len(recurrence))
    new_recurrence = sum(row["surface_status"] != "EXACT_SURFACE_ONE_RECIPE" for row in recurrence)
    check("cross_page_new_recurrence_count", new_recurrence == 4, new_recurrence)
    check("cross_page_recipe_invariant", all(row["portable_recipe_result"] == "SAME_RECIPE_ACROSS_RANDOM_PAGES" for row in recurrence), len(recurrence))
    check("fixed_core_inventory_complete", len(cores) == 46 and {row["atom"] for row in cores} == set(module.ATOM_VALUE), len(cores))
    check("fixed_core_values_unchanged", all(row["working_value_de"] == module.ATOM_VALUE[row["atom"]] for row in cores), len(cores))

    expected_images = {
        "f1r": ("c0f11e98eb472063c812876a0dafec1e1344f0be92c7847e2e22e294b2253e17", "1116", "1536"),
        "f24v": ("e224cf1a478ea0f5cf044eb2473a00d6bf78d2d28cff44bcba65a187d8c3a091", "1141", "1536"),
        "f81r": ("968a949a435de9bd2d316c271e5a88f41dc56869ba0f2c0e131e09843a549d67", "1150", "1536"),
        "f95v": ("5513aca39cacafecf110e623f30c075ab492ac3ceecc316b684ac4a2bb5997db", "1246", "1536"),
    }
    image_actual = {row["physical_page"]: (row["sha256"], row["width"], row["height"]) for row in images}
    check("image_manifest_exact", image_actual == expected_images, image_actual)
    check("page_summary_count", len(pages) == 4 and sum(int(row["event_count"]) for row in pages) == 688 and sum(int(row["statement_count"]) for row in pages) == 88, {"pages": len(pages), "events": sum(int(row["event_count"]) for row in pages), "statements": sum(int(row["statement_count"]) for row in pages)})
    check("page_decisions_amber", all(row["page_decision"] == "AMBER" and row["factorized_failure_count"] == "0" for row in pages), [row["page_decision"] for row in pages])
    check("decision_red_zero", len(decisions) == 5 and decisions[-1]["event_or_attachment_count"] == "0", decisions[-1])
    readable = (HERE / "FOUR_RANDOM_PAGES_READABLE_CORE_EDITION.md").read_text(encoding="utf-8")
    check("readable_edition_all_statements", all(row["statement_id"] in readable for row in statements), len(statements))

    check("summary_batch_decision", summary["batch_decision"] == "PASS_WITH_AMBER_MICROFORMS" and summary["factorized_failure_count"] == 0, summary["batch_decision"])
    check("summary_core_counts", [summary["event_count"], summary["statement_count"], summary["focus_attachment_count"]] == [688, 88, 677], [summary["event_count"], summary["statement_count"], summary["focus_attachment_count"]])
    artifact_text = "\n".join(path.read_text(encoding="utf-8", errors="replace") for path in REQUIRED if path.suffix in {".tsv", ".json", ".md"})
    check("no_sealed_page_token_in_outputs", "f84" not in artifact_text.lower(), "0 expected")
    check("no_private_absolute_path", str(ROOT) not in artifact_text, "0 expected")

    failed = [row for row in checks if not row["pass"]]
    result = {
        "experiment_id": "GDT404",
        "status": "PASS" if not failed else "FAIL",
        "check_count": len(checks),
        "passed_count": len(checks) - len(failed),
        "failed_count": len(failed),
        "checks": checks,
        "deterministic_hashes": second_hashes,
    }
    (OUT / "gdt404_validation.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps({key: result[key] for key in ("status", "check_count", "passed_count", "failed_count")}, sort_keys=True))
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
