#!/usr/bin/env python3
"""Build the complete R1 V68 nonmedical adversarial edition.

The builder preserves every V67 exact identity, formal value, mnemonic,
register transition, page namespace, renderer instruction, and surface.  It
adds only record/page-local nonmedical exemplar prose and a symmetric score.
"""

from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
BASE_LEDGER = ROOT / "experiments/yolo/sidequest_theory_candidates_v67/V67_R1_776_COVERAGE_LEDGER.tsv"
BASE_UNITS = ROOT / "experiments/yolo/sidequest_theory_candidates_v67/V67_R1_14_UNIT_ROUNDTRIP.tsv"

UNIT_ORDER = ["H1", "H2", "H3", "H4", "H5", "B1", "B2", "B3", "B4", "B5", "B6", "A1", "A2", "A3"]
EXPECTED_UNIT_COUNTS = {"H1": 14, "H2": 24, "H3": 17, "H4": 18, "H5": 27, "B1": 66, "B2": 62, "B3": 86, "B4": 47, "B5": 11, "B6": 9, "A1": 190, "A2": 65, "A3": 140}
ALLOWED_PAGES = {"f10r", "f11r", "f55v", "f56r", "f81v", "f82r", "f83r", "f67r2", "f68r1", "f69v"}


def norm(text: str) -> str:
    return " ".join(text.split())


def digest(text: str) -> str:
    return hashlib.sha256(norm(text).encode("utf-8")).hexdigest()[:20]


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle, delimiter="\t"))
    if not rows:
        raise AssertionError(f"empty input: {path}")
    return rows


def write_tsv(path: Path, rows: list[dict[str, object]], fields: list[str] | None = None) -> None:
    if not rows:
        raise AssertionError(f"empty output: {path}")
    names = fields or list(rows[0].keys())
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=names, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def prose(*sentences: str) -> str:
    return norm(" ".join(sentences))


DAY_NAMES = ["ersten", "zweiten", "dritten", "vierten", "fünften", "sechsten", "siebten"]
WORK_CLASSES = [
    "die Wurzelernte", "die Blütenernte", "die Blattsichtung", "das Schattentrocknen",
    "das Zerkleinern", "das Einweichen", "das Färbebad", "das Duftöl",
    "das Erwärmen", "das Filtern", "den Badedienst", "Reinigung und Vorratsschluss",
]
A1_MATRIX = " ".join(
    f"Am {day} Werkstatttag prüfe für {task} Materialbestand, Wasserqualität und freie Feuerstelle."
    for day in DAY_NAMES for task in WORK_CLASSES
)
A1_CONDITIONS = " ".join([
    "Bei trockenem Wetter darf gesammelt und im Schatten ausgelegt werden.",
    "Bei Regen wird nur sortiert, eingeweicht und im Haus gefiltert.",
    "Bei Frost bleiben frische Kräuter geschlossen im Vorrat.",
    "Bei großer Hitze wird kein Öl offen erwärmt.",
    "Bei klarem Wasser beginnt der helle Spülgang.",
    "Bei trübem Wasser werden Tuch und Zulauf zuerst geprüft.",
    "Bei vollem Bestand darf eine große Charge angesetzt werden.",
    "Bei knappem Bestand wird nur ein kleiner Anteil für den nächsten Dienst bereitet.",
])

A2_TASKS = [
    "prüfe den Brunnenzulauf", "reinige den oberen Vorratskasten", "zähle das trockene Brennholz",
    "räume die Feuerstelle", "prüfe die beiden Kessel", "ordne den Kräutervorrat",
    "sortiere die Wurzeln", "sortiere die Blüten", "sortiere die Blätter",
    "reinige Mörser und Schneidbrett", "setze die helle Lauge an", "setze das dunkle Färbebad an",
    "prüfe das Duftöl", "wechsle das Filtertuch", "scheuere das Hauptbecken",
    "scheuere das Nebenbecken", "öffne den ersten Zulauf", "prüfe den zweiten Zulauf",
    "spüle den Rücklauf", "reinige den unteren Ablauf", "zähle Eimer und Schöpfgefäße",
    "trockne die Handtücher", "wasche die Arbeitskleider", "scheuere Boden und Rinnen",
    "trockne Bänke und Bretter", "versiegle die Vorratsgläser", "prüfe Rechnung und Verbrauch",
    "halte Ruhetag und mache die Monatsaufnahme",
]
A2_TEXT = prose(
    "Das Zentrum bezeichnet das Monatsblatt der Werkstatt; jede der achtundzwanzig Stellen ist eine eigene Arbeitsadresse und kein Kartenwort.",
    *[f"An Stelle {i:02d} {task}." for i, task in enumerate(A2_TASKS, 1)],
    "Beginne in der hier redaktionell gesetzten Reihenfolge oder in einer im lokalen Exemplar ausdrücklich notierten Drehung; übertrage keine Stelle auf f69v.",
)

A3_RULES = [
    "sammle Wurzeln nur bei trockenem Boden und binde sie getrennt",
    "schneide frische Wurzeln klein und lege sie luftig aus",
    "pflücke Blüten vor der Mittagshitze und drücke sie nicht",
    "sortiere welke Blätter aus und verwahre nur gesunde Ware",
    "trockne duftende Pflanzen im Schatten auf sauberem Tuch",
    "weiche harte Pflanzenteile über Nacht in kaltem Wasser ein",
    "setze eine kleine helle Waschcharge vor der großen an",
    "führe einen Farbauszug zuerst über ein grobes Filter",
    "temperiere Duftöl nur bei kleiner Flamme und unter Aufsicht",
    "prüfe eine neue Farbe zuerst an einem alten Stoffrest",
    "spüle das Hauptbecken einmal mit klarem Wasser vor",
    "wiederhole die Beckenwaschung genau einmal und nicht öfter",
    "lasse trübe Flüssigkeit stehen und ziehe nur den klaren Teil ab",
    "halte den warmen Posten bedeckt bis zur nächsten Übergabe",
    "verwende kaltes Wasser für den letzten Lauf der Arbeitskleider",
    "verbinde zwei Restposten nur nach gleicher Geruchs- und Farbprobe",
    "teile eine starke Charge in zwei kleinere Dienstportionen",
    "fülle den oberen Kasten vor Öffnung des ersten Zulaufs",
    "schließe den unteren Ablauf vor jeder neuen Beschickung",
    "reinige das Filtertuch nach einer dunklen Färbung gesondert",
    "trockne Eimer und Bretter, bevor sie in den Vorrat kommen",
    "halte bei Frost die Leitungen leer und die Hähne offen",
    "verschiebe große Feuerarbeit bei starkem Wind auf den Folgetag",
    "prüfe bei trübem Brunnenwasser zuerst Sandfang und Tuch",
    "gib bei knappem Vorrat nur eine kleine bemessene Portion aus",
    "schreibe verbrauchte Kräuter, Öl und Brennholz am Abend ab",
    "übergib den fertigen Posten mit Zielstation und Maßzettel",
    "beende den Umlauf mit Reinigung, Vorratszählung und Meisterzeichen",
]
A3_TEXT = prose(
    "Die drei Kreisrubriken lehren achtundzwanzig voneinander unabhängige Werkstattregeln; ihre Nummern sind nur redaktionelle Adressen.",
    *[f"Regel {i:02d}: {rule}." for i, rule in enumerate(A3_RULES, 1)],
    "Diese Folge wird für sich konsultiert; sie bildet keinen sichtbaren Paarindex mit den achtundzwanzig Stellen von f68r1.",
)


