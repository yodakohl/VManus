#!/usr/bin/env python3
"""Build practical master-correction drills for four meaning-changing errors."""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
UNITS = ROOT / "experiments/yolo/sidequest_semantic_complete_reader_fifty_sixth_edition/FIFTY_SIXTH_258_COMPLETE_UNITS.tsv"
COPIES = ROOT / "experiments/yolo/sidequest_semantic_four_scribe_rendering_fifty_ninth_edition/FIFTY_NINTH_464_HAND_COPIES.tsv"


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


def alter_grade(sequence: str) -> tuple[str, str]:
    parts = sequence.split(" | ")
    for wanted, replacement, consequence in (
        ("EEE", "EE", "vollständig wird nur länger"),
        ("EE", "E", "länger wird kurz"),
        ("E", "EE", "kurz wird länger"),
    ):
        for index, part in enumerate(parts):
            atoms = part.split("+")
            if wanted in atoms:
                atoms[atoms.index(wanted)] = replacement
                parts[index] = "+".join(atoms)
                return " | ".join(parts), consequence
    raise ValueError("no E/EE/EEE grade target")


def alter_y_close(sequence: str) -> tuple[str, str]:
    parts = sequence.split(" | ")
    for index, part in enumerate(parts):
        atoms = part.split("+")
        if atoms[-1] == "Y":
            atoms[-1] = "CLOSE"
            parts[index] = "+".join(atoms)
            return " | ".join(parts), "laufender Posten wird zum Schrittabschluss"
    for index, part in enumerate(parts):
        atoms = part.split("+")
        if atoms[-1] == "CLOSE":
            atoms[-1] = "Y"
            parts[index] = "+".join(atoms)
            return " | ".join(parts), "Schrittabschluss wird zum weiterlaufenden Posten"
    raise ValueError("no Y/CLOSE target")


def alter_direction(sequence: str) -> tuple[str, str]:
    parts = sequence.split(" | ")
    for index, part in enumerate(parts):
        atoms = part.split("+")
        if "AL" in atoms:
            atoms[atoms.index("AL")] = "AR"
            parts[index] = "+".join(atoms)
            return " | ".join(parts), "Ziel wird Quelle"
        if "AR" in atoms:
            atoms[atoms.index("AR")] = "AL"
            parts[index] = "+".join(atoms)
            return " | ".join(parts), "Quelle wird Ziel"
    raise ValueError("no AL/AR target")


def alter_order(sequence: str) -> tuple[str, str]:
    parts = sequence.split(" | ")
    if len(parts) < 2:
        raise ValueError("too short")
    parts[0], parts[1] = parts[1], parts[0]
    return " | ".join(parts), "die ersten beiden Arbeitsschritte tauschen ihre Reihenfolge"


