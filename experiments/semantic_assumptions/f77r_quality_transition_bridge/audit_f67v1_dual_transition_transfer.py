#!/usr/bin/env python3
"""Test the f77r state-change rule on the dual f67v1 sector topology."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
BASE = Path("experiments/semantic_assumptions/f77r_quality_transition_bridge")
INTERLINEAR = Path(
    "experiments/semantic_assumptions/results/pre_grounding_interlinear.tsv"
)
PAGE_ANNOTATIONS = Path(
    "experiments/semantic_assumptions/results/existing_human_page_annotations.tsv"
)
SOURCE_EVT = Path("transcription/sources/Stolfi_text25e1-52.evt")
DESIGN = BASE / "F67V1_DUAL_TRANSFER_DESIGN.md"
ORDER = BASE / "F67V1_RADIAL_ORDER.tsv"
EDITIONS = ("ZL3b", "IT2a", "RF1b")
STATES = {"10": "HOT", "01": "MOIST", "00": "COLD", "11": "DRY"}


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def state(surface: str) -> tuple[str, str]:
    compact = "".join(surface.split())
    code = f"{int(compact.startswith('ot'))}{int(compact.endswith('y'))}"
    return code, STATES[code]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    paths = {
        INTERLINEAR: ROOT / INTERLINEAR,
        PAGE_ANNOTATIONS: ROOT / PAGE_ANNOTATIONS,
        SOURCE_EVT: ROOT / SOURCE_EVT,
        DESIGN: ROOT / DESIGN,
        ORDER: ROOT / ORDER,
    }
    interlinear = read_tsv(paths[INTERLINEAR])
    page_rows = read_tsv(paths[PAGE_ANNOTATIONS])
    order_rows = sorted(read_tsv(paths[ORDER]), key=lambda row: int(row["order"]))
    source_text = paths[SOURCE_EVT].read_bytes().decode("latin-1")

    by_locus: dict[str, dict[str, dict[str, str]]] = defaultdict(dict)
    for row in interlinear:
        by_locus[row["locus"]][row["edition"]] = row

    page = [row for row in page_rows if row["page"] == "f67v1"]
    assert len(page) == 1
    assert "each segment has 1, 2 or 3 stars" in page[0]["illustrations"]
    assert len(order_rows) == 17
    assert [int(row["order"]) for row in order_rows] == list(range(1, 18))
    for row in order_rows:
        assert f"<{row['locus']};U>" in source_text

    edition_results = {}
    target_rows = []
    for edition in EDITIONS:
        codes = []
        names = []
        for order_row in order_rows:
            locus = order_row["locus"]
            source = by_locus[locus][edition]
            code, name = state(source["surface"])
            codes.append(code)
            names.append(name)
            target_rows.append(
                {
                    "edition": edition,
                    "order": int(order_row["order"]),
                    "locus": locus,
                    "surface": source["surface"],
                    "bits": code,
                    "f57_page_role_state": name,
                }
            )
        changes = [
            names[index] != names[(index + 1) % len(names)]
            for index in range(len(names))
        ]
        edition_results[edition] = {
            "bit_sequence": codes,
            "state_sequence": names,
            "changed_sector_boundaries": sum(changes),
            "unchanged_sector_boundaries": len(changes) - sum(changes),
            "unchanged_sector_positions": [
                index + 1 for index, changed in enumerate(changes) if not changed
            ],
            "universal_output_iff_change_gate": all(changes),
        }

    result = {
        "status": "FINAL_POSTHOC_NONCONFIRMATION_UNIVERSAL_DUAL_TOPOLOGY_TRANSFER",
        "inputs": {str(path): digest(real) for path, real in paths.items()},
        "source_scope": {
            "radial_texts": 17,
            "cyclic_sectors": 17,
            "all_sectors_star_bearing": True,
            "exact_star_counts_used": False,
        },
        "target_rows": target_rows,
        "edition_results": edition_results,
        "decision": {
            "reject": (
                "universal graphical-output iff adjacent f57-derived state-change "
                "under the f67v1 boundary/sector dual"
            ),
            "retain": (
                "the narrower post-hoc f77r short-label tube-segment construction"
            ),
            "forbid": (
                "no star count quality element ot y lexeme plaintext or translation"
            ),
        },
    }

    assert {
        edition: (
            value["changed_sector_boundaries"],
            value["unchanged_sector_boundaries"],
        )
        for edition, value in edition_results.items()
    } == {"ZL3b": (10, 7), "IT2a": (9, 8), "RF1b": (8, 9)}
    assert not any(
        value["universal_output_iff_change_gate"]
        for value in edition_results.values()
    )

    payload = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.output:
        output = args.output if args.output.is_absolute() else ROOT / args.output
        output.write_text(payload, encoding="utf-8")
    else:
        print(payload, end="")


if __name__ == "__main__":
    main()
