#!/usr/bin/env python3
"""Build GDT656: apply one start/middle/end quality axis to observed AL wholes."""
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
BASE_REL = Path("experiments/yolo/gdt656_al_quality_position_shell")
ART = ROOT / BASE_REL / "artifacts"
G655 = Path("experiments/yolo/gdt655_dal_al_measured_material_completion")
G655_RUN = G655 / "src/run.py"
G655_ALLOW = G655 / "artifacts/PAGE_ALLOWLIST.tsv"
G655_COVERAGE = G655 / "artifacts/ALL_LINE_CONCRETE_COVERAGE_V32.tsv"
G655_COMPLETE = G655 / "artifacts/COMPLETE_PASSAGES_V32.tsv"
G655_ONE = G655 / "artifacts/ONE_UNKNOWN_PASSAGES_V32.tsv"
G655_GLOSSARY = G655 / "artifacts/V32_WORKING_TOKEN_GLOSSARY.tsv"
G655_DICTIONARY = G655 / "artifacts/WORKING_DICTIONARY_V32.tsv"
G655_RESULT = G655 / "artifacts/RESULT.json"
G655_REPORT = G655 / "REPORT.md"
G647_REPORT = Path("experiments/yolo/gdt647_quality_subdegree_family_migration/REPORT.md")
G652_REPORT = Path("experiments/yolo/gdt652_strict_v28_frontier_completion/REPORT.md")

spec = importlib.util.spec_from_file_location("gdt655_builder_for_gdt656", ROOT / G655_RUN)
if spec is None or spec.loader is None:
    raise RuntimeError("cannot load GDT655 builder")
g655 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(g655)
TOKENS_REL = g655.TOKENS_REL
CROSS_REL = g655.CROSS_REL
COVERAGE_FIELDS = g655.COVERAGE_FIELDS
ONE_FIELDS = g655.ONE_FIELDS

STATUS = "PASS_21_OBSERVED_AL_POSITION_WHOLES__V33"
GENERIC_FILLER = re.compile(
    r"arbeitsgut|arbeitschritt|arbeitsschritt|arbeitsmittel|arbeitsstoff|"
    r"arbeitsobjekt|werkzeug|produkt weiter|f.hre .* aus|leite .* weiter",
    re.IGNORECASE,
)


def target(
    surface: str,
    mode: str,
    meaning: str,
    composition: str,
    rival: str,
    basis: str,
    counterargument: str,
) -> dict[str, str]:
    return {
        "surface": surface,
        "mode": mode,
        "working_meaning_de": meaning,
        "composition": composition,
        "rival_de": rival,
        "decision_basis": basis,
        "counterargument": counterargument,
    }


