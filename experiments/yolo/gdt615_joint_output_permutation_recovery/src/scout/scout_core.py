#!/usr/bin/env python3
"""Read-only structural model used by the GDT615 heuristic scout.

This module deliberately has only three registered scientific inputs: the
merge tree, REGISTERED_SEARCH, and REGISTERED_TRAIN_SUBSTRINGS.  It proves no
global search claim.  Its exact routines replay only one concrete mapping's
raw renders and minimum subtree cover.
"""

from __future__ import annotations

import csv
import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Mapping, Sequence


CLAIM = "HEURISTIC_SCOUT_ONLY__NOT_A_PASS_OR_OPTIMALITY_PROOF"
HERE = Path(__file__).resolve().parent
EXPERIMENT = HERE.parents[1]
ROOT = EXPERIMENT.parents[2]
REGISTERED_SEARCH = EXPERIMENT / "artifacts/REGISTERED_SEARCH.json"
REGISTERED_SUBSTRINGS = (
    EXPERIMENT / "artifacts/REGISTERED_TRAIN_SUBSTRINGS.txt"
)
MERGE_TREE = (
    ROOT
    / "experiments/yolo/gdt608_compositional_stem_orientation/artifacts/merge_tree.tsv"
)
WORK_ROOT = EXPERIMENT / "artifacts/stage0_scout_work"
PUBLIC_STAGE0_ROOT = EXPERIMENT / "artifacts/stage0"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def canonical_json(payload: object) -> str:
    return json.dumps(payload, indent=2, sort_keys=True) + "\n"


def require_work_path(
    path: Path,
    *,
    allow_scout_source: bool = False,
    allow_public_candidate: bool = False,
) -> Path:
    resolved = path.resolve()
    allowed = [WORK_ROOT.resolve()]
    if allow_scout_source:
        allowed.append(HERE.resolve())
    if (
        allow_public_candidate
        and resolved.parent == PUBLIC_STAGE0_ROOT.resolve()
        and resolved.name.startswith("SCOUT_CANDIDATE_")
        and resolved.suffix == ".json"
    ):
        return resolved
    if not any(resolved == root or resolved.is_relative_to(root) for root in allowed):
        raise ValueError(f"path is outside the scout allow-list: {path}")
    return resolved


@dataclass(frozen=True, slots=True)
class Primitive:
    primitive_id: str
    role: str


@dataclass(frozen=True, slots=True)
class Card:
    card_id: str
    role: str
    output: str
    side_license: str | None


@dataclass(frozen=True, slots=True)
class Merge:
    rank: int
    left: str
    right: str
    merged: str
    leaves: tuple[str, ...]
    descendants: frozenset[int]


@dataclass(frozen=True, slots=True)
class Evaluation:
    mapping: tuple[str, ...]
    raw_renders: tuple[str, ...]
    supported_mask: int
    support_count: int
    cover_minimum: int


