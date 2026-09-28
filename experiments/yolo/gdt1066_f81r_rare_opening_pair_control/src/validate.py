#!/usr/bin/env python3
"""Independent replay of the fixed major-record first-five occurrence table."""
import csv
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
HERE = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "experiments/yolo/gdt791_thirty_page_visual_owner_spine/artifacts/GDT791_5866_OCCURRENCE_SPINE.tsv"
EXPECTED = {
    "f77r": ["F77_P1", "F77_P2", "F77_P3"],
    "f81r": ["F81R_UPPER_POOL", "F81R_LOWER_POOL"],
    "f82r": ["F82_P1", "F82_P2", "F82_P3"],
    "f83r": ["F83_P1", "F83_P2", "F83_P3", "F83_P4", "F83_P5"],
}


def main():
    result = json.loads((HERE / "artifacts/RESULT.json").read_text())
    source_bytes = SOURCE.read_bytes()
    assert result["source_sha256"] == hashlib.sha256(source_bytes).hexdigest()
    counts = Counter()
    by_owner = defaultdict(list)
    for row in csv.DictReader(source_bytes.decode("utf-8").splitlines(), delimiter="\t"):
        if row["occurrence_kind"] != "RUNNING_EVENT":
            continue
        word = row["surface"]
        counts[word] += 1
        page = row["physical_page"]
        if page in EXPECTED:
            owner = row["legacy_owner"] if page == "f81r" else row["record_id"]
            if owner in EXPECTED[page]:
                by_owner[(page, owner)].append(word)
    expected_pairs = [(page, a, b) for page, owners in EXPECTED.items() for a, b in zip(owners, owners[1:])]
    assert len(expected_pairs) == result["pair_count"] == 9
    assert result["selection_status"] == "POST_HOC_DESCRIPTIVE_ONLY"
    rare_count = 0
    for row, (page, a, b) in zip(result["pairs"], expected_pairs):
        left, right = by_owner[(page, a)], by_owner[(page, b)]
        assert (row["page"], row["left"], row["right"]) == (page, a, b)
        assert (row["left_tokens"], row["right_tokens"]) == (len(left), len(right))
        assert row["first_five_left"] == left[:5] and row["first_five_right"] == right[:5]
        shared = sorted(set(left[:5]).intersection(right[:5]))
        assert row["shared_first_five"] == shared
        assert row["shared_frequency_in_30_pages"] == {w: counts[w] for w in shared}
        assert row["rare_shared_first_five"] == [w for w in shared if counts[w] <= 4]
        rare_count += bool(row["rare_shared_first_five"])
    assert rare_count == result["rare_pair_count"] == 1
    assert result["pairs"][2]["rare_shared_first_five"] == ["olpchedy"]
    receipt = {"status": "PASS", "checks": "source hash, scope, nine pair owners, all lengths/openings/shared forms/frequencies, one rare pair", "rare_pair_count": rare_count}
    (HERE / "artifacts/VALIDATION.json").write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    print(json.dumps(receipt, sort_keys=True))


if __name__ == "__main__":
    main()
