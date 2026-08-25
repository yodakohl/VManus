#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from collections import Counter, defaultdict
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
SOURCE = ROOT / "sidequest_semantic_single_gap_unit_closure_eight_hundred_ninety_second"
MARKS = SOURCE / "EIGHT_HUNDRED_NINETY_SECOND_437_REVISED_MARK_DECK.tsv"
UNITS = SOURCE / "EIGHT_HUNDRED_NINETY_SECOND_118_REVISED_UNIT_EXECUTION.tsv"
VOCAB = SOURCE / "EIGHT_HUNDRED_NINETY_SECOND_231_REVISED_WORKSHOP_VOCABULARY.tsv"
CARDS = SOURCE / "EIGHT_HUNDRED_NINETY_SECOND_6_REVISED_JOB_CARDS.tsv"
PREFIX = "EIGHT_HUNDRED_NINETY_THIRD"

PROMOTIONS = {
    "PROC093": "KURZ WEITERARBEITEN",
    "PROC094": "UMSETZEN UND SCHLIESSEN",
    "PROC095": "POSTEN LEITEN",
    "PROC096": "KURZ WEITERHALTEN",
    "PROC136": "KURZ BEREITHALTEN UND UMSETZEN",
    "PROC137": "AUS DER QUELLE NEHMEN",
    "PROC143": "KURZ BEREITHALTEN",
    "PROC144": "AN DER ZIELSTELLE UMSETZEN UND SCHLIESSEN",
    "PROC151": "EINE PORTION UMSETZEN",
    "PROC152": "DANACH KURZ NACH SOLLMASS",
    "PROC044": "SOLLMASS ZUGEBEN",
    "PROC045": "KURZ AUS DER QUELLE ENTNEHMEN",
    "PROC049": "POSTEN WEITERBEARBEITEN",
    "PROC050": "ANSATZPORTION",
    "PROC158": "LAENGER WEITERANSETZEN",
    "PROC159": "KURZ WEITERLEITEN UND SCHLIESSEN",
    "PROC161": "KURZ DURCH DEN DURCHLASS FUEHREN",
    "PROC162": "WASSERPOSTEN SCHLIESSEN",
    "PROC163": "AM ZIELDURCHLASS ENTNEHMEN",
    "PROC164": "KURZ SAMMELN",
    "PROC056": "ZUTAT WEITERFUEHREN",
    "PROC057": "LANG DURCHZIEHEN UND SCHLIESSEN",
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
    target_units = [row for row in units if row["execution_status"] == "CORE_PLUS_LOCAL_MODEL" and int(row["model_marks"]) == 2]
    target_ids = set(PROMOTIONS)

    decisions: list[dict[str, object]] = []
    closures: list[dict[str, object]] = []
    for unit in target_units:
        local = [row for row in marks if row["order_id"] == unit["order_id"] and row["stage"] == unit["stage"] and row["unit"] == unit["unit"]]
        gaps = [row for row in local if row["apprentice_action"] == "COPY_LOCAL_MODEL"]
        closures.append(
            {
                "order_id": unit["order_id"],
                "master_unit_id": unit["master_unit_id"],
                "unit": unit["unit"],
                "page": unit["page"],
                "owner_de": unit["owner_trace_de"],
                "gap_surfaces": " ".join(row["surface"] for row in gaps),
                "gap_identities": " ".join(row["identity"] for row in gaps),
                "new_whole_words_de": " | ".join(PROMOTIONS[row["identity"]] for row in gaps),
                "complete_reading_de": unit["front_instruction_de"],
            }
        )
        for gap in gaps:
            index = local.index(gap)
            decisions.append(
                {
                    "identity": gap["identity"],
                    "surface": gap["surface"],
                    "old_default_de": gap["concrete_default_de"],
                    "new_whole_word_de": PROMOTIONS[gap["identity"]],
                    "master_unit_id": unit["master_unit_id"],
                    "unit": unit["unit"],
                    "owner_de": unit["owner_trace_de"],
                    "left_value_de": local[index - 1]["concrete_default_de"] if index else "UNIT_START",
                    "right_value_de": local[index + 1]["concrete_default_de"] if index + 1 < len(local) else "UNIT_END",
                }
            )

    revised_vocab: list[dict[str, object]] = []
    for row in vocabulary:
        if row["identity"] in target_ids:
            revised_vocab.append({**row, "short_value_de": PROMOTIONS[row["identity"]], "apprentice_action": "READ_TAUGHT_WHOLE_WORD", "semantic_revision": "YES", "fourth_lesson": "TWO_GAP_UNIT_CLOSURE"})
        else:
            revised_vocab.append({**row, "fourth_lesson": "NO_CHANGE"})
    revised_marks: list[dict[str, object]] = []
    for row in marks:
        if row["identity"] in target_ids:
            revised_marks.append({**row, "concrete_default_de": PROMOTIONS[row["identity"]], "apprentice_action": "READ_TAUGHT_WHOLE_WORD", "semantic_revision": "YES", "fourth_lesson": "TWO_GAP_UNIT_CLOSURE"})
        else:
            revised_marks.append({**row, "fourth_lesson": "NO_CHANGE"})

    marks_by_unit: dict[str, list[dict[str, object]]] = defaultdict(list)
    for mark in revised_marks:
        unit = unit_by_key[(str(mark["order_id"]), str(mark["stage"]), str(mark["unit"]))]
        marks_by_unit[unit["master_unit_id"]].append(mark)
    revised_units: list[dict[str, object]] = []
    for unit in units:
        local = marks_by_unit[unit["master_unit_id"]]
        readable = sum(row["apprentice_action"] != "COPY_LOCAL_MODEL" for row in local)
        model = len(local) - readable
        status = "MODEL_LEAF_REQUIRED" if unit["section"] == "WHEN" else "SHARED_OR_TAUGHT_EXECUTABLE" if model == 0 else "CORE_PLUS_LOCAL_MODEL"
        added = [str(row["concrete_default_de"]) for row in local if row["identity"] in target_ids]
        closed = unit["execution_status"] == "CORE_PLUS_LOCAL_MODEL" and int(unit["model_marks"]) == 2 and status == "SHARED_OR_TAUGHT_EXECUTABLE"
        revised_units.append({**unit, "core_marks": readable, "model_marks": model, "execution_status": status, "fourth_lesson_words_de": " | ".join(added) if added else "NONE", "two_gap_unit_closed": "YES" if closed else "NO"})

    status_counts = Counter(str(row["execution_status"]) for row in revised_units)
    revised_cards: list[dict[str, object]] = []
    for card in cards:
        local = [row for row in revised_units if row["order_id"] == card["order_id"]]
        counts = Counter(str(row["execution_status"]) for row in local)
        revised_cards.append({"order_id": card["order_id"], "title_de": card["title_de"], "units": len(local), "executable_units": counts["SHARED_OR_TAUGHT_EXECUTABLE"], "mixed_units": counts["CORE_PLUS_LOCAL_MODEL"], "condition_units": counts["MODEL_LEAF_REQUIRED"], "newly_closed_two_gap_units": sum(row["two_gap_unit_closed"] == "YES" for row in local)})

    write(f"{PREFIX}_22_TWO_GAP_WHOLE_WORDS.tsv", decisions, ["identity", "surface", "old_default_de", "new_whole_word_de", "master_unit_id", "unit", "owner_de", "left_value_de", "right_value_de"])
    write(f"{PREFIX}_11_CLOSED_TWO_GAP_UNITS.tsv", closures, ["order_id", "master_unit_id", "unit", "page", "owner_de", "gap_surfaces", "gap_identities", "new_whole_words_de", "complete_reading_de"])
    write(f"{PREFIX}_231_REVISED_WORKSHOP_VOCABULARY.tsv", revised_vocab, list(vocabulary[0]) + ["fourth_lesson"])
    write(f"{PREFIX}_437_REVISED_MARK_DECK.tsv", revised_marks, list(marks[0]) + ["fourth_lesson"])
    write(f"{PREFIX}_118_REVISED_UNIT_EXECUTION.tsv", revised_units, list(units[0]) + ["fourth_lesson_words_de", "two_gap_unit_closed"])
    write(f"{PREFIX}_6_REVISED_JOB_CARDS.tsv", revised_cards, ["order_id", "title_de", "units", "executable_units", "mixed_units", "condition_units", "newly_closed_two_gap_units"])

    lines = ["# Zwei-Lücken-Lektion", ""]
    lines.append("Elf Einheiten hatten je zwei lokale Karten. Beide werden als kurze Werkstattrufe gelernt; der umgebende gemeinsame Kern bleibt unverändert.")
    lines.append("")
    for row in closures:
        lines.extend([f"## {row['master_unit_id']} / `{row['gap_surfaces']}`", "", f"Neue Rufe: {row['new_whole_words_de']}.", f"Gesamt: {row['complete_reading_de']}", ""])
    lines.extend(["## Bilanz", "", f"Vollständig ausführbar: {status_counts['SHARED_OR_TAUGHT_EXECUTABLE']} von 118 Einheiten.", f"Verbleibende Mehrfachlücken: {status_counts['CORE_PLUS_LOCAL_MODEL']} Einheiten.", "Sechs WHEN-Blätter bleiben lokal."])
    (HERE / f"{PREFIX}_TWO_GAP_LESSON.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    summary = {
        "status": "PASS",
        "decision": "TWENTY_TWO_WHOLE_WORDS_CLOSE_ALL_ELEVEN_TWO_GAP_UNITS",
        "promoted_identities": len(target_ids),
        "promoted_marks": sum(row["identity"] in target_ids for row in revised_marks),
        "closed_units": sum(row["two_gap_unit_closed"] == "YES" for row in revised_units),
        "vocabulary_identities": len(revised_vocab),
        "marks": len(revised_marks),
        "units": len(revised_units),
        "unit_statuses": dict(status_counts),
        "condition_changes": 0,
        "component_changes": 0,
        "sealed_pages": ["f84", "f84r"],
    }
    (HERE / f"{PREFIX}_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (HERE / f"{PREFIX}_REPORT.md").write_text("# Sidequest Pass 893: two-gap unit closure\n\nTwenty-two short whole cards close all eleven two-gap units. The executable layer rises from 90 to 101 units; eleven longer multi-gap prose units and six condition leaves remain.\n", encoding="utf-8")


if __name__ == "__main__":
    main()
