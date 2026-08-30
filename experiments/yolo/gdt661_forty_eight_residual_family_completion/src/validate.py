#!/usr/bin/env python3
"""Independent source-first release validator for GDT661.

The builder is never imported. Protected source counts are reconstructed with
the guarded selector before the builder is invoked for the final byte replay.
"""
from __future__ import annotations

import csv
import hashlib
import io
import json
import re
import subprocess
import sys
import tempfile
from collections import Counter, defaultdict
from pathlib import Path
from typing import Callable

sys.dont_write_bytecode = True


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
BASE = Path("experiments/yolo/gdt661_forty_eight_residual_family_completion")
ART = ROOT / BASE / "artifacts"
RUN = ROOT / BASE / "src/run.py"
G660 = Path("experiments/yolo/gdt660_seventeen_residual_concrete_completion")
G659 = Path("experiments/yolo/gdt659_naked_y_local_reference")
TOKENS = Path("transcription/voynich_zl3b_tokens.tsv")
CROSS = Path("transcription/voynich_cross_transcription_lines.tsv")

OUTPUT_NAMES = (
    "PAGE_ALLOWLIST.tsv", "TARGET_DECISION_DECK.tsv", "ACCEPTED_WHOLE_SURFACE_DEFAULTS.tsv",
    "CONTEXT_RENDERING_CARDS.tsv", "ALL_OCCURRENCE_SEMANTIC_AUDIT.tsv", "READER_VARIANT_AUDIT.tsv",
    "FAMILY_COMPOSITION_ATLAS.tsv", "FRONTIER_48_COMPLETIONS.tsv", "TARGET_LINE_TRANSLATIONS.tsv",
    "ROUND_COVERAGE_COUNTS.tsv", "NEWLY_COMPLETED_LINES.tsv", "NEWLY_EXPOSED_ONE_HOLE_LINES.tsv",
    "V38_WORKING_TOKEN_GLOSSARY.tsv", "WORKING_DICTIONARY_V38.tsv", "ALL_LINE_CONCRETE_COVERAGE_V38.tsv",
    "COMPLETE_PASSAGES_V38.tsv", "ONE_UNKNOWN_PASSAGES_V38.tsv",
)
TARGET_ORDER = (
    "dam", "ches", "chs", "lkeey", "okchol", "r", "ctholy", "ols", "dl", "ykchy",
    "kchar", "qokorar", "ychoy", "sheoy", "ytal", "sokaiin", "shes", "qekeochor",
    "okary", "shkair", "keor", "odan", "kodaiin", "cho", "chotol", "d", "qoteees",
    "alchey", "sheody", "oeeo", "dshor", "sain", "sokeedy", "am", "chckhd", "otalor",
    "olkain", "chty", "loldy", "olteedy", "cheeky", "lkeedy", "dalchedy", "saii",
    "ykeedy", "yteody", "tdain", "chakal",
)
TARGETS = frozenset(TARGET_ORDER)
CONTEXT_SURFACES = frozenset({"r", "d"})
LOW_SURFACES = frozenset({"qekeochor", "shkair", "oeeo", "qoteees", "saii", "tdain", "chakal"})
EXPECTED_COUNTS = {
    "dam": 68, "ches": 31, "chs": 13, "lkeey": 38, "okchol": 10, "r": 129,
    "ctholy": 4, "ols": 17, "dl": 18, "ykchy": 20, "kchar": 1, "qokorar": 1,
    "ychoy": 1, "sheoy": 3, "ytal": 12, "sokaiin": 1, "shes": 5, "qekeochor": 1,
    "okary": 8, "shkair": 2, "keor": 6, "odan": 2, "kodaiin": 2, "cho": 75,
    "chotol": 7, "d": 53, "qoteees": 2, "alchey": 4, "sheody": 34, "oeeo": 1,
    "dshor": 14, "sain": 60, "sokeedy": 2, "am": 67, "chckhd": 4, "otalor": 4,
    "olkain": 33, "chty": 12, "loldy": 2, "olteedy": 3, "cheeky": 23, "lkeedy": 37,
    "dalchedy": 5, "saii": 1, "ykeedy": 26, "yteody": 7, "tdain": 2, "chakal": 1,
}
EXPECTED_MEANINGS = {
    "dam": "Dosis I", "ches": "trockenes Drogenmaterial, Mittelstufe", "chs": "Trockengut, Grundform",
    "lkeey": "Drogenholz, heiß am Gradende", "okchol": "heißer Ansatz aus Trockengut", "r": "Wurzel",
    "ctholy": "Blatt-/Krautdroge, Grundform", "ols": "Drogenstoffposten", "dl": "Rohstoffmaß",
    "ykchy": "Eintrag/Bezug: heiß-trocken am Gradanfang", "kchar": "heiße Trockenfraktion I",
    "qokorar": "heiße Drogenportion, Fraktion I", "ychoy": "Eintrag/Bezug: Trockenansatz am Gradanfang",
    "sheoy": "feucht angesetzte Zubereitung am Gradanfang",
    "ytal": "Eintrag/Bezug: kalter Rohstoff I am Gradanfang", "sokaiin": "heißer Samenansatz, Grad III",
    "shes": "feuchtes Drogenmaterial, Mittelstufe", "qekeochor": "heiße trocken angesetzte Drogenportion",
    "okary": "heiße Ansatzfraktion I, abgeschlossen", "shkair": "heiße angefeuchtete Drogenfraktion II",
    "keor": "heiße Drogenportion", "odan": "Zubereitungsdosis I",
    "kodaiin": "erhitzte Zubereitung, Dosis III", "cho": "Trockenansatz",
    "chotol": "Trockenansatz aus kaltem Material", "d": "Dosis",
    "qoteees": "kalter Qualitätsendwert, abgeschlossen", "alchey": "Rohstoff I, trocken in der Gradmitte",
    "sheody": "angefeuchteter Ansatz, abgeschlossen", "oeeo": "zweiter Mazerationsansatz",
    "dshor": "abgemessene Blüten-/Fruchtdroge", "sain": "Saatgut, Typ/Charge II",
    "sokeedy": "heißer Samenansatz am Gradende, fertig", "am": "Maßeinheit I",
    "chckhd": "trockenes Arzneikompositum, abgeschlossen",
    "otalor": "kalte Ansatzportion aus Rohstoff I", "olkain": "heißes Drogenmaterial, Grad II",
    "chty": "trocken-kalt am Gradanfang", "loldy": "Drogenholzstoff, fertig aufbereitet",
    "olteedy": "kaltes Drogenmaterial am Gradende, fertig",
    "cheeky": "trocken am Gradende, dann heiß am Gradanfang",
    "lkeedy": "Drogenholz, heiß am Gradende, abgeschlossen",
    "dalchedy": "abgemessener Rohstoff I, trocken in der Gradmitte, abgeschlossen",
    "saii": "Saatgutmenge III", "ykeedy": "Eintrag/Bezug: heiß am Gradende, abgeschlossen",
    "yteody": "Eintrag/Bezug: kalte Zubereitung, abgeschlossen", "tdain": "kalter Grad-/Maßwert II",
    "chakal": "Rohstoff I, trocken-heiß am Gradanfang",
}
EXPECTED_RENDER_CLASSES = {
    "AM_BODY": 13, "AM_LABEL": 1, "AM_TERMINAL": 53,
    "CHO_BODY": 69, "CHO_HEAD": 2, "CHO_TERMINAL": 4,
    "DAM_BODY": 24, "DAM_LABEL": 1, "DAM_TERMINAL": 43,
    "D_BEFORE_VALUE": 8, "D_BODY": 28, "D_LABEL": 6, "D_TERMINAL": 11,
    "EXACT_WHOLE": 414,
    "R_BEFORE_VALUE": 33, "R_BODY": 90, "R_HEAD": 1, "R_LABEL": 5,
    "Y_WHOLE_ENTRY": 13, "Y_WHOLE_REFERENCE": 53,
}
EXPECTED_SURFACE_STATS = {
    "dam": (68, 67, 52, 37, 37), "ches": (31, 31, 26, 28, 28),
    "chs": (13, 13, 10, 11, 11), "lkeey": (38, 37, 19, 34, 34),
    "okchol": (10, 9, 8, 9, 9), "r": (129, 127, 74, 57, 57),
    "ctholy": (4, 4, 4, 4, 4), "ols": (17, 17, 16, 12, 12),
    "dl": (18, 17, 15, 13, 13), "ykchy": (20, 20, 17, 15, 15),
    "kchar": (1, 1, 1, 1, 1), "qokorar": (1, 1, 1, 1, 1),
    "ychoy": (1, 1, 1, 1, 1), "sheoy": (3, 3, 3, 1, 1),
    "ytal": (12, 12, 10, 12, 12), "sokaiin": (1, 1, 1, 1, 1),
    "shes": (5, 5, 5, 2, 2), "qekeochor": (1, 1, 1, 1, 1),
    "okary": (8, 8, 8, 5, 5), "shkair": (2, 2, 2, 1, 1),
    "keor": (6, 6, 6, 5, 5), "odan": (2, 2, 2, 2, 2),
    "kodaiin": (2, 2, 2, 2, 2), "cho": (75, 75, 51, 45, 45),
    "chotol": (7, 7, 7, 5, 5), "d": (53, 50, 34, 20, 20),
    "qoteees": (2, 2, 2, 2, 2), "alchey": (4, 4, 4, 2, 2),
    "sheody": (34, 34, 26, 24, 26), "oeeo": (1, 1, 1, 1, 1),
    "dshor": (14, 13, 12, 12, 12), "sain": (60, 60, 33, 53, 53),
    "sokeedy": (2, 2, 2, 1, 1), "am": (67, 67, 39, 53, 53),
    "chckhd": (4, 4, 4, 2, 2), "otalor": (4, 4, 4, 4, 4),
    "olkain": (33, 32, 15, 30, 30), "chty": (12, 12, 12, 12, 12),
    "loldy": (2, 2, 2, 2, 2), "olteedy": (3, 3, 3, 2, 2),
    "cheeky": (23, 23, 22, 22, 22), "lkeedy": (37, 35, 21, 23, 23),
    "dalchedy": (5, 5, 4, 4, 4), "saii": (1, 1, 1, 0, 0),
    "ykeedy": (26, 26, 24, 19, 19), "yteody": (7, 7, 5, 7, 7),
    "tdain": (2, 2, 2, 0, 0), "chakal": (1, 1, 1, 0, 0),
}
EXPECTED_CONTEXT_CARDS = {
    ("am", "AM_BODY"): (13, "Maßeinheit I"),
    ("am", "AM_LABEL"): (1, "[Maßeinheit-I-Zeichen]"),
    ("am", "AM_TERMINAL"): (53, "Maßeinheit I."),
    ("cho", "CHO_BODY"): (69, "Trockenansatz"),
    ("cho", "CHO_HEAD"): (2, "Trockenansatz:"),
    ("cho", "CHO_TERMINAL"): (4, "Trockenansatz"),
    ("dam", "DAM_BODY"): (24, "Dosis I"),
    ("dam", "DAM_LABEL"): (1, "[Dosis-I-Zeichen]"),
    ("dam", "DAM_TERMINAL"): (43, "Dosis I."),
    ("d", "D_BEFORE_VALUE"): (8, "davon/Dosis:"),
    ("d", "D_BODY"): (28, "Dosis"),
    ("d", "D_LABEL"): (6, "[Dosiszeichen]"),
    ("d", "D_TERMINAL"): (11, "Dosisvermerk."),
    ("r", "R_BEFORE_VALUE"): (33, "Wurzel:"),
    ("r", "R_BODY"): (90, "Wurzel"),
    ("r", "R_HEAD"): (1, "Wurzel:"),
    ("r", "R_LABEL"): (5, "[Wurzelzeichen]"),
    ("ychoy", "Y_WHOLE_ENTRY"): (1, "Eintrag: Trockenansatz am Gradanfang"),
    ("ykchy", "Y_WHOLE_ENTRY"): (4, "Eintrag: heiß-trocken am Gradanfang"),
    ("ykeedy", "Y_WHOLE_ENTRY"): (4, "Eintrag: heiß am Gradende, abgeschlossen"),
    ("ytal", "Y_WHOLE_ENTRY"): (1, "Eintrag: kalter Rohstoff I am Gradanfang"),
    ("yteody", "Y_WHOLE_ENTRY"): (3, "Eintrag: kalte Zubereitung, abgeschlossen"),
    ("ykchy", "Y_WHOLE_REFERENCE"): (16, "hierzu: heiß-trocken am Gradanfang"),
    ("ykeedy", "Y_WHOLE_REFERENCE"): (22, "hierzu: heiß am Gradende, abgeschlossen"),
    ("ytal", "Y_WHOLE_REFERENCE"): (11, "hierzu: kalter Rohstoff I am Gradanfang"),
    ("yteody", "Y_WHOLE_REFERENCE"): (4, "hierzu: kalte Zubereitung, abgeschlossen"),
}
BASE_METRICS = {
    "physical_lines": 4128, "known_token_positions": 17579, "unknown_token_positions": 14760,
    "complete_multi_token_lines": 172, "strict_complete_lines": 83,
    "one_unknown_lines": 273, "strict_one_unknown_lines": 68, "working_glossary_surfaces": 510,
}
FINAL_METRICS = {
    "physical_lines": 4128, "known_token_positions": 18451, "unknown_token_positions": 13888,
    "complete_multi_token_lines": 233, "strict_complete_lines": 99,
    "one_unknown_lines": 290, "strict_one_unknown_lines": 73, "working_glossary_surfaces": 556,
}
VALUE_FORMS = frozenset({"n", "in", "iin", "iiin", "ain", "aiin", "aiiin"})
Y_SURFACES = frozenset({"ykchy", "ychoy", "ytal", "ykeedy", "yteody"})
FILLER = re.compile(
    r"arbeitsgut|arbeitsvorgang|arbeitschritt|arbeitsschritt|arbeitsmittel|arbeitsstoff|"
    r"\b(?:vorgang|prozess|tätigkeit|operation)\b|führe\s+.*\s+aus|leite\s+.*\s+weiter",
    re.I,
)
OPEN = re.compile(r"\[[^\]]+:\?\]")


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_hash(value: object) -> str:
    raw = json.dumps(value, sort_keys=True, ensure_ascii=True, separators=(",", ":")).encode()
    return hashlib.sha256(raw).hexdigest()