class Problem:
    """Validated fixed scout problem and concrete-mapping replayer."""

    def __init__(
        self,
        config: dict,
        primitives: tuple[Primitive, ...],
        cards_by_role: dict[str, tuple[Card, ...]],
        merges: tuple[Merge, ...],
        substrings: tuple[str, ...],
        input_hashes: dict[str, str],
    ) -> None:
        self.config = config
        self.primitives = primitives
        self.cards_by_role = cards_by_role
        self.merges = merges
        self.substrings = substrings
        self.substring_set = frozenset(substrings)
        self.input_hashes = input_hashes
        self.primitive_index = {
            primitive.primitive_id: index
            for index, primitive in enumerate(self.primitives)
        }
        self.card_by_id = {
            card.card_id: card
            for cards in self.cards_by_role.values()
            for card in cards
        }
        self.role_positions = {
            role: tuple(
                index
                for index, primitive in enumerate(self.primitives)
                if primitive.role == role
            )
            for role in self.cards_by_role
        }
        self.descendant_masks = tuple(
            sum(1 << index for index in merge.descendants)
            for merge in self.merges
        )
        self._cover_cache: dict[int, int] = {}

    @property
    def full_merge_mask(self) -> int:
        return (1 << len(self.merges)) - 1

    def identity_mapping(self) -> tuple[str, ...]:
        result = [""] * len(self.primitives)
        for role, positions in self.role_positions.items():
            cards = self.cards_by_role[role]
            if len(cards) != len(positions):
                raise AssertionError((role, len(cards), len(positions)))
            for position, card in zip(positions, cards, strict=True):
                result[position] = card.card_id
        return tuple(result)

    def validate_mapping(
        self, mapping: Sequence[str] | Mapping[str, str]
    ) -> tuple[str, ...]:
        if isinstance(mapping, Mapping):
            if set(mapping) != set(self.primitive_index):
                missing = sorted(set(self.primitive_index) - set(mapping))
                extra = sorted(set(mapping) - set(self.primitive_index))
                raise ValueError(f"mapping IDs differ; missing={missing}, extra={extra}")
            ordered = tuple(mapping[p.primitive_id] for p in self.primitives)
        else:
            ordered = tuple(mapping)
        if len(ordered) != len(self.primitives):
            raise ValueError("mapping must contain all 34 primitive positions")
        for role, positions in self.role_positions.items():
            expected = {card.card_id for card in self.cards_by_role[role]}
            observed = {ordered[index] for index in positions}
            if observed != expected or len(positions) != len(observed):
                raise ValueError(f"mapping is not a bijection for role {role}")
            for index in positions:
                card = self.card_by_id.get(ordered[index])
                if card is None or card.role != role:
                    raise ValueError(
                        f"card {ordered[index]!r} cannot bind to role {role}"
                    )
        return ordered

    def mapping_dict(self, mapping: Sequence[str]) -> dict[str, str]:
        ordered = self.validate_mapping(mapping)
        return {
            primitive.primitive_id: ordered[index]
            for index, primitive in enumerate(self.primitives)
        }

    def mapping_rows(self, mapping: Sequence[str]) -> list[dict[str, object]]:
        ordered = self.validate_mapping(mapping)
        rows = []
        for index, primitive in enumerate(self.primitives):
            card = self.card_by_id[ordered[index]]
            rows.append(
                {
                    "primitive_index": index,
                    "primitive_id": primitive.primitive_id,
                    "role": primitive.role,
                    "card_id": card.card_id,
                    "output": card.output,
                    "output_length": len(card.output),
                    "side_license": card.side_license or "",
                }
            )
        return rows

    def raw_renders(self, mapping: Sequence[str]) -> tuple[str, ...]:
        ordered = self.validate_mapping(mapping)
        rendered = {
            primitive.primitive_id: self.card_by_id[ordered[index]].output
            for index, primitive in enumerate(self.primitives)
        }
        values = []
        for merge in self.merges:
            value = rendered[merge.left] + rendered[merge.right]
            if not value:
                raise AssertionError(f"empty raw merge render at rank {merge.rank}")
            rendered[merge.merged] = value
            values.append(value)
        return tuple(values)

    def supported_mask(self, raw_renders: Sequence[str]) -> int:
        if len(raw_renders) != len(self.merges):
            raise ValueError("raw render count differs from merge count")
        result = 0
        for index, value in enumerate(raw_renders):
            if value in self.substring_set:
                result |= 1 << index
        return result

    def evaluate(self, mapping: Sequence[str]) -> Evaluation:
        ordered = self.validate_mapping(mapping)
        raw = self.raw_renders(ordered)
        supported = self.supported_mask(raw)
        return Evaluation(
            mapping=ordered,
            raw_renders=raw,
            supported_mask=supported,
            support_count=supported.bit_count(),
            cover_minimum=self.cover_minimum(supported),
        )

    def _candidate_cover_masks(self, bad_mask: int) -> tuple[int, ...]:
        covers = [0] * len(self.merges)
        for merge_index, descendants in enumerate(self.descendant_masks):
            if not (bad_mask & (1 << merge_index)):
                continue
            pending = descendants
            while pending:
                bit = pending & -pending
                covers[bit.bit_length() - 1] |= 1 << merge_index
                pending ^= bit
        return tuple(covers)

    def _cover_possible(
        self,
        bad_mask: int,
        budget: int,
        *,
        forbidden_mask: int = 0,
        preselected_mask: int = 0,
    ) -> bool:
        covers = self._candidate_cover_masks(bad_mask)
        uncovered = bad_mask
        pending = preselected_mask
        while pending:
            bit = pending & -pending
            uncovered &= ~covers[bit.bit_length() - 1]
            pending ^= bit
        budget -= preselected_mask.bit_count()
        if budget < 0:
            return False
        unavailable = forbidden_mask | preselected_mask
        memo: dict[tuple[int, int], bool] = {}

        def lower_bound(mask: int, unavailable_mask: int) -> int:
            option_sets = []
            pending_nodes = mask
            while pending_nodes:
                bit = pending_nodes & -pending_nodes
                index = bit.bit_length() - 1
                options = self.descendant_masks[index] & ~unavailable_mask
                if not options:
                    return len(self.merges) + 1
                option_sets.append((options.bit_count(), index, options))
                pending_nodes ^= bit
            used = 0
            disjoint = 0
            for _size, _index, options in sorted(option_sets):
                if not (options & used):
                    disjoint += 1
                    used |= options
            max_cover = max(
                (covers[index] & mask).bit_count()
                for index in range(len(covers))
                if not (unavailable_mask & (1 << index))
            )
            cardinality = (mask.bit_count() + max_cover - 1) // max_cover
            return max(disjoint, cardinality)

        def visit(mask: int, remaining: int) -> bool:
            if not mask:
                return True
            if remaining <= 0:
                return False
            key = (mask, remaining)
            cached = memo.get(key)
            if cached is not None:
                return cached
            if lower_bound(mask, unavailable) > remaining:
                memo[key] = False
                return False

            best_options = 0
            best_key: tuple[int, int] | None = None
            pending_nodes = mask
            while pending_nodes:
                bit = pending_nodes & -pending_nodes
                index = bit.bit_length() - 1
                options = self.descendant_masks[index] & ~unavailable
                if not options:
                    memo[key] = False
                    return False
                option_key = (options.bit_count(), index)
                if best_key is None or option_key < best_key:
                    best_key = option_key
                    best_options = options
                pending_nodes ^= bit

            candidates = []
            pending_candidates = best_options
            while pending_candidates:
                bit = pending_candidates & -pending_candidates
                candidate = bit.bit_length() - 1
                candidates.append(
                    (-(covers[candidate] & mask).bit_count(), candidate)
                )
                pending_candidates ^= bit
            for _negative_gain, candidate in sorted(candidates):
                if visit(mask & ~covers[candidate], remaining - 1):
                    memo[key] = True
                    return True
            memo[key] = False
            return False

        return visit(uncovered, budget)

    def _greedy_cover_size(self, bad_mask: int) -> int:
        covers = self._candidate_cover_masks(bad_mask)
        uncovered = bad_mask
        count = 0
        while uncovered:
            candidate = max(
                range(len(covers)),
                key=lambda index: ((covers[index] & uncovered).bit_count(), -index),
            )
            gain = covers[candidate] & uncovered
            if not gain:
                raise AssertionError("uncoverable merge in inclusive subtree model")
            uncovered &= ~gain
            count += 1
        return count

    def cover_minimum(self, supported_mask: int) -> int:
        supported_mask &= self.full_merge_mask
        cached = self._cover_cache.get(supported_mask)
        if cached is not None:
            return cached
        bad = self.full_merge_mask ^ supported_mask
        if not bad:
            self._cover_cache[supported_mask] = 0
            return 0
        upper = self._greedy_cover_size(bad)
        lower = 0
        disjoint_options = 0
        pending = bad
        option_rows = []
        while pending:
            bit = pending & -pending
            index = bit.bit_length() - 1
            option_rows.append(
                (self.descendant_masks[index].bit_count(), index)
            )
            pending ^= bit
        for _size, index in sorted(option_rows):
            options = self.descendant_masks[index]
            if not (options & disjoint_options):
                lower += 1
                disjoint_options |= options
        for limit in range(lower, upper + 1):
            if self._cover_possible(bad, limit):
                self._cover_cache[supported_mask] = limit
                return limit
        raise AssertionError("minimum-cover search failed above greedy upper bound")

    def canonical_cover(self, supported_mask: int) -> tuple[int, ...]:
        supported_mask &= self.full_merge_mask
        bad = self.full_merge_mask ^ supported_mask
        minimum = self.cover_minimum(supported_mask)
        if minimum == 0:
            return ()
        selected = 0
        forbidden = 0
        for candidate in range(len(self.merges)):
            bit = 1 << candidate
            trial = selected | bit
            if self._cover_possible(
                bad,
                minimum,
                forbidden_mask=forbidden,
                preselected_mask=trial,
            ):
                selected = trial
                if selected.bit_count() == minimum:
                    break
            else:
                forbidden |= bit
        if selected.bit_count() != minimum:
            raise AssertionError("canonical minimum cover has wrong cardinality")
        covers = self._candidate_cover_masks(bad)
        covered = 0
        pending = selected
        while pending:
            bit = pending & -pending
            covered |= covers[bit.bit_length() - 1]
            pending ^= bit
        if covered & bad != bad:
            raise AssertionError("canonical minimum cover does not cover every miss")
        return tuple(
            index + 1
            for index in range(len(self.merges))
            if selected & (1 << index)
        )

    def candidate_payload(
        self,
        evaluation: Evaluation,
        *,
        provenance: Mapping[str, object],
    ) -> dict[str, object]:
        canonical_cover = self.canonical_cover(evaluation.supported_mask)
        mapping_rows = self.mapping_rows(evaluation.mapping)
        raw_rows = []
        for index, (merge, value) in enumerate(
            zip(self.merges, evaluation.raw_renders, strict=True)
        ):
            raw_rows.append(
                {
                    "rank": merge.rank,
                    "merge": merge.merged,
                    "raw_render": value,
                    "raw_render_length": len(value),
                    "train_substring_supported": bool(
                        evaluation.supported_mask & (1 << index)
                    ),
                    "inclusive_recursive_merge_subtree_ranks": [
                        rank + 1 for rank in sorted(merge.descendants)
                    ],
                }
            )
        mapping_digest = hashlib.sha256(
            "\n".join(
                f"{row['primitive_id']}\t{row['card_id']}" for row in mapping_rows
            ).encode("ascii")
        ).hexdigest()
        return {
            "schema": "gdt615-stage0-heuristic-scout-candidate-v1",
            "claim": CLAIM,
            "scientific_pass": False,
            "global_optimality_claimed": False,
            "candidate_id": f"scout-{mapping_digest[:16]}",
            "mapping_sha256": mapping_digest,
            "registered_input_hashes": self.input_hashes,
            "provenance": dict(provenance),
            "raw_train_supported_merge_count": evaluation.support_count,
            "candidate_local_exact_cover_minimum": evaluation.cover_minimum,
            "candidate_local_canonical_cover_ranks": list(canonical_cover),
            "candidate_local_canonical_cover_merges": [
                self.merges[rank - 1].merged for rank in canonical_cover
            ],
            "mapping": mapping_rows,
            "raw_merges": raw_rows,
        }


