#!/usr/bin/env python3
"""Build the GDT181 abductive hybrid-compiler theory artifacts."""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent

METHOD = ROOT / "GDT181_HYBRID_TECHNICAL_COMPILER_THEORY_METHOD.md"
REPORT = ROOT / "GDT181_HYBRID_TECHNICAL_COMPILER_THEORY_REPORT.md"

QUALITY = ROOT / "gdt179_quality_decoder.tsv"
STEPS = ROOT / "gdt180_f77_process_steps.tsv"
TRANSITIONS = ROOT / "gdt180_f77_transition_translation.tsv"

INPUTS = [
    ROOT / "gdt003_nested_result.json",
    ROOT / "gdt159_result.json",
    ROOT / "gdt160_result.json",
    ROOT / "gdt161_result.json",
    ROOT / "gdt162_result.json",
    ROOT / "gdt168_result.json",
    ROOT / "gdt175_result.json",
    ROOT / "gdt177_result.json",
    ROOT / "gdt178_result.json",
    ROOT / "gdt179_result.json",
    ROOT / "gdt180_result.json",
    QUALITY,
    STEPS,
    TRANSITIONS,
    METHOD,
    ROOT / "GDT051_REVISED_HYBRID_REGISTER_COMPILER_REPORT.md",
    ROOT / "GDT083_HPR_LAYER_LOCALIZATION_SYNTHESIS_REPORT.md",
    ROOT / "GDT155_MEDIEVAL_ABBREVIATION_UNBLIND_REPORT.md",
    ROOT / "GDT157_LEARNED_ABBREVIATION_CAUSAL_REPORT.md",
]

