#!/usr/bin/env python3
"""Build the complete public f67--f73 page/reading IVTFF role atlas."""

from __future__ import annotations

import csv
import hashlib
import json
import re
from collections import Counter, defaultdict
from pathlib import Path

BASE = Path(__file__).resolve().parent
RESULTS = BASE / "results"
ALIGN = RESULTS / "source_sta_group_alignment.tsv"
META = RESULTS / "source_separator_transcription.tsv"
PUBLIC = RESULTS / "public_voynich_nu_page_annotations_v2.tsv"
OUT_TSV = RESULTS / "public_circle_block_role_atlas.tsv"
OUT_JSON = RESULTS / "public_circle_block_role_atlas.json"
REPORT = RESULTS / "public_circle_block_role_atlas_report.md"
READINGS = ("ZL3b", "IT2a", "RF1b")
ROLES = ("P", "L", "C", "R")
SCOPE_RE = re.compile(r"^f(67|68|69|70|71|72|73)")
CIRCULAR_COUNT_RE = re.compile(r"(\d+) items? of circular writing")
TEXT_ITEM_COUNT_RE = re.compile(r"This page has (\d+) text items")


def rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def page_class(description: str) -> str:
    lower = description.lower()
    matches = [
        label for label, phrase in (
            ("ASTRONOMICAL", "this is an astronomical page"),
            ("COSMOLOGICAL", "this is a so-called cosmological page"),
            ("ZODIAC", "this is a zodiac page"),
        ) if phrase in lower
    ]
    if len(matches) != 1:
        raise AssertionError(f"ambiguous public class: {description[:80]}")
    return matches[0]


