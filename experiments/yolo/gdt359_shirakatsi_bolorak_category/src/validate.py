#!/usr/bin/env python3
"""Nonimporting integrity validation for GDT359."""
from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
EXP = ROOT / "experiments/yolo/gdt359_shirakatsi_bolorak_category"
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

    sources = rows("gdt359_external_sources.tsv")
    visual = rows("gdt359_visual_census.tsv")
    terms = rows("gdt359_term_comparison.tsv")
    caveats = rows("gdt359_attribution_caveats.tsv")
    capacity = rows("gdt359_key_capacity.tsv")
    counter = rows("gdt359_counterexamples.tsv")
    result_path = ART / "gdt359_result.json"
    result = json.loads(result_path.read_text(encoding="utf-8"))

    expected_hashes = {
        "SHIRAKATSI_1958_MONOGRAPH": "f1baa1793e614cd488d1b00acc4443491ce9c27c12914b34055cbe9622eb9f22",
        "SHIRAKATSI_1962_BIBLIOGRAPHIC_RECORD": "56f438e15ea5b9e556b45108a1b1aa52921392e69b718596f94c77cc43a142af",
        "TUMANIAN_1971_ATTRIBUTION_STUDY": "46ce69f7474a60e80b9038120cf058935f562c628019ac81607b677ccc9af27c",
        "SHIRAKATSI_1979_COLLECTED_EDITION": "68322110bf8c18caacb0b6ed27cdde3ad21497314f8cec8bad273a1d542adbee",
    }
    by_source = {x["source_id"]: x for x in sources}
    ck("source_count", len(sources) == 4 and len(by_source) == 4)
    ck("source_ids", set(by_source) == set(expected_hashes))
    ck("source_hashes", all(by_source[k]["remote_sha256"] == v for k, v in expected_hashes.items()))
    ck("source_urls_https", all(x["url"].startswith("https://") for x in sources))
    ck("bibliography_not_content", by_source["SHIRAKATSI_1962_BIBLIOGRAPHIC_RECORD"]["use"] == "BIBLIOGRAPHIC_EXISTENCE_AND_SCOPE_ONLY_NOT_EDITION_CONTENT")

    by_visual = {x["observation_id"]: x for x in visual}
    ck("visual_count", len(visual) == 3 and len(by_visual) == 3)
    ck("visual_provenance", all(x["provenance"] == "AI_DIRECT_EXTERNAL_VISUAL_OBSERVATION" for x in visual))
    ck("complete_scan_scope", by_visual["V01_COMPLETE_1958_SCAN"]["scan_surface"] == "1-75")
    ck("captioned_surface", by_visual["V03_CAPTIONED_CALENDRICAL_BOLORAK"]["scan_surface"] == "43")
    ck("distinct_topology", by_visual["V03_CAPTIONED_CALENDRICAL_BOLORAK"]["interpretive_limit"] == "SOURCE_CAPTIONED_BOLORAK_DIFFERENT_TOPOLOGY")

    by_term = {x["comparison_id"]: x for x in terms}
    ck("term_count", len(terms) == 3 and len(by_term) == 3)
    ck("1958_caption_exact", by_term["T01_1958_CAPTION"]["printed_armenian"] == "Շիրակացու տոմարական բոլորակներից մեկը")
    ck("1974_caption_exact", by_term["T02_1974_CAPTION_INHERITED"]["printed_armenian"] == "Անանիա Շիրակացու կազմած բոլորակներից։")
    ck("shared_term", by_term["T03_CATEGORY_TEST"]["printed_armenian"] == "բոլորակներից")
    ck("category_inference", by_term["T03_CATEGORY_TEST"]["inference"] == "CATEGORY_WORD_DOES_NOT_KEY_EIGHT_COMPARTMENTS_OR_PHASES")

    by_caveat = {x["caveat_id"]: x for x in caveats}
    ck("caveat_count", len(caveats) == 4 and len(by_caveat) == 4)
    ck("tumanian_bounded", by_caveat["A02_TUMANIAN_CORRECTION"]["scope"] == "ATTRIBUTION_WARNING_NOT_F209R_REFUTATION")
    ck("scan_not_acquired", by_caveat["A03_1962_SCAN_NOT_ACQUIRED"]["scope"] == "NO_DIRECT_1962_FIGURE_CENSUS_CLAIM")

    by_capacity = {x["requirement_id"]: x for x in capacity}
    ck("capacity_count", len(capacity) == 5 and len(by_capacity) == 5)
    ck("zero_alignment_eligible", all(x["alignment_eligible"] == "NO" for x in capacity))
    ck("category_present", by_capacity["K01_CATEGORY_SCOPE"]["status"] == "PRESENT")
    ck("key_absent", all(by_capacity[k]["status"] == "ABSENT" for k in ("K02_EXACT_FUNCTION", "K03_SLOT_VALUES", "K04_START_DIRECTION_ORDER", "K05_INDEPENDENT_KEYED_WITNESS")))
    ck("counter_count", len(counter) == 5)
    ck("different_topology_counter", any(x["counterexample_id"] == "CE01_DIFFERENT_BOLORAK_TOPOLOGY" for x in counter))

    ck("result_schema", result["schema"] == "GDT359_SHIRAKATSI_BOLORAK_CATEGORY_V1")
    ck("result_status", result["status"] == "BOLORAK_CATEGORY_BROADENED_NO_FIGURE_KEY")
    ck("result_counts", result["counts"] == {"external_sources":4,"visual_observations":3,"term_comparisons":3,"attribution_caveats":4,"key_requirements":5,"key_requirements_alignment_eligible":0,"monograph_scan_surfaces":75,"monograph_printed_pages":132})
    findings = result["findings"]
    ck("category_broadened", findings["same_bolorak_vocabulary_spans_distinct_published_topologies"] is True and findings["bolorak_is_eight_compartment_specific"] is False)
    ck("no_key_or_witness", findings["exact_penn_function_found"] is False and findings["exact_penn_slot_key_found"] is False and findings["independent_exact_witness_found"] is False)
    ck("no_1962_scan", findings["public_1962_scan_acquired"] is False)
    ck("no_target_score", findings["voynich_target_scored"] is False)
    ck("no_ocr", findings["ocr_or_automated_text_recognition_used"] is False)
    access = result["source_access"]
    ck("external_access", access["external_monograph_scan_inspected"] is True and access["external_article_and_bibliography_inspected"] is True)
    ck("no_voynich_access", access["voynich_images_opened"] is False and access["voynich_transcription_or_formal_payload_opened"] is False)
    ck("no_f84", access["f84_rows_or_images_accessed"] is False)
    ck("remote_hash_binding", result["remote_source_hashes"] == expected_hashes)

    gdt358 = ROOT / "experiments/yolo/gdt358_shirakatsi_bolorak_attribution/artifacts/gdt358_result.json"
    ck("input_hash", result["inputs"] == {str(gdt358.relative_to(ROOT)): sha(gdt358)})
    for rel, digest in result["outputs"].items():
        ck("output_hash:" + rel, sha(ROOT / rel) == digest)
    for rel, digest in result["documents"].items():
        ck("document_hash:" + rel, sha(ROOT / rel) == digest)
    for rel, digest in result["implementation"].items():
        ck("implementation_hash:" + rel, sha(ROOT / rel) == digest)
    content = dict(result)
    claimed = content.pop("result_content_sha256")
    ck("content_hash", hashlib.sha256(stable(content)).hexdigest() == claimed)

    joined = "\n".join("\t".join(x.values()) for table in (sources, visual, terms, caveats, capacity, counter) for x in table).lower()
    ck("no_voynich_target", all(term not in joined for term in ("f68v3", "voynich token", "voynich tuple")))
    ck("no_f84_reference", "f84" not in joined)

    failed = sum(not x["pass"] for x in checks)
    validation = {
        "experiment": "GDT359",
        "schema": "GDT359_VALIDATION_V1",
        "status": "PASS" if not failed else "FAIL",
        "scope": "Nonimporting reconstruction of fixed source IDs/digests, caption text, topology distinctions, bounded attribution caveats, key-capacity decisions, bindings, and seal assertions. Remote bytes and direct visual observations are not independently re-fetched or re-reviewed.",
        "checks_passed": len(checks) - failed,
        "checks_failed": failed,
        "checks": checks,
        "result_sha256": sha(result_path),
        "implementation_sha256": sha(Path(__file__)),
    }
    (ART / "gdt359_validation.json").write_bytes(stable(validation))
    print(validation["status"], validation["checks_passed"], validation["checks_failed"])
    raise SystemExit(1 if failed else 0)


if __name__ == "__main__":
    main()
