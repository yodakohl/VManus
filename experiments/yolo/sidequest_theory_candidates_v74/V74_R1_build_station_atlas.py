#!/usr/bin/env python3
"""Build the complete V74 R1 Biological local-station atlas edition."""

from __future__ import annotations

import csv
import json
import re
from collections import Counter, OrderedDict, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
V69 = ROOT / "experiments/yolo/sidequest_theory_candidates_v69"
V70 = ROOT / "experiments/yolo/sidequest_theory_candidates_v70"
V71 = ROOT / "experiments/yolo/sidequest_theory_candidates_v71"
V72 = ROOT / "experiments/yolo/sidequest_theory_candidates_v72"
OUT = Path(__file__).resolve().parent

CARD_PATH = V69 / "V69_R4_FINAL_173_CARD_DICTIONARY.tsv"
EVENT_PATH = V69 / "V69_R4_FINAL_381_PROSE_EVENT_INTERLINEAR.tsv"
FIELD_PATH = V69 / "V69_R4_FINAL_135_FIELD_EDITION.tsv"
IMAGE_PATH = V70 / "V70_SELECTED_TEN_PAGE_IMAGE_REVISION.tsv"
OWNER_PATH = V71 / "V71_SELECTED_OWNER_LEDGER.tsv"
STATEMENT_PATH = V72 / "V72_SELECTED_116_STATEMENTS.tsv"

EVENT_OUT = OUT / "V74_R1_281_EVENT_INTERLINEAR.tsv"
FIELD_OUT = OUT / "V74_R1_115_FIELD_EDITION.tsv"
STATEMENT_OUT = OUT / "V74_R1_97_STATEMENT_EDITION.tsv"
CONTINUOUS_OUT = OUT / "V74_R1_SIX_RECORD_CONTINUOUS_EDITION.md"

BIO_PAGES = {"f81v", "f82r", "f83r"}