def _registered_hash(config: dict, path: Path) -> str:
    relative = path.relative_to(ROOT).as_posix()
    matches = [
        row["sha256"]
        for row in config.get("registered_inputs", [])
        if row.get("path") == relative
    ]
    if len(matches) != 1:
        raise ValueError(f"registered hash missing or repeated for {relative}")
    return str(matches[0])


def load_problem() -> Problem:
    config = json.loads(REGISTERED_SEARCH.read_text(encoding="utf-8"))
    if config.get("schema") != "gdt615-joint-output-binding-search-v1":
        raise ValueError("unexpected REGISTERED_SEARCH schema")

    tree_hash = sha256(MERGE_TREE)
    if tree_hash != _registered_hash(config, MERGE_TREE):
        raise ValueError("merge-tree hash differs from REGISTERED_SEARCH")
    substring_hash = sha256(REGISTERED_SUBSTRINGS)
    registered_substrings = config["registered_train_substrings"]
    if substring_hash != registered_substrings["sha256"]:
        raise ValueError("registered train-substring hash mismatch")

    primitives = tuple(
        Primitive(str(row["primitive_id"]), str(row["role"]))
        for row in config["primitive_role_assignment"]
    )
    if len(primitives) != 34 or len({p.primitive_id for p in primitives}) != 34:
        raise ValueError("primitive inventory is not 34 unique IDs")

    cards_by_role: dict[str, tuple[Card, ...]] = {}
    all_card_ids = set()
    all_outputs = set()
    for role, rows in config["primitive_output_deck"].items():
        cards = tuple(
            Card(
                card_id=str(row["card_id"]),
                role=str(role),
                output=str(row["output"]),
                side_license=(
                    str(row["side_license"])
                    if row.get("side_license") is not None
                    else None
                ),
            )
            for row in rows
        )
        cards_by_role[str(role)] = cards
        for card in cards:
            if card.card_id in all_card_ids:
                raise ValueError(f"duplicate primitive card ID {card.card_id}")
            all_card_ids.add(card.card_id)
            if card.output:
                if card.output in all_outputs:
                    raise ValueError(f"duplicate primitive output {card.output}")
                all_outputs.add(card.output)
            elif role != "null_layout":
                raise ValueError("only null_layout may have empty output")
    role_counts = {
        role: sum(primitive.role == role for primitive in primitives)
        for role in cards_by_role
    }
    if any(role_counts[role] != len(cards) for role, cards in cards_by_role.items()):
        raise ValueError("role-wise primitive/card counts differ")

    substrings = tuple(
        REGISTERED_SUBSTRINGS.read_text(encoding="ascii").splitlines()
    )
    if any(not value or len(value) > 12 for value in substrings):
        raise ValueError("registered substring outside nonempty 1..12 contract")
    if len(substrings) != len(set(substrings)):
        raise ValueError("registered substring table contains duplicates")
    if tuple(sorted(substrings, key=lambda value: (len(value), value.encode("ascii")))) != substrings:
        raise ValueError("registered substring table has unexpected ordering")
    if len(substrings) != int(registered_substrings["distinct_substring_count"]):
        raise ValueError("registered substring count mismatch")

    with MERGE_TREE.open(encoding="utf-8", newline="") as handle:
        tree_rows = list(csv.DictReader(handle, delimiter="\t"))
    if len(tree_rows) != 64:
        raise ValueError("merge tree must contain 64 rows")
    known = {primitive.primitive_id for primitive in primitives}
    expanded = {primitive.primitive_id: (primitive.primitive_id,) for primitive in primitives}
    descendant_by_name: dict[str, frozenset[int]] = {
        primitive.primitive_id: frozenset() for primitive in primitives
    }
    merges = []
    for index, row in enumerate(tree_rows):
        rank = int(row["rank"])
        if rank != index + 1:
            raise ValueError("merge ranks are not exactly 1..64")
        left = row["left"]
        right = row["right"]
        merged = row["merged"]
        if left not in known or right not in known or merged in known:
            raise ValueError(f"merge tree is not topological at rank {rank}")
        leaves = expanded[left] + expanded[right]
        published_leaves = tuple(row["leaf_sequence"].split())
        if leaves != published_leaves or len(leaves) != int(row["leaf_count"]):
            raise ValueError(f"leaf expansion mismatch at rank {rank}")
        descendants = frozenset(
            {index} | set(descendant_by_name[left]) | set(descendant_by_name[right])
        )
        merges.append(
            Merge(
                rank=rank,
                left=left,
                right=right,
                merged=merged,
                leaves=leaves,
                descendants=descendants,
            )
        )
        known.add(merged)
        expanded[merged] = leaves
        descendant_by_name[merged] = descendants

    primitive_role = {p.primitive_id: p.role for p in primitives}
    for merge in merges:
        if all(primitive_role[leaf] == "null_layout" for leaf in merge.leaves):
            raise ValueError(f"merge rank {merge.rank} can render empty")

    input_hashes = {
        MERGE_TREE.relative_to(ROOT).as_posix(): tree_hash,
        REGISTERED_SEARCH.relative_to(ROOT).as_posix(): sha256(REGISTERED_SEARCH),
        REGISTERED_SUBSTRINGS.relative_to(ROOT).as_posix(): substring_hash,
    }
    return Problem(
        config=config,
        primitives=primitives,
        cards_by_role=cards_by_role,
        merges=tuple(merges),
        substrings=substrings,
        input_hashes=input_hashes,
    )


def mapping_from_candidate(payload: Mapping[str, object]) -> dict[str, str]:
    rows = payload.get("mapping")
    if not isinstance(rows, list):
        raise ValueError("candidate mapping must be a list")
    result = {}
    for row in rows:
        if not isinstance(row, dict):
            raise ValueError("candidate mapping row is not an object")
        primitive_id = str(row["primitive_id"])
        card_id = str(row["card_id"])
        if primitive_id in result:
            raise ValueError(f"duplicate candidate primitive {primitive_id}")
        result[primitive_id] = card_id
    return result


def write_tsv(path: Path, rows: Iterable[Mapping[str, object]]) -> None:
    materialized = list(rows)
    if not materialized:
        raise ValueError(f"cannot write headerless empty TSV {path}")
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=list(materialized[0]),
            delimiter="\t",
            lineterminator="\n",
        )
        writer.writeheader()
        writer.writerows(materialized)
