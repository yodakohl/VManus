#!/usr/bin/env python3
"""Independent arithmetic/integrity validation for the fingerprint comparator."""

from __future__ import annotations

import csv
import gzip
import hashlib
import json
import math
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parent
RESULT = ROOT / "gdt003_structural_fingerprint_result.json"
FINGERPRINTS = ROOT / "gdt003_structural_fingerprints.tsv"
TRANSFORMS = ROOT / "gdt003_structural_fingerprint_transformations.tsv"
BASELINES = ROOT / "gdt003_structural_fingerprint_baselines.tsv"
RANKING = ROOT / "gdt003_structural_fingerprint_ranking.tsv"
FAMILY = ROOT / "gdt003_structural_fingerprint_family_ranking.tsv"
CORPORA = ROOT / "gdt003_structural_fingerprint_corpora.json.gz"
MANIFEST = ROOT / "gdt003_structural_fingerprint_corpus_manifest.tsv"
LEDGER = ROOT / "GDT002_YOLO_LEDGER.tsv"
OUT = ROOT / "gdt003_structural_fingerprint_validation.json"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_sha(value: object) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=True, separators=(",", ":")).encode()).hexdigest()


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def js_distance(left: list[float], right: list[float]) -> float:
    eps = 1e-12
    p, q = [value + eps for value in left], [value + eps for value in right]
    ps, qs = sum(p), sum(q)
    p, q = [value / ps for value in p], [value / qs for value in q]
    middle = [(a + b) / 2 for a, b in zip(p, q)]
    value = 0.5 * sum(a * math.log2(a / m) for a, m in zip(p, middle))
    value += 0.5 * sum(b * math.log2(b / m) for b, m in zip(q, middle))
    return math.sqrt(max(0.0, value))


