#!/usr/bin/env python3
"""Build GDT795: source-family transfer over the 101 admitted Kluge labels."""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import math
import random
import re
import subprocess
import sys
from collections import Counter, defaultdict
from itertools import combinations
from pathlib import Path
from typing import Any, Iterable

sys.dont_write_bytecode = True


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
BASE = ROOT / "experiments/yolo/gdt795_source_native_family_kluge_transfer"
SRC = BASE / "src"
DEFAULT_ARTIFACTS = BASE / "artifacts"
LOCK = SRC / "SOURCE_LOCK.tsv"
QUERY_SPECS = SRC / "GUARDED_QUERY_SPECS.tsv"
MODEL_SPECS = SRC / "CANDIDATE_MODEL_SPECS.tsv"
ATLAS = ROOT / "experiments/yolo/gdt794_complete_label_multiform_slot_transfer/artifacts/GDT794_216_ADMITTED_CIRCLE_LABEL_ATLAS.tsv"
ALIGNMENT = ROOT / "experiments/semantic_assumptions/results/source_sta_group_alignment.tsv"
PREFIX_MANIFEST = ROOT / "gdt233_prefix_manifest.tsv"

OUTPUT_NAMES = (
    "GDT795_101_KLUGE_SOURCE_FAMILY_ATLAS.tsv",
    "GDT795_11_RECURRENT_FAMILY_SIGNATURES.tsv",
    "GDT795_26_LOFO_BOUNDARY_FAMILY_TARGETS.tsv",
    "GDT795_EXACT_REPRESENTATION_SUMMARY.tsv",
    "GDT795_99_FAMILY_SIMILARITY_PREDICTIONS.tsv",
    "GDT795_SIMILARITY_MODEL_SUMMARY.tsv",
    "GDT795_SHARED_TEMPLATE_TRANSFORMS.tsv",
    "GDT795_RELATIVE_DISTANCE_AUDIT.tsv",
    "GDT795_5_CONTEXTUAL_POSITION_CARDS.tsv",
    "GDT795_CANDIDATE_ADJUDICATION.tsv",
    "GDT795_RELATION_EDGE_PACKET.tsv",
    "GDT795_HOMOLOG_VS_LOCAL_ORDER_MATCHES.tsv",
    "RESULT.json",
)

QUERY_COLUMNS = (
    "source_group_id",
    "edition",
    "locus",
    "source_group_index",
    "source_group_count",
    "left_separator",
    "right_separator",
    "sta_group_raw",
    "primary_sta_codes",
    "primary_sta_families",
    "primary_sta_symbol_count",
    "alternative_site_count",
    "nearest_basic_eva_primary",
)

EDGE_COLUMNS = (
    "edge_id", "batch_id", "page", "physical_folio", "diagram_unit_id",
    "pivot_visual_id", "pivot_locus", "target_visual_id", "target_locus",
    "relation_type", "direction_basis", "ownership_basis",
    "geometry_only_selection", "source_manifest_id", "page_crop_sha256",
    "pivot_crop_sha256", "target_crop_sha256", "source_aware_localizer",
    "relation_reviewer", "relation_confidence", "ambiguity_state",
    "formal_access_state", "fold_assignment", "eligibility_status",
)

