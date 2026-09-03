#!/usr/bin/env python3
"""Independent source, count, safety, and byte-replay validator for GDT771."""

from __future__ import annotations

import csv
import hashlib
import json
import subprocess
import sys
import tempfile
from collections import defaultdict
from pathlib import Path
from typing import Mapping, Sequence

sys.dont_write_bytecode = True


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
EXP = ROOT / "experiments/yolo/gdt771_complete_cache_discriminator_sufficiency"
SRC = EXP / "src"
ARTIFACTS = EXP / "artifacts"
RUNNER = SRC / "run.py"

TARGET_ATLAS = ROOT / "experiments/yolo/gdt769_liquid_process_role_identity_dispatch/artifacts/TARGET_526_EXACT_CONTEXT_ATLAS.tsv"
FRAME_ATLAS = ROOT / "experiments/yolo/gdt769_liquid_process_role_identity_dispatch/artifacts/FRAME_LOCUS_EVIDENCE.tsv"
INTEGRATED_READER = ROOT / "experiments/yolo/gdt734_v99r7_recurrent_unknown_family_dispatch/artifacts/V99R7_4128_INTEGRATED_LINE_READER.tsv"
QUANTITY_ATLAS = ROOT / "experiments/yolo/gdt760_quantity_bilateral_content_attachment/artifacts/QUANTITY_281_EXPRESSION_ATLAS.tsv"
GDT770_COHORT = ROOT / "experiments/yolo/gdt770_target_masked_valency_orphan_tournament/src/COHORT_15_LINE_SPECS.tsv"
GDT770_EXCLUSIONS = ROOT / "experiments/yolo/gdt770_target_masked_valency_orphan_tournament/src/COHORT_EXCLUSION_LEDGER.tsv"

TARGETS = {"ol", "ckhy", "ols", "otar"}
OUTPUTS = (
    "SELECTOR_461_GUARDED_LOCUS_INVENTORY.tsv",
    "COMPLETE_203_TARGET_CONTEXT_ATLAS.tsv",
    "OL_LEFT_BRANCH_ATLAS.tsv",
    "DISCRIMINATOR_OCCURRENCE_ATLAS.tsv",
    "DISCRIMINATOR_SUMMARY.tsv",
    "OTAR_IDENTITY_COVERAGE.tsv",
    "NEXT_SCORE_DECK.tsv",
    "GDT771_4_WORKING_DICTIONARY.tsv",
    "RESULT.json",
)
EXPECTED_DECISIONS = {
    "D01A_OL_LEFT_LICENSED": ("PASS_AVAILABLE", 14, 9),
    "D01X_OL_LEFT_RIGHT_EXACT": ("PASS_AVAILABLE", 11, 7),
    "D01B_OL_FULL_BRANCH": ("PASS_AVAILABLE", 7, 6),
    "D02_CKHY_FINAL_PATIENT": ("FAIL_NOT_ENOUGH_COMPLETE_CONTEXTS", 1, 1),
    "D03_OLS_RIGHT_VALUE": ("FAIL_NOT_ENOUGH_COMPLETE_CONTEXTS", 1, 1),
    "D04S_OTAR_SEQUENCE": ("PASS_AVAILABLE", 5, 4),
    "D04N_OTAR_NOMINAL": ("PASS_AVAILABLE", 3, 3),
    "D04E_OTAR_ENDPOINT": ("FAIL_NOT_ENOUGH_COMPLETE_CONTEXTS", 1, 1),
}


