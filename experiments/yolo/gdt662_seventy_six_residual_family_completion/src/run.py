#!/usr/bin/env python3
"""Build GDT662: complete the 76-form V38 frontier with a mixed recipe register."""
from __future__ import annotations

import argparse
import csv
import hashlib
import importlib.util
import json
import re
import sys
import tempfile
from collections import Counter, defaultdict
from pathlib import Path
from typing import Iterable

sys.dont_write_bytecode = True


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
BASE_REL = Path("experiments/yolo/gdt662_seventy_six_residual_family_completion")
ART = ROOT / BASE_REL / "artifacts"
G661 = Path("experiments/yolo/gdt661_forty_eight_residual_family_completion")
_spec = importlib.util.spec_from_file_location("gdt661_builder_for_gdt662", ROOT / G661 / "src/run.py")
if _spec is None or _spec.loader is None:
    raise RuntimeError("cannot load GDT661 builder")
g661 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(g661)
TOKENS_REL, CROSS_REL = g661.TOKENS_REL, g661.CROSS_REL
STATUS = "PASS_861_TARGET_POSITIONS__V39_MIXED_RECIPE_REGISTER"


def card(surface: str, meaning: str, composition: str, rival: str, family: str) -> dict[str, str]:
    return {
        "surface": surface,
        "working_meaning_de": meaning,
        "composition": composition,
        "strongest_rival_de": rival,
        "family": family,
    }