# Frozen completion of all 92 distinct, already exposed V69 Bio exemplar
# phrases.  Every value is local to the current V71 station owner.  Even when
# the source phrase mentions a run or outlet, it licenses no inter-station or
# page-global direction.
PHRASE_MAP = {
    "den aktiven Posten nach der örtlichen Vorschrift bemessen": "Bemesse den aktiven Bade- oder Waschposten nach der örtlichen Vorschrift.",
    "den recordlokalen aktiven Posten im Arbeitsgang fortführen": "Führe den aktiven Posten ausschließlich innerhalb dieses Records weiter.",
    "den aktiven Posten an der örtlich bezeichneten Station führen": "Führe den aktiven Posten an die örtlich bezeichnete Stelle innerhalb derselben Bildstation.",
    "lasse es bis zur Bereitschaft stehen und beende den Schritt": "Lasse den lokalen Posten bis zum bezeichneten Bereitschaftszustand stehen und beende den Schritt.",
    "rühre, bis alles gleichmäßig vermischt ist": "Rühre den lokalen Bade- oder Waschposten, bis er gleichmäßig vermischt ist.",
    "Diese aktive Portion": "Verwende nun diese aktive Bade- oder Waschportion.",
    "die bezeichnete Stelle oder den Lauf mit der aktiven Waschflotte spülen": "Spüle die bezeichnete Stelle oder den lokalen Lauf mit der aktiven Waschflotte.",
    "die verbrauchte Flüssigkeit zum Auffang- oder Auslassbereich abführen": "Lasse die verbrauchte Flüssigkeit in den örtlichen Auffang- oder Auslassbereich ab.",
    "gib einen abgemessenen Anteil in das Gefäß": "Gib einen abgemessenen Anteil in das örtlich bezeichnete Gefäß.",
    "die Charge für den vorgesehenen Gebrauch temperieren": "Temperiere die Charge für den vorgesehenen örtlichen Gebrauch.",
    "den örtlichen Prüfzustand der Charge feststellen": "Prüfe den örtlich vorgeschriebenen Zustand der Charge.",
    "lasse die Badende im temperierten Teilbad sitzen und beende den Schritt": "Lasse die badende Person im temperierten Teilbad sitzen und beende den örtlichen Schritt.",
    "das untere Becken": "Verwende das im Exemplar bezeichnete untere Becken dieser lokalen Szene.",
    "der vorbereitete Bade- oder Waschzusatz": "Verwende den vorbereiteten Bade- oder Waschzusatz.",
    "durch die verbundenen Läufe": "Führe die Flüssigkeit nur durch die innerhalb dieser Station verbundenen Läufe.",
    "spüle das benutzte Gefäß oder den Lauf einmal aus und beende den Schritt": "Spüle das benutzte Gefäß oder den lokalen Lauf einmal aus und beende den Schritt.",
    "fülle danach das Gefäß": "Fülle danach das örtlich bezeichnete Gefäß.",
    "die erste Öffnung": "Verwende die erste, im Exemplar bezeichnete Öffnung dieser Station.",
    "ziehe es ab und beende den Schritt": "Ziehe die örtliche Flüssigkeitsportion ab und beende den Schritt.",
    "Daraus, aus demselben Ansatz": "Nimm den nächsten Anteil aus demselben recordlokalen Ansatz.",
    "ein abgemessener Anteil": "Nimm einen abgemessenen Anteil des lokalen Postens.",
    "stelle die Mischung im bedeckten Auffanggefäß beiseite und beende den Schritt": "Stelle die Mischung im bedeckten örtlichen Auffanggefäß beiseite und beende den Schritt.",
    "erwärme es einmal und beende den Schritt": "Erwärme den lokalen Posten einmal und beende den Schritt.",
    "bei sanfter Wärme": "Halte die lokale Charge bei sanfter Wärme.",
    "beginne die Spülung": "Beginne die Spülung an dieser lokalen Station.",
    "warmes Wasser": "Verwende warmes Wasser für diesen örtlichen Posten.",
    "lasse die Flüssigkeit sich setzen und beende den Schritt": "Lasse die örtliche Flüssigkeit sich setzen und beende den Schritt.",
    "seihe es einmal durch ein Tuch und beende den Schritt": "Seihe den lokalen Posten einmal durch ein Tuch und beende den Schritt.",
    "durch ein Tuch": "Führe den lokalen Posten durch ein Tuch.",
    "unter derselben Einstellung": "Behalte für diesen örtlichen Schritt dieselbe Einstellung bei.",
    "das breite Gefäß": "Verwende das breite Gefäß dieser lokalen Station.",
    "über der örtlich bezeichneten Stelle": "Halte oder verwende den Posten über der örtlich bezeichneten Stelle.",
    "für dieselbe Dauer wie zuvor": "Halte den lokalen Posten für dieselbe recordlokale Dauer wie zuvor.",
    "gieße das erwärmte Wasser ein": "Gieße das erwärmte Wasser in das örtlich bezeichnete Gefäß oder Teilbad.",
    "mische zu gleichen Teilen und beende den Schritt": "Mische die örtlichen Anteile zu gleichen Teilen und beende den Schritt.",
    "zum unteren Ablauf hin": "Führe die Charge innerhalb dieser Station zum bezeichneten unteren Ablauf.",
    "wasche oder bade den bezeichneten Körper- oder Beckenbereich und beende den Schritt": "Wasche oder bade den bezeichneten Körper- oder Beckenbereich und beende den lokalen Schritt.",
    "die Waschflotte am bezeichneten Körper- oder Beckenbereich gebrauchen": "Gebrauche die Waschflotte am bezeichneten Körper- oder Beckenbereich dieser Station.",
    "halte es warm und beende den Schritt": "Halte den örtlichen Posten warm und beende den Schritt.",
    "und lasse es abkühlen": "Lasse den örtlichen Posten anschließend abkühlen.",
    "wasche einmal und beende diesen Durchgang": "Wasche den bezeichneten Bereich einmal und beende diesen örtlichen Durchgang.",
    "lasse es abkühlen und beende den Schritt": "Lasse den örtlichen Posten abkühlen und beende den Schritt.",
    "seihe es klar und beende den Schritt": "Seihe den örtlichen Posten klar und beende den Schritt.",
    "wende es an der markierten Stelle an": "Wende den aktiven Posten an der örtlich markierten Stelle an.",
    "bis es klar ist": "Führe den örtlichen Schritt fort, bis der bezeichnete Klarzustand erreicht ist.",
    "die zweite Öffnung": "Verwende die zweite, im Exemplar bezeichnete Öffnung dieser Station.",
    "die Badeflüssigkeit am bezeichneten Körper- oder Teilbadbereich gebrauchen": "Gebrauche die Badeflüssigkeit am bezeichneten Körper- oder Teilbadbereich.",
    "ziehe die klare Flüssigkeit ab": "Ziehe die klare örtliche Flüssigkeit ab.",
    "schließe den unteren Ablauf": "Schließe den bezeichneten unteren Ablauf dieser Station.",
    "lege ein warmes Tuch auf die bezeichnete äußere Stelle und beende den Schritt": "Lege ein warmes Tuch auf die bezeichnete äußere Stelle und beende den örtlichen Schritt.",
    "lasse es bis zur Klarheit ziehen und beende den Schritt": "Lasse den örtlichen Posten bis zum bezeichneten Klarzustand ziehen und beende den Schritt.",
    "öffne danach den oberen Lauf": "Öffne danach den innerhalb dieser Station bezeichneten oberen Lauf.",
    "erwärme den Bade- oder Waschzusatz sanft und beende den Arbeitsschritt": "Erwärme den Bade- oder Waschzusatz sanft und beende den örtlichen Arbeitsschritt.",
    "für einen Zeitabschnitt": "Halte den örtlichen Posten für den im Exemplar bestimmten Zeitabschnitt.",
    "richte die bezeichnete Beckenstation ein": "Richte die bezeichnete lokale Beckenstation ein.",
    "tauche das Tuch oder die Auflage in die temperierte Flüssigkeit und beende den Schritt": "Tauche das Tuch oder die Auflage in die temperierte Flüssigkeit und beende den örtlichen Schritt.",
    "der zurücklaufende Strom": "Verwende den im Exemplar als lokal zurücklaufend bezeichneten Strom nur innerhalb dieser Station.",
    "bevor es abkühlt": "Führe den örtlichen Gebrauch aus, bevor der Posten abkühlt.",
    "den vorigen recordlokalen Posten wieder aufnehmen": "Nimm den vorigen Posten innerhalb dieses Records wieder auf.",
    "eine mäßige Menge": "Nimm eine mäßige, im Exemplar bestimmte Menge.",
    "der eingetauchte Teil": "Behandle den im Exemplar bezeichneten eingetauchten Teil.",
    "die Badecharge am vorgesehenen Waschplatz gebrauchen": "Gebrauche die Badecharge am vorgesehenen örtlichen Waschplatz.",
    "die betroffene Stelle": "Behandle die im Exemplar bezeichnete betroffene Stelle.",
    "benutze danach den unteren Ablauf": "Benutze danach nur den unteren Ablauf dieser lokalen Station.",
    "und gehe zum nächsten Becken weiter": "Beende den Schritt an dieser Station; beginne ein nächstes Becken erst nach einem neuen Besitzeransatz.",
    "fahre am zweiten Lauf fort": "Fahre am zweiten, innerhalb dieser Station bezeichneten Lauf fort.",
    "gib sauberes Wasser hinzu und beende den Schritt": "Gib sauberes Wasser in diese lokale Station und beende den Schritt.",
    "der benetzte Körperbereich": "Behandle den im Exemplar bezeichneten benetzten Körperbereich.",
    "benetze den bezeichneten Körperbereich vollständig und beende den Schritt": "Benetze den bezeichneten Körperbereich vollständig und beende den örtlichen Schritt.",
    "kühles Wasser": "Verwende kühles Wasser für diesen örtlichen Posten.",
    "zu gleichen Anteilen": "Teile oder mische den örtlichen Posten zu gleichen Anteilen.",
    "wiederhole es an der zweiten Öffnung und beende den Schritt": "Wiederhole den örtlichen Gebrauch an der zweiten Öffnung und beende den Schritt.",
    "verwende den Anteil als örtliche Waschung und beende den Schritt": "Verwende den Anteil als örtliche Waschung und beende den Schritt.",
    "benetze den bezeichneten Bereich vollständig und beende den Schritt": "Benetze den bezeichneten Bereich vollständig und beende den örtlichen Schritt.",
    "wasche einmal und beende den Schritt": "Wasche den bezeichneten Bereich einmal und beende den örtlichen Schritt.",
    "behalte den Rückstand und beende den Schritt": "Behalte den örtlichen Rückstand und beende den Schritt.",
    "nach dem Absetzen": "Führe den örtlichen Schritt nach dem Absetzen der Charge aus.",
    "bis der Strom klar wird": "Führe den lokalen Lauf fort, bis der im Exemplar bezeichnete Klarzustand erreicht ist.",
    "nach der ersten Spülung": "Führe den nächsten örtlichen Schritt nach der ersten Spülung aus.",
    "Gleichmäßig bearbeiten": "Bearbeite den örtlichen Posten gleichmäßig.",
    "einen recordlokalen Anteil auswählen": "Wähle einen Anteil ausschließlich innerhalb dieses Records aus.",
    "den gefilterten Waschposten an der äußeren Haut- oder Wundstelle gebrauchen": "Gebrauche den gefilterten Waschposten an der bezeichneten äußeren Haut- oder Wundstelle.",
    "lege das warme Tuch auf die äußere Haut- oder Wundstelle und beende den Schritt": "Lege das warme Tuch auf die äußere Haut- oder Wundstelle und beende den örtlichen Schritt.",
    "solange es noch warm ist": "Gebrauche oder halte den örtlichen Posten, solange er noch warm ist.",
    "wasche zweimal und beende den Schritt": "Wasche den bezeichneten Bereich zweimal und beende den örtlichen Schritt.",
    "lasse die Mischung einlaufen": "Lasse die Mischung in das örtlich bezeichnete Gefäß oder Teilbad einlaufen.",
    "gebrauche sie sofort und beende den Schritt": "Gebrauche die aktive Portion sofort und beende den örtlichen Schritt.",
    "für die angegebene Dauer": "Halte den örtlichen Posten für die im Exemplar angegebene Dauer.",
    "bis es warm ist": "Führe den örtlichen Schritt fort, bis der Posten warm ist.",
    "mit der vorigen Mischung": "Verwende die vorige Mischung ausschließlich innerhalb dieses Records.",
    "ohne Kochen": "Führe den örtlichen Schritt ohne Kochen aus.",
    "an der bezeichneten Stelle": "Gebrauche die aktive Portion an der örtlich bezeichneten Stelle.",
}


