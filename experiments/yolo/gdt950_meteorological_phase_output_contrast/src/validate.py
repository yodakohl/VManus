#!/usr/bin/env python3
"""Independent audit of the frozen GDT950 phase/output census.

The source is rebuilt directly from GDT930 SOURCE.json; run.py is not imported.
This validates mechanical consequences, never word meanings.
"""
from __future__ import annotations

import csv
import hashlib
import json
import re
from collections import defaultdict
from pathlib import Path

EXP = Path(__file__).resolve().parents[1]
ROOT = EXP.parents[2]
ED = ("ZL3b", "IT2a", "RF1b")


def load(path):
    return json.loads(path.read_text(encoding="utf-8"))


def js(value):
    return json.dumps(value, ensure_ascii=False, indent=2) + "\n"


def csv_rows(path):
    with path.open(encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh, delimiter="\t"))


def bad(errors, check, **details):
    errors.append({"check": check, **details})


def locks(errors):
    lock = load(EXP / "PREREG_LOCK.json")
    for rel, wanted in lock.get("files", {}).items():
        path = EXP / rel
        if not path.is_file():
            bad(errors, "LOCK_FILE_MISSING", file=rel)
        elif hashlib.sha256(path.read_bytes()).hexdigest() != wanted:
            bad(errors, "LOCK_HASH_MISMATCH", file=rel)
    for rel, wanted in lock.get("source_files", {}).items():
        path = ROOT / rel
        if not path.is_file():
            bad(errors, "SOURCE_LOCK_FILE_MISSING", file=rel)
        elif hashlib.sha256(path.read_bytes()).hexdigest() != wanted:
            bad(errors, "SOURCE_LOCK_HASH_MISMATCH", file=rel)


def source_census(spec, errors):
    source = ROOT / spec["source"]
    if not source.is_file():
        bad(errors, "SOURCE_MISSING", file=spec["source"])
        return {}, [], []
    groups = load(source).get("groups", [])
    allowed = set(spec["discovery_pages"]) | set(spec["additional_pages"])
    if len({g.get("source_group_id") for g in groups}) != len(groups):
        bad(errors, "DUPLICATE_SOURCE_GROUP_ID")
    if any(g.get("edition") not in ED for g in groups):
        bad(errors, "EDITION_SCOPE")
    if any(g.get("page") not in allowed for g in groups):
        bad(errors, "PAGE_SCOPE")
    if any(str(g.get("page", "")).startswith("f84") or g.get("page") == "f116v" for g in groups):
        bad(errors, "FORBIDDEN_PAGE")
    lines = defaultdict(list)
    for g in groups:
        lines[(g["edition"], g["page"], g["locus"])].append(g)
    for key, rows in lines.items():
        rows.sort(key=lambda x: int(x["source_group_index"]))
        if [int(x["source_group_index"]) for x in rows] != list(range(1, len(rows) + 1)):
            bad(errors, "LINE_INDEX_SEQUENCE", key=key)
    ordered_keys = sorted(lines, key=lambda key: (
        ED.index(key[0]), list(spec["discovery_pages"] + spec["additional_pages"]).index(key[1]),
        int(key[2].split(".")[-1])))
    cases, unresolved, complete = [], [], []
    marked = {p["marked"]: p["id"] for p in spec["pairs"]}
    for key in ordered_keys:
        rows = lines[key]
        local = []
        for i, row in enumerate(rows):
            if row.get("kind") != "P" or row.get("ivtff_group_raw") not in spec["operators"]:
                continue
            right = rows[i + 1] if i + 1 < len(rows) else None
            case = {
                "edition": row["edition"], "page": row["page"], "locus": row["locus"],
                "partition": "DISCOVERY" if row["page"] in spec["discovery_pages"] else "ADDITIONAL",
                "operator_id": row["source_group_id"], "operator": row["ivtff_group_raw"],
                "result_id": right["source_group_id"] if right else "",
                "result_raw": right["ivtff_group_raw"] if right else "",
                "right_separator": row.get("right_separator"),
                "next_left_separator": right.get("left_separator") if right else ""
            }
            adjacent = right is not None and int(right["source_group_index"]) == int(row["source_group_index"]) + 1
            definite = right is not None and row.get("right_separator") == right.get("left_separator") == "DEFINITE_SPACE"
            if adjacent and definite and right.get("kind") == "P" and right.get("ivtff_group_raw") in marked:
                case.update(case_id=f"C{len(cases) + 1:03}", pair=marked[right["ivtff_group_raw"]])
                cases.append(case)
                local.append(case["case_id"])
            else:
                case["reason"] = ("LINE_END" if right is None else
                                   "NONCONSECUTIVE" if not adjacent else
                                   "UNCERTAIN_SEPARATOR" if not definite else "NO_LISTED_RESULT")
                unresolved.append(case)
        if local:
            complete.append({"edition": key[0], "page": key[1], "locus": key[2],
                             "case_ids": local, "groups": rows})
    return lines, cases, unresolved, complete


