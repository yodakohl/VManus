#!/usr/bin/env python3
"""Build GDT631: test ch/sh prefixed cth part compounds and quality contacts."""

from __future__ import annotations

import csv
import hashlib
import io
import json
import re
import subprocess
import sys
from collections import Counter, defaultdict
from itertools import combinations
from pathlib import Path
from typing import Iterable

sys.dont_write_bytecode = True


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
BASE_REL = Path("experiments/yolo/gdt631_prefixed_cth_quality_parts")
ART = ROOT / BASE_REL / "artifacts"
TOKENS_REL = Path("transcription/voynich_zl3b_tokens.tsv")
CROSS_REL = Path("transcription/voynich_cross_transcription_lines.tsv")
G625 = Path("experiments/yolo/gdt625_ordered_quality_state_transitions/artifacts")
G625_CTH_REL = G625 / "CTH_ROOT_FAMILY.tsv"
G625_TERMINAL_REL = G625 / "TERMINAL_QUALITY_OCCURRENCES.tsv"
G625_VISUAL_REL = G625 / "MANUAL_VISUAL_JUDGMENTS.tsv"
G623_VISUAL_OBS_REL = Path("experiments/yolo/gdt623_temperament_orientation_frequency/artifacts/VISUAL_OBSERVATIONS.tsv")
G623_VISUAL_ROLE_REL = Path("experiments/yolo/gdt623_temperament_orientation_frequency/artifacts/VISUAL_ROLE_AUDIT.tsv")
G627 = Path("experiments/yolo/gdt627_value_head_role_atlas/artifacts")
G627_AXIS_REL = G627 / "QUALITY_AXIS_DEGREE_OCCURRENCES.tsv"
G630 = Path("experiments/yolo/gdt630_outer_carrier_attachment/artifacts")
G628_OL_REL = Path("experiments/yolo/gdt628_chol_measure_frame/artifacts/OL_OR_CARRIER_OCCURRENCES.tsv")
ALLOW_REL = G630 / "PAGE_ALLOWLIST.tsv"
G630_EXPRESSIONS_REL = G630 / "VALUE_EXPRESSION_OCCURRENCES.tsv"
G630_DICT_REL = G630 / "WORKING_DICTIONARY_V7.tsv"
G630_RESULT_REL = G630 / "RESULT.json"

OUTPUTS = {
    "allowlist": BASE_REL / "artifacts/PAGE_ALLOWLIST.tsv",
    "occurrences": BASE_REL / "artifacts/PREFIXED_CTH_OCCURRENCES.tsv",
    "reader": BASE_REL / "artifacts/CROSS_READER_PREFIX_REALIZATIONS.tsv",
    "bridges": BASE_REL / "artifacts/CROSS_READER_PREFIX_BOUNDARY_BRIDGES.tsv",
    "outer_bridges": BASE_REL / "artifacts/TARGET_OUTER_BOUNDARY_BRIDGES.tsv",
    "matrix": BASE_REL / "artifacts/PREFIX_REMAINDER_MATRIX.tsv",
    "pairs": BASE_REL / "artifacts/PREFIX_REMAINDER_MINIMAL_PAIRS.tsv",
    "local": BASE_REL / "artifacts/LOCAL_PREFIX_CONTRASTS.tsv",
    "slots": BASE_REL / "artifacts/SHARED_PART_SLOT_FRAMES.tsv",
    "quality": BASE_REL / "artifacts/PREFIXED_CTH_QUALITY_CONTACTS.tsv",
    "local_quality": BASE_REL / "artifacts/PREFIXED_CTH_LOCAL_QUALITY_NEIGHBORS.tsv",
    "quality_summary": BASE_REL / "artifacts/QUALITY_CONTACT_SUMMARY.tsv",
    "repeated": BASE_REL / "artifacts/REPEATED_CLAUSE_FRAMES.tsv",
    "sections": BASE_REL / "artifacts/SECTION_PREFIX_PROFILE.tsv",
    "factor_grid": BASE_REL / "artifacts/EXTENDED_CTH_FACTOR_GRID.tsv",
    "historical": BASE_REL / "artifacts/HISTORICAL_COMPOSITION_COMPARATORS.tsv",
    "visual": BASE_REL / "artifacts/INHERITED_VISUAL_SCOPE.tsv",
    "cases": BASE_REL / "artifacts/CONCRETE_CLAUSES_V3.tsv",
    "ranking": BASE_REL / "artifacts/PREFIX_ROLE_RANKING.tsv",
    "dictionary": BASE_REL / "artifacts/WORKING_DICTIONARY_V8.tsv",
    "result": BASE_REL / "artifacts/RESULT.json",
}

PREFIX_ORDER = ("BARE", "CH", "SH", "K", "T")
PREFIX_SURFACE = {"BARE": "", "CH": "ch", "SH": "sh", "K": "k", "T": "t"}
PREFIX_DEFAULT = {
    "BARE": "unmarkierte cth-Pflanzenteilform",
    "CH": "trockene cth-Pflanzenteilform",
    "SH": "feuchte cth-Pflanzenteilform",
    "K": "heiße cth-Pflanzenteilform",
    "T": "kalte cth-Pflanzenteilform",
}
PREFIX_RE = re.compile(r"^(?:(ch|sh|k|t))?cth(.*)$")
FULL_FACTOR_RE = re.compile(r"^(?:(qo|o))?(?:(kch|ksh|tch|tsh|ch|sh|k|t))?cth(.*)$")
CORE_DEFAULT = {
    "NONE": "ohne Qualitätskern", "K": "heiß", "T": "kalt", "CH": "trocken", "SH": "feucht",
    "KCH": "heiß-trocken", "KSH": "heiß-feucht", "TCH": "kalt-trocken", "TSH": "kalt-feucht",
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_hash(value: object) -> str:
    raw = json.dumps(value, sort_keys=True, ensure_ascii=True, separators=(",", ":")).encode()
    return hashlib.sha256(raw).hexdigest()


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: list[dict[str, object]], fields: Iterable[str]) -> None:
    names = list(fields)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=names, delimiter="\t", lineterminator="\n", extrasaction="raise")
        writer.writeheader()
        for row in rows:
            writer.writerow({name: row.get(name, "NONE") if row.get(name, "") != "" else "NONE" for name in names})


def guarded_query(relative_path: Path, pages: set[str], columns: str) -> tuple[list[dict[str, str]], dict[str, int]]:
    command = [str(ROOT / "vmanus-exp"), "query-tsv", str(relative_path), "--selector", "page"]
    for page in sorted(pages):
        command.extend(("--allow", page))
    command.extend(("--columns", columns, "--forbid-prefix", "f84", "--forbid-prefix", "f84r"))
    completed = subprocess.run(command, cwd=ROOT, text=True, capture_output=True, check=False)
    if completed.returncode:
        raise RuntimeError(completed.stderr or "guarded query failed")
    stats_lines = [line for line in completed.stderr.splitlines() if line.startswith("GUARD_STATS ")]
    if len(stats_lines) != 1:
        raise RuntimeError("guard statistics missing")
    rows = list(csv.DictReader(io.StringIO(completed.stdout), delimiter="\t"))
    if any(row["page"] == "f1r" or row["page"].startswith("f84") for row in rows):
        raise RuntimeError("forbidden page materialized")
    return rows, {key: int(value) for key, value in json.loads(stats_lines[0][12:]).items()}


def line_number(locus: str) -> int:
    match = re.search(r"\.([0-9]+)$", locus)
    if match is None:
        raise ValueError(locus)
    return int(match.group(1))


def token_sort_key(row: dict[str, object]) -> tuple[str, int, int]:
    return str(row["page"]), line_number(str(row["locus"])), int(row["token_index"])


