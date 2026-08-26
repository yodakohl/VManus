#!/usr/bin/env python3
"""Validate GDT469 and verify a byte-identical deterministic rebuild."""

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
BASE = ROOT / "experiments/yolo/gdt469_provenance_aware_address_reader"
OUT = BASE / "artifacts"
RUN = BASE / "src/run.py"
READER = BASE / "src/read_supported_address.py"
G466 = ROOT / "experiments/yolo/gdt466_future_address_mixed_dictionary_intake"
G467 = ROOT / "experiments/yolo/gdt467_bounded_shell_composition_atlas"
G468 = ROOT / "experiments/yolo/gdt468_shell_recipe_carrier_support_atlas"

EXACT = OUT / "gdt469_107_exact_supported_replay.tsv"
SHELLS = OUT / "gdt469_8280_supported_shell_replay.tsv"
BRANCHES = OUT / "gdt469_81_supported_branch_replay.tsv"
CONTRACT = OUT / "gdt469_supported_intake_contract.json"
RESULT = OUT / "gdt469_result.json"
VALIDATION = OUT / "gdt469_validation.json"
GENERATED = (EXACT, SHELLS, BRANCHES, CONTRACT, RESULT)


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def cli(surface: str, content_class: str) -> tuple[int, dict[str, object], str]:
    completed = subprocess.run([sys.executable, str(READER), surface, content_class], cwd=ROOT, capture_output=True, text=True, check=False)
    return completed.returncode, json.loads(completed.stdout) if completed.stdout else {}, completed.stderr