# Order is the first-seen order of GDT661's 78-row/76-type frontier.  These are
# exact whitespace-delimited cards.  Composition is explanatory and predictive
# within this working model, but never dispatches a substring on its own.
EXACT_WHOLE_SPECS = (
    card("lkees", "stark erhitzte Holzdroge, Endstufe", "L_WOOD+K_HOT+EE_END+S_BOUND", "heißer L-Rahmenstoff", "WOOD"),
    card("shar", "angefeuchtete Drogenfraktion I", "SH_MOIST+AR_FRACTION_I", "Feuchtfraktion ohne Zubereitungswert", "MOIST"),
    card("ycheeo", "Eintrag: zweiter Trockenansatz", "Y_ENTRY+CHEE_DRY_II+O_PREP", "Y-Grenze vor CHEEO", "ENTRY"),
    card("otydy", "kalter Ansatz in Grundform, fertig", "O_PREP+T_COLD+Y_BASE+DY_FINISHED", "kalte Zustandsform", "COLD_PREP"),
    card("lkedar", "erhitzte Holzfraktion I", "L_WOOD+K_HOT+ED+AR_FRACTION_I", "erhitzte Ansatzfraktion I", "WOOD"),
    card("far", "Pflanzendroge", "LEARNED_F_DRUG_WHOLE", "Blüten- oder Fruchtdroge", "LEARNED_WHOLE"),
    card("dsheey", "abgemessene, vollständig angefeuchtete Droge", "D_MEASURED+SHEEY_MOIST_END", "Feuchtmaß am Gradende", "MOIST"),
    card("choty", "kalter Trockenansatz", "CH_DRY+O_PREP+T_COLD+Y_BASE", "nur kalt-trockener Zustand", "COLD_PREP"),
    card("chkey", "trocken-heiß in der Mittelstufe", "CH_DRY+K_HOT+EY_MIDDLE", "heiß getrocknete Form I", "DRY"),
    card("cheeoldy", "vollständig getrockneter Drogenstoff, fertig", "CH_DRY+EE_END+OL_MATERIAL+DY_FINISHED", "zweite Bindungsstufe", "DRY"),
    card("a", "je, zu gleichen Teilen", "LEARNED_EQUAL_PARTS_SIGN", "davon/mit als Mengenanschluss", "FUNCTION_WORD"),
    card("oteeo", "zweiter Kaltansatz", "O_PREP+T_COLD+EE_STAGE_II+O_MEDIUM", "kalte Zubereitung am Gradende", "COLD_PREP"),
    card("lain", "Drogenholz, Charge II", "L_WOOD+A_VALUE+IN_II", "Flüssigkeit oder Auszug, Klasse II", "WOOD"),
    card("dchy", "Dosis Trockendroge, Grundform", "D_DOSE+CHY_DRY_BASE", "bloßes Trockenmaß", "DRY"),
    card("oro", "Ansatzportion", "OR_PORTION+O_PREP", "zweite Portion", "PART"),
    card("oekor", "erwärmte Ansatzportion", "O_PREP+E_BOUND+K_HOT+OR_PORTION", "heißer Drogenteil", "PART"),
    card("ycho", "Eintrag: Trockenansatz", "Y_ENTRY+CHO_DRY_PREP", "Y-Grenze vor CHO", "ENTRY"),
    card("schodain", "trockener Samenansatz, Dosis II", "S_SEED+CHO_DRY_PREP+DAIN_DOSE_II", "Salzansatz, Grad II", "SEED"),
    card("choraly", "roher Pflanzenteil, Klasse I", "CHOR_PLANT_PART+AL_RAW_I+Y_BASE", "Blütenteil, Klasse I", "PART"),
    card("totchy", "kalter Ansatz aus kalt-trockener Droge", "T_COLD+O_PREP+TCH_COLD_DRY+Y_BASE", "doppelt kalt markierter Ansatz", "COLD_PREP"),
    card("qokol", "erhitzen", "QO_COMMAND+KOL_HOT_MATERIAL", "heißes Drogenmaterial", "Q_COMMAND"),
    card("sham", "ein Maß Flüssigkeit", "SH_MOIST+AM_UNIT_I", "ein Maß angefeuchteter Droge", "MOIST"),
    card("kochky", "heißer Trockenansatz, Grundform", "K_HOT+O_PREP+CHK_DRY_HOT+Y_BASE", "Arzneikompositumform", "DRY"),
    card("otoldy", "fertiger Kaltansatz", "O_PREP+TOL_COLD_MATERIAL+DY_FINISHED", "kaltes Materialfeld, geschlossen", "COLD_PREP"),
    card("qo", "nehmen", "LEARNED_RECIPE_COMMAND", "Rezept- oder Qualitätsrahmen", "FUNCTION_WORD"),
    card("ctho", "Krautansatz", "CTH_LEAF_HERB+O_PREP", "Blattansatz", "CTH"),
    card("dchaiin", "abgemessene Trockendroge, Grad III", "D_MEASURED+CH_DRY+A_VALUE+IIN_III", "Trockenheitsgrad III", "DRY"),
    card("ydaiin", "davon drei Maße", "Y_REFERENCE+DAIIN_DOSE_III", "Bezugsdosis III", "MEASURE"),
    card("dytory", "als kalte Portion abteilen", "DY_FINISHED+T_COLD+OR_PORTION+Y", "abgeschlossener kalter Teilwert", "PART"),
    card("kolschees", "heiß getrocknete Arzneispecies", "KOL_HOT_MATERIAL+S+CHEES_DRY_II", "heißes Material plus trockene Species", "HYBRID"),
    card("tchol", "kalt-trockenes Drogenmaterial", "T_COLD+CHOL_DRY_MATERIAL", "reine Qualitätsangabe", "DRY"),
    card("cthodd", "fertiger Krautabsud", "CTH_LEAF_HERB+O_PREP+DD_FINISHED", "fertiger Blattabsud", "CTH"),
    card("sheoty", "kalt angesetzte Feuchtzubereitung", "SHEO_MOIST_PREP+T_COLD+Y_BASE", "feucht-kalte Qualitätsform", "MOIST"),
    card("ykchokeo", "Eintrag: heiß-trockener Auszug", "Y_ENTRY+KCH_HOT_DRY+O_PREP+KEO", "verschachtelte Qualitätsform", "ENTRY"),
    card("ochockhy", "Trockenansatz eines Arzneikompositums", "O_PREP+CHO_DRY+CKH_COMPOSITE+Y", "heiß-trockener CTH-Ansatz", "CTH"),
    card("qoctheol", "Krautgrundstoff", "QO_FRAME+CTH_LEAF_HERB+E+OL_MATERIAL", "Blattgrundstoff", "HYBRID"),
    card("kcheeytain", "heiß-trocken bis Endstufe, danach kalt Grad II", "K_HOT+CHEEY_DRY_END+TAIN_COLD_II", "Zustandsliste ohne Folge", "HYBRID"),
    card("shckheody", "fertig angesetztes feuchtes Arzneikompositum", "SH_MOIST+CKH_COMPOSITE+EO_PREP+DY", "feuchter CTH-Ansatz", "CTH"),
    card("qodaiin", "Qualitätsgrad III", "QO_FRAME+DAIIN_GRADE_III", "Ansatzdosis III", "Q_COMMAND"),
    card("ytchocthol", "Eintrag: kalt-trockener Krautansatz", "Y_ENTRY+T_COLD+CHO_DRY+CTHOL_LEAF_HERB", "kalt-trockener Blattansatz", "ENTRY"),
    card("qolkeeoly", "erhitzte Drogenbasis; danach abseihen", "QOL_DRUG_BASE+KEEOL_HOT+Y_CLOSE", "zusammengeschriebene Materialliste", "HYBRID"),
    card("olsheedy", "vollständig eingeweichtes Drogenmaterial, fertig", "OL_MATERIAL+SH_MOIST+EE_END+DY", "feuchtes Material am Gradende", "MOIST"),
    card("shety", "feucht-kalt ansetzen", "SH_MOIST+E+T_COLD+Y", "feucht-kalter Zustand", "MOIST"),
    card("qokchdyl", "heiß-trocken aufbereitetes Drogenholz", "QO_FRAME+KCH_HOT_DRY+DY+L_WOOD", "Drogenstoff statt Holz", "WOOD"),
    card("saiiin", "Saatgutcharge IV", "S_SEED+A_VALUE+IIIN_IV", "Salz oder Samenmenge IV", "SEED"),
    card("qol", "Drogenstoff zugeben", "QO_FRAME+L_MATERIAL_AS_LEARNED_ACTION", "Rezeptgrundlage / Trägerdroge", "Q_COMMAND"),
    card("chee", "vollständig getrocknet", "CH_DRY+EE_END", "zweite Bindungsstufe", "DRY"),
    card("chl", "trocknen", "LEARNED_DRY_COMMAND", "trockenes Drogenholz/Kurzform", "LEARNED_WHOLE"),
    card("lokedy", "erhitztes Drogenholz, fertig", "L_WOOD+O_PREP+K_HOT+EDY", "heißer L-Rahmenansatz", "WOOD"),
    card("olkchdy", "heiß-trocken aufbereitetes Drogenmaterial", "OL_MATERIAL+KCH_HOT_DRY+DY", "heiß-trockener Qualitätswert", "DRY"),
    card("tees", "kalte Arzneispecies, Endstufe", "T_COLD+EE_END+S_SPECIES", "kaltes Drogenmaterial", "HYBRID"),
    card("olkedy", "erhitzte Drogenbasis, fertig", "OL_MATERIAL+K_HOT+EDY", "heißes Material in Mittelstufe", "DRY"),
    card("oly", "abseihen", "OL_MATERIAL+Y_CLOSE_AS_LEARNED_ACTION", "Drogenmaterial in Grundform", "HYBRID"),
    card("los", "Drogenholzposten", "LEARNED_WOOD_BATCH", "Holzpräparat einer Drogenart", "LEARNED_WHOLE"),
    card("olshdy", "angefeuchtetes Drogenmaterial, fertig", "OL_MATERIAL+SH_MOIST+DY", "feuchter Materialzustand", "MOIST"),
    card("doly", "eine Dosis Abguss", "D_DOSE+OL_DECANT+Y", "abgemessener Drogenstoff", "MEASURE"),
    card("keeol", "stark erhitzter Drogenstoff", "K_HOT+EE_END+OL_MATERIAL", "heißer Stoff am Gradende", "DRY"),
    card("aral", "Rohdrogenfraktion I", "AR_FRACTION_I+AL_RAW_I", "Fraktion neben separater Rohstoffklasse", "MEASURE"),
    card("dchedy", "abgemessene Trockendroge, fertig", "D_MEASURED+CHEDY_DRY_FINISHED", "Dosisfeld trocken und geschlossen", "DRY"),
    card("kair", "heiße Drogenfraktion II", "K_HOT+AIR_FRACTION_II", "Hitze-/Sortierklasse II", "MEASURE"),
    card("ra", "Wurzelanteil", "R_ROOT+A_VALUE_LINK", "Wurzelkopf vor offener Mengenstelle", "MEASURE"),
    card("lchedar", "getrocknete Holzfraktion I", "L_WOOD+CHED_DRY+AR_FRACTION_I", "Holz mit Trockenheitsgrad I", "WOOD"),
    card("ey", "anschließend", "LEARNED_SEQUENCE_SIGN", "mischen oder Mittelstufe", "FUNCTION_WORD"),
    card("pcheol", "getrockneter Pulverstoff", "P_POWDER+CHEOL_DRY_MATERIAL", "Pulver aus Trockendroge", "DRY"),
    card("lchedam", "ein Maß getrocknetes Drogenholz", "L_WOOD+CHED_DRY+DAM_DOSE_I", "Holz mit Trockenheitsmaß I", "WOOD"),
    card("qokeeey", "stark erhitzt, Endstufe III", "QO_FRAME+K_HOT+EEE_END_III+Y", "Bindungsstufe III", "Q_COMMAND"),
    card("oldy", "fertiger, abgeseihter Auszug", "OL_MATERIAL+D_FINISHED+Y", "fertig aufbereitetes Drogenmaterial", "HYBRID"),
    card("sheekchy", "vollständig anfeuchten, dann heiß-trocken ansetzen", "SHEE_MOIST_END+KCH_HOT_DRY+Y", "Qualitäten ohne Handlungsfolge", "MOIST"),
    card("ypshedy", "Eintrag: fertige Pulverpaste", "Y_ENTRY+P_POWDER+SHEDY_MOIST_FINISHED", "Y-Grenze vor Feuchtpulver", "ENTRY"),
    card("opchdy", "fertiges Trockenpulverpräparat", "O_PREP+P_POWDER+CHDY_DRY_FINISHED", "Trockenansatz mit P-Kopf", "DRY"),
    card("taral", "kalte Rohdrogenfraktion I", "T_COLD+AR_FRACTION_I+AL_RAW_I", "kalte Rohstoffklasse I", "MEASURE"),
    card("dytshy", "danach kalt-feucht ansetzen", "DY_SEQUENCE+T_COLD+SH_MOIST+Y", "kalt-feuchter Abschluss", "HYBRID"),
    card("choldy", "fertig getrocknete Droge", "CHOL_DRY_MATERIAL+DY_FINISHED", "Trockengut plus Abschluss", "DRY"),
    card("tchor", "kalt-trockene Drogenportion", "T_COLD+CHOR_PLANT_PART", "kalt-trockener Pflanzenteil", "PART"),
    card("sheoees", "vollständig eingeweichte Arzneimischung", "SHEO_MOIST_PREP+EE_END+S", "feuchtes Material, Bindungsstufe II", "HYBRID"),
    card("cheyet", "getrocknete, abgekühlte Wurzel", "LEARNED_LABEL_WHOLE", "Pflanzenname im einzigen Labelkontext", "LEARNED_WHOLE"),
)

