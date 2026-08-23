#!/usr/bin/env python3
"""Select one concrete lookup path for each of the four creative work orders."""

from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
SOURCE = ROOT / "experiments/yolo/sidequest_semantic_four_work_orders"


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: list[dict[str, object]], fields: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        for row in rows:
            writer.writerow({field: str(row.get(field, "")) for field in fields})


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


# A job uses the diagrams as menus.  Each row below is one deliberate shop
# choice, sometimes expressed by a short multi-card entry at one visible spot.
# Nothing outside these thirteen choices is executed by the four sample jobs.
SELECTIONS = [
    {
        "selection_id": "D1-C01-RIGHT-SECTOR-08",
        "work_order_id": "D1_ROOT_BATH_RIGHT_WHEEL",
        "source_unit": "M67_RIGHT_SECTORS",
        "choice_type": "SECTOR",
        "group_ids": ["A1:G018"],
        "selected_workshop_value_de": "Ausgangssektor 8: Zustand auf Übertragung vom Ausgang einstellen",
        "selection_reason_de": "passt zum Wurzelansatz, der vom Vorrat in das gemeinsame Becken übergeben wird",
    },
    {
        "selection_id": "D1-C02-LONG-CLOSED-GRADE",
        "work_order_id": "D1_ROOT_BATH_RIGHT_WHEEL",
        "source_unit": "M67_RIGHT_RING_RULES",
        "choice_type": "RING_RULE",
        "group_ids": ["A1:G033", "A1:G034", "A1:G035"],
        "selected_workshop_value_de": "lange Stufe wählen, Bedingungsgrad notieren und die Fortsetzung schließen",
        "selection_reason_de": "macht aus dem allgemeinen Beckenprogramm einen langen, abgeschlossenen Badgang",
    },
    {
        "selection_id": "D1-C03-LONG-PHASE",
        "work_order_id": "D1_ROOT_BATH_RIGHT_WHEEL",
        "source_unit": "M67_RIGHT_PHASES",
        "choice_type": "PHASE",
        "group_ids": ["A1:G148"],
        "selected_workshop_value_de": "Phasenstelle 3: lange oder volle Phase",
        "selection_reason_de": "verstärkt die längere Halte- und Ruhephase des Wurzelbades",
    },
    {
        "selection_id": "D1-C04-PLACE-GRADE",
        "work_order_id": "D1_ROOT_BATH_RIGHT_WHEEL",
        "source_unit": "M67_SHARED_LEGEND",
        "choice_type": "LEGEND_VALUE",
        "group_ids": ["A1:G184"],
        "selected_workshop_value_de": "Sollgrad des gewählten Himmelsplatzes übernehmen",
        "selection_reason_de": "liefert dem sichtbaren Sollmaß der Badzubereitung den Auftragsgrad",
    },
    {
        "selection_id": "D2-C01-RELEASED-READOUT",
        "work_order_id": "D2_CLEAR_EXTRACT_STAR_ATLAS",
        "source_unit": "M68_PANEL_HEADERS",
        "choice_type": "PANEL_MODE",
        "group_ids": ["A2:G013"],
        "selected_workshop_value_de": "mittleres Paneel: freigegebenen Ablesewert verwenden",
        "selection_reason_de": "entspricht dem nach Standzeit und Nachseihen freigegebenen Klarauszug",
    },
    {
        "selection_id": "D2-C02-TRANSFER-STATION-21",
        "work_order_id": "D2_CLEAR_EXTRACT_STAR_ATLAS",
        "source_unit": "M68_STAR_STATIONS",
        "choice_type": "STAR_STATION",
        "group_ids": ["A2:G053"],
        "selected_workshop_value_de": "Sternstation 21: den gewählten Wert oder Posten übertragen",
        "selection_reason_de": "passt zur anschließenden Weitergabe des Klarauszugs durch die lokalen Stationen",
    },
    {
        "selection_id": "D2-C03-BASE-GRADE",
        "work_order_id": "D2_CLEAR_EXTRACT_STAR_ATLAS",
        "source_unit": "M68_CENTER_KEY",
        "choice_type": "CENTER_GRADE",
        "group_ids": ["A2:G065"],
        "selected_workshop_value_de": "im Zentrum den aktuellen Grundgrad lesen",
        "selection_reason_de": "gibt der gewählten Übertragungsstation einen einfachen gemeinsamen Grad",
    },
    {
        "selection_id": "D3-C01-SLOT-22-LONG-HOLD",
        "work_order_id": "D3_STORED_APPLICATION_THREE_WHEELS",
        "source_unit": "M69_LEFT_28_SLOTS",
        "choice_type": "RADIAL_SLOT",
        "group_ids": ["A3:G131", "A3:G132"],
        "selected_workshop_value_de": "linker Platz 22: den aktuellen Posten in langer Stufe setzen",
        "selection_reason_de": "passt zum länger gehaltenen gelagerten Ansatz und zur Tuchanwendung",
    },
    {
        "selection_id": "D3-C02-MIDDLE-LONG-HOLD",
        "work_order_id": "D3_STORED_APPLICATION_THREE_WHEELS",
        "source_unit": "M69_MIDDLE_QUALITY",
        "choice_type": "QUALITY_VALUE",
        "group_ids": ["A3:G053"],
        "selected_workshop_value_de": "mittlere Qualität: diese Stellung länger halten",
        "selection_reason_de": "macht die Dauer zur Qualitätsbedingung der örtlichen Anwendung",
    },
    {
        "selection_id": "D3-C03-RIGHT-FIXED-STATE",
        "work_order_id": "D3_STORED_APPLICATION_THREE_WHEELS",
        "source_unit": "M69_RIGHT_LIGHT",
        "choice_type": "LIGHT_OR_STATE_VALUE",
        "group_ids": ["A3:G097"],
        "selected_workshop_value_de": "rechtes Rad: festen Zustand wählen",
        "selection_reason_de": "passt zum Festmachen der Anwendung und verhindert einen offenen Endzustand",
    },
    {
        "selection_id": "D4-C01-SOURCE-TO-TARGET-ASPECT",
        "work_order_id": "D4_FRESH_PLANT_LEFT_WHEEL",
        "source_unit": "M67_LEFT_ASPECT_FIELDS",
        "choice_type": "ASPECT_FIELD",
        "group_ids": ["A1:G081", "A1:G082", "A1:G083"],
        "selected_workshop_value_de": "Feld 33: den Posten vom bezeichneten Ausgang zum Ziel aktivieren",
        "selection_reason_de": "bildet die wiederholten Übergaben der frischen Pflanzencharge direkt ab",
    },
    {
        "selection_id": "D4-C02-INPUT-TARGET-GRADE",
        "work_order_id": "D4_FRESH_PLANT_LEFT_WHEEL",
        "source_unit": "M67_LEFT_OUTER_STATIONS",
        "choice_type": "OUTER_STATION",
        "group_ids": ["A1:G137", "A1:G138", "A1:G139"],
        "selected_workshop_value_de": "äußere Station 7: Eingangsposten zum Ziel bringen und Grad notieren",
        "selection_reason_de": "passt zur langen Beckenfolge mit mehreren Zielstellen",
    },
    {
        "selection_id": "D4-C03-TARGET-GRADE-SHORT",
        "work_order_id": "D4_FRESH_PLANT_LEFT_WHEEL",
        "source_unit": "M67_LEFT_RING_RULE",
        "choice_type": "RING_RULE_VALUE",
        "group_ids": ["A1:G156", "A1:G166"],
        "selected_workshop_value_de": "Zielgrad übernehmen und den Zielposten kurz ansetzen",
        "selection_reason_de": "schließt die lange Übergabefolge mit einer kurzen Zielbehandlung",
    },
]


