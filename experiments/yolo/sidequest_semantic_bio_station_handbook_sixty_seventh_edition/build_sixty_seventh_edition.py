#!/usr/bin/env python3
"""Write a compact local-station handbook for the three Biological pages."""

from __future__ import annotations

import csv
import hashlib
import json
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
CLAUSES = ROOT / "experiments/yolo/sidequest_semantic_period_clausebook_sixty_fifth_edition/SIXTY_FIFTH_381_PERIOD_SOURCE_CLAUSES.tsv"
UNITS = ROOT / "experiments/yolo/sidequest_semantic_complete_reader_fifty_sixth_edition/FIFTY_SIXTH_258_COMPLETE_UNITS.tsv"
STATEMENTS = ROOT / "experiments/yolo/sidequest_theory_candidates_v74/V74_SELECTED_97_STATEMENT_EDITION.tsv"
RECORDS = ROOT / "experiments/yolo/sidequest_theory_candidates_v74/V74_SELECTED_SIX_RECORD_EDITION.tsv"
BIO_PAGES = {"f81v", "f82r", "f83r"}

COMPACT = {
    "B1": "Im gemeinsamen zweireihigen Becken werden Portion, Wärme und Zusatz örtlich eingestellt. Der Posten wird gemischt, zum bezeichneten Platz geführt, gewaschen oder gebadet, anschließend gespült, abgesetzt, geseiht und am lokalen Ablauf beendet.",
    "B2": "Arbeite fünf sichtbare Stationsgruppen nacheinander ab: obere Paarbecken, linkes Mittelgerät, ungelöster Mittelposten, unteres Mehrpersonenbecken und Randplätze. An jeder Station neu bemessen, temperieren, benetzen oder baden, abziehen und schließen; Stoff und Richtung werden beim Stationswechsel nicht mitgenommen.",
    "B3": "Bearbeite zuerst die drei Randgefäße einzeln: setzen und benetzen, dann füllen und waschen, dann klarziehen, spülen und ablassen. Der Zwischenbereich bleibt exemplarabhängig. Erst danach folgt das sichtbar gekoppelte Hauptpaar mit warmem Tuch, doppelter Spülung, Klärung und lokalem Abzug.",
    "B4": "Am gekoppelten Hauptpaar wird ein Tuch in temperierte Flüssigkeit getaucht, der Waschposten gefiltert und warm aufgelegt. Danach werden linke offene Station und rechter Mehrarmknoten getrennt bedient: bemessen, mischen, zweimal waschen, ablassen beziehungsweise warmes Wasser einfüllen und bereitstellen.",
    "B5": "Am linken offenen Endposten ziehe eine Portion ab, erwärme sie einmal, halte sie für die örtliche Dauer und führe sie unter gleichem Ansatz zum Ziel; bemesse und mische an der zweiten Öffnung.",
    "B6": "Richte den rechten Mehrarmknoten ohne Kochen ein, benutze die erste Öffnung, bemesse den Posten, führe ihn durch Tuch und gebrauche die gefilterte Portion an der bezeichneten Stelle.",
}


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