UNIT_CONTENT: dict[str, dict[str, str]] = {
    "H1": {
        "title": "Wurzelkraut als Scheuer- und Badhauslauge",
        "text": prose(
            "Vom abgebildeten Wurzelkraut.", "Grabe den unteren Wurzelstock aus, klopfe Erde ab, wasche ihn zweimal und schneide ihn in dünne Stücke.",
            "Lege die Stücke in Regenwasser mit einer kleinen Portion Holzasche, erwärme den Topf gelinde und lasse den Ansatz über Nacht stehen.",
            "Ziehe den ersten klaren Lauf durch Leinwand ab, miss ihn nach dem örtlichen Werkstattmaß und prüfe ihn an einem alten Leinenrest.",
            "Verwende die milde Portion zum Scheuern hölzerner Wannen und zum Vorwaschen heller Tücher.",
            "Erwärme den zurückbehaltenen Wurzelposten ein zweites Mal, verbinde nur brauchbare klare Fraktionen und verwahre den Rest verschlossen und beschriftet im Materialschrank."
        ),
        "workflow": "Wurzel ernten > reinigen > schneiden > mit Wasser/Asche ausziehen > klären > messen > Probestoff > Wannen/Tuch reinigen > zweiten Lauf gewinnen > lagern",
        "purpose": "Lehrt einen vollständigen Rohstoffartikel mit Erst- und Zweitauszug sowie Qualitätsprobe.",
        "iconography": "Die f10r-Pflanze liefert sichtbar einen großen Wurzelbereich; Asche, Tuch und Wanne sind nicht abgebildet.",
        "history": "Illustrierte Pflanzenbücher und Haushalts-/Werkstattrezepte kennen Pflanzenrohstoffe und Laugen; die konkrete Verbindung bleibt nur eine Gattungsanalogie.",
        "contradiction": "Die aufwendige Pflanzenillustration und Wurzelgliederung passen unmittelbarer zu einem Arzneiherbal als zu einem Scheuermittelregister.",
        "iatro_compare": "Iatromedizin liest Wurzelauszug und bemessene Gabe; der Rivale ersetzt Krankheit und Einnahme durch Tuchprobe und Wannenpflege, ohne strukturelle Karte zu ändern.",
    },
    "H2": {
        "title": "Zwei Blütenfraktionen für Farbe und duftende Ölpaste",
        "text": prose(
            "Von derselben abgebildeten Pflanze nimm früh geöffnete Blütenköpfe und junge Blätter als ersten Werkstattposten.",
            "Zerstoße sie, presse den Saft durch ein Tuch, gib eine kleine bemessene Menge Alaunlösung hinzu und halte die klare farbige Fraktion getrennt.",
            "Ernte vor voller Blüte eine zweite Portion Spitzen, führe den vorigen H2-Posten recordlokal wieder heran und gleiche beide Fraktionen an einem Probestreifen ab.",
            "Gib einen Anteil in das kleine Färbebad für Bänder und Arbeitszeichen.",
            "Rühre den übrigen Pflanzenstoff mit Öl und wenig Wachs bei kleiner Wärme zu einer weichen, duftenden Paste, fülle sie in ein glasiertes Gefäß und verwende sie zum Einreiben von Holzgriffen oder Lederkanten."
        ),
        "workflow": "Frühernte > pressen > erste Farbfraktion > spätere Fraktion > H2-Vorposten aufnehmen > Probestreifen > Färbebad > Öl-/Wachspaste > lagern",
        "purpose": "Lehrt Zweifraktionsarbeit und einen strikt recordlokalen VORIGES-Rückschlag.",
        "iconography": "Blüten und Blätter sind am selben f10r-Bild sichtbar; Alaun, Wachs, Bänder, Holz und Leder sind Exemplarfüllungen.",
        "history": "Pflanzenfarbstoffe, Beizen, Duftstoffe und handwerkliche Pasten sind spätmittelalterliche Werkstattklassen; diese Pflanze ist dafür nicht identifiziert.",
        "contradiction": "Die zweifache Produktgabel Farbe plus Holz-/Lederpaste ist produktreicher und annahmelastiger als ein einziger medizinischer Salbenartikel.",
        "iatro_compare": "Beide Lesungen nutzen zwei Fraktionen und Öl; Medizin gewinnt beim einheitlichen Salbenziels, der Rivale bei der formalen Chargen- und Prüfstruktur.",
    },
    "H3": {
        "title": "Duftblüten für klares Spülwasser und Pflegeöl",
        "text": prose(
            "Von der kleinblütigen abgebildeten Pflanze sammle Blüten und junge Blätter am kühlen Morgen.",
            "Koche einen Teil kurz in verdünntem Wein, wringe ihn durch feine Leinwand, lasse den Auszug stehen und seihe ihn nochmals bis zur klaren örtlichen Qualitätsstufe.",
            "Bewahre frische Blüten für den zweiten Posten zurück.",
            "Miss vom klaren Auszug eine kleine Portion in das letzte Spülwasser für Badetücher und duftende Arbeitswäsche.",
            "Erwärme die zurückbehaltenen Blüten langsam in Öl, filtere den Feststoff ab und verwahre das Duftöl für hölzerne Kämme, Lederzeug und die äußere Pflege der Badhausbänke."
        ),
        "workflow": "Morgenernte > Wein-Auszug > zweimal filtrieren > klar prüfen > Anteil ins Spülwasser > zweite Blütenportion in Öl > filtrieren > lagern",
        "purpose": "Lehrt Klarprüfung und zwei getrennte Produktlinien aus demselben Bildbesitzer.",
        "iconography": "Das Pflanzenbild stützt nur den OWNER; Wein, Wäsche, Kämme und Bänke fehlen sichtbar.",
        "history": "Duftwässer, Ölauszüge und Wäschepflege sind plausible Haushalts-/Badhauspraktiken; ein illustrierter technischer Artikel dieser genauen Form ist nicht belegt.",
        "contradiction": "Die Lesung benötigt eine nicht sichtbare Duftqualität und drei verschiedene Gebrauchsgegenstände.",
        "iatro_compare": "Die medizinische Veilchenlesung besitzt stärkere Herbalkonventionen; der Rivale vermeidet Gemüts-, Brust- und Augenkrankheiten, muss aber eine Duftwerkstatt ergänzen.",
    },
    "H4": {
        "title": "Breitblatt-Auszug zum Reinigen und eine gebundene Werkstattpaste",
        "text": prose(
            "Vom breiten Blattkraut richte zuerst einen kalten Reinigungsansatz ein.",
            "Nimm eine bemessene Portion Blätter, zerstoße sie, füge Weißwein und Wasser hinzu, verschließe den Topf und lasse ihn kühl stehen.",
            "Wringe den Ansatz durch Leinwand, lasse Trub absitzen und verwahre den klaren Lauf.",
            "Wasche damit fleckige Tücher, Beckenränder und glatte Arbeitsbretter; prüfe zuvor eine kleine verborgene Stelle.",
            "Nimm einen Anteil der zurückbehaltenen Blätter, führe ihn als zweiten Ansatz, erwärme ihn gelinde und mische ihn mit Honig zu einer haftenden Paste.",
            "Trage die warme Paste dünn auf rissige Holzfugen oder Lederkanten auf und entferne Überschuss nach dem Abkühlen."
        ),
        "workflow": "Blätter messen > kalter Auszug > filtrieren/setzen > Reinigungsprobe > Tücher/Becken/Bretter > zweiter Ansatz > Honigbinder > Fugen-/Lederpaste",
        "purpose": "Lehrt offene Artikelprosa mit Wechsel von Flüssigreiniger zu gebundenem Restprodukt.",
        "iconography": "Das breite Blatt ist sichtbar; Tücher, Becken, Bretter, Honig und Reparaturziel sind nicht sichtbar.",
        "history": "Pflanzliche Reinigungs- und Bindemittel sind plausible Werkstattstoffe; die konkrete Allium-/Wegerich-Zuweisung bleibt ungesichert.",
        "contradiction": "Honig als Holz- oder Lederbinder ist schwächer als als medizinischer Salbenträger, und kein repariertes Objekt ist abgebildet.",
        "iatro_compare": "Iatromedizin liest Wundwäsche und Umschlag; der Rivale liest dieselbe Flüssig-/Feststoffgabel als Reinigung und Reparaturpaste.",
    },
    "H5": {
        "title": "Klebkraut für Fleckprobe, Etikettenleim und haltbaren Vorrat",
        "text": prose(
            "Vom klebrigen Feuchtkraut sammle zu Beginn der Blüte nur eine kleine bemessene Menge und halte es von trockenem Vorrat getrennt.",
            "Zerstoße frische klebrige Blätter, lege sie kurz auf einen einzelnen alten Leder- oder Stofffleck und prüfe die Zielstelle, bevor du den Gebrauch beendest und mit Wasser nachwäschst.",
            "Verwirf die Probe, wenn Farbe oder Faser leiden.",
            "Nimm vom übrigen Kraut die blühenden Stiele, trockne sie im Schatten, zerreibe sie grob und lagere sie trocken.",
            "Setze daraus mit mildem Wein einen schwachen Auszug an, seihe ihn durch Tuch, füge wenig Honig hinzu und erwärme gelinde.",
            "Wähle je Arbeit einen kleinen Anteil als Leim für Papieretiketten oder als dünne Markierpaste an Vorratsgefäßen."
        ),
        "workflow": "Kleinkollektion > isolierte Fleckprobe > kurz anwenden > abwaschen/verwerfen > Rest trocknen > Wein-Auszug > Honigbinder > Etiketten-/Gefäßmarkierung",
        "purpose": "Lehrt Zielprobe, Abbruchregel, Vorrat und kleine portionsweise Ausgabe.",
        "iconography": "Ein feuchtigkeitsliebendes oder klebrig wirkendes Kraut ist bildlich möglich; Leder, Stoff, Etiketten und Gefäße fehlen.",
        "history": "Pflanzenleime und Markierpasten sind handwerklich plausibel, doch Sonnentau als konkreter Klebrohstoff ist hochriskant.",
        "contradiction": "Die angenommene technische Klebkraft und zwei Gebrauchszwecke sind weder sichtbar noch aus einem Kartenanker ableitbar.",
        "iatro_compare": "Der Rivale vermeidet Warzen- und Hustenheilung, ist aber botanisch und produktgeschichtlich mindestens ebenso spekulativ wie die medizinische Sonnentauedition.",
    },
    "B1": {
        "title": "Morgendliche Badhausbeschickung und Grundkreislauf",
        "text": prose(
            "Vor Öffnung des Badhauses schließt der Betreiber den unteren Ablauf, spült den oberen Vorratskasten und prüft Brunnenzulauf, Feuer und freie Becken.",
            "Er setzt aus dem bereitgelegten Pflanzenzusatz eine milde Waschcharge an, teilt sie nach örtlichem Maß und verbindet sie mit dem erwärmten Hauptwasser.",
            "Die Mischung ruht, bis Trub absinkt; der klare Teil wird durch Tuch in das Hauptbecken geführt und auf eine für gewöhnliche Reinigung angenehme Wärme gebracht.",
            "Ein Anteil geht an die Nebenbecken, ein anderer bleibt als Nachfüllposten aktiv.",
            "Während des Dienstes prüft der Betreiber Füllstand, Geruch, Trübung und Wärme, füllt nur aus dem aktiven Posten nach und hält Rücklauf und Zielstation auseinander.",
            "Nach dem letzten Nutzer lässt er gebrauchte Flüssigkeit ab, spült Becken und Lauf, fängt wiederverwendbares klares Wasser getrennt und schließt mit Vorrats- und Brennholzeintrag."
        ),
        "workflow": "Ablauf schließen > Zulauf spülen > Pflanzencharge > messen/mischen > setzen/filtern > temperieren > Becken verteilen > überwachen/nachfüllen > ablassen > reinigen/buchen",
        "purpose": "Lehrt den vollständigen gemeinsamen Badhaus-Grundkreislauf mit OWNER, ACTIVE und TARGET.",
        "iconography": "Becken, verbindende Läufe und Figuren stützen Badhausbetrieb; Kräutercharge, Feuer und Buchung bleiben exemplarisch.",
        "history": "Öffentliche/private Bäder, Wannen, Heiz- und Wasserführung sind zeitgenössisch plausibel; die Seite ist kein nachgewiesener technischer Plan.",
        "contradiction": "Die organischen Figuren- und Beckenbilder können therapeutische Körperanwendung statt gewöhnlichen Betrieb zeigen.",
        "iatro_compare": "Beide Lesungen teilen Bad, Kräuterflotte und Apparat; nur Patient, Indikation und Heilziel entfallen zugunsten von Betreiber, Nutzer und Dienstschluss.",
    },
    "B2": {
        "title": "Einzelbecken für gewöhnliches Sitz- und Waschbad",
        "text": prose(
            "Reinige vor jedem Dienst das kleine Becken, den Zulauf und das Sitzbrett.",
            "Bereite aus klarem Wasser und einer kleinen duftenden Pflanzenportion eine frische Charge, führe sie durch Tuch und temperiere sie in einem Nebengefäß.",
            "Lasse den Badgast erst einsteigen, wenn Füllhöhe und Wärme örtlich geprüft sind.",
            "Führe den aktiven Posten langsam an die bezeichnete Beckenstelle, halte eine kühle Reserve zurück und ergänze nur nach Maß.",
            "Reiche ein warmes Tuch für die gewöhnliche äußere Reinigung, ohne Krankheit oder Körperteil im Register zu benennen.",
            "Nach dem Gebrauch öffne den Ablauf, fange brauchbares Vorwasser getrennt, spüle Becken und Tuch, gib den kühleren Schlussgang und lasse die Station offen trocknen."
        ),
        "workflow": "Einzelbecken reinigen > Duftcharge > filtern/temperieren > Nutzer einlassen > langsam füllen > Reserve/nach Maß > Tuchdienst > ablassen/spülen/trocknen",
        "purpose": "Lehrt eine kurze kundenbezogene Arbeitszelle ohne therapeutische Diagnose.",
        "iconography": "Figuren in Becken stützen tatsächliches Baden; ob gewöhnlich oder therapeutisch, ist nicht sichtbar entschieden.",
        "history": "Sitz-, Schwitz- und Waschbäder sowie Tuchdienst sind spätmittelalterliche Badehauspraxis; die genaue Abfolge bleibt Rekonstruktion.",
        "contradiction": "Der Nutzer ist eine stille Exemplarrolle, und die körpernahe Darstellung kann ebenso gut eine Behandlung bezeichnen.",
        "iatro_compare": "Dieselbe Apparatur trägt Teilbad und warme Auflage; der Rivale streicht Indikation und Therapie, gewinnt aber keine zusätzliche Kartenstütze.",
    },
    "B3": {
        "title": "Langer Reinigungs-, Rücklauf- und Wiederbeschickungszyklus",
        "text": prose(
            "Sperre nach dem Hauptdienst den warmen Beckenstrang vom Frischwasser ab und markiere Hauptbecken, Rücklauf und unteren Sammelort als getrennte Stationen.",
            "Lasse die gebrauchte Charge in den Absetzkasten laufen, halte groben Trub zurück und ziehe die obere klare Fraktion in ein Nebengefäß.",
            "Spüle den leeren Beckenboden, öffne den ersten Zulauf und führe eine kleine warme Frischportion hinein.",
            "Verbinde nur nach Geruchs- und Sichtprobe einen ausgewählten Anteil des geklärten Vorpostens mit dieser Frischportion.",
            "Temperiere den aktiven Posten, verteile ihn nacheinander auf zwei Becken und prüfe an jeder Zielstation freien Ablauf.",
            "Fange den unteren Lauf auf, lasse ihn nochmals setzen, wechsle das Filtertuch und führe die klare Fraktion in den Arbeitskreislauf zurück.",
            "Wiederhole den Wasch- und Ablassgang nur einmal.",
            "Wenn ein Lauf trüb bleibt, trenne ihn als Scheuerwasser ab; wenn Geruch, Wärme und Klarheit genügen, halte ihn für die nächste gewöhnliche Reinigung bereit.",
            "Zum Schluss spüle alle sichtbaren Auslässe, öffne die Leitungen zum Trocknen, setze ACTIVE und TARGET zurück und vermerke verbrauchtes Wasser, Tuch und Brennstoff."
        ),
        "workflow": "Strang isolieren > gebraucht ablassen > setzen > klare Fraktion ziehen > Becken spülen > Frischwasser > Voranteil prüfen/mischen > temperieren/verteilen > auffangen > erneut filtern > einmal wiederholen > trocknen/buchen",
        "purpose": "Lehrt den längsten Wartungszyklus, mehrere Stationen und kontrollierten PREVIOUS-Rückgriff.",
        "iconography": "Viele Becken, Läufe und Auslässe stützen einen hydraulischen Zyklus; konkrete Flussrichtung und Wiederverwendung sind nicht beschriftet.",
        "history": "Bad- und Wasseranlagen verlangen Reinigung, Heizung, Filtration und Abfluss; ein geschlossenes modernes Rückgewinnungssystem wäre anachronistisch.",
        "contradiction": "Die angenommene Wiederverwendung klarer Fraktionen ist hygienisch und technisch riskant und kann eine bloße Bildmetapher übermechanisieren.",
        "iatro_compare": "Iatromedizin liest denselben Ablauf als Lavage-/Badzyklus; der Rivale erklärt die lange Apparatefolge direkter, verliert aber den möglichen Körperzweck der Figuren.",
    },
    "B4": {
        "title": "Filtertuch-, Beckenrand- und Leitungswartung",
        "text": prose(
            "Nimm nach dem warmen Dienst das gebrauchte Filtertuch aus seinem Rahmen und halte den Restposten im Nebengefäß getrennt.",
            "Wähle einen kleinen Anteil sauberen Warmwassers, temperiere ihn und tränke damit ein grobes Arbeitstuch.",
            "Wische Beckenrand, Sitzbrett und sichtbare Ablagerungen am Zulauf ab; lege das warme Tuch kurz auf eine verhärtete Stelle und löse sie ohne scharfes Werkzeug.",
            "Führe den aktiven Posten durch frische Leinwand, spüle den Arbeitsort und lasse die schmutzige Fraktion vollständig ab.",
            "Fülle eine kleine Schlussportion nach, prüfe den freien Lauf und hänge beide Tücher getrennt zum Trocknen.",
            "Vermerke, welches Tuch für helle Wäsche und welches nur für Beckenarbeit wiederverwendet werden darf."
        ),
        "workflow": "Filtertuch entnehmen > Warmwasseranteil > Tuch temperieren > Ränder/Sitz/Zulauf reinigen > Ablagerung lösen > Rest filtrieren > ablassen > nachspülen > Tücher trennen/trocknen",
        "purpose": "Lehrt warme mechanische Reinigung und getrennte Tuchkreisläufe.",
        "iconography": "Becken und Läufe stützen Wartung; Filtertuch, Sitzbrett und Ablagerung sind lokale Ergänzungen.",
        "history": "Tuchfilter und manuelle Wannenreinigung sind einfache historische Techniken; der genaue Servicezettel ist nicht extern belegt.",
        "contradiction": "Menschennahe Bildpartien können eine Haut- oder Wundwäsche besser motivieren als eine Kalkablagerung.",
        "iatro_compare": "Der medizinische Text setzt Haut/Wunde und warme Auflage; der Rivale setzt Beckenrand/Ablagerung und behält Filter-, Spül- und Ablassfolge unverändert.",
    },
    "B5": {
        "title": "Zeitlich gehaltener Wärme- und Übergabeposten",
        "text": prose(
            "Ziehe den recordlokalen Restposten in das kleine Heizgefäß ab, erwärme ihn genau einmal und halte ihn bedeckt für die örtlich bestimmte Frist.",
            "Prüfe danach Geruch, Klarheit und ausreichende Wärme, verbinde ihn nur bei gleicher Qualität mit dem vorigen B5-Posten und übergib eine bemessene Portion an die nächste Badhausstation.",
            "Notiere Übergabezeit und Ziel, damit der Posten nicht ein zweites Mal erhitzt wird."
        ),
        "workflow": "Rest abziehen > einmal erwärmen > bedeckt halten > Qualität prüfen > B5-Vorposten vergleichen/verbinden > messen > nächste Station > Zeit notieren",
        "purpose": "Lehrt einen kurzen serviceinternen Übergabezettel mit Zeitkontrolle.",
        "iconography": "Der apparative f83r-Kontext stützt Stationen und Auslässe; ein Patient ist in diesem Nachtrag nicht nötig.",
        "history": "Chargenübergabe und einmaliges Erwärmen sind einfache Werkstattpraxis, aber kein spezifisch belegter mittelalterlicher Formulartyp.",
        "contradiction": "Zeit, Qualitätsprobe und Heizverbot sind vollständig exemplarisch und nicht durch die elf Karten ausgedrückt.",
        "iatro_compare": "Der technische Service braucht weniger Patient- und Therapierollen als ein medizinischer Nachtrag und gewinnt deshalb klar an lokaler Ökonomie.",
    },
    "B6": {
        "title": "Kalter Filter- und Zielübergabenachtrag",
        "text": prose(
            "Eröffne innerhalb von B6 einen neuen kalten oder vollständig abgekühlten Wasserposten und übernimm keinen aktiven Bestand aus B5.",
            "Miss eine kleine Portion, führe sie durch saubere Leinwand oder die einfache Öffnung und leite sie an den recordlokal bezeichneten Vorratskasten.",
            "Prüfe dort nur Klarheit und freien Lauf; lasse den Posten als offenen Kaltvorrat für den nächsten Dienst stehen."
        ),
        "workflow": "B6-Reset > kalten Posten eröffnen > messen > einfach filtern > Zielkasten > Klarheit/Lauf prüfen > offen bereitstellen",
        "purpose": "Lehrt Recordreset, kalte Reserve und offenen Schluss.",
        "iconography": "Auslass- und Beckenformen stützen eine technische Zielstation; kalte Qualität und Vorratszweck sind nicht sichtbar.",
        "history": "Kaltwasserreserve und einfache Tuchfiltration sind banal plausibel; die konkrete Zuordnung bleibt exemplarisch.",
        "contradiction": "Die kurze Folge könnte ebenso ein medizinischer Kaltgang sein; kein sichtbares Merkmal entscheidet den Zweck.",
        "iatro_compare": "Beide Lesungen teilen kalten Posten, Maß, Filter und Ziel; der Rivale vermeidet ausschließlich die unbelegte therapeutische Anwendung.",
    },
    "A1": {
        "title": "Siebenmalzwölf Werkstatt- und Qualitätswahlscheibe",
        "text": prose(
            "Dies ist die Wochen- und Qualitätstafel des Pflanzen-, Wasch- und Badhausbetriebs.",
            "Wähle zuerst einen der sieben Werkstatttage, danach eine der zwölf Arbeitsklassen und prüfe, ob Material, Wasser und Feuer die Arbeit erlauben.",
            A1_MATRIX,
            A1_CONDITIONS,
            "Das Ergebnis erlaubt, verkleinert oder verschiebt die bereits im Werkstattbuch bestimmte Arbeit; es benennt keine Krankheit und weist auf keinen einzelnen Herbal- oder Bio-Record.",
        ),
        "workflow": "einen von 7 Tagen > eine von 12 Arbeitsklassen > Material/Wasser/Feuer prüfen > eine von 8 Bedingungen > Arbeit erlauben/verkleinern/verschieben > lokal notieren",
        "purpose": "Lehrt eine vollständige 7×12-Auswahltabelle mit acht Qualitätsgates.",
        "iconography": "Die sichtbaren 7-, 12- und 8-Strukturen stützen Kardinalitäten; Wochentage und Arbeitsklassen sind externe Rivalenlabels.",
        "history": "Kalender, Arbeitsalmanache und Qualitätsregeln sind zeitgenössisch denkbar; Planet×Tierkreis besitzt jedoch die spezifischere historische 7×12-Parallele.",
        "contradiction": "Sieben Werkstatttage mal zwölf Arbeitsklassen sind eine erfundene Kreuzklassifikation ohne sichtbare Legende.",
        "iatro_compare": "Medizinische Astrologie erklärt 7 Planeten, 12 Zeichen/Körpersektoren und 8 Wahlbedingungen historisch genauer; der Rivale ist semantisch billiger, aber generischer.",
    },
    "A2": {
        "title": "Zentrum plus achtundzwanzig Adressen eines Monatsdienstplans",
        "text": A2_TEXT,
        "workflow": "Monatsblatt im Zentrum wählen > eine räumliche der 28 Adressen aufsuchen > genau deren Arbeitsauftrag lesen > Erledigung lokal markieren > Rotation nur aus Exemplar",
        "purpose": "Lehrt räumliches Nachschlagen ohne Prosakarten und ohne versteckten Kreisjoin.",
        "iconography": "Zentrum und 28 nichtzentrale Stern-/Stationsorte sind sichtbar; Monatsdienst und Aufgaben sind externe Inhalte.",
        "history": "Monatsrotas und Arbeitslisten sind allgemein plausibel; ein 28er-Mondhauskatalog ist die spezifischere historische Form.",
        "contradiction": "Die sternartigen Stationen tragen astronomische Bildargumente, während die 28 Werkstattaufgaben keinerlei sichtbare Zuordnung besitzen.",
        "iatro_compare": "Der Rivale kostet weniger externe Eigennamen, verliert aber die starke Mond-plus-28-Mondhäuser-Gattungsanalogie.",
    },
    "A3": {
        "title": "Unabhängige Achtundzwanzigerfolge von Werkstattregeln",
        "text": A3_TEXT,
        "workflow": "Kreisrubrik lesen > redaktionelle Regeladresse wählen > ganze lokale Regel ausführen > Ergebnis im Arbeitsbuch notieren > niemals mit A2 paaren",
        "purpose": "Lehrt eine geordnete, aber seitenlokale Sammlung von 28 ausführbaren Regeln.",
        "iconography": "Drei Kreisrubriken und 28 Radialeinträge stützen eine Regel-/Kalenderfolge; der konkrete Werkstattinhalt ist nicht sichtbar.",
        "history": "Arbeitskalender und Monatsregeln sind plausibel, medizinische Wahltage und Lunare besitzen jedoch reichere 28er-Traditionen.",
        "contradiction": "Die Regeln sind vollständig aus der Rivalenwelt geliefert; ohne Masterexemplar bleibt nur die 28er-Topologie.",
        "iatro_compare": "Beide Modelle benötigen ein lokales 28er-Exemplar. Medizin gewinnt an historischer Gattung, Werkstatt an geringerem Körper-/Therapieaufwand; f68 bleibt in beiden unverbunden.",
    },
}


