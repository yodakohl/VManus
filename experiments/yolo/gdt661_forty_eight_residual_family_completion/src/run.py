#!/usr/bin/env python3
"""Build GDT661: concrete family completion of the forty-eight V37 residuals."""
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
BASE_REL = Path("experiments/yolo/gdt661_forty_eight_residual_family_completion")
ART = ROOT / BASE_REL / "artifacts"
G660 = Path("experiments/yolo/gdt660_seventeen_residual_concrete_completion")
_spec = importlib.util.spec_from_file_location("gdt660_builder_for_gdt661", ROOT / G660 / "src/run.py")
if _spec is None or _spec.loader is None:
    raise RuntimeError("cannot load GDT660 builder")
g660 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(g660)
g659 = g660.g659
TOKENS_REL, CROSS_REL = g660.TOKENS_REL, g660.CROSS_REL
STATUS = "PASS_872_TARGET_POSITIONS__V38"


def whole(surface: str, meaning: str, composition: str, rival: str, family: str) -> dict[str, str]:
    return {"surface": surface, "working_meaning_de": meaning, "composition": composition,
            "strongest_rival_de": rival, "family": family}


# Composition tags and reader glosses are deliberately separate. Cards match
# exact whitespace-delimited wholes and never leak into substrings.
EXACT_WHOLE_SPECS = (
    whole("dam", "Dosis I", "D_DOSE+A_VALUE+M_UNIT_I", "Maßeinheit I oder Schlussmarke", "MEASURE_DOSAGE"),
    whole("ches", "trockenes Drogenmaterial, Mittelstufe", "CH_DRY+E_MIDDLE+S_BOUND", "trockene Arzneispecies", "DRUG_KIND_S"),
    whole("chs", "Trockengut, Grundform", "CH_DRY+S_BOUND_BASE", "trockene Arzneistoffform am Gradanfang", "DRUG_KIND_S"),
    whole("lkeey", "Drogenholz, heiß am Gradende", "L_WOOD+K_HOT+EEY_GRADE_END", "heißer L-Rahmenwert ohne Holz", "WOOD_HEAT_GRADE"),
    whole("okchol", "heißer Ansatz aus Trockengut", "O_PREP+K_HOT+CHOL_DRY_MATERIAL", "heiß-trockener Zubereitungsstoff", "HOT_DRY_PREP"),
    whole("r", "Wurzel", "R_ROOT_HEAD", "Harz oder Bezugszeichen", "ROOT_HEAD"),
    whole("ctholy", "Blatt-/Krautdroge, Grundform", "CTHOL_HERBAL_MATERIAL+Y_BASE", "unspezifisches CTH-Drogenmaterial", "CTH_HERBAL"),
    whole("ols", "Drogenstoffposten", "OL_MATERIAL+S_BOUND", "Samenstoff oder Sortenmarke", "DRUG_KIND_S"),
    whole("dl", "Rohstoffmaß", "D_MEASURE+L_MATERIAL_SHORT", "verkürztes DAL oder Drogenholzmaß", "MEASURE_DOSAGE"),
    whole("ykchy", "Eintrag/Bezug: heiß-trocken am Gradanfang", "Y_ENTRY_REF+KCH_HOT_DRY+Y_GRADE_START", "Y als reine Grenze vor KCHY", "QUALITY_START"),
    whole("kchar", "heiße Trockenfraktion I", "K_HOT+CH_DRY+AR_FRACTION_I", "heiße Drogenfraktion I", "FRACTION_PART"),
    whole("qokorar", "heiße Drogenportion, Fraktion I", "QO_FRAME+K_HOT+OR_PORTION+AR_FRACTION_I", "heiße Portionszubereitung, Dosis I", "FRACTION_PART"),
    whole("ychoy", "Eintrag/Bezug: Trockenansatz am Gradanfang", "Y_ENTRY_REF+CHO_DRY_PREP+Y_START", "Trockenansatz dieser Droge", "PREPARATION_YO"),
    whole("sheoy", "feucht angesetzte Zubereitung am Gradanfang", "SHEO_MOIST_PREP+Y_START", "Feuchtzubereitung in Grundform", "PREPARATION_YO"),
    whole("ytal", "Eintrag/Bezug: kalter Rohstoff I am Gradanfang", "Y_ENTRY_REF+T_COLD+AL_RAW_I", "Y als reine Eintragsgrenze", "QUALITY_START"),
    whole("sokaiin", "heißer Samenansatz, Grad III", "S_SEED+O_PREP+K_HOT+AIIN_III", "Saatgutzubereitung, Dosis III", "SEED_FORMS"),
    whole("shes", "feuchtes Drogenmaterial, Mittelstufe", "SH_MOIST+E_MIDDLE+S_BOUND", "feuchte Arzneispecies", "DRUG_KIND_S"),
    whole("qekeochor", "heiße trocken angesetzte Drogenportion", "QE_BOUND+KEO_HEATED_PREP+CHOR_PORTION", "Auszug aus Blüten-/Fruchtstand", "PREPARATION_MISC"),
    whole("okary", "heiße Ansatzfraktion I, abgeschlossen", "OKAR_HOT_PREP_FRACTION_I+Y_CLOSE", "Grundform statt Abschluss", "FRACTION_PART"),
    whole("shkair", "heiße angefeuchtete Drogenfraktion II", "SH_MOIST+K_HOT+AIR_FRACTION_II", "feuchte Fraktion II", "FRACTION_PART"),
    whole("keor", "heiße Drogenportion", "K_HOT+E_BOUND+OR_PORTION", "heißer Drogenteil", "FRACTION_PART"),
    whole("odan", "Zubereitungsdosis I", "O_PREP+D_DOSE+AN_I", "Ansatzmenge I", "MEASURE_DOSAGE"),
    whole("kodaiin", "erhitzte Zubereitung, Dosis III", "K_HOT+O_PREP+D_DOSE+AIIN_III", "heiße Ansatzcharge III", "MEASURE_DOSAGE"),
    whole("cho", "Trockenansatz", "CH_DRY+O_PREP", "Trockengut statt Zubereitung", "HOT_DRY_PREP"),
    whole("chotol", "Trockenansatz aus kaltem Material", "CHO_DRY_PREP+TOL_COLD_MATERIAL", "kalt-trockener Zubereitungsstoff", "HOT_DRY_PREP"),
    whole("d", "Dosis", "D_DOSE_HEAD", "Gradangabe oder Abschlusszeichen", "MEASURE_DOSAGE"),
    whole("qoteees", "kalter Qualitätsendwert, abgeschlossen", "QO_FRAME+T_COLD+EEE_END+S_CLOSED", "kalte Arzneispecies", "DRUG_KIND_S"),
    whole("alchey", "Rohstoff I, trocken in der Gradmitte", "AL_RAW_I+CH_DRY+EY_GRADE_MIDDLE", "trocken gebundenes Drogenholz", "RAW_COMPOSITE"),
    whole("sheody", "angefeuchteter Ansatz, abgeschlossen", "SHEO_MOIST_PREP+DY_CLOSED", "fertig aufbereitete Feuchtzubereitung", "PREPARATION_YO"),
    whole("oeeo", "zweiter Mazerationsansatz", "O_PREP+EE_STAGE_II+O_MEDIUM", "Misch-/Bindungsstufe II", "PREPARATION_MISC"),
    whole("dshor", "abgemessene Blüten-/Fruchtdroge", "D_MEASURED+SHOR_FLOWER_FRUIT_PART", "Dosis eines reproduktiven Pflanzenteils", "FRACTION_PART"),
    whole("sain", "Saatgut, Typ/Charge II", "S_SEED+AIN_II", "Samenmenge II", "SEED_FORMS"),
    whole("sokeedy", "heißer Samenansatz am Gradende, fertig", "S_SEED+O_PREP+K_HOT+EEDY_END_CLOSED", "getrocknete Saatzubereitung", "SEED_FORMS"),
    whole("am", "Maßeinheit I", "A_VALUE+M_UNIT_I", "Mengenabschluss I", "MEASURE_DOSAGE"),
    whole("chckhd", "trockenes Arzneikompositum, abgeschlossen", "CH_DRY+CKH_COMPOSITE+D_CLOSED", "verkürztes CHCKHDY", "RAW_COMPOSITE"),
    whole("otalor", "kalte Ansatzportion aus Rohstoff I", "O_PREP+T_COLD+AL_RAW_I+OR_PORTION", "kalte Rohstoffklasse I als Zutat", "FRACTION_PART"),
    whole("olkain", "heißes Drogenmaterial, Grad II", "OL_MATERIAL+K_HOT+AIN_II", "heißes Ansatzgut, Grad II", "PREPARATION_MISC"),
    whole("chty", "trocken-kalt am Gradanfang", "CH_DRY+T_COLD+Y_GRADE_START", "trocken-kalte gebundene Grundform", "QUALITY_START"),
    whole("loldy", "Drogenholzstoff, fertig aufbereitet", "L_WOOD+OL_MATERIAL+DY_FINISHED", "Holz-Materialfeld geschlossen", "PREPARATION_MISC"),
    whole("olteedy", "kaltes Drogenmaterial am Gradende, fertig", "OL_MATERIAL+T_COLD+EEDY_END_CLOSED", "kalter Ansatz am Gradende", "PREPARATION_MISC"),
    whole("cheeky", "trocken am Gradende, dann heiß am Gradanfang", "CH_DRY+EE_END+K_HOT+Y_START", "trocken angesetzte Heißzubereitung", "QUALITY_START"),
    whole("lkeedy", "Drogenholz, heiß am Gradende, abgeschlossen", "L_WOOD+K_HOT+EEDY_END_CLOSED", "heißer L-Rahmenwert ohne Holz", "WOOD_HEAT_GRADE"),
    whole("dalchedy", "abgemessener Rohstoff I, trocken in der Gradmitte, abgeschlossen", "DAL_MEASURED_RAW_I+CH_DRY+EDY_MIDDLE_CLOSED", "schlicht getrocknete Rohstoffmenge I", "RAW_COMPOSITE"),
    whole("saii", "Saatgutmenge III", "S_SEED+AII_III_READER_FORM", "verkürztes SAIIN", "SEED_FORMS"),
    whole("ykeedy", "Eintrag/Bezug: heiß am Gradende, abgeschlossen", "Y_ENTRY_REF+K_HOT+EEDY_END_CLOSED", "Y als reine Grenze", "WOOD_HEAT_GRADE"),
    whole("yteody", "Eintrag/Bezug: kalte Zubereitung, abgeschlossen", "Y_ENTRY_REF+T_COLD+E_BOUND+O_PREP+DY_FINISHED", "Y-Grenze plus TEODY-Karte", "QUALITY_START"),
    whole("tdain", "kalter Grad-/Maßwert II", "T_COLD+D_GRADE_MEASURE+AIN_II", "Dosis II der kalten Fraktion", "MEASURE_DOSAGE"),
    whole("chakal", "Rohstoff I, trocken-heiß am Gradanfang", "CH_DRY+A_LINK+K_HOT+AL_RAW_I", "CHOKAL-Trockenansatz", "RAW_COMPOSITE"),
)
EXACT_BY_SURFACE = {row["surface"]: row for row in EXACT_WHOLE_SPECS}
TARGET_ORDER = tuple(row["surface"] for row in EXACT_WHOLE_SPECS)
TARGET_SURFACES = frozenset(TARGET_ORDER)
CONTEXT_SCOPED_SURFACES = frozenset({"r", "d"})
LOW_SURFACES = frozenset({"qekeochor", "shkair", "oeeo", "qoteees", "saii", "tdain", "chakal"})
STRONG_SURFACES = frozenset({
    "okchol", "ctholy", "ykchy", "ytal", "odan", "kodaiin", "chotol", "sheody",
    "dshor", "sain", "otalor", "olkain", "chty", "cheeky", "dalchedy", "yteody",
})

