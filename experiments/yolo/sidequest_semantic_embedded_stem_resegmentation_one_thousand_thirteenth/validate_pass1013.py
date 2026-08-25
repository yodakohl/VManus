#!/usr/bin/env python3
"""Validate Pass 1013 against its fixed Pass-1011/1012 sources."""

from __future__ import annotations

import csv
import json
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
SOURCE = (
    ROOT
    / "experiments/yolo/sidequest_semantic_manual_optical_passage_audit_one_thousand_eleventh"
    / "PASS1011_627_OPTICALLY_REPAIRED_STATEMENTS.tsv"
)
CONTRACT = HERE / "PASS1013_46_SIGN_SEMANTIC_CONTRACT.tsv"
RESEGMENTATIONS = HERE / "PASS1013_10_RESEGMENTATIONS.tsv"
COMPOSITIONS = HERE / "PASS1013_102_COMPOSITION_CONTRACTS.tsv"
PRESSURE = HERE / "PASS1013_627_SEMANTIC_PRESSURE_MAP.tsv"
SUMMARY = HERE / "PASS1013_BUILD_SUMMARY.json"

RESEGMENT = {
    "CTH": ("CH", "T"),
    "CKH": ("CH", "K"),
    "CHEO": ("CH", "E", "O"),
    "CHK": ("CH", "K"),
    "CPH": ("CH", "P"),
    "SHED": ("SH", "E"),
    "SOLK": ("OL", "K"),
    "LSH": ("L", "SH"),
    "CFH": ("CH", "LOCAL_CHAR_F"),
    "LD": ("L", "D_ADDR"),
}
EXPECTED_MENTIONS = {
    "CTH": 88,
    "CKH": 104,
    "CHEO": 107,
    "CHK": 46,
    "CPH": 20,
    "SHED": 110,
    "SOLK": 30,
    "LSH": 22,
    "CFH": 5,
    "LD": 1,
}


def read_tsv(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle, delimiter="\t")
        return list(reader.fieldnames or []), list(reader)


def expand_sequence(value: str) -> str:
    events = []
    for event in value.split(" | "):
        expanded = [part for token in event.split("+") for part in RESEGMENT.get(token, (token,))]
        events.append("+".join(expanded))
    return " | ".join(events)


def main() -> None:
    checks: list[dict[str, object]] = []

    def check(name: str, passed: bool, detail: str) -> None:
        checks.append({"check": name, "passed": bool(passed), "detail": detail})

    _, source = read_tsv(SOURCE)
    _, contract = read_tsv(CONTRACT)
    _, reseg = read_tsv(RESEGMENTATIONS)
    _, compositions = read_tsv(COMPOSITIONS)
    _, pressure = read_tsv(PRESSURE)
    summary = json.loads(SUMMARY.read_text(encoding="utf-8"))

    check("statement_count", len(pressure) == len(source) == 627, f"source={len(source)} output={len(pressure)}")
    check("sign_count", len(contract) == 46, str(len(contract)))
    check("resegmentation_count", len(reseg) == 10, str(len(reseg)))
    check("composition_count", len(compositions) == 102, str(len(compositions)))
    check(
        "composition_partition",
        Counter(row["unit_type"] for row in compositions)
        == Counter({"FORMULA_CARD": 30, "CONTEXTUAL_COMPOSITION_NOT_NEW_WORD": 72}),
        str(Counter(row["unit_type"] for row in compositions)),
    )

    source_by_id = {row["statement_id"]: row for row in source}
    output_by_id = {row["statement_id"]: row for row in pressure}
    check("statement_ids", set(source_by_id) == set(output_by_id), f"{len(source_by_id)}/{len(output_by_id)}")

    preserved = True
    resegmented = True
    for statement_id, old in source_by_id.items():
        new = output_by_id[statement_id]
        for field in ("surface_sequence", "event_ids", "physical_page", "owner_id", "end_mode"):
            preserved &= old[field] == new[field]
        resegmented &= expand_sequence(old["component_sequence"]) == new["component_sequence"]
    check("source_bindings_preserved", preserved, "surface/event/page/owner/end unchanged")
    check("all_component_sequences_resegmented_exactly", resegmented, "627/627")

    signs = {row["sign"] for row in contract}
    output_tokens = {
        token
        for row in pressure
        for event in row["component_sequence"].split(" | ")
        for token in event.split("+")
    }
    check("all_output_tokens_licensed", output_tokens <= signs, str(sorted(output_tokens - signs)))
    check("removed_tokens_absent", not (set(RESEGMENT) & output_tokens), str(sorted(set(RESEGMENT) & output_tokens)))
    check(
        "no_specialist_class",
        all(row["pass1012_class"] != "SPECIALIST_MEANING_CANDIDATE" for row in contract),
        str(Counter(row["pass1012_class"] for row in contract)),
    )
    check(
        "air_promoted_as_lauf",
        any(
            row["sign"] == "AIR"
            and row["pass1012_class"] == "PORTABLE_CORE_MEANING"
            and row["single_core_value_de"] == "LAUF"
            for row in contract
        ),
        "AIR portable LAUF",
    )
    check(
        "expected_resegmentation_mentions",
        summary["resegmented_mentions"] == EXPECTED_MENTIONS,
        str(summary["resegmented_mentions"]),
    )

    event_counts = Counter()
    statement_counts = Counter(row["pass1013_statement_status"] for row in pressure)
    for row in pressure:
        event_counts["PORTABLE_CORE_COMPOSITION"] += int(row["portable_event_count"])
        event_counts["FORMAL_CONTROL_ONLY"] += int(row["formal_only_event_count"])
        event_counts["LOCAL_OWNER_DEPENDENT"] += int(row["local_event_count"])
    check("event_partition_3888", sum(event_counts.values()) == 3888, str(event_counts))
    check("statement_partition_627", sum(statement_counts.values()) == 627, str(statement_counts))
    check("summary_event_counts", dict(sorted(event_counts.items())) == summary["event_statuses"], str(event_counts))
    check("summary_statement_counts", dict(sorted(statement_counts.items())) == summary["statement_statuses"], str(statement_counts))

    forbidden_text = "\n".join(path.read_text(encoding="utf-8") for path in (CONTRACT, RESEGMENTATIONS, COMPOSITIONS, PRESSURE))
    check("sealed_page_tokens_absent", "f84" not in forbidden_text.lower(), "no f84 token")
    check("no_empty_literals", all(row["contract_literal_de"].strip() for row in pressure), "627/627")
    check(
        "manual_repairs_preserved",
        sum(row["working_translation_status"] == "MANUAL_IMAGE_REPAIR" for row in pressure) == 35,
        str(sum(row["working_translation_status"] == "MANUAL_IMAGE_REPAIR" for row in pressure)),
    )

    failures = [row for row in checks if not row["passed"]]
    result = {
        "status": "PASS" if not failures else "FAIL",
        "checks": len(checks),
        "failures": failures,
        "details": checks,
    }
    (HERE / "PASS1013_VALIDATION.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    if failures:
        raise SystemExit(json.dumps(failures, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
