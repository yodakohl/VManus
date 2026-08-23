#!/usr/bin/env python3
"""Build a bounded workshop compiler over the fixed 12 x 12 card lattice."""

from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
LATTICE = ROOT / "experiments/yolo/sidequest_semantic_slot_lattice_forty_seventh_edition/FORTY_SEVENTH_144_SLOT_LATTICE.tsv"
SURFACES = ROOT / "experiments/yolo/sidequest_semantic_surface_realization_forty_eighth_edition/FORTY_EIGHTH_24_SURFACE_DECISIONS.tsv"
PARAPHRASES = ROOT / "experiments/yolo/sidequest_semantic_controlled_paraphrase_forty_ninth_edition/FORTY_NINTH_17_CONTROLLED_PARAPHRASES.tsv"
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


def first_surface(value: str) -> str:
    candidates = [item for item in value.split("|") if item and item != "NONE"]
    return sorted(candidates, key=lambda item: (len(item), item))[0]


def main() -> None:
    lattice = read_tsv(LATTICE)
    surface_rows = {row["cell_id"]: row for row in read_tsv(SURFACES)}
    paraphrase_rows = {row["cell_id"]: row for row in read_tsv(PARAPHRASES)}
    observed_surfaces = {row["visible_surface"] for row in read_tsv(LEDGER)}
    if len(lattice) != 144 or len({row["cell_id"] for row in lattice}) != 144:
        raise RuntimeError("lattice is not a unique 144-cell inventory")
    if set(paraphrase_rows) != {
        cell_id for cell_id, row in surface_rows.items()
        if row["surface_decision"] == "BLOCK_UNTIL_NEW_REGISTERED_CARD"
    }:
        raise RuntimeError("controlled paraphrases do not exactly cover the blocked selected cells")

    decisions: list[dict[str, object]] = []
    for row in lattice:
        cell_id = row["cell_id"]
        branch: str
        output_atoms: str
        output_surfaces: str
        spoken: str
        drift: str
        exact_form: str
        licensed: str
        action: str
        reason: str

        if row["status"] == "OBSERVED":
            branch = "USE_OBSERVED_FUSED_CARD"
            output_atoms = row["normalized_atom_sequence"]
            output_surfaces = first_surface(row["observed_surfaces"])
            spoken = row["composed_short_reading_de"]
            drift = "NONE"
            exact_form = "YES"
            licensed = "YES"
            action = "REGISTERKARTE_ABSCHREIBEN"
            reason = f"{row['observed_group_count']} beobachtete Gruppe(n)"
        elif cell_id in surface_rows and surface_rows[cell_id]["surface_decision"] == "WRITE_AS_TWO_REGISTERED_CARDS":
            chosen = surface_rows[cell_id]
            branch = "USE_ANALYTIC_TWO_CARD_FORM"
            output_atoms = f"{row['base']} | {row['ending']}"
            output_surfaces = f"{first_surface(chosen['bare_base_surfaces'])} {first_surface(chosen['bare_ending_surfaces'])}"
            spoken = row["composed_short_reading_de"]
            drift = "BOUNDARY_SPLIT_ONLY"
            exact_form = "NO_ANALYTIC_EXPRESSION"
            licensed = "YES"
            action = "ZWEI_REGISTERKARTEN_GETRENNT_SCHREIBEN"
            reason = "Basis und Endung sind beide als selbständige Karten belegt"
        elif cell_id in paraphrase_rows:
            chosen = paraphrase_rows[cell_id]
            branch = "USE_CONTROLLED_PARAPHRASE"
            output_atoms = chosen["paraphrase_atom_sequence"]
            output_surfaces = chosen["representative_observed_surfaces"]
            spoken = chosen["spoken_paraphrase_de"]
            drift = chosen["controlled_meaning_drift"]
            exact_form = "NO_NEAREST_PARAPHRASE"
            licensed = "YES_WITH_SPOKEN_DRIFT"
            action = "BEOBACHTETE_KARTEN_UMSCHREIBEND_SCHREIBEN"
            reason = "gewünschte Fusion fehlt; vorhandene Karten tragen eine ausdrücklich genannte Zusatzbedeutung"
        else:
            branch = "REJECT_UNLICENSED_EMPTY_CELL"
            output_atoms = "NONE"
            output_surfaces = "NONE"
            spoken = "Meister nach einer Vorlage fragen"
            drift = "UNBOUNDED_IF_INVENTED"
            exact_form = "NO"
            licensed = "NO"
            action = "NICHT_ERFINDEN__MASTEREXEMPLAR_ANFORDERN"
            reason = "leere, nicht ausgewählte Gitterzelle ohne registrierte Form oder kontrollierte Umschreibung"

        if output_surfaces != "NONE":
            for surface in output_surfaces.split():
                if surface not in observed_surfaces:
                    raise RuntimeError(f"compiler invented an unobserved surface: {surface}")
        decisions.append({
            "cell_id": cell_id,
            "base": row["base"],
            "ending": row["ending"],
            "target_atom_sequence": row["normalized_atom_sequence"],
            "intended_reading_de": row["composed_short_reading_de"],
            "lattice_status": row["status"],
            "compiler_branch": branch,
            "output_atom_sequence": output_atoms,
            "output_surface_sequence": output_surfaces,
            "spoken_instruction_de": spoken,
            "meaning_drift": drift,
            "exact_registered_fused_form": exact_form,
            "licensed_for_apprentice": licensed,
            "master_action": action,
            "reason_de": reason,
        })

    licensed_rows = [row for row in decisions if row["compiler_branch"] != "REJECT_UNLICENSED_EMPTY_CELL"]
    rejected_rows = [row for row in decisions if row["compiler_branch"] == "REJECT_UNLICENSED_EMPTY_CELL"]
    write_tsv(OUT / "FIFTIETH_144_COMPILER_DECISIONS.tsv", decisions)
    write_tsv(OUT / "FIFTIETH_79_LICENSED_COMMANDS.tsv", licensed_rows)
    write_tsv(OUT / "FIFTIETH_65_REJECTED_CELLS.tsv", rejected_rows)

    examples = {}
    for row in decisions:
        examples.setdefault(row["compiler_branch"], row)
    manual = [
        "# Schreiber-Compiler: vom gemeinten Arbeitsbefehl zur Karte",
        "",
        "Der Lehrling prüft immer in derselben Reihenfolge:",
        "",
        "1. **Ganze registrierte Karte vorhanden?** Abschreiben.",
        "2. **Basis und Endung einzeln vorhanden?** Als zwei Karten schreiben.",
        "3. **Kontrollierte Umschreibung vorhanden?** Umschreiben und die Zusatzbedeutung mitdenken.",
        "4. **Sonst:** nichts erfinden; die Werkstattvorlage beim Meister anfordern.",
        "",
        "Die Entscheidung betrifft nur das feste 12×12-Lehrgitter. Sie erzeugt kein neues Voynich-Wort.",
        "",
    ]
    for branch in (
        "USE_OBSERVED_FUSED_CARD",
        "USE_ANALYTIC_TWO_CARD_FORM",
        "USE_CONTROLLED_PARAPHRASE",
        "REJECT_UNLICENSED_EMPTY_CELL",
    ):
        row = examples[branch]
        manual.extend([
            f"## {branch}",
            "",
            f"Wunsch: **{row['intended_reading_de']}** (`{row['target_atom_sequence']}`).",
            "",
            f"Ausgabe: `{row['output_surface_sequence']}`; Arbeitslesung: **{row['spoken_instruction_de']}**.",
            "",
        ])
    (OUT / "FIFTIETH_COMPILER_MANUAL.md").write_text("\n".join(manual).rstrip() + "\n", encoding="utf-8")

    counts = Counter(row["compiler_branch"] for row in decisions)
    summary = {
        "status": "CONSISTENT",
        "counts": {
            "lattice_cells": len(decisions),
            "licensed_commands": len(licensed_rows),
            "rejected_cells": len(rejected_rows),
            **dict(counts),
            "invented_surfaces": 0,
        },
        "sources": {str(path.relative_to(ROOT)): sha256(path) for path in (LATTICE, SURFACES, PARAPHRASES, LEDGER)},
    }
    (OUT / "BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
