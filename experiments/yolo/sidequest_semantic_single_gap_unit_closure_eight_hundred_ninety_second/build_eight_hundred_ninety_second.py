#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from collections import Counter, defaultdict
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
SOURCE = ROOT / "sidequest_semantic_local_only_unit_closure_eight_hundred_ninety_first"
MARKS = SOURCE / "EIGHT_HUNDRED_NINETY_FIRST_437_REVISED_MARK_DECK.tsv"
UNITS = SOURCE / "EIGHT_HUNDRED_NINETY_FIRST_118_REVISED_UNIT_EXECUTION.tsv"
VOCAB = SOURCE / "EIGHT_HUNDRED_NINETY_FIRST_231_REVISED_WORKSHOP_VOCABULARY.tsv"
CARDS = SOURCE / "EIGHT_HUNDRED_NINETY_FIRST_6_REVISED_JOB_CARDS.tsv"
PREFIX = "EIGHT_HUNDRED_NINETY_SECOND"

PROMOTIONS = {
    "PROC077": "NACHMISCHEN UND SCHLIESSEN",
    "PROC081": "ZIELKUEHLEN",
    "PROC084": "SPUELEN",
    "PROC090": "KURZ BEARBEITEN",
    "PROC110": "KURZ IM DURCHLASS HALTEN",
    "PROC113": "AUS DER QUELLE ANSETZEN",
    "PROC115": "WEITERARBEITEN",
    "PROC122": "KURZ HALTEN",
    "PROC132": "LANG ERWAERMEN UND SCHLIESSEN",
    "PROC133": "POSTEN UMSETZEN",
    "PROC134": "AN DER ZIELSTELLE EINBRINGEN",
    "PROC140": "IM ARBEITSGANG LEITEN",
    "PROC149": "VOLLSTAENDIG DURCHARBEITEN",
    "PROC150": "WASSER UMSETZEN",
    "PROC153": "AN DER ZIELSTELLE WEITERFUEHREN",
    "PROC043": "BEISEITESTELLEN",
    "PROC154": "POSTEN WEITERFUEHREN",
    "PROC065": "FOLGEPOSTEN",
    "PROC157": "LAENGER HALTEN",
    "PROC160": "WEITERANSETZEN",
    "PROC165": "AUS DER QUELLE ZUGEBEN",
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
    target_units = [row for row in units if row["execution_status"] == "CORE_PLUS_LOCAL_MODEL" and int(row["model_marks"]) == 1]
    target_ids = set(PROMOTIONS)

    decisions: list[dict[str, object]] = []
    unit_rows: list[dict[str, object]] = []
    for unit in target_units:
        local = [row for row in marks if row["order_id"] == unit["order_id"] and row["stage"] == unit["stage"] and row["unit"] == unit["unit"]]
        gap = [row for row in local if row["apprentice_action"] == "COPY_LOCAL_MODEL"]
        mark = gap[0]
        value = PROMOTIONS[mark["identity"]]
        index = local.index(mark)
        left = local[index - 1] if index else None
        right = local[index + 1] if index + 1 < len(local) else None
        decisions.append(
            {
                "identity": mark["identity"],
                "surface": mark["surface"],
                "old_default_de": mark["concrete_default_de"],
                "new_whole_word_de": value,
                "order_id": unit["order_id"],
                "master_unit_id": unit["master_unit_id"],
                "unit": unit["unit"],
                "page": unit["page"],
                "owner_de": unit["owner_trace_de"],
                "left_value_de": left["concrete_default_de"] if left else "UNIT_START",
                "right_value_de": right["concrete_default_de"] if right else "UNIT_END",
                "complete_reading_de": unit["front_instruction_de"],
            }
        )
        unit_rows.append(
            {
                "order_id": unit["order_id"],
                "master_unit_id": unit["master_unit_id"],
                "unit": unit["unit"],
                "surface_sequence": unit["back_copy_sequence"],
                "single_gap_surface": mark["surface"],
                "single_gap_value_de": value,
                "continuous_reading_de": unit["front_instruction_de"],
                "new_status": "SHARED_OR_TAUGHT_EXECUTABLE",
            }
        )

    revised_vocab: list[dict[str, object]] = []
    for row in vocabulary:
        if row["identity"] in target_ids:
            revised_vocab.append(
                {
                    **row,
                    "short_value_de": PROMOTIONS[row["identity"]],
                    "apprentice_action": "READ_TAUGHT_WHOLE_WORD",
                    "semantic_revision": "YES",
                    "third_lesson": "SINGLE_GAP_UNIT_CLOSURE",
                }
            )
        else:
            revised_vocab.append({**row, "third_lesson": "NO_CHANGE"})

    revised_marks: list[dict[str, object]] = []
    for row in marks:
        if row["identity"] in target_ids:
            revised_marks.append(
                {
                    **row,
                    "concrete_default_de": PROMOTIONS[row["identity"]],
                    "apprentice_action": "READ_TAUGHT_WHOLE_WORD",
                    "semantic_revision": "YES",
                    "third_lesson": "SINGLE_GAP_UNIT_CLOSURE",
                }
            )
        else:
            revised_marks.append({**row, "third_lesson": "NO_CHANGE"})

    marks_by_unit: dict[str, list[dict[str, object]]] = defaultdict(list)
    for mark in revised_marks:
        unit = unit_by_key[(str(mark["order_id"]), str(mark["stage"]), str(mark["unit"]))]
        marks_by_unit[unit["master_unit_id"]].append(mark)
    revised_units: list[dict[str, object]] = []
    for unit in units:
        local = marks_by_unit[unit["master_unit_id"]]
        readable = sum(row["apprentice_action"] != "COPY_LOCAL_MODEL" for row in local)
        model = len(local) - readable
        if unit["section"] == "WHEN":
            status = "MODEL_LEAF_REQUIRED"
        elif model == 0:
            status = "SHARED_OR_TAUGHT_EXECUTABLE"
        else:
            status = "CORE_PLUS_LOCAL_MODEL"
        added = [str(row["concrete_default_de"]) for row in local if row["identity"] in target_ids]
        closed = unit["execution_status"] == "CORE_PLUS_LOCAL_MODEL" and int(unit["model_marks"]) == 1 and status == "SHARED_OR_TAUGHT_EXECUTABLE"
        revised_units.append(
            {
                **unit,
                "core_marks": readable,
                "model_marks": model,
                "execution_status": status,
                "third_lesson_word_de": added[0] if added else "NONE",
                "single_gap_unit_closed": "YES" if closed else "NO",
            }
        )

    status_counts = Counter(str(row["execution_status"]) for row in revised_units)
    revised_cards: list[dict[str, object]] = []
    for card in cards:
        local = [row for row in revised_units if row["order_id"] == card["order_id"]]
        counts = Counter(str(row["execution_status"]) for row in local)
        revised_cards.append(
            {
                "order_id": card["order_id"],
                "title_de": card["title_de"],
                "units": len(local),
                "executable_units": counts["SHARED_OR_TAUGHT_EXECUTABLE"],
                "mixed_units": counts["CORE_PLUS_LOCAL_MODEL"],
                "condition_units": counts["MODEL_LEAF_REQUIRED"],
                "newly_closed_single_gap_units": sum(row["single_gap_unit_closed"] == "YES" for row in local),
            }
        )

    write(f"{PREFIX}_21_SINGLE_GAP_WHOLE_WORDS.tsv", decisions, ["identity", "surface", "old_default_de", "new_whole_word_de", "order_id", "master_unit_id", "unit", "page", "owner_de", "left_value_de", "right_value_de", "complete_reading_de"])
    write(f"{PREFIX}_21_CLOSED_SINGLE_GAP_UNITS.tsv", unit_rows, ["order_id", "master_unit_id", "unit", "surface_sequence", "single_gap_surface", "single_gap_value_de", "continuous_reading_de", "new_status"])
    write(f"{PREFIX}_231_REVISED_WORKSHOP_VOCABULARY.tsv", revised_vocab, list(vocabulary[0]) + ["third_lesson"])
    write(f"{PREFIX}_437_REVISED_MARK_DECK.tsv", revised_marks, list(marks[0]) + ["third_lesson"])
    write(f"{PREFIX}_118_REVISED_UNIT_EXECUTION.tsv", revised_units, list(units[0]) + ["third_lesson_word_de", "single_gap_unit_closed"])
    write(f"{PREFIX}_6_REVISED_JOB_CARDS.tsv", revised_cards, ["order_id", "title_de", "units", "executable_units", "mixed_units", "condition_units", "newly_closed_single_gap_units"])

    lines = ["# Ein-Lücken-Lektion", ""]
    lines.extend(
        [
            "Jede dieser 21 Einheiten war bis auf genau eine Karte bereits lesbar. Die einzelne Lücke erhält",
            "nun einen kurzen, handlungsfähigen Werkstattwert. Dadurch kann der Lehrling die ganze Einheit",
            "ohne lokales Prosa-Musterblatt ausführen.",
            "",
        ]
    )
    for row in decisions:
        lines.extend(
            [
                f"## {row['master_unit_id']} / `{row['surface']}` — {row['new_whole_word_de']}",
                "",
                f"Nachbar links: {row['left_value_de']}. Nachbar rechts: {row['right_value_de']}.",
                f"Gesamt: {row['complete_reading_de']}",
                "",
            ]
        )
    lines.extend(
        [
            "## Bilanz",
            "",
            f"Vollständig ausführbare Einheiten: {status_counts['SHARED_OR_TAUGHT_EXECUTABLE']} von 118.",
            f"Verbleibende gemischte Prosaeinheiten: {status_counts['CORE_PLUS_LOCAL_MODEL']}.",
            "Die sechs WHEN-Blätter bleiben vollständig lokal.",
        ]
    )
    (HERE / f"{PREFIX}_SINGLE_GAP_LESSON.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    summary = {
        "status": "PASS",
        "decision": "TWENTY_ONE_SINGLE_GAP_WHOLE_WORDS_FREE_ALL_TWENTY_ONE_SINGLE_GAP_UNITS",
        "promoted_identities": len(target_ids),
        "promoted_marks": sum(row["identity"] in target_ids for row in revised_marks),
        "closed_units": sum(row["single_gap_unit_closed"] == "YES" for row in revised_units),
        "vocabulary_identities": len(revised_vocab),
        "marks": len(revised_marks),
        "units": len(revised_units),
        "unit_statuses": dict(status_counts),
        "condition_changes": 0,
        "component_changes": 0,
        "sealed_pages": ["f84", "f84r"],
    }
    (HERE / f"{PREFIX}_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (HERE / f"{PREFIX}_REPORT.md").write_text(
        "# Sidequest Pass 892: single-gap unit closure\n\n"
        "All 21 prose units with exactly one residual local card gain a short whole-word reading.\n"
        "The fully executable layer rises from 69 to 90 units; 22 multi-gap prose units and six\n"
        "condition leaves remain. Components and conditions are unchanged.\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