ASSUMPTIONS: dict[str, dict[str, list[str]]] = {
    "H1": {"NONMEDICAL": ["IDENTITY:Wurzelkraut als Laugenstoff", "PROPERTY:reinigende Auszugsqualität", "MEDIUM:Holzasche und Regenwasser", "TARGET:Leinen und Holzwannen", "PURPOSE:Materiallagerung"], "IATROMEDICAL": ["IDENTITY:Teufelsabbiss/Skabiose", "PROPERTY:medizinische Wirksamkeit", "TARGET:Leibbeschwerde", "PARAMETER:therapeutische Dosis", "PURPOSE:innere Einnahme"]},
    "H2": {"NONMEDICAL": ["PROPERTY:Pflanzenfarbe", "MATERIAL:Alaun/Öl/Wachs", "TARGET:Bänder/Holz/Leder", "PURPOSE:zwei technische Produkte"], "IATROMEDICAL": ["IDENTITY:Teufelsabbiss", "PROPERTY:medizinische Wirkung", "TARGET:Geschwür/Schwellung", "PURPOSE:äußere Salbe"]},
    "H3": {"NONMEDICAL": ["IDENTITY:Duftpflanze", "PROPERTY:Duftauszug", "TARGET:Wäsche/Kämme/Bänke", "PURPOSE:Badhauspflege"], "IATROMEDICAL": ["IDENTITY:Veilchen", "PROPERTY:Gemüt-/Brustwirkung", "PARAMETER:Trankdosis", "TARGET:Augenumgebung"]},
    "H4": {"NONMEDICAL": ["IDENTITY:Breitblatt-Reiniger", "PROPERTY:reinigende Qualität", "TARGET:Tuch/Becken/Brett", "MATERIAL:Honigbinder", "PURPOSE:Holz-/Lederreparatur"], "IATROMEDICAL": ["IDENTITY:Allium/Wegerich", "PROPERTY:Wundwirkung", "TARGET:äußere Wunde", "PURPOSE:warmer Umschlag", "PARAMETER:medizinische Anwendung"]},
    "H5": {"NONMEDICAL": ["IDENTITY:Sonnentauartiges Klebkraut", "PROPERTY:technische Klebkraft", "TARGET:Leder/Stoff", "PURPOSE:Etikettenleim", "PURPOSE:Gefäßmarkierpaste"], "IATROMEDICAL": ["IDENTITY:Sonnentau", "TARGET:Warze/Hühnerauge", "PROPERTY:hautreizende Wirkung", "TARGET:trockener Husten", "PURPOSE:Brusttrank", "PARAMETER:therapeutische Gabe"]},
    "B1": {"NONMEDICAL": ["GENRE:gewöhnliches Badhaus", "MATERIAL:Pflanzenzusatz", "ROLE:Betreiber", "SYSTEM:Wasserkreislauf"], "IATROMEDICAL": ["GENRE:therapeutisches Bad", "ROLE:Patient", "MATERIAL:Kräuterflotte", "PURPOSE:Heilbehandlung", "SYSTEM:Apparatefluss"]},
    "B2": {"NONMEDICAL": ["GENRE:gewöhnlicher Badedienst", "ROLE:Badgast", "OBJECT:Sitzbecken", "PURPOSE:Hygiene/Tuchdienst"], "IATROMEDICAL": ["ROLE:Patient", "PURPOSE:Teilbadtherapie", "TARGET:Körperbereich", "PURPOSE:warme Auflage"]},
    "B3": {"NONMEDICAL": ["GENRE:Badhauswartung", "PROCESS:Rücklauf", "PROCESS:Wiederverwendung", "PURPOSE:Servicezyklus"], "IATROMEDICAL": ["ROLE:Patient", "PURPOSE:Lavage", "TARGET:Körperbereich", "PROCESS:zweiter Therapiezyklus", "SYSTEM:Rücklauf"]},
    "B4": {"NONMEDICAL": ["OBJECT:Filtertuch", "TARGET:Beckenablagerung", "PURPOSE:Leitungsreinigung", "PROCESS:Tuchtrennung"], "IATROMEDICAL": ["ROLE:Patient", "TARGET:Haut/Wunde", "PURPOSE:warme Auflage", "OBJECT:Tuch", "PURPOSE:Therapie"]},
    "B5": {"NONMEDICAL": ["OBJECT:Servicecharge", "PARAMETER:Haltezeit", "TARGET:nächste Station"], "IATROMEDICAL": ["OBJECT:medizinischer Posten", "ROLE:Patient", "PARAMETER:Therapiezeit", "TARGET:nächste Behandlung"]},
    "B6": {"NONMEDICAL": ["OBJECT:kalte Spülreserve", "PROCESS:einfache Filtration", "TARGET:Vorratskasten"], "IATROMEDICAL": ["PURPOSE:Kaltanwendung", "ROLE:Patient", "TARGET:Körperstelle", "PROCESS:Filtration"]},
    "A1": {"NONMEDICAL": ["VALUE:sieben Werkstatttage", "VALUE:zwölf Arbeitsklassen", "VALUE:acht Qualitätsbedingungen", "PURPOSE:Arbeitsplanung"], "IATROMEDICAL": ["VALUE:sieben Planeten", "VALUE:zwölf Tierkreiszeichen", "TARGET:Körpersektoren", "VALUE:acht Mondbedingungen", "PURPOSE:medizinische Wahl", "OBJECT:Eingriff"]},
    "A2": {"NONMEDICAL": ["OWNER:Monatsrota", "VALUE:28 Arbeitsadressen", "PURPOSE:Qualitäts-/Dienstplan"], "IATROMEDICAL": ["OWNER:Mond", "VALUE:28 Mondhäuser", "LABEL:externe Hausnamen", "PURPOSE:medizinisch-astrologische Konsultation", "ORDER:externe Orientierung"]},
    "A3": {"NONMEDICAL": ["VALUE:28 Werkstattregeln", "PURPOSE:Arbeitskalender", "CONTENT:konkrete Regeltexte"], "IATROMEDICAL": ["VALUE:28 Wahlregeln", "PURPOSE:medizinischer Wahlkalender", "CONTENT:Therapiehandlungen", "ORDER:externe Zeitordnung"]},
}


