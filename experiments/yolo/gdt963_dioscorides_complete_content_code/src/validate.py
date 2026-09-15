#!/usr/bin/env python3
"""Independent source and artifact checker for GDT963.

The replay is separate from build_source.py and run.py.  It checks the guarded
printed projection, alias scopes, source capacity table, and a D-ary Huffman
lower bound.  Target artifacts are inspected only after the runner creates them.
"""
from __future__ import annotations

import csv
import gzip
import hashlib
import heapq
import json
import re
import unicodedata
import xml.etree.ElementTree as ET
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve()
EXP = HERE.parents[1]
ROOT = EXP.parents[2]
SRC = EXP / "src"
ART = EXP / "artifacts"
GDT915 = ROOT / "experiments/yolo/gdt915_terminal_lr_phrase_transfer"
NS = {"t": "http://www.tei-c.org/ns/1.0"}


def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_gzip_json(path: Path):
    with gzip.open(path, "rt", encoding="utf-8") as handle:
        return json.load(handle)


def norm(value: str) -> str:
    return unicodedata.normalize("NFC", value.lower())


def source_text(element) -> str:
    if element.tag.rsplit("}", 1)[-1] in {"head", "note"}:
        return ""
    return (element.text or "") + "".join(
        source_text(child) + (child.tail or "") for child in element
    )


def build_alias_map(aliases: dict) -> tuple[dict[str, list[str]], list[dict]]:
    mapping: dict[str, list[str]] = {}
    errors: list[dict] = []
    for atom, forms in aliases.get("single_atom_forms", {}).items():
        for form in forms:
            key = norm(form)
            if key in mapping and mapping[key] != [atom]:
                errors.append({"kind": "conflicting_single_alias", "form": form,
                               "existing": mapping[key], "new": [atom]})
            mapping[key] = [atom]
    for form, atoms in aliases.get("expanded_forms", {}).items():
        key = norm(form)
        if key in mapping:
            errors.append({"kind": "expanded_single_overlap", "form": form,
                           "existing": mapping[key], "new": atoms})
        if not atoms or any(not isinstance(atom, str) or atom.startswith("LEX:")
                            for atom in atoms):
            errors.append({"kind": "invalid_expanded_atoms", "form": form, "atoms": atoms})
        mapping[key] = list(atoms)
    return mapping, errors


def replay_source() -> tuple[list[dict], dict, list[dict]]:
    aliases = read_json(SRC / "ALIASES.json")
    mapping, alias_errors = build_alias_map(aliases)
    root = ET.parse(SRC / "SOURCE_EXCERPTS.xml").getroot()
    records: list[dict] = []
    for entry in root:
        record_id = entry.attrib["id"]
        raw = " ".join(source_text(entry).split())
        joins = []
        for old, new in aliases.get("source_orthographic_joins", {}).get(record_id, {}).items():
            count = raw.count(old)
            if count != 1:
                alias_errors.append({"kind": "orthographic_join_count", "record": record_id,
                                     "old": old, "count": count})
            raw = raw.replace(old, new)
            joins.append([old, new])
        words = re.findall(r"[^\W\d_]+", raw, flags=re.UNICODE)
        tokens = []
        for index, word in enumerate(words):
            atoms = mapping.get(norm(word), ["LEX:" + norm(word)])
            if record_id == "I.1" and word == "Ἴριδι":
                atoms = ["CELESTIAL_IRIS"]
            tokens.append({"index": index, "printed_form": word, "atoms": atoms})
        stream = [atom for token in tokens for atom in token["atoms"]]
        records.append({
            "id": record_id,
            "raw_printed_projection": raw,
            "orthographic_joins": joins,
            "tokens": tokens,
            "atoms": stream,
            "counts": dict(Counter(stream)),
            "editorial_deletion_text": [source_text(x) for x in entry.findall(".//t:del", NS)],
            "editorial_addition_text": [source_text(x) for x in entry.findall(".//t:add", NS)],
        })
    totals = Counter(atom for record in records for atom in record["atoms"])
    derived = {"atom_count": len(totals), "counts": dict(totals),
               "global_singletons": sorted(a for a, n in totals.items() if n == 1)}
    return records, derived, alias_errors


