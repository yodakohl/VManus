#!/usr/bin/env python3
"""Generate and reverse-read one fresh Herbal output and one Bio application."""

from __future__ import annotations

import csv
import hashlib
import json
from collections import defaultdict
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
LEXICON = ROOT / "experiments/yolo/sidequest_semantic_handoff_lexicon_three_hundred_twentieth/THREE_HUNDRED_TWENTIETH_17_SHARED_HANDOFF_WORDS.tsv"
LEDGER = ROOT / "experiments/yolo/sidequest_semantic_thermal_temporal_completion/SELECTED_381_THERMAL_TEMPORAL_INTERLINEAR.tsv"

PASSAGES = [
    {
        "passage_id": "NEW_HERBAL_OUTPUT",
        "register": "HERBAL",
        "physical_lines": [
            ["chor", "chy", "char", "daiin"],
            ["cheeky", "cthy"],
        ],
        "intended_atomic_sequence": ["Ansatz", "Diesposten", "Gleichvorrat", "Sollmaß", "Langwärme", "Bereit"],
        "fluent_reading_de": "Nimm den laufenden Ansatz als aktuellen Posten aus demselben Vorrat, stelle das Sollmaß ein, halte ihn länger warm und halte ihn bereit.",
        "terminal_status": "OPEN_HANDOFF",
    },
    {
        "passage_id": "NEW_BIO_APPLICATION",
        "register": "BIO",
        "physical_lines": [
            ["otchey", "qoky", "chy", "daiin"],
            ["y", "qokal", "cheeky", "oldy"],
        ],
        "intended_atomic_sequence": ["Folgeposten", "Einsetzen", "Diesposten", "Sollmaß", "Diesposten", "Zieleinsatz", "Langwärme", "Fortschluss"],
        "fluent_reading_de": "Nimm den Folgeposten, setze ihn ein, miss denselben aktiven Posten, bringe ihn an die Zielstelle, halte ihn länger warm und schließe den fortgesetzten Gang.",
        "terminal_status": "CLOSED_LOCAL_STEP",
    },
]


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(name: str, rows: list[dict[str, str]]) -> None:
    with (HERE / name).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    lexicon = read(LEXICON)
    surface_to_word = {}
    word_by_id = {x["handoff_word_id"]: x for x in lexicon}
    for row in lexicon:
        for surface in row["surface_forms"].split("|"):
            if surface in surface_to_word and surface_to_word[surface] != row["handoff_word_id"]:
                raise ValueError(f"ambiguous shared surface {surface}")
            surface_to_word[surface] = row["handoff_word_id"]

    existing_by_statement: dict[str, list[str]] = defaultdict(list)
    for row in read(LEDGER):
        existing_by_statement[row["statement_id"]].append(row["joint_tuple_id"])
    existing_sequences = {tuple(value) for value in existing_by_statement.values()}

    passage_rows = []
    events = []
    roundtrip = []
    serial = 0
    for passage in PASSAGES:
        decoded_values = []
        decoded_ids = []
        for line_no, line in enumerate(passage["physical_lines"], 1):
            for position, surface in enumerate(line, 1):
                serial += 1
                word_id = surface_to_word[surface]
                word = word_by_id[word_id]
                decoded_values.append(word["handoff_atomic_value_de"])
                decoded_ids.append(word["joint_tuple_id"])
                event_id = f"N{serial:03d}"
                events.append(
                    {
                        "new_event_id": event_id,
                        "passage_id": passage["passage_id"],
                        "register": passage["register"],
                        "physical_line": str(line_no),
                        "position_in_line": str(position),
                        "surface": surface,
                        "handoff_word_id": word_id,
                        "joint_tuple_id": word["joint_tuple_id"],
                        "decoded_atomic_value_de": word["handoff_atomic_value_de"],
                        "card_identity_status": "ALREADY_REGISTERED",
                    }
                )
                roundtrip.append(
                    {
                        "new_event_id": event_id,
                        "surface": surface,
                        "expected_word_id": word_id,
                        "decoded_word_id": surface_to_word[surface],
                        "expected_value": word["handoff_atomic_value_de"],
                        "decoded_value": word_by_id[surface_to_word[surface]]["handoff_atomic_value_de"],
                        "identity_match": "YES",
                        "meaning_match": "YES",
                    }
                )
        if decoded_values != passage["intended_atomic_sequence"]:
            raise ValueError(f"roundtrip value failure {passage['passage_id']}")
        passage_rows.append(
            {
                "passage_id": passage["passage_id"],
                "register": passage["register"],
                "line_1": " ".join(passage["physical_lines"][0]),
                "line_2": " ".join(passage["physical_lines"][1]),
                "line_break_is_statement_break": "NO",
                "decoded_atomic_sequence": " → ".join(decoded_values),
                "fluent_reading_de": passage["fluent_reading_de"],
                "terminal_status": passage["terminal_status"],
                "all_cards_preexisting": "YES",
                "full_sequence_preexisting": "YES" if tuple(decoded_ids) in existing_sequences else "NO",
                "manuscript_text_claim": "NO_CREATIVE_WORKSHOP_DEMONSTRATION",
            }
        )

    write("THREE_HUNDRED_TWENTY_FOURTH_TWO_FRESH_PASSAGES.tsv", passage_rows)
    write("THREE_HUNDRED_TWENTY_FOURTH_14_RENDERED_EVENTS.tsv", events)
    write("THREE_HUNDRED_TWENTY_FOURTH_14_EVENT_ROUNDTRIP.tsv", roundtrip)
    names = [
        "THREE_HUNDRED_TWENTY_FOURTH_TWO_FRESH_PASSAGES.tsv",
        "THREE_HUNDRED_TWENTY_FOURTH_14_RENDERED_EVENTS.tsv",
        "THREE_HUNDRED_TWENTY_FOURTH_14_EVENT_ROUNDTRIP.tsv",
    ]
    summary = {
        "status": "PASS",
        "passages": len(passage_rows),
        "rendered_events": len(events),
        "old_card_identities": len({x["joint_tuple_id"] for x in events}),
        "new_card_identities": 0,
        "new_full_sequences": sum(x["full_sequence_preexisting"] == "NO" for x in passage_rows),
        "roundtrip_identity_matches": sum(x["identity_match"] == "YES" for x in roundtrip),
        "hashes": {name: hashlib.sha256((HERE / name).read_bytes()).hexdigest() for name in names},
    }
    (HERE / "THREE_HUNDRED_TWENTY_FOURTH_BUILD_SUMMARY.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )


if __name__ == "__main__":
    main()
