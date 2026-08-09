#!/usr/bin/env python3
"""Enumerate the declared f69r/Matthew 16-position class mappings."""

from __future__ import annotations

import json


N = 16
SOURCE = {
    "principal": frozenset({0, 4, 8, 12}),
    "collateral": frozenset(range(1, N, 2)),
    "unused": frozenset({2, 6, 10, 14}),
}
TARGET = {
    "principal": frozenset({2, 6, 10, 14}),  # green
    "collateral": frozenset(range(1, N, 2)),  # blue
    "unused": frozenset({0, 4, 8, 12}),  # blank
}


def transform(values: frozenset[int], offset: int, reflected: bool) -> frozenset[int]:
    sign = -1 if reflected else 1
    return frozenset((offset + sign * value) % N for value in values)


def main() -> None:
    matches = []
    for reflected in (False, True):
        for offset in range(N):
            if all(transform(SOURCE[key], offset, reflected) == TARGET[key] for key in SOURCE):
                matches.append({"offset": offset, "reflected": reflected})

    assert len(matches) == 8
    assert {row["offset"] for row in matches} == {2, 6, 10, 14}
    assert {row["reflected"] for row in matches} == {False, True}
    print(json.dumps({"dihedral_space": 32, "matching_mappings": matches, "n_matches": 8}, sort_keys=True))


if __name__ == "__main__":
    main()
