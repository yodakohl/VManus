#!/usr/bin/env python3
"""Independent GDT796 validator with two byte-identical builder replays."""

from __future__ import annotations

import csv
import hashlib
import io
import json
import random
import re
import subprocess
import sys
import tempfile
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Iterable, Sequence

import numpy as np

sys.dont_write_bytecode = True


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
BASE = ROOT / "experiments/yolo/gdt796_outer_ring_mirror_status_facies_bridge"
SRC = BASE / "src"
ART = BASE / "artifacts"
RUN = SRC / "run.py"
LOCK = SRC / "SOURCE_LOCK.tsv"
QUERY_SPECS = SRC / "GUARDED_QUERY_SPECS.tsv"
PHASE_SPECS = SRC / "PAGE_SIGN_PHASE_SPECS.tsv"
FACIES_MATRICES = SRC / "HISTORICAL_FACIES_MATRICES.tsv"
HISTORICAL_SOURCES = SRC / "HISTORICAL_SOURCE_REGISTRY.tsv"
ATLAS = ROOT / "experiments/yolo/gdt795_source_native_family_kluge_transfer/artifacts/GDT795_101_KLUGE_SOURCE_FAMILY_ATLAS.tsv"
VISUAL_SOURCE = ROOT / "experiments/yolo/gdt360_existing_annotation_joint_grounding/artifacts/gdt360_annotation_inventory.tsv"
SIGN_SOURCE = ROOT / "experiments/semantic_assumptions/results/public_zodiac_nymph_overview.tsv"

OUTPUT_NAMES = (
    "GDT796_OUTER10_400_TRANSFORM_RANKINGS.tsv",
    "GDT796_OUTER10_NULL_SUMMARIES.tsv",
    "GDT796_OUTER10_SPLIT_HALF_RANKS.tsv",
    "GDT796_OUTER10_BOUNDARY_POSITION_CONTRIBUTIONS.tsv",
    "GDT796_174_VISUAL_STATE_ATLAS.tsv",
    "GDT796_VISUAL_TRANSFER_SUMMARY.tsv",
    "GDT796_VISUAL_RECURRENT_FAMILY_CENSUS.tsv",
    "GDT796_3_VISUAL_STATUS_CARDS.tsv",
    "GDT796_240_FACIES_GLOBAL_TRANSFORMS.tsv",
    "GDT796_4_FACIES_SELECTED_MODEL_SUMMARY.tsv",
    "GDT796_FACIES_LEAVE_ONE_FAMILY_OUT.tsv",
    "GDT796_24_FACIES_LEAVE_ONE_SIGN_OUT.tsv",
    "GDT796_AQABAC_FACIES_RIVAL.tsv",
    "GDT796_HISTORICAL_FAMILY_STATUS_CENSUS.tsv",
    "GDT796_CANDIDATE_ADJUDICATION.tsv",
    "RESULT.json",
)

REQUIRED_LOCK_PATHS = {
    "experiments/yolo/gdt796_outer_ring_mirror_status_facies_bridge/METHOD.md",
    "experiments/yolo/gdt796_outer_ring_mirror_status_facies_bridge/PREREGISTRATION.md",
    "experiments/yolo/gdt796_outer_ring_mirror_status_facies_bridge/src/GUARDED_QUERY_SPECS.tsv",
    "experiments/yolo/gdt796_outer_ring_mirror_status_facies_bridge/src/PAGE_SIGN_PHASE_SPECS.tsv",
    "experiments/yolo/gdt796_outer_ring_mirror_status_facies_bridge/src/HISTORICAL_SOURCE_REGISTRY.tsv",
    "experiments/yolo/gdt796_outer_ring_mirror_status_facies_bridge/src/HISTORICAL_FACIES_MATRICES.tsv",
    "experiments/yolo/gdt796_outer_ring_mirror_status_facies_bridge/src/mirror_analysis.py",
    "experiments/yolo/gdt796_outer_ring_mirror_status_facies_bridge/src/run.py",
    "experiments/yolo/gdt796_outer_ring_mirror_status_facies_bridge/src/validate.py",
    "experiments/yolo/gdt795_source_native_family_kluge_transfer/artifacts/GDT795_101_KLUGE_SOURCE_FAMILY_ATLAS.tsv",
    "experiments/yolo/gdt360_existing_annotation_joint_grounding/artifacts/gdt360_annotation_inventory.tsv",
    "experiments/semantic_assumptions/results/public_zodiac_nymph_overview.tsv",
}

EXPECTED_STATUS = (
    "PARTIAL__101_LOCI__OUTER10_F71_RELATIVE_REFLECTION_C0_NOT_REUSABLE__"
    "554_GUARDED_VISUAL_ROWS__174_VARYING_STATES__3_VISUAL_RIVALS_BELOW_GATE__"
    "ZERO_STATUS_CARDS__GENERAL_VISUAL_CODE_FAIL__240_HISTORICAL_TRANSFORMS__"
    "AQABAC_FORTUNATE_FACIES_TARGET_MASKED_FAIL__"
    "LEARNED_ENTRY_PLUS_LOCAL_GRAPHIC_FIELD_PRIMARY__ZERO_COMPONENT_EXPORT__ZERO_CONFIRMED_LEXEMES"
)


def fields(text: str) -> tuple[str, ...]:
    return tuple(text.split())


EXPECTED_SCHEMAS = {
    OUTPUT_NAMES[0]: fields("""view_id source_field metric_id transform_71 transform_72 transform_71_orientation transform_71_shift transform_72_orientation transform_72_shift raw_score raw_rank raw_tie_count comparable_normalized_score comparable_normalized_rank comparable_normalized_tie_count exact_value_hits total_comparable_pairs f70_f71_raw_score f70_f72_raw_score f71_f72_raw_score f70_f71_comparable f70_f72_comparable f71_f72_comparable is_reported_f9_r0 is_identity"""),
    OUTPUT_NAMES[1]: fields("""view_id source_field metric_id null_id score_id seed iterations observed_best_transform_71 observed_best_transform_72 observed_best_score observed_best_tie_count null_mean_optimized_score null_population_sd null_ge_observed add_one_p missing_slot_treatment"""),
    OUTPUT_NAMES[2]: fields("""view_id source_field metric_id split_id train_a_members test_a_members raw_selected_transform_71 raw_selected_transform_72 raw_train_score raw_train_best_tie_count raw_test_score raw_test_rank raw_test_tie_count comparable_normalized_selected_transform_71 comparable_normalized_selected_transform_72 comparable_normalized_train_score comparable_normalized_train_best_tie_count comparable_normalized_test_score comparable_normalized_test_rank comparable_normalized_test_tie_count"""),
    OUTPUT_NAMES[3]: fields("""semantic_a_member local_coordinate f70_native_a_member f70_locus f70_surface f70_boundary_family f71_f9_native_a_member f71_f9_locus f71_f9_surface f71_f9_boundary_family f72_native_a_member f72_locus f72_surface f72_boundary_family f9_f70_f71_similarity f9_f70_f72_similarity f9_f71_f72_similarity f9_total_contribution identity_f71_native_a_member identity_f71_locus identity_f71_surface identity_f71_boundary_family identity_total_contribution f9_minus_identity f9_exact_pair_hits missing_slot_in_reference_pair"""),
    OUTPUT_NAMES[4]: fields("""visual_event_ordinal channel visual_state locus physical_folio source_selector visual_array_id atlas_array_id kluge_a_member complete_label_surface canonical_boundary_family canonical_compact_family transferred_prefix strict_residual provenance source_id confidence visual_detail block_state_counts block_is_state_pure semantic_ceiling"""),
    OUTPUT_NAMES[5]: fields("""channel representation_id source_field event_count state_count states visual_block_count state_pure_block_count block_state_pair_count local_block_loo_covered local_block_loo_credit local_block_loo_accuracy held_physical_folio_covered held_physical_folio_key_credit held_physical_folio_key_accuracy held_physical_folio_baseline_credit held_physical_folio_baseline_accuracy held_physical_folio_gain held_source_page_covered held_source_page_key_credit held_source_page_key_accuracy visual_null_iterations visual_null_mean_gain visual_null_p_gain_ge_observed decision semantic_export"""),
    OUTPUT_NAMES[6]: fields("""channel canonical_boundary_family event_count state_counts state_purity physical_folio_count physical_folios source_page_count source_pages visual_block_count all_supporting_blocks_state_pure loci surfaces candidate_ceiling component_export_credit"""),
    OUTPUT_NAMES[7]: fields("""card_id channel canonical_boundary_family working_default_de confidence event_count state_counts physical_folio_count source_page_count visual_block_count loci surfaces evidence counterevidence renderer_license prose_export_allowed component_export_credit confirmed_lexeme"""),
    OUTPUT_NAMES[8]: fields("""matrix_id taurus_phase direction offset cross_sign_recurrent_family_count family_balanced_status_purity family_balanced_planet_purity consistent_status_family_count consistent_planet_family_count training_without_aqabac_family_count training_without_aqabac_status_purity training_without_aqabac_planet_purity training_without_aqabac_consistent_status_count aqabac_event_count aqabac_status_purity aqabac_status_modes aqabac_status_counts aqabac_planet_purity aqabac_planet_modes aqabac_planet_counts aqabac_all_benefic semantic_export"""),
    OUTPUT_NAMES[9]: fields("""matrix_id taurus_phase selected_without_family selected_direction selected_offset training_family_count training_family_balanced_status_purity training_family_balanced_planet_purity training_consistent_status_family_count training_consistent_planet_family_count aqabac_event_count aqabac_status_purity aqabac_status_modes aqabac_status_counts aqabac_planet_purity aqabac_planet_modes aqabac_planet_counts aqabac_all_benefic aqabac_uniform_status_transform_count aqabac_all_benefic_transform_count aqabac_uniform_planet_transform_count null_iterations null_mean_optimized_training_status_purity null_p_optimized_status_ge_observed decision semantic_export"""),
    OUTPUT_NAMES[10]: fields("""matrix_id taurus_phase held_family held_event_count held_sign_count held_signs selected_direction selected_offset training_family_count training_status_purity held_status_purity held_status_modes held_status_counts held_planet_purity held_planet_modes held_planet_counts held_all_benefic held_consistent_status held_consistent_planet semantic_export"""),
    OUTPUT_NAMES[11]: fields("""matrix_id taurus_phase held_sign training_signs selected_direction_without_aqabac selected_offset_without_aqabac training_cross_sign_family_capacity_all training_family_count_without_aqabac held_any_training_family_capacity_all held_any_training_family_capacity_without_aqabac eligible_held_family_count_all eligible_held_family_count_without_aqabac held_family aqabac_target_diagnostic training_event_count held_event_count training_status_purity training_status_modes training_status_counts held_status_purity held_status_modes held_status_counts held_status_matches_training_mode training_status_unambiguous held_status_prediction_correct training_planet_purity training_planet_modes training_planet_counts held_planet_purity held_planet_modes held_planet_counts held_planet_matches_training_mode training_planet_unambiguous held_planet_prediction_correct decision semantic_export"""),
    OUTPUT_NAMES[12]: fields("""matrix_id taurus_phase evaluation_id direction offset locus source_selector sign kluge_a_member base_position transformed_degree facies_index planet coarse_status working_rival_de confidence component_export_credit"""),
    OUTPUT_NAMES[13]: fields("""matrix_id taurus_phase selected_direction_without_aqabac selected_offset_without_aqabac canonical_boundary_family event_count sign_count signs status_counts status_purity status_modes planet_counts planet_purity planet_modes fixed_status_candidate fixed_planet_candidate semantic_export"""),
    OUTPUT_NAMES[14]: fields("""candidate_id working_interpretation confidence decision evidence counterevidence component_export_credit confirmed_lexeme"""),
}

