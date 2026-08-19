#!/usr/bin/env python3
"""Build the external-only GDT357 source-access audit."""
from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
EXP = ROOT / "experiments/yolo/gdt357_sarkawag_source_access"
ART = EXP / "artifacts"
GDT356 = ROOT / "experiments/yolo/gdt356_ljs443_work_attribution/artifacts/gdt356_result.json"


def stable(value: object) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False) + "\n").encode()


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_tsv(path: Path, rows: list[dict[str, object]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


SOURCES = [
    {
        "source_id": "ABRAHAMYAN_1956_FULL_SCAN",
        "source_class": "SCHOLARLY_CRITICAL_EDITION_ARCHIVED_LIBRARY_SCAN",
        "bibliographic_reference": "A. G. Abrahamyan, Hovhannes Imastaseri matenagrut'yune, Yerevan University Press, 1956, 372 printed pages",
        "url": "https://web.archive.org/web/20241207183501id_/http://tert.nla.am/archive/HAY%20GIRQ/Ardy/1951-1980/imastaser.pdf",
        "remote_sha256": "b099488d34a6107447f90543d4255a6602cd1cdf4dfe7cdb2a6273132b00d302",
        "rows_or_surfaces": 382,
        "use": "DIRECT_NO_OCR_EDITION_FIGURE_AND_RANGE_AUDIT",
    },
    {
        "source_id": "ARMENIAN_MANUSCRIPTS_INDEX_V3",
        "source_class": "SCHOLARLY_OPEN_DATASET",
        "bibliographic_reference": "Vidal-Gorene, Sargsyan, and Van Elverdinghe, Index of Digitized Armenian Manuscripts v3.0, 2025",
        "url": "https://zenodo.org/api/records/16355337/files/index.tsv/content",
        "remote_sha256": "0c9bd071290efee1da5820e31eea1b0375e29b4da7ebcce70cd78bd6161f189a",
        "rows_or_surfaces": 2579,
        "use": "PUBLIC_WITNESS_AVAILABILITY_CENSUS",
    },
    {
        "source_id": "ARMENIAN_MANUSCRIPTS_INDEX_V2",
        "source_class": "SCHOLARLY_OPEN_DATASET_SUPERSEDED_SENSITIVITY",
        "bibliographic_reference": "Vidal-Gorene, Sargsyan, and Van Elverdinghe, Index of Digitized Armenian Manuscripts v2.0, 2022",
        "url": "https://data.opendata.am/dataset/b61a7d6d-4469-4a78-90ce-805ead52fb1a/resource/43d49bf2-497b-4835-9472-905fabacb324/download/manuscripts-index.csv",
        "remote_sha256": "fc59638f7aac6d1e0354b956f60b5d0163082fadacd36bad310d24c3ac1ccb45",
        "rows_or_surfaces": 1363,
        "use": "EARLIER_INDEX_SENSITIVITY",
    },
]

VISUAL = [
    {"observation_id":"EV01_COMPLETE_SWEEP","pdf_surfaces":"1-382","printed_pages":"covers-through-index","provenance":"AI_DIRECT_EXTERNAL_VISUAL_OBSERVATION","inspection":"COMPLETE_THUMBNAIL_CENSUS_PLUS_SELECTED_FULL_PAGE_REVIEW","visible_observation":"Edition contains printed prose, tables, numerical diagrams, manuscript facsimiles, and circular figures.","key_support":"NONE"},
    {"observation_id":"EV02_KHARNAKHORAN_CITED_RANGE","pdf_surfaces":"169-200","printed_pages":"159-190","provenance":"AI_DIRECT_EXTERNAL_VISUAL_OBSERVATION","inspection":"COMPLETE_RANGE_THUMBNAIL_CENSUS_AND_DIRECT_PAGE_REVIEW","visible_observation":"Linear printed text and tables; no reproduction of an eight-curved-band spiral is visible in this range.","key_support":"NONE"},
    {"observation_id":"EV03_ANNULAR_FIGURE","pdf_surfaces":"76","printed_pages":"72","provenance":"AI_DIRECT_EXTERNAL_VISUAL_OBSERVATION","inspection":"DIRECT_FULL_PAGE_REVIEW","visible_observation":"Open annular scheme with central circle, radial divisions, and ten outer circular cells.","key_support":"COUNTEREXAMPLE_TO_EIGHT_FROM_CIRCULARITY"},
    {"observation_id":"EV04_INTERLACED_CIRCLE_FACSIMILE","pdf_surfaces":"96","printed_pages":"90","provenance":"AI_DIRECT_EXTERNAL_VISUAL_OBSERVATION","inspection":"DIRECT_FULL_PAGE_REVIEW","visible_observation":"Manuscript facsimile with interlaced circular geometry and distributed writing; not an eight curved-band spiral.","key_support":"NONE"},
    {"observation_id":"EV05_OTHER_SELECTED_FIGURES","pdf_surfaces":"51,54,56,61,77","printed_pages":"47,50,52,57,73","provenance":"AI_DIRECT_EXTERNAL_VISUAL_OBSERVATION","inspection":"DIRECT_FULL_PAGE_REVIEW","visible_observation":"Tabular facsimile, manuscript stemma, figural-number diagrams, overlapping cycles, and a labelled human figure; none supplies the Penn slot key.","key_support":"NONE"},
]

WITNESSES = [
    {"witness_id":"LJS443","shelfmark":"LJS 443","index_v3_status":"PRESENT","index_v2_status":"ABSENT_OR_DIFFERENT_INDEXING","public_access_implication":"Selected manuscript remains externally accessible through Penn/OPenn; index row supplies no folio key."},
    {"witness_id":"MM1973","shelfmark":"Matenadaran 1973","index_v3_status":"ABSENT","index_v2_status":"ABSENT","public_access_implication":"No full-access index route to the cited witness; absence is dataset-scoped."},
    {"witness_id":"MM1999","shelfmark":"Matenadaran 1999","index_v3_status":"ABSENT","index_v2_status":"ABSENT","public_access_implication":"No full-access index route to the cited witness; absence is dataset-scoped."},
    {"witness_id":"APIA00248","shelfmark":"Armenian Patriarchate Istanbul 248","index_v3_status":"PRESENT_LOGIN_REQUIRED","index_v2_status":"PRESENT","public_access_implication":"Same-century astronomy/calendar miscellany only; metadata does not identify a Sarkawag parallel or slot key."},
]

CAPACITY = [
    {"requirement_id":"K01_FOLIO_CONCORDANCE","requirement":"Source identifies LJS443 209r-210r diagram function","status":"ABSENT","alignment_eligible":"NO"},
    {"requirement_id":"K02_SLOT_VALUES","requirement":"Eight external compartments have explicit authored values","status":"ABSENT","alignment_eligible":"NO"},
    {"requirement_id":"K03_START_DIRECTION_ORDER","requirement":"Authorial start plus direction/order or invariant ordering rule","status":"ABSENT","alignment_eligible":"NO"},
    {"requirement_id":"K04_PARALLEL_WITNESS","requirement":"Independent readable witness reproduces and keys the same topology","status":"ABSENT_FROM_AUDITED_PUBLIC_SOURCES","alignment_eligible":"NO"},
    {"requirement_id":"K05_PERIOD_SYSTEM_CONTEXT","requirement":"Calendar/lunar/computistical system context","status":"PRESENT_WORK_LEVEL","alignment_eligible":"NO"},
]

COUNTER = [
    {"counterexample_id":"CE01_EDITION_CIRCULAR_TEN","evidence":"Critical-edition p.72 annular figure has ten outer cells, not eight curved bands.","implication":"Circular calendar imagery does not license eight values."},
    {"counterexample_id":"CE02_EDITION_RANGE_NO_SPIRAL","evidence":"Direct inspection of printed pp.159-190 finds no eight-band spiral reproduction.","implication":"The cited edition range supplies text/tables but no visual concordance."},
    {"counterexample_id":"CE03_INDEX_ABSENCE_LIMIT","evidence":"MM1973 and MM1999 are absent from v2 and v3 public indexes.","implication":"No public parallel is available through this route; absence is not proof of nondigitization elsewhere."},
    {"counterexample_id":"CE04_NO_SLOT_KEY","evidence":"No audited source fixes values, start, direction, or order for Penn 209r-210r.","implication":"Voynich target exposure remains unjustified."},
]


def main() -> None:
    ART.mkdir(parents=True, exist_ok=True)
    paths = {
        "sources": ART / "gdt357_external_sources.tsv",
        "visual": ART / "gdt357_edition_visual_audit.tsv",
        "witnesses": ART / "gdt357_witness_access.tsv",
        "capacity": ART / "gdt357_key_capacity.tsv",
        "counter": ART / "gdt357_counterexamples.tsv",
    }
    for key, data in (("sources", SOURCES), ("visual", VISUAL), ("witnesses", WITNESSES), ("capacity", CAPACITY), ("counter", COUNTER)):
        write_tsv(paths[key], data)
    result = {
        "experiment": "GDT357",
        "schema": "GDT357_SARKAWAG_SOURCE_ACCESS_V1",
        "status": "CRITICAL_EDITION_RECOVERED_NO_FOLIO_KEY_OR_PUBLIC_PARALLEL",
        "counts": {
            "external_sources": len(SOURCES),
            "edition_pdf_surfaces": 382,
            "public_index_v3_rows": 2579,
            "visual_audit_rows": len(VISUAL),
            "witness_rows": len(WITNESSES),
            "key_requirements": len(CAPACITY),
            "key_requirements_alignment_eligible": sum(x["alignment_eligible"] == "YES" for x in CAPACITY),
        },
        "findings": {
            "critical_edition_recovered": True,
            "ocr_or_automated_text_recognition_used": False,
            "eight_band_spiral_reproduced_in_cited_edition_range": False,
            "mm1973_in_public_index_v3": False,
            "mm1999_in_public_index_v3": False,
            "folio_specific_slot_key_found": False,
            "voynich_target_scored": False,
        },
        "decision": "Close this public edition/index acquisition route; reopen only with a specialist concordance, readable parallel witness, or externally authored slot key.",
        "source_access": {
            "external_edition_images_inspected": True,
            "external_dataset_queried": True,
            "voynich_images_opened": False,
            "voynich_transcription_or_formal_payload_opened": False,
            "f84_rows_or_images_accessed": False,
        },
        "claim_ceiling": "Recovered critical edition plus negative public-key capacity; no diagram identity, slot values, Armenian origin or authorship for Voynich, language, plaintext, meaning, or translation.",
        "inputs": {str(GDT356.relative_to(ROOT)): sha(GDT356)},
        "remote_source_hashes": {row["source_id"]: row["remote_sha256"] for row in SOURCES},
        "outputs": {str(path.relative_to(ROOT)): sha(path) for path in paths.values()},
        "documents": {str(path.relative_to(ROOT)): sha(path) for path in (EXP / "METHOD.md", EXP / "SOURCE_AUDIT.md", EXP / "REPORT.md")},
        "implementation": {str(Path(__file__).relative_to(ROOT)): sha(Path(__file__))},
    }
    content = dict(result)
    result["result_content_sha256"] = hashlib.sha256(stable(content)).hexdigest()
    (ART / "gdt357_result.json").write_bytes(stable(result))


if __name__ == "__main__":
    main()
