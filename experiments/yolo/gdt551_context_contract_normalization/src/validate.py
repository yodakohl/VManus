#!/usr/bin/env python3
"""Independent validation for GDT551 context-contract normalization."""

from __future__ import annotations

import csv
import hashlib
import json
import subprocess
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
EXP = ROOT / "experiments/yolo/gdt551_context_contract_normalization"
ART = EXP / "artifacts"
RUN = EXP / "src/run.py"

G540 = ROOT / "experiments/yolo/gdt540_target_surface_context_requirement_contract/artifacts"
G546 = ROOT / "experiments/yolo/gdt546_consolidated_fragment_reader/artifacts"
G548 = ROOT / "experiments/yolo/gdt548_unified_145_prose_reader/artifacts"
G549 = ROOT / "experiments/yolo/gdt549_default_queue_visible_peer_bridges/artifacts"
G550 = ROOT / "experiments/yolo/gdt550_recurrent_sequence_frame_bridges/artifacts"

CONTRACT_IN = G540 / "gdt540_145_surface_context_contract.tsv"
FRAGMENT_IN = G546 / "gdt546_81_consolidated_fragment_reader.tsv"
READER_IN = G548 / "gdt548_145_unified_prose_reader.tsv"
WARNING_IN = G549 / "gdt549_9_context_mismatch_peer_audit.tsv"
VISIBLE_IN = G549 / "gdt549_23_exact_visible_default_cards.tsv"
RESIDUAL_IN = G550 / "gdt550_9_residual_support_queue.tsv"

PROFILE = ART / "gdt551_145_contract_class_profile.tsv"
ANCHOR = ART / "gdt551_81_anchor_contract_audit.tsv"
DISJOINT = ART / "gdt551_12_disjoint_instance_mode_audit.tsv"
WARNING = ART / "gdt551_9_previous_context_warning_audit.tsv"
PROMOTED = ART / "gdt551_4_promoted_context_cards.tsv"
RESIDUAL = ART / "gdt551_5_residual_interface_queue.tsv"
SUMMARY = ART / "gdt551_context_normalization_summary.tsv"
BOOK = ART / "GDT551_CONTEXT_CONTRACT_BOOK.md"
RESULT = ART / "gdt551_result.json"
VALIDATION = ART / "gdt551_validation.json"

STATUS = (
    "PASS_ALL_12_INSTANCE_MODE_DISJOINTS_NORMALIZED__"
    "FOUR_CONTEXT_RESTS_CLOSED__FIVE_INTERFACES_REMAIN"
)
ACTION_ROOTS = {"OK", "CH", "SH", "K", "S", "CHD", "T", "R", "P"}
ARGUMENT_ROOTS = {"Y", "AIIN", "AIN", "OR"}
MODE_BY_FLAGS = {
    (False, False): "SELF_CONTAINED",
    (False, True): "REQUIRES_ACTIVE_ARGUMENT",
    (True, False): "REQUIRES_ACTIVE_ACTION",
    (True, True): "REQUIRES_ACTIVE_ACTION_AND_ARGUMENT",
}
MODE_ORDER = {
    "SELF_CONTAINED": 0,
    "REQUIRES_ACTIVE_ARGUMENT": 1,
    "REQUIRES_ACTIVE_ACTION": 2,
    "REQUIRES_ACTIVE_ACTION_AND_ARGUMENT": 3,
}
EXPECTED_DISJOINT = {
    "chady",
    "chap",
    "chckhedy",
    "chepos",
    "folchol",
    "kody",
    "qoekedy",
    "qokshd",
    "qoteeod",
    "saiis",
    "shokaiir",
    "tosheo",
}
EXPECTED_PROMOTED = {"folchol", "qoteeod", "saiis", "shokaiir"}
EXPECTED_RESIDUAL = {"aiicthy", "chap", "ofaram", "rotaiin", "shso"}


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def keyed(rows: list[dict[str, str]], field: str) -> dict[str, dict[str, str]]:
    result = {row[field]: row for row in rows}
    if len(result) != len(rows):
        raise RuntimeError(f"Duplicate {field}")
    return result


def slots(recipe: str) -> tuple[bool, bool]:
    atoms = recipe.split("+")
    return (
        any(atom in ACTION_ROOTS for atom in atoms),
        any(atom in ARGUMENT_ROOTS for atom in atoms),
    )


def signature(recipe: str) -> str:
    action, argument = slots(recipe)
    return (
        ("ACTION_VISIBLE" if action else "ACTION_OPEN")
        + "/"
        + ("ARGUMENT_VISIBLE" if argument else "ARGUMENT_OPEN")
    )