VISUAL_QUERY_COLUMNS = fields("""case_id channel visual_state page physical_folio locus array_id provenance source_id confidence evidence_family evidence_lineage evidence_cluster visual_detail formal_coverage gdt327_coverage""")
SIGN_QUERY_COLUMNS = fields("""sign page physical_folio NYMPHS CLOTHED_NYMPHS COLOR_CLOTHES CROWNED_NYMPHS MALE_NYMPHS STARS STAR_W__TETHER HOLDING_STAR HOLDING_TETHER CANS COLOR_CANS""")
VIEW_SPECS = (
    ("ZL_MEMBER_NED", "zl_member_sequence", "CHAR_NORMALIZED_LEVENSHTEIN"),
    ("IT_MEMBER_NED", "it_member_sequence", "CHAR_NORMALIZED_LEVENSHTEIN"),
    ("RF_MEMBER_NED", "rf_member_sequence", "CHAR_NORMALIZED_LEVENSHTEIN"),
    ("BOUNDARY_NED", "canonical_boundary_family", "CHAR_NORMALIZED_LEVENSHTEIN"),
    ("COMPACT_NED", "canonical_compact_family", "CHAR_NORMALIZED_LEVENSHTEIN"),
    ("PREFIX_EXACT", "transferred_prefix", "CATEGORICAL_EXACT"),
    ("PREFIX_NED", "transferred_prefix", "CHAR_NORMALIZED_LEVENSHTEIN"),
    ("RESIDUAL_NED", "strict_residual", "CHAR_NORMALIZED_LEVENSHTEIN"),
)
VISUAL_CHANNELS = ("ZODIAC_BARREL", "ZODIAC_CLOTHING", "ZODIAC_FACING")
VISUAL_REPRESENTATIONS = (
    ("BOUNDARY_FAMILY", "canonical_boundary_family"),
    ("COMPACT_FAMILY", "canonical_compact_family"),
    ("TRANSFERRED_PREFIX", "transferred_prefix"),
    ("FORMAL_RESIDUAL", "strict_residual"),
)
TRANSFORMS = tuple(
    (("R" if orientation == 1 else "F") + str(shift), orientation, shift)
    for orientation in (1, -1) for shift in range(10)
)
TRANSFORM_BY_NAME = {name: (orientation, shift) for name, orientation, shift in TRANSFORMS}
TRANSFORM_ORDINAL = {name: index for index, (name, _, _) in enumerate(TRANSFORMS)}


class Audit:
    def __init__(self) -> None:
        self.checks = 0
        self.failures: list[str] = []

    def check(self, condition: bool, label: str) -> None:
        self.checks += 1
        if not condition:
            self.failures.append(label)


def read_tsv(path: Path) -> tuple[tuple[str, ...], list[dict[str, str]]]:
    with path.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle, delimiter="\t")
        return tuple(reader.fieldnames or ()), list(reader)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def f6(value: float) -> str:
    return f"{value:.6f}"


def f12(value: float) -> str:
    return f"{value:.12f}"


def joined(values: Iterable[Any]) -> str:
    materialized = [str(value) for value in values]
    return "|".join(materialized) if materialized else "NONE"


def count_text(values: Sequence[str]) -> str:
    counts = Counter(values)
    return joined(f"{value}:{count}" for value, count in sorted(counts.items()))


def purity(values: Sequence[str]) -> tuple[float, str, str]:
    counts = Counter(values)
    maximum = max(counts.values())
    return (
        maximum / len(values),
        joined(sorted(value for value, count in counts.items() if count == maximum)),
        count_text(values),
    )


def write_validation(audit: Audit, **extra: Any) -> int:
    payload = {"status": "PASS" if not audit.failures else "FAIL", "checks": audit.checks, "failures": audit.failures, **extra}
    ART.mkdir(parents=True, exist_ok=True)
    (ART / "VALIDATION.json").write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0 if not audit.failures else 1


def guard_query(source: Path, selector: str, allowed: Sequence[str], columns: Sequence[str], expected: dict[str, int]) -> tuple[list[dict[str, str]], dict[str, int]]:
    if any(value.lower().startswith("f84") for value in allowed):
        raise RuntimeError("sealed selector in validator allow-list")
    command = [str(ROOT / "vmanus-exp"), "query-tsv", source.relative_to(ROOT).as_posix(), "--selector", selector]
    for value in allowed:
        command.extend(("--allow", value))
    command.extend(("--columns", ",".join(columns), "--forbid-prefix", "f84"))
    completed = subprocess.run(command, cwd=ROOT, text=True, capture_output=True, check=False)
    if completed.returncode:
        raise RuntimeError(completed.stderr.strip())
    match = re.search(r"GUARD_STATS\s+(\{[^\n]+\})", completed.stderr)
    if not match:
        raise RuntimeError("missing GUARD_STATS")
    stats = json.loads(match.group(1))
    if stats != expected:
        raise RuntimeError(f"guard stats {stats} != {expected}")
    reader = csv.DictReader(io.StringIO(completed.stdout), delimiter="\t")
    rows = list(reader)
    if tuple(reader.fieldnames or ()) != tuple(columns):
        raise RuntimeError("guarded projection schema changed")
    return rows, stats


def levenshtein(left: str, right: str) -> int:
    if len(left) < len(right):
        left, right = right, left
    previous = list(range(len(right) + 1))
    for row_index, left_item in enumerate(left, start=1):
        current = [row_index]
        for column_index, right_item in enumerate(right, start=1):
            current.append(min(current[-1] + 1, previous[column_index] + 1, previous[column_index - 1] + (left_item != right_item)))
        previous = current
    return previous[-1]


def similarity(left: str | None, right: str | None, metric: str) -> float:
    if left is None or right is None:
        return 0.0
    if metric == "CATEGORICAL_EXACT":
        return float(left == right)
    return 1.0 - levenshtein(left, right) / max(len(left), len(right), 1)


def transform_coordinate(name: str, coordinate: int) -> int:
    orientation, shift = TRANSFORM_BY_NAME[name]
    return (orientation * coordinate + shift) % 10


def mirror_score(panel: list[list[dict[str, str] | None]], field: str, metric: str, t71: str, t72: str, coordinates: Sequence[int] = tuple(range(10))) -> dict[str, float | int]:
    raw = [0.0, 0.0, 0.0]
    comparable = [0, 0, 0]
    exact = 0
    for coordinate in coordinates:
        rows = (panel[0][coordinate], panel[1][transform_coordinate(t71, coordinate)], panel[2][transform_coordinate(t72, coordinate)])
        values = tuple(None if row is None else row[field] for row in rows)
        for pair_index, (left_index, right_index) in enumerate(((0, 1), (0, 2), (1, 2))):
            left, right = values[left_index], values[right_index]
            raw[pair_index] += similarity(left, right, metric)
            if left is not None and right is not None:
                comparable[pair_index] += 1
                exact += left == right
    return {
        "raw": sum(raw),
        "normalized": sum(value / count if count else 0.0 for value, count in zip(raw, comparable)),
        "exact": exact,
        "comparable": sum(comparable),
        "raw_01": raw[0], "raw_02": raw[1], "raw_12": raw[2],
        "count_01": comparable[0], "count_02": comparable[1], "count_12": comparable[2],
    }


def mirror_grid(panel: list[list[dict[str, str] | None]], field: str, metric: str, coordinates: Sequence[int] = tuple(range(10))) -> dict[tuple[str, str], dict[str, float | int]]:
    return {(left[0], right[0]): mirror_score(panel, field, metric, left[0], right[0], coordinates) for left in TRANSFORMS for right in TRANSFORMS}


def rank_of(values: dict[tuple[str, str], float], key: tuple[str, str]) -> tuple[int, int]:
    selected = values[key]
    return (1 + sum(value > selected + 1e-12 for value in values.values()), sum(abs(value - selected) <= 1e-12 for value in values.values()))


def grid_best(grid: dict[tuple[str, str], dict[str, float | int]], field: str) -> tuple[str, str]:
    return max(grid, key=lambda key: (float(grid[key][field]), -TRANSFORM_ORDINAL[key[0]], -TRANSFORM_ORDINAL[key[1]]))


def modes(values: Sequence[str]) -> set[str]:
    counts = Counter(values)
    maximum = max(counts.values())
    return {value for value, count in counts.items() if count == maximum}


def prediction(records: list[dict[str, str]], key_field: str, holdout_field: str) -> dict[str, float]:
    covered = 0
    credit = 0.0
    baseline = 0.0
    for index, target in enumerate(records):
        training = [row for other, row in enumerate(records) if other != index and row[holdout_field] != target[holdout_field]]
        keyed = [row for row in training if row[key_field] == target[key_field]]
        if not keyed:
            continue
        covered += 1
        key_modes = modes([row["visual_state"] for row in keyed])
        base_modes = modes([row["visual_state"] for row in training])
        if target["visual_state"] in key_modes:
            credit += 1.0 / len(key_modes)
        if target["visual_state"] in base_modes:
            baseline += 1.0 / len(base_modes)
    return {"covered": covered, "credit": credit, "baseline": baseline, "accuracy": credit / covered if covered else 0.0, "baseline_accuracy": baseline / covered if covered else 0.0, "gain": (credit - baseline) / covered if covered else 0.0}


def local_prediction(records: list[dict[str, str]], key_field: str) -> dict[str, float]:
    covered = 0
    credit = 0.0
    for index, target in enumerate(records):
        training = [row for other, row in enumerate(records) if other != index and row["visual_array_id"] == target["visual_array_id"] and row[key_field] == target[key_field]]
        if not training:
            continue
        covered += 1
        current_modes = modes([row["visual_state"] for row in training])
        if target["visual_state"] in current_modes:
            credit += 1.0 / len(current_modes)
    return {"covered": covered, "credit": credit, "accuracy": credit / covered if covered else 0.0}


