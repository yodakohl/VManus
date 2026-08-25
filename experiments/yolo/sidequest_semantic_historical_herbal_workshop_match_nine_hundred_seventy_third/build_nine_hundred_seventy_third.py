#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent


def write_tsv(name: str, rows: list[dict[str, str]], fields: list[str]) -> None:
    with (HERE / name).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


SOURCES = [
    {
        "source_id": "LJS419",
        "date_place": "15. Jh., Norditalien/Veneto",
        "object": "UPenn Oversize LJS 419, Erbario",
        "observed_or_catalogued_mechanism": "Drei Zeichenstile im selben Herbal; konventionelle und fantastische Pflanzen, naturalistischere Nachzeichnungen, Wurzeln/Blätter/Blüten/Früchte; italienische oder lateinische Notizen zu Eigenschaften und Zubereitungen um und über den Bildern.",
        "closest_sidequest_match": "Fünf Herbal-Seiten insgesamt; besonders überzeichnete Wurzeln, mehrteilige Pflanzenkörper und Text um das Bild.",
        "url": "https://openn.library.upenn.edu/Data/0001/html/ljs419.html",
        "weight": "PRIMARY_CLOSEST_IMAGE_AND_LAYOUT_ANALOGUE",
    },
    {
        "source_id": "LJS419_SCAN0040",
        "date_place": "15. Jh., Norditalien/Veneto",
        "object": "LJS 419 Scan 0265_0040",
        "observed_or_catalogued_mechanism": "Zwei sichtbar verschiedene Pflanzenkörper werden mit einem stark verformten tierähnlichen Wurzelkörper und einem kompakten Notizblock auf einer Seite kombiniert.",
        "closest_sidequest_match": "Zeigt, dass überzeichnete oder kombinierte Wurzelbilder keine exakte botanische Anatomie voraussetzen.",
        "url": "https://openn.library.upenn.edu/Data/0001/ljs419/data/web/0265_0040_web.jpg",
        "weight": "DIRECT_VISUAL_COMPARATOR",
    },
    {
        "source_id": "LJS419_SCAN0080",
        "date_place": "15. Jh., Norditalien/Veneto",
        "object": "LJS 419 Scan 0265_0080",
        "observed_or_catalogued_mechanism": "Eine einfache Pflanze trägt einen graphisch gezackten, unnatürlich langen Wurzelweg; der Bildcode ist merkfähig, aber botanisch nicht maßstäblich.",
        "closest_sidequest_match": "f10r/f11r/f13r: Wurzelgeometrie kann den brauchbaren Teil oder eine Merkform übertreiben.",
        "url": "https://openn.library.upenn.edu/Data/0001/ljs419/data/web/0265_0080_web.jpg",
        "weight": "DIRECT_VISUAL_COMPARATOR",
    },
    {
        "source_id": "LJS419_SCAN0120",
        "date_place": "15. Jh., Norditalien/Veneto",
        "object": "LJS 419 Scan 0265_0120",
        "observed_or_catalogued_mechanism": "Ein waagrechter, wiederholt gelappter Rhizomkörper trägt einen stark vereinfachten Blütenstängel.",
        "closest_sidequest_match": "f11r Mehrkronenstock und f55v Seitenrhizom: funktionale Pflanzenteile werden als wiederholbare Bildmodule dargestellt.",
        "url": "https://openn.library.upenn.edu/Data/0001/ljs419/data/web/0265_0120_web.jpg",
        "weight": "DIRECT_VISUAL_COMPARATOR",
    },
    {
        "source_id": "LJS419_SCAN0160",
        "date_place": "15. Jh., Norditalien/Veneto",
        "object": "LJS 419 Scan 0265_0160",
        "observed_or_catalogued_mechanism": "Drei getrennte Pflanzenfiguren mit eigenen Namen stehen nebeneinander; Wurzeln, Blätter, Blüten/Früchte und ein symbolischer Mondhinweis werden auf einer Seite kombiniert.",
        "closest_sidequest_match": "f88r Zutatenreihe und das Nebeneinander von Pflanzenmaterial und Himmels-/Zeitbezug im Gesamtbuch.",
        "url": "https://openn.library.upenn.edu/Data/0001/ljs419/data/web/0265_0160_web.jpg",
        "weight": "DIRECT_VISUAL_COMPARATOR",
    },
    {
        "source_id": "SLOANE4016",
        "date_place": "ca. 1440, Lombardei",
        "object": "British Library Sloane MS 4016, italienisches Herbal",
        "observed_or_catalogued_mechanism": "Vollseitige farbige Pflanzenbilder mit Beschriftungen, häufig mit Tieren oder Personen; norditalienische Tractatus-de-herbis-Bildtradition.",
        "closest_sidequest_match": "Belegt zeitnahe großformatige Bildbesitzer plus gelernte Namen; keine exakte Voynich-Pflanzenidentifikation.",
        "url": "https://searcharchives.bl.uk/catalog/040-002116409",
        "weight": "PRIMARY_POLISHED_HERBAL_CONTROL",
    },
    {
        "source_id": "WELLCOME_MS418",
        "date_place": "Mitte 15. Jh., Frankreich",
        "object": "Wellcome MS.418, medizinische Wässer und andere Heilmittel",
        "observed_or_catalogued_mechanism": "Pflanzenwässer mit vorgeschaltetem Index; Rezeptformeln beginnen mit Recype; Pflanzen, Mengen, Herstellung und Gebrauch werden ohne nötige Wasserillustration textlich verbunden.",
        "closest_sidequest_match": "Erlaubt Wasser als stilles Zubereitungsmedium auf Herbal-Seiten, obwohl das Bild nur die Pflanze zeigt.",
        "url": "https://wellcomecollection.org/works/f6nzyzh4",
        "weight": "PRIMARY_RECIPE_MEDIUM_ANALOGUE",
    },
    {
        "source_id": "HARLEY2374",
        "date_place": "15. Jh., England",
        "object": "British Library Harley MS 2374",
        "observed_or_catalogued_mechanism": "Botanisches lateinisch-englisches Glossar, partielles Antidotarium und medizinische Rezepte in einem Mischband.",
        "closest_sidequest_match": "Gelernte Drogennamen/Äquivalente neben produktiver Rezeptgrammatik; starkes f88r-Nomenklator-Analogon.",
        "url": "https://searcharchives.bl.uk/catalog/040-002048205",
        "weight": "PRIMARY_GLOSSARY_ANTIDOTARY_ANALOGUE",
    },
    {
        "source_id": "HARLEY2381",
        "date_place": "Mitte 15. Jh., England",
        "object": "British Library Harley MS 2381",
        "observed_or_catalogued_mechanism": "Kräuterliste, großer Rezeptbestand, Kalender, Mondkalender, Gewichte/Maße, Antidotarium und medizinische Wässer im selben Kompendium.",
        "closest_sidequest_match": "Stärkstes Inhaltsarchitektur-Analogon für Pflanzenmaterial + Zubereitung + Maß + getrennte Himmels-/Zeitsektion.",
        "url": "https://searcharchives.bl.uk/catalog/040-002048212",
        "weight": "PRIMARY_WHOLE_BOOK_ANALOGUE",
    },
    {
        "source_id": "WELLCOME_MS334",
        "date_place": "ca. 1475, Italien",
        "object": "Wellcome MS.334, Herbal",
        "observed_or_catalogued_mechanism": "Pflanzennamen und kurze Anwendungen; grobe Wasserfarben, teils groteske Gesichter an Wurzeln.",
        "closest_sidequest_match": "Später, aber besonders klar für Namen plus kurze Gebrauchsanweisung und bewusst groteske Wurzelbilder.",
        "url": "https://wellcomecollection.org/works/kjxqdfr6",
        "weight": "LATER_SUPPORTING_CONTROL",
    },
    {
        "source_id": "MET_JAR_56_171_88",
        "date_place": "2. Hälfte 15. Jh., Spanien/Valencia",
        "object": "Metropolitan Museum pharmacy jar 56.171.88",
        "observed_or_catalogued_mechanism": "Apotheker mischten zahlreiche verarbeitete Kräuter und Gewürze aus beschrifteten Vorratsgefäßen; Handbücher und Rezeptbücher gehörten zur Dosierpraxis.",
        "closest_sidequest_match": "Stützt f88r als Gefäß-, Zutaten- und Dosierregister, nicht die konkrete Gefäßform oder einen einzelnen Betrieb.",
        "url": "https://www.metmuseum.org/art/collection/search/471753",
        "weight": "MATERIAL_CULTURE_SUPPORT",
    },
]


