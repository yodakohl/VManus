#!/usr/bin/env python3
"""Build the immutable train-only substring table used by GDT615 Stage 0."""

from __future__ import annotations

import argparse
import hashlib
from pathlib import Path


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
EXP = ROOT / "experiments/yolo/gdt615_joint_output_permutation_recovery"
TRAIN = (
    ROOT
    / "experiments/yolo/gdt613_observation_complete_fst34_recovery/artifacts/reference_splits/synthetic_train.txt"
)
OUTPUT = EXP / "artifacts/REGISTERED_TRAIN_SUBSTRINGS.txt"
MIN_LENGTH = 1
MAX_LENGTH = 12


def digest_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def build_payload() -> bytes:
    words = TRAIN.read_text(encoding="ascii").splitlines()
    if not words or any(not word for word in words):
        raise AssertionError("train must contain one nonempty plaintext type per line")
    substrings = {
        word[start : start + length]
        for word in set(words)
        for length in range(MIN_LENGTH, min(MAX_LENGTH, len(word)) + 1)
        for start in range(len(word) - length + 1)
    }
    ordered = sorted(substrings, key=lambda value: (len(value), value))
    return ("\n".join(ordered) + "\n").encode("ascii")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    payload = build_payload()
    if args.check:
        if not OUTPUT.is_file() or OUTPUT.read_bytes() != payload:
            raise AssertionError("registered train substring table is stale")
    else:
        OUTPUT.parent.mkdir(parents=True, exist_ok=True)
        OUTPUT.write_bytes(payload)
    count = payload.count(b"\n")
    print(f"TRAIN_SUBSTRINGS count={count} sha256={digest_bytes(payload)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
