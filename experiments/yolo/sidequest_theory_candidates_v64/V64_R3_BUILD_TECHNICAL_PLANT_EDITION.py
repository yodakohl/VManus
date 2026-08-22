#!/usr/bin/env python3
"""Build the V64 R3 technical plant/raw-material Herbal edition."""

from __future__ import annotations

import csv
from collections import Counter, defaultdict
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
YOLO = ROOT / "experiments" / "yolo"

SOURCE_ARTICLES = YOLO / "sidequest_theory_candidates_v53" / "V53_SELECTED_FIVE_ARTICLES.tsv"
SOURCE_DECISIONS = YOLO / "sidequest_theory_candidates_v60" / "V60_SELECTED_EXACT_CARD_DECISIONS.tsv"
SOURCE_EVENTS = YOLO / "sidequest_theory_candidates_v60" / "V60_SELECTED_381_EVENT_LEDGER.tsv"
SOURCE_STATEMENTS = YOLO / "sidequest_theory_candidates_v61" / "V61_SELECTED_116_SOURCE_STATEMENTS.tsv"
SOURCE_MACHINE = YOLO / "sidequest_theory_candidates_v62" / "V62_SELECTED_116_REGISTER_TRANSITIONS.tsv"
SOURCE_PARSE_EVENTS = YOLO / "sidequest_theory_candidates_v63" / "V63_SELECTED_381_EVENT_TEMPLATE_LEDGER.tsv"
SOURCE_PARSE_FIELDS = YOLO / "sidequest_theory_candidates_v63" / "V63_SELECTED_135_FIELD_SLOT_PARSE.tsv"
SOURCE_PARSE_STATEMENTS = YOLO / "sidequest_theory_candidates_v63" / "V63_SELECTED_116_STATEMENT_SLOT_PARSE.tsv"

OUT_EVENTS = HERE / "V64_R3_100_EVENT_PLANT_LEDGER.tsv"
OUT_FIELDS = HERE / "V64_R3_20_FIELD_PLANT_EDITION.tsv"
OUT_STATEMENTS = HERE / "V64_R3_19_STATEMENT_COMPARISON.tsv"
OUT_RECORDS = HERE / "V64_R3_5_RECORD_PLANT_EDITION.tsv"
OUT_GRAPHS = HERE / "V64_R3_5_RECORD_PROCESS_GRAPHS.tsv"
OUT_COSTS = HERE / "V64_R3_10_RECORD_MODEL_ASSUMPTION_COSTS.tsv"


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: list[dict[str, str]]) -> None:
    if not rows:
        raise ValueError(f"empty output: {path.name}")
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n", extrasaction="raise")
        writer.writeheader()
        writer.writerows(rows)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def herbal(row: dict[str, str]) -> bool:
    return row["record_unit_id"].startswith("H")


FIXED_VALUE_CLAUSE = {
    "MASS?": "MASS?=vorgesehenen Mengenwert buchen",
    "ANWENDEN?": "ANWENDEN?=aktive Charge am gesetzten Arbeitsziel einsetzen",
    "BEREIT?": "BEREIT?=Freigabestand der aktiven Charge prüfen",
    "ANSATZ?": "ANSATZ?=aktiven Arbeitsansatz aufnehmen",
    "ZIEL?": "ZIEL?=Arbeitsziel setzen oder bestätigen",
    "KLAR?": "KLAR?=Klarzustand der aktiven Charge prüfen",
    "VORIGES?": "VORIGES?=vorige Charge wieder aufnehmen",
    "ANTEIL?": "ANTEIL?=bezeichnete Fraktion wählen",
}

ASSUMPTION_WEIGHTS = {
    "PART_OR_HARVEST": 1,
    "PROCESS_STEP": 1,
    "MEDIUM_OR_ADDITIVE": 1,
    "CONTAINER_OR_TARGET": 1,
    "STORAGE_CONDITION": 1,
    "PRODUCT_FUNCTION": 2,
    "DISEASE_OR_BODY": 2,
}


def assumptions(**counts: int) -> dict[str, int]:
    require(set(counts) <= set(ASSUMPTION_WEIGHTS), f"unknown assumption class: {set(counts) - set(ASSUMPTION_WEIGHTS)}")
    return {key: value for key, value in counts.items() if value}


def encode_assumptions(counts: dict[str, int]) -> str:
    return "|".join(f"{key}:{counts[key]}" for key in ASSUMPTION_WEIGHTS if counts.get(key)) or "NONE"


def assumption_cost(counts: dict[str, int]) -> int:
    return sum(ASSUMPTION_WEIGHTS[key] * count for key, count in counts.items())


