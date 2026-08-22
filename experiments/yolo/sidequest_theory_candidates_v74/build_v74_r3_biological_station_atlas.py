#!/usr/bin/env python3
"""Build V74 R3's complete Biological station-atlas third edition.

The output is a creative, executable bathhouse/apparatus/register reading over
the frozen V69 events, V71 owners, and V72 statements.  It never creates a
global flow direction and never promotes a concrete default into card meaning.
"""

from __future__ import annotations

import csv
import hashlib
import json
import re
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
V69 = ROOT / "experiments/yolo/sidequest_theory_candidates_v69"
V70 = ROOT / "experiments/yolo/sidequest_theory_candidates_v70"
V71 = ROOT / "experiments/yolo/sidequest_theory_candidates_v71"
V72 = ROOT / "experiments/yolo/sidequest_theory_candidates_v72"
V73 = ROOT / "experiments/yolo/sidequest_theory_candidates_v73"

EVENT_SOURCE = V69 / "V69_R4_FINAL_381_PROSE_EVENT_INTERLINEAR.tsv"
FIELD_SOURCE = V69 / "V69_R4_FINAL_135_FIELD_EDITION.tsv"
OWNER_SOURCE = V71 / "V71_SELECTED_OWNER_LEDGER.tsv"
STATEMENT_SOURCE = V72 / "V72_SELECTED_116_STATEMENTS.tsv"
IMAGE_SOURCE = V70 / "V70_SELECTED_TEN_PAGE_IMAGE_REVISION.tsv"
CONTINUITY_SOURCE = V73 / "V73_FOUR_ROLE_SELECTION.md"


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: list[dict[str, object]], columns: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        for row in rows:
            writer.writerow({column: row[column] for column in columns})


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


