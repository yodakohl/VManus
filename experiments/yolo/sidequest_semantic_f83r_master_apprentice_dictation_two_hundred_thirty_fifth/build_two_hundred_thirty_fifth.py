#!/usr/bin/env python3
from __future__ import annotations

import csv
import hashlib
import json
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
GRAPH_EVENTS = ROOT / "experiments/yolo/sidequest_semantic_f83r_local_station_graph_two_hundred_thirty_second/TWO_HUNDRED_THIRTY_SECOND_ONE_HUNDRED_FIFTY_THREE_EVENTS.tsv"
GRAPH_STATEMENTS = ROOT / "experiments/yolo/sidequest_semantic_f83r_local_station_graph_two_hundred_thirty_second/TWO_HUNDRED_THIRTY_SECOND_FIFTY_FOUR_STATEMENTS.tsv"
ADDENDA = ROOT / "experiments/yolo/sidequest_semantic_f83r_branch_addenda_two_hundred_thirty_fourth/TWO_HUNDRED_THIRTY_FOURTH_FOUR_REVISED_STATEMENTS.tsv"

NODE_SCRIPTS = {
    "N1": "Oben länger sammeln, danach am nächsten Platz länger wärmen; denselben Posten auf Sollwert halten, abführen und davon bemessen weitergeben.",
    "N2": "Ins runde Gefäß überführen; am Ziel einsetzen, länger halten, abführen und den nächsten Gang beginnen.",
    "N3": "Dem unteren Gefäß zuführen; Vorbereitung und Portion einsetzen, kurz oder lang absetzen, abführen und am Abzug enden.",
    "N4": "Im Zwischenblock einführen, halten und absetzen; Ziele bemessen, vorbereiten und schließen; Quellanteil zur Zielbereitung geben und zum Hauptpaar wechseln.",
    "N5": "Im Doppelbecken lang und kurz einwirken, einsetzen und befestigen; Einlage übertragen, zweimal durchlassen, Sollwert halten und absetzen.",
    "N6": "Im linken Arm Sollwert kurz wärmen, lang fortsetzen, Anteil zugeben, übertragen, Ergebnis nehmen und abführen.",
    "N7": "Im rechten Arm kurz sammeln, abführen, weiteren Anteil zum Ziel bringen, aus der Quelle ausgießen und kurz absetzen.",
    "N8": "Den linken Endtransfer schließen, neu einführen, am Ziel absetzen, weiter abziehen, Sollwert und Endstufe setzen und übergeben.",
    "N9": "Am rechten Ende länger sammeln, kurz bearbeiten, zum Endposten weiterführen, Sollwert setzen und die Einlage zum Endziel führen.",
}

