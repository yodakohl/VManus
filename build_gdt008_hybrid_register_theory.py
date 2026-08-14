#!/usr/bin/env python3
"""Build the GDT008 YOLO abductive hybrid-register theory artifacts."""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent
METHOD = ROOT / "GDT008_HYBRID_REGISTER_THEORY_METHOD.md"
REPORT = ROOT / "GDT008_HYBRID_REGISTER_THEORY_REPORT.md"
EVIDENCE = ROOT / "gdt008_evidence_map.tsv"
COMPARISON = ROOT / "gdt008_theory_comparison.tsv"
ROLES = ROOT / "gdt008_provisional_roles.tsv"
PARSES = ROOT / "gdt008_representative_parses.tsv"
PREDICTIONS = ROOT / "gdt008_novel_predictions.tsv"
MODEL = ROOT / "gdt008_hybrid_register_model.json"
RESULT = ROOT / "gdt008_result.json"

INPUTS = [
    ROOT / "experiments/semantic_assumptions/grammar/CONFIRMED_GRAMMAR.md",
    ROOT / "GDT001_CURRENT_SUMMARY.md",
    ROOT / "gdt001_current_summary.json",
    ROOT / "GDT002_MORPHOLOGY_FALSIFICATION_REPORT.md",
    ROOT / "gdt002_morphology_results.json",
    ROOT / "gdt002_morphology_occurrences.tsv",
    ROOT / "GDT003_PARADIGM_PREDICTION_REPORT.md",
    ROOT / "gdt003_results.json",
    ROOT / "GDT003_NESTED_HELDOUT_REPORT.md",
    ROOT / "gdt003_nested_result.json",
    ROOT / "GDT003_STRUCTURAL_FINGERPRINT_COMPARATOR_REPORT.md",
    ROOT / "gdt003_structural_fingerprint_result.json",
    ROOT / "Q20OB001_OPEN_BODY_REPORT.md",
    ROOT / "q20ob001_result.json",
]


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_sha(value: object) -> str:
    payload = json.dumps(value, sort_keys=True, ensure_ascii=True, separators=(",", ":"))
    return hashlib.sha256(payload.encode()).hexdigest()


def read_json(name: str) -> dict:
    return json.loads((ROOT / name).read_text(encoding="utf-8"))


