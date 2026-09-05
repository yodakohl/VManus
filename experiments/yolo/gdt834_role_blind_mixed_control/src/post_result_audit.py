#!/usr/bin/env python3
"""Posthoc aggregate audit of already locked fits; no fitting or scoring.

This audit was requested after RESULT.json reported BASELINE_RECOVERY_FAIL.
It is outside the preregistration and cannot change its decision or selection.
Only existing objectives are read; no new key, oracle or objective is computed.
"""
from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]
FIT_LOCK_SHA256 = "9e91fa0af401d4777e9af6cec9955957d438fc9ee0909b2e1e4785e385eec872"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def edit_distance(left, right):
    previous = list(range(len(right) + 1))
    for i, a in enumerate(left, 1):
        current = [i]
        for j, b in enumerate(right, 1):
            current.append(min(previous[j] + 1, current[-1] + 1, previous[j - 1] + (a != b)))
        previous = current
    return previous[-1]


def audit(base):
    bindings = {}

    def read(relative, expected=None):
        path = base / relative
        digest = sha(path)
        if expected is not None and digest != expected:
            raise ValueError("Frozen input changed: " + relative)
        bindings[relative] = digest
        return json.loads(path.read_text())

    lock = read("artifacts/FIT_LOCK.json", FIT_LOCK_SHA256)
    if len(lock["restarts"]) != 48 or len(lock["selected"]) != 6:
        raise ValueError("Incomplete fixed fit inventory")
    fits = {name: read(name, digest) for name, digest in lock["sha256"].items()}
    result = read("artifacts/RESULT.json")
    if result["fit_lock_sha256"] != FIT_LOCK_SHA256:
        raise ValueError("Result belongs to a different fit lock")
    primary = {(row["world_id"], row["arm"]): row for row in result["condition_results"]}
    capacity = read("prepared/CAPACITY.json")
    source = read("sealed/source_truth.json", capacity["source_truth_sha256"])
    generation = read("prepared/GENERATION.json")
    if generation["capacity_sha256"] != bindings["prepared/CAPACITY.json"]:
        raise ValueError("Generation capacity binding changed")
    generation_worlds = {row["world_id"]: row for row in generation["worlds"]}
    truths = {}
    ciphers = {}
    for world, entry in generation_worlds.items():
        truth = read(f"sealed/world_{world}_truth.json", entry["sealed_truth_sha256"])
        if truth["paragraphs"] != source["paragraphs"]:
            raise ValueError("Different source content across worlds")
        truths[world] = truth
        for packet, digest in entry["ciphertext_sha256"].items():
            ciphers[world, packet] = read(f"prepared/world_{world}_{packet}.json", digest)

    def aligned(world, arm, split):
        packet = ("typed_" if arm == "TYPED" else "") + split
        rows = ciphers[world, packet]["paragraphs"]
        gold = [p for p in source["paragraphs"] if p["split"] == split]
        if [p["paragraph_id"] for p in rows] != [p["paragraph_id"] for p in gold]:
            raise ValueError("Paragraph alignment changed")
        for row, paragraph in zip(rows, gold):
            if len(row["words"]) != len(paragraph["words"]):
                raise ValueError("Word alignment changed")
            yield row["words"], paragraph["words"]

    def true_key(world, arm):
        truth = truths[world]
        if arm == "BLIND":
            return truth["decode_map"]
        return {code: {"role": code[0], "output": output} for code, output in truth["typed_decode_map"].items()}

    def signature(fit):
        world, arm = fit["world_id"], fit["arm"]
        gold_key = true_key(world, arm)
        supports = {}
        for split in ("discovery", "held"):
            supports[split] = Counter(code for rows, _ in aligned(world, arm, split) for word in rows for code in word)
        if not set(supports["held"]) <= set(supports["discovery"]):
            raise ValueError("Held-only carrier")
        active = set(supports["discovery"]) | set(supports["held"])
        return tuple(sorted((gold_key[c]["role"], gold_key[c]["output"], fit["key"][c]["role"], fit["key"][c]["output"]) for c in active))

    selected_signatures = {signature(fits[name]) for name in lock["selected"]}
    selected_rows = []
    restart_rows = []
    classifications = Counter({"exact_observed_truth": 0, "same_observed_map_as_selected": 0, "other": 0})
    for selected_path in lock["selected"]:
        fit = fits[selected_path]
        world, arm = fit["world_id"], fit["arm"]
        observed_signature = signature(fit)
        key = true_key(world, arm)
        key_errors = [{"true_role": a, "true_output": b, "predicted_role": c, "predicted_output": d}
                      for a, b, c, d in observed_signature if (a, b) != (c, d)]
        split_counts = {}
        for split in ("discovery", "held"):
            totals = Counter()
            errors = Counter()
            true_wholeword_counts = Counter()
            for rows, gold_words in aligned(world, arm, split):
                paragraph_errors = 0
                for codes, gold in zip(rows, gold_words):
                    if "".join(key[c]["output"] for c in codes) != gold:
                        raise ValueError("Original-spelling truth roundtrip changed")
                    predicted = "".join(fit["key"][c]["output"] for c in codes)
                    wholeword = len(codes) == 1 and key[codes[0]]["role"] == "W"
                    if wholeword:
                        true_wholeword_counts[gold] += 1
                    totals["words"] += 1
                    if gold != predicted:
                        paragraph_errors += 1
                        totals["wrong_words"] += 1
                        totals["edit_distance"] += edit_distance(gold, predicted)
                        totals["non_wholeword_errors"] += not wholeword
                        # Only erroneous wholeword macro outputs are disclosed.
                        if wholeword:
                            errors[gold, predicted] += 1
                totals["paragraphs"] += 1
                totals["exact_paragraphs"] += paragraph_errors == 0
            split_counts[split] = {**dict(totals),
                "error_pairs": [{"true_output": gold, "predicted_output": pred,
                                 "wrong_word_occurrences": count,
                                 "source_occurrences_of_true_output": true_wholeword_counts[gold]}
                                for (gold, pred), count in sorted(errors.items())]}
        recorded = primary[world, arm]
        held = split_counts["held"]
        expected = recorded["recovery"]["all"]
        if (held["words"] - held["wrong_words"], held["edit_distance"], held["exact_paragraphs"]) != (
                expected["exact_words"], expected["edit_distance"], recorded["exact_held_paragraphs"]):
            raise ValueError("Aggregate error counts do not reproduce primary result")
        selected_rows.append({"world_id": world, "arm": arm, "selected_start": fit["start"],
            "observed_truth_carriers": len(observed_signature), "key_errors": key_errors,
            "split_counts": split_counts,
            "existing_primary_selected_minus_true_oracle_nats": recorded["selected_minus_oracle"]})
        group = [fits[name] for name in lock["restarts"] if (fits[name]["world_id"], fits[name]["arm"]) == (world, arm)]
        classes = {"exact_observed_truth": [], "same_observed_map_as_selected": [], "other": []}
        for restart in sorted(group, key=lambda row: row["start"]):
            sig = signature(restart)
            label = ("exact_observed_truth" if all((a, b) == (c, d) for a, b, c, d in sig)
                     else "same_observed_map_as_selected" if sig == observed_signature else "other")
            classes[label].append(restart["start"])
            classifications[label] += 1
        restart_rows.append({"world_id": world, "arm": arm, "fixed_restarts": len(group),
            "starts_by_observed_map": classes,
            "recorded_objective_range_by_observed_map": {
                label: {"minimum": min(f["discovery_objective"]["total_nats"] for f in group if f["start"] in starts),
                        "maximum": max(f["discovery_objective"]["total_nats"] for f in group if f["start"] in starts)}
                for label, starts in classes.items() if starts}})
    bindings["src/post_result_audit.py"] = sha(Path(__file__))
    return {"schema": "GDT834_POST_RESULT_AUDIT_V1", "status": "POSTHOC_AGGREGATE_AUDIT_COMPLETE",
        "primary_status_unchanged": result["status"], "outside_preregistration": True,
        "no_new_fit_or_objective_scoring": True, "no_new_key_or_oracle_panel": True,
        "denominator": "Each condition separately: all ordered original source word occurrences in its split. Six conditions share the same content and are not independent text samples. Carrier comparisons use discovery/held union; unused slots are excluded.",
        "selected_conditions": len(selected_rows), "distinct_selected_observed_role_output_maps": len(selected_signatures),
        "all_selected_mappings_identical_after_truth_carrier_alignment": len(selected_signatures) == 1,
        "selected": selected_rows, "existing_restart_counts": dict(classifications),
        "existing_restart_detail": restart_rows,
        "interpretation_limit": "Existing restart classifications do not establish a global optimum. Existing primary oracle differences are copied, not rescored. This posthoc audit cannot repair the formal recovery failure.",
        "source_sha256": bindings}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-dir", type=Path, default=BASE)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    result = audit(args.data_dir)
    output = args.data_dir / "artifacts/POST_RESULT_AUDIT.json"
    encoded = (json.dumps(result, indent=2, sort_keys=True) + "\n").encode()
    if args.check:
        if output.read_bytes() != encoded:
            raise ValueError("Post-result aggregate artifact differs")
    else:
        output.write_bytes(encoded)
    print(json.dumps({key: result[key] for key in ["status", "primary_status_unchanged",
          "distinct_selected_observed_role_output_maps", "existing_restart_counts"]}, sort_keys=True))
    print(json.dumps({"first_condition_errors": result["selected"][0]["key_errors"],
                     "first_condition_counts": result["selected"][0]["split_counts"]}, sort_keys=True))


if __name__ == "__main__":
    main()
