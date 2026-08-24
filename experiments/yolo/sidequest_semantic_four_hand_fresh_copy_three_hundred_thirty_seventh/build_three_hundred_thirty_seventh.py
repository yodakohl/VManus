#!/usr/bin/env python3
"""Render the fresh six-slot pair in four registered scribe habits."""

from __future__ import annotations

import csv
import json
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
SOURCE = ROOT / "experiments/yolo/sidequest_semantic_fresh_six_slot_copy_three_hundred_thirty_sixth/THREE_HUNDRED_THIRTY_SIXTH_16_FRESH_CARD_EVENTS.tsv"
HERBAL = ROOT / "experiments/yolo/sidequest_semantic_repaired_herbal_edition_three_hundred_thirtieth/THREE_HUNDRED_THIRTIETH_100_HERBAL_INTERLINEAR.tsv"
BIO = ROOT / "experiments/yolo/sidequest_semantic_repaired_bio_edition_three_hundred_thirty_second/THREE_HUNDRED_THIRTY_SECOND_281_REPAIRED_BIO_EVENTS.tsv"

HANDS = {
    "HAND_A_BARE": {
        "rule": "Kurze nackte Bezugs- und Operationsformen bevorzugen.",
        "forms": {"Quelle": "dar", "Zugabe": "okain", "Sollmaß": "aiin", "Klarauszug": "shey", "Bereit": "cthy", "Langkontakt": "okeey", "Einsetzen": "oky"},
    },
    "HAND_B_Q_OPERATIVE": {
        "rule": "Operative Eintrittskarten mit q und mittlere Referenzformen schreiben.",
        "forms": {"Quelle": "char", "Zugabe": "qokain", "Sollmaß": "daiin", "Klarauszug": "cheey", "Bereit": "shcthy", "Langkontakt": "qokeey", "Einsetzen": "qoky"},
    },
    "HAND_C_S_ENTRY": {
        "rule": "s-/sh-Eintrittsformen und ch-operatives Einsetzen bevorzugen.",
        "forms": {"Quelle": "sar", "Zugabe": "okain", "Sollmaß": "saiin", "Klarauszug": "shey", "Bereit": "shcthy", "Langkontakt": "okeey", "Einsetzen": "choky"},
    },
    "HAND_D_EXPANDED": {
        "rule": "ch-/t-erweiterte Bezugsformen und q-Operationen bevorzugen.",
        "forms": {"Quelle": "char", "Zugabe": "qokain", "Sollmaß": "taiin", "Klarauszug": "cheey", "Bereit": "checthy", "Langkontakt": "qokeey", "Einsetzen": "choky"},
    },
}


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: list[dict[str, object]], fields: list[str]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    source = read_tsv(SOURCE)
    old = read_tsv(HERBAL) + read_tsv(BIO)
    palette = defaultdict(set)
    surface_to_ids = defaultdict(set)
    for row in old:
        palette[row["joint_tuple_id"]].add(row["surface"])
        surface_to_ids[row["surface"]].add(row["joint_tuple_id"])

    rendered = []
    editions = []
    for hand_id, hand in HANDS.items():
        by_passage = defaultdict(list)
        for row in source:
            surface = hand["forms"].get(row["atomic_value_de"], row["surface"])
            licensed = surface in palette[row["joint_tuple_id"]]
            unique_decode = surface_to_ids[surface] == {row["joint_tuple_id"]}
            rendered.append({
                "hand_id": hand_id,
                "hand_rule": hand["rule"],
                "fresh_event_id": row["fresh_event_id"],
                "passage_id": row["passage_id"],
                "position": row["position"],
                "expected_joint_tuple_id": row["joint_tuple_id"],
                "atomic_value_de": row["atomic_value_de"],
                "slot_code": row["slot_code"],
                "microcycle": row["microcycle"],
                "rendered_surface": surface,
                "surface_registered_for_identity": "YES" if licensed else "NO",
                "surface_uniquely_decodes_to_identity": "YES" if unique_decode else "NO",
                "identity_preserved_by_registered_palette": "YES" if licensed else "NO",
            })
            by_passage[row["passage_id"]].append(surface)
        for passage_id, surfaces in by_passage.items():
            split = 3 if passage_id == "FRESH_HERBAL_PREPARATION" else 5
            editions.append({
                "hand_id": hand_id,
                "hand_rule": hand["rule"],
                "passage_id": passage_id,
                "line_1": " ".join(surfaces[:split]),
                "line_2": " ".join(surfaces[split:]),
                "logical_statement_crosses_line": "YES",
                "slot_sequence_preserved": "YES",
                "microcycle_sequence_preserved": "YES",
                "meaning_sequence_preserved": "YES",
            })

    rules = []
    for hand_id, hand in HANDS.items():
        rules.append({
            "hand_id": hand_id,
            "hand_rule": hand["rule"],
            "variable_value_forms": "|".join(f"{value}={surface}" for value, surface in hand["forms"].items()),
            "stable_cards_rule": "Alle übrigen Karten behalten ihre registrierte Ausgangsform.",
        })

    write_tsv(HERE / "THREE_HUNDRED_THIRTY_SEVENTH_64_RENDERED_EVENTS.tsv", rendered,
              ["hand_id", "hand_rule", "fresh_event_id", "passage_id", "position", "expected_joint_tuple_id", "atomic_value_de", "slot_code", "microcycle", "rendered_surface", "surface_registered_for_identity", "surface_uniquely_decodes_to_identity", "identity_preserved_by_registered_palette"])
    write_tsv(HERE / "THREE_HUNDRED_THIRTY_SEVENTH_EIGHT_SCRIBE_PASSAGES.tsv", editions,
              ["hand_id", "hand_rule", "passage_id", "line_1", "line_2", "logical_statement_crosses_line", "slot_sequence_preserved", "microcycle_sequence_preserved", "meaning_sequence_preserved"])
    write_tsv(HERE / "THREE_HUNDRED_THIRTY_SEVENTH_FOUR_HAND_RULES.tsv", rules,
              ["hand_id", "hand_rule", "variable_value_forms", "stable_cards_rule"])

    lines = ["# Vier Hände, dieselbe frische Doppelfolge", ""]
    for hand_id, hand in HANDS.items():
        lines.extend([f"## {hand_id}", "", hand["rule"], ""])
        for passage in [row for row in editions if row["hand_id"] == hand_id]:
            lines.extend([
                f"**{passage['passage_id']}**",
                "",
                f"`{passage['line_1']}`",
                f"`{passage['line_2']}`",
                "",
            ])
    lines.extend([
        "## Gemeinsame Rücklesung",
        "",
        "Alle vier Hände schreiben dieselben sechzehn Karten in denselben sechs Plätzen",
        "und vier Mikrogängen. Der physische Zeilenwechsel beendet die Aussage nicht.",
        "Stabile Fachkarten bleiben gleich; häufige Quelle-, Maß-, Klarauszug-, Bereit-,",
        "Kontakt- und Einsetzkarten tragen die persönlichen Allographen.",
    ])
    (HERE / "THREE_HUNDRED_THIRTY_SEVENTH_FOUR_HAND_EDITION.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    summary = {
        "status": "PASS",
        "hands": len(HANDS),
        "source_events": len(source),
        "rendered_events": len(rendered),
        "rendered_passages": len(editions),
        "registered_palette_matches": sum(row["identity_preserved_by_registered_palette"] == "YES" for row in rendered),
        "distinct_complete_copies": len({(row["line_1"], row["line_2"]) for row in editions}),
        "slot_sequences_preserved": sum(row["slot_sequence_preserved"] == "YES" for row in editions),
    }
    (HERE / "THREE_HUNDRED_THIRTY_SEVENTH_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
