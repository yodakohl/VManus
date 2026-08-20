#!/usr/bin/env python3
"""GDT395 scorer conformed to the frozen independent V1 output specification.

This module retains the original scorer's authenticated claim/oracle ingestion
and metric implementation.  It changes only aggregate serialization and the
diagnostic definitions that the independently frozen validator specified before
oracle access.  It does not import the validator.
"""

from __future__ import annotations

import csv
import hashlib
import itertools
import json
import math
import statistics
import tempfile
from pathlib import Path
from typing import Any, Iterable

import score_identifiability_v4 as v4

v3 = v4.v3
v1 = v4.v1

NA = "NA"
SCOREABLE = (
    "LEXICAL_IDENTITY", "SEMANTIC_ENTITY_IDENTITY",
    "HISTORICAL_STEM_ANCESTRY", "FUNCTION_CLASS", "ENTITY_REUSE",
    "REGISTER_LOCAL_VARIANT", "SEMANTIC_CATEGORY",
)
HOLD = tuple(prop for prop in v1.PROPERTIES if prop not in SCOREABLE)
QUALIFICATIONS = {
    "LEXICAL_IDENTITY": "ANONYMOUS_LEXICAL_ID_PARTITION_NOT_WORD_MEANING",
    "SEMANTIC_ENTITY_IDENTITY": "ANONYMOUS_ENTITY_COIDENTITY_ONLY",
    "HISTORICAL_STEM_ANCESTRY": "SHARED_HISTORICAL_STEM_PARTITION_NOT_GENEALOGY",
    "PRODUCTIVE_MORPHOLOGY": "UNSCORED_INTERFACE_HOLD_OPAQUE_COMPONENT_ID_NOT_BOOLEAN",
    "FOSSILIZED_MORPHOLOGY": "UNSCORED_INTERFACE_HOLD_OPAQUE_COMPONENT_ID_NOT_BOOLEAN",
    "FUNCTION_CLASS": "ANONYMOUS_FUNCTION_CLASS_PARTITION_ONLY",
    "COORDINATOR_RELATION": "UNSCORED_INTERFACE_HOLD_NO_TYPED_RANKED_TARGET_MAPPING",
    "ALTERNATIVE_RELATION": "UNSCORED_INTERFACE_HOLD_NO_TYPED_RANKED_TARGET_MAPPING",
    "REFERENCE_ANAPHORA": "UNSCORED_INTERFACE_HOLD_NO_DIRECT_ORACLE_REFERENCE_TARGET",
    "TEMPORAL_STATE_GATE": "UNSCORED_INTERFACE_HOLD_NO_MATCHING_CLAIM_TRUTH_FIELD",
    "SCOPE": "UNSCORED_INTERFACE_HOLD_NO_VALIDATED_EVENT_ORDER_CONTRACT",
    "ENTITY_REUSE": "RECURRING_ANONYMOUS_ENTITY_IDS_ONLY_SINGLETON_TRUTH_INELIGIBLE",
    "OPERATOR_CLASS": "UNSCORED_INTERFACE_HOLD_NO_ORACLE_OPERATOR_CLASS",
    "RECORD_SCHEMA": "UNSCORED_INTERFACE_HOLD_NO_RECORD_ID_IN_ACCEPTED_INPUT",
    "REGISTER_LOCAL_VARIANT": "AUTHENTIC_REGISTER_REALIZATION_IDENTITY_NOT_MEANING",
    "SEMANTIC_CATEGORY": "ANONYMOUS_CATEGORY_PARTITION_NOT_CATEGORY_MEANING",
    "ACTUAL_LEXICAL_MEANING": "UNSCORED_INTERFACE_HOLD_REQUIRES_EXTERNAL_GROUNDING",
}
STRESS_TESTS = (
    "EXACT_COMPOSITE_AS_WORD",
    "UNIVERSAL_VS_WORLD_LOCAL_COEFFICIENTS",
    "FREQUENCY_POSITION_RECURRENCE_RESIDUALIZATION",
    "SCALAR_ROLE_BOTTLENECKS",
    "FIXED_SHORT_HORIZON_OUTCOMES",
    "MULTI_CONSTRAINT_INTERSECTION_REPLACEMENT",
)
WORLD_FAMILIES = {
    "W01": "TECHNICAL_SCRIBAL_SHORTHAND",
    "W02": "ORGANIC_CODEBOOK",
    "W03": "ENGINEERED_CATALOGUE_CODE",
    "W04": "PROCEDURAL_RECIPE_NOTATION",
    "W05": "MNEMONIC_RITUAL_LEGACY",
    "W06": "ORGANIC_CATALOGUE_INDEX",
    "W07": "HYBRID_WORD_CODE_QUANTITY",
    "W08": "DIVERGED_MULTI_SCHOOL_NOTATION",
    "W09": "MEANINGFUL_RELATIONAL_SYSTEM",
    "W10": "SEMANTICS_LIGHT_GENERATOR",
}
WORLD_REP_FIELDS = (
    "view", "property", "world_id", "representation", "status",
    "decoders_scored", "decoders_clear", "luna_decoders_clear",
    "median_decoder_clear", "endpoint_qualification", "coverage", "nmi",
    "ari", "pair_f1", "balanced_accuracy", "mcc", "fdr", "top1", "mrr",
    "mrr_above_chance", "endpoint_accuracy", "exact_scope_accuracy",
    "interval_iou", "target_distance_mae", "primary_index",
    "false_positive_rate", "co_cluster_fpr",
)
DECISION_FIELDS = (
    "property", "decision", "endpoint_qualification", "exploratory_pattern",
    "representation", "worlds_clear", "meaningful_worlds_clear",
    "clear_world_ids", "clear_world_families", "w10_false_positive_rate",
    "w10_false_positive_upper95", "w10_guard_pass",
    "organic_confusion_flag", "organic_confusion_representations",
    "raw_p_value", "holm_adjusted_p_value", "inference_status",
)
W10_FIELDS = (
    "property", "representation", "endpoint_qualification", "panels",
    "seed_false_positive_rates", "false_positive_rate",
    "false_positive_upper95", "upper95_method", "point_guard_pass",
    "confirmatory_guard_pass", "inference_status",
)
ARCH_FIELDS = (
    "decoder_id", "endpoint", "truth_basis", "n", "nmi", "ari",
    "pair_f1", "balanced_accuracy", "mcc", "fdr",
)
STRESS_FIELDS = ("stress_test", "status")


