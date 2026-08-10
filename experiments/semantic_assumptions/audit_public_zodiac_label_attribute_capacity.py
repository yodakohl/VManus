#!/usr/bin/env python3
"""Capacity audit for explicit human zodiac-label attributes.

This script consumes the text-free metadata projection of Stolfi/Grove's
public label catalogue.  It does not read or score Voynich strings.  Missing
attribute mentions remain UNKNOWN; only explicit opposing phrases can form a
binary contrast.
"""

from __future__ import annotations

import csv
import hashlib
import json
import re
from collections import Counter
from pathlib import Path


BASE = Path(__file__).resolve().parent
RESULTS = BASE / "results"
ANNOTATIONS = RESULTS / "existing_human_label_annotations.tsv"
ANNOTATION_VALIDATION = RESULTS / "existing_human_annotation_atlas_validation.json"
PUBLIC_PAGES = RESULTS / "public_voynich_nu_page_annotations_v2.tsv"
TEAGUE = RESULTS / "public_zodiac_nymph_overview.json"
OUT_JSON = RESULTS / "public_zodiac_label_attribute_capacity.json"
REPORT = RESULTS / "public_zodiac_label_attribute_capacity_report.md"

PAGES = (
    "f70v2", "f70v1", "f71r", "f71v", "f72r1", "f72r2",
    "f72r3", "f72v3", "f72v2", "f72v1", "f73r", "f73v",
)
STOLFI_URL = (
    "https://www.ic.unicamp.br/~stolfi/PUB/EXPORT/voynich/Notes/107/"
    "work/Notes/614/labtit-best.idx"
)
STOLFI_SHA256 = "9267a2bbf2d485320ce8baaa2e3eeaccb6be7a02aa81ee9422a39ba00bef420a"

PATTERNS = {
    "BARREL_PRESENT": r"\b(?:vert\.?|hor\.?) barrel\b",
    "BARREL_ABSENT": r"\bno barrel\b",
    "VERTICAL_BARREL": r"\bvert\.? barrel\b",
    "HORIZONTAL_BARREL": r"\bhor\.? barrel\b",
    "FACING_LEFT": r"\bfacing left\b",
    "FACING_RIGHT": r"\bfacing right\b",
    "MALE": r"\bmale\??\b",
    "FEMALE": r"\bfemale\b|\bwoman\b|\bwomen\b",
    "DRESSED": r"\bdressed\??\b|\bpartdress\b",
    "CROWN": r"\bcrown(?:ed)?\b",
    "STAR_TAIL": r"\b(?:star with tail|tailed star|tail on star|tail to star|striped tail on star)\b",
    "HAT": r"\bhat\b",
    "STAR_ABSENT": r"\bno star\b",
}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def folio(page: str) -> str:
    match = re.match(r"f\d+", page)
    assert match
    return match.group(0)


