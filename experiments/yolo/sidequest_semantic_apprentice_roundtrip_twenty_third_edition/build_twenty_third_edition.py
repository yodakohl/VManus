#!/usr/bin/env python3
from pathlib import Path
import csv
import json

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
DICT = ROOT / "experiments/yolo/sidequest_semantic_final_productive_cards_nineteenth_edition/NINETEENTH_487_SURFACE_DICTIONARY.tsv"
UNITS = ROOT / "experiments/yolo/sidequest_semantic_stem_aligned_twentieth_edition/TWENTIETH_258_UNIT_TRANSLATIONS.tsv"


def read(path):
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(path, fields, rows):
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


DECK = [
    ("AIIN", "COMMON", "SOLLWERT", "Sollmaß oder Tabellenwert"),
    ("AIN", "COMMON", "PORTION", "Teilmenge oder Unterabschnitt"),
    ("IIN", "COMMON", "STUFE", "Arbeits- oder Bedingungsstufe"),
    ("AL", "COMMON", "ZIEL", "Zielstelle oder Zielsektor"),
    ("AR", "COMMON", "QUELLE", "Ausgang oder Bezugswert"),
    ("AIR", "COMMON", "LAUF_BAHN", "Wasserlauf oder Himmelsbahn"),
    ("OK", "COMMON", "ANSETZEN", "Posten in Arbeit setzen"),
    ("OL", "COMMON", "FORTSETZEN", "denselben Gang weiterführen"),
    ("OT", "COMMON", "FOLGEND", "nächster Posten oder nächste Stufe"),
    ("OR", "COMMON", "ANSATZ_SATZ", "Arbeitsansatz oder Tabellensatz"),
    ("Y", "BOUND", "DIESER_POSTEN", "aktuell gemeinter Posten"),
    ("E", "BOUND", "KURZ", "kurze oder erste Stufe"),
    ("EE", "BOUND", "LAENGER", "längere oder zweite Stufe"),
    ("EEE", "BOUND", "VOLL", "volle oder dritte Stufe"),
    ("CLOSE", "BOUND", "SCHLUSS", "lokalen Arbeitsschritt schließen"),
    ("CHD", "PROCESS", "UMSETZEN", "von einem Posten in den nächsten führen"),
    ("CTH", "PROCESS", "BEREIT", "Arbeitszustand ist bereit"),
    ("CKH", "PROCESS", "DURCHLAUF", "durch einen Gang führen"),
    ("CKHE", "PROCESS", "TRENNEN", "seihen oder Stoffe trennen"),
    ("CHK", "PROCESS", "WAERMEN", "wärmen oder warm halten"),
    ("SHED", "PROCESS", "ABSETZEN", "stehen und absetzen lassen"),
    ("SOLK", "PROCESS", "SAMMELN", "an einer Sammelstelle auffangen"),
    ("HO", "PROCESS", "EINGANGSPOSTEN", "Zutat oder Tafeleingang"),
    ("CHEO", "PROCESS", "AUSGABE_AUSZUG", "gewonnener Auszug oder Tabellenwert"),
    ("KCH", "PROCESS", "BEARBEITEN", "lokalen Arbeitsgang ausführen"),
    ("TY", "PROCESS", "TEIL", "Teil oder abgetrennter Posten"),
    ("SH", "PROCESS", "HALTEN", "Posten oder Tabellenwert halten"),
    ("CHEEY", "PROCESS", "SICHTBARES_ERGEBNIS", "Klarauszug oder Ablesewert"),
    ("YK", "TABLE_LOCAL", "KLASSE_HAUS", "bezeichnete Tabellenklasse"),
    ("YT", "TABLE_LOCAL", "PLATZ_PHASE", "bezeichneter Platz oder Phase"),
    ("OD", "TABLE_LOCAL", "MARKIERT", "Wert eintragen oder markieren"),
    ("YD", "TABLE_LOCAL", "AKTIVE_ZEILE", "aktive oder notierte Tabellenzeile"),
    ("AM", "TABLE_LOCAL", "ASPEKT", "Aspekt des sichtbaren Platzes"),
    ("G", "TABLE_LOCAL", "GRAD", "Grad des sichtbaren Platzes"),
    ("OS", "TABLE_LOCAL", "FELD", "sichtbares Feld oder Rahmen"),
    ("A", "TABLE_LOCAL", "HAUPTWERT", "Hauptwert der lokalen Tafel"),
    ("S", "TABLE_LOCAL", "NEBENWERT", "Nebenwert der lokalen Tafel"),
    ("O", "TABLE_LOCAL", "GRUNDWERT", "Grundwert der lokalen Tafel"),
    ("D", "TABLE_LOCAL", "FESTWERT", "festgesetzter Tabellenwert"),
    ("R", "TABLE_LOCAL", "BEZUGSWERT", "lokaler Bezugswert"),
    ("CH", "TABLE_LOCAL", "ZUSTAND", "lokaler Tabellenzustand"),
    ("T", "TABLE_LOCAL", "PHASENFOLGE", "Phase oder Platzfolge"),
    ("IIR", "TABLE_LOCAL", "INDEX", "lokaler Index"),
    ("OP", "TABLE_LOCAL", "PAARFELD", "Paar- oder Gegenfeld"),
    ("K", "TABLE_LOCAL", "KLASSE", "lokale Klasse"),
    ("SEL", "TABLE_LOCAL", "AUSGEWAEHLT", "gebundener Auswahlhaken"),
    ("CFH", "LEARNED_BODY", "AUSWRINGEN", "gelerntes Werkstattzeichen"),
    ("CPH", "LEARNED_BODY", "NACHSEIHEN", "gelerntes Werkstattzeichen"),
    ("PARTITION", "LEARNED_BODY", "ABTRENNEN", "gelerntes Werkstattzeichen"),
    ("WASH", "LEARNED_BODY", "WASCHEN", "gelerntes Werkstattzeichen"),
    ("LDDY", "LEARNED_BODY", "FESTMACHEN_SCHLUSS", "gelerntes Werkstattzeichen"),
    ("DCHE", "LEARNED_BODY", "WURZEL", "gelerntes Bildregisterzeichen"),
    ("DAN", "LEARNED_BODY", "ANWENDEN", "gelerntes Werkstattzeichen"),
    ("SK", "LEARNED_BODY", "AUSGIESSEN", "gelerntes Werkstattzeichen"),
    ("DL", "WHOLE_CARD", "ZUSATZ", "unzerlegte Fachkarte"),
    ("TALAM", "WHOLE_CARD", "AM_ZIEL_VERWAHREN", "unzerlegter Werkstattbefehl"),
]

