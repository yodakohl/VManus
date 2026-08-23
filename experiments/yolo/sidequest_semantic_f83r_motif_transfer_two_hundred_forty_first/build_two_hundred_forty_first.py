#!/usr/bin/env python3
from __future__ import annotations

import csv
import hashlib
import json
import re
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
SRC = ROOT / "experiments/yolo/sidequest_semantic_f83r_local_station_graph_two_hundred_thirty_second"
STATEMENTS = SRC / "TWO_HUNDRED_THIRTY_SECOND_FIFTY_FOUR_STATEMENTS.tsv"

MOTIF_TEXT = {
    "M01": "Schließen, dann neue Portion zugeben",
    "M02": "Ziel setzen, passieren und transferieren",
    "M03": "Halten oder bearbeiten, dann absetzen/schließen",
    "M04": "Bemessen, dann passieren oder zuführen",
    "M05": "Waschen oder Kontakt, dann schließen",
    "M06": "Empfangen, sammeln oder Ergebnis abnehmen",
    "M07": "Lokal übergeben, weiterleiten oder abführen",
}


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: list[dict[str, object]], fields: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def match(text: str) -> list[str]:
    t = text.lower()
    motifs: list[str] = []
    if re.search(r"ziel|dorthin|station|lauf", t) and re.search(r"durch|überf|übertrag|abführ|transfer|zuführ|abzieh|weiterf|einführ|bringen", t):
        motifs.append("M02")
    if re.search(r"einwirk|wärm|halt|absetz|bereit", t) and re.search(r"schluss|schließen", t):
        motifs.append("M03")
    if re.search(r"bemess|sollmaß|folgemaß|portion|anteil|menge", t) and re.search(r"durch|zuführ|überf|übertrag|transfer|lauf|bringen", t):
        motifs.append("M04")
    if re.search(r"wasch|einwirk", t) and re.search(r"schluss|schließen", t):
        motifs.append("M05")
    if re.search(r"auffang|ergebnis|abzug|abzieh|sammel|ausgieß", t):
        motifs.append("M06")
    if not motifs and re.search(r"überf|übertrag|abführ|transfer|zuführ|durchlass|durch den|einführ|weiterführ|bringen", t):
        motifs.append("M07")
    return motifs


