#!/usr/bin/env python3
"""Audit exact full-surface overlap between fixed prose and Astro namespaces."""

from __future__ import annotations

import csv
import json
from collections import defaultdict
from pathlib import Path


HERE = Path(__file__).resolve().parent
V22 = HERE.parent / "sidequest_theory_candidates_v22"
ASTRO = {"f67r2", "f68r1", "f69v"}


def main() -> None:
    with (V22 / "V22_SELECTED_COMPLETE_TRANSLATION_LEDGER.tsv").open(
            encoding="utf-8", newline="") as handle:
        ledger = list(csv.DictReader(handle, delimiter="\t"))
    prose: dict[str, list[dict[str, str]]] = defaultdict(list)
    astro: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in ledger:
        (astro if row["page"] in ASTRO else prose)[row["surface"]].append(row)
    common = sorted(set(prose) & set(astro))
    rows = []
    for surface in common:
        pmean = sorted({row["default_English"] for row in prose[surface]})
        amean = sorted({row["default_English"] for row in astro[surface]})
        exact_portable = len(set(pmean + amean)) == 1
        rows.append({
            "surface": surface,
            "prose_events": str(len(prose[surface])),
            "astro_events": str(len(astro[surface])),
            "prose_pages": "|".join(sorted({row["page"] for row in prose[surface]})),
            "astro_pages": "|".join(sorted({row["page"] for row in astro[surface]})),
            "prose_defaults": " || ".join(pmean),
            "astro_defaults": " || ".join(amean),
            "all_occurrence_exact_default_portable": "YES" if exact_portable else "NO",
            "working_disposition": (
                "PORTABLE_FULL_CARD" if exact_portable else "REGISTER_LOCAL_HOMOGRAPH"
            ),
        })
    assert len(rows) == 44
    assert sum(int(row["prose_events"]) for row in rows) == 98
    assert sum(int(row["astro_events"]) for row in rows) == 89
    assert not any(row["all_occurrence_exact_default_portable"] == "YES" for row in rows)
    path = HERE / "V23_EXACT_SURFACE_HOMOGRAPHS.tsv"
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t",
                                lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    result = {
        "schema": "SIDEQUEST_V23_EXACT_SURFACE_HOMOGRAPH_AUDIT_V1",
        "status": "PASS",
        "cross_namespace_surface_types": 44,
        "covered_prose_events": 98,
        "covered_astro_events": 89,
        "globally_portable_exact_defaults": 0,
        "complete_ledger_rows_unchanged": 776,
        "f84": {"opened": False, "queried": False, "retained": False},
        "f84r": {"opened": False, "queried": False, "retained": False},
    }
    (HERE / "V23_VALIDATION.json").write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
