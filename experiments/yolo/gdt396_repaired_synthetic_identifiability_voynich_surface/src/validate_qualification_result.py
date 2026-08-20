#!/usr/bin/env python3
"""Independent reconstruction of the negative GDT396 qualification result."""

from __future__ import annotations

import csv
import gzip
import hashlib
import json
import math
import statistics
from collections import Counter, defaultdict
from pathlib import Path


def repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("repository root not found")


ROOT = repo_root(Path(__file__).resolve())
EXP = ROOT / "experiments/yolo/gdt396_repaired_synthetic_identifiability_voynich_surface"
METRICS = EXP / ".work/claims/gdt396_qualification_metrics.tsv"
QUAL = EXP / "artifacts/gdt396_decoder_qualification.json"
RESULT = EXP / "artifacts/gdt396_result.json"
FREEZE = EXP / "artifacts/gdt396_result_freeze.json"
OUTPUT = EXP / "artifacts/gdt396_validation.json"
REPRESENTATION_ORDER = (
    "FULL_GROUP", "HOST_LIKE", "COMPOSITE_STATE", "INFERRED_COMPONENTS",
    "CONSTRUCTION_SPAN", "RECORD_TOPOLOGY", "MULTI_RESOLUTION",
)
SEMANTIC = {
    "SEMANTIC_ENTITY_IDENTITY", "CURRENT_PRODUCTIVE_COMPONENT", "CURRENT_SHARED_MEANING",
    "FUNCTION_OPERATOR_CLASS", "SEMANTIC_CATEGORY", "PRODUCTIVE_MORPHOLOGY",
    "TEMPORAL_STATE_GATE", "GENERIC_RELATION", "COORDINATOR_RELATION",
    "ALTERNATIVE_RELATION", "REFERENCE_ANAPHORA", "ENTITY_REUSE_ANTECEDENT",
}


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for block in iter(lambda: fh.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def content_hash(value: dict) -> str:
    payload = dict(value)
    payload.pop("content_sha256", None)
    return hashlib.sha256(json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def detail(row: dict) -> dict:
    return json.loads(row["metrics_json"])


def strict_seed_pass(row: dict) -> tuple[bool, float]:
    if row["status"] != "SCORED":
        return False, -math.inf
    value = detail(row); endpoint = row["endpoint"]; coverage = float(row["coverage"])
    if endpoint in {"PARTITION", "RECORD_PARTITION"}:
        margins = (coverage-.80, value["nonsingleton_clusters"]-3, .60-value["singleton_fraction"], .75-value["largest_cluster_fraction"], value["cocluster_pair_ratio"]-.25, 4.0-value["cocluster_pair_ratio"], value["nmi"]-.50, value["ari"]-.30, value["pair_f1"]-.40)
    elif endpoint == "BINARY":
        margins = (coverage-.60, value["balanced_accuracy"]-.70, value["mcc"]-.30, .30-value["fdr"])
    elif endpoint == "RANKED_TARGET":
        margins = (int(row["eligible_n"])-30, coverage-.60, value["mrr"]-.35, value["hits1"]-.20, value["ndcg5"]-.45, value["mrr_gain"]-.10)
        if row["property_id"] == "GENERIC_RELATION":
            margins += (value.get("relation_type_count", 0)-3,)
    elif endpoint == "SCOPE":
        margins = (coverage-.60, value["median_iou"]-.50, value["exact_rate"]-.25, float(row["gain"])-.10)
    elif endpoint == "MORPHOLOGY":
        margins = (coverage-.60, value["macro_f1"]-.60, value["mean_ap"]-.50, .10-value["current_false_discovery_rate"], value["recurrent_component_count"]-1, float(value["productive_fossil_component_ids_disjoint"])-1, value["proper_substring_fraction"]-.50)
    else:
        return False, -math.inf
    return all(item >= -1e-12 for item in margins), min(margins)


def close(a, b) -> bool:
    if a is None or b is None:
        return a is b
    return math.isclose(float(a), float(b), rel_tol=1e-12, abs_tol=1e-12)


def main() -> int:
    if OUTPUT.exists():
        raise RuntimeError(f"refusing to overwrite {OUTPUT}")
    with METRICS.open(encoding="utf-8", newline="") as fh:
        data = list(csv.DictReader(fh, delimiter="\t"))
    qual = json.loads(QUAL.read_text(encoding="utf-8"))
    result = json.loads(RESULT.read_text(encoding="utf-8"))
    frozen = json.loads(FREEZE.read_text(encoding="utf-8"))
    checks: dict[str, bool] = {}
    checks["matrix_count_domain"] = len(data) == 117100 and {row["phase"] for row in data} == {"QUALIFICATION"} and {row["world_id"] for row in data} == {f"W{i:02d}" for i in range(1, 11)} and {row["surface_id"] for row in data} == {"FREE_SURFACE", "VOYNICH_SURFACE"} and {int(row["corpus_seed"]) for row in data} == set(range(3961000, 3961005))
    checks["qualification_hash_content"] = qual.get("metrics_sha256") == sha256(METRICS) and qual.get("content_sha256") == content_hash(qual)
    checks["result_hash_content"] = result.get("qualification_result_sha256") == sha256(QUAL) and result.get("content_sha256") == content_hash(result)
    checks["freeze_hash_content_bindings"] = frozen.get("content_sha256") == content_hash(frozen) and all(sha256(EXP / path) == digest for path, digest in frozen.get("bindings", {}).items())

    grouped = defaultdict(lambda: defaultdict(list)); families = {}
    for row in data:
        if row["endpoint"] == "ARCHITECTURE_BINARY" or row["method_variant"] != "PRIMARY":
            continue
        key = (row["decoder_id"], row["property_id"], row["representation_id"], row["surface_id"])
        grouped[key][row["world_id"]].append(strict_seed_pass(row)); families[row["decoder_id"]] = row["method_family"]
    reconstructed = {}
    for key, worlds in grouped.items():
        decoder, prop, representation, surface = key
        passed_worlds = []; margins = []
        for world, values in sorted(worlds.items()):
            if len(values) != 5:
                raise RuntimeError(f"incomplete route {key}/{world}")
            if world != "W10" and sum(flag for flag, _ in values) >= 4:
                passed_worlds.append(world)
            margins.extend(margin for flag, margin in values if flag and math.isfinite(margin))
        w10 = [row for row in data if row["decoder_id"] == decoder and row["property_id"] == prop and row["representation_id"] == representation and row["surface_id"] == surface and row["world_id"] == "W10" and row["method_variant"] == "PRIMARY"]
        rates = []
        if prop in SEMANTIC:
            if len(w10) != 5 or len({row["corpus_seed"] for row in w10}) != 5:
                raise RuntimeError(f"incomplete W10 route {key}")
            if {row["status"] for row in w10} != {"UNSUPPORTED"}:
                for row in w10:
                    value = detail(row); rate = value.get("resolved_without_truth_rate", value.get("positive_prediction_rate"))
                    if rate is None:
                        raise RuntimeError(f"missing W10 rate {key}")
                    rates.append(float(rate))
        w10_ok = not rates or max(rates) <= .10
        reconstructed[key] = {
            "worlds": passed_worlds, "margin": statistics.median(margins) if margins else None,
            "rates": rates, "w10_ok": w10_ok, "route": len(passed_worlds) >= 2 and w10_ok,
        }
    result_routes = {(row["decoder_id"], row["property_id"], row["representation_id"], row["surface_id"]): row for row in qual["route_rows"]}
    route_equal = set(result_routes) == set(reconstructed)
    for key, expected in reconstructed.items():
        row = result_routes[key]
        route_equal &= row["meaningful_worlds_passing"] == expected["worlds"] and row["meaningful_world_pass_count"] == len(expected["worlds"]) and close(row["median_positive_margin"], expected["margin"]) and len(row["w10_false_positive_rates"]) == len(expected["rates"]) and all(close(a, b) for a, b in zip(row["w10_false_positive_rates"], expected["rates"])) and row["w10_veto_pass"] == expected["w10_ok"] and row["route_qualifies_before_representation_freeze"] == expected["route"]
    checks["routes_reconstructed"] = route_equal and len(reconstructed) == 1350 and sum(value["route"] for value in reconstructed.values()) == 18

    selections = {}
    for prop, surface in sorted({(key[1], key[3]) for key in reconstructed}):
        candidates = []
        for index, representation in enumerate(REPRESENTATION_ORDER):
            values = [(key, value) for key, value in reconstructed.items() if key[1] == prop and key[2] == representation and key[3] == surface and value["route"]]
            margins = [value["margin"] for _, value in values if value["margin"] is not None]
            candidates.append((len(values), statistics.median(margins) if margins else -math.inf, -index, representation))
        selections[(prop, surface)] = max(candidates)[3]
    result_selections = {(row["property_id"], row["surface_id"]): row["representation_id"] for row in qual["representation_selections"]}
    checks["selections_reconstructed"] = selections == result_selections and len(selections) == 50

    suite = {}
    decoders = sorted({key[0] for key in reconstructed})
    for decoder in decoders:
        lexical = all(any(key[0] == decoder and key[1] == "LEXICAL_IDENTITY" and key[3] == surface and value["route"] for key, value in reconstructed.items()) for surface in ("FREE_SURFACE", "VOYNICH_SURFACE"))
        relation = all(any(key[0] == decoder and key[1] in {"GENERIC_RELATION", "ENTITY_REUSE_ANTECEDENT"} and key[3] == surface and value["route"] for key, value in reconstructed.items()) for surface in ("FREE_SURFACE", "VOYNICH_SURFACE"))
        suite[decoder] = {"easy_equality": lexical, "simple_recurrent_relation": relation, "schema_and_determinism": True, "qualified": lexical and relation}
    checks["decoder_suite_reconstructed"] = suite == qual["decoder_wide_suite"] and sum(row["easy_equality"] for row in suite.values()) == 4 and sum(row["simple_recurrent_relation"] for row in suite.values()) == 0 and sum(row["qualified"] for row in suite.values()) == 0

    qualified = []
    for key, value in reconstructed.items():
        decoder, prop, representation, surface = key
        if value["route"] and selections[(prop, surface)] == representation and suite[decoder]["qualified"]:
            qualified.append(key)
    checks["qualified_routes_panels_zero"] = not qualified and qual["qualified_routes"] == [] and len(qual["confirmation_panels"]) == 50 and not any(row["confirmation_eligible"] for row in qual["confirmation_panels"])
    checks["status_mandatory"] = qual["status"] == result["status"] == "NO_CONFIRMATION_ELIGIBLE_PROPERTY"

    rated = [row for row in qual["route_rows"] if row["w10_false_positive_rates"]]
    checks["w10_arithmetic"] = len(rated) == 94 and sum(not row["w10_veto_pass"] for row in rated) == 78 and math.isclose(result["semantic_route_false_positive_fraction"], 78/94)
    checks["architecture_function_zero"] = len(qual["architecture_diagnostics"]) == 360 and len(qual["architecture_qualification"]) == 8 and sum(row["qualified"] for row in qual["architecture_qualification"]) == 0 and len(qual["function_multiconstraint_seed_diagnostics"]) == 500 and len(qual["function_multiconstraint_routes"]) == 10 and sum(row["qualified"] for row in qual["function_multiconstraint_routes"]) == 0

    matrix = EXP / "artifacts/gdt396_qualification_identifiability_matrix.tsv.gz"
    with gzip.open(matrix, "rb") as fh:
        decompressed_hash = hashlib.sha256(fh.read()).hexdigest()
    checks["strict_matrix_lossless"] = sha256(matrix) == result["strict_matrix_sha256"] and decompressed_hash == sha256(METRICS)
    checks["compact_artifact_hashes"] = sha256(EXP / "artifacts/gdt396_qualification_route_matrix.tsv") == result["route_matrix_sha256"] and sha256(EXP / "artifacts/gdt396_property_decisions.tsv") == result["property_decisions_sha256"]
    with (EXP / "artifacts/gdt396_property_decisions.tsv").open(encoding="utf-8", newline="") as fh:
        properties = list(csv.DictReader(fh, delimiter="\t"))
    checks["property_decision_counts"] = Counter(row["classification"] for row in properties) == Counter({"CURRENT_DECODER_INSTRUMENT_FALSE_NEGATIVE": 13, "SEMANTICS_LIGHT_FALSE_POSITIVE": 12, "REQUIRES_EXTERNAL_GROUNDING": 1})

    correction_freeze = EXP / "artifacts/gdt396_qualification_execution_correction_freeze_v2.json"
    correction_validation = EXP / "artifacts/gdt396_qualification_execution_correction_validation_v2.json"
    cv = json.loads(correction_validation.read_text(encoding="utf-8"))
    checks["correction_lineage"] = cv.get("status") == "PASS" and cv.get("freeze_sha256") == sha256(correction_freeze) and cv.get("validator_sha256") == sha256(EXP / "src/validate_qualification_execution_correction_v2.py")
    confirmation_paths = [EXP / "artifacts/gdt396_confirmation_claim_freeze.json", EXP / "artifacts/gdt396_confirmation_result.json", EXP / ".work/corpora/gdt396_confirmation_paired_manifest_v2.tsv", EXP / ".work/claims/gdt396_confirmation_claim_manifest.tsv", EXP / ".work/claims/gdt396_confirmation_metrics.tsv"]
    checks["confirmation_absent"] = not any(path.exists() for path in confirmation_paths) and result["confirmation_generated"] is False
    checks["seals"] = result.get("voynich_rows") == 0 and not result["f84"]["accessed"] and not result["f84r"]["accessed"]

    validator_hash = sha256(Path(__file__).resolve())
    output = {
        "schema": "GDT396_VALIDATION_V1", "status": "PASS" if all(checks.values()) else "FAIL",
        "checks": checks, "passed": sum(checks.values()), "total": len(checks),
        "result_freeze_sha256": sha256(FREEZE), "result_sha256": sha256(RESULT),
        "qualification_result_sha256": sha256(QUAL), "metrics_sha256": sha256(METRICS),
        "validator_sha256": validator_hash, "voynich_rows": 0,
        "f84": {"accessed": False, "rows": 0}, "f84r": {"accessed": False, "rows": 0},
    }
    output["content_sha256"] = content_hash(output)
    OUTPUT.write_text(json.dumps(output, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(OUTPUT, output["status"], f"{output['passed']}/{output['total']}")
    return 0 if output["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
