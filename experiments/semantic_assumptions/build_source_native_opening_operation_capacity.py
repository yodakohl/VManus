#!/usr/bin/env python3
"""Score-blind capacity for nested opening operations on exact remainders."""

from __future__ import annotations

import csv
import hashlib
import itertools
import json
import re
from collections import Counter, defaultdict
from pathlib import Path


BASE = Path(__file__).resolve().parent
RESULTS = BASE / "results"
SOURCE = RESULTS / "source_sta_family_consensus_groups.tsv"
PATH_ATLAS = RESULTS / "source_native_construction_path_atlas.json"
PATH_VALIDATION = RESULTS / "source_native_construction_path_atlas_validation.json"
SPEC = BASE / "SOURCE_NATIVE_OPENING_OPERATION_CAPACITY_SPEC.md"
BUILDER = Path(__file__).resolve()
OUT_TSV = RESULTS / "source_native_opening_operation_capacity.tsv"
OUT_JSON = RESULTS / "source_native_opening_operation_capacity.json"
OUT_REPORT = RESULTS / "source_native_opening_operation_capacity_report.md"
FROZEN = {
    SOURCE: "a202d93498e8a350a5d7e0ca46e831dcc37ea5c0182dc404d63cb797a98b1225",
    PATH_ATLAS: "22a5575582b6a45f6b469ea648dfc1a111c581c32c975c45a6edb89df21995ca",
    PATH_VALIDATION: "a7a254a5041495f09615c9681ae5d0bb83686698569314e30e16c66168f46e58",
    SPEC: "f3edf68c4e8830ec6195249ef9a065c12fa4634d2300c42f1a45bca1759d79c2",
}
OPERATIONS = ("NONE", "DA", "DAQ", "DAQK", "DAQKJ")
PREFIXES = ("DAQKJ", "DAQK", "DAQ", "DA")
FIELDS = (
    "pair_id",
    "left_operation",
    "right_operation",
    "shared_exact_remainders",
    "two_folio_per_operation_remainders",
    "left_groups_on_shared_remainders",
    "right_groups_on_shared_remainders",
    "union_physical_folios",
    "currier_A_shared_remainders",
    "currier_B_shared_remainders",
    "capacity_eligible",
)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def folio(page: str) -> str:
    match = re.fullmatch(r"(f\d+)[rv]\d*", page)
    if match is None:
        raise ValueError("page")
    return match.group(1)


def split_operation(surface: str) -> tuple[str, str]:
    for prefix in PREFIXES:
        if surface.startswith(prefix):
            return prefix, surface[len(prefix):]
    return "NONE", surface


