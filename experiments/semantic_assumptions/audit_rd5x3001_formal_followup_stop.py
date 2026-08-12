#!/usr/bin/env python3
"""Record the unscored RD5X3-001 formal follow-up stop.

This is deliberately a metadata-only capacity reconstruction.  It never reads
or serializes any formal-family, EVA, or group-surface field.
"""

from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter
from pathlib import Path

BASE = Path(__file__).resolve().parent
SOURCE = BASE / "results/source_sta_group_alignment.tsv"
TOPOLOGY = BASE / "results/rd5x3001_rosettes_doorway_topology_result.json"
OUT = BASE / "results/rd5x3001_formal_followup_stop.json"
REPORT = BASE / "results/rd5x3001_formal_followup_stop_report.md"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    if OUT.exists() or REPORT.exists():
        raise SystemExit("refusing overwrite")
    with SOURCE.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle, delimiter="\t")
        permitted = {"edition", "locus", "source_group_index", "source_group_count"}
        if not permitted.issubset(reader.fieldnames or []):
            raise SystemExit("metadata schema mismatch")
        rows = []
        for row in reader:
            locus = row["locus"]
            if locus.startswith("fRos.") and 146 <= int(locus.split(".", 1)[1]) <= 160:
                rows.append({key: row[key] for key in permitted})

    edition_rows = Counter(row["edition"] for row in rows)
    edition_loci = {
        edition: len({row["locus"] for row in rows if row["edition"] == edition})
        for edition in ("ZL3b", "IT2a", "RF1b")
    }
    group_count_by_edition_locus = Counter((row["edition"], row["locus"]) for row in rows)
    doubled = sorted(
        locus for (edition, locus), count in group_count_by_edition_locus.items()
        if edition == "ZL3b" and count == 2
    )
    counts = {
        "selected_loci": 15,
        "source_group_rows": len(rows),
        "source_group_rows_by_edition": dict(sorted(edition_rows.items())),
        "distinct_loci_by_edition": edition_loci,
        "loci_with_two_groups_per_present_reading": doubled,
        "physical_folios": 1,
        "present_readings": 2,
        "missing_readings": ["IT2a"],
        "formal_associations_scored": 0,
        "p_values_computed": 0,
    }
    if counts != {
        "selected_loci": 15,
        "source_group_rows": 32,
        "source_group_rows_by_edition": {"RF1b": 16, "ZL3b": 16},
        "distinct_loci_by_edition": {"ZL3b": 15, "IT2a": 0, "RF1b": 15},
        "loci_with_two_groups_per_present_reading": ["fRos.151"],
        "physical_folios": 1,
        "present_readings": 2,
        "missing_readings": ["IT2a"],
        "formal_associations_scored": 0,
        "p_values_computed": 0,
    }:
        raise SystemExit("registered capacity mismatch")

    result = {
        "experiment": "RD5X3001_FORMAL_FOLLOWUP_STOP",
        "status": "STOP_UNSCORED_PRETARGET_EXPOSURE_AND_ONE_FOLIO_TWO_READING_SUPPORT",
        "decision": "DO_NOT_SCORE_RD5X3_FILLER_OR_POSITION_ASSOCIATIONS",
        "inputs": {
            "source_sta_group_alignment_sha256": sha(SOURCE),
            "topology_result_sha256": sha(TOPOLOGY),
        },
        "counts": counts,
        "access": {
            "metadata_fields_used": ["edition", "locus", "source_group_count", "source_group_index"],
            "formal_family_sequence_previously_displayed_during_capacity_diagnostic": True,
            "display_occurred_after_visual_topology_result_but_before_formal_preregistration": True,
            "formal_identity_field_used_for_this_stop_reconstruction": False,
            "filler_or_position_statistic_computed": False,
        },
        "reason": (
            "A capacity lookup displayed the target formal-family sequences before any formal-content freeze. "
            "The panel also consists of one physical folio and only two alternate readings, with IT absent. "
            "A retrospective p-value would therefore be post-exposure and would not provide independent support."
        ),
        "claim_ceiling": (
            "The five-by-three visual topology remains valid. No formal filler or row-position association is "
            "scored, and no field, word, sound, language, cipher, plaintext, meaning, or translation follows."
        ),
    }
    OUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    REPORT.write_text(
        "# RD5X3-001 formal follow-up stop\n\n"
        "Status: **STOP_UNSCORED_PRETARGET_EXPOSURE_AND_ONE_FOLIO_TWO_READING_SUPPORT**\n\n"
        "The fixed fifteen loci have 16 source groups in ZL and 16 in RF; IT has no Rosettes rows. "
        "Only fRos.151 has two groups in each present reading. During a capacity diagnostic, the target "
        "formal-family sequences were displayed before a formal-content preregistration. No association, "
        "test statistic, null distribution, or p-value was computed.\n\n"
        "A retrospective score would not be clean evidence: the target was exposed, the panel is one physical "
        "folio, and ZL/RF are alternate readings rather than replications. The visual 5×3 topology is retained, "
        "but its contents are not scored.\n\n"
        f"Claim ceiling: {result['claim_ceiling']}\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
