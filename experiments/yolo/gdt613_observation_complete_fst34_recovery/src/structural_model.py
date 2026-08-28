#!/usr/bin/env python3
"""Exact structural feasibility model for the registered GDT613 gates."""
from __future__ import annotations

import csv
import hashlib
import itertools
import json
from collections import Counter
from functools import lru_cache
from pathlib import Path

import z3


ROLE_ORDER = ("L", "Y", "P", "U", "C", "X", "W", "N")
ROLE_NAMES = {
    "L": "literal_carrier",
    "Y": "syllabic_carrier",
    "P": "prefix_operator",
    "U": "suffix_operator",
    "C": "connector",
    "X": "context_abbreviation_mark",
    "W": "wholeform_logogram",
    "N": "null_layout",
}
ROLE_COUNTS = {"L": 18, "Y": 4, "P": 3, "U": 3, "C": 2, "X": 2, "W": 1, "N": 1}
RID = {role: index for index, role in enumerate(ROLE_ORDER)}
PAD = len(ROLE_ORDER)
MAX_LEAF_COUNT = 6

RELATIVE_INPUTS = {
    "merge_tree": Path(
        "experiments/yolo/gdt608_compositional_stem_orientation/artifacts/merge_tree.tsv"
    ),
    "model": Path(
        "experiments/yolo/gdt609_historical_mixed_abbreviation_prior/artifacts/model_v1.json"
    ),
    "primitives": Path(
        "experiments/yolo/gdt612_historical_fst34_target_attack/artifacts/primitives.tsv"
    ),
}
EXPECTED_HASHES = {
    "merge_tree": "2098c71be9da13b483cf2561e06412276d8c60aa32e72520e8877f8f5d53090a",
    "model": "0c9219bd02e063758806b58a174cbf546fdf0f3c5853ed3c98dcfa422abbe5f0",
    "primitives": "3a5e89dbd89c5c833db4884cadff0ccbdc438e9ce8e832be0bc1b7e3df636ae6",
}

# A separately validated SAT witness for the control that removes only the
# card-child gate.  The unconstrained SAT query is still executed; freezing a
# witness prevents Z3's arbitrary model choice from changing public artifacts.
RELAXED_WITNESS_ROLES = {
    "C": "L", "E": "U", "F": "P", "I": "Y", "K": "Y", "N": "Y",
    "P": "L", "S": "L", "T": "Y", "a": "C", "b": "P", "c": "L",
    "d": "U", "e": "X", "f": "L", "g": "L", "h": "L", "i": "L",
    "j": "L", "k": "L", "l": "X", "m": "L", "n": "L", "o": "C",
    "p": "U", "q": "L", "r": "L", "s": "P", "t": "L", "u": "W",
    "v": "L", "x": "L", "y": "N", "z": "L",
}
RELAXED_WITNESS_CARDS = {
    "So": "short", "air": "short", "daI": "short", "daN": "short",
    "dal": "whole", "dar": "whole", "eol": "whole", "yk": "whole",
}
RAW_MAX60_WITNESS_ROLES = {
    **{name: "L" for name in ("C", "F", "N", "P", "S", "T", "b", "c", "f", "g", "h", "j", "k", "n", "r", "u", "v", "x")},
    **{name: "Y" for name in ("I", "p", "q", "t")},
    **{name: "P" for name in ("i", "m", "z")},
    **{name: "U" for name in ("E", "K", "d")},
    **{name: "C" for name in ("a", "o")},
    **{name: "X" for name in ("e", "l")},
    "s": "W",
    "y": "N",
}


def constrain_witness(solver, variables, roles, cards) -> None:
    for name, role in roles.items():
        solver.add(variables["primitive_role"][name] == RID[role])
    for name in variables["short"]:
        solver.add(variables["short"][name] == (cards.get(name) == "short"))
        solver.add(variables["whole"][name] == (cards.get(name) == "whole"))


def build_raw_leaf_solver(rows, primitive_names, timeout_ms: int = 600_000):
    patterns = valid_substrings()
    solver = z3.Solver()
    solver.set(timeout=timeout_ms, random_seed=613)
    variables = {name: z3.Int(f"raw_role_{name}") for name in primitive_names}
    for value in variables.values():
        solver.add(value >= 0, value < len(ROLE_ORDER))
    for role, count in ROLE_COUNTS.items():
        solver.add(
            z3.Sum([z3.If(value == RID[role], 1, 0) for value in variables.values()])
            == count
        )
    accepted = {}
    for row in rows:
        leaves = row["leaf_sequence"].split()
        accepted[row["merged"]] = z3.Or(
            *[
                z3.And(*[variables[name] == RID[role] for name, role in zip(leaves, pattern)])
                for pattern in patterns[len(leaves)]
            ]
        )
    return solver, variables, accepted


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def load_inputs(repo: Path):
    paths = {name: repo / relative for name, relative in RELATIVE_INPUTS.items()}
    hashes = {name: sha256(path) for name, path in paths.items()}
    if hashes != EXPECTED_HASHES:
        raise RuntimeError(f"source drift: {hashes}")
    rows = read_tsv(paths["merge_tree"])
    primitive_rows = read_tsv(paths["primitives"])
    model = json.loads(paths["model"].read_text(encoding="utf-8"))
    primitive_names = [row["primitive"] for row in primitive_rows]
    if len(rows) != 64 or len(primitive_names) != 34 or len(set(primitive_names)) != 34:
        raise RuntimeError("unexpected 34/64 capacity")
    if max(int(row["leaf_count"]) for row in rows) != MAX_LEAF_COUNT:
        raise RuntimeError("unexpected maximum merge leaf count")
    model_counts = {
        row["role"]: int(row["count"])
        for row in model["primitive_capacity"]["buckets"]
    }
    expected_model_counts = {ROLE_NAMES[role]: count for role, count in ROLE_COUNTS.items()}
    if model_counts != expected_model_counts:
        raise RuntimeError("registered role deck drift")
    return rows, primitive_names, hashes


