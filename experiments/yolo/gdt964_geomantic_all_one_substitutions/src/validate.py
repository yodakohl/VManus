#!/usr/bin/env python3
"""Independent validator for GDT964's fixed Hamming-1 consequence screen."""
from __future__ import annotations

import csv
import hashlib
import itertools
import json
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve()
EXP = HERE.parents[1]
ROOT = EXP.parents[2]
ART = EXP / "artifacts"
OLD = ROOT / "experiments/yolo/gdt959_geomantic_element_remainder"
FIG = ROOT / "experiments/yolo/gdt957_f66r_complete_geomantic_margin"
ELEMENTS = ["AIR", "EARTH", "FIRE", "WATER"]
EDITIONS = ("ZL3b", "IT2a", "RF1b")


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_tsv(path: Path) -> list[dict]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def source_checks() -> tuple[list[dict], dict]:
    checks = []
    lock = load(EXP / "PREREG_LOCK.json")
    lock_errors = []
    for path, expected in lock.items():
        actual = sha(ROOT / path) if (ROOT / path).exists() else None
        if actual != expected:
            lock_errors.append({"path": path, "expected": expected, "actual": actual})
    checks.append({"name": "preregistration_lock", "ok": not lock_errors,
                   "checked": len(lock), "errors": lock_errors})
    fig = load(FIG / "src/SOURCE.json")
    figures = fig["figures"]
    fig_errors = []
    if [row["value"] for row in figures] != list(range(16)):
        fig_errors.append("figure_values")
    if len({row["name"] for row in figures}) != 16 or len({row["bits"] for row in figures}) != 16:
        fig_errors.append("figure_name_or_bit_uniqueness")
    if any(row["bits"] != format(row["value"], "04b") for row in figures):
        fig_errors.append("figure_bits")
    checks.append({"name": "gdt957_figure_key", "ok": not fig_errors,
                   "errors": fig_errors, "count": len(figures),
                   "vector_convention": fig.get("vector_convention")})
    src = load(OLD / "src/SOURCE.json")
    tables = src["tables"]
    table_errors = []
    for table in ("A", "B", "C"):
        values = tables.get(table, {}).get("elements", [])
        if len(values) != 16 or any(value not in ELEMENTS + [None] for value in values):
            table_errors.append(table)
    if src.get("uncertainty", {}).get("upper_completions") != ELEMENTS:
        table_errors.append("upper_completion_domain")
    checks.append({"name": "gdt959_element_tables", "ok": not table_errors,
                   "errors": table_errors, "tables": sorted(tables)})

    old = load(OLD / "artifacts/ALL_CANDIDATES.json")
    old_errors = []
    if len(old) != 1128:
        old_errors.append({"kind": "case_count", "actual": len(old), "expected": 1128})
    by_case = Counter(row.get("case") for row in old)
    if not all(row.get("edition") in EDITIONS for row in old):
        old_errors.append({"kind": "edition"})
    if not all(len(row.get("figures", [])) == len(row.get("names", [])) ==
               len(row.get("elements", [])) == 15 for row in old):
        old_errors.append({"kind": "record_width"})
    for row in old:
        expected_names = [figures[int(value)]["name"] for value in row["figures"]]
        expected_elements = [tables[row["table"]]["elements"][int(value)]
                             for value in row["figures"]]
        if row["names"] != expected_names or row["elements"] != expected_elements:
            old_errors.append({"kind": "source_projection", "case": row.get("case"),
                               "candidate_id": row.get("candidate_id"), "table": row.get("table")})
            if len(old_errors) > 25:
                break
    checks.append({"name": "gdt959_cases_and_source_projection", "ok": not old_errors,
                   "actual": len(old), "expected": 1128, "case_counts": dict(by_case),
                   "errors": old_errors[:25], "error_count": len(old_errors)})
    chart_rows = load(FIG / "artifacts/ALL_CASES.json")
    chart_errors = []
    chart_keys = {(row.get("edition"), row.get("direction")) for row in chart_rows}
    if chart_keys != {(edition, direction) for edition in EDITIONS for direction in
                      ("TOP_DOWN", "BOTTOM_UP")}:
        chart_errors.append({"kind": "chart_case_keys", "actual": sorted(chart_keys)})
    old_ids = defaultdict(set)
    for row in old:
        old_ids[row["case"]].add(row["candidate_id"])
    for chart in chart_rows:
        case = chart["case"]
        if old_ids[case] != set(chart.get("surviving_ids", [])):
            chart_errors.append({"kind": "chart_surviving_id_mismatch", "case": case,
                                 "old": len(old_ids[case]), "chart": len(chart.get("surviving_ids", []))})
    checks.append({"name": "gdt957_chart_direction_candidate_reconstruction", "ok": not chart_errors,
                   "actual_chart_cases": len(chart_rows), "errors": chart_errors})
    return checks, {"old_cases": len(old), "old_case_groups": len(by_case),
                    "figures": len(figures), "element_tables": sorted(tables)}