def parse_cth(surface: str) -> tuple[str, str] | None:
    match = PREFIX_RE.fullmatch(surface)
    if match is None:
        return None
    return (match.group(1) or "BARE").upper(), match.group(2) or "BARE"


def surface_for(prefix: str, remainder: str) -> str:
    return PREFIX_SURFACE[prefix] + "cth" + ("" if remainder == "BARE" else remainder)


def concatenated_span_count(words: list[str], target: str) -> int:
    count = 0
    for start in range(len(words)):
        joined = ""
        for end in range(start, len(words)):
            joined += words[end]
            if joined == target:
                count += 1
                break
            if len(joined) >= len(target) or not target.startswith(joined):
                break
    return count


def reader_mode(words: list[str], target: str, prefix: str, bare_surface: str) -> str:
    exact = target in words
    split = any(left == prefix and right == bare_surface for left, right in zip(words, words[1:]))
    normalized = concatenated_span_count(words, target)
    modes = []
    if exact:
        modes.append("FUSED")
    if split:
        modes.append("SPLIT_PREFIX")
    if normalized and not exact and not split:
        modes.append("OTHER_BOUNDARY")
    return "+".join(modes) if modes else "ABSENT_OR_DIFFERENT"


def line_maps(tokens: list[dict[str, object]]) -> tuple[dict[str, list[dict[str, object]]], dict[str, str]]:
    by_line: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in tokens:
        by_line[str(row["locus"])].append(row)
    for rows in by_line.values():
        rows.sort(key=lambda row: int(row["token_index"]))
    return by_line, {locus: " ".join(str(row["eva"]) for row in rows) for locus, rows in by_line.items()}


def make_occurrences(
    token_rows: list[dict[str, str]], cross_by_locus: dict[str, dict[str, str]], line_text: dict[str, str]
) -> tuple[list[dict[str, object]], list[dict[str, object]]]:
    readers = (("zl3b", "zl3b_clean"), ("it2a", "it2a_clean"), ("rf1b", "rf1b_clean"))
    ordinal: Counter[tuple[str, str]] = Counter()
    all_rows: list[dict[str, object]] = []
    reader_rows: list[dict[str, object]] = []
    for source in sorted(token_rows, key=token_sort_key):
        parsed = parse_cth(source["eva"])
        if parsed is None:
            continue
        prefix, remainder = parsed
        target = source["eva"]
        ordinal[source["locus"], target] += 1
        current_ordinal = ordinal[source["locus"], target]
        cross = cross_by_locus[source["locus"]]
        exact_caps, normalized_caps = [], []
        modes: dict[str, str] = {}
        bare_surface = surface_for("BARE", remainder)
        for reader, field in readers:
            words = cross[field].split()
            exact_caps.append(words.count(target))
            normalized_caps.append(concatenated_span_count(words, target))
            if prefix != "BARE":
                modes[reader] = reader_mode(words, target, PREFIX_SURFACE[prefix], bare_surface)
        exact_stable = int(current_ordinal <= min(exact_caps))
        normalized_stable = int(current_ordinal <= min(normalized_caps))
        occurrence = {
            "occurrence_id": "", "page": source["page"], "locus": source["locus"],
            "token_index": int(source["token_index"]), "surface": target, "prefix": prefix,
            "prefix_surface": PREFIX_SURFACE[prefix] or "NONE", "cth_root": "cth", "remainder": remainder,
            "bare_counterpart_surface": bare_surface, "section": source["section"], "hand": source["hand"],
            "triple_exact_token_stable": exact_stable, "triple_boundary_normalized": normalized_stable,
            "working_composition_de": PREFIX_DEFAULT[prefix], "surface_line": line_text[source["locus"]],
        }
        all_rows.append(occurrence)
        if prefix != "BARE":
            reader_rows.append({
                "occurrence_id": "", "page": source["page"], "locus": source["locus"],
                "token_index": int(source["token_index"]), "surface": target, "prefix": prefix,
                "remainder": remainder, "bare_counterpart_surface": bare_surface,
                "zl3b_mode": modes["zl3b"], "it2a_mode": modes["it2a"], "rf1b_mode": modes["rf1b"],
                "triple_exact_token_stable": exact_stable, "triple_boundary_normalized": normalized_stable,
                "any_split_prefix_reader": int(any("SPLIT_PREFIX" in mode for mode in modes.values())),
                "surface_line": line_text[source["locus"]],
            })
    for index, row in enumerate(all_rows, 1):
        row["occurrence_id"] = f"G631-O{index:04d}"
    occurrence_id = {(row["locus"], int(row["token_index"])): row["occurrence_id"] for row in all_rows}
    for row in reader_rows:
        row["occurrence_id"] = occurrence_id[row["locus"], int(row["token_index"])]
    return all_rows, reader_rows


def make_matrix(occurrences: list[dict[str, object]]) -> list[dict[str, object]]:
    grouped: dict[tuple[str, str], list[dict[str, object]]] = defaultdict(list)
    for row in occurrences:
        grouped[str(row["remainder"]), str(row["prefix"])].append(row)
    remainders = sorted({key[0] for key in grouped}, key=lambda rem: (-sum(len(grouped[rem, p]) for p in PREFIX_ORDER), rem))
    rows: list[dict[str, object]] = []
    for remainder in remainders:
        row: dict[str, object] = {"remainder": remainder}
        occupied = []
        for prefix in PREFIX_ORDER:
            selected = grouped.get((remainder, prefix), [])
            key = prefix.lower()
            row[f"{key}_surface"] = surface_for(prefix, remainder)
            row[f"{key}_occurrences"] = len(selected)
            row[f"{key}_pages"] = len({str(item["page"]) for item in selected})
            row[f"{key}_triple_exact"] = sum(int(item["triple_exact_token_stable"]) for item in selected)
            if selected:
                occupied.append(prefix)
        row["occupied_prefixes"] = "|".join(occupied)
        row["prefixed_modes"] = sum(bool(grouped.get((remainder, prefix))) for prefix in PREFIX_ORDER[1:])
        row["total_occurrences"] = sum(len(grouped.get((remainder, prefix), [])) for prefix in PREFIX_ORDER)
        rows.append(row)
    return rows


def make_pairs(matrix: list[dict[str, object]]) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for source in matrix:
        if not int(source["bare_occurrences"]):
            continue
        for prefix in PREFIX_ORDER[1:]:
            key = prefix.lower()
            if not int(source[f"{key}_occurrences"]):
                continue
            rows.append({
                "pair_id": "", "remainder": source["remainder"], "prefix": prefix,
                "bare_surface": source["bare_surface"], "prefixed_surface": source[f"{key}_surface"],
                "bare_occurrences": source["bare_occurrences"], "prefixed_occurrences": source[f"{key}_occurrences"],
                "bare_pages": source["bare_pages"], "prefixed_pages": source[f"{key}_pages"],
                "bare_triple_exact": source["bare_triple_exact"], "prefixed_triple_exact": source[f"{key}_triple_exact"],
                "working_contrast_de": f"{PREFIX_DEFAULT['BARE']} ↔ {PREFIX_DEFAULT[prefix]}",
                "pair_status": "TYPE_LEVEL_COMPOSITIONAL_PAIR",
            })
    rows.sort(key=lambda row: (PREFIX_ORDER.index(str(row["prefix"])), -int(row["prefixed_occurrences"]), str(row["remainder"])))
    for index, row in enumerate(rows, 1):
        row["pair_id"] = f"G631-M{index:03d}"
    return rows


