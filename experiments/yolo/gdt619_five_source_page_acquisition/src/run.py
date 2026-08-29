#!/usr/bin/env python3
"""Build or verify GDT619's offline source-image request registration."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
BASE = ROOT / "experiments/yolo/gdt619_five_source_page_acquisition"
PROFILE_PATH = BASE / "artifacts/REGISTERED_REQUEST_PROFILE.json"

GDT618_PLAN_PATH = (
    "experiments/yolo/gdt618_four_witness_herbal_concordance/"
    "artifacts/REGISTERED_SOURCE_PLAN.json"
)
GDT618_PLAN_SHA256 = (
    "2df86904b38212ba37ea3d0dcb0def241600e6f900c94bcb44d87ecd9f969502"
)
GDT618_PUBLIC_COMMIT = "c0266e78"

BSB_MANIFEST_URL = (
    "https://api.digitale-sammlungen.de/iiif/presentation/v3/"
    "bsb00107549/manifest"
)
BSB_SERVICE_ID_REGEX = (
    r"^https://api\.digitale-sammlungen\.de/iiif/image/v3/"
    r"bsb00107549_[0-9]{5}$"
)
def build_profile() -> dict:
    candidates = [
        {
            "candidate_id": "DEV01",
            "developmental_headword": "Balsamus",
            "lat6823": {
                "canvas_id": "https://gallica.bnf.fr/iiif/ark:/12148/btv1b6000517p/canvas/f58",
                "canvas_label": "25v",
                "canvas_size": {"height": 4581, "width": 3302},
                "folio": "f25v",
                "image_api_version": "1.1",
                "image_service_id": "https://gallica.bnf.fr/iiif/ark:/12148/btv1b6000517p/f58",
                "native_image_url": "https://gallica.bnf.fr/iiif/ark:/12148/btv1b6000517p/f58/full/full/0/native.jpg",
            },
            "clm28531": {
                "body_height": 2547,
                "body_id": "https://api.digitale-sammlungen.de/iiif/image/v3/bsb00107549_00026/full/max/0/default.jpg",
                "body_type": "Image",
                "body_width": 1707,
                "canvas_ordinal": 26,
                "folio": "f10v",
                "full_page_url": "https://api.digitale-sammlungen.de/iiif/image/v3/bsb00107549_00026/full/max/0/default.jpg",
                "image_service_id": "https://api.digitale-sammlungen.de/iiif/image/v3/bsb00107549_00026",
                "image_service_profile": "level2",
                "image_service_type": "ImageService3",
                "main_folio_ordinal": 20,
                "scan_id": "bsb00107549_00026",
            },
        },
        {
            "candidate_id": "DEV02",
            "developmental_headword": "Cerfolium",
            "lat6823": {
                "canvas_id": "https://gallica.bnf.fr/iiif/ark:/12148/btv1b6000517p/canvas/f96",
                "canvas_label": "44v",
                "canvas_size": {"height": 4553, "width": 3451},
                "folio": "f44v",
                "image_api_version": "1.1",
                "image_service_id": "https://gallica.bnf.fr/iiif/ark:/12148/btv1b6000517p/f96",
                "native_image_url": "https://gallica.bnf.fr/iiif/ark:/12148/btv1b6000517p/f96/full/full/0/native.jpg",
            },
            "clm28531": {
                "body_height": 2563,
                "body_id": "https://api.digitale-sammlungen.de/iiif/image/v3/bsb00107549_00076/full/max/0/default.jpg",
                "body_type": "Image",
                "body_width": 1707,
                "canvas_ordinal": 76,
                "folio": "f35v",
                "full_page_url": "https://api.digitale-sammlungen.de/iiif/image/v3/bsb00107549_00076/full/max/0/default.jpg",
                "image_service_id": "https://api.digitale-sammlungen.de/iiif/image/v3/bsb00107549_00076",
                "image_service_profile": "level2",
                "image_service_type": "ImageService3",
                "main_folio_ordinal": 70,
                "scan_id": "bsb00107549_00076",
            },
        },
        {
            "candidate_id": "DEV03",
            "developmental_headword": "Liquiritia",
            "lat6823": {
                "canvas_id": "https://gallica.bnf.fr/iiif/ark:/12148/btv1b6000517p/canvas/f178",
                "canvas_label": "85v",
                "canvas_size": {"height": 4557, "width": 3284},
                "folio": "f85v",
                "image_api_version": "1.1",
                "image_service_id": "https://gallica.bnf.fr/iiif/ark:/12148/btv1b6000517p/f178",
                "native_image_url": "https://gallica.bnf.fr/iiif/ark:/12148/btv1b6000517p/f178/full/full/0/native.jpg",
            },
            "clm28531": {
                "body_height": 2624,
                "body_id": "https://api.digitale-sammlungen.de/iiif/image/v3/bsb00107549_00165/full/max/0/default.jpg",
                "body_type": "Image",
                "body_width": 1707,
                "canvas_ordinal": 165,
                "folio": "f80r",
                "full_page_url": "https://api.digitale-sammlungen.de/iiif/image/v3/bsb00107549_00165/full/max/0/default.jpg",
                "image_service_id": "https://api.digitale-sammlungen.de/iiif/image/v3/bsb00107549_00165",
                "image_service_profile": "level2",
                "image_service_type": "ImageService3",
                "main_folio_ordinal": 159,
                "scan_id": "bsb00107549_00165",
            },
        },
        {
            "candidate_id": "DEV04",
            "developmental_headword": "Cucurbita",
            "lat6823": {
                "canvas_id": "https://gallica.bnf.fr/iiif/ark:/12148/btv1b6000517p/canvas/f91",
                "canvas_label": "42r",
                "canvas_size": {"height": 4388, "width": 3333},
                "folio": "f42r",
                "image_api_version": "1.1",
                "image_service_id": "https://gallica.bnf.fr/iiif/ark:/12148/btv1b6000517p/f91",
                "native_image_url": "https://gallica.bnf.fr/iiif/ark:/12148/btv1b6000517p/f91/full/full/0/native.jpg",
            },
            "clm28531": {
                "body_height": 2576,
                "body_id": "https://api.digitale-sammlungen.de/iiif/image/v3/bsb00107549_00097/full/max/0/default.jpg",
                "body_type": "Image",
                "body_width": 1707,
                "canvas_ordinal": 97,
                "folio": "f46r",
                "full_page_url": "https://api.digitale-sammlungen.de/iiif/image/v3/bsb00107549_00097/full/max/0/default.jpg",
                "image_service_id": "https://api.digitale-sammlungen.de/iiif/image/v3/bsb00107549_00097",
                "image_service_profile": "level2",
                "image_service_type": "ImageService3",
                "main_folio_ordinal": 91,
                "scan_id": "bsb00107549_00097",
            },
        },
        {
            "candidate_id": "DEV05",
            "developmental_headword": "Diptamus",
            "lat6823": {
                "canvas_id": "https://gallica.bnf.fr/iiif/ark:/12148/btv1b6000517p/canvas/f122",
                "canvas_label": "57v",
                "canvas_size": {"height": 4574, "width": 3346},
                "folio": "f57v",
                "image_api_version": "1.1",
                "image_service_id": "https://gallica.bnf.fr/iiif/ark:/12148/btv1b6000517p/f122",
                "native_image_url": "https://gallica.bnf.fr/iiif/ark:/12148/btv1b6000517p/f122/full/full/0/native.jpg",
            },
            "clm28531": {
                "body_height": 2587,
                "body_id": "https://api.digitale-sammlungen.de/iiif/image/v3/bsb00107549_00102/full/max/0/default.jpg",
                "body_type": "Image",
                "body_width": 1707,
                "canvas_ordinal": 102,
                "folio": "f48v",
                "full_page_url": "https://api.digitale-sammlungen.de/iiif/image/v3/bsb00107549_00102/full/max/0/default.jpg",
                "image_service_id": "https://api.digitale-sammlungen.de/iiif/image/v3/bsb00107549_00102",
                "image_service_profile": "level2",
                "image_service_type": "ImageService3",
                "main_folio_ordinal": 96,
                "scan_id": "bsb00107549_00102",
            },
        },
    ]

    return {
        "access_audit": {
            "developmental_metadata_responses_bound": 4,
            "image_bytes_received": 0,
            "registration_builder_network_requests": 0,
            "source_full_image_requests": 0,
            "source_page_images_opened": 0,
            "source_thumbnail_requests": 0,
            "target_requests": 0,
            "voynich_material_opened": 0,
        },
        "candidates": candidates,
        "claim_ceiling": (
            "REQUEST_PROFILE_ONLY__NO_SOURCE_LOCATOR_VERIFIED__NO_TRANSCRIPTION__"
            "NO_VOYNICH_VALUE_OR_MEANING"
        ),
        "decision": "PROFILE_REGISTERED__NO_IMAGE_REQUEST_EXECUTED",
        "dependency": {
            "gdt618_plan_path": GDT618_PLAN_PATH,
            "gdt618_plan_sha256": GDT618_PLAN_SHA256,
            "gdt618_public_commit": GDT618_PUBLIC_COMMIT,
        },
        "experiment_id": "GDT619",
        "metadata_evidence_bindings": [
            {
                "access_status": "DEVELOPMENTALLY_FETCHED_METADATA_ONLY__NO_IMAGE",
                "bytes": 261778,
                "role": "CLM28531_OFFICIAL_IIIF_V3_MANIFEST",
                "sha256": "6f25dbd8a0baff9a681e8c486a9a883ed704671c155a7cfd81775e9f2a235fd3",
                "url": "https://api.digitale-sammlungen.de/iiif/presentation/v3/bsb00107549/manifest",
            },
            {
                "access_status": "DEVELOPMENTALLY_FETCHED_METADATA_ONLY__NO_IMAGE",
                "bytes": 598251,
                "role": "COD_ICON_222_OFFICIAL_IIIF_V3_MANIFEST__SCAN_CONVENTION_CONTROL",
                "sha256": "05b7042359e9b9e1e270c325531e42f1e4d5fdad82014c1930af492a91e408c1",
                "url": "https://api.digitale-sammlungen.de/iiif/presentation/v3/bsb00020956/manifest",
            },
            {
                "access_status": "DEVELOPMENTALLY_FETCHED_METADATA_ONLY__NO_IMAGE",
                "bytes": 573418,
                "role": "COD_ICON_222_OFFICIAL_METS__SCAN_CONVENTION_CONTROL",
                "sha256": "280b9bd2e715f2bf977a705695110802c2aa1763d8051846d797e8b23a92ccbc",
                "url": "https://daten.digitale-sammlungen.de/~db/mets/bsb00020956_mets.xml",
            },
            {
                "access_status": "DEVELOPMENTALLY_FETCHED_METADATA_ONLY__NO_IMAGE",
                "bytes": 395209,
                "role": "CLM4623_OFFICIAL_IIIF_V3_MANIFEST__MICROFORM_CONVENTION_CONTROL",
                "sha256": "90dda0fc3b21ceec27ecf849fa74a328f2ce04eaff6fbb7022aecf39a50b4c77",
                "url": "https://api.digitale-sammlungen.de/iiif/presentation/v3/bsb00112053/manifest",
            },
        ],
        "forbidden_access": [
            "F84",
            "F84R",
            "VOYNICH_PAGE",
            "VOYNICH_TRANSCRIPTION",
            "VOYNICH_TARGET_FEATURE",
            "OCR",
            "AUTOMATIC_IMAGE_CLASSIFICATION",
            "EMBEDDING_RETRIEVAL",
            "GENERATED_CAPTION",
            "NETWORK_CROP",
            "UNREGISTERED_IMAGE_URL",
        ],
        "request_governance": {
            "accept_encoding": "identity",
            "bsb_minimum_seconds_between_completed_request_and_next_start": 4,
            "concurrency": 1,
            "follow_redirects": False,
            "http_method": "GET",
            "information_requests": False,
            "manifest_accept": "application/ld+json, application/json;q=0.9",
            "maximum_bsb_requests_direct_branch": 7,
            "maximum_bsb_requests_fallback_branch": 9,
            "maximum_gallica_requests": 5,
            "network_crops": False,
            "request_intent_must_be_fsynced_before_network": True,
            "request_journal_preserves_failures": True,
            "retries": 0,
            "stage_a_must_finish_before_stage_b": True,
            "stage_b_requires_public_stage1_resolution": True,
            "thumbnail_and_image_accept": "image/jpeg",
            "unregistered_head_requests": False,
            "unregistered_info_json_requests": False,
            "user_agent": "VManus-GDT619-source-image-acquisition/1.0",
        },
        "rights_policy": {
            "bnf_attribution": "Bibliothèque nationale de France",
            "bnf_license_url": "https://gallica.bnf.fr/html/und/conditions-dutilisation-des-contenus-de-gallica",
            "bsb_expected_rights": "https://creativecommons.org/publicdomain/mark/1.0/",
            "bsb_provider_must_include_logo": True,
            "bsb_required_statement_must_be_multilingual": True,
            "bsb_top_level_json_pointers": ["/rights", "/requiredStatement", "/provider"],
            "bsb_missing_license_action": "NO_IMAGE_OR_LOCAL_CROP_REDISTRIBUTION",
            "iiif_availability_is_redistribution_permission": False,
        },
        "schema_version": 1,
        "stage_a": {
            "acquisition_state_machine": {
                "commands": {
                    "acquire_fallback": "python3 experiments/yolo/gdt619_five_source_page_acquisition/src/acquire_stage_a.py acquire-fallback --private-dir ABSOLUTE_PRIVATE_DIR",
                    "acquire_primary": "python3 experiments/yolo/gdt619_five_source_page_acquisition/src/acquire_stage_a.py acquire-primary --private-dir ABSOLUTE_PRIVATE_DIR",
                    "record_fallback": "python3 experiments/yolo/gdt619_five_source_page_acquisition/src/acquire_stage_a.py record-fallback --private-dir ABSOLUTE_PRIVATE_DIR --scan25-observation ENUM --scan27-observation ENUM",
                    "record_primary": "python3 experiments/yolo/gdt619_five_source_page_acquisition/src/acquire_stage_a.py record-primary --private-dir ABSOLUTE_PRIVATE_DIR --observation ENUM",
                    "self_test": "python3 experiments/yolo/gdt619_five_source_page_acquisition/src/acquire_stage_a.py self-test",
                },
                "exact_initial_allowlist": [
                    "https://api.digitale-sammlungen.de/iiif/presentation/v3/bsb00107549/manifest",
                    "https://api.digitale-sammlungen.de/iiif/image/v3/bsb00107549_00026/full/1200,/0/default.jpg",
                    "https://api.digitale-sammlungen.de/iiif/image/v3/bsb00107549_00025/full/1200,/0/default.jpg",
                    "https://api.digitale-sammlungen.de/iiif/image/v3/bsb00107549_00027/full/1200,/0/default.jpg",
                ],
                "failure_bytes_policy": "PRESERVE_ONLY_BODY_BYTES_FULLY_OBTAINED_WITHIN_CAP_THEN_REJECTED_BY_DECODE_OR_SEMANTIC_VALIDATION__NO_CLAIM_FOR_HTTP_REDIRECT_WRONG_MEDIA_OR_OVERCAP",
                "exclusive_lock_filename": "STAGE_A_EXCLUSIVE.lock",
                "exclusive_lock_mode": "ADVISORY_FLOCK_NONBLOCKING__KERNEL_RELEASES_ON_PROCESS_DEATH",
                "jpeg_decoder_dependency": {"package": "Pillow", "version": "10.2.0", "requirements_path": "experiments/yolo/gdt619_five_source_page_acquisition/requirements.txt", "decode": "Image.verify_then_reopen_and_load"},
                "directory_durability": "FSYNC_PARENT_AFTER_OWNER_OR_LOCK_OR_JOURNAL_CREATION_AND_AFTER_EVERY_STATE_REPLACE",
                "new_private_directory_durability": "FSYNC_NEW_DIRECTORY_PARENT_ENTRY_IMMEDIATELY_AFTER_MKDIR",
                "exactly_once_policy": "FSYNC_IN_FLIGHT_BEFORE_GET__ANY_UNRESOLVED_ATTEMPT_PERMANENTLY_REFUSES_RESEND",
                "ownership_marker": {"filename": "GDT619_PRIVATE_OWNER.json", "fresh_or_exact_marker_required": True, "atomic_create_exclusive": True},
                "pre_send_duplicate_rule": "REFUSE_URL_IF_ANY_PRIOR_REQUEST_INTENT_OR_REQUEST_SUCCESS_EXISTS",
                "journal_filename": "REQUEST_JOURNAL.jsonl",
                "network_on_import": False,
                "output_directory_constraints": {
                    "absolute_path_required": True,
                    "group_or_other_permissions_allowed": False,
                    "outside_repository_required": True,
                    "symlink_allowed": False,
                    "symlinked_path_components_allowed": False,
                },
                "source_path": "experiments/yolo/gdt619_five_source_page_acquisition/src/acquire_stage_a.py",
                "request_intent_required_fields": [
                    "defined_delay_seconds",
                    "event",
                    "headers",
                    "intent_written_utc",
                    "method",
                    "resource_class",
                    "seconds_since_previous_bsb_completion",
                    "sequence",
                    "url",
                ],
                "request_success_required_fields": [
                    "defined_delay_seconds",
                    "event",
                    "intent_written_utc",
                    "observed_bytes",
                    "raw_sha256",
                    "request_started_utc",
                    "resource_class",
                    "response_completed_utc",
                    "response_headers",
                    "seconds_since_previous_bsb_completion",
                    "sequence",
                    "url",
                    "validation",
                ],
                "state_transitions": [
                    "ANY_REQUEST_INTENT->IN_FLIGHT_BEFORE_GET",
                    "ANY_UNRESOLVED_IN_FLIGHT->PERMANENT_RESEND_REFUSAL",
                    "MANIFEST_SUCCESS->MANIFEST_ACQUIRED__PRIMARY_THUMBNAIL_PENDING",
                    "SCAN26_SUCCESS->PRIMARY_ACQUIRED_AWAITING_OBSERVATION",
                    "SCAN25_SUCCESS->SCAN25_ACQUIRED__SCAN27_PENDING",
                    "SCAN27_SUCCESS->FALLBACK_ACQUIRED_AWAITING_OBSERVATIONS",
                    "NEW->PRIMARY_ACQUIRED_AWAITING_OBSERVATION",
                    "PRIMARY_ACQUIRED_AWAITING_OBSERVATION+VISIBLE->STAGE1_RESOLVED_PRIVATE_DRAFT",
                    "PRIMARY_ACQUIRED_AWAITING_OBSERVATION+VISIBLY_ABSENT->PRIMARY_VISIBLY_ABSENT__FALLBACK_AUTHORIZED",
                    "PRIMARY_ACQUIRED_AWAITING_OBSERVATION+AMBIGUOUS_OR_UNREADABLE->STOPPED_PRIMARY_AMBIGUOUS_OR_UNREADABLE",
                    "PRIMARY_VISIBLY_ABSENT__FALLBACK_AUTHORIZED->FALLBACK_ACQUIRED_AWAITING_OBSERVATIONS",
                    "FALLBACK_ACQUIRED_AWAITING_OBSERVATIONS+EXACTLY_ONE_VISIBLE->STAGE1_RESOLVED_PRIVATE_DRAFT",
                    "ANY_TRANSPORT_DECODE_SEMANTIC_FAILURE->STOPPED_FAILURE",
                ],
            },
            "bsb_manifest": {
                "expected_canvas_count": 316,
                "expected_object_id": "bsb00107549",
                "expected_presentation_api_version": 3,
                "expected_response_bytes": 261778,
                "expected_response_sha256": "6f25dbd8a0baff9a681e8c486a9a883ed704671c155a7cfd81775e9f2a235fd3",
                "maximum_response_bytes": 5000000,
                "request_order": 1,
                "url": BSB_MANIFEST_URL,
            },
            "canvas_service_extraction": {
                "canvas_array_json_pointer": "/items",
                "canvas_id_required": True,
                "painting_annotation_count": 1,
                "painting_annotation_page_count": 1,
                "resource_format": "image/jpeg",
                "service_profile": "level2",
                "service_id_regex": BSB_SERVICE_ID_REGEX,
                "service_json_pointer_from_canvas": "/items/0/items/0/body/service/0/id",
                "service_type": "ImageService3",
            },
            "metadata_mapping": {
                "base_canvas_ordinals": {
                    "f10v": 26,
                    "f35v": 76,
                    "f80r": 165,
                    "f46r": 97,
                    "f48v": 102,
                },
                "binding_order_statement": "WAGNER_FOLIATION_ADDED_AFTER_DISORDER__USE_PHYSICAL_BOUND_ORDER",
                "canvas_count": 316,
                "formula_recto": "2*n+5",
                "formula_verso": "2*n+6",
                "total_scan_model": "II_PLUS_154_LEAVES_PLUS_FOUR_COVER_OR_MIRROR_SCANS",
                "supporting_metadata_roles": [
                    "CLM28531_OFFICIAL_IIIF_V3_MANIFEST",
                    "COD_ICON_222_OFFICIAL_IIIF_V3_MANIFEST__SCAN_CONVENTION_CONTROL",
                    "COD_ICON_222_OFFICIAL_METS__SCAN_CONVENTION_CONTROL",
                    "CLM4623_OFFICIAL_IIIF_V3_MANIFEST__MICROFORM_CONVENTION_CONTROL",
                ],
            },
            "rubric_calibration": {
                "allowed_observation_enum": [
                    "VISIBLE",
                    "VISIBLY_ABSENT",
                    "AMBIGUOUS_OR_UNREADABLE",
                ],
                "fallback_global_deltas": [-1, 1],
                "fallback_rule": (
                    "ONLY_PRIMARY_VISIBLY_ABSENT_AUTHORIZES_SCAN25_THEN_SCAN27__"
                    "EXACTLY_ONE_VISIBLE_AND_ONE_VISIBLY_ABSENT_SELECTS_ONE_GLOBAL_"
                    "DELTA__AMBIGUOUS_OR_TRANSPORT_OR_DECODE_FAILURE_STOPS"
                ),
                "fallback_thumbnail_urls": [
                    "https://api.digitale-sammlungen.de/iiif/image/v3/bsb00107549_00025/full/1200,/0/default.jpg",
                    "https://api.digitale-sammlungen.de/iiif/image/v3/bsb00107549_00027/full/1200,/0/default.jpg",
                ],
                "headword": "Balsamus",
                "maximum_thumbnail_bytes": 5000000,
                "primary_canvas_ordinal": 26,
                "primary_folio": "f10v",
                "primary_thumbnail_url": "https://api.digitale-sammlungen.de/iiif/image/v3/bsb00107549_00026/full/1200,/0/default.jpg",
                "selection_method": "MANUALLY_VISIBLE_RUBRIC_ONLY__NO_IMAGE_SIMILARITY__NO_OCR",
                "thumbnail_request_suffix": "/full/1200,/0/default.jpg",
                "transport_or_decode_failure_action": "STOP_WITHOUT_FALLBACK",
            },
            "resolution_fail_stops": [
                "MANIFEST_REDIRECT_OR_NON_200",
                "MANIFEST_BYTES_OR_SHA256_CHANGED",
                "MANIFEST_NOT_EXACTLY_316_CANVASES",
                "UNEXPECTED_IIIF_PRESENTATION_OR_IMAGE_API_VERSION",
                "UNEXPECTED_BSB_OBJECT_OR_SERVICE_ID",
                "PRIMARY_AMBIGUOUS_OR_UNREADABLE",
                "PRIMARY_TRANSPORT_OR_DECODE_FAILURE",
                "FALLBACK_NOT_EXACTLY_ONE_VISIBLE_AND_ONE_VISIBLY_ABSENT",
                "FALLBACK_TRANSPORT_OR_DECODE_FAILURE",
                "ANY_SELECTION_USES_BOTANICAL_IMAGE_SIMILARITY",
                "ANY_OCR_OR_AUTOMATIC_IMAGE_CLASSIFICATION",
            ],
            "rubric_observation_policy": {
                "automatic_methods": False,
                "botanical_image_similarity": False,
                "manual_visible_rubric_only": True,
            },
            "stage1_resolution_contract": {
                "artifact_name": "STAGE1_RESOLUTION.json",
                "must_be_published_before_stage_b": True,
                "nested_types": {
                    "calibration": {
                        "branch": "str",
                        "observations": "list[object]",
                        "selected_global_delta": "int",
                    },
                    "manifest": {
                        "bytes": "int",
                        "sha256": "hex64",
                        "url": "https_url",
                    },
                    "request_evidence": {
                        "failure_count": "int",
                        "intent_count": "int",
                        "journal_sha256": "hex64",
                        "minimum_bsb_spacing_seconds": "number",
                        "success_count": "int",
                        "thumbnails": "list[one_direct_or_three_fallback_public_request_evidence_objects]",
                    },
                    "rights": {
                        "provider": "list[object]",
                        "requiredStatement": "object",
                        "rights": "https_url",
                    },
                    "schema_version": "int=1",
                    "selected_pages": "list[exactly_5_selected_page_objects]",
                    "status": "str=STAGE1_RESOLVED__STAGE_B_URLS_PUBLICLY_UNBOUND",
                },
                "selected_page_object_types": {
                    "body": "object{id:str,type:Image,format:image/jpeg,width:int,height:int,service:object}",
                    "candidate_id": "str",
                    "canvas_id": "str",
                    "canvas_ordinal": "int",
                    "folio": "str",
                    "stage_b_url": "https_url_ending_/full/max/0/default.jpg",
                },
                "stage_b_url_suffix": "/full/max/0/default.jpg",
                "status_before_publication": "STAGE_B_FORBIDDEN",
            },
        },
        "stage_b": {
            "access_order": [
                "BSB_CLM28531_DEV01",
                "BSB_CLM28531_DEV02",
                "BSB_CLM28531_DEV03",
                "BSB_CLM28531_DEV04",
                "BSB_CLM28531_DEV05",
                "BNF_LAT6823_DEV01",
                "BNF_LAT6823_DEV02",
                "BNF_LAT6823_DEV03",
                "BNF_LAT6823_DEV04",
                "BNF_LAT6823_DEV05",
            ],
            "bsb_full_pages": {
                "count": 5,
                "image_api_version": "3",
                "request_region": "full",
                "request_rotation": "0",
                "request_size": "max",
                "request_suffix": "/full/max/0/default.jpg",
                "request_quality_format": "default.jpg",
                "url_source": "PUBLIC_STAGE1_RESOLUTION_FIVE_LITERAL_BSB_STAGE_B_URLS",
            },
            "gallica_native_pages": {
                "count": 5,
                "image_api_version": "1.1",
                "manifest_sha256": "f22ea8cf697c5598f914bd92e101dd2da62a60df59561d67ef7384d5f5de7187",
                "request_region": "full",
                "request_rotation": "0",
                "request_size": "full",
                "request_quality_format": "native.jpg",
                "urls": [row["lat6823"]["native_image_url"] for row in candidates],
            },
            "local_crop_policy": {
                "authoritative_network_source_remains_full_page": True,
                "local_reading_crops_allowed_only_after_source_hashing": True,
                "network_crop_requests": 0,
                "required_provenance_fields": [
                    "SOURCE_JPEG_SHA256",
                    "SOURCE_WIDTH",
                    "SOURCE_HEIGHT",
                    "ZERO_BASED_X",
                    "ZERO_BASED_Y",
                    "WIDTH",
                    "HEIGHT",
                    "CROP_SHA256",
                ],
            },
            "request_log_required_fields": [
                "SEQUENCE",
                "STAGE",
                "CANDIDATE_ID",
                "RESOURCE_CLASS",
                "REQUEST_URL",
                "REQUEST_URL_SHA256",
                "STATUS",
                "RESPONSE_URL",
                "REDIRECT_ATTEMPTS",
                "CONTENT_TYPE",
                "CONTENT_LENGTH_HEADER",
                "OBSERVED_BYTES",
                "RAW_SHA256",
                "DECODED_WIDTH",
                "DECODED_HEIGHT",
                "ETAG",
                "LAST_MODIFIED",
                "INTENT_WRITTEN_UTC",
                "REQUEST_STARTED_UTC",
                "RESPONSE_COMPLETED_UTC",
                "SECONDS_SINCE_PREVIOUS_BSB_COMPLETION",
                "DEFINED_DELAY_SECONDS",
            ],
            "result_outcomes": [
                "TEN_SOURCE_PAGES_ACQUIRED__TARGET_UNOPENED",
                "SOURCE_PAGE_ACQUISITION_FAILURE",
                "SOURCE_LOCATOR_FAILURE",
            ],
        },
    }


def canonical_bytes(value: dict) -> bytes:
    return (
        json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False) + "\n"
    ).encode("utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--check", action="store_true", help="verify committed profile")
    mode.add_argument("--print-profile", action="store_true")
    mode.add_argument("--print-sha256", action="store_true")
    mode.add_argument("--write-profile", action="store_true")
    args = parser.parse_args()

    expected = canonical_bytes(build_profile())
    if args.print_profile:
        print(expected.decode("utf-8"), end="")
        return 0
    if args.print_sha256:
        print(hashlib.sha256(expected).hexdigest())
        return 0
    if args.write_profile:
        PROFILE_PATH.write_bytes(expected)
        print(f"WROTE {PROFILE_PATH.relative_to(ROOT)} {hashlib.sha256(expected).hexdigest()}")
        return 0
    if not PROFILE_PATH.is_file():
        print(f"FAIL missing {PROFILE_PATH.relative_to(ROOT)}")
        return 1
    actual = PROFILE_PATH.read_bytes()
    if actual != expected:
        print("FAIL registered request profile differs from deterministic builder")
        return 1
    print(f"PASS {PROFILE_PATH.relative_to(ROOT)} {hashlib.sha256(actual).hexdigest()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
