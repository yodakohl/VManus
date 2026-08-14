#!/usr/bin/env python3
"""Held-folio test of DY as local reset versus internal transition."""
from __future__ import annotations

import csv
import hashlib
import json
import math
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent
ALPHA = 0.5


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_sha(value):
    return hashlib.sha256(json.dumps(
        value, sort_keys=True, ensure_ascii=True, separators=(",", ":")
    ).encode()).hexdigest()


def read_tsv(name):
    with (ROOT / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(name, rows):
    rows = list(rows)
    with (ROOT / name).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def fit(events, context):
    counts = defaultdict(Counter)
    totals = Counter()
    for event in events:
        key = context(event)
        counts[key][event["next_state"]] += 1
        totals[key] += 1
    return counts, totals


def bits(events, model, context, alphabet_size):
    counts, totals = model
    total = 0.0
    for event in events:
        key = context(event)
        total -= math.log2(
            (counts[key][event["next_state"]] + ALPHA)
            / (totals[key] + ALPHA * alphabet_size)
        )
    return total


def js_divergence(left, right):
    keys = set(left) | set(right)
    left_total = sum(left.values())
    right_total = sum(right.values())
    result = 0.0
    for key in keys:
        p = left[key] / left_total
        q = right[key] / right_total
        midpoint = (p + q) / 2
        if p:
            result += 0.5 * p * math.log2(p / midpoint)
        if q:
            result += 0.5 * q * math.log2(q / midpoint)
    return result


def main():
    inventory = read_tsv("gdt016_group_state_inventory.tsv")
    assert len(inventory) == 15592
    assert not any(row["locus"].startswith("f84r") for row in inventory)
    grouped = defaultdict(list)
    for row in inventory:
        grouped[row["locus"]].append(row)
    lines = []
    events = []
    starts = Counter()
    post_dy = Counter()
    non_dy_internal = Counter()
    for locus, rows in sorted(grouped.items()):
        rows.sort(key=lambda row: int(row["group_index"]))
        lines.append(rows)
        starts[rows[0]["record_state"]] += 1
        for index in range(1, len(rows)):
            current = rows[index]
            previous = rows[index-1]
            position = ((int(current["group_index"])-1)/(int(current["group_count"])-1)
                        if int(current["group_count"]) > 1 else .5)
            event = {
                "physical_folio": current["physical_folio"],
                "position_bin": min(3, int(position*4)),
                "previous_state": previous["record_state"],
                "previous_dy": int(previous["record_state"] == "DY_RESOLUTION"),
                "next_state": current["record_state"],
            }
            events.append(event)
            (post_dy if event["previous_dy"] else non_dy_internal)[event["next_state"]] += 1
    alphabet = sorted({row["record_state"] for row in inventory})
    folios = sorted({row["physical_folio"] for row in inventory})
    contexts = {
        "POSITION": lambda event: (event["position_bin"],),
        "POSITION_PLUS_DY": lambda event: (event["position_bin"], event["previous_dy"]),
        "POSITION_PLUS_PREVIOUS_STATE": lambda event: (event["position_bin"], event["previous_state"]),
        "PREVIOUS_STATE": lambda event: (event["previous_state"],),
    }
    folds = []
    totals = Counter()
    positive_position_dy_folds = 0
    positive_reset_folds = 0
    reset_total = 0.0
    for held in folios:
        training_events = [event for event in events if event["physical_folio"] != held]
        testing_events = [event for event in events if event["physical_folio"] == held]
        scores = {}
        for name, context in contexts.items():
            scores[name] = bits(testing_events, fit(training_events, context), context, len(alphabet))
            totals[name] += scores[name]
        gain = scores["POSITION"] - scores["POSITION_PLUS_DY"]
        positive_position_dy_folds += gain > 0

        training_lines = [line for line in lines if line[0]["physical_folio"] != held]
        start_counts = Counter(line[0]["record_state"] for line in training_lines)
        internal_counts = Counter()
        for line in training_lines:
            for index in range(1, len(line)):
                if line[index-1]["record_state"] != "DY_RESOLUTION":
                    internal_counts[line[index]["record_state"]] += 1
        start_total = sum(start_counts.values())
        internal_total = sum(internal_counts.values())
        reset_llr = 0.0
        reset_events = 0
        for event in testing_events:
            if not event["previous_dy"]:
                continue
            value = event["next_state"]
            reset_llr += math.log2(
                (start_counts[value]+ALPHA)/(start_total+ALPHA*len(alphabet))
            ) - math.log2(
                (internal_counts[value]+ALPHA)/(internal_total+ALPHA*len(alphabet))
            )
            reset_events += 1
        reset_total += reset_llr
        positive_reset_folds += reset_llr > 0
        folds.append({
            "held_folio": held, "held_internal_boundaries": len(testing_events),
            "held_post_dy_boundaries": reset_events,
            "position_bits": f"{scores['POSITION']:.12f}",
            "position_plus_dy_bits": f"{scores['POSITION_PLUS_DY']:.12f}",
            "position_plus_previous_state_bits": f"{scores['POSITION_PLUS_PREVIOUS_STATE']:.12f}",
            "previous_state_bits": f"{scores['PREVIOUS_STATE']:.12f}",
            "dy_gain_vs_position": f"{gain:.12f}",
            "post_dy_start_vs_internal_log2_likelihood": f"{reset_llr:.12f}",
        })
    write_tsv("gdt018_heldout_boundary_models.tsv", folds)
    profile_rows = []
    for state in alphabet:
        profile_rows.append({
            "state": state, "line_start_count": starts[state],
            "line_start_fraction": f"{starts[state]/sum(starts.values()):.12f}",
            "post_dy_count": post_dy[state],
            "post_dy_fraction": f"{post_dy[state]/sum(post_dy.values()):.12f}",
            "non_dy_internal_count": non_dy_internal[state],
            "non_dy_internal_fraction": f"{non_dy_internal[state]/sum(non_dy_internal.values()):.12f}",
        })
    write_tsv("gdt018_next_state_profiles.tsv", profile_rows)
    dy_gain = totals["POSITION"] - totals["POSITION_PLUS_DY"]
    full_gain = totals["POSITION"] - totals["POSITION_PLUS_PREVIOUS_STATE"]
    selector_paid_gain = dy_gain - math.log2(len(contexts))
    extra_parameters = (8-4)*(len(alphabet)-1)
    bic_penalty = extra_parameters/2*math.log2(len(events))
    bic_net_gain = dy_gain-bic_penalty
    js_post_start = js_divergence(post_dy, starts)
    js_other_start = js_divergence(non_dy_internal, starts)
    status = ("DY_INTERNAL_TRANSITION_NOT_LOCAL_RESET"
              if dy_gain > 0 and reset_total < 0 else "DY_BOUNDARY_FUNCTION_UNRESOLVED")
    report = f"""# GDT018 DY boundary-function report

Status: **{status.replace('_', ' ')}**

`DY` is not a miniature line reset.  Across {sum(post_dy.values())} held
post-DY boundaries, the cross-folio log-likelihood ratio of line-start versus
non-DY internal continuation is {reset_total:.3f} bits; only
{positive_reset_folds}/{len(folios)} held folios favor line-start behavior.
The full-corpus Jensen-Shannon distance is {js_post_start:.4f} bit between
post-DY and line-start distributions, compared with {js_other_start:.4f} bit
between other internal continuations and line starts.

At the same time, DY is a strong transferable transition feature.  The
position-only held code uses {totals['POSITION']:.3f} bits.  Adding only
previous-DY status reduces this to {totals['POSITION_PLUS_DY']:.3f}, a gain of
{dy_gain:.3f} bits across {len(events)} internal boundaries and
{positive_position_dy_folds}/{len(folios)} positive held folios.  It captures
{100*dy_gain/full_gain:.1f}% of the gain obtained by adding the complete
previous state to the position model.  The four-model-selector-paid gain is
{selector_paid_gain:.3f} bits.  Even a conservative {extra_parameters}-extra-
parameter BIC approximation leaves {bic_net_gain:.3f} net bits.

The most coherent functional reading is therefore **internal resolution
linker**: DY closes or resolves a local field while licensing a distinctive
continuation, but it does not restart the line's state machine.  This refines
the earlier HPR/PRS theory: physical newline is the true record reset; DY is
an embedded transition checkpoint.  “Resolution” and “linker” are provisional
functional mnemonics, not translations.

This result uses a post-selected lossy state projection and partly recovers
known `y | q` structure.  It does not identify what is resolved, and it does
not make DY a linguistic suffix.  f84r was absent from the sole input and was
not opened, retained, joined, or scored.  No morpheme, word, syntax, sound,
language, plaintext, meaning, or translation is confirmed.
"""
    (ROOT/"GDT018_DY_BOUNDARY_FUNCTION_REPORT.md").write_text(report)
    outputs = ("gdt018_heldout_boundary_models.tsv", "gdt018_next_state_profiles.tsv",
               "GDT018_DY_BOUNDARY_FUNCTION_REPORT.md")
    inputs = ("gdt016_group_state_inventory.tsv", "gdt016_result.json",
              "GDT018_DY_BOUNDARY_FUNCTION_METHOD.md")
    result = {
        "schema": "GDT018_DY_BOUNDARY_FUNCTION_RESULT_V1", "status": status,
        "groups": len(inventory), "lines": len(lines), "physical_folios": len(folios),
        "internal_boundaries": len(events), "post_dy_boundaries": sum(post_dy.values()),
        "states": alphabet, "model_bits": dict(totals),
        "dy_gain_vs_position": dy_gain, "complete_previous_state_gain_vs_position": full_gain,
        "dy_fraction_of_full_previous_state_gain": dy_gain/full_gain,
        "positive_dy_gain_folios": positive_position_dy_folds,
        "selector_paid_dy_gain": selector_paid_gain, "bic_extra_parameters": extra_parameters,
        "bic_penalty_bits": bic_penalty, "bic_net_gain_bits": bic_net_gain,
        "post_dy_start_vs_internal_log2_likelihood": reset_total,
        "positive_local_reset_folios": positive_reset_folds,
        "js_post_dy_vs_start": js_post_start, "js_non_dy_internal_vs_start": js_other_start,
        "f84r": {"input_contains_rows": False, "opened": False, "retained": False,
                  "joined": False, "scored": False},
        "claim_ceiling": "Transferable anonymous internal-transition function only; no morpheme, word, syntax, sound, language, plaintext, meaning, or translation.",
        "inputs": {name: sha(ROOT/name) for name in inputs},
        "implementation": {"run_gdt018_dy_boundary_function.py": sha(Path(__file__))},
        "outputs": {name: sha(ROOT/name) for name in outputs},
    }
    result["result_content_sha256"] = canonical_sha(result)
    (ROOT/"gdt018_result.json").write_text(json.dumps(result, indent=2, sort_keys=True)+"\n")
    print(json.dumps({"status": status, "dy_gain": dy_gain,
                      "reset_llr": reset_total, "bic_net": bic_net_gain,
                      "positive_folds": positive_position_dy_folds}, sort_keys=True))


if __name__ == "__main__":
    main()
