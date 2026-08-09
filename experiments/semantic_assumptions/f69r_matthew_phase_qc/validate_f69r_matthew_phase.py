#!/usr/bin/env python3
"""Independent scalar reconstruction of the f69r/Matthew phase count."""

from __future__ import annotations


def label_source(position: int) -> str:
    if position % 4 == 0:
        return "principal"
    if position % 2 == 1:
        return "collateral"
    return "unused"


def label_target(position: int) -> str:
    if position % 4 == 0:
        return "unused"
    if position % 2 == 1:
        return "collateral"
    return "principal"


def main() -> None:
    accepted = []
    for reflected in (0, 1):
        for offset in range(16):
            sign = -1 if reflected else 1
            if all(label_source(i) == label_target((offset + sign * i) % 16) for i in range(16)):
                accepted.append((offset, bool(reflected)))
    assert accepted == [
        (2, False), (6, False), (10, False), (14, False),
        (2, True), (6, True), (10, True), (14, True),
    ]
    print("PASS 8_OF_32_PHASE_AMBIGUOUS_MATCH")


if __name__ == "__main__":
    main()