TARGET_SPECS = (
    target("chal", "NEW_EXACT_WHOLE", "Rohstoffklasse I, trocken am Gradanfang", "CH_DRY_START+AL_CLASS_I", "trockene Rohstoffform I", "42 occurrences, 35 exact; direct CH AL/CHAL split and complete CH/CHE/CHEE ladder", "CHAL can remain a learned dry materia whole"),
    target("cheal", "NEW_EXACT_WHOLE", "Rohstoffklasse I, trocken in der Gradmitte", "CH_DRY_MIDDLE+AL_CLASS_I", "trocken gebundene Rohstoffform I", "26 occurrences, 25 exact; direct CHE AL split and contrasts with CHAL", "E may be an attributive binder instead of the middle position"),
    target("cheeal", "NEW_EXACT_WHOLE", "Rohstoffklasse I, trocken am Gradende", "CH_DRY_END+AL_CLASS_I", "erweitert gebundene trockene Rohstoffform I", "three occurrences, two exact; fills the observed EE endpoint beside CHAL/CHEAL", "low support and the EEE sister show that E length is not automatically global"),
    target("shal", "NEW_EXACT_WHOLE", "Rohstoffklasse I, feucht am Gradanfang", "SH_MOIST_START+AL_CLASS_I", "feuchte Rohstoffform I", "15 occurrences, 11 exact; zero-E moist sister of SHEAL/SHEEAL", "SHAL can remain a learned moist materia whole"),
    target("sheal", "NEW_EXACT_WHOLE", "Rohstoffklasse I, feucht in der Gradmitte", "SH_MOIST_MIDDLE+AL_CLASS_I", "angefeuchtete Rohstoffform I", "14 occurrences, 13 exact; directly contrasts with CHAL on f58v.18", "E may be an attributive binder instead of the middle position"),
    target("sheeal", "NEW_EXACT_WHOLE", "Rohstoffklasse I, feucht am Gradende", "SH_MOIST_END+AL_CLASS_I", "stark angefeuchtete Rohstoffform I", "two occurrences, one exact; closes f108v.40 and completes the observed moist endpoint", "one reader-stable anchor is weak support for the EE endpoint"),
    target("kal", "NEW_EXACT_WHOLE", "Rohstoffklasse I, heiß am Gradanfang", "K_HOT_START+AL_CLASS_I", "heiße Rohstoffform I", "25 occurrences, 14 exact; hot start cell recurs under O and QO", "bare KAL is reader-variable and can be an indivisible learned whole"),
    target("tal", "NEW_EXACT_WHOLE", "Rohstoffklasse I, kalt am Gradanfang", "T_COLD_START+AL_CLASS_I", "kalte Rohstoffform I", "20 occurrences, 14 exact; cold start cell recurs under O and QO", "bare TAL is reader-variable and can be an indivisible learned whole"),
    target("oal", "NEW_EXACT_WHOLE", "Rohstoffklasse I im Ansatz", "O_PREP+AL_CLASS_I", "Rohstoffform I im Ansatz", "two occurrences, both exact; direct O AL/OAL boundary witness", "two occurrences cannot establish whether O is semantic or orthographic"),
    target("oeeal", "NEW_EXACT_WHOLE_LOCAL_ANALOGY", "Rohstoffklasse I im Ansatz, am Gradende", "OEEAL_EXACT_WHOLE_LOCAL_ANALOGY;O_AL_PARALLEL;EE_END_RIVAL", "gelerntes OEEAL-Ganzwort oder Rohstoffauszug der Klasse I", "two occurrences, both exact; f104r.14 places QOTAL ... OTAL ... OEEAL, f112v.43 places OOEEOR immediately before OEEAL and AL later in the line, and OEEAR has three exact material-context sisters", "there is no OEAL middle cell, no O|EE|AL boundary and no visible quality head, so the EE reading is licensed only for this exact whole"),
    target("okal", "REVISE_AL_QUALITY_MODEL", "Rohstoffklasse I im Ansatz, heiß am Gradanfang", "O_PREP+K_HOT_START+AL_CLASS_I", "Ansatz aus heißem Rohstoff, Form I", "123 occurrences, 102 exact; three O KAL/OKAL boundaries and the completed AL model", "the old fluent preparation reading remains viable"),
    target("okeal", "NEW_EXACT_WHOLE", "Rohstoffklasse I im Ansatz, heiß in der Gradmitte", "O_PREP+K_HOT_MIDDLE+AL_CLASS_I", "heiß gebundene Rohstoffform I im Ansatz", "ten occurrences, eight exact; E-marked sister of OKAL", "E may be binding rather than a middle-position marker"),
    target("otal", "REVISE_AL_QUALITY_MODEL", "Rohstoffklasse I im Ansatz, kalt am Gradanfang", "O_PREP+T_COLD_START+AL_CLASS_I", "Ansatz aus kaltem Rohstoff, Form I", "119 occurrences, 109 exact; direct OT AL/OTAL split and the completed AL model", "the old fluent preparation reading remains viable"),
    target("oteal", "NEW_EXACT_WHOLE", "Rohstoffklasse I im Ansatz, kalt in der Gradmitte", "O_PREP+T_COLD_MIDDLE+AL_CLASS_I", "kalt gebundene Rohstoffform I im Ansatz", "five occurrences, all exact; E-marked sister of OTAL", "low support leaves a learned whole possible"),
    target("oteeal", "NEW_EXACT_WHOLE", "Rohstoffklasse I im Ansatz, kalt am Gradende", "O_PREP+T_COLD_END+AL_CLASS_I", "erweitert gebundene kalte Rohstoffform I im Ansatz", "one all-reader exact occurrence fills the observed EE endpoint", "a singleton cannot independently identify the endpoint meaning"),
    target("qoal", "NEW_EXACT_WHOLE", "Rohstoffklasse I", "QO_SCOPE+AL_CLASS_I", "Rohstoffform I im QO-Rahmen", "five occurrences, four exact; observed QO sister of AL", "QO may contribute an unsuppressed lexical value"),
    target("qokal", "REVISE_AL_QUALITY_MODEL", "Rohstoffklasse I, heiß am Gradanfang", "QO_SCOPE+K_HOT_START+AL_CLASS_I", "heiße Substanz", "180 occurrences, 158 exact; QOKAL/QOTAL contrast and the completed AL model", "QO may change the head class, and the old generic substance reading is frequent"),
    target("qokeal", "NEW_EXACT_WHOLE", "Rohstoffklasse I, heiß in der Gradmitte", "QO_SCOPE+K_HOT_MIDDLE+AL_CLASS_I", "heiß gebundene Rohstoffform I", "four occurrences, all exact; E-marked sister of QOKAL", "four occurrences cannot exclude a learned whole"),
    target("qokeeal", "NEW_EXACT_WHOLE", "Rohstoffklasse I, heiß am Gradende", "QO_SCOPE+K_HOT_END+AL_CLASS_I", "erweitert gebundene heiße Rohstoffform I", "two occurrences, one exact; observed EE endpoint beside QOKAL/QOKEAL", "one stable anchor is weak support for the endpoint"),
    target("qotal", "NEW_EXACT_WHOLE", "Rohstoffklasse I, kalt am Gradanfang", "QO_SCOPE+T_COLD_START+AL_CLASS_I", "kalte Rohstoffform I im QO-Rahmen", "57 occurrences, 54 exact; recurrent cold sister of QOKAL and closes f83r.43", "QO may change the head class"),
    target("qoteal", "NEW_EXACT_WHOLE", "Rohstoffklasse I, kalt in der Gradmitte", "QO_SCOPE+T_COLD_MIDDLE+AL_CLASS_I", "kalt gebundene Rohstoffform I", "two occurrences, both exact; E-marked sister of QOTAL", "a two-token sample cannot exclude a learned whole"),
)
TARGET_BY_SURFACE = {row["surface"]: row for row in TARGET_SPECS}
EXPECTED_COUNTS = {
    "chal": (42, 26, 35, 35), "cheal": (26, 13, 25, 25), "cheeal": (3, 3, 2, 2),
    "shal": (15, 12, 11, 11), "sheal": (14, 12, 13, 13), "sheeal": (2, 2, 1, 1),
    "kal": (25, 21, 14, 14), "tal": (20, 13, 14, 14), "oal": (2, 2, 2, 2),
    "oeeal": (2, 2, 2, 2),
    "okal": (123, 64, 102, 102), "okeal": (10, 8, 8, 8),
    "otal": (119, 57, 109, 109), "oteal": (5, 4, 5, 5), "oteeal": (1, 1, 1, 1),
    "qoal": (5, 5, 4, 4), "qokal": (180, 54, 158, 158),
    "qokeal": (4, 4, 4, 4), "qokeeal": (2, 2, 1, 1),
    "qotal": (57, 36, 54, 54), "qoteal": (2, 2, 2, 2),
}
OBSERVED_HOLDS = {
    "cheeeal": (1, 1, 1, 1, "OBSERVED_EEE_OUTSIDE_THREE_POSITION_AXIS"),
    "keeal": (1, 1, 0, 0, "OBSERVED_ZERO_EXACT_SUPERFORM_WARNING"),
    "eeal": (1, 1, 0, 0, "OBSERVED_UNHEADED_ZERO_EXACT_WARNING"),
}
GRID_ROOTS = ("ch", "sh", "k", "t", "ok", "ot", "qok", "qot")
POSITION_BY_E = {0: "START", 1: "MIDDLE", 2: "END", 3: "EEE_OUTSIDE_AXIS"}

BOUNDARY_SPECS = (
    ("G656-B01", "CH_AL_SPLIT", "f116r.50", "ch al / chal", "reader boundary exposes CH plus AL"),
    ("G656-B02", "CHE_AL_SPLIT", "f58v.12", "cheal / che al", "reader boundary exposes CHE plus AL"),
    ("G656-B03", "O_AL_SPLIT", "f86v5.28", "o al / oal", "reader boundary exposes O plus AL"),
    ("G656-B04", "O_KAL_SPLIT", "f8r.20", "o kal / okal", "first reader boundary exposes O plus KAL"),
    ("G656-B05", "O_KAL_SPLIT", "f107v.37", "o kal / okal", "second reader boundary exposes O plus KAL"),
    ("G656-B06", "O_KAL_SPLIT", "f116r.20", "o kal / okal", "third reader boundary exposes O plus KAL"),
    ("G656-B07", "OT_AL_SPLIT", "f105v.15", "ot al / otal", "reader boundary exposes OT plus AL"),
    ("G656-B08", "KEEAL_SUPERFORM_WARNING", "f78r.34", "o keeal / okeeal", "warning: KEEAL has no all-reader exact anchor and remains held"),
)

PAIR_SPECS = (
    ("chal", "cheal", "trocken am Gradanfang / in der Gradmitte"),
    ("chal", "sheal", "trocken am Gradanfang / feucht in der Gradmitte"),
    ("okal", "otal", "heißer / kalter Rohstoffansatz am Gradanfang"),
    ("qokal", "qotal", "heißer / kalter Rohstoff am Gradanfang"),
    ("cheal", "cheeal", "trocken in der Gradmitte / am Gradende"),
)

