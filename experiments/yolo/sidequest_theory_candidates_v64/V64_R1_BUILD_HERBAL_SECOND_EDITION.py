#!/usr/bin/env python3
"""Build the blinded R1 V64 Herbal second edition from selected V53/V60--V63 artifacts."""

from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent

V53_ARTICLES = ROOT / "experiments/yolo/sidequest_theory_candidates_v53/V53_SELECTED_FIVE_ARTICLES.tsv"
V60_DICTIONARY = ROOT / "experiments/yolo/sidequest_theory_candidates_v60/V60_SELECTED_173_CARD_DICTIONARY.tsv"
V60_EVENTS = ROOT / "experiments/yolo/sidequest_theory_candidates_v60/V60_SELECTED_381_EVENT_LEDGER.tsv"
V61_STATEMENTS = ROOT / "experiments/yolo/sidequest_theory_candidates_v61/V61_SELECTED_116_SOURCE_STATEMENTS.tsv"
V62_TRANSITIONS = ROOT / "experiments/yolo/sidequest_theory_candidates_v62/V62_SELECTED_116_REGISTER_TRANSITIONS.tsv"
V63_TEMPLATES = ROOT / "experiments/yolo/sidequest_theory_candidates_v63/V63_SELECTED_TEMPLATE_DEFINITIONS.tsv"
V63_EVENTS = ROOT / "experiments/yolo/sidequest_theory_candidates_v63/V63_SELECTED_381_EVENT_TEMPLATE_LEDGER.tsv"
V63_STATEMENTS = ROOT / "experiments/yolo/sidequest_theory_candidates_v63/V63_SELECTED_116_STATEMENT_SLOT_PARSE.tsv"
V63_FIELDS = ROOT / "experiments/yolo/sidequest_theory_candidates_v63/V63_SELECTED_135_FIELD_SLOT_PARSE.tsv"

ALLOWED_PAGES = {"f10r", "f11r", "f55v", "f56r"}
RECORD_ORDER = ["H1", "H2", "H3", "H4", "H5"]
EXPECTED_RECORD_COUNTS = {
    "H1": (2, 2, 14),
    "H2": (3, 3, 24),
    "H3": (4, 4, 17),
    "H4": (4, 4, 18),
    "H5": (6, 7, 27),
}


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: list[dict[str, object]], columns: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        for row in rows:
            writer.writerow({column: row.get(column, "") for column in columns})


def split_pipe(value: str) -> list[str]:
    if not value or value == "NONE":
        return []
    return [item.strip() for item in value.split("|") if item.strip()]


