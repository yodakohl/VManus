#!/usr/bin/env python3
"""Independent validator for GDT783's majority-variant chsky audit.

This file deliberately does not import runner code. It reconstructs the
three physical loci and their reader-relative windows through guarded source
queries, then checks the frozen public artifacts against that reconstruction.
"""

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
EXP = ROOT / "experiments/yolo/gdt783_chsky_majority_variant_external_field"
SRC = EXP / "src"
ART = EXP / "artifacts"
RUN = SRC / "run.py"
LOCKS = SRC / "SOURCE_LOCK.tsv"
CANDIDATES = SRC / "CANDIDATE_6_SPECS.tsv"
HISTORICAL_SPECS = SRC / "HISTORICAL_COMPARATOR_SPECS.tsv"
FINAL_SELECTION = SRC / "FINAL_SELECTION_SPEC.tsv"
REPORT = EXP / "REPORT.md"

ALLOWLIST = ROOT / "experiments/yolo/gdt635_initial_head_same_remainder_swaps/artifacts/PAGE_ALLOWLIST.tsv"
TOKENS = Path("transcription/voynich_zl3b_tokens.tsv")
CROSS = Path("transcription/voynich_cross_transcription_lines.tsv")
LINES = Path("transcription/voynich_zl3b_lines.tsv")
DICTIONARY = ROOT / "experiments/yolo/gdt734_v99r7_recurrent_unknown_family_dispatch/artifacts/V99R7_1606_COMPLETE_WORD_CONFIDENCE.tsv"
AXIS_SPECS = ROOT / "experiments/yolo/gdt739_twelve_whole_local_dimension_dispatch/src/ANCHOR_AXIS_SPECS.tsv"
G754 = ROOT / "experiments/yolo/gdt754_active_productive_compound_provenance_sieve/artifacts/PROVENANCE_SIEVE_172_DECISIONS.tsv"
G768 = ROOT / "experiments/yolo/gdt768_chor_shor_part_identity_tournament/artifacts/GDT768_6_WORKING_DICTIONARY.tsv"
G781_SELECTED = ROOT / "experiments/yolo/gdt781_ol_remaining_23_exploratory_whole_projection/artifacts/GDT781_23_SELECTED_ATLAS.tsv"
G781_CARD = ROOT / "experiments/yolo/gdt781_ol_remaining_23_exploratory_whole_projection/artifacts/GDT781_23_RECURRENCE_EVIDENCE_CARDS.tsv"
G781_ANALOGY = ROOT / "experiments/yolo/gdt781_ol_remaining_23_exploratory_whole_projection/artifacts/GDT781_RAW_COMPLETE_WHOLE_ANALOGY_RELATIONS.tsv"
G782_RENDERER = ROOT / "experiments/yolo/gdt782_recurrent_six_target_external_field_adjudication/artifacts/GDT782_376_RENDERER.tsv"
G622_OBSERVATIONS = ROOT / "experiments/yolo/gdt622_clm667_temperament_codebook/artifacts/SOURCE_OBSERVATIONS.tsv"
G626_COMPARATORS = ROOT / "experiments/yolo/gdt626_mobile_operation_lexicon/artifacts/HISTORICAL_NUMERAL_COMPARATORS.tsv"

EXPECTED_SOURCE_HASHES = {
    "experiments/yolo/gdt635_initial_head_same_remainder_swaps/artifacts/PAGE_ALLOWLIST.tsv": "f0def5a04bd91443cf4770c78f1b67e62cac2060627d8de38faba27899188483",
    "transcription/voynich_zl3b_tokens.tsv": "6a061a26edc05ff37dc386c2215774c229a5ff087d3091e68bdd4983a6c007aa",
    "transcription/voynich_cross_transcription_lines.tsv": "ff3a4559004a29764c60102326de154b29fbba06a2a206bdd76d7feda432e16c",
    "transcription/voynich_zl3b_lines.tsv": "7520dd4c11f4d23c8492e4b2a52cc0fcbda6d9fc88a96ead8f1c31081a4d7ed2",
    "experiments/yolo/gdt734_v99r7_recurrent_unknown_family_dispatch/artifacts/V99R7_32339_COMPACT_CELL_REGISTER.tsv": "47e8c7375503c2af7c95049392660de23556993ef78c1f24a10af6d9d7a1ed3c",
    "experiments/yolo/gdt734_v99r7_recurrent_unknown_family_dispatch/artifacts/V99R7_1606_COMPLETE_WORD_CONFIDENCE.tsv": "9646b8960840f0a6bb10985f0f9d7eef1237725f0763b712a96f0190aeaf7816",
    "experiments/yolo/gdt739_twelve_whole_local_dimension_dispatch/src/ANCHOR_AXIS_SPECS.tsv": "0561329a79ce6c32e8eea4ca58a38e5a5f9602bf181beb79d741543b95aa2b53",
    "experiments/yolo/gdt754_active_productive_compound_provenance_sieve/artifacts/PROVENANCE_SIEVE_172_DECISIONS.tsv": "25f2af6f38af1b8aee8fb2d6160f2742ab28ec71e704b51df3daf6d03251718d",
    "experiments/yolo/gdt768_chor_shor_part_identity_tournament/artifacts/GDT768_6_WORKING_DICTIONARY.tsv": "2c9c805b12aa1adf1b858b8e4c6355a1b30ebbc85f0b4d0f74578a4a4a6ccde9",
    "experiments/yolo/gdt781_ol_remaining_23_exploratory_whole_projection/artifacts/GDT781_23_SELECTED_ATLAS.tsv": "9b7026e64499bf952ab6d84554c5d60c20ad05f99278841df8e1057250bfaa40",
    "experiments/yolo/gdt781_ol_remaining_23_exploratory_whole_projection/artifacts/GDT781_23_RECURRENCE_EVIDENCE_CARDS.tsv": "aedb745fa1d253305dc551828509890fafa1fd5c5ad20c9bf59c43ede8e58466",
    "experiments/yolo/gdt781_ol_remaining_23_exploratory_whole_projection/artifacts/GDT781_RAW_COMPLETE_WHOLE_ANALOGY_RELATIONS.tsv": "a42a22c9a80b9997f1a17e35e1d6766915ce97a8f28a66939e413f367eaa5445",
    "experiments/yolo/gdt782_recurrent_six_target_external_field_adjudication/artifacts/GDT782_376_RENDERER.tsv": "c9774c4282b3b3885d8d8325e53a961d30899a28188e470894edbf7ec810e232",
    "experiments/yolo/gdt782_recurrent_six_target_external_field_adjudication/artifacts/RESULT.json": "29f59ba0bda382584c813f38c1466122968eb7638be0797385cc630a46e8c2ad",
    "experiments/yolo/gdt782_recurrent_six_target_external_field_adjudication/src/run.py": "94b15ffaa293ea0dc55b7467fbada2c0d9bd0e9c636070d3e93b6857491389cc",
    "experiments/yolo/gdt622_clm667_temperament_codebook/artifacts/SOURCE_OBSERVATIONS.tsv": "bd0329ce4b8a1364b725325f00cee4630cb9d897bb3ca1758c9c12a00a479e83",
    "experiments/yolo/gdt626_mobile_operation_lexicon/artifacts/HISTORICAL_NUMERAL_COMPARATORS.tsv": "873372b70d9707efa9b214877d3c311baa0c8a00bedd19b764c5ebf30c556210",
}
EXPECTED_LOCK_TABLE_HASH = "e3524163e151152ed5357e8a9c64202b41582fb1f4548ee5266628de3b685c61"
EXPECTED_CANDIDATE_HASH = "664922757a07d09fa171abc1ae503ab00c84057732ec8e484143278f6ec0601a"
EXPECTED_HISTORICAL_HASH = "6d552089a1b5f30209989083864d31aa737ca00dee7498451fe418d89779f1e6"
EXPECTED_FINAL_SELECTION_HASH = "9148bd3612a27cb705c3330d3833331a583e7b946c5534bba9d9587814e90f1b"
EXPECTED_RUNNER_HASH = "8492b6c48d6d8ef5ece369d3e91bdb1343458e08fb1f7b12d02239741d474c67"

