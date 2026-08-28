#!/usr/bin/env python3
"""Exploratory concrete defaults for GDT582's mixed codebook."""

from __future__ import annotations


REGISTERS = (
    "SOURCE_SECTION_T",
    "HERBAL",
    "CELESTIAL",
    "BIOLOGICAL",
    "PHARMA",
)


# One compact invariant concept is retained per productive function stem.  The
# German value is the deliberately concrete universal workshop rival.  The
# selected pack may realize that concept more naturally in a register below.
CORE_DEFAULTS: dict[str, tuple[str, str, str]] = {
    "AIIN": ("OBJECT", "MEASURE_OR_VALUE", "Maß oder Kennwert"),
    "AIN": ("OBJECT", "PORTION_OR_FRACTION", "Teil oder Portion"),
    "AIR": ("RELATION", "WORKING_PATH", "entlang des Arbeitswegs"),
    "AL": ("RELATION", "TARGET", "zum Ziel"),
    "AM_ADDR": ("MODIFIER", "AUXILIARY_SITE", "an der Nebenstelle"),
    "AN": ("MODIFIER", "KIND_OR_CLASS", "in der bezeichneten Art"),
    "AR": ("RELATION", "SOURCE", "von der Quelle"),
    "A_ADDR": ("MODIFIER", "MAIN_SITE", "an der Hauptstelle"),
    "CARRIER_Q": ("MODIFIER", "NEW_BATCH", "als Neuansatz"),
    "CH": ("ACTION", "TAKE_OR_EXTRACT", "Entnimm"),
    "CHD": ("ACTION", "PROCESS_OR_TREAT", "Bearbeite"),
    "DA": ("MODIFIER", "SECOND_PASS", "im zweiten Durchgang"),
    "D_ADDR": ("MODIFIER", "WORK_SITE", "an der Arbeitsstelle"),
    "D_LABEL": ("MODIFIER", "D_VARIANT", "in der d-Variante"),
    "E": ("MODIFIER", "LOW_DEGREE", "auf Grad I"),
    "EE": ("MODIFIER", "MIDDLE_DEGREE", "auf Grad II"),
    "EEE": ("MODIFIER", "HIGH_DEGREE", "auf Grad III"),
    "G_LABEL": ("MODIFIER", "G_VARIANT", "in der g-Variante"),
    "HO": ("MODIFIER", "UPPER_CLASS", "in der Oberklasse"),
    "IIN": ("MODIFIER", "WORKING_STAGE", "auf der bezeichneten Stufe"),
    "K": ("ACTION", "TRANSFER_OR_ADD", "Gib zu"),
    "L": ("RELATION", "CONTACT_OR_CONNECTION", "über die Verbindung"),
    "LOCAL_CHAR_B": ("MODIFIER", "B_VARIANT", "in der b-Variante"),
    "LOCAL_CHAR_F": ("MODIFIER", "FINE_FORM", "in Feinform"),
    "LOCAL_CHAR_G": ("MODIFIER", "ALTERNATE_FORM", "in der Alternativform"),
    "LOCAL_CHAR_I": ("MODIFIER", "INNER_FORM", "in der Innenform"),
    "LOCAL_CHAR_J": ("MODIFIER", "J_VARIANT", "in der j-Variante"),
    "LOCAL_CHAR_Z": ("MODIFIER", "Z_VARIANT", "in der z-Variante"),
    "M_LOCAL": ("MODIFIER", "MIDDLE_SITE", "an der Mittelstelle"),
    "O": ("MODIFIER", "FORM_OR_MODE", "in Arbeitsform"),
    "OK": ("ACTION", "SET_OR_OPEN_BATCH", "Setze an"),
    "OR": ("OBJECT", "UNIT_OR_BATCH", "Einheit oder Ansatz"),
    "OS": ("MODIFIER", "PRIOR_REFERENCE", "mit Vorbezug"),
    "P": ("ACTION", "INSERT_OR_APPLY", "Lege ein"),
    "R": ("ACTION", "CHECK_OR_MARK", "Kennzeichne"),
    "S": ("ACTION", "SELECT_OR_SEPARATE", "Wähle aus"),
    "SH": ("ACTION", "HOLD_OR_REST", "Halte oder lass stehen"),
    "S_ADDR": ("MODIFIER", "END_SITE", "an der Endstelle"),
    "S_LABEL": ("MODIFIER", "S_VARIANT", "in der s-Variante"),
    "T": ("ACTION", "ADJUST_OR_TEMPER", "Stelle ein oder temperiere"),
    "Y": ("OBJECT", "CURRENT_GOOD_OR_BATCH", "Arbeitsgut"),
    "Z_ADDR": ("MODIFIER", "Z_SITE", "an der z-Stelle"),
}


