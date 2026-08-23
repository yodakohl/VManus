#!/usr/bin/env python3
"""Render the same 116 fixed meanings through four workshop hands."""

from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
SENTENCES = ROOT / "experiments/yolo/sidequest_semantic_fixed_phrase_expander_fifty_eighth_edition/FIFTY_EIGHTH_116_FIXED_EXPANSIONS.tsv"
LEDGER = ROOT / "experiments/yolo/sidequest_semantic_final_productive_cards_nineteenth_edition/NINETEENTH_776_SPEAKABLE_LEDGER.tsv"

PROFILES = (
    ("S1_BARE_MASTER", "bevorzugt ungerahmte Form", "not_q_or_s"),
    ("S2_Q_CELL_SCRIBE", "bevorzugt q-gerahmte Form", "starts_q"),
    ("S3_S_LINE_SCRIBE", "bevorzugt s-gerahmte Form", "starts_s"),
    ("S4_MIXED_COMPACT", "bevorzugt kurze o-/d-/a-Form", "starts_oda"),
)


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


def choose(surfaces: list[str], profile: str, offset: int) -> tuple[str, str]:
    pool = sorted(set(surfaces), key=lambda value: (len(value), value))
    tests = {
        "S1_BARE_MASTER": lambda value: not value.startswith(("q", "s")),
        "S2_Q_CELL_SCRIBE": lambda value: value.startswith("q"),
        "S3_S_LINE_SCRIBE": lambda value: value.startswith("s"),
        "S4_MIXED_COMPACT": lambda value: value.startswith(("o", "d", "a")),
    }
    preferred = [value for value in pool if tests[profile](value)]
    candidates = preferred or pool
    return candidates[offset % len(candidates)], "PROFILE_MATCH" if preferred else "REGISTERED_FALLBACK"