# Non-economy scores. Formal fidelity is fixed at five for both theories;
# assumption economy is computed mechanically from ASSUMPTIONS.
SCORES = {
    "H1": {"NONMEDICAL": (4, 5, 4, 4), "IATROMEDICAL": (5, 5, 5, 4)},
    "H2": {"NONMEDICAL": (4, 5, 4, 4), "IATROMEDICAL": (5, 5, 5, 4)},
    "H3": {"NONMEDICAL": (4, 4, 4, 4), "IATROMEDICAL": (5, 5, 5, 4)},
    "H4": {"NONMEDICAL": (4, 5, 4, 4), "IATROMEDICAL": (5, 5, 5, 4)},
    "H5": {"NONMEDICAL": (3, 4, 3, 4), "IATROMEDICAL": (4, 4, 5, 4)},
    "B1": {"NONMEDICAL": (5, 5, 5, 4), "IATROMEDICAL": (4, 5, 5, 4)},
    "B2": {"NONMEDICAL": (5, 5, 5, 4), "IATROMEDICAL": (5, 5, 5, 4)},
    "B3": {"NONMEDICAL": (5, 5, 5, 4), "IATROMEDICAL": (4, 5, 5, 4)},
    "B4": {"NONMEDICAL": (5, 5, 5, 4), "IATROMEDICAL": (4, 5, 4, 4)},
    "B5": {"NONMEDICAL": (5, 5, 4, 4), "IATROMEDICAL": (3, 4, 3, 4)},
    "B6": {"NONMEDICAL": (5, 5, 4, 4), "IATROMEDICAL": (3, 4, 3, 4)},
    "A1": {"NONMEDICAL": (4, 5, 4, 3), "IATROMEDICAL": (4, 5, 5, 3)},
    "A2": {"NONMEDICAL": (4, 5, 4, 3), "IATROMEDICAL": (4, 5, 5, 3)},
    "A3": {"NONMEDICAL": (4, 5, 4, 3), "IATROMEDICAL": (4, 5, 5, 3)},
}


