#!/usr/bin/env python3
"""Strict offline validator for the GDT621 double-reading registration."""

from __future__ import annotations

import argparse
import ast
import hashlib
import importlib.util
import json
import os
import re
import stat
import subprocess
import sys
from pathlib import Path
from typing import Any


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
BASE_REL = Path("experiments/yolo/gdt621_manual_source_double_reading")
BASE = ROOT / BASE_REL
PROFILE_REL = BASE_REL / "artifacts/REGISTERED_READING_PROFILE.json"
VALIDATION_REL = BASE_REL / "artifacts/REGISTERED_VALIDATION.json"
MANIFEST_REL = BASE_REL / "experiment.json"
RUN_REL = BASE_REL / "src/run.py"
VALIDATOR_REL = BASE_REL / "src/validate.py"
GDT620_RESULT_REL = Path(
    "experiments/yolo/gdt620_stage_b_source_page_acquisition/"
    "artifacts/STAGE_B_RESULT.json"
)

STATUS = "DOUBLE_READING_PROFILE_REGISTERED__NO_SOURCE_IMAGE_OPENED"
CLAIM_CEILING = (
    "MANUAL_SOURCE_READING_PROTOCOL_ONLY__NO_IMAGE_OPENED_AT_REGISTRATION__"
    "NO_VOYNICH_SIGN_WORD_LANGUAGE_PLAINTEXT_PLANT_OR_MEANING"
)
GDT620_REGISTRATION_COMMIT = "61a253ce2756ad06a6c69c620e702500f5e640ef"
# Replaced with the separate public result commit after GDT620 is pushed.  A
# non-hex placeholder deliberately keeps registration validation closed.
GDT620_RESULT_PUBLICATION_COMMIT = "798e05f46e79c4abd2047577669d3a67d561ec51"
GDT620_RESULT_SHA = (
    "f14976f54fd4ea0424ada9f23d19e7f02424beff739f5b4943dd3b0329ae378e"
)
BUILDER_SHA = "ef7178d314de8f5eeaf68ab77c5c1ae808d3fbf60d981ba32b30974f4f41ca3a"
PROFILE_SHA = "c34724e98e4da65564eb3245c0b7b82ee8d109748a98b253ffd67ed835886c9b"
GDT620_RESULT_STATUS = (
    "TEN_SOURCE_PAGES_ACQUIRED__SOURCE_READING_UNOPENED__TARGET_UNOPENED"
)

EXPECTED_QUESTION = (
    "Can two blinded readers independently produce and reconcile a diplomatic "
    "Latin heading-plus-twelve-token transcription before any control or "
    "Voynich target access?"
)
EXPECTED_MANIFEST_CLAIM_CEILING = (
    "This registration freezes a two-reader, Latin-first diplomatic "
    "source-reading protocol. It opens no source image, reads no source text, "
    "and accesses no Voynich target. A later compliant result can establish "
    "only a reproducible source transcription; it cannot assign any Voynich "
    "sign, word, language, plaintext, plant, operation, or meaning."
)
EXPECTED_ARTIFACT_POLICY = {
    "large_artifact_justification": (
        "The ten immutable full-page JPEGs remain private and outside the "
        "repository. Registration retains only compact protocol, profile, and "
        "validation artifacts; no image bytes, crops, renderings, private "
        "paths, or reader submissions are published."
    ),
    "max_inline_bytes": 5_000_000,
}

HEX40 = re.compile(r"^[0-9a-f]{40}$")
HEX64 = re.compile(r"^[0-9a-f]{64}$")
IMAGE_OR_DOCUMENT_SUFFIXES = {
    ".bmp", ".gif", ".jp2", ".jpeg", ".jpg", ".pdf", ".png", ".tif",
    ".tiff", ".webp",
}

EXPECTED_INPUTS = {str(GDT620_RESULT_REL)}
EXPECTED_OUTPUTS = {
    str(BASE_REL / "README.md"),
    str(BASE_REL / "METHOD.md"),
    str(BASE_REL / "PREREGISTRATION.md"),
    str(BASE_REL / "artifacts/README.md"),
    str(PROFILE_REL),
    str(VALIDATION_REL),
    str(RUN_REL),
    str(VALIDATOR_REL),
}
EXPECTED_TREE_FILES = {
    "README.md",
    "METHOD.md",
    "PREREGISTRATION.md",
    "artifacts/README.md",
    "artifacts/REGISTERED_READING_PROFILE.json",
    "artifacts/REGISTERED_VALIDATION.json",
    "experiment.json",
    "src/run.py",
    "src/validate.py",
}
EXPECTED_TREE_DIRECTORIES = {"artifacts", "src"}

EXPECTED_BINDINGS = (
    (1, "01_BSB_CLM28531_DEV01.jpg", "DEV01", "Balsamus", "CLM28531", "82b476a028ad94ba7392520a4cba527c9dc521a577207bbec5842d0f7e266c50", 1707, 2466, 654233),
    (2, "02_BSB_CLM28531_DEV02.jpg", "DEV02", "Cerfolium", "CLM28531", "e0c56b10b19e823c7b0247881d1cf27a1302cced0bd432956b98c47aab78746f", 1707, 2581, 590262),
    (3, "03_BSB_CLM28531_DEV03.jpg", "DEV03", "Liquiritia", "CLM28531", "4d87c0f033236b88abbb0ce6a5fe24a3664d63660080e15e0763642d9444aee0", 1707, 2562, 616531),
    (4, "04_BSB_CLM28531_DEV04.jpg", "DEV04", "Cucurbita", "CLM28531", "f5a112fd194f45db72518e1a146f05bd2eec239e346a1b137cba7f1eab24e035", 1707, 2591, 562974),
    (5, "05_BSB_CLM28531_DEV05.jpg", "DEV05", "Diptamus", "CLM28531", "808ff7b43c074ee0e67770cf51d7a38f683254c1a11883bf799bc9deeee1f4a8", 1707, 2581, 481123),
    (6, "06_BNF_LAT6823_DEV01.jpg", "DEV01", "Balsamus", "LAT6823", "a12f51056ad4e18ae4ed40739987dae3924618787ebbaac1c481ac0b2976ef2a", 3302, 4581, 2399224),
    (7, "07_BNF_LAT6823_DEV02.jpg", "DEV02", "Cerfolium", "LAT6823", "470aca9b7d6cdfd9aa3cb321d165f86b01e15f8de8193e50d8a9dbb722c71b11", 3451, 4553, 1815181),
    (8, "08_BNF_LAT6823_DEV03.jpg", "DEV03", "Liquiritia", "LAT6823", "01397d43449619b004fcee6fdacc3e236dfb3523f689ef0c51d0ff550f30b6b4", 3284, 4557, 2242239),
    (9, "09_BNF_LAT6823_DEV04.jpg", "DEV04", "Cucurbita", "LAT6823", "055dd108bbec73ca7a8b80f9cfa3c467b3ca560ef9650015f05aaffd2e28ca8d", 3333, 4388, 1896600),
    (10, "10_BNF_LAT6823_DEV05.jpg", "DEV05", "Diptamus", "LAT6823", "8091ac2ac1939ac11e88d314501c4ef68d0015e6c38b89ad08a07a30521e0a4a", 3346, 4574, 1920542),
)