def candidate_predictions(spec, candidate):
    phases = {x["name"]: x["phase"] for x in spec["phenomena"]}
    orientation = {x["id"]: x for x in spec["orientations"]}[candidate["orientation"]]
    marked = {p["marked"]: p["id"] for p in spec["pairs"]}
    by_pair = candidate["assignments"]
    output = []
    for op in spec["operators"]:
        operation = orientation[op]
        required = spec["operation_output_phases"][operation]
        for pair in spec["pairs"]:
            result = by_pair[pair["id"]]
            output.append({"operator": op, "result_raw": pair["marked"],
                           "operation": operation, "named_result": result,
                           "required_phase": required, "named_phase": phases[result],
                           "compatible": required == phases[result]})
    return output


def check_artifacts(spec, candidates, lines, cases, unresolved, complete, errors):
    A = EXP / "artifacts"
    expected_artifacts = {
        "SOURCE_CASES.json": cases,
        "UNRESOLVED_OPERATORS.json": unresolved,
        "COMPLETE_MATCHING_LINES.json": complete,
    }
    for name, expected in expected_artifacts.items():
        path = A / name
        if not path.is_file():
            bad(errors, "ARTIFACT_MISSING", file=name)
        elif load(path) != expected:
            bad(errors, "ARTIFACT_CONTENT", file=name)
    if len(cases) != 17:
        bad(errors, "QUALIFIED_PAIR_COUNT", expected=17, actual=len(cases))
    if len(unresolved) != 69:
        bad(errors, "UNRESOLVED_COUNT", expected=69, actual=len(unresolved))
    if any(c["partition"] != "DISCOVERY" for c in cases):
        bad(errors, "ADDITIONAL_QUALIFIED_CASE")
    if len(set(spec["additional_pages"])) != 4:
        bad(errors, "ADDITIONAL_LEAF_SPLIT", actual=spec["additional_pages"])
    if {c["page"] for c in cases} != {"f77r"}:
        bad(errors, "DISCOVERY_PAGE_CASE_SET")
    cand_expected = []
    classes = defaultdict(list)
    observed_classes = defaultdict(list)
    all_consequences = []
    candidate_ids = [candidate.get("id") for candidate in candidates]
    if len(candidates) != 240 or len(set(candidate_ids)) != 240:
        bad(errors, "CANDIDATE_COUNT_OR_IDS", expected=240, actual=len(candidates))
    if {candidate.get("orientation") for candidate in candidates} != {"CF", "FC"}:
        bad(errors, "ORIENTATION_SET")
    for candidate in candidates:
        assignments = candidate.get("assignments", {})
        if set(assignments) != {pair["id"] for pair in spec["pairs"]}:
            bad(errors, "ASSIGNMENT_KEYS", candidate=candidate.get("id"))
        if len(set(assignments.values())) != 4 or any(
                value not in {phenomenon["name"] for phenomenon in spec["phenomena"]}
                for value in assignments.values()):
            bad(errors, "ASSIGNMENT_INJECTIVITY", candidate=candidate.get("id"))
        pred = candidate_predictions(spec, candidate)
        if len(pred) != 8:
            bad(errors, "PREDICTION_COUNT", candidate=candidate.get("id"), actual=len(pred))
        if candidate.get("all_possible_pair_predictions") != pred:
            bad(errors, "PREDICTION_CONTENT", candidate=candidate.get("id"))
        vector = tuple(p["compatible"] for p in pred)
        classes[vector].append(candidate["id"])
        observed_vector = tuple(next(p for p in pred if p["operator"] == case["operator"] and
                                    p["result_raw"] == case["result_raw"])["compatible"]
                                for case in cases)
        observed_classes[observed_vector].append(candidate["id"])
        counts = {}
        for edition in ED:
            counts[edition] = {}
            for partition in ("DISCOVERY", "ADDITIONAL"):
                selected = [c for c in cases if c["edition"] == edition and c["partition"] == partition]
                contradictions = [c["case_id"] for c in selected
                                  if next(p for p in pred if p["operator"] == c["operator"] and p["result_raw"] == c["result_raw"])["compatible"] is False]
                counts[edition][partition] = {"cases": len(selected), "contradictions": contradictions,
                                               "compatible": len(selected) - len(contradictions),
                                               "survives": not contradictions}
                for c in selected:
                    p = next(p for p in pred if p["operator"] == c["operator"] and p["result_raw"] == c["result_raw"])
                    all_consequences.append({"candidate": candidate["id"], "case_id": c["case_id"],
                        "edition": c["edition"], "partition": c["partition"], "locus": c["locus"],
                        "operator_id": c["operator_id"], "result_id": c["result_id"],
                        "operator_raw": c["operator"], "result_raw": c["result_raw"],
                        "operation": p["operation"], "named_result": p["named_result"],
                        "required_phase": p["required_phase"], "named_phase": p["named_phase"],
                        "outcome": "COMPATIBLE_ASSUMPTIONS" if p["compatible"] else "CONTRADICTION"})
        cand_expected.append({"candidate": candidate["id"], "orientation": candidate["orientation"],
                              **candidate["assignments"], "by_edition": counts})
    path = A / "CANDIDATE_RESULTS.json"
    if not path.is_file() or load(path) != cand_expected:
        bad(errors, "CANDIDATE_RESULTS_CONTENT")
    class_expected = [{"class_id": f"E{i + 1:02}",
                       "compatibility_for_all_eight_possible_pairs": list(vector),
                       "candidates": members, "size": len(members)}
                      for i, (vector, members) in enumerate(sorted(classes.items()))]
    path = A / "PREDICTION_CLASSES.json"
    if not path.is_file() or load(path) != class_expected:
        bad(errors, "PREDICTION_CLASSES_CONTENT")
    observed_expected = [{"class_id": f"O{i + 1:02}",
                          "case_ids": [case["case_id"] for case in cases],
                          "compatibility": list(vector), "candidates": members,
                          "size": len(members)}
                         for i, (vector, members) in enumerate(sorted(observed_classes.items()))]
    class_lookup = {candidate: row["class_id"] for row in class_expected for candidate in row["candidates"]}
    observed_class_lookup = {candidate: row["class_id"] for row in observed_expected for candidate in row["candidates"]}
    table_expected = []
    for row in cand_expected:
        line = {key: value for key, value in row.items() if key != "by_edition"}
        line["phase_prediction_class"] = class_lookup[row["candidate"]]
        line["observed_prediction_class"] = observed_class_lookup[row["candidate"]]
        for edition in ED:
            for partition in ("DISCOVERY", "ADDITIONAL"):
                summary = row["by_edition"][edition][partition]
                line[f"{edition}_{partition}_cases"] = str(summary["cases"])
                line[f"{edition}_{partition}_contradictions"] = ",".join(summary["contradictions"]) or "NONE"
        line["independent_meaning_confirmation"] = "NONE"
        table_expected.append({key: str(value) for key, value in line.items()})
    table_path = A / "CANDIDATE_TABLE.tsv"
    if not table_path.is_file() or csv_rows(table_path) != table_expected:
        bad(errors, "CANDIDATE_TABLE_CONTENT")
    path = A / "OBSERVED_PREDICTION_CLASSES.json"
    if not path.is_file() or load(path) != observed_expected:
        bad(errors, "OBSERVED_PREDICTION_CLASSES_CONTENT")
    cons_path = A / "CONSEQUENCES.tsv"
    if not cons_path.is_file():
        bad(errors, "CONSEQUENCES_MISSING")
    else:
        if csv_rows(cons_path) != [{k: str(v) for k, v in row.items()} for row in all_consequences]:
            bad(errors, "CONSEQUENCES_CONTENT")
    return cand_expected, class_expected, observed_expected, all_consequences


