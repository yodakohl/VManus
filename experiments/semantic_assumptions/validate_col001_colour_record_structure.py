#!/usr/bin/env python3
"""Independent compact validator for the COL001 formal-record audit."""

from __future__ import annotations

import csv
import hashlib
import json
from collections import defaultdict
from pathlib import Path
from typing import Callable


REPO = Path(__file__).resolve().parents[2]
INTERLINEAR = REPO / "experiments/semantic_assumptions/results/pre_grounding_interlinear.tsv"
ANNOTATIONS = REPO / "experiments/semantic_assumptions/results/existing_human_exact_locus_annotations.tsv"
RESULT = REPO / "experiments/semantic_assumptions/results/col001_colour_record_structure.json"
OUTPUT = REPO / "experiments/semantic_assumptions/results/col001_colour_record_structure_validation.json"

EXPECTED_HASHES = {
    INTERLINEAR: "8052a51fa37ad467e754be39648336ec4014442dab5e223daab2e77efaba4a43",
    ANNOTATIONS: "79c7f06e91f90054aff4cdf27f098a5977d820acdf91f239a14c6ddf553a7f61",
    RESULT: "92b9bcd7edaf8b5361e5558546bcc86a30b7d8743d98b84df2c6c15625a34b79",
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def load_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as source:
        return list(csv.DictReader(source, delimiter="\t"))


def select(
    rows: list[dict[str, str]], predicate: Callable[[list[str], dict[str, str]], bool]
) -> list[dict[str, str]]:
    return [row for row in rows if predicate(row["root_sequence"].split(), row)]


def summary(rows: list[dict[str, str]]) -> dict[str, int]:
    support: dict[str, set[str]] = defaultdict(set)
    for row in rows:
        support[row["locus"]].add(row["edition"])
    return {
        "edition_rows": len(rows),
        "physical_loci": len(support),
        "two_or_more_readings": sum(len(value) >= 2 for value in support.values()),
        "all_three_readings": sum(len(value) == 3 for value in support.values()),
    }


def support_sets(rows: list[dict[str, str]]) -> dict[str, list[str]]:
    support: dict[str, set[str]] = defaultdict(set)
    for row in rows:
        support[row["locus"]].add(row["edition"])
    return {key: sorted(value) for key, value in sorted(support.items())}


def main() -> int:
    observed_hashes = {path: sha256(path) for path in EXPECTED_HASHES}
    require(observed_hashes == EXPECTED_HASHES, "frozen source/result hash mismatch")
    rows = load_tsv(INTERLINEAR)
    annotations = load_tsv(ANNOTATIONS)
    result = json.loads(RESULT.read_text(encoding="utf-8"))
    require(len(rows) == 15_960, "interlinear row-count mismatch")
    require(len(annotations) == 1_192, "human annotation row-count mismatch")

    root_i_os = select(rows, lambda roots, _row: "i+os" in roots)
    root_a = select(rows, lambda roots, _row: "a" in roots)
    root_o = select(rows, lambda roots, _row: "o" in roots)
    pair_ao = select(
        rows,
        lambda roots, _row: any(roots[index:index + 2] == ["a", "o"] for index in range(len(roots) - 1)),
    )
    pair_oa = select(
        rows,
        lambda roots, _row: any(roots[index:index + 2] == ["o", "a"] for index in range(len(roots) - 1)),
    )
    shell = select(rows, lambda _roots, row: row["role_sequence"] == "BARE+BARE BARE BARE")
    near = select(
        rows,
        lambda roots, _row: len(roots) == 3 and roots[0].endswith("+os") and roots[2] == "o",
    )
    f2 = [row for row in rows if row["locus"] == "f2r.15"]

    expected_summaries = {
        "i_plus_os": {"edition_rows": 2, "physical_loci": 1, "two_or_more_readings": 1, "all_three_readings": 0},
        "a": {"edition_rows": 934, "physical_loci": 408, "two_or_more_readings": 294, "all_three_readings": 232},
        "o": {"edition_rows": 1952, "physical_loci": 874, "two_or_more_readings": 609, "all_three_readings": 469},
        "a_to_o": {"edition_rows": 12, "physical_loci": 6, "two_or_more_readings": 4, "all_three_readings": 2},
        "o_to_a": {"edition_rows": 13, "physical_loci": 9, "two_or_more_readings": 2, "all_three_readings": 2},
        "shell": {"edition_rows": 9, "physical_loci": 5, "two_or_more_readings": 3, "all_three_readings": 1},
        "near": {"edition_rows": 4, "physical_loci": 2, "two_or_more_readings": 2, "all_three_readings": 0},
    }
    observed_summaries = {
        "i_plus_os": summary(root_i_os),
        "a": summary(root_a),
        "o": summary(root_o),
        "a_to_o": summary(pair_ao),
        "o_to_a": summary(pair_oa),
        "shell": summary(shell),
        "near": summary(near),
    }
    require(observed_summaries == expected_summaries, "reconstructed count mismatch")
    require(
        support_sets(near) == {
            "f2r.15": ["RF1b", "ZL3b"],
            "f67r2.40": ["IT2a", "ZL3b"],
        },
        "close-parallel locus/readings mismatch",
    )
    require(
        len(f2) == 2
        and all(row["surface"] == "ios an on" for row in f2)
        and all(row["root_sequence"] == "i+os a o" for row in f2)
        and all(row["role_sequence"] == "BARE+BARE BARE BARE" for row in f2),
        "f2r.15 formal record mismatch",
    )

    require(result["status"] == "PASS_SLOT_NARROWING_STOP_LEXICAL", "result status mismatch")
    require(result["component_support"]["i_plus_os"] == expected_summaries["i_plus_os"], "i+os result mismatch")
    require(result["component_support"]["a"] == expected_summaries["a"], "a result mismatch")
    require(result["component_support"]["o"] == expected_summaries["o"], "o result mismatch")
    for name in ("a_to_o", "o_to_a"):
        for key, value in expected_summaries[name].items():
            require(result["adjacent_root_pairs"][name][key] == value, f"{name}.{key} mismatch")
    for key, value in expected_summaries["shell"].items():
        require(result["formal_shell"][key] == value, f"shell.{key} mismatch")
    for key, value in expected_summaries["near"].items():
        require(result["three_root_first_plus_os_final_o"][key] == value, f"near.{key} mismatch")
    require(result["gates"] == {
        "f2r15_a_to_o_repeats_outside_f2r": True,
        "f2r15_i_plus_os_is_locus_unique": True,
        "formal_shell_is_instruction_specific": False,
        "lexical_gloss_authorized": False,
    }, "claim-gate mismatch")
    require(not any(result["prohibited_inputs"].values()), "prohibited-input flag mismatch")

    validation = {
        "experiment": "COL001_FORMAL_RECORD_AUDIT",
        "validator_status": "PASS_INDEPENDENT_RECONSTRUCTION",
        "checks": 27,
        "input_sha256": {
            str(path.relative_to(REPO)): digest
            for path, digest in observed_hashes.items()
        },
        "reconstructed_summaries": observed_summaries,
        "close_parallel_support": support_sets(near),
        "lexical_gloss_authorized": False,
        "prohibited_inputs_accessed": False,
    }
    OUTPUT.write_text(
        json.dumps(validation, indent=2, sort_keys=True, ensure_ascii=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps({
        "status": validation["validator_status"],
        "checks": validation["checks"],
        "output": str(OUTPUT.relative_to(REPO)),
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