IATRO_STRONGEST_CONTRADICTION = {
    "H1": "Krankheit, Einnahme und Dosis sind nicht sichtbar und nicht Kartenwerte.",
    "H2": "Geschwür, Schwellung und Salbenzweck stammen vollständig aus dem medizinischen Exemplar.",
    "H3": "Gemüt, Brust und Auge sind drei nicht sichtbare medizinische Zielergänzungen.",
    "H4": "Wunde und Körperstelle sind nicht abgebildet; die Flüssig-/Feststoffgabel bleibt technisch lesbar.",
    "H5": "Sonnentau, Warze und Husten ergeben eine besonders riskante doppelte Heiltradition.",
    "B1": "Badeapparat und Nutzer reichen aus; eine therapeutische Indikation fehlt.",
    "B2": "Badende sind sichtbar, aber Krankheit und Therapieart nicht.",
    "B3": "Die lange Leitungs-/Ablassfolge ist apparativ stärker verankert als eine Körperlavage.",
    "B4": "Tuch und warme Waschung können ebenso Gerätewartung sein.",
    "B5": "Der technische Nachtrag benötigt weder Patient noch Körperziel.",
    "B6": "Die offene kalte Übergabe hat keinen sichtbaren medizinischen Empfänger.",
    "A1": "Kein sichtbarer Querindex bindet Planet/Tierkreis an einen medizinischen Record.",
    "A2": "Mond und Hausnamen sind externe Editionswerte; Start und Richtung bleiben offen.",
    "A3": "Die 28 medizinischen Regeln sind vollständig lokaler Exemplartext und nicht mit A2 verbunden.",
}