STATIONS: dict[str, dict[str, str]] = {
    "B1_SHARED_TWO_ROW_POOL": {
        "gloss": "gemeinsames zweireihiges f81v-Becken-/Figurenfeld",
        "operation": "Belegungs-, Wasserstands-, Zeit- und Reinigungsregister eines gemeinsam bedienten Badefeldes",
        "medical": "gemeinsames therapeutisches Bad mit patienten- oder indikationsbezogenen Plätzen",
        "formal": "allegorisches Kollektivbild oder geordnete Figurentafel ohne ausführbare Badhandlung",
        "contact": "Alle ungefähr sechzehn Figuren liegen in derselben grünen Umgrenzung; keine Reihenfolge ist gezeichnet.",
        "break": "Keine Bildkante verbindet dieses Feld mit f82r oder f83r.",
        "lead": "OPERATIONAL_AND_MEDICAL_BATH_READINGS_BOTH_OPEN",
    },
    "B2_UPPER_PAIRED_BASINS_AND_CYLINDER": {
        "gloss": "obere f82r-Paarbecken-/Zylinderstation",
        "operation": "parallel geführte Beckenposten mit gemeinsam geprüftem Mittelzylinder und lokalen Anschlussbögen",
        "medical": "zwei örtliche therapeutische Bade- oder Applikationsplätze mit gemeinsamem Vorratsgefäß",
        "formal": "benachbarte Figuren-, Bogen- und Zylindervignetten ohne gemeinsame Bedienung",
        "contact": "Bögen treffen den Mittelzylinder und eine Hand hält ein Bogenende; die Richtung bleibt offen.",
        "break": "Vor der mittleren linken Station beginnt ein neuer sichtbarer Besitzer.",
        "lead": "LOCAL_APPARATUS_OPERATION_LEAD",
    },
    "B2_MIDDLE_LEFT_DEVICE_AND_INLINE_NODE": {
        "gloss": "mittlere linke f82r-Geräte-/Inline-Knotenstation",
        "operation": "Prüf- und Wartungsposten für Handgerät, Ring-/Fächerform und durchlaufenden lokalen Knoten",
        "medical": "örtliche Dampf-, Sprüh- oder Waschbehandlung an einer Figur",
        "formal": "ikonographischer Strahl, Stern oder Schmuckband mit beigeschriebener Legende",
        "contact": "Wellenlinien setzen am Handgerät an; der Doppelstrich läuft durch den Sternknoten, aber ohne Pfeil.",
        "break": "Die nahe Linie über dem rechten Liegepodest berührt es nicht sicher.",
        "lead": "LOCAL_DEVICE_OPERATION_SLIGHT_LEAD",
    },
    "B2_MIDDLE_RIGHT_AMBIGUOUS_STATION": {
        "gloss": "ungelöste mittlere f82r-Linien-/Liegepodeststation",
        "operation": "gesperrter Werkstattposten, der Linie und Liegepodest getrennt hält, bis das Exemplar den Besitzer nennt",
        "medical": "unabhängiger Liege-, Ruhe- oder Behandlungsposten",
        "formal": "Fortsetzung der Inline-Legende oder bloße freie Texttasche",
        "contact": "Linie und Podest sind nur nahe; ein tatsächlicher Kontakt ist nicht sichtbar gesichert.",
        "break": "Kein Stoff- oder Arbeitsstand darf über diesen ungelösten Besitzer hinweg vererbt werden.",
        "lead": "FORMAL_QUARANTINE_LEAD",
    },
    "B2_LOWER_GREEN_MULTI_FIGURE_POOL": {
        "gloss": "unteres grünes f82r-Mehrfigurenfeld",
        "operation": "Belegungs-, Reinigungs- und Losregister eines gemeinsamen unteren Bade- oder Waschfeldes",
        "medical": "Gruppenbad oder Reihenfolge örtlicher therapeutischer Anwendungen",
        "formal": "allegorisches Mehrfigurenfeld mit unabhängigen Bildrollen",
        "contact": "Mehrere Figuren schneiden dieselbe grüne Fläche; lokale Plätze sind sichtbar, aber kein Rundlauf.",
        "break": "Der Übergang von der ungelösten mittleren Station und zu den Randposten wird jeweils neu gesetzt.",
        "lead": "OPERATIONAL_AND_MEDICAL_POOL_READINGS_BOTH_OPEN",
    },
    "B2_LOWER_POOL_EDGE_STATIONS": {
        "gloss": "lokale f82r-Figuren-/Gefäßposten am unteren Feldrand",
        "operation": "einzeln geführte Randposten für Gefäß, Tuch, Platz und Abschluss am gemeinsamen Feld",
        "medical": "einzelne therapeutische Anwendungen an Figuren am Beckenrand",
        "formal": "wiederholte ikonographische Figurenplätze ohne gemeinsame Betriebsfunktion",
        "contact": "Gefäße und Figuren liegen am Feldrand; keine Leitung koppelt die einzelnen Plätze.",
        "break": "Das gemeinsame grüne Feld darf nicht automatisch jeden Randposten speisen.",
        "lead": "LOCAL_STATION_REGISTER_LEAD",
    },
    "B3_UPPER_MARGIN_OPEN_FAN_STATION": {
        "gloss": "obere f83r-Randstation mit offenem Fächerende",
        "operation": "lokaler Kontroll-, Tuch- oder Auffangposten an einem offenen Endmotiv",
        "medical": "örtliche Kopf-, Dampf- oder Spülbehandlung an der oberen Randfigur",
        "formal": "Strahlen- oder Fächerattribut mit zugehöriger Legende",
        "contact": "Figur und offenes Fächermotiv gehören lokal zusammen; die offenen Enden geben keine Richtung.",
        "break": "Zur mittleren Rundgefäßstation besteht keine gezeichnete Leitung.",
        "lead": "ICONOGRAPHIC_AND_OPERATIONAL_TIE",
    },
    "B3_MIDDLE_MARGIN_ROUND_VESSEL_STATION": {
        "gloss": "mittlere f83r-Randfigur im Rundgefäß",
        "operation": "einzeln geführter Füll-, Ruhe-, Reinigungs- und Abschlussplatz eines Rundgefäßes",
        "medical": "Einzelbad oder örtliche therapeutische Anwendung im runden Gefäß",
        "formal": "selbständige Figurenvignette oder Bildlegende innerhalb eines Dreierstapels",
        "contact": "Figur und Rundgefäß bilden eine lokale Station; zum oberen und unteren Posten fehlt die Leitung.",
        "break": "Kein Zustand geht ohne neuen Besitzer an die Korbstation weiter.",
        "lead": "LOCAL_BATH_OR_VESSEL_OPERATION_LEAD",
    },
    "B3_LOWER_MARGIN_BASKET_VESSEL_STATION": {
        "gloss": "untere f83r-Randfigur im korbartigen Gefäß",
        "operation": "lokaler Lade-, Wasch-, Abtropf- und Vorratsposten eines korbartigen Behälters",
        "medical": "Einzelbad, Kräuterauflage oder örtliche Waschbehandlung",
        "formal": "dritte Figurenvignette eines ikonographischen Randstapels",
        "contact": "Figur und Korb-/Schuppenform sind lokal gebunden; freie Striche enden offen.",
        "break": "Nach F086 folgt eine echte unverbundene Bildlücke.",
        "lead": "LOCAL_VESSEL_OPERATION_LEAD",
    },
    "B3_MARGIN_TO_MAIN_GAP_UNRESOLVED": {
        "gloss": "ungelöster f83r-Zwischenposten zwischen Randstapel und Hauptpaar",
        "operation": "Quarantäne- und Warteposten im Register; Werte werden notiert, aber keiner Bildstation physisch übergeben",
        "medical": "ausgelassene Fortsetzung einer Randbehandlung oder Beginn der Hauptpaaranwendung",
        "formal": "freier Text-/Exemplarbereich ohne rekonstruierbaren Bildbesitzer",
        "contact": "Zwischen Randstapel und Hauptpaar ist keine gezeichnete Kante vorhanden.",
        "break": "F087 beginnt und F099 beendet die ungelöste Zone jeweils mit sichtbarem Reset.",
        "lead": "FORMAL_QUARANTINE_LEAD",
    },
    "B3_MAIN_ARCH_LINKED_PAIR": {
        "gloss": "unteres f83r-Hauptpaar am gemeinsamen Bogen",
        "operation": "gekoppelter Vergleichs- oder Doppelbedienposten mit zwei Seiten unter einem ungerichteten Bogen",
        "medical": "paarige therapeutische Bade- oder Übertragungsdarstellung",
        "formal": "zwei Figuren unter Regenbogen- oder Himmelsband",
        "contact": "Der breite Bogen verbindet beide Figuren tatsächlich; Quelle, Senke und Richtung fehlen.",
        "break": "Die vorausgehende ungelöste Zone wird vor F099 vollständig verlassen.",
        "lead": "UNORIENTED_PAIRED_STATION_LEAD",
    },
    "B4_MAIN_ARCH_LINKED_PAIR": {
        "gloss": "f83r-Hauptpaar als eigener B4-Record",
        "operation": "neue Doppelstationsbuchung für zwei unter einem sichtbaren Bogen gekoppelte Plätze",
        "medical": "therapeutische Paaranwendung oder gemeinsamer Badeabschnitt",
        "formal": "dekoratives Figurenpaar unter einem Bogen",
        "contact": "Beide Seiten teilen den sichtbaren Bogen; B4 beginnt trotzdem mit geleerten Registern.",
        "break": "Der spätere Wechsel zu den Unterläufen setzt neue lokale Besitzer.",
        "lead": "UNORIENTED_PAIRED_STATION_LEAD",
    },
    "B4_MAIN_LEFT_OPEN_FRINGE_STATION": {
        "gloss": "linker f83r-Unterlauf mit offenen Fransen",
        "operation": "lokaler Sammel-, Ablass-, Tuch- und Wartungsposten an mehreren offenen Enden",
        "medical": "örtliche Ableitung, Waschung oder Auflage an der linken Figur",
        "formal": "ornamentaler Schweif oder Fransensaum",
        "contact": "Der gefüllte Unterlauf setzt am linken Gefäß an und endet offen; die Betriebsrichtung bleibt unbekannt.",
        "break": "Der Record setzt den Unterlauf als neuen Besitzer und später den rechten S-Lauf nochmals neu.",
        "lead": "LOCAL_OUTLET_MAINTENANCE_LEAD",
    },
    "B4_MAIN_RIGHT_S_RUN_MULTIPORT_STATION": {
        "gloss": "rechter f83r-S-Lauf mit Mehrarmknoten",
        "operation": "lokaler Mehranschluss-Prüf-, Verteil- oder Sammelposten ohne festgelegte Strömungsrichtung",
        "medical": "mehrfache örtliche Anwendung oder Ableitung an der rechten Figur",
        "formal": "Band- oder Rosettenornament mit beigeschriebener Legende",
        "contact": "Die S-Kontur trifft sichtbar den blauen Mehrarmknoten; alle Arme bleiben ungerichtet.",
        "break": "Kein unmittelbarer Besitzerübergang vom linken Fransenposten ist gezeichnet.",
        "lead": "LOCAL_MULTIPORT_OPERATION_LEAD",
    },
    "B5_LEFT_OPEN_FRINGE_STATION": {
        "gloss": "linker offener f83r-Endposten im eigenen B5-Record",
        "operation": "selbständige Wartungs-, Auffang- und Abschlussbuchung nur für den linken offenen Posten",
        "medical": "selbständige linke therapeutische Ableitung oder Waschung",
        "formal": "isolierte Bildlegende zum linken Ornament",
        "contact": "Lauf und freie Enden bilden lokal eine sichtbare Figur; keine Richtung ist markiert.",
        "break": "B5 endet vollständig; B6 darf nichts aus ACTIVE, TARGET oder PREVIOUS übernehmen.",
        "lead": "LOCAL_END_STATION_REGISTER_LEAD",
    },
    "B6_RIGHT_S_RUN_MULTIPORT_STATION": {
        "gloss": "rechter f83r-S-Lauf-/Mehrarm-Endposten im eigenen B6-Record",
        "operation": "selbständige Prüf-, Ziel- und Abschlussbuchung nur für den rechten Mehrarmknoten",
        "medical": "selbständige rechte therapeutische Anwendung oder Ableitung",
        "formal": "isolierte Bildlegende zum S-Band und Knotenornament",
        "contact": "S-Lauf und Mehrarmknoten sind lokal verbunden, aber weder Arm noch Flussrichtung ist ausgezeichnet.",
        "break": "B6 beginnt nach einem harten Recordreset und erbt keinen B5-Wert.",
        "lead": "LOCAL_MULTIPORT_REGISTER_LEAD",
    },
}


