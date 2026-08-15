#!/usr/bin/env python3
"""GDT100: evidence-bound HPR2 generative-theory revision."""
from __future__ import annotations
import csv,hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parent;METHOD=ROOT/"GDT100_HPR2_THEORY_REVISION_METHOD.md";REPORT=ROOT/"GDT100_HPR2_THEORY_REVISION_REPORT.md";COMP=ROOT/"gdt100_component_status.tsv";THEORIES=ROOT/"gdt100_theory_comparison.tsv";PRED=ROOT/"gdt100_novel_predictions.tsv";MODEL=ROOT/"gdt100_hpr2_revised_model.json";RESULT=ROOT/"gdt100_result.json"
INPUTS=("gdt003_nested_result.json","gdt060_result.json","gdt062_result.json","gdt073_result.json","gdt083_result.json","gdt089_result.json","gdt090_result.json","gdt091_result.json","gdt092_result.json","gdt093_result.json","gdt094_result.json","gdt095_result.json","gdt096_result.json","gdt097_result.json","gdt098_result.json","gdt099_result.json")
def write(p,rows,fields):
 with p.open("w",encoding="utf-8",newline="") as h:w=csv.DictWriter(h,fieldnames=fields,delimiter="\t",lineterminator="\n");w.writeheader();w.writerows(rows)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def csha(x):return hashlib.sha256(json.dumps(x,sort_keys=True,ensure_ascii=True,separators=(",",":")).encode()).hexdigest()