def assumption_economy(cost: int) -> int:
    if cost <= 3:
        return 5
    if cost <= 6:
        return 4
    if cost <= 9:
        return 3
    if cost <= 12:
        return 2
    if cost <= 15:
        return 1
    return 0


def split_text(text: str, count: int) -> list[str]:
    words = norm(text).split(" ")
    if len(words) < count:
        raise AssertionError(f"source text has only {len(words)} words for {count} groups")
    chunks: list[str] = []
    start = 0
    for index in range(count):
        stop = round((index + 1) * len(words) / count)
        chunks.append(" ".join(words[start:stop]))
        start = stop
    assert all(chunks)
    assert norm(" ".join(chunks)) == norm(text)
    return chunks


def build_rubric() -> list[dict[str, object]]:
    return [
        {"criterion": "C1_FORMAL_FIDELITY", "max_points": 5, "frozen_rule": "5 only when every exact ID, formal slot, mnemonic, register transition, namespace and rendered surface is preserved; subtract one per changed layer class", "symmetry": "same rule for both theories"},
        {"criterion": "C2_ICONOGRAPHY_FIT", "max_points": 5, "frozen_rule": "5 direct visible owner/apparatus/topology; 3 compatible but external purpose; 0 contradiction", "symmetry": "images may supply owners/objects but never card meanings"},
        {"criterion": "C3_WORKFLOW_EXECUTABILITY", "max_points": 5, "frozen_rule": "5 complete ordered executable workflow with reset/close; 3 substantial gaps; 0 incoherent", "symmetry": "same selected V61--V63 structure"},
        {"criterion": "C4_ASSUMPTION_ECONOMY", "max_points": 5, "frozen_rule": "5 for 0--3 explicit unsupported items; 4 for 4--6; 3 for 7--9; 2 for 10--12; 1 for 13--15; 0 above 15", "symmetry": "every concrete noun/property/purpose/external label costs one"},
        {"criterion": "C5_HISTORICAL_GENRE_FIT", "max_points": 5, "frozen_rule": "5 specific circa-1420 genre/process family; 3 only broad miscellany analogy; 0 anachronistic", "symmetry": "history calibrates source world, never signs"},
        {"criterion": "C6_CROSS_UNIT_PURPOSE", "max_points": 5, "frozen_rule": "5 direct coherent purpose without unshown joins; 3 library-level coherence only; 0 incompatible", "symmetry": "no score for an invented f68-to-f69 or Astro-to-prose key"},
    ]


