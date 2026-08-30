#!/usr/bin/env python3
"""Build GDT652: migrate four exact-anchored preparation grids into V29."""
from __future__ import annotations

import csv
import hashlib
import importlib.util
import json
import re
import sys
from collections import Counter
from pathlib import Path
from typing import Iterable

sys.dont_write_bytecode = True


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
BASE_REL = Path("experiments/yolo/gdt652_strict_v28_frontier_completion")
ART = ROOT / BASE_REL / "artifacts"
G651 = Path("experiments/yolo/gdt651_ckh_four_shell_family_migration")
G651_RUN = G651 / "src/run.py"
G651_ALLOW = G651 / "artifacts/PAGE_ALLOWLIST.tsv"
G651_COVERAGE = G651 / "artifacts/ALL_LINE_CONCRETE_COVERAGE_V28.tsv"
G651_COMPLETE = G651 / "artifacts/COMPLETE_PASSAGES_V28.tsv"
G651_ONE = G651 / "artifacts/ONE_UNKNOWN_PASSAGES_V28.tsv"
G651_GLOSSARY = G651 / "artifacts/V28_EXACT_TOKEN_GLOSSARY.tsv"
G651_DICTIONARY = G651 / "artifacts/WORKING_DICTIONARY_V28.tsv"
G651_RESULT = G651 / "artifacts/RESULT.json"
G651_REPORT = G651 / "REPORT.md"
G624_REPORT = Path("experiments/yolo/gdt624_productive_quality_shell_grid/REPORT.md")
G632_REPORT = Path("experiments/yolo/gdt632_cth_interfix_lattice/REPORT.md")
G633_REPORT = Path("experiments/yolo/gdt633_cth_interfix_semantic_contrasts/REPORT.md")
G647_REPORT = Path("experiments/yolo/gdt647_quality_subdegree_family_migration/REPORT.md")
G650_REPORT = Path("experiments/yolo/gdt650_v26_strict_family_completion/REPORT.md")

spec = importlib.util.spec_from_file_location("gdt651_builder_for_gdt652", ROOT / G651_RUN)
if spec is None or spec.loader is None:
    raise RuntimeError("cannot load GDT651 builder")
g651 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(g651)
g637 = g651.g637
TOKENS_REL = g651.TOKENS_REL
CROSS_REL = g651.CROSS_REL
COVERAGE_FIELDS = g651.COVERAGE_FIELDS
ONE_FIELDS = g651.ONE_FIELDS

STATUS = "PASS_35_EXACT_WHOLES__V29_PREPARATION_AND_MATERIA_GRIDS"
GENERIC_FILLER = re.compile(
    r"arbeitsgut|arbeitschritt|arbeitsschritt|arbeitsmittel|arbeitsstoff|"
    r"arbeitsobjekt|werkzeug|produkt weiter|f.hre .* aus|leite .* weiter",
    re.IGNORECASE,
)

# The sidequest explicitly permits replaceable meanings before proof. Every
# value remains bound to one complete observed surface. CKH_LEARNED, O_PREP,
# E_ATTR and the tail labels are structural tags, never exported free words.
def card(
    surface: str,
    family: str,
    tier: str,
    meaning: str,
    composition: str,
    rival: str,
    basis: str,
    counterargument: str,
    source_locus: str = "NONE",
) -> dict[str, str]:
    return {
        "surface": surface,
        "source_locus": source_locus,
        "strict_source": "0" if source_locus == "NONE" else "1",
        "family": family,
        "tier": tier,
        "working_meaning_de": meaning,
        "composition": composition,
        "rival_de": rival,
        "decision_basis": basis,
        "counterargument": counterargument,
    }


NEUTRAL_CKH_BASIS = (
    "observed exact-anchored member of the seventy-token quality-neutral CKH ladder beside four V28 qualified CKH shells"
)
NEUTRAL_CKH_COUNTER = (
    "Arzneikompositum is a learned family noun and a missing quality head may instead signal a distinct CKH register"
)
O_CKH_BASIS = (
    "observed exact-anchored O_PREP plus CKH_LEARNED cell; O CKH reader splits expose the same preparation boundary"
)
O_CKH_COUNTER = (
    "the preparation parse is compositional and does not independently identify the learned CKH object noun"
)
QUALIFIED_O_CKH_BASIS = (
    "observed exact-anchored cell in the populated CH/SH by E_ATTR by O_PREP plus CKH lattice, with three independent reader-split bridges"
)
QUALIFIED_O_CKH_COUNTER = (
    "the outer quality and preparation shells are inherited from sister grids rather than decoded afresh in every CKH token"
)
QUALIFIED_O_K_BASIS = (
    "observed exact-anchored cell in the eighty-eight-token qualified O_PREP plus K_HEISS grid, anchored by the complete six-cell OK ladder"
)
QUALIFIED_O_K_COUNTER = (
    "the whole is not directly split at every surface and the outer quality shell remains a learned compositional value"
)
O_AL_BASIS = (
    "observed exact-anchored member of the complete O plus P/S/R/L plus AL set beside already concrete PAL/SAL/RAL/LAL materia heads"
)
O_AL_COUNTER = (
    "AL may encode an item or measure form rather than raw state, and ORAL/OLAL admit rival internal segmentations"
)

