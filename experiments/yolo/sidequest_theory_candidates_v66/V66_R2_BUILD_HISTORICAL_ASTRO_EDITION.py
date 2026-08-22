#!/usr/bin/env python3
"""Build the V66 R2 local-exemplar Astro edition.

The page-bearing V22 ledger is materialised only through the guarded
``vmanus-exp query-tsv`` interface.  German text is locus-local editorial
content, never a portable reading of a ZL3b group.
"""

from __future__ import annotations

import csv
import io
import json
import subprocess
from collections import Counter, defaultdict
from pathlib import Path


OUT = Path(__file__).resolve().parent
ROOT = Path(__file__).resolve().parents[3]
SOURCE = ROOT / "experiments/yolo/sidequest_theory_candidates_v22/V22_SELECTED_COMPLETE_TRANSLATION_LEDGER.tsv"
RULE_SOURCE = ROOT / "experiments/yolo/sidequest_theory_candidates_v22/V22_F69_28_RULES.tsv"
PAGES = ("f67r2", "f68r1", "f69v")


def guarded_rows() -> list[dict[str, str]]:
    columns = [
        "page", "locus", "record", "line", "event_index", "surface",
        "exact_tuple_id", "source_event_serial",
    ]
    command = [str(ROOT / "vmanus-exp"), "query-tsv", str(SOURCE), "--selector", "page"]
    for page in PAGES:
        command.extend(("--allow", page))
    command.extend(("--columns", ",".join(columns), "--forbid-prefix", "f84"))
    proc = subprocess.run(command, cwd=ROOT, check=True, text=True, capture_output=True)
    rows = list(csv.DictReader(io.StringIO(proc.stdout), delimiter="\t"))
    rows.sort(key=lambda row: int(row["source_event_serial"]))
    assert len(rows) == 395
    assert {row["page"] for row in rows} == set(PAGES)
    assert not any(row["page"].startswith("f84") for row in rows)
    return rows


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: list[dict[str, object]], fields: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def locus_number(locus: str) -> int:
    return int(locus.rsplit(".", 1)[1])


def split_fragments(text: str, count: int) -> list[str]:
    words = text.split()
    assert len(words) >= count, (count, text)
    base, remainder = divmod(len(words), count)
    result: list[str] = []
    cursor = 0
    for index in range(count):
        width = base + (1 if index < remainder else 0)
        result.append(" ".join(words[cursor:cursor + width]))
        cursor += width
    assert cursor == len(words)
    return result


ZODIAC = [
    ("Widder", "Kopf und Gesicht"),
    ("Stier", "Hals und Kehle"),
    ("Zwillinge", "Schultern, Arme und Hände"),
    ("Krebs", "Brust und Brüste"),
    ("Löwe", "Herz und oberer Rücken"),
    ("Jungfrau", "Bauch und Eingeweide"),
    ("Waage", "Lenden und Nieren"),
    ("Skorpion", "Genitalien und Blase"),
    ("Schütze", "Hüften und Oberschenkel"),
    ("Steinbock", "Knie"),
    ("Wassermann", "Schienbeine und Knöchel"),
    ("Fische", "Füße"),
]

PLANETS = {
    15: ("Saturn", "kalt und trocken"),
    22: ("Jupiter", "warm und feucht"),
    28: ("Mars", "heiß und trocken"),
    31: ("Sonne", "warm und trocken"),
    34: ("Venus", "kühl und feucht"),
    37: ("Merkur", "wechselnd nach Verbindung"),
    47: ("Mond", "kalt und feucht"),
}

HOUSES = [
    "Haus I: Kranker und Körper",
    "Haus II: Mittel und Vorrat",
    "Haus III: Nachricht und kurzer Weg",
    "Haus IV: Grund und Ausgang",
    "Haus V: Kinder und Zeugung",
    "Haus VI: Krankheit und Leiden",
    "Haus VII: Arzt oder Gegenpartei",
    "Haus VIII: Krise und Tod",
    "Haus IX: Lehre und ferner Weg",
    "Haus X: Behandlung und leitender Meister",
    "Haus XI: Helfer und Hoffnung",
    "Haus XII: verborgene Gefahr und Einschließung",
]

CONDITIONS = [
    "Bedingung I: Der Mond sei frei von Saturn; andernfalls verschieben.",
    "Bedingung II: Der Mond sei frei von Mars; andernfalls nur mild handeln.",
    "Bedingung III: Der Mond sei nicht von der Sonne verbrannt.",
    "Bedingung IV: Der Mond trenne sich vom Übeltäter.",
    "Bedingung V: Der Mond wende sich einem Wohltäter zu.",
    "Bedingung VI: Trigon oder Sextil gelten als günstige Verbindung.",
    "Bedingung VII: Tages- oder Nachtzeichen müsse zur Arbeitszeit passen.",
    "Bedingung VIII: Bei unsicherem Stand werde die Maßnahme verschoben.",
]

