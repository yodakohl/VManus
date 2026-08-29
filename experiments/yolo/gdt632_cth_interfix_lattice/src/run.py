#!/usr/bin/env python3
"""Build GDT632: the ch/sh by NONE/e/o/eo by cth remainder lattice."""

from __future__ import annotations

import csv
import hashlib
import importlib.util
import json
import re
import sys
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
BASE_REL = Path("experiments/yolo/gdt632_cth_interfix_lattice")
ART = ROOT / BASE_REL / "artifacts"
G631_BASE = Path("experiments/yolo/gdt631_prefixed_cth_quality_parts")
G631_RUN_REL = G631_BASE / "src/run.py"
G631_RESULT_REL = G631_BASE / "artifacts/RESULT.json"
G631_DICT_REL = G631_BASE / "artifacts/WORKING_DICTIONARY_V8.tsv"
G631_VISUAL_REL = G631_BASE / "artifacts/INHERITED_VISUAL_SCOPE.tsv"
ALLOW_REL = G631_BASE / "artifacts/PAGE_ALLOWLIST.tsv"
G625_CTH_REL = Path("experiments/yolo/gdt625_ordered_quality_state_transitions/artifacts/CTH_ROOT_FAMILY.tsv")
TOKENS_REL = Path("transcription/voynich_zl3b_tokens.tsv")
CROSS_REL = Path("transcription/voynich_cross_transcription_lines.tsv")

spec = importlib.util.spec_from_file_location("gdt631_builder", ROOT / G631_RUN_REL)
if spec is None or spec.loader is None:
    raise RuntimeError("cannot load GDT631 builder helpers")
g631 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(g631)

OUTPUTS = {
    "allowlist": BASE_REL / "artifacts/PAGE_ALLOWLIST.tsv",
    "occurrences": BASE_REL / "artifacts/INTERFIX_FAMILY_OCCURRENCES.tsv",
    "reader": BASE_REL / "artifacts/CROSS_READER_INTERFIX_REALIZATIONS.tsv",
    "bridges": BASE_REL / "artifacts/CROSS_READER_INTERFIX_BOUNDARY_BRIDGES.tsv",
    "separated": BASE_REL / "artifacts/ALL_READER_SEPARATED_SHELL_CTH_SPANS.tsv",
    "expression_populations": BASE_REL / "artifacts/EXPRESSION_POPULATION_SUMMARY.tsv",
    "bridge_summary": BASE_REL / "artifacts/BOUNDARY_ORIENTATION_SUMMARY.tsv",
    "boundary_null": BASE_REL / "artifacts/ALTERNATIVE_INTERNAL_BOUNDARY_NULL.tsv",
    "outer_bridges": BASE_REL / "artifacts/OUTER_FAMILY_BOUNDARY_BRIDGES.tsv",
    "shells": BASE_REL / "artifacts/LEFT_QUALITY_SHELLS.tsv",
    "head_summary": BASE_REL / "artifacts/INNER_CTH_HEAD_PREFIX_SUMMARY.tsv",
    "head_matrix": BASE_REL / "artifacts/INNER_CTH_HEAD_REMAINDER_MATRIX.tsv",
    "hierarchy": BASE_REL / "artifacts/HIERARCHICAL_E_O_BASE_COVERAGE.tsv",
    "order_control": BASE_REL / "artifacts/E_O_ORDER_CONTROL.tsv",
    "reader_order_control": BASE_REL / "artifacts/CROSS_READER_E_O_HEAD_CONTROL.tsv",
    "out_of_lattice": BASE_REL / "artifacts/OUT_OF_LATTICE_Q_CTH_FORMS.tsv",
    "matrix": BASE_REL / "artifacts/INTERFIX_REMAINDER_MATRIX.tsv",
    "pairs": BASE_REL / "artifacts/SHARED_REMAINDER_PAIRS.tsv",
    "summary": BASE_REL / "artifacts/INTERFIX_CELL_SUMMARY.tsv",
    "sections": BASE_REL / "artifacts/INTERFIX_SECTION_PROFILE.tsv",
    "registers": BASE_REL / "artifacts/INTERFIX_REGISTER_PROFILE.tsv",
    "coexistence": BASE_REL / "artifacts/INTERFIX_PAGE_COEXISTENCE.tsv",
    "visual": BASE_REL / "artifacts/INHERITED_VISUAL_INTERFIX_SCOPE.tsv",
    "historical": BASE_REL / "artifacts/HISTORICAL_HYBRID_COMPARATORS.tsv",
    "contexts": BASE_REL / "artifacts/FIXED_CONTEXT_PARADIGMS.tsv",
    "one_sided_contexts": BASE_REL / "artifacts/ONE_SIDED_CONTEXT_PARADIGMS.tsv",
    "slots": BASE_REL / "artifacts/SHARED_CATEGORY_SLOTS.tsv",
    "quality": BASE_REL / "artifacts/INTERFIX_QUALITY_DEGREE_CONTACTS.tsv",
    "quality_summary": BASE_REL / "artifacts/INTERFIX_QUALITY_SUMMARY.tsv",
    "local_quality": BASE_REL / "artifacts/INTERFIX_LOCAL_QUALITY_NEIGHBORS.tsv",
    "repeated": BASE_REL / "artifacts/REPEATED_INTERFIX_CLAUSE_FRAMES.tsv",
    "cases": BASE_REL / "artifacts/CONCRETE_CLAUSES_V4.tsv",
    "ranking": BASE_REL / "artifacts/INTERFIX_ROLE_RANKING.tsv",
    "dictionary": BASE_REL / "artifacts/WORKING_DICTIONARY_V9.tsv",
    "result": BASE_REL / "artifacts/RESULT.json",
}

Q_ORDER = ("CH", "SH")
M_ORDER = ("NONE", "E", "O", "EO")
Q_SURFACE = {"CH": "ch", "SH": "sh"}
M_SURFACE = {"NONE": "", "E": "e", "O": "o", "EO": "eo"}
FAMILY_RE = re.compile(r"^(ch|sh)(eo|e|o)?cth(.*)$")
HEAD_RE = re.compile(r"^(eo|e|o)?cth(.*)$")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_hash(value: object) -> str:
    raw = json.dumps(value, sort_keys=True, ensure_ascii=True, separators=(",", ":")).encode()
    return hashlib.sha256(raw).hexdigest()


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: list[dict[str, object]], fields: Iterable[str]) -> None:
    g631.write_tsv(path, rows, fields)


def parse_family(surface: str) -> tuple[str, str, str] | None:
    match = FAMILY_RE.fullmatch(surface)
    if match is None:
        return None
    return match.group(1).upper(), (match.group(2) or "NONE").upper(), match.group(3) or "BARE"


def surface_for(q: str, interfix: str, remainder: str) -> str:
    return Q_SURFACE[q] + M_SURFACE[interfix] + "cth" + ("" if remainder == "BARE" else remainder)


def base_for(interfix: str, remainder: str) -> str:
    return M_SURFACE[interfix] + "cth" + ("" if remainder == "BARE" else remainder)


def material_reading(q: str, remainder: str, section: str) -> str:
    quality = "trockene" if q == "CH" else "feuchte"
    if remainder == "y" and section == "H":
        return f"{quality} Blatt-/Krautmaterialform"
    if remainder == "y":
        return f"{quality} CTH-Pflanzen-/Drogenmaterialform"
    return f"{quality} CTH-Materialform; Rest {remainder} offen"


def make_occurrences(
    token_rows: list[dict[str, str]], cross_by_locus: dict[str, dict[str, str]],
    line_text: dict[str, str], inherited_bases: set[str], by_line: dict[str, list[dict[str, object]]],
) -> list[dict[str, object]]:
    ordinal: Counter[tuple[str, str]] = Counter()
    rows: list[dict[str, object]] = []
    positions = {(str(token["locus"]), int(token["token_index"])): (index, len(line)) for locus, line in by_line.items() for index, token in enumerate(line)}
    for source in sorted(token_rows, key=g631.token_sort_key):
        parsed = parse_family(source["eva"])
        if parsed is None:
            continue
        q, interfix, remainder = parsed
        ordinal[source["locus"], source["eva"]] += 1
        cross = cross_by_locus[source["locus"]]
        exact_caps = [cross[field].split().count(source["eva"]) for field in ("zl3b_clean", "it2a_clean", "rf1b_clean")]
        normalized_caps = [g631.concatenated_span_count(cross[field].split(), source["eva"]) for field in ("zl3b_clean", "it2a_clean", "rf1b_clean")]
        line_index, line_length = positions[source["locus"], int(source["token_index"])]
        line = by_line[source["locus"]]
        rows.append({
            "occurrence_id": "", "page": source["page"], "locus": source["locus"], "token_index": int(source["token_index"]),
            "surface": source["eva"], "quality_prefix": q, "interfix": interfix, "remainder": remainder,
            "bare_cth_surface": "cth" + ("" if remainder == "BARE" else remainder),
            "in_inherited_cth_surface_deck": int(("cth" + ("" if remainder == "BARE" else remainder)) in inherited_bases),
            "triple_exact_token_stable": int(ordinal[source["locus"], source["eva"]] <= min(exact_caps)),
            "triple_boundary_normalized": int(ordinal[source["locus"], source["eva"]] <= min(normalized_caps)),
            "left_surface": str(line[line_index - 1]["eva"]) if line_index else "<START>",
            "right_surface": str(line[line_index + 1]["eva"]) if line_index + 1 < line_length else "<END>",
            "position": "FIRST" if line_index == 0 else "LAST" if line_index + 1 == line_length else "MIDDLE",
            "section": source["section"], "language": source["language"], "hand": source["hand"],
            "working_material_de": material_reading(q, remainder, source["section"]),
            "interfix_semantics": "OPEN", "surface_line": line_text[source["locus"]],
        })
    for index, row in enumerate(rows, 1):
        row["occurrence_id"] = f"G632-O{index:04d}"
    return rows


def reader_mode(words: list[str], q: str, interfix: str, remainder: str) -> str:
    target = surface_for(q, interfix, remainder)
    q_s, m_s = Q_SURFACE[q], M_SURFACE[interfix]
    bare = "cth" + ("" if remainder == "BARE" else remainder)
    modes: list[str] = []
    if target in words:
        modes.append("FUSED")
    split_q_right = m_s + bare
    if any(left == q_s and right == split_q_right for left, right in zip(words, words[1:])):
        modes.append("SPLIT_Q")
    if interfix != "NONE" and any(left == q_s + m_s and right == bare for left, right in zip(words, words[1:])):
        modes.append("SPLIT_QM")
    if interfix != "NONE" and any(words[index:index + 3] == [q_s, m_s, bare] for index in range(max(0, len(words) - 2))):
        modes.append("SPLIT_ALL")
    if not modes and g631.concatenated_span_count(words, target):
        modes.append("OTHER_BOUNDARY")
    return "+".join(modes) if modes else "ABSENT_OR_DIFFERENT"


def target_realizations(words: list[str], target: str) -> list[str]:
    """Return every one-to-four-token realization whose concatenation is target."""
    found: list[str] = []
    for start in range(len(words)):
        joined = ""
        for stop in range(start, min(len(words), start + 4)):
            joined += words[stop]
            if joined == target:
                found.append(" | ".join(words[start:stop + 1]))
                break
            if len(joined) >= len(target):
                break
    return found


def target_realization_spans(words: list[str], target: str) -> list[tuple[int, int]]:
    found: list[tuple[int, int]] = []
    for start in range(len(words)):
        joined = ""
        for stop in range(start, min(len(words), start + 4)):
            joined += words[stop]
            if joined == target:
                found.append((start, stop + 1))
                break
            if len(joined) >= len(target):
                break
    return found


def classify_bridge(modes: dict[str, str]) -> tuple[str, str, int]:
    if any("FUSED" in mode and "SPLIT" in mode for mode in modes.values()):
        return "MULTIPLE_TARGETS_SAME_LINE", "LINE_LEVEL_ONLY", 0
    if any("OTHER_BOUNDARY" in mode for mode in modes.values()):
        return "OUTER_REMAINDER_BOUNDARY", "DIRECT_OTHER_BOUNDARY", 0
    if any("SPLIT_QM" in mode for mode in modes.values()):
        return "LEFT_SHELL_TO_CTH_BOUNDARY", "DIRECT_ONE_TARGET_SPAN", 1
    if any("SPLIT_Q" in mode for mode in modes.values()):
        return "QUALITY_PREFIX_TO_CTH_BOUNDARY", "DIRECT_ONE_TARGET_SPAN", 1
    if any("SPLIT_ALL" in mode for mode in modes.values()):
        return "FULLY_SEPARATED_Q_M_CTH", "DIRECT_ONE_TARGET_SPAN", 1
    return "OTHER_READER_BOUNDARY", "DIRECT_OTHER_BOUNDARY", 0