def main() -> None:
    units = [row for row in read_tsv(UNITS) if row["unit_kind"] == "PROSE_STATEMENT"]
    copies = read_tsv(COPIES)
    bare_copy = {row["unit_id"]: row for row in copies if row["scribe_profile"] == "S1_BARE_MASTER"}

    pools = {
        "GRADE_CHANGE": [row for row in units if any(token in row["atom_sequence"] for token in ("E+Y", "EE+Y", "EEE", "E+CLOSE", "EE+CLOSE"))],
        "Y_CLOSE_CONFUSION": [row for row in units if any(part.split("+")[-1] in {"Y", "CLOSE"} for part in row["atom_sequence"].split(" | "))],
        "AL_AR_SWAP": [row for row in units if any(atom in {"AL", "AR"} for part in row["atom_sequence"].split(" | ") for atom in part.split("+"))],
        "DROP_DUPLICATE_REORDER": [row for row in units if len(row["atom_sequence"].split(" | ")) >= 2],
    }
    transforms = {
        "GRADE_CHANGE": alter_grade,
        "Y_CLOSE_CONFUSION": alter_y_close,
        "AL_AR_SWAP": alter_direction,
        "DROP_DUPLICATE_REORDER": alter_order,
    }
    detection = {
        "GRADE_CHANGE": ("LOCAL_CARD_READBACK", "Gradzeichen laut lesen; E, EE und EEE vergleichen."),
        "Y_CLOSE_CONFUSION": ("LOCAL_CARD_READBACK", "Prüfen, ob der Posten weiterläuft oder der Schritt wirklich schließt."),
        "AL_AR_SWAP": ("READBACK_PLUS_VISIBLE_OWNER", "Quelle und Ziel laut benennen und an der sichtbaren Station zeigen."),
        "DROP_DUPLICATE_REORDER": ("MASTER_EXEMPLAR_COMPARISON", "Kartenanzahl und Reihenfolge gegen die Vorlage zurückzählen."),
    }
    exercises = []
    for family, pool in pools.items():
        for row in pool[:8]:
            corrupted, consequence = transforms[family](row["atom_sequence"])
            channel, repair = detection[family]
            exercises.append({
                "exercise_id": f"EX-{len(exercises)+1:02d}",
                "error_family": family,
                "unit_id": row["unit_id"],
                "page": row["page"],
                "owner_or_namespace": row["owner_or_namespace"],
                "correct_surface_sequence": bare_copy[row["unit_id"]]["rendered_surface_sequence"],
                "correct_atom_sequence": row["atom_sequence"],
                "red_ink_corrupted_atom_sequence": corrupted,
                "wrong_readback_consequence_de": consequence,
                "detection_channel": channel,
                "master_repair_de": repair,
                "correct_working_reading_de": row["fluent_working_reading_de"],
                "new_surface_invented": "NO_RED_INK_ATOM_DRILL_ONLY",
            })
    write_tsv(OUT / "SIXTIETH_32_CORRECTION_EXERCISES.tsv", exercises)

    rules = [
        ("R01", "GRADE_CHANGE", "E/EE/EEE einzeln laut lesen", "LOCAL_CARD_READBACK"),
        ("R02", "GRADE_CHANGE", "Grad nie aus der Länge des ganzen Wortbildes raten", "LOCAL_CARD_READBACK"),
        ("R03", "Y_CLOSE_CONFUSION", "Y hält den Posten; nur gelernte Schlusskarte schließt", "LOCAL_CARD_READBACK"),
        ("R04", "Y_CLOSE_CONFUSION", "Zeilenende darf fehlenden Schluss nicht ersetzen", "LOCAL_CARD_READBACK"),
        ("R05", "AL_AR_SWAP", "AL mit Finger am Ziel, AR mit Finger an der Quelle lesen", "READBACK_PLUS_VISIBLE_OWNER"),
        ("R06", "AL_AR_SWAP", "bei unklarer Zeichnung nicht aus Gewohnheit umdrehen", "READBACK_PLUS_VISIBLE_OWNER"),
        ("R07", "DROP_DUPLICATE_REORDER", "jede Karte beim Rücklesen abhaken", "MASTER_EXEMPLAR_COMPARISON"),
        ("R08", "DROP_DUPLICATE_REORDER", "wiederholte Karte nur behalten, wenn sie in der Vorlage zweimal steht", "MASTER_EXEMPLAR_COMPARISON"),
    ]
    rule_rows = [
        {"rule_id": rule_id, "error_family": family, "master_rule_de": text, "detection_channel": channel}
        for rule_id, family, text, channel in rules
    ]
    write_tsv(OUT / "SIXTIETH_8_MASTER_CORRECTION_RULES.tsv", rule_rows)

    book = [
        "# Rotstiftbuch des Meisters",
        "",
        "Vier Fehlerarten werden je achtmal geübt. Die rote Atomfolge ist absichtlich",
        "falsch; es wird keine neue Manuskriptoberfläche gezeichnet.",
        "",
    ]
    for family in pools:
        book.extend([f"## {family}", ""])
        for row in (item for item in exercises if item["error_family"] == family):
            book.append(
                f"- {row['unit_id']}: `{row['correct_atom_sequence']}` → falsch "
                f"`{row['red_ink_corrupted_atom_sequence']}`; {row['wrong_readback_consequence_de']}."
            )
        book.append("")
    (OUT / "SIXTIETH_MASTER_CORRECTION_BOOK.md").write_text("\n".join(book).rstrip() + "\n", encoding="utf-8")

    summary = {
        "status": "CONSISTENT",
        "counts": {
            "error_families": len(pools),
            "correction_exercises": len(exercises),
            "master_rules": len(rule_rows),
            "local_readback_exercises": sum(row["detection_channel"] == "LOCAL_CARD_READBACK" for row in exercises),
            "owner_assisted_exercises": sum(row["detection_channel"] == "READBACK_PLUS_VISIBLE_OWNER" for row in exercises),
            "exemplar_required_exercises": sum(row["detection_channel"] == "MASTER_EXEMPLAR_COMPARISON" for row in exercises),
            "new_surfaces": 0,
        },
        "sources": {str(path.relative_to(ROOT)): sha256(path) for path in (UNITS, COPIES)},
    }
    (OUT / "BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
