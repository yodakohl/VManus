#!/usr/bin/env python3
from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
LEXICON = ROOT / "experiments/yolo/sidequest_semantic_local_sign_meanings_nine_hundred_thirty_eighth/PASS938_56_REVISED_ATOMIC_LEXICON.tsv"
SURFACES = ROOT / "experiments/yolo/sidequest_semantic_complete_surface_dictionary_nine_hundred_thirty_sixth/PASS936_1078_COMPLETE_SURFACE_DICTIONARY.tsv"
EVENTS = ROOT / "experiments/yolo/sidequest_semantic_integrated_fourteen_page_edition_nine_hundred_thirty_ninth/PASS939_2511_CURRENT_EVENT_INTERLINEAR.tsv"


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: list[dict[str, object]], fields: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


WHOLE_VALUES = {
    "daiin": "NACH SOLLMASS",
    "shedy": "ABSETZEN; ENDE",
    "chedy": "DIESEN POSTEN UMSETZEN",
    "qokedy": "KURZ ANSETZEN; ENDE",
    "qokeedy": "LAENGER ANSETZEN; ENDE",
    "dy": "DIESER POSTEN",
    "ol": "DAMIT WEITER",
    "qokain": "EINE PORTION ANSETZEN",
    "chey": "DIESER POSTEN",
    "aiin": "NACH SOLLMASS",
    "s": "VARIANTE WAEHLEN",
    "dal": "ZUR ZIELSTELLE",
    "shey": "KURZ HALTEN",
    "y": "DIESER POSTEN",
    "chol": "DAMIT WEITER",
    "ar": "AUS DER QUELLE",
    "dar": "AUS DEM BEZEICHNETEN TEIL",
    "qoky": "DIESEN POSTEN ANSETZEN",
    "lchedy": "WEITER UMSETZEN; ENDE",
    "qokeey": "LAENGER ANSETZEN",
    "or": "DER ANSATZ",
    "qokaiin": "NACH SOLLMASS ANSETZEN",
    "dain": "EINE PORTION",
    "qokal": "AN DER ZIELSTELLE ANSETZEN",
    "qol": "DAMIT WEITER",
    "cheey": "LAENGER HALTEN",
    "chy": "DIESER POSTEN",
    "otar": "DANACH AUS DER QUELLE",
    "cheol": "DEN AUSZUG WEITERFUEHREN",
    "okar": "AUS DER QUELLE ANSETZEN",
    "oldy": "DAMIT FORTFAHREN; ENDE",
    "sol": "DAMIT WEITER",
    "sar": "QUELLE WAEHLEN",
    "al": "ZUR ZIELSTELLE",
    "am": "AN DER INNENSTELLE",
    "chckhy": "DURCH DEN DURCHLASS FUEHREN",
    "qoty": "DANACH DIESER POSTEN",
    "r": "ZUSTAND MARKIEREN",
    "chor": "VOM ANSATZ ENTNEHMEN",
    "okal": "AN DER ZIELSTELLE ANSETZEN",
    "oky": "DIESEN POSTEN ANSETZEN",
    "qokey": "KURZ ANSETZEN",
    "saiin": "SOLLWERT WAEHLEN",
    "sain": "EINHEIT WAEHLEN",
    "chdy": "DIESEN POSTEN UMSETZEN",
    "o": "ARBEITSGANG AUSFUEHREN",
    "okaiin": "NACH SOLLMASS ANSETZEN",
    "okeey": "LAENGER ANSETZEN",
    "otedy": "NAECHSTEN SCHRITT KURZ; ENDE",
    "qokar": "AUS DER QUELLE ANSETZEN",
    "qoteedy": "NAECHSTEN SCHRITT LAENGER; ENDE",
    "shy": "DIESER POSTEN",
    "cthy": "BIS BEREIT FUEHREN",
    "d": "DER BEZEICHNETE TEIL",
    "okedy": "KURZ ANSETZEN; ENDE",
    "okeedy": "LAENGER ANSETZEN; ENDE",
    "oteey": "NAECHSTEN POSTEN LAENGER HALTEN",
    "otor": "DER NAECHSTE ANSATZ",
    "sal": "ZIELSTELLE WAEHLEN",
    "sheedy": "LAENGER HALTEN; ENDE",
    "shol": "WEITER HALTEN",
    "cheky": "KURZ BEHANDELN",
    "cheor": "AUSZUG MARKIEREN",
    "cho": "SICHTBARER TEIL",
}