def make_reader_rows(occurrences: list[dict[str, object]], cross_by_locus: dict[str, dict[str, str]]) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for source in occurrences:
        cross = cross_by_locus[str(source["locus"])]
        modes = {reader: reader_mode(cross[field].split(), str(source["quality_prefix"]), str(source["interfix"]), str(source["remainder"])) for reader, field in (("ZL3b", "zl3b_clean"), ("IT2a", "it2a_clean"), ("RF1b", "rf1b_clean"))}
        rows.append({
            "occurrence_id": source["occurrence_id"], "page": source["page"], "locus": source["locus"], "surface": source["surface"],
            "quality_prefix": source["quality_prefix"], "interfix": source["interfix"], "remainder": source["remainder"],
            "zl3b_mode": modes["ZL3b"], "it2a_mode": modes["IT2a"], "rf1b_mode": modes["RF1b"],
            "triple_exact_token_stable": source["triple_exact_token_stable"],
            "triple_boundary_normalized": source["triple_boundary_normalized"],
            "any_internal_split_reader": int(any("SPLIT" in mode for mode in modes.values())),
        })
    return rows


def make_bridges(occurrences: list[dict[str, object]], inherited_bases: set[str], cross_rows: list[dict[str, str]]) -> list[dict[str, object]]:
    remainders = {str(row["remainder"]) for row in occurrences}
    remainders.update(surface[3:] or "BARE" for surface in inherited_bases if surface.startswith("cth"))
    cells = [(q, interfix, remainder) for remainder in sorted(remainders) for q in Q_ORDER for interfix in M_ORDER]
    candidate_targets = {(q, interfix): sorted((surface_for(q, interfix, remainder) for remainder in remainders), key=len) for q in Q_ORDER for interfix in M_ORDER}
    rows: list[dict[str, object]] = []
    for cross in cross_rows:
        for q, interfix, remainder in cells:
            modes = {reader: reader_mode(cross[field].split(), q, interfix, remainder) for reader, field in (("ZL3b", "zl3b_clean"), ("IT2a", "it2a_clean"), ("RF1b", "rf1b_clean"))}
            if any(mode == "ABSENT_OR_DIFFERENT" for mode in modes.values()):
                continue
            if len(set(modes.values())) == 1 and not any("+" in mode for mode in modes.values()):
                continue
            target = surface_for(q, interfix, remainder)
            realizations = {
                reader: target_realizations(cross[field].split(), target)
                for reader, field in (("ZL3b", "zl3b_clean"), ("IT2a", "it2a_clean"), ("RF1b", "rf1b_clean"))
            }
            bridge_class, span_status, diagnostic = classify_bridge(modes)
            if diagnostic:
                for longer in candidate_targets[q, interfix]:
                    if len(longer) <= len(target) or not longer.startswith(target):
                        continue
                    overlap = False
                    for field in ("zl3b_clean", "it2a_clean", "rf1b_clean"):
                        words = cross[field].split()
                        short_spans = target_realization_spans(words, target)
                        long_spans = target_realization_spans(words, longer)
                        if any(short_start == long_start and short_stop <= long_stop for short_start, short_stop in short_spans for long_start, long_stop in long_spans):
                            overlap = True
                            break
                    if overlap:
                        bridge_class, span_status, diagnostic = "LEFT_SHELL_TO_CTH__RIGHT_EDGE_OVERLAP", "LEFT_BOUNDARY_VALID__RIGHT_EDGE_AMBIGUOUS", 0
                        break
            rows.append({
                "bridge_id": "", "page": cross["page"], "locus": cross["locus"], "surface": target,
                "quality_prefix": q, "interfix": interfix, "remainder": remainder,
                "bridge_class": bridge_class, "span_status": span_status, "diagnostic_internal_boundary": diagnostic,
                "left_shell_cth_boundary_visible": int(bridge_class in ("LEFT_SHELL_TO_CTH_BOUNDARY", "LEFT_SHELL_TO_CTH__RIGHT_EDGE_OVERLAP")),
                "observed_realizations": " || ".join(sorted({item for values in realizations.values() for item in values})),
                "zl3b_target_spans": len(realizations["ZL3b"]), "it2a_target_spans": len(realizations["IT2a"]),
                "rf1b_target_spans": len(realizations["RF1b"]),
                "zl3b_mode": modes["ZL3b"], "it2a_mode": modes["IT2a"], "rf1b_mode": modes["RF1b"],
                "zl3b_line": cross["zl3b_clean"], "it2a_line": cross["it2a_clean"], "rf1b_line": cross["rf1b_clean"],
            })
    rows.sort(key=lambda row: (str(row["page"]), g631.line_number(str(row["locus"])), str(row["surface"])))
    for index, row in enumerate(rows, 1):
        row["bridge_id"] = f"G632-B{index:03d}"
    return rows


def make_all_reader_separated(occurrences: list[dict[str, object]], inherited_bases: set[str], cross_rows: list[dict[str, str]]) -> list[dict[str, object]]:
    """Find shell|CTH spellings present as two tokens in all three readers."""
    fused_counts = Counter((str(row["quality_prefix"]), str(row["interfix"]), str(row["remainder"])) for row in occurrences)
    remainders = sorted({surface[3:] or "BARE" for surface in inherited_bases if surface.startswith("cth")})
    cells = [(q, interfix, remainder) for remainder in remainders for q in Q_ORDER for interfix in M_ORDER]
    rows: list[dict[str, object]] = []
    for cross in cross_rows:
        for q, interfix, remainder in cells:
            shell = Q_SURFACE[q] + M_SURFACE[interfix]
            bare = "cth" + ("" if remainder == "BARE" else remainder)
            fields = ("zl3b_clean", "it2a_clean", "rf1b_clean")
            present = []
            for field in fields:
                words = cross[field].split()
                present.append(any(left == shell and right == bare for left, right in zip(words, words[1:])))
            if not all(present):
                continue
            counterpart_count = fused_counts[q, interfix, remainder]
            rows.append({
                "span_id": "", "page": cross["page"], "locus": cross["locus"], "quality_prefix": q,
                "interfix": interfix, "remainder": remainder, "left_shell": shell, "cth_surface": bare,
                "separated_surface": f"{shell} | {bare}", "fused_counterpart": surface_for(q, interfix, remainder),
                "fused_counterpart_occurrences_elsewhere": counterpart_count,
                "evidence_role": "ALL_THREE_READERS_SEPARATE__FUSED_COUNTERPART_ELSEWHERE" if counterpart_count else "ALL_THREE_READERS_SEPARATE__SPLIT_ONLY_PREDICTED_CELL",
                "zl3b_line": cross["zl3b_clean"], "it2a_line": cross["it2a_clean"], "rf1b_line": cross["rf1b_clean"],
            })
    rows.sort(key=lambda row: (str(row["page"]), g631.line_number(str(row["locus"])), str(row["separated_surface"])))
    for index, row in enumerate(rows, 1):
        row["span_id"] = f"G632-SB{index:03d}"
    return rows


def make_bridge_summary(bridges: list[dict[str, object]], separated: list[dict[str, object]]) -> list[dict[str, object]]:
    direct_shell = [row for row in bridges if row["bridge_class"] == "LEFT_SHELL_TO_CTH_BOUNDARY" and int(row["diagnostic_internal_boundary"])]
    direct_q = [row for row in bridges if row["bridge_class"] == "QUALITY_PREFIX_TO_CTH_BOUNDARY" and int(row["diagnostic_internal_boundary"])]
    mixed = [row for row in bridges if row["bridge_class"] == "MULTIPLE_TARGETS_SAME_LINE"]
    outer = [row for row in bridges if row["bridge_class"] == "OUTER_REMAINDER_BOUNDARY"]
    overlapping = [row for row in bridges if row["bridge_class"] == "LEFT_SHELL_TO_CTH__RIGHT_EDGE_OVERLAP"]
    nonempty_q_splits = [row for row in direct_q if row["interfix"] != "NONE"]
    return [
        {"orientation": "LEFT_SHELL|CTH", "alternate_reader_spans": len(direct_shell), "all_reader_separated_spans": len(separated), "total_diagnostic_spans": len(direct_shell) + len(separated), "loci": "|".join(str(row["locus"]) for row in (*direct_shell, *separated)), "interpretation_de": "Die sichtbare Grenze liegt nach ch/che/cho/cheo bzw. sh/she/sho/sheo; e/o gehören links zum Qualitätsblock."},
        {"orientation": "QUALITY_PREFIX|M_CTH", "alternate_reader_spans": len(nonempty_q_splits), "all_reader_separated_spans": 0, "total_diagnostic_spans": len(nonempty_q_splits), "loci": "|".join(str(row["locus"]) for row in nonempty_q_splits), "interpretation_de": "Für nichtleeres e/o/eo wurde keine Grenze ch|octh oder sh|ecth gefunden."},
        {"orientation": "QUALITY_PREFIX|CTH_DIRECT", "alternate_reader_spans": len(direct_q) - len(nonempty_q_splits), "all_reader_separated_spans": 0, "total_diagnostic_spans": len(direct_q) - len(nonempty_q_splits), "loci": "|".join(str(row["locus"]) for row in direct_q if row["interfix"] == "NONE"), "interpretation_de": "Die direkte Reihe besitzt die einzelne Leserbrücke sh|cthey ↔ shcthey."},
        {"orientation": "LEFT_SHELL|CTH_RIGHT_EDGE_AMBIGUOUS", "alternate_reader_spans": len(overlapping), "all_reader_separated_spans": 0, "total_diagnostic_spans": 0, "loci": "|".join(str(row["locus"]) for row in overlapping), "interpretation_de": "Die linke Shell|CTH-Grenze ist sichtbar; nur der rechte Rand überlappt mit einem längeren Familienziel, daher nicht im konservativen Zwölfer gezählt."},
        {"orientation": "NON_DIAGNOSTIC_WARNINGS", "alternate_reader_spans": len(mixed) + len(outer), "all_reader_separated_spans": 0, "total_diagnostic_spans": 0, "loci": "|".join(str(row["locus"]) for row in (*mixed, *outer)), "interpretation_de": "Mehrfachziele derselben Zeile und äußere Restgrenzen werden nicht als interne Segmentierung gezählt."},
    ]


def make_expression_population_summary(
    occurrences: list[dict[str, object]], separated: list[dict[str, object]], bridges: list[dict[str, object]],
) -> list[dict[str, object]]:
    fused = [(str(row["page"]), str(row["locus"]), str(row["surface"]), str(row["remainder"])) for row in occurrences]
    all_reader = [(str(row["page"]), str(row["locus"]), str(row["fused_counterpart"]), str(row["remainder"])) for row in separated]
    conservative_alt = [
        (str(row["page"]), str(row["locus"]), str(row["surface"]), str(row["remainder"]))
        for row in bridges
        if int(row["diagnostic_internal_boundary"]) and "SPLIT" in str(row["zl3b_mode"]) and "FUSED" not in str(row["zl3b_mode"])
    ]
    ambiguous_alt = [
        (str(row["page"]), str(row["locus"]), str(row["surface"]), str(row["remainder"]))
        for row in bridges
        if row["bridge_class"] == "LEFT_SHELL_TO_CTH__RIGHT_EDGE_OVERLAP" and "SPLIT" in str(row["zl3b_mode"])
    ]
    populations = (
        ("FUSED_ZL", fused, "255 fusionierte ZL-Token"),
        ("FUSED_PLUS_ALL_READER_SEPARATED", [*fused, *all_reader], "ergänzt sieben in allen Lesern getrennte ZL-Ausdrücke"),
        ("CONSERVATIVE_BOUNDARY_NORMALIZED", [*fused, *all_reader, *conservative_alt], "ergänzt drei eindeutige ZL-split/anderer-Leser-fused Ausdrücke"),
        ("INCLUSIVE_LEFT_BOUNDARY", [*fused, *all_reader, *conservative_alt, *ambiguous_alt], "ergänzt f21r.7 mit sicherer linker und überlappender rechter Grenze"),
    )
    rows: list[dict[str, object]] = []
    prior_count = 0
    for population, items, description in populations:
        rows.append({
            "population": population, "occurrences": len(items), "types": len({item[2] for item in items}),
            "pages": len({item[0] for item in items}), "remainders": len({item[3] for item in items}),
            "added_occurrences": len(items) - prior_count, "added_loci": "|".join(item[1] for item in items[prior_count:]),
            "definition_de": description,
        })
        prior_count = len(items)
    return rows


