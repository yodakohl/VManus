#!/usr/bin/env python3
"""Independent validator for GDT782's six target-external field audit."""

from __future__ import annotations

import csv
import hashlib
import io
import json
import os
import re
import subprocess
import sys
import tempfile
from collections import Counter, defaultdict
from pathlib import Path
from typing import Iterable, Mapping, Sequence

sys.dont_write_bytecode = True


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
EXP = ROOT / "experiments/yolo/gdt782_recurrent_six_target_external_field_adjudication"
SRC = EXP / "src"
ART = EXP / "artifacts"
RUN = SRC / "run.py"
LOCKS = SRC / "SOURCE_LOCK.tsv"
CANDIDATES = SRC / "TARGET_6_CANDIDATES.tsv"
MANUAL = SRC / "MANUAL_READER_ASSESSMENTS.tsv"
FINAL = SRC / "TARGET_6_FINAL_SPECS.tsv"
REPORT = EXP / "REPORT.md"

ALLOWLIST = ROOT / "experiments/yolo/gdt635_initial_head_same_remainder_swaps/artifacts/PAGE_ALLOWLIST.tsv"
TOKENS = Path("transcription/voynich_zl3b_tokens.tsv")
CROSS = Path("transcription/voynich_cross_transcription_lines.tsv")
LINES = Path("transcription/voynich_zl3b_lines.tsv")
COMPACT = ROOT / "experiments/yolo/gdt734_v99r7_recurrent_unknown_family_dispatch/artifacts/V99R7_32339_COMPACT_CELL_REGISTER.tsv"
DICTIONARY = ROOT / "experiments/yolo/gdt734_v99r7_recurrent_unknown_family_dispatch/artifacts/V99R7_1606_COMPLETE_WORD_CONFIDENCE.tsv"
AXIS_SPECS = ROOT / "experiments/yolo/gdt739_twelve_whole_local_dimension_dispatch/src/ANCHOR_AXIS_SPECS.tsv"
G754 = ROOT / "experiments/yolo/gdt754_active_productive_compound_provenance_sieve/artifacts/PROVENANCE_SIEVE_172_DECISIONS.tsv"
G759 = ROOT / "experiments/yolo/gdt759_quantity_part_state_construction_atlas/artifacts/EXACT_122_CONSTRUCTION_SPAN_ATLAS.tsv"
G768 = ROOT / "experiments/yolo/gdt768_chor_shor_part_identity_tournament/artifacts/GDT768_6_WORKING_DICTIONARY.tsv"
G781_SELECTED = ROOT / "experiments/yolo/gdt781_ol_remaining_23_exploratory_whole_projection/artifacts/GDT781_23_SELECTED_ATLAS.tsv"
G781_RENDERER = ROOT / "experiments/yolo/gdt781_ol_remaining_23_exploratory_whole_projection/artifacts/GDT781_376_RENDERER.tsv"
G781_ANALOGY = ROOT / "experiments/yolo/gdt781_ol_remaining_23_exploratory_whole_projection/artifacts/GDT781_RAW_COMPLETE_WHOLE_ANALOGY_RELATIONS.tsv"

