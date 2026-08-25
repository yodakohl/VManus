#!/usr/bin/env python3
"""Build the Pass-910 three-layer apprentice handbook over fourteen pages.

This is a creative sidequest edition.  It deliberately gives every visible
group a usable workshop default while keeping three different mechanisms
separate: shared components, register-specific expansion, and copied local
names/cards.  Mixed transcription data are materialized only through guarded
page-specific queries.
"""

from __future__ import annotations

import csv
import hashlib
import io
import json
import subprocess
from collections import Counter, defaultdict
from functools import lru_cache
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
BASE = Path(__file__).resolve().parent
SOURCE = ROOT / "transcription/voynich_zl3b_lines.tsv"
PASS908 = ROOT / "experiments/yolo/sidequest_semantic_zero_learned_whole_roots_nine_hundred_eighth"
PASS909 = ROOT / "experiments/yolo/sidequest_semantic_four_page_reality_check_nine_hundred_ninth"

PASS908_CARDS = PASS908 / "NINE_HUNDRED_EIGHTH_231_ZERO_WHOLE_ROOT_CARD_DICTIONARY.tsv"
PASS909_COMPONENTS = PASS909 / "NINE_HUNDRED_NINTH_REVISED_COMPONENTS.tsv"
PASS909_F13 = PASS909 / "F13R_TRANSFER.tsv"
PASS909_F75 = PASS909 / "F75R_TRANSFER.tsv"
PASS909_F70 = PASS909 / "F70V_TRANSFER.tsv"
PASS909_F88 = PASS909 / "F88R_TRANSFER.tsv"

PORTABLE_OUT = BASE / "PASS910_PORTABLE_CORE.tsv"
EXPANSIONS_OUT = BASE / "PASS910_REGISTER_EXPANSIONS.tsv"
NOMENCLATOR_OUT = BASE / "PASS910_LOCAL_NOMENCLATOR.tsv"
DICTIONARY_OUT = BASE / "PASS910_CARD_DICTIONARY.tsv"
EVENTS_OUT = BASE / "PASS910_2511_EVENT_INTERLINEAR.tsv"
LOCI_OUT = BASE / "PASS910_LOCUS_EDITION.tsv"
PAGES_OUT = BASE / "PASS910_FOURTEEN_PAGE_SUMMARY.tsv"
EDITION_OUT = BASE / "PASS910_FOURTEEN_PAGE_EDITION.md"
HANDBOOK_OUT = BASE / "PASS910_MASTER_HANDBOOK.md"
REPORT_OUT = BASE / "PASS910_REPORT.md"
SUMMARY_OUT = BASE / "PASS910_BUILD_SUMMARY.json"


PAGE_SPECS = [
    ("f10r", "f10r", "HERBAL", "abgebildeter Pflanzenartikel f10r"),
    ("f11r", "f11r", "HERBAL", "abgebildeter Pflanzenartikel f11r"),
    ("f13r", "f13r", "HERBAL", "grosse abgebildete Pflanze mit Knollenwurzel"),
    ("f55v", "f55v", "HERBAL", "abgebildeter Pflanzenartikel f55v"),
    ("f56r", "f56r", "HERBAL", "abgebildeter Pflanzenartikel f56r"),
    ("f75r", "f75r", "BIOLOGICAL", "mehrstufige Becken-, Figuren- und Laufseite"),
    ("f81v", "f81v", "BIOLOGICAL", "gemeinsames Bad- und Beckenfeld"),
    ("f82r", "f82r", "BIOLOGICAL", "mehrere lokale Bad- und Leitungsstationen"),
    ("f83r", "f83r", "BIOLOGICAL", "lokale Becken-, Figuren- und Verbindungsstationen"),
    ("f67r2", "f67r2", "ZODIAC", "zwei lokale Himmelsraeder"),
    ("f68r1", "f68r1", "ZODIAC", "mehrteiliger Sternatlas mit lokalen Zentren"),
    ("f69v", "f69v", "ZODIAC", "drei getrennte heterogene Himmelsraeder"),
    ("f70v1", "f70v", "ZODIAC", "Widderrad mit Stern tragenden Figuren"),
    ("f70v2", "f70v", "ZODIAC", "Fischrad mit Stern tragenden Figuren"),
    ("f88r", "f88r", "PHARMA", "drei Gefaesse mit Wurzel- und Blattreihen"),
]

PHYSICAL_PAGE_ORDER = [
    "f10r", "f11r", "f13r", "f55v", "f56r",
    "f75r", "f81v", "f82r", "f83r",
    "f67r2", "f68r1", "f69v", "f70v", "f88r",
]