def make_boundary_bridges(
    pairs: list[dict[str, object]], cross_rows: list[dict[str, str]]
) -> list[dict[str, object]]:
    readers = (("ZL3b", "zl3b_clean"), ("IT2a", "it2a_clean"), ("RF1b", "rf1b_clean"))
    rows: list[dict[str, object]] = []
    for cross in cross_rows:
        for pair in pairs:
            target = str(pair["prefixed_surface"])
            prefix = PREFIX_SURFACE[str(pair["prefix"])]
            bare = str(pair["bare_surface"])
            modes: dict[str, str] = {}
            for reader, field in readers:
                words = cross[field].split()
                fused = target in words
                split = any(left == prefix and right == bare for left, right in zip(words, words[1:]))
                if fused and split:
                    modes[reader] = "BOTH"
                elif fused:
                    modes[reader] = "FUSED"
                elif split:
                    modes[reader] = "SPLIT_PREFIX"
                else:
                    modes[reader] = "ABSENT_OR_DIFFERENT"
            values = set(modes.values())
            normalized = all(mode != "ABSENT_OR_DIFFERENT" for mode in modes.values())
            crosses = any(mode in {"FUSED", "BOTH"} for mode in modes.values()) and any(mode in {"SPLIT_PREFIX", "BOTH"} for mode in modes.values())
            if not normalized or not crosses:
                continue
            rows.append({
                "bridge_id": "", "page": cross["page"], "locus": cross["locus"],
                "prefix": pair["prefix"], "remainder": pair["remainder"], "fused_surface": target,
                "split_surface": f"{prefix} {bare}", "zl3b_mode": modes["ZL3b"], "it2a_mode": modes["IT2a"],
                "rf1b_mode": modes["RF1b"], "triple_boundary_normalized": 1,
                "working_equivalence": f"{target} ↔ {prefix} {bare}",
                "zl3b_line": cross["zl3b_clean"], "it2a_line": cross["it2a_clean"], "rf1b_line": cross["rf1b_clean"],
            })
    rows.sort(key=lambda row: (str(row["page"]), line_number(str(row["locus"])), str(row["fused_surface"])))
    for index, row in enumerate(rows, 1):
        row["bridge_id"] = f"G631-B{index:02d}"
    return rows


def make_outer_boundary_bridges(cross_by_locus: dict[str, dict[str, str]]) -> list[dict[str, object]]:
    specs = (
        ("f111r.53", "chcthy", "chcthydain", "chcthy dain", "chcthy dain", "TRIPLE_NORMALIZED", "chcthy bleibt ganz; der Wert-II-Rest dain löst sich außen ab"),
        ("f81r.29", "chcthy", "l chcthy", "lchcthy", "l chcthy", "TRIPLE_NORMALIZED", "chcthy bleibt ganz; linkes l bindet nur in IT2a an"),
        ("f95v1.3", "chcthy", "chcthykedy", "chcthy kedy", "chcthyke y", "ZL_IT_PAIRWISE", "ZL/IT bewahren chcthy vor wechselnder rechter Grenze; RF1b liest den Rest anders"),
    )
    rows: list[dict[str, object]] = []
    for index, (locus, target, zl_span, it_span, rf_span, support, interpretation) in enumerate(specs, 1):
        source = cross_by_locus[locus]
        for expected, field in ((zl_span, "zl3b_clean"), (it_span, "it2a_clean"), (rf_span, "rf1b_clean")):
            if expected not in source[field]:
                raise RuntimeError(f"outer bridge drift {locus} {field}: {expected}")
        rows.append({
            "bridge_id": f"G631-X{index:02d}", "page": source["page"], "locus": locus, "target_unit": target,
            "zl3b_target_span": zl_span, "it2a_target_span": it_span, "rf1b_target_span": rf_span,
            "support": support, "working_interpretation_de": interpretation,
            "zl3b_line": source["zl3b_clean"], "it2a_line": source["it2a_clean"], "rf1b_line": source["rf1b_clean"],
        })
    return rows


def make_local_contrasts(occurrences: list[dict[str, object]], line_text: dict[str, str]) -> list[dict[str, object]]:
    by_line: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in occurrences:
        by_line[str(row["locus"])].append(row)
    rows: list[dict[str, object]] = []
    for locus, selected in by_line.items():
        for left, right in combinations(sorted(selected, key=lambda row: int(row["token_index"])), 2):
            if left["remainder"] != right["remainder"] or left["prefix"] == right["prefix"]:
                continue
            rows.append({
                "contrast_id": "", "page": left["page"], "locus": locus, "remainder": left["remainder"],
                "left_surface": left["surface"], "left_prefix": left["prefix"], "left_token_index": left["token_index"],
                "right_surface": right["surface"], "right_prefix": right["prefix"], "right_token_index": right["token_index"],
                "token_distance": int(right["token_index"]) - int(left["token_index"]),
                "both_triple_exact": int(int(left["triple_exact_token_stable"]) and int(right["triple_exact_token_stable"])),
                "contrast_class": "SAME_REMAINDER_LOCAL_PREFIX_CONTRAST", "surface_line": line_text[locus],
            })
    rows.sort(key=lambda row: (str(row["page"]), line_number(str(row["locus"])), int(row["left_token_index"])))
    for index, row in enumerate(rows, 1):
        row["contrast_id"] = f"G631-L{index:03d}"
    return rows


def make_shared_slots(
    occurrences: list[dict[str, object]], by_line: dict[str, list[dict[str, object]]], line_text: dict[str, str]
) -> list[dict[str, object]]:
    target_surfaces = {"cthy", "chcthy", "shcthy"}
    rows: list[dict[str, object]] = []
    occurrence_by_position = {(str(row["locus"]), int(row["token_index"])): row for row in occurrences}
    for locus, line in by_line.items():
        for index, token in enumerate(line):
            surface = str(token["eva"])
            if surface not in target_surfaces or index == 0 or str(line[index - 1]["eva"]) != "daiin" or index != len(line) - 1:
                continue
            occurrence = occurrence_by_position[locus, int(token["token_index"])]
            rows.append({
                "slot_id": "", "page": token["page"], "locus": locus, "surface": surface,
                "prefix": occurrence["prefix"], "frame": "daiin __ <LINE_END>",
                "target_triple_exact": occurrence["triple_exact_token_stable"],
                "working_category_de": "cth-Pflanzen-/Drogengut im gleichen terminalen Partslot",
                "surface_line": line_text[locus],
            })
    rows.sort(key=lambda row: (str(row["page"]), line_number(str(row["locus"]))))
    for index, row in enumerate(rows, 1):
        row["slot_id"] = f"G631-S{index:02d}"
    return rows


def axis_components(root: str) -> tuple[set[str], str]:
    core = root[2:] if root.startswith("qo") else root[1:] if root.startswith("o") else root
    axes: set[str] = set()
    if core.startswith("k"):
        axes.add("HOT")
        core = core[1:]
    elif core.startswith("t"):
        axes.add("COLD")
        core = core[1:]
    if core == "ch" or root.endswith("ch"):
        axes.add("DRY")
    if core == "sh" or root.endswith("sh"):
        axes.add("MOIST")
    return axes, "|".join(sorted(axes)) or "OPEN"


