#!/usr/bin/env python3
"""Build or verify GDT618's deterministic source-only registration plan."""

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
BASE = ROOT / "experiments/yolo/gdt618_four_witness_herbal_concordance"
PLAN_PATH = BASE / "artifacts/REGISTERED_SOURCE_PLAN.json"


def build_plan() -> dict:
    inherited_sources = [
        {
            "binding_sha256": "3a9e1d8ddad676b2554b63fcf3b5706e508e85cf07f9c691cad9a664206d5109",
            "source_id": "BNF_LAT6823_CATALOG",
            "url": "https://gallica.bnf.fr/services/OAIRecord?ark=btv1b6000517p",
        },
        {
            "binding_sha256": "f22ea8cf697c5598f914bd92e101dd2da62a60df59561d67ef7384d5f5de7187",
            "source_id": "BNF_LAT6823_MANIFEST",
            "url": "https://gallica.bnf.fr/iiif/ark:/12148/btv1b6000517p/manifest.json",
        },
        {
            "binding_sha256": "12a855c6f8bf5c7087d65cb605d31edcfd487b4b4ae61343c45efe21d2024385",
            "source_id": "MASSON116_CATALOG",
            "url": "https://alexandrine-bibnum.beauxartsparis.fr/api/items/223335",
        },
        {
            "binding_sha256": "846e000f5a05a1e232b7f39b40a22c10ca116c198a9397604807e5f0d88f074f",
            "source_id": "MASSON116_MANIFEST",
            "url": "https://alexandrine-bibnum.beauxartsparis.fr/iiif/2/223335/manifest",
        },
        {
            "binding_sha256": "eba2603f877c6b7c3dbe5222e95159caa0537cec9938aba728658eaaabb147db",
            "source_id": "SLOANE4016_CATALOG",
            "url": "https://searcharchives.bl.uk/catalog/040-002116409.json",
        },
        {
            "binding_sha256": "607f98404cb733caf4bacb70047175aaf88e75735af18436511a8eee1cc55e10",
            "source_id": "SLOANE4016_MANIFEST",
            "url": "https://bl.digirati.io/iiif/ark:/81055/vdc_100165172997.0x000001",
        },
    ]
    candidate_values = [
        ("DEV01", "Balsamus", "f25v", "f58", "f10v", "p96", "f10v", "cgfbt113999s", 220),
        ("DEV02", "Cerfolium", "f44v", "f96", "f35v", "p68", "f30v", "cgfbt114071j", 222),
        ("DEV03", "Citruli", "f42v", "f92", "f40r", "p77", "f32v", "cgfbt1140616", 222),
        ("DEV04", "Cucurbita", "f42r", "f91", "f46r", "p121", "f36r", "cgfbt114059w", 222),
        ("DEV05", "Diptamus", "f57v", "f122", "f48v", "p126", "f37v", "cgfbt114128s", 222),
    ]
    candidates = []
    for candidate_id, headword, lat, gallica_leaf, clm, masson, sloane, mandragore_ark, wagner_page in candidate_values:
        candidates.append(
            {
                "candidate_id": candidate_id,
                "developmental_headword": headword,
                "lat6823_canvas_binding": {
                    "canvas_id": f"https://gallica.bnf.fr/iiif/ark:/12148/btv1b6000517p/canvas/{gallica_leaf}",
                    "derived_from_frozen_manifest_sha256": "f22ea8cf697c5598f914bd92e101dd2da62a60df59561d67ef7384d5f5de7187",
                    "image_request_profile": "UNREGISTERED__FIX_ONLY_AFTER_PUBLIC_SOURCE_PLAN_AND_BEFORE_REQUEST",
                    "image_service_id": f"https://gallica.bnf.fr/iiif/ark:/12148/btv1b6000517p/{gallica_leaf}",
                },
                "locator_evidence": {
                    "lat6823_direct_rubric": {
                        "ark_id": mandragore_ark,
                        "authority": "BNF_MANDRAGORE",
                        "url": f"https://mandragore.bnf.fr/ark:/12148/{mandragore_ark}",
                    },
                    "wagner_explicit_triple": {
                        "clm28531": clm,
                        "masson116": masson,
                        "pdf_page": wagner_page,
                        "sloane4016": sloane,
                    },
                },
                "locator_status": "PROVISIONAL_FOUR_WITNESS_JOIN__MANUAL_VERIFICATION_REQUIRED",
                "locators": {
                    "BNF_LAT6823": lat,
                    "BSB_CLM28531": clm,
                    "MASSON116": masson,
                    "SLOANE4016": sloane,
                },
            }
        )
    return {
        "access_audit": {
            "image_request_profiles_registered": 0,
            "network_requests": 0,
            "page_images_opened": 0,
            "source_canvases_opened": 0,
            "target_features_opened": 0,
            "voynich_pages_opened": 0,
            "voynich_transcriptions_opened": 0,
        },
        "candidate_selection_status": "DEVELOPMENTAL__PREPUBLICATION_EXPOSURE_DECLARED",
        "candidate_selection_rule": "DIRECT_LAT6823_RUBRIC_ARK_PLUS_EXPLICIT_WAGNER_CLM_MASSON_SLOANE_LOCATORS",
        "candidates": candidates,
        "claim_ceiling": "SOURCE_PLAN_ONLY__NO_VERIFIED_CONCORDANCE__NO_VOYNICH_VALUE_OR_MEANING",
        "decision": "SOURCE_PLAN_REGISTERED__NO_IMAGES_OPENED",
        "experiment_id": "GDT618",
        "external_sources": [
            {
                "access_status": "REGISTERED_NOT_FETCHED",
                "institution": "Bayerische_Staatsbibliothek",
                "role": "OFFICIAL_CLM28531_IIIF_PRESENTATION_MANIFEST",
                "url": "https://api.digitale-sammlungen.de/iiif/presentation/v2/bsb00107549/manifest",
            },
            {
                "access_status": "REGISTERED_NOT_FETCHED",
                "institution": "Albert_Ludwigs_Universitaet_Freiburg",
                "role": "WAGNER_DISSERTATION_STABLE_LANDING",
                "url": "https://freidok.uni-freiburg.de/data/2936",
            },
            {
                "access_status": "HASH_BOUND_NOT_RETAINED_IN_GIT",
                "bytes": 62861131,
                "institution": "Albert_Ludwigs_Universitaet_Freiburg",
                "role": "WAGNER_DISSERTATION_PDF__APPENDIX_1_TRIPLE_CONCORDANCE",
                "sha256": "8f57e7aaee4fe049ecf3fbf201ba2bf13bd6c446438ed59098afe2d28ee7a4fe",
                "url": "https://freidok.uni-freiburg.de/files/2936/ETC8E6ksNFx7t_Bv/Diss_Eva_Wagner.pdf",
                "used_pdf_pages": [
                    220,
                    222
                ],
            },
        ],
        "forbidden_access": [
            "F84",
            "F84R",
            "VOYNICH_PAGE",
            "VOYNICH_TRANSCRIPTION",
            "VOYNICH_TARGET_FEATURE",
            "SOURCE_CANVAS_OR_PAGE_IMAGE_DURING_REGISTRATION",
            "OCR",
            "AUTOMATIC_IMAGE_CLASSIFICATION",
            "EMBEDDING_RETRIEVAL",
            "GENERATED_CAPTION",
            "SEMANTIC_VOYNICH_ASSIGNMENT",
        ],
        "future_image_request_policy": "PROFILE_MUST_BE_PUBLICLY_REGISTERED_AFTER_THIS_PLAN_AND_BEFORE_ANY_IMAGE_REQUEST",
        "inherited_gdt617": {
            "decision": "SOURCE_BINDING_PASS__TARGET_UNOPENED",
            "registry_path": "experiments/yolo/gdt617_triple_herbal_plaintext_transducer/artifacts/REGISTERED_SOURCE_BINDINGS.json",
            "registry_sha256": "f4bffe9a24931a175c726a9e0cc1dca9c73cbd69053c78cb1345357a6cc58089",
            "sources": inherited_sources,
            "validation_path": "experiments/yolo/gdt617_triple_herbal_plaintext_transducer/artifacts/REGISTERED_VALIDATION.json",
            "validation_sha256": "333b94e54f3426021f9513a6f71e2ef8204bca46fa93196603783fc9d5896762",
        },
        "schema_version": 1,
        "superseded_developmental_leads": [
            {
                "headword": "Ciclamen",
                "reason": "REPLACED_BY_STRONGER_DIRECT_RUBRIC_PLUS_EXPLICIT_WAGNER_ROW"
            },
            {
                "headword": "Cubebe",
                "reason": "REPLACED_BY_STRONGER_DIRECT_RUBRIC_PLUS_EXPLICIT_WAGNER_ROW"
            }
        ],
        "transcription_contract": {
            "body_token_count": 12,
            "clm_role": "INDEPENDENT_LOCATOR_AND_READING_CONTROL_ONLY__NEVER_REPAIR_LAT6823",
            "difference_policy": "RECORD_EVERY_DIFFERENCE_AND_RECONCILE_BEFORE_RESULT",
            "independent_readers": 2,
            "lat6823_role": "SOLE_SCORING_TEXT_WITNESS",
            "masson_role": "CONCORDANCE_LOCATOR_ONLY",
            "required_lat6823_span": "EXACT_HEADING_OR_RUBRIC_PLUS_FIRST_TWELVE_RUNNING_TEXT_TOKENS",
            "result_fields": [
                "READER_A_RAW",
                "READER_B_RAW",
                "DIFFERENCE_LEDGER",
                "RECONCILED_DIPLOMATIC",
                "NORMALIZATION_LEDGER",
                "EXACT_SCORING_BYTES",
            ],
            "sloane_role": "CONCORDANCE_LOCATOR_ONLY",
            "wagner_scope": "DIRECTLY_BINDS_CLM28531_MASSON116_SLOANE4016_ONLY__LAT6823_JOIN_SEPARATE",
        },
    }


def canonical_bytes(value: dict) -> bytes:
    return (json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False) + "\n").encode("utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--check", action="store_true", help="verify the committed plan (default)")
    mode.add_argument("--print-plan", action="store_true", help="print canonical plan bytes")
    mode.add_argument("--print-sha256", action="store_true", help="print canonical plan SHA-256")
    args = parser.parse_args()

    expected = canonical_bytes(build_plan())
    if args.print_plan:
        print(expected.decode("utf-8"), end="")
        return 0
    if args.print_sha256:
        print(hashlib.sha256(expected).hexdigest())
        return 0
    if not PLAN_PATH.is_file():
        print(f"FAIL missing {PLAN_PATH.relative_to(ROOT)}")
        return 1
    actual = PLAN_PATH.read_bytes()
    if actual != expected:
        print("FAIL registered source plan differs from deterministic builder")
        return 1
    print(f"PASS {PLAN_PATH.relative_to(ROOT)} {hashlib.sha256(actual).hexdigest()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