def split_pipe(value: str) -> list[str]:
    return value.split(" | ") if value else []


def split_compact(value: str) -> list[str]:
    return [] if value in {"", "NONE"} else value.split("|")


def guarded_query(path: Path, pages: set[str], columns: str) -> tuple[list[dict[str, str]], dict[str, int]]:
    command = [str(ROOT / "vmanus-exp"), "query-tsv", str(path), "--selector", "page"]
    for page in sorted(pages):
        command.extend(("--allow", page))
    command.extend(("--columns", columns))
    for prefix in ("f1r", "f84", "f84r"):
        command.extend(("--forbid-prefix", prefix))
    done = subprocess.run(command, cwd=ROOT, text=True, capture_output=True, check=False)
    stats_lines = [line for line in done.stderr.splitlines() if line.startswith("GUARD_STATS ")]
    if done.returncode or len(stats_lines) != 1:
        raise RuntimeError(done.stderr or "guarded query failed")
    rows = list(csv.DictReader(io.StringIO(done.stdout), delimiter="\t"))
    stats = {key: int(value) for key, value in json.loads(stats_lines[0][12:]).items()}
    if stats.get("selected") != len(rows):
        raise RuntimeError("guard stats disagree with materialized rows")
    if any(row.get("page") == "f1r" or row.get("page", "").startswith("f84") for row in rows):
        raise RuntimeError("forbidden page escaped guarded query")
    return rows, stats


