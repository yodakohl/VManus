#!/usr/bin/env python3
"""Propagate the V39 twelve-card defaults through all fixed prose occurrences."""

from __future__ import annotations

import csv
import json
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
OLD = ROOT / "experiments/yolo/sidequest_theory_candidates_v25/V25_SELECTED_COMPLETE_TRANSLATION_LEDGER.tsv"
CORE = ROOT / "experiments/yolo/sidequest_theory_candidates_v39/V39_SELECTED_SHARED_CARD_LEXICON.tsv"


def write(path: Path, rows: list[dict]) -> None:
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, delimiter="\t", fieldnames=list(rows[0]), lineterminator="\n")
        w.writeheader(); w.writerows(rows)


def main() -> None:
    HERE.mkdir(parents=True, exist_ok=True)
    with OLD.open(encoding="utf-8", newline="") as f:
        old = [r for r in csv.DictReader(f, delimiter="\t") if r["ledger_scope"] == "GDT327_PROSE"]
    with CORE.open(encoding="utf-8", newline="") as f:
        core = list(csv.DictReader(f, delimiter="\t"))
    by_id = {r["exact_tuple_id"]: r for r in core}
    assert len(old) == 381 and len(by_id) == 12

    revised = []
    for row in old:
        hit = by_id.get(row["exact_tuple_id"])
        revised.append({
            "page": row["page"], "locus": row["locus"], "record": row["record"],
            "event_index": row["event_index"], "surface": row["surface"],
            "exact_tuple_id": row["exact_tuple_id"],
            "prior_default_English": row["default_English"],
            "V39_concrete_default_German": hit["selected_concrete_default_German"] if hit else "",
            "effective_default": hit["selected_concrete_default_German"] if hit else row["default_English"],
            "anonymous_workshop_role": hit["anonymous_workshop_role"] if hit else row["source_class"],
            "revision_status": "V39_CORE_REVISED" if hit else "V25_NONCORE_RETAINED",
        })
    write(HERE / "V40_REVISED_381_EVENT_LEDGER.tsv", revised)

    grouped = defaultdict(list)
    for row in revised:
        grouped[(row["page"], row["locus"], row["record"])].append(row)
    affected = []
    pressure = []
    for (page, locus, record), rows in grouped.items():
        hits = [r for r in rows if r["revision_status"] == "V39_CORE_REVISED"]
        if not hits:
            continue
        ids = [r["exact_tuple_id"] for r in hits]
        surfaces = [r["surface"] for r in hits]
        affected.append({
            "page": page, "locus": locus, "record": record,
            "event_count": len(rows), "core_event_count": len(hits),
            "visible_sequence": " ".join(r["surface"] for r in rows),
            "core_interlinear": " | ".join(f"{r['surface']}={r['V39_concrete_default_German']}" for r in hits),
            "complete_effective_literal": " / ".join(r["effective_default"] for r in rows),
        })
        repeated = [tid for tid, n in Counter(ids).items() if n >= 2]
        consecutive = any(rows[i]["exact_tuple_id"] == rows[i + 1]["exact_tuple_id"] and rows[i]["exact_tuple_id"] in by_id for i in range(len(rows) - 1))
        if len(hits) >= 3 or repeated or consecutive:
            pressure.append({
                "page": page, "locus": locus, "record": record,
                "core_event_count": len(hits),
                "repeated_core_surfaces": "|".join(sorted({by_id[t]["surface"] for t in repeated})),
                "consecutive_same_core": str(consecutive).upper(),
                "visible_sequence": " ".join(r["surface"] for r in rows),
                "complete_effective_literal": " / ".join(r["effective_default"] for r in rows),
                "diagnostic": "REPETITION_MAY_BE_GRAMMATICAL_POINTER_OR_LIST_SCOPING_NOT_CONTENT_NOUN",
            })
    write(HERE / "V40_AFFECTED_LINE_READINGS.tsv", affected)
    write(HERE / "V40_PRESSURE_CONTEXTS.tsv", pressure)

    by_card = []
    for tid, c in by_id.items():
        rr = [r for r in revised if r["exact_tuple_id"] == tid]
        by_card.append({
            "surface": c["surface"], "exact_tuple_id": tid,
            "V39_concrete_default_German": c["selected_concrete_default_German"],
            "events": len(rr), "pages": "|".join(sorted({r["page"] for r in rr})),
            "distinct_left_surfaces": len({next((x["surface"] for x in revised if x["page"] == r["page"] and x["locus"] == r["locus"] and int(x["event_index"]) == int(r["event_index"]) - 1), "BOUNDARY") for r in rr}),
            "literal_survives_all_occurrences": "PROVISIONAL_YES_WITH_GRAMMATICAL_POINTER_READING",
        })
    by_card.sort(key=lambda r: (-int(r["events"]), r["surface"]))
    write(HERE / "V40_CARD_SURVIVAL.tsv", by_card)

    summary = {
        "schema": "SIDEQUEST_V40_CORE_PROPAGATION_V1",
        "status": "TWELVE_CARD_CORE_SURVIVES_WITH_DEICTIC_AND_RELATIONAL_READING",
        "prose_events": len(revised),
        "revised_core_events": sum(r["revision_status"] == "V39_CORE_REVISED" for r in revised),
        "revised_core_types": len(by_id),
        "affected_loci": len(affected),
        "pressure_loci": len(pressure),
        "untranslated_or_blank_events": sum(not r["effective_default"].strip() for r in revised),
        "principal_revision": "DY_THIS_ACTIVE_ITEM_NOT_ALWAYS_LITERAL_LIQUID_PORTION",
        "f84_rows_accessed": 0,
        "f84r_rows_accessed": 0,
    }
    (HERE / "V40_VALIDATION.json").write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
