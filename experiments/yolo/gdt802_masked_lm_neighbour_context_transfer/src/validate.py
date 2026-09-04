#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import re
import subprocess
from collections import Counter, defaultdict
from pathlib import Path


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
EXP = ROOT / "experiments/yolo/gdt802_masked_lm_neighbour_context_transfer"
SRC = EXP / "src"
ART = EXP / "artifacts"
G800 = ROOT / "experiments/yolo/gdt800_terminal_b2_b3_line_final_bridge/artifacts/GDT800_4137_MATCHED_TERMINAL_OCCURRENCES.tsv"
G801 = ROOT / "experiments/yolo/gdt801_terminal_lm_boundary_hierarchy_discriminator/artifacts/GDT801_542_SOURCE_SELECTOR_BOUNDARY_JOIN.tsv"
LINES = ROOT / "experiments/yolo/gdt734_v99r7_recurrent_unknown_family_dispatch/artifacts/V99R7_4128_INTEGRATED_LINE_READER.tsv"
ATLAS = ART / "GDT802_4137_MASKED_NEIGHBOUR_ATLAS.tsv"
FOLDS = ART / "GDT802_326_FOLD_ASSIGNMENTS.tsv"
METRICS = ART / "GDT802_SPARSE_RIDGE_METRICS.tsv"
RAW_AUDIT = ART / "GDT802_RAW_IDENTITY_AUDIT.tsv"
PREDICTIONS = ART / "GDT802_4137_FULL_PREDICTIONS.tsv"
CAPACITY = ART / "GDT802_CONTEXT_CAPACITY.tsv"
COEFFICIENTS = ART / "GDT802_SHARED_CONTEXT_COEFFICIENTS.tsv"
DAIIN = ART / "GDT802_DAIIN_POSITION_CARD.tsv"
SENSITIVITY = ART / "GDT802_SENSITIVITY.tsv"
NULLS = ART / "GDT802_PERMUTATION_NULLS.tsv"
CANDIDATES = ART / "GDT802_CANDIDATE_ADJUDICATION.tsv"
CARD = ART / "GDT802_STRUCTURAL_CARD.tsv"
RESULT = ART / "RESULT.json"
VALIDATION = ART / "VALIDATION.json"
REPORT = EXP / "REPORT.md"
FOLIO_RE = re.compile(r"^(f\d+[rv])")


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def header(path: Path) -> list[str]:
    with path.open(encoding="utf-8", newline="") as handle:
        return next(csv.reader(handle, delimiter="\t"))


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def close(left: float, right: float, tolerance: float = 2e-10) -> bool:
    return math.isclose(left, right, rel_tol=tolerance, abs_tol=1e-13)