RECORDS = {
    "H1": {
        "plant_identity_primary": "Teufelsabbiss-nahe Wiesenpflanze; reine Bildhypothese",
        "strongest_alternative_plant_identity": "Feld-Skabiose oder Acker-Witwenblume",
        "pictured_owner_description": "H1:O01 ist die einmal gesetzte abgebildete Wiesenpflanze; die Schrift selbst nennt weder Pflanze noch Teil.",
        "proposed_article_genre": "kurzer Wurzelarznei-Artikel mit Grundauszug und zweitem warmem Gebrauch",
        "strongest_nonmedical_procedure_reading": "Färber-/Beizprotokoll für eine Wurzelprobe: waschen, zerkleinern, wässern, abmessen, Rest lagern und eine zweite Probe erwärmen.",
        "unsupported_nouns": "Teufelsabbiss;Wiesenpflanze;Unterwurzel;Quellwasser;Wurzelstoff;Flüssigkeit;Vorratsrest",
        "unsupported_actions_or_relations": "waschen;zerteilen;zerstoßen;ziehen;erwärmen;trocken lagern",
        "revisions_from_v59_v53": "Magenschmerz und Rotwein werden zurückgezogen; H1 wird enger als Wurzelauszug gelesen. V61 trennt Grundbereitung und zweiten Gebrauch; V62 hält I001/T001/I002 anonym; nur ANWENDEN?, MASS?, der formale Link und BEREIT? bleiben Anker.",
        "strongest_contradiction": "10/14 Ereignisse sind exemplar-only, beide Felder nur AMBIGUOUS und die beiden offenen Felder liefern keinen sicheren Artikelabschluss.",
        "apprentice_writing_steps": "Bildbesitzer H1:O01 einmal setzen; F001 als I001 schreiben, nur E8/E9 als Kartenanker markieren; bei RESUME I001 und I002 tragen; F002 Link und Zustandsfrage ausführen; alle Sachwörter in der Exemplarspalte lassen.",
        "confidence": "LOW_MEDIUM",
    },
    "H2": {
        "plant_identity_primary": "dieselbe Teufelsabbiss-nahe Bildpflanze wie H1; reine Bildhypothese",
        "strongest_alternative_plant_identity": "Feld-Skabiose oder Acker-Witwenblume statt Teufelsabbiss",
        "pictured_owner_description": "H2:O01 übernimmt denselben sichtbaren Pflanzenbesitzer, eröffnet aber einen eigenständigen Artikelposten für obere Teile.",
        "proposed_article_genre": "Ergänzungsartikel aus Oberteilen, Presssaft und drei aufeinander bezogenen Chargen",
        "strongest_nonmedical_procedure_reading": "Färber-/Pigmentregister: obere Pflanzenteile ausziehen, eine Vorgabecharge mit dem vorigen Bad verbinden und eine zweite ölige Mustercharge lagern.",
        "unsupported_nouns": "Teufelsabbiss;Oberteile;Pflanzensaft;Handvoll;Blüte;Bitterkeit;Öl;Gefäß;äußerliche Arznei",
        "unsupported_actions_or_relations": "sammeln;pressen;einkochen;rühren;unter Öl lagern;äußerlich gebrauchen",
        "revisions_from_v59_v53": "Der frühere pauschale Saft-/Ölgebrauch wird in drei V61-Klauseln zerlegt. V62 macht I001→I002→I003 und PREVIOUS sichtbar; die doppelte ANSATZ?-Folge in F005 bleibt als zweistufige oder wiederholte Chargenmarke offen.",
        "strongest_contradiction": "14/24 Ereignisse bleiben exemplar-only; zwei unmittelbar benachbarte ANSATZ?-Anker ergeben keine glatte Prosa und können bloße Kategorienwiederholung sein.",
        "apprentice_writing_steps": "H2:O01 setzen; I001 in F003 anlegen; bei F004 I001 als PREVIOUS sichern und I002 öffnen; bei NEXT_PARALLEL_CELL F005 als I003 beginnen; Link-/Vorige-/Maßanker in Reihenfolge kopieren, Öl und Blütentermin nur aus dem Exemplar lesen.",
        "confidence": "LOW_MEDIUM",
    },
    "H3": {
        "plant_identity_primary": "Veilchen als Leitbild; Bildhypothese mit niedriger Sicherheit",
        "strongest_alternative_plant_identity": "Wald-Sanikel als konkreter Dolden-/Wurzelpflanzen-Rivale",
        "pictured_owner_description": "H3:O01 ist eine kleine Schattenpflanze; Blüten-, Blatt- und Wurzelteil sind nur bild-/artikelgestützte Füllungen.",
        "proposed_article_genre": "zweiteiliger Veilchenartikel: geklärter Blütenauszug, zurückbehaltener Presskuchen und warme Blattauflage",
        "strongest_nonmedical_procedure_reading": "Maler-/Färberwerkstatt: Blütenfarbstoff ausziehen und klären, Presskuchen zurücklegen, eine abgemessene Probe auf einen Testträger binden und warm prüfen.",
        "unsupported_nouns": "Veilchen;Blüten;junge Blätter;Schattenstandort;Tuch;Auszug;Presskuchen;Umschlag;Hautstelle",
        "unsupported_actions_or_relations": "sammeln;zerquetschen;pressen;seihen;abkühlen;zurückbehalten;auflegen",
        "revisions_from_v59_v53": "Wein bleibt aus dem Defaulttext heraus; die KLAR?-Karte trägt nur den Zustand. F007 wird als vollständig exemplar-only ausgewiesen, und Presskuchen, Maßauflage und warmer Blattumschlag werden als drei getrennte V61-Klauseln gelesen.",
        "strongest_contradiction": "14/17 Ereignisse sind exemplar-only, F007 ist ganz unparsed und weder Veilchen noch Sanikel wird von einer Schriftkarte benannt.",
        "apprentice_writing_steps": "H3:O01 setzen; F006 bis KLAR? als I001 führen; F007 trotz PREVIOUS-Einführung ausdrücklich EXEMPLAR_ONLY schreiben; F008 I001/I002 tragen und nur MASS? markieren; F009 als parallelen I003-Posten mit BEREIT?-Gate eröffnen.",
        "confidence": "LOW_MEDIUM",
    },
    "H4": {
        "plant_identity_primary": "Breitwegerich als bevorzugte, aber unbewiesene Bildidentität",
        "strongest_alternative_plant_identity": "Bärlauch oder anderes Allium",
        "pictured_owner_description": "H4:O01 ist ein breitblättriges Heilkraut; Blattbreite ist Bildargument, kein Kartenwert.",
        "proposed_article_genre": "zweiformiger Blattartikel: Weinauszug zur Waschung und warmer Blattrückstand als Auflage",
        "strongest_nonmedical_procedure_reading": "Textil-/Lederwerkstatt: Blattbad ansetzen, eine Probe damit waschen, den warmen Pflanzenbrei als Beiz- oder Weichmacherauftrag weiterverwenden.",
        "unsupported_nouns": "Breitwegerich;Blätter;Weißwein;Flüssigkeit;Hautstelle;Blattrückstand;Brei;Gefäß;Auflage",
        "unsupported_actions_or_relations": "zerstoßen;ziehen;rühren;waschen;befeuchten;erwärmen;auflegen",
        "revisions_from_v59_v53": "Wegerich wird vor Allium als Default gesetzt, ohne Sicherheit zu erhöhen. F012 bleibt vollständig exemplar-only; der formale Relationsslot in F013 benennt keine Hautstelle und endet im V62-Zustand sogar mit TARGET=UNSET.",
        "strongest_contradiction": "12/18 Ereignisse sind exemplar-only, F012 ist unparsed, und das lokal gelesene Auflageziel wird vom formalen Zielslot nicht referentiell aufgelöst.",
        "apprentice_writing_steps": "H4:O01 setzen; in F010 Standard- und Maßslot getrennt markieren; F011 als gleichen I001-Posten lesen; bei START_NEW_CLAUSE F012 als I002-Exemplar beginnen; F013 Maß, formalen Relationsslot und ANSATZ? kopieren, Ziel aber UNSET lassen.",
        "confidence": "LOW_MEDIUM",
    },
    "H5": {
        "plant_identity_primary": "Sonnentau als riskante Bildhypothese für eine feuchtlandliebende Drüsen-/Borstenpflanze",
        "strongest_alternative_plant_identity": "Fettkraut als andere klebrige Feuchtlandpflanze",
        "pictured_owner_description": "H5:O01 ist eine kleine klebrige oder borstige Feuchtlandpflanze; Wurzel, Blatt, Kopf und Blüte sind lokale Teilehypothesen.",
        "proposed_article_genre": "mehrteiliger Arzneipflanzenartikel mit Weinauszug, äußerer Auflage, Trockenreserve und Honigmischung",
        "strongest_nonmedical_procedure_reading": "Klebstoff-/Färbermusterblatt: klebrige Probe sammeln, in Wein ausziehen, auf einem Zielträger testen, Teile getrennt trocknen und eine Bindercharge mischen.",
        "unsupported_nouns": "Sonnentau;Feuchtlandpflanze;Wurzel;Blätter;Wein;Zielstelle;Auflage;Samenkopf;Knospenkopf;Blüten;Honig;Vorrat;Löffelgabe",
        "unsupported_actions_or_relations": "sammeln;trennen;ziehen;auflegen;trocknen;einnehmen;lagern;mischen",
        "revisions_from_v59_v53": "Brust- und Hustenindikation werden zurückgezogen. F014→F015 bleibt eine einzige V61-Klausel; F017–F019 werden ohne Anker nicht geglättet, sondern als exemplar-only Teile-/Vorratsposten veröffentlicht.",
        "strongest_contradiction": "21/27 Ereignisse, drei von sieben Feldern und drei von sechs Aussagen sind exemplar-only; Sonnentau, innerer Gebrauch und Honig sind vollständig lokale Wetten.",
        "apprentice_writing_steps": "H5:O01 setzen; F014 und F015 auf demselben Klauselzettel über den Zeilenreset führen; danach F016–F020 als getrennte Resume-/Parallelposten schreiben; nur MASS?, ANWENDEN?, ZIEL? und ANTEIL? markieren; drei unparsed Felder nicht nachträglich parsen.",
        "confidence": "LOW",
    },
}


