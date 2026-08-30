#!/usr/bin/env python3
"""Build GDT655: complete the observed AL/DAL measured-material system."""
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
BASE_REL = Path("experiments/yolo/gdt655_dal_al_measured_material_completion")
ART = ROOT / BASE_REL / "artifacts"
G654 = Path("experiments/yolo/gdt654_ar_or_surface_consolidation")
G654_RUN = G654 / "src/run.py"
G654_ALLOW = G654 / "artifacts/PAGE_ALLOWLIST.tsv"
G654_COVERAGE = G654 / "artifacts/ALL_LINE_CONCRETE_COVERAGE_V31.tsv"
G654_COMPLETE = G654 / "artifacts/COMPLETE_PASSAGES_V31.tsv"
G654_ONE = G654 / "artifacts/ONE_UNKNOWN_PASSAGES_V31.tsv"
G654_GLOSSARY = G654 / "artifacts/V31_EXACT_TOKEN_GLOSSARY.tsv"
G654_DICTIONARY = G654 / "artifacts/WORKING_DICTIONARY_V31.tsv"
G654_RESULT = G654 / "artifacts/RESULT.json"
G654_REPORT = G654 / "REPORT.md"
G636_REPORT = Path("experiments/yolo/gdt636_residual_four_head_semantics/REPORT.md")
G649_REPORT = Path("experiments/yolo/gdt649_strict_v25_hole_completion/REPORT.md")
G653_REPORT = Path("experiments/yolo/gdt653_strict_v29_boundary_compounds/REPORT.md")

spec = importlib.util.spec_from_file_location("gdt654_builder_for_gdt655", ROOT / G654_RUN)
if spec is None or spec.loader is None:
    raise RuntimeError("cannot load GDT654 builder")
g654 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(g654)
TOKENS_REL = g654.TOKENS_REL
CROSS_REL = g654.CROSS_REL
COVERAGE_FIELDS = g654.COVERAGE_FIELDS
ONE_FIELDS = g654.ONE_FIELDS

STATUS = "PASS_18_ANCHORED_PLUS_1_PREDICTED_DAL_AL_SURFACES__V32"
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
        "surface": surface, "mode": mode, "working_meaning_de": meaning,
        "composition": composition, "rival_de": rival,
        "decision_basis": basis, "counterargument": counterargument,
    }