SELECTOR_TEXT = {
    13: "Bestimme zuerst den Tag und danach die planetarische Stunde der vorgesehenen Maßnahme.",
    14: "Nenne den Kranken, seine Stärke und die sichtbar betroffene Körperstelle.",
    16: "Suche den Herrscher aus der Siebenerreihe und bewahre seine Grundqualität.",
    17: "Unterscheide warme, kalte, trockene und feuchte Wirkung nur als Exemplarregel.",
    18: "Bestimme das Zeichen, in dem der Mond zur fraglichen Stunde steht.",
    19: "Ordne dem Zeichen den Körperbezirk aus der Zwölferreihe zu.",
    20: "Ist gerade dieser Körperbezirk betroffen, so schone ihn in dieser Stunde.",
    21: "Verschiebe Aderlass, Schröpfen oder Schnitt am beherrschten Körperbezirk.",
    23: "Prüfe zusätzlich, ob der Mond an Licht zunimmt oder abnimmt.",
    24: "Zunehmendes Licht begünstigt stärkende, abnehmendes Licht entleerende Maßnahmen im Exemplar.",
    25: "Prüfe nun die schädlichen Verbindungen von Saturn und Mars.",
    26: "Bei schädlichem Aspekt verschiebe den starken Eingriff und wähle Schonung.",
    27: "Bei Sonnenverbrennung des Mondes halte die beabsichtigte Maßnahme zurück.",
    29: "Bei guter Verbindung eines Wohltäters darf eine milde Behandlung erfolgen.",
    30: "Wähle die Anwendung nach Krankheit, Kräften und sichtbarer Körperstelle.",
    32: "Bei Fülle kann das lokale Exemplar Aderlass oder Schröpfen erwägen.",
    33: "Bei Schwäche meide starke Entleerung und vermindere das gewöhnliche Maß.",
    35: "Für Bad und Salbung wähle nur eine gemäßigte Wärme.",
    36: "Für Trank und Arznei wahre das im Rezept vorgeschriebene Maß.",
    38: "Am Kopf handle nicht stark, solange der Mond im Widder steht.",
    39: "An Hals und Kehle handle nicht stark, solange der Mond im Stier steht.",
    40: "An Armen und Händen handle nicht stark bei Mond in den Zwillingen.",
    41: "An Brust und Brüsten handle nicht stark bei Mond im Krebs.",
    42: "An Herz und oberem Rücken handle nicht stark bei Mond im Löwen.",
    43: "An Bauch und Eingeweiden handle nicht stark bei Mond in der Jungfrau.",
    44: "An Lenden und Nieren handle nicht stark bei Mond in der Waage.",
    45: "An Genitalien und Blase handle nicht stark bei Mond im Skorpion.",
    46: "An Hüften und Schenkeln handle nicht stark bei Mond im Schützen.",
    48: "An den Knien handle nicht stark bei Mond im Steinbock.",
    49: "An Schienbeinen und Knöcheln handle nicht stark bei Mond im Wassermann.",
    50: "An den Füßen handle nicht stark bei Mond in den Fischen.",
    51: "Wenn Zeichen oder Körperbezirk unsicher bleibt, verschiebe die Maßnahme.",
    72: "Merke: Der Planet ist der Herr des Tages oder der Stunde; das Zeichen bezeichnet den geschonten Körperbezirk; das Haus bezeichnet die gestellte Frage; der Zustand des Mondes entscheidet, ob jetzt gehandelt, gemildert oder verschoben wird.",
    73: "Die Namen und medizinischen Zuordnungen dieser Ausgabe stammen aus einem äußeren zeitgenössischen Exemplar. Kein sichtbares Gebilde wird dadurch zum lateinischen oder deutschen Wort, und der gezeichnete Anfang bleibt unbekannt.",
    74: "Diese Tafel nennt weder Krankheit noch Arznei des einzelnen Kranken. Der Arzt bringt Diagnose, Rezept, Dosis und Eingriff aus seinem Fall oder Buch mit und benutzt das Diagramm nur als Wahlfilter.",
}

