#!/usr/bin/env python3
"""Validate and byte-replay GDT632."""

from __future__ import annotations

import csv
import hashlib
import json
import re
import subprocess
import sys
from collections import Counter
from pathlib import Path

sys.dont_write_bytecode = True


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
BASE = ROOT / "experiments/yolo/gdt632_cth_interfix_lattice"
ART = BASE / "artifacts"
RUN = BASE / "src/run.py"
RESULT = ART / "RESULT.json"
VALIDATION = ART / "VALIDATION.json"
V8 = ROOT / "experiments/yolo/gdt631_prefixed_cth_quality_parts/artifacts/WORKING_DICTIONARY_V8.tsv"

GENERATED = (
    ART / "PAGE_ALLOWLIST.tsv",
    ART / "INTERFIX_FAMILY_OCCURRENCES.tsv",
    ART / "OUT_OF_LATTICE_Q_CTH_FORMS.tsv",
    ART / "CROSS_READER_INTERFIX_REALIZATIONS.tsv",
    ART / "CROSS_READER_INTERFIX_BOUNDARY_BRIDGES.tsv",
    ART / "ALL_READER_SEPARATED_SHELL_CTH_SPANS.tsv",
    ART / "EXPRESSION_POPULATION_SUMMARY.tsv",
    ART / "BOUNDARY_ORIENTATION_SUMMARY.tsv",
    ART / "ALTERNATIVE_INTERNAL_BOUNDARY_NULL.tsv",
    ART / "OUTER_FAMILY_BOUNDARY_BRIDGES.tsv",
    ART / "LEFT_QUALITY_SHELLS.tsv",
    ART / "INNER_CTH_HEAD_PREFIX_SUMMARY.tsv",
    ART / "INNER_CTH_HEAD_REMAINDER_MATRIX.tsv",
    ART / "HIERARCHICAL_E_O_BASE_COVERAGE.tsv",
    ART / "E_O_ORDER_CONTROL.tsv",
    ART / "CROSS_READER_E_O_HEAD_CONTROL.tsv",
    ART / "INTERFIX_REMAINDER_MATRIX.tsv",
    ART / "SHARED_REMAINDER_PAIRS.tsv",
    ART / "INTERFIX_CELL_SUMMARY.tsv",
    ART / "INTERFIX_SECTION_PROFILE.tsv",
    ART / "INTERFIX_REGISTER_PROFILE.tsv",
    ART / "INTERFIX_PAGE_COEXISTENCE.tsv",
    ART / "INHERITED_VISUAL_INTERFIX_SCOPE.tsv",
    ART / "HISTORICAL_HYBRID_COMPARATORS.tsv",
    ART / "FIXED_CONTEXT_PARADIGMS.tsv",
    ART / "ONE_SIDED_CONTEXT_PARADIGMS.tsv",
    ART / "SHARED_CATEGORY_SLOTS.tsv",
    ART / "INTERFIX_QUALITY_DEGREE_CONTACTS.tsv",
    ART / "INTERFIX_QUALITY_SUMMARY.tsv",
    ART / "INTERFIX_LOCAL_QUALITY_NEIGHBORS.tsv",
    ART / "REPEATED_INTERFIX_CLAUSE_FRAMES.tsv",
    ART / "CONCRETE_CLAUSES_V4.tsv",
    ART / "INTERFIX_ROLE_RANKING.tsv",
    ART / "WORKING_DICTIONARY_V9.tsv",
    RESULT,
)


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_hash(value: object) -> str:
    raw = json.dumps(value, sort_keys=True, ensure_ascii=True, separators=(",", ":")).encode()
    return hashlib.sha256(raw).hexdigest()


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT))


