#!/usr/bin/env python3
"""Join the creative prose master reader and owner-addressed Astro reader."""

from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
PROSE = ROOT / "experiments/yolo/sidequest_semantic_unique_master_glosses"
ASTRO = ROOT / "experiments/yolo/sidequest_semantic_astro_nomenclator_closure"


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: list[dict[str, object]], fields: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        for row in rows:
            writer.writerow({field: str(row.get(field, "")) for field in fields})


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    prose_key = read_tsv(PROSE / "UNIQUE_230_SURFACE_READER_KEY.tsv")
    prose_events = read_tsv(PROSE / "UNIQUE_381_EVENT_INTERLINEAR.tsv")
    prose_statements = read_tsv(PROSE / "UNIQUE_116_STATEMENT_EDITION.tsv")
    astro_groups = read_tsv(ASTRO / "ASTRO_395_NOMENCLATOR_CLOSED.tsv")
    astro_loci = read_tsv(ASTRO / "ASTRO_142_NOMENCLATOR_CLOSED_LOCI.tsv")

    prose_by_surface = {row["visible_surface"]: row for row in prose_key}

    # In the diagrams, owner + visible surface is the compact lookup key.
    astro_by_owner_surface: dict[tuple[str, str], list[dict[str, str]]] = defaultdict(list)
    for row in astro_groups:
        astro_by_owner_surface[(row["local_image_owner"], row["surface_display"])].append(row)
    for key, group in astro_by_owner_surface.items():
        readings = {row["closed_workshop_reading_de"] for row in group}
        if len(readings) != 1:
            raise ValueError(f"owner-surface reading collision: {key} -> {readings}")

    reader_rows: list[dict[str, object]] = []
    prose_lookup: dict[str, str] = {}
    for index, row in enumerate(sorted(prose_key, key=lambda item: item["visible_surface"]), start=1):
        lookup_id = f"PR{index:03d}"
        prose_lookup[row["visible_surface"]] = lookup_id
        reader_rows.append({
            "lookup_id": lookup_id,
            "register": "PROSE",
            "visible_owner": "NOT_REQUIRED",
            "visible_surface": row["visible_surface"],
            "resolved_entry_id": row["master_card_id"],
            "master_or_local_head": row["master_head_form"],
            "short_workshop_reading_de": row["unique_short_meaning_de"],
            "component_or_local_parse": row["component_reading"],
            "namespace": "PROSE_SHARED_MASTER_DICTIONARY",
            "source_occurrences": row["observed_event_count"],
            "lookup_rule_de": "sichtbare Form direkt im Prosa-Meisterbuch nachschlagen",
            "orientation_rule": "STATEMENT_ORDER__LINE_BREAK_NOT_SENTENCE_END",
            "crosspage_rule": "PROSE_REGISTER_ONLY",
        })

    astro_lookup: dict[tuple[str, str], str] = {}
    for index, (key, group) in enumerate(sorted(astro_by_owner_surface.items()), start=1):
        owner, surface = key
        first = group[0]
        lookup_id = f"AR{index:03d}"
        astro_lookup[key] = lookup_id
        reader_rows.append({
            "lookup_id": lookup_id,
            "register": "ASTRO",
            "visible_owner": owner,
            "visible_surface": surface,
            "resolved_entry_id": f"ASTRO_OWNER_VALUE_{index:03d}",
            "master_or_local_head": surface,
            "short_workshop_reading_de": first["closed_workshop_reading_de"],
            "component_or_local_parse": first["local_segmentation"],
            "namespace": first["namespace_id"],
            "source_occurrences": len(group),
            "lookup_rule_de": "sichtbaren Stern-, Sektor- oder Radbesitzer zeigen und dort die Form nachschlagen",
            "orientation_rule": first["orientation_rule"],
            "crosspage_rule": first["crosspage_rule"],
        })
    reader_fields = [
        "lookup_id", "register", "visible_owner", "visible_surface", "resolved_entry_id",
        "master_or_local_head", "short_workshop_reading_de", "component_or_local_parse", "namespace",
        "source_occurrences", "lookup_rule_de", "orientation_rule", "crosspage_rule",
    ]
    write_tsv(OUT / "TEN_PAGE_607_READER_KEY.tsv", reader_rows, reader_fields)

    # Cross-register shared surfaces retain separate register expansions.
    astro_by_surface: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in astro_groups:
        astro_by_surface[row["surface_display"]].append(row)
    shared_surfaces = sorted(set(prose_by_surface) & set(astro_by_surface))
    bridge_rows: list[dict[str, object]] = []
    for surface in shared_surfaces:
        prose = prose_by_surface[surface]
        astro = astro_by_surface[surface]
        bridge_rows.append({
            "visible_surface": surface,
            "prose_master_card_id": prose["master_card_id"],
            "prose_unique_reading_de": prose["unique_short_meaning_de"],
            "prose_component": prose["component_reading"],
            "astro_occurrences": len(astro),
            "astro_owner_count": len({row["local_image_owner"] for row in astro}),
            "astro_namespaces": ";".join(sorted({row["namespace_id"] for row in astro})),
            "astro_owner_readings_de": " || ".join(sorted({row["closed_workshop_reading_de"] for row in astro})),
            "bridge_rule": "SAME_VISIBLE_FORM__REGISTER_AND_VISIBLE_OWNER_SUPPLY_EXPANSION",
        })
    bridge_fields = [
        "visible_surface", "prose_master_card_id", "prose_unique_reading_de", "prose_component",
        "astro_occurrences", "astro_owner_count", "astro_namespaces", "astro_owner_readings_de", "bridge_rule",
    ]
    write_tsv(OUT / "CROSS_REGISTER_44_SURFACE_BRIDGE.tsv", bridge_rows, bridge_fields)

    # Unified 776-group trace.
    trace_rows: list[dict[str, object]] = []
    for event in prose_events:
        lookup_id = prose_lookup[event["surface_display"]]
        trace_rows.append({
            "unified_serial": f"U{len(trace_rows) + 1:03d}",
            "register": "PROSE",
            "page": event["page"],
            "source_group_id": event["event_id"],
            "reading_unit_id": event["statement_id"],
            "visible_owner": "NOT_REQUIRED",
            "visible_surface": event["surface_display"],
            "lookup_id": lookup_id,
            "resolved_entry_id": event["master_card_id"],
            "resolved_reading_de": event["unique_short_meaning_de"],
            "lookup_status": "DIRECT_PROSE_SURFACE_PASS",
        })
    for group in astro_groups:
        key = (group["local_image_owner"], group["surface_display"])
        lookup_id = astro_lookup[key]
        trace_rows.append({
            "unified_serial": f"U{len(trace_rows) + 1:03d}",
            "register": "ASTRO",
            "page": group["page"],
            "source_group_id": group["opaque_local_id"],
            "reading_unit_id": group["locus"],
            "visible_owner": group["local_image_owner"],
            "visible_surface": group["surface_display"],
            "lookup_id": lookup_id,
            "resolved_entry_id": next(row["resolved_entry_id"] for row in reader_rows if row["lookup_id"] == lookup_id),
            "resolved_reading_de": group["closed_workshop_reading_de"],
            "lookup_status": "OWNER_PLUS_SURFACE_ASTRO_PASS",
        })
    trace_fields = [
        "unified_serial", "register", "page", "source_group_id", "reading_unit_id", "visible_owner",
        "visible_surface", "lookup_id", "resolved_entry_id", "resolved_reading_de", "lookup_status",
    ]
    write_tsv(OUT / "TEN_PAGE_776_READER_TRACE.tsv", trace_rows, trace_fields)

    # 116 prose statements plus 142 diagram loci.
    prose_events_by_statement: dict[str, list[dict[str, str]]] = defaultdict(list)
    for event in prose_events:
        prose_events_by_statement[event["statement_id"]].append(event)
    astro_groups_by_locus: dict[tuple[str, str], list[dict[str, str]]] = defaultdict(list)
    for group in astro_groups:
        astro_groups_by_locus[(group["page"], group["locus"])].append(group)

    unit_rows: list[dict[str, object]] = []
    for statement in prose_statements:
        ee = prose_events_by_statement[statement["statement_id"]]
        unit_rows.append({
            "unit_id": statement["statement_id"],
            "unit_kind": "PROSE_STATEMENT",
            "page": statement["page"],
            "record_or_diagram": statement["record_unit_id"],
            "visible_owner": "PICTURE_OR_ACTIVE_RECORD_OWNER",
            "visible_surface_sequence": statement["surface_sequence"],
            "lookup_sequence": " ".join(prose_lookup[row["surface_display"]] for row in ee),
            "literal_reading_sequence_de": statement["unique_literal_sequence_de"],
            "fluent_workshop_reading_de": statement["fluent_workshop_sentence_de"],
            "reading_rule": "DIRECT_PROSE_SURFACE_THEN_STATEMENT_ORDER",
        })
    for locus in astro_loci:
        gg = astro_groups_by_locus[(locus["page"], locus["locus"])]
        unit_rows.append({
            "unit_id": locus["locus"],
            "unit_kind": "ASTRO_VISIBLE_LOCUS",
            "page": locus["page"],
            "record_or_diagram": locus["diagram_id"],
            "visible_owner": locus["local_image_owner"],
            "visible_surface_sequence": locus["surface_sequence"],
            "lookup_sequence": " ".join(astro_lookup[(row["local_image_owner"], row["surface_display"])] for row in gg),
            "literal_reading_sequence_de": locus["compact_default_sequence_de"],
            "fluent_workshop_reading_de": locus["closed_locus_reading_de"],
            "reading_rule": "SELECT_VISIBLE_OWNER__READ_LOCAL_GROUPS__NO_CYCLIC_ORDER",
        })
    unit_fields = [
        "unit_id", "unit_kind", "page", "record_or_diagram", "visible_owner", "visible_surface_sequence",
        "lookup_sequence", "literal_reading_sequence_de", "fluent_workshop_reading_de", "reading_rule",
    ]
    write_tsv(OUT / "TEN_PAGE_258_READING_UNITS.tsv", unit_rows, unit_fields)

    manual = [
        "# Lehrlingsregel für alle zehn Seiten", "",
        "## Prosa", "",
        "1. Suche jede sichtbare Form direkt im Prosaabschnitt des 607er-Schlüssels.",
        "2. Lies die Karten in Aussagefolge; ein Zeilenwechsel beendet die Aussage nicht.",
        "3. Ergänze den sichtbaren Pflanzen-, Becken- oder Arbeitsbesitzer.", "",
        "## Kreis- und Sternseiten", "",
        "1. Zeige zuerst auf den sichtbaren Stern, Sektor, Ring oder die Legendenstelle.",
        "2. Suche erst die Kombination aus Besitzer und Oberfläche im Astroabschnitt.",
        "3. Lies nur die Gruppen dieses sichtbaren Ortes. Beginne nicht automatisch oben und laufe nicht im Kreis.",
        "4. Verbinde f68 und f69 nicht über gleiche Zahlen oder gleiche Oberflächen.", "",
        "## Gemeinsame Formen", "",
        "Vierundvierzig Oberflächen stehen in beiden Registern. In der Prosa liefern sie die praktische Handlung; im Diagramm liefert der sichtbare Besitzer die himmlische oder tabellarische Ausprägung. Das ist ein gemeinsamer Werkstattkern, kein wörtlicher Import von Wasser oder Pflanzen an den Himmel.", "",
    ]
    (OUT / "APPRENTICE_TEN_PAGE_READER_MANUAL.md").write_text("\n".join(manual).rstrip() + "\n", encoding="utf-8")

    readable = [
        "# Vollständiges Zehnseiten-Lesebuch", "",
        "Die sieben Prosaseiten werden über die gemeinsame Meisterkarte gelesen; die drei Diagrammseiten über sichtbaren Besitzer plus lokale Oberfläche.", "",
    ]
    current_section = None
    for row in unit_rows:
        section = f"{row['unit_kind']} · {row['record_or_diagram']} · {row['page']}"
        if section != current_section:
            current_section = section
            readable += [f"## {section}", ""]
        readable += [
            f"### {row['unit_id']}", "",
            f"- Oberfläche: `{row['visible_surface_sequence']}`",
            f"- Wörtlich: {row['literal_reading_sequence_de']}",
            f"- Werkstattlektüre: {row['fluent_workshop_reading_de']}", "",
        ]
    (OUT / "COMPLETE_TEN_PAGE_READER.md").write_text("\n".join(readable).rstrip() + "\n", encoding="utf-8")

    surface_conflicts = 0
    for surface, group in astro_by_surface.items():
        if len({row["closed_workshop_reading_de"] for row in group}) > 1:
            surface_conflicts += 1
    report = [
        "# Einheitlicher Leser für alle zehn Seiten", "",
        "## Ergebnis", "",
        "Die aktuelle Ausgabe liest nun alle 776 sichtbaren Gruppen mit einem einzigen zweigeteilten Werkstattschlüssel. Die sieben Prosaseiten liefern 381 Ereignisse in 116 Aussagen; die drei Diagrammseiten 395 Gruppen an 142 sichtbaren Orten.", "",
        f"Für die Prosa genügen 230 sichtbare Formen, die direkt auf 173 eindeutige Meisterkarten führen. Für die Diagramme genügen 377 Kombinationen aus sichtbarem Besitzer und Oberfläche. Zusammen besitzt das Taschenbuch 607 Nachschlagezeilen.", "",
        f"Die Besitzerregel ist notwendig: Astro allein enthält 301 verschiedene Oberflächen, und {surface_conflicts} davon tragen an verschiedenen sichtbaren Orten verschiedene konkrete Lesungen. Innerhalb derselben Besitzer-Oberflächen-Kombination entsteht dagegen kein Bedeutungswiderspruch.", "",
        "## Gemeinsamer Kartenbestand", "",
        f"Prosa und Diagramme teilen {len(shared_surfaces)} sichtbare Formen. Diese werden nicht als zwei zufällig gleich geschriebene Wörter behandelt, sondern als Werkstattkarten mit gemeinsamem operativem Kern und registerabhängiger Ausprägung: praktisch im Text, himmlisch oder tabellarisch am Diagrammbesitzer.", "",
        "## Leseregel", "",
        "Prosa: Oberfläche -> Meisterkarte -> eindeutiger Arbeitswert. Diagramm: sichtbarer Besitzer + Oberfläche -> lokaler Himmels- oder Tabellenwert. Weder Kreisrichtung noch gemeinsamer Startpunkt noch ein f68-f69-Schlüssel wird benötigt.", "",
        "Das ist die kreative zehnseitige Arbeitstheorie; die vollständige Lesbarkeit folgt aus dem gewählten Werkstattcodebuch und ist keine Behauptung einer historisch bestätigten Entzifferung.", "",
    ]
    (OUT / "TEN_PAGE_UNIFIED_READER_REPORT.md").write_text("\n".join(report).rstrip() + "\n", encoding="utf-8")

    content_names = [
        "TEN_PAGE_607_READER_KEY.tsv", "CROSS_REGISTER_44_SURFACE_BRIDGE.tsv",
        "TEN_PAGE_776_READER_TRACE.tsv", "TEN_PAGE_258_READING_UNITS.tsv",
        "APPRENTICE_TEN_PAGE_READER_MANUAL.md", "COMPLETE_TEN_PAGE_READER.md",
        "TEN_PAGE_UNIFIED_READER_REPORT.md",
    ]
    summary = {
        "status": "BUILT",
        "prose_reader_keys": len(prose_key),
        "astro_owner_surface_keys": len(astro_by_owner_surface),
        "unified_reader_keys": len(reader_rows),
        "prose_events": len(prose_events),
        "astro_groups": len(astro_groups),
        "unified_groups": len(trace_rows),
        "prose_statements": len(prose_statements),
        "astro_loci": len(astro_loci),
        "reading_units": len(unit_rows),
        "cross_register_shared_surfaces": len(shared_surfaces),
        "astro_surface_reading_conflicts_without_owner": surface_conflicts,
        "files_sha256": {name: sha(OUT / name) for name in content_names},
    }
    (OUT / "BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