F68_INTRO = {
    1: "Tafel der achtundzwanzig Häuser des Mondes: Der Kreis ist hier ein räumlicher Namenskatalog und noch kein bewiesener Lauf oder Kalender.",
    2: "Jede gezeichnete Sternstelle bewahrt einen eigenen lokalen Namen; der Benutzer findet sie nach Lage und nach einem außerhalb dieser Seite erlernten Himmelsort.",
    3: "Für die vollständige Vergleichsausgabe setzt der Herausgeber Haus eins an Quelllocus neun und zählt bis Quelllocus sechsunddreißig; weder dieser Anfang noch diese Richtung ist im Blatt bewiesen.",
    4: "Die Namen Alnat bis Arexe stammen aus einem lateinischen Picatrix-Vergleich und lesen kein Voynich-Gebilde.",
    5: "Der Benutzer bringt den Mondort aus Kalender oder Beobachtung mit.",
    6: "Er wählt danach genau eine gezeichnete Sternstelle.",
    7: "Ihre Wirkung wird in einem getrennten Regeltext nachgeschlagen.",
}

MANSIONS = [
    ("Alnat", "Arznei einnehmen oder Reise beginnen"),
    ("Albatain", "Wasserlauf, Brunnen oder Saat"),
    ("Alcorata", "Seefahrt, Feuerarbeit oder Jagd"),
    ("Aldebatam", "Bauten, Quellen oder Trennung"),
    ("Altintas", "Lernen, Reise oder Bau verbessern"),
    ("Achaia", "Ernte oder Arzneiwirkung hemmen"),
    ("Aldira", "Handel, Ernte oder sichere Schifffahrt"),
    ("Anathea", "Freundschaft, Reise oder Verwahrung"),
    ("Atraff", "Streit, Schaden oder Abwehr"),
    ("Algebhal", "Ehe, Gebäude oder Beistand"),
    ("Ozobea", "Befreiung, Handel oder festen Bau"),
    ("Acarfa", "Pflanzen, Besitz oder Schifffahrt"),
    ("Alahuc", "Handel, Saat, Reise oder Bau"),
    ("Acimech", "Kranke heilen, Reise oder Freundschaft"),
    ("Algafra", "Brunnen, Schatzsuche oder Trennung"),
    ("Aculine", "Befreiung oder Zwietracht"),
    ("Alichil", "dauerhafte Freundschaft, Bau oder Schifffahrt"),
    ("Alcalb", "Bau, Befreiung oder Streit"),
    ("Exaula", "Krieg, Ernte, Reise oder Gefangenschaft"),
    ("Nahaym", "Tiere zähmen, Rückkehr oder Versammlung"),
    ("Elbelda", "Bau, Ernte, Reise oder Trennung"),
    ("Cadaldeba", "Krankheit heilen oder Gefangene lösen"),
    ("Cacidebehah", "Krankheit heilen oder Gefangene lösen"),
    ("Zazedahot", "Handel, Ehe oder Sieg"),
    ("Cadalhacia", "Körperglied binden, Streit oder Bau"),
    ("Almiquidam", "Liebe, Reise oder festen Bau"),
    ("Algrafaium", "Krankheit heilen, Handel oder Gefahr"),
    ("Arexe", "Ernte, Reise, Frieden oder Gefangenschaft"),
]

F69_RUBRICS = {
    1: "Rubrik der achtundzwanzig Wahlstellen. Nimm zuerst den bekannten Mondort oder die im Kalender gelernte laufende Stelle. Prüfe dann die Kräfte des Kranken, die Art des Eingriffs und den beherrschten Körperbezirk. Eine günstige Stelle erlaubt nur die im Rezept bereits bestimmte Maßnahme; sie erfindet weder Krankheit noch Arznei.",
    2: "Bei schädlichem Mondstand, Verbindung mit Saturn oder Mars oder Beherrschung des betroffenen Körperteils werde ein starker Eingriff verschoben. Bei unsicherem Anfang des Kreises benutze die lokal gelernte Reihenfolge des Exemplars und übertrage niemals bloß dieselbe moderne Nummer aus einer anderen Tafel.",
    3: "Die folgenden kurzen Regeln nennen Bad, Waschung, Salbung, Ruhe, Maß oder Aderlass nur als konkrete Editionsfassung. Gleiche vollständige Einträge behalten dieselbe lokale Regel; langer und kurzer Schreibraum trägt keine günstige oder ungünstige Polarität.",
}