REGISTER_OVERRIDES: dict[str, dict[str, str]] = {
    "SOURCE_SECTION_T": {
        "AIIN": "Flüssigkeitsmaß",
        "AIN": "Portion",
        "OR": "Ansatz",
        "Y": "Arbeitsgut",
        "AL": "zur Zielstelle oder ins Zielgefäß",
        "AR": "von der Quelle oder aus dem Ausgangsgefäß",
        "L": "über den Arbeitskontakt",
        "AIR": "entlang des Arbeitswegs",
        "OK": "Setze an",
        "CH": "Entnimm",
        "SH": "Lass ruhen",
        "K": "Gib zu",
        "S": "Sondere aus",
        "CHD": "Bearbeite",
        "T": "Stelle ein oder temperiere",
        "R": "Kennzeichne oder prüfe",
        "P": "Bringe ein",
        "O": "in Arbeitsform",
        "IIN": "auf der bezeichneten Stufe",
        "D_ADDR": "an der Arbeitsstelle",
        "A_ADDR": "an der Hauptstelle",
        "AM_ADDR": "an der Nebenstelle",
        "S_ADDR": "an der Endstelle",
        "CARRIER_Q": "als Neuansatz",
    },
    "HERBAL": {
        "AIIN": "Pflanzenauszug oder Arbeitsmaß",
        "AIN": "Pflanzenportion",
        "OR": "Pflanzen- oder Arbeitseinheit",
        "Y": "Pflanzencharge",
        "AL": "zur Zielstelle oder ins Auffanggefäß",
        "AR": "vom Ausgangsmaterial oder -gefäß",
        "L": "über den Materialkontakt",
        "AIR": "entlang des Verarbeitungswegs",
        "OK": "Setze den Pflanzenansatz an",
        "CH": "Entnimm oder ziehe aus",
        "SH": "Halte oder lass ziehen",
        "K": "Gib zu",
        "S": "Wähle oder trenne ab",
        "CHD": "Bearbeite oder zerreibe",
        "T": "Stelle ein oder temperiere",
        "R": "Kennzeichne oder prüfe",
        "P": "Bringe ein",
        "O": "in Zubereitungsform",
        "IIN": "auf der Verarbeitungsstufe",
        "D_ADDR": "an der Pflanzen-Arbeitsstelle",
        "A_ADDR": "an der Pflanzen-Hauptstelle",
        "AM_ADDR": "an der Pflanzen-Nebenstelle",
        "S_ADDR": "an der Pflanzen-Endstelle",
        "CARRIER_Q": "als neuer Pflanzenansatz",
        "LOCAL_CHAR_F": "in Feinform",
        "LOCAL_CHAR_G": "in der Alternativform",
        "LOCAL_CHAR_I": "in der Innenform",
        "HO": "in der Oberklasse",
        "AN": "in der bezeichneten Pflanzenart",
        "OS": "mit Vorbezug",
    },
    "CELESTIAL": {
        "AIIN": "Positionswert",
        "AIN": "Sektoranteil",
        "OR": "Sektoreinheit",
        "Y": "Ringposition",
        "AL": "zur Zielposition",
        "AR": "von der Ausgangsposition",
        "L": "über den Ringkontakt",
        "AIR": "entlang der Ringbahn",
        "OK": "Trage ein",
        "CH": "Lies ab",
        "SH": "Halte fest",
        "K": "Ordne zu",
        "S": "Wähle aus",
        "CHD": "Berechne",
        "T": "Stelle ein",
        "R": "Markiere",
        "P": "Setze ein",
        "O": "in Eintragsform",
        "IIN": "auf der Feinstufe",
        "E": "auf Ringstufe I",
        "EE": "auf Ringstufe II",
        "EEE": "auf Ringstufe III",
        "D_ADDR": "an der unteren Ringstelle",
        "A_ADDR": "an der oberen Ringstelle",
        "AM_ADDR": "an der mittleren Ringstelle",
        "S_ADDR": "an der seitlichen Ringstelle",
        "Z_ADDR": "an der Zielmarke",
        "CARRIER_Q": "im Tabellenfeld",
        "LOCAL_CHAR_F": "bei der f-Marke",
        "LOCAL_CHAR_G": "bei der g-Marke",
        "LOCAL_CHAR_I": "bei der i-Marke",
        "LOCAL_CHAR_Z": "bei der z-Marke",
        "M_LOCAL": "an der Messmarke",
        "HO": "an der oberen Marke",
        "AN": "an der Nachbarmarke",
        "OS": "am Außenring",
        "D_LABEL": "in der d-Klasse",
        "G_LABEL": "in der g-Klasse",
        "S_LABEL": "in der s-Klasse",
    },
    "BIOLOGICAL": {
        "AIIN": "Stations- oder Badmaß",
        "AIN": "Anwendungsportion",
        "OR": "Becken- oder Körpereinheit",
        "Y": "Stationsansatz",
        "AL": "zur Zielstation oder ins Zielbecken",
        "AR": "von der Ausgangsstation oder aus dem Ausgangsbecken",
        "L": "über den Stationskontakt oder die Leitung",
        "AIR": "entlang des Stationswegs oder Kanals",
        "OK": "Beschicke oder bereite vor",
        "CH": "Entnimm oder lass ab",
        "SH": "Halte oder bade",
        "K": "Führe zu",
        "S": "Wähle oder leite um",
        "CHD": "Behandle",
        "T": "Reguliere oder temperiere",
        "R": "Kennzeichne oder prüfe",
        "P": "Bringe ein oder wende an",
        "O": "in Anwendungsform",
        "IIN": "auf der Anwendungsstufe",
        "E": "auf Grad I",
        "EE": "auf Grad II",
        "EEE": "auf Grad III",
        "D_ADDR": "an der Stations-Arbeitsstelle",
        "A_ADDR": "an der Stations-Hauptstelle",
        "AM_ADDR": "an der Stations-Nebenstelle",
        "S_ADDR": "an der Stations-Endstelle",
        "CARRIER_Q": "als neuer Bad- oder Stationsansatz",
        "LOCAL_CHAR_F": "in Feinform",
        "LOCAL_CHAR_G": "in der Alternativform",
        "LOCAL_CHAR_I": "in der Innenform",
        "LOCAL_CHAR_B": "in der b-Variante",
        "HO": "in der Oberklasse",
        "AN": "in der bezeichneten Stationsart",
    },
    "PHARMA": {
        "AIIN": "Dosis- oder Mengenmaß",
        "AIN": "Zutatenanteil",
        "OR": "Gefäß- oder Arbeitseinheit",
        "Y": "Drogencharge",
        "AL": "ins Aufnahme- oder Zielgefäß",
        "AR": "aus dem Ausgangsgefäß",
        "L": "über den Gefäßkontakt",
        "AIR": "durch den Transferkanal",
        "OK": "Setze den Ansatz an",
        "CH": "Entnimm oder ziehe aus",
        "SH": "Halte oder lass ziehen",
        "K": "Gib zu",
        "S": "Wähle oder trenne ab",
        "CHD": "Bearbeite oder zerreibe",
        "T": "Stelle ein oder temperiere",
        "R": "Kennzeichne oder prüfe",
        "P": "Gib hinein",
        "O": "in Arzneiform",
        "IIN": "auf der Zubereitungsstufe",
        "E": "auf Grad I",
        "EE": "auf Grad II",
        "EEE": "auf Grad III",
        "D_ADDR": "an der Drogen-Arbeitsstelle",
        "A_ADDR": "an der Drogen-Hauptstelle",
        "AM_ADDR": "an der Drogen-Nebenstelle",
        "S_ADDR": "an der Drogen-Endstelle",
        "CARRIER_Q": "als neuer Arzneiansatz",
        "LOCAL_CHAR_F": "in Feinform",
        "LOCAL_CHAR_G": "in der Alternativform",
        "LOCAL_CHAR_I": "in der Innenform",
        "LOCAL_CHAR_J": "in der j-Variante",
        "LOCAL_CHAR_B": "in der b-Variante",
        "M_LOCAL": "an der Mittelstelle",
        "G_LABEL": "in der g-Variante",
        "HO": "in der Oberklasse",
    },
}


