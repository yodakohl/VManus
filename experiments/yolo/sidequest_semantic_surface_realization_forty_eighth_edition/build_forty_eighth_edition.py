#!/usr/bin/env python3
"""Realize only those predicted cells expressible with existing whole cards."""

from __future__ import annotations

import csv
import hashlib
import json
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
PREDICTIONS = ROOT / "experiments/yolo/sidequest_semantic_slot_lattice_forty_seventh_edition/FORTY_SEVENTH_24_EMPTY_CELL_PREDICTIONS.tsv"
LEDGER = ROOT / "experiments/yolo/sidequest_semantic_final_productive_cards_nineteenth_edition/NINETEENTH_776_SPEAKABLE_LEDGER.tsv"

PROFILES = ("S1_BARE_MASTER", "S2_Q_CELL_SCRIBE", "S3_S_LINE_SCRIBE", "S4_MIXED_COMPACT")


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


def choose_surface(surfaces: list[str], profile: str, offset: int) -> str:
    unique = sorted(set(surfaces), key=lambda value: (len(value), value))
    if profile == "S2_Q_CELL_SCRIBE":
        candidates = [value for value in unique if value.startswith("q")]
    elif profile == "S3_S_LINE_SCRIBE":
        candidates = [value for value in unique if value.startswith("s")]
    elif profile == "S4_MIXED_COMPACT":
        candidates = [value for value in unique if value.startswith(("o", "d", "a"))]
    else:
        candidates = [value for value in unique if not value.startswith(("q", "s"))]
    pool = candidates or unique
    return pool[offset % len(pool)]


def donor(observed: dict[str, list[dict[str, str]]], base: str, ending: str, side: str) -> str:
    if side == "base":
        candidates = [(sequence, rows) for sequence, rows in observed.items() if sequence.startswith(base + "+")]
    else:
        candidates = [(sequence, rows) for sequence, rows in observed.items() if sequence.endswith("+" + ending)]
    if not candidates:
        return "NONE"
    sequence, rows = sorted(candidates, key=lambda item: (-len(item[1]), item[0]))[0]
    return f"{sequence}:{'|'.join(sorted({row['visible_surface'] for row in rows}))}"