STATUS = (
    "PASS__20_CACHE_OCCURRENCES__14_READER_EXACT__6_TARGET_MASKED__"
    "8_TARGET_EXTERNAL__65_EXTERNAL_NEIGHBORS__5_REVISED__1_KEPT__"
    "270_CONTEXTUAL__106_FALLBACKS__230_CONSUMED__ZERO_COMPONENT_EXPORT"
)
TARGET_ORDER = (
    "cheedaiin", "chedor", "chockhar", "keeor", "shdair", "sheckhal",
)
TARGETS = frozenset(TARGET_ORDER)
TARGET_COORDINATES = {
    ("f112v.23", 6, "cheedaiin"): "G781-S004",
    ("f76r.53", 5, "chedor"): "G781-S013",
    ("f100v.20", 8, "chockhar"): "G781-S001",
    ("f113v.25", 10, "keeor"): "G781-S005",
    ("f85r1.11", 3, "shdair"): "G781-S018",
    ("f81v.7", 3, "sheckhal"): "G781-S017",
}
EXTERNAL_IDS = {
    ("f17v.22", 4, "keeor"): "G782-X001",
    ("f83v.20", 6, "sheckhal"): "G782-X002",
    ("f86v3.27", 8, "cheedaiin"): "G782-X003",
    ("f104r.18", 5, "chockhar"): "G782-X004",
    ("f105v.26", 8, "chedor"): "G782-X005",
    ("f106v.32", 2, "shdair"): "G782-X006",
    ("f107r.10", 8, "cheedaiin"): "G782-X007",
    ("f112v.24", 8, "cheedaiin"): "G782-X008",
}
EXPECTED_RAW = Counter({
    "cheedaiin": 5, "chedor": 3, "chockhar": 2,
    "keeor": 6, "shdair": 2, "sheckhal": 2,
})
EXPECTED_EXACT = Counter({
    "cheedaiin": 4, "chedor": 2, "chockhar": 2,
    "keeor": 2, "shdair": 2, "sheckhal": 2,
})
EXPECTED_EXTERNAL = Counter({
    "cheedaiin": 3, "chedor": 1, "chockhar": 1,
    "keeor": 1, "shdair": 1, "sheckhal": 1,
})
EXPECTED_FINAL = {
    "cheedaiin": ("C1_GDT781_RIVAL_1", "Trockenmenge, Endstufe", "REVISE", "C1_MANUAL_STAGE_TIEBREAK_C0_IDENTITY"),
    "chedor": ("C3_EXTERNAL_REFINEMENT", "getrockneter Arzneistoff", "REVISE", "C1_GRAMMAR_COMPLEMENT_C0_IDENTITY"),
    "chockhar": ("C3_EXTERNAL_REFINEMENT", "erhitzter Ansatz", "REVISE", "C0_SINGLE_EXTERNAL_FIELD_C0_IDENTITY"),
    "keeor": ("C3_EXTERNAL_REFINEMENT", "getrockneter Arzneistoff", "REVISE", "C0_AGGRESSIVE_FIELD_TRANSFER_C0_IDENTITY"),
    "shdair": ("C0_GDT781_DEFAULT", "Arzneistoff", "KEEP", "C1_ROLE_CONFIRMATION_C0_IDENTITY"),
    "sheckhal": ("C3_EXTERNAL_REFINEMENT", "trockene Arzneimischung", "REVISE", "C1_SINGLE_R2_PLUS_OLD_ANALOGY_C0_IDENTITY"),
}
EXPECTED_SOURCE_HASHES = {
    "experiments/yolo/gdt635_initial_head_same_remainder_swaps/artifacts/PAGE_ALLOWLIST.tsv": "f0def5a04bd91443cf4770c78f1b67e62cac2060627d8de38faba27899188483",
    "transcription/voynich_zl3b_tokens.tsv": "6a061a26edc05ff37dc386c2215774c229a5ff087d3091e68bdd4983a6c007aa",
    "transcription/voynich_cross_transcription_lines.tsv": "ff3a4559004a29764c60102326de154b29fbba06a2a206bdd76d7feda432e16c",
    "transcription/voynich_zl3b_lines.tsv": "7520dd4c11f4d23c8492e4b2a52cc0fcbda6d9fc88a96ead8f1c31081a4d7ed2",
    "experiments/yolo/gdt734_v99r7_recurrent_unknown_family_dispatch/artifacts/V99R7_32339_COMPACT_CELL_REGISTER.tsv": "47e8c7375503c2af7c95049392660de23556993ef78c1f24a10af6d9d7a1ed3c",
    "experiments/yolo/gdt734_v99r7_recurrent_unknown_family_dispatch/artifacts/V99R7_1606_COMPLETE_WORD_CONFIDENCE.tsv": "9646b8960840f0a6bb10985f0f9d7eef1237725f0763b712a96f0190aeaf7816",
    "experiments/yolo/gdt739_twelve_whole_local_dimension_dispatch/src/ANCHOR_AXIS_SPECS.tsv": "0561329a79ce6c32e8eea4ca58a38e5a5f9602bf181beb79d741543b95aa2b53",
    "experiments/yolo/gdt781_ol_remaining_23_exploratory_whole_projection/artifacts/GDT781_23_SELECTED_ATLAS.tsv": "9b7026e64499bf952ab6d84554c5d60c20ad05f99278841df8e1057250bfaa40",
    "experiments/yolo/gdt781_ol_remaining_23_exploratory_whole_projection/artifacts/GDT781_376_RENDERER.tsv": "cf6c5a55cb44ed1e6b3ba0d0617d79b506897d2621d30914f5d9af3c24384be3",
    "experiments/yolo/gdt781_ol_remaining_23_exploratory_whole_projection/artifacts/GDT781_23_RECURRENCE_EVIDENCE_CARDS.tsv": "aedb745fa1d253305dc551828509890fafa1fd5c5ad20c9bf59c43ede8e58466",
    "experiments/yolo/gdt781_ol_remaining_23_exploratory_whole_projection/artifacts/GDT781_RAW_COMPLETE_WHOLE_ANALOGY_RELATIONS.tsv": "a42a22c9a80b9997f1a17e35e1d6766915ce97a8f28a66939e413f367eaa5445",
    "experiments/yolo/gdt781_ol_remaining_23_exploratory_whole_projection/artifacts/RESULT.json": "ea5052886c60624204552fb140743a6991a618a7d1749f6e2598f73c094aae3a",
    "experiments/yolo/gdt759_quantity_part_state_construction_atlas/artifacts/EXACT_122_CONSTRUCTION_SPAN_ATLAS.tsv": "456ffe9569f953ef69ac86d82e6d428fda22f41a7531d4722833a024eaed77c4",
    "experiments/yolo/gdt735_historical_semantic_bridge_atlas/artifacts/SEMANTIC_BRIDGE_ROLE_DICTIONARY.tsv": "b07b7b9e501c9c05a6b1d729c62e702405d397e69cf501d0ddba70b013eddb1e",
    "experiments/yolo/gdt735_historical_semantic_bridge_atlas/artifacts/HISTORICAL_SLOT_CENSUS.tsv": "84f8aa3b05dd5771072e584e90275260a96bdc849e40dce4fcde3103074366c8",
    "experiments/yolo/gdt754_active_productive_compound_provenance_sieve/artifacts/PROVENANCE_SIEVE_172_DECISIONS.tsv": "25f2af6f38af1b8aee8fb2d6160f2742ab28ec71e704b51df3daf6d03251718d",
    "experiments/yolo/gdt768_chor_shor_part_identity_tournament/artifacts/GDT768_6_WORKING_DICTIONARY.tsv": "2c9c805b12aa1adf1b858b8e4c6355a1b30ebbc85f0b4d0f74578a4a4a6ccde9",
    "tools/relation_edge_intake.py": "fb8447470aa81ed608b90aedf7478893ddf6a445351aa12ab23c6fd725be3a47",
    "vmanus-exp": "53b69eec8412b54d1248fd52d91c06e0eabc7f436b9015d0cfdb0746606c1528",
}
EXPECTED_SPEC_HASHES = {
    "candidates": "ad4dcd3dff6e97e4fb278660353b0324b5be2ba2f7603185e6ac545d9af2b2e5",
    "manual_assessments": "263423164ff991a8bf9ef21800ef49aac0a1183e2c30f423b5e430c8cd35c310",
    "final_specs": "a01a8adf9a23316627c34e91216fe9ec6f7742b57966f163cf357cc93e5c09af",
}
OUTPUT_NAMES = (
    "GDT782_20_CACHE_OCCURRENCE_ATLAS.tsv",
    "GDT782_14_READER_EXACT_OCCURRENCE_ATLAS.tsv",
    "GDT782_65_EXTERNAL_NEIGHBOR_ATLAS.tsv",
    "GDT782_8_EXTERNAL_FIELD_SUMMARY.tsv",
    "GDT782_REGISTERED_CONSTRUCTION_CONTACTS.tsv",
    "GDT782_23_CANDIDATE_SCORECARDS.tsv",
    "GDT782_18_MANUAL_READER_ASSESSMENTS.tsv",
    "GDT782_6_WORKING_REVISIONS.tsv",
    "GDT782_6_TARGET_PASSAGE_PATCHES.tsv",
    "GDT782_8_EXTERNAL_WORKING_READER.tsv",
    "GDT782_376_RENDERER.tsv",
    "GDT782_GDT388_EXTERNAL_FIELD_PACKET.tsv",
    "GDT782_RELATION_EDGE_CROSSWALK.tsv",
    "RELATION_PACKET_INTAKE.json",
    "RESULT.json",
)
AXIS_ORDER = (
    "HOT", "COLD", "DRY", "MOIST", "AMOUNT", "PART", "MATERIAL",
    "PREPARATION", "PROCESS", "CLOSE", "PASS", "BEGIN_STAGE",
    "MIDDLE_STAGE", "END_STAGE", "LEVEL_II", "LEVEL_III",
)
DIMENSIONS = {
    "THERMAL": ("HOT", "COLD"),
    "MOISTURE": ("DRY", "MOIST"),
    "STAGE": ("BEGIN_STAGE", "MIDDLE_STAGE", "END_STAGE"),
}
STAGE_PATTERNS = {
    "BEGIN_STAGE": re.compile(r"anfangsstufe|gradanfang|anfang des grades|grundform|grundstufe", re.I),
    "MIDDLE_STAGE": re.compile(r"mittelstufe|gradmitte|mitte des grades|mittlere|mittelstufig", re.I),
    "END_STAGE": re.compile(r"endstufe|gradende|ende des grades|vollständig|fertig|abgeschlossen", re.I),
    "LEVEL_II": re.compile(r"(?:stufe|grad|index|wert|klasse|charge) ii\b", re.I),
    "LEVEL_III": re.compile(r"(?:stufe|grad|index|wert|klasse|charge) iii\b", re.I),
}
RETIRED = ("pulver", "samen", "saat", "wurzel", "holz")


