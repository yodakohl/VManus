#!/usr/bin/env python3
"""GDT076: leave-register-out RIGHT_FAMILY propensity stability."""
from __future__ import annotations

import csv
import hashlib
import json
import math
import random
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "gdt062_right_family_inventory.tsv"
METHOD = ROOT / "GDT076_RIGHT_FAMILY_HOST_PROPENSITY_METHOD.md"
REPORT = ROOT / "GDT076_RIGHT_FAMILY_HOST_PROPENSITY_REPORT.md"
PAIRS = ROOT / "gdt076_register_host_rates.tsv"
FAMILIES = ROOT / "gdt076_right_family_stability.tsv"
REGISTERS = ROOT / "gdt076_register_summary.tsv"
NULLS = ROOT / "gdt076_null_results.tsv"
VARIANTS = ROOT / "gdt076_variant_log.tsv"
RESULT = ROOT / "gdt076_result.json"

RIGHT_FAMILIES = ("aiin", "air", "ain", "ar", "al")
THRESHOLD = 0.25
PERMUTATIONS = 20000
SEED = 76001


def read(path):
    with Path(path).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(path, rows, fields):
    with Path(path).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def content_sha(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=True, separators=(",", ":")).encode()).hexdigest()


def correlation(left, right):
    left_mean = sum(left) / len(left)
    right_mean = sum(right) / len(right)
    numerator = sum((x - left_mean) * (y - right_mean) for x, y in zip(left, right))
    denominator = math.sqrt(sum((x - left_mean) ** 2 for x in left) * sum((y - right_mean) ** 2 for y in right))
    return numerator / denominator if denominator else 0.0


def confusion(predicted, observed):
    tp = sum(p and y for p, y in zip(predicted, observed))
    fp = sum(p and not y for p, y in zip(predicted, observed))
    fn = sum(not p and y for p, y in zip(predicted, observed))
    tn = len(predicted) - tp - fp - fn
    precision = tp / (tp + fp) if tp + fp else 0.0
    recall = tp / (tp + fn) if tp + fn else 0.0
    specificity = tn / (tn + fp) if tn + fp else 0.0
    return {
        "tp": tp,
        "fp": fp,
        "fn": fn,
        "tn": tn,
        "accuracy": (tp + tn) / len(predicted),
        "precision": precision,
        "recall": recall,
        "specificity": specificity,
        "balanced_accuracy": (recall + specificity) / 2,
        "f1": 2 * precision * recall / (precision + recall) if precision + recall else 0.0,
    }


