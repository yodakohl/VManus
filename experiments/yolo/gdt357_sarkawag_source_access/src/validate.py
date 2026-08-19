#!/usr/bin/env python3
"""Nonimporting integrity validation for GDT357."""
from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
EXP = ROOT / "experiments/yolo/gdt357_sarkawag_source_access"
ART = EXP / "artifacts"


def stable(value: object) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False) + "\n").encode()


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_rows(name: str) -> list[dict[str, str]]:
    with (ART / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    checks: list[dict[str, object]] = []

    def ck(name: str, condition: bool, detail: str = "") -> None:
        checks.append({"name": name, "pass": bool(condition), "detail": detail})

    sources = read_rows("gdt357_external_sources.tsv")
    visual = read_rows("gdt357_edition_visual_audit.tsv")
    witnesses = read_rows("gdt357_witness_access.tsv")
    capacity = read_rows("gdt357_key_capacity.tsv")
    counter = read_rows("gdt357_counterexamples.tsv")
    result_path = ART / "gdt357_result.json"
    result = json.loads(result_path.read_text(encoding="utf-8"))

    expected_sources = {
        "ABRAHAMYAN_1956_FULL_SCAN": ("382", "b099488d34a6107447f90543d4255a6602cd1cdf4dfe7cdb2a6273132b00d302"),
        "ARMENIAN_MANUSCRIPTS_INDEX_V3": ("2579", "0c9bd071290efee1da5820e31eea1b0375e29b4da7ebcce70cd78bd6161f189a"),
        "ARMENIAN_MANUSCRIPTS_INDEX_V2": ("1363", "fc59638f7aac6d1e0354b956f60b5d0163082fadacd36bad310d24c3ac1ccb45"),
    }
    src = {x["source_id"]: x for x in sources}
    ck("source_count", len(sources) == 3)
    ck("source_ids", set(src) == set(expected_sources))
    ck("source_rows_hashes", all((src[k]["rows_or_surfaces"], src[k]["remote_sha256"]) == v for k, v in expected_sources.items()))
    ck("source_https", all(x["url"].startswith("https://") for x in sources))

    by_visual = {x["observation_id"]: x for x in visual}
    ck("visual_count", len(visual) == 5)
    ck("visual_unique", len(by_visual) == 5)
    ck("complete_sweep", by_visual["EV01_COMPLETE_SWEEP"]["pdf_surfaces"] == "1-382")
    ck("cited_range", (by_visual["EV02_KHARNAKHORAN_CITED_RANGE"]["pdf_surfaces"], by_visual["EV02_KHARNAKHORAN_CITED_RANGE"]["printed_pages"]) == ("169-200", "159-190"))
    ck("direct_provenance", all(x["provenance"] == "AI_DIRECT_EXTERNAL_VISUAL_OBSERVATION" for x in visual))
    ck("ten_cell_counterexample", "ten outer circular cells" in by_visual["EV03_ANNULAR_FIGURE"]["visible_observation"])
    ck("no_visual_key_support", not any(x["key_support"] not in {"NONE", "COUNTEREXAMPLE_TO_EIGHT_FROM_CIRCULARITY"} for x in visual))

    wit = {x["witness_id"]: x for x in witnesses}
    ck("witness_count", len(witnesses) == 4)
    ck("witness_ids", set(wit) == {"LJS443", "MM1973", "MM1999", "APIA00248"})
    ck("ljs443_present", wit["LJS443"]["index_v3_status"] == "PRESENT")
    ck("named_matenadaran_absent_v3", all(wit[k]["index_v3_status"] == "ABSENT" for k in ("MM1973", "MM1999")))
    ck("named_matenadaran_absent_v2", all(wit[k]["index_v2_status"] == "ABSENT" for k in ("MM1973", "MM1999")))
    ck("generic_parallel_not_keyed", "does not identify" in wit["APIA00248"]["public_access_implication"])

    by_capacity = {x["requirement_id"]: x for x in capacity}
    ck("capacity_count", len(capacity) == 5)
    ck("capacity_unique", len(by_capacity) == 5)
    ck("zero_alignment_eligible", all(x["alignment_eligible"] == "NO" for x in capacity))
    ck("key_absent", all(by_capacity[k]["status"].startswith("ABSENT") for k in ("K01_FOLIO_CONCORDANCE", "K02_SLOT_VALUES", "K03_START_DIRECTION_ORDER", "K04_PARALLEL_WITNESS")))
    ck("system_context_only", by_capacity["K05_PERIOD_SYSTEM_CONTEXT"]["status"] == "PRESENT_WORK_LEVEL")
    ck("counter_count", len(counter) == 4)

    ck("result_schema", result["schema"] == "GDT357_SARKAWAG_SOURCE_ACCESS_V1")
    ck("result_status", result["status"] == "CRITICAL_EDITION_RECOVERED_NO_FOLIO_KEY_OR_PUBLIC_PARALLEL")
    ck("result_counts", result["counts"] == {"external_sources":3,"edition_pdf_surfaces":382,"public_index_v3_rows":2579,"visual_audit_rows":5,"witness_rows":4,"key_requirements":5,"key_requirements_alignment_eligible":0})
    findings = result["findings"]
    ck("edition_recovered", findings["critical_edition_recovered"] is True)
    ck("no_ocr", findings["ocr_or_automated_text_recognition_used"] is False)
    ck("no_spiral_in_range", findings["eight_band_spiral_reproduced_in_cited_edition_range"] is False)
    ck("named_witnesses_absent", findings["mm1973_in_public_index_v3"] is False and findings["mm1999_in_public_index_v3"] is False)
    ck("no_key_and_no_score", findings["folio_specific_slot_key_found"] is False and findings["voynich_target_scored"] is False)
    access = result["source_access"]
    ck("external_only", access["external_edition_images_inspected"] is True and access["external_dataset_queried"] is True)
    ck("no_voynich_image", access["voynich_images_opened"] is False)
    ck("no_voynich_formal", access["voynich_transcription_or_formal_payload_opened"] is False)
    ck("no_f84_access", access["f84_rows_or_images_accessed"] is False)

    all_rows = sources + visual + witnesses + capacity + counter
    provenance_fields = "\n".join("\t".join(x.values()) for x in all_rows).lower()
    ck("no_f84_provenance", "f84" not in provenance_fields)
    ck("remote_hashes", result["remote_source_hashes"] == {x["source_id"]: x["remote_sha256"] for x in sources})

    gdt356 = ROOT / "experiments/yolo/gdt356_ljs443_work_attribution/artifacts/gdt356_result.json"
    ck("gdt356_input_hash", result["inputs"] == {str(gdt356.relative_to(ROOT)): sha(gdt356)})
    for rel, digest in result["outputs"].items():
        ck("output_hash:" + rel, sha(ROOT / rel) == digest)
    for rel, digest in result["documents"].items():
        ck("document_hash:" + rel, sha(ROOT / rel) == digest)
    for rel, digest in result["implementation"].items():
        ck("implementation_hash:" + rel, sha(ROOT / rel) == digest)
    content = dict(result)
    claimed = content.pop("result_content_sha256")
    ck("content_hash", hashlib.sha256(stable(content)).hexdigest() == claimed)

    failed = sum(not x["pass"] for x in checks)
    validation = {
        "experiment": "GDT357",
        "schema": "GDT357_VALIDATION_V1",
        "status": "PASS" if not failed else "FAIL",
        "scope": "Independent fixed source IDs/digests, visual-page scope, witness-index states, capacity decisions, bindings, and seal checks. Remote bytes and direct visual interpretation are not independently re-fetched or re-reviewed.",
        "checks_passed": len(checks) - failed,
        "checks_failed": failed,
        "checks": checks,
        "result_sha256": sha(result_path),
        "implementation_sha256": sha(Path(__file__)),
    }
    (ART / "gdt357_validation.json").write_bytes(stable(validation))
    print(validation["status"], validation["checks_passed"], validation["checks_failed"])
    raise SystemExit(1 if failed else 0)


if __name__ == "__main__":
    main()