CANDIDATE_SPECS = (
    card("ckhy", "QUALITY_NEUTRAL_CKH_GRID", "STRONG_NEUTRAL_CKH_FAMILY",
         "Arzneikompositum am Gradanfang", "CKH_LEARNED+y",
         "Arzneizubereitung am Gradanfang, Qualität nicht genannt", NEUTRAL_CKH_BASIS,
         NEUTRAL_CKH_COUNTER, "f9v.12"),
    card("ckhey", "QUALITY_NEUTRAL_CKH_GRID", "STRONG_NEUTRAL_CKH_FAMILY",
         "Arzneikompositum in der Gradmitte", "CKH_LEARNED+e+y",
         "Arzneizubereitung in der Gradmitte, Qualität nicht genannt", NEUTRAL_CKH_BASIS,
         NEUTRAL_CKH_COUNTER),
    card("ckheey", "QUALITY_NEUTRAL_CKH_GRID", "STRONG_NEUTRAL_CKH_FAMILY",
         "Arzneikompositum am Gradende", "CKH_LEARNED+ee+y",
         "Arzneizubereitung am Gradende, Qualität nicht genannt", NEUTRAL_CKH_BASIS,
         NEUTRAL_CKH_COUNTER),
    card("ckhdy", "QUALITY_NEUTRAL_CKH_GRID", "PROVISIONAL_LOW_N_CKH_FAMILY",
         "Arzneikompositum am Gradanfang, abgeschlossen", "CKH_LEARNED+d+y",
         "Arzneizubereitung am Gradanfang, abgeschlossen", NEUTRAL_CKH_BASIS,
         "one of four tokens is all-reader exact; " + NEUTRAL_CKH_COUNTER),
    card("ckhedy", "QUALITY_NEUTRAL_CKH_GRID", "PROVISIONAL_LOW_N_CKH_FAMILY",
         "Arzneikompositum in der Gradmitte, abgeschlossen", "CKH_LEARNED+e+d+y",
         "Arzneizubereitung in der Gradmitte, abgeschlossen", NEUTRAL_CKH_BASIS,
         "one of two tokens is all-reader exact; " + NEUTRAL_CKH_COUNTER),

    card("ockhy", "O_PREP_CKH_GRID", "STRONG_BOUNDARY_COMPOUND",
         "Ansatz eines Arzneikompositums am Gradanfang", "O_PREP+CKH_LEARNED+y",
         "zubereitetes Arzneikompositum am Gradanfang", O_CKH_BASIS, O_CKH_COUNTER),
    card("ockhey", "O_PREP_CKH_GRID", "STRONG_BOUNDARY_COMPOUND",
         "Ansatz eines Arzneikompositums in der Gradmitte", "O_PREP+CKH_LEARNED+e+y",
         "zubereitetes Arzneikompositum in der Gradmitte", O_CKH_BASIS, O_CKH_COUNTER),
    card("ockhedy", "O_PREP_CKH_GRID", "PROVISIONAL_LOW_N_BOUNDARY_COMPOUND",
         "Ansatz eines Arzneikompositums in der Gradmitte, abgeschlossen", "O_PREP+CKH_LEARNED+e+d+y",
         "zubereitetes Arzneikompositum in der Gradmitte, abgeschlossen", O_CKH_BASIS, O_CKH_COUNTER),

    card("chockhy", "QUALIFIED_O_PREP_CKH_GRID", "STRONG_COMPONENT_GRID",
         "Arzneikompositum im Trockenansatz am Gradanfang", "ch+O_PREP+CKH_LEARNED+y",
         "trocken zubereitetes Arzneikompositum am Gradanfang", QUALIFIED_O_CKH_BASIS,
         QUALIFIED_O_CKH_COUNTER),
    card("chockhey", "QUALIFIED_O_PREP_CKH_GRID", "STRONG_COMPONENT_GRID",
         "Arzneikompositum im Trockenansatz in der Gradmitte", "ch+O_PREP+CKH_LEARNED+e+y",
         "trocken zubereitetes Arzneikompositum in der Gradmitte", QUALIFIED_O_CKH_BASIS,
         QUALIFIED_O_CKH_COUNTER),
    card("chockhedy", "QUALIFIED_O_PREP_CKH_GRID", "PROVISIONAL_LOW_N_COMPONENT_GRID",
         "Arzneikompositum im Trockenansatz in der Gradmitte, abgeschlossen", "ch+O_PREP+CKH_LEARNED+e+d+y",
         "trocken zubereitetes Arzneikompositum in der Gradmitte, abgeschlossen", QUALIFIED_O_CKH_BASIS,
         QUALIFIED_O_CKH_COUNTER),
    card("cheockhy", "QUALIFIED_O_PREP_CKH_GRID", "STRONG_COMPONENT_GRID",
         "trocken angesetztes Arzneikompositum am Gradanfang", "ch+E_ATTR+O_PREP+CKH_LEARNED+y",
         "trocken gebundene CKH-Zubereitung am Gradanfang", QUALIFIED_O_CKH_BASIS,
         QUALIFIED_O_CKH_COUNTER, "f107v.7"),
    card("cheockhey", "QUALIFIED_O_PREP_CKH_GRID", "PROVISIONAL_LOW_N_COMPONENT_GRID",
         "trocken angesetztes Arzneikompositum in der Gradmitte", "ch+E_ATTR+O_PREP+CKH_LEARNED+e+y",
         "trocken gebundene CKH-Zubereitung in der Gradmitte", QUALIFIED_O_CKH_BASIS,
         QUALIFIED_O_CKH_COUNTER),
    card("shockhy", "QUALIFIED_O_PREP_CKH_GRID", "STRONG_COMPONENT_GRID",
         "Arzneikompositum im Feuchtansatz am Gradanfang", "sh+O_PREP+CKH_LEARNED+y",
         "feucht zubereitetes Arzneikompositum am Gradanfang", QUALIFIED_O_CKH_BASIS,
         QUALIFIED_O_CKH_COUNTER),
    card("shockhey", "QUALIFIED_O_PREP_CKH_GRID", "STRONG_COMPONENT_GRID",
         "Arzneikompositum im Feuchtansatz in der Gradmitte", "sh+O_PREP+CKH_LEARNED+e+y",
         "feucht zubereitetes Arzneikompositum in der Gradmitte", QUALIFIED_O_CKH_BASIS,
         QUALIFIED_O_CKH_COUNTER),
    card("sheockhy", "QUALIFIED_O_PREP_CKH_GRID", "PROVISIONAL_LOW_N_COMPONENT_GRID",
         "feucht angesetztes Arzneikompositum am Gradanfang", "sh+E_ATTR+O_PREP+CKH_LEARNED+y",
         "feucht gebundene CKH-Zubereitung am Gradanfang", QUALIFIED_O_CKH_BASIS,
         QUALIFIED_O_CKH_COUNTER),
    card("sheockhey", "QUALIFIED_O_PREP_CKH_GRID", "PROVISIONAL_LOW_N_COMPONENT_GRID",
         "feucht angesetztes Arzneikompositum in der Gradmitte", "sh+E_ATTR+O_PREP+CKH_LEARNED+e+y",
         "feucht gebundene CKH-Zubereitung in der Gradmitte", QUALIFIED_O_CKH_BASIS,
         QUALIFIED_O_CKH_COUNTER),

    card("chokey", "QUALIFIED_O_PREP_K_GRID", "STRONG_COMPONENT_GRID",
         "heiß-trockener Ansatz in der Gradmitte", "ch+O_PREP+K_HEISS+e+y",
         "Trockenansatz mit heißer Mittelqualität", QUALIFIED_O_K_BASIS,
         QUALIFIED_O_K_COUNTER, "f42v.15"),
    card("chokeey", "QUALIFIED_O_PREP_K_GRID", "STRONG_COMPONENT_GRID",
         "heiß-trockener Ansatz am Gradende", "ch+O_PREP+K_HEISS+ee+y",
         "Trockenansatz mit heißer Endqualität", QUALIFIED_O_K_BASIS, QUALIFIED_O_K_COUNTER),
    card("chokedy", "QUALIFIED_O_PREP_K_GRID", "STRONG_COMPONENT_GRID",
         "heiß-trockener Ansatz in der Gradmitte, abgeschlossen", "ch+O_PREP+K_HEISS+e+d+y",
         "Trockenansatz mit heißer Mittelqualität, abgeschlossen", QUALIFIED_O_K_BASIS,
         QUALIFIED_O_K_COUNTER),
    card("chokeedy", "QUALIFIED_O_PREP_K_GRID", "PROVISIONAL_LOW_N_COMPONENT_GRID",
         "heiß-trockener Ansatz am Gradende, abgeschlossen", "ch+O_PREP+K_HEISS+ee+d+y",
         "Trockenansatz mit heißer Endqualität, abgeschlossen", QUALIFIED_O_K_BASIS,
         QUALIFIED_O_K_COUNTER),
    card("cheoky", "QUALIFIED_O_PREP_K_GRID", "STRONG_COMPONENT_GRID",
         "trocken angesetzte heiße Zubereitung am Gradanfang", "ch+E_ATTR+O_PREP+K_HEISS+y",
         "trocken gebundener heißer Ansatz am Gradanfang", QUALIFIED_O_K_BASIS,
         QUALIFIED_O_K_COUNTER),
    card("cheokey", "QUALIFIED_O_PREP_K_GRID", "PROVISIONAL_LOW_N_COMPONENT_GRID",
         "trocken angesetzte heiße Zubereitung in der Gradmitte", "ch+E_ATTR+O_PREP+K_HEISS+e+y",
         "trocken gebundener heißer Ansatz in der Gradmitte", QUALIFIED_O_K_BASIS,
         QUALIFIED_O_K_COUNTER),
    card("cheokeey", "QUALIFIED_O_PREP_K_GRID", "STRONG_COMPONENT_GRID",
         "trocken angesetzte heiße Zubereitung am Gradende", "ch+E_ATTR+O_PREP+K_HEISS+ee+y",
         "trocken gebundener heißer Ansatz am Gradende", QUALIFIED_O_K_BASIS,
         QUALIFIED_O_K_COUNTER, "f27r.12"),
    card("cheokedy", "QUALIFIED_O_PREP_K_GRID", "PROVISIONAL_LOW_N_COMPONENT_GRID",
         "trocken angesetzte heiße Zubereitung in der Gradmitte, abgeschlossen", "ch+E_ATTR+O_PREP+K_HEISS+e+d+y",
         "trocken gebundener heißer Ansatz in der Gradmitte, abgeschlossen", QUALIFIED_O_K_BASIS,
         QUALIFIED_O_K_COUNTER),
    card("shoky", "QUALIFIED_O_PREP_K_GRID", "STRONG_COMPONENT_GRID",
         "heiß-feuchter Ansatz am Gradanfang", "sh+O_PREP+K_HEISS+y",
         "Feuchtansatz mit heißer Anfangsqualität", QUALIFIED_O_K_BASIS, QUALIFIED_O_K_COUNTER),
    card("shokey", "QUALIFIED_O_PREP_K_GRID", "STRONG_COMPONENT_GRID",
         "heiß-feuchter Ansatz in der Gradmitte", "sh+O_PREP+K_HEISS+e+y",
         "Feuchtansatz mit heißer Mittelqualität", QUALIFIED_O_K_BASIS, QUALIFIED_O_K_COUNTER),
    card("shokeey", "QUALIFIED_O_PREP_K_GRID", "PROVISIONAL_LOW_N_COMPONENT_GRID",
         "heiß-feuchter Ansatz am Gradende", "sh+O_PREP+K_HEISS+ee+y",
         "Feuchtansatz mit heißer Endqualität", QUALIFIED_O_K_BASIS, QUALIFIED_O_K_COUNTER),
    card("sheoky", "QUALIFIED_O_PREP_K_GRID", "STRONG_COMPONENT_GRID",
         "feucht angesetzte heiße Zubereitung am Gradanfang", "sh+E_ATTR+O_PREP+K_HEISS+y",
         "feucht gebundener heißer Ansatz am Gradanfang", QUALIFIED_O_K_BASIS,
         QUALIFIED_O_K_COUNTER),
    card("sheokey", "QUALIFIED_O_PREP_K_GRID", "PROVISIONAL_LOW_N_COMPONENT_GRID",
         "feucht angesetzte heiße Zubereitung in der Gradmitte", "sh+E_ATTR+O_PREP+K_HEISS+e+y",
         "feucht gebundener heißer Ansatz in der Gradmitte", QUALIFIED_O_K_BASIS,
         QUALIFIED_O_K_COUNTER),
    card("sheokeedy", "QUALIFIED_O_PREP_K_GRID", "PROVISIONAL_LOW_N_COMPONENT_GRID",
         "feucht angesetzte heiße Zubereitung am Gradende, abgeschlossen", "sh+E_ATTR+O_PREP+K_HEISS+ee+d+y",
         "feucht gebundener heißer Ansatz am Gradende, abgeschlossen", QUALIFIED_O_K_BASIS,
         QUALIFIED_O_K_COUNTER),

    card("opal", "O_PREP_MATERIA_AL_GRID", "STRONG_MATERIA_COMPOUND",
         "Ansatz aus Pulverrohstoff, Form I", "O_PREP+[PAL_LEARNED]",
         "Pulverzubereitung in der AL-Form", O_AL_BASIS, O_AL_COUNTER, "f75v.50"),
    card("osal", "O_PREP_MATERIA_AL_GRID", "STRONG_MATERIA_COMPOUND",
         "Ansatz aus Saatrohstoff, Form I", "O_PREP+[SAL_LEARNED]",
         "Saatzubereitung in der AL-Form", O_AL_BASIS, O_AL_COUNTER),
    card("oral", "O_PREP_MATERIA_AL_GRID", "EXPLORATORY_RIVAL_SEGMENTATION",
         "Ansatz aus Wurzelrohstoff, Form I", "O_PREP+[RAL_LEARNED]",
         "OR-Anteil in der AL-Form", O_AL_BASIS, O_AL_COUNTER),
    card("olal", "O_PREP_MATERIA_AL_GRID", "EXPLORATORY_RIVAL_SEGMENTATION",
         "Ansatz aus Holzrohstoff, Form I", "O_PREP+[LAL_LEARNED]",
         "OL-Anteil in der AL-Form", O_AL_BASIS, O_AL_COUNTER),
)