TARGET_SPECS = (
    target(
        "al", "NEW_EXACT_WHOLE", "Rohstoffklasse I", "AL_CLASS_I",
        "Rohstoffform I",
        "204 occurrences, 167 all-reader exact; AL coexists with DAL and with P/S/R/L material-head sisters",
        "AL is never line-initial and may be a bound classifier rather than an independent noun",
    ),
    target(
        "dal", "NEW_EXACT_WHOLE", "abgemessene Rohstoffmenge I", "D_MEASURE+AL_CLASS_I",
        "Rohdrogenposten",
        "191 occurrences, 147 exact; D+AR is already measured fraction and the exact DAIN/DAIL/DAIR row aligns value, material amount and fraction",
        "no reader directly splits D from AL, so DAL may still be a learned whole meaning raw-drug lot",
    ),
    target(
        "chdal", "NEW_EXACT_WHOLE", "trockene abgemessene Rohstoffmenge I am Gradanfang", "CH_DRY_START+DAL_MEASURED_MATERIAL_I",
        "trockener Rohdrogenposten",
        "19 occurrences, 13 exact, with DAL and CHDAL coexisting on two lines; CH/SH quality wholes use the same zero-E start versus E-middle contrast",
        "CHDAL lacks a direct CH|DAL split and CH may mark dry quality without fixing a subdegree",
    ),
    target(
        "shedal", "NEW_EXACT_WHOLE", "feuchte abgemessene Rohstoffmenge I in der Gradmitte", "SHE_MOIST_MIDDLE+DAL_MEASURED_MATERIAL_I",
        "feuchter Rohdrogenposten",
        "11 occurrences, seven exact, in the populated CH/CHED/SH/SHED plus DAL sister field and the recurrent zero-E/E quality-position contrast",
        "the fluent lot reading is strong and E may remain an attributive binder rather than a middle-position marker",
    ),
    target(
        "ail", "NEW_EXACT_WHOLE", "Rohstoffklasse II", "AL_CLASS_II",
        "Rohstoffform II",
        "five occurrences, three exact, extend the observed AL/AIL/AIIL minim ladder",
        "low support leaves form or charge class II equally possible",
    ),
    target(
        "aiil", "NEW_EXACT_WHOLE", "Rohstoffklasse III", "AL_CLASS_III",
        "Rohstoffform III",
        "one all-reader exact occurrence occupies the third observed AL minim level",
        "the singleton cannot independently distinguish class from form or amount",
    ),
    target(
        "dail", "NEW_EXACT_WHOLE", "abgemessene Rohstoffmenge II", "D_MEASURE+AL_CLASS_II",
        "Rohdrogenposten II",
        "two all-reader exact occurrences; f45v.4 places DAIN, DAIL and DAIR together in all readers",
        "there is no direct D|AIL split and the two tokens can be a learned whole",
    ),
    target(
        "daiil", "READER_UNSTABLE_COMPOSITIONAL_WHOLE", "abgemessene Rohstoffmenge III", "D_MEASURE+AL_CLASS_III",
        "Rohdrogenposten III",
        "one ZL3b/IT2a DAIIL occurrence is predicted by DAL/DAIL and paired with RF1b AIIL; the same D omission recurs coordinately in DAR/DAL",
        "zero all-reader exact and normalized anchors make this a visibly reader-unstable compositional card",
    ),
    target(
        "aly", "NEW_EXACT_WHOLE", "Rohstoffklasse I, Grundform", "AL_CLASS_I+Y_BASE",
        "Rohstoffform I, Grundform",
        "18 occurrences, 12 exact, extend AL with the recurrent family-bound Y ground-form tail",
        "class plus ground form may be redundant and the form reading remains viable",
    ),
    target(
        "aldy", "NEW_EXACT_WHOLE", "Rohstoffklasse I, abgeschlossen", "AL_CLASS_I+DY_COMPLETE",
        "Rohstoffform I, abgeschlossen",
        "ten occurrences, five exact, occupy the completed AL tail cell and close the DAIIL source line",
        "reader support is only half exact and DY may encode a form rather than completion",
    ),
    target(
        "daly", "NEW_EXACT_WHOLE", "abgemessene Rohstoffmenge I, Grundform", "DAL_MEASURED_MATERIAL_I+Y_BASE",
        "Rohdrogenposten, Grundform",
        "24 occurrences, 18 exact, extend DAL with the recurrent family-bound Y ground-form tail",
        "the only reader fork is DA|LY rather than a direct DAL|Y split",
    ),
    target(
        "daldy", "NEW_EXACT_WHOLE", "abgemessene Rohstoffmenge I, abgeschlossen", "DAL_MEASURED_MATERIAL_I+DY_COMPLETE",
        "abgeschlossener Rohdrogenposten",
        "19 occurrences and three direct DAL DY reader splits; six exact and eight split-normalized",
        "reader instability is high and DY may describe a form rather than completion",
    ),
    target(
        "chedal", "NEW_EXACT_WHOLE", "trockene abgemessene Rohstoffmenge I in der Gradmitte", "CHE_DRY_MIDDLE+DAL_MEASURED_MATERIAL_I",
        "trocken gebundener Rohdrogenposten",
        "22 occurrences, 15 exact, occupy the E-marked CHE sister cell beside CHDAL",
        "f58v.12 also permits CHE+AL+Y, and E may remain an attributive binder rather than a middle-position marker",
    ),
    target(
        "shdal", "NEW_EXACT_WHOLE", "feuchte abgemessene Rohstoffmenge I am Gradanfang", "SH_MOIST_START+DAL_MEASURED_MATERIAL_I",
        "feuchter Rohdrogenposten",
        "four occurrences, three exact, occupy the zero-E SH sister cell beside SHEDAL",
        "low support cannot distinguish the proposed start position from a learned whole",
    ),
    target(
        "odal", "NEW_EXACT_WHOLE", "abgemessene Rohstoffmenge I im Ansatz", "O_PREP+DAL_MEASURED_MATERIAL_I",
        "angesetzter Rohdrogenposten",
        "14 occurrences, 11 exact, extend DAL under the established O preparation frame",
        "O may create an indivisible preparation head rather than a transparent scope",
    ),
    target(
        "qodal", "NEW_EXACT_WHOLE", "abgemessene Rohstoffmenge I im Ansatz", "QO_SCOPE+DAL_MEASURED_MATERIAL_I",
        "Rohdrogenposten im QO-Rahmen",
        "seven occurrences, six exact, occupy the QO sister cell of ODAL",
        "QO may contribute an unsuppressed lexical value or change the head class",
    ),
    target(
        "oral", "REVISE_AL_OR_COMPOSITION", "Rohstoffportion, Klasse I", "OR_PORTION+AL_CLASS_I",
        "Ansatz aus Wurzelrohstoff, Form I",
        "ten occurrences, six exact and seven normalized; f79r.19 directly splits ZL3b ORAL into OR AL in both other readers, while OR and AL now have distinct whole-family values",
        "the old O+RAL preparation parse remains possible at nine unsplit loci",
    ),
    target(
        "chdaly", "REVISE_DAL_MODEL", "trockene abgemessene Rohstoffmenge I am Gradanfang, Grundform", "CH_DRY_START+DAL_MEASURED_MATERIAL_I+Y_BASE",
        "trockener Rohdrogenposten, Grundform",
        "three all-reader exact occurrences; the new DAL reading removes the isolated learned-post assumption",
        "CH+D+AL+Y and a learned DAL noun remain viable parses",
    ),
    target(
        "sodal", "REVISE_DAL_MODEL", "abgemessene Saat-Rohstoffmenge I im Ansatz", "S_SEED+O_PREP+DAL_MEASURED_MATERIAL_I",
        "Ansatz aus einem Saatdrogenposten",
        "two occurrences, one exact, with a direct S ODAL split and the revised ODAL material-amount card",
        "the two reader forks are weak and the old seed-lot reading remains fluent",
    ),
)

TARGET_BY_SURFACE = {row["surface"]: row for row in TARGET_SPECS}
EXPECTED_COUNTS = {
    "al": (204, 63, 167, 167), "dal": (191, 87, 147, 147),
    "chdal": (19, 15, 13, 13), "shedal": (11, 7, 7, 7),
    "ail": (5, 4, 3, 3), "aiil": (1, 1, 1, 1), "dail": (2, 2, 2, 2),
    "daiil": (1, 1, 0, 0), "aly": (18, 16, 12, 12), "aldy": (10, 10, 5, 5),
    "daly": (24, 19, 18, 18), "daldy": (19, 17, 6, 8),
    "chedal": (22, 15, 15, 15), "shdal": (4, 4, 3, 3),
    "odal": (14, 14, 11, 11), "qodal": (7, 6, 6, 6),
    "oral": (10, 10, 6, 7), "chdaly": (3, 3, 3, 3), "sodal": (2, 2, 1, 1),
}

