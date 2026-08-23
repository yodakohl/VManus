#!/usr/bin/env python3
"""Compose new workshop commands from the idiom deck and render four hands."""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
IDIOMS = ROOT / "experiments/yolo/sidequest_semantic_scribe_idiom_copybook_twenty_ninth_edition/TWENTY_NINTH_17_IDIOM_COPYBOOK.tsv"
COPIES = ROOT / "experiments/yolo/sidequest_semantic_scribe_idiom_copybook_twenty_ninth_edition/TWENTY_NINTH_68_SCRIBE_IDIOM_COPIES.tsv"
STATEMENTS = ROOT / "experiments/yolo/sidequest_semantic_four_scribe_copyshop/FOUR_HAND_116_STATEMENT_RENDERINGS.tsv"
OLD_EXERCISES = ROOT / "experiments/yolo/sidequest_semantic_new_dictations_thirtieth_edition/THIRTIETH_12_NEW_DICTATIONS.tsv"


EXERCISES = [
    ("X29", "PICTURED_PLANT", ("E03", "E12", "E16", "E04"), "Setze den aktuellen Pflanzenansatz auf Sollmaß, führe ihn im selben Gang weiter, lasse ihn kurz stehen und schließe."),
    ("X30", "UPPER_PAIRED_BASINS", ("E14", "E05", "E09"), "Bringe die nächste Portion zum Becken, setze sie um, führe sie weiter, halte sie länger und schließe."),
    ("X31", "CLOTH_FILTER", ("E01", "E17", "E10"), "Nimm diesen Posten nach Sollmaß, bringe ihn zum Tuch, halte ihn länger, setze kurz nach und schließe."),
    ("X32", "LOCAL_POOL_TARGET", ("E15", "E13", "E04"), "Führe den Fortsetzungsansatz weiter, stelle ihn auf Sollmaß, lasse ihn kurz absetzen und schließe."),
    ("X33", "CELESTIAL_TABLE", ("E02", "E08", "E11"), "Lies den Sollwert des aktuellen Tabellenpostens, arbeite an derselben Zielstelle weiter und setze den länger gehaltenen Wert erneut ein."),
    ("X34", "PICTURED_PLANT", ("E06", "E16", "E09"), "Führe denselben Pflanzenteil um das Sollmaß, gehe danach im gleichen Gang weiter, setze um, halte länger und schließe."),
    ("X35", "UPPER_PAIRED_BASINS", ("E03", "E14", "E10"), "Nimm den laufenden Beckenansatz, bringe die nächste Portion zum Ziel, halte länger, setze kurz nach und schließe."),
    ("X36", "CLOTH_FILTER", ("E12", "E05", "E04"), "Setze den aktuellen Posten am Tuch auf Sollmaß, führe ihn hindurch weiter, lasse kurz absetzen und schließe."),
    ("X37", "LOCAL_POOL_TARGET", ("E15", "E06", "E17"), "Führe den Fortsetzungsansatz weiter, halte denselben Posten beim Sollmaß und bringe ihn zum sichtbaren Ziel."),
    ("X38", "CELESTIAL_TABLE", ("E16", "E14", "E09"), "Gehe zur folgenden Tabellenzelle, bringe deren Portion an die Zieladresse, setze sie um, halte länger und schließe."),
    ("X39", "PICTURED_PLANT", ("E11", "E13", "E04"), "Setze den länger gehaltenen Pflanzenposten weiter an, stelle ihn auf Sollmaß, lasse kurz absetzen und schließe."),
    ("X40", "UPPER_PAIRED_BASINS", ("E01", "E08", "E10"), "Nimm den Beckenposten nach Sollmaß, arbeite am selben Ziel weiter, halte länger, setze kurz nach und schließe."),
    ("X41", "CLOTH_FILTER", ("E03", "E05", "E13", "E04"), "Nimm den laufenden Ansatz, setze ihn durch das Tuch um, führe ihn auf Sollmaß weiter, lasse kurz absetzen und schließe."),
    ("X42", "LOCAL_POOL_TARGET", ("E14", "E11", "E09"), "Bringe die nächste Portion zur Poolstation, setze den länger gehaltenen Posten weiter an, setze um und schließe."),
    ("X43", "CELESTIAL_TABLE", ("E02", "E16", "E12", "E04"), "Lies den Sollwert dieses Tabellenpostens, gehe im selben Gang weiter, setze den Wert und schließe nach kurzer Ruhe."),
    ("X44", "PICTURED_PLANT", ("E15", "E17", "E10"), "Führe den Fortsetzungsansatz weiter, bringe ihn zur bezeichneten Stelle, halte länger, setze kurz nach und schließe."),
    ("X45", "UPPER_PAIRED_BASINS", ("E06", "E08", "E11"), "Führe denselben Beckenposten um das Sollmaß, arbeite am Ziel weiter und setze den länger gehaltenen Posten erneut an."),
    ("X46", "CLOTH_FILTER", ("E12", "E16", "E17", "E09"), "Setze den Tuchposten auf Sollmaß, gehe im selben Gang weiter, bringe ihn zum Ziel, setze um, halte länger und schließe."),
    ("X47", "LOCAL_POOL_TARGET", ("E03", "E13", "E05", "E04"), "Nimm den laufenden Poolansatz, führe ihn auf Sollmaß weiter, setze ihn um, lasse kurz absetzen und schließe."),
    ("X48", "CELESTIAL_TABLE", ("E01", "E14", "E09"), "Nimm den Tabellenposten nach Sollwert, bringe die nächste Portion zur Zielzelle, setze um, halte länger und schließe."),
]

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