ACTION_NOUNS: dict[str, dict[str, str]] = {
    "SOURCE_SECTION_T": {
        "OK": "Ansetzen", "CH": "Entnehmen", "SH": "Ruhenlassen",
        "K": "Zugeben", "S": "Auswählen oder Aussondern", "CHD": "Bearbeiten",
        "T": "Einstellen oder Temperieren", "R": "Kennzeichnen oder Prüfen", "P": "Einbringen",
    },
    "HERBAL": {
        "OK": "Ansetzen", "CH": "Entnehmen oder Ausziehen", "SH": "Halten oder Ziehenlassen",
        "K": "Zugeben", "S": "Auswählen oder Abtrennen", "CHD": "Bearbeiten oder Zerreiben",
        "T": "Einstellen oder Temperieren", "R": "Kennzeichnen oder Prüfen", "P": "Einbringen",
    },
    "CELESTIAL": {
        "OK": "Eintragen", "CH": "Ablesen", "SH": "Festhalten",
        "K": "Zuordnen", "S": "Auswählen", "CHD": "Berechnen",
        "T": "Einstellen", "R": "Markieren", "P": "Einsetzen",
    },
    "BIOLOGICAL": {
        "OK": "Beschicken oder Vorbereiten", "CH": "Entnehmen oder Ablassen", "SH": "Halten oder Baden",
        "K": "Zuführen", "S": "Auswählen oder Umleiten", "CHD": "Behandeln",
        "T": "Regulieren oder Temperieren", "R": "Kennzeichnen oder Prüfen", "P": "Einbringen oder Anwenden",
    },
    "PHARMA": {
        "OK": "Ansetzen", "CH": "Entnehmen oder Ausziehen", "SH": "Halten oder Ziehenlassen",
        "K": "Zugeben", "S": "Auswählen oder Abtrennen", "CHD": "Bearbeiten oder Zerreiben",
        "T": "Einstellen oder Temperieren", "R": "Kennzeichnen oder Prüfen", "P": "Hineingeben",
    },
}