EXPECTED_SURFACE_COUNTS = {
    "dam": 68, "ches": 31, "chs": 13, "lkeey": 38, "okchol": 10, "r": 129,
    "ctholy": 4, "ols": 17, "dl": 18, "ykchy": 20, "kchar": 1, "qokorar": 1,
    "ychoy": 1, "sheoy": 3, "ytal": 12, "sokaiin": 1, "shes": 5, "qekeochor": 1,
    "okary": 8, "shkair": 2, "keor": 6, "odan": 2, "kodaiin": 2, "cho": 75,
    "chotol": 7, "d": 53, "qoteees": 2, "alchey": 4, "sheody": 34, "oeeo": 1,
    "dshor": 14, "sain": 60, "sokeedy": 2, "am": 67, "chckhd": 4, "otalor": 4,
    "olkain": 33, "chty": 12, "loldy": 2, "olteedy": 3, "cheeky": 23, "lkeedy": 37,
    "dalchedy": 5, "saii": 1, "ykeedy": 26, "yteody": 7, "tdain": 2, "chakal": 1,
}

FAMILY_ANCHORS = {
    "MEASURE_DOSAGE": ("d", "am", "dam", "dl", "odan", "kodaiin", "tdain", "dal", "dain", "daiin"),
    "DRUG_KIND_S": ("chs", "ches", "shes", "ols", "qoteees", "s"),
    "WOOD_HEAT_GRADE": ("lkeey", "lkeedy", "ykeedy", "lkey", "lkedy", "keey", "keedy"),
    "HOT_DRY_PREP": ("cho", "chotol", "okchol", "chol", "cheo", "choly"),
    "ROOT_HEAD": ("r", "ral", "rain", "raiin", "rar", "ror", "rol"),
    "CTH_HERBAL": ("ctholy", "cthy", "cthol", "chocthy", "shocthy"),
    "QUALITY_START": ("ykchy", "ytal", "chty", "cheeky", "yteody", "kchy", "tal", "teody"),
    "FRACTION_PART": ("kchar", "qokorar", "okary", "shkair", "keor", "dshor", "otalor", "ar", "or"),
    "PREPARATION_YO": ("ychoy", "sheoy", "sheody", "choy", "shoy", "sheo", "ody"),
    "SEED_FORMS": ("sokaiin", "sain", "sokeedy", "saii", "saiin", "sor", "sar"),
    "RAW_COMPOSITE": ("alchey", "dalchedy", "chakal", "chckhd", "al", "dal", "chckhy"),
    "PREPARATION_MISC": ("qekeochor", "oeeo", "olkain", "loldy", "olteedy", "keo", "oldy"),
}