def make_alternative_boundary_null(cross_rows: list[dict[str, str]]) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    definitions = (
        ("QUALITY|M_CTH", "ch/sh | e/o/eo+cth+Rest"),
        ("QUALITY|M|CTH", "ch/sh | e/o/eo | cth+Rest"),
    )
    for pattern, display in definitions:
        counts = Counter()
        loci: dict[str, set[str]] = defaultdict(set)
        examples: dict[str, list[str]] = defaultdict(list)
        for source in cross_rows:
            for reader, field in (("ZL3b", "zl3b_clean"), ("IT2a", "it2a_clean"), ("RF1b", "rf1b_clean")):
                words = source[field].split()
                hits = 0
                if pattern == "QUALITY|M_CTH":
                    hits = sum(left in ("ch", "sh") and re.fullmatch(r"(?:eo|e|o)cth.*", right) is not None for left, right in zip(words, words[1:]))
                else:
                    hits = sum(words[index] in ("ch", "sh") and words[index + 1] in ("e", "o", "eo") and words[index + 2].startswith("cth") for index in range(max(0, len(words) - 2)))
                if hits:
                    counts[reader] += hits
                    loci[reader].add(source["locus"])
                    if len(examples[reader]) < 3:
                        examples[reader].append(source[field])
        rows.append({
            "alternative_boundary": pattern, "display": display,
            "zl3b_occurrences": counts["ZL3b"], "it2a_occurrences": counts["IT2a"], "rf1b_occurrences": counts["RF1b"],
            "any_reader_occurrences": sum(counts.values()), "loci": "|".join(sorted(set().union(*loci.values()))) if loci else "",
            "examples": " || ".join(item for values in examples.values() for item in values),
            "disposition_de": "Im vollständigen guarded Leserpanel nicht beobachtet; die Gegenrichtung bleibt eine Nullzelle.",
        })
    return rows


def make_outer_bridges(occurrences: list[dict[str, object]], cross_rows: list[dict[str, str]]) -> list[dict[str, object]]:
    targets = sorted({str(row["surface"]) for row in occurrences}, key=lambda value: (-len(value), value))
    found: dict[tuple[str, str, str, str, str], dict[str, object]] = {}
    for source in cross_rows:
        words_by_reader = {reader: source[field].split() for reader, field in (("ZL3b", "zl3b_clean"), ("IT2a", "it2a_clean"), ("RF1b", "rf1b_clean"))}
        for target in targets:
            unions: set[tuple[str, str, str]] = set()
            for words in words_by_reader.values():
                for index, word in enumerate(words):
                    if word != target:
                        continue
                    if index:
                        unions.add((words[index - 1] + target, "LEFT", words[index - 1]))
                    if index + 1 < len(words):
                        unions.add((target + words[index + 1], "RIGHT", words[index + 1]))
            for union, side, external in unions:
                modes: dict[str, str] = {}
                for reader, words in words_by_reader.items():
                    values = []
                    if union in words:
                        values.append("FUSED")
                    pair = [external, target] if side == "LEFT" else [target, external]
                    if any(words[index:index + 2] == pair for index in range(max(0, len(words) - 1))):
                        values.append("SPLIT")
                    modes[reader] = "+".join(values) if values else "ABSENT_OR_DIFFERENT"
                if not any("FUSED" in mode for mode in modes.values()) or not any("SPLIT" in mode for mode in modes.values()):
                    continue
                key = (source["locus"], target, union, side, external)
                found[key] = {
                    "bridge_id": "", "page": source["page"], "locus": source["locus"], "family_surface": target,
                    "combined_surface": union, "boundary_side": side, "external_surface": external,
                    "zl3b_mode": modes["ZL3b"], "it2a_mode": modes["IT2a"], "rf1b_mode": modes["RF1b"],
                    "reader_scope": "TRIPLE_BOUNDARY_NORMALIZED" if all(mode != "ABSENT_OR_DIFFERENT" for mode in modes.values()) else "PAIRWISE_ONLY",
                    "zl3b_line": source["zl3b_clean"], "it2a_line": source["it2a_clean"], "rf1b_line": source["rf1b_clean"],
                }
    rows = sorted(found.values(), key=lambda row: (str(row["page"]), g631.line_number(str(row["locus"])), str(row["combined_surface"])))
    for index, row in enumerate(rows, 1):
        row["bridge_id"] = f"G632-OB{index:03d}"
    return rows


def make_left_shells(occurrences: list[dict[str, object]], bridges: list[dict[str, object]], separated: list[dict[str, object]]) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for q in Q_ORDER:
        for interfix in M_ORDER:
            selected = [row for row in occurrences if row["quality_prefix"] == q and row["interfix"] == interfix]
            direct = [row for row in bridges if row["quality_prefix"] == q and row["interfix"] == interfix and int(row["diagnostic_internal_boundary"])]
            universal = [row for row in separated if row["quality_prefix"] == q and row["interfix"] == interfix]
            shell = Q_SURFACE[q] + M_SURFACE[interfix]
            rows.append({
                "quality_prefix": q, "interfix": interfix, "left_shell": shell, "fused_occurrences": len(selected),
                "fused_types": len({str(row["surface"]) for row in selected}), "pages": len({str(row["page"]) for row in selected}),
                "direct_reader_boundary_spans": len(direct), "all_reader_separated_spans": len(universal),
                "observed_shell_cth_boundary": int(bool(direct or universal)),
                "working_shell_de": ("orthographischer linker Block mit provisorisch trockenem" if q == "CH" else "orthographischer linker Block mit provisorisch feuchtem") + f" ch/sh-Kern; {interfix.lower()}-Oberflächenreihe",
                "interfix_disposition": "direkte Reihe" if interfix == "NONE" else ("inneres o+CTH-Kopfglied; Lexik OPEN" if interfix == "O" else "abhängige/zusammengesetzte Formklasse; Lexik OPEN"),
            })
    return rows


def make_inner_head_rows(
    token_rows: list[dict[str, str]], cross_by_locus: dict[str, dict[str, str]], inherited_bases: set[str],
) -> tuple[list[dict[str, object]], list[dict[str, object]], list[dict[str, object]]]:
    ordinal: Counter[tuple[str, str]] = Counter()
    heads: list[dict[str, object]] = []
    for source in sorted(token_rows, key=g631.token_sort_key):
        match = HEAD_RE.fullmatch(source["eva"])
        if match is None:
            continue
        head_prefix = (match.group(1) or "NONE").upper()
        remainder = match.group(2) or "BARE"
        ordinal[source["locus"], source["eva"]] += 1
        cross = cross_by_locus[source["locus"]]
        exact_caps = [cross[field].split().count(source["eva"]) for field in ("zl3b_clean", "it2a_clean", "rf1b_clean")]
        heads.append({
            "page": source["page"], "locus": source["locus"], "surface": source["eva"], "head_prefix": head_prefix,
            "remainder": remainder, "triple_exact_token_stable": int(ordinal[source["locus"], source["eva"]] <= min(exact_caps)),
            "bare_cth_counterpart": "cth" + ("" if remainder == "BARE" else remainder),
            "bare_cth_counterpart_published": int(("cth" + ("" if remainder == "BARE" else remainder)) in inherited_bases),
            "section": source["section"], "language": source["language"], "hand": source["hand"],
        })
    summary: list[dict[str, object]] = []
    for prefix in M_ORDER:
        selected = [row for row in heads if row["head_prefix"] == prefix]
        summary.append({
            "head_prefix": prefix, "occurrences": len(selected), "types": len({str(row["surface"]) for row in selected}),
            "remainders": len({str(row["remainder"]) for row in selected}), "pages": len({str(row["page"]) for row in selected}),
            "triple_exact_occurrences": sum(int(row["triple_exact_token_stable"]) for row in selected),
            "occurrences_with_published_bare_cth_counterpart": sum(int(row["bare_cth_counterpart_published"]) for row in selected),
            "working_role_de": {
                "NONE": "nackter CTH-Pflanzen-/Drogenmaterialkopf",
                "E": "nicht als nackter Kopf belegt",
                "O": "o-gerahmter innerer CTH-Materialkopf",
                "EO": "nicht als nackter Kopf belegt",
            }[prefix],
        })
    grouped: dict[tuple[str, str], list[dict[str, object]]] = defaultdict(list)
    for row in heads:
        grouped[str(row["remainder"]), str(row["head_prefix"])].append(row)
    remainders = sorted({surface[3:] or "BARE" for surface in inherited_bases if surface.startswith("cth")} | {key[0] for key in grouped})
    matrix: list[dict[str, object]] = []
    for remainder in remainders:
        row: dict[str, object] = {"remainder": remainder}
        for prefix in M_ORDER:
            selected = grouped.get((remainder, prefix), [])
            surface = M_SURFACE[prefix] + "cth" + ("" if remainder == "BARE" else remainder)
            row[f"{prefix.lower()}_surface"] = surface
            row[f"{prefix.lower()}_occurrences"] = len(selected)
            row[f"{prefix.lower()}_pages"] = len({str(item["page"]) for item in selected})
            row[f"{prefix.lower()}_triple_exact"] = sum(int(item["triple_exact_token_stable"]) for item in selected)
        row["published_bare_cth_remainder"] = int(("cth" + ("" if remainder == "BARE" else remainder)) in inherited_bases)
        matrix.append(row)
    return heads, summary, matrix


def make_hierarchical_coverage(
    occurrences: list[dict[str, object]], heads: list[dict[str, object]], separated: list[dict[str, object]], bridges: list[dict[str, object]],
) -> list[dict[str, object]]:
    head_counts = Counter(str(row["surface"]) for row in heads)
    head_pages: dict[str, set[str]] = defaultdict(set)
    for row in heads:
        head_pages[str(row["surface"])].add(str(row["page"]))
    normalized_additions: list[dict[str, object]] = [
        {"page": row["page"], "surface": row["fused_counterpart"], "quality_prefix": row["quality_prefix"], "interfix": row["interfix"], "remainder": row["remainder"]}
        for row in separated
    ]
    normalized_additions.extend(
        {"page": row["page"], "surface": row["surface"], "quality_prefix": row["quality_prefix"], "interfix": row["interfix"], "remainder": row["remainder"]}
        for row in bridges
        if "SPLIT" in str(row["zl3b_mode"]) and "FUSED" not in str(row["zl3b_mode"])
        and (int(row["diagnostic_internal_boundary"]) or row["bridge_class"] == "LEFT_SHELL_TO_CTH__RIGHT_EDGE_OVERLAP")
    )
    populations = (("FUSED_ONLY", occurrences), ("INCLUSIVE_BOUNDARY_NORMALIZED", [*occurrences, *normalized_additions]))
    rows: list[dict[str, object]] = []
    for population, population_rows in populations:
        for q in Q_ORDER:
          for interfix in M_ORDER:
            selected = [row for row in population_rows if row["quality_prefix"] == q and row["interfix"] == interfix]
            e_slot = int(interfix in ("E", "EO"))
            o_slot = int(interfix in ("O", "EO"))
            bases = []
            for source in selected:
                remainder = str(source["remainder"])
                bases.append(("o" if o_slot else "") + "cth" + ("" if remainder == "BARE" else remainder))
            covered = [base for base in bases if head_counts[base]]
            same_page_covered = sum(str(source["page"]) in head_pages[base] for source, base in zip(selected, bases))
            distinct_bases = sorted(set(bases))
            covered_types = [base for base in distinct_bases if head_counts[base]]
            rows.append({
                "population": population, "quality_prefix": q, "interfix": interfix, "e_slot": e_slot, "o_slot": o_slot,
                "expression_occurrences": len(selected), "expression_types": len({str(row["surface"]) for row in selected}),
                "predicted_inner_head_family": "o+cth+R" if o_slot else "cth+R",
                "occurrences_with_attested_inner_head": len(covered), "types_with_attested_inner_head": len(covered_types),
                "occurrences_with_same_page_inner_head": same_page_covered, "coverage_scope": "GLOBAL_TYPE_DECK",
                "inner_head_token_coverage": f"{len(covered) / len(selected):.4f}" if selected else "0.0000",
                "inner_head_type_coverage": f"{len(covered_types) / len(distinct_bases):.4f}" if distinct_bases else "0.0000",
                "attested_inner_heads": "|".join(covered_types),
                "missing_inner_heads": "|".join(base for base in distinct_bases if not head_counts[base]),
                "morphological_composition": Q_SURFACE[q] + ("+e" if e_slot else "") + "+[" + ("o+" if o_slot else "") + "cth+R]",
                "orthographic_boundary_default": (Q_SURFACE[q] + M_SURFACE[interfix]) + " | cth+R",
            })
    return rows


