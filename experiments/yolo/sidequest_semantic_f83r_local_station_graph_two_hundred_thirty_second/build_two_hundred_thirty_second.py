#!/usr/bin/env python3
from __future__ import annotations

import csv
import hashlib
import json
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
EVENTS = ROOT / "experiments/yolo/sidequest_semantic_result_close_integration_two_hundred_twenty_first/TWO_HUNDRED_TWENTY_FIRST_381_EVENT_PROSE.tsv"
STATEMENTS = ROOT / "experiments/yolo/sidequest_semantic_result_close_integration_two_hundred_twenty_first/TWO_HUNDRED_TWENTY_FIRST_116_STATEMENT_PROSE.tsv"

NODES = {
    "obere offene Fächer-Randstation": ("N1", "SAMMEL- UND TEMPERIERSTELLE", "F071–F074", "B3", "local upper-margin station"),
    "mittlere runde Gefäß-Randstation": ("N2", "ÜBERGABE- UND HALTEGEFÄSS", "F075–F079", "B3", "local round vessel"),
    "untere korbartige Gefäß-Randstation": ("N3", "PORTIONS- UND ABSETZGEFÄSS", "F080–F086", "B3", "local basket-like vessel"),
    "ungelöster Zwischenposten zwischen Randstapel und Hauptpaar": ("N4", "DOSIER- UND VERTEILERBLOCK", "F087–F098", "B3", "owner unresolved among middle scenes"),
    "Hauptpaar am sichtbaren ungerichteten Bogen": ("N5", "EINWIRK- UND DURCHLASSPAAR", "F099–F119", "B3|B4", "two vessels visibly joined by broad arch; no direction"),
    "linke offene Fransen-/Unterlaufstation": ("N6", "LINKER TEMPERIER- UND ABZUGSARM", "F120–F125", "B4", "visible left descending open channel branch"),
    "rechte S-Lauf-/Mehrarmknotenstation": ("N7", "RECHTER SAMMEL- UND VERTEILERARM", "F126–F128", "B4", "visible S-conduit and multiended hub; no direction"),
    "linker offener Fransen-Endposten": ("N8", "LINKER ENDTRANSFERPOSTEN", "F129–F133", "B5", "record-local readdressing of left branch; no inherited text state"),
    "rechter S-Lauf-/Mehrarm-Endposten": ("N9", "RECHTER SAMMEL- UND ENDVERTEILERPOSTEN", "F134–F135", "B6", "record-local readdressing of right branch; no inherited text state"),
}

EDGES = [
    ("G01", "N1", "N2", "TEXT_ORDER_WITH_VISIBLE_GAP", "NO", "B3-S005", "Page order changes station; no drawn connector."),
    ("G02", "N2", "N3", "TEXT_ORDER_WITH_VISIBLE_GAP", "NO", "B3-S010", "Page order changes station; no drawn connector."),
    ("G03", "N3", "N4", "OWNER_BREAK_WITHIN_STATEMENT", "NO", "B3-S016:E263→E264", "The clause continues, but the visible owner breaks before E264."),
    ("G04", "N4", "N5", "OWNER_BREAK_WITHIN_STATEMENT", "NO", "B3-S026:E290→E291", "Long collection begins at the lower pair after an owner reset; upper/middle scenes are unconnected to it."),
    ("G05", "N5", "N6", "VISIBLE_UNDIRECTED_CONTACT", "YES", "image:C031–C032", "Left lower vessel continues into a blue-lined channel with open end; no arrow."),
    ("G06", "N5", "N7", "VISIBLE_UNDIRECTED_CONTACT", "YES", "image:C033–C035", "Right lower vessel continues into S-conduit and multiended hub; no arrow."),
    ("G07", "N6", "N7", "NO_DIRECT_EDGE", "NO", "image:C031–C035", "Branches meet only through the paired lower assembly, not directly."),
    ("G08", "N5", "N5", "RECORD_RESET_SAME_VISIBLE_OWNER", "NO", "B3-S034→B4-S001", "B4 restarts the text register although the visible pair remains the owner; this is no new physical edge."),
    ("G09", "N6", "N8", "RECORD_READDRESS_SAME_VISIBLE_BRANCH", "NO", "B4→B5", "B5 returns to the left endpost but inherits no B4 working state; this is an alias, not a new physical edge."),
    ("G10", "N7", "N9", "RECORD_READDRESS_SAME_VISIBLE_BRANCH", "NO", "B5→B6", "B6 addresses the right endpost in a fresh record; this is an alias, not a new physical edge."),
]

