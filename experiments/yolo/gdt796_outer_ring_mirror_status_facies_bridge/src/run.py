#!/usr/bin/env python3
"""Build GDT796: outer-ring mirror, visible status, and facies rivals."""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import random
import re
import subprocess
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Iterable, Sequence

sys.dont_write_bytecode = True


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
BASE = ROOT / "experiments/yolo/gdt796_outer_ring_mirror_status_facies_bridge"
SRC = BASE / "src"
DEFAULT_ARTIFACTS = BASE / "artifacts"
LOCK = SRC / "SOURCE_LOCK.tsv"
QUERY_SPECS = SRC / "GUARDED_QUERY_SPECS.tsv"
PHASE_SPECS = SRC / "PAGE_SIGN_PHASE_SPECS.tsv"
FACIES_MATRICES = SRC / "HISTORICAL_FACIES_MATRICES.tsv"
HISTORICAL_SOURCES = SRC / "HISTORICAL_SOURCE_REGISTRY.tsv"
GDT795_ATLAS = ROOT / "experiments/yolo/gdt795_source_native_family_kluge_transfer/artifacts/GDT795_101_KLUGE_SOURCE_FAMILY_ATLAS.tsv"
VISUAL_SOURCE = ROOT / "experiments/yolo/gdt360_existing_annotation_joint_grounding/artifacts/gdt360_annotation_inventory.tsv"
SIGN_SOURCE = ROOT / "experiments/semantic_assumptions/results/public_zodiac_nymph_overview.tsv"

sys.path.insert(0, str(SRC))
import mirror_analysis as mirror  # noqa: E402


VISUAL_QUERY_COLUMNS = (
    "case_id", "channel", "visual_state", "page", "physical_folio", "locus",
    "array_id", "provenance", "source_id", "confidence", "evidence_family",
    "evidence_lineage", "evidence_cluster", "visual_detail", "formal_coverage",
    "gdt327_coverage",
)
SIGN_QUERY_COLUMNS = (
    "sign", "page", "physical_folio", "NYMPHS", "CLOTHED_NYMPHS",
    "COLOR_CLOTHES", "CROWNED_NYMPHS", "MALE_NYMPHS", "STARS",
    "STAR_W__TETHER", "HOLDING_STAR", "HOLDING_TETHER", "CANS", "COLOR_CANS",
)
VISUAL_CHANNELS = ("ZODIAC_BARREL", "ZODIAC_CLOTHING", "ZODIAC_FACING")
VISUAL_REPRESENTATIONS = (
    ("BOUNDARY_FAMILY", "canonical_boundary_family"),
    ("COMPACT_FAMILY", "canonical_compact_family"),
    ("TRANSFERRED_PREFIX", "transferred_prefix"),
    ("FORMAL_RESIDUAL", "strict_residual"),
)
FACIES_PHASES = ("H0", "H1")
FACIES_DIRECTIONS = (1, -1)
FACIES_OFFSETS = tuple(range(30))
VISUAL_NULL_ITERATIONS = 1000
FACIES_NULL_ITERATIONS = 1000

MIRROR_OUTPUTS = (
    mirror.RANKING_NAME,
    mirror.NULL_NAME,
    mirror.SPLIT_NAME,
    mirror.CONTRIBUTION_NAME,
)
OUTPUT_NAMES = MIRROR_OUTPUTS + (
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


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(
    path: Path,
    rows: Iterable[dict[str, Any]],
    fields: Sequence[str] | None = None,
) -> None:
    materialized = list(rows)
    fieldnames = list(fields) if fields is not None else (list(materialized[0]) if materialized else [])
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=fieldnames,
            delimiter="\t",
            lineterminator="\n",
            extrasaction="raise",
        )
        writer.writeheader()
        for row in materialized:
            writer.writerow({field: row.get(field, "") for field in fieldnames})


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def verify_source_lock() -> None:
    rows = read_tsv(LOCK)
    if not rows or len(rows) != len({row["path"] for row in rows}):
        raise RuntimeError("source lock missing, empty, or duplicated")
    for row in rows:
        relative = Path(row["path"])
        if relative.is_absolute() or ".." in relative.parts:
            raise RuntimeError(f"invalid source-lock path: {row['path']}")
        path = ROOT / relative
        if not path.is_file() or sha256(path) != row["sha256"]:
            raise RuntimeError(f"source-lock mismatch: {row['path']}")


def f6(value: float) -> str:
    return f"{value:.6f}"


def joined(values: Iterable[Any]) -> str:
    materialized = [str(value) for value in values]
    return "|".join(materialized) if materialized else "NONE"


def run_guarded_query(
    source: Path,
    selector: str,
    allowed: Sequence[str],
    columns: Sequence[str],
    expected_stats: dict[str, int],
) -> list[dict[str, str]]:
    if any(value.startswith("f84") for value in allowed):
        raise RuntimeError("sealed selector entered guarded allow-list")
    command = [
        str(ROOT / "vmanus-exp"), "query-tsv", source.relative_to(ROOT).as_posix(),
        "--selector", selector,
    ]
    for value in allowed:
        command.extend(("--allow", value))
    command.extend(("--columns", ",".join(columns), "--forbid-prefix", "f84"))
    completed = subprocess.run(command, cwd=ROOT, text=True, capture_output=True, check=False)
    if completed.returncode:
        raise RuntimeError("guarded query failed: " + completed.stderr.strip())
    match = re.search(r"GUARD_STATS\s+(\{[^\n]+\})", completed.stderr)
    if not match:
        raise RuntimeError("guarded query omitted GUARD_STATS")
    stats = json.loads(match.group(1))
    if stats != expected_stats:
        raise RuntimeError(f"guarded query statistics changed: {stats} != {expected_stats}")
    rows = list(csv.DictReader(io.StringIO(completed.stdout), delimiter="\t"))
    if not rows or tuple(rows[0]) != tuple(columns):
        raise RuntimeError("guarded query schema changed")
    return rows


def guarded_sources(atlas: list[dict[str, str]]) -> tuple[list[dict[str, str]], list[dict[str, str]]]:
    specs = {row["query_id"]: row for row in read_tsv(QUERY_SPECS)}
    if set(specs) != {"K101_GDT360_VISUAL", "FIVE_PAGE_SIGN_MAP"}:
        raise RuntimeError("guarded query specification set changed")
    loci = sorted(row["locus"] for row in atlas)
    pages = ("f70v1", "f70v2", "f71v", "f72r1", "f72r2")
    visual_spec = specs["K101_GDT360_VISUAL"]
    sign_spec = specs["FIVE_PAGE_SIGN_MAP"]
    if visual_spec["path"] != VISUAL_SOURCE.relative_to(ROOT).as_posix() or visual_spec["selector"] != "locus":
        raise RuntimeError("visual guarded query path or selector changed")
    if tuple(visual_spec["columns"].split(",")) != VISUAL_QUERY_COLUMNS:
        raise RuntimeError("visual guarded query columns changed")
    if sign_spec["path"] != SIGN_SOURCE.relative_to(ROOT).as_posix() or sign_spec["selector"] != "page":
        raise RuntimeError("sign guarded query path or selector changed")
    if tuple(sign_spec["columns"].split(",")) != SIGN_QUERY_COLUMNS:
        raise RuntimeError("sign guarded query columns changed")
    visual = run_guarded_query(
        VISUAL_SOURCE, "locus", loci, VISUAL_QUERY_COLUMNS,
        {"selected": 554, "skipped_forbidden": 0, "skipped_not_allowed": 4053},
    )
    signs = run_guarded_query(
        SIGN_SOURCE, "page", pages, SIGN_QUERY_COLUMNS,
        {"selected": 5, "skipped_forbidden": 0, "skipped_not_allowed": 7},
    )
    return visual, signs