STATION_READINGS = {
    "B1_SHARED_TWO_ROW_POOL": (
        "gemeinsames zweireihiges Bad-/Waschfeld mit wiederholten lokalen Anwendungen",
        "ein gemeinsames Becken mit Füllen, Temperieren, Spülen und Reinigen",
        "zwei gereihte Figurenregister oder ein allegorisches Feld ohne Betriebssemantik"),
    "B2_UPPER_PAIRED_BASINS_AND_CYLINDER": (
        "gekoppelte obere Teilbäder mit örtlichem Temperieren und Anwendungswechsel",
        "zwei lokale Gefäße samt Mittelzylinder für Füllen, Halten und Entleeren",
        "mehrere nur benachbarte Vignetten ohne gemeinsame Bedienung"),
    "B2_MIDDLE_LEFT_DEVICE_AND_INLINE_NODE": (
        "örtliche Wasch-/Applikationsstation an Ring, Fächer und Inline-Knoten",
        "kleines örtliches Verteil- oder Spülgerät",
        "ikonographischer Strahl oder Stern an einem Schmuckband"),
    "B2_MIDDLE_RIGHT_AMBIGUOUS_STATION": (
        "mögliche Liege- oder Teilbadstation, deren Zuordnung das Exemplar bestimmt",
        "möglicher Inline-Knoten oder unabhängiges Podest",
        "bildlich unaufgelöster Zwischenposten ohne sicher bestimmbare Funktion"),
    "B2_LOWER_GREEN_MULTI_FIGURE_POOL": (
        "gemeinsames unteres Mehrpersonenbad mit lokalen Benetzungs- und Halteschritten",
        "großes unteres Becken für Füllen, Temperieren und Ablassen",
        "mehrere allegorische Figurenplätze ohne behauptete Badfunktion"),
    "B2_LOWER_POOL_EDGE_STATIONS": (
        "mehrere lokale Wasch-, Tuch- oder Teilbadplätze am Beckenrand",
        "Randposten eines größeren Beckens für portionsweise Bedienung",
        "das ganze grüne Feld als ein Besitzer oder bloße Figurenornamentik"),
    "B3_UPPER_MARGIN_OPEN_FAN_STATION": (
        "örtliche Benetzungs-/Auslassstation am offenen Fächerende",
        "kleiner Einlass-, Auslass- oder Spülposten",
        "rein ikonographischer Strahlenbesitzer"),
    "B3_MIDDLE_MARGIN_ROUND_VESSEL_STATION": (
        "Einpersonen-Teilbad oder Waschstation im runden Gefäß",
        "kleines rundes Becken für Füllen, Mischen und Ablassen",
        "Teil eines dreifachen Randstapels ohne eigenständige Betriebsfunktion"),
    "B3_LOWER_MARGIN_BASKET_VESSEL_STATION": (
        "örtliche Anwendung oder Teilbad im korbartigen Gefäß",
        "unterer Gefäßposten für Filtern, Halten und Auslassen",
        "Teil des dreifachen Randstapels oder symbolischer Korb"),
    "B3_MARGIN_TO_MAIN_GAP_UNRESOLVED": (
        "nur exemplarisch zuweisbarer Bade-/Waschposten zwischen Rand und Hauptpaar",
        "nur exemplarisch zuweisbarer Übergabe- oder Wartungsposten",
        "unaufgelöster Bildzwischenraum; weder Rand- noch Hauptstation erbt sicher"),
    "B3_MAIN_ARCH_LINKED_PAIR": (
        "sichtbar gekoppeltes Paar lokaler Bade-/Anwendungsstationen unter einem ungerichteten Bogen",
        "gekoppeltes Beckenpaar mit lokalem, aber ungerichtetem Austausch",
        "Regenbogen- oder Himmelsband ohne technische Kopplung"),
    "B4_MAIN_ARCH_LINKED_PAIR": (
        "gemeinsame Paarstation für Tuch-, Wasch- und Temperieranwendungen",
        "gekoppeltes Beckenpaar für Filtern, Spülen und Ablassen",
        "zwei getrennte Figuren mit dekorativem Bogen"),
    "B4_MAIN_LEFT_OPEN_FRINGE_STATION": (
        "linker örtlicher Wasch-/Auslassposten am offenen Fransenende",
        "linker Beckenrand- oder Ablaufposten",
        "ornamentaler Schweif statt Auslass"),
    "B4_MAIN_RIGHT_S_RUN_MULTIPORT_STATION": (
        "rechter örtlicher Verteil-/Anwendungsposten am S-Lauf und Mehrarmknoten",
        "rechter Mehrport-Bedienposten ohne bekannte Flussrichtung",
        "Band- oder Rosettenornament ohne technische Funktion"),
    "B5_LEFT_OPEN_FRINGE_STATION": (
        "eigenständiger linker Endposten für Abziehen, Erwärmen und örtliche Übergabe",
        "linker Bedien- oder Ablaufposten",
        "die gesamte Paarstation statt eines eigenständigen linken Postens"),
    "B6_RIGHT_S_RUN_MULTIPORT_STATION": (
        "eigenständiger rechter Filter-/Anwendungsposten am S-Lauf und Mehrarmknoten",
        "rechter Mehrport- oder Filterposten",
        "die gesamte Paarstation oder ein ornamentaler Knoten"),
}


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: list[dict[str, object]], fields: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t",
                                lineterminator="\n", extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def unique(items: list[str]) -> list[str]:
    out, seen = [], set()
    for item in items:
        if item and item not in seen:
            seen.add(item); out.append(item)
    return out