def read_tsv(path: Path) -> tuple[tuple[str, ...], list[dict[str, str]]]:
    raw = path.read_bytes()
    if b"\x00" in raw or b"\r" in raw:
        raise AssertionError(f"non-canonical TSV bytes: {path}")
    reader = csv.DictReader(raw.decode("utf-8").splitlines(), delimiter="\t")
    header = tuple(reader.fieldnames or ())
    rows = list(reader)
    if not header or len(header) != len(set(header)):
        raise AssertionError(f"invalid TSV header: {path}")
    if any(None in row for row in rows) or any(value is None for row in rows for value in row.values()):
        raise AssertionError(f"TSV width mismatch: {path}")
    return header, rows


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def guarded_query(
    path: Path, loci: Sequence[str], columns: Sequence[str]
) -> tuple[list[dict[str, str]], dict[str, int]]:
    command = [
        str(ROOT / "vmanus-exp"), "query-tsv", str(path.relative_to(ROOT)),
        "--selector", "locus",
    ]
    for locus in sorted(set(loci)):
        if locus.startswith("f84"):
            raise AssertionError("forbidden selector in allow list")
        command.extend(("--allow", locus))
    command.extend(("--columns", ",".join(columns)))
    completed = subprocess.run(
        command, cwd=ROOT, check=True, text=True,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE,
    )
    stats_lines = [line for line in completed.stderr.splitlines() if line.startswith("GUARD_STATS ")]
    if len(stats_lines) != 1:
        raise AssertionError("guard statistics missing or duplicated")
    stats = json.loads(stats_lines[0].removeprefix("GUARD_STATS "))
    rows = list(csv.DictReader(completed.stdout.splitlines(), delimiter="\t"))
    return rows, stats


def all_donors(row: Mapping[str, str]) -> list[dict[str, object]]:
    context = json.loads(row["context_views"])["D1"]
    return list(context["eligible_donors"]) + list(context["blocked_donors"])


def direct_donor(row: Mapping[str, str], direction: str) -> dict[str, object] | None:
    matches = [
        donor for donor in all_donors(row)
        if donor["direction"] == direction and int(donor["distance"]) == 1
    ]
    if len(matches) > 1:
        raise AssertionError(f"ambiguous direct donor at {row['target_occurrence_id']}")
    return matches[0] if matches else None


def exact(donor: Mapping[str, object] | None) -> bool:
    return bool(donor and int(donor.get("current_clean", 0)) == 1 and donor.get("gate_status") != "NONEXACT")


