#!/usr/bin/env python3
from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
ENTRIES = ROOT / "experiments/yolo/sidequest_semantic_compact_30_card_deck_nine_hundred_sixty_fifth/PASS965_COMPACT_86_ENTRY_CODEBOOK.tsv"
SURFACES = ROOT / "experiments/yolo/sidequest_semantic_surface_invariant_dictionary_nine_hundred_sixty_sixth/PASS966_1078_SURFACE_DICTIONARY.tsv"
ENCODER = ROOT / "experiments/yolo/sidequest_semantic_bidirectional_workshop_compiler_nine_hundred_seventieth/PASS970_948_RECIPE_ENCODER.tsv"
EVENTS = ROOT / "experiments/yolo/sidequest_semantic_compact_30_card_deck_nine_hundred_sixty_fifth/PASS965_2511_COMPACT_DECK_EDITION.tsv"
PROSE_MEMBERSHIP = ROOT / "experiments/yolo/sidequest_semantic_canonical_122_entry_edition_nine_hundred_fifty_eighth/PASS958_2010_CANONICAL_PROSE_INTERLINEAR.tsv"
CLAUSE_MEMBERSHIP = ROOT / "experiments/yolo/sidequest_semantic_canonical_122_entry_edition_nine_hundred_fifty_eighth/PASS958_354_CANONICAL_CLAUSE_TRANSLATIONS.tsv"
LOCAL = ROOT / "experiments/yolo/sidequest_semantic_diagram_address_readings_nine_hundred_thirtieth/PASS930_501_ADDRESS_EVENT_LEDGER.tsv"
F75_CORRECTION = ROOT / "experiments/yolo/sidequest_semantic_f75r_triangular_inset_nine_hundred_forty_eighth/PASS948_10_TRIANGULAR_INSET_EVENTS.tsv"
PAGES = ROOT / "experiments/yolo/sidequest_semantic_canonical_122_entry_edition_nine_hundred_fifty_eighth/PASS958_14_CANONICAL_PAGE_READINGS.tsv"
WRAPPER_RULES = ROOT / "experiments/yolo/sidequest_semantic_renderer_allograph_handbook_nine_hundred_sixty_seventh/PASS967_RENDERER_RULES.tsv"
POSITION_RULES = ROOT / "experiments/yolo/sidequest_semantic_wrapper_position_manual_nine_hundred_sixty_eighth/PASS968_WRAPPER_POSITION_COUNTS.tsv"


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: list[dict[str, object]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    entries = read_tsv(ENTRIES)
    surfaces = read_tsv(SURFACES)
    encoder = read_tsv(ENCODER)
    events = read_tsv(EVENTS)
    prose_membership = read_tsv(PROSE_MEMBERSHIP)
    clause_membership = read_tsv(CLAUSE_MEMBERSHIP)
    local = read_tsv(LOCAL)
    f75 = {row["event_id"]: row for row in read_tsv(F75_CORRECTION)}
    pages = read_tsv(PAGES)
    wrappers = read_tsv(WRAPPER_RULES)
    positions = read_tsv(POSITION_RULES)

    write_tsv(OUT / "PASS971_86_ENTRY_DICTIONARY.tsv", entries)
    write_tsv(OUT / "PASS971_1078_SURFACE_DICTIONARY.tsv", surfaces)
    write_tsv(OUT / "PASS971_948_RECIPE_ENCODER.tsv", encoder)
    write_tsv(OUT / "PASS971_2511_EVENT_EDITION.tsv", events)

    event_by_id = {row["event_id"]: row for row in events}
    prose_rows: list[dict[str, object]] = []
    by_clause: dict[str, list[dict[str, object]]] = defaultdict(list)
    for old in prose_membership:
        current = event_by_id[old["event_id"]]
        row = {
            "event_id": old["event_id"], "clause_id": old["clause_id"], "physical_page": old["physical_page"],
            "locus": old["locus"], "surface": old["surface"], "component_recipe": old["component_recipe"],
            "compact_layer": current["compact_layer"], "formula_card_id": current["formula_card_id"],
            "portable_core_de": current["portable_atomic_reading_de"],
            "owner_filled_reading_de": current["register_expansion_de"],
        }
        prose_rows.append(row)
        by_clause[old["clause_id"]].append(row)
    write_tsv(OUT / "PASS971_2010_PROSE_INTERLINEAR.tsv", prose_rows)

    clause_rows: list[dict[str, object]] = []
    for clause in clause_membership:
        members = by_clause[clause["clause_id"]]
        core = " ; ".join(str(row["portable_core_de"]) for row in members)
        expanded = " ; ".join(str(row["owner_filled_reading_de"]) for row in members)
        ending = "TEILGANG GESCHLOSSEN" if clause["end_reason"] == "LICENSED_DY_CLOSE" else "FORTSETZUNG OFFEN" if clause["end_reason"] == "PAGE_END_OPEN" else "LOKALER ABSCHNITT"
        counts = Counter(str(row["compact_layer"]) for row in members)
        clause_rows.append({
            "clause_id": clause["clause_id"], "physical_page": clause["physical_page"],
            "start_event": clause["start_event"], "end_event": clause["end_event"], "events": len(members),
            "productive_events": counts["PRODUCTIVE_ABBREVIATION_COMPOSITION"],
            "learned_formula_events": counts["LEARNED_FORMULA_CARD"],
            "end_reason": clause["end_reason"],
            "portable_core_clause_de": f"{core}. {ending}.",
            "owner_filled_clause_de": f"{expanded}. {ending}.",
            "event_ids": "|".join(str(row["event_id"]) for row in members),
        })
    write_tsv(OUT / "PASS971_354_CLAUSE_EDITION.tsv", clause_rows)

    local_rows: list[dict[str, object]] = []
    for row in local:
        if row["event_id"] in f75:
            correction = f75[row["event_id"]]
            visible_owner = correction["corrected_owner_de"]
            address_reading = correction["local_reading_de"]
            owner_id = correction["corrected_owner_id"]
            correction_status = "F75_TRIANGULAR_INSET_CORRECTED"
        else:
            visible_owner = row["visible_owner_de"]
            address_reading = row["address_reading_de"]
            owner_id = row["diagram_unit"]
            correction_status = "UNCHANGED"
        local_rows.append({
            "event_id": row["event_id"], "diagram_unit": row["diagram_unit"], "physical_page": row["physical_page"],
            "locus": row["locus"], "surface": row["surface"], "owner_id": owner_id,
            "visible_owner_de": visible_owner, "component_recipe": row["component_recipe"],
            "local_address_reading_de": address_reading, "diagram_model": row["diagram_model"],
            "correction_status": correction_status,
        })
    write_tsv(OUT / "PASS971_501_LOCAL_ADDRESS_LEDGER.tsv", local_rows)

    page_rows: list[dict[str, object]] = []
    for row in pages:
        reading = row["canonical_page_reading_de"]
        if row["physical_page"] == "f70v":
            reading = "Im Widderrad bezeichnen die Ringtexte Reihe, Klasse, nächsten Platz, Grad sowie Quell- oder Zielstelle; AIR ist Ringlauf. Im Fischring werden Plätze und Unterplätze des Fischpaars gewählt und mit Grad oder Wert versehen. Beide Paneele sind Adressregister, keine Werkstattrezeptur."
        page_rows.append({
            "physical_page": row["physical_page"], "book_stage": row["book_stage"], "unit_role_de": row["unit_role_de"],
            "events": row["events"], "prose_clauses": sum(clause["physical_page"] == row["physical_page"] for clause in clause_rows),
            "local_address_events": sum(local_event["physical_page"] == row["physical_page"] for local_event in local_rows),
            "current_page_reading_de": reading,
            "current_correction_de": "Sieben Textzeilen gehören zu einer einzigen dreieckigen Insel zwischen Rinnsal und breitem Ablauf." if row["physical_page"] == "f75r" else "NONE",
        })
    write_tsv(OUT / "PASS971_14_PAGE_EDITION.tsv", page_rows)
    write_tsv(OUT / "PASS971_RENDERER_RULES.tsv", wrappers)
    write_tsv(OUT / "PASS971_WRAPPER_POSITION_COUNTS.tsv", positions)

    theory = [
        "# Aktuelle kreative Arbeitstheorie — Pass 971",
        "",
        "## Was für ein Buch das wahrscheinlich ist",
        "",
        "Ein **bildadressiertes praktisches Fachkompendium**: Pflanzen und Stoffe werden ausgewählt und zubereitet; Bade-, Gefäß- und Stationsbilder geben Anwendungen oder Arbeitsplätze vor; Himmelsräder liefern getrennte Zeit-, Klassen- und Stellenregister. Der engste historische Mechanismus ist die Verbindung aus praktischem Rezeptbuch, medizinisch-astrologischem Almanach und kleinem Werkstattcodebuch.",
        "",
        "## Wie die Schrift funktioniert",
        "",
        "- 37 häufige produktive Stämme, 16 seltene Fachstämme, 30 gelernte Ganzkarten.",
        "- drei zusätzliche lokale Diagrammzeichen; insgesamt 83 gemeinsame plus drei lokale Lehreinträge.",
        "- jede der 1.078 beobachteten Oberflächen hat genau eine Stammfolge und einen Kernwert.",
        "- 948 beobachtete Stammfolgen können mit ihrer häufigsten Form wieder geschrieben werden.",
        "- `q-` bevorzugt Zelleintritt/nach Schluss; `s-` bevorzugt physischen Zeilenanfang; `d-/ch-/sh-/t-` sind kartenlokale Hüllen.",
        "- `Y` hält den aktuellen Posten offen; eine lizenzierte `DY`-Karte schließt. Der Zeilenrand beendet keine Aussage.",
        "",
        "## Portable Kernwerte",
        "",
        "`OK=SETZEN`, `CH=NEHMEN`, `K=GEBEN`, `AIIN=SOLLWERT`, `AIN=EINHEIT`, `OR=SATZ`, `AL=ZIEL`, `AR=QUELLE`, `E=KURZ`, `EE=LÄNGER`, `EEE=VOLL`, `Y=DIES`, `DY=SCHLIESSEN`. Im Pflanzenregister werden daraus Ansatz, Portion und Sollmaß; im Himmelsregister Stelle, Index und Tafelwert. Der Stamm selbst wechselt nicht.",
        "",
        "## Buchfolge der 14 Seiten",
        "",
    ]
    for row in page_rows:
        correction = " " + str(row["current_correction_de"]) if row["current_correction_de"] != "NONE" else ""
        theory.append(f"- **{row['physical_page']} — {row['unit_role_de']}**: {row['current_page_reading_de']}{correction}")
    theory.extend([
        "",
        "## Kürzeste Übersetzung des Systems",
        "",
        "Wähle am Bild den Posten. Nimm aus Quelle oder Teil, setze den Arbeitssatz, gib Einheit oder Sollwert, halte ihn kurz/länger/voll, leite ihn zu Ziel oder Durchlass und schließe den Teilgang. Im Himmelsbild werden dieselben Karten als Platz-, Reihen-, Grad- und Wertbefehle gelesen.",
    ])
    (OUT / "PASS971_CURRENT_WORKING_THEORY.md").write_text("\n".join(theory) + "\n", encoding="utf-8")

    manual = """# Kompakte Schreiberanweisung

1. Besitzer im Bild oder laufenden Absatz bestimmen.
2. Eine der 30 häufigen Ganzkarten erkennen; sonst aus 53 produktiven Stämmen lesen.
3. Slots in der Reihenfolge Rahmen/Folge → Handlung → Grad → Argument → DIES oder SCHLIESSEN füllen.
4. Defaultoberfläche aus dem 948-Rezept-Encoder wählen.
5. Nach Zellschluss `q-`, am Zeilenanfang `s-` bevorzugen, aber nur innerhalb der belegten Kartenpalette.
6. Lokale Pflanzennamen, Stationsklassen und Sternadressen aus dem Bildexemplar kopieren.
7. Beim Rücklesen zuerst Oberfläche → Stammfolge, dann Besitzer einsetzen.
"""
    (OUT / "PASS971_COMPACT_APPRENTICE_MANUAL.md").write_text(manual, encoding="utf-8")

    counts = Counter(row["compact_layer"] for row in events)
    report = f"""# Pass 971 — konsolidierte kompakte Werkstattausgabe

Diese Ausgabe ersetzt die Zwischenstände 958–970 als kreative Arbeitsbasis.
Sie enthält 86 Lehreinträge, 1.078 Oberflächen, 948 beobachtete
Komponentenrezepte, 2.511 Ereignisse, 2.010 Prosakarten, 354 Aussagen, 501
Bild-/Adresskarten und 14 Seitenlesungen.

Die Ereignisschichten sind {dict(counts)}. Die f75r-Loci 47–53 sind nun überall
an die eine dreieckige Insel gebunden. Die f70v-Lesung trennt Widder- und
Fischring ohne doppelte Standardformel. Alle Ganzkartenwerte sind portable
Kernfolgen, keine registerabhängigen Satzglossen.
"""
    (OUT / "PASS971_REPORT.md").write_text(report, encoding="utf-8")

    outputs = {
        path.name: hashlib.sha256(path.read_bytes()).hexdigest()
        for path in sorted(OUT.glob("PASS971_*"))
        if "BUILD_SUMMARY" not in path.name and "VALIDATION" not in path.name
    }
    summary = {
        "entries": len(entries), "surfaces": len(surfaces), "recipes": len(encoder), "events": len(events),
        "prose_events": len(prose_rows), "clauses": len(clause_rows), "local_events": len(local_rows), "pages": len(page_rows),
        "layer_counts": counts, "outputs": outputs,
    }
    (OUT / "PASS971_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