def main() -> None:
    idioms = {row["pattern_id"]: row for row in read_tsv(IDIOMS)}
    copies = {(row["pattern_id"], row["scribe_id"]): row for row in read_tsv(COPIES)}
    observed = [row["tuple_sequence"] for row in read_tsv(STATEMENTS) if row["scribe_id"] == "S1_BARE_MASTER"]
    old = [row["tuple_sequence"] for row in read_tsv(OLD_EXERCISES)]
    exercise_rows: list[dict[str, object]] = []
    copy_rows: list[dict[str, object]] = []
    new_sequences: set[str] = set()
    for exercise_id, owner, pattern_ids, dictation in EXERCISES:
        tuple_sequence = " ".join(idioms[pid]["tuple_sequence"] for pid in pattern_ids)
        atom_chain = " | ".join(idioms[pid]["pattern"] for pid in pattern_ids)
        spoken = " ; ".join(idioms[pid]["spoken_idiom_de"] for pid in pattern_ids)
        if tuple_sequence in new_sequences:
            raise RuntimeError(f"duplicate new tuple chain: {exercise_id}")
        new_sequences.add(tuple_sequence)
        observed_hit = any(f" {tuple_sequence} " in f" {sequence} " for sequence in observed)
        old_hit = any(f" {tuple_sequence} " in f" {sequence} " for sequence in old)
        target_needed = bool(set(pattern_ids) & {"E08", "E14", "E17"})
        previous_needed = bool(set(pattern_ids) & {"E15", "E16"})
        closed = bool(set(pattern_ids) & {"E04", "E09", "E10"})
        variants = []
        for profile in PROFILES:
            surfaces = " ".join(copies[(pid, profile)]["scribe_surface_sequence"] for pid in pattern_ids)
            variants.append(surfaces)
            copy_rows.append({
                "exercise_id": exercise_id,
                "silent_owner": owner,
                "master_dictation_de": dictation,
                "scribe_id": profile,
                "idiom_ids": "|".join(pattern_ids),
                "tuple_sequence": tuple_sequence,
                "atom_pattern_chain": atom_chain,
                "scribe_surface_sequence": surfaces,
                "semantic_readback_de": spoken,
                "initial_memory": f"OWNER={owner};ACTIVE={exercise_id}:A1;TARGET={'SET' if target_needed else 'LEER'};PREVIOUS={'SET' if previous_needed else 'LEER'}",
                "final_memory": f"OWNER={owner};ACTIVE={'CLOSED' if closed else exercise_id + ':A1'};TARGET={'SET' if target_needed else 'LEER'};PREVIOUS={'SET' if previous_needed else 'LEER'}",
                "meaning_changed": "NO",
                "status": "NEW_WORKSHOP_EXERCISE_NOT_MANUSCRIPT_TEXT",
            })
        exercise_rows.append({
            "exercise_id": exercise_id,
            "silent_owner": owner,
            "master_dictation_de": dictation,
            "idiom_ids": "|".join(pattern_ids),
            "idiom_count": len(pattern_ids),
            "tuple_count": len(tuple_sequence.split()),
            "tuple_sequence": tuple_sequence,
            "atom_pattern_chain": atom_chain,
            "spoken_idiom_chain_de": spoken,
            "memory_owner": owner,
            "memory_active": f"{exercise_id}:A1",
            "memory_target": "SET" if target_needed else "LEER",
            "memory_previous": "SET" if previous_needed else "LEER",
            "ends_closed": "YES" if closed else "NO",
            "distinct_surface_variants": len(set(variants)),
            "occurs_in_fixed_statement": "YES" if observed_hit else "NO",
            "occurs_in_prior_dictation": "YES" if old_hit else "NO",
            "four_surface_copies": " | ".join(f"{profile}:{variant}" for profile, variant in zip(PROFILES, variants)),
        })
    write_tsv(OUT / "FORTY_SECOND_20_FORWARD_COMMANDS.tsv", exercise_rows)
    write_tsv(OUT / "FORTY_SECOND_80_SCRIBE_COPIES.tsv", copy_rows)

    lines = [
        "# Zwanzig neue Meisterdiktate",
        "",
        "Diese Befehle stehen nicht auf den zehn Seiten. Sie prüfen die produktive Richtung:",
        "Der Meister nennt Bildbesitzer und Handlung; der Lehrling wählt gelernte Wendungen,",
        "führt die Vierfach-Merktafel und schreibt dieselbe Kartenfolge in einer von vier Händen.",
        "",
    ]
    for row in exercise_rows:
        lines.extend([
            f"## {row['exercise_id']} — {row['silent_owner']}",
            "",
            str(row["master_dictation_de"]),
            "",
            f"Werkstattlesung: {row['spoken_idiom_chain_de']}.",
            "",
            f"Atome: `{row['atom_pattern_chain']}`",
            "",
            f"Merktafel: `O={row['memory_owner']} | A={row['memory_active']} | T={row['memory_target']} | P={row['memory_previous']}`",
            "",
            f"Vier Hände: `{row['four_surface_copies']}`",
            "",
        ])
    (OUT / "FORTY_SECOND_MASTER_DICTATION_BOOK.md").write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")

    summary = {
        "status": "CONSISTENT",
        "counts": {
            "new_commands": len(exercise_rows),
            "scribe_copies": len(copy_rows),
            "scribe_profiles": len(PROFILES),
            "owners": len({row["silent_owner"] for row in exercise_rows}),
            "chains_absent_from_fixed_statements": sum(row["occurs_in_fixed_statement"] == "NO" for row in exercise_rows),
            "chains_absent_from_prior_dictations": sum(row["occurs_in_prior_dictation"] == "NO" for row in exercise_rows),
            "commands_with_surface_variation": sum(int(row["distinct_surface_variants"]) > 1 for row in exercise_rows),
        },
        "sources": {str(path.relative_to(ROOT)): sha256(path) for path in (IDIOMS, COPIES, STATEMENTS, OLD_EXERCISES)},
    }
    (OUT / "BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