def main() -> None:
    lexicon = read_tsv(LEXICON)
    surfaces = read_tsv(SURFACES)
    events = read_tsv(EVENTS)
    surface_by_name = {row["surface"]: row for row in surfaces}

    ranked = sorted(
        [row for row in surfaces if "WORKSHOP_PROSE" in row["observed_channels"]],
        key=lambda row: (-int(row["events"]), row["surface"]),
    )[:64]
    selected = [row["surface"] for row in ranked]
    if set(selected) != set(WHOLE_VALUES):
        raise SystemExit(f"whole-card inventory drift: missing={set(selected)-set(WHOLE_VALUES)} extra={set(WHOLE_VALUES)-set(selected)}")

    stem_rows: list[dict[str, object]] = []
    for row in lexicon:
        total = int(row["total_atom_occurrences"])
        if total >= 100:
            tier = "CORE_ABBREVIATION"
        elif total >= 20:
            tier = "WORKSHOP_ABBREVIATION"
        else:
            tier = "LOCAL_OR_SPECIAL_SIGN"
        stem_rows.append({
            **row,
            "hybrid_codebook_tier": tier,
            "use_rule_de": f"Als Einzelwert {row['atomic_pocket_value_de']} lesen; in einer bekannten Ganzkarte deren gelernte Kurzform vorziehen.",
        })
    write_tsv(OUT / "PASS941_56_PRODUCTIVE_ABBREVIATIONS.tsv", stem_rows, list(stem_rows[0]))

    whole_rows: list[dict[str, object]] = []
    for rank, row in enumerate(ranked, 1):
        whole_rows.append({
            "rank": rank,
            "surface": row["surface"],
            "component_recipe": row["component_recipe"],
            "learned_whole_card_de": WHOLE_VALUES[row["surface"]],
            "literal_component_reading_de": row["workshop_composition_de"],
            "image_register_reading_de": row["image_composition_de"],
            "events": row["events"],
            "physical_pages": row["physical_pages"],
            "registers": row["registers"],
            "channel_class": row["channel_class"],
            "learning_note_de": "Als häufige Formelkarte auswendig lernen; die Komponenten bleiben für neue oder seltene Karten produktiv.",
        })
    write_tsv(OUT / "PASS941_64_LEARNED_WHOLE_CARDS.tsv", whole_rows, list(whole_rows[0]))

    decision_rows: list[dict[str, object]] = []
    for row in surfaces:
        is_whole = row["surface"] in WHOLE_VALUES
        decision_rows.append({
            "surface": row["surface"],
            "component_recipe": row["component_recipe"],
            "events": row["events"],
            "physical_pages": row["physical_pages"],
            "channel_class": row["channel_class"],
            "reading_route": "LEARNED_WHOLE_CARD" if is_whole else "PRODUCTIVE_COMPONENT_COMPOSITION",
            "compact_default_de": WHOLE_VALUES[row["surface"]] if is_whole else row["workshop_composition_de"],
        })
    write_tsv(OUT / "PASS941_1078_HYBRID_DICTIONARY.tsv", decision_rows, list(decision_rows[0]))

    event_rows: list[dict[str, object]] = []
    route_counts: Counter[str] = Counter()
    for row in events:
        surface = row["surface"]
        route = "LEARNED_WHOLE_CARD" if surface in WHOLE_VALUES else "PRODUCTIVE_COMPONENT_COMPOSITION"
        route_counts[route] += 1
        dictionary = surface_by_name[surface]
        if route == "LEARNED_WHOLE_CARD" and row["channel"] == "WORKSHOP_PROSE":
            spoken = WHOLE_VALUES[surface]
        elif row["channel"] == "WORKSHOP_PROSE":
            spoken = dictionary["workshop_composition_de"]
        else:
            spoken = dictionary["image_composition_de"]
        event_rows.append({
            "event_id": row["event_id"],
            "physical_page": row["physical_page"],
            "locus": row["locus"],
            "channel": row["channel"],
            "surface": surface,
            "component_recipe": row["component_recipe"],
            "reading_route": route,
            "hybrid_codebook_reading_de": spoken,
        })
    write_tsv(OUT / "PASS941_2511_HYBRID_EVENT_READINGS.tsv", event_rows, list(event_rows[0]))

    book = [
        "# Pass 941 — Kürzel plus gelernte Ganzkarten",
        "",
        "Ein Lehrling lernt zuerst 56 kurze Werte. Die 64 häufigsten Formeln werden zusätzlich als ganze Karten gesprochen. Unbekannte oder seltene Formen bleiben dadurch lesbar: man setzt ihre Kürzel zusammen.",
        "",
        "## Die 64 Merkformeln",
        "",
    ]
    for row in whole_rows:
        book.append(f"- `{row['surface']}` = **{row['learned_whole_card_de']}**  ←  `{row['component_recipe']}` ({row['events']} Belege)")
    (OUT / "PASS941_HYBRID_POCKET_CODEBOOK.md").write_text("\n".join(book) + "\n", encoding="utf-8")

    report = f"""# Pass 941 — das gesuchte Mischsystem ist jetzt ausführbar

## Architektur

Die beste Werkstattfassung ist weder eine reine Buchstabenschrift noch ein
reiner Nomenklator. Sie hat **56 produktive Kürzel** und **64 gelernte
Ganzkarten**. Die Ganzkarten decken {sum(int(row['events']) for row in ranked)}
der 2.511 sichtbaren Ereignisse ab und kommen zusammen auf allen 14 Seiten vor.
Die übrigen Formen werden aus den Kürzeln gelesen.

Beispiele: `qokedy` wird als ganze Formel „KURZ ANSETZEN; ENDE“ gelernt, bleibt
aber durchsichtig als `OK+E+DY`. `qokeedy` ersetzt nur den kurzen durch den
längeren Grad. `daiin` wird schlicht „NACH SOLLMASS“, `chedy` „DIESEN POSTEN
UMSETZEN“, `shedy` „ABSETZEN; ENDE“ gesprochen.

## Warum das besser passt

Ein Schreiber muss nicht jede lange Oberfläche neu erraten. Häufige Karten
werden wie technische Brevigraphen auswendig gelernt; seltene Karten lassen
sich aus START, KURZ/LANG, ZIEL, QUELLE, SOLLWERT, DIES und ENDE neu bilden.
Das erklärt zugleich Gleichförmigkeit und die große seltene Schwanzschicht.
"""
    (OUT / "PASS941_REPORT.md").write_text(report, encoding="utf-8")
    summary = {
        "productive_abbreviations": len(stem_rows),
        "learned_whole_cards": len(whole_rows),
        "surfaces": len(decision_rows),
        "events": len(event_rows),
        "event_route_counts": dict(route_counts),
        "outputs": {},
    }
    for path in sorted(OUT.glob("PASS941_*")):
        summary["outputs"][path.name] = hashlib.sha256(path.read_bytes()).hexdigest()
    (OUT / "PASS941_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