def predictions_check(old: list[dict]) -> dict:
    path = ART / "PREDICTIONS.tsv"
    if not path.exists():
        return {"name": "predictions", "ok": False, "errors": ["missing"]}
    actual = read_tsv(path)
    expected = []
    target = load(OLD / "artifacts/TARGET_RECORDS.json")
    records = {(r["edition"], int(r["position_top_down"])): r for r in target}
    for candidate in old:
        for position, (figure, name, element) in enumerate(
                zip(candidate["figures"], candidate["names"], candidate["elements"]), 1):
            record = records[(candidate["edition"], position)]
            expected.append({"case": candidate["case"], "candidate_id": str(candidate["candidate_id"]),
                             "table": candidate["table"], "position": str(position),
                             "raw": record["raw"], "raw_state": record["state"],
                             "figure": str(figure), "predicted_name": name,
                             "predicted_element": element or "UNKNOWN",
                             "old959_status": candidate["status"]})
    return {"name": "all_16920_predictions", "ok": actual == expected,
            "actual": len(actual), "expected": len(expected),
            "errors": [] if actual == expected else ["row_or_value_mismatch"]}


def expected_pairs(target: list[dict]) -> tuple[list[dict], dict[str, list[dict]]]:
    pairs, edges = [], defaultdict(list)
    for edition in EDITIONS:
        rows = sorted((r for r in target if r["edition"] == edition),
                      key=lambda r: int(r["position_top_down"]))
        if len(rows) != 15:
            raise AssertionError((edition, len(rows)))
        for left, right in itertools.combinations(rows, 2):
            raw_left, raw_right = left["raw"], right["raw"]
            differences = []
            if left["state"] != "KNOWN" or right["state"] != "KNOWN":
                status = "UNKNOWN_TARGET"
            else:
                if not raw_left or not raw_right or any(not ("a" <= char <= "z")
                                                        for char in raw_left + raw_right):
                    raise AssertionError((edition, left, right))
                differences = [index + 1 for index, (a, b) in enumerate(zip(raw_left, raw_right))
                                if a != b]
                status = "EDGE" if len(raw_left) == len(raw_right) and len(differences) == 1 else "NOT_EDGE"
            row = {"edition": edition, "position1": int(left["position_top_down"]),
                   "position2": int(right["position_top_down"]), "raw1": raw_left,
                   "raw2": raw_right, "status": status,
                   "changed_position": differences[0] if status == "EDGE" else None}
            pairs.append(row)
            if status == "EDGE":
                edges[edition].append(row)
    return pairs, edges