HISTORICAL_COMPARATORS = (
    ("G656-H01", "1415", "Tadhg Ó Cuinn, An Irish Materia Medica", "drug lemma plus hot/cold/dry/wet quality", "https://celt.ucc.ie/published/G600005/index.html", "supports a mixed learned-head plus compact quality notation"),
    ("G656-H02", "1415", "Uiola entry", "beginning of one degree and end of another are both stated", "https://celt.ucc.ie/published/G600006/text890.html", "supports distinct START and END positions within numbered qualities"),
    ("G656-H03", "1415", "Nux longa entry", "middle of one degree contrasts with end of another", "https://celt.ucc.ie/published/G600005/text825.html", "supports distinct MIDDLE and END positions within numbered qualities"),
)

# These rows support or limit OEEAL without releasing EE as a free component.
# surface: carrier, role, occurrences, pages, exact, normalized, interpretation, decision
LOCAL_EE_SISTER_SPECS = (
    ("oeeal", "AL", "TARGET_LOCAL_ANALOGY", 2, 2, 2, 2, "Rohstoffklasse I im Ansatz, am Gradende", "ACCEPT_EXACT_WHOLE_ONLY"),
    ("oeear", "AR", "EXACT_MATERIAL_SISTER", 3, 3, 3, 3, "Fraktionsschwester im Ansatz-/Gradmilieu", "SUPPORT_ANALOGY_ONLY"),
    ("eal", "AL", "MISSING_MIDDLE_RIVAL", 0, 0, 0, 0, "keine beobachtete nackte Mittelzelle", "ABSENT_HOLD"),
    ("oeal", "AL", "MISSING_MIDDLE_RIVAL", 0, 0, 0, 0, "keine beobachtete O-Mittelzelle", "ABSENT_HOLD"),
    ("eeal", "AL", "UNHEADED_READER_WARNING", 1, 1, 0, 0, "unbelegte unqualifizierte Endlesung", "OBSERVED_ZERO_EXACT_HOLD"),
)

REALITY_LOCI = {
    "chal": ("f83v.16",), "cheal": ("f58r.13",), "cheeal": ("f51r.12",),
    "sheal": ("f58v.18",), "sheeal": ("f108v.40",), "oteeal": ("f103r.41",),
    "oeeal": ("f104r.14", "f112v.43"), "qokeeal": ("f111r.41",),
    "qotal": ("f83r.43",),
}

CURATED_REALITY_READINGS = {
    "f104r.14": "Grad-/Maßwert III; [choaiin]; [qokechy]; Rohstoffklasse I, kalt am Gradanfang; [cheolor]; Samen/Saatgut Typ III; [olkeechey]; Rohstoffklasse I im Ansatz, kalt am Gradanfang; Gut/Ansatz; Rohstoffklasse I im Ansatz, am Gradende.",
    "f112v.43": "[ooeeor]; Rohstoffklasse I im Ansatz, am Gradende; [olkeol]; Rohstoffklasse I; trockenes Material; [chl]; [olchedy]; [ykeedy]; [chtal]; heiße Drogenfraktion I; [opchy]; [famam].",
}

CURATED_COMPLETE_READINGS = {
    "f83v.16": "Grad-/Maßwert III; Rohstoffklasse I, heiß am Gradanfang; feuchtes Arzneikompositum in der Gradmitte; heiß am Gradende; Rohstoffklasse I, trocken am Gradanfang; nochmals heiß am Gradende; heiß, Grad III; trocken in der Gradmitte, abgeschlossen; Samenfraktion I; Rohstoffklasse I.",
    "f83r.43": "Grad-/Maßwert III; feuchtes Material; trocken in der Gradmitte, abgeschlossen; Rohstoffklasse I, kalt am Gradanfang; Samenfraktion I.",
    "f108v.40": "Grad-/Maßwert III; Rohstoffklasse I, feucht am Gradende; dreimal heiß am Gradende, jeweils abgeschlossen; kalt in der Gradmitte; zweimal heiß am Gradende; kalter Ansatz in der Gradmitte, abgeschlossen; kalt, Grad III.",
}

CURATED_READER_NOTES = {
    "f83v.16": "dreileser-strikt",
    "f83r.43": "ZL3b-Arbeitslesung; IT2a hat qotyl/rar, RF1b qokal/sar",
    "f108v.40": "ZL3b-Arbeitslesung; RF1b spaltet erstes qokeedy als qokee y und liest oted statt otedy",
}

OUTPUT_NAMES = (
    "PAGE_ALLOWLIST.tsv", "TARGET_DECISION_DECK.tsv", "AL_QUALITY_LATTICE_ATLAS.tsv",
    "BOUNDARY_EVIDENCE_ATLAS.tsv", "PAIR_CONTRAST_COUNTS.tsv",
    "HISTORICAL_SUBDEGREE_COMPARATORS.tsv", "LOCAL_EE_SISTER_EVIDENCE.tsv", "REVISION_LEDGER.tsv",
    "ALL_OCCURRENCE_SEMANTIC_AUDIT.tsv", "READER_VARIANT_AUDIT.tsv",
    "ROUND_COVERAGE_COUNTS.tsv", "ACCEPTED_WHOLE_SURFACE_DEFAULTS.tsv",
    "SOURCE_PASSAGE_REALITY_CHECK.tsv", "CURATED_COMPLETE_PASSAGE_READINGS.tsv",
    "AFFECTED_LINE_TRANSLATIONS.tsv", "NEWLY_COMPLETED_LINES.tsv",
    "NEWLY_EXPOSED_ONE_HOLE_LINES.tsv", "V33_WORKING_TOKEN_GLOSSARY.tsv",
    "ALL_LINE_CONCRETE_COVERAGE_V33.tsv", "COMPLETE_PASSAGES_V33.tsv",
    "ONE_UNKNOWN_PASSAGES_V33.tsv", "WORKING_DICTIONARY_V33.tsv",
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
        "working_glossary_surfaces": len(glossary),
    }


def dictionary_row(spec_row: dict[str, str], round_number: int, occurrences: int, exact_count: int) -> dict[str, object]:
    return {
        "entry": f"{spec_row['surface']}@GDT656_EXACT_WHOLE",
        "kind": f"EXACT_ZL3B_WHOLE_{spec_row['mode']}",
        "working_meaning_de": spec_row["working_meaning_de"],
        "composition": spec_row["composition"],
        "context_rule": (
            f"exact complete surface only; mode={spec_row['mode']}; {occurrences} audited occurrences; "
            f"{exact_count} all-reader exact; supersedes current glossary card without deleting material history"
        ),
        "status": f"NEW_V33_ACCEPTED_ROUND_{round_number:02d}",
    }


def line_position(line: list[dict[str, object]], token_index: int) -> int:
    for ordinal, token in enumerate(line, 1):
        if int(token["token_index"]) == token_index:
            return ordinal
    raise RuntimeError("token position not found")


