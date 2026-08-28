#!/usr/bin/env python3
"""Summarize GDT607 output-bucket confounds and five distinct formal roles."""
from __future__ import annotations

import csv
import hashlib
import json
import math
import statistics
from collections import Counter, defaultdict
from pathlib import Path


HERE = Path(__file__).resolve().parent.parent
OUT = HERE / "artifacts"
G606 = HERE.parent / "gdt606_mixed_nomenclator_decoder" / "artifacts"
TARGETS = ("o", "y", "ol", "C", "d")
STANDALONE_CONTROLS = ("qokaN", "qokEdy", "qokaI", "qokedy", "qokEy")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def average_ranks(values: list[float]) -> list[float]:
    order = sorted(range(len(values)), key=lambda index: values[index])
    output = [0.0] * len(values)
    cursor = 0
    while cursor < len(order):
        end = cursor + 1
        while end < len(order) and values[order[end]] == values[order[cursor]]:
            end += 1
        rank = (cursor + end - 1) / 2 + 1
        for index in order[cursor:end]:
            output[index] = rank
        cursor = end
    return output


def spearman(left: list[float], right: list[float]) -> float:
    a, b = average_ranks(left), average_ranks(right)
    mean_a, mean_b = statistics.mean(a), statistics.mean(b)
    numerator = sum((x - mean_a) * (y - mean_b) for x, y in zip(a, b))
    denominator = math.sqrt(
        sum((x - mean_a) ** 2 for x in a)
        * sum((y - mean_b) ** 2 for y in b)
    )
    return numerator / denominator


def context_features(data: dict, split: str):
    records = data["sequences"][split]
    line_chunks: dict[str, list[dict]] = defaultdict(list)
    for record in records:
        line_chunks[record["locus"]].append(record)
    line_first = Counter()
    line_last = Counter()
    occurrences = Counter()
    left_neighbors = defaultdict(Counter)
    right_neighbors = defaultdict(Counter)
    section_counts = defaultdict(Counter)
    section_totals = Counter()
    for chunks in line_chunks.values():
        chunks.sort(key=lambda record: record["chunk_index"])
        if chunks and chunks[0]["units"]:
            line_first[chunks[0]["units"][0]] += 1
        if chunks and chunks[-1]["units"]:
            line_last[chunks[-1]["units"][-1]] += 1
        for record in chunks:
            units = record["units"]
            section = record["section"]
            for index, unit in enumerate(units):
                occurrences[unit] += 1
                section_counts[unit][section] += 1
                section_totals[section] += 1
                left_neighbors[unit][units[index - 1] if index else "<CHUNK>"] += 1
                right_neighbors[unit][units[index + 1] if index + 1 < len(units) else "<CHUNK>"] += 1

    def normalized_entropy(counter: Counter) -> float:
        total = sum(counter.values())
        if total <= 1 or len(counter) <= 1:
            return 0.0
        entropy = -sum(
            (count / total) * math.log2(count / total) for count in counter.values()
        )
        return entropy / math.log2(len(counter))

    return {
        unit: {
            "line_first_fraction": line_first[unit] / occurrences[unit],
            "line_last_fraction": line_last[unit] / occurrences[unit],
            "left_neighbor_types": len(left_neighbors[unit]),
            "right_neighbor_types": len(right_neighbors[unit]),
            "left_neighbor_entropy": normalized_entropy(left_neighbors[unit]),
            "right_neighbor_entropy": normalized_entropy(right_neighbors[unit]),
            "section_rates_per_1000": {
                section: 1000 * section_counts[unit][section] / section_totals[section]
                for section in sorted(section_totals)
            },
        }
        for unit in data["inventory"]
        if occurrences[unit]
    }


