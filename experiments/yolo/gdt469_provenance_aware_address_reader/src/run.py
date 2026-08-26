#!/usr/bin/env python3
"""Build and replay the provenance-aware GDT469 address reader."""

from __future__ import annotations

import csv
import json
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
G466 = ROOT / "experiments/yolo/gdt466_future_address_mixed_dictionary_intake"
G467 = ROOT / "experiments/yolo/gdt467_bounded_shell_composition_atlas"
G468 = ROOT / "experiments/yolo/gdt468_shell_recipe_carrier_support_atlas"
sys.path.insert(0, str(G466 / "src"))
sys.path.insert(0, str(BASE / "src"))

from intake_lib import intake, read_tsv, select_function_channels  # noqa: E402
from support_lib import supported_intake  # noqa: E402


def write_tsv(path: Path, rows: list[dict[str, object]]) -> None:
    if not rows:
        raise ValueError(f"Refusing to write empty table: {path}")
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    rules = read_tsv(G466 / "artifacts/gdt466_44_function_channel_deck.tsv")
    families = read_tsv(G466 / "artifacts/gdt466_18_owner_family_channel_deck.tsv")
    labels = read_tsv(G466 / "artifacts/gdt466_107_intake_dictionary.tsv")
    recipes = read_tsv(G468 / "artifacts/gdt468_2300_recipe_support_atlas.tsv")
    supported_shells = read_tsv(G468 / "artifacts/gdt468_2760_supported_shell_phrasebook.tsv")
    shell_probes = read_tsv(G467 / "artifacts/gdt467_8280_multicore_precedence_probes.tsv")
    branch_probes = read_tsv(G466 / "artifacts/gdt466_81_channel_and_fallback_probes.tsv")
    exact_map = {row["surface"]: row for row in labels}
    recipe_map = {row["flattened_recipe_trace"]: row for row in recipes}
    shell_map = {row["exact_channel_signature"]: row for row in supported_shells}

    def read(surface: str, content_class: str, use_exact: bool = True) -> dict[str, object]:
        return supported_intake(
            surface, content_class, rules, families, exact_map if use_exact else {}, recipe_map, shell_map,
            intake, select_function_channels,
        )

    exact_rows: list[dict[str, object]] = []
    for ordinal, label in enumerate(labels, start=1):
        observed = read(label["surface"], label["content_class"])
        exact_rows.append({
            "replay_id": f"G469-E{ordinal:03d}", "surface": label["surface"], "content_class": label["content_class"],
            "observed_route": observed["route"], "observed_reading_de": observed["reading_de"],
            "source_reading_de": label["revised_short_default_de"], "ordered_recipe_trace": observed["ordered_recipe_trace"],
            "recipe_support_tier": observed["recipe_support_tier"], "recipe_support_rank": observed["recipe_support_rank"],
            "running_event_count": observed["running_event_count"], "running_page_count": observed["running_page_count"],
            "bounded_shell_match": observed["bounded_shell_match"],
            "replay_pass": "YES" if observed["route"] == "EXACT_KNOWN_LABEL" and observed["reading_de"] == label["revised_short_default_de"] else "NO",
        })
    write_tsv(OUT / "gdt469_107_exact_supported_replay.tsv", exact_rows)

    supported_shell_by_id = {row["shell_id"]: row for row in supported_shells}
    shell_rows: list[dict[str, object]] = []
    for ordinal, probe in enumerate(shell_probes, start=1):
        expected = supported_shell_by_id[probe["shell_id"]]
        observed = read(probe["synthetic_surface"], "PICTURED_PLANT", use_exact=False)
        passed = (
            observed["bounded_shell_id"] == expected["shell_id"]
            and observed["recipe_support_tier"] == expected["support_tier"]
            and observed["recipe_support_rank"] == int(expected["support_rank"])
            and observed["exact_channel_signature"] == expected["exact_channel_signature"]
            and observed["reading_de"] == probe["observed_reading_de"]
        )
        shell_rows.append({
            "replay_id": f"G469-S{ordinal:05d}", "source_probe_id": probe["probe_id"], "shell_id": probe["shell_id"],
            "synthetic_surface": probe["synthetic_surface"], "expected_channel_signature": expected["exact_channel_signature"],
            "observed_channel_signature": observed["exact_channel_signature"], "expected_support_tier": expected["support_tier"],
            "observed_support_tier": observed["recipe_support_tier"], "expected_support_rank": expected["support_rank"],
            "observed_support_rank": observed["recipe_support_rank"], "running_event_count": observed["running_event_count"],
            "running_page_count": observed["running_page_count"], "address_full_formula_count": observed["address_full_formula_count"],
            "address_hybrid_shell_count": observed["address_hybrid_shell_count"], "observed_reading_de": observed["reading_de"],
            "replay_pass": "YES" if passed else "NO",
        })
    write_tsv(OUT / "gdt469_8280_supported_shell_replay.tsv", shell_rows)

    branch_rows: list[dict[str, object]] = []
    for ordinal, probe in enumerate(branch_probes, start=1):
        observed = read(probe["surface"], probe["content_class"], use_exact=False)
        branch_rows.append({
            "replay_id": f"G469-B{ordinal:03d}", "source_probe_id": probe["probe_id"], "probe_kind": probe["probe_kind"],
            "surface": probe["surface"], "content_class": probe["content_class"], "expected_route": probe["observed_route"],
            "observed_route": observed["route"], "recipe_support_tier": observed["recipe_support_tier"],
            "bounded_shell_match": observed["bounded_shell_match"], "bounded_shell_id": observed["bounded_shell_id"],
            "ordered_recipe_trace": observed["ordered_recipe_trace"], "observed_reading_de": observed["reading_de"],
            "replay_pass": "YES" if observed["route"] == probe["observed_route"] else "NO",
        })
    write_tsv(OUT / "gdt469_81_supported_branch_replay.tsv", branch_rows)

    contract = {
        "status": "PROVENANCE_AWARE_ADDRESS_INTAKE_READY",
        "base_precedence": "GDT466_EXACT_THEN_FUNCTION_THEN_FAMILY_THEN_WHOLE_NAME",
        "provenance_order": ["RUNNING_EXACT_RECIPE", "ADDRESS_FULL_FORMULA_ONLY", "ADDRESS_HYBRID_SHELL_ONLY", "COMPOSITION_ONLY", "OUTSIDE_BOUNDED_SHELL_ATLAS"],
        "returned_identity_channels": ["surface", "route", "reading_de", "exact_channel_signature", "ordered_recipe_trace", "recipe_support_tier", "bounded_shell_id"],
        "cli": "python3 experiments/yolo/gdt469_provenance_aware_address_reader/src/read_supported_address.py SURFACE CONTENT_CLASS",
        "claim_boundary": "Support provenance changes confidence labels only; it never changes the GDT466 working reading or predicts a surface occurrence.",
    }
    (OUT / "gdt469_supported_intake_contract.json").write_text(json.dumps(contract, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    exact_tiers = Counter(row["recipe_support_tier"] for row in exact_rows)
    shell_tiers = Counter(row["observed_support_tier"] for row in shell_rows)
    branch_tiers = Counter(row["recipe_support_tier"] for row in branch_rows)
    result = {
        "status": "PROVENANCE_AWARE_ADDRESS_INTAKE_READY",
        "exact_label_replay_count": len(exact_rows), "exact_label_replay_pass_count": sum(row["replay_pass"] == "YES" for row in exact_rows),
        "exact_label_recipe_support_tier_counts": dict(sorted(exact_tiers.items())),
        "bounded_shell_replay_count": len(shell_rows), "bounded_shell_replay_pass_count": sum(row["replay_pass"] == "YES" for row in shell_rows),
        "bounded_shell_support_tier_counts": dict(sorted(shell_tiers.items())),
        "branch_replay_count": len(branch_rows), "branch_replay_pass_count": sum(row["replay_pass"] == "YES" for row in branch_rows),
        "branch_recipe_support_tier_counts": dict(sorted(branch_tiers.items())),
        "new_pages": 0, "new_channels": 0, "new_component_meanings": 0, "surface_predictions": 0, "confirmed_lexemes": 0,
    }
    (OUT / "gdt469_result.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
