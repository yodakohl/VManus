#!/usr/bin/env python3
"""Build the source-first GDT354 LJS 443 / f68v3 audit."""
from __future__ import annotations

import csv
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT))
from tools.vmanus_experiment import GuardedTSV  # noqa: E402

EXP = ROOT / "experiments/yolo/gdt354_ljs443_f68v3_source_audit"
ART = EXP / "artifacts"
HUMAN = ROOT / "experiments/semantic_assumptions/results/existing_human_page_annotations.tsv"


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
        "source_id": "LJS443_TEI",
        "source_class": "OFFICIAL_LIBRARY_METADATA",
        "manuscript_or_target": "University of Pennsylvania LJS 443",
        "folio_or_scope": "whole manuscript",
        "url": "https://openn.library.upenn.edu/Data/0001/ljs443/data/ljs443_TEI.xml",
        "bibliographic_reference": "OPenn TEI description of LJS 443, Collection of texts on the calendar",
        "exact_support": "Armenian collection of calendar commentaries, treatises, tables and diagrams; written after 1416; includes Anania Shirakatsi among named authors; diagrams on ff.192r-211v.",
        "remote_sha256": "becfa33a8ca1952a7c914e09d070e4d7cdd4f3509291998916a956397b8391b4",
        "evidence_use": "IDENTITY_DATE_CONTEXT_AND_FOLIO_MAPPING",
    },
    {
        "source_id": "LJS443_0422",
        "source_class": "OFFICIAL_PRIMARY_FACSIMILE",
        "manuscript_or_target": "University of Pennsylvania LJS 443",
        "folio_or_scope": "209r = old 210r",
        "url": "https://openn.library.upenn.edu/Data/0001/ljs443/data/web/0088_0422_web.jpg",
        "bibliographic_reference": "OPenn web image 0088_0422",
        "exact_support": "Official facsimile surface identified as a diagram by the TEI.",
        "remote_sha256": "a218414d67f5044281c8cf6e6a3606447d01b023782a8756d1a3a3207a660530",
        "evidence_use": "DIRECT_EXTERNAL_VISUAL_GEOMETRY",
    },
    {
        "source_id": "LJS443_0423",
        "source_class": "OFFICIAL_PRIMARY_FACSIMILE",
        "manuscript_or_target": "University of Pennsylvania LJS 443",
        "folio_or_scope": "209v = old 210v",
        "url": "https://openn.library.upenn.edu/Data/0001/ljs443/data/web/0088_0423_web.jpg",
        "bibliographic_reference": "OPenn web image 0088_0423",
        "exact_support": "Official facsimile surface identified as a diagram by the TEI.",
        "remote_sha256": "8254c56b22c5990cd560f7cfcc2efa6105803ee87954b2ea11a191b5bad768bf",
        "evidence_use": "DIRECT_EXTERNAL_VISUAL_GEOMETRY",
    },
    {
        "source_id": "LJS443_0424",
        "source_class": "OFFICIAL_PRIMARY_FACSIMILE",
        "manuscript_or_target": "University of Pennsylvania LJS 443",
        "folio_or_scope": "210r = old 211r",
        "url": "https://openn.library.upenn.edu/Data/0001/ljs443/data/web/0088_0424_web.jpg",
        "bibliographic_reference": "OPenn web image 0088_0424",
        "exact_support": "Official facsimile surface identified as a diagram by the TEI.",
        "remote_sha256": "6c5227d8f040c16c9d9eed8d2d5563c3c0d5a711f32038af35e47d5a9d28f875",
        "evidence_use": "DIRECT_EXTERNAL_VISUAL_GEOMETRY",
    },
    {
        "source_id": "VOYNICH_NU_LJS443",
        "source_class": "HUMAN_SECONDARY_COMPARISON",
        "manuscript_or_target": "LJS 443 and Voynich f68v3",
        "folio_or_scope": "illustration survey",
        "url": "https://www.voynich.nu/illustr.html",
        "bibliographic_reference": "Rene Zandbergen, The illustrations in the manuscript",
        "exact_support": "Reports several similar spiral drawings in LJS 443, with different spiral counts and directions, and explicitly warns that illustration interpretation is speculative.",
        "remote_sha256": "",
        "evidence_use": "PRIOR_HUMAN_TOPOLOGY_COMPARISON_ONLY",
    },
    {
        "source_id": "COMMONS_SHIRAKATSI_PHASES",
        "source_class": "HUMAN_SECONDARY_ICONOGRAPHIC_LABEL",
        "manuscript_or_target": "Anania Shirakatsi diagram reproduction",
        "folio_or_scope": "reproduction attributed to Soviet Armenian Encyclopedia vol.1 p.363",
        "url": "https://commons.wikimedia.org/wiki/File:Anania_Shirakatsi,_7th_century,_Phases_of_the_Moon,_Bolorakner.png",
        "bibliographic_reference": "Wikimedia Commons file description; secondary source only",
        "exact_support": "Calls the reproduced diagram Phases of the Moon; does not provide a folio-specific scholarly transcription or ordered compartment key.",
        "remote_sha256": "",
        "evidence_use": "PROVISIONAL_LUNAR_INTERPRETATION_NOT_SLOT_EVIDENCE",
    },
    {
        "source_id": "PAMBAKIAN_2022",
        "source_class": "SCHOLARLY_CONTEXT",
        "manuscript_or_target": "Cosmology attributed to Anania Shirakatsi",
        "folio_or_scope": "critical edition and study",
        "url": "https://doi.org/10.17630/sta/1372",
        "bibliographic_reference": "Stephanie Pambakian, The Cosmology attributed to Anania Sirakaci, PhD thesis, University of St Andrews, 2022",
        "exact_support": "Scholarly study of Anania's Cosmology and computistical context; accessible metadata does not identify the LJS 443 eight compartments.",
        "remote_sha256": "",
        "evidence_use": "HISTORICAL_CONTEXT_NOT_SLOT_KEY",
    },
]


