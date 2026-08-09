#!/usr/bin/env python3
"""Independent reconstruction of the public y.q/qo overlap correction."""

from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path

BASE = Path(__file__).resolve().parent
RES = BASE / "results"
INTERLINEAR = RES / "pre_grounding_interlinear.tsv"
IMPACT = RES / "source_separator_formal_impact.json"
METHOD = BASE / "SOURCE_HARD_EDGE_PUBLIC_BOUNDARY_OVERLAP_METHOD.md"
PRODUCER = BASE / "audit_source_hard_edge_public_boundary_overlap.py"
RESULT = RES / "source_hard_edge_public_boundary_overlap.json"
REPORT = RES / "source_hard_edge_public_boundary_overlap_report.md"
OUT = RES / "source_hard_edge_public_boundary_overlap_validation.json"
OUT_REPORT = RES / "source_hard_edge_public_boundary_overlap_validation_report.md"
TYPES = ("BOUND_D>Q_BARE","BOUND_D>Q_BOUND_D","BOUND_D>Q_BOUND_E","BOUND_D>Q_REL_I","BOUND_E>Q_BARE","BOUND_E>Q_BOUND_E")
READINGS = ("ZL3b", "IT2a", "RF1b")


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def update(c: Counter[str], left: str, right: str) -> None:
    tests = {
        "edges": True,
        "left_ends_y": left[-1] == "y",
        "right_starts_q": right[0] == "q",
        "right_starts_qo": right.startswith("qo"),
        "literal_y_q": left[-1] == "y" and right[0] == "q",
        "literal_y_qo": left[-1] == "y" and right.startswith("qo"),
        "literal_dy_or_ey_qo": left[-2:] in {"dy", "ey"} and right.startswith("qo"),
    }
    for name, passed in tests.items():
        c[name] += int(passed)


def encoded(c: Counter[str]) -> dict[str, int | float]:
    keys = ("edges","left_ends_y","right_starts_q","right_starts_qo","literal_y_q","literal_y_qo","literal_dy_or_ey_qo")
    out: dict[str, int | float] = {key: c[key] for key in keys}
    for key in keys[1:]:
        out[key + "_fraction"] = c[key] / c["edges"] if c["edges"] else 0.0
    return out


