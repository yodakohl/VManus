#!/usr/bin/env python3
"""Consistency checks for controlled paraphrases of blocked compounds."""

from __future__ import annotations

import csv
import json
from collections import Counter
from pathlib import Path


OUT = Path(__file__).resolve().parent


def read(name: str) -> list[dict[str, str]]:
    with (OUT / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> None:
    rows = read("FORTY_NINTH_17_CONTROLLED_PARAPHRASES.tsv")
    copies = read("FORTY_NINTH_68_SCRIBE_COPIES.tsv")
    per_cell = Counter(row["cell_id"] for row in copies)
    checks = {
        "seventeen_paraphrases": len(rows) == 17,
        "blocked_sequences_unique": len({row["blocked_fused_atom_sequence"] for row in rows}) == 17,
        "all_cards_observed": all(row["all_cards_individually_observed"] == "YES" for row in rows),
        "no_complete_chain_claim": all(row["complete_chain_observed"] == "NO" for row in rows),
        "no_exact_equivalence_claim": all(row["exact_semantic_equivalence"].startswith("NO_") for row in rows),
        "no_new_surface": all(row["new_surface_invented"] == "NO" for row in rows),
        "one_or_two_cards": all(int(row["paraphrase_card_count"]) in {1, 2} for row in rows),
        "sixty_eight_copies": len(copies) == 68,
        "four_copies_each": all(per_cell[row["cell_id"]] == 4 for row in rows),
        "copy_surfaces_observed": all(row["all_surfaces_observed"] == "YES" and row["new_surface_invented"] == "NO" for row in copies),
        "book_exists": (OUT / "FORTY_NINTH_CONTROLLED_PARAPHRASE_BOOK.md").exists(),
        "sealed_absent": not any("f84" in path.name.lower() for path in OUT.iterdir()),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (OUT / "VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if result["status"] != "PASS":
        raise SystemExit(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