def exemplar_phrase(event: dict[str, str]) -> str:
    vals = re.findall(r"\[EXEMPLAR:([^\]]+)\]", event["iatromedical_source_segment"])
    if not vals:
        raise ValueError(f"Bio event {event['event_serial']} has no exemplar phrase")
    value = re.sub(r"^A\d+(?:\+A\d+)*:", "", vals[-1]).strip()
    value = re.sub(r"\s+", " ", value)
    return value


def source_layer(event: dict[str, str]) -> str:
    card = event["selected_exact_mnemonic"] not in {"", "NONE", "UNKNOWN"}
    formal = event["strict_formal_prompt"] not in {"", "NONE", "UNKNOWN"}
    if card and formal: return "KNOWN_CARD_AND_FORMAL_WITH_EXEMPLAR_FILL"
    if card: return "KNOWN_CARD_WITH_EXEMPLAR_FILL"
    if formal: return "KNOWN_FORMAL_WITH_EXEMPLAR_FILL"
    if event["terminal_status"] == "TERMINAL": return "FORMAL_CLOSURE_MARKER_WITH_EXEMPLAR_FILL"
    return "EXEMPLAR_ONLY"


def literal_layer(event: dict[str, str], card: dict[str, str]) -> str:
    mnemonic = event["selected_exact_mnemonic"]
    prompt = event["strict_formal_prompt"]
    return " | ".join([
        f"EXACT_CARD_ID={event['joint_tuple_id']}",
        f"SURFACE_DISPLAY_ONLY={event['surface_display_only']}",
        f"OPAQUE_FORMULA={event['formal_formula_opaque']}",
        f"KNOWN_CARD={mnemonic if mnemonic not in {'', 'NONE', 'UNKNOWN'} else 'NONE'}",
        f"KNOWN_FORMAL={prompt if prompt not in {'', 'NONE', 'UNKNOWN'} else 'NONE'}",
        f"TERMINAL={event['terminal_status']}",
        f"V69_CONTROL_CLASS={card['V69_FINAL_CONTROL_CLASS']}",
    ])