EVIDENCE = ROOT / "gdt181_evidence_matrix.tsv"
MODELS = ROOT / "gdt181_model_comparison.tsv"
LEXICON = ROOT / "gdt181_provisional_translation_lexicon.tsv"
PARSES = ROOT / "gdt181_worked_parses.tsv"
PREDICTIONS = ROOT / "gdt181_predictions.tsv"
COUNTER = ROOT / "gdt181_counterexamples.tsv"
GRAMMAR = ROOT / "gdt181_generative_grammar.json"
RESULT = ROOT / "gdt181_result.json"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical(obj: object) -> bytes:
    return (json.dumps(obj, sort_keys=True, indent=2) + "\n").encode()


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: list[dict[str, object]]) -> None:
    assert rows
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def evidence_rows() -> list[dict[str, object]]:
    return [
        {"id":"E01","layer":"SOURCE","finding":"Manual separator states carry reproducible hierarchy; cleaner fragment boundaries are excluded.","grade":"CONFIRMED_STRUCTURAL","supports":"HYBRID,NOTATION","constrains":"VISIBLE_GROUP_IS_NOT_ASSUMED_WORD","source":"VOYNICH_ACTIVE_STATE.md"},
        {"id":"E02","layer":"RECORD","finding":"Physical lines carry a rising coordinate and reset at the next line.","grade":"CONFIRMED_STRUCTURAL","supports":"HYBRID,NOTATION","constrains":"LINE_IS_RECORD_OR_UTTERANCE_LIKE_NOT_SENTENCE_PROOF","source":"VOYNICH_ACTIVE_STATE.md"},
        {"id":"E03","layer":"CONTENT","finding":"Literal inventories have held page-scale coherence and adjacency structure.","grade":"CONFIRMED_STRUCTURAL","supports":"HYBRID,NATURAL_LANGUAGE,NOTATION","constrains":"PAGE_CONDITIONED_INVENTORY","source":"VOYNICH_ACTIVE_STATE.md"},
        {"id":"E04","layer":"ALGEBRA","finding":"Nested folio-held operation discovery gains AP over fixed string baselines, but precision is 0.000909 and the named q/right subgroup loses badly.","grade":"LIMITED_LOCAL_COMPOSITION","supports":"HYBRID","constrains":"NO_GENERAL_MORPHOLOGY_OR_Q_DY_MEANING","source":"GDT003_NESTED_HELDOUT_REPORT.md"},
        {"id":"E05","layer":"ABBREVIATION","finding":"Readable medieval diplomatic abbreviation produces rectangles, edge asymmetry, record effects, and recurring stripped hosts.","grade":"POSITIVE_CONTROL","supports":"HYBRID,NATURAL_LANGUAGE","constrains":"RECTANGLES_ARE_NOT_SEMANTIC_PROOF","source":"GDT155_MEDIEVAL_ABBREVIATION_UNBLIND_REPORT.md"},
        {"id":"E06","layer":"ALGEBRA","finding":"No historical diplomatic comparator reproduces the conjunction of Voynich operation scale, compatibility density, and left dominance.","grade":"RESIDUAL_SUPPORTED","supports":"HYBRID,NOTATION","constrains":"ABBREVIATION_ALONE_INSUFFICIENT","source":"GDT159_DIPLOMATIC_SURFACE_ALGEBRA_REPORT.md"},
        {"id":"E07","layer":"ALGEBRA","finding":"Specific LEFT×RIGHT incidence exceeds degree/frequency nulls, but similar normalized excess also occurs in historical corpora.","grade":"SUPPORTED_NONUNIQUE","supports":"HYBRID,NOTATION","constrains":"NOT_UNIQUE_LANGUAGE_OR_CIPHER_SIGNAL","source":"GDT160_COMPATIBILITY_PAIRING_NULL_REPORT.md"},
        {"id":"E08","layer":"ALGEBRA","finding":"The excess does not collapse into a small stable latent operation inventory.","grade":"NEGATIVE_CONSTRAINT","supports":"HYBRID","constrains":"NO_SMALL_FACTORIAL_MORPHEME_SYSTEM","source":"GDT161_LATENT_OPERATION_CLASS_REPORT.md"},
        {"id":"E09","layer":"COMPILER","finding":"The best explicit structural generator is line-reset FIELD chaining with wrappers, PAGE_HOST, RIGHT_FAMILY, DY checkpoints, and probabilistic B3 close.","grade":"LEADING_ABDUCTIVE_ARCHITECTURE","supports":"HYBRID","constrains":"FIELD_NAMES_ARE_FORMAL","source":"GDT051_REVISED_HYBRID_REGISTER_COMPILER_REPORT.md"},
        {"id":"E10","layer":"CONTENT","finding":"PAGE_HOST improves internal page vocabulary representation, while compiler state also clusters by page and external transfer fails.","grade":"LOCALIZED_BUT_UNGROUNDED","supports":"HYBRID","constrains":"PAGE_HOST_NOT_CONFIRMED_LEXEME","source":"GDT083_HPR_LAYER_LOCALIZATION_SYNTHESIS_REPORT.md"},
        {"id":"E11","layer":"CONTENT","finding":"Short hosts are identity-bearing and internally structured, not a pure arbitrary codebook.","grade":"INTERESTING_STRUCTURAL","supports":"HYBRID","constrains":"IDENTITY_MATTERS_WITHOUT_SEMANTIC_GLOSS","source":"GDT162_PAGE_HOST_CODEBOOK_REPORT.md"},
        {"id":"E12","layer":"CALIBRATION","finding":"Negative host-context diagnostics fail even on a true synthetic lexical codebook.","grade":"INSTRUMENT_LIMIT","supports":"HYBRID,NATURAL_LANGUAGE,NOTATION","constrains":"HOST_NEGATIVES_DO_NOT_EXCLUDE_SPARSE_LEXICALITY","source":"GDT168_SYNTHETIC_ARCHITECTURE_CALIBRATION_REPORT.md"},
        {"id":"E13","layer":"CONTEXT","finding":"Recurrent hosts have heterogeneous folio-conditioned next-partner instability in all powered registers.","grade":"MIXED_OR_UNRESOLVED","supports":"HYBRID","constrains":"NO_GLOBAL_NEXT_HOST_DICTIONARY","source":"GDT175_RECURRENCE_PARTNER_INSTABILITY_REPORT.md"},
        {"id":"E14","layer":"SEMANTICS","finding":"Readable-recipe position/length roles fail every independent Q20 source-native prediction.","grade":"NEGATIVE_CONSTRAINT","supports":"NONE","constrains":"NO_Q20_INGREDIENT_TOOL_INSTRUCTION_GLOSSES","source":"GDT177_Q20_ROLE_SCHEMA_VALIDATION_REPORT.md"},
        {"id":"E15","layer":"SEMANTICS","finding":"The complete human-nominated referent atlas does not support exact or transformed PAGE_HOST content addresses.","grade":"NEGATIVE_CONSTRAINT","supports":"NONE","constrains":"NO_GLOBAL_PAGE_HOST_DICTIONARY","source":"GDT178_REFERENT_DISTRIBUTIONAL_HOST_REPORT.md"},
        {"id":"E16","layer":"LOCAL_SEMANTICS","finding":"Two f57 registers reconstruct all eight source-frozen Hot/Moist/Cold/Dry positions with local two-bit rules.","grade":"PROVISIONAL_POSTHOC_PAGE_LOCAL","supports":"HYBRID,NOTATION","constrains":"NO_GLOBAL_OT_OK_Y_GLOSS","source":"GDT179_F57_PAGE_TRANSLATION_REPORT.md"},
        {"id":"E17","layer":"LOCAL_SEMANTICS","finding":"The f77 six-state sequence makes four element-incidence changes and one nonemitting repeated-state hold.","grade":"PROVISIONAL_POSTHOC_PAGE_LOCAL","supports":"HYBRID,NOTATION","constrains":"NO_NAMED_PROCESS_OR_MATERIAL","source":"GDT180_F77_PROCESS_TRANSLATION_REPORT.md"},
    ]