CLAUSES = {
    "H1-S001": {
        "translation": "Nimm vom Bildbesitzer die faserige Unterwurzel, wasche und zerstoße sie, setze sie mit Quellwasser an, wende eine vorgeschriebene Portion an und bewahre den übrigen Wurzelstoff trocken auf.",
        "unsupported_nouns": "Unterwurzel;Quellwasser;Wurzelstoff",
        "unsupported_actions": "waschen;zerstoßen;ansetzen;trocken aufbewahren",
        "revision": "Magenschmerz und Rotwein entfernt; Anwendung und Maß bleiben die einzigen exakten semantischen Prompts.",
        "strongest_local_alternative": "erste Feldzelle als Überschrift oder Material-/Farbprobenbuchung statt Arzneiklausel",
    },
    "H1-S002": {
        "translation": "Für einen zweiten Gebrauch nimm dieselbe Flüssigkeit wieder auf, erwärme sie nur handwarm, verbinde sie mit dem vorigen Ansatz und verwende sie, sobald sie bereit ist.",
        "unsupported_nouns": "Flüssigkeit;zweiter Gebrauch",
        "unsupported_actions": "erwärmen;verwenden",
        "revision": "V61-RESUME und V62-PREVIOUS ersetzen die frühere lose zweite Satzfolge.",
        "strongest_local_alternative": "warme zweite Färberprobe oder bloße Fortsetzungsrubrik",
    },
    "H2-S001": {
        "translation": "Nimm die oberen jungen Teile derselben Bildpflanze, setze daraus einen frischen Ansatz an, gib den ausgepressten Saft hinzu, lasse ihn gelinde einkochen und teile eine vorgeschriebene Portion ab.",
        "unsupported_nouns": "Oberteile;Pflanzensaft",
        "unsupported_actions": "nehmen;pressen;einkochen;abteilen",
        "revision": "Habitatbehauptung entfernt; die Klausel wird als erste Charge statt als Pflanzenbeschreibung gelesen.",
        "strongest_local_alternative": "erste Pigment- oder Färbercharge aus oberen Pflanzenteilen",
    },
    "H2-S002": {
        "translation": "Nimm eine kleine Handvoll vom vorigen Ansatz, verbinde beide Arbeitsanteile in vorgeschriebenem Maß und rühre sie zu einer gleichmäßigen Masse.",
        "unsupported_nouns": "Handvoll;Arbeitsanteile;Masse",
        "unsupported_actions": "nehmen;verbinden;rühren",
        "revision": "VORIGES? und die beiden formalen Links werden auf den anonymen PREVIOUS-Slot begrenzt.",
        "strongest_local_alternative": "zwei Chargen eines Materialregisters werden zusammengebucht, nicht physisch gemischt",
    },
    "H2-S003": {
        "translation": "Wenn sich die Blüten öffnen, beginne eine Schlusscharge, führe den Ansatz ein zweites Mal weiter, lasse ihn bis zu kräftiger Bitterkeit ziehen und bewahre die abgeteilte Portion unter Öl auf.",
        "unsupported_nouns": "Blüten;Schlusscharge;Bitterkeit;Öl",
        "unsupported_actions": "beginnen;ziehen;abteilen;aufbewahren",
        "revision": "Die doppelte ANSATZ?-Folge bleibt sichtbar und wird nicht zu zwei neuen Kartenbedeutungen zerlegt.",
        "strongest_local_alternative": "doppelte Kategorienmarke oder Kopierwiederholung vor einer Lagerbuchung",
    },
    "H3-S001": {
        "translation": "Sammle Blüten und junge Blätter am schattigen Standort kurz vor voller Blüte, zerquetsche und presse sie durch ein Tuch, seihe den Auszug zweimal, bis er klar ist, und lasse ihn abkühlen.",
        "unsupported_nouns": "Blüten;Blätter;Schattenstandort;Tuch;Auszug",
        "unsupported_actions": "sammeln;zerquetschen;pressen;seihen;abkühlen",
        "revision": "Wein entfällt; KLAR? bleibt ein Zustandsanker ohne ausgeschriebene Filterbedingung.",
        "strongest_local_alternative": "Herstellung eines geklärten Blütenfarbstoffs",
    },
    "H3-S002": {
        "translation": "Behalte den Presskuchen als vorigen Posten zurück.",
        "unsupported_nouns": "Presskuchen;Posten",
        "unsupported_actions": "zurückbehalten",
        "revision": "Der Ein-Ereignis-Satz wird ausdrücklich als vollständig exemplar-only geführt.",
        "strongest_local_alternative": "bloße Trenn- oder Ablagemarke im Musterbuch",
    },
    "H3-S003": {
        "translation": "Nimm vom zurückbehaltenen Material eine vorgeschriebene Portion und binde sie als Umschlag auf die geschwollene Hautstelle.",
        "unsupported_nouns": "Material;Portion;Umschlag;Hautstelle",
        "unsupported_actions": "nehmen;binden;auflegen",
        "revision": "MASS? liefert nur den Parameterprompt; Körperstelle und Umschlag bleiben Exemplarnomen.",
        "strongest_local_alternative": "abgemessene Farbprobe auf einen Testträger aufbringen",
    },
    "H3-S004": {
        "translation": "Bereite aus frischen Blättern einen zweiten warmen Umschlag und verwende ihn, sobald er bereit ist.",
        "unsupported_nouns": "Blätter;Umschlag",
        "unsupported_actions": "bereiten;erwärmen;verwenden",
        "revision": "NEXT_PARALLEL_CELL eröffnet I003; BEREIT? benennt nur das Gate, nicht Wärme oder Anwendung.",
        "strongest_local_alternative": "zweite warme Pigment- oder Leimprobe",
    },
    "H4-S001": {
        "translation": "Beginne einen standardisierten Blattposten, nimm ein vorgeschriebenes Maß frischer Blätter, zerstoße sie, gib weißen Wein hinzu und lasse den Ansatz zugedeckt ziehen.",
        "unsupported_nouns": "Blattposten;Blätter;Weißwein;Ansatz",
        "unsupported_actions": "zerstoßen;zugeben;ziehen",
        "revision": "Standard- und exakter Maßslot bleiben zwei getrennte Kanäle; Weißwein wird nur lokal ergänzt.",
        "strongest_local_alternative": "standardisierte Blattflotte für Färberei oder Lederbehandlung",
    },
    "H4-S002": {
        "translation": "Nimm ein vorgeschriebenes Maß der ausgezogenen Flüssigkeit, rühre sie gleichmäßig und wasche damit die gereizte Hautstelle einmal.",
        "unsupported_nouns": "Flüssigkeit;Hautstelle",
        "unsupported_actions": "rühren;waschen",
        "revision": "Die Waschung ist kein Kartenwert; nur MASS? bleibt kurz verankert.",
        "strongest_local_alternative": "Teststück mit einer abgemessenen Blattflotte spülen",
    },
    "H4-S003": {
        "translation": "Für den zweiten Gebrauch befeuchte den weichen Blattrückstand nochmals mit weißem Wein und lasse ihn handwarm erweichen.",
        "unsupported_nouns": "Blattrückstand;Weißwein;zweiter Gebrauch",
        "unsupported_actions": "befeuchten;erwärmen;erweichen",
        "revision": "F012 wird als START_NEW_CLAUSE, aber vollständig exemplar-only veröffentlicht.",
        "strongest_local_alternative": "zweite Weichmacherprobe aus dem Blattrest",
    },
    "H4-S004": {
        "translation": "Nimm davon ein vorgeschriebenes Maß, ordne den Brei der zu belegenden Stelle zu, halte ihn bedeckt als aktiven Ansatz und lege ihn frisch auf.",
        "unsupported_nouns": "Brei;Stelle;Ansatz;Auflage",
        "unsupported_actions": "zuordnen;bedecken;auflegen",
        "revision": "Der lokale Zielbezug wird als Wette markiert, weil TARGET trotz Formaloperator UNSET bleibt.",
        "strongest_local_alternative": "abgemessenen Pflanzenbrei einer Materialprobe zuordnen und frisch auftragen",
    },
    "H5-S001": {
        "translation": "Sammle im Frühjahr wenig von der ganzen Bildpflanze, trenne die dünne Wurzel in vorgeschriebenem Maß ab, füge junge Blätter hinzu, lasse alles in mildem Wein ziehen und wende den aktiven Auszug an der bezeichneten Zielstelle an.",
        "unsupported_nouns": "Bildpflanze;Wurzel;Blätter;Wein;Auszug;Zielstelle",
        "unsupported_actions": "sammeln;trennen;zugeben;ziehen",
        "revision": "F014 und F015 bleiben über H5-LB01 eine einzige Klausel; ANWENDEN? und ZIEL? erhalten keine stillen Sachobjekte.",
        "strongest_local_alternative": "klebrige Materialprobe ausziehen und auf einem Testträger anwenden",
    },
    "H5-S002": {
        "translation": "Vom selben Bildkraut nimm einen frischen feuchten Blattposten, wende ihn als dünne Auflage an und lasse ihn unbedeckt trocknen.",
        "unsupported_nouns": "Bildkraut;Blattposten;Auflage",
        "unsupported_actions": "nehmen;auflegen;trocknen",
        "revision": "Die Handlung bleibt ANWENDEN?; Auflage und Trocknung sind lokale Exemplarfüllungen.",
        "strongest_local_alternative": "Klebe- oder Farbprobe auf einem Träger trocknen lassen",
    },
    "H5-S003": {
        "translation": "Trenne den kleinen Samen- oder Knospenkopf und die schmalen Blätter als neuen Posten ab und trockne sie im Schatten.",
        "unsupported_nouns": "Samenkopf;Knospenkopf;Blätter;Posten;Schatten",
        "unsupported_actions": "trennen;trocknen",
        "revision": "F017 bleibt vollständig exemplar-only; V62 darf nur I002/T003/I001 verwalten.",
        "strongest_local_alternative": "Materialproben nach sichtbaren Pflanzenteilen sortieren und trocknen",
    },
    "H5-S004": {
        "translation": "Bereite vom getrockneten Vorrat einen kleinen Auszug, nimm ihn löffelweise ein und bewahre den Rest trocken im Schatten.",
        "unsupported_nouns": "Vorrat;Auszug;Löffelgabe;Rest;Schatten",
        "unsupported_actions": "bereiten;einnehmen;aufbewahren",
        "revision": "Magenschmerz wird entfernt; der ganze Satz bleibt exemplar-only und darf keine neue Verwendungs-Karte erzeugen.",
        "strongest_local_alternative": "getrocknete Probe prüfen und den Rest archivieren",
    },
    "H5-S005": {
        "translation": "Nimm als nächsten Posten eine frische Portion, mische sie mit Honig und gebrauche die Mischung sofort.",
        "unsupported_nouns": "Posten;Portion;Honig;Mischung",
        "unsupported_actions": "nehmen;mischen;gebrauchen",
        "revision": "Honig bleibt konkrete Rezeptwette in einer vollständig unparsed Parallelzelle.",
        "strongest_local_alternative": "frische Pflanzenprobe mit einem Binder mischen und sofort testen",
    },
    "H5-S006": {
        "translation": "Wähle von den hell geöffneten Blüten den bezeichneten Anteil in vorgeschriebenem Maß.",
        "unsupported_nouns": "Blüten;Anteil",
        "unsupported_actions": "wählen;abmessen",
        "revision": "ANTEIL? und MASS? bilden ein kurzes Gerüst; Blüte und Endverwendung bleiben offen.",
        "strongest_local_alternative": "helles Materialmuster auswählen und als Normprobe abmessen",
    },
}