def main() -> int:
    checks: list[dict[str, object]] = []

    def check(name: str, condition: bool, detail: str) -> None:
        checks.append({"name": name, "status": "PASS" if condition else "FAIL", "detail": detail})

    labels = read_tsv(G466 / "artifacts/gdt466_107_intake_dictionary.tsv")
    branch_source = read_tsv(G466 / "artifacts/gdt466_81_channel_and_fallback_probes.tsv")
    shell_source = read_tsv(G467 / "artifacts/gdt467_8280_multicore_precedence_probes.tsv")
    recipe_atlas = read_tsv(G468 / "artifacts/gdt468_2300_recipe_support_atlas.tsv")
    supported_shells = read_tsv(G468 / "artifacts/gdt468_2760_supported_shell_phrasebook.tsv")
    exact = read_tsv(EXACT)
    shells = read_tsv(SHELLS)
    branches = read_tsv(BRANCHES)
    contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
    result = json.loads(RESULT.read_text(encoding="utf-8"))
    recipe_map = {row["flattened_recipe_trace"]: row for row in recipe_atlas}
    shell_by_id = {row["shell_id"]: row for row in supported_shells}

    check("label_source_count", len(labels) == 107, f"observed={len(labels)}")
    check("branch_source_count", len(branch_source) == 81, f"observed={len(branch_source)}")
    check("shell_source_count", len(shell_source) == 8280, f"observed={len(shell_source)}")
    check("recipe_atlas_count", len(recipe_atlas) == 2300 and len(recipe_map) == 2300, f"observed={len(recipe_atlas)}")
    check("supported_shell_source_count", len(supported_shells) == 2760 and len(shell_by_id) == 2760, f"observed={len(supported_shells)}")

    check("exact_count", len(exact) == 107, f"observed={len(exact)}")
    check("exact_order", [row["surface"] for row in exact] == [row["surface"] for row in labels], "source order exact")
    check("exact_routes", all(row["observed_route"] == "EXACT_KNOWN_LABEL" for row in exact), "107/107")
    check("exact_readings", [row["observed_reading_de"] for row in exact] == [row["revised_short_default_de"] for row in labels] == [row["source_reading_de"] for row in exact], "all readings unchanged")
    check("exact_all_pass", all(row["replay_pass"] == "YES" for row in exact), "107/107")
    exact_tiers = Counter(row["recipe_support_tier"] for row in exact)
    check("exact_tiers", exact_tiers == Counter({"RUNNING_EXACT_RECIPE": 25, "ADDRESS_FULL_FORMULA_ONLY": 15, "ADDRESS_HYBRID_SHELL_ONLY": 16, "OUTSIDE_BOUNDED_SHELL_ATLAS": 51}), str(exact_tiers))
    exact_support_ok = True
    for row in exact:
        support = recipe_map.get(row["ordered_recipe_trace"])
        expected = support["support_tier"] if support else "OUTSIDE_BOUNDED_SHELL_ATLAS"
        exact_support_ok &= row["recipe_support_tier"] == expected and int(row["recipe_support_rank"]) == (int(support["support_rank"]) if support else 0)
    check("exact_support_join", exact_support_ok, "all recipe tiers/ranks exact")
    check("exact_cards_not_shell_rematched", all(row["bounded_shell_match"] == "NO" for row in exact), "exact card identity stays first")

    check("shell_count", len(shells) == 8280, f"observed={len(shells)}")
    check("shell_source_alignment", [row["source_probe_id"] for row in shells] == [row["probe_id"] for row in shell_source], "probe order exact")
    check("shell_ids", [row["shell_id"] for row in shells] == [row["shell_id"] for row in shell_source], "shell IDs exact")
    check("shell_channel_signatures", all(row["expected_channel_signature"] == row["observed_channel_signature"] == shell_by_id[row["shell_id"]]["exact_channel_signature"] for row in shells), "8280 exact")
    check("shell_support_tiers", all(row["expected_support_tier"] == row["observed_support_tier"] == shell_by_id[row["shell_id"]]["support_tier"] for row in shells), "8280 exact")
    check("shell_support_ranks", all(row["expected_support_rank"] == row["observed_support_rank"] == shell_by_id[row["shell_id"]]["support_rank"] for row in shells), "8280 exact")
    check("shell_readings_unchanged", [row["observed_reading_de"] for row in shells] == [row["observed_reading_de"] for row in shell_source], "GDT467 readings exact")
    check("shell_all_pass", all(row["replay_pass"] == "YES" for row in shells), "8280/8280")
    shell_tiers = Counter(row["observed_support_tier"] for row in shells)
    check("shell_tier_counts", shell_tiers == Counter({"RUNNING_EXACT_RECIPE": 315, "ADDRESS_FULL_FORMULA_ONLY": 72, "ADDRESS_HYBRID_SHELL_ONLY": 54, "COMPOSITION_ONLY": 7839}), str(shell_tiers))
    check("shell_support_metrics", all(
        row["running_event_count"] == recipe_map[shell_by_id[row["shell_id"]]["flattened_recipe_trace"]]["running_event_count"]
        and row["running_page_count"] == recipe_map[shell_by_id[row["shell_id"]]["flattened_recipe_trace"]]["running_page_count"]
        for row in shells
    ), "all running counts joined")

    check("branch_count", len(branches) == 81, f"observed={len(branches)}")
    check("branch_source_alignment", [row["source_probe_id"] for row in branches] == [row["probe_id"] for row in branch_source], "probe order exact")
    check("branch_routes_unchanged", all(row["expected_route"] == row["observed_route"] == source["observed_route"] for row, source in zip(branches, branch_source)), "81/81")
    check("branch_all_pass", all(row["replay_pass"] == "YES" for row in branches), "81/81")
    branch_tiers = Counter(row["recipe_support_tier"] for row in branches)
    check("branch_tier_counts", branch_tiers == Counter({"RUNNING_EXACT_RECIPE": 11, "ADDRESS_HYBRID_SHELL_ONLY": 4, "OUTSIDE_BOUNDED_SHELL_ATLAS": 66}), str(branch_tiers))
    check("branch_fallback", next(row for row in branches if row["probe_kind"] == "WHOLE_NAME_FALLBACK")["recipe_support_tier"] == "OUTSIDE_BOUNDED_SHELL_ATLAS", "whole fallback outside")

    check("contract_status", contract["status"] == "PROVENANCE_AWARE_ADDRESS_INTAKE_READY", contract["status"])
    check("contract_tier_order", contract["provenance_order"] == ["RUNNING_EXACT_RECIPE", "ADDRESS_FULL_FORMULA_ONLY", "ADDRESS_HYBRID_SHELL_ONLY", "COMPOSITION_ONLY", "OUTSIDE_BOUNDED_SHELL_ATLAS"], str(contract["provenance_order"]))
    check("contract_identity_channels", set(contract["returned_identity_channels"]) == {"surface", "route", "reading_de", "exact_channel_signature", "ordered_recipe_trace", "recipe_support_tier", "bounded_shell_id"}, str(contract["returned_identity_channels"]))
    check("contract_base_precedence", contract["base_precedence"] == "GDT466_EXACT_THEN_FUNCTION_THEN_FAMILY_THEN_WHOLE_NAME", contract["base_precedence"])

    code, payload, error = cli("otxainy", "STAR_BEARING_RING_POSITION")
    check("cli_supported_exit", code == 0, error or "exit 0")
    check("cli_supported_reading", payload.get("reading_de") == "DANACH · [STERNSTELLENNAME:x] · ANTEIL · POSTEN" and payload.get("bounded_shell_id") == "G467-S0234", str(payload))
    check("cli_supported_tier", payload.get("recipe_support_tier") == "ADDRESS_FULL_FORMULA_ONLY" and payload.get("recipe_support_rank") == 86 and payload.get("address_full_formula_count") == 1, str(payload))
    code, payload, error = cli("zxqv", "PICTURED_PLANT")
    check("cli_fallback_exit", code == 0, error or "exit 0")
    check("cli_fallback_reading", payload.get("reading_de") == "[PFLANZENNAME:zxqv]" and payload.get("route") == "WHOLE_LEARNED_OWNER_NAME", str(payload))
    check("cli_fallback_tier", payload.get("recipe_support_tier") == "OUTSIDE_BOUNDED_SHELL_ATLAS" and payload.get("bounded_shell_match") == "NO", str(payload))

    check("result_status", result["status"] == "PROVENANCE_AWARE_ADDRESS_INTAKE_READY", result["status"])
    check("result_exact", result["exact_label_replay_count"] == result["exact_label_replay_pass_count"] == 107 and result["exact_label_recipe_support_tier_counts"] == dict(sorted(exact_tiers.items())), str(result))
    check("result_shells", result["bounded_shell_replay_count"] == result["bounded_shell_replay_pass_count"] == 8280 and result["bounded_shell_support_tier_counts"] == dict(sorted(shell_tiers.items())), str(result))
    check("result_branches", result["branch_replay_count"] == result["branch_replay_pass_count"] == 81 and result["branch_recipe_support_tier_counts"] == dict(sorted(branch_tiers.items())), str(result))
    check("result_claim_ceiling", result["new_pages"] == result["new_channels"] == result["new_component_meanings"] == result["surface_predictions"] == result["confirmed_lexemes"] == 0, "no expanded claim")
    check("sealed_pages_absent", all(not row.get("physical_page", "").startswith("f84") for row in labels), "no sealed page rows")

    before = {path.name: sha256(path) for path in GENERATED}
    completed = subprocess.run([sys.executable, str(RUN)], cwd=ROOT, capture_output=True, text=True, check=False)
    check("deterministic_rebuild_exit", completed.returncode == 0, completed.stderr[-500:] or "exit 0")
    after = {path.name: sha256(path) for path in GENERATED}
    check("deterministic_rebuild_bytes", before == after, "all generated artifact hashes unchanged")

    passed = sum(row["status"] == "PASS" for row in checks)
    failed = len(checks) - passed
    payload = {"status": "PASS" if failed == 0 else "FAIL", "check_count": len(checks), "passed": passed, "failed": failed, "checks": checks}
    VALIDATION.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": payload["status"], "checks": len(checks), "passed": passed, "failed": failed}, ensure_ascii=False))
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
