#!/usr/bin/env python3
"""Audit the f57 outside form as a structural entry construction, not a word."""

from __future__ import annotations

import csv
import hashlib
import json
import math
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parent
GROUPS = ROOT / "gdt016_group_state_inventory.tsv"
F57 = ROOT / "gdt179_f57_inscription_inventory.tsv"
G179 = ROOT / "gdt179_result.json"
METHOD = ROOT / "GDT183_F57_START_CONSTRUCTION_METHOD.md"
REPORT = ROOT / "GDT183_F57_START_CONSTRUCTION_REPORT.md"
OCC = ROOT / "gdt183_start_construction_occurrences.tsv"
STATS = ROOT / "gdt183_start_construction_statistics.tsv"
COUNTER = ROOT / "gdt183_counterexamples.tsv"
RESULT = ROOT / "gdt183_result.json"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle, delimiter="\t"))
    # GDT016 is a prose-derived inventory.  The explicit guard is still binding.
    page_key = "page" if rows and "page" in rows[0] else "locus"
    assert not any(row[page_key].startswith("f84r") for row in rows)
    return [row for row in rows if not row[page_key].startswith("f84")]


def write_tsv(path: Path, rows: list[dict[str, object]]) -> None:
    assert rows
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def position(row: dict[str, str]) -> str:
    index, count = int(row["group_index"]), int(row["group_count"])
    if count == 1:
        return "SINGLE"
    if index == 1:
        return "FIRST"
    if index == count:
        return "LAST"
    return "CORE"


def hypergeom_all_successes(population: int, successes: int, draws: int) -> float:
    return math.comb(successes, draws) / math.comb(population, draws)


def canonical(obj: object) -> bytes:
    return (json.dumps(obj, sort_keys=True, indent=2) + "\n").encode()


