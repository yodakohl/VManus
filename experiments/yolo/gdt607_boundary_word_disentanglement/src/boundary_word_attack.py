#!/usr/bin/env python3
"""Separate boundary-only signs from whole-word signs in the GDT606 decoder."""
from __future__ import annotations

import argparse
import csv
import importlib.util
import json
import math
import os
import random
import statistics
import sys
from collections import Counter
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
HERE = Path(__file__).resolve().parent.parent
OUT = HERE / "artifacts"
DATA = ROOT / "experiments/yolo/gdt606_mixed_nomenclator_decoder/artifacts/unit_sequences.json"
DATA_SHA256 = "3ee0841e211314b72719acbbf79ed3a6dc7bfc3c157734f54dbdac92ac458fdf"
TARGETS = ("o", "y", "ol", "C", "d")
CONFIGS = {
    "B0_W11": {"L": 42, "D": 4, "S": 34, "N": 7, "B": 0, "W": 11},
    "B3_W8": {"L": 42, "D": 4, "S": 34, "N": 7, "B": 3, "W": 8},
    "B6_W5": {"L": 42, "D": 4, "S": 34, "N": 7, "B": 6, "W": 5},
    "B8_W3": {"L": 42, "D": 4, "S": 34, "N": 7, "B": 8, "W": 3},
    "B11_W0": {"L": 42, "D": 4, "S": 34, "N": 7, "B": 11, "W": 0},
}
SEEDS = (11, 29, 47, 71, 89, 107)


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


G606 = load_module(
    "gdt606_mixed_for_gdt607",
    ROOT / "experiments/yolo/gdt606_mixed_nomenclator_decoder/src/mixed_codebook_attack.py",
)


def decode_sequence(sequence, categories, outputs):
    words: list[str] = []
    buffer: list[str] = []
    for unit in sequence:
        category = categories[unit]
        output = outputs[unit]
        if category == "W":
            if buffer:
                words.append("".join(buffer))
                buffer = []
            words.append(output)
        elif category == "B":
            if buffer:
                words.append("".join(buffer))
                buffer = []
        elif category != "N":
            buffer.append(output)
    if buffer:
        words.append("".join(buffer))
    return words


def initialize_mapping(rng, units, config, candidates, features):
    remaining = set(units)
    categories: dict[str, str] = {}

    # High standalone fraction is a sensible whole-word start, but every
    # category remains swappable during annealing.
    ranked_words = sorted(
        sorted(remaining),
        key=lambda unit: (
            features[unit]["standalone_fraction"] + rng.random() * 0.8,
            rng.random(),
        ),
        reverse=True,
    )
    for unit in ranked_words[: config["W"]]:
        categories[unit] = "W"
        remaining.remove(unit)

    # Boundary signs begin without a target-derived positional preference.
    boundary_units = rng.sample(sorted(remaining), config["B"])
    for unit in boundary_units:
        categories[unit] = "B"
        remaining.remove(unit)

    ranked_nulls = sorted(
        sorted(remaining),
        key=lambda unit: (
            -features[unit]["frequency_quantile"] + rng.random() * 0.8,
            rng.random(),
        ),
        reverse=True,
    )
    for unit in ranked_nulls[: config["N"]]:
        categories[unit] = "N"
        remaining.remove(unit)

    shuffled = sorted(remaining)
    rng.shuffle(shuffled)
    cursor = 0
    for category in ("D", "S", "L"):
        for unit in shuffled[cursor : cursor + config[category]]:
            categories[unit] = category
        cursor += config[category]

    outputs: dict[str, str] = {}
    for category in ("D", "S", "W"):
        assigned = [unit for unit in units if categories[unit] == category]
        selected = rng.sample(candidates[category], len(assigned))
        for unit, output in zip(assigned, selected):
            outputs[unit] = output
    letter_counts = Counter()
    for unit in units:
        category = categories[unit]
        if category == "L":
            available = [char for char in candidates["L"] if letter_counts[char] < 6]
            output = rng.choice(available)
            outputs[unit] = output
            letter_counts[output] += 1
        elif category in {"N", "B"}:
            outputs[unit] = ""
    return categories, outputs