def make_order_control(token_rows: list[dict[str, str]]) -> list[dict[str, object]]:
    patterns = (
        ("BARE_CTH", re.compile(r"^cth.*$"), "nackter innerer CTH-Kopf"),
        ("BARE_E_CTH", re.compile(r"^ecth.*$"), "e ist nicht als nackter CTH-Kopf belegt"),
        ("BARE_O_CTH", re.compile(r"^octh.*$"), "o bildet eine eigenständige innere CTH-Kopfreihe"),
        ("BARE_EO_CTH", re.compile(r"^eocth.*$"), "eo ist nicht als nackter Kopf belegt"),
        ("BARE_OE_CTH", re.compile(r"^oecth.*$"), "umgekehrte oe-Kopfreihenfolge"),
        ("Q_E_CTH", re.compile(r"^(?:ch|sh)ecth.*$"), "e folgt ch/sh"),
        ("Q_O_CTH", re.compile(r"^(?:ch|sh)octh.*$"), "o steht zwischen ch/sh und CTH"),
        ("Q_EO_CTH", re.compile(r"^(?:ch|sh)eocth.*$"), "bezeugte Reihenfolge ch/sh + e + o + CTH"),
        ("Q_OE_CTH", re.compile(r"^(?:ch|sh)oecth.*$"), "umgekehrte Reihenfolge ch/sh + o + e + CTH"),
    )
    rows: list[dict[str, object]] = []
    for label, pattern, interpretation in patterns:
        selected = [row for row in token_rows if pattern.fullmatch(row["eva"])]
        rows.append({
            "pattern": label, "occurrences": len(selected), "types": len({row["eva"] for row in selected}),
            "pages": len({row["page"] for row in selected}), "example_surfaces": "|".join(sorted({row["eva"] for row in selected})[:8]),
            "interpretation_de": interpretation,
        })
    return rows


def make_cross_reader_order_control(cross_rows: list[dict[str, str]], inherited_bases: set[str]) -> list[dict[str, object]]:
    definitions = (
        ("FUSED_E_CTH", "FUSED_REGEX", re.compile(r"^ecth.*$"), "nackte e+CTH-Kopfreihe"),
        ("FUSED_O_CTH", "FUSED_REGEX", re.compile(r"^octh.*$"), "nackte o+CTH-Kopfreihe"),
        ("FUSED_EO_CTH", "FUSED_REGEX", re.compile(r"^eocth.*$"), "nackte eo+CTH-Kopfreihe"),
        ("FUSED_OE_CTH", "FUSED_REGEX", re.compile(r"^oecth.*$"), "umgekehrte nackte oe+CTH-Reihe"),
        ("SPLIT_E|CTH", "SPLIT_HEAD", "e", "getrennte e | CTH-Reihe"),
        ("SPLIT_O|CTH", "SPLIT_HEAD", "o", "getrennte o | CTH-Reihe"),
        ("SPLIT_EO|CTH", "SPLIT_HEAD", "eo", "getrennte eo | CTH-Reihe"),
        ("Q_OE_CTH_ANY_BOUNDARY", "SPAN_REGEX", re.compile(r"^(?:ch|sh)oecth.*$"), "umgekehrtes ch/sh+o+e+CTH in beliebiger Grenze bis vier Token"),
    )
    readers = (("ZL3b", "zl3b_clean"), ("IT2a", "it2a_clean"), ("RF1b", "rf1b_clean"))
    rows: list[dict[str, object]] = []
    for label, mode, value, interpretation in definitions:
        counts = Counter()
        loci: dict[str, set[str]] = defaultdict(set)
        examples: dict[str, list[str]] = defaultdict(list)
        for source in cross_rows:
            for reader, field in readers:
                words = source[field].split()
                if mode == "FUSED_REGEX":
                    hits = sum(value.fullmatch(word) is not None for word in words)
                elif mode == "SPLIT_HEAD":
                    hits = sum(left == value and right.startswith("cth") for left, right in zip(words, words[1:]))
                else:
                    hits = 0
                    for start in range(len(words)):
                        joined = ""
                        for stop in range(start, min(len(words), start + 4)):
                            joined += words[stop]
                            hits += int(value.fullmatch(joined) is not None)
                if hits:
                    counts[reader] += hits
                    loci[reader].add(source["locus"])
                    if len(examples[reader]) < 3:
                        examples[reader].append(source[field])
        rows.append({
            "pattern": label, "zl3b_occurrences": counts["ZL3b"], "it2a_occurrences": counts["IT2a"],
            "rf1b_occurrences": counts["RF1b"], "any_reader_occurrences": sum(counts.values()),
            "loci": "|".join(sorted(set().union(*loci.values()))) if loci else "",
            "examples": " || ".join(item for values in examples.values() for item in values),
            "interpretation_de": interpretation,
        })
    return rows


def make_out_of_lattice_census(
    token_rows: list[dict[str, str]], occurrences: list[dict[str, object]], cross_by_locus: dict[str, dict[str, str]],
) -> list[dict[str, object]]:
    """List every fused Q...CTH token not parsed by the preregistered four-slot lattice."""
    lattice_ids = {(str(row["locus"]), int(row["token_index"])) for row in occurrences}
    candidates = [
        row for row in sorted(token_rows, key=g631.token_sort_key)
        if re.fullmatch(r"(?:ch|sh).*cth.*", row["eva"]) is not None
    ]
    rows: list[dict[str, object]] = []
    ordinal: Counter[tuple[str, str]] = Counter()
    for source in candidates:
        key = (source["locus"], int(source["token_index"]))
        if key in lattice_ids:
            continue
        surface = source["eva"]
        if re.fullmatch(r"(?:ch|sh)eecth.*", surface):
            classification = "EE_NEAR_SLOT_RIVAL"
        elif "ol" in surface:
            classification = "OUTER_OL_CH_COMPOUND"
        else:
            classification = "OTHER_Q_CTH_EXTENSION"
        ordinal[source["locus"], surface] += 1
        cross = cross_by_locus[source["locus"]]
        exact_caps = [cross[field].split().count(surface) for field in ("zl3b_clean", "it2a_clean", "rf1b_clean")]
        normalized_caps = [g631.concatenated_span_count(cross[field].split(), surface) for field in ("zl3b_clean", "it2a_clean", "rf1b_clean")]
        modes = {}
        for reader, field in (("zl3b", "zl3b_clean"), ("it2a", "it2a_clean"), ("rf1b", "rf1b_clean")):
            words = cross[field].split()
            modes[reader] = "FUSED" if surface in words else "BOUNDARY_NORMALIZED" if target_realizations(words, surface) else "ABSENT_OR_DIFFERENT"
        rows.append({
            "occurrence_id": "", "page": source["page"], "locus": source["locus"],
            "token_index": source["token_index"], "surface": surface, "classification": classification,
            "triple_exact_token_stable": int(ordinal[source["locus"], surface] <= min(exact_caps)),
            "triple_boundary_normalized": int(ordinal[source["locus"], surface] <= min(normalized_caps)),
            "zl3b_mode": modes["zl3b"], "it2a_mode": modes["it2a"], "rf1b_mode": modes["rf1b"],
            "section": source["section"], "language": source["language"], "hand": source["hand"],
        })
    for index, row in enumerate(rows, 1):
        row["occurrence_id"] = f"G632-X{index:03d}"
    return rows


def make_matrix(occurrences: list[dict[str, object]]) -> list[dict[str, object]]:
    grouped: dict[tuple[str, str, str], list[dict[str, object]]] = defaultdict(list)
    for row in occurrences:
        grouped[str(row["remainder"]), str(row["quality_prefix"]), str(row["interfix"])].append(row)
    remainders = sorted({key[0] for key in grouped}, key=lambda remainder: (-sum(len(grouped.get((remainder, q, interfix), [])) for q in Q_ORDER for interfix in M_ORDER), remainder))
    rows: list[dict[str, object]] = []
    for remainder in remainders:
        row: dict[str, object] = {"remainder": remainder}
        occupied = []
        strict = 0
        for q in Q_ORDER:
            for interfix in M_ORDER:
                selected = grouped.get((remainder, q, interfix), [])
                key = f"{q.lower()}_{interfix.lower()}"
                row[f"{key}_surface"] = surface_for(q, interfix, remainder)
                row[f"{key}_occurrences"] = len(selected)
                row[f"{key}_pages"] = len({str(item["page"]) for item in selected})
                row[f"{key}_triple_exact"] = sum(int(item["triple_exact_token_stable"]) for item in selected)
                if selected:
                    occupied.append(f"{q}_{interfix}")
                    strict = max(strict, int(selected[0]["in_inherited_cth_surface_deck"]))
        row["in_inherited_cth_surface_deck"] = strict
        row["occupied_cells"] = len(occupied)
        row["occupied_cell_ids"] = "|".join(occupied)
        row["interfixes_with_both_quality_prefixes"] = sum(bool(grouped.get((remainder, "CH", interfix))) and bool(grouped.get((remainder, "SH", interfix))) for interfix in M_ORDER)
        row["total_occurrences"] = sum(len(grouped.get((remainder, q, interfix), [])) for q in Q_ORDER for interfix in M_ORDER)
        rows.append(row)
    return rows


def make_pairs(matrix: list[dict[str, object]]) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for source in matrix:
        for interfix in M_ORDER:
            ch_key, sh_key = f"ch_{interfix.lower()}", f"sh_{interfix.lower()}"
            if not int(source[f"{ch_key}_occurrences"]) or not int(source[f"{sh_key}_occurrences"]):
                continue
            rows.append({
                "pair_id": "", "interfix": interfix, "remainder": source["remainder"],
                "ch_surface": source[f"{ch_key}_surface"], "sh_surface": source[f"{sh_key}_surface"],
                "ch_occurrences": source[f"{ch_key}_occurrences"], "sh_occurrences": source[f"{sh_key}_occurrences"],
                "ch_pages": source[f"{ch_key}_pages"], "sh_pages": source[f"{sh_key}_pages"],
                "ch_triple_exact": source[f"{ch_key}_triple_exact"], "sh_triple_exact": source[f"{sh_key}_triple_exact"],
                "in_inherited_cth_surface_deck": source["in_inherited_cth_surface_deck"],
                "working_contrast_de": "trockene ↔ feuchte CTH-Materialform; Interfixbedeutung OPEN",
            })
    rows.sort(key=lambda row: (M_ORDER.index(str(row["interfix"])), -int(row["ch_occurrences"]) - int(row["sh_occurrences"]), str(row["remainder"])))
    for index, row in enumerate(rows, 1):
        row["pair_id"] = f"G632-P{index:03d}"
    return rows


def make_cell_summary(occurrences: list[dict[str, object]]) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for q in Q_ORDER:
        for interfix in M_ORDER:
            selected = [row for row in occurrences if row["quality_prefix"] == q and row["interfix"] == interfix]
            rows.append({
                "quality_prefix": q, "interfix": interfix, "occurrences": len(selected),
                "strict_occurrences": sum(int(row["in_inherited_cth_surface_deck"]) for row in selected),
                "types": len({str(row["surface"]) for row in selected}), "remainders": len({str(row["remainder"]) for row in selected}),
                "pages": len({str(row["page"]) for row in selected}),
                "triple_exact_occurrences": sum(int(row["triple_exact_token_stable"]) for row in selected),
                "sections": "|".join(sorted({str(row["section"]) for row in selected})) or "NONE",
                "hands": "|".join(sorted({str(row["hand"]) for row in selected})) or "NONE",
                "working_material_de": ("trockene" if q == "CH" else "feuchte") + " CTH-Materialreihe",
                "interfix_semantics": "OPEN",
            })
    return rows


def make_section_profile(occurrences: list[dict[str, object]]) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for q in Q_ORDER:
        for interfix in M_ORDER:
            sections = sorted({str(row["section"]) for row in occurrences if row["quality_prefix"] == q and row["interfix"] == interfix})
            for section in sections:
                selected = [row for row in occurrences if row["quality_prefix"] == q and row["interfix"] == interfix and row["section"] == section]
                rows.append({
                    "quality_prefix": q, "interfix": interfix, "section": section, "occurrences": len(selected),
                    "pages": len({str(row["page"]) for row in selected}), "types": len({str(row["surface"]) for row in selected}),
                    "triple_exact_occurrences": sum(int(row["triple_exact_token_stable"]) for row in selected),
                    "hands": "|".join(sorted({str(row["hand"]) for row in selected})),
                })
    return rows


