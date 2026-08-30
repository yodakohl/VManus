#!/usr/bin/env python3
"""Build GDT657: ordered and nested multi-quality AL exact-whole cards."""
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
BASE_REL = Path("experiments/yolo/gdt657_multi_quality_al_shell_order")
ART = ROOT / BASE_REL / "artifacts"
G656 = Path("experiments/yolo/gdt656_al_quality_position_shell")
G624_REPORT = Path("experiments/yolo/gdt624_productive_quality_shell_grid/REPORT.md")
G640_REPORT = Path("experiments/yolo/gdt640_downstream_component_prediction/REPORT.md")

spec = importlib.util.spec_from_file_location("gdt656_builder_for_gdt657", ROOT / G656 / "src/run.py")
if spec is None or spec.loader is None:
    raise RuntimeError("cannot load GDT656 builder")
g656 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(g656)
TOKENS_REL = g656.TOKENS_REL
CROSS_REL = g656.CROSS_REL
COVERAGE_FIELDS = g656.COVERAGE_FIELDS
ONE_FIELDS = g656.ONE_FIELDS

STATUS = "PASS_20_MULTI_QUALITY_AL_ORDER_WHOLES__V34"
GENERIC_FILLER = re.compile(
    r"arbeitsgut|arbeitschritt|arbeitsschritt|arbeitsmittel|arbeitsstoff|"
    r"arbeitsobjekt|werkzeug|produkt weiter|f.hre .* aus|leite .* weiter",
    re.IGNORECASE,
)


def card(surface: str, mode: str, meaning: str, composition: str, rival: str) -> dict[str, str]:
    return {"surface": surface, "mode": mode, "working_meaning_de": meaning,
            "composition": composition, "rival_de": rival}


TARGET_SPECS = (
    card("chkal", "EXACT_ORDERED_WHOLE", "Rohstoffklasse I, trocken-heiß am Gradanfang", "CH_DRY_START+KAL_HOT_RAW_I_START", "gelerntes CHKAL oder ungeordnetes trocken-heiß-Paar"),
    card("chtal", "EXACT_ORDERED_WHOLE", "Rohstoffklasse I, trocken-kalt am Gradanfang", "CH_DRY_START+TAL_COLD_RAW_I_START", "gelerntes CHTAL oder ungeordnetes trocken-kalt-Paar"),
    card("chekal", "EXACT_ORDERED_WHOLE", "Rohstoffklasse I: trocken in der Gradmitte; heiß am Gradanfang", "CHE_DRY_MIDDLE+KAL_HOT_RAW_I_START", "trocken gebundener heißer Rohstoff oder gelerntes CHEKAL"),
    card("choal", "READER_UNSTABLE_PREDICTED_COMPOUND", "Trockenansatz aus Rohstoffklasse I", "CHO_DRY_PREPARATION_HEAD+AL_CLASS_I", "gelerntes CHOAL-Ganzwort"),
    card("chokal", "EXACT_ORDERED_WHOLE", "Trockenansatz aus heißem Rohstoff Klasse I am Gradanfang", "CHO_DRY_PREPARATION_HEAD+KAL_HOT_RAW_I_START", "gelerntes CHOKAL-Ganzwort"),
    card("chotal", "EXACT_ORDERED_WHOLE", "Trockenansatz aus kaltem Rohstoff Klasse I am Gradanfang", "CHO_DRY_PREPARATION_HEAD+TAL_COLD_RAW_I_START", "gelerntes CHOTAL-Ganzwort"),
    card("cheoal", "EXACT_PREPARATION_HEAD_WHOLE", "trocken angesetzte Zubereitung aus Rohstoffklasse I", "CHEO_DRY_PREPARED_HEAD+AL_CLASS_I", "gelerntes CHEOAL-Ganzwort"),
    card("cheokal", "EXACT_PREPARATION_HEAD_WHOLE", "trocken angesetzte Zubereitung aus heißem Rohstoff Klasse I am Gradanfang", "CHEO_DRY_PREPARED_HEAD+KAL_HOT_RAW_I_START", "gelerntes CHEOKAL-Ganzwort"),
    card("shtal", "EXACT_ORDERED_WHOLE", "Rohstoffklasse I, feucht-kalt am Gradanfang", "SH_MOIST_START+TAL_COLD_RAW_I_START", "gelerntes SHTAL oder ungeordnetes feucht-kalt-Paar"),
    card("shekal", "EXACT_ORDERED_WHOLE", "Rohstoffklasse I: feucht in der Gradmitte; heiß am Gradanfang", "SHE_MOIST_MIDDLE+KAL_HOT_RAW_I_START", "feucht gebundener heißer Rohstoff oder gelerntes SHEKAL"),
    card("shokal", "EXACT_ORDERED_WHOLE", "Feuchtansatz aus heißem Rohstoff Klasse I am Gradanfang", "SHO_MOIST_PREPARATION_HEAD+KAL_HOT_RAW_I_START", "gelerntes SHOKAL-Ganzwort"),
    card("sheoal", "EXACT_PREPARATION_HEAD_WHOLE", "feucht angesetzte Zubereitung aus Rohstoffklasse I", "SHEO_MOIST_PREPARED_HEAD+AL_CLASS_I", "gelerntes SHEOAL-Ganzwort"),
    card("sheotal", "EXACT_PREPARATION_HEAD_WHOLE", "feucht angesetzte Zubereitung aus kaltem Rohstoff Klasse I am Gradanfang", "SHEO_MOIST_PREPARED_HEAD+TAL_COLD_RAW_I_START", "gelerntes SHEOTAL-Ganzwort"),
    card("kchal", "EXACT_ORDERED_WHOLE", "Rohstoffklasse I, heiß-trocken am Gradanfang", "K_HOT_START+CHAL_DRY_RAW_I_START", "gelerntes KCHAL oder ungeordnetes heiß-trocken-Paar"),
    card("tchal", "EXACT_ORDERED_WHOLE", "Rohstoffklasse I, kalt-trocken am Gradanfang", "T_COLD_START+CHAL_DRY_RAW_I_START", "gelerntes TCHAL oder ungeordnetes kalt-trocken-Paar"),
    card("okchal", "EXACT_NESTED_WHOLE", "Ansatz aus heiß-trockenem Rohstoff Klasse I am Gradanfang", "O_PREP+KCH_HOT_DRY_START+AL_CLASS_I", "gelerntes OKCHAL-Ganzwort"),
    card("okshal", "EXACT_NESTED_WHOLE", "Ansatz aus heiß-feuchtem Rohstoff Klasse I am Gradanfang", "O_PREP+KSH_HOT_MOIST_START+AL_CLASS_I", "gelerntes OKSHAL-Ganzwort"),
    card("otchal", "EXACT_NESTED_WHOLE", "Ansatz aus kalt-trockenem Rohstoff Klasse I am Gradanfang", "O_PREP+TCH_COLD_DRY_START+AL_CLASS_I", "gelerntes OTCHAL-Ganzwort"),
    card("otshal", "EXACT_NESTED_WHOLE", "Ansatz aus kalt-feuchtem Rohstoff Klasse I am Gradanfang", "O_PREP+TSH_COLD_MOIST_START+AL_CLASS_I", "gelerntes OTSHAL-Ganzwort"),
    card("qokchal", "READER_UNSTABLE_LOCAL_ANALOGY", "Rohstoffklasse I, heiß-trocken am Gradanfang", "QO_SCOPE+KCH_HOT_DRY_START+AL_CLASS_I", "QOKCH+OL-Material oder gelerntes QOKCHAL"),
)
TARGET_BY_SURFACE = {row["surface"]: row for row in TARGET_SPECS}
EXPECTED_COUNTS = {
    "chkal": (10, 8, 9, 9), "chtal": (6, 5, 5, 5), "chekal": (11, 9, 9, 9),
    "choal": (1, 1, 0, 0), "chokal": (4, 4, 4, 4), "chotal": (4, 4, 4, 4),
    "cheoal": (1, 1, 1, 1), "cheokal": (1, 1, 1, 1), "shtal": (2, 2, 1, 1),
    "shekal": (3, 3, 3, 3), "shokal": (3, 3, 3, 3), "sheoal": (1, 1, 1, 1),
    "sheotal": (1, 1, 1, 1), "kchal": (2, 2, 1, 1), "tchal": (2, 2, 2, 2),
    "okchal": (4, 4, 3, 3), "okshal": (1, 1, 1, 1), "otchal": (2, 2, 2, 2),
    "otshal": (1, 1, 1, 1), "qokchal": (1, 1, 0, 0),
}
WARNING_SURFACES = {"choal", "qokchal"}
ABSENT_CORE_HOLDS = ("chetal", "cheotal", "shkal", "shoal", "shotal", "shetal", "sheokal")
EXPECTED_NEW_HOLES = {"f33r.5": ("shekal", "otam", 0), "f66v.5": ("chokal", "shedefam", 0),
                      "f93r.32": ("chokal", "schos", 1), "f56r.13": ("kchal", "chokcheo", 1)}