def model_rows() -> list[dict[str, object]]:
    axes = [
        ("MEDIEVAL_ABBREVIATION_BEHAVIOR", 2, 0, 2),
        ("LINE_FIELD_COMPILER", 1, 2, 2),
        ("PAGE_CONDITIONED_INVENTORY", 2, 2, 2),
        ("BROAD_LEFT_RIGHT_INCIDENCE", 0, 2, 2),
        ("STABLE_RECORD_CLOSURE", 1, 2, 2),
        ("LOCAL_DIAGRAM_STATE_CODE", 0, 2, 2),
        ("STATE_WITH_WHOLE_FORM_DIVERSITY", 0, 2, 2),
        ("CURRIER_REGISTER_RENDERING", 2, 2, 2),
        ("SIMPLE_LANGUAGE_CIPHER_FAILURES", 0, 2, 2),
        ("HOST_CONTEXT_NONTRANSFER_WITH_IDENTITY", 1, 2, 2),
    ]
    rows: list[dict[str, object]] = []
    for axis, natural, notation, hybrid in axes:
        rows.append({"axis":axis,"COMPRESSED_NATURAL_LANGUAGE":natural,"PURE_TECHNICAL_NOTATION":notation,"HYBRID_TECHNICAL_COMPILER":hybrid,"scale":"0_POOR_1_PARTIAL_2_GOOD"})
    rows.append({"axis":"TOTAL","COMPRESSED_NATURAL_LANGUAGE":sum(x[1] for x in axes),"PURE_TECHNICAL_NOTATION":sum(x[2] for x in axes),"HYBRID_TECHNICAL_COMPILER":sum(x[3] for x in axes),"scale":"TRANSPARENT_ABDUCTIVE_SUM_NOT_PROBABILITY"})
    return rows


