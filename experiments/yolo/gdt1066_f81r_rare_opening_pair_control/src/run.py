#!/usr/bin/env python3
"""Descriptive, post-selection opening-pair census from admitted GDT791 events."""
import collections
import csv
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
HERE = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "experiments/yolo/gdt791_thirty_page_visual_owner_spine/artifacts/GDT791_5866_OCCURRENCE_SPINE.tsv"
ORDER = {
    "f77r": ("F77_P1", "F77_P2", "F77_P3"),
    "f81r": ("F81R_UPPER_POOL", "F81R_LOWER_POOL"),
    "f82r": ("F82_P1", "F82_P2", "F82_P3"),
    "f83r": ("F83_P1", "F83_P2", "F83_P3", "F83_P4", "F83_P5"),
}


def build():
    raw = SOURCE.read_bytes()
    events = list(csv.DictReader(raw.decode("utf-8").splitlines(), delimiter="\t"))
    running = [r for r in events if r["occurrence_kind"] == "RUNNING_EVENT"]
    frequency = collections.Counter(r["surface"] for r in running)
    groups = {page: {name: [] for name in names} for page, names in ORDER.items()}
    for row in running:
        page = row["physical_page"]
        if page not in groups:
            continue
        owner = row["legacy_owner"] if page == "f81r" else row["record_id"]
        if owner in groups[page]:
            groups[page][owner].append(row["surface"])
    pairs = []
    for page, names in ORDER.items():
        for left, right in zip(names, names[1:]):
            a, b = groups[page][left], groups[page][right]
            assert len(a) >= 5 and len(b) >= 5, (page, left, right)
            shared = sorted(set(a[:5]) & set(b[:5]))
            pairs.append({
                "page": page, "left": left, "right": right,
                "left_tokens": len(a), "right_tokens": len(b),
                "first_five_left": a[:5], "first_five_right": b[:5],
                "shared_first_five": shared,
                "rare_shared_first_five": [w for w in shared if frequency[w] <= 4],
                "shared_frequency_in_30_pages": {w: frequency[w] for w in shared},
            })
    return {
        "source_sha256": hashlib.sha256(raw).hexdigest(),
        "scope": "GDT791 ZL3b running events; four pool/apparatus pages with fixed major record owners",
        "selection_status": "POST_HOC_DESCRIPTIVE_ONLY",
        "rare_cutoff": 4, "opening_width": 5,
        "pairs": pairs,
        "pair_count": len(pairs),
        "rare_pair_count": sum(bool(p["rare_shared_first_five"]) for p in pairs),
    }


def main():
    result = build()
    assert result["pair_count"] == 9
    target = [p for p in result["pairs"] if p["page"] == "f81r"]
    assert len(target) == 1 and target[0]["rare_shared_first_five"] == ["olpchedy"]
    path = HERE / "artifacts/RESULT.json"
    path.write_text(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n")
    print(path.relative_to(ROOT))


if __name__ == "__main__":
    main()