SHORT_TAILS = ("okal", "otal", "kal", "tal", "oal")
SIMPLE_V33_AL_SURFACES = {
    "al", "chal", "cheal", "cheeal", "shal", "sheal", "sheeal", "kal", "tal", "oal", "oeeal",
    "okal", "okeal", "otal", "oteal", "oteeal", "qoal", "qokal", "qokeal", "qokeeal", "qotal", "qoteal",
}
ORDER_CONTRASTS = (
    ("chkal", "kchal", "CH+KAL", "K+CHAL", "trocken-heiß", "heiß-trocken", "ORDER_VISIBLE__UNORDERED_HUMORAL_PAIR_RIVAL"),
    ("chtal", "tchal", "CH+TAL", "T+CHAL", "trocken-kalt", "kalt-trocken", "ORDER_VISIBLE__UNORDERED_HUMORAL_PAIR_RIVAL"),
    ("chokal", "okchal", "CHO+KAL", "O+KCH+AL", "Trockenansatz aus heißem Rohstoff", "Ansatz aus heiß-trockenem Rohstoff", "NESTING_VISIBLE__LEARNED_WHOLE_RIVAL"),
    ("chotal", "otchal", "CHO+TAL", "O+TCH+AL", "Trockenansatz aus kaltem Rohstoff", "Ansatz aus kalt-trockenem Rohstoff", "NESTING_VISIBLE__LEARNED_WHOLE_RIVAL"),
    ("shokal", "okshal", "SHO+KAL", "O+KSH+AL", "Feuchtansatz aus heißem Rohstoff", "Ansatz aus heiß-feuchtem Rohstoff", "NESTING_VISIBLE__LEARNED_WHOLE_RIVAL"),
)
BOUNDARY_SPECS = (
    ("G657-B01", "PREPARATION_HEAD_SPLIT", "f106r.30", "sheo al / sheoal", "SHEO remains a visible bound preparation head before AL"),
    ("G657-B02", "RIGHT_FUSION_WARNING", "f43v.14", "choal / choalche", "CHOAL retains a reader warning"),
    ("G657-B03", "VOWEL_RIVAL_WARNING", "f112v.44", "qokchal / qokchol", "QOKCHAL retains the QOKCHOL rival"),
    ("G657-B04", "RIGHT_FUSION_WARNING", "f113r.46", "chkal / chkalkar", "no inheritance through RF1b right fusion"),
    ("G657-B05", "RIGHT_FUSION_WARNING", "f111v.34", "chtal / chtalsam", "no inheritance through RF1b right fusion"),
    ("G657-B06", "SPLIT_WARNING", "f66v.4", "chekal / chek l", "CHEKAL has a reader split"),
    ("G657-B07", "ALTERNATE_READING_WARNING", "f95r1.11", "chekal / chckhal", "CHEKAL has an IT2a rival whole"),
    ("G657-B08", "OMISSION_WARNING", "f76v.30", "shtal / tal", "RF1b omits initial SH"),
)
HISTORICAL_COMPARATORS = (
    ("G657-H01", "1415", "Tadhg Ó Cuinn, An Irish Materia Medica", "learned drug names with hot/cold and dry/moist quality pairs", "https://celt.ucc.ie/published/G600005/index.html", "architecture only; no Voynich value"),
    ("G657-H02", "1415", "Uiola entry", "different qualities occupy beginning and end positions of degrees", "https://celt.ucc.ie/published/G600006/text890.html", "ordered multi-quality fields are historically possible"),
    ("G657-H03", "1415", "Nux longa entry", "middle and end subdegree positions are explicitly distinguished", "https://celt.ucc.ie/published/G600005/text825.html", "compact subdegree notation is historically possible"),
)
CURATED_ONE_HOLE_READINGS = {
    "f33r.5": "Pulverfraktion II; Drogenportion; Menge III; kalt im Zubereitungsrahmen, Grad III; [OL: Material-/Zustandsträger; aktiver Bedeutungsrivale]; heiße Drogenportion; Menge III; Rohstoffklasse I im heißen Ansatz; Rohstoffklasse I im kalten Ansatz; trockene abgemessene Rohstoffmenge I; Rohstoffklasse I: feucht in der Gradmitte, heiß am Gradanfang; heiße Drogenfraktion I; [OTAM].",
    "f66v.5": "Feucht am Gradanfang, abgeschlossen; [SHEDEFAM]; heiß in der Gradmitte, abgeschlossen; Trockenansatz aus heißem Rohstoff Klasse I am Gradanfang; abgemessene Rohstoffmenge I.",
    "f93r.32": "Materialmaß; Trockenansatz aus heißem Rohstoff Klasse I am Gradanfang; [SCHOS].",
    "f56r.13": "Heiß-trockener Ansatz am Gradanfang; [CHOKCHEO]; Rohstoffklasse I, heiß-trocken am Gradanfang.",
}
OUTPUT_NAMES = (
    "PAGE_ALLOWLIST.tsv", "TARGET_DECISION_DECK.tsv", "ACCEPTED_WHOLE_SURFACE_DEFAULTS.tsv",
    "ALL_OCCURRENCE_SEMANTIC_AUDIT.tsv", "READER_VARIANT_AUDIT.tsv",
    "MULTI_QUALITY_ORDER_CONTRASTS.tsv", "ABSENT_CORE_HOLDS.tsv", "BOUNDARY_EVIDENCE_ATLAS.tsv",
    "HISTORICAL_ARCHITECTURE_COMPARATORS.tsv", "EXACT_TARGET_SUPERFORM_NONLEAK.tsv",
    "GLOBAL_SHORT_TAIL_NONLEAK_CONTROL.tsv", "CH_SH_AL_FAMILY_FRONTIER.tsv",
    "NONLEAK_CONTROL_SUMMARY.tsv", "TARGET_LINE_COEXISTENCE_AUDIT.tsv", "ROUND_COVERAGE_COUNTS.tsv",
    "AFFECTED_LINE_TRANSLATIONS.tsv", "SOURCE_PASSAGE_REALITY_CHECK.tsv", "NEWLY_COMPLETED_LINES.tsv",
    "NEWLY_EXPOSED_ONE_HOLE_LINES.tsv", "V34_WORKING_TOKEN_GLOSSARY.tsv",
    "ALL_LINE_CONCRETE_COVERAGE_V34.tsv", "COMPLETE_PASSAGES_V34.tsv",
    "ONE_UNKNOWN_PASSAGES_V34.tsv", "WORKING_DICTIONARY_V34.tsv",
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


def canonical_hash(value: object) -> str:
    raw = json.dumps(value, sort_keys=True, ensure_ascii=True, separators=(",", ":")).encode()
    return hashlib.sha256(raw).hexdigest()


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def string_rows(rows) -> list[dict[str, str]]:
    return [{str(key): str(value) for key, value in row.items()} for row in rows]


def split_pipe(value: object) -> list[str]:
    return str(value).split(" | ") if str(value) else []


def line_position(line: list[dict[str, object]], token_index: int) -> int:
    for ordinal, token in enumerate(line, 1):
        if int(token["token_index"]) == token_index:
            return ordinal
    raise RuntimeError("token position not found")


def metrics(coverage, one_unknown, complete, glossary) -> dict[str, int]:
    return {"physical_lines": len(coverage),
            "known_token_positions": sum(int(row["known_tokens"]) for row in coverage),
            "unknown_token_positions": sum(int(row["unknown_tokens"]) for row in coverage),
            "complete_multi_token_lines": len(complete),
            "strict_complete_lines": sum(int(row["strict_complete"]) for row in complete),
            "one_unknown_lines": len(one_unknown),
            "strict_one_unknown_lines": sum(int(row["strict_eligible"]) for row in one_unknown),
            "working_glossary_surfaces": len(glossary)}


def control_rows(name: str, surfaces: set[str], tokens, exact, boundary, base_gloss, matcher) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for surface in sorted(surfaces):
        members = [row for row in tokens if row["eva"] == surface]
        rows.append({
            "control": name, "surface": surface, "matched_units": "|".join(matcher(surface)),
            "occurrences": len(members), "pages": len({row["page"] for row in members}),
            "reader_exact_occurrences": sum(exact[row["locus"], int(row["token_index"])] for row in members),
            "split_normalized_occurrences": sum(boundary[row["locus"], int(row["token_index"])] for row in members),
            "loci": "|".join(sorted({str(row["locus"]) for row in members})),
            "v33_status": "PROTECTED_KNOWN_WHOLE" if surface in base_gloss else "OPEN_UNKNOWN_WHOLE",
            "decision": "RETAIN_PROTECTED_V33_CARD" if surface in base_gloss else "NO_SUBSTRING_INHERITANCE__REMAIN_OPEN",
        })
    return rows


def summarize_control(name: str, rows: list[dict[str, object]], tokens) -> dict[str, object]:
    surfaces = {str(row["surface"]) for row in rows}
    members = [row for row in tokens if row["eva"] in surfaces]
    return {"control": name, "surface_types": len(rows), "token_positions": len(members),
            "pages": len({row["page"] for row in members}),
            "reader_exact_occurrences": sum(int(row["reader_exact_occurrences"]) for row in rows),
            "split_normalized_occurrences": sum(int(row["split_normalized_occurrences"]) for row in rows),
            "note": "overlapping control; do not add to another deck"}


def build(output_dir: Path) -> dict[str, object]:
    output_dir.mkdir(parents=True, exist_ok=True)
    pages = {row["page"] for row in read_tsv(ROOT / G656 / "artifacts/PAGE_ALLOWLIST.tsv")}
    if "f1r" in pages or any(page.startswith("f84") for page in pages):
        raise RuntimeError("allow-list contains excluded or forbidden page")
    query = g656.g655.g654.g653.g637.g636.g635.g634.g633.g632.g631.guarded_query
    tokens, token_stats = query(TOKENS_REL, pages, "page,locus,token_index,eva,section,language,hand")
    cross, cross_stats = query(CROSS_REL, pages, "page,locus,all_three_present,all_present_exact,zl3b_clean,it2a_clean,rf1b_clean")
    cross_by_locus = {row["locus"]: row for row in cross}
    by_line, _ = g656.g655.g654.g653.g637.g636.g635.g634.g633.g632.g631.line_maps([dict(row) for row in tokens])
    exact, boundary = g656.g655.g654.g653.g637.g636.g635.g634.stable_maps(tokens, cross_by_locus)
    edition = g656.g655.g654.g653.g637
    base_dict = read_tsv(ROOT / G656 / "artifacts/WORKING_DICTIONARY_V33.tsv")
    base_gloss_rows = read_tsv(ROOT / G656 / "artifacts/V33_WORKING_TOKEN_GLOSSARY.tsv")
    base_gloss = {row["surface"]: dict(row) for row in base_gloss_rows}
    base_cov = read_tsv(ROOT / G656 / "artifacts/ALL_LINE_CONCRETE_COVERAGE_V33.tsv")
    base_complete = read_tsv(ROOT / G656 / "artifacts/COMPLETE_PASSAGES_V33.tsv")
    base_one = read_tsv(ROOT / G656 / "artifacts/ONE_UNKNOWN_PASSAGES_V33.tsv")
    if (len(base_dict), len(base_gloss), len(base_cov), len(base_complete), len(base_one)) != (550, 471, 4128, 133, 239):
        raise RuntimeError("GDT656 V33 base counts changed")
    replay_cov, replay_one, _, replay_complete = edition.build_line_coverage(by_line, base_gloss, exact, boundary, cross_by_locus)
    if string_rows(replay_cov) != string_rows(base_cov) or string_rows(replay_one) != string_rows(base_one) or string_rows(replay_complete) != string_rows(base_complete):
        raise RuntimeError("GDT656 V33 editions do not replay")
    if any(surface in base_gloss for surface in TARGET_BY_SURFACE):
        raise RuntimeError("GDT657 target already present in V33")
    if any(GENERIC_FILLER.search(row["working_meaning_de"]) for row in TARGET_SPECS):
        raise RuntimeError("generic target gloss")
    target_surfaces = set(TARGET_BY_SURFACE)
    all_surfaces = {str(row["eva"]) for row in tokens}
    direct_superforms = {surface for surface in all_surfaces if surface not in base_gloss and surface not in target_surfaces
                         and any(surface.endswith(target) for target in target_surfaces)}
    short_tail_surfaces = {surface for surface in all_surfaces if surface not in base_gloss and surface not in target_surfaces
                           and surface.endswith(SHORT_TAILS)}
    family_exclusions = target_surfaces | {"chal", "cheal", "cheeal", "shal", "sheal", "sheeal"}
    family_frontier = {surface for surface in all_surfaces if surface.startswith(("ch", "sh"))
                       and surface.endswith("al") and surface not in family_exclusions}
    direct_rows = control_rows(
        "DIRECT_TARGET_SUPERFORM_NONLEAK", direct_superforms, tokens, exact, boundary, base_gloss,
        lambda surface: sorted((target for target in target_surfaces if surface.endswith(target)), key=lambda value: (-len(value), value)),
    )
    short_rows = control_rows(
        "GLOBAL_SHORT_TAIL_NONLEAK", short_tail_surfaces, tokens, exact, boundary, base_gloss,
        lambda surface: [tail for tail in SHORT_TAILS if surface.endswith(tail)],
    )
    family_rows = control_rows(
        "CH_SH_AL_FAMILY_FRONTIER", family_frontier, tokens, exact, boundary, base_gloss,
        lambda surface: ["CH_OR_SH...AL"],
    )
    open_family_rows = [row for row in family_rows if row["v33_status"] == "OPEN_UNKNOWN_WHOLE"]
    protected_family_rows = [row for row in family_rows if row["v33_status"] == "PROTECTED_KNOWN_WHOLE"]
    control_summaries = [
        summarize_control("DIRECT_TARGET_SUPERFORM_NONLEAK", direct_rows, tokens),
        summarize_control("GLOBAL_SHORT_TAIL_NONLEAK", short_rows, tokens),
        summarize_control("CH_SH_AL_FAMILY_FRONTIER_ALL", family_rows, tokens),
        summarize_control("CH_SH_AL_FAMILY_FRONTIER_OPEN", open_family_rows, tokens),
        summarize_control("CH_SH_AL_FAMILY_FRONTIER_PROTECTED", protected_family_rows, tokens),
    ]
    frozen_controls = tuple((row["surface_types"], row["token_positions"], row["pages"],
                             row["reader_exact_occurrences"], row["split_normalized_occurrences"])
                            for row in control_summaries)
    if frozen_controls != ((4, 4, 4, 3, 3), (45, 85, 44, 67, 72), (45, 117, 61, 90, 91),
                           (40, 57, 43, 48, 49), (5, 60, 31, 42, 42)):
        raise RuntimeError(f"nonleak control drift: {frozen_controls!r}")
    if {row["surface"] for row in protected_family_rows} != {"chckhal", "chdal", "chedal", "shdal", "shedal"}:
        raise RuntimeError("protected family frontier changed")

    boundary_rows = []
    for bridge_id, evidence_type, locus, diagnostic, supports in BOUNDARY_SPECS:
        reader = cross_by_locus.get(locus)
        if reader is None:
            raise RuntimeError(f"missing boundary locus: {locus}")
        boundary_rows.append({"bridge_id": bridge_id, "evidence_type": evidence_type, "page": reader["page"],
                              "locus": locus, "diagnostic_surface": diagnostic, "zl3b_line": reader["zl3b_clean"],
                              "it2a_line": reader["it2a_clean"], "rf1b_line": reader["rf1b_clean"], "supports": supports})

    deck: list[dict[str, object]] = []
    audit_rows: list[dict[str, object]] = []
    variant_rows: list[dict[str, object]] = []
    round_rows: list[dict[str, object]] = [{"round": 0, "surface": "BASE_V33", "mode": "BASE",
        "dictionary_entries": len(base_dict), "dictionary_sha256": canonical_hash(base_dict),
        **metrics(base_cov, base_one, base_complete, base_gloss)}]
    newly_exposed_rows: list[dict[str, object]] = []
    seen_one_loci = {row["locus"] for row in base_one}
    gloss = {key: dict(value) for key, value in base_gloss.items()}
    dictionary = [dict(row) for row in base_dict]
    coverage, one, _, complete = edition.build_line_coverage(by_line, gloss, exact, boundary, cross_by_locus)
    for index, row in enumerate(TARGET_SPECS, 1):
        surface = row["surface"]
        members = [member for member in tokens if member["eva"] == surface]
        members.sort(key=lambda member: (member["page"], member["locus"], int(member["token_index"])))
        observed = (len(members), len({m["page"] for m in members}),
                    sum(exact[m["locus"], int(m["token_index"])] for m in members),
                    sum(boundary[m["locus"], int(m["token_index"])] for m in members))
        if observed != EXPECTED_COUNTS[surface]:
            raise RuntimeError(f"target count drift {surface}: {observed!r}")
        if surface in WARNING_SURFACES:
            for member in members:
                readers = cross_by_locus[member["locus"]]
                if surface not in readers["zl3b_clean"].split() or surface not in readers["it2a_clean"].split():
                    raise RuntimeError(f"warning surface lost ZL3b/IT2a agreement: {surface}")
        pre_by_locus = {item["locus"]: item for item in coverage}
        edition.set_gloss(gloss, surface, row["working_meaning_de"], f"GDT657:{row['mode']}",
                          "EXACT_WHOLE_MULTI_QUALITY_AL_ORDER", "KNOWN_EXACT_WHOLE", 155)
        dictionary.append({"entry": f"{surface}@GDT657_EXACT_WHOLE", "kind": f"EXACT_ZL3B_WHOLE_{row['mode']}",
                           "working_meaning_de": row["working_meaning_de"], "composition": row["composition"],
                           "context_rule": f"exact complete ZL3b surface only; {observed[0]} occurrences; {observed[2]} reader-exact; no substring inheritance",
                           "status": f"NEW_V34_ACCEPTED_ROUND_{index:02d}"})
        deck.append({"candidate_order": index, **row, "occurrences": observed[0], "pages": observed[1],
                     "reader_exact_occurrences": observed[2], "split_normalized_occurrences": observed[3],
                     "decision": "ACCEPT_V34_WITH_READER_WARNING" if surface in WARNING_SURFACES else "ACCEPT_V34_EXACT_WHOLE"})
        coverage, one, _, complete = edition.build_line_coverage(by_line, gloss, exact, boundary, cross_by_locus)
        post_by_locus = {item["locus"]: item for item in coverage}
        for occurrence, member in enumerate(members, 1):
            locus, token_index = member["locus"], int(member["token_index"])
            line = by_line[locus]
            ordinal = line_position(line, token_index)
            before, after = pre_by_locus[locus], post_by_locus[locus]
            before_glosses, after_glosses = split_pipe(before["token_glosses_de"]), split_pipe(after["token_glosses_de"])
            reader = cross_by_locus[locus]
            reader_exact, normalized = exact[locus, token_index], boundary[locus, token_index]
            zl_it_agree = int(surface in reader["zl3b_clean"].split() and surface in reader["it2a_clean"].split())
            support = "ALL_THREE_EXACT" if reader_exact else "ALL_THREE_SPLIT_NORMALIZED" if normalized else "ZL3B_IT2A_EXACT_RF_VARIANT" if zl_it_agree else "READER_VARIANT"
            verdict = "READER_VARIANT_WARNING" if not normalized else "CONCRETE_CONTEXT_COMPATIBLE" if int(before["known_tokens"]) >= 2 else "SHORT_OR_OPAQUE_CONTEXT"
            audit_rows.append({"audit_id": f"G657-A{index:02d}-{occurrence:04d}", "round": index,
                "surface": surface, "mode": row["mode"], "page": member["page"], "locus": locus,
                "section": member["section"], "language": member["language"], "hand": member["hand"],
                "token_ordinal": ordinal, "line_position": "ONLY" if len(line) == 1 else "INITIAL" if ordinal == 1 else "FINAL" if ordinal == len(line) else "MEDIAL",
                "previous": "<BOS>" if ordinal == 1 else line[ordinal - 2]["eva"],
                "following": "<EOS>" if ordinal == len(line) else line[ordinal]["eva"],
                "zl3b_line": before["zl3b_line"], "it2a_line": reader["it2a_clean"], "rf1b_line": reader["rf1b_clean"],
                "reader_support": support, "reader_exact": reader_exact, "split_normalized": normalized,
                "zl3b_it2a_exact": zl_it_agree, "before_gloss_de": before_glosses[ordinal - 1],
                "after_gloss_de": after_glosses[ordinal - 1], "known_other_tokens": int(before["known_tokens"]),
                "v33_line_de": before["token_glosses_de"], "v34_line_de": after["token_glosses_de"],
                "hard_collision": 0, "verdict": verdict})
            if support != "ALL_THREE_EXACT":
                variant_rows.append({"surface": surface, "page": member["page"], "locus": locus,
                    "zl3b_line": before["zl3b_line"], "it2a_line": reader["it2a_clean"], "rf1b_line": reader["rf1b_clean"],
                    "reader_support": support, "zl3b_it2a_exact": zl_it_agree,
                    "working_meaning_de": row["working_meaning_de"], "decision": "RETAIN_ZL3B_WHOLE_WITH_READER_WARNING"})
        current_one = {item["locus"]: item for item in one}
        for locus in sorted(set(current_one) - seen_one_loci):
            one_row = current_one[locus]
            newly_exposed_rows.append({"introduced_round": index, "enabled_by_surface": surface,
                **{field: one_row[field] for field in ONE_FIELDS},
                "curated_one_hole_reading_de": CURATED_ONE_HOLE_READINGS.get(locus, "NOT_CURATED")})
        seen_one_loci.update(current_one)
        round_rows.append({"round": index, "surface": surface, "mode": row["mode"],
            "dictionary_entries": len(dictionary), "dictionary_sha256": canonical_hash(dictionary),
            **metrics(coverage, one, complete, gloss)})
    final_metrics = metrics(coverage, one, complete, gloss)
    expected = {"physical_lines": 4128, "known_token_positions": 16696, "unknown_token_positions": 15643,
                "complete_multi_token_lines": 133, "strict_complete_lines": 78, "one_unknown_lines": 243,
                "strict_one_unknown_lines": 59, "working_glossary_surfaces": 491}
    if final_metrics != expected or len(dictionary) != 570:
        raise RuntimeError(f"unexpected V34 metrics: {final_metrics!r}")
    if (len(audit_rows), sum(int(row["reader_exact"]) for row in audit_rows),
            sum(int(row["split_normalized"]) for row in audit_rows), len(variant_rows)) != (61, 52, 52, 9):
        raise RuntimeError("target audit totals changed")
    if len({row["locus"] for row in audit_rows}) != 61 or len({row["page"] for row in audit_rows}) != 44:
        raise RuntimeError("target line/page totals changed")
    if sum(int(row["reader_exact_occurrences"]) > 0 for row in deck) != 18:
        raise RuntimeError("exact-whole anchor count changed")
    if {row["locus"] for row in complete} != {row["locus"] for row in base_complete}:
        raise RuntimeError("GDT657 unexpectedly completes or removes a passage")
    for surface in ABSENT_CORE_HOLDS:
        if any(row["eva"] == surface for row in tokens):
            raise RuntimeError(f"absent core hold became observed: {surface}")

    new_holes = [row for row in one if row["locus"] not in {base["locus"] for base in base_one}]
    if {row["locus"] for row in new_holes} != set(EXPECTED_NEW_HOLES) or len(newly_exposed_rows) != 4:
        raise RuntimeError("unexpected V34 one-hole frontier")
    exposed_by_locus = {row["locus"]: row for row in newly_exposed_rows}
    for locus, (enabled, residual, strict) in EXPECTED_NEW_HOLES.items():
        row = exposed_by_locus[locus]
        if (row["enabled_by_surface"], row["unknown_surface"], int(row["strict_eligible"])) != (enabled, residual, strict):
            raise RuntimeError(f"one-hole detail drift at {locus}")
        if row["curated_one_hole_reading_de"] == "NOT_CURATED" or GENERIC_FILLER.search(str(row["curated_one_hole_reading_de"])):
            raise RuntimeError(f"missing or generic one-hole reading at {locus}")

    final_gloss = [{key: row[key] for key in ("surface", "working_meaning_de", "source", "strength", "scope_state", "priority")}
                   for row in sorted(gloss.values(), key=lambda item: item["surface"])]
    final_by_locus = {row["locus"]: row for row in coverage}
    base_by_locus = {row["locus"]: row for row in base_cov}
    affected_rows: list[dict[str, object]] = []
    coexistence_rows: list[dict[str, object]] = []
    for locus in sorted(by_line):
        present = list(dict.fromkeys(token["eva"] for token in by_line[locus] if token["eva"] in target_surfaces))
        if not present:
            continue
        sisters = list(dict.fromkeys(token["eva"] for token in by_line[locus] if token["eva"] in SIMPLE_V33_AL_SURFACES))
        final = final_by_locus[locus]
        affected_rows.append({"page": final["page"], "locus": locus, "target_surfaces": "|".join(present),
            "zl3b_line": final["zl3b_line"], "v33_tokenwise_de": base_by_locus[locus]["token_glosses_de"],
            "v34_tokenwise_de": final["token_glosses_de"], "complete_v34": int(final["unknown_tokens"]) == 0})
        coexistence_rows.append({"page": final["page"], "locus": locus, "target_surfaces": "|".join(present),
            "target_count": len(present), "simple_v33_al_sisters": "|".join(sisters) or "NONE",
            "simple_v33_sister_present": int(bool(sisters)), "zl3b_line": final["zl3b_line"]})
    if len(affected_rows) != 61 or any(int(row["target_count"]) != 1 for row in coexistence_rows):
        raise RuntimeError("target line independence changed")
    if sum(int(row["simple_v33_sister_present"]) for row in coexistence_rows) != 15:
        raise RuntimeError("V33 AL sister coexistence changed")

    deck_by_surface = {row["surface"]: row for row in deck}
    contrast_rows = []
    for number, (left, right, left_parse, right_parse, left_meaning, right_meaning, decision) in enumerate(ORDER_CONTRASTS, 1):
        contrast_rows.append({"contrast_id": f"G657-O{number:02d}", "left_surface": left, "right_surface": right,
            "left_parse": left_parse, "right_parse": right_parse, "left_working_meaning_de": left_meaning,
            "right_working_meaning_de": right_meaning, "left_occurrences": deck_by_surface[left]["occurrences"],
            "right_occurrences": deck_by_surface[right]["occurrences"],
            "left_reader_exact": deck_by_surface[left]["reader_exact_occurrences"],
            "right_reader_exact": deck_by_surface[right]["reader_exact_occurrences"],
            "same_line_occurrences": 0, "decision": decision})
    hold_compositions = {
        "chetal": "CHE_DRY_MIDDLE+TAL_COLD_RAW_I_START", "cheotal": "CHEO_DRY_PREPARED_HEAD+TAL_COLD_RAW_I_START",
        "shkal": "SH_MOIST_START+KAL_HOT_RAW_I_START", "shoal": "SHO_MOIST_PREPARATION_HEAD+AL_CLASS_I",
        "shotal": "SHO_MOIST_PREPARATION_HEAD+TAL_COLD_RAW_I_START", "shetal": "SHE_MOIST_MIDDLE+TAL_COLD_RAW_I_START",
        "sheokal": "SHEO_MOIST_PREPARED_HEAD+KAL_HOT_RAW_I_START",
    }
    hold_rows = [{"surface": surface, "occurrences": 0, "pages": 0, "reader_exact_occurrences": 0,
                  "predicted_composition": hold_compositions[surface], "status": "ABSENT_PREDICTED_CELL_HOLD",
                  "decision": "NO_CARD__NO_MEANING_RELEASED"} for surface in ABSENT_CORE_HOLDS]
    accepted_defaults = [{"surface": item["surface"], **dictionary[550 + index],
                          "occurrences": item["occurrences"], "acceptance_mode": item["mode"]}
                         for index, item in enumerate(deck)]
    audits_by_surface: dict[str, list[dict[str, object]]] = {}
    for row in audit_rows:
        audits_by_surface.setdefault(str(row["surface"]), []).append(row)
    reality_rows = []
    for surface in TARGET_BY_SURFACE:
        candidates = audits_by_surface[surface]
        candidates.sort(key=lambda row: (-int(row["reader_exact"]), -int(row["known_other_tokens"]), str(row["locus"])))
        for rank, row in enumerate(candidates[:2 if len(candidates) >= 8 else 1], 1):
            final = final_by_locus[str(row["locus"])]
            reality_rows.append({"surface": surface, "selection_rank": rank, "page": row["page"], "locus": row["locus"],
                "reader_support": row["reader_support"], "zl3b_line": row["zl3b_line"],
                "tokenwise_v34_de": final["token_glosses_de"], "target_meaning_de": TARGET_BY_SURFACE[surface]["working_meaning_de"],
                "syntax_note": "EXACT_TOKEN_ORDER_BASELINE__RESIDUALS_RETAINED"})
    historical_rows = [{"comparator_id": row[0], "date": row[1], "source": row[2],
                        "observed_architecture": row[3], "source_url": row[4], "supports": row[5]}
                       for row in HISTORICAL_COMPARATORS]

    write_tsv(output_dir / "PAGE_ALLOWLIST.tsv", [{"page": page} for page in sorted(pages)], ("page",))
    write_tsv(output_dir / "TARGET_DECISION_DECK.tsv", deck, ("candidate_order", "surface", "mode", "working_meaning_de", "composition", "rival_de", "occurrences", "pages", "reader_exact_occurrences", "split_normalized_occurrences", "decision"))
    write_tsv(output_dir / "ACCEPTED_WHOLE_SURFACE_DEFAULTS.tsv", accepted_defaults, ("surface", "entry", "kind", "working_meaning_de", "composition", "context_rule", "status", "occurrences", "acceptance_mode"))
    write_tsv(output_dir / "ALL_OCCURRENCE_SEMANTIC_AUDIT.tsv", audit_rows, (
        "audit_id", "round", "surface", "mode", "page", "locus", "section", "language", "hand", "token_ordinal",
        "line_position", "previous", "following", "zl3b_line", "it2a_line", "rf1b_line", "reader_support",
        "reader_exact", "split_normalized", "zl3b_it2a_exact", "before_gloss_de", "after_gloss_de", "known_other_tokens",
        "v33_line_de", "v34_line_de", "hard_collision", "verdict"))
    write_tsv(output_dir / "READER_VARIANT_AUDIT.tsv", variant_rows, (
        "surface", "page", "locus", "zl3b_line", "it2a_line", "rf1b_line", "reader_support", "zl3b_it2a_exact",
        "working_meaning_de", "decision"))
    write_tsv(output_dir / "MULTI_QUALITY_ORDER_CONTRASTS.tsv", contrast_rows, (
        "contrast_id", "left_surface", "right_surface", "left_parse", "right_parse", "left_working_meaning_de",
        "right_working_meaning_de", "left_occurrences", "right_occurrences", "left_reader_exact", "right_reader_exact",
        "same_line_occurrences", "decision"))
    write_tsv(output_dir / "ABSENT_CORE_HOLDS.tsv", hold_rows, ("surface", "occurrences", "pages", "reader_exact_occurrences", "predicted_composition", "status", "decision"))
    write_tsv(output_dir / "BOUNDARY_EVIDENCE_ATLAS.tsv", boundary_rows, ("bridge_id", "evidence_type", "page", "locus", "diagnostic_surface", "zl3b_line", "it2a_line", "rf1b_line", "supports"))
    write_tsv(output_dir / "HISTORICAL_ARCHITECTURE_COMPARATORS.tsv", historical_rows, ("comparator_id", "date", "source", "observed_architecture", "source_url", "supports"))
    control_fields = ("control", "surface", "matched_units", "occurrences", "pages", "reader_exact_occurrences", "split_normalized_occurrences", "loci", "v33_status", "decision")
    write_tsv(output_dir / "EXACT_TARGET_SUPERFORM_NONLEAK.tsv", direct_rows, control_fields)
    write_tsv(output_dir / "GLOBAL_SHORT_TAIL_NONLEAK_CONTROL.tsv", short_rows, control_fields)
    write_tsv(output_dir / "CH_SH_AL_FAMILY_FRONTIER.tsv", family_rows, control_fields)
    write_tsv(output_dir / "NONLEAK_CONTROL_SUMMARY.tsv", control_summaries, ("control", "surface_types", "token_positions", "pages", "reader_exact_occurrences", "split_normalized_occurrences", "note"))
    write_tsv(output_dir / "TARGET_LINE_COEXISTENCE_AUDIT.tsv", coexistence_rows, ("page", "locus", "target_surfaces", "target_count", "simple_v33_al_sisters", "simple_v33_sister_present", "zl3b_line"))
    write_tsv(output_dir / "ROUND_COVERAGE_COUNTS.tsv", round_rows, ("round", "surface", "mode", "dictionary_entries", "dictionary_sha256", "physical_lines", "known_token_positions", "unknown_token_positions", "complete_multi_token_lines", "strict_complete_lines", "one_unknown_lines", "strict_one_unknown_lines", "working_glossary_surfaces"))
    write_tsv(output_dir / "AFFECTED_LINE_TRANSLATIONS.tsv", affected_rows, ("page", "locus", "target_surfaces", "zl3b_line", "v33_tokenwise_de", "v34_tokenwise_de", "complete_v34"))
    write_tsv(output_dir / "SOURCE_PASSAGE_REALITY_CHECK.tsv", reality_rows, ("surface", "selection_rank", "page", "locus", "reader_support", "zl3b_line", "tokenwise_v34_de", "target_meaning_de", "syntax_note"))
    write_tsv(output_dir / "NEWLY_COMPLETED_LINES.tsv", [], ("page", "locus", "strict_complete", "enabled_by_surfaces", "zl3b_line", "literal_v34_de"))
    write_tsv(output_dir / "ALL_LINE_CONCRETE_COVERAGE_V34.tsv", coverage, COVERAGE_FIELDS)
    write_tsv(output_dir / "COMPLETE_PASSAGES_V34.tsv", complete, ("rank", "strict_complete", *COVERAGE_FIELDS, "working_translation_de"))
    write_tsv(output_dir / "ONE_UNKNOWN_PASSAGES_V34.tsv", one, ONE_FIELDS)
    write_tsv(output_dir / "NEWLY_EXPOSED_ONE_HOLE_LINES.tsv", newly_exposed_rows, ("introduced_round", "enabled_by_surface", *ONE_FIELDS, "curated_one_hole_reading_de"))
    write_tsv(output_dir / "V34_WORKING_TOKEN_GLOSSARY.tsv", final_gloss, ("surface", "working_meaning_de", "source", "strength", "scope_state", "priority"))
    write_tsv(output_dir / "WORKING_DICTIONARY_V34.tsv", dictionary, ("entry", "kind", "working_meaning_de", "composition", "context_rule", "status"))

    output_paths = [output_dir / name for name in OUTPUT_NAMES]
    input_paths = (G656 / "src/run.py", G656 / "artifacts/PAGE_ALLOWLIST.tsv",
        G656 / "artifacts/ALL_LINE_CONCRETE_COVERAGE_V33.tsv", G656 / "artifacts/COMPLETE_PASSAGES_V33.tsv",
        G656 / "artifacts/ONE_UNKNOWN_PASSAGES_V33.tsv", G656 / "artifacts/V33_WORKING_TOKEN_GLOSSARY.tsv",
        G656 / "artifacts/WORKING_DICTIONARY_V33.tsv", G656 / "artifacts/RESULT.json", G656 / "REPORT.md",
        G624_REPORT, G640_REPORT, TOKENS_REL, CROSS_REL)
    verdicts = Counter(str(row["verdict"]) for row in audit_rows)
    result_core = {"schema": "GDT657_MULTI_QUALITY_AL_SHELL_ORDER_RESULT_V1", "experiment_id": "GDT657", "status": STATUS,
        "guard": {"f1r": "EXCLUDED", "f84": "FORBIDDEN", "f84r": "FORBIDDEN", "new_pages": 0,
            "new_images": 0, "allowed_pages": len(pages), "token_query": token_stats, "cross_query": cross_stats},
        "target_run": {"candidates": 20, "accepted_whole_cards": 20, "reader_anchored_exact_wholes": 18,
            "reader_warning_wholes": sorted(WARNING_SURFACES), "accepted_surfaces": [row["surface"] for row in deck],
            "audited_occurrences": 61, "target_lines": 61, "target_pages": 44,
            "sections": sorted({str(row["section"]) for row in audit_rows}),
            "languages": sorted({str(row["language"]) for row in audit_rows}),
            "hands": sorted({str(row["hand"]) for row in audit_rows}),
            "all_reader_exact_occurrences": 52, "split_normalized_occurrences": 52,
            "reader_variant_warnings": 9, "hard_collisions": 0, "verdicts": dict(sorted(verdicts.items()))},
        "ordered_model": {"order_contrasts": len(contrast_rows), "same_line_target_pairs": 0,
            "target_lines_with_simple_v33_al_sister": 15,
            "preparation_heads": "CHO/CHEO/SHO/SHEO are bound preparation heads inherited from GDT640",
            "diagnostic": "CHOKAL=CHO+KAL differs from OKCHAL=O+KCH+AL; CHKAL=CH+KAL differs from KCHAL=K+CHAL",
            "strongest_rival": "learned exact wholes or order-neutral humoral quality pairs",
            "structural_tags_not_free_words": ["AL_CLASS_I", "CH_DRY_START", "SH_MOIST_START", "K_HOT_START",
                "T_COLD_START", "CHO_DRY_PREPARATION_HEAD", "CHEO_DRY_PREPARED_HEAD",
                "SHO_MOIST_PREPARATION_HEAD", "SHEO_MOIST_PREPARED_HEAD", "O_PREP", "QO_SCOPE"],
            "absent_core_holds": list(ABSENT_CORE_HOLDS)},
        "nonleak_controls": {"decks_overlap_do_not_sum": True,
            "direct_target_superforms": control_summaries[0], "global_short_tail": control_summaries[1],
            "family_frontier_all": control_summaries[2], "family_frontier_open": control_summaries[3],
            "family_frontier_protected": control_summaries[4]},
        "coverage": {"base": metrics(base_cov, base_one, base_complete, base_gloss), "final": final_metrics,
            "newly_completed_lines": 0, "newly_exposed_one_hole_lines": 4, "affected_lines": 61,
            "new_one_hole_residuals": {locus: EXPECTED_NEW_HOLES[locus][1] for locus in sorted(EXPECTED_NEW_HOLES)}},
        "working_dictionary": {"v33_entries": len(base_dict), "v34_entries": len(dictionary),
            "accepted_tail_entries": 20, "v33_prefix_sha256": canonical_hash(base_dict), "v34_sha256": canonical_hash(dictionary),
            "v33_glossary_surfaces": len(base_gloss), "v34_glossary_surfaces": len(gloss)},
        "claim_boundary": "Exploratory exact-whole working translations for twenty observed multi-quality AL surfaces; ordered/nested predictions, not plaintext. CHOAL and QOKCHAL retain reader warnings. No substring inheritance, absent cell, free component, global character value, phonetics, language, exact ingredient, instruction, f1r, new page or image is asserted.",
        "inputs": {str(path): sha256(ROOT / path) for path in input_paths},
        "outputs": {str(BASE_REL / "artifacts" / path.name): sha256(path) for path in output_paths}}
    result = {**result_core, "content_sha256": canonical_hash(result_core)}
    (output_dir / "RESULT.json").write_text(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return result


def main() -> int:
    result = build(ART)
    print(f"GDT657 built: accepted=20 audits=61 exact=52 known={result['coverage']['final']['known_token_positions']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