APPARATUS_PATTERNS = [
    r"Grundbecken A mit Wärmestelle W1, Rinne R1 und Rücklauf R0",
    r"Teilbecken B mit Zugängen Z1-Z3, Wärmestelle W2, Filter F2 und Auslass A2",
    r"Hauptbecken C mit Vorwärmer W3, Leitungen L1-L4, Filter F3, Unterlauf U3 und Rücklauf R3",
    r"Nachklärbecken D mit Warmzulauf W4, Filtertuch F4, Unterlauf U4 und Rückleitung R4",
    r"Übergabebecken E mit Wärmeschale W5 und Leitung L5",
    r"Kaltbecken F mit einfacher Filteröffnung F6 und Zielstation Z6",
]


def bathhouse_rival(event: dict[str, str], owner: str) -> str:
    source = event["practical_source_segment"]
    values = []
    for tag in ("LOCAL_EXEMPLAR", "LOCAL", "LOCAL_ARGUMENT"):
        values = re.findall(r"\b" + tag + r"\[([^\]]+)\]", source)
        if values: break
    value = values[-1] if values else source
    value = re.sub(r";?\s*keine Kartenbedeutung", "", value, flags=re.I)
    for pattern in APPARATUS_PATTERNS:
        value = re.sub(pattern, "dieser lokalen Station", value)
    value = re.sub(r"\s+", " ", value).strip(" ;.")
    return f"Badehausbetrieb an [{owner}]: {value}."


def direction_status(raw: str) -> str:
    words = ("lauf", "strom", "öffnung", "ablauf", "abführen", "becken weiter", "station führen")
    return "LOCAL_EXEMPLAR_DIRECTION_ONLY" if any(x in raw.lower() for x in words) else "NO_DIRECTION_ASSERTED"