# These are local operational hypotheses, never card glosses.  Each list is in
# exact source-event order for its field.
FIELD_EVENT_FILLERS = {
    "F001": [
        "Bildbesitzer H1 als Rohstofflos H1-R01 eröffnen",
        "unteren Wurzelstock als sichtbaren Pflanzenteil wählen",
        "Erde und Fremdstoff mit Wasser abwaschen",
        "beschädigte Fasern aussortieren",
        "sauberen Wurzelstock grob schneiden",
        "Schnittgut im Mazeriergefäß mit Wasser bedecken",
        "Auszug umrühren und eine Prüfportion abnehmen",
        "aktive Prüfportion=H1-P01; Arbeitsziel=Musterstreifen H1-T01",
        "Sollwert für die Prüfportion in das Losregister eintragen",
        "trockenen Rest als H1-R02 verwahren",
    ],
    "F002": [
        "gelagerten Wurzelrest H1-R02 aufnehmen",
        "zweiten Auszug gelinde erwärmen",
        "formale Verknüpfung mit dem laufenden Wurzelauszug H1-P01 buchen",
        "Arbeitsstand H1-P02 freigeben",
    ],
    "F003": [
        "Bildbesitzer H2 als Oberteil-Los H2-R01 eröffnen",
        "Erntegut als verarbeitungsbereit markieren",
        "gepresste Arbeitsflüssigkeit H2-P01 als aktiven Ansatz führen",
        "Stängel und obere Blätter grob quetschen",
        "austretende Pflanzenflüssigkeit auffangen",
        "Pressgut mit Wasser nachziehen",
        "beide Flüssigkeiten zusammenführen",
        "Sollmenge für H2-P01 buchen",
        "Pressrückstand als Nebenfraktion H2-R02 markieren",
    ],
    "F004": [
        "frühe Erntefraktion H2-R03 eröffnen",
        "H2-P01 als aktiven Ansatz ansprechen",
        "eine Teilmenge H2-R03 in ein Vergleichsgefäß geben",
        "formalen aktiven Link zwischen Vergleichsgefäß und laufender Charge setzen",
        "vorige Charge H2-P01 wieder aufnehmen",
        "diese vorige Charge an Vergleich H2-P02 verknüpfen",
        "Sollmenge für H2-P02 buchen",
        "frühe Fraktion vollständig mazerieren",
    ],
    "F005": [
        "späte Erntefraktion H2-R04 eröffnen",
        "H2-P02 als ersten aktiven Ansatz führen",
        "späte Teilcharge H2-P03 als zweiten aktiven Ansatz führen",
        "beide Ernteauszüge in getrennten Gefäßen umrühren",
        "beide durch dasselbe Tuch seihen",
        "Farbe und Bodensatz als Vergleichsmerkmale notieren",
        "Vergleichspaar H2-P02/H2-P03 verschlossen lagern",
    ],
    "F006": [
        "Bildbesitzer H3 als Blüten-Kraut-Los H3-R01 eröffnen",
        "junge oberirdische Teile sammeln",
        "Blütenköpfe und Blätter in zwei Schalen sortieren",
        "Krautfraktion quetschen und in Wasser mazerieren",
        "Auszug zuerst grob, dann durch Tuch seihen",
        "Klarheitszustand des Filtrats H3-P01 prüfen",
        "klares Filtrat absetzen lassen und Feld schließen",
    ],
    "F007": ["einen Blütenkopf als Referenzfraktion H3-R02 zurücklegen"],
    "F008": [
        "Filtrat H3-P01 wieder aufnehmen",
        "drei gleiche Probengläser bereitstellen",
        "Filtrat auf die Probengläser verteilen",
        "Farbton und Niederschlag je Glas vermerken",
        "Sollmenge je Probenglas buchen",
    ],
    "F009": [
        "Blattfraktion H3-R03 als neue Charge eröffnen",
        "Blätter warm in Wasser ausziehen",
        "Arbeitsstand H3-P02 als bereit markieren",
        "Blattauszug und Referenzblüte getrennt verwahren",
    ],
    "F010": [
        "formalen Standardslot für Blattposten H4-R01 setzen",
        "Sollmenge frischer breiter Blätter buchen",
        "Blätter waschen und grob schneiden",
        "Schnittgut in Wasser mazerieren",
        "erste Blattflotte absetzen lassen und Feld schließen",
    ],
    "F011": [
        "Sollmenge aus H4-P01 abteilen",
        "weichen Blattrest aus der Flotte heben",
        "Rest pressen, Flüssigkeit seihen und beide Fraktionen schließen",
    ],
    "F012": [
        "zweite Blattfraktion H4-R02 eröffnen",
        "zweite Fraktion mit frischem Wasser waschen",
        "Fraktion warm mazerieren",
        "zweite Blattflotte H4-P03 seihen und schließen",
    ],
    "F013": [
        "Sollmenge der zweiten Flotte buchen",
        "opaken Relationsslot für Fraktionspaar und Lagergefäß setzen",
        "erste und zweite Flotte nebeneinander prüfen",
        "zweite Flotte als aktiven Ansatz H4-P03 führen",
        "Presskuchen und Flotten als Paarposten etikettieren",
        "Paarposten H4-P04 bedeckt lagern",
    ],
    "F014": [
        "Bildbesitzer H5 als drüsiges Feuchtland-Rohlos H5-R01 eröffnen",
        "kleine Gesamtpflanzenprobe sammeln",
        "feine Wurzel- und Krautfraktion trennen",
        "Sollmenge der Krautfraktion buchen",
    ],
    "F015": [
        "Krautfraktion in wenig Wasser einweichen",
        "weiches Material quetschen",
        "klebrige Flüssigkeit als Prüfcharge H5-P01 auffangen",
        "aktive Prüfcharge H5-P01 auf Prüffläche H5-T01 einsetzen",
        "Zieladresse H5-T01 nach dem Auftrag im Register festhalten",
    ],
    "F016": [
        "H5-P01 als aktive Charge wieder aufnehmen",
        "zweite Prüffläche H5-T02 bereitstellen",
        "aktive Charge auf H5-T02 einsetzen",
        "beschichtete Prüffläche lufttrocknen lassen und schließen",
    ],
    "F017": [
        "Kopf- oder Knospenfraktion H5-R02 eröffnen",
        "schmale Blattfraktion H5-R03 getrennt einführen",
        "beide Fraktionen mit Loszeichen versehen",
        "beide im Schatten trocknen",
    ],
    "F018": [
        "getrocknete Blattfraktion H5-R03 wieder aufnehmen",
        "Lagerfach H5-T04 zuweisen",
        "Fraktion trocken im Lagerfach verwahren",
    ],
    "F019": [
        "frischen Pflanzenrest H5-R04 als neue Arbeitscharge einführen",
        "Rest mit wenig Wasser wieder anfeuchten",
        "Rest zu gleichmäßiger Klebmasse arbeiten",
        "frische Masse H5-P02 im bedeckten Topf lagern",
    ],
    "F020": [
        "bezeichnete Blütenfraktion H5-R05 wählen",
        "geöffnete Blüte als Referenzteil einlegen",
        "Sollmenge des Referenzloses buchen",
    ],
}


FIELD_PLAN = {
    "F001": ("H1-R01 sichtbarer Wurzelstock", "H1-P01 Prüfauszug + H1-R02 Trockenrest", "Wurzelstock sammeln, waschen, sortieren, schneiden und in Wasser mazerieren; aktive Prüfportion am Musterstreifen einsetzen, Sollmaß buchen, Rest trocken lagern.", "Wasser, Musterstreifen und Auszugsfunktion sind lokale Annahmen."),
    "F002": ("H1-P01 + H1-R02", "H1-P02 freigegebener zweiter Wurzelauszug", "Gelagerten Wurzelrest aufnehmen, zweiten Auszug erwärmen, formal an den laufenden Stand verknüpfen und als bereit freigeben.", "Wärme und die Identität beider verknüpften Chargen sind nicht aus der Karte lesbar."),
    "F003": ("H2-R01 sichtbare obere Pflanzenteile", "H2-P01 Press-/Nachauszug + H2-R02 Pressrest", "Oberteile sammeln, quetschen, Pflanzenflüssigkeit auffangen, mit Wasser nachziehen, zusammenführen und nach Sollmenge buchen.", "Pressen, Wasser und oberirdischer Pflanzenteil sind Record-Expansion."),
    "F004": ("H2-P01 + frühe Fraktion H2-R03", "H2-P02 frühe Vergleichscharge", "Frühe Erntefraktion eröffnen, aktiven und vorigen Ansatz verknüpfen, Sollmenge abteilen und als Vergleich mazerieren.", "Die frühe Erntezeit und Vergleichsfunktion sind nicht durch die exakten Karten festgelegt."),
    "F005": ("H2-P02 + späte Fraktion H2-R04", "H2-P02/H2-P03 gelagertes Vergleichspaar", "Späte Fraktion als parallelen Ansatz führen, beide Auszüge gleich seihen, Farbe und Bodensatz vergleichen und verschlossen lagern.", "Spätfraktion, Farbe und Lagerart sind stille technische Argumente."),
    "F006": ("H3-R01 sichtbares Blüten-/Krautlos", "H3-P01 geklärtes Filtrat + sortierte Nebenfraktion", "Junge Teile sortieren, quetschen, in Wasser mazerieren und zweimal seihen; bei KLAR?-Gate absetzen lassen und schließen.", "Wasser, zweimaliges Seihen und die Farbextraktfunktion sind lokale Prozessannahmen."),
    "F007": ("H3-R01 Blütenkopf", "H3-R02 Referenzfraktion", "Einen Blütenkopf als offene Referenzfraktion zurücklegen.", "Das einzige Ereignis ist EXEMPLAR_ONLY; Referenzfunktion vollständig lokal."),
    "F008": ("H3-P01 geklärtes Filtrat", "H3-T03 dosierte Probenserie", "Filtrat wieder aufnehmen, auf drei Probengläser verteilen, Farbe und Niederschlag vermerken und das Sollmaß je Glas buchen.", "Gläser, Farbe und Probensinn sind stille technische Argumente."),
    "F009": ("H3-R03 Blattfraktion", "H3-P02 bereiter getrennter Blattauszug", "Blattfraktion warm ausziehen, am BEREIT?-Gate freigeben und getrennt von der Referenzblüte verwahren.", "Warmer Auszug und getrennte Lagerung sind exemplarische Expansion."),
    "F010": ("H4-R01 sichtbare breite Blätter", "H4-P01 erste abgesetzte Blattflotte", "Standardposten und Sollmaß setzen, Blätter waschen, schneiden und in Wasser mazerieren; erste Flotte absetzen und schließen.", "Wasser, Waschen und Blattflotte sind lokale Rohstoffannahmen."),
    "F011": ("H4-P01 Blattflotte", "H4-P02 geseihte Flüssigkeit + Presskuchen", "Sollmenge abteilen, weichen Blattrest heben, pressen und die Flüssigkeit seihen; beide Fraktionen schließen.", "Presskuchen und Trennverfahren stehen nicht in den lizenzierten Karten."),
    "F012": ("H4-R02 zweite Blattfraktion", "H4-P03 zweite geseihte Blattflotte", "Zweite Fraktion mit frischem Wasser waschen, warm mazerieren, seihen und als Parallelposten schließen.", "Das ganze Feld ist UNPARSED; alle Verfahrenswörter sind lokal."),
    "F013": ("H4-P02 + H4-P03", "H4-P04 etikettierter Paarlagerposten", "Sollmenge buchen, opaken Relationsslot setzen, beide Fraktionen vergleichen, aktiven Ansatz aufnehmen, etikettieren und bedeckt lagern.", "Der formale Relationsslot bedeutet weder Gefäß noch Vergleich; beides sind lokale Argumente."),
    "F014": ("H5-R01 sichtbares drüsiges Feuchtlandmaterial", "H5-R01 abgeteilte Krautfraktion", "Kleine Gesamtprobe sammeln, Wurzel und Kraut trennen und die Sollmenge der Krautfraktion buchen.", "Teilgrenze und kleine Menge sind visuell-lokale Annahmen."),
    "F015": ("H5-R01 Krautfraktion", "H5-P01 Mucilage-Prüfcharge an H5-T01", "Kraut einweichen und quetschen, klebrige Flüssigkeit auffangen, aktive Charge auf Prüffläche einsetzen und danach die Zieladresse buchen.", "Mucilage, Wasser und Prüffläche sind technische Hypothesen; ACTION vor TARGET bleibt auffällig."),
    "F016": ("H5-P01 aktive Prüfcharge", "H5-T02 luftgetrocknete Beschichtungsprobe", "Aktive Charge aufnehmen, auf eine zweite Prüffläche einsetzen, lufttrocknen lassen und schließen.", "Die zweite Prüffläche und Beschichtungsfunktion sind stille Argumente."),
    "F017": ("H5-R02 Kopf + H5-R03 schmales Blatt", "getrennte trocknende Referenzfraktionen", "Kopf- und Blattfraktion getrennt eröffnen, mit Loszeichen versehen und im Schatten trocknen.", "Das Feld ist UNPARSED; Fraktionen und Trocknung stammen nur aus dem Recordmodell."),
    "F018": ("getrocknete H5-R03 Blattfraktion", "H5-R03 im Lagerfach H5-T04", "Getrocknete Blattfraktion wieder aufnehmen, Lagerfach zuweisen und trocken verwahren.", "Das Feld ist UNPARSED; Lagerziel und Wiederaufnahme kommen aus V62 plus lokaler Expansion."),
    "F019": ("H5-R04 frischer Pflanzenrest", "H5-P02 frische Klebmasse", "Frischen Rest anfeuchten, homogenisieren und als Klebmasse im bedeckten Topf lagern.", "Das Feld ist UNPARSED; Binderfunktion, Wasser und Gefäß sind Zusatzannahmen."),
    "F020": ("H5-R05 geöffnete Blütenfraktion", "H5-R05 abgemessenes Referenzlos", "Bezeichnete Blütenfraktion wählen, als Referenzteil einlegen und das Sollmaß buchen.", "Nur Auswahl und Maß sind lizenziert; Blüte und Referenzzweck kommen aus Bild und Record."),
}