LATTICE_FORMS = (
    ("AL_MINIM_LADDER", "al", "A+L", "I", "TARGET"),
    ("AL_MINIM_LADDER", "ail", "A+I+L", "II", "TARGET"),
    ("AL_MINIM_LADDER", "aiil", "A+II+L", "III", "TARGET"),
    ("AL_MINIM_LADDER", "aiiil", "A+III+L", "IV", "ZERO_EXACT_HOLD"),
    ("AL_TAILS", "aly", "AL+Y", "BASE", "TARGET"),
    ("AL_TAILS", "aldy", "AL+DY", "COMPLETE", "TARGET"),
    ("D_AL_MINIM_LADDER", "dal", "D+A+L", "I", "TARGET"),
    ("D_AL_MINIM_LADDER", "dail", "D+A+I+L", "II", "TARGET"),
    ("D_AL_MINIM_LADDER", "daiil", "D+A+II+L", "III", "TARGET_READER_UNSTABLE"),
    ("D_AL_TAILS", "daly", "DAL+Y", "BASE", "TARGET"),
    ("D_AL_TAILS", "daldy", "DAL+DY", "COMPLETE", "TARGET"),
    ("DRY_MOIST_DAL_SHELLS", "chdal", "CH+DAL", "DRY", "TARGET"),
    ("DRY_MOIST_DAL_SHELLS", "chedal", "CHE+DAL", "DRY_BOUND", "TARGET"),
    ("DRY_MOIST_DAL_SHELLS", "shdal", "SH+DAL", "MOIST", "TARGET"),
    ("DRY_MOIST_DAL_SHELLS", "shedal", "SHE+DAL", "MOIST_BOUND", "TARGET"),
    ("PREPARATION_DAL_SHELLS", "odal", "O+DAL", "O_PREP", "TARGET"),
    ("PREPARATION_DAL_SHELLS", "qodal", "QO+DAL", "QO_SCOPE", "TARGET"),
    ("PORTION_AL_COMPOUND", "oral", "OR+AL", "PORTION_CLASS_I", "TARGET_REVISION"),
    ("HEAD_DAL_COMPOUNDS", "chdaly", "CH+DAL+Y", "DRY_BASE", "TARGET_REVISION"),
    ("HEAD_DAL_COMPOUNDS", "chdaldy", "CH+DAL+DY", "DRY_COMPLETE", "ZERO_EXACT_HOLD"),
    ("HEAD_DAL_COMPOUNDS", "sodal", "S+O+DAL", "SEED_PREP", "TARGET_REVISION"),
    ("MATERIAL_AL_ANCHORS", "pal", "P+AL", "POWDER", "V31_ANCHOR"),
    ("MATERIAL_AL_ANCHORS", "sal", "S+AL", "SEED", "V31_ANCHOR"),
    ("MATERIAL_AL_ANCHORS", "ral", "R+AL", "ROOT", "V31_ANCHOR"),
    ("MATERIAL_AL_ANCHORS", "lal", "L+AL", "WOOD", "V31_ANCHOR"),
    ("MEASURED_AR_ANCHORS", "dar", "D+AR", "I", "V31_ANCHOR"),
    ("MEASURED_AR_ANCHORS", "dair", "D+AIR", "II", "V31_ANCHOR"),
    ("MEASURED_AR_ANCHORS", "daiir", "D+AIIR", "III", "V31_ANCHOR"),
)

BOUNDARY_SPECS = (
    ("G655-B01", "AL_MATERIAL_SPLIT", "f54v.1", "sal / s al", "reader split exposes S plus AL"),
    ("G655-B02", "AL_MATERIAL_SPLIT", "f76r.33", "ral / r al", "reader split exposes R plus AL"),
    ("G655-B03", "AL_MATERIAL_SPLIT", "f116r.50", "chal / ch al", "reader split exposes CH plus AL"),
    ("G655-B04", "AL_PORTION_SPLIT", "f79r.19", "oral / or al", "reader split exposes OR plus AL"),
    ("G655-B05", "DAL_DY_SPLIT", "f75v.22", "daldy / dal dy", "first reader split exposes DAL plus DY"),
    ("G655-B06", "DAL_DY_SPLIT", "f89v1.13", "daldy / dal dy", "second reader split exposes DAL plus DY"),
    ("G655-B07", "DAL_DY_Y_SPLIT", "f103r.1", "daldy / dal dy / dal y", "three-reader granularity exposes DAL before a tail"),
    ("G655-B08", "CHEDAL_PARSE_WARNING", "f58v.12", "chedal dy / che al y", "warning: CHE plus AL remains a competing parse"),
    ("G655-B09", "S_ODAL_SPLIT", "f93r.11", "sodal / s odal", "reader split exposes S plus ODAL"),
)

PARALLEL_LOCI = (
    ("G655-P01", "f45v.4", "DAIN_DAIL_DAIR_LEVEL_II", "value or grade II / measured raw-material amount II / measured fraction II"),
    ("G655-P02", "f78r.27", "DAIIL_TO_AIIL_READER_FORK", "measured raw-material amount III / raw-material class III after D omission"),
    ("G655-P03", "f55r.9", "COORDINATED_D_OMISSION", "DAR/DAL/DAR in ZL3b and IT2a versus AR/AL/AR in RF1b"),
    ("G655-P04", "f83r.48", "DAL_AND_CHDAL", "measured raw-material amount I / dry measured raw-material amount I"),
    ("G655-P05", "f80v.28", "OR_AND_AL", "drug portion / raw-material class I"),
    ("G655-P06", "f83v.16", "SAR_AND_AL", "seed fraction I / raw-material class I"),
)

REALITY_LOCI = {
    "al": ("f2r.5", "f80v.28", "f83v.16"),
    "dal": ("f2r.11", "f75r.40", "f83r.14"),
    "chdal": ("f83r.48",), "shedal": ("f83r.47",),
    "dail": ("f45v.4",), "daldy": ("f45r.10", "f75v.22"),
    "oral": ("f79r.19", "f36r.2"),
}

