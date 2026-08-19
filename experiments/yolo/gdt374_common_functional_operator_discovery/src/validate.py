#!/usr/bin/env python3
"""Independent inventory/arithmetic validator for GDT374."""
from __future__ import annotations

import csv
import hashlib
import json
import math
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT))
from tools.vmanus_experiment import GuardedTSV  # noqa: E402

BASE = ROOT / "experiments/yolo/gdt374_common_functional_operator_discovery"
ART = BASE / "artifacts"
INTER = ROOT / "gdt327_joint_tuple_interlinear.tsv"
DRAW = ROOT / "experiments/semantic_assumptions/results/drawing_reset_segment_atlas.tsv"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def hid(prefix: str, *parts: object) -> str:
    return hashlib.sha256((prefix + "|" + "|".join(map(str, parts))).encode()).hexdigest()[:20]


def read(path: Path) -> list[dict[str, str]]:
    with path.open(newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    checks: list[dict[str, object]] = []

    def check(name: str, passed: bool, detail: str = "") -> None:
        checks.append({"check": name, "passed": bool(passed), "detail": detail})
        if not passed:
            raise AssertionError(f"{name}: {detail}")

    result_path = ART / "gdt374_result.json"
    result = json.loads(result_path.read_text())
    source = read(INTER)
    check("schema", result["schema"] == "GDT374_RESULT_V1")
    check("source_count", len(source) == 8448, str(len(source)))
    check("source_folios", len({r["physical_folio"] for r in source}) == 91)
    check("source_f84_absent", not any(r["page"].lower().startswith("f84") or r["locus"].lower().startswith("f84") for r in source))
    pages = {r["page"] for r in source}
    loci = {r["locus"] for r in source}
    guarded = GuardedTSV(DRAW, selector_column="page", allowed_values=pages, forbidden_prefixes=("f84",))
    draw = {}
    for row in guarded:
        if row["locus"] in loci:
            draw[(row["locus"], int(row["group_index"]))] = row
    check("guard_rejects_f84", guarded.stats.skipped_forbidden == 570, str(guarded.stats.skipped_forbidden))
    check("drawing_join", len(draw) == 8448, str(len(draw)))

    # Independently reconstruct the three record scopes and their opaque IDs.
    units = defaultdict(list)
    for row in source:
        segment = draw[(row["locus"], int(row["group_index"]))]["segment_id"]
        units[("FIELD", f"{row['locus']}|F{row['field_ordinal']}")].append(row)
        units[("DRAWING_RESET_SEGMENT", segment)].append(row)
        units[("PHYSICAL_LINE", row["locus"])].append(row)
    reconstructed = {}
    for (scope, unit), rows in units.items():
        rows.sort(key=lambda r: int(r["group_index"]))
        record_id = hid("RECORD", scope, unit)
        reconstructed[record_id] = {
            "record_id": record_id,
            "scope": scope,
            "physical_folio": rows[0]["physical_folio"],
            "locus": rows[0]["locus"],
            "field_ordinal": int(rows[0]["field_ordinal"]) if scope == "FIELD" else 0,
            "register": rows[0]["register"],
            "sequence": tuple(r["joint_tuple_id"] for r in rows),
        }
    records = read(ART / "gdt374_record_inventory.tsv")
    check("record_count", len(records) == len(reconstructed) == 4877, str(len(records)))
    check("record_scope_counts", Counter(r["scope"] for r in records) == Counter({"FIELD": 2400, "DRAWING_RESET_SEGMENT": 1334, "PHYSICAL_LINE": 1143}))
    check("record_ids", {r["record_id"] for r in records} == set(reconstructed))
    check("record_sequences", all(tuple(json.loads(r["opaque_tuple_sequence_json"])) == reconstructed[r["record_id"]]["sequence"] for r in records))

    # Rebuild exact insertion event IDs from source records, independent of the runner.
    expected_events = set()
    event_scope_counts = Counter()
    for scope in ("FIELD", "DRAWING_RESET_SEGMENT", "PHYSICAL_LINE"):
        by_folio = defaultdict(list)
        for rec in reconstructed.values():
            if rec["scope"] == scope:
                by_folio[rec["physical_folio"]].append(rec)
        for local in by_folio.values():
            by_sequence = defaultdict(list)
            for rec in local:
                by_sequence[rec["sequence"]].append(rec)
            seen = set()
            for target in local:
                long = target["sequence"]
                if len(long) < 2:
                    continue
                for index, inserted in enumerate(long):
                    short = long[:index] + long[index + 1 :]
                    position = "PREFIX" if index == 0 else "SUFFIX" if index == len(long) - 1 else "INTERNAL"
                    for source_rec in by_sequence.get(short, []):
                        key = (scope, source_rec["record_id"], position, inserted, long)
                        if key in seen:
                            continue
                        seen.add(key)
                        expected_events.add(hid("INSERT_EVENT", *key))
                        event_scope_counts[scope] += 1
    events = read(ART / "gdt374_rewrite_events.tsv")
    check("event_ids", {r["event_id"] for r in events} == expected_events)
    check("event_scope_counts", Counter(r["scope"] for r in events) == event_scope_counts == Counter({"FIELD": 277, "DRAWING_RESET_SEGMENT": 4}))
    field_events = [r for r in events if r["scope"] == "FIELD"]
    capacity = defaultdict(lambda: {"folios": set(), "bases": set()})
    for event in field_events:
        capacity[event["operator_class"]]["folios"].add(event["physical_folio"])
        capacity[event["operator_class"]]["bases"].add(event["base_signature"])
    library = {label for label, item in capacity.items() if len(item["folios"]) >= 2}
    promotion = {label for label, item in capacity.items() if len(item["folios"]) >= 2 and len(item["bases"]) >= 3}
    check("library_count", len(library) == result["inventory"]["primary_library_classes_two_folios"] == 23)
    check("promotion_capacity", len(promotion) == result["inventory"]["promotion_capacity_classes"] == 8)

    predictions = read(ART / "gdt374_holdout_predictions.tsv")
    scores = read(ART / "gdt374_transfer_scores.tsv")
    check("prediction_rows", len(predictions) == 632, str(len(predictions)))
    for summary in scores:
        split = summary["split"]
        local = [r for r in predictions if r["split"] == split]
        covered = [r for r in local if r["covered"] == "1"]
        gain = sum(float(r["gain_bits"]) for r in covered)
        check("score_events_" + split, int(summary["events"]) == len(local))
        check("score_covered_" + split, int(summary["covered"]) == len(covered))
        check("score_gain_" + split, math.isclose(float(summary["gain_bits"]), gain, abs_tol=1e-9))
        check("score_top1_" + split, int(summary["baseline_top1"]) == sum(int(r["baseline_rank"]) == 1 for r in covered) and int(summary["full_top1"]) == sum(int(r["full_rank"]) == 1 for r in covered))
        check("score_top5_" + split, int(summary["baseline_top5"]) == sum(int(r["baseline_top5"]) for r in covered) and int(summary["full_top5"]) == sum(int(r["full_top5"]) for r in covered))
    primary = next(r for r in scores if r["split"] == "physical_folio")
    check("primary_negative", float(primary["gain_bits"]) < 0 and float(primary["selector_paid_gain_bits"]) < 0)
    check("primary_result", math.isclose(float(primary["gain_bits"]), result["primary"]["gain_bits"], abs_tol=1e-9))
    check("unseen_base_negative", float(primary["unseen_base_gain_bits"]) < 0)

    null = read(ART / "gdt374_null_results.tsv")
    check("null_worlds", len(null) == 4096)
    observed = result["null"]["observed_total_gain_bits"]
    local_p = (1 + sum(float(r["total_gain_bits"]) >= observed - 1e-12 for r in null)) / 4097
    observed_max = result["null"]["observed_max_candidate_paid_gain_bits"]
    max_p = (1 + sum(float(r["max_candidate_paid_gain_bits"]) >= observed_max - 1e-12 for r in null)) / 4097
    check("null_local_p", math.isclose(local_p, result["null"]["local_p"], abs_tol=1e-15))
    check("null_max_p", math.isclose(max_p, result["null"]["max_library_p"], abs_tol=1e-15))
    check("null_mobile", result["null"]["mobile_events"] == 147 and result["null"]["capacity_status"] == "ADEQUATE")
    candidates = read(ART / "gdt374_candidate_atlas.tsv")
    check("candidate_rows", len(candidates) == 314, str(len(candidates)))
    check("zero_capacity_rows", {r["rewrite_type"] for r in candidates if r["classification"] == "NO_CAPACITY"} == {"ADJACENT_EXACT_TUPLE_DUPLICATION", "BOUNDARY_SPLIT_JOIN", "PRIOR_RECORD_SHORTEN_RESUME"})
    check("no_promotable", not any(r["classification"] == "INTERESTING_EXPLORATORY" for r in candidates) and result["promotable_candidate_ids"] == [])
    check("semantic_unassigned", all(r["anonymous_behavior_label"] == "UNASSIGNED" for r in candidates) and result["semantic_roles_assigned"] == 0)
    check("artifact_f84_absent", not any(
        value.lower().startswith("f84")
        for table, fields in ((records, ("page", "physical_folio", "locus")), (events, ("page", "physical_folio", "locus")), (predictions, ("physical_folio",)))
        for row in table for field in fields for value in (row[field],)
    ))
    check("status", result["status"] == "NO_PROMOTABLE_FUNCTIONAL_OPERATOR_FOUND")
    for rel, digest in result["inputs"].items():
        check("input_" + rel, sha(ROOT / rel) == digest)
    for rel, digest in result["outputs"].items():
        check("output_" + rel, sha(ROOT / rel) == digest)
    for rel, digest in result["documents"].items():
        check("document_" + rel, sha(ROOT / rel) == digest)
    for rel, digest in result["implementation"].items():
        check("implementation_" + rel, sha(ROOT / rel) == digest)
    payload = dict(result)
    stored = payload.pop("content_hash")
    check("content_hash", hashlib.sha256(json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()).hexdigest() == stored)
    validation = {
        "schema": "GDT374_VALIDATION_V1",
        "status": "PASS",
        "scope": "INDEPENDENT_SOURCE_GUARD_RECORD_EVENT_CAPACITY_AND_ARITHMETIC_RECONSTRUCTION; NAIVE_BAYES_AND_NULL_RNG_NOT_INDEPENDENTLY_REFIT",
        "checks_passed": len(checks),
        "checks_total": len(checks),
        "checks": checks,
        "result_sha256": sha(result_path),
        "validator_sha256": sha(BASE / "src/validate.py"),
        "f84_accessed": False,
    }
    (ART / "gdt374_validation.json").write_text(json.dumps(validation, indent=2, sort_keys=True) + "\n")
    print(f"PASS {len(checks)}/{len(checks)}")


if __name__ == "__main__":
    main()
