#!/usr/bin/env python3
"""Materialize the GDT215 evidence-bounded q13 generative theory."""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write(name: str, rows: list[dict[str, object]]) -> None:
    with (ROOT / name).open("w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        w.writeheader()
        w.writerows(rows)


EVIDENCE = [
    {"evidence_id":"E01","source":"GDT202","observation":"Anonymous page-conditioned compiler survives while all active local semantic values are withdrawn.","supports":"HYBRID_COMPILER","opposes":"DIRECT_WORD_DICTIONARY","strength":"STRONG_FORMAL","independence":"INTERNAL_FORMAL"},
    {"evidence_id":"E02","source":"GDT189-194","observation":"Static alphabetic, codebook, short expansion, consonantal and homophonic language channels lose matched anonymous controls and are unstable.","supports":"NONLITERAL_OR_ABBREVIATED_PAYLOAD","opposes":"SIMPLE_NATURAL_LANGUAGE_CIPHER","strength":"STRONG_NEGATIVE","independence":"INTERNAL_FORMAL"},
    {"evidence_id":"E03","source":"GDT210","observation":"Readable De balneis images are the closest page-genre comparator for figures, pools, watercourses, tiers, caves and structures.","supports":"THERAPEUTIC_BALNEOLOGICAL_CONTENT_PRIOR","opposes":"PURE_ALCHEMICAL_PERSONIFICATION","strength":"PROVISIONAL_EXTERNAL","independence":"EXTERNAL_READABLE"},
    {"evidence_id":"E04","source":"GDT211","observation":"Readable bath records use identity/indication plus optional location, hydraulics, procedure and outcome; q13 opening-host effect is confounded by generic Herbal-B openings.","supports":"BATH_RECORD_SCHEMA_COMPATIBLE","opposes":"LOCALIZED_IDENTITY_FIELD","strength":"WEAK_COMPATIBILITY","independence":"EXTERNAL_SCHEMA_PLUS_INTERNAL"},
    {"evidence_id":"E05","source":"GDT212","observation":"Readable bath illustrations weakly expose setting/hydraulics but fail to expose indication, procedure or outcome.","supports":"VISUAL_SETTING_HYDRAULIC_LAYER","opposes":"FIGURE_GESTURE_TRANSLATION","strength":"WEAK_EXTERNAL","independence":"EXTERNAL_READABLE"},
    {"evidence_id":"E06","source":"GDT213","observation":"A readable medical codex combines abstract connected systems, component labels and longer practical text, with variable label/prose layouts across pages.","supports":"MIXED_DIAGRAM_RECORD_FORMAT","opposes":"HOMOGENEOUS_TEXT_ROLE","strength":"PROVISIONAL_EXTERNAL","independence":"EXTERNAL_READABLE"},
    {"evidence_id":"E07","source":"GDT214","observation":"A readable hydraulic folio uses repeated machine components and compact nearby marks; component-key architecture is historically plausible.","supports":"DIAGRAM_REFERENCE_REGISTER","opposes":"EVERY_LABEL_IS_OBJECT_NAME","strength":"PROVISIONAL_EXTERNAL","independence":"EXTERNAL_READABLE"},
    {"evidence_id":"E08","source":"GDT187","observation":"Exact PAGE_HOST reuse covers 57/215 label occurrences in same-page prose but is not globally unusual, max-ten p=.2963.","supports":"REGISTER_LOCAL_ECOLOGY","opposes":"EXACT_LABEL_TO_PROSE_KEY_DICTIONARY","strength":"STRONG_NEGATIVE","independence":"INTERNAL_HELD_NULL"},
    {"evidence_id":"E09","source":"LRG001-007","observation":"Labels have a transferable construction profile concentrated at group-initial family and prose edges, but no exact q/D1 or A1 semantic mechanism localizes it.","supports":"DISTINCT_LABEL_REGISTER","opposes":"SIMPLE_DROPPED_PREFIX_KEY","strength":"STRONG_FORMAL","independence":"INTERNAL_HELD"},
    {"evidence_id":"E10","source":"GDT169","observation":"Repeated external-referent pairs do not preserve exact PAGE_HOST or full tuple robustly; locally owned queries have zero exact paired-host matches.","supports":"CONTEXTUAL_OR_DISTRIBUTED_CONTENT","opposes":"ONE_REFERENT_ONE_FIXED_HOST","strength":"STRONG_NEGATIVE","independence":"EXTERNAL_ANNOTATION_PLUS_INTERNAL"},
    {"evidence_id":"E11","source":"GDT165-167","observation":"Opaque exact-host next and distributional context do not transfer globally or within register despite local alignment structure.","supports":"PAGE_OR_RECORD_REBINDING","opposes":"STABLE_GLOBAL_LEXICAL_CODEBOOK","strength":"STRONG_NEGATIVE","independence":"INTERNAL_HELD"},
    {"evidence_id":"E12","source":"GDT168-174","observation":"Synthetic calibration shows host-context negatives cannot distinguish a sparse lexical codebook from distributed coding, while full surface parsing misses true components.","supports":"INSTRUMENT_LIMITED_HYBRID","opposes":"OVERINTERPRET_NEGATIVE_HOST_TESTS","strength":"STRONG_CALIBRATION","independence":"SYNTHETIC_ORACLE"},
]


SCHEMA = [
    {"layer_order":"1","latent_layer":"PAGE_PROFILE","generator":"page/register/hand-conditioned inventory and rendering policy","candidate_document_role":"SITE_OR_SYSTEM_CONTEXT","confidence":"FORMAL_CONFIRMED_ROLE_SPECULATIVE","observed_anchor":"page-conditioned root/host inventory","prohibited_gloss":"place name; bath name"},
    {"layer_order":"2","latent_layer":"VISUAL_SYSTEM","generator":"pools/enclosures/ducts/figures/repeated units and their physical relations","candidate_document_role":"SETTING_OR_HYDRAULIC_MODEL","confidence":"VISUAL_CONFIRMED_CONTENT_PROVISIONAL","observed_anchor":"human q13 catalogue and GDT210 comparators","prohibited_gloss":"water; patient; apparatus substance"},
    {"layer_order":"3","latent_layer":"GRAPHICAL_LABEL_REGISTER","generator":"short diagram-local source groups in a label-associated construction register","candidate_document_role":"COMPONENT_STATE_OR_CASE_REFERENCE","confidence":"FORMAL_REGISTER_CONFIRMED_ROLE_SPECULATIVE","observed_anchor":"LRG001-007; one connected-component locus f82r.10","prohibited_gloss":"object name; body part; person name"},
    {"layer_order":"4","latent_layer":"RECORD_OPEN","generator":"paragraph/record entry construction under line reset","candidate_document_role":"IDENTITY_OR_SETTING_HEADER","confidence":"WEAK_GENERIC_CONFOUND","observed_anchor":"GDT211 opening recurrence deficit","prohibited_gloss":"specific site or indication"},
    {"layer_order":"5","latent_layer":"RECORD_BODY","generator":"ENTRY_STATE? FIELD (DY_CLASS FIELD)* B3_CLASS?","candidate_document_role":"INDICATION_PROCEDURE_CAUTION_OR_DESCRIPTION","confidence":"FORMAL_CONFIRMED_ROLE_UNLOCALIZED","observed_anchor":"GDT202 HPR2 compiler; De balneis schema","prohibited_gloss":"disease; treatment; instruction"},
    {"layer_order":"6","latent_layer":"FIELD","generator":"WRAPPER? INNER_D? POSITION_FRAME? PAGE_HOST RIGHT_FAMILY?","candidate_document_role":"ONE_DISTRIBUTED_RECORD_VALUE","confidence":"FORMAL_CONFIRMED_CONTENT_UNKNOWN","observed_anchor":"HPR2 compiler","prohibited_gloss":"word; POS; morpheme"},
    {"layer_order":"7","latent_layer":"PAGE_HOST","generator":"opaque page-conditioned address/value component","candidate_document_role":"CONTENT_BEARING_ADDRESS_OR_CODE","confidence":"BEST_FORMAL_CONTENT_CANDIDATE_NOT_DICTIONARY","observed_anchor":"compiler stripping and calibration","prohibited_gloss":"lexical word; translated stem"},
    {"layer_order":"8","latent_layer":"RENDERER","generator":"WRAPPER/RIGHT_FAMILY/DY/B3 plus line/field position","candidate_document_role":"record grammar, closure and display state","confidence":"FORMAL_CONFIRMED_SEMANTICS_UNKNOWN","observed_anchor":"line-reset, field and boundary experiments","prohibited_gloss":"case; tense; number; suffix meaning"},
]


PREDICTIONS = [
    {"prediction_id":"P01","prediction":"A new provenance-clean repeated hydraulic component with singular text ownership should preserve a full record/label construction more often than exact PAGE_HOST alone across independent folios.","required_new_evidence":"at least two contrasting components repeated on an untouched physical folio plus discovery folios","existing_data_status":"NOT_TESTABLE_CURRENT_OWNERSHIP","failure_effect":"weakens component/state reference layer only","used_to_construct_theory":"NO"},
    {"prediction_id":"P02","prediction":"On a new readable q13-like bath/hydraulic homolog, local component captions should align with a distinct explanatory-text field or reference mechanism, while longer therapeutic payload need not be visually recoverable.","required_new_evidence":"source-readable diagram with diplomatic labels, prose and singular ownership","existing_data_status":"EXTERNAL_ACQUISITION_REQUIRED","failure_effect":"weakens historical mechanism prior","used_to_construct_theory":"NO"},
    {"prediction_id":"P03","prediction":"A newly acquired independently identified repeated bath/site/installation should preserve record-opening plus setting/hydraulic tuple structure across folios even when figure count and exact host differ.","required_new_evidence":"repeated external referent with held-folio replication and source-bound ownership","existing_data_status":"GDT169_CURRENT_PANEL_NEGATIVE_BUT_INSTRUMENT_LIMITED","failure_effect":"weakens bath-record compiler theory","used_to_construct_theory":"NO"},
    {"prediction_id":"P04","prediction":"If q13 prose contains indication/procedure content, direct visual labels or gestures will recover it poorly, but source-readable setting/hydraulic distinctions should concentrate near a subset of record fields.","required_new_evidence":"new human annotation with singular hydraulic relation and field-local text join","existing_data_status":"FIRST_HALF_SUPPORTED_BY_GDT212_SECOND_UNTESTABLE","failure_effect":"shifts content away from balneological records","used_to_construct_theory":"PARTLY"},
    {"prediction_id":"P05","prediction":"A true bilingual/keyed legend would collapse the page-conditioned host ambiguity and produce stable full-tuple correspondences; without it, more internal string mining will remain nonidentifying.","required_new_evidence":"external readable value or uniquely keyed homolog","existing_data_status":"NO_KEY_AVAILABLE","failure_effect":"requires new nonlexical architecture","used_to_construct_theory":"NO"},
]


COUNTER = [
    {"counterexample_id":"C01","awkward_fact":"No active Voynich word, label value or semantic state survives GDT202.","theory_response":"Theory remains a generative document schema, not a translation.","unresolved":1},
    {"counterexample_id":"C02","awkward_fact":"GDT187 fails the exact diagram-label to prose key prediction.","theory_response":"Any reference relation must be distributed/nonexact or absent; exact dictionary is rejected.","unresolved":1},
    {"counterexample_id":"C03","awkward_fact":"GDT169 finds no replicated exact host or tuple invariance for existing external-referent pairs.","theory_response":"Current annotations/parse may lack the right units; fixed lexical-code interpretation is weakened.","unresolved":1},
    {"counterexample_id":"C04","awkward_fact":"Only one f80r/f82r text-linked row has connected-component evidence; 22 are proximity-only.","theory_response":"Graphical label roles cannot be assigned per locus from current panel.","unresolved":1},
    {"counterexample_id":"C05","awkward_fact":"Long page-spanning q13 ducts exceed the closest De balneis image topology.","theory_response":"Retain a technical/hydraulic rendering layer beyond literal bath illustration.","unresolved":1},
    {"counterexample_id":"C06","awkward_fact":"Historical language mappings and fixed host-to-word dictionaries fail matched anonymous controls.","theory_response":"Payload must be heavily abbreviated, distributed, contextual, nonlinguistic, or some combination.","unresolved":1},
]


def main() -> None:
    write("gdt215_theory_evidence_matrix.tsv", EVIDENCE)
    write("gdt215_latent_record_schema.tsv", SCHEMA)
    write("gdt215_prediction_registry.tsv", PREDICTIONS)
    write("gdt215_counterexamples.tsv", COUNTER)
    result = {
        "experiment":"GDT215_Q13_GENERATIVE_THEORY_SYNTHESIS",
        "status":"HYBRID_BALNEOLOGICAL_RECORD_COMPILER_LEADING_SEMANTIC_KEY_ZERO",
        "leading_theory":"HYBRID_MEDICAL_RECORD_COMPILER_WITH_DIAGRAM_REFERENCE_REGISTER",
        "theory_class_ranking":[
            {"rank":1,"class":"HYBRID_LANGUAGE_ABBREVIATION_NOTATION","assessment":"LEADING"},
            {"rank":2,"class":"SEMANTIC_OR_TECHNICAL_NOTATION","assessment":"LIVE_SECONDARY"},
            {"rank":3,"class":"COMPRESSED_ABBREVIATED_NATURAL_LANGUAGE","assessment":"INSUFFICIENT_ALONE"},
        ],
        "counts":{"evidence_rows":len(EVIDENCE),"schema_layers":len(SCHEMA),"novel_predictions":len(PREDICTIONS),"counterexamples":len(COUNTER)},
        "semantic_coverage":{"confirmed_words":0,"plaintext_clauses":0,"licensed_semantic_states":0,"provisional_document_domain":"THERAPEUTIC_BALNEOLOGICAL_WITH_TECHNICAL_HYDRAULIC_RENDERING"},
        "claim":"The best current generator is a page-conditioned record compiler carrying opaque content addresses, embedded in a mixed medical diagram/practical-record document whose leading content prior is therapeutic balneology and whose graphical strings may form a separate component/state reference register.",
        "hard_limits":["no exact label-prose key dictionary","no stable one-referent-one-host mapping","no localized indication/procedure/outcome field","no exact readable topology homolog","no word, sound, language, plaintext or translation"],
        "next_route":"Acquire a provenance-clean repeated hydraulic/setting referent with singular ownership and held-folio replication, or a readable q13-like diagram with diplomatic labels and prose; do not mine another internal host gloss.",
        "f84":{"accessed":False,"input":False,"output":False},
    }
    input_names=[
        "GDT202_HYBRID_THEORY_RECONCILIATION_REPORT.md",
        "GDT210_THERAPEUTIC_BALNEOLOGICAL_COMPARATOR_REPORT.md",
        "GDT211_BALNEOLOGICAL_RECORD_SCHEMA_REPORT.md",
        "GDT212_DE_BALNEIS_VISUAL_TEXT_GROUNDING_REPORT.md",
        "GDT213_READABLE_MEDICAL_DIAGRAM_COMPARATOR_REPORT.md",
        "GDT214_HYDRAULIC_COMPONENT_KEY_COMPARATOR_REPORT.md",
        "GDT187_KEYED_OMISSION_TEST_REPORT.md",
        "run_gdt215_q13_generative_theory.py",
    ]
    output_names=["gdt215_theory_evidence_matrix.tsv","gdt215_latent_record_schema.tsv","gdt215_prediction_registry.tsv","gdt215_counterexamples.tsv"]
    doc_names=["GDT215_Q13_GENERATIVE_THEORY_METHOD.md","GDT215_Q13_GENERATIVE_THEORY_REPORT.md"]
    result["inputs_sha256"]={n:sha(ROOT/n) for n in input_names}
    result["outputs_sha256"]={n:sha(ROOT/n) for n in output_names}
    result["documents_sha256"]={n:sha(ROOT/n) for n in doc_names}
    result["validator_sha256"]=sha(ROOT/"validate_gdt215_q13_generative_theory.py")
    canonical=json.dumps(result,sort_keys=True,separators=(",",":"))
    result["content_sha256"]=hashlib.sha256(canonical.encode()).hexdigest()
    (ROOT/"gdt215_result.json").write_text(json.dumps(result,indent=2,sort_keys=True)+"\n",encoding="utf-8")


if __name__=="__main__":
    main()