CROSSWALK = [
    {
        "physical_page": "f10r",
        "visual_mechanism": "überzeichnete Doppel-Speicherwurzel mit getrenntem Blatt/Blütenkopf",
        "closest_historical_source": "LJS419_SCAN0080 + LJS419",
        "historically_natural_workflow": "Arzneiwurzel als Hauptvorrat; Blatt/Blüte als weitere geerntete Teile; kurze Notiz zur Zubereitung um das Bild",
        "revised_concrete_default": "Wurzelansatz zuerst, Blatt- oder Kopfanteil danach",
        "still_unlicensed": "exakte Art, Krankheit und Flüssigkeit",
    },
    {
        "physical_page": "f11r",
        "visual_mechanism": "drei bewurzelte Kronen unter einem Blütensoden",
        "closest_historical_source": "LJS419_SCAN0120",
        "historically_natural_workflow": "Rhizom-/Kronenstock in gebrauchsfähige Teile teilen und als ganzen oder geteilten Simple verarbeiten",
        "revised_concrete_default": "blühenden Stock teilen, Portionen aus den Kronen nehmen",
        "still_unlicensed": "Veilchen als sicherer Name",
    },
    {
        "physical_page": "f13r",
        "visual_mechanism": "große Wurzelkrone plus Blatt plus Blütenstand",
        "closest_historical_source": "LJS419 + SLOANE4016",
        "historically_natural_workflow": "mehrere Arzneiteile einer Simple getrennt sammeln und zubereiten",
        "revised_concrete_default": "Wurzel, Blatt und Blütenstand in mehreren kurzen Teilgängen",
        "still_unlicensed": "Malve, Pestwurz oder andere exakte Art",
    },
    {
        "physical_page": "f55v",
        "visual_mechanism": "großer Wurzelstock, Blattkrone und verzweigte Dolde",
        "closest_historical_source": "LJS419 + SLOANE4016",
        "historically_natural_workflow": "aromatische Wurzel und Dolden-/Samenanteile in unterschiedlichen Portionen einsetzen",
        "revised_concrete_default": "Doldenpflanzen-Wurzelansatz mit Blatt-/Doldenzusatz",
        "still_unlicensed": "Engelwurz, Liebstöckel oder Meisterwurz als sichere Art",
    },
    {
        "physical_page": "f56r",
        "visual_mechanism": "Knospen-, Blüten- und Samenstadien eines stacheligen Kopfes",
        "closest_historical_source": "LJS419 mehrteilige Merkbilder",
        "historically_natural_workflow": "Kopfmaterial nach Sammel-/Reifestufe unterscheiden und getrennt weiterverwenden",
        "revised_concrete_default": "stachelige Köpfe nach Reifestufe portionieren",
        "still_unlicensed": "Distel, Karde oder Carlina als sichere Art",
    },
    {
        "physical_page": "f88r",
        "visual_mechanism": "sechzehn etikettierte Drogenposten, drei Gefäßreihen und drei Arbeitsblöcke",
        "closest_historical_source": "HARLEY2374 + HARLEY2381 + MET_JAR_56_171_88",
        "historically_natural_workflow": "gelernten Drogennamen im Glossar/Vorrat wählen, Menge abnehmen, im Gefäß nach Rezeptkarte verarbeiten",
        "revised_concrete_default": "Drogen-Nomenklator plus produktive Ansatzgrammatik",
        "still_unlicensed": "die sechzehn konkreten Drogennamen",
    },
]


