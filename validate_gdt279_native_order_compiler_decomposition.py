#!/usr/bin/env python3
"""Independent artifact/accounting validation for GDT279."""
from __future__ import annotations

import csv
import hashlib
import json
import math
import random
import statistics
from collections import Counter, defaultdict
from pathlib import Path

R = Path(__file__).resolve().parent
SCORES = R / "gdt279_view_scores.tsv"
SHAPLEY = R / "gdt279_block_shapley.tsv"
CONTRASTS = R / "gdt279_view_contrasts.tsv"
FOLDS = R / "gdt279_folio_scores.tsv"
NULLS = R / "gdt279_null_results.tsv"
INTERMEDIATE = R / "gdt279_intermediate_event_inventory.tsv"
RESULT = R / "gdt279_result.json"
OUT = R / "gdt279_validation.json"
BLOCKS = ("OPPORTUNITY", "EDGE_COMPILER", "CLOSURE_BOUNDARY")
FIELDS = (
    ("register", 1, str), ("record_ordinal", 1, int), ("field_ordinal", 1, int),
    ("within_field_position", 1, str), ("wrapper", 2, str), ("q_flag", 2, int),
    ("local_frame", 2, str), ("inner_d", 2, str), ("right_family", 2, str),
    ("dy_closure", 4, str), ("b3", 4, str), ("line_close", 4, int),
    ("paragraph_close", 4, int), ("known_label_renderer", 2, str),
)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def csha(value: dict) -> str:
    q = dict(value)
    q.pop("content_sha256", None)
    return hashlib.sha256(
        json.dumps(q, sort_keys=True, ensure_ascii=True, separators=(",", ":")).encode()
    ).hexdigest()


def rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def close(a, b, tolerance=4e-8) -> bool:
    return math.isclose(float(a), float(b), rel_tol=0, abs_tol=tolerance)


def bucket(key: tuple, n: int = 256) -> int:
    raw = json.dumps(["COMPILER", key], sort_keys=True, separators=(",", ":")).encode()
    return int(hashlib.sha256(raw).hexdigest()[:16], 16) % n


def subset_key(row: dict, mask: int) -> tuple:
    if mask == 0:
        return ()
    return tuple(converter(row[name]) for name, bit, converter in FIELDS if mask & bit)


def chars(host: str):
    sequence = list(host) + ["<EOS>"]
    history = "^^"
    answer = []
    for char in sequence:
        answer.append((history[-2:], char))
        history += "$" if char == "<EOS>" else char
    return answer


def direct_score(events: list[dict], buckets: dict[str, int]) -> float:
    design = json.loads((R / "gdt276_design.json").read_text())
    K = len(design["alphabet"])
    prior = design["capacity"]["character_context_prior_mass"]
    by_fold: dict[str, list[dict]] = defaultdict(list)
    for row in events:
        by_fold[row["physical_folio"]].append(row)
    total = 0.0
    for held, test in sorted(by_fold.items()):
        training = [row for fold, rr in by_fold.items() if fold != held for row in rr]
        global_counts: dict[str, Counter] = defaultdict(Counter)
        context_counts: dict[tuple[int, str], Counter] = defaultdict(Counter)
        for row in training:
            b = buckets[row["observation_id"]]
            for history, char in chars(row["page_host"]):
                global_counts[history][char] += 1
                context_counts[(b, history)][char] += 1
        page_counts: dict[str, dict[str, Counter]] = defaultdict(lambda: defaultdict(Counter))
        for row in test:
            b = buckets[row["observation_id"]]
            for history, char in chars(row["page_host"]):
                base = (global_counts[history][char] + 0.5) / (sum(global_counts[history].values()) + 0.5 * K)
                page = page_counts[row["page"]][history]
                page_probability = (page[char] + prior * base) / (sum(page.values()) + prior)
                context = context_counts[(b, history)]
                probability = (context[char] + prior * page_probability) / (sum(context.values()) + prior)
                total -= math.log2(probability)
                page[char] += 1
    return total


def permuted(events: list[dict], original: dict[str, int], world: int) -> dict[str, int]:
    strata: dict[tuple, list[str]] = defaultdict(list)
    for row in events:
        strata[(row["register"], int(row["record_ordinal"]), row["within_field_position"], int(row["host_length"]))].append(row["observation_id"])
    rng = random.Random(int(hashlib.sha256(f"GDT276_MATCHED_CONTEXT_V1|{world}|ABBREVIATION_HEAVY_LANGUAGE".encode()).hexdigest()[:16], 16))
    answer = dict(original)
    for ids in strata.values():
        values = [original[i] for i in ids]
        rng.shuffle(values)
        for observation_id, value in zip(ids, values):
            answer[observation_id] = value
    return answer