def make_register_profile(
    occurrences: list[dict[str, object]], separated: list[dict[str, object]],
    bridges: list[dict[str, object]], meta_by_locus: dict[str, dict[str, str]],
) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    conservative = []
    ambiguous = []
    for source in bridges:
        if "SPLIT" not in str(source["zl3b_mode"]) or "FUSED" in str(source["zl3b_mode"]):
            continue
        normalized = {**source, **{field: meta_by_locus[str(source["locus"])][field] for field in ("section", "language", "hand")}}
        if int(source["diagnostic_internal_boundary"]):
            conservative.append(normalized)
        elif source["bridge_class"] == "LEFT_SHELL_TO_CTH__RIGHT_EDGE_OVERLAP":
            ambiguous.append(normalized)
    populations = (
        ("FUSED_ONLY", occurrences),
        ("FUSED_PLUS_ALL_READER_SEPARATED", [*occurrences, *separated]),
        ("CONSERVATIVE_BOUNDARY_NORMALIZED", [*occurrences, *separated, *conservative]),
        ("INCLUSIVE_LEFT_BOUNDARY", [*occurrences, *separated, *conservative, *ambiguous]),
    )
    for population, population_rows in populations:
        for scope_type, field in (("SECTION", "section"), ("LANGUAGE", "language"), ("HAND", "hand")):
            for scope in sorted({str(row[field]) for row in population_rows}):
                selected = [row for row in population_rows if row[field] == scope]
                counts = Counter(str(row["interfix"]) for row in selected)
                dominant = max(M_ORDER, key=lambda interfix: (counts[interfix], -M_ORDER.index(interfix)))
                row: dict[str, object] = {
                    "population": population, "scope_type": scope_type, "scope": scope, "occurrences": len(selected),
                    "dominant_interfix": dominant,
                }
                for interfix in M_ORDER:
                    row[f"{interfix.lower()}_occurrences"] = counts[interfix]
                    row[f"{interfix.lower()}_share"] = f"{counts[interfix] / len(selected):.4f}"
                row["diagnostic_de"] = "E und O sind registergeprägte lokale Klassen; die Populationen halten fusionierte, all-reader-getrennte, konservativ normalisierte und inklusive linke Grenzen auseinander."
                rows.append(row)
    return rows


def make_page_coexistence(
    occurrences: list[dict[str, object]], separated: list[dict[str, object]], bridges: list[dict[str, object]],
) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    conservative = [
        row for row in bridges
        if int(row["diagnostic_internal_boundary"]) and "SPLIT" in str(row["zl3b_mode"]) and "FUSED" not in str(row["zl3b_mode"])
    ]
    ambiguous = [
        row for row in bridges
        if row["bridge_class"] == "LEFT_SHELL_TO_CTH__RIGHT_EDGE_OVERLAP" and "SPLIT" in str(row["zl3b_mode"])
    ]
    populations = (
        ("FUSED_ONLY", occurrences),
        ("FUSED_PLUS_ALL_READER_SEPARATED", [*occurrences, *separated]),
        ("CONSERVATIVE_BOUNDARY_NORMALIZED", [*occurrences, *separated, *conservative]),
        ("INCLUSIVE_LEFT_BOUNDARY", [*occurrences, *separated, *conservative, *ambiguous]),
    )
    for population, population_rows in populations:
        by_page: dict[str, list[dict[str, object]]] = defaultdict(list)
        for row in population_rows:
            by_page[str(row["page"])].append(row)
        for page, selected in by_page.items():
            interfixes = sorted({str(row["interfix"]) for row in selected}, key=M_ORDER.index)
            if len(interfixes) < 2:
                continue
            nonempty = [interfix for interfix in interfixes if interfix != "NONE"]
            rows.append({
                "population": population, "page": page, "interfixes": "|".join(interfixes), "distinct_interfixes": len(interfixes),
                "distinct_nonempty_interfixes": len(nonempty),
                "occurrences": len(selected), "quality_prefixes": "|".join(sorted({str(row["quality_prefix"]) for row in selected})),
                "surfaces": "|".join(sorted({str(row.get("surface", row.get("fused_counterpart", ""))) for row in selected})),
                "loci": "|".join(sorted({str(row["locus"]) for row in selected}, key=g631.line_number)),
                "interpretation_de": "Mehrere Reihen auf derselben Seite widerlegen einen deterministischen Seiten-/Handersatz; konditionierte Allographie oder lokale Klassenwahl bleiben möglich.",
            })
    rows.sort(key=lambda row: (str(row["population"]), str(row["page"])))
    return rows


def make_inherited_visual_scope(old_visual: list[dict[str, str]]) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for source in old_visual:
        rows.append({
            "visual_id": source["visual_id"].replace("G631", "G632"), "page": source["page"], "locus": source["locus"],
            "target_scope": "DIRECT_NONE_CTH_ROW", "inherited_observation_de": source["inherited_observation_de"],
            "licensed_reading_de": source["licensed_reading_de"], "not_licensed_de": source["not_licensed_de"],
            "e_o_target_on_inherited_image": 0, "new_image_opened": 0,
        })
    rows.append({
        "visual_id": "G632-V04", "page": "ALL", "locus": "E_O_EO_TARGET_FAMILY", "target_scope": "EXTENDED_LEFT_SHELL_ROWS",
        "inherited_observation_de": "Keines der geerbten manuell geprüften Bildurteile trägt ein e/o/eo-CTH-Zieltoken.",
        "licensed_reading_de": "Nur der gemeinsame CTH-Pflanzen-/Drogenmaterialkopf darf vererbt werden; Herbal kann zu Blatt-/Krautmaterial verengen.",
        "not_licensed_de": "Keine Trennung Blatt/Wurzel/Blüte/Samen, Medium, Gefäß oder Operation nach e/o/eo.",
        "e_o_target_on_inherited_image": 0, "new_image_opened": 0,
    })
    return rows


def make_historical_comparators() -> list[dict[str, object]]:
    return [
        {
            "comparator_id": "G632-H01", "manuscript": "Pal.lat.1256", "date_place": "1401–1450; mittleres Ostdeutschland",
            "historical_system": "Synonyma apothecariorum; lateinisch-deutsche Synonyma simplicium; Quid pro quo; De dosibus",
            "relevance_de": "Zeitnahes Mischsystem aus gelernten Drogennamen, nummerierten Synonymgruppen, volkssprachlichen Entsprechungen, Substitutionsformeln und Dosisrubriken.",
            "source_url": "https://portail.biblissima.fr/en/ark:/43093/mdata4be843cf8c997190b99e016b5ad7760c77a6e2b9",
            "image_url": "https://digi.vatlib.it/iiifimage/MSS_Pal.lat.1256/Pal.lat.1256_0369_fa_0178r.jp2/full/2400,/0/default.jpg",
            "limit_de": "Belegt die historische Mischarchitektur, nicht ein Voynich-Zeichen oder eine Bedeutung für e/o.",
        },
        {
            "comparator_id": "G632-H02", "manuscript": "Wellcome MS 542", "date_place": "frühes 15. Jahrhundert",
            "historical_system": "Ganzname und Pflanzenteil neben gebundenen Qualitätsformen, Kürzeln und explizitem Grad",
            "relevance_de": "f118r variiert gebundene Qualitätsoberflächen im selben Aloe-Bereich; f119v kombiniert Eleborus, Radix, c./s.-Kürzel und Grad III als getrennte Module.",
            "source_url": "https://wellcomecollection.org/works/n674z2xd",
            "image_url": "https://iiif.wellcomecollection.org/image/b19608767_MS_542_0252.JP2/full/2400,/0/default.jpg",
            "limit_de": "Stützt gelernte Ganznamen plus gebundene Fachslots, liefert aber keinen Schlüssel e=X oder o=Y.",
        },
    ]


def make_fixed_contexts(occurrences: list[dict[str, object]]) -> list[dict[str, object]]:
    grouped: dict[tuple[str, str, str], list[dict[str, object]]] = defaultdict(list)
    for row in occurrences:
        grouped[str(row["remainder"]), str(row["left_surface"]), str(row["right_surface"])].append(row)
    rows: list[dict[str, object]] = []
    for (remainder, left, right), selected in grouped.items():
        cells = sorted({f"{row['quality_prefix']}_{row['interfix']}" for row in selected})
        if len(cells) < 2:
            continue
        rows.append({
            "context_id": "", "remainder": remainder, "left_surface": left, "right_surface": right,
            "cells": "|".join(cells), "distinct_cells": len(cells), "occurrences": len(selected),
            "pages": len({str(row["page"]) for row in selected}),
            "all_targets_triple_exact": int(all(int(row["triple_exact_token_stable"]) for row in selected)),
            "surfaces": "|".join(sorted({str(row["surface"]) for row in selected})),
            "loci": "|".join(str(row["locus"]) for row in selected),
        })
    rows.sort(key=lambda row: (-int(row["distinct_cells"]), -int(row["occurrences"]), str(row["remainder"]), str(row["left_surface"])))
    for index, row in enumerate(rows, 1):
        row["context_id"] = f"G632-F{index:03d}"
    return rows


def make_one_sided_contexts(occurrences: list[dict[str, object]]) -> list[dict[str, object]]:
    grouped: dict[tuple[str, str, str], list[dict[str, object]]] = defaultdict(list)
    for row in occurrences:
        grouped[str(row["remainder"]), "LEFT", str(row["left_surface"])].append(row)
        grouped[str(row["remainder"]), "RIGHT", str(row["right_surface"])].append(row)
    rows: list[dict[str, object]] = []
    for (remainder, side, neighbor), selected in grouped.items():
        cells = sorted({f"{row['quality_prefix']}_{row['interfix']}" for row in selected})
        if len(cells) < 3:
            continue
        rows.append({
            "context_id": "", "remainder": remainder, "fixed_side": side, "fixed_neighbor": neighbor,
            "cells": "|".join(cells), "distinct_cells": len(cells), "occurrences": len(selected),
            "pages": len({str(row["page"]) for row in selected}),
            "surfaces": "|".join(sorted({str(row["surface"]) for row in selected})),
            "triple_exact_occurrences": sum(int(row["triple_exact_token_stable"]) for row in selected),
            "loci": "|".join(str(row["locus"]) for row in selected),
        })
    rows.sort(key=lambda row: (-int(row["distinct_cells"]), -int(row["occurrences"]), str(row["remainder"]), str(row["fixed_side"]), str(row["fixed_neighbor"])))
    for index, row in enumerate(rows, 1):
        row["context_id"] = f"G632-OF{index:03d}"
    return rows


def make_slots(occurrences: list[dict[str, object]]) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for source in occurrences:
        if source["left_surface"] != "daiin" or source["position"] != "LAST":
            continue
        rows.append({
            "slot_id": f"G632-S{len(rows) + 1:03d}", "page": source["page"], "locus": source["locus"],
            "surface": source["surface"], "quality_prefix": source["quality_prefix"], "interfix": source["interfix"],
            "remainder": source["remainder"], "frame": "daiin __ <LINE_END>",
            "triple_exact_token_stable": source["triple_exact_token_stable"], "working_category_de": "CTH-Material-/Partslot",
            "surface_line": source["surface_line"],
        })
    return rows


def axis_relation(q: str, axes: set[str]) -> str:
    expected, opposite = (("DRY", "MOIST") if q == "CH" else ("MOIST", "DRY"))
    if expected in axes:
        return "MATCHING_PREFIX_AXIS"
    if opposite in axes:
        return "OPPOSITE_PREFIX_AXIS"
    return "ORTHOGONAL_AXIS"


def make_quality_contacts(occurrences: list[dict[str, object]], refs: dict[str, list[dict[str, object]]]) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for part in occurrences:
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
            rows.append({
                "contact_id": "", "occurrence_id": part["occurrence_id"], "page": part["page"], "locus": part["locus"],
                "part_surface": part["surface"], "quality_prefix": part["quality_prefix"], "interfix": part["interfix"],
                "remainder": part["remainder"], "quality_source": quality["source"], "quality_surface": quality["surface"],
                "quality_axes": quality["axis_label"], "distance": distance, "order": order,
                "prefix_axis_relation": axis_relation(str(part["quality_prefix"]), set(quality["axes"])),
                "both_triple_stable": int(int(part["triple_boundary_normalized"]) and int(quality["triple_stable"])),
                "working_part_de": part["working_material_de"], "working_quality_de": quality["working_reading_de"],
                "surface_line": part["surface_line"],
            })
    rows.sort(key=lambda row: (str(row["page"]), g631.line_number(str(row["locus"])), str(row["part_surface"]), int(row["distance"])))
    for index, row in enumerate(rows, 1):
        row["contact_id"] = f"G632-Q{index:03d}"
    return rows


def make_quality_summary(occurrences: list[dict[str, object]], contacts: list[dict[str, object]]) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for q in Q_ORDER:
        for interfix in M_ORDER:
            parts = [row for row in occurrences if row["quality_prefix"] == q and row["interfix"] == interfix]
            selected = [row for row in contacts if row["quality_prefix"] == q and row["interfix"] == interfix]
            relations = Counter(str(row["prefix_axis_relation"]) for row in selected)
            rows.append({
                "quality_prefix": q, "interfix": interfix, "part_occurrences": len(parts),
                "part_occurrences_with_contact": len({str(row["occurrence_id"]) for row in selected}),
                "contacts_within_three": len(selected), "immediate_contacts": sum(int(row["distance"]) == 1 for row in selected),
                "immediate_part_occurrences": len({str(row["occurrence_id"]) for row in selected if int(row["distance"]) == 1}),
                "matching_contacts": relations["MATCHING_PREFIX_AXIS"], "opposite_contacts": relations["OPPOSITE_PREFIX_AXIS"],
                "orthogonal_contacts": relations["ORTHOGONAL_AXIS"],
                "matching_immediate": sum(int(row["distance"]) == 1 and row["prefix_axis_relation"] == "MATCHING_PREFIX_AXIS" for row in selected),
                "opposite_immediate": sum(int(row["distance"]) == 1 and row["prefix_axis_relation"] == "OPPOSITE_PREFIX_AXIS" for row in selected),
                "both_triple_stable_contacts": sum(int(row["both_triple_stable"]) for row in selected),
            })
    return rows