def span_count(words: list[str], target: str) -> int:
    total = 0
    for start in range(len(words)):
        joined = ""
        for word in words[start:]:
            joined += word
            if joined == target:
                total += 1
                break
            if len(joined) >= len(target) or not target.startswith(joined):
                break
    return total


def position(ordinal: int, length: int) -> str:
    if length == 1:
        return "ONLY"
    if ordinal == 1:
        return "BOS"
    if ordinal == length:
        return "EOS"
    return "MEDIAL"


def render_class(surface: str, pos: str, kind: str, right: str) -> str:
    if surface == "r":
        if kind == "L" or pos == "ONLY":
            return "R_LABEL"
        if right in VALUE_FORMS:
            return "R_BEFORE_VALUE"
        return "R_HEAD" if pos == "BOS" else "R_BODY"
    if surface == "d":
        if kind == "L":
            return "D_LABEL"
        if right in VALUE_FORMS:
            return "D_BEFORE_VALUE"
        return "D_TERMINAL" if pos in {"EOS", "ONLY"} else "D_BODY"
    if surface == "cho":
        return "CHO_HEAD" if pos == "BOS" else "CHO_TERMINAL" if pos == "EOS" else "CHO_BODY"
    if surface in {"am", "dam"}:
        if kind == "L":
            return surface.upper() + "_LABEL"
        return surface.upper() + ("_TERMINAL" if pos in {"EOS", "ONLY"} else "_BODY")
    if surface in Y_SURFACES:
        return "Y_WHOLE_ENTRY" if pos == "BOS" else "Y_WHOLE_REFERENCE"
    return "EXACT_WHOLE"