CURATED_COMPLETE_READINGS = {
    "f75r.40": "Abgemessene Fraktion I; in der Gradmitte feucht abgeschlossen; heiß, Grad II; erneut in der Gradmitte feucht abgeschlossen; abgemessene Rohstoffmenge I; am Gradende heiß abgeschlossen; eingeweichte Wurzel.",
    "f77v.13": "Samenportion; feuchtes Drogenmaterial; am Gradanfang trocken abgeschlossen; am Gradende heiß abgeschlossen; abgemessene Fraktion I; in der Gradmitte feucht abgeschlossen; in der Gradmitte trocken abgeschlossen; heiße Substanz; erneut in der Gradmitte trocken abgeschlossen; heiß in der Gradmitte; eingeweichtes Drogenholz; abgemessene Rohstoffmenge I.",
    "f77v.30": "In der Gradmitte feucht; Drogenstoff/Ansatz; feucht am Gradende; in der Gradmitte heiß abgeschlossen; getrocknetes Drogenholz; heiß, Grad III; abgemessene Rohstoffmenge I; Menge III; in der Gradmitte trocken abgeschlossen.",
    "f78r.27": "Menge III; trockenes Arzneikompositum, Rohstoffform I; abgemessene Rohstoffmenge III; Rohstoffklasse I, abgeschlossen.",
    "f83r.14": "In der Gradmitte heiß-trocken abgeschlossen; am Gradende heiß abgeschlossen; in der Gradmitte feucht abgeschlossen; in der Gradmitte heiß-feucht abgeschlossen; abgemessene Rohstoffmenge I; getrocknetes Drogenholz; heiß, Grad III; feuchtes Blatt-/Krautgut; erneut abgemessene Rohstoffmenge I; Saatgut, Grundform.",
    "f83r.47": "Kalt-trockener Ansatz am Gradanfang abgeschlossen; heiß-trockener Ansatz am Gradanfang abgeschlossen; feuchte abgemessene Rohstoffmenge I in der Gradmitte.",
    "f83r.48": "Abgemessene Rohstoffmenge I; trockener Drogenstoff; Holzstoff; trockene abgemessene Rohstoffmenge I am Gradanfang; Menge III.",
}

