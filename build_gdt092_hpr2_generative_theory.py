#!/usr/bin/env python3
"""Build the GDT092 HPR2 generative theory synthesis."""
from __future__ import annotations
import csv,hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parent;METHOD=ROOT/"GDT092_HPR2_GENERATIVE_THEORY_METHOD.md";REPORT=ROOT/"GDT092_HPR2_GENERATIVE_THEORY_REPORT.md";COMP=ROOT/"gdt092_component_model.tsv";THEORIES=ROOT/"gdt092_theory_comparison.tsv";PRED=ROOT/"gdt092_novel_predictions.tsv";MODEL=ROOT/"gdt092_generative_model.json";RESULT=ROOT/"gdt092_result.json"
INPUTS=("gdt003_nested_result.json","gdt056_result.json","gdt060_result.json","gdt062_result.json","gdt067_result.json","gdt077_result.json","gdt083_result.json","gdt085_result.json","gdt087_result.json","gdt089_result.json","gdt090_result.json","gdt091_result.json")
def write(p,rows,fields):
 with p.open("w",encoding="utf-8",newline="") as h:w=csv.DictWriter(h,fieldnames=fields,delimiter="\t",lineterminator="\n");w.writeheader();w.writerows(rows)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def csha(v):return hashlib.sha256(json.dumps(v,sort_keys=True,ensure_ascii=True,separators=(",",":")).encode()).hexdigest()
