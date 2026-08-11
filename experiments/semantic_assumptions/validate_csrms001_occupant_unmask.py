#!/usr/bin/env python3
"""Independent validation of the frozen CSRMS001 occupant reveal."""

from __future__ import annotations

import csv
import hashlib
import json
import re
from collections import Counter, defaultdict
from pathlib import Path


BASE = Path(__file__).resolve().parent
RESULTS = BASE / "results"
SOURCE = RESULTS / "consensus_structural_record_interlinear_v1.tsv"
SELECTION = RESULTS / "csrms001_masked_recurrent_slot_selection.json"
SELECTION_TSV = RESULTS / "csrms001_masked_recurrent_slot_selection.tsv"
SELECTION_VALIDATION = RESULTS / "csrms001_masked_recurrent_slot_selection_validation.json"
SPEC = BASE / "CSRMS001_OCCUPANT_UNMASK_SPEC.md"
PRODUCER = BASE / "run_csrms001_occupant_unmask.py"
TABLE = RESULTS / "csrms001_occupant_unmask.tsv"
RESULT = RESULTS / "csrms001_occupant_unmask.json"
REPORT = RESULTS / "csrms001_occupant_unmask_report.md"
OUT_JSON = RESULTS / "csrms001_occupant_unmask_validation.json"
OUT_REPORT = RESULTS / "csrms001_occupant_unmask_validation_report.md"

FROZEN = {
    SELECTION: "e5c02c3ae7aa4376075e1e7310dad457e06bffc8384aa9deb611ff3299f3f270",
    SELECTION_TSV: "75077c41057f1dc0169add9f9f10356e5c8a676d1c6c8222301cff8dc47e4c86",
    SELECTION_VALIDATION: "bc268a3006eff3a5cfaf3a62240c5e46d28605f3fabfe05137bfdd72769835c9",
    SOURCE: "7c375a9336588096e657917548eb3f2038828d9d6d42b75da2d24b57ccd3f387",
}
FORMAL = re.compile(
    r"^([SFCL]):([^{}]+)\{adj=([^;]+);fl=([^;]+);ec=([^;]+);"
    r"o=([0-9]+);c=([0-9]+);p=([^{};]+)\}$"
)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical(value: object) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":"),
                       ensure_ascii=False) + "\n").encode()


def summarize(rows: list[dict[str, str]], field: str) -> list[dict[str, object]]:
    counts = Counter(row[field] for row in rows)
    folios: dict[str, set[int]] = defaultdict(set)
    for row in rows:
        folios[row[field]].add(int(row["physical_folio"]))
    return [{"value": value, "occurrences": count,
             "physical_folios": len(folios[value])}
            for value, count in sorted(counts.items(),
                                       key=lambda item: (-item[1], item[0].encode()))]


