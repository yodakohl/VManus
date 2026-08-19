#!/usr/bin/env python3
"""Build the external-only GDT358 Shirakatsi bolorak attribution audit."""
from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
EXP = ROOT / "experiments/yolo/gdt358_shirakatsi_bolorak_attribution"
ART = EXP / "artifacts"
GDT355 = ROOT / "experiments/yolo/gdt355_ljs443_diagram_series_census/artifacts/gdt355_result.json"
GDT357 = ROOT / "experiments/yolo/gdt357_sarkawag_source_access/artifacts/gdt357_result.json"


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
        "source_id": "PENN_LJS443_209R",
        "source_class": "OFFICIAL_PRIMARY_FACSIMILE",
        "bibliographic_reference": "University of Pennsylvania, LJS 443, current f.209r (old f.210r), OPenn image 0088_0422",
        "date_or_scope": "Copied after 1416; current f.209r",
        "url": "https://openn.library.upenn.edu/Data/0001/ljs443/data/web/0088_0422_web.jpg",
        "remote_sha256": "a218414d67f5044281c8cf6e6a3606447d01b023782a8756d1a3a3207a660530",
        "use": "PRIMARY_SURFACE_FOR_DIRECT_LANDMARK_COMPARISON",
    },
    {
        "source_id": "SAE_V1_P363_SCAN",
        "source_class": "ENCYCLOPEDIA_PAGE_SCAN_SECONDARY_SOURCE",
        "bibliographic_reference": "Haykakan Sovetakan Hanragitaran [Armenian Soviet Encyclopedia], vol. 1 (Yerevan, 1974), p.363",
        "date_or_scope": "1974; printed p.363",
        "url": "https://hy.wikisource.org/wiki/%D4%B7%D5%BB:%D5%80%D5%A1%D5%B5%D5%AF%D5%A1%D5%AF%D5%A1%D5%B6_%D5%8D%D5%B8%D5%BE%D5%A5%D5%BF%D5%A1%D5%AF%D5%A1%D5%B6_%D5%80%D5%A1%D5%B6%D6%80%D5%A1%D5%A3%D5%AB%D5%BF%D5%A1%D6%80%D5%A1%D5%B6_(Soviet_Armenian_Encyclopedia)_1.djvu/363",
        "remote_sha256": "7cbde2d0d9883fb4615eb6ec7e2282311b692f72a163f637b7283cb8136757fa",
        "use": "DIRECT_NO_OCR_FIGURE_AND_PRINTED_CAPTION_REVIEW",
    },
    {
        "source_id": "SAE_SHIRAKATSI_TRANSCRIPTION",
        "source_class": "SOURCE_PROVIDED_PROOFREAD_TRANSCRIPTION",
        "bibliographic_reference": "Wikisource proofread transcription of the Armenian Soviet Encyclopedia Anania Shirakatsi article, vol.1, pp.362-364",
        "date_or_scope": "Source article 1974; web snapshot 2026-08-19",
        "url": "https://hy.wikisource.org/wiki/%D5%80%D5%8D%D5%80/%D4%B1%D5%86%D4%B1%D5%86%D4%BB%D4%B1_%D5%87%D4%BB%D5%90%D4%B1%D4%BF%D4%B1%D5%91%D4%BB",
        "remote_sha256": "a39692d155aad2669baef38c63ba4e4e778d6f9bad37b6a38eb16dacf9030a21",
        "use": "CAPTION_AND_ARTICLE_CONTEXT_TRANSCRIPTION_CHECK",
    },
    {
        "source_id": "COMMONS_BOLORAKNER_PNG",
        "source_class": "USER_UPLOADED_DERIVATIVE_IMAGE_WITH_TERTIARY_METADATA",
        "bibliographic_reference": "Wikimedia Commons file uploaded by Vahram Mekhitarian, 20 September 2013",
        "date_or_scope": "2013 derivative crop of SAE p.363 figure",
        "url": "https://commons.wikimedia.org/wiki/File:Anania_Shirakatsi,_7th_century,_Phases_of_the_Moon,_Bolorakner.png",
        "remote_sha256": "42b912dfa17a47985a6441383bba39fbc12f1e9ee6ac9f62dc20c210c4688275",
        "use": "PROVENANCE_AUDIT_ONLY_NOT_SEMANTIC_EVIDENCE",
    },
    {
        "source_id": "SHIRAKATSI_1979_SCAN",
        "source_class": "SCHOLARLY_COLLECTED_EDITION_PUBLIC_SCAN",
        "bibliographic_reference": "Anania Shirakatsi, Matenagrut'yun, ed./trans. A. G. Abrahamyan and G. B. Petrosyan (Yerevan, 1979)",
        "date_or_scope": "1979; 401 PDF surfaces",
        "url": "https://archive.org/details/AnaniaShirakatsi1979",
        "remote_sha256": "68322110bf8c18caacb0b6ed27cdde3ad21497314f8cec8bad273a1d542adbee",
        "use": "DIRECT_NO_OCR_COMPLETE_FIGURE_CENSUS_AND_LUNAR_SECTION_REVIEW",
    },
    {
        "source_id": "AUA_1979_EDITORIAL_NOTE",
        "source_class": "SCHOLARLY_DIGITAL_EDITION_EDITORIAL_METADATA",
        "bibliographic_reference": "Digital Library of Armenian Literature, Anania Shirakatsi Matenagrut'yun, editorial source note",
        "date_or_scope": "1979 edition metadata; retrieved 2026-08-19",
        "url": "https://digilib.aua.am/book/1147/%D4%B1%D5%B6%D5%A1%D5%B6%D5%AB%D5%A1%20%D5%87%D5%AB%D6%80%D5%A1%D5%AF%D5%A1%D6%81%D5%AB,%20%D5%84%D5%A1%D5%BF%D5%A5%D5%B6%D5%A1%D5%A3%D6%80%D5%B8%D6%82%D5%A9%D5%B5%D5%B8%D6%82%D5%B6",
        "remote_sha256": "33dfeb4e08bc4d13970642888badbb1d251fcc6f962c876a0a8c093c7289578a",
        "use": "1962_TO_1979_LUNAR_WORK_REPUBLICATION_PROVENANCE",
    },
]