def build(output_dir: Path) -> dict[str, object]:
    output_dir.mkdir(parents=True, exist_ok=True)
    pages = {row["page"] for row in read_tsv(ROOT / G655_ALLOW)}
    if "f1r" in pages or any(page.startswith("f84") for page in pages):
        raise RuntimeError("allow-list contains excluded or forbidden page")
    guarded_query = g655.g654.g653.g637.g636.g635.g634.g633.g632.g631.guarded_query
    token_rows, token_stats = guarded_query(
        TOKENS_REL, pages, "page,locus,token_index,eva,section,language,hand",
    )
    cross_rows, cross_stats = guarded_query(
        CROSS_REL, pages, "page,locus,all_three_present,all_present_exact,zl3b_clean,it2a_clean,rf1b_clean",
    )
    cross_by_locus = {row["locus"]: row for row in cross_rows}
    by_line, _ = g655.g654.g653.g637.g636.g635.g634.g633.g632.g631.line_maps([dict(row) for row in token_rows])
    exact, boundary = g655.g654.g653.g637.g636.g635.g634.stable_maps(token_rows, cross_by_locus)

    base_dictionary = [dict(row) for row in read_tsv(ROOT / G655_DICTIONARY)]
    base_gloss_rows = read_tsv(ROOT / G655_GLOSSARY)
    base_glossary = {row["surface"]: dict(row) for row in base_gloss_rows}
    base_coverage = read_tsv(ROOT / G655_COVERAGE)
    base_complete = read_tsv(ROOT / G655_COMPLETE)
    base_one = read_tsv(ROOT / G655_ONE)
    if (len(base_dictionary), len(base_glossary), len(base_coverage), len(base_complete), len(base_one)) != (529, 453, 4128, 130, 225):
        raise RuntimeError("GDT655 V32 base counts changed")
    edition = g655.g654.g653.g637
    replay_coverage, replay_one, _, replay_complete = edition.build_line_coverage(
        by_line, base_glossary, exact, boundary, cross_by_locus,
    )
    if (string_rows(replay_coverage) != string_rows(base_coverage)
            or string_rows(replay_complete) != string_rows(base_complete)
            or string_rows(replay_one) != string_rows(base_one)):
        raise RuntimeError("GDT655 V32 editions do not replay")
    base_metrics = metrics(replay_coverage, replay_one, replay_complete, base_glossary)
    expected_base = {
        "physical_lines": 4128, "known_token_positions": 16398,
        "unknown_token_positions": 15941, "complete_multi_token_lines": 130,
        "strict_complete_lines": 77, "one_unknown_lines": 225,
        "strict_one_unknown_lines": 54, "working_glossary_surfaces": 453,
    }
    if base_metrics != expected_base:
        raise RuntimeError(f"GDT655 V32 metrics changed: {base_metrics!r}")

    if any(GENERIC_FILLER.search(row["working_meaning_de"]) for row in TARGET_SPECS):
        raise RuntimeError("generic filler in GDT656 target deck")
    new_surfaces = tuple(row["surface"] for row in TARGET_SPECS if row["mode"].startswith("NEW"))
    if any(surface in base_glossary for surface in new_surfaces):
        raise RuntimeError("new GDT656 target unexpectedly exists in V32 glossary")
    expected_old = {
        "okal": "Ansatz aus heißem Rohstoff, Form I",
        "otal": "Ansatz aus kaltem Rohstoff, Form I",
        "qokal": "heiße Substanz",
    }
    if any(base_glossary.get(surface, {}).get("working_meaning_de") != meaning for surface, meaning in expected_old.items()):
        raise RuntimeError("V32 AL quality revision base changed")

    token_counts = Counter(str(row["eva"]) for row in token_rows)
    for surface, expected in EXPECTED_COUNTS.items():
        members = [row for row in token_rows if row["eva"] == surface]
        observed = (
            len(members), len({row["page"] for row in members}),
            sum(exact[row["locus"], int(row["token_index"])] for row in members),
            sum(boundary[row["locus"], int(row["token_index"])] for row in members),
        )
        if observed != expected:
            raise RuntimeError(f"target count drift: {surface}: {observed!r}")
    for surface, expected in OBSERVED_HOLDS.items():
        members = [row for row in token_rows if row["eva"] == surface]
        observed = (
            len(members), len({row["page"] for row in members}),
            sum(exact[row["locus"], int(row["token_index"])] for row in members),
            sum(boundary[row["locus"], int(row["token_index"])] for row in members),
        )
        if observed != expected[:4]:
            raise RuntimeError(f"hold count drift: {surface}: {observed!r}")

    lattice_specs: list[tuple[str, str, str, str]] = [("BASE", "al", "AL", "BASE")]
    lattice_specs.extend((root.upper(), f"{root}{'e' * level}al", f"{root.upper()}+{'E' * level if level else 'ZERO_E'}+AL", POSITION_BY_E[level]) for root in GRID_ROOTS for level in range(4))
    lattice_specs.extend((
        ("O_UNQUALIFIED", "oal", "O+AL", "UNQUALIFIED_BASE"),
        ("O_UNQUALIFIED", "oeal", "OEAL_UNOBSERVED_WHOLE", "ABSENT_INTERMEDIATE_RIVAL"),
        ("O_UNQUALIFIED", "oeeal", "OEEAL_EXACT_WHOLE;O_AL_PARALLEL", "LOCAL_END_FORM_ANALOGY"),
        ("O_UNQUALIFIED", "oeeeal", "OEEEAL_UNOBSERVED_WHOLE", "EEE_OUTSIDE_AXIS"),
        ("QO_UNQUALIFIED", "qoal", "QO+AL", "UNQUALIFIED_BASE"),
        ("QO_UNQUALIFIED", "qoeal", "QOEAL_UNOBSERVED_WHOLE", "UNLICENSED_POSITION_RIVAL"),
        ("QO_UNQUALIFIED", "qoeeal", "QOEEAL_UNOBSERVED_WHOLE", "UNLICENSED_POSITION_RIVAL"),
        ("QO_UNQUALIFIED", "qoeeeal", "QOEEEAL_UNOBSERVED_WHOLE", "EEE_OUTSIDE_AXIS"),
        ("NO_VISIBLE_HEAD", "eal", "EAL_UNOBSERVED_WHOLE", "UNHEADED_RIVAL"),
        ("NO_VISIBLE_HEAD", "eeal", "EEAL_READER_UNSTABLE_WHOLE", "UNHEADED_RIVAL"),
        ("NO_VISIBLE_HEAD", "eeeal", "EEEAL_UNOBSERVED_WHOLE", "EEE_OUTSIDE_AXIS"),
    ))
    lattice_rows: list[dict[str, object]] = []
    for family, surface, decomposition, position in lattice_specs:
        members = [row for row in token_rows if row["eva"] == surface]
        base_row = base_glossary.get(surface)
        target_row = TARGET_BY_SURFACE.get(surface)
        if target_row:
            final_status = "ACCEPTED_V33"
            meaning = target_row["working_meaning_de"]
        elif surface == "al":
            final_status = "V32_BASE"
            meaning = base_row["working_meaning_de"] if base_row else "NOT_ASSIGNED"
        elif surface in OBSERVED_HOLDS:
            final_status = OBSERVED_HOLDS[surface][4]
            meaning = "NOT_ASSIGNED"
        else:
            final_status = "ABSENT_HOLD" if not members else "OBSERVED_UNREGISTERED_HOLD"
            meaning = "NOT_ASSIGNED"
        lattice_rows.append({
            "family": family, "surface": surface, "decomposition": decomposition,
            "quality_position": position,
            "v32_meaning_de": base_row["working_meaning_de"] if base_row else "OPEN",
            "v33_meaning_de": meaning, "zl3b_occurrences": len(members),
            "pages": len({row["page"] for row in members}),
            "reader_exact_occurrences": sum(exact[row["locus"], int(row["token_index"])] for row in members),
            "split_normalized_occurrences": sum(boundary[row["locus"], int(row["token_index"])] for row in members),
            "final_status": final_status,
        })

    boundary_rows: list[dict[str, object]] = []
    for bridge_id, evidence_type, locus, diagnostic, support in BOUNDARY_SPECS:
        row = cross_by_locus.get(locus)
        if row is None:
            raise RuntimeError(f"missing GDT656 boundary locus: {locus}")
        boundary_rows.append({
            "bridge_id": bridge_id, "evidence_type": evidence_type, "page": row["page"],
            "locus": locus, "diagnostic_surface": diagnostic, "zl3b_line": row["zl3b_clean"],
            "it2a_line": row["it2a_clean"], "rf1b_line": row["rf1b_clean"], "supports": support,
        })

    line_surfaces = {locus: {str(token["eva"]) for token in line} for locus, line in by_line.items()}
    pair_rows: list[dict[str, object]] = []
    for first, second, distinction in PAIR_SPECS:
        loci = sorted(locus for locus, surfaces in line_surfaces.items() if first in surfaces and second in surfaces)
        pair_rows.append({
            "first_surface": first, "second_surface": second, "required_distinction_de": distinction,
            "cooccurrence_lines": len(loci),
            "all_reader_exact_lines": sum(int(cross_by_locus[locus]["all_three_present"]) == 1 and int(cross_by_locus[locus]["all_present_exact"]) == 1 for locus in loci),
            "example_loci": "|".join(loci[:12]) or "NONE",
        })

    historical_rows = [
        {"comparator_id": row[0], "date": row[1], "source": row[2], "observed_architecture": row[3], "source_url": row[4], "supports": row[5]}
        for row in HISTORICAL_COMPARATORS
    ]
    local_ee_sister_rows: list[dict[str, object]] = []
    for evidence_number, spec_row in enumerate(LOCAL_EE_SISTER_SPECS, 1):
        surface, carrier, role, occurrences, page_count, exact_count, normalized_count, interpretation, decision = spec_row
        members = [row for row in token_rows if row["eva"] == surface]
        observed = (
            len(members), len({row["page"] for row in members}),
            sum(exact[row["locus"], int(row["token_index"])] for row in members),
            sum(boundary[row["locus"], int(row["token_index"])] for row in members),
        )
        expected = (occurrences, page_count, exact_count, normalized_count)
        if observed != expected:
            raise RuntimeError(f"local EE sister count drift: {surface}: {observed!r}")
        local_ee_sister_rows.append({
            "evidence_id": f"G656-S{evidence_number:02d}", "surface": surface,
            "carrier": carrier, "role": role, "occurrences": occurrences,
            "pages": page_count, "reader_exact_occurrences": exact_count,
            "split_normalized_occurrences": normalized_count,
            "loci": "|".join(sorted({str(row["locus"]) for row in members})) or "NONE",
            "working_interpretation_de": interpretation, "decision": decision,
        })

    glossary = {key: dict(value) for key, value in base_glossary.items()}
    coverage, one_unknown, _, complete = edition.build_line_coverage(by_line, glossary, exact, boundary, cross_by_locus)
    base_complete_loci = {row["locus"] for row in base_complete}
    seen_one_loci = {row["locus"] for row in base_one}
    accepted_dictionary_rows: list[dict[str, object]] = []
    target_deck: list[dict[str, object]] = []
    audit_rows: list[dict[str, object]] = []
    variant_rows: list[dict[str, object]] = []
    revision_rows: list[dict[str, object]] = []
    round_rows: list[dict[str, object]] = [{
        "round": 0, "surface": "BASE_V32", "mode": "BASE", "dictionary_entries": len(base_dictionary),
        "dictionary_sha256": canonical_hash(base_dictionary), **base_metrics,
    }]
    newly_exposed_rows: list[dict[str, object]] = []

    for round_number, raw_spec in enumerate(TARGET_SPECS, 1):
        spec_row = {key: str(value) for key, value in raw_spec.items()}
        surface = spec_row["surface"]
        members = [row for row in token_rows if row["eva"] == surface]
        members.sort(key=lambda row: (row["page"], row["locus"], int(row["token_index"])))
        exact_count = sum(exact[row["locus"], int(row["token_index"])] for row in members)
        normalized_count = sum(boundary[row["locus"], int(row["token_index"])] for row in members)
        if len(members) != token_counts[surface] or exact_count == 0:
            raise RuntimeError(f"target occurrence or exact-anchor drift: {surface}")
        pre_by_locus = {row["locus"]: row for row in coverage}
        old_gloss = base_glossary.get(surface, {}).get("working_meaning_de", "OPEN")
        edition.set_gloss(
            glossary, surface, spec_row["working_meaning_de"], f"GDT656:{spec_row['mode']}",
            "EXACT_WHOLE_AL_QUALITY_POSITION_SHELL", "KNOWN_EXACT_WHOLE", 154,
        )
        coverage, one_unknown, _, complete = edition.build_line_coverage(by_line, glossary, exact, boundary, cross_by_locus)
        post_by_locus = {row["locus"]: row for row in coverage}
        accepted_dictionary_rows.append(dictionary_row(spec_row, round_number, len(members), exact_count))
        if spec_row["mode"].startswith("REVISE"):
            revision_rows.append({
                "surface": surface, "mode": spec_row["mode"], "v32_meaning_de": old_gloss,
                "v33_meaning_de": spec_row["working_meaning_de"], "occurrences": len(members),
                "reader_exact_occurrences": exact_count, "reason": spec_row["decision_basis"],
            })

        for occurrence, member in enumerate(members, 1):
            locus, token_index = member["locus"], int(member["token_index"])
            line = by_line[locus]
            ordinal = line_position(line, token_index)
            before, after = pre_by_locus[locus], post_by_locus[locus]
            before_glosses, after_glosses = split_pipe(before["token_glosses_de"]), split_pipe(after["token_glosses_de"])
            reader_exact = exact[locus, token_index]
            normalized = boundary[locus, token_index]
            support = "ALL_THREE_EXACT" if reader_exact else "ALL_THREE_SPLIT_NORMALIZED" if normalized else "READER_VARIANT"
            known_other = int(before["known_tokens"]) - int(before["ambiguous_tokens"]) - int(before["reader_unstable_tokens"])
            verdict = "READER_VARIANT_WARNING" if support == "READER_VARIANT" else "CONCRETE_CONTEXT_COMPATIBLE" if known_other >= 2 else "SHORT_OR_OPAQUE_CONTEXT"
            audit_rows.append({
                "audit_id": f"G656-A{round_number:02d}-{occurrence:04d}", "round": round_number,
                "surface": surface, "mode": spec_row["mode"], "page": member["page"], "locus": locus,
                "section": member["section"], "language": member["language"], "hand": member["hand"],
                "token_ordinal": ordinal,
                "line_position": "ONLY" if len(line) == 1 else "INITIAL" if ordinal == 1 else "FINAL" if ordinal == len(line) else "MEDIAL",
                "previous": "<BOS>" if ordinal == 1 else line[ordinal - 2]["eva"],
                "following": "<EOS>" if ordinal == len(line) else line[ordinal]["eva"],
                "zl3b_line": before["zl3b_line"], "it2a_line": cross_by_locus[locus]["it2a_clean"],
                "rf1b_line": cross_by_locus[locus]["rf1b_clean"], "reader_support": support,
                "reader_exact": reader_exact, "split_normalized": normalized,
                "before_gloss_de": before_glosses[ordinal - 1], "after_gloss_de": after_glosses[ordinal - 1],
                "known_other_tokens": known_other, "v32_line_de": before["token_glosses_de"],
                "v33_line_de": after["token_glosses_de"], "hard_collision": 0, "verdict": verdict,
            })
            if support != "ALL_THREE_EXACT":
                variant_rows.append({
                    "surface": surface, "page": member["page"], "locus": locus,
                    "zl3b_line": before["zl3b_line"], "it2a_line": cross_by_locus[locus]["it2a_clean"],
                    "rf1b_line": cross_by_locus[locus]["rf1b_clean"], "reader_support": support,
                    "working_meaning_de": spec_row["working_meaning_de"],
                    "decision": "RETAIN_EXACT_ZL3B_WITH_READER_WARNING",
                })

        current_one_by_locus = {row["locus"]: row for row in one_unknown}
        for locus in sorted(set(current_one_by_locus) - seen_one_loci):
            newly_exposed_rows.append({
                "introduced_round": round_number, "enabled_by_surface": surface,
                **{field: current_one_by_locus[locus][field] for field in ONE_FIELDS},
            })
        seen_one_loci.update(current_one_by_locus)
        post_dictionary = [*base_dictionary, *accepted_dictionary_rows]
        target_deck.append({
            "candidate_id": f"G656-C{round_number:02d}", "candidate_order": round_number,
            "surface": surface, "mode": spec_row["mode"], "v32_meaning_de": old_gloss,
            "v33_meaning_de": spec_row["working_meaning_de"], "composition": spec_row["composition"],
            "rival_de": spec_row["rival_de"], "occurrences": len(members),
            "pages": len({row["page"] for row in members}), "reader_exact_occurrences": exact_count,
            "split_normalized_occurrences": normalized_count, "reader_variant_occurrences": len(members) - normalized_count,
            "decision": "ACCEPT_V33_EXACT_WHOLE", "decision_basis": spec_row["decision_basis"],
            "strongest_counterargument": spec_row["counterargument"],
        })
        round_rows.append({
            "round": round_number, "surface": surface, "mode": spec_row["mode"],
            "dictionary_entries": len(post_dictionary), "dictionary_sha256": canonical_hash(post_dictionary),
            **metrics(coverage, one_unknown, complete, glossary),
        })

    final_dictionary = [*base_dictionary, *accepted_dictionary_rows]
    final_coverage, final_one, _, final_complete = edition.build_line_coverage(by_line, glossary, exact, boundary, cross_by_locus)
    final_by_locus = {row["locus"]: row for row in final_coverage}
    base_by_locus = {row["locus"]: row for row in base_coverage}
    final_complete_by_locus = {row["locus"]: row for row in final_complete}
    final_metrics = metrics(final_coverage, final_one, final_complete, glossary)
    expected_final = {
        "physical_lines": 4128, "known_token_positions": 16635,
        "unknown_token_positions": 15704, "complete_multi_token_lines": 133,
        "strict_complete_lines": 78, "one_unknown_lines": 239,
        "strict_one_unknown_lines": 57, "working_glossary_surfaces": 471,
    }
    if final_metrics != expected_final:
        raise RuntimeError(f"unexpected V33 core metrics: {final_metrics!r}")
    final_gloss_rows = [
        {key: row[key] for key in ("surface", "working_meaning_de", "source", "strength", "scope_state", "priority")}
        for row in sorted(glossary.values(), key=lambda item: str(item["surface"]))
    ]

    targets = set(TARGET_BY_SURFACE)
    affected_rows: list[dict[str, object]] = []
    for locus in sorted(by_line):
        present = list(dict.fromkeys(token["eva"] for token in by_line[locus] if token["eva"] in targets))
        if not present:
            continue
        row = final_by_locus[locus]
        affected_rows.append({
            "page": row["page"], "locus": locus, "target_surfaces": "|".join(present),
            "zl3b_line": row["zl3b_line"], "v32_tokenwise_de": base_by_locus[locus]["token_glosses_de"],
            "v33_tokenwise_de": row["token_glosses_de"], "complete_v33": int(row["unknown_tokens"]) == 0,
        })

    new_complete_rows: list[dict[str, object]] = []
    for locus in sorted(set(final_complete_by_locus) - base_complete_loci):
        row = final_by_locus[locus]
        present = list(dict.fromkeys(token["eva"] for token in by_line[locus] if token["eva"] in targets))
        new_complete_rows.append({
            "page": row["page"], "locus": locus, "strict_complete": final_complete_by_locus[locus]["strict_complete"],
            "enabled_by_surfaces": "|".join(present), "zl3b_line": row["zl3b_line"],
            "literal_v33_de": "; ".join(split_pipe(row["token_glosses_de"])),
            "curated_workshop_reading_de": CURATED_COMPLETE_READINGS.get(locus, "NOT_CURATED"),
        })

    accepted_defaults = [{
        "surface": row["entry"].split("@", 1)[0], **row,
        "occurrences": next(item["occurrences"] for item in target_deck if item["surface"] == row["entry"].split("@", 1)[0]),
        "acceptance_mode": next(item["mode"] for item in target_deck if item["surface"] == row["entry"].split("@", 1)[0]),
    } for row in accepted_dictionary_rows]

    audit_by_surface_locus: dict[tuple[str, str], dict[str, object]] = {}
    for row in audit_rows:
        audit_by_surface_locus.setdefault((str(row["surface"]), str(row["locus"])), row)
    reality_rows: list[dict[str, object]] = []
    for surface in TARGET_BY_SURFACE:
        selected = list(REALITY_LOCI.get(surface, ()))
        if not selected:
            candidates = [row for (candidate_surface, _), row in audit_by_surface_locus.items() if candidate_surface == surface]
            candidates.sort(key=lambda row: (-int(row["reader_exact"]), -int(row["known_other_tokens"]), row["locus"]))
            selected = [str(row["locus"]) for row in candidates[:2 if len(candidates) >= 10 else 1]]
        for rank, locus in enumerate(selected, 1):
            row = audit_by_surface_locus.get((surface, locus))
            if row is None:
                raise RuntimeError(f"curated reality locus lacks target {surface}: {locus}")
            final = final_by_locus[locus]
            reality_rows.append({
                "surface": surface, "selection_rank": rank, "page": row["page"], "locus": locus,
                "reader_support": row["reader_support"], "zl3b_line": row["zl3b_line"],
                "tokenwise_v33_de": final["token_glosses_de"],
                "working_reading_de": CURATED_REALITY_READINGS.get(locus, CURATED_COMPLETE_READINGS.get(locus, "; ".join(split_pipe(final["token_glosses_de"])))),
                "syntax_note": "MANUAL_PARTIAL_SEQUENCE_READING" if locus in CURATED_REALITY_READINGS else "MANUAL_SEQUENCE_READING" if locus in CURATED_COMPLETE_READINGS else "TOKEN_ORDER_BASELINE",
            })

    curated_complete_rows: list[dict[str, object]] = []
    for locus, reading in CURATED_COMPLETE_READINGS.items():
        final = final_by_locus.get(locus)
        if final is None or locus not in final_complete_by_locus:
            raise RuntimeError(f"curated GDT656 line is not V33 complete: {locus}")
        present = list(dict.fromkeys(token["eva"] for token in by_line[locus] if token["eva"] in targets))
        curated_complete_rows.append({
            "page": final["page"], "locus": locus, "strict_complete": final_complete_by_locus[locus]["strict_complete"],
            "target_surfaces": "|".join(present), "zl3b_line": final["zl3b_line"],
            "tokenwise_v33_de": final["token_glosses_de"], "curated_workshop_reading_de": reading,
            "reader_note": CURATED_READER_NOTES[locus],
            "syntax_note": "QUALITIES_READ_AS_ORDERED_REGISTER_SEQUENCE__NOT_SIMULTANEOUS",
        })
    if any(GENERIC_FILLER.search(row["curated_workshop_reading_de"]) for row in curated_complete_rows):
        raise RuntimeError("generic filler in GDT656 curated readings")

    write_tsv(output_dir / "PAGE_ALLOWLIST.tsv", [{"page": page} for page in sorted(pages)], ("page",))
    write_tsv(output_dir / "TARGET_DECISION_DECK.tsv", target_deck, (
        "candidate_id", "candidate_order", "surface", "mode", "v32_meaning_de", "v33_meaning_de",
        "composition", "rival_de", "occurrences", "pages", "reader_exact_occurrences",
        "split_normalized_occurrences", "reader_variant_occurrences", "decision", "decision_basis",
        "strongest_counterargument",
    ))
    write_tsv(output_dir / "AL_QUALITY_LATTICE_ATLAS.tsv", lattice_rows, (
        "family", "surface", "decomposition", "quality_position", "v32_meaning_de", "v33_meaning_de",
        "zl3b_occurrences", "pages", "reader_exact_occurrences", "split_normalized_occurrences", "final_status",
    ))
    write_tsv(output_dir / "BOUNDARY_EVIDENCE_ATLAS.tsv", boundary_rows, (
        "bridge_id", "evidence_type", "page", "locus", "diagnostic_surface",
        "zl3b_line", "it2a_line", "rf1b_line", "supports",
    ))
    write_tsv(output_dir / "PAIR_CONTRAST_COUNTS.tsv", pair_rows, (
        "first_surface", "second_surface", "required_distinction_de", "cooccurrence_lines",
        "all_reader_exact_lines", "example_loci",
    ))
    write_tsv(output_dir / "HISTORICAL_SUBDEGREE_COMPARATORS.tsv", historical_rows, (
        "comparator_id", "date", "source", "observed_architecture", "source_url", "supports",
    ))
    write_tsv(output_dir / "LOCAL_EE_SISTER_EVIDENCE.tsv", local_ee_sister_rows, (
        "evidence_id", "surface", "carrier", "role", "occurrences", "pages",
        "reader_exact_occurrences", "split_normalized_occurrences", "loci",
        "working_interpretation_de", "decision",
    ))
    write_tsv(output_dir / "REVISION_LEDGER.tsv", revision_rows, (
        "surface", "mode", "v32_meaning_de", "v33_meaning_de", "occurrences", "reader_exact_occurrences", "reason",
    ))
    write_tsv(output_dir / "ALL_OCCURRENCE_SEMANTIC_AUDIT.tsv", audit_rows, (
        "audit_id", "round", "surface", "mode", "page", "locus", "section", "language", "hand",
        "token_ordinal", "line_position", "previous", "following", "zl3b_line", "it2a_line", "rf1b_line",
        "reader_support", "reader_exact", "split_normalized", "before_gloss_de", "after_gloss_de",
        "known_other_tokens", "v32_line_de", "v33_line_de", "hard_collision", "verdict",
    ))
    write_tsv(output_dir / "READER_VARIANT_AUDIT.tsv", variant_rows, (
        "surface", "page", "locus", "zl3b_line", "it2a_line", "rf1b_line", "reader_support",
        "working_meaning_de", "decision",
    ))
    write_tsv(output_dir / "ROUND_COVERAGE_COUNTS.tsv", round_rows, (
        "round", "surface", "mode", "dictionary_entries", "dictionary_sha256", "physical_lines",
        "known_token_positions", "unknown_token_positions", "complete_multi_token_lines", "strict_complete_lines",
        "one_unknown_lines", "strict_one_unknown_lines", "working_glossary_surfaces",
    ))
    write_tsv(output_dir / "ACCEPTED_WHOLE_SURFACE_DEFAULTS.tsv", accepted_defaults, (
        "surface", "entry", "kind", "working_meaning_de", "composition", "context_rule", "status",
        "occurrences", "acceptance_mode",
    ))
    write_tsv(output_dir / "SOURCE_PASSAGE_REALITY_CHECK.tsv", reality_rows, (
        "surface", "selection_rank", "page", "locus", "reader_support", "zl3b_line",
        "tokenwise_v33_de", "working_reading_de", "syntax_note",
    ))
    write_tsv(output_dir / "CURATED_COMPLETE_PASSAGE_READINGS.tsv", curated_complete_rows, (
        "page", "locus", "strict_complete", "target_surfaces", "zl3b_line",
        "tokenwise_v33_de", "curated_workshop_reading_de", "reader_note", "syntax_note",
    ))
    write_tsv(output_dir / "AFFECTED_LINE_TRANSLATIONS.tsv", affected_rows, (
        "page", "locus", "target_surfaces", "zl3b_line", "v32_tokenwise_de", "v33_tokenwise_de", "complete_v33",
    ))
    write_tsv(output_dir / "NEWLY_COMPLETED_LINES.tsv", new_complete_rows, (
        "page", "locus", "strict_complete", "enabled_by_surfaces", "zl3b_line", "literal_v33_de", "curated_workshop_reading_de",
    ))
    write_tsv(output_dir / "NEWLY_EXPOSED_ONE_HOLE_LINES.tsv", newly_exposed_rows, ("introduced_round", "enabled_by_surface", *ONE_FIELDS))
    write_tsv(output_dir / "V33_WORKING_TOKEN_GLOSSARY.tsv", final_gloss_rows, (
        "surface", "working_meaning_de", "source", "strength", "scope_state", "priority",
    ))
    write_tsv(output_dir / "ALL_LINE_CONCRETE_COVERAGE_V33.tsv", final_coverage, COVERAGE_FIELDS)
    write_tsv(output_dir / "COMPLETE_PASSAGES_V33.tsv", final_complete, ("rank", "strict_complete", *COVERAGE_FIELDS, "working_translation_de"))
    write_tsv(output_dir / "ONE_UNKNOWN_PASSAGES_V33.tsv", final_one, ONE_FIELDS)
    write_tsv(output_dir / "WORKING_DICTIONARY_V33.tsv", final_dictionary, (
        "entry", "kind", "working_meaning_de", "composition", "context_rule", "status",
    ))

    output_paths = [output_dir / name for name in OUTPUT_NAMES]
    input_paths = (
        G655_RUN, G655_ALLOW, G655_COVERAGE, G655_COMPLETE, G655_ONE, G655_GLOSSARY,
        G655_DICTIONARY, G655_RESULT, G655_REPORT, G647_REPORT, G652_REPORT, TOKENS_REL, CROSS_REL,
    )
    verdicts = Counter(row["verdict"] for row in audit_rows)
    observed_grid = [row for row in lattice_rows if int(row["zl3b_occurrences"]) > 0]
    result_core = {
        "schema": "GDT656_AL_QUALITY_POSITION_SHELL_RESULT_V1",
        "experiment_id": "GDT656", "status": STATUS,
        "guard": {"f1r": "EXCLUDED", "f84": "FORBIDDEN", "f84r": "FORBIDDEN", "new_pages": 0,
                  "new_images": 0, "allowed_pages": len(pages), "token_query": token_stats, "cross_query": cross_stats},
        "target_run": {
            "candidates": len(target_deck), "accepted_whole_cards": len(target_deck),
            "reader_anchored_exact_wholes": sum(int(row["reader_exact_occurrences"]) > 0 for row in target_deck),
            "accepted_surfaces": [row["surface"] for row in target_deck],
            "new_surfaces": [row["surface"] for row in target_deck if row["mode"].startswith("NEW")],
            "revised_surfaces": [row["surface"] for row in target_deck if row["mode"].startswith("REVISE")],
            "audited_occurrences": len(audit_rows),
            "all_reader_exact_occurrences": sum(int(row["reader_exact"]) for row in audit_rows),
            "split_normalized_occurrences": sum(int(row["split_normalized"]) for row in audit_rows),
            "reader_variant_warnings": sum(row["verdict"] == "READER_VARIANT_WARNING" for row in audit_rows),
            "hard_collisions": sum(int(row["hard_collision"]) for row in audit_rows),
            "verdicts": dict(sorted(verdicts.items())),
        },
        "full_al_quality_grid": {
            "cells": len(lattice_rows), "observed_cells": len(observed_grid),
            "occurrences": sum(int(row["zl3b_occurrences"]) for row in observed_grid),
            "all_reader_exact_occurrences": sum(int(row["reader_exact_occurrences"]) for row in observed_grid),
            "accepted_v33_cells": sum(row["final_status"] == "ACCEPTED_V33" for row in lattice_rows),
            "retained_v32_base_cells": ["al"],
            "observed_holds": sorted(OBSERVED_HOLDS),
        },
        "semantic_model": {
            "AL": "Rohstoffklasse I", "quality_heads": "CH/SH/K/T = trocken/feucht/heiss/kalt",
            "quality_positions": "zero E / E / EE = Gradanfang / Gradmitte / Gradende inside this AL grid",
            "O": "preparation context", "QO": "structural scope without a German free word",
            "historical_comparator": "Tadhg O Cuinn 1415 explicitly combines drug qualities with beginning/middle/end degree positions",
            "strongest_rival": "AL is raw-material form I and E is an attributive binder",
            "structural_tags_not_free_words": [
                "AL_CLASS_I", "CH_DRY_START", "SH_MOIST_START", "K_HOT_START", "T_COLD_START",
                "E_MIDDLE", "EE_END", "O_PREP", "QO_SCOPE",
            ],
            "local_exact_whole_analogy": "OEEAL = Rohstoffklasse I im Ansatz, am Gradende; supported by three exact OEEAR sisters; no free or global EE rule",
            "observed_holds": ["cheeeal", "eeal", "keeal"],
        },
        "coverage": {"base": base_metrics, "final": final_metrics,
                     "newly_completed_lines": len(new_complete_rows),
                     "newly_exposed_one_hole_lines": len(newly_exposed_rows),
                     "affected_lines": len(affected_rows)},
        "working_dictionary": {"v32_entries": len(base_dictionary), "v33_entries": len(final_dictionary),
                               "accepted_tail_entries": len(accepted_dictionary_rows),
                               "v32_prefix_sha256": canonical_hash(base_dictionary),
                               "v33_sha256": canonical_hash(final_dictionary),
                               "v32_glossary_surfaces": len(base_glossary), "v33_glossary_surfaces": len(glossary)},
        "claim_boundary": (
            "GDT656 is an exploratory exact-whole working translation of eighteen new and three revised observed AL position surfaces. "
            "The start/middle/end readings are family-bound defaults supported by the existing quality axis and a 1415 architecture comparator, not Voynich plaintext; OEEAL is one exact-whole local analogy, not a free EE rule. "
            "CHEEEAL, zero-exact KEEAL and EEAL, absent cells, multi-quality shells, free components, global E rules, phonetics, language, exact ingredient identity, f1r, new pages and new images remain outside."
        ),
        "inputs": {str(path): sha256(ROOT / path) for path in input_paths},
        "outputs": {str(BASE_REL / "artifacts" / path.name): sha256(path) for path in output_paths},
    }
    result = {**result_core, "content_sha256": canonical_hash(result_core)}
    (output_dir / "RESULT.json").write_text(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return result


def main() -> int:
    result = build(ART)
    target_run, coverage = result["target_run"], result["coverage"]
    print(
        f"GDT656 built: accepted={target_run['accepted_whole_cards']} audits={target_run['audited_occurrences']} "
        f"known={coverage['final']['known_token_positions']} complete={coverage['final']['complete_multi_token_lines']} "
        f"strict={coverage['final']['strict_complete_lines']} one_unknown={coverage['final']['one_unknown_lines']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
