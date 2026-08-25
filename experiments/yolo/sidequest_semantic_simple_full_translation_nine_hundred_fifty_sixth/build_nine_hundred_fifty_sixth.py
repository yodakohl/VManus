#!/usr/bin/env python3
from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
EVENTS = ROOT / "experiments/yolo/sidequest_semantic_concrete_root_lemmas_nine_hundred_fifty_fifth/PASS955_2511_SIMPLE_ROOT_AND_FORMULA_EDITION.tsv"
OLD_PROSE = ROOT / "experiments/yolo/sidequest_semantic_hybrid_card_retranslation_nine_hundred_forty_fourth/PASS944_2010_PROSE_CARD_INTERLINEAR.tsv"
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


def main() -> None:
    all_events = {row["event_id"]: row for row in read_tsv(EVENTS)}
    old_prose = read_tsv(OLD_PROSE)
    clauses = read_tsv(CLAUSES)
    pages = read_tsv(PAGES)

    prose: list[dict[str, object]] = []
    by_clause: dict[str, list[dict[str, object]]] = defaultdict(list)
    for old in old_prose:
        current = all_events[old["event_id"]]
        row = {
            "event_id": old["event_id"], "clause_id": old["clause_id"], "physical_page": old["physical_page"], "locus": old["locus"],
            "surface": old["surface"], "component_recipe": old["component_recipe"], "codebook_layer": current["codebook_layer"],
            "learned_card_id": current["learned_card_id"], "simple_reading_route": current["simple_reading_route"],
            "simple_card_reading_de": current["simple_card_reading_de"],
        }
        prose.append(row)
        by_clause[old["clause_id"]].append(row)
    write_tsv(OUT / "PASS956_2010_SIMPLE_PROSE_INTERLINEAR.tsv", prose)

    clause_rows: list[dict[str, object]] = []
    for clause in clauses:
        members = by_clause[clause["clause_id"]]
        layers = Counter(str(row["codebook_layer"]) for row in members)
        literal_cards = [f"{row['surface']}={row['simple_card_reading_de']}" for row in members]
        reading = "; dann ".join(str(row["simple_card_reading_de"]) for row in members)
        if clause["end_reason"] == "LICENSED_DY_CLOSE":
            reading += ". Teilgang geschlossen."
        elif clause["end_reason"] == "PAGE_END_OPEN":
            reading += ". Zur Fortsetzung offen."
        else:
            reading += "."
        clause_rows.append({
            "clause_id": clause["clause_id"], "physical_page": clause["physical_page"], "register": clause["register"],
            "start_event": clause["start_event"], "end_event": clause["end_event"], "events": len(members),
            "formula_cards": layers["LEARNED_FORMULA_CARD"], "root_compositions": layers["PRODUCTIVE_ABBREVIATION_COMPOSITION"],
            "end_reason": clause["end_reason"],
            "surface_equals_reading": " | ".join(literal_cards),
            "simple_continuous_reading_de": reading,
            "event_ids": "|".join(str(row["event_id"]) for row in members),
        })
    write_tsv(OUT / "PASS956_354_SIMPLE_CLAUSE_TRANSLATIONS.tsv", clause_rows)

    by_page: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in clause_rows:
        by_page[str(row["physical_page"])].append(row)
    md = [
        "# Vollständige einfache Übersetzung der 14 Seiten",
        "",
        "Die Gleichungen `Oberfläche=Lesung` zeigen jede Karte. Ein Punkt `·` trennt Stämme innerhalb einer produktiven Karte; ein Semikolon trennt aufeinanderfolgende Karten.",
        "",
    ]
    for page in pages:
        physical = page["physical_page"]
        md.extend([f"## {physical} — {page['unit_role_de']}", "", f"{page['concrete_function_de']}. {page['page_reading_de']}", ""])
        for clause in by_page.get(physical, []):
            md.extend([f"### {clause['clause_id']}", "", f"{clause['surface_equals_reading']}", "", f"**Lesung:** {clause['simple_continuous_reading_de']}", ""])
    (OUT / "PASS956_COMPLETE_SIMPLE_FOURTEEN_PAGE_TRANSLATION.md").write_text("\n".join(md), encoding="utf-8")

    layers = Counter(row["codebook_layer"] for row in prose)
    report = f"""# Pass 956 — die Vollübersetzung spricht jetzt in kurzen Werten

Alle 2.010 Prosakarten und 354 Klauseln sind neu gesetzt. Innerhalb einer Karte
steht kein versteckter deutscher Satz mehr: produktive Karten zeigen nur die
Folge ihrer Einwortlemmata; gelernte Formeln tragen einen ausdrücklich
memorierten Werkstattwert.

In der Prosa entfallen {layers['LEARNED_FORMULA_CARD']} Ereignisse auf
Formelkarten und {layers['PRODUCTIVE_ABBREVIATION_COMPOSITION']} auf freie
Stammkompositionen. Die Bild-/Adressschicht bleibt außerhalb der Prosaklauseln
an ihren sichtbaren Besitzern.
"""
    (OUT / "PASS956_REPORT.md").write_text(report, encoding="utf-8")
    outputs = {path.name: hashlib.sha256(path.read_bytes()).hexdigest() for path in sorted(OUT.glob("PASS956_*")) if "BUILD_SUMMARY" not in path.name and "VALIDATION" not in path.name}
    summary = {"prose_events": len(prose), "clauses": len(clause_rows), "prose_layer_counts": layers, "outputs": outputs}
    (OUT / "PASS956_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