F69_RULES_DE = [
    "Warmes Bad ist erlaubt, besonders nach Sonnenuntergang.",
    "Verwende eine kühle Waschung und beende danach.",
    "Meide den Aderlass.",
    "Eine Salbung ist erlaubt.",
    "Wende das Mittel an der oberen Körperhälfte an.",
    "Lass den Kranken ruhen und purgiere nicht.",
    "Vollende genau eine Spülung.",
    "Leite überschüssige Flüssigkeit ab.",
    "Meide ein heißes Bad.",
    "Wende das Mittel unterhalb der Taille an.",
    "Die Stelle ist für ein Bad günstig.",
    "Wiederhole die Waschung genau einmal.",
    "Verwende denselben bereiteten Ansatz.",
    "Bade, bis die Wärme sanft ist.",
    "Die Stelle ist für ein Bad günstig.",
    "Salbe die betroffene Stelle.",
    "Halte den Kranken in Ruhe.",
    "Verwende ein kleineres Maß.",
    "Spüle und beende die Anwendung.",
    "Meide eine zweite Anwendung.",
    "Verwende das getrocknete Kraut.",
    "Ein warmes Bad ist erlaubt; danach beenden.",
    "Bereite das gewöhnliche Bad unter der gesetzten Grenze.",
    "Die Stelle ist für ein Bad günstig.",
    "Seihe den Kräutertrank.",
    "Gieße auf und beende die Anwendung.",
    "Lege ein warmes Tuch auf.",
    "Prüfe das Mondhaus; bei Schwäche halte die Behandlung zurück.",
]