CONTROL_DEFAULTS: dict[str, tuple[str, str]] = {
    "OT": ("NEXT_RECORD", "danach / neuer Arbeitsgang"),
    "OL": ("CONTINUE_RECORD", "weiter im selben Arbeitsgang"),
    "DY": ("CLOSE_RECORD", "Arbeitsgang abschließen"),
    "RESUME_CARD": ("RESUME_MODIFIER", "vorige Angabe wieder aufnehmen"),
    "CHK": ("LOCAL_MACRO", "lokale CHK-Karte"),
    "CTH": ("LOCAL_MACRO", "lokale CTH-Karte"),
    "CPH": ("LOCAL_MACRO", "lokale CPH-Karte"),
    "CHEO": ("LOCAL_MACRO", "lokale CHEO-Karte"),
    "CFH": ("LOCAL_MACRO", "lokale CFH-Karte"),
    "CKH": ("LOCAL_MACRO", "lokale CKH-Karte"),
    "SECTION_MARKER": ("LOCAL_SIGN", "Abschnittsmarke"),
    "LOCAL_SIGN_X": ("LOCAL_SIGN", "lokales x-Zeichen"),
    "LOCAL_SIGN_C": ("LOCAL_SIGN", "lokales c-Zeichen"),
}


# Class-conditioned learned defaults deliberately form a nomenclator.  The
# raw core is not claimed to sound like the German ingredient.  It simply gets
# one replaceable default so that no learned name slot stays empty.
DRUG_INGREDIENT_DEFAULTS: dict[str, str] = {
    "d": "Wasser",
    "y": "Wein",
    "or": "Olivenöl",
    "s": "Salz",
    "yd": "Honig",
    "cheo": "Essig",
    "cphe": "Milch",
    "ody": "Bienenwachs",
    "ora": "Eiweiß",
    "cheosdy": "Eigelb",
    "am": "Schmalz",
    "dordy": "Butter",
    "da": "Mehl",
    "qk": "Asche",
    "dy": "Kalk",
    "cho": "Schwefel",
    "yko": "Alaun",
    "sy": "Vitriol",
    "od": "Harz",
    "opchos": "Gummi arabicum",
    "oiin": "Myrrhe",
    "e": "Weihrauch",
    "opchor": "Safranblüte",
    "opor": "Pfefferkorn oder Samen",
    "dchos": "Ingwerwurzel",
    "yor": "Zimtrinde",
    "ak": "Gewürznelkenknospe",
    "yt": "Salbeiblatt",
    "em": "Rautenblatt",
}


