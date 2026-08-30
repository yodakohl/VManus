#!/usr/bin/env python3
"""Independent, source-first release validator for GDT659.

Protected raw queries and an independent reader-boundary reconstruction run
before any GDT659 output is trusted.  The builder is never imported; its CLI is
invoked only at the end, into a temporary directory, for a byte replay.
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
BASE = Path("experiments/yolo/gdt659_naked_y_local_reference")
ART = ROOT / BASE / "artifacts"
RUN = ROOT / BASE / "src/run.py"
MANIFEST = ROOT / BASE / "experiment.json"
VALIDATION = ART / "VALIDATION.json"

G658 = Path("experiments/yolo/gdt658_four_residual_concrete_completion")
ALLOW = G658 / "artifacts/PAGE_ALLOWLIST.tsv"
BASE_GLOSSARY = G658 / "artifacts/V35_WORKING_TOKEN_GLOSSARY.tsv"
BASE_DICTIONARY = G658 / "artifacts/WORKING_DICTIONARY_V35.tsv"
BASE_COVERAGE = G658 / "artifacts/ALL_LINE_CONCRETE_COVERAGE_V35.tsv"
BASE_COMPLETE = G658 / "artifacts/COMPLETE_PASSAGES_V35.tsv"
BASE_ONE = G658 / "artifacts/ONE_UNKNOWN_PASSAGES_V35.tsv"
TOKENS = Path("transcription/voynich_zl3b_tokens.tsv")
CROSS = Path("transcription/voynich_cross_transcription_lines.tsv")

STATUS = "PASS_270_NAKED_Y_CONTEXT_CARDS__V36"
RESULT_SCHEMA = "GDT659_NAKED_Y_LOCAL_REFERENCE_RESULT_V1"
OUTPUT_NAMES = (
    "PAGE_ALLOWLIST.tsv", "Y_CONTEXT_CARDS.tsv", "Y_OCCURRENCE_CENSUS.tsv",
    "Y_CONTEXT_CLASS_SUMMARY.tsv", "Y_DIMENSION_PROFILE.tsv", "Y_PAGE_COUNTS.tsv",
    "Y_READER_BOUNDARY_AUDIT.tsv", "Y_READER_BOUNDARY_SUMMARY.tsv",
    "Y_NEIGHBOR_ATLAS.tsv", "Y_NEIGHBOR_SUMMARY.tsv",
    "Y_AFFECTED_LINE_TRANSLATIONS.tsv", "F80V21_WORKING_TRANSLATION.tsv",
    "V36_WORKING_TOKEN_GLOSSARY.tsv", "WORKING_DICTIONARY_V36.tsv",
    "ALL_LINE_CONCRETE_COVERAGE_V36.tsv", "COMPLETE_PASSAGES_V36.tsv",
    "ONE_UNKNOWN_PASSAGES_V36.tsv", "NEWLY_COMPLETED_LINES.tsv",
    "NEWLY_EXPOSED_ONE_HOLE_LINES.tsv", "ROUND_COVERAGE_COUNTS.tsv",
)

BASE_CLASSES = {
    "Y_ONLY_DIVIDER": 9, "Y_BOS_ENTRY": 60, "Y_EOS_CLOSE": 34,
    "Y_MEDIAL_RIGHT_REFERENCE": 43, "Y_MEDIAL_LEFT_CLOSE": 36,
    "Y_MEDIAL_BIDIRECTIONAL_HINGE": 50, "Y_MEDIAL_UNRESOLVED_HINGE": 38,
}
FINAL_ORDER = (
    "Y_LABEL_SIGLUM", "Y_BOS_ENTRY", "Y_EOS_CLOSE",
    "Y_MEDIAL_RIGHT_REFERENCE", "Y_MEDIAL_LEFT_CLOSE",
    "Y_MEDIAL_BIDIRECTIONAL_HINGE", "Y_MEDIAL_UNRESOLVED_HINGE",
    "Y_MEDIAL_RIGHT_REFERENCE_MATERIA",
)
FINAL_CLASSES = {
    "Y_LABEL_SIGLUM": 11, "Y_BOS_ENTRY": 60, "Y_EOS_CLOSE": 33,
    "Y_MEDIAL_RIGHT_REFERENCE": 31, "Y_MEDIAL_LEFT_CLOSE": 35,
    "Y_MEDIAL_BIDIRECTIONAL_HINGE": 49, "Y_MEDIAL_UNRESOLVED_HINGE": 38,
    "Y_MEDIAL_RIGHT_REFERENCE_MATERIA": 13,
}
POSITIONS = {"BOS": 60, "MEDIAL": 167, "EOS": 34, "ONLY": 9}
KINDS = {"P": 259, "L": 11}
BASE_METRICS = {
    "physical_lines": 4128, "known_token_positions": 16743,
    "unknown_token_positions": 15596, "complete_multi_token_lines": 138,
    "strict_complete_lines": 80, "one_unknown_lines": 239,
    "strict_one_unknown_lines": 57, "working_glossary_surfaces": 495,
}
FINAL_METRICS = {
    "physical_lines": 4128, "known_token_positions": 17013,
    "unknown_token_positions": 15326, "complete_multi_token_lines": 146,
    "strict_complete_lines": 80, "one_unknown_lines": 249,
    "strict_one_unknown_lines": 58, "working_glossary_surfaces": 495,
}
NEW_COMPLETE = {
    "f112r.9", "f39v.13", "f76r.13", "f77v.1", "f78v.7",
    "f80v.21", "f85r1.16", "f99r.2",
}
READER_MATRIX = {
    ("IT2a", "BOS"): (25, 29, 0, 0, 6, 60, 18),
    ("IT2a", "MEDIAL"): (57, 52, 23, 3, 32, 167, 43),
    ("IT2a", "EOS"): (16, 0, 12, 0, 6, 34, 13),
    ("IT2a", "ONLY"): (9, 0, 0, 0, 0, 9, 9),
    ("IT2a", "ALL"): (107, 81, 35, 3, 44, 270, 83),
    ("RF1b", "BOS"): (32, 24, 0, 0, 4, 60, 18),
    ("RF1b", "MEDIAL"): (107, 23, 13, 3, 21, 167, 43),
    ("RF1b", "EOS"): (20, 0, 9, 0, 5, 34, 13),
    ("RF1b", "ONLY"): (9, 0, 0, 0, 0, 9, 9),
    ("RF1b", "ALL"): (168, 47, 22, 3, 30, 270, 83),
}

# structural tag, selection rule, card render, live rival
CONTEXT = {
    "Y_LABEL_SIGLUM": (
        "NAKED_Y|TOKEN_KIND=L|ROLE=LABEL_SIGLUM",
        "token kind L overrides positional P-text semantics; subrole is ONLY, INTERNAL or CLOSE",
        "[Beschriftungszeichen] / ; / .",
        "bloßes Form- oder Schlusszeichen innerhalb des Labels",
    ),
    "Y_BOS_ENTRY": (
        "NAKED_Y|TOKEN_KIND=P|POSITION=BOS|ROLE=ENTRY_HEAD",
        "P token at physical-line beginning", "Eintrag:",
        "hierzu / zu derselben Droge, falls ein lokaler Antezedent sichtbar wird",
    ),
    "Y_EOS_CLOSE": (
        "NAKED_Y|TOKEN_KIND=P|POSITION=EOS|ROLE=ENTRY_CLOSE",
        "P token at physical-line end", ".",
        "postponierter Bezug auf den linken Stoff",
    ),
    "Y_MEDIAL_RIGHT_REFERENCE": (
        "NAKED_Y|TOKEN_KIND=P|POSITION=MEDIAL|ATTACHMENT=RIGHT",
        "observed ZL sister y+RIGHT and no observed LEFT+y sister", "hierzu:",
        "neuer Unterposten statt deiktischer Bezug",
    ),
    "Y_MEDIAL_LEFT_CLOSE": (
        "NAKED_Y|TOKEN_KIND=P|POSITION=MEDIAL|ATTACHMENT=LEFT",
        "observed ZL sister LEFT+y and no observed y+RIGHT sister", ";",
        "rechte Eintragsreferenz bei einem konkreten Folgekörper",
    ),
    "Y_MEDIAL_BIDIRECTIONAL_HINGE": (
        "NAKED_Y|TOKEN_KIND=P|POSITION=MEDIAL|ATTACHMENT=BOTH",
        "both observed ZL sisters LEFT+y and y+RIGHT", "hierzu:",
        "nur linkes Formende oder nur rechter Eintragskopf",
    ),
    "Y_MEDIAL_UNRESOLVED_HINGE": (
        "NAKED_Y|TOKEN_KIND=P|POSITION=MEDIAL|ATTACHMENT=UNRESOLVED",
        "neither LEFT+y nor y+RIGHT is observed as a ZL whole", "hierzu:",
        "gelernter lokaler Trenner ohne deiktische Funktion",
    ),
    "Y_MEDIAL_RIGHT_REFERENCE_MATERIA": (
        "NAKED_Y|TOKEN_KIND=P|POSITION=MEDIAL|ROLE=RIGHT_REFERENCE|RIGHT_CLASS=MATERIA_PREPARATION",
        "known V35 right Materia/preparation head with mechanical RIGHT attachment; plus explicit f80v.21 IT2a y+rchey exception",
        "hierzu: rechter Kopf",
        "plain mechanical right reference; f80v.21 retains its recorded LEFT-close rival",
    ),
}
TOKEN_GLOSS = {
    "Y_BOS_ENTRY": "Eintrag:", "Y_EOS_CLOSE": "Eintrag abgeschlossen",
    "Y_MEDIAL_RIGHT_REFERENCE": "hierzu:", "Y_MEDIAL_LEFT_CLOSE": "Eintragsteil abgeschlossen",
    "Y_MEDIAL_BIDIRECTIONAL_HINGE": "; hierzu:",
    "Y_MEDIAL_UNRESOLVED_HINGE": "hierzu:",
    "Y_MEDIAL_RIGHT_REFERENCE_MATERIA": "hierzu:",
}
LABEL_GLOSS = {
    "LABEL_ONLY": "Beschriftungszeichen", "LABEL_INTERNAL": "Labelgliederung",
    "LABEL_CLOSE": "Labelschluss", "LABEL_ENTRY": "Labelzeichen",
}
LABEL_RENDER = {
    "LABEL_ONLY": "[Beschriftungszeichen]", "LABEL_INTERNAL": ";",
    "LABEL_CLOSE": ".", "LABEL_ENTRY": "[Beschriftungszeichen]",
}
MATERIA_RE = re.compile(
    r"wurzel|droge|drogen|rohstoff|arznei|samen|holz|blatt|blüt|frucht|zutat|"
    r"pflanzen|pulver|feuchtgut|trockengut|stoff|material|präparat|ansatz|zubereitung|\bgut\b",
    re.IGNORECASE,
)
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


def split_pipe(value: str) -> list[str]:
    return value.split(" | ") if value else []


def split_compact(value: str) -> list[str]:
    return [] if value in {"", "NONE"} else value.split("|")


def guarded_query(path: Path, pages: set[str], columns: str) -> tuple[list[dict[str, str]], dict[str, int]]:
    command = [str(ROOT / "vmanus-exp"), "query-tsv", str(path), "--selector", "page"]
    for page in sorted(pages):
        command.extend(("--allow", page))
    command.extend(("--columns", columns, "--forbid-prefix", "f84", "--forbid-prefix", "f84r"))
    done = subprocess.run(command, cwd=ROOT, text=True, capture_output=True, check=False)
    stats_lines = [line for line in done.stderr.splitlines() if line.startswith("GUARD_STATS ")]
    if done.returncode or len(stats_lines) != 1:
        raise RuntimeError(done.stderr or "guarded TSV query failed")
    rows = list(csv.DictReader(io.StringIO(done.stdout), delimiter="\t"))
    stats = {key: int(value) for key, value in json.loads(stats_lines[0][12:]).items()}
    if stats.get("selected") != len(rows):
        raise RuntimeError("guard statistics disagree with materialized row count")
    if any(row.get("page") == "f1r" or row.get("page", "").startswith("f84") for row in rows):
        raise RuntimeError("forbidden page escaped guarded query")
    return rows, stats


def position(ordinal: int, length: int) -> str:
    if length == 1:
        return "ONLY"
    if ordinal == 1:
        return "BOS"
    if ordinal == length:
        return "EOS"
    return "MEDIAL"


def mechanical_class(place: str, left_count: int, right_count: int) -> str:
    if place == "ONLY":
        return "Y_ONLY_DIVIDER"
    if place == "BOS":
        return "Y_BOS_ENTRY"
    if place == "EOS":
        return "Y_EOS_CLOSE"
    if right_count and not left_count:
        return "Y_MEDIAL_RIGHT_REFERENCE"
    if left_count and not right_count:
        return "Y_MEDIAL_LEFT_CLOSE"
    if left_count and right_count:
        return "Y_MEDIAL_BIDIRECTIONAL_HINGE"
    return "Y_MEDIAL_UNRESOLVED_HINGE"


def boundary_candidates(words: list[str], index: int) -> dict[str, str]:
    candidates = {"SEPARATE": "y"}
    if index + 1 < len(words):
        candidates["MERGE_RIGHT"] = "y" + words[index + 1]
    if index:
        candidates["MERGE_LEFT"] = words[index - 1] + "y"
    if index and index + 1 < len(words):
        candidates["MERGE_BOTH"] = words[index - 1] + "y" + words[index + 1]
    return candidates


def independent_boundary_alignment(words: list[str], reader: list[str]) -> dict[int, tuple[str, str]]:
    """Order-preserving maximum boundary matching without builder code."""
    indices = [index for index, word in enumerate(words) if word == "y"]
    n, m = len(indices), len(reader)
    impossible = (-10**9, -10**9)
    score = [[impossible] * (m + 1) for _ in range(n + 1)]
    back: list[list[tuple[int, int, str, str] | None]] = [[None] * (m + 1) for _ in range(n + 1)]
    score[0][0] = (0, 0)
    rank = {"SEPARATE": 4, "MERGE_RIGHT": 3, "MERGE_LEFT": 2, "MERGE_BOTH": 1}
    for i in range(n + 1):
        for j in range(m + 1):
            if score[i][j] == impossible:
                continue
            if i < n and score[i][j] > score[i + 1][j]:
                score[i + 1][j] = score[i][j]
                back[i + 1][j] = (i, j, "VARIANT_OTHER", "")
            if j < m and score[i][j] > score[i][j + 1]:
                score[i][j + 1] = score[i][j]
                back[i][j + 1] = (i, j, "SKIP", "")
            if i < n and j < m:
                for category, surface in boundary_candidates(words, indices[i]).items():
                    if reader[j] != surface:
                        continue
                    proposed = (score[i][j][0] + 1, score[i][j][1] + rank[category])
                    if proposed > score[i + 1][j + 1]:
                        score[i + 1][j + 1] = proposed
                        back[i + 1][j + 1] = (i, j, category, surface)
    assignments: list[tuple[str, str] | None] = [None] * n
    i, j = n, m
    while i or j:
        step = back[i][j]
        if step is None:
            raise RuntimeError("reader-boundary traceback failed")
        old_i, old_j, category, surface = step
        if i == old_i + 1:
            assignments[old_i] = (category, surface)
        i, j = old_i, old_j
    if any(item is None for item in assignments):
        raise RuntimeError("reader-boundary occurrence left unassigned")
    return {index: assignments[number] for number, index in enumerate(indices)}  # type: ignore[misc]


def is_materia(surface: str, glossary: dict[str, dict[str, str]]) -> bool:
    return surface in glossary and bool(MATERIA_RE.search(glossary[surface]["working_meaning_de"]))


def label_subrole(place: str) -> str:
    return {"ONLY": "LABEL_ONLY", "MEDIAL": "LABEL_INTERNAL", "EOS": "LABEL_CLOSE"}.get(place, "LABEL_ENTRY")


def local_span(words: list[str], index: int) -> str:
    return " ".join(words[max(0, index - 1):min(len(words), index + 2)])


def manual_reader_status(expected: dict[str, object], cross: dict[str, str]) -> str:
    it_separate = expected["it2a_boundary_class"] == "SEPARATE"
    rf_separate = expected["rf1b_boundary_class"] == "SEPARATE"
    if cross["zl3b_clean"] == cross["it2a_clean"] == cross["rf1b_clean"]:
        return "EXACT_LINE"
    if it_separate and rf_separate:
        return "Y_RETAINED_OTHER_VARIANT"
    if not it_separate and not rf_separate:
        return "BOTH_LOSE_OR_FUSE_Y"
    return "IT_LOSES_OR_FUSES_Y" if not it_separate else "RF_LOSES_OR_FUSES_Y"


def coverage_metrics(
    coverage: list[dict[str, str]], complete: list[dict[str, str]],
    one: list[dict[str, str]], glossary_size: int,
) -> dict[str, int]:
    return {
        "physical_lines": len(coverage),
        "known_token_positions": sum(int(row["known_tokens"]) for row in coverage),
        "unknown_token_positions": sum(int(row["unknown_tokens"]) for row in coverage),
        "complete_multi_token_lines": len(complete),
        "strict_complete_lines": sum(int(row["strict_complete"]) for row in complete),
        "one_unknown_lines": len(one),
        "strict_one_unknown_lines": sum(int(row["strict_eligible"]) for row in one),
        "working_glossary_surfaces": glossary_size,
    }


def build_expected_occurrences(
    token_rows: list[dict[str, str]], cross_rows: list[dict[str, str]],
    glossary: dict[str, dict[str, str]],
) -> tuple[list[dict[str, object]], dict[str, list[dict[str, str]]], dict[str, dict[str, str]], Counter[str]]:
    cross_by = {row["locus"]: row for row in cross_rows}
    by_line: dict[str, list[dict[str, str]]] = defaultdict(list)
    surface_counts = Counter(row["eva"] for row in token_rows)
    for row in token_rows:
        by_line[row["locus"]].append(row)
    for line in by_line.values():
        line.sort(key=lambda row: int(row["token_index"]))

    expected: list[dict[str, object]] = []
    number = 0
    for locus in sorted(by_line):
        line = by_line[locus]
        words = [row["eva"] for row in line]
        y_indices = [index for index, word in enumerate(words) if word == "y"]
        if not y_indices:
            continue
        cross = cross_by[locus]
        assignments = {
            "IT2a": independent_boundary_alignment(words, cross["it2a_clean"].split()),
            "RF1b": independent_boundary_alignment(words, cross["rf1b_clean"].split()),
        }
        for index in y_indices:
            number += 1
            token = line[index]
            place = position(index + 1, len(line))
            left = words[index - 1] if index else "<BOS>"
            right = words[index + 1] if index + 1 < len(words) else "<EOS>"
            left_fused = left + "y" if index else "NONE"
            right_fused = "y" + right if index + 1 < len(words) else "NONE"
            left_count = 0 if left_fused == "NONE" else surface_counts[left_fused]
            right_count = 0 if right_fused == "NONE" else surface_counts[right_fused]
            base_class = mechanical_class(place, left_count, right_count)
            it_class, it_surface = assignments["IT2a"][index]
            rf_class, rf_surface = assignments["RF1b"][index]
            final_class = base_class
            materia_subtype = 0
            direction_override = 0
            if token["kind"] == "L":
                final_class = "Y_LABEL_SIGLUM"
            elif (
                place == "MEDIAL" and is_materia(right, glossary)
                and (
                    base_class == "Y_MEDIAL_RIGHT_REFERENCE"
                    or (locus == "f80v.21" and right == "rchey" and it_class == "MERGE_RIGHT")
                )
            ):
                final_class = "Y_MEDIAL_RIGHT_REFERENCE_MATERIA"
                materia_subtype = 1
                direction_override = int(base_class != "Y_MEDIAL_RIGHT_REFERENCE")
            subrole = label_subrole(place) if token["kind"] == "L" else "NONE"
            token_gloss = LABEL_GLOSS[subrole] if final_class == "Y_LABEL_SIGLUM" else TOKEN_GLOSS[final_class]
            if final_class == "Y_LABEL_SIGLUM":
                rendering = LABEL_RENDER[subrole]
            elif final_class == "Y_MEDIAL_RIGHT_REFERENCE_MATERIA":
                right_meaning = glossary[right]["working_meaning_de"]
                if locus == "f80v.21" and right == "rchey":
                    right_meaning = "trocken gebundene Wurzeldroge, Form I"
                rendering = "hierzu: " + right_meaning
            else:
                rendering = CONTEXT[final_class][2]
            expected.append({
                "occurrence_id": f"G659-Y{number:03d}", "page": token["page"], "locus": locus,
                "token_index": token["token_index"], "ordinal": index + 1, "line_length": len(line),
                "position": place, "token_kind": token["kind"], "section": token["section"],
                "language": token["language"], "hand": token["hand"], "left_surface": left,
                "right_surface": right, "left_fused_surface": left_fused,
                "left_fused_occurrences": left_count, "right_fused_surface": right_fused,
                "right_fused_occurrences": right_count, "left_v35_known": int(left in glossary),
                "left_v35_meaning_de": glossary.get(left, {}).get("working_meaning_de", "OPEN"),
                "right_v35_known": int(right in glossary),
                "right_v35_meaning_de": glossary.get(right, {}).get("working_meaning_de", "OPEN"),
                "right_materia_preparation_head": int(is_materia(right, glossary)),
                "base_context_class": base_class, "context_class": final_class,
                "materia_subtype": materia_subtype, "direction_override": direction_override,
                "label_subrole": subrole,
                "structural_tag": CONTEXT[final_class][0], "token_gloss_de": token_gloss,
                "working_render_de": rendering, "live_rival_de": CONTEXT[final_class][3],
                "all_three_present": cross["all_three_present"],
                "line_all_present_exact": cross["all_present_exact"],
                "all_reader_separate_y": int(it_class == "SEPARATE" and rf_class == "SEPARATE"),
                "it2a_boundary_class": it_class, "it2a_matched_surface": it_surface or "NONE",
                "rf1b_boundary_class": rf_class, "rf1b_matched_surface": rf_surface or "NONE",
            })
    return expected, by_line, cross_by, surface_counts


def validate_release(
    check: Callable[[object, str, str], None], token_rows: list[dict[str, str]],
    cross_rows: list[dict[str, str]], token_stats: dict[str, int],
    cross_stats: dict[str, int], pages: set[str],
) -> None:
    required = set(OUTPUT_NAMES) | {
        "RESULT.json", "MANUAL_Y_CONTEXT_AUDIT.tsv", "HISTORICAL_ENTRY_MARKER_ANALOGIES.tsv"
    }
    missing = sorted(name for name in required if not (ART / name).is_file())
    check(not missing, "required artifact packet", repr(missing))
    if missing:
        return

    # These reads occur only after the guarded raw-source gates in main().
    base_gloss_rows = read_tsv(ROOT / BASE_GLOSSARY)
    base_gloss = {row["surface"]: row for row in base_gloss_rows}
    check(len(base_gloss_rows) == len(base_gloss) == 495 and "y" not in base_gloss, "V35 glossary source state")
    expected, by_line, cross_by, surface_counts = build_expected_occurrences(token_rows, cross_rows, base_gloss)
    check(
        (len(expected), len({row["locus"] for row in expected}), len({row["page"] for row in expected})) == (270, 257, 125),
        "independent naked-y census 270/257/125",
    )
    pos_counts = Counter(str(row["position"]) for row in expected)
    kind_counts = Counter(str(row["token_kind"]) for row in expected)
    check(pos_counts == POSITIONS, "independent position census", repr(pos_counts))
    check(kind_counts == KINDS, "independent P/L census", repr(kind_counts))
    only = [row for row in expected if row["position"] == "ONLY"]
    check(len(only) == 9 and all(row["token_kind"] == "L" for row in only), "all nine ONLY occurrences are labels")
    check(sum(int(row["all_reader_separate_y"]) for row in expected) == 83, "83 per-occurrence all-reader separate-y positions")
    check(sum(int(row["line_all_present_exact"]) for row in expected) == 25, "25 full-line exact y positions")

    census = read_tsv(ART / "Y_OCCURRENCE_CENSUS.tsv")
    expected_by = {(str(row["locus"]), str(row["token_index"])): row for row in expected}
    census_by = {(row["locus"], row["token_index"]): row for row in census}
    check(len(census) == len(census_by) == 270 and set(census_by) == set(expected_by), "all 270 occurrences exactly once")
    census_ok = True
    for key, wanted in expected_by.items():
        got = census_by.get(key, {})
        census_ok &= all(got.get(field) == str(value) for field, value in wanted.items())
        census_ok &= not FILLER.search(" ".join(got.values()))
    check(census_ok, "independent occurrence metadata, hierarchy and rendering replay")

    base_counts = Counter(str(row["base_context_class"]) for row in expected)
    final_counts = Counter(str(row["context_class"]) for row in expected)
    check(base_counts == BASE_CLASSES, "mechanical context classes", repr(base_counts))
    check(final_counts == FINAL_CLASSES, "label/materia precedence classes", repr(final_counts))
    labels = [row for row in expected if row["context_class"] == "Y_LABEL_SIGLUM"]
    check(
        len(labels) == 11 and all(row["token_kind"] == "L" for row in labels)
        and Counter(str(row["label_subrole"]) for row in labels) == {"LABEL_ONLY": 9, "LABEL_INTERNAL": 1, "LABEL_CLOSE": 1}
        and {row["locus"] for row in labels if row["label_subrole"] != "LABEL_ONLY"} == {"f77v.1", "f99r.2"},
        "label precedence, including internal and close overrides",
    )
    materia = [row for row in expected if row["materia_subtype"] == 1]
    check(
        len(materia) == 13 and all(
            row["token_kind"] == "P" and row["position"] == "MEDIAL"
            and row["right_materia_preparation_head"] == 1
            and (
                row["base_context_class"] == "Y_MEDIAL_RIGHT_REFERENCE"
                or (
                    row["locus"] == "f80v.21" and row["right_surface"] == "rchey"
                    and row["it2a_boundary_class"] == "MERGE_RIGHT"
                )
            ) for row in materia
        ),
        "13 narrowly licensed right-materia subtype positions obey hierarchy",
    )
    direction_overrides = [row for row in expected if row["direction_override"] == 1]
    check(
        len(direction_overrides) == 1 and direction_overrides[0]["locus"] == "f80v.21",
        "exactly one materia direction override, at f80v.21",
    )

    cards = read_tsv(ART / "Y_CONTEXT_CARDS.tsv")
    check(len(cards) == 8 and [row["context_class"] for row in cards] == list(FINAL_ORDER), "eight ordered context cards")
    cards_ok = True
    for number, row in enumerate(cards, 1):
        role = row["context_class"]
        spec = CONTEXT[role]
        members = [item for item in expected if item["context_class"] == role]
        cards_ok &= (
            row["card_id"] == f"G659-C{number:02d}" and row["structural_tag"] == spec[0]
            and row["selection_rule"] == spec[1] and row["working_render_de"] == spec[2]
            and row["live_rival_de"] == spec[3] and int(row["occurrences"]) == len(members)
            and int(row["lines"]) == len({item["locus"] for item in members})
            and int(row["pages"]) == len({item["page"] for item in members})
            and int(row["all_reader_separate_y"]) == sum(int(item["all_reader_separate_y"]) for item in members)
            and row["status"] == "ACCEPT_V36_CONTEXT_CARD_NOT_GLOBAL_LEXEME"
            and not FILLER.search(" ".join(row.values()))
        )
    check(cards_ok, "context-card content and raw counts")
    bos_card = next(row for row in cards if row["context_class"] == "Y_BOS_ENTRY")
    unresolved = next(row for row in cards if row["context_class"] == "Y_MEDIAL_UNRESOLVED_HINGE")
    check(bos_card["working_render_de"] == "Eintrag:" and "dieser" not in bos_card["working_render_de"].lower(), "BOS card has no invented demonstrative")
    check(unresolved["working_render_de"] == "hierzu:" and "[lokale Gliederung]" not in unresolved["working_render_de"], "unresolved card has no placeholder prose")

    summary = read_tsv(ART / "Y_CONTEXT_CLASS_SUMMARY.tsv")
    summary_by = {(row["layer"], row["context_class"]): int(row["occurrences"]) for row in summary}
    check(
        len(summary) == 15
        and {role: summary_by.get(("MECHANICAL_BASE", role)) for role in BASE_CLASSES} == BASE_CLASSES
        and {role: summary_by.get(("FINAL_WITH_LABEL_AND_MATERIA_PRECEDENCE", role)) for role in FINAL_CLASSES} == FINAL_CLASSES,
        "two-layer context summary",
    )

    reader_audit = read_tsv(ART / "Y_READER_BOUNDARY_AUDIT.tsv")
    audit_by = {row["occurrence_id"]: row for row in reader_audit}
    check(len(reader_audit) == len(audit_by) == 270, "270 unique reader-boundary audits")
    reader_ok = True
    for wanted in expected:
        row = audit_by.get(str(wanted["occurrence_id"]), {})
        cross = cross_by[str(wanted["locus"])]
        fields = (
            "page", "locus", "ordinal", "position", "token_kind", "left_surface", "right_surface",
            "all_reader_separate_y", "it2a_boundary_class", "it2a_matched_surface",
            "rf1b_boundary_class", "rf1b_matched_surface",
        )
        reader_ok &= all(row.get(field) == str(wanted[field]) for field in fields)
        reader_ok &= row.get("target_surface") == "y"
        reader_ok &= row.get("zl3b_line") == cross["zl3b_clean"]
        reader_ok &= row.get("it2a_line") == cross["it2a_clean"]
        reader_ok &= row.get("rf1b_line") == cross["rf1b_clean"]
    check(reader_ok, "independent reader-boundary occurrence replay")

    reconstructed_matrix: dict[tuple[str, str], tuple[int, ...]] = {}
    for reader, prefix in (("IT2a", "it2a"), ("RF1b", "rf1b")):
        for place in ("BOS", "MEDIAL", "EOS", "ONLY", "ALL"):
            members = expected if place == "ALL" else [row for row in expected if row["position"] == place]
            counts = Counter(str(row[f"{prefix}_boundary_class"]) for row in members)
            reconstructed_matrix[reader, place] = (
                counts["SEPARATE"], counts["MERGE_RIGHT"], counts["MERGE_LEFT"],
                counts["MERGE_BOTH"], counts["VARIANT_OTHER"], len(members),
                sum(int(row["all_reader_separate_y"]) for row in members),
            )
    check(reconstructed_matrix == READER_MATRIX, "raw reader fusion matrix", repr(reconstructed_matrix))
    check(
        all(reconstructed_matrix[reader, "BOS"][2:4] == (0, 0) for reader in ("IT2a", "RF1b"))
        and all((reconstructed_matrix[reader, "EOS"][1], reconstructed_matrix[reader, "EOS"][3]) == (0, 0) for reader in ("IT2a", "RF1b")),
        "BOS binds only right; EOS binds only left",
    )
    reader_summary = read_tsv(ART / "Y_READER_BOUNDARY_SUMMARY.tsv")
    artifact_matrix = {
        (row["reader"], row["position"]): tuple(int(row[field]) for field in (
            "separate", "merge_right", "merge_left", "merge_both", "variant_or_other",
            "total", "all_reader_separate_capacity",
        )) for row in reader_summary
    }
    check(len(reader_summary) == 10 and artifact_matrix == READER_MATRIX, "reader-boundary summary packet")

    dimensions = read_tsv(ART / "Y_DIMENSION_PROFILE.tsv")
    dimension_by = {(row["dimension"], row["value"]): row for row in dimensions}
    dimension_ok = True
    field_map = {"POSITION": "position", "TOKEN_KIND": "token_kind", "SECTION": "section", "LANGUAGE": "language", "HAND": "hand"}
    expected_cells: set[tuple[str, str]] = set()
    for dimension, field in field_map.items():
        for value in sorted({str(row[field]) for row in expected}):
            expected_cells.add((dimension, value))
            members = [row for row in expected if str(row[field]) == value]
            got = dimension_by.get((dimension, value), {})
            dimension_ok &= tuple(int(got.get(key, -1)) for key in ("occurrences", "bos", "medial", "eos", "only")) == (
                len(members), sum(row["position"] == "BOS" for row in members),
                sum(row["position"] == "MEDIAL" for row in members),
                sum(row["position"] == "EOS" for row in members),
                sum(row["position"] == "ONLY" for row in members),
            )
    check(dimension_ok and set(dimension_by) == expected_cells, "section/language/hand/position profile replay")

    page_rows = read_tsv(ART / "Y_PAGE_COUNTS.tsv")
    page_by = {row["page"]: row for row in page_rows}
    expected_pages = {str(row["page"]) for row in expected}
    page_ok = len(page_rows) == len(page_by) == 125
    for page in expected_pages:
        members = [row for row in expected if row["page"] == page]
        got = page_by.get(page, {})
        page_ok &= tuple(int(got.get(field, -1)) for field in (
            "occurrences", "lines", "bos", "medial", "eos", "only", "p_tokens", "l_tokens"
        )) == (
            len(members), len({row["locus"] for row in members}),
            sum(row["position"] == "BOS" for row in members),
            sum(row["position"] == "MEDIAL" for row in members),
            sum(row["position"] == "EOS" for row in members),
            sum(row["position"] == "ONLY" for row in members),
            sum(row["token_kind"] == "P" for row in members),
            sum(row["token_kind"] == "L" for row in members),
        )
    check(page_ok and set(page_by) == expected_pages, "125-page occurrence profile replay")

    manual = read_tsv(ART / "MANUAL_Y_CONTEXT_AUDIT.tsv")
    manual_ok = len(manual) == len({row["sample_id"] for row in manual}) == 38
    for row in manual:
        candidates = [item for item in expected if item["locus"] == row["locus"]]
        manual_ok &= len(candidates) == 1
        if not candidates:
            continue
        item = candidates[0]
        words = [token["eva"] for token in by_line[row["locus"]]]
        index = int(item["ordinal"]) - 1
        span_words = row["local_span"].split()
        span_matches_source = any(
            words[start:start + len(span_words)] == span_words
            and start <= index < start + len(span_words)
            and span_words[index - start] == "y"
            for start in range(len(words) - len(span_words) + 1)
        )
        manual_ok &= (
            row["page"] == item["page"] and row["section"] == item["section"]
            and row["language"] == item["language"] and row["hand"] == item["hand"]
            and row["position"] == item["position"] and row["token_type"] == item["token_kind"]
            and span_matches_source
            and row["reader_status"] == manual_reader_status(item, cross_by[row["locus"]])
            and all(row[field].strip() for field in (
                "deictic_A", "entry_B", "closure_C", "best_role", "best_rendering_de",
                "reason", "rival/replacement_trigger",
            ))
            and not FILLER.search(" ".join(row.values()))
        )
    check(manual_ok, "38 protected manual contexts map to raw source")
    check(
        Counter(row["position"] for row in manual) == {"BOS": 10, "MEDIAL": 18, "EOS": 8, "ONLY": 2}
        and set(row["section"] for row in manual) == {"H", "P", "B", "C", "T", "S"}
        and set(row["language"] for row in manual) == {"A", "B"}
        and set(row["hand"] for row in manual) == {"1", "2", "3", "5", "@"}
        and len(set(row["reader_status"] for row in manual)) == 5,
        "manual audit is stratified across requested dimensions",
    )

    historical = read_tsv(ART / "HISTORICAL_ENTRY_MARKER_ANALOGIES.tsv")
    source_ids = {
        "HEXHAM_1415", "HARLEY_4087", "ROYAL_12_G_IV", "LANFRANK_WITNESSES",
        "CAPPELLI_UZH", "FRIEDMAN_EARLY_NOMENCLATORS",
    }
    check(
        len(historical) == 6 and {row["source_id"] for row in historical} == source_ids
        and all(all(value.strip() for value in row.values()) and row["url"].startswith("https://") for row in historical)
        and all(not FILLER.search(" ".join(row.values())) for row in historical),
        "six concrete historical analogies with limitations and URLs",
    )

    surface_pages: dict[str, set[str]] = defaultdict(set)
    for row in token_rows:
        surface_pages[row["eva"]].add(row["page"])
    neighbor_atlas = read_tsv(ART / "Y_NEIGHBOR_ATLAS.tsv")
    neighbor_by = {(row["side"], row["neighbor_surface"]): row for row in neighbor_atlas}
    expected_neighbor_keys: set[tuple[str, str]] = set()
    neighbor_summaries: dict[str, tuple[int, ...]] = {}
    neighbor_ok = True
    for side, field in (("LEFT", "left_surface"), ("RIGHT", "right_surface")):
        eligible = [row for row in expected if row[field] not in {"<BOS>", "<EOS>"}]
        grouped: dict[str, list[dict[str, object]]] = defaultdict(list)
        for row in eligible:
            grouped[str(row[field])].append(row)
        for surface, members in grouped.items():
            expected_neighbor_keys.add((side, surface))
            got = neighbor_by.get((side, surface), {})
            fused = surface + "y" if side == "LEFT" else "y" + surface
            known = surface in base_gloss
            neighbor_ok &= (
                int(got.get("occurrences", -1)) == len(members)
                and int(got.get("lines", -1)) == len({row["locus"] for row in members})
                and int(got.get("pages", -1)) == len({row["page"] for row in members})
                and got.get("v35_known") == str(int(known))
                and got.get("v35_meaning_de") == base_gloss.get(surface, {}).get("working_meaning_de", "OPEN")
                and got.get("v35_source") == base_gloss.get(surface, {}).get("source", "OPEN")
                and got.get("materia_preparation_head") == str(int(side == "RIGHT" and is_materia(surface, base_gloss)))
                and got.get("fused_sister_surface") == fused
                and got.get("fused_sister_occurrences") == str(surface_counts[fused])
                and got.get("fused_sister_pages") == str(len(surface_pages.get(fused, set())))
                and got.get("example_loci") == "|".join(sorted({str(row["locus"]) for row in members})[:8])
            )
        neighbor_summaries[side] = (
            len(eligible), len(grouped), sum(row[field] in base_gloss for row in eligible),
            sum(surface in base_gloss for surface in grouped),
            sum(surface_counts[(str(row[field]) + "y") if side == "LEFT" else ("y" + str(row[field]))] > 0 for row in eligible),
            sum(surface_counts[(surface + "y") if side == "LEFT" else ("y" + surface)] > 0 for surface in grouped),
            sum(side == "RIGHT" and is_materia(str(row[field]), base_gloss) for row in eligible),
            sum(side == "RIGHT" and is_materia(surface, base_gloss) for surface in grouped),
        )
    check(neighbor_ok and set(neighbor_by) == expected_neighbor_keys, "neighbor atlas independently replayed")
    neighbor_summary = read_tsv(ART / "Y_NEIGHBOR_SUMMARY.tsv")
    summary_by_side = {
        row["side"]: tuple(int(row[field]) for field in (
            "positions", "surface_types", "v35_known_positions", "v35_known_types",
            "fused_sister_positions", "fused_sister_types", "materia_preparation_positions",
            "materia_preparation_types",
        )) for row in neighbor_summary
    }
    check(len(neighbor_summary) == 2 and summary_by_side == neighbor_summaries, "neighbor summary independently replayed")

    f80_expected = next(row for row in expected if row["locus"] == "f80v.21")
    f80_cross = cross_by["f80v.21"]
    check(
        f80_cross["zl3b_clean"] == "tar kain okal y rchey qokal olor aiin okal otam"
        and f80_cross["it2a_clean"] == "tor kain okal yrchey qokal olor aiin okal otam"
        and f80_cross["rf1b_clean"] == "t r kain okal y rchey qokal oloraiin okal otam",
        "f80v.21 three-reader source line",
    )
    check(
        f80_expected["right_surface"] == "rchey"
        and f80_expected["right_materia_preparation_head"] == 1
        and f80_expected["base_context_class"] == "Y_MEDIAL_LEFT_CLOSE"
        and f80_expected["context_class"] == "Y_MEDIAL_RIGHT_REFERENCE_MATERIA"
        and f80_expected["it2a_boundary_class"] == "MERGE_RIGHT"
        and f80_expected["it2a_matched_surface"] == "yrchey"
        and f80_expected["rf1b_boundary_class"] == "SEPARATE"
        and f80_expected["working_render_de"] == "hierzu: trocken gebundene Wurzeldroge, Form I",
        "f80v.21 materia-right override",
    )
    f80 = read_tsv(ART / "F80V21_WORKING_TRANSLATION.tsv")
    f80_ok = len(f80) == 1
    if f80:
        row = f80[0]
        full = row["working_line_translation_de"]
        f80_ok &= (
            row["locus"] == "f80v.21" and row["local_span"] == "okal y rchey"
            and row["base_context_class"] == "Y_MEDIAL_LEFT_CLOSE"
            and row["final_context_class"] == "Y_MEDIAL_RIGHT_REFERENCE_MATERIA"
            and row["working_local_render_de"] == "hierzu: trocken gebundene Wurzeldroge, Form I"
            and row["v36_unknown_tokens"] == "0"
            and all(term in full for term in (
                "Kalte Drogenfraktion I", "heiß, Grad II", "Ansatzrohstoff Klasse I",
                "hierzu: trocken gebundene Wurzeldroge, Form I", "Zutat", "Menge III",
                "ein Maß kalten Ansatzes",
            ))
            and "[" not in full and "?" not in full and not FILLER.search(full)
        )
    check(f80_ok, "f80v.21 complete concrete root-drug translation")

    base_coverage = read_tsv(ROOT / BASE_COVERAGE)
    final_coverage = read_tsv(ART / "ALL_LINE_CONCRETE_COVERAGE_V36.tsv")
    base_cov_by = {row["locus"]: row for row in base_coverage}
    final_cov_by = {row["locus"]: row for row in final_coverage}
    check(
        len(base_cov_by) == len(final_cov_by) == len(by_line) == 4128
        and set(base_cov_by) == set(final_cov_by) == set(by_line),
        "4128-line V35/V36/raw identity",
    )
    non_y_count = 0
    y_count = 0
    preservation_ok = True
    non_y_before: list[tuple[object, ...]] = []
    non_y_after: list[tuple[object, ...]] = []
    source_fields = (
        "page", "locus", "section", "language", "hand", "token_count",
        "reader_exact_tokens", "split_normalized_tokens", "all_three_present",
        "all_present_exact", "zl3b_line",
    )
    for before in base_coverage:
        locus = before["locus"]
        line = by_line[locus]
        after = final_cov_by[locus]
        preservation_ok &= all(before[field] == after[field] for field in source_fields)
        before_columns = [split_pipe(before[field]) for field in ("token_glosses_de", "gloss_sources", "scope_states")]
        after_columns = [split_pipe(after[field]) for field in ("token_glosses_de", "gloss_sources", "scope_states")]
        preservation_ok &= all(len(column) == len(line) for column in (*before_columns, *after_columns))
        expected_y_here = 0
        for index, token in enumerate(line):
            if token["eva"] != "y":
                non_y_count += 1
                non_y_before.append((
                    locus, index + 1, token["eva"], before_columns[0][index],
                    before_columns[1][index], before_columns[2][index],
                ))
                non_y_after.append((
                    locus, index + 1, token["eva"], after_columns[0][index],
                    after_columns[1][index], after_columns[2][index],
                ))
                preservation_ok &= all(before_columns[column][index] == after_columns[column][index] for column in range(3))
                continue
            y_count += 1
            expected_y_here += 1
            occurrence = expected_by[(locus, token["token_index"])]
            preservation_ok &= before_columns[0][index] == "[y:?]"
            preservation_ok &= before_columns[1][index] == "OPEN" and before_columns[2][index] == "UNKNOWN_SURFACE"
            preservation_ok &= after_columns[0][index] == occurrence["token_gloss_de"]
            preservation_ok &= after_columns[1][index] == "GDT659:" + str(occurrence["context_class"])
            wanted_state = "KNOWN_CONTEXT_LICENSED" if occurrence["all_reader_separate_y"] else "READER_BOUNDARY_UNSTABLE"
            preservation_ok &= after_columns[2][index] == wanted_state
        before_pairs = list(zip(split_compact(before["unknown_ordinals"]), split_compact(before["unknown_surfaces"])))
        after_pairs = list(zip(split_compact(after["unknown_ordinals"]), split_compact(after["unknown_surfaces"])))
        preservation_ok &= after_pairs == [pair for pair in before_pairs if pair[1] != "y"]
        preservation_ok &= int(after["known_tokens"]) - int(before["known_tokens"]) == expected_y_here
        preservation_ok &= int(before["unknown_tokens"]) - int(after["unknown_tokens"]) == expected_y_here
        preservation_ok &= int(after["context_licensed_tokens"]) == after_columns[2].count("KNOWN_CONTEXT_LICENSED")
        preservation_ok &= int(after["ambiguous_tokens"]) == after_columns[2].count("AMBIGUOUS_ACTIVE_RIVAL")
        preservation_ok &= int(after["reader_unstable_tokens"]) == after_columns[2].count("READER_BOUNDARY_UNSTABLE")
    check(
        preservation_ok and non_y_count == 32069 and y_count == 270
        and non_y_before == non_y_after
        and canonical_hash(non_y_before) == canonical_hash(non_y_after),
        "all 32,069 non-y projections and their canonical hash are unchanged; exactly 270 y replaced",
    )
    non_y_projection_sha256 = canonical_hash(non_y_before)

    base_complete = read_tsv(ROOT / BASE_COMPLETE)
    base_one = read_tsv(ROOT / BASE_ONE)
    complete = read_tsv(ART / "COMPLETE_PASSAGES_V36.tsv")
    one = read_tsv(ART / "ONE_UNKNOWN_PASSAGES_V36.tsv")
    glossary = read_tsv(ART / "V36_WORKING_TOKEN_GLOSSARY.tsv")
    check(coverage_metrics(base_coverage, base_complete, base_one, len(base_gloss_rows)) == BASE_METRICS, "recomputed V35 metrics")
    check(coverage_metrics(final_coverage, complete, one, len(glossary)) == FINAL_METRICS, "recomputed V36 metrics")
    check(
        {row["locus"] for row in complete} == {
            row["locus"] for row in final_coverage
            if int(row["token_count"]) > 1 and int(row["unknown_tokens"]) == 0
        }
        and {row["locus"] for row in one} == {
            row["locus"] for row in final_coverage
            if int(row["known_tokens"]) >= 1 and int(row["unknown_tokens"]) == 1
        },
        "complete and one-hole tables independently derived",
    )
    check(
        all(int(row["strict_complete"]) == int(
            int(row["ambiguous_tokens"]) == 0 and int(row["reader_unstable_tokens"]) == 0
            and int(row["all_present_exact"]) == 1
        ) for row in complete)
        and all(int(row["strict_eligible"]) == int(
            int(row["ambiguous_tokens"]) == 0 and int(row["reader_unstable_tokens"]) == 0
            and int(row["all_present_exact"]) == 1
        ) for row in one),
        "strict complete/one-hole flags recomputed",
    )
    newly_complete = read_tsv(ART / "NEWLY_COMPLETED_LINES.tsv")
    check(
        len(newly_complete) == 8 and {row["locus"] for row in newly_complete} == NEW_COMPLETE
        and {row["locus"] for row in complete} - {row["locus"] for row in base_complete} == NEW_COMPLETE,
        "exact eight newly completed lines",
    )
    newly_one = read_tsv(ART / "NEWLY_EXPOSED_ONE_HOLE_LINES.tsv")
    derived_new_one = {row["locus"] for row in one} - {row["locus"] for row in base_one}
    check(
        len(newly_one) == len(derived_new_one) == 17
        and {row["locus"] for row in newly_one} == derived_new_one,
        "exact 17 newly exposed one-hole lines",
    )
    check(
        all(
            row["proposed_default_de"] == f"[{row['unknown_surface']}:?]"
            and row["proposal_basis"] == "NEWLY_EXPOSED_BY_GDT659_NO_NEW_CARD"
            and row["proposal_strength"] == "OPEN"
            for row in newly_one
        ),
        "new one-holes remain opaque; no new substring or prefix reading",
    )

    glossary_by = {row["surface"]: row for row in glossary}
    check(
        len(glossary) == len(glossary_by) == 495 and glossary_by == base_gloss
        and "y" not in glossary_by,
        "V35 glossary preserved exactly; no global y surface row",
    )

    base_dictionary = read_tsv(ROOT / BASE_DICTIONARY)
    dictionary = read_tsv(ART / "WORKING_DICTIONARY_V36.tsv")
    appended = dictionary[len(base_dictionary):]
    check(
        len(base_dictionary) == 574 and len(dictionary) == 582 and dictionary[:574] == base_dictionary,
        "V35 dictionary is exact V36 prefix",
    )
    check(
        len(appended) == 8
        and [row["entry"] for row in appended] == ["y@" + role for role in FINAL_ORDER]
        and all(
            row["kind"] == "CONTEXTUAL_NAKED_Y_CARD"
            and row["status"] == "NEW_V36_CONTEXT_CARD_NOT_GLOBAL_LEXEME" for row in appended
        )
        and not any(row["entry"] == "y" for row in dictionary)
        and all(not FILLER.search(" ".join(row.values())) for row in appended),
        "eight contextual dictionary cards and no global y card",
    )

    rounds = read_tsv(ART / "ROUND_COVERAGE_COUNTS.tsv")
    round_expected = (
        ("V35", "BASE", 574, *tuple(BASE_METRICS.values())),
        ("V36", "8_NAKED_Y_CONTEXT_CARDS_270_POSITIONS", 582, *tuple(FINAL_METRICS.values())),
    )
    round_actual = tuple((
        row["version"], row["added_context_card"], int(row["dictionary_entries"]),
        *tuple(int(row[field]) for field in BASE_METRICS),
    ) for row in rounds)
    check(round_actual == round_expected, "V35/V36 coverage round packet", repr(round_actual))

    affected = read_tsv(ART / "Y_AFFECTED_LINE_TRANSLATIONS.tsv")
    affected_by = {row["locus"]: row for row in affected}
    y_by_locus: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in expected:
        y_by_locus[str(row["locus"])].append(row)
    affected_ok = len(affected) == len(affected_by) == 257 and set(affected_by) == set(y_by_locus)
    for locus, occurrences in y_by_locus.items():
        row = affected_by.get(locus, {})
        ordered = sorted(occurrences, key=lambda item: int(item["ordinal"]))
        affected_ok &= (
            row.get("y_occurrences") == str(len(ordered))
            and row.get("y_ordinals") == "|".join(str(item["ordinal"]) for item in ordered)
            and row.get("context_classes") == "|".join(str(item["context_class"]) for item in ordered)
            and row.get("zl3b_line") == final_cov_by[locus]["zl3b_line"]
            and row.get("v35_token_glosses_de") == base_cov_by[locus]["token_glosses_de"]
            and row.get("v36_token_glosses_de") == final_cov_by[locus]["token_glosses_de"]
            and row.get("base_unknown_tokens") == base_cov_by[locus]["unknown_tokens"]
            and row.get("v36_unknown_tokens") == final_cov_by[locus]["unknown_tokens"]
            and not FILLER.search(row.get("v36_working_translation_de", ""))
        )
    check(affected_ok, "257 affected-line translations retain source and contextual classes")
    check(
        bool(f80) and affected_by["f80v.21"]["v36_working_translation_de"] == f80[0]["working_line_translation_de"],
        "f80v.21 full-line translation packet identity",
    )

    practical_values = [row["v36_working_translation_de"] for row in affected]
    practical_values.extend(row["working_translation_de"] for row in complete)
    practical_values.extend(row["proposed_complete_translation_de"] for row in one)
    spoken_structure = re.compile(
        r"Eintrag abgeschlossen|Eintragsteil abgeschlossen|Labelgliederung|Labelschluss",
        re.IGNORECASE,
    )
    check(
        all(not spoken_structure.search(value) and "; ;" not in value for value in practical_values),
        "practical renderer keeps close/label structure silent and avoids double separators",
    )
    label_only_loci = {
        str(row["locus"]) for row in expected if row["label_subrole"] == "LABEL_ONLY"
    }
    check(
        len(label_only_loci) == 9
        and all(
            affected_by[locus]["v36_working_translation_de"] == "[Beschriftungszeichen]"
            for locus in label_only_loci
        )
        and "Labelgliederung" not in affected_by["f77v.1"]["v36_working_translation_de"]
        and affected_by["f99r.2"]["v36_working_translation_de"].endswith("."),
        "LABEL_ONLY is bracketed; LABEL_INTERNAL is silent; LABEL_CLOSE is punctuation",
    )

    result = json.loads((ART / "RESULT.json").read_text(encoding="utf-8"))
    core = {key: value for key, value in result.items() if key != "content_sha256"}
    check(
        result.get("schema") == RESULT_SCHEMA and result.get("experiment_id") == "GDT659"
        and result.get("status") == STATUS,
        "result identity/status",
    )
    check(result.get("content_sha256") == canonical_hash(core), "result canonical content hash")
    check(
        result.get("guard", {}).get("token_query") == token_stats
        and result.get("guard", {}).get("cross_query") == cross_stats,
        "result guarded-query packet",
    )
    check(
        result.get("guard", {}).get("allowed_pages") == 179
        and result.get("guard", {}).get("f1r") == "EXCLUDED_BY_EXACT_ALLOWLIST"
        and result.get("guard", {}).get("f84") == result.get("guard", {}).get("f84r") == "FORBIDDEN"
        and result.get("guard", {}).get("new_pages") == result.get("guard", {}).get("new_images") == 0,
        "result forbidden-page/image ceiling",
    )
    check(
        result.get("census") == {
            "naked_y_positions": 270, "naked_y_lines": 257, "naked_y_pages": 125,
            "positions": {"BOS": 60, "EOS": 34, "MEDIAL": 167, "ONLY": 9},
            "token_kinds": {"L": 11, "P": 259}, "all_reader_separate_y": 83,
            "full_line_all_present_exact_y_positions": 25,
        },
        "result census packet",
    )
    context_result = result.get("context_cards", {})
    check(
        context_result.get("accepted_cards") == 8
        and context_result.get("base_classes") == dict(sorted(BASE_CLASSES.items()))
        and context_result.get("final_classes") == dict(sorted(FINAL_CLASSES.items()))
        and context_result.get("label_precedence_occurrences") == 11
        and context_result.get("label_subroles") == {"LABEL_CLOSE": 1, "LABEL_INTERNAL": 1, "LABEL_ONLY": 9}
        and context_result.get("materia_subtype_positions") == 13
        and context_result.get("materia_direction_overrides") == 1
        and context_result.get("all_positions_context_known") == 270
        and context_result.get("global_y_lexeme_added") is False,
        "result hierarchy packet",
    )
    check(
        result.get("coverage", {}).get("base") == BASE_METRICS
        and result.get("coverage", {}).get("final") == FINAL_METRICS,
        "result coverage metrics",
    )
    check(
        result.get("coverage", {}).get("affected_lines") == 257
        and result.get("coverage", {}).get("newly_completed_lines") == 8
        and set(result.get("coverage", {}).get("newly_completed_loci", [])) == NEW_COMPLETE
        and result.get("coverage", {}).get("newly_exposed_one_hole_lines") == 17
        and result.get("coverage", {}).get("non_y_token_positions_unchanged") == 32069
        and result.get("coverage", {}).get("non_y_exactly_unchanged") is True
        and result.get("coverage", {}).get("non_y_before_sha256") == non_y_projection_sha256
        and result.get("coverage", {}).get("non_y_after_sha256") == non_y_projection_sha256
        and non_y_projection_sha256 == "dbd66a18742b9e3d9532095c9d5d9610051b3043dfa8a8e2e0e2f076ba9aaeef",
        "result coverage deltas",
    )
    check(
        result.get("f80v21", {}).get("final_context_class") == "Y_MEDIAL_RIGHT_REFERENCE_MATERIA"
        and result.get("f80v21", {}).get("working_render_de") == "hierzu: trocken gebundene Wurzeldroge, Form I"
        and result.get("f80v21", {}).get("line_complete_v36") is True,
        "result f80v.21 packet",
    )
    check(
        result.get("supporting_inputs") == {"historical_analogy_rows": 6, "manual_context_rows": 38},
        "result supporting-input counts",
    )
    working = result.get("working_dictionary", {})
    check(
        working.get("v35_entries") == 574 and working.get("v36_entries") == 582
        and working.get("added_context_entries") == 8
        and working.get("v35_glossary_surfaces") == 495
        and working.get("v36_glossary_surfaces") == 495
        and working.get("v35_prefix_sha256") == canonical_hash(base_dictionary)
        and working.get("v36_sha256") == canonical_hash(dictionary),
        "result dictionary/glossary metrics and canonical hashes",
    )

    inputs = result.get("inputs", {})
    outputs = result.get("outputs", {})
    check(
        bool(inputs) and all(
            not Path(path).is_absolute() and (ROOT / path).is_file()
            and digest == sha256(ROOT / path) for path, digest in inputs.items()
        ),
        "result input provenance hashes",
    )
    expected_output_paths = {str(BASE / "artifacts" / name) for name in OUTPUT_NAMES}
    check(
        set(outputs) == expected_output_paths and all(
            not Path(path).is_absolute() and (ROOT / path).is_file()
            and digest == sha256(ROOT / path) for path, digest in outputs.items()
        ),
        "result output hashes",
    )
    replay_paths = result.get("determinism_contract", {}).get("replay_files", [])
    check(
        result.get("determinism_contract", {}).get("builder_supports_artifact_dir_cli") is True
        and set(replay_paths) == expected_output_paths | {str(BASE / "artifacts/RESULT.json")},
        "result determinism contract",
    )

    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    check(
        manifest.get("experiment_id") == "GDT659" and manifest.get("slug") == "naked_y_local_reference"
        and manifest.get("sealed_data") == {"f84": "FORBIDDEN", "f84r": "FORBIDDEN"}
        and manifest.get("commands") == {
            "run": f"python3 {BASE}/src/run.py", "validate": f"python3 {BASE}/src/validate.py"
        },
        "manifest identity, commands and seals",
    )

    safe_pages = True
    for name in (*OUTPUT_NAMES, "MANUAL_Y_CONTEXT_AUDIT.tsv"):
        for row in read_tsv(ART / name):
            page = row.get("page", "")
            locus_page = row.get("locus", "").split(".", 1)[0]
            safe_pages &= page != "f1r" and not page.startswith("f84")
            safe_pages &= locus_page != "f1r" and not locus_page.startswith("f84")
    check(safe_pages, "no f1r/f84/f84r in data-bearing artifacts")

    semantic_files = (
        "Y_CONTEXT_CARDS.tsv", "Y_OCCURRENCE_CENSUS.tsv", "Y_AFFECTED_LINE_TRANSLATIONS.tsv",
        "F80V21_WORKING_TRANSLATION.tsv", "V36_WORKING_TOKEN_GLOSSARY.tsv",
        "WORKING_DICTIONARY_V36.tsv", "ALL_LINE_CONCRETE_COVERAGE_V36.tsv",
        "COMPLETE_PASSAGES_V36.tsv", "ONE_UNKNOWN_PASSAGES_V36.tsv",
        "NEWLY_COMPLETED_LINES.tsv", "NEWLY_EXPOSED_ONE_HOLE_LINES.tsv",
        "MANUAL_Y_CONTEXT_AUDIT.tsv", "HISTORICAL_ENTRY_MARKER_ANALOGIES.tsv",
    )
    filler_hits = [name for name in semantic_files if FILLER.search((ART / name).read_text(encoding="utf-8"))]
    check(not filler_hits, "no generic work/filler prose in semantic artifacts", repr(filler_hits))

    builder_source = RUN.read_text(encoding="utf-8")
    inherited_guess_code = re.compile(
        r"\bdef\s+suggest_unknown\b|VISIBLE_(?:MULTI|SINGLE)_FIELD_COMPOSITION|"
        r"surface\.endswith\s*\(|surface\.startswith\s*\(",
        re.IGNORECASE,
    )
    check(
        not inherited_guess_code.search(builder_source),
        "builder has no suffix/prefix heuristic for newly exposed one-holes",
    )

    # This is intentionally the final validation action.
    try:
        with tempfile.TemporaryDirectory(prefix="gdt659_validator_replay_") as temporary:
            replay = Path(temporary)
            done = subprocess.run(
                [sys.executable, str(RUN), "--artifact-dir", str(replay)], cwd=ROOT,
                text=True, capture_output=True, check=False,
            )
            check(done.returncode == 0, "builder tempdir CLI replay exits zero", done.stderr or done.stdout)
            expected_names = set(OUTPUT_NAMES) | {"RESULT.json"}
            actual_names = {path.name for path in replay.iterdir() if path.is_file()}
            check(actual_names == expected_names, "builder replay output set", repr(sorted(actual_names)))
            replay_ok = done.returncode == 0 and actual_names == expected_names
            if replay_ok:
                replay_ok = all((ART / name).read_bytes() == (replay / name).read_bytes() for name in expected_names)
            check(replay_ok, "byte-identical external builder replay")
    except Exception as exc:
        check(False, "builder tempdir replay", f"{type(exc).__name__}: {exc}")


def main() -> int:
    passed: list[str] = []
    issues: list[str] = []

    def check(ok: object, name: str, detail: str = "") -> None:
        if ok:
            passed.append(name)
        else:
            issues.append(f"{name}: {detail or 'condition failed'}")

    try:
        # ---- Source-first guarded recensus; no GDT659 artifact/import above. ----
        allow_rows = read_tsv(ROOT / ALLOW)
        pages = {row["page"] for row in allow_rows}
        check(len(allow_rows) == len(pages) == 179, "179 unique inherited allow-list pages")
        check(
            "f1r" not in pages and not any(page.startswith("f84") for page in pages),
            "f1r excluded and f84/f84r forbidden before raw query",
        )
        token_rows, token_stats = guarded_query(
            TOKENS, pages, "page,locus,token_index,eva,kind,section,language,hand"
        )
        cross_rows, cross_stats = guarded_query(
            CROSS, pages,
            "page,locus,all_three_present,all_present_exact,zl3b_clean,it2a_clean,rf1b_clean",
        )
        expected_token_stats = {"selected": 32339, "skipped_forbidden": 709, "skipped_not_allowed": 5940}
        expected_cross_stats = {"selected": 4137, "skipped_forbidden": 98, "skipped_not_allowed": 1151}
        check(
            len(token_rows) == 32339 and token_stats == expected_token_stats,
            "guarded raw token query", repr(token_stats),
        )
        check(
            len(cross_rows) == 4137 and cross_stats == expected_cross_stats,
            "guarded raw cross-reader query", repr(cross_stats),
        )
        raw_by_line: dict[str, list[dict[str, str]]] = defaultdict(list)
        for row in token_rows:
            raw_by_line[row["locus"]].append(row)
        cross_by = {row["locus"]: row for row in cross_rows}
        raw_identity = len(raw_by_line) == 4128 and set(raw_by_line) <= set(cross_by)
        for locus, line in raw_by_line.items():
            line.sort(key=lambda row: int(row["token_index"]))
            raw_identity &= " ".join(row["eva"] for row in line) == cross_by[locus]["zl3b_clean"]
        check(raw_identity, "guarded token/line source identity")

        # Only after all raw gates are complete may artifacts be read or the
        # builder CLI eventually be executed.
        validate_release(check, token_rows, cross_rows, token_stats, cross_stats, pages)
    except Exception as exc:
        issues.append(f"validator exception: {type(exc).__name__}: {exc}")

    validation = {
        "schema": "GDT659_VALIDATION_V1", "experiment_id": "GDT659",
        "status": "PASS" if not issues else "FAIL",
        "source_first_guarded_queries": True, "builder_imported": False,
        "external_tempdir_byte_replay": not issues,
        "checks_passed": len(passed), "checks_failed": len(issues),
        "passed": passed, "issues": issues,
    }
    VALIDATION.write_text(
        json.dumps(validation, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    if issues:
        print(f"GDT659 validation FAIL: {len(issues)} issue(s), {len(passed)} checks passed")
        for issue in issues:
            print(f"- {issue}")
        return 1
    print(f"GDT659 validation PASS: {len(passed)} checks")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
