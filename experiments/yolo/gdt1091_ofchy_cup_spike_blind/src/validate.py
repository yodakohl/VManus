#!/usr/bin/env python3
"""Replay the fixed join and compare every published cell."""
import csv
import json
from pathlib import Path
from run import compute

ART = Path(__file__).resolve().parents[1] / "artifacts"


def main():
    joined, result = compute()
    with (ART / "JOINED.tsv").open(newline="") as f:
        actual = list(csv.DictReader(f, delimiter="\t"))
    assert actual == joined
    assert json.loads((ART / "RESULT.json").read_text()) == result
    assert len(joined) == 9 and set(result["strict_cup_by_folio"]) == {r["folio"] for r in joined}
    (ART / "VALIDATION.json").write_text(json.dumps({
        "status": "PASS", "joined_rows": 9,
        "checked": "map commitment, nine reader/source rows, every code, decision and result replay"},
        indent=2) + "\n")
    print("PASS")


if __name__ == "__main__":
    main()