def main() -> int:
    checks: list[str] = []

    def check(condition: bool, label: str) -> None:
        if not condition:
            raise AssertionError(label)
        checks.append(label)

    check(all(path.is_file() for path in GENERATED), "all generated artifacts exist before replay")
    before = {path: path.read_bytes() for path in GENERATED}
    completed = subprocess.run(
        [sys.executable, str(RUN)], cwd=ROOT, text=True, capture_output=True, check=False,
    )
    check(completed.returncode == 0, "builder exits zero")
    expected = (
        "GDT632 built: fused=255 separated=7 cells={'CH_NONE': 118, 'CH_E': 34, "
        "'CH_O': 23, 'CH_EO': 6, 'SH_NONE': 36, 'SH_E': 21, 'SH_O': 13, 'SH_EO': 4} "
        "heads=NONE:408,E:0,O:32,EO:0 pairs={'NONE': 5, 'E': 3, 'O': 3, 'EO': 1} "
        "bridges={'LEFT_SHELL_TO_CTH_BOUNDARY': 5, 'OUTER_REMAINDER_BOUNDARY': 1, "
        "'MULTIPLE_TARGETS_SAME_LINE': 1, 'LEFT_SHELL_TO_CTH__RIGHT_EDGE_OVERLAP': 1, "
        "'QUALITY_PREFIX_TO_CTH_BOUNDARY': 1} one_sided=12 coexistence=151 quality=97 "
        "repeated=9 cases=49 dictionary=67"
    )
    check(completed.stdout.strip() == expected, "builder summary")
    check(all(path.read_bytes() == before[path] for path in GENERATED), "builder replay is byte-identical")

    result = json.loads(RESULT.read_text(encoding="utf-8"))
    check(result["schema"] == "GDT632_CTH_INTERFIX_LATTICE_RESULT_V1", "result schema")
    check(result["experiment_id"] == "GDT632", "result experiment id")
    check(result["status"] == "COMPLETE_ORDERED_Q_E_O_CTH_HIERARCHY__E_O_MEANINGS_OPEN", "result status")
    content_hash = result["content_sha256"]
    result_core = {key: value for key, value in result.items() if key != "content_sha256"}
    check(content_hash == canonical_hash(result_core), "canonical result hash")

    check(result["guard"] == {
        "allowed_pages": 179,
        "cross_query": {"selected": 4137, "skipped_forbidden": 98, "skipped_not_allowed": 1151},
        "f1r": "EXCLUDED", "f84": "FORBIDDEN", "f84r": "FORBIDDEN", "new_image_pages": 0,
        "token_query": {"selected": 32339, "skipped_forbidden": 709, "skipped_not_allowed": 5940},
    }, "guarded source scope")
    expected_inputs = {
        "transcription/voynich_zl3b_tokens.tsv",
        "transcription/voynich_cross_transcription_lines.tsv",
        "experiments/yolo/gdt631_prefixed_cth_quality_parts/artifacts/PAGE_ALLOWLIST.tsv",
        "experiments/yolo/gdt625_ordered_quality_state_transitions/artifacts/CTH_ROOT_FAMILY.tsv",
        "experiments/yolo/gdt631_prefixed_cth_quality_parts/src/run.py",
        "experiments/yolo/gdt631_prefixed_cth_quality_parts/artifacts/RESULT.json",
        "experiments/yolo/gdt631_prefixed_cth_quality_parts/artifacts/WORKING_DICTIONARY_V8.tsv",
        "experiments/yolo/gdt631_prefixed_cth_quality_parts/artifacts/INHERITED_VISUAL_SCOPE.tsv",
    }
    check(set(result["inputs"]) == expected_inputs, "complete inherited input set")
    for path, digest in result["inputs"].items():
        check(sha256(ROOT / path) == digest, f"input hash {path}")
    for path, digest in result["outputs"].items():
        check(sha256(ROOT / path) == digest, f"output hash {path}")
    check(
        set(result["outputs"]) == {rel(path) for path in GENERATED if path != RESULT},
        "result binds every generated evidence file",
    )

    allow = read_tsv(ART / "PAGE_ALLOWLIST.tsv")
    check(len(allow) == 179 and len({row["page"] for row in allow}) == 179, "179-page allow-list")
    check(all(row["page"] != "f1r" and not row["page"].startswith("f84") for row in allow), "allow-list excludes sealed and sidequest-held folios")

    occurrences = read_tsv(ART / "INTERFIX_FAMILY_OCCURRENCES.tsv")
    check(len(occurrences) == 255, "255 fused four-slot lattice occurrences")
    check(len({row["surface"] for row in occurrences}) == 48, "48 fused lattice types")
    check(len({row["page"] for row in occurrences}) == 104, "104 fused lattice pages")
    check(len({row["remainder"] for row in occurrences}) == 21, "21 fused remainders")
    check(sum(int(row["in_inherited_cth_surface_deck"]) for row in occurrences) == 251, "251 inherited-base fused occurrences")
    check(sum(int(row["triple_exact_token_stable"]) for row in occurrences) == 227, "227 triple-exact fused occurrences")
    check(sum(int(row["triple_boundary_normalized"]) for row in occurrences) == 231, "231 boundary-normalized fused occurrences")
    check(Counter(row["quality_prefix"] for row in occurrences) == Counter({"CH": 181, "SH": 74}), "quality-prefix occurrence partition")
    check(Counter(row["interfix"] for row in occurrences) == Counter({"NONE": 154, "E": 55, "O": 36, "EO": 10}), "interfix occurrence partition")
    check(all(row["interfix_semantics"] == "OPEN" for row in occurrences), "every interfix meaning remains open")
    check(all(row["page"] != "f1r" and not row["page"].startswith("f84") for row in occurrences), "fused occurrences exclude sealed and held folios")
    q_surface = {"CH": "ch", "SH": "sh"}
    m_surface = {"NONE": "", "E": "e", "O": "o", "EO": "eo"}
    for row in occurrences:
        remainder = "" if row["remainder"] == "BARE" else row["remainder"]
        expected_surface = q_surface[row["quality_prefix"]] + m_surface[row["interfix"]] + "cth" + remainder
        check(row["surface"] == expected_surface, f"exact lattice parse {row['occurrence_id']}")

    cells = read_tsv(ART / "INTERFIX_CELL_SUMMARY.tsv")
    expected_cells = {
        ("CH", "NONE"): (118, 115, 20, 20, 74, 102),
        ("CH", "E"): (34, 34, 6, 6, 20, 31),
        ("CH", "O"): (23, 23, 4, 4, 21, 19),
        ("CH", "EO"): (6, 6, 3, 3, 5, 6),
        ("SH", "NONE"): (36, 36, 5, 5, 22, 33),
        ("SH", "E"): (21, 20, 4, 4, 10, 20),
        ("SH", "O"): (13, 13, 4, 4, 13, 13),
        ("SH", "EO"): (4, 4, 2, 2, 4, 3),
    }
    check(len(cells) == 8, "complete two-by-four cell summary")
    for row in cells:
        key = (row["quality_prefix"], row["interfix"])
        observed = tuple(int(row[field]) for field in ("occurrences", "strict_occurrences", "types", "remainders", "pages", "triple_exact_occurrences"))
        check(observed == expected_cells[key], f"cell census {key[0]}_{key[1]}")

    for surface, count, pages, stable in (
        ("chcthy", 75, 53, 69), ("shcthy", 29, 17, 26),
        ("checthy", 26, 17, 24), ("shecthy", 18, 10, 17),
        ("chocthy", 17, 15, 14), ("shocthy", 10, 10, 10),
        ("cheocthy", 4, 3, 4), ("sheocthy", 3, 3, 2),
    ):
        selected = [row for row in occurrences if row["surface"] == surface]
        check(len(selected) == count and len({row["page"] for row in selected}) == pages, f"primary form scope {surface}")
        check(sum(int(row["triple_exact_token_stable"]) for row in selected) == stable, f"primary form stability {surface}")

    outside = read_tsv(ART / "OUT_OF_LATTICE_Q_CTH_FORMS.tsv")
    outside_expected = {
        ("f29r.1", "cheecthy"): "EE_NEAR_SLOT_RIVAL",
        ("f82v.36", "sheecthey"): "EE_NEAR_SLOT_RIVAL",
        ("f34r.15", "cheolchcthy"): "OUTER_OL_CH_COMPOUND",
        ("f3r.10", "cholcthom"): "OUTER_OL_CH_COMPOUND",
        ("f93r.17", "cholchecthody"): "OUTER_OL_CH_COMPOUND",
    }
    check(len(outside) == 5, "five Q-CTH forms outside the preregistered raster")
    check({(row["locus"], row["surface"]): row["classification"] for row in outside} == outside_expected, "exact out-of-lattice census")
    check(Counter(row["classification"] for row in outside) == Counter({"OUTER_OL_CH_COMPOUND": 3, "EE_NEAR_SLOT_RIVAL": 2}), "out-of-lattice class partition")
    check(sum(int(row["triple_exact_token_stable"]) for row in outside) == 3, "three outliers are triple-exact")
    check(sum(int(row["triple_boundary_normalized"]) for row in outside) == 4, "four outliers are boundary-normalized")
    check(all(row["zl3b_mode"] == "FUSED" for row in outside), "all outliers are fused in the source reader")
    outside_modes = {
        row["surface"]: (row["zl3b_mode"], row["it2a_mode"], row["rf1b_mode"])
        for row in outside
    }
    check(outside_modes == {
        "cheecthy": ("FUSED", "FUSED", "FUSED"),
        "sheecthey": ("FUSED", "FUSED", "FUSED"),
        "cheolchcthy": ("FUSED", "FUSED", "FUSED"),
        "cholcthom": ("FUSED", "BOUNDARY_NORMALIZED", "FUSED"),
        "cholchecthody": ("FUSED", "ABSENT_OR_DIFFERENT", "ABSENT_OR_DIFFERENT"),
    }, "exact outlier reader modes")
    check(all(row["page"] != "f1r" and not row["page"].startswith("f84") for row in outside), "out-of-lattice rows exclude sealed and held folios")
    check(not {row["surface"] for row in outside} & {row["surface"] for row in occurrences}, "raster and out-of-lattice types are disjoint")

    reader = read_tsv(ART / "CROSS_READER_INTERFIX_REALIZATIONS.tsv")
    check(len(reader) == 255, "one reader-realization row per fused occurrence")
    check({row["occurrence_id"] for row in reader} == {row["occurrence_id"] for row in occurrences}, "reader realization occurrence coverage")
    check(sum(int(row["triple_exact_token_stable"]) for row in reader) == 227, "reader table preserves exact stability total")
    check(sum(int(row["triple_boundary_normalized"]) for row in reader) == 231, "reader table preserves normalized stability total")
    check(sum(int(row["any_internal_split_reader"]) for row in reader) == 4, "four fused-source rows have an internal split reader")

    bridges = read_tsv(ART / "CROSS_READER_INTERFIX_BOUNDARY_BRIDGES.tsv")
    expected_bridge_classes = Counter({
        "LEFT_SHELL_TO_CTH_BOUNDARY": 5,
        "OUTER_REMAINDER_BOUNDARY": 1,
        "MULTIPLE_TARGETS_SAME_LINE": 1,
        "LEFT_SHELL_TO_CTH__RIGHT_EDGE_OVERLAP": 1,
        "QUALITY_PREFIX_TO_CTH_BOUNDARY": 1,
    })
    check(len(bridges) == 9 and Counter(row["bridge_class"] for row in bridges) == expected_bridge_classes, "nine-row reader bridge partition")
    check(sum(int(row["diagnostic_internal_boundary"]) for row in bridges) == 6, "six conservative reader-internal bridges")
    check(sum(int(row["left_shell_cth_boundary_visible"]) for row in bridges) == 6, "six reader rows expose the left-shell boundary including overlap")
    bridge_by_locus = {row["locus"]: row for row in bridges}
    for locus, surface, bridge_class in (
        ("f102v1.7", "sheocthy", "LEFT_SHELL_TO_CTH_BOUNDARY"),
        ("f114v.33", "cheoctheey", "LEFT_SHELL_TO_CTH_BOUNDARY"),
        ("f20v.7", "shocthy", "MULTIPLE_TARGETS_SAME_LINE"),
        ("f21r.7", "chocthor", "LEFT_SHELL_TO_CTH__RIGHT_EDGE_OVERLAP"),
        ("f21r.9", "shcthey", "QUALITY_PREFIX_TO_CTH_BOUNDARY"),
        ("f21v.5", "shocthy", "LEFT_SHELL_TO_CTH_BOUNDARY"),
        ("f29v.7", "chocthy", "LEFT_SHELL_TO_CTH_BOUNDARY"),
        ("f5r.3", "chocthy", "LEFT_SHELL_TO_CTH_BOUNDARY"),
    ):
        check(bridge_by_locus[locus]["surface"] == surface and bridge_by_locus[locus]["bridge_class"] == bridge_class, f"reader bridge {locus}")
    check(bridge_by_locus["f21r.7"]["span_status"] == "LEFT_BOUNDARY_VALID__RIGHT_EDGE_AMBIGUOUS", "f21 right-edge overlap stays explicit")

    separated = read_tsv(ART / "ALL_READER_SEPARATED_SHELL_CTH_SPANS.tsv")
    check(len(separated) == 7, "seven all-reader shell-to-CTH spans")
    check(Counter(row["interfix"] for row in separated) == Counter({"O": 4, "EO": 2, "E": 1}), "separated-span interfix partition")
    split_only = [row for row in separated if row["evidence_role"] == "ALL_THREE_READERS_SEPARATE__SPLIT_ONLY_PREDICTED_CELL"]
    check(len(split_only) == 3, "three split-only component predictions")
    check({(row["locus"], row["fused_counterpart"]) for row in split_only} == {("f36v.13", "shecthol"), ("f87r.10", "shocthos"), ("f96r.9", "sheocthody")}, "exact split-only predictions")

    populations = {row["population"]: row for row in read_tsv(ART / "EXPRESSION_POPULATION_SUMMARY.tsv")}
    expected_populations = {
        "FUSED_ZL": (255, 48, 255),
        "FUSED_PLUS_ALL_READER_SEPARATED": (262, 51, 7),
        "CONSERVATIVE_BOUNDARY_NORMALIZED": (265, 52, 3),
        "INCLUSIVE_LEFT_BOUNDARY": (266, 53, 1),
    }
    check(set(populations) == set(expected_populations), "four explicitly named expression populations")
    for population, (occurrence_count, type_count, added) in expected_populations.items():
        row = populations[population]
        check((int(row["occurrences"]), int(row["types"]), int(row["added_occurrences"])) == (occurrence_count, type_count, added), f"expression population {population}")

    orientation = {row["orientation"]: row for row in read_tsv(ART / "BOUNDARY_ORIENTATION_SUMMARY.tsv")}
    check(len(orientation) == 5, "five boundary-orientation rows")
    check(orientation["LEFT_SHELL|CTH"]["total_diagnostic_spans"] == "12", "twelve conservative shell-to-CTH spans")
    check(orientation["QUALITY_PREFIX|M_CTH"]["total_diagnostic_spans"] == "0", "no nonempty quality-to-M-CTH split")
    check(orientation["QUALITY_PREFIX|CTH_DIRECT"]["total_diagnostic_spans"] == "1", "one direct quality-to-CTH bridge")
    check(orientation["LEFT_SHELL|CTH_RIGHT_EDGE_AMBIGUOUS"]["alternate_reader_spans"] == "1", "one left-valid right-overlap warning")
    boundary_null = read_tsv(ART / "ALTERNATIVE_INTERNAL_BOUNDARY_NULL.tsv")
    check(len(boundary_null) == 2, "two alternative internal-boundary controls")
    check(all(all(row[f"{reader}_occurrences"] == "0" for reader in ("zl3b", "it2a", "rf1b")) and row["any_reader_occurrences"] == "0" for row in boundary_null), "alternative internal boundaries are empty in every reader")

    outer = read_tsv(ART / "OUTER_FAMILY_BOUNDARY_BRIDGES.tsv")
    check(len(outer) == 5, "five outer family boundary bridges")
    check(Counter(row["reader_scope"] for row in outer) == Counter({"TRIPLE_BOUNDARY_NORMALIZED": 4, "PAIRWISE_ONLY": 1}), "outer bridge reader-scope partition")
    check({row["locus"] for row in outer} == {"f111r.53", "f81r.17", "f81r.29", "f82r.9", "f95v1.3"}, "exact outer bridge loci")

    heads = {row["head_prefix"]: row for row in read_tsv(ART / "INNER_CTH_HEAD_PREFIX_SUMMARY.tsv")}
    expected_heads = {
        "NONE": (408, 69, 69, 125, 347, 408),
        "E": (0, 0, 0, 0, 0, 0),
        "O": (32, 16, 16, 27, 24, 29),
        "EO": (0, 0, 0, 0, 0, 0),
    }
    check(set(heads) == set(expected_heads), "four inner-head prefix rows")
    for prefix, expected_values in expected_heads.items():
        observed = tuple(int(heads[prefix][field]) for field in ("occurrences", "types", "remainders", "pages", "triple_exact_occurrences", "occurrences_with_published_bare_cth_counterpart"))
        check(observed == expected_values, f"inner head census {prefix}")

    hierarchy = read_tsv(ART / "HIERARCHICAL_E_O_BASE_COVERAGE.tsv")
    check(len(hierarchy) == 16, "two complete two-by-four hierarchy populations")
    check(Counter(row["population"] for row in hierarchy) == Counter({"FUSED_ONLY": 8, "INCLUSIVE_BOUNDARY_NORMALIZED": 8}), "hierarchy population partition")
    check(all(row["coverage_scope"] == "GLOBAL_TYPE_DECK" for row in hierarchy), "hierarchy coverage scope is explicit")
    fused_o_rows = [row for row in hierarchy if row["population"] == "FUSED_ONLY" and row["o_slot"] == "1"]
    inclusive_o_rows = [row for row in hierarchy if row["population"] == "INCLUSIVE_BOUNDARY_NORMALIZED" and row["o_slot"] == "1"]
    check((sum(int(row["expression_occurrences"]) for row in fused_o_rows), sum(int(row["expression_types"]) for row in fused_o_rows)) == (46, 13), "fused O-bearing expression scope")
    check((sum(int(row["occurrences_with_attested_inner_head"]) for row in fused_o_rows), sum(int(row["types_with_attested_inner_head"]) for row in fused_o_rows)) == (46, 13), "complete fused O-head coverage")
    check(sum(int(row["occurrences_with_same_page_inner_head"]) for row in fused_o_rows) == 3, "three fused O-head occurrences share a page with the head")
    check((sum(int(row["expression_occurrences"]) for row in inclusive_o_rows), sum(int(row["expression_types"]) for row in inclusive_o_rows)) == (55, 17), "inclusive O-bearing expression scope")
    check((sum(int(row["occurrences_with_attested_inner_head"]) for row in inclusive_o_rows), sum(int(row["types_with_attested_inner_head"]) for row in inclusive_o_rows)) == (54, 16), "inclusive O-head coverage leaves one prediction")
    check({base for row in inclusive_o_rows for base in row["missing_inner_heads"].split("|") if base != "NONE"} == {"octheey"}, "octheey is the sole missing inclusive inner head")
    fused_o_bases = {base for row in fused_o_rows for base in row["attested_inner_heads"].split("|") if base}
    check(fused_o_bases == {"octham", "octhedy", "octhey", "octhody", "octhol", "octhy"}, "six fused inner O-head bases")
    inclusive_o_bases = {base for row in inclusive_o_rows for base in row["attested_inner_heads"].split("|") if base}
    check(inclusive_o_bases == fused_o_bases | {"octhor", "octhos"}, "eight inclusive attested inner O-head bases")

    order = {row["pattern"]: row for row in read_tsv(ART / "E_O_ORDER_CONTROL.tsv")}
    expected_order = {
        "BARE_CTH": (408, 69, 125), "BARE_E_CTH": (0, 0, 0), "BARE_O_CTH": (32, 16, 27),
        "BARE_EO_CTH": (0, 0, 0), "BARE_OE_CTH": (0, 0, 0), "Q_E_CTH": (55, 10, 22),
        "Q_O_CTH": (36, 8, 32), "Q_EO_CTH": (10, 5, 9), "Q_OE_CTH": (0, 0, 0),
    }
    check(set(order) == set(expected_order), "nine ordered E-O controls")
    for pattern, expected_values in expected_order.items():
        observed = tuple(int(order[pattern][field]) for field in ("occurrences", "types", "pages"))
        check(observed == expected_values, f"order control {pattern}")

    reader_order = {row["pattern"]: row for row in read_tsv(ART / "CROSS_READER_E_O_HEAD_CONTROL.tsv")}
    null_patterns = ("FUSED_E_CTH", "FUSED_EO_CTH", "FUSED_OE_CTH", "SPLIT_E|CTH", "SPLIT_EO|CTH", "Q_OE_CTH_ANY_BOUNDARY")
    for pattern in null_patterns:
        check(all(reader_order[pattern][f"{reader}_occurrences"] == "0" for reader in ("zl3b", "it2a", "rf1b")), f"cross-reader null {pattern}")
    check(tuple(reader_order["FUSED_O_CTH"][f"{reader}_occurrences"] for reader in ("zl3b", "it2a", "rf1b")) == ("32", "31", "28"), "cross-reader fused O-head positive control")
    check(tuple(reader_order["SPLIT_O|CTH"][f"{reader}_occurrences"] for reader in ("zl3b", "it2a", "rf1b")) == ("2", "0", "3"), "cross-reader split O-head positive control")

    matrix = read_tsv(ART / "INTERFIX_REMAINDER_MATRIX.tsv")
    check(len(matrix) == 21 and sum(int(row["total_occurrences"]) for row in matrix) == 255, "21-row remainder matrix covers every fused token")
    y_row = next(row for row in matrix if row["remainder"] == "y")
    check(y_row["occupied_cells"] == "8" and y_row["total_occurrences"] == "182", "y occupies all eight lattice cells")
    pairs = read_tsv(ART / "SHARED_REMAINDER_PAIRS.tsv")
    check(len(pairs) == 12 and Counter(row["interfix"] for row in pairs) == Counter({"NONE": 5, "E": 3, "O": 3, "EO": 1}), "twelve shared ch-sh remainder pairs")
    check({row["remainder"] for row in pairs if row["interfix"] == "EO"} == {"y"}, "EO shared pair is the y remainder")

    contexts = read_tsv(ART / "FIXED_CONTEXT_PARADIGMS.tsv")
    check(len(contexts) == 2, "two exact two-cell fixed contexts")
    check({row["cells"] for row in contexts} == {"CH_NONE|SH_NONE", "CH_NONE|SH_E"}, "fixed-context cell pairs")
    one_sided = read_tsv(ART / "ONE_SIDED_CONTEXT_PARADIGMS.tsv")
    check(len(one_sided) == 12 and min(int(row["distinct_cells"]) for row in one_sided) >= 3, "twelve one-sided contexts span at least three cells")
    slots = read_tsv(ART / "SHARED_CATEGORY_SLOTS.tsv")
    check(len(slots) == 4 and Counter(row["surface"] for row in slots) == Counter({"chcthy": 3, "shcthy": 1}), "four shared terminal material slots")

    registers = read_tsv(ART / "INTERFIX_REGISTER_PROFILE.tsv")
    check(len(registers) == 52, "four-population register profile")
    register_by_key = {(row["population"], row["scope_type"], row["scope"]): row for row in registers}
    for scope_type, scope, expected_counts in (
        ("SECTION", "B", (36, 29, 0, 0)), ("SECTION", "H", (52, 5, 25, 2)),
        ("LANGUAGE", "A", (40, 2, 28, 4)), ("LANGUAGE", "B", (114, 53, 8, 6)),
        ("HAND", "1", (38, 2, 28, 3)), ("HAND", "2", (56, 35, 2, 1)),
    ):
        row = register_by_key[("FUSED_ONLY", scope_type, scope)]
        observed = tuple(int(row[f"{interfix}_occurrences"]) for interfix in ("none", "e", "o", "eo"))
        check(observed == expected_counts, f"fused register profile {scope_type} {scope}")
    for language, expected_counts in (("A", (41, 3, 34, 5)), ("B", (114, 53, 8, 8))):
        row = register_by_key[("INCLUSIVE_LEFT_BOUNDARY", "LANGUAGE", language)]
        observed = tuple(int(row[f"{interfix}_occurrences"]) for interfix in ("none", "e", "o", "eo"))
        check(observed == expected_counts, f"inclusive language profile {language}")
    coexistence = read_tsv(ART / "INTERFIX_PAGE_COEXISTENCE.tsv")
    check(len(coexistence) == 151, "151 four-population coexistence rows")
    for population, expected_values in (
        ("FUSED_ONLY", (36, 4, 5, 1)),
        ("FUSED_PLUS_ALL_READER_SEPARATED", (38, 4, 6, 1)),
        ("CONSERVATIVE_BOUNDARY_NORMALIZED", (38, 4, 6, 1)),
        ("INCLUSIVE_LEFT_BOUNDARY", (39, 4, 6, 1)),
    ):
        selected = [row for row in coexistence if row["population"] == population]
        observed = (
            len(selected),
            sum(int(row["distinct_interfixes"]) >= 3 for row in selected),
            sum(int(row["distinct_nonempty_interfixes"]) >= 2 for row in selected),
            sum("E" in row["interfixes"].split("|") and "O" in row["interfixes"].split("|") for row in selected),
        )
        check(observed == expected_values, f"page coexistence {population}")

    quality = read_tsv(ART / "INTERFIX_QUALITY_DEGREE_CONTACTS.tsv")
    check(len(quality) == 97 and sum(row["distance"] == "1" for row in quality) == 55, "97 local degree contacts, 55 immediate")
    check(Counter(row["prefix_axis_relation"] for row in quality) == Counter({"ORTHOGONAL_AXIS": 89, "MATCHING_PREFIX_AXIS": 7, "OPPOSITE_PREFIX_AXIS": 1}), "degree-contact relation partition")
    quality_summary = read_tsv(ART / "INTERFIX_QUALITY_SUMMARY.tsv")
    check(len(quality_summary) == 8, "one quality summary per lattice cell")
    immediate_axis = {
        f"{row['quality_prefix']}_{row['interfix']}": (int(row["matching_immediate"]), int(row["opposite_immediate"]))
        for row in quality_summary
    }
    check(immediate_axis == {
        "CH_NONE": (3, 0), "CH_E": (0, 0), "CH_O": (1, 0), "CH_EO": (0, 0),
        "SH_NONE": (1, 0), "SH_E": (0, 0), "SH_O": (0, 0), "SH_EO": (0, 0),
    }, "direct same-axis immediate support remains cell-limited")
    local_quality = read_tsv(ART / "INTERFIX_LOCAL_QUALITY_NEIGHBORS.tsv")
    check(len(local_quality) == 36 and Counter(row["prefix_axis_relation"] for row in local_quality) == Counter({"MATCHING_PREFIX_AXIS": 20, "OPPOSITE_PREFIX_AXIS": 8, "ORTHOGONAL_AXIS": 8}), "broader immediate-neighbor relation partition")
    repeated = read_tsv(ART / "REPEATED_INTERFIX_CLAUSE_FRAMES.tsv")
    check(len(repeated) == 9, "nine repeated concrete clause frames")
    repeated_by_clause = {row["surface_clause"]: row for row in repeated}
    for clause, count, stable in (
        ("chcthy qokain", "4", "4"), ("qokain chcthy", "4", "3"),
        ("qokain checthy", "4", "4"), ("qokaiin shcthy", "3", "3"),
        ("qotain shcthy", "3", "3"),
    ):
        check(repeated_by_clause[clause]["occurrences"] == count and repeated_by_clause[clause]["triple_stable_occurrences"] == stable, f"repeated clause {clause}")
    cases = read_tsv(ART / "CONCRETE_CLAUSES_V4.tsv")
    check(len(cases) == 49, "49 concrete boundary-stable clauses")
    check(Counter(row["interfix"] for row in cases) == Counter({"NONE": 34, "E": 11, "O": 3, "EO": 1}), "concrete-clause interfix partition")
    check(all(row["interfix_semantics"] == "OPEN" and "OPEN" in row["residual_policy"] for row in cases), "case interfixes and residuals stay open")

    visual = read_tsv(ART / "INHERITED_VISUAL_INTERFIX_SCOPE.tsv")
    check(len(visual) == 4 and all(row["new_image_opened"] == "0" for row in visual), "four inherited visual limits and no new image")
    check(all(row["e_o_target_on_inherited_image"] == "0" for row in visual), "no inherited image carries an E-O target")
    historical = read_tsv(ART / "HISTORICAL_HYBRID_COMPARATORS.tsv")
    check(len(historical) == 2 and {row["manuscript"] for row in historical} == {"Pal.lat.1256", "Wellcome MS 542"}, "two period hybrid comparators")
    check(all(row["source_url"].startswith("https://") and row["image_url"].startswith("https://") for row in historical), "historical comparator source and image URLs")
    check(all("nicht" in row["limit_de"] or "kein" in row["limit_de"] for row in historical), "historical comparator claim limits")

    ranking = read_tsv(ART / "INTERFIX_ROLE_RANKING.tsv")
    check(len(ranking) == 5 and [row["rank"] for row in ranking] == ["1", "2", "3", "4", "5"], "five ranked interfix models")
    check(ranking[0]["model"] == "ORDERED_Q_E_O_CTH_HIERARCHY" and ranking[0]["disposition"] == "PRIMARY_MORPHOLOGICAL_STRUCTURE__E_O_OPEN", "ordered hierarchy ranks first with open semantics")
    check(ranking[-1]["model"] == "INDEPENDENT_WHOLE_WORDS" and ranking[-1]["disposition"] == "REJECTED_AS_PRIMARY", "independent whole-word model rejected as primary")
    old_dictionary = read_tsv(V8)
    dictionary = read_tsv(ART / "WORKING_DICTIONARY_V9.tsv")
    check(len(old_dictionary) == 47 and len(dictionary) == 67, "V9 consolidates forty-seven plus twenty entries")
    check(dictionary[:47] == old_dictionary, "all V8 entries retained byte-for-field")
    new_entries = {row["entry"]: row for row in dictionary[47:]}
    for entry in (
        "cth+R", "o+cth+R", "e nach ch/sh", "ch/sh+e?+[o?+cth+R]", "-y in CTH", "ch-", "sh-",
        "che-", "she-", "cho-", "sho-", "cheo-", "sheo-", "checthy", "shecthy", "chocthy",
        "shocthy", "cheocthy", "sheocthy", "[ch|sh]+e?+o? | CTH",
    ):
        check(entry in new_entries, f"V9 entry {entry}")

    family = result["family"]
    check(family["cell_counts"] == {"CH_NONE": 118, "CH_E": 34, "CH_O": 23, "CH_EO": 6, "SH_NONE": 36, "SH_E": 21, "SH_O": 13, "SH_EO": 4}, "result cell counts")
    check(family["target_q_cth_census"] == {
        "occurrences": 260, "types": 53, "lattice_occurrences": 255, "lattice_types": 48,
        "out_of_lattice_occurrences": 5, "out_of_lattice_types": 5,
        "class_counts": {"EE_NEAR_SLOT_RIVAL": 2, "OUTER_OL_CH_COMPOUND": 3},
        "outlier_triple_exact": 3, "outlier_triple_boundary_normalized": 4,
    }, "result binds full Q-CTH census and raster ceiling")
    check(family["expression_populations"] == {
        "FUSED_ZL": {"occurrences": 255, "types": 48, "pages": 104, "remainders": 21},
        "FUSED_PLUS_ALL_READER_SEPARATED": {"occurrences": 262, "types": 51, "pages": 104, "remainders": 22},
        "CONSERVATIVE_BOUNDARY_NORMALIZED": {"occurrences": 265, "types": 52, "pages": 105, "remainders": 23},
        "INCLUSIVE_LEFT_BOUNDARY": {"occurrences": 266, "types": 53, "pages": 105, "remainders": 23},
    }, "result expression populations")
    check(family["reader_bridge_rows"] == 9 and family["diagnostic_internal_reader_bridges"] == 6, "result reader bridge totals")
    check(family["conservative_left_shell_cth_boundary_spans"] == 12 and family["inclusive_left_shell_cth_boundary_spans"] == 13, "result conservative and inclusive shell boundaries")
    check(family["alternative_quality_m_cth_boundary_occurrences"] == 0, "result alternative boundary null")

    ordered = result["ordered_hierarchy"]
    check(ordered["model"] == "ch_or_sh + e_optional + [o_optional + cth_remainder]", "result ordered hierarchy model")
    check(ordered["coverage_scope"] == "GLOBAL_TYPE_DECK", "result hierarchy scope")
    check(ordered["inner_head_counts"] == {
        "NONE": {"occurrences": 408, "types": 69, "triple_exact": 347},
        "E": {"occurrences": 0, "types": 0, "triple_exact": 0},
        "O": {"occurrences": 32, "types": 16, "triple_exact": 24},
        "EO": {"occurrences": 0, "types": 0, "triple_exact": 0},
    }, "result inner-head counts")
    check(ordered["fused_o"] == {
        "expression_occurrences": 46, "expression_types": 13,
        "covered_occurrences": 46, "covered_types": 13,
        "same_page_covered_occurrences": 3,
        "attested_inner_bases": ["octham", "octhedy", "octhey", "octhody", "octhol", "octhy"],
        "missing_inner_bases": [],
    }, "result fused O hierarchy")
    check(ordered["inclusive_o"]["expression_occurrences"] == 55 and ordered["inclusive_o"]["expression_types"] == 17, "result inclusive O scope")
    check(ordered["inclusive_o"]["covered_occurrences"] == 54 and ordered["inclusive_o"]["covered_types"] == 16, "result inclusive O coverage")
    check(ordered["inclusive_o"]["attested_inner_bases"] == ["octham", "octhedy", "octhey", "octhody", "octhol", "octhor", "octhos", "octhy"], "result inclusive O bases")
    check(ordered["inclusive_o"]["missing_inner_bases"] == ["octheey"], "result octheey prediction")
    check(ordered["expected_eo_order_occurrences"] == 10 and ordered["reverse_oe_order_occurrences"] == 0, "result E-O order direction")
    check(all(value == 0 for readers in ordered["cross_reader_nulls"].values() for value in readers.values()), "result cross-reader null controls")

    check(result["quality"]["contacts_within_three"] == 97 and result["quality"]["immediate_contacts"] == 55, "result quality totals")
    check(result["quality"]["repeated_frames"] == 9 and result["quality"]["concrete_clauses"] == 49, "result concrete clause totals")
    check(result["working_dictionary"] == {"entries": 67, "inherited_v8": 47, "new_v9": 20}, "result dictionary summary")
    check(result["register_diagnostic"]["page_coexistence"]["FUSED_ONLY"]["pages_with_two_or_more_interfix_classes"] == 36, "result fused page coexistence")
    check(result["register_diagnostic"]["page_coexistence"]["FUSED_PLUS_ALL_READER_SEPARATED"]["pages_with_two_or_more_interfix_classes"] == 38, "result expanded page coexistence")

    filler_pattern = re.compile(r"Arbeitsgut|Arbeitsschritt|ausf(?:ü|ue)hren|weiterleiten|leite\s+weiter", re.IGNORECASE)
    semantic_texts = [row["working_reading_de"] for row in cases]
    semantic_texts.extend(row["working_meaning_de"] for row in dictionary)
    semantic_texts.extend(row["working_model_de"] for row in ranking)
    check(not any(filler_pattern.search(value) for value in semantic_texts), "no generic filler pseudo-translation")

    privacy_pattern = re.compile(
        "/" + r"home/|/" + r"tmp/|BEGIN (?:RSA |EC |OPENSSH |DSA )?PRIVATE KEY|AKIA[0-9A-Z]{16}|"
        r"gh[pousr]_[A-Za-z0-9]{20,}|xox[baprs]-|password\s*[=:]|api[_-]?key\s*[=:]|secret\s*[=:]",
        re.IGNORECASE,
    )
    required = (
        BASE / "README.md", BASE / "METHOD.md", BASE / "REPORT.md", BASE / "experiment.json",
        ART / "README.md", *GENERATED, RUN, BASE / "src/validate.py",
    )
    for path in required:
        check(path.is_file(), f"required file {rel(path)}")
        check(not privacy_pattern.search(path.read_text(encoding="utf-8")), f"privacy scan {rel(path)}")

    payload = {
        "schema": "GDT632_VALIDATION_V1",
        "experiment_id": "GDT632",
        "status": "PASS",
        "check_count": len(checks),
        "checks": checks,
        "result_sha256": sha256(RESULT),
    }
    VALIDATION.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"checks": len(checks), "status": "PASS"}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