def make_local_quality(occurrences: list[dict[str, object]], refs: dict[str, list[dict[str, object]]]) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for part in occurrences:
        for quality in refs.get(str(part["locus"]), []):
            if abs(int(part["token_index"]) - int(quality["index"])) != 1:
                continue
            rows.append({
                "neighbor_id": "", "occurrence_id": part["occurrence_id"], "page": part["page"], "locus": part["locus"],
                "part_surface": part["surface"], "quality_prefix": part["quality_prefix"], "interfix": part["interfix"],
                "quality_surface": quality["surface"], "quality_source": quality["source"], "quality_axes": quality["axis_label"],
                "prefix_axis_relation": axis_relation(str(part["quality_prefix"]), set(quality["axes"])),
                "both_triple_stable": int(int(part["triple_exact_token_stable"]) and int(quality["triple_stable"])),
                "surface_line": part["surface_line"],
            })
    rows.sort(key=lambda row: (str(row["page"]), g631.line_number(str(row["locus"])), str(row["part_surface"])))
    for index, row in enumerate(rows, 1):
        row["neighbor_id"] = f"G632-N{index:03d}"
    return rows


def make_repeated(contacts: list[dict[str, object]]) -> list[dict[str, object]]:
    grouped: dict[tuple[str, str, str], list[dict[str, object]]] = defaultdict(list)
    for row in contacts:
        if int(row["distance"]) == 1:
            grouped[str(row["part_surface"]), str(row["quality_surface"]), str(row["order"])].append(row)
    rows: list[dict[str, object]] = []
    for (part, quality, order), selected in grouped.items():
        if len(selected) < 2:
            continue
        first = selected[0]
        clause = f"{part} {quality}" if order == "PART_BEFORE_QUALITY" else f"{quality} {part}"
        rows.append({
            "frame_id": "", "part_surface": part, "quality_surface": quality, "order": order,
            "surface_clause": clause, "quality_prefix": first["quality_prefix"], "interfix": first["interfix"],
            "occurrences": len(selected), "pages": len({str(row["page"]) for row in selected}),
            "triple_stable_occurrences": sum(int(row["both_triple_stable"]) for row in selected),
            "prefix_axis_relation": first["prefix_axis_relation"],
            "working_reading_de": f"{first['working_part_de']}: {first['working_quality_de']}",
            "loci": "|".join(str(row["locus"]) for row in selected),
        })
    rows.sort(key=lambda row: (-int(row["occurrences"]), str(row["surface_clause"])))
    for index, row in enumerate(rows, 1):
        row["frame_id"] = f"G632-R{index:03d}"
    return rows


def make_cases(contacts: list[dict[str, object]]) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for source in contacts:
        if int(source["distance"]) != 1 or not int(source["both_triple_stable"]):
            continue
        clause = f"{source['part_surface']} {source['quality_surface']}" if source["order"] == "PART_BEFORE_QUALITY" else f"{source['quality_surface']} {source['part_surface']}"
        rows.append({
            "case_id": f"G632-C{len(rows) + 1:03d}", "page": source["page"], "locus": source["locus"],
            "surface_clause": clause, "quality_prefix": source["quality_prefix"], "interfix": source["interfix"],
            "working_reading_de": f"{source['working_part_de']}: {source['working_quality_de']}",
            "interfix_semantics": "OPEN", "prefix_axis_relation": source["prefix_axis_relation"],
            "residual_policy": "kleinste sichtbare Klammer; übrige Tokens OPEN",
        })
    return rows


def make_ranking(
    summary: list[dict[str, object]], pairs: list[dict[str, object]], bridges: list[dict[str, object]],
    separated: list[dict[str, object]], head_summary: list[dict[str, object]], hierarchy: list[dict[str, object]],
) -> list[dict[str, object]]:
    pair_counts = Counter(str(row["interfix"]) for row in pairs)
    direct = [row for row in bridges if int(row["diagnostic_internal_boundary"])]
    heads = {str(row["head_prefix"]): row for row in head_summary}
    o_rows = [row for row in hierarchy if row["population"] == "FUSED_ONLY" and int(row["o_slot"])]
    return [
        {"rank": 1, "model": "ORDERED_Q_E_O_CTH_HIERARCHY", "working_model_de": "ch/sh + e? + [o? + cth+Rest]; ch/sh tragen provisorisch trocken/feucht, e und o bleiben stumme Klassenmarker", "support": f"nackte o+cth-Reihe={heads['O']['occurrences']} Token/{heads['O']['types']} Typen, nackte e/eo-Reihen=0/0; alle {sum(int(row['expression_occurrences']) for row in o_rows)} fusionierten o/eo-Präfixtoken besitzen ihre innere Basis", "counterevidence": "im inklusiven Grenzpanel fehlt für cheoctheey noch die nackte Basis octheey; sichtbare Wortgrenzen schneiden oft nach dem linken Block", "disposition": "PRIMARY_MORPHOLOGICAL_STRUCTURE__E_O_OPEN"},
        {"rank": 2, "model": "ORTHOGRAPHIC_LEFT_SHELL_PLUS_CTH", "working_model_de": "Die Schreibung bündelt ch/che/cho/cheo bzw. sh/she/sho/sheo links und trennt danach vor CTH", "support": f"direkte Lesergrenzen={len(direct)}; in allen Lesern getrennte Shell-Spans={len(separated)}", "counterevidence": "orthographische Wortgrenze allein entscheidet nicht, ob o semantisch links oder beim CTH-Kopf gruppiert", "disposition": "PRIMARY_SURFACE_SEGMENTATION"},
        {"rank": 3, "model": "REGISTER_CONDITIONED_LOCAL_CLASS", "working_model_de": "e/o markieren registergeprägte, aber lokal auswählbare Form- oder Attributklassen; in der Übersetzung zunächst stumm", "support": "E häuft sich in B/Hand2, O in H/Hand1; zugleich koexistieren drei Reihen auf einzelnen Seiten", "counterevidence": "deterministischer Seiten-/Handersatz scheitert; konditionierte Allographie bleibt möglich", "disposition": "PRIMARY_SEMANTIC_DEFAULT"},
        {"rank": 4, "model": "NESTED_SEMANTIC_ATTRIBUTE", "working_model_de": "e/o sind zusätzliche Sachattribute innerhalb des Materialkopfs", "support": f"beide Qualitätspräfixe paaren über die vier Oberflächenklassen: {dict(pair_counts)}", "counterevidence": "kein sichtbarer oder wiederholter Kontext trennt Blatt, Wurzel, Medium oder Vorgang sicher nach e/o", "disposition": "LIVE_SEMANTIC_RIVAL"},
        {"rank": 5, "model": "INDEPENDENT_WHOLE_WORDS", "working_model_de": "jede Oberfläche wird separat gelernt", "support": "orthographisch bleiben die meisten Formen fusioniert", "counterevidence": "geordnetes Raster, nackte o+CTH-Basen, geteilte Reste und realisierte Split-only-Vorhersagen werden unnötig teuer", "disposition": "REJECTED_AS_PRIMARY"},
    ]


def make_dictionary(old: list[dict[str, str]]) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = [dict(row) for row in old]
    entries = (
        ("cth+R", "CTH_MATERIAL_STEM", "Pflanzen-/Drogenmaterialfamilie; im Herbal Blatt-/Krautmaterial", "cth+Rest"),
        ("o+cth+R", "O_FRAMED_CTH_INNER_HEAD", "o-gerahmte CTH-Materialfamilie; o in Fließlesung vorerst stumm", "o+[cth+Rest]"),
        ("e nach ch/sh", "DEPENDENT_E_CLASS_SLOT", "E-Binde-/Formklasse nach trocken/feucht-Kern; in Fließlesung stumm", "ch|sh + e"),
        ("ch/sh+e?+[o?+cth+R]", "ORDERED_E_O_CTH_HIERARCHY", "trocken/feucht markierte CTH-Materialform mit geordneten offenen e/o-Klassen", "Qualitätskern + e? + innerer o?-CTH-Kopf"),
        ("-y in CTH", "CTH_BASE_FORM_CLOSURE", "häufigster Abschluss der CTH-Grundform; kein eigenes Stoffwort", "cth+y"),
        ("ch-", "DRY_QUALITY_SHELL_CORE", "provisorisch trocken markierender linker Qualitätskern", "ch+(e|o|eo)?"),
        ("sh-", "MOIST_QUALITY_SHELL_CORE", "provisorisch feucht markierender linker Qualitätskern", "sh+(e|o|eo)?"),
        ("che-", "DRY_E_LEFT_SHELL", "trockener linker Qualitätsblock der e-Reihe; e in Fließlesung stumm", "ch+e"),
        ("she-", "MOIST_E_LEFT_SHELL", "feuchter linker Qualitätsblock der e-Reihe; e in Fließlesung stumm", "sh+e"),
        ("cho-", "DRY_O_LEFT_SHELL", "trockener linker Qualitätsblock der o-Reihe; o in Fließlesung stumm", "ch+o"),
        ("sho-", "MOIST_O_LEFT_SHELL", "feuchter linker Qualitätsblock der o-Reihe; o in Fließlesung stumm", "sh+o"),
        ("cheo-", "DRY_EO_LEFT_SHELL", "trockener linker Qualitätsblock der seltenen eo-Reihe", "ch+eo"),
        ("sheo-", "MOIST_EO_LEFT_SHELL", "feuchter linker Qualitätsblock der seltenen eo-Reihe", "sh+eo"),
        ("checthy", "DRY_E_CTH_MATERIAL", "trockene CTH-Materialform der e-Reihe", "che|cth+y"),
        ("shecthy", "MOIST_E_CTH_MATERIAL", "feuchte CTH-Materialform der e-Reihe", "she|cth+y"),
        ("chocthy", "DRY_O_CTH_MATERIAL", "trockene CTH-Materialform der o-Reihe", "ch+[o+cth+y]; sichtbar oft cho|cthy"),
        ("shocthy", "MOIST_O_CTH_MATERIAL", "feuchte CTH-Materialform der o-Reihe", "sh+[o+cth+y]; sichtbar oft sho|cthy"),
        ("cheocthy", "DRY_EO_CTH_MATERIAL", "trockene CTH-Materialform der eo-Reihe", "ch+e+[o+cth+y]; sichtbar cheo|cthy"),
        ("sheocthy", "MOIST_EO_CTH_MATERIAL", "feuchte CTH-Materialform der eo-Reihe", "sh+e+[o+cth+y]; sichtbar sheo|cthy"),
        ("[ch|sh]+e?+o? | CTH", "LEFT_SHELL_SURFACE_FRAME", "geschriebener linker Block vor CTH; Bedeutungsanalyse hierarchisch ch/sh+e?+[o?+CTH]", "linker Oberflächenblock | cth+Rest"),
    )
    for entry, kind, meaning, composition in entries:
        rows.append({"entry": entry, "kind": kind, "working_meaning_de": meaning, "composition": composition, "context_rule": "ch=trocken,sh=feucht; e ist abhängig, o besitzt eine nackte CTH-Kopfreihe; beide bleiben lexikalisch OPEN und in Fließlesung stumm", "status": "NEW_PRODUCTIVE_DEFAULT__ORDERED_E_O_HIERARCHY"})
    return rows


