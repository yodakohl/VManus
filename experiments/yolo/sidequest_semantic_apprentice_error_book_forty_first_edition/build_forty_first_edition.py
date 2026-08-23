#!/usr/bin/env python3
"""Build a concrete apprentice error-and-repair copybook from real statements."""

from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
EXPLICIT = ROOT / "experiments/yolo/sidequest_semantic_explicit_sentences_fortieth_edition/FORTIETH_116_EXPLICIT_SENTENCES.tsv"
MEMORY = ROOT / "experiments/yolo/sidequest_semantic_scribe_memory_thirty_ninth_edition/THIRTY_NINTH_116_MEMORY_TRANSITIONS.tsv"


RULES = [
    {
        "error_code": "E01_WRONG_OWNER",
        "teaching_axis": "OWNER",
        "wrong_rule_de": "beim sichtbaren Stationswechsel den alten Bildbesitzer weiterführen",
        "concrete_failure_de": "die richtige Handlung wird am falschen Becken, Pflanzenteil oder Gerät ausgeführt",
        "repair_rule_de": "OWNER beim sichtbaren Wechsel umsetzen und TARGET neu prüfen",
    },
    {
        "error_code": "E02_ACTIVE_PREVIOUS_SWAP",
        "teaching_axis": "ACTIVE_PREVIOUS",
        "wrong_rule_de": "den Vorposten statt des laufenden Postens bearbeiten",
        "concrete_failure_de": "eine bereits abgelegte Fraktion wird erneut behandelt und der neue Posten bleibt liegen",
        "repair_rule_de": "ACTIVE und PREVIOUS als zwei getrennte Kerben führen",
    },
    {
        "error_code": "E03_SOURCE_TARGET_SWAP",
        "teaching_axis": "AR_AL",
        "wrong_rule_de": "Quelle AR und Ziel AL vertauschen",
        "concrete_failure_de": "der Schreiber entnimmt aus der Zielschale oder bringt den Posten an die Vorratsquelle",
        "repair_rule_de": "AR immer als Ausgangsadresse, AL immer als Zieladresse lesen",
    },
    {
        "error_code": "E04_QUANTITY_CLASS_SWAP",
        "teaching_axis": "AIIN_AIN_IIN",
        "wrong_rule_de": "Sollwert, Portion und Prozessstufe als dieselbe Mengenangabe behandeln",
        "concrete_failure_de": "eine Portion wird zur Stufe oder ein Sollstand zur abzutrennenden Menge",
        "repair_rule_de": "AIIN=Sollwert, AIN=Portion und IIN=Stufe getrennt halten",
    },
    {
        "error_code": "E05_ORDER_SWAP",
        "teaching_axis": "OL_OT",
        "wrong_rule_de": "Fortsetzung OL und nächsten Posten OT vertauschen",
        "concrete_failure_de": "der laufende Ansatz wird zu früh verlassen oder ein neuer Posten nie begonnen",
        "repair_rule_de": "OL behält den Gang, OT öffnet den folgenden Gang",
    },
    {
        "error_code": "E06_GRADE_SWAP",
        "teaching_axis": "E_EE_EEE",
        "wrong_rule_de": "kurzen, längeren und vollen Grad gleich ausführen",
        "concrete_failure_de": "Kontakt, Halten oder Tabellenstufe dauert falsch lang",
        "repair_rule_de": "E kurz, EE länger, EEE vollständig nur innerhalb der lizenzierten Familie",
    },
    {
        "error_code": "E07_CURRENT_CLOSE_SWAP",
        "teaching_axis": "Y_CLOSE",
        "wrong_rule_de": "laufenden Posten Y und lokale Schlusskarte vertauschen",
        "concrete_failure_de": "der Arbeitsposten wird vorzeitig geschlossen oder eine fertige Zelle bleibt offen",
        "repair_rule_de": "Y hält ACTIVE verfügbar; nur die registrierte Schlusskarte beendet die Zelle",
    },
    {
        "error_code": "E08_RENDERER_AS_WORD",
        "teaching_axis": "SCRIBE_FRAME",
        "wrong_rule_de": "q/s/ch/d/t-Schreiberrahmen als zusätzliche Handlung lesen",
        "concrete_failure_de": "vor die echte Karte wird ein nie diktierter Arbeitsschritt eingeschoben",
        "repair_rule_de": "zuerst registrierte Oberfläche zum Kartenkörper normalisieren, dann Bedeutung lesen",
    },
]


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


