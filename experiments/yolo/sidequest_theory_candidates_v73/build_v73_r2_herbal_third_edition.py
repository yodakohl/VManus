#!/usr/bin/env python3
"""Build V73 R2: complete historical Herbal third edition.

Only frozen V69 formal tables, the V70 image selection, V71 central owners and
V72 central statements are consumed.  Surface spellings and tuple coordinates
are never used to choose content.  Every German context meaning below is an
occurrence-bound historical source exemplar, not a card translation.
"""

from __future__ import annotations

import csv
import hashlib
import json
import re
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
V69 = ROOT / "experiments/yolo/sidequest_theory_candidates_v69"
V70 = ROOT / "experiments/yolo/sidequest_theory_candidates_v70"
V71 = ROOT / "experiments/yolo/sidequest_theory_candidates_v71"
V72 = ROOT / "experiments/yolo/sidequest_theory_candidates_v72"
OUT = ROOT / "experiments/yolo/sidequest_theory_candidates_v73"

EVENTS_IN = V69 / "V69_R4_FINAL_381_PROSE_EVENT_INTERLINEAR.tsv"
FIELDS_IN = V69 / "V69_R4_FINAL_135_FIELD_EDITION.tsv"
CARDS_IN = V69 / "V69_R4_FINAL_173_CARD_DICTIONARY.tsv"
V70_IMAGES = V70 / "V70_SELECTED_TEN_PAGE_IMAGE_REVISION.tsv"
V71_OWNERS = V71 / "V71_SELECTED_OWNER_LEDGER.tsv"
V72_STATEMENTS = V72 / "V72_SELECTED_116_STATEMENTS.tsv"

EVENTS_OUT = OUT / "V73_R2_100_HERBAL_EVENTS.tsv"
FIELDS_OUT = OUT / "V73_R2_20_HERBAL_FIELDS.tsv"
STATEMENTS_OUT = OUT / "V73_R2_19_HERBAL_STATEMENTS.tsv"
ARTICLES_OUT = OUT / "V73_R2_FIVE_HERBAL_ARTICLES.tsv"
NOUNS_OUT = OUT / "V73_R2_UNSUPPORTED_NOUNS.tsv"
REPORT_OUT = OUT / "V73_R2_HERBAL_THIRD_EDITION_REPORT.md"


R2_BACKGROUND = [
    "Du kennst zeitgenössische Herbarien, Materia medica, Rezeptbücher, Abkürzungen und kompilierte Sammelhandschriften.",
    "Du vergleichst Namen, Beschreibungen, Qualitäten, Habitate, Zubereitungen, Anwendungen und Rezeptfortsetzungen.",
    "Du unterscheidest überlieferte Textpraxis von modernen Tabellen-, Datenbank- oder Übersetzungsannahmen.",
    "Du darfst historische Quellen recherchieren, aber niemals Voynich-Formen über Klang oder Buchstabenähnlichkeit zuordnen.",
    "Du lieferst die historisch plausibelste Quelltextstruktur samt Gegenbelegen und eng begrenzter Pseudoübersetzung.",
]