BATH_STATION_DEFAULTS: dict[str, str] = {
    "d": "Ablauf",
    "chd": "erwärmtes Becken",
    "kchs": "Zulaufrohr",
    "ork": "Badebecken",
    "sor": "Sitz- oder Behandlungsstation",
    "edy": "Kühlablauf",
}


PICTURED_PLANT_DEFAULTS: dict[str, str] = {
    "eeeon": "ganze blühende Heilpflanze",
    "oiil": "ganze Heilpflanze B",
}


# The only two running learned cores receive deliberately different, replaceable
# owner-bound readings.  Neither value is promoted to a productive stem.
LOCAL_X_DEFAULTS: dict[str, tuple[str, str]] = {
    "RUNNING:G515-E0410@2": ("INDICATION_OR_ILLNESS", "Krankheit oder Beschwerde"),
    "RUNNING:G515-E0438@2": ("REMEDY_OR_HEALING", "Heilmittel oder Heilwirkung"),
}


def core_family(root: str) -> str:
    return CORE_DEFAULTS[root][0]


def core_concept(root: str) -> str:
    return CORE_DEFAULTS[root][1]


def universal_gloss(root: str) -> str:
    return CORE_DEFAULTS[root][2]


def register_gloss(root: str, register: str) -> tuple[str, str]:
    override = REGISTER_OVERRIDES.get(register, {}).get(root)
    if override is not None:
        return override, "REGISTER_REALIZATION"
    return universal_gloss(root), "PORTABLE_CORE_REALIZATION"


def action_noun(root: str, register: str) -> str:
    value = ACTION_NOUNS.get(register, {}).get(root)
    if value is not None:
        return value
    if root in CORE_DEFAULTS:
        return core_concept(root).title()
    return f"{root}-Rahmen"
