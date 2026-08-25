#!/usr/bin/env python3
"""Validate the Pass-1014 optical core rereading."""

from __future__ import annotations

import csv
import json
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
PASS1011 = ROOT / "experiments/yolo/sidequest_semantic_manual_optical_passage_audit_one_thousand_eleventh"
PASS1013 = ROOT / "experiments/yolo/sidequest_semantic_embedded_stem_resegmentation_one_thousand_thirteenth"
SOURCE_OPTICAL = PASS1011 / "PASS1011_627_OPTICALLY_REPAIRED_STATEMENTS.tsv"
SOURCE_PRESSURE = PASS1013 / "PASS1013_627_SEMANTIC_PRESSURE_MAP.tsv"


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def check(name: str, condition: bool, details: str = "") -> dict[str, object]:
    return {"name": name, "passed": bool(condition), "details": details}


def main() -> None:
    source = read(SOURCE_OPTICAL)
    pressure = read(SOURCE_PRESSURE)
    passages = read(HERE / "PASS1014_35_OPTICAL_RETRANSLATIONS.tsv")
    comparison = read(HERE / "PASS1014_CHK_CKH_COMPARISON.tsv")
    reviewed = [row for row in source if row["optical_review_status"] == "MANUALLY_REVIEWED_ORIGINAL_IMAGE"]
    source_by_id = {row["statement_id"]: row for row in reviewed}
    pressure_by_id = {row["statement_id"]: row for row in pressure}
    forbidden = (
        "durchlass", "auszug", "absetz", "abtrenn", "auffang", "spül", "befest",
        "kühl", "filter", "tuch", "seriell", "weiterbearbeit",
    )

    checks = [
        check("exactly_35_optical_statements", len(passages) == len(reviewed) == 35),
        check("same_statement_set", {r["statement_id"] for r in passages} == set(source_by_id)),
        check("unique_statement_ids", len({r["statement_id"] for r in passages}) == 35),
        check("all_retranslations_nonempty", all(r["pass1014_core_owner_translation_de"].strip() for r in passages)),
        check("all_results_complete", all(r["result"] == "CORE_RETRANSLATION_COMPLETE" for r in passages)),
        check("surface_sequences_preserved", all(r["surface_sequence"] == source_by_id[r["statement_id"]]["surface_sequence"] for r in passages)),
        check("pass1013_components_preserved", all(r["pass1013_component_sequence"] == pressure_by_id[r["statement_id"]]["component_sequence"] for r in passages)),
        check("pass1013_literals_preserved", all(r["pass1013_core_literal_de"] == pressure_by_id[r["statement_id"]]["contract_literal_de"] for r in passages)),
        check("optical_fit_preserved", all(r["optical_fit"] == source_by_id[r["statement_id"]]["optical_fit"] for r in passages)),
        check("image_sources_preserved", all(r["optical_image_source"] == source_by_id[r["statement_id"]]["optical_image_source"] for r in passages)),
        check("no_withdrawn_specialist_words_in_new_readings", not any(term in r["pass1014_core_owner_translation_de"].casefold() for r in passages for term in forbidden)),
        check("no_sealed_pages", not any("f84" in "\t".join(r.values()).casefold() for r in passages)),
        check("comparison_has_two_families", [r["legacy_token"] for r in comparison] == ["CHK", "CKH"]),
        check("chk_count_46", comparison[0]["event_count"] == "46"),
        check("ckh_count_104", comparison[1]["event_count"] == "104"),
        check("chk_token_initial_43", comparison[0]["token_position_within_event_counts"].startswith("FIRST:43|")),
        check("ckh_token_initial_33", comparison[1]["token_position_within_event_counts"].startswith("FIRST:33|")),
        check("shared_atomic_value", all(r["shared_atomic_value_de"] == "NEHMEN + GEBEN" for r in comparison)),
        check("different_topologies", len({r["surface_topology"] for r in comparison}) == 2),
        check("zero_new_specialist_roots", json.loads((HERE / "PASS1014_BUILD_SUMMARY.json").read_text())["new_specialist_roots"] == 0),
    ]

    before = {path.name: path.read_bytes() for path in HERE.glob("PASS1014_*") if path.name != "PASS1014_VALIDATION.json"}
    subprocess.run(["python3", str(HERE / "build_pass1014.py")], cwd=ROOT, check=True)
    after = {path.name: path.read_bytes() for path in HERE.glob("PASS1014_*") if path.name != "PASS1014_VALIDATION.json"}
    checks.append(check("deterministic_rebuild", before == after))

    result = {
        "status": "PASS" if all(item["passed"] for item in checks) else "FAIL",
        "check_count": len(checks),
        "checks": checks,
    }
    (HERE / "PASS1014_VALIDATION.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    if result["status"] != "PASS":
        for item in checks:
            if not item["passed"]:
                print("FAIL", item["name"], item["details"])
        raise SystemExit(1)
    print(f"PASS {len(checks)}/{len(checks)}")


if __name__ == "__main__":
    main()