# event_serial, exemplar role, one concrete German meaning in record context,
# explicitly unsupported nouns (pipe-separated; NONE only for the visible owner).
EVENT_EDITION_TEXT = """
1	PLANT_PART	Von der abgebildeten, unbenannten Pflanze nimm einen Teil der Wurzel.	Wurzelteil
2	ACTION	Säubere ihn.	Reinigung
3	LOCAL_LINK	Führe ihn als denselben Arbeitsansatz weiter.	Arbeitsansatz
4	ACTION	Zerschneide ihn.	Zerschneiden
5	CONTAINER_ACTION	Gib die Stücke in ein Gefäß.	Gefäß
6	MEDIUM	Gieße Quellwasser darüber.	Quellwasser
7	PREPARATION	Fange den ersten Auszug in einem Glas auf.	Auszug|Glas
8	USE	Gebrauche diesen Auszug innerlich.	Auszug|innerlicher Gebrauch
9	DOSE	Nimm davon das örtlich vorgeschriebene kleine Maß.	Dosis
10	INDICATION_AND_STORAGE	Gebrauche es bei Stechen im Leib und verwahre den übrigen Wurzelvorrat verschlossen.	Leibschmerz|Vorratsgefäß
11	PREPARATION	Nimm erneut von dem frischen ersten Auszug.	Auszug
12	ACTION_CONDITION	Erwärme ihn gelinde.	Wärme
13	LOCAL_LINK	Führe ihn als denselben laufenden Ansatz fort.	Arbeitsansatz
14	STATE_AND_USE	Sobald er zum Gebrauch bereit ist, gebrauche ihn.	Gebrauchsreife
15	PLANT_PART	Nimm die jungen Spitzen mit Blütenständen und Blättern derselben unbenannten Pflanze.	junge Spitzen|Blütenstände|Blätter
16	HARVEST_CONDITION	Sammle sie, wenn sie sich eben öffnen.	Erntezeit
17	LOCAL_LINK	Führe sie als frischen Ansatz.	Arbeitsansatz
18	ACTION	Zerstoße das Kraut.	Kraut
19	ACTION	Presse den Saft durch ein Tuch.	Pflanzensaft|Tuch
20	PREPARATION	Fange die erste Fraktion auf.	Fraktion
21	MEDIUM	Gib Olivenöl hinzu.	Olivenöl
22	DOSE	Nimm das örtlich vorgeschriebene Maß.	Dosis
23	ACTION_CONDITION	Erwärme gelinde.	Wärme
24	PLANT_PART_AND_CONDITION	Nimm vor voller Blüte eine zweite Portion der Spitzen.	junge Spitzen|Erntezeit
25	LOCAL_LINK	Führe den ersten Ansatz weiter.	Arbeitsansatz
26	DOSE	Nimm eine Handvoll.	Handvoll
27	LOCAL_LINK	Verknüpfe diese Fraktion mit dem laufenden Arbeitsstand.	Arbeitsansatz
28	LOCAL_LINK	Nimm den vorherigen Posten hinzu.	vorheriger Posten
29	LOCAL_LINK	Führe beide als neuen aktiven Posten.	Arbeitsansatz
30	DOSE	Gib von beiden das gleiche örtliche Maß.	Dosis
31	ACTION	Vereinige die beiden Fraktionen.	Fraktionen
32	CONTAINER_ACTION	Gib sie in ein glasiertes Gefäß.	glasiertes Gefäß
33	PREPARATION	Führe die Mischung als Salbenansatz.	Salbenansatz
34	PREPARATION	Der wiederholte Ansatzvermerk bestätigt hier denselben Salbenposten.	Salbenansatz
35	ACTION_CONDITION	Rühre bei kleinem Feuer.	Feuer
36	STATE	Bis eine weiche Salbe entsteht.	Salbe
37	STORAGE	Bewahre sie bedeckt.	Vorratsgefäß
38	INDICATION_AND_USE	Lege sie äußerlich auf ein Geschwür oder eine harte Schwellung.	Geschwür|Schwellung
39	PLANT_PART_AND_CONDITION	Nimm im ersten Frühjahr Blüten und junge Blätter der unbenannten Pflanze.	Frühjahr|Blüten|junge Blätter
40	MEDIUM_ACTION	Koche sie in reinem Wein.	Wein
41	ACTION_IMPLEMENT	Wring den Ansatz durch ein feines Tuch.	Tuch
42	PREPARATION	Lass den Auszug stehen.	Auszug
43	ACTION_IMPLEMENT	Seihe ihn nochmals durch ein Tuch.	Tuch
44	STATE	Warte, bis der örtlich verlangte klare Zustand erreicht ist.	Klarzustand
45	ACTION_CONDITION	Lass ihn abkühlen; damit endet der erste Posten.	Abkühlung
46	PLANT_PART_AND_STORAGE	Behalte einen Teil der frischen Blüten für eine zweite Arznei zurück.	Blüten|zweite Arznei
47	LOCAL_LINK	Nimm den ersten Auszug wieder auf.	erster Auszug
48	DOSE	Nimm davon einen Anteil.	Anteil
49	USE	Gib ihn als Trank.	Trank
50	INDICATION	Gebrauche ihn bei bedrücktem Gemüt und beschwerter Brust.	Gemütsbeschwerde|Brustbeschwerde
51	DOSE	Gib ein kleines örtliches Maß.	Dosis
52	PLANT_PART	Nimm die zurückbehaltenen Blüten.	Blüten
53	MEDIUM_ACTION	Erwärme sie in Olivenöl.	Olivenöl
54	STATE	Warte, bis der örtliche Bereitschaftszustand erreicht ist.	Gebrauchsreife
55	INDICATION_AND_USE	Streiche das Öl äußerlich um die Lider, ohne das Auge zu berühren.	Lider|Auge|äußerliches Öl
56	FORMAL_START	Setze den ersten Posten an.	Posten
57	DOSE	Nimm ein örtlich vorgeschriebenes Maß.	Dosis
58	PLANT_PART_AND_ACTION	Zerstoße breite Blätter der unbenannten Pflanze.	Blätter
59	MEDIUM	Gib Weißwein hinzu.	Weißwein
60	STORAGE_AND_CLOSE	Verschließe das Gefäß und lass es kühl stehen; damit endet der Posten.	Gefäß|kühler Lagerort
61	DOSE	Miss eine Portion des Ansatzes ab.	Dosis
62	ACTION_IMPLEMENT	Wring sie durch Leinwand und lass sie klar absetzen.	Leinwand|Klarstand
63	STORAGE_AND_CLOSE	Verwahre den klaren Auszug; damit endet der Posten.	Vorratsgefäß
64	INDICATION_AND_USE	Wasche damit eine unreine äußere Wunde.	Wunde
65	PREPARATION	Verwende dazu den klaren Auszug.	Auszug
66	FREQUENCY	Einmal oder nach örtlicher Vorschrift.	Anwendungshäufigkeit
67	FORMAL_CLOSE	Beende diesen Gebrauch.	Gebrauchsabschluss
68	PLANT_PART_AND_DOSE	Nimm ein örtliches Maß der zurückbehaltenen Blätter.	Blätter|Dosis
69	TARGET	Lege sie an die bezeichnete äußere Stelle.	äußere Zielstelle
70	ACTION_CONDITION	Erwärme sie gelinde.	Wärme
71	LOCAL_LINK	Führe sie als zweiten Ansatz.	Arbeitsansatz
72	MEDIUM	Mische sie mit Honig.	Honig
73	USE	Lege den warmen Umschlag frisch auf.	Umschlag
74	VISIBLE_OWNER	Von der abgebildeten, unbenannten Pflanze.	NONE
75	HARVEST_AND_HABITAT	Sammle das ganze oberirdische Kraut an einem feuchten Standort.	oberirdisches Kraut|feuchter Standort
76	HARVEST_CONDITION	Nimm es zu Beginn der Blüte.	Blütezeit
77	DOSE	Nimm nur ein kleines örtliches Maß.	Dosis
78	PLANT_PART_AND_ACTION	Zerstoße die frischen klebrigen Blätter.	klebrige Blätter
79	USE	Lege sie als Auflage auf.	Auflage
80	INDICATION	Auf eine einzelne Warze oder ein Hühnerauge.	Warze|Hühnerauge
81	USE_DURATION	Lass die Auflage nur kurz einwirken.	Einwirkdauer
82	TARGET	An der örtlich bezeichneten Hautstelle.	Hautstelle
83	ACTION	Nimm die Auflage wieder ab.	Auflage
84	MEDIUM_ACTION	Wasche die Stelle mit Wasser.	Wasser
85	CONDITION_AND_USE	Wiederhole den Gebrauch nur, wenn er vertragen wird.	Verträglichkeit|Wiederholung
86	FORMAL_CLOSE	Beende die äußere Anwendung.	äußere Anwendung
87	PLANT_PART	Nimm vom übrigen Kraut die blühenden Stiele.	blühende Stiele
88	STORAGE_CONDITION	Trockne sie im Schatten.	Schatten
89	ACTION	Zerreibe sie grob.	Zerreibung
90	STORAGE	Verwahre sie trocken.	Vorrat
91	PREPARATION	Setze daraus einen schwachen Auszug an.	Auszug
92	MEDIUM	Nimm milden Wein als Medium.	Wein
93	ACTION_IMPLEMENT	Seihe ihn durch ein Tuch.	Tuch
94	MEDIUM	Gib Honig hinzu.	Honig
95	ACTION_CONDITION	Erwärme gelinde.	Wärme
96	USE	Gib den Auszug als Brusttrank.	Brusttrank
97	INDICATION	Gebrauche ihn bei trockenem Husten.	Husten
98	SELECT_PART	Führe den ausgewählten Trankanteil als Gabe.	Trankanteil|Gabe
99	DOSE_FREQUENCY	Je Gabe.	Gabe
100	DOSE	Nimm ein kleines örtliches Maß.	Dosis
""".strip()


