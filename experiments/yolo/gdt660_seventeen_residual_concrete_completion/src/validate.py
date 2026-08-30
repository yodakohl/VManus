#!/usr/bin/env python3
"""Independent source-first release validator for GDT660.

The protected transcription census is completed before any GDT660 artifact is
trusted. The builder is never imported. Its command-line interface is used
only as the final action, writing into a temporary directory for byte replay.
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
BASE = Path("experiments/yolo/gdt660_seventeen_residual_concrete_completion")
ART = ROOT / BASE / "artifacts"
RUN = ROOT / BASE / "src/run.py"
MANIFEST = ROOT / BASE / "experiment.json"
REPORT = ROOT / BASE / "REPORT.md"
VALIDATION = ART / "VALIDATION.json"

G659 = Path("experiments/yolo/gdt659_naked_y_local_reference")
ALLOW = G659 / "artifacts/PAGE_ALLOWLIST.tsv"
BASE_GLOSSARY = G659 / "artifacts/V36_WORKING_TOKEN_GLOSSARY.tsv"
BASE_DICTIONARY = G659 / "artifacts/WORKING_DICTIONARY_V36.tsv"
BASE_COVERAGE = G659 / "artifacts/ALL_LINE_CONCRETE_COVERAGE_V36.tsv"
BASE_COMPLETE = G659 / "artifacts/COMPLETE_PASSAGES_V36.tsv"
BASE_ONE = G659 / "artifacts/ONE_UNKNOWN_PASSAGES_V36.tsv"
TOKENS = Path("transcription/voynich_zl3b_tokens.tsv")
CROSS = Path("transcription/voynich_cross_transcription_lines.tsv")

OUTPUT_NAMES = (
    "PAGE_ALLOWLIST.tsv", "TARGET_DECISION_DECK.tsv",
    "ACCEPTED_WHOLE_SURFACE_DEFAULTS.tsv", "ALL_OCCURRENCE_SEMANTIC_AUDIT.tsv",
    "READER_VARIANT_AUDIT.tsv", "S_DY_CONTEXT_CENSUS.tsv",
    "S_DY_CONTEXT_CARDS.tsv", "S_DY_CONTEXT_SUMMARY.tsv",
    "MATERIA_AMOUNT_FAMILY_ATLAS.tsv", "QUALITY_PREPARATION_FAMILY_ATLAS.tsv",
    "Y_PREFIX_PLACEMENT_ATLAS.tsv", "TARGET_LINE_TRANSLATIONS.tsv",
    "ROUND_COVERAGE_COUNTS.tsv", "NEWLY_COMPLETED_LINES.tsv",
    "NEWLY_EXPOSED_ONE_HOLE_LINES.tsv", "V37_WORKING_TOKEN_GLOSSARY.tsv",
    "WORKING_DICTIONARY_V37.tsv", "ALL_LINE_CONCRETE_COVERAGE_V37.tsv",
    "COMPLETE_PASSAGES_V37.tsv", "ONE_UNKNOWN_PASSAGES_V37.tsv",
)

TARGET_ORDER = (
    "cholkar", "qodain", "lcho", "kchor", "okchan", "opchar", "ydy",
    "schokey", "s", "dy", "solkchy", "yckhey", "lshcthy", "ysheey",
    "cheeytal", "ochedar", "cheoty",
)
TARGETS = set(TARGET_ORDER)
WHOLE_ORDER = tuple(surface for surface in TARGET_ORDER if surface not in {"s", "dy"})

# positions, physical lines, pages, exact in all three readers, split-normalized
TARGET_COUNTS = {
    "cholkar": (3, 3, 3, 2, 3), "qodain": (10, 9, 6, 9, 9),
    "lcho": (6, 6, 5, 3, 3), "kchor": (19, 19, 19, 18, 18),
    "okchan": (1, 1, 1, 1, 1), "opchar": (2, 2, 2, 2, 2),
    "ydy": (5, 5, 5, 4, 4), "schokey": (1, 1, 1, 1, 1),
    "s": (272, 261, 125, 154, 154), "dy": (229, 205, 117, 149, 149),
    "solkchy": (1, 1, 1, 1, 1), "yckhey": (2, 2, 2, 2, 2),
    "lshcthy": (1, 1, 1, 1, 1), "ysheey": (8, 8, 8, 5, 7),
    "cheeytal": (1, 1, 1, 0, 0), "ochedar": (1, 1, 1, 1, 1),
    "cheoty": (4, 4, 4, 4, 4),
}

TARGET_POSITIONS = {"BOS": 36, "MEDIAL": 404, "EOS": 118, "ONLY": 8}
TARGET_KINDS = {"P": 558, "L": 8}
S_POSITIONS = {"BOS": 17, "MEDIAL": 214, "EOS": 33, "ONLY": 8}
DY_POSITIONS = {"BOS": 2, "MEDIAL": 150, "EOS": 77}
S_KINDS = {"P": 264, "L": 8}
DY_KINDS = {"P": 229}
S_LABEL_LOCI = {
    "f49v.15", "f66r.18", "f66r.35", "f75v.11",
    "f75v.2", "f76r.14", "f76r.37", "f76r.4",
}

BASE_METRICS = {
    "physical_lines": 4128, "known_token_positions": 17013,
    "unknown_token_positions": 15326, "complete_multi_token_lines": 146,
    "strict_complete_lines": 80, "one_unknown_lines": 249,
    "strict_one_unknown_lines": 58, "working_glossary_surfaces": 495,
}
FINAL_METRICS = {
    "physical_lines": 4128, "known_token_positions": 17579,
    "unknown_token_positions": 14760, "complete_multi_token_lines": 172,
    "strict_complete_lines": 83, "one_unknown_lines": 273,
    "strict_one_unknown_lines": 68, "working_glossary_surfaces": 510,
}

NEW_COMPLETE = {
    "f2r.3", "f6v.15", "f7r.10", "f11r.4", "f13v.10", "f15v.5",
    "f19v.10", "f24r.1", "f24r.18", "f29v.3", "f35v.19", "f36r.6",
    "f36v.4", "f50r.5", "f54v.12", "f54v.13", "f76r.29", "f77r.42",
    "f78r.13", "f79r.30", "f80r.42", "f81r.17", "f86v6.39",
    "f104r.42", "f115r.39", "f115v.28",
}

EXPECTED_WHOLE_MEANINGS = {
    "cholkar": "Trockengut: heiße Fraktion I",
    "qodain": "Qualitätsgrad II",
    "lcho": "Trockenansatz aus Drogenholz",
    "kchor": "Drogenportion, heiß-trocken",
    "okchan": "heiß-trockener Ansatz, Grad I",
    "opchar": "trockene Pulverfraktion I im Ansatz",
    "ydy": "Wertfeldwechsel/-schluss",
    "schokey": "heiß-trockener Samenansatz in der Gradmitte",
    "solkchy": "Saatgut, heiß-trocken am Gradanfang",
    "yckhey": "Eintrags-/Bezugsform: Arzneikompositum in der Gradmitte",
    "lshcthy": "feuchtes CTH-Drogenholz",
    "ysheey": "Eintrags-/Bezugsform: feucht am Gradende",
    "cheeytal": "Rohstoffklasse I: trocken am Gradende, kalt am Gradanfang",
    "ochedar": "trockener Ansatz in der Gradmitte, abgemessene Fraktion I",
    "cheoty": "trocken angesetzte kalte Zubereitung am Gradanfang",
}

CONTEXT_CARDS = {
    "S_LABEL_SIGLUM": ("s", 8, "[Beschriftungszeichen]", "[Beschriftungszeichen]"),
    "S_BOS": ("s", 17, "Samen-/Saatgutposten", "Samen-/Saatgutposten:"),
    "S_MEDIAL": ("s", 214, "Samen-/Saatgutposten", "Samen-/Saatgutposten"),
    "S_EOS": ("s", 33, "Samen-/Saatgutposten", "Samen-/Saatgutposten."),
    "DY_BOS_CLOSE": ("dy", 2, "voriges Qualitäts-/Wertfeld geschlossen", "voriges Qualitäts-/Wertfeld geschlossen:"),
    "DY_MEDIAL": ("dy", 150, "Qualitäts-/Wertfeld geschlossen", ";"),
    "DY_EOS": ("dy", 77, "Qualitäts-/Wertfeld geschlossen", "."),
}

MATERIA_FAMILIES = {
    "CHOLKAR_DRY_HOT_FRACTION": ("cholkar", "chol", "kar", "cholkaiin"),
    "QODAIN_QUALITY_II": ("qodain", "dain", "qodal", "qodaiin"),
    "LCHO_WOOD_DRY_PREP": ("lcho", "cho", "lcheo", "lchol"),
    "KCHOR_HOT_DRY_PORTION": ("kchor", "kor", "qotchor", "qokchor"),
    "OPCHAR_POWDER_FRACTION": ("opchar", "par", "opal", "pchar", "qopchar"),
    "SOLKCHY_SEED_MATERIAL": ("solkchy", "sol", "kchy"),
    "LSHCTHY_WOOD_MOIST_FORM": ("lshcthy", "shcthy", "lsheey"),
    "OCHEDAR_MEASURED_DRY_FRACTION": ("ochedar", "dar", "chedar", "odal"),
}
QUALITY_FAMILIES = {
    "OKCHAN_HOT_DRY_GRADE_I": ("okchan", "chan", "okchy", "okchey"),
    "SCHOKEY_SEED_DRY_PREP": ("schokey", "chokey", "schos"),
    "CHEEYTAL_DUAL_QUALITY": ("cheeytal", "cheey", "tal", "chekal"),
    "CHEOTY_COLD_DRY_START": ("cheoty", "cheoky", "otcho"),
}
Y_PREFIX_FAMILIES = {
    "YDY_VALUE_BOUNDARY": ("ydy", "dy"),
    "YSHEEY_MOIST_END": ("ysheey", "sheey"),
    "YCKHEY_COMPOSITE": ("yckhey", "ckhey"),
}

FILLER = re.compile(
    r"arbeitsgut|arbeitschritt|arbeitsschritt|arbeitsmittel|arbeitsstoff|"
    r"arbeitsobjekt|werkzeug|produkt\s+weiter|f.hre\s+.*\s+aus|"
    r"leite\s+.*\s+weiter|geh(?:e)?\s+zur\s+arbeit|nimm\s+.*\s+arbeite|"
    r"\b(?:vorgang|prozess|tätigkeit|operation)\b",
    re.IGNORECASE,
)
OPAQUE = re.compile(r"\[[^\]]*\?\]|\b(?:unbekannt|ungeklärt|unklar|offen)\b", re.IGNORECASE)


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


def line_position(ordinal: int, length: int) -> str:
    if length == 1:
        return "ONLY"
    if ordinal == 1:
        return "BOS"
    if ordinal == length:
        return "EOS"
    return "MEDIAL"


def independent_records(
    token_rows: list[dict[str, str]], cross_rows: list[dict[str, str]], surfaces: set[str],
) -> tuple[list[dict[str, object]], dict[str, list[dict[str, str]]], dict[str, dict[str, str]]]:
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
            occurrence_in_line = seen[locus]
            readers = [cross[locus][field].split() for field in ("zl3b_clean", "it2a_clean", "rf1b_clean")]
            direct = [tokens.count(surface) for tokens in readers]
            spans = [span_count(tokens, surface) for tokens in readers]
            line = by_locus[locus]
            ordinal = next(index for index, token in enumerate(line, 1) if token is row)
            records.append({
                **row, "token_ordinal": ordinal,
                "line_position": line_position(ordinal, len(line)),
                "previous": "<BOS>" if ordinal == 1 else line[ordinal - 2]["eva"],
                "following": "<EOS>" if ordinal == len(line) else line[ordinal]["eva"],
                "zl3b_line": cross[locus]["zl3b_clean"],
                "it2a_line": cross[locus]["it2a_clean"],
                "rf1b_line": cross[locus]["rf1b_clean"],
                "reader_exact": int(occurrence_in_line <= min(direct)),
                "split_normalized": int(occurrence_in_line <= min(spans)),
            })
    records.sort(key=lambda item: (
        TARGET_ORDER.index(str(item["eva"])), str(item["page"]),
        str(item["locus"]), int(item["token_index"]),
    ))
    return records, by_locus, cross


def census(records: list[dict[str, object]], surface: str) -> tuple[int, int, int, int, int]:
    members = [row for row in records if row["eva"] == surface]
    return (
        len(members), len({str(row["locus"]) for row in members}),
        len({str(row["page"]) for row in members}),
        sum(int(row["reader_exact"]) for row in members),
        sum(int(row["split_normalized"]) for row in members),
    )


def independent_stable_maps(
    token_rows: list[dict[str, str]], cross_rows: list[dict[str, str]],
) -> tuple[dict[tuple[str, int], int], dict[tuple[str, int], int]]:
    """Recompute the established exact and whitespace-split capacities."""
    cross = {row["locus"]: row for row in cross_rows}
    ordinals: Counter[tuple[str, str]] = Counter()
    exact: dict[tuple[str, int], int] = {}
    normalized: dict[tuple[str, int], int] = {}
    for row in sorted(token_rows, key=lambda item: (item["page"], item["locus"], int(item["token_index"]))):
        locus, surface = row["locus"], row["eva"]
        ordinals[locus, surface] += 1
        readers = [cross[locus][name].split() for name in ("zl3b_clean", "it2a_clean", "rf1b_clean")]
        exact_caps = [words.count(surface) for words in readers]
        norm_caps = [span_count(words, surface) for words in readers]
        key = locus, int(row["token_index"])
        exact[key] = int(ordinals[locus, surface] <= min(exact_caps))
        normalized[key] = int(ordinals[locus, surface] <= min(norm_caps))
    return exact, normalized


def expected_context_class(surface: str, position: str, kind: str) -> str:
    if surface == "s":
        if kind == "L":
            return "S_LABEL_SIGLUM"
        return {"BOS": "S_BOS", "MEDIAL": "S_MEDIAL", "EOS": "S_EOS"}[position]
    if surface == "dy":
        return {"BOS": "DY_BOS_CLOSE", "MEDIAL": "DY_MEDIAL", "EOS": "DY_EOS"}[position]
    return "EXACT_WHOLE"


def expected_placement(surface: str, position: str) -> str:
    if surface == "ydy":
        return "YDY_MEDIAL_NEXT_VALUE" if position == "MEDIAL" else "YDY_EOS_CLOSE"
    if surface == "ysheey":
        return "YSHEEY_BOS_ENTRY" if position == "BOS" else "YSHEEY_MEDIAL_REFERENCE"
    if surface == "yckhey":
        return "YCKHEY_BOS_ENTRY" if position == "BOS" else "YCKHEY_EOS_FORM"
    return "NONE"


def expected_occurrence_gloss(surface: str, position: str, kind: str) -> str:
    if surface in {"s", "dy"}:
        return CONTEXT_CARDS[expected_context_class(surface, position, kind)][2]
    if surface == "ydy":
        return "nächstes Wertfeld:" if position == "MEDIAL" else "Wertfeld abgeschlossen"
    if surface == "ysheey":
        return "Eintrag: feucht am Gradende" if position == "BOS" else "hierzu: feucht am Gradende"
    if surface == "yckhey":
        return "Eintrag: Arzneikompositum in der Gradmitte" if position == "BOS" else "Arzneikompositum in der Gradmitte"
    return EXPECTED_WHOLE_MEANINGS[surface]


def expected_occurrence_render(surface: str, position: str, kind: str) -> str:
    if surface in {"s", "dy"}:
        return CONTEXT_CARDS[expected_context_class(surface, position, kind)][3]
    if surface == "ydy":
        return "nächstes Wertfeld:" if position == "MEDIAL" else "."
    return expected_occurrence_gloss(surface, position, kind)


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


def field(row: dict[str, str], *names: str) -> str:
    for name in names:
        if name in row:
            return row[name]
    raise KeyError(f"none of the required fields present: {names!r}")


def validate_release(
    check: Callable[[object, str, str], None],
    token_rows: list[dict[str, str]], cross_rows: list[dict[str, str]],
    token_stats: dict[str, int], cross_stats: dict[str, int],
    records: list[dict[str, object]], by_line: dict[str, list[dict[str, str]]],
) -> None:
    required = set(OUTPUT_NAMES) | {"RESULT.json"}
    missing = sorted(name for name in required if not (ART / name).is_file())
    check(not missing, "required artifact packet", repr(missing))
    if missing:
        return
    # Artifact checks are deliberately below the guarded recensus in main().
    base_glossary = read_tsv(ROOT / BASE_GLOSSARY)
    base_dictionary = read_tsv(ROOT / BASE_DICTIONARY)
    base_coverage = read_tsv(ROOT / BASE_COVERAGE)
    base_complete = read_tsv(ROOT / BASE_COMPLETE)
    base_one = read_tsv(ROOT / BASE_ONE)
    glossary = read_tsv(ART / "V37_WORKING_TOKEN_GLOSSARY.tsv")
    dictionary = read_tsv(ART / "WORKING_DICTIONARY_V37.tsv")
    coverage = read_tsv(ART / "ALL_LINE_CONCRETE_COVERAGE_V37.tsv")
    complete = read_tsv(ART / "COMPLETE_PASSAGES_V37.tsv")
    one = read_tsv(ART / "ONE_UNKNOWN_PASSAGES_V37.tsv")

    check(coverage_metrics(base_coverage, base_complete, base_one, len(base_glossary)) == BASE_METRICS,
          "recomputed V36 base metrics")
    check(coverage_metrics(coverage, complete, one, len(glossary)) == FINAL_METRICS,
          "recomputed V37 final metrics")
    check(len(base_glossary) == 495 and len(base_dictionary) == 582, "V36 glossary/dictionary base sizes")

    base_by = {row["locus"]: row for row in base_coverage}
    final_by = {row["locus"]: row for row in coverage}
    check(
        len(base_by) == len(final_by) == len(by_line) == 4128
        and set(base_by) == set(final_by) == set(by_line),
        "4128-line V36/V37/raw identity",
    )
    record_by = {(str(row["locus"]), str(row["token_index"])): row for row in records}
    source_fields = (
        "page", "locus", "section", "language", "hand", "token_count",
        "reader_exact_tokens", "split_normalized_tokens", "all_three_present",
        "all_present_exact", "zl3b_line",
    )
    target_count = 0
    non_target_count = 0
    projection_ok = True
    non_target_before: list[tuple[object, ...]] = []
    non_target_after: list[tuple[object, ...]] = []
    for before in base_coverage:
        locus = before["locus"]
        after = final_by[locus]
        line = by_line[locus]
        projection_ok &= all(before[name] == after[name] for name in source_fields)
        before_columns = [split_pipe(before[name]) for name in ("token_glosses_de", "gloss_sources", "scope_states")]
        after_columns = [split_pipe(after[name]) for name in ("token_glosses_de", "gloss_sources", "scope_states")]
        projection_ok &= all(len(column) == len(line) for column in (*before_columns, *after_columns))
        expected_here = 0
        for index, token in enumerate(line):
            surface = token["eva"]
            if surface not in TARGETS:
                non_target_count += 1
                left = (locus, index + 1, surface, before_columns[0][index], before_columns[1][index], before_columns[2][index])
                right = (locus, index + 1, surface, after_columns[0][index], after_columns[1][index], after_columns[2][index])
                non_target_before.append(left)
                non_target_after.append(right)
                projection_ok &= left == right
                continue
            target_count += 1
            expected_here += 1
            raw = record_by[locus, token["token_index"]]
            projection_ok &= before_columns[0][index] == f"[{surface}:?]"
            projection_ok &= before_columns[1][index] == "OPEN"
            projection_ok &= before_columns[2][index] == "UNKNOWN_SURFACE"
            target_gloss = after_columns[0][index]
            projection_ok &= not FILLER.search(target_gloss) and not OPAQUE.search(target_gloss)
            projection_ok &= target_gloss == expected_occurrence_gloss(
                surface, str(raw["line_position"]), token["kind"]
            )
            projection_ok &= after_columns[1][index].startswith("GDT660:")
            wanted_state = "READER_BOUNDARY_UNSTABLE" if not int(raw["reader_exact"]) else None
            if wanted_state:
                projection_ok &= after_columns[2][index] == wanted_state
            else:
                projection_ok &= after_columns[2][index] in {"KNOWN_EXACT_WHOLE", "KNOWN_CONTEXT_LICENSED"}
        before_pairs = list(zip(split_compact(before["unknown_ordinals"]), split_compact(before["unknown_surfaces"])))
        after_pairs = list(zip(split_compact(after["unknown_ordinals"]), split_compact(after["unknown_surfaces"])))
        projection_ok &= after_pairs == [pair for pair in before_pairs if pair[1] not in TARGETS]
        projection_ok &= int(after["known_tokens"]) - int(before["known_tokens"]) == expected_here
        projection_ok &= int(before["unknown_tokens"]) - int(after["unknown_tokens"]) == expected_here
        projection_ok &= int(after["context_licensed_tokens"]) == after_columns[2].count("KNOWN_CONTEXT_LICENSED")
        projection_ok &= int(after["ambiguous_tokens"]) == after_columns[2].count("AMBIGUOUS_ACTIVE_RIVAL")
        projection_ok &= int(after["reader_unstable_tokens"]) == after_columns[2].count("READER_BOUNDARY_UNSTABLE")
    check(
        projection_ok and target_count == 566 and non_target_count == 31773,
        "exactly 566 target positions change and all 31,773 non-target projections remain identical",
    )
    check(non_target_before == non_target_after, "non-target projection sequence equality")
    non_target_sha = canonical_hash(non_target_before)
    check(canonical_hash(non_target_after) == non_target_sha, "non-target projection canonical hash equality")

    complete_loci = {row["locus"] for row in complete}
    one_loci = {row["locus"] for row in one}
    check(
        complete_loci == {row["locus"] for row in coverage if int(row["token_count"]) > 1 and int(row["unknown_tokens"]) == 0},
        "complete table independently derived from coverage",
    )
    check(
        one_loci == {row["locus"] for row in coverage if int(row["known_tokens"]) >= 1 and int(row["unknown_tokens"]) == 1},
        "one-hole table independently derived from coverage",
    )
    check(
        all(int(row["strict_complete"]) == int(
            int(row["ambiguous_tokens"]) == 0 and int(row["reader_unstable_tokens"]) == 0
            and int(row["all_present_exact"]) == 1
        ) for row in complete),
        "strict-complete flags independently recomputed",
    )
    check(
        all(int(row["strict_eligible"]) == int(
            int(row["ambiguous_tokens"]) == 0 and int(row["reader_unstable_tokens"]) == 0
            and int(row["all_present_exact"]) == 1
        ) for row in one),
        "strict-one-hole flags independently recomputed",
    )
    derived_new_complete = complete_loci - {row["locus"] for row in base_complete}
    new_complete = read_tsv(ART / "NEWLY_COMPLETED_LINES.tsv")
    check(derived_new_complete == NEW_COMPLETE, "exact 26 newly complete loci")
    check({row["locus"] for row in new_complete} == NEW_COMPLETE and len(new_complete) == 26,
          "newly-completed artifact exact locus set")
    check(sum(int(row["strict_complete"]) for row in new_complete) == 3,
          "three newly complete lines are strict")
    derived_new_one = one_loci - {row["locus"] for row in base_one}
    new_one = read_tsv(ART / "NEWLY_EXPOSED_ONE_HOLE_LINES.tsv")
    check(len(derived_new_one) == 48, "48 newly exposed one-hole loci")
    check({row["locus"] for row in new_one} == derived_new_one and len(new_one) == 48,
          "newly-exposed one-hole artifact exact locus set")
    check(sum(int(row["strict_eligible"]) for row in new_one) == 13,
          "13 newly exposed one-hole lines are strict")
    check(
        all(
            row["proposed_default_de"] == f"[{row['unknown_surface']}:?]"
            and row["proposal_basis"] == "NEWLY_EXPOSED_BY_GDT660_NO_NEW_CARD"
            and row["proposal_strength"] == "OPEN"
            for row in new_one
        ),
        "new one-hole residuals remain exact opaque wholes without substring inference",
    )

    artifact_allow = read_tsv(ART / "PAGE_ALLOWLIST.tsv")
    inherited_allow = read_tsv(ROOT / ALLOW)
    check(artifact_allow == inherited_allow and len(artifact_allow) == 179,
          "artifact allow-list is the exact inherited 179-page list")

    deck = read_tsv(ART / "TARGET_DECISION_DECK.tsv")
    deck_by = {row["surface"]: row for row in deck}
    check(len(deck) == len(deck_by) == 17 and [row["surface"] for row in deck] == list(TARGET_ORDER),
          "17-row target decision deck and fixed order")
    for index, surface in enumerate(TARGET_ORDER, 1):
        row = deck_by.get(surface, {})
        observed = tuple(int(row.get(name, -1)) for name in (
            "occurrences", "lines", "pages", "reader_exact_occurrences", "split_normalized_occurrences"
        ))
        check(observed == TARGET_COUNTS[surface], f"decision-deck source census:{surface}", repr(observed))
        check(row.get("decision_id") == f"G660-D{index:02d}", f"decision-deck stable id:{surface}")
        check(bool(row.get("composition")) and not FILLER.search(" ".join(row.values())),
              f"decision-deck concrete composition/no filler:{surface}")
        check(
            (
                "exact whitespace-delimited whole" in row.get("selection_rule", "").lower()
                if surface in WHOLE_ORDER else "never by substring" in row.get("selection_rule", "").lower()
            ),
            f"decision-deck exact-dispatch boundary:{surface}",
        )
        if surface in WHOLE_ORDER:
            check(row.get("working_default_de") == EXPECTED_WHOLE_MEANINGS[surface],
                  f"mandatory exact-whole default:{surface}", row.get("working_default_de", ""))
            check(
                row.get("mode") == ("EXACT_WHOLE_WITH_PLACEMENT_RENDER" if surface in {"ydy", "ysheey", "yckhey"} else "EXACT_WHOLE")
                and row.get("status") == "ACCEPT_V37_EXACT_WHOLE_NO_SUBSTRING_EXPORT",
                f"exact-whole decision scope:{surface}",
            )
        else:
            check(
                row.get("mode") == "OCCURRENCE_SCOPED_CONTEXT_CARDS"
                and row.get("status") == "ACCEPT_V37_CONTEXT_SCOPED_NOT_GLOBAL_LEXEME",
                f"occurrence-scoped short-form decision:{surface}",
            )
    check(deck_by["qodain"]["strongest_rival_de"] == "Ansatzdosis II",
          "qodain keeps Ansatzdosis II as the explicit rival")
    check("Samen-/Saatgutposten" in deck_by["s"]["working_default_de"],
          "s decision names a concrete seed post")
    check("Wertfeld" in deck_by["dy"]["working_default_de"],
          "dy decision names a concrete value-field close")

    accepted = read_tsv(ART / "ACCEPTED_WHOLE_SURFACE_DEFAULTS.tsv")
    accepted_by = {row["surface"]: row for row in accepted}
    check(len(accepted) == len(accepted_by) == 15 and [row["surface"] for row in accepted] == list(WHOLE_ORDER),
          "15 accepted exact-whole defaults and fixed order")
    check("s" not in accepted_by and "dy" not in accepted_by, "s and dy excluded from exact-whole defaults")
    for surface in WHOLE_ORDER:
        row = accepted_by.get(surface, {})
        check(row.get("working_meaning_de") == EXPECTED_WHOLE_MEANINGS[surface],
              f"accepted mandatory meaning:{surface}", row.get("working_meaning_de", ""))
        check(
            row.get("occurrences") == str(TARGET_COUNTS[surface][0])
            and row.get("scope") == "EXACT_WHITESPACE_DELIMITED_WHOLE"
            and row.get("status") == "ACCEPT_V37_PROVISIONAL_REPLACEABLE_NO_SUBSTRING_EXPORT",
            f"accepted exact scope/count:{surface}",
        )
        check(
            row.get("composition") == deck_by[surface]["composition"]
            and row.get("strongest_rival_de") == deck_by[surface]["strongest_rival_de"]
            and not FILLER.search(" ".join(row.values())),
            f"accepted composition/rival/no filler:{surface}",
        )

    cross_by = {row["locus"]: row for row in cross_rows}
    exact_map, normalized_map = independent_stable_maps(token_rows, cross_rows)
    surface_counts = Counter(row["eva"] for row in token_rows)
    audit = read_tsv(ART / "ALL_OCCURRENCE_SEMANTIC_AUDIT.tsv")
    audit_by_key = {(row["locus"], row["token_index"]): row for row in audit}
    check(len(audit) == len(audit_by_key) == 566 and set(audit_by_key) == set(record_by),
          "all 566 occurrence audits exactly once")
    check(len({row["occurrence_id"] for row in audit}) == 566, "566 unique occurrence audit IDs")
    audit_ok = True
    for key, raw in record_by.items():
        row = audit_by_key.get(key, {})
        line = by_line[str(raw["locus"])]
        ordinal = int(raw["token_ordinal"])
        surface = str(raw["eva"])
        position = str(raw["line_position"])
        left = "<BOS>" if ordinal == 1 else line[ordinal - 2]["eva"]
        right = "<EOS>" if ordinal == len(line) else line[ordinal]["eva"]
        left_fused = "NONE" if ordinal == 1 else left + surface
        right_fused = "NONE" if ordinal == len(line) else surface + right
        expected_class = expected_context_class(surface, position, str(raw["kind"]))
        expected_scope = "CONTEXT_SCOPED" if surface in {"s", "dy"} else "EXACT_WHOLE"
        wanted_state = (
            "READER_BOUNDARY_UNSTABLE" if not int(raw["reader_exact"])
            else "KNOWN_CONTEXT_LICENSED" if surface in {"s", "dy"} else "KNOWN_EXACT_WHOLE"
        )
        audit_ok &= (
            row.get("page") == raw["page"] and row.get("locus") == raw["locus"]
            and row.get("token_index") == str(raw["token_index"])
            and row.get("ordinal") == str(ordinal) and row.get("line_length") == str(len(line))
            and row.get("surface") == surface and row.get("token_kind") == raw["kind"]
            and row.get("position") == position and row.get("section") == raw["section"]
            and row.get("language") == raw["language"] and row.get("hand") == raw["hand"]
            and row.get("scope_mode") == expected_scope and row.get("context_class") == expected_class
            and row.get("placement_class") == expected_placement(surface, position)
            and row.get("left_surface") == left and row.get("right_surface") == right
            and row.get("left_fused_surface") == left_fused and row.get("right_fused_surface") == right_fused
            and row.get("left_fused_occurrences") == str(0 if left_fused == "NONE" else surface_counts[left_fused])
            and row.get("right_fused_occurrences") == str(0 if right_fused == "NONE" else surface_counts[right_fused])
            and row.get("working_gloss_de") == expected_occurrence_gloss(surface, position, str(raw["kind"]))
            and row.get("working_render_de") == expected_occurrence_render(surface, position, str(raw["kind"]))
            and row.get("reader_exact") == str(raw["reader_exact"])
            and row.get("split_normalized") == str(raw["split_normalized"])
            and row.get("zl3b_line") == raw["zl3b_line"]
            and row.get("it2a_line") == raw["it2a_line"]
            and row.get("rf1b_line") == raw["rf1b_line"]
            and row.get("v36_gloss_de") == f"[{surface}:?]"
            and row.get("v37_gloss_de") == expected_occurrence_gloss(surface, position, str(raw["kind"]))
            and row.get("v36_scope_state") == "UNKNOWN_SURFACE"
            and row.get("v37_scope_state") == wanted_state
            and row.get("exact_surface_dispatch") == str(int(surface in WHOLE_ORDER))
            and row.get("substring_dispatch") == "0"
            and bool(row.get("strongest_rival_de"))
            and not FILLER.search(" ".join(row.values()))
        )
    check(audit_ok, "source-first replay of all occurrence metadata, meanings, readers and dispatch")
    check(sum(int(row["exact_surface_dispatch"]) for row in audit) == 65,
          "exact-whole dispatch is confined to 65 long-form positions")
    check(sum(int(row["substring_dispatch"]) for row in audit) == 0,
          "zero substring-dispatched target positions")

    reader = read_tsv(ART / "READER_VARIANT_AUDIT.tsv")
    reader_by = {row["occurrence_id"]: row for row in reader}
    audit_id_by = {row["occurrence_id"]: row for row in audit}
    reader_ok = len(reader) == len(reader_by) == 566 and set(reader_by) == set(audit_id_by)
    for occurrence_id, row in reader_by.items():
        source = audit_id_by[occurrence_id]
        reader_ok &= all(row[name] == source[name] for name in (
            "page", "locus", "ordinal", "surface", "position", "reader_exact",
            "split_normalized", "all_present_exact", "zl3b_line", "it2a_line", "rf1b_line",
        ))
        reader_ok &= row["semantic_scope"] == source["scope_mode"] and "plaintext" in row["claim_boundary"]
    check(reader_ok, "566-row reader audit is an exact occurrence projection")
    check(sum(int(row["reader_exact"]) for row in reader) == 357, "reader artifact exact count 357")
    check(sum(int(row["split_normalized"]) for row in reader) == 360, "reader artifact normalized count 360")

    sd_census = read_tsv(ART / "S_DY_CONTEXT_CENSUS.tsv")
    sd_by = {row["occurrence_id"]: row for row in sd_census}
    expected_sd_ids = {row["occurrence_id"] for row in audit if row["surface"] in {"s", "dy"}}
    sd_fields = tuple(sd_census[0]) if sd_census else ()
    check(len(sd_census) == len(sd_by) == 501 and set(sd_by) == expected_sd_ids,
          "501-position s/dy context census")
    check(all(all(row[name] == audit_id_by[oid][name] for name in sd_fields) for oid, row in sd_by.items()),
          "s/dy census is an exact subset of the full audit")

    cards = read_tsv(ART / "S_DY_CONTEXT_CARDS.tsv")
    cards_by = {row["context_class"]: row for row in cards}
    check(len(cards) == len(cards_by) == 7 and [row["context_class"] for row in cards] == list(CONTEXT_CARDS),
          "seven ordered s/dy context cards")
    for index, (klass, (surface, count, gloss, render)) in enumerate(CONTEXT_CARDS.items(), 1):
        row = cards_by.get(klass, {})
        members = [item for item in audit if item["context_class"] == klass]
        check(
            row.get("card_id") == f"G660-C{index:02d}" and row.get("surface") == surface
            and row.get("occurrences") == str(count)
            and row.get("lines") == str(len({item['locus'] for item in members}))
            and row.get("pages") == str(len({item['page'] for item in members}))
            and row.get("reader_exact_occurrences") == str(sum(int(item["reader_exact"]) for item in members)),
            f"context-card raw counts:{klass}",
        )
        check(
            row.get("working_meaning_de") == gloss and row.get("token_gloss_de") == gloss
            and row.get("practical_render_de") == render and row.get("working_render_de") == render,
            f"context-card mandatory meaning/render:{klass}", repr(row),
        )
        check(
            bool(row.get("structural_tag")) and bool(row.get("selection_rule"))
            and bool(row.get("strongest_rival_de"))
            and row.get("status") == "ACCEPT_V37_CONTEXT_CARD_NOT_GLOBAL_LEXEME"
            and not FILLER.search(" ".join(row.values())),
            f"context-card scope/rival/no filler:{klass}",
        )

    sd_summary = read_tsv(ART / "S_DY_CONTEXT_SUMMARY.tsv")
    summary_by = {row["context_class"]: row for row in sd_summary}
    summary_ok = len(sd_summary) == len(summary_by) == 7 and set(summary_by) == set(CONTEXT_CARDS)
    for klass, row in summary_by.items():
        members = [item for item in audit if item["context_class"] == klass]
        attachment = "|".join(f"{name}:{count}" for name, count in sorted(Counter(
            item["attachment_class"] for item in members
        ).items())) or "NONE"
        summary_ok &= (
            row["surface"] == CONTEXT_CARDS[klass][0]
            and row["occurrences"] == str(len(members))
            and row["attachment_profile"] == attachment
            and row["reader_exact_occurrences"] == str(sum(int(item["reader_exact"]) for item in members))
            and row["split_normalized_occurrences"] == str(sum(int(item["split_normalized"]) for item in members))
        )
    check(summary_ok, "seven-cell s/dy context summary replay")

    token_by_surface: dict[str, list[dict[str, str]]] = defaultdict(list)
    for token in token_rows:
        token_by_surface[token["eva"]].append(token)
    base_gloss_by = {row["surface"]: row for row in base_glossary}

    def validate_family_atlas(filename: str, families: dict[str, tuple[str, ...]], y_prefix: bool = False) -> None:
        rows = read_tsv(ART / filename)
        expected_keys = [(family, surface) for family, surfaces in families.items() for surface in surfaces]
        by_key = {(row["family"], row["surface"]): row for row in rows}
        check(
            len(rows) == len(by_key) == len(expected_keys)
            and [(row["family"], row["surface"]) for row in rows] == expected_keys,
            f"family-atlas row set/order:{filename}",
        )
        atlas_ok = True
        for family, surfaces in families.items():
            for index, surface in enumerate(surfaces):
                row = by_key.get((family, surface), {})
                members = token_by_surface.get(surface, [])
                expected_meaning = EXPECTED_WHOLE_MEANINGS.get(surface, "ANCHOR_ONLY")
                atlas_ok &= (
                    row.get("role") == ("TARGET" if index == 0 else "VISIBLE_ANCHOR")
                    and row.get("occurrences") == str(len(members))
                    and row.get("lines") == str(len({item["locus"] for item in members}))
                    and row.get("pages") == str(len({item["page"] for item in members}))
                    and row.get("reader_exact_occurrences") == str(sum(
                        exact_map[item["locus"], int(item["token_index"])] for item in members
                    ))
                    and row.get("split_normalized_occurrences") == str(sum(
                        normalized_map[item["locus"], int(item["token_index"])] for item in members
                    ))
                    and row.get("v36_meaning_de") == base_gloss_by.get(surface, {}).get("working_meaning_de", "OPEN")
                    and row.get("v36_source") == base_gloss_by.get(surface, {}).get("source", "OPEN")
                    and row.get("gdt660_default_de") == expected_meaning
                    and "no glyph identity or substring export" in row.get("claim_scope", "")
                )
                if y_prefix:
                    placements = Counter(
                        item["placement_class"] for item in audit if item["surface"] == surface
                    )
                    profile = "|".join(f"{name}:{count}" for name, count in sorted(placements.items())) or "ANCHOR_ONLY"
                    atlas_ok &= row.get("placement_profile") == profile
        check(atlas_ok, f"family-atlas independent source/glossary replay:{filename}")

    validate_family_atlas("MATERIA_AMOUNT_FAMILY_ATLAS.tsv", MATERIA_FAMILIES)
    validate_family_atlas("QUALITY_PREPARATION_FAMILY_ATLAS.tsv", QUALITY_FAMILIES)
    validate_family_atlas("Y_PREFIX_PLACEMENT_ATLAS.tsv", Y_PREFIX_FAMILIES, y_prefix=True)

    glossary_by = {row["surface"]: row for row in glossary}
    check(len(glossary) == len(glossary_by) == 510, "510 unique V37 glossary surfaces")
    check([row["surface"] for row in glossary] == sorted(glossary_by), "V37 glossary stable surface sort")
    check("s" not in glossary_by and "dy" not in glossary_by, "no global s or dy glossary row")
    check(
        set(glossary_by) - set(base_gloss_by) == set(WHOLE_ORDER)
        and set(base_gloss_by) <= set(glossary_by),
        "V37 glossary adds exactly the 15 accepted wholes",
    )
    check(all(glossary_by[surface] == row for surface, row in base_gloss_by.items()),
          "all 495 inherited glossary rows are byte-field identical")
    for surface in WHOLE_ORDER:
        row = glossary_by[surface]
        check(
            row["working_meaning_de"] == EXPECTED_WHOLE_MEANINGS[surface]
            and row["source"] == "GDT660:EXACT_WHOLE"
            and row["strength"] == "PROVISIONAL_CONCRETE_EXACT_WHOLE"
            and row["scope_state"] == "KNOWN_EXACT_WHOLE" and row["priority"] == "210",
            f"V37 exact-whole glossary row:{surface}", repr(row),
        )

    appended = dictionary[len(base_dictionary):]
    check(len(dictionary) == 606 and dictionary[:582] == base_dictionary,
          "V37 dictionary has exact 582-row V36 prefix and 24 additions")
    check(len(appended) == 24, "dictionary appends 15 whole, 7 s/dy and 2 ydy-placement cards")
    exact_entries = appended[:15]
    context_entries = appended[15:22]
    placement_entries = appended[22:]
    check(
        [row["entry"] for row in exact_entries]
        == [f"{surface}@GDT660_EXACT_WHOLE" for surface in WHOLE_ORDER],
        "dictionary exact-whole entry order",
    )
    for surface, row in zip(WHOLE_ORDER, exact_entries):
        check(
            row["kind"] == "EXACT_WHOLE_SURFACE_CARD"
            and row["working_meaning_de"] == EXPECTED_WHOLE_MEANINGS[surface]
            and row["composition"] == accepted_by[surface]["composition"]
            and row["context_rule"] == "only the exact whitespace-delimited surface; no substring inheritance"
            and row["status"] == "NEW_V37_PROVISIONAL_CONCRETE_EXACT_WHOLE",
            f"dictionary exact-whole scope/meaning:{surface}",
        )
    check(
        [row["entry"] for row in context_entries]
        == [f"{CONTEXT_CARDS[klass][0]}@{klass}" for klass in CONTEXT_CARDS],
        "dictionary s/dy context entry order",
    )
    for klass, row in zip(CONTEXT_CARDS, context_entries):
        check(
            row["kind"] == "OCCURRENCE_SCOPED_CONTEXT_CARD"
            and row["working_meaning_de"] == CONTEXT_CARDS[klass][3]
            and row["composition"] == cards_by[klass]["structural_tag"]
            and row["context_rule"] == cards_by[klass]["selection_rule"]
            and row["status"] == "NEW_V37_CONTEXT_CARD_NOT_GLOBAL_LEXEME",
            f"dictionary occurrence-scoped context card:{klass}",
        )
    check(
        [(row["entry"], row["working_meaning_de"], row["kind"]) for row in placement_entries]
        == [
            ("ydy@YDY_MEDIAL_NEXT_VALUE", "nächstes Wertfeld:", "EXACT_WHOLE_PLACEMENT_CARD"),
            ("ydy@YDY_EOS_CLOSE", ".", "EXACT_WHOLE_PLACEMENT_CARD"),
        ],
        "two exact-whole ydy placement cards",
    )
    check(not any(row["entry"] in {"s", "dy"} for row in dictionary),
          "no bare global s/dy dictionary entry")
    check(not any(FILLER.search(" ".join(row.values())) for row in appended),
          "no generic filler in 24 appended dictionary cards")

    rounds = read_tsv(ART / "ROUND_COVERAGE_COUNTS.tsv")
    round_expected = (
        ("V36", "BASE", 582, *tuple(BASE_METRICS.values())),
        ("V37", "15_EXACT_WHOLES+7_S_DY_CONTEXT+2_YDY_PLACEMENT", 606, *tuple(FINAL_METRICS.values())),
    )
    round_actual = tuple((
        row["version"], row["added_cards"], int(row["dictionary_entries"]),
        *tuple(int(row[name]) for name in BASE_METRICS),
    ) for row in rounds)
    check(round_actual == round_expected, "V36/V37 coverage round packet", repr(round_actual))

    target_lines = read_tsv(ART / "TARGET_LINE_TRANSLATIONS.tsv")
    target_line_by = {row["locus"]: row for row in target_lines}
    expected_target_loci = {str(row["locus"]) for row in records}
    check(
        len(target_lines) == len(target_line_by) == 510
        and set(target_line_by) == expected_target_loci
        and sum(int(row["target_occurrences"]) for row in target_lines) == 566,
        "510 target-line translations covering all 566 positions",
    )
    line_ok = True
    practical_ok = True
    semantic_markers = {
        "cholkar": "Trockengut: heiße Fraktion I", "qodain": "Qualitätsgrad II",
        "lcho": "Trockenansatz aus Drogenholz", "kchor": "Drogenportion, heiß-trocken",
        "okchan": "heiß-trockener Ansatz, Grad I", "opchar": "trockene Pulverfraktion I im Ansatz",
        "schokey": "heiß-trockener Samenansatz in der Gradmitte",
        "solkchy": "Saatgut, heiß-trocken am Gradanfang", "yckhey": "Arzneikompositum in der Gradmitte",
        "lshcthy": "feuchtes CTH-Drogenholz", "ysheey": "feucht am Gradende",
        "cheeytal": "Rohstoffklasse I: trocken am Gradende, kalt am Gradanfang",
        "ochedar": "trockener Ansatz in der Gradmitte, abgemessene Fraktion I",
        "cheoty": "trocken angesetzte kalte Zubereitung am Gradanfang",
    }
    audit_by_locus: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in audit:
        audit_by_locus[row["locus"]].append(row)
    for locus, members in audit_by_locus.items():
        members.sort(key=lambda row: int(row["ordinal"]))
        row = target_line_by.get(locus, {})
        final = final_by[locus]
        base = base_by[locus]
        translation = row.get("v37_working_translation_de", "")
        line_ok &= (
            row.get("target_occurrences") == str(len(members))
            and row.get("target_ordinals") == "|".join(item["ordinal"] for item in members)
            and row.get("target_surfaces") == "|".join(item["surface"] for item in members)
            and row.get("context_or_placement_classes") == "|".join(
                item["context_class"] if item["context_class"] != "EXACT_WHOLE" else item["placement_class"]
                for item in members
            )
            and row.get("zl3b_line") == final["zl3b_line"]
            and row.get("v36_token_glosses_de") == base["token_glosses_de"]
            and row.get("v37_token_glosses_de") == final["token_glosses_de"]
            and row.get("v36_unknown_tokens") == base["unknown_tokens"]
            and row.get("v37_unknown_tokens") == final["unknown_tokens"]
            and row.get("v37_complete") == str(int(int(final["unknown_tokens"]) == 0))
        )
        practical_ok &= not FILLER.search(translation)
        practical_ok &= all(f"[{item['surface']}:?]" not in translation for item in members)
        if int(final["unknown_tokens"]) == 0:
            practical_ok &= not OPAQUE.search(translation)
        for item in members:
            surface, position, kind = item["surface"], item["position"], item["token_kind"]
            if surface in semantic_markers:
                practical_ok &= semantic_markers[surface] in translation
            elif surface == "s":
                practical_ok &= ("[Beschriftungszeichen]" if kind == "L" else "Samen-/Saatgutposten") in translation
            elif surface == "dy" and position == "BOS":
                practical_ok &= "voriges Qualitäts-/Wertfeld geschlossen" in translation
            elif surface == "ydy" and position == "MEDIAL":
                practical_ok &= "nächstes Wertfeld:" in translation
            elif surface in {"dy", "ydy"} and position == "EOS":
                practical_ok &= translation.endswith(".")
    check(line_ok, "target-line source, tokenwise and coverage identity")
    check(practical_ok, "every target carrier has its concrete practical rendering and no target placeholder")

    result = json.loads((ART / "RESULT.json").read_text(encoding="utf-8"))
    result_core = {key: value for key, value in result.items() if key != "content_sha256"}
    check(
        result.get("schema") == "GDT660_SEVENTEEN_RESIDUAL_CONCRETE_COMPLETION_RESULT_V1"
        and result.get("experiment_id") == "GDT660"
        and result.get("status") == "PASS_566_TARGET_POSITIONS__V37",
        "result identity and status",
    )
    check(result.get("content_sha256") == canonical_hash(result_core), "result canonical content hash")
    guard = result.get("guard", {})
    check(
        guard.get("token_query") == token_stats and guard.get("cross_query") == cross_stats,
        "result guarded-query statistics",
    )
    check(
        guard.get("allowed_pages") == 179 and guard.get("f1r") == "EXCLUDED_BY_EXACT_ALLOWLIST"
        and guard.get("f84") == guard.get("f84r") == "FORBIDDEN"
        and guard.get("new_pages") == guard.get("new_images") == 0,
        "result page/image ceiling",
    )
    target_result = result.get("targets", {})
    check(
        (
            target_result.get("surface_types"), target_result.get("exact_whole_surfaces"),
            target_result.get("context_scoped_surfaces"), target_result.get("positions"),
            target_result.get("lines"), target_result.get("pages"),
            target_result.get("reader_exact_positions"), target_result.get("split_normalized_positions"),
        ) == (17, 15, 2, 566, 510, 169, 357, 360),
        "result 17/15/2 and 566/510/169/357/360 target packet",
    )
    check(
        target_result.get("surface_counts") == {surface: TARGET_COUNTS[surface][0] for surface in TARGET_ORDER}
        and target_result.get("all_positions_concrete") is True
        and target_result.get("substring_dispatch_positions") == 0,
        "result per-surface counts and no-substring dispatch",
    )
    context_result = result.get("context_cards", {})
    check(
        context_result.get("s_dy_cards") == 7
        and context_result.get("counts") == {klass: spec[1] for klass, spec in CONTEXT_CARDS.items()}
        and context_result.get("global_s_lexeme_added") is False
        and context_result.get("global_dy_lexeme_added") is False,
        "result seven-card context packet and no global short lexemes",
    )
    coverage_result = result.get("coverage", {})
    check(
        coverage_result.get("base") == BASE_METRICS and coverage_result.get("final") == FINAL_METRICS,
        "result V36/V37 metrics",
    )
    check(
        coverage_result.get("affected_lines") == 510
        and coverage_result.get("newly_completed_lines") == 26
        and set(coverage_result.get("newly_completed_loci", [])) == NEW_COMPLETE
        and coverage_result.get("newly_exposed_one_hole_lines") == 48
        and set(coverage_result.get("newly_exposed_one_hole_loci", [])) == derived_new_one,
        "result completion/one-hole deltas",
    )
    check(
        coverage_result.get("non_target_token_positions_unchanged") == 31773
        and coverage_result.get("non_target_exactly_unchanged") is True
        and coverage_result.get("non_target_before_sha256") == non_target_sha
        and coverage_result.get("non_target_after_sha256") == non_target_sha
        and non_target_sha == "0fa958d8876e79fbe95ea361a45fe1d19d721f4cc5761282bd4b0af55d73204c",
        "result immutable non-target projection and frozen hash",
    )
    working_result = result.get("working_dictionary", {})
    check(
        working_result == {
            "added_exact_whole_entries": 15, "added_s_dy_context_entries": 7,
            "added_ydy_placement_entries": 2, "global_s_dy_glossary_rows": 0,
            "v36_entries": 582, "v36_glossary_surfaces": 495,
            "v37_entries": 606, "v37_glossary_surfaces": 510,
        },
        "result dictionary/glossary packet",
    )
    contract = result.get("determinism_contract", {})
    expected_output_paths = {str(BASE / "artifacts" / name) for name in OUTPUT_NAMES}
    check(
        contract.get("builder_supports_artifact_dir_cli") is True
        and contract.get("exact_whole_dispatch_requires_token_equality") is True
        and contract.get("s_dy_occurrence_dispatcher_required") is True
        and set(contract.get("replay_files", [])) == expected_output_paths | {str(BASE / "artifacts/RESULT.json")},
        "result deterministic exact-token replay contract",
    )
    claim = str(result.get("claim_boundary", "")).lower()
    check(
        all(term in claim for term in ("replaceable", "position-scoped", "no substring", "no", "f84"))
        and "plaintext" in claim and "phonetics" in claim,
        "result exploratory claim ceiling",
    )
    inputs = result.get("inputs", {})
    outputs = result.get("outputs", {})
    check(
        len(inputs) == 11 and all(
            not Path(path).is_absolute() and (ROOT / path).is_file()
            and digest == sha256(ROOT / path) for path, digest in inputs.items()
        ),
        "result eleven relative input provenance hashes",
    )
    check(
        set(outputs) == expected_output_paths and all(
            not Path(path).is_absolute() and (ROOT / path).is_file()
            and digest == sha256(ROOT / path) for path, digest in outputs.items()
        ),
        "result twenty relative output hashes",
    )

    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    check(
        manifest.get("experiment_id") == "GDT660"
        and manifest.get("slug") == "seventeen_residual_concrete_completion"
        and manifest.get("sealed_data") == {"f84": "FORBIDDEN", "f84r": "FORBIDDEN"}
        and manifest.get("commands") == {
            "run": f"python3 {BASE}/src/run.py", "validate": f"python3 {BASE}/src/validate.py"
        },
        "manifest identity, commands and explicit f84/f84r seals",
    )

    safe_pages = True
    for name in OUTPUT_NAMES:
        for row in read_tsv(ART / name):
            page = row.get("page", "")
            locus_page = row.get("locus", "").split(".", 1)[0]
            safe_pages &= page != "f1r" and not page.startswith("f84")
            safe_pages &= locus_page != "f1r" and not locus_page.startswith("f84")
    check(safe_pages, "no f1r/f84/f84r row in any generated TSV")
    semantic_names = (
        "TARGET_DECISION_DECK.tsv", "ACCEPTED_WHOLE_SURFACE_DEFAULTS.tsv",
        "ALL_OCCURRENCE_SEMANTIC_AUDIT.tsv", "S_DY_CONTEXT_CARDS.tsv",
        "TARGET_LINE_TRANSLATIONS.tsv", "V37_WORKING_TOKEN_GLOSSARY.tsv",
        "WORKING_DICTIONARY_V37.tsv", "COMPLETE_PASSAGES_V37.tsv",
        "ONE_UNKNOWN_PASSAGES_V37.tsv",
    )
    filler_hits = [name for name in semantic_names if FILLER.search((ART / name).read_text(encoding="utf-8"))]
    check(not filler_hits, "no generic work/process filler in semantic artifacts", repr(filler_hits))

    method_text = (ROOT / BASE / "METHOD.md").read_text(encoding="utf-8")
    report_text = REPORT.read_text(encoding="utf-8")
    run_text = RUN.read_text(encoding="utf-8")
    check(
        "vollständige, aufeinanderfolgende Lesertoken" in method_text
        and "Konkatenation exakt die ZL3b-Zieloberfläche" in method_text
        and "concatenated_span_count" in run_text,
          "360 count explicitly uses complete consecutive reader-token concatenation")
    check(
        not re.search(r"(?<!G660-T)\b548\b", method_text + "\n" + report_text)
        and not any(value == 548 for value in target_result.values() if isinstance(value, int)),
        "withdrawn 548 substring count is absent from claims and result metadata",
    )
    check("516" not in method_text + report_text,
          "unimplemented 516 full-alignment capacity is not claimed")

    # Deliberately the final validation action: execute, never import, the builder.
    try:
        with tempfile.TemporaryDirectory(prefix="gdt660_validator_replay_") as directory:
            replay = Path(directory)
            done = subprocess.run(
                [sys.executable, str(RUN), "--artifact-dir", str(replay)], cwd=ROOT,
                text=True, capture_output=True, check=False,
            )
            check(done.returncode == 0, "builder tempdir CLI replay exits zero", done.stderr or done.stdout)
            expected_names = set(OUTPUT_NAMES) | {"RESULT.json"}
            actual_names = {path.name for path in replay.iterdir() if path.is_file()}
            check(actual_names == expected_names, "builder replay exact 21-file output set", repr(sorted(actual_names)))
            replay_ok = done.returncode == 0 and actual_names == expected_names
            if replay_ok:
                replay_ok = all((ART / name).read_bytes() == (replay / name).read_bytes() for name in expected_names)
            check(replay_ok, "byte-identical external builder replay of all 21 files")
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
        # Source-first guarded recensus. No GDT660 artifact is read above.
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
        records, by_line, cross_by = independent_records(token_rows, cross_rows, TARGETS)
        raw_identity = len(by_line) == 4128 and set(by_line) <= set(cross_by)
        for locus, line in by_line.items():
            raw_identity &= " ".join(row["eva"] for row in line) == cross_by[locus]["zl3b_clean"]
        check(raw_identity, "guarded token/line source identity")
        for surface in TARGET_ORDER:
            observed = census(records, surface)
            check(observed == TARGET_COUNTS[surface], f"raw five-way target census:{surface}", repr(observed))
        check(
            (len(records), len({str(row['locus']) for row in records}), len({str(row['page']) for row in records}))
            == (566, 510, 169),
            "566/510/169 aggregate target census",
        )
        check(sum(int(row["reader_exact"]) for row in records) == 357, "357 all-reader exact target positions")
        check(sum(int(row["split_normalized"]) for row in records) == 360, "360 split-normalized target positions")
        check(Counter(str(row["line_position"]) for row in records) == TARGET_POSITIONS, "aggregate target positions")
        check(Counter(str(row["kind"]) for row in records) == TARGET_KINDS, "aggregate target token kinds")
        check(
            Counter(str(row["section"]) for row in records)
            == {"B": 80, "C": 2, "H": 345, "P": 38, "S": 72, "T": 29},
            "target section spread",
        )
        check(Counter(str(row["language"]) for row in records) == {"A": 315, "B": 251},
              "target language spread")
        check(Counter(str(row["hand"]) for row in records) == {"1": 303, "2": 175, "3": 71, "5": 10, "@": 7},
              "target hand spread")
        s_records = [row for row in records if row["eva"] == "s"]
        dy_records = [row for row in records if row["eva"] == "dy"]
        check(Counter(str(row["line_position"]) for row in s_records) == S_POSITIONS, "standalone s positions")
        check(Counter(str(row["line_position"]) for row in dy_records) == DY_POSITIONS, "standalone dy positions")
        check(Counter(str(row["kind"]) for row in s_records) == S_KINDS, "standalone s P/L kinds")
        check(Counter(str(row["kind"]) for row in dy_records) == DY_KINDS, "standalone dy P kind")
        check(
            {str(row["locus"]) for row in s_records if row["kind"] == "L"} == S_LABEL_LOCI
            and all(row["line_position"] == "ONLY" for row in s_records if row["kind"] == "L"),
            "eight standalone s label-only loci",
        )

        # Only now may generated artifacts be inspected.
        validate_release(check, token_rows, cross_rows, token_stats, cross_stats, records, by_line)
    except Exception as exc:
        issues.append(f"validator exception: {type(exc).__name__}: {exc}")

    validation = {
        "schema": "GDT660_VALIDATION_V1", "experiment_id": "GDT660",
        "status": "PASS" if not issues else "FAIL",
        "source_first_guarded_queries": True, "builder_imported": False,
        "external_tempdir_byte_replay": not issues,
        "checks_passed": len(passed), "checks_failed": len(issues),
        "passed": passed, "issues": issues,
    }
    VALIDATION.parent.mkdir(parents=True, exist_ok=True)
    VALIDATION.write_text(
        json.dumps(validation, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    if issues:
        print(f"GDT660 validation FAIL: {len(issues)} issue(s), {len(passed)} checks passed")
        for issue in issues:
            print(f"- {issue}")
        return 1
    print(f"GDT660 validation PASS: {len(passed)} checks")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