def locus_content(page: str, number: int) -> dict[str, str]:
    common = {
        "external_label_status": "NONE",
        "f68_f69_mapping": "NONE",
    }
    if page == "f67r2":
        rotation = "EDITORIAL_SOURCE_LOCUS_ORDER; AUTHORIAL_START_AND_DIRECTION_UNPROVEN"
        if 1 <= number <= 12:
            sign, body = ZODIAC[number - 1]
            return common | {
                "role": "ZODIAC_BODY_SECTOR_LOCAL_EXEMPLAR",
                "inventory_item": f"Z{number:02d}",
                "text": f"Externer Editionswert Zeichen {number}: {sign}; Körperbezirk: {body}; bei Mond in diesem Zeichen den Bezirk schonen und dort keinen starken Eingriff vornehmen.",
                "external_label_status": "EXTERNAL_LOCAL_EXEMPLAR_LABEL_NOT_VOYNICH_READING",
                "historical_basis": "S1|S2|S3|S4",
                "strongest_rival": "Zwölfteilige astronomische Lehrliste ohne Körperzuordnung",
                "rotation": rotation,
                "confidence": "0.46",
            }
        if number in PLANETS:
            planet, quality = PLANETS[number]
            index = list(PLANETS).index(number) + 1
            return common | {
                "role": "SEVEN_PLANET_LOCAL_EXEMPLAR",
                "inventory_item": f"P{index:02d}",
                "text": f"Externer Editionswert Planet {index}: {planet}; überlieferte Grundqualität: {quality}; als Tages- oder Stundenherr prüfen.",
                "external_label_status": "EXTERNAL_LOCAL_EXEMPLAR_LABEL_NOT_VOYNICH_READING",
                "historical_basis": "S1|S2|S4|S8",
                "strongest_rival": "Siebenerliste von Wochentagen oder bloßen Himmelskörpern",
                "rotation": rotation,
                "confidence": "0.44",
            }
        if 52 <= number <= 63:
            index = number - 51
            return common | {
                "role": "TWELVE_HOUSE_CONTROL_LOCAL_EXEMPLAR",
                "inventory_item": f"H{index:02d}",
                "text": f"Externer Editionswert {HOUSES[index - 1]}; das Haus rahmt die Frage, nicht die Voynich-Oberfläche.",
                "external_label_status": "EXTERNAL_LOCAL_EXEMPLAR_LABEL_NOT_VOYNICH_READING",
                "historical_basis": "S1|S4|S8",
                "strongest_rival": "Zweite Zeichenreihe oder unabhängiges Zwölferinventar",
                "rotation": rotation,
                "confidence": "0.31",
            }
        if 64 <= number <= 71:
            index = number - 63
            return common | {
                "role": "EIGHT_ELECTION_CONDITION_LOCAL_EXEMPLAR",
                "inventory_item": f"C{index:02d}",
                "text": CONDITIONS[index - 1],
                "external_label_status": "EXTERNAL_LOCAL_EXEMPLAR_CONDITION_NOT_VOYNICH_READING",
                "historical_basis": "S5|S8",
                "strongest_rival": "Acht grafische Sektoren ohne astrologische Bedingung",
                "rotation": rotation,
                "confidence": "0.30",
            }
        return common | {
            "role": "SELECTOR_INSTRUCTION_LOCAL_SOURCE_TEXT",
            "inventory_item": f"I{number:02d}",
            "text": SELECTOR_TEXT[number],
            "historical_basis": "S1|S2|S3|S4|S8",
            "strongest_rival": "Allgemeine astronomische Lehrprosa ohne medizinische Wahlfunktion",
            "rotation": rotation,
            "confidence": "0.36",
        }

    if page == "f68r1":
        rotation = "EDITORIAL_S01_EQUALS_SOURCE_LOCUS_9; AUTHORIAL_START_AND_DIRECTION_UNPROVEN"
        if 1 <= number <= 7:
            return common | {
                "role": "SPATIAL_CATALOGUE_INSTRUCTION_LOCAL_SOURCE_TEXT",
                "inventory_item": f"R{number:02d}",
                "text": F68_INTRO[number],
                "historical_basis": "S5|S6",
                "strongest_rival": "Sternnamenskatalog oder Gedächtnisbild ohne Mondhäuser",
                "rotation": rotation,
                "confidence": "0.34",
            }
        if number == 8:
            return common | {
                "role": "CENTRAL_LUNAR_CATALOGUE_OWNER",
                "inventory_item": "CENTRE",
                "text": "Der Mond als externer Editionsbesitzer eines Katalogs aus achtundzwanzig Häusern; kein Wortwert der Oberfläche.",
                "external_label_status": "EXTERNAL_LOCAL_EXEMPLAR_LABEL_NOT_VOYNICH_READING",
                "historical_basis": "S5|S6",
                "strongest_rival": "Beliebiger Zentralstern oder Instrumenttitel",
                "rotation": rotation,
                "confidence": "0.49",
            }
        if 9 <= number <= 36:
            index = number - 8
            name, operation = MANSIONS[index - 1]
            return common | {
                "role": "SPATIAL_LUNAR_MANSION_LOCAL_EXEMPLAR",
                "inventory_item": f"S{index:02d}",
                "text": f"Räumliche Stelle S{index:02d}; externer Picatrix-Vergleichsname: {name}; dort überlieferte Operationsklasse: {operation}.",
                "external_label_status": "EXTERNAL_LOCAL_EXEMPLAR_LABEL_NOT_VOYNICH_READING",
                "historical_basis": "S5",
                "strongest_rival": "Unbenannte Sternadresse ohne feste Wirkung",
                "rotation": rotation,
                "confidence": "0.30",
            }
        assert number == 37
        return common | {
            "role": "CENTRAL_CATALOGUE_LEGEND_LOCAL_SOURCE_TEXT",
            "inventory_item": "CENTRE_LEGEND",
            "text": "Der Mond besitzt in dieser lokalen Editionswelt einen vollständigen Kreis aus achtundzwanzig räumlichen Häusern.",
            "historical_basis": "S5|S6",
            "strongest_rival": "Zentrale Legende eines allgemeinen Sternverzeichnisses",
            "rotation": rotation,
            "confidence": "0.38",
        }

    assert page == "f69v"
    rotation = "TRANSCRIPTION_R01_EQUALS_SOURCE_LOCUS_4; AUTHORIAL_START_AND_DIRECTION_UNPROVEN"
    if 1 <= number <= 3:
        return common | {
            "role": "ORDERED_RULE_CIRCULAR_RUBRIC_LOCAL_SOURCE_TEXT",
            "inventory_item": f"RUBRIC{number}",
            "text": F69_RUBRICS[number],
            "historical_basis": "S1|S2|S4|S5|S7|S8",
            "strongest_rival": "Allgemeine Kalender-, Los- oder Arbeitsregel ohne Medizin",
            "rotation": rotation,
            "confidence": "0.32",
        }
    index = number - 3
    return common | {
        "role": "INDEPENDENT_28_ELECTION_RULE_LOCAL_SOURCE_TEXT",
        "inventory_item": f"E{index:02d}",
        "text": F69_RULES_DE[index - 1],
        "historical_basis": "S1|S2|S4|S5|S8",
        "strongest_rival": "Nichtmedizinische Mondhausoperation oder technischer Arbeitstermin",
        "rotation": rotation,
        "confidence": "0.29",
    }