def fmt(value: float | None) -> str:
    if value is None:
        return NA
    if value == 0:
        value = 0.0
    return format(value, ".12g")


def bool_text(value: bool) -> str:
    return "true" if value else "false"


def median(values: Iterable[float | None]) -> float | None:
    kept = [float(value) for value in values if value is not None]
    return float(statistics.median(kept)) if kept else None


def primary(nmi: float | None, ari: float | None, pair_f1: float | None) -> float | None:
    if nmi is None or ari is None or pair_f1 is None:
        return None
    return min(nmi / 0.35, ari / 0.20, pair_f1 / 0.35)


def blank_values() -> dict[str, str]:
    return {field: NA for field in (
        "eligible_n", "prediction_n", "coverage", "nmi", "ari", "pair_f1",
        "balanced_accuracy", "mcc", "fdr", "top1", "mrr",
        "mrr_above_chance", "endpoint_accuracy", "exact_scope_accuracy",
        "interval_iou", "target_distance_mae", "false_discoveries",
        "absent_truth_n", "unresolved_n", "invalid_n", "co_cluster_fpr",
        "false_positive_rate", "primary_index", "threshold_pass",
    )}


def hold_row(raw: dict[str, Any], pair: bool) -> dict[str, str]:
    row = {
        "view": "pair" if pair else "authentic",
        "world_id": str(raw["world_id"]),
        "corpus_seed": str(raw["corpus_seed"]),
        "representation": str(raw["representation"]),
        "decoder_id": str(raw["decoder_id"]),
        "property": str(raw["property"]),
        "kind": "UNSCORED",
        "status": "UNSCORED_PAIR_INTERFACE_HOLD" if pair else "UNSCORED_INTERFACE_HOLD",
        "endpoint_qualification": QUALIFICATIONS[str(raw["property"])],
        "metric_note": "PAIR_ENDPOINTS_HARD_DISABLED_NO_RECORD_ID" if pair else "FROZEN_INTERFACE_HOLD",
    }
    row.update(blank_values())
    return row


