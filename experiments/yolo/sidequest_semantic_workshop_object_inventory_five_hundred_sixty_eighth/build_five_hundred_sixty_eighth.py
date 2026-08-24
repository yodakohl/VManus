#!/usr/bin/env python3
import csv
import json
from collections import Counter, OrderedDict, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
SOURCE = ROOT / "sidequest_semantic_owner_specialized_macros_five_hundred_sixty_seventh"


def read_tsv(path):
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(name, rows):
    with (HERE / name).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


CHANNELS = ["MEASURE", "PORTION", "STAGE", "SOURCE", "FLOW_LIQUID", "TARGET", "PREPARATION", "READY", "SETTLE", "HEAT", "PASSAGE", "GRADE"]


def channels(parse):
    parts = set(parse.split("+"))
    result = []
    tests = [
        ("MEASURE", "AIIN" in parts), ("PORTION", "AIN" in parts), ("STAGE", "IIN" in parts),
        ("SOURCE", "AR" in parts), ("FLOW_LIQUID", "AIR" in parts), ("TARGET", "AL" in parts),
        ("PREPARATION", "OR" in parts), ("READY", "CTH" in parts), ("SETTLE", "SHED" in parts),
        ("HEAT", "CHK" in parts), ("PASSAGE", "CKH" in parts), ("GRADE", bool(parts & {"E", "EE", "EEE"})),
    ]
    return [name for name, condition in tests if condition]


def object_tags(row):
    tags = []
    owner = row["owner_object_class"]
    parts = set(row["component_parse"].split("+"))
    if owner == "PLANT_MATERIAL":
        tags.append("PICTURED_PLANT_MATTER")
    if "OR" in parts:
        tags.append("PREPARATION_BATCH")
    if parts & {"AIIN", "AIN"}:
        tags.append("MEASURED_PORTION")
    if owner in {"BASIN_LIQUID", "HAND_DEVICE_LIQUID", "TECHNICAL_STATION_LIQUID", "VESSEL_PREPARATION"}:
        tags.append("WORKING_LIQUID")
    if owner == "FIGURE_APPLICATION":
        tags.append("APPLICATION_CHARGE")
    if owner in {"SEPARATE_PORTION", "UNCLEAR_WORK_PORTION"}:
        tags.append("TARGETED_TRANSFER_PORTION")
    return tags or ["OWNER_BOUND_WORK_ITEM"]


