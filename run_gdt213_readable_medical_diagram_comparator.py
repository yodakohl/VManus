#!/usr/bin/env python3
"""Build the GDT213 readable labelled-medical-diagram comparator.

This is a fixed, qualitative system-architecture comparison.  It does not
read Voynich transcription, images, or any f84 artifact.
"""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_tsv(path: Path, rows: list[dict[str, object]], fields: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


SOURCES = [
    {
        "source_id": "BODLEIAN_ASHMOLE399_MANIFEST",
        "source_class": "PRIMARY_INSTITUTIONAL_IIIF",
        "repository": "Bodleian Libraries, University of Oxford",
        "shelfmark": "MS Ashmole 399",
        "folio": "MANUSCRIPT",
        "date_or_year": "1250-1310 catalogue range",
        "title_or_reference": "Medical and arithmetical treatises and recipes",
        "url": "https://iiif.bodleian.ox.ac.uk/iiif/manifest/2b7310aa-9199-4a5b-93fb-4f5f075ca28a.json",
        "retrieved_sha256": "154f04ccb77eb4186b79445f4fda0ddbb483e28ad526463f78f940f86aba1e10",
        "supporting_scope": "official shelfmark, canvas order, folio labels, institutional image services",
        "rights_note": "Bodleian image metadata; image terms CC BY-NC 4.0 as stated by the provider",
    },
    {
        "source_id": "BODLEIAN_ASHMOLE399_F13V",
        "source_class": "PRIMARY_INSTITUTIONAL_IMAGE",
        "repository": "Bodleian Libraries, University of Oxford",
        "shelfmark": "MS Ashmole 399",
        "folio": "13v",
        "date_or_year": "late thirteenth century",
        "title_or_reference": "female reproductive-system diagram",
        "url": "https://iiif.bodleian.ox.ac.uk/iiif/image/b4f412ad-a030-4ee9-9da4-01e7d93190f8/full/1800,/0/default.jpg",
        "retrieved_sha256": "48f79d1e003bf384ab4e0d7bef50aecdfa44a6ae2dc09ff567894cee260cf93a",
        "supporting_scope": "direct visual geometry, text placement, colors, and figure placement only",
        "rights_note": "not redistributed; hash and official URL only",
    },
    {
        "source_id": "BODLEIAN_ASHMOLE399_F22V",
        "source_class": "PRIMARY_INSTITUTIONAL_IMAGE",
        "repository": "Bodleian Libraries, University of Oxford",
        "shelfmark": "MS Ashmole 399",
        "folio": "22v",
        "date_or_year": "late thirteenth century",
        "title_or_reference": "eyes-and-brain diagram",
        "url": "https://iiif.bodleian.ox.ac.uk/iiif/image/b3c5b023-c431-4a4b-adcf-c407a1a7886d/full/1800,/0/default.jpg",
        "retrieved_sha256": "4d98f9bb3ebd3095f7b994aa05f58f7b734c8487ce0f22cb33bb0230eb58b7c2",
        "supporting_scope": "direct visual geometry and long-text placement only",
        "rights_note": "not redistributed; hash and official URL only",
    },
    {
        "source_id": "WHITTINGTON_2008",
        "source_class": "SCHOLARLY_ARTICLE",
        "repository": "Different Visions",
        "shelfmark": "DOI 10.61302/GLRT6998",
        "folio": "13v; 22v",
        "date_or_year": "2008",
        "title_or_reference": "Karl Whittington, The Cruciform Womb: Process, Symbol and Salvation in Bodleian Library MS Ashmole 399",
        "url": "https://differentvisions.org/the-cruciform-womb/",
        "retrieved_sha256": "58d62864799629b62e25234ce63dd9dbe3f79327b47dbdd58bf913f51ceb9776",
        "supporting_scope": "diagram identity; component labels; original label layer versus later conception/childbirth recipes; conceptual process-system interpretation",
        "rights_note": "claims paraphrased; no article text redistributed",
    },
    {
        "source_id": "GRIFFIN_2018",
        "source_class": "SCHOLARLY_PUBLIC_HISTORY",
        "repository": "Thinking 3D / University of Oxford project",
        "shelfmark": "MS Ashmole 399",
        "folio": "13v",
        "date_or_year": "2018",
        "title_or_reference": "Sarah Griffin, Ordering the Internal Body: A Thirteenth-Century Uterus Diagram",
        "url": "https://www.thinking3d.ac.uk/Ashmole1298/",
        "retrieved_sha256": "b299ff2e5eedb5d313dfd9f452aee5b822da23b46e69979c10e5d437b3224b16",
        "supporting_scope": "medical-compendium context; schematic functional rendering; component-label uniqueness; later practical-remedy layers in multiple hands",
        "rights_note": "claims paraphrased; no page text redistributed",
    },
]


OBSERVATIONS = [
    {
        "observation_id": "GDT213_O01",
        "folio": "13v",
        "provenance": "AI_DIRECT_VISUAL_OBSERVATION",
        "source_id": "BODLEIAN_ASHMOLE399_F13V",
        "confidence": "HIGH",
        "evidence_type": "OBSERVATION",
        "neutral_observation": "A large bilateral outlined system dominates the page; paired curved upper branches, round terminals, teardrop forms, and column-like lower forms connect to or flank a central vertical channel.",
        "interpretation_separated": "No anatomical name or physiological function is inferred from the pixels.",
    },
    {
        "observation_id": "GDT213_O02",
        "folio": "13v",
        "provenance": "AI_DIRECT_VISUAL_OBSERVATION",
        "source_id": "BODLEIAN_ASHMOLE399_F13V",
        "confidence": "HIGH",
        "evidence_type": "OBSERVATION",
        "neutral_observation": "One small humanlike figure is enclosed by an oval near the upper center of the outlined system.",
        "interpretation_separated": "The figure's identity is supplied only by scholarship, not by this observation.",
    },
    {
        "observation_id": "GDT213_O03",
        "folio": "13v",
        "provenance": "AI_DIRECT_VISUAL_OBSERVATION",
        "source_id": "BODLEIAN_ASHMOLE399_F13V",
        "confidence": "HIGH",
        "evidence_type": "OBSERVATION",
        "neutral_observation": "Several short inscriptions lie inside, along, or immediately against specific outlined components.",
        "interpretation_separated": "Visual placement supports component association but not a modern translation of any inscription.",
    },
    {
        "observation_id": "GDT213_O04",
        "folio": "13v",
        "provenance": "AI_DIRECT_VISUAL_OBSERVATION",
        "source_id": "BODLEIAN_ASHMOLE399_F13V",
        "confidence": "HIGH",
        "evidence_type": "OBSERVATION",
        "neutral_observation": "Dense longer text blocks occupy open spaces inside and beside the diagram and visibly differ in scale and layout from the short component inscriptions.",
        "interpretation_separated": "The content and chronological relation of the text layers come only from scholarship.",
    },
    {
        "observation_id": "GDT213_O05",
        "folio": "22v",
        "provenance": "AI_DIRECT_VISUAL_OBSERVATION",
        "source_id": "BODLEIAN_ASHMOLE399_F22V",
        "confidence": "HIGH",
        "evidence_type": "OBSERVATION",
        "neutral_observation": "A central vertical form branches symmetrically toward two circular terminals beneath an upper geometric band.",
        "interpretation_separated": "The eyes-and-brain identification is source-supplied, not inferred here.",
    },
    {
        "observation_id": "GDT213_O06",
        "folio": "22v",
        "provenance": "AI_DIRECT_VISUAL_OBSERVATION",
        "source_id": "BODLEIAN_ASHMOLE399_F22V",
        "confidence": "HIGH",
        "evidence_type": "OBSERVATION",
        "neutral_observation": "Continuous prose columns and lines fill most spaces around and partly within the branching form; there is no comparable dense set of visibly isolated component-caption strings.",
        "interpretation_separated": "This is a layout contrast with folio 13v, not a claim about textual grammar.",
    },
    {
        "observation_id": "GDT213_S01",
        "folio": "13v",
        "provenance": "EXISTING_SCHOLARLY_INTERPRETATION",
        "source_id": "WHITTINGTON_2008;GRIFFIN_2018",
        "confidence": "SOURCE_ASSERTED",
        "evidence_type": "INTERPRETATION",
        "neutral_observation": "Scholarship identifies the page as a schematic female reproductive-system diagram whose individual components are labelled.",
        "interpretation_separated": "Readable-medical identification; not transferred to Voynich.",
    },
    {
        "observation_id": "GDT213_S02",
        "folio": "13v",
        "provenance": "EXISTING_SCHOLARLY_INTERPRETATION",
        "source_id": "WHITTINGTON_2008;GRIFFIN_2018",
        "confidence": "SOURCE_ASSERTED",
        "evidence_type": "FORMAL_STRUCTURE",
        "neutral_observation": "Scholarship distinguishes an earlier component-label layer from later surrounding practical remedies in multiple hands.",
        "interpretation_separated": "This supplies a readable document-layer precedent, not evidence that Voynich q13 has the same chronology.",
    },
    {
        "observation_id": "GDT213_S03",
        "folio": "13v;22v",
        "provenance": "EXISTING_SCHOLARLY_INTERPRETATION",
        "source_id": "WHITTINGTON_2008",
        "confidence": "SOURCE_ASSERTED",
        "evidence_type": "INTERPRETATION",
        "neutral_observation": "Scholarship treats these pages as conceptual diagrams emphasizing process or transmission rather than naturalistic depiction alone.",
        "interpretation_separated": "Conceptual-medical diagramming is the only transferable claim.",
    },
]


COMPARISON = [
    {
        "axis_id": "A01",
        "architecture_axis": "SCHEMATIC_CONNECTED_SYSTEM",
        "ashmole399_evidence": "source-identified conceptual medical systems use branches, channels, bilateral terminals, and abstract components",
        "q13_f80_f82_evidence": "human catalogue records connected tubes, pools, enclosures, and figures",
        "comparison_class": "ARCHITECTURE_MATCH",
        "semantic_value": "MEDIEVAL_MEDICAL_SYSTEM_FORMAT_PLAUSIBLE",
        "limitation": "different exact topology and readable subject matter",
    },
    {
        "axis_id": "A02",
        "architecture_axis": "SHORT_LOCAL_LABELS_PLUS_LONGER_PROSE",
        "ashmole399_evidence": "f13v has source-identified component labels plus longer practical remedy text",
        "q13_f80_f82_evidence": "23 text-linked catalogue loci coexist with paragraph prose on the two pilot pages",
        "comparison_class": "ARCHITECTURE_MATCH",
        "semantic_value": "MIXED_LABEL_RECORD_LAYOUT_PLAUSIBLE",
        "limitation": "q13 label/prose chronology and functions are unknown",
    },
    {
        "axis_id": "A03",
        "architecture_axis": "SINGULAR_COMPONENT_OWNERSHIP",
        "ashmole399_evidence": "readable labels identify individual diagram components",
        "q13_f80_f82_evidence": "22 of 23 text-linked inventory rows are proximity-only; only f82r.10 is connected-component evidence",
        "comparison_class": "STRONG_ASYMMETRY",
        "semantic_value": "NO_LABEL_DICTIONARY_TRANSFER",
        "limitation": "q13 lacks the readable comparator's owner clarity",
    },
    {
        "axis_id": "A04",
        "architecture_axis": "HUMANLIKE_FIGURE_EMBEDDED_IN_SYSTEM",
        "ashmole399_evidence": "one small figure lies inside an oval within f13v's system",
        "q13_f80_f82_evidence": "multiple humanlike figures occur in or beside pools and connected structures",
        "comparison_class": "PARTIAL_ARCHITECTURE_MATCH",
        "semantic_value": "FIGURE_NEED_NOT_BE_PERSONIFIED_SUBSTANCE",
        "limitation": "number, placement, and readable functions differ",
    },
    {
        "axis_id": "A05",
        "architecture_axis": "MULTIPLE_CHRONOLOGICAL_TEXT_LAYERS",
        "ashmole399_evidence": "scholarship distinguishes earlier labels from later remedies in multiple hands",
        "q13_f80_f82_evidence": "no equivalent chronological layer distinction is established",
        "comparison_class": "VOYNICH_UNSUPPORTED",
        "semantic_value": "COMPOSITE_LAYER_HYPOTHESIS_ONLY",
        "limitation": "must not infer later additions in q13 from layout resemblance",
    },
    {
        "axis_id": "A06",
        "architecture_axis": "VISUAL_SYSTEM_IDENTIFIES_TEXT_CONTENT",
        "ashmole399_evidence": "readable labels and scholarship identify anatomy and practical reproductive remedies",
        "q13_f80_f82_evidence": "GDT212 recovers only weak setting/hydraulic role visibility and no indication/procedure/outcome field",
        "comparison_class": "STRONG_ASYMMETRY",
        "semantic_value": "CONTENT_BRIDGE_ABSENT",
        "limitation": "medieval format plausibility is not a Voynich gloss",
    },
    {
        "axis_id": "A07",
        "architecture_axis": "THERAPEUTIC_BALNEOLOGY_SPECIFICITY",
        "ashmole399_evidence": "medical anatomy, generation, and added remedies; not a bath-site book",
        "q13_f80_f82_evidence": "GDT210 therapeutic balneology remains the closest readable page-genre comparator",
        "comparison_class": "NO_CONTENT_MATCH",
        "semantic_value": "BROAD_MEDICAL_PRIOR_ONLY",
        "limitation": "Ashmole 399 neither confirms nor replaces the bath theory",
    },
    {
        "axis_id": "A08",
        "architecture_axis": "EXACT_TOPOLOGICAL_HOMOLOG",
        "ashmole399_evidence": "bilateral anatomical and optical systems without repeated bathing arrays",
        "q13_f80_f82_evidence": "repeated figures, pools, descending tubes, and page-spanning hydraulic structures",
        "comparison_class": "NO_EXACT_HOMOLOG",
        "semantic_value": "NONE",
        "limitation": "no direct source descent or object identification",
    },
]


COUNTEREXAMPLES = [
    {
        "counterexample_id": "C01",
        "claim_blocked": "Q13_LABELS_NAME_NEARBY_FIGURES",
        "evidence": "Only one of 23 f80r/f82r text-linked inventory rows has connected-component evidence; 22 are proximity-only.",
        "consequence": "The readable component-caption precedent cannot convert proximity into ownership.",
    },
    {
        "counterexample_id": "C02",
        "claim_blocked": "Q13_IS_AN_ANATOMY_DIAGRAM",
        "evidence": "Ashmole 399 has source-readable anatomical labels and a different bilateral topology; q13 has no comparable readable anchor.",
        "consequence": "The match is document architecture, not subject identity.",
    },
    {
        "counterexample_id": "C03",
        "claim_blocked": "Q13_HAS_LATER_REMEDIES_OVER_AN_EARLIER_DIAGRAM",
        "evidence": "The chronological separation is documented for Ashmole 399 only.",
        "consequence": "A composite-layer q13 model remains speculative and receives no score.",
    },
    {
        "counterexample_id": "C04",
        "claim_blocked": "VISIBLE_FIGURES_RECOVER_MEDICAL_INDICATIONS",
        "evidence": "GDT212 found indication text in all 32 readable bath records but explicit bodily-condition cues in only 14 catalogue scenes.",
        "consequence": "Figures cannot ground diseases, procedures, or outcomes.",
    },
    {
        "counterexample_id": "C05",
        "claim_blocked": "ASHMOLE399_CONFIRMS_BALNEOLOGY",
        "evidence": "The readable comparator concerns reproductive anatomy, conceptual physiology, and added remedies rather than baths.",
        "consequence": "It strengthens broad medical-technical format plausibility only.",
    },
]


def main() -> None:
    source_path = ROOT / "gdt213_ashmole_source_manifest.tsv"
    observation_path = ROOT / "gdt213_readable_medical_diagram_observations.tsv"
    comparison_path = ROOT / "gdt213_system_architecture_comparison.tsv"
    counter_path = ROOT / "gdt213_counterexamples.tsv"
    result_path = ROOT / "gdt213_result.json"

    write_tsv(source_path, SOURCES, list(SOURCES[0]))
    write_tsv(observation_path, OBSERVATIONS, list(OBSERVATIONS[0]))
    write_tsv(comparison_path, COMPARISON, list(COMPARISON[0]))
    write_tsv(counter_path, COUNTEREXAMPLES, list(COUNTEREXAMPLES[0]))

    classes: dict[str, int] = {}
    for row in COMPARISON:
        classes[row["comparison_class"]] = classes.get(row["comparison_class"], 0) + 1

    inputs = {}
    for name in [
        "GDT210_THERAPEUTIC_BALNEOLOGICAL_COMPARATOR_REPORT.md",
        "GDT212_DE_BALNEIS_VISUAL_TEXT_GROUNDING_REPORT.md",
        "run_gdt213_readable_medical_diagram_comparator.py",
    ]:
        inputs[name] = sha256(ROOT / name)

    outputs = {
        path.name: sha256(path)
        for path in [source_path, observation_path, comparison_path, counter_path]
    }
    documents = {
        name: sha256(ROOT / name)
        for name in [
            "GDT213_READABLE_MEDICAL_DIAGRAM_COMPARATOR_METHOD.md",
            "GDT213_READABLE_MEDICAL_DIAGRAM_SOURCE_AUDIT.md",
            "GDT213_READABLE_MEDICAL_DIAGRAM_COMPARATOR_REPORT.md",
        ]
    }
    result = {
        "experiment": "GDT213_READABLE_LABELLED_MEDICAL_DIAGRAM_COMPARATOR",
        "status": "MEDIEVAL_MEDICAL_SCHEMATIC_DOCUMENT_ARCHITECTURE_SUPPORTED_CONTENT_BRIDGE_ABSENT",
        "decision": "ARCHITECTURE_HOMOLOG_WITHOUT_TOPOLOGY_OR_SEMANTIC_TRANSFER",
        "sources": {
            "count": len(SOURCES),
            "primary_institutional_images": 2,
            "scholarly_interpretive_sources": 2,
        },
        "observations": {
            "count": len(OBSERVATIONS),
            "ai_direct_visual_observations": sum(r["provenance"] == "AI_DIRECT_VISUAL_OBSERVATION" for r in OBSERVATIONS),
            "existing_scholarly_rows": sum(r["provenance"] == "EXISTING_SCHOLARLY_INTERPRETATION" for r in OBSERVATIONS),
        },
        "comparison": {
            "axis_count": len(COMPARISON),
            "class_counts": classes,
            "q13_pilot_pages": ["f80r", "f82r"],
            "q13_text_linked_inventory_rows": 23,
            "q13_proximity_only_rows": 22,
            "q13_connected_component_rows": 1,
            "exact_topological_homolog": False,
            "singular_readable_voynich_bridge": False,
        },
        "interpretation": {
            "supported": "A medieval medical manuscript can combine abstract connected-system geometry, short component labels, and longer practical text on the same page.",
            "not_supported": [
                "q13 is an anatomy diagram",
                "q13 labels name nearby figures",
                "q13 prose is a later addition",
                "any Voynich word has an anatomical, therapeutic, or hydraulic meaning",
                "plaintext, language, translation, or source descent",
            ],
            "next_test": "Seek a readable medieval bath or hydraulic diagram with independently owned component labels; Ashmole 399 supplies the document architecture but not the content/topology bridge.",
        },
        "f84": {
            "accessed": False,
            "input": False,
            "output": False,
        },
        "inputs_sha256": inputs,
        "outputs_sha256": outputs,
        "documents_sha256": documents,
        "validator_sha256": sha256(ROOT / "validate_gdt213_readable_medical_diagram_comparator.py"),
    }
    canonical = json.dumps(result, sort_keys=True, separators=(",", ":"))
    result["content_sha256"] = hashlib.sha256(canonical.encode()).hexdigest()
    result_path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