def main() -> None:
    checks: list[tuple[str, bool]] = []
    result = json.loads(RESULT.read_text(encoding="utf-8"))
    fps = read_tsv(FINGERPRINTS)
    transforms = read_tsv(TRANSFORMS)
    baselines = read_tsv(BASELINES)
    ranking = read_tsv(RANKING)
    family = read_tsv(FAMILY)
    manifest = read_tsv(MANIFEST)
    with gzip.open(CORPORA, "rt", encoding="utf-8") as handle:
        corpus = json.load(handle)
    fp_by_id = {row["corpus_id"]: row for row in fps}
    manifest_by_id = {row["corpus_id"]: row for row in manifest}
    target = fp_by_id["VOYNICH_MATCHED"]

    checks.append(("schema", result["schema"] == "GDT003_STRUCTURAL_FINGERPRINT_COMPARATOR_RESULT_V1"))
    normalized = dict(result)
    recorded_content_hash = normalized.pop("result_content_sha256")
    checks.append(("result_content_hash", recorded_content_hash == canonical_sha(normalized)))
    for name, digest in result["inputs"].items():
        checks.append((f"input_hash_{name}", sha(ROOT / name) == digest))
    for name, digest in result["implementation"].items():
        checks.append((f"implementation_hash_{name}", sha(ROOT / name) == digest))
    for name, digest in result["outputs"].items():
        checks.append((f"output_hash_{name}", sha(ROOT / name) == digest))

    corpus_counts = Counter(row["corpus_id"] for row in corpus["records"])
    checks.append(("evaluated_count", len(fps) == 21 and result["corpora"]["evaluated"] == 21))
    checks.append(("matched_count", sum(row["capacity_state"] == "MATCHED_12000" for row in fps) == 20))
    checks.append(("manifest_corpus_counts", all(corpus_counts[row["corpus_id"]] == int(row["sampled_tokens"]) for row in manifest)))
    checks.append(("old_georgian_low_capacity", corpus_counts["OLD_GEORGIAN_UD"] == 6093 and fp_by_id["OLD_GEORGIAN_UD"]["capacity_state"] == "LOW_CAPACITY_UNMATCHED_ALL"))
    checks.append(("middle_armenian_unfitted", corpus_counts["MIDDLE_ARMENIAN_UD"] == 0 and manifest_by_id["MIDDLE_ARMENIAN_UD"]["capacity_state"] == "INSUFFICIENT_UNITS"))

    transform_counts = Counter(row["corpus_id"] for row in transforms)
    for row in fps:
        expected = transform_counts[row["corpus_id"]] / int(row["folds"])
        checks.append((f"operation_mean_{row['corpus_id']}", abs(expected - float(row["mean_discovered_operations"])) < 1e-12))
    baseline_index = {(row["corpus_id"], row["scope"], row["model"]): row for row in baselines}
    for row in fps:
        cid = row["corpus_id"]
        paradigm = float(baseline_index[cid, "ALL_ALGEBRA", "NESTED_PARADIGM"]["average_precision"] or 0)
        best = max(float(baseline_index[cid, "ALL_ALGEBRA", model]["average_precision"] or 0) for model in ("CHARACTER_ORDER2_KT", "CHARACTER_ORDER4_KT", "VISIBLE_WHOLE_GROUP_FREQUENCY", "NEAREST_EDIT_DISTANCE"))
        checks.append((f"ap_gain_{cid}", abs((paradigm - best) - float(row["ap_gain_over_best_string"])) < 1e-12))

    scalar_fields = result["distance_definition"]["scalars"]
    spectrum_fields = [key for key in target if key.startswith("spectrum_") and key not in {"spectrum_js_distance"}]
    matched = [row for row in fps if row["capacity_state"] == "MATCHED_12000"]
    ranges = {field: (min(float(row[field]) for row in matched), max(float(row[field]) for row in matched)) for field in scalar_fields}
    checks.append(("distance_ranges", all(abs(ranges[field][0] - float(result["distance_definition"]["ranges"][field][0])) < 1e-15 and abs(ranges[field][1] - float(result["distance_definition"]["ranges"][field][1])) < 1e-15 for field in scalar_fields)))
    for row in fps:
        jsd = js_distance([float(row[field]) for field in spectrum_fields], [float(target[field]) for field in spectrum_fields])
        terms = []
        for field in scalar_fields:
            low, high = ranges[field]
            scale = high - low if high > low else 1
            terms.append(((float(row[field]) - float(target[field])) / scale) ** 2)
        rms = math.sqrt(sum(terms) / len(terms))
        checks.append((f"distance_{row['corpus_id']}", abs(jsd - float(row["spectrum_js_distance"])) < 1e-12 and abs(rms - float(row["scalar_rms_distance"])) < 1e-12 and abs((jsd + rms) / 2 - float(row["structural_distance_to_voynich"])) < 1e-12))

    all_rank = [row for row in ranking if row["ranking_scope"] == "ALL_MATCHED"]
    expected_order = [row["corpus_id"] for row in sorted((row for row in fps if row["capacity_state"] == "MATCHED_12000" and row["corpus_id"] != "VOYNICH_MATCHED"), key=lambda row: (float(row["structural_distance_to_voynich"]), row["corpus_id"]))]
    checks.append(("all_rank_exact", [row["corpus_id"] for row in all_rank] == expected_order))
    checks.append(("closest_exact", result["closest_all_matched"][0]["corpus_id"] == expected_order[0] == "OLD_ITALIAN_UD_CONTROL"))
    family_members: dict[str, list[float]] = defaultdict(list)
    for row in fps:
        if row["capacity_state"] == "MATCHED_12000" and row["corpus_id"] != "VOYNICH_MATCHED":
            family_members[row["family"]].append(float(row["structural_distance_to_voynich"]))
    checks.append(("family_means", all(abs(float(row["mean_structural_distance"]) - sum(family_members[row["family"]]) / len(family_members[row["family"]])) < 1e-12 for row in family)))

    checks.append(("voynich_ap_negative", float(target["ap_gain_over_best_string"]) < 0))
    checks.append(("voynich_qright_ap_negative", float(target["voynich_qright_ap_gain"]) < 0))
    checks.append(("no_f84_records", not any("f84r" in str(value) for row in corpus["records"] for value in row.values())))
    checks.append(("claim_ceiling", "no language identification" in result["claim_ceiling"].lower() and "no phoneme" in result["claim_ceiling"].lower()))
    checks.append(("ledger_rows", "GDT003FP_CKPT001" in LEDGER.read_text(encoding="utf-8") and "GDT003FP_CKPT002" in LEDGER.read_text(encoding="utf-8")))

    failures = [name for name, passed in checks if not passed]
    validation = {
        "schema": "GDT003_STRUCTURAL_FINGERPRINT_VALIDATION_V1",
        "status": "PASS" if not failures else "FAIL",
        "checks": len(checks), "failures": failures,
        "result_sha256": sha(RESULT),
        "validator_sha256": sha(Path(__file__)),
        "scope": "Independent artifact hashes, corpus/count accounting, transformation totals, baseline gains, distance arithmetic, ranks, family aggregation, f84 exclusion, and claim ceiling. Does not redownload external corpora or independently rerun the nested search.",
    }
    OUT.write_text(json.dumps(validation, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(validation, sort_keys=True))
    if failures:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
