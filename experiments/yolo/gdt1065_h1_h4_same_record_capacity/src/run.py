#!/usr/bin/env python3
"""Fixed 24-body H1/H4 same-record capacity on the existing guarded spine."""
import csv
import hashlib
import json
from collections import defaultdict
from pathlib import Path


BASE = Path(__file__).resolve().parents[1]
ROOT = BASE.parents[2]
GRID = ROOT / "experiments/yolo/gdt735_historical_semantic_bridge_atlas/artifacts/OPAQUE_96_HEAD_BODY_GRID.tsv"
SPINE = ROOT / "experiments/yolo/gdt791_thirty_page_visual_owner_spine/artifacts/GDT791_5866_OCCURRENCE_SPINE.tsv"
OUT = BASE / "artifacts"
PAGES = {"f77r", "f82r", "f83r"}
HASHES = {
    "grid": "3fde00498dfce188dbf4df00027bef5c5a8293cd173722f6b4cfb3ca024a1871",
    "spine": "4075ffca8e7a8b9cefda62c9ec6997fb6c518dba8f86790f5309bfe2a8574707",
}


def read_tsv(path):
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main():
    assert hashlib.sha256(GRID.read_bytes()).hexdigest() == HASHES["grid"]
    assert hashlib.sha256(SPINE.read_bytes()).hexdigest() == HASHES["spine"]
    grid = read_tsv(GRID)
    spine = read_tsv(SPINE)
    assert len(grid) == 96 and len({r["body"] for r in grid}) == 24
    assert len(spine) == 5866
    form = {r["form"]: (r["opaque_head_id"], r["body"]) for r in grid}
    assert len(form) == 96

    # Select the fixed GDT791 physical record frame before form matching.
    records = defaultdict(list)
    for row in spine:
        if (row["physical_page"] in PAGES and
                row["occurrence_kind"] == "RUNNING_EVENT" and
                row["record_id"] != "NONE"):
            records[(row["physical_page"], row["record_id"])].append(row)
    assert len(records) == 13
    assert sum(map(len, records.values())) == 940

    pairs = []
    record_rows = []
    for (page, record), tokens in sorted(records.items()):
        tokens.sort(key=lambda r: int(r["occurrence_ordinal"]))
        hits = [(i, row, *form[row["surface"]])
                for i, row in enumerate(tokens) if row["surface"] in form]
        local = 0
        for i, h1, head1, body1 in hits:
            if head1 != "H1":
                continue
            for j, h4, head4, body4 in hits:
                if head4 != "H4" or body1 != body4 or j <= i:
                    continue
                strict = i == 0 and int(h4["token_ordinal_in_line"]) > 1
                pairs.append({
                    "page": page, "record_id": record, "body": body1,
                    "h1_surface": h1["surface"], "h1_locus": h1["locus"],
                    "h1_record_position": i + 1,
                    "h1_line_position": int(h1["token_ordinal_in_line"]),
                    "h4_surface": h4["surface"], "h4_locus": h4["locus"],
                    "h4_record_position": j + 1,
                    "h4_line_position": int(h4["token_ordinal_in_line"]),
                    "intervening_surfaces": [r["surface"] for r in tokens[i + 1:j]],
                    "strict_eligible": strict,
                })
                local += 1
        record_rows.append({"page": page, "record_id": record,
                            "first_surface": tokens[0]["surface"],
                            "tokens": len(tokens), "grid_hits": len(hits),
                            "ordered_same_body_pairs": local})
    assert sum(r["grid_hits"] for r in record_rows) == 88
    result = {"experiment_id": "GDT1065", "scope": "13 fixed deep-page records; ZL3b structural capacity",
              "input_sha256": HASHES, "records": record_rows, "pairs": pairs,
              "counts": {"records": 13, "running_tokens": 940, "grid_hits": 88,
                         "ordered_same_body_pairs": len(pairs),
                         "strict_eligible_pairs": sum(p["strict_eligible"] for p in pairs)},
              "decision": "ZERO_STRICT_SAME_RECORD_OPENING_H1_TO_INTERNAL_H4_CAPACITY_NO_MEANING_TEST"}
    OUT.mkdir(exist_ok=True)
    (OUT / "RESULT.json").write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(result["counts"], sort_keys=True))


if __name__ == "__main__":
    main()