def scored_row(raw: dict[str, Any]) -> tuple[dict[str, str], dict[str, Any]]:
    capacity = raw["status"] == "SCORED"
    nmi = float(raw["nmi"]) if capacity and raw["nmi"] is not None else None
    ari = float(raw["ari"]) if capacity and raw["ari"] is not None else None
    pair_f1 = float(raw["pair_f1"]) if capacity and raw["pair_f1"] is not None else None
    index = primary(nmi, ari, pair_f1)
    passed = bool(capacity and nmi is not None and ari is not None and pair_f1 is not None
                  and nmi >= 0.35 and ari >= 0.20 and pair_f1 >= 0.35)
    eligible_n = int(raw["eligible_n"])
    prediction_n = int(raw["prediction_n"]) - int(raw["false_discoveries"])
    coverage = prediction_n / eligible_n if eligible_n else None
    row = {
        "view": "authentic", "world_id": str(raw["world_id"]),
        "corpus_seed": str(raw["corpus_seed"]),
        "representation": str(raw["representation"]),
        "decoder_id": str(raw["decoder_id"]), "property": str(raw["property"]),
        "kind": "CLUSTERING", "status": str(raw["status"]),
        "eligible_n": str(eligible_n), "prediction_n": str(prediction_n),
        "coverage": fmt(coverage),
        "nmi": fmt(nmi), "ari": fmt(ari), "pair_f1": fmt(pair_f1),
        "balanced_accuracy": NA, "mcc": NA, "fdr": NA, "top1": NA,
        "mrr": NA, "mrr_above_chance": NA, "endpoint_accuracy": NA,
        "exact_scope_accuracy": NA, "interval_iou": NA,
        "target_distance_mae": NA,
        "false_discoveries": str(raw["false_discoveries"]),
        "absent_truth_n": str(raw["absent_truth_n"]),
        "unresolved_n": str(raw["unresolved_n"]), "invalid_n": "0",
        "co_cluster_fpr": fmt(float(raw["co_cluster_fpr"]) if raw["co_cluster_fpr"] is not None else None),
        "false_positive_rate": fmt(float(raw["false_positive_rate"]) if raw["false_positive_rate"] is not None else None),
        "primary_index": fmt(index), "threshold_pass": bool_text(passed),
        "endpoint_qualification": QUALIFICATIONS[str(raw["property"])],
        "metric_note": "PRIVATE_PER_EVENT_ABSTENTION_SINGLETONS",
    }
    metric = {
        "status": str(raw["status"]), "capacity": capacity,
        "coverage": coverage,
        "nmi": nmi, "ari": ari, "pair_f1": pair_f1,
        "primary_index": index,
        "false_positive_rate": (float(raw["false_positive_rate"])
                                if raw["false_positive_rate"] is not None else None),
        "co_cluster_fpr": (float(raw["co_cluster_fpr"])
                           if raw["co_cluster_fpr"] is not None else None),
        "passed": passed,
    }
    return row, metric


