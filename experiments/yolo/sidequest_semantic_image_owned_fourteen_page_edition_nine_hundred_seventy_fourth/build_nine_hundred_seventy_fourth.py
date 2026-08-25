#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
P971 = ROOT / "experiments/yolo/sidequest_semantic_canonical_compact_workshop_edition_nine_hundred_seventy_first"
P972 = ROOT / "experiments/yolo/sidequest_semantic_visual_material_owner_revision_nine_hundred_seventy_second"


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(path: Path, rows: list[dict[str, str]], fields: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


MATERIAL = {
    "DIES": "dieser Pflanzen-/Drogenposten",
    "SETZEN": "im Ansatz ansetzen",
    "KURZ": "kurz einwirken lassen",
    "SCHLIESSEN": "Teilansatz abschließen",
    "AUSFÜHREN": "den Arbeitsschritt ausführen",
    "FORTSETZEN": "denselben Ansatz fortführen",
    "LÄNGER": "länger halten oder ziehen lassen",
    "DANACH": "den nächsten Teilgang nehmen",
    "ZIEL": "in das Zielgefäß oder an die Gebrauchsstelle",
    "NEHMEN": "vom bezeichneten Pflanzenteil entnehmen",
    "TEIL": "Wurzel-, Blatt-, Blüten- oder Fruchtteil",
    "HALTEN": "halten, ziehen oder stehen lassen",
    "QUELLE": "aus Wurzelstock oder Vorrat",
    "GEBEN": "dem Ansatz zugeben",
    "SOLLWERT": "die vorgeschriebene Menge",
    "AUSWÄHLEN": "den bezeichneten Drogenposten wählen",
    "UMSETZEN": "in ein anderes Gefäß versetzen",
    "SATZ": "der laufende Ansatz",
    "LEITEN": "gießen, abführen oder durchleiten",
    "EINSTELLEN": "Menge, Dauer oder Stufe einstellen",
    "EINHEIT": "eine Portion",
    "MARKIEREN": "den Teilgang oder Zustand kennzeichnen",
    "EINSETZEN": "den Pflanzenteil einbringen",
    "BEREIT": "gebrauchsfertig",
    "ABSETZEN": "stehen und absetzen lassen",
    "DURCHLASS": "durch Tuch, Sieb oder Auslass",
    "INNEN": "im Gefäß oder inneren Anteil",
    "AUSZUG": "der gewonnene Auszug",
    "ZWEIT": "zweiter Ansatz oder zweite Zugabe",
    "BEGINNEN": "einen neuen Ansatz beginnen",
    "ORT": "die bezeichnete Gefäß-/Gebrauchsstelle",
    "LAUF": "der Flüssigkeitslauf",
    "BEHANDELN": "zerkleinern, wärmen, mischen oder bearbeiten",
    "STUFE": "Ernte-, Reife- oder Arbeitsstufe",
    "STERNORT": "zugeordneter Himmelsplatz",
    "AUFFANGEN": "im Gefäß auffangen",
    "VOLL": "bis zum vollen Grad",
    "SPÜLEN": "mit Arbeitsflüssigkeit spülen",
    "NEBENWEG": "zweiter Auszug oder Nebenweg",
    "UMLEITEN": "in einen anderen Empfänger leiten",
    "TEILSTOFF": "weiterer Pflanzenteil oder Hilfsstoff",
    "ZUSATZ": "ein Zusatz",
    "PRÜFEN": "Farbe, Klarheit oder Zustand prüfen",
    "TRENNEN": "Fraktion oder Pflanzenteil trennen",
    "EINMAL": "einmal oder eine Portion",
    "UNTERSTUFE": "untere/zweite Arbeitsstufe",
    "DAZU": "zum bisherigen Ansatz",
    "RAND": "am Gefäßrand oder äußeren Anteil",
    "RAHMEN": "die abgebildete Materialgruppe",
    "PAAR": "ein Paar oder zwei gleiche Portionen",
    "MITTE": "im Mittelgefäß oder mittleren Anteil",
    "AUSSEN": "äußerlich oder am Außenplatz",
    "BEFESTIGEN": "Auflage oder Einsatz befestigen",
    "VERBINDEN": "Materialien oder Gefäßwege verbinden",
    "ZWISCHEN": "Zwischenfraktion oder Zwischenplatz",
    "WIEDER": "den Gang wiederholen",
}

STATION = {
    "DIES": "dieser Stationsposten", "SETZEN": "an der Station ansetzen",
    "KURZ": "kurz halten", "SCHLIESSEN": "Stationszelle schließen",
    "AUSFÜHREN": "Stationshandlung ausführen", "FORTSETZEN": "im selben Lauf fortfahren",
    "LÄNGER": "länger halten", "DANACH": "zur nächsten Station",
    "ZIEL": "zur Ziel-/Aufnahmestelle", "NEHMEN": "aus Becken oder Vorrat entnehmen",
    "TEIL": "Teilbecken oder Arbeitsanteil", "HALTEN": "an der Station halten",
    "QUELLE": "von Ausgangs-/Entnahmestelle", "GEBEN": "in die Station geben",
    "SOLLWERT": "die vorgeschriebene Stationsmenge", "AUSWÄHLEN": "sichtbare Station wählen",
    "UMSETZEN": "zur nächsten Station versetzen", "SATZ": "laufende Stationskonfiguration",
    "LEITEN": "über den sichtbaren Weg leiten", "EINSTELLEN": "Stufe oder Stellung einstellen",
    "EINHEIT": "eine Stationsfüllung", "MARKIEREN": "Stationszustand markieren",
    "EINSETZEN": "in Becken oder Anschluss einsetzen", "BEREIT": "anwendungsbereit",
    "ABSETZEN": "im Becken absetzen lassen", "DURCHLASS": "durch sichtbaren Anschluss/Durchlass",
    "INNEN": "im inneren Becken", "AUSZUG": "Arbeitsauszug oder laufende Flüssigkeit",
    "ZWEIT": "zweite Station oder zweite Füllung", "BEGINNEN": "neue Stationszelle beginnen",
    "ORT": "sichtbare Station", "LAUF": "lokaler Wasser-/Arbeitslauf",
    "BEHANDELN": "baden, waschen oder technisch bearbeiten", "STUFE": "Stationsstufe",
    "STERNOT": "zugeordneter Himmelsplatz", "AUFFANGEN": "im Empfangsbecken auffangen",
    "VOLL": "vollständig halten/füllen", "SPÜLEN": "Becken oder Körperstelle spülen",
    "NEBENWEG": "Nebenrinne oder Nebenstation", "UMLEITEN": "zum anderen Becken umleiten",
    "TEILSTOFF": "Badezusatz oder Arbeitsstoff", "ZUSATZ": "Zusatz in der Station",
    "PRÜFEN": "sichtbaren Zustand prüfen", "TRENNEN": "Lauf oder Fraktion trennen",
    "EINMAL": "ein Durchgang", "UNTERSTUFE": "untere Station/Stufe",
    "DAZU": "zur aktuellen Station", "RAND": "am Beckenrand",
    "RAHMEN": "die abgebildete Stationsgruppe", "PAAR": "Paarbecken oder Paarposten",
    "MITTE": "Mittelbecken/Mittelstelle", "AUSSEN": "Außenbecken/Außenstelle",
    "BEFESTIGEN": "Auflage oder Einsatz befestigen", "VERBINDEN": "zwei Stationen verbinden",
    "ZWISCHEN": "Zwischenbecken oder Zwischenweg", "WIEDER": "Stationsgang wiederholen",
}

CELESTIAL = {
    "DIES": "dieser Himmels-/Ringposten", "SETZEN": "Posten aktivieren",
    "KURZ": "erster Grad", "SCHLIESSEN": "Eintrag schließen",
    "AUSFÜHREN": "eingetragene Operation ausführen", "FORTSETZEN": "in derselben Reihe fortfahren",
    "LÄNGER": "zweiter/längerer Grad", "DANACH": "nächster Platz",
    "ZIEL": "Zielplatz", "NEHMEN": "Eintrag entnehmen/wählen",
    "TEIL": "Unterplatz", "HALTEN": "Posten festhalten",
    "QUELLE": "Quellplatz", "GEBEN": "Wert zuordnen",
    "SOLLWERT": "eingetragener Wert", "AUSWÄHLEN": "Ring-/Sternplatz wählen",
    "UMSETZEN": "auf anderen Platz übertragen", "SATZ": "Eintragsklasse",
    "LEITEN": "zu verbundenem Platz führen", "EINSTELLEN": "Stellung/Grad einstellen",
    "EINHEIT": "eine Tabellen- oder Ringzelle", "MARKIEREN": "Platz kennzeichnen",
    "EINSETZEN": "in Ring/Tabelle eintragen", "BEREIT": "gültiger/freigegebener Eintrag",
    "ABSETZEN": "Eintrag ablegen", "DURCHLASS": "formale Verbindung",
    "INNEN": "Innenring/-platz", "AUSZUG": "lokale Eintragsklasse",
    "ZWEIT": "zweiter Ring/zweite Stufe", "BEGINNEN": "neue Reihe beginnen",
    "ORT": "lokale Adresse", "LAUF": "Ringlauf",
    "BEHANDELN": "eingetragene Regel anwenden", "STUFE": "Grad/Stufe",
    "STERNOT": "Sternstelle", "AUFFANGEN": "Ergebnisplatz",
    "VOLL": "voller Grad", "SPÜLEN": "Reihe durchlaufen",
    "NEBENWEG": "Nebenring/-zweig", "UMLEITEN": "auf Alternativplatz führen",
    "TEILSTOFF": "Unterklasse", "ZUSATZ": "Zusatzmarke",
    "PRÜFEN": "Platz/Regel prüfen", "TRENNEN": "Klasse oder Ring trennen",
    "EINMAL": "ein Platz/ein Umlauf", "UNTERSTUFE": "Untergrad",
    "DAZU": "zugeordnet", "RAND": "Außenrand",
    "RAHMEN": "Diagrammrahmen", "PAAR": "Paarposten",
    "MITTE": "Mittelpunkt/Mittelplatz", "AUSSEN": "Außenring/-platz",
    "BEFESTIGEN": "Marke fixieren", "VERBINDEN": "Plätze verbinden",
    "ZWISCHEN": "Zwischenplatz", "WIEDER": "Platzfolge wiederholen",
}


PAGE_READING = {
    "f10r": ("zweiknolliges blauköpfiges Heilkraut", "Wurzelansatz, danach Blatt-/Kopfanteil", "Nimm vom doppelten roten Speicherwurzelstock und setze daraus den ersten Ansatz. Halte und bearbeite ihn bis zum geschlossenen Gebrauchszustand. Nimm danach Blatt oder blauen Kopf nach Sollmaß, gib ihn zu und führe den zweiten, noch offenen Ansatz weiter."),
    "f11r": ("blühender dreikroniger Sodenstock", "Kronen teilen und portionsweise ansetzen", "Halte den blühenden Soden zusammen, teile ihn in drei bewurzelte Kronen und nimm von jeder die vorgeschriebene Portion. Gib die Teile in den Ansatz, arbeite sie weiter und trenne oder leite den letzten Zug ab; die Fortsetzung bleibt offen."),
    "f13r": ("große Wurzelkrone mit Blatt und Blütenstand", "drei Pflanzenteile in kurzen Teilgängen", "Bereite zuerst den Ansatz aus der großen Wurzelkrone. Setze Blatt und Blütenstand als getrennte Posten nach Sollmaß ein, halte und leite sie durch vier kurze geschlossene Arbeitsschritte; der letzte Zusatz bleibt offen."),
    "f55v": ("große aromatische Doldenpflanze", "Wurzelstock, Blattkrone und Dolde", "Setze die Wurzelzubereitung der großen Doldenpflanze an. Gib Blatt- und Doldenanteile in notierten Portionen zu, versetze den Ansatz zwischen Gefäßstellen, entnimm Proben und führe einen Anteil durch den Durchlass. Vier Teilgänge schließen; der lange Hauptansatz bleibt offen."),
    "f56r": ("stachelköpfiges Kraut in mehreren Reifestufen", "Knospe, Blüte und reifer Kopf getrennt", "Nimm vom stacheligen Kopf in der bezeichneten Reifestufe kleine Anteile und setze sie getrennt an. Gib Knospen-, Blüten- und reife Kopfanteile nacheinander zu, halte oder prüfe jeden Zug und führe den letzten Posten zur nächsten Verwendung."),
    "f88r": ("sechzehn Drogenposten und drei Gefäßansätze", "etikettierte Zutaten auswählen und rowweise verarbeiten", "Obere, mittlere und untere Reihe bilden je einen Gefäßansatz. Wähle das etikettierte Wurzel-, Blatt-, Frucht- oder Kronenmaterial, nimm die Sollmenge, setze den Ansatz, gib weitere Teile zu, halte oder leite den Auszug und schließe den Teilgang. Die Etiketten sind gelernte Drogennamen oder Klassencodes."),
    "f75r": ("großes Bad-/Stationsblatt mit dreieckiger Insel", "Figuren-, Becken- und Rinnenstationen zellenweise bedienen", "Arbeite jede sichtbare Figur-, Becken- oder Rinnenstation für sich ab: Posten einsetzen, kurz oder länger halten, über den lokalen Anschluss umsetzen, am Ziel neu ansetzen und die Zelle schließen. Die sieben Zeilen an der dreieckigen Insel gehören zu diesem einen lokalen Besitzer, nicht zu einem globalen Wasserkreislauf."),
    "f81v": ("gemeinsames zweireihiges Badfeld", "Badeposten halten, umsetzen und absetzen", "Setze den jeweiligen Badeposten im gemeinsamen Feld an, gib die bezeichnete Menge zu und halte ihn für die notierte Stufe. Führe ihn danach über den nächsten lokalen Lauf, setze ihn neu an und lass einzelne Züge im Becken absetzen."),
    "f82r": ("mehrere getrennte Bad- und Leitungsstationen", "lokale Station wählen; keine Gesamtmaschine", "Wähle an jeder Vignette den aktiven Posten, setze ihn an und führe ihn nur über den tatsächlich gezeichneten Anschluss weiter. Wiederhole Zugabe, Halten und Umsetzen nach der örtlichen Station; fange einzelne Ausgänge auf. Zwischen unverbundenen Bildern beginnt ein neuer Besitzer."),
    "f83r": ("Variantenatlas lokaler Becken und Anwendungen", "Anwendungsvarianten statt ein Kreislauf", "Lies jede kurze Gruppe als Variante: auswählen, ansetzen, halten, an die sichtbare Stelle umsetzen, dort neu ansetzen und absetzen oder auffangen. Reale Paarverbindungen gelten lokal; ein geschlossener Gesamtumlauf ist nicht gezeichnet."),
    "f67r2": ("zwei getrennte Himmelsräder und Tabelle", "Ring-/Tabellenposten auswählen", "Wähle einen Posten im jeweiligen Rad oder in der Tabelle, stelle seinen Grad oder Wert ein und führe die dort eingetragene Operation aus. Die beiden Räder bleiben eigene Adressräume; aus ihnen entsteht kein erzwungenes 7-mal-12-Schema."),
    "f68r1": ("mehrteilige Sternstellentafel", "räumliche Sternadressen ohne Umlaufrichtung", "Wähle die bezeichnete Sternstelle, entnimm ihren lokalen Eintrag und ordne ihm Wert, Grad oder Operation zu. Die Paneele besitzen mehrere lokale Zentren; eine feste Startstelle, Richtung oder Verbindung zu f69v ist nicht sichtbar."),
    "f69v": ("drei getrennte Himmelsräder", "linke 28 Plätze plus zwei eigene Verzeichnisse", "Das linke Rad bietet achtundzwanzig lokale Plätze; die beiden anderen Räder besitzen eigene Klassen und Einträge. Wähle und kennzeichne Plätze innerhalb ihres jeweiligen Rads. Lies sie nicht als eine lineare achtundzwanzigschrittige Rezeptfolge."),
    "f70v": ("Widder- und Fischring", "zwei Tierkreis-Adressregister", "Im Widderring werden Reihe, Klasse, Platz und Grad gewählt; AIR bedeutet hier Ringlauf. Im Fischring werden Plätze und Unterplätze des Fischpaars mit Grad oder Wert versehen. Beide Paneele sind Himmelsadressen, keine Flüssigkeitsrezeptur."),
}


BOOK_FLOW = [
    {"stage": "I_STOFF", "question": "WAS?", "pages": "f10r|f11r|f13r|f55v|f56r", "workshop_action": "Simple und sichtbaren Arzneiteil wählen; sammeln, teilen und als Vorrat/Ansatz vorbereiten.", "spoken_apprentice_rule": "Zeige zuerst auf Wurzel, Krone, Blatt, Blüte oder Kopf; dann lies die Karten."},
    {"stage": "II_ZUBEREITUNG", "question": "WIE HERSTELLEN?", "pages": "f88r", "workshop_action": "Gelernten Drogenposten wählen, Menge nehmen, in einem der Gefäße ansetzen und Auszug führen.", "spoken_apprentice_rule": "Etikett lernen; Rezeptkarten zusammensetzen; Teilgang schließen."},
    {"stage": "III_ANWENDUNG", "question": "WIE/WO ANWENDEN?", "pages": "f75r|f81v|f82r|f83r", "workshop_action": "Bade-, Wasch-, Auflage- oder Stationsposten lokal einsetzen, halten, umsetzen, auffangen oder absetzen.", "spoken_apprentice_rule": "Nur gezeichnete Verbindungen verfolgen; bei neuem Bildbesitzer neu beginnen."},
    {"stage": "IV_ZEIT_UND_AUSWAHL", "question": "WANN/WELCHE KLASSE?", "pages": "f67r2|f68r1|f69v|f70v1|f70v2", "workshop_action": "Himmelsplatz, Reihe, Grad oder Wert im passenden Diagramm nachschlagen.", "spoken_apprentice_rule": "Jedes Rad behält seinen eigenen Namensraum; keine Richtung erfinden."},
]


def expand(value: str, mapping: dict[str, str]) -> str:
    return " · ".join(mapping.get(part.strip(), part.strip().lower()) for part in value.split("·"))


def main() -> None:
    dictionary = read(P971 / "PASS971_86_ENTRY_DICTIONARY.tsv")
    expanded = []
    for row in dictionary:
        value = row["portable_value_de"]
        expanded.append({
            **row,
            "material_workshop_expansion_de": expand(value, MATERIAL),
            "station_workshop_expansion_de": expand(value, STATION),
            "celestial_lookup_expansion_de": expand(value, CELESTIAL),
        })
    write(
        HERE / "PASS974_86_ENTRY_REGISTER_EXPANSIONS.tsv",
        expanded,
        list(expanded[0]),
    )

    old_pages = {r["physical_page"]: r for r in read(P971 / "PASS971_14_PAGE_EDITION.tsv")}
    page_rows = []
    for page, old in old_pages.items():
        owner, workflow, fluent = PAGE_READING[page]
        page_rows.append({
            "physical_page": page,
            "book_stage": old["book_stage"],
            "unit_role_de": old["unit_role_de"],
            "events": old["events"],
            "prose_clauses": old["prose_clauses"],
            "local_address_events": old["local_address_events"],
            "visible_owner_or_namespace_de": owner,
            "concrete_workflow_de": workflow,
            "complete_working_reading_de": fluent,
            "portable_dictionary_status": "UNCHANGED_86_ENTRIES",
        })
    write(HERE / "PASS974_14_PAGE_IMAGE_OWNED_EDITION.tsv", page_rows, list(page_rows[0]))
    write(HERE / "PASS974_FOUR_STAGE_BOOK_FLOW.tsv", BOOK_FLOW, list(BOOK_FLOW[0]))

    lines = [
        "# Pass 974 — vollständige bildbesessene Vierzehn-Seiten-Ausgabe",
        "",
        "## Das Buch in einem Satz",
        "",
        "> Wähle am Bild Simple, Teil, Gefäß, Station oder Himmelsplatz; nimm die",
        "> angegebene Einheit, setze den Gang, halte ihn im notierten Grad, leite",
        "> ihn zur Zielstelle und schließe die Zelle.",
        "",
        "Die 86 Karten bleiben unverändert. Neu ist, dass jede Karte je nach",
        "sichtbarem Besitzer eine konkrete Material-, Stations- oder",
        "Himmelslesung erhält.",
        "",
    ]
    for stage in BOOK_FLOW:
        lines += [f"## {stage['stage']} — {stage['question']}", "", stage["workshop_action"], ""]
        pages = [p for p in page_rows if p["book_stage"] == stage["stage"]]
        for row in pages:
            lines += [f"### {row['physical_page']} — {row['visible_owner_or_namespace_de']}", "", row["complete_working_reading_de"], ""]
    lines += [
        "## Beste gegenwärtige Zwecklesung",
        "",
        "Die vier Stufen ergeben ein privates, bildadressiertes",
        "Materia-medica-/Antidotarium-/Bade-/Almanach-Werkstattbuch:",
        "**Stoff wählen → Ansatz herstellen → lokal anwenden/führen → Zeitpunkt",
        "oder Himmelsklasse nachschlagen.** Ein allgemeines Material-/Prozess-/",
        "Kalender-Musterbuch bleibt als einfachere Nebenlesung möglich; es benötigt",
        "aber dieselbe Kartenmaschine.",
        "",
    ]
    (HERE / "PASS974_COMPLETE_FOURTEEN_PAGE_READING.md").write_text("\n".join(lines), encoding="utf-8")
    summary = {
        "status": "PASS",
        "dictionary_entries": len(expanded),
        "pages": len(page_rows),
        "events": sum(int(r["events"]) for r in page_rows),
        "prose_clauses": sum(int(r["prose_clauses"]) for r in page_rows),
        "local_address_events": sum(int(r["local_address_events"]) for r in page_rows),
        "book_stages": len(BOOK_FLOW),
        "dictionary_values_changed": 0,
    }
    (HERE / "PASS974_BUILD_SUMMARY.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
