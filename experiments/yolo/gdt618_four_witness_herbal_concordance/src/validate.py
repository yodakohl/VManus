#!/usr/bin/env python3
"""Validate GDT618's source-only registration without network access."""

from __future__ import annotations

import argparse
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
BASE_REL = Path("experiments/yolo/gdt618_four_witness_herbal_concordance")
BASE = ROOT / BASE_REL
PLAN_REL = BASE_REL / "artifacts/REGISTERED_SOURCE_PLAN.json"
VALIDATION_REL = BASE_REL / "artifacts/REGISTERED_VALIDATION.json"
MANIFEST_REL = BASE_REL / "experiment.json"
GDT617_REGISTRY_REL = Path("experiments/yolo/gdt617_triple_herbal_plaintext_transducer/artifacts/REGISTERED_SOURCE_BINDINGS.json")
GDT617_VALIDATION_REL = Path("experiments/yolo/gdt617_triple_herbal_plaintext_transducer/artifacts/REGISTERED_VALIDATION.json")
BNF_MANIFEST_REL = Path("experiments/yolo/gdt617_triple_herbal_plaintext_transducer/artifacts/source_freeze/bnf_lat6823_manifest.json")
HEX64 = re.compile(r"^[0-9a-f]{64}$")


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_bytes(value: dict) -> bytes:
    return (json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False) + "\n").encode("utf-8")