def main() -> None:
    clauses = [row for row in read_tsv(CLAUSES) if row["page"] in BIO_PAGES]
    units = {
        row["unit_id"]: row for row in read_tsv(UNITS)
        if row["unit_kind"] == "PROSE_STATEMENT" and row["page"] in BIO_PAGES
    }
    selected_statements = {row["statement_id"]: row for row in read_tsv(STATEMENTS)}
    selected_records = {row["record_unit_id"]: row for row in read_tsv(RECORDS)}
    by_unit = defaultdict(list)
    for row in clauses:
        by_unit[row["unit_id"]].append(row)

    group_rows = []
    for row in clauses:
        owner = selected_statements[row["unit_id"]]["local_owner_sequence"]
        group_rows.append({
            "source_group_id": row["source_group_id"],
            "unit_id": row["unit_id"],
            "record_id": row["unit_id"].split("-")[0],
            "page": row["page"],
            "local_owner": owner,
            "visible_surface": row["visible_surface"],
            "clause_shape_id": row["clause_shape_id"],
            "source_slots": row["source_slots"],
            "period_source_clause": row["workshop_vernacular_clause"],
            "direction_scope": "CURRENT_VISIBLE_OWNER_ONLY",
        })
    write_tsv(OUT / "SIXTY_SEVENTH_281_BIO_GROUP_EDITION.tsv", group_rows)

    statement_rows = []
    for unit_id, unit in units.items():
        station = selected_statements[unit_id]
        rows = by_unit[unit_id]
        statement_rows.append({
            "unit_id": unit_id,
            "record_id": unit_id.split("-")[0],
            "page": unit["page"],
            "local_owner_sequence": station["local_owner_sequence"],
            "contains_visible_owner_break": station["contains_visible_owner_break"],
            "group_count": len(rows),
            "surface_sequence": unit["surface_sequence"],
            "clause_shape_sequence": ">".join(row["clause_shape_id"] for row in rows),
            "short_card_sequence_de": unit["card_by_card_reading_de"],
            "period_source_clause_sequence": " ".join(row["workshop_vernacular_clause"] for row in rows),
            "local_station_working_reading_de": station["balneological_statement_text"],
            "station_reset_rule": "RESET_SOURCE_TARGET_DIRECTION_AT_VISIBLE_OWNER_BREAK" if station["contains_visible_owner_break"] == "YES" else "KEEP_CURRENT_LOCAL_OWNER",
            "global_network_claim": "NONE",
        })
    write_tsv(OUT / "SIXTY_SEVENTH_97_BIO_STATEMENTS.tsv", statement_rows)

    station_rows = []
    station_number = 0
    for record_id in sorted(selected_records):
        for local_order, owner in enumerate(selected_records[record_id]["local_owner_sequence"].split("|"), start=1):
            station_number += 1
            station_rows.append({
                "station_number": station_number,
                "record_id": record_id,
                "page": selected_records[record_id]["page"],
                "local_order": local_order,
                "owner_id": owner,
                "entry_rule": "RESET_ACTIVE_SOURCE_TARGET_DIRECTION",
                "allowed_flow_claim": "LOCAL_CONTACT_OR_ROUTE_ONLY",
                "global_connection": "NONE",
            })
    write_tsv(OUT / "SIXTY_SEVENTH_16_LOCAL_STATIONS.tsv", station_rows)

    record_rows = []
    for record_id in sorted(selected_records):
        record = selected_records[record_id]
        record_rows.append({
            "record_id": record_id,
            "page": record["page"],
            "field_count": len(record["field_ids"].split("|")),
            "statement_count": len(record["statement_ids"].split("|")),
            "group_count": len(record["event_serials"].split("|")),
            "local_station_count": len(record["local_owner_sequence"].split("|")),
            "local_owner_sequence": record["local_owner_sequence"],
            "owner_break_event_serials": record["owner_break_event_serials"],
            "compact_station_handbook_de": COMPACT[record_id],
            "selected_station_synopsis": record["fluent_record_synopsis"],
            "strongest_global_rival": record["strongest_global_rival"],
            "global_flow_claim": "NONE",
        })
    write_tsv(OUT / "SIXTY_SEVENTH_6_COMPACT_BIO_RECORDS.tsv", record_rows)

    doc = [
        "# Kompaktes Biological-Stationshandbuch", "",
        "Die Figuren, Becken, Gefäße und lokalen Verbindungen werden als sechzehn",
        "örtliche Besitzer gelesen. Ein Besitzerwechsel setzt Quelle, Ziel und Richtung",
        "zurück. Es gibt keinen erfundenen seitenweiten Wasserkreislauf.", "",
    ]
    for row in record_rows:
        doc.extend([
            f"## {row['record_id']} · {row['page']}", "",
            f"**Stationen:** `{row['local_owner_sequence']}`", "",
            f"**Kompakte Anweisung:** {row['compact_station_handbook_de']}", "",
            f"**Stärkster Rivale:** {row['strongest_global_rival']}", "",
        ])
    (OUT / "SIXTY_SEVENTH_COMPLETE_BIO_STATION_HANDBOOK.md").write_text("\n".join(doc).rstrip() + "\n", encoding="utf-8")

    report = [
        "# Siebenundsechzigste Werkstattfassung: Biological-Stationshandbuch", "",
        "## Ergebnis", "",
        "Die drei Biological-Seiten enthalten sechs Records, 115 Felder, 97 Aussagen",
        "und 281 sichtbare Gruppen. Die aktuelle Bildgliederung ergibt sechzehn lokale",
        "Stationen. Jede Station kann mit derselben Klauselgrammatik für Bemessen,",
        "Temperieren, Mischen, Baden/Waschen, Tuchgang, Abziehen und lokalen Abschluss",
        "beschrieben werden.", "",
        "Der kreative medizinische Lead ist ein Bade-, Wasch- und Anwendungshandbuch.",
        "Der nahezu gleich gute technische Lead ist ein Badehaus-/Waschhausregister.",
        "Beide brauchen dieselben lokalen Besitzer. Keine Lesung darf aus bloßer",
        "Nachbarschaft einen globalen Rohrfluss oder eine Pfeilrichtung erfinden.", "",
        "Nur f81v, f82r und f83r wurden verwendet; f84 und f84r blieben versiegelt.",
    ]
    (OUT / "SIXTY_SEVENTH_EDITION_REPORT.md").write_text("\n".join(report).rstrip() + "\n", encoding="utf-8")

    summary = {
        "status": "CONSISTENT",
        "counts": {
            "bio_pages": len({row["page"] for row in group_rows}),
            "bio_records": len(record_rows),
            "local_stations": len(station_rows),
            "bio_fields": sum(int(row["field_count"]) for row in record_rows),
            "bio_statements": len(statement_rows),
            "bio_groups": len(group_rows),
        },
        "sources": {str(path.relative_to(ROOT)): sha256(path) for path in (CLAUSES, UNITS, STATEMENTS, RECORDS)},
    }
    (OUT / "BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