EXEMPLAR_ACTIONS: dict[str, list[str]] = {
    "B1_SHARED_TWO_ROW_POOL": [
        "Zähle die belegten Plätze in beiden Figurenreihen und trage die Summe in diesen Feldposten ein.",
        "Prüfe den gemeinsamen Wasserstand an der grünen Einfassung und markiere den örtlichen Sollstrich.",
        "Weise den nächsten freien Badeplatz innerhalb derselben Umgrenzung zu.",
        "Lege für den bezeichneten Platz ein sauberes Tuch und ein Arbeitsgefäß bereit.",
        "Markiere den eben gereinigten Platz als frei, ohne daraus eine Reihenfolge der Figuren abzuleiten.",
        "Erneuere die am Platz verbrauchte Wassermenge aus einem unbebilderten Vorrat.",
    ],
    "B2_UPPER_PAIRED_BASINS_AND_CYLINDER": [
        "Vergleiche die Füllstände der beiden oberen Figurenbecken und notiere nur die Abweichung.",
        "Prüfe beide sichtbaren Bogenkontakte am Mittelzylinder, ohne Ein- und Ausgang festzulegen.",
        "Reinige den Rand des im Exemplar bezeichneten oberen Beckens.",
        "Halte den Mittelzylinder geschlossen und notiere seinen örtlichen Arbeitszustand.",
        "Weise einen der beiden oberen Figurenplätze als nächsten Bedienposten aus.",
        "Lege an beiden Seiten gleiche Tuch- oder Gefäßposten für den Parallelvergleich bereit.",
    ],
    "B2_MIDDLE_LEFT_DEVICE_AND_INLINE_NODE": [
        "Prüfe das Handgerät und den lokalen Wellenansatz auf freien sichtbaren Kontakt.",
        "Wische Ring-/Fächerform und Inline-Knoten vor der nächsten Benutzung sauber.",
        "Notiere den Zustand des Doppelstrichs beiderseits des Sternknotens, ohne Flussrichtung einzutragen.",
        "Lege den im Exemplar bezeichneten Geräteposten für eine örtliche Wasch- oder Dampfprobe bereit.",
        "Sperre den Knoten während der Geräteprüfung als eigenen lokalen Posten.",
        "Markiere die abgeschlossene Geräteprüfung im f82r-Mittelstationsregister.",
    ],
    "B2_MIDDLE_RIGHT_AMBIGUOUS_STATION": [
        "Trage Linie und Liegepodest als zwei unzugeordnete Posten ein und sperre jede Übergabe zwischen ihnen.",
        "Prüfe vor Bedienung, ob das Exemplar den Linienposten oder das Liegepodest bezeichnet.",
        "Bereite das Liegepodest unabhängig von der darüberliegenden Linie als Ruhe- oder Arbeitsfläche vor.",
        "Halte Material und Tuch dieses Postens getrennt von der mittleren linken Knotenstation.",
    ],
    "B2_LOWER_GREEN_MULTI_FIGURE_POOL": [
        "Zähle die aktuell belegten Figurenplätze im unteren grünen Feld.",
        "Prüfe den gemeinsamen örtlichen Wasser- oder Arbeitsstand am Rand des unteren Feldes.",
        "Weise einen freien Figurenplatz im unteren Feld für den nächsten Arbeitsgang aus.",
        "Reinige nur den bezeichneten Platz und markiere ihn anschließend als bereit.",
        "Lege eine frische Tuch- oder Gefäßportion am bezeichneten unteren Platz bereit.",
        "Buche die Verweildauer des aktuellen Platzes, ohne einen Rundlauf anzunehmen.",
    ],
    "B2_LOWER_POOL_EDGE_STATIONS": [
        "Reinige das kleine Gefäß am bezeichneten unteren Randposten.",
        "Weise der zugehörigen Randfigur einen eigenen Tuch- und Arbeitslosposten zu.",
        "Prüfe den Kontakt dieses Postens zur grünen Feldkante; ergänze keine Leitung.",
        "Fülle nur das örtliche Randgefäß aus einem unbebilderten Vorrat.",
        "Markiere den einzelnen Randposten nach Gebrauch als geschlossen.",
        "Halte benachbarte Randposten als getrennte Buchungen auseinander.",
    ],
    "B3_UPPER_MARGIN_OPEN_FAN_STATION": [
        "Prüfe die offenen Punkt-/Fächerenden und notiere, welche frei bleiben.",
        "Lege ein Tuch oder kleines Auffanggefäß unmittelbar an der oberen Randstation bereit.",
        "Reinige nur den sichtbaren lokalen Fächerkontakt an der oberen Figur.",
        "Markiere den offenen Endposten nach der örtlichen Probe als geprüft.",
    ],
    "B3_MIDDLE_MARGIN_ROUND_VESSEL_STATION": [
        "Prüfe den Füllstand des runden Einzelgefäßes an der mittleren Randfigur.",
        "Reinige Rand und Innenfläche dieses Rundgefäßes vor dem nächsten Posten.",
        "Weise der mittleren Figur eine eigene Ruhe- oder Waschdauer zu.",
        "Schließe nur diese Rundgefäßbuchung und vererbe nichts an den Randstapel.",
    ],
    "B3_LOWER_MARGIN_BASKET_VESSEL_STATION": [
        "Lege den im Exemplar bezeichneten Tuch- oder Materialposten in das korbartige Gefäß.",
        "Spüle das korbartige Gefäß lokal und lasse es an seinen offenen Enden abtropfen, ohne Richtung festzulegen.",
        "Prüfe die untere Randfigur und ihr Gefäß als einen gemeinsamen Bedienposten.",
        "Nimm den getrockneten Materialposten aus dem Korb und schließe nur diese Buchung.",
    ],
    "B3_MARGIN_TO_MAIN_GAP_UNRESOLVED": [
        "Kopiere den Exemplarwert in einen Quarantäneposten, ohne ihn einer Bildstation zuzuweisen.",
        "Halte ACTIVE, TARGET und Material dieses Zwischenpostens von Randstapel und Hauptpaar getrennt.",
        "Notiere die ungelöste Besitzerfrage und setze jede physische Übergabe aus.",
        "Schließe den örtlichen Formularposten, ohne eine unsichtbare Verbindung zu ergänzen.",
    ],
    "B3_MAIN_ARCH_LINKED_PAIR": [
        "Vergleiche die Zustände beider Seiten des sichtbaren Bogens, ohne Quelle und Senke zu bestimmen.",
        "Reinige beide Figurenplätze des Hauptpaars als gleichrangige lokale Posten.",
        "Lege an beiden Seiten gleiche Arbeitsgefäße oder Tücher für den Paarvergleich bereit.",
        "Prüfe den Bogenkontakt an beiden Enden und notiere nur Kontakt vorhanden oder offen.",
        "Markiere den im Exemplar bezeichneten Platz innerhalb des Paars als aktuellen Bedienposten.",
        "Schließe den Doppelposten, ohne einen Rücklauf zum Randstapel zu buchen.",
    ],
    "B4_MAIN_ARCH_LINKED_PAIR": [
        "Eröffne im B4-Record einen neuen Paarvergleich für beide Seiten des sichtbaren Bogens.",
        "Prüfe beide Bogenenden auf Kontakt und halte ihre Betriebsrichtung unbestimmt.",
        "Reinige den im Exemplar gewählten Figurenplatz des Paars.",
        "Lege für beide Seiten gleiche lokale Arbeitsmittel bereit.",
        "Notiere den Zustandsunterschied der zwei Paarplätze.",
        "Schließe den aktuellen Paarposten vor dem Wechsel zu einem Unterlauf.",
    ],
    "B4_MAIN_LEFT_OPEN_FRINGE_STATION": [
        "Prüfe alle offenen Fransenenden des linken Unterlaufs auf freien Abschluss.",
        "Lege ein Auffangtuch unter die offenen Enden, ohne eine Ausflussrichtung zu behaupten.",
        "Reinige den gefüllten linken Unterlauf als eigenen lokalen Posten.",
        "Notiere, welche Fransenenden offen, belegt oder verschlossen sind.",
        "Schließe die linke Unterlaufbuchung vor jedem Wechsel zum rechten S-Lauf.",
    ],
    "B4_MAIN_RIGHT_S_RUN_MULTIPORT_STATION": [
        "Prüfe S-Lauf und Mehrarmknoten auf sichtbaren lokalen Kontakt.",
        "Notiere jeden freien Arm des Knotens, ohne Einlass und Auslass zu unterscheiden.",
        "Reinige den im Exemplar bezeichneten Knotenarm als eigenen Posten.",
        "Lege gleiche Auffang- oder Tuchposten an den bezeichneten freien Armen bereit.",
        "Schließe nur den rechten Mehrarmposten und erzeuge keinen globalen Rücklauf.",
    ],
    "B5_LEFT_OPEN_FRINGE_STATION": [
        "Eröffne nach hartem Recordreset einen selbständigen linken Fransenposten.",
        "Prüfe und reinige die offenen Enden nur innerhalb B5.",
        "Lege einen örtlichen Auffang- oder Tuchposten für B5 bereit.",
        "Streiche den linken Endposten ab und lösche alle B5-Registerwerte.",
    ],
    "B6_RIGHT_S_RUN_MULTIPORT_STATION": [
        "Eröffne B6 mit leerem Register am rechten S-Lauf-/Mehrarmknoten.",
        "Prüfe die freien Knotenarme, ohne einen B5-Wert zu übernehmen.",
        "Lege den bezeichneten örtlichen Tuch- oder Gefäßposten bereit.",
        "Schließe den rechten Mehrarmposten und lösche alle lokalen Registerwerte.",
    ],
}


