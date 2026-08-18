#!/usr/bin/env python3
"""Run the frozen GDT292 right-family closure-channel experiment."""
from __future__ import annotations

import csv
import hashlib
import json
import math
import random
import statistics
from collections import Counter, defaultdict
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

R = Path(__file__).resolve().parent
DESIGN = R / "gdt292_design.json"
METHOD = R / "GDT292_RIGHT_FAMILY_CLOSURE_CHANNEL_METHOD.md"
REPORT = R / "GDT292_RIGHT_FAMILY_CLOSURE_CHANNEL_REPORT.md"
RESULT = R / "gdt292_result.json"
OUT_PANEL = R / "gdt292_panel_scores.tsv"
OUT_FOLD = R / "gdt292_folio_scores.tsv"
OUT_BREAK = R / "gdt292_transfer_breakdown.tsv"
OUT_NULL = R / "gdt292_null_results.tsv"
OUT_SENS = R / "gdt292_voynich_sensitivities.tsv"
OUT_COUNTER = R / "gdt292_counterexamples.tsv"
MODELS = ("LAYOUT_CONTEXT", "EXACT_HOST", "OUTER_LOCAL_CONTEXT", "RIGHT_FAMILY")
ALPHA = 0.5


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def canonical_sha(value):
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, ensure_ascii=True, separators=(",", ":")).encode()
    ).hexdigest()


def result_sha(value):
    value = dict(value)
    value.pop("content_sha256", None)
    return canonical_sha(value)


