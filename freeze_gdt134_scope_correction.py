#!/usr/bin/env python3
"""Bind the post-enumeration GDT134 scope correction without inspecting f84."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
PREDICTION = ROOT / "gdt134_prediction.json"
SOURCE = ROOT / "gdt016_group_state_inventory.tsv"
FRAMES = ROOT / "gdt046_line_frames.tsv"
OUT = ROOT / "gdt134_scope_correction.json"


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def content_sha(value):
    payload = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(payload.encode()).hexdigest()


SUPERSEDED = {
    "status": "INSUFFICIENT_EXACT_NULL_CAPACITY",
    "result_sha256": "3022e3ee0cec954a5ef717894b1a7f0dac017477243eea78d38d384051d66416",
    "result_content_sha256": "0ed8e36b40e141ef40d710e00e8b2ba6690edea09bd2b1145a41257403107f12",
    "inventory_sha256": "953c760a51c9de934ca9e47ed40ad58ee5877a79326a0973ec4e6ec741fd87e6",
    "scores_sha256": "48da099217bae41d92114881fba6eb27feff71c6f8f2cf286a2ed9009c07a8dc",
    "null_sha256": "12d6707daad0dc7ad0b83863d8d92f8dd13d89605a6459971a3807a2887715b1",
    "report_sha256": "8ffdcf99c9f6ed6f672bb870c59b5176101abaae1b0110405a100cadbececd8d",
    "pairs": 261,
    "physical_folios": 68,
    "subsets": {"all": 261, "continuation_to_continuation": 230, "start_to_next": 31},
    "null_capacity": {"exact": 16, "coarse": 238},
    "gains": {
        "raw_all": -0.9206778352214577,
        "raw_continuation": -2.2134851240598077,
        "raw_start": 1.2928072888384625,
        "host_all": -9.69314449245698,
        "host_continuation": -5.540040996341254,
        "host_start": -4.153103496115818,
        "compiler_all": 2.2881840071799595,
        "compiler_continuation": 1.5366163823306016,
        "compiler_start": 0.7515676248491634,
    },
}


prediction = json.loads(PREDICTION.read_text())
assert prediction["status"] == "FROZEN_BEFORE_GENERAL_ADJACENT_PAIR_ENUMERATION"

correction = {
    "schema": "GDT134_SCOPE_CORRECTION_V1",
    "status": "POST_ENUMERATION_SCOPE_AND_NULL_CORRECTION_BEFORE_FINAL_RESCORING",
    "chronology": (
        "The public prediction preceded pair enumeration. The first local run then produced the "
        "superseded 261-pair result. A read-only capacity audit subsequently found that both "
        "nominally f84r-free inputs contain f84v rows, that nine resulting pairs should be excluded "
        "under the stronger all-f84 seal, and that the null must use exact rather than bucketed "
        "source-group count. This correction is post-enumeration and is not a new pristine freeze."
    ),
    "original_prediction_sha256": sha(PREDICTION),
    "superseded_prepublication_run": SUPERSEDED,
    "source_audit": {
        "gdt016_f84v_rows_reported_by_read_only_audit": 228,
        "gdt046_f84v_rows_reported_by_read_only_audit": 21,
        "f84r_rows_in_either_input": 0,
        "displayed_by_final_scorer": False,
        "retained_by_final_scorer": False,
        "parsed_by_hpr2_final_scorer": False,
        "joined_or_scored_by_final_scorer": False,
        "note": "Final code stream-rejects every f84* row before formal-field retention or HPR2 parsing.",
    },
    "corrected_scope": {
        "primary": "ALL_NON_Q20_NON_F84_CONTINUATION_TO_CONTINUATION_ADJACENT_COMPLETE_LINE_PAIRS",
        "descriptive_all_panel": "PRIMARY_PLUS_EXPOSED_GDT132_START_TO_NEXT_PAIRS",
        "exposed_sensitivity": "31_START_TO_NEXT_PAIRS_IDENTICAL_TO_CORRECTED_GDT132",
        "exact_strata_source_count": "EXACT_SOURCE_GROUP_COUNT_NOT_BUCKET",
        "exact_null_applies_to": "PRIMARY_CONTINUATION_TO_CONTINUATION_ONLY",
        "overlap_sensitivity": "SOURCE_LINE_PARITY_NONOVERLAPPING_SUBSETS",
    },
    "input_hashes": {SOURCE.name: sha(SOURCE), FRAMES.name: sha(FRAMES)},
    "claim_limit": (
        "The corrected run is a post-enumeration scope repair. Its exact null is capacity-limited; "
        "the start-to-next subset is an exposed duplicate and cannot count as replication."
    ),
}
correction["correction_content_sha256"] = content_sha(correction)
OUT.write_text(json.dumps(correction, indent=2, sort_keys=True) + "\n")
print(json.dumps({"status": correction["status"], "superseded_pairs": SUPERSEDED["pairs"]}, sort_keys=True))
