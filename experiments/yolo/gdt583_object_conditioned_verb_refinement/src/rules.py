#!/usr/bin/env python3
"""Occurrence-level exploratory subreadings for GDT583.

The portable GDT582 core values remain unchanged.  These ordered rules add a
contextual voice using fixed GDT581 action hosts, register, owner/page class,
and immediate same-card action direction.  First match wins.
"""

from __future__ import annotations

from dataclasses import dataclass


TARGET_ROOTS = ("T", "SH", "CHD", "S")
REGISTER_ORDER = (
    "SOURCE_SECTION_T", "HERBAL", "CELESTIAL", "BIOLOGICAL", "PHARMA",
)
PHYSICAL = ("HERBAL", "BIOLOGICAL", "PHARMA")
HP = ("HERBAL", "PHARMA")


@dataclass(frozen=True)
class Rule:
    rule_id: str
    priority: int
    root: str
    registers: tuple[str, ...]
    source_ids: tuple[str, ...] = ()
    physical_pages_not: tuple[str, ...] = ()
    direct_any: tuple[str, ...] = ()
    direct_none: tuple[str, ...] = ()
    host_any: tuple[str, ...] = ()
    host_none: tuple[str, ...] = ()
    host_any_groups: tuple[tuple[str, ...], ...] = ()
    previous_actions: tuple[str, ...] = ()
    next_actions: tuple[str, ...] = ()
    working_default_de: str = ""
    concrete_sense_de: str = ""
    reading_tier: str = ""
    rationale: str = ""

    def matches(
        self,
        *,
        root: str,
        register: str,
        source_id: str,
        physical_page: str,
        direct_tokens: set[str],
        host_tokens: set[str],
        previous_action: str,
        next_action: str,
    ) -> bool:
        if root != self.root or register not in self.registers:
            return False
        if self.source_ids and source_id not in self.source_ids:
            return False
        if physical_page in self.physical_pages_not:
            return False
        if self.direct_any and not direct_tokens.intersection(self.direct_any):
            return False
        if self.direct_none and direct_tokens.intersection(self.direct_none):
            return False
        if self.host_any and not host_tokens.intersection(self.host_any):
            return False
        if self.host_none and host_tokens.intersection(self.host_none):
            return False
        if any(not host_tokens.intersection(group) for group in self.host_any_groups):
            return False
        if self.previous_actions and previous_action not in self.previous_actions:
            return False
        if self.next_actions and next_action not in self.next_actions:
            return False
        return True


CH_TO_SH_HOSTS = (
    "G407-E0068", "G407-E0118", "G407-E0200", "G407-E0298",
    "G407-E0494", "G407-E0682", "G407-E1077", "G407-E1963",
    "G407-E2361", "G407-E2533", "G407-E3497", "G407-E3858",
)