TARGET_ORDER = tuple(row["surface"] for row in EXACT_WHOLE_SPECS)
TARGET_SURFACES = frozenset(TARGET_ORDER)
EXACT_BY_SURFACE = {row["surface"]: row for row in EXACT_WHOLE_SPECS}
EXPECTED_SURFACE_COUNTS = {
    "qol": 132, "qokol": 88, "oly": 53, "qo": 50, "qodaiin": 41, "choty": 34,
    "shar": 29, "chl": 28, "qokeeey": 27, "dchedy": 26, "oldy": 25, "dchy": 22,
    "olkedy": 22, "tchor": 21, "ctho": 18, "opchdy": 18, "tchol": 16, "aral": 15,
    "ey": 14, "ydaiin": 14, "kair": 11, "keeol": 10, "pcheol": 10, "a": 9,
    "otoldy": 9, "choldy": 8, "dsheey": 7, "shety": 7, "oteeo": 6, "sham": 6,
    "ycheeo": 6, "lain": 5, "los": 5, "chkey": 4, "doly": 4, "olkchdy": 4,
    "oro": 4, "dchaiin": 3, "olshdy": 3, "otydy": 3, "ycho": 3, "far": 2,
    "lchedam": 2, "lchedar": 2, "saiiin": 2, "sheekchy": 2, "taral": 2,
    "chee": 1, "cheeoldy": 1, "cheyet": 1, "choraly": 1, "cthodd": 1,
    "dytory": 1, "dytshy": 1, "kcheeytain": 1, "kochky": 1, "kolschees": 1,
    "lkedar": 1, "lkees": 1, "lokedy": 1, "ochockhy": 1, "oekor": 1,
    "olsheedy": 1, "qoctheol": 1, "qokchdyl": 1, "qolkeeoly": 1, "ra": 1,
    "schodain": 1, "shckheody": 1, "sheoees": 1, "sheoty": 1, "tees": 1,
    "totchy": 1, "ykchokeo": 1, "ypshedy": 1, "ytchocthol": 1,
}

