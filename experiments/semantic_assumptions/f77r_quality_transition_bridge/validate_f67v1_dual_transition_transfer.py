#!/usr/bin/env python3
"""Non-importing validation of the f67v1 dual-topology nonconfirmation."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
RESULT = Path(
    "experiments/semantic_assumptions/results/"
    "f67v1_dual_transition_transfer.json"
)
INTERLINEAR = Path(
    "experiments/semantic_assumptions/results/pre_grounding_interlinear.tsv"
)
ORDER = Path(
    "experiments/semantic_assumptions/f77r_quality_transition_bridge/"
    "F67V1_RADIAL_ORDER.tsv"
)
EDITIONS = ("ZL3b", "IT2a", "RF1b")


def tsv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def code(surface: str) -> str:
    value = "".join(surface.split())
    return ("1" if value.startswith("ot") else "0") + (
        "1" if value.endswith("y") else "0"
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    result_path = ROOT / RESULT
    result = json.loads(result_path.read_text(encoding="utf-8"))
    checks = []
    for relative, expected in result["inputs"].items():
        checks.append((f"hash:{relative}", sha(ROOT / relative) == expected))

    rows = tsv(ROOT / INTERLINEAR)
    order_rows = sorted(tsv(ROOT / ORDER), key=lambda row: int(row["order"]))
    by_locus = defaultdict(dict)
    for row in rows:
        by_locus[row["locus"]][row["edition"]] = row

    checks.append(("order_count", len(order_rows) == 17))
    checks.append(
        ("order_sequence", [int(row["order"]) for row in order_rows] == list(range(1, 18)))
    )
    expected_counts = {"ZL3b": (10, 7), "IT2a": (9, 8), "RF1b": (8, 9)}
    reconstructed = {}
    for edition in EDITIONS:
        sequence = [
            code(by_locus[row["locus"]][edition]["surface"]) for row in order_rows
        ]
        changes = [
            sequence[index] != sequence[(index + 1) % 17] for index in range(17)
        ]
        reconstructed[edition] = (sum(changes), 17 - sum(changes))
        stored = result["edition_results"][edition]
        checks.append((f"stored_bits:{edition}", sequence == stored["bit_sequence"]))
        checks.append(
            (
                f"stored_counts:{edition}",
                reconstructed[edition]
                == (
                    stored["changed_sector_boundaries"],
                    stored["unchanged_sector_boundaries"],
                ),
            )
        )
        checks.append((f"gate_fails:{edition}", not all(changes)))
    checks.append(("expected_counts", reconstructed == expected_counts))
    checks.append(("no_exact_counts", not result["source_scope"]["exact_star_counts_used"]))
    checks.append(
        (
            "decision_ceiling",
            result["decision"]["retain"]
            == "the narrower post-hoc f77r short-label tube-segment construction",
        )
    )

    failed = [name for name, passed in checks if not passed]
    validation = {
        "status": "PASS" if not failed else "FAIL",
        "nonimporting": True,
        "check_count": len(checks),
        "failed_checks": failed,
        "result_sha256": sha(result_path),
        "reconstructed_changed_unchanged": {
            edition: list(values) for edition, values in reconstructed.items()
        },
    }
    if failed:
        raise SystemExit(json.dumps(validation, indent=2))
    payload = json.dumps(validation, indent=2, sort_keys=True) + "\n"
    if args.output:
        output = args.output if args.output.is_absolute() else ROOT / args.output
        output.write_text(payload, encoding="utf-8")
    else:
        print(payload, end="")


if __name__ == "__main__":
    main()