def physical_folio(selector: str) -> str:
    match = FOLIO_RE.match(selector)
    if match is None:
        raise ValueError(selector)
    return match.group(1)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--skip-replay", action="store_true")
    args = parser.parse_args()
    checks: list[str] = []

    def check(name: str, condition: bool) -> None:
        assert condition, name
        checks.append(name)

    result = json.loads(RESULT.read_text(encoding="utf-8"))
    unhashed = dict(result)
    content_hash = unhashed.pop("content_hash")
    check("result_content_hash", content_hash == hashlib.sha256(json.dumps(unhashed, sort_keys=True, separators=(",", ":")).encode()).hexdigest())
    for category in ("inputs", "outputs", "implementation"):
        for path, digest in result[category].items():
            check(f"hash:{category}:{path}", sha(ROOT / path) == digest)

    schemas = {
        ATLAS: ["event_ordinal", "occurrence_id", "source_selector", "physical_folio", "locus", "token_index", "token_count", "distance_from_end", "distance_cell", "position_class", "position4", "masked_target", "stem", "terminal", "left_context", "right_context", "left_context_sensitivity", "right_context_sensitivity", "paired_neighbour", "direct_388", "population", "page_fold", "stem_fold", "semantic_export_credit"],
        FOLDS: ["group_type", "group_label", "event_count", "fold"],
        METRICS: ["population", "scheme", "model", "n_events", "m_events", "l_events", "folds", "covered_events", "covered_m", "logloss_nats", "total_logloss_nats", "mean_fold_logloss_nats", "brier", "auc", "gain_vs_p", "gain_vs_s"],
        RAW_AUDIT: ["holdout", "context_channel", "available_events", "eval_events", "informative_strata", "eval_stems", "pairs", "macro_auc", "micro_auc", "baseline_logloss_nats", "context_logloss_nats", "context_gain_nats", "novelty_macro_auc", "novelty_micro_auc", "decision"],
        PREDICTIONS: ["occurrence_id", "population", "terminal", "page_fold", "stem_fold", "page_p", "page_s", "page_c", "page_sc", "cross_p", "cross_c", "page_context_covered", "page_stem_covered", "cross_context_covered", "semantic_export_credit"],
        CAPACITY: ["population", "scheme", "n_events", "physical_folios", "stems", "left_real", "right_real", "both_real", "unique_left", "unique_right", "unique_raw_pairs", "singleton_raw_pairs", "unique_position_pairs", "singleton_position_pairs", "cross_stem_folio_bidirectional_pairs", "context_covered", "context_covered_m", "stem_covered", "stem_covered_m", "paired_neighbour_events"],
        COEFFICIENTS: ["side", "context_surface", "eligible_cross_folds", "global_events", "global_stems", "global_folios", "global_m", "mean_beta_context", "min_beta_context", "max_beta_context", "mean_beta_after_stem", "direct_events", "cache_rest_events", "semantic_export_credit"],
        DAIIN: ["population", "position4", "daiin_l", "daiin_m", "other_l", "other_m", "mh_odds_ratio", "exact_upper_p", "exact_lower_p", "decision", "semantic_export_credit"],
        SENSITIVITY: ["population", "analysis", "masked_events", "ordinary_context_gain", "masked_context_gain", "masked_context_coverage", "decision"],
        NULLS: ["null_id", "strata_fields", "seed", "permutations", "observed_total_gain_nats", "null_mean_total_gain_nats", "null_max_total_gain_nats", "exceed_or_equal", "add_one_p", "interpretation"],
        CANDIDATES: ["candidate_id", "candidate", "decision", "positive_evidence", "counterevidence", "claim_ceiling"],
        CARD: ["card_id", "scope", "structural_tag", "german_display", "confidence", "positive_evidence", "counterevidence", "token_display_rule", "equivalence_license", "component_export", "semantic_export", "plaintext_value"],
    }
    expected_outputs = {path.relative_to(ROOT).as_posix() for path in schemas} | {REPORT.relative_to(ROOT).as_posix()}
    check("result_output_set", set(result["outputs"]) == expected_outputs)
    for path, schema in schemas.items():
        rows = read_tsv(path)
        check(f"schema:{path.name}", header(path) == schema)
        check(f"no_blank:{path.name}", all(all(row[field] != "" for field in schema) for row in rows))

    locks = read_tsv(SRC / "SOURCE_LOCK.tsv")
    check("three_source_locks", len(locks) == 3)
    check("source_locks_relative", all(not Path(row["path"]).is_absolute() for row in locks))
    check("source_locks_match", all(sha(ROOT / row["path"]) == row["sha256"] for row in locks))
    check("six_candidate_specs", {row["candidate_id"] for row in read_tsv(SRC / "CANDIDATE_MODEL_SPECS.tsv")} == {f"C{i}" for i in range(1, 7)})

    source_rows = read_tsv(G800)
    line_rows = read_tsv(LINES)
    join_rows = read_tsv(G801)
    atlas = read_tsv(ATLAS)
    check("source_counts", (len(source_rows), len(line_rows), len(join_rows), len(atlas)) == (4137, 4128, 542, 4137))
    check("atlas_unique_ids", len({row["occurrence_id"] for row in atlas}) == 4137)
    check("atlas_terminal_margin", Counter(row["terminal"] for row in atlas) == Counter({"l": 3484, "m": 653}))
    check("atlas_direct_count", Counter(row["population"] for row in atlas) == Counter({"CACHE_REST_3749": 3749, "DIRECT_388": 388}))
    check("atlas_scope", (len({row["source_selector"] for row in atlas}), len({row["physical_folio"] for row in atlas}), len({row["stem"] for row in atlas})) == (177, 171, 155))
    check("sealed_absent", all(not any(value.startswith("f84") for value in row.values()) for row in atlas + source_rows + line_rows + join_rows))
    check("no_plaintext_export", all(row["semantic_export_credit"].startswith("ZERO") for row in atlas))

    line_map = {(row["page"], row["locus"]): row["zl3b_line"].split() for row in line_rows}
    source_map = {row["occurrence_id"]: row for row in source_rows}
    check("line_map_unique", len(line_map) == len(line_rows))
    check("source_map_unique", len(source_map) == len(source_rows))
    for row in atlas:
        source = source_map[row["occurrence_id"]]
        tokens = line_map[(source["page"], source["locus"])]
        index = int(source["token_index"])
        check(f"exact_target:{row['occurrence_id']}", tokens[index - 1] == source["surface"] and row["stem"] + row["terminal"] == source["surface"])
        check(f"left_join:{row['occurrence_id']}", row["left_context"] == (tokens[index - 2] if index > 1 else "NONE"))
        check(f"right_join:{row['occurrence_id']}", row["right_context"] == (tokens[index] if index < len(tokens) else "NONE"))
        check(f"physical_alias:{row['occurrence_id']}", row["physical_folio"] == physical_folio(row["source_selector"]))
        check(f"masked_target:{row['occurrence_id']}", row["masked_target"] == row["stem"] + "{l|m}")

    running = [row for row in join_rows if row["occurrence_kind"] == "RUNNING_EVENT"]
    endings: dict[str, set[str]] = defaultdict(set)
    for row in running:
        endings[row["stem"]].add(row["terminal"])
    direct_ids = {row["gdt800_occurrence_id"] for row in running if endings[row["stem"]] == {"l", "m"}}
    check("direct_definition", len(direct_ids) == 388 and direct_ids == {row["occurrence_id"] for row in atlas if row["direct_388"] == "1"})

    folds = read_tsv(FOLDS)
    check("fold_rows", len(folds) == 326)
    check("fold_group_counts", Counter(row["group_type"] for row in folds) == Counter({"PHYSICAL_FOLIO": 171, "STEM": 155}))
    page_loads = [0] * 5
    stem_loads = [0] * 5
    for row in folds:
        loads = page_loads if row["group_type"] == "PHYSICAL_FOLIO" else stem_loads
        loads[int(row["fold"])] += int(row["event_count"])
    check("page_fold_loads", page_loads == [828, 828, 827, 827, 827])
    check("stem_fold_loads", stem_loads == [829, 827, 827, 827, 827])
    f95 = {row["page_fold"] for row in atlas if row["source_selector"] in {"f95v1", "f95v2"}}
    check("f95v_cofold", len(f95) == 1)

    metrics = read_tsv(METRICS)
    check("metric_rows", len(metrics) == 36)
    metric_map = {(row["population"], row["scheme"], row["model"]): row for row in metrics}
    check("metric_keys_unique", len(metric_map) == 36)
    expected = {
        ("FULL_4137", "PAGE5", "P"): 0.306809617367,
        ("FULL_4137", "PAGE5", "S"): 0.293300118130,
        ("FULL_4137", "CROSSED5X5", "P"): 0.308956985261,
        ("FULL_4137", "CROSSED5X5", "C"): 0.306303883687,
        ("CACHE_REST_3749", "PAGE5", "S"): 0.289193399080,
        ("CACHE_REST_3749", "CROSSED5X5", "C"): 0.305831259133,
    }
    for key, value in expected.items():
        check(f"metric_value:{key}", close(float(metric_map[key]["logloss_nats"]), value))
    check("rest_stem_gain_positive", float(metric_map[("CACHE_REST_3749", "PAGE5", "S")]["gain_vs_p"]) > 0.015)
    check("rest_sparse_context_gain_positive", float(metric_map[("CACHE_REST_3749", "CROSSED5X5", "C")]["gain_vs_p"]) > 0.001)
    check("cross_stem_unseen", metric_map[("FULL_4137", "CROSSED5X5", "S")]["covered_events"] == "0")

    raw = read_tsv(RAW_AUDIT)
    check("raw_rows", len(raw) == 8)
    raw_map = {(row["holdout"], row["context_channel"]): row for row in raw}
    check("raw_folio_combined_macro_below_half", float(raw_map[("LEAVE_PHYSICAL_FOLIO_OUT", "LEFT_RIGHT_MEAN")]["macro_auc"]) < 0.45)
    check("right_rarity_beats_identity_folio", float(raw_map[("LEAVE_PHYSICAL_FOLIO_OUT", "RIGHT")]["novelty_macro_auc"]) > float(raw_map[("LEAVE_PHYSICAL_FOLIO_OUT", "RIGHT")]["macro_auc"]))
    check("pair_capacity_audit_negative", float(raw_map[("LEAVE_PHYSICAL_FOLIO_OUT", "PAIR")]["context_gain_nats"]) < 0)

    predictions = read_tsv(PREDICTIONS)
    check("prediction_rows", len(predictions) == 4137 and {row["occurrence_id"] for row in predictions} == set(source_map))
    check("prediction_ranges", all(0 < float(row[field]) < 1 for row in predictions for field in ("page_p", "page_s", "page_c", "page_sc", "cross_p", "cross_c")))
    check("cross_context_coverage", sum(int(row["cross_context_covered"]) for row in predictions) == 2701)

    capacity = read_tsv(CAPACITY)
    check("capacity_rows", len(capacity) == 9)
    full_capacity = next(row for row in capacity if row["population"] == "FULL_4137" and row["scheme"] == "CROSSED5X5")
    check("neighbour_capacity", tuple(int(full_capacity[field]) for field in ("left_real", "right_real", "both_real", "unique_left", "unique_right")) == (3827, 3351, 3067, 1352, 1143))
    check("raw_pair_capacity", (int(full_capacity["unique_raw_pairs"]), int(full_capacity["singleton_raw_pairs"])) == (2946, 2844))
    check("position_pair_capacity", (int(full_capacity["unique_position_pairs"]), int(full_capacity["singleton_position_pairs"]), int(full_capacity["cross_stem_folio_bidirectional_pairs"])) == (2970, 2889, 6))

    coefficients = read_tsv(COEFFICIENTS)
    check("coefficients_nonempty", len(coefficients) > 25)
    check("coefficients_opaque", all(row["semantic_export_credit"] == "ZERO__OPAQUE_COMPLETE_CONTEXT" for row in coefficients))
    check("daiin_context_candidate_not_meaning", any(row["context_surface"] == "daiin" for row in coefficients))

    daiin = read_tsv(DAIIN)
    check("daiin_rows", len(daiin) == 12)
    dmap = {(row["population"], row["position4"]): row for row in daiin}
    check("direct_daiin_pattern", (dmap[("DIRECT_388", "EARLIER")]["daiin_l"], dmap[("DIRECT_388", "EARLIER")]["daiin_m"], dmap[("DIRECT_388", "FINAL")]["daiin_l"], dmap[("DIRECT_388", "FINAL")]["daiin_m"]) == ("7", "0", "0", "5"))
    check("rest_daiin_pattern", (dmap[("CACHE_REST_3749", "EARLIER")]["daiin_l"], dmap[("CACHE_REST_3749", "EARLIER")]["daiin_m"], dmap[("CACHE_REST_3749", "PENULTIMATE")]["daiin_l"], dmap[("CACHE_REST_3749", "FINAL")]["daiin_l"], dmap[("CACHE_REST_3749", "FINAL")]["daiin_m"]) == ("54", "5", "12", "10", "11"))
    check("daiin_rest_not_selected", close(float(dmap[("CACHE_REST_3749", "FINAL")]["mh_odds_ratio"]), 0.89307358313) and dmap[("CACHE_REST_3749", "FINAL")]["decision"] == "NO_INCREMENTAL_DAIIN_BRIDGE")

    sensitivity = read_tsv(SENSITIVITY)
    check("two_sensitivities", len(sensitivity) == 2)
    check("masked_context_positive", all(float(row["masked_context_gain"]) > 0 and row["decision"] == "RETAINS" for row in sensitivity))
    nulls = read_tsv(NULLS)
    check("two_nulls", len(nulls) == 2)
    check("null_repetitions_match", all(int(row["permutations"]) == int(result["null_repetitions"]) for row in nulls))
    for row in nulls:
        if int(row["permutations"]):
            expected_p = (int(row["exceed_or_equal"]) + 1) / (int(row["permutations"]) + 1)
            check(f"null_p:{row['null_id']}", close(float(row["add_one_p"]), expected_p))

    candidates = {row["candidate_id"]: row for row in read_tsv(CANDIDATES)}
    check("candidate_count", set(candidates) == {f"C{i}" for i in range(1, 7)})
    check("candidate_decisions", candidates["C2"]["decision"] == "SELECTED" and candidates["C3"]["decision"] == "WEAK_MODEL_DEPENDENT_LEAD" and candidates["C5"]["decision"] == "RETIRED" and candidates["C6"]["decision"] == "REJECTED")
    card = read_tsv(CARD)
    check("one_card", len(card) == 1)
    check("card_ceiling", card[0]["equivalence_license"] == card[0]["component_export"] == card[0]["semantic_export"] == card[0]["plaintext_value"] == "NONE")
    check("card_context_unresolved", card[0]["structural_tag"].endswith("SPARSE_COMPLETE_CONTEXT_LEAD_UNRESOLVED"))

    check("result_decision", result["decision"] == "PHYSICAL_POSITION_PLUS_LEARNED_STEM__SPARSE_CONTEXT_LEAD_UNRESOLVED")
    check("result_booleans", result["stem_selected"] is True and result["sparse_context_lead"] is True and result["raw_context_robust"] is False and result["context_selected"] is False and result["daiin_selected"] is False)
    check("zero_semantics", result["semantic_exports"] == result["confirmed_lexemes"] == result["confirmed_plaintext_clauses"] == result["equivalence_licenses"] == 0)
    check("sealed_result", result["f84_or_f84r_accessed"] is False and result["new_pages_opened"] == result["new_images_opened"] == 0)
    report = REPORT.read_text(encoding="utf-8")
    check("report_architecture", "PHYSICAL LINE EDGE + LEARNED PAIRED-FAMILY PROPENSITY" in report)
    check("report_daiin_retires", "special `daiin -> m` bridge\nis retired" in report)
    check("report_no_translation", "no word meaning and no translation" in report)

    output_paths = [ROOT / path for path in result["outputs"]] + [RESULT]
    baseline_hashes = {path: sha(path) for path in output_paths}
    replay_count = 0
    if not args.skip_replay:
        for replay in range(2):
            completed = subprocess.run(
                ["python3", str(SRC / "run.py")], cwd=ROOT, check=True,
                stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
            )
            check(f"replay_exit:{replay + 1}", completed.returncode == 0)
            for path, digest in baseline_hashes.items():
                check(f"replay_hash:{replay + 1}:{path.name}", sha(path) == digest)
            replay_count += 1

    validation = {
        "schema": "GDT802_VALIDATION_V1", "experiment": "GDT802", "status": "PASS",
        "checks": len(checks), "replays": replay_count, "null_repetitions": result["null_repetitions"],
        "exact_joins_rechecked": len(atlas), "sealed_f84_or_f84r_seen": False,
        "validated_result_hash": sha(RESULT), "validated_output_hashes": {path.relative_to(ROOT).as_posix(): sha(path) for path in output_paths if path != RESULT},
    }
    validation["content_hash"] = hashlib.sha256(json.dumps(validation, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    VALIDATION.write_text(json.dumps(validation, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"PASS: {len(checks)} checks; {replay_count} byte-identical replays")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
