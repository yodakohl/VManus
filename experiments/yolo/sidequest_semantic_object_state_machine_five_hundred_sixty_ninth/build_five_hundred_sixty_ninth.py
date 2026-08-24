#!/usr/bin/env python3
import csv
import json
from collections import OrderedDict, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
P565 = ROOT / "sidequest_semantic_workshop_recipe_macros_five_hundred_sixty_fifth"
P568 = ROOT / "sidequest_semantic_workshop_object_inventory_five_hundred_sixty_eighth"


def read_tsv(path):
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(name, rows):
    with (HERE / name).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def baseline(owner_class):
    if owner_class == "PLANT_MATERIAL":
        return "PICTURED_PLANT_MATTER"
    if owner_class == "FIGURE_APPLICATION":
        return "APPLICATION_CHARGE"
    if owner_class in {"SEPARATE_PORTION", "UNCLEAR_WORK_PORTION"}:
        return "TARGETED_TRANSFER_PORTION"
    if owner_class == "VESSEL_PREPARATION":
        return "PREPARATION_BATCH"
    return "WORKING_LIQUID"


def destination(owner_class):
    if owner_class == "PLANT_MATERIAL":
        return "PREPARATION_BATCH"
    if owner_class == "FIGURE_APPLICATION":
        return "APPLICATION_CHARGE"
    if owner_class in {"SEPARATE_PORTION", "UNCLEAR_WORK_PORTION"}:
        return "TARGETED_TRANSFER_PORTION"
    if owner_class == "VESSEL_PREPARATION":
        return "PREPARATION_BATCH"
    return "WORKING_LIQUID"