def huffman_cost(counts: Counter, alphabet_size: int = 26) -> int:
    """Minimum weighted length for a nonempty D-ary prefix code."""
    if not counts:
        return 0
    if alphabet_size < 2:
        raise ValueError("alphabet must contain at least two symbols")
    if len(counts) == 1:
        return next(iter(counts.values()))
    heap = list(counts.values())
    remainder = (len(heap) - 1) % (alphabet_size - 1)
    if remainder:
        heap.extend([0] * ((alphabet_size - 1) - remainder))
    heapq.heapify(heap)
    cost = 0
    while len(heap) > 1:
        merged = sum(heapq.heappop(heap) for _ in range(alphabet_size))
        cost += merged
        heapq.heappush(heap, merged)
    return cost


def source_checks() -> tuple[list[dict], dict]:
    checks: list[dict] = []
    aliases = read_json(SRC / "ALIASES.json")
    source = read_json(SRC / "SOURCE.json")
    origin = read_json(SRC / "SOURCE_ORIGIN.json")
    lock_path = EXP / "PREREG_LOCK.json"
    if lock_path.exists():
        lock = read_json(lock_path)
        lock_errors = []
        for relative, expected in lock.get("files", {}).items():
            path = ROOT / relative
            actual = digest(path) if path.exists() else None
            if actual != expected:
                lock_errors.append({"path": relative, "expected": expected, "actual": actual})
        checks.append({"name": "preregistration_lock", "ok": not lock_errors,
                       "checked": len(lock.get("files", {})), "errors": lock_errors})
    else:
        checks.append({"name": "preregistration_lock", "ok": False, "errors": ["missing lock"]})
    rebuilt, derived, alias_errors = replay_source()
    registered = source.get("records", [])
    checks.append({"name": "source_schema", "ok": source.get("schema") ==
                   "GDT963_COMPLETE_PRINTED_CONTENT_STREAM_V1"})
    ids = [r["id"] for r in rebuilt]
    checks.append({"name": "source_record_ids", "ok": ids == [r["id"] for r in registered] ==
                   ["I.1", "I.2", "I.3", "IV.20"], "actual": ids})
    checks.append({"name": "origin_record_ids", "ok": origin.get("records") == ids,
                   "actual": origin.get("records")})
    record_errors = []
    for expected, actual in zip(rebuilt, registered):
        if expected != actual:
            record_errors.append({"record": expected["id"], "replay_sha256": hashlib.sha256(
                json.dumps(expected, ensure_ascii=False, sort_keys=True).encode()).hexdigest(),
                "registered_sha256": hashlib.sha256(json.dumps(actual, ensure_ascii=False,
                                                                sort_keys=True).encode()).hexdigest()})
    if len(rebuilt) != len(registered):
        record_errors.append({"kind": "record_count", "replay": len(rebuilt),
                              "registered": len(registered)})
    checks.append({"name": "source_projection_replay", "ok": not record_errors,
                   "errors": record_errors})
    derived_errors = [key for key in ("atom_count", "counts", "global_singletons")
                      if source.get(key) != derived[key]]
    checks.append({"name": "source_global_accounting", "ok": not derived_errors,
                   "errors": derived_errors, "atom_count": derived["atom_count"]})
    checks.append({"name": "alias_contract", "ok": not alias_errors,
                   "errors": alias_errors})

    scope_errors = []
    celestial = [(r["id"], t["index"], t["printed_form"])
                 for r in rebuilt for t in r["tokens"] if "CELESTIAL_IRIS" in t["atoms"]]
    expected_celestial = [("I.1", t["index"], "Ἴριδι") for t in rebuilt[0]["tokens"]
                          if t["printed_form"] == "Ἴριδι"]
    if celestial != expected_celestial:
        scope_errors.append({"kind": "celestial_iris_scope", "actual": celestial,
                             "expected": expected_celestial})
    allowed = set(aliases.get("single_atom_forms", {}))
    allowed |= {a for values in aliases.get("expanded_forms", {}).values() for a in values}
    allowed.add("CELESTIAL_IRIS")
    for record in rebuilt:
        for token in record["tokens"]:
            for atom in token["atoms"]:
                if not atom.startswith("LEX:") and atom not in allowed:
                    scope_errors.append({"kind": "unregistered_atom", "record": record["id"],
                                         "token": token["printed_form"], "atom": atom})
    checks.append({"name": "alias_scope_and_special_case", "ok": not scope_errors,
                   "errors": scope_errors})

    capacity_errors = []
    capacity_path = ART / "SOURCE_CAPACITY.tsv"
    if capacity_path.exists():
        with capacity_path.open(encoding="utf-8", newline="") as handle:
            actual_rows = list(csv.DictReader(handle, delimiter="\t"))
        totals = Counter(atom for record in rebuilt for atom in record["atoms"])
        expected_rows = []
        for record in rebuilt:
            others = set(atom for other in rebuilt if other["id"] != record["id"]
                         for atom in other["atoms"])
            expected_rows.append({"record": record["id"], "tokens": str(len(record["tokens"])),
                                  "atoms": str(len(record["atoms"])),
                                  "distinct_atoms": str(len(record["counts"])),
                                  "global_singleton_occurrences": str(sum(
                                      totals[a] == 1 for a in record["atoms"])),
                                  "shared_with_other_records": str(sum(a in others for a in record["atoms"]))})
        if actual_rows != expected_rows:
            capacity_errors.append({"kind": "SOURCE_CAPACITY.tsv_mismatch",
                                    "actual_rows": len(actual_rows),
                                    "expected_rows": len(expected_rows)})
    else:
        capacity_errors.append({"kind": "missing_SOURCE_CAPACITY.tsv"})
    checks.append({"name": "source_capacity_artifact", "ok": not capacity_errors,
                   "errors": capacity_errors})

    huffman = {r["id"]: huffman_cost(Counter(r["atoms"]), 26) for r in rebuilt}
    checks.append({"name": "dary_huffman_source_lower_bound", "ok": all(v > 0 for v in huffman.values()),
                   "alphabet": 26, "minimum_serialized_lengths": huffman})
    checks.append({"name": "source_origin_hash_metadata", "ok": isinstance(
        origin.get("full_xml_sha256"), str) and len(origin["full_xml_sha256"]) == 64,
                   "verified": False,
                   "note": "full upstream XML is not an admitted local input; metadata preserved"})
    return checks, {"records": len(rebuilt), "tokens": sum(len(r["tokens"]) for r in rebuilt),
                    "atoms": sum(len(r["atoms"]) for r in rebuilt),
                    "distinct_atoms": derived["atom_count"], "huffman_lower_bounds": huffman}


