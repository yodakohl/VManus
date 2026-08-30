#!/usr/bin/env python3
"""Build GDT659: deterministic contextual cards for every naked ZL3b y."""
from __future__ import annotations

import argparse
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
from typing import Iterable

sys.dont_write_bytecode = True


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
BASE_REL = Path("experiments/yolo/gdt659_naked_y_local_reference")
ART = ROOT / BASE_REL / "artifacts"
G658 = Path("experiments/yolo/gdt658_four_residual_concrete_completion")
TOKENS_REL = Path("transcription/voynich_zl3b_tokens.tsv")
CROSS_REL = Path("transcription/voynich_cross_transcription_lines.tsv")
STATUS = "PASS_270_NAKED_Y_CONTEXT_CARDS__V36"
F80V21_TRANSLATION_DE = (
    "Kalte Drogenfraktion I; heiß, Grad II; Ansatzrohstoff Klasse I, heiß am Gradanfang; "
    "hierzu: trocken gebundene Wurzeldroge, Form I; Rohstoff Klasse I, heiß am Gradanfang; "
    "Zutat, Menge III; Ansatzrohstoff Klasse I, heiß am Gradanfang; ein Maß kalten Ansatzes."
)
PRACTICAL_STRUCTURAL_WORDS = (
    "Eintrag abgeschlossen",
    "Eintragsteil abgeschlossen",
    "Labelgliederung",
    "Labelschluss",
)

OUTPUT_NAMES = (
    "PAGE_ALLOWLIST.tsv",
    "Y_CONTEXT_CARDS.tsv",
    "Y_OCCURRENCE_CENSUS.tsv",
    "Y_CONTEXT_CLASS_SUMMARY.tsv",
    "Y_DIMENSION_PROFILE.tsv",
    "Y_PAGE_COUNTS.tsv",
    "Y_READER_BOUNDARY_AUDIT.tsv",
    "Y_READER_BOUNDARY_SUMMARY.tsv",
    "Y_NEIGHBOR_ATLAS.tsv",
    "Y_NEIGHBOR_SUMMARY.tsv",
    "Y_AFFECTED_LINE_TRANSLATIONS.tsv",
    "F80V21_WORKING_TRANSLATION.tsv",
    "V36_WORKING_TOKEN_GLOSSARY.tsv",
    "WORKING_DICTIONARY_V36.tsv",
    "ALL_LINE_CONCRETE_COVERAGE_V36.tsv",
    "COMPLETE_PASSAGES_V36.tsv",
    "ONE_UNKNOWN_PASSAGES_V36.tsv",
    "NEWLY_COMPLETED_LINES.tsv",
    "NEWLY_EXPOSED_ONE_HOLE_LINES.tsv",
    "ROUND_COVERAGE_COUNTS.tsv",
)

BASE_CONTEXT_ORDER = (
    "Y_ONLY_DIVIDER",
    "Y_BOS_ENTRY",
    "Y_EOS_CLOSE",
    "Y_MEDIAL_RIGHT_REFERENCE",
    "Y_MEDIAL_LEFT_CLOSE",
    "Y_MEDIAL_BIDIRECTIONAL_HINGE",
    "Y_MEDIAL_UNRESOLVED_HINGE",
)
FINAL_CONTEXT_ORDER = (
    "Y_LABEL_SIGLUM",
    "Y_BOS_ENTRY",
    "Y_EOS_CLOSE",
    "Y_MEDIAL_RIGHT_REFERENCE",
    "Y_MEDIAL_LEFT_CLOSE",
    "Y_MEDIAL_BIDIRECTIONAL_HINGE",
    "Y_MEDIAL_UNRESOLVED_HINGE",
    "Y_MEDIAL_RIGHT_REFERENCE_MATERIA",
)

CONTEXT_SPECS = {
    "Y_LABEL_SIGLUM": {
        "structural_tag": "NAKED_Y|TOKEN_KIND=L|ROLE=LABEL_SIGLUM",
        "selection_rule": "token kind L overrides positional P-text semantics; subrole is ONLY, INTERNAL or CLOSE",
        "token_gloss_de": "Beschriftungszeichen",
        "working_render_de": "[Beschriftungszeichen] / ; / .",
        "live_rival_de": "bloßes Form- oder Schlusszeichen innerhalb des Labels",
    },
    "Y_BOS_ENTRY": {
        "structural_tag": "NAKED_Y|TOKEN_KIND=P|POSITION=BOS|ROLE=ENTRY_HEAD",
        "selection_rule": "P token at physical-line beginning",
        "token_gloss_de": "Eintrag:",
        "working_render_de": "Eintrag:",
        "live_rival_de": "hierzu / zu derselben Droge, falls ein lokaler Antezedent sichtbar wird",
    },
    "Y_EOS_CLOSE": {
        "structural_tag": "NAKED_Y|TOKEN_KIND=P|POSITION=EOS|ROLE=ENTRY_CLOSE",
        "selection_rule": "P token at physical-line end",
        "token_gloss_de": "Eintrag abgeschlossen",
        "working_render_de": ".",
        "live_rival_de": "postponierter Bezug auf den linken Stoff",
    },
    "Y_MEDIAL_RIGHT_REFERENCE": {
        "structural_tag": "NAKED_Y|TOKEN_KIND=P|POSITION=MEDIAL|ATTACHMENT=RIGHT",
        "selection_rule": "observed ZL sister y+RIGHT and no observed LEFT+y sister",
        "token_gloss_de": "hierzu:",
        "working_render_de": "hierzu:",
        "live_rival_de": "neuer Unterposten statt deiktischer Bezug",
    },
    "Y_MEDIAL_LEFT_CLOSE": {
        "structural_tag": "NAKED_Y|TOKEN_KIND=P|POSITION=MEDIAL|ATTACHMENT=LEFT",
        "selection_rule": "observed ZL sister LEFT+y and no observed y+RIGHT sister",
        "token_gloss_de": "Eintragsteil abgeschlossen",
        "working_render_de": ";",
        "live_rival_de": "rechte Eintragsreferenz bei einem konkreten Folgekörper",
    },
    "Y_MEDIAL_BIDIRECTIONAL_HINGE": {
        "structural_tag": "NAKED_Y|TOKEN_KIND=P|POSITION=MEDIAL|ATTACHMENT=BOTH",
        "selection_rule": "both observed ZL sisters LEFT+y and y+RIGHT",
        "token_gloss_de": "; hierzu:",
        "working_render_de": "hierzu:",
        "live_rival_de": "nur linkes Formende oder nur rechter Eintragskopf",
    },
    "Y_MEDIAL_UNRESOLVED_HINGE": {
        "structural_tag": "NAKED_Y|TOKEN_KIND=P|POSITION=MEDIAL|ATTACHMENT=UNRESOLVED",
        "selection_rule": "neither LEFT+y nor y+RIGHT is observed as a ZL whole",
        "token_gloss_de": "hierzu:",
        "working_render_de": "hierzu:",
        "live_rival_de": "gelernter lokaler Trenner ohne deiktische Funktion",
    },
    "Y_MEDIAL_RIGHT_REFERENCE_MATERIA": {
        "structural_tag": "NAKED_Y|TOKEN_KIND=P|POSITION=MEDIAL|ROLE=RIGHT_REFERENCE|RIGHT_CLASS=MATERIA_PREPARATION",
        "selection_rule": "known V35 right Materia/preparation head with mechanical RIGHT attachment; plus explicit f80v.21 IT2a y+rchey exception",
        "token_gloss_de": "hierzu:",
        "working_render_de": "hierzu: rechter Kopf",
        "live_rival_de": "plain mechanical right reference; f80v.21 retains its recorded LEFT-close rival",
    },
}

