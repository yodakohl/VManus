#!/usr/bin/env python3
"""Build the external-only GDT359 Shirakatsi bolorak category audit."""
from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
EXP = ROOT / "experiments/yolo/gdt359_shirakatsi_bolorak_category"
ART = EXP / "artifacts"
GDT358 = ROOT / "experiments/yolo/gdt358_shirakatsi_bolorak_attribution/artifacts/gdt358_result.json"


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
        "source_id": "SHIRAKATSI_1958_MONOGRAPH",
        "source_class": "SCHOLARLY_MONOGRAPH_PUBLIC_SCAN",
        "bibliographic_reference": "R. A. Abrahamyan, B. E. Tumanian, T. Kh. Hakobyan, S. T. Melik-Bakhshyan, Anania Shirakatsi (Yerevan: Haypethrat, 1958), 132 printed pages",
        "date_or_scope": "1958; 75 scan surfaces",
        "url": "https://orient.sci.am/archive/337/article-ustYjNHb2RwdS5P6oT3ZkD0yGUICe8QL14JVMKp9.pdf",
        "remote_sha256": "f1baa1793e614cd488d1b00acc4443491ce9c27c12914b34055cbe9622eb9f22",
        "use": "COMPLETE_NO_OCR_FIGURE_CENSUS_AND_CAPTION_REVIEW",
    },
    {
        "source_id": "SHIRAKATSI_1962_BIBLIOGRAPHIC_RECORD",
        "source_class": "NATIONAL_LIBRARY_BIBLIOGRAPHY_PUBLIC_SCAN",
        "bibliographic_reference": "Anania Shirakatsi bibliography, entry for A. G. Abrahamyan ed., Anania Shirakatsi's Lunar Cycles / Tables of the Lunar Circle (Yerevan, 1962), 110 pp.",
        "date_or_scope": "Bibliographic publication 2012; entry for 1962 edition",
        "url": "https://api.nla.am/server/api/core/bitstreams/254edfa7-93a4-46d0-8fb8-b981ab702e9e/content",
        "remote_sha256": "56f438e15ea5b9e556b45108a1b1aa52921392e69b718596f94c77cc43a142af",
        "use": "BIBLIOGRAPHIC_EXISTENCE_AND_SCOPE_ONLY_NOT_EDITION_CONTENT",
    },
    {
        "source_id": "TUMANIAN_1971_ATTRIBUTION_STUDY",
        "source_class": "SCHOLARLY_ARTICLE_PUBLIC_SCAN",
        "bibliographic_reference": "B. E. Tumanian, 'On Two Works Attributed to Shirakatsi,' Patma-Banasirakan Handes 4 (1971), 203-209",
        "date_or_scope": "1971; 7 pages",
        "url": "https://arar.sci.am/Content/171677/file_0.pdf",
        "remote_sha256": "46ce69f7474a60e80b9038120cf058935f562c628019ac81607b677ccc9af27c",
        "use": "ATTRIBUTION_WARNING_FOR_1962_AND_1970_EDITORIAL_CORPUS",
    },
    {
        "source_id": "SHIRAKATSI_1979_COLLECTED_EDITION",
        "source_class": "SCHOLARLY_COLLECTED_EDITION_PUBLIC_SCAN",
        "bibliographic_reference": "Anania Shirakatsi, Matenagrut'yun, ed./trans. A. G. Abrahamyan and G. B. Petrosyan (Yerevan, 1979)",
        "date_or_scope": "1979; 401 PDF surfaces; inherited visual census from GDT358",
        "url": "https://archive.org/details/AnaniaShirakatsi1979",
        "remote_sha256": "68322110bf8c18caacb0b6ed27cdde3ad21497314f8cec8bad273a1d542adbee",
        "use": "INHERITED_LUNAR_EDITION_SCOPE_AND_DISTINCT_TOPOLOGIES",
    },
]