COMBINED_CONDITIONS = {
    "D1_ROOT_BATH_RIGHT_WHEEL": "Rechter Ausgangssektor 8; lange geschlossene Badstufe; lange Phase; Sollgrad des gewählten Platzes.",
    "D2_CLEAR_EXTRACT_STAR_ATLAS": "Freigegebener Mittel-Paneelwert; Übertragungsstation 21; aktueller Grundgrad aus dem Zentrum.",
    "D3_STORED_APPLICATION_THREE_WHEELS": "Linker Platz 22 in langer Stufe; mittlere Stellung länger halten; rechter Zustand fest.",
    "D4_FRESH_PLANT_LEFT_WHEEL": "Vom Ausgang zum Ziel; äußere Station 7; Zielgrad kurz ansetzen.",
}


ECHO_NUCLEI = {
    "aiin": "VORGABEWERT",
    "cheey": "FREIGEGEBENER ODER AUSGELESENER WERT",
    "cho": "EINGANGSPOSTEN",
    "dal": "ZIELZUWEISUNG",
    "dy": "AKTUELLER POSTEN",
    "okeey": "LANGE STUFE",
    "okey": "KURZE STUFE",
    "oldy": "FORTSETZUNG ABSCHLIESSEN",
    "sheey": "LÄNGER HALTEN",
}


