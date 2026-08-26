#!/usr/bin/env python3
"""Validate GDT472 and verify a byte-identical deterministic rebuild."""

from __future__ import annotations

import csv
import hashlib
import json
import subprocess
import sys
from collections import Counter
from pathlib import Path

sys.dont_write_bytecode = True


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
BASE = ROOT / "experiments/yolo/gdt472_complete_address_template_dictionary"
OUT = BASE / "artifacts"
RUN = BASE / "src/run.py"
PREPARE = BASE / "src/prepare_complete_future_address.py"
G463 = ROOT / "experiments/yolo/gdt463_low_support_exact_card_edge_bridges"
G464 = ROOT / "experiments/yolo/gdt464_residual_exact_package_bridge"
G466 = ROOT / "experiments/yolo/gdt466_future_address_mixed_dictionary_intake"
G470 = ROOT / "experiments/yolo/gdt470_future_address_intake_worksheet"
G471 = ROOT / "experiments/yolo/gdt471_empirical_address_shell_phrasebook"

FULL = OUT / "gdt472_18_full_formula_cold_replay.tsv"
ASSIGNMENTS = OUT / "gdt472_107_complete_template_assignments.tsv"
SURFACES = OUT / "gdt472_87_transferable_surface_templates.tsv"
COMPONENTS = OUT / "gdt472_85_transferable_component_templates.tsv"
TOPOLOGIES = OUT / "gdt472_20_transferable_topologies.tsv"
PACKAGES = OUT / "gdt472_2_exact_package_cards.tsv"
TEMPLATE = OUT / "gdt472_complete_ranked_address_item_template.tsv"
CONTRACT = OUT / "gdt472_complete_dictionary_contract.json"
RESULT = OUT / "gdt472_result.json"
VALIDATION = OUT / "gdt472_validation.json"
GENERATED = (FULL, ASSIGNMENTS, SURFACES, COMPONENTS, TOPOLOGIES, PACKAGES, TEMPLATE, CONTRACT, RESULT)