def check_summary(spec, candidates, cases, unresolved, result_rows, class_rows, observed_class_rows, all_consequences, errors):
    path = EXP / "artifacts/RESULT.json"
    if not path.is_file():
        bad(errors, "RESULT_MISSING")
        return
    actual = load(path)
    summaries = {}
    for edition in ED:
        summaries[edition] = {"source_groups": sum(1 for row in lines_global.values() for x in row if x["edition"] == edition),
                              "qualified_pairs": sum(c["edition"] == edition for c in cases),
                              "unresolved_operator_positions": sum(c["edition"] == edition for c in unresolved)}
        for partition in ("DISCOVERY", "ADDITIONAL"):
            selected = [c for c in cases if c["edition"] == edition and c["partition"] == partition]
            survivors = [r["candidate"] for r in result_rows if r["by_edition"][edition][partition]["survives"]]
            summaries[edition][partition] = {"cases": len(selected), "surviving_candidates": survivors}
        summaries[edition]["joint_surviving_candidates"] = [r["candidate"] for r in result_rows
            if all(r["by_edition"][edition][part]["survives"] for part in ("DISCOVERY", "ADDITIONAL"))]
    if actual.get("candidates") != 240 or actual.get("possible_pair_predictions") != 1920:
        bad(errors, "RESULT_CANDIDATE_COUNTS")
    if actual.get("qualified_pairs") != 17 or actual.get("unresolved_operator_positions") != 69:
        bad(errors, "RESULT_CASE_COUNTS")
    if actual.get("phase_prediction_classes") != 14:
        bad(errors, "RESULT_CLASS_COUNT", actual=actual.get("phase_prediction_classes"))
    if actual.get("observed_prediction_classes") != len(observed_class_rows):
        bad(errors, "RESULT_OBSERVED_CLASS_COUNT", expected=len(observed_class_rows),
            actual=actual.get("observed_prediction_classes"))
    if actual.get("editions") != summaries:
        bad(errors, "RESULT_SUMMARIES")
    certificates = []
    for edition in ED:
        for partition in ("DISCOVERY", "ADDITIONAL"):
            for pair in spec["pairs"]:
                by_operator = {operator: [case for case in cases
                    if case["edition"] == edition and case["partition"] == partition
                    and case["pair"] == pair["id"] and case["operator"] == operator]
                               for operator in spec["operators"]}
                if all(by_operator.values()):
                    certificates.append({"edition": edition, "partition": partition,
                        "pair": pair["id"], "result_raw": pair["marked"],
                        "operator_1_cases": [case["case_id"] for case in by_operator[spec["operators"][0]]],
                        "operator_2_cases": [case["case_id"] for case in by_operator[spec["operators"][1]]],
                        "reason": "One fixed named result would need both LIQUID and SOLID under either orientation."})
    if actual.get("contradiction_certificates") != certificates:
        bad(errors, "RESULT_CERTIFICATES", expected=certificates,
            actual=actual.get("contradiction_certificates"))
    if len(summaries["ZL3b"]["DISCOVERY"]["surviving_candidates"]) != 0 or len(summaries["IT2a"]["DISCOVERY"]["surviving_candidates"]) != 0:
        bad(errors, "EXPECTED_ZL_IT_ZERO_SURVIVORS")
    if len(summaries["RF1b"]["DISCOVERY"]["surviving_candidates"]) != 72:
        bad(errors, "EXPECTED_RF_SURVIVORS", actual=len(summaries["RF1b"]["DISCOVERY"]["surviving_candidates"]))