def main() -> None:
    source_rows = guarded_rows()
    source_rules = read_tsv(RULE_SOURCE)
    assert len(source_rules) == 28
    by_locus: dict[tuple[str, str], list[dict[str, str]]] = defaultdict(list)
    for row in source_rows:
        by_locus[(row["page"], row["locus"])].append(row)

    group_rows: list[dict[str, object]] = []
    locus_rows: list[dict[str, object]] = []
    for (page, locus), events in by_locus.items():
        events.sort(key=lambda row: int(row["event_index"]))
        number = locus_number(locus)
        content = locus_content(page, number)
        fragments = split_fragments(content["text"], len(events))
        surface_sequence = " ".join(row["surface"] for row in events)
        for position, (event, fragment) in enumerate(zip(events, fragments), 1):
            group_rows.append({
                "group_serial": len(group_rows) + 1,
                "page": page,
                "locus": locus,
                "event_index": event["event_index"],
                "source_event_serial": event["source_event_serial"],
                "surface_ZL3b": event["surface"],
                "locus_role": content["role"],
                "inventory_item": content["inventory_item"],
                "default_content_German": f"[LOKALER EXEMPLARTEXT {position}/{len(events)}; KEINE KARTENGLOSSE] {fragment}",
                "content_status": "LOCAL_EXEMPLAR_SEGMENT_NOT_PORTABLE_CARD_VALUE",
                "external_label_status": content["external_label_status"],
                "historical_basis_ids": content["historical_basis"],
                "rotation_start_status": content["rotation"],
                "f68_f69_mapping": content["f68_f69_mapping"],
                "confidence": content["confidence"],
            })
        locus_rows.append({
            "page": page,
            "locus": locus,
            "locus_number": number,
            "group_count": len(events),
            "surface_sequence_ZL3b": surface_sequence,
            "structural_role": content["role"],
            "inventory_item": content["inventory_item"],
            "complete_local_exemplar_German": content["text"],
            "external_label_status": content["external_label_status"],
            "historical_basis_ids": content["historical_basis"],
            "strongest_rival": content["strongest_rival"],
            "rotation_start_status": content["rotation"],
            "f68_f69_mapping": content["f68_f69_mapping"],
            "confidence": content["confidence"],
        })

    diagrams = [
        {
            "diagram_id": "A1", "page": "f67r2", "locus_count": 74, "group_count": 190,
            "selected_system": "7_PLANETS_X_12_ZODIAC_BODY_SECTORS_WITH_12_HOUSES_AND_8_ELECTION_CHECKS",
            "complete_default_German": "Bestimme Tages- oder Stundenherrn, Mondzeichen und geschonten Körperbezirk; rahme die Frage durch das lokale Zwölferinventar, prüfe acht Mondbedingungen und erlaube, mildere oder verschiebe den bereits medizinisch bestimmten Eingriff.",
            "competing_value_system": "Nebeneinander kopierte Planeten-, Zeichen-, Häuser- und Lehrlisten ohne Verrechnung",
            "historical_mechanism": "Zodiakmann, Planetenstunden, Astrologia medicorum und medizinische electiones.",
            "strongest_counterevidence": "Keine vollständige 7-mal-12-Matrix, kein identifiziertes Symbol und keine sichtbare Rechenoperation.",
            "start_direction_status": "EDITORIAL SOURCE-LOCUS ORDER; AUTHORIAL START/DIRECTION UNPROVEN",
            "direct_crosspage_mapping": "NONE", "confidence": "0.46",
        },
        {
            "diagram_id": "A2", "page": "f68r1", "locus_count": 37, "group_count": 65,
            "selected_system": "CENTRE_PLUS_28_SPATIAL_LUNAR_MANSION_CATALOGUE",
            "complete_default_German": "Lies das Zentrum als Mondkatalog-Besitzer und jede der achtundzwanzig nichtzentralen Sternstellen als räumlich eigene Adresse; die Picatrix-Namen und Wirkungen sind nur ein äußerer vollständiger Editionsvergleich.",
            "competing_value_system": "Räumlicher Sternnamen- oder Gedächtniskatalog ohne Mondhausfolge",
            "historical_mechanism": "Lateinische 28-Mondhäuser-Verzeichnisse mit Namen und lokalen Operationen.",
            "strongest_counterevidence": "Die Zahl 28 allein entscheidet nichts; Start, Richtung und sämtliche Namen fehlen.",
            "start_direction_status": "EDITORIAL S01=f68r1.9; AUTHORIAL START/DIRECTION UNPROVEN",
            "direct_crosspage_mapping": "NONE", "confidence": "0.40",
        },
        {
            "diagram_id": "A3", "page": "f69v", "locus_count": 31, "group_count": 140,
            "selected_system": "INDEPENDENT_ORDERED_28_MEDICAL_ELECTION_RULES",
            "complete_default_German": "Lies die drei Kreisrubriken als Gebrauchsanweisung und die achtundzwanzig Radialeinträge als unabhängige lokale Wahlregeln für Bad, Waschung, Salbung, Ruhe, Maß oder Aderlass; gleiche vollständige Einträge behalten dieselbe Regel.",
            "competing_value_system": "Mondhausmagie, nichtmedizinische Arbeitswahl oder bloße Kopierfolge; ein gewöhnliches Lunarium hätte typischerweise dreißig Tage.",
            "historical_mechanism": "Mondhaus-electiones und medizinische Wahlpraxis, nicht eine bewiesene f68-Tabelle.",
            "strongest_counterevidence": "Keine externe Regel ist mit einer Oberfläche verankert; LONG/SHORT ist keine Polarität und die 28er-Zahl passt schlecht zum üblichen 30-Tage-Lunarium.",
            "start_direction_status": "TRANSCRIPTION R01=f69v.4; AUTHORIAL START/DIRECTION UNPROVEN",
            "direct_crosspage_mapping": "NONE", "confidence": "0.36",
        },
    ]

    sources = [
        {"source_id": "S1", "date": "ca. 1425", "institution_item": "Wellcome Collection MS.8515", "comparator": "Praktisches computistisches und astromedizinisches Handbuch", "supports": "Sieben Planeten, Medizin nach Tierkreiszeichen, vier Humores und Tabellen in einem Gebrauchscodex.", "limits": "Keine 28er-Identität und kein Voynich-Wert.", "url": "https://wellcomecollection.org/works/w9nkm98w"},
        {"source_id": "S2", "date": "1415–1420", "institution_item": "Wellcome Collection, englischer Faltalmanach", "comparator": "Mobiles medizinisches Almanachinstrument", "supports": "Planetenstunden und Mond im Zeichen wurden vor medizinischen Eingriffen konsultiert; Zodiakmann als Körperveto.", "limits": "Layout und Zeichen sind keine Voynich-Zuordnung.", "url": "https://wellcomecollection.org/stories/the-enigma-of-the-medieval-folding-almanac"},
        {"source_id": "S3", "date": "1430er", "institution_item": "Michael-of-Rhodes-Manuskript, Museo Galileo/Dibner project", "comparator": "Vernakuläre medizinische Astrologie", "supports": "Mondzeichen regieren Körperteile und steuern den Zeitpunkt des Aderlasses; separate Mondtabelle.", "limits": "Zwölf Zeichen, nicht 28 Stationen.", "url": "https://brunelleschi.imss.fi.it/michaelofrhodes/manuscript/page_103b.html"},
        {"source_id": "S4", "date": "ca. 1446", "institution_item": "British Library Harley MS 1736", "comparator": "Medizinisches Sammelbuch", "supports": "Astrologia medicorum neben lateinischem Text über sieben Planeten, Tierkreiszeichen und astrologische Tabellen.", "limits": "Etwas später als 1420; keine Voynich-Schriftbeziehung.", "url": "https://searcharchives.bl.uk/catalog/040-002047567"},
        {"source_id": "S5", "date": "mittelalterliche lateinische Überlieferung; konsultierte Edition 1986", "institution_item": "Warburg Institute, Picatrix Latinus", "comparator": "28 Mondhäuser mit Namen, Graden und Operationen", "supports": "Explizite 28er-Folge; einzelne Häuser betreffen Arzneieinnahme oder Heilung.", "limits": "Die Mehrzahl der Operationen ist nichtmedizinisch oder magisch; Namen/Start sind nur externer Editionsvergleich.", "url": "https://commons.warburg.sas.ac.uk/downloads/8g84mm241"},
        {"source_id": "S6", "date": "15. Jahrhundert", "institution_item": "Society of Antiquaries MSS/0039/01", "comparator": "28 Mondhäuser und sieben Planetensiegel in einem Manuskript", "supports": "Zeitgenössische gemeinsame Werkstattökologie von 28er- und 7er-Inventaren.", "limits": "Magisch-alchemische Zwecke, nicht medizinische Wahltafel.", "url": "https://collections.sal.org.uk/mss.0039.01"},
        {"source_id": "S7", "date": "spätmittelalterlicher Brugger Text; Edition 1977", "institution_item": "DBNL/KANTL, Braekman, Middelnederlandse maanvoorzeggingen", "comparator": "Kollektives Lunarium", "supports": "Tagesprognosen konnten Krankheit, Aderlass und Handlungsbeginn betreffen.", "limits": "Die Folge hat dreißig Mondtage; das schwächt eine wörtliche 28-Tage-Lesung von f69.", "url": "https://www.dbnl.org/tekst/_ver016197701_01/_ver016197701_01_0009.php"},
        {"source_id": "S8", "date": "ca. 1500", "institution_item": "Wellcome Collection MS.97", "comparator": "Astrologisches Handbuch für medizinische Behandlung", "supports": "Planetenherr, Planetenstunden, zwölf Zeichen, Komplexionen, Schröpfen und Aderlass als praktisches Bündel.", "limits": "Später Vergleich; keine 28er-Seitenidentität.", "url": "https://wellcomecollection.org/works/gftr4sa9"},
    ]

    group_fields = list(group_rows[0])
    locus_fields = list(locus_rows[0])
    diagram_fields = list(diagrams[0])
    source_fields = list(sources[0])
    write_tsv(OUT / "V66_R2_395_GROUP_ASTRO_INTERLINEAR.tsv", group_rows, group_fields)
    write_tsv(OUT / "V66_R2_142_LOCUS_EDITIONS.tsv", locus_rows, locus_fields)
    write_tsv(OUT / "V66_R2_THREE_DIAGRAM_EDITIONS.tsv", diagrams, diagram_fields)
    write_tsv(OUT / "V66_R2_HISTORICAL_SOURCES.tsv", sources, source_fields)

    page_groups = Counter(row["page"] for row in group_rows)
    page_loci = Counter(row["page"] for row in locus_rows)
    rule_loci = [row for row in locus_rows if row["page"] == "f69v" and int(row["locus_number"]) >= 4]
    repeated = {11: rule_loci[10]["complete_local_exemplar_German"], 15: rule_loci[14]["complete_local_exemplar_German"], 24: rule_loci[23]["complete_local_exemplar_German"]}
    checks = {
        "exact_pages": set(page_groups) == set(PAGES),
        "no_forbidden_page": not any(str(row["page"]).startswith("f84") for row in group_rows),
        "group_total_395": len(group_rows) == 395,
        "group_page_counts_190_65_140": page_groups == {"f67r2": 190, "f68r1": 65, "f69v": 140},
        "locus_total_142": len(locus_rows) == 142,
        "locus_page_counts_74_37_31": page_loci == {"f67r2": 74, "f68r1": 37, "f69v": 31},
        "three_diagrams": len(diagrams) == 3,
        "all_group_defaults_nonblank": all(str(row["default_content_German"]).strip() for row in group_rows),
        "all_groups_explicitly_not_card_gloss": all("KEINE KARTENGLOSSE" in str(row["default_content_German"]) for row in group_rows),
        "all_external_names_flagged": all(row["external_label_status"] != "NONE" for row in group_rows if row["locus_role"] in {"ZODIAC_BODY_SECTOR_LOCAL_EXEMPLAR", "SEVEN_PLANET_LOCAL_EXEMPLAR", "TWELVE_HOUSE_CONTROL_LOCAL_EXEMPLAR", "SPATIAL_LUNAR_MANSION_LOCAL_EXEMPLAR"}),
        "source_event_order_preserved": [int(row["source_event_serial"]) for row in group_rows] == [int(row["source_event_serial"]) for row in source_rows],
        "f68_has_28_spatial_stations": sum(row["structural_role"] == "SPATIAL_LUNAR_MANSION_LOCAL_EXEMPLAR" for row in locus_rows) == 28,
        "f69_has_28_rule_loci": len(rule_loci) == 28,
        "f69_rule_surfaces_match_v22": all(rule_loci[i]["surface_sequence_ZL3b"] == source_rules[i]["surface_entry"] for i in range(28)),
        "repeated_okeod_rule_consistent": len(set(repeated.values())) == 1,
        "no_f68_f69_identity_claim": all(row["f68_f69_mapping"] == "NONE" for row in locus_rows),
        "start_direction_uncertainty_explicit": all("UNPROVEN" in row["rotation_start_status"] for row in locus_rows),
        "sources_documented": len(sources) == 8,
    }
    validation = {
        "schema": "SIDEQUEST_V66_R2_HISTORICAL_ASTRO_EDITION_VALIDATION_V1",
        "status": "PASS" if all(checks.values()) else "FAIL",
        "checks": checks,
        "counts": {
            "pages": 3, "groups": len(group_rows), "loci": len(locus_rows),
            "groups_by_page": dict(page_groups), "loci_by_page": dict(page_loci),
            "f68_spatial_stations": 28, "f69_rule_loci": 28,
            "historical_sources": len(sources), "portable_Astro_card_glosses": 0,
        },
        "decisions": {
            "f67r2": diagrams[0]["selected_system"],
            "f68r1": diagrams[1]["selected_system"],
            "f69v": diagrams[2]["selected_system"],
            "f68_f69_mapping": "NONE",
            "lunar_day_vs_mansion": "28_MANSION_OR_RULE_SEQUENCE_PREFERRED; ORDINARY_LUNARIUM_TYPICALLY_30_DAYS",
        },
        "sealed": {"f84": "NOT_OPENED", "f84r": "NOT_OPENED"},
    }
    (OUT / "V66_R2_VALIDATION.json").write_text(json.dumps(validation, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if validation["status"] != "PASS":
        raise SystemExit(json.dumps(validation, ensure_ascii=False, indent=2))
    print(json.dumps(validation, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