def source_records(
    tokens: list[dict[str, str]], cross_rows: list[dict[str, str]],
) -> tuple[list[dict[str, object]], dict[str, list[dict[str, str]]]]:
    cross = {row["locus"]: row for row in cross_rows}
    by_line: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in tokens:
        by_line[row["locus"]].append(row)
    for line in by_line.values():
        line.sort(key=lambda item: int(item["token_index"]))
    records: list[dict[str, object]] = []
    for surface in TARGET_ORDER:
        members = [row for row in tokens if row["eva"] == surface]
        members.sort(key=lambda item: (item["page"], item["locus"], int(item["token_index"])))
        seen: Counter[str] = Counter()
        for token in members:
            locus = token["locus"]
            seen[locus] += 1
            line = by_line[locus]
            index = next(i for i, row in enumerate(line) if int(row["token_index"]) == int(token["token_index"]))
            words = [row["eva"] for row in line]
            pos = position(index + 1, len(line))
            left = words[index - 1] if index else "<BOS>"
            right = words[index + 1] if index + 1 < len(line) else "<EOS>"
            readers = [cross[locus][field].split() for field in ("zl3b_clean", "it2a_clean", "rf1b_clean")]
            direct_caps = [reader.count(surface) for reader in readers]
            span_caps = [span_count(reader, surface) for reader in readers]
            records.append({
                "page": token["page"], "locus": locus, "token_index": int(token["token_index"]),
                "ordinal": index + 1, "surface": surface, "kind": token["kind"], "position": pos,
                "left": left, "right": right, "rendering_class": render_class(surface, pos, token["kind"], right),
                "reader_exact": int(seen[locus] <= min(direct_caps)),
                "split_normalized": int(seen[locus] <= min(span_caps)),
                "all_present_exact": cross[locus]["all_present_exact"],
                "zl3b_line": cross[locus]["zl3b_clean"], "it2a_line": cross[locus]["it2a_clean"],
                "rf1b_line": cross[locus]["rf1b_clean"],
            })
    return records, by_line


def metric_rows(coverage, complete, one, glossary) -> dict[str, int]:
    return {
        "physical_lines": len(coverage),
        "known_token_positions": sum(int(row["known_tokens"]) for row in coverage),
        "unknown_token_positions": sum(int(row["unknown_tokens"]) for row in coverage),
        "complete_multi_token_lines": len(complete),
        "strict_complete_lines": sum(int(row["strict_complete"]) for row in complete),
        "one_unknown_lines": len(one),
        "strict_one_unknown_lines": sum(int(row["strict_eligible"]) for row in one),
        "working_glossary_surfaces": len(glossary),
    }