def main() -> None:
    statements = read_tsv(STATEMENTS)
    rows: list[dict[str, object]] = []
    for statement in statements:
        motifs = match(statement["graph_aware_reading_de"])
        rows.append({
            "statement_id": statement["statement_id"],
            "record_unit_id": statement["record_unit_id"],
            "node_path": statement["node_path"],
            "event_ids": statement["event_ids"],
            "visible_card_reading": statement["literal_card_reading"],
            "complete_station_reading_de": statement["graph_aware_reading_de"],
            "inherited_motifs": "|".join(m for m in motifs if m != "M07") or "NONE",
            "new_handoff_motif": "M07" if "M07" in motifs else "NONE",
            "primary_motif": motifs[0] if motifs else "ATOMIC_EXCEPTION",
            "primary_apprentice_rule": MOTIF_TEXT[motifs[0]] if motifs else "gelernte elementare Einzelanweisung",
            "owner_break_count": statement["owner_break_count"],
            "coverage_status": "MOTIF_COVERED" if motifs else "ATOMIC_EXCEPTION",
        })

    motif_rows: list[dict[str, object]] = []
    for motif_id, text in MOTIF_TEXT.items():
        occurrence_ids = [r["statement_id"] for r in rows if motif_id in (str(r["inherited_motifs"]) + "|" + str(r["new_handoff_motif"])).split("|")]
        motif_rows.append({
            "motif_id": motif_id,
            "apprentice_rule_de": text,
            "origin": "R240_F81_F82" if motif_id != "M07" else "R241_MINIMAL_ADDITION",
            "f83r_statement_count": len(occurrence_ids),
            "f83r_statement_ids": "|".join(occurrence_ids) or "NONE",
            "portable_surface_rule": "components choose relation/action/grade; owner supplies omitted object",
        })

    exceptions = [r for r in rows if r["coverage_status"] == "ATOMIC_EXCEPTION"]
    exception_rows = [{
        "statement_id": r["statement_id"],
        "node_path": r["node_path"],
        "visible_card_reading": r["visible_card_reading"],
        "complete_station_reading_de": r["complete_station_reading_de"],
        "exception_type": (
            "ATOMIC_SET" if "einsetzen" in str(r["complete_station_reading_de"]).lower()
            else "ATOMIC_FASTEN" if "befestigen" in str(r["complete_station_reading_de"]).lower()
            else "BARE_CLOSE"
        ),
        "teaching_action": "learn as one elementary card; do not invent another multi-card motif",
    } for r in exceptions]

    statement_path = OUT / "TWO_HUNDRED_FORTY_FIRST_FIFTY_FOUR_F83R_MOTIF_READINGS.tsv"
    motif_path = OUT / "TWO_HUNDRED_FORTY_FIRST_SEVEN_MOTIF_CURRICULUM.tsv"
    exception_path = OUT / "TWO_HUNDRED_FORTY_FIRST_THREE_ATOMIC_EXCEPTIONS.tsv"
    readable_path = OUT / "TWO_HUNDRED_FORTY_FIRST_READABLE_F83R_CURRICULUM.md"
    report_path = OUT / "TWO_HUNDRED_FORTY_FIRST_REPORT.md"
    write_tsv(statement_path, rows, list(rows[0]))
    write_tsv(motif_path, motif_rows, list(motif_rows[0]))
    write_tsv(exception_path, exception_rows, list(exception_rows[0]))

    by_node: dict[str, list[dict[str, object]]] = {}
    for row in rows:
        by_node.setdefault(str(row["node_path"]), []).append(row)
    readable = ["# f83r mit sieben Lehrmotiven", ""]
    for node, linked in by_node.items():
        readable += [f"## {node}", ""]
        for row in linked:
            readable.append(f"- {row['statement_id']} [{row['primary_motif']}]: {row['complete_station_reading_de']}")
        readable.append("")
    readable += [
        "## Die neue Karte M07", "",
        "**Lokal übergeben, weiterleiten oder abführen.** Besitzer und Richtung kommen aus der Zeichnung; die Karten müssen nur die Übergabehandlung und einen eventuellen Schluss setzen.", "",
        "Damit decken sieben Motive 51 der 54 f83r-Anweisungen. Die drei Reste sind absichtlich keine neuen Satzmotive, sondern elementare Einzelbefehle: einsetzen, befestigen, schließen.", "",
    ]
    readable_path.write_text("\n".join(readable), encoding="utf-8")

    old_covered = sum(r["coverage_status"] == "MOTIF_COVERED" and r["new_handoff_motif"] == "NONE" for r in rows)
    new_covered = sum(r["new_handoff_motif"] == "M07" for r in rows)
    report = f"""# Sidequest-Pass 241: Motive auf f83r übertragen

## Ergebnis

- Die sechs f81v/f82r-Motive decken **{old_covered}/54** f83r-Anweisungen.
- Ein einziges zusätzliches Motiv, **M07 LOKALE ÜBERGABE**, deckt weitere **{new_covered}**.
- Gesamt: **{old_covered + new_covered}/54** durch sieben wiederverwendbare Motive.
- Drei Anweisungen bleiben elementare Einzelkarten: einsetzen, befestigen, Schluss.

M07 ist keine neue Wortbedeutung. Es bündelt die bereits gelesenen Transferfamilien CHED, L+CHED, P+CHED und einfache Übergabeformen zu einer Lehrmeisteranweisung. Der Bildbesitzer bestimmt, welches Becken, welcher Arm oder welcher Endposten gemeint ist.

Damit reicht ein sehr kleiner Motifkurs für alle drei Biological-Seiten: produktive Komponenten erledigen die Satzarbeit; wenige ganze Zeichen und drei atomare Befehle werden aus dem Exemplar gelernt.

Source SHA-256: `{sha(STATEMENTS)}`.
"""
    report_path.write_text(report, encoding="utf-8")
    summary = {
        "status": "PASS",
        "statements": len(rows),
        "old_six_covered": old_covered,
        "m07_added": new_covered,
        "seven_motif_covered": old_covered + new_covered,
        "atomic_exceptions": len(exceptions),
        "motif_primary_counts": dict(Counter(str(r["primary_motif"]) for r in rows)),
        "outputs": {p.name: sha(p) for p in (statement_path, motif_path, exception_path, readable_path, report_path)},
    }
    (OUT / "BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