def main() -> None:
    base = read_tsv(BASE_LEDGER)
    base_units = read_tsv(BASE_UNITS)
    assert len(base) == 776 and len(base_units) == 14
    assert set(UNIT_CONTENT) == set(UNIT_ORDER)
    assert {r["page"] for r in base} == ALLOWED_PAGES
    assert all(not r["page"].startswith("f84") for r in base)

    by_unit: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in base:
        by_unit[row["unit_id"]].append(row)
    assert {unit: len(rows) for unit, rows in by_unit.items()} == EXPECTED_UNIT_COUNTS
    base_unit_by_id = {row["unit_id"]: row for row in base_units}

    score_rows: list[dict[str, object]] = []
    assumption_rows: list[dict[str, object]] = []
    score_by_unit_theory: dict[tuple[str, str], int] = {}
    for unit in UNIT_ORDER:
        for theory in ("NONMEDICAL", "IATROMEDICAL"):
            assumptions = ASSUMPTIONS[unit][theory]
            for index, item in enumerate(assumptions, 1):
                category, description = item.split(":", 1)
                assumption_rows.append({"assumption_id": f"{unit}-{theory[0]}{index:02d}", "unit_id": unit, "theory": theory, "category": category, "unsupported_assumption": description, "cost": 1, "not_a_card_meaning": "YES"})
            icon, workflow, historical, cross = SCORES[unit][theory]
            economy = assumption_economy(len(assumptions))
            total = 5 + icon + workflow + economy + historical + cross
            score_by_unit_theory[(unit, theory)] = total
            score_rows.append({
                "unit_id": unit, "page": base_unit_by_id[unit]["page"], "theory": theory,
                "C1_formal_fidelity": 5, "C2_iconography_fit": icon,
                "C3_workflow_executability": workflow, "C4_assumption_economy": economy,
                "C5_historical_genre_fit": historical, "C6_cross_unit_purpose": cross,
                "unsupported_assumption_cost": len(assumptions), "total_of_30": total,
            })
    write_tsv(OUT / "V68_R1_FROZEN_SYMMETRIC_RUBRIC.tsv", build_rubric())
    write_tsv(OUT / "V68_R1_ASSUMPTION_COSTS.tsv", assumption_rows)
    write_tsv(OUT / "V68_R1_UNIT_SCORE_COMPARISON.tsv", score_rows)

    output_ledger: list[dict[str, object]] = []
    fragments_by_unit: dict[str, list[str]] = {}
    for unit in UNIT_ORDER:
        fragments_by_unit[unit] = split_text(UNIT_CONTENT[unit]["text"], EXPECTED_UNIT_COUNTS[unit])
    position = Counter()
    preserve_columns = [
        "universal_group_serial", "register", "unit_id", "page", "source_serial", "locus",
        "field_or_address", "statement_or_station", "exact_card_or_local_group_id", "formal_value",
        "atomic_or_whole_card_mnemonic", "source_order_slot", "abbreviation_channel",
        "register_state_before", "register_update", "register_state_after", "selected_parse_status",
        "terminal_status", "renderer_instruction", "rendered_surface",
    ]
    for row in base:
        unit = row["unit_id"]
        position[unit] += 1
        fragment = fragments_by_unit[unit][position[unit] - 1]
        if row["register"] == "ASTRO":
            anchor = "ASTRO_PAGE_LOCAL_ADDRESS; NO_PROSE_CARD_OR_MNEMONIC"
        elif row["atomic_or_whole_card_mnemonic"] != "UNKNOWN":
            anchor = f"FROZEN_V60_MNEMONIC={row['atomic_or_whole_card_mnemonic']}; LOCAL_OBJECTS_NOT_INCLUDED"
        elif row["selected_parse_status"] not in {"UNPARSED_EXEMPLAR", ""}:
            anchor = f"FROZEN_FORMAL_SLOT={row['source_order_slot']}; NO_LEXICAL_EXPANSION"
        else:
            anchor = "UNKNOWN_OR_EXEMPLAR_ONLY; COPY_EXACT_ID"
        out = {column: row[column] for column in preserve_columns}
        out.update({
            "iatromedical_selected_local_expansion": row["local_selected_source_fragment"],
            "nonmedical_rival_local_expansion": fragment,
            "frozen_anchor_note": anchor,
            "nonmedical_source_status": "RECORD_OR_PAGE_LOCAL_EXEMPLAR; NOT_CARD_VALUE",
            "rival_unit_text_digest": digest(UNIT_CONTENT[unit]["text"]),
            "rival_fragment_digest": digest(fragment),
            "mechanical_identity_token_from_v67": row["mechanical_roundtrip_token"],
            "adversarial_roundtrip_status": "PASS_FROZEN_IDENTITY_PLUS_LOCAL_RIVAL_EXEMPLAR",
        })
        output_ledger.append(out)
    write_tsv(OUT / "V68_R1_776_GROUP_NONMEDICAL_LEDGER.tsv", output_ledger)

    edition_rows: list[dict[str, object]] = []
    contradiction_rows: list[dict[str, object]] = []
    for unit in UNIT_ORDER:
        info = UNIT_CONTENT[unit]
        base_unit = base_unit_by_id[unit]
        n_score = score_by_unit_theory[(unit, "NONMEDICAL")]
        i_score = score_by_unit_theory[(unit, "IATROMEDICAL")]
        winner = "NONMEDICAL" if n_score > i_score else "IATROMEDICAL" if i_score > n_score else "TIE"
        direct = f"{winner}; NONMEDICAL={n_score}/30; IATROMEDICAL={i_score}/30. {info['iatro_compare']}"
        edition_rows.append({
            "unit_id": unit, "page": base_unit["page"], "register": base_unit["register"],
            "group_count": EXPECTED_UNIT_COUNTS[unit], "field_or_locus_count": base_unit["field_or_locus_count"],
            "statement_count": base_unit["statement_count"], "nonmedical_article_or_diagram_title": info["title"],
            "complete_nonmedical_German_text": info["text"], "executable_workflow": info["workflow"],
            "teaching_purpose": info["purpose"], "explicit_iconographic_argument": info["iconography"],
            "explicit_historical_argument": info["history"], "strongest_nonmedical_contradiction": info["contradiction"],
            "complete_selected_iatromedical_baseline": base_unit["complete_selected_source_or_diagram_reading"],
            "direct_iatromedical_comparison": direct,
            "nonmedical_assumption_cost": len(ASSUMPTIONS[unit]["NONMEDICAL"]),
            "iatromedical_assumption_cost": len(ASSUMPTIONS[unit]["IATROMEDICAL"]),
            "nonmedical_score_of_30": n_score, "iatromedical_score_of_30": i_score,
            "unit_winner": winner, "semantic_contract": "FULL_LOCAL_RIVAL_EDITION; NO_NEW_CARD_MEANING",
        })
        contradiction_rows.append({
            "unit_id": unit, "page": base_unit["page"],
            "nonmedical_prediction": info["workflow"],
            "strongest_contradiction_to_nonmedical": info["contradiction"],
            "strongest_contradiction_to_iatromedical": IATRO_STRONGEST_CONTRADICTION[unit],
            "current_discriminator": "ICONOGRAPHY_AND_HISTORICAL_GENRE_ONLY; NO_CARD_SEMANTIC_DISCRIMINATOR",
            "unit_winner_under_frozen_rubric": winner,
        })
    write_tsv(OUT / "V68_R1_14_UNIT_ADVERSARIAL_EDITION.tsv", edition_rows)
    write_tsv(OUT / "V68_R1_CONTRADICTION_LEDGER.tsv", contradiction_rows)

    n_total = sum(score_by_unit_theory[(u, "NONMEDICAL")] for u in UNIT_ORDER)
    i_total = sum(score_by_unit_theory[(u, "IATROMEDICAL")] for u in UNIT_ORDER)
    winners = Counter(row["unit_winner"] for row in edition_rows)
    build_summary = {
        "status": "PASS",
        "pages": len({r["page"] for r in output_ledger}),
        "units": len(edition_rows),
        "groups": len(output_ledger),
        "register_counts": dict(Counter(r["register"] for r in output_ledger)),
        "nonmedical_total_of_420": n_total,
        "iatromedical_total_of_420": i_total,
        "nonmedical_margin": n_total - i_total,
        "unit_winners": dict(winners),
        "verdict": "NONMEDICAL_NUMERIC_WIN_BY_ONE_POINT; SUBSTANTIVE_TIE_AND_NOT_ROBUST",
        "new_card_meanings": 0,
        "direct_f68_f69_joins": 0,
        "phonetic_or_letter_claims": 0,
    }
    (OUT / "V68_R1_BUILD_SUMMARY.json").write_text(json.dumps(build_summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