def lexicon_rows() -> list[dict[str, object]]:
    return [
        {"entry":"PAGE_HOST","scope":"MANUSCRIPT_FORMAL","provisional_role":"OPAQUE_PAGE_OR_REGISTER_CONDITIONED_CONTENT_ADDRESS","english_gloss":"UNASSIGNED","confidence":"STRUCTURAL_ONLY","export_rule":"NEVER_GLOSS_WITHOUT_INDEPENDENT_REFERENT"},
        {"entry":"WRAPPER","scope":"MANUSCRIPT_FORMAL","provisional_role":"HOST_LICENSED_ENTRY_OR_RENDERING_COORDINATE","english_gloss":"UNASSIGNED","confidence":"STRUCTURAL_ONLY","export_rule":"NOT_A_POS_OR_MORPHEME"},
        {"entry":"RIGHT_FAMILY","scope":"MANUSCRIPT_FORMAL","provisional_role":"REGISTER_CONDITIONED_RIGHT_EDGE_RENDERER","english_gloss":"UNASSIGNED","confidence":"STRUCTURAL_ONLY","export_rule":"NOT_A_SUFFIX_MEANING"},
        {"entry":"DY_CLASS","scope":"MANUSCRIPT_FORMAL","provisional_role":"FIELD_CHECKPOINT_OR_CLOSURE_CLASS","english_gloss":"UNASSIGNED","confidence":"STRUCTURAL_ONLY","export_rule":"NOT_TRANSLATED_AS_END_OR_RESOLVE"},
        {"entry":"B3_CLASS","scope":"MANUSCRIPT_FORMAL","provisional_role":"PROBABILISTIC_PHYSICAL_RECORD_CLOSER","english_gloss":"UNASSIGNED","confidence":"STRUCTURAL_ONLY","export_rule":"NOT_PUNCTUATION_OR_WORD"},
        {"entry":"Q_OUTER","scope":"MANUSCRIPT_FORMAL","provisional_role":"LEFT_EDGE_ROUTING_OPERATION","english_gloss":"UNASSIGNED","confidence":"LIMITED_LOCAL_COMPOSITION","export_rule":"NO_SEMANTIC_OR_PHONOLOGICAL_VALUE"},
        {"entry":"N1_STARTS_OT_BIT","scope":"F57_N1_AND_F77_SEGMENTS_ONLY","provisional_role":"FIRE_INCIDENCE_COORDINATE","english_gloss":"UNASSIGNED","confidence":"PROVISIONAL_POSTHOC","export_rule":"DO_NOT_EXPORT_TO_PROSE_OR_OTHER_PAGES"},
        {"entry":"D1_HAS_OK_BIT","scope":"F57_D1_ONLY","provisional_role":"WATER_INCIDENCE_COORDINATE","english_gloss":"UNASSIGNED","confidence":"PROVISIONAL_POSTHOC","export_rule":"DO_NOT_EXPORT_TO_PROSE_OR_OTHER_PAGES"},
        {"entry":"LOCAL_TERMINAL_Y_BIT","scope":"F57_SHORT_LABELS_AND_F77_SEGMENTS_ONLY","provisional_role":"MOIST_OR_DRY_PARTITION_COORDINATE","english_gloss":"UNASSIGNED","confidence":"PROVISIONAL_POSTHOC","export_rule":"DO_NOT_EXPORT_TO_GLOBAL_DY_OR_WORD_FINAL_Y"},
        {"entry":"N1_F77_STATE_00","scope":"F57_N1_AND_F77_LOCAL_SCHEMA","provisional_role":"COLD_POSITION","english_gloss":"COLD_POSITION","confidence":"PROVISIONAL_PAGE_ROLE","export_rule":"POSITION_GLOSS_NOT_SOURCE_WORD"},
        {"entry":"N1_F77_STATE_01","scope":"F57_N1_AND_F77_LOCAL_SCHEMA","provisional_role":"MOIST_POSITION","english_gloss":"MOIST_POSITION","confidence":"PROVISIONAL_PAGE_ROLE","export_rule":"POSITION_GLOSS_NOT_SOURCE_WORD"},
        {"entry":"N1_F77_STATE_10","scope":"F57_N1_AND_F77_LOCAL_SCHEMA","provisional_role":"HOT_POSITION","english_gloss":"HOT_POSITION","confidence":"PROVISIONAL_PAGE_ROLE","export_rule":"POSITION_GLOSS_NOT_SOURCE_WORD"},
        {"entry":"N1_F77_STATE_11","scope":"F57_N1_AND_F77_LOCAL_SCHEMA","provisional_role":"DRY_POSITION","english_gloss":"DRY_POSITION","confidence":"PROVISIONAL_PAGE_ROLE","export_rule":"POSITION_GLOSS_NOT_SOURCE_WORD"},
        {"entry":"D1_STATE_00","scope":"F57_D1_LOCAL_SCHEMA","provisional_role":"HOT_POSITION","english_gloss":"HOT_POSITION","confidence":"PROVISIONAL_PAGE_ROLE","export_rule":"POSITION_GLOSS_NOT_SOURCE_WORD"},
        {"entry":"D1_STATE_01","scope":"F57_D1_LOCAL_SCHEMA","provisional_role":"DRY_POSITION","english_gloss":"DRY_POSITION","confidence":"PROVISIONAL_PAGE_ROLE","export_rule":"POSITION_GLOSS_NOT_SOURCE_WORD"},
        {"entry":"D1_STATE_10","scope":"F57_D1_LOCAL_SCHEMA","provisional_role":"COLD_POSITION","english_gloss":"COLD_POSITION","confidence":"PROVISIONAL_PAGE_ROLE","export_rule":"POSITION_GLOSS_NOT_SOURCE_WORD"},
        {"entry":"D1_STATE_11","scope":"F57_D1_LOCAL_SCHEMA","provisional_role":"MOIST_POSITION","english_gloss":"MOIST_POSITION","confidence":"PROVISIONAL_PAGE_ROLE","export_rule":"POSITION_GLOSS_NOT_SOURCE_WORD"},
    ]