OBSERVATIONS = [
    {
        "observation_id": "OBS_LJS443_0422",
        "source_id": "LJS443_0422",
        "provenance": "AI_DIRECT_EXTERNAL_VISUAL_OBSERVATION",
        "confidence": "HIGH",
        "visible_geometry": "Central blank circle surrounded by eight curved radial compartments inside one outer circle; text follows compartment curves; repeated red-ringed circular and crescent-like marks occur around the cycle.",
        "interpretation": "NONE_GEOMETRY_ONLY",
        "independent_witness": "NO_SAME_MANUSCRIPT_SERIES",
    },
    {
        "observation_id": "OBS_LJS443_0423",
        "source_id": "LJS443_0423",
        "provenance": "AI_DIRECT_EXTERNAL_VISUAL_OBSERVATION",
        "confidence": "HIGH",
        "visible_geometry": "Central blank circle surrounded by eight curved radial compartments inside one outer circle; text and repeated crescent-like or circular marks are distributed within the compartments.",
        "interpretation": "NONE_GEOMETRY_ONLY",
        "independent_witness": "NO_SAME_MANUSCRIPT_SERIES",
    },
    {
        "observation_id": "OBS_LJS443_0424",
        "source_id": "LJS443_0424",
        "provenance": "AI_DIRECT_EXTERNAL_VISUAL_OBSERVATION",
        "confidence": "HIGH",
        "visible_geometry": "Central blank circle surrounded by eight curved radial compartments inside one outer circle; text follows compartment curves; repeated ringed circular and crescent-like marks occur around the cycle.",
        "interpretation": "NONE_GEOMETRY_ONLY",
        "independent_witness": "NO_SAME_MANUSCRIPT_SERIES",
    },
]


