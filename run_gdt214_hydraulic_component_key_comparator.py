#!/usr/bin/env python3
"""Build GDT214 from fixed external source facts and published GDT187."""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def tsv(name: str, rows: list[dict[str, object]]) -> None:
    with (ROOT / name).open("w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        w.writeheader()
        w.writerows(rows)


SOURCES = [
    {
        "source_id": "MET_451298_API",
        "source_class": "PRIMARY_INSTITUTIONAL_CATALOGUE",
        "repository": "The Metropolitan Museum of Art",
        "object_id": "451298 / 55.121.11",
        "date": "715 AH / 1315 CE",
        "title": "Design on Each Side for Waterwheel Worked by Donkey Power",
        "url": "https://collectionapi.metmuseum.org/public/collection/v1/objects/451298",
        "retrieved_sha256": "ee9385d403743ee2efe36ca4cfb110d2c069508349391362fc243d47054b21ef",
        "claim_scope": "object identity, date, manuscript/copy attribution, device function, public-domain image URLs",
    },
    {
        "source_id": "MET_551211_OBVERSE",
        "source_class": "PRIMARY_INSTITUTIONAL_IMAGE",
        "repository": "The Metropolitan Museum of Art",
        "object_id": "55.121.11 obverse",
        "date": "1315 CE",
        "title": "single-ladle water-raising design",
        "url": "https://images.metmuseum.org/CRDImages/is/original/sf55-121-11v.jpg",
        "retrieved_sha256": "9c22ff7c10dc39cfb367539196410ab8479ec748974bd87481ba5293b0e6c47c",
        "claim_scope": "direct visible geometry and placement of compact marks only",
    },
    {
        "source_id": "MET_551211_REVERSE",
        "source_class": "PRIMARY_INSTITUTIONAL_IMAGE",
        "repository": "The Metropolitan Museum of Art",
        "object_id": "55.121.11 reverse",
        "date": "1315 CE",
        "title": "four-ladle water-raising design",
        "url": "https://images.metmuseum.org/CRDImages/is/original/sf55-121-11r.jpg",
        "retrieved_sha256": "15defb9c300628f032e831e6baf32be045fff267c32e912ad42e604f0cee13fd",
        "claim_scope": "direct visible geometry and placement of compact marks only",
    },
    {
        "source_id": "BALAFREJ_2022",
        "source_class": "SCHOLARLY_ARTICLE",
        "repository": "21: Inquiries into Art, History, and the Visual",
        "object_id": "DOI 10.11588/xxi.2022.4.91685",
        "date": "2022",
        "title": "Lamia Balafrej, Automated Slaves, Ambivalent Images, and Noneffective Machines in al-Jazari's Compendium",
        "url": "https://doi.org/10.11588/xxi.2022.4.91685",
        "retrieved_sha256": "NOT_LOCALLY_FROZEN_DOI_BOUND",
        "claim_scope": "general medieval Arabic mechanical-diagram practice: compact letter references can link depicted components to explanatory text",
    },
]


OBS = [
    {
        "observation_id": "GDT214_O01",
        "side": "OBVERSE",
        "provenance": "AI_DIRECT_VISUAL_OBSERVATION",
        "confidence": "HIGH",
        "neutral_observation": "A quadruped occupies an upper framed compartment and is connected by a pole/shaft to gears and a lifting mechanism above a painted water area.",
        "interpretation_excluded": "animal identity and device function come only from the Met catalogue",
    },
    {
        "observation_id": "GDT214_O02",
        "side": "OBVERSE",
        "provenance": "AI_DIRECT_VISUAL_OBSERVATION",
        "confidence": "HIGH",
        "neutral_observation": "Multiple isolated one- or few-mark inscriptions occur next to shafts, wheels, frames, and the water-lifting element rather than forming a continuous text block.",
        "interpretation_excluded": "marks are not transcribed, sounded, or translated",
    },
    {
        "observation_id": "GDT214_O03",
        "side": "REVERSE",
        "provenance": "AI_DIRECT_VISUAL_OBSERVATION",
        "confidence": "HIGH",
        "neutral_observation": "Four parallel vertical lifting units occupy repeated bays beneath a shared horizontal gear/shaft system and above four painted water areas.",
        "interpretation_excluded": "no mechanical reconstruction is inferred from pixels",
    },
    {
        "observation_id": "GDT214_O04",
        "side": "REVERSE",
        "provenance": "AI_DIRECT_VISUAL_OBSERVATION",
        "confidence": "HIGH",
        "neutral_observation": "Compact isolated inscriptions recur beside different repeated parts of the multi-bay system.",
        "interpretation_excluded": "visual proximity does not by itself prove a label-key relation",
    },
    {
        "observation_id": "GDT214_S01",
        "side": "BOTH",
        "provenance": "EXISTING_HUMAN_CATALOGUE",
        "confidence": "SOURCE_ASSERTED",
        "neutral_observation": "The Met identifies the folio as two designs for a donkey-powered water-raising device in which wheels lift ladles and discharge water into an irrigation channel.",
        "interpretation_excluded": "not transferred to q13",
    },
    {
        "observation_id": "GDT214_S02",
        "side": "COMPARATOR_TRADITION",
        "provenance": "EXISTING_SCHOLARLY_INTERPRETATION",
        "confidence": "SOURCE_ASSERTED_GENERAL_TRADITION",
        "neutral_observation": "Balafrej documents a medieval Arabic mechanics convention in which compact letter references identify diagram components by linking image and explanatory text.",
        "interpretation_excluded": "the article's explicit example is a related mechanics manuscript, so exact mark readings on Met 55.121.11 remain unassigned",
    },
]


COMPARE = [
    {
        "axis_id": "K01",
        "axis": "HYDRAULIC_NETWORK",
        "al_jazari": "source-identified water-raising machine with water, shafts, gears, ladles, and irrigation discharge",
        "q13": "catalogued pools, tubes, connected structures, and figures",
        "verdict": "STRONG_SYSTEM_ARCHITECTURE_MATCH",
        "consequence": "technical hydraulic rendering is historically plausible",
    },
    {
        "axis_id": "K02",
        "axis": "AGENT_FIGURE_IN_SYSTEM",
        "al_jazari": "donkey is structurally connected to the mechanism",
        "q13": "humanlike figures occur in and beside connected structures",
        "verdict": "PARTIAL_MATCH",
        "consequence": "an embedded figure need not be a diagram component name or personified material",
    },
    {
        "axis_id": "K03",
        "axis": "REPEATED_PARALLEL_COMPONENTS",
        "al_jazari": "reverse shows four repeated lifting bays under a shared drive",
        "q13": "repeated figure/pool/component arrays occur across q13",
        "verdict": "ARCHITECTURE_MATCH",
        "consequence": "array positions may be device stages or repeated installations",
    },
    {
        "axis_id": "K04",
        "axis": "COMPACT_COMPONENT_INDEX_MARKS",
        "al_jazari": "many isolated compact marks lie beside machine components; related scholarship documents letter-to-prose component keys",
        "q13": "graphical labels are multi-sign strings and almost all f80r/f82r ownership is proximity-only",
        "verdict": "MECHANISM_PLAUSIBLE_TARGET_BRIDGE_ABSENT",
        "consequence": "diagram labels could in principle be references rather than object names",
    },
    {
        "axis_id": "K05",
        "axis": "LABEL_KEY_REUSE_IN_EXPLANATORY_PROSE",
        "al_jazari": "component-key convention explicitly links compact diagram marks to explanatory text in the mechanics tradition",
        "q13": "GDT187 exact PAGE_HOST reuse covers 57/215 label occurrences in same-page prose and is not globally unusual; max-ten p=.2963",
        "verdict": "VOYNICH_PREDICTION_NOT_SUPPORTED",
        "consequence": "no q13 diagram-to-prose key dictionary is recovered",
    },
    {
        "axis_id": "K06",
        "axis": "EXACT_TOPOLOGY_OR_SOURCE_DESCENT",
        "al_jazari": "explicit gears, shafts, ladles, and animal drive",
        "q13": "no securely identified gears, drive train, ladles, or irrigation outlets",
        "verdict": "NO_EXACT_HOMOLOG",
        "consequence": "no direct al-Jazari source claim",
    },
    {
        "axis_id": "K07",
        "axis": "THERAPEUTIC_CONTENT",
        "al_jazari": "engineering treatise, not bath medicine",
        "q13": "therapeutic balneology remains the leading content theory",
        "verdict": "NO_CONTENT_MATCH",
        "consequence": "hydraulic mechanics is a rendering comparator only",
    },
]


COUNTER = [
    {"counterexample_id": "C01", "blocked_claim": "Q13_LABELS_ARE_ALJAZARI_STYLE_KEYS", "evidence": "GDT187 finds sparse but nonexceptional same-page exact-host label/prose reuse and max-ten p=.2963."},
    {"counterexample_id": "C02", "blocked_claim": "Q13_DEPICTS_A_WATER_RAISING_MACHINE", "evidence": "No q13 component is securely identified as a gear, shaft, ladle, animal drive, or irrigation outlet."},
    {"counterexample_id": "C03", "blocked_claim": "NEARBY_Q13_STRINGS_NAME_COMPONENTS", "evidence": "22/23 f80r/f82r text-linked rows are proximity-only; only f82r.10 has connected-component evidence."},
    {"counterexample_id": "C04", "blocked_claim": "HYDRAULIC_SIMILARITY_CONFIRMS_ENGINEERING_CONTENT", "evidence": "GDT210's therapeutic bath comparator remains closer in figure/pool ecology, while al-Jazari is closer only in explicit mechanism rendering."},
]


def main() -> None:
    tsv("gdt214_aljazari_source_manifest.tsv", SOURCES)
    tsv("gdt214_hydraulic_component_observations.tsv", OBS)
    tsv("gdt214_component_key_comparison.tsv", COMPARE)
    tsv("gdt214_counterexamples.tsv", COUNTER)
    result = {
        "experiment": "GDT214_HYDRAULIC_COMPONENT_KEY_COMPARATOR",
        "status": "HYDRAULIC_COMPONENT_KEY_FORMAT_HISTORICALLY_ATTESTED_VOYNICH_CROSS_REFERENCE_PREDICTION_UNSUPPORTED",
        "decision": "RENDERING_ARCHITECTURE_LEAD_WITHOUT_KEY_DICTIONARY",
        "counts": {
            "sources": len(SOURCES),
            "direct_visual_observations": 4,
            "source_interpretation_rows": 2,
            "comparison_axes": len(COMPARE),
            "counterexamples": len(COUNTER),
        },
        "gdt187": {
            "label_groups": 215,
            "same_page_prose_exact_host_reuse": 57,
            "paragraph_opening_exact_host_reuse": 22,
            "max_ten_p": 0.2963,
            "key_dictionary_supported": False,
        },
        "interpretation": {
            "supported": "Compact diagram component references and explanatory prose coexist in medieval hydraulic/mechanical manuscript culture.",
            "exploratory_q13_model": "Some q13 graphical strings could be a reference or component register rather than lexical object names.",
            "falsifier": "The existing same-page label/prose test does not recover an exceptional exact key dictionary.",
            "not_supported": ["al-Jazari source descent", "water-raising-machine identification", "component meaning", "word", "language", "plaintext", "translation"],
        },
        "f84": {"accessed": False, "input": False, "output": False},
    }
    input_names = [
        "GDT187_KEYED_OMISSION_TEST_REPORT.md",
        "gdt187_result.json",
        "run_gdt214_hydraulic_component_key_comparator.py",
    ]
    output_names = [
        "gdt214_aljazari_source_manifest.tsv",
        "gdt214_hydraulic_component_observations.tsv",
        "gdt214_component_key_comparison.tsv",
        "gdt214_counterexamples.tsv",
    ]
    doc_names = [
        "GDT214_HYDRAULIC_COMPONENT_KEY_COMPARATOR_METHOD.md",
        "GDT214_HYDRAULIC_COMPONENT_KEY_SOURCE_AUDIT.md",
        "GDT214_HYDRAULIC_COMPONENT_KEY_COMPARATOR_REPORT.md",
    ]
    result["inputs_sha256"] = {n: sha(ROOT / n) for n in input_names}
    result["outputs_sha256"] = {n: sha(ROOT / n) for n in output_names}
    result["documents_sha256"] = {n: sha(ROOT / n) for n in doc_names}
    result["validator_sha256"] = sha(ROOT / "validate_gdt214_hydraulic_component_key_comparator.py")
    canonical = json.dumps(result, sort_keys=True, separators=(",", ":"))
    result["content_sha256"] = hashlib.sha256(canonical.encode()).hexdigest()
    (ROOT / "gdt214_result.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