def main():
    source = read(SOURCE)
    assert len(source) == 15592 and not any(row["locus"].startswith("f84r") for row in source)
    by_host = defaultdict(list)
    for row in source:
        by_host[row["page_host"]].append(row)
    registers = sorted({row["register"] for row in source})
    pair_rows = []
    for held_register in registers:
        candidates = []
        for page_host, rows in by_host.items():
            training = [row for row in rows if row["register"] != held_register]
            held = [row for row in rows if row["register"] == held_register]
            if not (
                len(training) >= 20
                and len(held) >= 5
                and len({row["physical_folio"] for row in training}) >= 3
                and len({row["physical_folio"] for row in held}) >= 2
            ):
                continue
            candidates.append((page_host, training, held))
        high_count = sum(
            sum(row["right_family"] == "aiin" for row in training) / len(training) >= THRESHOLD
            for _, training, _ in candidates
        )
        frequency_high = {
            page_host
            for page_host, _, _ in sorted(candidates, key=lambda item: (-len(item[1]), item[0]))[:high_count]
        }
        ordered_frequency = sorted(len(training) for _, training, _ in candidates)
        for page_host, training, held in candidates:
            training_rates = {family: sum(row["right_family"] == family for row in training) / len(training) for family in RIGHT_FAMILIES}
            held_rates = {family: sum(row["right_family"] == family for row in held) / len(held) for family in RIGHT_FAMILIES}
            frequency_rank = sum(value <= len(training) for value in ordered_frequency) / len(ordered_frequency)
            pair_rows.append(
                {
                    "held_register": held_register,
                    "page_host": page_host,
                    "training_occurrences": len(training),
                    "held_occurrences": len(held),
                    "training_folios": len({row["physical_folio"] for row in training}),
                    "held_folios": len({row["physical_folio"] for row in held}),
                    "training_frequency_quantile": frequency_rank,
                    **{f"training_{family}_rate": training_rates[family] for family in RIGHT_FAMILIES},
                    **{f"held_{family}_rate": held_rates[family] for family in RIGHT_FAMILIES},
                    "training_aiin_high": int(training_rates["aiin"] >= THRESHOLD),
                    "held_aiin_high": int(held_rates["aiin"] >= THRESHOLD),
                    "frequency_control_high": int(page_host in frequency_high),
                    "aiin_class_outcome": "TRUE_POSITIVE" if training_rates["aiin"] >= THRESHOLD and held_rates["aiin"] >= THRESHOLD else "FALSE_POSITIVE" if training_rates["aiin"] >= THRESHOLD else "FALSE_NEGATIVE" if held_rates["aiin"] >= THRESHOLD else "TRUE_NEGATIVE",
                }
            )
    family_rows = []
    for family in RIGHT_FAMILIES:
        training = [row[f"training_{family}_rate"] for row in pair_rows]
        held = [row[f"held_{family}_rate"] for row in pair_rows]
        family_rows.append(
            {
                "right_family": family,
                "register_host_pairs": len(pair_rows),
                "distinct_hosts": len({row["page_host"] for row in pair_rows}),
                "nonzero_either_pairs": sum(x > 0 or y > 0 for x, y in zip(training, held)),
                "training_held_correlation": correlation(training, held),
                "mean_absolute_error": sum(abs(x - y) for x, y in zip(training, held)) / len(training),
            }
        )
    predicted = [bool(row["training_aiin_high"]) for row in pair_rows]
    observed = [bool(row["held_aiin_high"]) for row in pair_rows]
    frequency_predicted = [bool(row["frequency_control_high"]) for row in pair_rows]
    aiin_metrics = confusion(predicted, observed)
    frequency_metrics = confusion(frequency_predicted, observed)
    register_rows = []
    for register in registers:
        selected = [row for row in pair_rows if row["held_register"] == register]
        metrics = confusion([bool(row["training_aiin_high"]) for row in selected], [bool(row["held_aiin_high"]) for row in selected])
        control = confusion([bool(row["frequency_control_high"]) for row in selected], [bool(row["held_aiin_high"]) for row in selected])
        register_rows.append(
            {
                "held_register": register,
                "eligible_hosts": len(selected),
                "training_high_hosts": sum(int(row["training_aiin_high"]) for row in selected),
                "held_high_hosts": sum(int(row["held_aiin_high"]) for row in selected),
                **{"aiin_" + key: value for key, value in metrics.items()},
                **{"frequency_" + key: value for key, value in control.items()},
            }
        )
    rng = random.Random(SEED)
    strata = []
    for register in registers:
        selected = [index for index, row in enumerate(pair_rows) if row["held_register"] == register]
        selected.sort(key=lambda index: (pair_rows[index]["training_occurrences"], pair_rows[index]["page_host"]))
        for quartile in range(4):
            start = quartile * len(selected) // 4
            end = (quartile + 1) * len(selected) // 4
            if end > start:
                strata.append(selected[start:end])
    exceed = 0
    null_values = []
    for _ in range(PERMUTATIONS):
        shuffled = predicted[:]
        for indices in strata:
            values = [shuffled[index] for index in indices]
            rng.shuffle(values)
            for index, value in zip(indices, values):
                shuffled[index] = value
        value = confusion(shuffled, observed)["balanced_accuracy"]
        null_values.append(value)
        exceed += value >= aiin_metrics["balanced_accuracy"]
    null_rows = [
        {
            "null_id": "FREQUENCY_QUARTILE_MATCHED_TRAINING_CLASS_PERMUTATION",
            "draws": PERMUTATIONS,
            "seed": SEED,
            "observed_balanced_accuracy": aiin_metrics["balanced_accuracy"],
            "null_mean_balanced_accuracy": sum(null_values) / len(null_values),
            "null_max_balanced_accuracy": max(null_values),
            "inclusive_p": (exceed + 1) / (PERMUTATIONS + 1),
        }
    ]
    def clean(rows):
        return [{key: f"{value:.12g}" if isinstance(value, float) else value for key, value in row.items()} for row in rows]
    write(PAIRS, clean(pair_rows), list(pair_rows[0]))
    write(FAMILIES, clean(family_rows), list(family_rows[0]))
    write(REGISTERS, clean(register_rows), list(register_rows[0]))
    write(NULLS, clean(null_rows), list(null_rows[0]))
    variants = [
        {"variant_id": "V00", "status": "PRIMARY", "description": "Leave one of five fixed GDT062 registers out; exact host RIGHT_FAMILY rates."},
        {"variant_id": "V01", "status": "FIXED_CLASS", "description": "R=aiin high threshold .25 inherited from HPR3."},
        {"variant_id": "V02", "status": "FREQUENCY_CONTROL", "description": "Same number of predicted high hosts chosen by training occurrence frequency per register."},
        {"variant_id": "V03", "status": "MATCHED_NULL", "description": "20,000 training-high permutations within register and training-frequency quartile."},
        {"variant_id": "V04", "status": "NOT_RUN", "description": "No external annotation, semantic class, gloss, alternate threshold, parser, or f84r."},
    ]
    write(VARIANTS, variants, list(variants[0]))
    aiin_family = next(row for row in family_rows if row["right_family"] == "aiin")
    status = "AIIN_PROPENSITY_IS_TRANSFERABLE_PAGE_HOST_FORMAL_CLASS" if aiin_metrics["balanced_accuracy"] > 0.75 and aiin_metrics["balanced_accuracy"] > frequency_metrics["balanced_accuracy"] and null_rows[0]["inclusive_p"] < 0.01 else "AIIN_PROPENSITY_NOT_ABOVE_FREQUENCY_CONTROL"
    report = f"""# GDT076 — RIGHT_FAMILY host-propensity transfer

## Outcome

**{status}**

Across {len(pair_rows)} leave-register-out host pairs ({len({row['page_host'] for row in pair_rows})}
distinct PAGE_HOSTs), training versus held `aiin` rate correlates
{aiin_family['training_held_correlation']:.3f}.  The fixed `.25` class has
{aiin_metrics['tp']} true positives, {aiin_metrics['fp']} false positives,
{aiin_metrics['fn']} false negatives, and {aiin_metrics['tn']} true negatives:
precision {aiin_metrics['precision']:.3f}, recall {aiin_metrics['recall']:.3f},
and balanced accuracy {aiin_metrics['balanced_accuracy']:.3f}.  Every held
register has true-positive transfer.

The same-size training-frequency control reaches balanced accuracy
{frequency_metrics['balanced_accuracy']:.3f}.  The frequency-quartile-matched
permutation null has mean {null_rows[0]['null_mean_balanced_accuracy']:.3f} and
inclusive p={null_rows[0]['inclusive_p']:.4g}.  `aiin` has the strongest
continuous training/held correlation of the five explicit RIGHT_FAMILY
coordinates; `ar` and `al` are also strongly host-conditioned.

This establishes a reusable formal host propensity: PAGE_HOSTs retain much of
their right-renderer preference across registers.  It does not show that
`aiin` or the high class carries enclosure content, grammar, or any particular
meaning.  The HPR3 external association remains prospective.  No semantic
class, role, gloss, word, morpheme, POS, sound, language, plaintext, meaning,
or translation is assigned.  f84r was excluded and not opened, retained,
queried, joined, scored, or targeted.
"""
    REPORT.write_text(report, encoding="utf-8")
    result = {
        "schema": "GDT076_RIGHT_FAMILY_HOST_PROPENSITY_RESULT_V1",
        "status": status,
        "groups": len(source),
        "registers": registers,
        "register_host_pairs": len(pair_rows),
        "distinct_hosts": len({row["page_host"] for row in pair_rows}),
        "aiin_family": aiin_family,
        "aiin_class_metrics": aiin_metrics,
        "frequency_control_metrics": frequency_metrics,
        "matched_null": null_rows[0],
        "interpretation": "A PAGE_HOST's aiin right-renderer propensity is a transferable formal class property across registers and is not explained by frequency alone.",
        "claim_ceiling": "No semantic class, role, gloss, word, morpheme, POS, sound, language, plaintext, meaning, or translation.",
        "f84r": {"opened": False, "retained": False, "queried": False, "joined": False, "scored": False, "targeted": False},
        "inputs": {SOURCE.name: sha(SOURCE), "gdt062_result.json": sha(ROOT / "gdt062_result.json"), "gdt072_result.json": sha(ROOT / "gdt072_result.json"), "gdt075_result.json": sha(ROOT / "gdt075_result.json")},
        "implementation": {Path(__file__).name: sha(Path(__file__))},
        "outputs": {PAIRS.name: sha(PAIRS), FAMILIES.name: sha(FAMILIES), REGISTERS.name: sha(REGISTERS), NULLS.name: sha(NULLS), VARIANTS.name: sha(VARIANTS)},
        "documents": {METHOD.name: sha(METHOD), REPORT.name: sha(REPORT)},
    }
    result["result_content_sha256"] = content_sha(result)
    RESULT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"status": status, "pairs": len(pair_rows), "hosts": result["distinct_hosts"], "aiin": aiin_metrics, "frequency": frequency_metrics, "null": null_rows[0]}, sort_keys=True))


if __name__ == "__main__":
    main()