def quality_references() -> dict[str, list[dict[str, object]]]:
    by_locus: dict[str, list[dict[str, object]]] = defaultdict(list)
    seen: set[tuple[str, int, int, str]] = set()
    for source in read_tsv(ROOT / G627_AXIS_REL):
        axes, axis_label = axis_components(source["quality_root"])
        start = end = int(source["token_index"])
        key = source["locus"], start, end, "MINIM_QUALITY_DEGREE"
        if key in seen:
            continue
        seen.add(key)
        by_locus[source["locus"]].append({
            "source": "GDT627_MINIM_QUALITY_DEGREE", "start": start, "end": end,
            "surface": source["surface"], "quality_root": source["quality_root"], "axes": axes,
            "axis_label": axis_label, "working_reading_de": source["working_degree_de"],
            "triple_stable": int(source["triple_reading_token_stable"]),
        })
    for source in read_tsv(ROOT / G630_EXPRESSIONS_REL):
        if not int(source["core_quality_concrete"]):
            continue
        axes, axis_label = axis_components(source["quality_core"])
        start, end = int(source["token_index_start"]), int(source["token_index_end"])
        key = source["locus"], start, end, "OL_QUALITY_DEGREE"
        if key in seen:
            continue
        seen.add(key)
        by_locus[source["locus"]].append({
            "source": "GDT630_OL_QUALITY_DEGREE", "start": start, "end": end,
            "surface": source["surface_expression"], "quality_root": source["quality_core"], "axes": axes,
            "axis_label": axis_label, "working_reading_de": source["working_reading_de"],
            "triple_stable": int(source["expression_triple_reader_stable"]),
        })
    return by_locus


def local_quality_references() -> dict[str, list[dict[str, object]]]:
    by_locus: dict[str, list[dict[str, object]]] = defaultdict(list)
    for source in read_tsv(ROOT / G625_TERMINAL_REL):
        axes: set[str] = set()
        if source["thermal"] == "k":
            axes.add("HOT")
        elif source["thermal"] == "t":
            axes.add("COLD")
        if source["moisture"] == "ch":
            axes.add("DRY")
        elif source["moisture"] == "sh":
            axes.add("MOIST")
        by_locus[source["locus"]].append({
            "source": "GDT625_TERMINAL_QUALITY", "index": int(source["token_index"]),
            "surface": source["surface"], "axes": axes, "axis_label": "|".join(sorted(axes)),
            "working_reading_de": source["working_state_de"], "triple_stable": int(source["triple_reading_token_stable"]),
        })
    for source in read_tsv(ROOT / G628_OL_REL):
        if source["role"] != "QUALITY_STATE_CARRIER" or source["ending"] != "OL" or source["quality_core"] == "NONE":
            continue
        axes, axis_label = axis_components(source["quality_core"])
        by_locus[source["locus"]].append({
            "source": "GDT628_BARE_OL_QUALITY", "index": int(source["token_index"]),
            "surface": source["surface"], "axes": axes, "axis_label": axis_label,
            "working_reading_de": source["working_meaning_de"], "triple_stable": int(source["triple_reading_token_stable"]),
        })
    return by_locus


def contact_relation(prefix: str, axes: set[str]) -> str:
    if prefix == "BARE":
        return "NO_PREFIX_BASELINE"
    expected = {"CH": "DRY", "SH": "MOIST", "K": "HOT", "T": "COLD"}[prefix]
    opposite = {"DRY": "MOIST", "MOIST": "DRY", "HOT": "COLD", "COLD": "HOT"}[expected]
    if expected in axes:
        return "MATCHING_PREFIX_AXIS"
    if opposite in axes:
        return "OPPOSITE_PREFIX_AXIS"
    return "ORTHOGONAL_AXIS"


def part_reading(prefix: str, remainder: str, section: str = "OPEN") -> str:
    if prefix == "BARE":
        if remainder == "y":
            return "Blattgut/Blattdroge" if section == "H" else "CTH-Pflanzen-/Drogengut"
        return f"cth-Pflanzenteilform ({surface_for(prefix, remainder)})"
    quality = {"CH": "trockenes", "SH": "feuchtes", "K": "heißes", "T": "kaltes"}[prefix]
    if remainder == "y":
        return f"{quality} Blattgut/Blattdroge" if section == "H" else f"{quality} CTH-Pflanzen-/Drogengut"
    return f"{quality} cth-Pflanzenteilform ({surface_for(prefix, remainder)})"


def make_quality_contacts(
    occurrences: list[dict[str, object]], refs: dict[str, list[dict[str, object]]], line_text: dict[str, str]
) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for part in occurrences:
        prefix = str(part["prefix"])
        part_index = int(part["token_index"])
        for quality in refs.get(str(part["locus"]), []):
            start, end = int(quality["start"]), int(quality["end"])
            if end < part_index:
                distance, order = part_index - end, "QUALITY_BEFORE_PART"
            elif start > part_index:
                distance, order = start - part_index, "PART_BEFORE_QUALITY"
            else:
                continue
            if distance > 3:
                continue
            axes = set(quality["axes"])
            rows.append({
                "contact_id": "", "occurrence_id": part["occurrence_id"], "page": part["page"],
                "locus": part["locus"], "part_surface": part["surface"], "part_prefix": prefix,
                "part_remainder": part["remainder"], "part_token_index": part_index,
                "quality_source": quality["source"], "quality_surface": quality["surface"],
                "quality_root": quality["quality_root"], "quality_axes": quality["axis_label"],
                "quality_token_start": start, "quality_token_end": end, "distance": distance, "order": order,
                "prefix_axis_relation": contact_relation(prefix, axes),
                "both_triple_stable": int(int(part["triple_boundary_normalized"]) and int(quality["triple_stable"])),
                "working_part_de": part_reading(prefix, str(part["remainder"]), str(part["section"])),
                "working_quality_de": quality["working_reading_de"], "surface_line": line_text[str(part["locus"])],
            })
    rows.sort(key=lambda row: (str(row["page"]), line_number(str(row["locus"])), int(row["part_token_index"]), int(row["distance"]), str(row["quality_source"])))
    for index, row in enumerate(rows, 1):
        row["contact_id"] = f"G631-Q{index:03d}"
    return rows


def make_local_quality_neighbors(
    occurrences: list[dict[str, object]], refs: dict[str, list[dict[str, object]]], line_text: dict[str, str]
) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for part in occurrences:
        prefix = str(part["prefix"])
        if prefix == "BARE":
            continue
        for quality in refs.get(str(part["locus"]), []):
            if abs(int(part["token_index"]) - int(quality["index"])) != 1:
                continue
            relation = contact_relation(prefix, set(quality["axes"]))
            rows.append({
                "neighbor_id": "", "occurrence_id": part["occurrence_id"], "page": part["page"], "locus": part["locus"],
                "part_surface": part["surface"], "part_prefix": prefix, "part_remainder": part["remainder"],
                "quality_surface": quality["surface"], "quality_source": quality["source"], "quality_axes": quality["axis_label"],
                "order": "QUALITY_BEFORE_PART" if int(quality["index"]) < int(part["token_index"]) else "PART_BEFORE_QUALITY",
                "prefix_axis_relation": relation,
                "both_triple_stable": int(int(part["triple_exact_token_stable"]) and int(quality["triple_stable"])),
                "working_part_de": part_reading(prefix, str(part["remainder"]), str(part["section"])),
                "working_quality_de": quality["working_reading_de"], "surface_line": line_text[str(part["locus"])],
            })
    rows.sort(key=lambda row: (str(row["page"]), line_number(str(row["locus"])), str(row["part_surface"]), str(row["quality_surface"])))
    for index, row in enumerate(rows, 1):
        row["neighbor_id"] = f"G631-N{index:03d}"
    return rows


