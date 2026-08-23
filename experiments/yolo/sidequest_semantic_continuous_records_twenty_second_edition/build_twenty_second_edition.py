#!/usr/bin/env python3
from pathlib import Path
from collections import defaultdict
import csv
import json

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
BASE = ROOT / "experiments/yolo/sidequest_semantic_owner_filled_twenty_first_edition"


def read(path):
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(path, fields, rows):
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


NARRATIVES = {
    "H1": (
        "Wurzel-Wasserauszug",
        "Nimm von der abgebildeten Pflanze den Wurzelteil, säubere und zerschneide ihn, gib ihn in ein Gefäß und gieße Wasser darüber. Fange den ersten Auszug auf, gebrauche ein kleines örtliches Maß und verwahre den Rest. Nimm später noch einmal vom frischen Auszug, erwärme ihn gelinde und gebrauche ihn, sobald er bereit ist.",
        "Wurzelmaterial säubern, mazerieren, Prüfportion buchen und Rest lagern; kein Heilanlass nötig.",
    ),
    "H2": (
        "Zwei Erntefraktionen zu Salbe",
        "Sammle junge Spitzen, Blütenstände und Blätter beim Öffnen, zerstoße und presse sie durch Tuch. Fange die erste Fraktion auf, gib Öl im Sollmaß hinzu und erwärme gelinde. Nimm vor voller Blüte eine zweite Portion, vereinige beide Fraktionen im gleichen Maß, gib sie ins glasierte Gefäß, rühre bei kleinem Feuer bis zur weichen Salbe, bewahre sie bedeckt und lege sie äußerlich auf eine harte Schwellung.",
        "Zwei zeitlich getrennte Pflanzenfraktionen werden verglichen, vereinigt und als Materialprobe konserviert.",
    ),
    "H3": (
        "Blütenauszug und zweite Ölbereitung",
        "Nimm im frühen Frühjahr Blüten und junge Blätter, koche sie in Wein, wringe durch feines Tuch, lass stehen und seihe nochmals bis zum klaren Zustand. Kühle den ersten Auszug ab und behalte frische Blüten zurück. Gib vom Auszug ein kleines Maß als Trank; die zurückbehaltenen Blüten erwärme in Öl und streiche die fertige Bereitung äußerlich um die Lider.",
        "Blüten- und Blattfraktionen extrahieren, klären und als zwei Referenzproben lagern; Trank und Augenanwendung entfallen.",
    ),
    "H4": (
        "Blatt-Wein-Auszug und warmer Umschlag",
        "Zerstoße breite Blätter, gib Weißwein hinzu, verschließe das Gefäß und lass es kühl stehen. Miss eine Portion ab, wringe sie durch Leinwand, lass den Auszug klar absetzen und verwahre ihn. Wasche damit eine äußere Wunde. Aus zurückbehaltenen Blättern, Honig und gelinder Wärme bereite einen frischen Umschlag für die bezeichnete Stelle.",
        "Blätter in zwei Konservierungs- und Prüfchargen teilen: filtrierter Auszug und warmer Materialumschlag ohne Heilangabe.",
    ),
    "H5": (
        "Feuchtstandort-Pflanze: kurze Hautauflage und milder Trank",
        "Sammle das oberirdische Kraut zu Beginn der Blüte am feuchten Standort. Zerstoße wenige frische klebrige Blätter und lege sie nur kurz auf eine Warze oder ein Hühnerauge; nimm sie ab, wasche die Stelle und wiederhole nur bei guter Verträglichkeit. Trockne die übrigen Blütenstiele im Schatten, bereite mit mildem Wein einen schwachen Auszug, seihe, gib Honig hinzu und gebrauche ein kleines Maß als Brusttrank.",
        "Eine klebrige Feuchtstandortpflanze liefert eine kurze Materialprobe und einen gesonderten Wein-Honig-Auszug; Krankheit und Wirkung bleiben austauschbar.",
    ),
    "B1": (
        "Gemeinsames zweireihiges Becken",
        "Richte am gemeinsamen Figurenbecken eine abgemessene Waschcharge ein. Führe sie durch die örtlichen Läufe, halte und temperiere sie, mische bis gleichmäßig, lass sie stehen und sammle die klare Fraktion. Spüle Becken und Leitung, wasche den bezeichneten Bereich, benutze den unteren Ablauf und führe die Restflüssigkeit ab. Einzelne kurze, lange und warme Durchgänge sind Varianten derselben lokalen Station.",
        "Badehausbetrieb: Waschflotte ansetzen, temperieren, durch lokale Läufe führen, Becken reinigen und ablassen; keine Therapie nötig.",
    ),
    "B2": (
        "Paarbecken, Mittelknoten und unteres Mehrfigurenfeld",
        "Spüle zuerst die obere Paarbeckenstation, stelle die Mischung bereit und bemesse die Portion für das temperierte Teilbad. Führe sie durch Öffnungen und Tuch, temperiere und ziehe ab. Am mittleren Knoten gib sauberes Wasser zu, halte warm und prüfe den Zustand. Nach dem sichtbaren Stationswechsel beginne im unteren Feld eine neue Charge: abführen, unteren Ablauf schließen, mit kühlem und warmem Wasser ausgleichen, spülen, waschen und einen warmen Tuchgang ausführen.",
        "Mehrstationiger Badehaus-/Wasserwerkszettel mit Reinigung, Temperierung und Abfluss; die Figuren markieren Arbeitsplätze statt Patienten.",
    ),
    "B3": (
        "Randstationen bis zum Hauptpaar",
        "Arbeite nacheinander an der oberen Fächerstation, dem runden Gefäß, dem korbartigen Empfänger und den Zwischenposten: bemessen, mischen, temperieren, absetzen, klarziehen, waschen und verbrauchte Flüssigkeit abführen. Bei jedem sichtbaren Stationswechsel beginnt der Stoffbezug neu. Am Hauptpaar lege einen warmen Tuchgang an, spüle, ziehe den klaren Anteil ab, mische zu gleichen Teilen und beende mit Absetzen, Prüfung und unterem Becken.",
        "Stationsbuch für mehrere Gefäß- und Waschposten; kein einziger gerichteter Kreislauf verbindet alle Teilbilder.",
    ),
    "B4": (
        "Tuchanwendung und Unterlauf",
        "Tauche Tuch oder Auflage in die temperierte Flüssigkeit, führe die Charge zum bezeichneten Haut- oder Wundplatz, lege das warme Tuch auf und seihe die nächste Portion. Arbeite weiter, solange sie warm ist. Wechsle dann zur linken Unterlaufstation: bemessen, sanft wärmen, mischen, zweimal waschen und abführen. Nach dem sichtbaren Wechsel zur rechten S-Laufstation öffne den oberen Lauf, gieße warmes Wasser ins untere Becken und lass es bereit stehen.",
        "Wäsche-/Filtereinsatz mit anschließendem Spül- und Unterlaufbetrieb; die Körperlesung kann entfallen.",
    ),
    "B5": (
        "Kurzer Fransen-Endposten",
        "Ziehe die vorige Charge am linken Fransen-Endposten ab, erwärme einmal und führe sie für den angegebenen Zeitabschnitt zur örtlichen Station. Setze die vorige Mischung fort, bemesse sie, benutze die zweite Öffnung und rühre bis gleichmäßig.",
        "Kurzer Nebenposten eines Wasser- oder Waschbetriebs.",
    ),
    "B6": (
        "Rechter S-Lauf-Endposten",
        "Richte am rechten S-Lauf die bezeichnete Beckenstation ohne Kochen ein. Benutze die erste Öffnung, führe den Posten im Arbeitsgang fort, bemesse ihn, leite ihn durch Tuch und bringe die aktive Portion an die bezeichnete Stelle.",
        "Abschlussbuchung eines lokalen Filter-/Beckenpostens.",
    ),
}

