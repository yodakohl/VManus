#!/usr/bin/env python3
"""Distinguish stable plaintext carriers from carrier-switching LM words."""
from __future__ import annotations

import csv
import hashlib
import json
import math
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent / "artifacts"
PRIMARY = "primary_42L_4D_34S_7N_11W"
PRIMARY_SEEDS = (11, 29, 47, 71, 89, 107)
LANGUAGES = ("latin", "middle_high_german", "old_italian")


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_tsv(path):
    with path.open(newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path, rows, fields):
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def decode_with_carriers(sequence, mapping):
    words = []
    buffer = []
    carriers = []
    for unit in sequence:
        category, output = mapping[unit]
        if category == "W":
            if buffer:
                words.append(("".join(buffer), tuple(carriers)))
                buffer, carriers = [], []
            words.append((output, (unit,)))
        elif category != "N":
            buffer.append(output)
            carriers.append(unit)
    if buffer:
        words.append(("".join(buffer), tuple(carriers)))
    return words


def main():
    sequences = json.loads((HERE / "unit_sequences.json").read_text())
    held = sequences["sequences"]["held"]
    rows = read_tsv(HERE / "complete_mappings.tsv")
    mapping = defaultdict(dict)
    real_runs = defaultdict(list)
    for row in rows:
        if row["model_kind"] != "real":
            continue
        key = (row["language"], row["config"], int(row["seed"]))
        mapping[key][row["unit"]] = (row["category"], row["output"])
        if key not in real_runs[row["language"]]:
            real_runs[row["language"]].append(key)

    positional = read_tsv(HERE / "stable_held_words.tsv")
    audit_rows = []
    carrier_stable_words = []
    carrier_stable_fragments = []
    category_summary = {}
    for language in LANGUAGES:
        primary_keys = [(language, PRIMARY, seed) for seed in PRIMARY_SEEDS]
        all_keys = sorted(real_runs[language], key=lambda key: (key[1], key[2]))
        decoded = [
            [decode_with_carriers(record["units"], mapping[key]) for record in held]
            for key in primary_keys
        ]
        location_index = {
            (record["locus"], int(record["chunk_index"])): index
            for index, record in enumerate(held)
        }
        for row in [value for value in positional if value["language"] == language]:
            index = location_index[(row["locus"], int(row["chunk_index"]))]
            word = row["word"]
            carriers = Counter()
            for run in decoded:
                for text, carrier in run[index]:
                    if text == word:
                        carriers[carrier] += 1
                        break
            modal, support = carriers.most_common(1)[0]
            record = {
                **row,
                "modal_carrier_units": " ".join(modal),
                "modal_carrier_support": support,
                "modal_carrier_fraction": support / len(primary_keys),
                "carrier_stable_at_75pct": int(support >= math.ceil(0.75 * len(primary_keys))),
                "all_carrier_counts": ";".join(
                    f"{' '.join(carrier)}={count}" for carrier, count in carriers.most_common()
                ),
            }
            audit_rows.append(record)
            if record["carrier_stable_at_75pct"]:
                carrier_stable_words.append(record)

        # Search fragments while retaining the exact source-unit span that
        # emitted the containing decoded word.
        threshold = math.ceil(0.75 * len(primary_keys))
        for index, record in enumerate(held):
            support = Counter()
            for run in decoded:
                seen = set()
                for text, carrier in run[index]:
                    for size in range(4, min(12, len(text)) + 1):
                        for start in range(len(text) - size + 1):
                            seen.add((text[start:start + size], carrier))
                support.update(seen)
            viable = [
                (len(fragment), count, fragment, carrier)
                for (fragment, carrier), count in support.items()
                if count >= threshold
            ]
            if not viable:
                continue
            best = max(value[0] for value in viable)
            for length, count, fragment, carrier in sorted(
                viable, key=lambda value: (-value[0], -value[1], value[2], value[3])
            ):
                if length != best:
                    continue
                carrier_stable_fragments.append({
                    "language": language,
                    "page": record["page"],
                    "physical_folio": record["physical_folio"],
                    "locus": record["locus"],
                    "chunk_index": record["chunk_index"],
                    "fragment": fragment,
                    "length": length,
                    "carrier_units": " ".join(carrier),
                    "run_support": count,
                    "run_fraction": count / len(primary_keys),
                })

        units = sequences["inventory"]
        primary_category_counts = Counter()
        all_config_category_counts = Counter()
        primary_exact_counts = Counter()
        all_config_exact_counts = Counter()
        stable_primary_by_category = Counter()
        stable_all_by_category = Counter()
        cross_rows = []
        for unit in units:
            primary_values = [mapping[key][unit] for key in primary_keys]
            all_values = [mapping[key][unit] for key in all_keys]
            pcat, pcat_n = Counter(value[0] for value in primary_values).most_common(1)[0]
            acat, acat_n = Counter(value[0] for value in all_values).most_common(1)[0]
            pexact, pexact_n = Counter(primary_values).most_common(1)[0]
            aexact, aexact_n = Counter(all_values).most_common(1)[0]
            primary_category_counts[pcat_n / len(primary_values)] += 1
            all_config_category_counts[acat_n / len(all_values)] += 1
            primary_exact_counts[pexact_n / len(primary_values)] += 1
            all_config_exact_counts[aexact_n / len(all_values)] += 1
            if pcat_n == len(primary_values):
                stable_primary_by_category[pcat] += 1
            if acat_n == len(all_values):
                stable_all_by_category[acat] += 1
            cross_rows.append({
                "language": language, "unit": unit,
                "primary_modal_category": pcat,
                "primary_category_fraction": pcat_n / len(primary_values),
                "primary_modal_output": pexact[1],
                "primary_exact_fraction": pexact_n / len(primary_values),
                "all_configs_modal_category": acat,
                "all_configs_category_fraction": acat_n / len(all_values),
                "all_configs_modal_output": aexact[1],
                "all_configs_exact_fraction": aexact_n / len(all_values),
            })
        category_summary[language] = {
            "primary_stable_categories": dict(stable_primary_by_category),
            "all_config_stable_categories": dict(stable_all_by_category),
            "primary_category_all_start_units": sum(stable_primary_by_category.values()),
            "all_config_category_all_start_units": sum(stable_all_by_category.values()),
            "primary_exact_all_start_units": sum(
                count for fraction, count in primary_exact_counts.items() if fraction == 1.0
            ),
            "all_config_exact_all_start_units": sum(
                count for fraction, count in all_config_exact_counts.items() if fraction == 1.0
            ),
        }
        write_tsv(
            HERE / f"category_stability_all_configs_{language}.tsv",
            cross_rows, list(cross_rows[0]),
        )

    audit_fields = list(audit_rows[0]) if audit_rows else [
        "language", "page", "physical_folio", "locus", "chunk_index", "word",
    ]
    write_tsv(HERE / "positional_word_carrier_audit.tsv", audit_rows, audit_fields)
    write_tsv(
        HERE / "carrier_stable_words.tsv", carrier_stable_words, audit_fields
    )
    fragment_fields = list(carrier_stable_fragments[0]) if carrier_stable_fragments else [
        "language", "page", "physical_folio", "locus", "chunk_index", "fragment",
        "length", "carrier_units", "run_support", "run_fraction",
    ]
    write_tsv(
        HERE / "carrier_stable_fragments.tsv", carrier_stable_fragments, fragment_fields
    )
    result = {
        "schema": "gdt606-mixed-codebook-carrier-stability-v1",
        "complete_mappings_sha256": sha(HERE / "complete_mappings.tsv"),
        "positional_consensus_words": len(audit_rows),
        "carrier_stable_words_at_75pct": len(carrier_stable_words),
        "carrier_stable_word_folios": len({
            (row["language"], row["physical_folio"]) for row in carrier_stable_words
        }),
        "carrier_stable_fragments_at_75pct": len(carrier_stable_fragments),
        "carrier_stable_fragment_folios": len({
            (row["language"], row["physical_folio"]) for row in carrier_stable_fragments
        }),
        "category_summary": category_summary,
        "artifacts": {
            name: sha(HERE / name) for name in (
                "positional_word_carrier_audit.tsv", "carrier_stable_words.tsv",
                "carrier_stable_fragments.tsv",
                "category_stability_all_configs_latin.tsv",
                "category_stability_all_configs_middle_high_german.tsv",
                "category_stability_all_configs_old_italian.tsv",
            )
        },
        "decision": (
            "NO_STABLE_PLAINTEXT_CARRIER"
            if not carrier_stable_words and not carrier_stable_fragments
            else "CARRIER_STABLE_FRAGMENT_REQUIRES_FURTHER_GATES"
        ),
    }
    path = HERE / "carrier_stability_result.json"
    path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps({**result, "sha256": sha(path)}, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