def load_builder():
    path = BASE / "src/run.py"
    spec = importlib.util.spec_from_file_location("gdt618_builder", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load registration builder")
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
            "decision": "SOURCE_PLAN_REGISTERED__NO_IMAGES_OPENED" if self.passed else "REGISTRATION_VALIDATION_FAILURE",
            "experiment_id": "GDT618",
            "failed": len(self.rows) - passed,
            "passed": passed,
            "schema_version": 1,
            "status": "PASS" if self.passed else "FAIL",
            "total": len(self.rows),
        }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--print-artifact-template", action="store_true")
    args = parser.parse_args()

    audit = Audit()
    builder = load_builder()
    plan_path = ROOT / PLAN_REL
    manifest_path = ROOT / MANIFEST_REL
    validation_path = ROOT / VALIDATION_REL

    plan = json.loads(plan_path.read_text(encoding="utf-8"))
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    expected_plan = builder.canonical_bytes(builder.build_plan())

    audit.check("plan_is_canonical_builder_output", plan_path.read_bytes() == expected_plan)
    audit.check("plan_schema_and_experiment", plan.get("schema_version") == 1 and plan.get("experiment_id") == "GDT618")
    audit.check("registration_decision", plan.get("decision") == "SOURCE_PLAN_REGISTERED__NO_IMAGES_OPENED")
    audit.check("developmental_exposure_declared", plan.get("candidate_selection_status") == "DEVELOPMENTAL__PREPUBLICATION_EXPOSURE_DECLARED")
    audit.check("claim_ceiling", plan.get("claim_ceiling") == "SOURCE_PLAN_ONLY__NO_VERIFIED_CONCORDANCE__NO_VOYNICH_VALUE_OR_MEANING")

    inherited = plan.get("inherited_gdt617", {})
    registry_path = ROOT / inherited.get("registry_path", "__missing__")
    inherited_validation_path = ROOT / inherited.get("validation_path", "__missing__")
    audit.check("gdt617_decision", inherited.get("decision") == "SOURCE_BINDING_PASS__TARGET_UNOPENED")
    audit.check("gdt617_registry_hash", registry_path.is_file() and digest(registry_path) == inherited.get("registry_sha256"))
    audit.check("gdt617_validation_hash", inherited_validation_path.is_file() and digest(inherited_validation_path) == inherited.get("validation_sha256"))

    registry = json.loads(registry_path.read_text(encoding="utf-8"))
    actual_sources = [
        {
            "binding_sha256": source["expected_binding_sha256"],
            "source_id": source["source_id"],
            "url": source["url"],
        }
        for source in registry["sources"]
    ]
    audit.check("six_inherited_official_sources", len(actual_sources) == 6 and actual_sources == inherited.get("sources"))
    audit.check("inherited_urls_https", all(row["url"].startswith("https://") for row in actual_sources))
    audit.check("inherited_hashes_well_formed", all(HEX64.fullmatch(row["binding_sha256"]) for row in actual_sources))

    external = plan.get("external_sources", [])
    ext_roles = {row.get("role"): row for row in external}
    wagner = ext_roles.get("WAGNER_DISSERTATION_PDF__APPENDIX_1_TRIPLE_CONCORDANCE", {})
    audit.check("three_external_bindings", len(external) == 3)
    audit.check("bsb_official_manifest_exact_url", ext_roles.get("OFFICIAL_CLM28531_IIIF_PRESENTATION_MANIFEST", {}).get("url") == "https://api.digitale-sammlungen.de/iiif/presentation/v2/bsb00107549/manifest")
    audit.check("wagner_stable_landing_exact_url", ext_roles.get("WAGNER_DISSERTATION_STABLE_LANDING", {}).get("url") == "https://freidok.uni-freiburg.de/data/2936")
    audit.check("wagner_pdf_exact_binding", wagner.get("url") == "https://freidok.uni-freiburg.de/files/2936/ETC8E6ksNFx7t_Bv/Diss_Eva_Wagner.pdf" and wagner.get("bytes") == 62861131 and wagner.get("sha256") == "8f57e7aaee4fe049ecf3fbf201ba2bf13bd6c446438ed59098afe2d28ee7a4fe" and wagner.get("used_pdf_pages") == [220, 222])
    audit.check("external_sources_not_fetched", all(row.get("access_status") in {"REGISTERED_NOT_FETCHED", "HASH_BOUND_NOT_RETAINED_IN_GIT"} for row in external))

    expected_candidates = [
        ("DEV01", "Balsamus", "f25v", "f58", "f10v", "p96", "f10v", "cgfbt113999s", 220),
        ("DEV02", "Cerfolium", "f44v", "f96", "f35v", "p68", "f30v", "cgfbt114071j", 222),
        ("DEV03", "Citruli", "f42v", "f92", "f40r", "p77", "f32v", "cgfbt1140616", 222),
        ("DEV04", "Cucurbita", "f42r", "f91", "f46r", "p121", "f36r", "cgfbt114059w", 222),
        ("DEV05", "Diptamus", "f57v", "f122", "f48v", "p126", "f37v", "cgfbt114128s", 222),
    ]
    actual_candidates = []
    for row in plan.get("candidates", []):
        binding = row.get("lat6823_canvas_binding", {})
        evidence = row.get("locator_evidence", {})
        rubric = evidence.get("lat6823_direct_rubric", {})
        wagner_row = evidence.get("wagner_explicit_triple", {})
        service_id = binding.get("image_service_id", "")
        leaf = service_id.rsplit("/", 1)[-1]
        actual_candidates.append(
            (
                row.get("candidate_id"),
                row.get("developmental_headword"),
                row.get("locators", {}).get("BNF_LAT6823"),
                leaf,
                row.get("locators", {}).get("BSB_CLM28531"),
                row.get("locators", {}).get("MASSON116"),
                row.get("locators", {}).get("SLOANE4016"),
                rubric.get("ark_id"),
                wagner_row.get("pdf_page"),
            )
        )
    audit.check("five_candidate_rows_exact", actual_candidates == expected_candidates)
    audit.check("mechanical_candidate_selection_rule", plan.get("candidate_selection_rule") == "DIRECT_LAT6823_RUBRIC_ARK_PLUS_EXPLICIT_WAGNER_CLM_MASSON_SLOANE_LOCATORS")
    audit.check("candidate_status_provisional", all(row.get("locator_status") == "PROVISIONAL_FOUR_WITNESS_JOIN__MANUAL_VERIFICATION_REQUIRED" for row in plan.get("candidates", [])))
    audit.check("locators_unique_within_each_witness", all(len({row["locators"][witness] for row in plan["candidates"]}) == 5 for witness in ("BNF_LAT6823", "BSB_CLM28531", "MASSON116", "SLOANE4016")))
    evidence_ok = True
    for row in plan["candidates"]:
        rubric = row["locator_evidence"]["lat6823_direct_rubric"]
        wagner_row = row["locator_evidence"]["wagner_explicit_triple"]
        evidence_ok &= rubric.get("authority") == "BNF_MANDRAGORE"
        evidence_ok &= rubric.get("url") == f"https://mandragore.bnf.fr/ark:/12148/{rubric.get('ark_id')}"
        evidence_ok &= wagner_row == {
            "clm28531": row["locators"]["BSB_CLM28531"],
            "masson116": row["locators"]["MASSON116"],
            "pdf_page": 220 if row["candidate_id"] == "DEV01" else 222,
            "sloane4016": row["locators"]["SLOANE4016"],
        }
    audit.check("direct_rubric_and_explicit_wagner_evidence", evidence_ok)
    audit.check("superseded_leads_recorded", plan.get("superseded_developmental_leads") == [{"headword": "Ciclamen", "reason": "REPLACED_BY_STRONGER_DIRECT_RUBRIC_PLUS_EXPLICIT_WAGNER_ROW"}, {"headword": "Cubebe", "reason": "REPLACED_BY_STRONGER_DIRECT_RUBRIC_PLUS_EXPLICIT_WAGNER_ROW"}])

    frozen_manifest = json.loads((ROOT / BNF_MANIFEST_REL).read_text(encoding="utf-8"))
    canvases_by_label = {canvas["label"]: canvas for canvas in frozen_manifest["sequences"][0]["canvases"]}
    canvas_bindings_ok = True
    for row in plan["candidates"]:
        label = row["locators"]["BNF_LAT6823"].removeprefix("f")
        canvas = canvases_by_label.get(label, {})
        binding = row["lat6823_canvas_binding"]
        service = canvas.get("images", [{}])[0].get("resource", {}).get("service", {})
        canvas_bindings_ok &= canvas.get("@id") == binding.get("canvas_id")
        canvas_bindings_ok &= service.get("@id") == binding.get("image_service_id")
        canvas_bindings_ok &= binding.get("derived_from_frozen_manifest_sha256") == digest(ROOT / BNF_MANIFEST_REL)
        canvas_bindings_ok &= binding.get("image_request_profile") == "UNREGISTERED__FIX_ONLY_AFTER_PUBLIC_SOURCE_PLAN_AND_BEFORE_REQUEST"
    audit.check("lat6823_canvas_service_bindings_match_frozen_manifest", canvas_bindings_ok)
    audit.check("future_image_profile_deferred", plan.get("future_image_request_policy") == "PROFILE_MUST_BE_PUBLICLY_REGISTERED_AFTER_THIS_PLAN_AND_BEFORE_ANY_IMAGE_REQUEST")

    contract = plan.get("transcription_contract", {})
    audit.check("lat6823_sole_scoring_witness", contract.get("lat6823_role") == "SOLE_SCORING_TEXT_WITNESS")
    audit.check("clm_control_only", contract.get("clm_role") == "INDEPENDENT_LOCATOR_AND_READING_CONTROL_ONLY__NEVER_REPAIR_LAT6823")
    audit.check("masson_sloane_locator_only", contract.get("masson_role") == "CONCORDANCE_LOCATOR_ONLY" and contract.get("sloane_role") == "CONCORDANCE_LOCATOR_ONLY")
    audit.check("wagner_triple_scope_only", contract.get("wagner_scope") == "DIRECTLY_BINDS_CLM28531_MASSON116_SLOANE4016_ONLY__LAT6823_JOIN_SEPARATE")
    audit.check("exact_heading_plus_twelve", contract.get("required_lat6823_span") == "EXACT_HEADING_OR_RUBRIC_PLUS_FIRST_TWELVE_RUNNING_TEXT_TOKENS" and contract.get("body_token_count") == 12)
    audit.check("two_independent_readers", contract.get("independent_readers") == 2)
    audit.check("differences_reconciled", contract.get("difference_policy") == "RECORD_EVERY_DIFFERENCE_AND_RECONCILE_BEFORE_RESULT")
    audit.check("result_fields_complete", contract.get("result_fields") == ["READER_A_RAW", "READER_B_RAW", "DIFFERENCE_LEDGER", "RECONCILED_DIPLOMATIC", "NORMALIZATION_LEDGER", "EXACT_SCORING_BYTES"])

    audit.check("zero_prohibited_registration_access", plan.get("access_audit") and all(value == 0 for value in plan["access_audit"].values()))
    forbidden = set(plan.get("forbidden_access", []))
    audit.check("sealed_folios_forbidden_in_plan", {"F84", "F84R"}.issubset(forbidden))
    audit.check("target_and_semantics_forbidden", {"VOYNICH_PAGE", "VOYNICH_TRANSCRIPTION", "VOYNICH_TARGET_FEATURE", "SEMANTIC_VOYNICH_ASSIGNMENT"}.issubset(forbidden))
    image_suffixes = {".bmp", ".gif", ".jp2", ".jpeg", ".jpg", ".png", ".tif", ".tiff", ".webp"}
    audit.check("no_image_files_in_experiment", not any(path.is_file() and path.suffix.lower() in image_suffixes for path in BASE.rglob("*")))
    audit.check("wagner_pdf_not_retained", not any(path.is_file() and path.suffix.lower() == ".pdf" for path in BASE.rglob("*")))

    audit.check("manifest_identity", manifest.get("experiment_id") == "GDT618" and manifest.get("slug") == "four_witness_herbal_concordance")
    audit.check("manifest_status", manifest.get("status") == "SOURCE_PLAN_REGISTERED__NO_IMAGES_OPENED")
    audit.check("manifest_sealed_data", manifest.get("sealed_data") == {"f84": "FORBIDDEN", "f84r": "FORBIDDEN"})
    audit.check("manifest_dependency", manifest.get("dependencies") == ["GDT617"])
    audit.check("manifest_validation_binding", manifest.get("validation") == {"artifact": str(VALIDATION_REL), "status": "PASS"})

    expected_inputs = {str(GDT617_REGISTRY_REL), str(GDT617_VALIDATION_REL), str(BNF_MANIFEST_REL)}
    expected_outputs = {
        str(BASE_REL / "README.md"),
        str(BASE_REL / "METHOD.md"),
        str(BASE_REL / "PREREGISTRATION.md"),
        str(BASE_REL / "artifacts/README.md"),
        str(PLAN_REL),
        str(VALIDATION_REL),
        str(BASE_REL / "src/run.py"),
        str(BASE_REL / "src/validate.py"),
    }
    inputs = manifest.get("inputs", [])
    outputs = manifest.get("outputs", [])
    audit.check("manifest_path_sets", {row.get("path") for row in inputs} == expected_inputs and len(inputs) == len(expected_inputs) and {row.get("path") for row in outputs} == expected_outputs and len(outputs) == len(expected_outputs))
    nonvalidation_rows = inputs + [row for row in outputs if row.get("path") != str(VALIDATION_REL)]
    binding_rows_ok = all(
        isinstance(row.get("sha256"), str)
        and HEX64.fullmatch(row["sha256"])
        and (ROOT / row["path"]).is_file()
        and digest(ROOT / row["path"]) == row["sha256"]
        for row in nonvalidation_rows
    )
    audit.check("manifest_nonvalidation_hashes", binding_rows_ok)

    registered_payload = audit.payload()
    if args.print_artifact_template:
        print(json.dumps(registered_payload, indent=2, sort_keys=True, ensure_ascii=False))
        return 0 if audit.passed else 1

    audit.check("validation_artifact_matches_registered_payload", validation_path.is_file() and validation_path.read_bytes() == canonical_bytes(registered_payload))
    validation_rows = [row for row in outputs if row.get("path") == str(VALIDATION_REL)]
    audit.check("manifest_validation_artifact_hash", len(validation_rows) == 1 and validation_path.is_file() and digest(validation_path) == validation_rows[0].get("sha256"))

    payload = audit.payload()
    print(json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False))
    return 0 if audit.passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
