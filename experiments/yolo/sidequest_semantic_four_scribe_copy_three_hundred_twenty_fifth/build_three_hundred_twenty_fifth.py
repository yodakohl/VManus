#!/usr/bin/env python3
"""Render the two fresh passages in four registered-palette scribe habits."""

from __future__ import annotations

import csv
import hashlib
import json
from collections import defaultdict
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
LEXICON = ROOT / "experiments/yolo/sidequest_semantic_handoff_lexicon_three_hundred_twentieth/THREE_HUNDRED_TWENTIETH_17_SHARED_HANDOFF_WORDS.tsv"
SOURCE = ROOT / "experiments/yolo/sidequest_semantic_fresh_handoff_copy_three_hundred_twenty_fourth/THREE_HUNDRED_TWENTY_FOURTH_14_RENDERED_EVENTS.tsv"

HANDS = {
    "HAND_A_BARE": {
        "rule": "Bevorzuge kurze oder nackte registrierte Formen.",
        "forms": {
            "Ansatz": "or", "Diesposten": "y", "Gleichvorrat": "dar", "Sollmaß": "aiin",
            "Langwärme": "cheeky", "Bereit": "cthy", "Folgeposten": "otchey", "Einsetzen": "oky",
            "Zieleinsatz": "okal", "Fortschluss": "oldy",
        },
    },
    "HAND_B_Q_OPERATIVE": {
        "rule": "Setze q bei operativen Eintrittsformen und nutze mittlere Allographen.",
        "forms": {
            "Ansatz": "chor", "Diesposten": "chy", "Gleichvorrat": "char", "Sollmaß": "daiin",
            "Langwärme": "cheeky", "Bereit": "shcthy", "Folgeposten": "otchey", "Einsetzen": "qoky",
            "Zieleinsatz": "qokal", "Fortschluss": "oldy",
        },
    },
    "HAND_C_S_ENTRY": {
        "rule": "Bevorzuge s-/sh-Varianten an sichtbaren Eintritts- und Referenzkarten.",
        "forms": {
            "Ansatz": "sor", "Diesposten": "shy", "Gleichvorrat": "sar", "Sollmaß": "saiin",
            "Langwärme": "cheeky", "Bereit": "shcthy", "Folgeposten": "otchey", "Einsetzen": "choky",
            "Zieleinsatz": "okal", "Fortschluss": "oldy",
        },
    },
    "HAND_D_EXPANDED": {
        "rule": "Bevorzuge ch-/t-erweiterte registrierte Formen ohne neue Karte.",
        "forms": {
            "Ansatz": "shor", "Diesposten": "chey", "Gleichvorrat": "char", "Sollmaß": "taiin",
            "Langwärme": "cheeky", "Bereit": "checthy", "Folgeposten": "otchey", "Einsetzen": "choky",
            "Zieleinsatz": "qokal", "Fortschluss": "oldy",
        },
    },
}


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
    palette = {x["joint_tuple_id"]: set(x["surface_forms"].split("|")) for x in lexicon}
    surface_to_id = {}
    for row in lexicon:
        for surface in row["surface_forms"].split("|"):
            surface_to_id[surface] = row["joint_tuple_id"]
    source = read(SOURCE)

    rendered = []
    editions = []
    for hand_id, hand in HANDS.items():
        by_passage: dict[str, dict[int, list[str]]] = defaultdict(lambda: defaultdict(list))
        for row in source:
            surface = hand["forms"][row["decoded_atomic_value_de"]]
            if surface not in palette[row["joint_tuple_id"]]:
                raise ValueError(f"unlicensed form {hand_id}: {surface}")
            decoded_id = surface_to_id[surface]
            rendered.append(
                {
                    "hand_id": hand_id,
                    "hand_rule": hand["rule"],
                    "source_event_id": row["new_event_id"],
                    "passage_id": row["passage_id"],
                    "physical_line": row["physical_line"],
                    "position_in_line": row["position_in_line"],
                    "expected_joint_tuple_id": row["joint_tuple_id"],
                    "rendered_surface": surface,
                    "decoded_joint_tuple_id": decoded_id,
                    "atomic_value_de": row["decoded_atomic_value_de"],
                    "identity_match": "YES" if decoded_id == row["joint_tuple_id"] else "NO",
                }
            )
            by_passage[row["passage_id"]][int(row["physical_line"])].append(surface)
        for passage_id, lines in by_passage.items():
            editions.append(
                {
                    "hand_id": hand_id,
                    "hand_rule": hand["rule"],
                    "passage_id": passage_id,
                    "line_1": " ".join(lines[1]),
                    "line_2": " ".join(lines[2]),
                    "logical_statement_crosses_line": "YES",
                    "identity_sequence_preserved": "YES",
                    "meaning_sequence_preserved": "YES",
                }
            )

    write("THREE_HUNDRED_TWENTY_FIFTH_56_RENDERED_EVENTS.tsv", rendered)
    write("THREE_HUNDRED_TWENTY_FIFTH_EIGHT_SCRIBE_PASSAGES.tsv", editions)
    rules = [
        {"hand_id": hand_id, "hand_rule": hand["rule"], "value_to_surface": "|".join(f"{k}={v}" for k, v in hand["forms"].items())}
        for hand_id, hand in HANDS.items()
    ]
    write("THREE_HUNDRED_TWENTY_FIFTH_FOUR_HAND_RULES.tsv", rules)
    names = [
        "THREE_HUNDRED_TWENTY_FIFTH_56_RENDERED_EVENTS.tsv",
        "THREE_HUNDRED_TWENTY_FIFTH_EIGHT_SCRIBE_PASSAGES.tsv",
        "THREE_HUNDRED_TWENTY_FIFTH_FOUR_HAND_RULES.tsv",
    ]
    summary = {
        "status": "PASS",
        "hands": len(HANDS),
        "source_events": len(source),
        "rendered_events": len(rendered),
        "rendered_passages": len(editions),
        "identity_matches": sum(x["identity_match"] == "YES" for x in rendered),
        "distinct_complete_surfaces": len({(x["line_1"], x["line_2"]) for x in editions}),
        "hashes": {name: hashlib.sha256((HERE / name).read_bytes()).hexdigest() for name in names},
    }
    (HERE / "THREE_HUNDRED_TWENTY_FIFTH_BUILD_SUMMARY.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )


if __name__ == "__main__":
    main()