class Audit:
    def __init__(self) -> None:
        self.count = 0
        self.labels: list[str] = []

    def check(self, condition: bool, label: str) -> None:
        if not condition:
            raise AssertionError(label)
        self.count += 1
        self.labels.append(label)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def unique(rows: Sequence[Mapping[str, str]], field: str) -> dict[str, Mapping[str, str]]:
    output: dict[str, Mapping[str, str]] = {}
    for row in rows:
        key = row[field]
        if key in output:
            raise AssertionError(f"duplicate {field}: {key}")
        output[key] = row
    return output


def split_axes(value: str) -> set[str]:
    return set() if value in {"", "NONE", "OPEN"} else set(value.split("|"))


def joined(values: Iterable[str]) -> str:
    selected = set(values)
    return "|".join(axis for axis in AXIS_ORDER if axis in selected) or "NONE"


def count_string(values: Iterable[str]) -> str:
    counts = Counter(values)
    return "|".join(
        f"{axis}:{counts[axis]}" for axis in AXIS_ORDER if counts[axis]
    ) or "NONE"


def line_position(ordinal: int, length: int) -> str:
    if length == 1:
        return "SINGLE"
    if ordinal == 1:
        return "FIRST"
    if ordinal == length:
        return "LAST"
    return "MIDDLE"


def guarded_query(relative: Path, pages: set[str], columns: str) -> tuple[list[dict[str, str]], dict[str, int]]:
    command = [str(ROOT / "vmanus-exp"), "query-tsv", str(relative), "--selector", "page"]
    for page in sorted(pages):
        command.extend(("--allow", page))
    command.extend(("--columns", columns, "--forbid-prefix", "f84", "--forbid-prefix", "f84r"))
    completed = subprocess.run(command, cwd=ROOT, text=True, capture_output=True, check=False)
    if completed.returncode:
        raise RuntimeError(completed.stderr or "guarded query failed")
    stats_lines = [line for line in completed.stderr.splitlines() if line.startswith("GUARD_STATS ")]
    if len(stats_lines) != 1:
        raise RuntimeError("guard stats missing")
    rows = list(csv.DictReader(io.StringIO(completed.stdout), delimiter="\t"))
    if any(row["page"].startswith("f84") for row in rows):
        raise AssertionError("sealed selector materialized")
    return rows, {key: int(value) for key, value in json.loads(stats_lines[0][12:]).items()}


def validate_locks(audit: Audit) -> None:
    rows = read_tsv(LOCKS)
    audit.check(len(rows) == 19, "nineteen source locks")
    by_path = unique(rows, "path")
    audit.check(set(by_path) == set(EXPECTED_SOURCE_HASHES), "exact source-lock path set")
    for relative, expected in EXPECTED_SOURCE_HASHES.items():
        path = Path(relative)
        audit.check(not path.is_absolute() and ".." not in path.parts, f"safe lock path {relative}")
        audit.check(by_path[relative]["expected_sha256"] == expected, f"declared lock hash {relative}")
        audit.check(sha256(ROOT / path) == expected, f"source rehash {relative}")
    audit.check(sha256(LOCKS) == "e49bc9d925c30329961c9defc50f264d9c1cb5b216dfcfdd9909bf3e220fb999", "source-lock table hash")
    audit.check(sha256(CANDIDATES) == EXPECTED_SPEC_HASHES["candidates"], "candidate source hash")
    audit.check(sha256(MANUAL) == EXPECTED_SPEC_HASHES["manual_assessments"], "manual source hash")
    audit.check(sha256(FINAL) == EXPECTED_SPEC_HASHES["final_specs"], "final source hash")


