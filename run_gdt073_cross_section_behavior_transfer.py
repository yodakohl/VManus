#!/usr/bin/env python3
"""GDT073: target-section-held PAGE_HOST behavior-profile transfer."""
from __future__ import annotations

import csv
import hashlib
import json
import math
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "gdt062_right_family_inventory.tsv"
ANN = ROOT / "gdt012_annotated_core_inventory.tsv"
PARSED = ROOT / "gdt059_hpr2_external_inventory.tsv"
METHOD = ROOT / "GDT073_CROSS_SECTION_BEHAVIOR_TRANSFER_METHOD.md"
REPORT = ROOT / "GDT073_CROSS_SECTION_BEHAVIOR_TRANSFER_REPORT.md"
SCORES = ROOT / "gdt073_cross_section_scores.tsv"
FOLDS = ROOT / "gdt073_cross_section_folios.tsv"
PREDICTIONS = ROOT / "gdt073_cross_section_predictions.tsv"
VARIANTS = ROOT / "gdt073_variant_log.tsv"
RESULT = ROOT / "gdt073_result.json"

AXES = ("REL_ENCLOSURE", "REL_EXPLICIT_ATTACHMENT", "REL_ARRAY_OR_GROUP")
REPS = ("RAW_CHAR3", "PAGE_HOST_CHAR3", "BEHAVIOR_SELF_NEIGHBOR_NOPOS")
K = 5
SHRINK = 4.0


def read(path):
    with Path(path).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(path, rows, fields):
    with Path(path).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle, fieldnames=fields, delimiter="\t", lineterminator="\n"
        )
        writer.writeheader()
        writer.writerows(rows)


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def content_sha(value):
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, ensure_ascii=True, separators=(",", ":")).encode()
    ).hexdigest()


def trigrams(items):
    output = []
    for item in items:
        padded = "^" + item + "$"
        output.extend(padded[i : i + 3] for i in range(max(1, len(padded) - 2)))
    return Counter(output)


def distance(left, right):
    keys = set(left) | set(right)
    denominator = sum(max(left[key], right[key]) for key in keys)
    return 1 - sum(min(left[key], right[key]) for key in keys) / denominator if denominator else 0


def capacity(rows, axis):
    positive = [row for row in rows if axis in row["tags"]]
    negative = [row for row in rows if axis not in row["tags"]]
    return (
        len(rows) >= 10
        and len(positive) >= 3
        and len(negative) >= 3
        and len({row["physical_folio"] for row in positive}) >= 2
        and len({row["physical_folio"] for row in negative}) >= 2
    )


