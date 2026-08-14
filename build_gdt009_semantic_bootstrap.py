#!/usr/bin/env python3
"""Build a concrete YOLO semantic bootstrap over the frozen HPR-1 theory."""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_sha(value: object) -> str:
    payload = json.dumps(value, sort_keys=True, ensure_ascii=True, separators=(",", ":"))
    return hashlib.sha256(payload.encode()).hexdigest()


def read_tsv(name: str) -> list[dict[str, str]]:
    with (ROOT / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(name: str, rows: list[dict[str, object]]) -> None:
    with (ROOT / name).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def tagged(value: str, key: str) -> str:
    for part in value.split(";"):
        if part.startswith(key + ":"):
            return part.split(":", 1)[1]
    return ""


def main() -> None:
    occurrences = read_tsv("gdt002_morphology_occurrences.tsv")
    associations = read_tsv("gdt002_morphology_visual_associations.tsv")
    morphology = json.loads((ROOT / "gdt002_morphology_results.json").read_text())
    nested = json.loads((ROOT / "gdt003_nested_result.json").read_text())
    hpr = json.loads((ROOT / "gdt008_hybrid_register_model.json").read_text())
    assert not any(row["locus"].startswith("f84r") for row in occurrences)
    assert morphology["status"] == "FORMAL_REUSE_SUPPORTED_SEMANTIC_SLOT_SYSTEM_NOT_SUPPORTED"
    assert nested["status"] == "LIMITED/LOCAL COMPOSITION ONLY"
    assert hpr["theory_id"] == "HPR1_HYBRID_PROCEDURAL_REGISTER"

    best_assoc: dict[str, dict[str, str]] = {}
    for row in associations:
        key = row["module"]
        if key not in best_assoc or float(row["page_conditioned_one_sided_p"]) < float(best_assoc[key]["page_conditioned_one_sided_p"]):
            best_assoc[key] = row

    unit_evidence = []
    for module in ("AR", "OL", "DAL", "DAR", "SY", "TE", "TEE", "DY"):
        rows = [row for row in occurrences if row["module"] == module]
        exact = [row for row in rows if row["ZL3b_token"] and row["ZL3b_token"] == row["IT2a_token"] == row["RF1b_token"]]
        first = sum(int(row["source_group_index"]) == 1 for row in exact)
        last = sum(int(row["source_group_index"]) == int(tagged(row["source_group_count_by_reading"], "ZL3b")) for row in exact)
        label = sum(row["layout_role"] != "RUNNING_TEXT" for row in exact)
        annotated = sum(row["annotation_provenance"] != "NONE" for row in exact)
        states = {s: sum(tagged(row["match_state_by_reading"], "ZL3b") == s for row in exact) for s in ("FREE", "PREFIX", "INTERNAL", "SUFFIX")}
        assoc = best_assoc.get(module, {})
        summary = morphology["modules"][module.lower()]
        unit_evidence.append({
            "unit": module,
            "physical_occurrence_rows": len(rows),
            "all_reading_exact_rows": len(exact),
            "physical_folios": summary["physical_folios"],
            "free_physical": summary["free_physical"],
            "bound_physical": summary["bound_physical"],
            "host_types": summary["host_types"],
            "zl_free": states["FREE"],
            "zl_prefix": states["PREFIX"],
            "zl_internal": states["INTERNAL"],
            "zl_suffix": states["SUFFIX"],
            "line_first_share_exact": f"{first / len(exact):.6f}",
            "line_final_share_exact": f"{last / len(exact):.6f}",
            "nonprose_share_exact": f"{label / len(exact):.6f}",
            "annotated_rows_exact": annotated,
            "best_visual_axis": assoc.get("visual_contrast", "NONE"),
            "best_visual_effect": assoc.get("effect", ""),
            "best_page_conditioned_p": assoc.get("page_conditioned_one_sided_p", ""),
            "visual_caveat": assoc.get("confound", "NO_VISUAL_ASSOCIATION_ROW"),
        })

    evidence = [
        {"evidence_id":"S01","observation":"Lines have directional states and reset their coordinate at each physical newline.","weight":3,"procedural_reference_fit":1,"quantified_catalogue_fit":1,"spatial_flow_fit":0.5,"object_nomenclature_fit":0,"pure_template_fit":1,"meaning_pressure":"Treat a line as one bounded technical assertion/record."},
        {"evidence_id":"S02","observation":"Page-local root inventory is coherent while root adjacency remains directionally informative across Currier.","weight":3,"procedural_reference_fit":1,"quantified_catalogue_fit":1,"spatial_flow_fit":0.5,"object_nomenclature_fit":0.5,"pure_template_fit":0.5,"meaning_pressure":"Pages choose referents; lines assemble relations among them."},
        {"evidence_id":"S03","observation":"q-prepend combines with several right-edge states and survives all nested discovery folds.","weight":2,"procedural_reference_fit":1,"quantified_catalogue_fit":0.5,"spatial_flow_fit":0.5,"object_nomenclature_fit":0,"pure_template_fit":1,"meaning_pressure":"q is best treated as outer scope/dependency, not part of one object name."},
        {"evidence_id":"S04","observation":"DY is 98% right-concentrated in the morphology audit and combines widely with q-scoped hosts.","weight":3,"procedural_reference_fit":1,"quantified_catalogue_fit":1,"spatial_flow_fit":0.5,"object_nomenclature_fit":0,"pure_template_fit":1,"meaning_pressure":"DY is a closure/default-result field."},
        {"evidence_id":"S05","observation":"AR, OL, DAL, DAR, SY and DY occur free and bound; multiple tuples have manual split/join analogues.","weight":3,"procedural_reference_fit":1,"quantified_catalogue_fit":0.5,"spatial_flow_fit":0.5,"object_nomenclature_fit":0.5,"pure_template_fit":1,"meaning_pressure":"Fields may detach or contract; visible words are not indivisible names."},
        {"evidence_id":"S06","observation":"Exact che+VALUE is productive and AII+N tends to precede AI+N.","weight":2,"procedural_reference_fit":1,"quantified_catalogue_fit":1,"spatial_flow_fit":0,"object_nomenclature_fit":0,"pure_template_fit":0.5,"meaning_pressure":"A value carrier and ordered grade system are present."},
        {"evidence_id":"S07","observation":"Labels are denser in candidate modules and multi-module groups than prose.","weight":2,"procedural_reference_fit":1,"quantified_catalogue_fit":1,"spatial_flow_fit":0.5,"object_nomenclature_fit":1,"pure_template_fit":1,"meaning_pressure":"Labels are contracted field bundles, not necessarily proper names."},
        {"evidence_id":"S08","observation":"AROL-family labels occur by apparatus-like structures and by plants.","weight":3,"procedural_reference_fit":1,"quantified_catalogue_fit":0.5,"spatial_flow_fit":0,"object_nomenclature_fit":0,"pure_template_fit":0.5,"meaning_pressure":"AROL is a generic association/reference bundle; water/flow and object-name readings fail."},
        {"evidence_id":"S09","observation":"f83r juxtaposes reading-sensitive SAROLDAL with exact DAROLSY near two structures.","weight":1,"procedural_reference_fit":1,"quantified_catalogue_fit":0.5,"spatial_flow_fit":1,"object_nomenclature_fit":0.5,"pure_template_fit":0.5,"meaning_pressure":"d/s and DAL/SY can encode contrasting local states, but one panel cannot name the polarity."},
        {"evidence_id":"S10","observation":"The best DAL upper/lower visual association is weak and page-conditioned (p=.151); no module has a stable object role.","weight":2,"procedural_reference_fit":1,"quantified_catalogue_fit":0.5,"spatial_flow_fit":0,"object_nomenclature_fit":0,"pure_template_fit":1,"meaning_pressure":"Prefer abstract record functions over literal picture nouns or directions."},
        {"evidence_id":"S11","observation":"Nested transformation prediction remains below strong string statistics, especially q plus DY/DAL/DAR.","weight":3,"procedural_reference_fit":0.5,"quantified_catalogue_fit":0.5,"spatial_flow_fit":0.5,"object_nomenclature_fit":0.5,"pure_template_fit":1,"meaning_pressure":"Functions are conventional and renderer-dependent, not a clean ordinary-language affix algebra."},
        {"evidence_id":"S12","observation":"The metadata-aware nonsemantic context mixer beats every explicit language/semantic decoder.","weight":3,"procedural_reference_fit":1,"quantified_catalogue_fit":0.5,"spatial_flow_fit":0,"object_nomenclature_fit":0,"pure_template_fit":1,"meaning_pressure":"Any meaning-bearing layer must sit beneath a strong local register renderer."},
    ]
    worlds = {
        "W1_PROCEDURAL_REFERENCE_STATE": ("procedural_reference_fit", 4.5, "SELECTED"),
        "W2_QUANTIFIED_CATALOGUE": ("quantified_catalogue_fit", 3.5, "RIVAL"),
        "W3_SPATIAL_FLOW_DIAGRAM": ("spatial_flow_fit", 3.0, "RIVAL"),
        "W4_OBJECT_NOMENCLATURE": ("object_nomenclature_fit", 2.0, "RIVAL"),
        "W5_PURE_TEMPLATE_NO_SEMANTICS": ("pure_template_fit", 2.0, "NULL_RIVAL"),
    }
    world_rows = []
    for world, (field, penalty, decision) in worlds.items():
        raw = sum(float(row["weight"]) * float(row[field]) for row in evidence)
        world_rows.append({"world_id":world,"description":{
            "W1_PROCEDURAL_REFERENCE_STATE":"Lines describe or set relations among page-local referents, with scope, mode, grade, result-state, and closure fields.",
            "W2_QUANTIFIED_CATALOGUE":"Lines catalogue page-local objects through ordered grades and compact attribute fields.",
            "W3_SPATIAL_FLOW_DIAGRAM":"The recurrent pieces primarily encode sources, paths, destinations, and directional stages.",
            "W4_OBJECT_NOMENCLATURE":"Most recurrent compounds are abbreviated names of depicted objects.",
            "W5_PURE_TEMPLATE_NO_SEMANTICS":"A locally generated template process has no stable referential functions below its surface classes.",
        }[world],"weighted_fit":raw,"complexity_penalty":penalty,"net_abductive_score":raw-penalty,"rank":0,"decision":decision,"score_ceiling":"POSTHOC_ABDUCTIVE_RANK_NOT_PROBABILITY"})
    world_rows.sort(key=lambda row:(-float(row["net_abductive_score"]),row["world_id"]))
    for i,row in enumerate(world_rows,1): row["rank"] = i
    assert world_rows[0]["world_id"] == "W1_PROCEDURAL_REFERENCE_STATE"

    candidates = [
        ("LINE","TECHNICAL_ASSERTION_OR_RECORD","STRONG_ARCHITECTURAL","A line serializes one bounded description/update under a reset coordinate.","Could still be a synthetic production unit."),
        ("PAGE_ROOT_INVENTORY","LOCAL_REFERENTS","STRONG_ARCHITECTURAL","Page coherence plus directional root assembly fits a local inventory of items/processes/conditions.","No root referent is known."),
        ("q-","CURRENT_FRAME_OR_DEPENDENT_SCOPE","PROVISIONAL","Productive outer prepend; combines with DY/DAL/DAR; survives every nested training fold.","Held prediction does not beat string baselines; may be graphic onset class."),
        ("t / d / s at entry","NEW_RECORD / TWO_CONTINUATION_MODES","PROVISIONAL","Confirmed paragraph-state association and line-entry position.","Editorial paragraph state and no lexical gloss."),
        ("bound d-","SET_OR_ACTIVE_MODE","WEAK_PROVISIONAL","d/s minimal pairs and exact DAROL/DAROLSY fit an active rendering.","No repeated visual active/static contrast."),
        ("bound s-","DESCRIBE_OR_STATE_MODE","WEAK_PROVISIONAL","Contrasts with d on shared hosts; SAROL appears as a plant-associated label.","Polarity could be reversed or purely orthographic."),
        ("o- / ot-","ITEM_OR_LOCAL_FRAME","WEAK","o/ot participates inside q-scoped grids and labels.","o+TE versus OT+E segmentation is unresolved."),
        ("che-","VALUE_OR_ASSIGNMENT_CARRIER","STRONG_FORMAL_PROVISIONAL_SEMANTICS","Exact che+VALUE productivity is confirmed and root-conditioned.","Not established as a copula, preposition, or word."),
        ("AR","ASSOCIATION_OR_OPERATION_LINK","PROVISIONAL","Free/bound reuse, split/join with OL, and cross-object AROL contexts favor an abstract link.","Very frequent; segmentation nonunique; direct visual effects weak."),
        ("OL","REFERENT_OR_ITEM_FIELD","PROVISIONAL","Most diverse host inventory; free/bound; appears after AR and che and across object ecologies.","Could be a formal terminal class with no referential semantics."),
        ("AR+OL","ASSOCIATED_ITEM_OR_RELATION_TO_REFERENT","PROVISIONAL","Exact flow-adjacent DAROL plus plant AROL/SAROL and split/join AR|OL demand a cross-object function.","Opaque lexical AROL remains possible."),
        ("AI / AII + N","REDUCED / EXPANDED GRADE","PROVISIONAL","AII+N precedes AI+N more often than reverse.","No number or intensity value identified."),
        ("TE / TEE","COMPACT / EXPANDED INTERNAL GRADE","WEAK","TE/TEE minimal pairs nest inside identical q/o/DY frames.","Almost never free; substring parse may be accidental."),
        ("DAL","RESULT_CONFIGURATION_A","PROVISIONAL","Free/bound, right-biased, forms DAL+DY, weak upper/inside hints.","Upper/lower p=.151 and inside/outside p=.301; no direction assigned."),
        ("DAR","RESULT_CONFIGURATION_B_OR_DIRECTED_VARIANT","PROVISIONAL","Free/bound, strongly right-concentrated, contrasts with DAL/DY.","Often ambiguously d+AR; no source/destination proof."),
        ("SY","SECONDARY_OR_EXCEPTION_STATUS","WEAK_PROVISIONAL","82.8% right-concentrated and exact occurrences are notably label/final-position heavy.","Sparse and no replicated visual state."),
        ("DY","CLOSED_DEFAULT_OR_RESOLVED_STATE","STRONG_POSITION_PROVISIONAL_SEMANTICS","98% right concentration, 1,527 hosts, q compatibility, and DAL|DY split/join.","Could be a high-frequency formal ending without meaning; GDT003 null remains."),
        ("SOURCE SPACE / JOIN","EXPAND_OR_CONTRACT_FIELDS","STRONG_ARCHITECTURAL","AR|OL, DAL|DY, OL|CHEDY and other split/join analogues.","Not proof of author-intended linguistic morphemes."),
    ]
    candidate_rows = [{"unit":a,"selected_provisional_function":b,"rank":c,"support":d,"counterevidence":e,"claim_class":"PROVISIONAL_FUNCTION_NOT_TRANSLATION"} for a,b,c,d,e in candidates]

    parses = [
        ("f103r.12","otedy","[O:item-frame][TE:ordinary-grade][DY:resolved]","item/frame at ordinary grade; closed/default","ALL_THREE_EXACT","[OT][E][DY]"),
        ("f103r.15","qotedy","[Q:current-scope][O][TE][DY]","under the current frame: same ordinary closed value","ALL_THREE_EXACT","[Q][OT][E][DY]"),
        ("f103r.16","oteedy","[O][TEE:expanded-grade][DY]","item/frame at expanded grade; closed/default","ALL_THREE_EXACT","[OT][EE][DY]"),
        ("f103r.45","qoteedy","[Q][O][TEE][DY]","current-frame counterpart of expanded closed value","ALL_THREE_EXACT","[Q][OT][EE][DY]"),
        ("f82r.35","darol","[D:set/active][AR:association][OL:referent]","set/active association to local referent","ALL_THREE_EXACT_FLOW_ADJACENT","[DAR:configuration-B][OL]"),
        ("f82r.38","darary / daryry / jarary","[D?][AR?][AR?][Y]","possible parallel active/link bundle","READING_DISAGREEMENT","Do not normalize the three readings."),
        ("f83r.51","darolsy","[D][AR][OL][SY:secondary]","active associated item in secondary/marked state","ALL_THREE_EXACT_NEAR_RIGHT_STRUCTURE","[DAR][OL][SY]"),
        ("f83r.50","sasoldal / saroldal","[S:state][AR?][OL][DAL:configuration-A]","described associated item in configuration A","READING_SENSITIVE_NEAR_LEFT_STRUCTURE","ZL3b has AS rather than AR."),
        ("f99v.8","arol","[AR][OL]","bare associated-item/reference bundle","ALL_THREE_EXACT_PLANT_LABEL","Opaque AROL"),
        ("f102v2.14","sarol","[S][AR][OL]","state/description of associated item","ALL_THREE_EXACT_PLANT_LABEL","[SAR][OL]"),
        ("f75v.32","daldy","[DAL:configuration-A][DY:resolved]","configuration A in its closed/default state","ALL_THREE_EXACT_REPEATED_LABEL","[D][AL][DY]"),
        ("f75v.22","daldy / dal|dy","[DAL][DY]","same stock state bundle with detached/reading-variable closure","READING_AND_SEGMENTATION_SENSITIVE","IT2a detaches DY."),
        ("f80v.41","ar | ol / arol","[AR] <renderer> [OL]","expanded versus contracted associated-item bundle","MANUAL_SPLIT_JOIN_ANALOGY","Two independent adjacent fields."),
        ("f100r.25","cheol","[CHE:value-carrier][OL:referent]","explicit reference/value field","ALL_THREE_EXACT","Opaque CHEOL"),
    ]
    parse_rows = [{"locus":a,"surface":b,"selected_parse":c,"speculative_functional_reading":d,"evidence_state":e,"counterparse_or_caveat":f,"claim_class":"SPECULATIVE_GLOSS"} for a,b,c,d,e,f in parses]

    counterexamples = [
        ("AROL_EQUALS_WATER_OR_FLOW","FAILED","AROL at f99v.8 and SAROL at f102v2.14 are plant-associated labels; AROL is cross-object.","Retain generic association/reference bundle."),
        ("DAR_EQUALS_WATER","FAILED","DAR is widespread across prose and non-water contexts; f82r.38 is transcription-unstable.","Retain abstract mode/configuration ambiguity."),
        ("D_EQUALS_SOURCE_S_EQUALS_DESTINATION","FAILED","Only one suggestive f83r pair; no replicated ownership-safe polarity.","Use active/state mnemonics only."),
        ("DAL_EQUALS_UPPER_OR_INSIDE","WEAK","Page-conditioned visual p=.151 upper/lower and .301 inside/outside.","Configuration A only; no direction."),
        ("OL_EQUALS_APPARATUS","WEAK","Apparatus/flow enrichment is page-confounded and OL occurs widely with figures and plants.","Referent/item field is broader."),
        ("DY_IS_CONFIRMED_MORPHEME","FAILED_AS_CLAIM","Right-edge reuse is strong, but nested q+right-state prediction loses to string baselines.","Use closure as a theory component, not confirmed morphology."),
        ("Q_IS_CONFIRMED_GRAMMATICAL_PREFIX","FAILED_AS_CLAIM","q is formally productive yet adds no held advantage over KT/string statistics.","Current-scope is provisional."),
        ("F75V_DALDY_NAMES_SPOUTS","FAILED","Human annotations associate the two-line labels primarily with figures, not spout numbering.","Treat repeated DALDY as a stock field/state."),
        ("SIMPLE_NATURAL_LANGUAGE_PLAINTEXT","FAILED","Language mappings are unstable and lose to the metadata-aware source generator.","Hybrid register requires a renderer."),
        ("PURE_SEMANTIC_CODEBOOK","WEAK_RIVAL","Free/bound reuse, split/join, and cross-Currier directional adjacency look language-like.","Hybrid rather than pure code."),
    ]
    counter_rows = [{"hypothesis":a,"status":b,"counterexample":c,"effect_on_leading_theory":d} for a,b,c,d in counterexamples]

    predictions = [
        ("SP01","NEW_NON_F84_RELATION_ARRAYS","AR+OL-bearing labels will track an association/attachment role across at least two object classes better than any single object identity.","Freeze all labels in each array before form access; compare relation class with object class.","AR+OL predicts one object class only or no relation excess."),
        ("SP02","MATCHED_D_S_HOSTS","For identical hosts, d- and s- will align with two recurring record states rather than two object categories.","Acquire independent state annotations, then hold out physical folios.","Contrast vanishes or reverses across folios."),
        ("SP03","MATCHED_DAL_DAR_HOSTS","DAL and DAR on a shared host will predict a recurring binary configuration contrast, but not a universal spatial direction.","Preselect exact host pairs; blind geometry labels; leave one folio out.","No cross-folio configuration contrast."),
        ("SP04","REPEATED_ARRAYS","SY-bearing forms will be enriched in non-primary/second/exception positions within repeated arrays.","Ordinal and visual state fixed before form reveal; page-conditioned exact test.","No enrichment or one-page-only reversal."),
        ("SP05","LINE_POSITION","DY-bearing fields will be closer to line/record completion than matched shell-and-length controls.","Match page, Currier, kind, shell, and line length.","No positive held-folio shift."),
        ("SP06","Q_SCOPE_CONTEXT","q-scoped forms will preserve host role while depending more strongly on prior record/continuation context than unscoped hosts.","Same-host q pairs; held-folio context model without exact-form lookup.","q changes host role or context gain is absent."),
        ("SP07","CHE_VALUE_CONTEXT","che+OL and related che+VALUE forms will occupy value/reference slots more often than matched ch/sh forms.","New human structural annotation only; no lexical translation.","No held-page slot enrichment."),
        ("SP08","GRADE_ORDER","TEE/TE and AII/AI will show the same expanded-before-reduced ordering bias when matched by host.","Frozen two-grade collapse; held-page directional test.","The two systems have opposite or null held direction."),
        ("SP09","BOUNDARY_RENDERER","The same ordered latent tuple will be joined more often in labels and detached more often in prose.","Manual source boundaries; exact tuple; page and length matched.","No held-folio role effect."),
        ("SP10","PAGE_REGISTER_DECOMPOSITION","Page predicts referent/core inventory more strongly; Currier and line position predict wrappers/closures more strongly.","Crossed held-page/held-Currier information decomposition.","Both inequalities fail."),
    ]
    prediction_rows = [{"prediction_id":a,"target":b,"prediction":c,"measurement":d,"failure_condition":e,"status":"FROZEN_FOR_FUTURE_VALIDATION"} for a,b,c,d,e in predictions]

    write_tsv("gdt009_unit_evidence.tsv", unit_evidence)
    write_tsv("gdt009_world_evidence.tsv", evidence)
    write_tsv("gdt009_joint_worlds.tsv", world_rows)
    write_tsv("gdt009_semantic_candidates.tsv", candidate_rows)
    write_tsv("gdt009_locus_parses.tsv", parse_rows)
    write_tsv("gdt009_counterexamples.tsv", counter_rows)
    write_tsv("gdt009_predictions.tsv", prediction_rows)

    model = {
        "schema":"GDT009_PROCEDURAL_REFERENCE_STATE_MODEL_V1",
        "theory_id":"PRS1_PROCEDURAL_REFERENCE_STATE",
        "status":"SELECTED_EXPLORATORY_SEMANTIC_WORLD",
        "one_sentence":"Voynich lines are compact technical assertions that select page-local referents, place them under current/new/continuing record scope, express an association or operation, attach a grade/configuration, and close with a result-state; labels are contracted instances of the same fields.",
        "record_template":"[ENTRY_OR_SCOPE] [ITEM_FRAME_OR_VALUE_CARRIER] [ASSOCIATION/REFERENT CORE] [GRADE_OR_CONFIGURATION] [STATUS/CLOSURE]",
        "mnemonic_reading":{"q":"under current frame","t":"new record","d":"set/active","s":"describe/state","o/ot":"item/local frame","che":"value/reference follows","AR":"association/operation link","OL":"referent/item","AI/AII":"reduced/expanded grade","TE/TEE":"compact/expanded grade","DAL":"configuration A","DAR":"configuration B/directed variant","SY":"secondary/exception","DY":"closed/default/resolved"},
        "boundary_renderer":"Adjacent fields may be joined or detached; labels favor compact bundles and prose expands fields.",
        "known_unknowns":["polarity of d versus s","content of page-local cores","identity of configurations DAL/DAR","whether DY is one field or a bundle","historical language beneath the register"],
        "f84r":{"opened":False,"joined":False,"scored":False,"prior_predictions_unchanged":True},
        "claim_ceiling":"A selected speculative functional world model, not a confirmed language, morpheme, POS, word meaning, plaintext, translation, authorship, date, or origin.",
    }
    (ROOT / "gdt009_semantic_model.json").write_text(json.dumps(model,indent=2,sort_keys=True)+"\n")

    top = world_rows[0]
    report = f"""# GDT009 semantic bootstrap: procedural reference-state world

Status: **SELECTED EXPLORATORY SEMANTIC WORLD — PRS-1**

## Best current meaning theory

Voynich lines most plausibly behave as **compact technical assertions about
page-local referents**.  A line opens or continues a record, selects an item or
value frame, states an association/operation, adds a grade or configuration,
and optionally closes the result.  Labels are compressed one-field or
multi-field records, not necessarily names.  This is the semantic layer of the
HPR-1 renderer.

In deliberately concrete mnemonic English:

```text
q    under the current record/frame       t    start a new record
d    set/apply or active rendering        s    describe/state rendering
o/ot item/local frame                     che  an explicit value/reference follows
AR   association or operation link        OL   the referent/item field
AI/AII, TE/TEE  reduced/expanded grade    DAL/DAR configuration A/B
SY   secondary or exception status        DY   closed/default/resolved result
```

These are provisional functional readings, not dictionary translations.

## Joint-world comparison

| rank | world | weighted fit | penalty | net | decision |
| ---: | --- | ---: | ---: | ---: | --- |
"""
    for row in world_rows:
        report += f"| {row['rank']} | {row['world_id']} | {float(row['weighted_fit']):.1f} | {float(row['complexity_penalty']):.1f} | {float(row['net_abductive_score']):.1f} | {row['decision']} |\n"
    report += f"""

PRS-1 wins this deliberately post-hoc comparison with net score
{float(top['net_abductive_score']):.1f}.  The strongest rival is the pure
template null: it explains local predictability well but leaves the confirmed
page inventory, ordered carriers, split/join reuse, and cross-object AROL bundle
without functional content.  PRS-1 earns its extra layer by explaining those
facts together.

## What the pieces most likely do

- **q** is an outer dependency/current-frame instruction: not “a word”, but
  “interpret the enclosed field under the active record.”
- **d/s/t** select record mode.  `t` starts; `d` and `s` continue.  The working
  polarity is active/set versus descriptive/state, but it may reverse.
- **che** is the best candidate for an explicit value/assignment carrier.
- **AR** is an association/operation link and **OL** a referent/item field.
  `AROL` therefore means roughly *associated item / relation-to-referent*, not
  water, flow, woman, or plant.
- **AI/AII** and **TE/TEE** are reduced/expanded grades.  No number is assigned.
- **DAL/DAR** are alternative result configurations.  No left/right,
  source/destination, or upper/lower assignment survives yet.
- **SY** marks a secondary/exception state; **DY** is the default resolved or
  closed result.

## Representative readings

`otedy` is `[item-frame][ordinary-grade][resolved]`; `qotedy` is the same
bundle under current-record scope.  `oteedy/qoteedy` repeats the grid with an
expanded grade.  `darol` is an active association to a local referent.
`darolsy` is that association in a secondary state.  Reading-sensitive
`saroldal` is the descriptive/state counterpart in configuration A.  `daldy`
is a stock *configuration-A, resolved* bundle.  `cheol` is an explicit
reference/value field.

This interpretation explains why `darol` can occur by a flow-like structure
while `arol` and `sarol` also occur as plant labels: the bundle says what role
the local item plays in the record, not what kind of pictured object it is.

## Quantitative anchors

- GDT002 found AR/OL/DAL/DAR/SY/DY on 67–103 physical folios and in both free
  and bound use; DY has 1,527 host types and 98% right-edge concentration.
- Candidate-module density is 13.519 hits/100 symbols in labels versus 10.586
  in prose, and multi-module groups are 2.19 times as common in labels.
- Exact `daldy` recurs in 13 all-reading-exact physical groups.
- SY is sparse but 82.8% right-concentrated; among exact occurrences it is
  unusually final/label-heavy relative to the common modules.
- The best picture correlations remain weak: DAL upper/lower is p=.151 and
  inside/outside p=.301 after page conditioning.  Those clues motivate
  configuration semantics but do not name configurations.

## Counterexamples that shaped the theory

`AROL = water/flow`, `DAR = water`, `d/s = source/destination`, and
`DAL = upper` are rejected.  q and DY are not confirmed morphemes because the
nested algebra does not outperform string baselines.  The theory instead
assigns abstract record functions, where cross-object reuse is expected.

## What remains awkward

The pure-template source model is still a formidable alternative and compresses
better.  No core referent is securely named.  d/s polarity, DAL/DAR polarity,
and TE/TEE segmentation are invented.  Several strongest visual clues are
page-confounded.  PRS-1 is therefore a theory to generate sharper observations,
not a decoded paragraph.

## New predictions

Ten explicit predictions are frozen in `gdt009_predictions.tsv`.  The most
important are: AR+OL should transfer as an association role across object
classes; same-host d/s and DAL/DAR contrasts should align with repeatable
record/configuration states on unseen folios; SY should prefer secondary array
positions; DY should be record-final after shell matching; and q should depend
on prior record context while preserving host role.

## Conclusion

The best current concrete meaning theory is **PRS-1**: a procedural
reference-state register.  The manuscript is not merely a list of names and
not ordinary visible prose.  It records page-local items through reusable
association, grade, configuration, status, and closure fields, rendered with
scope/mode operators and aggressive abbreviation.  That theory explains more
observations at once than a literal flow vocabulary, object nomenclature, or
pure quantified catalogue, while remaining explicitly vulnerable to the pure
template null.

f84r remains sealed.  No language, sound, plaintext, or translation is claimed.
"""
    (ROOT / "GDT009_SEMANTIC_BOOTSTRAP_REPORT.md").write_text(report)

    outputs = ["gdt009_unit_evidence.tsv","gdt009_world_evidence.tsv","gdt009_joint_worlds.tsv","gdt009_semantic_candidates.tsv","gdt009_locus_parses.tsv","gdt009_counterexamples.tsv","gdt009_predictions.tsv","gdt009_semantic_model.json","GDT009_SEMANTIC_BOOTSTRAP_REPORT.md"]
    inputs = ["gdt002_morphology_occurrences.tsv","gdt002_morphology_visual_associations.tsv","gdt002_morphology_results.json","gdt002_morphology_minimal_pairs.tsv","gdt002_morphology_split_join.tsv","gdt003_nested_result.json","gdt008_hybrid_register_model.json","gdt008_result.json","experiments/semantic_assumptions/grammar/CONFIRMED_GRAMMAR.md","YOLO_MODE.md"]
    result = {
        "schema":"GDT009_SEMANTIC_BOOTSTRAP_RESULT_V1",
        "status":"PRS1_SELECTED_EXPLORATORY_SEMANTIC_WORLD",
        "leading_world":"W1_PROCEDURAL_REFERENCE_STATE",
        "leading_theory":"PRS1_PROCEDURAL_REFERENCE_STATE",
        "answer":"The strongest concrete reading is a procedural reference-state register: q scopes the current record; d/s select active versus descriptive modes; AR+OL associates a local referent; grade and configuration fields lead to SY secondary status or DY resolved closure. These are speculative functions, not translations.",
        "worlds_compared":len(world_rows),"semantic_candidates":len(candidate_rows),"representative_parses":len(parse_rows),"counterexamples":len(counter_rows),"novel_predictions":len(prediction_rows),
        "prior_results_preserved":{"GDT002":"FORMAL_REUSE_SUPPORTED_SEMANTIC_SLOT_SYSTEM_NOT_SUPPORTED","GDT003":"NOT DISTINGUISHABLE FROM STRING STATISTICS","GDT008":"HPR1_SELECTED_EXPLORATORY_WORLD_MODEL"},
        "f84r":{"opened":False,"joined":False,"scored":False},
        "inputs":{name:sha(ROOT/name) for name in inputs},
        "implementation":{"build_gdt009_semantic_bootstrap.py":sha(Path(__file__)),"GDT009_SEMANTIC_BOOTSTRAP_METHOD.md":sha(ROOT/"GDT009_SEMANTIC_BOOTSTRAP_METHOD.md")},
        "outputs":{name:sha(ROOT/name) for name in outputs},
        "claim_ceiling":model["claim_ceiling"],
    }
    result["result_content_sha256"] = canonical_sha(result)
    (ROOT / "gdt009_result.json").write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print(json.dumps({"status":result["status"],"leading":result["leading_world"],"world_score":top["net_abductive_score"],"parses":len(parse_rows)},sort_keys=True))


if __name__ == "__main__":
    main()