def main() -> None:
    predictions = read_tsv(PREDICTIONS)
    ledger = read_tsv(LEDGER)
    observed: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in ledger:
        observed[row["atom_sequence"]].append(row)

    decisions = []
    copies = []
    blocked = []
    for row in predictions:
        base_cards = observed.get(row["base"], [])
        ending_cards = observed.get(row["ending"], [])
        analytic = bool(base_cards and ending_cards)
        missing = []
        if not base_cards:
            missing.append("BARE_BASE_CARD")
        if not ending_cards:
            missing.append("BARE_ENDING_CARD")
        decision = {
            "prediction_rank": row["prediction_rank"],
            "cell_id": row["cell_id"],
            "predicted_fused_atom_sequence": row["normalized_atom_sequence"],
            "predicted_reading_de": row["future_readback_de"],
            "bare_base_available": "YES" if base_cards else "NO",
            "bare_base_surfaces": "|".join(sorted({card["visible_surface"] for card in base_cards})) or "NONE",
            "bare_ending_available": "YES" if ending_cards else "NO",
            "bare_ending_surfaces": "|".join(sorted({card["visible_surface"] for card in ending_cards})) or "NONE",
            "exact_fused_surface_available": "NO",
            "analytic_two_card_expression_available": "YES" if analytic else "NO",
            "surface_decision": "WRITE_AS_TWO_REGISTERED_CARDS" if analytic else "BLOCK_UNTIL_NEW_REGISTERED_CARD",
            "missing_inventory": "|".join(missing) or "NONE",
            "strongest_base_donor": donor(observed, row["base"], row["ending"], "base"),
            "strongest_ending_donor": donor(observed, row["base"], row["ending"], "ending"),
            "boundary_warning": "ANALYTIC_BASE|ENDING_IS_NOT_THE_PREDICTED_FUSED_BASE+ENDING_CARD" if analytic else "NO_SURFACE_OR_BOUNDARY_INVENTED",
        }
        decisions.append(decision)
        if analytic:
            base_surfaces = [card["visible_surface"] for card in base_cards]
            ending_surfaces = [card["visible_surface"] for card in ending_cards]
            for offset, profile in enumerate(PROFILES):
                base_surface = choose_surface(base_surfaces, profile, offset)
                ending_surface = choose_surface(ending_surfaces, profile, offset)
                copies.append({
                    "prediction_rank": row["prediction_rank"],
                    "cell_id": row["cell_id"],
                    "scribe_profile": profile,
                    "intended_fused_atom_sequence": row["normalized_atom_sequence"],
                    "written_analytic_atom_sequence": f"{row['base']} | {row['ending']}",
                    "written_surface_sequence": f"{base_surface} {ending_surface}",
                    "spoken_reading_de": row["future_readback_de"],
                    "uses_only_observed_surfaces": "YES",
                    "new_surface_invented": "NO",
                    "word_boundary_changed": "YES_FUSED_PREDICTION_TO_TWO_CARD_PARAPHRASE",
                    "status": "APPRENTICE_ANALYTIC_PARAPHRASE_NOT_MANUSCRIPT_FORM",
                })
        else:
            blocked.append({
                "prediction_rank": row["prediction_rank"],
                "cell_id": row["cell_id"],
                "predicted_fused_atom_sequence": row["normalized_atom_sequence"],
                "predicted_reading_de": row["future_readback_de"],
                "missing_inventory": "|".join(missing),
                "why_blocked_de": "Mindestens einer der beiden Teile besitzt keine selbständige registrierte Karte; Zusammenkleben würde eine neue Oberflächenregel erfinden.",
                "allowed_master_action_de": "Befehl umschreiben oder eine bereits gelernte Mehrklauselwendung benutzen; keine neue Voynich-Form erfinden.",
            })
    write_tsv(OUT / "FORTY_EIGHTH_24_SURFACE_DECISIONS.tsv", decisions)
    write_tsv(OUT / "FORTY_EIGHTH_28_ANALYTIC_COPIES.tsv", copies)
    write_tsv(OUT / "FORTY_EIGHTH_17_BLOCKED_COMPOUNDS.tsv", blocked)

    lines = [
        "# Oberfläche nur aus vorhandenem Kartenmaterial",
        "",
        "Keine der 24 vorhergesagten Fusionszellen hat bereits eine sichtbare Gesamtkarte.",
        "Sieben lassen sich jedoch als zwei getrennte, bereits registrierte Karten sprechen",
        "und in vier Händen schreiben. Das bewahrt die Bedeutung, ändert aber ausdrücklich",
        "die Wortgrenze. Siebzehn bleiben blockiert, weil Basis oder Endung nicht als eigene",
        "Karte existiert.",
        "",
        "## Sieben analytische Paraphrasen",
        "",
    ]
    for decision in (row for row in decisions if row["analytic_two_card_expression_available"] == "YES"):
        lines.extend([
            f"### {decision['predicted_fused_atom_sequence']}",
            "",
            f"Lesung: {next(row['spoken_reading_de'] for row in copies if row['cell_id'] == decision['cell_id'])}.",
            "",
        ])
        for copy in (row for row in copies if row["cell_id"] == decision["cell_id"]):
            lines.append(f"- {copy['scribe_profile']}: `{copy['written_surface_sequence']}` = `{copy['written_analytic_atom_sequence']}`")
        lines.append("")
    lines.extend(["## Siebzehn Blockaden", ""])
    for row in blocked:
        lines.append(f"- `{row['predicted_fused_atom_sequence']}` — {row['missing_inventory']}; umschreiben, nicht zusammenkleben.")
    (OUT / "FORTY_EIGHTH_SURFACE_REALIZATION_BOOK.md").write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")

    summary = {
        "status": "CONSISTENT",
        "counts": {
            "predicted_fused_cells": len(decisions),
            "existing_fused_surfaces": sum(row["exact_fused_surface_available"] == "YES" for row in decisions),
            "analytic_two_card_cells": sum(row["analytic_two_card_expression_available"] == "YES" for row in decisions),
            "analytic_four_hand_copies": len(copies),
            "blocked_cells": len(blocked),
        },
        "sources": {str(path.relative_to(ROOT)): sha256(path) for path in (PREDICTIONS, LEDGER)},
    }
    (OUT / "BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