sys.path.insert(0, str(G470 / "src"))
sys.path.insert(0, str(G471 / "src"))
sys.path.insert(0, str(BASE / "src"))
from worksheet_lib import WORKSHEET_FIELDS  # noqa: E402
from template_lib import EMPIRICAL_FIELDS  # noqa: E402
from complete_lib import COMPLETE_FIELDS  # noqa: E402


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def tsv_fields(path: Path) -> list[str]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t").fieldnames or [])


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def cli(surface: str, content_class: str, *extra: str) -> tuple[int, dict[str, object], str]:
    completed = subprocess.run(
        [sys.executable, str(PREPARE), surface, content_class, *extra],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    return completed.returncode, json.loads(completed.stdout) if completed.stdout else {}, completed.stderr


def main() -> int:
    checks: list[dict[str, object]] = []

    def check(name: str, condition: bool, detail: str) -> None:
        checks.append({"name": name, "status": "PASS" if condition else "FAIL", "detail": detail})

    labels = read_tsv(G466 / "artifacts/gdt466_107_intake_dictionary.tsv")
    old_assignments = read_tsv(G471 / "artifacts/gdt471_89_template_assignments.tsv")
    ykyd_source = next(row for row in read_tsv(G463 / "artifacts/gdt463_4_target_reconstructions.tsv") if row["surface"] == "ykyd")
    yddy_source = next(row for row in read_tsv(G464 / "artifacts/gdt464_10_target_revisions.tsv") if row["surface"] == "yddy")
    full = read_tsv(FULL)
    assignments = read_tsv(ASSIGNMENTS)
    surfaces = read_tsv(SURFACES)
    components = read_tsv(COMPONENTS)
    topologies = read_tsv(TOPOLOGIES)
    packages = read_tsv(PACKAGES)
    template = read_tsv(TEMPLATE)
    contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
    result = json.loads(RESULT.read_text(encoding="utf-8"))

    full_source = [row for row in labels if row["gdt466_hybrid_status"] == "FULL_FUNCTION_FORMULA"]
    check("label_source_count", len(labels) == 107, f"observed={len(labels)}")
    check("old_slot_assignment_count", len(old_assignments) == 89, f"observed={len(old_assignments)}")
    check("full_source_count", len(full_source) == 18, f"observed={len(full_source)}")
    check("source_partition", {row["surface"] for row in labels} == {row["source_surface"] for row in old_assignments} | {row["surface"] for row in full_source} and not ({row["source_surface"] for row in old_assignments} & {row["surface"] for row in full_source}), "89+18 disjoint")

    check("full_replay_count", len(full) == 18, f"observed={len(full)}")
    check("full_replay_order", [row["surface"] for row in full] == [row["surface"] for row in full_source], "source order exact")
    check("full_exact_replay", all(row["exact_label_reading_pass"] == "YES" and row["replay_pass"] == "YES" for row in full), "18/18")
    full_classes = Counter(row["replay_class"] for row in full)
    check("full_replay_classes", full_classes == Counter({"GENERAL_ZERO_NAME_FUNCTION_TEMPLATE": 16, "EXACT_PACKAGE_ONLY_ZERO_NAME_CARD": 2}), str(full_classes))
    general = [row for row in full if row["replay_class"] == "GENERAL_ZERO_NAME_FUNCTION_TEMPLATE"]
    exact_packages = [row for row in full if row["replay_class"] == "EXACT_PACKAGE_ONLY_ZERO_NAME_CARD"]
    check("general_full_cold_match", all(row["cold_complete_recipe_match"] == "YES" and row["cold_route"] == "CALIBRATED_FULL_FUNCTION_FORMULA" and row["cold_recipe"] == row["source_recipe"] and row["cold_reading_de"] == row["source_reading_de"] and row["cold_known_character_count"] == row["surface_character_count"] for row in general), "16/16")
    check("exact_package_surface_set", {row["surface"] for row in exact_packages} == {"ykyd", "yddy"}, str(sorted(row["surface"] for row in exact_packages)))
    ykyd_full = next(row for row in exact_packages if row["surface"] == "ykyd")
    yddy_full = next(row for row in exact_packages if row["surface"] == "yddy")
    check("ykyd_cold_partial", ykyd_full["cold_route"] == "CALIBRATED_FUNCTION_SHELL_PLUS_LEARNED_CORE" and ykyd_full["cold_recipe"] == "Y+K+Y" and ykyd_full["cold_known_character_count"] == "3", str(ykyd_full))
    check("yddy_cold_whole", yddy_full["cold_route"] == "WHOLE_LEARNED_OWNER_NAME" and yddy_full["cold_recipe"] == "NONE" and yddy_full["cold_known_character_count"] == "0", str(yddy_full))

    check("assignment_count", len(assignments) == 107, f"observed={len(assignments)}")
    check("assignment_order", [row["surface"] for row in assignments] == [row["surface"] for row in labels], "source order exact")
    check("assignment_ids_unique", len({row["complete_assignment_id"] for row in assignments}) == 107, "107 unique")
    assignment_modes = Counter(row["assignment_mode"] for row in assignments)
    expected_modes = Counter({"LEARNED_SLOT_TEMPLATE": 89, "GENERAL_ZERO_NAME_FUNCTION_TEMPLATE": 16, "EXACT_PACKAGE_ONLY_ZERO_NAME_CARD": 2})
    check("assignment_modes", assignment_modes == expected_modes, str(assignment_modes))
    check("assignment_transferability", sum(row["transferable"] == "YES" for row in assignments) == 105 and sum(row["transferable"] == "NO" for row in assignments) == 2, "105 transferable; 2 exact only")
    check("assignment_exact_runtime_rank", all(row["runtime_exact_label_rank"] == "0" for row in assignments), "107/107")
    package_assignments = [row for row in assignments if row["assignment_mode"] == "EXACT_PACKAGE_ONLY_ZERO_NAME_CARD"]
    check("package_assignments", {row["surface"] for row in package_assignments} == {"ykyd", "yddy"} and all(row["surface_template_id"] == row["component_template_id"] == row["topology_id"] == "NONE" and row["complete_template_id"].startswith("G472-X") for row in package_assignments), str(package_assignments))
    zero_assignments = [row for row in assignments if row["assignment_mode"] == "GENERAL_ZERO_NAME_FUNCTION_TEMPLATE"]
    check("zero_assignments_no_name_slots", len(zero_assignments) == 16 and all("{NAME_" not in row["surface_template"] and "{NAME_" not in row["component_template"] and "{NAME_" not in row["slot_topology"] for row in zero_assignments), "16/16")
    slot_assignments = [row for row in assignments if row["assignment_mode"] == "LEARNED_SLOT_TEMPLATE"]
    check("slot_assignments_keep_name_slots", len(slot_assignments) == 89 and all("{NAME_" in row["surface_template"] for row in slot_assignments), "89/89")
    old_by_surface = {row["source_surface"]: row for row in old_assignments}
    check("slot_assignment_replay", all(row["surface_template"] == old_by_surface[row["surface"]]["surface_template"] and row["component_template"] == old_by_surface[row["surface"]]["component_template"] and row["meaning_template_de"] == old_by_surface[row["surface"]]["meaning_template_de"] for row in slot_assignments), "89/89")
    check("assignment_no_sealed_pages", all(not row["physical_page"].startswith("f84") for row in assignments), "107/107")

    check("surface_template_count", len(surfaces) == 87, f"observed={len(surfaces)}")
    check("surface_ids_unique", len({row["surface_template_id"] for row in surfaces}) == 87 and len({row["surface_template"] for row in surfaces}) == 87, "87 unique")
    check("surface_source_total", sum(int(row["source_count"]) for row in surfaces) == 105, "total=105")
    surface_states = Counter(row["familiarity_state"] for row in surfaces)
    expected_states = Counter({"SINGLETON_EXACT_FUNCTION_TEMPLATE": 73, "RECURRENT_EXACT_FUNCTION_TEMPLATE": 6, "CROSS_OWNER_RECURRENT_EXACT_FUNCTION_TEMPLATE": 4, "MULTI_PAGE_RECURRENT_EXACT_FUNCTION_TEMPLATE": 3, "WHOLE_NAME_DEFAULT": 1})
    check("surface_state_counts", surface_states == expected_states, str(surface_states))
    recurrent_surfaces = [row for row in surfaces if int(row["source_count"]) > 1]
    check("surface_recurrence", len(recurrent_surfaces) == 14 and sum(int(row["source_count"]) for row in recurrent_surfaces) == 32, "14 templates/32 sources")
    zero_surface_rows = [row for row in surfaces if row["template_modes"] == "GENERAL_ZERO_NAME_FUNCTION_TEMPLATE"]
    check("zero_surface_templates", len(zero_surface_rows) == 16 and all(int(row["source_count"]) == 1 and row["learned_slot_counts"] == "0" and row["familiarity_state"] == "SINGLETON_EXACT_FUNCTION_TEMPLATE" for row in zero_surface_rows), "16 singleton zero-name templates")

    check("component_template_count", len(components) == 85, f"observed={len(components)}")
    check("component_ids_unique", len({row["component_template_id"] for row in components}) == 85 and len({row["component_template"] for row in components}) == 85, "85 unique")
    check("component_source_total", sum(int(row["source_count"]) for row in components) == 105, "total=105")
    recurrent_components = [row for row in components if int(row["source_count"]) > 1]
    check("component_recurrence", len(recurrent_components) == 15 and sum(int(row["source_count"]) for row in recurrent_components) == 35, "15 templates/35 sources")
    alternate_components = [row for row in components if row["alternate_surface_rendering"] == "YES"]
    check("component_alternate_renderings", len(alternate_components) == 2 and sum(int(row["source_count"]) for row in alternate_components) == 5 and {row["component_template"] for row in alternate_components} == {"{NAME_1} · AIIN", "{NAME_1} · O+IIN"}, str(sorted(row["component_template"] for row in alternate_components)))

    check("topology_count", len(topologies) == 20, f"observed={len(topologies)}")
    check("topology_ids_unique", len({row["topology_id"] for row in topologies}) == 20 and len({row["slot_topology"] for row in topologies}) == 20, "20 unique")
    check("topology_source_total", sum(int(row["source_count"]) for row in topologies) == 105, "total=105")
    recurrent_topologies = [row for row in topologies if row["recurrent"] == "YES"]
    check("topology_recurrence", len(recurrent_topologies) == 15 and sum(int(row["source_count"]) for row in recurrent_topologies) == 100, "15 topologies/100 sources")
    zero_topologies = [row for row in topologies if "GENERAL_ZERO_NAME_FUNCTION_TEMPLATE" in row["template_modes"].split("|")]
    check("zero_topology_set", {row["slot_topology"] for row in zero_topologies} == {"PREFIX", "PREFIX · SUFFIX", "PREFIX · INTERNAL · SUFFIX", "PREFIX · INTERNAL · INTERNAL · SUFFIX"}, str(sorted(row["slot_topology"] for row in zero_topologies)))
    check("zero_topology_counts", {row["slot_topology"]: int(row["source_count"]) for row in zero_topologies} == {"PREFIX": 1, "PREFIX · SUFFIX": 7, "PREFIX · INTERNAL · SUFFIX": 7, "PREFIX · INTERNAL · INTERNAL · SUFFIX": 1}, str({row["slot_topology"]: int(row["source_count"]) for row in zero_topologies}))

    check("package_count", len(packages) == 2, f"observed={len(packages)}")
    check("package_order", [row["surface"] for row in packages] == ["ykyd", "yddy"], str([row["surface"] for row in packages]))
    check("package_nontransferable", all(row["transferable"] == "NO" and row["reader_policy"] == "EXACT_SURFACE_ONLY__NEVER_GENERATE_OR_COMPONENT_MATCH" for row in packages), "2/2")
    ykyd = next(row for row in packages if row["surface"] == "ykyd")
    yddy = next(row for row in packages if row["surface"] == "yddy")
    check("ykyd_evidence", ykyd["source_experiment"] == "GDT463" and ykyd["source_evidence_id"] == ykyd_source["target_id"] and ykyd["exact_segmentation"] == ykyd_source["selected_surface_segmentation"] and ykyd["exact_recipe"] == ykyd_source["selected_function_recipe"], str(ykyd))
    check("yddy_evidence", yddy["source_experiment"] == "GDT464" and yddy["source_evidence_id"] == yddy_source["target_id"] and yddy["exact_segmentation"] == yddy_source["selected_surface_segmentation"] and yddy["exact_recipe"] == yddy_source["selected_function_recipe"], str(yddy))

    check("ranked_template_empty", template == [], f"rows={len(template)}")
    check("ranked_template_schema", tsv_fields(TEMPLATE) == WORKSHEET_FIELDS + EMPIRICAL_FIELDS + COMPLETE_FIELDS, f"columns={len(tsv_fields(TEMPLATE))}")
    check("contract_status", contract["status"] == "COMPLETE_107_LABEL_TEMPLATE_DICTIONARY_READY", contract["status"])
    check("contract_partition", contract["known_label_count"] == 107 and contract["learned_slot_label_count"] == 89 and contract["general_zero_name_formula_count"] == 16 and contract["exact_package_only_count"] == 2, str(contract))
    check("contract_decks", contract["transferable_surface_template_count"] == 87 and contract["transferable_component_template_count"] == 85 and contract["transferable_topology_count"] == 20, str(contract))
    check("contract_packages", contract["exact_package_cards"] == ["ykyd", "yddy"] and contract["page_slots"] == 4 and contract["page_slot_state"] == "UNRELEASED", str(contract))

    code, payload, error = cli("ykyd", "DRUG_OR_INGREDIENT_OBJECT")
    check("cli_ykyd_exit", code == 0, error or "exit 0")
    check("cli_ykyd_exact_package", payload.get("working_reading_de") == "POSTEN · GEBEN · POSTEN · HIER" and payload.get("complete_assignment_mode") == "EXACT_PACKAGE_ONLY_ZERO_NAME_CARD" and payload.get("complete_transferability") == "NO" and payload.get("complete_exact_package_card_id") == "G472-X01" and payload.get("empirical_familiarity_rank") == 0, str(payload))
    code, payload, error = cli("yddy", "DRUG_OR_INGREDIENT_OBJECT")
    check("cli_yddy_exit", code == 0, error or "exit 0")
    check("cli_yddy_exact_package", payload.get("working_reading_de") == "POSTEN · HIER · POSTEN" and payload.get("complete_assignment_mode") == "EXACT_PACKAGE_ONLY_ZERO_NAME_CARD" and payload.get("complete_transferability") == "NO" and payload.get("complete_exact_package_card_id") == "G472-X02", str(payload))
    code, payload, error = cli("otainy", "STAR_BEARING_RING_POSITION")
    check("cli_zero_name_exit", code == 0, error or "exit 0")
    check("cli_zero_name_template", payload.get("working_reading_de") == "DANACH · ANTEIL · POSTEN" and payload.get("complete_assignment_mode") == "GENERAL_ZERO_NAME_FUNCTION_TEMPLATE" and payload.get("complete_transferability") == "YES" and payload.get("empirical_learned_span_trace") == "", str(payload))
    code, payload, error = cli("otexeeon", "PICTURED_PLANT")
    check("cli_unseen_slot_exit", code == 0, error or "exit 0")
    check("cli_unseen_slot_rank", payload.get("empirical_familiarity_state") == "CROSS_OWNER_RECURRENT_EXACT_FUNCTION_TEMPLATE" and payload.get("empirical_familiarity_rank") == 1 and payload.get("complete_assignment_mode") == "UNSEEN_FORM_RANKED_BY_TRANSFERABLE_TEMPLATE", str(payload))
    code, payload, error = cli("otxal", "STAR_BEARING_RING_POSITION")
    check("cli_component_exit", code == 0, error or "exit 0")
    check("cli_component_rank", payload.get("empirical_familiarity_state") == "KNOWN_COMPONENT_TEMPLATE_ALTERNATE_RENDERING" and payload.get("empirical_familiarity_rank") == 5, str(payload))
    code, payload, error = cli("zxqv", "PICTURED_PLANT")
    check("cli_whole_exit", code == 0, error or "exit 0")
    check("cli_whole_default", payload.get("working_reading_de") == "[PFLANZENNAME:zxqv]" and payload.get("empirical_familiarity_state") == "WHOLE_NAME_DEFAULT" and payload.get("empirical_familiarity_rank") == 7, str(payload))

    check("result_status", result["status"] == "ALL_107_LABELS_HAVE_COMPLETE_TEMPLATE_ASSIGNMENTS__TWO_EXACT_PACKAGES_REMAIN_NONTRANSFERABLE", result["status"])
    check("result_full", result["full_formula_count"] == result["full_formula_replay_pass_count"] == 18 and result["general_zero_name_formula_count"] == 16 and result["exact_package_only_formula_count"] == 2, str(result))
    check("result_assignments", result["complete_assignment_count"] == 107 and result["assignment_mode_counts"] == dict(sorted(assignment_modes.items())) and result["transferable_assignment_count"] == 105 and result["nontransferable_assignment_count"] == 2, str(result))
    check("result_surface", result["transferable_surface_template_count"] == 87 and result["surface_template_state_counts"] == dict(sorted(surface_states.items())) and result["recurrent_surface_template_count"] == 14 and result["recurrent_surface_template_source_count"] == 32, str(result))
    check("result_components", result["transferable_component_template_count"] == 85 and result["recurrent_component_template_count"] == 15 and result["recurrent_component_template_source_count"] == 35, str(result))
    check("result_topologies", result["transferable_topology_count"] == 20 and result["recurrent_topology_count"] == 15 and result["recurrent_topology_source_count"] == 100, str(result))
    check("result_slots", result["future_page_slots"] == 4 and result["released_page_slots"] == 0, str(result))
    check("result_claim_ceiling", result["new_pages"] == result["new_channels"] == result["new_component_meanings"] == result["new_surface_predictions"] == result["confirmed_lexemes"] == 0, "no expanded claim")

    before = {path.name: sha256(path) for path in GENERATED}
    completed = subprocess.run([sys.executable, str(RUN)], cwd=ROOT, capture_output=True, text=True, check=False)
    check("deterministic_rebuild_exit", completed.returncode == 0, completed.stderr[-500:] or "exit 0")
    after = {path.name: sha256(path) for path in GENERATED}
    check("deterministic_rebuild_bytes", before == after, "all generated artifact hashes unchanged")

    passed = sum(row["status"] == "PASS" for row in checks)
    failed = len(checks) - passed
    payload = {
        "status": "PASS" if failed == 0 else "FAIL",
        "check_count": len(checks),
        "passed": passed,
        "failed": failed,
        "checks": checks,
    }
    VALIDATION.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": payload["status"], "checks": len(checks), "passed": passed, "failed": failed}, ensure_ascii=False))
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