STATEMENT_PLAN = {
    "H1-S001": {
        "reading": "Bild-Wurzelstock als Rohlos H1-R01 übernehmen, reinigen, schneiden und in Wasser mazerieren; aktive Prüfportion am Musterstreifen einsetzen, Sollmaß buchen und trockenen Rest lagern.",
        "winner": "IATROMEDICAL",
        "reason": "Der technische Ablauf ist registerklar, doch das f10r-Heilpflanzenbild und der V53-Abiss-Wasser-Vergleich stützen den medizinischen Artikel stärker als einen Musterstreifen.",
        "contradiction": "Prüfstreifen und Werkstattzweck besitzen keinen sichtbaren Eigentümer.",
        "tech": assumptions(PART_OR_HARVEST=1, PROCESS_STEP=5, MEDIUM_OR_ADDITIVE=1, CONTAINER_OR_TARGET=1, STORAGE_CONDITION=1, PRODUCT_FUNCTION=1),
        "med": assumptions(PART_OR_HARVEST=1, PROCESS_STEP=4, MEDIUM_OR_ADDITIVE=2, CONTAINER_OR_TARGET=1, STORAGE_CONDITION=1, PRODUCT_FUNCTION=1, DISEASE_OR_BODY=1),
    },
    "H1-S002": {
        "reading": "Gelagerte H1-Wurzelcharge aufnehmen, einen zweiten Auszug erwärmen, formal an den laufenden Stand verknüpfen und als arbeitsbereit freigeben.",
        "winner": "TIE",
        "reason": "RESUME/LINK/BEREIT trägt beide Lesungen; weder warme Anwendung noch Materialfreigabe ist Karteninhalt.",
        "contradiction": "Die verknüpften Chargen bleiben ohne lokale Prosa unbestimmt.",
        "tech": assumptions(PROCESS_STEP=1, PRODUCT_FUNCTION=1),
        "med": assumptions(PROCESS_STEP=1, CONTAINER_OR_TARGET=1, PRODUCT_FUNCTION=1),
    },
    "H2-S001": {
        "reading": "Oberteile derselben Bildpflanze als H2-R01 sammeln, quetschen und pressen; Flüssigkeit als aktiven Ansatz führen, mit Wasser nachziehen und nach Sollmenge buchen.",
        "winner": "TECHNICAL",
        "reason": "Aktiver Ansatz und Sollmaß ergeben eine saubere Chargeneröffnung; ein äußerlicher Arzneizweck erscheint hier noch nicht.",
        "contradiction": "Oberteile, Pressen und Wasser sind nicht kartengebunden.",
        "tech": assumptions(PART_OR_HARVEST=1, PROCESS_STEP=3, MEDIUM_OR_ADDITIVE=1, PRODUCT_FUNCTION=1),
        "med": assumptions(PART_OR_HARVEST=2, PROCESS_STEP=2, PRODUCT_FUNCTION=1),
    },
    "H2-S002": {
        "reading": "Frühe Erntefraktion H2-R03 an den laufenden Ansatz binden, vorige Charge wieder aufnehmen, Sollmenge abteilen und als Vergleichsmazerat führen.",
        "winner": "TECHNICAL",
        "reason": "Drei Linkoperationen, VORIGES? und MASS? passen unmittelbar zu einer Chargenvergleichsbuchung.",
        "contradiction": "Die frühe Erntefraktion ist ein lokaler, nicht formaler Wert.",
        "tech": assumptions(PART_OR_HARVEST=1, PROCESS_STEP=1, PRODUCT_FUNCTION=1),
        "med": assumptions(PART_OR_HARVEST=2, PRODUCT_FUNCTION=1),
    },
    "H2-S003": {
        "reading": "Späte Erntefraktion als parallelen Ansatz führen, beide Auszüge gleich seihen, Farbe und Bodensatz vergleichen und verschlossen lagern.",
        "winner": "TIE",
        "reason": "Parallele Ansätze sind formal passend, aber Erntezeit und Vergleich ebenso still wie Öl und äußerlicher Gebrauch der medizinischen Fassung.",
        "contradiction": "Kein exakter Trigger bezeichnet Vergleich, Farbe oder Lagerung.",
        "tech": assumptions(PART_OR_HARVEST=1, PROCESS_STEP=2, STORAGE_CONDITION=1, PRODUCT_FUNCTION=1),
        "med": assumptions(PART_OR_HARVEST=1, PROCESS_STEP=1, MEDIUM_OR_ADDITIVE=1, STORAGE_CONDITION=1, PRODUCT_FUNCTION=1),
    },
    "H3-S001": {
        "reading": "Blüten-/Krautlos sammeln, sortieren, quetschen, in Wasser mazerieren und zweimal seihen; am KLAR?-Gate schließen und das Filtrat absetzen lassen.",
        "winner": "TIE",
        "reason": "Klarheitsgate und Feldschluss tragen ein Filtrat, nicht aber dessen medizinischen oder technischen Zweck.",
        "contradiction": "Farbextraktfunktion und zweimaliges Seihen sind lokale Expansionen.",
        "tech": assumptions(PART_OR_HARVEST=2, PROCESS_STEP=4, MEDIUM_OR_ADDITIVE=1, PRODUCT_FUNCTION=1),
        "med": assumptions(PART_OR_HARVEST=3, PROCESS_STEP=3, PRODUCT_FUNCTION=1),
    },
    "H3-S002": {
        "reading": "Einen Blütenkopf als Referenzfraktion H3-R02 zurücklegen und offen weiterführen.",
        "winner": "TECHNICAL",
        "reason": "Ein einstelliger offener Posten funktioniert sparsamer als Materialreserve denn als vollständige Heilanweisung.",
        "contradiction": "Das einzige Ereignis ist EXEMPLAR_ONLY; selbst ‚zurücklegen‘ ist unbelegt.",
        "tech": assumptions(PART_OR_HARVEST=1, STORAGE_CONDITION=1, PRODUCT_FUNCTION=1),
        "med": assumptions(PART_OR_HARVEST=1, STORAGE_CONDITION=1, PRODUCT_FUNCTION=1),
    },
    "H3-S003": {
        "reading": "Klarfiltrat aufnehmen, auf drei Probengläser verteilen, Farbe und Niederschlag notieren und das Sollmaß je Glas buchen.",
        "winner": "IATROMEDICAL",
        "reason": "MASS? trägt nur das Maß; Probengläser und Farbe kosten mehr Zusatzannahmen als die im Herbal-Kontext erwartbare lokale Anwendung.",
        "contradiction": "Kein ACTION-Trigger trägt Dosieren oder Prüfen.",
        "tech": assumptions(PROCESS_STEP=2, CONTAINER_OR_TARGET=1, PRODUCT_FUNCTION=1),
        "med": assumptions(PROCESS_STEP=1, CONTAINER_OR_TARGET=1, PRODUCT_FUNCTION=1),
    },
    "H3-S004": {
        "reading": "Blattfraktion warm ausziehen, am BEREIT?-Gate freigeben und getrennt von der Referenzblüte verwahren.",
        "winner": "IATROMEDICAL",
        "reason": "BEREIT? passt beiden; das sichtbare Herbal-Genre macht eine Auflage etwas günstiger als eine unbebilderte Materialprobenserie.",
        "contradiction": "Blattfraktion, Wärme und Lagerung sind nicht in den Kartenwerten enthalten.",
        "tech": assumptions(PART_OR_HARVEST=1, PROCESS_STEP=2, STORAGE_CONDITION=1, PRODUCT_FUNCTION=1),
        "med": assumptions(PART_OR_HARVEST=1, PROCESS_STEP=2, CONTAINER_OR_TARGET=1, PRODUCT_FUNCTION=1),
    },
    "H4-S001": {
        "reading": "Standardposten H4-R01 und Sollmaß setzen, breite Blätter waschen, schneiden und in Wasser mazerieren; erste Blattflotte absetzen und schließen.",
        "winner": "TECHNICAL",
        "reason": "Doppelte Parametersetzung plus Terminalfeld ist eine klare Chargeneröffnung mit Commit.",
        "contradiction": "Die Blattflotte und das Mazerationsmedium bleiben lokale Werte.",
        "tech": assumptions(PART_OR_HARVEST=1, PROCESS_STEP=3, MEDIUM_OR_ADDITIVE=1, PRODUCT_FUNCTION=1),
        "med": assumptions(PART_OR_HARVEST=1, PROCESS_STEP=2, MEDIUM_OR_ADDITIVE=1, PRODUCT_FUNCTION=1),
    },
    "H4-S002": {
        "reading": "Sollmenge aus H4-P01 abteilen, weichen Blattrest heben, pressen, Flüssigkeit seihen und beide Fraktionen schließen.",
        "winner": "TECHNICAL",
        "reason": "Maß, neuer Zielregisterwert und Terminal passen besser zu einer gebuchten Fraktion als zu einer stillen Wundstelle.",
        "contradiction": "Pressen und die Zweifraktionsanalyse sind exemplarisch, nicht lexikalisch.",
        "tech": assumptions(PROCESS_STEP=2, CONTAINER_OR_TARGET=1, PRODUCT_FUNCTION=1),
        "med": assumptions(PROCESS_STEP=1, CONTAINER_OR_TARGET=1, PRODUCT_FUNCTION=1),
    },
    "H4-S003": {
        "reading": "Zweite Blattfraktion mit frischem Wasser waschen, warm mazerieren, seihen und als Parallelposten schließen.",
        "winner": "TECHNICAL",
        "reason": "Der neue aktive Posten und sofortige Commit bilden eine saubere Parallelcharge, obwohl alle vier Ereignisse ungeparst sind.",
        "contradiction": "Das ganze Feld ist UNPARSED; der technische Gewinn stammt nur aus Recordform und V62-Zustand.",
        "tech": assumptions(PART_OR_HARVEST=1, PROCESS_STEP=3, MEDIUM_OR_ADDITIVE=1, PRODUCT_FUNCTION=1),
        "med": assumptions(PROCESS_STEP=2, MEDIUM_OR_ADDITIVE=1, PRODUCT_FUNCTION=1),
    },
    "H4-S004": {
        "reading": "Sollmenge der zweiten Flotte buchen, opaken Relationsslot setzen, beide Fraktionen vergleichen, aktiven Ansatz aufnehmen und als Paarposten lagern.",
        "winner": "TIE",
        "reason": "Parameter, Relation und Ansatz tragen die Buchung, aber weder Paarlager noch frische Arznei ist formal ausgezeichnet.",
        "contradiction": "Der Relationsslot darf nicht als Gefäß- oder Mischwort gelesen werden.",
        "tech": assumptions(PROCESS_STEP=2, CONTAINER_OR_TARGET=1, STORAGE_CONDITION=1, PRODUCT_FUNCTION=1),
        "med": assumptions(PROCESS_STEP=1, CONTAINER_OR_TARGET=1, STORAGE_CONDITION=1, PRODUCT_FUNCTION=1),
    },
    "H5-S001": {
        "reading": "Drüsiges Feuchtlandmaterial sammeln, kleine Krautfraktion nach Sollmaß einweichen und quetschen; klebrige Prüfcharge auf eine Fläche einsetzen und danach die Zieladresse nachtragen.",
        "winner": "TECHNICAL",
        "reason": "MASS?–ANWENDEN?–ZIEL? und das klebrige Bildmerkmal ergeben einen konkreten Materialtest ohne Krankheitsannahme.",
        "contradiction": "Mucilage und Prüffläche sind Bild-/Recordargumente; ACTION vor TARGET ist notational auffällig.",
        "tech": assumptions(PART_OR_HARVEST=2, PROCESS_STEP=3, MEDIUM_OR_ADDITIVE=1, CONTAINER_OR_TARGET=1, PRODUCT_FUNCTION=1),
        "med": assumptions(PART_OR_HARVEST=2, PROCESS_STEP=2, MEDIUM_OR_ADDITIVE=1, CONTAINER_OR_TARGET=1, PRODUCT_FUNCTION=1),
    },
    "H5-S002": {
        "reading": "Aktive Mucilagecharge auf eine zweite Prüffläche einsetzen, lufttrocknen lassen und schließen.",
        "winner": "TECHNICAL",
        "reason": "ANWENDEN? plus Terminal bildet einen knappen Auftrag/Commit; Habitat und Pflaster der medizinischen Fassung benötigen zusätzliche Füllung.",
        "contradiction": "Beschichtung und zweite Fläche sind stille Zielargumente.",
        "tech": assumptions(PROCESS_STEP=1, CONTAINER_OR_TARGET=1, PRODUCT_FUNCTION=1),
        "med": assumptions(PART_OR_HARVEST=1, PROCESS_STEP=1, CONTAINER_OR_TARGET=1, PRODUCT_FUNCTION=1),
    },
    "H5-S003": {
        "reading": "Kopf- und Blattfraktion getrennt eröffnen, mit Loszeichen versehen und schattentrocken lagern.",
        "winner": "TIE",
        "reason": "Teiletrennung und Trocknung passen zu Rohstoff- wie Arzneivorrat; das Feld ist vollständig ungeparst.",
        "contradiction": "Alle vier Operationswörter stammen aus dem lokalen Recordmodell.",
        "tech": assumptions(PART_OR_HARVEST=2, PROCESS_STEP=1, STORAGE_CONDITION=1, PRODUCT_FUNCTION=1),
        "med": assumptions(PART_OR_HARVEST=2, PROCESS_STEP=1, STORAGE_CONDITION=1, PRODUCT_FUNCTION=1),
    },
    "H5-S004": {
        "reading": "Getrocknete Blattfraktion wieder aufnehmen, einem Lagerfach zuweisen und trocken verwahren.",
        "winner": "IATROMEDICAL",
        "reason": "V62 trägt Resume und neues Ziel, aber das ungeparste Feld bietet keinen technischen Produktzweck; der Herbal-Kontext bevorzugt Vorrat für späteren Gebrauch.",
        "contradiction": "Lagerfach und Trockenbedingung sind lokale Ergänzungen.",
        "tech": assumptions(CONTAINER_OR_TARGET=1, STORAGE_CONDITION=1, PRODUCT_FUNCTION=1),
        "med": assumptions(CONTAINER_OR_TARGET=1, STORAGE_CONDITION=1, PRODUCT_FUNCTION=1, DISEASE_OR_BODY=1),
    },
    "H5-S005": {
        "reading": "Frischen Pflanzenrest als neue Charge einführen, mit Wasser anfeuchten, zu gleichmäßiger Klebmasse arbeiten und bedeckt lagern.",
        "winner": "IATROMEDICAL",
        "reason": "Der Klebmassen-Zweck ist eine zusätzliche Produktwette in einem vollständig ungeparsten Feld; Honigmischung bleibt im Herbal-Kontext mindestens ebenso plausibel.",
        "contradiction": "Binder, Wasser und Topf sind unlizenzierte lokale Werte.",
        "tech": assumptions(PROCESS_STEP=2, MEDIUM_OR_ADDITIVE=1, STORAGE_CONDITION=1, PRODUCT_FUNCTION=1),
        "med": assumptions(PROCESS_STEP=1, MEDIUM_OR_ADDITIVE=1, PRODUCT_FUNCTION=1),
    },
    "H5-S006": {
        "reading": "Bezeichnete Blütenfraktion wählen, als neues Referenzlos einführen und das Sollmaß buchen.",
        "winner": "TIE",
        "reason": "ANTEIL? und MASS? tragen Auswahl und Maß, nicht aber Referenzlos oder Arzneidosis.",
        "contradiction": "Die Blüte ist sichtbares Argument; ihre Funktion bleibt ungeklärt.",
        "tech": assumptions(PART_OR_HARVEST=1, STORAGE_CONDITION=1, PRODUCT_FUNCTION=1),
        "med": assumptions(PART_OR_HARVEST=1, PRODUCT_FUNCTION=1),
    },
}