def make_quality_summary(contacts: list[dict[str, object]], occurrences: list[dict[str, object]]) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for prefix in PREFIX_ORDER:
        part_rows = [row for row in occurrences if row["prefix"] == prefix]
        selected = [row for row in contacts if row["part_prefix"] == prefix]
        relations = Counter(str(row["prefix_axis_relation"]) for row in selected)
        rows.append({
            "prefix": prefix, "working_prefix_de": PREFIX_DEFAULT[prefix], "part_occurrences": len(part_rows),
            "part_pages": len({str(row["page"]) for row in part_rows}), "contacts_within_three": len(selected),
            "immediate_contacts": sum(int(row["distance"]) == 1 for row in selected),
            "part_occurrences_with_contact_within_three": len({str(row["occurrence_id"]) for row in selected}),
            "part_occurrences_with_immediate_contact": len({str(row["occurrence_id"]) for row in selected if int(row["distance"]) == 1}),
            "both_triple_stable_contacts": sum(int(row["both_triple_stable"]) for row in selected),
            "matching_axis_contacts": relations["MATCHING_PREFIX_AXIS"],
            "opposite_axis_contacts": relations["OPPOSITE_PREFIX_AXIS"],
            "orthogonal_axis_contacts": relations["ORTHOGONAL_AXIS"],
            "matching_immediate": sum(int(row["distance"]) == 1 and row["prefix_axis_relation"] == "MATCHING_PREFIX_AXIS" for row in selected),
            "opposite_immediate": sum(int(row["distance"]) == 1 and row["prefix_axis_relation"] == "OPPOSITE_PREFIX_AXIS" for row in selected),
            "example_loci": "|".join(dict.fromkeys(str(row["locus"]) for row in selected[:8])) or "NONE",
        })
    return rows


def make_section_profile(occurrences: list[dict[str, object]]) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    sections = sorted({str(row["section"]) for row in occurrences})
    for prefix in PREFIX_ORDER:
        for section in sections:
            selected = [row for row in occurrences if row["prefix"] == prefix and row["section"] == section]
            if not selected:
                continue
            rows.append({
                "prefix": prefix, "section": section, "occurrences": len(selected),
                "pages": len({str(row["page"]) for row in selected}), "types": len({str(row["surface"]) for row in selected}),
                "triple_exact_occurrences": sum(int(row["triple_exact_token_stable"]) for row in selected),
                "hands": "|".join(sorted({str(row["hand"]) for row in selected})),
                "example_surfaces": "|".join(dict.fromkeys(str(row["surface"]) for row in selected[:8])),
            })
    return rows


def make_repeated_frames(contacts: list[dict[str, object]]) -> list[dict[str, object]]:
    grouped: dict[tuple[str, str, str], list[dict[str, object]]] = defaultdict(list)
    for row in contacts:
        if row["part_prefix"] == "BARE" or int(row["distance"]) != 1:
            continue
        grouped[str(row["part_surface"]), str(row["quality_surface"]), str(row["order"])].append(row)
    rows: list[dict[str, object]] = []
    for (part_surface, quality_surface, order), selected in grouped.items():
        if len(selected) < 2:
            continue
        first = selected[0]
        surface_clause = f"{part_surface} {quality_surface}" if order == "PART_BEFORE_QUALITY" else f"{quality_surface} {part_surface}"
        rows.append({
            "frame_id": "", "part_surface": part_surface, "quality_surface": quality_surface, "order": order,
            "surface_clause": surface_clause, "occurrences": len(selected),
            "pages": len({str(row["page"]) for row in selected}),
            "triple_stable_occurrences": sum(int(row["both_triple_stable"]) for row in selected),
            "prefix_axis_relation": first["prefix_axis_relation"],
            "working_reading_de": f"{first['working_part_de']}: {first['working_quality_de']}",
            "loci": "|".join(str(row["locus"]) for row in selected),
        })
    rows.sort(key=lambda row: (-int(row["occurrences"]), str(row["surface_clause"])))
    for index, row in enumerate(rows, 1):
        row["frame_id"] = f"G631-R{index:02d}"
    return rows


def make_factor_grid(token_rows: list[dict[str, str]], cross_by_locus: dict[str, dict[str, str]]) -> list[dict[str, object]]:
    grouped: dict[tuple[str, str], list[dict[str, object]]] = defaultdict(list)
    ordinal: Counter[tuple[str, str]] = Counter()
    for source in sorted(token_rows, key=token_sort_key):
        match = FULL_FACTOR_RE.fullmatch(source["eva"])
        if match is None:
            continue
        wrapper = (match.group(1) or "BARE").upper()
        core = (match.group(2) or "NONE").upper()
        remainder = match.group(3) or "BARE"
        ordinal[source["locus"], source["eva"]] += 1
        capacities = [cross_by_locus[source["locus"]][field].split().count(source["eva"]) for field in ("zl3b_clean", "it2a_clean", "rf1b_clean")]
        grouped[wrapper, core].append({
            "surface": source["eva"], "page": source["page"], "locus": source["locus"], "remainder": remainder,
            "stable": int(ordinal[source["locus"], source["eva"]] <= min(capacities)),
        })
    rows: list[dict[str, object]] = []
    for (wrapper, core), selected in sorted(grouped.items(), key=lambda item: (-len(item[1]), item[0])):
        wrapper_de = {"BARE": "ohne Außenrahmen", "O": "im o-Rahmen", "QO": "im qo-Rahmen"}[wrapper]
        rows.append({
            "outer_wrapper": wrapper, "quality_core": core, "occurrences": len(selected),
            "types": len({str(row["surface"]) for row in selected}), "pages": len({str(row["page"]) for row in selected}),
            "triple_exact_occurrences": sum(int(row["stable"]) for row in selected),
            "remainders": "|".join(sorted({str(row["remainder"]) for row in selected})),
            "example_surfaces": "|".join(dict.fromkeys(str(row["surface"]) for row in selected[:10])),
            "example_loci": "|".join(dict.fromkeys(str(row["locus"]) for row in selected[:10])),
            "working_factor_reading_de": f"{wrapper_de}: {CORE_DEFAULT[core]} markiertes cth-Pflanzen-/Drogengut",
            "status": "PRIMARY_CH_SH_SERIES" if wrapper == "BARE" and core in {"CH", "SH"} else "NEXT_FACTOR_LEAD",
        })
    return rows


def make_historical_comparators() -> list[dict[str, object]]:
    return [
        {"comparator_id": "G631-H01", "date": "1390er; terminus ante quem 1399", "manuscript": "VI Fc 29, De virtutibus herbarum", "observed_formula": "Galganus est herba sive radix sicca", "structural_parallel_de": "Pflanzenteilklasse und trockener Zustand stehen unmittelbar zusammen", "source_url": "https://herbaria.phil.muni.cz/en/node/385", "limit": "belegt semantische Slots, nicht Voynich-Schreibung oder Verschmelzung"},
        {"comparator_id": "G631-H02", "date": "frühes 15. Jahrhundert", "manuscript": "Wellcome MS 542, f119v", "observed_formula": "Eleborus ... Radix ponitur in medicinis c. et s. in iii gradu", "structural_parallel_de": "Drogenname, Partkopf, knappe heiß/trocken-Kürzel und Grad bilden einen Mikroeintrag", "source_url": "https://wellcomecollection.org/works/n674z2xd", "limit": "c. und s. sind lateinische Kürzel; keine Zeichengleichung mit ch/sh"},
        {"comparator_id": "G631-H03", "date": "Mitte 15. Jahrhundert", "manuscript": "Wellcome MS 541, f184r", "observed_formula": "Dyamidrin ... calidum et siccum in 3 gradu", "structural_parallel_de": "gelernter Drogenname plus kompaktes Doppelqualitätsfeld und Grad", "source_url": "https://wellcomecollection.org/works/dbfbsjp4", "limit": "historische Architektur, kein Entzifferungsschlüssel"},
    ]