def shuffled_visual(records: list[dict[str, str]], rng: random.Random) -> list[dict[str, str]]:
    copied = [dict(row) for row in records]
    blocks: dict[str, list[int]] = defaultdict(list)
    for index, row in enumerate(copied):
        blocks[row["visual_array_id"]].append(index)
    for indices in blocks.values():
        states = [copied[index]["visual_state"] for index in indices]
        rng.shuffle(states)
        for index, state in zip(indices, states):
            copied[index]["visual_state"] = state
    return copied


def family_groups(events: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    counts = Counter(row["canonical_boundary_family"] for row in events)
    groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in events:
        if counts[row["canonical_boundary_family"]] >= 2:
            groups[row["canonical_boundary_family"]].append(row)
    return {family: rows for family, rows in groups.items() if len({row["sign"] for row in rows}) >= 2}


def facies_score(events: list[dict[str, Any]], excluded: set[str] | None = None) -> dict[str, Any]:
    groups = {family: rows for family, rows in family_groups(events).items() if family not in (excluded or set())}
    if not groups:
        return {"family_count": 0, "status_purity": 0.0, "planet_purity": 0.0, "consistent_status": 0, "consistent_planet": 0}
    status = [purity([row["coarse_status"] for row in rows])[0] for rows in groups.values()]
    planet = [purity([row["planet"] for row in rows])[0] for rows in groups.values()]
    return {"family_count": len(groups), "status_purity": sum(status) / len(status), "planet_purity": sum(planet) / len(planet), "consistent_status": sum(value == 1.0 for value in status), "consistent_planet": sum(value == 1.0 for value in planet)}


def mapped_event(row: dict[str, Any], phase: str, matrix_id: str, direction: int, offset: int, phases: dict[str, dict[str, Any]], matrices: dict[tuple[str, str, int], dict[str, str]]) -> dict[str, Any]:
    spec = phases[row["source_selector"]]
    add = int(spec["h0_base_add"] if phase == "H0" else spec["h1_base_add"])
    base = ((int(row["kluge_a_member"]) - 1 + add) % 30) + 1
    degree = ((offset + direction * (base - 1)) % 30) + 1
    facies = ((degree - 1) // 10) + 1
    cell = matrices[matrix_id, spec["sign"], facies]
    return {**row, "sign": spec["sign"], "base_position": base, "transformed_degree": degree, "facies_index": facies, "planet": cell["planet"], "coarse_status": cell["coarse_status"]}


def select_facies(events: list[dict[str, Any]], phase: str, matrix_id: str, phases: dict[str, dict[str, Any]], matrices: dict[tuple[str, str, int], dict[str, str]], excluded: set[str] | None = None) -> tuple[int, int, dict[str, Any], list[dict[str, Any]]]:
    candidates = []
    for direction in (1, -1):
        for offset in range(30):
            mapped = [mapped_event(row, phase, matrix_id, direction, offset, phases, matrices) for row in events]
            candidates.append((direction, offset, facies_score(mapped, excluded), mapped))
    return max(candidates, key=lambda item: (item[2]["status_purity"], item[2]["planet_purity"], item[2]["consistent_status"], item[2]["consistent_planet"], item[0] == 1, -item[1]))


def validate_lock(audit: Audit) -> None:
    audit.check(LOCK.is_file(), "source lock exists")
    if not LOCK.is_file():
        return
    lock_fields, rows = read_tsv(LOCK)
    audit.check(lock_fields == ("path", "sha256", "role"), "source lock exact schema")
    paths = [row.get("path", "") for row in rows]
    audit.check(set(paths) == REQUIRED_LOCK_PATHS and len(paths) == len(set(paths)), "source lock exact unique path set")
    audit.check(all(row.get("role") for row in rows), "source lock roles populated")
    for row in rows:
        relative = Path(row.get("path", ""))
        contained = bool(row.get("path")) and not relative.is_absolute() and ".." not in relative.parts
        audit.check(contained, f"contained lock path {row.get('path', '')}")
        if not contained:
            continue
        path = ROOT / relative
        audit.check(path.is_file(), f"locked source exists {row['path']}")
        audit.check(bool(re.fullmatch(r"[0-9a-f]{64}", row.get("sha256", ""))), f"lock hash format {row['path']}")
        if path.is_file():
            audit.check(sha256(path) == row["sha256"], f"locked source hash {row['path']}")


def main() -> int:
    audit = Audit()
    validate_lock(audit)

    manifest = json.loads((BASE / "experiment.json").read_text(encoding="utf-8"))
    audit.check(manifest.get("sealed_data") == {"f84": "FORBIDDEN", "f84r": "FORBIDDEN"}, "manifest seals f84 and f84r")
    atlas_fields, atlas = read_tsv(ATLAS)
    audit.check(len(atlas) == 101 and len({row["locus"] for row in atlas}) == 101, "101 unique locked atlas loci")
    audit.check(not any(row["locus"].lower().startswith("f84") for row in atlas), "atlas allow-list excludes f84")
    audit.check("canonical_boundary_family" in atlas_fields, "atlas carries source-native family")

    spec_fields, specs = read_tsv(QUERY_SPECS)
    spec_by_id = {row["query_id"]: row for row in specs}
    audit.check(spec_fields == fields("query_id path selector allowed_values_source columns forbidden_prefixes"), "guard spec exact schema")
    audit.check(set(spec_by_id) == {"K101_GDT360_VISUAL", "FIVE_PAGE_SIGN_MAP"}, "two guarded query contracts")
    audit.check(all(row["forbidden_prefixes"] == "f84" for row in specs), "both guards forbid f84")
    audit.check(
        spec_by_id["K101_GDT360_VISUAL"]["path"] == VISUAL_SOURCE.relative_to(ROOT).as_posix()
        and spec_by_id["K101_GDT360_VISUAL"]["selector"] == "locus"
        and tuple(spec_by_id["K101_GDT360_VISUAL"]["columns"].split(",")) == VISUAL_QUERY_COLUMNS,
        "visual query fixes source selector and projection",
    )
    audit.check(
        spec_by_id["FIVE_PAGE_SIGN_MAP"]["path"] == SIGN_SOURCE.relative_to(ROOT).as_posix()
        and spec_by_id["FIVE_PAGE_SIGN_MAP"]["selector"] == "page"
        and tuple(spec_by_id["FIVE_PAGE_SIGN_MAP"]["columns"].split(",")) == SIGN_QUERY_COLUMNS,
        "sign query fixes source selector and projection",
    )
    guard_stats: dict[str, dict[str, int]] = {}
    visual_source_rows: list[dict[str, str]] = []
    sign_source_rows: list[dict[str, str]] = []
    try:
        visual_source_rows, visual_stats = guard_query(
            VISUAL_SOURCE, "locus", sorted(row["locus"] for row in atlas), VISUAL_QUERY_COLUMNS,
            {"selected": 554, "skipped_forbidden": 0, "skipped_not_allowed": 4053},
        )
        sign_source_rows, sign_stats = guard_query(
            SIGN_SOURCE, "page", ("f70v1", "f70v2", "f71v", "f72r1", "f72r2"), SIGN_QUERY_COLUMNS,
            {"selected": 5, "skipped_forbidden": 0, "skipped_not_allowed": 7},
        )
        guard_stats = {"visual": visual_stats, "sign": sign_stats}
    except (RuntimeError, KeyError, json.JSONDecodeError) as exc:
        audit.check(False, f"guarded reacquisition: {exc}")
    audit.check(len(visual_source_rows) == 554, "guard reacquires 554 visual rows")
    audit.check(len(sign_source_rows) == 5, "guard reacquires five sign rows")
    audit.check(not any(row.get("locus", "").lower().startswith("f84") for row in visual_source_rows), "visual guard materializes zero sealed rows")
    audit.check(not any(row.get("page", "").lower().startswith("f84") for row in sign_source_rows), "sign guard materializes zero sealed rows")

    for name in OUTPUT_NAMES:
        audit.check((ART / name).is_file(), f"canonical artifact exists {name}")
    if audit.failures:
        return write_validation(
            audit, builder_replays_completed=0, canonical_outputs_compared=0,
            guarded_query_stats=guard_stats, new_pages_or_images_opened=0, sealed_rows_materialized=0,
        )

    replay_one: dict[str, bytes] = {}
    completed_replays = 0
    for replay_index in (1, 2):
        with tempfile.TemporaryDirectory(prefix=f".gdt796_replay_{replay_index}_", dir=BASE) as tmp:
            completed = subprocess.run(
                [sys.executable, str(RUN), "--output-dir", tmp], cwd=ROOT,
                text=True, capture_output=True, check=False,
            )
            audit.check(completed.returncode == 0, f"builder replay {replay_index} exits zero")
            audit.check(completed.stdout.strip() == EXPECTED_STATUS, f"builder replay {replay_index} exact status")
            audit.check(not completed.stderr.strip(), f"builder replay {replay_index} empty stderr")
            if completed.returncode == 0:
                completed_replays += 1
            replay_files = {path.name for path in Path(tmp).iterdir() if path.is_file()}
            audit.check(replay_files == set(OUTPUT_NAMES), f"builder replay {replay_index} exact output set")
            for name in OUTPUT_NAMES:
                replay = Path(tmp) / name
                audit.check(replay.is_file(), f"replay {replay_index} creates {name}")
                if not replay.is_file():
                    continue
                data = replay.read_bytes()
                audit.check(data == (ART / name).read_bytes(), f"byte replay {replay_index} canonical {name}")
                if replay_index == 1:
                    replay_one[name] = data
                else:
                    audit.check(data == replay_one.get(name), f"byte equality replay 1 versus 2 {name}")

    artifacts: dict[str, list[dict[str, str]]] = {}
    for name, schema in EXPECTED_SCHEMAS.items():
        current_fields, rows = read_tsv(ART / name)
        audit.check(current_fields == schema, f"exact schema {name}")
        artifacts[name] = rows
    result = json.loads((ART / OUTPUT_NAMES[15]).read_text(encoding="utf-8"))
    for name, rows in artifacts.items():
        for row_index, row in enumerate(rows, start=2):
            for field, value in row.items():
                if field in {"locus", "loci", "source_selector", "source_page", "source_pages", "page", "physical_folio", "physical_folios"}:
                    audit.check(not any(part.lower().startswith("f84") for part in value.split("|")), f"no sealed selector {name}:{row_index}:{field}")
    for name in OUTPUT_NAMES:
        data = (ART / name).read_bytes()
        audit.check((b"/" + b"home/") not in data and b"BEGIN PRIVATE KEY" not in data, f"privacy scan {name}")

    rankings = artifacts[OUTPUT_NAMES[0]]
    nulls = artifacts[OUTPUT_NAMES[1]]
    splits = artifacts[OUTPUT_NAMES[2]]
    contributions = artifacts[OUTPUT_NAMES[3]]
    visual_atlas = artifacts[OUTPUT_NAMES[4]]
    visual_transfer = artifacts[OUTPUT_NAMES[5]]
    visual_census = artifacts[OUTPUT_NAMES[6]]
    visual_cards = artifacts[OUTPUT_NAMES[7]]
    transform_rows = artifacts[OUTPUT_NAMES[8]]
    selected_rows = artifacts[OUTPUT_NAMES[9]]
    lofo_rows = artifacts[OUTPUT_NAMES[10]]
    sign_out_rows = artifacts[OUTPUT_NAMES[11]]
    aqabac_rows = artifacts[OUTPUT_NAMES[12]]
    historical_census = artifacts[OUTPUT_NAMES[13]]
    adjudication = artifacts[OUTPUT_NAMES[14]]

    # Independent pure-Python reconstruction of all observed mirror scores.
    outer_members = tuple(range(6, 16))
    atlas_key = {(row["source_selector"], int(row["kluge_a_member"])): row for row in atlas}
    panel = [[atlas_key.get((page, member)) for member in outer_members] for page in ("f70v1", "f71v", "f72r1")]
    audit.check(tuple(tuple(member for member, row in zip(outer_members, page) if row is None) for page in panel) == ((14,), (), (14,)), "mirror missing pattern f70/f72 A14")
    audit.check(tuple(sum(row is not None for row in page) for page in panel) == (9, 10, 9), "mirror observed capacities 9/10/9")
    audit.check(len(rankings) == 3200, "3,200 mirror ranking rows")
    audit.check(Counter(row["view_id"] for row in rankings) == Counter({view: 400 for view, _, _ in VIEW_SPECS}), "eight complete mirror grids")
    ranking_map = {(row["view_id"], row["transform_71"], row["transform_72"]): row for row in rankings}
    mirror_grids: dict[str, dict[tuple[str, str], dict[str, float | int]]] = {}
    for view, source_field, metric in VIEW_SPECS:
        grid = mirror_grid(panel, source_field, metric)
        mirror_grids[view] = grid
        audit.check({(row["transform_71"], row["transform_72"]) for row in rankings if row["view_id"] == view} == set(grid), f"{view} D10xD10 keyspace")
        raw_values = {key: float(score["raw"]) for key, score in grid.items()}
        normalized_values = {key: float(score["normalized"]) for key, score in grid.items()}
        for key, score in grid.items():
            row = ranking_map[view, *key]
            orientation_71, shift_71 = TRANSFORM_BY_NAME[key[0]]
            orientation_72, shift_72 = TRANSFORM_BY_NAME[key[1]]
            audit.check(
                row["source_field"] == source_field and row["metric_id"] == metric
                and (int(row["transform_71_orientation"]), int(row["transform_71_shift"])) == (orientation_71, shift_71)
                and (int(row["transform_72_orientation"]), int(row["transform_72_shift"])) == (orientation_72, shift_72),
                f"mirror metadata {view}/{key[0]}/{key[1]}",
            )
            audit.check(
                abs(float(row["raw_score"]) - float(score["raw"])) <= 1e-12
                and abs(float(row["comparable_normalized_score"]) - float(score["normalized"])) <= 1e-12
                and int(row["exact_value_hits"]) == score["exact"]
                and int(row["total_comparable_pairs"]) == score["comparable"]
                and row["f70_f71_raw_score"] == f12(float(score["raw_01"]))
                and row["f70_f72_raw_score"] == f12(float(score["raw_02"]))
                and row["f71_f72_raw_score"] == f12(float(score["raw_12"])),
                f"independent mirror score {view}/{key[0]}/{key[1]}",
            )
            audit.check(
                (int(row["f70_f71_comparable"]), int(row["f70_f72_comparable"]), int(row["f71_f72_comparable"])) == (score["count_01"], score["count_02"], score["count_12"])
                and (int(row["raw_rank"]), int(row["raw_tie_count"])) == rank_of(raw_values, key)
                and (int(row["comparable_normalized_rank"]), int(row["comparable_normalized_tie_count"])) == rank_of(normalized_values, key),
                f"independent mirror ranks/decomposition {view}/{key[0]}/{key[1]}",
            )
        view_rows = [row for row in rankings if row["view_id"] == view]
        audit.check(sum(row["is_reported_f9_r0"] == "YES" for row in view_rows) == 1 and sum(row["is_identity"] == "YES" for row in view_rows) == 1, f"mirror marker uniqueness {view}")

    boundary_f9 = ranking_map["BOUNDARY_NED", "F9", "R0"]
    audit.check((boundary_f9["raw_rank"], boundary_f9["comparable_normalized_rank"]) == ("1", "1"), "boundary F9/R0 leads full grid")
    for view in ("ZL_MEMBER_NED", "IT_MEMBER_NED", "RF_MEMBER_NED"):
        audit.check(ranking_map[view, "F9", "R0"]["exact_value_hits"] == "0", f"{view} F9/R0 exact identities zero")

    audit.check(len(nulls) == 16 and Counter(row["view_id"] for row in nulls) == Counter({view: 2 for view, _, _ in VIEW_SPECS}), "16 mirror null summaries")
    for row in nulls:
        raw = row["null_id"] == "INCLUSIVE_NA_RAW_SUM"
        selected = ranking_map[row["view_id"], row["observed_best_transform_71"], row["observed_best_transform_72"]]
        audit.check(
            row["iterations"] == "4096" and row["seed"] == ("79510" if raw else "796013")
            and row["score_id"] == ("RAW_SUM__NA_PAIR_ZERO" if raw else "SUM_OF_THREE_PAIR_MEANS"),
            f"mirror null protocol {row['view_id']}/{row['null_id']}",
        )
        audit.check(
            selected["raw_rank" if raw else "comparable_normalized_rank"] == "1"
            and row["observed_best_score"] == selected["raw_score" if raw else "comparable_normalized_score"]
            and row["observed_best_tie_count"] == selected["raw_tie_count" if raw else "comparable_normalized_tie_count"]
            and row["add_one_p"] == f12((int(row["null_ge_observed"]) + 1) / 4097),
            f"mirror null optimum/add-one arithmetic {row['view_id']}/{row['null_id']}",
        )
    boundary_raw = next(row for row in nulls if row["view_id"] == "BOUNDARY_NED" and row["null_id"] == "INCLUSIVE_NA_RAW_SUM")
    boundary_fixed = next(row for row in nulls if row["view_id"] == "BOUNDARY_NED" and row["null_id"] == "FIXED_MASK_COMPARABLE_NORMALIZED")
    audit.check((boundary_raw["observed_best_transform_71"], boundary_raw["observed_best_transform_72"], boundary_raw["add_one_p"]) == ("F9", "R0", "0.003905296558"), "boundary inclusive-null control")
    audit.check((boundary_fixed["observed_best_transform_71"], boundary_fixed["observed_best_transform_72"], boundary_fixed["add_one_p"]) == ("F9", "R0", "0.034415425921"), "boundary fixed-mask-null control")

    audit.check(len(splits) == 16 and Counter(row["view_id"] for row in splits) == Counter({view: 2 for view, _, _ in VIEW_SPECS}), "16 split-half rows")
    view_specs = {view: (source, metric) for view, source, metric in VIEW_SPECS}
    for row in splits:
        train = tuple(int(value) - 6 for value in row["train_a_members"].split("|"))
        test = tuple(int(value) - 6 for value in row["test_a_members"].split("|"))
        audit.check(set(train).isdisjoint(test) and set(train) | set(test) == set(range(10)), f"split partition {row['view_id']}/{row['split_id']}")
        source_field, metric = view_specs[row["view_id"]]
        train_grid = mirror_grid(panel, source_field, metric, train)
        test_grid = mirror_grid(panel, source_field, metric, test)
        for prefix, score_field in (("raw", "raw"), ("comparable_normalized", "normalized")):
            chosen = grid_best(train_grid, score_field)
            test_values = {key: float(score[score_field]) for key, score in test_grid.items()}
            best_value = float(train_grid[chosen][score_field])
            audit.check(
                (row[f"{prefix}_selected_transform_71"], row[f"{prefix}_selected_transform_72"]) == chosen
                and row[f"{prefix}_train_score"] == f12(best_value)
                and int(row[f"{prefix}_train_best_tie_count"]) == sum(abs(float(score[score_field]) - best_value) <= 1e-12 for score in train_grid.values())
                and row[f"{prefix}_test_score"] == f12(float(test_grid[chosen][score_field]))
                and (int(row[f"{prefix}_test_rank"]), int(row[f"{prefix}_test_tie_count"])) == rank_of(test_values, chosen),
                f"independent split score {row['view_id']}/{row['split_id']}/{prefix}",
            )
    boundary_splits = [row for row in splits if row["view_id"] == "BOUNDARY_NED"]
    audit.check([int(row["raw_test_rank"]) for row in boundary_splits] == [122, 7], "boundary raw split ranks 122/7")
    audit.check([int(row["comparable_normalized_test_rank"]) for row in boundary_splits] == [203, 264], "boundary normalized split ranks 203/264")
    audit.check(sum(all(int(row["raw_test_rank"]) <= 40 for row in splits if row["view_id"] == view) for view, _, _ in VIEW_SPECS) == 0, "no view leads raw decile in both splits")

    audit.check(len(contributions) == 10 and [int(row["semantic_a_member"]) for row in contributions] == list(outer_members), "ten ordered position contributions")
    for row in contributions:
        coordinate = int(row["local_coordinate"])
        f9 = mirror_score(panel, "canonical_boundary_family", "CHAR_NORMALIZED_LEVENSHTEIN", "F9", "R0", (coordinate,))
        identity = mirror_score(panel, "canonical_boundary_family", "CHAR_NORMALIZED_LEVENSHTEIN", "R0", "R0", (coordinate,))
        audit.check(
            row["f9_f70_f71_similarity"] == f12(float(f9["raw_01"])) and row["f9_f70_f72_similarity"] == f12(float(f9["raw_02"]))
            and row["f9_f71_f72_similarity"] == f12(float(f9["raw_12"])) and row["f9_total_contribution"] == f12(float(f9["raw"]))
            and row["identity_total_contribution"] == f12(float(identity["raw"])) and row["f9_minus_identity"] == f12(float(f9["raw"]) - float(identity["raw"]))
            and int(row["f9_exact_pair_hits"]) == f9["exact"],
            f"independent position contribution {row['semantic_a_member']}",
        )
    delta_signs = Counter("POS" if float(row["f9_minus_identity"]) > 1e-12 else "NEG" if float(row["f9_minus_identity"]) < -1e-12 else "TIE" for row in contributions)
    audit.check(delta_signs == Counter({"POS": 7, "NEG": 1, "TIE": 2}), "F9 position deltas are 7 positive, 1 negative, 2 tied")
    audit.check(sum(row["missing_slot_in_reference_pair"] == "YES" for row in contributions) == 1, "only A14 has missing reference pair")
    audit.check(f12(sum(float(row["f9_total_contribution"]) for row in contributions)) == boundary_f9["raw_score"], "position contributions sum to F9 score")

    # Pairwise fixed-mask null: independently re-optimize the 20 relative transforms.
    boundary_values = [[None if row is None else row["canonical_boundary_family"] for row in page] for page in panel]
    sim_matrices = {(left, right): np.asarray([[similarity(a, b, "CHAR_NORMALIZED_LEVENSHTEIN") for b in boundary_values[right]] for a in boundary_values[left]]) for left, right in ((0, 1), (0, 2), (1, 2))}
    comp_matrices = {(left, right): np.asarray([[float(a is not None and b is not None) for b in boundary_values[right]] for a in boundary_values[left]]) for left, right in ((0, 1), (0, 2), (1, 2))}
    transform_indices = np.asarray([[transform_coordinate(name, coordinate) for coordinate in range(10)] for name, _, _ in TRANSFORMS])
    reference = np.arange(10)
    observed_pairwise: dict[tuple[int, int], float] = {}
    for pair in sim_matrices:
        left, _ = pair
        if left == 0:
            candidates = [sim_matrices[pair][reference, indices].sum() / comp_matrices[pair][reference, indices].sum() for indices in transform_indices]
        else:
            candidates = [sim_matrices[pair][indices, reference].sum() / comp_matrices[pair][indices, reference].sum() for indices in transform_indices]
        observed_pairwise[pair] = max(candidates)
    rng = np.random.default_rng(796013)
    allowed_masks = (np.asarray((0, 1, 2, 3, 4, 5, 6, 7, 9)), np.arange(10), np.asarray((0, 1, 2, 3, 4, 5, 6, 7, 9)))
    exceed = Counter()
    for _ in range(4096):
        permutations = []
        for allowed in allowed_masks:
            permutation = np.arange(10)
            permutation[allowed] = rng.permutation(allowed)
            permutations.append(permutation)
        for pair in sim_matrices:
            left, right = pair
            if left == 0:
                candidates = [sim_matrices[pair][permutations[left], permutations[right][indices]].sum() / comp_matrices[pair][reference, indices].sum() for indices in transform_indices]
            else:
                candidates = [sim_matrices[pair][permutations[left][indices], permutations[right]].sum() / comp_matrices[pair][indices, reference].sum() for indices in transform_indices]
            exceed[pair] += max(candidates) >= observed_pairwise[pair] - 1e-12
    pairwise_p = {pair: (exceed[pair] + 1) / 4097 for pair in exceed}
    audit.check((exceed[0, 1], exceed[1, 2], exceed[0, 2]) == (124, 319, 3364), "pairwise fixed-mask exceedance controls")
    audit.check(tuple(f12(pairwise_p[pair]) for pair in ((0, 1), (1, 2), (0, 2))) == ("0.030510129363", "0.078105931169", "0.821332682451"), "pairwise effect is f70-f71 driven")

    # Rebuild the useful visual join and its held-folio/block controls.
    useful = [row for row in visual_source_rows if row["channel"] in VISUAL_CHANNELS]
    expected_states = Counter({
        ("ZODIAC_BARREL", "PRESENT"): 55, ("ZODIAC_BARREL", "ABSENT"): 22,
        ("ZODIAC_CLOTHING", "DRESSED"): 11, ("ZODIAC_CLOTHING", "UNDRESSED"): 14,
        ("ZODIAC_CLOTHING", "UNCERTAIN"): 5, ("ZODIAC_FACING", "PROFILE"): 10,
        ("ZODIAC_FACING", "NON_DIRECTIONAL"): 57,
    })
    audit.check(len(useful) == 174 and len({(row["channel"], row["locus"]) for row in useful}) == 174, "174 unique useful visual events")
    audit.check(Counter((row["channel"], row["visual_state"]) for row in useful) == expected_states, "visual state census")
    audit.check(len(visual_atlas) == 174 and [int(row["visual_event_ordinal"]) for row in visual_atlas] == list(range(1, 175)), "ordered 174-row visual atlas")
    source_by_key = {(row["channel"], row["locus"]): row for row in useful}
    formal_by_locus = {row["locus"]: row for row in atlas}
    block_states: dict[tuple[str, str], Counter[str]] = defaultdict(Counter)
    for row in useful:
        block_states[row["channel"], row["array_id"]][row["visual_state"]] += 1
    for row in visual_atlas:
        source = source_by_key.get((row["channel"], row["locus"]))
        formal = formal_by_locus.get(row["locus"])
        counts = block_states[row["channel"], row["visual_array_id"]]
        audit.check(
            source is not None and formal is not None and row["visual_state"] == source["visual_state"]
            and row["physical_folio"] == source["physical_folio"] and row["source_selector"] == source["page"]
            and row["visual_array_id"] == source["array_id"] and row["atlas_array_id"] == formal["array_id"]
            and row["kluge_a_member"] == formal["kluge_a_member"] and row["complete_label_surface"] == formal["complete_label_surface"]
            and row["canonical_boundary_family"] == formal["canonical_boundary_family"]
            and row["canonical_compact_family"] == formal["canonical_compact_family"]
            and row["transferred_prefix"] == formal["transferred_prefix"] and row["strict_residual"] == formal["strict_residual"],
            f"visual guarded join {row['channel']}/{row['locus']}",
        )
        audit.check(
            row["block_state_counts"] == joined(f"{state}:{count}" for state, count in sorted(counts.items()))
            and row["block_is_state_pure"] == ("YES" if len(counts) == 1 else "NO")
            and row["semantic_ceiling"] == "EXISTING_VISUAL_STATE_CANDIDATE_ONLY",
            f"visual block state {row['channel']}/{row['locus']}",
        )

    transfer_by_key = {(row["channel"], row["representation_id"]): row for row in visual_transfer}
    audit.check(len(visual_transfer) == 12 and set(transfer_by_key) == {(channel, rep) for channel in VISUAL_CHANNELS for rep, _ in VISUAL_REPRESENTATIONS}, "complete 3x4 visual transfer grid")
    for channel_index, channel in enumerate(VISUAL_CHANNELS):
        records = [row for row in visual_atlas if row["channel"] == channel]
        blocks = {row["visual_array_id"] for row in records}
        pure_blocks = sum(len({row["visual_state"] for row in records if row["visual_array_id"] == block}) == 1 for block in blocks)
        for rep_index, (representation, source_field) in enumerate(VISUAL_REPRESENTATIONS):
            row = transfer_by_key[channel, representation]
            local = local_prediction(records, source_field)
            lofo = prediction(records, source_field, "physical_folio")
            lopo = prediction(records, source_field, "source_selector")
            rng_visual = random.Random(796100 + channel_index * 10 + rep_index)
            null_gains = [prediction(shuffled_visual(records, rng_visual), source_field, "physical_folio")["gain"] for _ in range(1000)]
            p_value = (1 + sum(value >= lofo["gain"] - 1e-12 for value in null_gains)) / 1001
            audit.check(
                row["source_field"] == source_field and int(row["event_count"]) == len(records)
                and int(row["state_count"]) == len({item["visual_state"] for item in records})
                and row["states"] == joined(sorted({item["visual_state"] for item in records}))
                and int(row["visual_block_count"]) == len(blocks) and int(row["state_pure_block_count"]) == pure_blocks,
                f"visual capacities {channel}/{representation}",
            )
            audit.check(
                int(row["local_block_loo_covered"]) == local["covered"] and row["local_block_loo_credit"] == f6(local["credit"])
                and row["local_block_loo_accuracy"] == f6(local["accuracy"])
                and int(row["held_physical_folio_covered"]) == lofo["covered"]
                and row["held_physical_folio_key_credit"] == f6(lofo["credit"])
                and row["held_physical_folio_key_accuracy"] == f6(lofo["accuracy"])
                and row["held_physical_folio_baseline_credit"] == f6(lofo["baseline"])
                and row["held_physical_folio_baseline_accuracy"] == f6(lofo["baseline_accuracy"])
                and row["held_physical_folio_gain"] == f6(lofo["gain"])
                and int(row["held_source_page_covered"]) == lopo["covered"]
                and row["held_source_page_key_credit"] == f6(lopo["credit"])
                and row["held_source_page_key_accuracy"] == f6(lopo["accuracy"]),
                f"visual prediction arithmetic {channel}/{representation}",
            )
            audit.check(
                row["visual_null_iterations"] == "1000" and row["visual_null_mean_gain"] == f6(sum(null_gains) / 1000)
                and row["visual_null_p_gain_ge_observed"] == f6(p_value)
                and row["decision"] == "BLOCK_CONFOUNDED_OR_NO_GENERAL_STATUS_TRANSFER" and row["semantic_export"] == "NONE",
                f"visual null and ceiling {channel}/{representation}",
            )

    expected_census_keys = []
    for channel in VISUAL_CHANNELS:
        grouped: dict[str, list[dict[str, str]]] = defaultdict(list)
        for row in visual_atlas:
            if row["channel"] == channel:
                grouped[row["canonical_boundary_family"]].append(row)
        expected_census_keys.extend((channel, family) for family, rows in grouped.items() if len(rows) >= 2)
    audit.check(len(visual_census) == 20 and {(row["channel"], row["canonical_boundary_family"]) for row in visual_census} == set(expected_census_keys), "20 recurrent visual family rows")
    for row in visual_census:
        events = [item for item in visual_atlas if item["channel"] == row["channel"] and item["canonical_boundary_family"] == row["canonical_boundary_family"]]
        audit.check(
            int(row["event_count"]) == len(events) and row["state_counts"] == count_text([item["visual_state"] for item in events])
            and row["state_purity"] == f6(max(Counter(item["visual_state"] for item in events).values()) / len(events))
            and int(row["physical_folio_count"]) == len({item["physical_folio"] for item in events})
            and int(row["source_page_count"]) == len({item["source_selector"] for item in events})
            and row["candidate_ceiling"] == "COMPLETE_FAMILY_VISUAL_STATUS_RIVAL_ONLY" and row["component_export_credit"] == "ZERO",
            f"visual recurrent census {row['channel']}/{row['canonical_boundary_family']}",
        )

    card_keys = {
        "BARREL_AQABAG": ("ZODIAC_BARREL", "AQABAG"),
        "CLOTHING_AQKA_ACA": ("ZODIAC_CLOTHING", "AQKA|ACA"),
        "FACING_AQACAB": ("ZODIAC_FACING", "AQACAB"),
    }
    audit.check(len(visual_cards) == 3 and {row["card_id"] for row in visual_cards} == set(card_keys), "three visual rivals, zero selected cards")
    cards_by_id = {row["card_id"]: row for row in visual_cards}
    for card_id, (channel, family) in card_keys.items():
        row = cards_by_id[card_id]
        events = [item for item in visual_atlas if item["channel"] == channel and item["canonical_boundary_family"] == family]
        audit.check(
            int(row["event_count"]) == len(events) and row["state_counts"] == count_text([item["visual_state"] for item in events])
            and int(row["physical_folio_count"]) == len({item["physical_folio"] for item in events})
            and int(row["source_page_count"]) == len({item["source_selector"] for item in events})
            and int(row["visual_block_count"]) == len({item["visual_array_id"] for item in events}),
            f"visual card census {card_id}",
        )
        audit.check(
            row["confidence"] == "EXPLORATORY_RIVAL_BELOW_GDT796_GATE" and row["renderer_license"] == "NONE__CANDIDATE_DECK_ONLY"
            and row["prose_export_allowed"] == "NO" and row["component_export_credit"] == "ZERO" and row["confirmed_lexeme"] == "NO"
            and bool(row["evidence"] and row["counterevidence"]),
            f"visual card below gate {card_id}",
        )
    audit.check(all(item["block_is_state_pure"] == "YES" for item in visual_atlas if item["channel"] == "ZODIAC_BARREL" and item["canonical_boundary_family"] == "AQABAG"), "barrel card entirely block-confounded")
    audit.check(cards_by_id["CLOTHING_AQKA_ACA"]["physical_folio_count"] == "1", "clothing card lacks cross-folio support")
    audit.check(cards_by_id["FACING_AQACAB"]["visual_block_count"] == "1", "facing card confined to one block")

    # Independently map both historical matrices through all 240 global transforms.
    _, phase_rows = read_tsv(PHASE_SPECS)
    _, matrix_rows = read_tsv(FACIES_MATRICES)
    _, source_rows = read_tsv(HISTORICAL_SOURCES)
    audit.check(len(phase_rows) == 5 and len({row["source_selector"] for row in phase_rows}) == 5, "five page/sign phase specifications")
    audit.check(len(source_rows) == 6 and all(row["evidence_boundary"] for row in source_rows), "six bounded historical source records")
    public_signs = {row["page"]: (row["sign"].strip().split()[0].upper(), row["physical_folio"]) for row in sign_source_rows}
    phases: dict[str, dict[str, Any]] = {}
    for row in phase_rows:
        audit.check(public_signs.get(row["source_selector"]) == (row["sign"], row["physical_folio"]), f"guarded page/sign mapping {row['source_selector']}")
        phases[row["source_selector"]] = {**row, "h0_base_add": int(row["h0_base_add"]), "h1_base_add": int(row["h1_base_add"])}
    status_by_planet = {"JUPITER": "BENEFIC", "VENUS": "BENEFIC", "MARS": "MALEFIC", "SATURN": "MALEFIC", "SOL": "OTHER", "MOON": "OTHER", "MERCURY": "OTHER"}
    matrices: dict[tuple[str, str, int], dict[str, str]] = {}
    for row in matrix_rows:
        key = (row["matrix_id"], row["sign"], int(row["facies_index"]))
        audit.check(key not in matrices, f"unique historical matrix cell {key}")
        matrices[key] = row
        audit.check(
            int(row["degree_start"]) == (int(row["facies_index"]) - 1) * 10 + 1
            and int(row["degree_end"]) == int(row["facies_index"]) * 10
            and status_by_planet.get(row["planet"]) == row["coarse_status"],
            f"historical matrix cell arithmetic {key}",
        )
    audit.check(len(matrix_rows) == len(matrices) == 72 and {key[0] for key in matrices} == {"PICATRIX_INDIAN", "CHALDEAN"}, "two complete 12x3 matrices")
    primary_pages = {page for page, spec in phases.items() if spec["primary_matrix_use"] == "YES"}
    base_events = [dict(row) for row in atlas if row["source_selector"] in primary_pages]
    for row in base_events:
        row["sign"] = phases[row["source_selector"]]["sign"]
    audit.check(len(base_events) == 87 and Counter(row["sign"] for row in base_events) == Counter({"PISCES": 29, "TAURUS": 29, "GEMINI": 29}), "facies panel 29/29/29")
    audit.check("f70v1" not in {row["source_selector"] for row in base_events}, "unpaired Aries page excluded from primary")

    transform_by_key = {(row["matrix_id"], row["taurus_phase"], int(row["direction"]), int(row["offset"])): row for row in transform_rows}
    expected_transform_keys = {(matrix_id, phase, direction, offset) for matrix_id in ("PICATRIX_INDIAN", "CHALDEAN") for phase in ("H0", "H1") for direction in (1, -1) for offset in range(30)}
    audit.check(len(transform_rows) == len(transform_by_key) == 240 and set(transform_by_key) == expected_transform_keys, "240 unique historical transform rows")
    mapped_cache: dict[tuple[str, str, int, int], list[dict[str, Any]]] = {}
    for key in expected_transform_keys:
        matrix_id, phase, direction, offset = key
        mapped = [mapped_event(row, phase, matrix_id, direction, offset, phases, matrices) for row in base_events]
        mapped_cache[key] = mapped
        score_all = facies_score(mapped)
        score_without = facies_score(mapped, {"AQABAC"})
        target = [row for row in mapped if row["canonical_boundary_family"] == "AQABAC"]
        target_status = purity([row["coarse_status"] for row in target])
        target_planet = purity([row["planet"] for row in target])
        actual = transform_by_key[key]
        audit.check(
            int(actual["cross_sign_recurrent_family_count"]) == score_all["family_count"]
            and actual["family_balanced_status_purity"] == f6(score_all["status_purity"])
            and actual["family_balanced_planet_purity"] == f6(score_all["planet_purity"])
            and int(actual["consistent_status_family_count"]) == score_all["consistent_status"]
            and int(actual["consistent_planet_family_count"]) == score_all["consistent_planet"]
            and int(actual["training_without_aqabac_family_count"]) == score_without["family_count"]
            and actual["training_without_aqabac_status_purity"] == f6(score_without["status_purity"])
            and actual["training_without_aqabac_planet_purity"] == f6(score_without["planet_purity"])
            and int(actual["training_without_aqabac_consistent_status_count"]) == score_without["consistent_status"],
            f"independent facies scores {matrix_id}/{phase}/D{direction}/O{offset}",
        )
        audit.check(
            int(actual["aqabac_event_count"]) == len(target) and actual["aqabac_status_purity"] == f6(target_status[0])
            and actual["aqabac_status_modes"] == target_status[1] and actual["aqabac_status_counts"] == target_status[2]
            and actual["aqabac_planet_purity"] == f6(target_planet[0]) and actual["aqabac_planet_modes"] == target_planet[1]
            and actual["aqabac_planet_counts"] == target_planet[2]
            and actual["aqabac_all_benefic"] == ("YES" if all(row["coarse_status"] == "BENEFIC" for row in target) else "NO")
            and actual["semantic_export"] == "NONE",
            f"independent AQABAC grid diagnostic {matrix_id}/{phase}/D{direction}/O{offset}",
        )
    audit.check(all(row["cross_sign_recurrent_family_count"] == "9" and row["training_without_aqabac_family_count"] == "8" for row in transform_rows), "global family capacity 9/8")

    selected_by_key: dict[tuple[str, str], tuple[int, int, dict[str, Any], list[dict[str, Any]]]] = {}
    selected_map = {(row["matrix_id"], row["taurus_phase"]): row for row in selected_rows}
    audit.check(len(selected_rows) == len(selected_map) == 4, "four selected matrix/phase summaries")
    for key, actual in selected_map.items():
        matrix_id, phase = key
        direction, offset, score, mapped = select_facies(base_events, phase, matrix_id, phases, matrices, {"AQABAC"})
        selected_by_key[key] = (direction, offset, score, mapped)
        target = [row for row in mapped if row["canonical_boundary_family"] == "AQABAC"]
        target_status = purity([row["coarse_status"] for row in target])
        target_planet = purity([row["planet"] for row in target])
        relevant = [row for row in transform_rows if row["matrix_id"] == matrix_id and row["taurus_phase"] == phase]
        audit.check(
            actual["selected_without_family"] == "AQABAC" and (int(actual["selected_direction"]), int(actual["selected_offset"])) == (direction, offset)
            and int(actual["training_family_count"]) == score["family_count"]
            and actual["training_family_balanced_status_purity"] == f6(score["status_purity"])
            and actual["training_family_balanced_planet_purity"] == f6(score["planet_purity"])
            and int(actual["training_consistent_status_family_count"]) == score["consistent_status"]
            and int(actual["training_consistent_planet_family_count"]) == score["consistent_planet"],
            f"selected target-masked model {matrix_id}/{phase}",
        )
        audit.check(
            actual["aqabac_status_purity"] == f6(target_status[0]) and actual["aqabac_status_counts"] == target_status[2]
            and actual["aqabac_planet_purity"] == f6(target_planet[0]) and actual["aqabac_planet_counts"] == target_planet[2]
            and int(actual["aqabac_uniform_status_transform_count"]) == sum(float(row["aqabac_status_purity"]) == 1.0 for row in relevant)
            and int(actual["aqabac_all_benefic_transform_count"]) == sum(row["aqabac_all_benefic"] == "YES" for row in relevant)
            and int(actual["aqabac_uniform_planet_transform_count"]) == sum(float(row["aqabac_planet_purity"]) == 1.0 for row in relevant),
            f"selected AQABAC evaluation {matrix_id}/{phase}",
        )
        p_numerator = round(float(actual["null_p_optimized_status_ge_observed"]) * 1001)
        audit.check(
            actual["null_iterations"] == "1000" and 1 <= p_numerator <= 1001
            and abs(float(actual["null_p_optimized_status_ge_observed"]) - p_numerator / 1001) <= 5.1e-7
            and 0 <= float(actual["null_mean_optimized_training_status_purity"]) <= 1
            and actual["semantic_export"] == "NONE",
            f"facies null arithmetic/ceiling {matrix_id}/{phase}",
        )

    lofo_map = {(row["matrix_id"], row["taurus_phase"], row["held_family"]): row for row in lofo_rows}
    audit.check(len(lofo_rows) == len(lofo_map) == 36, "36 unique leave-one-family rows")
    for key, actual in lofo_map.items():
        matrix_id, phase, family = key
        direction, offset, score, mapped = select_facies(base_events, phase, matrix_id, phases, matrices, {family})
        held = [row for row in mapped if row["canonical_boundary_family"] == family]
        status = purity([row["coarse_status"] for row in held])
        planet = purity([row["planet"] for row in held])
        audit.check(
            (int(actual["selected_direction"]), int(actual["selected_offset"])) == (direction, offset)
            and int(actual["training_family_count"]) == score["family_count"] and actual["training_status_purity"] == f6(score["status_purity"])
            and int(actual["held_event_count"]) == len(held) and int(actual["held_sign_count"]) == len({row["sign"] for row in held})
            and actual["held_signs"] == joined(sorted({row["sign"] for row in held}))
            and actual["held_status_purity"] == f6(status[0]) and actual["held_status_modes"] == status[1] and actual["held_status_counts"] == status[2]
            and actual["held_planet_purity"] == f6(planet[0]) and actual["held_planet_modes"] == planet[1] and actual["held_planet_counts"] == planet[2]
            and actual["held_consistent_status"] == ("YES" if status[0] == 1 else "NO")
            and actual["held_consistent_planet"] == ("YES" if planet[0] == 1 else "NO") and actual["semantic_export"] == "NONE",
            f"independent LOFO {matrix_id}/{phase}/{family}",
        )

    # Leave-one-sign-out: distinguish training capacity, broad audit capacity, and eligible held prediction.
    sign_out_map = {(row["matrix_id"], row["taurus_phase"], row["held_sign"], row["held_family"]): row for row in sign_out_rows}
    audit.check(len(sign_out_rows) == len(sign_out_map) == 24, "24 unique leave-one-sign rows")
    train_capacity = {"PISCES": 5, "TAURUS": 5, "GEMINI": 3}
    masked_train_capacity = {"PISCES": 4, "TAURUS": 4, "GEMINI": 2}
    broad_capacity = {"PISCES": 6, "TAURUS": 6, "GEMINI": 8}
    masked_broad_capacity = {"PISCES": 5, "TAURUS": 5, "GEMINI": 7}
    family_signs: dict[str, set[str]] = defaultdict(set)
    for row in base_events:
        family_signs[row["canonical_boundary_family"]].add(row["sign"])
    for matrix_id in ("PICATRIX_INDIAN", "CHALDEAN"):
        for phase in ("H0", "H1"):
            for held_sign in ("PISCES", "TAURUS", "GEMINI"):
                training_events = [row for row in base_events if row["sign"] != held_sign]
                held_events = [row for row in base_events if row["sign"] == held_sign]
                broad = sorted(family for family, signs in family_signs.items() if held_sign in signs and bool(signs - {held_sign}))
                direction, offset, score, training_mapped = select_facies(training_events, phase, matrix_id, phases, matrices, {"AQABAC"})
                held_mapped = [mapped_event(row, phase, matrix_id, direction, offset, phases, matrices) for row in held_events]
                training_groups = family_groups(training_mapped)
                held_groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
                for row in held_mapped:
                    held_groups[row["canonical_boundary_family"]].append(row)
                eligible = sorted(set(training_groups) & set(held_groups))
                audit.check(len(training_groups) == train_capacity[held_sign] and score["family_count"] == masked_train_capacity[held_sign], f"LOSO 5/5/3 and 4/4/2 capacity {matrix_id}/{phase}/{held_sign}")
                audit.check(len(broad) == broad_capacity[held_sign] and len([family for family in broad if family != "AQABAC"]) == masked_broad_capacity[held_sign], f"LOSO broad 6/6/8 and 5/5/7 capacity {matrix_id}/{phase}/{held_sign}")
                audit.check(eligible == ["AQABAB", "AQABAC"], f"LOSO eligible families {matrix_id}/{phase}/{held_sign}")
                for family in eligible:
                    actual = sign_out_map[matrix_id, phase, held_sign, family]
                    training = training_groups[family]
                    held = held_groups[family]
                    training_status = purity([row["coarse_status"] for row in training])
                    held_status = purity([row["coarse_status"] for row in held])
                    training_planet = purity([row["planet"] for row in training])
                    held_planet = purity([row["planet"] for row in held])
                    status_match = {row["coarse_status"] for row in held} <= set(training_status[1].split("|"))
                    planet_match = {row["planet"] for row in held} <= set(training_planet[1].split("|"))
                    target = family == "AQABAC"
                    expected_status_prediction = "NA_TARGET" if target else "NA_TIED_TRAINING" if training_status[0] < 1 else "YES" if status_match else "NO"
                    expected_planet_prediction = "NA_TARGET" if target else "NA_TIED_TRAINING" if training_planet[0] < 1 else "YES" if planet_match else "NO"
                    audit.check(
                        (int(actual["selected_direction_without_aqabac"]), int(actual["selected_offset_without_aqabac"])) == (direction, offset)
                        and int(actual["training_cross_sign_family_capacity_all"]) == train_capacity[held_sign]
                        and int(actual["training_family_count_without_aqabac"]) == masked_train_capacity[held_sign]
                        and int(actual["held_any_training_family_capacity_all"]) == broad_capacity[held_sign]
                        and int(actual["held_any_training_family_capacity_without_aqabac"]) == masked_broad_capacity[held_sign]
                        and actual["eligible_held_family_count_all"] == "2" and actual["eligible_held_family_count_without_aqabac"] == "1",
                        f"LOSO published capacities {matrix_id}/{phase}/{held_sign}/{family}",
                    )
                    audit.check(
                        int(actual["training_event_count"]) == len(training) and int(actual["held_event_count"]) == len(held)
                        and actual["training_status_purity"] == f6(training_status[0]) and actual["training_status_modes"] == training_status[1]
                        and actual["training_status_counts"] == training_status[2] and actual["held_status_purity"] == f6(held_status[0])
                        and actual["held_status_modes"] == held_status[1] and actual["held_status_counts"] == held_status[2]
                        and actual["held_status_matches_training_mode"] == ("YES" if status_match else "NO")
                        and actual["training_status_unambiguous"] == ("YES" if training_status[0] == 1 else "NO")
                        and actual["held_status_prediction_correct"] == expected_status_prediction,
                        f"LOSO independent status prediction {matrix_id}/{phase}/{held_sign}/{family}",
                    )
                    audit.check(
                        actual["training_planet_purity"] == f6(training_planet[0]) and actual["training_planet_modes"] == training_planet[1]
                        and actual["training_planet_counts"] == training_planet[2] and actual["held_planet_purity"] == f6(held_planet[0])
                        and actual["held_planet_modes"] == held_planet[1] and actual["held_planet_counts"] == held_planet[2]
                        and actual["held_planet_matches_training_mode"] == ("YES" if planet_match else "NO")
                        and actual["training_planet_unambiguous"] == ("YES" if training_planet[0] == 1 else "NO")
                        and actual["held_planet_prediction_correct"] == expected_planet_prediction
                        and actual["semantic_export"] == "NONE",
                        f"LOSO independent planet prediction {matrix_id}/{phase}/{held_sign}/{family}",
                    )
    audit.check({row["held_family"] for row in sign_out_rows} == {"AQABAB", "AQABAC"} and not any(row["held_family"] == "AQABBA" for row in sign_out_rows), "AQABBA lacks sign-holdout capacity")
    picatrix_non_target = [row for row in sign_out_rows if row["matrix_id"] == "PICATRIX_INDIAN" and row["aqabac_target_diagnostic"] == "NO"]
    audit.check(sum(row["held_status_matches_training_mode"] == "YES" for row in picatrix_non_target) == 3 and len(picatrix_non_target) == 6, "Picatrix broad-mode LOSO is 3/6")
    audit.check(sum(row["held_status_prediction_correct"] in {"YES", "NO"} for row in picatrix_non_target) == 5 and sum(row["held_status_prediction_correct"] == "YES" for row in picatrix_non_target) == 2, "Picatrix unambiguous LOSO is 2/5")

    audit.check(len(aqabac_rows) == 24 and Counter((row["matrix_id"], row["taurus_phase"], row["evaluation_id"]) for row in aqabac_rows) == Counter({(matrix_id, phase, evaluation): 3 for matrix_id in ("PICATRIX_INDIAN", "CHALDEAN") for phase in ("H0", "H1") for evaluation in ("NOMINAL_R0", "SELECTED_WITHOUT_AQABAC")}), "24 AQABAC event rivals")
    for row in aqabac_rows:
        if row["evaluation_id"] == "NOMINAL_R0":
            direction, offset = 1, 0
        else:
            direction, offset = selected_by_key[row["matrix_id"], row["taurus_phase"]][:2]
        source = next(event for event in base_events if event["locus"] == row["locus"])
        expected = mapped_event(source, row["taurus_phase"], row["matrix_id"], direction, offset, phases, matrices)
        audit.check(
            (int(row["direction"]), int(row["offset"])) == (direction, offset) and row["sign"] == expected["sign"]
            and int(row["base_position"]) == expected["base_position"] and int(row["transformed_degree"]) == expected["transformed_degree"]
            and int(row["facies_index"]) == expected["facies_index"] and row["planet"] == expected["planet"] and row["coarse_status"] == expected["coarse_status"]
            and row["confidence"] == "C0_HISTORICAL_MATRIX_RIVAL" and row["component_export_credit"] == "ZERO",
            f"independent AQABAC event {row['matrix_id']}/{row['taurus_phase']}/{row['evaluation_id']}/{row['locus']}",
        )

    census_map = {(row["matrix_id"], row["taurus_phase"], row["canonical_boundary_family"]): row for row in historical_census}
    audit.check(len(historical_census) == len(census_map) == 36, "36 unique historical family census rows")
    for (matrix_id, phase), (direction, offset, _, mapped) in selected_by_key.items():
        for family, events in family_groups(mapped).items():
            actual = census_map[matrix_id, phase, family]
            status = purity([row["coarse_status"] for row in events])
            planet = purity([row["planet"] for row in events])
            audit.check(
                (int(actual["selected_direction_without_aqabac"]), int(actual["selected_offset_without_aqabac"])) == (direction, offset)
                and int(actual["event_count"]) == len(events) and int(actual["sign_count"]) == len({row["sign"] for row in events})
                and actual["status_counts"] == status[2] and actual["status_purity"] == f6(status[0]) and actual["status_modes"] == status[1]
                and actual["planet_counts"] == planet[2] and actual["planet_purity"] == f6(planet[0]) and actual["planet_modes"] == planet[1]
                and actual["fixed_status_candidate"] == ("YES" if status[0] == 1 else "NO")
                and actual["fixed_planet_candidate"] == ("YES" if planet[0] == 1 else "NO") and actual["semantic_export"] == "NONE",
                f"independent historical census {matrix_id}/{phase}/{family}",
            )

    picatrix_h0 = selected_map["PICATRIX_INDIAN", "H0"]
    picatrix_h1 = selected_map["PICATRIX_INDIAN", "H1"]
    audit.check(
        (picatrix_h0["selected_direction"], picatrix_h0["selected_offset"]) != (picatrix_h1["selected_direction"], picatrix_h1["selected_offset"])
        and picatrix_h0["aqabac_status_counts"] != picatrix_h1["aqabac_status_counts"],
        "Picatrix global fit and target assignment are phase-unstable",
    )
    phase_consistent = {
        phase: {row["held_family"] for row in lofo_rows if row["matrix_id"] == "PICATRIX_INDIAN" and row["taurus_phase"] == phase and row["held_consistent_status"] == "YES"}
        for phase in ("H0", "H1")
    }
    audit.check(phase_consistent["H0"] & phase_consistent["H1"] == {"AQABBA"}, "AQABBA sole Picatrix H0/H1 LOFO intersection")
    aqabba = [row for row in lofo_rows if row["held_family"] == "AQABBA"]
    audit.check(
        all(row["held_event_count"] == "2" and row["held_signs"] == "GEMINI|PISCES" for row in aqabba)
        and all(row["held_status_counts"] == "BENEFIC:2" for row in aqabba if row["matrix_id"] == "PICATRIX_INDIAN")
        and any(row["matrix_id"] == "CHALDEAN" and row["held_status_counts"] != "BENEFIC:2" for row in aqabba),
        "AQABBA is two-event Pisces/Gemini and Chaldean-contradicted",
    )

    candidate_map = {row["candidate_id"]: row for row in adjudication}
    expected_candidates = {
        "F71_OUTER10_F9_MIRROR", "VISIBLE_STATUS_CODE", "AQABAC_FORTUNATE_FACIES",
        "AQABAC_MARKED_FACIES_QUALITY", "GLOBAL_FACIES_STATUS_CODE",
        "AQABBA_BENEFIC_RULER_FACIES", "LEARNED_ENTRY_PLUS_LOCAL_GRAPHIC_FIELD",
    }
    audit.check(len(adjudication) == len(candidate_map) == 7 and set(candidate_map) == expected_candidates, "seven exact candidate adjudications")
    mirror_candidate = candidate_map["F71_OUTER10_F9_MIRROR"]
    audit.check(
        mirror_candidate["confidence"] == "C0_RELATIVE_LAYOUT_ORDER_RIVAL" and mirror_candidate["decision"] == "RETAIN_C0_NOT_REUSABLE_KEY"
        and "descriptive" in mirror_candidate["evidence"] and "same-data" in mirror_candidate["counterevidence"]
        and "normalized ranks 203/400 and 264/400" in mirror_candidate["counterevidence"],
        "mirror is explicitly descriptive same-data texture, not decoder key",
    )
    audit.check(candidate_map["VISIBLE_STATUS_CODE"]["decision"] == "GENERAL_CODE_NOT_SELECTED", "general visual code not selected")
    audit.check(candidate_map["GLOBAL_FACIES_STATUS_CODE"]["decision"].startswith("NOT_SELECTED__PHASE_UNSTABLE"), "global facies architecture not selected")
    audit.check(
        candidate_map["AQABBA_BENEFIC_RULER_FACIES"]["confidence"] == "C0_TWO_EVENT_PICATRIX_PHASE_STABLE_RIVAL"
        and candidate_map["AQABBA_BENEFIC_RULER_FACIES"]["decision"] == "RETAIN_C0_FOR_INDEPENDENT_THIRD_EVENT_OR_HOST_TEST"
        and "only two events" in candidate_map["AQABBA_BENEFIC_RULER_FACIES"]["counterevidence"],
        "AQABBA remains bounded two-event C0",
    )
    audit.check(candidate_map["LEARNED_ENTRY_PLUS_LOCAL_GRAPHIC_FIELD"]["decision"] == "SELECTED_PRIMARY", "learned-entry/local-field architecture remains primary")
    audit.check(all(row["component_export_credit"] == "ZERO" and row["confirmed_lexeme"] == "NO" and row["evidence"] and row["counterevidence"] for row in adjudication), "adjudication exports zero components/lexemes")

    expected_scope = {
        "admitted_kluge_loci": 101, "new_pages_or_images_opened": 0, "guarded_visual_rows": 554,
        "varying_visual_state_rows": 174, "guarded_sign_rows": 5, "sealed_rows_materialized": 0,
        "mirror_outer_members": 10, "mirror_inner_members_used": 0,
    }
    expected_mirror = {
        "transform_rows": 3200, "boundary_best_transforms": "F9|R0",
        "boundary_raw_p": "0.003905296558", "boundary_fixed_mask_normalized_p": "0.034415425921",
        "boundary_split_half_raw_ranks": [122, 7], "boundary_split_half_normalized_ranks": [203, 264],
        "selected": "C0_F71_RELATIVE_REFLECTION_TEXTURE_NOT_REUSABLE_CODE",
    }
    expected_visual = {
        "channels": 3, "candidate_cards": 3, "status_cards_passing_gate": 0,
        "general_status_code": "NOT_SELECTED", "cards": [row["card_id"] for row in visual_cards],
    }
    picatrix_lofo_h0 = [row for row in lofo_rows if row["matrix_id"] == "PICATRIX_INDIAN" and row["taurus_phase"] == "H0"]
    picatrix_lofo_h1 = [row for row in lofo_rows if row["matrix_id"] == "PICATRIX_INDIAN" and row["taurus_phase"] == "H1"]
    expected_facies = {
        "historical_matrices": 2, "taurus_phases": 2, "global_transform_rows": 240,
        "picatrix_h0_selected_without_aqabac": f"D{picatrix_h0['selected_direction']}_O{picatrix_h0['selected_offset']}",
        "picatrix_h0_aqabac_status_counts": picatrix_h0["aqabac_status_counts"],
        "picatrix_h0_block_null_p": picatrix_h0["null_p_optimized_status_ge_observed"],
        "picatrix_h1_selected_without_aqabac": f"D{picatrix_h1['selected_direction']}_O{picatrix_h1['selected_offset']}",
        "picatrix_h1_aqabac_status_counts": picatrix_h1["aqabac_status_counts"],
        "picatrix_h1_block_null_p": picatrix_h1["null_p_optimized_status_ge_observed"],
        "picatrix_h0_lofo_consistent_status_families": sum(row["held_consistent_status"] == "YES" for row in picatrix_lofo_h0),
        "picatrix_h1_lofo_consistent_status_families": sum(row["held_consistent_status"] == "YES" for row in picatrix_lofo_h1),
        "picatrix_h0_h1_lofo_consistent_intersection": ["AQABBA"], "leave_one_sign_out_rows": 24,
        "picatrix_leave_one_sign_out_non_target_status_matches": 3,
        "picatrix_leave_one_sign_out_non_target_targets": 6,
        "picatrix_leave_one_sign_out_unambiguous_status_correct": 2,
        "picatrix_leave_one_sign_out_unambiguous_status_predictions": 5,
        "aqabac_fortunate_facies": "NOT_SELECTED__TARGET_MASKED_GLOBAL_PHASE_FAIL",
        "aqabac_marked_facies_quality": "RETAIN_C0_SEMANTICALLY_OPEN",
        "aqabba_benefic_ruler_facies": "RETAIN_C0_TWO_EVENTS_PISCES_GEMINI__NEEDS_INDEPENDENT_THIRD_EVENT_OR_HOST",
        "global_status_code": "NOT_SELECTED__PICATRIX_H1_TEXTURE_ONLY",
    }
    expected_decision = {
        "selected_primary_model": "LEARNED_ENTRY_PLUS_LOCAL_GRAPHIC_FIELD", "component_exports": 0,
        "confirmed_lexemes": 0,
        "next": "CONNECT_AQABBA_AND_THREE_VISUAL_RIVALS_TO_RUNNING_HOST_PARAGRAPHS_OR_TEST_INDEPENDENT_THIRD_EVENTS",
    }
    audit.check(result.get("experiment_id") == "GDT796" and result.get("status") == EXPECTED_STATUS, "result identity and exact status")
    audit.check(result.get("scope") == expected_scope, "result guarded scope")
    audit.check(result.get("mirror") == expected_mirror, "result mirror controls and ceiling")
    audit.check(result.get("visual") == expected_visual, "result visual controls and zero passing cards")
    audit.check(result.get("facies") == expected_facies, "result facies controls")
    audit.check(result.get("decision") == expected_decision, "result exact primary decision")
    audit.check(
        result["scope"]["new_pages_or_images_opened"] == result["scope"]["sealed_rows_materialized"] == result["scope"]["mirror_inner_members_used"] == 0
        and result["visual"]["status_cards_passing_gate"] == result["decision"]["component_exports"] == result["decision"]["confirmed_lexemes"] == 0,
        "global privacy and claim ceiling",
    )

    return write_validation(
        audit,
        builder_replays_completed=completed_replays,
        canonical_outputs_compared=len(OUTPUT_NAMES),
        builder_byte_replay=not any(item.startswith("byte replay") for item in audit.failures),
        replay_one_equals_replay_two=not any(item.startswith("byte equality replay") for item in audit.failures),
        guarded_query_stats=guard_stats,
        independent_mirror_transform_scores=3200,
        independent_facies_transform_scores=240,
        mirror_pairwise_fixed_mask_p={"f70_f71": f12(pairwise_p[0, 1]), "f71_f72": f12(pairwise_p[1, 2]), "f70_f72": f12(pairwise_p[0, 2])},
        leave_one_sign_out_training_capacity={"PISCES": 5, "TAURUS": 5, "GEMINI": 3},
        leave_one_sign_out_broad_held_capacity={"PISCES": 6, "TAURUS": 6, "GEMINI": 8},
        leave_one_sign_out_unambiguous_picatrix="2_OF_5",
        visual_status_cards_passing_gate=0,
        aqabba_claim="C0_TWO_EVENT_PICATRIX_RIVAL__NO_SIGN_HOLDOUT_CAPACITY__CHALDEAN_CONTRADICTED",
        claim_ceiling="ZERO_COMPONENT_EXPORT__ZERO_CONFIRMED_LEXEME__ZERO_VISUAL_STATUS_CARDS__NO_PROSE_EXPORT",
        new_pages_or_images_opened=0,
        sealed_rows_materialized=0,
    )


if __name__ == "__main__":
    raise SystemExit(main())