def replay_frames() -> list[dict]:
    """Rebuild the six-edition whole-page intake independently of run.py."""
    spec = read_json(GDT915 / "src/SPEC.json")
    editions = tuple(spec["editions"])
    phases = ("DISCOVERY", "EVALUATION")
    frames = []
    for edition in editions:
        pages = {}
        for phase in phases:
            data = read_json(GDT915 / "artifacts" / f"SOURCE_{phase}_{edition}.json")
            columns = data["group_columns"]
            for row in data["lines"]:
                metadata = row["metadata"]
                page = metadata["page"]
                if page not in spec["partitions"][phase]:
                    raise AssertionError(f"unregistered page {phase} {edition} {page}")
                if (metadata["section"] == "H" and metadata["kind"] == "P"
                        and page != "f1r"):
                    pages.setdefault(page, []).append((metadata, [
                        dict(zip(columns, group)) for group in row["groups"]]))
        for page, rows in sorted(pages.items()):
            rows.sort(key=lambda item: int(item[0]["source_row_index"]))
            reasons, words, groups = [], [], []
            for metadata, group_rows in rows:
                locus = metadata["locus"]
                count = int(metadata["source_group_count"])
                if ([int(group["source_group_index"]) for group in group_rows]
                        != list(range(1, count + 1)) or not group_rows):
                    reasons.append([locus, "INCOMPLETE_GROUP_INDICES"])
                if any(not re.fullmatch(r"[a-z]+", group["ivtff_group_raw"])
                       for group in group_rows):
                    reasons.append([locus, "NONLITERAL_GROUP"])
                if (group_rows and (group_rows[0]["left_separator"] != "LINE_START"
                                    or group_rows[-1]["right_separator"] != "LINE_END")):
                    reasons.append([locus, "OUTER_BOUNDARY"])
                for left, right in zip(group_rows, group_rows[1:]):
                    if (left["right_separator"] != right["left_separator"]
                            or left["right_separator"] not in
                            ("DEFINITE_SPACE", "DRAWING_INTERRUPTION")):
                        reasons.append([locus, "UNKNOWN_INTERNAL_SEAM",
                                         left["source_group_id"], right["source_group_id"]])
                words.extend(group["ivtff_group_raw"] for group in group_rows)
                groups.extend(dict(locus=locus, **group) for group in group_rows)
            text = "".join(words) if not reasons else None
            frames.append({"id": f"{edition}:{page}", "edition": edition, "page": page,
                           "physical_leaf": re.match(r"f\d+", page).group(),
                           "eligible": not reasons, "reasons": reasons,
                           "line_count": len(rows), "group_count": len(groups),
                           "groups": groups, "text": text,
                           "characters": len(text) if text else None,
                           "alphabet": sorted(set(text)) if text else []})
    return frames


