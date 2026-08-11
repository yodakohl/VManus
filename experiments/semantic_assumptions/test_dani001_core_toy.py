#!/usr/bin/env python3
"""Synthetic-only smoke and exactness tests for the DANI001 integer core."""

from __future__ import annotations

import hashlib
import itertools
import json
import os
import random
import tempfile
from array import array
from pathlib import Path

from dani001_core import (
    DEPOSITED_AFFIX,
    DIRECT,
    Dani001Core,
    Dani001CoreError,
    compile_shared,
)


def synthetic_constraints(n_core: int, n_vectors: int) -> tuple[list[int], list[int], list[int]]:
    masks: list[int] = []
    required: list[int] = []
    weights: list[int] = []
    constraint_index: dict[tuple[int, tuple[int, ...]], int] = {}

    def add(assignments: dict[int, int], row_weights: list[int]) -> None:
        mask = sum(1 << index for index in assignments)
        row = [255] * n_core
        for index, output in assignments.items():
            row[index] = output
        identity = (mask, tuple(row))
        if identity in constraint_index:
            existing = constraint_index[identity]
            for vector, weight in enumerate(row_weights):
                weights[existing * n_vectors + vector] += weight
            return
        constraint_index[identity] = len(masks)
        masks.append(mask)
        required.extend(row)
        weights.extend(row_weights)

    add({}, [1 + v for v in range(n_vectors)])
    for i in range(n_core):
        add({i: (i + 1) % n_core}, [1 + ((i + v) % 5) for v in range(n_vectors)])
    for i in range(n_core):
        j = (i + 1) % n_core
        first = (2 * i + 1) % n_core
        second = (first + 1) % n_core
        if first == second:
            continue
        add({i: first, j: second}, [2 + ((i + 2 * v) % 7) for v in range(n_vectors)])
    for i in range(max(1, n_core // 2)):
        inputs = [i, (i + 2) % n_core, (i + 4) % n_core]
        if len(set(inputs)) < 3:
            continue
        outputs = [(i + 1) % n_core, (i + 3) % n_core, (i + 5) % n_core]
        if len(set(outputs)) < 3:
            continue
        add(dict(zip(inputs, outputs)), [3 + ((i + v) % 11) for v in range(n_vectors)])
    return masks, required, weights


def words(raw: bytes) -> list[int]:
    values = array("I")
    values.frombytes(raw)
    return list(values)


def expect_rejected(callable_object: object) -> None:
    try:
        callable_object()  # type: ignore[operator]
    except (Dani001CoreError, TypeError, ValueError):
        return
    raise AssertionError("malformed input was not rejected")


def vector_mask(raw: bytes, n_vectors: int, full_n: int, begin: int, end: int) -> bytes:
    values = words(raw)
    selected = array("I")
    for vector in range(n_vectors):
        selected.extend(values[vector * full_n + begin:vector * full_n + end])
    return selected.tobytes()


def conjugate_constraints(
    n_core: int,
    masks: list[int],
    required: list[int],
    input_rename: list[int],
    output_rename: list[int],
) -> tuple[list[int], list[int]]:
    new_masks: list[int] = []
    new_required: list[int] = []
    for c, mask in enumerate(masks):
        row = [255] * n_core
        new_mask = 0
        for old_input in range(n_core):
            if not mask & (1 << old_input):
                continue
            new_input = input_rename[old_input]
            old_output = required[c * n_core + old_input]
            row[new_input] = output_rename[old_output]
            new_mask |= 1 << new_input
        new_masks.append(new_mask)
        new_required.extend(row)
    return new_masks, new_required


def check_conjugation(
    core: Dani001Core,
    raw: bytes,
    n_core: int,
    n_vectors: int,
    masks: list[int],
    required: list[int],
    weights: list[int],
) -> None:
    input_rename = list(range(1, n_core)) + [0]
    output_rename = list(reversed(range(n_core)))
    renamed_masks, renamed_required = conjugate_constraints(
        n_core, masks, required, input_rename, output_rename
    )
    renamed = core.enumerate_raw(
        n_core=n_core,
        input_masks=renamed_masks,
        required_outputs=renamed_required,
        n_vectors=n_vectors,
        weights=weights,
        rank_begin=0,
        rank_end=core.factorial(n_core),
        threads=1,
    )
    original_values = words(raw)
    renamed_values = words(renamed)
    n_ranks = core.factorial(n_core)
    inverse_input = [0] * n_core
    for old, new in enumerate(input_rename):
        inverse_input[new] = old
    for old_rank in range(n_ranks):
        permutation = core.unrank(n_core, old_rank)
        transformed = tuple(
            output_rename[permutation[inverse_input[new_input]]]
            for new_input in range(n_core)
        )
        new_rank = core.rank(transformed)
        for vector in range(n_vectors):
            assert (
                original_values[vector * n_ranks + old_rank]
                == renamed_values[vector * n_ranks + new_rank]
            )


def run() -> dict[str, object]:
    if os.cpu_count() is None or os.cpu_count() < 32:
        raise AssertionError("registered smoke requires at least 32 logical CPUs")
    with tempfile.TemporaryDirectory(prefix="dani001-core-toy-") as directory:
        library = compile_shared(Path(directory) / "libdani001_core.so")
        core = Dani001Core(library)
        assert core.has_openmp
        digests: dict[str, str] = {}

        # Compiler identity, external staging, and no-clobber are wrapper gates.
        expect_rejected(lambda: compile_shared(library))
        expect_rejected(
            lambda: compile_shared(Path(directory) / "wrong.so", cxx="/bin/false")
        )
        repository_candidate = Path(__file__).resolve().parent / ".forbidden-core.so"
        assert not repository_candidate.exists()
        expect_rejected(lambda: compile_shared(repository_candidate))

        for n_core in (4, 6):
            n_vectors = 3
            masks, required, weights = synthetic_constraints(n_core, n_vectors)
            n_ranks = core.factorial(n_core)
            one = core.enumerate_raw(
                n_core=n_core,
                input_masks=masks,
                required_outputs=required,
                n_vectors=n_vectors,
                weights=weights,
                rank_begin=0,
                rank_end=n_ranks,
                threads=1,
            )
            many = core.enumerate_raw(
                n_core=n_core,
                input_masks=masks,
                required_outputs=required,
                n_vectors=n_vectors,
                weights=weights,
                rank_begin=0,
                rank_end=n_ranks,
                threads=32,
            )
            scalar = core.enumerate_raw(
                n_core=n_core,
                input_masks=masks,
                required_outputs=required,
                n_vectors=n_vectors,
                weights=weights,
                rank_begin=0,
                rank_end=n_ranks,
                scalar=True,
            )
            assert one == many == scalar
            core.reset_traversal_audit()
            masked = core.enumerate_raw(
                n_core=n_core,
                input_masks=masks,
                required_outputs=required,
                n_vectors=n_vectors,
                weights=weights,
                rank_begin=1,
                rank_end=n_ranks,
                threads=32,
            )
            masked_audit = core.traversal_audit()
            assert masked == vector_mask(one, n_vectors, n_ranks, 1, n_ranks)
            assert len(masked) == n_vectors * (n_ranks - 1) * 4
            assert masked_audit["optimized_calls"] == 1
            assert masked_audit["constraint_traversals"] == len(masks)
            assert masked_audit["branches_considered"] > 0
            assert masked_audit["branches_pruned"] > 0
            assert masked_audit["completed_assignments"] > 0
            assert masked_audit["completed_rank_zero"] == 0
            for rank, expected_permutation in enumerate(
                itertools.permutations(range(n_core))
            ):
                permutation = core.unrank(n_core, rank)
                assert permutation == expected_permutation
                assert core.rank(permutation) == rank
            digests[f"toy_{n_core}_raw"] = hashlib.sha256(one).hexdigest()
            check_conjugation(core, one, n_core, n_vectors, masks, required, weights)

            order = list(range(len(masks)))
            random.Random(9000 + n_core).shuffle(order)
            reordered_masks = [masks[index] for index in order]
            reordered_required = [
                value
                for index in order
                for value in required[index * n_core:(index + 1) * n_core]
            ]
            reordered_weights = [
                value
                for index in order
                for value in weights[index * n_vectors:(index + 1) * n_vectors]
            ]
            reordered = core.enumerate_raw(
                n_core=n_core,
                input_masks=reordered_masks,
                required_outputs=reordered_required,
                n_vectors=n_vectors,
                weights=reordered_weights,
                rank_begin=0,
                rank_end=n_ranks,
                threads=32,
            )
            assert reordered == one

        # Exhaustive direct/pre-expanded equivalence on a synthetic code universe.
        keys = [
            core.encode_codes((1, 2)),
            core.encode_codes((5,)),
            core.encode_codes((8, 6)),
        ]
        direct_preimages = core.build_preimages(keys, DIRECT)
        affix_preimages = core.build_preimages(keys, DEPOSITED_AFFIX)
        alphabet = (1, 2, 5, 6, 7, 8, 12, 13, 14)
        skeletons = [
            core.encode_codes(codes)
            for length in range(1, 5)
            for codes in itertools.product(alphabet, repeat=length)
        ]
        assert core.check_preimage_equivalence(
            skeletons, keys, direct_preimages, DIRECT
        ) == 0
        assert core.check_preimage_equivalence(
            skeletons, keys, affix_preimages, DEPOSITED_AFFIX
        ) == 0
        assert core.direct_match(core.encode_codes((1, 2)), keys, DEPOSITED_AFFIX) == 1
        assert core.direct_match(core.encode_codes((12, 1, 2)), keys, DEPOSITED_AFFIX) == 2
        assert core.direct_match(core.encode_codes((12, 2, 1, 2)), keys, DEPOSITED_AFFIX) == 3
        assert core.direct_match(core.encode_codes((5, 1, 2)), keys, DEPOSITED_AFFIX) == 4
        assert core.direct_match(core.encode_codes((1, 2, 8, 6)), keys, DEPOSITED_AFFIX) == 5
        assert all(core.preimage_match(value, affix_preimages) for value in affix_preimages)
        # A panel frozenset is accepted only through deterministic sorted-unique
        # canonicalization in the wrapper.
        assert all(
            core.preimage_match(value, frozenset(affix_preimages))
            for value in affix_preimages
        )
        assert core.check_preimage_equivalence(
            skeletons,
            frozenset(keys),
            frozenset(affix_preimages),
            DEPOSITED_AFFIX,
        ) == 0
        digests["affix_preimages"] = hashlib.sha256(
            b"".join(value.to_bytes(8, "little") for value in affix_preimages)
        ).hexdigest()

        try:
            core.build_preimages([core.encode_codes((1,) * 9)], DEPOSITED_AFFIX)
        except Dani001CoreError as error:
            assert "OVERLENGTH_PREIMAGE" in str(error)
        else:
            raise AssertionError("overlength accepted preimage was not rejected")
        expect_rejected(lambda: core.encode_codes((15,)))

        # Every Python value crossing an unsigned ctypes boundary is checked
        # before conversion, including bool (an int subclass), negatives, and
        # oversized integers.
        unsigned_guard_calls = (
            lambda: core.factorial(-1),
            lambda: core.factorial(2**32),
            lambda: core.factorial(True),
            lambda: core.rank((-1,)),
            lambda: core.rank((256,)),
            lambda: core.rank((0, 0)),
            lambda: core.unrank(4, -1),
            lambda: core.unrank(4, 2**32),
            lambda: core.unrank(-1, 0),
            lambda: core.unrank(True, 0),
            lambda: core.unrank(4, True),
            lambda: core.encode_codes((-1,)),
            lambda: core.encode_codes((256,)),
            lambda: core.encode_codes((True,)),
            lambda: core.decode_codes(-1),
            lambda: core.decode_codes(2**64),
            lambda: core.decode_codes(True),
            lambda: core.direct_match(-1, keys, DIRECT),
            lambda: core.direct_match(2**64, keys, DIRECT),
            lambda: core.direct_match(keys[0], {-1}, DIRECT),
            lambda: core.direct_match(keys[0], {2**64}, DIRECT),
            lambda: core.direct_match(keys[0], {True}, DIRECT),
            lambda: core.direct_match(keys[0], keys, -1),
            lambda: core.direct_match(keys[0], keys, 2**32),
            lambda: core.build_preimages({-1}, DIRECT),
            lambda: core.build_preimages({2**64}, DIRECT),
            lambda: core.build_preimages({True}, DIRECT),
            lambda: core.build_preimages(keys, -1),
            lambda: core.build_preimages(keys, 2**32),
            lambda: core.preimage_match(-1, affix_preimages),
            lambda: core.preimage_match(2**64, affix_preimages),
            lambda: core.preimage_match(keys[0], {-1}),
            lambda: core.preimage_match(keys[0], {2**64}),
            lambda: core.preimage_match(keys[0], {True}),
            lambda: core.check_preimage_equivalence(
                {-1}, keys, affix_preimages, DEPOSITED_AFFIX
            ),
            lambda: core.check_preimage_equivalence(
                {2**64}, keys, affix_preimages, DEPOSITED_AFFIX
            ),
            lambda: core.check_preimage_equivalence(
                skeletons, keys, {-1}, DEPOSITED_AFFIX
            ),
            lambda: core.check_preimage_equivalence(
                skeletons, keys, {2**64}, DEPOSITED_AFFIX
            ),
            lambda: core.check_preimage_equivalence(
                skeletons, {-1}, affix_preimages, DEPOSITED_AFFIX
            ),
            lambda: core.check_preimage_equivalence(
                skeletons, {2**64}, affix_preimages, DEPOSITED_AFFIX
            ),
            lambda: core.check_preimage_equivalence(
                skeletons, keys, affix_preimages, -1
            ),
            lambda: core.check_preimage_equivalence(
                skeletons, keys, affix_preimages, 2**32
            ),
        )
        for guarded_call in unsigned_guard_calls:
            expect_rejected(guarded_call)

        # Constraint grammar and overflow guards.
        invalid_cases = (
            # Unassigned positions must be the exact 0xff sentinel.
            dict(
                n_core=4,
                input_masks=[1],
                required_outputs=[0, 0, 255, 255],
                n_vectors=1,
                weights=[1],
            ),
            # A partial bijection cannot reuse one output.
            dict(
                n_core=4,
                input_masks=[3],
                required_outputs=[0, 0, 255, 255],
                n_vectors=1,
                weights=[1],
            ),
            # A conservative all-constraints upper bound prevents uint32 wrap.
            dict(
                n_core=4,
                input_masks=[0, 1],
                required_outputs=[255] * 4 + [0, 255, 255, 255],
                n_vectors=1,
                weights=[2**32 - 1, 1],
            ),
        )
        for case in invalid_cases:
            try:
                core.enumerate_raw(
                    **case,
                    rank_begin=0,
                    rank_end=24,
                    threads=1,
                )
            except (Dani001CoreError, ValueError):
                pass
            else:
                raise AssertionError("malformed compiled constraint was not rejected")

        consolidated = core.enumerate_raw(
            n_core=4,
            input_masks=[1],
            required_outputs=[2, 255, 255, 255],
            n_vectors=1,
            weights=[5],
            rank_begin=0,
            rank_end=24,
            threads=1,
        )
        assert len(consolidated) == 24 * 4
        expect_rejected(
            lambda: core.enumerate_raw(
                n_core=4,
                input_masks=[1, 1],
                required_outputs=[2, 255, 255, 255] * 2,
                n_vectors=1,
                weights=[2, 3],
                rank_begin=0,
                rank_end=24,
                threads=32,
            )
        )

        valid_enumeration = {
            "n_core": 4,
            "input_masks": [1],
            "required_outputs": [2, 255, 255, 255],
            "n_vectors": 1,
            "weights": [1],
            "rank_begin": 0,
            "rank_end": 24,
            "threads": 1,
        }

        def rejected_enumeration(**changes: object) -> None:
            arguments = dict(valid_enumeration)
            arguments.update(changes)
            expect_rejected(lambda: core.enumerate_raw(**arguments))

        rejected_enumeration(n_core=-1)
        rejected_enumeration(n_core=2**32)
        rejected_enumeration(n_core=True)
        rejected_enumeration(n_vectors=-1)
        rejected_enumeration(n_vectors=2**32)
        rejected_enumeration(n_vectors=True)
        rejected_enumeration(input_masks=[-1])
        rejected_enumeration(input_masks=[2**16])
        rejected_enumeration(input_masks=[True])
        rejected_enumeration(input_masks=[16])
        rejected_enumeration(required_outputs=[-1, 255, 255, 255])
        rejected_enumeration(required_outputs=[256, 255, 255, 255])
        rejected_enumeration(required_outputs=[True, 255, 255, 255])
        rejected_enumeration(required_outputs=[4, 255, 255, 255])
        rejected_enumeration(required_outputs=[])
        rejected_enumeration(weights=[-1])
        rejected_enumeration(weights=[2**32])
        rejected_enumeration(weights=[True])
        rejected_enumeration(rank_begin=-1)
        rejected_enumeration(rank_begin=2**32)
        rejected_enumeration(rank_begin=True)
        rejected_enumeration(rank_end=-1)
        rejected_enumeration(rank_end=2**32)
        rejected_enumeration(rank_end=True)
        rejected_enumeration(threads=-1)
        rejected_enumeration(threads=2**32)
        rejected_enumeration(threads=True)
        rejected_enumeration(scalar=1)
        rejected_enumeration(n_core=7, rank_end=5040, scalar=True)

        # Full fake 10! nonidentity orbit: only anonymous integer constraints.
        n_core = 10
        n_vectors = 3
        masks, required, weights = synthetic_constraints(n_core, n_vectors)
        n_ranks = core.factorial(n_core)
        core.reset_traversal_audit()
        fake_one = core.enumerate_raw(
            n_core=n_core,
            input_masks=masks,
            required_outputs=required,
            n_vectors=n_vectors,
            weights=weights,
            rank_begin=1,
            rank_end=n_ranks,
            threads=1,
        )
        fake_one_audit = core.traversal_audit()
        assert fake_one_audit["optimized_calls"] == 1
        assert fake_one_audit["constraint_traversals"] == len(masks)
        assert fake_one_audit["branches_considered"] > 0
        assert fake_one_audit["branches_pruned"] > 0
        assert fake_one_audit["completed_assignments"] > 0
        assert fake_one_audit["completed_rank_zero"] == 0
        core.reset_traversal_audit()
        fake_many = core.enumerate_raw(
            n_core=n_core,
            input_masks=masks,
            required_outputs=required,
            n_vectors=n_vectors,
            weights=weights,
            rank_begin=1,
            rank_end=n_ranks,
            threads=32,
        )
        fake_many_audit = core.traversal_audit()
        assert fake_many_audit == fake_one_audit
        assert fake_one == fake_many
        assert len(fake_one) == n_vectors * (n_ranks - 1) * 4
        digests["fake_10_factorial_nonidentity"] = hashlib.sha256(fake_one).hexdigest()
        for rank in (0, 1, 2, 17, 999, n_ranks - 2, n_ranks - 1):
            assert core.rank(core.unrank(n_core, rank)) == rank

        return {
            "status": "PASS_SYNTHETIC_ONLY",
            "openmp_threads_compared": [1, 32],
            "toy_orbits": [24, 720],
            "fake_nonidentity_orbit": n_ranks - 1,
            "fake_vectors": n_vectors,
            "nonidentity_pruning_audit": fake_many_audit,
            "digests": digests,
            "real_panel_or_world_accessed": False,
        }


if __name__ == "__main__":
    print(json.dumps(run(), sort_keys=True, separators=(",", ":")))
