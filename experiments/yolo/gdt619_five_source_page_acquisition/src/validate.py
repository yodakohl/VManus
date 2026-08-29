#!/usr/bin/env python3
"""Validate GDT619's request registration without network or image access."""

from __future__ import annotations

import argparse
import ast
import hashlib
import importlib.util
import json
import re
from pathlib import Path


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
BASE_REL = Path("experiments/yolo/gdt619_five_source_page_acquisition")
BASE = ROOT / BASE_REL
PROFILE_REL = BASE_REL / "artifacts/REGISTERED_REQUEST_PROFILE.json"
VALIDATION_REL = BASE_REL / "artifacts/REGISTERED_VALIDATION.json"
MANIFEST_REL = BASE_REL / "experiment.json"
ACQUIRE_REL = BASE_REL / "src/acquire_stage_a.py"
REQUIREMENTS_REL = BASE_REL / "requirements.txt"
GDT618_PLAN_REL = Path(
    "experiments/yolo/gdt618_four_witness_herbal_concordance/"
    "artifacts/REGISTERED_SOURCE_PLAN.json"
)
GDT618_PLAN_SHA256 = (
    "2df86904b38212ba37ea3d0dcb0def241600e6f900c94bcb44d87ecd9f969502"
)
HEX64 = re.compile(r"^[0-9a-f]{64}$")


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_bytes(value: dict) -> bytes:
    return (
        json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False) + "\n"
    ).encode("utf-8")