def query_fingerprint(rows, *, skip_card_child_gate: bool, forbid_all_qok_whole: bool) -> str:
    payload = {
        "schema": "gdt613-structural-query-v1",
        "role_order": ROLE_ORDER,
        "role_counts": ROLE_COUNTS,
        "short_cards": 4,
        "whole_cards": 4,
        "short_transition": "Y",
        "whole_transition": "W",
        "skip_card_child_gate": skip_card_child_gate,
        "forbid_all_qok_whole": forbid_all_qok_whole,
        "exact_qok_whole_forbidden": True,
        "patterns": {
            str(length): valid_substrings()[length]
            for length in sorted(valid_substrings())
        },
        "merges": [
            {
                "rank": int(row["rank"]),
                "left": row["left"],
                "right": row["right"],
                "merged": row["merged"],
                "leaves": row["leaf_sequence"].split(),
            }
            for row in rows
        ],
    }
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


@lru_cache(maxsize=None)
def valid_substrings(max_length: int = MAX_LEAF_COUNT) -> dict[int, tuple[tuple[str, ...], ...]]:
    """Every role string embeddable in one exact GDT609 chunk.

    NULL is allowed as an unbounded run at either edge.  The exact role deck
    later limits an assignment to one NULL primitive, but the language itself
    is enumerated without relying on that fact.
    """
    cores = (("L",), ("Y",), ("X", "L"), ("L", "X"))
    complete: set[tuple[str, ...]] = {("C",), ("C", "U")}
    for leading_connector in ((), ("C",)):
        for trailing_connector in ((), ("C",)):
            complete.add(leading_connector + ("W",) + trailing_connector)
            for prefix_count in range(3):
                for core_count in range(1, 5):
                    for selected_cores in itertools.product(cores, repeat=core_count):
                        middle: tuple[str, ...] = ()
                        for index, core in enumerate(selected_cores):
                            if index:
                                middle += ("C",)
                            middle += core
                        for suffix_count in range(3):
                            complete.add(
                                leading_connector
                                + ("P",) * prefix_count
                                + middle
                                + ("U",) * suffix_count
                                + trailing_connector
                            )
    with_null = {
        ("N",) * left + sequence + ("N",) * right
        for sequence in complete
        for left in range(max_length + 1)
        for right in range(max_length + 1)
    }
    result: dict[int, set[tuple[str, ...]]] = {
        length: set() for length in range(1, max_length + 1)
    }
    for sequence in with_null:
        for length in result:
            for begin in range(0, len(sequence) - length + 1):
                result[length].add(sequence[begin : begin + length])
    return {length: tuple(sorted(patterns)) for length, patterns in result.items()}


@lru_cache(maxsize=None)
def valid_complete_strings(max_length: int = MAX_LEAF_COUNT) -> set[tuple[str, ...]]:
    """Exact complete GDT609 role strings through a finite audit length."""
    cores = (("L",), ("Y",), ("X", "L"), ("L", "X"))
    payloads: set[tuple[str, ...]] = {("C",), ("C", "U")}
    for leading_connector in ((), ("C",)):
        for trailing_connector in ((), ("C",)):
            payloads.add(leading_connector + ("W",) + trailing_connector)
            for prefix_count in range(3):
                for core_count in range(1, 5):
                    for selected_cores in itertools.product(cores, repeat=core_count):
                        middle: tuple[str, ...] = ()
                        for index, core in enumerate(selected_cores):
                            middle += (("C",) if index else ()) + core
                        for suffix_count in range(3):
                            payloads.add(
                                leading_connector
                                + ("P",) * prefix_count
                                + middle
                                + ("U",) * suffix_count
                                + trailing_connector
                            )
    return {
        ("N",) * left + payload + ("N",) * right
        for payload in payloads
        for left in range(max_length + 1)
        for right in range(max_length + 1)
        if 1 <= left + len(payload) + right <= max_length
    }


