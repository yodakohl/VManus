#!/usr/bin/env python3
"""Clean-room validation of opening-operation exact-remainder capacity."""

from __future__ import annotations

import csv
import hashlib
import io
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
BUILDER = BASE / "build_source_native_opening_operation_capacity.py"
TSV = RESULTS / "source_native_opening_operation_capacity.tsv"
PRODUCTION = RESULTS / "source_native_opening_operation_capacity.json"
PRODUCTION_REPORT = RESULTS / "source_native_opening_operation_capacity_report.md"
OUT = RESULTS / "source_native_opening_operation_capacity_validation.json"
REPORT = RESULTS / "source_native_opening_operation_capacity_validation_report.md"
FROZEN = {
    SOURCE: "a202d93498e8a350a5d7e0ca46e831dcc37ea5c0182dc404d63cb797a98b1225",
    PATH_ATLAS: "22a5575582b6a45f6b469ea648dfc1a111c581c32c975c45a6edb89df21995ca",
    PATH_VALIDATION: "a7a254a5041495f09615c9681ae5d0bb83686698569314e30e16c66168f46e58",
    SPEC: "f3edf68c4e8830ec6195249ef9a065c12fa4634d2300c42f1a45bca1759d79c2",
    BUILDER: "4e351dcfee3a76bf5ef196f9ee1ccf4115a79d709945196aa959b8c31b838cde",
    TSV: "424b1c3d74edf27280d9510cbd18adf3a857e756b918512b3b3313c2b77031be",
    PRODUCTION: "0c1fcac00d1b5934d43acf5e265d79ef876ee08401cfe78695936fccbf903dc7",
    PRODUCTION_REPORT: "b9853519879fc4fa77c8b94a1f718f72c96d50bae068cf7c5c0fdd4783db15e3",
}
OPERATIONS = ("NONE", "DA", "DAQ", "DAQK", "DAQKJ")
PREFIXES = ("DAQKJ", "DAQK", "DAQ", "DA")
FIELDS = (
    "pair_id", "left_operation", "right_operation", "shared_exact_remainders",
    "two_folio_per_operation_remainders", "left_groups_on_shared_remainders",
    "right_groups_on_shared_remainders", "union_physical_folios",
    "currier_A_shared_remainders", "currier_B_shared_remainders",
    "capacity_eligible",
)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def physical_folio(page: str) -> str:
    match = re.fullmatch(r"(f\d+)[rv]\d*", page)
    if match is None:
        raise ValueError("page")
    return match.group(1)


def assign(surface: str) -> tuple[str, str]:
    matches = [prefix for prefix in PREFIXES if surface[:len(prefix)] == prefix]
    if not matches:
        return "NONE", surface
    prefix = max(matches, key=len)
    return prefix, surface[len(prefix):]


def reconstruct(source_rows):
    selected = [row for row in source_rows if row["strict_zero_alternative"] == "1" and row["grammar_scope"] == "CONFIRMED_PROSE"]
    if len(source_rows) != 26184 or len(selected) != 21899 or len({row["consensus_group_id"] for row in selected}) != 21899:
        raise ValueError("identity")
    by_base = defaultdict(lambda: defaultdict(list))
    operation_counts = Counter()
    empty_counts = Counter()
    for row in selected:
        surface = row["family_surface"]
        if not surface or len(surface) != int(row["symbol_count"]):
            raise ValueError("surface")
        operation, base = assign(surface)
        operation_counts[operation] += 1
        if not base:
            empty_counts[operation] += 1
        else:
            by_base[base][operation].append((row["consensus_group_id"], physical_folio(row["page"]), row["currier"]))
    output = []
    for left, right in itertools.combinations(OPERATIONS, 2):
        common = {base for base, states in by_base.items() if states.get(left) and states.get(right)}
        robust = {base for base in common if len({value[1] for value in by_base[base][left]}) >= 2 and len({value[1] for value in by_base[base][right]}) >= 2}
        left_rows = [value for base in common for value in by_base[base][left]]
        right_rows = [value for base in common for value in by_base[base][right]]
        folios = {value[1] for value in left_rows + right_rows}
        register = {currier: sum(any(value[2] == currier for value in by_base[base][left]) and any(value[2] == currier for value in by_base[base][right]) for base in common) for currier in ("A", "B")}
        passes = len(common) >= 20 and len(robust) >= 10 and len(left_rows) >= 50 and len(right_rows) >= 50 and len(folios) >= 20 and min(register.values()) >= 5
        output.append({
            "pair_id": f"{left}__{right}",
            "left_operation": left,
            "right_operation": right,
            "shared_exact_remainders": len(common),
            "two_folio_per_operation_remainders": len(robust),
            "left_groups_on_shared_remainders": len(left_rows),
            "right_groups_on_shared_remainders": len(right_rows),
            "union_physical_folios": len(folios),
            "currier_A_shared_remainders": register["A"],
            "currier_B_shared_remainders": register["B"],
            "capacity_eligible": int(passes),
        })
    passing = [row for row in output if row["capacity_eligible"]]
    passing.sort(key=lambda row: (-row["two_folio_per_operation_remainders"], -min(row["left_groups_on_shared_remainders"], row["right_groups_on_shared_remainders"]), -row["union_physical_folios"], row["pair_id"]))
    return selected, by_base, operation_counts, empty_counts, output, passing