def load_builder():
    path = BASE / "src/run.py"
    spec = importlib.util.spec_from_file_location("gdt619_builder", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load GDT619 registration builder")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def load_acquirer():
    path = ROOT / ACQUIRE_REL
    spec = importlib.util.spec_from_file_location("gdt619_stage_a_acquirer", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load GDT619 Stage-A acquirer")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class Audit:
    def __init__(self) -> None:
        self.rows: list[dict[str, str]] = []

    def check(self, name: str, condition: bool) -> None:
        self.rows.append({"check": name, "status": "PASS" if condition else "FAIL"})

    @property
    def passed(self) -> bool:
        return all(row["status"] == "PASS" for row in self.rows)

    def payload(self) -> dict:
        passed = sum(row["status"] == "PASS" for row in self.rows)
        return {
            "checks": self.rows,
            "decision": (
                "PROFILE_REGISTERED__NO_IMAGE_REQUEST_EXECUTED"
                if self.passed
                else "REGISTRATION_VALIDATION_FAILURE"
            ),
            "experiment_id": "GDT619",
            "failed": len(self.rows) - passed,
            "passed": passed,
            "schema_version": 1,
            "status": "PASS" if self.passed else "FAIL",
            "total": len(self.rows),
        }


def main() -> int:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--print-artifact-template", action="store_true")
    mode.add_argument("--write-artifact", action="store_true")
    args = parser.parse_args()

    audit = Audit()
    builder = load_builder()
    profile_path = ROOT / PROFILE_REL
    validation_path = ROOT / VALIDATION_REL
    manifest_path = ROOT / MANIFEST_REL
    profile = json.loads(profile_path.read_text(encoding="utf-8"))
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))

    audit.check(
        "profile_is_canonical_builder_output",
        profile_path.read_bytes() == builder.canonical_bytes(builder.build_profile()),
    )
    audit.check(
        "profile_schema_and_identity",
        profile.get("schema_version") == 1 and profile.get("experiment_id") == "GDT619",
    )
    audit.check(
        "profile_registration_decision",
        profile.get("decision") == "PROFILE_REGISTERED__NO_IMAGE_REQUEST_EXECUTED",
    )
    audit.check(
        "profile_claim_ceiling",
        profile.get("claim_ceiling")
        == "REQUEST_PROFILE_ONLY__NO_SOURCE_LOCATOR_VERIFIED__NO_TRANSCRIPTION__NO_VOYNICH_VALUE_OR_MEANING",
    )

    dependency = profile.get("dependency", {})
    dependency_path = ROOT / dependency.get("gdt618_plan_path", "__missing__")
    audit.check(
        "gdt618_dependency_exact",
        dependency.get("gdt618_plan_path") == str(GDT618_PLAN_REL)
        and dependency.get("gdt618_plan_sha256") == GDT618_PLAN_SHA256
        and dependency.get("gdt618_public_commit") == "c0266e78",
    )
    audit.check(
        "gdt618_dependency_bytes",
        dependency_path.is_file() and digest(dependency_path) == GDT618_PLAN_SHA256,
    )

    expected_rows = [
        ("DEV01", "Balsamus", "f25v", "f58", "25v", 3302, 4581, "f10v", 20, 26, 1707, 2547),
        ("DEV02", "Cerfolium", "f44v", "f96", "44v", 3451, 4553, "f35v", 70, 76, 1707, 2563),
        ("DEV03", "Liquiritia", "f85v", "f178", "85v", 3284, 4557, "f80r", 159, 165, 1707, 2624),
        ("DEV04", "Cucurbita", "f42r", "f91", "42r", 3333, 4388, "f46r", 91, 97, 1707, 2576),
        ("DEV05", "Diptamus", "f57v", "f122", "57v", 3346, 4574, "f48v", 96, 102, 1707, 2587),
    ]
    actual_rows = []
    gallica_url_ok = True
    for row in profile.get("candidates", []):
        lat = row.get("lat6823", {})
        clm = row.get("clm28531", {})
        leaf = lat.get("image_service_id", "").rsplit("/", 1)[-1]
        size = lat.get("canvas_size", {})
        actual_rows.append(
            (
                row.get("candidate_id"),
                row.get("developmental_headword"),
                lat.get("folio"),
                leaf,
                lat.get("canvas_label"),
                size.get("width"),
                size.get("height"),
                clm.get("folio"),
                clm.get("main_folio_ordinal"),
                clm.get("canvas_ordinal"),
                clm.get("body_width"),
                clm.get("body_height"),
            )
        )
        service = lat.get("image_service_id")
        gallica_url_ok &= lat.get("canvas_id") == (
            f"https://gallica.bnf.fr/iiif/ark:/12148/btv1b6000517p/canvas/{leaf}"
        )
        gallica_url_ok &= lat.get("native_image_url") == (
            f"{service}/full/full/0/native.jpg"
        )
        gallica_url_ok &= lat.get("image_api_version") == "1.1"
        clm_ordinal = clm.get("canvas_ordinal")
        clm_service = (
            "https://api.digitale-sammlungen.de/iiif/image/v3/"
            f"bsb00107549_{clm_ordinal:05d}"
        )
        gallica_url_ok &= clm.get("scan_id") == f"bsb00107549_{clm_ordinal:05d}"
        gallica_url_ok &= clm.get("image_service_id") == clm_service
        gallica_url_ok &= clm.get("full_page_url") == f"{clm_service}/full/max/0/default.jpg"
        gallica_url_ok &= clm.get("body_id") == clm.get("full_page_url")
        gallica_url_ok &= clm.get("body_type") == "Image"
        gallica_url_ok &= clm.get("image_service_type") == "ImageService3"
        gallica_url_ok &= clm.get("image_service_profile") == "level2"
    audit.check("five_candidate_rows_exact", actual_rows == expected_rows)
    audit.check("five_gallica_canvas_service_urls_exact", gallica_url_ok)
    audit.check(
        "candidate_identities_unique",
        len({row[0] for row in actual_rows}) == 5
        and len({row[3] for row in actual_rows}) == 5
        and len({row[7] for row in actual_rows}) == 5
        and len({row[9] for row in actual_rows}) == 5,
    )

    access = profile.get("access_audit", {})
    audit.check(
        "metadata_only_exposure_and_zero_image_access",
        access
        == {
            "developmental_metadata_responses_bound": 4,
            "image_bytes_received": 0,
            "registration_builder_network_requests": 0,
            "source_full_image_requests": 0,
            "source_page_images_opened": 0,
            "source_thumbnail_requests": 0,
            "target_requests": 0,
            "voynich_material_opened": 0,
        },
    )
    expected_metadata = [
        ("CLM28531_OFFICIAL_IIIF_V3_MANIFEST", 261778, "6f25dbd8a0baff9a681e8c486a9a883ed704671c155a7cfd81775e9f2a235fd3", "https://api.digitale-sammlungen.de/iiif/presentation/v3/bsb00107549/manifest"),
        ("COD_ICON_222_OFFICIAL_IIIF_V3_MANIFEST__SCAN_CONVENTION_CONTROL", 598251, "05b7042359e9b9e1e270c325531e42f1e4d5fdad82014c1930af492a91e408c1", "https://api.digitale-sammlungen.de/iiif/presentation/v3/bsb00020956/manifest"),
        ("COD_ICON_222_OFFICIAL_METS__SCAN_CONVENTION_CONTROL", 573418, "280b9bd2e715f2bf977a705695110802c2aa1763d8051846d797e8b23a92ccbc", "https://daten.digitale-sammlungen.de/~db/mets/bsb00020956_mets.xml"),
        ("CLM4623_OFFICIAL_IIIF_V3_MANIFEST__MICROFORM_CONVENTION_CONTROL", 395209, "90dda0fc3b21ceec27ecf849fa74a328f2ce04eaff6fbb7022aecf39a50b4c77", "https://api.digitale-sammlungen.de/iiif/presentation/v3/bsb00112053/manifest"),
    ]
    actual_metadata = [
        (row.get("role"), row.get("bytes"), row.get("sha256"), row.get("url"))
        for row in profile.get("metadata_evidence_bindings", [])
    ]
    audit.check("four_metadata_bindings_exact", actual_metadata == expected_metadata)
    audit.check(
        "metadata_access_disclosed_no_images",
        all(
            row.get("access_status") == "DEVELOPMENTALLY_FETCHED_METADATA_ONLY__NO_IMAGE"
            and HEX64.fullmatch(row.get("sha256", ""))
            for row in profile.get("metadata_evidence_bindings", [])
        ),
    )
    forbidden = set(profile.get("forbidden_access", []))
    audit.check("sealed_folios_forbidden", {"F84", "F84R"}.issubset(forbidden))
    audit.check(
        "target_ocr_and_network_crops_forbidden",
        {
            "VOYNICH_PAGE",
            "VOYNICH_TRANSCRIPTION",
            "VOYNICH_TARGET_FEATURE",
            "OCR",
            "AUTOMATIC_IMAGE_CLASSIFICATION",
            "NETWORK_CROP",
            "UNREGISTERED_IMAGE_URL",
        }.issubset(forbidden),
    )

    governance = profile.get("request_governance", {})
    audit.check(
        "single_identity_no_redirect_no_retry",
        governance.get("accept_encoding") == "identity"
        and governance.get("concurrency") == 1
        and governance.get("follow_redirects") is False
        and governance.get("retries") == 0,
    )
    audit.check(
        "request_intent_and_failure_journal_bound",
        governance.get("request_intent_must_be_fsynced_before_network") is True
        and governance.get("request_journal_preserves_failures") is True,
    )
    audit.check(
        "bsb_rate_and_request_caps",
        governance.get("bsb_minimum_seconds_between_completed_request_and_next_start") == 4
        and governance.get("maximum_bsb_requests_direct_branch") == 7
        and governance.get("maximum_bsb_requests_fallback_branch") == 9
        and governance.get("maximum_gallica_requests") == 5,
    )
    audit.check(
        "head_info_and_network_crop_disabled",
        governance.get("http_method") == "GET"
        and governance.get("unregistered_head_requests") is False
        and governance.get("unregistered_info_json_requests") is False
        and governance.get("information_requests") is False
        and governance.get("network_crops") is False,
    )
    audit.check(
        "stage_order_and_public_resolution_gate",
        governance.get("stage_a_must_finish_before_stage_b") is True
        and governance.get("stage_b_requires_public_stage1_resolution") is True,
    )

    stage_a = profile.get("stage_a", {})
    machine = stage_a.get("acquisition_state_machine", {})
    audit.check(
        "stage_a_state_machine_contract_bound",
        machine.get("source_path")
        == "experiments/yolo/gdt619_five_source_page_acquisition/src/acquire_stage_a.py"
        and machine.get("network_on_import") is False
        and machine.get("journal_filename") == "REQUEST_JOURNAL.jsonl"
        and machine.get("failure_bytes_policy")
        == "PRESERVE_ONLY_BODY_BYTES_FULLY_OBTAINED_WITHIN_CAP_THEN_REJECTED_BY_DECODE_OR_SEMANTIC_VALIDATION__NO_CLAIM_FOR_HTTP_REDIRECT_WRONG_MEDIA_OR_OVERCAP"
        and machine.get("exclusive_lock_filename") == "STAGE_A_EXCLUSIVE.lock"
        and machine.get("exclusive_lock_mode")
        == "ADVISORY_FLOCK_NONBLOCKING__KERNEL_RELEASES_ON_PROCESS_DEATH"
        and machine.get("jpeg_decoder_dependency")
        == {"package": "Pillow", "version": "10.2.0", "requirements_path": str(REQUIREMENTS_REL), "decode": "Image.verify_then_reopen_and_load"}
        and machine.get("directory_durability")
        == "FSYNC_PARENT_AFTER_OWNER_OR_LOCK_OR_JOURNAL_CREATION_AND_AFTER_EVERY_STATE_REPLACE"
        and machine.get("new_private_directory_durability")
        == "FSYNC_NEW_DIRECTORY_PARENT_ENTRY_IMMEDIATELY_AFTER_MKDIR"
        and machine.get("exactly_once_policy")
        == "FSYNC_IN_FLIGHT_BEFORE_GET__ANY_UNRESOLVED_ATTEMPT_PERMANENTLY_REFUSES_RESEND"
        and machine.get("pre_send_duplicate_rule")
        == "REFUSE_URL_IF_ANY_PRIOR_REQUEST_INTENT_OR_REQUEST_SUCCESS_EXISTS"
        and machine.get("ownership_marker")
        == {"filename": "GDT619_PRIVATE_OWNER.json", "fresh_or_exact_marker_required": True, "atomic_create_exclusive": True}
        and len(machine.get("commands", {})) == 5,
    )
    audit.check(
        "stage_a_allowlist_exact_v3",
        machine.get("exact_initial_allowlist")
        == [
            "https://api.digitale-sammlungen.de/iiif/presentation/v3/bsb00107549/manifest",
            "https://api.digitale-sammlungen.de/iiif/image/v3/bsb00107549_00026/full/1200,/0/default.jpg",
            "https://api.digitale-sammlungen.de/iiif/image/v3/bsb00107549_00025/full/1200,/0/default.jpg",
            "https://api.digitale-sammlungen.de/iiif/image/v3/bsb00107549_00027/full/1200,/0/default.jpg",
        ],
    )
    audit.check(
        "stage_a_private_output_constraints",
        machine.get("output_directory_constraints")
        == {
            "absolute_path_required": True,
            "group_or_other_permissions_allowed": False,
            "outside_repository_required": True,
            "symlink_allowed": False,
            "symlinked_path_components_allowed": False,
        },
    )
    audit.check(
        "stage_a_journal_fields_exact",
        machine.get("request_intent_required_fields")
        == [
            "defined_delay_seconds",
            "event",
            "headers",
            "intent_written_utc",
            "method",
            "resource_class",
            "seconds_since_previous_bsb_completion",
            "sequence",
            "url",
        ]
        and machine.get("request_success_required_fields")
        == [
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
    )
    bsb = stage_a.get("bsb_manifest", {})
    audit.check(
        "bsb_manifest_profile_exact",
        bsb
        == {
            "expected_canvas_count": 316,
            "expected_object_id": "bsb00107549",
            "expected_presentation_api_version": 3,
            "expected_response_bytes": 261778,
            "expected_response_sha256": "6f25dbd8a0baff9a681e8c486a9a883ed704671c155a7cfd81775e9f2a235fd3",
            "maximum_response_bytes": 5000000,
            "request_order": 1,
            "url": "https://api.digitale-sammlungen.de/iiif/presentation/v3/bsb00107549/manifest",
        },
    )
    extraction = stage_a.get("canvas_service_extraction", {})
    audit.check(
        "bsb_service_extraction_and_identity_exact",
        extraction.get("canvas_array_json_pointer") == "/items"
        and extraction.get("service_json_pointer_from_canvas")
        == "/items/0/items/0/body/service/0/id"
        and extraction.get("painting_annotation_page_count") == 1
        and extraction.get("painting_annotation_count") == 1
        and extraction.get("resource_format") == "image/jpeg"
        and extraction.get("service_type") == "ImageService3"
        and extraction.get("service_profile") == "level2"
        and extraction.get("service_id_regex")
        == r"^https://api\.digitale-sammlungen\.de/iiif/image/v3/bsb00107549_[0-9]{5}$",
    )

    mapping = stage_a.get("metadata_mapping", {})
    audit.check(
        "metadata_formula_and_exact_canvases",
        mapping.get("canvas_count") == 316
        and mapping.get("formula_recto") == "2*n+5"
        and mapping.get("formula_verso") == "2*n+6"
        and mapping.get("base_canvas_ordinals")
        == {"f10v": 26, "f35v": 76, "f80r": 165, "f46r": 97, "f48v": 102}
        and mapping.get("total_scan_model")
        == "II_PLUS_154_LEAVES_PLUS_FOUR_COVER_OR_MIRROR_SCANS",
    )
    audit.check(
        "metadata_support_roles_and_bound_order",
        mapping.get("binding_order_statement")
        == "WAGNER_FOLIATION_ADDED_AFTER_DISORDER__USE_PHYSICAL_BOUND_ORDER"
        and mapping.get("supporting_metadata_roles")
        == [
            "CLM28531_OFFICIAL_IIIF_V3_MANIFEST",
            "COD_ICON_222_OFFICIAL_IIIF_V3_MANIFEST__SCAN_CONVENTION_CONTROL",
            "COD_ICON_222_OFFICIAL_METS__SCAN_CONVENTION_CONTROL",
            "CLM4623_OFFICIAL_IIIF_V3_MANIFEST__MICROFORM_CONVENTION_CONTROL",
        ],
    )

    calibration = stage_a.get("rubric_calibration", {})
    audit.check(
        "single_primary_balsamus_calibration_exact",
        calibration.get("headword") == "Balsamus"
        and calibration.get("primary_folio") == "f10v"
        and calibration.get("primary_canvas_ordinal") == 26
        and calibration.get("primary_thumbnail_url")
        == "https://api.digitale-sammlungen.de/iiif/image/v3/bsb00107549_00026/full/1200,/0/default.jpg"
        and calibration.get("thumbnail_request_suffix")
        == "/full/1200,/0/default.jpg"
        and calibration.get("maximum_thumbnail_bytes") == 5000000,
    )
    audit.check(
        "fallback_only_adjacent_scans_exact",
        calibration.get("fallback_global_deltas") == [-1, 1]
        and calibration.get("fallback_thumbnail_urls")
        == [
            "https://api.digitale-sammlungen.de/iiif/image/v3/bsb00107549_00025/full/1200,/0/default.jpg",
            "https://api.digitale-sammlungen.de/iiif/image/v3/bsb00107549_00027/full/1200,/0/default.jpg",
        ]
        and calibration.get("fallback_rule")
        == "ONLY_PRIMARY_VISIBLY_ABSENT_AUTHORIZES_SCAN25_THEN_SCAN27__EXACTLY_ONE_VISIBLE_AND_ONE_VISIBLY_ABSENT_SELECTS_ONE_GLOBAL_DELTA__AMBIGUOUS_OR_TRANSPORT_OR_DECODE_FAILURE_STOPS",
    )
    audit.check(
        "calibration_manual_rubric_not_image_similarity",
        calibration.get("selection_method")
        == "MANUALLY_VISIBLE_RUBRIC_ONLY__NO_IMAGE_SIMILARITY__NO_OCR"
        and calibration.get("allowed_observation_enum")
        == ["VISIBLE", "VISIBLY_ABSENT", "AMBIGUOUS_OR_UNREADABLE"]
        and calibration.get("transport_or_decode_failure_action")
        == "STOP_WITHOUT_FALLBACK"
        and stage_a.get("rubric_observation_policy")
        == {
            "automatic_methods": False,
            "botanical_image_similarity": False,
            "manual_visible_rubric_only": True,
        },
    )

    stage1 = stage_a.get("stage1_resolution_contract", {})
    audit.check(
        "stage1_publication_gate_exact",
        stage1.get("artifact_name") == "STAGE1_RESOLUTION.json"
        and stage1.get("must_be_published_before_stage_b") is True
        and stage1.get("status_before_publication") == "STAGE_B_FORBIDDEN"
        and stage1.get("stage_b_url_suffix") == "/full/max/0/default.jpg",
    )
    audit.check(
        "stage1_resolution_nested_types_complete",
        stage1.get("nested_types")
        == {
            "calibration": {"branch": "str", "observations": "list[object]", "selected_global_delta": "int"},
            "manifest": {"bytes": "int", "sha256": "hex64", "url": "https_url"},
            "request_evidence": {"failure_count": "int", "intent_count": "int", "journal_sha256": "hex64", "minimum_bsb_spacing_seconds": "number", "success_count": "int", "thumbnails": "list[one_direct_or_three_fallback_public_request_evidence_objects]"},
            "rights": {"provider": "list[object]", "requiredStatement": "object", "rights": "https_url"},
            "schema_version": "int=1",
            "selected_pages": "list[exactly_5_selected_page_objects]",
            "status": "str=STAGE1_RESOLVED__STAGE_B_URLS_PUBLICLY_UNBOUND",
        }
        and stage1.get("selected_page_object_types")
        == {
            "body": "object{id:str,type:Image,format:image/jpeg,width:int,height:int,service:object}",
            "candidate_id": "str",
            "canvas_id": "str",
            "canvas_ordinal": "int",
            "folio": "str",
            "stage_b_url": "https_url_ending_/full/max/0/default.jpg",
        },
    )
    fail_stops = set(stage_a.get("resolution_fail_stops", []))
    audit.check(
        "stage_a_fail_stops_complete",
        {
            "MANIFEST_REDIRECT_OR_NON_200",
            "MANIFEST_BYTES_OR_SHA256_CHANGED",
            "MANIFEST_NOT_EXACTLY_316_CANVASES",
            "PRIMARY_AMBIGUOUS_OR_UNREADABLE",
            "PRIMARY_TRANSPORT_OR_DECODE_FAILURE",
            "FALLBACK_NOT_EXACTLY_ONE_VISIBLE_AND_ONE_VISIBLY_ABSENT",
            "FALLBACK_TRANSPORT_OR_DECODE_FAILURE",
            "ANY_SELECTION_USES_BOTANICAL_IMAGE_SIMILARITY",
            "ANY_OCR_OR_AUTOMATIC_IMAGE_CLASSIFICATION",
        }.issubset(fail_stops),
    )

    stage_b = profile.get("stage_b", {})
    bsb_full = stage_b.get("bsb_full_pages", {})
    audit.check(
        "stage_b_five_bsb_full_pages_exact",
        bsb_full
        == {
            "count": 5,
            "image_api_version": "3",
            "request_quality_format": "default.jpg",
            "request_region": "full",
            "request_rotation": "0",
            "request_size": "max",
            "request_suffix": "/full/max/0/default.jpg",
            "url_source": "PUBLIC_STAGE1_RESOLUTION_FIVE_LITERAL_BSB_STAGE_B_URLS",
        },
    )
    gallica = stage_b.get("gallica_native_pages", {})
    expected_gallica_urls = [
        "https://gallica.bnf.fr/iiif/ark:/12148/btv1b6000517p/f58/full/full/0/native.jpg",
        "https://gallica.bnf.fr/iiif/ark:/12148/btv1b6000517p/f96/full/full/0/native.jpg",
        "https://gallica.bnf.fr/iiif/ark:/12148/btv1b6000517p/f178/full/full/0/native.jpg",
        "https://gallica.bnf.fr/iiif/ark:/12148/btv1b6000517p/f91/full/full/0/native.jpg",
        "https://gallica.bnf.fr/iiif/ark:/12148/btv1b6000517p/f122/full/full/0/native.jpg",
    ]
    audit.check(
        "stage_b_five_gallica_native_pages_exact",
        gallica.get("count") == 5
        and gallica.get("image_api_version") == "1.1"
        and gallica.get("manifest_sha256")
        == "f22ea8cf697c5598f914bd92e101dd2da62a60df59561d67ef7384d5f5de7187"
        and gallica.get("request_region") == "full"
        and gallica.get("request_size") == "full"
        and gallica.get("request_rotation") == "0"
        and gallica.get("request_quality_format") == "native.jpg"
        and gallica.get("urls") == expected_gallica_urls,
    )
    audit.check(
        "stage_b_access_order_exact",
        stage_b.get("access_order")
        == [
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
    )
    crop = stage_b.get("local_crop_policy", {})
    audit.check(
        "network_crops_zero_local_provenance_bound",
        crop.get("network_crop_requests") == 0
        and crop.get("authoritative_network_source_remains_full_page") is True
        and crop.get("local_reading_crops_allowed_only_after_source_hashing") is True
        and crop.get("required_provenance_fields")
        == [
            "SOURCE_JPEG_SHA256",
            "SOURCE_WIDTH",
            "SOURCE_HEIGHT",
            "ZERO_BASED_X",
            "ZERO_BASED_Y",
            "WIDTH",
            "HEIGHT",
            "CROP_SHA256",
        ],
    )
    audit.check(
        "request_log_contract_complete",
        stage_b.get("request_log_required_fields")
        == [
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
    )

    rights = profile.get("rights_policy", {})
    audit.check(
        "rights_policy_exact",
        rights.get("bnf_attribution") == "Bibliothèque nationale de France"
        and rights.get("bnf_license_url")
        == "https://gallica.bnf.fr/html/und/conditions-dutilisation-des-contenus-de-gallica"
        and rights.get("bsb_expected_rights")
        == "https://creativecommons.org/publicdomain/mark/1.0/"
        and rights.get("bsb_top_level_json_pointers")
        == ["/rights", "/requiredStatement", "/provider"]
        and rights.get("bsb_required_statement_must_be_multilingual") is True
        and rights.get("bsb_provider_must_include_logo") is True
        and rights.get("bsb_missing_license_action")
        == "NO_IMAGE_OR_LOCAL_CROP_REDISTRIBUTION"
        and rights.get("iiif_availability_is_redistribution_permission") is False,
    )

    acquirer = load_acquirer()
    acquirer_self_test = acquirer.self_test()
    audit.check(
        "stage_a_acquirer_import_is_inert_and_self_test_passes",
        acquirer_self_test.get("status") == "PASS"
        and acquirer_self_test.get("failed") == 0
        and acquirer_self_test.get("total") >= 25,
    )
    audit.check(
        "stage_a_acquirer_constants_match_profile",
        acquirer.MANIFEST_URL == bsb.get("url")
        and acquirer.MANIFEST_BYTES == bsb.get("expected_response_bytes")
        and acquirer.MANIFEST_SHA256 == bsb.get("expected_response_sha256")
        and acquirer.THUMBNAIL_MAX_BYTES == calibration.get("maximum_thumbnail_bytes")
        and acquirer.PRIMARY_THUMBNAIL_URL == calibration.get("primary_thumbnail_url")
        and acquirer.FALLBACK_THUMBNAIL_URLS == calibration.get("fallback_thumbnail_urls")
        and sorted(acquirer.OBSERVATIONS) == sorted(calibration.get("allowed_observation_enum", [])),
    )
    audit.check(
        "pillow_runtime_and_pin_exact",
        acquirer.PILLOW_VERSION == "10.2.0"
        and (ROOT / REQUIREMENTS_REL).read_text(encoding="utf-8") == "Pillow==10.2.0\n",
    )

    sources = [BASE / "src/run.py", BASE / "src/validate.py"]
    network_roots = {"urllib", "requests", "http", "socket"}

    def imported_roots(path: Path) -> set[str]:
        tree = ast.parse(path.read_text(encoding="utf-8"))
        found: set[str] = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                found.update(alias.name.split(".", 1)[0] for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module:
                found.add(node.module.split(".", 1)[0])
        return found

    audit.check(
        "registration_sources_have_no_network_imports",
        all(imported_roots(path).isdisjoint(network_roots) for path in sources),
    )
    image_suffixes = {".bmp", ".gif", ".jp2", ".jpeg", ".jpg", ".png", ".tif", ".tiff", ".webp"}
    audit.check(
        "no_images_or_pdfs_in_registration",
        not any(
            path.is_file() and (path.suffix.lower() in image_suffixes or path.suffix.lower() == ".pdf")
            for path in BASE.rglob("*")
        ),
    )
    audit.check(
        "stage1_resolution_not_present",
        not (BASE / "artifacts/STAGE1_RESOLUTION.json").exists(),
    )

    audit.check(
        "manifest_identity_status_and_seals",
        manifest.get("experiment_id") == "GDT619"
        and manifest.get("slug") == "five_source_page_acquisition"
        and manifest.get("status") == "PROFILE_REGISTERED__NO_IMAGE_REQUEST_EXECUTED"
        and manifest.get("sealed_data") == {"f84": "FORBIDDEN", "f84r": "FORBIDDEN"},
    )
    audit.check("manifest_dependency", manifest.get("dependencies") == ["GDT618"])
    audit.check(
        "manifest_commands_exact",
        manifest.get("commands")
        == {
            "run": "python3 experiments/yolo/gdt619_five_source_page_acquisition/src/run.py --check",
            "validate": "python3 experiments/yolo/gdt619_five_source_page_acquisition/src/validate.py",
        },
    )
    audit.check(
        "manifest_validation_binding",
        manifest.get("validation")
        == {"artifact": str(VALIDATION_REL), "status": "PASS"},
    )
    expected_inputs = {str(GDT618_PLAN_REL)}
    expected_outputs = {
        str(BASE_REL / "README.md"),
        str(BASE_REL / "METHOD.md"),
        str(BASE_REL / "PREREGISTRATION.md"),
        str(BASE_REL / "artifacts/README.md"),
        str(PROFILE_REL),
        str(VALIDATION_REL),
        str(ACQUIRE_REL),
        str(REQUIREMENTS_REL),
        str(BASE_REL / "src/run.py"),
        str(BASE_REL / "src/validate.py"),
    }
    inputs = manifest.get("inputs", [])
    outputs = manifest.get("outputs", [])
    audit.check(
        "manifest_path_sets",
        {row.get("path") for row in inputs} == expected_inputs
        and len(inputs) == len(expected_inputs)
        and {row.get("path") for row in outputs} == expected_outputs
        and len(outputs) == len(expected_outputs),
    )
    nonvalidation_rows = inputs + [
        row for row in outputs if row.get("path") != str(VALIDATION_REL)
    ]
    audit.check(
        "manifest_nonvalidation_hashes",
        all(
            isinstance(row.get("sha256"), str)
            and HEX64.fullmatch(row["sha256"])
            and (ROOT / row["path"]).is_file()
            and digest(ROOT / row["path"]) == row["sha256"]
            for row in nonvalidation_rows
        ),
    )

    registered_payload = audit.payload()
    if args.print_artifact_template:
        print(json.dumps(registered_payload, indent=2, sort_keys=True, ensure_ascii=False))
        return 0 if audit.passed else 1
    if args.write_artifact:
        if not audit.passed:
            print(json.dumps(registered_payload, indent=2, sort_keys=True, ensure_ascii=False))
            return 1
        validation_path.write_bytes(canonical_bytes(registered_payload))
        print(f"WROTE {validation_path.relative_to(ROOT)} {digest(validation_path)}")
        return 0

    audit.check(
        "validation_artifact_matches_registered_payload",
        validation_path.is_file()
        and validation_path.read_bytes() == canonical_bytes(registered_payload),
    )
    validation_rows = [
        row for row in outputs if row.get("path") == str(VALIDATION_REL)
    ]
    audit.check(
        "manifest_validation_artifact_hash",
        len(validation_rows) == 1
        and validation_path.is_file()
        and digest(validation_path) == validation_rows[0].get("sha256"),
    )

    payload = audit.payload()
    print(json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False))
    return 0 if audit.passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