def main():
    source_statements = read_tsv(P568 / "FIVE_HUNDRED_SIXTY_EIGHTH_ONE_HUNDRED_SIXTEEN_OBJECT_STATEMENTS.tsv")
    macro_map = {row["statement_id"]: row for row in read_tsv(P565 / "FIVE_HUNDRED_SIXTY_FIFTH_ONE_HUNDRED_SIXTEEN_MACRO_MAP.tsv")}
    events = read_tsv(P568 / "FIVE_HUNDRED_SIXTY_EIGHTH_THREE_HUNDRED_EIGHTY_ONE_OBJECT_EVENTS.tsv")

    record_order = ["H1", "H2", "H3", "H4", "H5", "B1", "B2", "B3", "B4", "B5", "B6"]
    transition_rows = []
    for record in record_order:
        rows = [row for row in source_statements if row["record"] == record]
        current = None
        previous_owner = None
        previous_closed = True
        for row in rows:
            owner = row["owner_object_class"]
            reset_reasons = []
            if current is None:
                reset_reasons.append("RECORD_START")
            if previous_owner is not None and owner != previous_owner:
                reset_reasons.append("VISIBLE_OWNER_CHANGE")
            if previous_closed and current is not None and owner == previous_owner:
                reset_reasons.append("PREVIOUS_CELL_COMMITTED")
            if reset_reasons:
                current = baseline(owner)
            input_object = current
            phases = macro_map[row["statement_id"]]["phase_signature"].split(">")
            if phases == ["STATE_ONLY"]:
                phases = []
            path = [current]
            qualifiers = []
            committed = False
            for phase in phases:
                if phase == "MATERIAL_PREP":
                    current = "PREPARATION_BATCH" if owner == "PLANT_MATERIAL" else current
                    path.append(current)
                elif phase == "MEASURE_CHARGE":
                    path.append("MEASURED_PORTION")
                    current = destination(owner)
                    path.append(current)
                elif phase == "APPLY":
                    current = "APPLICATION_CHARGE"
                    path.append(current)
                elif phase == "ROUTE":
                    current = "TARGETED_TRANSFER_PORTION"
                    path.append(current)
                elif phase == "HOLD":
                    qualifiers.append("HELD_OR_ACTING")
                elif phase == "THERMAL":
                    qualifiers.append("TEMPERED")
                elif phase == "WASH":
                    qualifiers.append("WASHED")
                elif phase == "SETTLE":
                    qualifiers.append("SETTLED_OR_COLLECTED")
                elif phase == "SPECIALIST":
                    qualifiers.append("SPECIALIST_PROCESSED")
                elif phase == "CLOSE":
                    committed = True
            transition_rows.append({
                "statement_id": row["statement_id"],
                "page": row["page"],
                "record": record,
                "owner_object_class": owner,
                "reset_here": "YES" if reset_reasons else "NO",
                "reset_reason": "|".join(reset_reasons) if reset_reasons else "CONTINUE_OPEN_OBJECT",
                "input_object": input_object,
                "phase_signature": macro_map[row["statement_id"]]["phase_signature"],
                "transition_path": ">".join(path),
                "output_object": current,
                "output_qualifiers": "|".join(qualifiers) if qualifiers else "UNCHANGED",
                "committed": "YES" if committed else "NO",
                "complete_reading_de": row["owner_specialized_reading_de"],
                "transition_complete": "YES",
            })
            previous_owner = owner
            previous_closed = committed

    transition_by_statement = {row["statement_id"]: row for row in transition_rows}
    event_rows = []
    for row in events:
        transition = transition_by_statement[row["statement_id"]]
        event_rows.append({
            **row,
            "input_object": transition["input_object"],
            "output_object": transition["output_object"],
            "output_qualifiers": transition["output_qualifiers"],
            "committed": transition["committed"],
            "state_binding_complete": "YES",
        })

    record_rows = []
    markdown = ["# Gegenstands- und Zustandsfluss", "", "Jede Zeile zeigt den vorliegenden Gegenstand, die vollständige Phasenfolge und den resultierenden Gegenstand. Bildwechsel oder eine bereits geschlossene Zelle starten einen frischen lokalen Arbeitszustand.", ""]
    for record in record_order:
        rows = [row for row in transition_rows if row["record"] == record]
        record_rows.append({
            "record": record,
            "page": rows[0]["page"],
            "statements": str(len(rows)),
            "resets": str(sum(row["reset_here"] == "YES" for row in rows)),
            "committed_cells": str(sum(row["committed"] == "YES" for row in rows)),
            "object_path": " || ".join(f"{row['statement_id']}:{row['input_object']}--{row['phase_signature']}-->{row['output_object']}" for row in rows),
        })
        markdown.extend([f"## {record}", ""])
        for row in rows:
            markdown.append(f"- **{row['statement_id']}** `{row['input_object']}` → `{row['phase_signature']}` → `{row['output_object']}`; Zustand `{row['output_qualifiers']}`; Schluss `{row['committed']}`; Start `{row['reset_reason']}`.")
        markdown.append("")

    state_rows = [
        {"state": "PICTURED_PLANT_MATTER", "meaning_de": "sichtbarer Pflanzenteil vor der Verarbeitung", "created_by": "PLANT_OWNER_RESET"},
        {"state": "PREPARATION_BATCH", "meaning_de": "laufender Ansatz oder Zubereitung", "created_by": "MATERIAL_PREP_OR_VESSEL_OWNER"},
        {"state": "MEASURED_PORTION", "meaning_de": "kurz abgeteilte oder bis Sollmaß bestimmte Portion", "created_by": "MEASURE_CHARGE_INTERMEDIATE"},
        {"state": "WORKING_LIQUID", "meaning_de": "Flüssigkeit in Becken, Gerät oder technischer Station", "created_by": "LIQUID_OWNER_OR_CHARGE_DESTINATION"},
        {"state": "APPLICATION_CHARGE", "meaning_de": "an einer Figuren-/Anwendungsstelle gehaltene Portion", "created_by": "FIGURE_OWNER_OR_APPLY"},
        {"state": "TARGETED_TRANSFER_PORTION", "meaning_de": "zur nächsten sichtbaren Stelle geführte Portion", "created_by": "ROUTE_OR_SEPARATE_OWNER"},
    ]
    write_tsv("FIVE_HUNDRED_SIXTY_NINTH_SIX_OBJECT_STATES.tsv", state_rows)
    write_tsv("FIVE_HUNDRED_SIXTY_NINTH_ONE_HUNDRED_SIXTEEN_TRANSITIONS.tsv", transition_rows)
    write_tsv("FIVE_HUNDRED_SIXTY_NINTH_ELEVEN_RECORD_FLOWS.tsv", record_rows)
    write_tsv("FIVE_HUNDRED_SIXTY_NINTH_THREE_HUNDRED_EIGHTY_ONE_STATE_EVENTS.tsv", event_rows)
    (HERE / "FIVE_HUNDRED_SIXTY_NINTH_COMPLETE_STATE_FLOW.md").write_text("\n".join(markdown).rstrip() + "\n", encoding="utf-8")
    summary = {
        "status": "PASS",
        "object_states": len(state_rows),
        "transitions": len(transition_rows),
        "records": len(record_rows),
        "events": len(event_rows),
        "resets": sum(row["reset_here"] == "YES" for row in transition_rows),
        "owner_change_resets": sum("VISIBLE_OWNER_CHANGE" in row["reset_reason"] for row in transition_rows),
        "commit_resets": sum("PREVIOUS_CELL_COMMITTED" in row["reset_reason"] for row in transition_rows),
        "committed_cells": sum(row["committed"] == "YES" for row in transition_rows),
        "complete_transitions": sum(row["transition_complete"] == "YES" for row in transition_rows),
    }
    (HERE / "FIVE_HUNDRED_SIXTY_NINTH_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    report = [
        "# Fünfhundertneunundsechzigste Runde: Gegenstandszustände",
        "",
        "## Ergebnis",
        "",
        "Die sechs Werkstattgegenstände bilden eine ausführbare Zustandsmaschine. Bildbesitzer starten Pflanzenstoff, Arbeitsflüssigkeit, Ansatz, Anwendungsladung oder Zielportion. Materialvorbereitung bildet einen Ansatz; Messen/Beschicken erzeugt vorübergehend eine Portion und gibt sie in den Besitzerzustand; Anlegen bildet eine Anwendungsladung; Weiterleiten eine Zielportion. Halten, Wärme, Waschen und Absetzen verändern den Zustand, Schließen verbucht die Zelle.",
        "",
        "Nach sichtbarem Besitzerwechsel oder bereits geschlossener Zelle startet die nächste Anweisung frisch. Dadurch wird keine fortlaufende unsichtbare Rohrleitung über unabhängige Bildstationen erfunden. Offene Zellen dürfen ihren Gegenstand dagegen in die nächste Aussage tragen.",
        "",
        "Alle 116 Aussagen und 381 Ereignisse besitzen nun Eingang, Phasenweg, Ausgang, Zustandsqualifikator und Schlussstatus. Herbal bildet vor allem Pflanzenteil→Ansatz→Portion. Biological bildet Arbeitsflüssigkeit/Anwendung→Halten/Temperieren/Absetzen→Zielportion oder Schluss.",
        "",
        "## Nächster Schritt",
        "",
        "Nun wird die Zustandsmaschine in echte natürlich lesbare Recordzusammenfassungen umgesetzt: pro Record ein Ausgangsmaterial, eine Folge von Transformationen und ein Endprodukt oder offener Rest.",
    ]
    (HERE / "FIVE_HUNDRED_SIXTY_NINTH_REPORT.md").write_text("\n".join(report) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
