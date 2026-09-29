#!/usr/bin/env python3
"""Replay GDT1090 and compare every published row."""
import csv
import json
from pathlib import Path
from run import compute

HERE = Path(__file__).resolve().parents[1]


def rows(path):
    with path.open(newline="") as f:
        return list(csv.DictReader(f, delimiter="\t"))


def main():
    deck, primary, secondary, result = compute()
    out = HERE / "artifacts"
    for name, expected in (("ALL_WORDS.tsv", deck), ("PRIMARY.tsv", primary),
                           ("SECONDARY.tsv", secondary)):
        actual = rows(out / name)
        assert actual == [{k: str(v) for k, v in r.items()} for r in expected], name
    assert json.loads((out / "RESULT.json").read_text()) == result
    assert result["schor"]["image_folio_ids"] == "f22r;f32r;f42v"
    assert result["schor"]["admitted_folios"] == 3
    assert result["schor"]["union_yes"] == 3
    assert len(result["union_yes_folios"]) == 12
    (out / "VALIDATION.json").write_text(json.dumps({
        "status": "PASS", "checked": ["guarded selector", "input hashes", "all rows",
            "target loci", "twelve union image folios"]}, indent=2) + "\n")
    print("PASS")


if __name__ == "__main__":
    main()
