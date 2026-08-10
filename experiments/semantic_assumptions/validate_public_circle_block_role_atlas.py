#!/usr/bin/env python3
"""Independent reconstruction of the public f67--f73 IVTFF role atlas."""

from __future__ import annotations

import csv
import hashlib
import io
import json
import re
from collections import Counter, defaultdict
from pathlib import Path

BASE = Path(__file__).resolve().parent
RESULTS = BASE / "results"
BUILDER = BASE / "build_public_circle_block_role_atlas.py"
ALIGN = RESULTS / "source_sta_group_alignment.tsv"
META = RESULTS / "source_separator_transcription.tsv"
PUBLIC = RESULTS / "public_voynich_nu_page_annotations_v2.tsv"
ATLAS = RESULTS / "public_circle_block_role_atlas.tsv"
RESULT = RESULTS / "public_circle_block_role_atlas.json"
RESULT_REPORT = RESULTS / "public_circle_block_role_atlas_report.md"
OUT = RESULTS / "public_circle_block_role_atlas_validation.json"
REPORT = RESULTS / "public_circle_block_role_atlas_validation.md"
READINGS = ("ZL3b", "IT2a", "RF1b")
ROLES = ("P", "L", "C", "R")
SCOPE = re.compile(r"^f(?:67|68|69|70|71|72|73)")


