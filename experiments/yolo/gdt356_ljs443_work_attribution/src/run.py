#!/usr/bin/env python3
"""Build the external-only GDT356 LJS 443 work-attribution audit."""
from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
EXP = ROOT / "experiments/yolo/gdt356_ljs443_work_attribution"
ART = EXP / "artifacts"
GDT355 = ROOT / "experiments/yolo/gdt355_ljs443_diagram_series_census/artifacts/gdt355_result.json"


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
        "source_id": "PENN_LJS443_CATALOG_JSON",
        "source_class": "OFFICIAL_LIBRARY_CATALOGUE",
        "bibliographic_reference": "Penn Libraries, LJS 443, bibid 9951496233503681",
        "url": "https://find.library.upenn.edu/catalog/9951496233503681.json",
        "remote_sha256": "c111a97ecbdb2a6727b1ca3c67fb9ff6e1141e53ea2e3ec947c1cded43656785",
        "exact_support": "Contents note assigns ff.145v-212r to Hovhannes Vardapet/Sarkawag and ff.213r-244r to Anania Shirakatsi; decoration note lists diagrams through f.211v.",
    },
    {
        "source_id": "PENN_LJS443_TEI",
        "source_class": "OFFICIAL_LIBRARY_METADATA",
        "bibliographic_reference": "OPenn TEI description of LJS 443",
        "url": "https://openn.library.upenn.edu/Data/0001/ljs443/data/ljs443_TEI.xml",
        "remote_sha256": "becfa33a8ca1952a7c914e09d070e4d7cdd4f3509291998916a956397b8391b4",
        "exact_support": "Binds current/legacy foliation and diagram surfaces; summary identifies the manuscript as an Armenian calendar compilation after 1416.",
    },
    {
        "source_id": "GALSTYAN_2022_SARKAWAG",
        "source_class": "SCHOLARLY_ARTICLE",
        "bibliographic_reference": "Gor Galstyan, The Commentary of the Armenian Calendar by Yovhannes Sarkawag, Banber Matenadarani 33 (2022), 425-445",
        "url": "https://banber.matenadaran.am/ftp/data/Banber33/23.GorGalstyan.pdf",
        "remote_sha256": "01e254512743c9c6a41ade8d0331668541be0b4d00e7f0e79727dbe502a5f463",
        "exact_support": "Documents the composite theoretical/practical collection, calendar exemplars, Kharnakhoran, lunar indicator, 532-year tables, and 19-year lunar computations; gives no LJS443 folio concordance.",
    },
    {
        "source_id": "BROUTIAN_2009_CALENDARS",
        "source_class": "SCHOLARLY_ARTICLE",
        "bibliographic_reference": "Grigor Broutian, Persian and Arabic Calendars as Presented by Anania Shirakatsi, Tarikh-e Elm 8 (2009), 1-17",
        "url": "https://arar.sci.am/Content/9535/73-89.pdf",
        "remote_sha256": "0366a3f1e9047b15126b97555600ce80c219b45c8f8dcc0696b17b915c60e718",
        "exact_support": "Describes the Kharnakhoran tradition as twelve large comparative calendar tables with day rows and calendar landmarks; does not identify the Penn spiral diagrams.",
    },
]

RANGES = [
    {"range_id":"R01","modern_folio_start":"3r","modern_folio_end":"54v","catalogued_work":"COMMENTARY_ON_CALENDAR","catalogued_author":"HAKOB_GHRIMETSI","contains_narrow_gdt355_subseries":"NO","support":"PENN_LJS443_CATALOG_JSON"},
    {"range_id":"R02","modern_folio_start":"145v","modern_folio_end":"212r","catalogued_work":"COMMENTARY_ON_CALENDAR","catalogued_author":"HOVHANNES_VARDAPET_SARKAWAG","contains_narrow_gdt355_subseries":"YES","support":"PENN_LJS443_CATALOG_JSON"},
    {"range_id":"R03","modern_folio_start":"209r","modern_folio_end":"210r","catalogued_work":"GDT355_NARROW_EIGHT_SPIRAL_BAND_SUBSERIES","catalogued_author":"WITHIN_R02_NOT_INDIVIDUALLY_ATTRIBUTED","contains_narrow_gdt355_subseries":"YES","support":"GDT355_PLUS_RANGE_CONTAINMENT"},
    {"range_id":"R04","modern_folio_start":"213r","modern_folio_end":"244r","catalogued_work":"ON_ASTRONOMY","catalogued_author":"ANANIA_SHIRAKATSI","contains_narrow_gdt355_subseries":"NO","support":"PENN_LJS443_CATALOG_JSON"},
]

