#!/usr/bin/env python3
"""Validate V76 R3 scope, coverage, symmetry and semantic ceiling."""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
OUT = HERE / "V76_R3_VALIDATION.json"


def load_tsv(name: str) -> list[dict[str, str]]:
    with (HERE / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


checks: list[dict[str, object]] = []


def check(name: str, condition: bool, detail: object) -> None:
    checks.append({"check": name, "pass": bool(condition), "detail": detail})


def main() -> None:
    units = load_tsv("V76_R3_14_UNIT_DUAL_PURPOSE.tsv")
    rubric = load_tsv("V76_R3_SYMMETRIC_PURPOSE_RUBRIC.tsv")
    graph = load_tsv("V76_R3_PROCESS_OWNERSHIP_GRAPH.tsv")
    contradictions = load_tsv("V76_R3_CONTRADICTIONS.tsv")
    summary = json.loads((HERE / "V76_R3_BUILD_SUMMARY.json").read_text(encoding="utf-8"))
    report = (HERE / "V76_R3_TECHNICAL_BOOK_PURPOSE_REPORT.md").read_text(encoding="utf-8")

    check("unit_row_count", len(units) == 14, len(units))
    check("unit_ids", {r["unit_id"] for r in units} == {f"H{i}" for i in range(1, 6)} | {f"B{i}" for i in range(1, 7)} | {f"A{i}" for i in range(1, 4)}, sorted(r["unit_id"] for r in units))
    check("ten_page_scope", {r["page"] for r in units} == {"f10r", "f11r", "f55v", "f56r", "f81v", "f82r", "f83r", "f67r2", "f68r1", "f69v"}, sorted({r["page"] for r in units}))
    check("sealed_pages_absent_from_units", not ({"f84", "f84r"} & {r["page"] for r in units}), sorted({r["page"] for r in units}))
    check("total_776", sum(int(r["group_count"]) for r in units) == 776, sum(int(r["group_count"]) for r in units))
    for section, expected in (("HERBAL", 100), ("BIOLOGICAL", 281), ("ASTRO", 395)):
        actual = sum(int(r["group_count"]) for r in units if r["section"] == section)
        check(f"section_total_{section.lower()}", actual == expected, actual)
    check("all_unit_cells_complete", all(all(value.strip() for value in row.values()) for row in units), "no blank cell")
    check("both_readings_every_unit", all(r["medical_reading"] and r["nonmedical_reading"] for r in units), "14/14 dual")
    check("same_owner_frame_both_models", all(r["smallest_owner_or_namespace"] and r["shared_formal_machine"] for r in units), "one shared owner column")
    check("no_portable_gloss_promoted", all(r["portable_dictionary_status"] == "NO_PORTABLE_GLOSS_ASSERTED__EXEMPLAR_VALUE_UNKNOWN" for r in units), "14/14 unknown")
    check("interpretation_ceiling_present", all("NO_WORD_STEM_SOUND_LANGUAGE" in r["interpretation_ceiling"] for r in units), "14/14")

    score_labels = ("image_fit", "owner_fit", "local_fit", "purpose_fit", "period_fit", "unsupported_cost", "geometry_cost", "attestation_cost")
    for model in ("medical", "nonmedical"):
        check(f"{model}_scores_in_range", all(0 <= int(r[f"{model}_{label}_0_4"]) <= 4 for r in units for label in score_labels), "0..4")
        for row in units:
            expected = (
                2 * int(row[f"{model}_image_fit_0_4"])
                + 2 * int(row[f"{model}_owner_fit_0_4"])
                + 2 * int(row[f"{model}_local_fit_0_4"])
                + 2 * int(row[f"{model}_purpose_fit_0_4"])
                + int(row[f"{model}_period_fit_0_4"])
                - 2 * int(row[f"{model}_unsupported_cost_0_4"])
                - 2 * int(row[f"{model}_geometry_cost_0_4"])
                - 4 * int(row[f"{model}_attestation_cost_0_4"])
            )
            check(f"score_formula_{model}_{row['unit_id']}", int(row[f"{model}_local_score"]) == expected, expected)

    medical_local = sum(int(r["medical_local_score"]) for r in units)
    nonmedical_local = sum(int(r["nonmedical_local_score"]) for r in units)
    check("local_totals", (medical_local, nonmedical_local) == (398, 404), [medical_local, nonmedical_local])
    check("astro_local_nonmedical_lead_only", all((r["local_score_lead"].startswith("ILLUSTRATED_MATERIAL") if r["section"] == "ASTRO" else r["local_score_lead"] == "TIE") for r in units), "H/B tie; A nonmedical")

    check("rubric_row_count", len(rubric) == 12, len(rubric))
    check("rubric_symmetric_columns", all(r["medical_score_0_4"] != "" and r["nonmedical_score_0_4"] != "" and r["symmetric_reason"] for r in rubric), "12/12")
    for row in rubric:
        sign = 1 if row["polarity"] == "BENEFIT" else -1
        check(f"rubric_formula_{row['rubric_id']}_medical", int(row["medical_weighted_contribution"]) == sign * int(row["weight"]) * int(row["medical_score_0_4"]), row["medical_weighted_contribution"])
        check(f"rubric_formula_{row['rubric_id']}_nonmedical", int(row["nonmedical_weighted_contribution"]) == sign * int(row["weight"]) * int(row["nonmedical_score_0_4"]), row["nonmedical_weighted_contribution"])
    medical_global = sum(int(r["medical_weighted_contribution"]) for r in rubric)
    nonmedical_global = sum(int(r["nonmedical_weighted_contribution"]) for r in rubric)
    check("whole_book_totals", (medical_global, nonmedical_global) == (53, 49), [medical_global, nonmedical_global])

    check("graph_nonempty", len(graph) == 27, len(graph))
    check("graph_has_all_unit_owner_edges", sum(r["relation"] == "OWNS_ALL_LISTED_GROUPS_IN_UNIT" for r in graph) == 14, sum(r["relation"] == "OWNS_ALL_LISTED_GROUPS_IN_UNIT" for r in graph))
    check("graph_has_both_purpose_chains", {r["model_scope"] for r in graph} >= {summary["medical_model"], summary["nonmedical_model"]}, sorted({r["model_scope"] for r in graph}))
    check("graph_semantic_guard", all("NO_CARD_GLOSS" in r["semantic_status"] for r in graph), "27/27")
    check("contradiction_count", len(contradictions) == 14, len(contradictions))
    check("contradictions_cover_both", all(r["burdens_model"] in {"BOTH", "MEDICAL", "NONMEDICAL"} for r in contradictions), sorted({r["burdens_model"] for r in contradictions}))
    check("contradiction_guards_complete", all(r["required_guard_or_repair"] and r["status"] for r in contradictions), "14/14")

    for phrase in (
        "PURPOSE_UNRESOLVED__NONMEDICAL_LOCAL_ECONOMY__MEDICAL_CROSS_SECTION_COHESION",
        "776/776",
        "Gemeinsame formale Maschine",
        "Rekonstruierte Herstellung",
        "Mehrere Haende",
        "Masterexemplar",
        "PROVISIONAL_UNATTESTED_MNEMONIC",
        "f84 und f84r blieben versiegelt",
    ):
        check(f"report_contains_{phrase[:24]}", phrase in report, phrase)

    check("summary_zero_new_words", summary["portable_dictionary_words_added"] == 0 and summary["confirmed_translations_added"] == 0, [summary["portable_dictionary_words_added"], summary["confirmed_translations_added"]])
    check("summary_sealed_both", summary["sealed"] == ["f84", "f84r"], summary["sealed"])
    check("summary_decision", summary["decision"] == "PURPOSE_UNRESOLVED__NONMEDICAL_LOCAL_ECONOMY__MEDICAL_CROSS_SECTION_COHESION", summary["decision"])
    for name, expected in summary["output_sha256"].items():
        actual = hashlib.sha256((HERE / name).read_bytes()).hexdigest()
        check(f"hash_{name}", actual == expected, actual)

    passed = sum(bool(item["pass"]) for item in checks)
    payload = {
        "round": "V76_R3",
        "status": "PASS" if passed == len(checks) else "FAIL",
        "checks_passed": passed,
        "checks_total": len(checks),
        "scope": {"units": len(units), "groups": sum(int(r["group_count"]) for r in units), "pages": len({r["page"] for r in units})},
        "decision": summary["decision"],
        "checks": checks,
    }
    OUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({key: payload[key] for key in ("round", "status", "checks_passed", "checks_total", "scope", "decision")}, ensure_ascii=False, indent=2))
    if payload["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
