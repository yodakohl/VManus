#!/usr/bin/env python3
from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
READINGS = ROOT / "experiments/yolo/sidequest_semantic_renderer_consolidated_card_deck_nine_hundred_forty_second/PASS942_2511_RENDERER_CONSOLIDATED_READINGS.tsv"
BINDINGS = ROOT / "experiments/yolo/sidequest_semantic_fluent_prose_nine_hundred_seventeenth/PASS917_2010_EVENT_BINDINGS.tsv"
CLAUSES = ROOT / "experiments/yolo/sidequest_semantic_macro_clause_translation_nine_hundred_thirty_seventh/PASS937_354_MACRO_CLAUSE_TRANSLATIONS.tsv"
PAGES = ROOT / "experiments/yolo/sidequest_semantic_scribe_style_reading_nine_hundred_fortieth/PASS940_14_SCRIBE_STYLE_PAGE_READINGS.tsv"


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: list[dict[str, object]], fields: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def spoken(text: str) -> str:
    if text == text.upper():
        for plain, german in {
            "LAENGER": "LÄNGER",
            "NAECHSTEN": "NÄCHSTEN",
            "FUEHREN": "FÜHREN",
            "AUSFUEHREN": "AUSFÜHREN",
            "WEITERFUEHREN": "WEITERFÜHREN",
            "WAEHLEN": "WÄHLEN",
            "SOLLMASS": "SOLLMAẞ",
        }.items():
            text = text.replace(plain, german)
        return text.lower()
    return text.replace("; ", ", ")


def compress_runs(items: list[tuple[str, str]]) -> list[str]:
    result: list[str] = []
    pos = 0
    while pos < len(items):
        route, phrase = items[pos]
        run = 1
        while pos + run < len(items) and items[pos + run] == items[pos]:
            run += 1
        marker = "Merkformel" if route == "LEARNED_CARD_FAMILY" else "gebildete Karte"
        unit = f"{marker}: {spoken(phrase)}"
        if run > 1:
            unit += f" ({run}×)"
        result.append(unit)
        pos += run
    return result


def main() -> None:
    readings = {row["event_id"]: row for row in read_tsv(READINGS)}
    bindings = read_tsv(BINDINGS)
    clauses = read_tsv(CLAUSES)
    pages = read_tsv(PAGES)
    event_clause = {row["event_id"]: row["clause_id"] for row in bindings}
    by_clause: dict[str, list[dict[str, str]]] = defaultdict(list)
    for event_id, clause_id in event_clause.items():
        by_clause[clause_id].append(readings[event_id])
    for rows in by_clause.values():
        rows.sort(key=lambda row: int(row["event_id"].split("E")[-1]))

    clause_rows: list[dict[str, object]] = []
    for clause in clauses:
        rows = by_clause[clause["clause_id"]]
        items = [(row["reading_route"], row["spoken_value_de"]) for row in rows]
        units = compress_runs(items)
        tail = "Arbeitszug beendet." if clause["end_reason"] == "LICENSED_DY_CLOSE" else "Zur Fortsetzung offen."
        clause_rows.append({
            "clause_id": clause["clause_id"],
            "physical_page": clause["physical_page"],
            "register": clause["register"],
            "start_event": clause["start_event"],
            "end_event": clause["end_event"],
            "events": len(rows),
            "learned_card_events": sum(row["reading_route"] == "LEARNED_CARD_FAMILY" for row in rows),
            "composed_events": sum(row["reading_route"] == "PRODUCTIVE_COMPOSITION" for row in rows),
            "spoken_units": len(units),
            "end_reason": clause["end_reason"],
            "hybrid_card_translation_de": "; dann ".join(units) + ". " + tail,
            "event_ids": "|".join(row["event_id"] for row in rows),
        })
    write_tsv(OUT / "PASS944_354_HYBRID_CARD_CLAUSES.tsv", clause_rows, list(clause_rows[0]))

    event_rows: list[dict[str, object]] = []
    for row in bindings:
        reading = readings[row["event_id"]]
        event_rows.append({
            "event_id": row["event_id"],
            "clause_id": row["clause_id"],
            "physical_page": reading["physical_page"],
            "locus": reading["locus"],
            "surface": reading["surface"],
            "component_recipe": reading["component_recipe"],
            "reading_route": reading["reading_route"],
            "spoken_value_de": spoken(reading["spoken_value_de"]),
        })
    write_tsv(OUT / "PASS944_2010_PROSE_CARD_INTERLINEAR.tsv", event_rows, list(event_rows[0]))

    by_page: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in clause_rows:
        by_page[str(row["physical_page"])].append(row)
    edition = [
        "# Pass 944 — vollständige Rückübersetzung mit Ganzkarten-Vorrang",
        "",
        "Die fettgedruckte Seitenaussage ist die flüssige Lesung. Darunter steht die vollständige Kartenrücklesung: häufige Formeln werden als Merkformel, alle übrigen Karten aus ihren Kürzeln gesprochen.",
        "",
    ]
    for page in pages:
        p = page["physical_page"]
        edition.extend([f"## {p}", "", f"**{page['scribe_style_page_reading_de']}**", ""])
        if page["diagram_reading_de"] != "KEINE_SEPARATE_BILDBESCHRIFTUNG":
            edition.extend([f"Bildregister: {page['diagram_reading_de']}", ""])
        for clause in by_page.get(p, []):
            edition.extend([f"### {clause['clause_id']}", "", str(clause["hybrid_card_translation_de"]), ""])
    (OUT / "PASS944_COMPLETE_HYBRID_RETRANSLATION.md").write_text("\n".join(edition), encoding="utf-8")

    routes = Counter(row["reading_route"] for row in event_rows)
    report = f"""# Pass 944 — Ganzkarten machen die Übersetzung kürzer

## Ergebnis

Alle 2.010 Prosakarten und 354 Klauseln sind erneut gelesen. **{routes['LEARNED_CARD_FAMILY']}**
Ereignisse werden nun als gelernte Formelkarten gesprochen; **{routes['PRODUCTIVE_COMPOSITION']}**
werden aus den 56 Kürzeln gebildet. Identische unmittelbar wiederholte Karten
erscheinen als `2×`, statt denselben deutschen Ausdruck künstlich zu verdoppeln.

## Gewinn

`qokedy` ist jetzt eine Werkstattformel „kurz ansetzen; Ende“, nicht drei
isolierte Wörter. `chedy` ist „diesen Posten umsetzen“, `daiin` „nach Sollmaß“.
Seltene Karten bleiben vollständig lesbar, weil ihre Komponenten sichtbar
bleiben. Das ist genau die gewünschte Mischung aus Fachkürzeln und gelerntem
Ganzkartenbestand.
"""
    (OUT / "PASS944_REPORT.md").write_text(report, encoding="utf-8")
    summary = {"clauses": len(clause_rows), "events": len(event_rows), "routes": dict(routes), "pages": len(pages), "outputs": {}}
    for path in sorted(OUT.glob("PASS944_*")):
        summary["outputs"][path.name] = hashlib.sha256(path.read_bytes()).hexdigest()
    (OUT / "PASS944_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
