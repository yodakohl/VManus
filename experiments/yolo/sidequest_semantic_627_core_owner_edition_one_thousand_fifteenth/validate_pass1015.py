#!/usr/bin/env python3
"""Validate the complete Pass-1015 owner/core edition."""

from __future__ import annotations

import csv
import json
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
PASS1013 = ROOT / "experiments/yolo/sidequest_semantic_embedded_stem_resegmentation_one_thousand_thirteenth"
PASS1014 = ROOT / "experiments/yolo/sidequest_semantic_optical_core_retranslation_one_thousand_fourteenth"
SOURCE_STATEMENTS = PASS1013 / "PASS1013_627_SEMANTIC_PRESSURE_MAP.tsv"
SOURCE_MANUAL = PASS1014 / "PASS1014_35_OPTICAL_RETRANSLATIONS.tsv"


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def check(name: str, condition: bool) -> dict[str, object]:
    return {"name": name, "passed": bool(condition)}


def main() -> None:
    source = read(SOURCE_STATEMENTS)
    manual = read(SOURCE_MANUAL)
    edition = read(HERE / "PASS1015_627_CORE_OWNER_EDITION.tsv")
    drawers = read(HERE / "PASS1015_NINE_DRAWER_SUMMARY.tsv")
    source_by_id = {row["statement_id"]: row for row in source}
    manual_by_id = {row["statement_id"]: row for row in manual}
    edition_by_id = {row["statement_id"]: row for row in edition}
    forbidden = (
        "durchlass", "auszug", "absetz", "abtrenn", "auffang", "spül", "befest",
        "bereit", "kühl", "filter", "tuch", "weiterbearbeit",
    )

    checks = [
        check("statement_count_627", len(source) == len(edition) == 627),
        check("unique_statement_ids", len(edition_by_id) == 627),
        check("same_statement_set", set(edition_by_id) == set(source_by_id)),
        check("event_count_3888", sum(int(row["event_count"]) for row in edition) == 3888),
        check("running_statement_page_labels_20", len({row["physical_page"] for row in edition}) == 20),
        check("surface_sequence_preserved", all(row["surface_sequence"] == source_by_id[row["statement_id"]]["surface_sequence"] for row in edition)),
        check("component_sequence_preserved", all(row["component_sequence"] == source_by_id[row["statement_id"]]["component_sequence"] for row in edition)),
        check("all_semantic_signatures_complete", all(row["semantic_signature"].count(" | ") == 10 for row in edition)),
        check("all_translations_nonempty", all(row["pass1015_core_owner_translation_de"].strip() for row in edition)),
        check("all_results_complete", all(row["result"] == "COMPLETE_CORE_OWNER_READING" for row in edition)),
        check("manual_origin_count_35", sum(row["translation_origin"] == "MANUAL_PASS1014_CORE_RETRANSLATION" for row in edition) == 35),
        check("generated_origin_count_592", sum(row["translation_origin"] == "DETERMINISTIC_OWNER_CORE_COMPOSITION" for row in edition) == 592),
        check("manual_texts_preserved", all(edition_by_id[sid]["pass1015_core_owner_translation_de"] == row["pass1014_core_owner_translation_de"] for sid, row in manual_by_id.items())),
        check("nine_drawers", len(drawers) == 9 and sum(int(row["statement_count"]) for row in drawers) == 627),
        check("licensed_close_count_566", sum(row["end_mode"] == "LICENSED_DY_CLOSE" for row in edition) == 566),
        check("endpoint_close_count_566", sum(row["endpoint"] == "CLOSE" for row in edition) == 566),
        check("no_withdrawn_terms_in_new_readings", not any(term in row["pass1015_core_owner_translation_de"].casefold() for row in edition for term in forbidden)),
        check("no_sealed_page_tokens", not any("f84" in "\t".join(row.values()).casefold() for row in edition)),
        check("no_empty_channels", all(all(row[key] for key in ("quantity_channel", "action_chain", "relation_chain", "grade_channel", "local_signs", "endpoint")) for row in edition)),
        check("new_specialist_roots_zero", json.loads((HERE / "PASS1015_BUILD_SUMMARY.json").read_text())["new_specialist_roots"] == 0),
    ]

    before = {path.name: path.read_bytes() for path in HERE.glob("PASS1015_*") if path.name != "PASS1015_VALIDATION.json"}
    subprocess.run(["python3", str(HERE / "build_pass1015.py")], cwd=ROOT, check=True)
    after = {path.name: path.read_bytes() for path in HERE.glob("PASS1015_*") if path.name != "PASS1015_VALIDATION.json"}
    checks.append(check("deterministic_rebuild", before == after))

    result = {
        "status": "PASS" if all(item["passed"] for item in checks) else "FAIL",
        "check_count": len(checks),
        "checks": checks,
    }
    (HERE / "PASS1015_VALIDATION.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    if result["status"] != "PASS":
        for item in checks:
            if not item["passed"]:
                print("FAIL", item["name"])
        raise SystemExit(1)
    print(f"PASS {len(checks)}/{len(checks)}")


if __name__ == "__main__":
    main()
