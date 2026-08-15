#!/usr/bin/env python3
"""Independent aggregate validation for GDT159.

This validator does not import either GDT159 or GDT003 runners.  It rebuilds
the three fingerprint coordinates from the exported selected operations,
reconstructs every B3 stratum from the published occurrence output, and checks
the complete hash/result chain.
"""

from __future__ import annotations

import csv
import gzip
import hashlib
import json
import math
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parent
RESULT = ROOT / "gdt159_result.json"
FP = ROOT / "gdt159_structural_fingerprints.tsv"
TRANS = ROOT / "gdt159_transformations.tsv"
BASE = ROOT / "gdt159_fingerprint_baselines.tsv"
COMPARE = ROOT / "gdt159_surface_algebra_comparison.tsv"
B3 = ROOT / "gdt159_b3_stability.tsv"
COUNTER = ROOT / "gdt159_counterexamples.tsv"
REPORT = ROOT / "GDT159_DIPLOMATIC_SURFACE_ALGEBRA_REPORT.md"
CORPORA = ROOT / "gdt159_diplomatic_corpora.json.gz"
MANIFEST = ROOT / "gdt159_diplomatic_corpus_manifest.tsv"
GDT003_FP = ROOT / "gdt003_structural_fingerprints.tsv"
GDT003_RESULT = ROOT / "gdt003_structural_fingerprint_result.json"
GDT045_OCC = ROOT / "gdt045_b3_occurrences.tsv"
GDT158_CLOSURE = ROOT / "gdt158_closure_folds.tsv"
OUT = ROOT / "gdt159_validation.json"


def sha(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def csha(value: object) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=True, separators=(",", ":")).encode()).hexdigest()


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def close(left: float, right: float, tolerance: float = 1e-12) -> bool:
    return abs(left - right) <= tolerance * max(1.0, abs(left), abs(right))


def pb_tail(probabilities: list[float], observed: int) -> float:
    dist = [1.0] + [0.0] * len(probabilities)
    for probability in probabilities:
        for count in range(len(probabilities), 0, -1):
            dist[count] = dist[count] * (1 - probability) + dist[count - 1] * probability
        dist[0] *= 1 - probability
    return sum(dist[observed:])