FIELDS = {
    "F001": (CLAUSES["H1-S001"]["translation"], "Unterwurzel;Quellwasser;Wurzelstoff", "Wurzelprobe waschen, zerkleinern, wässern, abmessen und Rest lagern"),
    "F002": (CLAUSES["H1-S002"]["translation"], "Flüssigkeit;zweiter Gebrauch", "zweite Färberprobe mit vorigem Bad verbinden und erwärmen"),
    "F003": (CLAUSES["H2-S001"]["translation"], "Oberteile;Pflanzensaft", "erste Pigmentcharge aus Oberteilen ansetzen und abmessen"),
    "F004": (CLAUSES["H2-S002"]["translation"], "Handvoll;Arbeitsanteile;Masse", "vorige und aktive Materialcharge zusammenbuchen oder mischen"),
    "F005": (CLAUSES["H2-S003"]["translation"], "Blüten;Schlusscharge;Bitterkeit;Öl", "zweite Pigmentcharge prüfen und unter Öl lagern"),
    "F006": (CLAUSES["H3-S001"]["translation"], "Blüten;Blätter;Schattenstandort;Tuch;Auszug", "Blütenfarbstoff ausziehen, zweimal filtern und klären"),
    "F007": (CLAUSES["H3-S002"]["translation"], "Presskuchen;Posten", "Pigmentkuchen als vorige Materialprobe zurücklegen"),
    "F008": (CLAUSES["H3-S003"]["translation"], "Material;Portion;Umschlag;Hautstelle", "abgemessene Farbprobe auf einen Testträger binden"),
    "F009": (CLAUSES["H3-S004"]["translation"], "Blätter;Umschlag", "zweite warme Pigment- oder Leimprobe prüfen"),
    "F010": (CLAUSES["H4-S001"]["translation"], "Blattposten;Blätter;Weißwein;Ansatz", "standardisierte Blattflotte ansetzen"),
    "F011": (CLAUSES["H4-S002"]["translation"], "Flüssigkeit;Hautstelle", "Teststück mit abgemessener Blattflotte waschen"),
    "F012": (CLAUSES["H4-S003"]["translation"], "Blattrückstand;Weißwein;zweiter Gebrauch", "zweite Weichmacherprobe aus dem Blattrest"),
    "F013": (CLAUSES["H4-S004"]["translation"], "Brei;Stelle;Ansatz;Auflage", "Pflanzenbrei einer Materialprobe zuordnen und frisch auftragen"),
    "F014": ("Sammle im Frühjahr wenig von der ganzen Bildpflanze und trenne die dünne Wurzel in vorgeschriebenem Maß ab—", "Bildpflanze;Wurzel", "klebrige Probe sammeln, Teil trennen und abmessen"),
    "F015": ("—füge junge Blätter hinzu, lasse alles in mildem Wein ziehen und wende den aktiven Auszug an der bezeichneten Zielstelle an.", "Blätter;Wein;Auszug;Zielstelle", "Probe im Lösungsmittel ausziehen und auf Testträger anwenden"),
    "F016": (CLAUSES["H5-S002"]["translation"], "Bildkraut;Blattposten;Auflage", "klebrige Probe auf Testträger auftragen und trocknen"),
    "F017": (CLAUSES["H5-S003"]["translation"], "Samenkopf;Knospenkopf;Blätter;Posten;Schatten", "Pflanzenteile als Materialproben trennen und trocknen"),
    "F018": (CLAUSES["H5-S004"]["translation"], "Vorrat;Auszug;Löffelgabe;Rest;Schatten", "getrocknete Probe prüfen und Rest archivieren"),
    "F019": (CLAUSES["H5-S005"]["translation"], "Posten;Portion;Honig;Mischung", "frische Pflanzenprobe mit Binder mischen"),
    "F020": (CLAUSES["H5-S006"]["translation"], "Blüten;Anteil", "helles Materialmuster als Normprobe auswählen"),
}


