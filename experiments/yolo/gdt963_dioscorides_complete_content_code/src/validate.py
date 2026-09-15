#!/usr/bin/env python3
"""Independent source and artifact checker for GDT963.

The replay is separate from build_source.py and run.py.  It checks the guarded
printed projection, alias scopes, source capacity table, and a D-ary Huffman
lower bound.  Target artifacts are inspected only after the runner creates them.
"""
from __future__ import annotations

import csv
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
NS = {"t": "http://www.tei-c.org/ns/1.0"}


def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


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


def optional_target_checks() -> tuple[list[dict], dict]:
    """Read runner artifacts only; never open target input caches here."""
    result_path = ART / "RESULT.json"
    if not result_path.exists():
        return [{"name": "target_intake", "ok": True, "status": "NOT_YET_INTAKEN",
                 "checked": False}], {"status": "NOT_YET_INTAKEN"}
    result = read_json(result_path)
    checks = [{"name": "target_result_json", "ok": isinstance(result, dict),
               "experiment_id": result.get("experiment_id") if isinstance(result, dict) else None}]
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
    return checks, {"status": "TARGET_ARTIFACTS_PRESENT", "result_keys": sorted(result)}


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
