#!/usr/bin/env python3
"""Build V73 R3's complete nonmedical Herbal third edition.

This is an explicitly creative ten-page workshop edition.  It preserves the
frozen V69 event identities, the V71 whole-plant owners, and the selected V72
statement structure.  Concrete plant-work instructions are occurrence-level
exemplar fills; they are not translations or new card values.
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
V71 = ROOT / "experiments/yolo/sidequest_theory_candidates_v71"
V72 = ROOT / "experiments/yolo/sidequest_theory_candidates_v72"

EVENT_SOURCE = V69 / "V69_R4_FINAL_381_PROSE_EVENT_INTERLINEAR.tsv"
FIELD_SOURCE = V69 / "V69_R4_FINAL_135_FIELD_EDITION.tsv"
OWNER_SOURCE = V71 / "V71_SELECTED_OWNER_LEDGER.tsv"
STATEMENT_SOURCE = V72 / "V72_SELECTED_116_STATEMENTS.tsv"


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


OWNERS = {
    "H1": "WHOLE_BROAD_TOOTHED_RADIAL_FLOWERED_HERB",
    "H2": "WHOLE_BROAD_TOOTHED_RADIAL_FLOWERED_HERB",
    "H3": "WHOLE_DENSE_BLUE_FLOWERED_CROWN_PLANT",
    "H4": "WHOLE_BROAD_LEAF_PANICLED_PLANT_WITH_MNEMONIC_ROOT",
    "H5": "WHOLE_MULTIHEAD_SPINY_OR_EMBLEMATIC_HERB",
}

OWNER_GLOSSES = {
    "H1": "ganze abgebildete f10r-Pflanze, erster Artikel",
    "H2": "ganze abgebildete f10r-Pflanze, zweiter selbständiger Arbeitsrecord",
    "H3": "ganze abgebildete f11r-Pflanze",
    "H4": "ganze abgebildete f55v-Pflanze; die groteske Wurzel bleibt bloß Bildmerkmal",
    "H5": "ganze abgebildete f56r-Pflanze mit mehreren Köpfen",
}

# One concrete, occurrence-specific workshop instruction per frozen event.
# The list lengths are deliberately identical to the frozen field event counts.
FIELD_PROGRAMS: dict[str, list[str]] = {
    "F001": [
        "Eröffne einen frischen Arbeitslos-Posten für die ganze Bildpflanze.",
        "Wähle daraus eine kleine unterirdische Probe.",
        "Bürste anhaftende Erde von dieser Probe ab.",
        "Spüle nur die gewählte Probe einmal mit sauberem Wasser.",
        "Schneide die gespülte Probe in gleichmäßig kleine Stücke.",
        "Lege die Stücke in ein bedeckbares Ziehgefäß.",
        "Gib so viel sauberes Wasser zu, dass die Stücke eben bedeckt sind.",
        "Prüfe einen kleinen Löffel des ersten Auszugs als Arbeitsprobe.",
        "Trage für den nassen Ansatz ein örtliches Maß ein.",
        "Breite den unbenutzten Pflanzenrest getrennt zum Trocknen aus.",
    ],
    "F002": [
        "Fülle einen zweiten kleinen Posten des Auszugs in ein Arbeitsgefäß.",
        "Erwärme diesen Posten sanft, ohne ihn zum Sieden zu bringen.",
        "Verknüpfe ihn recordlokal mit dem noch aktiven nassen H1-Ansatz.",
        "Gib ihn zum Abgießen frei, sobald sich der örtliche Bereitschaftszustand zeigt.",
    ],
    "F003": [
        "Eröffne aus derselben Bildpflanze ein neues, vom H1-Record getrenntes Los.",
        "Prüfe, ob das gewählte oberirdische Material frisch und unbeschädigt ist.",
        "Setze dieses Material als neuen aktiven Arbeitsansatz ein.",
        "Nimm davon eine gleichmäßige Handprobe.",
        "Quetsche die Handprobe in einem Mörser an.",
        "Presse das gequetschte Material durch ein sauberes Tuch.",
        "Fange die ausgedrückte Flüssigkeit in einem eigenen Gefäß auf.",
        "Trage für die Pressfraktion ein örtliches Maß ein.",
        "Lege den Presskuchen als getrennten Vergleichsposten zurück.",
    ],
    "F004": [
        "Öffne den Presskuchen als ersten Vergleichsposten wieder.",
        "Setze daraus eine erste Waschcharge an.",
        "Gib eine abgemessene Menge Wasser zur Waschcharge.",
        "Verknüpfe die Waschcharge mit dem aktiven H2-Los.",
        "Stelle die vorherige Pressflüssigkeit daneben, ohne auf H1 zurückzugreifen.",
        "Buche beide Fraktionen unter demselben recordlokalen Vergleich.",
        "Gib beiden Fraktionen das gleiche Prüfmaß.",
        "Notiere, welche der beiden Fraktionen nach dem Stehen klarer bleibt.",
    ],
    "F005": [
        "Seihe die erste Waschcharge durch ein frisches Tuch.",
        "Setze die geseihte Flüssigkeit als zweite Charge des H2-Loses an.",
        "Setze ihren Bodensatz als getrennten Arbeitsansatz an.",
        "Spüle diesen Bodensatz genau einmal nach.",
        "Lasse beide Flüssigkeiten stehen, bis sich Feststoff absetzt.",
        "Gieße die obere Flüssigkeit vorsichtig vom Satz ab.",
        "Trockne und lagere den verbleibenden Pressstoff als Referenzrest.",
    ],
    "F006": [
        "Eröffne ein frühlingszeitlich genommenes Los der ganzen f11r-Bildpflanze.",
        "Wähle daraus eine kleine unterirdische Probe.",
        "Zerkleinere die Probe unmittelbar nach der Entnahme.",
        "Zerdrücke sie und presse sie durch ein grobes Tuch.",
        "Führe die Flüssigkeit ein zweites Mal durch ein frisches feines Tuch.",
        "Nimm die Flüssigkeit an, sobald sie den örtlichen Klarheitszustand erreicht.",
        "Schließe den Posten und lasse das bedeckte Gefäß abkühlen.",
    ],
    "F007": [
        "Behalte eine trockene Kopf- oder Blütenprobe als getrennte Referenz zurück.",
    ],
    "F008": [
        "Nimm einen Arbeitsanteil der geklärten Flüssigkeit.",
        "Tränke damit einen sauberen Tuchstreifen.",
        "Lege den nassen Streifen auf eine neutrale Prüfunterlage.",
        "Lege einen zweiten trockenen Streifen als Vergleich daneben.",
        "Gib beiden Prüfposten dasselbe örtliche Flüssigkeitsmaß beziehungsweise Nullmaß.",
    ],
    "F009": [
        "Lege eine Blattprobe in ein nicht abgebildetes warmes Wasserbad.",
        "Zerstoße die erweichte Probe zu einer gleichmäßigen Masse.",
        "Nimm die Masse in den Arbeitsvergleich, sobald sie gebrauchsfertig ist.",
        "Notiere ihre Beschaffenheit und schließe den lokalen Vergleich.",
    ],
    "F010": [
        "Eröffne für die ganze f55v-Bildpflanze einen neuen Standardslot.",
        "Trage ein örtliches Maß des gewählten Blattmaterials ein.",
        "Schneide die Blattprobe in schmale Streifen.",
        "Bedecke die Streifen in einem nicht abgebildeten Gefäß mit Wasser.",
        "Schließe das Gefäß und lasse den Posten bis zur örtlichen Endmarke ziehen.",
    ],
    "F011": [
        "Teile die gezogene Flüssigkeit in zwei gleiche Messposten.",
        "Rühre den ersten Posten, bis er gleichmäßig erscheint.",
        "Schließe diesen Einzelposten nach einem Durchgang durch das Prüftuch.",
    ],
    "F012": [
        "Bereite für den zweiten Posten ein eigenes Gefäß vor.",
        "Halte dieses Gefäß bei mäßiger Wärme.",
        "Gib einen frischen, nicht abgebildeten Wasseranteil zu.",
        "Schließe den zweiten Posten nach demselben Arbeitsintervall.",
    ],
    "F013": [
        "Messe von beiden f55v-Fraktionen den gleichen Anteil ab.",
        "Setze für die zweite Fraktion einen lokalen Vergleichsslot.",
        "Vereinige je eine gleich große Probe beider Fraktionen.",
        "Führe die vereinigte Probe als aktiven H4-Ansatz weiter.",
        "Übertrage den Rest in ein bedecktes Vorratsgefäß.",
        "Verbrauche die frische Vergleichsprobe bei einer Materialwäsche, bevor sie verdirbt.",
    ],
    "F014": [
        "Eröffne ein zur örtlich passenden Jahreszeit genommenes Los der ganzen f56r-Bildpflanze.",
        "Wähle daraus eine unterirdische Probe.",
        "Schneide und quetsche die Probe an.",
        "Trage für die angequetschte Probe ein örtliches Maß ein.",
    ],
    "F015": [
        "Gib als unbebildertes Medium sauberes Wasser zur Probe.",
        "Lasse die Probe kalt ziehen.",
        "Übertrage die gefilterte Flüssigkeit in einen Arbeitsbecher.",
        "Prüfe einen kleinen Anteil davon auf einem neutralen Probetuch.",
        "Weise den geprüften Anteil dem bezeichneten recordlokalen Musterposten zu.",
    ],
    "F016": [
        "Nimm ein zweites Vergleichslos von einem feuchteren oder schattigeren Standort.",
        "Lege dieses Los in ein eigenes Arbeitsgefäß.",
        "Prüfe davon denselben Anteil wie beim ersten Los.",
        "Schließe den Posten, indem du seinen Rückstand offen an der Luft trocknest.",
    ],
    "F017": [
        "Wähle einen reifen Kopf der ganzen Bildpflanze als Muster.",
        "Trenne diesen Kopf vom übrigen Vorratsmaterial.",
        "Löse das darin enthaltene feine Material auf ein Tuch aus.",
        "Trockne das ausgelöste Material im Schatten.",
    ],
    "F018": [
        "Öffne den frischen H5-Arbeitsansatz erneut.",
        "Lege daneben eine trockene Kontrollprobe zurück.",
        "Kennzeichne beide Proben unter demselben Ganzpflanzenartikel.",
    ],
    "F019": [
        "Nimm den nächsten bezeichneten Pflanzenposten.",
        "Befeuchte ihn mit einem nicht abgebildeten Wasser- oder Bindemittelanteil.",
        "Vermenge ihn zu einer gleichmäßigen frischen Masse.",
        "Verwende die Masse sofort als Material- oder Haftprobe.",
    ],
    "F020": [
        "Wähle den im Master bezeichneten Kopf- oder Blütenteil.",
        "Sondere daraus das helle beziehungsweise geöffnete Material aus.",
        "Trage für diesen Endposten ein örtliches Maß ein.",
    ],
}

FIELD_TEXT = {
    "F001": "Eröffne das erste f10r-Los, wähle eine unterirdische Probe, säubere, spüle und zerkleinere sie, bedecke sie im Ziehgefäß mit Wasser, prüfe einen kleinen Auszug, bemesse den nassen Ansatz und trockne den Rest.",
    "F002": "Erwärme einen zweiten Auszugsposten sanft, verknüpfe ihn nur innerhalb H1 mit dem aktiven Ansatz und gieße ihn nach dem örtlichen Bereitschaftszeichen ab.",
    "F003": "Eröffne H2 unabhängig von H1, wähle frisches oberirdisches Material, setze es als Charge an, quetsche und presse es, fange die Flüssigkeit ab, bemesse sie und behalte den Presskuchen.",
    "F004": "Wasche den Presskuchen mit abgemessenem Wasser, stelle die vorige H2-Pressflüssigkeit daneben, buche beide Fraktionen unter demselben Vergleich, gib ihnen gleiche Prüfmaße und notiere die klarere Fraktion.",
    "F005": "Seihe die Waschcharge, führe Flüssigkeit und Satz als getrennte H2-Posten, spüle den Satz einmal, lasse beide stehen, gieße ab und trockne den Referenzrest.",
    "F006": "Zerkleinere und presse eine unterirdische Probe der f11r-Pflanze, seihe zweimal, nimm die Flüssigkeit am örtlichen Klarheitszeichen an und lasse sie bedeckt abkühlen.",
    "F007": "Bewahre eine trockene Kopf- oder Blütenprobe der f11r-Pflanze als Referenz auf.",
    "F008": "Tränke ein Probetuch mit einem gemessenen Anteil der geklärten Flüssigkeit und vergleiche es mit einem trockenen Tuch auf neutraler Unterlage.",
    "F009": "Erweiche eine Blattprobe im warmen Wasserbad, zerstoße sie, nimm sie am Bereitschaftszeichen in den Vergleich und notiere ihre Beschaffenheit.",
    "F010": "Eröffne einen f55v-Standardslot, bemesse und schneide Blattmaterial, bedecke es mit Wasser und lasse es im geschlossenen Gefäß bis zur Endmarke ziehen.",
    "F011": "Teile die Flüssigkeit in gleiche Messposten, rühre den ersten gleichmäßig und führe ihn einmal durch das Prüftuch.",
    "F012": "Bereite den zweiten Messposten in eigenem Gefäß mit frischem Wasser bei mäßiger Wärme und gleicher Arbeitsdauer.",
    "F013": "Bemesse beide Fraktionen gleich, setze einen Vergleichsslot, vereinige Teilproben, führe sie als H4-Ansatz, lagere den Rest bedeckt und verbrauche die frische Probe zeitnah.",
    "F014": "Eröffne ein saisonales f56r-Los, wähle eine unterirdische Probe, schneide und quetsche sie und trage ihr Maß ein.",
    "F015": "Ziehe die Probe kalt in Wasser, filtere sie, prüfe eine kleine Menge auf neutralem Tuch und weise sie dem recordlokalen Musterposten zu.",
    "F016": "Nimm ein Standort-Vergleichslos, halte es in eigenem Gefäß, prüfe denselben Anteil und trockne den Rückstand offen.",
    "F017": "Trenne einen reifen Kopf als Muster, löse feines Material auf ein Tuch aus und trockne es im Schatten.",
    "F018": "Stelle dem frischen H5-Ansatz eine trockene Kontrollprobe gegenüber und kennzeichne beide unter demselben Ganzpflanzenartikel.",
    "F019": "Befeuchte den nächsten Pflanzenposten mit einem unbebilderten Medium, vermenge ihn gleichmäßig und verwende ihn sofort als Material- oder Haftprobe.",
    "F020": "Wähle den bezeichneten Kopf- oder Blütenteil, sondere helles beziehungsweise geöffnetes Material aus und bemesse den Endposten.",
}

FIELD_STAGE = {
    "F001": "SAMPLING_WET_EXTRACTION_STORAGE",
    "F002": "GENTLE_HEAT_SETTLE_DECANT",
    "F003": "FRESH_SAMPLE_PRESS_EXTRACTION",
    "F004": "MATCHED_FRACTION_COMPARISON",
    "F005": "SECOND_WASH_SETTLE_STORAGE",
    "F006": "DOUBLE_FILTRATION_CLARIFICATION",
    "F007": "DRY_REFERENCE_STORAGE",
    "F008": "WET_DRY_MATERIAL_COMPARISON",
    "F009": "WARM_SOFTENING_TEXTURE_TEST",
    "F010": "MEASURED_WATER_STEEP",
    "F011": "FIRST_FRACTION_FILTER_TEST",
    "F012": "SECOND_FRACTION_WARM_CONTROL",
    "F013": "FRACTION_COMBINATION_AND_STORAGE",
    "F014": "SEASONAL_SAMPLE_MEASURE",
    "F015": "COLD_WATER_EXTRACTION_TEST",
    "F016": "SITE_LOT_COMPARISON",
    "F017": "HEAD_SAMPLE_DRY_STORAGE",
    "F018": "FRESH_VERSUS_DRY_CONTROL",
    "F019": "WET_BINDING_MATERIAL_TEST",
    "F020": "DESIGNATED_PART_END_MEASURE",
}

ARTICLE_TEXTS = {
    "H1": (
        "Erster Arbeitsartikel zur ganzen f10r-Pflanze. Eröffne ein frisches Los und nimm eine kleine "
        "unterirdische Probe. Bürste sie ab, spüle sie einmal, schneide sie klein und bedecke sie in einem "
        "Ziehgefäß mit sauberem Wasser. Prüfe einen kleinen Löffel des ersten Auszugs und trage das örtliche "
        "Maß ein; breite den unbenutzten Rest getrennt zum Trocknen aus. Fülle einen zweiten Auszugsposten ab, "
        "erwärme ihn sanft ohne Sieden, verknüpfe ihn nur innerhalb dieses Records mit dem aktiven nassen Ansatz "
        "und gieße ihn ab, sobald sich der örtliche Bereitschaftszustand zeigt."
    ),
    "H2": (
        "Zweiter, selbständiger Arbeitsartikel zur selben f10r-Bildpflanze. Beginne ein neues Los und wähle "
        "frisches oberirdisches Material. Quetsche und presse eine Handprobe, fange die Flüssigkeit getrennt auf, "
        "bemesse sie und behalte den Presskuchen. Wasche den Kuchen mit einer gleichen Wassermenge und stelle die "
        "vorige H2-Pressflüssigkeit daneben; beide gehören nur zum recordlokalen Vergleich, nicht zum alten H1-Los. "
        "Gib beiden gleiche Prüfmaße und notiere nach dem Stehen die klarere Fraktion. Seihe die Waschcharge, führe "
        "Flüssigkeit und Satz getrennt, spüle den Satz einmal nach, gieße die obere Flüssigkeit ab und trockne den "
        "verbleibenden Stoff als Referenz."
    ),
    "H3": (
        "Arbeitsartikel zur ganzen f11r-Pflanze. Nimm eine kleine unterirdische Probe, zerkleinere und presse sie "
        "durch ein grobes Tuch und seihe die Flüssigkeit danach durch ein feines. Nimm sie am örtlichen "
        "Klarheitszeichen an und lasse sie bedeckt abkühlen; bewahre außerdem eine trockene Kopf- oder Blütenprobe "
        "als Referenz auf. Tränke einen sauberen Tuchstreifen mit einem gemessenen Flüssigkeitsanteil und vergleiche "
        "ihn auf neutraler Unterlage mit einem trockenen Streifen. Erweiche schließlich eine Blattprobe im warmen "
        "Wasserbad, zerstoße sie, nimm sie am Bereitschaftszeichen in den Vergleich und notiere ihre Beschaffenheit."
    ),
    "H4": (
        "Arbeitsartikel zur ganzen f55v-Pflanze. Eröffne einen Standardslot, bemesse eine Blattprobe, schneide sie "
        "in Streifen und lasse sie bedeckt in Wasser ziehen. Teile die Flüssigkeit gleich; rühre und filtere die "
        "erste Fraktion, während die zweite in eigenem Gefäß mit frischem Wasser bei mäßiger Wärme dieselbe Zeit "
        "steht. Bemesse beide Fraktionen erneut, setze einen lokalen Vergleichsslot und vereinige gleich große "
        "Teilproben. Führe diese Mischung als aktiven H4-Ansatz, lagere den Rest bedeckt und verbrauche die frische "
        "Probe zeitnah für eine Materialwäsche. Die groteske Wurzelform liefert dabei keinen eigenen Arbeitsposten."
    ),
    "H5": (
        "Arbeitsartikel zur ganzen f56r-Pflanze. Eröffne ein saisonales Los, schneide und quetsche eine kleine "
        "unterirdische Probe, bemesse sie und lasse sie kalt in sauberem Wasser ziehen. Filtere den Auszug, prüfe "
        "eine gleiche Kleinmenge auf neutralem Tuch und weise sie einem recordlokalen Musterposten zu. Nimm ein "
        "zweites Los von einem feuchteren oder schattigeren Standort, prüfe denselben Anteil und trockne seinen "
        "Rückstand offen. Trenne außerdem einen reifen Kopf als Trockenmuster, löse feines Material auf ein Tuch aus "
        "und lagere es im Schatten. Stelle dem frischen Ansatz eine trockene Kontrollprobe gegenüber. Befeuchte "
        "einen weiteren bezeichneten Posten, vermenge ihn zur frischen Materialprobe und gebrauche ihn sofort; "
        "schließe mit dem abgemessenen hellen oder geöffneten Kopfteil."
    ),
}

ARTICLE_TITLES = {
    "H1": "Erste Nassprobe und Trockenreserve der f10r-Ganzpflanze",
    "H2": "Press-, Wasch- und Fraktionsvergleich der f10r-Ganzpflanze",
    "H3": "Klär-, Tuch- und Warmprobe der f11r-Ganzpflanze",
    "H4": "Parallele Wasserfraktionen der f55v-Ganzpflanze",
    "H5": "Standort-, Nass- und Trockenvergleich der f56r-Ganzpflanze",
}

ARTICLE_RIVALS = {
    "H1": "Heilkundlicher Wurzel-Auszug mit Dosis und therapeutischem Gebrauch.",
    "H2": "Heilkundliche Presssaftbereitung aus oberirdischen Pflanzenteilen.",
    "H3": "Heilkundlicher geklärter Auszug plus äußerliche Auflage.",
    "H4": "Heilkundliche Blattabkochung oder Waschung.",
    "H5": "Heilkundliche saisonale Sammlung, Auflage und Dosis.",
}

ARTICLE_CONTRADICTIONS = {
    "H1": "Nur die ganze Pflanze ist sichtbar; Wurzelwahl, Wasser, Gefäß, Maß und Arbeitszweck sind unbebilderte Exemplarfüllungen.",
    "H2": "Die zweite Recordgrenze ist formal, aber Pressen, Fraktionen, Vergleich und Klarheitsbeobachtung sind weder Bild- noch Kartenwerte.",
    "H3": "Tücher, Wasserbad, Prüfunterlage und jahreszeitliche Entnahme sind nicht gezeichnet; selbst KLAR? bleibt nur Fragezeichen-Mnemonic.",
    "H4": "Die Texttaschen beweisen keine Pflanzenpartien; Wassergefäße und parallele Fraktionen sind vollständig unbebildert.",
    "H5": "Mehrere Köpfe beweisen weder Reifestufen noch Samen; Standort, Wasser, Kontrollprobe und Bindemittel sind kreative Quellenargumente.",
}


def event_literal(event: dict[str, str], selected_segment: str) -> str:
    card = event["selected_exact_mnemonic"]
    prompt = event["strict_formal_prompt"]
    return (
        f"E{event['event_serial']}:[TUPLE:{event['joint_tuple_id']};"
        f"SURFACE_DISPLAY_ONLY:{event['surface_display_only']};"
        f"FORMULA:{event['formal_formula_opaque']};"
        f"CARD:{card};PROMPT:{prompt};TEMPLATE:{event['event_template']};"
        f"FROZEN_V72_SEGMENT:{selected_segment};TERMINAL:{event['terminal_status']}]"
    )


def register_effect(event: dict[str, str]) -> str:
    template = event["event_template"]
    effects = {
        "ACTION_APPLY": "EXECUTE_EXEMPLAR_USE(ACTIVE,LOCAL_SAMPLE_OR_TARGET)",
        "PARAMETER_ASSIGN": "MEASURE:=EXEMPLAR_VALUE",
        "LINK_ACTIVE": "PREVIOUS:=ACTIVE;ACTIVE:=EXEMPLAR_OR_LINKED_LOCAL_BATCH",
        "STATE_GATE": "IF EXEMPLAR_STATE_REACHED THEN RELEASE(ACTIVE)",
        "TARGET_ASSIGN": "TARGET:=EXEMPLAR_LOCAL_POST",
        "SELECT_PREVIOUS": "ACTIVE:=PREVIOUS_WITHIN_CURRENT_RECORD",
        "SELECT_PART": "SOURCE:=EXEMPLAR_PART_OF(WHOLE_PLANT_OWNER)",
        "EXEMPLAR_ONLY": "EXECUTE_TYPED_EXEMPLAR_STEP;NO_CONTROL_VALUE_INFERRED",
    }
    result = effects[template]
    if event["terminal_status"] == "TERMINAL":
        result += ";CLOSE_LOCAL_FIELD_ONLY"
    return result


def medical_rival(phrase: str, template: str) -> str:
    low = phrase.lower()
    if template == "ACTION_APPLY" or "verwende" in low or "prüfe" in low:
        return "MEDICAL_RIVAL: therapeutische Anwendung oder Probe derselben unbekannten Heilzubereitung."
    if template == "PARAMETER_ASSIGN" or "maß" in low or "bemesse" in low:
        return "MEDICAL_RIVAL: Dosis-, Dauer- oder Mengenangabe in einem Heilrezept."
    if "wasser" in low or "auszug" in low or "flüssigkeit" in low or "seihe" in low:
        return "MEDICAL_RIVAL: wässrige oder andere flüssige Heilmittelzubereitung aus derselben Bildpflanze."
    if "trock" in low or "lager" in low or "bewahr" in low:
        return "MEDICAL_RIVAL: Vorratshaltung eines heilkundlich bestimmten Pflanzenanteils."
    if "probe" in low or "material" in low or "kopf" in low or "blatt" in low:
        return "MEDICAL_RIVAL: Auswahl eines heilkundlich bestimmten Pflanzenanteils statt einer Materialprobe."
    return "MEDICAL_RIVAL: dieselbe Folge als unbekannter heilkundlicher Pflanzenartikel."


def contradiction(event: dict[str, str], phrase: str) -> str:
    issues = ["Bild bindet nur die ganze Pflanze, nicht diesen konkreten Arbeitsschritt"]
    low = phrase.lower()
    if any(word in low for word in ("wasser", "gefäß", "tuch", "mörser", "becher")):
        issues.append("Medium und Gerät sind nicht abgebildet")
    if event["parse_status"] == "UNPARSED_EXEMPLAR":
        issues.append("Ereignis besitzt keine bekannte Karte; Objekt und Handlung sind reine Exemplarfüllung")
    else:
        issues.append("bekannte Karte/Formalklasse ist nur gefrorener Prompt und trägt diese konkrete Lesung nicht")
    if event["terminal_status"] == "TERMINAL":
        issues.append("CLOSE beweist nur lokalen Formabschluss, nicht den gewählten Prozessabschluss")
    return "; ".join(issues) + "."


def selected_event_segments(statement: dict[str, str]) -> dict[int, str]:
    found: dict[int, str] = {}
    for part in statement["literal_owner_card_exemplar_layer"].split(" > "):
        match = re.match(r"E(\d+):(.*)", part)
        if match:
            found[int(match.group(1))] = match.group(2)
    return found


def build() -> None:
    all_events = read_tsv(EVENT_SOURCE)
    all_fields = read_tsv(FIELD_SOURCE)
    all_owners = read_tsv(OWNER_SOURCE)
    all_statements = read_tsv(STATEMENT_SOURCE)

    events = [row for row in all_events if 1 <= int(row["event_serial"]) <= 100]
    fields = [row for row in all_fields if row["record_unit_id"] in OWNERS]
    owners = {row["unit_id"]: row for row in all_owners if row["unit_kind"] == "PROSE_FIELD" and row["record_or_diagram"] in OWNERS}
    statements = {row["statement_id"]: row for row in all_statements if row["record_unit_id"] in OWNERS}

    segment_by_event: dict[int, str] = {}
    for statement in statements.values():
        segment_by_event.update(selected_event_segments(statement))

    field_event_counts = Counter(row["field_id"] for row in events)
    for field_id, program in FIELD_PROGRAMS.items():
        assert len(program) == field_event_counts[field_id], (field_id, len(program), field_event_counts[field_id])

    ordinal_by_field: Counter[str] = Counter()
    interlinear: list[dict[str, object]] = []
    for event in events:
        serial = int(event["event_serial"])
        field_id = event["field_id"]
        ordinal_by_field[field_id] += 1
        ordinal = ordinal_by_field[field_id]
        phrase = FIELD_PROGRAMS[field_id][ordinal - 1]
        owner_row = owners[field_id]
        assert owner_row["selected_visible_owner"] == OWNERS[event["record_unit_id"]]
        selected_segment = segment_by_event[serial]
        known = event["parse_status"] != "UNPARSED_EXEMPLAR"
        confidence = 0.44 if known else 0.24
        if event["event_template"] in {"SELECT_PREVIOUS", "STATE_GATE", "TARGET_ASSIGN", "SELECT_PART"}:
            confidence += 0.03
        if event["terminal_status"] == "TERMINAL":
            confidence -= 0.02
        row: dict[str, object] = {
            "event_serial": serial,
            "page": event["page"],
            "locus": event["locus"],
            "record_unit_id": event["record_unit_id"],
            "field_id": field_id,
            "statement_id": event["statement_id"],
            "event_ordinal_in_field": ordinal,
            "joint_tuple_id": event["joint_tuple_id"],
            "surface_display_only": event["surface_display_only"],
            "formal_formula_opaque": event["formal_formula_opaque"],
            "terminal_status": event["terminal_status"],
            "parse_status": event["parse_status"],
            "selected_exact_mnemonic": event["selected_exact_mnemonic"],
            "strict_formal_prompt": event["strict_formal_prompt"],
            "event_template": event["event_template"],
            "literal_exact_card_formal_exemplar_layer": event_literal(event, selected_segment),
            "whole_plant_owner": owner_row["selected_visible_owner"],
            "owner_status": owner_row["owner_status"],
            "owner_confidence": owner_row["confidence"],
            "concrete_technical_default": phrase,
            "default_layer": "FROZEN_CONTROL_CLASS_PLUS_CREATIVE_SOURCE_ARGUMENT" if known else "CREATIVE_OCCURRENCE_EXEMPLAR_FILL",
            "register_effect_in_creative_template": register_effect(event),
            "technical_default_confidence": f"{confidence:.2f}",
            "strongest_medical_rival": medical_rival(phrase, event["event_template"]),
            "contradiction": contradiction(event, phrase),
            "semantic_ceiling": "CREATIVE_NONMEDICAL_EXEMPLAR_NOT_TRANSLATION_CARD_VALUE_STEM_OR_SPECIES",
        }
        interlinear.append(row)

    interlinear_columns = [
        "event_serial", "page", "locus", "record_unit_id", "field_id", "statement_id",
        "event_ordinal_in_field", "joint_tuple_id", "surface_display_only", "formal_formula_opaque",
        "terminal_status", "parse_status", "selected_exact_mnemonic", "strict_formal_prompt",
        "event_template", "literal_exact_card_formal_exemplar_layer", "whole_plant_owner",
        "owner_status", "owner_confidence", "concrete_technical_default", "default_layer",
        "register_effect_in_creative_template", "technical_default_confidence",
        "strongest_medical_rival", "contradiction", "semantic_ceiling",
    ]
    interlinear_path = OUT / "V73_R3_100_EVENT_INTERLINEAR.tsv"
    write_tsv(interlinear_path, interlinear, interlinear_columns)

    events_by_field: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in interlinear:
        events_by_field[str(row["field_id"])].append(row)

    field_rows: list[dict[str, object]] = []
    for field in fields:
        field_id = field["field_id"]
        selected_statement = statements[field["statement_id"]]
        event_rows = events_by_field[field_id]
        owner_row = owners[field_id]
        field_rows.append({
            "field_id": field_id,
            "record_unit_id": field["record_unit_id"],
            "page": field["page"],
            "locus": field["locus"],
            "statement_id": field["statement_id"],
            "event_count": field["event_count"],
            "event_serials": field["event_serials"],
            "whole_plant_owner": owner_row["selected_visible_owner"],
            "owner_status": owner_row["owner_status"],
            "owner_confidence": owner_row["confidence"],
            "process_stage": FIELD_STAGE[field_id],
            "literal_event_sequence": " > ".join(str(row["literal_exact_card_formal_exemplar_layer"]) for row in event_rows),
            "concrete_nonmedical_field_reading": FIELD_TEXT[field_id],
            "selected_v72_statement_reading": selected_statement["selected_concrete_paraphrase"],
            "v73_revision": "REPLACE_MEDICAL_OR_RECEPTARIUM_DEFAULT_WITH_NONMEDICAL_PLANT_MATERIAL_PROCESS;KEEP_EVENT_ORDER_OWNER_AND_CONTROL_LAYER",
            "strongest_medical_rival": selected_statement["selected_concrete_paraphrase"],
            "contradiction": owner_row["visible_basis"] + " Concrete part, medium, vessel and operation remain unpictured exemplar fills.",
            "semantic_ceiling": "COMPLETE_CREATIVE_FIELD_NOT_DECIPHERMENT_OR_CARD_SEMANTICS",
        })

    field_columns = [
        "field_id", "record_unit_id", "page", "locus", "statement_id", "event_count",
        "event_serials", "whole_plant_owner", "owner_status", "owner_confidence", "process_stage",
        "literal_event_sequence", "concrete_nonmedical_field_reading", "selected_v72_statement_reading",
        "v73_revision", "strongest_medical_rival", "contradiction", "semantic_ceiling",
    ]
    field_path = OUT / "V73_R3_20_FIELD_EDITION.tsv"
    write_tsv(field_path, field_rows, field_columns)

    fields_by_record: dict[str, list[dict[str, object]]] = defaultdict(list)
    events_by_record: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in field_rows:
        fields_by_record[str(row["record_unit_id"])].append(row)
    for row in interlinear:
        events_by_record[str(row["record_unit_id"])].append(row)

    article_rows: list[dict[str, object]] = []
    for record in ["H1", "H2", "H3", "H4", "H5"]:
        record_fields = fields_by_record[record]
        record_events = events_by_record[record]
        statement_ids = list(dict.fromkeys(str(row["statement_id"]) for row in record_fields))
        article_rows.append({
            "record_unit_id": record,
            "page": record_fields[0]["page"],
            "whole_plant_owner": OWNERS[record],
            "owner_gloss_not_translation": OWNER_GLOSSES[record],
            "field_ids": "|".join(str(row["field_id"]) for row in record_fields),
            "statement_ids": "|".join(statement_ids),
            "field_count": len(record_fields),
            "statement_count": len(statement_ids),
            "event_count": len(record_events),
            "article_title_nonsemantic": ARTICLE_TITLES[record],
            "complete_readable_nonmedical_article": ARTICLE_TEXTS[record],
            "execution_trace": " > ".join(str(row["process_stage"]) for row in record_fields),
            "strongest_medical_rival": ARTICLE_RIVALS[record],
            "hardest_contradiction": ARTICLE_CONTRADICTIONS[record],
            "semantic_ceiling": "WORKSHOP_PROCESS_ARTICLE_NOT_HISTORICAL_TRANSLATION_OR_DOMAIN_IDENTIFICATION",
        })

    article_columns = [
        "record_unit_id", "page", "whole_plant_owner", "owner_gloss_not_translation",
        "field_ids", "statement_ids", "field_count", "statement_count", "event_count",
        "article_title_nonsemantic", "complete_readable_nonmedical_article", "execution_trace",
        "strongest_medical_rival", "hardest_contradiction", "semantic_ceiling",
    ]
    article_path = OUT / "V73_R3_FIVE_ARTICLES.tsv"
    write_tsv(article_path, article_rows, article_columns)

    revision_rows: list[dict[str, object]] = []
    for statement_id in sorted(statements, key=lambda value: (int(value[1]), int(value.split("S")[1]))):
        selected = statements[statement_id]
        constituent = selected["constituent_fields"].split("|")
        new_reading = " ".join(FIELD_TEXT[field_id] for field_id in constituent)
        revision_rows.append({
            "statement_id": statement_id,
            "record_unit_id": selected["record_unit_id"],
            "page": selected["page"],
            "constituent_fields": selected["constituent_fields"],
            "event_count": selected["event_count"],
            "v72_selected_reading": selected["selected_concrete_paraphrase"],
            "v73_nonmedical_reading": new_reading,
            "retained": "EXACT_EVENT_ORDER;WHOLE_PLANT_OWNER;KNOWN_CARD_FORMAL_LAYER;RECORD_LOCAL_CONTINUITY",
            "withdrawn": "MEDICAL_USE;SPECIES;PART_OWNER;UNPICTURED_PROCESS_AS_VISIBLE_FACT",
            "revision_reason": "Requested complete nonmedical plant-material counter-reading under the same frozen formal skeleton.",
            "semantic_ceiling": "RIVAL_WORKING_EDITION_NOT_EVIDENCE_FOR_DOMAIN",
        })
    revision_columns = [
        "statement_id", "record_unit_id", "page", "constituent_fields", "event_count",
        "v72_selected_reading", "v73_nonmedical_reading", "retained", "withdrawn",
        "revision_reason", "semantic_ceiling",
    ]
    revision_path = OUT / "V73_R3_19_STATEMENT_REVISIONS.tsv"
    write_tsv(revision_path, revision_rows, revision_columns)

    report_path = OUT / "V73_R3_TECHNICAL_REPORT.md"
    lines = [
        "# V73 R3 — nichtmedizinische Herbal-Drittedition",
        "",
        "Status: kreative Zehnseiten-Werkstattedition, keine Entzifferung oder Übersetzung.",
        "",
        "## Ergebnis",
        "",
        "Die Edition belegt alle **100 Herbal-Ereignisse**, **20 Felder**, **19 Aussagen** und **5 Records** ohne Leerstelle. "
        "Sie liest die fünf Records als Pflanzenmaterial-Buchungen für Probenahme, Vorbereitung, Nassauszug, Fraktionsvergleich und Lagerung. "
        "Von den 100 Ereignissen sind 29 durch eine eingefrorene Karte/Formalklasse teilweise typisiert; 71 bleiben reine Exemplarwerte.",
        "",
        "Jedes Bild besitzt weiterhin nur einen Ganzpflanzenartikel. Weder Texttasche noch Blatt, Wurzel oder Kopf wird zum eigenen Bildbesitzer. "
        "Wasser ist in mehreren Arbeitsdefaults ausdrücklich zugelassen, aber ebenso ausdrücklich **nicht abgebildet**.",
        "",
        "## Unveränderter technischer Rollenstand",
        "",
        "1. Die Gegenlesung denkt in Werkstattlisten, Abrechnungen, Maßen, Kalendern und Rezeptparametern.",
        "2. Karten dienen als Adressen, Verweise, Slots, Abhängigkeiten und Abschlusszeichen.",
        "3. Das Verfahren muss um 1420 handschriftlich ausführbar bleiben.",
        "4. Seitenlayout, Renderer und gespeicherter Exemplarwert bleiben getrennt.",
        "5. Eine brauchbare Lesung braucht eine ausführbare Regel, Beispielbuchungen und sichtbare Scheiterfälle.",
        "",
        "## Ausführbare Quellenregel",
        "",
        "```text",
        "BEGIN_RECORD(record, WHOLE_PLANT_OWNER)",
        "  ACTIVE = PREVIOUS = TARGET = MEASURE = UNSET",
        "  FOR each frozen event in exact V69 order:",
        "    emit exact tuple ID + opaque formula + known question-mark card/prompt",
        "    obtain the unknown occurrence value from the workshop exemplar",
        "    execute the occurrence-specific plant-work instruction",
        "    update only the licensed local register effect",
        "    CLOSE closes the local field, never proves a physical operation",
        "  END",
        "  clear all registers; no value passes to the next H-record",
        "END_RECORD",
        "```",
        "",
        "`SELECT_PREVIOUS` therefore means previous **within the current record only**. `LINK_ACTIVE` joins bookkeeping state, not an invisible pictured pipe. "
        "A known card still receives a concrete source argument from the exemplar; an unknown event receives both its typed value and its concrete action there.",
        "",
        "## Die fünf vollständigen Artikel",
        "",
    ]
    for article in article_rows:
        lines.extend([
            f"### {article['record_unit_id']} — {article['article_title_nonsemantic']}",
            "",
            str(article["complete_readable_nonmedical_article"]),
            "",
            f"Ablauf: `{article['execution_trace']}`.",
            "",
            f"Stärkster medizinischer Rivale: {article['strongest_medical_rival']}",
            "",
            f"Härtester Widerspruch: {article['hardest_contradiction']}",
            "",
        ])
    lines.extend([
        "## Was diese Fassung gewinnt",
        "",
        "- Sie gibt jedem der 100 Ereignisse eine kleine, ausführbare Defaultrolle.",
        "- Sie braucht keine Pflanzenart und keine neu erfundene Wortwurzel.",
        "- Sie nutzt Wasser nur dort, wo ein Nassprozess den Record tatsächlich zusammenhängender macht.",
        "- H1/H2 werden trotz gleicher Bildpflanze als getrennte Lose geführt; `VORIGES?` greift nicht über die Recordgrenze.",
        "- f55v-Texttaschen bleiben Restflächen um eine ganze Pflanze und werden nicht zu Blatt-/Wurzelrubriken.",
        "",
        "## Was sie nicht gewinnt",
        "",
        "Der Großteil der konkreten Handlung ist nicht im Formsystem erkannt: 71 Ereignisse sind vollkommen exemplarabhängig, und auch die 29 typisierten Ereignisse tragen nur Fragezeichen-Mnemonics oder Formalprompts. "
        "Kein Bild zeigt Wasser, Gefäß, Tuch, Mörser, Maß, Vergleichsbrett oder Lagerbehälter. Die technische Lesung ist deshalb eine kohärente nichtmedizinische Gegenfüllung derselben offenen Slots, keine bessere historische Übersetzung als der medizinische Rivale.",
        "",
        "Keine Karte, kein Stamm, kein Laut, keine Art und kein Klartext wurde neu bestätigt. f84 und f84r wurden nicht geöffnet.",
        "",
    ])
    report_path.write_text("\n".join(lines), encoding="utf-8")

    sources = [EVENT_SOURCE, FIELD_SOURCE, OWNER_SOURCE, STATEMENT_SOURCE]
    summary = {
        "experiment": "V73_R3_NONMEDICAL_HERBAL_THIRD_EDITION",
        "status": "CREATIVE_WORKSHOP_EDITION_NOT_DECIPHERMENT",
        "counts": {
            "events": len(interlinear),
            "fields": len(field_rows),
            "statements": len(revision_rows),
            "records": len(article_rows),
            "recognized_events": sum(row["parse_status"] != "UNPARSED_EXEMPLAR" for row in events),
            "exemplar_only_events": sum(row["parse_status"] == "UNPARSED_EXEMPLAR" for row in events),
        },
        "pages": sorted({str(row["page"]) for row in interlinear}),
        "source_hashes": {str(path.relative_to(ROOT)): sha256(path) for path in sources},
        "output_hashes": {
            path.name: sha256(path)
            for path in [interlinear_path, field_path, article_path, revision_path, report_path]
        },
        "sealed": ["f84", "f84r"],
        "semantic_ceiling": "NO_TRANSLATION_NO_CARD_OR_STEM_VALUE_NO_SPECIES_NO_DOMAIN_PROMOTION",
    }
    (OUT / "V73_R3_BUILD_SUMMARY.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )


if __name__ == "__main__":
    build()
