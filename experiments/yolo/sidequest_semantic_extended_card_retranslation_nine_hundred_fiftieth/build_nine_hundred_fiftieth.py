#!/usr/bin/env python3
from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
EVENTS = ROOT / "experiments/yolo/sidequest_semantic_extended_formula_deck_nine_hundred_forty_ninth/PASS949_2511_EXTENDED_THREE_LAYER_EDITION.tsv"
OLD_EVENTS = ROOT / "experiments/yolo/sidequest_semantic_hybrid_card_retranslation_nine_hundred_forty_fourth/PASS944_2010_PROSE_CARD_INTERLINEAR.tsv"
CLAUSES = ROOT / "experiments/yolo/sidequest_semantic_hybrid_card_retranslation_nine_hundred_forty_fourth/PASS944_354_HYBRID_CARD_CLAUSES.tsv"
PAGES = ROOT / "experiments/yolo/sidequest_semantic_book_function_synthesis_nine_hundred_forty_seventh/PASS947_14_UNIT_BOOK_MAP.tsv"


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: list[dict[str, object]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def collapse(values: list[str]) -> list[str]:
    result: list[str] = []
    pos = 0
    while pos < len(values):
        end = pos + 1
        while end < len(values) and values[end] == values[pos]:
            end += 1
        count = end - pos
        result.append(f"{count}× {values[pos]}" if count > 1 else values[pos])
        pos = end
    return result


def fluent_chain(values: list[str], end_reason: str) -> str:
    chunks = collapse(values)
    sentences: list[str] = []
    for offset in range(0, len(chunks), 6):
        group = chunks[offset:offset + 6]
        body = "; dann ".join(group)
        sentences.append(body[0].upper() + body[1:] + ".")
    if end_reason == "LICENSED_DY_CLOSE":
        sentences.append("Der Teilgang ist damit geschlossen.")
    elif end_reason == "PAGE_END_OPEN":
        sentences.append("Der Gang bleibt für die Fortsetzung offen.")
    return " ".join(sentences)


def main() -> None:
    all_events = {row["event_id"]: row for row in read_tsv(EVENTS)}
    old_events = read_tsv(OLD_EVENTS)
    clauses = read_tsv(CLAUSES)
    page_rows = read_tsv(PAGES)
    clause_by_id = {row["clause_id"]: row for row in clauses}

    prose_events: list[dict[str, object]] = []
    by_clause: dict[str, list[dict[str, object]]] = defaultdict(list)
    for old in old_events:
        current = all_events[old["event_id"]]
        row = {
            "event_id": old["event_id"],
            "clause_id": old["clause_id"],
            "physical_page": old["physical_page"],
            "locus": old["locus"],
            "surface": old["surface"],
            "component_recipe": old["component_recipe"],
            "codebook_layer": current["codebook_layer"],
            "learned_card_id": current["learned_card_id"],
            "pass949_revision": current["pass949_revision"],
            "spoken_value_de": current["current_value_de"],
        }
        prose_events.append(row)
        by_clause[old["clause_id"]].append(row)
    write_tsv(OUT / "PASS950_2010_EXTENDED_CARD_INTERLINEAR.tsv", prose_events)

    clause_rows: list[dict[str, object]] = []
    for clause in clauses:
        members = by_clause[clause["clause_id"]]
        values = [str(row["spoken_value_de"]) for row in members]
        layers = Counter(str(row["codebook_layer"]) for row in members)
        clause_rows.append({
            "clause_id": clause["clause_id"],
            "physical_page": clause["physical_page"],
            "register": clause["register"],
            "start_event": clause["start_event"],
            "end_event": clause["end_event"],
            "events": len(members),
            "learned_formula_events": layers["LEARNED_FORMULA_CARD"],
            "productive_events": layers["PRODUCTIVE_ABBREVIATION_COMPOSITION"],
            "newly_promoted_events": sum(str(row["pass949_revision"]) == "PROMOTED_RECURRENT_FORMULA" for row in members),
            "end_reason": clause["end_reason"],
            "literal_card_chain_de": " → ".join(values),
            "continuous_workshop_reading_de": fluent_chain(values, clause["end_reason"]),
            "event_ids": "|".join(str(row["event_id"]) for row in members),
        })
    write_tsv(OUT / "PASS950_354_EXTENDED_CARD_CLAUSES.tsv", clause_rows)

    clauses_by_page: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in clause_rows:
        clauses_by_page[str(row["physical_page"])].append(row)
    readable = [
        "# Vollständige Vierzehnseiten-Lesung mit 63 Formelkarten",
        "",
        "Jede Prosakarte erscheint in der Interlineare genau einmal. Die Sätze unten sind die komprimierte Werkstattlektüre; die Bilder und lokalen Namen werden weiterhin zuerst gelesen.",
        "",
    ]
    for page in page_rows:
        physical = page["physical_page"]
        readable.extend([f"## {physical} — {page['unit_role_de']}", "", f"{page['concrete_function_de']}. {page['page_reading_de']}", ""])
        for clause in clauses_by_page.get(physical, []):
            readable.extend([f"- **{clause['clause_id']}**: {clause['continuous_workshop_reading_de']}", ""])
        if physical == "f75r":
            readable.extend(["Eingesetztes Mini-Register f75r.47–53: Zielklasse wählen, am zweiten Grad eintragen, Gegenplatz verbinden, an der unteren Quelladresse fortführen, eine Einheit wählen und den Zielplatz schließen.", ""])
    (OUT / "PASS950_COMPLETE_EXTENDED_RETRANSLATION.md").write_text("\n".join(readable), encoding="utf-8")

    promoted = sum(row["pass949_revision"] == "PROMOTED_RECURRENT_FORMULA" for row in prose_events)
    report = f"""# Pass 950 — vollständige Neulesung mit erweitertem Kartensatz

Alle 2.010 Prosagruppen und 354 Klauseln wurden mit dem 63-Karten-Deck neu
gelesen. **{promoted} Prosavorkommen** wechseln dabei von einzeln aufgebauten
Kürzelfolgen zu vertrauten Ganzformeln. Die Reihenfolge, Klauselgrenzen und
offenen beziehungsweise geschlossenen Enden bleiben erhalten.

Auf f75r wird der Siebenzeiler nun als ein einziges eingesetztes Mini-Register
gesprochen. Die falsche Zerlegung in sieben separate Figurenetiketten entfällt.
"""
    (OUT / "PASS950_REPORT.md").write_text(report, encoding="utf-8")
    outputs = {path.name: hashlib.sha256(path.read_bytes()).hexdigest() for path in sorted(OUT.glob("PASS950_*")) if "BUILD_SUMMARY" not in path.name and "VALIDATION" not in path.name}
    summary = {"prose_events": len(prose_events), "clauses": len(clause_rows), "promoted_prose_events": promoted, "outputs": outputs}
    (OUT / "PASS950_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