RECORD_PLAN = {
    "H1": {
        "input": "skabiosen-/Teufelsabbiss-naher Wiesenpflanzen-Wurzelstock",
        "product": "H1-P01/H1-P02 Wurzelauszug für Materialprüfung + H1-R02 Trockenreserve",
        "article": "Vom sichtbaren Wiesenpflanzen-Los den unteren Wurzelstock sammeln, gründlich waschen, auslesen und schneiden. Das Schnittgut in Wasser mazerieren. Eine aktive Prüfportion am Musterstreifen einsetzen und das vorgesehene Maß buchen; den trockenen Rest als Reserve verwahren. Für die zweite Buchung den gelagerten Rest aufnehmen, den Auszug gelinde erwärmen, formal an den laufenden Arbeitsstand verknüpfen und als bereit freigeben.",
        "winner": "IATROMEDICAL",
        "why": "Die technische Folge ist ausführbar, doch Materialprüfstreifen und Endzweck sind zusätzlich; V53 besitzt für Abiss-Wasser den besseren Herbal-Kontext.",
        "contradiction": "Kein sichtbares Arbeitsgerät oder Produktziel weist auf Färben oder Materialprüfung.",
        "nodes": "H1:OWNER|H1-R01|F001|H1-P01+H1-R02|F002|H1-P02",
        "edges": "OWNER->COLLECT_ROOT->WASH->CUT->MACERATE->APPLY_TEST->ASSIGN_MEASURE->STORE_REST->RESUME->LINK_ACTIVE->READY_GATE",
        "commits": "NONE_OBSERVED;F001_OPEN;F002_OPEN",
    },
    "H2": {
        "input": "obere Teile derselben skabiosenartigen Bildpflanze",
        "product": "H2-P01 Pressauszug + H2-P02/H2-P03 frühe/späte Vergleichsserie",
        "article": "Obere Pflanzenteile als Rohlos sammeln, quetschen und pressen; die Flüssigkeit als aktiven Ansatz führen, mit Wasser nachziehen und nach Sollmenge buchen. Eine frühe Fraktion an den laufenden Ansatz binden, die vorige Charge wieder aufnehmen und als Vergleich mazerieren. Eine späte Fraktion parallel führen, beide Auszüge gleich seihen, Farbe und Bodensatz vergleichen und das Paar verschlossen lagern.",
        "winner": "TECHNICAL_INTERNAL_ONLY",
        "why": "Drei offene Felder, wiederholtes LINK_ACTIVE, VORIGES? und MASS? ergeben eine besonders saubere Chargenvergleichsfolge; der Produktzweck bleibt dennoch hypothetisch.",
        "contradiction": "Früh/spät, Wasser und Farbvergleich sind nicht aus Karten oder Bild sicher abzulesen.",
        "nodes": "H2:OWNER|F003|H2-P01|F004|H2-P02|F005|H2-P02+H2-P03",
        "edges": "OWNER->COLLECT_TOPS->PRESS->ASSIGN_MEASURE->SELECT_EARLY->LINK_PREVIOUS->MACERATE->SELECT_LATE->PARALLEL_LINK->STRAIN_EQUAL->COMPARE->STORE",
        "commits": "NONE_OBSERVED;F003_OPEN;F004_OPEN;F005_OPEN",
    },
    "H3": {
        "input": "kleine Schattenpflanze, Veilchen als Leitbild",
        "product": "H3-P01 geklärte Probenserie + H3-P02 Blattauszug + H3-R02 Referenzblüte",
        "article": "Junge oberirdische Teile der sichtbaren Schattenpflanze sammeln, Blüten und Blätter trennen, die Krautfraktion quetschen, in Wasser mazerieren und zweimal seihen. Am Klarheitsgate das Filtrat schließen und absetzen lassen. Einen Blütenkopf als Referenz zurücklegen. Das Filtrat auf gleiche Probengläser verteilen und je Sollmaß buchen. Die Blattfraktion warm ausziehen, als bereit markieren und getrennt verwahren.",
        "winner": "IATROMEDICAL",
        "why": "Der technische Filtrationskern ist stark, aber Farbe, Probengläser und Referenzsystem sind zusätzliche Produktannahmen; Veilchen-/Auflagenmechanismen passen besser zum sichtbaren Herbal-Rahmen.",
        "contradiction": "Nur KLAR?, MASS? und BEREIT? sind lizenziert; selbst die Produktklasse bleibt unbestimmt.",
        "nodes": "H3:OWNER|F006|H3-P01|F007|H3-R02|F008|H3-T03|F009|H3-P02",
        "edges": "OWNER->COLLECT_AND_SORT->MACERATE->DOUBLE_STRAIN->CLEAR_GATE_COMMIT->RESERVE_FLOWER->DOSE_SAMPLES->ASSIGN_MEASURE->EXTRACT_LEAF->READY_GATE->STORE_SEPARATE",
        "commits": "F006_TERMINAL;F007_OPEN;F008_OPEN;F009_OPEN",
    },
    "H4": {
        "input": "breitblättriges Kraut; Allium/Wegerich unentschieden",
        "product": "H4-P01/H4-P03 Blattflotten + H4-P02 Presskuchen, als H4-P04 Paarposten",
        "article": "Einen Standardposten breiter Blätter und sein Sollmaß buchen, die Blätter waschen, schneiden und in Wasser mazerieren; die erste Flotte absetzen und schließen. Eine Sollmenge abteilen, den weichen Rest pressen und die Flüssigkeit seihen. Eine zweite Blattfraktion parallel waschen, warm mazerieren, seihen und schließen. Danach die zweite Sollmenge, einen opaken Relationsslot und den aktiven Ansatz buchen, beide Fraktionen vergleichen, etikettieren und bedeckt lagern.",
        "winner": "TECHNICAL_INTERNAL_ONLY",
        "why": "Drei aufeinanderfolgende Commits, zwei Parameterposten und ein abschließender Fraktionslink bilden das stärkste technische Chargenregister der fünf Records.",
        "contradiction": "Nutzfunktion von Blattflotte und Presskuchen sowie Wasser, Wärme und Gefäß sind nicht sichtbar festgelegt.",
        "nodes": "H4:OWNER|F010|H4-P01|F011|H4-P02|F012|H4-P03|F013|H4-P04",
        "edges": "OWNER->STANDARD_SLOT->ASSIGN_MEASURE->WASH_AND_MACERATE->COMMIT_LIQUOR1->SEPARATE_AND_PRESS->COMMIT_CAKE->PARALLEL_WASH_AND_STRAIN->COMMIT_LIQUOR2->TARGET_SLOT->LINK_ACTIVE->COMPARE_AND_STORE_PAIR",
        "commits": "F010_TERMINAL;F011_TERMINAL;F012_TERMINAL;F013_OPEN",
    },
    "H5": {
        "input": "feuchtlandliebende drüsige/borstige Pflanze; Sonnentau als enger Rivale",
        "product": "H5-P01 Mucilage-Beschichtungsprobe + H5-P02 frische Klebmasse + trockene Teile-/Referenzlose",
        "article": "Eine kleine Probe des sichtbaren drüsigen Feuchtlandmaterials sammeln, Wurzel und Kraut trennen und die Krautmenge buchen. Das Kraut in wenig Wasser einweichen und quetschen, die klebrige Flüssigkeit als Prüfcharge auffangen, auf eine Prüffläche einsetzen und danach die Zieladresse eintragen. Eine zweite Beschichtung ausführen und trocknend schließen. Kopf und Blatt getrennt trocknen und das Blatt einem Lagerfach zuweisen. Frischen Rest zu einer Klebmasse arbeiten und bedeckt lagern. Schließlich die bezeichnete Blütenfraktion wählen und ihr Sollmaß buchen.",
        "winner": "TIE",
        "why": "Drüsig-klebriges Bild, ANWENDEN? und ZIEL? machen den Binder-/Beschichtungstest konkret; die medizinische Sonnentau-Lesung besitzt jedoch den stärkeren historischen Herbal-Prior und beide Editionen füllen drei ganze UNPARSED-Aussagen.",
        "contradiction": "Mucilage, Klebmasse und Prüfflächen sind unbebilderte Produktannahmen; ACTION_APPLY steht vor TARGET_ASSIGN.",
        "nodes": "H5:OWNER|F014|H5-R01|F015|H5-P01@T01|F016|H5-P01@T02|F017|H5-R02+R03|F018|H5-R03@T04|F019|H5-P02|F020|H5-R05",
        "edges": "OWNER->COLLECT_AND_PART->ASSIGN_MEASURE->SOAK_AND_PRESS->APPLY_TEST->ASSIGN_TARGET_AFTER_ACTION->APPLY_SECOND->DRY_COMMIT->SEPARATE_PARTS->DRY_STORE->RESUME_TO_STORAGE->INTRODUCE_FRESH_RESIDUE->MAKE_BINDER->SELECT_FLOWER_PART->ASSIGN_MEASURE",
        "commits": "F014_OPEN;F015_OPEN;F016_TERMINAL;F017_OPEN;F018_OPEN;F019_OPEN;F020_OPEN",
    },
}