def main() -> int:
    mappings = read_tsv(OUT / "gdt607_complete_mappings.tsv")
    features = {
        row["unit"]: row
        for row in read_tsv(OUT / "gdt607_unit_structural_features.tsv")
        if row["split"] == "train"
    }
    held_features = {
        row["unit"]: row
        for row in read_tsv(OUT / "gdt607_unit_structural_features.tsv")
        if row["split"] == "held"
    }
    units = sorted(features)
    primary_w = Counter(
        row["unit"]
        for row in mappings
        if row["config"] == "B0_W11" and row["category"] == "W"
    )
    w_fraction = [primary_w[unit] / 18 for unit in units]
    correlations = {
        "train_frequency": spearman(
            w_fraction, [math.log1p(float(features[unit]["occurrences"])) for unit in units]
        ),
        "train_standalone_fraction": spearman(
            w_fraction, [float(features[unit]["standalone_fraction"]) for unit in units]
        ),
        "train_middle_fraction": spearman(
            w_fraction, [float(features[unit]["middle_fraction"]) for unit in units]
        ),
    }

    data = json.loads((G606 / "unit_sequences.json").read_text())
    contexts = {split: context_features(data, split) for split in ("train", "held")}
    formal_defaults = {
        "C": "STRICT_LOCAL_CHUNK_OPENER",
        "d": "CHUNK_AND_PHYSICAL_LINE_HEAD_CARRIER",
        "y": "CHUNK_LINE_AND_WEAK_PARAGRAPH_CLOSURE_CARRIER",
        "ol": "BOUNDARY_AND_OCCASIONAL_STANDALONE_CARRIER",
        "o": "FLEXIBLE_BIDIRECTIONAL_CONNECTOR",
    }
    role_rows = []
    for unit in TARGETS:
        row = {
            "unit": unit,
            "formal_default": formal_defaults[unit],
            "train_occurrences": features[unit]["occurrences"],
            "held_occurrences": held_features[unit]["occurrences"],
            "held_standalone_fraction": held_features[unit]["standalone_fraction"],
            "held_chunk_first_fraction": held_features[unit]["first_fraction"],
            "held_chunk_last_fraction": held_features[unit]["last_fraction"],
            "held_chunk_middle_fraction": held_features[unit]["middle_fraction"],
            "held_line_first_fraction": contexts["held"][unit]["line_first_fraction"],
            "held_line_last_fraction": contexts["held"][unit]["line_last_fraction"],
            "held_left_neighbor_types": contexts["held"][unit]["left_neighbor_types"],
            "held_right_neighbor_types": contexts["held"][unit]["right_neighbor_types"],
            "held_left_neighbor_entropy": contexts["held"][unit]["left_neighbor_entropy"],
            "held_right_neighbor_entropy": contexts["held"][unit]["right_neighbor_entropy"],
            "primary_W_runs_of_18": primary_w[unit],
            "B_runs_with_B_slots_of_72": sum(
                row["category"] == "B"
                for row in mappings
                if row["unit"] == unit and row["config"] != "B0_W11"
            ),
            "W_runs_at_B8_W3_of_18": sum(
                row["category"] == "W"
                for row in mappings
                if row["unit"] == unit and row["config"] == "B8_W3"
            ),
        }
        role_rows.append(row)
    with (OUT / "gdt607_formal_role_defaults.tsv").open("w", newline="") as handle:
        writer = csv.DictWriter(
            handle, fieldnames=list(role_rows[0]), delimiter="\t", lineterminator="\n"
        )
        writer.writeheader()
        writer.writerows(role_rows)

    b_stability = {}
    for config in ("B3_W8", "B6_W5", "B8_W3", "B11_W0"):
        b_stability[config] = {}
        for language in ("latin", "old_italian", "middle_high_german"):
            counts = Counter(
                row["unit"]
                for row in mappings
                if row["config"] == config
                and row["language"] == language
                and row["category"] == "B"
            )
            b_stability[config][language] = {
                "all_six_units": sorted(unit for unit, count in counts.items() if count == 6),
                "maximum_start_support": max(counts.values()),
            }

    standalone_control = {
        unit: {
            "train_standalone_fraction": float(features[unit]["standalone_fraction"]),
            "primary_W_runs_of_18": primary_w[unit],
        }
        for unit in STANDALONE_CONTROLS
    }
    output = {
        "schema": "gdt607-output-bucket-and-formal-role-audit-v1",
        "input_hashes": {
            "complete_mappings": sha256(OUT / "gdt607_complete_mappings.tsv"),
            "structural_features": sha256(OUT / "gdt607_unit_structural_features.tsv"),
            "unit_sequences": sha256(G606 / "unit_sequences.json"),
        },
        "primary_W_correlations": correlations,
        "standalone_counterclass": standalone_control,
        "boundary_category_stability": b_stability,
        "formal_defaults": {row["unit"]: row for row in role_rows},
        "decision": "W_BUCKET_CONFUND_CORRECTED__FIVE_DISTINCT_OUTPUT_BEARING_FORMAL_ROLES",
        "next": (
            "Decompose BPE units into shared collapsed-glyph stems; fit distinct "
            "prefix, suffix, internal, whole-form and null roles with output-length/codebook MDL, "
            "then require synthetic and held carrier recovery before importing meanings."
        ),
        "claim_ceiling": (
            "Formal train-to-held positional roles and decoder-confound correction only; "
            "no word, morpheme, sound, language or meaning."
        ),
    }
    path = OUT / "gdt607_analysis.json"
    path.write_text(json.dumps(output, indent=2, sort_keys=True) + "\n")
    print(json.dumps({
        "decision": output["decision"],
        "primary_W_correlations": correlations,
        "formal_defaults": formal_defaults,
        "sha256": sha256(path),
    }, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