EVENT_EXPANSIONS = {
    1: "Nimm vom Bildbesitzer die faserige Unterwurzel",
    2: "wasche sie in sauberem Wasser",
    3: "führe sie als denselben Arbeitsansatz weiter",
    4: "zerteile sie gleichmäßig",
    5: "zerstoße sie grob",
    6: "gib Quellwasser hinzu",
    7: "lasse den Ansatz gelinde ziehen",
    8: "wende die aktive Portion an",
    9: "nach vorgeschriebenem Maß",
    10: "bewahre den übrigen Wurzelstoff trocken auf",
    11: "für einen zweiten Gebrauch nimm die Flüssigkeit wieder auf",
    12: "erwärme sie nur handwarm",
    13: "verbinde sie mit dem vorigen Ansatz",
    14: "verwende sie, sobald sie bereit ist",
    15: "nimm die oberen jungen Teile derselben Bildpflanze",
    16: "beginne, sobald das Pflanzenmaterial bereitliegt",
    17: "setze daraus einen frischen Ansatz an",
    18: "gib den ausgepressten Saft hinzu",
    19: "lasse ihn gelinde einkochen",
    20: "halte diese Charge als aktiven Posten",
    21: "teile die gebrauchsfertige Flüssigkeit ab",
    22: "nach vorgeschriebenem Maß",
    23: "bewahre diese erste Portion für die Verbindung",
    24: "sammle eine zweite Handvoll vor voller Blüte",
    25: "bereite daraus einen zweiten Ansatz",
    26: "nimm eine kleine Handvoll",
    27: "verbinde sie mit dem aktiven Arbeitsstand",
    28: "nimm dabei vom vorigen Ansatz",
    29: "verbinde beide Arbeitsanteile",
    30: "in vorgeschriebenem Maß",
    31: "rühre sie zu einer gleichmäßigen Masse",
    32: "wenn sich die Blüten öffnen, beginne die Schlusscharge",
    33: "halte sie als neuen Ansatz",
    34: "führe den Ansatz ein zweites Mal weiter",
    35: "nimm die aktive Portion",
    36: "lasse sie bis zu kräftiger Bitterkeit ziehen",
    37: "teile sie für den äußerlichen Gebrauch ab",
    38: "bewahre sie unter Öl in einem bedeckten Gefäß",
    39: "sammle Blüten und junge Blätter im Frühjahr",
    40: "von einem schattigen Standort",
    41: "kurz vor voller Blüte",
    42: "zerquetsche sie und presse sie durch ein Tuch",
    43: "seihe den Auszug ein zweites Mal",
    44: "bis der Auszug klar ist",
    45: "lasse die klare Flüssigkeit abkühlen",
    46: "behalte den Presskuchen als vorigen Posten zurück",
    47: "vom selben Bildkraut",
    48: "nimm diese zurückbehaltene Portion",
    49: "lege sie auf die geschwollene Hautstelle",
    50: "halte den Umschlag dort",
    51: "in vorgeschriebenem Maß",
    52: "bereite aus frischen Blättern einen zweiten warmen Umschlag",
    53: "lege ihn handwarm auf",
    54: "sobald er bereit ist",
    55: "verwende diese Portion frisch",
    56: "beginne den standardisierten ersten Blattposten",
    57: "mit einem vorgeschriebenen Maß frischer Blätter",
    58: "zerstoße die breiten Blätter",
    59: "gib weißen Wein hinzu",
    60: "lasse den Ansatz zugedeckt ziehen",
    61: "nimm ein vorgeschriebenes Maß der ausgezogenen Flüssigkeit",
    62: "rühre sie gleichmäßig",
    63: "wasche damit die gereizte Hautstelle einmal",
    64: "für den zweiten Gebrauch nimm den weichen Blattrückstand",
    65: "befeuchte ihn nochmals mit weißem Wein",
    66: "halte ihn nur handwarm",
    67: "lasse ihn sanft erweichen",
    68: "nimm davon ein vorgeschriebenes Maß",
    69: "ordne den Brei der zu belegenden Stelle zu",
    70: "halte ihn in einem bedeckten Gefäß",
    71: "führe ihn als aktiven Ansatz",
    72: "teile die frische Portion ab",
    73: "lege sie sofort auf die bezeichnete Stelle",
    74: "sammle im Frühjahr wenig von der ganzen Bildpflanze",
    75: "nimm als ersten Posten die unteren Teile",
    76: "trenne die dünne Wurzel ab",
    77: "in vorgeschriebenem Maß",
    78: "füge junge Blätter hinzu",
    79: "lasse alles in mildem Wein ziehen",
    80: "verwende Pflanzenmaterial vor voller Blüte",
    81: "wende den aktiven Auszug an",
    82: "an der bezeichneten Zielstelle",
    83: "vom selben Bildkraut",
    84: "nimm einen frischen feuchten Blattposten",
    85: "wende ihn als dünne Auflage an",
    86: "lasse die Auflage unbedeckt trocknen",
    87: "trenne den kleinen Samen- oder Knospenkopf ab",
    88: "nimm als nächsten Posten die schmalen Blätter",
    89: "lege das Pflanzenmaterial gesondert aus",
    90: "trockne es im Schatten",
    91: "bereite vom getrockneten Vorrat einen kleinen Auszug",
    92: "nimm ihn löffelweise ein",
    93: "bewahre den Rest trocken im Schatten",
    94: "nimm als nächsten Posten eine frische Portion",
    95: "verarbeite sie sofort",
    96: "mische sie mit Honig",
    97: "gebrauche die Mischung frisch",
    98: "wähle den bezeichneten Anteil",
    99: "von den hell geöffneten Blüten",
    100: "in vorgeschriebenem Maß",
}