FEATURES = [
    {"feature_id":"F01_CONTAINING_WORK","candidate":"Hovhannes Sarkawag Commentary on the Armenian Calendar","support_status":"SUPPORTED_WORK_LEVEL","source_support":"Penn exact range 145v-212r contains 209r-210r","eligible_for_slot_alignment":"NO","reason":"Work identity does not specify diagram values or authorship of this copy's drawings."},
    {"feature_id":"F02_COMPOSITE_CALENDAR_SYSTEM","candidate":"Theoretical and practical calendar collection","support_status":"SUPPORTED_WORK_LEVEL","source_support":"Galstyan 2022","eligible_for_slot_alignment":"NO","reason":"Broad work architecture only."},
    {"feature_id":"F03_MULTINATION_CALENDAR_EXEMPLARS","candidate":"Calendar exemplars and Kharnakhoran for multiple peoples","support_status":"SUPPORTED_SYSTEM_LEVEL_NOT_FOLIO_KEYED","source_support":"Galstyan 2022; Broutian 2009","eligible_for_slot_alignment":"NO","reason":"No concordance to the selected Penn folios."},
    {"feature_id":"F04_LUNAR_COMPUTATION","candidate":"Lunar indicator plus birth/fullness and 19-year-cycle computations","support_status":"SUPPORTED_SYSTEM_LEVEL_NOT_FOLIO_KEYED","source_support":"Galstyan 2022","eligible_for_slot_alignment":"NO","reason":"No source identifies an eight-phase sequence on 209r-210r."},
    {"feature_id":"F05_532_YEAR_TABLES","candidate":"Julian and Armenian fixed 532-year tables","support_status":"SUPPORTED_SYSTEM_LEVEL_NOT_FOLIO_KEYED","source_support":"Galstyan 2022","eligible_for_slot_alignment":"NO","reason":"No folio mapping to the spiral subseries."},
    {"feature_id":"F06_KHARNAKHORAN_SPIRAL_IDENTITY","candidate":"The selected spiral pages are Kharnakhoran tables","support_status":"UNSUPPORTED_FOLIO_LEVEL","source_support":"Broutian describes twelve large tables but supplies no LJS443 concordance","eligible_for_slot_alignment":"NO","reason":"Topology and folio identity are not established."},
    {"feature_id":"F07_EIGHT_LUNAR_PHASES","candidate":"Eight bands encode eight lunar phases","support_status":"UNSUPPORTED_FOLIO_LEVEL","source_support":"No audited source","eligible_for_slot_alignment":"NO","reason":"Scholarly lunar discussion does not key eight slots; GDT355 has a twelve-lobe counterexample."},
    {"feature_id":"F08_ANANIA_ASTRONOMY_ITEM","candidate":"The selected pages belong to Anania Shirakatsi On Astronomy","support_status":"CONTRADICTED_BY_RANGE","source_support":"Penn starts that item at 213r after the selected 209r-210r pages","eligible_for_slot_alignment":"NO","reason":"Exact catalogue range contradiction."},
    {"feature_id":"F09_SLOT_VALUES_ORDER","candidate":"Exact values ownership start direction and order for 209r-210r","support_status":"UNSUPPORTED_FOLIO_LEVEL","source_support":"No audited source","eligible_for_slot_alignment":"NO","reason":"Required transfer key is absent."},
]

