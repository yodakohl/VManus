#!/usr/bin/env python3
"""Validate the creative cross-dossier workshop macro grammar."""

from __future__ import annotations

import csv
import hashlib
import json
import re
import subprocess
import sys
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
PROSE = ROOT / "experiments/yolo/sidequest_semantic_bound_carrier_closure"
CASEBOOK = ROOT / "experiments/yolo/sidequest_semantic_integrated_workshop_casebook"


def rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    checks: list[dict[str, object]] = []

    def check(name: str, condition: bool, detail: object) -> None:
        checks.append({"check": name, "pass": bool(condition), "detail": detail})

    macros = rows(OUT / "TEN_WORKSHOP_MACROS.tsv")
    cards = rows(OUT / "CARD_MACRO_LEXICON.tsv")
    portable = rows(OUT / "CROSS_DOSSIER_PORTABLE_CORE.tsv")
    statements = rows(OUT / "STATEMENT_MACRO_PARSES.tsv")
    transitions = rows(OUT / "MACRO_TRANSITIONS.tsv")
    usage = rows(OUT / "MACRO_USAGE_SUMMARY.tsv")
    source_cards = rows(PROSE / "CLOSED_173_CARD_DICTIONARY.tsv")
    source_events = rows(PROSE / "CLOSED_381_EVENT_INTERLINEAR.tsv")
    source_phrases = rows(PROSE / "CLOSED_116_PHRASES.tsv")
    dossiers = rows(CASEBOOK / "FOUR_WORKSHOP_DOSSIERS.tsv")
    case_context = rows(CASEBOOK / "TEN_PAGE_776_CASE_CONTEXT.tsv")

    macro_ids = [f"M{i:02d}" for i in range(10)]
    check("ten_macros", len(macros) == 10, len(macros))
    check("macro_ids_exact", [r["macro_id"] for r in macros] == macro_ids, [r["macro_id"] for r in macros])
    check("usage_has_ten", [r["macro_id"] for r in usage] == macro_ids, [r["macro_id"] for r in usage])
    check("173_cards", len(cards) == 173 == len(source_cards), len(cards))
    check("card_ids_exact", {r["joint_tuple_id"] for r in cards} == {r["joint_tuple_id"] for r in source_cards}, "same IDs")
    check("card_defaults_preserved", {r["joint_tuple_id"]: r["atomic_default_de"] for r in cards} == {r["joint_tuple_id"]: r["closed_reading_de"] for r in source_cards}, "all defaults equal")
    check("card_occurrences_sum_381", sum(int(r["occurrences"]) for r in cards) == 381, sum(int(r["occurrences"]) for r in cards))
    check("all_cards_have_macro", all(r["primary_macro"] in macro_ids[1:] and r["all_macros"] for r in cards), "all assigned")
    check("no_condition_macro_on_prose_card", all("M00" not in r["all_macros"] for r in cards), "none")
    check("41_cross_dossier_cards", len(portable) == 41, len(portable))
    check("portable_definition", all(int(r["dossier_count"]) >= 2 and r["portable_status"] in {"PORTABLE_CORE", "CROSS_DOSSIER"} for r in portable), "all cross-dossier")
    check("116_statements", len(statements) == 116 == len(source_phrases), len(statements))
    check("statement_ids_exact", {r["statement_id"] for r in statements} == {r["statement_id"] for r in source_phrases}, "same IDs")
    source_phrase_by_id = {r["statement_id"]: r for r in source_phrases}
    check("surface_sequences_preserved", all(r["surface_sequence"] == source_phrase_by_id[r["statement_id"]]["surface_sequence"] for r in statements), "all equal")
    check("fluent_clauses_preserved", all(r["normalized_master_clause_de"] == source_phrase_by_id[r["statement_id"]]["fluent_workshop_sentence_de"] for r in statements), "all equal")
    trace_count = sum(len(r["event_macro_trace"].split(" | ")) for r in statements)
    check("381_events_in_traces", trace_count == 381 == len(source_events), trace_count)
    check("all_statement_macros_valid", all(r["macro_sequence"] and set(r["macro_sequence"].split(">")) <= set(macro_ids[1:]) for r in statements), "valid")
    check("89_committed_statements", sum(r["ends_with_commit"] == "YES" for r in statements) == 89, Counter(r["ends_with_commit"] for r in statements))
    check("four_dossiers", len(dossiers) == 4, len(dossiers))
    check("statement_dossier_partition", Counter(r["dossier_id"] for r in statements) == Counter({
        "D1_ROOT_BATH_RIGHT_WHEEL": 26, "D2_CLEAR_EXTRACT_STAR_ATLAS": 26,
        "D3_STORED_APPLICATION_THREE_WHEELS": 24, "D4_FRESH_PLANT_LEFT_WHEEL": 40,
    }), Counter(r["dossier_id"] for r in statements))
    check("inherited_776_context", len(case_context) == 776, len(case_context))
    check("transitions_nonempty", len(transitions) > 20 and sum(int(r["statement_internal_count"]) for r in transitions) > 100, {"rows": len(transitions), "count": sum(int(r["statement_internal_count"]) for r in transitions)})

    masters = (OUT / "FOUR_MASTER_SOURCE_TEXTS.md").read_text(encoding="utf-8")
    report = (OUT / "WORKSHOP_MACRO_GRAMMAR_REPORT.md").read_text(encoding="utf-8")
    check("all_four_master_titles", all(r["title_de"] in masters for r in dossiers), "all present")
    check("all_116_statement_ids_in_master", all(masters.count(f"**{r['statement_id']}**") == 1 for r in statements), "exactly once")
    check("book_order_explained", "WAS (Herbal) -> WIE (Biological) -> WANN (Astro)" in report and "WANN nachschlagen -> WAS bereiten -> WIE ausführen" in report, "both orders")
    check("scenario_not_crosslink_claim", "keine behaupteten expliziten Manuskriptverweise" in report, "caveat present")

    content_names = ["TEN_WORKSHOP_MACROS.tsv", "CARD_MACRO_LEXICON.tsv", "CROSS_DOSSIER_PORTABLE_CORE.tsv",
                     "STATEMENT_MACRO_PARSES.tsv", "MACRO_TRANSITIONS.tsv", "MACRO_USAGE_SUMMARY.tsv",
                     "FOUR_MASTER_SOURCE_TEXTS.md", "WORKSHOP_MACRO_GRAMMAR_REPORT.md"]
    content = "\n".join((OUT / name).read_text(encoding="utf-8", errors="replace") for name in content_names)
    sealed_page_token = re.compile(r"(?i)(?<![a-z0-9])f84(?:r|v)?(?![a-z0-9])")
    check("sealed_pages_absent", sealed_page_token.search(content) is None, "absent")

    before = {name: digest(OUT / name) for name in content_names}
    subprocess.run([sys.executable, str(OUT / "build_workshop_macro_grammar.py")], cwd=ROOT, check=True)
    after = {name: digest(OUT / name) for name in content_names}
    check("deterministic_rebuild", before == after, {"before": before, "after": after})

    passed = all(bool(r["pass"]) for r in checks)
    result = {"status": "PASS" if passed else "FAIL", "checks_passed": sum(bool(r["pass"]) for r in checks),
              "checks_total": len(checks), "checks": checks,
              "counts": {"macros": 10, "cards": 173, "portable_cards": 41, "events": 381,
                         "statements": 116, "dossiers": 4, "inherited_unified_groups": 776}}
    (OUT / "VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if not passed:
        for item in checks:
            if not item["pass"]:
                print(f"FAIL {item['check']}: {item['detail']}")
        raise SystemExit(1)
    print(f"PASS {result['checks_passed']}/{result['checks_total']}")


if __name__ == "__main__":
    main()