statements = read(BASE / "TWENTY_FIRST_116_OWNER_FILLED_PROSE.tsv")
by_record = defaultdict(list)
for row in statements:
    by_record[row["record_id"]].append(row)

record_rows = []
for record in ("H1", "H2", "H3", "H4", "H5", "B1", "B2", "B3", "B4", "B5", "B6"):
    members = by_record[record]
    title, narrative, rival = NARRATIVES[record]
    owners = list(dict.fromkeys(row["image_owner"] for row in members))
    record_rows.append(
        {
            "record_id": record,
            "page": members[0]["page"],
            "title_de": title,
            "statement_count": len(members),
            "group_count": sum(int(row["group_count"]) for row in members),
            "statement_ids": "|".join(row["statement_id"] for row in members),
            "image_owner_chain": " -> ".join(owners),
            "literal_card_chain_de": " || ".join(row["literal_card_reading_de"] for row in members),
            "continuous_workshop_translation_de": narrative,
            "continuous_technical_rival_de": rival,
        }
    )
write(HERE / "TWENTY_SECOND_11_CONTINUOUS_RECORDS.tsv", list(record_rows[0]), record_rows)

lines = [
    "# Elf fortlaufende Werkstattübersetzungen",
    "",
    "Zeilen sind keine Satzgrenzen. Jede Fassung deckt alle Aussagen ihres Records",
    "und wechselt den stillen Besitzer nur dort, wo das Bild tatsächlich wechselt.",
    "",
]
for row in record_rows:
    lines.extend(
        [
            f"## {row['record_id']} — {row['title_de']} ({row['page']})",
            "",
            f"Besitzerfolge: **{row['image_owner_chain']}**.",
            "",
            row["continuous_workshop_translation_de"],
            "",
            f"Technischer Rivale: {row['continuous_technical_rival_de']}",
            "",
            f"Gebundene Aussagen: `{row['statement_ids']}`",
            "",
        ]
    )
(HERE / "TWENTY_SECOND_CONTINUOUS_WORKSHOP_TRANSLATION.md").write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")

summary = {
    "status": "PASS",
    "counts": {
        "records": len(record_rows),
        "statements": sum(int(row["statement_count"]) for row in record_rows),
        "groups": sum(int(row["group_count"]) for row in record_rows),
        "herbal_records": 5,
        "biological_records": 6,
        "records_with_owner_change": sum(" -> " in row["image_owner_chain"] for row in record_rows),
    },
}
(HERE / "BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(json.dumps(summary, ensure_ascii=False, indent=2))
