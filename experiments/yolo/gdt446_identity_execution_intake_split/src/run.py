#!/usr/bin/env python3
"""Build the identity/execution split and its metamorphic correction audit."""

from __future__ import annotations

import csv
import importlib.util
import json
from collections import Counter
from pathlib import Path


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
BASE = ROOT / "experiments/yolo/gdt446_identity_execution_intake_split"
OUT = BASE / "artifacts"
CERTIFIER_PATH = BASE / "src/intake_certificate_v2.py"
CATALOG = ROOT / "experiments/yolo/gdt434_forty_nine_card_intake_reader/artifacts/gdt434_1563_recipe_intake_catalog.tsv"
CURRENT = ROOT / "experiments/yolo/gdt445_prospective_intake_certificate/artifacts/gdt445_4576_current_intake_certificates.tsv"
CANDIDATES = ROOT / "experiments/yolo/gdt445_prospective_intake_certificate/artifacts/gdt445_4938_candidate_intake_certificates.tsv"
PROBES = ROOT / "experiments/yolo/gdt445_prospective_intake_certificate/artifacts/gdt445_1468_mechanism_probe_certificates.tsv"
CLOSE_MATRIX = ROOT / "experiments/yolo/gdt443_close_context_rescue_atlas/artifacts/gdt443_936_close_context_rescue_matrix.tsv"
SEPARATOR_MATRIX = ROOT / "experiments/yolo/gdt444_focus_separated_action_pair_atlas/artifacts/gdt444_484_focus_separated_pair_matrix.tsv"


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: list[dict[str, object]]) -> None:
    if not rows:
        raise ValueError(f"Refusing to write empty table {path}")
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def gate_from_row(row: dict[str, str]) -> dict[str, str]:
    return {
        field: row[field]
        for field in (
            "factor_gate_status", "scope_selector_rules", "portable_factor_rules",
            "amber_factor_rules", "blocked_factor_rules",
        )
    }