def reconstruct_occurrences(audit: Audit) -> tuple[
    list[dict[str, object]], dict[str, list[dict[str, str]]], dict[str, dict[str, str]],
    dict[tuple[str, int], int], dict[str, dict[str, str]], dict[str, dict[str, int]],
]:
    pages = {row["page"] for row in read_tsv(ALLOWLIST)}
    audit.check(len(pages) == 179, "179-page inherited selector")
    tokens, token_stats = guarded_query(
        TOKENS, pages, "page,locus,token_index,eva,section,language,hand"
    )
    cross_rows, cross_stats = guarded_query(
        CROSS, pages, "page,locus,zl3b_clean,it2a_clean,rf1b_clean,all_three_present,all_present_exact"
    )
    line_rows, line_stats = guarded_query(
        LINES, pages, "page,locus,line_number,section,language,hand,token_count"
    )
    expected_stats = {
        "allowed_pages": 179,
        "tokens": {"selected": 32339, "skipped_forbidden": 709, "skipped_not_allowed": 5940},
        "cross": {"selected": 4137, "skipped_forbidden": 98, "skipped_not_allowed": 1151},
        "lines": {"selected": 4137, "skipped_forbidden": 98, "skipped_not_allowed": 1150},
    }
    audit.check(token_stats == expected_stats["tokens"], "guarded token counts")
    audit.check(cross_stats == expected_stats["cross"], "guarded cross-reader counts")
    audit.check(line_stats == expected_stats["lines"], "guarded line counts")
    by_line: defaultdict[str, list[dict[str, str]]] = defaultdict(list)
    for row in tokens:
        by_line[row["locus"]].append(row)
    for line in by_line.values():
        line.sort(key=lambda row: int(row["token_index"]))
    cross = {row["locus"]: row for row in cross_rows}
    line_meta = {row["locus"]: row for row in line_rows}
    exact: dict[tuple[str, int], int] = {}
    occurrences: list[dict[str, object]] = []
    for locus, line in by_line.items():
        seen: Counter[str] = Counter()
        capacity = {
            surface: min(
                cross[locus]["zl3b_clean"].split().count(surface),
                cross[locus]["it2a_clean"].split().count(surface),
                cross[locus]["rf1b_clean"].split().count(surface),
            )
            for surface in {token["eva"] for token in line}
        }
        for ordinal, token in enumerate(line, 1):
            surface = token["eva"]
            seen[surface] += 1
            is_exact = int(seen[surface] <= capacity[surface])
            exact[(locus, int(token["token_index"]))] = is_exact
            if surface not in TARGETS:
                continue
            key = (locus, ordinal, surface)
            span_id = TARGET_COORDINATES.get(key, "NONE")
            occurrence_class = (
                "TARGET_MASKED" if key in TARGET_COORDINATES
                else "EXTERNAL" if is_exact else "READER_NONEXACT"
            )
            occurrences.append({
                "key": key,
                "surface": surface,
                "locus": locus,
                "ordinal": ordinal,
                "token_index": int(token["token_index"]),
                "line_token_count": len(line),
                "line_position": line_position(ordinal, len(line)),
                "surface_rank": seen[surface],
                "counts": (
                    cross[locus]["zl3b_clean"].split().count(surface),
                    cross[locus]["it2a_clean"].split().count(surface),
                    cross[locus]["rf1b_clean"].split().count(surface),
                ),
                "reader_exact": is_exact,
                "occurrence_class": occurrence_class,
                "span_id": span_id,
                "page": token["page"],
                "section": token["section"],
                "language": token["language"],
                "hand": token["hand"],
                "written_line": " ".join(item["eva"] for item in line),
            })
    audit.check(len(occurrences) == 20, "twenty reconstructed occurrences")
    audit.check(Counter(row["surface"] for row in occurrences) == EXPECTED_RAW, "raw surface split")
    exact_occurrences = [row for row in occurrences if row["reader_exact"]]
    audit.check(len(exact_occurrences) == 14, "fourteen reconstructed reader-exact occurrences")
    audit.check(Counter(row["surface"] for row in exact_occurrences) == EXPECTED_EXACT, "reader-exact surface split")
    audit.check(Counter(row["occurrence_class"] for row in occurrences) == Counter({"EXTERNAL": 8, "TARGET_MASKED": 6, "READER_NONEXACT": 6}), "target external nonexact split")
    audit.check({row["key"] for row in occurrences if row["occurrence_class"] == "EXTERNAL"} == set(EXTERNAL_IDS), "exact eight external coordinates")

    actual20 = read_tsv(ART / "GDT782_20_CACHE_OCCURRENCE_ATLAS.tsv")
    actual14 = read_tsv(ART / "GDT782_14_READER_EXACT_OCCURRENCE_ATLAS.tsv")
    audit.check(len(actual20) == 20 and len({row["occurrence_id"] for row in actual20}) == 20, "published 20-row atlas")
    by_key = {(row["locus"], int(row["target_ordinal"]), row["surface"]): row for row in actual20}
    audit.check(set(by_key) == {row["key"] for row in occurrences}, "published occurrence coordinate set")
    for expected in occurrences:
        row = by_key[expected["key"]]
        audit.check(row["occurrence_class"] == expected["occurrence_class"], f"occurrence class {expected['key']}")
        audit.check(row["gdt781_span_id"] == expected["span_id"], f"target span ID {expected['key']}")
        audit.check(int(row["reader_exact"]) == expected["reader_exact"], f"reader exact {expected['key']}")
        audit.check(int(row["surface_rank_in_zl3b_line"]) == expected["surface_rank"], f"surface rank {expected['key']}")
        audit.check(tuple(int(row[name]) for name in ("zl3b_surface_count", "it2a_surface_count", "rf1b_surface_count")) == expected["counts"], f"reader capacities {expected['key']}")
        audit.check(int(row["token_index"]) == expected["token_index"] and int(row["line_token_count"]) == expected["line_token_count"], f"token geometry {expected['key']}")
        audit.check(row["line_position"] == expected["line_position"] and row["written_line_eva"] == expected["written_line"], f"line reconstruction {expected['key']}")
        audit.check(row["section"] == expected["section"] and row["language"] == expected["language"] and row["hand"] == expected["hand"], f"register metadata {expected['key']}")
        audit.check(row["selector_credit"] == "0" and row["component_export_credit"] == "0", f"occurrence zero credit {expected['key']}")
    audit.check({(row["locus"], int(row["target_ordinal"]), row["surface"]) for row in actual14} == {row["key"] for row in exact_occurrences}, "published exact-atlas subset")
    selected = {(row["locus"], int(row["right_ordinal"]), row["right_surface"]): row["span_id"] for row in read_tsv(G781_SELECTED) if row["right_surface"] in TARGETS}
    audit.check(selected == TARGET_COORDINATES, "parent six target coordinates")
    return occurrences, dict(by_line), cross, exact, line_meta, expected_stats


def axis_patterns(audit: Audit) -> dict[str, re.Pattern[str]]:
    rows = read_tsv(AXIS_SPECS)
    audit.check([row["axis_id"] for row in rows] == ["HOT", "COLD", "DRY", "MOIST", "AMOUNT", "VALUE", "PART", "MATERIAL", "PREPARATION", "PROCESS", "CLOSE", "PASS"], "axis-rule order")
    return {row["axis_id"]: re.compile(row["keyword_regex"].replace("\\\\", "\\"), re.I) for row in rows}


def semantic_axes(text: str, patterns: Mapping[str, re.Pattern[str]]) -> set[str]:
    axes = {axis for axis, pattern in patterns.items() if pattern.search(text)}
    if re.search(r"koch|ausgekoch", text, re.I):
        axes.add("HOT")
    axes.update(axis for axis, pattern in STAGE_PATTERNS.items() if pattern.search(text))
    return axes


def build_pool(audit: Audit) -> dict[str, dict[str, object]]:
    patterns = axis_patterns(audit)
    dictionary = read_tsv(DICTIONARY)
    grouped: defaultdict[str, list[dict[str, str]]] = defaultdict(list)
    for row in dictionary:
        meaning = row["working_meaning_de"]
        if not row["working_model_level"].startswith(("W2", "W3")):
            continue
        if row["gdt734_composition_semantic_credit"] != "0" or row["gdt734_component_export_allowed"] != "0":
            continue
        if row["gdt734_renderer_decision"] == "HOLD_UNCHANGED":
            continue
        if any(word in meaning.lower() for word in RETIRED):
            continue
        if not semantic_axes(meaning, patterns):
            continue
        grouped[row["surface"]].append(row)
    pool: dict[str, dict[str, object]] = {}
    for surface, rows in grouped.items():
        axis_sets = [semantic_axes(row["working_meaning_de"], patterns) for row in rows]
        core = set.intersection(*axis_sets)
        if not core:
            continue
        ranked = sorted(rows, key=lambda row: (-int(row["working_model_level"].startswith("W3")), -int(row["working_model_score_0_100_not_probability"]), row["reading_id"]))
        pool[surface] = {
            "axes": joined(core),
            "reading_ids": "|".join(row["reading_id"] for row in ranked),
            "levels": "|".join(sorted({row["working_model_level"] for row in rows})),
            "default": ranked[0]["working_meaning_de"],
        }
    audit.check(len(dictionary) == 1606, "1606 dictionary readings")
    audit.check(sum(len(rows) for rows in grouped.values()) == 770, "770 eligible clean readings")
    audit.check(len(pool) == 769, "769 clean whole surfaces")
    return pool