EXPECTED_READING_ORDER = [
    "READER_A_FIVE_RAW_CANONICAL_SUBMISSIONS",
    "READER_A_COMMITMENT_VERIFIED",
    "READER_B_FIVE_RAW_CANONICAL_SUBMISSIONS",
    "READER_B_COMMITMENT_VERIFIED",
    "BOTH_RAW_COMMITMENTS_FROZEN",
    "LATIN_RECONCILIATION",
    "LATIN_RECONCILIATION_FROZEN_ARTIFACT_VALIDATED",
    "PUBLIC_CHECKPOINT_COMMITTED_AND_HASH_VERIFIED",
    "CLM28531_FIVE_CONTROL_VIEWS",
]
EXPECTED_READER_PROTOCOL = {
    "readers": ["A", "B"],
    "independent_fresh_rendering_per_reader_and_page": True,
    "other_reader_rendering_hidden": True,
    "other_reader_submission_hidden_until_both_submitted": True,
    "submission_is_diplomatic_and_immutable_before_comparison": True,
    "latin_pages_first": [6, 7, 8, 9, 10],
    "separate_agent_sessions": True,
    "separate_rendering_sessions": True,
    "distinct_session_id_per_reader": True,
    "session_id_must_differ_between_readers": True,
    "precomparison_storage": "ROOT_MAILBOX_ONLY",
    "shared_workspace_materialization_before_both_complete": False,
    "both_complete_definition": (
        "five canonical hashable raw submissions from each reader"
    ),
    "reader_id_pattern": "^READER_[AB]$",
    "session_id_pattern": "^SESSION_[AB]_[A-F0-9]{16}$",
    "required_capture": {
        "heading_or_rubric": "diplomatic codepoint string",
        "lexical_tokens_after_heading": "exactly_12 whitespace-delimited diplomatic tokens",
        "spacing": "preserve visible spacing decisions",
        "abbreviations": "preserve visible abbreviation marks without silent expansion",
        "uncertainties": "codepoint-addressed notes",
        "reading_region": "main_text_block_only; exclude marginalia and image labels",
        "reading_order": "top-to-bottom then left-to-right",
        "rubric_end": "visible transition from rubric to main text",
        "token_definition": (
            "maximal run of non-whitespace codepoints; line break is whitespace; "
            "punctuation and abbreviation signs remain attached"
        ),
        "diplomatic_notation": {
            "expansion_or_normalization": "forbidden",
            "non_keyboard_sign": (
                "ASCII tag <SIGN:DESCRIPTION> with no whitespace"
            ),
            "notation_version": "GDT621_DIPLOMATIC_V1",
            "uncertain_boundary": (
                "record separately; never silently alter whitespace"
            ),
            "uncertain_letterform": (
                "ASCII tag <UNCERTAIN:x> with no whitespace; x is best literal "
                "letterform"
            ),
            "unicode_rule": "exact UTF-8 codepoints; no Unicode normalization",
            "unreadable_letterform": "ASCII tag <UNREADABLE> with no whitespace",
            "visible_letterform_policy": (
                "transcribe the visible letterform only; do not silently "
                "modernize, expand, or substitute"
            ),
        },
    },
}
EXPECTED_RECONCILIATION = {
    "access_audit": {
        "required_before_checkpoint": True,
        "attestation_precedes_checkpoint_hash": True,
        "allowed_inputs": (
            "only the two frozen raw bundles and the five registered Latin JPEGs "
            "when resolving glyphs"
        ),
        "exact_required_fields": [
            "adjudicator_id",
            "session_id",
            "started_utc",
            "completed_utc",
            "attested_utc",
            "frozen_reader_a_bundle_sha256",
            "frozen_reader_b_bundle_sha256",
            "only_frozen_bundles_and_five_latin_jpegs_used",
            "clm_access_count",
            "network_access_count",
            "repository_or_profile_access_count",
            "catalog_access_count",
            "edition_access_count",
            "other_source_access_count",
            "voynich_access_count",
            "f84_access_count",
            "f84r_access_count",
        ],
        "required_values": {
            "only_frozen_bundles_and_five_latin_jpegs_used": True,
            "clm_access_count": 0,
            "network_access_count": 0,
            "repository_or_profile_access_count": 0,
            "catalog_access_count": 0,
            "edition_access_count": 0,
            "other_source_access_count": 0,
            "voynich_access_count": 0,
            "f84_access_count": 0,
            "f84r_access_count": 0,
        },
    },
    "begins_only_after_both_complete_latin_submissions": True,
    "compare_every_codepoint": True,
    "compare_spacing": True,
    "compare_abbreviation_marks": True,
    "compare_token_boundaries": True,
    "difference_ledger_required": True,
    "difference_row_fields": [
        "candidate_id", "row_kind", "field", "position", "reader_a", "reader_b",
        "difference_type", "reconciled_reading", "resolution_reason",
        "adjudicator", "resolved_utc",
    ],
    "zero_difference_pages_require_explicit_zero_row": True,
    "row_kinds": {
        "difference": "DIFFERENCE",
        "agreement_sentinel": "AGREEMENT_NO_DIFFERENCE",
    },
    "zero_difference_rule": (
        "exactly one AGREEMENT_NO_DIFFERENCE row per zero-difference page; "
        "position, readings, resolution, adjudicator and resolved_utc are null; "
        "no fabricated position"
    ),
    "adjudicator_id_pattern": "^ADJUDICATOR_[A-F0-9]{16}$",
}
EXPECTED_CLM_CONTROL = {
    "pages": [1, 2, 3, 4, 5],
    "opens_only_after_both_latin_submissions": True,
    "opens_only_after_public_latin_reconciliation_checkpoint_commit": True,
    "separate_locator_control": True,
    "may_not_repair_or_replace_latin": True,
    "required_capture": "visible rubric/locator label plus notes only",
}
EXPECTED_DISPLAY_POLICY = {
    "local_only": True,
    "immutable_source_jpeg": True,
    "full_page_must_be_displayed_first": True,
    "zoom_allowed_after_full_page": True,
    "crop_may_be_viewed_in_memory": True,
    "derived_image_may_not_be_saved": True,
    "image_modification": False,
    "temporary_display_scaling_or_zoom_allowed": True,
    "immutable_source_jpeg_exists_and_is_never_rewritten": True,
    "temporary_in_memory_renderer_output_may_scale_or_resample_for_display": True,
    "persisted_derivative_forbidden": True,
    "rotation_enhancement_annotation_or_source_rewrite_forbidden": True,
}
EXPECTED_FORBIDDEN_METHODS = [
    "OCR", "AUTOMATIC_IMAGE_CLASSIFICATION", "AUTOMATIC_TEXT_RECOGNITION",
    "VOYNICH_TARGET_ACCESS", "F84", "F84R",
]
EXPECTED_LOCATOR_BLINDING = {
    "registered_headwords_are_locator_hints_not_discovery_endpoint": True,
    "reader_visible_inputs_ref": "locator_blinding.reader_packet.exact_payload_keys",
    "reader_forbidden_session_sources": [
        "registered_profile",
        "repository",
        "catalog",
        "edition",
        "network",
        "other_sources",
    ],
    "reader_attestation_required": True,
    "heading_or_rubric_remains_independent_diplomatic_capture": True,
    "primary_new_capture": "exactly_12_following_tokens",
    "reader_packet": {
        "exact_payload_keys": [
            "opaque_candidate_id",
            "source_sha256",
            "session_id",
            "opaque_rendering_handle",
        ],
        "additional_keys_allowed": False,
        "canonicalization": "UTF-8 JSON; sorted keys; compact separators; LF final byte",
        "sha256_preimage_rule": (
            "payload contains no hash field; compute SHA-256 over exact canonical payload"
        ),
        "reader_must_attest_exact_packet_keys_and_sha256": True,
        "rendering_handle_must_not_contain_path": True,
        "opaque_rendering_handle_pattern": "^R[AB][0-9]{2}-[0-9A-F]{16}$",
        "exact_value_checks": {
            "opaque_candidate_id_pattern": "^DEV0[1-5]$",
            "source_sha256_pattern": "^[0-9a-f]{64}$",
            "session_id_pattern": "^SESSION_[AB]_[A-F0-9]{16}$",
            "opaque_rendering_handle_forbids_semantic_text_path_url_or_headword": True,
        },
        "excluded_fields": [
            "headword",
            "witness_or_control_identity",
            "url",
            "crosswalk",
            "profile_or_repository_locator",
            "expected_rubric",
            "other_reader_submission",
            "private_filename",
            "private_directory",
        ],
    },
}
EXPECTED_CHECKPOINT_SCHEMA = {
    "additional_keys_allowed": False,
    "exact_artifact_keys": [
        "experiment_id",
        "status",
        "gdt620_binding",
        "raw_bundle_sha256s",
        "reconciled_latin",
        "difference_ledger",
        "reconciliation_access_audit",
        "canonicalization",
        "claim_ceiling",
        "checkpoint_sha256",
    ],
    "hash_preimage_exact_keys": [
        "experiment_id",
        "status",
        "gdt620_binding",
        "raw_bundle_sha256s",
        "reconciled_latin",
        "difference_ledger",
        "reconciliation_access_audit",
        "canonicalization",
        "claim_ceiling",
    ],
    "own_sha256_preimage": (
        "exact canonical checkpoint payload with checkpoint_sha256 absent; "
        "insert hash afterward"
    ),
    "required_values": {
        "experiment_id": "GDT621",
        "status": "LATIN_RECONCILIATION_FROZEN__CLM_UNOPENED",
    },
    "gdt620_binding_exact_keys": [
        "gdt620_acquisition_code_registration_commit",
        "gdt620_result_publication_commit",
        "gdt620_result_path",
        "gdt620_result_sha256",
    ],
    "raw_bundle_sha256s": {
        "exact_keys": ["READER_A", "READER_B"],
        "ordered": True,
        "sha256_pattern": "^[0-9a-f]{64}$",
    },
    "reconciled_latin": {
        "exactly_five_pages": True,
        "page_order": ["DEV01", "DEV02", "DEV03", "DEV04", "DEV05"],
        "each_page_exact_keys": [
            "candidate_id",
            "source_sha256",
            "heading_or_rubric",
            "tokens_1_through_12",
            "diplomatic_stream",
            "uncertainties",
        ],
        "exactly_12_tokens_each": True,
    },
    "difference_ledger": {
        "complete_for_all_five_pages": True,
        "ordinary_row_kind": "DIFFERENCE",
        "zero_page_exact_sentinel": "AGREEMENT_NO_DIFFERENCE",
        "zero_page_has_exactly_one_sentinel": True,
    },
}
EXPECTED_PHASE_SEALS = {
    "raw_double_submission": {
        "required_before_reconciliation": True,
        "canonicalization": "UTF-8 JSON; sorted keys; compact separators; LF final byte",
        "hash": "SHA-256 over canonical bytes",
        "requires": (
            "exactly one ordered DEV01..DEV05 canonical bundle for READER_A "
            "and exactly one for READER_B; each page once; verified bundle SHA-256"
        ),
        "hash_preimage_rule": (
            "compute SHA-256 over canonical payload with its own hash field absent; "
            "insert hash only afterward"
        ),
    },
    "latin_reconciliation": {
        "required_before_clm": True,
        "checkpoint_path": "artifacts/LATIN_RECONCILIATION_FROZEN.json",
        "checkpoint_status": "LATIN_RECONCILIATION_FROZEN__CLM_UNOPENED",
        "canonicalization": "UTF-8 JSON; sorted keys; compact separators; LF final byte",
        "hash": "SHA-256 over canonical bytes",
        "must_be_publicly_committed_before_clm_open": True,
        "clm_may_trigger_latin_change": False,
        "checkpoint_schema": EXPECTED_CHECKPOINT_SCHEMA,
        "hash_preimage_rule": (
            "compute SHA-256 over canonical payload with its own hash field absent; "
            "insert hash only afterward"
        ),
    },
}
EXPECTED_RESULT_CONTRACT = {
    "statuses": [
        STATUS,
        "LATIN_READER_A_SUBMITTED__READER_B_BLINDED",
        "LATIN_READER_B_SUBMITTED__READER_A_BLINDED",
        "LATIN_DOUBLE_SUBMISSIONS_FROZEN__RECONCILIATION_PENDING",
        "LATIN_RECONCILED__CLM_CONTROL_PENDING",
        "LATIN_RECONCILIATION_FROZEN__CLM_UNOPENED",
        "SOURCE_DOUBLE_READING_COMPLETE__TARGET_UNOPENED",
        "MANUAL_READING_STOP",
    ],
    "required_top_level_fields": [
        "experiment_id", "status", "dependency", "reader_submissions",
        "difference_ledger", "reconciled_latin", "clm_control",
        "access_audit", "claim_ceiling",
    ],
    "reader_submission_page_fields": [
        "candidate_id", "source_sha256", "rendering_session_id",
        "full_page_viewed_first", "heading_or_rubric", "tokens_1_through_12",
        "diplomatic_stream", "uncertainties", "submitted_utc",
        "access_audit_ref",
    ],
    "public_result_must_exclude": [
        "private_directory", "absolute_path", "image_bytes", "saved_crop",
        "voynich_material",
    ],
}