ARTICLE_FLUENT = {
    "H1": "Von der abgebildeten, unbenannten Pflanze nimm einen Teil der Wurzel; säubere und zerschneide ihn und führe ihn als denselben Arbeitsansatz. Gib die Stücke in ein Gefäß, gieße Quellwasser darüber und fange den ersten Auszug in einem Glas auf. Gebrauche davon das örtlich vorgeschriebene kleine Maß innerlich bei Stechen im Leib und verwahre den übrigen Wurzelvorrat verschlossen. Nimm erneut vom frischen Auszug, erwärme ihn gelinde, führe ihn als denselben Ansatz fort und gebrauche ihn, sobald er bereit ist.",
    "H2": "Von den jungen Spitzen derselben unbenannten Pflanze nimm Blütenstände und Blätter, wenn sie sich eben öffnen. Zerstoße das Kraut, presse den Saft durch ein Tuch, fange die erste Fraktion auf, gib Olivenöl im örtlichen Maß hinzu und erwärme gelinde. Nimm vor voller Blüte eine zweite Handvoll der Spitzen, führe den ersten Ansatz weiter, nimm den vorherigen Posten hinzu und vereinige beide Fraktionen im gleichen Maß. Gib sie in ein glasiertes Gefäß, führe sie als einen Salbenposten, rühre bei kleinem Feuer bis eine weiche Salbe entsteht, bewahre sie bedeckt und lege sie äußerlich auf ein Geschwür oder eine harte Schwellung.",
    "H3": "Von der unbenannten Pflanze nimm im ersten Frühjahr Blüten und junge Blätter, koche sie in reinem Wein, wringe sie durch ein feines Tuch, lass den Auszug stehen, seihe nochmals und lass ihn beim verlangten klaren Zustand abkühlen. Behalte frische Blüten für eine zweite Arznei zurück. Vom ersten Auszug gib ein kleines Maß als Trank bei bedrücktem Gemüt und beschwerter Brust. Die zurückbehaltenen Blüten erwärme in Olivenöl bis zum Bereitschaftszustand und streiche das Öl äußerlich um die Lider, ohne das Auge zu berühren.",
    "H4": "Von der unbenannten Pflanze setze einen ersten Posten aus einem vorgeschriebenen Maß zerstoßener breiter Blätter und Weißwein an; verschließe das Gefäß und lass es kühl stehen. Miss eine Portion ab, wringe sie durch Leinwand, lass sie klar absetzen und verwahre den Auszug. Wasche damit einmal oder nach örtlicher Vorschrift eine unreine äußere Wunde und beende diesen Gebrauch. Nimm anschließend ein örtliches Maß der zurückbehaltenen Blätter, lege sie an die bezeichnete Stelle, erwärme sie, führe sie als zweiten Ansatz, mische sie mit Honig und lege den warmen Umschlag frisch auf.",
    "H5": "Von der abgebildeten, unbenannten Pflanze sammle zu Beginn der Blüte das ganze oberirdische Kraut an einem feuchten Standort und nimm nur ein kleines örtliches Maß. Zerstoße die frischen klebrigen Blätter, lege sie kurz auf eine einzelne Warze oder ein Hühnerauge an der bezeichneten Hautstelle, nimm die Auflage wieder ab, wasche mit Wasser und wiederhole nur bei guter Verträglichkeit. Trockne die übrigen blühenden Stiele im Schatten, zerreibe und verwahre sie. Setze daraus mit mildem Wein einen schwachen, durch ein Tuch geseihten Auszug an, gib Honig hinzu, erwärme gelinde und gib ihn in kleinem Maß als Brusttrank bei trockenem Husten.",
}


