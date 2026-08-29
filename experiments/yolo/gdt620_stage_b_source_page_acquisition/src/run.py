#!/usr/bin/env python3
"""Build GDT620's Stage-B request profile without network or image access."""
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
BASE_REL = Path("experiments/yolo/gdt620_stage_b_source_page_acquisition")
PROFILE_REL = BASE_REL / "artifacts/REGISTERED_STAGE_B_PROFILE.json"
STAGE1_REL = Path("experiments/yolo/gdt619_five_source_page_acquisition/artifacts/STAGE1_RESOLUTION.json")
STAGE1_SHA256 = "95457d96fd7c8e4980c3e92bd1a4ac5009daf27090946b91407bbd476eb0d422"
SOURCE_PROFILE_REL = Path("experiments/yolo/gdt619_five_source_page_acquisition/artifacts/REGISTERED_REQUEST_PROFILE.json")
SOURCE_PROFILE_SHA256 = "c577525c5045b2e59ba68741fd098c1d94f43f6d52ac4364683f4dd1e1064164"
PUBLIC_STAGE1_COMMIT = "e82d73d6300f51c810ff131711ace31bb2610b69"
USER_AGENT = "VManus-GDT620-stage-b-source-acquisition/1.0"
BSB = [("DEV01",25,1707,2466),("DEV02",75,1707,2581),("DEV03",164,1707,2562),("DEV04",96,1707,2591),("DEV05",101,1707,2581)]
BNF = [("DEV01","f58",3302,4581),("DEV02","f96",3451,4553),("DEV03","f178",3284,4557),("DEV04","f91",3333,4388),("DEV05","f122",3346,4574)]

def canonical_bytes(value: object) -> bytes:
    return (json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False) + "\n").encode("utf-8")

