#!/usr/bin/env python3
from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter
from pathlib import Path


def root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("repository root not found")


ROOT = root(Path(__file__).resolve())
BASE = ROOT / "experiments/yolo/gdt390_q20_inter_record_pointer_census"
ART = BASE / "artifacts"
SOURCE = ROOT / "gdt114_q20_record_template_inventory.tsv"
R114 = ROOT / "gdt114_result.json"
R388 = ROOT / "experiments/yolo/gdt388_acquisition_ready_relation_edge_protocol/artifacts/gdt388_result.json"

META = [
    "unit_id", "edition", "page", "physical_folio", "star_ordinal",
    "open_locus", "body_line_loci", "record_line_count",
]


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def digest(payload: dict) -> str:
    clone = dict(payload)
    clone.pop("content_hash", None)
    return hashlib.sha256(json.dumps(clone, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def prefix_fields(raw: bytes, count: int) -> list[bytes]:
    """Return only the first fixed metadata fields; ignore the payload suffix."""
    fields: list[bytes] = []
    start = 0
    for _ in range(count):
        stop = raw.find(b"\t", start)
        if stop < 0:
            raise RuntimeError("short source row")
        fields.append(raw[start:stop])
        start = stop + 1
    return fields


def main() -> int:
    ART.mkdir(parents=True, exist_ok=True)
    by_edition: dict[str, list[dict[str, str]]] = {"ZL3b": [], "IT2a": [], "RF1b": []}
    with SOURCE.open("rb") as handle:
        header = handle.readline().rstrip(b"\r\n").split(b"\t")
        assert [field.decode() for field in header[: len(META)]] == META
        for raw in handle:
            values = [value.decode("utf-8") for value in prefix_fields(raw, len(META))]
            row = dict(zip(META, values))
            if row["edition"] not in by_edition:
                continue
            # Selector and page guard run before the row is retained.
            assert not row["page"].lower().startswith("f84")
            by_edition[row["edition"]].append(row)
    assert {edition: len(rows) for edition, rows in by_edition.items()} == {"ZL3b": 170, "IT2a": 170, "RF1b": 170}
    key_fields = ["unit_id", "page", "physical_folio", "star_ordinal", "open_locus", "body_line_loci", "record_line_count"]
    key_sets = {
        edition: {tuple(row[field] for field in key_fields) for row in rows}
        for edition, rows in by_edition.items()
    }
    assert key_sets["ZL3b"] == key_sets["IT2a"] == key_sets["RF1b"]
    records = sorted(
        ({field: row[field] for field in key_fields} for row in by_edition["ZL3b"]),
        key=lambda row: (row["page"], int(row["star_ordinal"]), row["unit_id"]),
    )
    pages = sorted({row["page"] for row in records})
    folios = sorted({row["physical_folio"] for row in records})
    assert len(records) == 170 and len(pages) == 13 and len(folios) == 8
    assert folios == ["f104", "f105", "f106", "f107", "f112", "f113", "f114", "f115"]

    frame = ART / "gdt390_record_frame.tsv"
    with frame.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=key_fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(records)

    page_order = sorted(pages, key=lambda page: hashlib.sha256(("GDT390_PAGE_ORDER_V1|" + page).encode()).hexdigest())
    record_order = sorted(
        (row["unit_id"] for row in records),
        key=lambda unit: hashlib.sha256(("GDT390_RECORD_ORDER_V1|" + unit).encode()).hexdigest(),
    )
    freeze = {
        "schema": "GDT390_PRE_IMAGE_FREEZE_V1",
        "status": "FROZEN_BEFORE_IMAGE_ACCESS",
        "frame": {
            "records": len(records),
            "pages": len(pages),
            "physical_folios": len(folios),
            "page_record_counts": dict(sorted(Counter(row["page"] for row in records).items())),
            "folio_record_counts": dict(sorted(Counter(row["physical_folio"] for row in records).items())),
            "page_review_order": page_order,
            "record_review_order": record_order,
            "page_order_rule": "ascending SHA256('GDT390_PAGE_ORDER_V1|' + exact_page)",
            "record_order_rule": "ascending SHA256('GDT390_RECORD_ORDER_V1|' + exact_unit_id)",
        },
        "allowed_page_states": [
            "NO_INTER_RECORD_POINTER",
            "AMBIGUOUS_CROSS_RECORD_GEOMETRY",
            "POINTER_WITH_UNRESOLVED_SOURCE_OR_TARGET",
            "POINTER_WITH_EXACT_SOURCE_AND_TARGET",
            "UNMAPPED_OR_UNREVIEWABLE",
        ],
        "allowed_direction_bases": ["VISIBLE_ARROWHEAD", "UNAMBIGUOUS_AUTHORIAL_DIRECTION_DEVICE", "NONE_OR_UNRESOLVED"],
        "forbidden_bases": ["PAGE_ORDER", "STAR_ORDINAL", "PROXIMITY", "COMMON_STAR_RENDERING", "OPEN_BODY_HIERARCHY", "TEXT_READING_ORDER", "FORMAL_IDENTITY_OR_RECURRENCE"],
        "eligibility": {
            "distinct_exact_source_and_target_unit_ids": True,
            "singular_endpoint_ownership": True,
            "independent_authorial_direction": True,
            "target_not_determined_by_order_or_grammar": True,
            "mobile_matched_alternative_target": True,
            "minimum_edges": 50,
            "minimum_physical_folios": 5,
        },
        "access": {
            "formal_suffix_fields_parsed_retained_or_displayed": False,
            "voynich_group_surface_access": False,
            "image_access_before_freeze": False,
            "prior_repository_page_exposure_disclosed": True,
            "ocr_or_automated_vision": False,
            "f84_access": False,
        },
        "reviewer_provenance": "SINGLE_AI_DIRECT_VISUAL_EXPLORATORY_NOT_PRISTINE_HUMAN_OR_CONFIRMATORY",
        "scoring_authorized": False,
        "inputs": {str(path.relative_to(ROOT)): sha(path) for path in [SOURCE, R114, R388]},
        "outputs": {str(frame.relative_to(ROOT)): sha(frame)},
        "implementation": {str((BASE / "src/freeze.py").relative_to(ROOT)): sha(BASE / "src/freeze.py")},
        "claim_ceiling": "Q20_INTER_RECORD_POINTER_GEOMETRY_AND_CAPACITY_ONLY",
    }
    freeze["content_hash"] = digest(freeze)
    (ART / "gdt390_pre_image_freeze.json").write_text(json.dumps(freeze, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"status": freeze["status"], "frame": freeze["frame"]}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