def main() -> None:
    write_tsv(
        "PASS973_HISTORICAL_SOURCES.tsv",
        SOURCES,
        ["source_id", "date_place", "object", "observed_or_catalogued_mechanism", "closest_sidequest_match", "url", "weight"],
    )
    write_tsv(
        "PASS973_SIX_PAGE_HISTORICAL_CROSSWALK.tsv",
        CROSSWALK,
        ["physical_page", "visual_mechanism", "closest_historical_source", "historically_natural_workflow", "revised_concrete_default", "still_unlicensed"],
    )
    report = """# Pass 973 — das nächste echte Werkstatt-Analogon

## Beste Gesamtentsprechung

Der stärkste historische Treffer ist keine einzelne Chiffre und kein einzelnes
Herbal, sondern die **Kreuzung aus drei realen Buchtypen**:

1. ein norditalienisches Bildherbal wie **LJS 419** oder **Sloane 4016**;
2. ein Antidotarium/Rezeptbuch mit Glossar und gelernten Drogennamen wie
   **Harley 2374**;
3. ein praktisches Sammelkompendium mit Kräutern, Rezepten, Maßen, Kalender und
   Mondkalender wie **Harley 2381**.

Das ergibt genau den Mechanismus, den unsere vierzehn Seiten brauchen:

> Das Bild wählt die Simple oder die Station. Ein lokaler Name/Klassencode
> nennt den Posten. Eine kleine produktive Kartenfolge gibt Auswahl, Menge,
> Ansatz, Grad, Ziel und Schluss an. Ein separater Himmelsanhang liefert Zeit-
> oder Klassenauswahl, ohne jedes Rezept auszuschreiben.

## Warum LJS 419 besonders wichtig ist

LJS 419 stammt aus dem Norditalien des 15. Jahrhunderts und vereinigt drei
Bildstile. Einige Pflanzen folgen überlieferten, teils fantastischen Mustern;
andere wurden naturalistischer nachgezeichnet. Die Notizen zu Eigenschaften
und Zubereitungen stehen um oder sogar über den Bildern und wechseln zwischen
Italienisch, Latein und Mischformen.

Vier direkt angesehene Seiten zeigen, wie wenig moderne botanische Anatomie
man verlangen darf:

- Scan 0040 verbindet zwei Pflanzen mit einem fast tierförmigen Wurzelkörper;
- Scan 0080 verlängert eine Wurzel zu einem graphischen Zickzackweg;
- Scan 0120 macht ein Rhizom zu einem wiederholten waagrechten Modul;
- Scan 0160 stellt drei getrennte Pflanzen mit Namen und einem Mondzeichen auf
  eine Seite.

Damit werden die Voynich-Wurzeln nicht identifiziert. Aber f10r, f11r, f13r
und f55v müssen nicht botanisch maßstäbliche Einzelporträts sein, um als
lehrbare Materia-medica-Bilder zu funktionieren.

## Wasser ohne Wasserbild

Wellcome MS.418 enthält Pflanzenwässer, einen vorangestellten Index und
Rezepte, die mit *Recype* beginnen. Das ist die direkte Antwort auf die
Wasserfrage: Ein Pflanzenbild kann eine Wasserzubereitung besitzen, ohne dass
im Bild ein Bach oder Gefäß erscheinen muss. Deshalb bleibt Wasser als Medium
in unseren Herbal-Lesungen offen; es wird nur nicht aus der Pflanzenform
selbst abgeleitet.

## f88r wird historisch verständlich

Harley 2374 verbindet ein lateinisch-englisches Pflanzenglossar mit
Antidotarium und Rezepten. Spätmittelalterliche Apotheken hielten verarbeitete
Bestandteile in Vorratsgefäßen und arbeiteten mit Rezept- und Dosierbüchern.
f88r sieht genau wie eine private Kurzfassung dieses Arbeitsganges aus:
sechzehn sichtbare Drogen, sechzehn gelernte Etiketten, drei Gefäße und drei
produktive Arbeitsblöcke.

## Neue Zwecktheorie

Die derzeit beste konkrete Arbeitstheorie lautet:

**Ein bildadressiertes Werkstattkompendium für Simple, Ansätze, Bäder bzw.
Anwendungsstationen und Himmelswahl.** Es ist näher an einem privaten
Materia-medica-/Antidotarium-/Almanach-Mischbuch als an einem fortlaufenden
Lehrtext. Die Kürzelschicht ist produktiv; seltene Pflanzen- und
Stationsnamen werden als Ganzkarten gelernt.

Diese Theorie sagt mehr als „technisches Register“, aber weniger als eine
erfundene Krankheit pro Seite. Sie erklärt zugleich das Bild zuerst, den Text
in der Restfläche, mehrere Schreiber, f88r-Etiketten und die separaten
Himmelsräder.
"""
    (HERE / "PASS973_HISTORICAL_HERBAL_WORKSHOP_REPORT.md").write_text(report, encoding="utf-8")
    summary = {
        "status": "PASS",
        "historical_sources": len(SOURCES),
        "direct_visual_comparators": sum(r["weight"] == "DIRECT_VISUAL_COMPARATOR" for r in SOURCES),
        "pages_crosswalked": len(CROSSWALK),
        "selected_mechanism": "IMAGE_HERBAL_PLUS_GLOSSARY_ANTIDOTARY_PLUS_CALENDAR_MISCELLANY",
        "strongest_image_analogue": "LJS419",
        "strongest_whole_book_analogue": "HARLEY2381",
    }
    (HERE / "PASS973_BUILD_SUMMARY.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