REVISION_SPECS: tuple[tuple[str, str, str], ...] = ()

FAMILY_FORMS = tuple(
    (
        str(row["family"]), str(row["surface"]), str(row["composition"]),
        str(row["working_meaning_de"]), "TARGET",
    )
    for row in CANDIDATE_SPECS
) + (
    ("QUALITY_NEUTRAL_CKH_GRID", "ckheedy", "CKH_LEARNED+ee+d+y", "Arzneikompositum am Gradende, abgeschlossen", "ABSENT_PREDICTION"),

    ("O_PREP_CKH_GRID", "ockheey", "O_PREP+CKH_LEARNED+ee+y", "Ansatz eines Arzneikompositums am Gradende", "ABSENT_PREDICTION"),
    ("O_PREP_CKH_GRID", "ockhdy", "O_PREP+CKH_LEARNED+d+y", "Ansatz eines Arzneikompositums am Gradanfang, abgeschlossen", "ABSENT_PREDICTION"),
    ("O_PREP_CKH_GRID", "ockheedy", "O_PREP+CKH_LEARNED+ee+d+y", "Ansatz eines Arzneikompositums am Gradende, abgeschlossen", "ABSENT_PREDICTION"),

    ("QUALIFIED_O_PREP_CKH_GRID", "chockheey", "ch+O_PREP+CKH_LEARNED+ee+y", "Arzneikompositum im Trockenansatz am Gradende", "ABSENT_PREDICTION"),
    ("QUALIFIED_O_PREP_CKH_GRID", "chockhdy", "ch+O_PREP+CKH_LEARNED+d+y", "Arzneikompositum im Trockenansatz am Gradanfang, abgeschlossen", "ZERO_EXACT_HOLD"),
    ("QUALIFIED_O_PREP_CKH_GRID", "chockheedy", "ch+O_PREP+CKH_LEARNED+ee+d+y", "Arzneikompositum im Trockenansatz am Gradende, abgeschlossen", "ABSENT_PREDICTION"),
    ("QUALIFIED_O_PREP_CKH_GRID", "cheockheey", "ch+E_ATTR+O_PREP+CKH_LEARNED+ee+y", "trocken angesetztes Arzneikompositum am Gradende", "ABSENT_PREDICTION"),
    ("QUALIFIED_O_PREP_CKH_GRID", "cheockhdy", "ch+E_ATTR+O_PREP+CKH_LEARNED+d+y", "trocken angesetztes Arzneikompositum am Gradanfang, abgeschlossen", "BRIDGE_ONLY_HOLD"),
    ("QUALIFIED_O_PREP_CKH_GRID", "cheockhedy", "ch+E_ATTR+O_PREP+CKH_LEARNED+e+d+y", "trocken angesetztes Arzneikompositum in der Gradmitte, abgeschlossen", "ABSENT_PREDICTION"),
    ("QUALIFIED_O_PREP_CKH_GRID", "cheockheedy", "ch+E_ATTR+O_PREP+CKH_LEARNED+ee+d+y", "trocken angesetztes Arzneikompositum am Gradende, abgeschlossen", "ABSENT_PREDICTION"),
    ("QUALIFIED_O_PREP_CKH_GRID", "shockheey", "sh+O_PREP+CKH_LEARNED+ee+y", "Arzneikompositum im Feuchtansatz am Gradende", "ABSENT_PREDICTION"),
    ("QUALIFIED_O_PREP_CKH_GRID", "shockhdy", "sh+O_PREP+CKH_LEARNED+d+y", "Arzneikompositum im Feuchtansatz am Gradanfang, abgeschlossen", "ABSENT_PREDICTION"),
    ("QUALIFIED_O_PREP_CKH_GRID", "shockhedy", "sh+O_PREP+CKH_LEARNED+e+d+y", "Arzneikompositum im Feuchtansatz in der Gradmitte, abgeschlossen", "ABSENT_PREDICTION"),
    ("QUALIFIED_O_PREP_CKH_GRID", "shockheedy", "sh+O_PREP+CKH_LEARNED+ee+d+y", "Arzneikompositum im Feuchtansatz am Gradende, abgeschlossen", "ABSENT_PREDICTION"),
    ("QUALIFIED_O_PREP_CKH_GRID", "sheockheey", "sh+E_ATTR+O_PREP+CKH_LEARNED+ee+y", "feucht angesetztes Arzneikompositum am Gradende", "ABSENT_PREDICTION"),
    ("QUALIFIED_O_PREP_CKH_GRID", "sheockhdy", "sh+E_ATTR+O_PREP+CKH_LEARNED+d+y", "feucht angesetztes Arzneikompositum am Gradanfang, abgeschlossen", "ABSENT_PREDICTION"),
    ("QUALIFIED_O_PREP_CKH_GRID", "sheockhedy", "sh+E_ATTR+O_PREP+CKH_LEARNED+e+d+y", "feucht angesetztes Arzneikompositum in der Gradmitte, abgeschlossen", "ZERO_EXACT_HOLD"),
    ("QUALIFIED_O_PREP_CKH_GRID", "sheockheedy", "sh+E_ATTR+O_PREP+CKH_LEARNED+ee+d+y", "feucht angesetztes Arzneikompositum am Gradende, abgeschlossen", "ABSENT_PREDICTION"),

    ("O_PREP_K_CONTROL_LADDER", "oky", "O_PREP+K_HEISS+y", "heißer Ansatz am Gradanfang", "V28_ANCHOR"),
    ("O_PREP_K_CONTROL_LADDER", "okey", "O_PREP+K_HEISS+e+y", "heißer Ansatz in der Gradmitte", "V28_ANCHOR"),
    ("O_PREP_K_CONTROL_LADDER", "okeey", "O_PREP+K_HEISS+ee+y", "heißer Ansatz am Gradende", "V28_ANCHOR"),
    ("O_PREP_K_CONTROL_LADDER", "okdy", "O_PREP+K_HEISS+d+y", "heißer Ansatz am Gradanfang, abgeschlossen", "V28_ANCHOR"),
    ("O_PREP_K_CONTROL_LADDER", "okedy", "O_PREP+K_HEISS+e+d+y", "heißer Ansatz in der Gradmitte, abgeschlossen", "V28_ANCHOR"),
    ("O_PREP_K_CONTROL_LADDER", "okeedy", "O_PREP+K_HEISS+ee+d+y", "heißer Ansatz am Gradende, abgeschlossen", "V28_ANCHOR"),
    ("QUALIFIED_O_PREP_K_GRID", "choky", "ch+O_PREP+K_HEISS+y", "heiß-trockener Ansatz am Gradanfang", "V28_ANCHOR"),
    ("QUALIFIED_O_PREP_K_GRID", "chokdy", "ch+O_PREP+K_HEISS+d+y", "heiß-trockener Ansatz am Gradanfang, abgeschlossen", "ABSENT_PREDICTION"),
    ("QUALIFIED_O_PREP_K_GRID", "cheokdy", "ch+E_ATTR+O_PREP+K_HEISS+d+y", "trocken angesetzte heiße Zubereitung am Gradanfang, abgeschlossen", "ABSENT_PREDICTION"),
    ("QUALIFIED_O_PREP_K_GRID", "cheokeedy", "ch+E_ATTR+O_PREP+K_HEISS+ee+d+y", "trocken angesetzte heiße Zubereitung am Gradende, abgeschlossen", "ABSENT_PREDICTION"),
    ("QUALIFIED_O_PREP_K_GRID", "shokdy", "sh+O_PREP+K_HEISS+d+y", "heiß-feuchter Ansatz am Gradanfang, abgeschlossen", "ABSENT_PREDICTION"),
    ("QUALIFIED_O_PREP_K_GRID", "shokedy", "sh+O_PREP+K_HEISS+e+d+y", "heiß-feuchter Ansatz in der Gradmitte, abgeschlossen", "ABSENT_PREDICTION"),
    ("QUALIFIED_O_PREP_K_GRID", "shokeedy", "sh+O_PREP+K_HEISS+ee+d+y", "heiß-feuchter Ansatz am Gradende, abgeschlossen", "ABSENT_PREDICTION"),
    ("QUALIFIED_O_PREP_K_GRID", "sheokeey", "sh+E_ATTR+O_PREP+K_HEISS+ee+y", "feucht angesetzte heiße Zubereitung am Gradende", "ABSENT_PREDICTION"),
    ("QUALIFIED_O_PREP_K_GRID", "sheokdy", "sh+E_ATTR+O_PREP+K_HEISS+d+y", "feucht angesetzte heiße Zubereitung am Gradanfang, abgeschlossen", "ABSENT_PREDICTION"),
    ("QUALIFIED_O_PREP_K_GRID", "sheokedy", "sh+E_ATTR+O_PREP+K_HEISS+e+d+y", "feucht angesetzte heiße Zubereitung in der Gradmitte, abgeschlossen", "ZERO_EXACT_HOLD"),
)