RULES = (
    # T: direction comes from immediate action order, never from a grade alone.
    Rule(
        "T_SOURCE_FIX", 10, "T", ("SOURCE_SECTION_T",),
        working_default_de="Lege fest",
        concrete_sense_de="Arbeitsbedingung oder Wert festlegen",
        reading_tier="REGISTER_SUBREADING",
        rationale="Source besitzt in GDT568 den Festlege-Verbrahmen",
    ),
    Rule(
        "T_CELESTIAL_SET", 20, "T", ("CELESTIAL",),
        working_default_de="Stelle die Ringposition ein",
        concrete_sense_de="Ringposition oder Tabellenwert einstellen",
        reading_tier="REGISTER_SUBREADING",
        rationale="celestiales Positions- und Tabellenregister",
    ),
    Rule(
        "T_AFTER_SH_COOL", 30, "T", PHYSICAL,
        previous_actions=("SH",),
        working_default_de="Kühle ab",
        concrete_sense_de="nach dem Halte-, Zieh- oder Badschritt abkühlen",
        reading_tier="REPEATED_DIRECTIONAL_SEQUENCE",
        rationale="sichtbare Umkehrfolge SH→T im selben festen Kartenhost",
    ),
    Rule(
        "T_HP_BEFORE_CHD_DRY", 40, "T", HP,
        next_actions=("CHD",),
        working_default_de="Trockne",
        concrete_sense_de="vor dem Aufarbeiten oder Zerreiben trocknen",
        reading_tier="LOCAL_BOLD_DIRECTIONAL_SEQUENCE",
        rationale="lokale Folge T→CHD auf f95v",
    ),
    Rule(
        "T_HP_BEFORE_SH_WARM", 50, "T", HP,
        next_actions=("SH",),
        working_default_de="Erwärme",
        concrete_sense_de="vor dem Ziehen- oder Halteschritt erwärmen",
        reading_tier="REPEATED_DIRECTIONAL_SEQUENCE",
        rationale="wiederkehrende Folge T→SH in Pflanzen- und Drogenkarten",
    ),
    Rule(
        "T_PHYSICAL_GRADE_TEMPER", 60, "T", PHYSICAL,
        direct_any=("E", "EE", "EEE"),
        working_default_de="Temperiere auf den Grad",
        concrete_sense_de="Charge, Bad oder Ansatz auf die geschriebene Stufe temperieren",
        reading_tier="GRADE_HOSTED_SUBREADING",
        rationale="Grad ist direkt von T oder einer auf T endenden Aktionskette gehostet",
    ),
    Rule(
        "T_HP_FORM_SET", 70, "T", HP,
        direct_any=("O", "IIN", "DA"),
        working_default_de="Stelle Form oder Stufe ein",
        concrete_sense_de="Zubereitungsform oder Verarbeitungsstufe einstellen",
        reading_tier="DIRECT_HOST_SUBREADING",
        rationale="Form-, Stufen- oder Durchgangsmarker direkt am T-Kopf",
    ),
    Rule(
        "T_BIO_STATION_REGULATE", 80, "T", ("BIOLOGICAL",),
        physical_pages_not=("f76r",),
        working_default_de="Reguliere die Station",
        concrete_sense_de="Bad-, Becken- oder Stationsbedingung regulieren",
        reading_tier="OWNER_REGISTER_SUBREADING",
        rationale="bebilderter Bad-, Becken- oder Stationsowner",
    ),
    Rule(
        "T_HP_MEASURE_SET", 90, "T", HP,
        direct_any=("AIIN", "AIN", "OR", "AL", "AR", "L", "AIR", "A_ADDR", "D_ADDR", "S_ADDR"),
        direct_none=("Y",),
        working_default_de="Stelle Maß oder Ort ein",
        concrete_sense_de="Maß, Anteil, Einheit oder Arbeitsort einstellen",
        reading_tier="DIRECT_HOST_SUBREADING",
        rationale="direktes Maß-, Einheits- oder Ortsargument ohne Charge",
    ),
    Rule(
        "T_PHYSICAL_BROAD", 99, "T", PHYSICAL,
        working_default_de="Stelle ein oder temperiere",
        concrete_sense_de="Charge oder Arbeitsbedingung einstellen oder temperieren",
        reading_tier="HONEST_BROAD_FALLBACK",
        rationale="Charge allein entscheidet weder Wärme, Kälte noch Trocknung",
    ),

    # SH: the twelve known CH→SH argument bridges override physical imagery.
    Rule(
        "SH_CH_BRIDGE_HOLD", 110, "SH", REGISTER_ORDER,
        source_ids=CH_TO_SH_HOSTS,
        working_default_de="Halte",
        concrete_sense_de="das vom Entnehmen übernommene Argument halten",
        reading_tier="OBSERVED_ARGUMENT_BRIDGE",
        rationale="GDT507-CH→SH-Brücke mit identischem Argument",
    ),
    Rule(
        "SH_CELESTIAL_FIX", 120, "SH", ("CELESTIAL",),
        working_default_de="Halte die Position fest",
        concrete_sense_de="Ringposition oder Tabellenwert festhalten",
        reading_tier="REGISTER_SUBREADING",
        rationale="celestiales Positions- und Tabellenregister",
    ),
    Rule(
        "SH_BIO_BATHE", 130, "SH", ("BIOLOGICAL",),
        physical_pages_not=("f76r",),
        host_any=("Y", "AIIN", "AIN", "OR", "E", "EE", "EEE", "O", "IIN", "LOCAL_CHAR_F"),
        working_default_de="Halte im Bad",
        concrete_sense_de="Anwendung im Bad- oder Stationsgang halten beziehungsweise baden",
        reading_tier="OWNER_OBJECT_SUBREADING",
        rationale="bebilderter Badowner plus Objekt-, Grad- oder Formsignal",
    ),
    Rule(
        "SH_HP_EXTRACT_STEEP", 140, "SH", HP,
        host_any=("AIIN",),
        working_default_de="Lass den Auszug ziehen",
        concrete_sense_de="Pflanzen- oder Drogengut im Auszug ziehen lassen",
        reading_tier="REMOTE_OBJECT_SUBREADING",
        rationale="AIIN ist im vollständigen GDT581-SH-Host sichtbar",
    ),
    Rule(
        "SH_HP_SOAK", 150, "SH", HP,
        host_any_groups=(("Y", "AIN", "OR"), ("E", "EE", "EEE", "O", "IIN", "LOCAL_CHAR_F")),
        working_default_de="Weiche ein",
        concrete_sense_de="Charge oder Portion in Form beziehungsweise auf Stufe einweichen",
        reading_tier="OBJECT_FORM_SUBREADING",
        rationale="Materialobjekt und Grad- oder Formsignal teilen den SH-Host",
    ),
    Rule(
        "SH_SOURCE_REST", 160, "SH", ("SOURCE_SECTION_T",),
        working_default_de="Lass ruhen",
        concrete_sense_de="Arbeitsgut oder Ansatz ruhen lassen",
        reading_tier="REGISTER_SUBREADING",
        rationale="Source-Ruhenlassen-Verbrahmen",
    ),
    Rule(
        "SH_REST_HOLD", 169, "SH", REGISTER_ORDER,
        working_default_de="Halte",
        concrete_sense_de="Zustand oder Argument halten",
        reading_tier="HONEST_BROAD_FALLBACK",
        rationale="kein hinreichender Bad-, Auszug- oder Einweichanker",
    ),

    # CHD: liquid signals veto grinding; the portable core remains processing.
    Rule(
        "CHD_CELESTIAL_CALCULATE", 170, "CHD", ("CELESTIAL",),
        working_default_de="Berechne",
        concrete_sense_de="Ringposition oder Tabellenwert berechnen",
        reading_tier="REGISTER_SUBREADING",
        rationale="celestiales Rechen- und Tabellenregister",
    ),
    Rule(
        "CHD_BIO_TREAT", 180, "CHD", ("BIOLOGICAL",),
        working_default_de="Behandle",
        concrete_sense_de="Stationsansatz oder Anwendung behandeln",
        reading_tier="REGISTER_SUBREADING",
        rationale="biologischer Behandlungsrahmen",
    ),
    Rule(
        "CHD_HP_DRY_GRIND", 190, "CHD", HP,
        host_any=("Y", "AIN", "OR", "LOCAL_CHAR_F"),
        host_none=("AIIN",),
        working_default_de="Zerreibe",
        concrete_sense_de="feste Pflanzen- oder Drogencharge zerreiben",
        reading_tier="OBJECT_STATE_SUBREADING",
        rationale="Feststoffsignal ohne Flüssigkeitsmaß im vollständigen CHD-Host",
    ),
    Rule(
        "CHD_REST_PROCESS", 199, "CHD", REGISTER_ORDER,
        working_default_de="Bearbeite",
        concrete_sense_de="Arbeitsgut oder Ansatz bearbeiten",
        reading_tier="HONEST_BROAD_FALLBACK",
        rationale="kein trockener Materialhost oder registereigene Speziallesung",
    ),

    # S: remote governed arguments are admitted; the isolated Biological
    # S→CHD carrier remains selection, not a forced physical grind sequence.
    Rule(
        "S_BIO_CHD_CARRIER_SELECT", 200, "S", ("BIOLOGICAL",),
        source_ids=("G407-E1883",),
        working_default_de="Wähle aus",
        concrete_sense_de="Stationsansatz auswählen",
        reading_tier="OBSERVED_PAIR_CARRIER",
        rationale="einziger vollständiger S→CHD-Träger; keine Seih-Zerreib-Gleichung",
    ),
    Rule(
        "S_CELESTIAL_SELECT", 210, "S", ("CELESTIAL",),
        working_default_de="Wähle aus",
        concrete_sense_de="Sektor, Position oder Tabellenwert auswählen",
        reading_tier="REGISTER_SUBREADING",
        rationale="celestiales Auswahlregister",
    ),
    Rule(
        "S_BIO_DIVERT", 220, "S", ("BIOLOGICAL",),
        host_any=("AL", "AR", "L", "AIR"),
        working_default_de="Leite um",
        concrete_sense_de="Fluss oder Anwendung zwischen Stationen umleiten",
        reading_tier="RELATION_HOST_SUBREADING",
        rationale="Ziel-, Quellen-, Kontakt- oder Wegrelation im vollständigen S-Host",
    ),
    Rule(
        "S_HP_STRAIN", 230, "S", HP,
        host_any=("AIIN",),
        working_default_de="Seihe ab",
        concrete_sense_de="Auszug oder abgemessene Flüssigkeit abseihen",
        reading_tier="REMOTE_OBJECT_SUBREADING",
        rationale="AIIN im vollständigen GDT581-S-Host",
    ),
    Rule(
        "S_HP_SIEVE", 240, "S", HP,
        host_any=("AIN", "OR", "LOCAL_CHAR_F"),
        working_default_de="Siebe",
        concrete_sense_de="Portion, Einheit oder Feinform sieben",
        reading_tier="OBJECT_FORM_SUBREADING",
        rationale="Portions-, Einheits- oder Feinformsignal im S-Host",
    ),
    Rule(
        "S_HP_SEPARATE", 250, "S", HP,
        host_any=("Y",),
        working_default_de="Trenne ab",
        concrete_sense_de="Pflanzen- oder Drogencharge abtrennen",
        reading_tier="OBJECT_SUBREADING",
        rationale="Charge als sichtbares S-Argument",
    ),
    Rule(
        "S_SOURCE_SORT_OUT", 260, "S", ("SOURCE_SECTION_T",),
        working_default_de="Sondere aus",
        concrete_sense_de="Arbeitsgut oder Wert aussondern",
        reading_tier="REGISTER_SUBREADING",
        rationale="Source-Aussonder-Verbrahmen",
    ),
    Rule(
        "S_REST_SELECT", 269, "S", REGISTER_ORDER,
        working_default_de="Wähle aus",
        concrete_sense_de="Material, Station oder Arbeitsschritt auswählen",
        reading_tier="HONEST_BROAD_FALLBACK",
        rationale="kein hinreichender Trenn-, Sieb- oder Umleitungsanker",
    ),
)


def select_rule(**context: object) -> Rule:
    matches = [rule for rule in RULES if rule.matches(**context)]
    if not matches:
        raise RuntimeError(f"No GDT583 rule for context: {context}")
    return min(matches, key=lambda rule: (rule.priority, rule.rule_id))