ATTRIBUTION = [
    {
        "claim_id": "A01_SAME_SURFACE",
        "claim": "The SAE p.363 figure is a reproduction of Penn LJS443 current f.209r",
        "support_status": "SUPPORTED_DIRECT_VISUAL_IDENTITY",
        "support": "Same eight curved compartments, blank double-ring center, same ringed/crescent marks, same inscription placement, and same manuscript lines immediately below the wheel.",
        "semantic_eligibility": "GEOMETRY_AND_PROVENANCE_ONLY",
    },
    {
        "claim_id": "A02_PRINTED_ATTRIBUTION",
        "claim": "The encyclopedia caption attributes the reproduced figure to circular tables/cycles composed by Anania Shirakatsi",
        "support_status": "SUPPORTED_SECONDARY_SOURCE_CAPTION",
        "support": "Printed Armenian: 'Անանիա Շիրակացու կազմած բոլորակներից։'; literal working translation: 'From among the boloraks/circular tables composed by Anania Shirakatsi.'",
        "semantic_eligibility": "AUTHOR_TRADITION_ATTRIBUTION_ONLY",
    },
    {
        "claim_id": "A03_MOON_PHASE_LABEL",
        "claim": "The exact eight-compartment figure represents eight phases of the Moon",
        "support_status": "UNSUPPORTED_BY_PRINTED_CAPTION",
        "support": "The 2013 Commons uploader supplied 'Phases of the Moon'; the printed SAE caption says only that the image is from Shirakatsi's boloraks/circular tables.",
        "semantic_eligibility": "NO",
    },
    {
        "claim_id": "A04_ARTICLE_LUNAR_CONTEXT",
        "claim": "The containing encyclopedia article discusses Shirakatsi's lunar science",
        "support_status": "SUPPORTED_ARTICLE_LEVEL_NOT_FIGURE_KEYED",
        "support": "The article separately says he explained lunar phases and compiled 19-year lunar birth/fullness tables; it does not explicitly attach either statement to the reproduced wheel.",
        "semantic_eligibility": "SYSTEM_CONTEXT_ONLY",
    },
    {
        "claim_id": "A05_CATALOGUE_RANGE",
        "claim": "Penn catalogues f.209r inside Hovhannes Sarkawag's Commentary on the Calendar rather than the later Anania On Astronomy item",
        "support_status": "SUPPORTED_CATALOGUE_LEVEL_ATTRIBUTION_CONFLICT",
        "support": "Penn range 145v-212r is Sarkawag; Anania On Astronomy begins at 213r. A reproduced older table or a secondary-source misattribution remain possible.",
        "semantic_eligibility": "CONFLICT_UNRESOLVED",
    },
    {
        "claim_id": "A06_INDEPENDENT_HOMOLOGUE",
        "claim": "The encyclopedia supplies an independent manuscript witness of the eight-compartment topology",
        "support_status": "CONTRADICTED_SAME_SURFACE_REPRODUCTION",
        "support": "The figure reproduces the Penn manuscript surface itself, including the same writing below it.",
        "semantic_eligibility": "NO",
    },
]