def pair_checks(old: list[dict]) -> tuple[list[dict], dict]:
    target = load(OLD / "artifacts/TARGET_RECORDS.json")
    expected, edges = expected_pairs(target)
    path = ART / "ALL_PAIRS.json"
    if not path.exists():
        return [{"name": "all_pairs", "ok": True, "status": "NOT_YET_EVALUATED",
                 "checked": False}], {"pairs_expected": len(expected),
                                      "edge_counts": {e: len(v) for e, v in edges.items()}}
    actual = load(path)
    checks = [{"name": "all_315_pairs", "ok": actual == expected,
               "actual": len(actual), "expected": len(expected),
               "edge_counts": {e: len(v) for e, v in edges.items()},
               "errors": [] if actual == expected else ["pair_rows_or_statuses"]}]
    return checks, {"pairs": len(actual), "edge_counts": {e: len(v) for e, v in edges.items()}}


def expected_candidates(old: list[dict], edges: dict[str, list[dict]]) -> list[dict]:
    rows = []
    for candidate in old:
        consequence = []
        for edge in edges[candidate["edition"]]:
            i, j = edge["position1"] - 1, edge["position2"] - 1
            values = [candidate["elements"][i], candidate["elements"][j]]
            conflict = None not in values and values[0] != values[1]
            consequence.append({**edge, "names": [candidate["names"][i], candidate["names"][j]],
                                "elements": values, "conflict": conflict,
                                "unknown_source": None in values})
        allowed = [value for value in ELEMENTS if consequence and all(
            len({value if element is None else element for element in edge["elements"]}) == 1
            for edge in consequence)]
        lower = bool(consequence) and all(not edge["unknown_source"] and not edge["conflict"]
                                          for edge in consequence)
        upper = bool(allowed)
        rows.append({"case": candidate["case"], "edition": candidate["edition"],
                     "direction": candidate["direction"], "candidate_id": candidate["candidate_id"],
                     "table": candidate["table"], "figures": candidate["figures"],
                     "names": candidate["names"], "elements": candidate["elements"],
                     "old959_status": candidate["status"], "edges": consequence,
                     "lower": lower, "upper": upper,
                     "allowed_source_completions": allowed,
                     "status": "NO_CAPACITY" if not consequence else
                     "COMPATIBLE_KNOWN_EDGES" if lower else "UNKNOWN_ONLY" if upper else "CONTRADICTED",
                     "unknown_target_labels": candidate["unknown_target_labels"],
                     "independent_confirmation_leaves": 0})
    return rows


def candidate_checks(old: list[dict], edges: dict[str, list[dict]]) -> tuple[list[dict], dict, list[dict]]:
    expected = expected_candidates(old, edges)
    path = ART / "ALL_CANDIDATES.json"
    if not path.exists():
        return [{"name": "all_candidate_consequences", "ok": True,
                 "status": "NOT_YET_EVALUATED", "checked": False}], {}, expected
    actual = load(path)
    ok = actual == expected
    checks = [{"name": "all_1128_candidate_consequences", "ok": ok,
               "actual": len(actual), "expected": len(expected),
               "errors": [] if ok else ["candidate_or_edge_mismatch"]}]
    return checks, {"statuses": dict(Counter(row["status"] for row in actual))}, expected