RECORD_SUMMARIES = {
    "B1": "Führe f81v als gemeinsames zweireihiges Badefeldregister: Plätze zählen und zuweisen, lokale Maße und Zeiten setzen, Tücher oder Gefäße bereitstellen, einzelne Plätze temperieren, spülen oder schließen. Die gemeinsame Umgrenzung erlaubt einen Poolbesitzer, aber keine Reihen- oder Flussfolge.",
    "B2": "Führe f82r als Atlas getrennter Konfigurationen. Bediene zuerst die obere Paarbecken-/Zylinderstation, setze danach die mittlere linke Geräte-/Knotenstation neu, quarantäniere Linie und Liegepodest in F057–F058, eröffne das untere Mehrfigurenfeld erst bei F059 und führe die Randposten ab F062 separat. Jeder Besitzerwechsel sperrt physischen Carry.",
    "B3": "Führe f83r zunächst als drei getrennte Randstationen: offenes Fächerende, Rundgefäß und Korbgefäß. Nach F086 beginnt eine ungelöste Zone F087–F098 ohne Bildkante. Erst F099 eröffnet das tatsächlich bogenverbundene Hauptpaar; beide Seiten bleiben gleichrangig und ungerichtet.",
    "B4": "Eröffne das f83r-Hauptpaar als neuen B4-Record. Buche Paarvergleich und lokale Bedienung, setze bei F120 den linken offenen Fransenposten neu und bei F126 den rechten S-Lauf-/Mehrarmknoten nochmals neu. Sichtbare lokale Anschlüsse erlauben Wartung, aber keinen globalen Kreislauf.",
    "B5": "Führe ausschließlich den linken offenen Fransenposten als eigenen B5-Record, prüfe, reinige und schließe ihn lokal und lösche am Ende ACTIVE, TARGET und PREVIOUS.",
    "B6": "Beginne nach vollständigem Reset einen eigenen B6-Record für den rechten S-Lauf-/Mehrarmknoten. Prüfe, adressiere und schließe nur diesen Posten; kein B5-Wert darf übernommen werden.",
}


GRAPH_ROWS = [
    ("f81v", "B1", "B1_SHARED_POOL_FIGURE_SET", "B1_SHARED_TWO_ROW_POOL", "COMMON_VISIBLE_ENCLOSURE", "UNDIRECTED", "shared green boundary", "LOCAL_OWNER_ONLY"),
    ("f82r", "B2", "B2_UPPER_LEFT_BASIN", "B2_UPPER_CYLINDER", "VISIBLE_LOCAL_CONTACT", "UNDIRECTED", "arch meets cylinder", "WITHIN_COMPOSITE_OWNER"),
    ("f82r", "B2", "B2_UPPER_RIGHT_BASIN", "B2_UPPER_CYLINDER", "VISIBLE_LOCAL_CONTACT", "UNDIRECTED", "arch meets cylinder", "WITHIN_COMPOSITE_OWNER"),
    ("f82r", "B2", "B2_MIDDLE_HAND_DEVICE", "B2_MIDDLE_INLINE_NODE", "VISIBLE_LOCAL_CONTACT", "UNDIRECTED", "waves and double line meet local node", "WITHIN_COMPOSITE_OWNER"),
    ("f82r", "B2", "B2_UPPER_PAIRED_BASINS_AND_CYLINDER", "B2_MIDDLE_LEFT_DEVICE_AND_INLINE_NODE", "NO_VISIBLE_EDGE", "NONE", "owner reset at F053", "BLOCK_PHYSICAL_CARRY"),
    ("f82r", "B2", "B2_MIDDLE_LEFT_DEVICE_AND_INLINE_NODE", "B2_MIDDLE_RIGHT_AMBIGUOUS_STATION", "CONTACT_UNRESOLVED", "NONE", "line lies near but does not securely touch platform", "BLOCK_PHYSICAL_CARRY"),
    ("f82r", "B2", "B2_MIDDLE_RIGHT_AMBIGUOUS_STATION", "B2_LOWER_GREEN_MULTI_FIGURE_POOL", "NO_VISIBLE_EDGE", "NONE", "owner reset inside B2-S012", "BLOCK_PHYSICAL_CARRY"),
    ("f82r", "B2", "B2_LOWER_GREEN_MULTI_FIGURE_POOL", "B2_LOWER_POOL_EDGE_STATIONS", "ADJACENT_FIELD_EDGE_NO_PIPE", "NONE", "edge stations recur at common field but lack conduits", "BLOCK_AUTOMATIC_CARRY"),
    ("f83r", "B3", "B3_UPPER_MARGIN_OPEN_FAN_STATION", "B3_MIDDLE_MARGIN_ROUND_VESSEL_STATION", "NO_VISIBLE_EDGE", "NONE", "owner reset at F075", "BLOCK_PHYSICAL_CARRY"),
    ("f83r", "B3", "B3_MIDDLE_MARGIN_ROUND_VESSEL_STATION", "B3_LOWER_MARGIN_BASKET_VESSEL_STATION", "NO_VISIBLE_EDGE", "NONE", "owner reset at F080", "BLOCK_PHYSICAL_CARRY"),
    ("f83r", "B3", "B3_LOWER_MARGIN_BASKET_VESSEL_STATION", "B3_MARGIN_TO_MAIN_GAP_UNRESOLVED", "NO_VISIBLE_EDGE", "NONE", "break inside B3-S016", "BLOCK_PHYSICAL_CARRY"),
    ("f83r", "B3", "B3_MARGIN_TO_MAIN_GAP_UNRESOLVED", "B3_MAIN_ARCH_LINKED_PAIR", "NO_VISIBLE_EDGE", "NONE", "break inside B3-S026", "BLOCK_PHYSICAL_CARRY"),
    ("f83r", "B3", "B3_MAIN_PAIR_LEFT", "B3_MAIN_PAIR_RIGHT", "VISIBLE_LOCAL_CONTACT", "UNDIRECTED", "broad arch joins both figures", "WITHIN_COMPOSITE_OWNER"),
    ("f83r", "B4", "B4_MAIN_PAIR_LEFT", "B4_MAIN_PAIR_RIGHT", "VISIBLE_LOCAL_CONTACT", "UNDIRECTED", "shared arch", "WITHIN_COMPOSITE_OWNER"),
    ("f83r", "B4", "B4_MAIN_PAIR_LEFT", "B4_MAIN_LEFT_OPEN_FRINGE_STATION", "VISIBLE_LOCAL_ATTACHMENT_BUT_TEXT_OWNER_RESET", "UNDIRECTED", "filled under-run attaches at left vessel; F120 resets text owner", "NO_LEDGER_CARRY_WITHOUT_EXEMPLAR"),
    ("f83r", "B4", "B4_MAIN_PAIR_RIGHT", "B4_MAIN_RIGHT_S_RUN_MULTIPORT_STATION", "VISIBLE_LOCAL_ATTACHMENT_BUT_TEXT_OWNER_RESET", "UNDIRECTED", "S-contour meets right basin/node; F126 resets text owner", "NO_LEDGER_CARRY_WITHOUT_EXEMPLAR"),
    ("f83r", "B4", "B4_MAIN_LEFT_OPEN_FRINGE_STATION", "B4_MAIN_RIGHT_S_RUN_MULTIPORT_STATION", "NO_DIRECT_VISIBLE_EDGE", "NONE", "break inside B4-S015", "BLOCK_DIRECT_CARRY"),
    ("f83r", "B5_TO_B6", "B5_LEFT_OPEN_FRINGE_STATION", "B6_RIGHT_S_RUN_MULTIPORT_STATION", "RECORD_RESET", "NONE", "B5 closes before independent B6 begins", "FORBID_ALL_REGISTER_CARRY"),
]