def main() -> int:
    ART.mkdir(parents=True, exist_ok=True)
    pages = {row["page"] for row in read_tsv(ROOT / ALLOW_REL)}
    if "f1r" in pages or any(page.startswith("f84") for page in pages):
        raise RuntimeError("allow-list contains forbidden page")
    token_rows, token_stats = g631.guarded_query(TOKENS_REL, pages, "page,locus,token_index,eva,section,language,hand")
    cross_rows, cross_stats = g631.guarded_query(CROSS_REL, pages, "page,locus,all_three_present,all_present_exact,zl3b_clean,it2a_clean,rf1b_clean")
    cross_by_locus = {row["locus"]: row for row in cross_rows}
    by_line, line_text = g631.line_maps([dict(row) for row in token_rows])
    inherited_bases = {row["surface"] for row in read_tsv(ROOT / G625_CTH_REL)}

    occurrences = make_occurrences(token_rows, cross_by_locus, line_text, inherited_bases, by_line)
    reader = make_reader_rows(occurrences, cross_by_locus)
    matrix = make_matrix(occurrences)
    pairs = make_pairs(matrix)
    bridges = make_bridges(occurrences, inherited_bases, cross_rows)
    separated = make_all_reader_separated(occurrences, inherited_bases, cross_rows)
    meta_by_locus = {row["locus"]: row for row in token_rows}
    for row in separated:
        meta = meta_by_locus[str(row["locus"])]
        row.update({"section": meta["section"], "language": meta["language"], "hand": meta["hand"]})
    bridge_summary = make_bridge_summary(bridges, separated)
    expression_populations = make_expression_population_summary(occurrences, separated, bridges)
    boundary_null = make_alternative_boundary_null(cross_rows)
    outer_bridges = make_outer_bridges(occurrences, cross_rows)
    shells = make_left_shells(occurrences, bridges, separated)
    heads, head_summary, head_matrix = make_inner_head_rows(token_rows, cross_by_locus, inherited_bases)
    hierarchy = make_hierarchical_coverage(occurrences, heads, separated, bridges)
    order_control = make_order_control(token_rows)
    reader_order_control = make_cross_reader_order_control(cross_rows, inherited_bases)
    out_of_lattice = make_out_of_lattice_census(token_rows, occurrences, cross_by_locus)
    summary = make_cell_summary(occurrences)
    sections = make_section_profile(occurrences)
    registers = make_register_profile(occurrences, separated, bridges, meta_by_locus)
    coexistence = make_page_coexistence(occurrences, separated, bridges)
    visual = make_inherited_visual_scope(read_tsv(ROOT / G631_VISUAL_REL))
    historical = make_historical_comparators()
    contexts = make_fixed_contexts(occurrences)
    one_sided_contexts = make_one_sided_contexts(occurrences)
    slots = make_slots(occurrences)
    quality = make_quality_contacts(occurrences, g631.quality_references())
    quality_summary = make_quality_summary(occurrences, quality)
    local_quality = make_local_quality(occurrences, g631.local_quality_references())
    repeated = make_repeated(quality)
    cases = make_cases(quality)
    ranking = make_ranking(summary, pairs, bridges, separated, head_summary, hierarchy)
    dictionary = make_dictionary(read_tsv(ROOT / G631_DICT_REL))

    write_tsv(ROOT / OUTPUTS["allowlist"], [{"page": page} for page in sorted(pages)], ("page",))
    write_tsv(ROOT / OUTPUTS["occurrences"], occurrences, (
        "occurrence_id", "page", "locus", "token_index", "surface", "quality_prefix", "interfix", "remainder",
        "bare_cth_surface", "in_inherited_cth_surface_deck", "triple_exact_token_stable", "triple_boundary_normalized",
        "left_surface", "right_surface", "position", "section", "language", "hand", "working_material_de", "interfix_semantics", "surface_line",
    ))
    write_tsv(ROOT / OUTPUTS["reader"], reader, (
        "occurrence_id", "page", "locus", "surface", "quality_prefix", "interfix", "remainder",
        "zl3b_mode", "it2a_mode", "rf1b_mode", "triple_exact_token_stable", "triple_boundary_normalized", "any_internal_split_reader",
    ))
    write_tsv(ROOT / OUTPUTS["bridges"], bridges, (
        "bridge_id", "page", "locus", "surface", "quality_prefix", "interfix", "remainder",
        "bridge_class", "span_status", "diagnostic_internal_boundary", "left_shell_cth_boundary_visible", "observed_realizations",
        "zl3b_target_spans", "it2a_target_spans", "rf1b_target_spans",
        "zl3b_mode", "it2a_mode", "rf1b_mode", "zl3b_line", "it2a_line", "rf1b_line",
    ))
    write_tsv(ROOT / OUTPUTS["separated"], separated, (
        "span_id", "page", "locus", "quality_prefix", "interfix", "remainder", "left_shell", "cth_surface",
        "separated_surface", "fused_counterpart", "fused_counterpart_occurrences_elsewhere", "evidence_role",
        "section", "language", "hand",
        "zl3b_line", "it2a_line", "rf1b_line",
    ))
    write_tsv(ROOT / OUTPUTS["bridge_summary"], bridge_summary, ("orientation", "alternate_reader_spans", "all_reader_separated_spans", "total_diagnostic_spans", "loci", "interpretation_de"))
    write_tsv(ROOT / OUTPUTS["expression_populations"], expression_populations, ("population", "occurrences", "types", "pages", "remainders", "added_occurrences", "added_loci", "definition_de"))
    write_tsv(ROOT / OUTPUTS["boundary_null"], boundary_null, ("alternative_boundary", "display", "zl3b_occurrences", "it2a_occurrences", "rf1b_occurrences", "any_reader_occurrences", "loci", "examples", "disposition_de"))
    write_tsv(ROOT / OUTPUTS["outer_bridges"], outer_bridges, ("bridge_id", "page", "locus", "family_surface", "combined_surface", "boundary_side", "external_surface", "zl3b_mode", "it2a_mode", "rf1b_mode", "reader_scope", "zl3b_line", "it2a_line", "rf1b_line"))
    write_tsv(ROOT / OUTPUTS["shells"], shells, ("quality_prefix", "interfix", "left_shell", "fused_occurrences", "fused_types", "pages", "direct_reader_boundary_spans", "all_reader_separated_spans", "observed_shell_cth_boundary", "working_shell_de", "interfix_disposition"))
    write_tsv(ROOT / OUTPUTS["head_summary"], head_summary, ("head_prefix", "occurrences", "types", "remainders", "pages", "triple_exact_occurrences", "occurrences_with_published_bare_cth_counterpart", "working_role_de"))
    head_matrix_fields = ["remainder"]
    for prefix in M_ORDER:
        key = prefix.lower()
        head_matrix_fields.extend((f"{key}_surface", f"{key}_occurrences", f"{key}_pages", f"{key}_triple_exact"))
    head_matrix_fields.append("published_bare_cth_remainder")
    write_tsv(ROOT / OUTPUTS["head_matrix"], head_matrix, head_matrix_fields)
    write_tsv(ROOT / OUTPUTS["hierarchy"], hierarchy, ("population", "quality_prefix", "interfix", "e_slot", "o_slot", "expression_occurrences", "expression_types", "predicted_inner_head_family", "occurrences_with_attested_inner_head", "types_with_attested_inner_head", "occurrences_with_same_page_inner_head", "coverage_scope", "inner_head_token_coverage", "inner_head_type_coverage", "attested_inner_heads", "missing_inner_heads", "morphological_composition", "orthographic_boundary_default"))
    write_tsv(ROOT / OUTPUTS["order_control"], order_control, ("pattern", "occurrences", "types", "pages", "example_surfaces", "interpretation_de"))
    write_tsv(ROOT / OUTPUTS["reader_order_control"], reader_order_control, ("pattern", "zl3b_occurrences", "it2a_occurrences", "rf1b_occurrences", "any_reader_occurrences", "loci", "examples", "interpretation_de"))
    write_tsv(ROOT / OUTPUTS["out_of_lattice"], out_of_lattice, (
        "occurrence_id", "page", "locus", "token_index", "surface", "classification",
        "triple_exact_token_stable", "triple_boundary_normalized", "zl3b_mode", "it2a_mode", "rf1b_mode",
        "section", "language", "hand",
    ))
    matrix_fields = ["remainder"]
    for q in Q_ORDER:
        for interfix in M_ORDER:
            key = f"{q.lower()}_{interfix.lower()}"
            matrix_fields.extend((f"{key}_surface", f"{key}_occurrences", f"{key}_pages", f"{key}_triple_exact"))
    matrix_fields.extend(("in_inherited_cth_surface_deck", "occupied_cells", "occupied_cell_ids", "interfixes_with_both_quality_prefixes", "total_occurrences"))
    write_tsv(ROOT / OUTPUTS["matrix"], matrix, matrix_fields)
    write_tsv(ROOT / OUTPUTS["pairs"], pairs, (
        "pair_id", "interfix", "remainder", "ch_surface", "sh_surface", "ch_occurrences", "sh_occurrences",
        "ch_pages", "sh_pages", "ch_triple_exact", "sh_triple_exact", "in_inherited_cth_surface_deck", "working_contrast_de",
    ))
    write_tsv(ROOT / OUTPUTS["summary"], summary, (
        "quality_prefix", "interfix", "occurrences", "strict_occurrences", "types", "remainders", "pages",
        "triple_exact_occurrences", "sections", "hands", "working_material_de", "interfix_semantics",
    ))
    write_tsv(ROOT / OUTPUTS["sections"], sections, ("quality_prefix", "interfix", "section", "occurrences", "pages", "types", "triple_exact_occurrences", "hands"))
    write_tsv(ROOT / OUTPUTS["registers"], registers, ("population", "scope_type", "scope", "occurrences", "none_occurrences", "none_share", "e_occurrences", "e_share", "o_occurrences", "o_share", "eo_occurrences", "eo_share", "dominant_interfix", "diagnostic_de"))
    write_tsv(ROOT / OUTPUTS["coexistence"], coexistence, ("population", "page", "interfixes", "distinct_interfixes", "distinct_nonempty_interfixes", "occurrences", "quality_prefixes", "surfaces", "loci", "interpretation_de"))
    write_tsv(ROOT / OUTPUTS["visual"], visual, ("visual_id", "page", "locus", "target_scope", "inherited_observation_de", "licensed_reading_de", "not_licensed_de", "e_o_target_on_inherited_image", "new_image_opened"))
    write_tsv(ROOT / OUTPUTS["historical"], historical, ("comparator_id", "manuscript", "date_place", "historical_system", "relevance_de", "source_url", "image_url", "limit_de"))
    write_tsv(ROOT / OUTPUTS["contexts"], contexts, ("context_id", "remainder", "left_surface", "right_surface", "cells", "distinct_cells", "occurrences", "pages", "all_targets_triple_exact", "surfaces", "loci"))
    write_tsv(ROOT / OUTPUTS["one_sided_contexts"], one_sided_contexts, ("context_id", "remainder", "fixed_side", "fixed_neighbor", "cells", "distinct_cells", "occurrences", "pages", "surfaces", "triple_exact_occurrences", "loci"))
    write_tsv(ROOT / OUTPUTS["slots"], slots, ("slot_id", "page", "locus", "surface", "quality_prefix", "interfix", "remainder", "frame", "triple_exact_token_stable", "working_category_de", "surface_line"))
    quality_fields = ("contact_id", "occurrence_id", "page", "locus", "part_surface", "quality_prefix", "interfix", "remainder", "quality_source", "quality_surface", "quality_axes", "distance", "order", "prefix_axis_relation", "both_triple_stable", "working_part_de", "working_quality_de", "surface_line")
    write_tsv(ROOT / OUTPUTS["quality"], quality, quality_fields)
    write_tsv(ROOT / OUTPUTS["quality_summary"], quality_summary, ("quality_prefix", "interfix", "part_occurrences", "part_occurrences_with_contact", "contacts_within_three", "immediate_contacts", "immediate_part_occurrences", "matching_contacts", "opposite_contacts", "orthogonal_contacts", "matching_immediate", "opposite_immediate", "both_triple_stable_contacts"))
    write_tsv(ROOT / OUTPUTS["local_quality"], local_quality, ("neighbor_id", "occurrence_id", "page", "locus", "part_surface", "quality_prefix", "interfix", "quality_surface", "quality_source", "quality_axes", "prefix_axis_relation", "both_triple_stable", "surface_line"))
    write_tsv(ROOT / OUTPUTS["repeated"], repeated, ("frame_id", "part_surface", "quality_surface", "order", "surface_clause", "quality_prefix", "interfix", "occurrences", "pages", "triple_stable_occurrences", "prefix_axis_relation", "working_reading_de", "loci"))
    write_tsv(ROOT / OUTPUTS["cases"], cases, ("case_id", "page", "locus", "surface_clause", "quality_prefix", "interfix", "working_reading_de", "interfix_semantics", "prefix_axis_relation", "residual_policy"))
    write_tsv(ROOT / OUTPUTS["ranking"], ranking, ("rank", "model", "working_model_de", "support", "counterevidence", "disposition"))
    write_tsv(ROOT / OUTPUTS["dictionary"], dictionary, ("entry", "kind", "working_meaning_de", "composition", "context_rule", "status"))

    cell_counts = {(row["quality_prefix"], row["interfix"]): int(row["occurrences"]) for row in summary}
    pair_counts = Counter(str(row["interfix"]) for row in pairs)
    relation_counts = Counter(str(row["prefix_axis_relation"]) for row in quality)
    local_relation_counts = Counter(str(row["prefix_axis_relation"]) for row in local_quality)
    quality_axis_by_cell = {
        f"{row['quality_prefix']}_{row['interfix']}": {
            "matching_immediate": int(row["matching_immediate"]), "opposite_immediate": int(row["opposite_immediate"])
        }
        for row in quality_summary
    }
    bridge_classes = Counter(str(row["bridge_class"]) for row in bridges)
    head_by_prefix = {str(row["head_prefix"]): row for row in head_summary}
    order_by_pattern = {str(row["pattern"]): row for row in order_control}
    reader_order_by_pattern = {str(row["pattern"]): row for row in reader_order_control}
    expression_population_by = {str(row["population"]): row for row in expression_populations}
    language_profiles = {
        population: {
            str(row["scope"]): {interfix: int(row[f"{interfix.lower()}_occurrences"]) for interfix in M_ORDER}
            for row in registers if row["population"] == population and row["scope_type"] == "LANGUAGE"
        }
        for population in ("FUSED_ONLY", "FUSED_PLUS_ALL_READER_SEPARATED", "CONSERVATIVE_BOUNDARY_NORMALIZED", "INCLUSIVE_LEFT_BOUNDARY")
    }
    fused_surfaces = {str(row["surface"]) for row in occurrences}
    split_only = [row for row in separated if int(row["fused_counterpart_occurrences_elsewhere"]) == 0]
    hierarchy_fused = [row for row in hierarchy if row["population"] == "FUSED_ONLY"]
    hierarchy_inclusive = [row for row in hierarchy if row["population"] == "INCLUSIVE_BOUNDARY_NORMALIZED"]
    o_inner_bases_fused = sorted({base for row in hierarchy_fused if int(row["o_slot"]) for base in str(row["attested_inner_heads"]).split("|") if base})
    o_inner_bases_inclusive = sorted({base for row in hierarchy_inclusive if int(row["o_slot"]) for base in str(row["attested_inner_heads"]).split("|") if base})
    o_missing_bases_fused = sorted({base for row in hierarchy_fused if int(row["o_slot"]) for base in str(row["missing_inner_heads"]).split("|") if base})
    o_missing_bases_inclusive = sorted({base for row in hierarchy_inclusive if int(row["o_slot"]) for base in str(row["missing_inner_heads"]).split("|") if base})
    coexistence_summary = {
        population: {
            "pages_with_two_or_more_interfix_classes": sum(row["population"] == population for row in coexistence),
            "pages_with_three_interfix_classes": sum(row["population"] == population and int(row["distinct_interfixes"]) >= 3 for row in coexistence),
            "pages_with_two_nonempty_interfix_classes": sum(row["population"] == population and int(row["distinct_nonempty_interfixes"]) >= 2 for row in coexistence),
            "pages_with_e_and_o": sum(row["population"] == population and "E" in str(row["interfixes"]).split("|") and "O" in str(row["interfixes"]).split("|") for row in coexistence),
        }
        for population in ("FUSED_ONLY", "FUSED_PLUS_ALL_READER_SEPARATED", "CONSERVATIVE_BOUNDARY_NORMALIZED", "INCLUSIVE_LEFT_BOUNDARY")
    }
    output_hashes = {str(path): sha256(ROOT / path) for key, path in OUTPUTS.items() if key != "result"}
    input_paths = (TOKENS_REL, CROSS_REL, ALLOW_REL, G625_CTH_REL, G631_RUN_REL, G631_RESULT_REL, G631_DICT_REL, G631_VISUAL_REL)
    result_core = {
        "schema": "GDT632_CTH_INTERFIX_LATTICE_RESULT_V1", "experiment_id": "GDT632",
        "status": "COMPLETE_ORDERED_Q_E_O_CTH_HIERARCHY__E_O_MEANINGS_OPEN",
        "guard": {"f1r": "EXCLUDED", "f84": "FORBIDDEN", "f84r": "FORBIDDEN", "new_image_pages": 0, "allowed_pages": len(pages), "token_query": token_stats, "cross_query": cross_stats},
        "family": {
            "fused_occurrences": len(occurrences), "fused_types": len(fused_surfaces),
            "all_reader_separated_expressions": len(separated), "split_only_predicted_expressions": len(split_only),
            "expression_populations": {
                population: {
                    "occurrences": int(row["occurrences"]), "types": int(row["types"]),
                    "pages": int(row["pages"]), "remainders": int(row["remainders"]),
                }
                for population, row in expression_population_by.items()
            },
            "target_q_cth_census": {
                "occurrences": len(occurrences) + len(out_of_lattice),
                "types": len(fused_surfaces | {str(row["surface"]) for row in out_of_lattice}),
                "lattice_occurrences": len(occurrences), "lattice_types": len(fused_surfaces),
                "out_of_lattice_occurrences": len(out_of_lattice),
                "out_of_lattice_types": len({str(row["surface"]) for row in out_of_lattice}),
                "class_counts": dict(sorted(Counter(str(row["classification"]) for row in out_of_lattice).items())),
                "outlier_triple_exact": sum(int(row["triple_exact_token_stable"]) for row in out_of_lattice),
                "outlier_triple_boundary_normalized": sum(int(row["triple_boundary_normalized"]) for row in out_of_lattice),
            },
            "pages": len({str(row["page"]) for row in occurrences} | {str(row["page"]) for row in separated}),
            "strict_fused_occurrences": sum(int(row["in_inherited_cth_surface_deck"]) for row in occurrences),
            "cell_counts": {f"{q}_{interfix}": cell_counts[q, interfix] for q in Q_ORDER for interfix in M_ORDER},
            "fused_remainders": len(matrix), "shared_pair_counts": dict(sorted(pair_counts.items())),
            "reader_bridge_rows": len(bridges), "reader_bridge_classes": dict(sorted(bridge_classes.items())),
            "diagnostic_internal_reader_bridges": sum(int(row["diagnostic_internal_boundary"]) for row in bridges),
            "diagnostic_internal_boundary_spans_total": sum(int(row["diagnostic_internal_boundary"]) for row in bridges) + len(separated),
            "conservative_left_shell_cth_boundary_spans": sum(row["orientation"] == "LEFT_SHELL|CTH" and int(row["total_diagnostic_spans"]) or 0 for row in bridge_summary),
            "inclusive_left_shell_cth_boundary_spans": sum(int(row["left_shell_cth_boundary_visible"]) for row in bridges) + len(separated),
            "alternative_quality_m_cth_boundary_occurrences": sum(int(row["any_reader_occurrences"]) for row in boundary_null),
            "outer_family_boundary_bridges": dict(sorted(Counter(str(row["reader_scope"]) for row in outer_bridges).items())),
        },
        "quality": {"contacts_within_three": len(quality), "immediate_contacts": sum(int(row["distance"]) == 1 for row in quality), "relation_counts": dict(sorted(relation_counts.items())), "local_neighbor_counts": dict(sorted(local_relation_counts.items())), "repeated_frames": len(repeated), "concrete_clauses": len(cases), "same_axis_immediate_by_cell": quality_axis_by_cell, "disposition": "dry/moist is inherited across the lattice; direct same-axis immediate support exists in CH_NONE, CH_O and SH_NONE, not yet E or EO"},
        "ordered_hierarchy": {
            "model": "ch_or_sh + e_optional + [o_optional + cth_remainder]", "coverage_scope": "GLOBAL_TYPE_DECK",
            "inner_head_counts": {prefix: {"occurrences": int(head_by_prefix[prefix]["occurrences"]), "types": int(head_by_prefix[prefix]["types"]), "triple_exact": int(head_by_prefix[prefix]["triple_exact_occurrences"])} for prefix in M_ORDER},
            "fused_o": {
                "expression_occurrences": sum(int(row["expression_occurrences"]) for row in hierarchy_fused if int(row["o_slot"])),
                "expression_types": sum(int(row["expression_types"]) for row in hierarchy_fused if int(row["o_slot"])),
                "covered_occurrences": sum(int(row["occurrences_with_attested_inner_head"]) for row in hierarchy_fused if int(row["o_slot"])),
                "covered_types": sum(int(row["types_with_attested_inner_head"]) for row in hierarchy_fused if int(row["o_slot"])),
                "same_page_covered_occurrences": sum(int(row["occurrences_with_same_page_inner_head"]) for row in hierarchy_fused if int(row["o_slot"])),
                "attested_inner_bases": o_inner_bases_fused, "missing_inner_bases": o_missing_bases_fused,
            },
            "inclusive_o": {
                "expression_occurrences": sum(int(row["expression_occurrences"]) for row in hierarchy_inclusive if int(row["o_slot"])),
                "expression_types": sum(int(row["expression_types"]) for row in hierarchy_inclusive if int(row["o_slot"])),
                "covered_occurrences": sum(int(row["occurrences_with_attested_inner_head"]) for row in hierarchy_inclusive if int(row["o_slot"])),
                "covered_types": sum(int(row["types_with_attested_inner_head"]) for row in hierarchy_inclusive if int(row["o_slot"])),
                "same_page_covered_occurrences": sum(int(row["occurrences_with_same_page_inner_head"]) for row in hierarchy_inclusive if int(row["o_slot"])),
                "attested_inner_bases": o_inner_bases_inclusive, "missing_inner_bases": o_missing_bases_inclusive,
            },
            "expected_eo_order_occurrences": int(order_by_pattern["Q_EO_CTH"]["occurrences"]),
            "reverse_oe_order_occurrences": int(order_by_pattern["Q_OE_CTH"]["occurrences"]),
            "cross_reader_nulls": {pattern: {reader: int(reader_order_by_pattern[pattern][f"{reader}_occurrences"]) for reader in ("zl3b", "it2a", "rf1b")} for pattern in ("FUSED_E_CTH", "FUSED_EO_CTH", "FUSED_OE_CTH", "SPLIT_E|CTH", "SPLIT_EO|CTH", "Q_OE_CTH_ANY_BOUNDARY")},
            "surface_boundary": "reader spacing favors [quality+e?+o?]|CTH; orthographic chunking is distinct from morphological base hierarchy",
        },
        "interfix_disposition": {"NONE": "direct inherited family", "E": "dependent register-skewed local class after ch/sh; lexical meaning OPEN", "O": "productive inner o+CTH head frame; lexical meaning OPEN", "EO": "ordered dependent e plus inner o+CTH frame; lexical meanings OPEN", "quality_axis": "ch=dry and sh=moist remain provisional defaults across all four classes"},
        "register_diagnostic": {"fixed_counts_population": "FUSED_ONLY", "section_B": {"NONE": 36, "E": 29, "O": 0, "EO": 0}, "section_H": {"NONE": 52, "E": 5, "O": 25, "EO": 2}, "hand_1": {"NONE": 38, "E": 2, "O": 28, "EO": 3}, "hand_2": {"NONE": 56, "E": 35, "O": 2, "EO": 1}, "language_profiles": language_profiles, "page_coexistence": coexistence_summary, "disposition": "register effect is strong; same-page coexistence rejects deterministic page/hand replacement but not conditioned allography"},
        "working_dictionary": {"entries": len(dictionary), "inherited_v8": len(dictionary) - 20, "new_v9": 20},
        "claim_boundary": "The preregistered ch/sh by NONE/e/o/eo CTH raster covers 255 of 260 fused Q...CTH tokens and has the ordered hierarchy ch/sh + optional e + [optional o + CTH remainder]. The five outside forms are two ee near-slot rivals and three larger ol/ch compounds. A naked o+CTH row has 32 occurrences and 16 types, while naked e+CTH and eo+CTH rows are empty in every reader. All 46 fused o/eo-prefixed occurrences in 13 surface types reduce to six independently attested inner o+CTH bases; only three share a page with that base. Boundary-normalized expansion covers 54/55 O-bearing expressions and predicts the single missing head octheey. Twelve conservative reader spans expose shell|CTH, and three split-only expressions realize component predictions without an attested fused target. E and O remain silent open class markers, not invented ingredient words. Dry/moist and CTH-material are inherited provisional defaults, not directly reconfirmed in every E/O cell. No phonetics, language, species or full manuscript solution is claimed.",
        "inputs": {str(path): sha256(ROOT / path) for path in input_paths}, "outputs": output_hashes,
    }
    result = {**result_core, "content_sha256": canonical_hash(result_core)}
    (ROOT / OUTPUTS["result"]).write_text(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    head_counts_text = ",".join(f"{key}:{head_by_prefix[key]['occurrences']}" for key in M_ORDER)
    print(f"GDT632 built: fused={len(occurrences)} separated={len(separated)} cells={result_core['family']['cell_counts']} heads={head_counts_text} pairs={dict(pair_counts)} bridges={dict(bridge_classes)} one_sided={len(one_sided_contexts)} coexistence={len(coexistence)} quality={len(quality)} repeated={len(repeated)} cases={len(cases)} dictionary={len(dictionary)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