def target_intake_checks(source: dict) -> tuple[list[dict], dict]:
    checks = []
    frames_path = ART / "TARGET_FRAMES.json.gz"
    if not frames_path.exists():
        return [{"name": "target_intake", "ok": True, "status": "NOT_YET_INTAKEN",
                 "checked": False}], {"status": "NOT_YET_INTAKEN"}
    expected_frames = replay_frames()
    actual_frames = read_gzip_json(frames_path)
    checks.append({"name": "target_frames_replay", "ok": actual_frames == expected_frames,
                   "actual": len(actual_frames), "expected": len(expected_frames)})
    checks.append({"name": "target_frame_denominators", "ok": len(actual_frames) == 357
                   and all(sum(f["edition"] == ed for f in actual_frames) == 119
                           for ed in ("ZL3b", "IT2a", "RF1b")),
                   "actual_by_edition": dict(Counter(f["edition"] for f in actual_frames))})
    predicted_path = ART / "PREDICTIONS.tsv"
    prediction_errors = []
    expected_predictions = []
    for record in source["records"]:
        for token in record["tokens"]:
            expected_predictions.append({"record": record["id"],
                                         "source_token_index": str(token["index"]),
                                         "printed_form": token["printed_form"],
                                         "expanded_atoms": " ".join(token["atoms"])})
    if predicted_path.exists():
        with predicted_path.open(encoding="utf-8", newline="") as handle:
            actual_predictions = list(csv.DictReader(handle, delimiter="\t"))
        if actual_predictions != expected_predictions:
            prediction_errors.append({"kind": "PREDICTIONS.tsv_mismatch",
                                      "actual": len(actual_predictions),
                                      "expected": len(expected_predictions)})
    else:
        prediction_errors.append({"kind": "missing_PREDICTIONS.tsv"})
    checks.append({"name": "source_predictions", "ok": not prediction_errors,
                   "errors": prediction_errors, "actual": len(expected_predictions)})
    identical_errors = []
    identical_path = ART / "IDENTICAL_TARGET_STRINGS.json"
    if identical_path.exists():
        groups = {}
        for frame in actual_frames:
            if frame["eligible"]:
                groups.setdefault(frame["text"], []).append(frame["id"])
        expected_identical = [groups[text] for text in sorted(groups)]
        actual_identical = read_json(identical_path)
        if actual_identical != expected_identical:
            identical_errors.append({"kind": "identical_target_grouping_mismatch",
                                     "actual": len(actual_identical),
                                     "expected": len(expected_identical)})
    else:
        identical_errors.append({"kind": "missing_IDENTICAL_TARGET_STRINGS.json"})
    checks.append({"name": "identical_target_strings", "ok": not identical_errors,
                   "errors": identical_errors})
    local_path = ART / "ALL_LOCAL_CASES.json.gz"
    if local_path.exists():
        local_cases = read_gzip_json(local_path)
        local_checks, local_summary = local_case_checks(source, actual_frames)
        checks.extend(local_checks)
        summary = {"status": "LOCAL_CASES_REPLAYED", **local_summary}
        joint_path = ART / "JOINT_RESULTS.json"
        if joint_path.exists():
            joint_checks, joint_summary = joint_case_checks(source, actual_frames,
                                                            read_gzip_json(local_path))
            checks.extend(joint_checks)
            summary.update(joint_summary)
        result_path = ART / "RESULT.json"
        if result_path.exists():
            result = read_json(result_path)
            expected_local = dict(Counter(case.get("status") for case in local_cases))
            expected_joint = summary.get("joint_statuses", {})
            unresolved = any(status.startswith(("UNKNOWN", "ERROR"))
                             for status in expected_joint.values())
            expected_overall = ("BOUNDED_SEARCH_UNRESOLVED" if unresolved else
                                "COMPLETE_CONDITIONAL_CODE_WITNESS" if "SAT" in expected_joint.values()
                                else "COMPLETE_FIXED_CODE_NO_WITNESS")
            result_errors = []
            expected_values = {
                "status": expected_overall, "source_records": 4,
                "source_atoms": 613, "distinct_source_atoms": source["atom_count"],
                "global_source_singletons": len(source["global_singletons"]),
                "frames": len(actual_frames), "local_cases": len(local_cases),
                "local_statuses": expected_local, "joint_statuses": expected_joint,
                "confirmed_words": 0, "significance_claim": False,
                "independent_confirmation_leaves": 0,
            }
            for field, expected in expected_values.items():
                if result.get(field) != expected:
                    result_errors.append({"field": field, "actual": result.get(field),
                                          "expected": expected})
            checks.append({"name": "result_aggregation", "ok": not result_errors,
                           "errors": result_errors})
    else:
        checks.append({"name": "local_cases", "ok": True, "status": "RUNNING_OR_NOT_YET_WRITTEN",
                       "checked": False})
        summary = {"status": "INTAKE_REPLAYED", "frames": len(actual_frames),
                   "eligible_frames": sum(f["eligible"] for f in actual_frames),
                   "eligible_by_edition": dict(Counter(f["edition"] for f in actual_frames
                                                        if f["eligible"]))}
    return checks, summary