VISUAL = [
    {
        "observation_id": "V01_COMPLETE_1958_SCAN",
        "scan_surface": "1-75",
        "printed_pages": "covers-through-132",
        "provenance": "AI_DIRECT_EXTERNAL_VISUAL_OBSERVATION",
        "inspection": "COMPLETE_THUMBNAIL_CENSUS_PLUS_SELECTED_FULL_PAGE_REVIEW",
        "visible_geometry": "The scan contains prose, tables, manuscript facsimiles and circular astronomical/calendrical figures; no visible exact LJS443 f.209r eight-curved-compartment surface was found.",
        "interpretive_limit": "ABSENCE_IN_THIS_EDITION_NOT_ABSENCE_FROM_TRADITION",
    },
    {
        "observation_id": "V02_CONCENTRIC_ASTRONOMICAL_FIGURE",
        "scan_surface": "34",
        "printed_pages": "64-65",
        "provenance": "AI_DIRECT_EXTERNAL_VISUAL_OBSERVATION",
        "inspection": "DIRECT_FULL_PAGE_REVIEW",
        "visible_geometry": "Large concentric rings enclose a curved sequence of repeated star/crescent-like marks; topology differs from the Penn eight curved compartments.",
        "interpretive_limit": "DISTINCT_ASTRONOMICAL_TOPOLOGY_ONLY",
    },
    {
        "observation_id": "V03_CAPTIONED_CALENDRICAL_BOLORAK",
        "scan_surface": "43",
        "printed_pages": "80-81",
        "provenance": "AI_DIRECT_EXTERNAL_VISUAL_OBSERVATION",
        "inspection": "DIRECT_FULL_PAGE_REVIEW",
        "visible_geometry": "A manuscript facsimile contains several concentric annular grids divided into many cells around a blank center; visibly not the Penn eight-compartment wheel.",
        "interpretive_limit": "SOURCE_CAPTIONED_BOLORAK_DIFFERENT_TOPOLOGY",
    },
]

TERMS = [
    {
        "comparison_id": "T01_1958_CAPTION",
        "source_id": "SHIRAKATSI_1958_MONOGRAPH",
        "printed_armenian": "Շիրակացու տոմարական բոլորակներից մեկը",
        "literal_working_translation": "One of Shirakatsi's calendrical boloraks",
        "surface_topology": "MULTIRING_ANNULAR_CELL_GRID",
        "inference": "BOLORAK_TERM_ATTESTED_ON_NON_EIGHT_CURVED_TOPOLOGY",
    },
    {
        "comparison_id": "T02_1974_CAPTION_INHERITED",
        "source_id": "GDT358_SAE_V1_P363",
        "printed_armenian": "Անանիա Շիրակացու կազմած բոլորակներից։",
        "literal_working_translation": "From among the boloraks composed by Anania Shirakatsi",
        "surface_topology": "EIGHT_INWARD_CURVED_COMPARTMENTS",
        "inference": "EXACT_PENN_SURFACE_TRADITION_ATTRIBUTION_ONLY",
    },
    {
        "comparison_id": "T03_CATEGORY_TEST",
        "source_id": "CROSS_SOURCE",
        "printed_armenian": "բոլորակներից",
        "literal_working_translation": "from among boloraks",
        "surface_topology": "AT_LEAST_TWO_DISTINCT_PUBLISHED_TOPOLOGIES",
        "inference": "CATEGORY_WORD_DOES_NOT_KEY_EIGHT_COMPARTMENTS_OR_PHASES",
    },
]

CAVEATS = [
    {"caveat_id":"A01_PENN_RANGE_CONFLICT","evidence":"Penn catalogues f.209r in Hovhannes Sarkawag's Commentary on the Calendar, while its separate Anania astronomy item begins f.213r.","scope":"EXACT_SURFACE_AUTHORSHIP_UNRESOLVED"},
    {"caveat_id":"A02_TUMANIAN_CORRECTION","evidence":"Tumanian 1971 challenges Shirakatsi attribution for two spring-full-moon works published in the 1962 and 1970 editorial corpus.","scope":"ATTRIBUTION_WARNING_NOT_F209R_REFUTATION"},
    {"caveat_id":"A03_1962_SCAN_NOT_ACQUIRED","evidence":"The 1962 lunar-cycle edition is bibliographically verified, but an exact public scan was not acquired in this pass.","scope":"NO_DIRECT_1962_FIGURE_CENSUS_CLAIM"},
    {"caveat_id":"A04_SECONDARY_CAPTIONS","evidence":"Both topology labels used here are modern scholarly captions, not authorial medieval slot keys.","scope":"CATEGORY_PROVENANCE_ONLY"},
]

CAPACITY = [
    {"requirement_id":"K01_CATEGORY_SCOPE","requirement":"Published use of bolorak vocabulary across distinct topologies","status":"PRESENT","alignment_eligible":"NO","reason":"Broadens the category; does not key a diagram."},
    {"requirement_id":"K02_EXACT_FUNCTION","requirement":"Figure-specific function of LJS443 f.209r","status":"ABSENT","alignment_eligible":"NO","reason":"No audited source identifies what its eight compartments encode."},
    {"requirement_id":"K03_SLOT_VALUES","requirement":"Eight explicit compartment values","status":"ABSENT","alignment_eligible":"NO","reason":"No value list or compartment concordance was recovered."},
    {"requirement_id":"K04_START_DIRECTION_ORDER","requirement":"Authored start, direction and order","status":"ABSENT","alignment_eligible":"NO","reason":"No operational slot key was recovered."},
    {"requirement_id":"K05_INDEPENDENT_KEYED_WITNESS","requirement":"Independent readable witness of the same topology with values","status":"ABSENT","alignment_eligible":"NO","reason":"The new 1958 figure is a different topology."},
]

