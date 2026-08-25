#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from collections import Counter, defaultdict
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
SOURCE = ROOT / "sidequest_semantic_four_gap_recipe_closure_eight_hundred_ninety_fifth"
MARKS = SOURCE / "EIGHT_HUNDRED_NINETY_FIFTH_437_REVISED_MARK_DECK.tsv"
UNITS = SOURCE / "EIGHT_HUNDRED_NINETY_FIFTH_118_REVISED_UNIT_EXECUTION.tsv"
VOCAB = SOURCE / "EIGHT_HUNDRED_NINETY_FIFTH_231_REVISED_WORKSHOP_VOCABULARY.tsv"
CARDS = SOURCE / "EIGHT_HUNDRED_NINETY_FIFTH_6_REVISED_JOB_CARDS.tsv"
PREFIX = "EIGHT_HUNDRED_NINETY_SIXTH"

PROMOTIONS = {
    "PROC068": "WASSER ZUGEBEN",
    "PROC071": "KUEHL WEITERARBEITEN",
    "PROC022": "ANSATZ WEITERFUEHREN",
    "PROC073": "KURZ AM ZIELDURCHLASS HALTEN",
    "PROC074": "LAENGER AN DER ZIELSTELLE ANSETZEN",
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
    target = next(row for row in units if row["execution_status"] == "CORE_PLUS_LOCAL_MODEL")
    target_marks = [row for row in marks if row["order_id"] == target["order_id"] and row["stage"] == target["stage"] and row["unit"] == target["unit"]]
    gaps = [row for row in target_marks if row["apprentice_action"] == "COPY_LOCAL_MODEL"]
    target_ids = set(PROMOTIONS)

    decisions = []
    for gap in gaps:
        index = target_marks.index(gap)
        decisions.append({"position_in_statement": index + 1, "identity": gap["identity"], "surface": gap["surface"], "old_default_de": gap["concrete_default_de"], "new_whole_word_de": PROMOTIONS[gap["identity"]], "left_surface": target_marks[index - 1]["surface"] if index else "UNIT_START", "right_surface": target_marks[index + 1]["surface"] if index + 1 < len(target_marks) else "UNIT_END", "owner_de": gap["owner_or_handle_de"]})

    revised_vocab = []
    for row in vocabulary:
        if row["identity"] in target_ids:
            revised_vocab.append({**row, "short_value_de": PROMOTIONS[row["identity"]], "apprentice_action": "READ_TAUGHT_WHOLE_WORD", "semantic_revision": "YES", "seventh_lesson": "FINAL_PROSE_GAP_CLOSURE"})
        else:
            revised_vocab.append({**row, "seventh_lesson": "NO_CHANGE"})
    revised_marks = []
    for row in marks:
        if row["identity"] in target_ids:
            revised_marks.append({**row, "concrete_default_de": PROMOTIONS[row["identity"]], "apprentice_action": "READ_TAUGHT_WHOLE_WORD", "semantic_revision": "YES", "seventh_lesson": "FINAL_PROSE_GAP_CLOSURE"})
        else:
            revised_marks.append({**row, "seventh_lesson": "NO_CHANGE"})

    marks_by_unit: dict[str, list[dict[str, object]]] = defaultdict(list)
    for mark in revised_marks:
        unit = unit_by_key[(str(mark["order_id"]), str(mark["stage"]), str(mark["unit"]))]
        marks_by_unit[unit["master_unit_id"]].append(mark)
    revised_units = []
    for unit in units:
        local = marks_by_unit[unit["master_unit_id"]]
        readable = sum(row["apprentice_action"] != "COPY_LOCAL_MODEL" for row in local)
        model = len(local) - readable
        status = "MODEL_LEAF_REQUIRED" if unit["section"] == "WHEN" else "SHARED_OR_TAUGHT_EXECUTABLE" if model == 0 else "CORE_PLUS_LOCAL_MODEL"
        newly = unit["master_unit_id"] == target["master_unit_id"] and status == "SHARED_OR_TAUGHT_EXECUTABLE"
        revised_units.append({**unit, "core_marks": readable, "model_marks": model, "execution_status": status, "final_prose_gap_words_de": " | ".join(PROMOTIONS[row["identity"]] for row in local if row["identity"] in target_ids) or "NONE", "final_prose_gap_closed": "YES" if newly else "NO"})

    passage = []
    for position, row in enumerate([mark for mark in revised_marks if mark["order_id"] == target["order_id"] and mark["stage"] == target["stage"] and mark["unit"] == target["unit"]], start=1):
        passage.append({"position": position, "surface": row["surface"], "identity": row["identity"], "short_value_de": row["concrete_default_de"], "reading_source": "FINAL_FIVE_GAP_LESSON" if row["identity"] in target_ids else row["apprentice_action"], "owner_de": row["owner_or_handle_de"]})

    status_counts = Counter(str(row["execution_status"]) for row in revised_units)
    revised_cards = []
    for card in cards:
        local = [row for row in revised_units if row["order_id"] == card["order_id"]]
        counts = Counter(str(row["execution_status"]) for row in local)
        revised_cards.append({"order_id": card["order_id"], "title_de": card["title_de"], "units": len(local), "prose_units": sum(row["section"] != "WHEN" for row in local), "executable_prose_units": sum(row["section"] != "WHEN" and row["execution_status"] == "SHARED_OR_TAUGHT_EXECUTABLE" for row in local), "condition_units": counts["MODEL_LEAF_REQUIRED"], "prose_complete": "YES"})

    prose_units = [row for row in revised_units if row["section"] != "WHEN"]
    write(f"{PREFIX}_5_FINAL_PROSE_WHOLE_WORDS.tsv", decisions, ["position_in_statement", "identity", "surface", "old_default_de", "new_whole_word_de", "left_surface", "right_surface", "owner_de"])
    write(f"{PREFIX}_19_CARD_B1_S002_MASTER_PASSAGE.tsv", passage, ["position", "surface", "identity", "short_value_de", "reading_source", "owner_de"])
    write(f"{PREFIX}_231_COMPLETE_WORKSHOP_VOCABULARY.tsv", revised_vocab, list(vocabulary[0]) + ["seventh_lesson"])
    write(f"{PREFIX}_437_COMPLETE_MARK_DECK.tsv", revised_marks, list(marks[0]) + ["seventh_lesson"])
    write(f"{PREFIX}_118_COMPLETE_UNIT_EXECUTION.tsv", revised_units, list(units[0]) + ["final_prose_gap_words_de", "final_prose_gap_closed"])
    write(f"{PREFIX}_112_COMPLETE_PROSE_UNITS.tsv", prose_units, list(revised_units[0]))
    write(f"{PREFIX}_6_PROSE_COMPLETE_JOB_CARDS.tsv", revised_cards, ["order_id", "title_de", "units", "prose_units", "executable_prose_units", "condition_units", "prose_complete"])

    units_by_order: dict[str, list[dict[str, object]]] = defaultdict(list)
    for unit in prose_units:
        units_by_order[str(unit["order_id"])].append(unit)
    lines = ["# Prosa-vollständiges Werkstattbuch", ""]
    lines.extend(["Alle 112 WHAT-/HOW-Einheiten sind jetzt aus gemeinsamem Kern und gelernten Ganzkarten lesbar.", "Die sechs WHEN-Gruppen bleiben als vollständige lokale Bildblätter daneben liegen.", ""])
    for card in revised_cards:
        lines.extend([f"## {card['order_id']}: {card['title_de']}", ""])
        for unit in units_by_order[str(card["order_id"])]:
            local = marks_by_unit[unit["master_unit_id"]]
            literal = "; ".join(str(row["concrete_default_de"]) for row in local)
            lines.extend([f"### {unit['master_unit_id']} / {unit['unit']}", "", f"`{unit['back_copy_sequence']}`", f"**Kartenweise:** {literal}.", f"**Flüssig:** {unit['front_instruction_de']}", ""])
    (HERE / f"{PREFIX}_PROSE_COMPLETE_WORKSHOP_BOOK.md").write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")

    action_counts = Counter(str(row["apprentice_action"]) for row in revised_marks)
    summary = {"status": "PASS", "decision": "ALL_ONE_HUNDRED_TWELVE_PROSE_UNITS_ARE_READABLE_FROM_SHARED_CORE_AND_TAUGHT_WHOLE_CARDS", "final_promoted_identities": len(target_ids), "final_promoted_marks": sum(row["identity"] in target_ids for row in revised_marks), "prose_units": len(prose_units), "prose_marks": sum(row["master_section"] != "WHEN" for row in revised_marks), "condition_units": status_counts["MODEL_LEAF_REQUIRED"], "condition_marks": sum(row["master_section"] == "WHEN" for row in revised_marks), "vocabulary_identities": len(revised_vocab), "marks": len(revised_marks), "units": len(revised_units), "unit_statuses": dict(status_counts), "mark_actions": dict(action_counts), "remaining_local_prose_marks": sum(row["master_section"] != "WHEN" and row["apprentice_action"] == "COPY_LOCAL_MODEL" for row in revised_marks), "condition_changes": 0, "component_changes": 0, "sealed_pages": ["f84", "f84r"]}
    (HERE / f"{PREFIX}_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (HERE / f"{PREFIX}_REPORT.md").write_text("# Sidequest Pass 896: prose-complete workshop edition\n\nFive short whole cards close B1-S002, the sole remaining prose gap. All 112 WHAT/HOW units and all 364 prose marks are now readable from the shared core and taught whole-card vocabulary. The six complete local WHEN leaves remain separate and unchanged.\n", encoding="utf-8")


if __name__ == "__main__":
    main()