def prefix_free(code: dict[str, str]) -> bool:
    values = sorted(code.values())
    return bool(values) and all(value and not right.startswith(value)
                                 for value, right in zip(values, values[1:]))


def local_case_checks(source: dict, frames: list[dict]) -> tuple[list[dict], dict]:
    """Check every local receipt and exact SAT witness without accepting solver claims."""
    cases = read_gzip_json(ART / "ALL_LOCAL_CASES.json.gz")
    frame_by_id = {frame["id"]: frame for frame in frames}
    record_by_id = {record["id"]: record for record in source["records"]}
    errors = []
    expected_count = len(frames) * len(record_by_id)
    if len(cases) != expected_count:
        errors.append({"kind": "local_case_count", "actual": len(cases), "expected": expected_count})
    seen = set()
    for case in cases:
        key = (case.get("target_id"), case.get("record"))
        if key in seen:
            errors.append({"kind": "duplicate_local_case", "key": key})
        seen.add(key)
        frame = frame_by_id.get(case.get("target_id"))
        record = record_by_id.get(case.get("record"))
        if frame is None or record is None:
            errors.append({"kind": "unknown_local_reference", "key": key})
            continue
        expected_chars = frame["characters"]
        if case.get("edition") != frame["edition"] or case.get("page") != frame["page"]:
            errors.append({"kind": "frame_identity", "key": key})
        if case.get("source_atoms") != len(record["atoms"]):
            errors.append({"kind": "source_atom_denominator", "key": key})
        if case.get("target_characters") != expected_chars:
            errors.append({"kind": "target_length_denominator", "key": key})
        if not frame["eligible"]:
            if case.get("status") != "UNKNOWN_SOURCE" or case.get("reasons") != frame["reasons"]:
                errors.append({"kind": "unknown_frame_status", "key": key})
            continue
        bound = huffman_cost(Counter(record["atoms"]), len(frame["alphabet"]))
        if case.get("prefix_length_lower_bound") != bound:
            errors.append({"kind": "huffman_bound", "key": key, "actual": case.get(
                "prefix_length_lower_bound"), "expected": bound})
        status = case.get("status")
        if bound > len(frame["text"]) and status != "CONTRADICTED_LENGTH_BOUND":
            errors.append({"kind": "length_contradiction_status", "key": key, "status": status})
        receipt = case.get("solver_result")
        if status == "SAT":
            if not isinstance(receipt, dict) or receipt.get("status") != "SAT":
                errors.append({"kind": "missing_sat_receipt", "key": key})
                continue
            code = receipt.get("code")
            outputs = receipt.get("outputs")
            if not isinstance(code, dict) or not prefix_free(code):
                errors.append({"kind": "invalid_local_code", "key": key})
            elif any(atom not in code for atom in set(record["atoms"])):
                errors.append({"kind": "incomplete_local_code", "key": key})
            elif not isinstance(outputs, dict) or outputs.get(record["id"]) != frame["text"]:
                errors.append({"kind": "local_output_mismatch", "key": key})
            else:
                rendered = "".join(code[atom] for atom in record["atoms"])
                if rendered != frame["text"]:
                    errors.append({"kind": "local_exact_concat", "key": key})
            assignment = receipt.get("assignments", {}).get(record["id"], {})
            if assignment.get("id") != frame["id"]:
                errors.append({"kind": "local_assignment_mismatch", "key": key})
        elif isinstance(receipt, dict) and receipt.get("status") not in {
                status, "UNKNOWN_SOLVER", "UNKNOWN_WALL_CEILING", "ERROR_MODEL_IMPLEMENTATION",
                "ERROR_SOLVER_PROCESS"}:
            errors.append({"kind": "receipt_status_mismatch", "key": key,
                           "case_status": status, "receipt_status": receipt.get("status")})
    checks = [{"name": "all_local_cases", "ok": not errors and len(cases) == expected_count,
               "actual": len(cases), "expected": expected_count, "errors": errors[:30],
               "error_count": len(errors)}]
    table_path = ART / "CANDIDATE_TABLE.tsv"
    if table_path.exists():
        with table_path.open(encoding="utf-8", newline="") as handle:
            table = list(csv.DictReader(handle, delimiter="\t"))
        table_errors = []
        if len(table) != len(cases):
            table_errors.append({"kind": "candidate_table_count", "actual": len(table),
                                 "expected": len(cases)})
        for row, case in zip(table, cases):
            for field in ("edition", "page", "record", "status", "source_atoms",
                          "target_characters", "prefix_length_lower_bound"):
                if row.get(field) != str(case.get(field, "")):
                    table_errors.append({"kind": "candidate_table_row", "field": field,
                                         "case": case.get("target_id"), "actual": row.get(field),
                                         "expected": str(case.get(field, ""))})
                    break
        checks.append({"name": "candidate_table", "ok": not table_errors,
                       "actual": len(table), "expected": len(cases),
                       "errors": table_errors[:30], "error_count": len(table_errors)})
    return checks, {"local_cases": len(cases),
                    "local_statuses": dict(Counter(case.get("status") for case in cases))}