def serialize(rows) -> str:
    handle = io.StringIO(newline="")
    writer = csv.DictWriter(handle, fieldnames=FIELDS, delimiter="\t", lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    return handle.getvalue()


def expected_report(source_rows, output, passing) -> str:
    best = passing[0] if passing else max(output, key=lambda row: (row["two_folio_per_operation_remainders"], min(row["left_groups_on_shared_remainders"], row["right_groups_on_shared_remainders"]), row["union_physical_folios"], row["pair_id"]))
    chosen = passing[0]["pair_id"] if passing else None
    status = "PASS_SCORE_BLIND_OPENING_OPERATION_CAPACITY" if chosen else "STOP_INSUFFICIENT_OPENING_OPERATION_CAPACITY"
    return f"""# Source-native opening-operation capacity

Status: **{status}**

The longest-prefix split assigns all **{len(source_rows):,}** strict prose groups to
`NONE/DA/DAQ/DAQK/DAQKJ` without opening any external-context outcome. Of ten
operation pairs, **{len(passing)}** pass the frozen capacity gates. The selected
pair is **{chosen or 'NONE'}**. The strongest capacity row `{best['pair_id']}`
has **{best['shared_exact_remainders']}** shared exact remainders,
**{best['two_folio_per_operation_remainders']}** replicated on at least two
folios per operation, and **{best['left_groups_on_shared_remainders']} /
{best['right_groups_on_shared_remainders']}** groups across
**{best['union_physical_folios']}** folios.

This is capacity for one separately frozen structural-context preflight only.
It supplies no detachment, wordhood, prefix meaning, sound, language, cipher,
plaintext, or translation.
"""


def main() -> None:
    if OUT.exists() or REPORT.exists():
        raise SystemExit("refusing overwrite")
    failures = []
    checks = 0

    def check(condition, name):
        nonlocal checks
        checks += 1
        if not condition:
            failures.append(name)

    for path, expected in FROZEN.items():
        check(sha(path) == expected, f"hash:{path.name}")
    with SOURCE.open(encoding="utf-8", newline="") as handle:
        source_rows = list(csv.DictReader(handle, delimiter="\t"))
    selected, by_base, operation_counts, empty_counts, rows, passing = reconstruct(source_rows)
    check(len(selected) == 21899 and len(rows) == 10, "capacity")
    check(serialize(rows) == TSV.read_text(), "tsv-bytes")
    stored = json.loads(PRODUCTION.read_text())
    check(stored["operation_group_counts"] == {value: operation_counts[value] for value in OPERATIONS}, "operation-counts")
    check(stored["empty_remainder_counts"] == {value: empty_counts[value] for value in OPERATIONS}, "empty-counts")
    check(stored["nonempty_exact_remainders"] == len(by_base), "base-count")
    check(stored["eligible_operation_pairs"] == [row["pair_id"] for row in passing], "passing")
    check(stored["selected_operation_pair"] == "NONE__DA" and len(passing) == 4, "selection")
    check(stored["status"] == "PASS_SCORE_BLIND_OPENING_OPERATION_CAPACITY" and stored["decision"] == "FREEZE_ONE_HELD_CONTEXT_PREFLIGHT", "decision")
    check(stored["tsv_sha256"] == sha(TSV), "tsv-binding")
    check(stored["remainder_identities_stored"] == 0 and stored["context_fields_accessed"] == 0 and stored["context_scores_computed"] == 0 and stored["english_glosses"] == 0, "isolation")
    check(PRODUCTION_REPORT.read_text() == expected_report(selected, rows, passing), "report-bytes")
    chosen = next(row for row in rows if row["pair_id"] == "NONE__DA")
    check(chosen["shared_exact_remainders"] == 122 and chosen["two_folio_per_operation_remainders"] == 53 and chosen["union_physical_folios"] == 94, "chosen-capacity")
    if failures:
        raise SystemExit("validation failed: " + failures[0])
    result = {
        "experiment": "SOURCE_NATIVE_OPENING_OPERATION_CAPACITY_VALIDATION",
        "status": "PASS_INDEPENDENT_10_PAIR_OPENING_CAPACITY_RECONSTRUCTION",
        "checks": checks,
        "failures": [],
        "eligible_pairs": 4,
        "selected_pair": "NONE__DA",
        "selected_shared_exact_remainders": 122,
        "selected_two_folio_per_operation_remainders": 53,
        "context_fields_accessed": 0,
        "context_scores_computed": 0,
        "inputs": {path.name: sha(path) for path in FROZEN},
        "english_glosses": 0,
        "claim_ceiling": "Independent score-blind capacity reconstruction only; no detachment, wordhood, prefix meaning, sound, language, cipher operation, plaintext, or translation follows.",
    }
    OUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    REPORT.write_text(f"""# Opening-operation capacity validation

Status: **{result['status']}**

A clean-room implementation reconstructs all 21,899 operation assignments,
2,625 nonempty exact remainders, all ten pair rows, four passing pairs, the
score-blind `NONE__DA` selection, exact TSV/report bytes, and bindings in
**{checks}** checks. It opens no external-context outcome.

This validates capacity only and supplies no detachment, wordhood, prefix
meaning, sound, language, cipher, plaintext, or translation.
""")
    print(json.dumps({"status": result["status"], "checks": checks}, sort_keys=True))


if __name__ == "__main__":
    main()