def normalize_panels(raw_panel: list[dict[str, Any]]) -> tuple[list[dict[str, str]], list[dict[str, str]], dict[tuple[str, int, str, str, str], dict[str, Any]]]:
    panel: list[dict[str, str]] = []
    pair_panel: list[dict[str, str]] = []
    metrics: dict[tuple[str, int, str, str, str], dict[str, Any]] = {}
    for raw in raw_panel:
        if raw["view"] == "pair":
            pair_panel.append(hold_row(raw, True))
        elif raw["property"] in HOLD:
            panel.append(hold_row(raw, False))
        else:
            row, metric = scored_row(raw)
            panel.append(row)
            metrics[(str(raw["world_id"]), int(raw["corpus_seed"]),
                     str(raw["representation"]), str(raw["decoder_id"]),
                     str(raw["property"]))] = metric
    return panel, pair_panel, metrics


def decoder_aggregate(metrics: dict, world: str, rep: str, decoder: str, prop: str) -> dict[str, Any]:
    rows = [metrics[(world, seed, rep, decoder, prop)] for seed in v1.HELD_SEEDS]
    passes = [bool(row["passed"]) for row in rows]
    answer: dict[str, Any] = {"clear": sum(passes) >= 3}
    for field in ("coverage", "nmi", "ari", "pair_f1", "primary_index",
                  "false_positive_rate", "co_cluster_fpr"):
        answer[field] = median(row[field] for row in rows)
    return answer


def world_rows(metrics: dict, implementations: dict[str, str]) -> tuple[list[dict[str, str]], dict]:
    decoders = sorted(implementations)
    rows: list[dict[str, str]] = []
    aggregates: dict = {}
    for prop in v1.PROPERTIES:
        for world in v1.WORLDS:
            for rep in v1.REPRESENTATIONS:
                row = {field: NA for field in v1.AGG_METRICS}
                if prop in HOLD:
                    row.update({
                        "view": "authentic", "property": prop, "world_id": world,
                        "representation": rep, "status": "UNSCORED_INTERFACE_HOLD",
                        "decoders_scored": "0", "decoders_clear": "0",
                        "luna_decoders_clear": "0", "median_decoder_clear": "false",
                        "endpoint_qualification": QUALIFICATIONS[prop],
                    })
                    rows.append(row)
                    continue
                per = {decoder: decoder_aggregate(metrics, world, rep, decoder, prop)
                       for decoder in decoders}
                clear = [decoder for decoder in decoders if per[decoder]["clear"]]
                luna = [decoder for decoder in clear if implementations[decoder] == "LUNA"]
                world_clear = len(clear) >= 3 and len(luna) >= 2
                coords = {field: median(value[field] for value in per.values())
                          for field in ("coverage", "nmi", "ari", "pair_f1", "primary_index",
                                        "false_positive_rate", "co_cluster_fpr")}
                aggregates[(prop, world, rep)] = {
                    "world_clear": world_clear, "decoders_clear": tuple(clear),
                    "luna_clear": tuple(luna), **coords,
                }
                row.update({
                    "view": "authentic", "property": prop, "world_id": world,
                    "representation": rep, "status": "SCORED",
                    "decoders_scored": str(len(decoders)), "decoders_clear": str(len(clear)),
                    "luna_decoders_clear": str(len(luna)),
                    "median_decoder_clear": bool_text(world_clear),
                    "endpoint_qualification": QUALIFICATIONS[prop],
                    "coverage": fmt(coords["coverage"]), "nmi": fmt(coords["nmi"]),
                    "ari": fmt(coords["ari"]), "pair_f1": fmt(coords["pair_f1"]),
                    "primary_index": fmt(coords["primary_index"]),
                    "false_positive_rate": fmt(coords["false_positive_rate"]),
                    "co_cluster_fpr": fmt(coords["co_cluster_fpr"]),
                })
                rows.append(row)
    return rows, aggregates


def exact_upper95(values: list[float]) -> float:
    samples = [float(statistics.median(values[index] for index in draw))
               for draw in itertools.product(range(5), repeat=5)]
    samples.sort()
    return samples[math.ceil(0.95 * len(samples)) - 1]


