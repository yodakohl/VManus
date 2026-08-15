#!/usr/bin/env python3
"""GDT051: generate the revised HPR-2 record compiler and audit artifacts."""
from __future__ import annotations
import csv,hashlib,json
from collections import defaultdict
from pathlib import Path
ROOT=Path(__file__).resolve().parent;SOURCE=ROOT/"gdt016_group_state_inventory.tsv";METHOD=ROOT/"GDT051_REVISED_HYBRID_REGISTER_COMPILER_METHOD.md";REPORT=ROOT/"GDT051_REVISED_HYBRID_REGISTER_COMPILER_REPORT.md";MODEL=ROOT/"gdt051_hpr2_model.json";COMP=ROOT/"gdt051_component_status.tsv";PARSES=ROOT/"gdt051_representative_parses.tsv";PRED=ROOT/"gdt051_novel_predictions.tsv";RESULT=ROOT/"gdt051_result.json"
INPUTS=("gdt008_result.json","gdt012_result.json","gdt014_result.json","gdt016_result.json","gdt020_result.json","gdt025_result.json","gdt029_result.json","gdt035_result.json","gdt036_result.json","gdt041_result.json","gdt042_result.json","gdt043_result.json","gdt045_result.json","gdt046_result.json","gdt048_result.json","gdt049_result.json","gdt050_result.json")
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def csha(v):return hashlib.sha256(json.dumps(v,sort_keys=True,ensure_ascii=True,separators=(",",":")).encode()).hexdigest()
def read(p):
 with Path(p).open(encoding="utf-8",newline="")as h:return list(csv.DictReader(h,delimiter="\t"))
def write(p,rows,fields):
 with Path(p).open("w",encoding="utf-8",newline="")as h:w=csv.DictWriter(h,fieldnames=fields,delimiter="\t",lineterminator="\n");w.writeheader();w.writerows(rows)