_LATIN_HASHES = {
    candidate: sha
    for _sequence, _filename, candidate, _headword, witness, sha,
    _width, _height, _byte_count in EXPECTED_BINDINGS
    if witness == "LAT6823"
}
_CLM_HASHES = {
    candidate: sha
    for _sequence, _filename, candidate, _headword, witness, sha,
    _width, _height, _byte_count in EXPECTED_BINDINGS
    if witness == "CLM28531"
}
EXPECTED_LATIN_EVENT_ORDER = [
    {
        "sequence": sequence,
        "reader_id": reader,
        "candidate_id": f"DEV{candidate_number:02d}",
        "source_sha256": _LATIN_HASHES[f"DEV{candidate_number:02d}"],
    }
    for sequence, (reader, candidate_number) in enumerate(
        [
            (reader, candidate_number)
            for reader in ("READER_A", "READER_B")
            for candidate_number in range(1, 6)
        ],
        1,
    )
]
EXPECTED_CLM_EVENT_ORDER = [
    {
        "sequence": candidate_number,
        "candidate_id": f"DEV{candidate_number:02d}",
        "source_sha256": _CLM_HASHES[f"DEV{candidate_number:02d}"],
    }
    for candidate_number in range(1, 6)
]
EXPECTED_ACCESS_AUDIT = {
    "canonical_schema_source": True,
    "latin_event_count": 10,
    "latin_event_order": EXPECTED_LATIN_EVENT_ORDER,
    "latin_event_required_fields": [
        "sequence",
        "reader_id",
        "session_id",
        "candidate_id",
        "source_sha256",
        "reader_packet_sha256",
        "reader_packet_exact_keys_verified",
        "opened_utc",
        "closed_utc",
        "attested_utc",
        "full_page_viewed_first",
        "only_opaque_packet_used",
        "profile_not_consulted",
        "repository_not_consulted",
        "catalog_not_consulted",
        "edition_not_consulted",
        "network_not_consulted",
        "other_sources_not_consulted",
        "other_reader_material_not_seen",
        "ocr_or_automation_used",
    ],
    "latin_required_values": {
        "full_page_viewed_first": True,
        "only_opaque_packet_used": True,
        "reader_packet_exact_keys_verified": True,
        "profile_not_consulted": True,
        "repository_not_consulted": True,
        "catalog_not_consulted": True,
        "edition_not_consulted": True,
        "network_not_consulted": True,
        "other_sources_not_consulted": True,
        "other_reader_material_not_seen": True,
        "ocr_or_automation_used": False,
    },
    "clm_event_count": 5,
    "clm_event_order": EXPECTED_CLM_EVENT_ORDER,
    "clm_event_required_fields": [
        "sequence",
        "controller_id",
        "session_id",
        "candidate_id",
        "source_sha256",
        "checkpoint_committed_utc",
        "opened_utc",
        "closed_utc",
        "attested_utc",
        "full_page_viewed_first",
        "public_checkpoint_commit",
        "public_checkpoint_sha256",
        "public_checkpoint_commit_verified",
        "public_checkpoint_hash_verified",
        "clm_changed_latin",
        "ocr_or_automation_used",
    ],
    "clm_event_required_values": {
        "full_page_viewed_first": True,
        "public_checkpoint_commit_verified": True,
        "public_checkpoint_hash_verified": True,
        "clm_changed_latin": False,
        "ocr_or_automation_used": False,
    },
    "clm_temporal_rule": (
        "for every Clm event, opened_utc must be strictly later than "
        "checkpoint_committed_utc"
    ),
    "controller_id_pattern": "^CONTROLLER_[A-F0-9]{16}$",
    "controller_session_id_pattern": "^CLM_SESSION_[A-F0-9]{16}$",
    "global_required_values": {
        "target_access_count": 0,
        "voynich_access_count": 0,
        "f84_access_count": 0,
        "f84r_access_count": 0,
    },
}
EXPECTED_RESULT_CONTRACT.update(
    {
        "raw_bundle_contract": {
            "additional_keys_allowed": False,
            "canonicalization": (
                "UTF-8 JSON; sorted keys; compact separators; LF final byte"
            ),
            "exactly_one_bundle_per_reader": True,
            "reader_order": ["READER_A", "READER_B"],
            "exact_artifact_keys": [
                "reader_id",
                "session_id",
                "pages",
                "submitted_utc",
                "bundle_sha256",
            ],
            "hash_preimage_exact_keys": [
                "reader_id",
                "session_id",
                "pages",
                "submitted_utc",
            ],
            "bundle_sha256_preimage": (
                "exact canonical bundle payload with bundle_sha256 absent"
            ),
            "bundle_sha256_pattern": "^[0-9a-f]{64}$",
            "page_order": ["DEV01", "DEV02", "DEV03", "DEV04", "DEV05"],
            "each_candidate_exactly_once": True,
            "page_exact_payload_keys": [
                "candidate_id",
                "source_sha256",
                "rendering_session_id",
                "full_page_viewed_first",
                "heading_or_rubric",
                "tokens_1_through_12",
                "diplomatic_stream",
                "uncertainties",
                "submitted_utc",
                "access_audit_ref",
            ],
            "page_source_sha256_must_equal_registered_latin_binding": True,
        },
        "checkpoint_binding": {
            "required_fields": [
                "latin_checkpoint_public_commit",
                "latin_checkpoint_sha256",
            ],
            "checkpoint_commit_and_sha_must_be_verified_before_clm": True,
            "final_raw_bundle_sha256s_must_byte_identically_equal_checkpoint": True,
            "final_reconciled_latin_must_byte_identically_equal_checkpoint": True,
            "final_difference_ledger_must_byte_identically_equal_checkpoint": True,
            "later_latin_change_forbidden": True,
        },
        "canonicalization": {
            "encoding": "UTF-8",
            "json_keys": "sorted",
            "separators": [",", ":"],
            "terminal_newline": "LF",
            "hash": "SHA-256 over exact canonical bytes",
            "hash_preimage_rule": (
                "compute artifact SHA-256 with that artifact's own hash field "
                "absent; insert hash only afterward"
            ),
        },
        "access_audit": EXPECTED_ACCESS_AUDIT,
        "privacy": {
            "absolute_path_regex_forbidden": (
                "(^|[\\s\"'])(/|[A-Za-z]:[\\\\/])"
            ),
            "private_directory_components_forbidden": True,
            "image_bytes_forbidden": True,
            "bare_registered_filenames_allowed_only_in_registered_profile": True,
            "reader_results_should_use_candidate_id_and_source_sha256_not_filename": True,
        },
    }
)


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_bytes(value: Any) -> bytes:
    return (
        json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False) + "\n"
    ).encode("utf-8")


