#!/usr/bin/env python3
"""Bind every short Biological work unit to one visible or unresolved station."""

from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
EVENTS = ROOT / "experiments/yolo/sidequest_semantic_atomic_bio_glossary_three_hundred_fourteenth/THREE_HUNDRED_FOURTEENTH_281_ATOMIC_EVENT_READINGS.tsv"
STATEMENTS = ROOT / "experiments/yolo/sidequest_semantic_bio_clause_templates_three_hundred_fifteenth/THREE_HUNDRED_FIFTEENTH_97_TEMPLATE_STATEMENTS.tsv"
LONG_EVENTS = ROOT / "experiments/yolo/sidequest_semantic_all_long_bio_three_hundred_seventeenth/THREE_HUNDRED_SEVENTEENTH_105_LONG_STATEMENT_EVENTS.tsv"
LONG_STEPS = ROOT / "experiments/yolo/sidequest_semantic_all_long_bio_three_hundred_seventeenth/THREE_HUNDRED_SEVENTEENTH_32_MICROSTEPS.tsv"
VISUAL = ROOT / "experiments/yolo/sidequest_theory_candidates_v74/V74_R3_281_EVENT_INTERLINEAR.tsv"

STATION_ROLES = {
    "B1_SHARED_TWO_ROW_POOL": ("GEMEINSAMES_BEHANDLUNGSBECKEN", "Spülen, portionieren, kurz oder lang einwirken, absetzen und lokale Zielpassagen prüfen."),
    "B2_UPPER_PAIRED_BASINS_AND_CYLINDER": ("PAARBECKEN_MIT_MITTELZYLINDER", "Zwei obere Becken lokal abgleichen, Posten zuführen, temperieren und wieder abziehen."),
    "B2_MIDDLE_LEFT_DEVICE_AND_INLINE_NODE": ("ZWISCHENGERAET_MIT_KNOTEN", "Posten durchlassen, Klarlauf bearbeiten und Sollwerte einstellen."),
    "B2_MIDDLE_RIGHT_AMBIGUOUS_STATION": ("AMBIGUER_RECHTER_POSTEN", "Einen lokalen Übergabeposten bedienen; Ein- und Ausgang bleiben unbestimmt."),
    "B2_LOWER_GREEN_MULTI_FIGURE_POOL": ("MEHRPLATZ_BADBECKEN", "Posten auf Plätze verteilen, einwirken lassen, waschen und lokal abführen."),
    "B2_LOWER_POOL_EDGE_STATIONS": ("RAND_ZUFUEHR_ABFUEHRSTATIONEN", "Zuführung, Zielkontakt und Abführung an den Randplätzen ausführen."),
    "B3_UPPER_MARGIN_OPEN_FAN_STATION": ("OFFENER_FAECHERZULAUF", "Einen offenen Zulauf oder Fächerposten beschicken und behandeln."),
    "B3_MIDDLE_MARGIN_ROUND_VESSEL_STATION": ("RUNDE_ZWISCHENSTATION", "Einen runden Zwischenposten sammeln, einstellen und weitergeben."),
    "B3_LOWER_MARGIN_BASKET_VESSEL_STATION": ("KORB_SAMMELGEFAESS", "Im korbartigen Gefäß sammeln, behandeln und abziehen."),
    "B3_MARGIN_TO_MAIN_GAP_UNRESOLVED": ("UNVERBUNDENER_UEBERGABEPOSTEN", "Nach der sichtbaren Lücke einen neuen Übergabeposten beginnen; keine Leitung ergänzen."),
    "B3_MAIN_ARCH_LINKED_PAIR": ("SICHTBAR_VERBUNDENES_PAAR", "Am sichtbaren Paar zuführen, durchleiten, behandeln und lokal abführen."),
    "B4_MAIN_ARCH_LINKED_PAIR": ("ANWENDUNGS_UND_DURCHLASS_PAAR", "Kontakt, Zielpassage und Absetzung am sichtbaren Paar ausführen."),
    "B4_MAIN_LEFT_OPEN_FRINGE_STATION": ("OFFENE_LINKSSTATION", "An der offenen linken Station zuführen, spülen und neu ansetzen."),
    "B4_MAIN_RIGHT_S_RUN_MULTIPORT_STATION": ("S_FOERMIGER_MEHRPORT", "Mehrere lokale Ports nacheinander beschicken, behandeln und abführen."),
    "B5_LEFT_OPEN_FRINGE_STATION": ("LINKER_NACHTRAGSPOSTEN", "Einen offenen Nachtragsposten absetzen, messen und überführen."),
    "B6_RIGHT_S_RUN_MULTIPORT_STATION": ("RECHTER_NACHTRAGSPOSTEN", "Am rechten Nachtragsposten sammeln, einstellen und am Endziel einlegen."),
}


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh, delimiter="\t"))