def read_tsv(path):
    with Path(path).open(encoding="utf8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path, rows):
    fields = []
    for row in rows:
        for key in row:
            if key not in fields:
                fields.append(key)
    with Path(path).open("w", encoding="utf8", newline="") as handle:
        writer = csv.DictWriter(handle, fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows([{key: row.get(key, "NA") for key in fields} for row in rows])


def ordinal_bucket(value):
    n = int(value)
    return "1" if n == 1 else "2" if n == 2 else "3_4" if n <= 4 else "5_PLUS"


def group_position(row):
    index = int(row["group_index"])
    count = int(row["group_count"])
    return "ONLY" if count == 1 else "FIRST" if index == 1 else "LAST" if index == count else "MIDDLE"


def outcome(row):
    return "|".join((row["dy_closure"], row["b3"], row["line_close"], row["paragraph_close"]))


def layout_key(row):
    return (
        row["section"], row["currier"], row["hand"], row["register"],
        row["within_field_position"], ordinal_bucket(row["record_ordinal"]),
        ordinal_bucket(row["field_ordinal"]), group_position(row), int(row["host_length"]),
    )


def outer_key(row):
    return (row["page_host"], row["wrapper"], row["local_frame"], row["inner_d"])


def right_key(row):
    return outer_key(row) + (row["right_family"],)


def null_key(row):
    return (
        row["physical_folio"], *layout_key(row), row["wrapper"],
        row["local_frame"], row["inner_d"],
    )


def score(events, split="physical_folio", prior=11.0, keep_predictions=False):
    outcomes = sorted({outcome(row) for row in events})
    outcome_index = {value: index for index, value in enumerate(outcomes)}
    k = len(outcomes)
    folds = defaultdict(list)
    for index, row in enumerate(events):
        folds[row[split]].append(index)
    totals = Counter()
    tops = Counter()
    fold_rows = []
    predictions = []
    breakdown = defaultdict(lambda: [0, 0.0])
    for held, test_ids in sorted(folds.items()):
        train_ids = [index for index, row in enumerate(events) if row[split] != held]
        global_counts = Counter()
        layout_counts = defaultdict(Counter)
        host_counts = defaultdict(Counter)
        outer_counts = defaultdict(Counter)
        right_counts = defaultdict(Counter)
        for index in train_ids:
            row = events[index]
            y = outcome(row)
            global_counts[y] += 1
            layout_counts[layout_key(row)][y] += 1
            host_counts[row["page_host"]][y] += 1
            outer_counts[outer_key(row)][y] += 1
            right_counts[right_key(row)][y] += 1
        fold_bits = Counter()
        fold_top = Counter()
        for index in test_ids:
            row = events[index]
            actual = outcome(row)
            probabilities = {model: {} for model in MODELS}
            for y in outcomes:
                p0 = (global_counts[y] + ALPHA) / (len(train_ids) + ALPHA * k)
                counts = layout_counts[layout_key(row)]
                p_layout = (counts[y] + prior * p0) / (sum(counts.values()) + prior)
                counts = host_counts[row["page_host"]]
                p_host = (counts[y] + prior * p_layout) / (sum(counts.values()) + prior)
                counts = outer_counts[outer_key(row)]
                p_outer = (counts[y] + prior * p_host) / (sum(counts.values()) + prior)
                counts = right_counts[right_key(row)]
                p_right = (counts[y] + prior * p_outer) / (sum(counts.values()) + prior)
                for model, probability in zip(MODELS, (p_layout, p_host, p_outer, p_right)):
                    probabilities[model][y] = probability
            for model in MODELS:
                bits = -math.log2(probabilities[model][actual])
                totals[model] += bits
                fold_bits[model] += bits
                predicted = max(outcomes, key=lambda y: (probabilities[model][y], -outcome_index[y]))
                correct = int(predicted == actual)
                tops[model] += correct
                fold_top[model] += correct
            gain = math.log2(probabilities["RIGHT_FAMILY"][actual] / probabilities["OUTER_LOCAL_CONTEXT"][actual])
            for kind, value in (
                ("RIGHT_FAMILY", row["right_family"]),
                ("CLOSURE_CLASS", actual),
                ("FOLIO", held),
            ):
                breakdown[kind, value][0] += 1
                breakdown[kind, value][1] += gain
            if keep_predictions:
                predictions.append({
                    "actual": actual,
                    "outer": probabilities["OUTER_LOCAL_CONTEXT"],
                    "right": probabilities["RIGHT_FAMILY"],
                    "null_key": null_key(row),
                    "observation_id": row["observation_id"],
                })
        for model in MODELS:
            fold_rows.append({
                "split": "HELD_" + split.upper(), "held_value": held,
                "prior_mass": prior, "model": model, "events": len(test_ids),
                "bits": fold_bits[model], "top1": fold_top[model],
            })
    return {
        "outcomes": outcomes, "bits": dict(totals), "top1": dict(tops),
        "fold_rows": fold_rows, "predictions": predictions,
        "breakdown": {key: value for key, value in breakdown.items()},
        "events": len(events),
    }


def null_gains(scored, panel, worlds):
    predictions = scored["predictions"]
    strata = defaultdict(list)
    for index, row in enumerate(predictions):
        strata[row["null_key"]].append(index)
    values = []
    mobile_world0 = 0
    swappable_events = sum(len(ids) for ids in strata.values() if len(ids) > 1)
    for world in range(worlds):
        labels = [row["actual"] for row in predictions]
        for key, ids in sorted(strata.items(), key=lambda item: repr(item[0])):
            seed_text = "GDT292_HELD_CLOSURE_ALIGNMENT|{}|{}|{}".format(
                panel, world, "|".join(map(str, key))
            )
            rng = random.Random(int(hashlib.sha256(seed_text.encode()).hexdigest()[:16], 16))
            shuffled = [labels[index] for index in ids]
            rng.shuffle(shuffled)
            for index, label in zip(ids, shuffled):
                if world == 0 and label != labels[index]:
                    mobile_world0 += 1
                labels[index] = label
        gain = sum(
            math.log2(row["right"][label] / row["outer"][label])
            for row, label in zip(predictions, labels)
        ) / len(predictions)
        values.append(gain)
    return values, mobile_world0, swappable_events


def worker(item):
    panel, events, worlds = item
    scored = score(events, keep_predictions=True)
    null_values, mobile, swappable = null_gains(scored, panel, worlds)
    return panel, scored, null_values, mobile, swappable


def gain_per_event(scored):
    return (scored["bits"]["OUTER_LOCAL_CONTEXT"] - scored["bits"]["RIGHT_FAMILY"]) / scored["events"]


def main():
    design = json.loads(DESIGN.read_text())
    assert design["status"] == "FROZEN_BEFORE_GDT292_SCORING"
    assert design["content_sha256"] == result_sha(design)
    for row in read_tsv(R / "gdt292_freeze_manifest.tsv"):
        assert sha(R / row["artifact"]) == row["frozen_sha256"]
    native = read_tsv(R / "gdt278_native_event_inventory.tsv")
    assert not any(row["page"].startswith("f84") or row["locus"].startswith("f84") for row in native)
    panels = {panel: [row for row in native if row["control_id"] == panel] for panel in design["panels"]}
    assert all(len(rows) == design["events_per_panel"] for rows in panels.values())

    results = {}
    with ProcessPoolExecutor(max_workers=4) as executor:
        futures = {
            executor.submit(worker, (panel, rows, design["null_worlds"])): panel
            for panel, rows in panels.items()
        }
        for future in as_completed(futures):
            panel, scored, null_values, mobile, swappable = future.result()
            results[panel] = (scored, null_values, mobile, swappable)
            print(json.dumps({"panel": panel, "gain": gain_per_event(scored)}, sort_keys=True), flush=True)

    panel_rows = []
    fold_rows = []
    breakdown_rows = []
    null_rows = []
    observations = {}
    null_means = {}
    null_sds = {}
    for panel in design["panels"]:
        scored, null_values, mobile, swappable = results[panel]
        observations[panel] = gain_per_event(scored)
        null_means[panel] = statistics.mean(null_values)
        null_sds[panel] = statistics.pstdev(null_values)
        for model in MODELS:
            panel_rows.append({
                "control_id": panel, "split": "HELD_PHYSICAL_FOLIO",
                "prior_mass": design["primary_prior_mass"], "model": model,
                "events": scored["events"], "bits": f'{scored["bits"][model]:.12f}',
                "bits_per_event": f'{scored["bits"][model] / scored["events"]:.12f}',
                "top1": scored["top1"][model],
                "top1_rate": f'{scored["top1"][model] / scored["events"]:.12f}',
            })
        for row in scored["fold_rows"]:
            base = next(
                x for x in scored["fold_rows"]
                if x["held_value"] == row["held_value"] and x["model"] == "OUTER_LOCAL_CONTEXT"
            )
            fold_rows.append({
                "control_id": panel, **row, "bits": f'{row["bits"]:.12f}',
                "right_gain_bits": f'{base["bits"] - row["bits"]:.12f}'
                if row["model"] == "RIGHT_FAMILY" else "NA",
            })
        for (kind, value), pair in sorted(scored["breakdown"].items()):
            count, gain = pair
            breakdown_rows.append({
                "control_id": panel, "breakdown": kind, "value": value,
                "events": count, "gain_bits": f"{gain:.12f}",
                "gain_bits_per_event": f"{gain / count:.12f}",
            })
        for world, value in enumerate(null_values):
            null_rows.append({
                "control_id": panel, "world_index": world,
                "right_gain_bits_per_event": f"{value:.12f}",
            })

    variable_panels = [panel for panel in design["panels"] if null_sds[panel] > 1e-15]
    fixed_panels = [panel for panel in design["panels"] if panel not in variable_panels]
    z_scores = {
        panel: (observations[panel] - null_means[panel]) / null_sds[panel]
        for panel in variable_panels
    }
    world_max = [
        max((results[panel][1][world] - null_means[panel]) / null_sds[panel] for panel in variable_panels)
        for world in range(design["null_worlds"])
    ] if variable_panels else []
    summaries = []
    for panel in design["panels"]:
        scored, null_values, mobile, swappable = results[panel]
        variable = panel in variable_panels
        local_p = (1 + sum(value >= observations[panel] - 1e-15 for value in null_values)) / (design["null_worlds"] + 1) if variable else None
        max_p = (1 + sum(value >= z_scores[panel] - 1e-15 for value in world_max)) / (design["null_worlds"] + 1) if variable else None
        right_rows = [value for (kind, _), value in scored["breakdown"].items() if kind == "RIGHT_FAMILY"]
        fold_gain_rows = [
            row for row in scored["fold_rows"] if row["model"] == "RIGHT_FAMILY"
        ]
        positive_folios = 0
        for row in fold_gain_rows:
            base = next(
                x for x in scored["fold_rows"]
                if x["held_value"] == row["held_value"] and x["model"] == "OUTER_LOCAL_CONTEXT"
            )
            positive_folios += int(base["bits"] - row["bits"] > 0)
        summaries.append({
            "control_id": panel, "events": scored["events"],
            "folios": len({row["physical_folio"] for row in panels[panel]}),
            "closure_classes": len(scored["outcomes"]),
            "right_family_classes": len({row["right_family"] for row in panels[panel]}),
            "right_gain_bits_per_event": f"{observations[panel]:.12f}",
            "positive_right_family_classes": sum(pair[1] > 0 for pair in right_rows),
            "positive_folios": positive_folios,
            "null_mean": f'{null_means[panel]:.12f}',
            "null_sd": f'{null_sds[panel]:.12f}',
            "observed_z": f'{z_scores[panel]:.12f}' if variable else "NA_ZERO_NULL_VARIANCE",
            "local_p": f'{local_p:.12f}' if variable else "NA_ZERO_NULL_VARIANCE",
            "max_variable_family_p": f'{max_p:.12f}' if variable else "NA_ZERO_NULL_VARIANCE",
            "null_mobile_events_world0": mobile,
            "null_swappable_events": swappable,
        })

    voy = panels["VOYNICH_REFERENCE"]
    sensitivity = []
    for prior in design["voynich_prior_sensitivities"]:
        scored = score(voy, prior=prior)
        sensitivity.append({
            "split": "HELD_PHYSICAL_FOLIO", "prior_mass": prior,
            "events": scored["events"], "right_gain_bits_per_event": gain_per_event(scored),
        })
    for split in ("section", "hand"):
        scored = score(voy, split=split, prior=design["primary_prior_mass"])
        sensitivity.append({
            "split": "HELD_" + split.upper(), "prior_mass": design["primary_prior_mass"],
            "events": scored["events"], "right_gain_bits_per_event": gain_per_event(scored),
        })
    sensitivity_rows = [
        {**row, "right_gain_bits_per_event": f'{row["right_gain_bits_per_event"]:.12f}'}
        for row in sensitivity
    ]
    v = next(row for row in summaries if row["control_id"] == "VOYNICH_REFERENCE")
    transfer = {row["split"]: row["right_gain_bits_per_event"] for row in sensitivity}
    gates = {
        "primary_gain_positive": float(v["right_gain_bits_per_event"]) > 0,
        "at_least_four_of_six_right_classes_positive": int(v["right_family_classes"]) == 6 and int(v["positive_right_family_classes"]) >= 4,
        "at_least_sixty_of_ninety_one_folios_positive": int(v["folios"]) == 91 and int(v["positive_folios"]) >= 60,
        "held_section_gain_positive": transfer["HELD_SECTION"] > 0,
        "held_hand_gain_positive": transfer["HELD_HAND"] > 0,
        "maxT_p_le_0_05": not str(v["max_variable_family_p"]).startswith("NA") and float(v["max_variable_family_p"]) <= 0.05,
    }
    status = design["decision"]["support"] if all(gates.values()) else design["decision"]["fail"]

    write_tsv(OUT_PANEL, panel_rows)
    write_tsv(OUT_FOLD, fold_rows)
    write_tsv(OUT_BREAK, breakdown_rows)
    write_tsv(OUT_NULL, null_rows)
    write_tsv(OUT_SENS, sensitivity_rows)
    counterexamples = [
        {"counterexample": "RIGHT_FAMILY_INCREMENT_NONPOSITIVE", "evidence": f'Voynich {float(v["right_gain_bits_per_event"]):+.6f} bits/event', "impact": "fails a transferable closure channel if nonpositive"},
        {"counterexample": "RIGHT_FAMILY_CLASS_CONCENTRATION", "evidence": f'{v["positive_right_family_classes"]}/{v["right_family_classes"]} classes positive', "impact": "fewer than four of six fails breadth"},
        {"counterexample": "FOLIO_CONCENTRATION", "evidence": f'{v["positive_folios"]}/{v["folios"]} folios positive', "impact": "fewer than sixty fails transfer"},
        {"counterexample": "SECTION_OR_HAND_DEPENDENCE", "evidence": f'held-section {transfer["HELD_SECTION"]:+.6f}; held-hand {transfer["HELD_HAND"]:+.6f}', "impact": "either nonpositive fails transfer"},
        {"counterexample": "SAME_GROUP_PARSER_COUPLING", "evidence": "RIGHT_FAMILY and DY/B3 are parsed from the same source group", "impact": "even a positive association cannot establish causal order, suffixation, or semantics"},
        {"counterexample": "ABOVE_SHUFFLED_NULL_BUT_BELOW_PREDICTIVE_BASELINE", "evidence": f'observed {float(v["right_gain_bits_per_event"]):+.6f} versus shuffled mean {float(v["null_mean"]):+.6f} bits/event', "impact": "a small alignment diagnostic does not rescue negative held-folio predictive gain"},
        {"counterexample": "ZERO_VARIANCE_CONTROL_NULL", "evidence": ",".join(fixed_panels) if fixed_panels else "NONE", "impact": "those panels remain descriptive and are excluded from maxT"},
        {"counterexample": "F84_USED", "evidence": "only the published f84-free native inventory was read", "impact": "no f84 access"},
    ]
    write_tsv(OUT_COUNTER, counterexamples)

    report = [
        "# GDT292 — right-family closure channel", "", f"Status: **{status}**.", "",
        "## Held-folio result", "",
        "| panel | gain (bits/event) | positive right classes | positive folios | null SD | local p | max-family p |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    for row in summaries:
        report.append(
            f'| {row["control_id"]} | {float(row["right_gain_bits_per_event"]):+.4f} | '
            f'{row["positive_right_family_classes"]}/{row["right_family_classes"]} | '
            f'{row["positive_folios"]}/{row["folios"]} | {float(row["null_sd"]):.4f} | '
            f'{row["local_p"]} | {row["max_variable_family_p"]} |'
        )
    report += [
        "", "Positive gain means the exact frozen right-family class improves held-folio closure-tuple code length after layout, exact host, wrapper, local frame, and inner-D.",
        "", "The permutation test asks a different question: whether the observed right/closure alignment is less damaging (or more helpful) than shuffled alignments. Voynich may therefore be above its shuffled null while still losing to the outer-context predictive baseline. Frozen support requires positive absolute gain as well as a corrected null result.",
        "", "## Voynich sensitivities", "",
    ]
    for row in sensitivity:
        report.append(f'- {row["split"]}, prior {row["prior_mass"]}: {row["right_gain_bits_per_event"]:+.6f} bits/event.')
    report += ["", "## Frozen gates", ""]
    report += [f'- `{key}`: **{"PASS" if value else "FAIL"}**' for key, value in gates.items()]
    report += [
        "", "## Interpretation and claim ceiling", "",
        "This is a same-group parser-coupled formal association test. Even a positive result would not prove that the right family is a linguistic suffix, that it causally creates closure, or that it is content-neutral. It cannot establish a grammar name, lexical class, abbreviation, sound, language, meaning, plaintext, or translation.",
        "", "Only the published f84-free native event inventory was read. No f84 row was opened, parsed, retained, joined, or scored.",
    ]
    REPORT.write_text("\n".join(report) + "\n")

    outputs = [OUT_PANEL, OUT_FOLD, OUT_BREAK, OUT_NULL, OUT_SENS, OUT_COUNTER, REPORT]
    inputs = [
        "gdt292_design.json", "gdt292_design_validation.json", "gdt292_freeze_manifest.tsv",
        "gdt278_native_event_inventory.tsv", "gdt291_result.json", "gdt290_result.json",
        "gdt062_result.json", "gdt288_result.json",
    ]
    result = {
        "schema": "GDT292_RIGHT_FAMILY_CLOSURE_CHANNEL_RESULT_V1",
        "status": status, "summary": summaries, "voynich_summary": v,
        "voynich_sensitivities": sensitivity, "frozen_gates": gates,
        "variable_null_panels": variable_panels, "zero_null_variance_panels": fixed_panels,
        "same_group_parser_coupled": True, "new_corpora": 0, "new_architectures": 0,
        "semantic_assignments": 0, "page_host_substrings_mined": 0,
        "claim_ceiling": design["claim_ceiling"], "f84": design["f84"],
        "inputs": {name: sha(R / name) for name in inputs},
        "documents": {METHOD.name: sha(METHOD), REPORT.name: sha(REPORT)},
        "implementation": {Path(__file__).name: sha(Path(__file__))},
        "outputs": {path.name: sha(path) for path in outputs},
    }
    result["content_sha256"] = result_sha(result)
    RESULT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"status": status, "voynich": v, "gates": gates}, sort_keys=True))


if __name__ == "__main__":
    main()