def tokens(atom_sequence: str) -> set[str]:
    return {part for group in atom_sequence.split(" | ") for part in group.split("+")}


def replace_atoms(atom_sequence: str, mapping: dict[str, str]) -> str:
    groups = []
    for group in atom_sequence.split(" | "):
        groups.append("+".join(mapping.get(part, part) for part in group.split("+")))
    return " | ".join(groups)


def varied_pick(candidates: list[dict[str, str]], used: set[str], count: int = 4) -> list[dict[str, str]]:
    chosen: list[dict[str, str]] = []
    records: set[str] = set()
    for row in candidates:
        if row["statement_id"] in used or row["record_id"] in records:
            continue
        chosen.append(row)
        records.add(row["record_id"])
        used.add(row["statement_id"])
        if len(chosen) == count:
            return chosen
    for row in candidates:
        if row["statement_id"] in used:
            continue
        chosen.append(row)
        used.add(row["statement_id"])
        if len(chosen) == count:
            return chosen
    raise RuntimeError(f"could not select {count} distinct examples")


def main() -> None:
    explicit = read_tsv(EXPLICIT)
    memory = {row["statement_id"]: row for row in read_tsv(MEMORY)}
    used: set[str] = set()
    selections: dict[str, list[dict[str, str]]] = {}
    selections["E01_WRONG_OWNER"] = varied_pick([
        row for row in explicit
        if memory[row["statement_id"]]["visible_owner_operation"] in {"VOR_SATZ_UMSCHALTEN", "IM_SATZ_UMSCHALTEN"}
    ], used)
    selections["E02_ACTIVE_PREVIOUS_SWAP"] = varied_pick([
        row for row in explicit
        if row["previous_expansion_de"] != "NICHT_BENÖTIGT" and row["active_expansion_de"] != row["previous_expansion_de"]
    ], used)
    selections["E03_SOURCE_TARGET_SWAP"] = varied_pick([
        row for row in explicit if tokens(row["atom_sequence"]) & {"AR", "AL"}
    ], used)
    selections["E04_QUANTITY_CLASS_SWAP"] = varied_pick([
        row for row in explicit if tokens(row["atom_sequence"]) & {"AIIN", "AIN", "IIN"}
    ], used)
    selections["E05_ORDER_SWAP"] = varied_pick([
        row for row in explicit if tokens(row["atom_sequence"]) & {"OL", "OT"}
    ], used)
    selections["E06_GRADE_SWAP"] = varied_pick([
        row for row in explicit if tokens(row["atom_sequence"]) & {"E", "EE", "EEE"}
    ], used)
    selections["E07_CURRENT_CLOSE_SWAP"] = varied_pick([
        row for row in explicit if tokens(row["atom_sequence"]) & {"Y", "CLOSE"}
    ], used)
    selections["E08_RENDERER_AS_WORD"] = varied_pick([
        row for row in explicit if any(surface.startswith(("q", "s", "ch", "d", "t")) for surface in row["surface_sequence"].split())
    ], used)

    rule_by_code = {row["error_code"]: row for row in RULES}
    errors: list[dict[str, object]] = []
    error_serial = 0
    for code, selected in selections.items():
        rule = rule_by_code[code]
        for row in selected:
            error_serial += 1
            mem = memory[row["statement_id"]]
            atom = row["atom_sequence"]
            if code == "E01_WRONG_OWNER":
                wrong_atom = atom
                wrong_choice = f"OWNER={mem['visible_owner_pre']} statt {mem['visible_owner_post']}"
            elif code == "E02_ACTIVE_PREVIOUS_SWAP":
                wrong_atom = atom
                wrong_choice = f"ACTIVE={row['previous_expansion_de']} statt {row['active_expansion_de']}"
            elif code == "E03_SOURCE_TARGET_SWAP":
                wrong_atom = replace_atoms(atom, {"AR": "AL!", "AL": "AR!"})
                wrong_choice = "AR↔AL"
            elif code == "E04_QUANTITY_CLASS_SWAP":
                wrong_atom = replace_atoms(atom, {"AIIN": "AIN!", "AIN": "IIN!", "IIN": "AIIN!"})
                wrong_choice = "AIIN→AIN, AIN→IIN oder IIN→AIIN"
            elif code == "E05_ORDER_SWAP":
                wrong_atom = replace_atoms(atom, {"OL": "OT!", "OT": "OL!"})
                wrong_choice = "OL↔OT"
            elif code == "E06_GRADE_SWAP":
                wrong_atom = replace_atoms(atom, {"E": "EE!", "EE": "EEE!", "EEE": "E!"})
                wrong_choice = "E→EE, EE→EEE oder EEE→E"
            elif code == "E07_CURRENT_CLOSE_SWAP":
                wrong_atom = replace_atoms(atom, {"Y": "CLOSE!", "CLOSE": "Y!"})
                wrong_choice = "Y↔CLOSE"
            else:
                wrong_atom = "EXTRA_WRAPPER_ACTION! | " + atom
                wrong_choice = "Schreiberrahmen als eigenes Verb"
            errors.append({
                "error_serial": error_serial,
                "error_code": code,
                "teaching_axis": rule["teaching_axis"],
                "statement_id": row["statement_id"],
                "record_id": row["record_id"],
                "page": row["page"],
                "surface_sequence": row["surface_sequence"],
                "correct_atom_sequence": atom,
                "wrong_atom_or_register_reading": wrong_atom,
                "wrong_choice_de": wrong_choice,
                "concrete_wrong_result_de": rule["concrete_failure_de"],
                "correct_full_sentence_de": row["fully_explicit_apprentice_sentence_de"],
                "repair_rule_de": rule["repair_rule_de"],
                "copying_exercise_de": f"Lies {row['statement_id']} erneut; nenne zuerst {rule['teaching_axis']}, dann sprich nur die korrigierte Folge.",
            })
    write_tsv(OUT / "FORTY_FIRST_32_APPRENTICE_ERRORS.tsv", errors)

    rule_rows = []
    by_code = Counter(row["error_code"] for row in errors)
    for rule in RULES:
        rule_rows.append({
            **rule,
            "real_examples": by_code[rule["error_code"]],
            "teaching_order": len(rule_rows) + 1,
            "master_mnemonic_de": {
                "E01_WRONG_OWNER": "Erst schauen, dann schreiben.",
                "E02_ACTIVE_PREVIOUS_SWAP": "Der Stein ist jetzt; die Kerbe war vorher.",
                "E03_SOURCE_TARGET_SWAP": "AR heraus, AL hinan.",
                "E04_QUANTITY_CLASS_SWAP": "Wert, Teil, Stufe sind drei Dinge.",
                "E05_ORDER_SWAP": "OL bleibt, OT springt.",
                "E06_GRADE_SWAP": "Ein Strich kurz, zwei länger, drei voll.",
                "E07_CURRENT_CLOSE_SWAP": "Y bleibt in der Hand; Schluss legt ab.",
                "E08_RENDERER_AS_WORD": "Die Handform spricht nicht mit.",
            }[rule["error_code"]],
        })
    write_tsv(OUT / "FORTY_FIRST_EIGHT_ERROR_RULES.tsv", rule_rows)

    lines = [
        "# Fehlerbuch für den Werkstattlehrling",
        "",
        "Jede Lektion zeigt vier echte Aussagen. Der Meister lässt genau einen Fehler zu,",
        "lässt den Lehrling die konkrete Folge benennen und setzt dann die kurze Regel daneben.",
        "",
    ]
    for rule in rule_rows:
        lines.extend([
            f"## {rule['error_code']} — {rule['teaching_axis']}",
            "",
            f"Merksatz: **{rule['master_mnemonic_de']}**",
            "",
            f"Fehler: {rule['wrong_rule_de']}. Folge: {rule['concrete_failure_de']}. Reparatur: {rule['repair_rule_de']}.",
            "",
        ])
        for error in (row for row in errors if row["error_code"] == rule["error_code"]):
            lines.extend([
                f"- `{error['statement_id']}` · sichtbar `{error['surface_sequence']}`",
                f"  - falsche Wahl: {error['wrong_choice_de']}",
                f"  - richtig: {error['correct_atom_sequence']}",
            ])
        lines.append("")
    (OUT / "FORTY_FIRST_CORRECTION_COPYBOOK.md").write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")

    summary = {
        "status": "CONSISTENT",
        "counts": {
            "error_rules": len(rule_rows),
            "worked_errors": len(errors),
            "distinct_statements": len({row["statement_id"] for row in errors}),
            "records_represented": len({row["record_id"] for row in errors}),
            "pages_represented": len({row["page"] for row in errors}),
            "examples_per_rule": dict(by_code),
        },
        "sources": {str(path.relative_to(ROOT)): sha256(path) for path in (EXPLICIT, MEMORY)},
    }
    (OUT / "BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
