#!/usr/bin/env python3
"""Validate the creative integrated workshop casebook."""

from __future__ import annotations

import csv
import hashlib
import json
import subprocess
import sys
from collections import Counter
from pathlib import Path


OUT = Path(__file__).resolve().parent
ROOT = Path(__file__).resolve().parents[3]
PROSE = ROOT / "experiments/yolo/sidequest_semantic_bound_carrier_closure"
ASTRO = ROOT / "experiments/yolo/sidequest_semantic_astro_instrument_readings"


def rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    checks: list[dict[str, object]] = []

    def check(name: str, condition: bool, detail: object) -> None:
        checks.append({"check": name, "pass": bool(condition), "detail": detail})

    dossiers = rows(OUT / "FOUR_WORKSHOP_DOSSIERS.tsv")
    steps = rows(OUT / "WORKFLOW_STEPS.tsv")
    pages = rows(OUT / "TEN_PAGE_USAGE_MAP.tsv")
    context = rows(OUT / "TEN_PAGE_776_CASE_CONTEXT.tsv")
    rules = rows(OUT / "WORKSHOP_RULES.tsv")
    source_context = rows(ASTRO / "TEN_PAGE_776_INSTRUMENT_CONTEXT.tsv")
    source_phrases = rows(PROSE / "CLOSED_116_PHRASES.tsv")
    source_events = rows(PROSE / "CLOSED_381_EVENT_INTERLINEAR.tsv")
    source_loci = rows(ASTRO / "ASTRO_142_OPERATIONAL_LOCI.tsv")
    source_modules = rows(ASTRO / "FOURTEEN_INSTRUMENT_MODULES.tsv")

    check("four_dossiers", len(dossiers) == 4, len(dossiers))
    check("eleven_records_partitioned", len({x for d in dossiers for x in d["record_units"].split(";")}) == 11, [d["record_units"] for d in dossiers])
    check("fourteen_modules_partitioned", len({x for d in dossiers for x in d["astro_modules"].split(";")}) == 14, [d["astro_modules"] for d in dossiers])
    check("116_source_statements", len(source_phrases) == 116, len(source_phrases))
    check("381_source_events", len(source_events) == 381, len(source_events))
    check("142_source_loci", len(source_loci) == 142, len(source_loci))
    check("395_source_astro_groups", sum(int(r["group_count"]) for r in source_loci) == 395, sum(int(r["group_count"]) for r in source_loci))
    check("14_source_modules", len(source_modules) == 14, len(source_modules))
    check("776_context_rows", len(context) == 776 == len(source_context), len(context))
    check("unified_serial_exact", [r["unified_serial"] for r in context] == [r["unified_serial"] for r in source_context], "ordered identity")

    source_fields = list(source_context[0])
    check("source_context_preserved", all(all(a[k] == b[k] for k in source_fields) for a, b in zip(context, source_context)), "all original columns byte-values equal")
    check("one_dossier_each", all(r["dossier_id"] and ";" not in r["dossier_id"] for r in context), Counter(r["dossier_id"] for r in context))
    check("phase_counts", Counter(r["case_phase"] for r in context) == Counter({"WHAT": 100, "HOW": 281, "WHEN": 395}), Counter(r["case_phase"] for r in context))
    check("all_ten_pages", {r["page"] for r in pages} == {"f10r", "f11r", "f55v", "f56r", "f81v", "f82r", "f83r", "f67r2", "f68r1", "f69v"}, [r["page"] for r in pages])
    check("ten_page_rows", len(pages) == 10, len(pages))
    check("all_pages_used", all(r["usage_status"] == "USED_IN_COMPLETE_CASEBOOK" for r in pages), "all used")

    check("dossier_statement_sum", sum(int(r["prose_statement_count"]) for r in dossiers) == 116, sum(int(r["prose_statement_count"]) for r in dossiers))
    check("dossier_event_sum", sum(int(r["prose_event_count"]) for r in dossiers) == 381, sum(int(r["prose_event_count"]) for r in dossiers))
    check("dossier_locus_sum", sum(int(r["astro_locus_count"]) for r in dossiers) == 142, sum(int(r["astro_locus_count"]) for r in dossiers))
    check("dossier_astro_group_sum", sum(int(r["astro_group_count"]) for r in dossiers) == 395, sum(int(r["astro_group_count"]) for r in dossiers))
    check("dossier_total_group_sum", sum(int(r["total_group_count"]) for r in dossiers) == 776, sum(int(r["total_group_count"]) for r in dossiers))
    check("25_unit_steps", len(steps) == 25, len(steps))
    check("step_source_units_unique", len({r["source_unit"] for r in steps}) == 25, len({r["source_unit"] for r in steps}))
    check("18_manual_rules", len(rules) == 18, len(rules))
    check("rule_ids", [r["rule_id"] for r in rules] == [f"R{i:02d}" for i in range(1, 19)], [r["rule_id"] for r in rules])

    for filename in ["INTEGRATED_WORKSHOP_CASEBOOK_REPORT.md", "MASTER_WORKSHOP_MANUAL.md", "FOUR_COMPLETE_WORKSHOP_CASES.md"]:
        text = (OUT / filename).read_text(encoding="utf-8")
        lowered = text.lower()
        link_terms = ("querverweis", "seitenverweis", "manuskriptlink", "aufeinander verweisen")
        check(f"{filename}_explicit_scenario_caveat", "kein" in lowered and any(term in lowered for term in link_terms), "caveat present")
        check(f"{filename}_no_sealed_page", "f84" not in text.lower(), "sealed pages absent")

    content_files = [
        "FOUR_WORKSHOP_DOSSIERS.tsv", "WORKFLOW_STEPS.tsv", "TEN_PAGE_USAGE_MAP.tsv", "TEN_PAGE_776_CASE_CONTEXT.tsv",
        "MASTER_WORKSHOP_MANUAL.md", "FOUR_COMPLETE_WORKSHOP_CASES.md", "INTEGRATED_WORKSHOP_CASEBOOK_REPORT.md", "WORKSHOP_RULES.tsv",
    ]
    all_text = "\n".join((OUT / name).read_text(encoding="utf-8", errors="replace") for name in content_files)
    check("no_sealed_tokens_anywhere", "f84" not in all_text.lower(), "none")

    tracked_outputs = [
        "FOUR_WORKSHOP_DOSSIERS.tsv", "WORKFLOW_STEPS.tsv", "TEN_PAGE_USAGE_MAP.tsv", "TEN_PAGE_776_CASE_CONTEXT.tsv",
        "MASTER_WORKSHOP_MANUAL.md", "FOUR_COMPLETE_WORKSHOP_CASES.md", "INTEGRATED_WORKSHOP_CASEBOOK_REPORT.md", "WORKSHOP_RULES.tsv",
    ]
    before = {name: digest(OUT / name) for name in tracked_outputs}
    subprocess.run([sys.executable, str(OUT / "build_integrated_workshop_casebook.py")], cwd=ROOT, check=True)
    after = {name: digest(OUT / name) for name in tracked_outputs}
    check("deterministic_rebuild", before == after, {"before": before, "after": after})

    passed = all(bool(item["pass"]) for item in checks)
    result = {
        "status": "PASS" if passed else "FAIL",
        "checks_passed": sum(bool(item["pass"]) for item in checks),
        "checks_total": len(checks),
        "checks": checks,
        "counts": {"dossiers": 4, "records": 11, "statements": 116, "prose_events": 381,
                   "astro_modules": 14, "astro_loci": 142, "astro_groups": 395, "unified_groups": 776, "pages": 10},
    }
    (OUT / "VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if not passed:
        for item in checks:
            if not item["pass"]:
                print(f"FAIL {item['check']}: {item['detail']}")
        raise SystemExit(1)
    print(f"PASS {result['checks_passed']}/{result['checks_total']}")


if __name__ == "__main__":
    main()
