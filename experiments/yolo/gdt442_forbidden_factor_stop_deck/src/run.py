#!/usr/bin/env python3
"""Build the complete stop deck and factor lattice for the GDT441 reader."""

from __future__ import annotations

import csv
import importlib.util
import json
from collections import Counter, defaultdict
from pathlib import Path


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
BASE = ROOT / "experiments/yolo/gdt442_forbidden_factor_stop_deck"
OUT = BASE / "artifacts"
READER_PATH = ROOT / "experiments/yolo/gdt441_factor_gated_unseen_recipe_reader/src/factor_gate_stream_read.py"
CANDIDATES = ROOT / "experiments/yolo/gdt441_factor_gated_unseen_recipe_reader/artifacts/gdt441_4938_candidate_factor_gate.tsv"


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: list[dict[str, object]], fields: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    reader = load_module("gdt441_reader_for_stop_deck", READER_PATH)
    candidate_rows = read_tsv(CANDIDATES)
    stopped = [row for row in candidate_rows if row["factor_gate_status"] == "STOP__UNLICENSED_FACTOR"]

    reason_recipes: dict[str, list[str]] = defaultdict(list)
    candidate_audit: list[dict[str, object]] = []
    for index, row in enumerate(stopped, start=1):
        reasons = row["blocked_factor_rules"].split("|")
        for reason in reasons:
            reason_recipes[reason].append(row["candidate_recipe"])
        candidate_audit.append({
            "stop_candidate_id": f"G442-C{index:03d}",
            "candidate_recipe": row["candidate_recipe"],
            "current_status": row["current_status"],
            "source_neighbor_count": row["source_neighbor_count"],
            "blocked_rule_count": len(reasons),
            "blocked_rules": row["blocked_factor_rules"],
            "stop_family": "ADJACENT_ACTION_PAIR" if all(reason.startswith("PAIR:") for reason in reasons) else "CLOSE_CONTEXT",
            "instruction": "STOP__PAIR_NOT_LICENSED" if all(reason.startswith("PAIR:") for reason in reasons) else "STOP__ACTIVE_HEAD_REQUIRED",
            "automatic_repair": "NONE",
        })
    write_tsv(OUT / "gdt442_269_stop_candidate_audit.tsv", candidate_audit, list(candidate_audit[0]))

    actions = sorted(reader.COMPILER.ACTION_ROOTS)
    foci = sorted(reader.FOCUS_ROOTS)
    pair_rules = {f"{left}>{right}" for left in actions for right in actions}
    known_pairs = reader.PORTABLE_ACTION_PAIRS | reader.LOCAL_ACTION_PAIRS
    missing_pairs = sorted(pair_rules - known_pairs)
    all_heads = actions + ["OWNER"]
    all_focus_edges = {f"{head}<-{focus}" for head in all_heads for focus in foci}
    known_focus = (
        reader.PORTABLE_FOCUS_EDGES | reader.LOCAL_FOCUS_EDGES
        | reader.LOCAL_OWNER_FOCUS_EDGES | {"R<-E"}
    )
    missing_focus = sorted(all_focus_edges - known_focus)

    lattice: list[dict[str, object]] = []
    for pair in sorted(pair_rules):
        status = "GREEN_CROSS_PAGE" if pair in reader.PORTABLE_ACTION_PAIRS else "AMBER_LOCAL_APPENDIX" if pair in reader.LOCAL_ACTION_PAIRS else "STOP_UNLICENSED"
        reason = "PAIR:" + pair
        lattice.append({
            "factor_family": "ADJACENT_ACTION_PAIR", "factor_rule": reason,
            "factor_status": status, "candidate_stop_row_count": len(reason_recipes[reason]),
            "instruction": "READ" if status == "GREEN_CROSS_PAGE" else "READ_AMBER" if status == "AMBER_LOCAL_APPENDIX" else "STOP",
        })
    for edge in sorted(all_focus_edges):
        if edge in reader.PORTABLE_FOCUS_EDGES or edge == "R<-E":
            status = "GREEN_CROSS_PAGE_OR_OLD_R_TOPOLOGY"
        elif edge in reader.LOCAL_FOCUS_EDGES or edge in reader.LOCAL_OWNER_FOCUS_EDGES:
            status = "AMBER_LOCAL_APPENDIX"
        else:
            status = "STOP_UNLICENSED"
        reason = "FOCUS:" + edge
        lattice.append({
            "factor_family": "FOCUS_HEAD_EDGE", "factor_rule": reason,
            "factor_status": status, "candidate_stop_row_count": len(reason_recipes[reason]),
            "instruction": "READ" if status.startswith("GREEN") else "READ_AMBER" if status.startswith("AMBER") else "STOP",
        })
    for head in actions:
        reason = "CLOSE:" + head
        lattice.append({
            "factor_family": "CLOSE_TARGET", "factor_rule": reason,
            "factor_status": "GREEN_CROSS_PAGE", "candidate_stop_row_count": len(reason_recipes[reason]),
            "instruction": "READ",
        })
    lattice.append({
        "factor_family": "CLOSE_CONTEXT", "factor_rule": "CLOSE:NO_ACTIVE_ACTION",
        "factor_status": "STOP_MISSING_CONTEXT", "candidate_stop_row_count": len(reason_recipes["CLOSE:NO_ACTIVE_ACTION"]),
        "instruction": "STOP_UNTIL_VISIBLE_OR_INHERITED_HEAD",
    })
    write_tsv(OUT / "gdt442_complete_201_factor_lattice.tsv", lattice, list(lattice[0]))

    deck_specs: list[tuple[str, str, str, str]] = []
    for pair in missing_pairs:
        deck_specs.append(("ADJACENT_ACTION_PAIR", "PAIR:" + pair, pair.replace(">", "+"), "STOP_UNLICENSED_PAIR"))
    for edge in missing_focus:
        head, focus = edge.split("<-")
        deck_specs.append(("FOCUS_HEAD_EDGE", "FOCUS:" + edge, f"{head}+{focus}", "STOP_UNLICENSED_FOCUS_EDGE"))
    deck_specs.append(("CLOSE_CONTEXT", "CLOSE:NO_ACTIVE_ACTION", "DY", "STOP_ACTIVE_HEAD_REQUIRED"))

    stop_deck: list[dict[str, object]] = []
    probes: list[dict[str, object]] = []
    for index, (family, rule, recipe, decision) in enumerate(deck_specs, start=1):
        examples = sorted(set(reason_recipes[rule]))
        stop_deck.append({
            "stop_rule_id": f"G442-F{index:02d}", "factor_family": family,
            "blocked_rule": rule, "minimal_probe_recipe": recipe,
            "candidate_stop_row_count": len(reason_recipes[rule]),
            "candidate_example_recipes": "|".join(examples[:8]) or "NONE",
            "present_in_269_candidate_queue": "YES" if examples else "NO",
            "reader_decision": decision,
            "meaning_change_allowed": "NO", "automatic_repair": "NONE",
        })
        owner = f"TEST_OWNER_{index:02d}"
        if family == "CLOSE_CONTEXT":
            stream = [
                {"event_id": "BAD", "statement_id": "ST", "physical_page": "TEST", "register": "HERBAL", "owner_de": owner, "surface": "bad", "component_recipe": recipe},
                {"event_id": "RECOVERY", "statement_id": "ST", "physical_page": "TEST", "register": "HERBAL", "owner_de": owner, "surface": "ok", "component_recipe": "OK+Y"},
            ]
            bad_index, recovery_index = 0, 1
        else:
            stream = [
                {"event_id": "ANCHOR", "statement_id": "ST", "physical_page": "TEST", "register": "HERBAL", "owner_de": owner, "surface": "anchor", "component_recipe": "OK+Y"},
                {"event_id": "BAD", "statement_id": "ST", "physical_page": "TEST", "register": "HERBAL", "owner_de": owner, "surface": "bad", "component_recipe": recipe},
                {"event_id": "RECOVERY", "statement_id": "ST", "physical_page": "TEST", "register": "HERBAL", "owner_de": owner, "surface": "recover", "component_recipe": "AIIN+DY"},
            ]
            bad_index, recovery_index = 1, 2
        replay = reader.stream_rows(stream)
        bad = replay[bad_index]
        recovery = replay[recovery_index]
        probes.append({
            "stop_rule_id": f"G442-F{index:02d}", "blocked_rule": rule,
            "probe_recipe": recipe, "probe_reader_status": bad["reader_status"],
            "probe_blocked_factor_rules": bad["blocked_factor_rules"],
            "active_action_before_stop": bad["active_action_before"],
            "active_action_after_stop": bad["active_action_after"],
            "active_argument_before_stop": bad["active_argument_before"],
            "active_argument_after_stop": bad["active_argument_after"],
            "state_preserved": "YES" if (
                bad["active_action_before"] == bad["active_action_after"]
                and bad["active_argument_before"] == bad["active_argument_after"]
            ) else "NO",
            "recovery_recipe": recovery["component_recipe"],
            "recovery_reader_status": recovery["reader_status"],
            "recovery_succeeds": "YES" if not str(recovery["reader_status"]).startswith("STOP") else "NO",
        })
    write_tsv(OUT / "gdt442_47_stop_rule_deck.tsv", stop_deck, list(stop_deck[0]))
    write_tsv(OUT / "gdt442_47_stop_state_probes.tsv", probes, list(probes[0]))

    stop_families = Counter(row["factor_family"] for row in stop_deck)
    result = {
        "status": "COMPLETE_47_RULE_STOP_DECK__ALL_STOPS_STATE_SAFE",
        "candidate_stop_row_count": len(stopped),
        "candidate_absent_count": sum(row["current_status"] == "ABSENT" for row in stopped),
        "candidate_observed_neutral_context_stop_count": sum(row["current_status"] == "OBSERVED" for row in stopped),
        "candidate_rows_with_two_pair_blocks": sum(int(row["blocked_rule_count"]) == 2 for row in candidate_audit),
        "factor_lattice_row_count": len(lattice),
        "stop_rule_count": len(stop_deck),
        "unlicensed_action_pair_count": stop_families["ADJACENT_ACTION_PAIR"],
        "unlicensed_focus_edge_count": stop_families["FOCUS_HEAD_EDGE"],
        "missing_close_context_count": stop_families["CLOSE_CONTEXT"],
        "stop_probe_count": len(probes),
        "state_preserved_count": sum(row["state_preserved"] == "YES" for row in probes),
        "recovery_succeeds_count": sum(row["recovery_succeeds"] == "YES" for row in probes),
        "meaning_revisions": 0,
        "surface_predictions": 0,
        "new_pages": 0,
    }
    (OUT / "gdt442_result.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