def mode_states(states: Sequence[str]) -> tuple[set[str], int]:
    counts = Counter(states)
    maximum = max(counts.values())
    return {state for state, count in counts.items() if count == maximum}, maximum


def prediction_metrics(
    records: list[dict[str, Any]],
    key_field: str,
    holdout_field: str,
) -> dict[str, float]:
    covered = 0
    key_credit = 0.0
    baseline_credit = 0.0
    for target_index, target in enumerate(records):
        training = [
            row for index, row in enumerate(records)
            if index != target_index and row[holdout_field] != target[holdout_field]
        ]
        keyed = [row for row in training if row[key_field] == target[key_field]]
        if not keyed:
            continue
        covered += 1
        key_modes, _ = mode_states([row["visual_state"] for row in keyed])
        baseline_modes, _ = mode_states([row["visual_state"] for row in training])
        if target["visual_state"] in key_modes:
            key_credit += 1.0 / len(key_modes)
        if target["visual_state"] in baseline_modes:
            baseline_credit += 1.0 / len(baseline_modes)
    return {
        "covered": covered,
        "key_credit": key_credit,
        "baseline_credit": baseline_credit,
        "key_accuracy": key_credit / covered if covered else 0.0,
        "baseline_accuracy": baseline_credit / covered if covered else 0.0,
        "gain": (key_credit - baseline_credit) / covered if covered else 0.0,
    }


def local_block_loo_metrics(records: list[dict[str, Any]], key_field: str) -> dict[str, float]:
    covered = 0
    credit = 0.0
    for target_index, target in enumerate(records):
        training = [
            row for index, row in enumerate(records)
            if index != target_index
            and row["visual_array_id"] == target["visual_array_id"]
            and row[key_field] == target[key_field]
        ]
        if not training:
            continue
        covered += 1
        modes, _ = mode_states([row["visual_state"] for row in training])
        if target["visual_state"] in modes:
            credit += 1.0 / len(modes)
    return {"covered": covered, "credit": credit, "accuracy": credit / covered if covered else 0.0}


def permuted_visual_records(records: list[dict[str, Any]], rng: random.Random) -> list[dict[str, Any]]:
    copied = [dict(row) for row in records]
    by_block: dict[str, list[int]] = defaultdict(list)
    for index, row in enumerate(copied):
        by_block[row["visual_array_id"]].append(index)
    for indices in by_block.values():
        states = [copied[index]["visual_state"] for index in indices]
        rng.shuffle(states)
        for index, state in zip(indices, states):
            copied[index]["visual_state"] = state
    return copied