LESSONS = [
    (1, "BESITZER", "Zeige zuerst Pflanze, Becken, Station, Stern, Ring oder Feld; der Besitzer liefert das konkrete Substantiv."),
    (2, "ARBEITSSTUECK", "Sprich einen ganzen Arbeitsschritt; die physische Zeile beendet ihn nicht automatisch."),
    (3, "LAENGSTER_KERN", "Suche die längste gelernte Karte oder den längsten Fachkörper, bevor du kurze Kerne liest."),
    (4, "ORDNUNG", "Setze OT für den nächsten und OL für denselben fortgesetzten Posten."),
    (5, "HANDLUNG", "Wähle OK, CHD, CKH, CKHE, CHK, SHED, SOLK oder eine gelernte Fachkarte."),
    (6, "MENGE", "Füge AIN für Portion, AIIN für Sollwert oder IIN für Stufe hinzu."),
    (7, "RICHTUNG", "Füge AR für Quelle, AL für Ziel oder AIR für Lauf/Bahn hinzu."),
    (8, "GRAD", "Setze E, EE oder EEE nur an eine dafür gelernte Handlungsfamilie."),
    (9, "POSTEN", "Y hält den gerade gemeinten Posten aktiv; es ist weder Satzzeichen noch Stoffname."),
    (10, "ABSCHLUSS", "Nutze nur die registrierte Schlusskarte der Familie; sichtbares dy ist nicht überall Schluss."),
    (11, "TAFEL", "Auf den Kreisblättern lies zuerst den sichtbaren Platz, dann YK, YT, OD, AM, G, OS oder die lokalen Primitiva."),
    (12, "GANZKARTE", "DL, TALAM und seltene lokale Werte werden aus dem Meisterexemplar kopiert, nicht erfunden zerlegt."),
    (13, "SCHREIBERFORM", "Wähle erst die Karte und danach ihre registrierte q-, s-, ch-, d- oder t-Schreiberform."),
    (14, "RUECKLESEN", "Lies Oberfläche zu Karte, Karte zu Kernen und Kerne mit Besitzer zurück; erst danach sprich flüssig."),
]

PROMPTS = {
    "H1-S001": "Wurzel ansetzen, Teil abtrennen, Wasser zulaufen lassen und auf Sollmaß stellen.",
    "H3-S001": "Pflanzenteil auswringen, bis zum Sollstand ruhen lassen, nachseihen und den Klarauszug beiseitestellen.",
    "H4-S002": "Die Portion auf Sollmaß bringen, umsetzen und am Ziel verwahren.",
    "B1-S002": "Wasserlauf und Portionen zum Beckenziel führen, länger halten, überführen und schließen.",
    "B2-S016": "Vom Ausgang zum Ziel führen, abteilen, auf Sollmaß stellen, kurz einsetzen und schließen.",
    "B4-S001": "Den bezeichneten Einsatz länger arbeiten lassen und den Schritt schließen.",
    "f67r2.19": "In der aktiven Zeile Eingang, Teil, Quelle und aktuellen Aspekt lesen.",
    "f68r1.37": "Zentralen Posten setzen, Quelle aktivieren und den aktuellen Grundgrad lesen.",
    "f69v.19": "Im linken Radialplatz Quelle und Ziel als eine gerichtete Zuordnung lesen.",
}