def w10_rows(metrics: dict, implementations: dict[str, str]) -> tuple[list[dict[str, str]], dict]:
    decoders = sorted(implementations)
    rows: list[dict[str, str]] = []
    diagnostics: dict = {}
    for prop in SCOREABLE:
        for rep in v1.REPRESENTATIONS:
            seed_rates: list[float] = []
            complete = True
            for seed in v1.HELD_SEEDS:
                rates = [metrics[("W10", seed, rep, decoder, prop)]["false_positive_rate"]
                         for decoder in decoders]
                if any(rate is None for rate in rates):
                    complete = False
                    break
                seed_rates.append(float(statistics.median(rates)))
            if complete:
                point = float(statistics.median(seed_rates))
                upper = exact_upper95(seed_rates)
                guard = upper <= 0.10
                encoded = "|".join(f"{seed}:{fmt(rate)}"
                                   for seed, rate in zip(v1.HELD_SEEDS, seed_rates))
            else:
                point = upper = None
                guard = False
                encoded = NA
            diagnostics[(prop, rep)] = {"point": point, "upper": upper, "guard": guard}
            rows.append({
                "property": prop, "representation": rep,
                "endpoint_qualification": QUALIFICATIONS[prop], "panels": "25",
                "seed_false_positive_rates": encoded,
                "false_positive_rate": fmt(point), "false_positive_upper95": fmt(upper),
                "upper95_method": "EXACT_SEED_CLUSTER_BOOTSTRAP_3125_NEAREST_RANK",
                "point_guard_pass": bool_text(guard),
                "confirmatory_guard_pass": "false",
                "inference_status": "EXPLORATORY_UNCONFIRMED",
            })
    return rows, diagnostics


def decision_rows(aggregates: dict, w10: dict) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for prop in v1.PROPERTIES:
        if prop in HOLD:
            rows.append({
                "property": prop, "decision": "UNSCORED_INTERFACE_HOLD",
                "endpoint_qualification": QUALIFICATIONS[prop],
                "exploratory_pattern": "UNSCORED_INTERFACE_HOLD",
                "representation": "ALL", "worlds_clear": NA,
                "meaningful_worlds_clear": NA, "clear_world_ids": "NONE",
                "clear_world_families": NA, "w10_false_positive_rate": NA,
                "w10_false_positive_upper95": NA, "w10_guard_pass": "false",
                "organic_confusion_flag": "UNSCORED_INTERFACE_HOLD",
                "organic_confusion_representations": "NONE", "raw_p_value": NA,
                "holm_adjusted_p_value": NA, "inference_status": "UNSCORED_INTERFACE_HOLD",
            })
            continue
        candidates = []
        for order, rep in enumerate(v1.REPRESENTATIONS):
            clear = [world for world in v1.WORLDS if aggregates[(prop, world, rep)]["world_clear"]]
            meaningful = [world for world in clear if world != "W10"]
            guard = w10[(prop, rep)]
            upper = guard["upper"] if guard["upper"] is not None else math.inf
            candidates.append((int(guard["guard"]), len(meaningful), -upper, -order,
                               rep, clear, guard))
        chosen = max(candidates)
        rep, clear, guard = chosen[4], chosen[5], chosen[6]
        meaningful = [world for world in clear if world != "W10"]
        if guard["guard"] and len(meaningful) >= 7:
            pattern = "POINT_THRESHOLD_GENERAL_PATTERN"
        elif guard["guard"] and 2 <= len(meaningful) <= 6:
            pattern = "POINT_THRESHOLD_FAMILY_SPECIFIC_PATTERN"
        else:
            pattern = "NO_POINT_THRESHOLD_PATTERN"
        rows.append({
            "property": prop, "decision": "EXPLORATORY_UNCONFIRMED",
            "endpoint_qualification": QUALIFICATIONS[prop],
            "exploratory_pattern": pattern, "representation": rep,
            "worlds_clear": str(len(clear)), "meaningful_worlds_clear": str(len(meaningful)),
            "clear_world_ids": "|".join(clear) if clear else "NONE",
            "clear_world_families": NA,
            "w10_false_positive_rate": fmt(guard["point"]),
            "w10_false_positive_upper95": fmt(guard["upper"]),
            "w10_guard_pass": bool_text(bool(guard["guard"])),
            "organic_confusion_flag": "UNSCORED_PAIR_INTERFACE_HOLD",
            "organic_confusion_representations": "NONE", "raw_p_value": NA,
            "holm_adjusted_p_value": NA,
            "inference_status": "EXPLORATORY_UNCONFIRMED_NO_FROZEN_RECORD_BLOCK_NULLS",
        })
    return rows