PAGE_FLUENT = {
    "f10r": (
        "Nimm den bezeichneten Teil der abgebildeten Pflanze, ordne Portion und Sollmass zu und setze den Arbeitsgang an. "
        "Fuehre den Ansatz ueber die angegebenen Teil- und Anschlussstellen weiter, halte oder bearbeite ihn nach Grad und schliesse nur die markierten Teilgaenge."
    ),
    "f11r": (
        "Arbeite aus der abgebildeten Pflanze einen neuen Posten heraus, bemiss ihn und fuehre ihn in den laufenden Ansatz. "
        "Wechsle zwischen Entnahme-, Arbeits- und Aufnahmestelle, lasse die bezeichneten Stufen ablaufen und nimm den vorigen Posten wieder auf, wenn die Karte darauf verweist."
    ),
    "f13r": (
        "Setze einen Teil der grossen abgebildeten Pflanze in den Arbeitsgang, halte den Ansatz und nimm an den bezeichneten Stellen Material ab. "
        "Gib nach Mass zu, bearbeite und fuehre weiter, presse oder leite durch den Durchlass und schliesse den fertigen Teilgang."
    ),
    "f55v": (
        "Waehle den dargestellten Pflanzenstoff, setze Portionen und Mass und fuehre ihn durch die aufeinanderfolgenden Arbeitsstellen. "
        "Halte, wasche, presse oder sammle den Posten je nach Karte; fuehre den Ansatz danach weiter und bearbeite ihn an der Nebenstelle."
    ),
    "f56r": (
        "Nimm jeweils den im Bild oder Muster bezeichneten Pflanzenteil und fuehre ihn in den aktuellen Ansatz. "
        "Arbeite in kurzen und laengeren Graden durch Entnahme-, Anschluss- und Sammelstellen, halte den Posten bereit und schliesse die ausdrücklich markierten Schritte."
    ),
    "f75r": (
        "Fuehre die Posten von der oberen Mehrstufenanlage ueber Aufnahme-, Ausgangs- und Durchlassstellen zur mittleren und unteren Beckenstation. "
        "Setze jede Station kurz oder laenger an, halte und pruefe den Posten, leite ihn weiter und lies die sieben kurzen Beischriften als lokale Stationskennungen."
    ),
    "f81v": (
        "Besetze das gemeinsame Bad- und Beckenfeld mit den bezeichneten Posten und halte sie an ihren lokalen Stellen. "
        "Fuehre Portionen und Sollmasse durch kurze, laengere und geschlossene Stationsschritte; die kleinen Bildkennungen werden als ganze lokale Werte gelesen."
    ),
    "f82r": (
        "Arbeite die sichtbaren Bad-, Becken- und Leitungsstationen nacheinander ab, ohne daraus einen einzigen geschlossenen Kreislauf zu machen. "
        "Nimm Posten an Ausgangsstellen ab, setze sie an Anschlussstellen ein, leite sie durch lokale Verbindungen und uebernimm Bildkennungen und seltene Arbeitskarten aus dem Stationsmuster."
    ),
    "f83r": (
        "Fuehre die Posten durch die lokal verbundenen Becken- und Figurenstationen, wobei jeder Besitzerwechsel einen neuen Stationsbezug setzt. "
        "Halte, versetze, leite und sammle nach Mass und Grad; behandle nicht verbundene Bildteile als getrennte Arbeitsfaecher und kopiere ihre Kennungen ganz."
    ),
    "f67r2": (
        "Lies die beiden Himmelsraeder als getrennte Register: setze Ringstelle, Index, Grad und aktuellen Bezug und gehe dann zur naechsten markierten Stelle. "
        "Die zahlreichen kurzen Beischriften sind gelernte Sektor- oder Figurenkennungen, nicht ausgeschriebene Werkstattverben."
    ),
    "f68r1": (
        "Waehle im mehrteiligen Sternatlas zuerst das lokale Zentrum oder Paneel und lies dann die zugehoerigen Sternstellen. "
        "Mass-, Stufen-, Adress- und Bezugskarten ordnen den Eintrag; die einzelnen Sternnamen oder Klassen bleiben im lokalen Namensfach."
    ),
    "f69v": (
        "Behandle die drei sichtbaren Himmelsraeder als getrennte Instrumente und lies in jedem nur seine eigene Stellen-, Grad- und Bezugsfolge. "
        "Setze keinen gemeinsamen Start, keine feste Drehrichtung und keinen automatischen Schluessel zwischen den Raedern voraus."
    ),
    "f70v": (
        "Im Widder- und Fischrad laeuft dieselbe kurze Ringgrammatik: naechste Stelle, Mass oder Index, Grad, aktueller Bezug und gegebenenfalls Abschluss. "
        "Die Stern tragenden Figuren besitzen lokale Kennungen; ihre konkrete astronomische Rolle wird aus dem Radmuster gelernt und nicht aus einer Pflanzen- oder Badbedeutung der Teilzeichen."
    ),
    "f88r": (
        "Lies zuerst die sechzehn Wurzel- und Blattkennungen bei den drei Zutatenreihen und ordne sie den benachbarten Gefaessen zu. "
        "Nimm dann Portion oder Sollmass, beginne und fuehre den Gefaessansatz weiter, gib die bezeichneten Teile zu, halte oder leite den Auszug und schliesse die markierten Teilgaenge."
    ),
}

VISUAL_LABEL_LOCI = {
    "f75r.47", "f75r.48", "f75r.49", "f75r.50",
    "f75r.51", "f75r.52", "f75r.53",
}

PORTABLE_CORE = [
    "AIIN", "AIN", "AIR", "AL", "AR", "CKH", "DY", "E", "EE",
    "EEE", "IIN", "L", "OL", "OT", "Y",
]

SUPPLEMENTAL_COMPONENTS = {
    "AN": {
        "portable": "NACHGABE ODER ZUSATZ",
        "HERBAL": "weiterer Pflanzenzusatz",
        "BIOLOGICAL": "weiterer Stationsposten",
        "ZODIAC": "weiterer Ringwert",
        "PHARMA": "weitere Zutat",
        "decision": "LOCAL_WORKSHOP_ROOT",
    },
    "A_ADDR": {
        "portable": "LOKALE ADRESSE",
        "HERBAL": "lokale Artikelstelle",
        "BIOLOGICAL": "lokale Station",
        "ZODIAC": "lokale Ringstelle",
        "PHARMA": "lokale Rezeptstelle",
        "decision": "REGISTER_LOCAL_ONLY",
    },
    "D_LABEL": {
        "portable": "LOKALES D-KENNZEICHEN",
        "HERBAL": "lokaler Artikelmarker",
        "BIOLOGICAL": "lokaler Stationsmarker",
        "ZODIAC": "lokaler Phasenmarker",
        "PHARMA": "lokaler Rezeptmarker",
        "decision": "REGISTER_LOCAL_ONLY",
    },
    "OS": {
        "portable": "DAZU ODER AUCH",
        "HERBAL": "dazu",
        "BIOLOGICAL": "auch an dieser Station",
        "ZODIAC": "auch an dieser Stelle",
        "PHARMA": "dazu",
        "decision": "LOCAL_WORKSHOP_ROOT",
    },
    "RESUME_CARD": {
        "portable": "DAVON ODER WIEDERAUFNAHME",
        "HERBAL": "davon weiterarbeiten",
        "BIOLOGICAL": "diesen Stationsposten wiederaufnehmen",
        "ZODIAC": "diesen Bezug wiederaufnehmen",
        "PHARMA": "davon weiterarbeiten",
        "decision": "LOCAL_WORKSHOP_ROOT",
    },
    "G_LABEL": {
        "portable": "LOKALE G-ENDUNG",
        "HERBAL": "lokales Kennzeichen",
        "BIOLOGICAL": "lokales Kennzeichen",
        "ZODIAC": "lokale Figurenkennung",
        "PHARMA": "lokale Zutatenkennung",
        "decision": "LOCAL_SIGN",
    },
    "Z_ADDR": {
        "portable": "LOKALER Z-BEZUG",
        "HERBAL": "lokaler Bezug",
        "BIOLOGICAL": "lokaler Bezug",
        "ZODIAC": "lokaler Ringbezug",
        "PHARMA": "lokaler Bezug",
        "decision": "LOCAL_SIGN",
    },
    "M_LOCAL": {
        "portable": "LOKALES M-ZEICHEN",
        "HERBAL": "lokale Stelle",
        "BIOLOGICAL": "lokale Stelle",
        "ZODIAC": "lokales Innenzeichen",
        "PHARMA": "lokale Zutatenklasse",
        "decision": "LOCAL_SIGN",
    },
    "CARRIER_Q": {
        "portable": "SCHREIBTRAEGER Q",
        "HERBAL": "q-Träger",
        "BIOLOGICAL": "q-Träger",
        "ZODIAC": "q-Träger",
        "PHARMA": "q-Träger",
        "decision": "RENDERER_ONLY",
    },
}


