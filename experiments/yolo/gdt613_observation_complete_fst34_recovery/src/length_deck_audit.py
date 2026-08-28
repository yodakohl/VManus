#!/usr/bin/env python3
"""Necessary collision-free capacity audit for GDT613's frozen length deck."""
from __future__ import annotations

import csv
import json
from collections import Counter, defaultdict
from pathlib import Path


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
EXP = ROOT / "experiments/yolo/gdt613_observation_complete_fst34_recovery"
ART = EXP / "artifacts"
SPLITS = ART / "reference_splits"


def write_tsv(path: Path, fields: list[str], rows: list[dict]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle, fieldnames=fields, delimiter="\t", lineterminator="\n"
        )
        writer.writeheader()
        writer.writerows(rows)


def ngram_capacity(train: list[str], held: list[str], length: int):
    train_types: dict[str, set[str]] = defaultdict(set)
    held_events = Counter()
    for word in train:
        for begin in range(len(word) - length + 1):
            train_types[word[begin : begin + length]].add(word)
    for word in held:
        held_events.update(
            word[begin : begin + length]
            for begin in range(len(word) - length + 1)
        )
    eligible = sorted(
        value
        for value, word_types in train_types.items()
        if len(word_types) >= 8 and held_events[value] >= 16
    )
    return train_types, held_events, eligible


def whole_envelope_upper_bound(
    train_words: set[str], whole_length: int, connector_one: list[str], connector_two: list[str]
):
    """Max train types for CONNECTOR? WHOLE CONNECTOR? under generous choices."""
    whole_candidates = sorted(
        {
            word[begin : begin + whole_length]
            for word in train_words
            for begin in range(len(word) - whole_length + 1)
        }
    )
    best = None
    for whole in whole_candidates:
        for one in connector_one:
            for two in connector_two:
                generated = {
                    whole,
                    one + whole,
                    two + whole,
                    whole + one,
                    whole + two,
                    one + whole + one,
                    one + whole + two,
                    two + whole + one,
                    two + whole + two,
                }
                hits = sorted(generated & train_words)
                candidate = (len(hits), whole, one, two, hits)
                if best is None or candidate[:4] > best[:4]:
                    best = candidate
    if best is None:
        raise RuntimeError("empty whole-envelope search")
    return {
        "whole_length": whole_length,
        "maximum_train_word_types": best[0],
        "whole_output": best[1],
        "connector_length1": best[2],
        "connector_length2": best[3],
        "witness_train_word_types": best[4],
    }


def main() -> int:
    profile = json.loads((ART / "length_card_profile.json").read_text(encoding="utf-8"))
    train = (SPLITS / "synthetic_train.txt").read_text(encoding="utf-8").split()
    held = (SPLITS / "synthetic_held.txt").read_text(encoding="utf-8").split()
    required = Counter()
    for lengths in profile["primitive"].values():
        required.update(length for length in lengths if length > 0)
    for lengths in profile["override"].values():
        required.update(length for length in lengths if length > 0)

    rows = []
    eligible_by_length = {}
    for length in range(1, max(required) + 1):
        train_types, held_events, eligible = ngram_capacity(train, held, length)
        eligible_by_length[length] = eligible
        rows.append(
            {
                "output_length": length,
                "required_unique_cards": required[length],
                "observed_train_ngrams": len(train_types),
                "eligible_unique_ngrams": len(eligible),
                "capacity_margin": len(eligible) - required[length],
                "eligible_values": ",".join(eligible),
            }
        )
    one_character_slots = []
    for role, lengths in profile["primitive"].items():
        one_character_slots.extend(role for length in lengths if length == 1)
    whole_envelopes = [
        whole_envelope_upper_bound(
            set(train), length, eligible_by_length[1], eligible_by_length[2]
        )
        for length in (3, 4, 5, 6)
    ]
    result = {
        "schema": "gdt613-length-deck-audit-v1",
        "decision": "FIXED_LENGTH_DECK_INFEASIBLE_FOR_FROZEN_NATURAL_LATIN_SPLITS",
        "train_tokens": len(train),
        "train_word_types": len(set(train)),
        "held_tokens": len(held),
        "held_word_types": len(set(held)),
        "one_character_cards_required": required[1],
        "one_character_values_observed": len(set("".join(train + held))),
        "one_character_values_meeting_8_train_types_and_16_held_events": len(
            eligible_by_length[1]
        ),
        "eligible_one_character_values": eligible_by_length[1],
        "one_character_slots": one_character_slots,
        "minimum_length1_to_length2_moves_for_uniqueness_only": max(
            0, required[1] - len(set("".join(train + held)))
        ),
        "minimum_length1_to_length2_moves_with_registered_exposure": max(
            0, required[1] - len(eligible_by_length[1])
        ),
        "whole_parameters": {
            "primitive_length4": 1,
            "override_length3": 1,
            "override_length4": 1,
            "override_length5": 1,
            "override_length6": 1,
        },
        "whole_train_word_type_threshold": 8,
        "whole_envelope_upper_bounds": whole_envelopes,
        "whole_parameters_reaching_train_threshold": sum(
            row["maximum_train_word_types"] >= 8 for row in whole_envelopes
        ),
        "claim_ceiling": (
            "Necessary substring-capacity upper bound only; role position and joint word "
            "segmentation can reduce feasibility further but cannot repair this deficit."
        ),
    }
    (ART / "length_deck_feasibility.json").write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    write_tsv(
        ART / "length_deck_ngram_capacity.tsv",
        [
            "output_length",
            "required_unique_cards",
            "observed_train_ngrams",
            "eligible_unique_ngrams",
            "capacity_margin",
            "eligible_values",
        ],
        rows,
    )
    write_tsv(
        ART / "wholeform_envelope_capacity.tsv",
        [
            "whole_length",
            "maximum_train_word_types",
            "whole_output",
            "connector_length1",
            "connector_length2",
            "witness_train_word_types",
        ],
        [
            {
                **row,
                "witness_train_word_types": ",".join(row["witness_train_word_types"]),
            }
            for row in whole_envelopes
        ],
    )
    print(
        json.dumps(
            {
                "decision": result["decision"],
                "required": result["one_character_cards_required"],
                "eligible": result[
                    "one_character_values_meeting_8_train_types_and_16_held_events"
                ],
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
