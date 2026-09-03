#!/usr/bin/env python3
"""Strictly validate GDT768 and byte-replay every declared builder output."""

from __future__ import annotations

import argparse
import csv
import importlib.util
import json
import math
import re
import subprocess
import sys
import tempfile
from collections import Counter, defaultdict
from pathlib import Path
from types import ModuleType
from typing import Iterable, Mapping, Sequence

sys.dont_write_bytecode = True


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
EXP = ROOT / "experiments/yolo/gdt768_chor_shor_part_identity_tournament"
SRC = EXP / "src"
DEFAULT_ARTIFACTS = EXP / "artifacts"
RUN_PATH = SRC / "run.py"
CORE_PATH = SRC / "core_atlas.py"

CORE_OUTPUTS = {
    "occurrences": "ANCHOR_404_OCCURRENCE_ATLAS.tsv",
    "multi": "MULTI_ANCHOR_33_LINE_ATLAS.tsv",
    "pairs": "ANCHOR_15_PAIR_SUMMARY.tsv",
    "ablation": "ANCHOR_6X3X3_FAMILY_ABLATION.tsv",
    "roles": "ANCHOR_6_ROLE_GEOMETRY.tsv",
}
MODEL_METRICS_NAME = "MODEL_OBSERVED_METRICS.tsv"
MODEL_EVIDENCE_NAME = "MODEL_5_FEATURE_EVIDENCE.tsv"
MODEL_SCOREBOARD_NAME = "MODEL_5_SCOREBOARD.tsv"
DICTIONARY_NAME = "GDT768_6_WORKING_DICTIONARY.tsv"
READER_NAME = "TWELVE_COMPLETE_LINE_READER.tsv"
HISTORICAL_READER_NAME = "HISTORICAL_PART_REGISTER_READER.md"
RESULT_NAME = "RESULT.json"

SOURCE_SPECS = {
    "anchors": SRC / "ANCHOR_6_DEFAULT_SPECS.tsv",
    "features": SRC / "COMPARISON_FEATURE_SPECS.tsv",
    "history": SRC / "HISTORICAL_PART_SIGNATURES.tsv",
    "models": SRC / "MODEL_5_SPECS.tsv",
}

TARGET_COUNTS = Counter(
    {"chor": 176, "shor": 77, "cthy": 85, "dair": 63, "kooiin": 2, "koaiin": 1}
)
PAIR_COUNTS = {
    frozenset(("chor", "cthy")): (14, 11, 5),
    frozenset(("cthy", "shor")): (8, 7, 3),
    frozenset(("chor", "shor")): (8, 8, 3),
    frozenset(("chor", "dair")): (5, 5, 2),
}
FAMILY_D1_DRY_MOIST = {
    ("chor", 0): (45, 9),
    ("chor", 1): (28, 9),
    ("chor", 2): (12, 7),
    ("shor", 0): (8, 12),
    ("shor", 1): (8, 5),
    ("shor", 2): (7, 2),
}
GDT754_SCOPE_EXPOSURES = {
    ("chor", "D1"): 8,
    ("chor", "R3"): 18,
    ("chor", "LINE"): 26,
    ("shor", "D1"): 0,
    ("shor", "R3"): 4,
    ("shor", "LINE"): 9,
    ("cthy", "D1"): 7,
    ("cthy", "R3"): 8,
    ("cthy", "LINE"): 11,
    ("dair", "D1"): 1,
    ("dair", "R3"): 1,
    ("dair", "LINE"): 8,
    ("kooiin", "D1"): 0,
    ("kooiin", "R3"): 0,
    ("kooiin", "LINE"): 0,
    ("koaiin", "D1"): 0,
    ("koaiin", "R3"): 0,
    ("koaiin", "LINE"): 0,
}
EXPECTED_MODEL_SCORES = {
    "M01": 0.644178,
    "M02": 0.820437,
    "M03": 0.820437,
    "M04": 0.631987,
    "M05": 0.132523,
}

READER_COLUMNS = {
    "line_rank", "locus", "line_class", "ordinal", "surface",
    "reader_exact", "portable_role_de", "concrete_default_de",
    "working_confidence", "positive_evidence_de", "counterevidence_de",
    "primary_rival_de", "structural_only", "line_working_reader_de",
    "line_finding_de", "confirmed_plaintext", "confirmed_lexeme",
    "component_export_credit",
}
ZERO_FIELDS = {
    "confirmed_lexeme", "confirmed_lexemes", "confirmed_plaintext",
    "confirmed_plaintext_clause", "confirmed_plaintext_clauses",
    "plaintext_clauses", "component_credit", "component_export_credit",
    "component_exports", "component_values", "confirmed_components",
    "identity_credit", "lexical_credit", "confirmed_english_lexemes",
    "confirmed_german_lexemes", "identified_component_values",
}
NAKED_OLD_GLOSS = re.compile(
    r"(?i)(?<![a-z])`?(?:ol|r|s|l|o)`?\s*(?:=|->|→|:)\s*"
    r"`?(?:wurzel(?:teil|droge)?|radix|samen|saat(?:gut)?|holz(?:droge)?|"
    r"lignum|wasser|aqua|öl|oel|oleum)`?(?![a-z])"
)
OLD_SINGLE_SURFACE_GLOSSES = {
    "r": ("wurzel", "radix"),
    "s": ("samen", "saat"),
    "l": ("holz", "lignum"),
    "o": ("wasser", "aqua"),
    "ol": ("öl", "oel", "oleum"),
}
ACTIVE_SEMANTIC_MARKERS = (
    "portable", "concrete", "default", "renderer", "translation",
    "selected_meaning", "working_role",
)
INACTIVE_SEMANTIC_MARKERS = (
    "rival", "counter", "evidence", "warning", "caveat", "old_",
    "prior_", "historical", "finding",
)


