#!/usr/bin/env python3
"""Validate Pass 910 coverage, defaults, layering, and reproducibility."""

from __future__ import annotations

import csv
import hashlib
import io
import json
import subprocess
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
BASE = Path(__file__).resolve().parent
SOURCE = ROOT / "transcription/voynich_zl3b_lines.tsv"
BUILDER = BASE / "build_nine_hundred_tenth.py"
VALIDATION = BASE / "PASS910_VALIDATION.json"

EVENTS = BASE / "PASS910_2511_EVENT_INTERLINEAR.tsv"
DICTIONARY = BASE / "PASS910_CARD_DICTIONARY.tsv"
LOCI = BASE / "PASS910_LOCUS_EDITION.tsv"
PAGES = BASE / "PASS910_FOURTEEN_PAGE_SUMMARY.tsv"
PORTABLE = BASE / "PASS910_PORTABLE_CORE.tsv"
EXPANSIONS = BASE / "PASS910_REGISTER_EXPANSIONS.tsv"
NOMENCLATOR = BASE / "PASS910_LOCAL_NOMENCLATOR.tsv"
EDITION = BASE / "PASS910_FOURTEEN_PAGE_EDITION.md"
HANDBOOK = BASE / "PASS910_MASTER_HANDBOOK.md"
REPORT = BASE / "PASS910_REPORT.md"
SUMMARY = BASE / "PASS910_BUILD_SUMMARY.json"

SELECTORS = [
    "f10r", "f11r", "f13r", "f55v", "f56r", "f75r", "f81v", "f82r",
    "f83r", "f67r2", "f68r1", "f69v", "f70v1", "f70v2", "f88r",
]
PHYSICAL = [
    "f10r", "f11r", "f13r", "f55v", "f56r", "f75r", "f81v", "f82r",
    "f83r", "f67r2", "f68r1", "f69v", "f70v", "f88r",
]
EXPECTED_PAGE = {
    "f10r": (12, 92), "f11r": (7, 59), "f13r": (10, 77),
    "f55v": (12, 106), "f56r": (19, 105), "f75r": (53, 418),
    "f81v": (28, 255), "f82r": (45, 291), "f83r": (55, 345),
    "f67r2": (74, 190), "f68r1": (37, 65), "f69v": (31, 140),
    "f70v": (50, 218), "f88r": (31, 150),
}
PORTABLE_SET = {
    "AIIN", "AIN", "AIR", "AL", "AR", "CKH", "DY", "E", "EE", "EEE",
    "IIN", "L", "OL", "OT", "Y",
}
ALLOWED_MODES = {
    "LEARNED_COMPONENT_RECIPE",
    "NEW_COMPONENT_COMPOSITION",
    "REGISTER_COMPOSITION_WITH_LOCAL_SIGN",
    "LOCAL_NOMENCLATOR",
    "LOCAL_WORKSHOP_CARD",
}
OUTPUTS = [
    EVENTS, DICTIONARY, LOCI, PAGES, PORTABLE, EXPANSIONS, NOMENCLATOR,
    EDITION, HANDBOOK, REPORT, SUMMARY,
]


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def guarded(selector: str) -> list[tuple[str, int, str, str]]:
    if selector.lower().startswith("f84"):
        raise ValueError("sealed selector")
    command = [
        str(ROOT / "vmanus-exp"), "query-tsv", str(SOURCE),
        "--selector", "page", "--allow", selector,
        "--columns", "page,locus,kind,token_count,eva_clean",
        "--forbid-prefix", "f84",
    ]
    completed = subprocess.run(command, cwd=ROOT, check=True, text=True, capture_output=True)
    source_rows = list(csv.DictReader(io.StringIO(completed.stdout), delimiter="\t"))
    return [
        (row["locus"], index, token, row["kind"])
        for row in source_rows
        for index, token in enumerate(row["eva_clean"].split(), start=1)
    ]


def check(checks: dict[str, bool], name: str, condition: bool) -> None:
    checks[name] = bool(condition)