REGISTER_VERBS = {
    "HERBAL": {
        "O": "fuehre den Verarbeitungsgang aus",
        "OK": "setze die Zubereitung an",
        "CH": "nimm den bezeichneten Pflanzenteil",
        "CHD": "setze das Material um",
        "CHK": "behandle den Zustand des Ansatzes",
        "CKH": "fuehre durch den Seih- oder Durchlassweg",
        "CTH": "pruefe den Zubereitungsstatus",
        "K": "gib den bezeichneten Teil hinzu",
        "L": "leite den Posten weiter",
        "LD": "befestige den Posten",
        "LSH": "wasche oder spuele den Teil",
        "P": "setze den Teil ein",
        "R": "setze den markierten Zustand",
        "S": "pruefe oder fahre fort",
        "SH": "halte den Ansatz",
        "SHED": "lasse den Ansatz ruhen",
        "SOLK": "sammle im Gefaess",
        "T": "bearbeite den Teil",
        "CFH": "presse den Teil aus",
        "CHEO": "verwende den Auszug",
        "HO": "verwende den bezeichneten Pflanzenteil",
        "OR": "mit dem Pflanzenansatz",
    },
    "BIOLOGICAL": {
        "O": "fuehre den Stationsgang aus",
        "OK": "aktiviere die Station",
        "CH": "nimm den Stationsposten ab",
        "CHD": "setze den Stationsposten um",
        "CHK": "behandle den Zustand des Postens",
        "CKH": "fuehre durch die Beckenverbindung",
        "CTH": "pruefe den Stationsstatus",
        "K": "setze den Posten ein",
        "L": "verbinde mit der naechsten Station",
        "LD": "befestige den Einsatz",
        "LSH": "spuele die Station",
        "P": "beginne oder besetze die Station",
        "R": "setze den markierten Zustand",
        "S": "pruefe die Station",
        "SH": "halte den Stationsposten",
        "SHED": "halte ihn an der Station",
        "SOLK": "sammle an der Auffangstelle",
        "T": "bediene den Abschnitt",
        "CFH": "fuehre die Press- oder Trennoperation aus",
        "CHEO": "verwende den lokalen Arbeitsinhalt",
        "HO": "verwende den Koerper- oder Anlagenabschnitt",
        "OR": "mit dem Arbeitsansatz",
    },
    "ZODIAC": {
        "O": "lies den Ringgang",
        "OK": "setze die Ringstelle",
        "CH": "lies die Kennung",
        "CHD": "wechsle zur Bezugsstelle",
        "CHK": "setze den Kennungszustand",
        "CKH": "folge dem Ringdurchgang",
        "CTH": "pruefe den Stellenstatus",
        "K": "ordne den Wert zu",
        "L": "verbinde mit der naechsten Stelle",
        "LD": "binde die Kennung an die Stelle",
        "LSH": "markiere den Ringgang",
        "P": "beginne den Eintrag",
        "R": "setze den markierten Zustand",
        "S": "verwende die Stern- oder Phasenkennung",
        "SH": "halte den Bezug",
        "SHED": "halte den Ringstatus",
        "SOLK": "binde an die lokale Sammelstelle",
        "T": "markiere die Stelle",
        "CFH": "verwende die lokale Trennkennung",
        "CHEO": "lies den lokalen Eintrag",
        "HO": "verwende den Figurenteil",
        "OR": "mit dem lokalen Eintrag",
    },
    "PHARMA": {
        "O": "fuehre den Zubereitungsgang aus",
        "OK": "beginne den Ansatz",
        "CH": "nimm die bezeichnete Zutat",
        "CHD": "setze den Ansatz um",
        "CHK": "behandle den Zustand des Ansatzes",
        "CKH": "fuehre durch den Gefaessdurchgang",
        "CTH": "pruefe den Ansatzstatus",
        "K": "gib die Zutat hinzu",
        "L": "leite zum Gefaess",
        "LD": "befestige den Verschluss",
        "LSH": "spuele das Gefaess",
        "P": "setze die Zutat ein",
        "R": "setze den markierten Zustand",
        "S": "und dann",
        "SH": "halte den Ansatz",
        "SHED": "lasse den Ansatz ruhen",
        "SOLK": "sammle im Gefaess",
        "T": "bearbeite die Zutat",
        "CFH": "presse die Zutat ab",
        "CHEO": "verwende den Auszug",
        "HO": "verwende den Zutatenteil",
        "OR": "mit dem Gefaessansatz",
    },
}


COMMON_PHRASES = {
    "AIIN": "nach vorgeschriebenem Mass",
    "AIN": "eine Portion oder Einheit",
    "AIR": "ueber den Lauf oder die Bahn",
    "AL": "an der Aufnahme- oder Anschlussstelle",
    "AR": "von der Ausgangs- oder Entnahmestelle",
    "AN": "mit einer weiteren Zugabe",
    "DA": "auf der markierten zweiten Stufe",
    "DY": "schliesse die Teilfolge",
    "E": "im kurzen Grad",
    "EE": "im laengeren Grad",
    "EEE": "im vollen Grad",
    "IIN": "auf der angegebenen Stufe oder am Index",
    "OL": "fahre fort",
    "OT": "danach oder an der naechsten Stelle",
    "Y": "mit dem aktuellen Posten oder Bezug",
    "A_ADDR": "an der lokalen Adresse",
    "AM_ADDR": "an der lokalen M-Adresse",
    "D_ADDR": "an der Teil- oder Unteradresse",
    "S_ADDR": "an der lokalen S-Adresse",
    "D_LABEL": "mit dem lokalen D-Kennzeichen",
    "S_LABEL": "mit dem lokalen S-Kennzeichen",
    "G_LABEL": "mit der lokalen G-Endung",
    "Z_ADDR": "am lokalen Z-Bezug",
    "M_LOCAL": "mit dem lokalen M-Zeichen",
    "OS": "dazu oder ebenfalls",
    "RESUME_CARD": "nimm den vorigen Posten wieder auf",
}


LOCAL_PREFIX = {"HERBAL": "H", "BIOLOGICAL": "B", "ZODIAC": "Z", "PHARMA": "P"}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: list[dict[str, object]], fields: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def guarded_rows(selector: str) -> list[dict[str, str]]:
    if selector.lower().startswith("f84"):
        raise ValueError("sealed selector requested")
    command = [
        str(ROOT / "vmanus-exp"), "query-tsv", str(SOURCE),
        "--selector", "page", "--allow", selector,
        "--columns", "page,locus,kind,token_count,eva_clean",
        "--forbid-prefix", "f84",
    ]
    completed = subprocess.run(command, cwd=ROOT, check=True, text=True, capture_output=True)
    rows = list(csv.DictReader(io.StringIO(completed.stdout), delimiter="\t"))
    if not rows or {row["page"] for row in rows} != {selector}:
        raise RuntimeError(f"guarded load failed for {selector}")
    return rows