def validate_neighbors(
    audit: Audit,
    occurrences: Sequence[Mapping[str, object]],
    by_line: Mapping[str, list[dict[str, str]]],
    exact: Mapping[tuple[str, int], int],
) -> tuple[list[dict[str, str]], dict[str, Counter[str]]]:
    pool = build_pool(audit)
    cells = {(row["locus"], int(row["token_ordinal"])): row for row in read_tsv(COMPACT)}
    g754 = unique(read_tsv(G754), "surface")
    g768 = unique(read_tsv(G768), "surface")
    constructions = read_tsv(G759)
    members: defaultdict[tuple[str, int], list[dict[str, str]]] = defaultdict(list)
    for construction in constructions:
        members[(construction["locus"], int(construction["left_token_ordinal"]))].append(construction)
        members[(construction["locus"], int(construction["right_token_ordinal"]))].append(construction)
    same_sources: defaultdict[str, set[str]] = defaultdict(set)
    for row in read_tsv(G781_ANALOGY):
        if row["candidate_surface"] in TARGETS:
            same_sources[row["candidate_surface"]].add(row["known_neighbor_surface"])
    actual = read_tsv(ART / "GDT782_65_EXTERNAL_NEIGHBOR_ATLAS.tsv")
    actual_by_key = {(row["locus"], int(row["target_ordinal"]), int(row["neighbor_ordinal"])): row for row in actual}
    expected_keys: set[tuple[str, int, int]] = set()
    external_rows = [row for row in occurrences if row["occurrence_class"] == "EXTERNAL"]
    for target in external_rows:
        locus = str(target["locus"])
        target_ordinal = int(target["ordinal"])
        external_id = EXTERNAL_IDS[(locus, target_ordinal, str(target["surface"]))]
        for ordinal, token in enumerate(by_line[locus], 1):
            if ordinal == target_ordinal:
                continue
            key = (locus, target_ordinal, ordinal)
            expected_keys.add(key)
            row = actual_by_key[key]
            surface = token["eva"]
            is_exact = exact[(locus, int(token["token_index"]))]
            cell = cells[(locus, ordinal)]
            clean = pool.get(surface) if is_exact else None
            later = g754.get(surface)
            construction = members.get((locus, ordinal), [None])[0]
            semantic = cell["v99r7_semantic_value_de"]
            retired = int(any(word in semantic.lower() for word in RETIRED))
            source_composed = int(cell["gdt734_composition_semantic_credit"] != "0")
            if surface in TARGETS:
                klass = "COHORT_TARGET_MASKED"
            elif not is_exact:
                klass = "NONEXACT_VISIBLE_ONLY"
            elif later is not None and later["source_literal_prose_spoken_after_gdt754"] == "0":
                klass, source_composed = "SANITIZED_GDT754_WHOLE_HYPOTHESIS", 1
            elif clean is not None:
                klass = "CLEAN_W2W3_COMPLETE_WHOLE"
            elif construction is not None:
                klass = "LICENSED_EXACT_CONSTRUCTION_MEMBER"
            elif retired:
                klass = "QUARANTINED_RETIRED_LITERAL"
            elif source_composed:
                klass = "SOURCE_COMPOSED_UNCLEAN"
            elif cell["unknown_v99r7"] == "1" or semantic.startswith("["):
                klass = "OPEN_EXACT"
            else:
                klass = "LOWER_GRADE_WHOLE_HYPOTHESIS"
            other_targets = sorted(candidate for candidate in TARGETS if candidate != target["surface"] and surface in same_sources[candidate])
            clean_default = "NONE"
            clean_axes = "NONE"
            if clean is not None:
                clean_default = str(clean["default"])
                clean_axes = str(clean["axes"])
                if surface in g768:
                    clean_default = g768[surface]["concrete_default_de"]
            if klass == "SANITIZED_GDT754_WHOLE_HYPOTHESIS":
                clean_default, clean_axes = "BLOCKED_BY_GDT754", "NONE"
            audit.check(row["external_id"] == external_id and row["surface"] == target["surface"], f"external identity {key}")
            audit.check(row["neighbor_surface"] == surface and int(row["offset"]) == ordinal - target_ordinal and int(row["absolute_distance"]) == abs(ordinal - target_ordinal), f"neighbor geometry {key}")
            audit.check(int(row["neighbor_reader_exact"]) == is_exact and row["neighbor_class"] == klass, f"neighbor exact class {key}")
            audit.check(row["clean_pool_reading_ids"] == (str(clean["reading_ids"]) if clean else "NONE") and row["clean_pool_level"] == (str(clean["levels"]) if clean else "NONE"), f"neighbor clean provenance {key}")
            audit.check(row["clean_pool_default_de"] == clean_default and row["clean_pool_axes"] == clean_axes, f"neighbor clean display axes {key}")
            audit.check(int(row["gdt754_provenance_present"]) == int(later is not None), f"GDT754 presence {key}")
            audit.check(row["gdt754_sanitized_default_de"] == (later["current_working_whole_default_de"] if later else "NONE") and row["gdt754_sanitized_axes"] == (later["later_role_axes_selected"] if later else "NONE"), f"GDT754 sanitation {key}")
            audit.check(row["later_display_override_de"] == (g768[surface]["concrete_default_de"] if surface in g768 else "NONE"), f"later display override {key}")
            audit.check(int(row["retired_literal_visible"]) == retired and int(row["source_composed_visible"]) == source_composed, f"quarantine flags {key}")
            audit.check(row["other_cohort_target_analogy_source"] == ("|".join(other_targets) or "NONE"), f"cross-cohort annotation {key}")
            audit.check(int(row["same_target_analogy_source"]) == int(surface in same_sources[str(target["surface"])]), f"same-target annotation {key}")
            audit.check(int(row["target_surface_leakage"]) == int(surface in TARGETS) and int(row["within_radius_3"]) == int(abs(ordinal - target_ordinal) <= 3), f"radius and leakage {key}")
            audit.check(row["selector_credit"] == row["default_is_translation"] == row["component_export_credit"] == "0", f"neighbor zero credits {key}")
    audit.check(len(actual) == 65 and set(actual_by_key) == expected_keys, "complete 65-neighbor atlas")
    audit.check(sum(int(row["within_radius_3"]) for row in actual) == 38, "38 radius-three neighbor rows")
    audit.check(sum(row["within_radius_3"] == "1" and row["neighbor_class"] == "CLEAN_W2W3_COMPLETE_WHOLE" for row in actual) == 17, "17 clean radius-three donors")
    audit.check(sum(int(row["target_surface_leakage"]) for row in actual if row["within_radius_3"] == "1") == 0, "zero radius-three target leakage")
    audit.check(sum(int(row["same_target_analogy_source"]) for row in actual if row["within_radius_3"] == "1") == 0, "zero same-target analogy leakage")
    audit.check(sum(row["other_cohort_target_analogy_source"] != "NONE" for row in actual if row["within_radius_3"] == "1") == 1, "one radius-three cross-cohort source")
    audit.check(sum(row["other_cohort_target_analogy_source"] != "NONE" for row in actual) == 2, "two full-line cross-cohort sources")
    sanitized = [row for row in actual if row["neighbor_class"] == "SANITIZED_GDT754_WHOLE_HYPOTHESIS"]
    audit.check(len(sanitized) == 1 and sanitized[0]["neighbor_surface"] == "okeol" and sanitized[0]["absolute_distance"] == "5", "one nonvoting R5 okeol sanitation")
    cthy = [row for row in actual if row["neighbor_surface"] == "cthy" and row["neighbor_reader_exact"] == "1"]
    audit.check(len(cthy) == 1 and cthy[0]["clean_pool_default_de"] == "Blattgut" and cthy[0]["later_display_source"] == "GDT768_WORKING_DICTIONARY", "current cthy Blattgut display")

    weights: defaultdict[str, Counter[str]] = defaultdict(Counter)
    by_external: defaultdict[str, list[dict[str, str]]] = defaultdict(list)
    for row in actual:
        by_external[row["external_id"]].append(row)
    for external_id, rows in by_external.items():
        best: dict[str, int] = {}
        for row in rows:
            if row["neighbor_class"] != "CLEAN_W2W3_COMPLETE_WHOLE" or int(row["absolute_distance"]) > 3:
                continue
            for axis in split_axes(row["clean_pool_axes"]):
                best[axis] = max(best.get(axis, 0), 4 - int(row["absolute_distance"]))
        weights[rows[0]["surface"]].update(best)
    return actual, dict(weights)


