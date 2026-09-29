#!/usr/bin/env python3
"""Clearly post-result sensitivity over every frozen one/two image-code union."""
import csv
import hashlib
import itertools
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
HERE = Path(__file__).resolve().parents[1]
OLD = ROOT / "experiments/yolo/gdt1089_head_edit1_organ_blind_holdfolio/artifacts"
WORDS = HERE / "artifacts/ALL_WORDS.tsv"
FEATURES = ("HORIZONTAL_BEADS", "BASAL_SWOLLEN_BRANCHES", "RADIATE_HEAD",
            "SPINY_ROUND_HEAD", "BROAD_PETAL_FLOWER", "MULTI_UNIT_SPIKE")
FIELDS = ("feature_count", "features", "positive_folios", "all_positive_count",
          "all_positive_words", "fair_exact_three_count", "fair_exact_three_words")


def table(path):
    with path.open(newline="") as f:
        return list(csv.DictReader(f, delimiter="\t"))


def calculate():
    a = {r["folio"]: r for r in table(OLD / "BLIND_A.tsv")}
    b = {r["folio"]: r for r in table(OLD / "BLIND_B.tsv")}
    assert len(a) == len(b) == 38 and set(a) == set(b)
    words = table(WORDS)
    assert len(words) == 169
    fair = {r["word"] for r in words if r["admitted_folios"] == "3"
            and r["image_folios"] == "3"}
    assert len(fair) == 5
    rows = []
    for width in (1, 2):
        for fs in itertools.combinations(FEATURES, width):
            positive = {p for p in a if all(any(t[p][f] == "YES" for f in fs)
                        for t in (a, b))}
            hits = sorted(r["word"] for r in words
                if set(r["image_folio_ids"].split(";")) <= positive)
            fair_hits = sorted(set(hits) & fair)
            rows.append(dict(feature_count=width, features="+".join(fs),
                positive_folios=len(positive), all_positive_count=len(hits),
                all_positive_words=";".join(hits) or "-",
                fair_exact_three_count=len(fair_hits),
                fair_exact_three_words=";".join(fair_hits) or "-"))
    result = {
        "status": "POST_RESULT_EXPLORATORY", "feature_sets": len(rows),
        "singletons_with_any_full_word": sum(r["all_positive_count"] > 0 for r in rows if r["feature_count"] == 1),
        "pairs_with_any_full_word": sum(r["all_positive_count"] > 0 for r in rows if r["feature_count"] == 2),
        "schor_full_feature_sets": [r["features"] for r in rows if "schor" in r["all_positive_words"].split(";")],
        "fair_full_words_by_set": {r["features"]: r["fair_exact_three_words"] for r in rows
            if r["fair_exact_three_count"]},
        "input_sha256": {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in (WORDS, OLD / "BLIND_A.tsv", OLD / "BLIND_B.tsv")},
        "ceiling": "Selected words and code unions, no search-wide significance or word meaning."
    }
    return rows, result


def main():
    rows, result = calculate()
    out = HERE / "artifacts"
    with (out / "FEATURE_FAMILY.tsv").open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    (out / "FEATURE_FAMILY_RESULT.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