def canonical_write(path: Path, payload: dict) -> None:
    if path.exists():
        raise SystemExit(f"refusing overwrite: {path}")
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main() -> None:
    if REPORT.exists():
        raise SystemExit(f"refusing overwrite: {REPORT}")

    validation = json.loads(ANNOTATION_VALIDATION.read_text(encoding="utf-8"))
    assert validation["status"] == "PASS_EXISTING_HUMAN_ANNOTATION_ATLAS_VALIDATION"
    assert validation["source_hashes"][
        "experiments/semantic_assumptions/cache/existing_human_annotations/labtit-best.idx"
    ] == STOLFI_SHA256

    rows = [row for row in read_tsv(ANNOTATIONS) if row["section"] == "zodiac"]
    assert len(rows) == 300
    assert len({row["source_record_id"] for row in rows}) == 300
    assert len({row["location"] for row in rows}) == 300
    assert {row["page"] for row in rows} == set(PAGES)
    assert {row["source_url"] for row in rows} == {STOLFI_URL}

    counts: dict[str, dict] = {}
    matched: dict[str, list[dict[str, str]]] = {}
    for name, pattern in PATTERNS.items():
        selected = [row for row in rows if re.search(pattern, row["comments"], re.I)]
        matched[name] = selected
        counts[name] = {
            "records": len(selected),
            "pages": sorted({row["page"] for row in selected}),
            "folios": sorted({folio(row["page"]) for row in selected}),
            "by_page": dict(sorted(Counter(row["page"] for row in selected).items())),
        }

    assert not ({row["source_record_id"] for row in matched["BARREL_PRESENT"]} & {
        row["source_record_id"] for row in matched["BARREL_ABSENT"]
    })
    assert counts["BARREL_PRESENT"]["records"] == 79
    assert counts["BARREL_PRESENT"]["folios"] == ["f70", "f71", "f72"]
    assert counts["BARREL_ABSENT"]["records"] == 27
    assert counts["BARREL_ABSENT"]["folios"] == ["f72"]
    assert counts["HORIZONTAL_BARREL"]["records"] == 10
    assert counts["HORIZONTAL_BARREL"]["folios"] == ["f70"]
    assert counts["FACING_RIGHT"]["records"] == 1
    assert counts["FEMALE"]["records"] == 1

    one_sided = {
        name: counts[name]
        for name in ("DRESSED", "CROWN", "STAR_TAIL", "HAT")
    }
    contrasts = {
        "BARREL_PRESENT_VS_ABSENT": {
            "state_a": counts["BARREL_PRESENT"],
            "state_b": counts["BARREL_ABSENT"],
            "state_a_min_two_folios": len(counts["BARREL_PRESENT"]["folios"]) >= 2,
            "state_b_min_two_folios": len(counts["BARREL_ABSENT"]["folios"]) >= 2,
        },
        "VERTICAL_VS_HORIZONTAL_BARREL": {
            "state_a": counts["VERTICAL_BARREL"],
            "state_b": counts["HORIZONTAL_BARREL"],
            "state_a_min_two_folios": len(counts["VERTICAL_BARREL"]["folios"]) >= 2,
            "state_b_min_two_folios": len(counts["HORIZONTAL_BARREL"]["folios"]) >= 2,
        },
        "FACING_LEFT_VS_RIGHT": {
            "state_a": counts["FACING_LEFT"],
            "state_b": counts["FACING_RIGHT"],
            "state_a_min_two_folios": len(counts["FACING_LEFT"]["folios"]) >= 2,
            "state_b_min_two_folios": len(counts["FACING_RIGHT"]["folios"]) >= 2,
        },
        "MALE_VS_FEMALE": {
            "state_a": counts["MALE"],
            "state_b": counts["FEMALE"],
            "state_a_min_two_folios": len(counts["MALE"]["folios"]) >= 2,
            "state_b_min_two_folios": len(counts["FEMALE"]["folios"]) >= 2,
        },
    }
    for contrast in contrasts.values():
        contrast["eligible"] = bool(
            contrast["state_a_min_two_folios"] and contrast["state_b_min_two_folios"]
        )
    assert not any(contrast["eligible"] for contrast in contrasts.values())

    public = {row["page"]: row for row in read_tsv(PUBLIC_PAGES)}
    assert "they are all holding a star" in public["f72v2"]["illustrations"].lower()
    teague = json.loads(TEAGUE.read_text(encoding="utf-8"))
    assert teague["complete_counts"]["nymph_minus_star_by_page"]["f72v2"] == 0
    assert counts["STAR_ABSENT"]["records"] == 1
    star_row = matched["STAR_ABSENT"][0]
    assert star_row["source_record_id"] == "STOLFI_BEST_0684"
    assert star_row["page"] == "f72v2"

    gates = {
        "exact_300_unique_zodiac_records": len(rows) == 300,
        "all_12_pages_four_folios_present": len({row["page"] for row in rows}) == 12
        and len({folio(row["page"]) for row in rows}) == 4,
        "all_missing_mentions_kept_unknown": True,
        "barrel_absence_confined_to_one_folio": counts["BARREL_ABSENT"]["folios"] == ["f72"],
        "no_explicit_binary_contrast_has_two_folios_per_state": not any(
            contrast["eligible"] for contrast in contrasts.values()
        ),
        "f72v2_star_annotation_conflict_retained_unknown": True,
        "zero_voynich_strings_scored": True,
        "zero_ocr_or_automated_vision": True,
    }
    assert all(gates.values())

    result = {
        "experiment": "PUBLIC_ZODIAC_LABEL_ATTRIBUTE_CAPACITY",
        "status": "STOP_UNSCORED_NO_TRANSFERABLE_EXPLICIT_BINARY_ATTRIBUTE",
        "inputs": {
            str(ANNOTATIONS.relative_to(BASE)): sha(ANNOTATIONS),
            str(ANNOTATION_VALIDATION.relative_to(BASE)): sha(ANNOTATION_VALIDATION),
            str(PUBLIC_PAGES.relative_to(BASE)): sha(PUBLIC_PAGES),
            str(TEAGUE.relative_to(BASE)): sha(TEAGUE),
        },
        "public_source": {"url": STOLFI_URL, "sha256": STOLFI_SHA256},
        "counts": {
            "zodiac_records": len(rows),
            "pages": 12,
            "physical_folios": 4,
            "attributes": counts,
        },
        "binary_contrasts": contrasts,
        "one_sided_positive_only_attributes": one_sided,
        "source_disagreement": {
            "page": "f72v2",
            "source_record_id": "STOLFI_BEST_0684",
            "stolfi_state": "NO_STAR",
            "teague_nymph_minus_star": 0,
            "voynich_nu_state": "ALL_30_HOLDING_STAR",
            "adjudication": "UNKNOWN",
        },
        "gates": gates,
        "decision": "STOP_BEFORE_VOYNICH_FEATURE_ACCESS",
        "claim_ceiling": (
            "The public human catalogue supplies useful positive attribute metadata, but no explicit "
            "opposing state spans two physical folios. It cannot support a transferable semantic "
            "test. The conflicting f72v2 star state remains unknown. No Voynich word, stem, meaning, "
            "plaintext, or translation follows."
        ),
    }
    canonical_write(OUT_JSON, result)

    report = (
        "# Public zodiac-label attribute capacity audit\n\n"
        "Status: **STOP_UNSCORED_NO_TRANSFERABLE_EXPLICIT_BINARY_ATTRIBUTE**\n\n"
        "The public 1998 Stolfi/Grove catalogue contains 300 unique zodiac label records on "
        "12 panels and four physical folios. Missing attribute mentions were kept UNKNOWN. "
        "No Voynich string, OCR output, or automated image feature was used.\n\n"
        "The strongest genuine binary field is barrel presence. It has **79** explicit present "
        "records on f70, f71, and f72, but all **27** explicit `no barrel` records are on f72. "
        "Horizontal barrels occur only on f70. Facing-right has one record and FEMALE has one; "
        "clothing, crown, star-tail, and hat are positive-only annotations. Consequently no "
        "explicit opposing state spans the minimum two folios per state.\n\n"
        "There is also a source conflict at f72v2: Stolfi record 0684 says `no star`, while "
        "Teague's complete count gives no missing star there and the current public page catalogue "
        "says all 30 figures hold stars. The slot is retained as UNKNOWN rather than adjudicated.\n\n"
        "This closes the current attribute table before any Voynich feature access. Reopen only "
        "with explicit positive and negative slot states spanning at least two physical folios each. "
        "No BARREL, LEFT, RIGHT, MALE, FEMALE, CROWN, STAR, word, stem, meaning, plaintext, or "
        "translation follows.\n\n"
        f"Public source: {STOLFI_URL}\n"
    )
    REPORT.write_text(report, encoding="utf-8")
    print(json.dumps({"status": result["status"], "records": len(rows)}, sort_keys=True))


if __name__ == "__main__":
    main()