def opposition(candidate_axes: set[str], field: Mapping[str, int]) -> float:
    totals: list[int] = []
    for members in DIMENSIONS.values():
        asserted = candidate_axes & set(members)
        if asserted:
            totals.append(sum(field.get(axis, 0) for axis in members if axis not in asserted))
    return sum(totals) / len(totals) if totals else 0.0


def validate_adjudication(audit: Audit, occurrences: Sequence[Mapping[str, object]], neighbors: Sequence[Mapping[str, str]], weights: Mapping[str, Counter[str]]) -> None:
    candidate_source = read_tsv(CANDIDATES)
    final_source = read_tsv(FINAL)
    manual_source = read_tsv(MANUAL)
    scorecards = read_tsv(ART / "GDT782_23_CANDIDATE_SCORECARDS.tsv")
    revisions = read_tsv(ART / "GDT782_6_WORKING_REVISIONS.tsv")
    manual_art = read_tsv(ART / "GDT782_18_MANUAL_READER_ASSESSMENTS.tsv")
    summaries = read_tsv(ART / "GDT782_8_EXTERNAL_FIELD_SUMMARY.tsv")
    contacts = read_tsv(ART / "GDT782_REGISTERED_CONSTRUCTION_CONTACTS.tsv")
    audit.check(len(candidate_source) == len(scorecards) == 23, "23 candidates and scorecards")
    audit.check(Counter(row["surface"] for row in candidate_source) == Counter({"cheedaiin": 3, "chedor": 4, "chockhar": 4, "keeor": 5, "shdair": 3, "sheckhal": 4}), "18 inherited plus five refinement candidates")
    audit.check(len(final_source) == len(revisions) == 6 and tuple(row["surface"] for row in final_source) == TARGET_ORDER, "six ordered final cards")
    finals = unique(final_source, "surface")
    revs = unique(revisions, "surface")
    score_by_key = {(row["surface"], row["candidate_id"]): row for row in scorecards}
    audit.check(set(score_by_key) == {(row["surface"], row["candidate_id"]) for row in candidate_source}, "scorecard candidate identity")
    for surface, expected in EXPECTED_FINAL.items():
        source = finals[surface]
        revision = revs[surface]
        observed = (source["selected_candidate_id"], source["gdt782_default_de"], source["decision"], source["confidence"])
        audit.check(observed == expected, f"final card {surface}")
        for field in source:
            if field in revision:
                audit.check(revision[field] == source[field], f"revision copies final source {surface} {field}")
        audit.check(sum(int(row["selected_final"]) for row in scorecards if row["surface"] == surface) == 1, f"one selected scorecard {surface}")
        audit.check(score_by_key[(surface, source["selected_candidate_id"])]["selected_final"] == "1", f"selected candidate link {surface}")
        audit.check(revision["field_score_is_decision_rule"] == "0" and revision["substring_used"] == "0", f"manual decision and no substring {surface}")
    audit.check(Counter(row["decision"] for row in revisions) == Counter({"REVISE": 5, "KEEP": 1}), "five revisions one keep")
    audit.check(len(manual_source) == len(manual_art) == 18, "eighteen manual reader rows")
    audit.check(Counter(row["reader_id"] for row in manual_source) == Counter({"FIELD_GRAMMAR_READER": 6, "APOTHECARY_READER": 6, "EXTERNAL_CENSUS_READER": 6}), "three six-form manual readers")
    manual_by_key = {(row["reader_id"], row["surface"]): row for row in manual_art}
    for number, source in enumerate(manual_source, 1):
        row = manual_by_key[(source["reader_id"], source["surface"])]
        audit.check(row["assessment_id"] == f"G782-M{number:03d}", f"manual assessment ID {number}")
        audit.check(all(row[field] == value for field, value in source.items()), f"manual source copy {number}")
        audit.check(row["assessment_is_proof"] == row["component_export_credit"] == "0", f"manual zero proof/export {number}")

    contacts_by_target: defaultdict[str, list[dict[str, str]]] = defaultdict(list)
    for row in contacts:
        contacts_by_target[row["surface"]].append(row)
    external_by_surface: defaultdict[str, list[Mapping[str, object]]] = defaultdict(list)
    for row in occurrences:
        if row["occurrence_class"] == "EXTERNAL":
            external_by_surface[str(row["surface"])].append(row)
    neighbor_by_external: defaultdict[str, list[Mapping[str, str]]] = defaultdict(list)
    for row in neighbors:
        neighbor_by_external[row["external_id"]].append(row)
    audit.check(len(contacts) == 1, "one registered target construction")
    contact = contacts[0]
    audit.check((contact["surface"], contact["locus"], contact["construction_ordinal_start"], contact["construction_ordinal_end"], contact["construction_eva"], contact["construction_default_de"], contact["exact_pair_global_count"]) == ("chedor", "f105v.26", "6", "7", "or aiin", "drei Portionen", "36"), "exact or-aiin construction contact")

    for candidate in candidate_source:
        surface = candidate["surface"]
        axes = split_axes(candidate["candidate_axes"])
        field = weights.get(surface, Counter())
        support = sum(field.get(axis, 0) for axis in axes)
        support_mean = support / len(axes) if axes else 0.0
        oppose = opposition(axes, field)
        redundancy = 0.0
        complement = 0.0
        endpoint = 0.0
        patient = 0.0
        if contacts_by_target.get(surface):
            if axes & {"AMOUNT", "PART"}:
                redundancy += 3.0
            if axes & {"MATERIAL", "PREPARATION"}:
                complement += 2.0
        for target in external_by_surface[surface]:
            external_id = EXTERNAL_IDS[(str(target["locus"]), int(target["ordinal"]), surface)]
            rows = neighbor_by_external[external_id]
            left = next((row for row in rows if row["offset"] == "-1"), None)
            right = next((row for row in rows if row["offset"] == "1"), None)
            if left and not contacts_by_target.get(surface):
                left_axes = split_axes(left["clean_pool_axes"])
                if left_axes & {"AMOUNT", "PART"}:
                    redundancy += float(bool(axes & {"AMOUNT", "PART"}))
                    complement += float(bool(axes & {"MATERIAL", "PREPARATION"}))
            if right and "PROCESS" in split_axes(right["clean_pool_axes"]) and axes & {"MATERIAL", "PREPARATION"}:
                patient += 2.0
            if target["line_position"] == "LAST" and "END_STAGE" in axes:
                endpoint += 2.0
            if any(row["offset"] == "-1" and "CLOSE" in split_axes(row["clean_pool_axes"]) for row in rows) and "END_STAGE" in axes:
                endpoint += 1.0
        score = support_mean - oppose - redundancy + complement + endpoint + patient
        row = score_by_key[(surface, candidate["candidate_id"])]
        audit.check(int(row["candidate_axis_support_total"]) == support and row["candidate_axis_support_mean"] == f"{support_mean:.3f}", f"candidate support {surface} {candidate['candidate_id']}")
        audit.check(row["opposition_mean"] == f"{oppose:.3f}" and row["amount_redundancy_penalty"] == f"{redundancy:.3f}", f"candidate opposition redundancy {surface} {candidate['candidate_id']}")
        audit.check(row["content_complement_bonus"] == f"{complement:.3f}" and row["endpoint_bonus"] == f"{endpoint:.3f}" and row["patient_before_process_bonus"] == f"{patient:.3f}", f"candidate bonuses {surface} {candidate['candidate_id']}")
        audit.check(row["exploratory_field_score"] == f"{score:.3f}" and row["score_is_lexical_probability"] == "0", f"candidate score nonprobability {surface} {candidate['candidate_id']}")
    for surface in TARGET_ORDER:
        rows = sorted((row for row in scorecards if row["surface"] == surface), key=lambda row: (-float(row["exploratory_field_score"]), row["candidate_id"]))
        audit.check([int(row["field_score_rank"]) for row in rows] == list(range(1, len(rows) + 1)), f"candidate rank {surface}")

    audit.check(len(summaries) == 8 and {row["external_id"] for row in summaries} == set(EXTERNAL_IDS.values()), "eight external field summaries")
    for row in summaries:
        audit.check(row["target_masked_during_field_read"] == "1" and row["strict_target_surface_leakage"] == "0", f"summary target masking {row['external_id']}")
    sheckhal = next(row for row in summaries if row["surface"] == "sheckhal")
    audit.check(sheckhal["radius3_clean_donors"] == "1" and sheckhal["radius3_clean_surfaces"] == "cheal", "sheckhal one R2 clean donor")