def worked_parses() -> list[dict[str, object]]:
    qualities = read_tsv(QUALITY)
    steps = read_tsv(STEPS)
    transitions = read_tsv(TRANSITIONS)
    assert len(qualities) == 8 and len(steps) == 6 and len(transitions) == 5
    rows: list[dict[str, object]] = []
    for row in qualities:
        predicate = "STARTS_OT" if row["register"] == "N1" else "HAS_OK_COMPONENT"
        rows.append({
            "parse_id": f"F57_{row['locus']}", "folio":"f57v", "locus":row["locus"],
            "surface_ZL3b":row["ZL3b"], "alternate_readings":f"IT2a={row['IT2a']};RF1b={row['RF1b']}",
            "formal_parse":f"{predicate}={row['selector_bit']} + TERMINAL_Y={row['terminal_y_bit']} + OPAQUE_RESIDUAL",
            "local_bits":row["selector_bit"] + row["terminal_y_bit"],
            "provisional_translation":row["decoded_quality"] + "_POSITION",
            "translation_level":"SCHEMA_POSITION_NOT_WORD", "status":row["evidence_status"],
        })
    for row in steps:
        rows.append({
            "parse_id":f"F77_{row['locus']}", "folio":"f77r", "locus":row["locus"],
            "surface_ZL3b":row["ZL3b_surface"], "alternate_readings":f"IT2a={row['IT2a_surface']};RF1b={row['RF1b_surface']}",
            "formal_parse":f"STARTS_OT={row['local_state_bits'][0]} + TERMINAL_Y={row['local_state_bits'][1]} + OPAQUE_RESIDUAL",
            "local_bits":row["local_state_bits"],
            "provisional_translation":row["provisional_quality_state"] + "_STATE",
            "translation_level":"PROCESS_STATE_NOT_WORD", "status":row["confidence"],
        })
    for row in transitions:
        rows.append({
            "parse_id":f"F77_BOUNDARY_{row['boundary']}", "folio":"f77r", "locus":row["opening"],
            "surface_ZL3b":"VISIBLE_OPENING", "alternate_readings":"NOT_TEXTUAL",
            "formal_parse":f"{row['left_state']}->{row['right_state']};EMISSION={row['visible_emission']}",
            "local_bits":"NA", "provisional_translation":row["provisional_transition_class"] + "_TRANSITION",
            "translation_level":"DIAGRAM_RELATION_NOT_WORD", "status":"PROVISIONAL_POSTHOC",
        })
    return rows


def prediction_rows() -> list[dict[str, object]]:
    return [
        {"id":"P1","scope":"FRESH_SCHEMA_EQUIVALENT_DIAGRAM","prediction":"A source-owned four-quality register will use a two-coordinate four-state partition and place the same second coordinate on Moist/Dry.","novel":"YES","failure":"A comparable independently owned register requires exceptions or another partition.","status":"UNTESTED"},
        {"id":"P2","scope":"FRESH_SEGMENTED_PROCESS","prediction":"Outputs occur at state changes and not at an unchanged adjacent-state hold.","novel":"YES","failure":"A securely owned comparable process emits at a same-state boundary or fails to emit at a changed boundary.","status":"UNTESTED"},
        {"id":"P3","scope":"F77_LEGEND_OR_HOMOLOG","prediction":"The five boundaries resolve to EARTH,FIRE,NONE,AIR,WATER in physical order.","novel":"YES","failure":"A readable source-owned legend fixes another order.","status":"UNTESTED"},
        {"id":"P4","scope":"F57_R2_HOMOLOG","prediction":"The lone stable changing column is a repeated binary property coordinate, but a homolog must distinguish thermal class from page half and grammatical gender.","novel":"YES","failure":"A homolog shows the column is nonrepeatable or unrelated to any stable binary row property.","status":"UNTESTED"},
        {"id":"P5","scope":"READABLE_TECHNICAL_HOMOLOG","prediction":"Compiler-layer variation can change with record position/register while the same externally identified content address remains recoverable.","novel":"YES","failure":"Only raw whole forms preserve referents and compiler stripping destroys every content match.","status":"UNTESTED"},
        {"id":"P6","scope":"NEW_INDEPENDENT_REFERENT","prediction":"If PAGE_HOST contains address information, a repeated singular referent will preserve PAGE_HOST or a small licensed address family more than compiler-only fields.","novel":"YES","failure":"A powered independently owned referent panel again favors raw/compiler or matched nulls.","status":"UNTESTED"},
        {"id":"P7","scope":"GLOBAL_TRANSLATION_STRATEGY","prediction":"A one-layer phoneme substitution will not recover stable plaintext until compiler coordinates are modeled or removed.","novel":"YES","failure":"A frozen grapheme-to-phoneme map alone yields stable held-folio phonotactics and recurrent lexical values.","status":"UNTESTED"},
    ]


