#!/usr/bin/env python3
"""Turn the current ten-page reader into four execution-order work orders.

The older casebook supplies only the creative dossier assignment.  Every
surface reading comes from the newer unified reader.  The shop executes each
order as WHEN -> WHAT -> HOW even though the manuscript sections are arranged
as WHAT / HOW / WHEN.
"""

from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
READER = ROOT / "experiments/yolo/sidequest_semantic_ten_page_unified_reader"
CASEBOOK = ROOT / "experiments/yolo/sidequest_semantic_integrated_workshop_casebook"
PHASE_RANK = {"WHEN": 0, "WHAT": 1, "HOW": 2}
PHASE_DE = {"WHEN": "WANN", "WHAT": "WAS", "HOW": "WIE"}


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


def main() -> None:
    source_trace = read_tsv(READER / "TEN_PAGE_776_READER_TRACE.tsv")
    source_units = read_tsv(READER / "TEN_PAGE_258_READING_UNITS.tsv")
    old_context = read_tsv(CASEBOOK / "TEN_PAGE_776_CASE_CONTEXT.tsv")
    old_dossiers = read_tsv(CASEBOOK / "FOUR_WORKSHOP_DOSSIERS.tsv")
    old_steps = read_tsv(CASEBOOK / "WORKFLOW_STEPS.tsv")

    context_by_group = {row["local_unit_id"]: row for row in old_context}
    if len(context_by_group) != len(old_context):
        raise ValueError("old case assignment contains duplicate source groups")
    if {row["source_group_id"] for row in source_trace} != set(context_by_group):
        raise ValueError("current reader and old creative assignment do not cover the same 776 groups")

    dossier_by_id = {row["dossier_id"]: row for row in old_dossiers}
    dossier_order = {row["dossier_id"]: index for index, row in enumerate(old_dossiers, start=1)}
    old_step_by_key = {(row["dossier_id"], row["source_unit"]): row for row in old_steps}

    # Freeze the actual execution order: condition first, material second,
    # procedure third.  The relative order inside each phase remains the old
    # dossier order.
    step_order: dict[tuple[str, str], int] = {}
    phase_step: dict[tuple[str, str], int] = {}
    ordered_step_keys: list[tuple[str, str]] = []
    for dossier in old_dossiers:
        did = dossier["dossier_id"]
        local = [row for row in old_steps if row["dossier_id"] == did]
        local.sort(key=lambda row: (PHASE_RANK[row["phase"]], int(row["step_no"])))
        phase_seen: Counter[str] = Counter()
        for execution_step, row in enumerate(local, start=1):
            key = (did, row["source_unit"])
            phase_seen[row["phase"]] += 1
            step_order[key] = execution_step
            phase_step[key] = phase_seen[row["phase"]]
            ordered_step_keys.append(key)

    joined_groups: list[dict[str, object]] = []
    assignment_by_unit: dict[tuple[str, str], tuple[str, str, str]] = {}
    source_trace_index: dict[str, int] = {}
    for source_index, row in enumerate(source_trace, start=1):
        source_trace_index[row["source_group_id"]] = source_index
        assignment = context_by_group[row["source_group_id"]]
        did = assignment["dossier_id"]
        phase = assignment["case_phase"]
        source_unit = assignment["case_source_unit"]
        unit_key = (row["register"], row["reading_unit_id"])
        unit_assignment = (did, phase, source_unit)
        prior = assignment_by_unit.setdefault(unit_key, unit_assignment)
        if prior != unit_assignment:
            raise ValueError(f"reading unit split between work orders: {unit_key}")
        joined_groups.append({
            **row,
            "work_order_id": did,
            "work_order_title_de": dossier_by_id[did]["title_de"],
            "phase": phase,
            "execution_step": step_order[(did, source_unit)],
            "phase_step": phase_step[(did, source_unit)],
            "source_unit": source_unit,
            "assignment_status": "CREATIVE_WORK_ORDER_PAIRING__CURRENT_READER_VALUE",
        })

    # Bind every current reading unit to exactly one work order and source
    # step.  Input order supplies stable order within a source record/module.
    unit_rows: list[dict[str, object]] = []
    unit_index_by_key: dict[tuple[str, str], int] = {}
    units_by_step: dict[tuple[str, str], list[dict[str, object]]] = defaultdict(list)
    execution_unit_counter: Counter[str] = Counter()
    source_units_sorted = sorted(
        enumerate(source_units, start=1),
        key=lambda pair: (
            dossier_order[assignment_by_unit[("PROSE" if pair[1]["unit_kind"] == "PROSE_STATEMENT" else "ASTRO", pair[1]["unit_id"])][0]],
            step_order[(
                assignment_by_unit[("PROSE" if pair[1]["unit_kind"] == "PROSE_STATEMENT" else "ASTRO", pair[1]["unit_id"])][0],
                assignment_by_unit[("PROSE" if pair[1]["unit_kind"] == "PROSE_STATEMENT" else "ASTRO", pair[1]["unit_id"])][2],
            )],
            pair[0],
        ),
    )
    for original_index, row in source_units_sorted:
        register = "PROSE" if row["unit_kind"] == "PROSE_STATEMENT" else "ASTRO"
        key = (register, row["unit_id"])
        did, phase, source_unit = assignment_by_unit[key]
        execution_unit_counter[did] += 1
        execution_unit_no = execution_unit_counter[did]
        unit_index_by_key[key] = execution_unit_no
        enriched = {
            "work_order_id": did,
            "work_order_title_de": dossier_by_id[did]["title_de"],
            "execution_unit_no": execution_unit_no,
            "execution_step": step_order[(did, source_unit)],
            "phase": phase,
            "phase_step": phase_step[(did, source_unit)],
            "source_unit": source_unit,
            **row,
            "execution_instruction_de": (
                "Bedingungswert wählen und auf den Auftrag übernehmen"
                if phase == "WHEN"
                else "Materialposten vorbereiten und an den Arbeitsgang übergeben"
                if phase == "WHAT"
                else "Arbeitsgang am sichtbaren Besitzer ausführen"
            ),
        }
        unit_rows.append(enriched)
        units_by_step[(did, source_unit)].append(enriched)

    unit_fields = [
        "work_order_id", "work_order_title_de", "execution_unit_no", "execution_step", "phase",
        "phase_step", "source_unit", "unit_id", "unit_kind", "page", "record_or_diagram",
        "visible_owner", "visible_surface_sequence", "lookup_sequence", "literal_reading_sequence_de",
        "fluent_workshop_reading_de", "reading_rule", "execution_instruction_de",
    ]
    write_tsv(OUT / "FOUR_WORK_ORDER_258_UNITS.tsv", unit_rows, unit_fields)

    # Reorder the complete group trace to actual shop execution order.
    joined_groups.sort(key=lambda row: (
        dossier_order[str(row["work_order_id"])],
        int(row["execution_step"]),
        unit_index_by_key[(str(row["register"]), str(row["reading_unit_id"]))],
        source_trace_index[str(row["source_group_id"])],
    ))
    trace_rows: list[dict[str, object]] = []
    for work_order_serial, row in enumerate(joined_groups, start=1):
        trace_rows.append({
            "work_order_serial": f"W{work_order_serial:03d}",
            "source_unified_serial": row["unified_serial"],
            "work_order_id": row["work_order_id"],
            "work_order_title_de": row["work_order_title_de"],
            "phase": row["phase"],
            "execution_step": row["execution_step"],
            "phase_step": row["phase_step"],
            "source_unit": row["source_unit"],
            "reading_unit_id": row["reading_unit_id"],
            "register": row["register"],
            "page": row["page"],
            "source_group_id": row["source_group_id"],
            "visible_owner": row["visible_owner"],
            "visible_surface": row["visible_surface"],
            "lookup_id": row["lookup_id"],
            "resolved_entry_id": row["resolved_entry_id"],
            "resolved_reading_de": row["resolved_reading_de"],
            "lookup_status": row["lookup_status"],
            "assignment_status": row["assignment_status"],
        })
    trace_fields = [
        "work_order_serial", "source_unified_serial", "work_order_id", "work_order_title_de",
        "phase", "execution_step", "phase_step", "source_unit", "reading_unit_id", "register",
        "page", "source_group_id", "visible_owner", "visible_surface", "lookup_id",
        "resolved_entry_id", "resolved_reading_de", "lookup_status", "assignment_status",
    ]
    write_tsv(OUT / "TEN_PAGE_776_WORK_ORDER_TRACE.tsv", trace_rows, trace_fields)

    groups_by_step: Counter[tuple[str, str]] = Counter(
        (str(row["work_order_id"]), str(row["source_unit"])) for row in trace_rows
    )
    step_rows: list[dict[str, object]] = []
    for did, source_unit in sorted(ordered_step_keys, key=lambda key: (dossier_order[key[0]], step_order[key])):
        old = old_step_by_key[(did, source_unit)]
        current_units = units_by_step[(did, source_unit)]
        phase = old["phase"]
        step_rows.append({
            "work_order_id": did,
            "work_order_title_de": dossier_by_id[did]["title_de"],
            "execution_step": step_order[(did, source_unit)],
            "phase": phase,
            "phase_step": phase_step[(did, source_unit)],
            "source_unit": source_unit,
            "page": old["page"],
            "reading_unit_count": len(current_units),
            "visible_group_count": groups_by_step[(did, source_unit)],
            "compact_command_de": old["short_action_de"],
            "complete_current_reading_de": " ".join(str(row["fluent_workshop_reading_de"]) for row in current_units),
            "handoff_de": (
                "Bedingung auf die Auftragskarte schreiben; dann Material bereitstellen"
                if phase == "WHEN"
                else "vorbereiteten Posten an die Ausführungsstation übergeben"
                if phase == "WHAT"
                else "Ergebnis, Ziel und Abschluss auf der Auftragskarte vermerken"
            ),
        })
    step_fields = [
        "work_order_id", "work_order_title_de", "execution_step", "phase", "phase_step",
        "source_unit", "page", "reading_unit_count", "visible_group_count", "compact_command_de",
        "complete_current_reading_de", "handoff_de",
    ]
    write_tsv(OUT / "TWENTY_FIVE_EXECUTION_STEPS.tsv", step_rows, step_fields)

    trace_by_dossier: dict[str, list[dict[str, object]]] = defaultdict(list)
    units_by_dossier: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in trace_rows:
        trace_by_dossier[str(row["work_order_id"])].append(row)
    for row in unit_rows:
        units_by_dossier[str(row["work_order_id"])].append(row)

    order_rows: list[dict[str, object]] = []
    for dossier in old_dossiers:
        did = dossier["dossier_id"]
        local_trace = trace_by_dossier[did]
        local_units = units_by_dossier[did]
        group_phase = Counter(str(row["phase"]) for row in local_trace)
        unit_phase = Counter(str(row["phase"]) for row in local_units)
        order_rows.append({
            "work_order_id": did,
            "title_de": dossier["title_de"],
            "execution_order": "WHEN>WHAT>HOW",
            "when_pages": dossier["when_pages"],
            "what_pages": dossier["what_pages"],
            "how_pages": dossier["how_pages"],
            "when_source_units": dossier["astro_modules"],
            "what_source_units": ";".join(unit for unit in dossier["record_units"].split(";") if unit.startswith("H")),
            "how_source_units": ";".join(unit for unit in dossier["record_units"].split(";") if unit.startswith("B")),
            "when_reading_units": unit_phase["WHEN"],
            "what_reading_units": unit_phase["WHAT"],
            "how_reading_units": unit_phase["HOW"],
            "when_groups": group_phase["WHEN"],
            "what_groups": group_phase["WHAT"],
            "how_groups": group_phase["HOW"],
            "total_reading_units": len(local_units),
            "total_groups": len(local_trace),
            "condition_de": dossier["condition_de"],
            "input_de": dossier["input_de"],
            "process_de": dossier["process_de"],
            "output_de": dossier["output_de"],
            "use_de": dossier["use_de"],
            "pairing_status": "CREATIVE_WORKSHOP_SCENARIO__NO_MANUSCRIPT_CROSS_REFERENCE_CLAIM",
        })
    order_fields = [
        "work_order_id", "title_de", "execution_order", "when_pages", "what_pages", "how_pages",
        "when_source_units", "what_source_units", "how_source_units", "when_reading_units",
        "what_reading_units", "how_reading_units", "when_groups", "what_groups", "how_groups",
        "total_reading_units", "total_groups", "condition_de", "input_de", "process_de",
        "output_de", "use_de", "pairing_status",
    ]
    write_tsv(OUT / "FOUR_WORK_ORDERS.tsv", order_rows, order_fields)

    # Four compact job cards for an apprentice at the bench.
    card_lines = [
        "# Vier Werkstatt-Auftragskarten", "",
        "Arbeitsrichtung für alle vier Karten: **WANN wählen → WAS bereitstellen → WIE ausführen**.",
        "Die Bilder liefern den jeweils aktiven Besitzer; die Kartenfolge liefert den Arbeitsgang.", "",
    ]
    for order in order_rows:
        did = str(order["work_order_id"])
        card_lines += [
            f"## {did} — {order['title_de']}", "",
            f"**1 · WANN ({order['when_pages']}):** {order['condition_de']}.", "",
        ]
        for step in (row for row in step_rows if row["work_order_id"] == did and row["phase"] == "WHEN"):
            card_lines.append(f"- {step['source_unit']}: {step['compact_command_de']}.")
        card_lines += ["", f"**2 · WAS ({order['what_pages']}):** {order['input_de']}.", ""]
        for step in (row for row in step_rows if row["work_order_id"] == did and row["phase"] == "WHAT"):
            card_lines.append(f"- {step['source_unit']}: {step['compact_command_de']}.")
        card_lines += ["", f"**3 · WIE ({order['how_pages']}):** {order['process_de']}.", ""]
        for step in (row for row in step_rows if row["work_order_id"] == did and row["phase"] == "HOW"):
            card_lines.append(f"- {step['source_unit']}: {step['compact_command_de']}.")
        card_lines += [
            "",
            f"**Abgabe:** {order['output_de']}.",
            f"**Umfang:** {order['total_reading_units']} Leseeinheiten / {order['total_groups']} sichtbare Gruppen.", "",
        ]
    (OUT / "FOUR_ONE_PAGE_JOB_CARDS.md").write_text("\n".join(card_lines).rstrip() + "\n", encoding="utf-8")

    # Full readable edition in execution order, carrying every one of the 258
    # statement/locus readings from the current reader.
    complete_lines = [
        "# Vier vollständige Werkstattaufträge", "",
        "Hier steht die Benutzungsreihenfolge, nicht die Buchreihenfolge: zuerst wird die sichtbare Bedingung gewählt, dann der Stoffposten vorbereitet, dann der Arbeitsgang ausgeführt.", "",
    ]
    for order in order_rows:
        did = str(order["work_order_id"])
        complete_lines += [
            f"## {did} — {order['title_de']}", "",
            f"**Auftrag:** Zuerst {order['condition_de']}. Dann {order['input_de']} bereitstellen. Anschließend {order['process_de']}. Ergebnis: {order['output_de']}.", "",
        ]
        last_phase = None
        last_step = None
        for unit in units_by_dossier[did]:
            phase = str(unit["phase"])
            step = int(unit["execution_step"])
            if phase != last_phase:
                last_phase = phase
                phase_execution_steps = [
                    int(row["execution_step"])
                    for row in step_rows
                    if row["work_order_id"] == did and row["phase"] == phase
                ]
                span = (
                    str(phase_execution_steps[0])
                    if len(phase_execution_steps) == 1
                    else f"{phase_execution_steps[0]}–{phase_execution_steps[-1]}"
                )
                complete_lines += [f"### {PHASE_DE[phase]} — Schritte {span}", ""]
            if step != last_step:
                last_step = step
                source = str(unit["source_unit"])
                step_info = old_step_by_key[(did, source)]
                complete_lines += [
                    f"#### Schritt {step}: {source} / {step_info['page']} — {step_info['short_action_de']}", "",
                ]
            complete_lines += [
                f"- **{unit['unit_id']}** `{unit['visible_surface_sequence']}`",
                f"  - wörtlich: {unit['literal_reading_sequence_de']}",
                f"  - Werkstattlektüre: {unit['fluent_workshop_reading_de']}",
            ]
        complete_lines += ["", "**Rückgabe an den Meister:** Auftrag, gewählte Bedingung, Stoffposten und ausgeführter Abschluss werden gemeinsam zurückgelesen.", ""]
    (OUT / "FOUR_COMPLETE_WORK_ORDERS.md").write_text("\n".join(complete_lines).rstrip() + "\n", encoding="utf-8")

    report_lines = [
        "# Vier ausführbare Werkstattaufträge", "", "## Ergebnis", "",
        "Der bisherige Zehnseiten-Leser ist jetzt als tatsächlicher Arbeitsablauf gesetzt. Die Buchteile liefern weiterhin Pflanzenstoff, Ausführung und Himmels-/Zeitbedingung; am Werktisch wird diese Ordnung jedoch umgedreht: **WANN → WAS → WIE**.", "",
        "Alle 776 sichtbaren Gruppen erscheinen genau einmal: 381 Prosakarten in 116 Aussagen und 395 Diagrammgruppen an 142 sichtbaren Orten. Daraus entstehen 258 lesbare Arbeitseinheiten und 25 größere Ausführungsschritte in vier Aufträgen.", "",
        "## Die vier Aufträge", "",
    ]
    for order in order_rows:
        report_lines.append(
            f"- **{order['title_de']}** — zuerst {order['condition_de']}; dann {order['input_de']}; schließlich {order['process_de']}. ({order['total_groups']} Gruppen)"
        )
    report_lines += [
        "", "## Was sich verbessert", "",
        "Die ältere Dossierfassung erzählte erst WAS, dann WIE und setzte WANN ans Ende. Das war eine Beschreibung des Buchaufbaus, aber kein glaubwürdiger Auftrag an einen Schreiber oder Werkstattgehilfen. Die neue Ausgabe trägt zuerst die Bedingung ein, holt dann den richtigen Materialposten und führt erst danach die Stationsfolge aus. Dadurch werden die Astrotafeln zu Auftragsköpfen statt nachträglichen Kommentaren.", "",
        "Die jüngste 173-Karten-Lesung wird unverändert übernommen. Alte Mehrdeutigkeiten wie mehrere Karten mit derselben pauschalen Bedeutung sind deshalb nicht wieder eingeführt; jede Prosakarte und jede Besitzer-Oberflächen-Kombination der Diagramme behält ihren aktuellen konkreten Werkstattwert.", "",
        "## Praktische Lesung", "",
        "Am geschlossensten wirkt der Klarauszug-Auftrag: Sternstation wählen, Kräuter- oder Blütenansatz auswringen und stehen lassen, nachseihen und den klaren Auszug anschließend durch die sichtbaren lokalen Stationen führen. Der Wurzelbad-Auftrag ist der beste Lehrfall für eine gemeinsame Beckenroutine. Die gelagerte Anwendung trennt Auswahl, Tucharbeit und Reinigung. Die frische Pflanzenfolge bleibt der längste Meisterfall mit wiederholten Übergaben.", "",
        "Die Paarungen bleiben unsere kreative Werkstattordnung; es wird kein geschriebener Querverweis zwischen den Seiten erfunden. Ebenso werden die getrennten Diagramme nicht durch einen unsichtbaren gemeinsamen Schlüssel verbunden.", "",
        "Die kurzen Karten stehen in `FOUR_ONE_PAGE_JOB_CARDS.md`; die vollständigen 258 Lesungen in `FOUR_COMPLETE_WORK_ORDERS.md`; die Gruppe-für-Gruppe-Ausführung in `TEN_PAGE_776_WORK_ORDER_TRACE.tsv`.", "",
    ]
    (OUT / "FOUR_WORK_ORDER_REPORT.md").write_text("\n".join(report_lines), encoding="utf-8")

    content_files = [
        "FOUR_WORK_ORDERS.tsv", "TWENTY_FIVE_EXECUTION_STEPS.tsv", "FOUR_WORK_ORDER_258_UNITS.tsv",
        "TEN_PAGE_776_WORK_ORDER_TRACE.tsv", "FOUR_ONE_PAGE_JOB_CARDS.md",
        "FOUR_COMPLETE_WORK_ORDERS.md", "FOUR_WORK_ORDER_REPORT.md",
    ]
    summary = {
        "status": "BUILT",
        "execution_order": "WHEN>WHAT>HOW",
        "work_orders": len(order_rows),
        "execution_steps": len(step_rows),
        "reading_units": len(unit_rows),
        "prose_statements": sum(row["unit_kind"] == "PROSE_STATEMENT" for row in source_units),
        "astro_loci": sum(row["unit_kind"] == "ASTRO_VISIBLE_LOCUS" for row in source_units),
        "visible_groups": len(trace_rows),
        "prose_groups": sum(row["register"] == "PROSE" for row in source_trace),
        "astro_groups": sum(row["register"] == "ASTRO" for row in source_trace),
        "work_order_group_counts": {row["work_order_id"]: row["total_groups"] for row in order_rows},
        "source_sha256": {
            "reader_trace": sha256(READER / "TEN_PAGE_776_READER_TRACE.tsv"),
            "reader_units": sha256(READER / "TEN_PAGE_258_READING_UNITS.tsv"),
            "creative_assignment": sha256(CASEBOOK / "TEN_PAGE_776_CASE_CONTEXT.tsv"),
        },
        "output_sha256": {name: sha256(OUT / name) for name in content_files},
    }
    (OUT / "BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