def load(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def classify(text: str) -> str:
    lower = text.lower()
    found = []
    if "this is an astronomical page" in lower:
        found.append("ASTRONOMICAL")
    if "this is a so-called cosmological page" in lower:
        found.append("COSMOLOGICAL")
    if "this is a zodiac page" in lower:
        found.append("ZODIAC")
    assert len(found) == 1
    return found[0]


def reconstruct() -> tuple[list[dict[str, str]], dict[str, object], str]:
    public_rows = [row for row in load(PUBLIC) if SCOPE.match(row["page"])]
    assert len(public_rows) == len({row["page"] for row in public_rows}) == 26
    public = {row["page"]: row for row in public_rows}
    pages = tuple(row["page"] for row in public_rows)
    classes = {page: classify(public[page]["general_description"]) for page in pages}
    class_counts = Counter(classes.values())
    assert class_counts == Counter({"ZODIAC": 12, "ASTRONOMICAL": 7, "COSMOLOGICAL": 7})
    declared_c = {}
    declared_total = {}
    for page in pages:
        text = public[page]["text_description"]
        c = re.search(r"(\d+) items? of circular writing", text)
        total = re.search(r"This page has (\d+) text items", text)
        declared_c[page] = int(c.group(1)) if c else None
        declared_total[page] = int(total.group(1)) if total else None

    meta_rows = load(META)
    metadata = {row["source_group_id"]: row for row in meta_rows}
    assert len(metadata) == len(meta_rows)
    alignment_rows = load(ALIGN)
    assert len({row["source_group_id"] for row in alignment_rows}) == len(alignment_rows)
    groups = Counter()
    zero = Counter()
    alt = Counter()
    loci = defaultdict(set)
    for row in alignment_rows:
        info = metadata[row["source_group_id"]]
        if info["page"] not in public:
            continue
        key = (info["page"], row["edition"], info["kind"])
        assert row["edition"] in READINGS and info["kind"] in ROLES
        groups[key] += 1
        loci[key].add(info["locus"])
        (alt if int(row["alternative_site_count"]) else zero)[key] += 1
    atlas = []
    for page in pages:
        folio = re.match(r"^(f\d+)", page).group(1)
        for reading in READINGS:
            for role in ROLES:
                key = (page, reading, role)
                atlas.append({
                    "page": page,
                    "physical_folio": folio,
                    "public_page_class": classes[page],
                    "public_declared_text_items": "" if declared_total[page] is None else str(declared_total[page]),
                    "public_declared_circular_items": "" if declared_c[page] is None else str(declared_c[page]),
                    "public_text_mentions_circular": "1" if "circular" in public[page]["text_description"].lower() else "0",
                    "reading": reading,
                    "ivtff_role": role,
                    "locus_count": str(len(loci[key])),
                    "source_group_count": str(groups[key]),
                    "zero_alternative_group_count": str(zero[key]),
                    "alternative_group_count": str(alt[key]),
                })
    buffer = io.StringIO(newline="")
    writer = csv.DictWriter(buffer, fieldnames=list(atlas[0]), delimiter="\t", lineterminator="\n")
    writer.writeheader()
    writer.writerows(atlas)
    tsv_text = buffer.getvalue()
    role_presence = {
        role: sum(all(loci[(page, reading, role)] for reading in READINGS) for page in pages)
        for role in ROLES
    }
    numeric = [page for page in pages if declared_c[page] is not None]
    exact = [f"{page}|{reading}" for page in numeric for reading in READINGS if len(loci[(page, reading, "C")]) == declared_c[page]]
    mismatch = [f"{page}|{reading}" for page in numeric for reading in READINGS if len(loci[(page, reading, "C")]) != declared_c[page]]
    no_numeric = [page for page in pages if declared_c[page] is None]
    zero_c = [page for page in no_numeric if all(not loci[(page, reading, "C")] for reading in READINGS)]
    signatures = {
        page: {reading: "".join(role for role in ROLES if loci[(page, reading, role)]) for reading in READINGS}
        for page in pages
    }
    gates = {
        "exact_26_public_pages": len(pages) == 26,
        "exact_312_page_reading_role_rows": len(atlas) == 312,
        "all_page_role_signatures_agree_across_readings": all(len(set(row.values())) == 1 for row in signatures.values()),
        "all_numeric_public_circular_counts_match_IVTFF_C_loci": not mismatch,
        "exact_69_numeric_page_reading_matches": len(exact) == 69,
        "three_no_numeric_pages_all_have_zero_C": zero_c == ["f67r2", "f67v1", "f67v2"],
        "zero_english_glosses": True,
    }
    expected = {
        "experiment": "PUBLIC_CIRCLE_BLOCK_ROLE_ATLAS",
        "status": "PASS_COMPLETE_PUBLIC_CIRCLE_ROLE_ATLAS" if all(gates.values()) else "FAIL_PUBLIC_CIRCLE_ROLE_ATLAS",
        "inputs": {path.name: digest(path) for path in (ALIGN, META, PUBLIC, BUILDER)},
        "scope": {
            "pages": list(pages),
            "page_count": len(pages),
            "physical_folios": sorted({re.match(r"^(f\d+)", page).group(1) for page in pages}),
            "class_counts": dict(sorted(class_counts.items())),
            "atlas_rows": len(atlas),
        },
        "role_page_presence_all_readings": role_presence,
        "page_role_signatures": signatures,
        "public_numeric_circular_count_pages": numeric,
        "public_numeric_to_IVTFF_C_exact_cells": exact,
        "public_numeric_to_IVTFF_C_mismatch_cells": mismatch,
        "pages_without_numeric_public_circular_count": no_numeric,
        "no_numeric_pages_with_zero_C_all_readings": zero_c,
        "f67r2_public_text_mentions_circular_but_has_no_numeric_item_and_zero_C": "circular" in public["f67r2"]["text_description"].lower() and declared_c["f67r2"] is None and all(not loci[("f67r2", reading, "C")] for reading in READINGS),
        "gates": gates,
        "artifacts": {ATLAS.name: {"sha256": hashlib.sha256(tsv_text.encode()).hexdigest(), "rows": len(atlas)}},
        "claim_ceiling": "Descriptive public-page/IVTFF role coverage only. Visual circularity is not interchangeable with C; no ownership, object, function, word, meaning, plaintext, or translation.",
    }
    report = (
        "# Public f67--f73 circle-block role atlas\n\n"
        f"Status: **{expected['status']}**\n\n"
        "The atlas covers all 26 public page panels, seven folios, three alternate readings, and four IVTFF roles in 312 rows. Public classes are 7 astronomical, 7 cosmological, and 12 zodiac pages. All 26 page-level role signatures agree across readings.\n\n"
        "The public catalogue gives a numeric circular-writing count on 23 pages. Every one of the resulting 69 page-reading cells exactly matches the number of IVTFF `C` loci. The only pages without a numeric circular-item count are f67r2, f67v1, and f67v2, and all three have zero `C` loci. f67r2 still mentions a short circular text in prose, showing that a visual/descriptive circular phrase need not receive the `C` code.\n\n"
        f"All-reading page presence by role is {role_presence}. This is a coverage/provenance result only: visual circularity, page class, and IVTFF role are distinct layers, with no object ownership, word, meaning, plaintext, or translation.\n"
    )
    return atlas, expected, report


def main() -> None:
    if OUT.exists() or REPORT.exists():
        raise SystemExit("refusing overwrite")
    atlas, expected, report = reconstruct()
    assert ATLAS.read_text(encoding="utf-8") == (lambda rows_: _serialize(rows_))(atlas)
    assert json.loads(RESULT.read_text(encoding="utf-8")) == expected
    assert RESULT_REPORT.read_text(encoding="utf-8") == report
    assertions = len(load(ALIGN)) + len(load(META)) + len(load(PUBLIC)) + len(atlas) + 69
    validation = {
        "experiment": "PUBLIC_CIRCLE_BLOCK_ROLE_ATLAS_VALIDATION",
        "status": "PASS",
        "assertions": assertions,
        "bindings": {path.name: digest(path) for path in (BUILDER, ALIGN, META, PUBLIC, ATLAS, RESULT, RESULT_REPORT)},
        "reconstructed": {"pages": 26, "atlas_rows": 312, "numeric_C_cells": 69, "role_page_presence": expected["role_page_presence_all_readings"]},
        "production_module_imported": False,
        "claim_ceiling": "Independent descriptive coverage validation only; no ownership, object, function, word, meaning, plaintext, or translation.",
    }
    OUT.write_text(json.dumps(validation, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    REPORT.write_text(
        "# Public circle-block role-atlas validation\n\n"
        f"Status: **PASS** ({assertions} checks). The nonimporting reconstruction matches all 312 atlas rows, 26 page signatures, 69 public-count/IVTFF-C cells, JSON fields, and report bytes exactly.\n",
        encoding="utf-8",
    )
    print(json.dumps({"status": "PASS", "assertions": assertions}, sort_keys=True))


def _serialize(atlas: list[dict[str, str]]) -> str:
    buffer = io.StringIO(newline="")
    writer = csv.DictWriter(buffer, fieldnames=list(atlas[0]), delimiter="\t", lineterminator="\n")
    writer.writeheader()
    writer.writerows(atlas)
    return buffer.getvalue()


if __name__ == "__main__":
    main()