def main() -> int:
    checks: dict[str, bool] = {}

    subprocess.run(["python3", str(BUILDER)], cwd=ROOT, check=True, text=True, capture_output=True)
    first_hashes = {path.name: sha(path) for path in OUTPUTS}
    subprocess.run(["python3", str(BUILDER)], cwd=ROOT, check=True, text=True, capture_output=True)
    second_hashes = {path.name: sha(path) for path in OUTPUTS}
    check(checks, "deterministic_rebuild", first_hashes == second_hashes)

    event_rows = rows(EVENTS)
    dictionary_rows = rows(DICTIONARY)
    locus_rows = rows(LOCI)
    page_rows = rows(PAGES)
    portable_rows = rows(PORTABLE)
    expansion_rows = rows(EXPANSIONS)
    nomenclator_rows = rows(NOMENCLATOR)
    summary = json.loads(SUMMARY.read_text(encoding="utf-8"))

    check(checks, "events_2511", len(event_rows) == 2511)
    check(checks, "loci_464", len(locus_rows) == 464)
    check(checks, "physical_pages_14", [row["physical_page"] for row in page_rows] == PHYSICAL)
    check(checks, "fourteen_fluent_page_translations", all(row["fluent_page_translation_de"].strip() for row in page_rows) and len({row["fluent_page_translation_de"] for row in page_rows}) == 14)
    check(checks, "source_selectors_15", {row["source_page"] for row in event_rows} == set(SELECTORS))
    check(checks, "event_ids_contiguous", [row["event_id"] for row in event_rows] == [f"P910-E{i:04d}" for i in range(1, 2512)])
    check(checks, "dictionary_ids_contiguous", [row["dictionary_entry_id"] for row in dictionary_rows] == [f"P910-D{i:04d}" for i in range(1, len(dictionary_rows) + 1)])

    source_sequence = []
    for selector in SELECTORS:
        source_sequence.extend((selector, locus, index, token, kind) for locus, index, token, kind in guarded(selector))
    event_sequence = [
        (row["source_page"], row["locus"], int(row["token_index"]), row["surface"], row["source_kind"])
        for row in event_rows
    ]
    check(checks, "guarded_source_sequence_exact", event_sequence == source_sequence)

    by_physical = Counter(row["physical_page"] for row in event_rows)
    locus_by_physical = defaultdict(set)
    for row in event_rows:
        locus_by_physical[row["physical_page"]].add((row["source_page"], row["locus"]))
    for physical, (expected_loci, expected_groups) in EXPECTED_PAGE.items():
        check(checks, f"page_counts_{physical}", len(locus_by_physical[physical]) == expected_loci and by_physical[physical] == expected_groups)

    required_event_fields = [
        "dictionary_entry_id", "surface", "visible_owner_de", "form_analysis_source",
        "component_recipe", "meaning_mode", "portable_value_de", "register_value_de",
        "fluent_token_de",
    ]
    check(checks, "every_event_has_defaults", all(all(row[field].strip() for field in required_event_fields) for row in event_rows))
    check(checks, "meaning_modes_exact", set(row["meaning_mode"] for row in event_rows) == ALLOWED_MODES)
    check(checks, "no_sentence_end_from_line", all(row["line_is_sentence_end"] == "NO" for row in event_rows))
    forbidden_defaults = ("UNKNOWN", "EXEMPLAR", "[?]", "UNBEKANNT")
    check(
        checks,
        "no_placeholder_default",
        all(not any(term in (row["portable_value_de"] + row["register_value_de"] + row["fluent_token_de"]).upper() for term in forbidden_defaults) for row in event_rows),
    )

    local_modes = {"LOCAL_NOMENCLATOR", "LOCAL_WORKSHOP_CARD"}
    check(checks, "all_labels_are_nomenclator", all(row["meaning_mode"] == "LOCAL_NOMENCLATOR" for row in event_rows if row["usage_class"] == "LABEL"))
    check(checks, "local_codes_exact", all(bool(row["local_code"]) == (row["meaning_mode"] in local_modes) for row in event_rows))
    local_mapping: dict[tuple[str, str, str], set[str]] = defaultdict(set)
    for row in event_rows:
        if row["local_code"]:
            local_mapping[(row["register"], row["usage_class"], row["surface"])].add(row["local_code"])
    check(checks, "local_code_stable", all(len(values) == 1 for values in local_mapping.values()))
    check(checks, "nomenclator_codes_unique", len({row["local_code"] for row in nomenclator_rows}) == len(nomenclator_rows))
    check(checks, "nomenclator_covers_local_codes", {row["local_code"] for row in nomenclator_rows} == {row["local_code"] for row in event_rows if row["local_code"]})
    check(checks, "f88_labels_16", sum(row["source_page"] == "f88r" and row["usage_class"] == "LABEL" for row in event_rows) == 16)

    dictionary_event_counts = Counter(row["dictionary_entry_id"] for row in event_rows)
    check(checks, "dictionary_counts_events", all(dictionary_event_counts[row["dictionary_entry_id"]] == int(row["events"]) for row in dictionary_rows))
    dictionary_keys = [
        (row["register"], row["usage_class"], row["surface"], row["component_recipe"], row["meaning_mode"], row["local_code"])
        for row in dictionary_rows
    ]
    check(checks, "dictionary_keys_unique", len(dictionary_keys) == len(set(dictionary_keys)))

    event_loci = defaultdict(list)
    for row in event_rows:
        event_loci[(row["source_page"], row["locus"])].append(row)
    check(checks, "locus_keys_exact", {(row["source_page"], row["locus"]) for row in locus_rows} == set(event_loci))
    check(checks, "locus_group_counts", all(int(row["groups"]) == len(event_loci[(row["source_page"], row["locus"])]) for row in locus_rows))
    check(
        checks,
        "locus_source_sequences",
        all(
            row["source_sequence"] == " ".join(event["surface"] for event in event_loci[(row["source_page"], row["locus"])])
            for row in locus_rows
        ),
    )
    check(checks, "locus_no_sentence_claim", all(row["sentence_boundary_claim"] == "NONE__PHYSICAL_LOCUS_ONLY" for row in locus_rows))

    check(checks, "portable_core_15", len(portable_rows) == 15 and {row["component"] for row in portable_rows} == PORTABLE_SET)
    portable_map = {row["component"]: row["portable_value_de"] for row in portable_rows}
    check(checks, "air_path_not_water", portable_map["AIR"] == "LAUF ODER BAHN")
    check(checks, "al_connection", portable_map["AL"] == "AUFNAHME- ODER ANSCHLUSSSTELLE")
    check(checks, "ar_output", portable_map["AR"] == "AUSGANGS- ODER ENTNAHMESTELLE")
    check(checks, "expansion_rows_49", len(expansion_rows) == 49)
    check(checks, "four_register_expansions", all(row["herbal_de"] and row["biological_de"] and row["zodiac_de"] and row["pharma_de"] for row in expansion_rows))

    mode_counts = Counter(row["meaning_mode"] for row in event_rows)
    for mode, key in (
        ("LEARNED_COMPONENT_RECIPE", "learned_component_events"),
        ("NEW_COMPONENT_COMPOSITION", "new_component_events"),
        ("REGISTER_COMPOSITION_WITH_LOCAL_SIGN", "local_sign_component_events"),
        ("LOCAL_NOMENCLATOR", "local_nomenclator_events"),
        ("LOCAL_WORKSHOP_CARD", "local_workshop_card_events"),
    ):
        check(checks, f"summary_mode_{mode}", summary[key] == mode_counts[mode])
    check(checks, "summary_core_counts", summary["events"] == 2511 and summary["loci"] == 464 and summary["physical_pages"] == 14 and summary["source_selectors"] == 15)
    check(checks, "summary_hashes", summary["events_sha256"] == sha(EVENTS) and summary["dictionary_sha256"] == sha(DICTIONARY) and summary["edition_sha256"] == sha(EDITION) and summary["report_sha256"] == sha(REPORT))

    edition_text = EDITION.read_text(encoding="utf-8")
    check(checks, "edition_has_14_pages", all(f"## {page} —" in edition_text for page in PHYSICAL))
    check(checks, "edition_has_every_locus", all(f"`{row['locus']}`" in edition_text for row in locus_rows))
    check(checks, "handbook_present", HANDBOOK.is_file() and "Die drei Schichten" in HANDBOOK.read_text(encoding="utf-8"))
    check(checks, "report_present", REPORT.is_file() and "Keine Gruppe bleibt ohne Defaultlesung" in REPORT.read_text(encoding="utf-8"))
    check(checks, "sealed_selectors_absent", all(not selector.lower().startswith("f84") for selector in SELECTORS))

    failures = [name for name, passed in checks.items() if not passed]
    result = {
        "status": "PASS" if not failures else "FAIL",
        "checks_passed": sum(checks.values()),
        "checks_total": len(checks),
        "failures": failures,
        "decision": "THREE_LAYER_WORKSHOP_GRAMMAR_WITH_LOCAL_NOMENCLATOR",
        "events": len(event_rows),
        "loci": len(locus_rows),
        "physical_pages": len(page_rows),
        "dictionary_entries": len(dictionary_rows),
        "local_drawer_entries": len(nomenclator_rows),
        "events_sha256": sha(EVENTS),
        "report_sha256": sha(REPORT),
    }
    VALIDATION.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, sort_keys=True))
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
