#!/usr/bin/env python3
"""Independent integration validator for the public GDT615 Stage-0 bundle.

This module deliberately imports no GDT615 implementation module.  Its semantic
inputs are limited to REGISTERED_SEARCH.json, REGISTERED_TRAIN_SUBSTRINGS.txt,
merge_tree.tsv, and the published artifacts/stage0 files.  Source files named
by STAGE0_BUNDLE.json are opened only as opaque byte streams for the explicitly
registered size/SHA-256 checks; they are never imported, parsed, or executed.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import itertools
import json
import os
import sys
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence


SCHEMA = "gdt615-stage0-integration-validation-v1"
MERGE_COUNT = 64
PAID_BUDGET = 8
ALL_MERGES = (1 << MERGE_COUNT) - 1

STAGE0_JSON_FILES = {
    "bundle": "STAGE0_BUNDLE.json",
    "commit": "STAGE0_MAPPING_COMMIT.json",
    "decisive": "DECISIVE_QUERY_MANIFEST.json",
    "independent": "INDEPENDENT_RESULT.json",
    "input_manifest": "PRIMARY_INPUT_MANIFEST.json",
    "primary": "PRIMARY_RESULT.json",
    "replay": "STAGE0_REPLAY_CERTIFICATE.json",
    "scout": "SCOUT_RESULT.json",
    "scout_candidate_replay": "SCOUT_CANDIDATE_001_REPLAY.json",
}

STAGE0_BYTE_FILES = {
    "base_encoding": "PRIMARY_BASE_ENCODING.smt2",
    "query_log": "PRIMARY_QUERY_CERTIFICATES.jsonl",
    "mapping_tsv": "mapping.tsv",
    "cover_tsv": "minimum_cover.tsv",
    "raw_merges_tsv": "raw_merges.tsv",
}

OPAQUE_BUNDLE_SOURCE_ALLOWLIST = {
    "experiments/yolo/gdt615_joint_output_permutation_recovery/src/primary/solve.py",
    "experiments/yolo/gdt615_joint_output_permutation_recovery/src/primary/test_solve.py",
    "experiments/yolo/gdt615_joint_output_permutation_recovery/src/independent/stage0_independent.cpp",
    "experiments/yolo/gdt615_joint_output_permutation_recovery/src/independent/Makefile",
    "experiments/yolo/gdt615_joint_output_permutation_recovery/src/finalize_stage0.py",
}


class ValidationError(RuntimeError):
    pass


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> tuple[int, str]:
    digest = hashlib.sha256()
    size = 0
    with path.open("rb") as handle:
        while True:
            block = handle.read(1 << 20)
            if not block:
                break
            size += len(block)
            digest.update(block)
    return size, digest.hexdigest()


def load_json_bytes(data: bytes, label: str) -> Any:
    try:
        return json.loads(data.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValidationError(f"invalid JSON in {label}: {exc}") from exc


def load_tsv_bytes(data: bytes, label: str) -> list[dict[str, str]]:
    try:
        text = data.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise ValidationError(f"invalid UTF-8 in {label}") from exc
    reader = csv.DictReader(text.splitlines(), delimiter="\t")
    if reader.fieldnames is None:
        raise ValidationError(f"missing TSV header in {label}")
    rows = list(reader)
    if any(None in row for row in rows):
        raise ValidationError(f"ragged TSV row in {label}")
    return rows


def compact_evidence(value: Any) -> Any:
    """Keep small evidence inline and content-address large successful matches."""
    payload = json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=True
    ).encode("utf-8")
    if len(payload) <= 768:
        return value
    evidence: dict[str, Any] = {
        "canonical_json_bytes": len(payload),
        "kind": type(value).__name__,
        "sha256": sha256_bytes(payload),
    }
    if isinstance(value, (list, dict)):
        evidence["item_count"] = len(value)
    return evidence


class CheckRecorder:
    def __init__(self) -> None:
        self.rows: list[dict[str, Any]] = []

    def add(self, check_id: str, passed: bool, evidence: Any | None = None) -> None:
        if any(row["check_id"] == check_id for row in self.rows):
            raise ValidationError(f"duplicate check ID: {check_id}")
        row: dict[str, Any] = {"check_id": check_id, "passed": bool(passed)}
        if evidence is not None:
            row["evidence"] = evidence
        self.rows.append(row)

    def equal(self, check_id: str, observed: Any, expected: Any) -> None:
        passed = observed == expected
        if passed:
            evidence = {"matched": compact_evidence(observed)}
        else:
            evidence = {
                "observed": compact_evidence(observed),
                "expected": compact_evidence(expected),
            }
        self.add(check_id, passed, evidence)

    @property
    def passed(self) -> bool:
        return all(row["passed"] for row in self.rows)


@dataclass(frozen=True)
class MergeRow:
    rank: int
    left: str
    right: str
    merged: str
    leaves: tuple[str, ...]
    subtree_mask: int
    depth: int


@dataclass(frozen=True)
class RenderedMerge:
    rank: int
    merge: str
    leaves: tuple[str, ...]
    raw_render: str
    supported: bool
    subtree_ranks: tuple[int, ...]

    def primary_dict(self) -> dict[str, Any]:
        return {
            "rank": self.rank,
            "merge": self.merge,
            "leaves": list(self.leaves),
            "raw_render": self.raw_render,
            "train_substring_member": self.supported,
            "inclusive_recursive_merge_subtree_ranks": list(self.subtree_ranks),
        }


class ExactCover:
    """Exhaustive inclusive-DAG set cover with deterministic lexicographic replay."""

    def __init__(self, subtree_masks: Sequence[int]) -> None:
        if len(subtree_masks) != MERGE_COUNT:
            raise ValidationError("cover solver requires exactly 64 merge subtrees")
        self.subtree_masks = tuple(subtree_masks)
        covers = [0] * MERGE_COUNT
        for paid in range(MERGE_COUNT):
            bit = 1 << paid
            for affected, subtree in enumerate(subtree_masks):
                if subtree & bit:
                    covers[paid] |= 1 << affected
        self.covers = tuple(covers)

    def _exists_factory(self) -> tuple[Any, dict[str, int]]:
        stats = {"states": 0}

        @lru_cache(maxsize=None)
        def exists(uncovered: int, available: int, slots: int) -> bool:
            stats["states"] += 1
            if uncovered == 0:
                return True
            if slots <= 0 or available == 0:
                return False

            union_cover = 0
            max_gain = 0
            bits = available
            while bits:
                low = bits & -bits
                candidate = low.bit_length() - 1
                relevant = self.covers[candidate] & uncovered
                union_cover |= relevant
                max_gain = max(max_gain, relevant.bit_count())
                bits ^= low
            if uncovered & ~union_cover:
                return False
            if max_gain == 0 or (uncovered.bit_count() + max_gain - 1) // max_gain > slots:
                return False

            pivot = -1
            pivot_choices = MERGE_COUNT + 1
            bits = uncovered
            while bits:
                low = bits & -bits
                element = low.bit_length() - 1
                choices = (self.subtree_masks[element] & available).bit_count()
                if choices < pivot_choices:
                    pivot = element
                    pivot_choices = choices
                bits ^= low
            if pivot < 0 or pivot_choices == 0:
                return False

            pivot_candidates = self.subtree_masks[pivot] & available
            branch_available = available
            while pivot_candidates:
                low = pivot_candidates & -pivot_candidates
                candidate = low.bit_length() - 1
                if exists(
                    uncovered & ~self.covers[candidate],
                    branch_available & ~low,
                    slots - 1,
                ):
                    return True
                branch_available &= ~low
                pivot_candidates ^= low
            return False

        return exists, stats

    def solve(self, unsupported: int) -> dict[str, Any]:
        total_states = 0
        minimum = None
        for size in range(MERGE_COUNT + 1):
            exists, stats = self._exists_factory()
            possible = exists(unsupported, ALL_MERGES, size)
            total_states += stats["states"]
            if possible:
                minimum = size
                break
        if minimum is None:
            raise ValidationError("inclusive-DAG cover unexpectedly infeasible")

        chosen: list[int] = []
        uncovered = unsupported
        previous = -1
        lex_states = 0
        for position in range(minimum):
            remaining = minimum - position - 1
            selected = False
            for candidate in range(previous + 1, MERGE_COUNT):
                if MERGE_COUNT - candidate - 1 < remaining:
                    break
                after = uncovered & ~self.covers[candidate]
                available = 0 if candidate == MERGE_COUNT - 1 else ALL_MERGES ^ ((1 << (candidate + 1)) - 1)
                exists, stats = self._exists_factory()
                possible = exists(after, available, remaining)
                lex_states += stats["states"]
                if possible:
                    chosen.append(candidate + 1)
                    uncovered = after
                    previous = candidate
                    selected = True
                    break
            if not selected:
                raise ValidationError("could not reconstruct lexicographic minimum cover")
        if uncovered:
            raise ValidationError("lexicographic cover leaves unsupported merge uncovered")
        return {
            "minimum": minimum,
            "lex_ranks": chosen,
            "k_minus_one_excluded": True,
            "exhaustive_states": total_states + lex_states,
        }


def expected_deck(registered: Mapping[str, Any]) -> tuple[list[dict[str, str]], dict[str, dict[str, Any]]]:
    slots = registered["primitive_role_assignment"]
    if not isinstance(slots, list):
        raise ValidationError("primitive_role_assignment must be a list")
    deck_by_card: dict[str, dict[str, Any]] = {}
    for role, cards in registered["primitive_output_deck"].items():
        for source in cards:
            record = dict(source)
            record["role"] = role
            record["derived_length"] = len(record["output"])
            card_id = record["card_id"]
            if card_id in deck_by_card:
                raise ValidationError(f"duplicate registered card ID: {card_id}")
            deck_by_card[card_id] = record
    return slots, deck_by_card


def validate_mapping(
    rows: Sequence[Mapping[str, Any]],
    slots: Sequence[Mapping[str, str]],
    deck_by_card: Mapping[str, Mapping[str, Any]],
    *,
    require_length: bool,
    require_license_metadata: bool,
) -> tuple[list[dict[str, str]], list[str]]:
    errors: list[str] = []
    normalized: list[dict[str, str]] = []
    if len(rows) != len(slots):
        errors.append(f"mapping row count {len(rows)} != {len(slots)}")
    seen_primitives: set[str] = set()
    seen_cards: set[str] = set()
    for index, row in enumerate(rows):
        if index >= len(slots):
            errors.append("mapping contains extra row")
            continue
        slot = slots[index]
        primitive_id = str(row.get("primitive_id", ""))
        role = str(row.get("role", ""))
        card_id = str(row.get("card_id", ""))
        output = str(row.get("output", ""))
        if primitive_id != slot["primitive_id"]:
            errors.append(f"row {index}: primitive order/id mismatch")
        if role != slot["role"]:
            errors.append(f"{primitive_id}: slot role mismatch")
        if primitive_id in seen_primitives:
            errors.append(f"duplicate primitive {primitive_id}")
        seen_primitives.add(primitive_id)
        if card_id in seen_cards:
            errors.append(f"duplicate card {card_id}")
        seen_cards.add(card_id)
        card = deck_by_card.get(card_id)
        if card is None:
            errors.append(f"unknown card {card_id}")
        else:
            if role != card["role"]:
                errors.append(f"{primitive_id}: card role mismatch")
            if output != card["output"]:
                errors.append(f"{primitive_id}: card output mismatch")
            if require_length and int(row.get("length", -1)) != card["derived_length"]:
                errors.append(f"{primitive_id}: derived length mismatch")
            if require_license_metadata:
                expected_license = card.get("side_license")
                observed_license = row.get("side_license")
                if expected_license != observed_license:
                    errors.append(f"{primitive_id}: side-license metadata mismatch")
        normalized.append(
            {
                "primitive_id": primitive_id,
                "role": role,
                "card_id": card_id,
                "output": output,
            }
        )
    expected_cards = set(deck_by_card)
    if seen_cards != expected_cards:
        errors.append("mapping card set is not the complete registered deck")
    return normalized, errors


def parse_merge_tree(data: bytes, primitive_ids: set[str]) -> list[MergeRow]:
    rows = load_tsv_bytes(data, "merge_tree.tsv")
    expected_header = [
        "rank", "left", "right", "merged", "train_occurrences",
        "leaf_sequence", "leaf_count", "tree_depth",
    ]
    if not rows or list(rows[0]) != expected_header:
        raise ValidationError("unexpected merge_tree.tsv header")
    unit_leaves: dict[str, tuple[str, ...]] = {primitive: (primitive,) for primitive in primitive_ids}
    unit_subtree: dict[str, int] = {primitive: 0 for primitive in primitive_ids}
    unit_depth: dict[str, int] = {primitive: 0 for primitive in primitive_ids}
    result: list[MergeRow] = []
    for index, row in enumerate(rows, start=1):
        rank = int(row["rank"])
        if rank != index:
            raise ValidationError("merge ranks are not exactly 1..64")
        left, right, merged = row["left"], row["right"], row["merged"]
        if left not in unit_leaves or right not in unit_leaves:
            raise ValidationError(f"rank {rank}: non-topological child")
        leaves = unit_leaves[left] + unit_leaves[right]
        declared_leaves = tuple(row["leaf_sequence"].split())
        if leaves != declared_leaves or int(row["leaf_count"]) != len(leaves):
            raise ValidationError(f"rank {rank}: recursive leaf sequence mismatch")
        depth = max(unit_depth[left], unit_depth[right]) + 1
        if int(row["tree_depth"]) != depth:
            raise ValidationError(f"rank {rank}: tree depth mismatch")
        subtree = (1 << (rank - 1)) | unit_subtree[left] | unit_subtree[right]
        if merged in unit_leaves:
            raise ValidationError(f"rank {rank}: duplicate merged unit")
        unit_leaves[merged] = leaves
        unit_subtree[merged] = subtree
        unit_depth[merged] = depth
        result.append(MergeRow(rank, left, right, merged, leaves, subtree, depth))
    if len(result) != MERGE_COUNT:
        raise ValidationError(f"expected 64 merges, got {len(result)}")
    return result


def reconstruct_merges(
    merges: Sequence[MergeRow],
    mapping: Sequence[Mapping[str, str]],
    substrings: set[str],
) -> list[RenderedMerge]:
    output_by_primitive = {row["primitive_id"]: row["output"] for row in mapping}
    unit_render = dict(output_by_primitive)
    result: list[RenderedMerge] = []
    for merge in merges:
        if merge.left not in unit_render or merge.right not in unit_render:
            raise ValidationError(f"rank {merge.rank}: render child unavailable")
        render = unit_render[merge.left] + unit_render[merge.right]
        direct_leaf_render = "".join(output_by_primitive[primitive] for primitive in merge.leaves)
        if render != direct_leaf_render:
            raise ValidationError(f"rank {merge.rank}: recursive/direct render mismatch")
        unit_render[merge.merged] = render
        subtree_ranks = tuple(index + 1 for index in range(MERGE_COUNT) if merge.subtree_mask & (1 << index))
        result.append(
            RenderedMerge(
                rank=merge.rank,
                merge=merge.merged,
                leaves=merge.leaves,
                raw_render=render,
                supported=render in substrings,
                subtree_ranks=subtree_ranks,
            )
        )
    return result


def positional_negative_mapping(
    registered: Mapping[str, Any],
    slots: Sequence[Mapping[str, str]],
) -> list[dict[str, str]]:
    slots_by_role: dict[str, list[Mapping[str, str]]] = {}
    for slot in slots:
        slots_by_role.setdefault(slot["role"], []).append(slot)
    assigned: dict[str, dict[str, str]] = {}
    for role, role_slots in slots_by_role.items():
        cards = registered["primitive_output_deck"][role]
        if len(cards) != len(role_slots):
            raise ValidationError(f"negative-control positional mismatch in role {role}")
        for slot, card in zip(role_slots, cards):
            assigned[slot["primitive_id"]] = {
                "primitive_id": slot["primitive_id"],
                "role": role,
                "card_id": card["card_id"],
                "output": card["output"],
            }
    return [assigned[slot["primitive_id"]] for slot in slots]


def canonical_primary_raw(rows: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    return [
        {
            "rank": int(row["rank"]),
            "merge": row["merge"],
            "leaves": list(row["leaves"]),
            "raw_render": row["raw_render"],
            "train_substring_member": bool(row["train_substring_member"]),
            "inclusive_recursive_merge_subtree_ranks": list(row["inclusive_recursive_merge_subtree_ranks"]),
        }
        for row in rows
    ]


def canonical_tsv_raw(rows: Sequence[Mapping[str, str]]) -> list[dict[str, Any]]:
    return [
        {
            "rank": int(row["rank"]),
            "merge": row["merge"],
            "leaves": row["leaves"].split(",") if row["leaves"] else [],
            "raw_render": row["raw_render"],
            "train_substring_member": row["train_substring_member"] == "1",
            "inclusive_recursive_merge_subtree_ranks": [
                int(value) for value in row["inclusive_subtree_ranks"].split(",") if value
            ],
        }
        for row in rows
    ]


def safe_repo_path(repo_root: Path, relative: str) -> Path:
    candidate = (repo_root / relative).resolve()
    root = repo_root.resolve()
    try:
        candidate.relative_to(root)
    except ValueError as exc:
        raise ValidationError(f"bundle path escapes repository: {relative}") from exc
    return candidate


def expected_decisive_queries(mapping_ids: list[str]) -> dict[str, dict[str, Any]]:
    base = [
        "same-role card-to-primitive bijection over all 34 slots",
        "exact registered train-substring MDD membership for all 64 raw renders",
        "for each unsupported render, at least one hit in its inclusive merge subtree",
        "at most 8 merge-node hits",
    ]
    key = repr(mapping_ids)
    return {
        "Q0001": {
            "claim": "existence", "phase": "existence", "result": "sat",
            "constraint": {"core_hit_maximum": 8}, "context": base,
        },
        "Q0006": {
            "claim": "support_55_exists", "phase": "support_boundary_sat", "result": "sat",
            "constraint": {"support_at_least": 55}, "context": base + ["support >= 55"],
        },
        "Q0007": {
            "claim": "support_56_excluded", "phase": "support_boundary_unsat", "result": "unsat",
            "constraint": {"support_at_least": 56}, "context": base + ["support >= 56"],
        },
        "Q0011": {
            "claim": "cover_4_exists_at_support_55", "phase": "cover_boundary_sat", "result": "sat",
            "constraint": {"core_hit_at_most": 4}, "context": base + ["support = 55", "hit count <= 4"],
        },
        "Q0012": {
            "claim": "cover_3_excluded_at_support_55", "phase": "cover_boundary_unsat", "result": "unsat",
            "constraint": {"core_hit_at_most": 3}, "context": base + ["support = 55", "hit count <= 3"],
        },
        "Q0190": {
            "claim": "final_key_exists", "phase": "final_key_sat", "result": "sat",
            "constraint": {"minimum_cover": 4, "support": 55},
            "context": base + ["support = 55", "hit count <= 4", f"card-ID key = {key}"],
        },
        "Q0191": {
            "claim": "earlier_key_excluded", "phase": "lexicographic_key_predecessor_unsat", "result": "unsat",
            "constraint": {"core_hit_at_most": 4, "key_less_than": mapping_ids, "support": 55},
            "context": base + ["support = 55", "hit count <= 4", f"card-ID key lexicographically precedes {key}"],
        },
        "Q0192": {
            "claim": "canonical_cover_exists", "phase": "canonical_cover_sat", "result": "sat",
            "constraint": {"ascending_merge_ranks": [2, 3, 14, 23]},
            "context": base + ["support = 55", "hit count = 4", f"card-ID key = {key}", "ascending cover tuple = [2, 3, 14, 23]"],
        },
        "Q0193": {
            "claim": "earlier_cover_excluded", "phase": "canonical_cover_predecessor_unsat", "result": "unsat",
            "constraint": {"tuple_less_than": [2, 3, 14, 23]},
            "context": base + ["support = 55", "hit count = 4", f"card-ID key = {key}", "ascending cover tuple lexicographically precedes [2, 3, 14, 23]"],
        },
    }


def run_validation(
    repo_root: Path,
    registered_path: Path,
    substring_path: Path,
    merge_path: Path,
    stage0_dir: Path,
) -> dict[str, Any]:
    checks = CheckRecorder()

    for path, basename in (
        (registered_path, "REGISTERED_SEARCH.json"),
        (substring_path, "REGISTERED_TRAIN_SUBSTRINGS.txt"),
        (merge_path, "merge_tree.tsv"),
    ):
        if path.name != basename:
            raise ValidationError(f"unexpected admitted input basename: {path.name}")

    registered_bytes = registered_path.read_bytes()
    substring_bytes = substring_path.read_bytes()
    merge_bytes = merge_path.read_bytes()
    registered = load_json_bytes(registered_bytes, registered_path.name)

    stage_json_bytes: dict[str, bytes] = {}
    stage_json: dict[str, Any] = {}
    for label, filename in STAGE0_JSON_FILES.items():
        data = (stage0_dir / filename).read_bytes()
        stage_json_bytes[label] = data
        stage_json[label] = load_json_bytes(data, filename)
    stage_bytes = {
        label: (stage0_dir / filename).read_bytes()
        for label, filename in STAGE0_BYTE_FILES.items()
    }

    actual_input_hashes = {
        "REGISTERED_SEARCH.json": sha256_bytes(registered_bytes),
        "REGISTERED_TRAIN_SUBSTRINGS.txt": sha256_bytes(substring_bytes),
        "merge_tree.tsv": sha256_bytes(merge_bytes),
    }
    registered_merge_hash = next(
        row["sha256"] for row in registered["registered_inputs"]
        if Path(row["path"]).name == "merge_tree.tsv"
    )
    checks.equal(
        "input.registered_train_substring_hash",
        actual_input_hashes["REGISTERED_TRAIN_SUBSTRINGS.txt"],
        registered["registered_train_substrings"]["sha256"],
    )
    checks.equal("input.registered_merge_tree_hash", actual_input_hashes["merge_tree.tsv"], registered_merge_hash)

    input_hash_claims = {
        "primary_result": stage_json["primary"]["input_hashes"],
        "independent_result": stage_json["independent"]["input_sha256"],
        "mapping_commit": stage_json["commit"]["registered_input_sha256"],
        "primary_input_manifest": {
            key: stage_json["input_manifest"][key] for key in actual_input_hashes
        },
        "scout_result": {
            Path(key).name: value
            for key, value in stage_json["scout"]["registered_input_hashes"].items()
        },
    }
    for label, claimed in input_hash_claims.items():
        checks.equal(f"input.hash_consensus.{label}", claimed, actual_input_hashes)

    try:
        substring_text = substring_bytes.decode("ascii")
    except UnicodeDecodeError as exc:
        raise ValidationError("registered train substrings are not ASCII") from exc
    substring_lines = substring_text.splitlines()
    substring_set = set(substring_lines)
    sorted_substrings = sorted(substring_lines, key=lambda value: (len(value.encode("ascii")), value.encode("ascii")))
    substring_meta = registered["registered_train_substrings"]
    substring_contract = (
        len(substring_lines) == substring_meta["distinct_substring_count"] == 28101
        and len(substring_set) == len(substring_lines)
        and substring_lines == sorted_substrings
        and all(1 <= len(value) <= 12 and value.isascii() and value.islower() and value.isalpha() for value in substring_lines)
        and min(map(len, substring_lines)) == substring_meta["minimum_length"] == 1
        and max(map(len, substring_lines)) == substring_meta["maximum_length"] == 12
    )
    checks.add(
        "input.train_substring_contract",
        substring_contract,
        {"distinct": len(substring_set), "minimum_length": min(map(len, substring_lines)), "maximum_length": max(map(len, substring_lines))},
    )

    slots, deck_by_card = expected_deck(registered)
    checks.add(
        "deck.registered_capacity_and_uniqueness",
        len(slots) == 34
        and len({row["primitive_id"] for row in slots}) == 34
        and len(deck_by_card) == 34
        and len({card["output"] for card in deck_by_card.values() if card["output"]}) == 33,
        {"primitive_slots": len(slots), "cards": len(deck_by_card)},
    )

    primary_mapping, primary_mapping_errors = validate_mapping(
        stage_json["primary"]["mapping"], slots, deck_by_card,
        require_length=True, require_license_metadata=True,
    )
    independent_mapping, independent_mapping_errors = validate_mapping(
        stage_json["independent"]["mapping"], slots, deck_by_card,
        require_length=False, require_license_metadata=False,
    )
    commit_mapping, commit_mapping_errors = validate_mapping(
        stage_json["commit"]["mapping"], slots, deck_by_card,
        require_length=True, require_license_metadata=True,
    )
    mapping_tsv_rows = load_tsv_bytes(stage_bytes["mapping_tsv"], "mapping.tsv")
    tsv_mapping, tsv_mapping_errors = validate_mapping(
        mapping_tsv_rows, slots, deck_by_card,
        require_length=True, require_license_metadata=False,
    )
    for label, errors in (
        ("primary", primary_mapping_errors),
        ("independent", independent_mapping_errors),
        ("commit", commit_mapping_errors),
        ("mapping_tsv", tsv_mapping_errors),
    ):
        checks.add(f"mapping.role_bijection_and_metadata.{label}", not errors, errors or {"rows": 34})
    checks.add(
        "mapping.full_primary_cpp_commit_tsv_match",
        primary_mapping == independent_mapping == commit_mapping == tsv_mapping,
        {"card_id_sequence": [row["card_id"] for row in primary_mapping]},
    )

    merges = parse_merge_tree(merge_bytes, {row["primitive_id"] for row in slots})
    checks.add("merge_tree.recursive_structure", len(merges) == 64, {"merge_count": len(merges)})
    rendered = reconstruct_merges(merges, primary_mapping, substring_set)
    reconstructed_primary_rows = [row.primary_dict() for row in rendered]
    checks.equal(
        "render.all_64_primary_rows",
        canonical_primary_raw(stage_json["primary"]["raw_merges"]),
        reconstructed_primary_rows,
    )
    checks.equal(
        "render.all_64_tsv_rows",
        canonical_tsv_raw(load_tsv_bytes(stage_bytes["raw_merges_tsv"], "raw_merges.tsv")),
        reconstructed_primary_rows,
    )
    supported_ranks = [row.rank for row in rendered if row.supported]
    unsupported_rows = [row for row in rendered if not row.supported]
    unsupported_mask = sum(1 << (row.rank - 1) for row in unsupported_rows)
    checks.equal("render.support_count", len(supported_ranks), 55)
    checks.equal("render.independent_supported_ranks", stage_json["independent"]["supported_merge_ranks"], supported_ranks)
    checks.equal("render.commit_supported_ranks", stage_json["commit"]["raw_supported_merge_ranks"], supported_ranks)
    checks.equal(
        "render.commit_unsupported_rows",
        stage_json["commit"]["raw_unsupported_merges"],
        [{"merge": row.merge, "rank": row.rank, "raw_render": row.raw_render} for row in unsupported_rows],
    )

    cover_solver = ExactCover([row.subtree_mask for row in merges])
    winner_cover = cover_solver.solve(unsupported_mask)
    checks.equal("cover.winner_exact_minimum", winner_cover["minimum"], 4)
    checks.equal("cover.winner_lex_ranks", winner_cover["lex_ranks"], [2, 3, 14, 23])
    checks.equal("cover.primary_ranks", [row["rank"] for row in stage_json["primary"]["canonical_minimum_cover"]], winner_cover["lex_ranks"])
    checks.equal("cover.independent_ranks", stage_json["independent"]["minimum_cover_ranks"], winner_cover["lex_ranks"])
    checks.equal("cover.commit_ranks", [row["rank"] for row in stage_json["commit"]["canonical_relaxed_minimum_cover"]], winner_cover["lex_ranks"])
    cover_tsv = load_tsv_bytes(stage_bytes["cover_tsv"], "minimum_cover.tsv")
    checks.equal("cover.tsv_ranks", [int(row["rank"]) for row in cover_tsv], winner_cover["lex_ranks"])

    key_ids = [row["card_id"] for row in primary_mapping]
    primary_objective = stage_json["primary"]["objective"]
    independent_objective = stage_json["independent"]["objective"]
    commit_objective = stage_json["commit"]["objective"]
    expected_objective = {
        "support": 55,
        "cover": 4,
        "key": key_ids,
    }
    objective_views = {
        "primary": {
            "support": primary_objective["raw_train_supported_named_merges"],
            "cover": primary_objective["exact_minimum_core_hit"],
            "key": primary_objective["lexicographic_card_id_sequence"],
        },
        "independent": {
            "support": independent_objective["raw_supported_merge_count"],
            "cover": independent_objective["minimum_inclusive_dag_cover"],
            "key": [row["card_id"] for row in independent_mapping],
        },
        "commit": {
            "support": commit_objective["raw_train_supported_named_merges"],
            "cover": commit_objective["exact_minimum_core_hit"],
            "key": commit_objective["lexicographic_card_id_sequence"],
        },
    }
    for label, view in objective_views.items():
        checks.equal(f"objective.full_match.{label}", view, expected_objective)
    checks.add(
        "objective.independent_full_space_complete",
        stage_json["independent"]["status"] == "GLOBAL_OPTIMUM_COMPLETE"
        and stage_json["independent"]["complete"] is True
        and stage_json["independent"]["winner_direct_replay_matches"] is True
        and stage_json["independent"]["search"]["small_role_tasks_completed"]
        == stage_json["independent"]["search"]["small_role_tasks_total"] == 1728,
        stage_json["independent"]["search"],
    )

    negative_mapping = positional_negative_mapping(registered, slots)
    negative_rendered = reconstruct_merges(merges, negative_mapping, substring_set)
    negative_supported = [row.rank for row in negative_rendered if row.supported]
    negative_unsupported_mask = sum(1 << (row.rank - 1) for row in negative_rendered if not row.supported)
    negative_cover = cover_solver.solve(negative_unsupported_mask)
    expected_negative = {
        "support": 25,
        "minimum": 15,
        "lex_ranks": [1, 3, 4, 5, 6, 8, 9, 11, 12, 14, 23, 24, 29, 31, 52],
    }
    checks.equal(
        "negative_control.direct_reconstruction",
        {"support": len(negative_supported), "minimum": negative_cover["minimum"], "lex_ranks": negative_cover["lex_ranks"]},
        expected_negative,
    )
    primary_negative = stage_json["primary"]["negative_control"]
    independent_negative = stage_json["independent"]["negative_control"]
    commit_negative = stage_json["commit"]["negative_control"]
    for label, observed in (
        ("primary", {
            "support": primary_negative["replayed_raw_supported_merges"],
            "minimum": primary_negative["replayed_exact_minimum"],
            "lex_ranks": primary_negative["canonical_cover_ranks"],
        }),
        ("independent", {
            "support": independent_negative["raw_supported_merge_count"],
            "minimum": independent_negative["minimum_inclusive_dag_cover"],
            "lex_ranks": independent_negative["minimum_cover_ranks"],
        }),
        ("commit", {
            "support": commit_negative["replayed_raw_supported_merges"],
            "minimum": commit_negative["replayed_exact_minimum"],
            "lex_ranks": commit_negative["canonical_cover_ranks"],
        }),
    ):
        checks.equal(f"negative_control.full_match.{label}", observed, expected_negative)
    checks.add(
        "negative_control.train_only_scope",
        primary_negative["relation"] == commit_negative["relation"] == "GDT615_TRAIN_ONLY"
        and primary_negative["historical_gdt614_train_intersection_held_minimum_not_replayed"] == 18
        and commit_negative["historical_gdt614_train_intersection_held_minimum_not_replayed"] == 18,
        {"relation": primary_negative["relation"], "historical_value_not_replayed": 18},
    )

    query_log_hash = sha256_bytes(stage_bytes["query_log"])
    base_encoding_hash = sha256_bytes(stage_bytes["base_encoding"])
    query_rows = [load_json_bytes(line, "PRIMARY_QUERY_CERTIFICATES.jsonl") for line in stage_bytes["query_log"].splitlines() if line]
    checks.add(
        "queries.full_log_sequence",
        len(query_rows) == 193
        and [row["query_id"] for row in query_rows] == [f"Q{index:04d}" for index in range(1, 194)]
        and stage_json["primary"]["solver"]["query_count"] == 193,
        {"query_count": len(query_rows)},
    )
    decisive = stage_json["decisive"]
    checks.equal("queries.base_encoding_hash", decisive["base_encoding_sha256"], base_encoding_hash)
    checks.equal("queries.full_log_hash", decisive["full_query_log_sha256"], query_log_hash)
    query_by_id = {row["query_id"]: row for row in query_rows}
    decisive_by_id = {row["query_id"]: row for row in decisive["queries"]}
    expected_queries = expected_decisive_queries(key_ids)
    checks.equal("queries.decisive_id_set", sorted(decisive_by_id), sorted(expected_queries))
    for query_id, expected in expected_queries.items():
        manifest_row = decisive_by_id.get(query_id, {})
        log_row = query_by_id.get(query_id, {})
        observed = {
            "claim": manifest_row.get("claim"),
            "phase": manifest_row.get("phase"),
            "result": manifest_row.get("result"),
            "constraint": manifest_row.get("logged_constraint"),
            "context": manifest_row.get("effective_context"),
            "log_phase": log_row.get("phase"),
            "log_result": log_row.get("result"),
            "log_constraint": log_row.get("constraint"),
        }
        desired = {
            "claim": expected["claim"],
            "phase": expected["phase"],
            "result": expected["result"],
            "constraint": expected["constraint"],
            "context": expected["context"],
            "log_phase": expected["phase"],
            "log_result": expected["result"],
            "log_constraint": expected["constraint"],
        }
        checks.equal(f"queries.decisive_context.{query_id}", observed, desired)
    checks.add(
        "queries.manifest_status",
        decisive["schema"] == "gdt615-stage0-decisive-query-contexts-v1" and decisive["status"] == "PASS",
        {"schema": decisive["schema"], "status": decisive["status"]},
    )

    bundle = stage_json["bundle"]
    bundle_paths: set[str] = set()
    opaque_hash_only_paths: list[str] = []
    bundle_all_match = True
    for entry in bundle["files"]:
        relative = entry["path"]
        duplicate = relative in bundle_paths
        bundle_paths.add(relative)
        path = safe_repo_path(repo_root, relative)
        is_public_stage0 = "artifacts/stage0/" in relative
        allowed = is_public_stage0 or relative in OPAQUE_BUNDLE_SOURCE_ALLOWLIST
        if not is_public_stage0:
            opaque_hash_only_paths.append(relative)
        exists = path.is_file() and not path.is_symlink()
        if exists:
            actual_bytes, actual_sha = sha256_file(path)
        else:
            actual_bytes, actual_sha = -1, "MISSING"
        passed = (
            not duplicate and allowed and exists
            and actual_bytes == entry["bytes"] and actual_sha == entry["sha256"]
        )
        bundle_all_match &= passed
        safe_id = relative.replace("/", ".")
        checks.add(
            f"bundle.hash.{safe_id}",
            passed,
            {
                "declared_bytes": entry["bytes"], "actual_bytes": actual_bytes,
                "declared_sha256": entry["sha256"], "actual_sha256": actual_sha,
                "access_mode": "public_stage0_parseable" if is_public_stage0 else "opaque_hash_only",
            },
        )
    checks.add(
        "bundle.contract",
        bundle["schema"] == "gdt615-stage0-stable-bundle-v1"
        and bundle["status"] == "PASS"
        and bundle_all_match
        and len(bundle_paths) == len(bundle["files"]),
        {"entries": len(bundle_paths), "all_hashes_match": bundle_all_match},
    )

    replay = stage_json["replay"]
    replay_aliases = {
        "BASE_ENCODING.smt2": stage_bytes["base_encoding"],
        "INPUT_MANIFEST.json": stage_json_bytes["input_manifest"],
        "QUERY_CERTIFICATES.jsonl": stage_bytes["query_log"],
        "RESULT.json": stage_json_bytes["primary"],
        "mapping.tsv": stage_bytes["mapping_tsv"],
        "minimum_cover.tsv": stage_bytes["cover_tsv"],
        "raw_merges.tsv": stage_bytes["raw_merges_tsv"],
    }
    for stable_name, record in sorted(replay["stable_files"].items()):
        internal_match = record["byte_identical"] is True and record["first_sha256"] == record["replay_sha256"]
        if stable_name in replay_aliases:
            internal_match &= sha256_bytes(replay_aliases[stable_name]) == record["first_sha256"]
        checks.add(
            f"replay.stable_hash.{stable_name}",
            internal_match,
            {"sha256": record["first_sha256"], "public_copy_checked": stable_name in replay_aliases},
        )
    checks.add(
        "replay.status_and_volatile_scope",
        replay["status"] == "PASS"
        and replay["stale_pid_run_state_published"] is False
        and "QUERY_DIAGNOSTICS.jsonl" in replay["excluded_volatile_files"],
        {"status": replay["status"], "stale_pid_run_state_published": replay["stale_pid_run_state_published"]},
    )

    commit = stage_json["commit"]
    exact_evidence = commit["exact_evidence"]
    checks.add(
        "commit.evidence_hashes_and_matches",
        all(
            exact_evidence[key] is True
            for key in (
                "primary_and_independent_canonical_cover_match",
                "primary_and_independent_full_mapping_match",
                "primary_and_independent_objectives_match",
                "primary_and_independent_supported_rank_set_match",
            )
        )
        and exact_evidence["primary_result_sha256"] == sha256_bytes(stage_json_bytes["primary"])
        and exact_evidence["independent_result_sha256"] == sha256_bytes(stage_json_bytes["independent"])
        and exact_evidence["primary_query_log_sha256"] == query_log_hash,
        exact_evidence,
    )

    partition = registered["partition_access"]
    search = registered["search"]
    primary_manifest_keys = set(stage_json["input_manifest"])
    allowed_primary_manifest_keys = {
        "BASE_ENCODING.smt2", "REGISTERED_SEARCH.json", "REGISTERED_TRAIN_SUBSTRINGS.txt",
        "merge_tree.tsv", "solver_source", "z3_version",
    }
    restricted_tokens = (b"held", b"lm_confirm", b"synthetic_train", b"f84", b"voynich")
    encoding_lower = stage_bytes["base_encoding"].lower()
    query_lower = stage_bytes["query_log"].lower()
    restricted_in_decisive_bytes = [token.decode() for token in restricted_tokens if token in encoding_lower or token in query_lower]
    no_restricted_data = (
        partition["stage0"] == ["merge_tree.tsv", "REGISTERED_SEARCH.json", "REGISTERED_TRAIN_SUBSTRINGS.txt"]
        and partition["stage0_and_stage1_processes_have_readable_held_mount"] is False
        and partition["stage0_through_stage2_processes_have_readable_lm_confirm_mount"] is False
        and search["held_reveal_after_mapping_commit"] is False
        and search["held_reveal_after_complete_three_world_train_bundle_commit"] is True
        and commit["held_or_lm_confirm_opened"] is False
        and commit["f84_or_f84r_opened"] is False
        and commit["voynich_target_opened"] is False
        and primary_manifest_keys == allowed_primary_manifest_keys
        and not restricted_in_decisive_bytes
    )
    checks.add(
        "scope.no_held_lm_confirm_f84_or_target_access",
        no_restricted_data,
        {
            "stage0_inputs": partition["stage0"],
            "commit_flags": {
                "held_or_lm_confirm_opened": commit["held_or_lm_confirm_opened"],
                "f84_or_f84r_opened": commit["f84_or_f84r_opened"],
                "voynich_target_opened": commit["voynich_target_opened"],
            },
            "restricted_tokens_in_base_or_query_log": restricted_in_decisive_bytes,
        },
    )
    checks.add(
        "scope.claim_and_stage_boundary",
        "train-only" in commit["claim_scope"].lower()
        and "no voynich" in commit["claim_scope"].lower()
        and commit["stage0_cover_is_actual_paid_location_selection"] is False
        and commit["stage1_status"] == "NOT_RUN"
        and commit["status"] == "STAGE0_MAPPING_CERTIFICATE_PASS__STAGE1_NOT_RUN",
        {
            "claim_scope": commit["claim_scope"],
            "stage0_cover_is_actual_paid_location_selection": commit["stage0_cover_is_actual_paid_location_selection"],
            "stage1_status": commit["stage1_status"],
        },
    )
    scout = stage_json["scout"]
    scout_replay = stage_json["scout_candidate_replay"]
    checks.add(
        "scope.scout_not_promoted_to_proof",
        scout["scientific_pass"] is False
        and scout["global_optimality_claimed"] is False
        and scout["infeasibility_claimed"] is False
        and scout_replay["scientific_pass"] is False
        and scout_replay["global_optimality_checked"] is False,
        {"scout_claim": scout["claim"], "replay_claim": scout_replay["claim"]},
    )

    failed = [row["check_id"] for row in checks.rows if not row["passed"]]
    result = {
        "schema": SCHEMA,
        "status": "PASS" if checks.passed else "FAIL",
        "checks": checks.rows,
        "summary": {
            "check_count": len(checks.rows),
            "passed_count": len(checks.rows) - len(failed),
            "failed_count": len(failed),
            "failed_check_ids": failed,
        },
        "recomputed": {
            "input_sha256": actual_input_hashes,
            "mapping_card_id_sequence": key_ids,
            "raw_train_supported_merge_count": len(supported_ranks),
            "raw_train_supported_merge_ranks": supported_ranks,
            "raw_train_unsupported_merges": [
                {"rank": row.rank, "merge": row.merge, "raw_render": row.raw_render}
                for row in unsupported_rows
            ],
            "winner_cover": winner_cover,
            "negative_control": {
                "raw_train_supported_merge_count": len(negative_supported),
                "cover": negative_cover,
            },
            "decisive_query_count": len(expected_queries),
            "full_query_count": len(query_rows),
            "bundle_entry_count": len(bundle_paths),
        },
        "data_access": {
            "semantic_inputs": [
                "REGISTERED_SEARCH.json",
                "REGISTERED_TRAIN_SUBSTRINGS.txt",
                "merge_tree.tsv",
                "artifacts/stage0/* public result/certificate artifacts",
            ],
            "opaque_bundle_hash_only_paths": sorted(opaque_hash_only_paths),
            "primary_or_finalizer_module_imported": False,
            "held_or_lm_confirm_opened": False,
            "f84_or_f84r_opened": False,
            "voynich_target_opened": False,
        },
    }
    return result


def brute_small_cover(subtrees: Sequence[int], unsupported: int) -> tuple[int, list[int]]:
    covers = []
    for paid in range(len(subtrees)):
        cover = 0
        for affected, subtree in enumerate(subtrees):
            if subtree & (1 << paid):
                cover |= 1 << affected
        covers.append(cover)
    for size in range(len(subtrees) + 1):
        for chosen in itertools.combinations(range(len(subtrees)), size):
            covered = 0
            for paid in chosen:
                covered |= covers[paid]
            if unsupported & ~covered == 0:
                return size, [paid + 1 for paid in chosen]
    raise AssertionError("small brute cover is infeasible")


def self_test() -> None:
    if sha256_bytes(b"abc") != "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad":
        raise AssertionError("SHA-256 self-test failed")
    small = [1 << index for index in range(6)]
    small[2] |= small[0] | small[1]
    small[4] |= small[2] | small[3]
    small[5] |= small[1]
    padded = small + [1 << index for index in range(6, MERGE_COUNT)]
    solver = ExactCover(padded)
    for unsupported in range(1 << 6):
        expected_minimum, expected_lex = brute_small_cover(small, unsupported)
        observed = solver.solve(unsupported)
        if observed["minimum"] != expected_minimum or observed["lex_ranks"] != expected_lex:
            raise AssertionError(f"cover parity failed for mask {unsupported}")
    print("STAGE0_VALIDATE_SELF_TEST_PASS")


def default_paths() -> tuple[Path, Path, Path, Path, Path, Path]:
    experiment = Path(__file__).resolve().parents[1]
    repo_root = experiment.parents[2]
    registered = experiment / "artifacts" / "REGISTERED_SEARCH.json"
    substrings = experiment / "artifacts" / "REGISTERED_TRAIN_SUBSTRINGS.txt"
    merge_tree = repo_root / "experiments" / "yolo" / "gdt608_compositional_stem_orientation" / "artifacts" / "merge_tree.tsv"
    stage0 = experiment / "artifacts" / "stage0"
    output = stage0 / "STAGE0_VALIDATION.json"
    return repo_root, experiment, registered, substrings, merge_tree, output


def parse_args(argv: Sequence[str]) -> argparse.Namespace:
    repo_root, experiment, registered, substrings, merge_tree, output = default_paths()
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=repo_root)
    parser.add_argument("--registered-search", type=Path, default=registered)
    parser.add_argument("--train-substrings", type=Path, default=substrings)
    parser.add_argument("--merge-tree", type=Path, default=merge_tree)
    parser.add_argument("--stage0-dir", type=Path, default=experiment / "artifacts" / "stage0")
    parser.add_argument("--output", type=Path, default=output)
    parser.add_argument("--self-test", action="store_true")
    return parser.parse_args(argv)


def write_deterministic_json(path: Path, value: Any) -> None:
    data = (json.dumps(value, indent=2, sort_keys=True, ensure_ascii=True) + "\n").encode("utf-8")
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_bytes(data)
    os.replace(temporary, path)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(sys.argv[1:] if argv is None else argv)
    if args.self_test:
        self_test()
        return 0
    try:
        result = run_validation(
            args.repo_root.resolve(),
            args.registered_search.resolve(),
            args.train_substrings.resolve(),
            args.merge_tree.resolve(),
            args.stage0_dir.resolve(),
        )
    except (OSError, KeyError, TypeError, ValueError, ValidationError) as exc:
        print(f"STAGE0_VALIDATION_ERROR: {exc}", file=sys.stderr)
        return 2
    write_deterministic_json(args.output.resolve(), result)
    print(
        f"STAGE0_VALIDATION_{result['status']} "
        f"checks={result['summary']['passed_count']}/{result['summary']['check_count']} "
        f"output={args.output}"
    )
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