def architecture_rows(raw: list[dict[str, Any]]) -> list[dict[str, str]]:
    rows = []
    for value in raw:
        rows.append({field: (str(value[field]) if field in {"decoder_id", "endpoint", "truth_basis"}
                             else (str(int(value[field])) if field == "n"
                                   else fmt(float(value[field]) if value[field] is not None else None)))
                     for field in ARCH_FIELDS})
    return rows


def canonical_json_bytes(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("ascii")


def aggregate_hash(items: Iterable[tuple[str, str]]) -> str:
    return hashlib.sha256(canonical_json_bytes({label: digest for label, digest in items})).hexdigest()


def write_tsv(path: Path, fields: tuple[str, ...], rows: list[dict[str, str]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field, NA) for field in fields})


def compact_summary(args: Any, freeze: dict, decisions: list[dict[str, str]]) -> dict[str, Any]:
    bindings = freeze["bindings"]
    roles = {}
    for role in v1.ROLE_NAMES:
        roles[role] = [(entry["path"], entry["sha256"]) for entry in bindings[role]]
    held = []
    handle, reader = v1.open_tsv(args.corpus_manifest)
    try:
        for row in reader:
            seed = int(row["corpus_seed"])
            if seed in v1.HELD_SEEDS:
                held.append((row["oracle_relpath"], row["oracle_sha256"]))
    finally:
        handle.close()
    decision_map = {row["property"]: {
        "decision": row["decision"], "exploratory_pattern": row["exploratory_pattern"],
        "representation": row["representation"],
    } for row in decisions}
    return {
        "schema": "GDT395_IDENTIFIABILITY_SCORE_SUMMARY_V1", "status": "PASS",
        "panel": {
            "worlds": 10, "held_seeds": 5, "representations": 6, "decoders": 5,
            "scoreable_properties": 7, "interface_hold_properties": 10,
            "authentic_claim_files": 1500, "pair_claim_files": 600,
            "world_claim_files": 50, "held_oracle_files": 50,
        },
        "input_sha256": {
            "claims_freeze": v1.sha256_file(args.claims_freeze),
            "claims_validation": v1.sha256_file(args.claims_validation),
            "corpus_manifest": v1.sha256_file(args.corpus_manifest),
            "authentic_event_claims": aggregate_hash(roles["authentic_event_claims"]),
            "pair_event_claims": aggregate_hash(roles["pair_event_claims"]),
            "world_claims": aggregate_hash(roles["world_claims"]),
            "held_oracles": aggregate_hash(held),
        },
        "decisions": decision_map, "endpoint_qualification": dict(QUALIFICATIONS),
        "interface_hold_properties": list(HOLD),
        "confirmatory_promotions_enabled": False,
        "unscored_method_stress_tests": list(STRESS_TESTS),
        "ambiguities": [
            "NO_RECORD_ID_IN_ACCEPTED_SCORER_INPUT",
            "NO_FROZEN_RECORD_BLOCK_NULLS",
            "NO_9999_LOCALITY_PRESERVING_PERMUTATIONS",
            "NO_RANKED_TARGET_INTERFACE",
            "PAIR_ENDPOINTS_HARD_DISABLED",
        ],
        "contains_event_rows": False, "voynich_rows": 0,
    }