def validate_renderer_and_claims(audit: Audit) -> None:
    parent = read_tsv(G781_RENDERER)
    renderer = read_tsv(ART / "GDT782_376_RENDERER.tsv")
    audit.check(len(parent) == len(renderer) == 376, "376-row parent and child renderer")
    parent_fields = list(parent[0])
    audit.check(all(field in renderer[0] for field in parent_fields), "all parent columns inherited")
    by_id = unique(renderer, "target_occurrence_id")
    for parent_row in parent:
        child = by_id[parent_row["target_occurrence_id"]]
        for field in parent_fields:
            audit.check(child[field] == parent_row[field], f"parent byte field {parent_row['target_occurrence_id']} {field}")
    targets = [row for row in renderer if row["gdt782_card_id"] != "NONE"]
    audit.check(len(targets) == 6 and {row["right_surface"] for row in targets} == TARGETS, "six renderer target cards")
    audit.check(sum(int(row["gdt782_renderer_contextual"]) for row in renderer) == 270, "270 contextual renderer rows")
    audit.check(sum(1 - int(row["gdt782_renderer_contextual"]) for row in renderer) == 106, "106 fallback renderer rows")
    audit.check(sum(int(row["gdt782_display_changed"]) for row in renderer) == 5, "five renderer display changes")
    consumed = {token for row in renderer for token in row["gdt782_consumed_token_ids"].split("|") if token != "NONE"}
    audit.check(len(consumed) == 230 and sum(int(row["gdt782_consumed_token_count"]) for row in renderer) == 230, "230 unique noncolliding consumptions")
    for row in targets:
        expected = EXPECTED_FINAL[row["right_surface"]]
        audit.check((row["gdt782_default_de"], row["gdt782_decision"], row["gdt782_confidence"]) == (expected[1], expected[2], expected[3]), f"renderer final card {row['right_surface']}")
    audit.check(sum(all(row[field] == "0" for field in ("gdt782_default_is_translation", "gdt782_confirmed_lexeme", "gdt782_confirmed_plaintext", "gdt782_component_export_credit")) for row in renderer) == 376, "renderer zero translation and export credit")

    patches = read_tsv(ART / "GDT782_6_TARGET_PASSAGE_PATCHES.tsv")
    external_reader = read_tsv(ART / "GDT782_8_EXTERNAL_WORKING_READER.tsv")
    audit.check(len(patches) == 6 and sum(int(row["display_changed"]) for row in patches) == 5, "six patches five changed")
    audit.check(len(external_reader) == 8 and all(row["status"] == "AGGREGATE_CARD_AUDIT_NOT_EXTERNAL_RENDERER_LICENSE" for row in external_reader), "outside reader is audit not licence")
    all_display = "\n".join(row["working_field_render_de"] for row in external_reader)
    audit.check("Grundansatz bis zur mittleren Heizstufe erwärmt" not in all_display, "stale okeol prose absent from reader")
    audit.check("Wärme-/Mittelstufenfeld; genaue Funktion und Träger offen" in all_display, "sanitized okeol display present")
    audit.check("⟨Blattgut⟩" in all_display and "CTH-Drogenmaterial⟩" not in all_display, "current cthy display present")
    x005 = next(row for row in external_reader if row["external_id"] == "G782-X005")
    audit.check("⟦Menge: drei Portionen⟧ | ⟦Stoff: getrockneter Arzneistoff⟧" in x005["working_field_render_de"], "explicit quantity and substance field split")

    zero_fields = {
        "default_is_translation", "confirmed_lexeme", "confirmed_plaintext",
        "component_export_credit", "numeric_identity_confirmed",
        "specific_substance_confirmed", "score_is_lexical_probability",
        "assessment_is_proof", "selector_credit", "score_eligible",
    }
    for name in OUTPUT_NAMES:
        if not name.endswith(".tsv"):
            continue
        rows = read_tsv(ART / name)
        for row_number, row in enumerate(rows, 2):
            for field in zero_fields & set(row):
                audit.check(row[field] == "0", f"zero claim {name}:{row_number}:{field}")