BRIDGE_SPECS = (
    ("G652-B01", "QUALITY_NEUTRAL_CKH_GRID", "f75v.17", "sheckhy ... ckhy", "qualified and quality-neutral CKH same-line contact"),
    ("G652-B02", "QUALITY_NEUTRAL_CKH_GRID", "f33v.3", "chckhy ... ckhdy", "dry-qualified and completed-neutral CKH same-line contact"),
    ("G652-B03", "QUALITY_NEUTRAL_CKH_GRID", "f34v.2", "chckhdy ... ckhy", "completed-dry and neutral CKH same-line contact"),
    ("G652-B04", "QUALIFIED_O_PREP_CKH_GRID", "f58v.28", "ycheockhy / ycheo ckhy", "reader split exposes CKHY after the CHEO span"),
    ("G652-B05", "QUALITY_NEUTRAL_CKH_GRID", "f30r.12", "ckhey ckhey", "all-reader exact middle-cell repetition"),
    ("G652-B06", "QUALITY_NEUTRAL_CKH_GRID", "f6v.3", "ckhy ... ckhy", "all-reader exact beginning-cell repetition"),
    ("G652-B07", "O_PREP_CKH_GRID", "f40v.15", "o ckhy / ockhy", "reader split directly exposes O_PREP plus CKHY"),
    ("G652-B08", "O_PREP_CKH_GRID", "f99r.48", "ockhey / o ckhey", "reader split directly exposes O_PREP plus CKHEY"),
    ("G652-B09", "QUALIFIED_O_PREP_CKH_GRID", "f51v.12", "cho ckhey / chockhey", "reader split exposes the CHO plus CKHEY composition"),
    ("G652-B10", "QUALIFIED_O_PREP_CKH_GRID", "f115r.6", "cheo ckhdy / cheockhdy", "reader split predicts a bridge-only completed cell without exporting it"),
    ("G652-B11", "QUALIFIED_O_PREP_CKH_GRID", "f104r.23", "sheockhey / sheo ckhey", "reader split exposes the SHEO plus CKHEY composition"),
    ("G652-B12", "QUALIFIED_O_PREP_K_GRID", "f47r.8", "shokeey / sho keey", "reader split exposes the SHO plus KEEY composition"),
    ("G652-B13", "QUALIFIED_O_PREP_K_GRID", "f42v.7", "sheokey / sheo key", "reader split exposes the SHEO plus KEY composition"),
    ("G652-B14", "O_PREP_MATERIA_AL_GRID", "f89v1.24", "opaldaiin / opal daiin", "reader boundary exposes OPAL as one complete unit before DAIIN"),
)

SMOOTHED_SOURCE_LINES = {
    "f9v.12": "Heiß-trocken, Grad III; Arzneikompositum am Gradanfang; Pflanzenteil.",
    "f107v.7": "Kalt, Grad III; trocken angesetztes Arzneikompositum am Gradanfang; trocken, Grad II; heiß, Grad II.",
    "f27r.12": "Gradwert II; Trockenansatz, heiß am Gradende; trocken in der Gradmitte; Blatt-/Krautdroge, Form I; Ansatz aus kaltem Rohstoff, Form I.",
    "f42v.15": "Trockenansatz: heiß in der Gradmitte; Trockengut; heißer Ansatz in der Gradmitte.",
    "f75v.50": "Ansatz aus kaltem Rohstoff, Form I; Ansatz aus Pulverrohstoff, Form I.",
}

