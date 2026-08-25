#!/usr/bin/env python3
from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
P971 = ROOT / "experiments/yolo/sidequest_semantic_canonical_compact_workshop_edition_nine_hundred_seventy_first"


def write_tsv(path: Path, rows: list[dict[str, object]], fields: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


PAGE_ROWS = [
    {
        "physical_page": "f10r",
        "canvas_or_source": "https://www.voynich.com/folios/color/010r.jpg",
        "review_sha256": "10cbe2bf1d60ba299f362d23e5859c3463256be9a2102a8da75c30a5d512cd67",
        "review_dimensions": "1107x1536",
        "visual_owner_id": "F10R_BLUE_HEAD_DOUBLE_STORAGE_ROOT",
        "visible_form_de": "Aufrechter Stängel; paarige gesägte breite Blätter; blauer endständiger Kopf; waagrechter Wurzelstock mit zwei roten Speicherorganen.",
        "likely_used_parts_de": "Speicherwurzel/Wurzelstock zuerst; daneben Blatt und blauer Kopf als getrennte Ernteposten.",
        "functional_owner_de": "zweiknolliges blauköpfiges Heilkraut",
        "adventurous_identity_guess_de": "Skabiosen-/Flockenblumen-Typ mit überzeichnetem Speicherwurzelstock",
        "owner_confidence": "MEDIUM",
        "revised_page_reading_de": "Nimm zunächst vom doppelten Speicherwurzelstock, setze daraus den ersten Ansatz und führe ihn bis zum geschlossenen Gebrauchszustand. Danach nimm Blatt oder blauen Kopf nach Sollmaß als zweiten Posten, gib ihn zu und führe den noch offenen Ansatz weiter.",
        "hard_visual_correction_de": "Die zwei roten Speicherorgane sind bildlich stärker als jede Wasser-Hypothese; Wasser bleibt mögliches Medium, nicht sichtbarer Besitzer.",
    },
    {
        "physical_page": "f11r",
        "canvas_or_source": "https://www.voynich.com/folios/color/011r.jpg",
        "review_sha256": "cf59bd10136cff0c6d400c9d86c9f96b7e004b5fbb512c14ed7de89e99cf0353",
        "review_dimensions": "1096x1536",
        "visual_owner_id": "F11R_FLOWERING_THREE_CROWN_SOD",
        "visible_form_de": "Dichter blühender Soden aus vielen rund gekerbten Blättern; drei klar getrennte Kronen/Stiele; darunter kreuzende lange zähnige Wurzeläste.",
        "likely_used_parts_de": "ganzer blühender Soden oder drei abgeteilte bewurzelte Kronen",
        "functional_owner_de": "teilbarer blühender Mehrkronenstock",
        "adventurous_identity_guess_de": "Veilchen-/Gundelreben-artiger niedriger Blütensoden",
        "owner_confidence": "MEDIUM_HIGH",
        "revised_page_reading_de": "Halte den blühenden Stock zusammen, teile ihn in bewurzelte Kronen und nimm von jeder die vorgeschriebene Portion. Gib die Teile in den Ansatz, arbeite sie weiter und trenne oder leite den letzten Zug ab; der Folgezug bleibt offen.",
        "hard_visual_correction_de": "Das Bild zeigt keinen einzelnen Pflanzenstamm, sondern mindestens drei bewurzelte Kronen; TEIL/TRENNEN bekommt hier erstmals einen sehr konkreten Bildträger.",
    },
    {
        "physical_page": "f13r",
        "canvas_or_source": "https://collections.library.yale.edu/iiif/2/1006098/full/2000,/0/default.jpg",
        "review_sha256": "f5e5ac17156704dbf7424bd2d59ff287d9194d91f24033fed4d53d9dabcf6cf5",
        "review_dimensions": "2000x2863",
        "visual_owner_id": "F13R_LARGE_CROWN_ROOT_LOBED_LEAF_SIMPLE",
        "visible_form_de": "Sehr großer rotbrauner Speicherwurzelkörper mit fingerartigen Ausläufern und heller Knospenkrone; breite rund gelappte gezähnte Blätter; dichter endständiger Blütenstand.",
        "likely_used_parts_de": "Speicherwurzel/Krone, Blatt und Blütenstand als drei getrennte Materialklassen",
        "functional_owner_de": "großwurzeliges breitblättriges Kronenkraut",
        "adventurous_identity_guess_de": "Malven-/Pestwurz-Typ mit stark überzeichneter Arzneiwurzel",
        "owner_confidence": "MEDIUM_HIGH",
        "revised_page_reading_de": "Bereite zuerst den Ansatz aus der großen Krone oder Wurzel. Setze Blatt und Blütenstand als getrennte Posten nach Sollmaß ein, halte und führe sie durch vier kurze geschlossene Arbeitsschritte; der letzte Zusatz bleibt offen.",
        "hard_visual_correction_de": "Die Seite bietet drei klar unterscheidbare Pflanzenteile; die fünf kurzen Textgänge können daher Teilzubereitungen sein, ohne fünf verschiedene Pflanzen zu erfinden.",
    },
    {
        "physical_page": "f55v",
        "canvas_or_source": "https://www.voynich.com/folios/color/055v.jpg",
        "review_sha256": "21e8e7b405801501b7f8f9e3deba51e0936881c85b5e11d19b712e214e9d6580",
        "review_dimensions": "1215x1536",
        "visual_owner_id": "F55V_GREAT_UMBELLIFER_ROOT_LEAF_UMBEL",
        "visible_form_de": "Große Blattkrone; langer rötlicher Schaft; deutlich verzweigter, gitterartiger Doldenstand mit blauen Enden; kräftiger Wurzelstock mit Seitenwurzel und rundem Speicheransatz.",
        "likely_used_parts_de": "Wurzelstock, Blattkrone und Samen-/Blütendolde",
        "functional_owner_de": "große aromatische Doldenpflanze",
        "adventurous_identity_guess_de": "Engelwurz-/Liebstöckel-/Meisterwurz-Typ",
        "owner_confidence": "HIGH_FOR_UMBELLIFER_TYPE__LOW_FOR_SPECIES",
        "revised_page_reading_de": "Setze die Wurzelzubereitung der großen Doldenpflanze an. Gib Blatt- und Doldenanteile in notierten Portionen zu, versetze den Ansatz zwischen Gefäßstellen, entnimm Proben und führe einen Teil durch den Durchlass. Vier Teilgänge schließen; der lange Hauptansatz bleibt offen.",
        "hard_visual_correction_de": "Die alte Wasserufer-/Dock-/Plantain-Lesung verliert; der verzweigte Doldenstand spricht deutlich stärker für eine große Doldenpflanze.",
    },
    {
        "physical_page": "f56r",
        "canvas_or_source": "https://www.voynich.com/folios/color/056r.jpg",
        "review_sha256": "cd29de3b1b21574a041a9b63b23a12164b6409eef7df7b6eb4bf657606064547",
        "review_dimensions": "1177x1536",
        "visual_owner_id": "F56R_THORNY_HEAD_LIFE_STAGE_SERIES",
        "visible_form_de": "Ein hoher Stängel trägt zwei stachelige dunkle Knospen/Köpfe, zwei blaue Blütenformen und einen großen spiraligen offenen Scheiben- oder Samenstand.",
        "likely_used_parts_de": "Kopf in Knospen-, Blüten- und reifem Samenstadium; möglicherweise zusätzlich Stängelanteil",
        "functional_owner_de": "stachelköpfiges Kraut in mehreren Reifestufen",
        "adventurous_identity_guess_de": "Distel-/Karden-/Carlina-Typ",
        "owner_confidence": "HIGH_FOR_STAGE_SERIES__MEDIUM_FOR_THISTLE_TYPE",
        "revised_page_reading_de": "Nimm vom stacheligen Kopf in der bezeichneten Reifestufe kleine Anteile und setze sie getrennt an. Gib Knospen-, Blüten- und reife Kopfanteile nacheinander zu, halte oder prüfe jeden Zug und führe den letzten Posten zur nächsten Verwendung.",
        "hard_visual_correction_de": "Die fünf Kopfzeichnungen werden als Entwicklungsreihe eines Krauts gelesen, nicht als fünf unabhängige Zutaten; dadurch erhält STUFE hier einen konkreten Bildsinn.",
    },
    {
        "physical_page": "f88r",
        "canvas_or_source": "https://collections.library.yale.edu/iiif/2/1037112/full/2000,/0/default.jpg",
        "review_sha256": "aa266580695fc4a84cd031015c56f51f1b6ce807b6998c6ef4b8b68bae11983b",
        "review_dimensions": "2000x2752",
        "visual_owner_id": "F88R_THREE_VESSEL_SIXTEEN_DRUG_LABEL_REGISTER",
        "visible_form_de": "Drei hochformatige bemalte Gefäße; drei horizontale Reihen abgetrennter Wurzeln, Blätter und Pflanzenteile; sechzehn kurze Etiketten und drei längere Arbeitsblöcke.",
        "likely_used_parts_de": "sechzehn lokal bezeichnete Drogenposten, in drei Gefäß-/Ansatzgruppen organisiert",
        "functional_owner_de": "Zutaten- und Gefäßregister",
        "adventurous_identity_guess_de": "Apothekerblatt oder Rezept-Nomenklator für drei Ansätze",
        "owner_confidence": "VERY_HIGH_FOR_REGISTER__LOW_FOR_INDIVIDUAL_DRUG_NAMES",
        "revised_page_reading_de": "Wähle in jeder Reihe die bezeichneten Wurzel-, Blatt- oder Fruchtposten. Entnimm die Menge, setze den zugehörigen Gefäßansatz an, gib weitere Bestandteile zu, halte oder leite den Auszug und schließe den Teilgang. Die sechzehn Etiketten sind lokale Drogenadressen, nicht frei übersetzte Arbeitssätze.",
        "hard_visual_correction_de": "f88r erzwingt den Mischbetrieb: produktive Fachkürzel in der Prosa, gelernte Ganznamen/Klassencodes an den abgebildeten Zutaten.",
    },
]


F88_OBJECTS = [
    ("P912-E2362", "TOP_01", "blasser vielzehiger Wurzelbusch mit schmalen Trieben", "Wurzelposten"),
    ("P912-E2363", "TOP_02", "schmale dunkle Spindelwurzel mit langen Fingern", "Wurzelposten"),
    ("P912-E2364", "TOP_03", "heller Hals mit gegabeltem Faserwurzelbüschel", "Wurzelposten"),
    ("P912-E2365", "TOP_04", "braune behaarte Spindelknolle mit feinen Seitenwurzeln", "Knollenposten"),
    ("P912-E2366", "TOP_05", "heller Knotenkopf mit langen geschlungenen Wurzeln", "Wurzelposten"),
    ("P912-E2367", "TOP_06", "einzelnes grünes lanzettliches Blatt", "Blattposten"),
    ("P912-E2415", "MID_01", "kräftiger gegabelter Wurzelstock mit kleiner gelappter Blattkrone", "Wurzel-und-Blatt-Posten"),
    ("P912-E2416", "MID_02", "schmale braune Wurzel mit kleinem grünem Kopf", "Wurzelposten"),
    ("P912-E2417", "MID_03", "aufrechter grüner gezähnter Frucht- oder Blattkörper am Wurzelbüschel", "Frucht-oder-Blatt-Posten"),
    ("P912-E2418", "MID_04", "heller gespreizter Faserwurzelstock", "Wurzelposten"),
    ("P912-E2419", "MID_05", "braun gepunkteter ovaler Körper mit Wurzeln und gezähnten grünen Teilen", "Frucht-oder-Wurzel-Posten"),
    ("P912-E2420", "MID_06", "langer Zweig mit mehreren paarigen grünen Blättern", "Blatt-/Zweigposten"),
    ("P912-E2460", "BOT_01", "runde Krone mit roten Wurzeln und vier gezähnten Blättern", "Kronenposten"),
    ("P912-E2461", "BOT_02", "kriechender dünner Stock mit rund gezähnten Blättern", "Blatt-/Rhizomposten"),
    ("P912-E2462", "BOT_03", "großer geschichteter heller Wurzel- oder Schnittkörper mit rötlichem Grund", "Wurzel-/Schnittposten"),
    ("P912-E2463", "BOT_04", "langer rötlicher Speicherteil mit zwei langen grünen Blättern", "Speicherwurzelposten"),
]


def main() -> None:
    pages = read_tsv(P971 / "PASS971_14_PAGE_EDITION.tsv")
    page_by_id = {row["physical_page"]: row for row in pages}
    revised = []
    for row in PAGE_ROWS:
        source = page_by_id[row["physical_page"]]
        revised.append({
            **row,
            "events": source["events"],
            "prose_clauses": source["prose_clauses"],
            "local_address_events": source["local_address_events"],
            "pass971_page_reading_de": source["current_page_reading_de"],
        })

    page_fields = [
        "physical_page", "canvas_or_source", "review_sha256", "review_dimensions",
        "visual_owner_id", "visible_form_de", "likely_used_parts_de",
        "functional_owner_de", "adventurous_identity_guess_de", "owner_confidence",
        "events", "prose_clauses", "local_address_events", "pass971_page_reading_de",
        "revised_page_reading_de", "hard_visual_correction_de",
    ]
    write_tsv(HERE / "PASS972_SIX_PAGE_VISUAL_OWNER_REVISION.tsv", revised, page_fields)

    ledger = read_tsv(P971 / "PASS971_501_LOCAL_ADDRESS_LEDGER.tsv")
    by_event = {row["event_id"]: row for row in ledger if row["physical_page"] == "f88r"}
    labels = []
    for event_id, object_id, description, object_class in F88_OBJECTS:
        source = by_event[event_id]
        labels.append({
            "event_id": event_id,
            "locus": source["locus"],
            "surface": source["surface"],
            "visual_object_id": object_id,
            "visible_object_de": description,
            "functional_object_class_de": object_class,
            "local_reading_de": f"{object_id}: gelernter Drogenname oder Klassencode für {description}",
            "portable_operation_reading_allowed": "NO__LABEL_REGISTER",
        })
    write_tsv(
        HERE / "PASS972_F88R_SIXTEEN_LABEL_OWNER_MAP.tsv",
        labels,
        ["event_id", "locus", "surface", "visual_object_id", "visible_object_de",
         "functional_object_class_de", "local_reading_de", "portable_operation_reading_allowed"],
    )

    summary = {
        "status": "PASS",
        "pages_reviewed": len(revised),
        "page_events": sum(int(row["events"]) for row in revised),
        "f88r_labels_mapped": len(labels),
        "functional_owner_values": len({row["functional_owner_de"] for row in revised}),
        "species_claims_confirmed": 0,
        "water_visible_as_herbal_owner": 0,
        "strong_corrections": ["F11R_MULTI_CROWN", "F55V_UMBELLIFER", "F56R_STAGE_SERIES", "F88R_LABEL_NOMENCLATOR"],
    }
    (HERE / "PASS972_BUILD_SUMMARY.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    report = f"""# Pass 972 — konkrete Bildbesitzer statt allgemeiner Pflanzenellipse

## Ergebnis

Die sechs Materialseiten lassen sich konkreter lesen, ohne eine einzelne
Pflanzenart zu erzwingen. Der stärkste neue Gewinn ist nicht ein lateinischer
Name, sondern die Art des jeweils still mitgelesenen Materials:

- **f10r:** doppelter Speicherwurzelstock plus Blatt und blauer Kopf;
- **f11r:** ein blühender Soden mit drei abteilbaren bewurzelten Kronen;
- **f13r:** große Arzneiwurzel/Krone, breite gelappte Blätter und Blütenstand;
- **f55v:** große aromatische **Doldenpflanze**, nicht primär Wasserpflanze;
- **f56r:** stachelige Köpfe in Knospen-, Blüten- und Samenreife;
- **f88r:** sechzehn lokale Drogenposten in drei Gefäßgruppen.

Damit bekommen mehrere kurze Kartenwerte eine anschauliche Rücklesung. TEIL
und TRENNEN können auf f11r Kronen teilen; STUFE kann auf f56r Reifestufen
unterscheiden; QUELLE/VORRAT kann auf f10r/f13r/f55v den Wurzelstock meinen;
SETZEN, SOLLWERT und SCHLIESSEN bleiben die gemeinsame Werkstattgrammatik.

## Die wichtigste Revision

f55v war bisher zu oft als Wasserufer-, Dock- oder Plantain-Pflanze gelesen
worden. Der hohe Schaft endet aber in einem klar verzweigten Doldenbau. Die
ökonomischste Arbeitsannahme ist jetzt eine große Doldenpflanze vom
Engelwurz-/Liebstöckel-/Meisterwurz-Typ. Das bindet Wurzelstock, große
Blattkrone und Blüten-/Samenstand in einen einzigen Materia-medica-Artikel.

f56r ist ebenfalls keine lose Phantasieblume. Die stacheligen Knospen, blauen
Blütenformen und die große spiralige Scheibe lassen sich als mehrere Stadien
eines distelartigen Kopfes lesen. Das erklärt, warum der Text wiederholt
kleine Anteile, Stufen, Halten und Weiterverwendung kombiniert.

## Wasserfrage

Keines der fünf Herbal-Bilder zeigt sicher Wasser, einen Bach oder ein Gefäß.
Das heißt ausdrücklich **nicht**, dass die Anweisungen kein Wasser verwenden.
Es bedeutet nur: Wasser ist dort ein mögliches stilles Medium der
Zubereitung, nicht der sichtbare Pflanzenbesitzer. Auf f88r sind dagegen echte
Gefäße sichtbar; dort ist eine Flüssigkeits-/Ansatzlesung bildlich deutlich
leichter.

## f88r: lokaler Nomenklator

Die sechzehn kurzen Etiketten wurden einzeln den sechzehn sichtbaren
Wurzel-/Blatt-/Fruchtposten zugeordnet. Sie werden nicht als sechzehn kleine
Arbeitssätze zerlegt. Das Mischsystem lautet hier besonders klar:

> Bildetikett = gelernter Drogenname oder Klassencode.  Lauftext = kurze
> produktive Werkstattkarten für Auswahl, Menge, Ansatz, Halten, Leiten und
> Schluss.

## Kompakte Arbeitsübersetzung

> Nimm vom im Bild bezeichneten Wurzel-, Blatt-, Blüten- oder Fruchtposten.
> Teile ihn nach dem sichtbaren Körper oder Reifestadium, gib die notierte
> Menge in den Ansatz, halte oder leite den Gang und schließe ihn. Auf f88r
> wähle dazu den etikettierten Drogenposten und das zugehörige Gefäß.

Die Artnamen bleiben Wetten. Die funktionalen Besitzer — Speicherwurzel,
Mehrkronenstock, Doldenpflanze, Reifestufenköpfe und Zutatenregister — sind die
neue konkrete Arbeitsbasis.
"""
    (HERE / "PASS972_VISUAL_MATERIAL_OWNER_REPORT.md").write_text(report, encoding="utf-8")


if __name__ == "__main__":
    main()