def statement_event_segments(statement: dict[str, str]) -> dict[int, str]:
    return {int(serial): segment for serial, segment in re.findall(r"E(\d+)\[([^\]]+)\]", statement["literal_owner_card_exemplar_layer"])}


def literal_layer(event: dict[str, str], segment: str) -> str:
    return (
        f"E{event['event_serial']}:[TUPLE:{event['joint_tuple_id']};"
        f"SURFACE_DISPLAY_ONLY:{event['surface_display_only']};FORMULA:{event['formal_formula_opaque']};"
        f"CARD:{event['selected_exact_mnemonic']};PROMPT:{event['strict_formal_prompt']};"
        f"TEMPLATE:{event['event_template']};FROZEN_V72_SEGMENT:{segment};"
        f"TERMINAL:{event['terminal_status']}]"
    )


def measure_kind(serial: int) -> str:
    return ["Arbeitsdauer", "örtliche Füllhöhe", "Chargen- oder Platzmaß"][serial % 3]


def operational_default(event: dict[str, str], owner: str, ordinal_in_owner: int) -> str:
    station = STATIONS[owner]
    gloss = station["gloss"]
    template = event["event_template"]
    serial = int(event["event_serial"])
    if template == "PARAMETER_ASSIGN":
        return f"Trage an der Station „{gloss}“ die exemplarisch vorgegebene {measure_kind(serial)} ein; der Wert gilt nur in {event['record_unit_id']}."
    if template == "LINK_ACTIVE":
        return f"Markiere den aktuellen {event['record_unit_id']}-Arbeitszettel als zur Station „{gloss}“ gehörig; ergänze dadurch keine physische Leitung."
    if template == "TARGET_ASSIGN":
        return f"Setze an der Station „{gloss}“ den im Exemplar bezeichneten lokalen Platz oder Auffangposten als TARGET; keine entfernte Station wird adressiert."
    if template == "TERMINAL_FLUSH":
        return f"Spüle den örtlichen Arbeitsbereich der Station „{gloss}“ einmal und streiche nur diesen Feldposten als abgeschlossen; erzeuge keinen Weiterfluss."
    if template == "TERMINAL_DRAIN":
        return f"Entleere nur den örtlichen Gefäß- oder Tuchposten der Station „{gloss}“ in einen unbebilderten Sammelbehälter und schließe das Feld; bestimme keine Folgestation."
    if template == "ACTION_APPLY":
        return f"Führe am eingetragenen Platz der Station „{gloss}“ genau einen lokalen Bade-, Wasch- oder Gerätegang aus und buche ihn dort ab."
    if template == "ACTION_TEMPER":
        return f"Halte den Arbeitsbereich der Station „{gloss}“ für das eingetragene Intervall handwarm und notiere danach den lokalen Zustand."
    if template == "STATE_GATE":
        return f"Prüfe an der Station „{gloss}“ die im Exemplar bezeichnete Freigabebedingung und öffne erst dann den lokalen Bedienposten."
    if template == "SELECT_PREVIOUS":
        return f"Rufe ausschließlich den unmittelbar vorigen Posten desselben {event['record_unit_id']}-Records auf; übernimm nichts aus einer anderen Bildstation oder einem anderen Record."
    if template == "SELECT_PART":
        return f"Wähle innerhalb der Station „{gloss}“ genau den im Exemplar bezeichneten Figuren-, Gefäß- oder Anschlussteil als lokalen SOURCE-Posten."
    actions = EXEMPLAR_ACTIONS[owner]
    return actions[(ordinal_in_owner - 1) % len(actions)]


def register_effect(event: dict[str, str], owner_status: str) -> str:
    template = event["event_template"]
    effects = {
        "PARAMETER_ASSIGN": "MEASURE:=EXEMPLAR_VALUE",
        "LINK_ACTIVE": "ACTIVE_LEDGER:=LINK(ACTIVE_LEDGER,LOCAL_OWNER);NO_PHYSICAL_EDGE_CREATED",
        "TARGET_ASSIGN": "TARGET:=EXEMPLAR_LOCAL_POST",
        "TERMINAL_FLUSH": "EXECUTE_LOCAL_FLUSH_DEFAULT;CLOSE_FIELD;NO_SUCCESSOR",
        "TERMINAL_DRAIN": "EXECUTE_LOCAL_DRAIN_DEFAULT;CLOSE_FIELD;NO_SUCCESSOR",
        "ACTION_APPLY": "EXECUTE_ONE_LOCAL_SERVICE_DEFAULT",
        "ACTION_TEMPER": "SET_LOCAL_CONDITION_FOR_EXEMPLAR_INTERVAL",
        "STATE_GATE": "IF EXEMPLAR_LOCAL_STATE THEN RELEASE_LOCAL_POST",
        "SELECT_PREVIOUS": "ACTIVE_LEDGER:=PREVIOUS_WITHIN_SAME_RECORD_ONLY",
        "SELECT_PART": "SOURCE:=EXEMPLAR_PART_WITHIN_LOCAL_OWNER",
        "EXEMPLAR_ONLY": "EXECUTE_OCCURRENCE_EXEMPLAR_DEFAULT;NO_CARD_VALUE_INFERRED",
    }
    result = effects[template]
    if owner_status == "UNRESOLVED":
        result += ";QUARANTINE_OWNER;BLOCK_PHYSICAL_CARRY"
    if event["terminal_status"] == "TERMINAL" and template not in {"TERMINAL_FLUSH", "TERMINAL_DRAIN"}:
        result += ";FORMAL_CLOSE_ONLY"
    return result


def source_class(event: dict[str, str]) -> str:
    if event["parse_status"] == "UNPARSED_EXEMPLAR":
        return "OCCURRENCE_EXEMPLAR_ONLY"
    if event["parse_status"] == "UNIQUE_FORMAL_ONLY":
        return "FROZEN_FORMAL_CONTROL_PLUS_CREATIVE_OPERAND"
    if event["parse_status"] == "UNIQUE_CONVERGENT_CHANNELS":
        return "FROZEN_CARD_AND_FORMAL_CONTROL_PLUS_CREATIVE_OPERAND"
    return "FROZEN_EXACT_CARD_MNEMONIC_PLUS_CREATIVE_OPERAND"


def confidence(event: dict[str, str], owner_status: str) -> str:
    base = {"DIRECT_VISIBLE": 0.34, "INHERITED_VISIBLE": 0.29, "PAGE_OWNER_ONLY": 0.27, "UNRESOLVED": 0.11}[owner_status]
    if event["parse_status"] != "UNPARSED_EXEMPLAR":
        base += 0.12
    if event["event_template"] in {"TERMINAL_FLUSH", "TERMINAL_DRAIN"}:
        base += 0.03
    return f"{base:.2f}"


def contact_constraint(owner: str, owner_status: str, incoming: str) -> str:
    pieces = [incoming, "NO_GLOBAL_FLOW_DIRECTION"]
    if owner_status == "UNRESOLVED":
        pieces.extend(["OWNER_UNRESOLVED", "NO_MATERIAL_OR_STATE_CARRY"])
    elif "ARCH_LINKED_PAIR" in owner or "S_RUN" in owner or "DEVICE_AND_INLINE" in owner or "UPPER_PAIRED" in owner:
        pieces.append("VISIBLE_LOCAL_CONTACT_IS_UNDIRECTED")
    else:
        pieces.append("OWNER_CONTEXT_ONLY_NO_PIPE_INFERRED")
    return ";".join(pieces)