OUTPUT_NAMES = (
    "PAGE_ALLOWLIST.tsv", "TARGET_DECISION_DECK.tsv", "FAMILY_EVIDENCE_ATLAS.tsv",
    "BOUNDARY_BRIDGE_ATLAS.tsv", "RISK_AND_RIVAL_REGISTER.tsv", "ALL_OCCURRENCE_SEMANTIC_AUDIT.tsv",
    "READER_VARIANT_AUDIT.tsv", "SEQUENTIAL_DECISION_LEDGER.tsv",
    "ROUND_COVERAGE_COUNTS.tsv", "ACCEPTED_WHOLE_SURFACE_DEFAULTS.tsv",
    "SOURCE_PASSAGE_REALITY_CHECK.tsv", "AFFECTED_LINE_TRANSLATIONS.tsv",
    "NEWLY_COMPLETED_LINES.tsv", "NEWLY_EXPOSED_ONE_HOLE_LINES.tsv",
    "V29_EXACT_TOKEN_GLOSSARY.tsv", "ALL_LINE_CONCRETE_COVERAGE_V29.tsv",
    "COMPLETE_PASSAGES_V29.tsv", "ONE_UNKNOWN_PASSAGES_V29.tsv",
    "WORKING_DICTIONARY_V29.tsv",
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


def string_rows(rows: list[dict[str, object]]) -> list[dict[str, str]]:
    return [{str(key): str(value) for key, value in row.items()} for row in rows]


def split_pipe(value: object) -> list[str]:
    return str(value).split(" | ") if str(value) else []


def metrics(coverage, one_unknown, complete, glossary) -> dict[str, int]:
    return {
        "physical_lines": len(coverage),
        "known_token_positions": sum(int(row["known_tokens"]) for row in coverage),
        "unknown_token_positions": sum(int(row["unknown_tokens"]) for row in coverage),
        "complete_multi_token_lines": len(complete),
        "strict_complete_lines": sum(int(row["strict_complete"]) for row in complete),
        "one_unknown_lines": len(one_unknown),
        "strict_one_unknown_lines": sum(int(row["strict_eligible"]) for row in one_unknown),
        "exact_glossary_surfaces": len(glossary),
    }


def line_position(line: list[dict[str, object]], token_index: int) -> int:
    for ordinal, token in enumerate(line, 1):
        if int(token["token_index"]) == token_index:
            return ordinal
    raise RuntimeError("token position not found")


def dictionary_row(spec_row: dict[str, str], round_number: int, occurrences: int, exact_count: int) -> dict[str, object]:
    return {
        "entry": f"{spec_row['surface']}@GDT652_EXACT_WHOLE",
        "kind": f"EXACT_ZL3B_WHOLE_{spec_row['tier']}",
        "working_meaning_de": spec_row["working_meaning_de"],
        "composition": spec_row["composition"],
        "context_rule": (
            f"exact complete surface only; tier={spec_row['tier']}; {occurrences} audited occurrences; "
            f"{exact_count} all-reader exact; learned components remain family-bound"
        ),
        "status": f"NEW_V29_ACCEPTED_ROUND_{round_number:02d}",
    }


def build(output_dir: Path) -> dict[str, object]:
    output_dir.mkdir(parents=True, exist_ok=True)
    pages = {row["page"] for row in read_tsv(ROOT / G651_ALLOW)}
    if "f1r" in pages or any(page.startswith("f84") for page in pages):
        raise RuntimeError("allow-list contains excluded or forbidden page")
    guarded_query = g637.g636.g635.g634.g633.g632.g631.guarded_query
    token_rows, token_stats = guarded_query(
        TOKENS_REL, pages, "page,locus,token_index,eva,section,language,hand",
    )
    cross_rows, cross_stats = guarded_query(
        CROSS_REL, pages, "page,locus,all_three_present,all_present_exact,zl3b_clean,it2a_clean,rf1b_clean",
    )
    cross_by_locus = {row["locus"]: row for row in cross_rows}
    by_line, _ = g637.g636.g635.g634.g633.g632.g631.line_maps([dict(row) for row in token_rows])
    exact, boundary = g637.g636.g635.g634.stable_maps(token_rows, cross_by_locus)

    base_dictionary = [dict(row) for row in read_tsv(ROOT / G651_DICTIONARY)]
    base_gloss_rows = read_tsv(ROOT / G651_GLOSSARY)
    base_glossary = {row["surface"]: dict(row) for row in base_gloss_rows}
    base_coverage = read_tsv(ROOT / G651_COVERAGE)
    base_complete = read_tsv(ROOT / G651_COMPLETE)
    base_one = read_tsv(ROOT / G651_ONE)
    if (len(base_dictionary), len(base_glossary), len(base_coverage), len(base_complete), len(base_one)) != (450, 379, 4128, 107, 159):
        raise RuntimeError("GDT651 V28 base counts changed")
    replay_coverage, replay_one, _, replay_complete = g637.build_line_coverage(
        by_line, base_glossary, exact, boundary, cross_by_locus,
    )
    if (string_rows(replay_coverage) != string_rows(base_coverage)
            or string_rows(replay_complete) != string_rows(base_complete)
            or string_rows(replay_one) != string_rows(base_one)):
        raise RuntimeError("GDT651 V28 editions do not replay")
    base_metrics = metrics(replay_coverage, replay_one, replay_complete, base_glossary)
    expected_base = {
        "physical_lines": 4128, "known_token_positions": 14741,
        "unknown_token_positions": 17598, "complete_multi_token_lines": 107,
        "strict_complete_lines": 62, "one_unknown_lines": 159,
        "strict_one_unknown_lines": 40, "exact_glossary_surfaces": 379,
    }
    if base_metrics != expected_base:
        raise RuntimeError(f"GDT651 V28 metrics changed: {base_metrics!r}")

    targets = {str(row["surface"]) for row in CANDIDATE_SPECS}
    revision_surfaces = {surface for surface, _, _ in REVISION_SPECS}
    if targets & set(base_glossary):
        raise RuntimeError("a GDT652 target is already in the V28 glossary")
    if revision_surfaces - set(base_glossary) or targets & revision_surfaces:
        raise RuntimeError("GDT652 revision deck no longer matches the V28 glossary")
    strict_source = {str(row["surface"]): str(row["source_locus"]) for row in CANDIDATE_SPECS if row["strict_source"] == "1"}
    source_pairs = {(row["unknown_surface"], row["locus"]): row for row in base_one}
    for surface, locus in strict_source.items():
        source = source_pairs.get((surface, locus))
        if source is None or int(source["strict_eligible"]) != 1:
            raise RuntimeError(f"strict GDT651 source frontier changed: {(surface, locus)}")
    if strict_source != {
            "ckhy": "f9v.12", "cheockhy": "f107v.7",
            "cheokeey": "f27r.12", "chokey": "f42v.15",
            "opal": "f75v.50"}:
        raise RuntimeError("strict source deck changed")
    strict_hole_rows = sorted(
        (row for row in base_one if row["unknown_surface"] in targets and int(row["strict_eligible"]) == 1),
        key=lambda row: row["locus"],
    )
    if [(row["unknown_surface"], row["locus"]) for row in strict_hole_rows] != [
            ("cheockhy", "f107v.7"), ("cheokeey", "f27r.12"),
            ("chokey", "f42v.15"), ("opal", "f75v.50"),
            ("ckhy", "f9v.12")]:
        raise RuntimeError("GDT652 strict-hole frontier changed")

    token_counts = Counter(str(row["eva"]) for row in token_rows)
    family_rows: list[dict[str, object]] = []
    for family, surface, composition, reading, planned_status in FAMILY_FORMS:
        members = [row for row in token_rows if row["eva"] == surface]
        exact_count = sum(exact[row["locus"], int(row["token_index"])] for row in members)
        normalized_count = sum(boundary[row["locus"], int(row["token_index"])] for row in members)
        family_rows.append({
            "family": family, "surface": surface, "composition": composition,
            "predicted_reading_de": reading, "zl3b_occurrences": len(members),
            "pages": len({row["page"] for row in members}),
            "reader_exact_occurrences": exact_count,
            "split_normalized_occurrences": normalized_count,
            "planned_status": planned_status,
            "final_status": (
                "ACCEPTED_V29" if surface in targets else
                "V28_ANCHOR" if surface in base_glossary else
                "ABSENT_HOLD" if not members else planned_status
            ),
        })

    bridge_rows: list[dict[str, object]] = []
    for bridge_id, family, locus, diagnostic, support in BRIDGE_SPECS:
        row = cross_by_locus.get(locus)
        if row is None:
            raise RuntimeError(f"missing bridge locus: {locus}")
        bridge_rows.append({
            "bridge_id": bridge_id, "family": family, "page": row["page"], "locus": locus,
            "diagnostic_surface": diagnostic, "zl3b_line": row["zl3b_clean"],
            "it2a_line": row["it2a_clean"], "rf1b_line": row["rf1b_clean"],
            "supports": support,
        })

    glossary = {key: dict(value) for key, value in base_glossary.items()}
    coverage, one_unknown, _, complete = g637.build_line_coverage(
        by_line, glossary, exact, boundary, cross_by_locus,
    )
    if metrics(coverage, one_unknown, complete, glossary) != base_metrics:
        raise RuntimeError("V28 replay changed before the first GDT652 target")
    base_complete_loci = {row["locus"] for row in base_complete}
    seen_one_loci = {row["locus"] for row in base_one}
    accepted_dictionary_rows: list[dict[str, object]] = []
    target_deck: list[dict[str, object]] = []
    audit_rows: list[dict[str, object]] = []
    variant_rows: list[dict[str, object]] = []
    ledger_rows: list[dict[str, object]] = []
    newly_exposed_rows: list[dict[str, object]] = []
    round_rows: list[dict[str, object]] = [{
        "round": 0, "surface": "BASE_V28", "tier": "BASE", "dictionary_entries": len(base_dictionary),
        "dictionary_sha256": canonical_hash(base_dictionary), **base_metrics,
    }]

    for round_number, raw_spec in enumerate(CANDIDATE_SPECS, 1):
        spec_row = {key: str(value) for key, value in raw_spec.items()}
        surface = spec_row["surface"]
        if GENERIC_FILLER.search(spec_row["working_meaning_de"]):
            raise RuntimeError(f"generic filler in target: {surface}")
        members = [row for row in token_rows if row["eva"] == surface]
        if not members or len(members) != token_counts[surface]:
            raise RuntimeError(f"target occurrence drift: {surface}")
        exact_count = sum(exact[row["locus"], int(row["token_index"])] for row in members)
        split_count = sum(boundary[row["locus"], int(row["token_index"])] for row in members)
        if exact_count == 0:
            raise RuntimeError(f"accepted target lacks an all-reader exact anchor: {surface}")

        pre_coverage, pre_one, pre_complete = coverage, one_unknown, complete
        pre_by_locus = {row["locus"]: row for row in pre_coverage}
        pre_complete_loci = {row["locus"] for row in pre_complete}
        if spec_row["strict_source"] == "1":
            source = {row["locus"]: row for row in pre_one}.get(spec_row["source_locus"])
            if source is None or source["unknown_surface"] != surface or int(source["strict_eligible"]) != 1:
                raise RuntimeError(f"source line no longer strict one-hole: {surface}")

        g637.set_gloss(
            glossary, surface, spec_row["working_meaning_de"], f"GDT652:{spec_row['tier']}",
            "EXACT_WHOLE_FAMILY_EXTENSION", "KNOWN_EXACT_WHOLE", 148,
        )
        coverage, one_unknown, _, complete = g637.build_line_coverage(
            by_line, glossary, exact, boundary, cross_by_locus,
        )
        post_by_locus = {row["locus"]: row for row in coverage}
        new_complete_loci = sorted({row["locus"] for row in complete} - pre_complete_loci)
        if spec_row["strict_source"] == "1" and spec_row["source_locus"] not in new_complete_loci:
            raise RuntimeError(f"target failed to close strict source: {surface}")

        verdicts: Counter[str] = Counter()
        members.sort(key=lambda row: (row["page"], row["locus"], int(row["token_index"])))
        for occurrence, member in enumerate(members, 1):
            locus, token_index = member["locus"], int(member["token_index"])
            line = by_line[locus]
            ordinal = line_position(line, token_index)
            before, after = pre_by_locus[locus], post_by_locus[locus]
            before_glosses, after_glosses = split_pipe(before["token_glosses_de"]), split_pipe(after["token_glosses_de"])
            reader_exact = exact[locus, token_index]
            normalized = boundary[locus, token_index]
            support = "ALL_THREE_EXACT" if reader_exact else "ALL_THREE_SPLIT_NORMALIZED" if normalized else "READER_VARIANT"
            known_other = int(before["known_tokens"])
            clean_other = known_other - int(before["ambiguous_tokens"]) - int(before["reader_unstable_tokens"])
            if support == "READER_VARIANT":
                verdict = "READER_VARIANT_WARNING"
            elif spec_row["tier"].startswith("EXPLORATORY"):
                verdict = "EXPLORATORY_CONTEXT_NO_RECORDED_COLLISION" if clean_other >= 2 else "EXPLORATORY_SHORT_OR_OPAQUE"
            elif clean_other >= 2:
                verdict = "FAMILY_CONTEXT_COMPATIBLE"
            else:
                verdict = "SHORT_OR_OPAQUE_CONTEXT"
            verdicts[verdict] += 1
            audit_rows.append({
                "audit_id": f"G652-A{round_number:02d}-{occurrence:03d}", "round": round_number,
                "surface": surface, "tier": spec_row["tier"], "page": member["page"], "locus": locus,
                "section": member["section"], "language": member["language"], "hand": member["hand"],
                "token_ordinal": ordinal,
                "line_position": "ONLY" if len(line) == 1 else "INITIAL" if ordinal == 1 else "FINAL" if ordinal == len(line) else "MEDIAL",
                "previous": "<BOS>" if ordinal == 1 else line[ordinal - 2]["eva"],
                "following": "<EOS>" if ordinal == len(line) else line[ordinal]["eva"],
                "zl3b_line": before["zl3b_line"], "it2a_line": cross_by_locus[locus]["it2a_clean"],
                "rf1b_line": cross_by_locus[locus]["rf1b_clean"], "reader_support": support,
                "reader_exact": reader_exact, "split_normalized": normalized,
                "before_gloss_de": before_glosses[ordinal - 1], "after_gloss_de": after_glosses[ordinal - 1],
                "known_other_tokens": known_other, "clean_known_other_tokens": clean_other,
                "local_before_de": before["token_glosses_de"], "local_after_de": after["token_glosses_de"],
                "hard_collision": 0, "verdict": verdict,
            })
            if support != "ALL_THREE_EXACT":
                variant_rows.append({
                    "surface": surface, "page": member["page"], "locus": locus,
                    "zl3b_line": before["zl3b_line"], "it2a_line": cross_by_locus[locus]["it2a_clean"],
                    "rf1b_line": cross_by_locus[locus]["rf1b_clean"], "reader_support": support,
                    "working_meaning_de": spec_row["working_meaning_de"],
                    "decision": "RETAIN_EXACT_ZL3B_WITH_READER_WARNING",
                })

        accepted_dictionary_rows.append(dictionary_row(spec_row, round_number, len(members), exact_count))
        current_one_by_locus = {row["locus"]: row for row in one_unknown}
        for locus in sorted(set(current_one_by_locus) - seen_one_loci):
            newly_exposed_rows.append({
                "introduced_round": round_number, "enabled_by_surface": surface,
                **{field: current_one_by_locus[locus][field] for field in ONE_FIELDS},
            })
        seen_one_loci.update(current_one_by_locus)
        post_dictionary = [*base_dictionary, *accepted_dictionary_rows]
        ledger_rows.append({
            "round": round_number, "surface": surface, "tier": spec_row["tier"], "decision": "ACCEPT_V29_EXACT_WHOLE",
            "decision_reason": spec_row["decision_basis"], "pre_dictionary_entries": len(post_dictionary) - 1,
            "post_dictionary_entries": len(post_dictionary), "occurrences": len(members),
            "all_reader_exact": exact_count, "split_normalized": split_count,
            "reader_variant": len(members) - split_count, "hard_collisions": 0,
            "complete_before": len(pre_complete), "complete_after": len(complete),
            "strict_complete_after": sum(int(row["strict_complete"]) for row in complete),
            "one_unknown_before": len(pre_one), "one_unknown_after": len(one_unknown),
            "new_complete_loci": "|".join(new_complete_loci) or "NONE",
        })
        target_deck.append({
            "candidate_id": f"G652-C{round_number:02d}", "candidate_order": round_number,
            "surface": surface, "source_locus": spec_row["source_locus"], "strict_source": spec_row["strict_source"],
            "family": spec_row["family"], "acceptance_tier": spec_row["tier"],
            "working_meaning_de": spec_row["working_meaning_de"], "composition": spec_row["composition"],
            "rival_de": spec_row["rival_de"], "occurrences": len(members),
            "pages": len({row["page"] for row in members}), "reader_exact_occurrences": exact_count,
            "split_normalized_occurrences": split_count, "decision": "ACCEPT_V29_EXACT_WHOLE",
            "decision_basis": spec_row["decision_basis"], "strongest_counterargument": spec_row["counterargument"],
        })
        round_rows.append({
            "round": round_number, "surface": surface, "tier": spec_row["tier"],
            "dictionary_entries": len(post_dictionary), "dictionary_sha256": canonical_hash(post_dictionary),
            **metrics(coverage, one_unknown, complete, glossary),
        })

    final_dictionary = [*base_dictionary, *accepted_dictionary_rows]
    final_coverage, final_one, _, final_complete = g637.build_line_coverage(
        by_line, glossary, exact, boundary, cross_by_locus,
    )
    final_by_locus = {row["locus"]: row for row in final_coverage}
    base_by_locus = {row["locus"]: row for row in base_coverage}
    final_complete_by_locus = {row["locus"]: row for row in final_complete}
    final_metrics = metrics(final_coverage, final_one, final_complete, glossary)
    final_gloss_rows = [
        {key: row[key] for key in ("surface", "working_meaning_de", "source", "strength", "scope_state", "priority")}
        for row in sorted(glossary.values(), key=lambda item: str(item["surface"]))
    ]
    accepted_defaults = [{
        "surface": row["entry"].split("@", 1)[0], **row,
        "source_locus": next(item["source_locus"] for item in target_deck if item["surface"] == row["entry"].split("@", 1)[0]),
        "occurrences": next(item["occurrences"] for item in target_deck if item["surface"] == row["entry"].split("@", 1)[0]),
        "acceptance_tier": next(item["acceptance_tier"] for item in target_deck if item["surface"] == row["entry"].split("@", 1)[0]),
    } for row in accepted_dictionary_rows]

    risk_rows = [{
        "surface": row["surface"], "acceptance_tier": row["acceptance_tier"],
        "working_meaning_de": row["working_meaning_de"], "rival_de": row["rival_de"],
        "strongest_support": row["decision_basis"], "strongest_counterargument": row["strongest_counterargument"],
        "replacement_trigger": (
            "replace Arzneikompositum if one better learned object value explains the neutral and four qualified CKH shells; split a compound if direct reader boundaries demand it"
        ),
    } for row in target_deck]

    reality_rows: list[dict[str, object]] = []
    for strict_hole in strict_hole_rows:
        surface, locus = strict_hole["unknown_surface"], strict_hole["locus"]
        row = final_by_locus[locus]
        reality_rows.append({
            "surface": surface, "page": row["page"], "locus": locus,
            "strict_complete": final_complete_by_locus[locus]["strict_complete"],
            "zl3b_line": row["zl3b_line"], "tokenwise_translation_de": row["token_glosses_de"],
            "smoothed_working_reading_de": SMOOTHED_SOURCE_LINES[locus],
            "acceptance_tier": next(item["acceptance_tier"] for item in target_deck if item["surface"] == surface),
        })
    reality_rows.sort(key=lambda row: row["locus"])

    affected_rows: list[dict[str, object]] = []
    for locus in sorted(by_line):
        present = list(dict.fromkeys(
            token["eva"] for token in by_line[locus] if token["eva"] in targets | revision_surfaces
        ))
        if not present:
            continue
        row = final_by_locus[locus]
        affected_rows.append({
            "page": row["page"], "locus": locus, "target_surfaces": "|".join(present),
            "zl3b_line": row["zl3b_line"], "v28_tokenwise_de": base_by_locus[locus]["token_glosses_de"],
            "v29_tokenwise_de": row["token_glosses_de"],
            "v29_working_reading_de": "; ".join(split_pipe(row["token_glosses_de"])),
            "complete_v29": int(row["unknown_tokens"]) == 0,
        })

    new_complete_rows: list[dict[str, object]] = []
    for locus in sorted(set(final_complete_by_locus) - base_complete_loci):
        row = final_by_locus[locus]
        present = list(dict.fromkeys(token["eva"] for token in by_line[locus] if token["eva"] in targets))
        new_complete_rows.append({
            "page": row["page"], "locus": locus, "strict_complete": final_complete_by_locus[locus]["strict_complete"],
            "enabled_by_surfaces": "|".join(present), "zl3b_line": row["zl3b_line"],
            "literal_v29_de": "; ".join(split_pipe(row["token_glosses_de"])),
            "curated_source_reading_de": SMOOTHED_SOURCE_LINES.get(locus, "NOT_CURATED_SOURCE_LINE"),
        })

    write_tsv(output_dir / "PAGE_ALLOWLIST.tsv", [{"page": page} for page in sorted(pages)], ("page",))
    write_tsv(output_dir / "TARGET_DECISION_DECK.tsv", target_deck, (
        "candidate_id", "candidate_order", "surface", "source_locus", "strict_source", "family",
        "acceptance_tier", "working_meaning_de", "composition", "rival_de", "occurrences", "pages",
        "reader_exact_occurrences", "split_normalized_occurrences", "decision", "decision_basis",
        "strongest_counterargument",
    ))
    write_tsv(output_dir / "FAMILY_EVIDENCE_ATLAS.tsv", family_rows, (
        "family", "surface", "composition", "predicted_reading_de", "zl3b_occurrences", "pages",
        "reader_exact_occurrences", "split_normalized_occurrences", "planned_status", "final_status",
    ))
    write_tsv(output_dir / "BOUNDARY_BRIDGE_ATLAS.tsv", bridge_rows, (
        "bridge_id", "family", "page", "locus", "diagnostic_surface", "zl3b_line",
        "it2a_line", "rf1b_line", "supports",
    ))
    write_tsv(output_dir / "RISK_AND_RIVAL_REGISTER.tsv", risk_rows, (
        "surface", "acceptance_tier", "working_meaning_de", "rival_de", "strongest_support",
        "strongest_counterargument", "replacement_trigger",
    ))
    write_tsv(output_dir / "ALL_OCCURRENCE_SEMANTIC_AUDIT.tsv", audit_rows, (
        "audit_id", "round", "surface", "tier", "page", "locus", "section", "language", "hand",
        "token_ordinal", "line_position", "previous", "following", "zl3b_line", "it2a_line", "rf1b_line",
        "reader_support", "reader_exact", "split_normalized", "before_gloss_de", "after_gloss_de",
        "known_other_tokens", "clean_known_other_tokens", "local_before_de", "local_after_de",
        "hard_collision", "verdict",
    ))
    write_tsv(output_dir / "READER_VARIANT_AUDIT.tsv", variant_rows, (
        "surface", "page", "locus", "zl3b_line", "it2a_line", "rf1b_line", "reader_support",
        "working_meaning_de", "decision",
    ))
    write_tsv(output_dir / "SEQUENTIAL_DECISION_LEDGER.tsv", ledger_rows, (
        "round", "surface", "tier", "decision", "decision_reason", "pre_dictionary_entries",
        "post_dictionary_entries", "occurrences", "all_reader_exact", "split_normalized", "reader_variant",
        "hard_collisions", "complete_before", "complete_after", "strict_complete_after", "one_unknown_before",
        "one_unknown_after", "new_complete_loci",
    ))
    write_tsv(output_dir / "ROUND_COVERAGE_COUNTS.tsv", round_rows, (
        "round", "surface", "tier", "dictionary_entries", "dictionary_sha256", "physical_lines",
        "known_token_positions", "unknown_token_positions", "complete_multi_token_lines", "strict_complete_lines",
        "one_unknown_lines", "strict_one_unknown_lines", "exact_glossary_surfaces",
    ))
    write_tsv(output_dir / "ACCEPTED_WHOLE_SURFACE_DEFAULTS.tsv", accepted_defaults, (
        "surface", "entry", "kind", "working_meaning_de", "composition", "context_rule", "status",
        "source_locus", "occurrences", "acceptance_tier",
    ))
    write_tsv(output_dir / "SOURCE_PASSAGE_REALITY_CHECK.tsv", reality_rows, (
        "surface", "page", "locus", "strict_complete", "zl3b_line", "tokenwise_translation_de",
        "smoothed_working_reading_de", "acceptance_tier",
    ))
    write_tsv(output_dir / "AFFECTED_LINE_TRANSLATIONS.tsv", affected_rows, (
        "page", "locus", "target_surfaces", "zl3b_line", "v28_tokenwise_de", "v29_tokenwise_de",
        "v29_working_reading_de", "complete_v29",
    ))
    write_tsv(output_dir / "NEWLY_COMPLETED_LINES.tsv", new_complete_rows, (
        "page", "locus", "strict_complete", "enabled_by_surfaces", "zl3b_line", "literal_v29_de",
        "curated_source_reading_de",
    ))
    write_tsv(output_dir / "NEWLY_EXPOSED_ONE_HOLE_LINES.tsv", newly_exposed_rows, (
        "introduced_round", "enabled_by_surface", *ONE_FIELDS,
    ))
    write_tsv(output_dir / "V29_EXACT_TOKEN_GLOSSARY.tsv", final_gloss_rows, (
        "surface", "working_meaning_de", "source", "strength", "scope_state", "priority",
    ))
    write_tsv(output_dir / "ALL_LINE_CONCRETE_COVERAGE_V29.tsv", final_coverage, COVERAGE_FIELDS)
    write_tsv(output_dir / "COMPLETE_PASSAGES_V29.tsv", final_complete, (
        "rank", "strict_complete", *COVERAGE_FIELDS, "working_translation_de",
    ))
    write_tsv(output_dir / "ONE_UNKNOWN_PASSAGES_V29.tsv", final_one, ONE_FIELDS)
    write_tsv(output_dir / "WORKING_DICTIONARY_V29.tsv", final_dictionary, (
        "entry", "kind", "working_meaning_de", "composition", "context_rule", "status",
    ))

    output_paths = [output_dir / name for name in OUTPUT_NAMES]
    input_paths = (
        G651_RUN, G651_ALLOW, G651_COVERAGE, G651_COMPLETE, G651_ONE,
        G651_GLOSSARY, G651_DICTIONARY, G651_RESULT, G651_REPORT,
        G624_REPORT, G632_REPORT, G633_REPORT, G647_REPORT, G650_REPORT,
        TOKENS_REL, CROSS_REL,
    )
    verdicts = Counter(row["verdict"] for row in audit_rows)
    tiers = Counter(row["acceptance_tier"] for row in target_deck)
    result_core = {
        "schema": "GDT652_PREPARATION_GRID_MIGRATION_RESULT_V2",
        "experiment_id": "GDT652", "status": STATUS,
        "guard": {"f1r": "EXCLUDED", "f84": "FORBIDDEN", "f84r": "FORBIDDEN", "new_pages": 0,
                  "new_images": 0, "allowed_pages": len(pages), "token_query": token_stats, "cross_query": cross_stats},
        "target_run": {
            "candidates": len(target_deck), "accepted_exact_wholes": len(target_deck),
            "accepted_surfaces": [row["surface"] for row in target_deck],
            "strict_v28_holes_closed": len(strict_hole_rows), "acceptance_tiers": dict(sorted(tiers.items())),
            "audited_occurrences": len(audit_rows),
            "all_reader_exact_occurrences": sum(int(row["reader_exact"]) for row in audit_rows),
            "split_normalized_occurrences": sum(int(row["split_normalized"]) for row in audit_rows),
            "reader_variant_warnings": sum(row["verdict"] == "READER_VARIANT_WARNING" for row in audit_rows),
            "hard_collisions": sum(int(row["hard_collision"]) for row in audit_rows),
            "verdicts": dict(sorted(verdicts.items())),
            "held_or_absent_cells": sorted(
                row["surface"] for row in family_rows
                if row["final_status"] in {"ABSENT_HOLD", "ZERO_EXACT_HOLD", "BRIDGE_ONLY_HOLD"}
            ),
        },
        "neutral_ckh_grid": {
            "accepted_cells": ["ckhy", "ckhey", "ckheey", "ckhdy", "ckhedy"],
            "absent_cells": ["ckheedy"],
            "quality_role": "UNSPECIFIED_NOT_NULL_QUALITY_CLAIM",
            "learned_noun": "Arzneikompositum",
        },
        "preparation_grids": {
            "o_ckh_accepted": ["ockhy", "ockhey", "ockhedy"],
            "qualified_o_ckh_accepted": [
                "chockhy", "chockhey", "chockhedy", "cheockhy", "cheockhey",
                "shockhy", "shockhey", "sheockhy", "sheockhey",
            ],
            "qualified_o_k_accepted": [
                "chokey", "chokeey", "chokedy", "chokeedy", "cheoky", "cheokey",
                "cheokeey", "cheokedy", "shoky", "shokey", "shokeey", "sheoky",
                "sheokey", "sheokeedy",
            ],
            "o_materia_al_accepted": ["opal", "osal", "oral", "olal"],
            "structural_tags_not_free_words": ["O_PREP", "CKH_LEARNED", "E_ATTR", "K_HEISS"],
        },
        "coverage": {"base": base_metrics, "final": final_metrics,
                     "newly_completed_lines": len(new_complete_rows),
                     "newly_exposed_one_hole_lines": len(newly_exposed_rows),
                     "affected_lines": len(affected_rows)},
        "working_dictionary": {"v28_entries": len(base_dictionary), "v29_entries": len(final_dictionary),
                               "accepted_tail_entries": len(accepted_dictionary_rows),
                               "v28_prefix_sha256": canonical_hash(base_dictionary),
                               "v29_sha256": canonical_hash(final_dictionary),
                               "v28_glossary_surfaces": len(base_glossary), "v29_glossary_surfaces": len(glossary)},
        "claim_boundary": (
            "GDT652 is an exploratory working translation, not a solved plaintext. It adds thirty-five observed exact-whole cards in four preparation/materia "
            "grids and closes five strict V28 holes. Arzneikompositum remains a replaceable learned family noun; quality-neutral means that no CH/SH/E quality "
            "is written, not that the object has no quality. O_PREP, CKH_LEARNED, E_ATTR, K_HEISS, tails and component boundaries are family-bound structural "
            "tags, not unrestricted free words. ORAL and OLAL keep explicit rival segmentations. Unobserved and zero-exact cells remain unwritten. No global "
            "suffix, absent-cell meaning, plaintext, phonetics, language, exact ingredient identity, f1r, new page or new image is asserted."
        ),
        "inputs": {str(path): sha256(ROOT / path) for path in input_paths},
        "outputs": {str(BASE_REL / "artifacts" / path.name): sha256(path) for path in output_paths},
    }
    result = {**result_core, "content_sha256": canonical_hash(result_core)}
    (output_dir / "RESULT.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8",
    )
    return result


def main() -> int:
    result = build(ART)
    target, coverage = result["target_run"], result["coverage"]
    print(
        f"GDT652 built: accepted={target['accepted_exact_wholes']} audits={target['audited_occurrences']} "
        f"known={coverage['final']['known_token_positions']} complete={coverage['final']['complete_multi_token_lines']} "
        f"strict={coverage['final']['strict_complete_lines']} one_unknown={coverage['final']['one_unknown_lines']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