def _concat_vectors(left_length, left_vector, right_length, right_vector):
    total = left_length + right_length
    output = []
    for position in range(MAX_LEAF_COUNT):
        expression = z3.IntVal(PAD)
        for boundary in reversed(range(1, MAX_LEAF_COUNT + 1)):
            value = left_vector[position] if position < boundary else right_vector[position - boundary]
            expression = z3.If(left_length == boundary, value, expression)
        output.append(z3.If(position < total, expression, PAD))
    return total, output


def _accepted(length, vector, patterns_by_length):
    return z3.Or(
        *[
            z3.And(
                length == size,
                *[vector[index] == RID[role] for index, role in enumerate(pattern)],
            )
            for size, patterns in patterns_by_length.items()
            for pattern in patterns
        ]
    )


def build_solver(
    rows,
    primitive_names,
    *,
    skip_card_child_gate: bool,
    forbid_all_qok_whole: bool,
    timeout_ms: int = 600_000,
):
    patterns = valid_substrings()
    solver = z3.Solver()
    solver.set(timeout=timeout_ms, random_seed=613)
    primitive_role = {name: z3.Int(f"role_{name}") for name in primitive_names}
    for value in primitive_role.values():
        solver.add(value >= 0, value < len(ROLE_ORDER))
    for role, count in ROLE_COUNTS.items():
        solver.add(
            z3.Sum([z3.If(value == RID[role], 1, 0) for value in primitive_role.values()])
            == count
        )

    lengths = {name: z3.IntVal(1) for name in primitive_names}
    vectors = {
        name: [primitive_role[name]] + [z3.IntVal(PAD)] * (MAX_LEAF_COUNT - 1)
        for name in primitive_names
    }
    short: dict[str, z3.BoolRef] = {}
    whole: dict[str, z3.BoolRef] = {}
    child_compositions = {}
    effective_compositions = {}
    for row in rows:
        name, left, right = row["merged"], row["left"], row["right"]
        short[name] = z3.Bool(f"short_{name}")
        whole[name] = z3.Bool(f"whole_{name}")
        solver.add(z3.Not(z3.And(short[name], whole[name])))
        if name == "qok" or (forbid_all_qok_whole and name.startswith("qok")):
            solver.add(z3.Not(whole[name]))
        is_card = z3.Or(short[name], whole[name])
        child_length, child_vector = _concat_vectors(
            lengths[left], vectors[left], lengths[right], vectors[right]
        )
        solver.add(child_length <= MAX_LEAF_COUNT)
        child_compositions[name] = (child_length, child_vector)
        child_accepted = _accepted(child_length, child_vector, patterns)
        solver.add(
            z3.Implies(z3.Not(is_card), child_accepted)
            if skip_card_child_gate
            else child_accepted
        )
        node_length = z3.Int(f"len_{name}")
        node_vector = [z3.Int(f"seq_{name}_{index}") for index in range(MAX_LEAF_COUNT)]
        solver.add(node_length == z3.If(is_card, 1, child_length))
        for index in range(MAX_LEAF_COUNT):
            card_role = z3.If(short[name], RID["Y"], z3.If(whole[name], RID["W"], PAD))
            solver.add(
                node_vector[index]
                == z3.If(is_card, card_role if index == 0 else PAD, child_vector[index])
            )
        lengths[name], vectors[name] = node_length, node_vector
        effective_compositions[name] = (node_length, node_vector)
    solver.add(z3.Sum([z3.If(value, 1, 0) for value in short.values()]) == 4)
    solver.add(z3.Sum([z3.If(value, 1, 0) for value in whole.values()]) == 4)
    variables = {
        "primitive_role": primitive_role,
        "short": short,
        "whole": whole,
        "child": child_compositions,
        "effective": effective_compositions,
    }
    return solver, variables, patterns


def _model_sequence(model, length_expression, vector):
    length = model.eval(length_expression).as_long()
    return [ROLE_ORDER[model.eval(vector[index]).as_long()] for index in range(length)]


def extract_witness(model, rows, variables, patterns):
    roles = {
        name: ROLE_ORDER[model.eval(variable).as_long()]
        for name, variable in variables["primitive_role"].items()
    }
    cards = {}
    merges = []
    for row in rows:
        name = row["merged"]
        if z3.is_true(model.eval(variables["short"][name])):
            cards[name] = "short"
        elif z3.is_true(model.eval(variables["whole"][name])):
            cards[name] = "whole"
        child = _model_sequence(model, *variables["child"][name])
        effective = _model_sequence(model, *variables["effective"][name])
        merges.append(
            {
                "unit": name,
                "child_role_sequence": child,
                "child_embeddable": tuple(child) in patterns[len(child)],
                "effective_role_sequence": effective,
                "card": cards.get(name, "none"),
            }
        )
    return {
        "roles": roles,
        "role_counts": dict(sorted(Counter(roles.values()).items())),
        "cards": dict(sorted(cards.items())),
        "merges": merges,
    }
