#!/usr/bin/env python3
"""Validate the complete R1 V67 workshop-manual artifacts."""

from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter
from pathlib import Path


OUT = Path(__file__).resolve().parent
ALLOWED_PAGES = {"f10r", "f11r", "f55v", "f56r", "f81v", "f82r", "f83r", "f67r2", "f68r1", "f69v"}
EXPECTED_UNITS = {"H1": 14, "H2": 24, "H3": 17, "H4": 18, "H5": 27, "B1": 66, "B2": 62, "B3": 86, "B4": 47, "B5": 11, "B6": 9, "A1": 190, "A2": 65, "A3": 140}
EXPECTED_PAGES = {"f10r": 38, "f11r": 17, "f55v": 18, "f56r": 27, "f81v": 66, "f82r": 62, "f83r": 153, "f67r2": 190, "f68r1": 65, "f69v": 140}
MNEMONICS = {"UNKNOWN", "MASS?", "ANWENDEN?", "BEREIT?", "ANSATZ?", "ZIEL?", "KLAR?", "VORIGES?", "ANTEIL?", "TEMPERIEREN?", "SPÜLEN?", "ABLASSEN?", "NONE_ASTRO_NAMESPACE"}


def read(name: str) -> list[dict[str, str]]:
    with (OUT / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def digest(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:20]


def check(name: str, condition: bool, detail: object, checks: list[dict[str, object]]) -> None:
    checks.append({"check": name, "status": "PASS" if condition else "FAIL", "detail": detail})
    if not condition:
        raise AssertionError(f"{name}: {detail}")


def main() -> None:
    ledger = read("V67_R1_776_COVERAGE_LEDGER.tsv")
    units = read("V67_R1_14_UNIT_ROUNDTRIP.tsv")
    traces = read("V67_R1_REPRESENTATIVE_LONG_TRACES.tsv")
    curriculum = read("V67_R1_9_LESSON_CURRICULUM.tsv")
    roles = read("V67_R1_FIVE_SCRIBE_ROLES.tsv")
    models = read("V67_R1_SOURCE_ORDER_MODEL_COMPARISON.tsv")
    errors = read("V67_R1_APPRENTICE_ERROR_REPAIRS.tsv")
    templates = read("V67_R1_SOURCE_ORDER_TEMPLATES.tsv")
    checks: list[dict[str, object]] = []

    check("coverage_rows", len(ledger) == 776, len(ledger), checks)
    check("unit_rows", len(units) == 14, len(units), checks)
    check("page_scope", {r["page"] for r in ledger} == ALLOWED_PAGES, sorted({r["page"] for r in ledger}), checks)
    check("sealed_absent", all(not r["page"].startswith("f84") for r in ledger), True, checks)
    check("serial_contiguous", [int(r["universal_group_serial"]) for r in ledger] == list(range(1, 777)), True, checks)
    check("unit_counts", dict(Counter(r["unit_id"] for r in ledger)) == EXPECTED_UNITS, dict(Counter(r["unit_id"] for r in ledger)), checks)
    check("page_counts", dict(Counter(r["page"] for r in ledger)) == EXPECTED_PAGES, dict(Counter(r["page"] for r in ledger)), checks)
    check("prose_astro_split", Counter(r["register"] for r in ledger) == {"HERBAL": 100, "BIO": 281, "ASTRO": 395}, dict(Counter(r["register"] for r in ledger)), checks)
    check("mnemonic_freeze", {r["atomic_or_whole_card_mnemonic"] for r in ledger} <= MNEMONICS, sorted({r["atomic_or_whole_card_mnemonic"] for r in ledger}), checks)
    check("all_layers_present", all(r["exact_card_or_local_group_id"] and r["formal_value"] and r["atomic_or_whole_card_mnemonic"] and r["local_selected_source_fragment"] and r["rendered_surface"] for r in ledger), True, checks)
    check("surface_semantics_not_claimed", all(r["semantic_invertibility_from_surface_alone"] == "NOT_CLAIMED" for r in ledger), True, checks)
    check("source_fragment_digests", all(r["source_fragment_digest"] == digest(r["local_selected_source_fragment"]) for r in ledger), True, checks)
    check("terminal_renderer_match", all((r["terminal_status"] == "TERMINAL" and "ATTACH_SELECTED_CLOSE" in r["renderer_instruction"]) or (r["terminal_status"] != "TERMINAL" and "KEEP_SELECTED_FIELD_NONCLOSE" in r["renderer_instruction"]) for r in ledger if r["register"] != "ASTRO"), True, checks)
    check("exact_roundtrip_status", all(r["roundtrip_status"].startswith("PASS_EXACT") for r in ledger), True, checks)
    check("astro_namespace_separate", all((r["register"] != "ASTRO") or (r["atomic_or_whole_card_mnemonic"] == "NONE_ASTRO_NAMESPACE" and r["exact_card_or_local_group_id"].startswith("ASTRO_LOCAL_ADDRESS::")) for r in ledger), True, checks)
    check("no_f68_f69_join", all("f68r1" not in r["exact_card_or_local_group_id"] or "f69v" not in r["exact_card_or_local_group_id"] for r in ledger), True, checks)
    check("unit_group_total", sum(int(r["group_count"]) for r in units) == 776, sum(int(r["group_count"]) for r in units), checks)
    check("prose_fields", sum(int(r["field_or_locus_count"]) for r in units if r["register"] != "ASTRO") == 135, True, checks)
    check("prose_statements", sum(int(r["statement_count"]) for r in units if r["register"] != "ASTRO") == 116, True, checks)
    check("astro_loci", sum(int(r["field_or_locus_count"]) for r in units if r["register"] == "ASTRO") == 142, True, checks)
    check("structured_count", sum(int(r["recognized_or_structured_groups"]) for r in units) == 119, True, checks)
    check("exemplar_count", sum(int(r["exemplar_only_groups"]) for r in units) == 657, True, checks)
    check("trace_rows", len(traces) == 253, len(traces), checks)
    check("trace_unit_counts", Counter(r["unit_id"] for r in traces) == {"H5": 27, "B3": 86, "A3": 140}, dict(Counter(r["unit_id"] for r in traces)), checks)
    check("trace_chain_complete", all(r["SOURCE_TEXT_PACKET"] and r["SLOT_PACKET"] and r["CARD_PACKET"] and r["RENDER_PACKET"] and r["REVERSE_PACKET"] for r in traces), True, checks)
    check("curriculum_size", len(curriculum) == 9, len(curriculum), checks)
    check("scribe_roles", len(roles) == 5, len(roles), checks)
    check("three_source_templates", {r["register"] for r in templates} == {"HERBAL", "BIO", "ASTRO"}, True, checks)
    check("model_comparison", len(models) == 4 and sum(r["decision"] == "SELECT" for r in models) == 1, True, checks)
    check("error_repairs", len(errors) >= 12, len(errors), checks)
    check("no_language_claim", all(r["authorial_language_or_sound_claim"] == "NONE" for r in units) and all(r["language_claim"] == "NONE" for r in models), True, checks)

    result = {
        "status": "PASS",
        "checks_passed": len(checks),
        "counts": {
            "pages": 10, "units": 14, "groups": 776, "prose_groups": 381,
            "astro_groups": 395, "fields": 135, "statements": 116,
            "astro_loci": 142, "long_trace_rows": 253,
        },
        "claims_not_made": ["phonetic value", "letter expansion", "surface-alone semantic inversion", "f68r1-to-f69v join"],
        "checks": checks,
    }
    (OUT / "V67_R1_VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": result["status"], **result["counts"], "checks_passed": len(checks)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