def confidence(event: dict[str, str], owner_row: dict[str, str], raw: str) -> tuple[str, str]:
    score = 0.60 if event["parse_status"] != "UNPARSED_EXEMPLAR" else 0.40
    score += {"DIRECT_VISIBLE": 0.08, "INHERITED_VISIBLE": 0.02,
              "PAGE_OWNER_ONLY": 0.03, "UNRESOLVED": -0.14}[owner_row["owner_status"]]
    if direction_status(raw) == "LOCAL_EXEMPLAR_DIRECTION_ONLY": score -= 0.04
    score = max(0.24, min(0.70, round(score, 2)))
    label = "MEDIUM_HIGH_INTERNAL" if score >= 0.62 else "MEDIUM_INTERNAL" if score >= 0.48 else "LOW_MEDIUM_INTERNAL" if score >= 0.34 else "LOW_INTERNAL"
    return f"{score:.2f}", label


def contradiction(event: dict[str, str], owner_row: dict[str, str], raw: str) -> str:
    notes = ["Stoff, Heilindikation und konkrete Handlung stammen aus dem Masterexemplar, nicht aus der Bildkontur"]
    if owner_row["owner_status"] == "UNRESOLVED":
        notes.append("selbst der lokale Besitzer ist an dieser Lücke nur exemplarisch entscheidbar")
    if direction_status(raw) == "LOCAL_EXEMPLAR_DIRECTION_ONLY":
        notes.append("jede Richtung gilt nur innerhalb dieser Station; Pfeil und globaler Seitenfluss fehlen")
    card = event["selected_exact_mnemonic"]
    prompt = event["strict_formal_prompt"]
    if card not in {"", "NONE", "UNKNOWN"}:
        notes.append(f"{card} bleibt ein unsicherer Ganzkarten-Merksatz, keine Wortbedeutung")
    if prompt not in {"", "NONE", "UNKNOWN"}:
        notes.append(f"{prompt} bleibt eine formale Slotanweisung, keine Übersetzung")
    if event["terminal_status"] == "TERMINAL":
        notes.append("der Schlussmarker stützt nur den Feldabschluss")
    return "; ".join(notes) + "."


def field_transition(fields: list[dict[str, str]], owner_by_field: dict[str, dict[str, str]]) -> dict[str, str]:
    result, prior_by_record = {}, {}
    for field in fields:
        fid, rec = field["field_id"], field["record_unit_id"]
        row, owner = owner_by_field[fid], owner_by_field[fid]["selected_visible_owner"]
        prior = prior_by_record.get(rec)
        if row["owner_status"] == "UNRESOLVED":
            mode = "MASTER_EXEMPLAR_OWNER_LOOKUP" if prior == owner else "RESET_AT_V71_GAP_AND_MASTER_EXEMPLAR_OWNER_LOOKUP"
        elif prior is None:
            mode = "RESET_AT_RECORD_START"
        elif prior == owner:
            mode = "CARRY_WITHIN_LOCAL_STATION"
        else:
            mode = "RESET_AT_V71_SCENE_GAP"
        result[fid] = mode
        prior_by_record[rec] = owner
    return result


def owner_clause_prefix(owner_row: dict[str, str], transition: str) -> str:
    owner, desc = owner_row["selected_visible_owner"], owner_row["silent_argument_default"]
    if "MASTER_EXEMPLAR" in transition:
        return f"Am nur durch das Masterexemplar zuweisbaren örtlichen Posten [{owner}] ({desc})"
    if transition.startswith("CARRY"):
        return f"An derselben lokalen Station [{owner}]"
    return f"Setze den lokalen Besitzer [{owner}] ({desc})"


