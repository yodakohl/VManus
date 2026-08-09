#!/usr/bin/env python3
"""Reproduce the exposed f57v.8 / f77v.3 cross-page form audit.

This is a descriptive source audit, not a preregistered significance test.
It reads manual transcriptions and human annotations only.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
INTERLINEAR = Path(
    "experiments/semantic_assumptions/results/pre_grounding_interlinear.tsv"
)
EXACT_ANNOTATIONS = Path(
    "experiments/semantic_assumptions/results/existing_human_exact_locus_annotations.tsv"
)
LABEL_ANNOTATIONS = Path(
    "experiments/semantic_assumptions/results/existing_human_label_annotations.tsv"
)
LOCI = ("f57v.8", "f77v.3")
EDITIONS = ("ZL3b", "IT2a", "RF1b")


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def word_has_ol_k(root_sequence: str) -> bool:
    return any({"ol", "k"} <= set(word.split("+")) for word in root_sequence.split())


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    interlinear_path = ROOT / INTERLINEAR
    exact_path = ROOT / EXACT_ANNOTATIONS
    label_path = ROOT / LABEL_ANNOTATIONS
    interlinear = read_tsv(interlinear_path)
    exact = read_tsv(exact_path)
    labels = read_tsv(label_path)

    by_locus: dict[str, dict[str, dict[str, str]]] = defaultdict(dict)
    for row in interlinear:
        by_locus[row["locus"]][row["edition"]] = row

    target_rows = []
    for locus in LOCI:
        for edition in EDITIONS:
            row = by_locus[locus][edition]
            target_rows.append(
                {
                    "locus": locus,
                    "edition": edition,
                    "surface": row["surface"],
                    "root_sequence": row["root_sequence"],
                    "role_sequence": row["role_sequence"],
                    "code": row["code"],
                }
            )

    exact_surface_equal = {
        edition: (
            by_locus[LOCI[0]][edition]["surface"]
            == by_locus[LOCI[1]][edition]["surface"]
        )
        for edition in EDITIONS
    }
    shared_ol_k = {
        edition: all(word_has_ol_k(by_locus[locus][edition]["root_sequence"]) for locus in LOCI)
        for edition in EDITIONS
    }

    complete = []
    for locus, edition_rows in by_locus.items():
        if set(edition_rows) != set(EDITIONS):
            continue
        if all(word_has_ol_k(edition_rows[edition]["root_sequence"]) for edition in EDITIONS):
            complete.append(locus)

    kind_l = [locus for locus in complete if by_locus[locus]["ZL3b"]["kind"] == "L"]

    keedal_counts = {}
    for edition in EDITIONS:
        hits = []
        for row in interlinear:
            if row["edition"] != edition:
                continue
            for word in row["surface"].split():
                if "keedal" in word:
                    hits.append(
                        {
                            "locus": row["locus"],
                            "section": row["section"],
                            "code": row["code"],
                            "surface": word,
                        }
                    )
        keedal_counts[edition] = {"count": len(hits), "hits": hits}

    exact_target_annotations = [
        {
            "locus": row["locus"],
            "unit_description": row["unit_description"],
            "local_comment": row["local_comment"],
            "local_relation_tags": row["local_relation_tags"],
            "unit_relation_tags": row["unit_relation_tags"],
            "certainty": row["certainty"],
            "relation_scope": row["relation_scope"],
        }
        for row in exact
        if row["locus"] in LOCI
    ]

    legacy = [
        {
            "source_record_id": row["source_record_id"],
            "page": row["page"],
            "location": row["location"],
            "transcriber_code": row["transcriber_code"],
            "comments": row["comments"],
        }
        for row in labels
        if row["source_record_id"] in {"STOLFI_BEST_0050", "STOLFI_BEST_0877"}
    ]

    result = {
        "status": "PROVISIONAL_TRANSCRIPTION_SENSITIVE_COLD_POSITION_FORM_CANDIDATE",
        "exposure": "POSTHOC_DESCRIPTIVE_NO_SIGNIFICANCE_TEST",
        "inputs": {
            str(INTERLINEAR): sha256(interlinear_path),
            str(EXACT_ANNOTATIONS): sha256(exact_path),
            str(LABEL_ANNOTATIONS): sha256(label_path),
        },
        "target_rows": target_rows,
        "exact_surface_equal_by_edition": exact_surface_equal,
        "shared_ol_plus_k_by_edition": shared_ol_k,
        "all_reading_ol_plus_k_word_loci": len(complete),
        "all_reading_ol_plus_k_word_pages": len(
            {by_locus[locus]["ZL3b"]["page"] for locus in complete}
        ),
        "all_reading_ol_plus_k_kind_L_loci": len(kind_l),
        "all_reading_ol_plus_k_kind_L_pages": len(
            {by_locus[locus]["ZL3b"]["page"] for locus in kind_l}
        ),
        "all_reading_ol_plus_k_kind_L_members": kind_l,
        "keedal_family": keedal_counts,
        "exact_human_annotations": exact_target_annotations,
        "legacy_label_rows": legacy,
        "decision": {
            "retain": (
                "f57v.8 COLD-position and f77v.3 cross-page form candidate"
            ),
            "reject": [
                "ol equals COLD",
                "k equals COLD",
                "ol+k equals COLD",
                "olkeedal is a confirmed lexeme",
                "f77v.3 has a securely owned cold referent",
            ],
            "reopen_only_if": (
                "a third independent explicitly owned HOT/MOIST/COLD/DRY value "
                "is frozen before its Voynich string, or f77v.3 ownership is "
                "resolved by new author-visible evidence"
            ),
        },
    }

    # Frozen reconstruction guards.
    assert exact_surface_equal == {"ZL3b": True, "IT2a": False, "RF1b": False}
    assert all(shared_ol_k.values())
    assert len(complete) == 418
    assert len({by_locus[locus]["ZL3b"]["page"] for locus in complete}) == 95
    assert len(kind_l) == 16
    assert len({by_locus[locus]["ZL3b"]["page"] for locus in kind_l}) == 14
    assert {edition: keedal_counts[edition]["count"] for edition in EDITIONS} == {
        "ZL3b": 16,
        "IT2a": 15,
        "RF1b": 11,
    }
    assert len(exact_target_annotations) == 2
    assert len(legacy) == 2

    payload = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.output:
        output = args.output if args.output.is_absolute() else ROOT / args.output
        output.write_text(payload, encoding="utf-8")
    else:
        print(payload, end="")


if __name__ == "__main__":
    main()