def main() -> None:
    if any(path.exists() for path in (OUT_TSV, OUT_JSON, OUT_REPORT)):
        raise SystemExit("refusing overwrite")
    for path, expected in FROZEN.items():
        if sha(path) != expected:
            raise SystemExit(f"frozen mismatch: {path.name}")
    if json.loads(PATH_VALIDATION.read_text())["status"] != "PASS_INDEPENDENT_13_PATH_CONSTRUCTION_RECONSTRUCTION":
        raise SystemExit("path validation")
    with SOURCE.open(encoding="utf-8", newline="") as handle:
        source_rows = list(csv.DictReader(handle, delimiter="\t"))
    rows = [row for row in source_rows if row["strict_zero_alternative"] == "1" and row["grammar_scope"] == "CONFIRMED_PROSE"]
    if len(source_rows) != 26184 or len(rows) != 21899 or len({row["consensus_group_id"] for row in rows}) != 21899:
        raise SystemExit("source identity")
    by_remainder = defaultdict(lambda: defaultdict(list))
    operation_groups = Counter()
    empty_remainders = Counter()
    for row in rows:
        surface = row["family_surface"]
        if not surface or len(surface) != int(row["symbol_count"]):
            raise SystemExit("surface")
        operation, remainder = split_operation(surface)
        operation_groups[operation] += 1
        if not remainder:
            empty_remainders[operation] += 1
            continue
        by_remainder[remainder][operation].append(
            (row["consensus_group_id"], folio(row["page"]), row["currier"])
        )
    output_rows = []
    for left, right in itertools.combinations(OPERATIONS, 2):
        shared = {base for base, states in by_remainder.items() if left in states and right in states}
        replicated = {
            base for base in shared
            if len({value[1] for value in by_remainder[base][left]}) >= 2
            and len({value[1] for value in by_remainder[base][right]}) >= 2
        }
        left_values = [value for base in shared for value in by_remainder[base][left]]
        right_values = [value for base in shared for value in by_remainder[base][right]]
        folios = {value[1] for value in left_values + right_values}
        by_currier = {
            currier: sum(
                any(value[2] == currier for value in by_remainder[base][left])
                and any(value[2] == currier for value in by_remainder[base][right])
                for base in shared
            )
            for currier in ("A", "B")
        }
        eligible = (
            len(shared) >= 20
            and len(replicated) >= 10
            and len(left_values) >= 50
            and len(right_values) >= 50
            and len(folios) >= 20
            and min(by_currier.values()) >= 5
        )
        output_rows.append(
            {
                "pair_id": f"{left}__{right}",
                "left_operation": left,
                "right_operation": right,
                "shared_exact_remainders": len(shared),
                "two_folio_per_operation_remainders": len(replicated),
                "left_groups_on_shared_remainders": len(left_values),
                "right_groups_on_shared_remainders": len(right_values),
                "union_physical_folios": len(folios),
                "currier_A_shared_remainders": by_currier["A"],
                "currier_B_shared_remainders": by_currier["B"],
                "capacity_eligible": int(eligible),
            }
        )
    passing = [row for row in output_rows if row["capacity_eligible"]]
    passing.sort(
        key=lambda row: (
            -row["two_folio_per_operation_remainders"],
            -min(row["left_groups_on_shared_remainders"], row["right_groups_on_shared_remainders"]),
            -row["union_physical_folios"],
            row["pair_id"],
        )
    )
    selected = passing[0]["pair_id"] if passing else None
    with OUT_TSV.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(output_rows)
    result = {
        "experiment": "SOURCE_NATIVE_OPENING_OPERATION_CAPACITY",
        "status": "PASS_SCORE_BLIND_OPENING_OPERATION_CAPACITY" if selected else "STOP_INSUFFICIENT_OPENING_OPERATION_CAPACITY",
        "decision": "FREEZE_ONE_HELD_CONTEXT_PREFLIGHT" if selected else "DO_NOT_SCORE_OPENING_OPERATION_CONTEXT",
        "inputs": {path.name: sha(path) for path in (*FROZEN, BUILDER)},
        "source_groups": len(rows),
        "operation_group_counts": {operation: operation_groups[operation] for operation in OPERATIONS},
        "empty_remainder_counts": {operation: empty_remainders[operation] for operation in OPERATIONS},
        "nonempty_exact_remainders": len(by_remainder),
        "operation_pairs": len(output_rows),
        "eligible_operation_pairs": [row["pair_id"] for row in passing],
        "selected_operation_pair": selected,
        "tsv_sha256": sha(OUT_TSV),
        "remainder_identities_stored": 0,
        "context_fields_accessed": 0,
        "context_scores_computed": 0,
        "english_glosses": 0,
        "claim_ceiling": "Score-blind exact-remainder capacity only; no detachment, wordhood, prefix meaning, sound, language, cipher operation, plaintext, or translation follows.",
    }
    OUT_JSON.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    best = passing[0] if passing else max(output_rows, key=lambda row: (row["two_folio_per_operation_remainders"], min(row["left_groups_on_shared_remainders"], row["right_groups_on_shared_remainders"]), row["union_physical_folios"], row["pair_id"]))
    OUT_REPORT.write_text(
        f"""# Source-native opening-operation capacity

Status: **{result['status']}**

The longest-prefix split assigns all **{len(rows):,}** strict prose groups to
`NONE/DA/DAQ/DAQK/DAQKJ` without opening any external-context outcome. Of ten
operation pairs, **{len(passing)}** pass the frozen capacity gates. The selected
pair is **{selected or 'NONE'}**. The strongest capacity row `{best['pair_id']}`
has **{best['shared_exact_remainders']}** shared exact remainders,
**{best['two_folio_per_operation_remainders']}** replicated on at least two
folios per operation, and **{best['left_groups_on_shared_remainders']} /
{best['right_groups_on_shared_remainders']}** groups across
**{best['union_physical_folios']}** folios.

This is capacity for one separately frozen structural-context preflight only.
It supplies no detachment, wordhood, prefix meaning, sound, language, cipher,
plaintext, or translation.
"""
    )
    print(json.dumps({"status": result["status"], "eligible_pairs": len(passing), "selected_pair": selected}, sort_keys=True))


if __name__ == "__main__":
    main()