def build() -> None:
    cards = read_tsv(CARD_PATH)
    events_all = read_tsv(EVENT_PATH)
    fields_all = read_tsv(FIELD_PATH)
    images = read_tsv(IMAGE_PATH)
    owners_all = read_tsv(OWNER_PATH)
    statements_all = read_tsv(STATEMENT_PATH)
    events = [r for r in events_all if r["page"] in BIO_PAGES]
    fields = [r for r in fields_all if r["page"] in BIO_PAGES]
    owners = [r for r in owners_all if r["unit_kind"] == "PROSE_FIELD" and r["page"] in BIO_PAGES]
    statements = [r for r in statements_all if r["page"] in BIO_PAGES]
    card_by_id = {r["joint_tuple_id"]: r for r in cards}
    owner_by_field = {r["unit_id"]: r for r in owners}
    statement_by_id = {r["statement_id"]: r for r in statements}
    transition_by_field = field_transition(fields, owner_by_field)
    events_by_field = defaultdict(list)
    for event in events: events_by_field[event["field_id"]].append(event)

    observed_phrases = {exemplar_phrase(event) for event in events}
    missing = observed_phrases - set(PHRASE_MAP)
    extra = set(PHRASE_MAP) - observed_phrases
    if missing or extra:
        raise ValueError(f"phrase-map mismatch missing={sorted(missing)} extra={sorted(extra)}")

    event_rows = []
    first_event_in_field = {fid: min(int(e["event_serial"]) for e in ev) for fid, ev in events_by_field.items()}
    for index, event in enumerate(events, 1):
        fid = event["field_id"]
        owner_row = owner_by_field[fid]
        owner = owner_row["selected_visible_owner"]
        raw = exemplar_phrase(event)
        default = PHRASE_MAP[raw]
        score, label = confidence(event, owner_row, raw)
        transition = transition_by_field[fid] if int(event["event_serial"]) == first_event_in_field[fid] else "SAME_FIELD_OWNER"
        medical, bath_station, formal_station = STATION_READINGS[owner]
        iconographic = f"Ikonographisch/formal an [{owner}]: {formal_station}; die exakte Karte kann nur einen lokalen Konstruktionsplatz füllen."
        event_rows.append({
            "bio_event_row": index, "event_serial": event["event_serial"],
            "page": event["page"], "locus": event["locus"], "record_unit_id": event["record_unit_id"],
            "field_id": fid, "statement_id": event["statement_id"],
            "exact_card_id": event["joint_tuple_id"], "surface_display_only": event["surface_display_only"],
            "literal_exact_card_layer": literal_layer(event, card_by_id[event["joint_tuple_id"]]),
            "v71_local_owner": owner, "owner_status": owner_row["owner_status"],
            "owner_transition": transition, "visible_contact_basis": owner_row["visible_basis"],
            "concrete_german_default": default, "source_layer": source_layer(event),
            "parse_status": event["parse_status"], "working_confidence": score,
            "confidence_label": label, "confidence_scope": "INTERNAL_STATION_ATLAS_COHERENCE_NOT_DECIPHERMENT_PROBABILITY",
            "medical_application_reading": f"Medizinische Anwendung an [{owner}]: {default}",
            "bathhouse_operation_rival": bathhouse_rival(event, owner),
            "iconographic_formal_rival": iconographic,
            "station_medical_model": medical, "station_bathhouse_model": bath_station,
            "strongest_rival": bathhouse_rival(event, owner) if owner_row["owner_status"] != "UNRESOLVED" else iconographic,
            "local_direction_status": direction_status(raw), "global_flow_claim": "NONE",
            "contradiction": contradiction(event, owner_row, raw),
            "semantic_ceiling": "LOCAL_OCCURRENCE_DEFAULT_NOT_CARD_STEM_SOUND_LANGUAGE_OR_GLOBAL_FLOW_MEANING",
        })

    event_columns = list(event_rows[0])
    write_tsv(EVENT_OUT, event_rows, event_columns)

    out_events_by_field = defaultdict(list)
    for row in event_rows: out_events_by_field[row["field_id"]].append(row)
    field_rows = []
    for index, field in enumerate(fields, 1):
        fid, owner_row = field["field_id"], owner_by_field[field["field_id"]]
        ev = out_events_by_field[fid]
        owner = owner_row["selected_visible_owner"]
        prefix = owner_clause_prefix(owner_row, transition_by_field[fid])
        text = prefix + ": " + " ".join(r["concrete_german_default"] for r in ev)
        medical, bath, formal = STATION_READINGS[owner]
        field_rows.append({
            "bio_field_row": index, "field_id": fid, "record_unit_id": field["record_unit_id"],
            "page": field["page"], "locus": field["locus"], "statement_id": field["statement_id"],
            "event_count": field["event_count"], "event_serials": field["event_serials"],
            "v71_local_owner": owner, "owner_status": owner_row["owner_status"],
            "owner_transition": transition_by_field[fid], "visible_contact_basis": owner_row["visible_basis"],
            "literal_exact_card_sequence": " > ".join(f"E{int(r['event_serial']):03d}:{r['exact_card_id']}" for r in ev),
            "complete_event_default_sequence": " | ".join(f"E{int(r['event_serial']):03d}={r['concrete_german_default']}" for r in ev),
            "readable_field_text": text,
            "source_layer_counts": json.dumps(dict(sorted(Counter(r["source_layer"] for r in ev).items())), ensure_ascii=False),
            "minimum_working_confidence": min(float(r["working_confidence"]) for r in ev),
            "mean_working_confidence": f"{sum(float(r['working_confidence']) for r in ev)/len(ev):.3f}",
            "medical_application_model": medical, "bathhouse_operation_model": bath,
            "iconographic_formal_model": formal,
            "strongest_rival": " ".join(r["strongest_rival"] for r in ev),
            "contradiction": " ".join(unique([r["contradiction"] for r in ev])),
            "global_flow_claim": "NONE",
            "semantic_ceiling": "COMPLETE_LOCAL_FIELD_EXPANSION_NOT_TRANSLATION",
        })
    write_tsv(FIELD_OUT, field_rows, list(field_rows[0]))

    field_out_by_id = {r["field_id"]: r for r in field_rows}
    out_events_by_statement = defaultdict(list)
    for row in event_rows: out_events_by_statement[row["statement_id"]].append(row)
    statement_rows = []
    for index, statement in enumerate(statements, 1):
        fids = statement["constituent_fields"].split("|")
        fr = [field_out_by_id[f] for f in fids]
        ev = out_events_by_statement[statement["statement_id"]]
        owners_in_order = unique([r["v71_local_owner"] for r in fr])
        clauses, prior = [], None
        for row in fr:
            if prior is not None and row["v71_local_owner"] != prior:
                clauses.append("OHNE BILDVERBINDUNG: Setze jetzt einen neuen lokalen Besitzer. " + row["readable_field_text"])
            else:
                clauses.append(row["readable_field_text"])
            prior = row["v71_local_owner"]
        statement_rows.append({
            "bio_statement_row": index, "statement_id": statement["statement_id"],
            "record_unit_id": statement["record_unit_id"], "page": statement["page"],
            "constituent_fields": statement["constituent_fields"], "event_count": statement["event_count"],
            "event_serials": statement["event_serials"],
            "owner_sequence": " > ".join(owners_in_order),
            "internal_owner_reset": "YES" if len(owners_in_order) > 1 else "NO",
            "literal_exact_card_sequence": " > ".join(f"E{int(r['event_serial']):03d}:{r['exact_card_id']}" for r in ev),
            "continuous_local_statement": " ".join(clauses),
            "v72_selected_paraphrase": statement["selected_concrete_paraphrase"],
            "medical_application_reading": " / ".join(unique([r["medical_application_model"] for r in fr])),
            "bathhouse_operation_rival": " / ".join(unique([r["bathhouse_operation_model"] for r in fr])),
            "iconographic_formal_rival": " / ".join(unique([r["iconographic_formal_model"] for r in fr])),
            "repair_cost_0_4": statement["repair_cost_0_4"], "line_crossing": statement["line_crossing"],
            "contradiction": statement["hardest_contradiction"] + " Globaler Fluss bleibt unbehauptet.",
            "global_flow_claim": "NONE",
            "semantic_ceiling": "OWNER_BOUNDED_STATEMENT_EXPANSION_NOT_TRANSLATION",
        })
    write_tsv(STATEMENT_OUT, statement_rows, list(statement_rows[0]))

    # Continuous six-record edition, preserving station resets and exact field order.
    fields_by_record = defaultdict(list)
    for row in field_rows: fields_by_record[row["record_unit_id"]].append(row)
    statements_by_record = defaultdict(list)
    for row in statement_rows: statements_by_record[row["record_unit_id"]].append(row)
    lines = [
        "# V74 R1 — sechs kontinuierliche Biological-Recordfassungen", "",
        "Status: konkrete lokale Stationsatlas-Arbeitstheorie; keine Übersetzung.", "",
        "Die Ausgabe erlaubt exemplarische Richtung nur innerhalb eines aktiven V71-Besitzers. Jeder Besitzerwechsel setzt die Station neu; kein Pfeil, Kreislauf oder globaler Seitenfluss wird ergänzt.", "",
        "## Lehrbare Stationsschablone", "", "```text",
        "RECORD-REGISTER ZURÜCKSETZEN",
        "→ kleinsten sichtbaren lokalen Besitzer setzen",
        "→ exakte Kartenfolge kopieren",
        "→ bekannten Karten-/Formalslot unverändert übernehmen",
        "→ occurrence-spezifische Bade-/Waschhandlung aus dem Masterexemplar einsetzen",
        "→ Richtung höchstens innerhalb der aktuellen Station zulassen",
        "→ bei V71-Lücke Besitzer und Richtung vollständig zurücksetzen",
        "→ CLOSE beendet den Feldposten, nicht notwendig den Record",
        "```", "",
    ]
    for rec in ("B1", "B2", "B3", "B4", "B5", "B6"):
        rr = fields_by_record[rec]
        lines.extend([f"## {rec} — {rr[0]['page']}", "", f"Abdeckung: {len(rr)} Felder, {sum(int(r['event_count']) for r in rr)} Ereignisse, {len(statements_by_record[rec])} Aussagen.", ""])
        prior = None
        for row in rr:
            if row["v71_local_owner"] != prior:
                owner = row["v71_local_owner"]
                medical, bath, formal = STATION_READINGS[owner]
                lines.extend([f"### Station `{owner}`", "", f"Medizinisch: {medical}.  ", f"Badehaus: {bath}.  ", f"Ikonographisch/formal: {formal}.", ""])
            lines.append(row["readable_field_text"] + "\n")
            prior = row["v71_local_owner"]
        lines.extend(["### Recordgrenze", "", "Alle Arbeitsregister und jede lokale Richtungsannahme werden hier zurückgesetzt.", ""])
    lines.extend(["## Rücklesegrenze", "", "Ohne Masterexemplar bleiben nur exakte Kartenfolge, lokale Bildbesitzer, Kontaktgrenzen, bekannte unsichere Kontrollkarten und Feldschlüsse. Stoff, Krankheit, Baderezept, Bedienhandlung und Richtung sind nicht rückgewinnbar.", ""])
    CONTINUOUS_OUT.write_text("\n".join(lines), encoding="utf-8")


if __name__ == "__main__":
    build()
    print(json.dumps({"status": "BUILT", "events": 281, "fields": 115, "statements": 97, "records": 6}, indent=2))