MATERIA_RE = re.compile(
    r"wurzel|droge|drogen|rohstoff|arznei|samen|holz|blatt|blüt|frucht|zutat|"
    r"pflanzen|pulver|feuchtgut|trockengut|stoff|material|präparat|ansatz|zubereitung|\bgut\b",
    re.IGNORECASE,
)

EXPECTED_BASE_CLASSES = {
    "Y_ONLY_DIVIDER": 9,
    "Y_BOS_ENTRY": 60,
    "Y_EOS_CLOSE": 34,
    "Y_MEDIAL_RIGHT_REFERENCE": 43,
    "Y_MEDIAL_LEFT_CLOSE": 36,
    "Y_MEDIAL_BIDIRECTIONAL_HINGE": 50,
    "Y_MEDIAL_UNRESOLVED_HINGE": 38,
}
EXPECTED_FINAL_CLASSES = {
    "Y_LABEL_SIGLUM": 11,
    "Y_BOS_ENTRY": 60,
    "Y_EOS_CLOSE": 33,
    "Y_MEDIAL_RIGHT_REFERENCE": 31,
    "Y_MEDIAL_LEFT_CLOSE": 35,
    "Y_MEDIAL_BIDIRECTIONAL_HINGE": 49,
    "Y_MEDIAL_UNRESOLVED_HINGE": 38,
    "Y_MEDIAL_RIGHT_REFERENCE_MATERIA": 13,
}
EXPECTED_POSITIONS = {"BOS": 60, "MEDIAL": 167, "EOS": 34, "ONLY": 9}
EXPECTED_KINDS = {"P": 259, "L": 11}
EXPECTED_READER = {
    "IT2a": {"SEPARATE": 107, "MERGE_RIGHT": 81, "MERGE_LEFT": 35, "MERGE_BOTH": 3, "VARIANT_OTHER": 44},
    "RF1b": {"SEPARATE": 168, "MERGE_RIGHT": 47, "MERGE_LEFT": 22, "MERGE_BOTH": 3, "VARIANT_OTHER": 30},
}


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


def parse_compact_pipe(value: str) -> list[str]:
    return [] if value in {"", "NONE"} else value.split("|")


def guarded_query(path: Path, pages: set[str], columns: str) -> tuple[list[dict[str, str]], dict[str, int]]:
    command = [str(ROOT / "vmanus-exp"), "query-tsv", str(path), "--selector", "page"]
    for page in sorted(pages):
        command.extend(("--allow", page))
    command.extend(("--columns", columns, "--forbid-prefix", "f84", "--forbid-prefix", "f84r"))
    completed = subprocess.run(command, cwd=ROOT, check=True, text=True, capture_output=True)
    rows = list(csv.DictReader(io.StringIO(completed.stdout), delimiter="\t"))
    stats_lines = [line for line in completed.stderr.splitlines() if line.startswith("GUARD_STATS ")]
    if len(stats_lines) != 1:
        raise RuntimeError("guarded query did not emit exactly one statistics line")
    stats = json.loads(stats_lines[0].removeprefix("GUARD_STATS "))
    if int(stats["selected"]) != len(rows):
        raise RuntimeError("guarded query selected count differs from parsed rows")
    return rows, {key: int(value) for key, value in stats.items()}


def line_position(ordinal: int, length: int) -> str:
    if length == 1:
        return "ONLY"
    if ordinal == 1:
        return "BOS"
    if ordinal == length:
        return "EOS"
    return "MEDIAL"


def base_context_class(position: str, left_count: int, right_count: int) -> str:
    if position == "ONLY":
        return "Y_ONLY_DIVIDER"
    if position == "BOS":
        return "Y_BOS_ENTRY"
    if position == "EOS":
        return "Y_EOS_CLOSE"
    if right_count and not left_count:
        return "Y_MEDIAL_RIGHT_REFERENCE"
    if left_count and not right_count:
        return "Y_MEDIAL_LEFT_CLOSE"
    if left_count and right_count:
        return "Y_MEDIAL_BIDIRECTIONAL_HINGE"
    return "Y_MEDIAL_UNRESOLVED_HINGE"


def label_subrole(position: str) -> str:
    return {"ONLY": "LABEL_ONLY", "MEDIAL": "LABEL_INTERNAL", "EOS": "LABEL_CLOSE"}.get(position, "LABEL_ENTRY")


def is_materia_head(surface: str, glossary: dict[str, dict[str, str]]) -> bool:
    return bool(surface in glossary and MATERIA_RE.search(glossary[surface]["working_meaning_de"]))


def candidate_surfaces(words: list[str], index: int) -> dict[str, str]:
    candidates = {"SEPARATE": "y"}
    if index + 1 < len(words):
        candidates["MERGE_RIGHT"] = "y" + words[index + 1]
    if index:
        candidates["MERGE_LEFT"] = words[index - 1] + "y"
    if index and index + 1 < len(words):
        candidates["MERGE_BOTH"] = words[index - 1] + "y" + words[index + 1]
    return candidates


def reader_boundary_assignments(words: list[str], reader_words: list[str]) -> dict[int, tuple[str, str]]:
    """Maximize exact, order-preserving Y boundary matches without reusing reader tokens."""
    y_indices = [index for index, word in enumerate(words) if word == "y"]
    n, m = len(y_indices), len(reader_words)
    impossible = (-10**9, -10**9)
    score = [[impossible for _ in range(m + 1)] for _ in range(n + 1)]
    back: list[list[tuple[int, int, str, str] | None]] = [[None for _ in range(m + 1)] for _ in range(n + 1)]
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
                back[i][j + 1] = (i, j, "SKIP_READER_TOKEN", "")
            if i < n and j < m:
                for category, surface in candidate_surfaces(words, y_indices[i]).items():
                    if reader_words[j] != surface:
                        continue
                    proposed = (score[i][j][0] + 1, score[i][j][1] + rank[category])
                    if proposed > score[i + 1][j + 1]:
                        score[i + 1][j + 1] = proposed
                        back[i + 1][j + 1] = (i, j, category, surface)
    result: list[tuple[str, str] | None] = [None] * n
    i, j = n, m
    while i or j:
        step = back[i][j]
        if step is None:
            raise RuntimeError("reader boundary alignment has no traceback")
        previous_i, previous_j, category, surface = step
        if i == previous_i + 1:
            result[previous_i] = (category, surface)
        i, j = previous_i, previous_j
    if any(item is None for item in result):
        raise RuntimeError("reader boundary alignment left an occurrence unassigned")
    return {index: result[ordinal] for ordinal, index in enumerate(y_indices)}  # type: ignore[index]


def metrics(
    coverage: list[dict[str, object]], one_unknown: list[dict[str, object]],
    complete: list[dict[str, object]], glossary: list[dict[str, object]],
) -> dict[str, int]:
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


def context_token_gloss(occurrence: dict[str, object]) -> str:
    if occurrence["context_class"] != "Y_LABEL_SIGLUM":
        return CONTEXT_SPECS[str(occurrence["context_class"])]["token_gloss_de"]
    return {
        "LABEL_ONLY": "Beschriftungszeichen",
        "LABEL_INTERNAL": "Labelgliederung",
        "LABEL_CLOSE": "Labelschluss",
        "LABEL_ENTRY": "Labelzeichen",
    }[str(occurrence["label_subrole"])]


def natural_right_meaning(locus: str, surface: str, meaning: str) -> str:
    if locus == "f80v.21" and surface == "rchey":
        return "trocken gebundene Wurzeldroge, Form I"
    return meaning


