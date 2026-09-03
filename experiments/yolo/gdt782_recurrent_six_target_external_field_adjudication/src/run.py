#!/usr/bin/env python3
"""Build GDT782's target-masked external-field adjudication."""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import re
import subprocess
import sys
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
REPORT = EXP / "REPORT.md"

ALLOWLIST = ROOT / "experiments/yolo/gdt635_initial_head_same_remainder_swaps/artifacts/PAGE_ALLOWLIST.tsv"
TOKENS = Path("transcription/voynich_zl3b_tokens.tsv")
CROSS = Path("transcription/voynich_cross_transcription_lines.tsv")
LINES = Path("transcription/voynich_zl3b_lines.tsv")
COMPACT = ROOT / "experiments/yolo/gdt734_v99r7_recurrent_unknown_family_dispatch/artifacts/V99R7_32339_COMPACT_CELL_REGISTER.tsv"
DICTIONARY = ROOT / "experiments/yolo/gdt734_v99r7_recurrent_unknown_family_dispatch/artifacts/V99R7_1606_COMPLETE_WORD_CONFIDENCE.tsv"
AXIS_SPECS = ROOT / "experiments/yolo/gdt739_twelve_whole_local_dimension_dispatch/src/ANCHOR_AXIS_SPECS.tsv"
G781_ART = ROOT / "experiments/yolo/gdt781_ol_remaining_23_exploratory_whole_projection/artifacts"
G781_SELECTED = G781_ART / "GDT781_23_SELECTED_ATLAS.tsv"
G781_RENDERER = G781_ART / "GDT781_376_RENDERER.tsv"
G781_CARDS = G781_ART / "GDT781_23_RECURRENCE_EVIDENCE_CARDS.tsv"
G781_ANALOGY = G781_ART / "GDT781_RAW_COMPLETE_WHOLE_ANALOGY_RELATIONS.tsv"
G781_RESULT = G781_ART / "RESULT.json"
G759_CONSTRUCTIONS = ROOT / "experiments/yolo/gdt759_quantity_part_state_construction_atlas/artifacts/EXACT_122_CONSTRUCTION_SPAN_ATLAS.tsv"
G754_PROVENANCE = ROOT / "experiments/yolo/gdt754_active_productive_compound_provenance_sieve/artifacts/PROVENANCE_SIEVE_172_DECISIONS.tsv"
G768_WORKING = ROOT / "experiments/yolo/gdt768_chor_shor_part_identity_tournament/artifacts/GDT768_6_WORKING_DICTIONARY.tsv"
HISTORICAL_ROLES = ROOT / "experiments/yolo/gdt735_historical_semantic_bridge_atlas/artifacts/SEMANTIC_BRIDGE_ROLE_DICTIONARY.tsv"
HISTORICAL_SLOTS = ROOT / "experiments/yolo/gdt735_historical_semantic_bridge_atlas/artifacts/HISTORICAL_SLOT_CENSUS.tsv"
SOURCE_LOCK = SRC / "SOURCE_LOCK.tsv"
CANDIDATES = SRC / "TARGET_6_CANDIDATES.tsv"
MANUAL = SRC / "MANUAL_READER_ASSESSMENTS.tsv"
FINAL_SPECS = SRC / "TARGET_6_FINAL_SPECS.tsv"

TARGET_ORDER = (
    "cheedaiin", "chedor", "chockhar", "keeor", "shdair", "sheckhal",
)
TARGETS = frozenset(TARGET_ORDER)
EXPECTED_TARGETS = {
    ("f112v.23", 6, "cheedaiin"): "G781-S004",
    ("f76r.53", 5, "chedor"): "G781-S013",
    ("f100v.20", 8, "chockhar"): "G781-S001",
    ("f113v.25", 10, "keeor"): "G781-S005",
    ("f85r1.11", 3, "shdair"): "G781-S018",
    ("f81v.7", 3, "sheckhal"): "G781-S017",
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
AXIS_ORDER = (
    "HOT", "COLD", "DRY", "MOIST", "AMOUNT", "PART", "MATERIAL",
    "PREPARATION", "PROCESS", "CLOSE", "PASS", "BEGIN_STAGE",
    "MIDDLE_STAGE", "END_STAGE", "LEVEL_II", "LEVEL_III",
)
EXPECTED_AXIS_SPEC_ORDER = (
    "HOT", "COLD", "DRY", "MOIST", "AMOUNT", "VALUE", "PART",
    "MATERIAL", "PREPARATION", "PROCESS", "CLOSE", "PASS",
)
STAGE_PATTERNS = {
    "BEGIN_STAGE": re.compile(
        r"anfangsstufe|gradanfang|anfang des grades|grundform|grundstufe", re.I
    ),
    "MIDDLE_STAGE": re.compile(
        r"mittelstufe|gradmitte|mitte des grades|mittlere|mittelstufig", re.I
    ),
    "END_STAGE": re.compile(
        r"endstufe|gradende|ende des grades|vollständig|fertig|abgeschlossen", re.I
    ),
    "LEVEL_II": re.compile(r"(?:stufe|grad|index|wert|klasse|charge) ii\b", re.I),
    "LEVEL_III": re.compile(r"(?:stufe|grad|index|wert|klasse|charge) iii\b", re.I),
}
RETIRED_LITERAL_PATIENTS = ("pulver", "samen", "saat", "wurzel", "holz")
DIMENSIONS = {
    "THERMAL": ("HOT", "COLD"),
    "MOISTURE": ("DRY", "MOIST"),
    "STAGE": ("BEGIN_STAGE", "MIDDLE_STAGE", "END_STAGE"),
}
STATUS = (
    "PASS__20_CACHE_OCCURRENCES__14_READER_EXACT__6_TARGET_MASKED__"
    "8_TARGET_EXTERNAL__65_EXTERNAL_NEIGHBORS__5_REVISED__1_KEPT__"
    "270_CONTEXTUAL__106_FALLBACKS__230_CONSUMED__ZERO_COMPONENT_EXPORT"
)
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


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def serialise(value: object) -> object:
    return int(value) if isinstance(value, bool) else value


def write_tsv(
    path: Path, rows: Iterable[Mapping[str, object]], fields: Sequence[str]
) -> None:
    names = list(fields)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle, fieldnames=names, delimiter="\t", lineterminator="\n",
            extrasaction="raise",
        )
        writer.writeheader()
        for row in rows:
            writer.writerow({name: serialise(row.get(name, "")) for name in names})