LOW_SURFACES = frozenset({
    "lkees", "lkedar", "far", "cheeoldy", "choraly", "totchy", "kochky", "cthodd",
    "ykchokeo", "ochockhy", "qoctheol", "kcheeytain", "shckheody", "ytchocthol",
    "qolkeeoly", "qokchdyl", "tees", "ypshedy", "dytshy", "sheoees", "cheyet",
})
STRONG_SURFACES = frozenset({
    "shar", "choty", "qokol", "qo", "ctho", "qodaiin", "qol", "chl", "oly", "ey",
    "dchedy", "oldy", "dchy", "olkedy", "tchor", "opchdy", "tchol", "aral", "ydaiin",
    "kair", "keeol", "pcheol", "otoldy", "choldy", "dsheey", "shety", "sham", "lain",
})
LEARNED_FUNCTION_SURFACES = frozenset({"qo", "a", "ey"})
LEARNED_WHOLE_SURFACES = frozenset({"chl", "far", "los", "cheyet"})
HYBRID_SURFACES = frozenset({"oro", "dytory", "kolschees", "cthodd", "ochockhy", "shckheody", "qokchdyl", "dytshy"})
Y_ENTRY_SURFACES = frozenset({"ycheeo", "ycho", "ykchokeo", "ypshedy", "ytchocthol"})
ACTION_SURFACES = frozenset({"qokol", "qokeeey", "chl", "dytory", "sheekchy", "shety", "dytshy"})
ACTION_RENDER = {
    "qokeeey": "erhitze bis Endstufe III",
    "dytory": "teile als kalte Portion ab", "sheekchy": "feuchte vollständig an, dann setze heiß-trocken an",
    "shety": "setze feucht-kalt an", "dytshy": "setze danach kalt-feucht an",
}
GRADE_AFTER_QOKOL = {"dain": "II", "daiin": "III", "daiiin": "IV"}
ACTION_BOUNDARY_SURFACES = frozenset({
    "qol", "qokol", "qokeeey", "chl", "oly", "shety", "sheekchy", "dytory", "dytshy",
})
CHL_PREVIOUS_CONTEXTS = frozenset({("qokar", "aiin"), ("qokar", "ykeedy")})
EY_MIX_CONTEXTS = frozenset({("cheol", "cheor")})
Y_PAYLOADS = {
    "ycheeo": "zweiter Trockenansatz", "ycho": "Trockenansatz", "ykchokeo": "heiß-trockener Auszug",
    "ypshedy": "fertige Pulverpaste", "ytchocthol": "kalt-trockener Krautansatz",
}
OUTPUT_NAMES = (
    "PAGE_ALLOWLIST.tsv", "TARGET_DECISION_DECK.tsv", "ACCEPTED_WHOLE_SURFACE_DEFAULTS.tsv",
    "CONTEXT_RENDERING_CARDS.tsv", "CARD_ARCHITECTURE_SUMMARY.tsv", "ALL_OCCURRENCE_SEMANTIC_AUDIT.tsv",
    "READER_VARIANT_AUDIT.tsv", "FAMILY_COMPOSITION_ATLAS.tsv", "FRONTIER_76_COMPLETIONS.tsv",
    "TARGET_LINE_TRANSLATIONS.tsv", "ROUND_COVERAGE_COUNTS.tsv", "NEWLY_COMPLETED_LINES.tsv",
    "NEWLY_EXPOSED_ONE_HOLE_LINES.tsv", "V39_WORKING_TOKEN_GLOSSARY.tsv", "WORKING_DICTIONARY_V39.tsv",
    "ALL_LINE_CONCRETE_COVERAGE_V39.tsv", "COMPLETE_PASSAGES_V39.tsv", "ONE_UNKNOWN_PASSAGES_V39.tsv",
)
GENERIC_FILLER = re.compile(
    r"arbeitsgut|arbeitsvorgang|arbeitschritt|arbeitsschritt|arbeitsmittel|arbeitsstoff|vorgang ausführen|gut bearbeiten",
    re.I,
)


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: list[dict[str, object]], fields: Iterable[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(fields), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_hash(value: object) -> str:
    raw = json.dumps(value, sort_keys=True, ensure_ascii=True, separators=(",", ":")).encode()
    return hashlib.sha256(raw).hexdigest()


def split_pipe(value: object) -> list[str]:
    return str(value).split(" | ") if str(value) else []


def parse_compact(value: object) -> list[str]:
    return [] if str(value) in {"", "NONE"} else str(value).split("|")


def position_label(ordinal: int, length: int) -> str:
    if length == 1:
        return "ONLY"
    if ordinal == 1:
        return "BOS"
    if ordinal == length:
        return "EOS"
    return "MEDIAL"


def card_type(surface: str) -> str:
    if surface in LEARNED_FUNCTION_SURFACES:
        return "LEARNED_FUNCTION_WORD"
    if surface in LEARNED_WHOLE_SURFACES:
        return "LEARNED_WHOLE"
    if surface in HYBRID_SURFACES:
        return "HYBRID_EXACT"
    return "PRODUCTIVE_COMPOUND"


def card_strength(surface: str) -> str:
    if surface in LOW_SURFACES:
        return "LOW_EXPLORATORY"
    if surface in STRONG_SURFACES:
        return "STRONG_PRACTICAL_OR_COMPOSITIONAL"
    return "MEDIUM_EXACT_WHOLE"


def rendering_class(surface: str, position: str, left_surface: str = "<BOS>", right_surface: str = "<EOS>") -> str:
    if surface in Y_ENTRY_SURFACES:
        return "Y_ENTRY_COMMAND"
    if surface == "qo":
        return "QO_TAKE_PREVIOUS" if position in {"EOS", "ONLY"} else "QO_TAKE_NEXT"
    if surface == "qol":
        if right_surface == "qol":
            return "QOL_ADD_PREVIOUS"
        if left_surface == "qol":
            return "QOL_ADD_NEXT"
        if position in {"EOS", "ONLY"} or right_surface in ACTION_BOUNDARY_SURFACES:
            return "QOL_ADD_PREVIOUS"
        return "QOL_ADD_NEXT"
    if surface == "qokol":
        if right_surface in GRADE_AFTER_QOKOL:
            return "QOKOL_TO_GRADE"
        if right_surface == "qokol":
            return "QOKOL_DOUBLE_START"
        return "QOKOL_HEAT_NEXT"
    if surface == "oly":
        return "OLY_STRAIN_FINISH" if position in {"EOS", "ONLY"} else "OLY_STRAIN_PREVIOUS"
    if surface == "a":
        return "A_EQUAL_PARTS_CONTINUATION" if position in {"EOS", "ONLY"} else "A_EQUAL_PARTS"
    if surface == "ey":
        if position in {"EOS", "ONLY"}:
            return "EY_MIX_PREVIOUS"
        if position == "BOS":
            return "EY_MIX_NEXT"
        if (left_surface, right_surface) in EY_MIX_CONTEXTS:
            return "EY_MIX_BETWEEN_MATERIALS"
        return "EY_SEQUENCE_NEXT"
    if surface == "qodaiin" and right_surface == "qodaiin":
        return "QODAIIN_GRADE_PREVIOUS"
    if surface == "qodaiin" and left_surface == "qodaiin":
        return "QODAIIN_GRADE_NEXT"
    if surface == "chee" and right_surface == "ol":
        return "CHEE_DRY_MATERIAL_NEXT"
    if surface == "chl":
        if position in {"EOS", "ONLY"}:
            return "CHL_DRY_FINISH"
        if (left_surface, right_surface) in CHL_PREVIOUS_CONTEXTS:
            return "CHL_DRY_PREVIOUS_HOT_FRACTION"
        return "CHL_DRY_NEXT"
    if surface in ACTION_SURFACES:
        return "PRACTICAL_ACTION"
    return "EXACT_WHOLE"


def occurrence_render(
    surface: str,
    position: str,
    left_surface: str = "<BOS>",
    right_surface: str = "<EOS>",
) -> str:
    klass = rendering_class(surface, position, left_surface, right_surface)
    if klass == "Y_ENTRY_COMMAND":
        return "Eintrag: " + Y_PAYLOADS[surface]
    if klass == "QO_TAKE_NEXT":
        return "nimm Folgendes:"
    if klass == "QO_TAKE_PREVIOUS":
        return "nimm Vorstehendes."
    if klass == "QOL_ADD_PREVIOUS":
        return "gib Vorstehendes hinzu"
    if klass == "QOL_ADD_NEXT":
        return "gib Folgendes hinzu:"
    if klass in {"QOKOL_TO_GRADE", "QOKOL_DOUBLE_START"}:
        return "erhitze"
    if klass == "QOKOL_HEAT_NEXT":
        return "erhitze Folgendes:"
    if klass == "OLY_STRAIN_FINISH":
        return "seihe Vorstehendes ab."
    if klass == "OLY_STRAIN_PREVIOUS":
        return "seihe Vorstehendes ab"
    if klass == "A_EQUAL_PARTS":
        return "je zu gleichen Teilen"
    if klass == "A_EQUAL_PARTS_CONTINUATION":
        return "zu gleichen Teilen mit Folgendem:"
    if klass == "EY_SEQUENCE_NEXT":
        return "anschließend:"
    if klass == "EY_MIX_PREVIOUS":
        return "mische Vorstehendes."
    if klass == "EY_MIX_NEXT":
        return "mische Folgendes:"
    if klass == "EY_MIX_BETWEEN_MATERIALS":
        return "mische Vorstehendes mit Folgendem:"
    if klass == "QODAIIN_GRADE_PREVIOUS":
        return "Vorstehendes: Qualitätsgrad III"
    if klass == "QODAIIN_GRADE_NEXT":
        return "Folgendes: Qualitätsgrad III"
    if klass == "CHEE_DRY_MATERIAL_NEXT":
        return "vollständig getrocknetes"
    if klass == "CHL_DRY_FINISH":
        return "trockne."
    if klass == "CHL_DRY_NEXT":
        return "trockne Folgendes:"
    if klass == "CHL_DRY_PREVIOUS_HOT_FRACTION":
        return "trockne die vorstehende heiße Drogenfraktion I"
    if klass == "PRACTICAL_ACTION":
        return ACTION_RENDER[surface]
    return EXACT_BY_SURFACE[surface]["working_meaning_de"]


def line_translation(
    locus: str,
    line: list[dict[str, str]],
    glosses: list[str],
    y_occurrence_by_token: dict[tuple[str, int], dict[str, object]],
    inherited_target_by_token: dict[tuple[str, int], dict[str, object]],
    target_by_token: dict[tuple[str, int], dict[str, object]],
) -> str:
    merged = dict(inherited_target_by_token)
    merged.update(target_by_token)
    marked = list(glosses)
    replacements: dict[str, str] = {}
    members = sorted(
        (row for key, row in target_by_token.items() if key[0] == locus),
        key=lambda row: int(row["ordinal"]),
    )
    for occurrence in members:
        ordinal = int(occurrence["ordinal"])
        marker = f"§G662_{occurrence['token_index']}_{ordinal}§"
        marked[ordinal - 1] = marker
        replacements[marker] = str(occurrence["working_render_de"])
    rendered = g661.g660.practical_line_translation(locus, line, marked, y_occurrence_by_token, merged)
    for marker, replacement in replacements.items():
        if rendered.count(marker) != 1:
            raise RuntimeError(f"positional render marker lost or duplicated at {locus}: {marker}")
        rendered = rendered.replace(marker, replacement)
    words = [row["eva"] for row in line]
    double_grade_sequences = [
        GRADE_AFTER_QOKOL[words[index + 2]]
        for index in range(len(words) - 2)
        if words[index] == "qokol" and words[index + 1] == "qokol" and words[index + 2] in GRADE_AFTER_QOKOL
    ]
    for grade in double_grade_sequences:
        pattern = rf"erhitze; erhitze; (?:Qualitätsgrad|Grad-/Maßwert) {grade}"
        rendered, replaced = re.subn(pattern, f"erhitze zweimal bis Grad {grade}", rendered, count=1)
        if replaced != 1:
            raise RuntimeError(f"qokol qokol grade fold failed at {locus}: {grade}")
    single_grade_sequences = [
        GRADE_AFTER_QOKOL[words[index + 1]]
        for index in range(len(words) - 1)
        if words[index] == "qokol" and words[index + 1] in GRADE_AFTER_QOKOL
        and not (index > 0 and words[index - 1] == "qokol")
    ]
    for grade in single_grade_sequences:
        pattern = rf"erhitze; (?:Qualitätsgrad|Grad-/Maßwert) {grade}"
        rendered, replaced = re.subn(pattern, f"erhitze bis Grad {grade}", rendered, count=1)
        if replaced != 1:
            raise RuntimeError(f"qokol grade fold failed at {locus}: {grade}")
    non_grade_qokol_pairs = sum(
        words[index] == words[index + 1] == "qokol"
        and (index + 2 >= len(words) or words[index + 2] not in GRADE_AFTER_QOKOL)
        for index in range(len(words) - 1)
    )
    for _ in range(non_grade_qokol_pairs):
        rendered, replaced = re.subn(
            r"erhitze; erhitze Folgendes:",
            "erhitze zweimal Folgendes:",
            rendered,
            count=1,
        )
        if replaced != 1:
            raise RuntimeError(f"qokol qokol non-grade fold failed at {locus}")
    qo_y_pairs = sum(words[index] == "qo" and words[index + 1] == "y" for index in range(len(words) - 1))
    for _ in range(qo_y_pairs):
        rendered, replaced = re.subn(
            r"nimm Folgendes:\s*;?\s*hierzu:",
            "nimm hierzu Folgendes:",
            rendered,
            count=1,
        )
        if replaced != 1:
            raise RuntimeError(f"qo y fold failed at {locus}")
    chee_ol_pairs = sum(words[index] == "chee" and words[index + 1] == "ol" for index in range(len(words) - 1))
    for _ in range(chee_ol_pairs):
        rendered, replaced = re.subn(
            r"vollständig getrocknetes; Eigenschafts-/Zustands-/Materialträger; als nacktes Wort Gut/Ansatz",
            "vollständig getrocknetes Drogenmaterial",
            rendered,
            count=1,
        )
        if replaced != 1:
            raise RuntimeError(f"chee ol fold failed at {locus}")
    return re.sub(r"\.{2,}", ".", rendered).replace(".;", ";").replace(":;", ":")


def metrics(coverage, one_unknown, complete, glossary) -> dict[str, int]:
    return {
        "physical_lines": len(coverage),
        "known_token_positions": sum(int(row["known_tokens"]) for row in coverage),
        "unknown_token_positions": sum(int(row["unknown_tokens"]) for row in coverage),
        "complete_multi_token_lines": len(complete),
        "strict_complete_lines": sum(int(row["strict_complete"]) for row in complete),
        "one_unknown_lines": len(one_unknown),
        "strict_one_unknown_lines": sum(int(row["strict_eligible"]) for row in one_unknown),
        "working_glossary_surfaces": len(glossary),
    }


def build(output_dir: Path) -> dict[str, object]:
    output_dir.mkdir(parents=True, exist_ok=True)
    pages = {row["page"] for row in read_tsv(ROOT / G661 / "artifacts/PAGE_ALLOWLIST.tsv")}
    if len(pages) != 179 or "f1r" in pages or any(page.startswith("f84") for page in pages):
        raise RuntimeError("inherited page allow-list is not the exact safe 179-page panel")
    tokens, token_stats = g661.g659.guarded_query(
        TOKENS_REL, pages, "page,locus,token_index,eva,kind,section,language,hand"
    )
    cross, cross_stats = g661.g659.guarded_query(
        CROSS_REL, pages, "page,locus,all_three_present,all_present_exact,zl3b_clean,it2a_clean,rf1b_clean"
    )
    if (len(tokens), len(cross)) != (32339, 4137):
        raise RuntimeError("guarded source census drift")
    by_line: dict[str, list[dict[str, str]]] = defaultdict(list)
    tokens_by_surface: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in tokens:
        by_line[row["locus"]].append(row)
        tokens_by_surface[row["eva"]].append(row)
    for line in by_line.values():
        line.sort(key=lambda row: int(row["token_index"]))
    cross_by_locus = {row["locus"]: row for row in cross}
    if len(by_line) != 4128:
        raise RuntimeError("physical-line census drift")
    for locus, line in by_line.items():
        if locus not in cross_by_locus or " ".join(row["eva"] for row in line) != cross_by_locus[locus]["zl3b_clean"]:
            raise RuntimeError(f"guarded token/cross mismatch: {locus}")

    base_dictionary = read_tsv(ROOT / G661 / "artifacts/WORKING_DICTIONARY_V38.tsv")
    base_glossary_rows = read_tsv(ROOT / G661 / "artifacts/V38_WORKING_TOKEN_GLOSSARY.tsv")
    base_coverage = read_tsv(ROOT / G661 / "artifacts/ALL_LINE_CONCRETE_COVERAGE_V38.tsv")
    base_complete = read_tsv(ROOT / G661 / "artifacts/COMPLETE_PASSAGES_V38.tsv")
    base_one = read_tsv(ROOT / G661 / "artifacts/ONE_UNKNOWN_PASSAGES_V38.tsv")
    frontier = read_tsv(ROOT / G661 / "artifacts/NEWLY_EXPOSED_ONE_HOLE_LINES.tsv")
    y_occurrences = read_tsv(ROOT / g661.g660.G659 / "artifacts/Y_OCCURRENCE_CENSUS.tsv")
    inherited_g660 = read_tsv(ROOT / g661.G660 / "artifacts/ALL_OCCURRENCE_SEMANTIC_AUDIT.tsv")
    inherited_g661 = read_tsv(ROOT / G661 / "artifacts/ALL_OCCURRENCE_SEMANTIC_AUDIT.tsv")
    dimensions = (len(base_dictionary), len(base_glossary_rows), len(base_coverage), len(base_complete), len(base_one), len(frontier))
    if dimensions != (678, 556, 4128, 233, 290, 78):
        raise RuntimeError(f"V38 base dimensions drift: {dimensions!r}")
    frontier_order = tuple(dict.fromkeys(row["unknown_surface"] for row in frontier))
    if frontier_order != TARGET_ORDER or len(TARGET_SURFACES) != 76:
        raise RuntimeError("the seventy-six frontier surfaces or fixed order drifted")
    base_glossary = {row["surface"]: row for row in base_glossary_rows}
    if any(surface in base_glossary for surface in TARGET_SURFACES):
        raise RuntimeError("a GDT662 target unexpectedly already has a V38 glossary row")
    y_occurrence_by_token = {(row["locus"], int(row["token_index"])): row for row in y_occurrences}
    inherited_target_by_token: dict[tuple[str, int], dict[str, object]] = {}
    for row in (*inherited_g660, *inherited_g661):
        inherited_target_by_token[(row["locus"], int(row["token_index"]))] = row
    surface_counts = Counter(row["eva"] for row in tokens)
    observed_counts = {surface: surface_counts[surface] for surface in TARGET_ORDER}
    if observed_counts != {surface: EXPECTED_SURFACE_COUNTS[surface] for surface in TARGET_ORDER}:
        raise RuntimeError(f"target surface count drift: {observed_counts!r}")
    if sum(observed_counts.values()) != 861:
        raise RuntimeError("target position count drift")
    exact, normalized = g661.g660.stable_maps(tokens, cross_by_locus)

    occurrences: list[dict[str, object]] = []
    target_by_token: dict[tuple[str, int], dict[str, object]] = {}
    context_counts: Counter[str] = Counter()
    for locus in sorted(by_line):
        line = by_line[locus]
        words = [row["eva"] for row in line]
        for index, token in enumerate(line):
            surface = token["eva"]
            if surface not in TARGET_SURFACES:
                continue
            ordinal = index + 1
            position = position_label(ordinal, len(line))
            key = (locus, int(token["token_index"]))
            left_surface = words[index - 1] if index else "<BOS>"
            right_surface = words[index + 1] if index + 1 < len(line) else "<EOS>"
            klass = rendering_class(surface, position, left_surface, right_surface)
            item: dict[str, object] = {
                "occurrence_id": f"G662-T{len(occurrences) + 1:04d}",
                "page": token["page"], "locus": locus, "token_index": token["token_index"],
                "ordinal": ordinal, "line_length": len(line), "surface": surface,
                "token_kind": token["kind"], "position": position, "section": token["section"],
                "language": token["language"], "hand": token["hand"],
                "family": EXACT_BY_SURFACE[surface]["family"], "card_type": card_type(surface),
                "scope_mode": "EXACT_WHITESPACE_WHOLE_WITH_OPTIONAL_PRACTICAL_RENDER",
                "rendering_class": klass,
                "left_surface": left_surface,
                "right_surface": right_surface,
                "working_gloss_de": EXACT_BY_SURFACE[surface]["working_meaning_de"],
                "working_render_de": occurrence_render(surface, position, left_surface, right_surface),
                "composition": EXACT_BY_SURFACE[surface]["composition"],
                "strongest_rival_de": EXACT_BY_SURFACE[surface]["strongest_rival_de"],
                "reader_exact": exact[key], "split_normalized": normalized[key],
                "all_three_present": cross_by_locus[locus]["all_three_present"],
                "all_present_exact": cross_by_locus[locus]["all_present_exact"],
                "zl3b_line": cross_by_locus[locus]["zl3b_clean"],
                "it2a_line": cross_by_locus[locus]["it2a_clean"],
                "rf1b_line": cross_by_locus[locus]["rf1b_clean"],
            }
            occurrences.append(item)
            target_by_token[key] = item
            context_counts[klass] += 1
    if len(occurrences) != 861 or len(target_by_token) != 861:
        raise RuntimeError("target occurrence census drift")

    base_by_locus = {row["locus"]: row for row in base_coverage}
    coverage_rows: list[dict[str, object]] = []
    non_target_before: list[tuple[object, ...]] = []
    non_target_after: list[tuple[object, ...]] = []
    affected_loci: set[str] = set()
    for base_row in base_coverage:
        locus = base_row["locus"]
        line = by_line[locus]
        glosses = split_pipe(base_row["token_glosses_de"])
        sources = split_pipe(base_row["gloss_sources"])
        states = split_pipe(base_row["scope_states"])
        if not (len(line) == len(glosses) == len(sources) == len(states)):
            raise RuntimeError(f"V38 token columns misalign: {locus}")
        unknown_pairs = list(zip(parse_compact(base_row["unknown_ordinals"]), parse_compact(base_row["unknown_surfaces"])))
        target_ordinals: set[str] = set()
        for index, token in enumerate(line):
            key = (locus, int(token["token_index"]))
            if key not in target_by_token:
                non_target_before.append((locus, index + 1, token["eva"], glosses[index], sources[index], states[index]))
                continue
            occurrence = target_by_token[key]
            surface = token["eva"]
            if glosses[index] != f"[{surface}:?]" or sources[index] != "OPEN" or states[index] != "UNKNOWN_SURFACE":
                raise RuntimeError(f"V38 target not open at {locus}.{index + 1}: {surface}")
            glosses[index] = str(occurrence["working_gloss_de"])
            sources[index] = f"GDT662:EXACT_WHOLE:{surface}"
            states[index] = "KNOWN_EXACT_WHOLE" if int(occurrence["reader_exact"]) else "READER_BOUNDARY_UNSTABLE"
            target_ordinals.add(str(index + 1))
            affected_loci.add(locus)
        for index, token in enumerate(line):
            if (locus, int(token["token_index"])) not in target_by_token:
                non_target_after.append((locus, index + 1, token["eva"], glosses[index], sources[index], states[index]))
        unknown_pairs = [pair for pair in unknown_pairs if pair[0] not in target_ordinals]
        result = dict(base_row)
        result["known_tokens"] = int(base_row["known_tokens"]) + len(target_ordinals)
        result["context_licensed_tokens"] = states.count("KNOWN_CONTEXT_LICENSED")
        result["ambiguous_tokens"] = states.count("AMBIGUOUS_ACTIVE_RIVAL")
        result["reader_unstable_tokens"] = states.count("READER_BOUNDARY_UNSTABLE")
        result["unknown_tokens"] = len(unknown_pairs)
        result["coverage_fraction"] = f"{int(result['known_tokens']) / int(result['token_count']):.6f}"
        result["token_glosses_de"] = " | ".join(glosses)
        result["gloss_sources"] = " | ".join(sources)
        result["scope_states"] = " | ".join(states)
        result["unknown_ordinals"] = "|".join(pair[0] for pair in unknown_pairs) or "NONE"
        result["unknown_surfaces"] = "|".join(pair[1] for pair in unknown_pairs) or "NONE"
        if int(base_row["unknown_tokens"]) - len(target_ordinals) != len(unknown_pairs):
            raise RuntimeError(f"V38→V39 arithmetic drift: {locus}")
        coverage_rows.append(result)
    if non_target_before != non_target_after:
        raise RuntimeError("a non-target projection changed")
    non_target_sha = canonical_hash(non_target_before)
    coverage_by_locus = {str(row["locus"]): row for row in coverage_rows}

    complete_rows: list[dict[str, object]] = []
    for row in coverage_rows:
        if int(row["unknown_tokens"]) or int(row["token_count"]) < 2:
            continue
        item = dict(row)
        item["strict_complete"] = int(
            int(row["ambiguous_tokens"]) == 0 and int(row["reader_unstable_tokens"]) == 0
            and int(row["all_present_exact"]) == 1
        )
        item["working_translation_de"] = line_translation(
            str(row["locus"]), by_line[str(row["locus"])], split_pipe(row["token_glosses_de"]),
            y_occurrence_by_token, inherited_target_by_token, target_by_token,
        )
        complete_rows.append(item)
    complete_rows.sort(key=lambda row: (-int(row["strict_complete"]), -int(row["token_count"]), str(row["locus"])))
    for rank, row in enumerate(complete_rows, 1):
        row["rank"] = rank

    base_one_by_locus = {row["locus"]: row for row in base_one}
    one_rows: list[dict[str, object]] = []
    for row in coverage_rows:
        if int(row["unknown_tokens"]) != 1 or int(row["known_tokens"]) < 1:
            continue
        ordinal = int(str(row["unknown_ordinals"]))
        surface = str(row["unknown_surfaces"])
        old = base_one_by_locus.get(str(row["locus"]))
        if old and old["unknown_surface"] == surface and int(old["unknown_ordinal"]) == ordinal:
            proposal, basis, strength = old["proposed_default_de"], old["proposal_basis"], old["proposal_strength"]
        else:
            proposal, basis, strength = f"[{surface}:?]", "NEWLY_EXPOSED_BY_GDT662_NO_NEW_CARD", "OPEN"
        strict = int(
            int(row["ambiguous_tokens"]) == 0 and int(row["reader_unstable_tokens"]) == 0
            and int(row["all_present_exact"]) == 1
        )
        score = int(row["known_tokens"]) * 1_000_000 + strict * 10_000 - int(row["token_count"]) * 100
        line = by_line[str(row["locus"])]
        proposed_glosses = split_pipe(row["token_glosses_de"])
        proposed_glosses[ordinal - 1] = proposal
        one_rows.append({
            "rank": 0, "score": score, "strict_eligible": strict, **row,
            "unknown_ordinal": ordinal, "unknown_surface": surface,
            "previous": "<BOS>" if ordinal == 1 else line[ordinal - 2]["eva"],
            "following": "<EOS>" if ordinal == len(line) else line[ordinal]["eva"],
            "proposed_default_de": proposal, "proposal_basis": basis, "proposal_strength": strength,
            "proposed_complete_translation_de": line_translation(
                str(row["locus"]), line, proposed_glosses, y_occurrence_by_token,
                inherited_target_by_token, target_by_token,
            ),
        })
    one_rows.sort(key=lambda row: (-int(row["score"]), str(row["locus"])))
    for rank, row in enumerate(one_rows, 1):
        row["rank"] = rank

    glossary_rows: list[dict[str, object]] = [dict(row) for row in base_glossary_rows]
    dictionary_rows: list[dict[str, object]] = [dict(row) for row in base_dictionary]
    for spec_row in EXACT_WHOLE_SPECS:
        surface = spec_row["surface"]
        glossary_rows.append({
            "surface": surface, "working_meaning_de": spec_row["working_meaning_de"],
            "source": "GDT662:EXACT_WHOLE", "strength": card_strength(surface),
            "scope_state": "KNOWN_EXACT_WHOLE", "priority": 225,
        })
        dictionary_rows.append({
            "entry": f"{surface}@GDT662_EXACT_WHOLE", "kind": card_type(surface),
            "working_meaning_de": spec_row["working_meaning_de"], "composition": spec_row["composition"],
            "context_rule": "only the exact whitespace-delimited surface; no substring inheritance",
            "status": "NEW_V39_PROVISIONAL_CONCRETE_RECIPE_DEFAULT",
        })
    glossary_rows.sort(key=lambda row: str(row["surface"]))
    if len(glossary_rows) != 632:
        raise RuntimeError("V39 glossary dimension drift")

    context_cards: list[dict[str, object]] = []
    for klass, surface in sorted({(str(row["rendering_class"]), str(row["surface"])) for row in occurrences}):
        if klass == "EXACT_WHOLE":
            continue
        members = [row for row in occurrences if row["rendering_class"] == klass and row["surface"] == surface]
        context_cards.append({
            "card_id": f"G662-C{len(context_cards) + 1:02d}", "rendering_class": klass,
            "surface": surface, "occurrences": len(members), "working_render_de": members[0]["working_render_de"],
            "selection_rule": "exact token equality; position only where named in the rendering class",
            "semantic_effect": "practical German rendering; exact whole default and source surface remain visible",
        })
        dictionary_rows.append({
            "entry": f"{surface}@GDT662_{klass}", "kind": "PRACTICAL_RENDERING_CARD",
            "working_meaning_de": members[0]["working_render_de"], "composition": klass,
            "context_rule": "exact token equality; position only where named in the rendering class",
            "status": "NEW_V39_RENDER_OF_EXACT_WHOLE",
        })

    architecture_rows: list[dict[str, object]] = []
    for kind in ("PRODUCTIVE_COMPOUND", "LEARNED_FUNCTION_WORD", "LEARNED_WHOLE", "HYBRID_EXACT"):
        surfaces = [surface for surface in TARGET_ORDER if card_type(surface) == kind]
        architecture_rows.append({
            "card_type": kind, "surface_types": len(surfaces),
            "positions": sum(EXPECTED_SURFACE_COUNTS[surface] for surface in surfaces),
            "surfaces": "|".join(surfaces),
            "dispatch_rule": "exact whole only; component analysis is explanatory, never automatic substring export",
        })

    base_complete_loci = {row["locus"] for row in base_complete}
    newly_completed = [dict(row) for row in complete_rows if row["locus"] not in base_complete_loci]
    newly_completed.sort(key=lambda row: str(row["locus"]))
    for rank, row in enumerate(newly_completed, 1):
        row["rank"] = rank
    base_one_loci = {row["locus"] for row in base_one}
    newly_one = [dict(row) for row in one_rows if row["locus"] not in base_one_loci]
    newly_one.sort(key=lambda row: str(row["locus"]))
    for rank, row in enumerate(newly_one, 1):
        row["rank"] = rank
        row["base_unknown_tokens"] = base_by_locus[str(row["locus"])]["unknown_tokens"]

    audit_rows: list[dict[str, object]] = []
    reader_rows: list[dict[str, object]] = []
    for occurrence in occurrences:
        locus, ordinal = str(occurrence["locus"]), int(occurrence["ordinal"])
        base_row, final_row = base_by_locus[locus], coverage_by_locus[locus]
        audit_rows.append({
            **occurrence,
            "v38_gloss_de": split_pipe(base_row["token_glosses_de"])[ordinal - 1],
            "v39_gloss_de": split_pipe(final_row["token_glosses_de"])[ordinal - 1],
            "v38_scope_state": split_pipe(base_row["scope_states"])[ordinal - 1],
            "v39_scope_state": split_pipe(final_row["scope_states"])[ordinal - 1],
            "v39_working_translation_de": line_translation(
                locus, by_line[locus], split_pipe(final_row["token_glosses_de"]),
                y_occurrence_by_token, inherited_target_by_token, target_by_token,
            ),
            "exact_surface_dispatch": 1, "substring_dispatch": 0,
        })
        reader_rows.append({
            "occurrence_id": occurrence["occurrence_id"], "page": occurrence["page"], "locus": locus,
            "ordinal": ordinal, "surface": occurrence["surface"], "position": occurrence["position"],
            "reader_exact": occurrence["reader_exact"], "split_normalized": occurrence["split_normalized"],
            "all_present_exact": occurrence["all_present_exact"], "zl3b_line": occurrence["zl3b_line"],
            "it2a_line": occurrence["it2a_line"], "rf1b_line": occurrence["rf1b_line"],
            "claim_boundary": "reader agreement conditions confidence only; it does not identify plaintext",
        })
    if any(str(row["v38_gloss_de"]) != f"[{row['surface']}:?]" for row in audit_rows):
        raise RuntimeError("not every target occurrence was open in V38")
    if any(GENERIC_FILLER.search(str(row["v39_gloss_de"])) for row in audit_rows):
        raise RuntimeError("generic work filler leaked into GDT662")

    decision_rows: list[dict[str, object]] = []
    accepted_rows: list[dict[str, object]] = []
    for index, spec_row in enumerate(EXACT_WHOLE_SPECS, 1):
        surface = spec_row["surface"]
        members = [row for row in occurrences if row["surface"] == surface]
        decision_rows.append({
            "decision_id": f"G662-D{index:02d}", "surface": surface, "family": spec_row["family"],
            "card_type": card_type(surface), "working_default_de": spec_row["working_meaning_de"],
            "composition": spec_row["composition"], "strongest_rival_de": spec_row["strongest_rival_de"],
            "occurrences": len(members), "lines": len({row["locus"] for row in members}),
            "pages": len({row["page"] for row in members}),
            "reader_exact_occurrences": sum(int(row["reader_exact"]) for row in members),
            "split_normalized_occurrences": sum(int(row["split_normalized"]) for row in members),
            "rendering_classes": "|".join(sorted({str(row["rendering_class"]) for row in members})),
            "strength": card_strength(surface), "status": "ACCEPT_V39_REPLACEABLE_NO_SUBSTRING_EXPORT",
        })
        accepted_rows.append({
            "surface": surface, "working_meaning_de": spec_row["working_meaning_de"],
            "composition": spec_row["composition"], "strongest_rival_de": spec_row["strongest_rival_de"],
            "card_type": card_type(surface), "strength": card_strength(surface), "occurrences": len(members),
            "scope": "EXACT_WHITESPACE_DELIMITED_WHOLE", "status": "ACCEPT_V39_REPLACEABLE_NO_SUBSTRING_EXPORT",
        })

    family_rows: list[dict[str, object]] = []
    for family in sorted({row["family"] for row in EXACT_WHOLE_SPECS}):
        for surface in [row["surface"] for row in EXACT_WHOLE_SPECS if row["family"] == family]:
            members = tokens_by_surface[surface]
            family_rows.append({
                "family": family, "surface": surface, "card_type": card_type(surface),
                "occurrences": len(members), "lines": len({row["locus"] for row in members}),
                "pages": len({row["page"] for row in members}),
                "working_default_de": EXACT_BY_SURFACE[surface]["working_meaning_de"],
                "composition": EXACT_BY_SURFACE[surface]["composition"],
                "claim_scope": "exact whole; composition predicts relatives only as an explicit future proposal",
            })

    target_line_rows: list[dict[str, object]] = []
    for locus in sorted(affected_loci):
        members = [row for row in occurrences if row["locus"] == locus]
        base_row, final_row = base_by_locus[locus], coverage_by_locus[locus]
        target_line_rows.append({
            "page": final_row["page"], "locus": locus, "section": final_row["section"],
            "target_occurrences": len(members), "target_ordinals": "|".join(str(row["ordinal"]) for row in members),
            "target_surfaces": "|".join(str(row["surface"]) for row in members),
            "rendering_classes": "|".join(str(row["rendering_class"]) for row in members),
            "zl3b_line": final_row["zl3b_line"], "v38_token_glosses_de": base_row["token_glosses_de"],
            "v39_token_glosses_de": final_row["token_glosses_de"],
            "v39_working_translation_de": line_translation(
                locus, by_line[locus], split_pipe(final_row["token_glosses_de"]),
                y_occurrence_by_token, inherited_target_by_token, target_by_token,
            ),
            "v38_unknown_tokens": base_row["unknown_tokens"], "v39_unknown_tokens": final_row["unknown_tokens"],
            "v39_complete": int(int(final_row["unknown_tokens"]) == 0),
        })

    frontier_rows: list[dict[str, object]] = []
    for row in frontier:
        surface, locus = row["unknown_surface"], row["locus"]
        final_row = coverage_by_locus[locus]
        frontier_rows.append({
            "rank": row["rank"], "page": row["page"], "locus": locus, "surface": surface,
            "working_default_de": EXACT_BY_SURFACE[surface]["working_meaning_de"],
            "practical_render_de": occurrence_render(
                surface,
                position_label(int(row["unknown_ordinal"]), int(row["token_count"])),
                str(row["previous"]),
                str(row["following"]),
            ),
            "card_type": card_type(surface), "composition": EXACT_BY_SURFACE[surface]["composition"],
            "strongest_rival_de": EXACT_BY_SURFACE[surface]["strongest_rival_de"], "strength": card_strength(surface),
            "zl3b_line": row["zl3b_line"], "v38_translation_de": row["proposed_complete_translation_de"],
            "v39_translation_de": line_translation(
                locus, by_line[locus], split_pipe(final_row["token_glosses_de"]),
                y_occurrence_by_token, inherited_target_by_token, target_by_token,
            ),
            "status": "COMPLETE_WITH_PROVISIONAL_CONCRETE_DEFAULT",
        })
    if len(frontier_rows) != 78 or any(f"[{row['surface']}:?]" in str(row["v39_translation_de"]) for row in frontier_rows):
        raise RuntimeError("a GDT661 frontier slot remained open")

    base_metrics = metrics(base_coverage, base_one, base_complete, base_glossary_rows)
    final_metrics = metrics(coverage_rows, one_rows, complete_rows, glossary_rows)
    expected_base = {
        "physical_lines": 4128, "known_token_positions": 18451, "unknown_token_positions": 13888,
        "complete_multi_token_lines": 233, "strict_complete_lines": 99,
        "one_unknown_lines": 290, "strict_one_unknown_lines": 73, "working_glossary_surfaces": 556,
    }
    if base_metrics != expected_base:
        raise RuntimeError(f"V38 base metrics drift: {base_metrics!r}")
    round_rows = [
        {"version": "V38", "added_cards": "BASE", "dictionary_entries": len(base_dictionary), **base_metrics},
        {"version": "V39", "added_cards": f"76_EXACT_WHOLES+{len(context_cards)}_RENDERINGS",
         "dictionary_entries": len(dictionary_rows), **final_metrics},
    ]

    coverage_fields, complete_fields, one_fields = list(base_coverage[0]), list(base_complete[0]), list(base_one[0])
    write_tsv(output_dir / "PAGE_ALLOWLIST.tsv", [{"page": page} for page in sorted(pages)], ("page",))
    write_tsv(output_dir / "TARGET_DECISION_DECK.tsv", decision_rows, list(decision_rows[0]))
    write_tsv(output_dir / "ACCEPTED_WHOLE_SURFACE_DEFAULTS.tsv", accepted_rows, list(accepted_rows[0]))
    write_tsv(output_dir / "CONTEXT_RENDERING_CARDS.tsv", context_cards, list(context_cards[0]))
    write_tsv(output_dir / "CARD_ARCHITECTURE_SUMMARY.tsv", architecture_rows, list(architecture_rows[0]))
    write_tsv(output_dir / "ALL_OCCURRENCE_SEMANTIC_AUDIT.tsv", audit_rows, list(audit_rows[0]))
    write_tsv(output_dir / "READER_VARIANT_AUDIT.tsv", reader_rows, list(reader_rows[0]))
    write_tsv(output_dir / "FAMILY_COMPOSITION_ATLAS.tsv", family_rows, list(family_rows[0]))
    write_tsv(output_dir / "FRONTIER_76_COMPLETIONS.tsv", frontier_rows, list(frontier_rows[0]))
    write_tsv(output_dir / "TARGET_LINE_TRANSLATIONS.tsv", target_line_rows, list(target_line_rows[0]))
    write_tsv(output_dir / "ROUND_COVERAGE_COUNTS.tsv", round_rows, list(round_rows[0]))
    write_tsv(output_dir / "NEWLY_COMPLETED_LINES.tsv", newly_completed, complete_fields)
    write_tsv(output_dir / "NEWLY_EXPOSED_ONE_HOLE_LINES.tsv", newly_one, ["base_unknown_tokens", *one_fields])
    write_tsv(output_dir / "V39_WORKING_TOKEN_GLOSSARY.tsv", glossary_rows, list(base_glossary_rows[0]))
    write_tsv(output_dir / "WORKING_DICTIONARY_V39.tsv", dictionary_rows, list(base_dictionary[0]))
    write_tsv(output_dir / "ALL_LINE_CONCRETE_COVERAGE_V39.tsv", coverage_rows, coverage_fields)
    write_tsv(output_dir / "COMPLETE_PASSAGES_V39.tsv", complete_rows, complete_fields)
    write_tsv(output_dir / "ONE_UNKNOWN_PASSAGES_V39.tsv", one_rows, one_fields)

    input_paths = (
        G661 / "REPORT.md", G661 / "artifacts/RESULT.json", G661 / "artifacts/PAGE_ALLOWLIST.tsv",
        G661 / "artifacts/V38_WORKING_TOKEN_GLOSSARY.tsv", G661 / "artifacts/WORKING_DICTIONARY_V38.tsv",
        G661 / "artifacts/ALL_LINE_CONCRETE_COVERAGE_V38.tsv", G661 / "artifacts/COMPLETE_PASSAGES_V38.tsv",
        G661 / "artifacts/ONE_UNKNOWN_PASSAGES_V38.tsv", G661 / "artifacts/NEWLY_EXPOSED_ONE_HOLE_LINES.tsv",
        G661 / "artifacts/ALL_OCCURRENCE_SEMANTIC_AUDIT.tsv", g661.G660 / "artifacts/ALL_OCCURRENCE_SEMANTIC_AUDIT.tsv",
        g661.g660.G659 / "artifacts/Y_OCCURRENCE_CENSUS.tsv", TOKENS_REL, CROSS_REL,
    )
    output_paths = [output_dir / name for name in OUTPUT_NAMES]
    result_core: dict[str, object] = {
        "schema": "GDT662_SEVENTY_SIX_RESIDUAL_FAMILY_COMPLETION_RESULT_V1",
        "experiment_id": "GDT662", "status": STATUS,
        "guard": {
            "allowed_pages": len(pages), "f1r": "EXCLUDED_BY_EXACT_ALLOWLIST", "f84": "FORBIDDEN",
            "f84r": "FORBIDDEN", "new_pages": 0, "new_images": 0,
            "token_query": token_stats, "cross_query": cross_stats,
        },
        "targets": {
            "surface_types": len(TARGET_SURFACES), "exact_whole_surfaces": len(EXACT_WHOLE_SPECS),
            "positions": len(occurrences), "lines": len(affected_loci), "pages": len({row["page"] for row in occurrences}),
            "surface_counts": observed_counts,
            "reader_exact_positions": sum(int(row["reader_exact"]) for row in occurrences),
            "split_normalized_positions": sum(int(row["split_normalized"]) for row in occurrences),
            "rendering_classes": dict(sorted(context_counts.items())), "all_positions_concrete": True,
            "substring_dispatch_positions": 0,
        },
        "architecture": {
            row["card_type"]: {"surface_types": row["surface_types"], "positions": row["positions"]}
            for row in architecture_rows
        },
        "coverage": {
            "base": base_metrics, "final": final_metrics, "affected_lines": len(affected_loci),
            "newly_completed_lines": len(newly_completed), "newly_completed_loci": sorted(row["locus"] for row in newly_completed),
            "newly_exposed_one_hole_lines": len(newly_one), "newly_exposed_one_hole_loci": sorted(row["locus"] for row in newly_one),
            "non_target_token_positions_unchanged": len(non_target_before),
            "non_target_before_sha256": non_target_sha, "non_target_after_sha256": canonical_hash(non_target_after),
            "non_target_exactly_unchanged": True,
        },
        "working_dictionary": {
            "v38_entries": len(base_dictionary), "v39_entries": len(dictionary_rows),
            "added_exact_whole_entries": len(EXACT_WHOLE_SPECS), "added_rendering_entries": len(context_cards),
            "v38_glossary_surfaces": len(base_glossary_rows), "v39_glossary_surfaces": len(glossary_rows),
        },
        "frontier": {"source_rows": len(frontier), "completed_rows": len(frontier_rows), "unfilled_target_slots": 0},
        "determinism_contract": {
            "builder_supports_artifact_dir_cli": True, "exact_whole_dispatch_requires_token_equality": True,
            "replay_files": [str(BASE_REL / "artifacts" / name) for name in (*OUTPUT_NAMES, "RESULT.json")],
        },
        "claim_boundary": (
            "Exploratory replaceable concrete defaults for 76 V38 residual whitespace-delimited surfaces at 861 inherited positions. "
            "The mixed register contains productive compounds, three learned function words, four learned wholes and exact hybrids. "
            "Practical actions such as erhitzen, trocknen, mischen and abseihen are working readings, not confirmed plaintext. "
            "No substring dispatch, glyph identity, phonetics, language, exact ingredient, disease, new page, image, f1r, f84 or f84r is asserted."
        ),
        "inputs": {str(path): sha256(ROOT / path) for path in input_paths},
        "outputs": {str(BASE_REL / "artifacts" / path.name): sha256(path) for path in output_paths},
    }
    result = {**result_core, "content_sha256": canonical_hash(result_core)}
    (output_dir / "RESULT.json").write_text(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return result


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--artifact-dir", type=Path, default=ART)
    args = parser.parse_args(argv)
    result = build(args.artifact_dir)
    if args.artifact_dir.resolve() == ART.resolve():
        with tempfile.TemporaryDirectory(prefix="gdt662_replay_") as directory:
            replay_dir = Path(directory)
            replay_result = build(replay_dir)
            if replay_result != result:
                raise RuntimeError("tempdir RESULT replay differs")
            for name in (*OUTPUT_NAMES, "RESULT.json"):
                if (ART / name).read_bytes() != (replay_dir / name).read_bytes():
                    raise RuntimeError(f"tempdir replay differs: {name}")
    print(
        f"GDT662 built: targets={result['targets']['positions']} wholes=76 "
        f"known={result['coverage']['final']['known_token_positions']} "
        f"complete={result['coverage']['final']['complete_multi_token_lines']} "
        f"one_hole={result['coverage']['final']['one_unknown_lines']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