LANDMARKS = [
    {"landmark_id":"L01_TOPOLOGY","penn_observation":"Eight inward-curving compartments around a blank double-ring center","sae_observation":"Same eight inward-curving compartments and blank double-ring center","match":"EXACT_VISUAL_LAYOUT_MATCH"},
    {"landmark_id":"L02_ROUND_MARKS","penn_observation":"Eight dark/ringed circular marks at the same compartment positions","sae_observation":"Same eight circular marks after monochrome reproduction","match":"EXACT_POSITIONAL_MATCH"},
    {"landmark_id":"L03_CRESCENTS","penn_observation":"Repeated crescent-like marks beside the circular marks","sae_observation":"Same crescent-like marks at corresponding locations","match":"EXACT_POSITIONAL_MATCH"},
    {"landmark_id":"L04_INSCRIPTIONS","penn_observation":"Curved Armenian inscriptions follow the compartment edges","sae_observation":"Same inscription shapes and placements in monochrome","match":"EXACT_SURFACE_REPRODUCTION"},
    {"landmark_id":"L05_LOWER_TEXT","penn_observation":"Multiple manuscript lines immediately below the circle","sae_observation":"Same lower manuscript lines included below the reproduced circle","match":"EXACT_SURFACE_REPRODUCTION"},
]