def render_line(
    locus: str, line: list[dict[str, str]], glosses: list[str], occurrence_by_token: dict[tuple[str, int], dict[str, object]],
) -> str:
    if locus == "f80v.21":
        return F80V21_TRANSLATION_DE
    rendered: list[str] = []
    terminal_close = False
    index = 0
    while index < len(line):
        token = line[index]
        if token["eva"] != "y":
            rendered.append(glosses[index])
            index += 1
            continue
        occurrence = occurrence_by_token[(locus, int(token["token_index"]))]
        context_class = str(occurrence["context_class"])
        if context_class == "Y_LABEL_SIGLUM":
            if occurrence["label_subrole"] == "LABEL_ONLY":
                rendered.append("[Beschriftungszeichen]")
            terminal_close = terminal_close or occurrence["label_subrole"] == "LABEL_CLOSE"
            index += 1
            continue
        if context_class == "Y_BOS_ENTRY" and index + 1 < len(line):
            rendered.append(f"Eintrag: {glosses[index + 1]}")
            index += 2
            continue
        if context_class == "Y_EOS_CLOSE":
            terminal_close = True
            index += 1
            continue
        if context_class == "Y_MEDIAL_LEFT_CLOSE":
            index += 1
            continue
        if index + 1 < len(line):
            right_surface = line[index + 1]["eva"]
            right_meaning = natural_right_meaning(locus, right_surface, glosses[index + 1])
            rendered.append(f"hierzu: {right_meaning}")
            index += 2
            continue
        rendered.append(context_token_gloss(occurrence))
        index += 1
    practical = "; ".join(rendered)
    if terminal_close and practical:
        practical = practical.rstrip("; .") + "."
    return practical