def validate_result_and_edges(audit: Audit, guard_stats: Mapping[str, Mapping[str, int]]) -> None:
    result = json.loads((ART / "RESULT.json").read_text(encoding="utf-8"))
    audit.check(result["experiment_id"] == "GDT782" and result["status"] == STATUS, "result identity and status")
    audit.check(result["source_locks"] == 19 and result["source_lock_sha256"] == sha256(LOCKS), "result source-lock binding")
    audit.check(result["source_spec_sha256"] == EXPECTED_SPEC_HASHES, "result source-spec hashes")
    audit.check(result["inherited_guard"] == guard_stats, "result guarded-query counts")
    audit.check(result["clean_pool"] == {"dictionary_rows": 1606, "clean_axis_reading_rows": 770, "clean_axis_whole_pool": 769}, "result clean-pool counts")
    audit.check(result["cohort"]["cache_occurrences"] == 20 and result["cohort"]["reader_exact_occurrences"] == 14 and result["cohort"]["target_external_occurrences"] == 8, "result cohort counts")
    audit.check(result["cohort"]["radius3_cross_cohort_analogy_source_contacts"] == 1 and result["cohort"]["full_line_cross_cohort_analogy_source_contacts"] == 2, "result cross-cohort radius labels")
    audit.check(result["provenance_sanitation"] == {"gdt754_neighbor_rows": 1, "sanitized_neighbor_rows": 1, "sanitized_surfaces": ["okeol"], "radius3_clean_votes_removed": 0}, "result provenance sanitation")
    audit.check(result["adjudication"]["final_defaults"] == {surface: expected[1] for surface, expected in EXPECTED_FINAL.items()}, "result six final defaults")
    audit.check(result["adjudication"]["revised_cards"] == 5 and result["adjudication"]["kept_cards"] == 1, "result five revised one kept")
    audit.check(result["renderer"]["rows"] == 376 and result["renderer"]["gdt782_contextual"] == 270 and result["renderer"]["gdt782_fallbacks"] == 106 and result["renderer"]["display_changes"] == 5, "result renderer counts")
    audit.check(result["consumption"]["gdt782_unique_right_tokens"] == 230 and result["consumption"]["collisions"] == 0, "result consumption counts")
    for field in ("confirmed_lexemes", "confirmed_plaintext_clauses", "numeric_identities", "specific_substances", "component_exports", "new_pages", "new_images", "new_ocr", "new_transcriptions", "sealed_pages_accessed"):
        audit.check(result[field] == 0, f"result zero {field}")
    expected_intake = {
        "status": "VALID_ACQUISITION_NOT_SCORE_READY", "packet_rows": 8,
        "eligible_edges": 0, "eligible_folios": 0, "discovery_edges": 0,
        "holdout_edges": 0, "mobile_edges": 0,
        "capacity_gate_50_edges_5_folios": False, "holdout_gate": False,
        "mobile_null_gate": False, "score_ready": False, "errors": [],
    }
    intake = json.loads((ART / "RELATION_PACKET_INTAKE.json").read_text(encoding="utf-8"))
    audit.check(intake == expected_intake and result["relation_packet"] == expected_intake, "stored edge intake")
    completed = subprocess.run(
        [str(ROOT / "vmanus-exp"), "check-edge-packet", str(ART / "GDT782_GDT388_EXTERNAL_FIELD_PACKET.tsv")],
        cwd=ROOT, text=True, capture_output=True, check=False,
    )
    audit.check(completed.returncode == 0, "executable edge packet command")
    audit.check(json.loads(completed.stdout) == expected_intake, "executable edge packet result")
    packet = read_tsv(ART / "GDT782_GDT388_EXTERNAL_FIELD_PACKET.tsv")
    crosswalk = read_tsv(ART / "GDT782_RELATION_EDGE_CROSSWALK.tsv")
    audit.check(len(packet) == len(crosswalk) == 8 and {row["edge_id"] for row in packet} == {row["edge_id"] for row in crosswalk}, "eight packet crosswalk edges")
    audit.check(all(row["eligibility_status"] == "INELIGIBLE_EXPLORATORY_TEXT_RELATION" and row["formal_access_state"] == "SEALED_NOT_ACCESSED" for row in packet), "packet ineligible and seals untouched")


def byte_replay(audit: Audit) -> list[str]:
    with tempfile.TemporaryDirectory(prefix="gdt782_replay_") as raw:
        replay_root = Path(raw)
        replay_art = replay_root / "artifacts"
        replay_report = replay_root / "REPORT.md"
        environment = dict(os.environ)
        environment["PYTHONDONTWRITEBYTECODE"] = "1"
        completed = subprocess.run(
            [sys.executable, "-B", str(RUN), "--artifacts-dir", str(replay_art), "--report-path", str(replay_report)],
            cwd=ROOT, env=environment, text=True, capture_output=True, check=False,
        )
        audit.check(completed.returncode == 0, "runner replay exits zero")
        replayed: list[str] = []
        for name in OUTPUT_NAMES:
            audit.check((replay_art / name).read_bytes() == (ART / name).read_bytes(), f"byte replay {name}")
            replayed.append(name)
        audit.check((replay_art / "README.md").read_bytes() == (ART / "README.md").read_bytes(), "byte replay artifact README")
        audit.check(replay_report.read_bytes() == REPORT.read_bytes(), "byte replay report")
        replayed.extend(("README.md", "../REPORT.md"))
        return replayed


def main() -> int:
    audit = Audit()
    validate_locks(audit)
    occurrences, by_line, _, exact, _, guard_stats = reconstruct_occurrences(audit)
    neighbors, weights = validate_neighbors(audit, occurrences, by_line, exact)
    validate_adjudication(audit, occurrences, neighbors, weights)
    validate_renderer_and_claims(audit)
    validate_result_and_edges(audit, guard_stats)
    replayed = byte_replay(audit)
    validation = {
        "experiment_id": "GDT782",
        "status": "PASS",
        "checks": audit.count,
        "source_locks": 19,
        "source_lock_sha256": sha256(LOCKS),
        "candidate_specs_sha256": sha256(CANDIDATES),
        "manual_assessments_sha256": sha256(MANUAL),
        "final_specs_sha256": sha256(FINAL),
        "runner_sha256": sha256(RUN),
        "result_sha256": sha256(ART / "RESULT.json"),
        "report_sha256": sha256(REPORT),
        "independent_occurrence_reconstruction": {"raw": 20, "reader_exact": 14, "targets": 6, "external": 8, "nonexact": 6},
        "independent_neighbor_reconstruction": {"full_line_rows": 65, "radius3_rows": 38, "clean_radius3_donors": 17, "radius3_target_leakage": 0, "radius3_cross_cohort_sources": 1, "full_line_cross_cohort_sources": 2},
        "renderer": {"rows": 376, "contextual": 270, "fallback": 106, "display_changes": 5, "consumed": 230},
        "byte_replay": "PASS",
        "replayed_files": replayed,
        "run_py_imported": False,
        "sealed_pages_accessed": 0,
    }
    (ART / "VALIDATION.json").write_text(
        json.dumps(validation, ensure_ascii=False, sort_keys=True, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"GDT782_VALIDATION_PASS {audit.count} checks; {len(replayed)} files replayed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
