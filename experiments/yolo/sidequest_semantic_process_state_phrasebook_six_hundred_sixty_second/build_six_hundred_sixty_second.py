#!/usr/bin/env python3
"""Consolidate 11 exact process/state transitions into six teaching phrases."""

from __future__ import annotations

import csv
import json
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
P661 = ROOT / "experiments/yolo/sidequest_semantic_process_state_axis_six_hundred_sixty_first"


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: list[dict[str, object]], fields: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, delimiter="\t", fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


ASSIGNMENTS = {
    "H3-S004": ("P01_SET_TO_READY", "Weiter ansetzen, bis der Posten bereit ist."),
    "B2-S005": ("P01_SET_TO_READY", "Nach Sollmass ansetzen; den Arbeitsgang kurz bis bereit fuehren und fortsetzen."),
    "B2-S008": ("P02_SET_TO_SETTLE_CLOSE", "Aus dem Vorrat ansetzen, absetzen lassen und abschliessen."),
    "B2-S012": ("P03_READY_TO_GRADED_SET", "Den Posten kurz bereit halten und danach laenger ansetzen."),
    "B3-S011": ("P04_READY_TRANSFER_TO_SET", "Kurz halten bis bereit, den Posten umsetzen und neu ansetzen."),
    "B3-S013": ("P03_READY_TO_GRADED_SET", "Den Posten kurz bereit halten, kurz ansetzen und abschliessen."),
    "B3-S021#1": ("P01_SET_TO_READY", "Nach Sollmass ansetzen, bis der Posten bereit ist."),
    "B3-S021#2": ("P05_READY_TO_TRANSFER_CLOSE", "Den bereiten Posten an der Zielstelle umsetzen und abschliessen."),
    "B3-S026": ("P01_SET_TO_READY", "Eine Portion ansetzen, bis der Posten bereit ist."),
    "B4-S011": ("P06_WARM_TO_CONTINUED_SET", "Den Posten kurz waermen und danach laenger fortsetzen."),
    "B4-S013": ("P02_SET_TO_SETTLE_CLOSE", "Weiter ansetzen, absetzen lassen und abschliessen."),
}

PHRASES = {
    "P01_SET_TO_READY": ("ANSETZEN BIS BEREIT", "gesetzte Menge, Quelle oder Fortsetzung in Bereitschaft fuehren"),
    "P02_SET_TO_SETTLE_CLOSE": ("ANSETZEN, ABSETZEN, SCHLIESSEN", "gesetzten Posten absetzen lassen und beenden"),
    "P03_READY_TO_GRADED_SET": ("BEREIT, DANN GRADUIERT ANSETZEN", "bereiten Posten kurz oder lang neu ansetzen"),
    "P04_READY_TRANSFER_TO_SET": ("BEREIT UMSETZEN UND NEU ANSETZEN", "Bereitschaft in Transfer und Neukonfiguration uebergeben"),
    "P05_READY_TO_TRANSFER_CLOSE": ("BEREIT UMSETZEN UND SCHLIESSEN", "bereiten Posten an Zielstelle umsetzen und beenden"),
    "P06_WARM_TO_CONTINUED_SET": ("WAERMEN UND LAENGER FORTSETZEN", "kurze Waerme in lange Fortsetzung uebergeben"),
}


def main() -> None:
    HERE.mkdir(parents=True, exist_ok=True)
    transitions = read_tsv(P661 / "SIX_HUNDRED_SIXTY_FIRST_11_IMMEDIATE_TRANSITIONS.tsv")
    seen: Counter[str] = Counter()
    rows = []
    for transition in transitions:
        sid = transition["statement_id"]
        seen[sid] += 1
        key = f"{sid}#{seen[sid]}" if sum(row["statement_id"] == sid for row in transitions) > 1 else sid
        phrase_id, fluent = ASSIGNMENTS[key]
        rows.append({
            "statement_id": sid,
            "page": transition["page"],
            "phrase_id": phrase_id,
            "direction": transition["direction"],
            "source_surface": f"{transition['left_surface']} {transition['right_surface']}",
            "left_reading_de": transition["left_reading_de"],
            "right_reading_de": transition["right_reading_de"],
            "fluent_phrase_de": fluent,
            "source_cards_retained": "YES",
        })

    phrase_rows = []
    for phrase_id, (short, rule) in PHRASES.items():
        members = [row for row in rows if row["phrase_id"] == phrase_id]
        phrase_rows.append({
            "phrase_id": phrase_id,
            "short_reading_de": short,
            "teaching_rule_de": rule,
            "instances": len(members),
            "statement_ids": "|".join(row["statement_id"] for row in members),
            "source_surfaces": " || ".join(row["source_surface"] for row in members),
        })

    write_tsv(HERE / "SIX_HUNDRED_SIXTY_SECOND_11_FLUENT_TRANSITIONS.tsv", rows, list(rows[0]))
    write_tsv(HERE / "SIX_HUNDRED_SIXTY_SECOND_6_TEACHING_PHRASES.tsv", phrase_rows, list(phrase_rows[0]))

    md = [
        "# Kleines Prozess-Zustands-Phrasenbuch",
        "",
        "Sechs Lehrphrasen fassen elf direkt benachbarte Quellpaare zusammen.",
        "",
    ]
    for phrase in phrase_rows:
        md.extend([
            f"## {phrase['phrase_id']} — {phrase['short_reading_de']}",
            "",
            f"Regel: {phrase['teaching_rule_de']}.",
            "",
        ])
        for row in rows:
            if row["phrase_id"] == phrase["phrase_id"]:
                md.append(f"- `{row['source_surface']}` — {row['fluent_phrase_de']}")
        md.append("")
    (HERE / "SIX_HUNDRED_SIXTY_SECOND_PHRASEBOOK.md").write_text("\n".join(md).rstrip() + "\n", encoding="utf-8")

    summary = {
        "status": "PASS",
        "source_transitions": len(rows),
        "teaching_phrases": len(phrase_rows),
        "set_to_ready": sum(row["phrase_id"] == "P01_SET_TO_READY" for row in rows),
        "set_to_settle_close": sum(row["phrase_id"] == "P02_SET_TO_SETTLE_CLOSE" for row in rows),
        "ready_to_graded_set": sum(row["phrase_id"] == "P03_READY_TO_GRADED_SET" for row in rows),
        "other_singleton_phrases": sum(int(row["instances"]) == 1 for row in phrase_rows),
        "decision": "SIX_SHORT_PHRASES_READ_ALL_ELEVEN_DIRECT_PROCESS_STATE_TRANSITIONS",
    }
    (HERE / "SIX_HUNDRED_SIXTY_SECOND_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
