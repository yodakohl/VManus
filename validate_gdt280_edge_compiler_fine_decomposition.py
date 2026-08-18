#!/usr/bin/env python3
"""Independent accounting and primary-score validation for GDT280."""
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
SCORE = R / "gdt280_edge_scores.tsv"
SHAPE = R / "gdt280_edge_shapley.tsv"
PROFILE = R / "gdt280_edge_profiles.tsv"
NULL = R / "gdt280_null_results.tsv"
FOLD = R / "gdt280_folio_scores.tsv"
RESULT = R / "gdt280_result.json"
OUT = R / "gdt280_validation.json"
BLOCKS = ("OUTER_WRAPPER", "LOCAL_FRAME", "RIGHT_FAMILY", "DISPLAY_RENDERER")
FIELD_ORDER = (
    ("register", 0, str), ("record_ordinal", 0, int), ("field_ordinal", 0, int),
    ("within_field_position", 0, str), ("wrapper", 1, str), ("q_flag", 1, int),
    ("local_frame", 2, str), ("inner_d", 2, str), ("right_family", 4, str),
    ("dy_closure", 0, str), ("b3", 0, str), ("line_close", 0, int),
    ("paragraph_close", 0, int), ("known_label_renderer", 8, str),
)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def csha(value: dict) -> str:
    q = dict(value)
    q.pop("content_sha256", None)
    return hashlib.sha256(json.dumps(q, sort_keys=True, ensure_ascii=True, separators=(",", ":")).encode()).hexdigest()


def rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def close(a, b, tolerance=5e-8) -> bool:
    return math.isclose(float(a), float(b), rel_tol=0, abs_tol=tolerance)


def key(row: dict, mask: int) -> tuple:
    return tuple(converter(row[name]) for name, bit, converter in FIELD_ORDER if bit == 0 or mask & bit)


def bucket(value: tuple) -> int:
    raw = json.dumps(["COMPILER", value], sort_keys=True, separators=(",", ":")).encode()
    return int(hashlib.sha256(raw).hexdigest()[:16], 16) % 256


def chars(host: str):
    seq = list(host) + ["<EOS>"]
    history = "^^"
    for char in seq:
        yield history[-2:], char
        history += "$" if char == "<EOS>" else char


def direct_score(events: list[dict], mapping: dict[str, int]) -> float:
    design = json.loads((R / "gdt276_design.json").read_text())
    K = len(design["alphabet"])
    prior = design["capacity"]["character_context_prior_mass"]
    by_fold = defaultdict(list)
    for row in events:
        by_fold[row["physical_folio"]].append(row)
    total = 0.0
    for held, test in sorted(by_fold.items()):
        global_counts = defaultdict(Counter)
        context_counts = defaultdict(Counter)
        for fold, rr in by_fold.items():
            if fold == held:
                continue
            for row in rr:
                b = mapping[row["observation_id"]]
                for history, char in chars(row["page_host"]):
                    global_counts[history][char] += 1
                    context_counts[(b, history)][char] += 1
        page_counts = defaultdict(lambda: defaultdict(Counter))
        for row in test:
            b = mapping[row["observation_id"]]
            for history, char in chars(row["page_host"]):
                q = global_counts[history]
                base = (q[char] + 0.5) / (sum(q.values()) + 0.5 * K)
                page = page_counts[row["page"]][history]
                pp = (page[char] + prior * base) / (sum(page.values()) + prior)
                context = context_counts[(b, history)]
                probability = (context[char] + prior * pp) / (sum(context.values()) + prior)
                total -= math.log2(probability)
                page[char] += 1
    return total


def permute(events: list[dict], mapping: dict[str, int], world: int) -> dict[str, int]:
    strata = defaultdict(list)
    for row in events:
        strata[(row["register"], int(row["record_ordinal"]), row["within_field_position"], int(row["host_length"]))].append(row["observation_id"])
    rng = random.Random(int(hashlib.sha256(f"GDT276_MATCHED_CONTEXT_V1|{world}|ABBREVIATION_HEAVY_LANGUAGE".encode()).hexdigest()[:16], 16))
    answer = dict(mapping)
    for ids in strata.values():
        values = [mapping[x] for x in ids]
        rng.shuffle(values)
        for observation_id, value in zip(ids, values):
            answer[observation_id] = value
    return answer