def main():
 source=[]
 for r in read(SOURCE):
  if r["locus"].startswith("f84r"):continue
  source.append(r)
 by=defaultdict(list)
 for r in source:by[r["locus"]].append(r)
 components=[
  {"component":"PHYSICAL_LINE_RESET","layer":"RECORD","status":"SUPPORTED","formal_role":"record serialization resets at each physical line","evidence":"GDT016/GDT020 transferable line and phase structure","counterevidence":"not every line has a unique opener or closer"},
  {"component":"DY","layer":"FIELD_BOUNDARY","status":"SUPPORTED_FORM_PROVISIONAL_FUNCTION","formal_role":"internal checkpoint/field-transition realization","evidence":"right-edge concentration and transferable within-line phase","counterevidence":"not a local reset; next payload is decoupled; not a confirmed morpheme"},
  {"component":"B3","layer":"RECORD_CLOSE","status":"STRONG_SUPPORTED","formal_role":"probabilistic physical-record closing marker class","evidence":"148/213 final; positive in every register and held non-HB/S","counterevidence":"endpoint recall only 0.124; not mandatory punctuation"},
  {"component":"Q2","layer":"RECORD_OPEN","status":"WEAK_PROVISIONAL","formal_role":"opener class preferentially paired with B3","evidence":"31 pairs versus 23.933 expected, local p .0071","counterevidence":"max-search p .071 and held non-HB/S p .116"},
  {"component":"QJB_QKB_VS_LJB_LKB","layer":"CLOSURE_RENDERER","status":"HOST_LICENSED_REGISTER_RULE","formal_role":"Currier-B checkpoint-branch realization licensed mainly by host spelling","evidence":"host ngrams predict held folios and unseen hosts","counterevidence":"previous-DY gain beyond host is small and unstable"},
  {"component":"CH_CHE_SH","layer":"LEFT_RENDERER","status":"HOST_LICENSED_WEAK_POSITIONAL","formal_role":"host/register-conditioned carrier renderers with weak shared placement","evidence":"held-folio and held-host position/context gains","counterevidence":"register dominates; no universal wrapper function"},
  {"component":"CARRIER_PLUS_D","layer":"NESTED_LEFT_STACK","status":"COMBINATORIAL_SUPPORTED_FUNCTION_UNKNOWN","formal_role":"ordered carrier+D+host stack shared by HB/S","evidence":"101 B/S double stacks with host/folio-controlled excess","counterevidence":"no tested stable coarse local-context function"},
  {"component":"O_OT_AR_AL","layer":"LOCAL_FRAME","status":"PROVISIONAL","formal_role":"O/OT-framed AR/AL fields tend later than bare forms","evidence":"OTAR and OTAL positional ladders","counterevidence":"semantic reference gloss is postselected and visually confounded"},
  {"component":"AIR","layer":"RIGHT_FAMILY","status":"REGISTER_SELECTION_SUPPORTED_FUNCTION_UNKNOWN","formal_role":"HB/S-enriched member of AIIN/AIR/AIN/AR/AL family","evidence":"54/1201 target versus 19/1034 controls; survives every target-folio deletion","counterevidence":"no stable local role and no OKAIR human-label grounding"},
  {"component":"KAIIN","layer":"HOST","status":"FAILED_AS_PRIVILEGED_CORE","formal_role":"ordinary K+AIIN construction cell","evidence":"K and AIIN both independently reusable","counterevidence":"all matched family tests p >= .297"},
  {"component":"CKHY_GLOSS","layer":"CONTENT","status":"FAILED_SEMANTIC_GLOSS","formal_role":"none assigned","evidence":"formal core remains recurrent","counterevidence":"second prospective parallel/fused leaf-or-stalk transfer failed"},
  {"component":"PAGE_LOCAL_HOSTS","layer":"CONTENT","status":"REQUIRED_BUT_UNGROUNDED","formal_role":"page-selected technical content inventory","evidence":"page-conditioned root inventory and residual host reuse","counterevidence":"no stable concrete referent survives transfer"},
  {"component":"PHYSICAL_JOIN_SPLIT","layer":"BOUNDARY_RENDERER","status":"UNCONFIRMED","formal_role":"possible optional contraction/expansion","evidence":"source split/join near-misses and label density","counterevidence":"GDT004-GDT007 found no confirmed physical module boundary"},
  {"component":"NATURAL_LANGUAGE_STEM_LAYER","layer":"CONTENT","status":"ABDUCTIVE_ONLY","formal_role":"possible abbreviated lexical/mnemonic residue","evidence":"free/bound reuse and page-local inventories","counterevidence":"complete language/cipher models and phonological routes fail; GDT003 equals string statistics"},
 ]
 write(COMP,components,list(components[0]))
 examples={
  "f50r.3":"ENTRY/OL; AR; DY; DY; DY; DY; DY; DY; CARRIER+K+AIIN; B3",
  "f34v.4":"ENTRY+CARRIER+D+AIIN; CARRIER+K+AL; DY; Q+OK+ED+AR; CARRIER+D+AIIN; OL+DAR; Q+OL+DAR; CARRIER+DY; D+AIIN; B3",
  "f51r.9":"ENTRY+OL; D+AIIN; D+AI+M; Q+CARRIER+O+DAL; DAL; Q+O+DY; Q+O+ETA+B3",
  "f104r.39":"OL; AR; AIIN; DY; Q+OT+AL; CARRIER+OL; Q+O+AR; AIIN; Q+DY; Q+OT+AIR; HOST",
  "f105v.16":"D+AIIN; CARRIER; DAL; CARRIER; OK+AIR; AIIN; HOST; AIIN; OK+AL; CARRIER+O+D+AIIN; OT+AIIN; B3",
  "f40v.18":"S+AIIN; OT+AIN; CARRIER+CKHY; OK+AL; OK+AIR; AR+OL; Q+OK+EY; OK+AR+Y",
 }
 parses=[]
 for locus,parse in examples.items():
  z=sorted(by[locus],key=lambda r:int(r["group_index"]));assert z and len(z)==int(z[0]["group_count"])
  parses.append({"locus":locus,"register":("HA"if z[0]["section"]=="H"and z[0]["currier"]=="A"else"HB"if z[0]["section"]=="H"else"SB"),"surface_sequence":" | ".join(r["token"]for r in z),"state_sequence":" > ".join(r["record_state"]for r in z),"hpr2_formal_parse":parse,"semantic_reading":"UNASSIGNED","caveat":"operational parse; alternative segmentations remain"})
 write(PARSES,parses,list(parses[0]))
 predictions=[
  {"prediction_id":"HPR2_P01","target":"NON_F84_DIAGNOSTIC_LABEL_LINES_WITH_SOURCE_NATIVE_B3_CAPACITY","prediction":"B3 will retain endpoint enrichment outside confirmed prose after ownership-neutral census","kill":"B3 endpoint rate is no higher than matched stable final-member classes","status":"FROZEN_NOT_RUN"},
  {"prediction_id":"HPR2_P02","target":"COMPLETE_NON_F84_LINES","prediction":"B3-ended records will show a distinct internal-DY field-count profile after folio/register/length control","kill":"profile gain is zero or reverses under held folios","status":"FROZEN_NOT_RUN"},
  {"prediction_id":"HPR2_P03","target":"UNSEEN_O_OT_HOST_FAMILIES","prediction":"OT-framed AR/AL-compatible hosts occur later than matched bare hosts","kill":"held-host positional direction is absent","status":"FROZEN_NOT_RUN"},
  {"prediction_id":"HPR2_P04","target":"FUTURE_NON_F84_HUMAN_VISUAL_ANNOTATIONS","prediction":"page-local host identity will predict visual referent class better than wrapper or right-state identity","kill":"wrapper/right state equals or beats host under held-folio matched controls","status":"FROZEN_NOT_RUN"},
  {"prediction_id":"HPR2_P05","target":"CARRIER_PLUS_D_COMPLETE_LINES","prediction":"carrier+D will associate with a longer-range field template not any single adjacent position","kill":"no held-folio gain for a predeclared two-field context model","status":"FROZEN_NOT_RUN"},
  {"prediction_id":"HPR2_P06","target":"AIR_RIGHT_FAMILY","prediction":"AIR preference will reproduce under nested training-folio discovery rather than a fixed post-hoc suffix set","kill":"held-folio gain does not beat a matched character/right-edge baseline","status":"FROZEN_NOT_RUN"},
 ]
 write(PRED,predictions,list(predictions[0]))
 model={"schema":"GDT051_HPR2_GENERATIVE_MODEL_V1","name":"HPR-2_LAYERED_TECHNICAL_RECORD_COMPILER","leading_theory":"HYBRID_LANGUAGE_ABBREVIATION_PLUS_RECORD_NOTATION","generator":{"manuscript":"shared construction graph plus register/hand renderer plus page-local host inventory","page":"select domain-conditioned host inventory","paragraph":"editorial opening/continuation state is context, not semantics","line":"record_open? field (DY field)* record_close?; reset at physical newline","record_open":"Q2-class weak probabilistic option","field":"left_renderer? inner_D? local_frame? page_host right_family?","left_renderer":"CH/CHE/SH host-and-register licensed; D may nest under carrier in Currier B","local_frame":"O/OT ladder, strongest for AR/AL-like hosts","right_family":"AIIN/AIR/AIN/AR/AL and related renderer choices; AIR enriched in HB/S","record_close":"source-native final B3 probabilistic marker","surface":"source separators retained; join/split renderer remains unconfirmed"},"provisional_semantic_layer":{"AR":"local association/reference lead only","PAGE_HOST":"technical content/referent placeholder","all_other_components":"UNASSIGNED"},"rejected_or_downgraded":{"q_as_free_scope_operator":"host licensing dominates","DY_as_line_closer":"B3 is the stronger physical-record closer; DY is internal phase/checkpoint","KAIIN_as_content_core":"matched family tests fail","OKAIR_as_indivisible_core":"AIR selection generalizes across bases","CKHY_parallel_fused_gloss":"failed second prospective transfer","physical_module_boundary":"unconfirmed"},"f84r":"SEALED_NOT_ACCESSED"}
 MODEL.write_text(json.dumps(model,indent=2,sort_keys=True)+"\n")
 decision="HPR2_LAYERED_TECHNICAL_RECORD_COMPILER_SELECTED_WITH_CONTENT_UNGROUNDED"
 report=f"""# GDT051 — revised hybrid register compiler

## Outcome

**{decision}**

The strongest current generative theory remains hybrid rather than ordinary
plaintext or pure notation, but HPR-2 is materially stricter than HPR-1:

```text
LINE  := OPEN? FIELD (DY FIELD)* CLOSE?
FIELD := WRAPPER? INNER_D? LOCAL_FRAME? PAGE_HOST RIGHT_FAMILY?
OPEN  := weak Q2 class
CLOSE := probabilistic source-native B3 class
```

The manuscript behaves like a layered technical record compiler. Physical
lines reset records. DY is an internal checkpoint/field transition, not the
best line terminator. B3 is the first strongly transferable physical-record
closing class. CH/CHE/SH and Q/L branches are host/register-licensed renderers,
not freely interchangeable morphemes. Carrier+D is a genuine nested stack but
has no recovered local function. AIR is a reusable HB/S right-family choice,
not an OKAIR-specific meaning. Page-local hosts remain the likely content
layer, yet none has a transferred concrete referent.

## What this explains

- dense Currier-B field chaining and sparse Currier-A chaining;
- Currier A `EO` versus Currier B `E` closure realization;
- free/bound surface reuse without requiring ordinary word boundaries;
- repeated carrier+host constructions and host-licensed q/L branches;
- why B/S share forms while wrapper and right-family choices still differ;
- why string models predict transformations: much of the renderer is local;
- why simple language/cipher maps fail: visible groups mix record state,
  rendering, and page-local content.

## What remains awkward

The content layer is still ungrounded. AR has only a postselected relational
lead; CKHY's concrete gloss failed; OKAIR and KAIIN do not yield meanings; and
no confirmed physical module boundary exists. The global nonsemantic models
remain stronger than every complete semantic decoder. HPR-2 is therefore the
best abductive architecture, not a decipherment.

Six new non-f84 predictions are frozen. The highest-value next test is P02:
whether B3-ended lines have a transferable internal-DY field-count profile
after register, folio, and length control. That tests the record compiler's
hierarchy without inventing a word meaning.

No word, morpheme, POS, sound, language, plaintext, concrete meaning, or
translation is established. f84r was skipped before inventory retention and
was not opened, retained, queried, joined, scored, or used as a prediction
target.
""";REPORT.write_text(report,encoding="utf-8")
 result={"schema":"GDT051_REVISED_HPR2_COMPILER_RESULT_V1","status":decision,"component_count":len(components),"representative_parse_count":len(parses),"prediction_count":len(predictions),"leading_theory":model["leading_theory"],"claim_ceiling":"Selected abductive layered record architecture; content and semantic functions remain ungrounded; no word, morpheme, POS, sound, language, plaintext, concrete meaning, or translation.","f84r":{"opened":False,"retained":False,"queried":False,"joined":False,"scored":False,"prediction_target":False},"inputs":{name:sha(ROOT/name)for name in INPUTS}|{SOURCE.name:sha(SOURCE)},"implementation":{Path(__file__).name:sha(Path(__file__))},"outputs":{MODEL.name:sha(MODEL),COMP.name:sha(COMP),PARSES.name:sha(PARSES),PRED.name:sha(PRED)},"documents":{METHOD.name:sha(METHOD),REPORT.name:sha(REPORT)}};result["result_content_sha256"]=csha(result);RESULT.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n");print(json.dumps({"status":decision,"components":len(components),"parses":len(parses),"predictions":len(predictions)},sort_keys=True))
if __name__=="__main__":main()
