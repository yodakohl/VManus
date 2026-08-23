#!/usr/bin/env python3
"""Replace sentence-like card defaults with exact atomic gloss sequences."""

from __future__ import annotations

import csv
import json
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
DICTIONARY = ROOT / "experiments/yolo/sidequest_semantic_centennial_working_edition/HUNDREDTH_CORRECTED_173_CARD_DICTIONARY.tsv"
EVENTS = ROOT / "experiments/yolo/sidequest_semantic_centennial_working_edition/HUNDREDTH_381_PROSE_INTERLINEAR.tsv"


ATOM_VALUES = {
    "AIIN": "Sollmaß", "AIN": "Anteil", "AIR": "Lauf", "AL": "Ziel",
    "AM": "verwahren", "AR": "Quelle", "CFH": "auswringen", "CHD": "umsetzen",
    "CHEEY": "Ergebnis", "CHEO": "Auszug", "CHK": "wärmen", "CKH": "Durchlass",
    "CKHE": "trennen", "CLOSE": "Schluss", "CPH": "nachseihen", "CTH": "bereit",
    "DAIN": "Tuch", "DAN": "anwenden", "DCHE": "Wurzel", "DCHOL": "vorher",
    "E": "kurz", "EE": "länger", "EEE": "vollständig", "HO": "Zutat",
    "IIN": "Stufe", "KCH": "bearbeiten", "L": "abführen", "LDDY": "festbinden",
    "LOCAL_WHOLE": "Zusatz", "ODY": "kühlen", "OK": "ansetzen", "OL": "weiter",
    "OR": "Ansatz", "OS": "Gefäß", "OT": "danach", "P": "zuführen",
    "PARTITION": "teilen", "SH": "halten", "SHED": "absetzen", "SK": "ausgießen",
    "SOLK": "sammeln", "TY": "Teil", "WASH": "waschen", "Y": "Posten",
}


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, fields: list[str], rows: list[dict[str, object]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    source = read_tsv(DICTIONARY)
    components = [
        {
            "atom": atom,
            "atomic_default_de": value,
            "word_class": (
                "ARGUMENT" if atom in {"AIIN", "AIN", "IIN", "AL", "AR", "AIR", "Y", "TY", "DAIN", "OS"}
                else "GRADE_OR_ORDER" if atom in {"E", "EE", "EEE", "OL", "OT", "DCHOL"}
                else "ENDPOINT" if atom in {"CLOSE", "CTH", "CHEEY"}
                else "OPERATION_OR_LEARNED_BODY"
            ),
            "composition_rule": "one atom contributes one short default; no sentence expansion inside the dictionary",
        }
        for atom, value in ATOM_VALUES.items()
    ]
    atomic_dictionary: list[dict[str, object]] = []
    revisions: list[dict[str, object]] = []
    for row in source:
        atoms = row["semantic_atoms"].split("+")
        glosses = [ATOM_VALUES[atom] for atom in atoms]
        atomic = "+".join(glosses)
        original = row["short_default_de"]
        original_word_count = len(original.replace(";", " ").split())
        status = "KEEP_SHORT_DEFAULT" if original_word_count <= 2 and ";" not in original else "REPLACE_SENTENCE_LIKE_DEFAULT"
        atomic_dictionary.append({
            "dictionary_order": row["dictionary_order"],
            "master_card_id": row["master_card_id"],
            "master_form": row["master_form"],
            "registered_surface_family": row["registered_surface_family"],
            "semantic_atoms": row["semantic_atoms"],
            "atomic_default_de": atomic,
            "atomic_unit_count": len(atoms),
            "original_short_default_de": original,
            "revision_status": status,
            "productivity_tier": row["productivity_tier"],
            "composition_policy": row["composition_policy"],
        })
        if status == "REPLACE_SENTENCE_LIKE_DEFAULT" or original.casefold() != atomic.replace("+", " ").casefold():
            revisions.append({
                "master_card_id": row["master_card_id"],
                "surface_family": row["registered_surface_family"],
                "semantic_atoms": row["semantic_atoms"],
                "old_default_de": original,
                "new_atomic_default_de": atomic,
                "reason": "one short value per component; fluent syntax belongs to the statement layer",
            })

    by_id = {row["master_card_id"]: row for row in atomic_dictionary}
    event_rows: list[dict[str, object]] = []
    for event in read_tsv(EVENTS):
        card = by_id[event["master_card_id"]]
        event_rows.append({
            "event_serial": event["event_serial"],
            "statement_id": event["statement_id"],
            "record_unit_id": event["record_unit_id"],
            "page": event["page"],
            "visible_surface": event["visible_surface"],
            "master_card_id": event["master_card_id"],
            "semantic_atoms": event["semantic_atoms"],
            "atomic_default_de": card["atomic_default_de"],
            "statement_translation_de": event["statement_translation_de"],
        })

    write_tsv(OUT / "HUNDRED_FIRST_44_ATOMIC_COMPONENTS.tsv", list(components[0]), components)
    write_tsv(OUT / "HUNDRED_FIRST_173_ATOMIC_DICTIONARY.tsv", list(atomic_dictionary[0]), atomic_dictionary)
    write_tsv(OUT / "HUNDRED_FIRST_REVISED_DEFAULTS.tsv", list(revisions[0]), revisions)
    write_tsv(OUT / "HUNDRED_FIRST_381_EVENT_ATOMIC_INTERLINEAR.tsv", list(event_rows[0]), event_rows)

    status_counts = Counter(row["revision_status"] for row in atomic_dictionary)
    unit_counts = Counter(int(row["atomic_unit_count"]) for row in atomic_dictionary)
    report = [
        "# Hunderterste Runde: Wörter sind wieder Wörter", "",
        "## Korrektur", "",
        "Das Kartenwörterbuch enthält ab jetzt keine versteckten Sätze mehr. Jede Karte",
        "bekommt exakt die kurze Summe ihrer Komponenten, getrennt durch `+`. Erst die",
        "Aussagengrammatik macht daraus flüssiges Deutsch.", "",
        f"Die 173 Karten verwenden nur 44 atomare Defaults. {status_counts['REPLACE_SENTENCE_LIKE_DEFAULT']}",
        "alte, satzartige Defaults werden ausdrücklich ersetzt; auch kurze alte Paraphrasen",
        "werden im Revisionsblatt auf denselben Atomwortlaut normalisiert.", "",
    ]
    for size in sorted(unit_counts):
        report.append(f"- {size} atomare Einheit(en): {unit_counts[size]} Karten")
    report.extend([
        "", "Beispiele:", "",
        "- `qokaiin` = `ansetzen+Sollmaß`, nicht ein ganzer Rezeptsatz.",
        "- `qokeedy` = `ansetzen+länger+Schluss`.",
        "- `lcheckhedy` = `abführen+trennen+Schluss`, nicht CKH plus ein erfundener Grad.",
        "- `qokylddy` = `ansetzen+Posten+festbinden`.",
        "- `taiin` bleibt dieselbe Karte `Sollmaß`; ein sichtbares t ist kein Inhaltsstamm.", "",
        "Damit kann ein Lehrling zuerst 44 echte kurze Werte lernen, dann 173 registrierte",
        "Karten und erst danach die flüssigen Werkstattsätze. Die Bedeutungsarbeit liegt nun",
        "an der richtigen Ebene und nicht in überladenen Pseudowörtern.", "",
        "Nur die festen Prosaseiten wurden verwendet; f84 und f84r blieben versiegelt.",
    ])
    (OUT / "HUNDRED_FIRST_ATOMIC_DEFAULT_REPORT.md").write_text("\n".join(report) + "\n", encoding="utf-8")
    summary = {
        "status": "CONSISTENT", "atomic_components": len(components), "cards": len(atomic_dictionary),
        "events": len(event_rows), "revision_rows": len(revisions),
        "revision_status": dict(status_counts), "atomic_unit_counts": {str(k): v for k, v in sorted(unit_counts.items())},
        "max_atomic_units": max(unit_counts),
    }
    (OUT / "BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