OUTPUT_NAMES = (
    "PAGE_ALLOWLIST.tsv", "TARGET_DECISION_DECK.tsv", "ACCEPTED_WHOLE_SURFACE_DEFAULTS.tsv",
    "CONTEXT_RENDERING_CARDS.tsv", "ALL_OCCURRENCE_SEMANTIC_AUDIT.tsv", "READER_VARIANT_AUDIT.tsv",
    "FAMILY_COMPOSITION_ATLAS.tsv", "FRONTIER_48_COMPLETIONS.tsv", "TARGET_LINE_TRANSLATIONS.tsv",
    "ROUND_COVERAGE_COUNTS.tsv", "NEWLY_COMPLETED_LINES.tsv", "NEWLY_EXPOSED_ONE_HOLE_LINES.tsv",
    "V38_WORKING_TOKEN_GLOSSARY.tsv", "WORKING_DICTIONARY_V38.tsv", "ALL_LINE_CONCRETE_COVERAGE_V38.tsv",
    "COMPLETE_PASSAGES_V38.tsv", "ONE_UNKNOWN_PASSAGES_V38.tsv",
)
VALUE_FORMS = frozenset({"n", "in", "iin", "iiin", "ain", "aiin", "aiiin"})
Y_ENTRY_SURFACES = frozenset({"ykchy", "ychoy", "ytal", "ykeedy", "yteody"})
GENERIC_FILLER = re.compile(r"arbeitsgut|arbeitsvorgang|arbeitschritt|arbeitsschritt|arbeitsmittel|arbeitsstoff", re.I)


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


def card_strength(surface: str) -> str:
    if surface in LOW_SURFACES:
        return "LOW_EXPLORATORY"
    if surface in STRONG_SURFACES:
        return "STRONG_FAMILY_COMPOSITION"
    if surface in CONTEXT_SCOPED_SURFACES or surface in {"cho", "am", "dam"}:
        return "CONTEXT_STRONG"
    return "MEDIUM_EXACT_WHOLE"


def rendering_class(surface: str, position: str, kind: str, right: str) -> str:
    if surface == "r":
        if kind == "L" or position == "ONLY":
            return "R_LABEL"
        if right in VALUE_FORMS:
            return "R_BEFORE_VALUE"
        return "R_HEAD" if position == "BOS" else "R_BODY"
    if surface == "d":
        if kind == "L":
            return "D_LABEL"
        if right in VALUE_FORMS:
            return "D_BEFORE_VALUE"
        return "D_TERMINAL" if position in {"EOS", "ONLY"} else "D_BODY"
    if surface == "cho":
        return "CHO_HEAD" if position == "BOS" else "CHO_TERMINAL" if position == "EOS" else "CHO_BODY"
    if surface in {"am", "dam"}:
        if kind == "L":
            return f"{surface.upper()}_LABEL"
        return f"{surface.upper()}_TERMINAL" if position in {"EOS", "ONLY"} else f"{surface.upper()}_BODY"
    if surface in Y_ENTRY_SURFACES:
        return "Y_WHOLE_ENTRY" if position == "BOS" else "Y_WHOLE_REFERENCE"
    return "EXACT_WHOLE"


def occurrence_render(surface: str, position: str, kind: str, right: str) -> str:
    default = EXACT_BY_SURFACE[surface]["working_meaning_de"]
    klass = rendering_class(surface, position, kind, right)
    if klass == "R_LABEL":
        return "[Wurzelzeichen]"
    if klass in {"R_BEFORE_VALUE", "R_HEAD"}:
        return "Wurzel:"
    if klass == "D_LABEL":
        return "[Dosiszeichen]"
    if klass == "D_BEFORE_VALUE":
        return "davon/Dosis:"
    if klass == "D_TERMINAL":
        return "Dosisvermerk."
    if klass == "CHO_HEAD":
        return "Trockenansatz:"
    if klass == "AM_LABEL":
        return "[Maßeinheit-I-Zeichen]"
    if klass == "DAM_LABEL":
        return "[Dosis-I-Zeichen]"
    if klass in {"AM_TERMINAL", "DAM_TERMINAL"}:
        return default + "."
    if klass in {"Y_WHOLE_ENTRY", "Y_WHOLE_REFERENCE"}:
        prefix = "Eintrag: " if klass == "Y_WHOLE_ENTRY" else "hierzu: "
        payloads = {
            "ykchy": "heiß-trocken am Gradanfang",
            "ychoy": "Trockenansatz am Gradanfang",
            "ytal": "kalter Rohstoff I am Gradanfang",
            "ykeedy": "heiß am Gradende, abgeschlossen",
            "yteody": "kalte Zubereitung, abgeschlossen",
        }
        return prefix + payloads[surface]
    return default