ARTICLE_STRUCTURE = {
    "H1": "radix/pars -> purgatio et sectio -> infusio/aqua -> usus et mensura -> indicatio -> conservatio -> iterated warm use",
    "H2": "pars aeria et tempus collectionis -> succus/oleum -> secunda collectio -> previous/current linking -> compositio -> unguentum -> applicatio",
    "H3": "collectio verna -> decoctio in vino -> colatura/clarificatio -> reservatio -> potus/indicatio/mensura -> oleum ad usum externum",
    "H4": "first leaf macerate -> clarification/storage -> wash application -> second leaf preparation -> honey poultice",
    "H5": "habitat/harvest -> brief topical application -> wash-off -> drying/storage -> wine/honey extract -> pectoral use and dose",
}


ARTICLE_RIVAL = {
    "H1": "Pflanzenmaterial-Los: Wurzel säubern, in Wasser mazerieren, Prüfportion buchen und Rest lagern; kein Arzneigebrauch nötig.",
    "H2": "Zwei zeitlich getrennte Erntefraktionen werden gepresst, verglichen und als Materialproben konserviert; Salbe und Geschwür entfallen.",
    "H3": "Blüten- und Blattfraktionen werden extrahiert, geklärt und als Referenzproben gelagert; Trank, Gemüt, Brust und Augenöl entfallen.",
    "H4": "Zwei Blattlose werden mazeriert, gewaschen, verglichen und gelagert; Wunde, Honig und Umschlag entfallen.",
    "H5": "Kopf-, Blatt- und Krautfraktionen werden als klebrige Probe, Trockenlos und schwacher Auszug geführt; Warze, Husten und Brusttrank entfallen.",
}


ROLE_BASE_CONFIDENCE = {
    "VISIBLE_OWNER": 0.50,
    "PLANT_PART": 0.36,
    "PLANT_PART_AND_ACTION": 0.34,
    "PLANT_PART_AND_CONDITION": 0.32,
    "PLANT_PART_AND_STORAGE": 0.31,
    "PLANT_PART_AND_DOSE": 0.33,
    "HARVEST_AND_HABITAT": 0.28,
    "HARVEST_CONDITION": 0.30,
    "ACTION": 0.32,
    "ACTION_CONDITION": 0.30,
    "ACTION_IMPLEMENT": 0.28,
    "MEDIUM": 0.24,
    "MEDIUM_ACTION": 0.25,
    "CONTAINER_ACTION": 0.25,
    "PREPARATION": 0.29,
    "STORAGE": 0.28,
    "STORAGE_CONDITION": 0.27,
    "STORAGE_AND_CLOSE": 0.30,
    "LOCAL_LINK": 0.34,
    "DOSE": 0.31,
    "DOSE_FREQUENCY": 0.29,
    "STATE": 0.31,
    "STATE_AND_USE": 0.29,
    "USE": 0.25,
    "USE_DURATION": 0.24,
    "CONDITION_AND_USE": 0.23,
    "INDICATION": 0.18,
    "INDICATION_AND_USE": 0.18,
    "INDICATION_AND_STORAGE": 0.18,
    "TARGET": 0.26,
    "FREQUENCY": 0.27,
    "FORMAL_START": 0.40,
    "FORMAL_CLOSE": 0.40,
    "SELECT_PART": 0.35,
}