def incoming_relations(fields: list[dict[str, str]], owners: dict[str, dict[str, str]]) -> dict[str, str]:
    result: dict[str, str] = {}
    previous_record = ""
    previous_owner = ""
    for field in fields:
        record = field["record_unit_id"]
        owner = owners[field["field_id"]]["selected_visible_owner"]
        if record != previous_record:
            if record == "B6" and previous_record == "B5":
                relation = "HARD_RECORD_RESET_B5_TO_B6;CLEAR_OWNER_ACTIVE_TARGET_PREVIOUS"
            else:
                relation = "RECORD_RESET;CLEAR_OWNER_ACTIVE_TARGET_PREVIOUS"
        elif owner == previous_owner:
            relation = "SAME_LOCAL_OWNER_LEDGER_CONTINUATION"
        else:
            relation = "BREAK_VISIBLE_OWNER;BLOCK_PHYSICAL_CARRY;BOOKKEEPING_ID_MAY_CONTINUE_ONLY"
        result[field["field_id"]] = relation
        previous_record, previous_owner = record, owner
    return result


def field_class(rows: list[dict[str, object]]) -> str:
    templates = {str(row["event_template"]) for row in rows}
    labels = []
    if templates & {"TERMINAL_FLUSH", "TERMINAL_DRAIN"}:
        labels.append("LOCAL_MAINTENANCE_CLOSE")
    if templates & {"ACTION_APPLY", "ACTION_TEMPER", "STATE_GATE"}:
        labels.append("LOCAL_SERVICE_OR_CONDITION")
    if templates & {"PARAMETER_ASSIGN", "TARGET_ASSIGN", "LINK_ACTIVE", "SELECT_PREVIOUS", "SELECT_PART"}:
        labels.append("REGISTER_CONTROL")
    if "EXEMPLAR_ONLY" in templates:
        labels.append("EXEMPLAR_STATION_CONTENT")
    return "+".join(labels)