EDITION = [
    {"observation_id":"E01_COMPLETE_SCAN","pdf_surfaces":"1-401","printed_pages":"covers-through-index","provenance":"AI_DIRECT_EXTERNAL_VISUAL_OBSERVATION","inspection":"COMPLETE_THUMBNAIL_CENSUS_PLUS_SELECTED_FULL_PAGE_REVIEW","visible_observation":"Collected edition contains prose, long tabular runs, reconstructed figures, and manuscript facsimiles; no visible exact reproduction of the Penn eight-curved-band surface was found.","slot_key_support":"NONE"},
    {"observation_id":"E02_LUNAR_SECTION_START","pdf_surfaces":"144","printed_pages":"143","provenance":"AI_DIRECT_EXTERNAL_VISUAL_OBSERVATION","inspection":"DIRECT_FULL_PAGE_REVIEW","visible_observation":"A bracketed lunar-table section heading begins near the bottom of the page.","slot_key_support":"LUNAR_CONTEXT_ONLY"},
    {"observation_id":"E03_NUMERIC_ORBIT_FIGURE","pdf_surfaces":"145","printed_pages":"144","provenance":"AI_DIRECT_EXTERNAL_VISUAL_OBSERVATION","inspection":"DIRECT_FULL_PAGE_REVIEW","visible_observation":"Overlapping circular/orbital construction with many numeric labels and accompanying prose.","slot_key_support":"COUNTEREXAMPLE_DIFFERENT_TOPOLOGY"},
    {"observation_id":"E04_ANNULAR_TABLE_FACSIMILE","pdf_surfaces":"146","printed_pages":"145","provenance":"AI_DIRECT_EXTERNAL_VISUAL_OBSERVATION","inspection":"DIRECT_FULL_PAGE_REVIEW","visible_observation":"Manuscript facsimile with concentric annular table above prose; not the Penn eight-curved-band wheel.","slot_key_support":"COUNTEREXAMPLE_DIFFERENT_TOPOLOGY"},
    {"observation_id":"E05_RADIAL_TABLE_FACSIMILE","pdf_surfaces":"147","printed_pages":"146","provenance":"AI_DIRECT_EXTERNAL_VISUAL_OBSERVATION","inspection":"DIRECT_FULL_PAGE_REVIEW","visible_observation":"Manuscript facsimile with dense radial table above prose; not the Penn eight-curved-band wheel.","slot_key_support":"COUNTEREXAMPLE_DIFFERENT_TOPOLOGY"},
]

CAPACITY = [
    {"requirement_id":"K01_EXACT_SURFACE_PROVENANCE","requirement":"Secondary source identifies the exact Penn surface","status":"PRESENT","alignment_eligible":"NO","reason":"Same-surface attribution is not an independent keyed homologue."},
    {"requirement_id":"K02_EXACT_DIAGRAM_FUNCTION","requirement":"Scholarly source explicitly identifies what the eight compartments encode","status":"ABSENT","alignment_eligible":"NO","reason":"Printed caption says boloraks/circular tables only."},
    {"requirement_id":"K03_SLOT_VALUES","requirement":"Eight compartments have explicit externally readable values","status":"ABSENT","alignment_eligible":"NO","reason":"No compartment transcription or value key was recovered."},
    {"requirement_id":"K04_START_DIRECTION_ORDER","requirement":"Authorial start plus direction/order or invariant ordering rule","status":"ABSENT","alignment_eligible":"NO","reason":"Neither caption nor edition supplies it."},
    {"requirement_id":"K05_INDEPENDENT_WITNESS","requirement":"Independent readable witness reproduces and keys the same topology","status":"ABSENT","alignment_eligible":"NO","reason":"SAE and Commons reproduce the same Penn surface."},
    {"requirement_id":"K06_LUNAR_SYSTEM_CONTEXT","requirement":"Shirakatsi lunar/calendrical system context","status":"PRESENT_NOT_FIGURE_KEYED","alignment_eligible":"NO","reason":"Article and collected edition document lunar work without attaching a slot key to f.209r."},
]

COUNTER = [
    {"counterexample_id":"CE01_COMMONS_GLOSS","evidence":"'Phases of the Moon' occurs in uploader-authored Commons metadata, not the 1974 printed caption.","implication":"Do not promote the modern file title to historical diagram identification."},
    {"counterexample_id":"CE02_SAME_SURFACE","evidence":"SAE figure retains the exact Penn wheel and manuscript lines below it.","implication":"This is provenance evidence, not independent topological replication."},
    {"counterexample_id":"CE03_CATALOGUE_CONFLICT","evidence":"Penn places f.209r in Sarkawag's calendar commentary; its separate Anania astronomy item starts at f.213r.","implication":"The encyclopedia attribution may reflect borrowed tradition, compilation, or misattribution; individual authorship is unresolved."},
    {"counterexample_id":"CE04_1979_OTHER_DIAGRAMS","evidence":"The audited 1979 lunar section reproduces other circular/radial diagrams but no visible exact f.209r wheel.","implication":"Lunar content plus circularity does not identify this specific eight-compartment figure."},
    {"counterexample_id":"CE05_NO_SLOT_KEY","evidence":"No audited source gives eight compartment values, start, direction, or order.","implication":"No Voynich slot alignment or semantic scoring is authorized."},
]


