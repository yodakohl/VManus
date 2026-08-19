#!/usr/bin/env python3
"""Nonimporting integrity validation for GDT356."""
from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
EXP = ROOT / "experiments/yolo/gdt356_ljs443_work_attribution"
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

    sources = rows("gdt356_external_sources.tsv")
    ranges = rows("gdt356_work_ranges.tsv")
    features = rows("gdt356_feature_audit.tsv")
    counter = rows("gdt356_counterexamples.tsv")
    result_path = ART / "gdt356_result.json"
    result = json.loads(result_path.read_text(encoding="utf-8"))

    expected_sources = {
        "PENN_LJS443_CATALOG_JSON": ("OFFICIAL_LIBRARY_CATALOGUE", "c111a97ecbdb2a6727b1ca3c67fb9ff6e1141e53ea2e3ec947c1cded43656785"),
        "PENN_LJS443_TEI": ("OFFICIAL_LIBRARY_METADATA", "becfa33a8ca1952a7c914e09d070e4d7cdd4f3509291998916a956397b8391b4"),
        "GALSTYAN_2022_SARKAWAG": ("SCHOLARLY_ARTICLE", "01e254512743c9c6a41ade8d0331668541be0b4d00e7f0e79727dbe502a5f463"),
        "BROUTIAN_2009_CALENDARS": ("SCHOLARLY_ARTICLE", "0366a3f1e9047b15126b97555600ce80c219b45c8f8dcc0696b17b915c60e718"),
    }
    src = {x["source_id"]: x for x in sources}
    ck("source_count", len(sources) == 4)
    ck("source_ids", set(src) == set(expected_sources))
    ck("source_class_and_hash", all((src[k]["source_class"], src[k]["remote_sha256"]) == v for k, v in expected_sources.items()))
    ck("source_hash_shapes", all(len(x["remote_sha256"]) == 64 for x in sources))
    ck("source_https", all(x["url"].startswith("https://") for x in sources))

    by_range = {x["range_id"]: x for x in ranges}
    ck("range_count", len(ranges) == 4)
    ck("range_ids", set(by_range) == {"R01", "R02", "R03", "R04"})
    ck("hakob_range", (by_range["R01"]["modern_folio_start"], by_range["R01"]["modern_folio_end"], by_range["R01"]["catalogued_author"]) == ("3r", "54v", "HAKOB_GHRIMETSI"))
    ck("hovhannes_range", (by_range["R02"]["modern_folio_start"], by_range["R02"]["modern_folio_end"], by_range["R02"]["catalogued_author"]) == ("145v", "212r", "HOVHANNES_VARDAPET_SARKAWAG"))
    ck("narrow_range", (by_range["R03"]["modern_folio_start"], by_range["R03"]["modern_folio_end"]) == ("209r", "210r"))
    ck("anania_range", (by_range["R04"]["modern_folio_start"], by_range["R04"]["modern_folio_end"], by_range["R04"]["catalogued_author"]) == ("213r", "244r", "ANANIA_SHIRAKATSI"))
    ck("only_hovhannes_contains", [x["range_id"] for x in ranges if x["catalogued_author"] in {"HAKOB_GHRIMETSI", "HOVHANNES_VARDAPET_SARKAWAG", "ANANIA_SHIRAKATSI"} and x["contains_narrow_gdt355_subseries"] == "YES"] == ["R02"])

    by_feature = {x["feature_id"]: x for x in features}
    statuses = [x["support_status"] for x in features]
    ck("feature_count", len(features) == 9)
    ck("feature_unique", len(by_feature) == 9)
    ck("support_vocab", set(statuses) == {"SUPPORTED_WORK_LEVEL", "SUPPORTED_SYSTEM_LEVEL_NOT_FOLIO_KEYED", "UNSUPPORTED_FOLIO_LEVEL", "CONTRADICTED_BY_RANGE"})
    ck("support_counts", (statuses.count("SUPPORTED_WORK_LEVEL"), statuses.count("SUPPORTED_SYSTEM_LEVEL_NOT_FOLIO_KEYED"), statuses.count("UNSUPPORTED_FOLIO_LEVEL"), statuses.count("CONTRADICTED_BY_RANGE")) == (2, 3, 3, 1))
    ck("zero_alignment_eligible", all(x["eligible_for_slot_alignment"] == "NO" for x in features))
    ck("work_supported", by_feature["F01_CONTAINING_WORK"]["support_status"] == "SUPPORTED_WORK_LEVEL")
    ck("anania_contradicted", by_feature["F08_ANANIA_ASTRONOMY_ITEM"]["support_status"] == "CONTRADICTED_BY_RANGE")
    ck("slot_key_unsupported", by_feature["F09_SLOT_VALUES_ORDER"]["support_status"] == "UNSUPPORTED_FOLIO_LEVEL")
    ck("eight_phase_unsupported", by_feature["F07_EIGHT_LUNAR_PHASES"]["support_status"] == "UNSUPPORTED_FOLIO_LEVEL")
    ck("counterexample_count", len(counter) == 5)
    ck("counterexample_ids", {x["counterexample_id"] for x in counter} == {"CE01_RANGE", "CE02_LUNAR_SCALE", "CE03_TABLE_FORM", "CE04_CURVED_TWELVE", "CE05_NO_REPLICATION"})

    ck("result_schema", result["schema"] == "GDT356_LJS443_WORK_ATTRIBUTION_V1")
    ck("result_status", result["status"] == "WORK_ATTRIBUTION_NARROWED_FOLIO_KEY_STILL_ABSENT")
    ck("result_folios", result["work_attribution"]["narrow_subseries_folios"] == ["209r", "209v", "210r"])
    ck("result_range", result["work_attribution"]["containing_catalogued_range"] == "145v-212r")
    ck("no_personal_diagram_authorship", result["work_attribution"]["individual_diagram_authorship_claimed"] is False)
    ck("result_counts", result["counts"] == {"external_sources":4,"catalogued_ranges":4,"audited_features":9,"supported_work_level":2,"supported_system_not_folio_keyed":3,"unsupported_folio_level":3,"contradicted_by_range":1,"features_eligible_for_slot_alignment":0})
    access = result["source_access"]
    ck("external_text_only", access["external_catalogue_and_scholarship_accessed"] is True and access["external_manuscript_images_newly_opened"] is False)
    ck("no_voynich_image", access["voynich_images_opened"] is False)
    ck("no_voynich_formal", access["voynich_transcription_or_formal_payload_opened"] is False)
    ck("no_f84_access", access["f84_rows_or_images_accessed"] is False)
    ck("no_f84_rows", all("f84" not in "\t".join(x.values()).lower() for x in ranges + features + counter))
    ck("remote_hashes", result["remote_source_hashes"] == {x["source_id"]: x["remote_sha256"] for x in sources})

    gdt355 = ROOT / "experiments/yolo/gdt355_ljs443_diagram_series_census/artifacts/gdt355_result.json"
    ck("gdt355_input_hash", result["inputs"] == {str(gdt355.relative_to(ROOT)): sha(gdt355)})
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
        "experiment": "GDT356",
        "schema": "GDT356_VALIDATION_V1",
        "status": "PASS" if not failed else "FAIL",
        "scope": "Independent fixed source IDs/digests, work ranges, support classes, counts, bindings and seal checks. Remote bytes and scholarly interpretation are not independently re-fetched or peer-reviewed.",
        "checks_passed": len(checks) - failed,
        "checks_failed": failed,
        "checks": checks,
        "result_sha256": sha(result_path),
        "implementation_sha256": sha(Path(__file__)),
    }
    (ART / "gdt356_validation.json").write_bytes(stable(validation))
    print(validation["status"], validation["checks_passed"], validation["checks_failed"])
    raise SystemExit(1 if failed else 0)


if __name__ == "__main__":
    main()