def occurrence_gloss(surface: str, position: str, kind: str, right: str) -> str:
    klass = rendering_class(surface, position, kind, right)
    if klass == "R_LABEL":
        return "[Wurzelzeichen]"
    if klass == "D_LABEL":
        return "[Dosis-/Maßzeichen]"
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
    members = sorted(
        (row for key, row in target_by_token.items() if key[0] == locus),
        key=lambda row: int(row["ordinal"]),
    )
    marked_glosses = list(glosses)
    marker_to_render: dict[str, str] = {}
    for occurrence in members:
        ordinal = int(occurrence["ordinal"])
        marker = f"§G661_{occurrence['token_index']}_{ordinal}§"
        marked_glosses[ordinal - 1] = marker
        marker_to_render[marker] = str(occurrence["working_render_de"])
    rendered = g660.practical_line_translation(
        locus, line, marked_glosses, y_occurrence_by_token, merged
    )
    for marker, replacement in marker_to_render.items():
        if rendered.count(marker) != 1:
            raise RuntimeError(f"positional render marker lost or duplicated at {locus}: {marker}")
        rendered = rendered.replace(marker, replacement)
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
    pages = {row["page"] for row in read_tsv(ROOT / G660 / "artifacts/PAGE_ALLOWLIST.tsv")}
    if len(pages) != 179 or "f1r" in pages or any(page.startswith("f84") for page in pages):
        raise RuntimeError("inherited page allow-list is not the exact safe 179-page panel")
    tokens, token_stats = g659.guarded_query(
        TOKENS_REL, pages, "page,locus,token_index,eva,kind,section,language,hand"
    )
    cross, cross_stats = g659.guarded_query(
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

    base_dictionary = read_tsv(ROOT / G660 / "artifacts/WORKING_DICTIONARY_V37.tsv")
    base_glossary_rows = read_tsv(ROOT / G660 / "artifacts/V37_WORKING_TOKEN_GLOSSARY.tsv")
    base_coverage = read_tsv(ROOT / G660 / "artifacts/ALL_LINE_CONCRETE_COVERAGE_V37.tsv")
    base_complete = read_tsv(ROOT / G660 / "artifacts/COMPLETE_PASSAGES_V37.tsv")
    base_one = read_tsv(ROOT / G660 / "artifacts/ONE_UNKNOWN_PASSAGES_V37.tsv")
    frontier = read_tsv(ROOT / G660 / "artifacts/NEWLY_EXPOSED_ONE_HOLE_LINES.tsv")
    y_occurrences = read_tsv(ROOT / g660.G659 / "artifacts/Y_OCCURRENCE_CENSUS.tsv")
    inherited_audit = read_tsv(ROOT / G660 / "artifacts/ALL_OCCURRENCE_SEMANTIC_AUDIT.tsv")
    dimensions = (len(base_dictionary), len(base_glossary_rows), len(base_coverage), len(base_complete), len(base_one), len(frontier))
    if dimensions != (606, 510, 4128, 172, 273, 48):
        raise RuntimeError(f"V37 base dimensions drift: {dimensions!r}")
    if tuple(row["unknown_surface"] for row in frontier) != TARGET_ORDER:
        raise RuntimeError("the forty-eight frontier surfaces or their fixed order drifted")
    base_glossary = {row["surface"]: row for row in base_glossary_rows}
    if any(surface in base_glossary for surface in TARGET_SURFACES):
        raise RuntimeError("a GDT661 target unexpectedly already has a V37 glossary row")
    y_occurrence_by_token = {(row["locus"], int(row["token_index"])): row for row in y_occurrences}
    inherited_target_by_token = {(row["locus"], int(row["token_index"])): row for row in inherited_audit}
    surface_counts = Counter(row["eva"] for row in tokens)
    observed_counts = {surface: surface_counts[surface] for surface in TARGET_ORDER}
    if observed_counts != EXPECTED_SURFACE_COUNTS or sum(observed_counts.values()) != 872:
        raise RuntimeError(f"target surface count drift: {observed_counts!r}")
    exact, normalized = g660.stable_maps(tokens, cross_by_locus)

    occurrence_rows: list[dict[str, object]] = []
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
            left = words[index - 1] if index else "<BOS>"
            right = words[index + 1] if index + 1 < len(line) else "<EOS>"
            klass = rendering_class(surface, position, token["kind"], right)
            key = (locus, int(token["token_index"]))
            item: dict[str, object] = {
                "occurrence_id": f"G661-T{len(occurrence_rows) + 1:04d}",
                "page": token["page"], "locus": locus, "token_index": token["token_index"],
                "ordinal": ordinal, "line_length": len(line), "surface": surface,
                "token_kind": token["kind"], "position": position, "section": token["section"],
                "language": token["language"], "hand": token["hand"],
                "family": EXACT_BY_SURFACE[surface]["family"],
                "scope_mode": (
                    "OCCURRENCE_SCOPED_CONTEXT_CARD" if surface in CONTEXT_SCOPED_SURFACES
                    else "EXACT_WHOLE_WITH_CONTEXT_RENDERING"
                ),
                "rendering_class": klass, "left_surface": left, "right_surface": right,
                "working_gloss_de": occurrence_gloss(surface, position, token["kind"], right),
                "working_render_de": occurrence_render(surface, position, token["kind"], right),
                "composition": EXACT_BY_SURFACE[surface]["composition"],
                "strongest_rival_de": EXACT_BY_SURFACE[surface]["strongest_rival_de"],
                "reader_exact": exact[key], "split_normalized": normalized[key],
                "all_three_present": cross_by_locus[locus]["all_three_present"],
                "all_present_exact": cross_by_locus[locus]["all_present_exact"],
                "zl3b_line": cross_by_locus[locus]["zl3b_clean"],
                "it2a_line": cross_by_locus[locus]["it2a_clean"],
                "rf1b_line": cross_by_locus[locus]["rf1b_clean"],
            }
            occurrence_rows.append(item)
            target_by_token[key] = item
            context_counts[klass] += 1
    if len(occurrence_rows) != 872 or len(target_by_token) != 872:
        raise RuntimeError("target occurrence census drift")
    if len({row["locus"] for row in occurrence_rows}) != 786 or len({row["page"] for row in occurrence_rows}) != 168:
        raise RuntimeError("target line/page census drift")
    if sum(int(row["reader_exact"]) for row in occurrence_rows) != 600 or sum(int(row["split_normalized"]) for row in occurrence_rows) != 602:
        raise RuntimeError("target reader census drift")

    base_coverage_by_locus = {row["locus"]: row for row in base_coverage}
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
            raise RuntimeError(f"V37 coverage token columns misalign: {locus}")
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
                raise RuntimeError(f"V37 target not open at {locus}.{index + 1}: {surface}")
            glosses[index] = str(occurrence["working_gloss_de"])
            if surface in CONTEXT_SCOPED_SURFACES:
                sources[index] = f"GDT661:{occurrence['rendering_class']}"
                states[index] = "KNOWN_CONTEXT_LICENSED" if int(occurrence["reader_exact"]) else "READER_BOUNDARY_UNSTABLE"
            else:
                sources[index] = f"GDT661:EXACT_WHOLE:{surface}"
                states[index] = "KNOWN_EXACT_WHOLE" if int(occurrence["reader_exact"]) else "READER_BOUNDARY_UNSTABLE"
            target_ordinals.add(str(index + 1))
            affected_loci.add(locus)
        for index, token in enumerate(line):
            key = (locus, int(token["token_index"]))
            if key not in target_by_token:
                non_target_after.append((locus, index + 1, token["eva"], glosses[index], sources[index], states[index]))
        unknown_pairs = [pair for pair in unknown_pairs if pair[0] not in target_ordinals]
        result_row: dict[str, object] = dict(base_row)
        result_row["known_tokens"] = int(base_row["known_tokens"]) + len(target_ordinals)
        result_row["context_licensed_tokens"] = states.count("KNOWN_CONTEXT_LICENSED")
        result_row["ambiguous_tokens"] = states.count("AMBIGUOUS_ACTIVE_RIVAL")
        result_row["reader_unstable_tokens"] = states.count("READER_BOUNDARY_UNSTABLE")
        result_row["unknown_tokens"] = len(unknown_pairs)
        result_row["coverage_fraction"] = f"{int(result_row['known_tokens']) / int(result_row['token_count']):.6f}"
        result_row["token_glosses_de"] = " | ".join(glosses)
        result_row["gloss_sources"] = " | ".join(sources)
        result_row["scope_states"] = " | ".join(states)
        result_row["unknown_ordinals"] = "|".join(pair[0] for pair in unknown_pairs) or "NONE"
        result_row["unknown_surfaces"] = "|".join(pair[1] for pair in unknown_pairs) or "NONE"
        if int(base_row["unknown_tokens"]) - len(target_ordinals) != len(unknown_pairs):
            raise RuntimeError(f"V37→V38 arithmetic drift: {locus}")
        coverage_rows.append(result_row)
    if non_target_before != non_target_after:
        raise RuntimeError("a non-target projection changed")
    non_target_sha = canonical_hash(non_target_before)
    coverage_by_locus = {str(row["locus"]): row for row in coverage_rows}

    complete_rows: list[dict[str, object]] = []
    for row in coverage_rows:
        if int(row["unknown_tokens"]) or int(row["token_count"]) < 2:
            continue
        complete = dict(row)
        complete["strict_complete"] = int(
            int(row["ambiguous_tokens"]) == 0
            and int(row["reader_unstable_tokens"]) == 0
            and int(row["all_present_exact"]) == 1
        )
        complete["working_translation_de"] = line_translation(
            str(row["locus"]), by_line[str(row["locus"])], split_pipe(row["token_glosses_de"]),
            y_occurrence_by_token, inherited_target_by_token, target_by_token,
        )
        complete_rows.append(complete)
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
        previous_card = base_one_by_locus.get(str(row["locus"]))
        if previous_card and previous_card["unknown_surface"] == surface and int(previous_card["unknown_ordinal"]) == ordinal:
            proposal = previous_card["proposed_default_de"]
            basis = previous_card["proposal_basis"]
            strength = previous_card["proposal_strength"]
        else:
            proposal, basis, strength = f"[{surface}:?]", "NEWLY_EXPOSED_BY_GDT661_NO_NEW_CARD", "OPEN"
        strict = int(
            int(row["ambiguous_tokens"]) == 0
            and int(row["reader_unstable_tokens"]) == 0
            and int(row["all_present_exact"]) == 1
        )
        strength_rank = {"HIGH": 4, "MEDIUM": 3, "LOW": 2, "OPEN": 1}.get(strength, 1)
        score = int(row["known_tokens"]) * 1_000_000 + strength_rank * 100_000 + strict * 10_000 - int(row["token_count"]) * 100
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
    for spec_row in EXACT_WHOLE_SPECS:
        if spec_row["surface"] in CONTEXT_SCOPED_SURFACES:
            continue
        glossary_rows.append({
            "surface": spec_row["surface"], "working_meaning_de": spec_row["working_meaning_de"],
            "source": "GDT661:EXACT_WHOLE", "strength": card_strength(spec_row["surface"]),
            "scope_state": "KNOWN_EXACT_WHOLE", "priority": 220,
        })
    glossary_rows.sort(key=lambda row: str(row["surface"]))
    if len(glossary_rows) != 556:
        raise RuntimeError("V38 glossary dimension drift")

    dictionary_rows: list[dict[str, object]] = [dict(row) for row in base_dictionary]
    for spec_row in EXACT_WHOLE_SPECS:
        if spec_row["surface"] in CONTEXT_SCOPED_SURFACES:
            continue
        dictionary_rows.append({
            "entry": f"{spec_row['surface']}@GDT661_EXACT_WHOLE", "kind": "EXACT_WHOLE_SURFACE_CARD",
            "working_meaning_de": spec_row["working_meaning_de"], "composition": spec_row["composition"],
            "context_rule": "only the exact whitespace-delimited surface; no substring inheritance",
            "status": "NEW_V38_PROVISIONAL_CONCRETE_FAMILY_DEFAULT",
        })
    context_cards: list[dict[str, object]] = []
    context_keys = sorted({(str(row["rendering_class"]), str(row["surface"])) for row in occurrence_rows})
    for klass, surface_key in context_keys:
        if klass == "EXACT_WHOLE":
            continue
        members = [
            row for row in occurrence_rows
            if row["rendering_class"] == klass and row["surface"] == surface_key
        ]
        surfaces = sorted({str(row["surface"]) for row in members})
        context_cards.append({
            "card_id": f"G661-C{len(context_cards) + 1:02d}", "rendering_class": klass,
            "surfaces": "|".join(surfaces), "occurrences": len(members),
            "working_render_de": str(members[0]["working_render_de"]),
            "selection_rule": "exact token equality plus physical-line position, right neighbour, or label kind",
            "semantic_effect": (
                "occurrence-scoped lexical card" if surface_key in CONTEXT_SCOPED_SURFACES
                else "punctuation/attachment only; lexical whole-word default remains unchanged"
            ),
        })
        dictionary_rows.append({
            "entry": f"{'|'.join(surfaces)}@GDT661_{klass}", "kind": "EXACT_WHOLE_RENDERING_CARD",
            "working_meaning_de": str(members[0]["working_render_de"]), "composition": klass,
            "context_rule": "exact token equality plus physical-line position, right neighbour, or label kind",
            "status": (
                "NEW_V38_CONTEXT_CARD_NOT_GLOBAL_LEXEME" if surface_key in CONTEXT_SCOPED_SURFACES
                else "NEW_V38_POSITIONAL_RENDER_OF_EXACT_WHOLE"
            ),
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
        row["base_unknown_tokens"] = base_coverage_by_locus[str(row["locus"])]["unknown_tokens"]

    audit_rows: list[dict[str, object]] = []
    reader_rows: list[dict[str, object]] = []
    for occurrence in occurrence_rows:
        locus = str(occurrence["locus"])
        ordinal = int(occurrence["ordinal"])
        base_row = base_coverage_by_locus[locus]
        final_row = coverage_by_locus[locus]
        audit_rows.append({
            **occurrence,
            "v37_gloss_de": split_pipe(base_row["token_glosses_de"])[ordinal - 1],
            "v38_gloss_de": split_pipe(final_row["token_glosses_de"])[ordinal - 1],
            "v37_scope_state": split_pipe(base_row["scope_states"])[ordinal - 1],
            "v38_scope_state": split_pipe(final_row["scope_states"])[ordinal - 1],
            "v38_working_translation_de": line_translation(
                locus, by_line[locus], split_pipe(final_row["token_glosses_de"]),
                y_occurrence_by_token, inherited_target_by_token, target_by_token,
            ),
            "exact_surface_dispatch": int(str(occurrence["surface"]) not in CONTEXT_SCOPED_SURFACES),
            "context_surface_dispatch": int(str(occurrence["surface"]) in CONTEXT_SCOPED_SURFACES),
            "substring_dispatch": 0,
        })
        reader_rows.append({
            "occurrence_id": occurrence["occurrence_id"], "page": occurrence["page"], "locus": locus,
            "ordinal": ordinal, "surface": occurrence["surface"], "position": occurrence["position"],
            "reader_exact": occurrence["reader_exact"], "split_normalized": occurrence["split_normalized"],
            "all_present_exact": occurrence["all_present_exact"], "zl3b_line": occurrence["zl3b_line"],
            "it2a_line": occurrence["it2a_line"], "rf1b_line": occurrence["rf1b_line"],
            "claim_boundary": "reader agreement conditions confidence only; it does not identify plaintext",
        })
    if any(str(row["v37_gloss_de"]) != f"[{row['surface']}:?]" for row in audit_rows):
        raise RuntimeError("not every target occurrence was open in V37")
    if any(GENERIC_FILLER.search(str(row["v38_gloss_de"])) for row in audit_rows):
        raise RuntimeError("generic work filler leaked into GDT661")

    decision_rows: list[dict[str, object]] = []
    accepted_rows: list[dict[str, object]] = []
    for index, spec_row in enumerate(EXACT_WHOLE_SPECS, 1):
        surface = spec_row["surface"]
        members = [row for row in occurrence_rows if row["surface"] == surface]
        decision_rows.append({
            "decision_id": f"G661-D{index:02d}", "surface": surface, "family": spec_row["family"],
            "working_default_de": spec_row["working_meaning_de"], "composition": spec_row["composition"],
            "strongest_rival_de": spec_row["strongest_rival_de"],
            "occurrences": len(members), "lines": len({row["locus"] for row in members}),
            "pages": len({row["page"] for row in members}),
            "reader_exact_occurrences": sum(int(row["reader_exact"]) for row in members),
            "split_normalized_occurrences": sum(int(row["split_normalized"]) for row in members),
            "rendering_classes": "|".join(sorted({str(row["rendering_class"]) for row in members})),
            "strength": card_strength(surface),
            "status": (
                "ACCEPT_V38_CONTEXT_SCOPED_NOT_GLOBAL_LEXEME"
                if surface in CONTEXT_SCOPED_SURFACES
                else "ACCEPT_V38_PROVISIONAL_REPLACEABLE_NO_SUBSTRING_EXPORT"
            ),
        })
        if surface not in CONTEXT_SCOPED_SURFACES:
            accepted_rows.append({
                "surface": surface, "working_meaning_de": spec_row["working_meaning_de"],
                "composition": spec_row["composition"], "strongest_rival_de": spec_row["strongest_rival_de"],
                "strength": card_strength(surface), "occurrences": len(members),
                "scope": "EXACT_WHITESPACE_DELIMITED_WHOLE",
                "status": "ACCEPT_V38_PROVISIONAL_REPLACEABLE_NO_SUBSTRING_EXPORT",
            })

    family_rows: list[dict[str, object]] = []
    for family, anchors in FAMILY_ANCHORS.items():
        targets_in_family = {row["surface"] for row in EXACT_WHOLE_SPECS if row["family"] == family}
        for surface in anchors:
            members = tokens_by_surface.get(surface, [])
            family_rows.append({
                "family": family, "role": "TARGET" if surface in targets_in_family else "VISIBLE_ANCHOR",
                "surface": surface, "occurrences": len(members), "lines": len({row["locus"] for row in members}),
                "pages": len({row["page"] for row in members}),
                "v37_meaning_de": base_glossary.get(surface, {}).get("working_meaning_de", "OPEN"),
                "gdt661_default_de": EXACT_BY_SURFACE.get(surface, {}).get("working_meaning_de", "ANCHOR_ONLY"),
                "claim_scope": "whole-surface comparison; composition does not license substring dispatch",
            })
    if {row["surface"] for row in family_rows if row["role"] == "TARGET"} != TARGET_SURFACES:
        raise RuntimeError("family atlas does not cover every target")

    target_line_rows: list[dict[str, object]] = []
    for locus in sorted(affected_loci):
        members = [row for row in occurrence_rows if row["locus"] == locus]
        base_row, final_row = base_coverage_by_locus[locus], coverage_by_locus[locus]
        target_line_rows.append({
            "page": final_row["page"], "locus": locus, "section": final_row["section"],
            "target_occurrences": len(members),
            "target_ordinals": "|".join(str(row["ordinal"]) for row in members),
            "target_surfaces": "|".join(str(row["surface"]) for row in members),
            "rendering_classes": "|".join(str(row["rendering_class"]) for row in members),
            "zl3b_line": final_row["zl3b_line"],
            "v37_token_glosses_de": base_row["token_glosses_de"],
            "v38_token_glosses_de": final_row["token_glosses_de"],
            "v38_working_translation_de": line_translation(
                locus, by_line[locus], split_pipe(final_row["token_glosses_de"]),
                y_occurrence_by_token, inherited_target_by_token, target_by_token,
            ),
            "v37_unknown_tokens": base_row["unknown_tokens"],
            "v38_unknown_tokens": final_row["unknown_tokens"],
            "v38_complete": int(int(final_row["unknown_tokens"]) == 0),
        })

    frontier_rows: list[dict[str, object]] = []
    for row in frontier:
        surface, locus = row["unknown_surface"], row["locus"]
        final_row = coverage_by_locus[locus]
        frontier_rows.append({
            "rank": row["rank"], "page": row["page"], "locus": locus, "surface": surface,
            "working_default_de": EXACT_BY_SURFACE[surface]["working_meaning_de"],
            "composition": EXACT_BY_SURFACE[surface]["composition"],
            "strongest_rival_de": EXACT_BY_SURFACE[surface]["strongest_rival_de"],
            "strength": card_strength(surface),
            "zl3b_line": row["zl3b_line"],
            "v37_translation_de": row["proposed_complete_translation_de"],
            "v38_translation_de": line_translation(
                locus, by_line[locus], split_pipe(final_row["token_glosses_de"]),
                y_occurrence_by_token, inherited_target_by_token, target_by_token,
            ),
            "status": "COMPLETE_WITH_PROVISIONAL_CONCRETE_DEFAULT",
        })
    if len(frontier_rows) != 48:
        raise RuntimeError("frontier completion count drift")
    if any(f"[{row['surface']}:?]" in str(row["v38_translation_de"]) for row in frontier_rows):
        raise RuntimeError("a frontier target slot remained open")

    base_metrics = metrics(base_coverage, base_one, base_complete, base_glossary_rows)
    final_metrics = metrics(coverage_rows, one_rows, complete_rows, glossary_rows)
    expected_base = {
        "physical_lines": 4128, "known_token_positions": 17579, "unknown_token_positions": 14760,
        "complete_multi_token_lines": 172, "strict_complete_lines": 83,
        "one_unknown_lines": 273, "strict_one_unknown_lines": 68, "working_glossary_surfaces": 510,
    }
    if base_metrics != expected_base:
        raise RuntimeError(f"V37 base metrics drift: {base_metrics!r}")
    expected_final = {
        "physical_lines": 4128, "known_token_positions": 18451, "unknown_token_positions": 13888,
        "complete_multi_token_lines": 233, "strict_complete_lines": 99,
        "one_unknown_lines": 290, "strict_one_unknown_lines": 73, "working_glossary_surfaces": 556,
    }
    if final_metrics != expected_final:
        raise RuntimeError(f"V38 metric drift: {final_metrics!r}")
    if len(newly_completed) != 61 or len(newly_one) != 78:
        raise RuntimeError("V38 completion/frontier delta drift")
    round_rows = [
        {"version": "V37", "added_cards": "BASE", "dictionary_entries": len(base_dictionary), **base_metrics},
        {"version": "V38", "added_cards": f"46_EXACT_WHOLES+2_CONTEXT_SURFACES+{len(context_cards)}_RENDERINGS",
         "dictionary_entries": len(dictionary_rows), **final_metrics},
    ]

    coverage_fields = list(base_coverage[0])
    complete_fields = list(base_complete[0])
    one_fields = list(base_one[0])
    write_tsv(output_dir / "PAGE_ALLOWLIST.tsv", [{"page": page} for page in sorted(pages)], ("page",))
    write_tsv(output_dir / "TARGET_DECISION_DECK.tsv", decision_rows, list(decision_rows[0]))
    write_tsv(output_dir / "ACCEPTED_WHOLE_SURFACE_DEFAULTS.tsv", accepted_rows, list(accepted_rows[0]))
    write_tsv(output_dir / "CONTEXT_RENDERING_CARDS.tsv", context_cards, list(context_cards[0]))
    write_tsv(output_dir / "ALL_OCCURRENCE_SEMANTIC_AUDIT.tsv", audit_rows, list(audit_rows[0]))
    write_tsv(output_dir / "READER_VARIANT_AUDIT.tsv", reader_rows, list(reader_rows[0]))
    write_tsv(output_dir / "FAMILY_COMPOSITION_ATLAS.tsv", family_rows, list(family_rows[0]))
    write_tsv(output_dir / "FRONTIER_48_COMPLETIONS.tsv", frontier_rows, list(frontier_rows[0]))
    write_tsv(output_dir / "TARGET_LINE_TRANSLATIONS.tsv", target_line_rows, list(target_line_rows[0]))
    write_tsv(output_dir / "ROUND_COVERAGE_COUNTS.tsv", round_rows, list(round_rows[0]))
    write_tsv(output_dir / "NEWLY_COMPLETED_LINES.tsv", newly_completed, complete_fields)
    write_tsv(output_dir / "NEWLY_EXPOSED_ONE_HOLE_LINES.tsv", newly_one, ["base_unknown_tokens", *one_fields])
    write_tsv(output_dir / "V38_WORKING_TOKEN_GLOSSARY.tsv", glossary_rows, list(base_glossary_rows[0]))
    write_tsv(output_dir / "WORKING_DICTIONARY_V38.tsv", dictionary_rows, list(base_dictionary[0]))
    write_tsv(output_dir / "ALL_LINE_CONCRETE_COVERAGE_V38.tsv", coverage_rows, coverage_fields)
    write_tsv(output_dir / "COMPLETE_PASSAGES_V38.tsv", complete_rows, complete_fields)
    write_tsv(output_dir / "ONE_UNKNOWN_PASSAGES_V38.tsv", one_rows, one_fields)

    input_paths = (
        G660 / "REPORT.md", G660 / "artifacts/RESULT.json", G660 / "artifacts/PAGE_ALLOWLIST.tsv",
        G660 / "artifacts/V37_WORKING_TOKEN_GLOSSARY.tsv", G660 / "artifacts/WORKING_DICTIONARY_V37.tsv",
        G660 / "artifacts/ALL_LINE_CONCRETE_COVERAGE_V37.tsv", G660 / "artifacts/COMPLETE_PASSAGES_V37.tsv",
        G660 / "artifacts/ONE_UNKNOWN_PASSAGES_V37.tsv", G660 / "artifacts/NEWLY_EXPOSED_ONE_HOLE_LINES.tsv",
        G660 / "artifacts/ALL_OCCURRENCE_SEMANTIC_AUDIT.tsv", g660.G659 / "artifacts/Y_OCCURRENCE_CENSUS.tsv",
        TOKENS_REL, CROSS_REL,
    )
    output_paths = [output_dir / name for name in OUTPUT_NAMES]
    result_core: dict[str, object] = {
        "schema": "GDT661_FORTY_EIGHT_RESIDUAL_FAMILY_COMPLETION_RESULT_V1",
        "experiment_id": "GDT661", "status": STATUS,
        "guard": {
            "allowed_pages": len(pages), "f1r": "EXCLUDED_BY_EXACT_ALLOWLIST",
            "f84": "FORBIDDEN", "f84r": "FORBIDDEN", "new_pages": 0, "new_images": 0,
            "token_query": token_stats, "cross_query": cross_stats,
        },
        "targets": {
            "surface_types": len(TARGET_SURFACES), "exact_whole_surfaces": len(EXACT_WHOLE_SPECS) - 2,
            "context_scoped_surfaces": len(CONTEXT_SCOPED_SURFACES),
            "positions": len(occurrence_rows), "lines": len(affected_loci),
            "pages": len({row["page"] for row in occurrence_rows}), "surface_counts": observed_counts,
            "reader_exact_positions": sum(int(row["reader_exact"]) for row in occurrence_rows),
            "split_normalized_positions": sum(int(row["split_normalized"]) for row in occurrence_rows),
            "rendering_classes": dict(sorted(context_counts.items())),
            "all_positions_concrete": True, "substring_dispatch_positions": 0,
        },
        "coverage": {
            "base": base_metrics, "final": final_metrics, "affected_lines": len(affected_loci),
            "newly_completed_lines": len(newly_completed),
            "newly_completed_loci": sorted(row["locus"] for row in newly_completed),
            "newly_exposed_one_hole_lines": len(newly_one),
            "newly_exposed_one_hole_loci": sorted(row["locus"] for row in newly_one),
            "non_target_token_positions_unchanged": len(non_target_before),
            "non_target_before_sha256": non_target_sha,
            "non_target_after_sha256": canonical_hash(non_target_after),
            "non_target_exactly_unchanged": True,
        },
        "working_dictionary": {
            "v37_entries": len(base_dictionary), "v38_entries": len(dictionary_rows),
            "added_exact_whole_entries": len(EXACT_WHOLE_SPECS) - 2,
            "added_rendering_entries": len(context_cards),
            "v37_glossary_surfaces": len(base_glossary_rows), "v38_glossary_surfaces": len(glossary_rows),
        },
        "frontier": {"source_rows": len(frontier), "completed_rows": len(frontier_rows), "unfilled_target_slots": 0},
        "determinism_contract": {
            "builder_supports_artifact_dir_cli": True,
            "exact_whole_dispatch_requires_token_equality": True,
            "replay_files": [str(BASE_REL / "artifacts" / name) for name in (*OUTPUT_NAMES, "RESULT.json")],
        },
        "claim_boundary": (
            "Exploratory replaceable concrete defaults for exactly forty-eight V37 residual whitespace-delimited surfaces. "
            "All 872 occurrences receive concrete defaults; naked r and d remain occurrence-scoped while positional cards render attachment. Composition is a family model, "
            "not substring dispatch. No glyph identity, phonetics, language, exact historical plaintext, new page, image, f1r, f84 or f84r is asserted."
        ),
        "inputs": {str(path): sha256(ROOT / path) for path in input_paths},
        "outputs": {str(BASE_REL / "artifacts" / path.name): sha256(path) for path in output_paths},
    }
    result = {**result_core, "content_sha256": canonical_hash(result_core)}
    (output_dir / "RESULT.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    return result


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--artifact-dir", type=Path, default=ART)
    args = parser.parse_args(argv)
    result = build(args.artifact_dir)
    if args.artifact_dir.resolve() == ART.resolve():
        with tempfile.TemporaryDirectory(prefix="gdt661_replay_") as directory:
            replay_dir = Path(directory)
            replay_result = build(replay_dir)
            if replay_result != result:
                raise RuntimeError("tempdir RESULT replay differs")
            for name in (*OUTPUT_NAMES, "RESULT.json"):
                if (ART / name).read_bytes() != (replay_dir / name).read_bytes():
                    raise RuntimeError(f"tempdir replay differs: {name}")
    print(
        f"GDT661 built: targets={result['targets']['positions']} wholes=46 context_surfaces=2 "
        f"known={result['coverage']['final']['known_token_positions']} "
        f"complete={result['coverage']['final']['complete_multi_token_lines']} "
        f"one_hole={result['coverage']['final']['one_unknown_lines']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