def counter_rows() -> list[dict[str, object]]:
    return [
        {"id":"C1","counterexample":"The named q-plus-right-edge GDT003 subgroup loses to string baselines.","effect_on_theory":"Q and DY remain formal operations without a semantic gloss."},
        {"id":"C2","counterexample":"Exact PAGE_HOST and transformed-host external referent atlases fail on the complete human-nominated panel.","effect_on_theory":"No PAGE_HOST dictionary is published."},
        {"id":"C3","counterexample":"No stable compact LEFT/RIGHT operation-class inventory predicts unseen compatibility.","effect_on_theory":"The compiler is distributed/host-licensed rather than a tiny factorial morphology."},
        {"id":"C4","counterexample":"The Q20 recipe-role projection fails all independent tests.","effect_on_theory":"Q20 remains structurally record-like but semantically untranslated."},
        {"id":"C5","counterexample":"The f57 decoder is post-hoc and proximity-owned on one folio.","effect_on_theory":"Its state meanings stay local and provisional."},
        {"id":"C6","counterexample":"A cached f77 puff order agrees with the proposed transition classes at zero of four.","effect_on_theory":"Visible outputs are not named element labels."},
        {"id":"C7","counterexample":"The f67v1 universal emission transfer failed.","effect_on_theory":"State-change emission is not manuscript-wide."},
        {"id":"C8","counterexample":"Global nonsemantic source models remain stronger than semantic decoders.","effect_on_theory":"The model is explanatory, not a compression win or decipherment proof."},
        {"id":"C9","counterexample":"No confirmed phonetic alphabet, language, plaintext clause, or whole-word translation exists.","effect_on_theory":"Underlying content type remains unresolved."},
    ]


def grammar_object() -> dict[str, object]:
    return {
        "theory":"PAGE_CONDITIONED_HYBRID_TECHNICAL_COMPILER",
        "status":"LEADING_ABDUCTIVE_GENERATOR_NOT_CONFIRMED_DECIPHERMENT",
        "productions":{
            "DOCUMENT":["PAGE+"],
            "PAGE":["PAGE_PROFILE ADDRESS_INVENTORY RECORD+"],
            "RECORD":["ENTRY_STATE? FIELD (CHECKPOINT FIELD)* CLOSE?"],
            "FIELD":["WRAPPER? INNER_D? POSITION_FRAME? PAGE_HOST RIGHT_FAMILY?"],
            "CHECKPOINT":["DY_CLASS"],
            "CLOSE":["B3_CLASS"],
            "DIAGRAM_LABEL":["LOCAL_SELECTOR? LOCAL_ADDRESS LOCAL_STATE_EDGE?"],
        },
        "latent_layers":[
            {"layer":"PAGE_PROFILE","function":"licenses inventory and renderer ecology","semantic_status":"UNASSIGNED"},
            {"layer":"PAGE_HOST","function":"opaque content/address candidate","semantic_status":"UNASSIGNED"},
            {"layer":"COMPILER","function":"record, placement, register and edge realization","semantic_status":"FORMAL_ONLY"},
            {"layer":"LOCAL_DIAGRAM_STATE","function":"finite state coordinate where external schema licenses it","semantic_status":"PROVISIONAL_F57_F77_ONLY"},
        ],
        "local_state_decoder":{
            "scope":["f57v:N1","f57v:D1","f77r:top_segments"],
            "states_by_register":{
                "N1_and_f77":{"00":"COLD_POSITION","01":"MOIST_POSITION","10":"HOT_POSITION","11":"DRY_POSITION"},
                "D1":{"00":"HOT_POSITION","01":"DRY_POSITION","10":"COLD_POSITION","11":"MOIST_POSITION"}
            },
            "N1_and_f77_bits":["STARTS_OT","TERMINAL_Y"],
            "D1_bits":["HAS_OK_COMPONENT","TERMINAL_Y"],
            "surface_predicates_are_morpheme_boundaries":False,
        },
        "translation_policy":{
            "opaque_address_rendering":"ADDR[folio:register:position]",
            "local_position_glosses_are_words":False,
            "global_export_requires":"FROZEN_INDEPENDENT_SCHEMA_TRANSFER",
            "f84r_target":False,
        },
    }