def joint_case_checks(source: dict, frames: list[dict], cases: list[dict]) -> tuple[list[dict], dict]:
    """Audit joint receipts and SAT witnesses, preserving UNKNOWN/error capacity."""
    joint = read_json(ART / "JOINT_RESULTS.json")
    frame_by_id = {frame["id"]: frame for frame in frames}
    records = {record["id"]: record for record in source["records"]}
    by_key = {(case.get("target_id"), case.get("record")): case for case in cases}
    # Exactly these statuses are proven local exclusions by the frozen runner;
    # all UNKNOWN and ERROR statuses remain eligible for joint reconsideration.
    excluded = {"CONTRADICTED_LENGTH_BOUND", "UNSAT_SOLVER", "UNSAT_EMPTY_DOMAIN",
                "UNSAT_NONEMPTY_LENGTH", "UNKNOWN_SOURCE"}
    errors = []
    summary = {"joint_statuses": {}}
    for edition in ("ZL3b", "IT2a", "RF1b"):
        result = joint.get(edition)
        if not isinstance(result, dict) or "status" not in result:
            errors.append({"kind": "missing_joint_edition", "edition": edition})
            continue
        status = result["status"]
        summary["joint_statuses"][edition] = status
        eligible = [frame for frame in frames if frame["edition"] == edition and frame["eligible"]]
        leaves = {frame["physical_leaf"] for frame in eligible}
        if len(leaves) < 4:
            if status != "NO_CAPACITY":
                errors.append({"kind": "joint_capacity_status", "edition": edition,
                               "leaves": len(leaves), "status": status})
            continue
        domains = {}
        for record_id in records:
            domains[record_id] = []
            for frame in eligible:
                local = by_key.get((frame["id"], record_id))
                if local is not None and local.get("status") not in excluded:
                    domains[record_id].append(frame)
        empty = sorted(record_id for record_id, values in domains.items() if not values)
        if empty:
            if status != "CONTRADICTED_EMPTY_LOCAL_ROLE":
                errors.append({"kind": "joint_empty_domain_status", "edition": edition,
                               "empty_roles": empty, "status": status})
            continue
        if status == "SAT":
            code = result.get("code")
            outputs = result.get("outputs")
            assignments = result.get("assignments")
            if not isinstance(code, dict) or not prefix_free(code):
                errors.append({"kind": "invalid_joint_code", "edition": edition})
                continue
            if not isinstance(outputs, dict) or not isinstance(assignments, dict):
                errors.append({"kind": "incomplete_joint_witness", "edition": edition})
                continue
            selected_leaves = []
            for record_id, record in records.items():
                target = assignments.get(record_id)
                if not isinstance(target, dict) or target.get("id") not in {
                        frame["id"] for frame in domains[record_id]}:
                    errors.append({"kind": "joint_assignment_domain", "edition": edition,
                                   "record": record_id})
                    continue
                selected = frame_by_id.get(target["id"])
                if selected is None:
                    errors.append({"kind": "joint_assignment_unknown", "edition": edition,
                                   "record": record_id})
                    continue
                selected_leaves.append(selected["physical_leaf"])
                rendered = "".join(code[atom] for atom in record["atoms"]
                                    if atom in code)
                if any(atom not in code for atom in record["atoms"]):
                    errors.append({"kind": "joint_code_missing_atom", "edition": edition,
                                   "record": record_id})
                elif outputs.get(record_id) != selected["text"] or rendered != selected["text"]:
                    errors.append({"kind": "joint_exact_concat", "edition": edition,
                                   "record": record_id})
            if len(selected_leaves) != len(set(selected_leaves)):
                errors.append({"kind": "joint_physical_leaf_collision", "edition": edition})
        elif status not in {"UNSAT_SOLVER", "UNKNOWN_SOLVER", "UNKNOWN_WALL_CEILING",
                            "ERROR_SOLVER_PROCESS", "ERROR_MODEL_IMPLEMENTATION"}:
            errors.append({"kind": "unexpected_joint_status", "edition": edition, "status": status})
    checks = [{"name": "joint_results_and_witnesses", "ok": not errors,
               "errors": errors[:30], "error_count": len(errors),
               "joint_editions": sorted(joint)}]
    return checks, summary


