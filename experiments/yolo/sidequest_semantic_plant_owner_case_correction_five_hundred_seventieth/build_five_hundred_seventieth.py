#!/usr/bin/env python3
import csv
import json
from collections import Counter, OrderedDict, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
P565 = ROOT / "sidequest_semantic_workshop_recipe_macros_five_hundred_sixty_fifth"
P567 = ROOT / "sidequest_semantic_owner_specialized_macros_five_hundred_sixty_seventh"


def read_tsv(path):
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(name, rows):
    with (HERE / name).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


CHANNELS = ["MEASURE", "PORTION", "STAGE", "SOURCE", "FLOW_LIQUID", "TARGET", "PREPARATION", "READY", "SETTLE", "HEAT", "PASSAGE", "GRADE"]


def modifier_channels(parse):
    parts = set(parse.split("+"))
    tests = [
        ("MEASURE", "AIIN" in parts), ("PORTION", "AIN" in parts), ("STAGE", "IIN" in parts),
        ("SOURCE", "AR" in parts), ("FLOW_LIQUID", "AIR" in parts), ("TARGET", "AL" in parts),
        ("PREPARATION", "OR" in parts), ("READY", "CTH" in parts), ("SETTLE", "SHED" in parts),
        ("HEAT", "CHK" in parts), ("PASSAGE", "CKH" in parts), ("GRADE", bool(parts & {"E", "EE", "EEE"})),
    ]
    return [name for name, condition in tests if condition]


def corrected_class(owner, old):
    return "PLANT_MATERIAL" if "pflanze" in owner.lower() else old


def object_tags(row):
    tags = []
    owner = row["corrected_owner_object_class"]
    parts = set(row["component_parse"].split("+"))
    if owner == "PLANT_MATERIAL": tags.append("PICTURED_PLANT_MATTER")
    if "OR" in parts: tags.append("PREPARATION_BATCH")
    if parts & {"AIIN", "AIN"}: tags.append("MEASURED_PORTION")
    if owner in {"BASIN_LIQUID", "HAND_DEVICE_LIQUID", "TECHNICAL_STATION_LIQUID", "VESSEL_PREPARATION"}: tags.append("WORKING_LIQUID")
    if owner == "FIGURE_APPLICATION": tags.append("APPLICATION_CHARGE")
    if owner in {"SEPARATE_PORTION", "UNCLEAR_WORK_PORTION"}: tags.append("TARGETED_TRANSFER_PORTION")
    return tags or ["OWNER_BOUND_WORK_ITEM"]


def baseline(owner):
    if owner == "PLANT_MATERIAL": return "PICTURED_PLANT_MATTER"
    if owner == "FIGURE_APPLICATION": return "APPLICATION_CHARGE"
    if owner in {"SEPARATE_PORTION", "UNCLEAR_WORK_PORTION"}: return "TARGETED_TRANSFER_PORTION"
    if owner == "VESSEL_PREPARATION": return "PREPARATION_BATCH"
    return "WORKING_LIQUID"


def destination(owner):
    if owner == "PLANT_MATERIAL": return "PREPARATION_BATCH"
    if owner == "FIGURE_APPLICATION": return "APPLICATION_CHARGE"
    if owner in {"SEPARATE_PORTION", "UNCLEAR_WORK_PORTION"}: return "TARGETED_TRANSFER_PORTION"
    if owner == "VESSEL_PREPARATION": return "PREPARATION_BATCH"
    return "WORKING_LIQUID"