def main(argv: list[str] | None = None) -> int:
    v1.open_tsv = v3.open_tsv_v3
    v1.parse_bool = v3.parse_world_boolean_v3
    v1.architecture_scores = v3.architecture_scores_v3
    v1.parse_oracle_scalar = v4.parse_oracle_partition_v4
    args = v1.parse_args(argv)
    role_paths = {
        "authentic_event_claims": args.claims_tsv,
        "pair_event_claims": args.pair_claims_tsv,
        "world_claims": args.world_claim_json,
    }
    _, model_tiers, freeze = v1.validate_blind_gate(
        args.claims_freeze, args.claims_validation, role_paths,
    )
    expected_oracles = v1.validate_oracle_manifest(freeze, args.corpus_manifest, args.oracle_tsv)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    if any(args.output_dir.iterdir()):
        raise v1.Refusal("output directory must be empty")
    with tempfile.TemporaryDirectory(prefix="gdt395_score_v5_") as temp_dir:
        db = v1.create_database(str(Path(temp_dir) / "score.sqlite3"))
        try:
            v1.ingest_claims(db, args.claims_tsv, "main")
            v1.ingest_claims(db, args.pair_claims_tsv, "pair")
            world_claims = v1.ingest_world_claims(args.world_claim_json)
            decoders = v1.validate_claim_dimensions(db, world_claims, model_tiers)
            v1.validate_preoracle_claims(db, decoders)
            v1.ingest_oracle(db, args.oracle_tsv, expected_oracles)
            v1.validate_oracle_joins(db, decoders)
            raw: list[dict[str, Any]] = []
            for view, worlds in (("main", v1.WORLDS), ("pair", tuple(sorted(v1.PAIR_WORLDS)))):
                for world in worlds:
                    for seed in v1.HELD_SEEDS:
                        for rep in v1.REPRESENTATIONS:
                            for decoder in decoders:
                                raw.extend(v1.score_panel(db, view, world, seed, rep, decoder))
        finally:
            db.close()
    panel, pair_panel, metrics = normalize_panels(raw)
    worlds, aggregates = world_rows(metrics, model_tiers)
    w10, w10_diag = w10_rows(metrics, model_tiers)
    decisions = decision_rows(aggregates, w10_diag)
    architecture = architecture_rows(v3.architecture_scores_v3(world_claims, decoders))
    stress = [{"stress_test": name, "status": "UNSCORED_NO_EXPLICIT_DECODER_PREDICTIONS"}
              for name in STRESS_TESTS]
    write_tsv(args.output_dir / "panel_metrics.tsv", v1.METRIC_FIELDS, panel)
    write_tsv(args.output_dir / "pair_panel_metrics.tsv", v1.METRIC_FIELDS, pair_panel)
    write_tsv(args.output_dir / "world_representation_metrics.tsv", WORLD_REP_FIELDS, worlds)
    write_tsv(args.output_dir / "property_decisions.tsv", DECISION_FIELDS, decisions)
    write_tsv(args.output_dir / "w10_false_discoveries.tsv", W10_FIELDS, w10)
    write_tsv(args.output_dir / "architecture_metrics.tsv", ARCH_FIELDS, architecture)
    write_tsv(args.output_dir / "method_stress_tests.tsv", STRESS_FIELDS, stress)
    with (args.output_dir / "summary.json").open("x", encoding="utf-8") as handle:
        json.dump(compact_summary(args, freeze, decisions), handle, indent=2,
                  sort_keys=True, ensure_ascii=True, allow_nan=False)
        handle.write("\n")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except v1.Refusal as exc:
        print(f"REFUSED: {exc}", file=v1.sys.stderr)
        raise SystemExit(2)