def write_tsv(path: Path, records: list[dict]) -> None:
    if not records:
        path.write_text("")
        return
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(
            handle, fieldnames=list(records[0]), delimiter="\t", lineterminator="\n"
        )
        writer.writeheader()
        writer.writerows(records)


def structural_features(data):
    output = {}
    rows = []
    for split in ("train", "held"):
        records = data["sequences"][split]
        occurrences = Counter(unit for record in records for unit in record["units"])
        solo = Counter(record["units"][0] for record in records if len(record["units"]) == 1)
        first = Counter(record["units"][0] for record in records if record["units"])
        last = Counter(record["units"][-1] for record in records if record["units"])
        middle = Counter(unit for record in records for unit in record["units"][1:-1])
        output[split] = {
            unit: {
                "occurrences": occurrences[unit],
                "standalone_fraction": solo[unit] / occurrences[unit] if occurrences[unit] else 0.0,
                "first_fraction": first[unit] / occurrences[unit] if occurrences[unit] else 0.0,
                "last_fraction": last[unit] / occurrences[unit] if occurrences[unit] else 0.0,
                "middle_fraction": middle[unit] / occurrences[unit] if occurrences[unit] else 0.0,
            }
            for unit in data["inventory"]
        }
        for unit in data["inventory"]:
            rows.append({"split": split, "unit": unit, **output[split][unit]})
    return output, rows


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--reference-dir", type=Path, required=True)
    parser.add_argument("--iterations", type=int, default=8000)
    parser.add_argument("--workers", type=int, default=min(12, os.cpu_count() or 1))
    args = parser.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    if G606.sha(DATA) != DATA_SHA256:
        raise RuntimeError("GDT606 unit sequence binding changed")
    data = json.loads(DATA.read_text())
    units = data["inventory"]
    train_records = data["sequences"]["train"]
    held_records = data["sequences"]["held"]
    structure, structure_rows = structural_features(data)
    write_tsv(OUT / "gdt607_unit_structural_features.tsv", structure_rows)

    train_counter = Counter(tuple(record["units"]) for record in train_records)
    train_chunk_types = list(train_counter)
    train_chunk_weights = [math.sqrt(train_counter[chunk]) for chunk in train_chunk_types]
    affected = {unit: set() for unit in units}
    for index, chunk in enumerate(train_chunk_types):
        for unit in set(chunk):
            affected[unit].add(index)
    unit_occ = Counter(unit for record in train_records for unit in record["units"])
    unit_solo = Counter(
        record["units"][0] for record in train_records if len(record["units"]) == 1
    )
    ranked = {
        unit: index / (len(units) - 1)
        for index, unit in enumerate(sorted(units, key=lambda value: (-unit_occ[value], value)))
    }
    features = {
        unit: {
            "standalone_fraction": unit_solo[unit] / unit_occ[unit],
            "frequency_quantile": 1.0 - ranked[unit],
        }
        for unit in units
    }

    reference_words, reference_hashes = G606.load_reference_words(args.reference_dir)
    packs = {
        language: G606.make_language_pack(words, language)
        for language, words in reference_words.items()
    }
    for pack in packs.values():
        pack["real_candidates"]["B"] = [""]
    G606.CONFIGS = CONFIGS
    G606.decode_sequence = decode_sequence
    G606.initialize_mapping = initialize_mapping
    G606.GLOBAL.update(
        {
            "units": units,
            "train_chunk_types": train_chunk_types,
            "train_chunk_weights": train_chunk_weights,
            "train_affected": affected,
            "features": features,
            "packs": packs,
        }
    )

    jobs = [
        {
            "language": language,
            "model_kind": "real",
            "config": config,
            "seed": seed,
            "iterations": args.iterations,
        }
        for language in sorted(packs)
        for config in CONFIGS
        for seed in SEEDS
    ]
    results = []
    with ProcessPoolExecutor(max_workers=args.workers) as pool:
        futures = [pool.submit(G606.anneal, job) for job in jobs]
        for future in as_completed(futures):
            result = future.result()
            results.append(result)
            print(
                result["language"], result["config"], result["seed"],
                f"objective={result['train_objective']:.6f}", flush=True,
            )
    results.sort(key=lambda row: (row["language"], row["config"], row["seed"]))

    held_frequency = Counter(unit for record in held_records for unit in record["units"])
    mapping_rows = []
    target_rows = []
    summaries = {}
    for language in sorted(packs):
        summaries[language] = {}
        pack = packs[language]
        for config in CONFIGS:
            runs = [
                run for run in results
                if run["language"] == language and run["config"] == config
            ]
            for run in runs:
                held_metrics, _decoded = G606.evaluate_mapping(
                    run["mapping"], held_records, pack["real_model"],
                    pack["destroyed_model"], pack["real_lexicon"],
                )
                run["held_metrics"] = held_metrics
                for unit in units:
                    mapping_rows.append(
                        {
                            "language": language,
                            "config": config,
                            "seed": run["seed"],
                            "unit": unit,
                            "category": run["mapping"][unit]["category"],
                            "output": run["mapping"][unit]["output"] or "<EMPTY>",
                            "train_occurrences": data["frequency"]["train"][unit],
                            "held_occurrences": data["frequency"]["held"].get(unit, 0),
                        }
                    )
            agreements = G606.pair_agreement(runs, held_frequency)
            summaries[language][config] = {
                "train_objective_range": [
                    min(run["train_objective"] for run in runs),
                    max(run["train_objective"] for run in runs),
                ],
                "held_real_minus_destroyed_range": [
                    min(run["held_metrics"]["real_minus_destroyed_bits_per_character"] for run in runs),
                    max(run["held_metrics"]["real_minus_destroyed_bits_per_character"] for run in runs),
                ],
                "minimum_category_held_agreement": min(
                    pair["category_held_weighted_agreement"] for pair in agreements
                ),
                "mean_category_held_agreement": statistics.mean(
                    pair["category_held_weighted_agreement"] for pair in agreements
                ),
            }
            for unit in TARGETS:
                counts = Counter(run["mapping"][unit]["category"] for run in runs)
                target_rows.append(
                    {
                        "language": language,
                        "config": config,
                        "unit": unit,
                        "B_count": counts["B"],
                        "W_count": counts["W"],
                        "L_count": counts["L"],
                        "D_count": counts["D"],
                        "S_count": counts["S"],
                        "N_count": counts["N"],
                        "modal_category": counts.most_common(1)[0][0],
                        "modal_support": counts.most_common(1)[0][1],
                        "held_occurrences": held_frequency[unit],
                        "held_standalone_fraction": structure["held"][unit]["standalone_fraction"],
                        "held_first_fraction": structure["held"][unit]["first_fraction"],
                        "held_last_fraction": structure["held"][unit]["last_fraction"],
                        "held_middle_fraction": structure["held"][unit]["middle_fraction"],
                    }
                )

    write_tsv(OUT / "gdt607_complete_mappings.tsv", mapping_rows)
    write_tsv(OUT / "gdt607_target_category_grid.tsv", target_rows)
    result_without_mapping = []
    for run in results:
        result_without_mapping.append(
            {key: value for key, value in run.items() if key != "mapping"}
        )
    output = {
        "schema": "gdt607-boundary-word-disentanglement-v1",
        "unit_sequences_sha256": DATA_SHA256,
        "reference_sources": reference_hashes,
        "configs": CONFIGS,
        "seeds": list(SEEDS),
        "iterations": args.iterations,
        "runs": len(results),
        "summaries": summaries,
        "target_structure": {unit: structure["held"][unit] for unit in TARGETS},
        "run_metrics": result_without_mapping,
        "artifacts": {
            name: G606.sha(OUT / name)
            for name in (
                "gdt607_complete_mappings.tsv",
                "gdt607_target_category_grid.tsv",
                "gdt607_unit_structural_features.tsv",
            )
        },
        "claim_ceiling": (
            "Exploratory separation of boundary-only and whole-word output roles; "
            "no category or generated output is a word, sound or meaning."
        ),
    }
    result_path = OUT / "gdt607_result.json"
    result_path.write_text(json.dumps(output, indent=2, sort_keys=True) + "\n")
    print(json.dumps({
        "runs": len(results),
        "targets": target_rows,
        "sha256": G606.sha(result_path),
    }, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
