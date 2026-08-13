#!/usr/bin/env python3
"""Independent arithmetic/stability validation of the scaled group-code screen."""

import hashlib, json, math
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def c2(n): return n * (n - 1) / 2


def ari(a, b):
    cells = Counter(zip(a, b)); ca = Counter(a); cb = Counter(b); denominator = c2(len(a))
    observed = sum(c2(value) for value in cells.values()); aa = sum(c2(value) for value in ca.values()); bb = sum(c2(value) for value in cb.values())
    expected = aa * bb / denominator
    return (observed - expected) / (.5 * (aa + bb) - expected)


def main():
    checks = []
    def need(value, name):
        if not value: raise AssertionError(name)
        checks.append(name)
    scale = json.load(open(ROOT / "gdt001_group_code_scale_results.json")); stability = json.load(open(ROOT / "gdt001_group_code_scale_stability.json")); anonymous = json.load(open(ROOT / "gdt001_group_code_anonymous_null_results.json")); root = json.load(open(ROOT / "gdt001_root_character_code_results.json"))
    need(scale["status"] == "EXPLORATORY_NOT_CONFIRMED_TRANSLATION", "scale_status"); need([row["k"] for row in scale["rows"]] == [256, 512, 1024], "scale_sizes")
    for row in scale["rows"]:
        need(abs(row["total_bits"] - row["key_bits"] - row["payload_bits"] - row["fixed_bits"]) < 1e-6, f"scale_sum_{row['k']}")
        digest = hashlib.sha256((json.dumps(row["mapping"], sort_keys=True, separators=(",", ":")) + "\n").encode()).hexdigest()
        need(digest == row["decoder_hash"], f"scale_map_hash_{row['k']}"); need(row["cpu_exact"] is True, f"scale_cpu_{row['k']}")
    best_language = min(scale["rows"], key=lambda row: row["total_bits"]); best_null = min(row["matched_null_bits"] for row in scale["rows"])
    family_gain = best_null - best_language["total_bits"]; need(abs(family_gain - 5880.960600502905) < 1e-6, "selection_correct_family_gain")
    need(stability["decision"] == "STOP_SCALE_UNSTABLE", "stability_stop"); need(len(stability["rows"]) == 3, "three_restarts")
    maps = [[item["target"] for item in row["mapping"]] for row in stability["rows"]]; agreements = [ari(maps[i], maps[j]) for i in range(3) for j in range(i + 1, 3)]
    need(max(agreements) < .20, "restart_partition_ari_below_point2"); need(len({row["decoder_hash"] for row in stability["rows"]}) == 3, "restart_hashes_distinct")
    need(anonymous["decision"] == "CONTINUE_CZECH_BEATS_ANONYMOUS_NULL", "anonymous_control_result"); need(0 < anonymous["best"]["gap_vs_best_czech_bits"] < 1000, "czech_margin_small")
    need(root["result"]["total_bits"] > best_language["total_bits"], "root_code_loses_surface_code"); need(root["result"]["gap_vs_variable_context_bits"] > 0, "root_code_loses_global")
    output = {"schema": "GDT001_GROUP_CODE_SCALE_VALIDATION_V1", "status": "PASS_EXPLORATORY_SCALE_ARITHMETIC_AND_STABILITY_STOP", "checks": checks,
              "check_count": len(checks), "selection_correct_family_gain_bits": family_gain, "restart_pair_ari": agreements,
              "claim_ceiling": "Independent artifact arithmetic and partition diagnostic only; no established character, sound, language, plaintext, meaning, or translation."}
    (ROOT / "gdt001_group_code_scale_validation.json").write_text(json.dumps(output, sort_keys=True, separators=(",", ":")) + "\n")
    print(json.dumps({"status": output["status"], "checks": len(checks), "family_gain_bits": family_gain, "max_ari": max(agreements)}))


if __name__ == "__main__": main()