def main() -> int:
    checks: list[str] = []
    failures: list[str] = []

    def check(name: str, condition: bool) -> None:
        checks.append(name)
        if not condition:
            failures.append(name)

    inherited_allow = ROOT / G660 / "artifacts/PAGE_ALLOWLIST.tsv"
    pages_rows = read_tsv(inherited_allow)
    pages = {row["page"] for row in pages_rows}
    check("allowlist_179", len(pages) == 179 and len(pages_rows) == 179)
    check("allowlist_excludes_f1r_f84", "f1r" not in pages and not any(page.startswith("f84") for page in pages))
    check("allowlist_inherited_bytes", (ART / "PAGE_ALLOWLIST.tsv").read_bytes() == inherited_allow.read_bytes())
    tokens, token_stats = guarded_query(TOKENS, pages, "page,locus,token_index,eva,kind,section,language,hand")
    cross, cross_stats = guarded_query(
        CROSS, pages, "page,locus,all_three_present,all_present_exact,zl3b_clean,it2a_clean,rf1b_clean"
    )
    check("guarded_token_census", len(tokens) == 32339)
    check("guarded_cross_census", len(cross) == 4137)
    check("guard_stats_selected", token_stats.get("selected") == 32339 and cross_stats.get("selected") == 4137)
    records, by_line = source_records(tokens, cross)
    cross_by_locus = {row["locus"]: row for row in cross}
    check("cross_unique_loci", len(cross_by_locus) == 4137)
    check("source_physical_lines", len(by_line) == 4128)
    check("source_zl_lines_match_cross", all(
        locus in cross_by_locus and " ".join(row["eva"] for row in line) == cross_by_locus[locus]["zl3b_clean"]
        for locus, line in by_line.items()
    ))
    check("source_target_positions", len(records) == 872)
    check("source_surface_counts", dict(Counter(str(row["surface"]) for row in records)) == EXPECTED_COUNTS)
    check("source_affected_lines", len({str(row["locus"]) for row in records}) == 786)
    check("source_affected_pages", len({str(row["page"]) for row in records}) == 168)
    check("source_reader_exact", sum(int(row["reader_exact"]) for row in records) == 600)
    check("source_split_normalized", sum(int(row["split_normalized"]) for row in records) == 602)
    actual_surface_stats = {}
    for surface in TARGET_ORDER:
        members = [row for row in records if row["surface"] == surface]
        actual_surface_stats[surface] = (
            len(members), len({row["locus"] for row in members}), len({row["page"] for row in members}),
            sum(int(row["reader_exact"]) for row in members), sum(int(row["split_normalized"]) for row in members),
        )
    check("source_per_surface_stats", actual_surface_stats == EXPECTED_SURFACE_STATS)
    check("source_render_classes", dict(Counter(str(row["rendering_class"]) for row in records)) == EXPECTED_RENDER_CLASSES)
    check("source_r_kinds", Counter(str(row["kind"]) for row in records if row["surface"] == "r") == {"P": 124, "L": 5})
    check("source_d_kinds", Counter(str(row["kind"]) for row in records if row["surface"] == "d") == {"P": 47, "L": 6})

    decision = read_tsv(ART / "TARGET_DECISION_DECK.tsv")
    accepted = read_tsv(ART / "ACCEPTED_WHOLE_SURFACE_DEFAULTS.tsv")
    context_cards = read_tsv(ART / "CONTEXT_RENDERING_CARDS.tsv")
    audit = read_tsv(ART / "ALL_OCCURRENCE_SEMANTIC_AUDIT.tsv")
    reader = read_tsv(ART / "READER_VARIANT_AUDIT.tsv")
    family = read_tsv(ART / "FAMILY_COMPOSITION_ATLAS.tsv")
    frontier = read_tsv(ART / "FRONTIER_48_COMPLETIONS.tsv")
    target_lines = read_tsv(ART / "TARGET_LINE_TRANSLATIONS.tsv")
    rounds = read_tsv(ART / "ROUND_COVERAGE_COUNTS.tsv")
    new_complete = read_tsv(ART / "NEWLY_COMPLETED_LINES.tsv")
    new_one = read_tsv(ART / "NEWLY_EXPOSED_ONE_HOLE_LINES.tsv")
    glossary = read_tsv(ART / "V38_WORKING_TOKEN_GLOSSARY.tsv")
    dictionary = read_tsv(ART / "WORKING_DICTIONARY_V38.tsv")
    coverage = read_tsv(ART / "ALL_LINE_CONCRETE_COVERAGE_V38.tsv")
    complete = read_tsv(ART / "COMPLETE_PASSAGES_V38.tsv")
    one = read_tsv(ART / "ONE_UNKNOWN_PASSAGES_V38.tsv")
    base_glossary = read_tsv(ROOT / G660 / "artifacts/V37_WORKING_TOKEN_GLOSSARY.tsv")
    base_dictionary = read_tsv(ROOT / G660 / "artifacts/WORKING_DICTIONARY_V37.tsv")
    base_coverage = read_tsv(ROOT / G660 / "artifacts/ALL_LINE_CONCRETE_COVERAGE_V37.tsv")
    base_complete = read_tsv(ROOT / G660 / "artifacts/COMPLETE_PASSAGES_V37.tsv")
    base_one = read_tsv(ROOT / G660 / "artifacts/ONE_UNKNOWN_PASSAGES_V37.tsv")
    source_frontier = read_tsv(ROOT / G660 / "artifacts/NEWLY_EXPOSED_ONE_HOLE_LINES.tsv")

    check("decision_48_order", len(decision) == 48 and tuple(row["surface"] for row in decision) == TARGET_ORDER)
    check("decision_counts", {row["surface"]: int(row["occurrences"]) for row in decision} == EXPECTED_COUNTS)
    check("decision_meanings", {row["surface"]: row["working_default_de"] for row in decision} == EXPECTED_MEANINGS)
    check("decision_context_status", all(
        (row["surface"] in CONTEXT_SURFACES) == (row["status"] == "ACCEPT_V38_CONTEXT_SCOPED_NOT_GLOBAL_LEXEME")
        for row in decision
    ))
    check("decision_low_set", {row["surface"] for row in decision if row["strength"] == "LOW_EXPLORATORY"} == LOW_SURFACES)
    check("accepted_46", len(accepted) == 46 and {row["surface"] for row in accepted} == TARGETS - CONTEXT_SURFACES)
    check("accepted_meanings", all(row["working_meaning_de"] == EXPECTED_MEANINGS[row["surface"]] for row in accepted))
    check("accepted_exact_scope", all(row["scope"] == "EXACT_WHITESPACE_DELIMITED_WHOLE" for row in accepted))
    check("context_cards_26", len(context_cards) == 26)
    check("context_card_ids", [row["card_id"] for row in context_cards] == [f"G661-C{i:02d}" for i in range(1, 27)])
    check("context_card_counts", sum(int(row["occurrences"]) for row in context_cards) == 458)
    check("context_card_exact_map", {
        (row["surfaces"], row["rendering_class"]): (int(row["occurrences"]), row["working_render_de"])
        for row in context_cards
    } == EXPECTED_CONTEXT_CARDS)
    check("context_r_d_scoped", all(
        row["semantic_effect"] == "occurrence-scoped lexical card"
        for row in context_cards if row["surfaces"] in CONTEXT_SURFACES
    ))
    check("context_labels", {
        (row["surfaces"], row["rendering_class"], int(row["occurrences"]))
        for row in context_cards if row["rendering_class"].endswith("_LABEL")
    } == {("am", "AM_LABEL", 1), ("dam", "DAM_LABEL", 1), ("d", "D_LABEL", 6), ("r", "R_LABEL", 5)})

    check("audit_872", len(audit) == 872)
    check("audit_unique_positions", len({(row["locus"], row["token_index"]) for row in audit}) == 872)
    check("audit_counts", dict(Counter(row["surface"] for row in audit)) == EXPECTED_COUNTS)
    check("audit_v37_open", all(row["v37_gloss_de"] == f"[{row['surface']}:?]" for row in audit))
    check("audit_v38_concrete", all(not OPEN.search(row["v38_gloss_de"]) and not FILLER.search(row["v38_gloss_de"]) for row in audit))
    check("audit_context_dispatch", all(
        int(row["context_surface_dispatch"]) == int(row["surface"] in CONTEXT_SURFACES)
        and int(row["exact_surface_dispatch"]) == int(row["surface"] not in CONTEXT_SURFACES)
        and int(row["substring_dispatch"]) == 0 for row in audit
    ))
    source_by_key = {(str(row["locus"]), int(row["token_index"])): row for row in records}
    audit_full_match = True
    for row in audit:
        key = (row["locus"], int(row["token_index"]))
        source = source_by_key.get(key)
        if source is None:
            audit_full_match = False
            break
        expected_gloss = EXPECTED_MEANINGS[row["surface"]]
        if row["rendering_class"] == "R_LABEL":
            expected_gloss = "[Wurzelzeichen]"
        elif row["rendering_class"] == "D_LABEL":
            expected_gloss = "[Dosis-/Maßzeichen]"
        expected_state = (
            "KNOWN_CONTEXT_LICENSED" if row["surface"] in CONTEXT_SURFACES else "KNOWN_EXACT_WHOLE"
        ) if int(source["reader_exact"]) else "READER_BOUNDARY_UNSTABLE"
        audit_full_match &= all((
            row["page"] == source["page"], int(row["ordinal"]) == int(source["ordinal"]),
            row["surface"] == source["surface"], row["token_kind"] == source["kind"],
            row["position"] == source["position"], row["left_surface"] == source["left"],
            row["right_surface"] == source["right"], row["rendering_class"] == source["rendering_class"],
            int(row["reader_exact"]) == int(source["reader_exact"]),
            int(row["split_normalized"]) == int(source["split_normalized"]),
            row["all_present_exact"] == source["all_present_exact"],
            row["zl3b_line"] == source["zl3b_line"], row["it2a_line"] == source["it2a_line"],
            row["rf1b_line"] == source["rf1b_line"], row["v38_gloss_de"] == expected_gloss,
            row["v38_scope_state"] == expected_state,
        ))
    check("audit_full_source_match", audit_full_match and len(source_by_key) == len(audit))
    check("reader_872", len(reader) == 872 and len({row["occurrence_id"] for row in reader}) == 872)
    check("reader_totals", sum(int(row["reader_exact"]) for row in reader) == 600 and sum(int(row["split_normalized"]) for row in reader) == 602)
    check("family_all_targets", {row["surface"] for row in family if row["role"] == "TARGET"} == TARGETS)
    check("family_no_substring_claim", all("does not license substring" in row["claim_scope"] for row in family))

    check("frontier_48_order", len(frontier) == 48 and tuple(row["surface"] for row in frontier) == TARGET_ORDER)
    check("frontier_source_loci", [row["locus"] for row in frontier] == [row["locus"] for row in source_frontier])
    check("frontier_meanings", all(row["working_default_de"] == EXPECTED_MEANINGS[row["surface"]] for row in frontier))
    check("frontier_no_open_holes", all(not OPEN.search(row["v38_translation_de"]) for row in frontier))
    check("frontier_no_filler", all(not FILLER.search(row["v38_translation_de"]) for row in frontier))
    check("frontier_low_marked", {row["surface"] for row in frontier if row["strength"] == "LOW_EXPLORATORY"} == LOW_SURFACES)
    check("target_lines_786", len(target_lines) == 786 and sum(int(row["target_occurrences"]) for row in target_lines) == 872)
    check("target_line_no_filler", all(not FILLER.search(row["v38_working_translation_de"]) for row in target_lines))
    target_line_map = {row["locus"]: row["v38_working_translation_de"] for row in target_lines}
    check("repeated_dam_position_render", target_line_map["f23v.8"].endswith("Dosis I.") and "; Dosis I;" in target_line_map["f23v.8"])
    check("repeated_d_position_render", target_line_map["f35v.12"].count("davon/Dosis:") == 2)
    check("mixed_d_position_render", all(
        text.count("davon/Dosis:") == 1 and text.count("Dosisvermerk.") == 1 and "Dosis:vermerk" not in text
        for text in (target_line_map["f38v.1"], target_line_map["f38v.4"])
    ))
    check("repeated_r_position_render", "Wurzel; Rohstoffklasse I; Wurzel: Menge III" in target_line_map["f76v.38"])

    base_by_locus = {row["locus"]: row for row in base_coverage}
    final_by_locus = {row["locus"]: row for row in coverage}
    check("coverage_loci_preserved", set(base_by_locus) == set(final_by_locus) and len(final_by_locus) == 4128)
    source_target_keys = {(str(row["locus"]), int(row["ordinal"])) for row in records}
    target_changes = 0
    non_target_same = True
    unknown_arithmetic = True
    unknown_lists_exact = True
    for locus, before in base_by_locus.items():
        after = final_by_locus[locus]
        b_gloss, a_gloss = split_pipe(before["token_glosses_de"]), split_pipe(after["token_glosses_de"])
        b_sources, a_sources = split_pipe(before["gloss_sources"]), split_pipe(after["gloss_sources"])
        b_states, a_states = split_pipe(before["scope_states"]), split_pipe(after["scope_states"])
        local = 0
        for ordinal in range(1, len(b_gloss) + 1):
            if (locus, ordinal) in source_target_keys:
                local += 1
                target_changes += 1
                if b_gloss[ordinal - 1] == a_gloss[ordinal - 1]:
                    non_target_same = False
            elif (b_gloss[ordinal - 1], b_sources[ordinal - 1], b_states[ordinal - 1]) != (a_gloss[ordinal - 1], a_sources[ordinal - 1], a_states[ordinal - 1]):
                non_target_same = False
        unknown_arithmetic &= int(after["known_tokens"]) == int(before["known_tokens"]) + local
        unknown_arithmetic &= int(after["unknown_tokens"]) == int(before["unknown_tokens"]) - local
        before_pairs = list(zip(split_compact(before["unknown_ordinals"]), split_compact(before["unknown_surfaces"])))
        expected_pairs = [pair for pair in before_pairs if (locus, int(pair[0])) not in source_target_keys]
        after_pairs = list(zip(split_compact(after["unknown_ordinals"]), split_compact(after["unknown_surfaces"])))
        unknown_lists_exact &= after_pairs == expected_pairs
    check("coverage_target_changes_872", target_changes == 872)
    check("coverage_non_target_projection_same", non_target_same)
    check("coverage_unknown_arithmetic", unknown_arithmetic)
    check("coverage_unknown_lists_exact", unknown_lists_exact)
    check("coverage_metrics", metric_rows(coverage, complete, one, glossary) == FINAL_METRICS)
    check("base_metrics", metric_rows(base_coverage, base_complete, base_one, base_glossary) == BASE_METRICS)
    check("new_complete_61", len(new_complete) == 61 and {row["locus"] for row in new_complete} == {row["locus"] for row in complete} - {row["locus"] for row in base_complete})
    check("new_one_78", len(new_one) == 78 and {row["locus"] for row in new_one} == {row["locus"] for row in one} - {row["locus"] for row in base_one})
    derived_complete = {
        row["locus"]: int(int(row["ambiguous_tokens"]) == 0 and int(row["reader_unstable_tokens"]) == 0 and int(row["all_present_exact"]) == 1)
        for row in coverage if int(row["unknown_tokens"]) == 0 and int(row["token_count"]) >= 2
    }
    derived_one = {
        row["locus"]: int(int(row["ambiguous_tokens"]) == 0 and int(row["reader_unstable_tokens"]) == 0 and int(row["all_present_exact"]) == 1)
        for row in coverage if int(row["unknown_tokens"]) == 1 and int(row["known_tokens"]) >= 1
    }
    check("complete_derived_from_coverage", {row["locus"]: int(row["strict_complete"]) for row in complete} == derived_complete)
    check("one_derived_from_coverage", {row["locus"]: int(row["strict_eligible"]) for row in one} == derived_one)
    check("complete_no_open", all(not OPEN.search(row["working_translation_de"]) for row in complete))

    check("glossary_556_unique", len(glossary) == 556 and len({row["surface"] for row in glossary}) == 556)
    base_glossary_map = {row["surface"]: row for row in base_glossary}
    glossary_map = {row["surface"]: row for row in glossary}
    check("glossary_base_unchanged", all(glossary_map.get(surface) == row for surface, row in base_glossary_map.items()))
    check("glossary_46_new", set(glossary_map) - set(base_glossary_map) == TARGETS - CONTEXT_SURFACES)
    check("glossary_no_global_r_d", not (CONTEXT_SURFACES & set(glossary_map)))
    check("glossary_new_meanings", all(glossary_map[surface]["working_meaning_de"] == EXPECTED_MEANINGS[surface] for surface in TARGETS - CONTEXT_SURFACES))
    check("dictionary_678", len(dictionary) == 678)
    check("dictionary_base_prefix", dictionary[:606] == base_dictionary)
    added_dictionary = dictionary[606:]
    check("dictionary_46_wholes", sum(row["kind"] == "EXACT_WHOLE_SURFACE_CARD" for row in added_dictionary) == 46)
    check("dictionary_26_renderers", sum(row["kind"] == "EXACT_WHOLE_RENDERING_CARD" for row in added_dictionary) == 26)
    check("dictionary_exact_entry_set", {
        row["entry"] for row in added_dictionary if row["kind"] == "EXACT_WHOLE_SURFACE_CARD"
    } == {f"{surface}@GDT661_EXACT_WHOLE" for surface in TARGETS - CONTEXT_SURFACES})
    check("dictionary_no_global_r_d", not any(
        row["kind"] == "EXACT_WHOLE_SURFACE_CARD" and row["entry"].split("@", 1)[0] in CONTEXT_SURFACES
        for row in added_dictionary
    ))
    check("round_two_rows", len(rounds) == 2 and [row["version"] for row in rounds] == ["V37", "V38"])
    round_metrics = [{key: int(row[key]) for key in FINAL_METRICS} for row in rounds]
    check("round_base_metrics", round_metrics[0] == BASE_METRICS)
    check("round_final_metrics", round_metrics[1] == FINAL_METRICS)

    result = json.loads((ART / "RESULT.json").read_text(encoding="utf-8"))
    check("result_status", result.get("status") == "PASS_872_TARGET_POSITIONS__V38")
    check("result_content_hash", result.get("content_sha256") == canonical_hash({k: v for k, v in result.items() if k != "content_sha256"}))
    check("result_target_dimensions", all((
        result["targets"]["surface_types"] == 48,
        result["targets"]["exact_whole_surfaces"] == 46,
        result["targets"]["context_scoped_surfaces"] == 2,
        result["targets"]["positions"] == 872,
        result["targets"]["lines"] == 786,
        result["targets"]["pages"] == 168,
        result["targets"]["reader_exact_positions"] == 600,
        result["targets"]["split_normalized_positions"] == 602,
    )))
    check("result_surface_counts", result["targets"]["surface_counts"] == EXPECTED_COUNTS)
    check("result_render_classes", result["targets"]["rendering_classes"] == EXPECTED_RENDER_CLASSES)
    check("result_final_metrics", result["coverage"]["final"] == FINAL_METRICS)
    check("result_delta_counts", result["coverage"]["newly_completed_lines"] == 61 and result["coverage"]["newly_exposed_one_hole_lines"] == 78)
    check("result_non_target_hash", result["coverage"]["non_target_before_sha256"] == result["coverage"]["non_target_after_sha256"])
    check("result_dictionary", result["working_dictionary"] == {
        "v37_entries": 606, "v38_entries": 678, "added_exact_whole_entries": 46,
        "added_rendering_entries": 26, "v37_glossary_surfaces": 510, "v38_glossary_surfaces": 556,
    })
    check("result_frontier", result["frontier"] == {"source_rows": 48, "completed_rows": 48, "unfilled_target_slots": 0})
    output_hashes = result.get("outputs", {})
    check("result_output_hash_keys", set(output_hashes) == {str(BASE / "artifacts" / name) for name in OUTPUT_NAMES})
    check("result_output_hashes", all(output_hashes.get(str(BASE / "artifacts" / name)) == sha256(ART / name) for name in OUTPUT_NAMES))
    input_hashes = result.get("inputs", {})
    check("result_input_hashes", bool(input_hashes) and all((ROOT / path).is_file() and sha256(ROOT / path) == digest for path, digest in input_hashes.items()))
    check("claim_boundary_no_plaintext_claim", "No glyph identity" in result["claim_boundary"] and "not substring dispatch" in result["claim_boundary"])

    replay_ok = True
    replay_error = ""
    with tempfile.TemporaryDirectory(prefix="gdt661_validator_replay_") as directory:
        replay_dir = Path(directory)
        done = subprocess.run(
            [sys.executable, str(RUN), "--artifact-dir", str(replay_dir)],
            cwd=ROOT, text=True, capture_output=True, check=False,
        )
        if done.returncode:
            replay_ok = False
            replay_error = done.stderr or done.stdout
        else:
            for name in (*OUTPUT_NAMES, "RESULT.json"):
                if not (replay_dir / name).is_file() or (ART / name).read_bytes() != (replay_dir / name).read_bytes():
                    replay_ok = False
                    replay_error = f"byte replay mismatch: {name}"
                    break
    check("tempdir_byte_replay", replay_ok)

    status = f"PASS_{len(checks)}_INDEPENDENT_CHECKS" if not failures else f"FAIL_{len(failures)}_OF_{len(checks)}_CHECKS"
    validation = {
        "schema": "GDT661_INDEPENDENT_VALIDATION_V1", "experiment_id": "GDT661", "status": status,
        "checks_run": len(checks), "checks_passed": len(checks) - len(failures),
        "failures": failures, "replay_error": replay_error,
        "source_census": {
            "allowed_pages": len(pages), "tokens": len(tokens), "cross_rows": len(cross),
            "target_positions": len(records), "target_lines": len({row["locus"] for row in records}),
            "target_pages": len({row["page"] for row in records}),
            "reader_exact": sum(int(row["reader_exact"]) for row in records),
            "split_normalized": sum(int(row["split_normalized"]) for row in records),
            "token_guard_stats": token_stats, "cross_guard_stats": cross_stats,
        },
        "checked_artifacts": [str(BASE / "artifacts" / name) for name in (*OUTPUT_NAMES, "RESULT.json")],
        "claim_boundary": "Independent source-first shape, arithmetic, scope, concreteness, hash, and byte-replay validation; not a plaintext proof.",
    }
    (ART / "VALIDATION.json").write_text(json.dumps(validation, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if failures:
        print(status, file=sys.stderr)
        for name in failures:
            print(f"FAIL {name}", file=sys.stderr)
        if replay_error:
            print(replay_error, file=sys.stderr)
        return 1
    print(f"GDT661 validated: {status}; byte_replay=PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