def build(output_dir: Path) -> dict[str, object]:
    output_dir.mkdir(parents=True, exist_ok=True)
    allowlist_source = ROOT / G658 / "artifacts/PAGE_ALLOWLIST.tsv"
    pages = {row["page"] for row in read_tsv(allowlist_source)}
    if len(pages) != 179 or "f1r" in pages or any(page.startswith("f84") for page in pages):
        raise RuntimeError("inherited page allow-list is not the exact safe 179-page panel")

    tokens, token_stats = guarded_query(
        TOKENS_REL, pages, "page,locus,token_index,eva,kind,section,language,hand"
    )
    cross, cross_stats = guarded_query(
        CROSS_REL, pages,
        "page,locus,all_three_present,all_present_exact,zl3b_clean,it2a_clean,rf1b_clean",
    )
    if (len(tokens), len(cross)) != (32339, 4137):
        raise RuntimeError("guarded source census drift")
    cross_by_locus = {row["locus"]: row for row in cross}
    by_line: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in tokens:
        by_line[row["locus"]].append(row)
    for line in by_line.values():
        line.sort(key=lambda row: int(row["token_index"]))
    if len(by_line) != 4128:
        raise RuntimeError("ZL physical-line count drift")
    for locus, line in by_line.items():
        if locus not in cross_by_locus:
            raise RuntimeError(f"cross-reader line missing: {locus}")
        if " ".join(row["eva"] for row in line) != cross_by_locus[locus]["zl3b_clean"]:
            raise RuntimeError(f"ZL token/line text mismatch: {locus}")

    base_dictionary = read_tsv(ROOT / G658 / "artifacts/WORKING_DICTIONARY_V35.tsv")
    base_glossary_rows = read_tsv(ROOT / G658 / "artifacts/V35_WORKING_TOKEN_GLOSSARY.tsv")
    base_glossary = {row["surface"]: row for row in base_glossary_rows}
    base_coverage = read_tsv(ROOT / G658 / "artifacts/ALL_LINE_CONCRETE_COVERAGE_V35.tsv")
    base_complete = read_tsv(ROOT / G658 / "artifacts/COMPLETE_PASSAGES_V35.tsv")
    base_one = read_tsv(ROOT / G658 / "artifacts/ONE_UNKNOWN_PASSAGES_V35.tsv")
    manual_audit = read_tsv(ROOT / BASE_REL / "artifacts/MANUAL_Y_CONTEXT_AUDIT.tsv")
    historical = read_tsv(ROOT / BASE_REL / "artifacts/HISTORICAL_ENTRY_MARKER_ANALOGIES.tsv")
    if (len(base_dictionary), len(base_glossary_rows), len(base_coverage), len(base_complete), len(base_one)) != (574, 495, 4128, 138, 239):
        raise RuntimeError("V35 base dimensions drift")
    if len(manual_audit) != 38 or len(historical) != 6:
        raise RuntimeError("manual/historical input dimensions drift")
    if "y" in base_glossary:
        raise RuntimeError("naked y unexpectedly already present in V35 surface glossary")

    surface_counts = Counter(row["eva"] for row in tokens)
    surface_pages: dict[str, set[str]] = defaultdict(set)
    for row in tokens:
        surface_pages[row["eva"]].add(row["page"])

    occurrence_rows: list[dict[str, object]] = []
    reader_rows: list[dict[str, object]] = []
    base_counts: Counter[str] = Counter()
    final_counts: Counter[str] = Counter()
    position_counts: Counter[str] = Counter()
    kind_counts: Counter[str] = Counter()
    all_reader_position: Counter[str] = Counter()
    reader_category_counts: dict[str, Counter[str]] = {"IT2a": Counter(), "RF1b": Counter()}
    reader_position_counts: dict[tuple[str, str], Counter[str]] = defaultdict(Counter)

    occurrence_id = 0
    for locus, line in sorted(by_line.items()):
        words = [row["eva"] for row in line]
        y_indices = [index for index, word in enumerate(words) if word == "y"]
        if not y_indices:
            continue
        cross_row = cross_by_locus[locus]
        assignments = {
            "IT2a": reader_boundary_assignments(words, cross_row["it2a_clean"].split()),
            "RF1b": reader_boundary_assignments(words, cross_row["rf1b_clean"].split()),
        }
        for index in y_indices:
            occurrence_id += 1
            token = line[index]
            ordinal = index + 1
            position = line_position(ordinal, len(line))
            left = words[index - 1] if index else "<BOS>"
            right = words[index + 1] if index + 1 < len(words) else "<EOS>"
            left_surface = left + "y" if index else ""
            right_surface = "y" + right if index + 1 < len(words) else ""
            left_count = surface_counts[left_surface] if left_surface else 0
            right_count = surface_counts[right_surface] if right_surface else 0
            base_class = base_context_class(position, left_count, right_count)
            it_category, it_surface = assignments["IT2a"][index]
            rf_category, rf_surface = assignments["RF1b"][index]
            context_class = base_class
            materia_subtype = 0
            direction_override = 0
            if token["kind"] == "L":
                context_class = "Y_LABEL_SIGLUM"
            elif (
                position == "MEDIAL"
                and is_materia_head(right, base_glossary)
                and (
                    base_class == "Y_MEDIAL_RIGHT_REFERENCE"
                    or (locus == "f80v.21" and right == "rchey" and it_category == "MERGE_RIGHT")
                )
            ):
                context_class = "Y_MEDIAL_RIGHT_REFERENCE_MATERIA"
                materia_subtype = 1
                direction_override = int(base_class != "Y_MEDIAL_RIGHT_REFERENCE")
            spec = CONTEXT_SPECS[context_class]
            label_role = label_subrole(position) if token["kind"] == "L" else "NONE"
            all_reader_separate = int(it_category == "SEPARATE" and rf_category == "SEPARATE")
            if context_class == "Y_MEDIAL_RIGHT_REFERENCE_MATERIA":
                working_render = "hierzu: " + natural_right_meaning(
                    locus, right, base_glossary[right]["working_meaning_de"]
                )
            elif context_class == "Y_LABEL_SIGLUM":
                working_render = {
                    "LABEL_ONLY": "[Beschriftungszeichen]",
                    "LABEL_INTERNAL": ";",
                    "LABEL_CLOSE": ".",
                    "LABEL_ENTRY": "Eintrag:",
                }[label_role]
            else:
                working_render = spec["working_render_de"]
            row = {
                "occurrence_id": f"G659-Y{occurrence_id:03d}",
                "page": token["page"], "locus": locus, "token_index": token["token_index"],
                "ordinal": ordinal, "line_length": len(line), "position": position,
                "token_kind": token["kind"], "section": token["section"],
                "language": token["language"], "hand": token["hand"],
                "left_surface": left, "right_surface": right,
                "left_fused_surface": left_surface or "NONE", "left_fused_occurrences": left_count,
                "right_fused_surface": right_surface or "NONE", "right_fused_occurrences": right_count,
                "left_v35_known": int(left in base_glossary),
                "left_v35_meaning_de": base_glossary.get(left, {}).get("working_meaning_de", "OPEN"),
                "right_v35_known": int(right in base_glossary),
                "right_v35_meaning_de": base_glossary.get(right, {}).get("working_meaning_de", "OPEN"),
                "right_materia_preparation_head": int(is_materia_head(right, base_glossary)),
                "base_context_class": base_class, "context_class": context_class,
                "materia_subtype": materia_subtype, "direction_override": direction_override,
                "label_subrole": label_role,
                "structural_tag": spec["structural_tag"],
                "token_gloss_de": context_token_gloss({"context_class": context_class, "label_subrole": label_role}),
                "working_render_de": working_render, "live_rival_de": spec["live_rival_de"],
                "all_three_present": cross_row["all_three_present"],
                "line_all_present_exact": cross_row["all_present_exact"],
                "all_reader_separate_y": all_reader_separate,
                "it2a_boundary_class": it_category, "it2a_matched_surface": it_surface or "NONE",
                "rf1b_boundary_class": rf_category, "rf1b_matched_surface": rf_surface or "NONE",
            }
            occurrence_rows.append(row)
            reader_rows.append({
                "occurrence_id": row["occurrence_id"], "page": token["page"], "locus": locus,
                "ordinal": ordinal, "position": position, "token_kind": token["kind"],
                "left_surface": left, "target_surface": "y", "right_surface": right,
                "all_reader_separate_y": all_reader_separate,
                "it2a_boundary_class": it_category, "it2a_matched_surface": it_surface or "NONE",
                "rf1b_boundary_class": rf_category, "rf1b_matched_surface": rf_surface or "NONE",
                "zl3b_line": cross_row["zl3b_clean"], "it2a_line": cross_row["it2a_clean"],
                "rf1b_line": cross_row["rf1b_clean"],
            })
            base_counts[base_class] += 1
            final_counts[context_class] += 1
            position_counts[position] += 1
            kind_counts[token["kind"]] += 1
            all_reader_position[position] += all_reader_separate
            for reader, category in (("IT2a", it_category), ("RF1b", rf_category)):
                reader_category_counts[reader][category] += 1
                reader_position_counts[reader, position][category] += 1

    if len(occurrence_rows) != 270 or len({row["locus"] for row in occurrence_rows}) != 257:
        raise RuntimeError("naked-y occurrence census drift")
    if len({row["page"] for row in occurrence_rows}) != 125:
        raise RuntimeError("naked-y page census drift")
    if dict(position_counts) != EXPECTED_POSITIONS or dict(kind_counts) != EXPECTED_KINDS:
        raise RuntimeError("position or token-kind profile drift")
    if dict(base_counts) != EXPECTED_BASE_CLASSES or dict(final_counts) != EXPECTED_FINAL_CLASSES:
        raise RuntimeError(f"context class drift: base={dict(base_counts)!r} final={dict(final_counts)!r}")
    if sum(int(row["all_reader_separate_y"]) for row in occurrence_rows) != 83:
        raise RuntimeError("all-reader separate-y capacity drift")
    if {reader: dict(counts) for reader, counts in reader_category_counts.items()} != EXPECTED_READER:
        raise RuntimeError("reader boundary allocation drift")
    label_rows = [row for row in occurrence_rows if row["context_class"] == "Y_LABEL_SIGLUM"]
    if Counter(row["label_subrole"] for row in label_rows) != {"LABEL_ONLY": 9, "LABEL_INTERNAL": 1, "LABEL_CLOSE": 1}:
        raise RuntimeError("label-siglum precedence drift")
    if {row["locus"] for row in label_rows if row["label_subrole"] != "LABEL_ONLY"} != {"f77v.1", "f99r.2"}:
        raise RuntimeError("non-ONLY label loci drift")
    label_practical = {
        "LABEL_ONLY": "[Beschriftungszeichen]",
        "LABEL_INTERNAL": ";",
        "LABEL_CLOSE": ".",
        "LABEL_ENTRY": "Eintrag:",
    }
    practical_by_class = {
        "Y_BOS_ENTRY": "Eintrag:",
        "Y_EOS_CLOSE": ".",
        "Y_MEDIAL_RIGHT_REFERENCE": "hierzu:",
        "Y_MEDIAL_LEFT_CLOSE": ";",
        "Y_MEDIAL_BIDIRECTIONAL_HINGE": "hierzu:",
        "Y_MEDIAL_UNRESOLVED_HINGE": "hierzu:",
    }
    for row in occurrence_rows:
        context_class = str(row["context_class"])
        if context_class == "Y_LABEL_SIGLUM":
            expected_render = label_practical[str(row["label_subrole"])]
            if row["working_render_de"] != expected_render:
                raise RuntimeError("label occurrence practical rendering drift")
        elif context_class in practical_by_class and row["working_render_de"] != practical_by_class[context_class]:
            raise RuntimeError("non-materia occurrence practical rendering drift")
        elif context_class == "Y_MEDIAL_RIGHT_REFERENCE_MATERIA" and not str(row["working_render_de"]).startswith("hierzu: "):
            raise RuntimeError("materia occurrence practical rendering drift")
    separate_by_locus_ordinal = {
        (str(row["locus"]), int(row["ordinal"])): int(row["all_reader_separate_y"])
        for row in occurrence_rows
    }
    if {
        key: separate_by_locus_ordinal[key]
        for key in (("f107v.47", 1), ("f107v.47", 9), ("f6v.4", 1), ("f6v.4", 6),
                    ("f76r.29", 12), ("f76r.29", 14))
    } != {
        ("f107v.47", 1): 0, ("f107v.47", 9): 1,
        ("f6v.4", 1): 0, ("f6v.4", 6): 1,
        ("f76r.29", 12): 0, ("f76r.29", 14): 0,
    }:
        raise RuntimeError("multi-y all-reader intersection assignment drift")
    context_by_locus = {str(row["locus"]): row for row in occurrence_rows}
    if (
        context_by_locus["f48v.6"]["context_class"] != "Y_MEDIAL_BIDIRECTIONAL_HINGE"
        or context_by_locus["f76r.13"]["context_class"] != "Y_MEDIAL_BIDIRECTIONAL_HINGE"
    ):
        raise RuntimeError("mechanical hinge precedence drift at f48v.6/f76r.13")
    materia_rows = [row for row in occurrence_rows if int(row["materia_subtype"])]
    if len(materia_rows) != 13 or any(
        row["base_context_class"] != "Y_MEDIAL_RIGHT_REFERENCE" and row["locus"] != "f80v.21"
        for row in materia_rows
    ):
        raise RuntimeError("right-evidenced materia subtype scope drift")
    direction_override_rows = [row for row in occurrence_rows if int(row["direction_override"])]
    if len(direction_override_rows) != 1 or direction_override_rows[0]["locus"] != "f80v.21":
        raise RuntimeError("materia direction override must remain local to f80v.21")
    f80_occurrence = next(row for row in occurrence_rows if row["locus"] == "f80v.21")
    if (
        f80_occurrence["base_context_class"] != "Y_MEDIAL_LEFT_CLOSE"
        or f80_occurrence["context_class"] != "Y_MEDIAL_RIGHT_REFERENCE_MATERIA"
        or f80_occurrence["working_render_de"] != "hierzu: trocken gebundene Wurzeldroge, Form I"
        or f80_occurrence["left_fused_occurrences"] != 16
        or f80_occurrence["right_fused_occurrences"] != 0
        or f80_occurrence["it2a_boundary_class"] != "MERGE_RIGHT"
        or f80_occurrence["rf1b_boundary_class"] != "SEPARATE"
    ):
        raise RuntimeError("f80v.21 contextual override drift")

    occurrence_fields = list(occurrence_rows[0])
    reader_fields = list(reader_rows[0])
    write_tsv(output_dir / "PAGE_ALLOWLIST.tsv", [{"page": page} for page in sorted(pages)], ("page",))
    write_tsv(output_dir / "Y_OCCURRENCE_CENSUS.tsv", occurrence_rows, occurrence_fields)
    write_tsv(output_dir / "Y_READER_BOUNDARY_AUDIT.tsv", reader_rows, reader_fields)

    context_cards: list[dict[str, object]] = []
    for index, context_class in enumerate(FINAL_CONTEXT_ORDER, 1):
        members = [row for row in occurrence_rows if row["context_class"] == context_class]
        if not members:
            continue
        spec = CONTEXT_SPECS[context_class]
        context_cards.append({
            "card_id": f"G659-C{index:02d}", "context_class": context_class,
            "structural_tag": spec["structural_tag"], "selection_rule": spec["selection_rule"],
            "working_render_de": spec["working_render_de"], "live_rival_de": spec["live_rival_de"],
            "occurrences": len(members), "lines": len({row["locus"] for row in members}),
            "pages": len({row["page"] for row in members}),
            "all_reader_separate_y": sum(int(row["all_reader_separate_y"]) for row in members),
            "status": "ACCEPT_V36_CONTEXT_CARD_NOT_GLOBAL_LEXEME",
        })
    if len(context_cards) != 8:
        raise RuntimeError("V36 context-card count drift")
    expected_card_renders = {
        "Y_LABEL_SIGLUM": "[Beschriftungszeichen] / ; / .",
        "Y_BOS_ENTRY": "Eintrag:",
        "Y_EOS_CLOSE": ".",
        "Y_MEDIAL_RIGHT_REFERENCE": "hierzu:",
        "Y_MEDIAL_LEFT_CLOSE": ";",
        "Y_MEDIAL_BIDIRECTIONAL_HINGE": "hierzu:",
        "Y_MEDIAL_UNRESOLVED_HINGE": "hierzu:",
        "Y_MEDIAL_RIGHT_REFERENCE_MATERIA": "hierzu: rechter Kopf",
    }
    if {str(row["context_class"]): str(row["working_render_de"]) for row in context_cards} != expected_card_renders:
        raise RuntimeError("context-card practical rendering map drift")
    write_tsv(output_dir / "Y_CONTEXT_CARDS.tsv", context_cards, list(context_cards[0]))

    context_summary: list[dict[str, object]] = []
    for layer, order, counter in (
        ("MECHANICAL_BASE", BASE_CONTEXT_ORDER, base_counts),
        ("FINAL_WITH_LABEL_AND_MATERIA_PRECEDENCE", FINAL_CONTEXT_ORDER, final_counts),
    ):
        for context_class in order:
            context_summary.append({
                "layer": layer, "context_class": context_class, "occurrences": counter[context_class],
                "fraction_of_270": f"{counter[context_class] / 270:.6f}",
            })
    write_tsv(output_dir / "Y_CONTEXT_CLASS_SUMMARY.tsv", context_summary, list(context_summary[0]))

    dimension_rows: list[dict[str, object]] = []
    for dimension, values in (
        ("POSITION", sorted({str(row["position"]) for row in occurrence_rows})),
        ("TOKEN_KIND", sorted({str(row["token_kind"]) for row in occurrence_rows})),
        ("SECTION", sorted({str(row["section"]) for row in occurrence_rows})),
        ("LANGUAGE", sorted({str(row["language"]) for row in occurrence_rows})),
        ("HAND", sorted({str(row["hand"]) for row in occurrence_rows})),
    ):
        for value in values:
            members = [row for row in occurrence_rows if str(row[dimension.lower() if dimension != "TOKEN_KIND" else "token_kind"]) == value]
            dimension_rows.append({
                "dimension": dimension, "value": value, "occurrences": len(members),
                "bos": sum(row["position"] == "BOS" for row in members),
                "medial": sum(row["position"] == "MEDIAL" for row in members),
                "eos": sum(row["position"] == "EOS" for row in members),
                "only": sum(row["position"] == "ONLY" for row in members),
            })
    write_tsv(output_dir / "Y_DIMENSION_PROFILE.tsv", dimension_rows, list(dimension_rows[0]))

    page_rows: list[dict[str, object]] = []
    for page in sorted({str(row["page"]) for row in occurrence_rows}):
        members = [row for row in occurrence_rows if row["page"] == page]
        page_rows.append({
            "page": page, "occurrences": len(members), "lines": len({row["locus"] for row in members}),
            "bos": sum(row["position"] == "BOS" for row in members),
            "medial": sum(row["position"] == "MEDIAL" for row in members),
            "eos": sum(row["position"] == "EOS" for row in members),
            "only": sum(row["position"] == "ONLY" for row in members),
            "p_tokens": sum(row["token_kind"] == "P" for row in members),
            "l_tokens": sum(row["token_kind"] == "L" for row in members),
        })
    write_tsv(output_dir / "Y_PAGE_COUNTS.tsv", page_rows, list(page_rows[0]))

    reader_summary: list[dict[str, object]] = []
    for reader in ("IT2a", "RF1b"):
        for position in ("BOS", "MEDIAL", "EOS", "ONLY", "ALL"):
            counts = reader_category_counts[reader] if position == "ALL" else reader_position_counts[reader, position]
            reader_summary.append({
                "reader": reader, "position": position,
                "separate": counts["SEPARATE"], "merge_right": counts["MERGE_RIGHT"],
                "merge_left": counts["MERGE_LEFT"], "merge_both": counts["MERGE_BOTH"],
                "variant_or_other": counts["VARIANT_OTHER"], "total": sum(counts.values()),
                "all_reader_separate_capacity": sum(int(row["all_reader_separate_y"]) for row in occurrence_rows if position == "ALL" or row["position"] == position),
            })
    write_tsv(output_dir / "Y_READER_BOUNDARY_SUMMARY.tsv", reader_summary, list(reader_summary[0]))

    neighbor_rows: list[dict[str, object]] = []
    neighbor_summary: list[dict[str, object]] = []
    for side in ("LEFT", "RIGHT"):
        field = "left_surface" if side == "LEFT" else "right_surface"
        eligible = [row for row in occurrence_rows if row[field] not in {"<BOS>", "<EOS>"}]
        grouped: dict[str, list[dict[str, object]]] = defaultdict(list)
        for row in eligible:
            grouped[str(row[field])].append(row)
        for surface in sorted(grouped):
            members = grouped[surface]
            fused = surface + "y" if side == "LEFT" else "y" + surface
            known = surface in base_glossary
            neighbor_rows.append({
                "side": side, "neighbor_surface": surface, "occurrences": len(members),
                "lines": len({row["locus"] for row in members}), "pages": len({row["page"] for row in members}),
                "v35_known": int(known),
                "v35_meaning_de": base_glossary.get(surface, {}).get("working_meaning_de", "OPEN"),
                "v35_source": base_glossary.get(surface, {}).get("source", "OPEN"),
                "materia_preparation_head": int(side == "RIGHT" and is_materia_head(surface, base_glossary)),
                "fused_sister_surface": fused, "fused_sister_occurrences": surface_counts[fused],
                "fused_sister_pages": len(surface_pages.get(fused, set())),
                "example_loci": "|".join(sorted({str(row["locus"]) for row in members})[:8]),
            })
        neighbor_summary.append({
            "side": side, "positions": len(eligible), "surface_types": len(grouped),
            "v35_known_positions": sum(row[field] in base_glossary for row in eligible),
            "v35_known_types": sum(surface in base_glossary for surface in grouped),
            "fused_sister_positions": sum(surface_counts[(str(row[field]) + "y") if side == "LEFT" else ("y" + str(row[field]))] > 0 for row in eligible),
            "fused_sister_types": sum(surface_counts[(surface + "y") if side == "LEFT" else ("y" + surface)] > 0 for surface in grouped),
            "materia_preparation_positions": sum(side == "RIGHT" and is_materia_head(str(row[field]), base_glossary) for row in eligible),
            "materia_preparation_types": sum(side == "RIGHT" and is_materia_head(surface, base_glossary) for surface in grouped),
        })
    write_tsv(output_dir / "Y_NEIGHBOR_ATLAS.tsv", neighbor_rows, list(neighbor_rows[0]))
    write_tsv(output_dir / "Y_NEIGHBOR_SUMMARY.tsv", neighbor_summary, list(neighbor_summary[0]))

    occurrence_by_token = {
        (str(row["locus"]), int(row["token_index"])): row for row in occurrence_rows
    }
    base_coverage_by_locus = {row["locus"]: row for row in base_coverage}
    coverage_rows: list[dict[str, object]] = []
    affected_rows: list[dict[str, object]] = []
    non_y_before: list[tuple[object, ...]] = []
    non_y_after: list[tuple[object, ...]] = []
    for base_row in base_coverage:
        locus = base_row["locus"]
        line = by_line[locus]
        glosses = split_pipe(base_row["token_glosses_de"])
        sources = split_pipe(base_row["gloss_sources"])
        states = split_pipe(base_row["scope_states"])
        if not (len(line) == len(glosses) == len(sources) == len(states)):
            raise RuntimeError(f"V35 coverage token columns misalign: {locus}")
        unknown_pairs = list(zip(parse_compact_pipe(base_row["unknown_ordinals"]), parse_compact_pipe(base_row["unknown_surfaces"])))
        original_unknown = len(unknown_pairs)
        y_classes: list[str] = []
        y_ordinals: list[str] = []
        for index, token in enumerate(line):
            if token["eva"] != "y":
                non_y_before.append(
                    (locus, index + 1, token["eva"], glosses[index], sources[index], states[index])
                )
        for index, token in enumerate(line):
            if token["eva"] != "y":
                continue
            if glosses[index] != "[y:?]" or sources[index] != "OPEN" or states[index] != "UNKNOWN_SURFACE":
                raise RuntimeError(f"V35 naked y is not an open surface at {locus}.{index + 1}")
            occurrence = occurrence_by_token[(locus, int(token["token_index"]))]
            glosses[index] = context_token_gloss(occurrence)
            sources[index] = "GDT659:" + str(occurrence["context_class"])
            states[index] = "KNOWN_CONTEXT_LICENSED" if int(occurrence["all_reader_separate_y"]) else "READER_BOUNDARY_UNSTABLE"
            y_classes.append(str(occurrence["context_class"]))
            y_ordinals.append(str(index + 1))
        for index, token in enumerate(line):
            if token["eva"] != "y":
                non_y_after.append(
                    (locus, index + 1, token["eva"], glosses[index], sources[index], states[index])
                )
        if y_classes:
            unknown_pairs = [(ordinal, surface) for ordinal, surface in unknown_pairs if surface != "y"]
        row: dict[str, object] = dict(base_row)
        row["known_tokens"] = int(base_row["known_tokens"]) + len(y_classes)
        row["context_licensed_tokens"] = states.count("KNOWN_CONTEXT_LICENSED")
        row["ambiguous_tokens"] = states.count("AMBIGUOUS_ACTIVE_RIVAL")
        row["reader_unstable_tokens"] = states.count("READER_BOUNDARY_UNSTABLE")
        row["unknown_tokens"] = len(unknown_pairs)
        row["coverage_fraction"] = f"{int(row['known_tokens']) / int(row['token_count']):.6f}"
        row["token_glosses_de"] = " | ".join(glosses)
        row["gloss_sources"] = " | ".join(sources)
        row["scope_states"] = " | ".join(states)
        row["unknown_ordinals"] = "|".join(pair[0] for pair in unknown_pairs) or "NONE"
        row["unknown_surfaces"] = "|".join(pair[1] for pair in unknown_pairs) or "NONE"
        if int(base_row["unknown_tokens"]) - len(y_classes) != len(unknown_pairs):
            raise RuntimeError(f"V35→V36 unknown-token arithmetic drift: {locus}")
        coverage_rows.append(row)
        if y_classes:
            affected_rows.append({
                "page": row["page"], "locus": locus, "section": row["section"],
                "language": row["language"], "hand": row["hand"],
                "y_occurrences": len(y_classes), "y_ordinals": "|".join(y_ordinals),
                "context_classes": "|".join(y_classes), "zl3b_line": row["zl3b_line"],
                "v35_token_glosses_de": base_row["token_glosses_de"],
                "v36_token_glosses_de": row["token_glosses_de"],
                "v36_working_translation_de": render_line(locus, line, glosses, occurrence_by_token),
                "base_unknown_tokens": original_unknown, "v36_unknown_tokens": len(unknown_pairs),
            })
    if len(affected_rows) != 257 or len(non_y_before) != 32069 or non_y_before != non_y_after:
        raise RuntimeError("non-y preservation or affected-line count drift")
    non_y_before_sha256 = canonical_hash(non_y_before)
    non_y_after_sha256 = canonical_hash(non_y_after)
    if non_y_before_sha256 != non_y_after_sha256:
        raise RuntimeError("non-y before/after projection hash drift")
    if any(
        phrase in str(row["v36_working_translation_de"])
        for row in affected_rows for phrase in PRACTICAL_STRUCTURAL_WORDS
    ):
        raise RuntimeError("structural y label leaked into a practical affected-line translation")
    only_label_loci = {
        str(row["locus"]) for row in occurrence_rows if row["label_subrole"] == "LABEL_ONLY"
    }
    only_label_translations = {
        str(row["locus"]): str(row["v36_working_translation_de"])
        for row in affected_rows if row["locus"] in only_label_loci
    }
    if (
        len(only_label_loci) != 9
        or set(only_label_translations) != only_label_loci
        or set(only_label_translations.values()) != {"[Beschriftungszeichen]"}
        or any(
            "Beschriftungszeichen" in str(row["v36_working_translation_de"])
            and row["locus"] not in only_label_loci
            for row in affected_rows
        )
    ):
        raise RuntimeError("LABEL_ONLY practical rendering drift")

    coverage_fields = list(base_coverage[0])
    write_tsv(output_dir / "ALL_LINE_CONCRETE_COVERAGE_V36.tsv", coverage_rows, coverage_fields)
    write_tsv(output_dir / "Y_AFFECTED_LINE_TRANSLATIONS.tsv", affected_rows, list(affected_rows[0]))

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
        complete["working_translation_de"] = render_line(
            str(row["locus"]), by_line[str(row["locus"])], split_pipe(row["token_glosses_de"]), occurrence_by_token
        )
        complete_rows.append(complete)
    complete_rows.sort(key=lambda row: (-int(row["strict_complete"]), -int(row["token_count"]), str(row["locus"])))
    for rank, row in enumerate(complete_rows, 1):
        row["rank"] = rank
    if any(
        phrase in str(row["working_translation_de"])
        for row in complete_rows for phrase in PRACTICAL_STRUCTURAL_WORDS
    ):
        raise RuntimeError("structural y label leaked into a practical complete translation")
    complete_fields = list(base_complete[0])
    write_tsv(output_dir / "COMPLETE_PASSAGES_V36.tsv", complete_rows, complete_fields)

    base_one_by_locus = {row["locus"]: row for row in base_one}
    one_rows: list[dict[str, object]] = []
    for row in coverage_rows:
        if int(row["unknown_tokens"]) != 1 or int(row["known_tokens"]) < 1:
            continue
        ordinal = int(str(row["unknown_ordinals"]))
        surface = str(row["unknown_surfaces"])
        base_proposal = base_one_by_locus.get(str(row["locus"]))
        if base_proposal and base_proposal["unknown_surface"] == surface:
            proposal = base_proposal["proposed_default_de"]
            basis = base_proposal["proposal_basis"]
            strength = base_proposal["proposal_strength"]
        else:
            proposal = f"[{surface}:?]"
            basis = "NEWLY_EXPOSED_BY_GDT659_NO_NEW_CARD"
            strength = "OPEN"
        strict = int(
            int(row["ambiguous_tokens"]) == 0
            and int(row["reader_unstable_tokens"]) == 0
            and int(row["all_present_exact"]) == 1
        )
        strength_rank = {"HIGH": 4, "MEDIUM": 3, "LOW": 2, "OPEN": 1}[strength]
        score = int(row["known_tokens"]) * 1_000_000 + strength_rank * 100_000 + strict * 10_000 - int(row["token_count"]) * 100
        line = by_line[str(row["locus"])]
        proposed_glosses = split_pipe(row["token_glosses_de"])
        proposed_glosses[ordinal - 1] = proposal
        item = {
            "rank": 0, "score": score, "strict_eligible": strict, **row,
            "unknown_ordinal": ordinal, "unknown_surface": surface,
            "previous": "<BOS>" if ordinal == 1 else line[ordinal - 2]["eva"],
            "following": "<EOS>" if ordinal == len(line) else line[ordinal]["eva"],
            "proposed_default_de": proposal, "proposal_basis": basis, "proposal_strength": strength,
            "proposed_complete_translation_de": render_line(
                str(row["locus"]), line, proposed_glosses, occurrence_by_token
            ),
        }
        one_rows.append(item)
    one_rows.sort(key=lambda row: (-int(row["score"]), str(row["locus"])))
    for rank, row in enumerate(one_rows, 1):
        row["rank"] = rank
    if any(
        phrase in str(row["proposed_complete_translation_de"])
        for row in one_rows for phrase in PRACTICAL_STRUCTURAL_WORDS
    ):
        raise RuntimeError("structural y label leaked into a practical one-hole preview")
    one_fields = list(base_one[0])
    write_tsv(output_dir / "ONE_UNKNOWN_PASSAGES_V36.tsv", one_rows, one_fields)

    base_complete_loci = {row["locus"] for row in base_complete}
    newly_completed = [dict(row) for row in complete_rows if row["locus"] not in base_complete_loci]
    newly_completed.sort(key=lambda row: str(row["locus"]))
    for rank, row in enumerate(newly_completed, 1):
        row["rank"] = rank
    expected_completed = {"f112r.9", "f39v.13", "f76r.13", "f77v.1", "f78v.7", "f80v.21", "f85r1.16", "f99r.2"}
    if {row["locus"] for row in newly_completed} != expected_completed:
        raise RuntimeError("newly completed V36 loci drift")
    write_tsv(output_dir / "NEWLY_COMPLETED_LINES.tsv", newly_completed, complete_fields)

    base_one_loci = {row["locus"] for row in base_one}
    newly_one = [dict(row) for row in one_rows if row["locus"] not in base_one_loci]
    newly_one.sort(key=lambda row: str(row["locus"]))
    for rank, row in enumerate(newly_one, 1):
        row["rank"] = rank
    if len(newly_one) != 17:
        raise RuntimeError("new V36 one-hole count drift")
    if any(
        row["proposed_default_de"] != f"[{row['unknown_surface']}:?]"
        or row["proposal_basis"] != "NEWLY_EXPOSED_BY_GDT659_NO_NEW_CARD"
        or row["proposal_strength"] != "OPEN"
        for row in newly_one
    ):
        raise RuntimeError("newly exposed one-hole preview exceeded the Y-only claim scope")
    new_one_fields = ["base_unknown_tokens", *one_fields]
    for row in newly_one:
        row["base_unknown_tokens"] = base_coverage_by_locus[str(row["locus"])]["unknown_tokens"]
    write_tsv(output_dir / "NEWLY_EXPOSED_ONE_HOLE_LINES.tsv", newly_one, new_one_fields)

    glossary_rows: list[dict[str, object]] = [dict(row) for row in base_glossary_rows]
    glossary_rows.sort(key=lambda row: str(row["surface"]))
    if (
        len(glossary_rows) != 495
        or len({str(row["surface"]) for row in glossary_rows}) != 495
        or any(row["surface"] == "y" for row in glossary_rows)
    ):
        raise RuntimeError("V36 glossary surface count drift")
    write_tsv(output_dir / "V36_WORKING_TOKEN_GLOSSARY.tsv", glossary_rows, list(base_glossary_rows[0]))

    dictionary_rows: list[dict[str, object]] = [dict(row) for row in base_dictionary]
    for context_class in FINAL_CONTEXT_ORDER:
        if not final_counts[context_class]:
            continue
        spec = CONTEXT_SPECS[context_class]
        dictionary_rows.append({
            "entry": f"y@{context_class}", "kind": "CONTEXTUAL_NAKED_Y_CARD",
            "working_meaning_de": spec["working_render_de"],
            "composition": spec["structural_tag"], "context_rule": spec["selection_rule"],
            "status": "NEW_V36_CONTEXT_CARD_NOT_GLOBAL_LEXEME",
        })
    if len(dictionary_rows) != 582 or any(row["entry"] == "y" for row in dictionary_rows):
        raise RuntimeError("V36 dictionary count or global naked-y entry drift")
    write_tsv(output_dir / "WORKING_DICTIONARY_V36.tsv", dictionary_rows, list(base_dictionary[0]))

    base_metrics = metrics(
        [dict(row) for row in base_coverage], [dict(row) for row in base_one],
        [dict(row) for row in base_complete], [dict(row) for row in base_glossary_rows],
    )
    final_metrics = metrics(coverage_rows, one_rows, complete_rows, glossary_rows)
    expected_base_metrics = {
        "physical_lines": 4128, "known_token_positions": 16743, "unknown_token_positions": 15596,
        "complete_multi_token_lines": 138, "strict_complete_lines": 80,
        "one_unknown_lines": 239, "strict_one_unknown_lines": 57, "working_glossary_surfaces": 495,
    }
    expected_final_metrics = {
        "physical_lines": 4128, "known_token_positions": 17013, "unknown_token_positions": 15326,
        "complete_multi_token_lines": 146, "strict_complete_lines": 80,
        "one_unknown_lines": 249, "strict_one_unknown_lines": 58, "working_glossary_surfaces": 495,
    }
    if base_metrics != expected_base_metrics or final_metrics != expected_final_metrics:
        raise RuntimeError(f"V35/V36 coverage metrics drift: {base_metrics!r} -> {final_metrics!r}")

    round_rows = [
        {
            "version": "V35", "added_context_card": "BASE", "dictionary_entries": len(base_dictionary),
            **base_metrics,
        },
        {
            "version": "V36", "added_context_card": "8_NAKED_Y_CONTEXT_CARDS_270_POSITIONS",
            "dictionary_entries": len(dictionary_rows), **final_metrics,
        },
    ]
    write_tsv(output_dir / "ROUND_COVERAGE_COUNTS.tsv", round_rows, list(round_rows[0]))

    f80_coverage = next(row for row in coverage_rows if row["locus"] == "f80v.21")
    f80_translation = next(row for row in affected_rows if row["locus"] == "f80v.21")
    f80_complete = next(row for row in complete_rows if row["locus"] == "f80v.21")
    f80_rows = [{
        "page": "f80v", "locus": "f80v.21", "local_span": "okal y rchey",
        "base_context_class": f80_occurrence["base_context_class"],
        "final_context_class": f80_occurrence["context_class"],
        "structural_tag": f80_occurrence["structural_tag"],
        "reader_evidence": "ZL3b/RF1b y|rchey; IT2a yrchey",
        "left_sister": "okaly:16", "right_zl_sister": "yrchey:0",
        "right_v35_head": "rchey = Wurzel/Wurzeldroge, trocken gebunden, Form I",
        "working_local_render_de": "hierzu: trocken gebundene Wurzeldroge, Form I",
        "working_line_translation_de": f80_translation["v36_working_translation_de"],
        "v36_unknown_tokens": f80_coverage["unknown_tokens"],
        "claim_boundary": "local contextual rendering; no global y lexeme and no exact ingredient identity",
    }]
    if (
        f80_rows[0]["v36_unknown_tokens"] != 0
        or f80_rows[0]["working_line_translation_de"] != F80V21_TRANSLATION_DE
        or f80_translation["v36_working_translation_de"] != F80V21_TRANSLATION_DE
        or f80_complete["working_translation_de"] != F80V21_TRANSLATION_DE
    ):
        raise RuntimeError("f80v.21 did not close with the required concrete rendering")
    write_tsv(output_dir / "F80V21_WORKING_TRANSLATION.tsv", f80_rows, list(f80_rows[0]))

    input_paths = (
        G658 / "REPORT.md",
        G658 / "artifacts/RESULT.json",
        G658 / "artifacts/PAGE_ALLOWLIST.tsv",
        G658 / "artifacts/V35_WORKING_TOKEN_GLOSSARY.tsv",
        G658 / "artifacts/WORKING_DICTIONARY_V35.tsv",
        G658 / "artifacts/ALL_LINE_CONCRETE_COVERAGE_V35.tsv",
        G658 / "artifacts/COMPLETE_PASSAGES_V35.tsv",
        G658 / "artifacts/ONE_UNKNOWN_PASSAGES_V35.tsv",
        BASE_REL / "artifacts/MANUAL_Y_CONTEXT_AUDIT.tsv",
        BASE_REL / "artifacts/HISTORICAL_ENTRY_MARKER_ANALOGIES.tsv",
        TOKENS_REL,
        CROSS_REL,
    )
    output_paths = [output_dir / name for name in OUTPUT_NAMES]
    result_core: dict[str, object] = {
        "schema": "GDT659_NAKED_Y_LOCAL_REFERENCE_RESULT_V1",
        "experiment_id": "GDT659", "status": STATUS,
        "guard": {
            "allowed_pages": len(pages), "f1r": "EXCLUDED_BY_EXACT_ALLOWLIST",
            "f84": "FORBIDDEN", "f84r": "FORBIDDEN",
            "token_query": token_stats, "cross_query": cross_stats,
            "new_pages": 0, "new_images": 0,
        },
        "census": {
            "naked_y_positions": len(occurrence_rows), "naked_y_lines": len({row["locus"] for row in occurrence_rows}),
            "naked_y_pages": len({row["page"] for row in occurrence_rows}),
            "positions": dict(sorted(position_counts.items())), "token_kinds": dict(sorted(kind_counts.items())),
            "all_reader_separate_y": sum(int(row["all_reader_separate_y"]) for row in occurrence_rows),
            "full_line_all_present_exact_y_positions": sum(int(row["line_all_present_exact"]) for row in occurrence_rows),
        },
        "context_cards": {
            "accepted_cards": len(context_cards), "base_classes": dict(sorted(base_counts.items())),
            "final_classes": dict(sorted(final_counts.items())), "label_precedence_occurrences": len(label_rows),
            "label_subroles": dict(sorted(Counter(row["label_subrole"] for row in label_rows).items())),
            "materia_subtype_positions": sum(int(row["materia_subtype"]) for row in occurrence_rows),
            "materia_direction_overrides": sum(int(row["direction_override"]) for row in occurrence_rows),
            "all_positions_context_known": 270, "global_y_lexeme_added": False,
        },
        "reader_boundaries": {
            "IT2a": dict(sorted(reader_category_counts["IT2a"].items())),
            "RF1b": dict(sorted(reader_category_counts["RF1b"].items())),
        },
        "neighbors": {
            row["side"].lower(): {key: value for key, value in row.items() if key != "side"}
            for row in neighbor_summary
        },
        "f80v21": {
            "base_context_class": f80_occurrence["base_context_class"],
            "final_context_class": f80_occurrence["context_class"],
            "working_render_de": f80_occurrence["working_render_de"],
            "it2a_boundary_class": f80_occurrence["it2a_boundary_class"],
            "rf1b_boundary_class": f80_occurrence["rf1b_boundary_class"],
            "line_complete_v36": True,
        },
        "coverage": {
            "base": base_metrics, "final": final_metrics,
            "affected_lines": len(affected_rows), "newly_completed_lines": len(newly_completed),
            "newly_completed_loci": sorted(row["locus"] for row in newly_completed),
            "newly_exposed_one_hole_lines": len(newly_one),
            "non_y_token_positions_unchanged": len(non_y_before),
            "non_y_before_sha256": non_y_before_sha256,
            "non_y_after_sha256": non_y_after_sha256,
            "non_y_exactly_unchanged": non_y_before == non_y_after,
        },
        "working_dictionary": {
            "v35_entries": len(base_dictionary), "v36_entries": len(dictionary_rows),
            "added_context_entries": len(dictionary_rows) - len(base_dictionary),
            "v35_glossary_surfaces": len(base_glossary_rows), "v36_glossary_surfaces": len(glossary_rows),
            "v35_prefix_sha256": canonical_hash(base_dictionary), "v36_sha256": canonical_hash(dictionary_rows),
        },
        "supporting_inputs": {
            "manual_context_rows": len(manual_audit), "historical_analogy_rows": len(historical),
        },
        "determinism_contract": {
            "builder_supports_artifact_dir_cli": True,
            "naked_y_occurrence_dispatcher_required": True,
            "surface_glossary_must_not_dispatch_naked_y": True,
            "replay_files": [str(BASE_REL / "artifacts" / name) for name in (*OUTPUT_NAMES, "RESULT.json")],
        },
        "claim_boundary": (
            "Exploratory deterministic occurrence-context renderings for all 270 naked ZL3b y positions. "
            "The eight cards are positional, neighbour-conditioned or label-conditioned; no global Y=dieser "
            "lexeme, substring inheritance, phonetics, language, plaintext, exact ingredient, new page, image or f1r is asserted."
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
        with tempfile.TemporaryDirectory(prefix="gdt659_replay_") as directory:
            replay_dir = Path(directory)
            replay_result = build(replay_dir)
            if replay_result != result:
                raise RuntimeError("tempdir RESULT replay differs")
            for name in (*OUTPUT_NAMES, "RESULT.json"):
                if (ART / name).read_bytes() != (replay_dir / name).read_bytes():
                    raise RuntimeError(f"tempdir replay differs: {name}")
    print(
        "GDT659 built: y=270 cards=8 label=11 materia_subtype=13 direction_override=1 "
        f"known={result['coverage']['final']['known_token_positions']} "
        f"complete={result['coverage']['final']['complete_multi_token_lines']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