OUTPUT_NAMES = (
    "PAGE_ALLOWLIST.tsv", "TARGET_DECISION_DECK.tsv", "DAL_AL_LATTICE_ATLAS.tsv",
    "BOUNDARY_EVIDENCE_ATLAS.tsv", "PARALLEL_MEASURE_EVIDENCE.tsv", "PAIR_CONTRAST_COUNTS.tsv",
    "REVISION_LEDGER.tsv", "ALL_OCCURRENCE_SEMANTIC_AUDIT.tsv", "READER_VARIANT_AUDIT.tsv",
    "ROUND_COVERAGE_COUNTS.tsv", "ACCEPTED_WHOLE_SURFACE_DEFAULTS.tsv",
    "SOURCE_PASSAGE_REALITY_CHECK.tsv", "CURATED_COMPLETE_PASSAGE_READINGS.tsv",
    "AFFECTED_LINE_TRANSLATIONS.tsv", "NEWLY_COMPLETED_LINES.tsv",
    "NEWLY_EXPOSED_ONE_HOLE_LINES.tsv", "V32_WORKING_TOKEN_GLOSSARY.tsv",
    "ALL_LINE_CONCRETE_COVERAGE_V32.tsv", "COMPLETE_PASSAGES_V32.tsv",
    "ONE_UNKNOWN_PASSAGES_V32.tsv", "WORKING_DICTIONARY_V32.tsv",
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
    predicted = spec_row["mode"] == "READER_UNSTABLE_COMPOSITIONAL_WHOLE"
    return {
        "entry": f"{spec_row['surface']}@GDT655_{'PREDICTED_WHOLE' if predicted else 'EXACT_WHOLE'}",
        "kind": (
            "PREDICTED_ZL3B_WHOLE_READER_UNSTABLE"
            if predicted else f"EXACT_ZL3B_WHOLE_{spec_row['mode']}"
        ),
        "working_meaning_de": spec_row["working_meaning_de"],
        "composition": spec_row["composition"],
        "context_rule": (
            f"{'predicted' if predicted else 'exact'} complete ZL3B surface only; "
            f"mode={spec_row['mode']}; {occurrences} audited occurrences; "
            f"{exact_count} all-reader exact; supersedes current glossary card without deleting material history"
        ),
        "status": f"NEW_V32_ACCEPTED_ROUND_{round_number:02d}",
    }


def line_position(line: list[dict[str, object]], token_index: int) -> int:
    for ordinal, token in enumerate(line, 1):
        if int(token["token_index"]) == token_index:
            return ordinal
    raise RuntimeError("token position not found")


def build(output_dir: Path) -> dict[str, object]:
    output_dir.mkdir(parents=True, exist_ok=True)
    pages = {row["page"] for row in read_tsv(ROOT / G654_ALLOW)}
    if "f1r" in pages or any(page.startswith("f84") for page in pages):
        raise RuntimeError("allow-list contains excluded or forbidden page")
    guarded_query = g654.g653.g637.g636.g635.g634.g633.g632.g631.guarded_query
    token_rows, token_stats = guarded_query(
        TOKENS_REL, pages, "page,locus,token_index,eva,section,language,hand",
    )
    cross_rows, cross_stats = guarded_query(
        CROSS_REL, pages, "page,locus,all_three_present,all_present_exact,zl3b_clean,it2a_clean,rf1b_clean",
    )
    cross_by_locus = {row["locus"]: row for row in cross_rows}
    by_line, _ = g654.g653.g637.g636.g635.g634.g633.g632.g631.line_maps([dict(row) for row in token_rows])
    exact, boundary = g654.g653.g637.g636.g635.g634.stable_maps(token_rows, cross_by_locus)

    base_dictionary = [dict(row) for row in read_tsv(ROOT / G654_DICTIONARY)]
    base_gloss_rows = read_tsv(ROOT / G654_GLOSSARY)
    base_glossary = {row["surface"]: dict(row) for row in base_gloss_rows}
    base_coverage = read_tsv(ROOT / G654_COVERAGE)
    base_complete = read_tsv(ROOT / G654_COMPLETE)
    base_one = read_tsv(ROOT / G654_ONE)
    if (len(base_dictionary), len(base_glossary), len(base_coverage), len(base_complete), len(base_one)) != (510, 437, 4128, 123, 197):
        raise RuntimeError("GDT654 V31 base counts changed")
    replay_coverage, replay_one, _, replay_complete = g654.g653.g637.build_line_coverage(
        by_line, base_glossary, exact, boundary, cross_by_locus,
    )
    if (string_rows(replay_coverage) != string_rows(base_coverage)
            or string_rows(replay_complete) != string_rows(base_complete)
            or string_rows(replay_one) != string_rows(base_one)):
        raise RuntimeError("GDT654 V31 editions do not replay")
    base_metrics = metrics(replay_coverage, replay_one, replay_complete, base_glossary)
    expected_base = {
        "physical_lines": 4128, "known_token_positions": 15846,
        "unknown_token_positions": 16493, "complete_multi_token_lines": 123,
        "strict_complete_lines": 75, "one_unknown_lines": 197,
        "strict_one_unknown_lines": 44, "working_glossary_surfaces": 437,
    }
    if base_metrics != expected_base:
        raise RuntimeError(f"GDT654 V31 metrics changed: {base_metrics!r}")

    if any(GENERIC_FILLER.search(row["working_meaning_de"]) for row in TARGET_SPECS):
        raise RuntimeError("generic filler in GDT655 target deck")
    new_surfaces = tuple(row["surface"] for row in TARGET_SPECS if not row["mode"].startswith("REVISE"))
    if any(surface in base_glossary for surface in new_surfaces):
        raise RuntimeError("new GDT655 target unexpectedly exists in V31 glossary")
    if base_glossary.get("chdaly", {}).get("working_meaning_de") != "trockener Rohdrogenposten, Grundform":
        raise RuntimeError("V31 CHDALY rival changed")
    if base_glossary.get("sodal", {}).get("working_meaning_de") != "Ansatz aus einem Saatdrogenposten":
        raise RuntimeError("V31 SODAL rival changed")

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

    lattice_rows: list[dict[str, object]] = []
    for family, surface, decomposition, level, role in LATTICE_FORMS:
        members = [row for row in token_rows if row["eva"] == surface]
        base_row = base_glossary.get(surface)
        target_row = TARGET_BY_SURFACE.get(surface)
        lattice_rows.append({
            "family": family, "surface": surface, "decomposition": decomposition,
            "level_or_role": level, "planned_role": role,
            "v31_meaning_de": base_row["working_meaning_de"] if base_row else "OPEN",
            "v32_meaning_de": target_row["working_meaning_de"] if target_row else base_row["working_meaning_de"] if base_row else "NOT_ASSIGNED",
            "zl3b_occurrences": len(members), "pages": len({row["page"] for row in members}),
            "reader_exact_occurrences": sum(exact[row["locus"], int(row["token_index"])] for row in members),
            "split_normalized_occurrences": sum(boundary[row["locus"], int(row["token_index"])] for row in members),
            "final_status": (
                "ACCEPTED_V32" if target_row else "V31_ANCHOR" if base_row else
                "OBSERVED_ZERO_EXACT_HOLD" if members else "ABSENT_HOLD"
            ),
        })

    cross_by = cross_by_locus
    boundary_rows: list[dict[str, object]] = []
    for bridge_id, evidence_type, locus, diagnostic, support in BOUNDARY_SPECS:
        row = cross_by.get(locus)
        if row is None:
            raise RuntimeError(f"missing GDT655 boundary locus: {locus}")
        boundary_rows.append({
            "bridge_id": bridge_id, "evidence_type": evidence_type,
            "page": row["page"], "locus": locus, "diagnostic_surface": diagnostic,
            "zl3b_line": row["zl3b_clean"], "it2a_line": row["it2a_clean"],
            "rf1b_line": row["rf1b_clean"], "supports": support,
        })

    parallel_rows: list[dict[str, object]] = []
    for evidence_id, locus, relation, reading in PARALLEL_LOCI:
        row = cross_by.get(locus)
        if row is None:
            raise RuntimeError(f"missing GDT655 parallel locus: {locus}")
        parallel_rows.append({
            "evidence_id": evidence_id, "page": row["page"], "locus": locus,
            "relation": relation, "working_reading_de": reading,
            "zl3b_line": row["zl3b_clean"], "it2a_line": row["it2a_clean"],
            "rf1b_line": row["rf1b_clean"],
            "all_three_exact_line": int(row["all_three_present"]) == 1 and int(row["all_present_exact"]) == 1,
        })

    line_surfaces = {locus: {str(token["eva"]) for token in line} for locus, line in by_line.items()}
    pair_specs = (
        ("al", "dal", "Rohstoffklasse I / abgemessene Rohstoffmenge I"),
        ("dal", "dail", "abgemessene Rohstoffmenge I / II"),
        ("dal", "daldy", "Rohstoffmenge / abgeschlossene Rohstoffmenge"),
        ("dal", "chdal", "Rohstoffmenge / trockene Rohstoffmenge"),
        ("al", "oral", "Rohstoffklasse I / Rohstoffportion"),
        ("dal", "daiin", "abgemessene Rohstoffmenge I / Mengen- oder Gradwert III"),
    )
    pair_rows: list[dict[str, object]] = []
    for first, second, distinction in pair_specs:
        loci = sorted(locus for locus, surfaces in line_surfaces.items() if first in surfaces and second in surfaces)
        pair_rows.append({
            "first_surface": first, "second_surface": second,
            "required_distinction_de": distinction, "cooccurrence_lines": len(loci),
            "all_reader_exact_lines": sum(
                int(cross_by[locus]["all_three_present"]) == 1 and int(cross_by[locus]["all_present_exact"]) == 1
                for locus in loci
            ),
            "example_loci": "|".join(loci[:12]) or "NONE",
        })

    glossary = {key: dict(value) for key, value in base_glossary.items()}
    coverage, one_unknown, _, complete = g654.g653.g637.build_line_coverage(
        by_line, glossary, exact, boundary, cross_by_locus,
    )
    base_complete_loci = {row["locus"] for row in base_complete}
    seen_one_loci = {row["locus"] for row in base_one}
    accepted_dictionary_rows: list[dict[str, object]] = []
    target_deck: list[dict[str, object]] = []
    audit_rows: list[dict[str, object]] = []
    variant_rows: list[dict[str, object]] = []
    revision_rows: list[dict[str, object]] = []
    round_rows: list[dict[str, object]] = [{
        "round": 0, "surface": "BASE_V31", "mode": "BASE",
        "dictionary_entries": len(base_dictionary),
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
        reader_unstable_prediction = spec_row["mode"] == "READER_UNSTABLE_COMPOSITIONAL_WHOLE"
        if len(members) != token_counts[surface] or (exact_count == 0 and not reader_unstable_prediction):
            raise RuntimeError(f"target occurrence or anchor drift: {surface}")
        pre_coverage, pre_complete = coverage, complete
        pre_by_locus = {row["locus"]: row for row in pre_coverage}
        old_gloss = base_glossary.get(surface, {}).get("working_meaning_de", "OPEN")
        g654.g653.g637.set_gloss(
            glossary, surface, spec_row["working_meaning_de"], f"GDT655:{spec_row['mode']}",
            "READER_UNSTABLE_COMPOSITIONAL_WHOLE" if reader_unstable_prediction else "EXACT_WHOLE_DAL_AL_CONSOLIDATION",
            "KNOWN_ZL3B_PREDICTED_WHOLE_READER_UNSTABLE" if reader_unstable_prediction else "KNOWN_EXACT_WHOLE",
            151 if reader_unstable_prediction else 152,
        )
        coverage, one_unknown, _, complete = g654.g653.g637.build_line_coverage(
            by_line, glossary, exact, boundary, cross_by_locus,
        )
        post_by_locus = {row["locus"]: row for row in coverage}
        accepted_dictionary_rows.append(dictionary_row(spec_row, round_number, len(members), exact_count))
        if spec_row["mode"].startswith("REVISE"):
            revision_rows.append({
                "surface": surface, "mode": spec_row["mode"], "v31_meaning_de": old_gloss,
                "v32_meaning_de": spec_row["working_meaning_de"], "occurrences": len(members),
                "reader_exact_occurrences": exact_count, "reason": spec_row["decision_basis"],
            })

        verdicts: Counter[str] = Counter()
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
            verdicts[verdict] += 1
            audit_rows.append({
                "audit_id": f"G655-A{round_number:02d}-{occurrence:04d}", "round": round_number,
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
                "known_other_tokens": known_other, "v31_line_de": before["token_glosses_de"],
                "v32_line_de": after["token_glosses_de"], "hard_collision": 0, "verdict": verdict,
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
            "candidate_id": f"G655-C{round_number:02d}", "candidate_order": round_number,
            "surface": surface, "mode": spec_row["mode"], "v31_meaning_de": old_gloss,
            "v32_meaning_de": spec_row["working_meaning_de"], "composition": spec_row["composition"],
            "rival_de": spec_row["rival_de"], "occurrences": len(members),
            "pages": len({row["page"] for row in members}), "reader_exact_occurrences": exact_count,
            "split_normalized_occurrences": normalized_count, "reader_variant_occurrences": len(members) - normalized_count,
            "decision": "ACCEPT_V32_READER_UNSTABLE_PREDICTED_WHOLE" if reader_unstable_prediction else "ACCEPT_V32_EXACT_WHOLE",
            "decision_basis": spec_row["decision_basis"],
            "strongest_counterargument": spec_row["counterargument"],
        })
        round_rows.append({
            "round": round_number, "surface": surface, "mode": spec_row["mode"],
            "dictionary_entries": len(post_dictionary), "dictionary_sha256": canonical_hash(post_dictionary),
            **metrics(coverage, one_unknown, complete, glossary),
        })

    final_dictionary = [*base_dictionary, *accepted_dictionary_rows]
    final_coverage, final_one, _, final_complete = g654.g653.g637.build_line_coverage(
        by_line, glossary, exact, boundary, cross_by_locus,
    )
    final_by_locus = {row["locus"]: row for row in final_coverage}
    base_by_locus = {row["locus"]: row for row in base_coverage}
    final_complete_by_locus = {row["locus"]: row for row in final_complete}
    final_metrics = metrics(final_coverage, final_one, final_complete, glossary)
    expected_final = {
        "physical_lines": 4128, "known_token_positions": 16398,
        "unknown_token_positions": 15941, "complete_multi_token_lines": 130,
        "strict_complete_lines": 77, "one_unknown_lines": 225,
        "strict_one_unknown_lines": 54, "working_glossary_surfaces": 453,
    }
    if final_metrics != expected_final:
        raise RuntimeError(f"unexpected V32 metrics: {final_metrics!r}")
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
            "zl3b_line": row["zl3b_line"], "v31_tokenwise_de": base_by_locus[locus]["token_glosses_de"],
            "v32_tokenwise_de": row["token_glosses_de"], "complete_v32": int(row["unknown_tokens"]) == 0,
        })

    new_complete_rows: list[dict[str, object]] = []
    for locus in sorted(set(final_complete_by_locus) - base_complete_loci):
        row = final_by_locus[locus]
        present = list(dict.fromkeys(token["eva"] for token in by_line[locus] if token["eva"] in targets))
        new_complete_rows.append({
            "page": row["page"], "locus": locus, "strict_complete": final_complete_by_locus[locus]["strict_complete"],
            "enabled_by_surfaces": "|".join(present), "zl3b_line": row["zl3b_line"],
            "literal_v32_de": "; ".join(split_pipe(row["token_glosses_de"])),
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
                "tokenwise_v32_de": final["token_glosses_de"],
                "working_reading_de": CURATED_COMPLETE_READINGS.get(locus, "; ".join(split_pipe(final["token_glosses_de"]))),
                "syntax_note": "MANUAL_SEQUENCE_READING" if locus in CURATED_COMPLETE_READINGS else "TOKEN_ORDER_BASELINE",
            })

    curated_complete_rows: list[dict[str, object]] = []
    for locus, reading in CURATED_COMPLETE_READINGS.items():
        final = final_by_locus.get(locus)
        if final is None or locus not in final_complete_by_locus:
            raise RuntimeError(f"curated GDT655 line is not V32 complete: {locus}")
        present = list(dict.fromkeys(token["eva"] for token in by_line[locus] if token["eva"] in targets))
        curated_complete_rows.append({
            "page": final["page"], "locus": locus,
            "strict_complete": final_complete_by_locus[locus]["strict_complete"],
            "target_surfaces": "|".join(present), "zl3b_line": final["zl3b_line"],
            "tokenwise_v32_de": final["token_glosses_de"], "curated_workshop_reading_de": reading,
            "syntax_note": "QUALITIES_READ_AS_ORDERED_REGISTER_SEQUENCE__NOT_SIMULTANEOUS",
        })

    write_tsv(output_dir / "PAGE_ALLOWLIST.tsv", [{"page": page} for page in sorted(pages)], ("page",))
    write_tsv(output_dir / "TARGET_DECISION_DECK.tsv", target_deck, (
        "candidate_id", "candidate_order", "surface", "mode", "v31_meaning_de", "v32_meaning_de",
        "composition", "rival_de", "occurrences", "pages", "reader_exact_occurrences",
        "split_normalized_occurrences", "reader_variant_occurrences", "decision", "decision_basis",
        "strongest_counterargument",
    ))
    write_tsv(output_dir / "DAL_AL_LATTICE_ATLAS.tsv", lattice_rows, (
        "family", "surface", "decomposition", "level_or_role", "planned_role", "v31_meaning_de",
        "v32_meaning_de", "zl3b_occurrences", "pages", "reader_exact_occurrences",
        "split_normalized_occurrences", "final_status",
    ))
    write_tsv(output_dir / "BOUNDARY_EVIDENCE_ATLAS.tsv", boundary_rows, (
        "bridge_id", "evidence_type", "page", "locus", "diagnostic_surface",
        "zl3b_line", "it2a_line", "rf1b_line", "supports",
    ))
    write_tsv(output_dir / "PARALLEL_MEASURE_EVIDENCE.tsv", parallel_rows, (
        "evidence_id", "page", "locus", "relation", "working_reading_de",
        "zl3b_line", "it2a_line", "rf1b_line", "all_three_exact_line",
    ))
    write_tsv(output_dir / "PAIR_CONTRAST_COUNTS.tsv", pair_rows, (
        "first_surface", "second_surface", "required_distinction_de", "cooccurrence_lines",
        "all_reader_exact_lines", "example_loci",
    ))
    write_tsv(output_dir / "REVISION_LEDGER.tsv", revision_rows, (
        "surface", "mode", "v31_meaning_de", "v32_meaning_de", "occurrences",
        "reader_exact_occurrences", "reason",
    ))
    write_tsv(output_dir / "ALL_OCCURRENCE_SEMANTIC_AUDIT.tsv", audit_rows, (
        "audit_id", "round", "surface", "mode", "page", "locus", "section", "language", "hand",
        "token_ordinal", "line_position", "previous", "following", "zl3b_line", "it2a_line", "rf1b_line",
        "reader_support", "reader_exact", "split_normalized", "before_gloss_de", "after_gloss_de",
        "known_other_tokens", "v31_line_de", "v32_line_de", "hard_collision", "verdict",
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
        "tokenwise_v32_de", "working_reading_de", "syntax_note",
    ))
    write_tsv(output_dir / "CURATED_COMPLETE_PASSAGE_READINGS.tsv", curated_complete_rows, (
        "page", "locus", "strict_complete", "target_surfaces", "zl3b_line",
        "tokenwise_v32_de", "curated_workshop_reading_de", "syntax_note",
    ))
    write_tsv(output_dir / "AFFECTED_LINE_TRANSLATIONS.tsv", affected_rows, (
        "page", "locus", "target_surfaces", "zl3b_line", "v31_tokenwise_de", "v32_tokenwise_de", "complete_v32",
    ))
    write_tsv(output_dir / "NEWLY_COMPLETED_LINES.tsv", new_complete_rows, (
        "page", "locus", "strict_complete", "enabled_by_surfaces", "zl3b_line",
        "literal_v32_de", "curated_workshop_reading_de",
    ))
    write_tsv(output_dir / "NEWLY_EXPOSED_ONE_HOLE_LINES.tsv", newly_exposed_rows, (
        "introduced_round", "enabled_by_surface", *ONE_FIELDS,
    ))
    write_tsv(output_dir / "V32_WORKING_TOKEN_GLOSSARY.tsv", final_gloss_rows, (
        "surface", "working_meaning_de", "source", "strength", "scope_state", "priority",
    ))
    write_tsv(output_dir / "ALL_LINE_CONCRETE_COVERAGE_V32.tsv", final_coverage, COVERAGE_FIELDS)
    write_tsv(output_dir / "COMPLETE_PASSAGES_V32.tsv", final_complete, (
        "rank", "strict_complete", *COVERAGE_FIELDS, "working_translation_de",
    ))
    write_tsv(output_dir / "ONE_UNKNOWN_PASSAGES_V32.tsv", final_one, ONE_FIELDS)
    write_tsv(output_dir / "WORKING_DICTIONARY_V32.tsv", final_dictionary, (
        "entry", "kind", "working_meaning_de", "composition", "context_rule", "status",
    ))

    output_paths = [output_dir / name for name in OUTPUT_NAMES]
    input_paths = (
        G654_RUN, G654_ALLOW, G654_COVERAGE, G654_COMPLETE, G654_ONE,
        G654_GLOSSARY, G654_DICTIONARY, G654_RESULT, G654_REPORT,
        G636_REPORT, G649_REPORT, G653_REPORT, TOKENS_REL, CROSS_REL,
    )
    verdicts = Counter(row["verdict"] for row in audit_rows)
    result_core = {
        "schema": "GDT655_DAL_AL_MEASURED_MATERIAL_RESULT_V1",
        "experiment_id": "GDT655", "status": STATUS,
        "guard": {"f1r": "EXCLUDED", "f84": "FORBIDDEN", "f84r": "FORBIDDEN", "new_pages": 0,
                  "new_images": 0, "allowed_pages": len(pages), "token_query": token_stats, "cross_query": cross_stats},
        "target_run": {
            "candidates": len(target_deck), "accepted_whole_cards": len(target_deck),
            "reader_anchored_exact_wholes": sum(int(row["reader_exact_occurrences"]) > 0 for row in target_deck),
            "reader_unstable_predicted_wholes": sum(int(row["reader_exact_occurrences"]) == 0 for row in target_deck),
            "accepted_surfaces": [row["surface"] for row in target_deck],
            "reader_anchored_new_surfaces": [
                row["surface"] for row in target_deck if row["mode"].startswith("NEW")
            ],
            "all_new_surfaces": [
                row["surface"] for row in target_deck if not row["mode"].startswith("REVISE")
            ],
            "reader_unstable_predicted_surfaces": [
                row["surface"] for row in target_deck if row["mode"] == "READER_UNSTABLE_COMPOSITIONAL_WHOLE"
            ],
            "revised_surfaces": [row["surface"] for row in target_deck if row["mode"].startswith("REVISE")],
            "audited_occurrences": len(audit_rows),
            "all_reader_exact_occurrences": sum(int(row["reader_exact"]) for row in audit_rows),
            "split_normalized_occurrences": sum(int(row["split_normalized"]) for row in audit_rows),
            "reader_variant_warnings": sum(row["verdict"] == "READER_VARIANT_WARNING" for row in audit_rows),
            "hard_collisions": sum(int(row["hard_collision"]) for row in audit_rows),
            "verdicts": dict(sorted(verdicts.items())),
        },
        "semantic_model": {
            "AL_I": "Rohstoffklasse I", "AIL_II": "Rohstoffklasse II", "AIIL_III": "Rohstoffklasse III",
            "DAL_I": "abgemessene Rohstoffmenge I", "DAIL_II": "abgemessene Rohstoffmenge II",
            "ORAL": "Rohstoffportion, Klasse I",
            "AR_OR_DAL": "Mischungsanteil oder Fraktion / abgemessene Eingangsmenge / abgeteilte Portion",
            "strongest_parallel": "f45v.4 all-reader exact DAIN DAIL DAIR at level II",
            "strongest_rival": "DAL is a learned raw-drug lot and AL is a raw-material form",
            "reader_unstable_prediction": "daiil=abgemessene Rohstoffmenge III; ZL3b/IT2a agree while RF1b omits D",
            "zero_exact_holds": ["aiiil", "chdaldy"],
            "structural_tags_not_free_words": [
                "AL_CLASS_I", "D_MEASURE", "DAL_MEASURED_MATERIAL_I", "CH_DRY_START", "SHE_MOIST_MIDDLE",
                "O_PREP", "QO_SCOPE", "Y_BASE", "DY_COMPLETE",
            ],
        },
        "coverage": {"base": base_metrics, "final": final_metrics,
                     "newly_completed_lines": len(new_complete_rows),
                     "newly_exposed_one_hole_lines": len(newly_exposed_rows),
                     "affected_lines": len(affected_rows)},
        "working_dictionary": {"v31_entries": len(base_dictionary), "v32_entries": len(final_dictionary),
                               "accepted_tail_entries": len(accepted_dictionary_rows),
                               "v31_prefix_sha256": canonical_hash(base_dictionary),
                               "v32_sha256": canonical_hash(final_dictionary),
                               "v31_glossary_surfaces": len(base_glossary), "v32_glossary_surfaces": len(glossary)},
        "claim_boundary": (
            "GDT655 is an exploratory working-translation consolidation, not solved plaintext. It promotes fifteen new reader-anchored exact wholes, one explicitly reader-unstable compositional whole DAIIL, and revises ORAL, CHDALY and SODAL inside the AL/DAL measured-material family. "
            "AL=Rohstoffklasse and DAL=abgemessene Rohstoffmenge are concrete replaceable defaults; Rohstoffform and Rohdrogenposten remain active rivals. "
            "No free component, global suffix, other zero-exact or absent-cell meaning, phonetics, language, exact ingredient identity, f1r, new page or new image is asserted."
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
    target_run, coverage = result["target_run"], result["coverage"]
    print(
        f"GDT655 built: accepted={target_run['accepted_whole_cards']} audits={target_run['audited_occurrences']} "
        f"known={coverage['final']['known_token_positions']} complete={coverage['final']['complete_multi_token_lines']} "
        f"strict={coverage['final']['strict_complete_lines']} one_unknown={coverage['final']['one_unknown_lines']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
