#!/usr/bin/env python3
"""Rewrite the same fourteen units under a coherent nonmedical master source."""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
LEDGER = ROOT / "experiments/yolo/sidequest_semantic_consolidated_workshop_sixty_ninth_edition/SIXTY_NINTH_776_CURRENT_GROUP_LEDGER.tsv"
UNITS = ROOT / "experiments/yolo/sidequest_semantic_consolidated_workshop_sixty_ninth_edition/SIXTY_NINTH_14_CURRENT_UNITS.tsv"

RIVALS = {
    "H1": ("Wurzel-Ausziehartikel", "Zerschneide die Wurzel, setze sie mit Wasser im Gefäß an, fange den ersten Farbstoff- oder Gerbauszug auf, prüfe ein kleines Maß und erwärme den weitergeführten Ansatz.", 4, 3, "innerer Gebrauch oder Körperbeschwerde wäre medizinisch; das Bild zeigt nur Pflanze und Restfläche"),
    "H2": ("Pflanzenleim- oder Schlichteartikel", "Presse junge Spitzen durch Tuch, vereinige zwei gleich bemessene Fraktionen und rühre den Ansatz mit Öl oder Binder bei kleiner Wärme bis zu einer streichfähigen Paste.", 4, 3, "Salbe und Schwellung gegen allgemeine Paste und Werkstückauftrag"),
    "H3": ("Blütenfarbstoff- oder Duftartikel", "Koche Blüten in Wein oder Auszugsmedium, wringe und seihe klar; behalte einen Teil zurück, gebrauche den klaren Auszug als Farbe oder Duftbasis und erwärme den Rest in Öl für eine zweite Beschichtung.", 4, 4, "Trank/Augenanwendung gegen Farb-, Duft- oder Kosmetikprozess"),
    "H4": ("Blattwäsche und Schlichte", "Lasse zerstoßene Blätter mit Auszugsmedium kühl stehen, wringe durch Leinwand, verwahre den klaren Waschposten und gebrauche ihn an Stoff oder Leder; erwärme den Blattrest mit Binder und lege ihn als Schlichte auf.", 3, 4, "Wundwäsche/Auflage gegen Textil- oder Lederwäsche und Klebeschicht"),
    "H5": ("Klebriger Pflanzenrohstoff in zwei Werkstattgängen", "Gebrauche das frische klebrige Kraut kurz an einem kleinen Werkstück und wasche nach; trockne den Rest, bereite einen gesiebten, mit Honig oder Binder versetzten Auszug und dosiere ihn als Vorratsprodukt.", 3, 4, "Warze/Husten gegen ätzenden, klebenden oder konservierenden Werkstoff"),
    "B1": ("Gemeinsames Wasch- und Färbebecken", "Betreibe das zweireihige Becken mit Maß, Wärme, Zusatz, Umrühren, Spülen, Absetzen, Seihen und örtlichem Ablauf; die Figuren markieren Arbeitsplätze oder Benutzer, nicht Krankheiten.", 5, 4, "therapeutisches Gemeinschaftsbad gegen gewöhnlichen Wasch-/Färbebetrieb"),
    "B2": ("Mehrstations-Badehaus oder Waschwerk", "Bediene Paarbecken, Mittelgerät, unteren Sammelpool und Randplätze jeweils neu: füllen, temperieren, portionsweise gebrauchen, abziehen, nachwaschen und schließen.", 5, 4, "Teilbäder und Körperstellen gegen allgemeine Becken- und Stationsbedienung"),
    "B3": ("Gefäß-, Wasch- und Klärstationsregister", "Arbeite die drei Randgefäße und das sichtbare Hauptpaar getrennt ab: setzen, füllen, mischen, klarziehen, waschen, ablassen und lokal schließen; der Zwischenposten bleibt ein Wartungsplatz.", 4, 4, "Körperanwendung gegen lokale Flüssigkeits- und Gefäßwartung"),
    "B4": ("Tuchwäsche, Tränkung und Umlauf", "Tauche Tuch in temperierte Flüssigkeit, filtere und spüle es; mische und bemesse am linken Posten, lasse ab, und fülle am rechten Mehrarmknoten warmes Wasser nach.", 5, 4, "warme Wundauflage gegen Tuchwäsche oder textile Ausrüstung"),
    "B5": ("Linker Bedienposten", "Ziehe eine Portion am offenen Ende ab, erwärme und halte sie, führe sie zum Arbeitsziel, bemesse und mische sie an der zweiten Öffnung.", 2, 4, "kein sichtbarer Körperanker; technischer Bediengang ist direkter"),
    "B6": ("Rechter Filterposten", "Richte den Mehrarmknoten ohne Kochen ein, wähle die erste Öffnung, bemesse, führe durch Tuch und gib die gefilterte Portion an die Zielstation.", 2, 5, "kein sichtbarer Patient; Filter- und Mehrportbetrieb ist bildnäher"),
    "A1": ("Doppeltes Himmels- und Kalendermerkblatt", "Schlage im linken oder rechten Rad nur den lokalen Sektor-, Stern- oder Bedingungswert nach; beide Räder bleiben getrennt.", 4, 4, "iatromathematische Wahl gegen allgemeine Kalender- oder Lehrtafel"),
    "A2": ("Mehrpaneeliger Sternatlas", "Zeige einen lokalen Sternplatz im passenden Paneel und kopiere dessen Exemplaretikett; Zentren und 28 Plätze bilden keine erzwungene Folge.", 4, 4, "Mondstationsgebrauch gegen rein räumlichen Sternkatalog"),
    "A3": ("Arbeitsalmanach aus drei Rosetten", "Benutze links das örtliche 28-Platz-Kalenderinventar, in der Mitte einen Zustands- oder Wetterring und rechts einen Licht- oder Qualitätsring; halte alle drei Schlüssel getrennt.", 4, 4, "medizinische Wahlzeiten gegen allgemeinen Arbeits-, Wetter- oder Qualitätsalmanach"),
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
    units = read_tsv(UNITS)
    unit_rows = []
    for row in units:
        rival_title, rival_text, medical_score, rival_score, discriminator = RIVALS[row["unit_id"]]
        unit_rows.append({
            "unit_order": row["unit_order"],
            "unit_id": row["unit_id"],
            "page": row["page"],
            "register": row["register"],
            "group_count": row["group_count"],
            "medical_or_iatromedical_working_reading": row["compact_current_reading_de"],
            "nonmedical_rival_title": rival_title,
            "nonmedical_rival_reading": rival_text,
            "medical_content_fit_0_to_5": medical_score,
            "nonmedical_content_fit_0_to_5": rival_score,
            "strongest_discriminator": discriminator,
            "shared_formal_architecture": "SAME_CARDS_SAME_CLAUSES_SAME_OWNERS",
        })
    write_tsv(OUT / "SEVENTIETH_14_DUAL_CONTENT_UNITS.tsv", unit_rows)

    unit_lookup = {row["unit_id"]: row for row in unit_rows}
    dual = []
    for row in read_tsv(LEDGER):
        prefix = row["unit_or_locus"].split("-")[0]
        if row["register"] == "ASTRO_LOCAL_LOOKUP":
            prefix = {"f67r2": "A1", "f68r1": "A2", "f69v": "A3"}[row["page"]]
        unit = unit_lookup[prefix]
        dual.append({
            **row,
            "content_unit_id": prefix,
            "medical_master_frame": unit["medical_or_iatromedical_working_reading"],
            "nonmedical_master_frame": unit["nonmedical_rival_reading"],
            "formal_reading_changed": "NO",
            "surface_changed": "NO",
        })
    write_tsv(OUT / "SEVENTIETH_776_DUAL_CONTENT_LEDGER.tsv", dual)

    discriminator_rows = []
    for row in unit_rows:
        direction = "MEDICAL" if int(row["medical_content_fit_0_to_5"]) > int(row["nonmedical_content_fit_0_to_5"]) else "NONMEDICAL" if int(row["nonmedical_content_fit_0_to_5"]) > int(row["medical_content_fit_0_to_5"]) else "TIE"
        discriminator_rows.append({
            "unit_id": row["unit_id"],
            "page": row["page"],
            "medical_fit": row["medical_content_fit_0_to_5"],
            "nonmedical_fit": row["nonmedical_content_fit_0_to_5"],
            "local_direction": direction,
            "decisive_missing_or_present_clue": row["strongest_discriminator"],
            "next_fixed_page_reading_focus": "look for body-use wording versus material/station wording inside the existing unit",
        })
    write_tsv(OUT / "SEVENTIETH_14_CONTENT_DISCRIMINATORS.tsv", discriminator_rows)

    doc = [
        "# Vollständiges nichtmedizinisches Gegenbuch", "",
        "Dieselben Karten, Klauseln, Bilder und lokalen Adressen werden hier unter einem",
        "anderen Meisterexemplar gelesen: Pflanzenrohstoff und Auszug, Wasch-/Färbe-/",
        "Badehausbetrieb und ein allgemeiner Himmels- oder Arbeitsalmanach.", "",
    ]
    for row in unit_rows:
        doc.extend([
            f"## {row['unit_id']} · {row['page']} · {row['nonmedical_rival_title']}", "",
            row["nonmedical_rival_reading"], "",
            f"**Medizinische Parallelfassung:** {row['medical_or_iatromedical_working_reading']}", "",
            f"**Trennendes Detail:** {row['strongest_discriminator']}.", "",
        ])
    (OUT / "SEVENTIETH_COMPLETE_NONMEDICAL_COUNTERBOOK.md").write_text("\n".join(doc).rstrip() + "\n", encoding="utf-8")

    medical_total = sum(int(row["medical_content_fit_0_to_5"]) for row in unit_rows)
    rival_total = sum(int(row["nonmedical_content_fit_0_to_5"]) for row in unit_rows)
    report = [
        "# Siebzigste Werkstattfassung: nichtmedizinisches Gegenbuch", "",
        "## Ergebnis", "",
        "A coherent nonmedical master source can regenerate the same fourteen units",
        "without changing a card, clause, owner or visible surface. It reads Herbal as",
        "plant-material processing, Biological as wash/bath/dyehouse operation and Astro",
        "as a general celestial work almanac.", "",
        f"The deliberately simple local content tally is medical {medical_total} versus nonmedical {rival_total}. The rival is especially strong in H4, H5, B5 and B6; the medical reading is stronger where people, immersion or bodily application are visually natural.", "",
        "This does not weaken the writing-system model. It sharpens the next semantic",
        "task: body-use versus material/station wording must be resolved inside the",
        "existing cards and owners, not by adding new pages or grand book-purpose claims.", "",
        "Only the fixed ten pages were used; f84 and f84r remained sealed.",
    ]
    (OUT / "SEVENTIETH_EDITION_REPORT.md").write_text("\n".join(report).rstrip() + "\n", encoding="utf-8")

    summary = {
        "status": "CONSISTENT",
        "counts": {
            "dual_content_units": len(unit_rows),
            "dual_content_groups": len(dual),
            "content_discriminators": len(discriminator_rows),
            "medical_fit_total": medical_total,
            "nonmedical_fit_total": rival_total,
        },
        "sources": {str(path.relative_to(ROOT)): sha256(path) for path in (LEDGER, UNITS)},
    }
    (OUT / "BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