def read_tsv(name: str) -> list[dict[str, str]]:
    with (ROOT / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: list[dict[str, object]]) -> None:
    fields = list(rows[0])
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    morphology = read_json("gdt002_morphology_results.json")
    gdt003 = read_json("gdt003_results.json")
    nested = read_json("gdt003_nested_result.json")
    source_summary = read_json("gdt001_current_summary.json")
    open_body = read_json("q20ob001_result.json")
    fp = read_json("gdt003_structural_fingerprint_result.json")
    occurrences = read_tsv("gdt002_morphology_occurrences.tsv")

    assert not any(row["locus"].startswith("f84r") for row in occurrences)
    assert morphology["status"] == "FORMAL_REUSE_SUPPORTED_SEMANTIC_SLOT_SYSTEM_NOT_SUPPORTED"
    assert gdt003["status"] == "NOT DISTINGUISHABLE FROM STRING STATISTICS"
    assert nested["status"] == "LIMITED/LOCAL COMPOSITION ONLY"
    assert source_summary["decision"] == "NO_DECIPHERMENT_CANDIDATE_FREEZE"
    assert open_body["status"] == "OPEN_BODY_DEPENDENCE_NOT_ABOVE_MATCHED_CONTROLS"

    exact_daldy = [
        row for row in occurrences
        if row["module"] == "DAL"
        and row["ZL3b_token"] == row["IT2a_token"] == row["RF1b_token"] == "daldy"
    ]
    assert len(exact_daldy) == 13

    evidence = [
        {"evidence_id": "E01", "observation": "Physical lines carry a rising local coordinate that resets at every new line.", "weight": 3, "compressed_language_fit": 0.5, "notation_fit": 1.0, "hybrid_fit": 1.0, "source": "CONFIRMED_GRAMMAR.md", "theory_use": "LINE is the primary record/utterance serialization unit."},
        {"evidence_id": "E02", "observation": "Literal roots have a qualified order-free page inventory, while adjacent identities retain local assembly information.", "weight": 2, "compressed_language_fit": 1.0, "notation_fit": 1.0, "hybrid_fit": 1.0, "source": "CONFIRMED_GRAMMAR.md", "theory_use": "A page selects a domain lexicon; line schemas order selected fields."},
        {"evidence_id": "E03", "observation": "Directional root-pair information transfers across Currier A/B beyond unordered pair affinity (+0.01725 bit/edge).", "weight": 3, "compressed_language_fit": 1.0, "notation_fit": 0.5, "hybrid_fit": 1.0, "source": "CONFIRMED_GRAMMAR.md", "theory_use": "Currier profiles are renderers of a shared abstract construction system."},
        {"evidence_id": "E04", "observation": "AR, OL, DAL, DAR, SY and DY occur freely and bound; ar|ol and dar|ol have manual split/join analogues.", "weight": 3, "compressed_language_fit": 1.0, "notation_fit": 0.5, "hybrid_fit": 1.0, "source": "gdt002_morphology_results.json", "theory_use": "Units are reusable macros/abbreviated stems; boundaries serialize fields rather than lexical words."},
        {"evidence_id": "E05", "observation": "Labels contain 13.519 candidate hits per 100 symbols versus 10.586 in prose and 2.19x the multi-module-group rate.", "weight": 2, "compressed_language_fit": 0.5, "notation_fit": 1.0, "hybrid_fit": 1.0, "source": "gdt002_morphology_results.json", "theory_use": "Labels are compact record projections; prose expands the same repertoire."},
        {"evidence_id": "E06", "observation": "q-prepend and DY-append form the clearest compatible edge pair; q survives every nested training fold.", "weight": 2, "compressed_language_fit": 1.0, "notation_fit": 1.0, "hybrid_fit": 1.0, "source": "gdt003_results.json;gdt003_nested_result.json", "theory_use": "Left scope and right closure are separate realization dimensions."},
        {"evidence_id": "E07", "observation": f"daldy recurs as {len(exact_daldy)} all-reading-exact physical groups across prose/nonprose, while f75v contains a second reading-sensitive identical label.", "weight": 2, "compressed_language_fit": 0.5, "notation_fit": 1.0, "hybrid_fit": 1.0, "source": "gdt002_morphology_occurrences.tsv", "theory_use": "DAL+DY is a stock field value/formula rather than an object name."},
        {"evidence_id": "E08", "observation": "The global source winner is a metadata-aware online context mixer at 2.960465 bits/source symbol and is not language-specific.", "weight": 3, "compressed_language_fit": 0.0, "notation_fit": 1.0, "hybrid_fit": 1.0, "source": "GDT001_CURRENT_SUMMARY.md", "theory_use": "Realization is locally templatic and register-conditioned rather than a single substitution/plain-language stream."},
        {"evidence_id": "E09", "observation": "Thousands of language/cipher/notation searches yield no stable mapping; language-side candidates lose decisively to the source generator.", "weight": 3, "compressed_language_fit": 0.0, "notation_fit": 1.0, "hybrid_fit": 1.0, "source": "GDT001_CURRENT_SUMMARY.md", "theory_use": "The observed layer is not direct plaintext and contains a manuscript-specific conventionalization layer."},
        {"evidence_id": "E10", "observation": "AROL occurs in apparatus-associated and plant-label contexts; visual-role scans do not recover a stable object meaning.", "weight": 2, "compressed_language_fit": 0.5, "notation_fit": 1.0, "hybrid_fit": 1.0, "source": "gdt002_morphology_results.json", "theory_use": "AROL is a relational/record construction, not a noun meaning flow or plant."},
        {"evidence_id": "E11", "observation": "che+VALUE is highly productive and AII+N tends to precede AI+N within lines.", "weight": 2, "compressed_language_fit": 1.0, "notation_fit": 1.0, "hybrid_fit": 1.0, "source": "CONFIRMED_GRAMMAR.md", "theory_use": "Explicit field carriers and ordered parameter grades coexist with stem material."},
        {"evidence_id": "E12", "observation": "Held directional adjacency survives metadata exclusion and exceeds the fixed Timm copy/modify generator.", "weight": 3, "compressed_language_fit": 1.0, "notation_fit": 0.5, "hybrid_fit": 1.0, "source": "CONFIRMED_GRAMMAR.md", "theory_use": "The system has genuine constructional sequencing, not only local imitation or a bag of codes."},
        {"evidence_id": "E13", "observation": "Q20 positional OPEN does not improve BODY prediction in the registered direct-cache model.", "weight": 1, "compressed_language_fit": 0.5, "notation_fit": 1.0, "hybrid_fit": 1.0, "source": "q20ob001_result.json", "theory_use": "Records need not be heading-plus-content; fields can be locally generated from page schema without lexical copying."},
    ]

    penalties = {"COMPRESSED_ABBREVIATED_NATURAL_LANGUAGE": 2.0, "SEMANTIC_TECHNICAL_NOTATION": 2.5, "HYBRID_REGISTER": 4.0}
    fit_fields = {
        "COMPRESSED_ABBREVIATED_NATURAL_LANGUAGE": "compressed_language_fit",
        "SEMANTIC_TECHNICAL_NOTATION": "notation_fit",
        "HYBRID_REGISTER": "hybrid_fit",
    }
    descriptions = {
        "COMPRESSED_ABBREVIATED_NATURAL_LANGUAGE": "A heavily abbreviated natural language whose apparent words are stem-plus-affix complexes.",
        "SEMANTIC_TECHNICAL_NOTATION": "A purpose-built technical code in which roots and shells are field symbols rather than linguistic material.",
        "HYBRID_REGISTER": "Natural-language-derived stems conventionalized inside a line-bounded technical field notation with aggressive abbreviation.",
    }
    comparisons = []
    for architecture, field in fit_fields.items():
        raw = sum(float(row["weight"]) * float(row[field]) for row in evidence)
        comparisons.append({
            "architecture": architecture,
            "description": descriptions[architecture],
            "weighted_fit": raw,
            "complexity_penalty": penalties[architecture],
            "net_abductive_score": raw - penalties[architecture],
            "score_status": "POSTHOC_THEORY_SELECTION_AID_NOT_PROBABILITY",
        })
    comparisons.sort(key=lambda row: (-float(row["net_abductive_score"]), str(row["architecture"])))
    for rank, row in enumerate(comparisons, 1):
        row["rank"] = rank
        row["decision"] = "SELECTED_LEADING_THEORY" if rank == 1 else "RETAINED_AS_RIVAL"
    assert comparisons[0]["architecture"] == "HYBRID_REGISTER"

    roles = [
        {"unit": "PAGE_ROOT_INVENTORY", "slot": "DOMAIN", "provisional_role": "local technical lexicon", "speculative_value": "materials, entities, operations, conditions, identifiers selected for one page", "confidence": "STRONG_ARCHITECTURAL", "ambiguity": "No individual root meaning is assigned."},
        {"unit": "t / d / s (bare line-entry)", "slot": "ENTRY_STATE", "provisional_role": "record initialization/continuation mode", "speculative_value": "t = initialize/new entry; d and s = two continuation modes", "confidence": "PROVISIONAL_FUNCTION", "ambiguity": "Paragraph state is editorially reconstructed; d/s contrast is not semantically identified."},
        {"unit": "q-", "slot": "OUTER_SCOPE", "provisional_role": "dependent/current-frame wrapper", "speculative_value": "apply or read the enclosed form under the active record frame", "confidence": "PROVISIONAL_FUNCTION", "ambiguity": "Could instead be an orthographic/phonological onset class; no English word is implied."},
        {"unit": "o- / ot-", "slot": "LOCAL_FRAME", "provisional_role": "local view or parameter frame", "speculative_value": "unmarked versus extended/marked frame", "confidence": "WEAK_PROVISIONAL", "ambiguity": "o→ot is recovered in only one nested fold and competes with alternative parses."},
        {"unit": "d- / s- (bound)", "slot": "LOCAL_MODE", "provisional_role": "contrastive operation/state selector", "speculative_value": "d = active/process instance; s = state/reference instance", "confidence": "PROVISIONAL_FUNCTION", "ambiguity": "Both also occur freely; semantic polarity is invented to make the theory explicit."},
        {"unit": "ch- / sh- / che-", "slot": "CARRIER_FAMILY", "provisional_role": "field introducer/allomorphic carrier", "speculative_value": "che introduces an explicit value field; ch/sh select related carrier modes", "confidence": "CHE_STRONG_OTHERS_PROVISIONAL", "ambiguity": "No copula, preposition, or POS is assigned."},
        {"unit": "AR", "slot": "CORE_RELATION", "provisional_role": "relational/process anchor", "speculative_value": "relation, operation, or linkage class rather than a pictured-object name", "confidence": "PROVISIONAL_FUNCTION", "ambiguity": "AR is extremely frequent and segmentation is nonunique."},
        {"unit": "OL", "slot": "CORE_REFERENCE", "provisional_role": "entity/material/reference anchor", "speculative_value": "the referenced item or domain value in a compound", "confidence": "PROVISIONAL_FUNCTION", "ambiguity": "OL is not water: it occurs across registers and object ecologies."},
        {"unit": "AI / AII + N", "slot": "PARAMETER_GRADE", "provisional_role": "ordered grade/extent encoding", "speculative_value": "more-explicit/higher grade tends to precede reduced/lower grade", "confidence": "PROVISIONAL_FUNCTION", "ambiguity": "Not a number, count, or measurement value."},
        {"unit": "TE / TEE", "slot": "INTERNAL_GRADE", "provisional_role": "graphic/abbreviation grade inside a frame", "speculative_value": "short versus expanded internal realization", "confidence": "WEAK", "ambiguity": "Only one stable free occurrence each; TE nests inside TEE."},
        {"unit": "DY", "slot": "RIGHT_CLOSURE", "provisional_role": "default/completed result-state closure", "speculative_value": "record value is closed, standard, or resolved", "confidence": "STRONG_POSITION_PROVISIONAL_VALUE", "ambiguity": "The functional value is speculative; DY may bundle smaller operations."},
        {"unit": "DAL / DAR", "slot": "RIGHT_STATE", "provisional_role": "contrastive result/argument settings", "speculative_value": "two alternative settings within one field, not necessarily left/right or source/destination", "confidence": "PROVISIONAL_FUNCTION", "ambiguity": "DAR is also parsable as d+AR; DAL/DAR/DY operations are often order-dependent."},
        {"unit": "SY", "slot": "RIGHT_QUALIFIER", "provisional_role": "secondary status/exception qualifier", "speculative_value": "marked secondary state", "confidence": "PROVISIONAL_FUNCTION", "ambiguity": "Sparse relative to DY and no visual partition survives control."},
        {"unit": "SOURCE SPACE / JOIN", "slot": "BOUNDARY_RENDERER", "provisional_role": "field serialization choice", "speculative_value": "expand adjacent modules as separate groups or contract them into one label/form", "confidence": "STRONG_ARCHITECTURAL", "ambiguity": "Spaces are hierarchical but not assumed linguistic word boundaries."},
        {"unit": "CURRIER A / B", "slot": "REGISTER_RENDERER", "provisional_role": "two realization profiles over a shared construction graph", "speculative_value": "cataloguing/descriptive versus procedural/expanded technical register", "confidence": "PROVISIONAL_FUNCTION", "ambiguity": "Not two languages, dialects, authors, or topics by proof."},
    ]

    parses = [
        {"locus": "f103r.12", "surface": "otedy", "parse": "[O:local-frame][TE:internal-grade][DY:closure]", "reading_state": "ALL_THREE_EXACT", "interpretive_gloss": "unmarked framed value, default/closed state", "status": "REPRESENTATIVE_PROVISIONAL_PARSE", "counterparse": "[OT:marked-frame][E:core][DY]"},
        {"locus": "f103r.15", "surface": "qotedy", "parse": "[Q:outer-scope][O][TE][DY]", "reading_state": "ALL_THREE_EXACT", "interpretive_gloss": "same framed value under dependent/current scope", "status": "REPRESENTATIVE_PROVISIONAL_PARSE", "counterparse": "[Q][OT][E][DY]"},
        {"locus": "f103r.16", "surface": "oteedy", "parse": "[O][TEE:expanded-grade][DY]", "reading_state": "ALL_THREE_EXACT", "interpretive_gloss": "expanded internal grade with the same closure", "status": "REPRESENTATIVE_PROVISIONAL_PARSE", "counterparse": "[OT][EE][DY]"},
        {"locus": "f103r.45", "surface": "qoteedy", "parse": "[Q][O][TEE][DY]", "reading_state": "ALL_THREE_EXACT", "interpretive_gloss": "scoped expanded-grade counterpart", "status": "REPRESENTATIVE_PROVISIONAL_PARSE", "counterparse": "[Q][OT][EE][DY]"},
        {"locus": "f82r.35", "surface": "darol", "parse": "[D:active-mode][AR:relation][OL:reference]", "reading_state": "ALL_THREE_EXACT", "interpretive_gloss": "active relational-reference record", "status": "VISUALLY_FLOW_ADJACENT_BUT_NOT_FLOW_WORD", "counterparse": "[DAR:right-state][OL]"},
        {"locus": "f83r.51", "surface": "darolsy", "parse": "[D][AR][OL][SY:secondary-status]", "reading_state": "ALL_THREE_EXACT", "interpretive_gloss": "active relational-reference with marked secondary status", "status": "PROVISIONAL_LABEL_PARSE", "counterparse": "[DAR][OL][SY]"},
        {"locus": "f83r.50", "surface": "saroldal", "parse": "[S:state-mode][AR][OL][DAL:result-setting]", "reading_state": "IT2a_RF1b;ZL3b=sasoldal", "interpretive_gloss": "state/reference counterpart with alternate result setting", "status": "READING_SENSITIVE_PROVISIONAL_PARSE", "counterparse": "ZL3b [S][AS][OL][DAL]"},
        {"locus": "f75v.32", "surface": "daldy", "parse": "[DAL:result-setting][DY:closure]", "reading_state": "ALL_THREE_EXACT", "interpretive_gloss": "stock setting-plus-closure formula", "status": "REPEATED_LABEL_FORM_NOT_OBJECT_NAME", "counterparse": "[D][AL][DY]"},
        {"locus": "f75v.22", "surface": "daldy", "parse": "[DAL][DY]", "reading_state": "ZL3b_RF1b;IT2a=dal", "interpretive_gloss": "second stock-form occurrence with reading-sensitive closure", "status": "REPEATED_LABEL_READING_SENSITIVE", "counterparse": "IT2a [DAL]"},
        {"locus": "f99v.8", "surface": "arol", "parse": "[AR][OL]", "reading_state": "ALL_THREE_EXACT", "interpretive_gloss": "bare relational-reference compound", "status": "PLANT_LABEL_COUNTEREXAMPLE_TO_FLOW_MEANING", "counterparse": "opaque AROL remains possible"},
        {"locus": "f102v2.14", "surface": "sarol", "parse": "[S][AR][OL]", "reading_state": "ALL_THREE_EXACT", "interpretive_gloss": "state/reference rendering of the same compound", "status": "PLANT_LABEL_COUNTEREXAMPLE_TO_FLOW_MEANING", "counterparse": "[SAR][OL]"},
        {"locus": "f80v.41", "surface": "ar | ol / arol", "parse": "[AR] <BOUNDARY_RENDERER> [OL]", "reading_state": "MANUAL_SPLIT_JOIN_ANALOGY", "interpretive_gloss": "one latent compound with expanded or contracted serialization", "status": "BOUNDARY_VARIANT", "counterparse": "two collocated independent fields"},
        {"locus": "f100r.25", "surface": "cheol", "parse": "[CHE:explicit-value-carrier][OL:value]", "reading_state": "ALL_THREE_EXACT", "interpretive_gloss": "explicit reference/value field", "status": "CARRIER_PARSE", "counterparse": "opaque CHEOL remains possible"},
    ]

    predictions = [
        {"prediction_id": "P01", "target_scope": "SEALED_F84R", "prediction": "Candidate-module hits per 100 symbols will be at least 1.15x higher in labels than prose, and the label multi-module rate at least 1.5x the prose rate.", "measurement": "Reuse the frozen GDT002 candidate set and exact role census without tuning.", "failure_condition": "Either ratio falls below its threshold.", "status": "FROZEN_NOVEL_PREDICTION_UNOPENED"},
        {"prediction_id": "P02", "target_scope": "SEALED_F84R", "prediction": "At least one q-scoped/unscoped host pair will share a DY/DAL/DAR/SY terminal class, yielding a complete or 3-of-4 left-scope by right-state grid.", "measurement": "Strict all-reading groups only; no new operations may be invented.", "failure_condition": "No qualifying grid exists.", "status": "FROZEN_NOVEL_PREDICTION_UNOPENED"},
        {"prediction_id": "P03", "target_scope": "SEALED_F84R", "prediction": "Within repeated visual-label groups, shared right-state class will be more common than shared exact core expression.", "measurement": "Compare pairwise class agreement under the frozen inventory; ownership remains proximity-aware.", "failure_condition": "Exact-core agreement equals or exceeds right-state agreement.", "status": "FROZEN_NOVEL_PREDICTION_UNOPENED"},
        {"prediction_id": "P04", "target_scope": "SEALED_F84R", "prediction": "Line-initial entry carriers and q wrappers will be left-biased, whereas DY/DAL/DAR/SY-bearing forms will be right-biased within physical lines.", "measurement": "Predeclare first/last third and compare exact opportunities.", "failure_condition": "Both directional effects are absent or reversed.", "status": "FROZEN_NOVEL_PREDICTION_UNOPENED"},
        {"prediction_id": "P05", "target_scope": "NONHOLDOUT_BOUNDARY_AUDIT", "prediction": "Right-state modules detach across source spaces more often than q or bare entry carriers after matching host frequency and line position.", "measurement": "Source-native synchronized boundaries; no cleaner fragments.", "failure_condition": "Matched detachment odds are not larger for the right-state class.", "status": "FROZEN_NOVEL_PREDICTION_NOT_RUN"},
        {"prediction_id": "P06", "target_scope": "NONHOLDOUT_LINE_POSITION", "prediction": "Exact daldy is enriched as the final physical group relative to matched five-sign forms by at least 0.15 probability points.", "measurement": "Match page, Currier, layout kind, and line group count before comparison.", "failure_condition": "Adjusted enrichment is below +0.15.", "status": "FROZEN_NOVEL_PREDICTION_NOT_RUN"},
        {"prediction_id": "P07", "target_scope": "CROSS_CURRIER_TRANSFER", "prediction": "Collapsing register-specific carrier/internal-grade variants while preserving core and right-state order improves held cross-Currier adjacency by at least 0.005 bit/edge over literal identities.", "measurement": "Train on the opposite Currier stratum only; frozen collapse dictionary.", "failure_condition": "Gain is below +0.005 bit/edge.", "status": "FROZEN_NOVEL_PREDICTION_NOT_RUN"},
        {"prediction_id": "P08", "target_scope": "OPERATION_INTERACTION", "prediction": "Conditional on page and host, q is approximately independent of the choice DY/DAL/DAR/SY, while d-versus-s retains a measurable interaction with that choice.", "measurement": "Hierarchical exact/penalized interaction model; no semantic outcome.", "failure_condition": "q is more dependent than d/s or neither contrast is estimable.", "status": "FROZEN_NOVEL_PREDICTION_NOT_RUN"},
        {"prediction_id": "P09", "target_scope": "LABEL_PROSE_RENDERING", "prediction": "For the same ordered module tuple, labels favor JOIN and prose favor SPACE after matching section, page, and total ink length.", "measurement": "Manual boundaries only; tuple identity frozen before role comparison.", "failure_condition": "Role-conditioned join odds do not have the predicted direction.", "status": "FROZEN_NOVEL_PREDICTION_NOT_RUN"},
        {"prediction_id": "P10", "target_scope": "PAGE_REGISTER_DECOMPOSITION", "prediction": "Page identity predicts core inventory better than wrapper inventory, while Currier/line position predicts wrapper and right-state realization better than core identity.", "measurement": "Crossed held-page/held-Currier information decomposition.", "failure_condition": "The two predicted inequalities both fail.", "status": "FROZEN_NOVEL_PREDICTION_NOT_RUN"},
    ]

    model = {
        "schema": "GDT008_HYBRID_PROCEDURAL_REGISTER_MODEL_V1",
        "theory_id": "HPR1_HYBRID_PROCEDURAL_REGISTER",
        "status": "SELECTED_EXPLORATORY_WORLD_MODEL",
        "one_sentence_theory": "Voynichese is an abbreviation-rich technical register in which page-local natural-language-derived stems are serialized through line-bounded notation-like fields, scope/mode wrappers, state closures, and optional join/detach rendering.",
        "generator": {
            "MANUSCRIPT": "shared construction graph plus register-conditioned renderer",
            "PAGE": "choose DOMAIN and a coherent page-local CORE inventory",
            "PARAGRAPH": "choose INIT or CONTINUE discourse/record state",
            "LINE": "emit ENTRY_STATE then an ordered sequence of FIELD tuples; reset coordinate at newline",
            "FIELD": "OUTER_SCOPE? + LOCAL_MODE/CARRIER? + CORE+ + RIGHT_STATE/QUALIFIER? + CLOSURE?",
            "BOUNDARY": "render adjacent latent components as JOIN, manual SPACE, or detached completion according to register, role, and available width",
            "REGISTER": "Currier/section/hand/layout profiles alter surface probabilities without changing the shared construction graph",
        },
        "formal_template": "[OUTER_SCOPE] [LOCAL_MODE_OR_CARRIER] [SMALL_CORE+] [RIGHT_STATE_OR_QUALIFIER] [CLOSURE]",
        "latent_classes": {row["unit"]: {"slot": row["slot"], "provisional_role": row["provisional_role"], "speculative_value": row["speculative_value"]} for row in roles},
        "semantic_layer": "Cores may ultimately derive from technical lexemes; wrappers and closures are primarily conventional record functions. Exact lexical values remain unassigned.",
        "historical_plausibility": "A late-medieval practical compendium could mix abbreviated vernacular or learned stems, conventional carrier signs, compact tabular/caption fields, and expanded prose-like serializations. This is a document-practice analogy, not a source, region, or language identification.",
        "f84r_access": {"formal_payload_opened": False, "formal_payload_joined": False, "formal_payload_scored": False, "prediction_packet_frozen": True},
        "claim_ceiling": "Exploratory generative theory only; no confirmed language, sound, morpheme, POS, word meaning, plaintext, translation, author, date, or origin.",
    }

    write_tsv(EVIDENCE, evidence)
    write_tsv(COMPARISON, comparisons)
    write_tsv(ROLES, roles)
    write_tsv(PARSES, parses)
    write_tsv(PREDICTIONS, predictions)
    MODEL.write_text(json.dumps(model, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    selected = comparisons[0]
    report = f"""# GDT008 hybrid procedural-register theory

Status: **SELECTED EXPLORATORY WORLD MODEL — HPR-1**

## Best current overall theory

**Voynichese is an abbreviation-rich technical register: page-local,
natural-language-derived stems are inserted into line-bounded record fields,
then rendered with notation-like left scope/mode operators, right state and
closure codes, and optional joined or detached spelling.**

This is not ordinary continuous prose, but it is not a pure arbitrary code
either. Its cores can preserve lexical or mnemonic material while its visible
surface is dominated by a manuscript-specific field grammar. Labels are the
most contracted form of the register; paragraph lines are expanded
serializations of the same machinery.

The theory is called **HPR-1: Hybrid Procedural Register**. “Procedural” means
that lines serialize ordered technical fields; it does not assert that every
line is an imperative or recipe.

## Why this theory wins the abductive comparison

| rank | architecture | weighted fit | complexity penalty | net score | decision |
| ---: | --- | ---: | ---: | ---: | --- |
"""
    for row in comparisons:
        report += f"| {row['rank']} | {row['architecture']} | {float(row['weighted_fit']):.1f} | {float(row['complexity_penalty']):.1f} | {float(row['net_abductive_score']):.1f} | {row['decision']} |\n"
    report += """

The score is deliberately post-hoc and is not statistical evidence. Pure
compressed language explains free/bound reuse and directional adjacency, but
handles the line reset, repeated stock forms, metadata-sensitive surface, and
failure of every direct language decoder poorly. Pure notation explains those
features but handles split/join fluidity, pervasive free forms, and the shared
cross-Currier directional construction less naturally. HPR-1 pays extra
complexity for two layers, yet explains both sets with one renderer.

## Explicit generator

```text
MANUSCRIPT := shared construction graph + REGISTER_RENDERER
PAGE       := choose DOMAIN and page-local CORE inventory
PARAGRAPH  := choose INIT or CONTINUE state
LINE       := ENTRY_STATE FIELD+ ; reset coordinate at newline
FIELD      := OUTER_SCOPE? LOCAL/CARRIER? CORE+ RIGHT_STATE? CLOSURE?
SURFACE    := join or detach adjacent components under boundary renderer

OUTER_SCOPE  := q | empty
ENTRY_STATE  := t | d | s | expanded entry form
LOCAL        := d | s | o | ot | ch | sh | ...
CARRIER      := che | related ch/sh frames
CORE         := AR | OL | AI/AII grades | page-selected root
RIGHT_STATE  := DAL | DAR | SY | related terminal class
CLOSURE      := DY | Y | related terminal closure
```

The renderer is probabilistic and conditioned by Currier, page, line position,
layout kind, and neighboring fields. Therefore the context mixer can beat a
rigid morphology grammar without making the underlying fields unreal.

## Historical plausibility

HPR-1 requires no modern cryptographic machinery. A late-medieval practical
compiler could combine abbreviated vernacular or learned stems, conventional
carrier marks, compact tabular/caption fields, and expanded prose-like
serializations. A private technical register also explains why a competent
reader might recover whole field bundles while modern language models fail on
the visible layer. This is an analogy to manuscript practice—not an
identification of a source, region, language, or profession.

## Provisional functional dictionary

These are latent functions, not translations:

- **q-**: outer dependent/current-frame wrapper—roughly “interpret this form
  under the active record frame.”
- **t / d / s at entry**: initialize versus two continuation modes.
- **bound d- / s-**: active/process-like versus state/reference-like local
  mode. This polarity is deliberately speculative.
- **o- / ot-**: unmarked versus expanded local frame; weak because the parse
  competes with `o + TE`.
- **che-**: explicit value-field carrier. `ch/sh` are related carrier modes.
- **AR**: relational/process anchor; **OL**: entity/material/reference anchor.
  Thus AROL is a generic relation-to-reference construction, not “water.”
- **AI/AII+N**: ordered parameter grades, without assuming numbers.
- **TE/TEE**: short/expanded internal graphic grade, not a secure free core.
- **DAL/DAR**: contrastive result or argument settings.
- **SY**: secondary/exception status.
- **DY**: default/completed result-state closure.
- **source space/JOIN**: expansion versus contraction of adjacent fields.

## Representative parses

| locus | surface | provisional parse | abductive reading | caveat |
| --- | --- | --- | --- | --- |
"""
    for row in parses:
        report += f"| {row['locus']} | `{row['surface']}` | `{row['parse']}` | {row['interpretive_gloss']} | {row['counterparse']} |\n"
    report += f"""

The `otedy/qotedy` and `oteedy/qoteedy` grids are the cleanest illustration:
the same internal grade and closure survive addition of outer `q`. `darolsy`
and the reading-sensitive `saroldal` show a different local mode and terminal
state around shared AR+OL material. `ar | ol` versus `arol` makes the renderer
visible directly.

`daldy` is especially informative under HPR-1. It occurs in {len(exact_daldy)}
all-reading-exact physical groups and also appears twice among f75v's labels,
although one of those two is IT2a-sensitive. It behaves better as a stock
setting-plus-closure formula than as the name of two different figures. The
same form's prose recurrence is expected if labels are compressed record
fields rather than a separate vocabulary.

## What HPR-1 explains at once

1. **Free/bound reuse:** macros and abbreviated stems may occupy their own
   field or be contracted into a neighboring field.
2. **Split/join spellings:** visible spaces are renderer choices over a latent
   field sequence, not necessarily word boundaries.
3. **Right-edge DY:** a closure/status code naturally occurs across many
   otherwise unrelated cores and can also be written alone.
4. **Productive q+X:** scope is outside the local value and therefore combines
   with multiple right states.
5. **Line reset:** every line serializes one record/utterance from entry state
   toward values and closures, then starts a new record.
6. **Page coherence:** the page selects its technical core inventory.
7. **Currier effects with shared grammar:** Currier profiles change the
   renderer and favored carriers while preserving abstract field order.
8. **Dense labels:** captions suppress optional boundaries and carriers,
   yielding more multi-module groups and fewer standalone pieces.
9. **Extreme local compatibility:** reusable field values create many edit
   rectangles; renderer priors also make them look like generic string
   regularity, explaining GDT003's weak precision.
10. **Failed language/cipher mappings:** the surface is neither plaintext nor
    a stationary substitution. A decoder must infer page lexicon, register,
    record schema, and boundary rendering jointly.
11. **Failed simple visual meanings:** AROL-like structures encode relation or
    record function and can accompany apparatus, figures, and plants without
    naming any of them.
12. **Q20 OPEN failure:** an entry field need not lexically predict its body;
    both can be generated from a page schema and record state.

## Awkward observations

- The global nonsemantic context mixer still compresses better than every
  explicit semantic/language model. HPR-1 has not yet supplied a competitive
  complete encoder.
- The literal q plus DY/DAL/DAR subsystem is worse than strong string
  baselines in nested held-folio prediction. Its functional interpretation is
  therefore abductive, not independently predictive.
- Many edge operations are order-dependent, and TE/TEE segmentation is
  particularly ambiguous.
- Visual associations are weak and page-confounded; no core has a secure
  referent.
- Currier A/B may reflect more than rendering—different scribes, source
  strata, or generating processes remain possible.
- A purely synthetic templatic generator could imitate much of HPR-1. The
  cross-Currier directional relation rules out one fixed Timm generator, not
  all synthetic alternatives.

## Novel frozen predictions

Ten predictions are frozen in `gdt008_novel_predictions.tsv`. Four concern the
still-sealed f84r formal payload: increased label contraction, at least one
q-by-right-state partial grid, greater sharing of terminal class than exact
core among repeated labels, and opposing within-line biases for entry versus
closure classes. Six nonholdout predictions test boundary asymmetry, daldy
line position, register collapse, q versus d/s interactions, label/prose JOIN
choice, and page-versus-register information decomposition.

They are predictions of the constructed world model, not prerequisites for
allowing the theory to exist. None was used in the architecture score.

## Conclusion

HPR-1 is the strongest present generative explanation because it treats the
Voynich surface as a **technical register compiler**, not as ordinary words
and not as an arbitrary lookup code. Page-local stem material supplies domain
content; a shared field grammar supplies order; left operators scope or select
record mode; right modules encode state/closure; and the renderer decides how
much to join, detach, or abbreviate.

This pass deliberately chooses that theory. It is concrete enough to generate
forms and risky predictions, but its proposed functions remain exploratory.
f84r has not been opened.
"""
    REPORT.write_text(report, encoding="utf-8")

    outputs = [EVIDENCE, COMPARISON, ROLES, PARSES, PREDICTIONS, MODEL, REPORT]
    result = {
        "schema": "GDT008_HYBRID_REGISTER_THEORY_RESULT_V1",
        "status": "HPR1_SELECTED_EXPLORATORY_WORLD_MODEL",
        "leading_theory": model["theory_id"],
        "decision": selected,
        "architecture_count": len(comparisons),
        "evidence_dimensions": len(evidence),
        "provisional_roles": len(roles),
        "representative_parses": len(parses),
        "novel_predictions": len(predictions),
        "daldy_all_reading_exact_groups": len(exact_daldy),
        "prior_results_preserved": {
            "GDT002": morphology["status"],
            "GDT003": gdt003["status"],
            "GDT003_NESTED": nested["status"],
            "GDT003_FINGERPRINT": fp["status"],
            "GDT001": source_summary["decision"],
            "Q20_OPEN_BODY": open_body["status"],
        },
        "f84r": model["f84r_access"],
        "inputs": {str(path.relative_to(ROOT)): sha(path) for path in INPUTS},
        "implementation": {Path(__file__).name: sha(Path(__file__)), METHOD.name: sha(METHOD)},
        "outputs": {path.name: sha(path) for path in outputs},
        "claim_ceiling": model["claim_ceiling"],
    }
    result["result_content_sha256"] = canonical_sha(result)
    RESULT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"status": result["status"], "leading_theory": result["leading_theory"], "net_score": selected["net_abductive_score"], "predictions": len(predictions)}, sort_keys=True))


if __name__ == "__main__":
    main()