def main() -> None:
    articles = read_tsv(SOURCE_ARTICLES)
    decisions = read_tsv(SOURCE_DECISIONS)
    all_events = read_tsv(SOURCE_EVENTS)
    all_statements = read_tsv(SOURCE_STATEMENTS)
    all_machine = read_tsv(SOURCE_MACHINE)
    all_parse_events = read_tsv(SOURCE_PARSE_EVENTS)
    all_parse_fields = read_tsv(SOURCE_PARSE_FIELDS)
    all_parse_statements = read_tsv(SOURCE_PARSE_STATEMENTS)

    require((len(articles), len(decisions), len(all_events), len(all_statements), len(all_machine), len(all_parse_events), len(all_parse_fields), len(all_parse_statements)) == (5, 11, 381, 116, 116, 381, 135, 116), "selected source counts changed")
    require(Counter(row["parse_status"] for row in all_parse_fields) == Counter({"UNIQUE": 14, "AMBIGUOUS": 56, "UNPARSED": 65}), "V63 overall field constraint changed")

    events = [row for row in all_events if herbal(row)]
    statements = [row for row in all_statements if herbal(row)]
    machine = [row for row in all_machine if herbal(row)]
    parse_events = [row for row in all_parse_events if herbal(row)]
    parse_fields = [row for row in all_parse_fields if herbal(row)]
    parse_statements = [row for row in all_parse_statements if herbal(row)]
    require((len(events), len(statements), len(machine), len(parse_events), len(parse_fields), len(parse_statements)) == (100, 19, 19, 100, 20, 19), "Herbal scope changed")
    require(Counter(row["parse_status"] for row in parse_fields) == Counter({"AMBIGUOUS": 15, "UNPARSED": 5}), "Herbal field statuses changed")
    require(Counter(row["parse_status"] for row in parse_statements) == Counter({"AMBIGUOUS": 14, "UNPARSED": 5}), "Herbal statement statuses changed")
    require(set(FIELD_EVENT_FILLERS) == set(FIELD_PLAN) == {row["field_id"] for row in parse_fields}, "field plans incomplete")
    require(set(STATEMENT_PLAN) == {row["statement_id"] for row in parse_statements}, "statement plans incomplete")
    require(set(RECORD_PLAN) == {row["article_id"] for row in articles}, "record plans incomplete")

    article_by_id = {row["article_id"]: row for row in articles}
    source_event_by_serial = {row["event_serial"]: row for row in events}
    parse_event_by_serial = {row["event_serial"]: row for row in parse_events}
    statement_by_id = {row["statement_id"]: row for row in statements}
    machine_by_id = {row["statement_id"]: row for row in machine}
    parse_statement_by_id = {row["statement_id"]: row for row in parse_statements}

    events_by_field: dict[str, list[dict[str, str]]] = defaultdict(list)
    events_by_record: dict[str, list[dict[str, str]]] = defaultdict(list)
    for event in events:
        events_by_field[event["field_id"]].append(event)
        events_by_record[event["record_unit_id"]].append(event)
    for field_id, fillers in FIELD_EVENT_FILLERS.items():
        require(len(fillers) == len(events_by_field[field_id]), f"event filler count mismatch: {field_id}")

    event_rows: list[dict[str, str]] = []
    for event in events:
        parsed = parse_event_by_serial[event["event_serial"]]
        filler = FIELD_EVENT_FILLERS[event["field_id"]][events_by_field[event["field_id"]].index(event)]
        mnemonic = parsed["selected_exact_mnemonic"]
        formal = parsed["strict_formal_prompt"]
        exact_clause = FIXED_VALUE_CLAUSE.get(mnemonic, "NONE")
        formal_clause = f"{formal}=FORMAL_OPAQUE_SLOT_OPERATION" if formal != "NONE" else "NONE"
        if mnemonic != "UNKNOWN" and formal != "NONE":
            source_class = "V60_EXACT_VALUE+V63_FORMAL_CHANNEL_SEPARATE+V53/V64_LOCAL_ARGUMENT"
        elif mnemonic != "UNKNOWN":
            source_class = "V60_EXACT_VALUE+V53/V64_LOCAL_ARGUMENT"
        elif formal != "NONE":
            source_class = "V63_FORMAL_CHANNEL_NO_SEMANTIC_WORD+V53/V64_LOCAL_ARGUMENT"
        else:
            source_class = "V53_VISIBLE_OWNER_OR_V64_RECORD_LOCAL_HYPOTHESIS;NOT_CARD_MEANING"
        clauses = [clause for clause in (exact_clause, formal_clause, f"LOCAL[{filler}]") if clause != "NONE"]
        field_source = next(row for row in parse_fields if row["field_id"] == event["field_id"])
        machine_source = machine_by_id[field_source["statement_id"]]
        event_rows.append(
            {
                "event_serial": event["event_serial"],
                "page": event["page"],
                "locus": event["locus"],
                "record_unit_id": event["record_unit_id"],
                "field_id": event["field_id"],
                "statement_id": field_source["statement_id"],
                "joint_tuple_id_opaque": event["joint_tuple_id"],
                "surface_display_only": event["surface"],
                "formal_formula_opaque": event["formal_formula_opaque"],
                "terminal_status": event["terminal_status"],
                "fixed_exact_mnemonic": mnemonic,
                "strict_formal_prompt": formal,
                "event_template": parsed["event_template"],
                "event_parse_status": parsed["event_parse_status"],
                "fixed_value_clause": exact_clause,
                "formal_clause_no_semantic_inheritance": formal_clause,
                "v64_local_plant_filler": filler,
                "complete_layered_technical_reading": " ; ".join(clauses),
                "local_filler_source_class": source_class,
                "local_input_id": FIELD_PLAN[event["field_id"]][0],
                "local_output_id": FIELD_PLAN[event["field_id"]][1],
                "statement_pre_state": machine_source["pre_state"],
                "statement_post_state": machine_source["post_state"],
                "iatromedical_comparator_event": event["LOCAL_IATROMEDICAL_EXPANSION"],
                "opaque_roundtrip_atom": parsed["opaque_roundtrip_atom"],
                "noninheritance_contract": "EXACT_TUPLE_ATOMIC;EXACT_VALUE_FIXED;FORMAL_PROMPT_NO_SEMANTIC_WORD;LOCAL_FILLER_NEVER_CARD_GLOSS",
                "source_lineage": "V53_VISUAL+V60_SELECTED_EVENT+V61/V62_STATE+V63_SELECTED_PARSE>V64_R3_LOCAL_PLANT_EDITION",
            }
        )

    field_rows: list[dict[str, str]] = []
    for parsed_field in parse_fields:
        field_id = parsed_field["field_id"]
        source_field_events = events_by_field[field_id]
        input_id, output_id, reading, contradiction = FIELD_PLAN[field_id]
        plan = STATEMENT_PLAN[parsed_field["statement_id"]]
        field_rows.append(
            {
                "field_id": field_id,
                "record_unit_id": parsed_field["record_unit_id"],
                "page": parsed_field["page"],
                "locus": parsed_field["locus"],
                "statement_id": parsed_field["statement_id"],
                "field_position_in_statement": parsed_field["field_position_in_statement"],
                "event_count": parsed_field["event_count"],
                "event_serials": parsed_field["event_serials"],
                "v63_primary_template": parsed_field["primary_template"],
                "v63_ordered_template_sequence": parsed_field["ordered_event_template_sequence"],
                "v63_parse_status_fixed": parsed_field["parse_status"],
                "recognized_event_count": parsed_field["recognized_event_count"],
                "exemplar_only_event_count": parsed_field["exemplar_only_event_count"],
                "register_pre_state_statement_envelope": parsed_field["register_pre_state_statement_envelope"],
                "register_post_state_statement_envelope": parsed_field["register_post_state_statement_envelope"],
                "local_plant_input": input_id,
                "complete_technical_field_reading": reading,
                "local_plant_output": output_id,
                "iatromedical_field_comparator": " ; ".join(event["LOCAL_IATROMEDICAL_EXPANSION"] for event in source_field_events),
                "comparison_winner_from_statement": plan["winner"],
                "strongest_technical_contradiction": contradiction,
                "opaque_roundtrip_trace": parsed_field["opaque_roundtrip_trace"],
                "roundtrip_status": parsed_field["roundtrip_status"],
                "layer_contract": "V63_STATUS_UNCHANGED;V62_ENVELOPE_UNCHANGED;V64_WORDS_LOCAL_ONLY",
                "source_lineage": "V60_SELECTED_EVENTS>V63_SELECTED_FIELD_PARSE>V64_R3_PLANT_FIELD",
            }
        )

    statement_rows: list[dict[str, str]] = []
    for source_statement in statements:
        statement_id = source_statement["statement_id"]
        parsed_statement = parse_statement_by_id[statement_id]
        source_machine = machine_by_id[statement_id]
        plan = STATEMENT_PLAN[statement_id]
        statement_rows.append(
            {
                "statement_id": statement_id,
                "record_unit_id": source_statement["record_unit_id"],
                "page": source_statement["page"],
                "constituent_fields": source_statement["constituent_fields"],
                "event_count": source_statement["event_count"],
                "event_serials": source_statement["event_serials"],
                "closure_sequence": source_statement["closure_sequence"],
                "v63_parse_status_fixed": parsed_statement["parse_status"],
                "v63_ordered_template_sequence": parsed_statement["ordered_event_template_sequence"],
                "pre_state": source_machine["pre_state"],
                "owner_operation": source_machine["owner_operation"],
                "active_item_preparation_operation": source_machine["active_item_preparation_operation"],
                "target_station_operation": source_machine["target_station_operation"],
                "previous_item_operation": source_machine["previous_item_operation"],
                "post_state": source_machine["post_state"],
                "complete_technical_plant_reading": plan["reading"],
                "complete_iatromedical_comparator": source_statement["concrete_workshop_reading"],
                "technical_assumptions": encode_assumptions(plan["tech"]),
                "technical_weighted_cost": str(assumption_cost(plan["tech"])),
                "iatromedical_assumptions": encode_assumptions(plan["med"]),
                "iatromedical_weighted_cost": str(assumption_cost(plan["med"])),
                "coherence_winner": plan["winner"],
                "comparison_reason": plan["reason"],
                "strongest_technical_contradiction": plan["contradiction"],
                "opaque_roundtrip_trace": parsed_statement["opaque_roundtrip_trace"],
                "roundtrip_status": parsed_statement["roundtrip_status"],
                "comparison_contract": "SAME_SOURCE_STATEMENT+SAME_V60_VALUES+SAME_V62_STATE+SAME_V63_STATUS;ONLY_LOCAL_EDITION_DIFFERS",
                "source_lineage": "V61_SELECTED_STATEMENT>V62_SELECTED_MACHINE>V63_SELECTED_PARSE>V64_R3_DUAL_READING",
            }
        )

    statement_rows_by_record: dict[str, list[dict[str, str]]] = defaultdict(list)
    fields_by_record: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in statement_rows:
        statement_rows_by_record[row["record_unit_id"]].append(row)
    for row in field_rows:
        fields_by_record[row["record_unit_id"]].append(row)

    record_rows: list[dict[str, str]] = []
    graph_rows: list[dict[str, str]] = []
    cost_rows: list[dict[str, str]] = []
    for article in articles:
        record = article["article_id"]
        plan = RECORD_PLAN[record]
        record_events = events_by_record[record]
        record_fields = fields_by_record[record]
        record_statements = statement_rows_by_record[record]
        status_counts = Counter(row["v63_parse_status_fixed"] for row in record_fields)
        statement_winners = Counter(row["coherence_winner"] for row in record_statements)
        technical_cost = sum(int(row["technical_weighted_cost"]) for row in record_statements)
        medical_cost = sum(int(row["iatromedical_weighted_cost"]) for row in record_statements)
        terminal_fields = [row["field_id"] for row in record_fields if any(source_event_by_serial[serial]["terminal_status"] == "TERMINAL" for serial in row["event_serials"].split("|"))]
        record_rows.append(
            {
                "record_unit_id": record,
                "folio_record": article["folio_record"],
                "best_visible_plant_category_fixed": article["pictured_owner_default"],
                "strongest_visual_rival_fixed": article["pictured_owner_rival"],
                "field_count": str(len(record_fields)),
                "statement_count": str(len(record_statements)),
                "event_count": str(len(record_events)),
                "recognized_event_count": str(sum(parse_event_by_serial[event["event_serial"]]["event_template"] != "EXEMPLAR_ONLY" for event in record_events)),
                "field_status_summary": ";".join(f"{key}={status_counts[key]}" for key in ("UNIQUE", "AMBIGUOUS", "UNPARSED")),
                "technical_plant_input": plan["input"],
                "technical_product": plan["product"],
                "complete_technical_plant_article": plan["article"],
                "complete_iatromedical_article": article["selected_complete_working_translation_German"],
                "terminal_commit_fields": "|".join(terminal_fields) if terminal_fields else "NONE",
                "statement_winner_summary": ";".join(f"{key}={statement_winners[key]}" for key in ("TECHNICAL", "IATROMEDICAL", "TIE")),
                "technical_weighted_assumption_cost": str(technical_cost),
                "iatromedical_weighted_assumption_cost": str(medical_cost),
                "record_coherence_winner": plan["winner"],
                "coherence_reason": plan["why"],
                "strongest_technical_contradiction": plan["contradiction"],
                "visual_binding_contract": "VISIBLE_CATEGORY_IS_OWNER_ARGUMENT_ONLY;NEVER_CARD_GLOSS;BOTANICAL_IDENTITY_UNRESOLVED",
                "source_lineage": "V53_SELECTED_VISUAL_AND_IATRO_ARTICLE+V60-V63_SELECTED>V64_R3_TECHNICAL_PLANT_ARTICLE",
            }
        )
        field_path = "|".join(row["field_id"] for row in record_fields)
        graph_rows.append(
            {
                "record_unit_id": record,
                "field_path": field_path,
                "node_path": plan["nodes"],
                "operation_edge_path": plan["edges"],
                "observed_commit_points": plan["commits"],
                "initial_register_state": machine_by_id[record_statements[0]["statement_id"]]["pre_state"],
                "final_register_state": machine_by_id[record_statements[-1]["statement_id"]]["post_state"],
                "execution_rule": "FOLLOW_FIELD_PATH;APPLY_V62_STATEMENT_TRANSITION;EXECUTE_LICENSED_V63_TEMPLATE;EXPAND_EXEMPLAR_LOCALLY;COMMIT_ONLY_OBSERVED_TERMINAL",
                "graph_status": "COMPLETE_RECORD_GRAPH_LOCAL_HYPOTHESIS",
                "source_lineage": "V61_ORDER+V62_TRANSITIONS+V63_TEMPLATES>V64_R3_PROCESS_GRAPH",
            }
        )
        for model, total in (("TECHNICAL_PLANT_REGISTER", technical_cost), ("IATROMEDICAL", medical_cost)):
            combined: Counter[str] = Counter()
            key = "tech" if model == "TECHNICAL_PLANT_REGISTER" else "med"
            for source_statement in statements:
                if source_statement["record_unit_id"] == record:
                    combined.update(STATEMENT_PLAN[source_statement["statement_id"]][key])
            cost_rows.append(
                {
                    "record_unit_id": record,
                    "model": model,
                    "weight_contract": "PART/HARVEST=1;PROCESS=1;MEDIUM=1;CONTAINER/TARGET=1;STORAGE=1;PRODUCT_FUNCTION=2;DISEASE/BODY=2;VISIBLE_OWNER=0",
                    "assumption_counts": encode_assumptions(dict(combined)),
                    "weighted_cost": str(total),
                    "cost_scope": "SUM_OF_STATEMENT_LOCAL_FILLERS;EXACT_MNEMONICS+FORMAL_PROMPTS+V62_REGISTERS_COST_ZERO",
                    "interpretation": "EXPLORATORY_DESCRIPTION_LENGTH_PROXY_NOT_PROBABILITY",
                    "source_lineage": "V64_R3_FIXED_SYMMETRIC_COST_RUBRIC",
                }
            )

    require((len(event_rows), len(field_rows), len(statement_rows), len(record_rows), len(graph_rows), len(cost_rows)) == (100, 20, 19, 5, 5, 10), "output counts changed")
    require(Counter(row["coherence_winner"] for row in statement_rows) == Counter({"TECHNICAL": 8, "IATROMEDICAL": 5, "TIE": 6}), "statement comparison changed")
    write_tsv(OUT_EVENTS, event_rows)
    write_tsv(OUT_FIELDS, field_rows)
    write_tsv(OUT_STATEMENTS, statement_rows)
    write_tsv(OUT_RECORDS, record_rows)
    write_tsv(OUT_GRAPHS, graph_rows)
    write_tsv(OUT_COSTS, cost_rows)
    print("PASS V64 R3 build")
    print("records=5 statements=19 fields=20 events=100 graphs=5 costs=10")
    print("Herbal field status=AMBIGUOUS:15;UNPARSED:5;UNIQUE:0")
    print("statement comparison=TECHNICAL:8;IATROMEDICAL:5;TIE:6")


if __name__ == "__main__":
    main()
