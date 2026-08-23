#!/usr/bin/env python3
"""Enumerate the tiny missing-card deck and choose a practical four-card supplement."""

from __future__ import annotations

import csv
import hashlib
import itertools
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
LATTICE = ROOT / "experiments/yolo/sidequest_semantic_slot_lattice_forty_seventh_edition/FORTY_SEVENTH_144_SLOT_LATTICE.tsv"
COMPILER = ROOT / "experiments/yolo/sidequest_semantic_compiler_decision_tree_fiftieth_edition/FIFTIETH_144_COMPILER_DECISIONS.tsv"
REQUESTS = ROOT / "experiments/yolo/sidequest_semantic_master_card_requests_fifty_first_edition/FIFTY_FIRST_8_MASTER_CARD_REQUESTS.tsv"
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
    lattice = read_tsv(LATTICE)
    compiler = {row["cell_id"]: row for row in read_tsv(COMPILER)}
    request_rows = read_tsv(REQUESTS)
    candidates = tuple(sorted(row["candidate_atom"] for row in request_rows))
    ledger = read_tsv(LEDGER)
    observed_atoms = {row["atom_sequence"] for row in ledger}
    surfaces: dict[str, list[str]] = {}
    for atom in observed_atoms:
        surfaces[atom] = sorted({row["visible_surface"] for row in ledger if row["atom_sequence"] == atom}, key=lambda item: (len(item), item))

    selected_paraphrase_ids = {
        cell_id for cell_id, row in compiler.items() if row["compiler_branch"] == "USE_CONTROLLED_PARAPHRASE"
    }
    subset_rows = []
    for mask in range(1 << len(candidates)):
        chosen = tuple(candidates[index] for index in range(len(candidates)) if mask & (1 << index))
        available = observed_atoms | set(chosen)
        analytic = [
            row for row in lattice
            if row["status"] == "OBSERVED" or (row["base"] in available and row["ending"] in available)
        ]
        analytic_ids = {row["cell_id"] for row in analytic}
        remaining_paraphrases = selected_paraphrase_ids - analytic_ids
        total_licensed = len(analytic_ids | remaining_paraphrases)
        newly_licensed = sum(
            compiler[row["cell_id"]]["compiler_branch"] == "REJECT_UNLICENSED_EMPTY_CELL"
            for row in analytic
        )
        shortened = len(selected_paraphrase_ids & analytic_ids)
        subset_rows.append({
            "subset_id": f"S{mask:03d}",
            "selected_cards": "|".join(chosen) or "NONE",
            "card_count": len(chosen),
            "observed_or_analytic_cells": len(analytic_ids),
            "remaining_controlled_paraphrases": len(remaining_paraphrases),
            "total_licensed_commands": total_licensed,
            "rejected_commands": 144 - total_licensed,
            "newly_licensed_vs_fiftieth": newly_licensed,
            "newly_licensed_beyond_25_free_approvals": newly_licensed - 25,
            "paraphrases_shortened": shortened,
            "utility_score": 3 * newly_licensed + shortened,
            "invented_surface_count": 0,
        })
    write_tsv(OUT / "FIFTY_SECOND_256_SUBSET_RESULTS.tsv", subset_rows)

    frontier = []
    for budget in range(9):
        pool = [row for row in subset_rows if int(row["card_count"]) == budget]
        best = sorted(
            pool,
            key=lambda row: (
                -int(row["total_licensed_commands"]),
                -int(row["paraphrases_shortened"]),
                row["selected_cards"],
            ),
        )[0]
        frontier.append({"card_budget": budget, **best})
    write_tsv(OUT / "FIFTY_SECOND_9_BUDGET_FRONTIER.tsv", frontier)

    recommended_cards = {"CHK", "CKHE", "E+CLOSE", "EE+CLOSE"}
    recommended = next(row for row in subset_rows if set(row["selected_cards"].split("|")) == recommended_cards)
    available = observed_atoms | recommended_cards
    recommended_rows = []
    for row in lattice:
        old = compiler[row["cell_id"]]
        analytic = row["status"] == "OBSERVED" or (row["base"] in available and row["ending"] in available)
        if row["status"] == "OBSERVED":
            branch = "OBSERVED_FUSED_CARD"
            atom_output = row["normalized_atom_sequence"]
            surface_output = surfaces[row["normalized_atom_sequence"]][0]
            surface_status = "OBSERVED"
        elif analytic:
            branch = "ANALYTIC_TWO_CARD_FORM"
            atom_output = f"{row['base']} | {row['ending']}"
            base_surface = surfaces[row["base"]][0] if row["base"] in surfaces else f"<{row['base']}_MASTER_CARD>"
            ending_surface = surfaces[row["ending"]][0] if row["ending"] in surfaces else f"<{row['ending']}_MASTER_CARD>"
            surface_output = f"{base_surface} {ending_surface}"
            surface_status = "HYPOTHETICAL_MASTER_CATEGORY" if "<" in surface_output else "OBSERVED_COMPONENTS"
        elif old["compiler_branch"] == "USE_CONTROLLED_PARAPHRASE":
            branch = "CONTROLLED_PARAPHRASE"
            atom_output = old["output_atom_sequence"]
            surface_output = old["output_surface_sequence"]
            surface_status = "OBSERVED_COMPONENTS_WITH_DRIFT"
        else:
            branch = "REJECT_AND_ASK_MASTER"
            atom_output = "NONE"
            surface_output = "NONE"
            surface_status = "NO_SURFACE"
        recommended_rows.append({
            "cell_id": row["cell_id"],
            "target_atom_sequence": row["normalized_atom_sequence"],
            "intended_reading_de": row["composed_short_reading_de"],
            "four_card_branch": branch,
            "output_atom_sequence": atom_output,
            "output_surface_or_placeholder": surface_output,
            "surface_status": surface_status,
            "new_surface_claimed": "NO",
        })
    write_tsv(OUT / "FIFTY_SECOND_144_FOUR_CARD_COMPILER.tsv", recommended_rows)

    manual = [
        "# Das kleinste starke Ergänzungsdeck",
        "",
        "Der Meister lehrt vier neue **Kartenkategorien**, noch ohne behauptete",
        "Voynich-Oberfläche:",
        "",
        "- `CKHE` — TRENNEN",
        "- `CHK` — WÄRMEN",
        "- `E+CLOSE` — KURZ, DANN SCHLUSS",
        "- `EE+CLOSE` — LÄNGER, DANN SCHLUSS.",
        "",
        "Zusätzlich werden die 25 Kombinationen zugelassen, deren zwei Einzelkarten",
        "ohnehin bereits im Register stehen. Mit diesen kostenlosen Lehrbuchzeilen und",
        "den vier neuen Kartenkategorien kann der Lehrling 128 von 144 Gitterbefehlen",
        "ausdrücken: 116 als beobachtete oder analytische Kartenfolge und zwölf als",
        "kontrollierte Umschreibung. Sechzehn bleiben beim Meister.",
        "",
        "Die vier Platzhalter sind Unterrichtsfächer, keine erfundenen Manuskriptwörter.",
        "Erst ein reales Exemplar dürfte ihnen eine sichtbare Form geben.",
    ]
    (OUT / "FIFTY_SECOND_FOUR_CARD_DECK.md").write_text("\n".join(manual).rstrip() + "\n", encoding="utf-8")

    summary = {
        "status": "CONSISTENT",
        "counts": {
            "candidate_missing_cards": len(candidates),
            "enumerated_subsets": len(subset_rows),
            "budget_frontier_rows": len(frontier),
            "recommended_card_count": len(recommended_cards),
            "recommended_licensed_commands": int(recommended["total_licensed_commands"]),
            "recommended_rejected_commands": int(recommended["rejected_commands"]),
            "recommended_observed_or_analytic": int(recommended["observed_or_analytic_cells"]),
            "recommended_remaining_paraphrases": int(recommended["remaining_controlled_paraphrases"]),
            "invented_surfaces": 0,
        },
        "recommended_cards": sorted(recommended_cards),
        "sources": {str(path.relative_to(ROOT)): sha256(path) for path in (LATTICE, COMPILER, REQUESTS, LEDGER)},
    }
    (OUT / "BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
