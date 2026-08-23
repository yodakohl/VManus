#!/usr/bin/env python3
"""Build the practical four-slot memory slate for the fixed ten-page workshop."""

from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
TRANSITIONS = ROOT / "experiments/yolo/sidequest_theory_candidates_v62/V62_SELECTED_116_REGISTER_TRANSITIONS.tsv"
STATEMENTS = ROOT / "experiments/yolo/sidequest_semantic_owner_filled_twenty_first_edition/TWENTY_FIRST_116_OWNER_FILLED_PROSE.tsv"
PROGRAMS = ROOT / "experiments/yolo/sidequest_semantic_process_macros_thirty_eighth_edition/THIRTY_EIGHTH_116_MACRO_PROGRAMS.tsv"
WORKED = ROOT / "experiments/yolo/sidequest_semantic_worked_dossier_thirty_seventh_edition/THIRTY_SEVENTH_26_WORK_STEPS.tsv"


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: list[dict[str, object]], fields: list[str] | None = None) -> None:
    if not rows:
        raise ValueError(f"refusing to write empty table: {path}")
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields or list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def parse_state(text: str) -> dict[str, str]:
    result: dict[str, str] = {}
    for part in text.split(";"):
        key, value = part.split("=", 1)
        result[key] = value
    return result


def short_slot(value: str) -> str:
    if value == "UNSET":
        return "LEER"
    value = value.replace("ACTIVE_ITEM/PREPARATION", "POSTEN")
    value = value.replace("TARGET/STATION", "ZIEL")
    value = value.replace("PREVIOUS_ITEM", "VORIGES")
    return value


def atom_tokens(atom_sequence: str) -> set[str]:
    tokens: set[str] = set()
    for group in atom_sequence.split(" | "):
        tokens.update(part.strip() for part in group.split("+") if part.strip())
    return tokens


def cue_phrase(tokens: set[str]) -> str:
    cues = []
    for token, phrase in (
        ("OT", "NÄCHSTER_POSTEN"),
        ("OL", "FORTSETZEN"),
        ("AR", "QUELLE_SICHTBAR"),
        ("AL", "ZIEL_SICHTBAR"),
        ("Y", "AKTUELLER_POSTEN"),
        ("AIIN", "SOLLWERT"),
        ("AIN", "PORTION"),
        ("IIN", "STUFE"),
        ("CLOSE", "ZELLE_SCHLIESSEN"),
    ):
        if token in tokens:
            cues.append(phrase)
    return "|".join(cues) if cues else "NUR_GELERNTE_KARTE_ODER_LOKALER_INHALT"