def table_and_group_checks(candidates: list[dict], edges: dict[str, list[dict]]) -> list[dict]:
    """Recreate every derived TSV and both provenance grouping files."""
    checks = []
    edge_rows = []
    candidate_rows = []
    for row in candidates:
        for edge in row["edges"]:
            i, j = edge["position1"] - 1, edge["position2"] - 1
            values = edge["elements"]
            edge_rows.append({"case": row["case"], "candidate_id": row["candidate_id"],
                              "table": row["table"], "position1": i + 1, "position2": j + 1,
                              "raw1": edge["raw1"], "raw2": edge["raw2"],
                              "changed_position": edge["changed_position"],
                              "name1": edge["names"][0], "name2": edge["names"][1],
                              "element1": values[0] or "UNKNOWN", "element2": values[1] or "UNKNOWN",
                              "explicit_conflict": edge["conflict"]})
        candidate_rows.append({"case": row["case"], "candidate_id": row["candidate_id"],
                               "table": row["table"], "old959_status": row["old959_status"],
                               "new_status": row["status"], "edge_count": len(row["edges"]),
                               "explicit_conflicts": sum(edge["conflict"] for edge in row["edges"]),
                               "source_completions": " | ".join(row["allowed_source_completions"]),
                               "predicted_names": " | ".join(row["names"]),
                               "predicted_elements": " | ".join(x or "UNKNOWN" for x in row["elements"]),
                               "independent_confirmation_leaves": 0})
    for name, expected in (("EDGE_CONSEQUENCES.tsv", edge_rows), ("CANDIDATE_TABLE.tsv", candidate_rows)):
        path = ART / name
        if not path.exists():
            checks.append({"name": name, "ok": False, "errors": ["missing"]})
            continue
        actual = read_tsv(path)
        # csv.DictReader returns strings; stringify exactly as DictWriter does.
        wanted = [{key: str(value) if value is not None else "" for key, value in row.items()}
                  for row in expected]
        checks.append({"name": name, "ok": actual == wanted, "actual": len(actual),
                       "expected": len(wanted),
                       "errors": [] if actual == wanted else ["row_or_value_mismatch"]})
    summary = []
    for case, table in sorted({(row["case"], row["table"]) for row in candidates}):
        rows = [row for row in candidates if row["case"] == case and row["table"] == table]
        summary.append({"case": case, "table": table, "candidates": len(rows),
                        "lower": sum(row["lower"] for row in rows),
                        "upper": sum(row["upper"] for row in rows),
                        "contradicted": sum(row["status"] == "CONTRADICTED" for row in rows)})
    path = ART / "SUMMARY.tsv"
    if path.exists():
        actual = read_tsv(path)
        wanted = [{key: str(value) for key, value in row.items()} for row in summary]
        checks.append({"name": "SUMMARY.tsv", "ok": actual == wanted, "actual": len(actual),
                       "expected": len(wanted), "errors": [] if actual == wanted else ["rows"]})
    else:
        checks.append({"name": "SUMMARY.tsv", "ok": False, "errors": ["missing"]})

    for kind in ("physical", "observed"):
        groups = defaultdict(list)
        for row in candidates:
            key = (tuple(row["names"]) if kind == "physical" else
                   (row["edition"], tuple((edge["position1"], edge["position2"],
                                            *edge["elements"]) for edge in row["edges"])))
            groups[repr(key)].append({"case": row["case"], "candidate_id": row["candidate_id"],
                                      "table": row["table"], "status": row["status"]})
        wanted = [{"prediction": key, "provenance": value} for key, value in sorted(groups.items())]
        path = ART / f"IDENTICAL_{kind.upper()}_PREDICTIONS.json"
        if path.exists():
            actual = load(path)
            checks.append({"name": path.name, "ok": actual == wanted, "actual": len(actual),
                           "expected": len(wanted), "errors": [] if actual == wanted else ["groups"]})
        else:
            checks.append({"name": path.name, "ok": False, "errors": ["missing"]})
    return checks