def build() -> None:
    events = [row for row in read_tsv(EVENT_SOURCE) if 101 <= int(row["event_serial"]) <= 381]
    fields = [row for row in read_tsv(FIELD_SOURCE) if row["record_unit_id"].startswith("B")]
    owner_rows = {
        row["unit_id"]: row for row in read_tsv(OWNER_SOURCE)
        if row["section"] == "BIOLOGICAL" and row["unit_kind"] == "PROSE_FIELD"
    }
    statements = {
        row["statement_id"]: row for row in read_tsv(STATEMENT_SOURCE)
        if row["record_unit_id"].startswith("B")
    }
    image_rows = [row for row in read_tsv(IMAGE_SOURCE) if row["page"] in {"f81v", "f82r", "f83r"}]

    assert len(events) == 281 and len(fields) == 115 and len(statements) == 97 and len(owner_rows) == 115
    assert set(row["selected_visible_owner"] for row in owner_rows.values()) == set(STATIONS)
    assert len(image_rows) == 3

    event_segments: dict[int, str] = {}
    for statement in statements.values():
        event_segments.update(statement_event_segments(statement))
    assert set(event_segments) == set(range(101, 382))

    incoming = incoming_relations(fields, owner_rows)
    ordinal_by_owner: Counter[str] = Counter()
    ordinal_by_field: Counter[str] = Counter()
    event_rows: list[dict[str, object]] = []
    for event in events:
        owner_row = owner_rows[event["field_id"]]
        owner = owner_row["selected_visible_owner"]
        ordinal_by_owner[owner] += 1
        ordinal_by_field[event["field_id"]] += 1
        default = operational_default(event, owner, ordinal_by_owner[owner])
        station = STATIONS[owner]
        row: dict[str, object] = {
            "event_serial": event["event_serial"],
            "page": event["page"],
            "locus": event["locus"],
            "record_unit_id": event["record_unit_id"],
            "field_id": event["field_id"],
            "statement_id": event["statement_id"],
            "event_ordinal_in_field": ordinal_by_field[event["field_id"]],
            "joint_tuple_id": event["joint_tuple_id"],
            "surface_display_only": event["surface_display_only"],
            "formal_formula_opaque": event["formal_formula_opaque"],
            "terminal_status": event["terminal_status"],
            "parse_status": event["parse_status"],
            "selected_exact_mnemonic": event["selected_exact_mnemonic"],
            "strict_formal_prompt": event["strict_formal_prompt"],
            "event_template": event["event_template"],
            "literal_exact_card_formal_exemplar_layer": literal_layer(event, event_segments[int(event["event_serial"])]),
            "local_owner_status": owner_row["owner_status"],
            "local_visible_or_inherited_owner": owner,
            "owner_gloss_not_translation": station["gloss"],
            "incoming_contact_and_reset": incoming[event["field_id"]] if ordinal_by_field[event["field_id"]] == 1 else "WITHIN_FIELD_SAME_OWNER",
            "concrete_german_operational_default": default,
            "operational_register_effect": register_effect(event, owner_row["owner_status"]),
            "source_class": source_class(event),
            "operational_default_confidence": confidence(event, owner_row["owner_status"]),
            "strongest_medical_rival": "MEDICAL_RIVAL: " + station["medical"] + ".",
            "strongest_iconographic_or_formal_rival": "FORMAL_RIVAL: " + station["formal"] + ".",
            "contact_direction_constraint": contact_constraint(owner, owner_row["owner_status"], incoming[event["field_id"]]),
            "hardest_contradiction": owner_row["visible_basis"] + "; " + owner_row["strongest_rival"] + ". Der konkrete Arbeitsgang bleibt ein Exemplarwert und keine Kartenbedeutung.",
            "semantic_ceiling": "CREATIVE_LOCAL_STATION_DEFAULT_NOT_WORD_CARD_STEM_SOUND_LANGUAGE_OR_TRANSLATION",
        }
        event_rows.append(row)

    event_columns = [
        "event_serial", "page", "locus", "record_unit_id", "field_id", "statement_id",
        "event_ordinal_in_field", "joint_tuple_id", "surface_display_only", "formal_formula_opaque",
        "terminal_status", "parse_status", "selected_exact_mnemonic", "strict_formal_prompt",
        "event_template", "literal_exact_card_formal_exemplar_layer", "local_owner_status",
        "local_visible_or_inherited_owner", "owner_gloss_not_translation", "incoming_contact_and_reset",
        "concrete_german_operational_default", "operational_register_effect", "source_class",
        "operational_default_confidence", "strongest_medical_rival",
        "strongest_iconographic_or_formal_rival", "contact_direction_constraint",
        "hardest_contradiction", "semantic_ceiling",
    ]
    event_path = OUT / "V74_R3_281_EVENT_INTERLINEAR.tsv"
    write_tsv(event_path, event_rows, event_columns)

    by_field: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in event_rows:
        by_field[str(row["field_id"])].append(row)
    field_rows: list[dict[str, object]] = []
    for field in fields:
        owner_row = owner_rows[field["field_id"]]
        owner = owner_row["selected_visible_owner"]
        rows = by_field[field["field_id"]]
        field_rows.append({
            "field_id": field["field_id"],
            "record_unit_id": field["record_unit_id"],
            "page": field["page"],
            "locus": field["locus"],
            "statement_id": field["statement_id"],
            "event_count": field["event_count"],
            "event_serials": field["event_serials"],
            "local_owner_status": owner_row["owner_status"],
            "local_visible_or_inherited_owner": owner,
            "owner_gloss_not_translation": STATIONS[owner]["gloss"],
            "incoming_contact_and_reset": incoming[field["field_id"]],
            "field_source_class": field_class(rows),
            "literal_event_sequence": " > ".join(str(row["literal_exact_card_formal_exemplar_layer"]) for row in rows),
            "complete_concrete_operational_field": " ".join(str(row["concrete_german_operational_default"]) for row in rows),
            "register_effect_sequence": " > ".join(str(row["operational_register_effect"]) for row in rows),
            "strongest_medical_rival": "MEDICAL_RIVAL: " + STATIONS[owner]["medical"] + ".",
            "strongest_iconographic_or_formal_rival": "FORMAL_RIVAL: " + STATIONS[owner]["formal"] + ".",
            "contact_direction_constraint": contact_constraint(owner, owner_row["owner_status"], incoming[field["field_id"]]),
            "contradiction": owner_row["visible_basis"] + "; no water, substance, sequence or global direction is established by the field.",
            "semantic_ceiling": "COMPLETE_CREATIVE_FIELD_NOT_DECIPHERMENT_OR_CARD_SEMANTICS",
        })
    field_columns = [
        "field_id", "record_unit_id", "page", "locus", "statement_id", "event_count",
        "event_serials", "local_owner_status", "local_visible_or_inherited_owner",
        "owner_gloss_not_translation", "incoming_contact_and_reset", "field_source_class",
        "literal_event_sequence", "complete_concrete_operational_field", "register_effect_sequence",
        "strongest_medical_rival", "strongest_iconographic_or_formal_rival",
        "contact_direction_constraint", "contradiction", "semantic_ceiling",
    ]
    field_path = OUT / "V74_R3_115_FIELD_EDITION.tsv"
    write_tsv(field_path, field_rows, field_columns)

    by_statement: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in event_rows:
        by_statement[str(row["statement_id"])].append(row)
    statement_rows: list[dict[str, object]] = []
    for statement_id, statement in statements.items():
        rows = by_statement[statement_id]
        owners_in_statement = list(dict.fromkeys(str(row["local_visible_or_inherited_owner"]) for row in rows))
        station_medical = " | ".join(STATIONS[owner]["medical"] for owner in owners_in_statement)
        station_formal = " | ".join(STATIONS[owner]["formal"] for owner in owners_in_statement)
        statement_rows.append({
            "statement_id": statement_id,
            "record_unit_id": statement["record_unit_id"],
            "page": statement["page"],
            "constituent_fields": statement["constituent_fields"],
            "event_count": statement["event_count"],
            "event_serials": statement["event_serials"],
            "owner_bindings": statement["owner_bindings"],
            "owner_transition": statement["owner_transition"],
            "source_class": statement["source_class"],
            "literal_owner_card_exemplar_layer": statement["literal_owner_card_exemplar_layer"],
            "complete_concrete_operational_statement": " ".join(str(row["concrete_german_operational_default"]) for row in rows),
            "frozen_v72_technical_paraphrase": statement["selected_concrete_paraphrase"],
            "strongest_medical_rival": "MEDICAL_RIVAL: " + station_medical + ".",
            "strongest_iconographic_or_formal_rival": "FORMAL_RIVAL: " + station_formal + ".",
            "repair_cost_0_4": statement["repair_cost_0_4"],
            "repair_reason": statement["repair_reason"],
            "line_crossing": statement["line_crossing"],
            "contact_direction_constraint": "BREAK_ENFORCED" if "BREAK_VISIBLE_GAP" in statement["owner_transition"] else "LOCAL_OWNER_ONLY;NO_GLOBAL_DIRECTION",
            "hardest_contradiction": statement["hardest_contradiction"],
            "semantic_ceiling": "COMPLETE_CREATIVE_STATEMENT_NOT_DECIPHERMENT_OR_CARD_SEMANTICS",
        })
    statement_rows.sort(key=lambda row: int(str(row["event_serials"]).split("|")[0]))
    statement_columns = [
        "statement_id", "record_unit_id", "page", "constituent_fields", "event_count",
        "event_serials", "owner_bindings", "owner_transition", "source_class",
        "literal_owner_card_exemplar_layer", "complete_concrete_operational_statement",
        "frozen_v72_technical_paraphrase", "strongest_medical_rival",
        "strongest_iconographic_or_formal_rival", "repair_cost_0_4", "repair_reason",
        "line_crossing", "contact_direction_constraint", "hardest_contradiction", "semantic_ceiling",
    ]
    statement_path = OUT / "V74_R3_97_STATEMENT_EDITION.tsv"
    write_tsv(statement_path, statement_rows, statement_columns)

    by_record_events: dict[str, list[dict[str, object]]] = defaultdict(list)
    by_record_fields: dict[str, list[dict[str, object]]] = defaultdict(list)
    by_record_statements: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in event_rows:
        by_record_events[str(row["record_unit_id"])].append(row)
    for row in field_rows:
        by_record_fields[str(row["record_unit_id"])].append(row)
    for row in statement_rows:
        by_record_statements[str(row["record_unit_id"])].append(row)
    record_rows: list[dict[str, object]] = []
    for record in ["B1", "B2", "B3", "B4", "B5", "B6"]:
        record_events = by_record_events[record]
        record_fields = by_record_fields[record]
        record_statements = by_record_statements[record]
        owner_sequence = list(dict.fromkeys(str(row["local_visible_or_inherited_owner"]) for row in record_fields))
        record_rows.append({
            "record_unit_id": record,
            "page": record_events[0]["page"],
            "event_count": len(record_events),
            "field_count": len(record_fields),
            "statement_count": len(record_statements),
            "owner_sequence": " > ".join(owner_sequence),
            "record_reset_rule": "BEGIN_CLEAR_OWNER_ACTIVE_TARGET_PREVIOUS;END_CLEAR_OWNER_ACTIVE_TARGET_PREVIOUS" + (";NO_B5_TO_B6_CARRY" if record in {"B5", "B6"} else ""),
            "readable_operational_record": RECORD_SUMMARIES[record],
            "complete_event_trace": " ".join(str(row["concrete_german_operational_default"]) for row in record_events),
            "medical_competitor": " | ".join(dict.fromkeys(STATIONS[owner]["medical"] for owner in owner_sequence)),
            "formal_iconographic_competitor": " | ".join(dict.fromkeys(STATIONS[owner]["formal"] for owner in owner_sequence)),
            "hardest_contradiction": "No visible arrow, common reservoir, global source, sink or return route binds this record; all physical operations are occurrence-level defaults.",
            "semantic_ceiling": "EXECUTABLE_LOCAL_RECORD_NOT_TRANSLATION_OR_GLOBAL_FLOW_MODEL",
        })
    record_columns = [
        "record_unit_id", "page", "event_count", "field_count", "statement_count",
        "owner_sequence", "record_reset_rule", "readable_operational_record",
        "complete_event_trace", "medical_competitor", "formal_iconographic_competitor",
        "hardest_contradiction", "semantic_ceiling",
    ]
    record_path = OUT / "V74_R3_SIX_RECORD_EDITION.tsv"
    write_tsv(record_path, record_rows, record_columns)

    station_rows: list[dict[str, object]] = []
    for owner, data in STATIONS.items():
        field_ids = [field_id for field_id, row in owner_rows.items() if row["selected_visible_owner"] == owner]
        station_rows.append({
            "station_owner": owner,
            "page": owner_rows[field_ids[0]]["page"],
            "records": "|".join(sorted({owner_rows[field_id]["record_or_diagram"] for field_id in field_ids})),
            "field_count": len(field_ids),
            "owner_statuses": "|".join(sorted({owner_rows[field_id]["owner_status"] for field_id in field_ids})),
            "technical_operational_reading": data["operation"],
            "medical_reading": data["medical"],
            "iconographic_or_formal_reading": data["formal"],
            "actual_visible_contact": data["contact"],
            "required_disconnection_or_reset": data["break"],
            "r3_local_lead": data["lead"],
            "confidence": "LOW" if "UNRESOLVED" in owner else "MEDIUM",
            "semantic_ceiling": "STATION_COMPARISON_NOT_DOMAIN_OR_MEANING_ASSIGNMENT",
        })
    station_path = OUT / "V74_R3_STATION_COMPARISON.tsv"
    write_tsv(station_path, station_rows, [
        "station_owner", "page", "records", "field_count", "owner_statuses",
        "technical_operational_reading", "medical_reading", "iconographic_or_formal_reading",
        "actual_visible_contact", "required_disconnection_or_reset", "r3_local_lead",
        "confidence", "semantic_ceiling",
    ])

    graph_rows: list[dict[str, object]] = []
    for index, (page, record, left, right, status, direction, evidence, carry) in enumerate(GRAPH_ROWS, 1):
        graph_rows.append({
            "graph_edge_id": f"V74R3G{index:03d}",
            "page": page,
            "record_scope": record,
            "endpoint_a": left,
            "endpoint_b": right,
            "edge_status": status,
            "directedness": direction,
            "visible_basis_or_reset": evidence,
            "permitted_register_or_material_carry": carry,
            "prohibited_inference": "NO_GLOBAL_FLOW;NO_SOURCE_SINK;NO_RETURN_DIRECTION;NO_CROSS_RECORD_INHERITANCE",
        })
    graph_path = OUT / "V74_R3_LOCAL_PROCESS_GRAPHS.tsv"
    write_tsv(graph_path, graph_rows, [
        "graph_edge_id", "page", "record_scope", "endpoint_a", "endpoint_b",
        "edge_status", "directedness", "visible_basis_or_reset",
        "permitted_register_or_material_carry", "prohibited_inference",
    ])

    report_path = OUT / "V74_R3_TECHNICAL_REPORT.md"
    lines = [
        "# V74 R3 — Biological station-atlas third edition",
        "",
        "Status: kreative technische Zehnseiten-Arbeitsedition, keine Entzifferung oder Übersetzung.",
        "",
        "## Ergebnis",
        "",
        "Alle **281 Ereignisse**, **115 Felder**, **97 Aussagen** und **6 Records** auf f81v/f82r/f83r besitzen jetzt eine konkrete lokale Betriebslesung. "
        "Die Edition behandelt die Bilder als Atlas von Bad-, Wasch-, Geräte-, Gefäß-, Kontroll- und Abschlussstationen. Sie erzeugt ausdrücklich keinen Gesamtwasserkreislauf.",
        "",
        "Von 281 Ereignissen bleiben 191 reine Exemplarwerte; 90 besitzen mindestens eine eingefrorene exakte Karten- oder Formalklasse. "
        "Auch dort sind Wasser, Tuch, Temperatur, Platz, Gefäß und Arbeitshandlung nur konkrete Quellenfüllungen, keine Bedeutungen der sichtbaren Gruppen.",
        "",
        "## Ausführbare Registerregel",
        "",
        "```text",
        "BEGIN B-record: clear OWNER, ACTIVE, TARGET, PREVIOUS, MEASURE",
        "SET smallest V71 owner for the current field",
        "IF owner changes: block physical carry; retain record ID only as bookkeeping",
        "IF owner unresolved: quarantine ACTIVE and TARGET until the exemplar resolves it",
        "EXECUTE exact event in V69 order with its opaque card/formal layer",
        "APPLY concrete occurrence default only at the local owner",
        "VISIBLE contact permits local comparison, never source/sink/direction",
        "CLOSE closes a field; FLUSH?/DRAIN? close only their local post",
        "END B-record: clear every register",
        "B5 -> B6: mandatory hard reset, no inherited value",
        "```",
        "",
        "Sichtbarer Kontakt und Registervererbung sind getrennte Größen. Der B4-Unterlauf kann sichtbar am Gefäß ansetzen, während der Text beim Besitzerwechsel trotzdem einen neuen lokalen Posten eröffnet. Umgekehrt erzeugt `LINK_ACTIVE` niemals eine gezeichnete Leitung.",
        "",
        "## Die sechs Records",
        "",
    ]
    for row in record_rows:
        lines.extend([
            f"### {row['record_unit_id']} — {row['page']}",
            "",
            str(row["readable_operational_record"]),
            "",
            f"Umfang: {row['event_count']} Ereignisse, {row['field_count']} Felder, {row['statement_count']} Aussagen.",
            "",
        ])
    lines.extend([
        "## Kontaktgraph und harte Sperren",
        "",
        "Der maschinenlesbare Graph enthält ausschließlich `UNDIRECTED` oder `NONE`. Positive lokale Kontakte sind die obere f82r-Paar-/Zylinderkonfiguration, der f82r-Geräte-/Inline-Knoten, die Hauptbogenpaare sowie die lokalen f83r-Unterläufe. "
        "Echte Sperren liegen zwischen den f82r-Konfigurationen, zwischen den drei f83r-Randstationen, über F087–F098, zwischen linkem und rechtem Unterlauf sowie zwingend zwischen B5 und B6.",
        "",
        "Vier V72-Aussagen behalten einen internen Besitzerbruch: `B2-S012`, `B3-S016`, `B3-S026` und `B4-S015`. F057–F058 sowie F087–F098 bleiben unaufgelöst; ihre konkreten Defaults sind Quarantänehandlungen im Register und kein imaginärer Stofftransport.",
        "",
        "## Stationsvergleich",
        "",
        "Für jede der 16 lokalen Besitzerklassen stehen technische, medizinische und formal-ikonographische Gegenlesung nebeneinander. f81v und das untere f82r-Feld tragen Bad-/Poollesungen am stärksten. Geräte-, Gefäß- und Unterlaufstationen tragen eine technische Bedienlesung. Offene Fächer, Bögen und Knoten behalten jedoch starke ikonographische Rivalen; die zwei ungelösten Besitzer werden formal quarantänisiert.",
        "",
        "## Gewinn und Grenze",
        "",
        "Die Edition ist ausführbar, weil ein Schreiber nur Record, lokalen Besitzer, Exemplarwert und Abschlussstatus verfolgen muss. Sie ist zugleich streng lokal: kein Pfeil, gemeinsamer Vorrat, Quelle, Senke oder Rücklauf wird ergänzt. "
        "Der Preis ist hoch: 191/281 konkrete Vorgänge kommen vollständig aus dem angenommenen Masterexemplar, und selbst die 90 typisierten Vorgänge bestimmen keinen Gegenstand oder Zweck.",
        "",
        "Keine neue Karte, kein Stamm, Laut, Wort, POS, Sprache oder Klartext wurde eingeführt. f84 und f84r blieben versiegelt.",
        "",
    ])
    report_path.write_text("\n".join(lines), encoding="utf-8")

    source_paths = [EVENT_SOURCE, FIELD_SOURCE, OWNER_SOURCE, STATEMENT_SOURCE, IMAGE_SOURCE, CONTINUITY_SOURCE]
    output_paths = [event_path, field_path, statement_path, record_path, station_path, graph_path, report_path]
    summary = {
        "experiment": "V74_R3_BIOLOGICAL_STATION_ATLAS_THIRD_EDITION",
        "status": "CREATIVE_EXECUTABLE_LOCAL_STATION_READING_NOT_DECIPHERMENT",
        "counts": {
            "events": len(event_rows),
            "fields": len(field_rows),
            "statements": len(statement_rows),
            "records": len(record_rows),
            "station_owners": len(station_rows),
            "graph_edges": len(graph_rows),
            "recognized_or_formal_events": sum(row["parse_status"] != "UNPARSED_EXEMPLAR" for row in events),
            "exemplar_only_events": sum(row["parse_status"] == "UNPARSED_EXEMPLAR" for row in events),
            "unresolved_fields": sum(row["owner_status"] == "UNRESOLVED" for row in owner_rows.values()),
        },
        "pages": sorted({str(row["page"]) for row in event_rows}),
        "source_hashes": {str(path.relative_to(ROOT)): sha256(path) for path in source_paths},
        "output_hashes": {path.name: sha256(path) for path in output_paths},
        "global_direction": "NOT_INFERRED",
        "sealed": ["f84", "f84r"],
        "semantic_ceiling": "NO_CARD_STEM_SOUND_LANGUAGE_MEANING_OR_TRANSLATION_PROMOTION",
    }
    (OUT / "V74_R3_BUILD_SUMMARY.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


if __name__ == "__main__":
    build()
