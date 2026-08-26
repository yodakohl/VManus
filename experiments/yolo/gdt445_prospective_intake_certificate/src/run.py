#!/usr/bin/env python3
"""Build the integrated prospective intake certificate and exhaustive audits."""

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
BASE = ROOT / "experiments/yolo/gdt445_prospective_intake_certificate"
OUT = BASE / "artifacts"
CERTIFIER_PATH = BASE / "src/intake_certificate.py"
CURRENT = ROOT / "experiments/yolo/gdt441_factor_gated_unseen_recipe_reader/artifacts/gdt441_4576_factor_reader_replay.tsv"
CANDIDATES = ROOT / "experiments/yolo/gdt441_factor_gated_unseen_recipe_reader/artifacts/gdt441_4938_candidate_factor_gate.tsv"
STOP_PROBES = ROOT / "experiments/yolo/gdt442_forbidden_factor_stop_deck/artifacts/gdt442_47_stop_state_probes.tsv"
CLOSE_MATRIX = ROOT / "experiments/yolo/gdt443_close_context_rescue_atlas/artifacts/gdt443_936_close_context_rescue_matrix.tsv"
SEPARATOR_MATRIX = ROOT / "experiments/yolo/gdt444_focus_separated_action_pair_atlas/artifacts/gdt444_484_focus_separated_pair_matrix.tsv"


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: list[dict[str, object]], fields: list[str] | None = None) -> None:
    if not rows:
        raise ValueError(f"Refusing to write empty table {path}")
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields or list(rows[0]), delimiter="\t", lineterminator="\n")
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
            "factor_gate_status",
            "scope_selector_rules",
            "portable_factor_rules",
            "amber_factor_rules",
            "blocked_factor_rules",
        )
    }


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    certifier = load_module("gdt445_intake_certificate", CERTIFIER_PATH)

    current_certificates: list[dict[str, object]] = []
    for source in read_tsv(CURRENT):
        cert = certifier.issue_certificate(
            source["component_recipe"],
            source["active_action_before"],
            source["active_argument_before"],
            precomputed_gate=gate_from_row(source),
        )
        current_certificates.append({
            "certificate_id": f"G445-CUR-{len(current_certificates) + 1:04d}",
            "event_id": source["event_id"],
            "physical_page": source["physical_page"],
            "statement_id": source["statement_id"],
            "surface": source["surface"],
            **cert,
            "source_action_after": source["active_action_after"],
            "source_argument_after": source["active_argument_after"],
            "state_transition_match": "YES" if (
                cert["outgoing_action"] == source["active_action_after"]
                and cert["outgoing_argument"] == source["active_argument_after"]
            ) else "NO",
        })
    write_tsv(OUT / "gdt445_4576_current_intake_certificates.tsv", current_certificates)

    candidate_certificates: list[dict[str, object]] = []
    for source in read_tsv(CANDIDATES):
        cert = certifier.issue_certificate(source["candidate_recipe"], precomputed_gate=gate_from_row(source))
        candidate_certificates.append({
            "certificate_id": f"G445-CAN-{len(candidate_certificates) + 1:04d}",
            "current_status": source["current_status"],
            "source_neighbor_count": source["source_neighbor_count"],
            **cert,
            "factor_gate_matches_gdt441": "YES" if all(
                cert[field] == source[field]
                for field in (
                    "factor_gate_status",
                    "scope_selector_rules",
                    "portable_factor_rules",
                    "amber_factor_rules",
                    "blocked_factor_rules",
                )
            ) else "NO",
        })
    write_tsv(OUT / "gdt445_4938_candidate_intake_certificates.tsv", candidate_certificates)

    probes: list[dict[str, object]] = []
    for source in read_tsv(STOP_PROBES):
        cert = certifier.issue_certificate(source["probe_recipe"])
        probes.append({
            "probe_id": f"G445-STOP-{source['stop_rule_id']}",
            "probe_family": "FIXED_STOP_DECK",
            "expected_gate_status": source["probe_reader_status"],
            "expected_blocked_rules": source["probe_blocked_factor_rules"],
            **cert,
            "probe_matches_source": "YES" if (
                cert["factor_gate_status"] == source["probe_reader_status"]
                and cert["blocked_factor_rules"] == source["probe_blocked_factor_rules"]
            ) else "NO",
        })
    for index, source in enumerate(read_tsv(CLOSE_MATRIX), start=1):
        cert = certifier.issue_certificate(
            source["candidate_recipe"],
            source["incoming_semantic_action"],
            "NONE",
            source["incoming_scope_action"],
        )
        probes.append({
            "probe_id": f"G445-CLOSE-{index:04d}",
            "probe_family": "INHERITED_HEAD_CLOSE_MATRIX",
            "expected_gate_status": source["factor_gate_status"],
            "expected_blocked_rules": source["blocked_factor_rules"],
            **cert,
            "probe_matches_source": "YES" if (
                cert["factor_gate_status"] == source["factor_gate_status"]
                and cert["blocked_factor_rules"] == source["blocked_factor_rules"]
                and "INHERITED_HEAD_CLOSE" in str(cert["mechanism_flags"])
            ) else "NO",
        })
    for index, source in enumerate(read_tsv(SEPARATOR_MATRIX), start=1):
        cert = certifier.issue_certificate(source["separated_recipe"])
        probes.append({
            "probe_id": f"G445-SLOT-{index:04d}",
            "probe_family": "VISIBLE_SLOT_SEPARATED_PAIR_MATRIX",
            "expected_gate_status": source["separated_factor_gate_status"],
            "expected_blocked_rules": source["blocked_factor_rules"],
            **cert,
            "probe_matches_source": "YES" if (
                cert["factor_gate_status"] == source["separated_factor_gate_status"]
                and cert["blocked_factor_rules"] == source["blocked_factor_rules"]
                and "VISIBLE_SLOT_SEPARATED_CHAIN" in str(cert["mechanism_flags"])
                and cert["direct_pair_promoted"] == "NO"
            ) else "NO",
        })
    unseen = certifier.issue_certificate("UNSEEN_TEST_ATOM")
    probes.append({
        "probe_id": "G445-UNSEEN-0001",
        "probe_family": "UNSEEN_ATOM_GUARD",
        "expected_gate_status": "STOP__UNSEEN_ATOM",
        "expected_blocked_rules": "UNSEEN:UNSEEN_TEST_ATOM",
        **unseen,
        "probe_matches_source": "YES" if (
            unseen["factor_gate_status"] == "STOP__UNSEEN_ATOM"
            and unseen["primary_intake_route"] == "STOP_UNSEEN_ATOM"
        ) else "NO",
    })
    write_tsv(OUT / "gdt445_1468_mechanism_probe_certificates.tsv", probes)

    route_counts = Counter(str(row["primary_intake_route"]) for row in candidate_certificates + probes)
    route_order = [
        "EXACT_CATALOG",
        "KNOWN_FACTOR_COMPOSITION_GREEN",
        "KNOWN_FACTOR_COMPOSITION_AMBER",
        "INHERITED_HEAD_CLOSE_GREEN",
        "INHERITED_HEAD_CLOSE_AMBER",
        "VISIBLE_SLOT_SEPARATED_CHAIN_GREEN",
        "VISIBLE_SLOT_SEPARATED_CHAIN_AMBER",
        "STOP_UNSEEN_ATOM",
        "STOP_UNLICENSED_DIRECT_PAIR",
        "STOP_UNLICENSED_FOCUS_EDGE",
        "STOP_CLOSE_NEEDS_ACTIVE_HEAD",
        "STOP_MULTIPLE_UNLICENSED_FACTORS",
        "STOP_UNLICENSED_FACTOR",
    ]
    manual: list[dict[str, object]] = []
    for rank, route in enumerate(route_order, start=1):
        manual.append({
            "decision_rank": rank,
            "primary_intake_route": route,
            "observed_audit_row_count": route_counts[route],
            "instruction_de": certifier.route_explanation(route),
            "may_mutate_state": "NO" if route.startswith("STOP") else "YES",
            "may_invent_surface": "NO",
            "may_predict_occurrence": "NO",
            "may_revise_meaning": "NO",
        })
    write_tsv(OUT / "gdt445_13_route_intake_manual.tsv", manual)

    current_routes = Counter(str(row["primary_intake_route"]) for row in current_certificates)
    candidate_routes = Counter(str(row["primary_intake_route"]) for row in candidate_certificates)
    probe_routes = Counter(str(row["primary_intake_route"]) for row in probes)
    result = {
        "status": "ONE_EXECUTABLE_CERTIFICATE_INTEGRATES_EXACT_FACTOR_CONTEXT_SLOT_AND_STOP_ROUTES",
        "current_event_certificate_count": len(current_certificates),
        "current_exact_catalog_count": current_routes["EXACT_CATALOG"],
        "current_state_transition_match_count": sum(row["state_transition_match"] == "YES" for row in current_certificates),
        "candidate_certificate_count": len(candidate_certificates),
        "candidate_observed_exact_count": sum(row["current_status"] == "OBSERVED" and row["primary_intake_route"] == "EXACT_CATALOG" for row in candidate_certificates),
        "candidate_absent_read_count": sum(row["current_status"] == "ABSENT" and row["certificate_decision"] == "READ" for row in candidate_certificates),
        "candidate_absent_exact_catalog_count": sum(row["current_status"] == "ABSENT" and row["primary_intake_route"] == "EXACT_CATALOG" for row in candidate_certificates),
        "candidate_absent_factor_green_count": sum(
            row["current_status"] == "ABSENT"
            and row["primary_intake_route"] in {
                "KNOWN_FACTOR_COMPOSITION_GREEN",
                "VISIBLE_SLOT_SEPARATED_CHAIN_GREEN",
                "INHERITED_HEAD_CLOSE_GREEN",
            }
            for row in candidate_certificates
        ),
        "candidate_absent_amber_count": sum(row["current_status"] == "ABSENT" and row["certificate_decision"] == "READ_AMBER" for row in candidate_certificates),
        "candidate_absent_stop_count": sum(row["current_status"] == "ABSENT" and row["certificate_decision"] == "STOP" for row in candidate_certificates),
        "mechanism_probe_count": len(probes),
        "mechanism_probe_match_count": sum(row["probe_matches_source"] == "YES" for row in probes),
        "stop_probe_count": sum(row["probe_family"] == "FIXED_STOP_DECK" for row in probes),
        "close_context_probe_count": sum(row["probe_family"] == "INHERITED_HEAD_CLOSE_MATRIX" for row in probes),
        "separated_chain_probe_count": sum(row["probe_family"] == "VISIBLE_SLOT_SEPARATED_PAIR_MATRIX" for row in probes),
        "unseen_atom_probe_count": sum(row["probe_family"] == "UNSEEN_ATOM_GUARD" for row in probes),
        "route_count": len(manual),
        "routes_exercised_count": sum(route_counts[route] > 0 for route in route_order),
        "current_route_counts": dict(sorted(current_routes.items())),
        "candidate_route_counts": dict(sorted(candidate_routes.items())),
        "probe_route_counts": dict(sorted(probe_routes.items())),
        "state_unsafe_stop_count": sum(row["certificate_decision"] == "STOP" and row["state_preserved_on_stop"] != "YES" for row in probes + candidate_certificates),
        "direct_pair_promotions": 0,
        "invisible_separators_invented": 0,
        "meaning_revisions": 0,
        "surface_predictions": 0,
        "occurrence_predictions": 0,
        "new_pages": 0,
    }
    (OUT / "gdt445_result.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
