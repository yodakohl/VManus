#!/usr/bin/env python3
"""Resolve ambiguous case fragments through desk, page, and record owners."""

from __future__ import annotations

import csv
import json
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
P613 = ROOT / "experiments/yolo/sidequest_semantic_duplicate_command_resolution_six_hundred_thirteenth"
P646 = ROOT / "experiments/yolo/sidequest_semantic_case_fragment_capacity_six_hundred_forty_sixth"


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: list[dict[str, object]], fields: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, delimiter="\t", fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def desk(record: str) -> str:
    if record.startswith("H"):
        return "P_PREPARATION_DESK"
    if record in {"B1", "B2"}:
        return "B_BATH_DESK"
    return "S_STATION_DESK"


def main() -> None:
    HERE.mkdir(parents=True, exist_ok=True)
    events = read_tsv(P613 / "SIX_HUNDRED_THIRTEENTH_381_REVISED_EVENT_COMMANDS.tsv")
    ambiguous = read_tsv(P646 / "SIX_HUNDRED_FORTY_SIXTH_AMBIGUOUS_FRAGMENTS.tsv")

    contexts_by_case: dict[str, list[dict[str, str]]] = defaultdict(list)
    seen = set()
    for row in events:
        if row["case_id"] not in {"C1", "C2", "C3", "C4", "C5"}:
            continue
        key = (row["case_id"], row["record"], row["page"])
        if key in seen:
            continue
        seen.add(key)
        contexts_by_case[row["case_id"]].append({
            "case_id": row["case_id"],
            "record": row["record"],
            "page": row["page"],
            "desk": desk(row["record"]),
            "domain": "HERBAL" if row["record"].startswith("H") else "BIOLOGICAL",
        })
    for contexts in contexts_by_case.values():
        contexts.sort(key=lambda row: row["record"])

    desk_cases: dict[str, set[str]] = defaultdict(set)
    page_cases: dict[str, set[str]] = defaultdict(set)
    record_cases: dict[str, set[str]] = defaultdict(set)
    for case_id, contexts in contexts_by_case.items():
        for context in contexts:
            desk_cases[context["desk"]].add(case_id)
            page_cases[context["page"]].add(case_id)
            record_cases[context["record"]].add(case_id)

    rows: list[dict[str, object]] = []
    for fragment in ambiguous:
        source_case = fragment["source_case"]
        card_candidates = set(fragment["matching_cases"].split("|"))
        for context in contexts_by_case[source_case]:
            after_desk = sorted(card_candidates & desk_cases[context["desk"]])
            after_page = sorted(card_candidates & page_cases[context["page"]])
            after_record = sorted(card_candidates & record_cases[context["record"]])
            rows.append({
                "fragment_id": fragment["fragment_id"],
                "source_case": source_case,
                "domain": context["domain"],
                "desk": context["desk"],
                "page": context["page"],
                "record": context["record"],
                "surface_fragment": fragment["surface_fragment"],
                "card_candidates": "|".join(sorted(card_candidates)),
                "card_candidate_count": len(card_candidates),
                "desk_candidates": "|".join(after_desk),
                "desk_candidate_count": len(after_desk),
                "desk_resolves": "YES" if after_desk == [source_case] else "NO",
                "page_candidates": "|".join(after_page),
                "page_candidate_count": len(after_page),
                "page_resolves": "YES" if after_page == [source_case] else "NO",
                "record_candidates": "|".join(after_record),
                "record_candidate_count": len(after_record),
                "record_resolves": "YES" if after_record == [source_case] else "NO",
                "minimum_context_level": (
                    "DESK"
                    if after_desk == [source_case]
                    else "PAGE"
                    if after_page == [source_case]
                    else "RECORD"
                    if after_record == [source_case]
                    else "UNRESOLVED"
                ),
                "may_insert_missing_cards": "NO_NOT_UNLESS_COPY_DAMAGE_IS_INDEPENDENTLY_KNOWN",
                "safe_owner_reading_de": f"gemeinsamer Untergang innerhalb {context['record']} auf {context['page']}; keine ausgelassene Spezialkarte automatisch ergänzen",
            })

    summary_rows: list[dict[str, object]] = []
    for domain in ["ALL", "HERBAL", "BIOLOGICAL"]:
        selected = rows if domain == "ALL" else [row for row in rows if row["domain"] == domain]
        for level, column in [("CARDS_ONLY", None), ("DESK", "desk_resolves"), ("PAGE", "page_resolves"), ("RECORD", "record_resolves")]:
            resolved = 0 if column is None else sum(row[column] == "YES" for row in selected)
            summary_rows.append({
                "domain": domain,
                "context_level": level,
                "contextualized_fragments": len(selected),
                "resolved": resolved,
                "unresolved": len(selected) - resolved,
                "resolution_fraction": f"{resolved}/{len(selected)}",
            })

    minimum_rows: list[dict[str, object]] = []
    for level in ["DESK", "PAGE", "RECORD", "UNRESOLVED"]:
        selected = [row for row in rows if row["minimum_context_level"] == level]
        minimum_rows.append({
            "minimum_context_level": level,
            "contexts": len(selected),
            "herbal": sum(row["domain"] == "HERBAL" for row in selected),
            "biological": sum(row["domain"] == "BIOLOGICAL" for row in selected),
            "example_fragment": selected[0]["surface_fragment"] if selected else "NONE",
            "example_owner": f"{selected[0]['page']}:{selected[0]['record']}" if selected else "NONE",
        })

    write_tsv(HERE / "SIX_HUNDRED_FORTY_SEVENTH_74_OWNER_CONTEXTS.tsv", rows, list(rows[0]))
    write_tsv(HERE / "SIX_HUNDRED_FORTY_SEVENTH_12_LEVEL_SUMMARY.tsv", summary_rows, list(summary_rows[0]))
    write_tsv(HERE / "SIX_HUNDRED_FORTY_SEVENTH_4_MINIMUM_LEVELS.tsv", minimum_rows, list(minimum_rows[0]))

    md = [
        "# Kartenrest plus sichtbarer Besitzer",
        "",
        "Jedes der 37 mehrdeutigen Kartenfragmente wird zweimal gesetzt: einmal in seinem Herbal-Record und einmal im zugehörigen Biological-Record. So entstehen 74 konkrete Besitzerkontexte.",
        "",
        "| Ebene | alle | Herbal | Biological |",
        "|---|---:|---:|---:|",
    ]
    for level in ["DESK", "PAGE", "RECORD"]:
        all_row = next(row for row in summary_rows if row["domain"] == "ALL" and row["context_level"] == level)
        herbal_row = next(row for row in summary_rows if row["domain"] == "HERBAL" and row["context_level"] == level)
        bio_row = next(row for row in summary_rows if row["domain"] == "BIOLOGICAL" and row["context_level"] == level)
        md.append(f"| {level} | {all_row['resolution_fraction']} | {herbal_row['resolution_fraction']} | {bio_row['resolution_fraction']} |")
    md.extend([
        "",
        "Der Tisch allein hilft vor allem im Biological-Register. Die physische Seite löst die meisten Fälle, lässt aber f10r (C1/C2) und f83r (C3/C4/C5) teilweise offen. Erst der konkrete Recordbesitzer adressiert alle Fragmente eindeutig.",
        "",
        "Diese Adressauflösung erlaubt noch keine automatische Ergänzung verschwundener Karten. Derselbe gemeinsame Rückgrat kann auch ein absichtlich kurzer Untergang sein. Karten dürfen nur eingesetzt werden, wenn Beschädigung oder Kollation unabhängig zeigt, dass tatsächlich etwas fehlt.",
    ])
    (HERE / "SIX_HUNDRED_FORTY_SEVENTH_OWNER_HIERARCHY_BOOK.md").write_text("\n".join(md).rstrip() + "\n", encoding="utf-8")

    summary = {
        "status": "PASS",
        "ambiguous_fragments": len(ambiguous),
        "owner_contexts": len(rows),
        "desk_resolutions": sum(row["desk_resolves"] == "YES" for row in rows),
        "page_resolutions": sum(row["page_resolves"] == "YES" for row in rows),
        "record_resolutions": sum(row["record_resolves"] == "YES" for row in rows),
        "minimum_level_counts": {row["minimum_context_level"]: int(row["contexts"]) for row in minimum_rows},
        "automatic_missing_card_insertions": 0,
        "new_cards": 0,
        "new_surfaces": 0,
        "new_meanings": 0,
        "decision": "VISIBLE_RECORD_OWNER_RESOLVES_ADDRESS_NOT_MISSING_CONTENT",
    }
    (HERE / "SIX_HUNDRED_FORTY_SEVENTH_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