def allowed(recipe: str) -> set[str]:
    action, argument = slots(recipe)
    return {
        MODE_BY_FLAGS[(use_action, use_argument)]
        for use_action in ([False] if action else [False, True])
        for use_argument in ([False] if argument else [False, True])
    }


def modes(value: str) -> set[str]:
    return set() if value == "NONE" else set(value.split("|"))


def mode_string(values: set[str]) -> str:
    return "|".join(sorted(values, key=MODE_ORDER.__getitem__))


def relation(anchor: str, target: str) -> str:
    old = allowed(anchor)
    new = allowed(target)
    if old == new:
        return "IDENTICAL_SLOT_CONTRACT"
    if new < old:
        return "TARGET_CONTRACT_NARROWER_BY_VISIBLE_EXTENSION"
    if old < new:
        return "TARGET_CONTRACT_WIDER_BY_EXTENSION"
    if old & new:
        return "OVERLAPPING_SLOT_CONTRACTS"
    return "DISJOINT_SLOT_CONTRACTS"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    checks: list[dict[str, Any]] = []

    def check(name: str, passed: bool, detail: Any) -> None:
        checks.append({"check": name, "passed": bool(passed), "detail": detail})

    contracts = read_tsv(CONTRACT_IN)
    fragments = read_tsv(FRAGMENT_IN)
    reader_rows = read_tsv(READER_IN)
    source_warnings = read_tsv(WARNING_IN)
    visible_rows = read_tsv(VISIBLE_IN)
    source_residual = read_tsv(RESIDUAL_IN)
    check(
        "source_row_counts",
        [len(contracts), len(fragments), len(reader_rows), len(source_warnings), len(visible_rows), len(source_residual)]
        == [145, 81, 145, 9, 23, 9],
        [len(contracts), len(fragments), len(reader_rows), len(source_warnings), len(visible_rows), len(source_residual)],
    )

    contract_by_surface = keyed(contracts, "surface")
    fragment_by_surface = keyed(fragments, "surface")
    reader_by_surface = keyed(reader_rows, "surface")
    warning_by_surface = keyed(source_warnings, "surface")
    visible_by_surface = keyed(visible_rows, "surface")

    profiles = read_tsv(PROFILE)
    profile_by_signature = keyed(profiles, "contract_signature")
    expected_signatures = {
        "ACTION_VISIBLE/ARGUMENT_VISIBLE",
        "ACTION_VISIBLE/ARGUMENT_OPEN",
        "ACTION_OPEN/ARGUMENT_VISIBLE",
        "ACTION_OPEN/ARGUMENT_OPEN",
    }
    check("four_contract_classes", set(profile_by_signature) == expected_signatures, sorted(profile_by_signature))
    expected_profile: dict[str, dict[str, Any]] = defaultdict(lambda: {"count": 0, "modes": Counter()})
    for row in contracts:
        key = signature(row["final_recipe"])
        expected_profile[key]["count"] += 1
        for mode in modes(row["observed_requirement_modes"]):
            expected_profile[key]["modes"][mode] += 1
    profile_errors = []
    for key, expected in expected_profile.items():
        row = profile_by_signature[key]
        representative = {
            "ACTION_VISIBLE/ARGUMENT_VISIBLE": "CH+Y",
            "ACTION_VISIBLE/ARGUMENT_OPEN": "CH+E",
            "ACTION_OPEN/ARGUMENT_VISIBLE": "O+Y",
            "ACTION_OPEN/ARGUMENT_OPEN": "O+E",
        }[key]
        if (
            int(row["surface_count"]) != expected["count"]
            or row["allowed_observed_modes"] != mode_string(allowed(representative))
            or int(row["self_contained_surface_count"]) != expected["modes"]["SELF_CONTAINED"]
            or int(row["active_argument_surface_count"]) != expected["modes"]["REQUIRES_ACTIVE_ARGUMENT"]
            or int(row["active_action_surface_count"]) != expected["modes"]["REQUIRES_ACTIVE_ACTION"]
            or int(row["both_active_surface_count"]) != expected["modes"]["REQUIRES_ACTIVE_ACTION_AND_ARGUMENT"]
        ):
            profile_errors.append(key)
    check("profile_metrics_exact", not profile_errors, profile_errors)
    check("profile_surface_sum", sum(int(row["surface_count"]) for row in profiles) == 145, sum(int(row["surface_count"]) for row in profiles))

    anchors = read_tsv(ANCHOR)
    anchor_by_surface = keyed(anchors, "surface")
    check("anchor_card_set_exact", set(anchor_by_surface) == set(fragment_by_surface), len(anchor_by_surface))
    anchor_errors = []
    feasibility_errors = []
    preservation_errors = []
    for surface, source in fragment_by_surface.items():
        row = anchor_by_surface[surface]
        anchor_recipe = source["primary_anchor_recipe"]
        target_recipe = source["final_recipe"]
        if (
            row["primary_anchor_recipe"] != anchor_recipe
            or row["final_recipe"] != target_recipe
            or row["anchor_contract_signature"] != signature(anchor_recipe)
            or row["full_contract_signature"] != signature(target_recipe)
            or row["anchor_allowed_modes"] != mode_string(allowed(anchor_recipe))
            or row["full_allowed_modes"] != mode_string(allowed(target_recipe))
            or row["contract_relation"] != relation(anchor_recipe, target_recipe)
            or row["old_instance_mode_relation"] != source["primary_anchor_context_relation"]
        ):
            anchor_errors.append(surface)
        if not modes(row["old_anchor_modes"]) <= allowed(anchor_recipe) or not modes(row["target_modes"]) <= allowed(target_recipe):
            feasibility_errors.append(surface)
        if (
            row["neutral_component_reading_de"] != source["neutral_component_reading_de"]
            or row["known_contextual_readings_de"] != source["known_contextual_readings_de"]
            or target_recipe != reader_by_surface[surface]["final_recipe"]
        ):
            preservation_errors.append(surface)
    check("anchor_contract_reconstruction_exact", not anchor_errors, anchor_errors)
    check("all_81_anchor_and_target_modes_feasible", not feasibility_errors, feasibility_errors)
    check("all_81_recipes_and_meanings_preserved", not preservation_errors, preservation_errors)

    disjoint = read_tsv(DISJOINT)
    disjoint_by_surface = keyed(disjoint, "surface")
    expected_disjoint_from_source = {
        row["surface"]
        for row in fragments
        if row["primary_anchor_context_relation"] == "TARGET_MODE_SET_DISJOINT"
    }
    check("twelve_disjoint_source_cards", expected_disjoint_from_source == EXPECTED_DISJOINT, sorted(expected_disjoint_from_source))
    check("disjoint_output_set_exact", set(disjoint_by_surface) == EXPECTED_DISJOINT, sorted(disjoint_by_surface))
    relations = Counter(row["contract_relation"] for row in disjoint)
    check("eleven_disjoints_share_identical_contract", relations["IDENTICAL_SLOT_CONTRACT"] == 11, dict(relations))
    narrowed = {row["surface"] for row in disjoint if row["contract_relation"] == "TARGET_CONTRACT_NARROWER_BY_VISIBLE_EXTENSION"}
    check("kody_alone_fills_open_action_slot", narrowed == {"kody"}, sorted(narrowed))
    check("all_twelve_disjoints_normalized", all(row["normalized_context_status"].startswith("NORMALIZED_") for row in disjoint), Counter(row["normalized_context_status"] for row in disjoint))

    warnings = read_tsv(WARNING)
    warnings_by_surface = keyed(warnings, "surface")
    check("nine_warning_set_exact", set(warnings_by_surface) == set(warning_by_surface), sorted(warnings_by_surface))
    warning_errors = []
    for surface, source in warning_by_surface.items():
        row = warnings_by_surface[surface]
        anchor = anchor_by_surface[surface]
        if (
            row["anchor_recipe"] != source["anchor_recipe"]
            or row["target_modes"] != source["target_modes"]
            or row["old_anchor_modes"] != source["old_anchor_modes"]
            or row["current_peer_event_count"] != source["current_peer_event_count"]
            or row["contract_relation"] != anchor["contract_relation"]
            or not row["normalized_context_status"].startswith("NORMALIZED_")
        ):
            warning_errors.append(surface)
    check("all_nine_warnings_normalized_without_peer_requirement", not warning_errors, warning_errors)
    check("five_warning_cards_retain_optional_peers", sum(int(row["current_peer_event_count"]) > 0 for row in warnings) == 5, {row["surface"]: row["current_peer_event_count"] for row in warnings})

    promoted = read_tsv(PROMOTED)
    promoted_by_surface = keyed(promoted, "surface")
    source_context_residual = {
        row["surface"]
        for row in source_residual
        if row["residual_dimension"] == "ANCHOR_CONTEXT"
    }
    check("four_source_context_rests", source_context_residual == EXPECTED_PROMOTED, sorted(source_context_residual))
    check("four_promoted_context_cards_exact", set(promoted_by_surface) == EXPECTED_PROMOTED, sorted(promoted_by_surface))
    promoted_errors = []
    for surface in EXPECTED_PROMOTED:
        row = promoted_by_surface[surface]
        source = visible_by_surface[surface]
        anchor = anchor_by_surface[surface]
        if (
            row["final_recipe"] != source["final_recipe"]
            or row["selected_visible_trace"] != source["selected_visible_trace"]
            or row["exact_surface_reconstruction"] != "YES"
            or row["exact_recipe_reconstruction"] != "YES"
            or row["neutral_component_reading_de"] != source["neutral_component_reading_de"]
            or row["known_contextual_readings_de"] != source["known_contextual_readings_de"]
            or row["contract_relation"] != "IDENTICAL_SLOT_CONTRACT"
            or row["full_contract_signature"] != anchor["full_contract_signature"]
        ):
            promoted_errors.append(surface)
    check("promoted_routes_meanings_and_contracts_exact", not promoted_errors, promoted_errors)
    promoted_signatures = Counter(row["full_contract_signature"] for row in promoted)
    check("promoted_contract_split_two_plus_two", promoted_signatures == Counter({"ACTION_OPEN/ARGUMENT_OPEN": 2, "ACTION_VISIBLE/ARGUMENT_OPEN": 2}), dict(promoted_signatures))

    residual = read_tsv(RESIDUAL)
    residual_by_surface = keyed(residual, "surface")
    source_interface = {
        row["surface"]: row
        for row in source_residual
        if row["residual_dimension"] == "DIRECT_INTERFACE"
    }
    check("five_interface_rests_exact", set(residual_by_surface) == EXPECTED_RESIDUAL == set(source_interface), sorted(residual_by_surface))
    residual_errors = [
        surface
        for surface, row in residual_by_surface.items()
        if row["final_recipe"] != source_interface[surface]["final_recipe"]
        or row["residual_detail"] != source_interface[surface]["residual_detail"]
        or row["residual_dimension"] != "DIRECT_INTERFACE"
    ]
    check("interface_recipes_and_pairs_preserved", not residual_errors, residual_errors)

    result = json.loads(RESULT.read_text(encoding="utf-8"))
    expected_metrics = {
        "status": STATUS,
        "reader_surface_count": 145,
        "slot_contract_class_count": 4,
        "fragment_anchor_card_count": 81,
        "anchor_and_target_mode_contract_feasible_count": 81,
        "disjoint_instance_mode_card_count": 12,
        "disjoint_identical_contract_count": 11,
        "disjoint_extension_narrowed_contract_count": 1,
        "disjoint_normalized_count": 12,
        "previous_context_warning_count": 9,
        "previous_context_warning_normalized_count": 9,
        "prior_peer_supported_warning_count": 5,
        "promoted_context_card_count": 4,
        "promoted_exact_visible_route_count": 4,
        "promoted_complete_neutral_meaning_count": 4,
        "promoted_complete_context_meaning_count": 4,
        "residual_support_card_count": 5,
        "residual_anchor_context_count": 0,
        "residual_direct_interface_count": 5,
        "new_pages": 0,
        "recipe_changes": 0,
        "root_meaning_changes": 0,
    }
    check("result_metrics_exact", result == expected_metrics, {key: result.get(key) for key in expected_metrics if result.get(key) != expected_metrics[key]})
    summary = {row["metric"]: row["value"] for row in read_tsv(SUMMARY)}
    check("summary_matches_result", all(summary.get(key) == str(value) for key, value in result.items()), len(summary))
    book = BOOK.read_text(encoding="utf-8")
    check("book_names_all_four_promotions", all(f"`{surface}`" in book for surface in EXPECTED_PROMOTED), len(book))
    check("book_names_all_five_interfaces", all(f"`{surface}:" in book for surface in EXPECTED_RESIDUAL), len(book))
    check("book_states_no_lexical_switch", "Kein Fall braucht einen lexikalischen Kontextumschalter" in book, len(book))

    deterministic_files = [PROFILE, ANCHOR, DISJOINT, WARNING, PROMOTED, RESIDUAL, SUMMARY, BOOK, RESULT]
    before = {path.name: sha256(path) for path in deterministic_files}
    replay = subprocess.run(
        [sys.executable, str(RUN)],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    after = {path.name: sha256(path) for path in deterministic_files}
    check("deterministic_replay_exit", replay.returncode == 0, replay.stderr[-2000:])
    check("deterministic_artifact_hashes", before == after, {name: [before[name], after[name]] for name in before if before[name] != after[name]})

    passed = all(item["passed"] for item in checks)
    payload = {
        "status": "PASS" if passed else "FAIL",
        "check_count": len(checks),
        "passed_count": sum(item["passed"] for item in checks),
        "failed_count": sum(not item["passed"] for item in checks),
        "checks": checks,
        "input_sha256": {
            path.name: sha256(path)
            for path in [CONTRACT_IN, FRAGMENT_IN, READER_IN, WARNING_IN, VISIBLE_IN, RESIDUAL_IN]
        },
        "artifact_sha256": {path.name: sha256(path) for path in deterministic_files},
    }
    VALIDATION.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