def build_profile() -> dict:
    requests = []
    headers = {"Accept":"image/jpeg","Accept-Encoding":"identity","User-Agent":USER_AGENT}
    for sequence,(candidate,scan,width,height) in enumerate(BSB,1):
        service=f"https://api.digitale-sammlungen.de/iiif/image/v3/bsb00107549_{scan:05d}"
        requests.append({"candidate_id":candidate,"expected_dimensions":{"height":height,"width":width},"headers":headers,"institution":"BSB","resource_class":"IIIF_IMAGE_V3_MANIFEST_ADVERTISED_FULL_BODY","sequence":sequence,"url":f"{service}/full/max/0/default.jpg"})
    for sequence,(candidate,leaf,width,height) in enumerate(BNF,6):
        requests.append({"candidate_id":candidate,"expected_dimensions":{"height":height,"width":width},"headers":headers,"institution":"BNF_GALLICA","resource_class":"IIIF_IMAGE_1_1_NATIVE_FULL_RESOURCE","sequence":sequence,"url":f"https://gallica.bnf.fr/iiif/ark:/12148/btv1b6000517p/{leaf}/full/full/0/native.jpg"})
    return {
      "access_state_at_registration":{"image_bytes_received":0,"network_requests":0,"registration_is_offline":True,"source_images_opened":0,"stage1_already_public":True,"stage_b_acquisition_code_is_separate":True,"voynich_material_opened":0},
      "claim_ceiling":"REQUEST_PROFILE_ONLY__STAGE1_PUBLIC_AND_DELTA_MINUS_ONE__NO_STAGE_B_IMAGE_ACQUIRED__NO_SOURCE_TRANSCRIPTION__NO_VOYNICH_VALUE_OR_MEANING",
      "decision":"STAGE_B_PROFILE_REGISTERED__NO_STAGE_B_REQUEST_EXECUTED",
      "status":"STAGE_B_PROFILE_REGISTERED__NO_STAGE_B_REQUEST_EXECUTED",
      "dependency":{"public_stage1_commit":PUBLIC_STAGE1_COMMIT,"source_profile_path":str(SOURCE_PROFILE_REL),"source_profile_sha256":SOURCE_PROFILE_SHA256,"stage1_path":str(STAGE1_REL),"stage1_sha256":STAGE1_SHA256,"stage1_status_inside_frozen_artifact":"STAGE1_RESOLVED__STAGE_B_URLS_PUBLICLY_UNBOUND","stage1_publication_effect":"GLOBAL_DELTA_MINUS_ONE__STAGE_B_AUTHORIZED_NOT_EXECUTED"},
      "experiment_id":"GDT620",
      "forbidden_access":["F84","F84R","VOYNICH_PAGE","VOYNICH_TRANSCRIPTION","SOURCE_IMAGE_DISPLAY","SOURCE_IMAGE_READING","OCR","NETWORK_CROP","UNREGISTERED_URL"],
      "execution_publication_gate":{"committed_paths_must_match_runtime_bytes":[str(BASE_REL / "METHOD.md"),str(BASE_REL / "PREREGISTRATION.md"),str(PROFILE_REL),str(BASE_REL / "requirements.txt"),str(BASE_REL / "src/acquire_stage_b.py"),str(BASE_REL / "src/validate.py"),str(BASE_REL / "experiment.json")],"network_forbidden_until_registration_commit_is_public":True,"public_registration_commit_argument_required":True,"registration_commit_must_be_ancestor_of_origin_main":True,"working_tree_only_code_cannot_authorize_network":True},
      "output_contract":{"acquisition_implementation":"SEPARATE_CODE_WITHIN_GDT620__NOT_PART_OF_REGISTRATION_BUILDER","private_directory":{"absolute":True,"outside_repository":True,"mode":"0700","no_symlink_components":True,"ownership_marker_required":True,"second_execution_state_directory_forbidden_by_policy":True},"private_files":{"source_jpegs":"exactly_10","request_journal":"REQUEST_JOURNAL.jsonl","state":"stage_b_state.json"},"public_result_required_fields":["status","request_order","literal_urls","observed_bytes","raw_sha256","decoded_width","decoded_height","request_started_utc","response_completed_utc","response_headers","failure_count"],"public_result_must_exclude":["absolute_private_path","private_filename","image_bytes","authentication_material","machine_metadata"],"success_status":"TEN_SOURCE_PAGES_ACQUIRED__SOURCE_READING_UNOPENED__TARGET_UNOPENED"},
      "protocol":{"cap_semantics":{"content_encoding":"ABSENT_OR_IDENTITY_ONLY","content_length":"ZERO_OR_ONE_VALID_NONNEGATIVE_DECIMAL_AT_MOST_CAP__IF_PRESENT_MUST_EQUAL_OBSERVED_BYTES","content_length_above_cap":"STOP_BEFORE_BODY_READ","missing_or_at_most_cap_content_length":"STREAM_CAP_PLUS_ONE_STILL_REQUIRED","observed_body_above_cap":"STOP","partial_body_or_decode_or_dimension_mismatch":"STOP","transfer_encoding":"ABSENT_OR_EXACT_CHUNKED_WITHOUT_CONTENT_LENGTH"},"concurrency":1,"durability":"ADVISORY_SINGLE_PROCESS_LOCK__FSYNC_FILE_AND_PARENT_DIRECTORY_AFTER_CREATE_OR_REPLACE__PROCESS_DEATH_RELEASES_LOCK","exactly_once":"AT_MOST_ONCE_PER_BOUND_EXECUTION_STATE__FSYNC_REQUEST_INTENT_AND_IN_FLIGHT_STATE_BEFORE_GET__REFUSE_ANY_URL_WITH_PRIOR_INTENT_OR_SUCCESS__PERSIST_NEXT_SEQUENCE_AFTER_SUCCESS__SECOND_STATE_DIRECTORY_FORBIDDEN_BY_POLICY","failure_action":"STOP_ON_FIRST_FAILURE__NO_LATER_REQUEST","fixed_pre_request_delay":{"applies_to_sequences":[2,3,4,5,6,7,8,9,10],"elapsed_wall_time_never_reduces_delay":True,"required_after_restart":True,"seconds":4.0},"follow_redirects":False,"full_jpeg_validation":"Pillow_10_2_0__LOAD_TRUNCATED_FALSE__DECOMPRESSION_WARNINGS_ARE_ERRORS__verify_then_reopen_and_load__JPEG_ONE_FRAME__EXACT_STORED_DIMENSIONS__NO_EXIF_ORIENTATION_CORRECTION","header_semantics":{"application_headers_exact":["Accept","Accept-Encoding","User-Agent"],"opener_default_addheaders_disabled":True,"protocol_headers_may_be_generated_by_python":["Host","Connection: close"],"wire_header_set_claimed_exact":False},"http_method":"GET","maximum_response_bytes_each":50000000,"maximum_response_bytes_total":500000000,"network_crops":False,"proxy_cookie_auth":"DISABLED","request_total_wall_seconds":180,"socket_operation_timeout_seconds":60,"requests_allowed":10,"requests_by_institution":{"BNF_GALLICA":5,"BSB":5},"retries":0,"unregistered_head_requests":False,"unregistered_info_json_requests":False,"unregistered_manifest_requests":False},
      "requests":requests,
      "rights_policy":{"bnf_attribution":"Bibliothèque nationale de France","bnf_terms_url":"https://gallica.bnf.fr/html/und/conditions-dutilisation-des-contenus-de-gallica","bsb_rights":"https://creativecommons.org/publicdomain/mark/1.0/","image_redistribution_in_repository":False,"private_source_images_only":True},
      "schema_version":1,"sealed_data":{"f84":"FORBIDDEN","f84r":"FORBIDDEN"}}

def main() -> int:
    parser=argparse.ArgumentParser()
    mode=parser.add_mutually_exclusive_group()
    mode.add_argument("--check",action="store_true"); mode.add_argument("--print-profile",action="store_true"); mode.add_argument("--print-sha256",action="store_true"); mode.add_argument("--write-profile",action="store_true")
    args=parser.parse_args(); payload=canonical_bytes(build_profile()); path=ROOT/PROFILE_REL; sha256=hashlib.sha256(payload).hexdigest()
    if args.print_profile: print(payload.decode("utf-8"),end="")
    elif args.print_sha256: print(sha256)
    elif args.write_profile:
        path.parent.mkdir(parents=True,exist_ok=True); path.write_bytes(payload); print(f"WROTE {PROFILE_REL} {sha256}")
    else:
        if not path.is_file() or path.read_bytes()!=payload: print(f"FAIL {PROFILE_REL}"); return 1
        print(f"PASS {PROFILE_REL} {sha256}")
    return 0

if __name__=="__main__": raise SystemExit(main())
