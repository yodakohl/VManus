#!/usr/bin/env python3
"""Validate the complete 54-word source-vocabulary refinement."""

from __future__ import annotations

import csv
import json
from pathlib import Path


OUT = Path(__file__).resolve().parent


def read_tsv(name: str) -> list[dict[str, str]]:
    with (OUT / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    ranking = read_tsv("EIGHTY_FIRST_54_SOURCE_WORD_RANKING.tsv")
    lexicon = read_tsv("EIGHTY_FIRST_54_REFINED_SOURCE_LEXICON.tsv")
    revisions = read_tsv("EIGHTY_FIRST_12_SOURCE_WORD_REVISIONS.tsv")
    checks = {
        "ranking_54": len(ranking) == 54 and len({row["source_slot"] for row in ranking}) == 54,
        "lexicon_54": len(lexicon) == 54 and len({row["source_slot"] for row in lexicon}) == 54,
        "revisions_12": len(revisions) == 12,
        "all_values_nonempty": all(row["revised_value_de"] for row in ranking),
        "all_provenance_assigned": all(row["provenance_class"] in {"DIRECT_VISIBLE_OWNER_OR_GEOMETRY", "VISIBLE_CONTEXT_PLUS_CARD", "CARD_OR_REGISTER_ONLY", "MASTER_SELECTED_CONTENT"} for row in ranking),
        "confidence_bounded": all(1 <= int(row["working_confidence_1_to_5"]) <= 5 for row in ranking),
        "actions_valid": all(row["action"] in {"KEEP", "REVISE_PLAINER"} for row in ranking),
        "revision_rows_match": {row["source_slot"] for row in revisions} == {row["source_slot"] for row in ranking if row["action"] == "REVISE_PLAINER"},
        "sealed_pages_absent": all("f84" not in row["unit_uses"].lower() for row in ranking),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (OUT / "VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if result["status"] != "PASS":
        raise SystemExit(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