def shapley(values: dict[int, float]) -> dict[str, float]:
    answer = {}
    for i, block in enumerate(BLOCKS):
        bit = 1 << i
        value = 0.0
        for mask in range(8):
            if mask & bit:
                continue
            size = mask.bit_count()
            weight = math.factorial(size) * math.factorial(2 - size) / math.factorial(3)
            value += weight * (values[mask | bit] - values[mask])
        answer[block] = value
    return answer


def main() -> None:
    checks: list[dict] = []

    def check(name: str, condition: bool) -> None:
        checks.append({"check": name, "pass": bool(condition)})
        assert condition, name

    design = json.loads((R / "gdt279_design.json").read_text())
    result = json.loads(RESULT.read_text())
    score = rows(SCORES)
    shape = rows(SHAPLEY)
    contrast = rows(CONTRASTS)
    folds = rows(FOLDS)
    null = rows(NULLS)
    intermediate = rows(INTERMEDIATE)
    check("design_frozen", design["status"] == "FROZEN_BEFORE_GDT279_BLOCK_SCORING")
    check("design_hash", design["content_sha256"] == csha(design))
    frozen = rows(R / "gdt279_gdt278_freeze_manifest.tsv")
    check("gdt278_frozen", len(frozen) == 20 and all(sha(R / row["artifact"]) == row["frozen_sha256"] for row in frozen))
    check("result_status", result["status"] == "NATIVE_EXCESS_SHARED_OPPORTUNITY_INTERACTION_LEAD")
    check("panel_counts", result["panels"] == 38 and result["intermediate_panels"] == 11)
    check("score_count", len(score) == 38 * 2 * 8)
    check("score_views", Counter((x["representation"], x["view"]) for x in score) == {
        ("PUBLISHED_FROZEN_GDT278", "NATIVE_ORDER"): 128,
        ("PUBLISHED_FROZEN_GDT278", "LENGTH_MATCHED_OVERLAY"): 88,
        ("PUBLISHED_FROZEN_GDT278", "MATCHED_SAMPLE_NATIVE_LAYOUT"): 88,
        ("LOFO_SAFE", "NATIVE_ORDER"): 128,
        ("LOFO_SAFE", "LENGTH_MATCHED_OVERLAY"): 88,
        ("LOFO_SAFE", "MATCHED_SAMPLE_NATIVE_LAYOUT"): 88,
    })
    check("all_subsets", all({int(x["subset_mask"]) for x in score if x["control_id"] == control and x["view"] == view and x["representation"] == rep} == set(range(8)) for control, view, rep in {(x["control_id"], x["view"], x["representation"]) for x in score}))

    by_null: dict[tuple[str, str, str, int], list[float]] = defaultdict(list)
    for row in null:
        by_null[(row["control_id"], row["view"], row["representation"], int(row["subset_mask"]))].append(float(row["held_bits"]))
    published_keys = {(x["control_id"], x["view"], "PUBLISHED_FROZEN_GDT278", mask) for x in score if x["representation"] == "PUBLISHED_FROZEN_GDT278" for mask in range(8)}
    safe_full_keys = {(x["control_id"], x["view"], "LOFO_SAFE", 7) for x in score if x["representation"] == "LOFO_SAFE"}
    check("null_key_set", set(by_null) == published_keys | safe_full_keys)
    check("null_64", all(len(values) == 64 for values in by_null.values()))
    for row in score:
        key = (row["control_id"], row["view"], row["representation"], int(row["subset_mask"]))
        if key not in by_null:
            check("nonfull_safe_null_blank:" + ":".join(map(str, key)), row["null_worlds"] == "0" and row["saving_bits"] == "NA")
            continue
        values = by_null[key]
        mean = statistics.mean(values)
        sd = statistics.pstdev(values)
        saving = mean - float(row["observed_bits"])
        check("score_arithmetic:" + ":".join(map(str, key)), close(row["null_mean_bits"], mean) and close(row["null_sd_bits"], sd) and close(row["saving_bits"], saving) and close(row["saving_bits_per_event"], saving / int(row["events"])) and (row["null_z"] == "NA" if sd == 0 else close(row["null_z"], saving / sd)))

    groups = sorted({(x["control_id"], x["view"], x["representation"]) for x in score})
    for group in groups:
        rr = {int(x["subset_mask"]): x for x in score if (x["control_id"], x["view"], x["representation"]) == group}
        if group[2] == "PUBLISHED_FROZEN_GDT278":
            values = {mask: float(row["saving_bits_per_event"]) for mask, row in rr.items()}
            target = "NULL_ADJUSTED_SAVING_BITS_PER_EVENT"
        else:
            empty = float(rr[0]["observed_bits"])
            values = {mask: (empty - float(row["observed_bits"])) / int(row["events"]) for mask, row in rr.items()}
            target = "OBSERVED_EMPTY_MINUS_SUBSET_BITS_PER_EVENT"
            check("safe_improvement_fields:" + ":".join(group), all(close(row["observed_empty_minus_model_bits_per_event"], values[mask]) for mask, row in rr.items()))
        expected = shapley(values)
        actual = {x["block"]: float(x["shapley_bits_per_event"]) for x in shape if (x["control_id"], x["view"], x["representation"]) == group and x["allocation_target"] == target}
        check("shapley:" + ":".join(group), set(actual) == set(BLOCKS) and all(close(actual[block], expected[block], 2e-9) for block in BLOCKS) and close(sum(actual.values()), values[7] - values[0], 2e-9))

    parent_scores = {(x["control_id"], x["view"]): x for x in rows(R / "gdt278_magnitude_scores.tsv") if x["representation"] == "PUBLISHED_FULL_INVENTORY"}
    parent_null: dict[tuple[str, str], list[float]] = defaultdict(list)
    for row in rows(R / "gdt278_null_results.tsv"):
        if row["representation"] == "PUBLISHED_FULL_INVENTORY":
            parent_null[(row["control_id"], row["view"])].append(float(row["held_bits"]))
    for key, old in parent_scores.items():
        current = next(x for x in score if (x["control_id"], x["view"]) == key and x["representation"] == "PUBLISHED_FROZEN_GDT278" and x["subset_mask"] == "7")
        check("parent_full:" + ":".join(key), close(current["observed_bits"], old["observed_bits"]) and close(current["saving_bits"], old["saving_bits"]))
        current_null = by_null[(key[0], key[1], "PUBLISHED_FROZEN_GDT278", 7)]
        check("parent_null:" + ":".join(key), all(close(a, b) for a, b in zip(current_null, parent_null[key])))

    check("intermediate_count", len(intermediate) == 49_236 == result["intermediate_events"])
    by_intermediate: dict[str, list[dict]] = defaultdict(list)
    for row in intermediate:
        by_intermediate[row["control_id"]].append(row)
    check("intermediate_controls", len(by_intermediate) == 11 and all(len(rr) == 4476 for rr in by_intermediate.values()))
    check("intermediate_unique", all(len({x["source_observation_id"] for x in rr}) == 4476 for rr in by_intermediate.values()))
    check("no_f84", not any(x["page"].startswith("f84") or x["locus"].startswith("f84") for x in intermediate))
    parent_matched: dict[str, list[dict]] = defaultdict(list)
    for row in rows(R / "gdt278_matched_event_inventory.tsv"):
        control = "VOYNICH_REFERENCE" if row["control_id"] == "VOYNICH_MATCHED_REFERENCE" else row["control_id"]
        parent_matched[control].append(row)
    same_fields = ("page_host", "host_length", "wrapper", "q_flag", "local_frame", "inner_d", "right_family", "dy_closure", "b3", "known_label_renderer", "source_folio_hash", "source_line_hash", "source_surface_sha256")
    for control, rr in by_intermediate.items():
        a = {x["source_observation_id"]: x for x in rr}
        b = {x["source_observation_id"]: x for x in parent_matched[control]}
        check("same_source_set:" + control, set(a) == set(b))
        check("same_source_payload:" + control, all(all(a[key][field] == b[key][field] for field in same_fields) for key in a))
        check("full_bucket_rebuilt:" + control, all(bucket(subset_key(x, 7)) == int(x["compiler_bucket"]) for x in rr))

    # Independently rescore every intermediate FULL model and three fixed null worlds.
    published_full = {(x["control_id"], x["view"]): x for x in score if x["representation"] == "PUBLISHED_FROZEN_GDT278" and x["subset_mask"] == "7"}
    for control, rr in by_intermediate.items():
        bm = {x["observation_id"]: int(x["compiler_bucket"]) for x in rr}
        observed = direct_score(rr, bm)
        artifact = published_full[(control, "MATCHED_SAMPLE_NATIVE_LAYOUT")]
        check("independent_intermediate_score:" + control, close(observed, artifact["observed_bits"]))
        expected_null = by_null[(control, "MATCHED_SAMPLE_NATIVE_LAYOUT", "PUBLISHED_FROZEN_GDT278", 7)]
        for world in (0, 31, 63):
            value = direct_score(rr, permuted(rr, bm, world))
            check(f"independent_intermediate_null:{control}:{world}", close(value, expected_null[world]))

    check("contrast_count", len(contrast) == 22)
    by_contrast = {(x["control_id"], x["representation"]): x for x in contrast}
    for key, row in by_contrast.items():
        control, representation = key
        values = {}
        blocks = {}
        for view in ("LENGTH_MATCHED_OVERLAY", "MATCHED_SAMPLE_NATIVE_LAYOUT", "NATIVE_ORDER"):
            full = next(x for x in score if x["control_id"] == control and x["view"] == view and x["representation"] == representation and x["subset_mask"] == "7")
            values[view] = float(full["saving_bits_per_event"])
            blocks[view] = {x["block"]: float(x["shapley_bits_per_event"]) for x in shape if x["control_id"] == control and x["view"] == view and x["representation"] == representation}
        check("contrast_values:" + ":".join(key), close(row["layout_delta_bits_per_event"], values["MATCHED_SAMPLE_NATIVE_LAYOUT"] - values["LENGTH_MATCHED_OVERLAY"]) and close(row["selection_delta_bits_per_event"], values["NATIVE_ORDER"] - values["MATCHED_SAMPLE_NATIVE_LAYOUT"]))
        deltas = {block: blocks["MATCHED_SAMPLE_NATIVE_LAYOUT"][block] - blocks["LENGTH_MATCHED_OVERLAY"][block] for block in BLOCKS}
        lead = max(BLOCKS, key=lambda block: (deltas[block], -BLOCKS.index(block)))
        check("contrast_blocks:" + ":".join(key), row["layout_leading_block"] == lead and all(close(row["layout_delta_" + block.lower()], deltas[block]) for block in BLOCKS))

    positive = set(json.loads((R / "gdt278_result.json").read_text())["native_safe_reproductions"])
    eligible = [x for x in contrast if x["representation"] == "PUBLISHED_FROZEN_GDT278" and x["control_id"] in positive]
    check("headline_population", {x["control_id"] for x in eligible} == {"LATIN_MEDICAL_GRAPHEMATIC", "LATIN_15C_GRAPHEMATIC"})
    check("headline_logic", all(float(x["layout_delta_bits_per_event"]) > 0 and x["layout_leading_block"] == "OPPORTUNITY" for x in eligible))
    check("safe_layout_sign", all(float(by_contrast[(control, "LOFO_SAFE")]["layout_delta_bits_per_event"]) > 0 for control in ("LATIN_MEDICAL_GRAPHEMATIC", "LATIN_15C_GRAPHEMATIC")))
    fold_sum: dict[tuple[str, str, str], float] = defaultdict(float)
    for row in folds:
        fold_sum[(row["control_id"], row["view"], row["representation"])] += float(row["held_bits"])
    check("fold_sums", all(close(x["observed_bits"], fold_sum[(x["control_id"], x["view"], x["representation"])]) for x in score if x["subset_mask"] == "7"))
    check("no_semantics", result["semantic_assignments"] == result["hpr1_semantics_used"] == result["voynich_substrings_mined"] == 0)
    check("f84_false", result["f84"]["input_files"] == 0 and not any(v for key, v in result["f84"].items() if key != "input_files"))
    check("inputs", all(sha(R / name) == digest for name, digest in result["inputs"].items()))
    check("documents", all(sha(R / name) == digest for name, digest in result["documents"].items()))
    check("implementation", all(sha(R / name) == digest for name, digest in result["implementation"].items()))
    check("outputs", all(sha(R / name) == digest for name, digest in result["outputs"].items()))
    check("content_hash", result["content_sha256"] == csha(result))
    validation = {
        "schema": "GDT279_NATIVE_ORDER_COMPILER_DECOMPOSITION_VALIDATION_V1",
        "status": "PASS",
        "checks_passed": len(checks),
        "checks_total": len(checks),
        "checks": checks,
        "result_sha256": sha(RESULT),
        "validator_sha256": sha(Path(__file__)),
    }
    validation["content_sha256"] = csha(validation)
    OUT.write_text(json.dumps(validation, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"status": "PASS", "checks": len(checks)}, sort_keys=True))


if __name__ == "__main__":
    main()