def main() -> None:
    if OUT_JSON.exists() or OUT_REPORT.exists():
        raise SystemExit("refusing to overwrite CSRMS001 unmask validation")
    checks = []
    for path, expected in FROZEN.items():
        assert sha(path) == expected
    checks.append("frozen_inputs")

    with SELECTION_TSV.open(encoding="utf-8", newline="") as handle:
        selected = list(csv.DictReader(handle, delimiter="\t"))
    with SOURCE.open(encoding="utf-8", newline="") as handle:
        source = {row["record_order"]: row for row in csv.DictReader(handle, delimiter="\t")}
    with TABLE.open(encoding="utf-8", newline="") as handle:
        actual = list(csv.DictReader(handle, delimiter="\t"))
    assert len(selected) == len(actual) == 10
    checks.append("ten_rows_only")

    reconstructed = []
    for fixed in selected:
        row = source[fixed["record_order"]]
        index = int(fixed["occupant_ordinal"]) - 1
        family = row["family_expression"].split(" ")[index]
        members = [row[f"{reading}_sta_expression"].split(" | ")[index]
                   for reading in ("zl", "it", "rf")]
        assert members[0] == members[1] == members[2]
        evas = [row[f"{reading}_basic_eva_lossy_expression"].split(" ")[index]
                for reading in ("zl", "it", "rf")]
        formal = row["formal_expression"].split(" | ")[index]
        match = FORMAL.fullmatch(formal)
        assert match and match.group(2) == family
        pos, _, adj, fl, ec, opening, closing, _ = match.groups()
        shell = f"{pos}|adj={adj}|fl={fl}|ec={ec}|o={opening}|c={closing}"
        reconstructed.append({
            "occurrence_order": fixed["occurrence_order"],
            "record_order": row["record_order"], "segment_id": row["segment_id"],
            "page": row["page"], "physical_folio": fixed["physical_folio"],
            "section": row["section"], "currier": row["currier"], "hand": row["hand"],
            "record_length": fixed["record_length"], "occupant_ordinal": fixed["occupant_ordinal"],
            "family_surface": family, "exact_sta_member_group": members[0],
            "zl_basic_eva_lossy": evas[0], "it_basic_eva_lossy": evas[1],
            "rf_basic_eva_lossy": evas[2], "current_formal_expression": formal,
            "current_formal_shell": shell,
        })
    assert actual == reconstructed
    checks.append("exact_frozen_row_reveal")

    families = summarize(actual, "family_surface")
    members = summarize(actual, "exact_sta_member_group")
    shells = summarize(actual, "current_formal_shell")
    assert len(families) == 9 and len(members) == 10 and len(shells) == 9
    assert families[0] == {"value": "QKAB", "occurrences": 2, "physical_folios": 2}
    assert members[0]["occurrences"] == 1
    assert shells[0]["occurrences"] == 2
    checks.append("support_counts")

    flags = {
        "FAMILY_RECURRENCE": families[0]["occurrences"] >= 5 and families[0]["physical_folios"] >= 5,
        "MEMBER_RECURRENCE": members[0]["occurrences"] >= 4 and members[0]["physical_folios"] >= 4,
        "CURRENT_SHELL_RECURRENCE": shells[0]["occurrences"] >= 7 and shells[0]["physical_folios"] >= 6,
    }
    assert flags == {"FAMILY_RECURRENCE": False, "MEMBER_RECURRENCE": False,
                     "CURRENT_SHELL_RECURRENCE": False}
    checks.append("registered_flags_all_fail")

    result = json.loads(RESULT.read_text(encoding="utf-8"))
    assert RESULT.read_bytes() == canonical(result)
    assert result["status"] == "STOP_DIVERSE_OCCUPANTS_NO_RECURRENT_FILLER_CLASS"
    assert result["decision"] == "CLOSE_RECURRENT_SLOT_FILLER_ROUTE"
    assert result["family_support"] == families
    assert result["member_support"] == members
    assert result["current_shell_support"] == shells
    assert result["flags"] == flags
    assert result["background_comparison_performed"] is False
    assert result["alternative_context_search_performed"] is False
    assert result["english_glosses"] == 0
    assert result["outputs"] == {TABLE.name: sha(TABLE)}
    checks.append("canonical_result_and_stop")

    report = REPORT.read_text(encoding="utf-8")
    assert "**9** family surfaces" in report and "**10** exact member groups" in report
    assert "not words or translations" in report
    checks.append("report_ceiling")

    validation = {
        "experiment": "CSRMS001_FROZEN_SLOT_OCCUPANT_UNMASK_VALIDATION",
        "status": "PASS_INDEPENDENT_TEN_OCCUPANT_STOP_RECONSTRUCTION",
        "validated_result_sha256": sha(RESULT),
        "validated_table_sha256": sha(TABLE),
        "check_count": len(checks), "checks": checks,
        "reconstructed": {"occupants": 10, "families": 9, "exact_members": 10,
                            "current_shells": 9, "recurrence_flags_passing": 0},
        "claim_ceiling": result["claim_ceiling"],
    }
    OUT_JSON.write_bytes(canonical(validation))
    OUT_REPORT.write_text(
        "# CSRMS001 occupant-unmask validation\n\n"
        "Status: **PASS_INDEPENDENT_TEN_OCCUPANT_STOP_RECONSTRUCTION**\n\n"
        f"All **{len(checks)}** checks pass. Independent code reopens only the ten frozen rows "
        "and reconstructs nine families, ten exact members, nine formal shells, all three "
        "failed recurrence flags, and the canonical stop result.\n\n"
        "The selected position is structurally recurrent but its occupants are diverse. This "
        "supplies no lexical slot, POS, morpheme, word, sound, language, cipher, plaintext, "
        "meaning, or translation.\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