def main() -> None:
    if OUT.exists() or OUT_REPORT.exists():
        raise SystemExit("refusing overwrite")
    checks = 0
    def check(condition: bool, label: str) -> None:
        nonlocal checks
        checks += 1
        if not condition:
            raise AssertionError(label)
    check(sha(INTERLINEAR) == "8052a51fa37ad467e754be39648336ec4014442dab5e223daab2e77efaba4a43", "interlinear hash")
    check(sha(IMPACT) == "3db3e606b8e86756adea25a90aaeb4e7e6bce1bb22e66ecd8462ada433a8e797", "impact hash")
    result = json.loads(RESULT.read_text(encoding="utf-8"))
    impact = json.loads(IMPACT.read_text(encoding="utf-8"))
    skips = {(x["edition"],x["locus"],x["registered_edge"]) for x in impact["formal_adjacency_correction"]["skipped_registered_edge_examples"]}
    check(len(skips) == 6, "skip count")
    total: Counter[str] = Counter(); direct: Counter[str] = Counter()
    type_total = defaultdict(Counter); type_direct = defaultdict(Counter)
    reading_total = defaultdict(Counter); reading_direct = defaultdict(Counter)
    last = Counter(); first2 = Counter(); pair2 = Counter(); seen = set()
    rows = list(csv.DictReader(INTERLINEAR.open(encoding="utf-8", newline=""), delimiter="\t"))
    check(len(rows) == 15_960, "row count")
    for row in rows:
        nodes = [part.partition("=")[0] for part in row["formal_interlinear"].split(" | ")] if row["formal_interlinear"] else []
        for edge in [part for part in row["confirmed_edges"].split(";") if part]:
            coord, kind = edge.split(":", 1)
            a, b = (int(part[1:]) - 1 for part in coord.split(">"))
            check(kind in TYPES and b == a + 1 and b < len(nodes), "edge binding")
            key = row["edition"], row["locus"], edge
            check(key not in seen, "edge unique"); seen.add(key)
            left, right = nodes[a], nodes[b]
            update(total,left,right); update(type_total[kind],left,right); update(reading_total[row["edition"]],left,right)
            last[left[-1]] += 1; first2[right[:2]] += 1; pair2[left[-2:] + "|" + right[:2]] += 1
            if key not in skips:
                update(direct,left,right); update(type_direct[kind],left,right); update(reading_direct[row["edition"]],left,right)
    check(encoded(total) == result["all_registered_edges"], "all summary")
    check(encoded(direct) == result["direct_adjacent_source_group_edges"], "direct summary")
    check({k:encoded(type_total[k]) for k in TYPES} == result["by_edge_type_all"], "type all")
    check({k:encoded(type_direct[k]) for k in TYPES} == result["by_edge_type_direct"], "type direct")
    check({k:encoded(reading_total[k]) for k in READINGS} == result["by_reading_all"], "reading all")
    check({k:encoded(reading_direct[k]) for k in READINGS} == result["by_reading_direct"], "reading direct")
    check(result["surface_inventory"] == {"left_final_character_counts":dict(sorted(last.items())),"right_initial_two_character_counts":dict(sorted(first2.items())),"left_final_two_to_right_initial_two_counts":dict(sorted(pair2.items()))}, "inventory")
    check((total["edges"],direct["edges"],direct["literal_y_q"],direct["right_starts_qo"],direct["literal_dy_or_ey_qo"]) == (4737,4731,4247,4564,4095), "exact headline")
    check(all(type_direct[k]["literal_y_q"] * 2 > type_direct[k]["edges"] for k in TYPES), "all type majority")
    check(result["inputs"] == {path.name:sha(path) for path in (INTERLINEAR,IMPACT,METHOD,PRODUCER)}, "input bindings")
    check(result["status"] == "PASS_PUBLIC_Y_Q_DOMINANCE_RECLASSIFICATION", "status")
    check(result["decision"] == "DEMOTE_HARD_EDGE_NOVELTY_RETAIN_SOURCE_SAFE_CONDITIONAL_ROLE_PARTITION", "decision")
    check(result["gates"]["english_lexical_gloss_assigned"] is False and all(v for k,v in result["gates"].items() if k != "english_lexical_gloss_assigned"), "gates")
    check("not a newly\ndiscovered syntax" in REPORT.read_text(encoding="utf-8"), "report conclusion")
    check(encoded(Counter({**direct,"literal_y_q":direct["literal_y_q"]-1})) != result["direct_adjacent_source_group_edges"], "count mutation")
    check(("ZL3b","f0.0","W1>W2:BOUND_D>Q_BARE") not in skips, "skip mutation")
    check("plaintext" in result["claim_ceiling"] and "translation" in result["claim_ceiling"], "claim ceiling")
    validation = {
        "experiment": "SOURCE_HARD_EDGE_PUBLIC_BOUNDARY_OVERLAP_VALIDATION",
        "status": "PASS_INDEPENDENT_4737_EDGE_PUBLIC_OVERLAP_RECONSTRUCTION",
        "checks": checks,
        "inputs": {p.name:sha(p) for p in (INTERLINEAR,IMPACT,METHOD,PRODUCER,RESULT,REPORT,Path(__file__).resolve())},
        "headline": {"all_edges":4737,"direct_edges":4731,"direct_literal_y_q":4247,"direct_right_qo":4564,"direct_dy_or_ey_qo":4095},
        "maximum_numeric_delta": 0.0,
        "claim_ceiling": "Validates the public-prior novelty correction only; no wordhood, syntax, sound, language, cipher, meaning, plaintext, or translation follows.",
    }
    OUT.write_text(json.dumps(validation, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    OUT_REPORT.write_text(f"""# Public hard-edge overlap validation

Status: **{validation['status']}**

Independent code reconstructs all 4,737 registered edges, the 4,731 direct
source-group subset, all six edge classes, all three alternate readings, every
surface inventory cell, the exact 4,247 `y|q`, 4,564 `qo...`, and 4,095
`(dy|ey)|qo` direct counts, gates, bindings, and mutations in **{checks}**
checks with zero numeric discrepancy.

This validates a novelty correction only. No wordhood, syntax, sound,
language, cipher, meaning, plaintext, or translation follows.
""", encoding="utf-8")
    print(json.dumps({"status":validation["status"],"checks":checks}, sort_keys=True))


if __name__ == "__main__":
    main()
