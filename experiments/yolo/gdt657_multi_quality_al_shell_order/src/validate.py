#!/usr/bin/env python3
"""Independent release validator for GDT657."""
from __future__ import annotations

import csv
import hashlib
import importlib.util
import io
import json
import re
import subprocess
import sys
import tempfile
from collections import Counter, defaultdict
from pathlib import Path

sys.dont_write_bytecode = True


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
BASE = Path("experiments/yolo/gdt657_multi_quality_al_shell_order")
ART = ROOT / BASE / "artifacts"
RUN = ROOT / BASE / "src/run.py"
MANIFEST = ROOT / BASE / "experiment.json"
REPORT = ROOT / BASE / "REPORT.md"
VALIDATION = ART / "VALIDATION.json"
G656 = Path("experiments/yolo/gdt656_al_quality_position_shell")
G656_ALLOW = G656 / "artifacts/PAGE_ALLOWLIST.tsv"
G656_COVERAGE = G656 / "artifacts/ALL_LINE_CONCRETE_COVERAGE_V33.tsv"
G656_COMPLETE = G656 / "artifacts/COMPLETE_PASSAGES_V33.tsv"
G656_ONE = G656 / "artifacts/ONE_UNKNOWN_PASSAGES_V33.tsv"
G656_GLOSSARY = G656 / "artifacts/V33_WORKING_TOKEN_GLOSSARY.tsv"
G656_DICTIONARY = G656 / "artifacts/WORKING_DICTIONARY_V33.tsv"
TOKENS = Path("transcription/voynich_zl3b_tokens.tsv")
CROSS = Path("transcription/voynich_cross_transcription_lines.tsv")