def main():
 for name in INPUTS:assert (ROOT/name).exists()
 components=[
  {"component":"PHYSICAL_LINE","model_layer":"RECORD_SERIALIZATION","status":"STRONG_FORMAL","provisional_function":"record/utterance-like unit with internal coordinate reset","evidence":"confirmed line reset and record architecture","counterevidence":"not a decoded sentence"},
  {"component":"SOURCE_SEPARATOR","model_layer":"SERIALIZATION","status":"STRONG_FORMAL","provisional_function":"hierarchical physical grouping","evidence":"source-native separator information","counterevidence":"not established linguistic word space"},
  {"component":"PAGE_HOST_OR_SUBHOST","model_layer":"CONTENT_ADDRESS","status":"PROVISIONAL","provisional_function":"page-conditioned technical content address, identity or reusable submotif","evidence":"page-local inventory and weak external PAGE_HOST leads","counterevidence":"GDT095 no selector-paid exhaustive channel; GDT099 no global survivor"},
  {"component":"O_Y_BASE","model_layer":"HOST_BRANCH","status":"STRONG_FORMAL","provisional_function":"binary construction branch licensing outer wrapper","evidence":"q->O and d->Y across tails/registers/held folios","counterevidence":"identical to first-character string baseline"},
  {"component":"Q_WRAPPER","model_layer":"OUTER_COMPILER","status":"STRONG_FORMAL","provisional_function":"early O-branch wrapper","evidence":"GDT086/GDT087/GDT091/GDT094","counterevidence":"no sound, meaning, or string-baseline advantage"},
  {"component":"D_WRAPPER","model_layer":"OUTER_COMPILER","status":"STRONG_FORMAL","provisional_function":"late Y-branch wrapper","evidence":"GDT087/GDT091/GDT094","counterevidence":"archived global entry gloss is false"},
  {"component":"CH_CHE_SH_S_WRAPPERS","model_layer":"OUTER_OR_LOCAL_COMPILER","status":"CONDITIONAL","provisional_function":"host/register-conditioned construction wrappers","evidence":"wrapper compatibility and register effects","counterevidence":"directions reverse in at least one register"},
  {"component":"RIGHT_FAMILY","model_layer":"REGISTER_RENDERER","status":"STRONG_FORMAL","provisional_function":"host-conditional register rendering in AIIN/AIR/AIN/AR/AL families","evidence":"GDT062 whole-folio-held transfer","counterevidence":"content neutrality not independently proved"},
  {"component":"DY","model_layer":"INTERNAL_CHECKPOINT","status":"PROVISIONAL","provisional_function":"frequent internal record-phase boundary/renderer","evidence":"record segmentation and PCH cross-register enrichment","counterevidence":"GDT060 external post-boundary host transfer negative; GDT003 string baseline"},
  {"component":"B3","model_layer":"RECORD_CLOSE","status":"PROVISIONAL_FORMAL","provisional_function":"source-native line/field close coordinate","evidence":"final-position architecture","counterevidence":"external content-neutrality not separately confirmed"},
  {"component":"PCH_SUBMOTIF","model_layer":"DOMAIN_HOST_FAMILY","status":"WEAK_POSTSELECTED","provisional_function":"recurrent pharma/recipe record-phase host family","evidence":"331 groups; HB/S context cosine .732; six pharma spatial-context cases","counterevidence":"maxT .147; five non-pharma annotated negatives; rank 60/84 context motifs"},
  {"component":"EXACT_HOST_VISUAL_BUNDLE","model_layer":"SEMANTIC_GROUNDING","status":"NOT_SUPPORTED","provisional_function":"NONE","evidence":"narrow os/DARK_LEAF seed only","counterevidence":"GDT090 broad bundle stability p=.9713"},
 ]
 write(COMP,components,list(components[0]))
 theories=[
  {"rank":1,"theory":"HYBRID_CONTENT_ADDRESS_PLUS_ABBREVIATION_AND_RECORD_COMPILER","fit_score_0_to_10":8,"strength":"explains page vocabulary, formal branches, register rendering, line reset and weak domain-local grounding together","awkward":"content addresses lack transferable gloss; GDT003/string ceiling"},
  {"rank":2,"theory":"COMPRESSED_OR_ABBREVIATED_NATURAL_LANGUAGE","fit_score_0_to_10":5,"strength":"free/bound reuse and local similarity are compatible with abbreviation","awkward":"extreme compiler regularity and transformation gains do not beat string baselines; no phonology"},
  {"rank":3,"theory":"PURE_SEMANTIC_OR_TECHNICAL_NOTATION","fit_score_0_to_10":4,"strength":"record fields, page inventories and repeated diagram labels are compatible","awkward":"large productive surface variation and cross-register host continuity are excessive for a simple code list"},
 ]
 write(THEORIES,theories,list(theories[0]))
 predictions=[
  {"prediction_id":"HPR2R_P01","scope":"FUTURE_NON_F84_FRESH_PHARMA_LABEL_PANEL","prediction":"PCH-bearing PAGE_HOSTs are enriched for the same frozen mixed spatial-context endpoint","kill_or_downgrade":"no enrichment under within-folio matched comparison","status":"FROZEN_NOT_RUN","semantic_role":"UNASSIGNED"},
  {"prediction_id":"HPR2R_P02","scope":"FUTURE_NON_F84_EXTERNAL_CONTENT_PANEL","prediction":"PAGE_HOST/subhost features exceed compiler-only and raw string after whole-folio holdout","kill_or_downgrade":"raw equals or beats host, or no selector-paid gain","status":"FROZEN_NOT_RUN","semantic_role":"UNASSIGNED"},
  {"prediction_id":"HPR2R_P03","scope":"NEW_O_Y_MATCHED_TAILS","prediction":"q remains O-selecting/early and d Y-selecting/late on unseen tails and folios","kill_or_downgrade":"either directional rule reverses after exact tail and folio exclusion","status":"FROZEN_NOT_RUN","semantic_role":"UNASSIGNED"},
  {"prediction_id":"HPR2R_P04","scope":"NEW_CROSS_REGISTER_HOSTS","prediction":"RIGHT_FAMILY changes by register conditional on retained PAGE_HOST while host identity persists","kill_or_downgrade":"register adds no held codelength beyond host/compiler nuisance","status":"FROZEN_NOT_RUN","semantic_role":"UNASSIGNED"},
  {"prediction_id":"HPR2R_P05","scope":"FUTURE_EXTERNAL_LAYOUT_AND_APPEARANCE_AXES","prediction":"B3 associates with record boundary/layout but not independent appearance content after PAGE_HOST control","kill_or_downgrade":"B3 adds transferable appearance prediction","status":"FROZEN_NOT_RUN","semantic_role":"UNASSIGNED"},
  {"prediction_id":"HPR2R_P06","scope":"FUTURE_NEW_PAGE_BLOCK","prediction":"page-local PAGE_HOST inventory improves sequential prediction beyond register/wrapper without relying on a single page","kill_or_downgrade":"gain vanishes under leave-one-page influence deletion","status":"FROZEN_NOT_RUN","semantic_role":"UNASSIGNED"},
 ]
 write(PRED,predictions,list(predictions[0]))
 model={"schema":"GDT100_HPR2_REVISED_GENERATIVE_MODEL_V1","name":"HYBRID_CONTENT_ADDRESS_PLUS_RECORD_COMPILER","leading_theory":theories[0]["theory"],"grammar":{"MANUSCRIPT":"REGISTER_BLOCK+","PAGE":"PAGE_PROFILE CONTENT_ADDRESS_INVENTORY LINE+","LINE":"ENTRY_STATE? FIELD (DY_CHECKPOINT FIELD)* B3_CLOSE?","FIELD":"OUTER_WRAPPER? LOCAL_O_OT_FRAME? CONTENT_ADDRESS RIGHT_FAMILY?","CONTENT_ADDRESS":"OPAQUE_PAGE_HOST | O_Y_BASE+TAIL | REUSABLE_SUBHOST_MOTIF+RESIDUAL","OUTER_WRAPPER":{"Q":"O_BASE_EARLY","D":"Y_BASE_LATE","CH_CHE_SH_S":"HOST_REGISTER_CONDITIONAL"},"RIGHT_FAMILY":"render(CONTENT_ADDRESS,REGISTER,WRAPPER)","DY":"PROVISIONAL_INTERNAL_CHECKPOINT","B3":"PROVISIONAL_RECORD_CLOSE"},"semantic_assignments":[],"provisional_content_candidates":[{"form":"PCH","role":"UNASSIGNED","status":"WEAK_DOMAIN_CONFINED_HOST_FAMILY"},{"form":"OS","role":"UNASSIGNED","status":"WEAK_TWO_LOCUS_DARK_LEAF_SEED"}],"superseded":"GDT092 wording that PAGE_HOST directly supplies a content lexicon; revised to ungrounded content-address layer","translation_readiness":"NOT_READY_REQUIRES_FRESH_TRANSFERABLE_EXTERNAL_CONTENT_AXIS","f84r":"SEALED_NO_PREDICTION"};MODEL.write_text(json.dumps(model,indent=2,sort_keys=True)+"\n")
 status="HYBRID_CONTENT_ADDRESS_PLUS_RECORD_COMPILER_REMAINS_LEADING_WITH_SEMANTICS_UNGROUNDED"
 REPORT.write_text(f"""# GDT100 — revised HPR2 generative theory

## Leading theory

**HYBRID CONTENT ADDRESS + ABBREVIATION + RECORD COMPILER**

The best current generator is still hybrid, but GDT092's claim that PAGE_HOST
directly supplies a content lexicon was too strong. The safer and more useful
model is:

```text
PAGE  := PAGE_PROFILE + CONTENT_ADDRESS_INVENTORY + LINE+
LINE  := ENTRY? FIELD (DY_CHECKPOINT FIELD)* B3_CLOSE?
FIELD := OUTER_WRAPPER? O_OT_FRAME? CONTENT_ADDRESS RIGHT_FAMILY?

CONTENT_ADDRESS := opaque PAGE_HOST
                 | O/Y branch + tail
                 | reusable subhost motif + residual

q -> O branch, early          d -> Y branch, late
RIGHT_FAMILY -> register-conditioned rendering
```

The compiler half is the strongest part. q/O and d/Y transfer to unseen tails
and folios, RIGHT_FAMILY transfers by register, and line/reset/field structure
is pervasive. Those operations still do not beat string statistics as a
linguistic morphology model.

The content-address half is plausible but ungrounded. PAGE_HOSTs have page-local
inventory signal. The narrow GDT089 and GDT096 external leads favor PAGE_HOST
over compiler features in limited panels, but GDT095's exhaustive descriptor
channel does not pay selection and GDT099 finds no global submotif association.
`PCH` is the clearest concrete new candidate: a recurrent HB/S record-phase
host family with a domain-local pharmaceutical spatial-context association,
not a manuscript-wide spatial word.

This remains more coherent than compressed natural language alone or pure
notation alone because it explains formal reuse, register rendering, page
vocabulary, and record serialization together. It is not ready for translation.
Six new non-f84 predictions are frozen. f84r receives no prediction and remains
completely sealed.
""",encoding="utf-8")
 result={"schema":"GDT100_HPR2_THEORY_REVISION_RESULT_V1","status":status,"leading_theory":theories[0]["theory"],"components":len(components),"theories":len(theories),"predictions":len(predictions),"semantic_assignments":0,"major_revision":"PAGE_HOST_CONTENT_LEXICON_TO_UNGROUNDED_CONTENT_ADDRESS_LAYER","interpretation":"Explicit abductive generator with strong formal compiler and provisional content-address layer; translation remains unready.","claim_ceiling":"Exploratory generative theory only; no confirmed role, gloss, word, morpheme, POS, sound, language, plaintext, meaning, or translation.","f84r":{"opened":False,"retained":False,"queried":False,"joined":False,"scored":False,"targeted":False,"prediction_made":False},"inputs":{n:sha(ROOT/n) for n in INPUTS},"implementation":{Path(__file__).name:sha(Path(__file__))},"outputs":{COMP.name:sha(COMP),THEORIES.name:sha(THEORIES),PRED.name:sha(PRED),MODEL.name:sha(MODEL)},"documents":{METHOD.name:sha(METHOD),REPORT.name:sha(REPORT)}};result["result_content_sha256"]=csha(result);RESULT.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n");print(json.dumps({"status":status,"components":len(components),"predictions":len(predictions),"leading":theories[0]["theory"]},sort_keys=True))
if __name__=="__main__":main()
