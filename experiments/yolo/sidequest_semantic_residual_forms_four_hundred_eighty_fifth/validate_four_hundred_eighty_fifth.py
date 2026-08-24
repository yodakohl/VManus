#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent


def read(name: str) -> list[dict[str, str]]:
    with (HERE / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    selected = read("FOUR_HUNDRED_EIGHTY_FIFTH_43_OPTIMAL_MOTIF_OCCURRENCES.tsv")
    decomposition = read("FOUR_HUNDRED_EIGHTY_FIFTH_65_LOCAL_FORM_DECOMPOSITIONS.tsv")
    residual = read("FOUR_HUNDRED_EIGHTY_FIFTH_75_RESIDUAL_SPANS.tsv")
    mini = read("FOUR_HUNDRED_EIGHTY_FIFTH_THREE_RESIDUAL_MINI_FORMS.tsv")
    local_deck = read("FOUR_HUNDRED_EIGHTY_FIFTH_59_ITEM_LOCAL_DECK.tsv")
    manual = read("FOUR_HUNDRED_EIGHTY_FIFTH_277_ITEM_REVISED_MANUAL.tsv")
    ledger = read("FOUR_HUNDRED_EIGHTY_FIFTH_776_REDUCED_MANUAL_RECONSTRUCTION.tsv")
    counts = Counter(row["strategy"] for row in decomposition)
    checks = {
        "selected_occurrences_43": len(selected) == 43,
        "selected_events_112": sum(int(row["events"]) for row in selected) == 112,
        "local_forms_65": len(decomposition) == 65,
        "local_statement_ids_unique": len({row["statement_id"] for row in decomposition}) == 65,
        "original_events_302": sum(int(row["statement_events"]) for row in decomposition) == 302,
        "residual_spans_75": len(residual) == 75,
        "residual_events_190": sum(int(row["events"]) for row in residual) == 190,
        "three_mini_forms": len(mini) == 3,
        "strategy_counts": counts == {"MOTIFS_ONLY": 2, "ONE_LOCAL_RESIDUAL": 46, "SHARED_RESIDUAL_MINI_FORM": 7, "KEEP_WHOLE_LOCAL_FORM": 10},
        "local_deck_59": len(local_deck) == 59,
        "local_deck_atoms_225": sum(int(row["events_to_memorize"]) for row in local_deck) == 225,
        "manual_277": len(manual) == 277,
        "ledger_776": len(ledger) == 776,
        "prose_381": sum(row["domain"] == "PROSE" for row in ledger) == 381,
        "astro_395": sum(row["domain"] == "ASTRO" for row in ledger) == 395,
        "surface_still_exact_663": sum(row["surface_exact_without_exemplar"] == "YES" for row in ledger) == 663,
        "fixed_pages_only": {row["page"] for row in ledger} == {"f10r", "f11r", "f55v", "f56r", "f81v", "f82r", "f83r", "f67r2", "f68r1", "f69v"},
        "sealed_pages_absent": all(not row["page"].startswith("f84") for row in ledger),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / "FOUR_HUNDRED_EIGHTY_FIFTH_VALIDATION.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(result["status"])
    for key, value in checks.items():
        print(f"{key}\t{'PASS' if value else 'FAIL'}")
    if result["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