LOCUS_SPECS = {
    "f25r.2": {
        "page": "f25r", "zl3b_ordinal": 3, "reader_ordinals": (3, 3, 3),
        "reader_surfaces": ("chsky", "chrky", "chsky"),
        "occurrence_class": "EXTERNAL", "strength": "STRONG",
        "primary_radius": 3, "alignment_warning": 4,
    },
    "f86v5.15": {
        "page": "f86v5", "zl3b_ordinal": 12, "reader_ordinals": (12, 12, 12),
        "reader_surfaces": ("chsky", "chsky", "chsky"),
        "occurrence_class": "TARGET_MASKED", "strength": "TARGET_EXACT",
        "primary_radius": 5, "alignment_warning": 99,
    },
    "f103r.37": {
        "page": "f103r", "zl3b_ordinal": 7, "reader_ordinals": (7, 7, 7),
        "reader_surfaces": ("chsky", "chsky", "chsty"),
        "occurrence_class": "EXTERNAL", "strength": "WEAK",
        "primary_radius": 3, "alignment_warning": 1,
    },
}
AXIS_ORDER = (
    "HOT", "COLD", "DRY", "MOIST", "AMOUNT", "VALUE", "PART",
    "MATERIAL", "PREPARATION", "PROCESS", "CLOSE", "PASS",
    "STAGE", "BEGIN_STAGE", "MIDDLE_STAGE", "END_STAGE", "LEVEL_II", "LEVEL_III",
)
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

    def check(self, condition: bool, label: str) -> None:
        if not condition:
            raise AssertionError(label)
        self.count += 1


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


def joined(values: Iterable[str]) -> str:
    selected = set(values)
    return "|".join(axis for axis in AXIS_ORDER if axis in selected) or "NONE"


def split_axes(value: str) -> set[str]:
    return set() if value in {"", "NONE", "OPEN"} else set(value.split("|"))


def with_generic_stage(axes: Iterable[str]) -> set[str]:
    normalized = set(axes)
    if normalized & {"BEGIN_STAGE", "MIDDLE_STAGE", "END_STAGE", "LEVEL_II", "LEVEL_III"}:
        normalized.add("STAGE")
    return normalized


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
    audit.check(len(rows) == len(EXPECTED_SOURCE_HASHES) == 17, "seventeen source locks")
    by_path = unique(rows, "path")
    audit.check(set(by_path) == set(EXPECTED_SOURCE_HASHES), "exact source-lock path set")
    for relative, expected in EXPECTED_SOURCE_HASHES.items():
        path = Path(relative)
        audit.check(not path.is_absolute() and ".." not in path.parts, f"safe lock path {relative}")
        audit.check(by_path[relative]["expected_sha256"] == expected, f"declared lock hash {relative}")
        audit.check(sha256(ROOT / path) == expected, f"source rehash {relative}")
    audit.check(sha256(LOCKS) == EXPECTED_LOCK_TABLE_HASH, "source-lock table hash")
    audit.check(sha256(CANDIDATES) == EXPECTED_CANDIDATE_HASH, "candidate spec hash")
    audit.check(sha256(HISTORICAL_SPECS) == EXPECTED_HISTORICAL_HASH, "historical spec hash")
    audit.check(sha256(FINAL_SELECTION) == EXPECTED_FINAL_SELECTION_HASH, "final selection spec hash")
    audit.check(sha256(RUN) == EXPECTED_RUNNER_HASH, "frozen runner hash")


def majority(values: Sequence[str]) -> tuple[str, int, str]:
    counts = Counter(values)
    surface, count = sorted(counts.items(), key=lambda item: (-item[1], item[0]))[0]
    if len(counts) == 1:
        return surface, count, "EXACT_3_OF_3"
    if count == 2:
        return surface, count, "MAJORITY_2_OF_3"
    return "NONE", 1, "THREE_WAY_SPLIT"


