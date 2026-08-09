#!/usr/bin/env python3
"""Source-only capacity audit for explicitly local plant-part descriptions.

This script never reads Voynich strings from the interlinear and computes no
manuscript feature score.  It audits only the public human-annotation atlas.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from collections import Counter
from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[3]
INPUT = Path(
    "experiments/semantic_assumptions/results/"
    "existing_human_exact_locus_annotations.tsv"
)

STRONG = {
    "REL_EXPLICIT_ATTACHMENT",
    "REL_ENCLOSURE",
    "REL_OVERLAP_OR_CONTACT",
}

TERMS = {
    "ROOT": re.compile(r"\b(root|roots|rhizome|tuber|bulb)\b", re.I),
    "LEAF": re.compile(r"\b(leaf|leaves|foliage)\b", re.I),
    "FLOWER": re.compile(r"\b(flower|flowers|bloom|blooms|petal|petals)\b", re.I),
    "STEM": re.compile(r"\b(stem|stalk|stems|stalks)\b", re.I),
    "FRUIT": re.compile(r"\b(fruit|fruits|berry|berries|seed|seeds)\b", re.I),
}


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    source = ROOT / INPUT
    with source.open(newline="", encoding="utf-8") as handle:
        all_rows = list(csv.DictReader(handle, delimiter="\t"))

    selected: list[dict[str, object]] = []
    for row in all_rows:
        relations = set(filter(None, row["local_relation_tags"].split(";")))
        tags = set(filter(None, row["object_tags"].split(";")))
        hits = [name for name, pattern in TERMS.items() if pattern.search(row["local_comment"])]
        if not (
            row["certainty"] == "UNHEDGED"
            and row["relation_scope"] == "EXACT_LOCAL_COMMENT"
            and "PLANT" in tags
            and relations & STRONG
            and hits
        ):
            continue
        selected.append(
            {
                "page": row["page"],
                "locus": row["locus"],
                "terms": hits,
                "editorial_label": "LABEL" in tags,
                "normalized_code": row["normalized_code"],
                "relation_tags": sorted(relations),
            }
        )

    term_summary = {}
    for term in TERMS:
        rows = [row for row in selected if term in row["terms"]]
        term_summary[term] = {
            "rows": len(rows),
            "pages": len({str(row["page"]) for row in rows}),
            "loci": [str(row["locus"]) for row in rows],
        }

    result = {
        "status": "STOP_NO_REPLICATED_OWNED_PLANT_PART_CONTRAST",
        "source": str(INPUT),
        "source_sha256": sha256(source),
        "selection": {
            "certainty": "UNHEDGED",
            "scope": "EXACT_LOCAL_COMMENT",
            "required_object_tag": "PLANT",
            "strong_relation_any": sorted(STRONG),
            "term_families": list(TERMS),
        },
        "selected_rows": len(selected),
        "selected_pages": len({str(row["page"]) for row in selected}),
        "editorial_label_rows": sum(bool(row["editorial_label"]) for row in selected),
        "explicit_attachment_rows": sum(
            "REL_EXPLICIT_ATTACHMENT" in row["relation_tags"] for row in selected
        ),
        "relation_tagsets": dict(
            sorted(Counter(";".join(row["relation_tags"]) for row in selected).items())
        ),
        "terms": term_summary,
        "rows": selected,
        "decision": {
            "minimum_independent_folios": 5,
            "minimum_readable_classes": 2,
            "minimum_owned_examples_per_class": 3,
            "admitted": False,
            "reason": (
                "zero explicit-attachment rows; apparent part mentions are sparse and "
                "require source-level ownership adjudication"
            ),
        },
    }

    # Frozen internal reconstruction guards.
    assert result["selected_rows"] == 8
    assert result["selected_pages"] == 5
    assert result["editorial_label_rows"] == 5
    assert result["explicit_attachment_rows"] == 0
    assert term_summary["ROOT"]["rows"] == 2
    assert term_summary["LEAF"]["rows"] == 3
    assert term_summary["FLOWER"]["rows"] == 2
    assert term_summary["STEM"]["rows"] == 3
    assert term_summary["FRUIT"]["rows"] == 0

    payload = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.output:
        output = args.output if args.output.is_absolute() else ROOT / args.output
        output.write_text(payload, encoding="utf-8")
    else:
        print(payload, end="")


if __name__ == "__main__":
    main()