COUNTEREXAMPLES = [
    {"counterexample_id":"CE01_RANGE","evidence":"Anania On Astronomy begins at 213r","implication":"209r-210r cannot be assigned to that catalogued item."},
    {"counterexample_id":"CE02_LUNAR_SCALE","evidence":"Audited scholarship discusses a 19-year lunar cycle and lunar birth/fullness calculations, not an eight-phase key for these folios","implication":"Lunar content at work level does not identify the eight bands."},
    {"counterexample_id":"CE03_TABLE_FORM","evidence":"Kharnakhoran is described as twelve large comparative tables","implication":"Do not relabel the three spiral pages Kharnakhoran without a folio concordance."},
    {"counterexample_id":"CE04_CURVED_TWELVE","evidence":"GDT355 current f.206v has twelve curved text-bearing lobes","implication":"Curved lobe form does not uniquely encode eight."},
    {"counterexample_id":"CE05_NO_REPLICATION","evidence":"One contiguous manuscript series and no second externally keyed homologous folio","implication":"No independent transfer endpoint exists."},
]


def main() -> None:
    ART.mkdir(parents=True, exist_ok=True)
    source_path = ART / "gdt356_external_sources.tsv"
    range_path = ART / "gdt356_work_ranges.tsv"
    feature_path = ART / "gdt356_feature_audit.tsv"
    counter_path = ART / "gdt356_counterexamples.tsv"
    write_tsv(source_path, SOURCES)
    write_tsv(range_path, RANGES)
    write_tsv(feature_path, FEATURES)
    write_tsv(counter_path, COUNTEREXAMPLES)
    result = {
        "experiment": "GDT356",
        "schema": "GDT356_LJS443_WORK_ATTRIBUTION_V1",
        "status": "WORK_ATTRIBUTION_NARROWED_FOLIO_KEY_STILL_ABSENT",
        "exposure": "POST_GDT355_EXTERNAL_SOURCE_ATTRIBUTION_AUDIT",
        "counts": {
            "external_sources": len(SOURCES),
            "catalogued_ranges": len(RANGES),
            "audited_features": len(FEATURES),
            "supported_work_level": sum(x["support_status"] == "SUPPORTED_WORK_LEVEL" for x in FEATURES),
            "supported_system_not_folio_keyed": sum(x["support_status"] == "SUPPORTED_SYSTEM_LEVEL_NOT_FOLIO_KEYED" for x in FEATURES),
            "unsupported_folio_level": sum(x["support_status"] == "UNSUPPORTED_FOLIO_LEVEL" for x in FEATURES),
            "contradicted_by_range": sum(x["support_status"] == "CONTRADICTED_BY_RANGE" for x in FEATURES),
            "features_eligible_for_slot_alignment": sum(x["eligible_for_slot_alignment"] == "YES" for x in FEATURES),
        },
        "work_attribution": {
            "narrow_subseries_folios": ["209r", "209v", "210r"],
            "containing_catalogued_range": "145v-212r",
            "containing_work": "Commentary on the Calendar",
            "catalogued_author": "Hovhannes Vardapet, also known as Hovhannes Sarkawag",
            "individual_diagram_authorship_claimed": False,
        },
        "decision": "Search Hovhannes Sarkawag commentary editions or specialist catalogues for a folio concordance; do not score the Voynich target without fixed external slot values and order.",
        "source_access": {
            "external_catalogue_and_scholarship_accessed": True,
            "external_manuscript_images_newly_opened": False,
            "voynich_images_opened": False,
            "voynich_transcription_or_formal_payload_opened": False,
            "f84_rows_or_images_accessed": False,
        },
        "claim_ceiling": "Containing catalogued work plus system-level calendrical possibilities and an explicit absent folio key; no diagram identity, slot value, copying, Armenian origin for Voynich, language, plaintext, or translation.",
        "inputs": {str(GDT355.relative_to(ROOT)): sha(GDT355)},
        "remote_source_hashes": {row["source_id"]: row["remote_sha256"] for row in SOURCES},
        "outputs": {str(path.relative_to(ROOT)): sha(path) for path in (source_path, range_path, feature_path, counter_path)},
        "documents": {str(path.relative_to(ROOT)): sha(path) for path in (EXP / "METHOD.md", EXP / "SOURCE_AUDIT.md", EXP / "REPORT.md")},
        "implementation": {str(Path(__file__).relative_to(ROOT)): sha(Path(__file__))},
    }
    content = dict(result)
    result["result_content_sha256"] = hashlib.sha256(stable(content)).hexdigest()
    (ART / "gdt356_result.json").write_bytes(stable(result))


if __name__ == "__main__":
    main()