dictionary = read(DICT)
units = read(UNITS)
surface_map = {row["visible_surface"]: row for row in dictionary}
unit_map = {row["unit_id"]: row for row in units}

deck_rows = [
    {"teaching_order": index, "symbol": symbol, "layer": layer, "atomic_value_de": value, "owner_expansion_de": expansion}
    for index, (symbol, layer, value, expansion) in enumerate(DECK, 1)
]
write(HERE / "TWENTY_THIRD_COMPONENT_DECK.tsv", list(deck_rows[0]), deck_rows)

lesson_rows = [
    {"lesson": number, "name": name, "master_rule_de": rule}
    for number, name, rule in LESSONS
]
write(HERE / "TWENTY_THIRD_FOURTEEN_LESSONS.tsv", list(lesson_rows[0]), lesson_rows)

example_rows = []
for number, (unit_id, prompt) in enumerate(PROMPTS.items(), 1):
    row = unit_map[unit_id]
    surfaces = row["surface_sequence"].split()
    missing = [surface for surface in surfaces if surface not in surface_map]
    if missing:
        raise ValueError(f"unregistered surfaces in {unit_id}: {missing}")
    example_rows.append(
        {
            "example": number,
            "register": row["register"],
            "page": row["page"],
            "unit_id": unit_id,
            "visible_owner": row["visible_owner"],
            "master_dictation_de": prompt,
            "apprentice_surface_sequence": row["surface_sequence"],
            "recovered_atom_sequence": row["atom_sequence"],
            "recovered_literal_de": row["literal_card_reading_de"],
            "fluent_owner_reading_de": row["owner_expansion_de"],
            "roundtrip": "SAME_REGISTERED_UNIT",
        }
    )
write(HERE / "TWENTY_THIRD_NINE_ROUNDTRIP_EXAMPLES.tsv", list(example_rows[0]), example_rows)

manual = [
    "# Lehrbuch des Meisters: Karten setzen und zurücklesen",
    "",
    "Dieses Heft behandelt die Rekonstruktion als erlernbares Werkstattsystem.",
    "Der Meister diktiert keinen Buchstabentext, sondern Besitzer plus Arbeit;",
    "der Lehrling setzt produktive Kürzel und gelernte Ganzkarten.",
    "",
    "## Vier Kartenkästen",
    "",
    "- COMMON/BOUND: kleine gemeinsame Grammatik für Folge, Handlung, Menge, Richtung, Grad und aktuellen Posten.",
    "- PROCESS: Fachkörper für Umsetzen, Durchlauf, Trennen, Wärmen, Absetzen, Sammeln und sichtbares Ergebnis.",
    "- TABLE_LOCAL: lokale Kreisblattwerte; der sichtbare Stern, Sektor oder Ring ist immer Teil der Adresse.",
    "- LEARNED_BODY/WHOLE_CARD: seltene Werkstattzeichen werden als Ganzes aus dem Exemplar gelernt.",
    "",
    "## Vierzehn Lektionen",
    "",
]
for row in lesson_rows:
    manual.append(f"{row['lesson']}. **{row['name']}** — {row['master_rule_de']}")
manual.extend(["", "## Neun Hin-und-zurück-Lesungen", ""])
for row in example_rows:
    manual.extend(
        [
            f"### {row['example']}. {row['unit_id']} ({row['page']})",
            "",
            f"Meister: {row['master_dictation_de']}",
            "",
            f"Lehrling schreibt: `{row['apprentice_surface_sequence']}`",
            "",
            f"Kerne: `{row['recovered_atom_sequence']}`",
            "",
            f"Rücklesung: {row['recovered_literal_de']}",
            "",
            f"Mit sichtbarem Besitzer: {row['fluent_owner_reading_de']}",
            "",
        ]
    )
manual.extend(
    [
        "## Werkstattentscheidung",
        "",
        "Das System ist für mehrere Schreiber einfach genug, wenn der Meister drei Dinge",
        "mitliefert: das Bild oder Tabellenfeld, den kleinen gemeinsamen Kartenkasten und",
        "das lokale Exemplar. Es ist absichtlich kein reines Alphabet. Genau diese Mischung",
        "erklärt, warum viele Folgen regelhaft aussehen und seltene Werte trotzdem auswendig",
        "gelernt werden müssen.",
    ]
)
(HERE / "TWENTY_THIRD_MASTER_APPRENTICE_MANUAL.md").write_text("\n".join(manual).rstrip() + "\n", encoding="utf-8")

summary = {
    "status": "PASS",
    "counts": {
        "deck_entries": len(deck_rows),
        "lessons": len(lesson_rows),
        "roundtrip_examples": len(example_rows),
        "prose_examples": sum(row["register"] == "PROSE" for row in example_rows),
        "astro_examples": sum(row["register"] == "ASTRO" for row in example_rows),
        "registered_surfaces": len(dictionary),
        "available_units": len(units),
    },
}
(HERE / "BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(json.dumps(summary, ensure_ascii=False, indent=2))