def is_safe_regular(path: Path, boundary: Path) -> bool:
    try:
        info = path.lstat()
        resolved = path.resolve(strict=True)
        resolved.relative_to(boundary.resolve(strict=True))
    except (FileNotFoundError, OSError, RuntimeError, ValueError):
        return False
    return stat.S_ISREG(info.st_mode) and not stat.S_ISLNK(info.st_mode)


def load_json(path: Path, boundary: Path) -> dict[str, Any]:
    if not is_safe_regular(path, boundary):
        return {}
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError):
        return {}
    return value if isinstance(value, dict) else {}


def as_dict(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def load_module(relative: Path, name: str):
    sys.dont_write_bytecode = True
    spec = importlib.util.spec_from_file_location(name, ROOT / relative)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {relative}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    try:
        spec.loader.exec_module(module)
    except Exception:
        sys.modules.pop(name, None)
        raise
    return module


def safe_git_run(arguments: list[str]) -> subprocess.CompletedProcess[bytes]:
    environment = {
        key: value for key, value in os.environ.items() if not key.startswith("GIT_")
    }
    environment.update(
        {
            "GIT_CONFIG_GLOBAL": "/dev/null",
            "GIT_CONFIG_NOSYSTEM": "1",
            "GIT_OPTIONAL_LOCKS": "0",
        }
    )
    return subprocess.run(
        [
            "/usr/bin/git",
            f"--git-dir={ROOT / '.git'}",
            f"--work-tree={ROOT}",
            "--no-pager",
            *arguments,
        ],
        cwd=ROOT,
        env=environment,
        check=False,
        capture_output=True,
        timeout=30,
    )


def git_blob(commit: str, relative: Path) -> bytes | None:
    completed = safe_git_run(["show", f"{commit}:{relative.as_posix()}"])
    return completed.stdout if completed.returncode == 0 else None


def git_ancestor(commit: str, descendant: str) -> bool:
    return (
        safe_git_run(["merge-base", "--is-ancestor", commit, descendant]).returncode
        == 0
    )


def is_exact_main_guard(statement: ast.If) -> bool:
    test = statement.test
    return (
        isinstance(test, ast.Compare)
        and isinstance(test.left, ast.Name)
        and test.left.id == "__name__"
        and len(test.ops) == 1
        and isinstance(test.ops[0], ast.Eq)
        and len(test.comparators) == 1
        and isinstance(test.comparators[0], ast.Constant)
        and test.comparators[0].value == "__main__"
    )


def qualified_name(node: ast.AST) -> str:
    parts: list[str] = []
    while isinstance(node, ast.Attribute):
        parts.append(node.attr)
        node = node.value
    if isinstance(node, ast.Name):
        parts.append(node.id)
    return ".".join(reversed(parts))


def builder_static_findings(path: Path) -> list[str]:
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    except (OSError, UnicodeDecodeError, SyntaxError) as exc:
        return [f"parse:{type(exc).__name__}"]
    findings: list[str] = []
    forbidden_import_roots = {
        "PIL", "cv2", "http", "numpy", "pytesseract", "requests", "socket",
        "subprocess", "urllib",
    }
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name.split(".", 1)[0] in forbidden_import_roots:
                    findings.append(f"forbidden-import:{alias.name}")
        elif isinstance(node, ast.ImportFrom):
            root = (node.module or "").split(".", 1)[0]
            if root in forbidden_import_roots:
                findings.append(f"forbidden-import:{node.module}")

    network_names = {
        "connect", "connect_ex", "create_connection", "getaddrinfo",
        "requests.get", "requests.post", "requests.request", "sendmsg", "sendto",
        "socket.create_connection", "socket.getaddrinfo",
        "urllib.request.urlopen", "urlopen",
    }

    class ExecutedAtImport(ast.NodeVisitor):
        def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
            for decorator in node.decorator_list:
                self.visit(decorator)
            for default in (*node.args.defaults, *node.args.kw_defaults):
                if default is not None:
                    self.visit(default)
            if node.returns is not None:
                self.visit(node.returns)

        visit_AsyncFunctionDef = visit_FunctionDef

        def visit_Lambda(self, node: ast.Lambda) -> None:
            del node

        def visit_ClassDef(self, node: ast.ClassDef) -> None:
            for decorator in node.decorator_list:
                self.visit(decorator)
            for base in node.bases:
                self.visit(base)
            for keyword in node.keywords:
                self.visit(keyword.value)
            for statement in node.body:
                self.visit(statement)

        def visit_If(self, node: ast.If) -> None:
            if is_exact_main_guard(node):
                for statement in node.orelse:
                    self.visit(statement)
                return
            self.generic_visit(node)

        def visit_Call(self, node: ast.Call) -> None:
            name = qualified_name(node.func)
            tail = name.rsplit(".", 1)[-1]
            if name in network_names or tail in {
                "connect", "connect_ex", "create_connection", "getaddrinfo",
                "sendmsg", "sendto", "urlopen",
            }:
                findings.append(f"top-level-network-call:{name}")
            self.generic_visit(node)

    ExecutedAtImport().visit(tree)
    return sorted(set(findings))


def tree_snapshot(root: Path, *, strong: bool) -> tuple[tuple[Any, ...], ...]:
    rows: list[tuple[Any, ...]] = []
    for current, directory_names, file_names in os.walk(root, followlinks=False):
        current_path = Path(current)
        if current_path == ROOT and ".git" in directory_names:
            directory_names.remove(".git")
        for name in sorted(directory_names + file_names):
            path = current_path / name
            relative = path.relative_to(root).as_posix()
            info = path.lstat()
            if stat.S_ISLNK(info.st_mode):
                rows.append((relative, "L", info.st_mode, os.readlink(path)))
                if name in directory_names:
                    directory_names.remove(name)
            elif stat.S_ISDIR(info.st_mode):
                rows.append((relative, "D", info.st_mode, info.st_mtime_ns))
            elif stat.S_ISREG(info.st_mode):
                rows.append(
                    (
                        relative,
                        "F",
                        info.st_mode,
                        info.st_size,
                        info.st_mtime_ns,
                        info.st_ctime_ns,
                        (
                            digest(path)
                            if strong
                            and relative in EXPECTED_TREE_FILES
                            and path.suffix.lower()
                            not in IMAGE_OR_DOCUMENT_SUFFIXES
                            else None
                        ),
                    )
                )
            else:
                rows.append((relative, "O", info.st_mode, info.st_size))
    return tuple(sorted(rows))


def collect_tree() -> tuple[set[str], set[str], list[str]]:
    files: set[str] = set()
    directories: set[str] = set()
    special: list[str] = []
    for current, directory_names, file_names in os.walk(BASE, followlinks=False):
        current_path = Path(current)
        for name in sorted(directory_names + file_names):
            path = current_path / name
            relative = path.relative_to(BASE).as_posix()
            info = path.lstat()
            if stat.S_ISLNK(info.st_mode):
                special.append(relative)
                if name in directory_names:
                    directory_names.remove(name)
            elif stat.S_ISDIR(info.st_mode):
                directories.add(relative)
            elif stat.S_ISREG(info.st_mode):
                files.add(relative)
            else:
                special.append(relative)
    return files, directories, special


def privacy_findings(data: bytes, label: str) -> list[str]:
    text = data.decode("utf-8", errors="replace")
    findings: list[str] = []
    private_markers = (
        "/" + "home" + "/",
        "/" + "tmp" + "/",
        "/" + "Users" + "/",
        "file" + "://",
        "C:" + "\\Users\\",
        "-----BEGIN " + "PRIVATE KEY-----",
        "-----BEGIN " + "RSA PRIVATE KEY-----",
        "-----BEGIN " + "OPENSSH PRIVATE KEY-----",
        "-----BEGIN " + "EC PRIVATE KEY-----",
    )
    for marker in private_markers:
        if marker in text:
            findings.append(f"{label}:{marker[:24]}")
    credential_patterns = (
        re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
        re.compile(r"\bgh[pousr]_[A-Za-z0-9]{20,}\b"),
        re.compile(r"\bsk-[A-Za-z0-9_-]{20,}\b"),
        re.compile(r"(?i)\bbearer\s+[A-Za-z0-9._~+/-]{16,}={0,2}\b"),
        re.compile(
            r"(?i)\b(?:api[_-]?key|access[_-]?token|password|secret)\b"
            r"\s*[:=]\s*['\"][^'\"\r\n]{12,}['\"]"
        ),
    )
    for pattern in credential_patterns:
        if pattern.search(text):
            findings.append(f"{label}:credential-pattern")
    return findings


def private_path_name(path: str) -> bool:
    name = Path(path).name
    return (
        name in {".env", ".netrc", "credentials.json", "id_rsa", "id_ed25519"}
        or Path(name).suffix.lower() in {".key", ".p12", ".pem", ".pfx"}
        or name.startswith("GDT621_PRIVATE_")
        or name in {
            "READER_A_SUBMISSION.json",
            "READER_B_SUBMISSION.json",
            "DIFFERENCE_LEDGER.json",
            "READING_RESULT_DRAFT.json",
        }
    )


def staged_privacy_findings() -> list[str]:
    listed = safe_git_run(
        ["diff", "--cached", "--name-only", "-z", "--diff-filter=ACMR"]
    )
    if listed.returncode != 0:
        return ["staged-tree:list-failed"]
    findings: list[str] = []
    for raw_path in listed.stdout.split(b"\0"):
        if not raw_path:
            continue
        try:
            path = raw_path.decode("utf-8")
        except UnicodeDecodeError:
            findings.append("staged-tree:non-utf8-path")
            continue
        suffix = Path(path).suffix.lower()
        if suffix in IMAGE_OR_DOCUMENT_SUFFIXES:
            findings.append(f"staged-tree:forbidden-image-or-document:{path}")
            continue
        if private_path_name(path):
            findings.append(f"staged-tree:private-name:{path}")
            continue
        blob = safe_git_run(["show", f":{path}"])
        if blob.returncode != 0:
            findings.append(f"staged-tree:unreadable:{path}")
            continue
        findings.extend(privacy_findings(blob.stdout, f"staged:{path}"))
    return findings


class OfflineAccessForbidden(RuntimeError):
    pass


def offline_worker() -> int:
    """Import the builder with process, network, and image access denied."""

    import builtins
    import io
    import socket
    import urllib.request

    probe_network_events: list[str] = []
    probe_image_events: list[str] = []
    unexpected_network_events: list[str] = []
    unexpected_image_events: list[str] = []
    unexpected_process_events: list[str] = []
    probing_network = True
    probing_image = True

    def deny_network(label: str):
        def blocked(*_args: Any, **_kwargs: Any):
            target = probe_network_events if probing_network else unexpected_network_events
            target.append(label)
            raise OfflineAccessForbidden(label)

        return blocked

    socket.socket.connect = deny_network("socket.socket.connect")  # type: ignore[method-assign]
    socket.socket.connect_ex = deny_network("socket.socket.connect_ex")  # type: ignore[method-assign]
    socket.socket.sendto = deny_network("socket.socket.sendto")  # type: ignore[method-assign]
    if hasattr(socket.socket, "sendmsg"):
        socket.socket.sendmsg = deny_network("socket.socket.sendmsg")  # type: ignore[attr-defined,method-assign]
    socket.create_connection = deny_network("socket.create_connection")
    socket.getaddrinfo = deny_network("socket.getaddrinfo")
    urllib.request.urlopen = deny_network("urllib.request.urlopen")
    urllib.request.OpenerDirector.open = deny_network(
        "urllib.request.OpenerDirector.open"
    )
    urllib.request.AbstractHTTPHandler.do_open = deny_network(
        "urllib.request.AbstractHTTPHandler.do_open"
    )

    real_builtin_open = builtins.open
    real_io_open = io.open
    real_os_open = os.open

    def is_image_argument(value: Any) -> bool:
        try:
            return Path(os.fspath(value)).suffix.lower() in IMAGE_OR_DOCUMENT_SUFFIXES
        except (TypeError, ValueError):
            return False

    def guarded_builtin_open(file: Any, *args: Any, **kwargs: Any):
        if is_image_argument(file):
            target = probe_image_events if probing_image else unexpected_image_events
            target.append("builtins.open")
            raise OfflineAccessForbidden("image/document open")
        return real_builtin_open(file, *args, **kwargs)

    def guarded_io_open(file: Any, *args: Any, **kwargs: Any):
        if is_image_argument(file):
            target = probe_image_events if probing_image else unexpected_image_events
            target.append("io.open")
            raise OfflineAccessForbidden("image/document open")
        return real_io_open(file, *args, **kwargs)

    def guarded_os_open(file: Any, *args: Any, **kwargs: Any):
        if is_image_argument(file):
            target = probe_image_events if probing_image else unexpected_image_events
            target.append("os.open")
            raise OfflineAccessForbidden("image/document open")
        return real_os_open(file, *args, **kwargs)

    builtins.open = guarded_builtin_open  # type: ignore[assignment]
    io.open = guarded_io_open  # type: ignore[assignment]
    os.open = guarded_os_open  # type: ignore[assignment]

    def deny_process(*args: Any, **_kwargs: Any):
        unexpected_process_events.append(repr(args)[:160])
        raise OfflineAccessForbidden("process execution")

    subprocess.run = deny_process  # type: ignore[assignment]
    subprocess.Popen = deny_process  # type: ignore[assignment,misc]
    os.system = deny_process  # type: ignore[assignment]
    os.popen = deny_process  # type: ignore[assignment]
    for spawn_name in (
        "posix_spawn", "posix_spawnp", "spawnl", "spawnle", "spawnlp",
        "spawnlpe", "spawnv", "spawnve", "spawnvp", "spawnvpe",
    ):
        if hasattr(os, spawn_name):
            setattr(os, spawn_name, deny_process)

    def expect_blocked(action: Any, events: list[str]) -> bool:
        before = len(events)
        try:
            action()
        except OfflineAccessForbidden:
            return len(events) == before + 1
        return False

    def connect_probe(method: str) -> None:
        client = socket.socket()
        try:
            getattr(client, method)(("127.0.0.1", 9))
        finally:
            client.close()

    network_probes_ok = all(
        (
            expect_blocked(
                lambda: socket.getaddrinfo("example.invalid", 443),
                probe_network_events,
            ),
            expect_blocked(
                lambda: socket.create_connection(("127.0.0.1", 9), timeout=0.01),
                probe_network_events,
            ),
            expect_blocked(lambda: connect_probe("connect"), probe_network_events),
            expect_blocked(
                lambda: connect_probe("connect_ex"), probe_network_events
            ),
            expect_blocked(
                lambda: urllib.request.urlopen("https://example.invalid"),
                probe_network_events,
            ),
            expect_blocked(
                lambda: urllib.request.build_opener().open("https://example.invalid"),
                probe_network_events,
            ),
        )
    )
    image_probe_ok = all(
        (
            expect_blocked(
                lambda: builtins.open("__gdt621_forbidden_probe__.jpg", "rb"),
                probe_image_events,
            ),
            expect_blocked(
                lambda: io.open("__gdt621_forbidden_probe__.jpg", "rb"),
                probe_image_events,
            ),
            expect_blocked(
                lambda: os.open("__gdt621_forbidden_probe__.jpg", os.O_RDONLY),
                probe_image_events,
            ),
        )
    )
    probing_network = False
    probing_image = False

    try:
        profile_path = ROOT / PROFILE_REL
        builder = load_module(RUN_REL, "gdt621_builder_guarded")
        built = builder.build_profile()
        built_bytes = builder.canonical_bytes(built)
        payload = {
            "builder_profile_match": profile_path.read_bytes() == built_bytes,
            "builder_sha256": digest(ROOT / RUN_REL),
            "builder_values": {
                "gdt620_commit": builder.GDT620_COMMIT,
                "gdt620_result_commit": builder.GDT620_RESULT_COMMIT,
                "pages": [list(row) for row in builder.PAGES],
                "profile_rel": str(builder.PROFILE_REL),
                "result_rel": str(builder.RESULT_REL),
                "result_sha": builder.RESULT_SHA,
            },
            "guard_image_probe_events": probe_image_events,
            "guard_image_probe_ok": image_probe_ok,
            "guard_network_probe_events": probe_network_events,
            "guard_network_probes_ok": network_probes_ok,
            "image_open_attempts": unexpected_image_events,
            "network_attempts": unexpected_network_events,
            "process_attempts": unexpected_process_events,
            "profile_sha256": hashlib.sha256(built_bytes).hexdigest(),
            "schema_version": 1,
            "status": "PASS",
        }
        print(json.dumps(payload, sort_keys=True))
        return 0
    except BaseException as exc:
        print(
            json.dumps(
                {
                    "error_type": type(exc).__name__,
                    "guard_image_probe_events": probe_image_events,
                    "guard_image_probe_ok": image_probe_ok,
                    "guard_network_probe_events": probe_network_events,
                    "guard_network_probes_ok": network_probes_ok,
                    "image_open_attempts": unexpected_image_events,
                    "network_attempts": unexpected_network_events,
                    "process_attempts": unexpected_process_events,
                    "schema_version": 1,
                    "status": "FAIL",
                },
                sort_keys=True,
            )
        )
        return 1


def run_offline_worker() -> tuple[dict[str, Any], bool]:
    environment = {
        key: value
        for key, value in os.environ.items()
        if not key.startswith("PYTHON") and not key.startswith("GIT_")
    }
    environment.update(
        {
            "PYTHONDONTWRITEBYTECODE": "1",
            "PYTHONNOUSERSITE": "1",
            "PYTHONSAFEPATH": "1",
        }
    )
    completed = subprocess.run(
        [sys.executable, str(ROOT / VALIDATOR_REL), "--_offline-worker"],
        cwd=ROOT,
        env=environment,
        check=False,
        capture_output=True,
        timeout=90,
    )
    try:
        payload = json.loads(completed.stdout.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError):
        payload = {}
    return payload, completed.returncode == 0


class Audit:
    def __init__(self) -> None:
        self.rows: list[dict[str, str]] = []

    def check(self, name: str, condition: bool) -> None:
        self.rows.append({"check": name, "status": "PASS" if condition else "FAIL"})

    @property
    def passed(self) -> bool:
        return all(row["status"] == "PASS" for row in self.rows)

    def payload(self) -> dict[str, Any]:
        passed = sum(row["status"] == "PASS" for row in self.rows)
        return {
            "checks": self.rows,
            "decision": STATUS if self.passed else "REGISTRATION_VALIDATION_FAILURE",
            "experiment_id": "GDT621",
            "failed": len(self.rows) - passed,
            "images_opened": 0,
            "network_requests": 0,
            "passed": passed,
            "schema_version": 1,
            "source_text_read": False,
            "status": "PASS" if self.passed else "FAIL",
            "total": len(self.rows),
            "voynich_material_opened": False,
        }


def main() -> int:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--check", action="store_true")
    mode.add_argument("--write", action="store_true")
    mode.add_argument("--print-artifact-template", action="store_true")
    mode.add_argument("--_offline-worker", action="store_true", help=argparse.SUPPRESS)
    args = parser.parse_args()
    if args._offline_worker:
        return offline_worker()

    audit = Audit()
    profile_path = ROOT / PROFILE_REL
    result_path = ROOT / GDT620_RESULT_REL
    manifest_path = ROOT / MANIFEST_REL
    validation_path = ROOT / VALIDATION_REL
    profile = load_json(profile_path, BASE)
    result = load_json(result_path, ROOT)
    manifest = load_json(manifest_path, BASE)

    repository_before = tree_snapshot(ROOT, strong=False)
    experiment_before = tree_snapshot(BASE, strong=True)
    worker_inputs_safe = (
        is_safe_regular(ROOT / RUN_REL, BASE)
        and is_safe_regular(profile_path, BASE)
        and is_safe_regular(ROOT / VALIDATOR_REL, BASE)
    )
    worker, worker_completed = (
        run_offline_worker() if worker_inputs_safe else ({}, False)
    )
    experiment_after = tree_snapshot(BASE, strong=True)
    repository_after = tree_snapshot(ROOT, strong=False)

    audit.check(
        "canonical_builder_and_profile_bytes_exact",
        worker_completed
        and worker.get("status") == "PASS"
        and worker.get("builder_profile_match") is True
        and worker.get("builder_sha256") == BUILDER_SHA
        and worker.get("profile_sha256") == PROFILE_SHA
        and is_safe_regular(profile_path, BASE)
        and digest(profile_path) == PROFILE_SHA
        and profile_path.read_bytes() == canonical_bytes(profile),
    )
    expected_network_probes = {
        "socket.getaddrinfo",
        "socket.create_connection",
        "socket.socket.connect",
        "socket.socket.connect_ex",
        "urllib.request.urlopen",
        "urllib.request.OpenerDirector.open",
    }
    audit.check(
        "isolated_import_blocks_network_process_and_image_access",
        worker_completed
        and worker.get("guard_network_probes_ok") is True
        and set(worker.get("guard_network_probe_events", []))
        == expected_network_probes
        and worker.get("guard_image_probe_ok") is True
        and worker.get("guard_image_probe_events")
        == ["builtins.open", "io.open", "os.open"]
        and worker.get("network_attempts") == []
        and worker.get("image_open_attempts") == []
        and worker.get("process_attempts") == [],
    )
    audit.check(
        "guarded_import_leaves_repository_unchanged",
        experiment_before == experiment_after
        and repository_before == repository_after,
    )
    audit.check(
        "builder_is_inert_and_has_no_network_ocr_or_image_import",
        worker_inputs_safe and builder_static_findings(ROOT / RUN_REL) == [],
    )
    expected_builder_pages = [list(row[:-1]) for row in EXPECTED_BINDINGS]
    audit.check(
        "builder_dependency_constants_and_ten_bindings_exact",
        worker.get("builder_values")
        == {
            "gdt620_commit": GDT620_REGISTRATION_COMMIT,
            "gdt620_result_commit": GDT620_RESULT_PUBLICATION_COMMIT,
            "pages": expected_builder_pages,
            "profile_rel": str(PROFILE_REL),
            "result_rel": str(GDT620_RESULT_REL),
            "result_sha": GDT620_RESULT_SHA,
        },
    )

    expected_profile_keys = {
        "access_state_at_registration",
        "claim_ceiling",
        "clm_control",
        "dependency",
        "display_policy",
        "experiment_id",
        "forbidden_methods",
        "locator_blinding",
        "phase_seals",
        "private_page_bindings",
        "reader_protocol",
        "reading_order",
        "reconciliation",
        "result_contract",
        "schema_version",
        "sealed_data",
        "status",
    }
    audit.check(
        "profile_identity_status_claim_and_seals_exact",
        set(profile) == expected_profile_keys
        and profile.get("schema_version") == 1
        and profile.get("experiment_id") == "GDT621"
        and profile.get("status") == STATUS
        and "decision" not in profile
        and profile.get("claim_ceiling") == CLAIM_CEILING
        and profile.get("sealed_data")
        == {"f84": "FORBIDDEN", "f84r": "FORBIDDEN"},
    )
    audit.check(
        "profile_dependency_exact",
        profile.get("dependency")
        == {
            "gdt620_acquisition_code_registration_commit": GDT620_REGISTRATION_COMMIT,
            "gdt620_result_publication_commit": GDT620_RESULT_PUBLICATION_COMMIT,
            "gdt620_result_path": str(GDT620_RESULT_REL),
            "gdt620_result_sha256": GDT620_RESULT_SHA,
            "gdt620_result_status": GDT620_RESULT_STATUS,
        },
    )

    result_safe = is_safe_regular(result_path, ROOT)
    result_canonical = (
        result_safe
        and digest(result_path) == GDT620_RESULT_SHA
        and result_path.read_bytes() == canonical_bytes(result)
    )
    audit.check(
        "gdt620_result_canonical_sha_identity_and_access_boundary_exact",
        result_canonical
        and result.get("schema_version") == 1
        and result.get("experiment_id") == "GDT620"
        and result.get("status") == GDT620_RESULT_STATUS
        and result.get("failure_count") == 0
        and result.get("request_order") == list(range(1, 11))
        and result.get("sealed_data")
        == {"f84": "FORBIDDEN", "f84r": "FORBIDDEN"}
        and result.get("access_boundary")
        == {
            "automatic_transcription": False,
            "local_crop_created": False,
            "network_crop_requests": 0,
            "source_text_read": False,
            "target_opened": False,
            "voynich_material_opened": False,
        }
        and as_dict(result.get("gdt620_public_registration")).get("commit")
        == GDT620_REGISTRATION_COMMIT,
    )
    raw_result_pages = result.get("pages", [])
    result_pages = raw_result_pages if isinstance(raw_result_pages, list) else []
    result_rows = [
        (
            row.get("sequence"),
            row.get("candidate_id"),
            row.get("headword"),
            row.get("witness"),
            row.get("raw_sha256"),
            row.get("decoded_width"),
            row.get("decoded_height"),
            row.get("observed_bytes"),
        )
        for row in result_pages
        if isinstance(row, dict)
    ]
    expected_result_rows = [
        (sequence, candidate, headword, witness, sha, width, height, byte_count)
        for sequence, _filename, candidate, headword, witness, sha, width, height, byte_count
        in EXPECTED_BINDINGS
    ]
    audit.check(
        "gdt620_result_ten_image_hashes_dimensions_and_order_exact",
        result_rows == expected_result_rows
        and len({row[4] for row in result_rows}) == 10
        and all(HEX64.fullmatch(row[4] or "") is not None for row in result_rows),
    )
    raw_literal_urls = result.get("literal_urls", [])
    literal_urls = raw_literal_urls if isinstance(raw_literal_urls, list) else []
    audit.check(
        "gdt620_result_success_transport_rows_consistent",
        len(result_pages) == 10
        and len(literal_urls) == 10
        and all(isinstance(row, dict) for row in result_pages)
        and all(
            row.get("status") == "SUCCESS"
            and row.get("content_type") == "image/jpeg"
            and row.get("redirect_attempts") == 0
            and row.get("response_url") == row.get("request_url")
            and row.get("request_url") == literal_urls[index]
            for index, row in enumerate(result_pages)
        ),
    )

    publication_commit_valid = (
        HEX40.fullmatch(GDT620_RESULT_PUBLICATION_COMMIT) is not None
    )
    published_blob = (
        git_blob(GDT620_RESULT_PUBLICATION_COMMIT, GDT620_RESULT_REL)
        if publication_commit_valid
        else None
    )
    origin_blob = git_blob("refs/remotes/origin/main", GDT620_RESULT_REL)
    audit.check(
        "gdt620_result_commit_is_public_and_exact",
        publication_commit_valid
        and git_ancestor(GDT620_REGISTRATION_COMMIT, GDT620_RESULT_PUBLICATION_COMMIT)
        and git_ancestor(
            GDT620_RESULT_PUBLICATION_COMMIT, "refs/remotes/origin/main"
        )
        and published_blob is not None
        and hashlib.sha256(published_blob).hexdigest() == GDT620_RESULT_SHA
        and origin_blob is not None
        and hashlib.sha256(origin_blob).hexdigest() == GDT620_RESULT_SHA
        and result_safe
        and result_path.read_bytes() == published_blob == origin_blob,
    )
    inherited_git_dir = os.environ.get("GIT_DIR")
    inherited_git_work_tree = os.environ.get("GIT_WORK_TREE")
    try:
        os.environ["GIT_DIR"] = str(ROOT / "__forbidden_fake_git_dir__")
        os.environ["GIT_WORK_TREE"] = str(ROOT.parent)
        hostile_blob = (
            git_blob(GDT620_RESULT_PUBLICATION_COMMIT, GDT620_RESULT_REL)
            if publication_commit_valid
            else None
        )
    finally:
        if inherited_git_dir is None:
            os.environ.pop("GIT_DIR", None)
        else:
            os.environ["GIT_DIR"] = inherited_git_dir
        if inherited_git_work_tree is None:
            os.environ.pop("GIT_WORK_TREE", None)
        else:
            os.environ["GIT_WORK_TREE"] = inherited_git_work_tree
    audit.check(
        "git_environment_cannot_redirect_public_result_binding",
        published_blob is not None and hostile_blob == published_blob,
    )

    bindings = profile.get("private_page_bindings", [])
    binding_rows = [
        (
            row.get("sequence"),
            row.get("private_filename"),
            row.get("candidate_id"),
            row.get("headword"),
            row.get("witness"),
            row.get("sha256"),
            as_dict(row.get("dimensions")).get("width"),
            as_dict(row.get("dimensions")).get("height"),
        )
        for row in bindings
        if isinstance(row, dict)
    ]
    expected_binding_rows = [tuple(row[:-1]) for row in EXPECTED_BINDINGS]
    audit.check(
        "profile_ten_private_filename_hash_dimension_bindings_exact",
        binding_rows == expected_binding_rows,
    )
    audit.check(
        "profile_bindings_unique_safe_and_cross_bound_to_result",
        binding_rows == expected_binding_rows
        and len(binding_rows) == 10
        and len({row[0] for row in binding_rows}) == 10
        and len({row[1] for row in binding_rows}) == 10
        and len({row[5] for row in binding_rows}) == 10
        and all(
            isinstance(row[1], str)
            and Path(row[1]).name == row[1]
            and not Path(row[1]).is_absolute()
            and Path(row[1]).suffix.lower() == ".jpg"
            and ".." not in Path(row[1]).parts
            for row in binding_rows
        )
        and [
            (row[0], row[2], row[3], row[4], row[5], row[6], row[7])
            for row in binding_rows
        ]
        == [
            (row[0], row[1], row[2], row[3], row[4], row[5], row[6])
            for row in result_rows
        ],
    )
    audit.check(
        "latin_first_reader_and_reconciliation_order_exact",
        profile.get("reading_order") == EXPECTED_READING_ORDER,
    )
    audit.check(
        "opaque_reader_packet_locator_and_nonaccess_contract_exact",
        profile.get("locator_blinding") == EXPECTED_LOCATOR_BLINDING,
    )
    audit.check(
        "independent_blinded_reader_capture_contract_exact",
        profile.get("reader_protocol") == EXPECTED_READER_PROTOCOL,
    )
    audit.check(
        "codepoint_spacing_abbreviation_token_reconciliation_exact",
        profile.get("reconciliation") == EXPECTED_RECONCILIATION,
    )
    audit.check(
        "clm_is_post_latin_locator_control_only",
        profile.get("clm_control") == EXPECTED_CLM_CONTROL,
    )
    audit.check(
        "raw_submission_and_public_reconciliation_phase_seals_exact",
        profile.get("phase_seals") == EXPECTED_PHASE_SEALS,
    )
    audit.check(
        "immutable_local_full_page_display_policy_exact",
        profile.get("display_policy") == EXPECTED_DISPLAY_POLICY,
    )
    audit.check(
        "registration_access_and_forbidden_methods_exact",
        profile.get("access_state_at_registration")
        == {
            "network_requests": 0,
            "images_opened": 0,
            "source_text_read": False,
            "voynich_material_opened": False,
        }
        and profile.get("forbidden_methods") == EXPECTED_FORBIDDEN_METHODS,
    )
    audit.check(
        "future_result_schema_and_public_exclusions_exact",
        profile.get("result_contract") == EXPECTED_RESULT_CONTRACT,
    )

    docs_rel = (
        BASE_REL / "README.md",
        BASE_REL / "METHOD.md",
        BASE_REL / "PREREGISTRATION.md",
        BASE_REL / "artifacts/README.md",
    )
    docs: dict[Path, str] = {}
    for relative in docs_rel:
        path = ROOT / relative
        if is_safe_regular(path, BASE):
            try:
                docs[relative] = path.read_text(encoding="utf-8")
            except (OSError, UnicodeDecodeError):
                docs[relative] = ""
        else:
            docs[relative] = ""
    readme = " ".join(docs[BASE_REL / "README.md"].lower().split())
    method = " ".join(docs[BASE_REL / "METHOD.md"].lower().split())
    prereg = " ".join(docs[BASE_REL / "PREREGISTRATION.md"].lower().split())
    artifact_readme = " ".join(
        docs[BASE_REL / "artifacts/README.md"].lower().split()
    )
    combined_docs = "\n".join(docs.values()).lower()
    audit.check(
        "documentation_question_status_and_result_sha_exact",
        STATUS.lower() in readme
        and STATUS.lower() in method
        and STATUS.lower() in prereg
        and EXPECTED_QUESTION.lower() in method
        and GDT620_RESULT_SHA in method,
    )
    audit.check(
        "documentation_independent_fresh_rendering_and_blinding_exact",
        "two independent diplomatic readings" in readme
        and "different fresh local renderings" in readme
        and "before either can see the other's rendering or reading" in readme
        and "separate agent and rendering sessions with distinct session ids"
        in method
        and "root-mailbox storage, not the shared workspace" in method
        and "separate agent/rendering sessions with distinct session ids" in prereg
        and "root-mailbox storage, never the shared workspace" in prereg,
    )
    audit.check(
        "documentation_opaque_packet_and_source_nonaccess_exact",
        "exact packet fields are" in method
        and all(
            field in method
            for field in (
                "`opaque_candidate_id`",
                "`source_sha256`",
                "`session_id`",
                "`opaque_rendering_handle`",
            )
        )
        and "path-free" in method
        and "^r[ab][0-9]{2}-[0-9a-f]{16}$" in method
        and "no additional keys are allowed" in method
        and "reader attests the exact keys and packet hash" in method
        and all(
            term in method
            for term in (
                "headword",
                "witness/control identity",
                "url",
                "crosswalk",
                "expected rubric",
                "filename/path",
                "other submission",
            )
        )
        and "profile, repository, catalog, edition, network, other sources"
        in method
        and "opaque packet is canonical json with exactly" in prereg
        and "no extra key is allowed" in prereg,
    )
    audit.check(
        "documentation_raw_bundle_and_nonempty_checkpoint_schema_exact",
        "exactly one ordered dev01–dev05 bundle" in method
        and "bundle sha excludes `bundle_sha256`" in method
        and "page source hashes match the registered" in method
        and "checkpoint cannot be empty or status-only" in method
        and "both bundle hashes" in method
        and "all five reconciled rubric-plus-12-token readings" in method
        and "complete ledger" in method
        and "nonrecursive checkpoint hash" in method,
    )
    audit.check(
        "documentation_checkpoint_identity_and_adjudicator_nonaccess_exact",
        "final result binds its public commit and sha" in method
        and "byte-identically reuses bundle hashes, reconciled latin, and ledger"
        in method
        and "later latin change is forbidden" in method
        and "before checkpoint hashing the adjudicator attests" in method
        and "only the frozen bundles and five latin jpegs" in method
        and all(
            phrase in method
            for phrase in (
                "clm, network, repo/profile, catalog, edition, other-source, voynich, f84, and f84r access counts are zero",
            )
        ),
    )
    audit.check(
        "documentation_latin_first_then_clm_control_only_exact",
        "latin dev01–dev05 are read first" in method
        and "separate rubric/locator controls" in method
        and "clm may not repair, replace, normalize, or adjudicate latin" in method
        and "publicly committed before clm" in method
        and "public commit-and-hash verification, then clm" in prereg
        and "clm cannot alter latin" in prereg,
    )
    audit.check(
        "documentation_diplomatic_twelve_token_and_reconciliation_exact",
        "exactly the first twelve whitespace-delimited lexical tokens" in method
        and all(
            phrase in method
            for phrase in (
                "codepoints, spacing, abbreviation marks, and token boundaries",
                "both raw commitments then freeze before reconciliation",
                "reconciliation compare every codepoint, space, abbreviation mark, and token boundary",
                "explicit zero-difference row",
            )
        )
        and "tokens are maximal non-whitespace runs" in prereg
        and "explicit difference ledger" in prereg
        and "agreement_no_difference" in method
        and "no invented position" in method,
    )
    audit.check(
        "documentation_notation_version_unicode_and_hash_preimage_exact",
        "gdt621_diplomatic_v1" in method
        and "without unicode normalization" in method
        and all(
            tag in method
            for tag in ("<sign:description>", "<uncertain:x>", "<unreadable>")
        )
        and "hash preimage omits its own hash field" in method
        and "hash preimages omit their own hash field" in prereg,
    )
    audit.check(
        "documentation_local_display_no_ocr_or_derived_image_exact",
        all(
            phrase in method
            for phrase in (
                "all display is local",
                "immutable source jpeg exists and is never rewritten",
                "temporary in-memory renderer output may be scaled or resampled",
                "no derivative is persisted",
                "ocr",
                "automatic text recognition",
                "image classification",
            )
        )
        and "only temporary in-memory renderer output may resample for display"
        in prereg
        and "no derivative persists" in prereg
        and "no jpeg, rendering, crop, ocr output" in artifact_readme,
    )
    audit.check(
        "documentation_access_audit_order_values_and_clm_time_exact",
        "sole canonical access-audit schema" in prereg
        and "exactly ten latin view events" in method
        and "five later clm events" in method
        and "target/voynich/f84/f84r access counts zero" in method
        and "checkpoint_committed_utc" in method
        and "opened_utc` must be strictly later" in method
        and "exactly ten ordered latin and five later clm events" in prereg
        and "must open strictly afterward" in prereg,
    )
    audit.check(
        "documentation_registration_boundary_seals_and_claim_ceiling_exact",
        "registration opens no image and performs no network request" in readme
        and "registration performs zero network requests and opens zero images"
        in prereg
        and all(term in combined_docs for term in ("voynich", "f84", "f84r"))
        and "never a voynich sign, word, language, plaintext, plant identification, operation, or meaning"
        in method
        and "no jpeg" in artifact_readme
        and "source transcription" in artifact_readme
        and "private directory" in artifact_readme,
    )
    audit.check(
        "documentation_distinguishes_registration_and_result_publication_commits",
        GDT620_REGISTRATION_COMMIT in method
        and GDT620_RESULT_PUBLICATION_COMMIT in method
        and "acquisition code was registered publicly" in method
        and "artifact was published separately" in method,
    )

    actual_files, actual_directories, special = collect_tree()
    prewrite_files = EXPECTED_TREE_FILES - {
        "artifacts/REGISTERED_VALIDATION.json"
    }
    audit.check(
        "registration_tree_exact_and_symlink_free",
        actual_directories == EXPECTED_TREE_DIRECTORIES
        and special == []
        and (
            actual_files == EXPECTED_TREE_FILES
            or (args.write and actual_files == prewrite_files)
        ),
    )
    audit.check(
        "no_image_document_private_runtime_or_special_file_retained",
        not any(
            Path(relative).suffix.lower() in IMAGE_OR_DOCUMENT_SUFFIXES
            for relative in actual_files
        )
        and not any(private_path_name(relative) for relative in actual_files),
    )
    working_privacy: list[str] = []
    for relative in sorted(actual_files):
        if Path(relative).suffix.lower() in IMAGE_OR_DOCUMENT_SUFFIXES:
            continue
        path = BASE / relative
        if is_safe_regular(path, BASE):
            working_privacy.extend(
                privacy_findings(path.read_bytes(), f"working:{relative}")
            )
        else:
            working_privacy.append(f"working:unsafe:{relative}")
    if result_safe:
        working_privacy.extend(
            privacy_findings(result_path.read_bytes(), f"input:{GDT620_RESULT_REL}")
        )
    else:
        working_privacy.append("input:gdt620-result-unsafe")
    audit.check("working_tree_and_input_privacy_patterns_clean", working_privacy == [])
    audit.check("exact_staged_tree_privacy_patterns_clean", staged_privacy_findings() == [])

    audit.check(
        "manifest_canonical_identity_status_and_seals_exact",
        is_safe_regular(manifest_path, BASE)
        and manifest_path.read_bytes() == canonical_bytes(manifest)
        and manifest.get("schema_version") == 1
        and manifest.get("experiment_id") == "GDT621"
        and manifest.get("slug") == "manual_source_double_reading"
        and manifest.get("title") == "Manual source double reading"
        and manifest.get("created") == "2026-08-29"
        and manifest.get("updated") == "2026-08-29"
        and manifest.get("status") == STATUS
        and manifest.get("sealed_data")
        == {"f84": "FORBIDDEN", "f84r": "FORBIDDEN"},
    )
    audit.check(
        "manifest_question_claim_ceiling_and_artifact_policy_exact",
        manifest.get("question") == EXPECTED_QUESTION
        and manifest.get("claim_ceiling") == EXPECTED_MANIFEST_CLAIM_CEILING
        and manifest.get("artifact_policy") == EXPECTED_ARTIFACT_POLICY,
    )
    audit.check(
        "manifest_dependency_commands_and_validation_binding_exact",
        manifest.get("dependencies") == ["GDT620"]
        and manifest.get("commands")
        == {
            "run": f"python3 {RUN_REL} --check",
            "validate": f"python3 {VALIDATOR_REL} --check",
        }
        and manifest.get("validation")
        == {"artifact": str(VALIDATION_REL), "status": "PASS"},
    )
    raw_inputs = manifest.get("inputs", [])
    raw_outputs = manifest.get("outputs", [])
    inputs = raw_inputs if isinstance(raw_inputs, list) else []
    outputs = raw_outputs if isinstance(raw_outputs, list) else []
    audit.check(
        "manifest_input_and_output_path_sets_exact",
        isinstance(raw_inputs, list)
        and isinstance(raw_outputs, list)
        and len(inputs) == len(EXPECTED_INPUTS)
        and len(outputs) == len(EXPECTED_OUTPUTS)
        and {
            row.get("path")
            for row in inputs
            if isinstance(row, dict) and isinstance(row.get("path"), str)
        }
        == EXPECTED_INPUTS
        and {
            row.get("path")
            for row in outputs
            if isinstance(row, dict) and isinstance(row.get("path"), str)
        }
        == EXPECTED_OUTPUTS,
    )
    all_rows = inputs + outputs
    validation_rows = [
        row
        for row in outputs
        if isinstance(row, dict) and row.get("path") == str(VALIDATION_REL)
    ]
    nonvalidation_rows = [
        row
        for row in all_rows
        if isinstance(row, dict) and row.get("path") != str(VALIDATION_REL)
    ]
    audit.check(
        "manifest_rows_roles_and_nonvalidation_hashes_exact",
        len(all_rows) == len(EXPECTED_INPUTS) + len(EXPECTED_OUTPUTS)
        and all(
            isinstance(row, dict)
            and set(row) == {"path", "role", "sha256"}
            and isinstance(row.get("role"), str)
            and bool(row["role"].strip())
            for row in all_rows
        )
        and len(validation_rows) == 1
        and all(
            isinstance(row.get("sha256"), str)
            and isinstance(row.get("path"), str)
            and HEX64.fullmatch(row["sha256"]) is not None
            and is_safe_regular(ROOT / row["path"], ROOT)
            and digest(ROOT / row["path"]) == row["sha256"]
            for row in nonvalidation_rows
        )
        and len(inputs) == 1
        and isinstance(inputs[0], dict)
        and inputs[0].get("sha256") == GDT620_RESULT_SHA,
    )

    registered_payload = audit.payload()
    if args.print_artifact_template:
        print(json.dumps(registered_payload, indent=2, sort_keys=True, ensure_ascii=False))
        return 0 if audit.passed else 1
    if args.write:
        if not audit.passed:
            print(json.dumps(registered_payload, indent=2, sort_keys=True, ensure_ascii=False))
            return 1
        validation_path.write_bytes(canonical_bytes(registered_payload))
        print(f"WROTE {VALIDATION_REL} {digest(validation_path)}")
        return 0

    audit.check(
        "validation_artifact_matches_registered_payload",
        is_safe_regular(validation_path, BASE)
        and validation_path.read_bytes() == canonical_bytes(registered_payload),
    )
    audit.check(
        "manifest_validation_artifact_hash_exact",
        len(validation_rows) == 1
        and is_safe_regular(validation_path, BASE)
        and HEX64.fullmatch(str(validation_rows[0].get("sha256", ""))) is not None
        and digest(validation_path) == validation_rows[0].get("sha256"),
    )
    payload = audit.payload()
    print(json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False))
    return 0 if audit.passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
