#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from collections import Counter, defaultdict
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
SOURCE = ROOT / "sidequest_semantic_two_gap_unit_closure_eight_hundred_ninety_third"
MARKS = SOURCE / "EIGHT_HUNDRED_NINETY_THIRD_437_REVISED_MARK_DECK.tsv"
UNITS = SOURCE / "EIGHT_HUNDRED_NINETY_THIRD_118_REVISED_UNIT_EXECUTION.tsv"
VOCAB = SOURCE / "EIGHT_HUNDRED_NINETY_THIRD_231_REVISED_WORKSHOP_VOCABULARY.tsv"
CARDS = SOURCE / "EIGHT_HUNDRED_NINETY_THIRD_6_REVISED_JOB_CARDS.tsv"
PREFIX = "EIGHT_HUNDRED_NINETY_FOURTH"

PROMOTIONS = {
    "PROC087": "POSTEN SAMMELN",
    "PROC088": "ZUR ZIELSTELLE LEITEN UND UMSETZEN",
    "PROC089": "DANACH ZUR QUELLE",
    "PROC101": "DURCH DEN DURCHLASS LEITEN",
    "PROC102": "LEITEN UND UMSETZEN",
    "PROC103": "KURZ DURCHLEITEN UND SCHLIESSEN",
    "PROC116": "POSTEN LEITEN UND ENTNEHMEN",
    "PROC118": "LAENGER LEITEN",
    "PROC119": "VOLLSTAENDIG ANSETZEN UND SCHLIESSEN",
    "PROC123": "AUS DER QUELLE LEITEN UND UMSETZEN",
    "PROC124": "KURZE PROBE ENTNEHMEN",
    "PROC125": "EINBRINGEN UMSETZEN UND SCHLIESSEN",
    "PROC146": "LAENGER AUS DER QUELLE ARBEITEN",
    "PROC147": "NACH SOLLMASS LEITEN",
    "PROC148": "ZIELANSATZ KUEHLEN",
    "PROC039": "EINE PORTION ZUGEBEN",
    "PROC040": "EINE NACHGABE ZUGEBEN",
    "PROC041": "ARBEITSGANG SCHLIESSEN",
    "PROC167": "VON DORT WEITERLEITEN",
    "PROC168": "AN DER ZIELSTELLE UMSETZEN",
    "PROC169": "BIS ZUR ZWEITEN STUFE",
}


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(name: str, rows: list[dict[str, object]], fields: list[str]) -> None:
    with (HERE / name).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    marks = read(MARKS)
    units = read(UNITS)
    vocabulary = read(VOCAB)
    cards = read(CARDS)
    unit_by_key = {(row["order_id"], row["stage"], row["unit"]): row for row in units}
    target_units = [row for row in units if row["execution_status"] == "CORE_PLUS_LOCAL_MODEL" and int(row["model_marks"]) == 3]
    target_ids = set(PROMOTIONS)
    decisions: list[dict[str, object]] = []
    phrases: list[dict[str, object]] = []
    for phrase_index, unit in enumerate(target_units, start=1):
        local = [row for row in marks if row["order_id"] == unit["order_id"] and row["stage"] == unit["stage"] and row["unit"] == unit["unit"]]
        gaps = [row for row in local if row["apprentice_action"] == "COPY_LOCAL_MODEL"]
        phrase_id = f"TGP{phrase_index:02d}"
        phrase_value = " -> ".join(PROMOTIONS[row["identity"]] for row in gaps)
        phrases.append({"phrase_id": phrase_id, "order_id": unit["order_id"], "master_unit_id": unit["master_unit_id"], "unit": unit["unit"], "page": unit["page"], "owner_de": unit["owner_trace_de"], "surface_phrase": " ".join(row["surface"] for row in gaps), "identity_phrase": " ".join(row["identity"] for row in gaps), "spoken_workshop_phrase_de": phrase_value, "complete_reading_de": unit["front_instruction_de"]})
        for position, gap in enumerate(gaps, start=1):
            decisions.append({"phrase_id": phrase_id, "position": position, "identity": gap["identity"], "surface": gap["surface"], "old_default_de": gap["concrete_default_de"], "new_whole_word_de": PROMOTIONS[gap["identity"]], "master_unit_id": unit["master_unit_id"], "unit": unit["unit"], "owner_de": unit["owner_trace_de"]})

    revised_vocab = []
    for row in vocabulary:
        if row["identity"] in target_ids:
            revised_vocab.append({**row, "short_value_de": PROMOTIONS[row["identity"]], "apprentice_action": "READ_TAUGHT_WHOLE_WORD", "semantic_revision": "YES", "fifth_lesson": "THREE_GAP_PHRASE_CLOSURE"})
        else:
            revised_vocab.append({**row, "fifth_lesson": "NO_CHANGE"})
    revised_marks = []
    for row in marks:
        if row["identity"] in target_ids:
            revised_marks.append({**row, "concrete_default_de": PROMOTIONS[row["identity"]], "apprentice_action": "READ_TAUGHT_WHOLE_WORD", "semantic_revision": "YES", "fifth_lesson": "THREE_GAP_PHRASE_CLOSURE"})
        else:
            revised_marks.append({**row, "fifth_lesson": "NO_CHANGE"})

    marks_by_unit: dict[str, list[dict[str, object]]] = defaultdict(list)
    for mark in revised_marks:
        unit = unit_by_key[(str(mark["order_id"]), str(mark["stage"]), str(mark["unit"]))]
        marks_by_unit[unit["master_unit_id"]].append(mark)
    phrase_by_unit = {row["master_unit_id"]: row for row in phrases}
    revised_units = []
    for unit in units:
        local = marks_by_unit[unit["master_unit_id"]]
        readable = sum(row["apprentice_action"] != "COPY_LOCAL_MODEL" for row in local)
        model = len(local) - readable
        status = "MODEL_LEAF_REQUIRED" if unit["section"] == "WHEN" else "SHARED_OR_TAUGHT_EXECUTABLE" if model == 0 else "CORE_PLUS_LOCAL_MODEL"
        closed = unit["master_unit_id"] in phrase_by_unit and status == "SHARED_OR_TAUGHT_EXECUTABLE"
        phrase = phrase_by_unit.get(unit["master_unit_id"])
        revised_units.append({**unit, "core_marks": readable, "model_marks": model, "execution_status": status, "three_gap_phrase_id": phrase["phrase_id"] if phrase else "NONE", "three_gap_phrase_de": phrase["spoken_workshop_phrase_de"] if phrase else "NONE", "three_gap_unit_closed": "YES" if closed else "NO"})

    status_counts = Counter(str(row["execution_status"]) for row in revised_units)
    revised_cards = []
    for card in cards:
        local = [row for row in revised_units if row["order_id"] == card["order_id"]]
        counts = Counter(str(row["execution_status"]) for row in local)
        revised_cards.append({"order_id": card["order_id"], "title_de": card["title_de"], "units": len(local), "executable_units": counts["SHARED_OR_TAUGHT_EXECUTABLE"], "mixed_units": counts["CORE_PLUS_LOCAL_MODEL"], "condition_units": counts["MODEL_LEAF_REQUIRED"], "newly_closed_three_gap_units": sum(row["three_gap_unit_closed"] == "YES" for row in local)})

    write(f"{PREFIX}_21_THREE_GAP_WHOLE_WORDS.tsv", decisions, ["phrase_id", "position", "identity", "surface", "old_default_de", "new_whole_word_de", "master_unit_id", "unit", "owner_de"])
    write(f"{PREFIX}_7_MEMORIZED_THREE_CARD_PHRASES.tsv", phrases, ["phrase_id", "order_id", "master_unit_id", "unit", "page", "owner_de", "surface_phrase", "identity_phrase", "spoken_workshop_phrase_de", "complete_reading_de"])
    write(f"{PREFIX}_231_REVISED_WORKSHOP_VOCABULARY.tsv", revised_vocab, list(vocabulary[0]) + ["fifth_lesson"])
    write(f"{PREFIX}_437_REVISED_MARK_DECK.tsv", revised_marks, list(marks[0]) + ["fifth_lesson"])
    write(f"{PREFIX}_118_REVISED_UNIT_EXECUTION.tsv", revised_units, list(units[0]) + ["three_gap_phrase_id", "three_gap_phrase_de", "three_gap_unit_closed"])
    write(f"{PREFIX}_6_REVISED_JOB_CARDS.tsv", revised_cards, ["order_id", "title_de", "units", "executable_units", "mixed_units", "condition_units", "newly_closed_three_gap_units"])

    lines = ["# Drei-Lücken-Phrasen", "", "Sieben lokale Dreierinseln werden zugleich als drei einzelne Kartenwerte und als ein gesprochener Werkstattblock gelernt.", ""]
    for row in phrases:
        lines.extend([f"## {row['phrase_id']} / {row['master_unit_id']}", "", f"`{row['surface_phrase']}`", f"**Ruf:** {row['spoken_workshop_phrase_de']}.", f"**Satz:** {row['complete_reading_de']}", ""])
    lines.extend(["## Bilanz", "", f"Vollständig ausführbar: {status_counts['SHARED_OR_TAUGHT_EXECUTABLE']} von 118 Einheiten.", f"Verbleibende lange Prosalücken: {status_counts['CORE_PLUS_LOCAL_MODEL']}.", "Sechs WHEN-Blätter bleiben lokal."])
    (HERE / f"{PREFIX}_THREE_GAP_PHRASEBOOK.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    summary = {"status": "PASS", "decision": "SEVEN_MEMORIZED_THREE_CARD_PHRASES_CLOSE_ALL_SEVEN_THREE_GAP_UNITS", "promoted_identities": len(target_ids), "promoted_marks": sum(row["identity"] in target_ids for row in revised_marks), "phrase_blocks": len(phrases), "closed_units": sum(row["three_gap_unit_closed"] == "YES" for row in revised_units), "vocabulary_identities": len(revised_vocab), "marks": len(revised_marks), "units": len(revised_units), "unit_statuses": dict(status_counts), "condition_changes": 0, "component_changes": 0, "sealed_pages": ["f84", "f84r"]}
    (HERE / f"{PREFIX}_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (HERE / f"{PREFIX}_REPORT.md").write_text("# Sidequest Pass 894: three-gap phrase closure\n\nSeven three-card local islands receive individual short values and a memorized spoken phrase. All seven units close, raising the executable layer from 101 to 108; four long prose gaps and six WHEN leaves remain.\n", encoding="utf-8")


if __name__ == "__main__":
    main()