def reconstruct_loci(audit: Audit) -> tuple[dict[str, dict[str, object]], list[dict[str, object]], dict[str, dict[str, int]]]:
    pages = {row["page"] for row in read_tsv(ALLOWLIST)}
    audit.check(len(pages) == 179, "179-page inherited selector")
    tokens, token_stats = guarded_query(TOKENS, pages, "page,locus,token_index,eva,section,language,hand")
    cross_rows, cross_stats = guarded_query(
        CROSS, pages,
        "page,locus,zl3b_clean,it2a_clean,rf1b_clean,all_three_present,all_present_exact",
    )
    lines, line_stats = guarded_query(
        LINES, pages, "page,locus,line_number,section,language,hand,token_count",
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
    for rows in by_line.values():
        rows.sort(key=lambda row: int(row["token_index"]))
    cross = unique(cross_rows, "locus")
    line_meta = unique(lines, "locus")
    raw = [
        (locus, ordinal, token)
        for locus, rows in by_line.items()
        for ordinal, token in enumerate(rows, 1)
        if token["eva"] == "chsky"
    ]
    audit.check(len(raw) == 3, "exactly three ZL3b chsky cache positions")
    audit.check({(locus, ordinal) for locus, ordinal, _ in raw} == {(key, int(spec["zl3b_ordinal"])) for key, spec in LOCUS_SPECS.items()}, "three expected physical loci exactly once")

    loci: dict[str, dict[str, object]] = {}
    windows: list[dict[str, object]] = []
    for locus, spec in LOCUS_SPECS.items():
        row = cross[locus]
        readers = (row["zl3b_clean"].split(), row["it2a_clean"].split(), row["rf1b_clean"].split())
        ordinals = tuple(int(value) for value in spec["reader_ordinals"])
        surfaces = tuple(reader[ordinal - 1] for reader, ordinal in zip(readers, ordinals))
        audit.check(surfaces == spec["reader_surfaces"], f"reader target surfaces {locus}")
        majority_surface, majority_count, consensus = majority(surfaces)
        audit.check(majority_surface == "chsky" and majority_count >= 2, f"chsky majority {locus}")
        if spec["occurrence_class"] == "TARGET_MASKED":
            audit.check(consensus == "EXACT_3_OF_3", "target is exact in all three readers")
        else:
            audit.check(consensus == "MAJORITY_2_OF_3", f"external is fixed two-of-three {locus}")
        lefts = tuple(reader[ordinal - 2] if ordinal > 1 else "LINE_EDGE" for reader, ordinal in zip(readers, ordinals))
        rights = tuple(reader[ordinal] if ordinal < len(reader) else "LINE_EDGE" for reader, ordinal in zip(readers, ordinals))
        stable_flanks = int(len(set(lefts)) == 1 and len(set(rights)) == 1)
        expected_stable = int(locus in {"f25r.2", "f86v5.15"})
        audit.check(stable_flanks == expected_stable, f"immediate flank stability {locus}")
        if locus == "f25r.2":
            audit.check(lefts == ("chor",) * 3 and rights == ("chotchy",) * 3, "f25 strong exact flanks")
        if locus == "f103r.37":
            audit.check(lefts == ("qokchdy", "qokeedy", "qokeedy") and rights == ("eeey", "shey", "ey"), "f103 weak discordant flanks")
        line = by_line[locus]
        audit.check(" ".join(token["eva"] for token in line) == row["zl3b_clean"], f"ZL3b line reconstruction {locus}")
        audit.check(line_meta[locus]["page"] == spec["page"], f"line metadata page {locus}")
        loci[locus] = {
            "locus": locus,
            "page": spec["page"],
            "zl3b_ordinal": int(spec["zl3b_ordinal"]),
            "reader_ordinals": ordinals,
            "reader_surfaces": surfaces,
            "majority_surface": majority_surface,
            "majority_count": majority_count,
            "target_consensus": consensus,
            "occurrence_class": spec["occurrence_class"],
            "strength": spec["strength"],
            "stable_immediate_flanks": stable_flanks,
            "left_surfaces": lefts,
            "right_surfaces": rights,
            "readers": readers,
            "written_line": row["zl3b_clean"],
            "section": line[0]["section"],
            "language": line[0]["language"],
            "hand": line[0]["hand"],
        }
        for neighbor_ordinal in range(1, max(map(len, readers)) + 1):
            if neighbor_ordinal == ordinals[0]:
                continue
            offset = neighbor_ordinal - ordinals[0]
            neighbor_surfaces = tuple(
                reader[neighbor_ordinal - 1] if neighbor_ordinal <= len(reader) else "<ABSENT>"
                for reader in readers
            )
            neighbor_surface, neighbor_count, raw_consensus = majority(neighbor_surfaces)
            neighbor_consensus = {
                "EXACT_3_OF_3": "THREE_OF_THREE",
                "MAJORITY_2_OF_3": "TWO_OF_THREE",
                "THREE_WAY_SPLIT": "NO_MAJORITY",
            }[raw_consensus]
            windows.append({
                "locus": locus,
                "neighbor_ordinal": neighbor_ordinal,
                "offset": offset,
                "zl3b_surface": neighbor_surfaces[0],
                "it2a_surface": neighbor_surfaces[1],
                "rf1b_surface": neighbor_surfaces[2],
                "consensus_surface": neighbor_surface,
                "consensus_count": neighbor_count,
                "consensus_class": neighbor_consensus,
                "reader_exact_neighbor": int(neighbor_consensus == "THREE_OF_THREE"),
                "reader_consensus_neighbor": int(neighbor_count >= 2),
                "occurrence_class": spec["occurrence_class"],
                "target_masked": int(spec["occurrence_class"] == "TARGET_MASKED"),
                "within_primary_radius": int(abs(offset) <= int(spec["primary_radius"])),
                "reader_boundary_shift_warning": int(offset >= int(spec["alignment_warning"])),
            })
    audit.check(len(windows) == 28, "twenty-eight target-aligned positional slots")
    audit.check(Counter(row["locus"] for row in windows) == Counter({"f86v5.15": 11, "f25r.2": 9, "f103r.37": 8}), "complete maximum-reader positional slots")
    parent_targets = [row for row in read_tsv(G781_SELECTED) if row["right_surface"] == "chsky"]
    audit.check(len(parent_targets) == 1, "one fixed parent chsky target")
    parent = parent_targets[0]
    audit.check((parent["locus"], parent["right_ordinal"], parent["span_id"]) == ("f86v5.15", "12", "G781-S020"), "parent target mask coordinate")
    audit.check(sum(int(row["target_masked"]) for row in windows) == 11, "target sensitivity field marked throughout its eleven slots")
    return loci, windows, expected_stats


def axis_patterns(audit: Audit) -> dict[str, re.Pattern[str]]:
    rows = read_tsv(AXIS_SPECS)
    audit.check([row["axis_id"] for row in rows] == ["HOT", "COLD", "DRY", "MOIST", "AMOUNT", "VALUE", "PART", "MATERIAL", "PREPARATION", "PROCESS", "CLOSE", "PASS"], "axis-rule order")
    return {row["axis_id"]: re.compile(row["keyword_regex"].replace("\\\\", "\\"), re.I) for row in rows}


def semantic_axes(text: str, patterns: Mapping[str, re.Pattern[str]]) -> set[str]:
    axes = {axis for axis, pattern in patterns.items() if pattern.search(text)}
    if re.search(r"koch|ausgekoch", text, re.I):
        axes.add("HOT")
    stage_axes = {axis for axis, pattern in STAGE_PATTERNS.items() if pattern.search(text)}
    axes.update(stage_axes)
    if stage_axes:
        axes.add("STAGE")
    return axes


def build_clean_pool(audit: Audit) -> dict[str, dict[str, object]]:
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


def reconstruct_analogs_and_fields(audit: Audit, windows: Sequence[Mapping[str, object]]) -> tuple[list[dict[str, object]], dict[str, list[dict[str, object]]], dict[str, dict[str, object]]]:
    pool = build_clean_pool(audit)
    provenance = unique(read_tsv(G754), "surface")
    later_display = unique(read_tsv(G768), "surface")
    relations = [row for row in read_tsv(G781_ANALOGY) if row["candidate_surface"] == "chsky"]
    audit.check(len(relations) == 4, "four inherited chsky analogy relations")
    audit.check({row["known_neighbor_surface"] for row in relations} == {"cheky", "chky", "choky", "chyky"}, "fixed four analog surfaces")
    analogs: list[dict[str, object]] = []
    for row in relations:
        surface = row["known_neighbor_surface"]
        blocked = surface in provenance and provenance[surface]["source_literal_prose_spoken_after_gdt754"] == "0"
        admissible = int(not blocked and surface in pool)
        analogs.append({
            "surface": surface,
            "relation_id": row["relation_id"],
            "blocked_gdt754": int(blocked),
            "admissible": admissible,
            "axes": joined(with_generic_stage(split_axes(str(pool[surface]["axes"])))) if surface in pool else "NONE",
            "source_axes": row["known_neighbor_core_axes"],
        })
    audit.check(Counter(item["admissible"] for item in analogs) == Counter({1: 3, 0: 1}), "three admissible analogs one blocked")
    blocked = [item for item in analogs if item["blocked_gdt754"]]
    audit.check(len(blocked) == 1 and blocked[0]["surface"] == "chky", "GDT754 blocks only chky")
    audit.check(provenance["chky"]["later_role_axes_selected"] == "HOT|DRY|BEGIN_STAGE|PROCESS|CLOSE", "blocked chky retains only background axes")
    # The inherited relation deck freezes its candidate consensus from the
    # donors' source axes. Generic STAGE is a later descriptive normalization
    # and must not be promoted into the inherited analogy consensus.
    admissible_axis_sets = [split_axes(str(item["source_axes"])) for item in analogs if item["admissible"]]
    audit.check(set.intersection(*admissible_axis_sets) == {"HOT", "DRY"}, "admissible analog core remains HOT and DRY")

    fields: defaultdict[str, list[dict[str, object]]] = defaultdict(list)
    for row in windows:
        if not row["reader_consensus_neighbor"] or not row["within_primary_radius"]:
            continue
        surface = str(row["consensus_surface"])
        clean = pool.get(surface)
        blocked_neighbor = surface in provenance and provenance[surface]["source_literal_prose_spoken_after_gdt754"] == "0"
        admissible = int(clean is not None and not blocked_neighbor)
        display = "NONE"
        axes = "NONE"
        if clean is not None:
            display = str(clean["default"])
            axes = str(clean["axes"])
        if surface in later_display:
            display = later_display[surface]["concrete_default_de"]
        fields[str(row["locus"])].append({
            **row,
            "clean_pool_present": int(clean is not None),
            "blocked_gdt754": int(blocked_neighbor),
            "field_vote_admissible": admissible,
            "clean_default_de": display,
            "clean_axes": axes if admissible else "NONE",
        })
    audit.check(set(fields) == set(LOCUS_SPECS), "three independently reconstructed masked fields")
    audit.check(all(row["target_masked"] == 1 for row in fields["f86v5.15"]), "target field is sensitivity-only and masked")
    audit.check(any(row["consensus_surface"] == "chor" and row["clean_default_de"] == "Blütenstand" for row in fields["f25r.2"]), "current chor display at strong external field")
    f25_axes = set().union(*(split_axes(str(row["clean_axes"])) for row in fields["f25r.2"] if row["field_vote_admissible"]))
    f103_axes = set().union(*(split_axes(str(row["clean_axes"])) for row in fields["f103r.37"] if row["field_vote_admissible"]))
    target_axes = set().union(*(split_axes(str(row["clean_axes"])) for row in fields["f86v5.15"] if row["field_vote_admissible"]))
    audit.check("DRY" in f25_axes, "strong f25 field contains dry support")
    audit.check("HOT" in f103_axes, "weak f103 field contains hot support")
    audit.check("HOT" in target_axes and "DRY" not in target_axes, "masked target context contains hot but not dry")
    return analogs, dict(fields), pool


def validate_historical_sources(audit: Audit) -> None:
    specs = read_tsv(HISTORICAL_SPECS)
    audit.check(len(specs) == 3 and [row["comparator_id"] for row in specs] == ["G783-H01", "G783-H02", "G783-H03"], "three frozen historical comparators")
    observations = read_tsv(G622_OBSERVATIONS)
    audit.check(len(observations) == 28, "28 bound Clm 667 observations")
    audit.check(
        all(row["thermal"] in {"HOT", "COLD"} and row["moisture"] in {"", "DRY", "MOIST"} for row in observations),
        "Clm 667 thermal plus optional moisture fields",
    )
    audit.check(Counter(row["thermal"] for row in observations) == Counter({"HOT": 23, "COLD": 5}), "Clm 667 thermal census")
    comparators = unique(read_tsv(G626_COMPARATORS), "source_id")
    for source_id in ("WELLCOME_MS542_QUALITY", "VAT_PAL_LAT_1234"):
        audit.check(source_id in comparators, f"bound historical source {source_id}")
    audit.check("calidum et siccum" in comparators["WELLCOME_MS542_QUALITY"]["witness_or_text"].lower(), "Wellcome hot-dry witness")
    audit.check("calide" in " ".join(comparators["VAT_PAL_LAT_1234"].values()).lower(), "Pal.lat. thermal rubric witness")
    audit.check(all(row["voynich_form_credit"] == row["lexeme_credit"] == row["component_export_credit"] == "0" for row in specs), "historical sources have zero form or lexical credit")


def validate_public_artifacts(
    audit: Audit,
    loci: Mapping[str, Mapping[str, object]],
    windows: Sequence[Mapping[str, object]],
    analogs: Sequence[Mapping[str, object]],
    fields: Mapping[str, Sequence[Mapping[str, object]]],
    pool: Mapping[str, Mapping[str, object]],
    guard_stats: Mapping[str, Mapping[str, int]],
) -> tuple[str, list[str]]:
    locus_meta = {
        "f86v5.15": {
            "id": "G783-L001", "folio": "f86", "role": "TARGET_MASKED_SENSITIVITY",
            "variant": "EXACT_3_OF_3", "radius": 5, "warning": 99,
            "external": "0", "sensitivity": "1",
        },
        "f25r.2": {
            "id": "G783-L002", "folio": "f25", "role": "EXTERNAL_STRONG_MAJORITY",
            "variant": "ZL_RF_CHSKY__IT_CHRKY", "radius": 3, "warning": 4,
            "external": "1", "sensitivity": "0",
        },
        "f103r.37": {
            "id": "G783-L003", "folio": "f103", "role": "EXTERNAL_WEAK_MAJORITY",
            "variant": "ZL_IT_CHSKY__RF_CHSTY", "radius": 3, "warning": 1,
            "external": "1", "sensitivity": "0",
        },
    }

    locus_rows = read_tsv(ART / "GDT783_3_PHYSICAL_LOCUS_ATLAS.tsv")
    audit.check(len(locus_rows) == 3, "three published physical loci")
    locus_by_name = unique(locus_rows, "locus")
    audit.check(set(locus_by_name) == set(loci), "published physical locus identity")
    for locus, reconstructed in loci.items():
        row = locus_by_name[locus]
        meta = locus_meta[locus]
        readers = reconstructed["readers"]
        audit.check(row["locus_id"] == meta["id"] and row["page"] == reconstructed["page"] and row["physical_folio"] == meta["folio"], f"locus identity {locus}")
        audit.check(row["locus_role"] == meta["role"] and row["variant_strength"] == meta["variant"], f"locus role and variant strength {locus}")
        audit.check(row["target_ordinal_in_each_reader"] == str(reconstructed["zl3b_ordinal"]), f"target ordinal {locus}")
        audit.check(tuple(row[name] for name in ("zl3b_target_form", "it2a_target_form", "rf1b_target_form")) == reconstructed["reader_surfaces"], f"published reader forms {locus}")
        audit.check(row["majority_surface"] == "chsky" and int(row["majority_reader_count"]) == reconstructed["majority_count"], f"physical majority {locus}")
        audit.check(row["physical_locus_weight"] == "1" and row["alternate_readers_counted_independently"] == "0", f"one physical vote {locus}")
        audit.check(row["external_field_vote"] == meta["external"] and row["target_context_sensitivity_only"] == meta["sensitivity"], f"external versus sensitivity field {locus}")
        audit.check(row["primary_field_radius"] == str(meta["radius"]) and row["alignment_warning_from_positive_offset"] == str(meta["warning"]), f"field geometry policy {locus}")
        audit.check(tuple(row[name] for name in ("zl3b_line", "it2a_line", "rf1b_line")) == tuple(" ".join(reader) for reader in readers), f"three reader lines {locus}")
        audit.check(row["target_masked_in_all_reader_fields"] == "1" and row["variant_letters_semantically_exported"] == row["default_is_translation"] == "0", f"mask and zero variant credit {locus}")

    provenance = unique(read_tsv(G754), "surface")
    later_display = unique(read_tsv(G768), "surface")
    neighbor_rows = read_tsv(ART / "GDT783_28_POSITIONAL_READER_CONSENSUS_NEIGHBOR_ATLAS.tsv")
    audit.check(len(neighbor_rows) == 28 and len({row["neighbor_id"] for row in neighbor_rows}) == 28, "28 unique published positional neighbors")
    neighbors_by_key = {(row["locus"], int(row["neighbor_ordinal"])): row for row in neighbor_rows}
    audit.check(set(neighbors_by_key) == {(str(row["locus"]), int(row["neighbor_ordinal"])) for row in windows}, "complete positional-neighbor key set")
    for expected in windows:
        locus = str(expected["locus"])
        row = neighbors_by_key[(locus, int(expected["neighbor_ordinal"]))]
        meta = locus_meta[locus]
        surface = str(expected["consensus_surface"])
        clean = pool.get(surface) if surface != "NONE" else None
        sanitized = surface in provenance and provenance[surface]["source_literal_prose_spoken_after_gdt754"] == "0"
        if expected["consensus_class"] == "NO_MAJORITY":
            neighbor_class = "NO_READER_MAJORITY"
        elif sanitized:
            neighbor_class = "SANITIZED_GDT754_WHOLE_HYPOTHESIS"
        elif clean is not None:
            neighbor_class = "CLEAN_W2W3_COMPLETE_WHOLE"
        else:
            neighbor_class = "OPEN_OR_NONAXIS_MAJORITY_WHOLE"
        clean_ids = str(clean["reading_ids"]) if clean is not None else "NONE"
        clean_axes = str(clean["axes"]) if clean is not None and not sanitized else "NONE"
        display = str(clean["default"]) if clean is not None else "NONE"
        if surface in later_display:
            display = later_display[surface]["concrete_default_de"]
        if sanitized:
            display = provenance[surface]["current_working_whole_default_de"]
        eligible = int(bool(expected["within_primary_radius"] and expected["reader_consensus_neighbor"] and clean is not None and not sanitized))
        audit.check(row["locus_id"] == meta["id"] and row["locus_role"] == meta["role"], f"neighbor locus metadata {locus}:{expected['neighbor_ordinal']}")
        audit.check(int(row["target_ordinal"]) == loci[locus]["zl3b_ordinal"] and int(row["neighbor_ordinal"]) == expected["neighbor_ordinal"], f"neighbor ordinals {locus}:{expected['neighbor_ordinal']}")
        audit.check(int(row["offset"]) == expected["offset"] and int(row["absolute_distance"]) == abs(int(expected["offset"])), f"neighbor offset {locus}:{expected['neighbor_ordinal']}")
        audit.check(tuple(row[name] for name in ("zl3b_surface", "it2a_surface", "rf1b_surface")) == (expected["zl3b_surface"], expected["it2a_surface"], expected["rf1b_surface"]), f"neighbor reader surfaces {locus}:{expected['neighbor_ordinal']}")
        audit.check(row["majority_surface"] == surface and int(row["majority_reader_count"]) == expected["consensus_count"] and row["reader_consensus_class"] == expected["consensus_class"], f"neighbor majority {locus}:{expected['neighbor_ordinal']}")
        audit.check(row["neighbor_class"] == neighbor_class and row["clean_pool_reading_ids"] == clean_ids and row["clean_pool_axes"] == clean_axes, f"neighbor clean classification {locus}:{expected['neighbor_ordinal']}")
        audit.check(row["working_display_de"] == display, f"neighbor display {locus}:{expected['neighbor_ordinal']}")
        audit.check(int(row["gdt754_provenance_present"]) == int(surface in provenance), f"neighbor GDT754 presence {locus}:{expected['neighbor_ordinal']}")
        audit.check(row["gdt754_renderer_disposition"] == (provenance[surface]["renderer_disposition"] if surface in provenance else "NONE"), f"neighbor GDT754 disposition {locus}:{expected['neighbor_ordinal']}")
        audit.check(row["gdt754_sanitized_axes"] == (provenance[surface]["later_role_axes_selected"] if sanitized else "NONE"), f"neighbor GDT754 axes {locus}:{expected['neighbor_ordinal']}")
        audit.check(int(row["gdt768_display_override"]) == int(surface in later_display), f"neighbor later display {locus}:{expected['neighbor_ordinal']}")
        audit.check(int(row["within_primary_radius"]) == expected["within_primary_radius"] and int(row["eligible_field_vote"]) == eligible, f"neighbor eligibility {locus}:{expected['neighbor_ordinal']}")
        audit.check(int(row["reader_boundary_shift_warning"]) == expected["reader_boundary_shift_warning"], f"boundary warning {locus}:{expected['neighbor_ordinal']}")
        audit.check(row["target_slot_removed_before_reading"] == row["physical_locus_weight"] == "1", f"neighbor target mask and one-locus weight {locus}:{expected['neighbor_ordinal']}")
        audit.check(row["alternate_readers_counted_independently"] == row["variant_letters_semantically_exported"] == row["component_export_credit"] == "0", f"neighbor zero reader/variant/component credits {locus}:{expected['neighbor_ordinal']}")
    audit.check(sum(int(row["eligible_field_vote"]) for row in neighbor_rows) == 10, "ten eligible positional consensus donors")
    audit.check(sum(int(row["gdt754_provenance_present"]) for row in neighbor_rows) == 0, "zero GDT754 neighbor exposures")
    audit.check(sum(int(row["gdt768_display_override"]) for row in neighbor_rows) == 1, "one current-display override")

    def axis_contact_string(counter: Counter[str]) -> str:
        return "|".join(f"{axis}:{counter[axis]}" for axis in AXIS_ORDER if counter[axis]) or "NONE"

    summary_rows = read_tsv(ART / "GDT783_3_TARGET_MASKED_FIELD_SUMMARY.tsv")
    audit.check(len(summary_rows) == 3, "three field summaries")
    summary_by_locus = unique(summary_rows, "locus")
    reconstructed_field_axes: dict[str, set[str]] = {}
    for locus, meta in locus_meta.items():
        row = summary_by_locus[locus]
        donor_rows = [item for item in fields[locus] if item["field_vote_admissible"]]
        axes_counter: Counter[str] = Counter()
        for item in donor_rows:
            axes_counter.update(with_generic_stage(split_axes(str(item["clean_axes"]))))
        axis_union = set(axes_counter)
        reconstructed_field_axes[locus] = axis_union
        donor_surfaces = "|".join(str(item["consensus_surface"]) for item in donor_rows) or "NONE"
        audit.check(row["locus_id"] == meta["id"] and row["locus_role"] == meta["role"] and row["variant_strength"] == meta["variant"], f"field summary identity {locus}")
        audit.check(int(row["primary_radius"]) == meta["radius"] and int(row["eligible_consensus_donors"]) == len(donor_rows), f"field summary donor count {locus}")
        audit.check(row["eligible_consensus_surfaces"] == donor_surfaces, f"field donor sequence {locus}")
        audit.check(row["field_axis_union"] == joined(axis_union) and row["field_axis_contacts"] == axis_contact_string(axes_counter), f"field axes {locus}")
        flag_axes = {
            "hot_present": "HOT", "cold_present": "COLD", "dry_present": "DRY",
            "moist_present": "MOIST", "material_present": "MATERIAL",
            "preparation_present": "PREPARATION", "process_present": "PROCESS",
            "stage_present": "STAGE",
        }
        for field_name, axis in flag_axes.items():
            audit.check(int(row[field_name]) == int(axis in axis_union), f"field axis flag {locus}:{axis}")
        audit.check(row["target_masked"] == row["physical_locus_weight"] == "1", f"summary masked and one-locus weight {locus}")
        audit.check(row["alternate_readers_counted_independently"] == row["field_axes_are_target_meanings"] == row["component_export_credit"] == "0", f"summary zero semantic export {locus}")
    audit.check(Counter(int(row["eligible_consensus_donors"]) for row in summary_rows) == Counter({3: 2, 4: 1}), "field donor split 4/3/3")

    relation_rows = {row["known_neighbor_surface"]: row for row in read_tsv(G781_ANALOGY) if row["candidate_surface"] == "chsky"}
    analog_rows = read_tsv(ART / "GDT783_4_GDT781_ANALOG_PROVENANCE_AUDIT.tsv")
    audit.check(len(analog_rows) == 4 and len({row["audit_id"] for row in analog_rows}) == 4, "four published analog audits")
    analog_by_surface = unique(analog_rows, "donor_surface")
    audit.check(set(analog_by_surface) == {str(item["surface"]) for item in analogs}, "analog audit surfaces")
    for item in analogs:
        surface = str(item["surface"])
        row = analog_by_surface[surface]
        relation = relation_rows[surface]
        present = surface in provenance
        blocked = bool(item["blocked_gdt754"])
        audit.check(row["gdt781_relation_id"] == item["relation_id"] and row["candidate_surface"] == "chsky", f"analog relation identity {surface}")
        audit.check(row["whole_levenshtein_distance"] == "1" and row["gdt781_donor_default_de"] == relation["known_neighbor_best_gloss_de"], f"analog inherited card {surface}")
        audit.check(row["current_clean_pool_axes"] == item["axes"], f"analog independently reconstructed axes {surface}")
        audit.check(int(row["gdt754_provenance_present"]) == int(present), f"analog GDT754 presence {surface}")
        audit.check(row["gdt754_source_literal_spoken"] == (provenance[surface]["source_literal_prose_spoken_after_gdt754"] if present else "NONE"), f"analog GDT754 speech gate {surface}")
        audit.check(row["gdt754_current_whole_default_de"] == (provenance[surface]["current_working_whole_default_de"] if present else "NONE"), f"analog GDT754 current default {surface}")
        audit.check(row["audit_decision"] == ("BLOCK_GDT754_SOURCE_COMPOSITION" if blocked else "KEEP_CLEAN_COMPLETE_WHOLE_ANALOG"), f"analog provenance decision {surface}")
        audit.check(int(row["eligible_analogy_vote"]) == item["admissible"], f"analog eligibility {surface}")
        audit.check(int(row["hot_axis_vote"]) == int(bool(item["admissible"] and "HOT" in split_axes(str(item["axes"])))) and int(row["dry_axis_vote"]) == int(bool(item["admissible"] and "DRY" in split_axes(str(item["axes"])))), f"analog axis votes {surface}")
        audit.check(row["donor_identity_exported"] == row["substring_or_variant_letter_used"] == row["component_export_credit"] == "0", f"analog zero export {surface}")
    audit.check(sum(int(row["eligible_analogy_vote"]) for row in analog_rows) == 3, "three clean analogy votes")

    historical_rows = read_tsv(ART / "GDT783_3_HISTORICAL_COMPARATOR_AUDIT.tsv")
    historical_specs = unique(read_tsv(HISTORICAL_SPECS), "comparator_id")
    audit.check(len(historical_rows) == 3 and set(row["comparator_id"] for row in historical_rows) == set(historical_specs), "three historical audit rows")
    observations = read_tsv(G622_OBSERVATIONS)
    historical_source_rows = unique(read_tsv(G626_COMPARATORS), "source_id")
    for row in historical_rows:
        spec = historical_specs[row["comparator_id"]]
        for field_name, value in spec.items():
            audit.check(row[field_name] == value, f"historical spec copy {row['comparator_id']}:{field_name}")
        if row["source_id"] == "GDT622_CLM667":
            audit.check(row["bound_witness"] == "GDT622 bound CLM667 source-observation census", "CLM667 bound witness")
            hot_dry = sum(item["thermal"] == "HOT" and item["moisture"] == "DRY" for item in observations)
            hot_moist = sum(item["thermal"] == "HOT" and item["moisture"] == "MOIST" for item in observations)
            hot_only = sum(item["thermal"] == "HOT" and item["moisture"] == "" for item in observations)
            audit.check(row["observed_architecture"] == f"28 rows: HOT+DRY={hot_dry}; HOT+MOIST={hot_moist}; HOT-only={hot_only}", "CLM667 observed architecture")
            audit.check(row["source_url"] == observations[0]["image_url"], "CLM667 bound source URL")
            expected_pair = "1"
        else:
            source = historical_source_rows[row["source_id"]]
            audit.check(row["bound_witness"] == source["witness_or_text"] and row["observed_architecture"] == source["mechanism_relevant_to_gdt626"] and row["source_url"] == source["url"], f"bound historical source row {row['source_id']}")
            expected_pair = "1" if row["source_id"] == "WELLCOME_MS542_QUALITY" else "0"
        audit.check(row["supports_hot_slot_architecture"] == "1" and row["supports_hot_dry_pair_architecture"] == expected_pair, f"historical architecture flags {row['comparator_id']}")
        audit.check(row["selects_chsky_candidate"] == row["default_is_translation"] == "0", f"historical source does not select candidate {row['comparator_id']}")

    candidate_specs = read_tsv(CANDIDATES)
    candidate_rows = read_tsv(ART / "GDT783_6_CANDIDATE_SCORECARDS.tsv")
    audit.check(len(candidate_specs) == len(candidate_rows) == 6, "six candidate specs and scorecards")
    candidates_by_id = unique(candidate_rows, "candidate_id")
    audit.check(set(candidates_by_id) == {row["candidate_id"] for row in candidate_specs}, "candidate identity set")
    analog_axis_sets = [split_axes(str(item["axes"])) for item in analogs if item["admissible"]]
    external_axis_sets = [reconstructed_field_axes[locus] for locus in ("f25r.2", "f103r.37")]
    target_axis_set = reconstructed_field_axes["f86v5.15"]
    opposite = {"HOT": "COLD", "COLD": "HOT", "DRY": "MOIST", "MOIST": "DRY"}
    computed_scores: dict[str, float] = {}
    for spec in candidate_specs:
        row = candidates_by_id[spec["candidate_id"]]
        for field_name, value in spec.items():
            audit.check(row[field_name] == value, f"candidate spec copy {spec['candidate_id']}:{field_name}")
        axes = split_axes(spec["candidate_axes"])
        analog_full = sum(axes <= donor_axes for donor_axes in analog_axis_sets)
        external_full = sum(axes <= field_axes for field_axes in external_axis_sets)
        target_full = int(axes <= target_axis_set)
        external_mean = sum(sum(axis in field_axes for field_axes in external_axis_sets) / len(external_axis_sets) for axis in axes) / len(axes)
        target_coverage = sum(axis in target_axis_set for axis in axes) / len(axes)
        opposed = sum(sum(opposite.get(axis) in field_axes for field_axes in (*external_axis_sets, target_axis_set)) for axis in axes if axis in opposite)
        complexity = 0.5 * (len(axes) - 1)
        continuity = 0.25 * int(spec["parent_candidate"])
        score = 2 * analog_full + 3 * external_full + target_full + external_mean + 0.5 * target_coverage - opposed - complexity + continuity
        computed_scores[spec["candidate_id"]] = score
        audit.check(int(row["eligible_analogy_full_support"]) == analog_full and int(row["external_physical_locus_full_support"]) == external_full and int(row["target_masked_context_full_support"]) == target_full, f"candidate full-support counts {spec['candidate_id']}")
        audit.check(row["external_axis_presence_mean"] == f"{external_mean:.6f}" and row["target_axis_coverage"] == f"{target_coverage:.6f}", f"candidate axis coverage {spec['candidate_id']}")
        audit.check(int(row["opposed_field_contacts"]) == opposed and row["axis_complexity_penalty"] == f"{complexity:.6f}" and row["parent_continuity_bonus"] == f"{continuity:.6f}", f"candidate penalties and continuity {spec['candidate_id']}")
        audit.check(row["exploratory_score"] == f"{score:.6f}", f"candidate score {spec['candidate_id']}")
        audit.check(row["score_formula"] == "2*A_FULL+3*E_FULL+T_FULL+E_AXIS_MEAN+0.5*T_AXIS_COVERAGE-OPPOSITION-0.5*(AXES-1)+0.25*PARENT", f"published score formula {spec['candidate_id']}")
        audit.check(row["score_is_lexical_probability"] == row["variant_letters_used_as_features"] == "0", f"candidate score zero lexical/variant claim {spec['candidate_id']}")
    ranking = sorted(computed_scores, key=lambda candidate_id: (-computed_scores[candidate_id], candidate_id))
    audit.check([int(candidates_by_id[candidate_id]["score_rank"]) for candidate_id in ranking] == list(range(1, 7)), "deterministic candidate rank")
    score_winners = [row["candidate_id"] for row in candidate_rows if row["score_selected"] == "1"]
    audit.check(score_winners == [ranking[0]], "unique deterministic score winner")

    final_rows = read_tsv(FINAL_SELECTION)
    audit.check(len(final_rows) == 1, "one frozen final-selection row")
    final = final_rows[0]
    selected_id = final["selected_candidate_id"]
    dissent_id = final["dissent_candidate_id"]
    audit.check(selected_id in candidates_by_id and dissent_id in candidates_by_id and selected_id != dissent_id, "frozen practical selection and dissent candidates")
    audit.check(final["portable_minimum_core_axes"] == "HOT" and final["portable_minimum_core_de"] == candidates_by_id["C01_HOT_QUALITY"]["portable_default_de"], "HOT portable minimum core")
    audit.check(final["practical_whole_default_de"] == candidates_by_id[selected_id]["portable_default_de"] and final["target_span_default_de"] == candidates_by_id[selected_id]["target_span_default_de"], "practical candidate values copied")
    audit.check(final["dissent_candidate_id"] == ranking[0] and candidates_by_id[ranking[0]]["portable_default_de"] == "heiß", "score-winning HOT-only dissent retained")
    audit.check(sum(int(row["practical_selection_spec"]) for row in candidate_rows) == 1 and candidates_by_id[selected_id]["practical_selection_spec"] == "1", "one practical selection linked to final spec")
    audit.check(final["hot_confidence"] == "C1_ROLE" and final["dry_confidence"] == "C0_STANDING_RIVAL", "split HOT and DRY confidence")
    audit.check("DRY" in split_axes(candidates_by_id[selected_id]["candidate_axes"]) and "HOT" in split_axes(candidates_by_id[selected_id]["candidate_axes"]), "practical card retains HOT and DRY")
    audit.check("HOT-only" in final["counterevidence_de"] and "DRY" in final["counterevidence_de"], "published HOT-only dissent and unresolved DRY")
    audit.check(final["default_is_translation"] == final["confirmed_lexeme"] == final["confirmed_plaintext"] == final["component_export_credit"] == final["variant_letter_export_credit"] == "0", "final selection zero plaintext/component/variant credit")

    revisions = read_tsv(ART / "GDT783_1_WORKING_REVISION.tsv")
    audit.check(len(revisions) == 1, "one working revision")
    revision = revisions[0]
    for field_name, value in final.items():
        audit.check(revision[field_name] == value, f"revision final-spec copy {field_name}")
    parent_cards = [row for row in read_tsv(G781_CARD) if row["surface"] == "chsky"]
    audit.check(len(parent_cards) == 1 and revision["gdt781_parent_default_de"] == parent_cards[0]["preferred_gdt781_default_de"], "revision parent card")
    audit.check(revision["selected_exploratory_score"] == f"{computed_scores[selected_id]:.6f}" and revision["dissent_exploratory_score"] == f"{computed_scores[dissent_id]:.6f}" and revision["score_winner_candidate_id"] == ranking[0], "revision publishes score/practical disagreement")
    audit.check(revision["eligible_analogs"] == "3" and revision["blocked_analogs"] == "1" and revision["external_physical_loci"] == "2", "revision evidence counts")
    audit.check(revision["external_hot_loci"] == revision["external_dry_loci"] == "1" and revision["external_display_license"] == "0", "revision split external axes and zero outside licence")

    patches = read_tsv(ART / "GDT783_1_TARGET_PASSAGE_PATCH.tsv")
    audit.check(len(patches) == 1, "one target passage patch")
    patch = patches[0]
    parent_renderer = read_tsv(G782_RENDERER)
    parent_by_id = unique(parent_renderer, "target_occurrence_id")
    parent_target = parent_by_id["G769-T0466"]
    audit.check((patch["target_occurrence_id"], patch["locus"], patch["right_surface"], patch["ol_ordinal"], patch["right_ordinal"]) == ("G769-T0466", "f86v5.15", "chsky", "11", "12"), "target patch coordinate")
    audit.check(patch["written_line_eva"] == parent_target["written_line_eva"] and patch["gdt781_span_id"] == "G781-S020", "target patch parent line and span")
    audit.check(patch["practical_whole_default_de"] == final["practical_whole_default_de"] and patch["portable_minimum_core_de"] == final["portable_minimum_core_de"], "target patch frozen meanings")
    audit.check(f"⟦{parent_target['gdt782_default_de']}⟧" in patch["gdt782_inherited_patch_de"] and f"⟦{final['target_span_default_de']}⟧" in patch["gdt783_practical_patch_de"], "target patch before/after display")
    audit.check(patch["target_masked_during_adjudication"] == "1" and patch["new_token_consumption"] == patch["default_is_translation"] == patch["confirmed_plaintext"] == patch["component_export_credit"] == "0", "target patch mask and zero claims")

    external_readers = read_tsv(ART / "GDT783_2_EXTERNAL_WORKING_READER.tsv")
    audit.check(len(external_readers) == 2 and {row["locus"] for row in external_readers} == {"f25r.2", "f103r.37"}, "two external audit readers")
    for row in external_readers:
        reconstructed = loci[row["locus"]]
        audit.check(row["reader_target_forms"] == "/".join(reconstructed["reader_surfaces"]) and row["majority_surface"] == "chsky", f"external reader variant forms {row['locus']}")
        audit.check(row["practical_card_under_test_de"] == final["practical_whole_default_de"] and row["portable_minimum_core_de"] == final["portable_minimum_core_de"], f"external reader frozen cards {row['locus']}")
        audit.check(row["status"] == "AGGREGATE_CARD_AUDIT_NOT_EXTERNAL_RENDERER_LICENSE" and row["external_renderer_license"] == "0", f"external reader no licence {row['locus']}")
        audit.check(row["default_is_translation"] == row["confirmed_plaintext"] == row["variant_letter_export_credit"] == row["component_export_credit"] == "0", f"external reader zero claims {row['locus']}")
    audit.check("⟨Blütenstand⟩" in next(row for row in external_readers if row["locus"] == "f25r.2")["working_consensus_field_render_de"], "f25 reader current plant-part display")
    audit.check("heiß am Ende des Grades" in next(row for row in external_readers if row["locus"] == "f103r.37")["working_consensus_field_render_de"], "f103 reader hot field visible")

    renderer = read_tsv(ART / "GDT783_376_RENDERER.tsv")
    audit.check(len(parent_renderer) == len(renderer) == 376, "376 parent and child renderer rows")
    parent_fields = list(parent_renderer[0])
    audit.check(len(parent_fields) == 109 and all(field_name in renderer[0] for field_name in parent_fields), "109 inherited parent columns")
    renderer_by_id = unique(renderer, "target_occurrence_id")
    audit.check(set(renderer_by_id) == set(parent_by_id), "renderer occurrence identity preserved")
    for occurrence_id, parent_row in parent_by_id.items():
        child = renderer_by_id[occurrence_id]
        for field_name in parent_fields:
            audit.check(child[field_name] == parent_row[field_name], f"inherited renderer field {occurrence_id}:{field_name}")
    target_rows = [row for row in renderer if row["gdt783_card_id"] != "NONE"]
    audit.check(len(target_rows) == 1 and target_rows[0]["target_occurrence_id"] == "G769-T0466", "one target-only GDT783 renderer mutation")
    target_row = target_rows[0]
    audit.check(target_row["gdt783_default_de"] == final["target_span_default_de"] and target_row["gdt783_practical_whole_default_de"] == final["practical_whole_default_de"] and target_row["gdt783_portable_minimum_core_de"] == final["portable_minimum_core_de"], "renderer selected displays")
    audit.check(target_row["gdt783_decision"] == final["decision"] and target_row["gdt783_functional_axes"] == candidates_by_id[selected_id]["candidate_axes"], "renderer final decision and axes")
    audit.check(target_row["gdt783_external_physical_loci"] == "2" and target_row["gdt783_variant_policy"] == "PHYSICAL_LOCUS_ONCE__TWO_OF_THREE_ADMITTED__NO_VARIANT_LETTER_EXPORT", "renderer physical-locus variant policy")
    audit.check(sum(int(row["gdt783_renderer_contextual"]) for row in renderer) == 270 and sum(1 - int(row["gdt783_renderer_contextual"]) for row in renderer) == 106, "renderer 270 contextual and 106 fallback")
    audit.check(sum(int(row["gdt783_display_changed"]) for row in renderer) == 1 and sum(row["gdt783_card_id"] == "NONE" and row["gdt783_display_changed"] == "0" for row in renderer) == 375, "one target display change only")
    consumed = {token for row in renderer for token in row["gdt783_consumed_token_ids"].split("|") if token != "NONE"}
    audit.check(len(consumed) == 230 and sum(int(row["gdt783_consumed_token_count"]) for row in renderer) == 230, "230 unchanged noncolliding consumptions")
    audit.check(all(row["gdt783_default_is_translation"] == row["gdt783_confirmed_lexeme"] == row["gdt783_confirmed_plaintext"] == row["gdt783_component_export_credit"] == row["gdt783_variant_letter_export_credit"] == "0" for row in renderer), "renderer zero translation/component/variant claims")

    zero_fields = {
        "default_is_translation", "confirmed_lexeme", "confirmed_plaintext",
        "component_export_credit", "variant_letter_export_credit",
        "variant_letters_semantically_exported", "variant_letters_used_as_features",
        "alternate_readers_counted_independently", "field_axes_are_target_meanings",
        "donor_identity_exported", "substring_or_variant_letter_used",
        "external_renderer_license", "selects_chsky_candidate", "score_is_lexical_probability",
        "score_eligible",
    }
    output_names = (
        "GDT783_3_PHYSICAL_LOCUS_ATLAS.tsv",
        "GDT783_28_POSITIONAL_READER_CONSENSUS_NEIGHBOR_ATLAS.tsv",
        "GDT783_3_TARGET_MASKED_FIELD_SUMMARY.tsv",
        "GDT783_4_GDT781_ANALOG_PROVENANCE_AUDIT.tsv",
        "GDT783_3_HISTORICAL_COMPARATOR_AUDIT.tsv",
        "GDT783_6_CANDIDATE_SCORECARDS.tsv",
        "GDT783_1_WORKING_REVISION.tsv",
        "GDT783_1_TARGET_PASSAGE_PATCH.tsv",
        "GDT783_2_EXTERNAL_WORKING_READER.tsv",
        "GDT783_376_RENDERER.tsv",
        "GDT783_GDT388_VARIANT_FIELD_PACKET.tsv",
        "GDT783_RELATION_EDGE_CROSSWALK.tsv",
        "RELATION_PACKET_INTAKE.json",
        "RESULT.json",
    )
    for name in output_names:
        if not name.endswith(".tsv"):
            continue
        for row_number, row in enumerate(read_tsv(ART / name), 2):
            for field_name in zero_fields & set(row):
                audit.check(row[field_name] == "0", f"zero claim {name}:{row_number}:{field_name}")

    expected_intake = {
        "status": "VALID_ACQUISITION_NOT_SCORE_READY", "packet_rows": 2,
        "eligible_edges": 0, "eligible_folios": 0, "discovery_edges": 0,
        "holdout_edges": 0, "mobile_edges": 0,
        "capacity_gate_50_edges_5_folios": False, "holdout_gate": False,
        "mobile_null_gate": False, "score_ready": False, "errors": [],
    }
    intake = json.loads((ART / "RELATION_PACKET_INTAKE.json").read_text(encoding="utf-8"))
    audit.check(intake == expected_intake, "stored relation-packet intake")
    completed = subprocess.run(
        [str(ROOT / "vmanus-exp"), "check-edge-packet", str(ART / "GDT783_GDT388_VARIANT_FIELD_PACKET.tsv")],
        cwd=ROOT, text=True, capture_output=True, check=False,
    )
    audit.check(completed.returncode == 0 and json.loads(completed.stdout) == expected_intake, "executable relation-packet intake")
    packet = read_tsv(ART / "GDT783_GDT388_VARIANT_FIELD_PACKET.tsv")
    crosswalk = read_tsv(ART / "GDT783_RELATION_EDGE_CROSSWALK.tsv")
    audit.check(len(packet) == len(crosswalk) == 2 and {row["edge_id"] for row in packet} == {row["edge_id"] for row in crosswalk}, "two packet/crosswalk edges")
    audit.check({row["page"] for row in packet} == {"f25r", "f103r"}, "external edge pages")
    audit.check(all(row["eligibility_status"] == "INELIGIBLE_EXPLORATORY_TEXT_RELATION" and row["formal_access_state"] == "SEALED_NOT_ACCESSED" for row in packet), "packet ineligible and seals untouched")
    audit.check(all(row["physical_locus_weight"] == "1" and row["score_eligible"] == row["variant_letter_export_credit"] == row["component_export_credit"] == "0" for row in crosswalk), "crosswalk one physical locus and zero score/export")

    result = json.loads((ART / "RESULT.json").read_text(encoding="utf-8"))
    expected_status = (
        "PASS__3_PHYSICAL_LOCI_ONCE__1_TARGET_MASKED__2_EXTERNAL_MAJORITY_VARIANTS__"
        "28_POSITIONAL_NEIGHBORS__4_ANALOGS_1_GDT754_BLOCKED__"
        "PRACTICAL_HOT_DRY_WITH_HOT_MINIMUM_CORE__270_CONTEXTUAL__106_FALLBACKS__"
        "230_CONSUMED__ZERO_VARIANT_LETTER_EXPORT"
    )
    audit.check(result["experiment_id"] == "GDT783" and result["status"] == expected_status, "result identity and status")
    audit.check(result["source_locks"] == 17 and result["source_lock_sha256"] == sha256(LOCKS), "result source-lock binding")
    audit.check(result["source_spec_sha256"] == {"candidates": EXPECTED_CANDIDATE_HASH, "final_selection": EXPECTED_FINAL_SELECTION_HASH, "historical_comparators": EXPECTED_HISTORICAL_HASH}, "result source-spec hashes")
    audit.check(result["inherited_guard"] == guard_stats, "result guarded-query counts")
    audit.check(result["clean_pool"] == {"dictionary_rows": 1606, "clean_axis_reading_rows": 770, "clean_axis_whole_pool": 769}, "result clean-pool counts")
    audit.check(result["loci"] == {"physical_loci": 3, "masked_target_loci": 1, "external_majority_variant_loci": 2, "positional_neighbor_slots": 28, "eligible_primary_field_donors": 10, "gdt754_sanitized_neighbor_slots": 0, "gdt768_display_override_slots": 1, "alternate_reader_independent_votes": 0}, "result locus counts")
    audit.check(result["analogy"] == {"parent_analogs": 4, "eligible_clean_analogs": 3, "gdt754_blocked_analogs": 1, "blocked_surface": "chky", "eligible_common_axes": "HOT|DRY"}, "result analogy counts")
    audit.check(result["adjudication"]["practical_selected_candidate"] == selected_id and result["adjudication"]["score_winner"] == ranking[0] and result["adjudication"]["dissent_retained"] is True, "result practical/score dissent")
    audit.check(result["adjudication"]["practical_whole_default_de"] == final["practical_whole_default_de"] and result["adjudication"]["target_span_default_de"] == final["target_span_default_de"] and result["adjudication"]["portable_minimum_core_de"] == final["portable_minimum_core_de"], "result final meanings")
    audit.check(result["adjudication"]["hot_confidence"] == final["hot_confidence"] and result["adjudication"]["dry_confidence"] == final["dry_confidence"] and result["adjudication"]["external_renderer_licenses"] == 0, "result split confidence and no external licence")
    audit.check(result["renderer"] == {"rows": 376, "inherited_parent_columns": 109, "gdt782_contextual": 270, "gdt782_fallbacks": 106, "gdt783_contextual": 270, "gdt783_fallbacks": 106, "display_changes": 1, "unchanged_non_target_rows": 375}, "result renderer counts")
    audit.check(result["consumption"] == {"gdt782_unique_right_tokens": 230, "gdt783_unique_right_tokens": 230, "new_consumptions": 0, "collisions": 0}, "result consumption counts")
    audit.check(result["relation_packet"] == expected_intake, "result relation packet")
    for field_name in ("confirmed_lexemes", "confirmed_plaintext_clauses", "numeric_identities", "specific_substances", "component_exports", "variant_letter_exports", "new_pages", "new_images", "new_ocr", "new_transcriptions", "sealed_pages_accessed"):
        audit.check(result[field_name] == 0, f"result zero {field_name}")

    with tempfile.TemporaryDirectory(prefix="gdt783_replay_") as raw:
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
        for name in output_names:
            audit.check((replay_art / name).read_bytes() == (ART / name).read_bytes(), f"byte replay {name}")
            replayed.append(name)
        audit.check((replay_art / "README.md").read_bytes() == (ART / "README.md").read_bytes(), "byte replay artifact README")
        audit.check(replay_report.read_bytes() == REPORT.read_bytes(), "byte replay report")
        replayed.extend(("README.md", "../REPORT.md"))
    return selected_id, replayed


def main() -> int:
    audit = Audit()
    validate_locks(audit)
    loci, windows, guard_stats = reconstruct_loci(audit)
    analogs, fields, pool = reconstruct_analogs_and_fields(audit, windows)
    validate_historical_sources(audit)
    selected, replayed = validate_public_artifacts(audit, loci, windows, analogs, fields, pool, guard_stats)
    validation = {
        "experiment_id": "GDT783",
        "status": "PASS",
        "checks": audit.count,
        "source_locks": 17,
        "source_lock_sha256": sha256(LOCKS),
        "candidate_specs_sha256": sha256(CANDIDATES),
        "historical_specs_sha256": sha256(HISTORICAL_SPECS),
        "runner_sha256": sha256(RUN),
        "result_sha256": sha256(ART / "RESULT.json"),
        "report_sha256": sha256(REPORT),
        "independent_physical_locus_reconstruction": {
            "physical_loci": 3, "target_exact": 1, "external_two_of_three": 2,
            "strong_external": 1, "weak_external": 1,
        },
        "independent_window_reconstruction": {
            "rows": 28, "external_radius": 3, "target_sensitivity_radius": 5,
            "external_physical_loci": 2,
        },
        "independent_analogy_reconstruction": {
            "raw": 4, "admissible": 3, "gdt754_blocked": ["chky"],
            "admissible_core_axes": "HOT|DRY",
        },
        "selected_candidate_id": selected,
        "renderer": {"rows": 376, "contextual": 270, "fallback": 106, "consumed": 230},
        "byte_replay": "PASS",
        "replayed_files": replayed,
        "run_py_imported": False,
        "sealed_pages_accessed": 0,
    }
    (ART / "VALIDATION.json").write_text(
        json.dumps(validation, ensure_ascii=False, sort_keys=True, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"GDT783_VALIDATION_PASS {audit.count} checks; {len(replayed)} files replayed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
