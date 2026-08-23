#!/usr/bin/env python3
from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
ROUNDTRIP = ROOT / "experiments/yolo/sidequest_semantic_apprentice_roundtrip_two_hundred_fifth"
BASE = ROOT / "experiments/yolo/sidequest_semantic_vocabulary_granularity_two_hundred_third"
APPRENTICE = ROOT / "experiments/yolo/sidequest_semantic_apprentice_dictionary_two_hundred_fourth"
TOKENS = ROUNDTRIP / "TWO_HUNDRED_FIFTH_32_TOKEN_ROUNDTRIP.tsv"
FIELDS = ROUNDTRIP / "TWO_HUNDRED_FIFTH_SIX_FIELD_WORKSHOP_TEXT.tsv"
EVENTS = BASE / "TWO_HUNDRED_THIRD_381_EVENT_COMPACT_EDITION.tsv"
INDEX = APPRENTICE / "TWO_HUNDRED_FOURTH_173_CARD_APPRENTICE_INDEX.tsv"


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(path: Path, rows: list[dict[str, object]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    tokens = read(TOKENS)
    fields = read(FIELDS)
    events = read(EVENTS)
    index = {row["master_card_id"]: row for row in read(INDEX)}

    exact_pairs: Counter[tuple[str, str]] = Counter()
    drawer_pairs: Counter[tuple[str, str]] = Counter()
    exact_example: dict[tuple[str, str], str] = {}
    drawer_example: dict[tuple[str, str], str] = {}
    by_statement: dict[str, list[dict[str, str]]] = defaultdict(list)
    for event in events:
        by_statement[event["statement_id"]].append(event)
    for statement_id, rows in by_statement.items():
        for left, right in zip(rows, rows[1:]):
            pair = (left["master_card_id"], right["master_card_id"])
            drawers = (index[pair[0]]["drawer"], index[pair[1]]["drawer"])
            exact_pairs[pair] += 1
            drawer_pairs[drawers] += 1
            exact_example.setdefault(pair, statement_id)
            drawer_example.setdefault(drawers, statement_id)

    pair_rows: list[dict[str, object]] = []
    per_field: dict[str, Counter[str]] = defaultdict(Counter)
    for field_id in dict.fromkeys(row["field_id"] for row in tokens):
        rows = [row for row in tokens if row["field_id"] == field_id]
        for pair_position, (left, right) in enumerate(zip(rows, rows[1:]), 1):
            left_id = left["intended_card_id"]
            right_id = right["intended_card_id"]
            pair = (left_id, right_id)
            drawers = (index[left_id]["drawer"], index[right_id]["drawer"])
            if exact_pairs[pair] > 0:
                support = "DIRECT_EXACT_BIGRAM"
            elif drawer_pairs[drawers] >= 3:
                support = "SUPPORTED_DRAWER_RECOMBINATION"
            else:
                support = "THIN_DRAWER_RECOMBINATION"
            per_field[field_id][support] += 1
            pair_rows.append({
                "field_id": field_id,
                "pair_position": pair_position,
                "left_card_id": left_id,
                "left_value_de": left["intended_value_de"],
                "left_drawer": drawers[0],
                "right_card_id": right_id,
                "right_value_de": right["intended_value_de"],
                "right_drawer": drawers[1],
                "exact_bigram_occurrences": exact_pairs[pair],
                "exact_example_statement": exact_example.get(pair, "NONE"),
                "drawer_bigram_occurrences": drawer_pairs[drawers],
                "drawer_example_statement": drawer_example[drawers],
                "support_class": support,
            })
    write(OUT / "TWO_HUNDRED_SIXTH_26_PAIR_PRESSURE.tsv", pair_rows)

    field_rows: list[dict[str, object]] = []
    field_source = {row["field_id"]: row for row in fields}
    for field_id, counts in per_field.items():
        if counts["THIN_DRAWER_RECOMBINATION"]:
            verdict = "KEEP_AS_CREATIVE_DRAFT__DO_NOT_TREAT_AS_PHRASE_EVIDENCE"
        elif counts["DIRECT_EXACT_BIGRAM"] >= 2:
            verdict = "DIRECT_BACKBONE"
        else:
            verdict = "SUPPORTED_RECOMBINATION"
        field_rows.append({
            "field_id": field_id,
            "field_mode": field_source[field_id]["field_mode"],
            "direct_pairs": counts["DIRECT_EXACT_BIGRAM"],
            "supported_recombinations": counts["SUPPORTED_DRAWER_RECOMBINATION"],
            "thin_recombinations": counts["THIN_DRAWER_RECOMBINATION"],
            "total_pairs": sum(counts.values()),
            "verdict": verdict,
            "source_instruction_de": field_source[field_id]["source_instruction_de"],
        })
    write(OUT / "TWO_HUNDRED_SIXTH_SIX_FIELD_SUPPORT.tsv", field_rows)

    support_counts = Counter(row["support_class"] for row in pair_rows)
    summary = {
        "token_source_sha256": hashlib.sha256(TOKENS.read_bytes()).hexdigest(),
        "event_source_sha256": hashlib.sha256(EVENTS.read_bytes()).hexdigest(),
        "pairs": len(pair_rows),
        "fields": len(field_rows),
        "support_counts": dict(support_counts),
        "drawer_unattested_pairs": sum(int(row["drawer_bigram_occurrences"]) == 0 for row in pair_rows),
        "fields_with_thin_recombination": sum(int(row["thin_recombinations"]) > 0 for row in field_rows),
        "fresh_card_types": 0,
        "sealed_pages_accessed": False,
    }
    (OUT / "BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