def load_module(name: str, path: Path) -> ModuleType:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load module: {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def read_tsv(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle, delimiter="\t")
        fields = list(reader.fieldnames or ())
        if not fields or len(fields) != len(set(fields)):
            raise AssertionError(f"invalid or duplicate TSV header: {path.name}")
        rows = list(reader)
    return fields, rows


def pipe_items(value: object) -> tuple[str, ...]:
    text = str(value)
    if not text or text == "NONE":
        return ()
    return tuple(item for item in text.split("|") if item)


def is_zero(value: object) -> bool:
    return value is False or value == 0 or str(value).strip().lower() in {
        "0", "false", "none", "zero",
    }


def required_columns(fields: Sequence[str], required: Iterable[str], label: str) -> None:
    missing = set(required) - set(fields)
    if missing:
        raise AssertionError(f"{label} missing columns: {sorted(missing)}")


def numeric(mapping: Mapping[str, object], aliases: Sequence[str], label: str) -> int:
    for name in aliases:
        if name in mapping:
            return int(mapping[name])
    raise AssertionError(f"missing numeric field {label}; accepted aliases={aliases}")


def column(fields: Sequence[str], aliases: Sequence[str], label: str) -> str:
    for name in aliases:
        if name in fields:
            return name
    raise AssertionError(f"missing column {label}; accepted aliases={aliases}")


def parse_weights(value: str) -> dict[str, float]:
    result: dict[str, float] = {}
    for item in pipe_items(value):
        feature, weight = item.split(":", 1)
        result[feature] = float(weight)
    return result


def pipe_cell(values: Iterable[object]) -> str:
    items = [str(value) for value in values]
    return "|".join(items) if items else "NONE"


def json_cell(value: object) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def donor_cell(rows: Sequence[Mapping[str, object]]) -> str:
    if not rows:
        return "NONE"
    return ";".join(
        f"{row['surface']}@{row['ordinal']}:d{row['distance']}"
        f"[{pipe_cell(row.get('features', ()))}]"
        for row in rows
    )


def blocked_cell(rows: Sequence[Mapping[str, object]]) -> str:
    if not rows:
        return "NONE"
    return ";".join(
        f"{row['surface']}@{row['ordinal']}:d{row['distance']}" for row in rows
    )


def same_cell(actual: object, expected: object) -> bool:
    """Compare a TSV scalar to an in-memory scalar without type ambiguity."""

    if isinstance(expected, bool):
        return str(actual).strip().lower() in ({"1", "true"} if expected else {"0", "false"})
    if isinstance(expected, float):
        try:
            return math.isclose(float(actual), expected, rel_tol=0.0, abs_tol=5e-7)
        except (TypeError, ValueError):
            return False
    return str(actual) == str(expected)


def recursive_zero_checks(value: object, check, path: str = "result") -> int:
    hits = 0
    if isinstance(value, Mapping):
        for key, item in value.items():
            child = f"{path}.{key}"
            lowered = str(key).lower()
            if (
                lowered in ZERO_FIELDS
                or lowered.startswith("confirmed_")
                or lowered.endswith("_identity_credit")
                or lowered.endswith("_component_credit")
                or lowered.endswith("_component_export_credit")
                or lowered.endswith("_component_values")
            ):
                check(is_zero(item), f"zero claim field {child}")
                hits += 1
            hits += recursive_zero_checks(item, check, child)
    elif isinstance(value, list):
        for index, item in enumerate(value):
            hits += recursive_zero_checks(item, check, f"{path}[{index}]")
    return hits


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--artifacts-dir", type=Path, default=DEFAULT_ARTIFACTS)
    parser.add_argument("--check-only", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    art = args.artifacts_dir if args.artifacts_dir.is_absolute() else ROOT / args.artifacts_dir
    run = load_module("gdt768_run_for_validation", RUN_PATH)
    core_module = load_module("gdt768_core_independent_validation", CORE_PATH)
    checks = 0

    def check(condition: bool, message: str) -> None:
        nonlocal checks
        checks += 1
        if not condition:
            raise AssertionError(message)

    # The builder owns the output contract.  The validator deliberately imports
    # that tuple instead of maintaining an independently drifting file list.
    check(hasattr(run, "OUTPUT_NAMES"), "run.py does not declare OUTPUT_NAMES")
    declared = tuple(str(name) for name in run.OUTPUT_NAMES)
    check(bool(declared), "OUTPUT_NAMES is empty")
    check(len(declared) == len(set(declared)), "OUTPUT_NAMES contains duplicates")
    check(
        all(Path(name).name == name and name not in {"", ".", ".."} for name in declared),
        "OUTPUT_NAMES must contain safe artifact basenames only",
    )
    check("VALIDATION.json" not in declared, "VALIDATION.json must not be a builder output")
    planned = {
        *CORE_OUTPUTS.values(),
        MODEL_METRICS_NAME,
        MODEL_EVIDENCE_NAME,
        MODEL_SCOREBOARD_NAME,
        DICTIONARY_NAME,
        READER_NAME,
        HISTORICAL_READER_NAME,
        RESULT_NAME,
    }
    check(set(declared) == planned, f"unexpected declared output contract: {declared}")
    check(art.is_dir(), f"artifact directory missing: {art}")
    for name in declared:
        path = art / name
        check(path.is_file(), f"declared artifact missing: {name}")
        check(path.stat().st_size > 0, f"declared artifact empty: {name}")

    tables: dict[str, tuple[list[str], list[dict[str, str]]]] = {}
    for name in declared:
        if name.endswith(".tsv"):
            tables[name] = read_tsv(art / name)
            check(bool(tables[name][1]), f"TSV has no rows: {name}")
    result = json.loads((art / RESULT_NAME).read_text(encoding="utf-8"))
    historical_reader = (art / HISTORICAL_READER_NAME).read_text(encoding="utf-8")

    # Declarative decks are part of the executable claim boundary: each one is
    # complete, internally unique, foreign-key clean, and exports no identity.
    source_tables = {name: read_tsv(path) for name, path in SOURCE_SPECS.items()}
    anchor_fields, anchor_specs = source_tables["anchors"]
    feature_fields, feature_specs = source_tables["features"]
    history_fields, history_specs = source_tables["history"]
    model_fields, model_specs = source_tables["models"]
    check(len(anchor_specs) == 6, "anchor specification must have six rows")
    check(len(feature_specs) == 13, "comparison deck must have thirteen rows")
    check(len(history_specs) == 9, "historical deck must have nine rows")
    check(len(model_specs) == 5, "model deck must have five rows")
    check(
        Counter(row["surface"] for row in anchor_specs)
        == Counter({surface: 1 for surface in TARGET_COUNTS}),
        "anchor specification target forms changed",
    )
    check(
        {row["feature_id"] for row in feature_specs}
        == {f"CF{number:02d}" for number in range(1, 14)},
        "comparison feature identifiers changed",
    )
    check(
        {row["signature_id"] for row in history_specs}
        == {f"HP{number:02d}" for number in range(1, 10)},
        "historical signature identifiers changed",
    )
    check(
        {row["model_id"] for row in model_specs}
        == {f"M{number:02d}" for number in range(1, 6)},
        "model identifiers changed",
    )
    for label, (fields, rows) in source_tables.items():
        zero_columns = ZERO_FIELDS & set(fields)
        check(bool(zero_columns), f"{label} deck exposes no explicit zero-credit field")
        for row_number, row in enumerate(rows, 2):
            for field in zero_columns:
                check(is_zero(row[field]), f"{label}:{row_number} has nonzero {field}")
    feature_ids = {row["feature_id"] for row in feature_specs}
    history_ids = {row["signature_id"] for row in history_specs}
    model_weight_maps: dict[str, dict[str, float]] = {}
    for row in model_specs:
        weights = parse_weights(row["feature_weights"])
        model_weight_maps[row["model_id"]] = weights
        check(bool(weights), f"{row['model_id']} has no feature weights")
        check(set(weights) <= feature_ids, f"{row['model_id']} references unknown features")
        check(all(weight > 0 for weight in weights.values()), f"{row['model_id']} has nonpositive weight")
        check(
            set(pipe_items(row["historical_signature_ids"])) <= history_ids,
            f"{row['model_id']} references unknown historical signatures",
        )

    # Rebuild the guarded in-memory atlas independently of every serialized
    # artifact.  This is the reference object for all exact table comparisons.
    core = core_module.build_core_atlas(ROOT)
    metadata = core["metadata"]
    check(metadata["target_occurrences"] == 404, "core target occurrence gate != 404")
    check(Counter(metadata["anchor_counts"]) == TARGET_COUNTS, "core anchor counts changed")
    check(tuple(metadata["target_forms"]) == tuple(TARGET_COUNTS), "core target order changed")
    check(metadata["multi_anchor_lines"] == 33, "core multi-anchor line gate != 33")
    check(metadata["multi_anchor_pages"] == 26, "core multi-anchor page gate != 26")
    check(len(core["pair_summary"]) == 15, "core unordered pair gate != 15")
    check(len(core["role_geometry"]) == 6, "core role row gate != 6")
    check(len(core["family_ablation"]) == 54, "core ablation row gate != 54")
    check(
        metadata["gdt754_source_composed_surface_count"] == 172,
        "GDT754 quarantine inventory gate != 172",
    )
    check(
        metadata["gdt754_source_composed_target_context_exposures"] == 54,
        "GDT754 target-context exposure gate != 54",
    )
    check(
        metadata["gdt754_source_composed_unique_target_line_positions"] == 48,
        "GDT754 unique target-line-position gate != 48",
    )
    check(
        metadata["gdt754_source_composed_unique_target_line_surfaces"] == 27,
        "GDT754 unique target-line-surface gate != 27",
    )
    check(metadata["guard"]["selected"] == 4137, "guard selected gate changed")
    check(metadata["guard"]["skipped_forbidden"] == 98, "guard forbidden gate changed")
    check(metadata["guard"]["skipped_not_allowed"] == 1150, "guard allow-list gate changed")
    check(metadata["f84_accessed"] is False, "core reports f84 access")
    check(metadata["f84r_accessed"] is False, "core reports f84r access")

    source_composed = core_module.load_gdt754_source_composed_surfaces(ROOT)
    check(len(source_composed) == 172, "loaded GDT754 quarantine is not 172 unique surfaces")
    check(not set(TARGET_COUNTS) & set(source_composed), "target entered GDT754 quarantine")
    exposed_positions: set[tuple[str, int]] = set()
    exposed_surface_positions: set[tuple[str, int, str]] = set()
    for occurrence in core["occurrences"]:
        locus = str(occurrence["locus"])
        check(not locus.lower().startswith("f84"), f"sealed locus entered core: {locus}")
        for radius in (0, 1, 2):
            for scope in ("D1", "R3", "LINE"):
                view = occurrence["family_views"][radius]["scope"][scope]
                donors = {str(item["surface"]) for item in view["donors"]}
                blocked = {
                    (str(item["surface"]), int(item["ordinal"]))
                    for item in view["blocked_source_composed_donors"]
                }
                check(not donors & source_composed, "GDT754 surface leaked into eligible donors")
                check(
                    {surface for surface, _token_index in blocked} <= source_composed,
                    "non-GDT754 surface entered source-composed block",
                )
                if radius == 0 and scope == "LINE":
                    for surface, ordinal in blocked:
                        exposed_positions.add((locus, ordinal))
                        exposed_surface_positions.add(
                            (str(occurrence["target_occurrence_id"]), locus, ordinal, surface)
                        )
    check(len(exposed_surface_positions) == 54, "reconstructed GDT754 exposures != 54")
    check(len(exposed_positions) == 48, "reconstructed GDT754 unique positions != 48")

    pair_lookup = {
        frozenset((row["first_surface"], row["second_surface"])): row
        for row in core["pair_summary"]
    }
    for pair, expected in PAIR_COUNTS.items():
        row = pair_lookup[pair]
        actual = (row["line_count"], row["page_count"], row["direct_pair_count"])
        check(actual == expected, f"core pair count changed for {sorted(pair)}: {actual}")

    ablation_lookup = {
        (row["target_surface"], row["family_radius"], row["scope"]): row
        for row in core["family_ablation"]
    }
    check(len(ablation_lookup) == 54, "core ablation keys are not unique")
    for (target, radius), expected in FAMILY_D1_DRY_MOIST.items():
        row = ablation_lookup[target, radius, "D1"]
        actual = (
            row["feature_occurrence_counts"]["DRY"],
            row["feature_occurrence_counts"]["MOIST"],
        )
        check(actual == expected, f"family D1 dry/moist changed for {target} ED{radius}")
    for (target, scope), expected in GDT754_SCOPE_EXPOSURES.items():
        values = {
            int(ablation_lookup[target, radius, scope]["source_composed_blocked_donor_positions"])
            for radius in (0, 1, 2)
        }
        check(values == {expected}, f"GDT754 block changed for {target}/{scope}: {values}")

    # Exact serialization rebound: no atlas row may merely have the right row
    # count while pointing at a different token, line, family view, or gate.
    occurrence_fields, occurrence_rows = tables[CORE_OUTPUTS["occurrences"]]
    occurrence_base = [
        "target_occurrence_id", "surface", "page", "physical_folio", "locus",
        "line_number", "section", "language", "hand", "ordinal", "token_index",
        "line_token_count", "line_position", "normalized_line_position",
        "paragraph_start_line", "paragraph_end_line", "true_paragraph_opener",
        "true_paragraph_closer", "written_line_eva",
    ]
    occurrence_view_fields: list[str] = []
    for radius in (0, 1, 2):
        for scope in ("d1", "r3", "line"):
            stem = f"ed{radius}_{scope}"
            occurrence_view_fields.extend(
                [
                    f"{stem}_features", f"{stem}_donors", f"{stem}_family_blocked",
                    f"{stem}_source_composed_blocked", f"{stem}_eligible_positions",
                    f"{stem}_family_blocked_positions",
                    f"{stem}_source_composed_blocked_positions",
                ]
            )
    expected_occurrence_fields = occurrence_base + occurrence_view_fields + [
        "reader_exact", "gdt754_source_composed_gate",
        "edit_distance_semantic_credit", "component_export_credit",
    ]
    check(occurrence_fields == expected_occurrence_fields, "occurrence atlas schema/order changed")
    check(len(occurrence_rows) == 404, "occurrence artifact row gate != 404")
    occurrence_by_id = {row["target_occurrence_id"]: row for row in occurrence_rows}
    check(len(occurrence_by_id) == 404, "occurrence artifact IDs are not unique")
    for expected in core["occurrences"]:
        identity = expected["target_occurrence_id"]
        check(identity in occurrence_by_id, f"missing occurrence artifact row {identity}")
        actual = occurrence_by_id[identity]
        for field in occurrence_base:
            check(
                same_cell(actual[field], expected[field]),
                f"occurrence rebound mismatch {identity}.{field}",
            )
        for radius in (0, 1, 2):
            for scope in ("D1", "R3", "LINE"):
                view = expected["family_views"][radius]["scope"][scope]
                stem = f"ed{radius}_{scope.lower()}"
                expected_cells = {
                    f"{stem}_features": pipe_cell(view["features"]),
                    f"{stem}_donors": donor_cell(view["donors"]),
                    f"{stem}_family_blocked": blocked_cell(view["blocked_family_donors"]),
                    f"{stem}_source_composed_blocked": blocked_cell(
                        view["blocked_source_composed_donors"]
                    ),
                    f"{stem}_eligible_positions": view["eligible_donor_positions"],
                    f"{stem}_family_blocked_positions": view["family_blocked_positions"],
                    f"{stem}_source_composed_blocked_positions": view[
                        "source_composed_blocked_positions"
                    ],
                }
                for field, value in expected_cells.items():
                    check(same_cell(actual[field], value), f"occurrence view mismatch {identity}.{field}")
        check(actual["reader_exact"] == "1", f"occurrence is not reader exact: {identity}")
        check(
            actual["gdt754_source_composed_gate"] == "ACTIVE_172_SURFACES",
            f"occurrence lacks active GDT754 gate: {identity}",
        )
        check(is_zero(actual["edit_distance_semantic_credit"]), f"ED identity credit at {identity}")
        check(is_zero(actual["component_export_credit"]), f"component export at {identity}")

    multi_fields, multi_rows = tables[CORE_OUTPUTS["multi"]]
    expected_multi_fields = [
        "multi_anchor_line_id", "page", "physical_folio", "locus", "line_number",
        "section", "language", "hand", "paragraph_start_line", "paragraph_end_line",
        "line_token_count", "distinct_exact_anchor_count", "exact_anchor_occurrence_count",
        "exact_anchor_surfaces", "exact_anchor_ordinals", "exact_anchor_counts",
        "written_line_eva", "reader_exact_anchor_positions", "confirmed_plaintext",
        "component_export_credit",
    ]
    check(multi_fields == expected_multi_fields, "multi-anchor atlas schema/order changed")
    check(len(multi_rows) == 33, "multi-anchor artifact row gate != 33")
    multi_by_id = {row["multi_anchor_line_id"]: row for row in multi_rows}
    check(len(multi_by_id) == 33, "multi-anchor artifact IDs are not unique")
    multi_scalar_fields = [
        "multi_anchor_line_id", "page", "physical_folio", "locus", "line_number",
        "section", "language", "hand", "paragraph_start_line", "paragraph_end_line",
        "line_token_count", "distinct_exact_anchor_count", "exact_anchor_occurrence_count",
        "written_line_eva",
    ]
    for expected in core["multi_anchor_lines"]:
        identity = expected["multi_anchor_line_id"]
        check(identity in multi_by_id, f"missing multi-anchor artifact row {identity}")
        actual = multi_by_id[identity]
        for field in multi_scalar_fields:
            check(same_cell(actual[field], expected[field]), f"multi rebound mismatch {identity}.{field}")
        check(
            actual["exact_anchor_surfaces"] == pipe_cell(expected["exact_anchor_surfaces"]),
            f"multi surface order mismatch {identity}",
        )
        check(
            actual["exact_anchor_ordinals"] == pipe_cell(expected["exact_anchor_ordinals"]),
            f"multi ordinal order mismatch {identity}",
        )
        check(
            actual["exact_anchor_counts"] == json_cell(expected["exact_anchor_counts"]),
            f"multi anchor counts mismatch {identity}",
        )
        check(
            tuple(expected["exact_anchor_flags"])
            == (1,) * int(expected["exact_anchor_occurrence_count"]),
            f"core multi exact flags are not all one: {identity}",
        )
        check(actual["reader_exact_anchor_positions"] == "1", f"multi exact seal absent: {identity}")
        check(is_zero(actual["confirmed_plaintext"]), f"multi plaintext claim at {identity}")
        check(is_zero(actual["component_export_credit"]), f"multi component claim at {identity}")

    pair_fields, pair_rows = tables[CORE_OUTPUTS["pairs"]]
    expected_pair_fields = [
        "pair_id", "first_surface", "second_surface", "line_count", "page_count",
        "occurrence_pair_count", "direct_pair_count", "first_before_second",
        "second_before_first", "loci", "pages", "identity_direction_credit",
        "component_export_credit",
    ]
    check(pair_fields == expected_pair_fields, "pair summary schema/order changed")
    check(len(pair_rows) == 15, "pair artifact row gate != 15")
    pair_by_id = {row["pair_id"]: row for row in pair_rows}
    check(len(pair_by_id) == 15, "pair artifact IDs are not unique")
    for expected in core["pair_summary"]:
        identity = expected["pair_id"]
        check(identity in pair_by_id, f"missing pair artifact row {identity}")
        actual = pair_by_id[identity]
        for field in (
            "pair_id", "first_surface", "second_surface", "line_count", "page_count",
            "occurrence_pair_count", "direct_pair_count", "first_before_second",
            "second_before_first",
        ):
            check(same_cell(actual[field], expected[field]), f"pair rebound mismatch {identity}.{field}")
        check(actual["loci"] == pipe_cell(expected["loci"]), f"pair loci mismatch {identity}")
        check(actual["pages"] == pipe_cell(expected["pages"]), f"pair pages mismatch {identity}")
        check(is_zero(actual["identity_direction_credit"]), f"pair identity credit at {identity}")
        check(is_zero(actual["component_export_credit"]), f"pair component credit at {identity}")

    ablation_fields, ablation_rows = tables[CORE_OUTPUTS["ablation"]]
    expected_ablation_fields = [
        "target_surface", "family_radius", "scope", "target_occurrences",
        "global_family_blocked_surface_count", "global_source_composed_blocked_surface_count",
        "eligible_donor_positions", "family_blocked_donor_positions",
        "source_composed_blocked_donor_positions", "eligible_unique_donor_surfaces",
        "global_family_blocked_surfaces",
    ]
    for feature in core_module.FEATURES:
        stem = feature.lower()
        expected_ablation_fields.extend([f"{stem}_target_occurrences", f"{stem}_donor_positions"])
    expected_ablation_fields.extend(
        [
            "eligible_donor_surface_counts", "family_blocked_surface_counts",
            "source_composed_blocked_surface_counts", "edit_distance_semantic_credit",
            "component_export_credit",
        ]
    )
    check(ablation_fields == expected_ablation_fields, "family ablation schema/order changed")
    check(len(ablation_rows) == 54, "family ablation artifact row gate != 54")
    ablation_by_key = {
        (row["target_surface"], int(row["family_radius"]), row["scope"]): row
        for row in ablation_rows
    }
    check(len(ablation_by_key) == 54, "family ablation artifact keys are not unique")
    for expected in core["family_ablation"]:
        key = (expected["target_surface"], expected["family_radius"], expected["scope"])
        check(key in ablation_by_key, f"missing family ablation artifact row {key}")
        actual = ablation_by_key[key]
        for field in (
            "target_surface", "family_radius", "scope", "target_occurrences",
            "global_family_blocked_surface_count", "global_source_composed_blocked_surface_count",
            "eligible_donor_positions", "family_blocked_donor_positions",
            "source_composed_blocked_donor_positions", "eligible_unique_donor_surfaces",
        ):
            check(same_cell(actual[field], expected[field]), f"ablation rebound mismatch {key}.{field}")
        check(
            actual["global_family_blocked_surfaces"]
            == pipe_cell(expected["global_family_blocked_surfaces"]),
            f"family surface list mismatch {key}",
        )
        for feature in core_module.FEATURES:
            stem = feature.lower()
            check(
                int(actual[f"{stem}_target_occurrences"])
                == int(expected["feature_occurrence_counts"][feature]),
                f"ablation target feature mismatch {key}/{feature}",
            )
            check(
                int(actual[f"{stem}_donor_positions"])
                == int(expected["feature_donor_counts"][feature]),
                f"ablation donor feature mismatch {key}/{feature}",
            )
        for field, source_field in (
            ("eligible_donor_surface_counts", "donor_surface_counts"),
            ("family_blocked_surface_counts", "blocked_surface_counts"),
            ("source_composed_blocked_surface_counts", "source_composed_blocked_surface_counts"),
        ):
            check(actual[field] == json_cell(expected[source_field]), f"ablation JSON mismatch {key}.{field}")
        check(is_zero(actual["edit_distance_semantic_credit"]), f"ED credit at {key}")
        check(is_zero(actual["component_export_credit"]), f"component credit at {key}")

    role_fields, role_rows = tables[CORE_OUTPUTS["roles"]]
    expected_role_fields = [
        "surface", "reader_exact_occurrences", "pages", "physical_folios", "loci",
        "line_first", "line_last", "line_position_counts", "paragraph_start_line",
        "paragraph_end_line", "true_paragraph_opener", "true_paragraph_closer",
        "multi_anchor_line_occurrences", "multi_anchor_loci", "mean_ordinal",
        "mean_normalized_line_position", "section_counts", "language_counts",
        "hand_counts", "current_target_role_occurrence_counts",
        "current_target_axis_occurrence_counts", "role_is_translation",
        "component_export_credit",
    ]
    check(role_fields == expected_role_fields, "role geometry schema/order changed")
    check(len(role_rows) == 6, "role geometry artifact row gate != 6")
    role_by_surface = {row["surface"]: row for row in role_rows}
    check(set(role_by_surface) == set(TARGET_COUNTS), "role geometry target set changed")
    for expected in core["role_geometry"]:
        surface = expected["surface"]
        actual = role_by_surface[surface]
        for field in (
            "surface", "reader_exact_occurrences", "pages", "physical_folios", "loci",
            "line_first", "line_last", "paragraph_start_line", "paragraph_end_line",
            "true_paragraph_opener", "true_paragraph_closer",
            "multi_anchor_line_occurrences", "multi_anchor_loci", "mean_ordinal",
            "mean_normalized_line_position",
        ):
            check(same_cell(actual[field], expected[field]), f"role rebound mismatch {surface}.{field}")
        for field in (
            "line_position_counts", "section_counts", "language_counts", "hand_counts",
            "current_target_role_occurrence_counts", "current_target_axis_occurrence_counts",
        ):
            check(actual[field] == json_cell(expected[field]), f"role JSON mismatch {surface}.{field}")
        check(is_zero(actual["role_is_translation"]), f"role translated at {surface}")
        check(is_zero(actual["component_export_credit"]), f"role component credit at {surface}")

    # Model tables must expose every declared comparison, preserve zero lexical
    # credit, and reproduce the published weighted arithmetic row for row.
    metric_fields, metric_rows = tables[MODEL_METRICS_NAME]
    expected_metric_fields = [
        "metric_id", "feature_id", "metric_group", "target_or_pair", "scope",
        "family_radius", "numerator", "denominator", "value", "display",
        "interpretation", "source", "flower_vs_seed_identity_credit", "component_credit",
    ]
    check(metric_fields == expected_metric_fields, "observed metric schema/order changed")
    check(len(metric_rows) == 63, "observed metric row gate != 63")
    check(len({row["metric_id"] for row in metric_rows}) == 63, "metric IDs are not unique")
    check(
        {row["feature_id"] for row in metric_rows} == feature_ids,
        "observed metrics do not cover exactly CF01..CF13",
    )
    for row in metric_rows:
        check(row["metric_id"] and row["display"] and row["interpretation"], "blank observed metric content")
        check(math.isfinite(float(row["value"])), f"nonfinite metric {row['metric_id']}")
        check(is_zero(row["flower_vs_seed_identity_credit"]), f"metric identity credit {row['metric_id']}")
        check(is_zero(row["component_credit"]), f"metric component credit {row['metric_id']}")

    evidence_fields, evidence_rows = tables[MODEL_EVIDENCE_NAME]
    expected_evidence_fields = [
        "model_id", "model_label", "feature_id", "feature_label", "applicable",
        "weight", "match_score_0_1", "weighted_evidence", "evidence",
        "counterevidence", "historical_or_visual_prior_only",
        "flower_vs_seed_identity_credit", "confirmed_lexeme", "component_export_credit",
    ]
    check(evidence_fields == expected_evidence_fields, "model evidence schema/order changed")
    check(len(evidence_rows) == 65, "model evidence must be the complete 5x13 matrix")
    evidence_by_key = {(row["model_id"], row["feature_id"]): row for row in evidence_rows}
    check(len(evidence_by_key) == 65, "model-feature evidence keys are not unique")
    check(
        set(evidence_by_key)
        == {(f"M{m:02d}", f"CF{f:02d}") for m in range(1, 6) for f in range(1, 14)},
        "model-feature evidence matrix is incomplete",
    )
    for (model_id, feature_id), row in evidence_by_key.items():
        expected_weight = model_weight_maps[model_id].get(feature_id, 0.0)
        expected_applicable = int(expected_weight > 0.0)
        weight = float(row["weight"])
        match = float(row["match_score_0_1"])
        weighted = float(row["weighted_evidence"])
        check(int(row["applicable"]) == expected_applicable, f"applicability mismatch {model_id}/{feature_id}")
        check(math.isclose(weight, expected_weight, abs_tol=1e-9), f"weight mismatch {model_id}/{feature_id}")
        check(0.0 <= match <= 1.0, f"match outside [0,1] {model_id}/{feature_id}")
        check(
            math.isclose(weighted, weight * match, rel_tol=0.0, abs_tol=1.1e-6),
            f"weighted evidence arithmetic mismatch {model_id}/{feature_id}",
        )
        if not expected_applicable:
            check(match == 0.0 and weighted == 0.0, f"inapplicable evidence scored {model_id}/{feature_id}")
        check(row["evidence"] and row["counterevidence"], f"blank evidence prose {model_id}/{feature_id}")
        check(row["historical_or_visual_prior_only"] in {"0", "1"}, f"bad prior flag {model_id}/{feature_id}")
        check(is_zero(row["flower_vs_seed_identity_credit"]), f"identity credit {model_id}/{feature_id}")
        check(is_zero(row["confirmed_lexeme"]), f"confirmed lexeme {model_id}/{feature_id}")
        check(is_zero(row["component_export_credit"]), f"component export {model_id}/{feature_id}")

    scoreboard_fields, scoreboard_rows = tables[MODEL_SCOREBOARD_NAME]
    expected_scoreboard_fields = [
        "rank", "model_id", "model_label", "score_0_1", "weighted_sum",
        "applicable_weight", "minimum_interpretive_support_met",
        "minimum_interpretive_support_rule", "chor_portable_de", "shor_portable_de",
        "chor_bold_de", "shor_bold_de", "evidence", "counterevidence",
        "replacement_rule_de", "flower_vs_seed_identity_credit", "confirmed_lexeme",
        "component_export_credit", "decision", "dictionary_replacement_allowed",
    ]
    check(scoreboard_fields == expected_scoreboard_fields, "scoreboard schema/order changed")
    check(len(scoreboard_rows) == 5, "scoreboard row gate != 5")
    scoreboard_by_model = {row["model_id"]: row for row in scoreboard_rows}
    check(set(scoreboard_by_model) == set(model_weight_maps), "scoreboard model set changed")
    for model_id, row in scoreboard_by_model.items():
        applicable_rows = [
            evidence_by_key[model_id, feature_id]
            for feature_id in feature_ids
            if int(evidence_by_key[model_id, feature_id]["applicable"])
        ]
        expected_weighted_sum = sum(float(item["weighted_evidence"]) for item in applicable_rows)
        expected_applicable_weight = sum(float(item["weight"]) for item in applicable_rows)
        expected_score = expected_weighted_sum / expected_applicable_weight
        check(
            math.isclose(float(row["weighted_sum"]), expected_weighted_sum, abs_tol=3e-6),
            f"scoreboard weighted sum mismatch {model_id}",
        )
        check(
            math.isclose(float(row["applicable_weight"]), expected_applicable_weight, abs_tol=1e-9),
            f"scoreboard applicable weight mismatch {model_id}",
        )
        check(
            math.isclose(float(row["score_0_1"]), expected_score, abs_tol=1.1e-6),
            f"scoreboard score mismatch {model_id}",
        )
        check(0.0 <= float(row["score_0_1"]) <= 1.0, f"score out of range {model_id}")
        check(
            math.isclose(
                float(row["score_0_1"]), EXPECTED_MODEL_SCORES[model_id], abs_tol=1e-6
            ),
            f"fixed model score changed {model_id}",
        )
        check(row["minimum_interpretive_support_met"] in {"0", "1"}, f"bad support flag {model_id}")
        check(row["decision"] and row["replacement_rule_de"], f"blank model decision {model_id}")
        check(is_zero(row["flower_vs_seed_identity_credit"]), f"scoreboard identity credit {model_id}")
        check(is_zero(row["confirmed_lexeme"]), f"scoreboard confirmed lexeme {model_id}")
        check(is_zero(row["component_export_credit"]), f"scoreboard component export {model_id}")
        check(is_zero(row["dictionary_replacement_allowed"]), f"unauthorized replacement {model_id}")
    ordered_scores = sorted(
        ((-float(row["score_0_1"]), row["model_id"], int(row["rank"])) for row in scoreboard_rows)
    )
    prior_score: float | None = None
    prior_rank = 0
    for ordinal, (negative_score, model_id, rank) in enumerate(ordered_scores, 1):
        score = -negative_score
        expected_rank = prior_rank if prior_score is not None and math.isclose(score, prior_score, abs_tol=1e-9) else ordinal
        check(rank == expected_rank, f"scoreboard rank mismatch {model_id}")
        prior_score, prior_rank = score, expected_rank
    check(
        math.isclose(
            float(scoreboard_by_model["M02"]["score_0_1"]),
            float(scoreboard_by_model["M03"]["score_0_1"]),
            abs_tol=1e-9,
        ),
        "directional flower/seed models are no longer evidence-symmetric",
    )

    dictionary_fields, dictionary_rows = tables[DICTIONARY_NAME]
    expected_dictionary_fields = [
        "anchor_id", "surface", "anchor_class", "portable_default_de",
        "concrete_default_de", "working_confidence", "primary_rival_de",
        "secondary_rival_de", "positive_evidence_de", "counterevidence_de",
        "register_scope", "tournament_result", "model_rank_context",
        "directional_model_gap", "replacement_guard", "default_is_translation",
        "confirmed_lexeme", "component_export_credit",
    ]
    check(dictionary_fields == expected_dictionary_fields, "working dictionary schema/order changed")
    check(len(dictionary_rows) == 6, "working dictionary row gate != 6")
    dictionary_by_surface = {row["surface"]: row for row in dictionary_rows}
    check(set(dictionary_by_surface) == set(TARGET_COUNTS), "dictionary target set changed")
    check(len(dictionary_by_surface) == 6, "dictionary surfaces are not unique")
    for surface, row in dictionary_by_surface.items():
        for field in (
            "portable_default_de", "concrete_default_de", "working_confidence",
            "primary_rival_de", "secondary_rival_de", "positive_evidence_de",
            "counterevidence_de", "replacement_guard",
        ):
            check(bool(row[field].strip()), f"blank dictionary field {surface}.{field}")
        model_context = json.loads(row["model_rank_context"])
        check(set(model_context) == set(model_weight_maps), f"dictionary model context incomplete {surface}")
        check(is_zero(row["default_is_translation"]), f"dictionary default asserted translated {surface}")
        check(is_zero(row["confirmed_lexeme"]), f"dictionary lexeme confirmed {surface}")
        check(is_zero(row["component_export_credit"]), f"dictionary component export {surface}")

    # The reader is a complete-token renderer, not selected anchor snippets.
    # Bind every ordinal back both to its source spec and the guarded line cache.
    line_spec_path = SRC / "LINE_12_TOKEN_DEFAULT_SPECS.tsv"
    line_spec_fields, line_specs = read_tsv(line_spec_path)
    required_columns(
        line_spec_fields,
        READER_COLUMNS - {"reader_exact", "confirmed_plaintext"},
        "reader source deck",
    )
    check(len(line_specs) == 94, "reader source deck token gate != 94")
    source_reader_by_key = {
        (int(row["line_rank"]), row["locus"], int(row["ordinal"])): row
        for row in line_specs
    }
    check(len(source_reader_by_key) == 94, "reader source keys are not unique")
    for key, row in source_reader_by_key.items():
        check(not row["locus"].lower().startswith("f84"), f"sealed reader source locus {key}")
        check(is_zero(row["confirmed_lexeme"]), f"reader source lexeme claim {key}")
        check(is_zero(row["component_export_credit"]), f"reader source component claim {key}")

    reader_fields, reader_rows = tables[READER_NAME]
    expected_reader_fields = [
        "line_rank", "locus", "line_class", "ordinal", "surface", "reader_exact",
        "portable_role_de", "concrete_default_de", "working_confidence",
        "positive_evidence_de", "counterevidence_de", "primary_rival_de",
        "structural_only", "written_line_eva", "token_default_sequence",
        "line_working_reader_de", "line_finding_de", "confirmed_plaintext",
        "confirmed_lexeme", "component_export_credit",
    ]
    check(reader_fields == expected_reader_fields, "reader schema/order changed")
    required_columns(reader_fields, READER_COLUMNS, "reader artifact")
    check(len(reader_rows) == 94, "reader artifact token gate != 94")
    reader_by_key = {
        (int(row["line_rank"]), row["locus"], int(row["ordinal"])): row
        for row in reader_rows
    }
    check(len(reader_by_key) == 94, "reader artifact keys are not unique")
    check(set(reader_by_key) == set(source_reader_by_key), "reader artifact/source token keys differ")
    by_rank: defaultdict[int, list[dict[str, str]]] = defaultdict(list)
    for row in reader_rows:
        by_rank[int(row["line_rank"])].append(row)
    check(set(by_rank) == set(range(1, 13)), "reader line ranks are not exactly 1..12")
    check(len({row["locus"] for row in reader_rows}) == 12, "reader does not contain 12 loci")
    _g764, environment = core_module.load_guarded_environment(ROOT)
    context = environment["context"]
    for rank in range(1, 13):
        rows = sorted(by_rank[rank], key=lambda row: int(row["ordinal"]))
        loci = {row["locus"] for row in rows}
        check(len(loci) == 1, f"reader rank {rank} spans multiple loci")
        locus = next(iter(loci))
        check(not locus.lower().startswith("f84"), f"sealed reader locus {locus}")
        check(locus in context.by_line, f"reader locus absent from guarded cache: {locus}")
        line = context.by_line[locus]
        check(len(rows) == len(line), f"reader line is incomplete: {locus}")
        check(
            [int(row["ordinal"]) for row in rows] == list(range(1, len(line) + 1)),
            f"reader ordinals are incomplete: {locus}",
        )
        expected_surfaces = [str(token["eva"]) for token in line]
        check([row["surface"] for row in rows] == expected_surfaces, f"reader surfaces mismatch {locus}")
        expected_written = " ".join(expected_surfaces)
        check({row["written_line_eva"] for row in rows} == {expected_written}, f"reader EVA line mismatch {locus}")
        check(len({row["line_class"] for row in rows}) == 1, f"reader line class varies {locus}")
        check(
            len({row["line_working_reader_de"] for row in rows}) == 1
            and bool(rows[0]["line_working_reader_de"].strip()),
            f"reader assembled reading missing or varies {locus}",
        )
        check(
            len({row["line_finding_de"] for row in rows}) == 1
            and bool(rows[0]["line_finding_de"].strip()),
            f"reader finding missing or varies {locus}",
        )
        expected_sequence = " | ".join(
            f"{row['surface']}={row['concrete_default_de']}" for row in rows
        )
        check(
            {row["token_default_sequence"] for row in rows} == {expected_sequence},
            f"reader complete default sequence mismatch {locus}",
        )
        for row, token in zip(rows, line):
            key = (rank, locus, int(row["ordinal"]))
            source = source_reader_by_key[key]
            check(row["reader_exact"] == "1", f"reader token is not exact: {key}")
            check(
                bool(context.exact[(locus, int(token["token_index"]))]),
                f"guarded cache says reader token is nonexact: {key}",
            )
            for field in (
                "line_rank", "locus", "line_class", "ordinal", "surface",
                "portable_role_de", "working_confidence", "positive_evidence_de",
                "counterevidence_de", "primary_rival_de", "structural_only",
                "line_working_reader_de", "line_finding_de",
            ):
                check(row[field] == source[field], f"reader/source mismatch {key}.{field}")
            expected_concrete = dictionary_by_surface.get(row["surface"], source).get(
                "concrete_default_de", source["concrete_default_de"]
            )
            check(row["concrete_default_de"] == expected_concrete, f"reader default mismatch {key}")
            for field in (
                "portable_role_de", "concrete_default_de", "working_confidence",
                "positive_evidence_de", "counterevidence_de", "primary_rival_de",
            ):
                check(bool(row[field].strip()), f"reader field blank {key}.{field}")
            check(row["structural_only"] in {"0", "1"}, f"bad structural flag {key}")
            check(is_zero(row["confirmed_plaintext"]), f"reader plaintext claim {key}")
            check(is_zero(row["confirmed_lexeme"]), f"reader lexeme claim {key}")
            check(is_zero(row["component_export_credit"]), f"reader component claim {key}")

    # Apply the zero-credit contract to every emitted TSV column whose name
    # denotes a confirmed lexical/plaintext/component/identity claim.
    zero_column_hits = 0
    for name, (fields, rows) in tables.items():
        claim_fields = {
            field
            for field in fields
            if field.lower() in ZERO_FIELDS
            or field.lower().startswith("confirmed_")
            or field.lower().endswith("_identity_credit")
            or field.lower().endswith("_component_credit")
            or field.lower().endswith("_component_export_credit")
        }
        for row_number, row in enumerate(rows, 2):
            for field in claim_fields:
                zero_column_hits += 1
                check(is_zero(row[field]), f"nonzero claim {name}:{row_number}.{field}")
        for row_number, row in enumerate(rows, 2):
            for field in fields:
                if field in {"page", "physical_folio", "locus"}:
                    check(
                        not row[field].strip().lower().startswith("f84"),
                        f"sealed f84/f84r reference {name}:{row_number}.{field}",
                    )
    check(zero_column_hits > 1000, "too few explicit zero-credit cells were audited")

    # Retired one-character and ol glosses may be discussed as rivals, but may
    # not silently return as active portable/default translations.
    for name in declared:
        text_value = (art / name).read_text(encoding="utf-8")
        check(NAKED_OLD_GLOSS.search(text_value) is None, f"naked retired gloss mapping in {name}")
    for _name, (fields, rows) in tables.items():
        active_fields = [
            field
            for field in fields
            if any(marker in field.lower() for marker in ACTIVE_SEMANTIC_MARKERS)
            and not any(marker in field.lower() for marker in INACTIVE_SEMANTIC_MARKERS)
        ]
        if "surface" not in fields:
            continue
        for row_number, row in enumerate(rows, 2):
            surface = row["surface"].strip().lower()
            if surface not in OLD_SINGLE_SURFACE_GLOSSES:
                continue
            for field in active_fields:
                normalized = row[field].lower().replace("ö", "oe")
                for retired in OLD_SINGLE_SURFACE_GLOSSES[surface]:
                    check(
                        retired.replace("ö", "oe") not in normalized,
                        f"retired active gloss {_name}:{row_number} {surface}/{field}",
                    )

    # RESULT is a compact machine-readable mirror of the same gates.
    expected_result_keys = {
        "experiment_id", "status", "scope", "counts", "guards", "model_result",
        "dictionary_result", "reader_result", "claim_boundary",
    }
    check(set(result) == expected_result_keys, "RESULT top-level contract changed")
    check(result["experiment_id"] == "GDT768", "wrong RESULT experiment_id")
    check(result["status"] == run.STATUS, "RESULT status does not match run.STATUS")
    check(result["scope"]["source"] == "ALREADY_ADMITTED_GUARDED_CACHE_ONLY", "scope source changed")
    for field in (
        "new_page_opened", "new_image_opened", "new_transcription_opened",
        "f84_accessed", "f84r_accessed",
    ):
        check(result["scope"][field] is False, f"RESULT scope violation: {field}")
    expected_result_counts = {
        "anchor_forms": 6,
        "anchor_occurrences": 404,
        "anchor_pages": metadata["target_pages"],
        "anchor_loci": metadata["target_loci"],
        "multi_anchor_lines": 33,
        "multi_anchor_pages": 26,
        "unordered_anchor_pairs": 15,
        "family_ablation_rows": 54,
        "model_candidates": 5,
        "complete_reader_lines": 12,
        "reader_tokens": 94,
    }
    check(result["counts"] == expected_result_counts, "RESULT counts do not match fixed gates")
    expected_guard_values = {
        "guard_selected": 4137,
        "guard_skipped_forbidden": 98,
        "guard_skipped_not_allowed": 1150,
        "gdt754_source_composed_surfaces": 172,
        "gdt754_target_context_exposures": 54,
    }
    for field, expected in expected_guard_values.items():
        check(result["guards"].get(field) == expected, f"RESULT guard mismatch {field}")
    for field in (
        "edit_distance_semantic_credit", "component_export_credit",
        "f84_accessed", "f84r_accessed",
    ):
        check(is_zero(result["guards"].get(field)), f"RESULT nonzero/true guard claim {field}")
    ranked = sorted(scoreboard_rows, key=lambda row: int(row["rank"]))
    check(result["model_result"]["top_model_id"] == ranked[0]["model_id"], "RESULT top model mismatch")
    check(
        math.isclose(
            float(result["model_result"]["top_model_score"]),
            float(ranked[0]["score_0_1"]),
            abs_tol=1e-9,
        ),
        "RESULT top score mismatch",
    )
    check(result["dictionary_result"]["entries"] == 6, "RESULT dictionary count mismatch")
    check(result["dictionary_result"]["concrete_defaults_present"] is True, "RESULT lacks defaults")
    check(result["reader_result"]["complete_lines"] == 12, "RESULT reader line count mismatch")
    check(result["reader_result"]["tokens"] == 94, "RESULT reader token count mismatch")
    check(result["reader_result"]["all_tokens_have_default"] is True, "RESULT reader defaults false")
    check(result["reader_result"]["all_tokens_reader_exact"] is True, "RESULT reader exact false")
    recursive_hits = recursive_zero_checks(result, check)
    check(recursive_hits >= 8, "RESULT has too few explicit zero claim fields")
    check(
        result["claim_boundary"]
        == {
            "confirmed_english_lexemes": 0,
            "confirmed_german_lexemes": 0,
            "confirmed_plaintext_clauses": 0,
            "identified_language": None,
            "identified_cipher": None,
            "identified_plant_or_substance": None,
            "identified_component_values": 0,
        },
        "RESULT claim boundary changed",
    )

    # The prose reader must visibly retain every anchor/model and its zero-claim
    # ceiling; otherwise the human-facing artifact can drift from RESULT.
    for surface in TARGET_COUNTS:
        check(f"`{surface}`" in historical_reader, f"historical reader omits {surface}")
    for model_id in model_weight_maps:
        check(f"`{model_id}`" in historical_reader, f"historical reader omits {model_id}")
    check(
        re.search(r"Bestätigte Lexeme, Komponenten und Klartextsätze:\s*jeweils \*\*0\*\*", historical_reader)
        is not None,
        "historical reader omits explicit zero claim ceiling",
    )

    # A fresh process in a temporary directory must reproduce every declared
    # artifact byte-for-byte, including RESULT and the human reader.
    with tempfile.TemporaryDirectory(prefix="gdt768-validation-") as replay_dir_text:
        replay_dir = Path(replay_dir_text)
        completed = subprocess.run(
            [sys.executable, str(RUN_PATH), "--artifacts-dir", str(replay_dir)],
            cwd=ROOT,
            check=False,
            capture_output=True,
            text=True,
        )
        check(completed.returncode == 0, f"builder replay failed: {completed.stderr.strip()}")
        emitted = {path.name for path in replay_dir.iterdir() if path.is_file()}
        check(emitted == set(declared), f"builder replay emitted wrong files: {sorted(emitted)}")
        for name in declared:
            check(
                (replay_dir / name).read_bytes() == (art / name).read_bytes(),
                f"builder replay is not byte-identical: {name}",
            )

    validation = {
        "experiment_id": "GDT768",
        "status": "PASS",
        "checks": checks,
        "declared_output_count": len(declared),
        "core_gates": {
            "anchor_occurrences": 404,
            "multi_anchor_lines": 33,
            "unordered_anchor_pairs": 15,
            "anchor_forms": 6,
            "family_ablation_rows": 54,
            "gdt754_target_context_exposures": 54,
        },
        "reader_lines": 12,
        "reader_tokens": 94,
        "byte_replay": True,
        "f84_accessed": False,
        "f84r_accessed": False,
        "confirmed_lexemes": 0,
        "confirmed_plaintext_clauses": 0,
        "component_exports": 0,
    }
    if not args.check_only:
        (art / "VALIDATION.json").write_text(
            json.dumps(validation, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
    print(json.dumps(validation, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