def main():
    source = read(SOURCE)
    annotations = read(ANN)
    parsed = read(PARSED)
    assert len(source) == 15592 and len(annotations) == len(parsed) == 671
    assert not any(row["locus"].startswith("f84r") for row in source + parsed)

    by_line = defaultdict(list)
    for row in source:
        by_line[row["locus"]].append(row)
    events = []
    for line in by_line.values():
        line.sort(key=lambda row: int(row["group_index"]))
        for index, row in enumerate(line):
            previous = line[index - 1] if index else None
            following = line[index + 1] if index + 1 < len(line) else None
            tokens = [
                "W=" + row["wrapper"],
                "D=" + row["inner_d"],
                "F=" + row["local_frame"],
                "R=" + row["right_family"],
                "DY=" + row["dy_closure"],
                "B3=" + row["b3"],
                "PW=" + (previous["wrapper"] if previous else "BOS"),
                "PF=" + (previous["local_frame"] if previous else "BOS"),
                "PDY=" + (previous["dy_closure"] if previous else "BOS"),
                "NW=" + (following["wrapper"] if following else "EOS"),
                "NF=" + (following["local_frame"] if following else "EOS"),
                "NDY=" + (following["dy_closure"] if following else "EOS"),
            ]
            events.append(
                {
                    "section": row["section"],
                    "folio": row["physical_folio"],
                    "host": row["page_host"],
                    "tokens": tokens,
                }
            )

    annotation_map = {
        (row["locus"], row["group_index"]): row for row in annotations
    }
    parsed_by_locus = defaultdict(list)
    for row in parsed:
        parsed_by_locus[row["locus"]].append(row)
    rows = []
    for locus, groups in sorted(parsed_by_locus.items()):
        groups.sort(key=lambda row: int(row["group_index"]))
        annotation = annotation_map[locus, groups[0]["group_index"]]
        tags = {
            value
            for value in (annotation["object_tags"] + ";" + annotation["relation_tags"]).split(";")
            if value and value != "LABEL"
        }
        rows.append(
            {
                "unit_id": locus,
                "physical_folio": groups[0]["physical_folio"],
                "section": groups[0]["section"],
                "tags": tags,
                "groups": groups,
                "nuisance": Counter(
                    (
                        "KIND=" + annotation["kind"],
                        "UNIT=" + annotation["unit"],
                        "N=" + str(len(groups)),
                        "CERT=" + annotation["annotation_certainty"],
                    )
                ),
            }
        )

    raw = {row["unit_id"]: trigrams(group["token"] for group in row["groups"]) for row in rows}
    host = {row["unit_id"]: trigrams(group["page_host"] for group in row["groups"]) for row in rows}
    score_rows = []
    fold_rows = []
    prediction_rows = []
    excluded = []

    for target_section in sorted({row["section"] for row in rows}):
        profile_counts = defaultdict(Counter)
        profile_n = Counter()
        profile_folios = defaultdict(set)
        for event in events:
            if event["section"] == target_section:
                continue
            profile_counts[event["host"]].update(event["tokens"])
            profile_n[event["host"]] += 1
            profile_folios[event["host"]].add(event["folio"])
        profiles = {
            page_host: Counter({key: value / profile_n[page_host] for key, value in counts.items()})
            for page_host, counts in profile_counts.items()
            if len(profile_folios[page_host]) >= 2
        }

        def supported(row):
            return all(group["page_host"] in profiles for group in row["groups"])

        target_all = [row for row in rows if row["section"] == target_section and supported(row)]
        training_all = [row for row in rows if row["section"] != target_section and supported(row)]

        def behavior(row):
            output = Counter()
            for group in row["groups"]:
                output.update(profiles[group["page_host"]])
            return output

        for axis in AXES:
            if not capacity(target_all, axis) or not capacity(training_all, axis):
                excluded.append(
                    {
                        "external_axis": axis,
                        "target_section": target_section,
                        "target_loci": len(target_all),
                        "target_positive": sum(axis in row["tags"] for row in target_all),
                        "training_loci": len(training_all),
                        "training_positive": sum(axis in row["tags"] for row in training_all),
                        "status": "EXCLUDED_CAPACITY",
                    }
                )
                continue
            totals = {representation: 0.0 for representation in REPS}
            nuisance_total = 0.0
            by_folio = defaultdict(lambda: {"nuisance": 0.0, "predictions": 0, **{rep: 0.0 for rep in REPS}})
            for target in target_all:
                nuisance_distance = {
                    row["unit_id"]: distance(target["nuisance"], row["nuisance"])
                    for row in training_all
                }
                nearest = sorted(
                    training_all,
                    key=lambda row: (nuisance_distance[row["unit_id"]], row["unit_id"]),
                )[:K]
                weights = [1 / (0.1 + nuisance_distance[row["unit_id"]]) for row in nearest]
                base_probability = (
                    sum(weight * int(axis in row["tags"]) for weight, row in zip(weights, nearest)) + 0.5
                ) / (sum(weights) + 1)
                observed = int(axis in target["tags"])
                nuisance_loss = -math.log2(base_probability if observed else 1 - base_probability)
                nuisance_total += nuisance_loss
                by_folio[target["physical_folio"]]["nuisance"] += nuisance_loss
                by_folio[target["physical_folio"]]["predictions"] += 1
                target_features = {
                    "RAW_CHAR3": raw[target["unit_id"]],
                    "PAGE_HOST_CHAR3": host[target["unit_id"]],
                    "BEHAVIOR_SELF_NEIGHBOR_NOPOS": behavior(target),
                }
                probabilities = {}
                for representation in REPS:
                    def feature(row):
                        if representation == "RAW_CHAR3":
                            return raw[row["unit_id"]]
                        if representation == "PAGE_HOST_CHAR3":
                            return host[row["unit_id"]]
                        return behavior(row)

                    ranked = sorted(
                        training_all,
                        key=lambda row: (
                            nuisance_distance[row["unit_id"]]
                            + distance(target_features[representation], feature(row)),
                            row["unit_id"],
                        ),
                    )[:K]
                    ranked_weights = [
                        1
                        / (
                            0.1
                            + nuisance_distance[row["unit_id"]]
                            + distance(target_features[representation], feature(row))
                        )
                        for row in ranked
                    ]
                    probability = (
                        sum(
                            weight * int(axis in row["tags"])
                            for weight, row in zip(ranked_weights, ranked)
                        )
                        + SHRINK * base_probability
                    ) / (sum(ranked_weights) + SHRINK)
                    loss = -math.log2(probability if observed else 1 - probability)
                    totals[representation] += loss
                    by_folio[target["physical_folio"]][representation] += loss
                    probabilities[representation] = probability
                prediction_rows.append(
                    {
                        "external_axis": axis,
                        "target_section": target_section,
                        "target_folio": target["physical_folio"],
                        "target_locus": target["unit_id"],
                        "observed": observed,
                        "nuisance_probability": base_probability,
                        **{representation + "_probability": probabilities[representation] for representation in REPS},
                    }
                )
            for representation in REPS:
                gains = [values["nuisance"] - values[representation] for values in by_folio.values()]
                score_rows.append(
                    {
                        "external_axis": axis,
                        "target_section": target_section,
                        "target_loci": len(target_all),
                        "target_positive": sum(axis in row["tags"] for row in target_all),
                        "target_folios": len(by_folio),
                        "training_loci": len(training_all),
                        "training_positive": sum(axis in row["tags"] for row in training_all),
                        "training_sections": ";".join(sorted({row["section"] for row in training_all})),
                        "representation": representation,
                        "nuisance_bits": nuisance_total,
                        "held_bits": totals[representation],
                        "gain_bits": nuisance_total - totals[representation],
                        "gain_per_prediction": (nuisance_total - totals[representation]) / len(target_all),
                        "positive_gain_folios": sum(value > 0 for value in gains),
                        "min_folio_gain": min(gains),
                        "max_folio_gain": max(gains),
                    }
                )
            for folio, values in sorted(by_folio.items()):
                for representation in REPS:
                    fold_rows.append(
                        {
                            "external_axis": axis,
                            "target_section": target_section,
                            "target_folio": folio,
                            "predictions": values["predictions"],
                            "representation": representation,
                            "gain_bits": values["nuisance"] - values[representation],
                        }
                    )

    def clean(rows):
        return [
            {key: f"{value:.12g}" if isinstance(value, float) else value for key, value in row.items()}
            for row in rows
        ]

    write(SCORES, clean(score_rows), list(score_rows[0]))
    write(FOLDS, clean(fold_rows), list(fold_rows[0]))
    write(PREDICTIONS, clean(prediction_rows), list(prediction_rows[0]))
    write(ROOT / "gdt073_cross_section_exclusions.tsv", excluded, list(excluded[0]))
    variants = [
        {"variant_id": "V00", "status": "PRIMARY", "description": "Fixed GDT068 SELF+NEIGHBOR no-position profile; target section excluded from profile and annotation training."},
        {"variant_id": "V01", "status": "RUN_BASELINES", "description": "Raw and PAGE_HOST char3 on identical targets and training pools."},
        {"variant_id": "V02", "status": "FIXED_AXIS_FAMILY", "description": "Only GDT070 multi-section axes: enclosure, explicit attachment, array/group."},
        {"variant_id": "V03", "status": "POSTSELECTED_AUDIT", "description": "Axes and representation derive from archived results; no independent validation claim."},
        {"variant_id": "V04", "status": "NOT_RUN", "description": "No alternative smoothing, K, parser, semantic class, gloss, or f84r."},
    ]
    write(VARIANTS, variants, list(variants[0]))
    behavior = [row for row in score_rows if row["representation"] == "BEHAVIOR_SELF_NEIGHBOR_NOPOS"]
    raw_rows = [row for row in score_rows if row["representation"] == "RAW_CHAR3"]
    summary = {
        "cells": len(behavior),
        "positive_cells": sum(row["gain_bits"] > 0 for row in behavior),
        "cells_beating_raw": sum(
            row["gain_bits"]
            > next(
                raw["gain_bits"]
                for raw in raw_rows
                if raw["external_axis"] == row["external_axis"]
                and raw["target_section"] == row["target_section"]
            )
            for row in behavior
        ),
        "total_gain_bits": sum(row["gain_bits"] for row in behavior),
        "cell_mean_gain_per_prediction": sum(row["gain_per_prediction"] for row in behavior) / len(behavior),
    }
    raw_summary = {
        "positive_cells": sum(row["gain_bits"] > 0 for row in raw_rows),
        "total_gain_bits": sum(row["gain_bits"] for row in raw_rows),
        "cell_mean_gain_per_prediction": sum(row["gain_per_prediction"] for row in raw_rows) / len(raw_rows),
    }
    axis_summary = {}
    for axis in AXES:
        selected = [row for row in behavior if row["external_axis"] == axis]
        axis_summary[axis] = {
            "cells": len(selected),
            "positive_cells": sum(row["gain_bits"] > 0 for row in selected),
            "total_gain_bits": sum(row["gain_bits"] for row in selected),
            "mean_gain_per_prediction": sum(row["gain_per_prediction"] for row in selected) / len(selected),
            "sections": ";".join(row["target_section"] for row in selected),
        }
    if summary["positive_cells"] > len(behavior) / 2 and summary["cells_beating_raw"] > len(behavior) / 2:
        status = "BEHAVIOR_PROFILE_CROSS_SECTION_TRANSFER_PROVISIONAL"
    elif summary["positive_cells"] > len(behavior) / 2:
        status = "BEHAVIOR_PROFILE_CROSS_SECTION_SIGNAL_NOT_ABOVE_RAW_STRINGS"
    else:
        status = "BEHAVIOR_PROFILE_CROSS_SECTION_TRANSFER_NOT_SUPPORTED"
    report = f"""# GDT073 — cross-section PAGE_HOST behavior transfer

## Outcome

**{status}**

The frozen behavior profile was trained and represented without the entire
target section.  {summary['cells']} target axis×section cells passed capacity.
It improved on nuisance in {summary['positive_cells']}/{summary['cells']} cells
and beat raw-character trigrams in {summary['cells_beating_raw']}/{summary['cells']}.
Its total gain is {summary['total_gain_bits']:+.3f} bits with cell-balanced
{summary['cell_mean_gain_per_prediction']:+.4f} bit/prediction; raw strings
give {raw_summary['total_gain_bits']:+.3f} bits and
{raw_summary['cell_mean_gain_per_prediction']:+.4f} bit/prediction.

By archived axis, enclosure is positive in
{axis_summary['REL_ENCLOSURE']['positive_cells']}/{axis_summary['REL_ENCLOSURE']['cells']}
target sections, explicit attachment in
{axis_summary['REL_EXPLICIT_ATTACHMENT']['positive_cells']}/{axis_summary['REL_EXPLICIT_ATTACHMENT']['cells']},
and array/group in
{axis_summary['REL_ARRAY_OR_GROUP']['positive_cells']}/{axis_summary['REL_ARRAY_OR_GROUP']['cells']}.

This is the strongest available section-transfer stress test of the HPR3
behavior layer, but the external axes and representation were selected in
earlier archived exploration.  It does not score the four prospective GDT072
predictions and cannot confirm a content class.  Every target cell, folio, and
counterexample is exported.  No semantic class, role, gloss, word, morpheme,
POS, sound, language, plaintext, meaning, or translation is assigned.  f84r
was excluded and not opened, retained, queried, joined, scored, or targeted.
"""
    REPORT.write_text(report, encoding="utf-8")
    result = {
        "schema": "GDT073_CROSS_SECTION_BEHAVIOR_TRANSFER_RESULT_V1",
        "status": status,
        "groups": len(source),
        "annotated_loci": len(rows),
        "axes": list(AXES),
        "representations": list(REPS),
        "summary": summary,
        "raw_summary": raw_summary,
        "axis_summary": axis_summary,
        "selection_disclosure": "The representation and axes are inherited from GDT068/GDT070; this is a postselected archived-data transfer audit, not independent validation.",
        "interpretation": "Target-section-held formal behavior transfer only; target section excluded from source-profile construction and annotation training.",
        "claim_ceiling": "No semantic class, role, gloss, word, morpheme, POS, sound, language, plaintext, meaning, or translation.",
        "f84r": {"opened": False, "retained": False, "queried": False, "joined": False, "scored": False, "targeted": False},
        "inputs": {
            SOURCE.name: sha(SOURCE),
            ANN.name: sha(ANN),
            PARSED.name: sha(PARSED),
            "gdt068_result.json": sha(ROOT / "gdt068_result.json"),
            "gdt070_result.json": sha(ROOT / "gdt070_result.json"),
            "gdt072_result.json": sha(ROOT / "gdt072_result.json"),
        },
        "implementation": {Path(__file__).name: sha(Path(__file__))},
        "outputs": {
            SCORES.name: sha(SCORES),
            FOLDS.name: sha(FOLDS),
            PREDICTIONS.name: sha(PREDICTIONS),
            "gdt073_cross_section_exclusions.tsv": sha(ROOT / "gdt073_cross_section_exclusions.tsv"),
            VARIANTS.name: sha(VARIANTS),
        },
        "documents": {METHOD.name: sha(METHOD), REPORT.name: sha(REPORT)},
    }
    result["result_content_sha256"] = content_sha(result)
    RESULT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"status": status, "summary": summary, "raw": raw_summary, "axes": axis_summary}, sort_keys=True))


if __name__ == "__main__":
    main()