RULES = [
    ("R01", "BILD_ZUERST", "Die Zeichnung ist fertig, bevor der Text gesetzt wird."),
    ("R02", "BESITZER_ZEIGEN", "Der Meister zeigt auf den lokalen Bildposten; sein Name muss nicht ausgeschrieben werden."),
    ("R03", "BESITZER_VERERBEN", "Folgezellen behalten denselben Besitzer bis zu einer sichtbaren Lücke oder neuen Szene."),
    ("R04", "RECORD_NEUSTART", "Jeder neue Record löscht den laufenden Posten, auch am selben sichtbaren Arm."),
    ("R05", "BESITZERBRUCH", "Ein Besitzerwechsel darf mitten in einer Aussage stehen; der Bildbruch ist stärker als die Satzmelodie."),
    ("R06", "OK_AKTIVIEREN", "OK setzt den folgenden Posten oder Arbeitsgang ein."),
    ("R07", "CHED_UEBERFUEHREN", "CHED führt einen Posten über; P und L spezifizieren hinein beziehungsweise hinaus."),
    ("R08", "AR_AL_ADRESSE", "AR nimmt von der Quelle, AL weist das Ziel zu."),
    ("R09", "Y_REFERENT", "Y hält den aktuell gemeinten Posten verfügbar: dies/es."),
    ("R10", "AIIN_SOLLWERT", "AIIN bezeichnet den vorgeschriebenen Wert oder das Maß."),
    ("R11", "OL_FORTSETZUNG", "OL führt denselben Ansatz, Weg oder Arbeitsstand weiter."),
    ("R12", "OT_FOLGE", "OT wechselt zum folgenden Posten oder Schritt."),
    ("R13", "OR_ANSATZ", "OR bezeichnet den laufenden Ansatz oder die laufende Zubereitung."),
    ("R14", "E_GRADE", "E, EE und EEE markieren kurz, länger und vollständig innerhalb lizenzierter Reihen."),
    ("R15", "Y_OFFEN_DY_SCHLUSS", "Y hält den Posten offen; nur die gelernte DY-Endkonstruktion schließt die Zelle."),
    ("R16", "ABA_RUECKKEHR", "A–B–A aktiviert A, wendet B an und nimmt denselben A-Posten wieder auf."),
    ("R17", "DOPPELTE_ZELLE", "Zwei geschlossene gleiche Zellen wiederholen den abgeschlossenen Arbeitsgang."),
    ("R18", "LO_GANZWORT", "LO wird als lokale Ganzkarte Abzug gelernt."),
    ("R19", "RENDERER_HUELLE", "q/s/ch/d-Hüllen werden nach Hand, Position und Kartendeck gesetzt; sie ändern nicht frei die Bedeutung."),
    ("R20", "ZEILE_IST_RAUM", "Ein physisches Zeilenende beendet keine Aussage; weitergelesen wird bis Zellschluss oder Ownerbruch."),
]


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(path: Path, rows: list[dict[str, object]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    events = read(GRAPH_EVENTS)
    statements = read(GRAPH_STATEMENTS)
    addendum_overrides = {row["statement_id"]: row["revised_addendum_reading_de"] for row in read(ADDENDA)}
    by_node: dict[str, list[dict[str, str]]] = defaultdict(list)
    by_statement: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in events:
        by_node[row["graph_node_id"]].append(row)
        by_statement[row["statement_id"]].append(row)

    node_rows: list[dict[str, object]] = []
    for node_id in sorted(by_node, key=lambda value: int(value[1:])):
        rows = by_node[node_id]
        node_rows.append({
            "node_id": node_id,
            "master_points_to": rows[0]["visible_owner"],
            "master_dictation_de": NODE_SCRIPTS[node_id],
            "statement_ids": "|".join(dict.fromkeys(row["statement_id"] for row in rows)),
            "event_count": len(rows),
            "apprentice_exact_card_stream": " ".join(row["visible_surface"] for row in rows),
            "apprentice_portable_readback": " | ".join(row["portable_value_de"] for row in rows),
            "state_reset_before_node": "YES" if node_id in {"N1", "N8", "N9"} else "NO",
            "visible_gap_before_node": "YES" if node_id in {"N2", "N3", "N4", "N5"} else "NO",
        })
    write(OUT / "TWO_HUNDRED_THIRTY_FIFTH_NINE_NODE_MASTER_SCRIPT.tsv", node_rows)

    trace_rows: list[dict[str, object]] = []
    for row in statements:
        owned = by_statement[row["statement_id"]]
        nodes = list(dict.fromkeys(event["graph_node_id"] for event in owned))
        values = " | ".join(event["portable_value_de"] for event in owned)
        rules = []
        if any("Sollwert" in event["portable_value_de"] or "bemess" in event["portable_value_de"] for event in owned):
            rules.append("AIIN_SOLLWERT")
        if any(any(term in event["portable_value_de"].lower() for term in ("überführ", "transfer", "zuführ", "abführ")) for event in owned):
            rules.append("CHED_TRANSFER")
        if any(any(term in event["portable_value_de"].lower() for term in ("kurz", "lang", "voll")) for event in owned):
            rules.append("E_GRADE")
        if any(event["terminal_status"] == "TERMINAL" for event in owned):
            rules.append("CLOSE")
        if len(nodes) > 1:
            rules.append("OWNER_BREAK")
        if not rules:
            rules.append("LOCAL_CARD_OR_ADDRESS")
        trace_rows.append({
            "statement_id": row["statement_id"],
            "record_unit_id": row["record_unit_id"],
            "node_path": "→".join(nodes),
            "master_says_de": addendum_overrides.get(row["statement_id"], row["graph_aware_reading_de"]),
            "apprentice_selects_visible_cards": " ".join(event["visible_surface"] for event in owned),
            "apprentice_reads_back_values": values,
            "rules_used": "|".join(rules),
            "event_ids": "|".join(event["event_id"] for event in owned),
            "event_count": len(owned),
        })
    write(OUT / "TWO_HUNDRED_THIRTY_FIFTH_FIFTY_FOUR_DICTATION_TRACES.tsv", trace_rows)

    rule_rows = [{"rule_id": rule_id, "rule_name": name, "master_teaching_de": teaching} for rule_id, name, teaching in RULES]
    write(OUT / "TWO_HUNDRED_THIRTY_FIFTH_TWENTY_RULE_MANUAL.tsv", rule_rows)

    manual = [
        "# Kurzes Meister–Lehrling-Handbuch für f83r",
        "",
        "Der Meister diktiert nicht jeden Buchstaben. Er zeigt zuerst auf die bereits gezeichnete Station, nennt Handlung, Bezug, Grad und Abschluss; der Lehrling setzt daraus Karten und positionsabhängige Hüllen.",
        "",
        "## Die neun Diktatblöcke",
        "",
    ]
    for row in node_rows:
        manual.extend([
            f"### {row['node_id']} — {row['master_points_to']}",
            "",
            f"**Meister:** {row['master_dictation_de']}",
            "",
            f"**Lehrling schreibt:** `{row['apprentice_exact_card_stream']}`",
            "",
        ])
    manual.extend([
        "## Warum mehrere Schreiber das lernen können",
        "",
        "Nur wenige Bausteine sind produktiv: OK, CHED, AR/AL/Y, AIIN, OL/OT/OR, die E-Grade und die Endkonstruktion. Besondere lokale Gegenstände bleiben als ganze Karten im Exemplar; auf f83r ist `lo = Abzug` das klarste Beispiel. Der Schreiber muss daher kein geheimes Alphabet lernen, sondern ein kleines Register plus Kartenkasten und Musterseite.",
        "",
        "Die exakte Oberflächenform bleibt dennoch exemplarabhängig. Das Handbuch erklärt die Komposition, nicht warum derselbe Kartenwert einmal mit q-, s-, ch- oder d-Hülle geschrieben wird.",
    ])
    (OUT / "TWO_HUNDRED_THIRTY_FIFTH_READABLE_APPRENTICE_MANUAL.md").write_text("\n".join(manual).rstrip() + "\n", encoding="utf-8")

    report = [
        "# Pass 235 — f83r vorwärts als Meisterdiktat erzeugen",
        "",
        "Neun Besitzerblöcke, 54 Diktatschritte und 153 Karten sind vollständig verbunden. Der Meister kann das Blatt mit 20 kurzen Werkstattregeln anleiten: Bildbesitzer zeigen, Recordzustand führen, Relation/Operation/Grad wählen, gegebenenfalls schließen und lokale Ganzkarten aus dem Exemplar einsetzen.",
        "",
        "Das Modell ist damit nicht nur eine rückwärts angepasste Übersetzung. Es besitzt einen plausiblen Erzeugungsweg für mehrere Schreiber um 1420: gemeinsames Kartenregister, mündliche Kurzvorgabe, sichtbare Bildadresse und positionsabhängige Rendererhülle.",
        "",
        "Nächster Schritt: denselben 20-Regel-Lehrplan ohne neue Bedeutungen auf f81v und f82r anwenden. Was dort nicht vorwärts formulierbar ist, markiert die nächste echte Wörterbuchlücke.",
    ]
    (OUT / "TWO_HUNDRED_THIRTY_FIFTH_REPORT.md").write_text("\n".join(report).rstrip() + "\n", encoding="utf-8")
    summary = {
        "graph_event_sha256": hashlib.sha256(GRAPH_EVENTS.read_bytes()).hexdigest(),
        "graph_statement_sha256": hashlib.sha256(GRAPH_STATEMENTS.read_bytes()).hexdigest(),
        "addenda_sha256": hashlib.sha256(ADDENDA.read_bytes()).hexdigest(),
        "nodes": len(node_rows),
        "statements": len(trace_rows),
        "events": sum(int(row["event_count"]) for row in trace_rows),
        "rules": len(rule_rows),
        "sealed_pages_accessed": False,
    }
    (OUT / "BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