def load_components() -> dict[str, dict[str, str]]:
    result: dict[str, dict[str, str]] = {}
    for row in read_tsv(PASS909_COMPONENTS):
        result[row["component"]] = {
            "portable": row["revised_portable_value_de"],
            "HERBAL": row["herbal_expansion"],
            "BIOLOGICAL": row["biological_expansion"],
            "ZODIAC": row["zodiac_expansion"],
            "PHARMA": row["pharma_expansion"],
            "decision": row["decision"],
        }
    result.update(SUPPLEMENTAL_COMPONENTS)
    return result


def valid_recipe(recipe: str) -> bool:
    return bool(recipe and recipe != "NONE" and "?" not in recipe and "[" not in recipe)


def load_recipe_candidates() -> tuple[dict[str, Counter[str]], set[str], set[str]]:
    candidates: dict[str, Counter[str]] = defaultdict(Counter)
    pass908_surfaces: set[str] = set()
    extended_surfaces: set[str] = set()
    for row in read_tsv(PASS908_CARDS):
        recipe = row["component_recipe"]
        if not valid_recipe(recipe):
            continue
        weight = max(1, int(row["marks"]))
        for surface in row["surface_forms"].split(" | "):
            candidates[surface][recipe] += weight
            pass908_surfaces.add(surface)
    for path in (PASS909_F13, PASS909_F75, PASS909_F70):
        for row in read_tsv(path):
            recipe = row["component_recipe"]
            surface = row["surface"]
            if valid_recipe(recipe):
                candidates[surface][recipe] += 2
                extended_surfaces.add(surface)
    return candidates, pass908_surfaces, extended_surfaces


def split_recipe(recipe: str) -> list[str]:
    return [part.strip() for part in recipe.split("+") if part.strip()]


def choose_recipe(surface: str, options: Counter[str], token_last: bool) -> str | None:
    if not options:
        return None
    if surface == "dy" and "Y" in options:
        return "Y"
    ordered = sorted(options, key=lambda recipe: (-options[recipe], len(split_recipe(recipe)), recipe))
    if token_last:
        closed = [recipe for recipe in ordered if split_recipe(recipe)[-1:] == ["DY"]]
        if closed:
            return closed[0]
    open_options = [recipe for recipe in ordered if split_recipe(recipe)[-1:] != ["DY"]]
    return open_options[0] if open_options else ordered[0]


HEURISTIC_CUES = [
    ("qolk", "SOLK"), ("solk", "SOLK"), ("aiin", "AIIN"),
    ("cheo", "CHEO"), ("shed", "SHED"), ("ched", "CHD"),
    ("lsh", "LSH"), ("ldd", "LD"), ("air", "AIR"), ("iin", "IIN"),
    ("ain", "AIN"), ("qok", "OK"), ("chok", "OK"), ("qot", "OT"),
    ("chol", "OL"), ("qol", "OL"), ("cfh", "CFH"),
    ("chek", "CHK"), ("chk", "CHK"), ("ckh", "CKH"), ("cth", "CTH"),
    ("eee", "EEE"), ("or", "OR"),
    ("ok", "OK"), ("ot", "OT"), ("ol", "OL"), ("ls", "OL"),
    ("chd", "CHD"), ("ee", "EE"), ("da", "DA"),
    ("al", "AL"), ("ar", "AR"), ("an", "AN"), ("sh", "SH"),
    ("ch", "CH"),
    ("q", "CARRIER_Q"), ("o", "O"), ("k", "K"), ("l", "L"),
    ("r", "R"), ("s", "S"), ("t", "T"), ("p", "P"),
    ("y", "Y"), ("e", "E"), ("d", "D_ADDR"),
    ("a", "A_ADDR"), ("m", "AM_ADDR"),
]


def heuristic_recipe(surface: str) -> tuple[str | None, str]:
    @lru_cache(maxsize=None)
    def solve(index: int) -> tuple[float, tuple[tuple[str, str], ...], int]:
        if index == len(surface):
            return 0.0, (), 0
        best = (-10_000.0, (), 10_000)
        for cue, component in HEURISTIC_CUES:
            if surface.startswith(cue, index):
                next_score, next_parts, next_residual = solve(index + len(cue))
                cue_score = float(len(cue) ** 2) if len(cue) > 1 else 0.35
                candidate = (cue_score + next_score, ((cue, component),) + next_parts, next_residual)
                if (candidate[0], -candidate[2], -len(candidate[1])) > (best[0], -best[2], -len(best[1])):
                    best = candidate
        next_score, next_parts, next_residual = solve(index + 1)
        residual_candidate = (
            next_score - 3.0,
            ((surface[index], f"LOCAL_CHAR_{surface[index].upper()}"),) + next_parts,
            next_residual + 1,
        )
        if (residual_candidate[0], -residual_candidate[2], -len(residual_candidate[1])) > (
            best[0], -best[2], -len(best[1])
        ):
            best = residual_candidate
        return best

    _, parts, residual = solve(0)
    components = [component for _, component in parts]
    multi_anchor = any(len(cue) > 1 and not component.startswith("LOCAL_CHAR_") for cue, component in parts)
    atomic = len(surface) <= 2 and residual == 0
    if residual <= 1 and (multi_anchor or atomic) and len(components) <= 9:
        status = "HEURISTIC_PLUS_LOCAL_SIGN" if residual else "HEURISTIC_COMPOSITION"
        return "+".join(components), status
    return None, "LOCAL_WORKSHOP_CARD"


def usage_class(selector: str, locus: str, kind: str) -> str:
    if locus in VISUAL_LABEL_LOCI:
        return "LABEL"
    if kind == "P":
        return "PROSE"
    if kind == "L":
        return "LABEL"
    if kind == "C":
        return "RING_TEXT"
    return "DIAGRAM_TEXT"


def component_values(recipe: str, register: str, catalog: dict[str, dict[str, str]]) -> tuple[str, str]:
    portable: list[str] = []
    concrete: list[str] = []
    for component in split_recipe(recipe):
        if component == "CARRIER_Q":
            continue
        if component.startswith("LOCAL_CHAR_"):
            char = component.removeprefix("LOCAL_CHAR_")
            portable.append(f"LOKALES ZEICHEN {char}")
            concrete.append(f"lokales {char}-Kennzeichen")
            continue
        entry = catalog.get(component)
        if entry:
            portable.append(entry["portable"])
            concrete.append(entry[register])
        else:
            portable.append(f"LOKALE KOMPONENTE {component}")
            concrete.append(f"lokale {component}-Komponente")
    return " · ".join(portable), " · ".join(concrete)