def main() -> None:
    checks: list[dict[str, object]] = []

    def check(name: str, passed: bool, detail: object = "") -> None:
        checks.append({"check": name, "passed": bool(passed), "detail": detail})
        if not passed:
            raise AssertionError(f"{name}: {detail}")

    result = json.loads(RESULT.read_text(encoding="utf-8"))
    content = dict(result)
    claimed = content.pop("result_content_sha256")
    check("result_content_hash", claimed == csha(content))
    check("schema", result["schema"] == "GDT159_DIPLOMATIC_SURFACE_ALGEBRA_RESULT_V1")
    check("source_freeze_commit", result["source_freeze_commit"] == "90ebc626ab4ff6ccf555a42510c4b5de5f4ce4c5")

    for name, digest in result["inputs"].items():
        check(f"input_hash:{name}", sha(ROOT / name) == digest)
    for name, digest in result["outputs"].items():
        check(f"output_hash:{name}", sha(ROOT / name) == digest)
    for name, digest in result["implementation"].items():
        check(f"implementation_hash:{name}", sha(ROOT / name) == digest)
    original = json.loads(GDT003_RESULT.read_text(encoding="utf-8"))["implementation"]
    check("frozen_gdt003_runner_unchanged", result["implementation"]["run_gdt003_structural_fingerprint_comparator.py"] == original["run_gdt003_structural_fingerprint_comparator.py"])
    check("frozen_gdt003_core_unchanged", result["implementation"]["run_gdt003_nested_heldout.py"] == original["run_gdt003_nested_heldout.py"])

    with gzip.open(CORPORA, "rt", encoding="utf-8") as handle:
        source = json.load(handle)
    check("source_records", len(source["records"]) == 42975)
    check("source_has_no_voynich_or_f84r", not any("f84r" in json.dumps(row, ensure_ascii=False).lower() or "voynich" in json.dumps(row, ensure_ascii=False).lower() for row in source["records"]))
    check("five_fingerprints", len(read(FP)) == 5)
    check("baseline_rows", len(read(BASE)) == 75)

    fingerprints = {row["corpus_id"]: row for row in read(FP)}
    transforms = read(TRANS)
    by_corpus: dict[str, list[dict[str, str]]] = defaultdict(list)
    by_fold: dict[tuple[str, str], list[dict[str, str]]] = defaultdict(list)
    for row in transforms:
        by_corpus[row["corpus_id"]].append(row)
        by_fold[row["corpus_id"], row["held_fold"]].append(row)
    for corpus_id, row in fingerprints.items():
        values = by_corpus[corpus_id]
        folds = int(row["folds"])
        check(f"{corpus_id}:operation_count", close(len(values) / folds, float(row["mean_discovered_operations"])))
        left = sum(int(value["edge_types"]) for value in values if value["operation_family"].startswith("PREFIX"))
        right = sum(int(value["edge_types"]) for value in values if value["operation_family"].startswith("SUFFIX"))
        check(f"{corpus_id}:left_support", left == int(row["left_edge_support"]))
        check(f"{corpus_id}:right_support", right == int(row["right_edge_support"]))
        check(f"{corpus_id}:edge_ratio", close(math.log2((right + 1) / (left + 1)), float(row["left_right_log2_support_ratio"])))
        denominator = sum(len(items) * (len(items) - 1) // 2 for (cid, _), items in by_fold.items() if cid == corpus_id)
        reconstructed = int(row["compatible_operation_pairs"]) / max(1, denominator)
        check(f"{corpus_id}:compatible_density", close(reconstructed, float(row["compatible_pair_density"])), (reconstructed, row["compatible_pair_density"]))

    target = next(row for row in read(GDT003_FP) if row["corpus_id"] == "VOYNICH_MATCHED")
    target_ops = float(target["mean_discovered_operations"])
    target_pairs = float(target["compatible_pair_density"])
    target_edge = float(target["left_right_log2_support_ratio"])
    comparison = read(COMPARE)
    check("comparison_rows", len(comparison) == 8)
    for row in comparison:
        ops = float(row["mean_discovered_operations"])
        pairs = float(row["compatible_pair_density"])
        edge = float(row["left_right_log2_support_ratio"])
        op_ratio, pair_ratio = ops / target_ops, pairs / target_pairs
        distance = math.sqrt((math.log2(max(op_ratio, 1e-12)) ** 2 + math.log2(max(pair_ratio, 1e-12)) ** 2 + (edge - target_edge) ** 2) / 3)
        check(f"comparison:{row['corpus_id']}:op_ratio", close(op_ratio, float(row["operation_scale_ratio_to_voynich"])))
        check(f"comparison:{row['corpus_id']}:pair_ratio", close(pair_ratio, float(row["compatible_density_ratio_to_voynich"])))
        check(f"comparison:{row['corpus_id']}:distance", close(distance, float(row["three_coordinate_log_rms_distance"])))
        regime = int(0.5 <= op_ratio <= 2 and 0.5 <= pair_ratio <= 2 and edge < 0)
        check(f"comparison:{row['corpus_id']}:regime", regime == int(row["voynich_algebraic_regime"]))
    matched_new = [row for row in comparison if row["source"] == "NEW_GDT159" and row["capacity_state"] == "MATCHED_12000"]
    check("two_matched_new", len(matched_new) == 2)
    check("no_matched_new_regime", not any(int(row["voynich_algebraic_regime"]) for row in matched_new))
    closest = min(matched_new, key=lambda row: float(row["three_coordinate_log_rms_distance"]))
    check("closest_new", closest["corpus_id"] == result["closest_matched_new"]["corpus_id"] == "LATIN_15C_GRAPHEMATIC")
    check("surface_status", result["status"] == "SURFACE_ALGEBRA_RESIDUAL_REMAINS_UNEXPLAINED")

    occ = read(GDT045_OCC)
    check("b3_occurrences_no_f84r", len(occ) == 213 and not any(row["page"] == "f84r" for row in occ))
    exported_b3 = {(row["scope_type"], row["scope"]): row for row in read(B3) if row["system"] == "VOYNICH"}
    powered = []
    for field, scope_type in (("register", "REGISTER"), ("hand", "HAND")):
        grouped: dict[str, list[dict[str, str]]] = defaultdict(list)
        for row in occ:
            grouped[row[field]].append(row)
        for scope, rows in sorted(grouped.items()):
            saved = exported_b3[scope_type, scope]
            observed = sum(int(row["physical_line_end"]) for row in rows)
            by_line: dict[str, list[dict[str, str]]] = defaultdict(list)
            for row in rows:
                by_line[row["locus"]].append(row)
            probabilities = [len(values) / int(values[0]["group_count"]) for values in by_line.values()]
            expected = sum(probabilities)
            effect = observed / len(rows) - expected / len(rows)
            folios = {row["physical_folio"] for row in rows}
            leave = []
            for folio in folios:
                kept = [row for row in rows if row["physical_folio"] != folio]
                if kept:
                    leave.append(sum(int(row["physical_line_end"]) for row in kept) / len(kept) - sum(1 / int(row["group_count"]) for row in kept) / len(kept))
            is_powered = len(rows) >= 10 and len(folios) >= 3
            check(f"b3:{scope_type}:{scope}:support", len(rows) == int(saved["support"]))
            check(f"b3:{scope_type}:{scope}:observed", observed == int(saved["endpoint_hits"]))
            check(f"b3:{scope_type}:{scope}:expected", close(expected, float(saved["expected_hits"])))
            check(f"b3:{scope_type}:{scope}:effect", close(effect, float(saved["rate_effect"])))
            check(f"b3:{scope_type}:{scope}:p", close(pb_tail(probabilities, observed), float(saved["local_poisson_binomial_p"])))
            if leave:
                check(f"b3:{scope_type}:{scope}:lofo", close(min(leave), float(saved["leave_one_folio_min_effect"])))
            check(f"b3:{scope_type}:{scope}:powered", int(is_powered) == int(saved["powered"]))
            if is_powered:
                powered.append((effect, min(leave)))
    check("eight_powered_b3_strata", len(powered) == result["b3_powered_strata"] == 8)
    check("powered_b3_all_positive", all(effect > 0 and leave > 0 for effect, leave in powered))
    check("b3_status", result["b3_status"] == "B3_FIXED_CLASS_STABLE_ACROSS_POWERED_STRATA")

    closure = read(GDT158_CLOSURE)
    expected_selector = {
        "AUGSBURG_ACCOUNTS:ORIGINAL_ENTRY": (18, 4, 0.5),
        "NUREMBERG_LETTERBOOKS:EXPANDED": (4, 2, 0.75),
        "NUREMBERG_LETTERBOOKS:REAL_DIPLOMATIC": (4, 2, 0.75),
    }
    generic = {row["system"]: row for row in read(B3) if row["system"] != "VOYNICH"}
    for view, expected in expected_selector.items():
        rows = [row for row in closure if row["corpus_view"] == view]
        counts = Counter(row["selected_predicate"] for row in rows)
        actual = (len(rows), len(counts), counts.most_common(1)[0][1] / len(rows))
        check(f"selector:{view}", actual == expected)
        check(f"selector_export:{view}", int(generic[view]["support"]) == expected[0] and int(generic[view]["distinct_selected_identities"]) == expected[1] and close(float(generic[view]["modal_identity_fraction"]), expected[2]))

    check("counterexamples", len(read(COUNTER)) == 7)
    check("report_status", "SURFACE_ALGEBRA_RESIDUAL_REMAINS_UNEXPLAINED" in REPORT.read_text(encoding="utf-8") and "B3_FIXED_CLASS_STABLE_ACROSS_POWERED_STRATA" in REPORT.read_text(encoding="utf-8"))
    check("f84r_flags", all(value is False for value in result["f84r"].values()))

    validation = {
        "schema": "GDT159_DIPLOMATIC_SURFACE_ALGEBRA_VALIDATION_V1",
        "status": "PASS_INDEPENDENT_TRANSFORMATION_AGGREGATE_AND_B3_RECONSTRUCTION",
        "checks_passed": sum(int(row["passed"]) for row in checks),
        "checks_total": len(checks), "checks": checks,
        "result_sha256": sha(RESULT),
        "inputs": {path.name: sha(path) for path in (FP, TRANS, BASE, COMPARE, B3, COUNTER, REPORT, CORPORA, MANIFEST, GDT003_FP, GDT003_RESULT, GDT045_OCC, GDT158_CLOSURE)},
    }
    validation["validation_content_sha256"] = csha(validation)
    OUT.write_text(json.dumps(validation, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"PASS {validation['checks_passed']}/{validation['checks_total']}")


if __name__ == "__main__":
    main()