def main() -> None:
    sentences = read_tsv(SENTENCES)
    prose_ledger = [row for row in read_tsv(LEDGER) if row["register"] == "PROSE"]
    by_unit: dict[str, list[dict[str, str]]] = defaultdict(list)
    by_atom: dict[str, list[str]] = defaultdict(list)
    for row in prose_ledger:
        by_unit[row["reading_unit_id"]].append(row)
        by_atom[row["atom_sequence"]].append(row["visible_surface"])

    profile_rows = [
        {"scribe_profile": profile, "copying_habit_de": habit, "surface_preference": preference,
         "meaning_rule_de": "Nur innerhalb derselben atom_sequence wählen; Kartenfolge und Satzlesung nie ändern."}
        for profile, habit, preference in PROFILES
    ]
    write_tsv(OUT / "FIFTY_NINTH_4_SCRIBE_PROFILES.tsv", profile_rows)

    choices = []
    copies = []
    for sentence in sentences:
        source_groups = by_unit[sentence["unit_id"]]
        source_surfaces = [row["visible_surface"] for row in source_groups]
        atom_sequence = " | ".join(row["atom_sequence"] for row in source_groups)
        for profile_index, (profile, _, _) in enumerate(PROFILES):
            written = []
            match_count = 0
            for group_index, group in enumerate(source_groups, 1):
                selected, selection = choose(by_atom[group["atom_sequence"]], profile, profile_index + group_index)
                written.append(selected)
                match_count += selection == "PROFILE_MATCH"
                choices.append({
                    "copy_id": f"{sentence['unit_id']}::{profile}",
                    "unit_id": sentence["unit_id"],
                    "page": sentence["page"],
                    "scribe_profile": profile,
                    "group_position": group_index,
                    "source_group_id": group["source_group_id"],
                    "atom_sequence": group["atom_sequence"],
                    "source_surface": group["visible_surface"],
                    "selected_surface": selected,
                    "selection_mode": selection,
                    "surface_changed": "YES" if selected != group["visible_surface"] else "NO",
                    "atom_identity_preserved": "YES",
                })
            changed = sum(left != right for left, right in zip(source_surfaces, written))
            copies.append({
                "copy_id": f"{sentence['unit_id']}::{profile}",
                "unit_id": sentence["unit_id"],
                "page": sentence["page"],
                "scribe_profile": profile,
                "group_count": len(source_groups),
                "source_surface_sequence": " ".join(source_surfaces),
                "rendered_surface_sequence": " ".join(written),
                "atom_sequence": atom_sequence,
                "fixed_generated_prose_de": sentence["fixed_generated_prose_de"],
                "surface_changes": changed,
                "profile_matches": match_count,
                "semantic_readback_changed": "NO",
                "status": "SAFE_ALLOGRAPHIC_RENDERING",
            })
    write_tsv(OUT / "FIFTY_NINTH_1524_GROUP_CHOICES.tsv", choices)
    write_tsv(OUT / "FIFTY_NINTH_464_HAND_COPIES.tsv", copies)

    safety = [
        ("SAFE01", "same atom_sequence, different registered surface", "SAFE", "Schreibergewohnheit ändert sich, Kartenwert bleibt."),
        ("SAFE02", "same card order across a physical line", "SAFE", "Zeilenumbruch ist Platz, kein Satzwechsel."),
        ("SAFE03", "q/s/bare wrapper chosen from the same atom family", "SAFE", "Rahmenallograph bleibt Rendererwahl."),
        ("SAFE04", "different surface length within the same registered atom", "SAFE", "Kürzung oder Expansion ändert die Lesung nicht."),
        ("UNSAFE01", "replace E by EE or EEE", "UNSAFE", "Grad ändert sich."),
        ("UNSAFE02", "replace Y by a licensed CLOSE card", "UNSAFE", "aktueller Posten wird mit Schrittabschluss verwechselt."),
        ("UNSAFE03", "swap AL and AR", "UNSAFE", "Ziel und Quelle vertauschen sich."),
        ("UNSAFE04", "drop, duplicate, or reorder a card", "UNSAFE", "Arbeitsfolge oder Referent ändert sich."),
    ]
    safety_rows = [
        {"rule_id": rule_id, "copy_operation": operation, "classification": classification, "master_explanation_de": explanation}
        for rule_id, operation, classification, explanation in safety
    ]
    write_tsv(OUT / "FIFTY_NINTH_8_SAFE_UNSAFE_RULES.tsv", safety_rows)

    sample_units = ["H1-S001", "H3-S001", "B2-S012", "B4-S015"]
    book = [
        "# Vier Hände, dieselbe Werkstattanweisung",
        "",
        "Jede Hand darf nur eine andere registrierte Oberfläche derselben Karte wählen.",
        "Kartenfolge, Grad, Richtung, Referent und Schluss bleiben unangetastet.",
        "",
    ]
    for unit_id in sample_units:
        book.extend([f"## {unit_id}", ""])
        for row in (copy for copy in copies if copy["unit_id"] == unit_id):
            book.append(f"- {row['scribe_profile']}: `{row['rendered_surface_sequence']}`")
        book.append("")
    (OUT / "FIFTY_NINTH_FOUR_HAND_COPYBOOK.md").write_text("\n".join(book).rstrip() + "\n", encoding="utf-8")

    summary = {
        "status": "CONSISTENT",
        "counts": {
            "scribe_profiles": len(profile_rows),
            "statement_copies": len(copies),
            "group_choices": len(choices),
            "safe_rules": sum(row["classification"] == "SAFE" for row in safety_rows),
            "unsafe_rules": sum(row["classification"] == "UNSAFE" for row in safety_rows),
            "surface_changes": sum(int(row["surface_changes"]) for row in copies),
            "semantic_readback_changes": sum(row["semantic_readback_changed"] == "YES" for row in copies),
        },
        "profile_match_counts": dict(Counter(row["scribe_profile"] for row in choices if row["selection_mode"] == "PROFILE_MATCH")),
        "sources": {str(path.relative_to(ROOT)): sha256(path) for path in (SENTENCES, LEDGER)},
    }
    (OUT / "BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
