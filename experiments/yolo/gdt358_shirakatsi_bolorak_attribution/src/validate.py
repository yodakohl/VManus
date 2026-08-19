#!/usr/bin/env python3
"""Nonimporting validation for GDT358."""
from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
EXP = ROOT / "experiments/yolo/gdt358_shirakatsi_bolorak_attribution"
ART = EXP / "artifacts"


def stable(value: object) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False) + "\n").encode()


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rows(name: str) -> list[dict[str, str]]:
    with (ART / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    checks: list[dict[str, object]] = []

    def ck(name: str, condition: bool, detail: str = "") -> None:
        checks.append({"name": name, "pass": bool(condition), "detail": detail})

    sources = rows("gdt358_external_sources.tsv")
    attribution = rows("gdt358_attribution_chain.tsv")
    landmarks = rows("gdt358_image_landmark_audit.tsv")
    edition = rows("gdt358_edition_visual_audit.tsv")
    capacity = rows("gdt358_key_capacity.tsv")
    counter = rows("gdt358_counterexamples.tsv")
    result_path = ART / "gdt358_result.json"
    result = json.loads(result_path.read_text(encoding="utf-8"))

    expected_hashes = {
        "PENN_LJS443_209R": "a218414d67f5044281c8cf6e6a3606447d01b023782a8756d1a3a3207a660530",
        "SAE_V1_P363_SCAN": "7cbde2d0d9883fb4615eb6ec7e2282311b692f72a163f637b7283cb8136757fa",
        "SAE_SHIRAKATSI_TRANSCRIPTION": "a39692d155aad2669baef38c63ba4e4e778d6f9bad37b6a38eb16dacf9030a21",
        "COMMONS_BOLORAKNER_PNG": "42b912dfa17a47985a6441383bba39fbc12f1e9ee6ac9f62dc20c210c4688275",
        "SHIRAKATSI_1979_SCAN": "68322110bf8c18caacb0b6ed27cdde3ad21497314f8cec8bad273a1d542adbee",
        "AUA_1979_EDITORIAL_NOTE": "33dfeb4e08bc4d13970642888badbb1d251fcc6f962c876a0a8c093c7289578a",
    }
    by_source = {x["source_id"]: x for x in sources}
    ck("source_count", len(sources) == 6)
    ck("source_ids", set(by_source) == set(expected_hashes))
    ck("source_hashes", all(by_source[k]["remote_sha256"] == v for k, v in expected_hashes.items()))
    ck("source_urls_https", all(x["url"].startswith("https://") for x in sources))
    ck("commons_not_semantic", by_source["COMMONS_BOLORAKNER_PNG"]["use"] == "PROVENANCE_AUDIT_ONLY_NOT_SEMANTIC_EVIDENCE")

    by_claim = {x["claim_id"]: x for x in attribution}
    ck("claim_count", len(attribution) == 6 and len(by_claim) == 6)
    ck("same_surface_supported", by_claim["A01_SAME_SURFACE"]["support_status"] == "SUPPORTED_DIRECT_VISUAL_IDENTITY")
    ck("caption_supported", by_claim["A02_PRINTED_ATTRIBUTION"]["support_status"] == "SUPPORTED_SECONDARY_SOURCE_CAPTION")
    ck("caption_armenian_bound", "Անանիա Շիրակացու կազմած բոլորակներից" in by_claim["A02_PRINTED_ATTRIBUTION"]["support"])
    ck("moon_phase_not_supported", by_claim["A03_MOON_PHASE_LABEL"]["support_status"] == "UNSUPPORTED_BY_PRINTED_CAPTION" and by_claim["A03_MOON_PHASE_LABEL"]["semantic_eligibility"] == "NO")
    ck("lunar_context_not_keyed", by_claim["A04_ARTICLE_LUNAR_CONTEXT"]["support_status"] == "SUPPORTED_ARTICLE_LEVEL_NOT_FIGURE_KEYED")
    ck("catalogue_conflict", by_claim["A05_CATALOGUE_RANGE"]["semantic_eligibility"] == "CONFLICT_UNRESOLVED")
    ck("same_surface_not_independent", by_claim["A06_INDEPENDENT_HOMOLOGUE"]["support_status"] == "CONTRADICTED_SAME_SURFACE_REPRODUCTION")

    by_landmark = {x["landmark_id"]: x for x in landmarks}
    ck("landmark_count", len(landmarks) == 5 and len(by_landmark) == 5)
    ck("landmark_exact", all(x["match"].startswith("EXACT_") for x in landmarks))
    ck("lower_text_landmark", by_landmark["L05_LOWER_TEXT"]["match"] == "EXACT_SURFACE_REPRODUCTION")

    by_edition = {x["observation_id"]: x for x in edition}
    ck("edition_count", len(edition) == 5 and len(by_edition) == 5)
    ck("edition_sweep", by_edition["E01_COMPLETE_SCAN"]["pdf_surfaces"] == "1-401")
    ck("edition_no_ocr_provenance", all(x["provenance"] == "AI_DIRECT_EXTERNAL_VISUAL_OBSERVATION" for x in edition))
    ck("lunar_section_context", by_edition["E02_LUNAR_SECTION_START"]["slot_key_support"] == "LUNAR_CONTEXT_ONLY")
    ck("other_topologies", all(by_edition[k]["slot_key_support"] == "COUNTEREXAMPLE_DIFFERENT_TOPOLOGY" for k in ("E03_NUMERIC_ORBIT_FIGURE", "E04_ANNULAR_TABLE_FACSIMILE", "E05_RADIAL_TABLE_FACSIMILE")))

    by_capacity = {x["requirement_id"]: x for x in capacity}
    ck("capacity_count", len(capacity) == 6 and len(by_capacity) == 6)
    ck("zero_alignment_eligible", all(x["alignment_eligible"] == "NO" for x in capacity))
    ck("surface_present_only", by_capacity["K01_EXACT_SURFACE_PROVENANCE"]["status"] == "PRESENT")
    ck("function_absent", by_capacity["K02_EXACT_DIAGRAM_FUNCTION"]["status"] == "ABSENT")
    ck("key_parts_absent", all(by_capacity[k]["status"] == "ABSENT" for k in ("K03_SLOT_VALUES", "K04_START_DIRECTION_ORDER", "K05_INDEPENDENT_WITNESS")))
    ck("system_context_only", by_capacity["K06_LUNAR_SYSTEM_CONTEXT"]["status"] == "PRESENT_NOT_FIGURE_KEYED")
    ck("counter_count", len(counter) == 5)
    ck("commons_counterexample", any(x["counterexample_id"] == "CE01_COMMONS_GLOSS" and "uploader-authored" in x["evidence"] for x in counter))

    ck("result_schema", result["schema"] == "GDT358_SHIRAKATSI_BOLORAK_ATTRIBUTION_V1")
    ck("result_status", result["status"] == "SAME_SURFACE_ANANIA_BOLORAK_ATTRIBUTION_NO_PHASE_OR_SLOT_KEY")
    ck("result_counts", result["counts"] == {"external_sources":6,"attribution_claims":6,"manual_landmark_rows":5,"edition_visual_rows":5,"edition_pdf_surfaces":401,"key_requirements":6,"key_requirements_alignment_eligible":0})
    findings = result["findings"]
    ck("same_surface_true", findings["same_penn_surface_reproduced_in_1974_encyclopedia"] is True)
    ck("printed_attribution_true", findings["printed_caption_attributes_bolorak_to_shirakatsi"] is True)
    ck("printed_phase_false", findings["printed_caption_says_moon_phases"] is False)
    ck("uploader_gloss_true", findings["commons_moon_phase_gloss_is_uploader_metadata"] is True)
    ck("no_parallel_key_score", findings["independent_parallel_witness_found"] is False and findings["folio_specific_slot_key_found"] is False and findings["voynich_target_scored"] is False)
    ck("no_ocr", findings["ocr_or_automated_text_recognition_used"] is False)
    access = result["source_access"]
    ck("external_access", access["external_manuscript_image_inspected"] is True and access["external_encyclopedia_page_inspected"] is True and access["external_collected_edition_inspected"] is True)
    ck("no_voynich_image", access["voynich_images_opened"] is False)
    ck("no_voynich_formal", access["voynich_transcription_or_formal_payload_opened"] is False)
    ck("no_f84", access["f84_rows_or_images_accessed"] is False)
    ck("remote_hash_binding", result["remote_source_hashes"] == expected_hashes)

    gdt355 = ROOT / "experiments/yolo/gdt355_ljs443_diagram_series_census/artifacts/gdt355_result.json"
    gdt357 = ROOT / "experiments/yolo/gdt357_sarkawag_source_access/artifacts/gdt357_result.json"
    ck("input_hashes", result["inputs"] == {str(p.relative_to(ROOT)): sha(p) for p in (gdt355, gdt357)})
    for rel, digest in result["outputs"].items():
        ck("output_hash:" + rel, sha(ROOT / rel) == digest)
    for rel, digest in result["documents"].items():
        ck("document_hash:" + rel, sha(ROOT / rel) == digest)
    for rel, digest in result["implementation"].items():
        ck("implementation_hash:" + rel, sha(ROOT / rel) == digest)
    content = dict(result)
    claimed = content.pop("result_content_sha256")
    ck("content_hash", hashlib.sha256(stable(content)).hexdigest() == claimed)

    joined = "\n".join("\t".join(x.values()) for table in (sources, attribution, landmarks, edition, capacity, counter) for x in table).lower()
    ck("no_voynich_target_reference", all(term not in joined for term in ("f68v3", "voynich token", "voynich tuple")))
    ck("no_f84_reference", "f84" not in joined)

    failed = sum(not x["pass"] for x in checks)
    validation = {
        "experiment": "GDT358",
        "schema": "GDT358_VALIDATION_V1",
        "status": "PASS" if not failed else "FAIL",
        "scope": "Nonimporting reconstruction of fixed source IDs/digests, caption-vs-uploader provenance, same-surface landmark records, edition scope, capacity decisions, bindings, and seal assertions. Remote bytes and direct visual identity are not independently re-fetched or re-reviewed.",
        "checks_passed": len(checks) - failed,
        "checks_failed": failed,
        "checks": checks,
        "result_sha256": sha(result_path),
        "implementation_sha256": sha(Path(__file__)),
    }
    (ART / "gdt358_validation.json").write_bytes(stable(validation))
    print(validation["status"], validation["checks_passed"], validation["checks_failed"])
    raise SystemExit(1 if failed else 0)


if __name__ == "__main__":
    main()