def compact(source: dict[str, str], certificate: dict[str, object], prefix: dict[str, object]) -> dict[str, object]:
    return {
        **prefix,
        "component_recipe": certificate["component_recipe"],
        "catalog_intake_tier": certificate["catalog_intake_tier"],
        "identity_route": certificate["identity_route"],
        "identity_status": certificate["identity_status"],
        "factor_gate_status": certificate["factor_gate_status"],
        "execution_route": certificate["execution_route"],
        "execution_decision": certificate["execution_decision"],
        "incoming_action": certificate["incoming_action"],
        "incoming_argument": certificate["incoming_argument"],
        "scope_context_mode": certificate["scope_context_mode"],
        "scope_incoming_action": certificate["scope_incoming_action"],
        "visible_separated_chains": certificate["visible_separated_chains"],
        "portable_factor_rules": certificate["portable_factor_rules"],
        "amber_factor_rules": certificate["amber_factor_rules"],
        "blocked_factor_rules": certificate["blocked_factor_rules"],
        "outgoing_action_v2": certificate["outgoing_action_v2"],
        "outgoing_argument_v2": certificate["outgoing_argument_v2"],
        "execution_stop_preserves_state": certificate["execution_stop_preserves_state"],
        "identity_only_when_execution_stops": certificate["identity_only_when_execution_stops"],
        "legacy_gdt445_route": source.get("primary_intake_route", certificate["legacy_gdt445_route"]),
        "legacy_gdt445_decision": source.get("certificate_decision", certificate["legacy_gdt445_decision"]),
        "gdt445_correction": certificate["gdt445_correction"],
        "identity_does_not_override_execution": certificate["identity_does_not_override_execution"],
    }


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    certifier = load_module("gdt446_split_certificate", CERTIFIER_PATH)

    catalog_rows: list[dict[str, object]] = []
    for index, source in enumerate(read_tsv(CATALOG), start=1):
        cert = certifier.issue_split_certificate(source["component_recipe"])
        catalog_rows.append(compact(source, cert, {
            "catalog_row_id": f"G446-CAT-{index:04d}",
            "source_catalog_tier": source["intake_tier"],
        }))
    write_tsv(OUT / "gdt446_1563_catalog_identity_execution.tsv", catalog_rows)

    current_rows: list[dict[str, object]] = []
    for index, source in enumerate(read_tsv(CURRENT), start=1):
        cert = certifier.issue_split_certificate(
            source["component_recipe"],
            source["incoming_action"],
            source["incoming_argument"],
            precomputed_gate=gate_from_row(source),
        )
        row = compact(source, cert, {
            "current_row_id": f"G446-CUR-{index:04d}",
            "event_id": source["event_id"],
            "physical_page": source["physical_page"],
            "statement_id": source["statement_id"],
            "surface": source["surface"],
        })
        row["source_action_after"] = source["source_action_after"]
        row["source_argument_after"] = source["source_argument_after"]
        row["state_transition_match"] = "YES" if (
            cert["outgoing_action_v2"] == source["source_action_after"]
            and cert["outgoing_argument_v2"] == source["source_argument_after"]
        ) else "NO"
        current_rows.append(row)
    write_tsv(OUT / "gdt446_4576_current_identity_execution.tsv", current_rows)

    candidate_rows: list[dict[str, object]] = []
    for index, source in enumerate(read_tsv(CANDIDATES), start=1):
        cert = certifier.issue_split_certificate(source["component_recipe"], precomputed_gate=gate_from_row(source))
        candidate_rows.append(compact(source, cert, {
            "candidate_row_id": f"G446-CAN-{index:04d}",
            "current_status": source["current_status"],
            "source_neighbor_count": source["source_neighbor_count"],
        }))
    write_tsv(OUT / "gdt446_4938_candidate_identity_execution.tsv", candidate_rows)

    probe_rows: list[dict[str, object]] = []
    for index, source in enumerate(read_tsv(PROBES), start=1):
        scope = source["scope_incoming_action"]
        scope_value = None if scope == "AUTO" else scope
        cert = certifier.issue_split_certificate(
            source["component_recipe"],
            source["incoming_action"],
            source["incoming_argument"],
            scope_value,
            source["next_visible_recipe"],
            gate_from_row(source),
        )
        probe_rows.append(compact(source, cert, {
            "probe_row_id": f"G446-PRO-{index:04d}",
            "probe_id": source["probe_id"],
            "probe_family": source["probe_family"],
            "probe_matches_source_gate": "YES" if cert["factor_gate_status"] == source["expected_gate_status"] and cert["blocked_factor_rules"] == source["expected_blocked_rules"] else "NO",
        }))
    write_tsv(OUT / "gdt446_1468_probe_identity_execution.tsv", probe_rows)

    transformations: list[dict[str, object]] = []
    for index, source in enumerate(read_tsv(SEPARATOR_MATRIX), start=1):
        if source["separated_factor_gate_status"] == "STOP__UNLICENSED_FACTOR":
            continue
        original = certifier.issue_split_certificate(source["separated_recipe"])
        stripped_recipe = f"{source['left_action']}+{source['right_action']}"
        transformed = certifier.issue_split_certificate(stripped_recipe)
        transformations.append({
            "transformation_id": f"G446-DEL-{index:04d}",
            "transformation_family": "DELETE_VISIBLE_FOCUS_SEPARATOR",
            "source_recipe": source["separated_recipe"],
            "source_identity_route": original["identity_route"],
            "source_execution_route": original["execution_route"],
            "source_execution_decision": original["execution_decision"],
            "transformed_recipe": stripped_recipe,
            "transformed_identity_route": transformed["identity_route"],
            "transformed_execution_route": transformed["execution_route"],
            "transformed_execution_decision": transformed["execution_decision"],
            "transformed_blocked_rules": transformed["blocked_factor_rules"],
            "expected_change": f"STOP_ON_PAIR:{source['direct_pair']}",
            "transformation_pass": "YES" if transformed["execution_decision"] == "STOP" and transformed["blocked_factor_rules"] == f"PAIR:{source['direct_pair']}" else "NO",
            "state_preserved": transformed["execution_stop_preserves_state"],
            "identity_override_used": "NO",
        })
    close_index = 0
    for source in read_tsv(CLOSE_MATRIX):
        if source["factor_gate_status"] == "STOP__UNLICENSED_FACTOR":
            continue
        close_index += 1
        original = certifier.issue_split_certificate(
            source["candidate_recipe"], source["incoming_semantic_action"], "NONE", source["incoming_scope_action"]
        )
        transformed = certifier.issue_split_certificate(source["candidate_recipe"])
        transformations.append({
            "transformation_id": f"G446-HEAD-{close_index:04d}",
            "transformation_family": "REMOVE_INHERITED_ACTION_HEAD",
            "source_recipe": source["candidate_recipe"],
            "source_identity_route": original["identity_route"],
            "source_execution_route": original["execution_route"],
            "source_execution_decision": original["execution_decision"],
            "transformed_recipe": source["candidate_recipe"],
            "transformed_identity_route": transformed["identity_route"],
            "transformed_execution_route": transformed["execution_route"],
            "transformed_execution_decision": transformed["execution_decision"],
            "transformed_blocked_rules": transformed["blocked_factor_rules"],
            "expected_change": "STOP_ON_CLOSE:NO_ACTIVE_ACTION",
            "transformation_pass": "YES" if transformed["execution_decision"] == "STOP" and "CLOSE:NO_ACTIVE_ACTION" in str(transformed["blocked_factor_rules"]).split("|") else "NO",
            "state_preserved": transformed["execution_stop_preserves_state"],
            "identity_override_used": "NO",
        })
    write_tsv(OUT / "gdt446_1405_route_change_transformations.tsv", transformations)

    corrections: list[dict[str, object]] = []
    for dataset, rows, id_field in (
        ("CURRENT", current_rows, "current_row_id"),
        ("CANDIDATE", candidate_rows, "candidate_row_id"),
        ("PROBE", probe_rows, "probe_row_id"),
    ):
        for row in rows:
            if row["legacy_gdt445_decision"] == row["execution_decision"]:
                continue
            corrections.append({
                "correction_id": f"G446-FIX-{len(corrections) + 1:03d}",
                "dataset": dataset,
                "source_row_id": row[id_field],
                "component_recipe": row["component_recipe"],
                "catalog_intake_tier": row["catalog_intake_tier"],
                "identity_route": row["identity_route"],
                "factor_gate_status": row["factor_gate_status"],
                "blocked_factor_rules": row["blocked_factor_rules"],
                "legacy_gdt445_route": row["legacy_gdt445_route"],
                "legacy_gdt445_decision": row["legacy_gdt445_decision"],
                "corrected_execution_route": row["execution_route"],
                "corrected_execution_decision": row["execution_decision"],
                "correction_reason": "IDENTITY_CANNOT_OVERRIDE_FACTOR_EXECUTION",
            })
    write_tsv(OUT / "gdt446_73_gdt445_decision_corrections.tsv", corrections)

    result = {
        "status": "IDENTITY_AND_EXECUTION_SPLIT__ELEVEN_FALSE_EXECUTIONS_STOPPED",
        "catalog_key_count": len(catalog_rows),
        "catalog_identity_tier_counts": dict(sorted(Counter(row["identity_route"] for row in catalog_rows).items())),
        "catalog_execution_counts": dict(sorted(Counter(row["execution_decision"] for row in catalog_rows).items())),
        "catalog_neutral_context_stop_count": sum(row["execution_decision"] == "STOP" for row in catalog_rows),
        "catalog_observed_missing_head_stop_count": sum(row["source_catalog_tier"] == "T0_EXACT_OBSERVED" and row["execution_decision"] == "STOP" for row in catalog_rows),
        "catalog_narrow_stop_count": sum(row["source_catalog_tier"] == "T4_NARROW_APPENDIX" and row["execution_decision"] == "STOP" for row in catalog_rows),
        "current_event_count": len(current_rows),
        "current_green_count": sum(row["execution_decision"] == "READ" for row in current_rows),
        "current_amber_count": sum(row["execution_decision"] == "READ_AMBER" for row in current_rows),
        "current_stop_count": sum(row["execution_decision"] == "STOP" for row in current_rows),
        "current_state_match_count": sum(row["state_transition_match"] == "YES" for row in current_rows),
        "candidate_count": len(candidate_rows),
        "candidate_execution_counts": dict(sorted(Counter(row["execution_decision"] for row in candidate_rows).items())),
        "candidate_absent_execution_counts": dict(sorted(Counter(row["execution_decision"] for row in candidate_rows if row["current_status"] == "ABSENT").items())),
        "probe_count": len(probe_rows),
        "probe_execution_counts": dict(sorted(Counter(row["execution_decision"] for row in probe_rows).items())),
        "transformation_count": len(transformations),
        "transformation_pass_count": sum(row["transformation_pass"] == "YES" for row in transformations),
        "separator_deletion_count": sum(row["transformation_family"] == "DELETE_VISIBLE_FOCUS_SEPARATOR" for row in transformations),
        "head_removal_count": sum(row["transformation_family"] == "REMOVE_INHERITED_ACTION_HEAD" for row in transformations),
        "legacy_decision_correction_count": len(corrections),
        "legacy_read_to_amber_count": sum(row["legacy_gdt445_decision"] == "READ" and row["corrected_execution_decision"] == "READ_AMBER" for row in corrections),
        "legacy_read_to_stop_count": sum(row["legacy_gdt445_decision"] == "READ" and row["corrected_execution_decision"] == "STOP" for row in corrections),
        "meaning_revisions": 0,
        "surface_predictions": 0,
        "occurrence_predictions": 0,
        "new_pages": 0,
    }
    (OUT / "gdt446_result.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