GATES = [
    ("EXTERNAL_IDENTITY_DATE_CONTEXT", "PASS", "Official Penn metadata identifies LJS 443 as an Armenian post-1416 calendar/diagram collection."),
    ("EXTERNAL_EIGHT_CURVED_COMPARTMENT_FAMILY", "PASS", "Three adjacent official surfaces independently inspected within one manuscript series have eight curved compartments."),
    ("EXTERNAL_LUNAR_INTERPRETATION", "PROVISIONAL_SECONDARY", "Repeated crescent/circular marks and a secondary phase label support a hypothesis, not an ordered scholarly key."),
    ("EXTERNAL_READABLE_SLOT_VALUES", "FAIL", "No folio-specific scholarly compartment transcription/meaning key was located."),
    ("EXTERNAL_FIXED_START_AND_ORDER", "FAIL", "No authorial start or reading direction is documented."),
    ("TARGET_EIGHT_BAND_TOPOLOGY", "PASS", "Existing human annotation explicitly reports eight inward-spiralling written bands."),
    ("TARGET_FIXED_PHASE", "FAIL", "The human annotation supplies no start/direction/phase key."),
    ("TARGET_INDEPENDENT_FOLIO_TRANSFER", "FAIL", "Only one target folio has this topology."),
    ("VOYNICH_FORMAL_SCORING_AUTHORIZED", "NO", "The readable-slot, phase and transfer gates fail."),
]


def main() -> None:
    ART.mkdir(parents=True, exist_ok=True)
    guard = GuardedTSV(HUMAN, selector_column="page", allowed_values={"f68v3"})
    selected = list(guard)
    assert len(selected) == 1 and selected[0]["page"] == "f68v3"
    assert selected[0]["tentative_identifications_are_role_evidence"] == "0"
    assert "eight bands" in selected[0]["illustrations"].lower()

    sources_path = ART / "gdt354_external_sources.tsv"
    observations_path = ART / "gdt354_external_visual_observations.tsv"
    target_path = ART / "gdt354_target_topology.tsv"
    gates_path = ART / "gdt354_endpoint_capacity.tsv"
    write_tsv(sources_path, SOURCES)
    write_tsv(observations_path, OBSERVATIONS)
    write_tsv(target_path, [{
        "page": "f68v3",
        "provenance": "EXISTING_HUMAN_ANNOTATION",
        "annotation_source": selected[0]["source_url"],
        "visible_geometry": selected[0]["illustrations"],
        "text_topology": "EIGHT_INWARD_SPIRALLING_WRITING_BANDS",
        "fixed_start": "NO",
        "fixed_direction": "NO",
        "slot_values": "UNKNOWN",
        "tentative_identifications_are_role_evidence": "0",
    }])
    write_tsv(gates_path, [{"gate": gate, "status": status, "basis": basis} for gate, status, basis in GATES])

    result = {
        "experiment": "GDT354",
        "schema": "GDT354_LJS443_F68V3_SOURCE_AUDIT_V1",
        "status": "PROVISIONAL_EIGHT_BAND_SYSTEM_HOMOLOGUE_NO_SLOT_TRANSFER",
        "exposure": "SOURCE_FIRST_POSTHOC_ACQUISITION_AUDIT",
        "counts": {"external_source_rows": len(SOURCES), "external_facsimiles_inspected": 3, "direct_external_observations": len(OBSERVATIONS), "external_manuscripts": 1, "target_pages": 1, "gates_pass": 3, "gates_fail": 4, "gates_other": 2},
        "decision": "Retain LJS 443 as a provisional eight-curved-band calendar/astronomy diagram-family homologue; do not expose Voynich formal payload until external slot values/order and target phase/transfer exist.",
        "source_access": {
            "external_images_opened": True,
            "voynich_images_opened": False,
            "voynich_transcription_or_formal_payload_opened": False,
            "f84_rows_or_images_accessed": False,
            "human_annotation_guard_stats": guard.stats.__dict__,
        },
        "claim_ceiling": "Provisional eight-curved-band calendar/astronomy diagram-family homologue only; no lunar-table identity, slot value, phase, direction, Armenian connection, source copying, language, plaintext, or translation.",
        "selected_human_source_content_sha256": hashlib.sha256(stable(selected)).hexdigest(),
        "outputs": {str(path.relative_to(ROOT)): sha(path) for path in (sources_path, observations_path, target_path, gates_path)},
        "documents": {str(path.relative_to(ROOT)): sha(path) for path in (EXP / "METHOD.md", EXP / "SOURCE_AUDIT.md", EXP / "REPORT.md")},
        "implementation": {str(Path(__file__).relative_to(ROOT)): sha(Path(__file__))},
    }
    content = dict(result)
    result["result_content_sha256"] = hashlib.sha256(stable(content)).hexdigest()
    (ART / "gdt354_result.json").write_bytes(stable(result))


if __name__ == "__main__":
    main()

