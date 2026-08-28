#!/usr/bin/env python3
from __future__ import annotations

import os

import csv
import json
import statistics
from pathlib import Path

WORK = Path(os.environ.get("GDT612_WORK", Path(__file__).resolve().parent)).resolve()
EVAL = WORK / "evaluation"


def read_tsv(path):
    with Path(path).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path, fields, rows):
    with Path(path).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def triple(rows, field):
    values = [float(row[field]) for row in rows]
    return min(values), statistics.mean(values), max(values)


def main():
    metrics = read_tsv(EVAL / "held_run_metrics.tsv")
    stability = {row["language"]: row for row in read_tsv(EVAL / "carrier_stability.tsv")}
    baselines = {row["language"]: row for row in read_tsv(EVAL / "reference_baselines.tsv")}
    rows = []
    for language in ("latin", "old_italian", "middle_high_german"):
        for kind in ("real", "destroyed"):
            selected = [row for row in metrics if row["language"] == language and row["kind"] == kind]
            order = triple(selected, "held_order_signal_bits_per_letter")
            lexicon = triple(selected, "held_lexicon_char_coverage")
            top = triple(selected, "top_token_fraction")
            top10 = triple(selected, "top10_token_fraction")
            output = {
                "language": language, "fit_kind": kind, "starts": len(selected),
                "held_order_min": f"{order[0]:.12f}", "held_order_mean": f"{order[1]:.12f}", "held_order_max": f"{order[2]:.12f}",
                "held_lexicon_min": f"{lexicon[0]:.12f}", "held_lexicon_mean": f"{lexicon[1]:.12f}", "held_lexicon_max": f"{lexicon[2]:.12f}",
                "top_token_fraction_min": f"{top[0]:.12f}", "top_token_fraction_mean": f"{top[1]:.12f}", "top_token_fraction_max": f"{top[2]:.12f}",
                "top10_fraction_min": f"{top10[0]:.12f}", "top10_fraction_mean": f"{top10[1]:.12f}", "top10_fraction_max": f"{top10[2]:.12f}",
                "reference_top_token_fraction": baselines[language]["top_token_fraction"],
                "reference_top10_fraction": baselines[language]["top10_token_fraction"],
            }
            if kind == "real":
                output.update({
                    "primitive_exact_pairwise": stability[language]["primitive_role_output_pairwise_agreement"],
                    "unit_output_pairwise": stability[language]["unit_output_pairwise_agreement"],
                    "unanimous_primitive_outputs": stability[language]["unanimous_primitive_role_output_of_34"],
                    "unanimous_unit_outputs": stability[language]["unanimous_unit_output_of_98"],
                    "unanimous_held_spans": stability[language]["unanimous_held_word_spans"],
                })
            else:
                output.update({
                    "primitive_exact_pairwise": "NA", "unit_output_pairwise": "NA",
                    "unanimous_primitive_outputs": "NA", "unanimous_unit_outputs": "NA", "unanimous_held_spans": "NA",
                })
            rows.append(output)
    write_tsv(EVAL / "language_summary.tsv", list(rows[0]), rows)

    consensus = read_tsv(EVAL / "carrier_consensus.tsv")
    stable_roles = [
        row for row in consensus
        if row["carrier_level"] == "primitive" and row["role_support_of_6"] == "6"
    ]
    write_tsv(EVAL / "unanimous_structural_roles.tsv", list(stable_roles[0]), stable_roles)
    conclusion = {
        "target_ready": False,
        "restart_stable_concrete_meanings": 0,
        "reason": "Synthetic key recovery failed and target has zero unanimous primitive outputs, unit outputs, and held word spans in every language.",
        "positive_held_order_signal_is_not_key_evidence": True,
        "unanimous_structural_roles": len(stable_roles),
        "best_held_paragraph": json.loads((EVAL / "best_held_paragraph.json").read_text()),
    }
    (EVAL / "CONCLUSION.json").write_text(json.dumps(conclusion, indent=2, sort_keys=True) + "\n")
    print(json.dumps(conclusion, sort_keys=True))


if __name__ == "__main__":
    main()
