#!/usr/bin/env python3
"""Independent reconstruction of GDT292 scoring, nulls, and decision."""
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
RESULT = R / "gdt292_result.json"
OUT = R / "gdt292_validation.json"
MODELS = ("LAYOUT_CONTEXT", "EXACT_HOST", "OUTER_LOCAL_CONTEXT", "RIGHT_FAMILY")
ALPHA = 0.5


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def content_sha(value):
    value = dict(value)
    value.pop("content_sha256", None)
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, ensure_ascii=True, separators=(",", ":")).encode()
    ).hexdigest()


def rows(path):
    with Path(path).open(encoding="utf8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def close(left, right, tolerance=3e-8):
    return math.isclose(float(left), float(right), rel_tol=0, abs_tol=tolerance)


def ob(value):
    n = int(value)
    return "1" if n == 1 else "2" if n == 2 else "3_4" if n <= 4 else "5_PLUS"


def gp(row):
    i, n = int(row["group_index"]), int(row["group_count"])
    return "ONLY" if n == 1 else "FIRST" if i == 1 else "LAST" if i == n else "MIDDLE"


def target(row):
    return "|".join((row["dy_closure"], row["b3"], row["line_close"], row["paragraph_close"]))


def layout(row):
    return (
        row["section"], row["currier"], row["hand"], row["register"],
        row["within_field_position"], ob(row["record_ordinal"]), ob(row["field_ordinal"]),
        gp(row), int(row["host_length"]),
    )


def outer(row):
    return row["page_host"], row["wrapper"], row["local_frame"], row["inner_d"]


def with_right(row):
    return outer(row) + (row["right_family"],)


def permutation_stratum(row):
    return row["physical_folio"], *layout(row), row["wrapper"], row["local_frame"], row["inner_d"]


def rebuild_score(events, split="physical_folio", prior=11.0, retain=False):
    labels = sorted({target(row) for row in events})
    label_rank = {label: index for index, label in enumerate(labels)}
    folds = defaultdict(list)
    for index, row in enumerate(events):
        folds[row[split]].append(index)
    bits = Counter()
    top1 = Counter()
    fold_output = []
    predictions = []
    breakouts = defaultdict(lambda: [0, 0.0])
    for held, test in sorted(folds.items()):
        training = [index for index, row in enumerate(events) if row[split] != held]
        g = Counter()
        lc, hc, oc, rc = (defaultdict(Counter) for _ in range(4))
        for index in training:
            row = events[index]
            label = target(row)
            g[label] += 1
            lc[layout(row)][label] += 1
            hc[row["page_host"]][label] += 1
            oc[outer(row)][label] += 1
            rc[with_right(row)][label] += 1
        fold_bits, fold_top = Counter(), Counter()
        for index in test:
            row = events[index]
            actual = target(row)
            probability = {model: {} for model in MODELS}
            for label in labels:
                p0 = (g[label] + ALPHA) / (len(training) + ALPHA * len(labels))
                count = lc[layout(row)]
                p1 = (count[label] + prior * p0) / (sum(count.values()) + prior)
                count = hc[row["page_host"]]
                p2 = (count[label] + prior * p1) / (sum(count.values()) + prior)
                count = oc[outer(row)]
                p3 = (count[label] + prior * p2) / (sum(count.values()) + prior)
                count = rc[with_right(row)]
                p4 = (count[label] + prior * p3) / (sum(count.values()) + prior)
                for model, p in zip(MODELS, (p1, p2, p3, p4)):
                    probability[model][label] = p
            for model in MODELS:
                value = -math.log2(probability[model][actual])
                bits[model] += value
                fold_bits[model] += value
                guess = max(labels, key=lambda label: (probability[model][label], -label_rank[label]))
                hit = int(guess == actual)
                top1[model] += hit
                fold_top[model] += hit
            gain = math.log2(probability["RIGHT_FAMILY"][actual] / probability["OUTER_LOCAL_CONTEXT"][actual])
            for kind, value in (("RIGHT_FAMILY", row["right_family"]), ("CLOSURE_CLASS", actual), ("FOLIO", held)):
                breakouts[kind, value][0] += 1
                breakouts[kind, value][1] += gain
            if retain:
                predictions.append((actual, probability["OUTER_LOCAL_CONTEXT"], probability["RIGHT_FAMILY"], permutation_stratum(row)))
        for model in MODELS:
            fold_output.append((held, model, len(test), fold_bits[model], fold_top[model]))
    return {
        "labels": labels, "bits": dict(bits), "top1": dict(top1), "folds": fold_output,
        "predictions": predictions, "breakouts": dict(breakouts), "n": len(events),
    }


def rebuild_null(scored, panel, worlds):
    strata = defaultdict(list)
    for index, prediction in enumerate(scored["predictions"]):
        strata[prediction[3]].append(index)
    result = []
    mobile = 0
    swappable = sum(len(indexes) for indexes in strata.values() if len(indexes) > 1)
    for world in range(worlds):
        y = [prediction[0] for prediction in scored["predictions"]]
        for key, indexes in sorted(strata.items(), key=lambda item: repr(item[0])):
            seed = "GDT292_HELD_CLOSURE_ALIGNMENT|{}|{}|{}".format(panel, world, "|".join(map(str, key)))
            rng = random.Random(int(hashlib.sha256(seed.encode()).hexdigest()[:16], 16))
            shuffled = [y[index] for index in indexes]
            rng.shuffle(shuffled)
            for index, label in zip(indexes, shuffled):
                if world == 0 and label != y[index]:
                    mobile += 1
                y[index] = label
        result.append(sum(
            math.log2(prediction[2][label] / prediction[1][label])
            for prediction, label in zip(scored["predictions"], y)
        ) / scored["n"])
    return result, mobile, swappable


def panel_job(item):
    panel, events, worlds = item
    scored = rebuild_score(events, retain=True)
    null, mobile, swappable = rebuild_null(scored, panel, worlds)
    return panel, scored, null, mobile, swappable


def gain(scored):
    return (scored["bits"]["OUTER_LOCAL_CONTEXT"] - scored["bits"]["RIGHT_FAMILY"]) / scored["n"]


def main():
    checks = []

    def check(name, value):
        checks.append({"check": name, "pass": bool(value)})
        assert value, name

    design = json.loads((R / "gdt292_design.json").read_text())
    result = json.loads(RESULT.read_text())
    panel_table = rows(R / "gdt292_panel_scores.tsv")
    fold_table = rows(R / "gdt292_folio_scores.tsv")
    break_table = rows(R / "gdt292_transfer_breakdown.tsv")
    null_table = rows(R / "gdt292_null_results.tsv")
    sensitivity_table = rows(R / "gdt292_voynich_sensitivities.tsv")
    check("design_content", design["content_sha256"] == content_sha(design))
    check("design_status", design["status"] == "FROZEN_BEFORE_GDT292_SCORING")
    manifest = rows(R / "gdt292_freeze_manifest.tsv")
    check("freeze_manifest", len(manifest) == 6 and all(sha(R / row["artifact"]) == row["frozen_sha256"] for row in manifest))
    native = rows(R / "gdt278_native_event_inventory.tsv")
    check("native_no_f84", not any(row["page"].startswith("f84") or row["locus"].startswith("f84") for row in native))
    panels = {panel: [row for row in native if row["control_id"] == panel] for panel in design["panels"]}
    check("panel_event_counts", all(len(value) == 8448 for value in panels.values()))
    check("table_shapes", len(panel_table) == 32 and len(null_table) == 512 and len(sensitivity_table) == 4)

    rebuilt = {}
    with ProcessPoolExecutor(max_workers=4) as executor:
        futures = {
            executor.submit(panel_job, (panel, events, design["null_worlds"])): panel
            for panel, events in panels.items()
        }
        for future in as_completed(futures):
            answer = future.result()
            rebuilt[answer[0]] = answer[1:]

    observed, means, sds = {}, {}, {}
    for panel in design["panels"]:
        scored, null_values, mobile, swappable = rebuilt[panel]
        observed[panel] = gain(scored)
        means[panel] = statistics.mean(null_values)
        sds[panel] = statistics.pstdev(null_values)
        table = [row for row in panel_table if row["control_id"] == panel]
        check("panel_models:" + panel, len(table) == 4)
        for model in MODELS:
            row = next(row for row in table if row["model"] == model)
            check("panel_score:" + panel + ":" + model, int(row["events"]) == 8448 and close(row["bits"], scored["bits"][model]) and int(row["top1"]) == scored["top1"][model])
        stored_folds = [row for row in fold_table if row["control_id"] == panel]
        check("fold_shape:" + panel, len(stored_folds) == len(scored["folds"]))
        check("fold_values:" + panel, all(
            int(next(row for row in stored_folds if row["held_value"] == held and row["model"] == model)["events"]) == n
            and close(next(row for row in stored_folds if row["held_value"] == held and row["model"] == model)["bits"], bits)
            and int(next(row for row in stored_folds if row["held_value"] == held and row["model"] == model)["top1"]) == top
            for held, model, n, bits, top in scored["folds"]
        ))
        stored_breaks = [row for row in break_table if row["control_id"] == panel]
        check("break_shape:" + panel, len(stored_breaks) == len(scored["breakouts"]))
        check("break_values:" + panel, all(
            int(next(row for row in stored_breaks if row["breakdown"] == kind and row["value"] == value)["events"]) == pair[0]
            and close(next(row for row in stored_breaks if row["breakdown"] == kind and row["value"] == value)["gain_bits"], pair[1])
            for (kind, value), pair in scored["breakouts"].items()
        ))
        stored_null = sorted((row for row in null_table if row["control_id"] == panel), key=lambda row: int(row["world_index"]))
        check("null_values:" + panel, len(stored_null) == 64 and all(close(row["right_gain_bits_per_event"], value) for row, value in zip(stored_null, null_values)))
        summary = next(row for row in result["summary"] if row["control_id"] == panel)
        positive_folios = 0
        for held in sorted({row["physical_folio"] for row in panels[panel]}):
            base = next(x for x in scored["folds"] if x[0] == held and x[1] == "OUTER_LOCAL_CONTEXT")
            right = next(x for x in scored["folds"] if x[0] == held and x[1] == "RIGHT_FAMILY")
            positive_folios += int(base[3] - right[3] > 0)
        positive_right = sum(pair[1] > 0 for (kind, _), pair in scored["breakouts"].items() if kind == "RIGHT_FAMILY")
        check("summary_core:" + panel,
              close(summary["right_gain_bits_per_event"], observed[panel])
              and close(summary["null_mean"], means[panel]) and close(summary["null_sd"], sds[panel])
              and int(summary["null_mobile_events_world0"]) == mobile
              and int(summary["null_swappable_events"]) == swappable
              and int(summary["positive_folios"]) == positive_folios
              and int(summary["positive_right_family_classes"]) == positive_right)

    variable = [panel for panel in design["panels"] if sds[panel] > 1e-15]
    z = {panel: (observed[panel] - means[panel]) / sds[panel] for panel in variable}
    maxima = [max((rebuilt[panel][1][world] - means[panel]) / sds[panel] for panel in variable) for world in range(64)]
    for panel in design["panels"]:
        summary = next(row for row in result["summary"] if row["control_id"] == panel)
        if panel in variable:
            local_p = (1 + sum(value >= observed[panel] - 1e-15 for value in rebuilt[panel][1])) / 65
            max_p = (1 + sum(value >= z[panel] - 1e-15 for value in maxima)) / 65
            check("null_summary:" + panel, close(summary["observed_z"], z[panel]) and close(summary["local_p"], local_p) and close(summary["max_variable_family_p"], max_p))
        else:
            check("null_summary:" + panel, summary["observed_z"] == summary["local_p"] == summary["max_variable_family_p"] == "NA_ZERO_NULL_VARIANCE")
    check("variable_panel_lists", result["variable_null_panels"] == variable and result["zero_null_variance_panels"] == [panel for panel in design["panels"] if panel not in variable])

    voy = panels["VOYNICH_REFERENCE"]
    for prior in design["voynich_prior_sensitivities"]:
        scored = rebuild_score(voy, prior=prior)
        stored = next(row for row in result["voynich_sensitivities"] if row["split"] == "HELD_PHYSICAL_FOLIO" and float(row["prior_mass"]) == prior)
        check("prior_sensitivity:" + str(prior), int(stored["events"]) == 8448 and close(stored["right_gain_bits_per_event"], gain(scored)))
    for split in ("section", "hand"):
        scored = rebuild_score(voy, split=split, prior=11.0)
        stored = next(row for row in result["voynich_sensitivities"] if row["split"] == "HELD_" + split.upper())
        check("split_sensitivity:" + split, int(stored["events"]) == 8448 and close(stored["right_gain_bits_per_event"], gain(scored)))

    v = result["voynich_summary"]
    transfers = {row["split"]: float(row["right_gain_bits_per_event"]) for row in result["voynich_sensitivities"]}
    gates = {
        "primary_gain_positive": float(v["right_gain_bits_per_event"]) > 0,
        "at_least_four_of_six_right_classes_positive": int(v["right_family_classes"]) == 6 and int(v["positive_right_family_classes"]) >= 4,
        "at_least_sixty_of_ninety_one_folios_positive": int(v["folios"]) == 91 and int(v["positive_folios"]) >= 60,
        "held_section_gain_positive": transfers["HELD_SECTION"] > 0,
        "held_hand_gain_positive": transfers["HELD_HAND"] > 0,
        "maxT_p_le_0_05": float(v["max_variable_family_p"]) <= 0.05,
    }
    expected_status = design["decision"]["support"] if all(gates.values()) else design["decision"]["fail"]
    check("decision", result["frozen_gates"] == gates and result["status"] == expected_status)
    check("prohibitions", result["same_group_parser_coupled"] is True and result["new_corpora"] == result["new_architectures"] == result["semantic_assignments"] == result["page_host_substrings_mined"] == 0)
    check("result_content", result["content_sha256"] == content_sha(result))
    check("bound_hashes", all(sha(R / name) == value for section in ("inputs", "documents", "implementation", "outputs") for name, value in result[section].items()))
    check("f84_flags", result["f84"]["input_files"] == 0 and not any(value for key, value in result["f84"].items() if key != "input_files"))

    validation = {
        "schema": "GDT292_RIGHT_FAMILY_CLOSURE_CHANNEL_VALIDATION_V1",
        "status": "PASS",
        "validation_scope": "INDEPENDENT_ALL_PANEL_HELD_FOLIO_SCORES_FOLDS_BREAKDOWNS_NULLS_MAXT_VOYNICH_PRIORS_SECTION_HAND_DECISION_AND_HASHES",
        "checks_passed": len(checks), "checks_total": len(checks), "checks": checks,
        "result_sha256": sha(RESULT), "validator_sha256": sha(Path(__file__)),
    }
    validation["content_sha256"] = content_sha(validation)
    OUT.write_text(json.dumps(validation, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"status": "PASS", "checks": len(checks)}, sort_keys=True))


if __name__ == "__main__":
    main()
