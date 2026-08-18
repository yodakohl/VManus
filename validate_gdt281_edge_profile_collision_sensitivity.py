#!/usr/bin/env python3
"""Independent accounting and primary-score validation for GDT281."""
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
SCORE = R / "gdt281_exact_scores.tsv"
SHAPE = R / "gdt281_exact_shapley.tsv"
PROFILE = R / "gdt281_exact_profiles.tsv"
NULL = R / "gdt281_null_results.tsv"
FOLD = R / "gdt281_folio_scores.tsv"
RESULT = R / "gdt281_result.json"
OUT = R / "gdt281_validation.json"
BLOCKS = ("OUTER_WRAPPER", "LOCAL_FRAME", "RIGHT_FAMILY", "DISPLAY_RENDERER")
FIELDS = (
    ("register", 0, str), ("record_ordinal", 0, int), ("field_ordinal", 0, int),
    ("within_field_position", 0, str), ("wrapper", 1, str), ("q_flag", 1, int),
    ("local_frame", 2, str), ("inner_d", 2, str), ("right_family", 4, str),
    ("dy_closure", 0, str), ("b3", 0, str), ("line_close", 0, int),
    ("paragraph_close", 0, int), ("known_label_renderer", 8, str),
)
PRIMARY = ("LATIN_SCHOLASTIC_GRAPHEMATIC", "LATIN_MEDICAL_GRAPHEMATIC", "LATIN_15C_GRAPHEMATIC", "VOYNICH_REFERENCE")


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def csha(value: dict) -> str:
    q = dict(value); q.pop("content_sha256", None)
    return hashlib.sha256(json.dumps(q, sort_keys=True, ensure_ascii=True, separators=(",", ":")).encode()).hexdigest()


def rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def close(a, b, tolerance=7e-8) -> bool:
    return math.isclose(float(a), float(b), rel_tol=0, abs_tol=tolerance)


def key(row: dict, mask: int) -> tuple:
    return tuple(converter(row[name]) for name, bit, converter in FIELDS if bit == 0 or mask & bit)


def chars(host: str):
    history = "^^"
    for char in list(host) + ["<EOS>"]:
        yield history[-2:], char
        history += "$" if char == "<EOS>" else char


def direct_score(events: list[dict], mapping: dict[str, tuple]) -> float:
    design = json.loads((R / "gdt276_design.json").read_text())
    k = len(design["alphabet"]); prior = design["capacity"]["character_context_prior_mass"]
    by_fold = defaultdict(list)
    for row in events:
        by_fold[row["physical_folio"]].append(row)
    total = 0.0
    for held, test in sorted(by_fold.items()):
        global_counts = defaultdict(Counter); context_counts = defaultdict(Counter)
        for fold, rr in by_fold.items():
            if fold == held:
                continue
            for row in rr:
                context = mapping[row["observation_id"]]
                for history, char in chars(row["page_host"]):
                    global_counts[history][char] += 1; context_counts[(context, history)][char] += 1
        page_counts = defaultdict(lambda: defaultdict(Counter))
        for row in test:
            context = mapping[row["observation_id"]]
            for history, char in chars(row["page_host"]):
                q = global_counts[history]; base = (q[char] + .5) / (sum(q.values()) + .5 * k)
                p = page_counts[row["page"]][history]; page = (p[char] + prior * base) / (sum(p.values()) + prior)
                z = context_counts[(context, history)]; probability = (z[char] + prior * page) / (sum(z.values()) + prior)
                total -= math.log2(probability); p[char] += 1
    return total


def permute(events: list[dict], mapping: dict[str, tuple], world: int) -> dict[str, tuple]:
    strata = defaultdict(list)
    for row in events:
        strata[(row["register"], int(row["record_ordinal"]), row["within_field_position"], int(row["host_length"]))].append(row["observation_id"])
    rng = random.Random(int(hashlib.sha256(f"GDT276_MATCHED_CONTEXT_V1|{world}|ABBREVIATION_HEAVY_LANGUAGE".encode()).hexdigest()[:16], 16))
    answer = dict(mapping)
    for ids in strata.values():
        values = [mapping[x] for x in ids]; rng.shuffle(values)
        for observation_id, value in zip(ids, values):
            answer[observation_id] = value
    return answer


def shapley(values: dict[int, float]) -> dict[str, float]:
    out = {}
    for i, block in enumerate(BLOCKS):
        bit = 1 << i; total = 0.0
        for mask in range(16):
            if mask & bit:
                continue
            size = mask.bit_count(); weight = math.factorial(size) * math.factorial(3 - size) / math.factorial(4)
            total += weight * (values[mask | bit] - values[mask])
        out[block] = total
    return out