COUNTER = [
    {"counterexample_id":"CE01_DIFFERENT_BOLORAK_TOPOLOGY","evidence":"The 1958 captioned calendrical bolorak is a multi-ring annular grid, not an eight-curved-compartment wheel.","implication":"Bolorak cannot serve as an eight-phase or topology-specific key."},
    {"counterexample_id":"CE02_ANOTHER_ASTRONOMICAL_TOPOLOGY","evidence":"The same monograph reproduces a distinct concentric star/crescent astronomical diagram on printed p.65.","implication":"Circular astronomical content admits visibly heterogeneous layouts."},
    {"counterexample_id":"CE03_NO_1958_EXACT_SURFACE","evidence":"Complete 75-surface visual census found no exact Penn wheel.","implication":"The earlier synthesis gives category context, not an independent exact witness."},
    {"counterexample_id":"CE04_ATTRIBUTION_INSTABILITY","evidence":"Tumanian 1971 corrects attribution of two works from the related 1962/1970 editorial corpus.","implication":"Modern Shirakatsi attribution is not itself a medieval provenance proof."},
    {"counterexample_id":"CE05_NO_ORDERED_KEY","evidence":"No audited source supplies values, start, direction or order for the Penn compartments.","implication":"No Voynich alignment is licensed."},
]


def main() -> None:
    ART.mkdir(parents=True, exist_ok=True)
    paths = {
        "sources": ART / "gdt359_external_sources.tsv",
        "visual": ART / "gdt359_visual_census.tsv",
        "terms": ART / "gdt359_term_comparison.tsv",
        "caveats": ART / "gdt359_attribution_caveats.tsv",
        "capacity": ART / "gdt359_key_capacity.tsv",
        "counter": ART / "gdt359_counterexamples.tsv",
    }
    for key, rows in (("sources", SOURCES), ("visual", VISUAL), ("terms", TERMS), ("caveats", CAVEATS), ("capacity", CAPACITY), ("counter", COUNTER)):
        write_tsv(paths[key], rows)
    result = {
        "experiment": "GDT359",
        "schema": "GDT359_SHIRAKATSI_BOLORAK_CATEGORY_V1",
        "status": "BOLORAK_CATEGORY_BROADENED_NO_FIGURE_KEY",
        "counts": {
            "external_sources": len(SOURCES),
            "visual_observations": len(VISUAL),
            "term_comparisons": len(TERMS),
            "attribution_caveats": len(CAVEATS),
            "key_requirements": len(CAPACITY),
            "key_requirements_alignment_eligible": sum(x["alignment_eligible"] == "YES" for x in CAPACITY),
            "monograph_scan_surfaces": 75,
            "monograph_printed_pages": 132,
        },
        "findings": {
            "same_bolorak_vocabulary_spans_distinct_published_topologies": True,
            "bolorak_is_eight_compartment_specific": False,
            "exact_penn_function_found": False,
            "exact_penn_slot_key_found": False,
            "independent_exact_witness_found": False,
            "public_1962_scan_acquired": False,
            "voynich_target_scored": False,
            "ocr_or_automated_text_recognition_used": False,
        },
        "decision": "Treat bolorak as a broad calendrical/circular-table category in the audited scholarship, not an eight-phase or topology-specific key; retain the Penn surface attribution only at tradition level and do not align Voynich slots.",
        "source_access": {
            "external_monograph_scan_inspected": True,
            "external_article_and_bibliography_inspected": True,
            "voynich_images_opened": False,
            "voynich_transcription_or_formal_payload_opened": False,
            "f84_rows_or_images_accessed": False,
        },
        "claim_ceiling": "Published Shirakatsi bolorak vocabulary spans distinct circular/table topologies; no exact Penn function, eight phases, slot key, independent witness, Voynich alignment, Armenian origin/authorship, language, plaintext, meaning, or translation.",
        "inputs": {str(GDT358.relative_to(ROOT)): sha(GDT358)},
        "remote_source_hashes": {row["source_id"]: row["remote_sha256"] for row in SOURCES},
        "outputs": {str(path.relative_to(ROOT)): sha(path) for path in paths.values()},
        "documents": {str(path.relative_to(ROOT)): sha(path) for path in (EXP / "METHOD.md", EXP / "SOURCE_AUDIT.md", EXP / "REPORT.md")},
        "implementation": {str(Path(__file__).relative_to(ROOT)): sha(Path(__file__))},
    }
    content = dict(result)
    result["result_content_sha256"] = hashlib.sha256(stable(content)).hexdigest()
    (ART / "gdt359_result.json").write_bytes(stable(result))


if __name__ == "__main__":
    main()
