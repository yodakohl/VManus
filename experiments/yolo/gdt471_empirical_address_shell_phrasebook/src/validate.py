#!/usr/bin/env python3
"""Validate GDT471 and verify a byte-identical deterministic rebuild."""

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
BASE = ROOT / "experiments/yolo/gdt471_empirical_address_shell_phrasebook"
OUT = BASE / "artifacts"
RUN = BASE / "src/run.py"
PREPARE = BASE / "src/prepare_ranked_future_address.py"
G466 = ROOT / "experiments/yolo/gdt466_future_address_mixed_dictionary_intake"
G470 = ROOT / "experiments/yolo/gdt470_future_address_intake_worksheet"

ASSIGNMENTS = OUT / "gdt471_89_template_assignments.tsv"
SURFACES = OUT / "gdt471_71_empirical_surface_templates.tsv"
COMPONENTS = OUT / "gdt471_69_component_templates.tsv"
TOPOLOGIES = OUT / "gdt471_16_slot_topologies.tsv"
MUTATIONS = OUT / "gdt471_89_mutation_template_replay.tsv"
FAMILIES = OUT / "gdt471_18_family_marker_core_change_sensitivity.tsv"
TEMPLATE = OUT / "gdt471_ranked_address_item_template.tsv"
CONTRACT = OUT / "gdt471_familiarity_contract.json"
RESULT = OUT / "gdt471_result.json"
VALIDATION = OUT / "gdt471_validation.json"
GENERATED = (ASSIGNMENTS, SURFACES, COMPONENTS, TOPOLOGIES, MUTATIONS, FAMILIES, TEMPLATE, CONTRACT, RESULT)