def main() -> None:
    checks = []
    def check(name, condition):
        checks.append({"check": name, "pass": bool(condition)}); assert condition, name

    design = json.loads((R / "gdt281_design.json").read_text()); result = json.loads(RESULT.read_text())
    score = rows(SCORE); shape = rows(SHAPE); profile = rows(PROFILE); null = rows(NULL); folds = rows(FOLD)
    check("design", design["status"] == "FROZEN_BEFORE_GDT281_EXACT_CONTEXT_SCORING" and design["content_sha256"] == csha(design))
    frozen = rows(R / "gdt281_gdt280_freeze_manifest.tsv")
    check("parent_frozen", len(frozen) == 15 and all(sha(R / x["artifact"]) == x["frozen_sha256"] for x in frozen))
    check("status", result["status"] == "HASH_COLLISION_SENSITIVITY_PRESERVES_LATIN_RIGHT_VOYNICH_WRAPPER_SPLIT")
    check("counts", len(score) == 10 * 2 * 16 and len(shape) == 10 * 2 * 4 and len(profile) == 10 * 2 and len(null) == 10 * 16 * 64)
    groups = sorted({(x["control_id"], x["view"], x["representation"]) for x in score})
    check("groups", len(groups) == 20 and all({int(x["subset_mask"]) for x in score if (x["control_id"], x["view"], x["representation"]) == group} == set(range(16)) for group in groups))
    by_null = defaultdict(list)
    for row in null:
        by_null[(row["control_id"], row["view"], row["representation"], int(row["subset_mask"]))].append(float(row["held_bits"]))
    check("null_groups", len(by_null) == 10 * 16 and all(key[2] == "PUBLISHED_EXACT_CONTEXT" and len(value) == 64 for key, value in by_null.items()))
    for row in score:
        k = (row["control_id"], row["view"], row["representation"], int(row["subset_mask"]))
        if k not in by_null:
            check("safe_no_null:" + ":".join(map(str, k)), row["null_worlds"] == "0" and row["saving_bits"] == "NA")
            continue
        values = by_null[k]; mean = statistics.mean(values); sd = statistics.pstdev(values); saving = mean - float(row["observed_bits"])
        check("score:" + ":".join(map(str, k)), close(row["null_mean_bits"], mean) and close(row["null_sd_bits"], sd) and close(row["saving_bits"], saving) and close(row["saving_bits_per_event"], saving / int(row["events"])) and (row["null_z"] == "NA" if sd == 0 else close(row["null_z"], saving / sd)))
    for group in groups:
        rr = {int(x["subset_mask"]): x for x in score if (x["control_id"], x["view"], x["representation"]) == group}
        if group[2] == "PUBLISHED_EXACT_CONTEXT":
            values = {mask: float(row["saving_bits_per_event"]) for mask, row in rr.items()}; target = "NULL_ADJUSTED_INCREMENT_OVER_BASE_BITS_PER_EVENT"
        else:
            base = float(rr[0]["observed_bits"]); values = {mask: (base - float(row["observed_bits"])) / int(row["events"]) for mask, row in rr.items()}; target = "OBSERVED_BASE_MINUS_SUBSET_BITS_PER_EVENT"
            check("safe_values:" + ":".join(group), all(close(rr[mask]["observed_base_minus_model_bits_per_event"], values[mask]) for mask in range(16)))
        expected = shapley(values)
        actual = {x["block"]: float(x["shapley_bits_per_event"]) for x in shape if (x["control_id"], x["view"], x["representation"]) == group and x["allocation_target"] == target}
        check("shapley:" + ":".join(group), set(actual) == set(BLOCKS) and all(close(actual[b], expected[b], 4e-9) for b in BLOCKS) and close(sum(actual.values()), values[15] - values[0], 4e-9))
        p = next(x for x in profile if (x["control_id"], x["view"], x["representation"]) == group)
        lead = max(BLOCKS, key=lambda b: (actual[b], -BLOCKS.index(b)))
        check("profile:" + ":".join(group), p["leading_block"] == lead and close(p["edge_increment_bits_per_event"], values[15] - values[0]) and all(close(p["shapley_" + b.lower()], actual[b]) for b in BLOCKS))
    fold_sum = defaultdict(float)
    for row in folds:
        fold_sum[(row["control_id"], row["view"], row["representation"], row["subset"])] += float(row["held_bits"])
    for row in score:
        if row["subset_mask"] in ("0", "15"):
            label = "BASE_NO_EDGE" if row["subset_mask"] == "0" else "FULL_EDGE"
            check("fold:" + row["control_id"] + ":" + row["view"] + ":" + row["representation"] + ":" + label, close(row["observed_bits"], fold_sum[(row["control_id"], row["view"], row["representation"], label)]))

    primary = {(x["control_id"], x["representation"]): x for x in profile if x["view"] == "NATIVE_ORDER" and x["control_id"] in PRIMARY}
    check("primary_set", len(primary) == 8)
    for rep in ("PUBLISHED_EXACT_CONTEXT", "LOFO_SAFE_EXACT_CONTEXT"):
        check("latin_right:" + rep, all(primary[(c, rep)]["leading_block"] == "RIGHT_FAMILY" and float(primary[(c, rep)]["leading_value_bits_per_event"]) > 0 for c in PRIMARY[:3]))
        check("vms_wrapper:" + rep, primary[(PRIMARY[3], rep)]["leading_block"] == "OUTER_WRAPPER" and float(primary[(PRIMARY[3], rep)]["leading_value_bits_per_event"]) > 0)
    check("latin_renderer_zero", all(abs(float(primary[(c, "PUBLISHED_EXACT_CONTEXT")]["shapley_display_renderer"])) <= 1e-10 for c in PRIMARY[:3]))

    native = rows(R / "gdt278_native_event_inventory.tsv")
    check("native_no_f84", not any(x["page"].startswith("f84") or x["locus"].startswith("f84") for x in native))
    artifact = {(x["control_id"], int(x["subset_mask"])): x for x in score if x["view"] == "NATIVE_ORDER" and x["representation"] == "PUBLISHED_EXACT_CONTEXT" and x["control_id"] in PRIMARY and int(x["subset_mask"]) in (0, 8, 15)}
    null0 = {(x["control_id"], int(x["subset_mask"])): x for x in null if x["view"] == "NATIVE_ORDER" and x["representation"] == "PUBLISHED_EXACT_CONTEXT" and x["control_id"] in PRIMARY and int(x["subset_mask"]) in (0, 15) and int(x["world_index"]) == 0}
    for control in PRIMARY:
        events = [x for x in native if x["control_id"] == control]
        check("primary_events:" + control, bool(events))
        for mask in (0, 8, 15):
            mapping = {x["observation_id"]: key(x, mask) for x in events}; observed = direct_score(events, mapping)
            check(f"direct:{control}:{mask}", close(observed, artifact[(control, mask)]["observed_bits"]))
            if mask in (0, 15):
                check(f"direct_null0:{control}:{mask}", close(direct_score(events, permute(events, mapping, 0)), null0[(control, mask)]["held_bits"]))
        if control != "VOYNICH_REFERENCE":
            check("renderer_constant:" + control, {x["known_label_renderer"] for x in events} == {"NONE"})
            check("renderer_context_bijection:" + control, len({key(x, 0) for x in events}) == len({key(x, 8) for x in events}))

    check("result_checks", result["frozen_checks"] == {"latin_published_right_family": True, "latin_lofo_safe_right_family": True, "voynich_published_outer_wrapper": True, "voynich_lofo_safe_outer_wrapper": True, "constant_latin_renderer_zero": True})
    check("no_semantics", result["semantic_assignments"] == result["hpr1_semantics_used"] == result["voynich_substrings_mined"] == 0)
    check("f84", result["f84"]["input_files"] == 0 and not any(v for name, v in result["f84"].items() if name != "input_files"))
    check("inputs", all(sha(R / name) == digest for name, digest in result["inputs"].items()))
    check("documents", all(sha(R / name) == digest for name, digest in result["documents"].items()))
    check("implementation", all(sha(R / name) == digest for name, digest in result["implementation"].items()))
    check("outputs", all(sha(R / name) == digest for name, digest in result["outputs"].items()))
    check("content", result["content_sha256"] == csha(result))
    validation = {"schema": "GDT281_EDGE_PROFILE_COLLISION_SENSITIVITY_VALIDATION_V1", "status": "PASS", "validation_scope": "INDEPENDENT_PUBLISHED_PRIMARY_RESCORE_AND_RETAINED_SAFE_ACCOUNTING", "checks_passed": len(checks), "checks_total": len(checks), "checks": checks, "result_sha256": sha(RESULT), "validator_sha256": sha(Path(__file__))}
    validation["content_sha256"] = csha(validation)
    OUT.write_text(json.dumps(validation, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"status": "PASS", "checks": len(checks)}, sort_keys=True))


if __name__ == "__main__":
    main()