def main() -> None:
    v53_rows = read_tsv(V53_ARTICLES)
    v53_by_record = {row["article_id"]: row for row in v53_rows}
    dictionary_rows = read_tsv(V60_DICTIONARY)
    v60_events = [row for row in read_tsv(V60_EVENTS) if row["page"] in ALLOWED_PAGES]
    v61_statements = [row for row in read_tsv(V61_STATEMENTS) if row["page"] in ALLOWED_PAGES]
    v62_transitions = [row for row in read_tsv(V62_TRANSITIONS) if row["page"] in ALLOWED_PAGES]
    template_rows = read_tsv(V63_TEMPLATES)
    v63_events = [row for row in read_tsv(V63_EVENTS) if row["page"] in ALLOWED_PAGES]
    v63_statements = [row for row in read_tsv(V63_STATEMENTS) if row["page"] in ALLOWED_PAGES]
    v63_fields = [row for row in read_tsv(V63_FIELDS) if row["page"] in ALLOWED_PAGES]

    assert len(v53_rows) == 5 and set(v53_by_record) == set(RECORD_ORDER)
    assert len(dictionary_rows) == 173
    assert len(v60_events) == len(v63_events) == 100
    assert len(v61_statements) == len(v62_transitions) == len(v63_statements) == 19
    assert len(v63_fields) == 20
    assert len(template_rows) == 12
    assert set(EVENT_EXPANSIONS) == set(range(1, 101))
    assert set(FIELDS) == {f"F{index:03d}" for index in range(1, 21)}
    assert set(CLAUSES) == {row["statement_id"] for row in v61_statements}
    assert {row["page"] for row in v60_events} == ALLOWED_PAGES

    v60_by_serial = {int(row["event_serial"]): row for row in v60_events}
    v63_event_by_serial = {int(row["event_serial"]): row for row in v63_events}
    v61_by_statement = {row["statement_id"]: row for row in v61_statements}
    v62_by_statement = {row["statement_id"]: row for row in v62_transitions}
    v63_statement_by_id = {row["statement_id"]: row for row in v63_statements}
    v63_field_by_id = {row["field_id"]: row for row in v63_fields}
    assert set(v60_by_serial) == set(v63_event_by_serial) == set(range(1, 101))

    event_rows: list[dict[str, object]] = []
    for serial in range(1, 101):
        old = v60_by_serial[serial]
        parsed = v63_event_by_serial[serial]
        statement = v63_statement_by_id[parsed["statement_id"]]
        transition = v62_by_statement[parsed["statement_id"]]
        support = "EXEMPLAR_ONLY" if parsed["event_parse_status"] == "UNPARSED_EXEMPLAR" else "UNIQUE_EVENT_TEMPLATE;LOCAL_WORDING_AMBIGUOUS"
        event_rows.append(
            {
                "event_serial": serial,
                "record_unit_id": old["record_unit_id"],
                "page": old["page"],
                "locus": old["locus"],
                "field_id": old["field_id"],
                "statement_id": parsed["statement_id"],
                "event_index_in_record": old["event_index_in_record"],
                "surface_display_only": old["surface"],
                "joint_tuple_id": old["joint_tuple_id"],
                "formal_formula_opaque": old["formal_formula_opaque"],
                "terminal_status": old["terminal_status"],
                "selected_exact_mnemonic_unchanged": old["ATOMIC_OR_WHOLE_CARD_MNEMONIC"],
                "strict_formal_prompt": parsed["strict_formal_prompt"],
                "v63_event_template": parsed["event_template"],
                "v63_event_parse_status": parsed["event_parse_status"],
                "v64_support_class": support,
                "v63_statement_parse_status": statement["parse_status"],
                "v63_field_parse_status": v63_field_by_id[old["field_id"]]["parse_status"],
                "v62_statement_pre_state": transition["pre_state"],
                "v62_statement_post_state": transition["post_state"],
                "register_scope": "STATEMENT_ENVELOPE_ONLY;NO_EVENT_ORDER_INHERITANCE",
                "v59_local_expansion_for_comparison": old["LOCAL_IATROMEDICAL_EXPANSION"],
                "v64_local_source_expansion": EVENT_EXPANSIONS[serial],
                "local_expansion_level": "CREATIVE_HERBAL_EXEMPLAR;NOT_CARD_VALUE",
                "unsupported_nouns_reference": f"SEE_{old['record_unit_id']}_RECORD_LEDGER",
                "strongest_nonmedical_field_reading": FIELDS[old["field_id"]][2],
                "semantic_noninheritance": "EXACT_CARD_UNCHANGED;FORMAL_CONTROL_NOT_WORD;SURFACE_DISPLAY_ONLY",
                "source_lineage": "V53_SELECTED_VISUAL_OWNER>V60_SELECTED_EVENT>V61_SELECTED_STATEMENT>V62_SELECTED_REGISTER>V63_SELECTED_PARSE>V64_R1",
            }
        )

    clause_rows: list[dict[str, object]] = []
    for statement in v61_statements:
        statement_id = statement["statement_id"]
        parsed = v63_statement_by_id[statement_id]
        transition = v62_by_statement[statement_id]
        manual = CLAUSES[statement_id]
        v64_class = "EXEMPLAR_ONLY" if parsed["parse_status"] == "UNPARSED" else parsed["parse_status"]
        clause_rows.append(
            {
                "statement_id": statement_id,
                "record_unit_id": statement["record_unit_id"],
                "page": statement["page"],
                "statement_ordinal_in_record": statement["statement_ordinal_in_record"],
                "constituent_loci": statement["constituent_loci"],
                "constituent_fields": statement["constituent_fields"],
                "event_count": statement["event_count"],
                "event_serials": statement["event_serials"],
                "entry_boundary_class": statement["entry_boundary_class"],
                "exit_boundary_class": statement["exit_boundary_class"],
                "internal_cross_line_boundaries": statement["internal_cross_line_boundaries"],
                "v63_parse_status": parsed["parse_status"],
                "v64_support_class": v64_class,
                "licensed_primitive_sequence": parsed["licensed_primitive_sequence"],
                "recognized_event_count": parsed["recognized_event_count"],
                "exemplar_only_event_count": parsed["exemplar_only_event_count"],
                "v62_pre_state": transition["pre_state"],
                "v62_operations": (
                    f"OWNER:{transition['owner_operation']};ACTIVE:{transition['active_item_preparation_operation']};"
                    f"TARGET:{transition['target_station_operation']};PREVIOUS:{transition['previous_item_operation']}"
                ),
                "v62_post_state": transition["post_state"],
                "v64_german_clause": manual["translation"],
                "exact_unsupported_nouns": manual["unsupported_nouns"],
                "unsupported_actions_or_relations": manual["unsupported_actions"],
                "revision_from_v59_v53": manual["revision"],
                "strongest_local_alternative": manual["strongest_local_alternative"],
                "semantic_boundary": "CLAUSE_IS_LOCAL_EXEMPLAR;NO_NOUN_OR_ACTION_BACKFILLS_A_CARD",
                "source_lineage": "V61_SELECTED_CLAUSE>V62_SELECTED_REGISTERS>V63_SELECTED_PARSE>V64_R1",
            }
        )

    field_rows: list[dict[str, object]] = []
    for field_id in sorted(v63_field_by_id, key=lambda value: int(value[1:])):
        parsed = v63_field_by_id[field_id]
        statement = v61_by_statement[parsed["statement_id"]]
        local_text, unsupported, nonmedical = FIELDS[field_id]
        v64_class = "EXEMPLAR_ONLY" if parsed["parse_status"] == "UNPARSED" else parsed["parse_status"]
        continuation = "SINGLE_FIELD_CLAUSE"
        if field_id == "F014":
            continuation = "CONTINUES_ACROSS_H5_LB01_TO_F015"
        elif field_id == "F015":
            continuation = "RESUMES_H5_LB01_AND_COMPLETES_H5_S001"
        field_rows.append(
            {
                "field_id": field_id,
                "record_unit_id": parsed["record_unit_id"],
                "page": parsed["page"],
                "locus": parsed["locus"],
                "statement_id": parsed["statement_id"],
                "field_position_in_statement": parsed["field_position_in_statement"],
                "continuation_role": continuation,
                "event_count": parsed["event_count"],
                "event_serials": parsed["event_serials"],
                "v63_parse_status": parsed["parse_status"],
                "v64_support_class": v64_class,
                "primary_template": parsed["primary_template"],
                "licensed_primitive_sequence": parsed["licensed_primitive_sequence"],
                "recognized_event_count": parsed["recognized_event_count"],
                "exemplar_only_event_count": parsed["exemplar_only_event_count"],
                "v62_statement_pre_state": parsed["register_pre_state_statement_envelope"],
                "v62_statement_post_state": parsed["register_post_state_statement_envelope"],
                "v64_field_german": local_text,
                "exact_unsupported_nouns": unsupported,
                "strongest_nonmedical_field_reading": nonmedical,
                "strongest_contradiction": (
                    "NO_LICENSED_TEMPLATE;COMPLETE_LOCAL_EXEMPLAR" if v64_class == "EXEMPLAR_ONLY"
                    else "LICENSED_PRIMITIVES_DO_NOT_DETERMINE_LOCAL_NOUNS_OR_CLAUSE"
                ),
                "semantic_boundary": "FIELD_TEXT_IS_LOCAL_EXEMPLAR;CLOSURE_REMAINS_SILENT",
                "source_lineage": "V53_SELECTED_OWNER>V63_SELECTED_FIELD_PARSE>V64_R1",
            }
        )

    clauses_by_record: dict[str, list[dict[str, object]]] = defaultdict(list)
    fields_by_record: dict[str, list[dict[str, object]]] = defaultdict(list)
    events_by_record: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in clause_rows:
        clauses_by_record[str(row["record_unit_id"])].append(row)
    for row in field_rows:
        fields_by_record[str(row["record_unit_id"])].append(row)
    for row in event_rows:
        events_by_record[str(row["record_unit_id"])].append(row)

    record_rows: list[dict[str, object]] = []
    for record in RECORD_ORDER:
        manual = RECORDS[record]
        old = v53_by_record[record]
        rec_clauses = clauses_by_record[record]
        rec_fields = fields_by_record[record]
        rec_events = events_by_record[record]
        statement_count, field_count, event_count = EXPECTED_RECORD_COUNTS[record]
        assert len(rec_clauses) == statement_count
        assert len(rec_fields) == field_count
        assert len(rec_events) == event_count
        status_counts = Counter(str(row["v64_support_class"]) for row in rec_clauses)
        field_status_counts = Counter(str(row["v64_support_class"]) for row in rec_fields)
        recognized_events = sum(row["v64_support_class"] != "EXEMPLAR_ONLY" for row in rec_events)
        record_rows.append(
            {
                "record_unit_id": record,
                "page": rec_events[0]["page"],
                "v53_folio_record": old["folio_record"],
                "clause_count": len(rec_clauses),
                "field_count": len(rec_fields),
                "event_count": len(rec_events),
                "v63_unique_statement_count": status_counts.get("UNIQUE", 0),
                "v63_ambiguous_statement_count": status_counts.get("AMBIGUOUS", 0),
                "v63_exemplar_only_statement_count": status_counts.get("EXEMPLAR_ONLY", 0),
                "v63_unique_field_count": field_status_counts.get("UNIQUE", 0),
                "v63_ambiguous_field_count": field_status_counts.get("AMBIGUOUS", 0),
                "v63_exemplar_only_field_count": field_status_counts.get("EXEMPLAR_ONLY", 0),
                "recognized_event_count": recognized_events,
                "exemplar_only_event_count": len(rec_events) - recognized_events,
                "v53_visual_owner_freeze": old["pictured_owner_default"],
                "v53_visual_owner_rival_freeze": old["pictured_owner_rival"],
                "pictured_owner_description": manual["pictured_owner_description"],
                "plant_identity_primary": manual["plant_identity_primary"],
                "strongest_alternative_plant_identity": manual["strongest_alternative_plant_identity"],
                "proposed_article_genre": manual["proposed_article_genre"],
                "clause_ids": "|".join(str(row["statement_id"]) for row in rec_clauses),
                "clause_by_clause_german": " || ".join(f"{row['statement_id']}: {row['v64_german_clause']}" for row in rec_clauses),
                "complete_second_edition_german": " ".join(str(row["v64_german_clause"]) for row in rec_clauses),
                "strongest_nonmedical_procedure_reading": manual["strongest_nonmedical_procedure_reading"],
                "exact_unsupported_nouns": manual["unsupported_nouns"],
                "unsupported_actions_or_relations": manual["unsupported_actions_or_relations"],
                "revisions_from_v59_v53": manual["revisions_from_v59_v53"],
                "strongest_contradiction": manual["strongest_contradiction"],
                "apprentice_writing_reading_steps": manual["apprentice_writing_steps"],
                "confidence": manual["confidence"],
                "dictionary_decision": "NO_CHANGE_TO_V60_CARD_VALUES",
                "semantic_boundary": "PLANT_AND_PROCEDURE_ARE_CREATIVE_LOCAL_EXEMPLARS;NOT_TRANSLATION",
                "source_lineage": "V53_SELECTED_VISUAL_FREEZE>V60_SELECTED_CARD_VALUES>V61_SELECTED_CONTINUATION>V62_SELECTED_REGISTERS>V63_SELECTED_PARSE>V64_R1",
            }
        )

    dictionary_delta_columns = [
        "joint_tuple_id",
        "v60_mnemonic",
        "v64_mnemonic",
        "decision",
        "reason",
    ]

    record_sections = []
    for row in record_rows:
        clause_lines = "\n".join(
            f"{index}. **{clause['statement_id']} ({clause['constituent_fields']}; {clause['v64_support_class']}):** {clause['v64_german_clause']}"
            for index, clause in enumerate(clauses_by_record[str(row["record_unit_id"])], 1)
        )
        record_sections.append(
            f"""### {row['record_unit_id']} — {row['page']}

- **Bildbesitzer:** {row['pictured_owner_description']}
- **Artikelgattung:** {row['proposed_article_genre']}.
- **Pflanzenwette:** {row['plant_identity_primary']}. Stärkster Pflanzenrivale: {row['strongest_alternative_plant_identity']}.
- **V63-Druck:** Aussagen UNIQUE/AMBIGUOUS/EXEMPLAR_ONLY = {row['v63_unique_statement_count']}/{row['v63_ambiguous_statement_count']}/{row['v63_exemplar_only_statement_count']}; Felder = {row['v63_unique_field_count']}/{row['v63_ambiguous_field_count']}/{row['v63_exemplar_only_field_count']}; Ereignisse erkannt/exemplar-only = {row['recognized_event_count']}/{row['exemplar_only_event_count']}.

Klauseln:

{clause_lines}

**Flüssige Arbeitsübersetzung:** {row['complete_second_edition_german']}

**Nichtmedizinischer Rivale:** {row['strongest_nonmedical_procedure_reading']}

**Exakt ungestützte Nomen:** `{row['exact_unsupported_nouns']}`. Ungestützte Handlungen/Relationen: `{row['unsupported_actions_or_relations']}`.

**Revision:** {row['revisions_from_v59_v53']}

**Stärkster Widerspruch:** {row['strongest_contradiction']}

**Lehrlingsregel:** {row['apprentice_writing_reading_steps']}
"""
        )

    record_table = "\n".join(
        f"| {row['record_unit_id']} | {row['clause_count']} | {row['field_count']} | {row['event_count']} | {row['recognized_event_count']} | {row['exemplar_only_event_count']} |"
        for row in record_rows
    )
    report = f"""# V64 R1 — Herbal-Quellenedition, zweite Fassung

Status: vollständige kreative Arbeitsedition; keine Entzifferung, kein historischer Pflanzennachweis.

## Ergebnis

Die fünf Herbal-Records lassen sich als **bebilderte Materia-medica-Artikel mit werkstattartigem Karten- und Registergerüst** kohärenter als in V53 lesen. Die Verbesserung ist eine bessere Quellenedition, nicht ein größeres Wörterbuch: V60 bleibt byteinhaltlich unverändert, der Dictionary-Delta hat null Datenzeilen.

Die ausgewählte V63-Fassung ist im Herbal-Scope streng: 29/100 Ereignisse tragen ein eindeutiges exaktes oder formales Template, 71 sind `EXEMPLAR_ONLY`. Auf höherer Ebene gibt es **0 UNIQUE-Aussagen und 0 UNIQUE-Felder**. Von 19 Aussagen sind 14 `AMBIGUOUS` und fünf `EXEMPLAR_ONLY`; von 20 Feldern sind 15 `AMBIGUOUS` und fünf `EXEMPLAR_ONLY`. Konkrete Pflanze, Teil, Medium, Gefäß, Körperstelle und Indikation kommen daher stets aus Bild und lokalem Artikel-Exemplar.

| Record | Klauseln | Felder | Ereignisse | erkannte Ereignisse | exemplar-only Ereignisse |
|---|---:|---:|---:|---:|---:|
{record_table}

## Editionsregel

1. V53 setzt nur den sichtbaren Besitzerrahmen; der Pflanzenname bleibt eine Wette.
2. V61 bestimmt 19 Klauseln. Physische Zeilen werden nicht als Sätze gelesen; insbesondere bilden F014 und F015 über H5-LB01 eine Klausel.
3. V62 führt OWNER, ACTIVE, TARGET und PREVIOUS ausschließlich als recordlokale IDs. Ein deutsches Sachwort darf keine ID definieren.
4. V63 liefert pro Ereignis `UNIQUE_EVENT_TEMPLATE` oder `EXEMPLAR_ONLY`, pro Feld/Aussage `AMBIGUOUS` oder `EXEMPLAR_ONLY`. Kein höheres Herbal-Segment ist UNIQUE.
5. Der Lehrling kopiert zuerst Kartenanker, formale Operation und Registerübergang. Danach schreibt er die konkrete deutsche Quellenphrase in eine getrennte Exemplarspalte.
6. Feldschluss bleibt stumm. Keine lokale Phrase wird zu einer Karten- oder Stammglosse zurückgeschrieben.

## Die fünf vollständigen Artikel

{''.join(record_sections)}

## Gesamtwidersprüche

- 71 Prozent der Ereignisse und fünf ganze Felder besitzen kein lizenziertes Template; vollständige Prosa lässt sich daher sehr leicht aus gewöhnlicher Materia medica ergänzen.
- Die Bildbesitzer sind nicht textintern benannt. Teufelsabbiss, Veilchen, Breitwegerich und Sonnentau bleiben austauschbare Bildhypothesen mit publizierten Rivalen.
- Formale Parameter-, Link- und Zieloperatoren liefern keine Zahl, Einheit, Relation oder Destination. H4s lokales Auflageziel bleibt sogar bei TARGET=UNSET.
- H2s doppelte ANSATZ?-Folge und H5s drei vollständig exemplarischen Teilefelder passen ebenso zu Kategorien-/Musterbuchführung.
- Der nichtmedizinische Färber-, Material- und Binderworkflow benutzt dasselbe Bildbesitzer-, Chargen-, Maß-, Link- und Ablageskelett. Die Schrift entscheidet nicht zwischen den Genres.

## Artefaktgrenzen

- `V64_R1_100_EVENT_INTERLINEAR.tsv` übernimmt jede exakte Karte unverändert und trennt V63-Template von lokaler Quellenphrase.
- `V64_R1_20_FIELD_EDITION.tsv` veröffentlicht alle 20 Felder samt V63-Status und V62-Aussagezustand.
- `V64_R1_19_CLAUSE_EDITION.tsv` realisiert die V61-Fortsetzungskarte klauselnweise.
- `V64_R1_5_RECORD_EDITION.tsv` enthält Bildbesitzer, Artikelgattung, vollständigen Text, Pflanzen- und Verfahrensrivalen, ungestützte Nomen, Revision, Widerspruch und Lehrlingsregel.
- `V64_R1_DICTIONARY_DELTA.tsv` enthält nur den Header: null Kartenänderungen.

Validierung: `V64_R1_VALIDATION.json`.
"""

    write_tsv(OUT / "V64_R1_100_EVENT_INTERLINEAR.tsv", event_rows, list(event_rows[0]))
    write_tsv(OUT / "V64_R1_19_CLAUSE_EDITION.tsv", clause_rows, list(clause_rows[0]))
    write_tsv(OUT / "V64_R1_20_FIELD_EDITION.tsv", field_rows, list(field_rows[0]))
    write_tsv(OUT / "V64_R1_5_RECORD_EDITION.tsv", record_rows, list(record_rows[0]))
    write_tsv(OUT / "V64_R1_DICTIONARY_DELTA.tsv", [], dictionary_delta_columns)
    (OUT / "V64_R1_HERBAL_SECOND_EDITION_REPORT.md").write_text(report, encoding="utf-8")

    build_summary = {
        "status": "BUILT_PENDING_INDEPENDENT_VALIDATION",
        "pages": len(ALLOWED_PAGES),
        "records": len(record_rows),
        "clauses": len(clause_rows),
        "fields": len(field_rows),
        "events": len(event_rows),
        "recognized_events": sum(row["v64_support_class"] != "EXEMPLAR_ONLY" for row in event_rows),
        "exemplar_only_events": sum(row["v64_support_class"] == "EXEMPLAR_ONLY" for row in event_rows),
        "statement_status_counts": dict(Counter(str(row["v64_support_class"]) for row in clause_rows)),
        "field_status_counts": dict(Counter(str(row["v64_support_class"]) for row in field_rows)),
        "dictionary_delta_rows": 0,
        "v60_dictionary_sha256": hashlib.sha256(V60_DICTIONARY.read_bytes()).hexdigest(),
    }
    (OUT / "V64_R1_BUILD_SUMMARY.json").write_text(
        json.dumps(build_summary, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