def shapley(values: dict[int, float]) -> dict[str, float]:
    answer = {}
    for i, block in enumerate(BLOCKS):
        bit = 1 << i
        value = 0.0
        for mask in range(16):
            if mask & bit:
                continue
            size = mask.bit_count()
            weight = math.factorial(size) * math.factorial(3 - size) / math.factorial(4)
            value += weight * (values[mask | bit] - values[mask])
        answer[block] = value
    return answer


def main() -> None:
    checks = []

    def check(name, condition):
        checks.append({"check": name, "pass": bool(condition)})
        assert condition, name

    design = json.loads((R / "gdt280_design.json").read_text())
    result = json.loads(RESULT.read_text())
    score = rows(SCORE); shape = rows(SHAPE); profiles = rows(PROFILE); null = rows(NULL); folds = rows(FOLD)
    check("design", design["status"] == "FROZEN_BEFORE_GDT280_EDGE_SCORING" and design["content_sha256"] == csha(design))
    frozen = rows(R / "gdt280_gdt279_freeze_manifest.tsv")
    check("parent_frozen", len(frozen) == 16 and all(sha(R / x["artifact"]) == x["frozen_sha256"] for x in frozen))
    check("status", result["status"] == "VOYNICH_EDGE_PROFILE_DIFFERS_FROM_LATIN_RIGHT_FAMILY_LEAD")
    check("counts", len(score) == 38 * 2 * 16 and len(shape) == 38 * 2 * 4 and len(profiles) == 38 * 2)
    groups = sorted({(x["control_id"], x["view"], x["representation"]) for x in score})
    check("groups", len(groups) == 76 and all({int(x["subset_mask"]) for x in score if (x["control_id"], x["view"], x["representation"]) == group} == set(range(16)) for group in groups))
    by_null = defaultdict(list)
    for row in null:
        by_null[(row["control_id"], row["view"], row["representation"], int(row["subset_mask"]))].append(float(row["held_bits"]))
    published = {(x["control_id"], x["view"], "PUBLISHED_FROZEN_GDT279", mask) for x in score if x["representation"] == "PUBLISHED_FROZEN_GDT279" for mask in range(16)}
    safe_full = {(x["control_id"], x["view"], "LOFO_SAFE", 15) for x in score if x["representation"] == "LOFO_SAFE"}
    check("null_keys", set(by_null) == published | safe_full)
    check("null_counts", all(len(v) == 64 for v in by_null.values()))
    for row in score:
        k = (row["control_id"], row["view"], row["representation"], int(row["subset_mask"]))
        if k not in by_null:
            check("safe_blank:" + ":".join(map(str, k)), row["null_worlds"] == "0" and row["saving_bits"] == "NA")
            continue
        v = by_null[k]; mean = statistics.mean(v); sd = statistics.pstdev(v); saving = mean - float(row["observed_bits"])
        check("score:" + ":".join(map(str, k)), close(row["null_mean_bits"], mean) and close(row["null_sd_bits"], sd) and close(row["saving_bits"], saving) and close(row["saving_bits_per_event"], saving / int(row["events"])) and (row["null_z"] == "NA" if sd == 0 else close(row["null_z"], saving / sd)))
    for group in groups:
        rr = {int(x["subset_mask"]): x for x in score if (x["control_id"], x["view"], x["representation"]) == group}
        if group[2] == "PUBLISHED_FROZEN_GDT279":
            values = {mask: float(x["saving_bits_per_event"]) for mask, x in rr.items()}
            target = "NULL_ADJUSTED_INCREMENT_OVER_BASE_BITS_PER_EVENT"
        else:
            base = float(rr[0]["observed_bits"])
            values = {mask: (base - float(x["observed_bits"])) / int(x["events"]) for mask, x in rr.items()}
            target = "OBSERVED_BASE_MINUS_SUBSET_BITS_PER_EVENT"
            check("safe_fields:" + ":".join(group), all(close(x["observed_base_minus_model_bits_per_event"], values[mask]) for mask, x in rr.items()))
        expected = shapley(values)
        actual = {x["block"]: float(x["shapley_bits_per_event"]) for x in shape if (x["control_id"], x["view"], x["representation"]) == group and x["allocation_target"] == target}
        check("shapley:" + ":".join(group), set(actual) == set(BLOCKS) and all(close(actual[b], expected[b], 3e-9) for b in BLOCKS) and close(sum(actual.values()), values[15] - values[0], 3e-9))
        profile = next(x for x in profiles if (x["control_id"], x["view"], x["representation"]) == group)
        lead = max(BLOCKS, key=lambda b: (actual[b], -BLOCKS.index(b)))
        check("profile:" + ":".join(group), profile["leading_block"] == lead and close(profile["edge_increment_bits_per_event"], values[15] - values[0]) and all(close(profile["shapley_" + b.lower()], actual[b]) for b in BLOCKS))

    parent_score = {(x["control_id"], x["view"], x["representation"]): x for x in rows(R / "gdt279_view_scores.tsv") if x["subset_mask"] == "7"}
    parent_null = defaultdict(list)
    for row in rows(R / "gdt279_null_results.tsv"):
        if row["subset_mask"] == "7":
            parent_null[(row["control_id"], row["view"], row["representation"])].append(float(row["held_bits"]))
    for group in groups:
        parent_rep = "PUBLISHED_FROZEN_GDT278" if group[2] == "PUBLISHED_FROZEN_GDT279" else "LOFO_SAFE"
        old = parent_score[(group[0], group[1], parent_rep)]
        full = next(x for x in score if (x["control_id"], x["view"], x["representation"]) == group and x["subset_mask"] == "15")
        check("parent_full:" + ":".join(group), close(full["observed_bits"], old["observed_bits"]))
        if group[2] == "PUBLISHED_FROZEN_GDT279":
            values = by_null[(group[0], group[1], group[2], 15)]
            expected = parent_null[(group[0], group[1], parent_rep)]
            check("parent_null:" + ":".join(group), all(close(a, b) for a, b in zip(values, expected)))

    fold_sum = defaultdict(float)
    for row in folds:
        fold_sum[(row["control_id"], row["view"], row["representation"], row["subset"])] += float(row["held_bits"])
    for row in score:
        if row["subset_mask"] in ("0", "15"):
            label = "BASE_NO_EDGE" if row["subset_mask"] == "0" else "FULL_EDGE"
            check("fold_sum:" + row["control_id"] + ":" + row["view"] + ":" + row["representation"] + ":" + label, close(row["observed_bits"], fold_sum[(row["control_id"], row["view"], row["representation"], label)]))

    primary_controls = ("LATIN_SCHOLASTIC_GRAPHEMATIC", "LATIN_MEDICAL_GRAPHEMATIC", "LATIN_15C_GRAPHEMATIC", "VOYNICH_REFERENCE")
    primary_profiles = {x["control_id"]: x for x in profiles if x["view"] == "NATIVE_ORDER" and x["representation"] == "PUBLISHED_FROZEN_GDT279" and x["control_id"] in primary_controls}
    safe_profiles = {x["control_id"]: x for x in profiles if x["view"] == "NATIVE_ORDER" and x["representation"] == "LOFO_SAFE" and x["control_id"] in primary_controls}
    check("primary_set", set(primary_profiles) == set(primary_controls) == set(safe_profiles))
    check("latin_right", all(primary_profiles[c]["leading_block"] == safe_profiles[c]["leading_block"] == "RIGHT_FAMILY" for c in primary_controls[:3]))
    check("voynich_wrapper", primary_profiles["VOYNICH_REFERENCE"]["leading_block"] == safe_profiles["VOYNICH_REFERENCE"]["leading_block"] == "OUTER_WRAPPER")
    check("safe_magnitude_sensitivity", close(safe_profiles["VOYNICH_REFERENCE"]["edge_increment_bits_per_event"], 0.031852521193) and float(safe_profiles["VOYNICH_REFERENCE"]["edge_increment_bits_per_event"]) < 0.15 * float(primary_profiles["VOYNICH_REFERENCE"]["edge_increment_bits_per_event"]))
    check("latin_renderer_constant", all({x["known_label_renderer"] for x in rows(R / "gdt278_native_event_inventory.tsv") if x["control_id"] == control} == {"NONE"} for control in primary_controls[:3]))
    check("no_f84_native", not any(x["page"].startswith("f84") or x["locus"].startswith("f84") for x in rows(R / "gdt278_native_event_inventory.tsv")))

    # Independently rebuild and score BASE/FULL plus null world zero on primary native panels.
    native = rows(R / "gdt278_native_event_inventory.tsv")
    artifact = {(x["control_id"], int(x["subset_mask"])): x for x in score if x["view"] == "NATIVE_ORDER" and x["representation"] == "PUBLISHED_FROZEN_GDT279" and x["control_id"] in primary_controls and int(x["subset_mask"]) in (0, 15)}
    null_artifact = defaultdict(list)
    for x in null:
        if x["view"] == "NATIVE_ORDER" and x["representation"] == "PUBLISHED_FROZEN_GDT279" and x["control_id"] in primary_controls and int(x["subset_mask"]) in (0, 15):
            null_artifact[(x["control_id"], int(x["subset_mask"]))].append(float(x["held_bits"]))
    for control in primary_controls:
        events = [x for x in native if x["control_id"] == control]
        check("primary_events:" + control, bool(events))
        for mask in (0, 15):
            mapping = {x["observation_id"]: bucket(key(x, mask)) for x in events}
            if mask == 15:
                check("full_bucket:" + control, all(mapping[x["observation_id"]] == int(x["compiler_bucket"]) for x in events))
            observed = direct_score(events, mapping)
            check(f"independent_score:{control}:{mask}", close(observed, artifact[(control, mask)]["observed_bits"]))
            world0 = direct_score(events, permute(events, mapping, 0))
            check(f"independent_null0:{control}:{mask}", close(world0, null_artifact[(control, mask)][0]))

    check("result_leaders", result["native_profile_leaders"] == {c: primary_profiles[c]["leading_block"] for c in primary_controls})
    check("safe_result_values", all(close(result["native_safe_edge_increment_bits_per_event"][c], safe_profiles[c]["edge_increment_bits_per_event"]) and close(result["native_safe_to_published_edge_increment_ratio"][c], float(safe_profiles[c]["edge_increment_bits_per_event"]) / float(primary_profiles[c]["edge_increment_bits_per_event"])) for c in primary_controls))
    check("no_semantics", result["semantic_assignments"] == result["hpr1_semantics_used"] == result["voynich_substrings_mined"] == 0)
    check("f84", result["f84"]["input_files"] == 0 and not any(v for name, v in result["f84"].items() if name != "input_files"))
    check("inputs", all(sha(R / name) == digest for name, digest in result["inputs"].items()))
    check("documents", all(sha(R / name) == digest for name, digest in result["documents"].items()))
    check("implementation", all(sha(R / name) == digest for name, digest in result["implementation"].items()))
    check("outputs", all(sha(R / name) == digest for name, digest in result["outputs"].items()))
    check("content", result["content_sha256"] == csha(result))
    validation = {"schema": "GDT280_EDGE_COMPILER_FINE_DECOMPOSITION_VALIDATION_V1", "status": "PASS", "checks_passed": len(checks), "checks_total": len(checks), "checks": checks, "result_sha256": sha(RESULT), "validator_sha256": sha(Path(__file__))}
    validation["content_sha256"] = csha(validation)
    OUT.write_text(json.dumps(validation, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"status": "PASS", "checks": len(checks)}, sort_keys=True))


if __name__ == "__main__":
    main()