OVERRIDES = {
    "B3-S016": "Am N3-Abzug abziehen; nach sichtbarem Besitzerbruch bei N4 einführen; Schluss.",
    "B3-S026": "Bei N4 von der Quelle übertragen, Sollabsetzung und Zielbereitung setzen; nach Besitzerbruch am N5-Paar länger sammeln; Schluss.",
    "B4-S015": "Am linken N6-Arm Anteil, Ergebnis und Zielpassage setzen; nach Besitzerbruch am rechten N7-Knoten kurz sammeln und abführen; Schluss.",
}


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(path: Path, rows: list[dict[str, object]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    event_source = [row for row in read(EVENTS) if row["page"] == "f83r"]
    statement_source = {row["statement_id"]: row for row in read(STATEMENTS) if row["record_unit_id"] in {"B3", "B4", "B5", "B6"}}
    by_owner: dict[str, list[dict[str, str]]] = defaultdict(list)
    by_statement: dict[str, list[dict[str, str]]] = defaultdict(list)
    event_rows: list[dict[str, object]] = []
    for row in event_source:
        by_owner[row["visible_owner"]].append(row)
        by_statement[row["statement_id"]].append(row)
        node_id = NODES[row["visible_owner"]][0]
        event_rows.append({
            "event_id": row["event_id"],
            "statement_id": row["statement_id"],
            "field_id": row["field_id"],
            "visible_surface": row["visible_surface"],
            "portable_value_de": row["portable_value_de"],
            "terminal_status": row["terminal_status"],
            "visible_owner": row["visible_owner"],
            "graph_node_id": node_id,
            "node_function_de": NODES[row["visible_owner"]][1],
        })

    node_rows: list[dict[str, object]] = []
    for owner, (node_id, function, field_range, records, visual_note) in NODES.items():
        rows = by_owner[owner]
        node_rows.append({
            "node_id": node_id,
            "visible_owner": owner,
            "field_range": field_range,
            "record_units": records,
            "event_count": len(rows),
            "statement_count": len({row["statement_id"] for row in rows}),
            "selected_function_de": function,
            "portable_operation_chain_de": " | ".join(dict.fromkeys(row["portable_value_de"] for row in rows)),
            "visible_geometry_note": visual_note,
            "direction_status": "NO_DIRECTION_INFERRED",
        })
    node_rows.sort(key=lambda row: int(str(row["node_id"])[1:]))

    edge_rows = [
        {"edge_id": edge_id, "from_node": source, "to_node": target, "edge_class": edge_class, "visible_contact": visible, "source_transition": transition, "reading_limit": limit}
        for edge_id, source, target, edge_class, visible, transition, limit in EDGES
    ]

    statement_rows: list[dict[str, object]] = []
    for statement_id, source in statement_source.items():
        rows = by_statement[statement_id]
        nodes = [NODES[row["visible_owner"]][0] for row in rows]
        compressed = list(dict.fromkeys(nodes))
        breaks = sum(a != b for a, b in zip(nodes, nodes[1:]))
        statement_rows.append({
            "statement_id": statement_id,
            "record_unit_id": source["record_unit_id"],
            "event_count": len(rows),
            "event_ids": "|".join(row["event_id"] for row in rows),
            "node_path": "→".join(compressed),
            "owner_break_count": breaks,
            "literal_card_reading": source["r221_literal_card_reading"],
            "graph_aware_reading_de": OVERRIDES.get(statement_id, source["r221_owner_expansion_de"]),
            "edge_claim": "OWNER_BREAK_NOT_PHYSICAL_EDGE" if breaks else "LOCAL_NODE_ONLY",
        })
    statement_rows.sort(key=lambda row: int(str(row["event_ids"]).split("|")[0][1:]))

    write(OUT / "TWO_HUNDRED_THIRTY_SECOND_NINE_GRAPH_NODES.tsv", node_rows)
    write(OUT / "TWO_HUNDRED_THIRTY_SECOND_TEN_GRAPH_EDGES.tsv", edge_rows)
    write(OUT / "TWO_HUNDRED_THIRTY_SECOND_ONE_HUNDRED_FIFTY_THREE_EVENTS.tsv", event_rows)
    write(OUT / "TWO_HUNDRED_THIRTY_SECOND_FIFTY_FOUR_STATEMENTS.tsv", statement_rows)

    readable = [
        "# f83r als lokaler Arbeitsgraph",
        "",
        "## Textfolge oben und in der Mitte",
        "",
        "`N1 Sammeln/Temperieren` → **sichtbare Lücke** → `N2 Übergeben/Halten` → **sichtbare Lücke** → `N3 Portionieren/Absetzen` → **Besitzerbruch mitten in B3-S016** → `N4 Dosieren/Verteilen` → **Besitzerbruch mitten in B3-S026** → `N5 Einwirken/Durchlassen`.",
        "",
        "Diese Pfeile bedeuten ausschließlich Leserichtung. Zwischen N1–N5 ist keine durchgehende Leitung gezeichnet.",
        "",
        "## Sichtbar verbundene untere Gruppe",
        "",
        "Im Knoten N5 sind zwei Gefäße durch einen breiten Bogen sichtbar verbunden. Vom linken Gefäß führt eine blaue, offene Kanalform zu `N6`; vom rechten eine S-förmige Leitung zum Mehrarmknoten `N7`. Keine Kante hat einen Pfeil.",
        "",
        "`N6` liest sich als linker Temperier-/Abzugsarm; `N7` als rechter Sammel-/Verteilerarm. B5 adressiert den linken Arm neu als `N8`, B6 den rechten neu als `N9`; beide Recordwechsel löschen den laufenden Textzustand.",
        "",
        "## Konkreter Ablauf als Arbeitstheorie",
        "",
        "Oben sammeln und temperieren, im runden Gefäß halten, unten portionieren und absetzen. Danach folgt eine nicht sicher lokalisierte Dosier-/Verteilerreihe. Am sichtbar verbundenen Hauptpaar wirken lassen und zweimal durchlassen. Der linke Arm temperiert, zieht ab und führt zum Ergebnis; der rechte sammelt, verteilt und setzt kurz ab. Die beiden Nachträge buchen linken beziehungsweise rechten Endposten neu.",
        "",
        "Das ist kein geschlossener Kreislauf: Drei obere Übergänge sind bloße Textreihenfolge, zwei Wechsel schneiden sogar eine laufende Aussage, und nur die untere Paar-/Kanalgruppe besitzt echte Bildkontakte.",
    ]
    (OUT / "TWO_HUNDRED_THIRTY_SECOND_READABLE_LOCAL_GRAPH.md").write_text("\n".join(readable).rstrip() + "\n", encoding="utf-8")

    report = [
        "# Pass 232 — vollständiger lokaler f83r-Stationsgraph",
        "",
        "Alle 153 f83r-Ereignisse und 54 Aussagen sind neun Text-/Besitzerknoten zugeordnet. Der Graph trennt erstmals drei Dinge konsequent: bloße Seitenreihenfolge, Besitzerbruch innerhalb einer Aussage und echte sichtbare Berührung.",
        "",
        "Nur die untere Gruppe besitzt reale Bildkanten: der breite Bogen innerhalb des Hauptpaars, der linke blaue Kanal und der rechte S-Lauf mit Mehrarmknoten. N1–N4 stehen zwar in Textfolge, sind aber nicht gezeichnet verbunden. B5 und B6 readdressieren die beiden unteren Arme mit neuem Recordzustand.",
        "",
        "Die kreative Gesamtlesung wird dadurch besser statt schwächer: nicht eine fantastische Universalmaschine, sondern ein Stationsblatt mit mehreren unabhängigen oberen Arbeitsplätzen und einer wirklich gekoppelten unteren Teilapparatur.",
        "",
        "Nächster Schritt: N5–N7 als einzige sichtbar gekoppelte Teilapparatur vollständig lesen und aus den beiden Textarmen eine konkrete Zwei-Ausgang-Funktion ableiten.",
    ]
    (OUT / "TWO_HUNDRED_THIRTY_SECOND_REPORT.md").write_text("\n".join(report).rstrip() + "\n", encoding="utf-8")
    summary = {
        "event_source_sha256": hashlib.sha256(EVENTS.read_bytes()).hexdigest(),
        "statement_source_sha256": hashlib.sha256(STATEMENTS.read_bytes()).hexdigest(),
        "nodes": len(node_rows),
        "edges": len(edge_rows),
        "events": len(event_rows),
        "statements": len(statement_rows),
        "owner_break_statements": sum(int(row["owner_break_count"]) > 0 for row in statement_rows),
        "visible_contact_edges": sum(row["visible_contact"] == "YES" for row in edge_rows),
        "sealed_pages_accessed": False,
    }
    (OUT / "BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