def fluent_recipe(recipe: str, register: str) -> str:
    phrases: list[str] = []
    for component in split_recipe(recipe):
        if component == "CARRIER_Q":
            continue
        phrase = COMMON_PHRASES.get(component) or REGISTER_VERBS[register].get(component)
        if component == "AIR":
            phrase = {
                "HERBAL": "ueber den Verarbeitungsweg",
                "BIOLOGICAL": "ueber den Wasser- oder Rohrlauf",
                "ZODIAC": "entlang des Ringlaufs",
                "PHARMA": "ueber den Flussweg des Ansatzes",
            }[register]
        if component == "AL":
            phrase = {
                "HERBAL": "an der Arbeitsstelle",
                "BIOLOGICAL": "an der Becken- oder Anschlussstelle",
                "ZODIAC": "an der Figurenstelle",
                "PHARMA": "an der Empfangs- oder Gefaessstelle",
            }[register]
        if component == "AR":
            phrase = {
                "HERBAL": "von der Entnahmeseite",
                "BIOLOGICAL": "von der Ausgangsstation",
                "ZODIAC": "von der Bezugsstelle",
                "PHARMA": "von der Vorrats- oder Entnahmestelle",
            }[register]
        if component.startswith("LOCAL_CHAR_"):
            phrase = f"verwende das lokale {component[-1]}-Kennzeichen"
        if phrase:
            phrases.append(phrase)
    if not phrases:
        return "verwende die gelernte lokale Karte"
    return "; ".join(phrases)


def load_visible_label_maps() -> tuple[dict[tuple[str, str, int], str], dict[str, str], dict[tuple[str, str, int], str]]:
    f70: dict[tuple[str, str, int], str] = {}
    for row in read_tsv(PASS909_F70):
        f70[(row["page"], row["locus"], int(row["group_index"]))] = row["concrete_owner"]
    f88 = {row["locus"]: row["creative_default_de"] for row in read_tsv(PASS909_F88) if row["kind"] == "LABEL"}
    f75: dict[tuple[str, str, int], str] = {}
    for row in read_tsv(PASS909_F75):
        if row["paragraph_or_label_block"] == "LABEL":
            f75[("f75r", row["locus"], int(row["token_index"]))] = row["owner_station_id"]
    return f70, f88, f75


def label_description(
    selector: str,
    locus: str,
    token_index: int,
    owner: str,
    f70: dict[tuple[str, str, int], str],
    f88: dict[str, str],
    f75: dict[tuple[str, str, int], str],
) -> str:
    if selector == "f88r" and locus in f88:
        return f88[locus].replace("_", " ").lower()
    if selector == "f75r":
        station = f75.get((selector, locus, token_index), "lokale Beckenstation")
        return f"Kennung der {station.replace('_', ' ').lower()}"
    if selector in {"f70v1", "f70v2"}:
        visible = f70.get((selector, locus, token_index), owner)
        return f"Kennung fuer {visible.replace('_', ' ').lower()}"
    return f"Kennung am {owner} ({locus})"


def local_card_phrase(register: str, code: str) -> str:
    return {
        "HERBAL": f"fuehre den im Muster bezeichneten Pflanzen-Arbeitsschritt {code} aus",
        "BIOLOGICAL": f"fuehre den im Muster bezeichneten Stationsschritt {code} aus",
        "ZODIAC": f"lies den im Muster bezeichneten Ringwert {code}",
        "PHARMA": f"fuehre den im Muster bezeichneten Zubereitungsschritt {code} aus",
    }[register]


def build_component_outputs(catalog: dict[str, dict[str, str]]) -> None:
    portable_rows = []
    for order, component in enumerate(PORTABLE_CORE, start=1):
        row = catalog[component]
        portable_rows.append(
            {
                "order": order,
                "component": component,
                "portable_value_de": row["portable"],
                "apprentice_rule_de": f"Lies {component} zuerst als {row['portable']}; setze erst danach den Bildregisterwert ein.",
            }
        )
    write_tsv(PORTABLE_OUT, portable_rows, ["order", "component", "portable_value_de", "apprentice_rule_de"])

    expansion_rows = []
    for component in sorted(catalog):
        row = catalog[component]
        layer = "A_PORTABLE_CORE" if component in PORTABLE_CORE else (
            "C_LOCAL_SIGN" if row["decision"] in {"REGISTER_LOCAL_ONLY", "LOCAL_SIGN", "RENDERER_ONLY"} else "B_REGISTER_OPERATOR"
        )
        expansion_rows.append(
            {
                "component": component,
                "layer": layer,
                "portable_value_de": row["portable"],
                "herbal_de": row["HERBAL"],
                "biological_de": row["BIOLOGICAL"],
                "zodiac_de": row["ZODIAC"],
                "pharma_de": row["PHARMA"],
                "pass909_decision": row["decision"].replace("KEEP_FORMAL", "KEEP_ADDRESS_ROLE"),
            }
        )
    write_tsv(
        EXPANSIONS_OUT,
        expansion_rows,
        ["component", "layer", "portable_value_de", "herbal_de", "biological_de", "zodiac_de", "pharma_de", "pass909_decision"],
    )