def build_visual_outputs(
    atlas: list[dict[str, str]], visual_source_rows: list[dict[str, str]]
) -> tuple[
    list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]
]:
    atlas_by_locus = {row["locus"]: row for row in atlas}
    relevant = [row for row in visual_source_rows if row["channel"] in VISUAL_CHANNELS]
    if len(relevant) != 174 or len({(row["channel"], row["locus"]) for row in relevant}) != 174:
        raise RuntimeError("visual varying-channel capacity changed")
    expected = Counter({
        ("ZODIAC_BARREL", "PRESENT"): 55,
        ("ZODIAC_BARREL", "ABSENT"): 22,
        ("ZODIAC_CLOTHING", "DRESSED"): 11,
        ("ZODIAC_CLOTHING", "UNDRESSED"): 14,
        ("ZODIAC_CLOTHING", "UNCERTAIN"): 5,
        ("ZODIAC_FACING", "PROFILE"): 10,
        ("ZODIAC_FACING", "NON_DIRECTIONAL"): 57,
    })
    if Counter((row["channel"], row["visual_state"]) for row in relevant) != expected:
        raise RuntimeError("visual state census changed")

    block_states: dict[tuple[str, str], Counter[str]] = defaultdict(Counter)
    for row in relevant:
        block_states[row["channel"], row["array_id"]][row["visual_state"]] += 1
    joined_rows: list[dict[str, Any]] = []
    for ordinal, source in enumerate(sorted(relevant, key=lambda row: (row["channel"], row["page"], row["locus"])), start=1):
        if source["locus"] not in atlas_by_locus:
            raise RuntimeError("guarded visual row lacks GDT795 atlas locus")
        formal = atlas_by_locus[source["locus"]]
        counts = block_states[source["channel"], source["array_id"]]
        joined_rows.append({
            "visual_event_ordinal": ordinal,
            "channel": source["channel"],
            "visual_state": source["visual_state"],
            "locus": source["locus"],
            "physical_folio": source["physical_folio"],
            "source_selector": source["page"],
            "visual_array_id": source["array_id"],
            "atlas_array_id": formal["array_id"],
            "kluge_a_member": formal["kluge_a_member"],
            "complete_label_surface": formal["complete_label_surface"],
            "canonical_boundary_family": formal["canonical_boundary_family"],
            "canonical_compact_family": formal["canonical_compact_family"],
            "transferred_prefix": formal["transferred_prefix"],
            "strict_residual": formal["strict_residual"],
            "provenance": source["provenance"],
            "source_id": source["source_id"],
            "confidence": source["confidence"],
            "visual_detail": source["visual_detail"],
            "block_state_counts": joined(f"{state}:{count}" for state, count in sorted(counts.items())),
            "block_is_state_pure": "YES" if len(counts) == 1 else "NO",
            "semantic_ceiling": "EXISTING_VISUAL_STATE_CANDIDATE_ONLY",
        })

    transfer_rows: list[dict[str, Any]] = []
    for channel_index, channel in enumerate(VISUAL_CHANNELS):
        channel_rows = [row for row in joined_rows if row["channel"] == channel]
        channel_blocks = {(row["visual_array_id"], row["visual_state"]) for row in channel_rows}
        block_ids = {row["visual_array_id"] for row in channel_rows}
        pure_blocks = sum(
            len({row["visual_state"] for row in channel_rows if row["visual_array_id"] == block}) == 1
            for block in block_ids
        )
        for rep_index, (representation_id, field) in enumerate(VISUAL_REPRESENTATIONS):
            local = local_block_loo_metrics(channel_rows, field)
            lofo = prediction_metrics(channel_rows, field, "physical_folio")
            lopo = prediction_metrics(channel_rows, field, "source_selector")
            rng = random.Random(796100 + channel_index * 10 + rep_index)
            null_gains = []
            for _ in range(VISUAL_NULL_ITERATIONS):
                permuted = permuted_visual_records(channel_rows, rng)
                null_gains.append(prediction_metrics(permuted, field, "physical_folio")["gain"])
            p_value = (1 + sum(value >= lofo["gain"] - 1e-12 for value in null_gains)) / (VISUAL_NULL_ITERATIONS + 1)
            transfer_rows.append({
                "channel": channel,
                "representation_id": representation_id,
                "source_field": field,
                "event_count": len(channel_rows),
                "state_count": len({row["visual_state"] for row in channel_rows}),
                "states": joined(sorted({row["visual_state"] for row in channel_rows})),
                "visual_block_count": len(block_ids),
                "state_pure_block_count": pure_blocks,
                "block_state_pair_count": len(channel_blocks),
                "local_block_loo_covered": int(local["covered"]),
                "local_block_loo_credit": f6(local["credit"]),
                "local_block_loo_accuracy": f6(local["accuracy"]),
                "held_physical_folio_covered": int(lofo["covered"]),
                "held_physical_folio_key_credit": f6(lofo["key_credit"]),
                "held_physical_folio_key_accuracy": f6(lofo["key_accuracy"]),
                "held_physical_folio_baseline_credit": f6(lofo["baseline_credit"]),
                "held_physical_folio_baseline_accuracy": f6(lofo["baseline_accuracy"]),
                "held_physical_folio_gain": f6(lofo["gain"]),
                "held_source_page_covered": int(lopo["covered"]),
                "held_source_page_key_credit": f6(lopo["key_credit"]),
                "held_source_page_key_accuracy": f6(lopo["key_accuracy"]),
                "visual_null_iterations": VISUAL_NULL_ITERATIONS,
                "visual_null_mean_gain": f6(sum(null_gains) / len(null_gains)),
                "visual_null_p_gain_ge_observed": f6(p_value),
                "decision": "BLOCK_CONFOUNDED_OR_NO_GENERAL_STATUS_TRANSFER",
                "semantic_export": "NONE",
            })

    recurrent_family_rows: list[dict[str, Any]] = []
    for channel in VISUAL_CHANNELS:
        channel_rows = [row for row in joined_rows if row["channel"] == channel]
        by_family: dict[str, list[dict[str, Any]]] = defaultdict(list)
        for row in channel_rows:
            by_family[row["canonical_boundary_family"]].append(row)
        for family, rows in sorted(by_family.items()):
            if len(rows) < 2:
                continue
            states = Counter(row["visual_state"] for row in rows)
            recurrent_family_rows.append({
                "channel": channel,
                "canonical_boundary_family": family,
                "event_count": len(rows),
                "state_counts": joined(f"{state}:{count}" for state, count in sorted(states.items())),
                "state_purity": f6(max(states.values()) / len(rows)),
                "physical_folio_count": len({row["physical_folio"] for row in rows}),
                "physical_folios": joined(sorted({row["physical_folio"] for row in rows})),
                "source_page_count": len({row["source_selector"] for row in rows}),
                "source_pages": joined(sorted({row["source_selector"] for row in rows})),
                "visual_block_count": len({row["visual_array_id"] for row in rows}),
                "all_supporting_blocks_state_pure": "YES" if all(row["block_is_state_pure"] == "YES" for row in rows) else "NO",
                "loci": joined(row["locus"] for row in rows),
                "surfaces": joined(row["complete_label_surface"] for row in rows),
                "candidate_ceiling": "COMPLETE_FAMILY_VISUAL_STATUS_RIVAL_ONLY",
                "component_export_credit": "ZERO",
            })

    card_specs = (
        ("BARREL_AQABAG", "ZODIAC_BARREL", "AQABAG", "mit Fass/Behälter dargestellte Figur"),
        ("CLOTHING_AQKA_ACA", "ZODIAC_CLOTHING", "AQKA|ACA", "unbekleidete Figur"),
        ("FACING_AQACAB", "ZODIAC_FACING", "AQACAB", "Profilfigur"),
    )
    cards: list[dict[str, Any]] = []
    for card_id, channel, family, display in card_specs:
        rows = [row for row in joined_rows if row["channel"] == channel and row["canonical_boundary_family"] == family]
        states = Counter(row["visual_state"] for row in rows)
        cards.append({
            "card_id": card_id,
            "channel": channel,
            "canonical_boundary_family": family,
            "working_default_de": display,
            "confidence": "EXPLORATORY_RIVAL_BELOW_GDT796_GATE",
            "event_count": len(rows),
            "state_counts": joined(f"{state}:{count}" for state, count in sorted(states.items())),
            "physical_folio_count": len({row["physical_folio"] for row in rows}),
            "source_page_count": len({row["source_selector"] for row in rows}),
            "visual_block_count": len({row["visual_array_id"] for row in rows}),
            "loci": joined(row["locus"] for row in rows),
            "surfaces": joined(row["complete_label_surface"] for row in rows),
            "evidence": (
                "three AQABAG events are PRESENT on three source pages/two physical folios"
                if card_id == "BARREL_AQABAG"
                else "two complete-family events share the proposed visible state"
            ),
            "counterevidence": (
                "every supporting event lies in a barrel-PRESENT-only page×ring block; AQABAB and AQABAC cross barrel states"
                if card_id == "BARREL_AQABAG"
                else "both events lie on one physical folio" if card_id == "CLOTHING_AQKA_ACA"
                else "both events lie in the sole PROFILE block and descend from hedged source assertions"
            ),
            "renderer_license": "NONE__CANDIDATE_DECK_ONLY",
            "prose_export_allowed": "NO",
            "component_export_credit": "ZERO",
            "confirmed_lexeme": "NO",
        })
    return joined_rows, transfer_rows, recurrent_family_rows, cards


def canonical_sign(value: str) -> str:
    return value.strip().split()[0].upper()


def load_facies_contract(sign_rows: list[dict[str, str]]) -> tuple[
    dict[str, dict[str, Any]], dict[tuple[str, str, int], dict[str, str]]
]:
    phase_rows = read_tsv(PHASE_SPECS)
    if len(phase_rows) != 5 or len({row["source_selector"] for row in phase_rows}) != 5:
        raise RuntimeError("page/sign phase specification changed")
    public = {row["page"]: (canonical_sign(row["sign"]), row["physical_folio"]) for row in sign_rows}
    phases: dict[str, dict[str, Any]] = {}
    for row in phase_rows:
        page = row["source_selector"]
        expected_sign = row["sign"]
        if page not in public or public[page] != (expected_sign, row["physical_folio"]):
            raise RuntimeError(f"public sign mapping changed at {page}: {public.get(page)}")
        phases[page] = {
            **row,
            "h0_base_add": int(row["h0_base_add"]),
            "h1_base_add": int(row["h1_base_add"]),
        }
    matrix_rows = read_tsv(FACIES_MATRICES)
    if len(matrix_rows) != 72:
        raise RuntimeError("expected two complete 12x3 facies matrices")
    matrices: dict[tuple[str, str, int], dict[str, str]] = {}
    for row in matrix_rows:
        key = (row["matrix_id"], row["sign"], int(row["facies_index"]))
        if key in matrices:
            raise RuntimeError(f"duplicate facies matrix cell {key}")
        if int(row["degree_start"]) != (int(row["facies_index"]) - 1) * 10 + 1:
            raise RuntimeError(f"facies degree start changed at {key}")
        if int(row["degree_end"]) != int(row["facies_index"]) * 10:
            raise RuntimeError(f"facies degree end changed at {key}")
        matrices[key] = row
    if {key[0] for key in matrices} != {"PICATRIX_INDIAN", "CHALDEAN"}:
        raise RuntimeError("historical matrix identifiers changed")
    if len(read_tsv(HISTORICAL_SOURCES)) != 6:
        raise RuntimeError("historical source registry changed")
    return phases, matrices


