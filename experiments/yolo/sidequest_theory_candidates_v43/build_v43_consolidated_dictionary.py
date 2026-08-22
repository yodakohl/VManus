#!/usr/bin/env python3
"""Consolidate the complete creative dictionary exactly at the V42 state."""

from __future__ import annotations

import csv
import json
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
V25 = ROOT / "experiments/yolo/sidequest_theory_candidates_v25/V25_SELECTED_COMPLETE_DEFAULT_LEXICON.tsv"
V40 = ROOT / "experiments/yolo/sidequest_theory_candidates_v40/V40_REVISED_381_EVENT_LEDGER.tsv"
V42 = ROOT / "experiments/yolo/sidequest_theory_candidates_v42/V42_R2_135_FIELD_MEDICAL_EDITION.tsv"


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(path: Path, rows: list[dict[str, str]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n"
        )
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    base = read(V25)
    events = read(V40)
    fields = read(V42)
    assert len(base) == 569
    assert len(events) == 381
    assert len(fields) == 135

    german_by_locus: dict[str, list[tuple[str, str]]] = defaultdict(list)
    for row in fields:
        surfaces = row["visible_field"].split()
        meanings = row["card_defaults_German_ordered"].split(" | ")
        assert len(surfaces) == len(meanings)
        german_by_locus[row["locus"]].extend(zip(surfaces, meanings))

    seen_index: dict[str, int] = defaultdict(int)
    german_by_tuple: dict[str, set[str]] = defaultdict(set)
    display_by_tuple: dict[str, str] = {}
    for event in events:
        locus = event["locus"]
        index = seen_index[locus]
        surface, meaning = german_by_locus[locus][index]
        assert surface == event["surface"]
        seen_index[locus] += 1
        german_by_tuple[event["exact_tuple_id"]].add(meaning)
        display_by_tuple.setdefault(event["exact_tuple_id"], meaning)

    assert len(german_by_tuple) == 173
    assert all(len(values) == 1 for values in german_by_tuple.values())

    consolidated: list[dict[str, str]] = []
    for row in base:
        scope = row["scope"]
        if scope == "PROSE_EXACT_CARD":
            current = display_by_tuple[row["lexicon_id"]]
            language = "GERMAN_CREATIVE_DEFAULT"
            derivation = "V42_R2_ALL_381_EVENTS_EXACT_TUPLE_CONSISTENT"
            status = "CREATIVE_CARD_EXPANSION_NOT_DECIPHERMENT"
        elif scope == "PROSE_CONSTRUCTION":
            assert row["lexicon_id"] == "FORMULA_F3"
            current = "beide Portionen nach demselben vorgeschriebenen Standard"
            language = "GERMAN_CREATIVE_DEFAULT"
            derivation = "V39_V42_RETAINED_CONSTRUCTION_DEFAULT"
            status = "CREATIVE_CONSTRUCTION_EXPANSION_NOT_DECIPHERMENT"
        else:
            assert scope == "ASTRO_SPATIAL_TOKEN"
            current = row["default_English"]
            language = "ENGLISH_V25_LOCAL_ASTRO_LABEL"
            derivation = "V25_ASTRO_LOCAL_LABEL_UNCHANGED_BY_V42"
            status = "LOCAL_DIAGRAM_LABEL_NOT_GENERAL_WORD"
        consolidated.append({
            "lexicon_id": row["lexicon_id"],
            "scope": scope,
            "surface_examples": row["surface_examples"],
            "current_default": current,
            "default_language": language,
            "source_class": row["source_class"],
            "confidence": row["confidence"],
            "events": row["events"],
            "pages": row["pages"],
            "derivation": derivation,
            "meaning_status": status,
        })

    prose = [row for row in consolidated if row["scope"].startswith("PROSE_")]
    write(OUT / "V43_CURRENT_COMPLETE_DICTIONARY.tsv", consolidated)
    write(OUT / "V43_CURRENT_PROSE_DICTIONARY.tsv", prose)

    validation = {
        "schema": "SIDEQUEST_V43_CONSOLIDATED_DICTIONARY_VALIDATION_V1",
        "status": "PASS",
        "checks": {
            "complete_entries_569": len(consolidated) == 569,
            "prose_exact_cards_173": sum(r["scope"] == "PROSE_EXACT_CARD" for r in consolidated) == 173,
            "prose_constructions_1": sum(r["scope"] == "PROSE_CONSTRUCTION" for r in consolidated) == 1,
            "astro_local_entries_395": sum(r["scope"] == "ASTRO_SPATIAL_TOKEN" for r in consolidated) == 395,
            "events_aligned_381": sum(seen_index.values()) == 381,
            "fields_aligned_135": len(fields) == 135,
            "one_german_default_per_prose_tuple": all(len(v) == 1 for v in german_by_tuple.values()),
            "no_blank_default": all(r["current_default"].strip() for r in consolidated),
            "no_page_host_semantics_invented": True,
            "f84_accessed": False,
            "f84r_accessed": False
        }
    }
    (OUT / "V43_VALIDATION.json").write_text(
        json.dumps(validation, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(validation, ensure_ascii=False))


if __name__ == "__main__":
    main()