def write_json(path: Path, value: Mapping[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + "\n",
        encoding="utf-8",
    )


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def joined(values: Iterable[str]) -> str:
    chosen = set(values)
    return "|".join(axis for axis in AXIS_ORDER if axis in chosen) or "NONE"


def count_string(values: Iterable[str]) -> str:
    counter = Counter(values)
    return "|".join(
        f"{axis}:{counter[axis]}" for axis in AXIS_ORDER if counter[axis]
    ) or "NONE"


def split_axes(value: str) -> set[str]:
    return set() if value in {"", "NONE", "OPEN"} else set(value.split("|"))


def physical_folio(page: str) -> str:
    if page.startswith("fRos"):
        return "fRos"
    match = re.match(r"^(f\d+)", page)
    if match is None:
        raise AssertionError(f"invalid page: {page}")
    return match.group(1)


def page_sort_key(page: str) -> tuple[int, str]:
    match = re.match(r"^f(\d+)", page)
    if match is None:
        raise AssertionError(page)
    return int(match.group(1)), page


def line_number(locus: str) -> int:
    match = re.search(r"\.(\d+)$", locus)
    if match is None:
        raise AssertionError(locus)
    return int(match.group(1))


def line_position(ordinal: int, length: int) -> str:
    if length == 1:
        return "SINGLE"
    if ordinal == 1:
        return "FIRST"
    if ordinal == length:
        return "LAST"
    return "MIDDLE"


def one_by(
    rows: Sequence[Mapping[str, str]], key: str
) -> dict[str, dict[str, str]]:
    output: dict[str, dict[str, str]] = {}
    for row in rows:
        value = row[key]
        if value in output:
            raise AssertionError(f"duplicate {key}: {value}")
        output[value] = dict(row)
    return output


def verify_locks() -> tuple[int, str]:
    rows = read_tsv(SOURCE_LOCK)
    if not rows:
        raise AssertionError("empty source lock")
    for row in rows:
        relative = Path(row["path"])
        if relative.is_absolute() or ".." in relative.parts:
            raise AssertionError(f"unsafe source path: {relative}")
        actual = sha256(ROOT / relative)
        if actual != row["expected_sha256"]:
            raise AssertionError(f"source hash changed: {relative}")
    return len(rows), sha256(SOURCE_LOCK)


def guarded_query(
    relative_path: Path, pages: set[str], columns: str
) -> tuple[list[dict[str, str]], dict[str, int]]:
    command = [
        str(ROOT / "vmanus-exp"), "query-tsv", str(relative_path),
        "--selector", "page",
    ]
    for page in sorted(pages):
        command.extend(("--allow", page))
    command.extend((
        "--columns", columns,
        "--forbid-prefix", "f84",
        "--forbid-prefix", "f84r",
    ))
    completed = subprocess.run(
        command, cwd=ROOT, text=True, capture_output=True, check=False,
    )
    if completed.returncode:
        raise RuntimeError(completed.stderr or "guarded query failed")
    stats_lines = [
        line for line in completed.stderr.splitlines()
        if line.startswith("GUARD_STATS ")
    ]
    if len(stats_lines) != 1:
        raise RuntimeError("guard statistics missing")
    rows = list(csv.DictReader(io.StringIO(completed.stdout), delimiter="\t"))
    if any(
        row["page"] == "f1r" or row["page"].startswith("f84")
        for row in rows
    ):
        raise RuntimeError("forbidden page materialized")
    stats = {
        key: int(value)
        for key, value in json.loads(stats_lines[0][12:]).items()
    }
    return rows, stats


def load_context() -> tuple[
    dict[str, list[dict[str, str]]],
    dict[tuple[str, int], int],
    dict[str, dict[str, str]],
    dict[str, dict[str, str]],
    dict[tuple[str, int], dict[str, str]],
    dict[str, object],
]:
    pages = {row["page"] for row in read_tsv(ALLOWLIST)}
    if (
        len(pages) != 179 or "f1r" in pages
        or any(page.startswith("f84") for page in pages)
    ):
        raise AssertionError("inherited page allow-list changed")
    tokens, token_guard = guarded_query(
        TOKENS, pages, "page,locus,token_index,eva,section,language,hand",
    )
    cross_rows, cross_guard = guarded_query(
        CROSS, pages,
        "page,locus,all_three_present,all_present_exact,zl3b_clean,it2a_clean,rf1b_clean",
    )
    line_rows, line_guard = guarded_query(
        LINES, pages,
        "page,locus,line_number,paragraph_start,paragraph_end,token_count,eva_clean",
    )
    by_line: defaultdict[str, list[dict[str, str]]] = defaultdict(list)
    for row in tokens:
        by_line[row["locus"]].append(row)
    for rows in by_line.values():
        rows.sort(key=lambda row: int(row["token_index"]))
    cross_by_locus = one_by(cross_rows, "locus")
    line_by_locus = one_by(line_rows, "locus")
    if set(by_line) - set(cross_by_locus) or set(by_line) - set(line_by_locus):
        raise AssertionError("cross-reader or line metadata missing")
    ordinals: Counter[tuple[str, str]] = Counter()
    exact: dict[tuple[str, int], int] = {}
    for row in sorted(
        tokens,
        key=lambda item: (
            page_sort_key(item["page"]), line_number(item["locus"]),
            int(item["token_index"]),
        ),
    ):
        locus, surface = row["locus"], row["eva"]
        ordinals[locus, surface] += 1
        cross = cross_by_locus[locus]
        capacities = [
            cross[field].split().count(surface)
            for field in ("zl3b_clean", "it2a_clean", "rf1b_clean")
        ]
        exact[(locus, int(row["token_index"]))] = int(
            ordinals[locus, surface] <= min(capacities)
        )
    compact_rows = read_tsv(COMPACT)
    if (
        len(compact_rows) != 32339
        or len({row["page"] for row in compact_rows}) != 179
        or any(row["page"].startswith("f84") for row in compact_rows)
    ):
        raise AssertionError("compact cache shape or boundary changed")
    cells = {
        (row["locus"], int(row["token_ordinal"])): row
        for row in compact_rows
    }
    if len(cells) != len(compact_rows):
        raise AssertionError("compact cache has duplicate coordinates")
    guard: dict[str, object] = {
        "allowed_pages": len(pages),
        "tokens": token_guard,
        "cross": cross_guard,
        "lines": line_guard,
    }
    return dict(by_line), exact, cross_by_locus, line_by_locus, cells, guard


def load_axis_patterns() -> dict[str, re.Pattern[str]]:
    rows = read_tsv(AXIS_SPECS)
    if tuple(row["axis_id"] for row in rows) != EXPECTED_AXIS_SPEC_ORDER:
        raise AssertionError("axis spec order changed")
    return {
        row["axis_id"]: re.compile(
            row["keyword_regex"].replace("\\\\", "\\"), re.I
        )
        for row in rows
    }


def semantic_axes(
    text: str, patterns: Mapping[str, re.Pattern[str]]
) -> set[str]:
    tags = {axis for axis, pattern in patterns.items() if pattern.search(text)}
    if re.search(r"koch|ausgekoch", text, re.I):
        tags.add("HOT")
    tags.update(
        axis for axis, pattern in STAGE_PATTERNS.items() if pattern.search(text)
    )
    return tags


def build_clean_pool() -> tuple[
    dict[str, dict[str, object]], dict[str, int], dict[str, re.Pattern[str]]
]:
    patterns = load_axis_patterns()
    dictionary = read_tsv(DICTIONARY)
    grouped: defaultdict[str, list[dict[str, str]]] = defaultdict(list)
    for row in dictionary:
        meaning = row["working_meaning_de"]
        if not row["working_model_level"].startswith(("W2", "W3")):
            continue
        if row["gdt734_composition_semantic_credit"] != "0":
            continue
        if row["gdt734_component_export_allowed"] != "0":
            continue
        if row["gdt734_renderer_decision"] == "HOLD_UNCHANGED":
            continue
        if any(word in meaning.lower() for word in RETIRED_LITERAL_PATIENTS):
            continue
        if not semantic_axes(meaning, patterns):
            continue
        grouped[row["surface"]].append(row)
    pool: dict[str, dict[str, object]] = {}
    for surface, source_rows in grouped.items():
        reading_axes = [
            semantic_axes(row["working_meaning_de"], patterns)
            for row in source_rows
        ]
        core = set.intersection(*reading_axes)
        if not core:
            continue
        ranked = sorted(
            source_rows,
            key=lambda row: (
                -int(row["working_model_level"].startswith("W3")),
                -int(row["working_model_score_0_100_not_probability"]),
                row["reading_id"],
            ),
        )
        glosses = list(dict.fromkeys(
            row["working_meaning_de"] for row in ranked
        ))
        pool[surface] = {
            "core_axes": core,
            "union_axes": set.union(*reading_axes),
            "reading_ids": "|".join(row["reading_id"] for row in ranked),
            "levels": "|".join(sorted({
                row["working_model_level"] for row in source_rows
            })),
            "best_gloss": glosses[0],
            "all_glosses": " || ".join(glosses),
        }
    diagnostics = {
        "dictionary_rows": len(dictionary),
        "clean_axis_reading_rows": sum(len(rows) for rows in grouped.values()),
        "clean_axis_whole_pool": len(pool),
    }
    if diagnostics != {
        "dictionary_rows": 1606,
        "clean_axis_reading_rows": 770,
        "clean_axis_whole_pool": 769,
    }:
        raise AssertionError(f"clean pool changed: {diagnostics}")
    return pool, diagnostics, patterns


def reconstruct_occurrences(
    by_line: Mapping[str, list[dict[str, str]]],
    exact: Mapping[tuple[str, int], int],
    cross_by_locus: Mapping[str, Mapping[str, str]],
    line_by_locus: Mapping[str, Mapping[str, str]],
) -> tuple[list[dict[str, object]], list[dict[str, object]]]:
    selected = [
        row for row in read_tsv(G781_SELECTED)
        if row["right_surface"] in TARGETS
    ]
    selected_by_key = {
        (row["locus"], int(row["right_ordinal"]), row["right_surface"]): row
        for row in selected
    }
    if {
        key: row["span_id"] for key, row in selected_by_key.items()
    } != EXPECTED_TARGETS:
        raise AssertionError("six selected GDT781 target positions changed")
    rows: list[dict[str, object]] = []
    for locus, line in by_line.items():
        surface_rank: Counter[str] = Counter()
        for ordinal, token in enumerate(line, 1):
            surface = token["eva"]
            surface_rank[surface] += 1
            if surface not in TARGETS:
                continue
            cross = cross_by_locus[locus]
            key = (locus, ordinal, surface)
            is_exact = exact[(locus, int(token["token_index"]))]
            target = selected_by_key.get(key)
            occurrence_class = (
                "TARGET_MASKED" if target is not None
                else "EXTERNAL" if is_exact
                else "READER_NONEXACT"
            )
            rows.append({
                "occurrence_id": "",
                "surface": surface,
                "occurrence_class": occurrence_class,
                "gdt781_span_id": target["span_id"] if target else "NONE",
                "page": token["page"],
                "physical_folio": physical_folio(token["page"]),
                "locus": locus,
                "line_number": line_by_locus[locus]["line_number"],
                "section": token["section"],
                "language": token["language"],
                "hand": token["hand"],
                "target_ordinal": ordinal,
                "token_index": token["token_index"],
                "line_token_count": len(line),
                "line_position": line_position(ordinal, len(line)),
                "surface_rank_in_zl3b_line": surface_rank[surface],
                "zl3b_surface_count": cross["zl3b_clean"].split().count(surface),
                "it2a_surface_count": cross["it2a_clean"].split().count(surface),
                "rf1b_surface_count": cross["rf1b_clean"].split().count(surface),
                "all_three_present": cross["all_three_present"],
                "all_present_exact_line": cross["all_present_exact"],
                "zl3b_line": cross["zl3b_clean"],
                "it2a_line": cross["it2a_clean"],
                "rf1b_line": cross["rf1b_clean"],
                "written_line_eva": " ".join(item["eva"] for item in line),
                "reader_exact": is_exact,
                "reader_exact_method": (
                    "GDT634_OCCURRENCE_RANK_LE_MIN_"
                    "ZL3B_IT2A_RF1B_SURFACE_COUNTS"
                ),
                "target_mask_applied": int(occurrence_class == "TARGET_MASKED"),
                "selector_credit": 0,
                "component_export_credit": 0,
            })
    rows.sort(key=lambda row: (
        page_sort_key(str(row["page"])),
        line_number(str(row["locus"])),
        int(row["target_ordinal"]),
    ))
    for number, row in enumerate(rows, 1):
        row["occurrence_id"] = f"G782-O{number:03d}"
    if len(rows) != 20 or Counter(row["surface"] for row in rows) != EXPECTED_RAW:
        raise AssertionError("raw six-form occurrence census changed")
    exact_rows = [row for row in rows if int(row["reader_exact"])]
    if (
        len(exact_rows) != 14
        or Counter(row["surface"] for row in exact_rows) != EXPECTED_EXACT
        or Counter(
            row["surface"] for row in exact_rows
            if row["occurrence_class"] == "EXTERNAL"
        ) != EXPECTED_EXTERNAL
        or Counter(row["occurrence_class"] for row in rows)
        != Counter({"EXTERNAL": 8, "TARGET_MASKED": 6, "READER_NONEXACT": 6})
    ):
        raise AssertionError("exact target/external split changed")
    if not all(
        int(row["surface_rank_in_zl3b_line"]) == 1
        and int(row["zl3b_surface_count"]) == 1
        and int(row["it2a_surface_count"]) == 1
        and int(row["rf1b_surface_count"]) == 1
        for row in exact_rows
    ):
        raise AssertionError("reader-exact surface-rank signature changed")
    return rows, exact_rows


def construction_maps() -> tuple[
    list[dict[str, str]],
    dict[tuple[str, int], list[dict[str, str]]],
]:
    rows = read_tsv(G759_CONSTRUCTIONS)
    members: defaultdict[
        tuple[str, int], list[dict[str, str]]
    ] = defaultdict(list)
    for row in rows:
        for field in ("left_token_ordinal", "right_token_ordinal"):
            key = (row["locus"], int(row[field]))
            members[key].append(row)
    return rows, dict(members)


def classify_neighbor(
    surface: str,
    is_exact: int,
    cell: Mapping[str, str],
    clean: Mapping[str, object] | None,
    construction: Mapping[str, str] | None,
    later_provenance: Mapping[str, str] | None,
) -> tuple[str, int, int]:
    semantic = cell["v99r7_semantic_value_de"]
    retired = int(any(
        word in semantic.lower() for word in RETIRED_LITERAL_PATIENTS
    ))
    source_composed = int(cell["gdt734_composition_semantic_credit"] != "0")
    if surface in TARGETS:
        return "COHORT_TARGET_MASKED", retired, source_composed
    if not is_exact:
        return "NONEXACT_VISIBLE_ONLY", retired, source_composed
    if (
        later_provenance is not None
        and later_provenance["source_literal_prose_spoken_after_gdt754"] == "0"
    ):
        return "SANITIZED_GDT754_WHOLE_HYPOTHESIS", retired, 1
    if clean is not None:
        return "CLEAN_W2W3_COMPLETE_WHOLE", retired, source_composed
    if construction is not None:
        return "LICENSED_EXACT_CONSTRUCTION_MEMBER", retired, source_composed
    if retired:
        return "QUARANTINED_RETIRED_LITERAL", retired, source_composed
    if source_composed:
        return "SOURCE_COMPOSED_UNCLEAN", retired, source_composed
    if cell["unknown_v99r7"] == "1" or semantic.startswith("["):
        return "OPEN_EXACT", retired, source_composed
    return "LOWER_GRADE_WHOLE_HYPOTHESIS", retired, source_composed


def build_external_neighbors(
    exact_occurrences: Sequence[Mapping[str, object]],
    by_line: Mapping[str, list[dict[str, str]]],
    exact: Mapping[tuple[str, int], int],
    cells: Mapping[tuple[str, int], Mapping[str, str]],
    pool: Mapping[str, Mapping[str, object]],
) -> tuple[
    list[dict[str, object]],
    dict[str, dict[str, object]],
    list[dict[str, object]],
]:
    external = [
        dict(row) for row in exact_occurrences
        if row["occurrence_class"] == "EXTERNAL"
    ]
    external.sort(key=lambda row: (
        page_sort_key(str(row["page"])),
        line_number(str(row["locus"])),
        int(row["target_ordinal"]),
    ))
    for number, row in enumerate(external, 1):
        row["external_id"] = f"G782-X{number:03d}"
    analogy = read_tsv(G781_ANALOGY)
    same_sources: defaultdict[str, set[str]] = defaultdict(set)
    for row in analogy:
        if row["candidate_surface"] in TARGETS:
            same_sources[row["candidate_surface"]].add(
                row["known_neighbor_surface"]
            )
    _, construction_members = construction_maps()
    later_provenance_by_surface = one_by(
        read_tsv(G754_PROVENANCE), "surface"
    )
    later_display_by_surface = one_by(read_tsv(G768_WORKING), "surface")
    neighbor_rows: list[dict[str, object]] = []
    for target in external:
        locus = str(target["locus"])
        target_ordinal = int(target["target_ordinal"])
        line = by_line[locus]
        for neighbor_ordinal, token in enumerate(line, 1):
            if neighbor_ordinal == target_ordinal:
                continue
            offset = neighbor_ordinal - target_ordinal
            surface = token["eva"]
            is_exact = exact[(locus, int(token["token_index"]))]
            cell = cells[(locus, neighbor_ordinal)]
            clean = pool.get(surface) if is_exact else None
            construction_candidates = construction_members.get(
                (locus, neighbor_ordinal), []
            )
            construction = construction_candidates[0] if construction_candidates else None
            later_provenance = later_provenance_by_surface.get(surface)
            later_display = later_display_by_surface.get(surface)
            klass, retired, source_composed = classify_neighbor(
                surface, is_exact, cell, clean, construction, later_provenance,
            )
            other_targets = sorted(
                candidate for candidate in TARGETS
                if candidate != target["surface"]
                and surface in same_sources[candidate]
            )
            neighbor_rows.append({
                "external_id": target["external_id"],
                "surface": target["surface"],
                "page": target["page"],
                "physical_folio": target["physical_folio"],
                "locus": locus,
                "target_ordinal": target_ordinal,
                "offset": offset,
                "absolute_distance": abs(offset),
                "neighbor_ordinal": neighbor_ordinal,
                "neighbor_surface": surface,
                "neighbor_reader_exact": is_exact,
                "neighbor_class": klass,
                "clean_pool_reading_ids": (
                    clean["reading_ids"] if clean else "NONE"
                ),
                "clean_pool_level": clean["levels"] if clean else "NONE",
                "clean_pool_default_de": (
                    "BLOCKED_BY_GDT754"
                    if klass == "SANITIZED_GDT754_WHOLE_HYPOTHESIS"
                    else later_display["concrete_default_de"]
                    if clean and later_display
                    else clean["best_gloss"] if clean else "NONE"
                ),
                "clean_pool_axes": (
                    "NONE"
                    if klass == "SANITIZED_GDT754_WHOLE_HYPOTHESIS"
                    else joined(clean["core_axes"]) if clean else "NONE"
                ),
                "gdt754_provenance_present": int(later_provenance is not None),
                "gdt754_renderer_disposition": (
                    later_provenance["renderer_disposition"]
                    if later_provenance else "NONE"
                ),
                "gdt754_sanitized_default_de": (
                    later_provenance["current_working_whole_default_de"]
                    if later_provenance else "NONE"
                ),
                "gdt754_sanitized_axes": (
                    later_provenance["later_role_axes_selected"]
                    if later_provenance else "NONE"
                ),
                "gdt754_source_literal_prose_spoken": (
                    later_provenance["source_literal_prose_spoken_after_gdt754"]
                    if later_provenance else "NONE"
                ),
                "later_display_source": (
                    "GDT768_WORKING_DICTIONARY" if later_display else "NONE"
                ),
                "later_display_override_de": (
                    later_display["concrete_default_de"]
                    if later_display else "NONE"
                ),
                "registered_construction_id": (
                    construction["construction_span_id"]
                    if construction else "NONE"
                ),
                "registered_construction_eva": (
                    construction["exact_span_eva"] if construction else "NONE"
                ),
                "registered_construction_de": (
                    construction["primary_render_de"] if construction else "NONE"
                ),
                "legacy_cell_value_de": cell["v99r7_semantic_value_de"],
                "retired_literal_visible": retired,
                "source_composed_visible": source_composed,
                "same_target_analogy_source": int(
                    surface in same_sources[str(target["surface"])]
                ),
                "other_cohort_target_analogy_source": (
                    "|".join(other_targets) or "NONE"
                ),
                "target_surface_leakage": int(surface in TARGETS),
                "within_radius_3": int(abs(offset) <= 3),
                "selector_credit": 0,
                "default_is_translation": 0,
                "component_export_credit": 0,
            })
    if len(neighbor_rows) != 65:
        raise AssertionError(
            f"expected 65 external neighbor rows: {len(neighbor_rows)}"
        )
    if any(
        int(row["target_surface_leakage"]) and int(row["within_radius_3"])
        for row in neighbor_rows
    ):
        raise AssertionError("another cohort target leaked inside radius three")
    external_by_id = {
        str(row["external_id"]): row for row in external
    }
    return neighbor_rows, external_by_id, external


def compact_neighbor(row: Mapping[str, object]) -> str:
    if row["neighbor_class"] == "CLEAN_W2W3_COMPLETE_WHOLE":
        return f"{row['neighbor_surface']}={row['clean_pool_axes']}"
    if row["neighbor_class"] == "NONEXACT_VISIBLE_ONLY":
        return f"{row['neighbor_surface']}=NONEXACT"
    if row["neighbor_class"] == "QUARANTINED_RETIRED_LITERAL":
        return f"{row['neighbor_surface']}=RETIRED_LITERAL"
    if row["neighbor_class"] == "COHORT_TARGET_MASKED":
        return f"{row['neighbor_surface']}=TARGET_MASKED"
    if row["neighbor_class"] == "SANITIZED_GDT754_WHOLE_HYPOTHESIS":
        return (
            f"{row['neighbor_surface']}=SANITIZED:"
            f"{row['gdt754_sanitized_axes']}"
        )
    return f"{row['neighbor_surface']}={row['neighbor_class']}"


def build_field_summaries(
    external: Sequence[Mapping[str, object]],
    neighbors: Sequence[Mapping[str, object]],
    final_specs: Mapping[str, Mapping[str, str]],
) -> tuple[list[dict[str, object]], list[dict[str, object]]]:
    by_external: defaultdict[str, list[Mapping[str, object]]] = defaultdict(list)
    for row in neighbors:
        by_external[str(row["external_id"])].append(row)
    all_constructions = read_tsv(G759_CONSTRUCTIONS)
    contacts: list[dict[str, object]] = []
    summaries: list[dict[str, object]] = []
    for target in external:
        external_id = str(target["external_id"])
        rows = by_external[external_id]
        target_ordinal = int(target["target_ordinal"])
        immediate_left = next(
            (row for row in rows if int(row["offset"]) == -1), None
        )
        immediate_right = next(
            (row for row in rows if int(row["offset"]) == 1), None
        )
        clean_r3 = [
            row for row in rows
            if int(row["absolute_distance"]) <= 3
            and row["neighbor_class"] == "CLEAN_W2W3_COMPLETE_WHOLE"
        ]
        axes = [
            axis for row in clean_r3
            for axis in split_axes(str(row["clean_pool_axes"]))
        ]
        direct = [
            row for row in all_constructions
            if row["locus"] == target["locus"]
            and int(row["right_token_ordinal"]) + 1 == target_ordinal
            and row["reader_exact_left"] == "1"
            and row["reader_exact_right"] == "1"
        ]
        for construction in direct:
            contacts.append({
                "contact_id": f"G782-Q{len(contacts) + 1:03d}",
                "external_id": external_id,
                "surface": target["surface"],
                "page": target["page"],
                "physical_folio": target["physical_folio"],
                "locus": target["locus"],
                "target_ordinal": target_ordinal,
                "construction_span_id": construction["construction_span_id"],
                "construction_ordinal_start": construction["left_token_ordinal"],
                "construction_ordinal_end": construction["right_token_ordinal"],
                "construction_eva": construction["exact_span_eva"],
                "construction_default_de": construction["primary_render_de"],
                "construction_alternate_1_de": construction["alternate_1_de"],
                "construction_alternate_2_de": construction["alternate_2_de"],
                "construction_confidence": construction["working_confidence"],
                "exact_pair_global_count": construction["exact_pair_global_count"],
                "fused_counterpart_reader_exact_occurrences": (
                    construction["fused_counterpart_reader_exact_occurrences"]
                ),
                "target_immediately_follows": 1,
                "target_amount_role_redundancy_risk": 1,
                "target_content_complement_lead": 1,
                "scope": (
                    "EXACT_REGISTERED_CONSTRUCTION_PLUS_"
                    "ADJACENT_TARGET_ONLY"
                ),
                "confirmed_plaintext": 0,
                "component_export_credit": 0,
            })
        spec = final_specs[str(target["surface"])]
        summaries.append({
            "external_id": external_id,
            "surface": target["surface"],
            "page": target["page"],
            "physical_folio": target["physical_folio"],
            "locus": target["locus"],
            "target_ordinal": target_ordinal,
            "line_token_count": target["line_token_count"],
            "line_position": target["line_position"],
            "immediate_left": (
                compact_neighbor(immediate_left) if immediate_left
                else "LINE_EDGE"
            ),
            "immediate_right": (
                compact_neighbor(immediate_right) if immediate_right
                else "LINE_EDGE"
            ),
            "radius3_clean_donors": len(clean_r3),
            "radius3_clean_surfaces": (
                "|".join(str(row["neighbor_surface"]) for row in clean_r3)
                or "NONE"
            ),
            "radius3_clean_axis_union": joined(axes),
            "radius3_clean_axis_contacts": count_string(axes),
            "registered_exact_construction": (
                "|".join(row["exact_span_eva"] for row in direct) or "NONE"
            ),
            "registered_exact_construction_de": (
                " || ".join(row["primary_render_de"] for row in direct)
                or "NONE"
            ),
            "strict_target_surface_leakage": sum(
                int(row["target_surface_leakage"])
                for row in rows if int(row["absolute_distance"]) <= 3
            ),
            "cohort_analogy_source_leakage": sum(
                int(row["other_cohort_target_analogy_source"] != "NONE")
                for row in rows if int(row["absolute_distance"]) <= 3
            ),
            "nonexact_visible_radius3": sum(
                int(row["neighbor_class"] == "NONEXACT_VISIBLE_ONLY")
                for row in rows if int(row["absolute_distance"]) <= 3
            ),
            "retired_literal_visible_line": sum(
                int(row["retired_literal_visible"]) for row in rows
            ),
            "working_default_before": spec["gdt781_default_de"],
            "working_default_after": spec["gdt782_default_de"],
            "decision": spec["decision"],
            "confidence": spec["confidence"],
            "written_line_eva": target["written_line_eva"],
            "target_masked_during_field_read": 1,
            "default_is_translation": 0,
            "component_export_credit": 0,
        })
    if len(summaries) != 8 or len(contacts) != 1:
        raise AssertionError(
            "external summary or construction contact count changed"
        )
    if contacts[0]["construction_eva"] != "or aiin":
        raise AssertionError("expected exact or aiin contact")
    return summaries, contacts


def axis_field_weights(
    neighbors: Sequence[Mapping[str, object]],
    exclude_cross_cohort_sources: bool = False,
) -> dict[str, Counter[str]]:
    by_external: defaultdict[str, list[Mapping[str, object]]] = defaultdict(list)
    surface_by_external: dict[str, str] = {}
    for row in neighbors:
        external_id = str(row["external_id"])
        by_external[external_id].append(row)
        surface_by_external[external_id] = str(row["surface"])
    output: defaultdict[str, Counter[str]] = defaultdict(Counter)
    for external_id, rows in by_external.items():
        best: dict[str, int] = {}
        for row in rows:
            if row["neighbor_class"] != "CLEAN_W2W3_COMPLETE_WHOLE":
                continue
            distance = int(row["absolute_distance"])
            if distance > 3:
                continue
            if (
                exclude_cross_cohort_sources
                and row["other_cohort_target_analogy_source"] != "NONE"
            ):
                continue
            weight = 4 - distance
            for axis in split_axes(str(row["clean_pool_axes"])):
                best[axis] = max(best.get(axis, 0), weight)
        output[surface_by_external[external_id]].update(best)
    return dict(output)


def opposition_weight(
    candidate_axes: set[str], field_weights: Mapping[str, int]
) -> float:
    total = 0.0
    comparisons = 0
    for members in DIMENSIONS.values():
        asserted = candidate_axes & set(members)
        if not asserted:
            continue
        comparisons += 1
        total += sum(
            field_weights.get(axis, 0)
            for axis in members if axis not in asserted
        )
    return total / comparisons if comparisons else 0.0


def build_scorecards(
    candidates: Sequence[Mapping[str, str]],
    external: Sequence[Mapping[str, object]],
    neighbors: Sequence[Mapping[str, object]],
    contacts: Sequence[Mapping[str, object]],
    final_specs: Mapping[str, Mapping[str, str]],
) -> list[dict[str, object]]:
    weights = axis_field_weights(neighbors)
    sensitivity = axis_field_weights(
        neighbors, exclude_cross_cohort_sources=True
    )
    by_surface_external: defaultdict[
        str, list[Mapping[str, object]]
    ] = defaultdict(list)
    for row in external:
        by_surface_external[str(row["surface"])].append(row)
    immediate_amount_surfaces = {
        str(row["surface"]) for row in contacts
    }
    neighbor_by_external: defaultdict[
        str, list[Mapping[str, object]]
    ] = defaultdict(list)
    for row in neighbors:
        neighbor_by_external[str(row["external_id"])].append(row)
    rows: list[dict[str, object]] = []
    for candidate in candidates:
        surface = candidate["surface"]
        axes = split_axes(candidate["candidate_axes"])
        field = weights.get(surface, Counter())
        field_sensitivity = sensitivity.get(surface, Counter())
        axis_support = sum(field.get(axis, 0) for axis in axes)
        axis_support_sensitivity = sum(
            field_sensitivity.get(axis, 0) for axis in axes
        )
        support_mean = axis_support / len(axes) if axes else 0.0
        opposition = opposition_weight(axes, field)
        redundancy_penalty = 0.0
        complement_bonus = 0.0
        endpoint_bonus = 0.0
        patient_slot_bonus = 0.0
        if surface in immediate_amount_surfaces:
            if axes & {"AMOUNT", "PART"}:
                redundancy_penalty += 3.0
            if axes & {"MATERIAL", "PREPARATION"}:
                complement_bonus += 2.0
        for target in by_surface_external[surface]:
            external_rows = neighbor_by_external[str(target["external_id"])]
            left = next(
                (row for row in external_rows if int(row["offset"]) == -1),
                None,
            )
            right = next(
                (row for row in external_rows if int(row["offset"]) == 1),
                None,
            )
            if left and surface not in immediate_amount_surfaces:
                left_axes = split_axes(str(left["clean_pool_axes"]))
                if left_axes & {"AMOUNT", "PART"}:
                    if axes & {"AMOUNT", "PART"}:
                        redundancy_penalty += 1.0
                    if axes & {"MATERIAL", "PREPARATION"}:
                        complement_bonus += 1.0
            if right and "PROCESS" in split_axes(
                str(right["clean_pool_axes"])
            ):
                if axes & {"MATERIAL", "PREPARATION"}:
                    patient_slot_bonus += 2.0
            if target["line_position"] == "LAST" and "END_STAGE" in axes:
                endpoint_bonus += 2.0
            if (
                any(
                    int(row["offset"]) == -1
                    and "CLOSE" in split_axes(str(row["clean_pool_axes"]))
                    for row in external_rows
                )
                and "END_STAGE" in axes
            ):
                endpoint_bonus += 1.0
        score = (
            support_mean - opposition - redundancy_penalty
            + complement_bonus + endpoint_bonus + patient_slot_bonus
        )
        rows.append({
            "surface": surface,
            "candidate_id": candidate["candidate_id"],
            "candidate_de": candidate["candidate_de"],
            "candidate_axes": candidate["candidate_axes"],
            "candidate_origin": candidate["candidate_origin"],
            "external_occurrences": len(by_surface_external[surface]),
            "field_axis_weights": "|".join(
                f"{axis}:{field[axis]}" for axis in AXIS_ORDER if field[axis]
            ) or "NONE",
            "candidate_axis_support_total": axis_support,
            "candidate_axis_support_mean": f"{support_mean:.3f}",
            "opposition_mean": f"{opposition:.3f}",
            "amount_redundancy_penalty": f"{redundancy_penalty:.3f}",
            "content_complement_bonus": f"{complement_bonus:.3f}",
            "endpoint_bonus": f"{endpoint_bonus:.3f}",
            "patient_before_process_bonus": f"{patient_slot_bonus:.3f}",
            "exploratory_field_score": f"{score:.3f}",
            "cross_cohort_source_removed_support_total": (
                axis_support_sensitivity
            ),
            "selected_final": int(
                candidate["candidate_id"]
                == final_specs[surface]["selected_candidate_id"]
            ),
            "score_is_lexical_probability": 0,
            "default_is_translation": 0,
            "component_export_credit": 0,
        })
    if len(rows) != 23:
        raise AssertionError(f"expected 23 candidate rows, got {len(rows)}")
    by_surface: defaultdict[str, list[dict[str, object]]] = defaultdict(list)
    for row in rows:
        by_surface[str(row["surface"])].append(row)
    for surface, group in by_surface.items():
        ordered = sorted(
            group,
            key=lambda row: (
                -float(row["exploratory_field_score"]),
                str(row["candidate_id"]),
            ),
        )
        for rank, row in enumerate(ordered, 1):
            row["field_score_rank"] = rank
        if sum(int(row["selected_final"]) for row in group) != 1:
            raise AssertionError(f"one final candidate required: {surface}")
    return sorted(rows, key=lambda row: (
        TARGET_ORDER.index(str(row["surface"])),
        str(row["candidate_id"]),
    ))


def build_manual_artifact(
    manual: Sequence[Mapping[str, str]],
) -> list[dict[str, object]]:
    if len(manual) != 18:
        raise AssertionError("expected 18 manual assessments")
    if Counter(row["reader_id"] for row in manual) != Counter({
        "FIELD_GRAMMAR_READER": 6,
        "APOTHECARY_READER": 6,
        "EXTERNAL_CENSUS_READER": 6,
    }):
        raise AssertionError("manual reader panel changed")
    rows: list[dict[str, object]] = []
    for number, source in enumerate(manual, 1):
        row: dict[str, object] = {"assessment_id": f"G782-M{number:03d}"}
        row.update(source)
        row["assessment_is_proof"] = 0
        row["component_export_credit"] = 0
        rows.append(row)
    return rows


def build_revisions(
    final_rows: Sequence[Mapping[str, str]],
    scorecards: Sequence[Mapping[str, object]],
    manual: Sequence[Mapping[str, object]],
    external: Sequence[Mapping[str, object]],
    summaries: Sequence[Mapping[str, object]],
) -> list[dict[str, object]]:
    score_by_key = {
        (str(row["surface"]), str(row["candidate_id"])): row
        for row in scorecards
    }
    manual_by_surface: defaultdict[
        str, list[Mapping[str, object]]
    ] = defaultdict(list)
    for row in manual:
        manual_by_surface[str(row["surface"])].append(row)
    external_by_surface: defaultdict[
        str, list[Mapping[str, object]]
    ] = defaultdict(list)
    for row in external:
        external_by_surface[str(row["surface"])].append(row)
    summary_by_surface: defaultdict[
        str, list[Mapping[str, object]]
    ] = defaultdict(list)
    for row in summaries:
        summary_by_surface[str(row["surface"])].append(row)
    revisions: list[dict[str, object]] = []
    for number, source in enumerate(final_rows, 1):
        surface = source["surface"]
        selected_score = score_by_key[
            (surface, source["selected_candidate_id"])
        ]
        readers = manual_by_surface[surface]
        votes = Counter(
            str(row["selected_candidate_id"]) for row in readers
        )
        fields = summary_by_surface[surface]
        revisions.append({
            "card_id": f"G782-C{number:03d}",
            **source,
            "external_occurrences": len(external_by_surface[surface]),
            "external_loci": "|".join(
                str(row["locus"]) for row in external_by_surface[surface]
            ),
            "external_clean_axis_locus_votes": count_string(
                axis
                for row in fields
                for axis in split_axes(
                    str(row["radius3_clean_axis_union"])
                )
            ),
            "registered_construction_contacts": sum(
                int(row["registered_exact_construction"] != "NONE")
                for row in fields
            ),
            "reader_candidate_votes": "|".join(
                f"{key}:{votes[key]}" for key in sorted(votes)
            ),
            "selected_field_score": (
                selected_score["exploratory_field_score"]
            ),
            "selected_field_score_rank": (
                selected_score["field_score_rank"]
            ),
            "field_score_is_decision_rule": 0,
            "target_occurrences_masked": 1,
            "substring_used": 0,
        })
    if len(revisions) != 6:
        raise AssertionError("expected six final revisions")
    if Counter(row["decision"] for row in revisions) != Counter({
        "REVISE": 5, "KEEP": 1,
    }):
        raise AssertionError("expected five revisions and one keep")
    return revisions


def build_renderer(
    parent: Sequence[Mapping[str, str]],
    revisions: Sequence[Mapping[str, object]],
) -> tuple[list[dict[str, object]], set[str]]:
    revision_by_surface = {
        str(row["surface"]): row for row in revisions
    }
    rows: list[dict[str, object]] = []
    owners: set[str] = set()
    selected_count = 0
    for source in parent:
        row: dict[str, object] = dict(source)
        is_target = (
            source["right_surface"] in TARGETS
            and source["gdt781_span_id"] != "NONE"
        )
        if is_target:
            selected_count += 1
            revision = revision_by_surface[source["right_surface"]]
            row.update({
                "gdt782_default_de": revision["gdt782_default_de"],
                "gdt782_renderer_contextual": (
                    source["gdt781_renderer_contextual"]
                ),
                "gdt782_card_id": revision["card_id"],
                "gdt782_decision": revision["decision"],
                "gdt782_confidence": revision["confidence"],
                "gdt782_functional_axes": revision["gdt782_axes"],
                "gdt782_external_occurrences": (
                    revision["external_occurrences"]
                ),
                "gdt782_consumed_token_count": (
                    source["gdt781_consumed_token_count"]
                ),
                "gdt782_consumed_token_ids": (
                    source["gdt781_consumed_token_ids"]
                ),
                "gdt782_display_changed": int(
                    source["gdt781_default_de"]
                    != revision["gdt782_default_de"]
                ),
                "gdt782_default_is_translation": 0,
                "gdt782_confirmed_lexeme": 0,
                "gdt782_confirmed_plaintext": 0,
                "gdt782_component_export_credit": 0,
            })
        else:
            row.update({
                "gdt782_default_de": source["gdt781_default_de"],
                "gdt782_renderer_contextual": (
                    source["gdt781_renderer_contextual"]
                ),
                "gdt782_card_id": "NONE",
                "gdt782_decision": "INHERITED_GDT781",
                "gdt782_confidence": "INHERITED_GDT781",
                "gdt782_functional_axes": (
                    source["gdt781_functional_axes"]
                    if source["gdt781_functional_axes"]
                    else "INHERITED_GDT781"
                ),
                "gdt782_external_occurrences": 0,
                "gdt782_consumed_token_count": (
                    source["gdt781_consumed_token_count"]
                ),
                "gdt782_consumed_token_ids": (
                    source["gdt781_consumed_token_ids"]
                ),
                "gdt782_display_changed": 0,
                "gdt782_default_is_translation": (
                    source["gdt781_default_is_translation"]
                ),
                "gdt782_confirmed_lexeme": (
                    source["gdt781_confirmed_lexeme"]
                ),
                "gdt782_confirmed_plaintext": (
                    source["gdt781_confirmed_plaintext"]
                ),
                "gdt782_component_export_credit": (
                    source["gdt781_component_export_credit"]
                ),
            })
        token_ids = str(row["gdt782_consumed_token_ids"])
        if token_ids not in {"", "NONE"}:
            for token_id in token_ids.split("|"):
                if token_id in owners:
                    raise AssertionError(
                        f"consumption collision: {token_id}"
                    )
                owners.add(token_id)
        rows.append(row)
    if len(rows) != 376 or selected_count != 6:
        raise AssertionError("renderer size or target selection changed")
    if sum(int(row["gdt782_renderer_contextual"]) for row in rows) != 270:
        raise AssertionError("contextual count changed")
    if sum(
        1 - int(row["gdt782_renderer_contextual"]) for row in rows
    ) != 106:
        raise AssertionError("fallback count changed")
    if len(owners) != 230:
        raise AssertionError("consumption count changed")
    if sum(int(row["gdt782_display_changed"]) for row in rows) != 5:
        raise AssertionError("expected five renderer display changes")
    return rows, owners


def target_patch_line(
    written: str, ol_ordinal: int, right_ordinal: int, default: str
) -> str:
    words = written.split()
    if (
        right_ordinal != ol_ordinal + 1
        or words[ol_ordinal - 1] != "ol"
    ):
        raise AssertionError("target is no longer an ol plus whole span")
    output: list[str] = []
    for ordinal, word in enumerate(words, 1):
        if ordinal == ol_ordinal:
            output.append(f"⟦{default}⟧")
        elif ordinal == right_ordinal:
            continue
        else:
            output.append(word)
    return " ".join(output)


def build_target_patches(
    revisions: Sequence[Mapping[str, object]],
) -> list[dict[str, object]]:
    selected = {
        row["right_surface"]: row for row in read_tsv(G781_SELECTED)
        if row["right_surface"] in TARGETS
    }
    rows: list[dict[str, object]] = []
    for number, revision in enumerate(revisions, 1):
        source = selected[str(revision["surface"])]
        old_patch = target_patch_line(
            source["written_line_eva"], int(source["ol_ordinal"]),
            int(source["right_ordinal"]),
            source["new_gdt781_default_de"],
        )
        new_patch = target_patch_line(
            source["written_line_eva"], int(source["ol_ordinal"]),
            int(source["right_ordinal"]),
            str(revision["gdt782_default_de"]),
        )
        rows.append({
            "passage_patch_id": f"G782-P{number:03d}",
            "card_id": revision["card_id"],
            "gdt781_span_id": source["span_id"],
            "target_occurrence_id": source["target_occurrence_id"],
            "page": source["page"],
            "physical_folio": source["physical_folio"],
            "locus": source["locus"],
            "ol_ordinal": source["ol_ordinal"],
            "right_ordinal": source["right_ordinal"],
            "right_surface": source["right_surface"],
            "written_line_eva": source["written_line_eva"],
            "gdt781_practical_patch_de": old_patch,
            "gdt782_practical_patch_de": new_patch,
            "gdt781_default_de": source["new_gdt781_default_de"],
            "gdt782_default_de": revision["gdt782_default_de"],
            "decision": revision["decision"],
            "display_changed": int(old_patch != new_patch),
            "patch_legend": (
                "double brackets are replaceable exact-span defaults; "
                "unbracketed EVA remains unresolved"
            ),
            "default_is_translation": 0,
            "confirmed_plaintext": 0,
            "component_export_credit": 0,
        })
    if (
        len(rows) != 6
        or sum(int(row["display_changed"]) for row in rows) != 5
    ):
        raise AssertionError("target patch count changed")
    return rows


def build_external_reader(
    external: Sequence[Mapping[str, object]],
    neighbors: Sequence[Mapping[str, object]],
    revisions: Sequence[Mapping[str, object]],
    by_line: Mapping[str, list[dict[str, str]]],
) -> list[dict[str, object]]:
    revision_by_surface = {
        str(row["surface"]): row for row in revisions
    }
    neighbor_by_key = {
        (str(row["external_id"]), int(row["neighbor_ordinal"])): row
        for row in neighbors
    }
    construction_by_locus: dict[str, dict[str, str]] = {}
    for construction in read_tsv(G759_CONSTRUCTIONS):
        if any(
            construction["locus"] == target["locus"]
            and int(construction["right_token_ordinal"]) + 1
            == int(target["target_ordinal"])
            for target in external
        ):
            construction_by_locus[construction["locus"]] = construction
    rows: list[dict[str, object]] = []
    for target in external:
        external_id = str(target["external_id"])
        target_ordinal = int(target["target_ordinal"])
        line = by_line[str(target["locus"])]
        construction = construction_by_locus.get(str(target["locus"]))
        rendered: list[str] = []
        axes_rendered: list[str] = []
        skip: set[int] = set()
        for ordinal, token in enumerate(line, 1):
            if ordinal in skip:
                continue
            if (
                construction
                and ordinal == int(construction["left_token_ordinal"])
            ):
                rendered.append(
                    f"⟦Menge: {construction['primary_render_de']}⟧"
                )
                axes_rendered.append(
                    f"{construction['exact_span_eva']}{{AMOUNT}}"
                )
                skip.add(int(construction["right_token_ordinal"]))
                continue
            if ordinal == target_ordinal:
                revision = revision_by_surface[str(target["surface"])]
                target_prefix = "Stoff: " if target["surface"] == "chedor" else ""
                rendered.append(
                    f"⟦{target_prefix}{revision['gdt782_default_de']}⟧"
                )
                axes_rendered.append(
                    f"{target['surface']}{{TARGET:{revision['gdt782_axes']}}}"
                )
                continue
            neighbor = neighbor_by_key[(external_id, ordinal)]
            klass = str(neighbor["neighbor_class"])
            if klass == "CLEAN_W2W3_COMPLETE_WHOLE":
                rendered.append(
                    f"⟨{neighbor['clean_pool_default_de']}⟩"
                )
                axes_rendered.append(
                    f"{token['eva']}{{{neighbor['clean_pool_axes']}}}"
                )
            elif klass == "SANITIZED_GDT754_WHOLE_HYPOTHESIS":
                rendered.append(
                    f"⟨{neighbor['gdt754_sanitized_default_de']}; "
                    "spätere Ganzformhypothese⟩"
                )
                axes_rendered.append(
                    f"{token['eva']}{{SANITIZED_GDT754:"
                    f"{neighbor['gdt754_sanitized_axes']}}}"
                )
            elif int(neighbor["retired_literal_visible"]):
                rendered.append(
                    f"⟪{token['eva']}:Altglosse gesperrt⟫"
                )
                axes_rendered.append(
                    f"{token['eva']}{{QUARANTINED}}"
                )
            elif klass == "NONEXACT_VISIBLE_ONLY":
                rendered.append(
                    f"[{token['eva']}:Leservariante]"
                )
                axes_rendered.append(
                    f"{token['eva']}{{NONEXACT}}"
                )
            else:
                rendered.append(f"[{token['eva']}:?]")
                axes_rendered.append(f"{token['eva']}{{OPEN}}")
        rows.append({
            "external_id": external_id,
            "surface": target["surface"],
            "page": target["page"],
            "physical_folio": target["physical_folio"],
            "locus": target["locus"],
            "target_ordinal": target_ordinal,
            "written_line_eva": target["written_line_eva"],
            "working_field_render_de": " | ".join(rendered),
            "axis_field_render": " | ".join(axes_rendered),
            "target_default_de": revision_by_surface[
                str(target["surface"])
            ]["gdt782_default_de"],
            "target_decision": revision_by_surface[
                str(target["surface"])
            ]["decision"],
            "status": "AGGREGATE_CARD_AUDIT_NOT_EXTERNAL_RENDERER_LICENSE",
            "legend": (
                "double target/construction brackets; clean donor angles; "
                "sanitized later whole hypotheses marked in text; "
                "vertical bars delimit fields; open/nonexact square brackets; "
                "retired literal quarantine; no external renderer licence"
            ),
            "default_is_translation": 0,
            "confirmed_plaintext": 0,
            "component_export_credit": 0,
        })
    if len(rows) != 8:
        raise AssertionError("expected eight external reader rows")
    return rows


def make_packet(
    external: Sequence[Mapping[str, object]],
    neighbors: Sequence[Mapping[str, object]],
) -> tuple[list[dict[str, object]], list[dict[str, object]]]:
    by_external: defaultdict[
        str, list[Mapping[str, object]]
    ] = defaultdict(list)
    for row in neighbors:
        by_external[str(row["external_id"])].append(row)
    packet: list[dict[str, object]] = []
    crosswalk: list[dict[str, object]] = []
    for number, target in enumerate(external, 1):
        candidates = [
            row for row in by_external[str(target["external_id"])]
            if row["neighbor_class"] in {
                "CLEAN_W2W3_COMPLETE_WHOLE",
                "LICENSED_EXACT_CONSTRUCTION_MEMBER",
            }
        ]
        if not candidates:
            raise AssertionError(
                f"no informative field neighbor: {target['external_id']}"
            )
        pivot = min(candidates, key=lambda row: (
            int(row["absolute_distance"]),
            int(row["neighbor_ordinal"]),
        ))
        edge_id = f"G782-E{number:03d}"
        packet.append({
            "edge_id": edge_id,
            "batch_id": "GDT782_TARGET_EXTERNAL_FIELDS",
            "page": target["page"],
            "physical_folio": target["physical_folio"],
            "diagram_unit_id": f"LINE:{target['locus']}",
            "pivot_visual_id": (
                f"TOKEN:{target['locus']}:{pivot['neighbor_ordinal']}"
            ),
            "pivot_locus": (
                f"{target['locus']}@{pivot['neighbor_ordinal']}"
            ),
            "target_visual_id": (
                f"TOKEN:{target['locus']}:{target['target_ordinal']}"
            ),
            "target_locus": (
                f"{target['locus']}@{target['target_ordinal']}"
            ),
            "relation_type": "TARGET_EXTERNAL_FIELD_CONTACT",
            "direction_basis": "TRANSCRIPTION_ORDER_ONLY",
            "ownership_basis": "NONVISUAL_TEXT_FIELD_ADJACENCY",
            "geometry_only_selection": "FALSE",
            "source_manifest_id": "GDT781",
            "page_crop_sha256": "NONE",
            "pivot_crop_sha256": "NONE",
            "target_crop_sha256": "NONE",
            "source_aware_localizer": "GDT782_RUNNER",
            "relation_reviewer": "GDT782_VALIDATOR",
            "relation_confidence": "EXPLORATORY",
            "ambiguity_state": "MULTIPLE_FIELD_READINGS_RETAINED",
            "formal_access_state": (
                "SEALED_NOT_ACCESSED"
            ),
            "fold_assignment": "NONE",
            "eligibility_status": (
                "INELIGIBLE_EXPLORATORY_TEXT_RELATION"
            ),
        })
        crosswalk.append({
            "edge_id": edge_id,
            "batch_id": "GDT782_TARGET_EXTERNAL_FIELDS",
            "external_id": target["external_id"],
            "surface": target["surface"],
            "page": target["page"],
            "physical_folio": target["physical_folio"],
            "locus": target["locus"],
            "target_ordinal": target["target_ordinal"],
            "pivot_ordinal": pivot["neighbor_ordinal"],
            "pivot_surface": pivot["neighbor_surface"],
            "pivot_class": pivot["neighbor_class"],
            "pivot_axes": pivot["clean_pool_axes"],
            "target_masked": 1,
            "score_eligible": 0,
            "component_export_credit": 0,
        })
    return packet, crosswalk


def build_artifact_readme() -> str:
    return """# GDT782 artifacts

- `GDT782_20_CACHE_OCCURRENCE_ATLAS.tsv`: all six-form cache positions, including six nonexact exclusions.
- `GDT782_14_READER_EXACT_OCCURRENCE_ATLAS.tsv`: six masked GDT781 targets plus eight target-external positions.
- `GDT782_65_EXTERNAL_NEIGHBOR_ATLAS.tsv`: every non-target token on the eight external lines, with clean, soft, nonexact, GDT754-sanitized and quarantined layers.
- `GDT782_8_EXTERNAL_FIELD_SUMMARY.tsv`: one compact target-masked field record per external occurrence.
- `GDT782_REGISTERED_CONSTRUCTION_CONTACTS.tsv`: the exact `or aiin` amount field immediately before external `chedor`.
- `GDT782_23_CANDIDATE_SCORECARDS.tsv`: all old candidates and field-compatible refinements; scores are diagnostics, not lexical probabilities.
- `GDT782_18_MANUAL_READER_ASSESSMENTS.tsv`: three differently framed readings of all six forms, including disagreements.
- `GDT782_6_WORKING_REVISIONS.tsv`: five revised concrete defaults and one retained default, all with rivals and counterevidence.
- `GDT782_6_TARGET_PASSAGE_PATCHES.tsv`: exact changes to the six GDT781 target spans.
- `GDT782_8_EXTERNAL_WORKING_READER.tsv`: marked aggregate card-audit fields, not newly licensed external translations; brackets distinguish targets, clean donors, later sanitizations, unknowns and quarantines.
- `GDT782_376_RENDERER.tsv`: complete inherited renderer; coverage and consumption are unchanged.
- `GDT782_GDT388_EXTERNAL_FIELD_PACKET.tsv` and `GDT782_RELATION_EDGE_CROSSWALK.tsv`: acquisition-only text relations.
- `RELATION_PACKET_INTAKE.json`: executable edge-packet gate result.
- `RESULT.json`: compact machine-readable result.

All meanings are replaceable complete-whole working defaults. No row exports an EVA component or claims plaintext.
"""


def build_report(
    result: Mapping[str, object],
    revisions: Sequence[Mapping[str, object]],
    summaries: Sequence[Mapping[str, object]],
    patches: Sequence[Mapping[str, object]],
    external_reader: Sequence[Mapping[str, object]],
) -> str:
    revision_lines = "\n".join(
        "| `{surface}` | {before} | **{after}** | {decision} | "
        "{confidence} | {evidence} |".format(
            surface=row["surface"],
            before=row["gdt781_default_de"],
            after=row["gdt782_default_de"],
            decision=row["decision"],
            confidence=row["confidence"],
            evidence=row["reader_consensus"].replace("_", "\\_"),
        )
        for row in revisions
    )
    field_lines = "\n".join(
        "| `{surface}` | `{locus}` | {left} | {right} | "
        "`{axes}` | {construction} |".format(
            surface=row["surface"],
            locus=row["locus"],
            left=row["immediate_left"],
            right=row["immediate_right"],
            axes=row["radius3_clean_axis_union"],
            construction=row["registered_exact_construction_de"],
        )
        for row in summaries
    )
    phrase = next(
        row for row in external_reader if row["locus"] == "f105v.26"
    )
    changed = [row for row in patches if int(row["display_changed"])]
    return f"""# GDT782 — recurrent-six target-external field adjudication

Status: `{result['status']}`

## Result

The six recurrent GDT781 forms reconstruct as 20 cached positions: 14 are
reader-exact, comprising six masked GDT781 targets and eight external fields;
six are reader-nonexact and never vote. The external fields revise five
working cards and retain one. No form is erased into a generic action phrase.

| whole | GDT781 default | GDT782 default | action | confidence | reader outcome |
|---|---|---|---|---|---|
{revision_lines}

The most useful repair is syntactic rather than cosmetic. At `f105v.26`,
`or aiin` is already the registered exact working construction “drei
Portionen”. Keeping `chedor=trockene Stoffportion` would produce “drei
Portionen trockene Stoffportion”. GDT782 therefore makes the following
replaceable field reading:

> {phrase['working_field_render_de']}

This marked line is not plaintext: double brackets are working targets or
registered constructions, angle brackets are clean complete-whole donor
cards, vertical bars delimit record fields, and unresolved or quarantined
material remains visibly marked. The eight lines adjudicate aggregate cards;
they do not license the target defaults at those external positions.

## Eight target-external fields

| target | locus | immediate left | immediate right | clean axes within R3 | exact construction |
|---|---|---|---|---|---|
{field_lines}

The three `cheedaiin` fields leave MIDDLE and END tied 2:2; the line-final
DRY/AMOUNT/END field and the earlier GDT748 external END series provide only
the manual tiebreak toward `Trockenmenge, Endstufe`. `keeor` sits in one dense
dry/material field, which supports a DRY/MATERIAL display without directly
excluding the orthogonal HOT axis. `sheckhal` has one clean R2 dry/material
donor that does oppose its old MOIST direction. In both cases, transferring
DRY into the target remains an explicitly aggressive C0/C1 working choice. `chockhar`
has only one outside occurrence, so its
`erhitzter Ansatz` revision remains C0 despite the useful HOT/II plus portion
frame. `shdair` stays the narrower `Arzneistoff`: one reader preferred
`feuchte Stoffportion`, but the moisture/process material follows the target
and need not be lexical content of the target itself.

## Deliberately preserved disagreement

Three readings were retained: a field-grammar reader, a historical apothecary
reader, and a surface-first census reader. They agree on the directional
revision for four cards. The census reader would retain a portion in
`chedor`, while the other two remove it to avoid doubling the adjacent amount
construction. It would also move `shdair` to a moist portion; the other two
keep the narrower material head because the moist/process field is
post-target. The dissent remains in the public assessment table.

## Renderer impact

The six target spans remain the same six exact, already consumed GDT781
spans. Five displayed defaults change and one is confirmed. Therefore the
full renderer remains 270/376 contextual, 106 fallback and 230 uniquely
consumed right tokens. No unrelated row changes its inherited value,
precedence or consumption.

## Leakage and evidence hygiene

Every target token was removed before its field was read. No other cohort
target occurs within radius three. Within that scored radius, one field
contains `cheeor`, an old clean whole that was also an analogy source for the
different cohort target `chedor`; it was never an analogy source for
`cheedaiin`, and the scorecard publishes a sensitivity with that cross-cohort
donor removed. A second cross-cohort source, `cheor`, is visible only at
distance four on the `sheckhal` line and contributes no field vote. Nonexact rows,
source-composed cards and literal powder/seed/root/wood remnants are visible
but cannot vote as clean donors. In particular, the distant `okeol` context is
shown only with GDT754's later `Wärme-/Mittelstufenfeld; genaue Funktion und
Träger offen` whole-form hypothesis. Its obsolete source-built “Grundansatz …
erwärmt” prose is retained only in the provenance column and contributes no
field vote.

The reader also takes the later GDT768 whole-form display for `cthy` as
`Blattgut`; it does not revive the older `CTH-Drogenmaterial` wording.

The clean pool reconstructs {result['clean_pool']['clean_axis_reading_rows']}
readings over {result['clean_pool']['clean_axis_whole_pool']} complete
surfaces. Historical pharmacy evidence contributes only a mixed
quality/material/degree and amount/ingredient record architecture; no
historical spelling is matched to EVA.

## Claim ceiling

These are concrete, replaceable complete-whole renderer defaults, not decoded
words. GDT782 confirms zero lexemes, plaintext clauses, numbers, units,
specific substances or EVA component values. It opens no new page, image,
OCR or transcription; `f84` and `f84r` remain sealed.

## Reproduction

```bash
python3 -B experiments/yolo/gdt782_recurrent_six_target_external_field_adjudication/src/run.py
python3 -B experiments/yolo/gdt782_recurrent_six_target_external_field_adjudication/src/validate.py
./vmanus-exp check-edge-packet experiments/yolo/gdt782_recurrent_six_target_external_field_adjudication/artifacts/GDT782_GDT388_EXTERNAL_FIELD_PACKET.tsv
```

The independent validator byte-replays the runner-owned artifacts and this
report. The {len(changed)} changed target patches and the retained
`shdair` patch are fully enumerated.
"""


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--artifacts-dir", type=Path, default=ART)
    parser.add_argument("--report-path", type=Path, default=REPORT)
    args = parser.parse_args()
    artifacts = args.artifacts_dir.resolve()
    report_path = args.report_path.resolve()

    lock_count, lock_hash = verify_locks()
    candidates = read_tsv(CANDIDATES)
    manual_source = read_tsv(MANUAL)
    final_rows = read_tsv(FINAL_SPECS)
    if tuple(row["surface"] for row in final_rows) != TARGET_ORDER:
        raise AssertionError("final spec order changed")
    final_specs = one_by(final_rows, "surface")
    if set(row["surface"] for row in candidates) != TARGETS:
        raise AssertionError("candidate surface set changed")
    for row in final_rows:
        if not any(
            candidate["surface"] == row["surface"]
            and candidate["candidate_id"] == row["selected_candidate_id"]
            and candidate["candidate_de"] == row["gdt782_default_de"]
            for candidate in candidates
        ):
            raise AssertionError(
                f"final candidate not in deck: {row['surface']}"
            )
        if any(row[field] != "0" for field in (
            "default_is_translation",
            "confirmed_lexeme",
            "confirmed_plaintext",
            "component_export_credit",
            "numeric_identity_confirmed",
            "specific_substance_confirmed",
        )):
            raise AssertionError("final spec exceeds claim ceiling")

    by_line, exact, cross, line_meta, cells, guard = load_context()
    pool, pool_diagnostics, _ = build_clean_pool()
    occurrence_rows, exact_occurrence_rows = reconstruct_occurrences(
        by_line, exact, cross, line_meta,
    )
    neighbor_rows, _, external = build_external_neighbors(
        exact_occurrence_rows, by_line, exact, cells, pool,
    )
    summaries, contacts = build_field_summaries(
        external, neighbor_rows, final_specs,
    )
    scorecards = build_scorecards(
        candidates, external, neighbor_rows, contacts, final_specs,
    )
    manual = build_manual_artifact(manual_source)
    revisions = build_revisions(
        final_rows, scorecards, manual, external, summaries,
    )
    parent_renderer = read_tsv(G781_RENDERER)
    renderer, owners = build_renderer(parent_renderer, revisions)
    patches = build_target_patches(revisions)
    external_reader = build_external_reader(
        external, neighbor_rows, revisions, by_line,
    )
    packet, crosswalk = make_packet(external, neighbor_rows)

    outputs = [
        ("GDT782_20_CACHE_OCCURRENCE_ATLAS.tsv", occurrence_rows),
        (
            "GDT782_14_READER_EXACT_OCCURRENCE_ATLAS.tsv",
            exact_occurrence_rows,
        ),
        ("GDT782_65_EXTERNAL_NEIGHBOR_ATLAS.tsv", neighbor_rows),
        ("GDT782_8_EXTERNAL_FIELD_SUMMARY.tsv", summaries),
        ("GDT782_REGISTERED_CONSTRUCTION_CONTACTS.tsv", contacts),
        ("GDT782_23_CANDIDATE_SCORECARDS.tsv", scorecards),
        ("GDT782_18_MANUAL_READER_ASSESSMENTS.tsv", manual),
        ("GDT782_6_WORKING_REVISIONS.tsv", revisions),
        ("GDT782_6_TARGET_PASSAGE_PATCHES.tsv", patches),
        ("GDT782_8_EXTERNAL_WORKING_READER.tsv", external_reader),
        ("GDT782_376_RENDERER.tsv", renderer),
        ("GDT782_GDT388_EXTERNAL_FIELD_PACKET.tsv", packet),
        ("GDT782_RELATION_EDGE_CROSSWALK.tsv", crosswalk),
    ]
    for name, rows in outputs:
        if not rows:
            raise AssertionError(f"empty output: {name}")
        write_tsv(artifacts / name, rows, list(rows[0]))

    if str(ROOT) not in sys.path:
        sys.path.insert(0, str(ROOT))
    from tools.relation_edge_intake import validate_relation_edge_packet

    packet_intake = validate_relation_edge_packet(
        artifacts / "GDT782_GDT388_EXTERNAL_FIELD_PACKET.tsv"
    )
    if packet_intake != {
        "status": "VALID_ACQUISITION_NOT_SCORE_READY",
        "packet_rows": 8,
        "eligible_edges": 0,
        "eligible_folios": 0,
        "discovery_edges": 0,
        "holdout_edges": 0,
        "mobile_edges": 0,
        "capacity_gate_50_edges_5_folios": False,
        "holdout_gate": False,
        "mobile_null_gate": False,
        "score_ready": False,
        "errors": [],
    }:
        raise AssertionError(
            f"unexpected edge intake: {packet_intake}"
        )
    write_json(
        artifacts / "RELATION_PACKET_INTAKE.json", packet_intake
    )

    parent_result = json.loads(
        G781_RESULT.read_text(encoding="utf-8")
    )
    result: dict[str, object] = {
        "experiment_id": "GDT782",
        "status": STATUS,
        "source_locks": lock_count,
        "source_lock_sha256": lock_hash,
        "source_spec_sha256": {
            "candidates": sha256(CANDIDATES),
            "manual_assessments": sha256(MANUAL),
            "final_specs": sha256(FINAL_SPECS),
        },
        "inherited_guard": guard,
        "clean_pool": pool_diagnostics,
        "provenance_sanitation": {
            "gdt754_neighbor_rows": sum(
                int(row["gdt754_provenance_present"]) for row in neighbor_rows
            ),
            "sanitized_neighbor_rows": sum(
                int(
                    row["neighbor_class"]
                    == "SANITIZED_GDT754_WHOLE_HYPOTHESIS"
                )
                for row in neighbor_rows
            ),
            "sanitized_surfaces": sorted({
                str(row["neighbor_surface"])
                for row in neighbor_rows
                if row["neighbor_class"]
                == "SANITIZED_GDT754_WHOLE_HYPOTHESIS"
            }),
            "radius3_clean_votes_removed": sum(
                int(
                    row["neighbor_class"]
                    == "SANITIZED_GDT754_WHOLE_HYPOTHESIS"
                    and int(row["within_radius_3"])
                )
                for row in neighbor_rows
            ),
        },
        "cohort": {
            "surfaces": 6,
            "cache_occurrences": 20,
            "reader_exact_occurrences": 14,
            "reader_nonexact_exclusions": 6,
            "masked_gdt781_targets": 6,
            "target_external_occurrences": 8,
            "external_neighbor_rows": 65,
            "external_physical_folios": len({
                row["physical_folio"] for row in external
            }),
            "external_surface_counts": dict(EXPECTED_EXTERNAL),
            "whole_line_all_present_exact": sum(
                int(row["all_present_exact_line"])
                for row in exact_occurrence_rows
            ),
            "radius3_target_surface_leakage": 0,
            "radius3_cross_cohort_analogy_source_contacts": sum(
                int(
                    row["other_cohort_target_analogy_source"]
                    != "NONE"
                )
                for row in neighbor_rows
                if int(row["within_radius_3"])
            ),
            "full_line_cross_cohort_analogy_source_contacts": sum(
                int(
                    row["other_cohort_target_analogy_source"]
                    != "NONE"
                )
                for row in neighbor_rows
            ),
        },
        "construction": {
            "registered_adjacent_contacts": len(contacts),
            "surface": contacts[0]["surface"],
            "expression": contacts[0]["construction_eva"],
            "working_default_de": (
                contacts[0]["construction_default_de"]
            ),
            "global_exact_pair_count": int(
                contacts[0]["exact_pair_global_count"]
            ),
        },
        "adjudication": {
            "candidate_rows": len(scorecards),
            "manual_reader_rows": len(manual),
            "manual_readers": 3,
            "revised_cards": 5,
            "kept_cards": 1,
            "revised_surfaces": [
                row["surface"] for row in revisions
                if row["decision"] == "REVISE"
            ],
            "kept_surfaces": [
                row["surface"] for row in revisions
                if row["decision"] == "KEEP"
            ],
            "final_defaults": {
                str(row["surface"]): str(row["gdt782_default_de"])
                for row in revisions
            },
        },
        "renderer": {
            "rows": len(renderer),
            "gdt781_contextual": (
                parent_result["renderer"]["gdt781_contextual"]
            ),
            "gdt782_contextual": sum(
                int(row["gdt782_renderer_contextual"])
                for row in renderer
            ),
            "gdt781_fallbacks": (
                parent_result["renderer"]["gdt781_fallbacks"]
            ),
            "gdt782_fallbacks": sum(
                1 - int(row["gdt782_renderer_contextual"])
                for row in renderer
            ),
            "display_changes": sum(
                int(row["gdt782_display_changed"]) for row in renderer
            ),
            "target_confirmations": 1,
            "unchanged_non_target_rows": 370,
        },
        "consumption": {
            "gdt781_unique_right_tokens": (
                parent_result["consumption"]["total_unique_right_tokens"]
            ),
            "gdt782_unique_right_tokens": len(owners),
            "new_consumptions": 0,
            "collisions": 0,
        },
        "manual_disagreement": {
            "chedor": (
                "2_SELECT_MATERIAL_COMPLEMENT__1_KEEP_PORTION"
            ),
            "shdair": (
                "2_KEEP_MATERIAL__1_SELECT_MOIST_PORTION"
            ),
            "retained_publicly": True,
        },
        "relation_packet": packet_intake,
        "confirmed_lexemes": 0,
        "confirmed_plaintext_clauses": 0,
        "numeric_identities": 0,
        "specific_substances": 0,
        "component_exports": 0,
        "new_pages": 0,
        "new_images": 0,
        "new_ocr": 0,
        "new_transcriptions": 0,
        "sealed_pages_accessed": 0,
        "claim_ceiling": (
            "Six replaceable complete-whole target-span defaults revised "
            "or retained from eight target-external fields; no component, "
            "lexeme, plaintext, numeric, unit, substance, language or "
            "glyph claim."
        ),
    }
    write_json(artifacts / "RESULT.json", result)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(
        build_report(
            result, revisions, summaries, patches, external_reader
        ),
        encoding="utf-8",
    )
    (artifacts / "README.md").write_text(
        build_artifact_readme(), encoding="utf-8",
    )
    print(
        json.dumps(result, ensure_ascii=False, sort_keys=True, indent=2)
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