def mapped_facies_event(
    row: dict[str, Any],
    phase: str,
    matrix_id: str,
    direction: int,
    offset: int,
    phases: dict[str, dict[str, Any]],
    matrices: dict[tuple[str, str, int], dict[str, str]],
) -> dict[str, Any]:
    spec = phases[row["source_selector"]]
    add = int(spec["h0_base_add"] if phase == "H0" else spec["h1_base_add"])
    base_position = ((int(row["kluge_a_member"]) - 1 + add) % 30) + 1
    transformed = ((offset + direction * (base_position - 1)) % 30) + 1
    facies_index = ((transformed - 1) // 10) + 1
    cell = matrices[matrix_id, spec["sign"], facies_index]
    return {
        **row,
        "sign": spec["sign"],
        "base_position": base_position,
        "transformed_degree": transformed,
        "facies_index": facies_index,
        "planet": cell["planet"],
        "coarse_status": cell["coarse_status"],
    }


def facies_family_groups(events: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    all_counts = Counter(row["canonical_boundary_family"] for row in events)
    groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in events:
        family = row["canonical_boundary_family"]
        if all_counts[family] >= 2:
            groups[family].append(row)
    return {
        family: rows for family, rows in groups.items()
        if len({row["sign"] for row in rows}) >= 2
    }


def purity(values: Sequence[str]) -> tuple[float, str, str]:
    counts = Counter(values)
    maximum = max(counts.values())
    modes = sorted(value for value, count in counts.items() if count == maximum)
    return maximum / len(values), joined(modes), joined(f"{value}:{count}" for value, count in sorted(counts.items()))


def facies_score(mapped: list[dict[str, Any]], excluded: set[str] | None = None) -> dict[str, Any]:
    excluded = excluded or set()
    groups = {family: rows for family, rows in facies_family_groups(mapped).items() if family not in excluded}
    if not groups:
        return {
            "family_count": 0, "status_purity": 0.0, "planet_purity": 0.0,
            "consistent_status": 0, "consistent_planet": 0,
        }
    status_purities = []
    planet_purities = []
    consistent_status = 0
    consistent_planet = 0
    for rows in groups.values():
        status_value = purity([row["coarse_status"] for row in rows])[0]
        planet_value = purity([row["planet"] for row in rows])[0]
        status_purities.append(status_value)
        planet_purities.append(planet_value)
        consistent_status += status_value == 1.0
        consistent_planet += planet_value == 1.0
    return {
        "family_count": len(groups),
        "status_purity": sum(status_purities) / len(status_purities),
        "planet_purity": sum(planet_purities) / len(planet_purities),
        "consistent_status": consistent_status,
        "consistent_planet": consistent_planet,
    }


def select_facies_transform(
    base_events: list[dict[str, Any]],
    phase: str,
    matrix_id: str,
    phases: dict[str, dict[str, Any]],
    matrices: dict[tuple[str, str, int], dict[str, str]],
    excluded: set[str] | None = None,
) -> tuple[int, int, dict[str, Any], list[dict[str, Any]]]:
    candidates = []
    for direction in FACIES_DIRECTIONS:
        for offset in FACIES_OFFSETS:
            mapped = [mapped_facies_event(row, phase, matrix_id, direction, offset, phases, matrices) for row in base_events]
            score = facies_score(mapped, excluded)
            candidates.append((direction, offset, score, mapped))
    return max(
        candidates,
        key=lambda item: (
            item[2]["status_purity"], item[2]["planet_purity"],
            item[2]["consistent_status"], item[2]["consistent_planet"],
            item[0] == 1, -item[1],
        ),
    )


def rotate_families_within_arrays(events: list[dict[str, Any]], rng: random.Random) -> list[dict[str, Any]]:
    copied = [dict(row) for row in events]
    by_array: dict[str, list[int]] = defaultdict(list)
    for index, row in enumerate(copied):
        by_array[row["array_id"]].append(index)
    for indices in by_array.values():
        ordered = sorted(indices, key=lambda index: int(copied[index]["slot_index"]))
        values = [copied[index]["canonical_boundary_family"] for index in ordered]
        if rng.randrange(2):
            values.reverse()
        shift = rng.randrange(len(values))
        values = values[shift:] + values[:shift]
        for index, value in zip(ordered, values):
            copied[index]["canonical_boundary_family"] = value
    return copied


def build_facies_outputs(
    atlas: list[dict[str, str]],
    sign_rows: list[dict[str, str]],
) -> tuple[
    list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]],
    list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]
]:
    phases, matrices = load_facies_contract(sign_rows)
    primary_pages = {page for page, spec in phases.items() if spec["primary_matrix_use"] == "YES"}
    base_events: list[dict[str, Any]] = [dict(row) for row in atlas if row["source_selector"] in primary_pages]
    for row in base_events:
        row["sign"] = phases[row["source_selector"]]["sign"]
    if len(base_events) != 87 or Counter(row["sign"] for row in base_events) != Counter({"TAURUS": 29, "PISCES": 29, "GEMINI": 29}):
        raise RuntimeError("primary facies panel changed")

    transform_rows: list[dict[str, Any]] = []
    mapped_cache: dict[tuple[str, str, int, int], list[dict[str, Any]]] = {}
    for matrix_id in ("PICATRIX_INDIAN", "CHALDEAN"):
        for phase in FACIES_PHASES:
            for direction in FACIES_DIRECTIONS:
                for offset in FACIES_OFFSETS:
                    mapped = [mapped_facies_event(row, phase, matrix_id, direction, offset, phases, matrices) for row in base_events]
                    mapped_cache[matrix_id, phase, direction, offset] = mapped
                    score_all = facies_score(mapped)
                    score_without_target = facies_score(mapped, {"AQABAC"})
                    aqabac = [row for row in mapped if row["canonical_boundary_family"] == "AQABAC"]
                    aq_status = purity([row["coarse_status"] for row in aqabac]) if aqabac else (0.0, "NONE", "NONE")
                    aq_planet = purity([row["planet"] for row in aqabac]) if aqabac else (0.0, "NONE", "NONE")
                    transform_rows.append({
                        "matrix_id": matrix_id,
                        "taurus_phase": phase,
                        "direction": direction,
                        "offset": offset,
                        "cross_sign_recurrent_family_count": score_all["family_count"],
                        "family_balanced_status_purity": f6(score_all["status_purity"]),
                        "family_balanced_planet_purity": f6(score_all["planet_purity"]),
                        "consistent_status_family_count": score_all["consistent_status"],
                        "consistent_planet_family_count": score_all["consistent_planet"],
                        "training_without_aqabac_family_count": score_without_target["family_count"],
                        "training_without_aqabac_status_purity": f6(score_without_target["status_purity"]),
                        "training_without_aqabac_planet_purity": f6(score_without_target["planet_purity"]),
                        "training_without_aqabac_consistent_status_count": score_without_target["consistent_status"],
                        "aqabac_event_count": len(aqabac),
                        "aqabac_status_purity": f6(aq_status[0]),
                        "aqabac_status_modes": aq_status[1],
                        "aqabac_status_counts": aq_status[2],
                        "aqabac_planet_purity": f6(aq_planet[0]),
                        "aqabac_planet_modes": aq_planet[1],
                        "aqabac_planet_counts": aq_planet[2],
                        "aqabac_all_benefic": "YES" if aqabac and all(row["coarse_status"] == "BENEFIC" for row in aqabac) else "NO",
                        "semantic_export": "NONE",
                    })

    selected_rows: list[dict[str, Any]] = []
    selected_by_model: dict[tuple[str, str], tuple[int, int, list[dict[str, Any]]]] = {}
    for model_index, matrix_id in enumerate(("PICATRIX_INDIAN", "CHALDEAN")):
        for phase_index, phase in enumerate(FACIES_PHASES):
            direction, offset, score, mapped = select_facies_transform(
                base_events, phase, matrix_id, phases, matrices, {"AQABAC"}
            )
            selected_by_model[matrix_id, phase] = (direction, offset, mapped)
            target = [row for row in mapped if row["canonical_boundary_family"] == "AQABAC"]
            target_status = purity([row["coarse_status"] for row in target])
            target_planet = purity([row["planet"] for row in target])
            rng = random.Random(796200 + model_index * 10 + phase_index)
            null_best_scores: list[float] = []
            for _ in range(FACIES_NULL_ITERATIONS):
                permuted = rotate_families_within_arrays(base_events, rng)
                _, _, null_score, _ = select_facies_transform(
                    permuted, phase, matrix_id, phases, matrices, {"AQABAC"}
                )
                null_best_scores.append(float(null_score["status_purity"]))
            p_value = (1 + sum(value >= float(score["status_purity"]) - 1e-12 for value in null_best_scores)) / (FACIES_NULL_ITERATIONS + 1)
            relevant_transforms = [row for row in transform_rows if row["matrix_id"] == matrix_id and row["taurus_phase"] == phase]
            selected_rows.append({
                "matrix_id": matrix_id,
                "taurus_phase": phase,
                "selected_without_family": "AQABAC",
                "selected_direction": direction,
                "selected_offset": offset,
                "training_family_count": score["family_count"],
                "training_family_balanced_status_purity": f6(score["status_purity"]),
                "training_family_balanced_planet_purity": f6(score["planet_purity"]),
                "training_consistent_status_family_count": score["consistent_status"],
                "training_consistent_planet_family_count": score["consistent_planet"],
                "aqabac_event_count": len(target),
                "aqabac_status_purity": f6(target_status[0]),
                "aqabac_status_modes": target_status[1],
                "aqabac_status_counts": target_status[2],
                "aqabac_planet_purity": f6(target_planet[0]),
                "aqabac_planet_modes": target_planet[1],
                "aqabac_planet_counts": target_planet[2],
                "aqabac_all_benefic": "YES" if all(row["coarse_status"] == "BENEFIC" for row in target) else "NO",
                "aqabac_uniform_status_transform_count": sum(float(row["aqabac_status_purity"]) == 1.0 for row in relevant_transforms),
                "aqabac_all_benefic_transform_count": sum(row["aqabac_all_benefic"] == "YES" for row in relevant_transforms),
                "aqabac_uniform_planet_transform_count": sum(float(row["aqabac_planet_purity"]) == 1.0 for row in relevant_transforms),
                "null_iterations": FACIES_NULL_ITERATIONS,
                "null_mean_optimized_training_status_purity": f6(sum(null_best_scores) / len(null_best_scores)),
                "null_p_optimized_status_ge_observed": f6(p_value),
                "decision": "NO_GLOBAL_FACIES_STATUS_CODE__AQABAC_HELD_FAIL" if target_status[0] < 1.0 else "GLOBAL_MODEL_STILL_REQUIRES_HELD_FAMILY_AND_PHASE_STABILITY",
                "semantic_export": "NONE",
            })

    lofo_rows: list[dict[str, Any]] = []
    for matrix_id in ("PICATRIX_INDIAN", "CHALDEAN"):
        for phase in FACIES_PHASES:
            reference = mapped_cache[matrix_id, phase, 1, 0]
            held_families = sorted(facies_family_groups(reference))
            for family in held_families:
                direction, offset, score, mapped = select_facies_transform(
                    base_events, phase, matrix_id, phases, matrices, {family}
                )
                held = [row for row in mapped if row["canonical_boundary_family"] == family]
                status_value = purity([row["coarse_status"] for row in held])
                planet_value = purity([row["planet"] for row in held])
                lofo_rows.append({
                    "matrix_id": matrix_id,
                    "taurus_phase": phase,
                    "held_family": family,
                    "held_event_count": len(held),
                    "held_sign_count": len({row["sign"] for row in held}),
                    "held_signs": joined(sorted({row["sign"] for row in held})),
                    "selected_direction": direction,
                    "selected_offset": offset,
                    "training_family_count": score["family_count"],
                    "training_status_purity": f6(score["status_purity"]),
                    "held_status_purity": f6(status_value[0]),
                    "held_status_modes": status_value[1],
                    "held_status_counts": status_value[2],
                    "held_planet_purity": f6(planet_value[0]),
                    "held_planet_modes": planet_value[1],
                    "held_planet_counts": planet_value[2],
                    "held_all_benefic": "YES" if all(row["coarse_status"] == "BENEFIC" for row in held) else "NO",
                    "held_consistent_status": "YES" if status_value[0] == 1.0 else "NO",
                    "held_consistent_planet": "YES" if planet_value[0] == 1.0 else "NO",
                    "semantic_export": "NONE",
                })

    sign_out_rows: list[dict[str, Any]] = []
    for matrix_id in ("PICATRIX_INDIAN", "CHALDEAN"):
        for phase in FACIES_PHASES:
            for held_sign in ("PISCES", "TAURUS", "GEMINI"):
                training_events = [row for row in base_events if row["sign"] != held_sign]
                held_events = [row for row in base_events if row["sign"] == held_sign]
                family_signs: dict[str, set[str]] = defaultdict(set)
                for row in base_events:
                    family_signs[row["canonical_boundary_family"]].add(row["sign"])
                broad_held_capacity = sorted(
                    family for family, signs in family_signs.items()
                    if held_sign in signs and bool(signs - {held_sign})
                )
                direction, offset, target_masked_score, training_mapped = select_facies_transform(
                    training_events, phase, matrix_id, phases, matrices, {"AQABAC"}
                )
                held_mapped = [
                    mapped_facies_event(row, phase, matrix_id, direction, offset, phases, matrices)
                    for row in held_events
                ]
                training_groups = facies_family_groups(training_mapped)
                capacity_all = len(training_groups)
                capacity_without_target = len([family for family in training_groups if family != "AQABAC"])
                held_by_family: dict[str, list[dict[str, Any]]] = defaultdict(list)
                for row in held_mapped:
                    held_by_family[row["canonical_boundary_family"]].append(row)
                eligible = sorted(set(training_groups) & set(held_by_family))
                for family in eligible:
                    training_family = training_groups[family]
                    held_family = held_by_family[family]
                    training_status = purity([row["coarse_status"] for row in training_family])
                    held_status = purity([row["coarse_status"] for row in held_family])
                    training_planet = purity([row["planet"] for row in training_family])
                    held_planet = purity([row["planet"] for row in held_family])
                    training_status_modes = set(training_status[1].split("|"))
                    training_planet_modes = set(training_planet[1].split("|"))
                    held_status_values = {row["coarse_status"] for row in held_family}
                    held_planet_values = {row["planet"] for row in held_family}
                    status_match = held_status_values <= training_status_modes
                    planet_match = held_planet_values <= training_planet_modes
                    sign_out_rows.append({
                        "matrix_id": matrix_id,
                        "taurus_phase": phase,
                        "held_sign": held_sign,
                        "training_signs": joined(sorted({row["sign"] for row in training_events})),
                        "selected_direction_without_aqabac": direction,
                        "selected_offset_without_aqabac": offset,
                        "training_cross_sign_family_capacity_all": capacity_all,
                        "training_family_count_without_aqabac": target_masked_score["family_count"],
                        "held_any_training_family_capacity_all": len(broad_held_capacity),
                        "held_any_training_family_capacity_without_aqabac": len([value for value in broad_held_capacity if value != "AQABAC"]),
                        "eligible_held_family_count_all": len(eligible),
                        "eligible_held_family_count_without_aqabac": len([value for value in eligible if value != "AQABAC"]),
                        "held_family": family,
                        "aqabac_target_diagnostic": "YES" if family == "AQABAC" else "NO",
                        "training_event_count": len(training_family),
                        "held_event_count": len(held_family),
                        "training_status_purity": f6(training_status[0]),
                        "training_status_modes": training_status[1],
                        "training_status_counts": training_status[2],
                        "held_status_purity": f6(held_status[0]),
                        "held_status_modes": held_status[1],
                        "held_status_counts": held_status[2],
                        "held_status_matches_training_mode": "YES" if status_match else "NO",
                        "training_status_unambiguous": "YES" if training_status[0] == 1.0 else "NO",
                        "held_status_prediction_correct": (
                            "NA_TARGET" if family == "AQABAC" else
                            "NA_TIED_TRAINING" if training_status[0] < 1.0 else
                            "YES" if status_match else "NO"
                        ),
                        "training_planet_purity": f6(training_planet[0]),
                        "training_planet_modes": training_planet[1],
                        "training_planet_counts": training_planet[2],
                        "held_planet_purity": f6(held_planet[0]),
                        "held_planet_modes": held_planet[1],
                        "held_planet_counts": held_planet[2],
                        "held_planet_matches_training_mode": "YES" if planet_match else "NO",
                        "training_planet_unambiguous": "YES" if training_planet[0] == 1.0 else "NO",
                        "held_planet_prediction_correct": (
                            "NA_TARGET" if family == "AQABAC" else
                            "NA_TIED_TRAINING" if training_planet[0] < 1.0 else
                            "YES" if planet_match else "NO"
                        ),
                        "decision": (
                            "TARGET_DIAGNOSTIC_ONLY" if family == "AQABAC"
                            else "HELD_STATUS_MATCH" if status_match else "HELD_STATUS_MISS"
                        ),
                        "semantic_export": "NONE",
                    })
                if capacity_all != {"PISCES": 5, "TAURUS": 5, "GEMINI": 3}[held_sign]:
                    raise RuntimeError(f"leave-one-sign-out training capacity changed at {matrix_id}/{phase}/{held_sign}")
                if len(broad_held_capacity) != {"PISCES": 6, "TAURUS": 6, "GEMINI": 8}[held_sign]:
                    raise RuntimeError(f"leave-one-sign-out broad held capacity changed at {matrix_id}/{phase}/{held_sign}")
                if len(eligible) != 2 or capacity_without_target != target_masked_score["family_count"]:
                    raise RuntimeError(f"leave-one-sign-out eligible capacity changed at {matrix_id}/{phase}/{held_sign}")
    if len(sign_out_rows) != 24:
        raise RuntimeError(f"leave-one-sign-out row count changed: {len(sign_out_rows)}")

    target_rows: list[dict[str, Any]] = []
    for matrix_id in ("PICATRIX_INDIAN", "CHALDEAN"):
        for phase in FACIES_PHASES:
            selected_direction, selected_offset, _ = selected_by_model[matrix_id, phase]
            for evaluation_id, direction, offset in (
                ("NOMINAL_R0", 1, 0),
                ("SELECTED_WITHOUT_AQABAC", selected_direction, selected_offset),
            ):
                mapped = mapped_cache[matrix_id, phase, direction, offset]
                for row in mapped:
                    if row["canonical_boundary_family"] != "AQABAC":
                        continue
                    target_rows.append({
                        "matrix_id": matrix_id,
                        "taurus_phase": phase,
                        "evaluation_id": evaluation_id,
                        "direction": direction,
                        "offset": offset,
                        "locus": row["locus"],
                        "source_selector": row["source_selector"],
                        "sign": row["sign"],
                        "kluge_a_member": row["kluge_a_member"],
                        "base_position": row["base_position"],
                        "transformed_degree": row["transformed_degree"],
                        "facies_index": row["facies_index"],
                        "planet": row["planet"],
                        "coarse_status": row["coarse_status"],
                        "working_rival_de": "günstige/benefische Facies" if row["coarse_status"] == "BENEFIC" else "markierte Faciesqualität; Polarität offen",
                        "confidence": "C0_HISTORICAL_MATRIX_RIVAL",
                        "component_export_credit": "ZERO",
                    })

    census_rows: list[dict[str, Any]] = []
    for matrix_id in ("PICATRIX_INDIAN", "CHALDEAN"):
        for phase in FACIES_PHASES:
            direction, offset, mapped = selected_by_model[matrix_id, phase]
            for family, rows in sorted(facies_family_groups(mapped).items()):
                status_value = purity([row["coarse_status"] for row in rows])
                planet_value = purity([row["planet"] for row in rows])
                census_rows.append({
                    "matrix_id": matrix_id,
                    "taurus_phase": phase,
                    "selected_direction_without_aqabac": direction,
                    "selected_offset_without_aqabac": offset,
                    "canonical_boundary_family": family,
                    "event_count": len(rows),
                    "sign_count": len({row["sign"] for row in rows}),
                    "signs": joined(sorted({row["sign"] for row in rows})),
                    "status_counts": status_value[2],
                    "status_purity": f6(status_value[0]),
                    "status_modes": status_value[1],
                    "planet_counts": planet_value[2],
                    "planet_purity": f6(planet_value[0]),
                    "planet_modes": planet_value[1],
                    "fixed_status_candidate": "YES" if status_value[0] == 1.0 else "NO",
                    "fixed_planet_candidate": "YES" if planet_value[0] == 1.0 else "NO",
                    "semantic_export": "NONE",
                })
    return transform_rows, selected_rows, lofo_rows, sign_out_rows, target_rows, census_rows


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_ARTIFACTS)
    args = parser.parse_args()
    out = args.output_dir.resolve()
    out.mkdir(parents=True, exist_ok=True)
    verify_source_lock()

    atlas = read_tsv(GDT795_ATLAS)
    if len(atlas) != 101 or len({row["locus"] for row in atlas}) != 101:
        raise RuntimeError("GDT795 atlas capacity changed")
    visual_source_rows, sign_rows = guarded_sources(atlas)
    mirror_counts = mirror.run_analysis(out)
    if mirror_counts != {
        mirror.RANKING_NAME: 3200,
        mirror.NULL_NAME: 16,
        mirror.SPLIT_NAME: 16,
        mirror.CONTRIBUTION_NAME: 10,
    }:
        raise RuntimeError(f"mirror output capacity changed: {mirror_counts}")

    visual_atlas, visual_summary, visual_census, visual_cards = build_visual_outputs(atlas, visual_source_rows)
    write_tsv(out / OUTPUT_NAMES[4], visual_atlas)
    write_tsv(out / OUTPUT_NAMES[5], visual_summary)
    write_tsv(out / OUTPUT_NAMES[6], visual_census)
    write_tsv(out / OUTPUT_NAMES[7], visual_cards)

    facies_transforms, facies_selected, facies_lofo, facies_sign_out, aqabac_rows, historical_census = build_facies_outputs(atlas, sign_rows)
    write_tsv(out / OUTPUT_NAMES[8], facies_transforms)
    write_tsv(out / OUTPUT_NAMES[9], facies_selected)
    write_tsv(out / OUTPUT_NAMES[10], facies_lofo)
    write_tsv(out / OUTPUT_NAMES[11], facies_sign_out)
    write_tsv(out / OUTPUT_NAMES[12], aqabac_rows)
    write_tsv(out / OUTPUT_NAMES[13], historical_census)

    mirror_null = read_tsv(out / mirror.NULL_NAME)
    boundary_raw = next(row for row in mirror_null if row["view_id"] == "BOUNDARY_NED" and row["null_id"] == "INCLUSIVE_NA_RAW_SUM")
    boundary_fixed = next(row for row in mirror_null if row["view_id"] == "BOUNDARY_NED" and row["null_id"] == "FIXED_MASK_COMPARABLE_NORMALIZED")
    mirror_splits = read_tsv(out / mirror.SPLIT_NAME)
    boundary_splits = [row for row in mirror_splits if row["view_id"] == "BOUNDARY_NED"]
    mirror_split_ranks = [int(row["raw_test_rank"]) for row in boundary_splits]
    mirror_normalized_split_ranks = [int(row["comparable_normalized_test_rank"]) for row in boundary_splits]
    primary_facies = next(row for row in facies_selected if row["matrix_id"] == "PICATRIX_INDIAN" and row["taurus_phase"] == "H0")
    alternate_facies = next(row for row in facies_selected if row["matrix_id"] == "PICATRIX_INDIAN" and row["taurus_phase"] == "H1")
    picatrix_lofo_h0 = [row for row in facies_lofo if row["matrix_id"] == "PICATRIX_INDIAN" and row["taurus_phase"] == "H0"]
    picatrix_lofo_h1 = [row for row in facies_lofo if row["matrix_id"] == "PICATRIX_INDIAN" and row["taurus_phase"] == "H1"]
    aqabba_h0 = next(row for row in picatrix_lofo_h0 if row["held_family"] == "AQABBA")
    aqabba_h1 = next(row for row in picatrix_lofo_h1 if row["held_family"] == "AQABBA")
    picatrix_h0_consistent = {
        row["held_family"] for row in picatrix_lofo_h0 if row["held_consistent_status"] == "YES"
    }
    picatrix_h1_consistent = {
        row["held_family"] for row in picatrix_lofo_h1 if row["held_consistent_status"] == "YES"
    }
    picatrix_phase_stable = sorted(picatrix_h0_consistent & picatrix_h1_consistent)
    if picatrix_phase_stable != ["AQABBA"]:
        raise RuntimeError(f"Picatrix phase-stable LOFO family set changed: {picatrix_phase_stable}")

    picatrix_sign_out = [
        row for row in facies_sign_out
        if row["matrix_id"] == "PICATRIX_INDIAN" and row["aqabac_target_diagnostic"] == "NO"
    ]
    decisions = [
        {
            "candidate_id": "F71_OUTER10_F9_MIRROR",
            "working_interpretation": "f71 outer-ten has a relative reflection texture against f70/f72",
            "confidence": "C0_RELATIVE_LAYOUT_ORDER_RIVAL",
            "decision": "RETAIN_C0_NOT_REUSABLE_KEY",
            "evidence": f"descriptive full-sample boundary F9/R0 raw p={boundary_raw['add_one_p']}; fixed-mask normalized p={boundary_fixed['add_one_p']}",
            "counterevidence": (
                f"raw split-half ranks {mirror_split_ranks[0]}/400 and {mirror_split_ranks[1]}/400; "
                f"normalized ranks {mirror_normalized_split_ranks[0]}/400 and {mirror_normalized_split_ranks[1]}/400; "
                "F9 was an earlier same-data rival and exact member identity is zero"
            ),
            "component_export_credit": "ZERO",
            "confirmed_lexeme": "NO",
        },
        {
            "candidate_id": "VISIBLE_STATUS_CODE",
            "working_interpretation": "one family/prefix/residual field names barrel, clothing or facing state",
            "confidence": "THREE_EXPLORATORY_RIVALS_BELOW_GATE",
            "decision": "GENERAL_CODE_NOT_SELECTED",
            "evidence": "three complete-family candidate cards retain repeated visible states for future contradiction or confirmation",
            "counterevidence": "barrel and facing are page×ring-pure blocks; clothing transfers poorly across folios/pages",
            "component_export_credit": "ZERO",
            "confirmed_lexeme": "NO",
        },
        {
            "candidate_id": "AQABAC_FORTUNATE_FACIES",
            "working_interpretation": "AQABAC = facies fortunata / favorable treatment window",
            "confidence": "C0_HISTORICAL_RIVAL",
            "decision": "NOT_SELECTED__TARGET_MASKED_GLOBAL_PHASE_FAIL" if primary_facies["aqabac_all_benefic"] != "YES" else "RETAIN_PENDING_H1_AND_LOFO",
            "evidence": "nominal Picatrix H0 places Pisces03/Taurus08/Gemini11 under Jupiter/Venus/Venus",
            "counterevidence": f"target-masked global fit selects direction {primary_facies['selected_direction']} offset {primary_facies['selected_offset']} and yields {primary_facies['aqabac_status_counts']}; H1 sensitivity also required",
            "component_export_credit": "ZERO",
            "confirmed_lexeme": "NO",
        },
        {
            "candidate_id": "AQABAC_MARKED_FACIES_QUALITY",
            "working_interpretation": "AQABAC = markierte Facies-/Qualitätsklasse mit offener Polarität",
            "confidence": "C0_CROSS_SIGN_HISTORICAL_CLASS_RIVAL",
            "decision": "RETAIN_C0_SEMANTICALLY_OPEN",
            "evidence": "the complete family occurs once each in Pisces, Taurus and Gemini and can be evaluated in two attested facies systems",
            "counterevidence": "no target-masked global phase gives one planet or status; visual barrel, clothing and facing states also disagree",
            "component_export_credit": "ZERO",
            "confirmed_lexeme": "NO",
        },
        {
            "candidate_id": "GLOBAL_FACIES_STATUS_CODE",
            "working_interpretation": "recurrent complete families encode fixed benefic/malefic/other facies classes",
            "confidence": "C0_HISTORICAL_ARCHITECTURE",
            "decision": "NOT_SELECTED__PHASE_UNSTABLE__H1_TEXTURE_RETAINED_C0",
            "evidence": "two complete historical matrices and all 60 global transforms are exhaustively retained",
            "counterevidence": (
                f"Picatrix H0 block-null p={primary_facies['null_p_optimized_status_ge_observed']} and "
                f"H1 p={alternate_facies['null_p_optimized_status_ge_observed']}; the selected offsets and family assignments change, "
                "and AQABAC fails both target-masked phases"
            ),
            "component_export_credit": "ZERO",
            "confirmed_lexeme": "NO",
        },
        {
            "candidate_id": "AQABBA_BENEFIC_RULER_FACIES",
            "working_interpretation": "AQABBA = Facies mit benefischem Herrscher",
            "confidence": "C0_TWO_EVENT_PICATRIX_PHASE_STABLE_RIVAL",
            "decision": "RETAIN_C0_FOR_INDEPENDENT_THIRD_EVENT_OR_HOST_TEST",
            "evidence": (
                f"only Picatrix H0/H1 LOFO-consistent intersection; H0 {aqabba_h0['held_status_counts']}, "
                f"H1 {aqabba_h1['held_status_counts']} across Pisces and Gemini"
            ),
            "counterevidence": "only two events and no Taurus event, so phase robustness is partly trivial; Chaldean assignments disagree",
            "component_export_credit": "ZERO",
            "confirmed_lexeme": "NO",
        },
        {
            "candidate_id": "LEARNED_ENTRY_PLUS_LOCAL_GRAPHIC_FIELD",
            "working_interpretation": "individual learned member designations plus locally copied semantically open graphical/status material",
            "confidence": "C1_SELECTED_ARCHITECTURE",
            "decision": "SELECTED_PRIMARY",
            "evidence": "mirror texture is diffuse, visible candidates are block-bound, and historical phase does not transfer",
            "counterevidence": "three concrete visual rivals and the AQABBA benefic-ruler rival remain available for later independent tests",
            "component_export_credit": "ZERO",
            "confirmed_lexeme": "NO",
        },
    ]
    write_tsv(out / OUTPUT_NAMES[14], decisions)

    result = {
        "experiment_id": "GDT796",
        "scope": {
            "admitted_kluge_loci": 101,
            "new_pages_or_images_opened": 0,
            "guarded_visual_rows": 554,
            "varying_visual_state_rows": len(visual_atlas),
            "guarded_sign_rows": 5,
            "sealed_rows_materialized": 0,
            "mirror_outer_members": 10,
            "mirror_inner_members_used": 0,
        },
        "mirror": {
            "transform_rows": mirror_counts[mirror.RANKING_NAME],
            "boundary_best_transforms": f"{boundary_raw['observed_best_transform_71']}|{boundary_raw['observed_best_transform_72']}",
            "boundary_raw_p": boundary_raw["add_one_p"],
            "boundary_fixed_mask_normalized_p": boundary_fixed["add_one_p"],
            "boundary_split_half_raw_ranks": mirror_split_ranks,
            "boundary_split_half_normalized_ranks": mirror_normalized_split_ranks,
            "selected": "C0_F71_RELATIVE_REFLECTION_TEXTURE_NOT_REUSABLE_CODE",
        },
        "visual": {
            "channels": 3,
            "candidate_cards": len(visual_cards),
            "status_cards_passing_gate": 0,
            "general_status_code": "NOT_SELECTED",
            "cards": [row["card_id"] for row in visual_cards],
        },
        "facies": {
            "historical_matrices": 2,
            "taurus_phases": 2,
            "global_transform_rows": len(facies_transforms),
            "picatrix_h0_selected_without_aqabac": f"D{primary_facies['selected_direction']}_O{primary_facies['selected_offset']}",
            "picatrix_h0_aqabac_status_counts": primary_facies["aqabac_status_counts"],
            "picatrix_h0_block_null_p": primary_facies["null_p_optimized_status_ge_observed"],
            "picatrix_h1_selected_without_aqabac": f"D{alternate_facies['selected_direction']}_O{alternate_facies['selected_offset']}",
            "picatrix_h1_aqabac_status_counts": alternate_facies["aqabac_status_counts"],
            "picatrix_h1_block_null_p": alternate_facies["null_p_optimized_status_ge_observed"],
            "picatrix_h0_lofo_consistent_status_families": sum(row["held_consistent_status"] == "YES" for row in picatrix_lofo_h0),
            "picatrix_h1_lofo_consistent_status_families": sum(row["held_consistent_status"] == "YES" for row in picatrix_lofo_h1),
            "picatrix_h0_h1_lofo_consistent_intersection": picatrix_phase_stable,
            "leave_one_sign_out_rows": len(facies_sign_out),
            "picatrix_leave_one_sign_out_non_target_status_matches": sum(row["held_status_matches_training_mode"] == "YES" for row in picatrix_sign_out),
            "picatrix_leave_one_sign_out_non_target_targets": len(picatrix_sign_out),
            "picatrix_leave_one_sign_out_unambiguous_status_predictions": sum(row["training_status_unambiguous"] == "YES" for row in picatrix_sign_out),
            "picatrix_leave_one_sign_out_unambiguous_status_correct": sum(row["held_status_prediction_correct"] == "YES" for row in picatrix_sign_out),
            "aqabac_fortunate_facies": "NOT_SELECTED__TARGET_MASKED_GLOBAL_PHASE_FAIL" if primary_facies["aqabac_all_benefic"] != "YES" else "RETAIN_C0",
            "aqabac_marked_facies_quality": "RETAIN_C0_SEMANTICALLY_OPEN",
            "aqabba_benefic_ruler_facies": "RETAIN_C0_TWO_EVENTS_PISCES_GEMINI__NEEDS_INDEPENDENT_THIRD_EVENT_OR_HOST",
            "global_status_code": "NOT_SELECTED__PICATRIX_H1_TEXTURE_ONLY",
        },
        "decision": {
            "selected_primary_model": "LEARNED_ENTRY_PLUS_LOCAL_GRAPHIC_FIELD",
            "component_exports": 0,
            "confirmed_lexemes": 0,
            "next": "CONNECT_AQABBA_AND_THREE_VISUAL_RIVALS_TO_RUNNING_HOST_PARAGRAPHS_OR_TEST_INDEPENDENT_THIRD_EVENTS",
        },
    }
    status = (
        "PARTIAL__101_LOCI__OUTER10_F71_RELATIVE_REFLECTION_C0_NOT_REUSABLE__"
        "554_GUARDED_VISUAL_ROWS__174_VARYING_STATES__3_VISUAL_RIVALS_BELOW_GATE__ZERO_STATUS_CARDS__GENERAL_VISUAL_CODE_FAIL__"
        "240_HISTORICAL_TRANSFORMS__AQABAC_FORTUNATE_FACIES_TARGET_MASKED_FAIL__"
        "LEARNED_ENTRY_PLUS_LOCAL_GRAPHIC_FIELD_PRIMARY__ZERO_COMPONENT_EXPORT__ZERO_CONFIRMED_LEXEMES"
    )
    result["status"] = status
    (out / OUTPUT_NAMES[15]).write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(status)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