def make_inherited_visual_scope() -> list[dict[str, object]]:
    return [
        {"visual_id": "G631-V01", "page": "f2v", "locus": "f2v.3", "target_surface": "chcthy daiin", "inherited_observation_de": "Seite mit sehr großem rundem Blatt, heller Blüte und auffälligem unterirdischem Stock", "licensed_reading_de": "im Herbal ist CTH-Blatt-/Krautgut visuell plausibel", "not_licensed_de": "Trockenheit, drei Blätter oder eine absolute Maßeinheit", "source_provenance": "GDT623_VISUAL_OBSERVATIONS_AND_ROLE_AUDIT", "new_image_opened": 0},
        {"visual_id": "G631-V02", "page": "f18r", "locus": "f18r.6", "target_surface": "ytol chcthy", "inherited_observation_de": "reiche Belaubung, große Blüte und feine Wurzeln auf derselben geöffneten Seite", "licensed_reading_de": "CTH als oberirdisches Pflanzen-/Drogengut bleibt möglich", "not_licensed_de": "lokaler Grad, Trockenoperation oder eindeutiger gezeichneter Träger", "source_provenance": "GDT623_VISUAL_ROLE_AUDIT__GDT625_MANUAL_VISUAL_JUDGMENTS", "new_image_opened": 0},
        {"visual_id": "G631-V03", "page": "f43v", "locus": "f43v.7", "target_surface": "chcthy", "inherited_observation_de": "zwei sichtbar verschiedene Pflanzen- oder Wurzeleinheiten", "licensed_reading_de": "eine technische Zeile kann mehrere Träger/Zellen enthalten", "not_licensed_de": "Fernbindung aller Qualitätsformen an einen einzigen Träger", "source_provenance": "GDT623_VISUAL_ROLE_AUDIT__GDT625_F43_WARNING", "new_image_opened": 0},
    ]


def make_cases(contacts: list[dict[str, object]]) -> list[dict[str, object]]:
    selected = [row for row in contacts if row["part_prefix"] != "BARE" and int(row["distance"]) == 1 and int(row["both_triple_stable"])]
    rows: list[dict[str, object]] = []
    seen: set[tuple[str, str, str]] = set()
    for source in selected:
        key = str(source["locus"]), str(source["part_surface"]), str(source["quality_surface"])
        if key in seen:
            continue
        seen.add(key)
        clause = (f"{source['part_surface']} {source['quality_surface']}" if source["order"] == "PART_BEFORE_QUALITY" else f"{source['quality_surface']} {source['part_surface']}")
        rows.append({
            "case_id": f"G631-C{len(rows) + 1:02d}", "page": source["page"], "locus": source["locus"],
            "surface_clause": clause, "segmentation": f"{source['part_prefix'].lower()}+cth+{source['part_remainder']} | {source['quality_surface']}",
            "working_reading_de": f"{source['working_part_de']}: {source['working_quality_de']}",
            "prefix_axis_relation": source["prefix_axis_relation"], "reader_status": "TRIPLE_STABLE_COMPONENTS",
            "residual_policy": "Nur die sichtbare Part-Qualitätsklammer wird gelesen; übrige Tokens bleiben OPEN",
        })
    return rows


def make_ranking(matrix: list[dict[str, object]], quality_summary: list[dict[str, object]]) -> list[dict[str, object]]:
    ch_pairs = sum(int(row["ch_occurrences"]) > 0 and int(row["bare_occurrences"]) > 0 for row in matrix)
    sh_pairs = sum(int(row["sh_occurrences"]) > 0 and int(row["bare_occurrences"]) > 0 for row in matrix)
    summary = {str(row["prefix"]): row for row in quality_summary}
    return [
        {"rank": 1, "model": "QUALITY_PREFIX_PLUS_CTH_PART", "working_model_de": "ch/sh markieren trocken/feucht auf einer wiederkehrenden cth-Pflanzenteilbasis", "support": f"ch hat {ch_pairs} und sh {sh_pairs} bezeugte Restparallelen zur nackten cth-Reihe; k/t fehlen; unmittelbare Gradkontakte ch={summary['CH']['immediate_contacts']}, sh={summary['SH']['immediate_contacts']}", "counterevidence": "f24v.8 und f20v.3 stellen feuchtes shol unmittelbar neben chcthy; außerhalb Herbal ist Blattgut zu eng", "disposition": "PRIMARY_WORKING_COMPOSITION__MEANING_PROVISIONAL"},
        {"rank": 2, "model": "BINARY_SCRIBAL_OR_REGISTER_PREFIX", "working_model_de": "ch/sh kodieren zwei technische Klassen ohne gesicherte Trocken-/Feuchtbedeutung", "support": "die binäre Distribution ist auch als Klassifikator erklärbar", "counterevidence": "ch/sh tragen bereits unabhängig die aktuelle Qualitätsopposition und ergeben konkrete kompositionale Lesungen", "disposition": "LIVE_SEMANTIC_RIVAL"},
        {"rank": 3, "model": "FUSED_INDEPENDENT_CELL", "working_model_de": "ch oder sh war ursprünglich ein separater Qualitätscode vor cth und wurde zusammengeschrieben", "support": "technische Handschriften variieren Wortgrenzen", "counterevidence": "das vollständige Restparadigma verhält sich wie eine produktive Formfamilie, nicht wie ein einmaliger Spacingfehler", "disposition": "LIVE_BOUNDARY_RIVAL"},
        {"rank": 4, "model": "GENERIC_OPERATION", "working_model_de": "chcthy oder shcthy bedeuten unspezifisch bearbeiten, nehmen oder weitergeben", "support": "keiner", "counterevidence": "erklärt weder gemeinsame cth-Reste noch die selektive ch/sh-Opposition", "disposition": "REJECTED_AS_DEFAULT"},
    ]


def make_dictionary(old: list[dict[str, str]]) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = [dict(row) for row in old]
    rows.extend([
        {"entry": "ch+cth*", "kind": "DRY_PREFIXED_CTH_PART_FAMILY", "working_meaning_de": "trocken markierte cth-Pflanzen-/Drogenmaterialform", "composition": "ch (trocken) + cth (Blatt-/Krautteilfamilie) + Rest", "context_rule": "nur für die bezeugte chcth-Restfamilie; Herbal konkretisiert zu Blatt-/Krautgut", "status": "NEW_PRODUCTIVE_WORKING_DEFAULT"},
        {"entry": "sh+cth*", "kind": "MOIST_PREFIXED_CTH_PART_FAMILY", "working_meaning_de": "feucht markierte cth-Pflanzen-/Drogenmaterialform", "composition": "sh (feucht) + cth (Blatt-/Krautteilfamilie) + Rest", "context_rule": "nur für die bezeugte shcth-Restfamilie; Herbal konkretisiert zu Blatt-/Krautgut", "status": "NEW_PRODUCTIVE_WORKING_DEFAULT"},
        {"entry": "chcthy", "kind": "DRY_CTH_MATERIAL", "working_meaning_de": "trockene CTH-Materialform; im Herbal trockenes Blatt-/Krautgut", "composition": "ch+cth+y", "context_rule": "global CTH-Drogengut; Blattlesung nur im Herbal-Kontext", "status": "NEW_PRIMARY_WORKING_WORD__SEMANTIC_PROVISIONAL"},
        {"entry": "shcthy", "kind": "MOIST_CTH_MATERIAL", "working_meaning_de": "feuchte CTH-Materialform; im Herbal feuchtes Blatt-/Krautgut", "composition": "sh+cth+y", "context_rule": "global CTH-Drogengut; Blattlesung nur im Herbal-Kontext", "status": "NEW_PRIMARY_WORKING_WORD__SEMANTIC_PROVISIONAL"},
        {"entry": "chcthy kchol daiin", "kind": "DRY_LEAF_HOT_DRY_DEGREE_CLAUSE", "working_meaning_de": "trockenes Blattgut: heiß-trocken, Grad III", "composition": "ch+cth+y | k+ch+ol | d+a+III", "context_rule": "nur am dreifach stabilen unmittelbaren f45r.3-Span", "status": "NEW_CONCRETE_LOCAL_CLAUSE"},
        {"entry": "shol daiin shcthy", "kind": "MOIST_DEGREE_LEAF_CLAUSE", "working_meaning_de": "feuchtes Blattgut: feucht, Grad III", "composition": "sh+ol | d+a+III | sh+cth+y", "context_rule": "nur am dreifach stabilen unmittelbaren f93r.21-Span", "status": "NEW_CONCRETE_LOCAL_CLAUSE"},
        {"entry": "QUALITY_PREFIX+CTH_PART", "kind": "PREFIXED_PART_FRAME", "working_meaning_de": "qualitätsmarkiertes CTH-Pflanzen-/Drogengut", "composition": "ch|sh + cth + Rest", "context_rule": "ch=trocken und sh=feucht; einfache k/t-Gegenstücke fehlen, tchcthy bleibt Singleton", "status": "NEW_COMPOSITIONAL_FRAME"},
        {"entry": "tchcthy", "kind": "NESTED_COLD_DRY_CTH_PART", "working_meaning_de": "kalt-trockenes cth-Blatt-/Krautgut", "composition": "t+ch+cth+y", "context_rule": "ein dreifach exakter Beleg f80v.33; produktive Erweiterung erst nach Wiederholung", "status": "NEW_LOW_SINGLETON_DEFAULT"},
        {"entry": "oshctho", "kind": "WRAPPED_MOIST_CTH_PART", "working_meaning_de": "im o-Rahmen feuchte cth-Pflanzenteilform; Endung o offen", "composition": "o+sh+cth+o", "context_rule": "f37v.21 in zwei Lesern exakt, RF1b verkürzt; Außenrahmen und Endung noch offen", "status": "NEW_LOW_SINGLETON_DEFAULT"},
    ])
    return rows