def main() -> None:
    groups = read_tsv(GROUPS)
    f57 = read_tsv(F57)
    g179 = json.loads(G179.read_text())
    assert not g179["f84r_accessed"]

    family = [row for row in groups if row["family_surface"] == "BAFAB"]
    assert len(family) == 4 and all(position(row) == "FIRST" for row in family)
    d_wrapped = [row for row in groups if row["stripped_prefix"] == "d"]
    d_first = sum(position(row) == "FIRST" for row in d_wrapped)
    raw_p = hypergeom_all_successes(len(d_wrapped), d_first, len(family))

    by_family: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in groups:
        by_family[row["family_surface"]].append(row)
    matched = [rows for rows in by_family.values() if len(rows) == len(family)]
    all_first = sum(all(position(row) == "FIRST" for row in rows) for rows in matched)
    family_search_rate = all_first / len(matched)

    outside = next(row for row in f57 if row["locus"] == "f57v.1")
    occurrence_rows: list[dict[str, object]] = [{
        "locus":"f57v.1", "page":"f57v", "section":"C", "surface":outside["surface"],
        "family":"BAFAB", "position":"SINGLE_OUTSIDE_COMMON_RING_START",
        "wrapper":"d", "page_host":"air_or_airol", "right_family":"al_or_none",
        "record_state":"DIAGRAM_LABEL", "evidence":"HUMAN_START_POSITION_PLUS_ALTERNATE_READINGS",
    }]
    for row in sorted(family, key=lambda item: item["locus"]):
        occurrence_rows.append({
            "locus":row["locus"], "page":row["page"], "section":row["section"],
            "surface":row["token"], "family":row["family_surface"], "position":position(row),
            "wrapper":row["stripped_prefix"], "page_host":row["residual_host"],
            "right_family":"NOT_SEPARATELY_PARSED_IN_GDT016", "record_state":row["record_state"],
            "evidence":"HPR2_PARSER_COVERED_PROSE",
        })
    write_tsv(OCC, occurrence_rows)

    stats_rows = [
        {"test":"BAFAB_FIRST_IN_HPR2_PROSE","numerator":4,"denominator":4,"value":1.0,
         "comparison":"ALL_FOUR_PARSER_COVERED_OCCURRENCES_ARE_FIRST"},
        {"test":"D_WRAPPER_FIRST_RATE","numerator":d_first,"denominator":len(d_wrapped),
         "value":d_first/len(d_wrapped),"comparison":"MATCHED_OUTER_WRAPPER_BASE_RATE"},
        {"test":"BAFAB_VS_D_WRAPPER_HYPERGEOMETRIC","numerator":4,"denominator":4,
         "value":raw_p,"comparison":"RAW_EXTERNALLY_NOMINATED_FAMILY_P"},
        {"test":"COUNT4_FAMILY_SEARCH_RATE","numerator":all_first,"denominator":len(matched),
         "value":family_search_rate,"comparison":"FAMILIES_WITH_FOUR_PARSER_OCCURRENCES_AND_ALL_FIRST"},
        {"test":"DISTINCT_RECORD_STATES","numerator":len({row['record_state'] for row in family}),
         "denominator":len(family),"value":len({row['record_state'] for row in family})/len(family),
         "comparison":"ENTRY_AL_AND_OL_STATES_PREVENT_WHOLE_WORD_GLOSS"},
    ]
    write_tsv(STATS, stats_rows)

    counter_rows = [
        {"id":"C1","finding":"The four parser-covered BAFAB prose occurrences are a selected parseable subset.","impact":"The 4/4 entry rate is exploratory and cannot stand as an unbiased manuscript census."},
        {"id":"C2","finding":"The matched count-four family scan contains two all-FIRST families among 83.","impact":"The nominal family-search rate is 0.0241; BAFAB is unusual but not unique."},
        {"id":"C3","finding":"BAFAB realizes ENTRY_STATE, AL_STATE, and OL_STATE in prose.","impact":"The whole surface does not have one stable compiler role, much less a fixed lexical meaning."},
        {"id":"C4","finding":"f57v.1 alternates between dairal and dairol across readings.","impact":"Even the local host/right realization is not transcription-stable."},
        {"id":"C5","finding":"d- was already independently identified as an entry-enriched wrapper.","impact":"The new enrichment can be explained by a known compiler layer rather than a content word."},
        {"id":"C6","finding":"No independent diagram start marker with a frozen BAFAB prediction was tested.","impact":"START_MARKER_LIKE remains a structural interpretation, not a confirmed translation."},
    ]
    write_tsv(COUNTER, counter_rows)

    outputs = [OCC, STATS, COUNTER]
    result = {
        "experiment":"GDT183_F57_START_CONSTRUCTION_AUDIT",
        "status":"D_WRAPPED_BAFAB_ENTRY_ENRICHED_WHOLE_WORD_START_GLOSS_NOT_SUPPORTED",
        "headline":"The f57 outside dairal/dairol form belongs to an entry-enriched formal family, but the reusable evidence localizes to a d-wrapped construction rather than a translated word.",
        "counts":{
            "f57_outside_labels":1, "parser_covered_BAFAB_prose":len(family),
            "BAFAB_first":4, "d_wrapped_groups":len(d_wrapped), "d_wrapped_first":d_first,
            "matched_count4_families":len(matched), "matched_all_first_families":all_first,
            "distinct_BAFAB_record_states":len({row["record_state"] for row in family}),
        },
        "statistics":{"raw_hypergeometric_p":raw_p,"count4_family_search_rate":family_search_rate},
        "interpretation":{
            "supported":"F57_OUTSIDE_FORM_IS_START_MARKER_LIKE_AND_USES_ENTRY_ENRICHED_D_WRAPPED_FAMILY",
            "not_supported":["DAIRAL_MEANS_START","DAIROL_MEANS_TITLE","AIR_IS_A_TRANSLATED_LEXEME"],
            "best_parse":"d[ENTRY_WRAPPER] + air/airol[OPAQUE_PAGE_HOST_OR_HOST_PLUS_RIGHT]",
        },
        "claim_ceiling":"A structural entry-marker analysis for one exposed diagram label and an entry-enriched parser-covered family. No word meaning, morpheme, sound, language, title, plaintext, or translation is established.",
        "inputs":{path.name:sha(path) for path in (GROUPS,F57,G179)},
        "outputs":{path.name:sha(path) for path in outputs},
        "documents":{path.name:sha(path) for path in (METHOD,REPORT)},
        "implementation":sha(Path(__file__)),
        "f84r_accessed":False,
    }
    RESULT.write_bytes(canonical(result))
    print(json.dumps(result["counts"], sort_keys=True))


if __name__ == "__main__":
    main()