def main() -> int:
    checks: list[str] = []

    def check(condition: bool, label: str) -> None:
        if not condition:
            raise AssertionError(label)
        checks.append(label)

    _target_header, all_targets = read_tsv(TARGET_ATLAS)
    targets = [row for row in all_targets if row["surface"] in TARGETS]
    loci = sorted({row["locus"] for row in targets})
    check(len(targets) == 523 and len(loci) == 461, "523 exact targets on 461 explicit loci")
    check(all(row["reader_exact"] == "1" for row in targets), "all target rows are reader-exact")
    check(not any(row["locus"].startswith("f84") for row in targets), "no sealed target locus")

    integrated, integrated_stats = guarded_query(
        INTEGRATED_READER, loci,
        ("page", "locus", "token_count", "complete_line_v99r7", "unknown_cells_v99r7", "zl3b_line"),
    )
    quantity, quantity_stats = guarded_query(
        QUANTITY_ATLAS, loci,
        ("expression_id", "page", "physical_folio", "locus", "mode", "source_expression_eva",
         "start_ordinal", "end_ordinal", "right_surface", "right_ordinal", "right_reader_exact",
         "right_source_composed_quarantined", "value_label", "written_line_eva"),
    )
    check(integrated_stats == {"selected": 461, "skipped_forbidden": 0, "skipped_not_allowed": 3667}, "integrated guard stats exact")
    check(quantity_stats == {"selected": 46, "skipped_forbidden": 0, "skipped_not_allowed": 235}, "quantity guard stats exact")
    check(len(integrated) == 461 and {row["locus"] for row in integrated} == set(loci), "guarded selector is one-to-one")

    base_complete = {
        row["locus"] for row in integrated
        if row["complete_line_v99r7"] == "1" and row["unknown_cells_v99r7"] == "0"
    }
    _cohort_header, cohort = read_tsv(GDT770_COHORT)
    g770_loci = {row["locus"] for row in cohort}
    _old_ex_header, old_exclusions = read_tsv(GDT770_EXCLUSIONS)
    _new_ex_header, new_exclusions = read_tsv(SRC / "ADDITIONAL_EXCLUSION_SPECS.tsv")
    excluded = {row["locus"] for row in old_exclusions + new_exclusions}
    union = base_complete | g770_loci
    strict = union - excluded
    check((len(base_complete), len(g770_loci), len(union)) == (173, 15, 176), "complete-cache locus counts exact")
    check(sum(row["locus"] in union for row in targets) == 203, "203 admitted target occurrences")
    check(sum(row["locus"] in strict for row in targets) == 195, "195 strict target occurrences")

    _bare_header, bare_rows = read_tsv(SRC / "OL_BARE_VALUE_FORMS.tsv")
    bare = {row["surface"] for row in bare_rows}
    _left_header, left_transfer_rows = read_tsv(SRC / "OL_LEFT_ROLE_TRANSFERS.tsv")
    left_transfers = {
        (row["locus"], row["target_ordinal"], row["left_surface"], row["left_ordinal"])
        for row in left_transfer_rows
    }
    _cross_header, cross_rows = read_tsv(SRC / "OL_RIGHT_ROLE_CROSSWALK.tsv")
    crosswalk: dict[str, set[str]] = defaultdict(set)
    for row in cross_rows:
        if row["admit_for_left_amount_branch"] == "1":
            crosswalk[row["source_role"]].add(row["gdt770_allowed_role"])
    _transfer_header, transfer_rows = read_tsv(SRC / "OL_RIGHT_ROLE_TRANSFERS.tsv")
    transfers = {
        (row["locus"], row["target_ordinal"], row["right_surface"], row["right_ordinal"]): {
            value for value in row["gdt770_allowed_roles"].split("|") if value != "NONE"
        }
        for row in transfer_rows
    }
    quantity_keys = {
        (row["locus"], row["right_ordinal"])
        for row in quantity
        if row["right_surface"] == "ol" and row["right_reader_exact"] == "1"
        and row["right_source_composed_quarantined"] == "0"
        and int(row["end_ordinal"]) + 1 == int(row["right_ordinal"])
    }
    left_ids: set[str] = set()
    right_exact_ids: set[str] = set()
    full_ids: set[str] = set()
    for row in targets:
        if row["surface"] != "ol" or row["locus"] not in strict:
            continue
        ordinal = int(row["ordinal"])
        tokens = row["written_line_eva"].split()
        left_surface = tokens[ordinal - 2] if ordinal > 1 else "LINE_EDGE"
        right_surface = tokens[ordinal] if ordinal < len(tokens) else "LINE_EDGE"
        left = direct_donor(row, "LEFT")
        right = direct_donor(row, "RIGHT")
        left_transfer = (row["locus"], row["ordinal"], left_surface, str(ordinal - 1)) in left_transfers
        licensed = (
            (row["locus"], row["ordinal"]) in quantity_keys
            or (left_surface in bare and exact(left))
            or left_transfer
        )
        if not licensed:
            continue
        target_id = row["target_occurrence_id"]
        left_ids.add(target_id)
        if exact(right):
            right_exact_ids.add(target_id)
        allowed: set[str] = set()
        if right and right.get("gate_status") == "ELIGIBLE" and exact(right):
            for role in right.get("roles", []):
                allowed.update(crosswalk.get(str(role), set()))
        allowed.update(transfers.get((row["locus"], row["ordinal"], right_surface, str(ordinal + 1)), set()))
        if exact(right) and allowed:
            full_ids.add(target_id)
    check((len(left_ids), len({next(r["page"] for r in targets if r["target_occurrence_id"] == i) for i in left_ids})) == (14, 9), "independent ol left count 14/9")
    check((len(right_exact_ids), len({next(r["page"] for r in targets if r["target_occurrence_id"] == i) for i in right_exact_ids})) == (11, 7), "independent ol right-exact count 11/7")
    check((len(full_ids), len({next(r["page"] for r in targets if r["target_occurrence_id"] == i) for i in full_ids})) == (7, 6), "independent ol full-branch count 7/6")
    expected_full_loci = {"f112r.36", "f30v.2", "f75r.26", "f81r.15", "f81r.22", "f82r.33", "f85r1.21"}
    observed_full_loci = {next(r["locus"] for r in targets if r["target_occurrence_id"] == i) for i in full_ids}
    check(observed_full_loci == expected_full_loci, "ol full-branch loci exact")

    _summary_header, summary = read_tsv(ARTIFACTS / "DISCRIMINATOR_SUMMARY.tsv")
    observed_decisions = {
        row["discriminator_id"]: (
            row["decision"], int(row["qualified_occurrences"]), int(row["qualified_distinct_pages"])
        )
        for row in summary
    }
    check(observed_decisions == EXPECTED_DECISIONS, "all eight discriminator decisions exact")
    _occ_header, occurrences = read_tsv(ARTIFACTS / "DISCRIMINATOR_OCCURRENCE_ATLAS.tsv")
    endpoint_rows = [row for row in occurrences if row["discriminator_id"] == "D04E_OTAR_ENDPOINT" and row["strict_qualified"] == "1"]
    check([(row["locus"], row["ordinal"]) for row in endpoint_rows] == [("f75r.43", "6")], "otar endpoint is exactly f75r.43@6")

    for name in OUTPUTS:
        check((ARTIFACTS / name).is_file(), f"artifact exists: {name}")
    with tempfile.TemporaryDirectory(prefix="gdt771-replay-") as temporary:
        replay = Path(temporary)
        subprocess.run(
            [sys.executable, str(RUNNER), "--output-dir", str(replay)],
            cwd=ROOT, check=True, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        )
        mismatches = [name for name in OUTPUTS if (ARTIFACTS / name).read_bytes() != (replay / name).read_bytes()]
    check(not mismatches, "nine-artifact byte replay exact")

    result = json.loads((ARTIFACTS / "RESULT.json").read_text(encoding="utf-8"))
    check(result["confirmed_lexemes"] == result["confirmed_plaintext_clauses"] == result["component_export_credit"] == 0, "semantic claim ceiling remains zero")
    check(result["sealed_data"] == {"f84": "FORBIDDEN", "f84r": "FORBIDDEN"}, "sealed-page policy explicit")
    check(all(sha256(ROOT / relative) == digest for relative, digest in result["source_sha256"].items()), "all source hashes replay")

    for name in OUTPUTS:
        if not name.endswith(".tsv"):
            continue
        _header, rows = read_tsv(ARTIFACTS / name)
        for row in rows:
            for key in ("locus", "page", "physical_folio"):
                if key in row:
                    check(not row[key].startswith("f84"), f"no sealed row in {name}:{key}:{row.get(key, '')}")
            for key in ("semantic_identity_credit", "component_export_credit", "confirmed_lexeme", "confirmed_plaintext"):
                if key in row:
                    check(row[key] == "0", f"zero {key} in {name}")

    validation = {
        "experiment_id": "GDT771",
        "status": "PASS",
        "checks_passed": len(checks),
        "independent_core": {
            "explicit_selector_loci": 461,
            "strict_target_occurrences": 195,
            "ol_left_occurrences_pages": [14, 9],
            "ol_right_exact_occurrences_pages": [11, 7],
            "ol_full_branch_occurrences_pages": [7, 6],
            "otar_endpoint_locus": "f75r.43@6",
        },
        "byte_replay": {"output_count": len(OUTPUTS), "mismatches": []},
        "forbidden_rows_materialized": 0,
        "confirmed_lexemes": 0,
        "confirmed_plaintext_clauses": 0,
        "component_export_credit": 0,
    }
    (ARTIFACTS / "VALIDATION.json").write_text(
        json.dumps(validation, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(validation, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