def main() -> None:
    for path in INPUTS:
        assert path.exists(), path
    g179 = json.loads((ROOT / "gdt179_result.json").read_text())
    g180 = json.loads((ROOT / "gdt180_result.json").read_text())
    assert g179["counts"]["quality_labels"] == 8
    assert g179["counts"]["internal_decoder_matches"] == 8
    assert g180["counts"]["segments"] == 6 and g180["counts"]["relation_matches"] == 5
    assert not g179["f84r_accessed"] and not g180["f84r_accessed"]

    e = evidence_rows()
    m = model_rows()
    l = lexicon_rows()
    p = worked_parses()
    pred = prediction_rows()
    c = counter_rows()
    grammar = grammar_object()

    write_tsv(EVIDENCE, e)
    write_tsv(MODELS, m)
    write_tsv(LEXICON, l)
    write_tsv(PARSES, p)
    write_tsv(PREDICTIONS, pred)
    write_tsv(COUNTER, c)
    GRAMMAR.write_bytes(canonical(grammar))

    totals = m[-1]
    scores = {
        "COMPRESSED_NATURAL_LANGUAGE": int(totals["COMPRESSED_NATURAL_LANGUAGE"]),
        "PURE_TECHNICAL_NOTATION": int(totals["PURE_TECHNICAL_NOTATION"]),
        "HYBRID_TECHNICAL_COMPILER": int(totals["HYBRID_TECHNICAL_COMPILER"]),
    }
    assert max(scores, key=scores.get) == "HYBRID_TECHNICAL_COMPILER"

    outputs = [EVIDENCE, MODELS, LEXICON, PARSES, PREDICTIONS, COUNTER, GRAMMAR]
    result = {
        "experiment":"GDT181_HYBRID_TECHNICAL_COMPILER_THEORY",
        "status":"LEADING_HYBRID_TECHNICAL_COMPILER_WITH_LOCAL_F57_F77_STATE_DECODING",
        "leading_theory":"PAGE_CONDITIONED_HYBRID_TECHNICAL_COMPILER",
        "abductive_scores":scores,
        "translation_coverage":{
            "folios_with_provisional_semantic_scaffold":2,
            "f57_quality_positions":8,
            "f77_process_states":6,
            "f77_transition_relations":5,
            "confirmed_source_words":0,
            "confirmed_plaintext_clauses":0,
        },
        "counts":{
            "evidence_rows":len(e), "model_axes":len(m)-1, "lexicon_entries":len(l),
            "worked_parse_rows":len(p), "predictions":len(pred), "counterexamples":len(c),
        },
        "inputs":{str(path.relative_to(ROOT)):sha(path) for path in INPUTS},
        "outputs":{path.name:sha(path) for path in outputs},
        "documents":{path.name:sha(path) for path in [METHOD, REPORT]},
        "implementation":sha(Path(__file__).resolve()),
        "f84r_accessed":False,
        "f84r_prediction_created":False,
        "claim_ceiling":"The leading abductive surface generator is a page-conditioned hybrid technical compiler. It supports provisional local f57/f77 quality-state and transition readings, while every source word, prose clause, language, phonology, and global PAGE_HOST dictionary remains unconfirmed.",
    }
    RESULT.write_bytes(canonical(result))
    print(json.dumps({"status":result["status"], **result["translation_coverage"]}, sort_keys=True))


if __name__ == "__main__":
    main()