VISIBLE_PART_NOUNS = {
    "Wurzelteil", "junge Spitzen", "Blütenstände", "Blätter", "Kraut",
    "Fraktionen", "Blüten", "junge Blätter", "oberirdisches Kraut",
    "klebrige Blätter", "blühende Stiele",
}
MEDICAL_NOUNS = {
    "innerlicher Gebrauch", "Leibschmerz", "Geschwür", "Schwellung",
    "zweite Arznei", "Trank", "Gemütsbeschwerde", "Brustbeschwerde",
    "Lider", "Auge", "äußerliches Öl", "Wunde", "äußere Zielstelle",
    "Umschlag", "Auflage", "Warze", "Hühnerauge", "Hautstelle",
    "Verträglichkeit", "äußere Anwendung", "Brusttrank", "Husten",
}
QUANT_NOUNS = {
    "Dosis", "Handvoll", "Erntezeit", "Frühjahr", "Anteil", "Blütezeit",
    "Einwirkdauer", "Anwendungshäufigkeit", "Wiederholung", "Gabe",
}
MATERIAL_NOUNS = {
    "Gefäß", "Quellwasser", "Glas", "Auszug", "Pflanzensaft", "Tuch",
    "Olivenöl", "glasiertes Gefäß", "Feuer", "Vorratsgefäß", "Wein",
    "Leinwand", "Weißwein", "Honig", "Wasser", "Schatten",
}


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: list[dict[str, str]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def parse_event_edition() -> dict[int, dict[str, str]]:
    result: dict[int, dict[str, str]] = {}
    for line in EVENT_EDITION_TEXT.splitlines():
        serial, role, meaning, nouns = line.split("\t")
        result[int(serial)] = {"role": role, "meaning": meaning, "nouns": nouns}
    return result


def clean_practical(text: str) -> str:
    local = re.findall(r"LOCAL\[(.*?)\]", text)
    if local:
        value = "; ".join(local)
    else:
        value = re.sub(r"\[[^\]]*\]", "", text).strip(" ;")
    value = re.sub(r"\bH[1-5]-(?:R|P|I|T)\d+\b", "dem lokalen Posten", value)
    value = re.sub(r"\s+", " ", value).strip()
    return "Technischer Pflanzenmaterial-Rivale: " + value.rstrip(".") + "."


def literal_layer(event: dict[str, str], owner: str, role: str) -> str:
    pieces = [f"[OWNER:{owner}]", f"[OPAQUE_CARD:{event['joint_tuple_id']}]"]
    if event["selected_exact_mnemonic"] != "UNKNOWN":
        pieces.append(f"[CARD:{event['selected_exact_mnemonic']}]")
    if event["strict_formal_prompt"] != "NONE":
        pieces.append(f"[FORMAL:{event['strict_formal_prompt']}]")
    pieces.append(f"[CONTEXT_EXEMPLAR:{role}]")
    if event["terminal_status"] == "TERMINAL":
        pieces.append("[CLOSE]")
    return " > ".join(pieces)


def support_class(event: dict[str, str]) -> str:
    mnemonic = event["selected_exact_mnemonic"] != "UNKNOWN"
    formal = event["strict_formal_prompt"] != "NONE"
    if mnemonic and formal:
        return "EXACT_MNEMONIC_AND_STRICT_FORMAL_PROMPT"
    if mnemonic:
        return "EXACT_WORKING_MNEMONIC"
    if formal:
        return "STRICT_FORMAL_PROMPT_NO_WORD_VALUE"
    return "UNKNOWN_EXEMPLAR_WHOLE_CARD"


def meaning_confidence(role: str, event: dict[str, str]) -> float:
    value = ROLE_BASE_CONFIDENCE.get(role, 0.27)
    if event["selected_exact_mnemonic"] != "UNKNOWN" or event["strict_formal_prompt"] != "NONE":
        value = max(value, 0.46)
    if event["terminal_status"] == "TERMINAL":
        value = max(value, 0.40)
    return round(value, 2)


def noun_support(noun: str) -> str:
    if noun in VISIBLE_PART_NOUNS:
        return "VISIBLE_PART_BUT_EVENT_BINDING_UNSUPPORTED"
    if noun in MEDICAL_NOUNS:
        return "UNPICTURED_MEDICAL_OR_USE_NOUN"
    if noun in QUANT_NOUNS:
        return "UNPICTURED_QUANTITATIVE_OR_TEMPORAL_NOUN"
    if noun in MATERIAL_NOUNS:
        return "UNPICTURED_MATERIAL_IMPLEMENT_OR_MEDIUM"
    return "UNPICTURED_RECIPE_STATE_OR_OPERATION_NOUN"


def contradiction(nouns: str) -> str:
    if nouns == "NONE":
        return "Die ganze Pflanze ist sichtbar, aber weder ihr Artname noch der konkrete Wert der opaken Karte ist daraus ableitbar."
    parts = nouns.split("|")
    visible = [n for n in parts if n in VISIBLE_PART_NOUNS]
    unseen = [n for n in parts if n not in VISIBLE_PART_NOUNS]
    clauses: list[str] = []
    if visible:
        clauses.append("Die Bildpflanze enthält passende Formen, doch keine Textlinie bindet dieses Ereignis sicher an " + ", ".join(visible))
    if unseen:
        clauses.append("Nicht abgebildet und keiner Karte als Wortwert zugewiesen sind " + ", ".join(unseen))
    return "; ".join(clauses) + "."


def ordered_unique(items: list[str]) -> list[str]:
    return list(dict.fromkeys(items))


def aggregate_nouns(event_rows: list[dict[str, str]]) -> str:
    nouns: list[str] = []
    for row in event_rows:
        if row["unsupported_nouns"] != "NONE":
            nouns.extend(row["unsupported_nouns"].split("|"))
    return "|".join(ordered_unique(nouns)) if nouns else "NONE"


def build() -> tuple[list[dict[str, str]], list[dict[str, str]], list[dict[str, str]], list[dict[str, str]], list[dict[str, str]]]:
    editions = parse_event_edition()
    events = [row for row in read_tsv(EVENTS_IN) if int(row["event_serial"]) <= 100]
    fields_source = {
        row["field_id"]: row
        for row in read_tsv(FIELDS_IN)
        if row["field_id"].startswith("F") and int(row["field_id"][1:]) <= 20
    }
    cards = {row["joint_tuple_id"]: row for row in read_tsv(CARDS_IN)}
    owners = {
        row["unit_id"]: row
        for row in read_tsv(V71_OWNERS)
        if row["unit_kind"] == "PROSE_FIELD" and row["section"] == "HERBAL"
    }
    statements_source = {
        row["statement_id"]: row
        for row in read_tsv(V72_STATEMENTS)
        if row["record_unit_id"].startswith("H")
    }
    image_rows = {
        row["page"]: row
        for row in read_tsv(V70_IMAGES)
        if row["section"] == "HERBAL"
    }

    event_rows: list[dict[str, str]] = []
    for event in events:
        serial = int(event["event_serial"])
        edition = editions[serial]
        owner_row = owners[event["field_id"]]
        owner = owner_row["selected_visible_owner"]
        card = cards[event["joint_tuple_id"]]
        row = {
            "event_serial": str(serial),
            "record_unit_id": event["record_unit_id"],
            "page": event["page"],
            "locus": event["locus"],
            "field_id": event["field_id"],
            "statement_id": event["statement_id"],
            "joint_tuple_id": event["joint_tuple_id"],
            "whole_plant_owner": owner,
            "owner_status": owner_row["owner_status"],
            "owner_confidence": owner_row["confidence"],
            "exact_literal_card_formal_exemplar_layer": literal_layer(event, owner, edition["role"]),
            "v69_support_class": support_class(event),
            "concrete_german_meaning_in_context": edition["meaning"],
            "meaning_in_context_confidence": f"{meaning_confidence(edition['role'], event):.2f}",
            "strongest_alternative": clean_practical(event["practical_source_segment"]),
            "strongest_contradiction": contradiction(edition["nouns"]),
            "unsupported_nouns": edition["nouns"],
            "image_geometry_guard": image_rows[event["page"]]["selected_geometry"],
            "terminal_status": event["terminal_status"],
            "semantic_ceiling": "OCCURRENCE_CONTEXT_EXEMPLAR_NOT_CARD_WORD_STEM_SOUND_OR_SPECIES",
        }
        # The dictionary is used only to verify exact identity/support class.
        if card["ATOMIC_OR_WHOLE_CARD_MNEMONIC"] != event["selected_exact_mnemonic"]:
            raise ValueError(f"card/event mnemonic mismatch at E{serial}")
        event_rows.append(row)

    by_field: dict[str, list[dict[str, str]]] = defaultdict(list)
    by_statement: dict[str, list[dict[str, str]]] = defaultdict(list)
    by_record: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in event_rows:
        by_field[row["field_id"]].append(row)
        by_statement[row["statement_id"]].append(row)
        by_record[row["record_unit_id"]].append(row)

    field_rows: list[dict[str, str]] = []
    for fid in sorted(fields_source, key=lambda x: int(x[1:])):
        source = fields_source[fid]
        members = by_field[fid]
        field_rows.append({
            "field_id": fid,
            "record_unit_id": source["record_unit_id"],
            "page": source["page"],
            "locus": source["locus"],
            "statement_id": source["statement_id"],
            "event_serials": "|".join(row["event_serial"] for row in members),
            "whole_plant_owner": members[0]["whole_plant_owner"],
            "literal_event_sequence": " || ".join(f"E{row['event_serial']}={row['exact_literal_card_formal_exemplar_layer']}" for row in members),
            "third_edition_field_text": " ".join(row["concrete_german_meaning_in_context"] for row in members),
            "historical_source_order": source["primary_template"],
            "parse_status": source["parse_status"],
            "strongest_alternative": " ".join(row["strongest_alternative"] for row in members),
            "unsupported_nouns": aggregate_nouns(members),
            "strongest_contradiction": "Alle Inhalte außer dem ganzen Pflanzenbesitzer und den expliziten Formalankern bleiben occurrence-gebundene Quellenwerte.",
            "semantic_ceiling": "FIELD_RECEPTARIUM_EXEMPLAR_NOT_TRANSLATION",
        })

    statement_rows: list[dict[str, str]] = []
    for sid, source in statements_source.items():
        members = by_statement[sid]
        statement_rows.append({
            "statement_id": sid,
            "record_unit_id": source["record_unit_id"],
            "page": source["page"],
            "constituent_fields": source["constituent_fields"],
            "event_serials": "|".join(row["event_serial"] for row in members),
            "whole_plant_owner": members[0]["whole_plant_owner"],
            "v72_selected_paraphrase": source["selected_concrete_paraphrase"],
            "third_edition_statement_text": " ".join(row["concrete_german_meaning_in_context"] for row in members),
            "literal_event_sequence": " || ".join(f"E{row['event_serial']}={row['exact_literal_card_formal_exemplar_layer']}" for row in members),
            "strongest_alternative": " ".join(row["strongest_alternative"] for row in members),
            "unsupported_nouns": aggregate_nouns(members),
            "strongest_contradiction": source["hardest_contradiction"],
            "line_crossing": source["line_crossing"],
            "semantic_ceiling": "STATEMENT_SOURCE_CLASS_EXEMPLAR_NOT_TRANSLATION",
        })

    article_rows: list[dict[str, str]] = []
    for record in ("H1", "H2", "H3", "H4", "H5"):
        members = by_record[record]
        article_rows.append({
            "record_unit_id": record,
            "page": members[0]["page"],
            "whole_plant_owner": members[0]["whole_plant_owner"],
            "field_ids": "|".join(ordered_unique(row["field_id"] for row in members)),
            "statement_ids": "|".join(ordered_unique(row["statement_id"] for row in members)),
            "event_serials": "|".join(row["event_serial"] for row in members),
            "historical_source_structure": ARTICLE_STRUCTURE[record],
            "event_bound_continuous_text": " ".join(row["concrete_german_meaning_in_context"] for row in members),
            "fluent_article": ARTICLE_FLUENT[record],
            "event_alignment": " || ".join(f"E{row['event_serial']}={row['concrete_german_meaning_in_context']}" for row in members),
            "strongest_alternative_article": ARTICLE_RIVAL[record],
            "unsupported_nouns": aggregate_nouns(members),
            "strongest_contradiction": "Das Bild trägt den ganzen Pflanzenartikel, aber weder Artname noch Rezeptmedien, Indikationen, Mengen oder genaue Ereigniswerte.",
            "semantic_ceiling": "CONTINUOUS_HISTORICAL_WORKING_ARTICLE_NOT_DECIPHERMENT",
        })

    noun_occurrences: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in event_rows:
        if row["unsupported_nouns"] == "NONE":
            continue
        for noun in row["unsupported_nouns"].split("|"):
            noun_occurrences[noun].append(row)
    noun_rows: list[dict[str, str]] = []
    for noun in sorted(noun_occurrences, key=str.casefold):
        members = noun_occurrences[noun]
        klass = noun_support(noun)
        rationale = {
            "VISIBLE_PART_BUT_EVENT_BINDING_UNSUPPORTED": "Die Form kommt an der Ganzpflanze vor, doch kein Leader oder Kartenwert bindet dieses Ereignis an genau diesen Teil.",
            "UNPICTURED_MEDICAL_OR_USE_NOUN": "Weder Leiden, Körperziel noch therapeutischer Gebrauch ist abgebildet; der Ausdruck stammt nur aus dem historischen Quellenexemplar.",
            "UNPICTURED_QUANTITATIVE_OR_TEMPORAL_NOUN": "Menge, Zeitpunkt oder Wiederholungszahl ist nicht bildlich angegeben und bleibt ein Receptarium-Wert.",
            "UNPICTURED_MATERIAL_IMPLEMENT_OR_MEDIUM": "Medium, Gerät oder Behälter ist nicht abgebildet und keiner opaken Karte als Wortbedeutung zugewiesen.",
            "UNPICTURED_RECIPE_STATE_OR_OPERATION_NOUN": "Der abstrakte Rezept-/Arbeitsbegriff ist eine konkrete Quellenfüllung, nicht aus Bild oder Karte gelesen.",
        }[klass]
        noun_rows.append({
            "unsupported_noun": noun,
            "support_class": klass,
            "event_count": str(len(members)),
            "event_serials": "|".join(row["event_serial"] for row in members),
            "records": "|".join(ordered_unique(row["record_unit_id"] for row in members)),
            "pages": "|".join(ordered_unique(row["page"] for row in members)),
            "rationale": rationale,
            "semantic_ceiling": "EXPLICIT_SOURCE_EXEMPLAR_NOUN_NOT_VOYNICH_LEXEME",
        })
    return event_rows, field_rows, statement_rows, article_rows, noun_rows


def md_escape(value: str) -> str:
    return value.replace("|", "\\|").replace("\n", " ")


def build_report(
    event_rows: list[dict[str, str]],
    field_rows: list[dict[str, str]],
    statement_rows: list[dict[str, str]],
    article_rows: list[dict[str, str]],
    noun_rows: list[dict[str, str]],
) -> str:
    support_counts = Counter(row["v69_support_class"] for row in event_rows)
    out: list[str] = [
        "# V73 R2 — Herbal third edition",
        "",
        "Status: kreative historische Arbeitsedition auf vier Bildern und fünf formalen Records; keine Entzifferung.",
        "",
        "## Unveränderter R2-Hintergrund",
        "",
    ]
    out += [f"{i}. {line}" for i, line in enumerate(R2_BACKGROUND, 1)]
    out += [
        "",
        "## Ergebnis",
        "",
        "Alle 100 Herbal-Ereignisse, 20 Felder, 19 Aussagen und fünf Records sind vollständig rekonstruiert. f10r trägt zwei formale Recordartikel (H1 und H2) unter derselben unbekannten Ganzpflanze; H3–H5 besitzen je eine weitere Bildpflanze. Das sind fünf Textartikel, aber nur vier Pflanzenbilder.",
        "",
        "Jede Ereigniszeile trennt vier Dinge: exakte opake Kartenidentität, den bereits eingefrorenen Karten-/Formalhandle, einen occurrence-gebundenen Kontext-Exemplarwert und den namenlosen Ganzpflanzenbesitzer. Kein deutsches Kontextwort wird dadurch zur Kartenbedeutung.",
        "",
        "Formale Stützung der 100 Ereignisse: " + ", ".join(f"{k}={v}" for k, v in sorted(support_counts.items())) + ". Die übrige Lesbarkeit entsteht aus einem konkret gewählten Receptarium-Exemplar.",
        "",
        "## Eingefrorene Quellenordnung",
        "",
        "Die Edition erlaubt die in mittelalterlichen Herbarien und Receptarien gewöhnliche Folge `Bildpflanze/pars -> Sammelzeit oder Habitat -> Zubereitung -> Medium -> Prüfzustand/Maß -> Anwendung/Indikation -> Aufbewahrung`. Nicht jeder Artikel enthält jedes Glied. Ein Bild muss Wasser, Wein, Öl, Honig, Tuch, Gefäß, Krankheit oder Dosis nicht darstellen; diese Substantive werden deshalb ausdrücklich als unbebilderte Quellenwerte geführt.",
        "",
        "Die vier Bildbesitzer bleiben `WHOLE_*`; f10r-Blätter, f11r-Krone, f55v-Großblatt/Wurzel und f56r-Mehrfachköpfe liefern keine sicheren Artbestimmungen. Die alten engen Namen bleiben entzogen.",
        "",
        "## Fünf kontinuierliche Artikel",
        "",
    ]
    for article in article_rows:
        out += [
            f"### {article['record_unit_id']} — {article['page']}",
            "",
            f"**Besitzer:** `{article['whole_plant_owner']}`",
            "",
            f"**Historische Struktur:** `{article['historical_source_structure']}`",
            "",
            article["fluent_article"],
            "",
            f"**Stärkster Rivale:** {article['strongest_alternative_article']}",
            "",
            f"**Explizit ungestützte Substantive:** {article['unsupported_nouns'].replace('|', ', ')}.",
            "",
            f"**Härtester Widerspruch:** {article['strongest_contradiction']}",
            "",
        ]

    out += [
        "## Alle zwanzig Felder",
        "",
        "| Feld | Record/Locus | Ereignisse | Dritte Edition |",
        "|---|---|---|---|",
    ]
    for field in field_rows:
        out.append(
            f"| {field['field_id']} | {field['record_unit_id']} / {field['locus']} | {field['event_serials']} | {md_escape(field['third_edition_field_text'])} |"
        )
    out += [
        "",
        "## Fünf Literalproben",
        "",
    ]
    for serial in (1, 17, 44, 69, 98):
        row = event_rows[serial - 1]
        out += [
            f"- **E{serial}:** `{row['exact_literal_card_formal_exemplar_layer']}` → {row['concrete_german_meaning_in_context']} Confidence {row['meaning_in_context_confidence']}. Alternative: {row['strongest_alternative']} Widerspruch: {row['strongest_contradiction']}",
        ]

    noun_classes = Counter(row["support_class"] for row in noun_rows)
    out += [
        "",
        "## Audit der ungestützten Substantive",
        "",
        f"Die vollständige Nomenliste enthält {len(noun_rows)} verschiedene Ausdrücke. Klassen: " + ", ".join(f"{k}={v}" for k, v in sorted(noun_classes.items())) + ".",
        "",
        "`VISIBLE_PART_BUT_EVENT_BINDING_UNSUPPORTED` bedeutet nicht unsichtbar: Der Teil kann an der Ganzpflanze vorkommen, ist aber nicht durch Leader oder Kartenwert an das konkrete Ereignis gebunden. Alle anderen Klassen sind tatsächlich unbebilderte Quellenwerte. Die vollständigen Ereignisbindungen stehen in `V73_R2_UNSUPPORTED_NOUNS.tsv`.",
        "",
        "## Historische Gattungskalibrierung",
        "",
        "1. British Library, [Egerton MS 747](https://searcharchives.bl.uk/catalog/032-001983805), *Tractatus de herbis*, ca. 1280–1350. Der Katalog verbindet große Pflanzenbilder mit Herbal, Antidotarium, Dosen, Substitutionen, Maßen und Synonymen. Das trägt die Artikel-/Receptarium-Ordnung, nicht diese konkreten Rezepte.",
        "2. British Library, [Egerton MS 2020](https://searcharchives.bl.uk/catalog/032-001982947), Carrara-Herbal, ca. 1390–1404. Der zeitnahe Bildherbal-Vergleich trägt benannte Simples als Gattung, identifiziert aber keine der vier Pflanzen.",
        "3. British Library, [Royal MS 2 B VII](https://searcharchives.bl.uk/catalog/041-002353538), anthropomorphe Alraunenbilder. Die Quelle kalibriert nur mnemonic-groteske Wurzelgestaltung; f55v wird weder Alraune noch Tier genannt.",
        "",
        "## Was diese Edition nicht leistet",
        "",
        "Die 100 deutschen Ereigniswerte sind ein einziges vollständig ausgeschriebenes historisches Exemplar. Sie wurden nicht aus Oberfläche, Lautung, Teilzeichen, Stamm, PAGE_HOST oder Kartenwiederholung gewonnen. Ein anderes Masterexemplar könnte dieselben 100 opaken Karten mit der technischen Rivalenedition füllen. Pflanzenarten, bestätigte Wörter und Klartextklauseln bleiben null. f84 und f84r blieben versiegelt.",
        "",
        "## Reproduzierbarkeit",
        "",
        "```bash",
        "python experiments/yolo/sidequest_theory_candidates_v73/build_v73_r2_herbal_third_edition.py",
        "python experiments/yolo/sidequest_theory_candidates_v73/validate_v73_r2_herbal_third_edition.py",
        "```",
        "",
    ]
    return "\n".join(out)


def main() -> None:
    event_rows, field_rows, statement_rows, article_rows, noun_rows = build()
    write_tsv(EVENTS_OUT, event_rows)
    write_tsv(FIELDS_OUT, field_rows)
    write_tsv(STATEMENTS_OUT, statement_rows)
    write_tsv(ARTICLES_OUT, article_rows)
    write_tsv(NOUNS_OUT, noun_rows)
    REPORT_OUT.write_text(build_report(event_rows, field_rows, statement_rows, article_rows, noun_rows), encoding="utf-8")
    print(json.dumps({
        "events": len(event_rows),
        "fields": len(field_rows),
        "statements": len(statement_rows),
        "articles": len(article_rows),
        "unsupported_nouns": len(noun_rows),
        "events_sha256": hashlib.sha256(EVENTS_OUT.read_bytes()).hexdigest(),
    }, ensure_ascii=False))


if __name__ == "__main__":
    main()
