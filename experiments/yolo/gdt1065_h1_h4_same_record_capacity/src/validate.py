#!/usr/bin/env python3
"""Independently reconstruct the capacity from GDT790's line artifact."""
import csv
import json
from collections import defaultdict
from pathlib import Path


BASE = Path(__file__).resolve().parents[1]
ROOT = BASE.parents[2]
GRID = ROOT / "experiments/yolo/gdt735_historical_semantic_bridge_atlas/artifacts/OPAQUE_96_HEAD_BODY_GRID.tsv"
LINES = ROOT / "experiments/yolo/gdt790_panel_owner_image_grammar_overlay/artifacts/GDT790_123_IMAGE_AWARE_LINES.tsv"


def tsv(path):
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main():
    result = json.loads((BASE / "artifacts/RESULT.json").read_text(encoding="utf-8"))
    grid = tsv(GRID)
    lines = tsv(LINES)
    assert len(lines) == 123
    byform = {r["form"]: (r["opaque_head_id"], r["body"]) for r in grid}
    records = defaultdict(list)
    for row in lines:
        assert row["page"] in {"f77r", "f82r", "f83r"}
        key = (row["page"], row["record_id"])
        for linepos, word in enumerate(row["zl3b_line"].split(), 1):
            records[key].append((row["locus"], linepos, word))
    assert len(records) == 13 and sum(map(len, records.values())) == 940
    found = set()
    for (page, record), tokens in records.items():
        for i, (hloc, hpos, word1) in enumerate(tokens):
            if word1 not in byform or byform[word1][0] != "H1":
                continue
            for j in range(i + 1, len(tokens)):
                zloc, zpos, word4 = tokens[j]
                if word4 not in byform or byform[word4] != ("H4", byform[word1][1]):
                    continue
                found.add((page, record, byform[word1][1], hloc, i + 1, hpos,
                           zloc, j + 1, zpos, tuple(w for _, _, w in tokens[i + 1:j])))
    saved = {(r["page"], r["record_id"], r["body"], r["h1_locus"],
              r["h1_record_position"], r["h1_line_position"], r["h4_locus"],
              r["h4_record_position"], r["h4_line_position"],
              tuple(r["intervening_surfaces"])) for r in result["pairs"]}
    assert found == saved, (found ^ saved)
    assert len(found) == result["counts"]["ordered_same_body_pairs"] == 4
    assert sum(i == 1 and zpos > 1 for _, _, _, _, i, _, _, _, zpos, _ in found) == 0
    assert result["counts"]["strict_eligible_pairs"] == 0
    assert {r["record_id"] for r in result["records"]} == {r for _, r in records}
    print("PASS: GDT790 independent-line reconstruction matches all four pairs and zero strict capacity")


if __name__ == "__main__":
    main()