def main() -> int:
    ART.mkdir(parents=True, exist_ok=True)
    pages = {row["page"] for row in read_tsv(ROOT / ALLOW_REL)}
    if "f1r" in pages or any(page.startswith("f84") for page in pages):
        raise RuntimeError("allow-list contains forbidden page")
    token_rows, token_stats = guarded_query(TOKENS_REL, pages, "page,locus,token_index,eva,section,hand")
    cross_rows, cross_stats = guarded_query(CROSS_REL, pages, "page,locus,all_three_present,all_present_exact,zl3b_clean,it2a_clean,rf1b_clean")
    cross_by_locus = {row["locus"]: row for row in cross_rows}
    raw_by_line, line_text = line_maps([dict(row) for row in token_rows])

    occurrences, reader_rows = make_occurrences(token_rows, cross_by_locus, line_text)
    inherited_bare_surfaces = {row["surface"] for row in read_tsv(ROOT / G625_CTH_REL)}
    for row in occurrences:
        row["in_inherited_cth_surface_deck"] = int(str(row["bare_counterpart_surface"]) in inherited_bare_surfaces)
    matrix = make_matrix(occurrences)
    pairs = make_pairs(matrix)
    bridges = make_boundary_bridges(pairs, cross_rows)
    outer_bridges = make_outer_boundary_bridges(cross_by_locus)
    local = make_local_contrasts(occurrences, line_text)
    slots = make_shared_slots(occurrences, raw_by_line, line_text)
    contacts = make_quality_contacts(occurrences, quality_references(), line_text)
    local_quality = make_local_quality_neighbors(occurrences, local_quality_references(), line_text)
    quality_summary = make_quality_summary(contacts, occurrences)
    repeated = make_repeated_frames(contacts)
    sections = make_section_profile(occurrences)
    factor_grid = make_factor_grid(token_rows, cross_by_locus)
    historical = make_historical_comparators()
    visual = make_inherited_visual_scope()
    cases = make_cases(contacts)
    ranking = make_ranking(matrix, quality_summary)
    dictionary = make_dictionary(read_tsv(ROOT / G630_DICT_REL))

    prefix_counts = Counter(str(row["prefix"]) for row in occurrences)
    if prefix_counts["K"] or prefix_counts["T"]:
        raise RuntimeError(f"unexpected k/t prefixed cth family changed: {prefix_counts}")

    write_tsv(ROOT / OUTPUTS["allowlist"], [{"page": page} for page in sorted(pages)], ("page",))
    write_tsv(ROOT / OUTPUTS["occurrences"], occurrences, (
        "occurrence_id", "page", "locus", "token_index", "surface", "prefix", "prefix_surface", "cth_root", "remainder",
        "bare_counterpart_surface", "section", "hand", "triple_exact_token_stable", "triple_boundary_normalized",
        "in_inherited_cth_surface_deck", "working_composition_de", "surface_line",
    ))
    write_tsv(ROOT / OUTPUTS["reader"], reader_rows, (
        "occurrence_id", "page", "locus", "token_index", "surface", "prefix", "remainder", "bare_counterpart_surface",
        "zl3b_mode", "it2a_mode", "rf1b_mode", "triple_exact_token_stable", "triple_boundary_normalized",
        "any_split_prefix_reader", "surface_line",
    ))
    write_tsv(ROOT / OUTPUTS["bridges"], bridges, (
        "bridge_id", "page", "locus", "prefix", "remainder", "fused_surface", "split_surface",
        "zl3b_mode", "it2a_mode", "rf1b_mode", "triple_boundary_normalized", "working_equivalence",
        "zl3b_line", "it2a_line", "rf1b_line",
    ))
    write_tsv(ROOT / OUTPUTS["outer_bridges"], outer_bridges, (
        "bridge_id", "page", "locus", "target_unit", "zl3b_target_span", "it2a_target_span", "rf1b_target_span",
        "support", "working_interpretation_de", "zl3b_line", "it2a_line", "rf1b_line",
    ))
    matrix_fields = ["remainder"]
    for prefix in PREFIX_ORDER:
        key = prefix.lower()
        matrix_fields.extend((f"{key}_surface", f"{key}_occurrences", f"{key}_pages", f"{key}_triple_exact"))
    matrix_fields.extend(("occupied_prefixes", "prefixed_modes", "total_occurrences"))
    write_tsv(ROOT / OUTPUTS["matrix"], matrix, matrix_fields)
    write_tsv(ROOT / OUTPUTS["pairs"], pairs, (
        "pair_id", "remainder", "prefix", "bare_surface", "prefixed_surface", "bare_occurrences", "prefixed_occurrences",
        "bare_pages", "prefixed_pages", "bare_triple_exact", "prefixed_triple_exact", "working_contrast_de", "pair_status",
    ))
    write_tsv(ROOT / OUTPUTS["local"], local, (
        "contrast_id", "page", "locus", "remainder", "left_surface", "left_prefix", "left_token_index",
        "right_surface", "right_prefix", "right_token_index", "token_distance", "both_triple_exact", "contrast_class", "surface_line",
    ))
    write_tsv(ROOT / OUTPUTS["slots"], slots, (
        "slot_id", "page", "locus", "surface", "prefix", "frame", "target_triple_exact", "working_category_de", "surface_line",
    ))
    write_tsv(ROOT / OUTPUTS["quality"], contacts, (
        "contact_id", "occurrence_id", "page", "locus", "part_surface", "part_prefix", "part_remainder", "part_token_index",
        "quality_source", "quality_surface", "quality_root", "quality_axes", "quality_token_start", "quality_token_end", "distance", "order",
        "prefix_axis_relation", "both_triple_stable", "working_part_de", "working_quality_de", "surface_line",
    ))
    write_tsv(ROOT / OUTPUTS["local_quality"], local_quality, (
        "neighbor_id", "occurrence_id", "page", "locus", "part_surface", "part_prefix", "part_remainder",
        "quality_surface", "quality_source", "quality_axes", "order", "prefix_axis_relation", "both_triple_stable",
        "working_part_de", "working_quality_de", "surface_line",
    ))
    write_tsv(ROOT / OUTPUTS["quality_summary"], quality_summary, (
        "prefix", "working_prefix_de", "part_occurrences", "part_pages", "contacts_within_three", "immediate_contacts",
        "part_occurrences_with_contact_within_three", "part_occurrences_with_immediate_contact",
        "both_triple_stable_contacts", "matching_axis_contacts", "opposite_axis_contacts", "orthogonal_axis_contacts",
        "matching_immediate", "opposite_immediate", "example_loci",
    ))
    write_tsv(ROOT / OUTPUTS["repeated"], repeated, (
        "frame_id", "part_surface", "quality_surface", "order", "surface_clause", "occurrences", "pages",
        "triple_stable_occurrences", "prefix_axis_relation", "working_reading_de", "loci",
    ))
    write_tsv(ROOT / OUTPUTS["sections"], sections, (
        "prefix", "section", "occurrences", "pages", "types", "triple_exact_occurrences", "hands", "example_surfaces",
    ))
    write_tsv(ROOT / OUTPUTS["factor_grid"], factor_grid, (
        "outer_wrapper", "quality_core", "occurrences", "types", "pages", "triple_exact_occurrences", "remainders",
        "example_surfaces", "example_loci", "working_factor_reading_de", "status",
    ))
    write_tsv(ROOT / OUTPUTS["historical"], historical, (
        "comparator_id", "date", "manuscript", "observed_formula", "structural_parallel_de", "source_url", "limit",
    ))
    write_tsv(ROOT / OUTPUTS["visual"], visual, (
        "visual_id", "page", "locus", "target_surface", "inherited_observation_de", "licensed_reading_de",
        "not_licensed_de", "source_provenance", "new_image_opened",
    ))
    write_tsv(ROOT / OUTPUTS["cases"], cases, (
        "case_id", "page", "locus", "surface_clause", "segmentation", "working_reading_de",
        "prefix_axis_relation", "reader_status", "residual_policy",
    ))
    write_tsv(ROOT / OUTPUTS["ranking"], ranking, ("rank", "model", "working_model_de", "support", "counterevidence", "disposition"))
    write_tsv(ROOT / OUTPUTS["dictionary"], dictionary, ("entry", "kind", "working_meaning_de", "composition", "context_rule", "status"))

    pair_counts = Counter(str(row["prefix"]) for row in pairs)
    reader_split = Counter(str(row["prefix"]) for row in reader_rows if int(row["any_split_prefix_reader"]))
    relation_counts = Counter(str(row["prefix_axis_relation"]) for row in contacts)
    strict_counts = Counter(str(row["prefix"]) for row in occurrences if int(row["in_inherited_cth_surface_deck"]))
    prefixed_contacts = [row for row in contacts if row["part_prefix"] != "BARE"]
    local_quality_relations = Counter(str(row["prefix_axis_relation"]) for row in local_quality)
    slot_counts = Counter(str(row["surface"]) for row in slots)
    prefix_types = {prefix: len({str(row["surface"]) for row in occurrences if row["prefix"] == prefix}) for prefix in PREFIX_ORDER}
    output_hashes = {str(path): sha256(ROOT / path) for key, path in OUTPUTS.items() if key != "result"}
    input_paths = (TOKENS_REL, CROSS_REL, ALLOW_REL, G623_VISUAL_OBS_REL, G623_VISUAL_ROLE_REL, G625_CTH_REL, G625_TERMINAL_REL, G625_VISUAL_REL, G627_AXIS_REL, G628_OL_REL, G630_EXPRESSIONS_REL, G630_DICT_REL, G630_RESULT_REL)
    result_core = {
        "schema": "GDT631_PREFIXED_CTH_QUALITY_PARTS_RESULT_V1",
        "experiment_id": "GDT631",
        "status": "CH_SH_PRODUCTIVE_CTH_PREFIX_OPPOSITION__DRY_MOIST_DEFAULT_PROVISIONAL",
        "guard": {"f1r": "EXCLUDED", "f84": "FORBIDDEN", "f84r": "FORBIDDEN", "new_image_pages": 0, "allowed_pages": len(pages), "token_query": token_stats, "cross_query": cross_stats},
        "family": {
            "occurrences": len(occurrences), "types": len({str(row["surface"]) for row in occurrences}),
            "prefix_occurrence_counts": dict(sorted(prefix_counts.items())), "prefix_type_counts": dict(sorted(prefix_types.items())),
            "strict_inherited_base_occurrence_counts": dict(sorted(strict_counts.items())),
            "extended_unpaired_occurrences": sum(not int(row["in_inherited_cth_surface_deck"]) for row in occurrences),
            "remainders": len(matrix), "type_level_bare_pairs": dict(sorted(pair_counts.items())),
            "local_same_remainder_contrasts": len(local), "reader_split_occurrences": dict(sorted(reader_split.items())),
            "cross_reader_prefix_boundary_bridges": len(bridges), "target_outer_boundary_bridges": len(outer_bridges),
            "shared_terminal_part_slot_counts": dict(sorted(slot_counts.items())),
        },
        "quality_contacts": {
            "all_cth_within_three": len(contacts), "prefixed_within_three": len(prefixed_contacts),
            "prefixed_immediate": sum(int(row["distance"]) == 1 for row in prefixed_contacts),
            "prefixed_both_triple_stable": sum(int(row["both_triple_stable"]) for row in prefixed_contacts),
            "all_relation_counts": dict(sorted(relation_counts.items())), "concrete_clauses": len(cases),
            "repeated_clause_frames": len(repeated),
        },
        "adjacent_quality_rivals": {"neighbors": len(local_quality), "relation_counts": dict(sorted(local_quality_relations.items())), "sharpest_warning": "f24v.8 kochky chcthy shol sain"},
        "extended_factor_grid": {"occupied_cells": len(factor_grid), "tchcthy": "single triple-exact nested cold-dry lead", "oshctho": "single two-reader-exact wrapped moist lead"},
        "working_composition": {
            "chcthy": "ch+cth+y = trockenes Blattgut/Blattdroge",
            "shcthy": "sh+cth+y = feuchtes Blattgut/Blattdroge",
            "scope": "bezeugte chcth/shcth-Restfamilie",
            "unlicensed": "kcth/tcth sind im freigegebenen Panel unbelegt und werden nicht erfunden",
        },
        "working_dictionary": {"entries": len(dictionary), "inherited_v7": len(dictionary) - 9, "new_v8": 9},
        "claim_boundary": "The same inherited cth remainder is repeatedly realized bare and with ch or sh; a same-span sh cthey versus shcthey reader bridge confirms that this is a real boundary option, while simple k and t counterparts are absent. Under the inherited exploratory key this promotes chcth* and shcth* structurally and retains dry/moist as the best provisional meanings. Herbal chcthy/shcthy read as dry/moist leaf or herb material; elsewhere the safer concrete default is dry/moist CTH drug material. Immediate degree contacts support this, while adjacent shol at f24v.8 and f20v.3 preserves a real semantic rival. No phonetics, language, species identity, or manuscript solution is claimed.",
        "inputs": {str(path): sha256(ROOT / path) for path in input_paths}, "outputs": output_hashes,
    }
    result = {**result_core, "content_sha256": canonical_hash(result_core)}
    (ROOT / OUTPUTS["result"]).write_text(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"GDT631 built: family={len(occurrences)} strict={dict(strict_counts)} prefixes={dict(prefix_counts)} pairs={dict(pair_counts)} bridges={len(bridges)} slots={len(slots)} degree_contacts={len(prefixed_contacts)} local_quality={len(local_quality)} cases={len(cases)} dictionary={len(dictionary)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