def main() -> None:
    ART.mkdir(parents=True, exist_ok=True)
    paths = {
        "sources": ART / "gdt358_external_sources.tsv",
        "attribution": ART / "gdt358_attribution_chain.tsv",
        "landmarks": ART / "gdt358_image_landmark_audit.tsv",
        "edition": ART / "gdt358_edition_visual_audit.tsv",
        "capacity": ART / "gdt358_key_capacity.tsv",
        "counter": ART / "gdt358_counterexamples.tsv",
    }
    for key, rows in (("sources", SOURCES), ("attribution", ATTRIBUTION), ("landmarks", LANDMARKS), ("edition", EDITION), ("capacity", CAPACITY), ("counter", COUNTER)):
        write_tsv(paths[key], rows)
    result = {
        "experiment": "GDT358",
        "schema": "GDT358_SHIRAKATSI_BOLORAK_ATTRIBUTION_V1",
        "status": "SAME_SURFACE_ANANIA_BOLORAK_ATTRIBUTION_NO_PHASE_OR_SLOT_KEY",
        "counts": {
            "external_sources": len(SOURCES),
            "attribution_claims": len(ATTRIBUTION),
            "manual_landmark_rows": len(LANDMARKS),
            "edition_visual_rows": len(EDITION),
            "edition_pdf_surfaces": 401,
            "key_requirements": len(CAPACITY),
            "key_requirements_alignment_eligible": sum(x["alignment_eligible"] == "YES" for x in CAPACITY),
        },
        "findings": {
            "same_penn_surface_reproduced_in_1974_encyclopedia": True,
            "printed_caption_attributes_bolorak_to_shirakatsi": True,
            "printed_caption_says_moon_phases": False,
            "commons_moon_phase_gloss_is_uploader_metadata": True,
            "independent_parallel_witness_found": False,
            "folio_specific_slot_key_found": False,
            "voynich_target_scored": False,
            "ocr_or_automated_text_recognition_used": False,
        },
        "decision": "Retain a stronger Anania/Shirakatsi bolorak-tradition attribution for the exact Penn surface, but do not call it an eight-phase diagram or align any Voynich slots without a scholarly figure-specific key or independent readable witness.",
        "source_access": {
            "external_manuscript_image_inspected": True,
            "external_encyclopedia_page_inspected": True,
            "external_collected_edition_inspected": True,
            "voynich_images_opened": False,
            "voynich_transcription_or_formal_payload_opened": False,
            "f84_rows_or_images_accessed": False,
        },
        "claim_ceiling": "Exact-surface secondary attribution to a Shirakatsi bolorak/circular-table tradition plus explicit source conflict and missing slot key; no eight-phase identification, independent homologue, Voynich alignment, Armenian origin, authorship, language, plaintext, meaning, or translation.",
        "inputs": {str(p.relative_to(ROOT)): sha(p) for p in (GDT355, GDT357)},
        "remote_source_hashes": {row["source_id"]: row["remote_sha256"] for row in SOURCES},
        "outputs": {str(path.relative_to(ROOT)): sha(path) for path in paths.values()},
        "documents": {str(path.relative_to(ROOT)): sha(path) for path in (EXP / "METHOD.md", EXP / "SOURCE_AUDIT.md", EXP / "REPORT.md")},
        "implementation": {str(Path(__file__).relative_to(ROOT)): sha(Path(__file__))},
    }
    content = dict(result)
    result["result_content_sha256"] = hashlib.sha256(stable(content)).hexdigest()
    (ART / "gdt358_result.json").write_bytes(stable(result))


if __name__ == "__main__":
    main()