sys.path.insert(0, str(G470 / "src"))
sys.path.insert(0, str(BASE / "src"))
from worksheet_lib import WORKSHEET_FIELDS  # noqa: E402
from template_lib import EMPIRICAL_FIELDS  # noqa: E402


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

    probes = read_tsv(G466 / "artifacts/gdt466_89_unseen_core_insertion_probes.tsv")
    labels = read_tsv(G466 / "artifacts/gdt466_107_intake_dictionary.tsv")
    rule_source = read_tsv(G466 / "artifacts/gdt466_44_function_channel_deck.tsv")
    family_source = read_tsv(G466 / "artifacts/gdt466_18_owner_family_channel_deck.tsv")
    supported_source = read_tsv(G470 / "artifacts/gdt470_89_supported_unseen_core_replay.tsv")
    assignments = read_tsv(ASSIGNMENTS)
    surfaces = read_tsv(SURFACES)
    components = read_tsv(COMPONENTS)
    topologies = read_tsv(TOPOLOGIES)
    mutations = read_tsv(MUTATIONS)
    families = read_tsv(FAMILIES)
    template = read_tsv(TEMPLATE)
    contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
    result = json.loads(RESULT.read_text(encoding="utf-8"))

    check("probe_source_count", len(probes) == 89, f"observed={len(probes)}")
    check("label_source_count", len(labels) == 107, f"observed={len(labels)}")
    check("rule_source_count", len(rule_source) == 44, f"observed={len(rule_source)}")
    check("family_source_count", len(family_source) == 18, f"observed={len(family_source)}")
    check("supported_source_count", len(supported_source) == 89 and all(row["replay_pass"] == "YES" for row in supported_source), "89/89")
    check("probe_sources_unique", len({row["source_surface"] for row in probes}) == 89, "89 unique")
    label_surfaces = {row["surface"] for row in labels}
    check("probe_sources_are_labels", all(row["source_surface"] in label_surfaces for row in probes), "89/89")

    check("assignment_count", len(assignments) == 89, f"observed={len(assignments)}")
    check("assignment_order", [row["source_probe_id"] for row in assignments] == [row["probe_id"] for row in probes], "source order exact")
    check("assignment_surface_order", [row["source_surface"] for row in assignments] == [row["source_surface"] for row in probes], "surface order exact")
    check("assignment_ids_unique", len({row["assignment_id"] for row in assignments}) == 89, "89 unique")
    check("assignment_template_ids_present", all(row["surface_template_id"] != "NONE" and row["component_template_id"] != "NONE" and row["topology_id"] != "NONE" for row in assignments), "89/89")
    check("assignment_slots_cover_names", all(int(row["learned_slot_count"]) >= 1 and row["learned_span_trace"] for row in assignments), "89/89")
    check("assignment_no_sealed_pages", all(not row["physical_page"].startswith("f84") for row in assignments), "89/89")

    check("surface_template_count", len(surfaces) == 71, f"observed={len(surfaces)}")
    check("surface_template_ids_unique", len({row["surface_template_id"] for row in surfaces}) == 71, "71 unique")
    check("surface_templates_unique", len({row["surface_template"] for row in surfaces}) == 71, "71 unique")
    check("surface_source_total", sum(int(row["source_count"]) for row in surfaces) == 89, "total=89")
    surface_states = Counter(row["familiarity_state"] for row in surfaces)
    expected_surface_states = Counter({
        "SINGLETON_EXACT_FUNCTION_TEMPLATE": 57,
        "RECURRENT_EXACT_FUNCTION_TEMPLATE": 6,
        "CROSS_OWNER_RECURRENT_EXACT_FUNCTION_TEMPLATE": 4,
        "MULTI_PAGE_RECURRENT_EXACT_FUNCTION_TEMPLATE": 3,
        "WHOLE_NAME_DEFAULT": 1,
    })
    check("surface_state_counts", surface_states == expected_surface_states, str(surface_states))
    check("surface_rank_mapping", all(int(row["familiarity_rank"]) == {
        "CROSS_OWNER_RECURRENT_EXACT_FUNCTION_TEMPLATE": 1,
        "MULTI_PAGE_RECURRENT_EXACT_FUNCTION_TEMPLATE": 2,
        "RECURRENT_EXACT_FUNCTION_TEMPLATE": 3,
        "SINGLETON_EXACT_FUNCTION_TEMPLATE": 4,
        "WHOLE_NAME_DEFAULT": 7,
    }[row["familiarity_state"]] for row in surfaces), "71/71")
    recurrent_surfaces = [row for row in surfaces if int(row["source_count"]) > 1]
    check("surface_recurrence", len(recurrent_surfaces) == 14 and sum(int(row["source_count"]) for row in recurrent_surfaces) == 32, "14 templates/32 sources")
    cross_owner = [row for row in surfaces if row["familiarity_state"] == "CROSS_OWNER_RECURRENT_EXACT_FUNCTION_TEMPLATE"]
    check("cross_owner_function_templates", len(cross_owner) == 4 and sum(int(row["source_count"]) for row in cross_owner) == 11, "4 templates/11 sources")
    cross_owner_template_set = {row["surface_template"] for row in cross_owner}
    check("cross_owner_template_set", cross_owner_template_set == {"ot{NAME_1}", "ar{NAME_1}", "ol{NAME_1}", "{NAME_1}ar{NAME_2}"}, str(sorted(cross_owner_template_set)))
    cross_page_function = [row for row in surfaces if int(row["function_channel_count"]) > 0 and int(row["page_count"]) > 1]
    check("cross_page_function_templates", len(cross_page_function) == 7 and sum(int(row["source_count"]) for row in cross_page_function) == 18, "7 templates/18 sources")
    ot_name = next(row for row in surfaces if row["surface_template"] == "ot{NAME_1}")
    check("ot_name_anchor", int(ot_name["source_count"]) == 5 and int(ot_name["content_class_count"]) == 4 and int(ot_name["page_count"]) == 4 and int(ot_name["familiarity_rank"]) == 1, str(ot_name))
    whole_name = next(row for row in surfaces if row["surface_template"] == "{NAME_1}")
    check("whole_name_not_promoted", int(whole_name["source_count"]) == 2 and whole_name["familiarity_state"] == "WHOLE_NAME_DEFAULT" and int(whole_name["familiarity_rank"]) == 7, str(whole_name))

    check("component_template_count", len(components) == 69, f"observed={len(components)}")
    check("component_ids_unique", len({row["component_template_id"] for row in components}) == 69, "69 unique")
    check("component_source_total", sum(int(row["source_count"]) for row in components) == 89, "total=89")
    recurrent_components = [row for row in components if int(row["source_count"]) > 1]
    check("component_recurrence", len(recurrent_components) == 15 and sum(int(row["source_count"]) for row in recurrent_components) == 35, "15 templates/35 sources")
    alternate = [row for row in components if row["alternate_surface_rendering"] == "YES"]
    check("alternate_component_count", len(alternate) == 2 and sum(int(row["source_count"]) for row in alternate) == 5, "2 templates/5 sources")
    alternate_component_set = {row["component_template"] for row in alternate}
    check("alternate_component_set", alternate_component_set == {"{NAME_1} · AIIN", "{NAME_1} · O+IIN"}, str(sorted(alternate_component_set)))
    aiin = next(row for row in alternate if row["component_template"] == "{NAME_1} · AIIN")
    check("aiin_renderer_pair", set(aiin["surface_templates"].split("|")) == {"{NAME_1}aiin", "{NAME_1}daiin"} and int(aiin["source_count"]) == 3, str(aiin))
    oiin = next(row for row in alternate if row["component_template"] == "{NAME_1} · O+IIN")
    check("oiin_renderer_pair", set(oiin["surface_templates"].split("|")) == {"{NAME_1}oin", "{NAME_1}oiin"} and int(oiin["source_count"]) == 2 and int(oiin["content_class_count"]) == 2, str(oiin))

    check("topology_count", len(topologies) == 16, f"observed={len(topologies)}")
    check("topology_ids_unique", len({row["topology_id"] for row in topologies}) == 16, "16 unique")
    check("topology_source_total", sum(int(row["source_count"]) for row in topologies) == 89, "total=89")
    recurrent_topologies = [row for row in topologies if row["recurrent"] == "YES"]
    check("topology_recurrence", len(recurrent_topologies) == 13 and sum(int(row["source_count"]) for row in recurrent_topologies) == 86, "13 topologies/86 sources")
    prefix_name = next(row for row in topologies if row["slot_topology"] == "PREFIX · {NAME_1}")
    check("prefix_name_topology", int(prefix_name["source_count"]) == 17 and int(prefix_name["content_class_count"]) == 4, str(prefix_name))

    check("mutation_count", len(mutations) == 89, f"observed={len(mutations)}")
    check("mutation_order", [row["source_probe_id"] for row in mutations] == [row["probe_id"] for row in probes], "source order exact")
    check("mutation_surface_templates", all(row["source_surface_template"] == row["mutated_surface_template"] for row in mutations), "89/89")
    check("mutation_component_templates", all(row["source_component_template"] == row["mutated_component_template"] for row in mutations), "89/89")
    check("mutation_topologies", all(row["source_slot_topology"] == row["mutated_slot_topology"] for row in mutations), "89/89")
    check("mutation_function_templates", all(row["function_template_stable"] == "YES" for row in mutations), "89/89")
    check("mutation_gdt470_replay", all(row["gdt470_supported_replay_pass"] == "YES" for row in mutations), "89/89")
    check("mutation_all_pass", all(row["replay_pass"] == "YES" for row in mutations), "89/89")
    mutation_states = Counter(row["familiarity_state"] for row in mutations)
    assignment_states = Counter(row["familiarity_state"] for row in assignments)
    check("mutation_familiarity_distribution", mutation_states == assignment_states == Counter({"SINGLETON_EXACT_FUNCTION_TEMPLATE": 57, "RECURRENT_EXACT_FUNCTION_TEMPLATE": 12, "CROSS_OWNER_RECURRENT_EXACT_FUNCTION_TEMPLATE": 11, "MULTI_PAGE_RECURRENT_EXACT_FUNCTION_TEMPLATE": 7, "WHOLE_NAME_DEFAULT": 2}), str(mutation_states))
    check("route_stability", sum(row["route_stable"] == "YES" for row in mutations) == 88, "88/89")
    route_changes = [row for row in mutations if row["route_stable"] == "NO"]
    check("only_cheosdy_route_changes", len(route_changes) == 1 and route_changes[0]["source_surface"] == "cheosdy" and route_changes[0]["source_route"] == "STRICT_OWNER_FAMILY_PLUS_LEARNED_NAME" and route_changes[0]["mutated_route"] == "WHOLE_LEARNED_OWNER_NAME", str(route_changes))
    source_family = [row for row in mutations if row["source_has_family_marker"] == "YES"]
    check("source_family_probe_count", len(source_family) == 30, f"observed={len(source_family)}")
    check("family_any_retained", sum(row["mutation_retains_any_family_marker"] == "YES" for row in source_family) == 19, "19/30")
    check("family_exact_trace_retained", sum(row["family_marker_trace_stable"] == "YES" for row in source_family) == 15, "15/30")
    check("family_trace_changed", sum(row["family_marker_trace_stable"] == "NO" for row in mutations) == 15, "15/89")

    check("family_sensitivity_count", len(families) == 18, f"observed={len(families)}")
    check("family_sensitivity_order", [row["family_id"] for row in families] == [row["family_id"] for row in family_source], "source order exact")
    check("family_occurrence_totals", sum(int(row["source_probe_match_count"]) for row in families) == 48 and sum(int(row["mutation_probe_match_count"]) for row in families) == 32, "48 source; 32 mutation")
    check("family_retention_totals", sum(int(row["paired_retained_count"]) for row in families) == 32 and sum(int(row["paired_lost_count"]) for row in families) == 16 and sum(int(row["paired_gained_count"]) for row in families) == 0, "32 retained; 16 lost; 0 gained")
    family_lost_stem_set = {row["surface_stem"] for row in families if int(row["paired_lost_count"]) > 0}
    check("family_lost_stem_set", family_lost_stem_set == {"otora", "cheo", "dara", "raiin", "opal", "otch", "raii"}, str(sorted(family_lost_stem_set)))
    check("family_policy_separate", all(row["policy"] == "OWNER_FAMILY_MARKER_ONLY__NOT_A_FUNCTION_TEMPLATE" for row in families), "18/18")

    check("ranked_template_empty", template == [], f"rows={len(template)}")
    check("ranked_template_schema", tsv_fields(TEMPLATE) == WORKSHEET_FIELDS + EMPIRICAL_FIELDS, f"columns={len(tsv_fields(TEMPLATE))}")
    check("contract_status", contract["status"] == "EMPIRICAL_ADDRESS_SHELL_PHRASEBOOK_READY", contract["status"])
    check("contract_rank_order", [row["rank"] for row in contract["familiarity_order"]] == list(range(9)), str(contract["familiarity_order"]))
    check("contract_family_policy", contract["family_marker_policy"] == "Owner-family substrings remain a separate lexical clue and never increase function-template familiarity.", str(contract))
    check("contract_slots", contract["page_slots"] == 4 and contract["page_slot_state"] == "UNRELEASED", str(contract))

    code, payload, error = cli("otexeeon", "PICTURED_PLANT", "--zl3b", "otexeeon")
    check("cli_cross_owner_exit", code == 0, error or "exit 0")
    check("cli_cross_owner_reading", payload.get("working_reading_de") == "DANACH · [PFLANZENNAME:exeeon]", str(payload))
    check("cli_cross_owner_rank", payload.get("empirical_familiarity_state") == "CROSS_OWNER_RECURRENT_EXACT_FUNCTION_TEMPLATE" and payload.get("empirical_familiarity_rank") == 1 and payload.get("empirical_source_count") == 5 and payload.get("empirical_content_class_count") == 4, str(payload))
    code, payload, error = cli("otxal", "STAR_BEARING_RING_POSITION")
    check("cli_component_exit", code == 0, error or "exit 0")
    check("cli_component_rank", payload.get("empirical_familiarity_state") == "KNOWN_COMPONENT_TEMPLATE_ALTERNATE_RENDERING" and payload.get("empirical_familiarity_rank") == 5 and payload.get("empirical_component_template") == "OT · {NAME_1} · AL", str(payload))
    code, payload, error = cli("otxainy", "STAR_BEARING_RING_POSITION")
    check("cli_topology_exit", code == 0, error or "exit 0")
    check("cli_topology_rank", payload.get("empirical_familiarity_state") == "KNOWN_SLOT_TOPOLOGY_ONLY" and payload.get("empirical_familiarity_rank") == 6 and payload.get("recipe_support_tier") == "ADDRESS_FULL_FORMULA_ONLY", str(payload))
    code, payload, error = cli("zxqv", "PICTURED_PLANT")
    check("cli_whole_exit", code == 0, error or "exit 0")
    check("cli_whole_rank", payload.get("empirical_familiarity_state") == "WHOLE_NAME_DEFAULT" and payload.get("empirical_familiarity_rank") == 7 and payload.get("working_reading_de") == "[PFLANZENNAME:zxqv]", str(payload))
    code, payload, error = cli("oiil", "PICTURED_PLANT")
    check("cli_exact_exit", code == 0, error or "exit 0")
    check("cli_exact_rank", payload.get("empirical_familiarity_state") == "EXACT_LABEL_CARD" and payload.get("empirical_familiarity_rank") == 0 and payload.get("intake_action") == "REUSE_EXACT_LABEL_CARD", str(payload))

    check("result_status", result["status"] == "EMPIRICAL_FUNCTION_TEMPLATES_READY__FAMILY_MARKERS_REMAIN_CORE_SENSITIVE", result["status"])
    check("result_surface_counts", result["source_pattern_count"] == 89 and result["surface_template_count"] == 71 and result["surface_template_state_counts"] == dict(sorted(surface_states.items())) and result["source_assignment_state_counts"] == dict(sorted(assignment_states.items())), str(result))
    check("result_recurrence", result["recurrent_surface_template_count"] == 14 and result["recurrent_surface_template_source_count"] == 32 and result["cross_owner_function_template_count"] == 4 and result["cross_owner_function_template_source_count"] == 11 and result["cross_page_function_template_count"] == 7 and result["cross_page_function_template_source_count"] == 18, str(result))
    check("result_component_counts", result["component_template_count"] == 69 and result["recurrent_component_template_count"] == 15 and result["recurrent_component_template_source_count"] == 35 and result["alternate_rendering_component_template_count"] == 2 and result["alternate_rendering_component_source_count"] == 5, str(result))
    check("result_topology_counts", result["slot_topology_count"] == 16 and result["recurrent_slot_topology_count"] == 13 and result["recurrent_slot_topology_source_count"] == 86, str(result))
    check("result_mutations", result["mutation_replay_count"] == result["mutation_replay_pass_count"] == result["function_template_stable_count"] == 89 and result["route_stable_count"] == 88, str(result))
    check("result_family_counts", result["source_family_marker_probe_count"] == 30 and result["mutation_any_family_marker_probe_count"] == 19 and result["source_family_marker_exact_trace_retained_count"] == 15 and result["family_marker_trace_stable_count"] == 74 and result["family_marker_trace_changed_count"] == 15, str(result))
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