# surface: mode, German whole-surface default, ordered structural composition,
# occurrences, pages, all-reader exact occurrences, split-normalized occurrences
TARGETS = {
    "chkal": ("EXACT_ORDERED_WHOLE", "Rohstoffklasse I, trocken-heiß am Gradanfang", "CH_DRY_START+KAL_HOT_RAW_I_START", 10, 8, 9, 9),
    "chtal": ("EXACT_ORDERED_WHOLE", "Rohstoffklasse I, trocken-kalt am Gradanfang", "CH_DRY_START+TAL_COLD_RAW_I_START", 6, 5, 5, 5),
    "chekal": ("EXACT_ORDERED_WHOLE", "Rohstoffklasse I: trocken in der Gradmitte; heiß am Gradanfang", "CHE_DRY_MIDDLE+KAL_HOT_RAW_I_START", 11, 9, 9, 9),
    "choal": ("READER_UNSTABLE_PREDICTED_COMPOUND", "Trockenansatz aus Rohstoffklasse I", "CHO_DRY_PREPARATION_HEAD+AL_CLASS_I", 1, 1, 0, 0),
    "chokal": ("EXACT_ORDERED_WHOLE", "Trockenansatz aus heißem Rohstoff Klasse I am Gradanfang", "CHO_DRY_PREPARATION_HEAD+KAL_HOT_RAW_I_START", 4, 4, 4, 4),
    "chotal": ("EXACT_ORDERED_WHOLE", "Trockenansatz aus kaltem Rohstoff Klasse I am Gradanfang", "CHO_DRY_PREPARATION_HEAD+TAL_COLD_RAW_I_START", 4, 4, 4, 4),
    "cheoal": ("EXACT_PREPARATION_HEAD_WHOLE", "trocken angesetzte Zubereitung aus Rohstoffklasse I", "CHEO_DRY_PREPARED_HEAD+AL_CLASS_I", 1, 1, 1, 1),
    "cheokal": ("EXACT_PREPARATION_HEAD_WHOLE", "trocken angesetzte Zubereitung aus heißem Rohstoff Klasse I am Gradanfang", "CHEO_DRY_PREPARED_HEAD+KAL_HOT_RAW_I_START", 1, 1, 1, 1),
    "shtal": ("EXACT_ORDERED_WHOLE", "Rohstoffklasse I, feucht-kalt am Gradanfang", "SH_MOIST_START+TAL_COLD_RAW_I_START", 2, 2, 1, 1),
    "shekal": ("EXACT_ORDERED_WHOLE", "Rohstoffklasse I: feucht in der Gradmitte; heiß am Gradanfang", "SHE_MOIST_MIDDLE+KAL_HOT_RAW_I_START", 3, 3, 3, 3),
    "shokal": ("EXACT_ORDERED_WHOLE", "Feuchtansatz aus heißem Rohstoff Klasse I am Gradanfang", "SHO_MOIST_PREPARATION_HEAD+KAL_HOT_RAW_I_START", 3, 3, 3, 3),
    "sheoal": ("EXACT_PREPARATION_HEAD_WHOLE", "feucht angesetzte Zubereitung aus Rohstoffklasse I", "SHEO_MOIST_PREPARED_HEAD+AL_CLASS_I", 1, 1, 1, 1),
    "sheotal": ("EXACT_PREPARATION_HEAD_WHOLE", "feucht angesetzte Zubereitung aus kaltem Rohstoff Klasse I am Gradanfang", "SHEO_MOIST_PREPARED_HEAD+TAL_COLD_RAW_I_START", 1, 1, 1, 1),
    "kchal": ("EXACT_ORDERED_WHOLE", "Rohstoffklasse I, heiß-trocken am Gradanfang", "K_HOT_START+CHAL_DRY_RAW_I_START", 2, 2, 1, 1),
    "tchal": ("EXACT_ORDERED_WHOLE", "Rohstoffklasse I, kalt-trocken am Gradanfang", "T_COLD_START+CHAL_DRY_RAW_I_START", 2, 2, 2, 2),
    "okchal": ("EXACT_NESTED_WHOLE", "Ansatz aus heiß-trockenem Rohstoff Klasse I am Gradanfang", "O_PREP+KCH_HOT_DRY_START+AL_CLASS_I", 4, 4, 3, 3),
    "okshal": ("EXACT_NESTED_WHOLE", "Ansatz aus heiß-feuchtem Rohstoff Klasse I am Gradanfang", "O_PREP+KSH_HOT_MOIST_START+AL_CLASS_I", 1, 1, 1, 1),
    "otchal": ("EXACT_NESTED_WHOLE", "Ansatz aus kalt-trockenem Rohstoff Klasse I am Gradanfang", "O_PREP+TCH_COLD_DRY_START+AL_CLASS_I", 2, 2, 2, 2),
    "otshal": ("EXACT_NESTED_WHOLE", "Ansatz aus kalt-feuchtem Rohstoff Klasse I am Gradanfang", "O_PREP+TSH_COLD_MOIST_START+AL_CLASS_I", 1, 1, 1, 1),
    "qokchal": ("READER_UNSTABLE_LOCAL_ANALOGY", "Rohstoffklasse I, heiß-trocken am Gradanfang", "QO_SCOPE+KCH_HOT_DRY_START+AL_CLASS_I", 1, 1, 0, 0),
}
TARGET_ORDER = list(TARGETS)
UNSTABLE_TARGETS = {"choal", "qokchal"}
ABSENT_HOLDS = {
    "chetal": "CHE_DRY_MIDDLE+TAL_COLD_RAW_I_START",
    "cheotal": "CHEO_DRY_PREPARED_HEAD+TAL_COLD_RAW_I_START",
    "shkal": "SH_MOIST_START+KAL_HOT_RAW_I_START",
    "shoal": "SHO_MOIST_PREPARATION_HEAD+AL_CLASS_I",
    "shotal": "SHO_MOIST_PREPARATION_HEAD+TAL_COLD_RAW_I_START",
    "shetal": "SHE_MOIST_MIDDLE+TAL_COLD_RAW_I_START",
    "sheokal": "SHEO_MOIST_PREPARED_HEAD+KAL_HOT_RAW_I_START",
}
DIRECT_SUPERFORMS = ("dykchal", "olchokal", "schoal", "solchkal")
SHORT_TAILS = ("kal", "tal", "oal", "okal", "otal")
EXPECTED_SHORT_TAIL_TYPES = (
    "akal", "alkal", "aloal", "chakal", "cheeytal", "chekoal", "cholkal", "cphoal", "dalkal", "daroal",
    "dlkal", "doal", "dokal", "dtal", "dytal", "eeokal", "kalkal", "keeoal", "lkal", "lotal",
    "lsheetal", "ltal", "olchokal", "olkal", "oltal", "ototaykal", "pcheolkal", "pchoetal", "pcholkal", "qekal",
    "qetal", "qoetal", "qoolkal", "qotlolkal", "rkal", "schoal", "sheykal", "sholkal", "skal", "sokal",
    "solchkal", "ykal", "ykalkal", "ytal", "ytolkal",
)
SIMPLE_AL_ANCHORS = {"chal", "cheal", "cheeal", "shal", "sheal", "sheeal"}
PROTECTED_FRONTIER = {"chckhal", "chdal", "chedal", "shdal", "shedal"}
EXPECTED_FRONTIER_TYPES = (
    "chairal", "chakal", "chalal", "chcfhal", "chckhal", "chckheal", "chcthal", "chdal", "chdalal", "checthal",
    "chedal", "cheeeal", "cheeytal", "chefal", "chekoal", "chelal", "cheodal", "cheolchal", "chkaidararal", "chkodal",
    "chlal", "chodaal", "chodal", "choddal", "chokeal", "chokedal", "cholal", "choldal", "cholkal", "chopchal",
    "chorcholsal", "chpal", "sharal", "shcthal", "shdal", "sheckhal", "shedal", "sheedal", "sheodal", "sheolkeal",
    "sheykal", "shodal", "sholkal", "shoral", "shydal",
)
NEW_ONE_HOLES = {
    "f33r.5": ("shekal", "otam", "0"),
    "f66v.5": ("chokal", "shedefam", "0"),
    "f93r.32": ("chokal", "schos", "1"),
    "f56r.13": ("kchal", "chokcheo", "1"),
}
BASE_METRICS = {
    "physical_lines": 4128,
    "known_token_positions": 16635,
    "unknown_token_positions": 15704,
    "complete_multi_token_lines": 133,
    "strict_complete_lines": 78,
    "one_unknown_lines": 239,
    "strict_one_unknown_lines": 57,
    "working_glossary_surfaces": 471,
}
FINAL_METRICS = {
    "physical_lines": 4128,
    "known_token_positions": 16696,
    "unknown_token_positions": 15643,
    "complete_multi_token_lines": 133,
    "strict_complete_lines": 78,
    "one_unknown_lines": 243,
    "strict_one_unknown_lines": 59,
    "working_glossary_surfaces": 491,
}
STATUS = "PASS_20_MULTI_QUALITY_AL_ORDER_WHOLES__V34"
RESULT_CONTENT = "e19b3def67cf03dd7598738fc1655abe11f5c64287705c5dd42a63a494d3f8cf"
ORDER_CONTRASTS = (
    ("chkal", "kchal", "CH+KAL", "K+CHAL", "trocken-heiß", "heiß-trocken", "ORDER_VISIBLE__UNORDERED_HUMORAL_PAIR_RIVAL"),
    ("chtal", "tchal", "CH+TAL", "T+CHAL", "trocken-kalt", "kalt-trocken", "ORDER_VISIBLE__UNORDERED_HUMORAL_PAIR_RIVAL"),
    ("chokal", "okchal", "CHO+KAL", "O+KCH+AL", "Trockenansatz aus heißem Rohstoff", "Ansatz aus heiß-trockenem Rohstoff", "NESTING_VISIBLE__LEARNED_WHOLE_RIVAL"),
    ("chotal", "otchal", "CHO+TAL", "O+TCH+AL", "Trockenansatz aus kaltem Rohstoff", "Ansatz aus kalt-trockenem Rohstoff", "NESTING_VISIBLE__LEARNED_WHOLE_RIVAL"),
    ("shokal", "okshal", "SHO+KAL", "O+KSH+AL", "Feuchtansatz aus heißem Rohstoff", "Ansatz aus heiß-feuchtem Rohstoff", "NESTING_VISIBLE__LEARNED_WHOLE_RIVAL"),
)
BOUNDARIES = {
    "G657-B01": ("PREPARATION_HEAD_SPLIT", "f106r.30", "sheo al / sheoal", "SHEO remains a visible bound preparation head before AL"),
    "G657-B02": ("RIGHT_FUSION_WARNING", "f43v.14", "choal / choalche", "CHOAL retains a reader warning"),
    "G657-B03": ("VOWEL_RIVAL_WARNING", "f112v.44", "qokchal / qokchol", "QOKCHAL retains the QOKCHOL rival"),
    "G657-B04": ("RIGHT_FUSION_WARNING", "f113r.46", "chkal / chkalkar", "no inheritance through RF1b right fusion"),
    "G657-B05": ("RIGHT_FUSION_WARNING", "f111v.34", "chtal / chtalsam", "no inheritance through RF1b right fusion"),
    "G657-B06": ("SPLIT_WARNING", "f66v.4", "chekal / chek l", "CHEKAL has a reader split"),
    "G657-B07": ("ALTERNATE_READING_WARNING", "f95r1.11", "chekal / chckhal", "CHEKAL has an IT2a rival whole"),
    "G657-B08": ("OMISSION_WARNING", "f76v.30", "shtal / tal", "RF1b omits initial SH"),
}
HISTORICAL = (
    ("G657-H01", "1415", "Tadhg Ó Cuinn, An Irish Materia Medica", "learned drug names with hot/cold and dry/moist quality pairs", "https://celt.ucc.ie/published/G600005/index.html", "architecture only; no Voynich value"),
    ("G657-H02", "1415", "Uiola entry", "different qualities occupy beginning and end positions of degrees", "https://celt.ucc.ie/published/G600006/text890.html", "ordered multi-quality fields are historically possible"),
    ("G657-H03", "1415", "Nux longa entry", "middle and end subdegree positions are explicitly distinguished", "https://celt.ucc.ie/published/G600005/text825.html", "compact subdegree notation is historically possible"),
)
BUILDER_OUTPUTS = (
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
REPLAY_OUTPUTS = (*BUILDER_OUTPUTS, "RESULT.json")
INPUTS = {
    str(G656 / "src/run.py"), str(G656_ALLOW), str(G656_COVERAGE), str(G656_COMPLETE), str(G656_ONE),
    str(G656_GLOSSARY), str(G656_DICTIONARY), str(G656 / "artifacts/RESULT.json"), str(G656 / "REPORT.md"),
    "experiments/yolo/gdt624_productive_quality_shell_grid/REPORT.md",
    "experiments/yolo/gdt640_downstream_component_prediction/REPORT.md",
    str(TOKENS), str(CROSS),
}
FILLER = re.compile(
    r"arbeitsgut|arbeitschritt|arbeitsschritt|arbeitsmittel|arbeitsstoff|arbeitsobjekt|"
    r"werkzeug|produkt weiter|f.hre .* aus|leite .* weiter|geh(?:e)? zur arbeit|nimm .* arbeite",
    re.IGNORECASE,
)


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_hash(value: object) -> str:
    raw = json.dumps(value, sort_keys=True, ensure_ascii=True, separators=(",", ":")).encode()
    return hashlib.sha256(raw).hexdigest()


def guarded_query(path: Path, pages: set[str], columns: str) -> tuple[list[dict[str, str]], dict[str, int]]:
    command = [str(ROOT / "vmanus-exp"), "query-tsv", str(path), "--selector", "page"]
    for page in sorted(pages):
        command.extend(("--allow", page))
    command.extend(("--columns", columns, "--forbid-prefix", "f84", "--forbid-prefix", "f84r"))
    done = subprocess.run(command, cwd=ROOT, text=True, capture_output=True, check=False)
    stats_lines = [line for line in done.stderr.splitlines() if line.startswith("GUARD_STATS ")]
    if done.returncode or len(stats_lines) != 1:
        raise RuntimeError(done.stderr or "guarded query failed")
    rows = list(csv.DictReader(io.StringIO(done.stdout), delimiter="\t"))
    if any(row.get("page") == "f1r" or row.get("page", "").startswith("f84") for row in rows):
        raise RuntimeError("excluded or forbidden page materialized")
    return rows, json.loads(stats_lines[0].removeprefix("GUARD_STATS "))


def span_count(tokens: list[str], target: str) -> int:
    total = 0
    for start in range(len(tokens)):
        joined = ""
        for token in tokens[start:]:
            joined += token
            if joined == target:
                total += 1
                break
            if len(joined) >= len(target) or not target.startswith(joined):
                break
    return total


def independent_records(
    token_rows: list[dict[str, str]], cross_rows: list[dict[str, str]], surfaces: set[str]
) -> list[dict[str, object]]:
    cross = {row["locus"]: row for row in cross_rows}
    by_locus: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in token_rows:
        by_locus[row["locus"]].append(row)
    for line in by_locus.values():
        line.sort(key=lambda item: int(item["token_index"]))
    records: list[dict[str, object]] = []
    for surface in sorted(surfaces):
        members = [row for row in token_rows if row["eva"] == surface]
        members.sort(key=lambda item: (item["page"], item["locus"], int(item["token_index"])))
        seen: Counter[str] = Counter()
        for row in members:
            locus = row["locus"]
            seen[locus] += 1
            needed = seen[locus]
            readers = [cross[locus][field].split() for field in ("zl3b_clean", "it2a_clean", "rf1b_clean")]
            direct = [tokens.count(surface) for tokens in readers]
            spans = [span_count(tokens, surface) for tokens in readers]
            line = by_locus[locus]
            ordinal = next(i for i, token in enumerate(line, 1) if token is row)
            records.append(
                {
                    **row,
                    "token_ordinal": ordinal,
                    "previous": "<BOS>" if ordinal == 1 else line[ordinal - 2]["eva"],
                    "following": "<EOS>" if ordinal == len(line) else line[ordinal]["eva"],
                    "zl3b_line": cross[locus]["zl3b_clean"],
                    "it2a_line": cross[locus]["it2a_clean"],
                    "rf1b_line": cross[locus]["rf1b_clean"],
                    "reader_exact": int(needed <= min(direct)),
                    "split_normalized": int(needed <= min(spans)),
                }
            )
    return records


def census(records: list[dict[str, object]], surface: str) -> tuple[int, int, int, int]:
    members = [row for row in records if row["eva"] == surface]
    return (
        len(members),
        len({str(row["page"]) for row in members}),
        sum(int(row["reader_exact"]) for row in members),
        sum(int(row["split_normalized"]) for row in members),
    )


def aggregate_census(
    records: list[dict[str, object]], surfaces: set[str]
) -> tuple[int, int, int, int, int]:
    members = [row for row in records if str(row["eva"]) in surfaces]
    return (
        len(surfaces),
        len(members),
        len({str(row["page"]) for row in members}),
        sum(int(row["reader_exact"]) for row in members),
        sum(int(row["split_normalized"]) for row in members),
    )


def coverage_metrics(
    coverage: list[dict[str, str]], complete: list[dict[str, str]], one_unknown: list[dict[str, str]], glossary_size: int
) -> dict[str, int]:
    return {
        "physical_lines": len(coverage),
        "known_token_positions": sum(int(row["known_tokens"]) for row in coverage),
        "unknown_token_positions": sum(int(row["unknown_tokens"]) for row in coverage),
        "complete_multi_token_lines": len(complete),
        "strict_complete_lines": sum(int(row["strict_complete"]) for row in complete),
        "one_unknown_lines": len(one_unknown),
        "strict_one_unknown_lines": sum(int(row["strict_eligible"]) for row in one_unknown),
        "working_glossary_surfaces": glossary_size,
    }


def load_builder():
    spec = importlib.util.spec_from_file_location("gdt657_builder_validation", RUN)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load GDT657 builder")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main() -> int:
    passed: list[str] = []
    issues: list[str] = []

    def check(ok: object, name: str, detail: str = "") -> None:
        (passed if ok else issues).append(name if ok else f"{name}: {detail or 'condition failed'}")

    result = json.loads((ART / "RESULT.json").read_text(encoding="utf-8"))
    check(result.get("schema") == "GDT657_MULTI_QUALITY_AL_SHELL_ORDER_RESULT_V1", "result schema")
    check(result.get("experiment_id") == "GDT657" and result.get("status") == STATUS, "result identity/status")
    result_core = {key: value for key, value in result.items() if key != "content_sha256"}
    check(
        result.get("content_sha256") == RESULT_CONTENT == canonical_hash(result_core),
        "result content hash",
        str(result.get("content_sha256")),
    )

    allow_rows = read_tsv(ART / "PAGE_ALLOWLIST.tsv")
    pages = {row["page"] for row in allow_rows}
    check(len(allow_rows) == len(pages) == 179, "179 unique guarded pages")
    check("f1r" not in pages and not any(page.startswith("f84") for page in pages), "f1r excluded and f84/f84r forbidden")
    check((ART / "PAGE_ALLOWLIST.tsv").read_bytes() == (ROOT / G656_ALLOW).read_bytes(), "V33 allowlist inherited byte-identically")

    token_rows, token_stats = guarded_query(TOKENS, pages, "page,locus,token_index,eva,section,language,hand")
    cross_rows, cross_stats = guarded_query(
        CROSS, pages, "page,locus,all_three_present,all_present_exact,zl3b_clean,it2a_clean,rf1b_clean"
    )
    expected_token_stats = {"selected": 32339, "skipped_forbidden": 709, "skipped_not_allowed": 5940}
    expected_cross_stats = {"selected": 4137, "skipped_forbidden": 98, "skipped_not_allowed": 1151}
    check(len(token_rows) == 32339 and token_stats == expected_token_stats, "guarded token recensus", repr(token_stats))
    check(len(cross_rows) == 4137 and cross_stats == expected_cross_stats, "guarded cross recensus", repr(cross_stats))
    guard = result.get("guard", {})
    check(guard.get("token_query") == token_stats and guard.get("cross_query") == cross_stats, "result guarded query counts")
    check(
        guard.get("allowed_pages") == 179
        and guard.get("f1r") == "EXCLUDED"
        and guard.get("f84") == guard.get("f84r") == "FORBIDDEN"
        and guard.get("new_pages") == guard.get("new_images") == 0,
        "result guard ceiling",
    )

    base_gloss_rows = read_tsv(ROOT / G656_GLOSSARY)
    base_gloss = {row["surface"]: row for row in base_gloss_rows}
    all_surfaces = {row["eva"] for row in token_rows}
    target_surfaces = set(TARGETS)
    direct_surfaces = {
        surface
        for surface in all_surfaces
        if surface not in base_gloss
        and surface not in target_surfaces
        and any(surface.endswith(target) for target in target_surfaces)
    }
    short_surfaces = {
        surface
        for surface in all_surfaces
        if surface not in base_gloss
        and surface not in target_surfaces
        and surface.endswith(SHORT_TAILS)
    }
    frontier_surfaces = {
        surface
        for surface in all_surfaces
        if surface.startswith(("ch", "sh"))
        and surface.endswith("al")
        and surface not in target_surfaces | SIMPLE_AL_ANCHORS
    }
    check(direct_surfaces == set(DIRECT_SUPERFORMS), "independent direct-superform type derivation", repr(sorted(direct_surfaces)))
    check(short_surfaces == set(EXPECTED_SHORT_TAIL_TYPES), "independent short-tail type derivation", repr(sorted(short_surfaces)))
    check(frontier_surfaces == set(EXPECTED_FRONTIER_TYPES), "independent CH/SH...AL frontier derivation", repr(sorted(frontier_surfaces)))
    check(frontier_surfaces & set(base_gloss) == PROTECTED_FRONTIER, "independent protected-frontier derivation")

    census_surfaces = target_surfaces | set(ABSENT_HOLDS) | direct_surfaces | short_surfaces | frontier_surfaces
    records = independent_records(token_rows, cross_rows, census_surfaces)
    cross_by = {row["locus"]: row for row in cross_rows}
    by_locus: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in token_rows:
        by_locus[row["locus"]].append(row)
    for line in by_locus.values():
        line.sort(key=lambda item: int(item["token_index"]))

    deck = read_tsv(ART / "TARGET_DECISION_DECK.tsv")
    deck_by = {row["surface"]: row for row in deck}
    check(len(deck) == len(deck_by) == 20 and [row["surface"] for row in deck] == TARGET_ORDER, "20 ordered target cards")
    for index, (surface, spec) in enumerate(TARGETS.items(), 1):
        independent = census(records, surface)
        artifact = tuple(
            int(deck_by[surface][field])
            for field in ("occurrences", "pages", "reader_exact_occurrences", "split_normalized_occurrences")
        )
        check(independent == spec[3:] == artifact, f"independent target census:{surface}", repr(independent))
        check(
            tuple(deck_by[surface][field] for field in ("mode", "working_meaning_de", "composition")) == spec[:3],
            f"target semantics/composition:{surface}",
        )
        expected_decision = "ACCEPT_V34_WITH_READER_WARNING" if surface in UNSTABLE_TARGETS else "ACCEPT_V34_EXACT_WHOLE"
        check(
            deck_by[surface]["candidate_order"] == str(index)
            and deck_by[surface]["decision"] == expected_decision
            and bool(deck_by[surface]["rival_de"]),
            f"target admission/rival:{surface}",
        )
    check(
        sum(spec[3] for spec in TARGETS.values()) == 61
        and sum(spec[5] for spec in TARGETS.values()) == sum(spec[6] for spec in TARGETS.values()) == 52,
        "61 target positions and 52 exact/normalized",
    )
    target_records = [row for row in records if row["eva"] in target_surfaces]
    check(len({str(row["locus"]) for row in target_records}) == 61, "61 distinct target lines")
    check(len({str(row["page"]) for row in target_records}) == 44, "44 distinct target pages")
    check(
        {surface for surface, spec in TARGETS.items() if spec[5] == 0} == UNSTABLE_TARGETS
        and sum(spec[5] > 0 for spec in TARGETS.values()) == 18,
        "18 reader-anchored cards plus two named warning cards",
    )
    check(
        {str(row["section"]) for row in target_records} == {"B", "H", "P", "S", "T"}
        and {str(row["language"]) for row in target_records} == {"A", "B"}
        and {str(row["hand"]) for row in target_records} == {"1", "2", "3", "5"},
        "target register spread",
    )

    # The preparation heads are bound family chunks, not flat global character values.
    bound_head_compositions = {
        "choal": "CHO_DRY_PREPARATION_HEAD+AL_CLASS_I",
        "chokal": "CHO_DRY_PREPARATION_HEAD+KAL_HOT_RAW_I_START",
        "chotal": "CHO_DRY_PREPARATION_HEAD+TAL_COLD_RAW_I_START",
        "cheoal": "CHEO_DRY_PREPARED_HEAD+AL_CLASS_I",
        "cheokal": "CHEO_DRY_PREPARED_HEAD+KAL_HOT_RAW_I_START",
        "shokal": "SHO_MOIST_PREPARATION_HEAD+KAL_HOT_RAW_I_START",
        "sheoal": "SHEO_MOIST_PREPARED_HEAD+AL_CLASS_I",
        "sheotal": "SHEO_MOIST_PREPARED_HEAD+TAL_COLD_RAW_I_START",
    }
    check(
        all(deck_by[surface]["composition"] == composition for surface, composition in bound_head_compositions.items()),
        "CHO/CHEO/SHO/SHEO retained as bound preparation heads",
    )
    check(
        all("+O_PREP+" not in deck_by[surface]["composition"] for surface in bound_head_compositions),
        "no flat quality-plus-O decomposition leak",
    )

    base_coverage = read_tsv(ROOT / G656_COVERAGE)
    base_complete = read_tsv(ROOT / G656_COMPLETE)
    base_one = read_tsv(ROOT / G656_ONE)
    base_dictionary = read_tsv(ROOT / G656_DICTIONARY)
    coverage = read_tsv(ART / "ALL_LINE_CONCRETE_COVERAGE_V34.tsv")
    complete = read_tsv(ART / "COMPLETE_PASSAGES_V34.tsv")
    one = read_tsv(ART / "ONE_UNKNOWN_PASSAGES_V34.tsv")
    glossary_rows = read_tsv(ART / "V34_WORKING_TOKEN_GLOSSARY.tsv")
    glossary = {row["surface"]: row for row in glossary_rows}
    dictionary = read_tsv(ART / "WORKING_DICTIONARY_V34.tsv")
    check(coverage_metrics(base_coverage, base_complete, base_one, len(base_gloss)) == BASE_METRICS, "V33 base metrics")
    check(coverage_metrics(coverage, complete, one, len(glossary)) == FINAL_METRICS, "V34 final metrics")
    check(sum(int(row["token_count"]) for row in coverage) == 32339, "V34 token census")
    check((ART / "COMPLETE_PASSAGES_V34.tsv").read_bytes() == (ROOT / G656_COMPLETE).read_bytes(), "no completed-passage change")
    check(len(read_tsv(ART / "NEWLY_COMPLETED_LINES.tsv")) == 0, "zero newly completed lines")

    base_cov_by = {row["locus"]: row for row in base_coverage}
    cov_by = {row["locus"]: row for row in coverage}
    target_positions = Counter(row["locus"] for row in token_rows if row["eva"] in target_surfaces)
    check(
        all(
            int(cov_by[locus]["known_tokens"]) - int(base_cov_by[locus]["known_tokens"])
            == target_positions.get(locus, 0)
            for locus in cov_by
        ),
        "linewise 20-surface coverage deltas",
    )
    check(
        FINAL_METRICS["known_token_positions"] - BASE_METRICS["known_token_positions"] == 61
        and BASE_METRICS["unknown_token_positions"] - FINAL_METRICS["unknown_token_positions"] == 61,
        "V33-to-V34 position delta",
    )

    check(len(base_gloss_rows) == len(base_gloss) == 471 and len(glossary_rows) == len(glossary) == 491, "glossary 471 to 491")
    check(set(glossary) == set(base_gloss) | target_surfaces, "exact 20-surface glossary extension")
    check(all(glossary[surface] == row for surface, row in base_gloss.items()), "V33 glossary rows unchanged")
    for surface, spec in TARGETS.items():
        row = glossary[surface]
        check(
            tuple(row[field] for field in ("working_meaning_de", "source", "strength", "scope_state", "priority"))
            == (spec[1], f"GDT657:{spec[0]}", "EXACT_WHOLE_MULTI_QUALITY_AL_ORDER", "KNOWN_EXACT_WHOLE", "155"),
            f"V34 glossary card:{surface}",
        )
    check(not (set(ABSENT_HOLDS) | direct_surfaces | short_surfaces) & (set(glossary) - set(base_gloss)), "holds/nonleak types not exported")

    additions = dictionary[len(base_dictionary):]
    check(len(base_dictionary) == 550 and len(dictionary) == 570 and dictionary[:550] == base_dictionary, "dictionary 550 to 570 with frozen prefix")
    check([row["entry"].split("@", 1)[0] for row in additions] == TARGET_ORDER, "20 ordered dictionary additions")
    for index, (surface, row) in enumerate(zip(TARGET_ORDER, additions), 1):
        spec = TARGETS[surface]
        check(
            tuple(row[field] for field in ("entry", "kind", "working_meaning_de", "composition", "status"))
            == (
                f"{surface}@GDT657_EXACT_WHOLE",
                f"EXACT_ZL3B_WHOLE_{spec[0]}",
                spec[1],
                spec[2],
                f"NEW_V34_ACCEPTED_ROUND_{index:02d}",
            )
            and row["context_rule"].startswith("exact complete ZL3b surface only;")
            and "no substring inheritance" in row["context_rule"],
            f"dictionary exact-whole addition:{surface}",
        )
    accepted = read_tsv(ART / "ACCEPTED_WHOLE_SURFACE_DEFAULTS.tsv")
    check(len(accepted) == 20 and [row["surface"] for row in accepted] == TARGET_ORDER, "20 accepted defaults")
    check(
        all(
            accepted[index]["entry"] == additions[index]["entry"]
            and accepted[index]["working_meaning_de"] == TARGETS[surface][1]
            and accepted[index]["composition"] == TARGETS[surface][2]
            and accepted[index]["occurrences"] == str(TARGETS[surface][3])
            and accepted[index]["acceptance_mode"] == TARGETS[surface][0]
            for index, surface in enumerate(TARGET_ORDER)
        ),
        "accepted defaults mirror dictionary/deck",
    )

    audits = read_tsv(ART / "ALL_OCCURRENCE_SEMANTIC_AUDIT.tsv")
    check(len(audits) == len({row["audit_id"] for row in audits}) == 61, "61 unique occurrence audits")
    check(Counter(row["surface"] for row in audits) == Counter({surface: spec[3] for surface, spec in TARGETS.items()}), "audit surface census")
    check(sum(int(row["reader_exact"]) for row in audits) == sum(int(row["split_normalized"]) for row in audits) == 52, "audit 52 exact/normalized")
    check(sum(int(row["hard_collision"]) for row in audits) == 0, "zero target hard collisions")
    independent_by = {surface: [row for row in records if row["eva"] == surface] for surface in TARGETS}
    audit_by = {surface: [row for row in audits if row["surface"] == surface] for surface in TARGETS}
    for round_number, surface in enumerate(TARGET_ORDER, 1):
        fidelity = len(independent_by[surface]) == len(audit_by[surface])
        for occurrence, (expected, row) in enumerate(zip(independent_by[surface], audit_by[surface]), 1):
            cross = cross_by[str(expected["locus"])]
            zl_it = int(surface in cross["zl3b_clean"].split() and surface in cross["it2a_clean"].split())
            support = (
                "ALL_THREE_EXACT"
                if expected["reader_exact"]
                else "ALL_THREE_SPLIT_NORMALIZED"
                if expected["split_normalized"]
                else "ZL3B_IT2A_EXACT_RF_VARIANT"
                if zl_it
                else "READER_VARIANT"
            )
            fidelity &= (
                row["audit_id"] == f"G657-A{round_number:02d}-{occurrence:04d}"
                and row["round"] == str(round_number)
                and row["mode"] == TARGETS[surface][0]
                and tuple(row[field] for field in ("page", "locus", "section", "language", "hand"))
                == tuple(str(expected[field]) for field in ("page", "locus", "section", "language", "hand"))
                and (row["token_ordinal"], row["previous"], row["following"])
                == (str(expected["token_ordinal"]), str(expected["previous"]), str(expected["following"]))
                and tuple(row[field] for field in ("zl3b_line", "it2a_line", "rf1b_line"))
                == tuple(str(expected[field]) for field in ("zl3b_line", "it2a_line", "rf1b_line"))
                and (row["reader_exact"], row["split_normalized"], row["zl3b_it2a_exact"], row["reader_support"])
                == (str(expected["reader_exact"]), str(expected["split_normalized"]), str(zl_it), support)
                and row["before_gloss_de"] == f"[{surface}:?]"
                and row["after_gloss_de"] == TARGETS[surface][1]
                and row["v33_line_de"] == base_cov_by[str(expected["locus"])]["token_glosses_de"]
                and row["v34_line_de"] == cov_by[str(expected["locus"])]["token_glosses_de"]
            )
        check(fidelity, f"independent audit source/reader replay:{surface}")
    check(
        Counter(row["verdict"] for row in audits)
        == Counter({"CONCRETE_CONTEXT_COMPATIBLE": 46, "READER_VARIANT_WARNING": 9, "SHORT_OR_OPAQUE_CONTEXT": 6}),
        "audit verdict totals",
    )
    variants = read_tsv(ART / "READER_VARIANT_AUDIT.tsv")
    check(
        len(variants) == 9
        and Counter(row["reader_support"] for row in variants)
        == Counter({"ZL3B_IT2A_EXACT_RF_VARIANT": 6, "READER_VARIANT": 3}),
        "nine explicit reader warnings",
    )
    expected_variants = Counter(
        (row["surface"], row["page"], row["locus"], row["reader_support"], row["zl3b_it2a_exact"], TARGETS[row["surface"]][1])
        for row in audits
        if row["reader_exact"] == "0"
    )
    artifact_variants = Counter(
        (row["surface"], row["page"], row["locus"], row["reader_support"], row["zl3b_it2a_exact"], row["working_meaning_de"])
        for row in variants
    )
    check(
        artifact_variants == expected_variants
        and all(row["decision"] == "RETAIN_ZL3B_WHOLE_WITH_READER_WARNING" for row in variants),
        "variant audit exactly covers non-exact targets",
    )

    holds = read_tsv(ART / "ABSENT_CORE_HOLDS.tsv")
    holds_by = {row["surface"]: row for row in holds}
    check(len(holds) == len(holds_by) == 7 and list(holds_by) == list(ABSENT_HOLDS), "seven ordered absent core holds")
    for surface, composition in ABSENT_HOLDS.items():
        row = holds_by[surface]
        check(census(records, surface) == (0, 0, 0, 0), f"independent absent hold census:{surface}")
        check(
            (row["occurrences"], row["pages"], row["reader_exact_occurrences"], row["predicted_composition"], row["status"], row["decision"])
            == ("0", "0", "0", composition, "ABSENT_PREDICTED_CELL_HOLD", "NO_CARD__NO_MEANING_RELEASED"),
            f"absent hold decision:{surface}",
        )
    check(not set(ABSENT_HOLDS) & set(glossary), "absent holds not in V34 glossary")

    def check_control(path_name: str, expected_control: str, expected_surfaces: set[str]) -> list[dict[str, str]]:
        rows = read_tsv(ART / path_name)
        rows_by = {row["surface"]: row for row in rows}
        check(len(rows) == len(rows_by) == len(expected_surfaces) and set(rows_by) == expected_surfaces, f"{expected_control} exact type deck")
        for surface in sorted(expected_surfaces):
            row = rows_by[surface]
            independent = census(records, surface)
            artifact = tuple(
                int(row[field])
                for field in ("occurrences", "pages", "reader_exact_occurrences", "split_normalized_occurrences")
            )
            expected_loci = "|".join(sorted({str(record["locus"]) for record in records if record["eva"] == surface}))
            known = surface in base_gloss
            check(independent == artifact and row["loci"] == expected_loci, f"independent {expected_control} census:{surface}")
            check(
                row["control"] == expected_control
                and row["v33_status"] == ("PROTECTED_KNOWN_WHOLE" if known else "OPEN_UNKNOWN_WHOLE")
                and row["decision"]
                == ("RETAIN_PROTECTED_V33_CARD" if known else "NO_SUBSTRING_INHERITANCE__REMAIN_OPEN"),
                f"{expected_control} nonleak decision:{surface}",
            )
        return rows

    direct_rows = check_control("EXACT_TARGET_SUPERFORM_NONLEAK.tsv", "DIRECT_TARGET_SUPERFORM_NONLEAK", direct_surfaces)
    short_rows = check_control("GLOBAL_SHORT_TAIL_NONLEAK_CONTROL.tsv", "GLOBAL_SHORT_TAIL_NONLEAK", short_surfaces)
    frontier_rows = check_control("CH_SH_AL_FAMILY_FRONTIER.tsv", "CH_SH_AL_FAMILY_FRONTIER", frontier_surfaces)
    open_frontier = {row["surface"] for row in frontier_rows if row["v33_status"] == "OPEN_UNKNOWN_WHOLE"}
    protected_frontier = {row["surface"] for row in frontier_rows if row["v33_status"] == "PROTECTED_KNOWN_WHOLE"}
    check(len(open_frontier) == 40 and protected_frontier == PROTECTED_FRONTIER, "40 open plus five protected frontier types")
    control_expected = {
        "DIRECT_TARGET_SUPERFORM_NONLEAK": (4, 4, 4, 3, 3),
        "GLOBAL_SHORT_TAIL_NONLEAK": (45, 85, 44, 67, 72),
        "CH_SH_AL_FAMILY_FRONTIER_ALL": (45, 117, 61, 90, 91),
        "CH_SH_AL_FAMILY_FRONTIER_OPEN": (40, 57, 43, 48, 49),
        "CH_SH_AL_FAMILY_FRONTIER_PROTECTED": (5, 60, 31, 42, 42),
    }
    check(aggregate_census(records, direct_surfaces) == control_expected["DIRECT_TARGET_SUPERFORM_NONLEAK"], "direct-superform aggregate recensus")
    check(aggregate_census(records, short_surfaces) == control_expected["GLOBAL_SHORT_TAIL_NONLEAK"], "short-tail aggregate recensus")
    check(aggregate_census(records, frontier_surfaces) == control_expected["CH_SH_AL_FAMILY_FRONTIER_ALL"], "family-frontier aggregate recensus")
    check(aggregate_census(records, open_frontier) == control_expected["CH_SH_AL_FAMILY_FRONTIER_OPEN"], "open-frontier aggregate recensus")
    check(aggregate_census(records, protected_frontier) == control_expected["CH_SH_AL_FAMILY_FRONTIER_PROTECTED"], "protected-frontier aggregate recensus")
    summaries = read_tsv(ART / "NONLEAK_CONTROL_SUMMARY.tsv")
    summary_by = {row["control"]: row for row in summaries}
    check(len(summaries) == len(summary_by) == 5 and set(summary_by) == set(control_expected), "five separate nonleak summaries")
    for name, expected in control_expected.items():
        row = summary_by[name]
        observed = tuple(
            int(row[field])
            for field in ("surface_types", "token_positions", "pages", "reader_exact_occurrences", "split_normalized_occurrences")
        )
        check(observed == expected and "do not add" in row["note"], f"nonleak summary:{name}", repr(observed))
    check(bool(direct_surfaces & short_surfaces) and bool(short_surfaces & frontier_surfaces), "nonleak decks visibly overlap")

    contrasts = read_tsv(ART / "MULTI_QUALITY_ORDER_CONTRASTS.tsv")
    check(len(contrasts) == 5, "five order/nesting contrasts")
    for index, (row, spec) in enumerate(zip(contrasts, ORDER_CONTRASTS), 1):
        left, right, left_parse, right_parse, left_meaning, right_meaning, decision = spec
        check(
            tuple(
                row[field]
                for field in (
                    "contrast_id", "left_surface", "right_surface", "left_parse", "right_parse",
                    "left_working_meaning_de", "right_working_meaning_de", "decision",
                )
            )
            == (f"G657-O{index:02d}", left, right, left_parse, right_parse, left_meaning, right_meaning, decision)
            and (row["left_occurrences"], row["right_occurrences"], row["left_reader_exact"], row["right_reader_exact"])
            == (str(TARGETS[left][3]), str(TARGETS[right][3]), str(TARGETS[left][5]), str(TARGETS[right][5]))
            and row["same_line_occurrences"] == "0"
            and left_meaning != right_meaning,
            f"ordered contrast:{left}/{right}",
        )

    boundary_rows = read_tsv(ART / "BOUNDARY_EVIDENCE_ATLAS.tsv")
    boundary_by = {row["bridge_id"]: row for row in boundary_rows}
    check(len(boundary_rows) == len(boundary_by) == 8 and list(boundary_by) == list(BOUNDARIES), "eight ordered boundary witnesses")
    for bridge_id, (kind, locus, diagnostic, supports) in BOUNDARIES.items():
        row, source = boundary_by[bridge_id], cross_by[locus]
        check(
            (row["evidence_type"], row["locus"], row["diagnostic_surface"], row["supports"])
            == (kind, locus, diagnostic, supports),
            f"boundary identity:{bridge_id}",
        )
        check(
            row["page"] == source["page"]
            and tuple(row[field] for field in ("zl3b_line", "it2a_line", "rf1b_line"))
            == tuple(source[field] for field in ("zl3b_clean", "it2a_clean", "rf1b_clean")),
            f"boundary source fidelity:{bridge_id}",
        )
    historical = read_tsv(ART / "HISTORICAL_ARCHITECTURE_COMPARATORS.tsv")
    check(
        len(historical) == 3
        and [tuple(row[field] for field in ("comparator_id", "date", "source", "observed_architecture", "source_url", "supports")) for row in historical]
        == list(HISTORICAL),
        "three fixed 1415 architecture comparators",
    )

    base_one_loci = {row["locus"] for row in base_one}
    final_one_loci = {row["locus"] for row in one}
    check(final_one_loci - base_one_loci == set(NEW_ONE_HOLES) and not (base_one_loci - final_one_loci), "exact four-line one-hole frontier delta")
    exposed = read_tsv(ART / "NEWLY_EXPOSED_ONE_HOLE_LINES.tsv")
    exposed_by = {row["locus"]: row for row in exposed}
    check(len(exposed) == len(exposed_by) == 4 and set(exposed_by) == set(NEW_ONE_HOLES), "four unique newly exposed one-hole rows")
    expected_rounds = {surface: TARGET_ORDER.index(surface) + 1 for surface in TARGET_ORDER}
    for locus, (enabled, residual, strict) in NEW_ONE_HOLES.items():
        row = exposed_by[locus]
        curated = row["curated_one_hole_reading_de"]
        check(
            row["introduced_round"] == str(expected_rounds[enabled])
            and row["enabled_by_surface"] == enabled
            and row["unknown_tokens"] == "1"
            and row["unknown_surface"] == residual
            and row["strict_eligible"] == strict,
            f"one-hole provenance:{locus}",
        )
        check(
            f"[{residual.upper()}]" in curated
            and "?" not in curated
            and not FILLER.search(curated)
            and row["token_glosses_de"] == cov_by[locus]["token_glosses_de"]
            and row["zl3b_line"] == cov_by[locus]["zl3b_line"],
            f"one-hole literal curated reading:{locus}",
        )

    round_rows = read_tsv(ART / "ROUND_COVERAGE_COUNTS.tsv")
    check(len(round_rows) == 21 and [row["round"] for row in round_rows] == [str(index) for index in range(21)], "21 ordered coverage rounds")
    cumulative_known = BASE_METRICS["known_token_positions"]
    for index, row in enumerate(round_rows):
        if index:
            cumulative_known += TARGETS[TARGET_ORDER[index - 1]][3]
        expected_surface = "BASE_V33" if index == 0 else TARGET_ORDER[index - 1]
        expected_mode = "BASE" if index == 0 else TARGETS[expected_surface][0]
        expected_one = 239 if index < 5 else 241 if index < 10 else 242 if index < 14 else 243
        expected_strict_one = 57 if index < 5 else 58 if index < 14 else 59
        observed = (
            row["surface"], row["mode"], int(row["dictionary_entries"]), int(row["physical_lines"]),
            int(row["known_token_positions"]), int(row["unknown_token_positions"]),
            int(row["complete_multi_token_lines"]), int(row["strict_complete_lines"]),
            int(row["one_unknown_lines"]), int(row["strict_one_unknown_lines"]), int(row["working_glossary_surfaces"]),
        )
        expected = (
            expected_surface, expected_mode, 550 + index, 4128, cumulative_known,
            32339 - cumulative_known, 133, 78, expected_one, expected_strict_one, 471 + index,
        )
        check(observed == expected, f"round metrics:{index}", repr(observed))
        check(row["dictionary_sha256"] == canonical_hash(dictionary[: 550 + index]), f"round dictionary hash:{index}")

    affected = read_tsv(ART / "AFFECTED_LINE_TRANSLATIONS.tsv")
    affected_by = {row["locus"]: row for row in affected}
    target_loci = {row["locus"] for row in token_rows if row["eva"] in target_surfaces}
    check(len(affected) == len(affected_by) == 61 and set(affected_by) == target_loci, "61 affected-line edition rows")
    check(
        all(
            row["page"] == cov_by[locus]["page"]
            and row["zl3b_line"] == cov_by[locus]["zl3b_line"]
            and row["v33_tokenwise_de"] == base_cov_by[locus]["token_glosses_de"]
            and row["v34_tokenwise_de"] == cov_by[locus]["token_glosses_de"]
            and row["complete_v34"].lower() in {"false", "0"}
            for locus, row in affected_by.items()
        ),
        "affected-line source/edition fidelity",
    )
    simple_v33 = {
        "al", "chal", "cheal", "cheeal", "shal", "sheal", "sheeal", "kal", "tal", "oal", "oeeal",
        "okal", "okeal", "otal", "oteal", "oteeal", "qoal", "qokal", "qokeal", "qokeeal", "qotal", "qoteal",
    }
    coexistence = read_tsv(ART / "TARGET_LINE_COEXISTENCE_AUDIT.tsv")
    coexist_by = {row["locus"]: row for row in coexistence}
    check(len(coexistence) == len(coexist_by) == 61 and set(coexist_by) == target_loci, "61 target coexistence rows")
    coexistence_ok = True
    for locus, row in coexist_by.items():
        line_surfaces = [token["eva"] for token in by_locus[locus]]
        targets_here = list(dict.fromkeys(surface for surface in line_surfaces if surface in target_surfaces))
        sisters_here = list(dict.fromkeys(surface for surface in line_surfaces if surface in simple_v33))
        coexistence_ok &= (
            len(targets_here) == 1
            and row["target_surfaces"] == targets_here[0]
            and row["target_count"] == "1"
            and row["simple_v33_al_sisters"] == ("|".join(sisters_here) or "NONE")
            and row["simple_v33_sister_present"] == str(int(bool(sisters_here)))
            and row["zl3b_line"] == cov_by[locus]["zl3b_line"]
        )
    check(coexistence_ok, "independent target-line coexistence replay")
    check(sum(int(row["simple_v33_sister_present"]) for row in coexistence) == 15, "15 target lines with simple V33 AL sister")

    reality = read_tsv(ART / "SOURCE_PASSAGE_REALITY_CHECK.tsv")
    check(len(reality) == 22 and set(row["surface"] for row in reality) == target_surfaces, "22 reality checks cover all targets")
    check(
        all(
            row["locus"] in cross_by
            and row["zl3b_line"] == cross_by[row["locus"]]["zl3b_clean"]
            and row["tokenwise_v34_de"] == cov_by[row["locus"]]["token_glosses_de"]
            and row["target_meaning_de"] == TARGETS[row["surface"]][1]
            and row["syntax_note"] == "EXACT_TOKEN_ORDER_BASELINE__RESIDUALS_RETAINED"
            and not FILLER.search(row["tokenwise_v34_de"])
            for row in reality
        ),
        "reality-check source/meaning fidelity",
    )

    target_run = result.get("target_run", {})
    check(
        (
            target_run.get("candidates"), target_run.get("accepted_whole_cards"),
            target_run.get("reader_anchored_exact_wholes"), target_run.get("audited_occurrences"),
            target_run.get("target_lines"), target_run.get("target_pages"),
            target_run.get("all_reader_exact_occurrences"), target_run.get("split_normalized_occurrences"),
            target_run.get("reader_variant_warnings"), target_run.get("hard_collisions"),
        )
        == (20, 20, 18, 61, 61, 44, 52, 52, 9, 0),
        "result target metrics",
    )
    check(
        target_run.get("accepted_surfaces") == TARGET_ORDER
        and target_run.get("reader_warning_wholes") == sorted(UNSTABLE_TARGETS)
        and target_run.get("sections") == ["B", "H", "P", "S", "T"]
        and target_run.get("languages") == ["A", "B"]
        and target_run.get("hands") == ["1", "2", "3", "5"]
        and target_run.get("verdicts") == {"CONCRETE_CONTEXT_COMPATIBLE": 46, "READER_VARIANT_WARNING": 9, "SHORT_OR_OPAQUE_CONTEXT": 6},
        "result target packet",
    )
    check(
        result.get("coverage")
        == {
            "base": BASE_METRICS,
            "final": FINAL_METRICS,
            "newly_completed_lines": 0,
            "newly_exposed_one_hole_lines": 4,
            "affected_lines": 61,
            "new_one_hole_residuals": {locus: NEW_ONE_HOLES[locus][1] for locus in sorted(NEW_ONE_HOLES)},
        },
        "result coverage packet",
    )
    working = result.get("working_dictionary", {})
    check(
        (
            working.get("v33_entries"), working.get("v34_entries"), working.get("accepted_tail_entries"),
            working.get("v33_glossary_surfaces"), working.get("v34_glossary_surfaces"),
        )
        == (550, 570, 20, 471, 491),
        "result dictionary metrics",
    )
    check(
        working.get("v33_prefix_sha256") == canonical_hash(base_dictionary)
        and working.get("v34_sha256") == canonical_hash(dictionary),
        "result dictionary hashes",
    )
    ordered = result.get("ordered_model", {})
    check(
        ordered.get("order_contrasts") == 5
        and ordered.get("same_line_target_pairs") == 0
        and ordered.get("target_lines_with_simple_v33_al_sister") == 15
        and ordered.get("absent_core_holds") == list(ABSENT_HOLDS)
        and "CHO/CHEO/SHO/SHEO are bound preparation heads" in str(ordered.get("preparation_heads"))
        and "CHOKAL=CHO+KAL differs from OKCHAL=O+KCH+AL" in str(ordered.get("diagnostic"))
        and "CHKAL=CH+KAL differs from KCHAL=K+CHAL" in str(ordered.get("diagnostic")),
        "result ordered/nested model",
    )
    nonleak = result.get("nonleak_controls", {})
    check(nonleak.get("decks_overlap_do_not_sum") is True, "result nonleak non-additivity")
    result_control_map = {
        "direct_target_superforms": "DIRECT_TARGET_SUPERFORM_NONLEAK",
        "global_short_tail": "GLOBAL_SHORT_TAIL_NONLEAK",
        "family_frontier_all": "CH_SH_AL_FAMILY_FRONTIER_ALL",
        "family_frontier_open": "CH_SH_AL_FAMILY_FRONTIER_OPEN",
        "family_frontier_protected": "CH_SH_AL_FAMILY_FRONTIER_PROTECTED",
    }
    check(
        all(
            tuple(
                int(nonleak[key][field])
                for field in ("surface_types", "token_positions", "pages", "reader_exact_occurrences", "split_normalized_occurrences")
            )
            == control_expected[name]
            and nonleak[key]["control"] == name
            for key, name in result_control_map.items()
        ),
        "result five-deck nonleak packet",
    )
    claim = str(result.get("claim_boundary", "")).lower()
    check(
        all(
            term in claim
            for term in (
                "exploratory", "exact-whole", "twenty", "ordered/nested", "not plaintext", "choal", "qokchal",
                "substring", "absent cell", "free component", "phonetics", "language", "exact ingredient", "f1r", "new page", "image",
            )
        ),
        "result claim ceiling",
    )

    inputs = result.get("inputs", {})
    check(set(inputs) == INPUTS and all(not Path(path).is_absolute() and (ROOT / path).is_file() for path in inputs), "result input path set")
    for path, digest in inputs.items():
        check(sha256(ROOT / path) == digest, f"result input hash:{path}")
    outputs = result.get("outputs", {})
    expected_outputs = {str(BASE / "artifacts" / name) for name in BUILDER_OUTPUTS}
    check(set(outputs) == expected_outputs, "result output path set")
    for path, digest in outputs.items():
        check(sha256(ROOT / path) == digest, f"result output hash:{path}")

    report_text = REPORT.read_text(encoding="utf-8").lower()
    for needle in (
        "61 positionen", "52 positionen", "cho + kal", "o + kch + al", "ch + kal", "k + chal",
        "cheokal", "sheotal", "am gradanfang", "vier zeilen", "otam", "shedefam", "schos", "chokcheo",
        "vier unbekannte direkte superformen", "45 unbekannte typen", "sieben aus dem raster erwartete kernzellen",
    ):
        check(needle in report_text, f"report contains:{needle}")
    scan_paths = [ROOT / BASE / name for name in ("REPORT.md", "METHOD.md", "README.md", "artifacts/README.md", "artifacts/RESULT.json")]
    scan_paths.extend(sorted(ART.glob("*.tsv")))
    filler_hits = [str(path.relative_to(ROOT)) for path in scan_paths if FILLER.search(path.read_text(encoding="utf-8"))]
    check(not filler_hits, "no generic filler", repr(filler_hits))

    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    check(manifest.get("experiment_id") == "GDT657" and manifest.get("slug") == "multi_quality_al_shell_order", "manifest identity")
    check(manifest.get("status") == STATUS, "manifest status")
    check(manifest.get("sealed_data") == {"f84": "FORBIDDEN", "f84r": "FORBIDDEN"}, "manifest seals")
    check(
        manifest.get("commands")
        == {"run": f"python3 {BASE}/src/run.py", "validate": f"python3 {BASE}/src/validate.py"},
        "manifest commands",
    )
    check(
        manifest.get("validation") == {"artifact": str(BASE / "artifacts/VALIDATION.json"), "status": "PASS"},
        "manifest validation",
    )
    check({"GDT624", "GDT640", "GDT656"} <= set(manifest.get("dependencies", [])), "manifest dependency core")
    question, ceiling = str(manifest.get("question", "")).lower(), str(manifest.get("claim_ceiling", "")).lower()
    check(
        len(question) >= 80 and all(term in question for term in ("twenty", "multi-quality", "order", "nest")),
        "manifest question core",
    )
    check(
        len(ceiling) >= 120
        and all(term in ceiling for term in ("explor", "exact whole", "reader", "substring", "plaintext", "ingredient")),
        "manifest claim ceiling core",
    )
    manifest_inputs = {row.get("path"): row for row in manifest.get("inputs", [])}
    check(set(manifest_inputs) == set(inputs), "manifest/result inputs")
    for path, row in manifest_inputs.items():
        if path in inputs:
            check(row.get("sha256") == inputs[path] == sha256(ROOT / path) and bool(row.get("role")), f"manifest input seal:{path}")
    manifest_outputs = {row.get("path"): row for row in manifest.get("outputs", [])}
    required = {
        str(BASE / path)
        for path in (
            "METHOD.md", "README.md", "REPORT.md", "artifacts/README.md", "artifacts/RESULT.json",
            "artifacts/VALIDATION.json", "src/run.py", "src/validate.py", *[f"artifacts/{name}" for name in BUILDER_OUTPUTS],
        )
    }
    check(required <= set(manifest_outputs), "manifest core outputs")
    for path, row in manifest_outputs.items():
        target_path = ROOT / str(path)
        check(not Path(str(path)).is_absolute() and target_path.is_file() and bool(row.get("role")), f"manifest output path:{path}")
        if str(path) != str(BASE / "artifacts/VALIDATION.json") and target_path.is_file():
            check(row.get("sha256") == sha256(target_path), f"manifest output seal:{path}")

    # Only after the independent raw census, semantics, coverage, nonleak,
    # provenance, report and manifest checks do we import the implementation.
    try:
        builder = load_builder()
        with tempfile.TemporaryDirectory(prefix="gdt657_validate_") as temporary:
            replay = Path(temporary)
            builder.build(replay)
            check({path.name for path in replay.iterdir()} == set(REPLAY_OUTPUTS), "replay output set")
            for name in REPLAY_OUTPUTS:
                check((ART / name).read_bytes() == (replay / name).read_bytes(), f"byte replay:{name}")
    except Exception as exc:
        issues.append(f"builder replay: {type(exc).__name__}: {exc}")

    validation = {
        "schema": "GDT657_VALIDATION_V1",
        "experiment_id": "GDT657",
        "status": "PASS" if not issues else "FAIL",
        "checks_passed": len(passed),
        "checks_failed": len(issues),
        "passed": passed,
        "issues": issues,
    }
    VALIDATION.write_text(json.dumps(validation, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if issues:
        print(f"GDT657 validation FAIL: {len(issues)} issue(s), {len(passed)} checks passed")
        for issue in issues:
            print(f"- {issue}")
        return 1
    print(f"GDT657 validation PASS: {len(passed)} checks")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