def main() -> None:
    transitions = read_tsv(TRANSITIONS)
    statements = read_tsv(STATEMENTS)
    programs = read_tsv(PROGRAMS)
    worked = read_tsv(WORKED)
    by_transition = {row["statement_id"]: row for row in transitions}
    by_program = {row["statement_id"]: row for row in programs}
    by_statement = {row["statement_id"]: row for row in statements}
    if not (len(by_transition) == len(by_program) == len(by_statement) == 116):
        raise RuntimeError("expected the same 116 statements in all three sources")

    memory_rows: list[dict[str, object]] = []
    prior_record = ""
    prior_visible_owner = "LEER"
    owner_ops: Counter[str] = Counter()
    slot_ops: dict[str, Counter[str]] = {
        "ACTIVE": Counter(), "TARGET": Counter(), "PREVIOUS": Counter()
    }
    for statement in sorted(statements, key=lambda row: int(row["unit_serial"])):
        sid = statement["statement_id"]
        trans = by_transition[sid]
        program = by_program[sid]
        pre = parse_state(trans["pre_state"])
        post = parse_state(trans["post_state"])
        owner_parts = statement["image_owner"].split("|")
        first_owner, final_owner = owner_parts[0], owner_parts[-1]
        if statement["record_id"] != prior_record:
            visible_owner_pre = "LEER"
            owner_operation = "AUS_BILD_SETZEN"
        elif len(owner_parts) > 1:
            visible_owner_pre = prior_visible_owner
            owner_operation = "IM_SATZ_UMSCHALTEN"
        elif prior_visible_owner != first_owner:
            visible_owner_pre = prior_visible_owner
            owner_operation = "VOR_SATZ_UMSCHALTEN"
        else:
            visible_owner_pre = prior_visible_owner
            owner_operation = "MITFÜHREN"
        owner_ops[owner_operation] += 1
        slot_ops["ACTIVE"][trans["active_item_preparation_operation"]] += 1
        slot_ops["TARGET"][trans["target_station_operation"]] += 1
        slot_ops["PREVIOUS"][trans["previous_item_operation"]] += 1
        tokens = atom_tokens(statement["atom_sequence"])
        pre_values = [visible_owner_pre, pre["ACTIVE_ITEM/PREPARATION"], pre["TARGET/STATION"], pre["PREVIOUS_ITEM"]]
        post_values = [final_owner, post["ACTIVE_ITEM/PREPARATION"], post["TARGET/STATION"], post["PREVIOUS_ITEM"]]
        memory_rows.append({
            "sequence": statement["unit_serial"],
            "statement_id": sid,
            "record_id": statement["record_id"],
            "page": statement["page"],
            "statement_ordinal": trans["statement_ordinal_in_record"],
            "entry_boundary": trans["entry_boundary_class"],
            "exit_boundary": trans["exit_boundary_class"],
            "visible_owner_pre": visible_owner_pre,
            "visible_owner_operation": owner_operation,
            "visible_owner_post": final_owner,
            "owner_break_inside_statement": statement["owner_break_inside_statement"],
            "active_pre": short_slot(pre["ACTIVE_ITEM/PREPARATION"]),
            "active_operation": trans["active_item_preparation_operation"],
            "active_post": short_slot(post["ACTIVE_ITEM/PREPARATION"]),
            "target_pre": short_slot(pre["TARGET/STATION"]),
            "target_operation": trans["target_station_operation"],
            "target_post": short_slot(post["TARGET/STATION"]),
            "previous_pre": short_slot(pre["PREVIOUS_ITEM"]),
            "previous_operation": trans["previous_item_operation"],
            "previous_post": short_slot(post["PREVIOUS_ITEM"]),
            "memory_slots_filled_pre": sum(value not in {"LEER", "UNSET"} for value in pre_values),
            "memory_slots_filled_post": sum(value not in {"LEER", "UNSET"} for value in post_values),
            "visible_card_cues": cue_phrase(tokens),
            "surface_sequence": statement["surface_sequence"],
            "atom_sequence": statement["atom_sequence"],
            "macro_program": program["macro_program"],
            "literal_card_reading_de": statement["literal_card_reading_de"],
            "expanded_workshop_reading_de": statement["selected_concrete_reading_de"],
            "scribe_memory_instruction_de": (
                f"Besitzer {owner_operation.lower().replace('_', ' ')}: {final_owner}; "
                f"Posten {trans['active_item_preparation_operation'].lower()}: {short_slot(post['ACTIVE_ITEM/PREPARATION'])}; "
                f"Ziel {trans['target_station_operation'].lower()}: {short_slot(post['TARGET/STATION'])}; "
                f"Voriges {trans['previous_item_operation'].lower()}: {short_slot(post['PREVIOUS_ITEM'])}."
            ),
        })
        prior_record = statement["record_id"]
        prior_visible_owner = final_owner

    write_tsv(OUT / "THIRTY_NINTH_116_MEMORY_TRANSITIONS.tsv", memory_rows)

    slot_rows = [
        {
            "slot": "OWNER",
            "what_the_scribe_remembers": "welches Bildobjekt oder welche lokale Station die stillen Substantive liefert",
            "physical_aid": "linke Randmarke oder Finger am Bild",
            "set_rule": "am Recordanfang aus dem Bild setzen; bei sichtbarem Szenenwechsel umschalten",
            "carry_rule": "über Felder und Zeilen mitführen",
            "clear_rule": "erst am Recordende; Ziel bei Stationswechsel neu prüfen",
            "operation_counts": ";".join(f"{key}={value}" for key, value in sorted(owner_ops.items())),
        },
        {
            "slot": "ACTIVE",
            "what_the_scribe_remembers": "der gerade bearbeitete Posten oder Ansatz",
            "physical_aid": "ein verschiebbarer Stein oder Wachstafelstrich",
            "set_rule": "beim ersten oder nächsten Posten setzen",
            "carry_rule": "bei Y oder fortgesetztem Gang beibehalten",
            "clear_rule": "nicht durch Zeilenende oder bloßen Zellschluss; beim echten neuen Posten ersetzen",
            "operation_counts": ";".join(f"{key}={value}" for key, value in sorted(slot_ops["ACTIVE"].items())),
        },
        {
            "slot": "TARGET",
            "what_the_scribe_remembers": "die örtlich bezeichnete Zielstelle, Öffnung, Schale oder Tabellenzelle",
            "physical_aid": "zweite Randkerbe oder Zeigefinger auf der Zielstation",
            "set_rule": "durch AL/Zielkarte oder sichtbare lokale Stelle setzen",
            "carry_rule": "nur solange derselbe örtliche Gang läuft",
            "clear_rule": "bei neuem Parallelgang, neuer Klausel oder Stationswechsel löschen",
            "operation_counts": ";".join(f"{key}={value}" for key, value in sorted(slot_ops["TARGET"].items())),
        },
        {
            "slot": "PREVIOUS",
            "what_the_scribe_remembers": "genau den unmittelbar zuvor abgelegten oder verdrängten Posten",
            "physical_aid": "eine einzelne Kerbe; keine Liste früherer Posten",
            "set_rule": "alten ACTIVE-Wert beim Wechsel hierher schieben",
            "carry_rule": "bis VORIGES/OL ihn abruft oder ein neuer Posten ihn überschreibt",
            "clear_rule": "am Recordende und bei ausdrücklich unabhängigem Neubeginn",
            "operation_counts": ";".join(f"{key}={value}" for key, value in sorted(slot_ops["PREVIOUS"].items())),
        },
    ]
    write_tsv(OUT / "THIRTY_NINTH_FOUR_MEMORY_SLOTS.tsv", slot_rows)

    memory_by_id = {row["statement_id"]: row for row in memory_rows}
    worked_rows = []
    for row in worked:
        mem = memory_by_id[row["statement_id"]]
        worked_rows.append({
            "job_step": row["job_step"],
            "phase": row["phase"],
            "statement_id": row["statement_id"],
            "page": row["page"],
            "owner_pre": mem["visible_owner_pre"],
            "owner_operation": mem["visible_owner_operation"],
            "owner_post": mem["visible_owner_post"],
            "active_pre": mem["active_pre"],
            "active_operation": mem["active_operation"],
            "active_post": mem["active_post"],
            "target_pre": mem["target_pre"],
            "target_operation": mem["target_operation"],
            "target_post": mem["target_post"],
            "previous_pre": mem["previous_pre"],
            "previous_operation": mem["previous_operation"],
            "previous_post": mem["previous_post"],
            "visible_card_cues": mem["visible_card_cues"],
            "surface_sequence": row["surface_sequence"],
            "macro_program": mem["macro_program"],
            "master_dictation_de": row["master_dictation_de"],
            "scribe_readback_de": row["apprentice_readback_de"],
        })
    write_tsv(OUT / "THIRTY_NINTH_26_WORKED_JOB_MEMORY_TRACE.tsv", worked_rows)

    max_load = max(int(row["memory_slots_filled_post"]) for row in memory_rows)
    internal_owner_breaks = sum(row["owner_break_inside_statement"] == "YES" for row in memory_rows)
    lines = [
        "# Die Vierfach-Merktafel des Schreibers",
        "",
        "Der Schreiber muss nicht einen langen deutschen Satz im Kopf verschlüsseln. Er hält vier",
        "kleine recordlokale Werte fest: Bildbesitzer, laufender Posten, Zielstelle und Vorposten.",
        "Quelle, Maß, Stufe und Abschluss stehen dagegen normalerweise sichtbar auf der Karte und",
        "brauchen keinen fünften dauerhaften Speicherplatz.",
        "",
        "## Handregel",
        "",
        "1. Setze beim ersten Feld den Bildbesitzer.",
        "2. Lege den aktuellen Arbeitsgegenstand auf ACTIVE.",
        "3. Wenn eine Zielstelle genannt oder gezeigt wird, setze TARGET.",
        "4. Beim Wechsel eines Postens schiebe den alten ACTIVE-Wert genau einmal auf PREVIOUS.",
        "5. Ein Zeilenende ändert keinen der vier Werte.",
        "6. CLOSE beendet die lokale Zelle, löscht aber die Merktafel nicht von selbst.",
        "7. Bei einem sichtbaren Stationswechsel wechsle OWNER und prüfe TARGET neu.",
        "8. Erst am Recordende werden alle vier Zeichen abgewischt.",
        "",
        "## Praktische Form",
        "",
        "Ein Lehrmeister kann die vier Werte mit vier Kerben auf einer kleinen Wachstafel führen:",
        "`O | A | T | P`. Es wird nur die anonyme laufende Identität notiert, nicht das ganze Wort.",
        "Dadurch können mehrere Hände dieselbe Kurzschrift lernen, obwohl die konkrete Pflanze,",
        "Schale oder Sternstelle allein aus Bild und Exemplar kommt.",
        "",
        "## Umfang",
        "",
        f"Die Tafel ist für alle {len(memory_rows)} Proseaussagen ausgeschrieben. Die höchste gleichzeitige",
        f"Belegung beträgt {max_load}/4 Werte. {internal_owner_breaks} Aussagen wechseln ihren sichtbaren Besitzer",
        "innerhalb derselben Aussage; dort muss der Schreiber den Wechsel mitten im Arbeitsgang vollziehen.",
        "Der vollständige D2-Musterauftrag zeigt dieselbe Tafel über 26 aufeinanderfolgende Schritte.",
        "",
        "## Was diese Runde verbessert",
        "",
        "Die früheren langen Lesungen werden nun als sichtbare Karten plus vier kurze Gedächtniswerte",
        "erklärt. Das macht Ellipsen wie ‚weiterführen‘, ‚dorthin‘ oder ‚davon‘ ausführbar, ohne diese",
        "ausgeschriebenen Referenten in einen einzelnen Wortstamm hineinzupacken.",
    ]
    (OUT / "THIRTY_NINTH_SCRIBE_MEMORY_MANUAL.md").write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")

    summary = {
        "status": "CONSISTENT",
        "counts": {
            "memory_slots": len(slot_rows),
            "statements": len(memory_rows),
            "worked_job_steps": len(worked_rows),
            "max_slots_filled": max_load,
            "owner_breaks_inside_statement": internal_owner_breaks,
            "record_starts": sum(row["entry_boundary"] == "RECORD_START" for row in memory_rows),
            "visible_owner_switches": sum(row["visible_owner_operation"] in {"VOR_SATZ_UMSCHALTEN", "IM_SATZ_UMSCHALTEN"} for row in memory_rows),
        },
        "sources": {str(path.relative_to(ROOT)): sha256(path) for path in (TRANSITIONS, STATEMENTS, PROGRAMS, WORKED)},
    }
    (OUT / "BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