def main() -> None:
    orders = read_tsv(SOURCE / "FOUR_WORK_ORDERS.tsv")
    source_units = read_tsv(SOURCE / "FOUR_WORK_ORDER_258_UNITS.tsv")
    source_trace = read_tsv(SOURCE / "TEN_PAGE_776_WORK_ORDER_TRACE.tsv")
    order_by_id = {row["work_order_id"]: row for row in orders}
    order_rank = {row["work_order_id"]: index for index, row in enumerate(orders, start=1)}
    trace_by_group = {row["source_group_id"]: row for row in source_trace}

    selected_group_to_choice: dict[str, dict[str, object]] = {}
    choice_rows: list[dict[str, object]] = []
    choice_rank: dict[str, int] = {}
    choice_counter: Counter[str] = Counter()
    for selection in SELECTIONS:
        did = str(selection["work_order_id"])
        group_ids = list(selection["group_ids"])
        source_rows = [trace_by_group[group_id] for group_id in group_ids]
        if any(row["register"] != "ASTRO" for row in source_rows):
            raise ValueError(f"non-Astro choice: {selection['selection_id']}")
        if any(row["work_order_id"] != did for row in source_rows):
            raise ValueError(f"choice crosses work-order assignment: {selection['selection_id']}")
        if any(row["source_unit"] != selection["source_unit"] for row in source_rows):
            raise ValueError(f"choice crosses source module: {selection['selection_id']}")
        for group_id in group_ids:
            if group_id in selected_group_to_choice:
                raise ValueError(f"Astro group selected twice: {group_id}")
            selected_group_to_choice[group_id] = selection
        choice_counter[did] += 1
        choice_rank[str(selection["selection_id"])] = choice_counter[did]
        choice_rows.append({
            "selection_id": selection["selection_id"],
            "work_order_id": did,
            "work_order_title_de": order_by_id[did]["title_de"],
            "choice_order": choice_counter[did],
            "choice_type": selection["choice_type"],
            "source_unit": selection["source_unit"],
            "page": source_rows[0]["page"],
            "reading_unit_ids": ";".join(dict.fromkeys(row["reading_unit_id"] for row in source_rows)),
            "source_group_ids": ";".join(group_ids),
            "visible_surface_sequence": " ".join(row["visible_surface"] for row in source_rows),
            "current_reader_values_de": " | ".join(row["resolved_reading_de"] for row in source_rows),
            "selected_workshop_value_de": selection["selected_workshop_value_de"],
            "selection_reason_de": selection["selection_reason_de"],
            "selection_status": "EXECUTE_THIS_VISIBLE_OPTION",
        })
    choice_fields = [
        "selection_id", "work_order_id", "work_order_title_de", "choice_order", "choice_type",
        "source_unit", "page", "reading_unit_ids", "source_group_ids", "visible_surface_sequence",
        "current_reader_values_de", "selected_workshop_value_de", "selection_reason_de", "selection_status",
    ]
    write_tsv(OUT / "SELECTED_13_ASTRO_CHOICES.tsv", choice_rows, choice_fields)

    menu_rows: list[dict[str, object]] = []
    for row in (item for item in source_trace if item["register"] == "ASTRO"):
        choice = selected_group_to_choice.get(row["source_group_id"])
        menu_rows.append({
            "work_order_id": row["work_order_id"],
            "work_order_title_de": row["work_order_title_de"],
            "page": row["page"],
            "source_unit": row["source_unit"],
            "reading_unit_id": row["reading_unit_id"],
            "source_group_id": row["source_group_id"],
            "visible_owner": row["visible_owner"],
            "visible_surface": row["visible_surface"],
            "current_reader_value_de": row["resolved_reading_de"],
            "menu_status": "SELECTED_FOR_SAMPLE_JOB" if choice else "UNSELECTED_REFERENCE_OPTION",
            "selection_id": choice["selection_id"] if choice else "NO_SELECTION",
            "selection_reason_de": choice["selection_reason_de"] if choice else "als alternative Nachschlageoption erhalten",
        })
    menu_fields = [
        "work_order_id", "work_order_title_de", "page", "source_unit", "reading_unit_id",
        "source_group_id", "visible_owner", "visible_surface", "current_reader_value_de",
        "menu_status", "selection_id", "selection_reason_de",
    ]
    write_tsv(OUT / "ASTRO_395_MENU_STATUS.tsv", menu_rows, menu_fields)

    # Exact visible forms that were selected in a diagram and also occur in
    # the prose are the clearest dictionary payoff of this round.
    prose_by_surface: dict[str, list[dict[str, str]]] = defaultdict(list)
    selected_astro_by_surface: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in source_trace:
        if row["register"] == "PROSE":
            prose_by_surface[row["visible_surface"]].append(row)
        elif row["source_group_id"] in selected_group_to_choice:
            selected_astro_by_surface[row["visible_surface"]].append(row)
    echo_surfaces = sorted(set(prose_by_surface) & set(selected_astro_by_surface))
    if set(echo_surfaces) != set(ECHO_NUCLEI):
        raise ValueError(f"unexpected selected cross-register echoes: {echo_surfaces}")
    echo_rows: list[dict[str, object]] = []
    for surface in echo_surfaces:
        astro_rows = selected_astro_by_surface[surface]
        prose_rows = prose_by_surface[surface]
        echo_rows.append({
            "visible_surface": surface,
            "shared_workshop_nucleus_de": ECHO_NUCLEI[surface],
            "selected_work_orders": ";".join(sorted({row["work_order_id"] for row in astro_rows})),
            "selected_astro_group_ids": ";".join(row["source_group_id"] for row in astro_rows),
            "selected_astro_readings_de": " | ".join(row["resolved_reading_de"] for row in astro_rows),
            "prose_occurrence_count": len(prose_rows),
            "prose_event_ids": ";".join(row["source_group_id"] for row in prose_rows),
            "prose_statement_ids": ";".join(dict.fromkeys(row["reading_unit_id"] for row in prose_rows)),
            "prose_readings_de": " | ".join(dict.fromkeys(row["resolved_reading_de"] for row in prose_rows)),
            "creative_reading_rule_de": "gleiche sichtbare Karte, gemeinsamer Werkstattkern, registergerechte konkrete Ausprägung",
        })
    echo_fields = [
        "visible_surface", "shared_workshop_nucleus_de", "selected_work_orders",
        "selected_astro_group_ids", "selected_astro_readings_de", "prose_occurrence_count",
        "prose_event_ids", "prose_statement_ids", "prose_readings_de", "creative_reading_rule_de",
    ]
    write_tsv(OUT / "SELECTED_9_CROSS_REGISTER_ECHOS.tsv", echo_rows, echo_fields)

    groups_by_prose_unit: dict[tuple[str, str], list[dict[str, str]]] = defaultdict(list)
    for row in source_trace:
        if row["register"] == "PROSE":
            groups_by_prose_unit[(row["work_order_id"], row["reading_unit_id"])].append(row)

    units_by_order: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in source_units:
        if row["phase"] in {"WHAT", "HOW"}:
            units_by_order[row["work_order_id"]].append(row)

    active_unit_rows: list[dict[str, object]] = []
    active_trace_rows: list[dict[str, object]] = []
    active_global_no = 0
    active_group_no = 0
    for order in orders:
        did = order["work_order_id"]
        active_local_no = 0
        local_choices = [row for row in choice_rows if row["work_order_id"] == did]
        local_choices.sort(key=lambda row: int(row["choice_order"]))
        for choice in local_choices:
            active_local_no += 1
            active_global_no += 1
            group_ids = str(choice["source_group_ids"]).split(";")
            active_unit_rows.append({
                "active_global_no": active_global_no,
                "active_unit_no": active_local_no,
                "active_unit_id": choice["selection_id"],
                "work_order_id": did,
                "work_order_title_de": order["title_de"],
                "phase": "WHEN",
                "unit_kind": "SELECTED_ASTRO_OPTION",
                "source_unit": choice["source_unit"],
                "page": choice["page"],
                "source_group_ids": choice["source_group_ids"],
                "visible_surface_sequence": choice["visible_surface_sequence"],
                "literal_reading_sequence_de": choice["current_reader_values_de"],
                "fluent_workshop_reading_de": choice["selected_workshop_value_de"],
                "execution_note_de": choice["selection_reason_de"],
            })
            for group_id in group_ids:
                active_group_no += 1
                source = trace_by_group[group_id]
                active_trace_rows.append({
                    "active_group_serial": f"P{active_group_no:03d}",
                    "work_order_id": did,
                    "active_unit_no": active_local_no,
                    "active_unit_id": choice["selection_id"],
                    "phase": "WHEN",
                    "path_role": "SELECTED_LOOKUP_VALUE",
                    "source_group_id": group_id,
                    "page": source["page"],
                    "source_unit": source["source_unit"],
                    "reading_unit_id": source["reading_unit_id"],
                    "visible_owner": source["visible_owner"],
                    "visible_surface": source["visible_surface"],
                    "lookup_id": source["lookup_id"],
                    "resolved_entry_id": source["resolved_entry_id"],
                    "resolved_reading_de": source["resolved_reading_de"],
                })

        # The already translated prose now follows in WHAT -> HOW order.
        local_prose = sorted(units_by_order[did], key=lambda row: int(row["execution_unit_no"]))
        for unit in local_prose:
            active_local_no += 1
            active_global_no += 1
            group_rows = groups_by_prose_unit[(did, unit["unit_id"])]
            group_ids = [row["source_group_id"] for row in group_rows]
            active_unit_rows.append({
                "active_global_no": active_global_no,
                "active_unit_no": active_local_no,
                "active_unit_id": unit["unit_id"],
                "work_order_id": did,
                "work_order_title_de": order["title_de"],
                "phase": unit["phase"],
                "unit_kind": unit["unit_kind"],
                "source_unit": unit["source_unit"],
                "page": unit["page"],
                "source_group_ids": ";".join(group_ids),
                "visible_surface_sequence": unit["visible_surface_sequence"],
                "literal_reading_sequence_de": unit["literal_reading_sequence_de"],
                "fluent_workshop_reading_de": unit["fluent_workshop_reading_de"],
                "execution_note_de": "aktuellen Stoff- oder Stationsposten ausführen",
            })
            for source in group_rows:
                active_group_no += 1
                active_trace_rows.append({
                    "active_group_serial": f"P{active_group_no:03d}",
                    "work_order_id": did,
                    "active_unit_no": active_local_no,
                    "active_unit_id": unit["unit_id"],
                    "phase": unit["phase"],
                    "path_role": "EXECUTED_PROSE_CARD",
                    "source_group_id": source["source_group_id"],
                    "page": source["page"],
                    "source_unit": source["source_unit"],
                    "reading_unit_id": source["reading_unit_id"],
                    "visible_owner": source["visible_owner"],
                    "visible_surface": source["visible_surface"],
                    "lookup_id": source["lookup_id"],
                    "resolved_entry_id": source["resolved_entry_id"],
                    "resolved_reading_de": source["resolved_reading_de"],
                })

    active_unit_fields = [
        "active_global_no", "active_unit_no", "active_unit_id", "work_order_id",
        "work_order_title_de", "phase", "unit_kind", "source_unit", "page", "source_group_ids",
        "visible_surface_sequence", "literal_reading_sequence_de", "fluent_workshop_reading_de",
        "execution_note_de",
    ]
    write_tsv(OUT / "FOUR_ACTIVE_129_READING_STEPS.tsv", active_unit_rows, active_unit_fields)
    active_trace_fields = [
        "active_group_serial", "work_order_id", "active_unit_no", "active_unit_id", "phase",
        "path_role", "source_group_id", "page", "source_unit", "reading_unit_id", "visible_owner",
        "visible_surface", "lookup_id", "resolved_entry_id", "resolved_reading_de",
    ]
    write_tsv(OUT / "FOUR_ACTIVE_402_GROUP_TRACE.tsv", active_trace_rows, active_trace_fields)

    active_units_by_order = Counter(row["work_order_id"] for row in active_unit_rows)
    active_groups_by_order = Counter(row["work_order_id"] for row in active_trace_rows)
    prose_units_by_order = Counter(row["work_order_id"] for row in active_unit_rows if row["unit_kind"] == "PROSE_STATEMENT")
    prose_groups_by_order = Counter(row["work_order_id"] for row in active_trace_rows if row["path_role"] == "EXECUTED_PROSE_CARD")
    selected_groups_by_order = Counter(row["work_order_id"] for row in active_trace_rows if row["path_role"] == "SELECTED_LOOKUP_VALUE")
    astro_inventory_by_order = Counter(row["work_order_id"] for row in menu_rows)
    path_rows: list[dict[str, object]] = []
    for order in orders:
        did = order["work_order_id"]
        path_rows.append({
            "work_order_id": did,
            "title_de": order["title_de"],
            "selected_condition_de": COMBINED_CONDITIONS[did],
            "astro_choice_count": choice_counter[did],
            "selected_astro_group_count": selected_groups_by_order[did],
            "unselected_astro_menu_group_count": astro_inventory_by_order[did] - selected_groups_by_order[did],
            "prose_statement_count": prose_units_by_order[did],
            "prose_group_count": prose_groups_by_order[did],
            "active_reading_step_count": active_units_by_order[did],
            "active_group_count": active_groups_by_order[did],
            "material_de": order["input_de"],
            "procedure_de": order["process_de"],
            "result_de": order["output_de"],
            "execution_order": "SELECTED_WHEN>WHAT>HOW",
        })
    path_fields = [
        "work_order_id", "title_de", "selected_condition_de", "astro_choice_count",
        "selected_astro_group_count", "unselected_astro_menu_group_count", "prose_statement_count",
        "prose_group_count", "active_reading_step_count", "active_group_count", "material_de",
        "procedure_de", "result_de", "execution_order",
    ]
    write_tsv(OUT / "FOUR_SELECTED_JOB_PATHS.tsv", path_rows, path_fields)

    sheet_lines = [
        "# Vier konkrete Werkstattzettel", "",
        "Diese Fassung führt nicht alle Diagrammwerte aus. Jeder Auftrag wählt nur die unten genannten sichtbaren Werte; die übrigen Rad-, Stern- und Paneeleinträge bleiben Nachschlageoptionen.", "",
    ]
    for path in path_rows:
        did = str(path["work_order_id"])
        sheet_lines += [
            f"## {did} — {path['title_de']}", "",
            f"**Gewählte Bedingung:** {path['selected_condition_de']}", "",
            "### WANN — sichtbare Auswahl", "",
        ]
        for choice in (row for row in choice_rows if row["work_order_id"] == did):
            sheet_lines += [
                f"- **{choice['selection_id']}** `{choice['visible_surface_sequence']}` — {choice['selected_workshop_value_de']}.",
            ]
        for phase in ("WHAT", "HOW"):
            sheet_lines += ["", f"### {'WAS' if phase == 'WHAT' else 'WIE'} — vollständige Ausführung", ""]
            last_source = None
            for unit in (row for row in active_unit_rows if row["work_order_id"] == did and row["phase"] == phase):
                if unit["source_unit"] != last_source:
                    if last_source is not None:
                        sheet_lines.append("")
                    last_source = unit["source_unit"]
                    sheet_lines += [f"#### {last_source} / {unit['page']}", ""]
                sheet_lines.append(
                    f"- **{unit['active_unit_id']}** `{unit['visible_surface_sequence']}` — {unit['fluent_workshop_reading_de']}"
                )
        sheet_lines += [
            "", f"**Abgabe:** {path['result_de']}.",
            f"**Aktiver Pfad:** {path['active_reading_step_count']} Leseschritte / {path['active_group_count']} Gruppen. Weitere {path['unselected_astro_menu_group_count']} Diagrammgruppen bleiben Auswahlmenü.", "",
        ]
    (OUT / "FOUR_FLUENT_SELECTED_JOB_SHEETS.md").write_text("\n".join(sheet_lines).rstrip() + "\n", encoding="utf-8")

    report = f"""# Vom Nachschlageblatt zum ausgeführten Auftrag

## Die wichtige Korrektur

Die vorige Vier-Auftrags-Ausgabe war als vollständiges Lesebuch richtig, aber als tatsächlicher Werkstattablauf zu wörtlich: Sie ließ einen Lehrling jede Beschriftung eines Rades oder Sternblatts nacheinander ausführen. Ein Rad mit 28 Plätzen ist jedoch ein Menü. Der Auftrag wählt einen Platz; er verbraucht nicht alle 28.

Diese Fassung trennt daher das **vollständige Nachschlageinventar** von vier **konkret gewählten Pfaden**. Alle 395 Diagrammgruppen bleiben im Menü erhalten. Für die vier Musteraufträge werden 13 sichtbare Wahlen mit zusammen 21 Diagrammgruppen aktiviert; 374 Diagrammgruppen bleiben ungewählte Alternativen.

Zu den unveränderten 381 Prosakarten kommen damit nur die 21 tatsächlich gewählten Diagrammgruppen. Die vier ausführbaren Pfade umfassen 402 Gruppen in 129 Leseschritten: 116 vollständige Prosa-Aussagen und 13 Bedingungswahlen.

## Die vier konkreten Einstellungen

1. **Wurzelbad:** rechter Ausgangssektor 8, lange geschlossene Stufe, lange Phase, Sollgrad des gewählten Platzes.
2. **Klarauszug:** freigegebener Mittel-Paneelwert, Übertragungsstation 21 und aktueller Grundgrad.
3. **Gelagerte Anwendung:** linker Platz 22 in langer Stufe, mittlere Stellung länger halten, rechter Zustand fest.
4. **Frische Pflanzenfolge:** Ausgang zum Ziel, äußere Station 7 und kurze Zielbehandlung im gewählten Grad.

Damit lesen sich die Diagramme erstmals wie ein Werkstattkopf: *Wähle diese Bedingung*, dann folgt der bereits vollständige Stoff- und Arbeitsgang. Die Auswahl ist unsere kreative Konkretisierung; sie behauptet weder eine historische Nummerierung noch einen verborgenen Schlüssel zwischen den Diagrammseiten.

## Praktischer Gewinn

Der Klarauszug bleibt der geschlossenste Musterauftrag: freigegebenen Paneelwert wählen, Station 21 als Übertragung nehmen, Grundgrad setzen, dann den Ansatz auswringen, stehen lassen und nachseihen und den klaren Auszug durch die lokalen Stationen führen. Beim gespeicherten Auftrag erklärt die gewählte lange Stufe erstmals, warum Halten, Tuch und Festmachen zusammengehören. Der frische Pflanzenfall erhält einen sauberen Ausgang-Ziel-Kopf statt einer pauschalen Lesung des ganzen linken Rades.

## Wörterbuchgewinn aus den gewählten Pfaden

Neun ausgewählte Diagrammkarten stehen mit exakt derselben sichtbaren Form auch in der Prosa. Ihre konkrete Verwendung ist bemerkenswert geschlossen: `aiin` ist Vorgabewert als Himmelsgrad oder Stoffmaß; `cheey` ein freigegebener Ablesewert oder der ausgelesene Klarauszug; `cho` der Eingangsposten; `dal` die Zielzuweisung; `dy` der aktuelle Posten; `okeey` und `okey` lange beziehungsweise kurze Stufe; `oldy` schließt eine Fortsetzung; `sheey` hält länger. Das ist derzeit der stärkste kleine gemeinsame Kartenkern zwischen praktischer Prosa und Diagrammgebrauch.

Diese neun Echos wurden nicht zu neuen langen Satzbedeutungen aufgeblasen. Die gemeinsame Bedeutung bleibt jeweils kurz; Besitzer und Register liefern den konkreten Gegenstand.

`FOUR_FLUENT_SELECTED_JOB_SHEETS.md` enthält die vier ausgeführten Zettel. `ASTRO_395_MENU_STATUS.tsv` zeigt für jeden Diagrammeintrag, ob er gewählt wurde oder als Alternative im Nachschlageblatt bleibt. `SELECTED_9_CROSS_REGISTER_ECHOS.tsv` bindet den gemeinsamen Neun-Karten-Kern.
"""
    (OUT / "MENU_TO_PATH_REPORT.md").write_text(report, encoding="utf-8")

    content_names = [
        "SELECTED_13_ASTRO_CHOICES.tsv", "ASTRO_395_MENU_STATUS.tsv",
        "SELECTED_9_CROSS_REGISTER_ECHOS.tsv",
        "FOUR_ACTIVE_129_READING_STEPS.tsv", "FOUR_ACTIVE_402_GROUP_TRACE.tsv",
        "FOUR_SELECTED_JOB_PATHS.tsv", "FOUR_FLUENT_SELECTED_JOB_SHEETS.md",
        "MENU_TO_PATH_REPORT.md",
    ]
    summary = {
        "status": "BUILT",
        "work_orders": len(orders),
        "selected_astro_choices": len(choice_rows),
        "selected_astro_groups": len(selected_group_to_choice),
        "selected_exact_surface_echoes": len(echo_rows),
        "unselected_astro_menu_groups": len(menu_rows) - len(selected_group_to_choice),
        "active_reading_steps": len(active_unit_rows),
        "active_prose_statements": sum(row["unit_kind"] == "PROSE_STATEMENT" for row in active_unit_rows),
        "active_group_count": len(active_trace_rows),
        "active_prose_groups": sum(row["path_role"] == "EXECUTED_PROSE_CARD" for row in active_trace_rows),
        "active_astro_groups": sum(row["path_role"] == "SELECTED_LOOKUP_VALUE" for row in active_trace_rows),
        "active_groups_by_work_order": dict(active_groups_by_order),
        "source_sha256": {
            "work_orders": sha256(SOURCE / "FOUR_WORK_ORDERS.tsv"),
            "reading_units": sha256(SOURCE / "FOUR_WORK_ORDER_258_UNITS.tsv"),
            "group_trace": sha256(SOURCE / "TEN_PAGE_776_WORK_ORDER_TRACE.tsv"),
        },
        "output_sha256": {name: sha256(OUT / name) for name in content_names},
    }
    (OUT / "BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