def cross_checks(expected_candidates_rows: list[dict]) -> list[dict]:
    lookup = {(row["edition"], row["direction"], row["candidate_id"], row["table"]): row
              for row in expected_candidates_rows}
    cross = []
    for row in expected_candidates_rows:
        if row["edition"] != "IT2a":
            continue
        linked = [lookup.get((edition, row["direction"], row["candidate_id"], row["table"]))
                  for edition in EDITIONS]
        common = set(ELEMENTS)
        for linked_row in linked:
            common &= set(linked_row["allowed_source_completions"]) if linked_row else set()
        cross.append({"direction": row["direction"], "candidate_id": row["candidate_id"],
                      "table": row["table"], "names": row["names"], "figures": row["figures"],
                      "all_editions_present": all(linked),
                      "lower": all(x and x["lower"] for x in linked), "upper": bool(common),
                      "common_source_completions": sorted(common),
                      "edition_statuses": {edition: (x["status"] if x else "MISSING_KEY")
                                           for edition, x in zip(EDITIONS, linked)}})
    checks = []
    path = ART / "COMPLETE_IT2A_CROSS_EDITION.json"
    if path.exists():
        actual = load(path)
        checks.append({"name": "cross_edition_table", "ok": actual == cross,
                       "actual": len(actual), "expected": len(cross),
                       "errors": [] if actual == cross else ["cross_rows"]})
    else:
        checks.append({"name": "cross_edition_table", "ok": False, "errors": ["missing"]})
    oldcross = load(OLD / "artifacts/COMPLETE_IT2A_CROSS_EDITION.json")
    old_keys = {(row["direction"], row["candidate_id"], row["table"]) for row in oldcross if row["upper"]}
    expected_previous = [row for row in cross if (row["direction"], row["candidate_id"], row["table"]) in old_keys]
    path = ART / "PREVIOUS_SEVEN.json"
    if path.exists():
        actual = load(path)
        checks.append({"name": "previous_seven", "ok": actual == expected_previous,
                       "actual": len(actual), "expected": len(expected_previous),
                       "errors": [] if actual == expected_previous else ["previous_rows"]})
    else:
        checks.append({"name": "previous_seven", "ok": False, "errors": ["missing"]})
    return checks


def result_checks(old: list[dict], pairs: list[dict], edges: dict[str, list[dict]], candidates: list[dict]) -> dict:
    path = ART / "RESULT.json"
    if not path.exists():
        return {"name": "result_aggregation", "ok": False, "errors": ["missing"]}
    result = load(path)
    expected_statuses = dict(Counter(row["status"] for row in candidates))
    expected_edges = {edition: len(edges[edition]) for edition in EDITIONS}
    expected = {"candidate_table_cases": len(candidates), "pair_cases": len(pairs),
                "edge_counts": expected_edges, "edge_consequences": sum(len(row["edges"]) for row in candidates),
                "statuses": expected_statuses, "confirmed_words": 0,
                "independent_confirmation_leaves": 0, "significance_claim": False}
    errors = [{"field": key, "actual": result.get(key), "expected": value}
              for key, value in expected.items() if result.get(key) != value]
    return {"name": "result_aggregation", "ok": not errors, "errors": errors}


def validate() -> dict:
    checks, source_summary = source_checks()
    old = load(OLD / "artifacts/ALL_CANDIDATES.json")
    checks.append(predictions_check(old))
    pair_result, pair_summary = pair_checks(old)
    checks.extend(pair_result)
    target = load(OLD / "artifacts/TARGET_RECORDS.json")
    pairs, edges = expected_pairs(target)
    candidate_result, candidate_summary, expected = candidate_checks(old, edges)
    checks.extend(candidate_result)
    if (ART / "ALL_CANDIDATES.json").exists():
        checks.extend(table_and_group_checks(expected, edges))
        checks.extend(cross_checks(expected))
    checks.append(result_checks(old, pairs, edges, expected)) if (ART / "ALL_CANDIDATES.json").exists() else None
    ok = all(check.get("ok", False) for check in checks)
    return {"experiment_id": "GDT964", "status": "VALIDATION_PASS" if ok else "VALIDATION_FAIL",
            "checks": checks, "source": source_summary, "pairs": pair_summary,
            "candidates": candidate_summary,
            "claim_ceiling": "independent computation/audit only; no semantic confirmation or meaning claim"}


def main() -> int:
    output = validate()
    ART.mkdir(parents=True, exist_ok=True)
    (ART / "VALIDATION.json").write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n",
                                           encoding="utf-8")
    print(json.dumps(output, ensure_ascii=False, indent=2))
    return 0 if output["status"] == "VALIDATION_PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