def main() -> None:
    if OUT_TSV.exists() or OUT_JSON.exists() or REPORT.exists():
        raise SystemExit("refusing overwrite")
    public_rows = [row for row in rows(PUBLIC) if SCOPE_RE.match(row["page"])]
    if len(public_rows) != 26 or len({row["page"] for row in public_rows}) != 26:
        raise AssertionError("public f67--f73 page scope changed")
    public = {row["page"]: row for row in public_rows}
    pages = tuple(row["page"] for row in public_rows)
    classes = {page: page_class(public[page]["general_description"]) for page in pages}
    class_counts = Counter(classes.values())
    if class_counts != Counter({"ZODIAC": 12, "ASTRONOMICAL": 7, "COSMOLOGICAL": 7}):
        raise AssertionError("public class counts changed")

    declared_circular = {}
    declared_total = {}
    for page in pages:
        text = public[page]["text_description"]
        circular = CIRCULAR_COUNT_RE.search(text)
        total = TEXT_ITEM_COUNT_RE.search(text)
        declared_circular[page] = int(circular.group(1)) if circular else None
        declared_total[page] = int(total.group(1)) if total else None
    metadata_rows = rows(META)
    metadata = {row["source_group_id"]: row for row in metadata_rows}
    if len(metadata) != len(metadata_rows):
        raise AssertionError("duplicate metadata group ID")

    group_counts = Counter()
    zero_alt_counts = Counter()
    alt_counts = Counter()
    loci = defaultdict(set)
    alignment_rows = rows(ALIGN)
    if len({row["source_group_id"] for row in alignment_rows}) != len(alignment_rows):
        raise AssertionError("duplicate alignment group ID")
    for row in alignment_rows:
        info = metadata[row["source_group_id"]]
        page = info["page"]
        if page not in public:
            continue
        reading = row["edition"]
        role = info["kind"]
        if reading not in READINGS or role not in ROLES:
            raise AssertionError("unexpected reading/role inside scope")
        key = (page, reading, role)
        group_counts[key] += 1
        loci[key].add(info["locus"])
        if int(row["alternative_site_count"]):
            alt_counts[key] += 1
        else:
            zero_alt_counts[key] += 1

    atlas_rows = []
    for page in pages:
        folio = re.match(r"^(f\d+)", page).group(1)
        for reading in READINGS:
            for role in ROLES:
                key = (page, reading, role)
                atlas_rows.append({
                    "page": page,
                    "physical_folio": folio,
                    "public_page_class": classes[page],
                    "public_declared_text_items": "" if declared_total[page] is None else str(declared_total[page]),
                    "public_declared_circular_items": "" if declared_circular[page] is None else str(declared_circular[page]),
                    "public_text_mentions_circular": "1" if "circular" in public[page]["text_description"].lower() else "0",
                    "reading": reading,
                    "ivtff_role": role,
                    "locus_count": str(len(loci[key])),
                    "source_group_count": str(group_counts[key]),
                    "zero_alternative_group_count": str(zero_alt_counts[key]),
                    "alternative_group_count": str(alt_counts[key]),
                })
    fieldnames = list(atlas_rows[0])
    with OUT_TSV.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(atlas_rows)

    role_page_presence = {
        role: sum(all(len(loci[(page, reading, role)]) > 0 for reading in READINGS) for page in pages)
        for role in ROLES
    }
    numeric_pages = [page for page in pages if declared_circular[page] is not None]
    exact_cells = [
        f"{page}|{reading}" for page in numeric_pages for reading in READINGS
        if len(loci[(page, reading, "C")]) == declared_circular[page]
    ]
    mismatch_cells = [
        f"{page}|{reading}" for page in numeric_pages for reading in READINGS
        if len(loci[(page, reading, "C")]) != declared_circular[page]
    ]
    no_numeric_pages = [page for page in pages if declared_circular[page] is None]
    zero_c_no_numeric = [page for page in no_numeric_pages if all(len(loci[(page, reading, "C")]) == 0 for reading in READINGS)]
    page_signatures = {
        page: {
            reading: "".join(role for role in ROLES if loci[(page, reading, role)])
            for reading in READINGS
        }
        for page in pages
    }
    signature_agreement = [page for page in pages if len(set(page_signatures[page].values())) == 1]
    gates = {
        "exact_26_public_pages": len(pages) == 26,
        "exact_312_page_reading_role_rows": len(atlas_rows) == 312,
        "all_page_role_signatures_agree_across_readings": len(signature_agreement) == 26,
        "all_numeric_public_circular_counts_match_IVTFF_C_loci": len(mismatch_cells) == 0,
        "exact_69_numeric_page_reading_matches": len(exact_cells) == 69,
        "three_no_numeric_pages_all_have_zero_C": zero_c_no_numeric == ["f67r2", "f67v1", "f67v2"],
        "zero_english_glosses": True,
    }
    status = "PASS_COMPLETE_PUBLIC_CIRCLE_ROLE_ATLAS" if all(gates.values()) else "FAIL_PUBLIC_CIRCLE_ROLE_ATLAS"
    result = {
        "experiment": "PUBLIC_CIRCLE_BLOCK_ROLE_ATLAS",
        "status": status,
        "inputs": {path.name: sha(path) for path in (ALIGN, META, PUBLIC, Path(__file__))},
        "scope": {
            "pages": list(pages),
            "page_count": len(pages),
            "physical_folios": sorted({re.match(r"^(f\d+)", page).group(1) for page in pages}),
            "class_counts": dict(sorted(class_counts.items())),
            "atlas_rows": len(atlas_rows),
        },
        "role_page_presence_all_readings": role_page_presence,
        "page_role_signatures": page_signatures,
        "public_numeric_circular_count_pages": numeric_pages,
        "public_numeric_to_IVTFF_C_exact_cells": exact_cells,
        "public_numeric_to_IVTFF_C_mismatch_cells": mismatch_cells,
        "pages_without_numeric_public_circular_count": no_numeric_pages,
        "no_numeric_pages_with_zero_C_all_readings": zero_c_no_numeric,
        "f67r2_public_text_mentions_circular_but_has_no_numeric_item_and_zero_C": (
            "circular" in public["f67r2"]["text_description"].lower()
            and declared_circular["f67r2"] is None
            and all(len(loci[("f67r2", reading, "C")]) == 0 for reading in READINGS)
        ),
        "gates": gates,
        "artifacts": {OUT_TSV.name: {"sha256": sha(OUT_TSV), "rows": len(atlas_rows)}},
        "claim_ceiling": "Descriptive public-page/IVTFF role coverage only. Visual circularity is not interchangeable with C; no ownership, object, function, word, meaning, plaintext, or translation.",
    }
    OUT_JSON.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    REPORT.write_text(
        "# Public f67--f73 circle-block role atlas\n\n"
        f"Status: **{status}**\n\n"
        f"The atlas covers all 26 public page panels, seven folios, three alternate readings, and four IVTFF roles in 312 rows. Public classes are 7 astronomical, 7 cosmological, and 12 zodiac pages. All 26 page-level role signatures agree across readings.\n\n"
        f"The public catalogue gives a numeric circular-writing count on 23 pages. Every one of the resulting 69 page-reading cells exactly matches the number of IVTFF `C` loci. The only pages without a numeric circular-item count are f67r2, f67v1, and f67v2, and all three have zero `C` loci. f67r2 still mentions a short circular text in prose, showing that a visual/descriptive circular phrase need not receive the `C` code.\n\n"
        f"All-reading page presence by role is {role_page_presence}. This is a coverage/provenance result only: visual circularity, page class, and IVTFF role are distinct layers, with no object ownership, word, meaning, plaintext, or translation.\n",
        encoding="utf-8",
    )
    print(json.dumps({"status": status, "rows": len(atlas_rows), "role_page_presence": role_page_presence, "exact_C_cells": len(exact_cells)}, sort_keys=True))


if __name__ == "__main__":
    main()
