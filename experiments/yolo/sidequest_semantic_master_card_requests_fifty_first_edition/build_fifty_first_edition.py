#!/usr/bin/env python3
"""Rank the missing bare cards that would make the workshop compiler more useful."""

from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
LATTICE = ROOT / "experiments/yolo/sidequest_semantic_slot_lattice_forty_seventh_edition/FORTY_SEVENTH_144_SLOT_LATTICE.tsv"
COMPILER = ROOT / "experiments/yolo/sidequest_semantic_compiler_decision_tree_fiftieth_edition/FIFTIETH_144_COMPILER_DECISIONS.tsv"
LEDGER = ROOT / "experiments/yolo/sidequest_semantic_final_productive_cards_nineteenth_edition/NINETEENTH_776_SPEAKABLE_LEDGER.tsv"


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: list[dict[str, object]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    lattice_rows = read_tsv(LATTICE)
    lattice = {row["cell_id"]: row for row in lattice_rows}
    compiler = {row["cell_id"]: row for row in read_tsv(COMPILER)}
    observed = Counter(row["atom_sequence"] for row in read_tsv(LEDGER))
    rejected = [row for row in compiler.values() if row["compiler_branch"] == "REJECT_UNLICENSED_EMPTY_CELL"]

    bases = sorted({row["base"] for row in lattice_rows})
    endings = sorted({row["ending"] for row in lattice_rows})
    candidates = [("BASE", value) for value in bases if not observed[value]] + [
        ("ENDING", value) for value in endings if not observed[value]
    ]
    requests = []
    for kind, value in candidates:
        direct_new: list[str] = []
        shorter: list[str] = []
        paired: list[str] = []
        incident: list[str] = []
        meanings = set()
        for cell_id, row in lattice.items():
            if row["status"] == "OBSERVED":
                continue
            if (kind == "BASE" and row["base"] != value) or (kind == "ENDING" and row["ending"] != value):
                continue
            incident.append(cell_id)
            meanings.add(row["base_value_de"] if kind == "BASE" else row["ending_value_de"])
            other_available = bool(observed[row["ending"]] if kind == "BASE" else observed[row["base"]])
            if not other_available:
                paired.append(cell_id)
            elif compiler[cell_id]["compiler_branch"] == "REJECT_UNLICENSED_EMPTY_CELL":
                direct_new.append(cell_id)
            elif compiler[cell_id]["compiler_branch"] == "USE_CONTROLLED_PARAPHRASE":
                shorter.append(cell_id)
        score = 3 * len(direct_new) + len(shorter)
        requests.append({
            "candidate_kind": kind,
            "candidate_atom": value,
            "candidate_meaning_de": "|".join(sorted(meanings)),
            "new_commands_unlocked_by_this_card_alone": len(direct_new),
            "licensed_paraphrases_shortened": len(shorter),
            "double_missing_cells_touched_but_not_yet_unlocked": len(paired),
            "all_incident_empty_cells": len(incident),
            "utility_score": score,
            "new_command_cell_ids": "|".join(direct_new) or "NONE",
            "shortened_paraphrase_cell_ids": "|".join(shorter) or "NONE",
            "still_paired_cell_ids": "|".join(paired) or "NONE",
            "requested_master_object": f"BARE_{value}_CARD_WITH_REGISTERED_SURFACE",
            "surface_proposed": "NONE",
        })
    requests.sort(key=lambda row: (-int(row["utility_score"]), -int(row["all_incident_empty_cells"]), row["candidate_atom"]))
    for rank, row in enumerate(requests, 1):
        row["priority_rank"] = rank
    request_fields = ["priority_rank"] + [key for key in requests[0] if key != "priority_rank"]
    requests = [{key: row[key] for key in request_fields} for row in requests]

    triage = []
    approval = []
    paired_rows = []
    for row in sorted(rejected, key=lambda item: item["cell_id"]):
        cell = lattice[row["cell_id"]]
        base_ok = bool(observed[cell["base"]])
        ending_ok = bool(observed[cell["ending"]])
        missing = []
        if not base_ok:
            missing.append(cell["base"])
        if not ending_ok:
            missing.append(cell["ending"])
        if not missing:
            category = "MEANING_SELECTION_ONLY"
            next_action = "Lesung als neue analytische Zwei-Karten-Regel in das Lehrbuch aufnehmen"
        elif len(missing) == 1:
            category = "ONE_MASTER_CARD_MISSING"
            next_action = f"Bare Karte {missing[0]} im Masterexemplar suchen oder lehren"
        else:
            category = "TWO_MASTER_CARDS_MISSING"
            next_action = f"Bare Karten {missing[0]} und {missing[1]} gemeinsam anfordern"
        out = {
            "cell_id": row["cell_id"],
            "target_atom_sequence": row["target_atom_sequence"],
            "intended_reading_de": row["intended_reading_de"],
            "analogy_score": cell["analogy_score"],
            "triage_category": category,
            "bare_base_available": "YES" if base_ok else "NO",
            "bare_ending_available": "YES" if ending_ok else "NO",
            "missing_atoms": "|".join(missing) or "NONE",
            "next_master_action_de": next_action,
            "new_surface_proposed": "NO",
        }
        triage.append(out)
        if category == "MEANING_SELECTION_ONLY":
            approval.append(dict(out))
        elif category == "TWO_MASTER_CARDS_MISSING":
            paired_rows.append(dict(out))
    approval.sort(key=lambda row: (-int(row["analogy_score"]), row["cell_id"]))
    for rank, row in enumerate(approval, 1):
        row["approval_rank"] = rank
    approval_fields = ["approval_rank"] + [key for key in approval[0] if key != "approval_rank"]
    approval = [{key: row[key] for key in approval_fields} for row in approval]

    write_tsv(OUT / "FIFTY_FIRST_8_MASTER_CARD_REQUESTS.tsv", requests)
    write_tsv(OUT / "FIFTY_FIRST_65_REJECTION_TRIAGE.tsv", triage)
    write_tsv(OUT / "FIFTY_FIRST_25_MEANING_APPROVALS.tsv", approval)
    write_tsv(OUT / "FIFTY_FIRST_8_DOUBLE_MISSING_CELLS.tsv", paired_rows)

    lines = [
        "# Welche acht Karten soll der Meister zuerst liefern?",
        "",
        "Nicht alle 65 Compiler-Rückfragen brauchen eine neue Karte. 25 besitzen Basis",
        "und Endung bereits einzeln; ihnen fehlt nur die Aufnahme als gelehrte analytische",
        "Kombination. 32 weitere Befehle würden durch jeweils eine neue bare Karte sofort",
        "schreibbar. Acht Zellen brauchen zwei fehlende Karten.",
        "",
        "## Rangfolge der fehlenden Karten",
        "",
    ]
    for row in requests:
        lines.append(
            f"{row['priority_rank']}. **{row['candidate_atom']} = {row['candidate_meaning_de']}**: "
            f"{row['new_commands_unlocked_by_this_card_alone']} neue Befehle; "
            f"{row['licensed_paraphrases_shortened']} Umschreibungen werden kürzer."
        )
    lines.extend([
        "",
        "Die Bitte beschreibt nur die benötigte Kartenfunktion. Eine sichtbare Form wird",
        "nicht erfunden; der Meister müsste sie aus einem realen Exemplar oder seinem",
        "gelernten Nomenklator liefern.",
    ])
    (OUT / "FIFTY_FIRST_MASTER_REQUEST_BOOK.md").write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")

    categories = Counter(row["triage_category"] for row in triage)
    summary = {
        "status": "CONSISTENT",
        "counts": {
            "missing_bare_card_categories": len(requests),
            "rejected_cells_triaged": len(triage),
            "meaning_selection_only": categories["MEANING_SELECTION_ONLY"],
            "one_master_card_missing": categories["ONE_MASTER_CARD_MISSING"],
            "two_master_cards_missing": categories["TWO_MASTER_CARDS_MISSING"],
            "single_addition_unlock_sum": sum(int(row["new_commands_unlocked_by_this_card_alone"]) for row in requests),
            "invented_surfaces": 0,
        },
        "sources": {str(path.relative_to(ROOT)): sha256(path) for path in (LATTICE, COMPILER, LEDGER)},
    }
    (OUT / "BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