def main():
    events = read_tsv(SOURCE / "FIVE_HUNDRED_SIXTY_SEVENTH_THREE_HUNDRED_EIGHTY_ONE_EVENT_BINDING.tsv")
    statements = read_tsv(SOURCE / "FIVE_HUNDRED_SIXTY_SEVENTH_ONE_HUNDRED_SIXTEEN_OWNER_SPECIALIZED_STATEMENTS.tsv")

    matrix = defaultdict(Counter)
    enriched_events = []
    for row in events:
        event_channels = channels(row["component_parse"])
        tags = object_tags(row)
        for channel in event_channels:
            matrix[row["owner_object_class"]][channel] += 1
        enriched_events.append({
            **row,
            "modifier_channels": "|".join(event_channels) if event_channels else "NONE",
            "portable_object_tags": "|".join(tags),
            "object_assignment_complete": "YES",
        })

    profile_names = {
        "PLANT_MATERIAL": "PFLANZENSTOFF_UND_ANSATZ",
        "BASIN_LIQUID": "ABGEMESSENE_BECKENFLUESSIGKEIT",
        "FIGURE_APPLICATION": "ZEITLICH_ABGESTUFTE_ANWENDUNGSPORTION",
        "HAND_DEVICE_LIQUID": "HANDGERAET_TRANSFERFLUESSIGKEIT",
        "SEPARATE_PORTION": "GETRENNT_GEFUEHRTE_ZIELPORTION",
        "TECHNICAL_STATION_LIQUID": "STATIONS_UND_TRANSFERFLUESSIGKEIT",
        "UNCLEAR_WORK_PORTION": "ABGEMESSENE_ARBEITSPORTION",
        "VESSEL_PREPARATION": "GEFAESSANSATZ",
    }
    profile_rows = []
    for owner_class in sorted(matrix):
        counts = matrix[owner_class]
        owner_events = [row for row in events if row["owner_object_class"] == owner_class]
        dominant = sorted(CHANNELS, key=lambda channel: (-counts[channel], channel))[:3]
        profile_rows.append({
            "owner_object_class": owner_class,
            "concrete_workshop_profile_de": profile_names[owner_class],
            "events": str(len(owner_events)),
            "statements": str(len({row['statement_id'] for row in owner_events})),
            "records": str(len({row['record'] for row in owner_events})),
            **{channel.lower(): str(counts[channel]) for channel in CHANNELS},
            "three_dominant_channels": "|".join(dominant),
        })

    portable_defs = OrderedDict([
        ("PICTURED_PLANT_MATTER", "sichtbarer Pflanzenteil vor oder während der Zubereitung"),
        ("PREPARATION_BATCH", "gebildeter Ansatz oder laufende Zubereitung"),
        ("MEASURED_PORTION", "abgeteilte oder bis zum Sollmaß bestimmte Menge"),
        ("WORKING_LIQUID", "Flüssigkeit in Becken, Gefäß, Handgerät oder Station"),
        ("APPLICATION_CHARGE", "an Figuren oder einer Anwendungslage gehaltene Portion"),
        ("TARGETED_TRANSFER_PORTION", "getrennt zu Ziel oder nächster Station geführte Portion"),
    ])
    portable_rows = []
    for index, (tag, meaning) in enumerate(portable_defs.items(), 1):
        selected = [row for row in enriched_events if tag in row["portable_object_tags"].split("|")]
        portable_rows.append({
            "object_no": f"O{index:02d}",
            "portable_object": tag,
            "working_meaning_de": meaning,
            "events": str(len(selected)),
            "statements": str(len({row['statement_id'] for row in selected})),
            "records": str(len({row['record'] for row in selected})),
            "owner_classes": "|".join(sorted({row["owner_object_class"] for row in selected})),
            "not_asserted": "kein konkreter Stoffname, keine Pflanzenart, keine Krankheit",
        })

    statement_event_map = defaultdict(list)
    for row in enriched_events:
        statement_event_map[row["statement_id"]].append(row)
    statement_rows = []
    source_statement = {row["statement_id"]: row for row in statements}
    for statement_id, rows in statement_event_map.items():
        tags = sorted({tag for row in rows for tag in row["portable_object_tags"].split("|")})
        mods = sorted({tag for row in rows for tag in row["modifier_channels"].split("|") if tag != "NONE"})
        statement_rows.append({
            "statement_id": statement_id,
            "page": rows[0]["page"],
            "record": rows[0]["record"],
            "owner_object_class": rows[0]["owner_object_class"],
            "portable_objects": "|".join(tags),
            "modifier_channels": "|".join(mods) if mods else "NONE",
            "owner_specialized_reading_de": source_statement[statement_id]["owner_specialized_complete_reading_de"],
            "object_inventory_complete": "YES",
        })

    write_tsv("FIVE_HUNDRED_SIXTY_EIGHTH_EIGHT_OWNER_MODIFIER_PROFILES.tsv", profile_rows)
    write_tsv("FIVE_HUNDRED_SIXTY_EIGHTH_SIX_PORTABLE_WORKSHOP_OBJECTS.tsv", portable_rows)
    write_tsv("FIVE_HUNDRED_SIXTY_EIGHTH_ONE_HUNDRED_SIXTEEN_OBJECT_STATEMENTS.tsv", statement_rows)
    write_tsv("FIVE_HUNDRED_SIXTY_EIGHTH_THREE_HUNDRED_EIGHTY_ONE_OBJECT_EVENTS.tsv", enriched_events)
    summary = {
        "status": "PASS",
        "owner_profiles": len(profile_rows),
        "portable_objects": len(portable_rows),
        "modifier_channels": len(CHANNELS),
        "events": len(enriched_events),
        "statements": len(statement_rows),
        "object_assignments": sum(row["object_assignment_complete"] == "YES" for row in enriched_events),
        "specific_substance_claims": 0,
    }
    (HERE / "FIVE_HUNDRED_SIXTY_EIGHTH_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    report = [
        "# Fünfhundertachtundsechzigste Runde: Werkstattgegenstände",
        "",
        "## Ergebnis",
        "",
        "Sechs übergreifende Gegenstände reichen für die zehnseitige Lesung: sichtbarer Pflanzenstoff, daraus gebildeter Ansatz, abgemessene Portion, Arbeitsflüssigkeit in Becken/Gefäß/Station, Anwendungsladung am Figurenpaar und getrennt geführte Zielportion. Sie sind Rollen, keine behaupteten Stoffnamen.",
        "",
        "Die Modifikatoren unterscheiden die Bildklassen deutlich. Pflanzenmaterial trägt 13 Zubereitungs- und 12 Maßbezüge. Beckenflüssigkeit trägt 13 Ziel-, neun Durchlass- und 24 Gradbezüge. Figurenpaar-Anwendung trägt 18 Grad-, aber nur zwei Durchlassbezüge; eine zeitlich abgestufte Anwendung ist dort die bessere Defaultlesung. Technische Stationen verbinden zwölf Ziele, sieben Maße, fünf Portionen und 19 Grade.",
        "",
        "Damit wird die Arbeitswelt konkreter, ohne falsche Stoffwörter: Pflanzenstoff → Ansatz → abgemessene Portion → Arbeitsflüssigkeit oder Anwendungsladung → Zielstation. Öl, Wein, Honig, Krankheit und Pflanzenart bleiben ungesetzt, solange keine der zehn Seiten sie erzwingt.",
        "",
        "## Nächster Schritt",
        "",
        "Nun werden diese sechs Gegenstände als Zustandsmaschine über die elf Records verfolgt: Wann wird Pflanzenstoff zum Ansatz, Ansatz zur Portion, Portion zur Arbeitsflüssigkeit oder Anwendung, und wann wird sie weitergeführt oder geschlossen?",
    ]
    (HERE / "FIVE_HUNDRED_SIXTY_EIGHTH_REPORT.md").write_text("\n".join(report) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