def optional_target_checks() -> tuple[list[dict], dict]:
    """Read guarded source caches and runner artifacts only."""
    source = read_json(SRC / "SOURCE.json")
    checks, summary = target_intake_checks(source)
    result_path = ART / "RESULT.json"
    if not result_path.exists():
        return checks, summary
    result = read_json(result_path)
    checks.append({"name": "target_result_json", "ok": isinstance(result, dict)
                   and result.get("status") is not None,
                   "experiment_id": result.get("experiment_id") if isinstance(result, dict) else None})
    receipt_errors = []
    for item in result.get("artifacts", []) if isinstance(result, dict) else []:
        if not isinstance(item, dict) or "path" not in item:
            receipt_errors.append({"kind": "malformed_artifact_receipt", "item": item})
            continue
        path = ROOT / item["path"]
        if not path.exists():
            receipt_errors.append({"kind": "missing_artifact", "path": item["path"]})
        elif item.get("sha256") and digest(path) != item["sha256"]:
            receipt_errors.append({"kind": "artifact_hash", "path": item["path"]})
    checks.append({"name": "target_artifact_receipts", "ok": not receipt_errors,
                   "errors": receipt_errors})
    summary.update({"status": "TARGET_ARTIFACTS_PRESENT", "result_keys": sorted(result)})
    return checks, summary


def validate() -> dict:
    checks, counts = source_checks()
    target_checks, target_summary = optional_target_checks()
    checks.extend(target_checks)
    ok = all(check.get("ok", False) for check in checks)
    return {"experiment_id": "GDT963", "status": "VALIDATION_PASS" if ok else "VALIDATION_FAIL",
            "independent_algorithm": "independent XML/alias replay, exact source accounting, D-ary Huffman bound",
            "checks": checks, "source_counts": counts, "target": target_summary,
            "claim_ceiling": "source/engineering contract validation only; no confirmed language or semantic reading"}


def main() -> int:
    output = validate()
    ART.mkdir(parents=True, exist_ok=True)
    (ART / "VALIDATION.json").write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n",
                                           encoding="utf-8")
    print(json.dumps(output, ensure_ascii=False, indent=2))
    return 0 if output["status"] == "VALIDATION_PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