def main():
    global lines_global
    errors = []
    locks(errors)
    spec = load(SPEC_PATH := EXP / "src/SPEC.json")
    candidates = load(EXP / "src/CANDIDATES.json")
    lines_global, cases, unresolved, complete = source_census(spec, errors)
    result_rows, class_rows, observed_class_rows, all_consequences = check_artifacts(spec, candidates, lines_global, cases, unresolved, complete, errors)
    check_summary(spec, candidates, cases, unresolved, result_rows, class_rows, observed_class_rows, all_consequences, errors)
    report = {
        "experiment": "GDT950", "independent": True,
        "status": "PASS" if not errors else "FAIL", "errors": errors,
        "source_groups": sum(len(v) for v in lines_global.values()),
        "source_lines": len(lines_global), "qualified_pairs": len(cases),
        "unresolved_operator_positions": len(unresolved), "candidates": len(candidates),
        "predictions_per_candidate": 8, "possible_pair_predictions": len(candidates) * 8,
        "prediction_classes": len(class_rows),
        "discovery_page": "f77r", "additional_pages": spec["additional_pages"],
        "additional_qualified_cases": sum(c["partition"] == "ADDITIONAL" for c in cases),
        "meaning_validated": False, "confirmed_words": 0,
        "claim_ceiling": "phase/output bridge audit only; no word or meteorological meaning confirmed",
        "historical_note": "The frozen preregistration's Aquinas citation range is loose; the relevant comparison is I.14-I.15, while I.13 concerns the Milky Way. This does not affect the mechanical result."
    }
    (EXP / "artifacts/VALIDATION.json").write_text(js(report), encoding="utf-8")
    print(js(report))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