EDITIONS = ("ZL3b", "IT2a", "RF1b")
TEMPLATE_BY_PAGE = {
    "f70v1": ("T15", 15),
    "f71v": ("T15", 15),
    "f72r1": ("T15", 15),
    "f70v2": ("T30", 30),
    "f72r2": ("T30", 30),
}


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(
    path: Path,
    rows: Iterable[dict[str, Any]],
    fields: Iterable[str] | None = None,
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
    if not rows or len({row["path"] for row in rows}) != len(rows):
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
    materialized = list(values)
    return "|".join(str(value) for value in materialized) if materialized else "NONE"


def circular_distance(left: int, right: int, period: int = 30) -> int:
    difference = abs(left - right) % period
    return min(difference, period - difference)


def signed_circular_delta(left: int, right: int, period: int = 30) -> int:
    return ((right - left + period // 2) % period) - period // 2


def circular_mean_member(values: list[int], period: int = 30) -> int:
    x = sum(math.cos(2 * math.pi * (value - 1) / period) for value in values)
    y = sum(math.sin(2 * math.pi * (value - 1) / period) for value in values)
    if abs(x) < 1e-12 and abs(y) < 1e-12:
        return min(values)
    raw = (math.atan2(y, x) * period / (2 * math.pi)) % period + 1
    return ((int(math.floor(raw + 0.5)) - 1) % period) + 1


def levenshtein(left: str, right: str) -> int:
    previous = list(range(len(right) + 1))
    for row_index, left_symbol in enumerate(left, start=1):
        current = [row_index]
        for column_index, right_symbol in enumerate(right, start=1):
            current.append(
                min(
                    current[-1] + 1,
                    previous[column_index] + 1,
                    previous[column_index - 1] + (left_symbol != right_symbol),
                )
            )
        previous = current
    return previous[-1]


def normalized_similarity(left: str, right: str) -> float:
    return 1.0 - levenshtein(left, right) / max(len(left), len(right), 1)


def guarded_alignment_query(loci: list[str]) -> tuple[list[dict[str, str]], dict[str, int]]:
    specs = read_tsv(QUERY_SPECS)
    if len(specs) != 1:
        raise RuntimeError("expected one guarded query specification")
    spec = specs[0]
    if spec["selector"] != "locus" or spec["path"] != ALIGNMENT.relative_to(ROOT).as_posix():
        raise RuntimeError("guarded query specification changed")
    if tuple(spec["columns"].split(",")) != QUERY_COLUMNS:
        raise RuntimeError("guarded query column specification changed")
    if any(value.startswith("f84") for value in loci):
        raise RuntimeError("sealed selector entered admitted locus list")

    command = [
        str(ROOT / "vmanus-exp"),
        "query-tsv",
        spec["path"],
        "--selector",
        "locus",
    ]
    for locus in loci:
        command.extend(("--allow", locus))
    command.extend(("--columns", spec["columns"], "--forbid-prefix", "f84"))
    completed = subprocess.run(
        command,
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    if completed.returncode:
        raise RuntimeError("guarded alignment query failed: " + completed.stderr.strip())
    match = re.search(r"GUARD_STATS\s+(\{[^\n]+\})", completed.stderr)
    if not match:
        raise RuntimeError("guarded alignment query omitted guard statistics")
    stats = json.loads(match.group(1))
    rows = list(csv.DictReader(io.StringIO(completed.stdout), delimiter="\t"))
    if tuple(rows[0]) != QUERY_COLUMNS:
        raise RuntimeError("guarded alignment output schema changed")
    if stats != {"selected": 394, "skipped_forbidden": 2122, "skipped_not_allowed": 112954}:
        raise RuntimeError(f"guard statistics changed: {stats}")
    return rows, stats


def majority_value(values: dict[str, str]) -> tuple[str, int, list[str]]:
    counts = Counter(values.values())
    ranked = sorted(counts.items(), key=lambda item: (-item[1], item[0]))
    value, support = ranked[0]
    if support < 2:
        raise RuntimeError(f"no two-reader majority: {values}")
    supporters = sorted(edition for edition, candidate in values.items() if candidate == value)
    return value, support, supporters


def derive_prefix(boundary_family: str, prefixes: list[str]) -> tuple[str, str]:
    compact = boundary_family.replace("|", "")
    prefix = next((candidate for candidate in prefixes if compact.startswith(candidate)), "NONE")
    if prefix == "NONE":
        return prefix, boundary_family
    if not boundary_family.startswith(prefix):
        raise RuntimeError(f"selected prefix crosses a source group boundary: {boundary_family}")
    residual = boundary_family[len(prefix):]
    return prefix, residual if residual else "EMPTY"


def exact_rows(
    rows: list[dict[str, Any]],
    field: str,
    representation_id: str,
) -> list[dict[str, Any]]:
    result: list[dict[str, Any]] = []
    for target in rows:
        key = str(target[field])
        if key == "NONE":
            continue
        training = [
            row for row in rows
            if row["physical_folio"] != target["physical_folio"] and row[field] == key
        ]
        if not training:
            continue
        training_positions = [int(row["kluge_a_member"]) for row in training]
        target_a = int(target["kluge_a_member"])
        predicted = circular_mean_member(training_positions)
        same_template = [row for row in training if row["template_id"] == target["template_id"]]
        result.append(
            {
                "representation_id": representation_id,
                "representation_key": key,
                "held_physical_folio": target["physical_folio"],
                "target_source_selector": target["source_selector"],
                "target_template_id": target["template_id"],
                "target_locus": target["locus"],
                "target_surface": target["complete_label_surface"],
                "target_a_member": target_a,
                "training_event_count": len(training),
                "training_physical_folios": joined(sorted({row["physical_folio"] for row in training})),
                "training_templates": joined(sorted({row["template_id"] for row in training})),
                "training_a_members": joined(int(row["kluge_a_member"]) for row in training),
                "training_surfaces": joined(row["complete_label_surface"] for row in training),
                "any_training_exact_a": "YES" if target_a in training_positions else "NO",
                "any_training_within_one_a": "YES" if any(circular_distance(target_a, value) <= 1 for value in training_positions) else "NO",
                "circular_mean_predicted_a": predicted,
                "circular_mean_distance": circular_distance(target_a, predicted),
                "same_template_training_events": len(same_template),
                "same_template_any_exact_a": "YES" if any(int(row["kluge_a_member"]) == target_a for row in same_template) else "NO",
                "same_template_any_within_one_a": "YES" if any(circular_distance(target_a, int(row["kluge_a_member"])) <= 1 for row in same_template) else "NO",
                "interpretation_ceiling": "COMPLETE_FORMAL_SIGNATURE_POSITION_DIAGNOSTIC_ONLY",
            }
        )
    return result


def exact_metrics(predictions: list[dict[str, Any]]) -> dict[str, float]:
    count = len(predictions)
    return {
        "target_count": count,
        "key_count": len({row["representation_key"] for row in predictions}),
        "any_exact": sum(row["any_training_exact_a"] == "YES" for row in predictions),
        "any_pm1": sum(row["any_training_within_one_a"] == "YES" for row in predictions),
        "mean_exact": sum(int(row["circular_mean_distance"]) == 0 for row in predictions),
        "mean_pm1": sum(int(row["circular_mean_distance"]) <= 1 for row in predictions),
        "mean_distance": sum(int(row["circular_mean_distance"]) for row in predictions) / count if count else 0.0,
    }


def permute_members(rows: list[dict[str, Any]], rng: random.Random) -> list[dict[str, Any]]:
    copied = [dict(row) for row in rows]
    by_page: dict[str, list[int]] = defaultdict(list)
    for index, row in enumerate(copied):
        by_page[row["source_selector"]].append(index)
    for indices in by_page.values():
        values = [copied[index]["kluge_a_member"] for index in indices]
        rng.shuffle(values)
        for index, value in zip(indices, values):
            copied[index]["kluge_a_member"] = value
    return copied


def similarity_predictions(
    rows: list[dict[str, Any]],
    field: str,
    representation_id: str,
    members: list[int] | None = None,
    matrix: list[list[float]] | None = None,
) -> list[dict[str, Any]]:
    values = [str(row[field]) for row in rows]
    if matrix is None:
        matrix = [
            [normalized_similarity(values[left], values[right]) for right in range(len(rows))]
            for left in range(len(rows))
        ]
    assigned = members or [int(row["kluge_a_member"]) for row in rows]
    predictions: list[dict[str, Any]] = []
    for target_index, target in enumerate(rows):
        scores: dict[int, float] = {}
        supports: dict[int, list[int]] = defaultdict(list)
        for train_index, train in enumerate(rows):
            if train["physical_folio"] == target["physical_folio"]:
                continue
            member = assigned[train_index]
            score = matrix[target_index][train_index]
            if member not in scores or score > scores[member]:
                scores[member] = score
                supports[member] = [train_index]
            elif abs(score - scores[member]) < 1e-12:
                supports[member].append(train_index)
        target_member = assigned[target_index]
        if target_member not in scores:
            continue
        true_score = scores[target_member]
        better = sum(score > true_score + 1e-12 for score in scores.values())
        tied = sum(abs(score - true_score) < 1e-12 for score in scores.values())
        rank_low = better + 1
        rank_high = better + tied
        best_score = max(scores.values())
        top_members = sorted(member for member, score in scores.items() if abs(score - best_score) < 1e-12)
        fractional_top1 = (1.0 / len(top_members)) if target_member in top_members else 0.0
        fractional_pm1 = sum(circular_distance(target_member, member) <= 1 for member in top_members) / len(top_members)
        reciprocal_rank = sum(1.0 / rank for rank in range(rank_low, rank_high + 1)) / tied
        normalized_rank = ((rank_low + rank_high) / 2) / len(scores)
        support_indices = [index for member in top_members for index in supports[member]]
        predictions.append(
            {
                "representation_id": representation_id,
                "held_physical_folio": target["physical_folio"],
                "target_locus": target["locus"],
                "target_surface": target["complete_label_surface"],
                "target_a_member": target_member,
                "candidate_a_count": len(scores),
                "true_a_similarity": f6(true_score),
                "rank_low": rank_low,
                "rank_high": rank_high,
                "normalized_midrank": f6(normalized_rank),
                "tie_adjusted_reciprocal_rank": f6(reciprocal_rank),
                "top_a_members": joined(top_members),
                "top_similarity": f6(best_score),
                "fractional_top1_credit": f6(fractional_top1),
                "fractional_within_one_credit": f6(fractional_pm1),
                "top_support_loci": joined(rows[index]["locus"] for index in support_indices),
                "top_support_surfaces": joined(rows[index]["complete_label_surface"] for index in support_indices),
                "interpretation_ceiling": "APPROXIMATE_FORM_TEXTURE_POSITION_DIAGNOSTIC_ONLY",
            }
        )
    return predictions


def similarity_metrics(predictions: list[dict[str, Any]]) -> dict[str, float]:
    count = len(predictions)
    return {
        "target_count": count,
        "fractional_top1": sum(float(row["fractional_top1_credit"]) for row in predictions) / count,
        "fractional_pm1": sum(float(row["fractional_within_one_credit"]) for row in predictions) / count,
        "mrr": sum(float(row["tie_adjusted_reciprocal_rank"]) for row in predictions) / count,
        "mean_rank": sum(float(row["normalized_midrank"]) for row in predictions) / count,
    }


def transform_hits(
    left: dict[int, dict[str, Any]],
    right: dict[int, dict[str, Any]],
    period: int,
    orientation: int,
    shift: int,
) -> tuple[int, int, list[str]]:
    matches: list[str] = []
    comparable = 0
    for left_member, left_row in sorted(left.items()):
        right_member = ((orientation * (left_member - 1) + shift) % period) + 1
        if right_member not in right:
            continue
        comparable += 1
        right_row = right[right_member]
        if left_row["canonical_boundary_family"] == right_row["canonical_boundary_family"]:
            matches.append(
                f"{left_member}>{right_member}:{left_row['canonical_boundary_family']}:"
                f"{left_row['complete_label_surface']}>{right_row['complete_label_surface']}"
            )
    return len(matches), comparable, matches


def best_transform(
    left: dict[int, dict[str, Any]],
    right: dict[int, dict[str, Any]],
    period: int,
) -> tuple[int, int, int, int, list[str]]:
    candidates = []
    for orientation in (1, -1):
        for shift in range(period):
            hits, comparable, matches = transform_hits(left, right, period, orientation, shift)
            candidates.append((hits, comparable, orientation, shift, matches))
    return max(candidates, key=lambda row: (row[0], row[1], row[2] == 1, -row[3]))


def recurrent_default(signature: str, positions: list[int]) -> tuple[str, str, str]:
    defaults = {
        "AQABAB": (
            "im T15-Kontext Bezeichnung der Stelle 09A / des vierten äußeren Ringplatzes",
            "C1_CONTEXTUAL_T15_POSITION",
            "außerhalb T15 auch 04A und 25A; kein universeller Neuner-Code",
        ),
        "AQABAG": (
            "im T15-Kontext frühe innere Mitgliedsstelle 02-03A",
            "C0_CONTEXTUAL_T15_WINDOW",
            "im T30-Kontext auch 10A; nur zwei positive physische Folios",
        ),
        "AQABA": (
            "breite graphische Bezeichnungsklasse; einzelne Mitgliedsbedeutung offen",
            "C0_GRAPHICAL_CLASS_ONLY",
            "neun Belege an acht A-Positionen; keine eindeutige Stelle",
        ),
        "AQAB": (
            "f72-gebundene kurze graphische Bezeichnungsklasse",
            "C0_PAGE_BOUND_GRAPHICAL_CLASS",
            "sechs Belege an sechs A-Positionen und kein zweites Folio",
        ),
        "AQABAC": (
            "wandernde vollständige Formklasse an 03A/08A/11A",
            "C0_MULTI_POSITION_CLASS",
            "drei Folios, aber keine gemeinsame oder benachbarte A-Stelle",
        ),
        "AQACAB": (
            "T30-Formklasse an 02A/06A/28A",
            "C0_MULTI_POSITION_CLASS",
            "gleiche Signatur und sogar okaram-Ganzform verschieben stark",
        ),
        "AQABBA": (
            "T30-Gegenbereichspaar 26A/05A",
            "C0_OPPOSITION_RIVAL",
            "nur zwei Belege; keine absolute Mitgliedsstelle",
        ),
        "AQABLA": (
            "kontextwechselnde Formklasse an T15-13A und T30-04A",
            "C0_MULTI_POSITION_CLASS",
            "Templatewechsel zerstört eine absolute Position",
        ),
        "AQACABBA": (
            "f72-interne Formbezeichnung an 10A/12A",
            "C0_SAME_FOLIO_WINDOW",
            "identische Oberfläche, aber kein unabhängiges Folio",
        ),
        "AQAFA": (
            "f72-interne Gegenbereichsform an 05A/29A",
            "C0_SAME_FOLIO_OPPOSITION_RIVAL",
            "nur ein physisches Folio und verschiedene Oberflächen",
        ),
        "AQKA|ACA": (
            "f72-interne Ganzbezeichnung an 04A/15A",
            "C0_SAME_FOLIO_MULTI_POSITION",
            "identische Oberfläche, aber stark verschiedene Plätze",
        ),
    }
    if signature not in defaults:
        return (
            "beobachtete graphische Formklasse an " + "/".join(f"{value:02d}A" for value in positions),
            "C0_OBSERVED_FORMAL_CLASS",
            "keine übertragene konkrete Bedeutung",
        )
    return defaults[signature]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_ARTIFACTS)
    args = parser.parse_args()
    out = args.output_dir.resolve()
    out.mkdir(parents=True, exist_ok=True)
    verify_source_lock()

    source_atlas = read_tsv(ATLAS)
    kluge_source = [row for row in source_atlas if row["kluge_a_member"] != "NA"]
    if len(kluge_source) != 101 or len({row["locus"] for row in kluge_source}) != 101:
        raise RuntimeError("GDT794 Kluge panel changed")
    if {row["source_selector"] for row in kluge_source} != set(TEMPLATE_BY_PAGE):
        raise RuntimeError("unexpected Kluge source selectors")
    loci = sorted(row["locus"] for row in kluge_source)
    alignment_rows, guard_stats = guarded_alignment_query(loci)

    by_locus_edition: dict[str, dict[str, list[dict[str, str]]]] = defaultdict(lambda: defaultdict(list))
    for row in alignment_rows:
        if row["locus"] not in set(loci):
            raise RuntimeError("guarded query returned an unrequested locus")
        by_locus_edition[row["locus"]][row["edition"]].append(row)

    prefix_rows = read_tsv(PREFIX_MANIFEST)
    prefixes = sorted(
        (row["prefix"] for row in prefix_rows if row["selection_status"] == "STRICT_TRAINING_SELECTED"),
        key=lambda value: (-len(value), value),
    )
    if len(prefixes) != 14 or "BACA" in prefixes:
        raise RuntimeError("GDT233 strict prefix set changed")

    atlas_rows: list[dict[str, Any]] = []
    source_by_locus = {row["locus"]: row for row in kluge_source}
    for ordinal, locus in enumerate(loci, start=1):
        source = source_by_locus[locus]
        editions = by_locus_edition.get(locus, {})
        if set(editions) != set(EDITIONS):
            raise RuntimeError(f"missing alternate reading at {locus}: {sorted(editions)}")
        boundary_values: dict[str, str] = {}
        compact_values: dict[str, str] = {}
        member_values: dict[str, str] = {}
        group_counts: dict[str, int] = {}
        alternatives: dict[str, int] = {}
        nearest_eva: dict[str, str] = {}
        for edition in EDITIONS:
            groups = sorted(editions[edition], key=lambda row: int(row["source_group_index"]))
            expected_count = int(groups[0]["source_group_count"])
            if [int(row["source_group_index"]) for row in groups] != list(range(1, expected_count + 1)):
                raise RuntimeError(f"non-contiguous source groups at {edition} {locus}")
            if any(int(row["source_group_count"]) != expected_count for row in groups):
                raise RuntimeError(f"source group count changes inside {edition} {locus}")
            boundary = "|".join(row["primary_sta_families"] for row in groups)
            boundary_values[edition] = boundary
            compact_values[edition] = boundary.replace("|", "")
            member_values[edition] = "|".join(
                ".".join(row["primary_sta_codes"].split()) for row in groups
            )
            group_counts[edition] = expected_count
            alternatives[edition] = sum(int(row["alternative_site_count"]) for row in groups)
            nearest_eva[edition] = " ".join(row["nearest_basic_eva_primary"] for row in groups)

        canonical_boundary, boundary_support, boundary_editions = majority_value(boundary_values)
        canonical_compact, compact_support, compact_editions = majority_value(compact_values)
        member_counts = Counter(member_values.values())
        member_support = max(member_counts.values())
        member_agreement = (
            "ALL3_MEMBER_SEQUENCE" if member_support == 3
            else "MEMBER_SEQUENCE_2OF3" if member_support == 2
            else "MEMBER_SEQUENCE_ALL_DIFFERENT"
        )
        if canonical_boundary.replace("|", "") != canonical_compact:
            raise RuntimeError(f"boundary and compact majorities disagree at {locus}")
        if boundary_support == 3:
            agreement = "ALL3_BOUNDARY_AND_FAMILY"
        elif compact_support == 3:
            agreement = "ALL3_FAMILY__BOUNDARY_2OF3"
        else:
            agreement = "FAMILY_2OF3"
        prefix, residual = derive_prefix(canonical_boundary, prefixes)
        template_id, period = TEMPLATE_BY_PAGE[source["source_selector"]]
        atlas_rows.append(
            {
                "family_atlas_ordinal": ordinal,
                "template_id": template_id,
                "template_period": period,
                "physical_folio": source["physical_folio"],
                "source_selector": source["source_selector"],
                "array_id": source["array_id"],
                "locus": locus,
                "slot_index": source["slot_index"],
                "slot_count": source["slot_count"],
                "kluge_a_member": source["kluge_a_member"],
                "complete_label_surface": source["complete_label_surface"],
                "label_token_count": source["label_token_count"],
                "zl_boundary_family": boundary_values["ZL3b"],
                "it_boundary_family": boundary_values["IT2a"],
                "rf_boundary_family": boundary_values["RF1b"],
                "zl_member_sequence": member_values["ZL3b"],
                "it_member_sequence": member_values["IT2a"],
                "rf_member_sequence": member_values["RF1b"],
                "member_sequence_max_support": member_support,
                "member_sequence_agreement": member_agreement,
                "canonical_boundary_family": canonical_boundary,
                "canonical_compact_family": canonical_compact,
                "boundary_reader_support": boundary_support,
                "compact_reader_support": compact_support,
                "boundary_supporting_editions": joined(boundary_editions),
                "compact_supporting_editions": joined(compact_editions),
                "agreement_class": agreement,
                "zl_group_count": group_counts["ZL3b"],
                "it_group_count": group_counts["IT2a"],
                "rf_group_count": group_counts["RF1b"],
                "transferred_prefix": prefix,
                "strict_residual": residual,
                "zl_alternative_sites": alternatives["ZL3b"],
                "it_alternative_sites": alternatives["IT2a"],
                "rf_alternative_sites": alternatives["RF1b"],
                "zl_nearest_eva": nearest_eva["ZL3b"],
                "it_nearest_eva": nearest_eva["IT2a"],
                "rf_nearest_eva": nearest_eva["RF1b"],
                "source_family_semantics": "FORMAL_TRANSCRIPTION_FAMILY__NOT_AUTHORIAL_WORD_OR_SOUND",
                "component_export_credit": "ZERO",
            }
        )
    if Counter(row["agreement_class"] for row in atlas_rows) != Counter({
        "ALL3_BOUNDARY_AND_FAMILY": 81,
        "ALL3_FAMILY__BOUNDARY_2OF3": 11,
        "FAMILY_2OF3": 9,
    }):
        raise RuntimeError("source-family agreement census changed")
    if Counter(row["member_sequence_agreement"] for row in atlas_rows) != Counter({
        "ALL3_MEMBER_SEQUENCE": 55,
        "MEMBER_SEQUENCE_2OF3": 36,
        "MEMBER_SEQUENCE_ALL_DIFFERENT": 10,
    }):
        raise RuntimeError("source-member agreement census changed")
    if not all(int(row["zl_group_count"]) == int(row["label_token_count"]) for row in atlas_rows):
        raise RuntimeError("ZL source groups no longer align one-for-one with GDT794 label tokens")
    write_tsv(out / OUTPUT_NAMES[0], atlas_rows)

    by_signature: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in atlas_rows:
        by_signature[row["canonical_boundary_family"]].append(row)
    recurrent = {key: rows for key, rows in by_signature.items() if len(rows) >= 2}
    if len(recurrent) != 11 or sum(len(rows) for rows in recurrent.values()) != 38:
        raise RuntimeError("recurrent source-family census changed")
    recurrent_rows: list[dict[str, Any]] = []
    for signature, rows in sorted(recurrent.items()):
        positions = sorted(int(row["kluge_a_member"]) for row in rows)
        by_a: dict[int, set[str]] = defaultdict(set)
        for row in rows:
            by_a[int(row["kluge_a_member"])].add(row["physical_folio"])
        same_a = sorted(member for member, folios in by_a.items() if len(folios) >= 2)
        same_a_pairs = [
            (left, right)
            for left, right in combinations(rows, 2)
            if left["physical_folio"] != right["physical_folio"]
            and left["kluge_a_member"] == right["kluge_a_member"]
        ]
        default, confidence, counterevidence = recurrent_default(signature, sorted(set(positions)))
        recurrent_rows.append(
            {
                "canonical_boundary_family": signature,
                "occurrence_count": len(rows),
                "distinct_surface_count": len({row["complete_label_surface"] for row in rows}),
                "complete_label_surfaces": joined(sorted({row["complete_label_surface"] for row in rows})),
                "physical_folio_count": len({row["physical_folio"] for row in rows}),
                "physical_folios": joined(sorted({row["physical_folio"] for row in rows})),
                "template_ids": joined(sorted({row["template_id"] for row in rows})),
                "a_members": joined(positions),
                "distinct_a_count": len(set(positions)),
                "cross_folio_same_a_members": joined(same_a),
                "cross_folio_same_a_family_pair_count": len(same_a_pairs),
                "same_a_exact_zl_member_pair_count": sum(
                    left["zl_member_sequence"] == right["zl_member_sequence"]
                    for left, right in same_a_pairs
                ),
                "working_default_de": default,
                "confidence": confidence,
                "evidence": f"{len(rows)} Belege; {len({row['physical_folio'] for row in rows})} physische Folios; A={joined(positions)}",
                "counterevidence": counterevidence,
                "renderer_license": "CONTEXTUAL_CIRCLE_CARD_ONLY" if signature in {"AQABAB", "AQABAG"} else "NO_SEMANTIC_RENDERER_LICENSE",
                "component_export_credit": "ZERO",
                "confirmed_lexeme": "NO",
            }
        )
    write_tsv(out / OUTPUT_NAMES[1], recurrent_rows)

    representations = (
        ("complete_label_surface", "VISIBLE_COMPLETE_SURFACE"),
        ("zl_member_sequence", "ZL_MEMBER_SEQUENCE"),
        ("canonical_boundary_family", "BOUNDARY_FAMILY"),
        ("canonical_compact_family", "COMPACT_FAMILY"),
        ("transferred_prefix", "TRANSFERRED_PREFIX"),
        ("strict_residual", "FORMAL_RESIDUAL"),
    )
    all_exact: dict[str, list[dict[str, Any]]] = {}
    exact_summary: list[dict[str, Any]] = []
    rng = random.Random(795001)
    boundary_null: list[dict[str, float]] = []
    for _ in range(2000):
        permuted = permute_members(atlas_rows, rng)
        boundary_null.append(exact_metrics(exact_rows(permuted, "canonical_boundary_family", "BOUNDARY_FAMILY")))
    for field, representation_id in representations:
        predictions = exact_rows(atlas_rows, field, representation_id)
        all_exact[representation_id] = predictions
        metrics = exact_metrics(predictions)
        is_boundary = representation_id == "BOUNDARY_FAMILY"
        exact_summary.append(
            {
                "representation_id": representation_id,
                "target_event_count": int(metrics["target_count"]),
                "cross_folio_key_count": int(metrics["key_count"]),
                "any_training_exact_a_count": int(metrics["any_exact"]),
                "any_training_exact_a_rate": f6(metrics["any_exact"] / metrics["target_count"]),
                "any_training_within_one_count": int(metrics["any_pm1"]),
                "any_training_within_one_rate": f6(metrics["any_pm1"] / metrics["target_count"]),
                "circular_mean_exact_count": int(metrics["mean_exact"]),
                "circular_mean_within_one_count": int(metrics["mean_pm1"]),
                "circular_mean_distance": f6(metrics["mean_distance"]),
                "null_iterations": 2000 if is_boundary else 0,
                "null_mean_any_exact_count": f6(sum(row["any_exact"] for row in boundary_null) / len(boundary_null)) if is_boundary else "NA",
                "null_p_any_exact_ge_observed": f6((1 + sum(row["any_exact"] >= metrics["any_exact"] for row in boundary_null)) / (len(boundary_null) + 1)) if is_boundary else "NA",
                "null_mean_circular_distance": f6(sum(row["mean_distance"] for row in boundary_null) / len(boundary_null)) if is_boundary else "NA",
                "null_p_distance_le_observed": f6((1 + sum(row["mean_distance"] <= metrics["mean_distance"] for row in boundary_null)) / (len(boundary_null) + 1)) if is_boundary else "NA",
                "gate_result": "FAIL_SEVERAL_POSITION_CODEBOOK" if representation_id != "BOUNDARY_FAMILY" else "TWO_ANCHORS_ONLY__FAIL_SEVERAL_POSITION_CODEBOOK",
                "component_export_credit": "ZERO",
            }
        )
    boundary_predictions = all_exact["BOUNDARY_FAMILY"]
    if len(boundary_predictions) != 26:
        raise RuntimeError(f"expected 26 exact boundary-family targets, found {len(boundary_predictions)}")
    write_tsv(out / OUTPUT_NAMES[2], boundary_predictions)
    write_tsv(out / OUTPUT_NAMES[3], exact_summary)

    similarity_fields = (
        ("canonical_boundary_family", "BOUNDARY_FAMILY_EDIT"),
        ("canonical_compact_family", "COMPACT_FAMILY_EDIT"),
        ("surface_compact", "VISIBLE_SURFACE_EDIT"),
    )
    for row in atlas_rows:
        row["surface_compact"] = str(row["complete_label_surface"]).replace(" ", "")
    similarity_results: dict[str, list[dict[str, Any]]] = {}
    similarity_matrices: dict[str, list[list[float]]] = {}
    for field, representation_id in similarity_fields:
        values = [str(row[field]) for row in atlas_rows]
        matrix = [
            [normalized_similarity(values[left], values[right]) for right in range(len(atlas_rows))]
            for left in range(len(atlas_rows))
        ]
        similarity_matrices[representation_id] = matrix
        similarity_results[representation_id] = similarity_predictions(
            atlas_rows, field, representation_id, matrix=matrix
        )
    boundary_similarity = similarity_results["BOUNDARY_FAMILY_EDIT"]
    if len(boundary_similarity) != 99:
        raise RuntimeError(f"expected 99 similarity targets, found {len(boundary_similarity)}")
    write_tsv(out / OUTPUT_NAMES[4], boundary_similarity)

    permutation_rng = random.Random(795002)
    permuted_members: list[list[int]] = []
    base_members = [int(row["kluge_a_member"]) for row in atlas_rows]
    by_page_indices: dict[str, list[int]] = defaultdict(list)
    for index, row in enumerate(atlas_rows):
        by_page_indices[row["source_selector"]].append(index)
    for _ in range(500):
        values = list(base_members)
        for indices in by_page_indices.values():
            local = [values[index] for index in indices]
            permutation_rng.shuffle(local)
            for index, value in zip(indices, local):
                values[index] = value
        permuted_members.append(values)

    similarity_summary: list[dict[str, Any]] = []
    for field, representation_id in similarity_fields:
        observed = similarity_metrics(similarity_results[representation_id])
        null_metrics = [
            similarity_metrics(
                similarity_predictions(
                    atlas_rows,
                    field,
                    representation_id,
                    values,
                    similarity_matrices[representation_id],
                )
            )
            for values in permuted_members
        ]
        similarity_summary.append(
            {
                "representation_id": representation_id,
                "target_event_count": int(observed["target_count"]),
                "fractional_top1": f6(observed["fractional_top1"]),
                "fractional_within_one": f6(observed["fractional_pm1"]),
                "tie_adjusted_mrr": f6(observed["mrr"]),
                "mean_normalized_rank": f6(observed["mean_rank"]),
                "null_iterations": len(null_metrics),
                "null_mean_fractional_top1": f6(sum(row["fractional_top1"] for row in null_metrics) / len(null_metrics)),
                "null_p_top1_ge_observed": f6((1 + sum(row["fractional_top1"] >= observed["fractional_top1"] for row in null_metrics)) / (len(null_metrics) + 1)),
                "null_mean_mrr": f6(sum(row["mrr"] for row in null_metrics) / len(null_metrics)),
                "null_p_mrr_ge_observed": f6((1 + sum(row["mrr"] >= observed["mrr"] for row in null_metrics)) / (len(null_metrics) + 1)),
                "null_mean_rank": f6(sum(row["mean_rank"] for row in null_metrics) / len(null_metrics)),
                "null_p_rank_le_observed": f6((1 + sum(row["mean_rank"] <= observed["mean_rank"] for row in null_metrics)) / (len(null_metrics) + 1)),
                "gate_result": "WEAK_FORM_TEXTURE_ONLY" if representation_id != "VISIBLE_SURFACE_EDIT" else "VISIBLE_SURFACE_BASELINE_FAIL",
                "semantic_export": "NONE",
            }
        )
    write_tsv(out / OUTPUT_NAMES[5], similarity_summary)

    maps: dict[str, dict[int, dict[str, Any]]] = defaultdict(dict)
    for row in atlas_rows:
        maps[row["source_selector"]][int(row["kluge_a_member"])] = row
    pair_specs = (
        ("T15_PAIR_F70_F71", "f70v1", "f71v", 15),
        ("T15_PAIR_F70_F72", "f70v1", "f72r1", 15),
        ("T15_PAIR_F71_F72", "f71v", "f72r1", 15),
        ("T30_PAIR_F70_F72", "f70v2", "f72r2", 30),
    )
    transform_rows: list[dict[str, Any]] = []
    transform_rng = random.Random(795003)
    for model_id, left_page, right_page, period in pair_specs:
        left = maps[left_page]
        right = maps[right_page]
        native_hits, native_comparable, native_matches = transform_hits(left, right, period, 1, 0)
        best_hits, best_comparable, orientation, shift, best_matches = best_transform(left, right, period)
        null_best: list[int] = []
        for _ in range(500):
            shuffled_left_values = list(left.values())
            shuffled_right_values = list(right.values())
            transform_rng.shuffle(shuffled_left_values)
            transform_rng.shuffle(shuffled_right_values)
            shuffled_left = dict(zip(sorted(left), shuffled_left_values))
            shuffled_right = dict(zip(sorted(right), shuffled_right_values))
            null_best.append(best_transform(shuffled_left, shuffled_right, period)[0])
        common = set(row["canonical_boundary_family"] for row in left.values()) & set(row["canonical_boundary_family"] for row in right.values())
        transform_rows.append(
            {
                "model_id": model_id,
                "template_id": f"T{period}",
                "left_page": left_page,
                "right_pages": right_page,
                "period": period,
                "common_exact_family_count": len(common),
                "common_exact_families": joined(sorted(common)),
                "native_comparable_positions": native_comparable,
                "native_exact_hits": native_hits,
                "native_matches": joined(native_matches),
                "best_orientation": "FORWARD" if orientation == 1 else "REVERSE",
                "best_shift": shift,
                "best_comparable_positions": best_comparable,
                "best_exact_hits": best_hits,
                "best_matches": joined(best_matches),
                "null_iterations": len(null_best),
                "null_mean_best_hits": f6(sum(null_best) / len(null_best)),
                "null_p_best_hits_ge_observed": f6((1 + sum(value >= best_hits for value in null_best)) / (len(null_best) + 1)),
                "gate_result": "FAIL_SHARED_TRANSFORM__FEWER_THAN_3_EXACT_SIGNATURES",
                "component_export_credit": "ZERO",
            }
        )

    reference = maps["f70v1"]
    targets = (maps["f71v"], maps["f72r1"])
    joint_options = []
    for orientation in (1, -1):
        for shift in range(15):
            parts = [transform_hits(reference, target, 15, orientation, shift) for target in targets]
            joint_options.append((sum(part[0] for part in parts), sum(part[1] for part in parts), orientation, shift, [item for part in parts for item in part[2]]))
    joint_best = max(joint_options, key=lambda row: (row[0], row[1], row[2] == 1, -row[3]))
    native_parts = [transform_hits(reference, target, 15, 1, 0) for target in targets]
    transform_rows.append(
        {
            "model_id": "T15_ONE_TRANSFORM_AGAINST_TWO_PAGES",
            "template_id": "T15",
            "left_page": "f70v1",
            "right_pages": "f71v|f72r1",
            "period": 15,
            "common_exact_family_count": 2,
            "common_exact_families": "AQABAB|AQABAG",
            "native_comparable_positions": sum(part[1] for part in native_parts),
            "native_exact_hits": sum(part[0] for part in native_parts),
            "native_matches": joined(item for part in native_parts for item in part[2]),
            "best_orientation": "FORWARD" if joint_best[2] == 1 else "REVERSE",
            "best_shift": joint_best[3],
            "best_comparable_positions": joint_best[1],
            "best_exact_hits": joint_best[0],
            "best_matches": joined(joint_best[4]),
            "null_iterations": 0,
            "null_mean_best_hits": "NA",
            "null_p_best_hits_ge_observed": "NA",
            "gate_result": "FAIL_ONE_SHARED_TRANSFORM__THE_TWO_ANCHORS_REQUIRE_DIFFERENT_SHIFTS",
            "component_export_credit": "ZERO",
        }
    )
    write_tsv(out / OUTPUT_NAMES[6], transform_rows)

    unique_cross_page: dict[str, tuple[int, int]] = {}
    t30_left = maps["f70v2"]
    t30_right = maps["f72r2"]
    left_signature_positions: dict[str, list[int]] = defaultdict(list)
    right_signature_positions: dict[str, list[int]] = defaultdict(list)
    for member, row in t30_left.items():
        left_signature_positions[row["canonical_boundary_family"]].append(member)
    for member, row in t30_right.items():
        right_signature_positions[row["canonical_boundary_family"]].append(member)
    for signature in sorted(set(left_signature_positions) & set(right_signature_positions)):
        if len(left_signature_positions[signature]) == len(right_signature_positions[signature]) == 1:
            unique_cross_page[signature] = (left_signature_positions[signature][0], right_signature_positions[signature][0])
    distance_rows: list[dict[str, Any]] = []
    for left_signature, right_signature in combinations(sorted(unique_cross_page), 2):
        left_a1, right_a1 = unique_cross_page[left_signature]
        left_a2, right_a2 = unique_cross_page[right_signature]
        signed_left = signed_circular_delta(left_a1, left_a2)
        signed_right = signed_circular_delta(right_a1, right_a2)
        distance_rows.append(
            {
                "left_signature": left_signature,
                "right_signature": right_signature,
                "f70_left_a": left_a1,
                "f70_right_a": left_a2,
                "f72_left_a": right_a1,
                "f72_right_a": right_a2,
                "f70_signed_distance": signed_left,
                "f72_signed_distance": signed_right,
                "f70_unsigned_distance": abs(signed_left),
                "f72_unsigned_distance": abs(signed_right),
                "absolute_distance_difference": abs(abs(signed_left) - abs(signed_right)),
                "candidate": "SIX_TO_SEVEN_MEMBER_INTERVAL" if abs(abs(signed_left) - abs(signed_right)) <= 1 else "NO_STABLE_INTERVAL",
                "evidence_status": "ANALYTICAL_CATALOGUE_DISTANCE__NOT_GDT388_EXTERNAL_RELATION_EDGE",
                "component_export_credit": "ZERO",
            }
        )
    write_tsv(out / OUTPUT_NAMES[7], distance_rows)

    card_specs = {
        "f70v1.5": ("Bezeichnung der T15-Stelle 09A / äußerer Ringplatz 4 von 10", "C1_CONTEXTUAL_POSITION", "SELECTED_CONTEXT_CARD"),
        "f72r1.5": ("Bezeichnung der T15-Stelle 09A / äußerer Ringplatz 4 von 10", "C1_CONTEXTUAL_POSITION", "SELECTED_CONTEXT_CARD"),
        "f70v1.14": ("Bezeichnung einer frühen inneren T15-Stelle, hier 02A", "C0_CONTEXTUAL_WINDOW", "SELECTED_CONTEXT_CARD"),
        "f71v.15": ("Bezeichnung einer frühen inneren T15-Stelle, hier 03A", "C0_CONTEXTUAL_WINDOW", "SELECTED_CONTEXT_CARD"),
        "f70v2.31": ("T30-Stelle 10A; Gegenbeleg gegen eine freie AQABAG=02-03-Lesung", "COUNTEREXAMPLE", "NO_RENDERER_LICENSE"),
    }
    cards: list[dict[str, Any]] = []
    atlas_by_locus = {row["locus"]: row for row in atlas_rows}
    if set(card_specs) - set(atlas_by_locus):
        raise RuntimeError("contextual position card locus changed")
    for locus, (display, confidence, license_state) in card_specs.items():
        row = atlas_by_locus[locus]
        cards.append(
            {
                "locus": locus,
                "physical_folio": row["physical_folio"],
                "source_selector": row["source_selector"],
                "template_id": row["template_id"],
                "kluge_a_member": row["kluge_a_member"],
                "complete_label_surface": row["complete_label_surface"],
                "canonical_boundary_family": row["canonical_boundary_family"],
                "zl_member_sequence": row["zl_member_sequence"],
                "working_default_de": display,
                "confidence": confidence,
                "evidence": (
                    "dieselbe vollständige Familien-Signatur liegt auf einem anderen physischen T15-Folio an gleicher oder benachbarter A-Stelle"
                    if license_state == "SELECTED_CONTEXT_CARD"
                    else "dieselbe AQABAG-Signatur erscheint außerhalb T15 an 10A"
                ),
                "counterevidence": (
                    "die beiden 09A-Belege stimmen nur auf Familienebene überein; ihre vollständigen "
                    "Quellmitgliedsfolgen enden B2 versus B3; Kluge-A ist Kataloghomologie, kein "
                    "bewiesener Autorenzahlenwert"
                    if row["canonical_boundary_family"] == "AQABAB"
                    else "nur zwei Ankerfamilien; Kluge-A ist Kataloghomologie, kein bewiesener Autorenzahlenwert"
                ),
                "renderer_license": license_state,
                "prose_export_allowed": "NO",
                "component_export_credit": "ZERO",
                "confirmed_lexeme": "NO",
            }
        )
    write_tsv(out / OUTPUT_NAMES[8], cards)

    model_specs = {row["model_id"]: row for row in read_tsv(MODEL_SPECS)}
    decisions = {
        "FULL_FAMILY_A_CODE": ("NO", "FAIL", "26 held targets but only four have any exact-A support; just two signature anchors provide those hits"),
        "T15_TWO_ANCHOR_SEED": ("RIVAL", "RETAIN_CONTEXT_CARDS", "AQABAB repeats at 09A and AQABAG at adjacent 02A/03A, but their required shifts differ"),
        "SHARED_DIAGRAM_TRANSFORM": ("NO", "FAIL", "best exact family count is one on T15 and two on T30, not three"),
        "RELATIVE_FAMILY_DISTANCE": ("RIVAL", "ONE_PM1_PAIR_ONLY", "AQABAC-AQABBA spans seven versus six A-members; no external relation edge"),
        "FAMILY_SIMILARITY_TEXTURE": ("RIVAL", "WEAK", "family edit ranking improves on visible surface but remains a weak non-unique position texture"),
        "LEARNED_MEMBER_PLUS_GRAPHIC_LAYER": ("YES", "SELECTED_PRIMARY", "74 family signatures and broad cross-position collisions favor individual learned designations plus graphical class material"),
    }
    adjudication: list[dict[str, Any]] = []
    for model_id in model_specs:
        selected, gate, evidence = decisions[model_id]
        spec = model_specs[model_id]
        adjudication.append(
            {
                "model_id": model_id,
                "unit": spec["unit"],
                "concrete_interpretation": spec["concrete_interpretation"],
                "selection_requirement": spec["selection_requirement"],
                "selected_working_model": selected,
                "gate_result": gate,
                "evidence_and_counterevidence": evidence,
                "component_export_credit": "ZERO",
                "confirmed_lexeme": "NO",
            }
        )
    write_tsv(out / OUTPUT_NAMES[9], adjudication)
    write_tsv(out / OUTPUT_NAMES[10], [], EDGE_COLUMNS)

    indexed_rows = list(enumerate(atlas_rows))
    same_k_edges = [
        (left_index, right_index)
        for (left_index, left), (right_index, right) in combinations(indexed_rows, 2)
        if left["source_selector"] != right["source_selector"]
        and left["kluge_a_member"] == right["kluge_a_member"]
    ]
    local_edges: list[tuple[int, int]] = []
    by_array_indices: dict[str, list[int]] = defaultdict(list)
    for index, row in indexed_rows:
        by_array_indices[row["array_id"]].append(index)
    for indices in by_array_indices.values():
        ordered = sorted(indices, key=lambda index: int(atlas_rows[index]["slot_index"]))
        for left_index, right_index in zip(ordered, ordered[1:]):
            if int(atlas_rows[right_index]["slot_index"]) == int(atlas_rows[left_index]["slot_index"]) + 1:
                local_edges.append((left_index, right_index))
    if len(same_k_edges) != 156 or len(local_edges) != 87:
        raise RuntimeError("homolog or local-edge capacity changed")

    order_rows: list[dict[str, Any]] = []
    order_rng = random.Random(795004)
    for field, representation_id in (
        ("zl_member_sequence", "ZL_MEMBER_SEQUENCE"),
        ("canonical_boundary_family", "BOUNDARY_FAMILY"),
        ("transferred_prefix", "TRANSFERRED_PREFIX"),
        ("strict_residual", "FORMAL_RESIDUAL"),
    ):
        values = [str(row[field]) for row in atlas_rows]
        for scope, edges, grouping_field in (
            ("CROSS_CHART_SAME_K", same_k_edges, "source_selector"),
            ("CONSECUTIVE_SOURCE_SLOT", local_edges, "array_id"),
        ):
            observed = sum(values[left] == values[right] for left, right in edges)
            groups: dict[str, list[int]] = defaultdict(list)
            for index, row in enumerate(atlas_rows):
                groups[str(row[grouping_field])].append(index)
            null_counts: list[int] = []
            for _ in range(5000):
                shuffled = list(values)
                for indices in groups.values():
                    local_values = [shuffled[index] for index in indices]
                    order_rng.shuffle(local_values)
                    for index, value in zip(indices, local_values):
                        shuffled[index] = value
                null_counts.append(sum(shuffled[left] == shuffled[right] for left, right in edges))
            order_rows.append(
                {
                    "scope": scope,
                    "representation_id": representation_id,
                    "edge_count": len(edges),
                    "observed_exact_matches": observed,
                    "observed_match_rate": f6(observed / len(edges)),
                    "null_iterations": len(null_counts),
                    "null_mean_matches": f6(sum(null_counts) / len(null_counts)),
                    "null_p_matches_ge_observed": f6((1 + sum(value >= observed for value in null_counts)) / (len(null_counts) + 1)),
                    "interpretation": (
                        "LOCAL_GRAPHICAL_PREFIX_BLOCKING"
                        if scope == "CONSECUTIVE_SOURCE_SLOT" and representation_id == "TRANSFERRED_PREFIX"
                        else "NO_POSITIVE_FIXED_K_CONTENT_KEY"
                    ),
                    "semantic_export": "NONE",
                }
            )
    write_tsv(out / OUTPUT_NAMES[11], order_rows)

    boundary_metrics = exact_metrics(boundary_predictions)
    boundary_sim_metrics = similarity_metrics(boundary_similarity)
    status = (
        "PARTIAL__101_KLUGE_LOCI__394_GUARDED_GROUP_ROWS__2122_SEALED_ROWS_REJECTED_PRE_MATERIALIZATION__"
        "81_ALL3_BOUNDARY__11_BOUNDARY_ONLY_DISAGREEMENTS__9_FAMILY_DISAGREEMENTS_RESOLVED_2OF3__"
        "55_ALL3_MEMBER_SEQUENCES__74_BOUNDARY_SIGNATURES__73_COMPACT_SIGNATURES__11_RECURRENT__"
        "26_EXACT_LOFO_TARGETS__4_ANY_EXACT_A__6_ANY_PM1__ZERO_EXACT_MEMBER_SAME_K__"
        "T15_TWO_CONTEXTUAL_ANCHORS__SHARED_TRANSFORMS_FAIL__LOCAL_PREFIX_BLOCKING_35_OF_87__WEAK_FAMILY_TEXTURE__"
        "LEARNED_MEMBER_PLUS_GRAPHICAL_LAYER_PRIMARY__ZERO_COMPONENT_EXPORT__ZERO_CONFIRMED_LEXEMES"
    )
    result = {
        "experiment_id": "GDT795",
        "status": status,
        "scope": {
            "admitted_kluge_loci": 101,
            "physical_folios": 3,
            "source_selectors": 5,
            "new_pages_or_images_opened": 0,
            "mixed_sources_queried": 1,
            "guard_selected_rows": guard_stats["selected"],
            "sealed_rows_rejected_before_materialization": guard_stats["skipped_forbidden"],
            "sealed_rows_materialized": 0,
        },
        "counts": {
            "all3_boundary_and_family": 81,
            "all3_family_boundary_majority": 11,
            "family_two_of_three": 9,
            "all3_member_sequences": 55,
            "member_sequence_two_of_three": 36,
            "member_sequence_all_different": 10,
            "canonical_family_signatures": len(by_signature),
            "compact_family_signatures": len({row["canonical_compact_family"] for row in atlas_rows}),
            "visible_complete_surfaces": len({row["complete_label_surface"] for row in atlas_rows}),
            "recurrent_family_signatures": len(recurrent),
            "recurrent_family_events": sum(len(rows) for rows in recurrent.values()),
            "exact_boundary_lofo_targets": int(boundary_metrics["target_count"]),
            "exact_boundary_any_exact_a": int(boundary_metrics["any_exact"]),
            "exact_boundary_any_pm1": int(boundary_metrics["any_pm1"]),
            "similarity_targets": int(boundary_sim_metrics["target_count"]),
            "contextual_position_cards": len(cards),
            "selected_context_cards": sum(row["renderer_license"] == "SELECTED_CONTEXT_CARD" for row in cards),
            "cross_chart_same_k_pairs": len(same_k_edges),
            "consecutive_source_slot_edges": len(local_edges),
            "consecutive_same_prefix_edges": next(
                int(row["observed_exact_matches"])
                for row in order_rows
                if row["scope"] == "CONSECUTIVE_SOURCE_SLOT" and row["representation_id"] == "TRANSFERRED_PREFIX"
            ),
            "component_exports": 0,
            "confirmed_lexemes": 0,
        },
        "decision": {
            "full_family_position_codebook": "NOT_SELECTED",
            "t15_two_anchor_seed": "RETAIN_CONTEXTUAL_COMPLETE_SIGNATURE_CARDS",
            "shared_diagram_transform": "NOT_SELECTED",
            "relative_distance": "ONE_SIX_TO_SEVEN_MEMBER_RIVAL__NOT_EXTERNAL_RELATION_EVIDENCE",
            "family_similarity": "WEAK_FORM_TEXTURE_ONLY",
            "local_prefix_blocking": "SELECTED_AS_GRAPHICAL_RENDERER_STRUCTURE_NOT_CONTENT",
            "same_k_member_identity": "ZERO_OF_156_CROSS_CHART_PAIRS",
            "selected_primary_model": "LEARNED_MEMBER_PLUS_GRAPHICAL_LAYER",
            "next": "TEST_T15_POSITION_CARDS_AGAINST_VISIBLE_FIGURE_ATTRIBUTES_AND_RUNNING_PROSE_HOSTS_WITHOUT_EXPORTING_FAMILY_COMPONENTS",
        },
    }
    (out / OUTPUT_NAMES[12]).write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(status)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