def main() -> int:
    catalog = load_components()
    candidates, pass908_surfaces, extended_surfaces = load_recipe_candidates()
    f70_labels, f88_labels, f75_labels = load_visible_label_maps()
    build_component_outputs(catalog)

    raw_events: list[dict[str, object]] = []
    page_owner = {selector: owner for selector, _, _, owner in PAGE_SPECS}
    page_register = {selector: register for selector, _, register, _ in PAGE_SPECS}
    page_physical = {selector: physical for selector, physical, _, _ in PAGE_SPECS}

    event_number = 0
    for selector, physical, register, owner in PAGE_SPECS:
        for line_order, row in enumerate(guarded_rows(selector), start=1):
            tokens = row["eva_clean"].split()
            use = usage_class(selector, row["locus"], row["kind"])
            for token_index, surface in enumerate(tokens, start=1):
                event_number += 1
                token_last = token_index == len(tokens)
                recipe = choose_recipe(surface, candidates.get(surface, Counter()), token_last)
                if surface in pass908_surfaces and recipe:
                    analysis_source = "PASS908_EXACT_RECIPE"
                elif surface in extended_surfaces and recipe:
                    analysis_source = "PASS909_EXTENDED_RECIPE"
                else:
                    heuristic, heuristic_status = heuristic_recipe(surface)
                    if recipe is None:
                        recipe = heuristic
                        analysis_source = heuristic_status
                    else:
                        analysis_source = "PASS909_EXTENDED_RECIPE"

                if use == "LABEL":
                    meaning_mode = "LOCAL_NOMENCLATOR"
                elif analysis_source in {"PASS908_EXACT_RECIPE", "PASS909_EXTENDED_RECIPE"}:
                    meaning_mode = "LEARNED_COMPONENT_RECIPE"
                elif analysis_source == "HEURISTIC_COMPOSITION":
                    meaning_mode = "NEW_COMPONENT_COMPOSITION"
                elif analysis_source == "HEURISTIC_PLUS_LOCAL_SIGN":
                    meaning_mode = "REGISTER_COMPOSITION_WITH_LOCAL_SIGN"
                else:
                    meaning_mode = "LOCAL_WORKSHOP_CARD"

                if recipe:
                    portable_value, register_value = component_values(recipe, register, catalog)
                    fluent = fluent_recipe(recipe, register)
                    displayed_recipe = recipe
                else:
                    portable_value = "GELERNTE LOKALE GANZKARTE"
                    register_value = "im Muster gelernter lokaler Arbeitswert"
                    fluent = ""
                    displayed_recipe = f"WHOLE[{surface}]"

                visible_label = ""
                if meaning_mode == "LOCAL_NOMENCLATOR":
                    visible_label = label_description(
                        selector, row["locus"], token_index, owner,
                        f70_labels, f88_labels, f75_labels,
                    )
                    register_value = visible_label
                    fluent = f"lies die gelernte lokale Kennung: {visible_label}"

                raw_events.append(
                    {
                        "event_id": f"P910-E{event_number:04d}",
                        "physical_page": physical,
                        "source_page": selector,
                        "register": register,
                        "locus": row["locus"],
                        "source_kind": row["kind"],
                        "usage_class": use,
                        "line_order": line_order,
                        "token_index": token_index,
                        "surface": surface,
                        "visible_owner_de": owner,
                        "form_analysis_source": analysis_source,
                        "component_recipe": displayed_recipe,
                        "meaning_mode": meaning_mode,
                        "portable_value_de": portable_value,
                        "register_value_de": register_value,
                        "local_code": "",
                        "fluent_token_de": fluent,
                        "line_is_sentence_end": "NO",
                    }
                )

    local_keys = sorted(
        {
            (str(row["register"]), str(row["usage_class"]), str(row["surface"]))
            for row in raw_events
            if row["meaning_mode"] in {"LOCAL_NOMENCLATOR", "LOCAL_WORKSHOP_CARD"}
        }
    )
    local_codes: dict[tuple[str, str, str], str] = {}
    counters: Counter[tuple[str, str]] = Counter()
    for register, use, surface in local_keys:
        drawer = "L" if use == "LABEL" else "W"
        counters[(register, drawer)] += 1
        local_codes[(register, use, surface)] = f"{LOCAL_PREFIX[register]}-{drawer}{counters[(register, drawer)]:03d}"

    for row in raw_events:
        if row["meaning_mode"] in {"LOCAL_NOMENCLATOR", "LOCAL_WORKSHOP_CARD"}:
            key = (str(row["register"]), str(row["usage_class"]), str(row["surface"]))
            code = local_codes[key]
            row["local_code"] = code
            if row["meaning_mode"] == "LOCAL_WORKSHOP_CARD":
                row["register_value_de"] = local_card_phrase(str(row["register"]), code)
                row["fluent_token_de"] = str(row["register_value_de"])

    dictionary_keys = sorted(
        {
            (
                str(row["register"]), str(row["usage_class"]), str(row["surface"]),
                str(row["component_recipe"]), str(row["meaning_mode"]), str(row["local_code"]),
            )
            for row in raw_events
        }
    )
    dictionary_ids = {key: f"P910-D{index:04d}" for index, key in enumerate(dictionary_keys, start=1)}
    for row in raw_events:
        key = (
            str(row["register"]), str(row["usage_class"]), str(row["surface"]),
            str(row["component_recipe"]), str(row["meaning_mode"]), str(row["local_code"]),
        )
        row["dictionary_entry_id"] = dictionary_ids[key]

    event_fields = [
        "event_id", "dictionary_entry_id", "physical_page", "source_page", "register",
        "locus", "source_kind", "usage_class", "line_order", "token_index", "surface",
        "visible_owner_de", "form_analysis_source", "component_recipe", "meaning_mode",
        "portable_value_de", "register_value_de", "local_code", "fluent_token_de",
        "line_is_sentence_end",
    ]
    write_tsv(EVENTS_OUT, raw_events, event_fields)

    by_dict: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in raw_events:
        by_dict[str(row["dictionary_entry_id"])].append(row)
    dictionary_rows = []
    for dictionary_id in sorted(by_dict):
        rows = by_dict[dictionary_id]
        first = rows[0]
        dictionary_rows.append(
            {
                "dictionary_entry_id": dictionary_id,
                "surface": first["surface"],
                "register": first["register"],
                "usage_class": first["usage_class"],
                "component_recipe": first["component_recipe"],
                "meaning_mode": first["meaning_mode"],
                "portable_value_de": first["portable_value_de"],
                "register_default_de": first["register_value_de"],
                "local_code": first["local_code"],
                "events": len(rows),
                "physical_pages": "|".join(sorted({str(row["physical_page"]) for row in rows}, key=PHYSICAL_PAGE_ORDER.index)),
                "default_reading_de": first["fluent_token_de"],
            }
        )
    write_tsv(
        DICTIONARY_OUT,
        dictionary_rows,
        [
            "dictionary_entry_id", "surface", "register", "usage_class", "component_recipe",
            "meaning_mode", "portable_value_de", "register_default_de", "local_code",
            "events", "physical_pages", "default_reading_de",
        ],
    )

    nomenclator_rows = []
    for row in dictionary_rows:
        if row["meaning_mode"] not in {"LOCAL_NOMENCLATOR", "LOCAL_WORKSHOP_CARD"}:
            continue
        events = by_dict[str(row["dictionary_entry_id"])]
        nomenclator_rows.append(
            {
                "local_code": row["local_code"],
                "surface": row["surface"],
                "register": row["register"],
                "drawer": "PICTURED_NAME_OR_CLASS" if row["meaning_mode"] == "LOCAL_NOMENCLATOR" else "COPIED_WORKSHOP_CARD",
                "visible_owner_or_default_de": row["register_default_de"],
                "form_recipe_if_any": row["component_recipe"],
                "events": row["events"],
                "loci": "|".join(sorted({str(event["locus"]) for event in events})),
                "apprentice_rule_de": "Kopiere die ganze Karte mit ihrem sichtbaren Besitzer; leite ihren Sachwert nicht aus den Teilzeichen ab.",
            }
        )
    write_tsv(
        NOMENCLATOR_OUT,
        nomenclator_rows,
        ["local_code", "surface", "register", "drawer", "visible_owner_or_default_de", "form_recipe_if_any", "events", "loci", "apprentice_rule_de"],
    )

    locus_groups: dict[tuple[str, str], list[dict[str, object]]] = defaultdict(list)
    for row in raw_events:
        locus_groups[(str(row["source_page"]), str(row["locus"]))].append(row)
    locus_rows = []
    for locus_number, ((selector, locus), rows) in enumerate(locus_groups.items(), start=1):
        first = rows[0]
        locus_rows.append(
            {
                "locus_reading_id": f"P910-L{locus_number:03d}",
                "physical_page": first["physical_page"],
                "source_page": selector,
                "register": first["register"],
                "locus": locus,
                "usage_class": first["usage_class"],
                "visible_owner_de": first["visible_owner_de"],
                "groups": len(rows),
                "source_sequence": " ".join(str(row["surface"]) for row in rows),
                "workshop_flow_de": "; ".join(str(row["fluent_token_de"]) for row in rows),
                "sentence_boundary_claim": "NONE__PHYSICAL_LOCUS_ONLY",
            }
        )
    write_tsv(
        LOCI_OUT,
        locus_rows,
        ["locus_reading_id", "physical_page", "source_page", "register", "locus", "usage_class", "visible_owner_de", "groups", "source_sequence", "workshop_flow_de", "sentence_boundary_claim"],
    )

    page_rows = []
    for physical in PHYSICAL_PAGE_ORDER:
        rows = [row for row in raw_events if row["physical_page"] == physical]
        modes = Counter(str(row["meaning_mode"]) for row in rows)
        page_rows.append(
            {
                "physical_page": physical,
                "source_selectors": "|".join(dict.fromkeys(str(row["source_page"]) for row in rows)),
                "register": rows[0]["register"],
                "visible_owner_de": " | ".join(dict.fromkeys(str(row["visible_owner_de"]) for row in rows)),
                "loci": len({(row["source_page"], row["locus"]) for row in rows}),
                "groups": len(rows),
                "surface_types": len({row["surface"] for row in rows}),
                "learned_component_events": modes["LEARNED_COMPONENT_RECIPE"],
                "new_component_events": modes["NEW_COMPONENT_COMPOSITION"],
                "local_sign_component_events": modes["REGISTER_COMPOSITION_WITH_LOCAL_SIGN"],
                "local_nomenclator_events": modes["LOCAL_NOMENCLATOR"],
                "local_workshop_card_events": modes["LOCAL_WORKSHOP_CARD"],
                "page_reading_de": {
                    "HERBAL": "Bildbesessener Pflanzenartikel: Stoff oder Teil waehlen, Menge und Arbeitsgang setzen, bearbeiten und weiterfuehren.",
                    "BIOLOGICAL": "Stationsblatt: Posten an Becken-, Koerper- oder Anschlussstellen setzen, halten, umsetzen und weiterleiten.",
                    "ZODIAC": "Himmelsregister: Ringstelle, Index, Grad und Bezug lesen; lokale Figurenkennungen aus dem Muster uebernehmen.",
                    "PHARMA": "Zutaten- und Ansatzblatt: lokale Drogenkennung lesen, Portion oder Mass setzen und den Gefaessgang ausfuehren.",
                }[str(rows[0]["register"])],
                "fluent_page_translation_de": PAGE_FLUENT[physical],
            }
        )
    write_tsv(
        PAGES_OUT,
        page_rows,
        ["physical_page", "source_selectors", "register", "visible_owner_de", "loci", "groups", "surface_types", "learned_component_events", "new_component_events", "local_sign_component_events", "local_nomenclator_events", "local_workshop_card_events", "page_reading_de", "fluent_page_translation_de"],
    )

    edition_lines = [
        "# Pass 910 — vollständige Vierzehn-Seiten-Werkstattausgabe",
        "",
        "Jede sichtbare Gruppe besitzt hier eine konkrete Lesung. Die physischen Zeilen",
        "sind nur Loci; sie werden nicht zu Satzgrenzen erklärt. Ein lokaler Code bedeutet",
        "einen vollständig gelernten Sachwert: Diesen ganzen Wert aus Besitzer und Muster lernen.",
        "",
    ]
    locus_by_page: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in locus_rows:
        locus_by_page[str(row["physical_page"])].append(row)
    page_summary_by_id = {str(row["physical_page"]): row for row in page_rows}
    for physical in PHYSICAL_PAGE_ORDER:
        summary = page_summary_by_id[physical]
        edition_lines.extend(
            [
                f"## {physical} — {summary['register']}",
                "",
                f"**Besitzer:** {summary['visible_owner_de']}",
                "",
                f"**Seitenlesung:** {summary['page_reading_de']}",
                "",
                f"**Flüssige Arbeitsübersetzung:** {summary['fluent_page_translation_de']}",
                "",
            ]
        )
        for locus in locus_by_page[physical]:
            edition_lines.append(f"- `{locus['locus']}` ({locus['usage_class']}): {locus['workshop_flow_de']}")
        edition_lines.append("")
    EDITION_OUT.write_text("\n".join(edition_lines).rstrip() + "\n", encoding="utf-8")

    total_modes = Counter(str(row["meaning_mode"]) for row in raw_events)
    handbook_lines = [
        "# Pass 910 — Meisterhandbuch für die Vierzehn-Seiten-Werkstatt",
        "",
        "## Was der Lehrling lernt",
        "",
        "1. Bestimme zuerst den sichtbaren Besitzer: Pflanze, Station, Himmelsrad oder Zutatenfeld.",
        "2. Lies die fünfzehn portablen Kerne immer zuerst in ihrem kurzen Grundwert.",
        "3. Setze erst danach die Fachausführung des jeweiligen Registers ein.",
        "4. Bei einer Bildkennung oder lokalen Ganzkarte kopiere den ganzen Eintrag aus dem Muster.",
        "5. Ein sichtbares DY schließt nur in einer lizenzierten Schlusskarte; Y hält den aktuellen Bezug offen.",
        "6. Eine physische Zeile beendet keine Aussage automatisch.",
        "",
        "## Die fünfzehn tragenden Kerne",
        "",
        "| Kern | Grundwert |",
        "|---|---|",
    ]
    for component in PORTABLE_CORE:
        handbook_lines.append(f"| `{component}` | {catalog[component]['portable']} |")
    handbook_lines.extend(
        [
            "",
            "## Die drei Schichten",
            "",
            f"- Bereits gelernte Komponentenrezepte: {total_modes['LEARNED_COMPONENT_RECIPE']} sichtbare Gruppen.",
            f"- Neu gebildete, vollständig zerlegte Kompositionen: {total_modes['NEW_COMPONENT_COMPOSITION']} sichtbare Gruppen.",
            f"- Registerkompositionen mit genau einem lokalen Zeichen: {total_modes['REGISTER_COMPOSITION_WITH_LOCAL_SIGN']} sichtbare Gruppen.",
            f"- Bildgebundener Nomenklator: {total_modes['LOCAL_NOMENCLATOR']} sichtbare Gruppen.",
            f"- Kopierte Werkstattkarten: {total_modes['LOCAL_WORKSHOP_CARD']} sichtbare Gruppen.",
            "",
            "Die letzte Schicht ist kein Abfallkorb. Jede Karte hat eine feste lokale Kennung und",
            "einen konkreten Werkstattsatz. Nur ihr innerer Sachwert wird aus dem Muster gelernt,",
            "nicht aus einer nachträglich erfundenen Buchstabenbedeutung.",
            "",
            "## Lesen und Schreiben",
            "",
            "Beim Schreiben wählt der Meister Besitzer und Sachwert, setzt portable Ablaufteile davor",
            "oder darum und rendert die Karte in der lokalen Hand. Beim Lesen erkennt der Lehrling",
            "zuerst Besitzer und Kartentyp, liest die portablen Teile und ergänzt lokale Namen aus dem",
            "Bild-/Musterfach. Dadurch können dieselben Formen in einem Bad einen Lauf, im Tierkreis",
            "aber eine Ringbahn bezeichnen, ohne dass AIR selbst WASSER heißen muss.",
        ]
    )
    HANDBOOK_OUT.write_text("\n".join(handbook_lines).rstrip() + "\n", encoding="utf-8")

    report_lines = [
        "# Pass 910 — dreischichtiges Vierzehn-Seiten-Meisterhandbuch",
        "",
        "## Ergebnis",
        "",
        f"Die Ausgabe bindet alle {len(raw_events)} sichtbaren Gruppen auf vierzehn physischen Seiten.",
        f"{total_modes['LEARNED_COMPONENT_RECIPE']} Gruppen verwenden eine bereits gelernte Komponentenrezeptur;",
        f"{total_modes['NEW_COMPONENT_COMPOSITION']} sind neue vollständige Zusammensetzungen;",
        f"{total_modes['REGISTER_COMPOSITION_WITH_LOCAL_SIGN']} enthalten zusätzlich genau ein lokales Zeichen;",
        f"{total_modes['LOCAL_NOMENCLATOR']} sind bildgebundene Namen oder Klassen;",
        f"{total_modes['LOCAL_WORKSHOP_CARD']} sind gelernte lokale Arbeitskarten.",
        "Keine Gruppe bleibt ohne Defaultlesung.",
        "",
        "Die beste Arbeitstheorie ist damit kein Universalwörterbuch, sondern ein kleines",
        "Schreiberprogramm mit vier Fachregistern und einem kopierten Namensfach.",
        "",
        "## Was jetzt wirklich fest im Sidequest-Handbuch steht",
        "",
        "- Menge/Einheit: AIIN und AIN.",
        "- Reihenfolge: OT und OL.",
        "- Grad/Stufe: E, EE, EEE und IIN.",
        "- Referenz/Schluss: Y und lizenziertes DY.",
        "- Weg/Adresse: L, CKH, AIR, AL und AR.",
        "",
        "Konkrete Verben wie wärmen, entnehmen, einsetzen oder prüfen bleiben Registerausführungen.",
        "Pflanzen-, Zutaten- und Figurenwerte dürfen als gelernte Ganzkarten auftreten.",
        "",
        "## Vollständige Ausgaben",
        "",
        "- `PASS910_2511_EVENT_INTERLINEAR.tsv`: jede sichtbare Gruppe in Quellreihenfolge.",
        "- `PASS910_CARD_DICTIONARY.tsv`: ein Default je Register-, Nutzungs- und Rezeptlesung.",
        "- `PASS910_LOCAL_NOMENCLATOR.tsv`: alle kopierten Namen und lokalen Ganzkarten.",
        "- `PASS910_LOCUS_EDITION.tsv`: jeder physische Locus ohne erfundene Satzgrenze.",
        "- `PASS910_FOURTEEN_PAGE_EDITION.md`: die vollständige lesbare Seitenausgabe.",
        "",
        "## Nächster sinnvoller Schritt",
        "",
        "Nicht sofort weitere Seiten hinzufügen. Zuerst die häufigsten lokalen Ganzkarten nach",
        "Register und sichtbarem Besitzer ordnen. Nur wenn zwei oder mehr Karten dabei dieselbe",
        "kurze Sachfunktion zeigen, wird eine neue Fachwurzel vorgeschlagen; sonst bleiben sie",
        "ehrlich im Nomenklator.",
    ]
    REPORT_OUT.write_text("\n".join(report_lines).rstrip() + "\n", encoding="utf-8")

    summary = {
        "status": "BUILT",
        "decision": "THREE_LAYER_WORKSHOP_GRAMMAR_WITH_LOCAL_NOMENCLATOR",
        "physical_pages": len(PHYSICAL_PAGE_ORDER),
        "source_selectors": len(PAGE_SPECS),
        "events": len(raw_events),
        "loci": len(locus_rows),
        "dictionary_entries": len(dictionary_rows),
        "surface_types": len({row["surface"] for row in raw_events}),
        "portable_core_components": len(PORTABLE_CORE),
        "learned_component_events": total_modes["LEARNED_COMPONENT_RECIPE"],
        "new_component_events": total_modes["NEW_COMPONENT_COMPOSITION"],
        "local_sign_component_events": total_modes["REGISTER_COMPOSITION_WITH_LOCAL_SIGN"],
        "shared_component_events": (
            total_modes["LEARNED_COMPONENT_RECIPE"]
            + total_modes["NEW_COMPONENT_COMPOSITION"]
            + total_modes["REGISTER_COMPOSITION_WITH_LOCAL_SIGN"]
        ),
        "local_nomenclator_events": total_modes["LOCAL_NOMENCLATOR"],
        "local_workshop_card_events": total_modes["LOCAL_WORKSHOP_CARD"],
        "local_drawer_entries": len(nomenclator_rows),
        "sealed_pages_accessed": 0,
        "events_sha256": sha(EVENTS_OUT),
        "dictionary_sha256": sha(DICTIONARY_OUT),
        "edition_sha256": sha(EDITION_OUT),
        "report_sha256": sha(REPORT_OUT),
    }
    SUMMARY_OUT.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(summary, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