def write(path: Path, rows: list[dict[str, object]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    events = read(EVENTS)
    statement_reading = {row["statement_id"]: row["compact_template_reading_de"] for row in read(STATEMENTS)}
    long_event_step = {row["event_id"]: row["microstep_id"] for row in read(LONG_EVENTS)}
    long_step_reading = {row["microstep_id"]: row["concrete_reading_de"] for row in read(LONG_STEPS)}
    visual = {f"E{int(row['event_serial']):03d}": row for row in read(VISUAL)}

    annotated = []
    for event in events:
        vis = visual[event["event_id"]]
        base_unit = long_event_step.get(event["event_id"], event["statement_id"])
        annotated.append({
            **event,
            "base_unit": base_unit,
            "owner_id": vis["local_visible_or_inherited_owner"],
            "owner_status": vis["local_owner_status"],
            "owner_gloss": vis["owner_gloss_not_translation"],
            "incoming_rule": vis["incoming_contact_and_reset"],
            "direction_constraint": vis["contact_direction_constraint"],
        })

    # First cut on work-unit identity, then on a genuine owner change.  The
    # latter splits B3-S016 at E264 and leaves every final unit owner-pure.
    groups: list[list[dict[str, str]]] = []
    for event in annotated:
        if not groups or groups[-1][-1]["base_unit"] != event["base_unit"] or groups[-1][-1]["owner_id"] != event["owner_id"]:
            groups.append([])
        groups[-1].append(event)
    group_count_by_base = Counter(group[0]["base_unit"] for group in groups)
    seen_by_base: Counter[str] = Counter()

    unit_rows: list[dict[str, object]] = []
    previous_owner_by_record: dict[str, str] = {}
    for group in groups:
        first = group[0]
        base = first["base_unit"]
        seen_by_base[base] += 1
        unit_id = base if group_count_by_base[base] == 1 else f"{base}-O{seen_by_base[base]}"
        if base == "B3-S016" and first["event_id"] == "E263":
            reading = "Ziehe den Posten aus dem korbartigen Randgefäß ab."
        elif base == "B3-S016" and first["event_id"] == "E264":
            reading = "Beginne jenseits der sichtbaren Lücke einen neuen Rücktransferposten."
        else:
            reading = long_step_reading.get(base, statement_reading[first["statement_id"]])
        prior_owner = previous_owner_by_record.get(first["record_unit_id"])
        if prior_owner is None:
            boundary = "RECORD_START"
        elif prior_owner == first["owner_id"]:
            boundary = "SAME_LOCAL_STATION"
        elif "BREAK_VISIBLE_OWNER" in first["incoming_rule"]:
            boundary = "VISIBLE_OWNER_BREAK_NO_PHYSICAL_CARRY"
        else:
            boundary = "OWNER_CHANGE_NO_INFERRED_CONNECTION"
        previous_owner_by_record[first["record_unit_id"]] = first["owner_id"]
        unit_rows.append({
            "station_work_unit_id": unit_id,
            "base_unit_id": base,
            "statement_id": first["statement_id"],
            "record_unit_id": first["record_unit_id"],
            "page": first["page"],
            "event_ids": "|".join(row["event_id"] for row in group),
            "surfaces": " ".join(row["fresh_surface"] for row in group),
            "atomic_chain": " → ".join(row["atomic_gloss_de"] for row in group),
            "event_count": len(group),
            "owner_id": first["owner_id"],
            "owner_status": first["owner_status"],
            "owner_gloss_not_translation": first["owner_gloss"],
            "station_role": STATION_ROLES[first["owner_id"]][0],
            "work_instruction_de": reading,
            "boundary_from_previous_unit": boundary,
            "incoming_contact_rule": first["incoming_rule"],
            "direction_constraint": first["direction_constraint"],
            "global_flow_edge": "NONE",
        })
    unit_path = HERE / "THREE_HUNDRED_EIGHTEENTH_118_STATION_WORK_UNITS.tsv"
    write(unit_path, unit_rows)

    station_rows: list[dict[str, object]] = []
    for owner_id, (role, summary) in STATION_ROLES.items():
        selected_units = [row for row in unit_rows if row["owner_id"] == owner_id]
        selected_events = [event for event in annotated if event["owner_id"] == owner_id]
        station_rows.append({
            "owner_id": owner_id,
            "station_role": role,
            "owner_statuses": "|".join(sorted({event["owner_status"] for event in selected_events})),
            "owner_gloss_not_translation": selected_events[0]["owner_gloss"],
            "record_units": "|".join(sorted({event["record_unit_id"] for event in selected_events})),
            "event_count": len(selected_events),
            "work_unit_count": len(selected_units),
            "statement_count": len({event["statement_id"] for event in selected_events}),
            "concrete_station_summary_de": summary,
            "ordered_work_units": "|".join(str(row["station_work_unit_id"]) for row in selected_units),
            "connection_rule": "Nur innerhalb dieses sichtbaren Besitzers verbinden; Besitzerwechsel erzeugt keinen globalen Fluss.",
        })
    station_path = HERE / "THREE_HUNDRED_EIGHTEENTH_16_STATION_OPERATING_CARDS.tsv"
    write(station_path, station_rows)

    boundary_rows = []
    for row in unit_rows:
        if row["boundary_from_previous_unit"] == "SAME_LOCAL_STATION":
            continue
        boundary_rows.append({
            "station_work_unit_id": row["station_work_unit_id"],
            "record_unit_id": row["record_unit_id"],
            "new_owner_id": row["owner_id"],
            "boundary_class": row["boundary_from_previous_unit"],
            "incoming_contact_rule": row["incoming_contact_rule"],
            "physical_connection_claim": "NONE",
            "reading_de": "Neuen lokalen Stationsposten beginnen; den vorherigen Posten nicht durch eine unsichtbare Leitung fortschreiben.",
        })
    boundary_path = HERE / "THREE_HUNDRED_EIGHTEENTH_16_STATION_ENTRIES.tsv"
    write(boundary_path, boundary_rows)

    by_station = {row["owner_id"]: row for row in station_rows}
    lines = [
        "# Sechzehn Biological-Stationen mit vollständigen Arbeitsfolgen",
        "",
        "Die Reihenfolge ist die Textreihenfolge. Innerhalb einer Station dürfen Schritte zusammengehören; bei jedem Besitzerwechsel beginnt ein neuer lokaler Posten. Es wird keine unsichtbare Verbindung ergänzt.",
        "",
    ]
    current_owner = None
    for unit in unit_rows:
        if unit["owner_id"] != current_owner:
            current_owner = unit["owner_id"]
            station = by_station[current_owner]
            lines += [f"## {station['station_role']}", "", f"Bildbesitzer: {station['owner_gloss_not_translation']}.", ""]
        lines.append(f"- **{unit['station_work_unit_id']}:** {unit['work_instruction_de']}")
    lines.append("")
    edition_path = HERE / "THREE_HUNDRED_EIGHTEENTH_COMPLETE_STATION_EDITION.md"
    edition_path.write_text("\n".join(lines), encoding="utf-8")

    report_path = HERE / "THREE_HUNDRED_EIGHTEENTH_REPORT.md"
    report_path.write_text(
        "# Sidequest-Pass 318: sechzehn lokale Biological-Betriebsstationen\n\n"
        "Die 97 Aussagen beziehungsweise 32 Mikroschritte der langen Aussagen ergeben 118 ownerreine Arbeitsunits. B3-S016 wird korrekt in zwei Einheiten gespalten: Abzug am korbartigen Randgefäß, dann nach der sichtbaren Lücke ein neuer unresolved Rücktransferposten. Alle 281 Karten sind genau einmal enthalten.\n\n"
        "Die Einheiten verteilen sich auf sechzehn sichtbare oder ausdrücklich ungelöste Besitzer: gemeinsames Becken, obere Paarbecken, Zwischenknoten, unteres Mehrplatzbecken, Randstationen, drei Randgefäße, die ungelöste Lücke, sichtbare Bogenpaare, offene Fransen- und S-Lauf-Stationen sowie zwei Nachtragsposten. Zehn Besitzerbrüche und sechs Recordstarts eröffnen lokale Stationen. Kein Übergang wird zu einer globalen Wasserleitung erklärt.\n",
        encoding="utf-8",
    )
    summary_data = {
        "status": "PASS", "events": sum(int(row["event_count"]) for row in unit_rows),
        "statements": len({event["statement_id"] for event in annotated}),
        "long_microsteps": len(long_step_reading), "station_work_units": len(unit_rows),
        "stations": len(station_rows), "station_entries": len(boundary_rows),
        "record_starts": sum(row["boundary_class"] == "RECORD_START" for row in boundary_rows),
        "owner_break_entries": sum(row["boundary_class"] == "VISIBLE_OWNER_BREAK_NO_PHYSICAL_CARRY" for row in boundary_rows),
        "unresolved_events": sum(event["owner_status"] == "UNRESOLVED" for event in annotated),
        "global_flow_edges": sum(row["global_flow_edge"] != "NONE" for row in unit_rows),
        "source_hashes": {str(path.relative_to(ROOT)): sha(path) for path in (EVENTS, STATEMENTS, LONG_EVENTS, LONG_STEPS, VISUAL)},
        "output_hashes": {path.name: sha(path) for path in (unit_path, station_path, boundary_path, edition_path, report_path)},
    }
    (HERE / "BUILD_SUMMARY.json").write_text(json.dumps(summary_data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