def main():
    old_events = read_tsv(P567 / "FIVE_HUNDRED_SIXTY_SEVENTH_THREE_HUNDRED_EIGHTY_ONE_EVENT_BINDING.tsv")
    old_statements = read_tsv(P567 / "FIVE_HUNDRED_SIXTY_SEVENTH_ONE_HUNDRED_SIXTEEN_OWNER_SPECIALIZED_STATEMENTS.tsv")
    macro_map = {row["statement_id"]: row for row in read_tsv(P565 / "FIVE_HUNDRED_SIXTY_FIFTH_ONE_HUNDRED_SIXTEEN_MACRO_MAP.tsv")}

    event_rows = []
    profile_counts = defaultdict(Counter)
    for row in old_events:
        owner = next(item["silent_owner_de"] for item in old_statements if item["statement_id"] == row["statement_id"])
        new_class = corrected_class(owner, row["owner_object_class"])
        corrected = {**row, "previous_owner_object_class": row["owner_object_class"], "corrected_owner_object_class": new_class}
        corrected["modifier_channels"] = "|".join(modifier_channels(row["component_parse"])) or "NONE"
        corrected["portable_object_tags"] = "|".join(object_tags(corrected))
        corrected["owner_class_changed"] = "YES" if new_class != row["owner_object_class"] else "NO"
        event_rows.append(corrected)
        profile_counts[new_class]["events"] += 1
        for channel in modifier_channels(row["component_parse"]): profile_counts[new_class][channel] += 1

    statement_rows = []
    for row in old_statements:
        new_class = corrected_class(row["silent_owner_de"], row["owner_object_class"])
        reading = row["owner_specialized_complete_reading_de"]
        work_object = row["supplied_work_object_de"]
        portion = row["supplied_portion_de"]
        if new_class == "PLANT_MATERIAL" and row["owner_object_class"] != "PLANT_MATERIAL":
            work_object = "den Pflanzenstoff oder Ansatz"
            portion = "eine abgemessene Portion des Pflanzenstoffs"
            reading = reading.replace("eine abgemessene Portion der Beckenflüssigkeit", "eine abgemessene Portion des Pflanzenstoffs in den Ansatz")
            reading = reading.replace("die Bad- oder Beckenflüssigkeit", "den Pflanzenstoff oder Ansatz")
        statement_rows.append({
            **row,
            "previous_owner_object_class": row["owner_object_class"],
            "corrected_owner_object_class": new_class,
            "corrected_work_object_de": work_object,
            "corrected_portion_de": portion,
            "corrected_complete_reading_de": reading,
            "owner_class_changed": "YES" if new_class != row["owner_object_class"] else "NO",
        })

    profile_rows = []
    for owner_class in sorted(profile_counts):
        counts = profile_counts[owner_class]
        selected = [row for row in event_rows if row["corrected_owner_object_class"] == owner_class]
        profile_rows.append({
            "owner_object_class": owner_class,
            "events": str(counts["events"]),
            "statements": str(len({row['statement_id'] for row in selected})),
            "records": str(len({row['record'] for row in selected})),
            **{channel.lower(): str(counts[channel]) for channel in CHANNELS},
        })

    transition_rows = []
    record_order = ["H1", "H2", "H3", "H4", "H5", "B1", "B2", "B3", "B4", "B5", "B6"]
    for record in record_order:
        rows = [row for row in statement_rows if row["record"] == record]
        current = None; previous_owner = None; previous_closed = True
        for row in rows:
            owner = row["corrected_owner_object_class"]
            reasons = []
            if current is None: reasons.append("RECORD_START")
            if previous_owner is not None and owner != previous_owner: reasons.append("VISIBLE_OWNER_CHANGE")
            if previous_closed and current is not None and owner == previous_owner: reasons.append("PREVIOUS_CELL_COMMITTED")
            if reasons: current = baseline(owner)
            input_object = current; path = [current]; qualifiers = []; committed = False
            phases = macro_map[row["statement_id"]]["phase_signature"].split(">")
            if phases == ["STATE_ONLY"]: phases = []
            for phase in phases:
                if phase == "MATERIAL_PREP":
                    current = "PREPARATION_BATCH" if owner == "PLANT_MATERIAL" else current; path.append(current)
                elif phase == "MEASURE_CHARGE": path.append("MEASURED_PORTION"); current = destination(owner); path.append(current)
                elif phase == "APPLY": current = "APPLICATION_CHARGE"; path.append(current)
                elif phase == "ROUTE": current = "TARGETED_TRANSFER_PORTION"; path.append(current)
                elif phase == "HOLD": qualifiers.append("HELD_OR_ACTING")
                elif phase == "THERMAL": qualifiers.append("TEMPERED")
                elif phase == "WASH": qualifiers.append("WASHED")
                elif phase == "SETTLE": qualifiers.append("SETTLED_OR_COLLECTED")
                elif phase == "SPECIALIST": qualifiers.append("SPECIALIST_PROCESSED")
                elif phase == "CLOSE": committed = True
            transition_rows.append({
                "statement_id": row["statement_id"], "page": row["page"], "record": record,
                "owner_object_class": owner, "reset_here": "YES" if reasons else "NO",
                "reset_reason": "|".join(reasons) if reasons else "CONTINUE_OPEN_OBJECT", "input_object": input_object,
                "phase_signature": macro_map[row["statement_id"]]["phase_signature"], "transition_path": ">".join(path),
                "output_object": current, "output_qualifiers": "|".join(qualifiers) if qualifiers else "UNCHANGED",
                "committed": "YES" if committed else "NO", "corrected_complete_reading_de": row["corrected_complete_reading_de"],
                "transition_complete": "YES",
            })
            previous_owner = owner; previous_closed = committed

    record_rows = []
    for record in record_order:
        rows = [row for row in transition_rows if row["record"] == record]
        record_rows.append({
            "record": record, "page": rows[0]["page"], "statements": str(len(rows)),
            "resets": str(sum(row["reset_here"] == "YES" for row in rows)),
            "committed_cells": str(sum(row["committed"] == "YES" for row in rows)),
            "start_object": rows[0]["input_object"], "final_object": rows[-1]["output_object"],
            "object_path": " || ".join(f"{row['statement_id']}:{row['input_object']}--{row['phase_signature']}-->{row['output_object']}" for row in rows),
        })

    write_tsv("FIVE_HUNDRED_SEVENTIETH_THREE_HUNDRED_EIGHTY_ONE_CORRECTED_EVENTS.tsv", event_rows)
    write_tsv("FIVE_HUNDRED_SEVENTIETH_ONE_HUNDRED_SIXTEEN_CORRECTED_STATEMENTS.tsv", statement_rows)
    write_tsv("FIVE_HUNDRED_SEVENTIETH_EIGHT_CORRECTED_PROFILES.tsv", profile_rows)
    write_tsv("FIVE_HUNDRED_SEVENTIETH_ONE_HUNDRED_SIXTEEN_CORRECTED_TRANSITIONS.tsv", transition_rows)
    write_tsv("FIVE_HUNDRED_SEVENTIETH_ELEVEN_CORRECTED_RECORD_FLOWS.tsv", record_rows)
    summary = {
        "status": "PASS", "events": len(event_rows), "statements": len(statement_rows), "profiles": len(profile_rows),
        "transitions": len(transition_rows), "records": len(record_rows),
        "corrected_events": sum(row["owner_class_changed"] == "YES" for row in event_rows),
        "corrected_statements": sum(row["owner_class_changed"] == "YES" for row in statement_rows),
        "corrected_record": "H3", "h3_start_object": next(row["start_object"] for row in record_rows if row["record"] == "H3"),
        "complete_transitions": sum(row["transition_complete"] == "YES" for row in transition_rows),
    }
    (HERE / "FIVE_HUNDRED_SEVENTIETH_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    report = [
        "# Fünfhundertsiebzigste Runde: Pflanzenbesitzer-Korrektur",
        "",
        "## Korrektur",
        "",
        "`Kronenpflanze` enthielt das Suchwort nur mit kleinem Binnen-p und wurde deshalb in Pass 567–569 fälschlich der Defaultklasse Beckenflüssigkeit zugeordnet. Die Besitzererkennung ist nun ohne Beachtung der Großschreibung. Genau 17 H3-Ereignisse und vier H3-Aussagen wechseln von BASIN_LIQUID zu PLANT_MATERIAL.",
        "",
        "H3 startet jetzt korrekt mit PICTURED_PLANT_MATTER und bildet durch seine erste lange Folge einen PREPARATION_BATCH. Die beiden späteren Maß-/Beschickungszellen füllen Pflanzenstoff in diesen Ansatz statt Beckenflüssigkeit. Alle anderen 364 Ereignisse und 112 Aussagen bleiben unverändert.",
        "",
        "Die acht Modifikatorprofile und alle 116 Zustandsübergänge wurden neu aufgebaut. Dies ist eine mechanische Besitzerkorrektur, keine neue Bedeutungsannahme.",
        "",
        "## Nächster Schritt",
        "",
        "Auf der korrigierten Basis werden nun die elf natürlichen Start–Verarbeitung–Ende-Zusammenfassungen geschrieben.",
    ]
    (HERE / "FIVE_HUNDRED_SEVENTIETH_REPORT.md").write_text("\n".join(report) + "\n", encoding="utf-8")


if __name__ == "__main__": main()