def main():
 prior={n:json.loads((ROOT/n).read_text()) for n in INPUTS};assert all(not any(x.get("f84r",{}).values()) for x in prior.values() if isinstance(x.get("f84r"),dict))
 components=[
 {"component":"PAGE_PROFILE","formal_generation":"selects page-local host inventory and register/compiler ecology","evidence":"GDT082/GDT083 page signal; Currier/register architecture","counterevidence":"compiler-only also page-clusters","status":"STRONG_FORMAL_PAGE_STATE_CONTENT_UNPROVEN","semantic_role":"UNASSIGNED"},
 {"component":"PAGE_HOST","formal_generation":"reusable lexical-like content candidate after wrapper/frame stripping","evidence":"page gain exceeds raw/residual; DARK_LEAF +4.342 held bits while raw/compiler negative","counterevidence":"broad cross-section behavior transfer fails; exact visual bundles unstable","status":"PROVISIONAL_CONTENT_LAYER","semantic_role":"UNASSIGNED"},
 {"component":"BASE_O_Y","formal_generation":"first PAGE_HOST coordinate licensing wrapper branch","evidence":"GDT085 held-host wrapper factor; GDT087 4641-group transfer","counterevidence":"does not independently predict right family, position, register or DY","status":"STRONG_FORMAL_COORDINATE","semantic_role":"UNASSIGNED"},
 {"component":"Q_WRAPPER","formal_generation":"early wrapper strongly licensed before O-base PAGE_HOST","evidence":"+122.330 held bits; 1746/3436 O versus 42/1205 Y; placement p=.00110","counterevidence":"ordinary host spelling can encode the same constraint; no meaning","status":"STRONG_FORMAL_OPERATOR","semantic_role":"UNASSIGNED"},
 {"component":"D_WRAPPER","formal_generation":"late wrapper preferentially licensed before Y-base PAGE_HOST","evidence":"+65.082 held bits; 106/1205 Y versus 14/3436 O; matched late shift p=.0483","counterevidence":"sparse relative to q; earlier global entry description was host-mixed","status":"PROVISIONAL_FORMAL_OPERATOR","semantic_role":"UNASSIGNED"},
 {"component":"CH_CHE_SH_S_WRAPPERS","formal_generation":"host/register-conditioned construction wrappers","evidence":"cross-core reuse and conditional wrapper gains","counterevidence":"direction reverses in at least one register; no universal function","status":"CONDITIONAL_RENDERERS_OR_OPERATORS","semantic_role":"UNASSIGNED"},
 {"component":"LOCAL_O_OT_FRAME","formal_generation":"changes record placement while often preserving PAGE_HOST","evidence":"GDT065 cross-frame page-context preservation","counterevidence":"function and semantic neutrality unresolved","status":"PROVISIONAL_LOCAL_FRAME","semantic_role":"UNASSIGNED"},
 {"component":"RIGHT_FAMILY","formal_generation":"host/register-conditioned terminal renderer from AIIN/AIR/AIN/AR/AL/NONE","evidence":"GDT062 transferable register conditioning; GDT077 asymmetric wrapper conditioning","counterevidence":"GDT085 exact host identity still required; independent content neutrality unproved","status":"STRONG_RENDERER_CONTENT_NEUTRALITY_UNPROVEN","semantic_role":"UNASSIGNED"},
 {"component":"DY_CHECKPOINT","formal_generation":"marks a field boundary/closure and shifts following distribution","evidence":"boundary association and late placement","counterevidence":"PAGE_HOST transition generalization fails; not a productive linguistic suffix above strings","status":"FORMAL_BOUNDARY_NOT_SEMANTIC_SUFFIX","semantic_role":"UNASSIGNED"},
 {"component":"B3_CLOSE","formal_generation":"rare closing state retained as compiler feature","evidence":"line/field closure concentration","counterevidence":"GDT067 internal content-neutrality prediction not supported","status":"FORMAL_CLOSE_CONTENT_NEUTRALITY_FAILED_OR_UNPROVEN","semantic_role":"UNASSIGNED"},
 {"component":"OS_HOST_SEED","formal_generation":"exact PAGE_HOST reused under ch/che and DY variation","evidence":"two strict plant labels both DARK_LEAF and LIGHT_ROOT; PAGE_HOST descriptor model positive","counterevidence":"two scored loci; global maxT fails; whole descriptor stability not above control","status":"WEAK_POSTSELECTED_VISUAL_ASSOCIATION","semantic_role":"UNASSIGNED"}]
 theories=[
 {"theory":"COMPRESSED_ABBREVIATED_NATURAL_LANGUAGE","rank":2,"fit_score_0_to_10":5,"explains":"reusable hosts; free/bound reuse; local visual signal","fails_or_strains":"extreme host-conditioned wrapper legality; page compiler; right renderers; GDT003 baselines"},
 {"theory":"PURE_SEMANTIC_OR_TECHNICAL_NOTATION","rank":3,"fit_score_0_to_10":4,"explains":"record states; line reset; wrapper/right templates; diagram labels","fails_or_strains":"large reusable page-local host vocabulary; prose/label reuse; descriptor-specific PAGE_HOST signal"},
 {"theory":"HYBRID_CONTENT_LEXICON_PLUS_ABBREVIATION_AND_RECORD_COMPILER","rank":1,"fit_score_0_to_10":8,"explains":"PAGE_HOST vocabulary plus formal wrappers/frames/renderers/boundaries and register shifts","fails_or_strains":"semantic hosts not stable enough for glosses; compiler also page-clusters; GDT003 remains negative"}]
 predictions=[
 {"prediction_id":"HPR2G_P01","target":"FUTURE_NON_F84_STRICT_PLANT_LABEL_WITH_EXACT_PAGE_HOST_OS","prediction":"human description contains both DARK_LEAF and LIGHT_ROOT neutral attributes","success":"both attributes present without redefining regex or PAGE_HOST","failure":"either attribute absent","status":"FROZEN_NOT_RUN"},
 {"prediction_id":"HPR2G_P02","target":"SOURCE_ONLY_O_Y_MATCHED_TAILS_NOT_USED_BY_GDT087","prediction":"q rate O>Y and d rate Y>O after register control","success":"both directions positive on held tails and folios","failure":"either direction nonpositive","status":"FROZEN_NOT_RUN"},
 {"prediction_id":"HPR2G_P03","target":"SOURCE_ONLY_NEW_O_Y_MATCHED_TAILS","prediction":"q+O is earlier and d+Y later than bare matched hosts","success":"combined opposing position statistic positive","failure":"combined statistic nonpositive","status":"FROZEN_NOT_RUN"},
 {"prediction_id":"HPR2G_P04","target":"FRESH_NON_F84_EXTERNAL_CONTENT_PANEL","prediction":"PAGE_HOST representation beats RAW and COMPILER_ONLY for at least one frozen neutral content axis","success":"positive selector-paid held gain and same direction on multiple folios","failure":"raw or compiler equals/exceeds PAGE_HOST","status":"FROZEN_NOT_RUN"},
 {"prediction_id":"HPR2G_P05","target":"FRESH_NON_F84_SAME_HOST_DIFFERENT_WRAPPER_OR_RIGHT_PANEL","prediction":"frozen content association follows PAGE_HOST rather than wrapper/right renderer","success":"same-host association transfers across compiler variants","failure":"association follows wrapper/right or disappears","status":"FROZEN_NOT_RUN"},
 {"prediction_id":"HPR2G_P06","target":"FRESH_NON_F84_EXTERNAL_PANEL_B3_NEGATIVE_CONTROL","prediction":"B3 adds no external content signal after PAGE_HOST and position","success":"B3 gain <= paid complexity","failure":"stable positive B3 gain","status":"FROZEN_NOT_RUN"}]
 model={"schema":"GDT092_HPR2_GENERATIVE_MODEL_V1","leading_theory":"HYBRID_CONTENT_LEXICON_PLUS_ABBREVIATION_AND_RECORD_COMPILER","grammar":{"MANUSCRIPT":"REGISTER_BLOCK+","PAGE":"PAGE_PROFILE LOCAL_HOST_LEXICON LINE+","LINE":"ENTRY_STATE? FIELD (DY_CHECKPOINT FIELD)* B3_CLOSE?","FIELD":"OUTER_WRAPPER? LOCAL_O_OT_FRAME? PAGE_HOST RIGHT_FAMILY?","OUTER_WRAPPER_COMPATIBILITY":{"Q":"O_BASE; EARLY","D":"Y_BASE; LATE","CH_CHE_SH_S":"HOST_AND_REGISTER_CONDITIONAL"},"PAGE_HOST":"OPAQUE_HOST | BASE_O_Y + TAIL_OR_TERMINAL","RIGHT_FAMILY":"render(PAGE_HOST,REGISTER,WRAPPER) in {AIIN,AIR,AIN,AR,AL,NONE}"},"theory_type":"HYBRID","translation_readiness":"NOT_READY_HOST_CONTENT_CLASSES_REQUIRE_INDEPENDENT_TRANSFER","semantic_assignments":[] ,"f84r":"SEALED_NO_PREDICTION"}
 write(COMP,components,list(components[0]));write(THEORIES,theories,list(theories[0]));write(PRED,predictions,list(predictions[0]));MODEL.write_text(json.dumps(model,indent=2,sort_keys=True)+"\n")
 REPORT.write_text("""# GDT092 — strongest current HPR2 generative theory

## Leading theory

**HYBRID CONTENT LEXICON + ABBREVIATION + RECORD COMPILER**

Voynichese is best modeled as a page-conditioned technical record system.  A
PAGE_HOST sequence supplies the lexical-like local vocabulary.  Formal layers
select construction branches, record placement, rendering, and boundaries.
This is more coherent than ordinary compressed natural language alone and
more coherent than pure notation alone.

```text
PAGE := PAGE_PROFILE + LOCAL_HOST_LEXICON + LINE+
LINE := ENTRY? FIELD (DY_CHECKPOINT FIELD)* B3_CLOSE?
FIELD := OUTER_WRAPPER? LOCAL_O_OT_FRAME? PAGE_HOST RIGHT_FAMILY?

OUTER_WRAPPER:
    q -> O-base host, early
    d -> Y-base host, late
    ch/che/sh/s -> host/register conditional

PAGE_HOST := opaque host | O/Y base + tail/terminal
RIGHT_FAMILY := render(PAGE_HOST, register, wrapper)
```

This explains free/bound reuse: the same host may appear bare, wrapped, or
right-rendered because the host and compiler layers are distinct.  It explains
the dense q-X families without treating q as a sound or lexical morpheme.  It
explains Currier/register effects as compiler-profile shifts, line reset as
record serialization, DY as a field checkpoint, and repeated labels as reuse
of content hosts under different renderings.

The theory remains awkward in three places.  GDT003 transformation completion
does not beat string statistics.  Compiler-only features themselves cluster
by page.  Exact PAGE_HOSTs do not yet preserve complete visual-property
bundles; the strongest content seed (`os` with DARK_LEAF/LIGHT_ROOT) has only
two scored loci and fails global correction.  Therefore the model is explicit
enough to predict, but not ready to translate.

Six non-f84 predictions are frozen.  f84r remains completely sealed and no
f84r prediction is made here.
""",encoding="utf-8")
 status="HYBRID_PAGE_HOST_LEXICON_PLUS_RECORD_COMPILER_IS_LEADING_GENERATIVE_THEORY"
 result={"schema":"GDT092_HPR2_GENERATIVE_THEORY_RESULT_V1","status":status,"leading_theory":model["leading_theory"],"components":len(components),"novel_predictions":len(predictions),"semantic_assignments":0,"translation_readiness":model["translation_readiness"],"claim_ceiling":"Explicit abductive formal generator and testable latent-function predictions; no word, gloss, morpheme, POS, sound, language, plaintext, translation, authorship, or origin.","f84r":{"opened":False,"retained":False,"queried":False,"joined":False,"scored":False,"targeted":False,"prediction_made":False},"inputs":{n:sha(ROOT/n) for n in INPUTS},"implementation":{Path(__file__).name:sha(Path(__file__))},"outputs":{COMP.name:sha(COMP),THEORIES.name:sha(THEORIES),PRED.name:sha(PRED),MODEL.name:sha(MODEL)},"documents":{METHOD.name:sha(METHOD),REPORT.name:sha(REPORT)}};result["result_content_sha256"]=csha(result);RESULT.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n");print(json.dumps({"status":status,"leading":model["leading_theory"],"components":len(components),"predictions":len(predictions)},sort_keys=True))
if __name__=="__main__":main()
