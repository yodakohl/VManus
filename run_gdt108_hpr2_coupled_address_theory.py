#!/usr/bin/env python3
"""GDT108: synthesize the coupled content-address + relation-renderer theory."""
import csv,hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parent;METHOD=ROOT/"GDT108_HPR2_COUPLED_ADDRESS_THEORY_METHOD.md";REPORT=ROOT/"GDT108_HPR2_COUPLED_ADDRESS_THEORY_REPORT.md";MODEL=ROOT/"gdt108_hpr2_coupled_address_model.json";COMP=ROOT/"gdt108_component_status.tsv";THEORY=ROOT/"gdt108_theory_comparison.tsv";PRED=ROOT/"gdt108_novel_predictions.tsv";RESULT=ROOT/"gdt108_result.json"
INPUTS=["gdt003_nested_result.json","gdt100_result.json","gdt101_result.json","gdt102_result.json","gdt103_result.json","gdt104_result.json","gdt105_result.json","gdt106_result.json","gdt107_result.json"]
def write(p,rows,fields):
 with p.open("w",encoding="utf-8",newline="") as h:w=csv.DictWriter(h,fieldnames=fields,delimiter="\t",lineterminator="\n");w.writeheader();w.writerows(rows)
def read(p):
 with p.open(encoding="utf-8",newline="") as h:return list(csv.DictReader(h,delimiter="\t"))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def csha(x):return hashlib.sha256(json.dumps(x,sort_keys=True,ensure_ascii=True,separators=(",",":")).encode()).hexdigest()
def main():
 bound={name:json.loads((ROOT/name).read_text()) for name in INPUTS};assert all(not any(x.get("f84r",{}).values()) for x in bound.values());components=[
 {"component":"PHYSICAL_LINE","layer":"RECORD_SERIALIZATION","status":"STRONG_FORMAL","provisional_function":"line-reset record unit","support":"confirmed line reset and directional within-line coordinate","counterevidence":"not a decoded sentence"},
 {"component":"PAGE_ADDRESS_INVENTORY","layer":"PAGE_PROFILE","status":"STRONG_FORMAL","provisional_function":"page-conditioned address vocabulary","support":"held page-local PAGE_HOST inventory","counterevidence":"page topic/meaning unproved"},
 {"component":"FULL_PAGE_HOST","layer":"CONTENT_ADDRESS","status":"PROVISIONAL_EXTERNAL_LEAD","provisional_function":"coupled object/content address","support":"GDT103 +61.849 object-axis bits and GDT106 full-host representation winner","counterevidence":"archive exposed; broad exact-host bundles and cross-section transfer fail"},
 {"component":"EDGE_STRIPPED_CORE","layer":"ADDRESS_CORE","status":"NOT_INDEPENDENTLY_SUPPORTED","provisional_function":"latent reusable core inside address","support":"formal split/join and dense families","counterevidence":"GDT106 stripping destroys signal; GDT107 object preservation p=.536"},
 {"component":"FINAL_CHARACTER","layer":"EDGE_STATE","status":"STRONG_FORMAL_COUPLED","provisional_function":"renderer-licensing address edge","support":"GDT105 15561.557 held-bit gain; all folios/registers; non-PCH to PCH transfer","counterevidence":"parser overlap; cannot be removed from external address"},
 {"component":"Q_WRAPPER","layer":"OUTER_ROUTER","status":"STRONG_FORMAL","provisional_function":"early O-branch router","support":"GDT086/087/091/094","counterevidence":"identical to first-character string baseline; no meaning"},
 {"component":"D_WRAPPER","layer":"OUTER_ROUTER","status":"STRONG_FORMAL","provisional_function":"late Y-branch router","support":"GDT087/091/094","counterevidence":"no global entry gloss; no meaning"},
 {"component":"CH_CHE_SH_S","layer":"OUTER_OR_LOCAL_ROUTER","status":"CONDITIONAL","provisional_function":"host/register-conditioned construction wrapper","support":"cross-core compatibility and register effects","counterevidence":"directions reverse; GDT103 object signal diluted"},
 {"component":"O_OT_FRAME","layer":"POSITION_FRAME","status":"FORMAL_PLACEMENT","provisional_function":"record placement/frame variant","support":"placement differences with address preservation leads","counterevidence":"GDT103 object signal diluted; external preservation weak"},
 {"component":"DY","layer":"RELATION_RENDERER","status":"PROVISIONAL_RELATION_LAYOUT","provisional_function":"checkpoint/link carrying relation-layout information","support":"GDT103/GDT104 +10.319 relation-axis bits and near-zero object increment","counterevidence":"GDT060 pre-host transition negative; ordinary final-character licensing"},
 {"component":"RIGHT_FAMILY","layer":"RELATION_REGISTER_RENDERER","status":"STRONG_FORMAL_PROVISIONAL_RELATION","provisional_function":"host/register-conditioned relation-layout renderer","support":"GDT062 held register gain; GDT104 +7.907 relation and -4.715 object bits","counterevidence":"specific right-family role/gloss absent"},
 {"component":"B3","layer":"RECORD_CLOSE","status":"PROVISIONAL_NEUTRAL_CLOSE","provisional_function":"content-neutral record close","support":"final architecture; GDT103 active-only near zero on both channels","counterevidence":"categorical zero-token encoding artifact; limited positive capacity"},
 {"component":"PCH_FAMILY","layer":"DENSE_ADDRESS_FAMILY","status":"STRONG_FORMAL_POSTSELECTED","provisional_function":"dense coupled address family","support":"18/18 inspected cells, 45/45 rectangles, 45 folios","counterevidence":"only 181/331 PCH groups; prefix-tail dependent; GDT003 string ceiling; no gloss"},
 {"component":"SEMANTIC_DICTIONARY","layer":"GROUNDING","status":"ABSENT","provisional_function":"NONE","support":"no confirmed entry","counterevidence":"all transferable individual gloss attempts fail/weak"},
 ];write(COMP,components,list(components[0]));criteria=("formal_composition","page_inventory","external_object_channel","record_architecture","register_rendering","free_bound_reuse","directional_adjacency","edge_grammar","semantic_transfer","historical_plausibility");theories=[
 {"theory":"HYBRID_COUPLED_CONTENT_ADDRESS_PLUS_RELATION_RENDERER","formal_composition":1,"page_inventory":1,"external_object_channel":1,"record_architecture":1,"register_rendering":1,"free_bound_reuse":1,"directional_adjacency":1,"edge_grammar":1,"semantic_transfer":0,"historical_plausibility":1,"major_failure":"no stable semantic dictionary; string baseline ceiling"},
 {"theory":"COMPRESSED_ABBREVIATED_NATURAL_LANGUAGE","formal_composition":1,"page_inventory":1,"external_object_channel":1,"record_architecture":0,"register_rendering":1,"free_bound_reuse":1,"directional_adjacency":1,"edge_grammar":0,"semantic_transfer":0,"historical_plausibility":1,"major_failure":"does not naturally explain extreme edge-renderer determinism or baseline failures"},
 {"theory":"PURE_SEMANTIC_TECHNICAL_NOTATION","formal_composition":1,"page_inventory":1,"external_object_channel":1,"record_architecture":1,"register_rendering":1,"free_bound_reuse":0,"directional_adjacency":0,"edge_grammar":1,"semantic_transfer":0,"historical_plausibility":1,"major_failure":"underexplains language-like free/bound reuse and directional partner structure"},
 ]
 for x in theories:x["criteria_score"]=sum(int(x[k]) for k in criteria);x["rank"]=""
 theories.sort(key=lambda x:(-x["criteria_score"],x["theory"]));
 for i,x in enumerate(theories,1):x["rank"]=i
 write(THEORY,theories,list(theories[0]));preds=[
 {"prediction_id":"HPR2V3_P01","scope":"FRESH_NON_F84_EXTERNAL_PANEL","prediction":"FULL_PAGE_HOST beats RAW/COMPILER primarily on predeclared object/content axes","failure":"selector-paid object-axis margin <=0","status":"FROZEN_NOT_RUN","semantic_role":"UNASSIGNED"},
 {"prediction_id":"HPR2V3_P02","scope":"FRESH_NON_F84_EXTERNAL_PANEL","prediction":"DY and RIGHT additions improve relation/layout axes more than object axes","failure":"relation-minus-object increment <=0 for either layer","status":"FROZEN_NOT_RUN","semantic_role":"UNASSIGNED"},
 {"prediction_id":"HPR2V3_P03","scope":"FRESH_NON_F84_EXTERNAL_PANEL","prediction":"B3 adds no material object or relation signal after full PAGE_HOST","failure":"absolute four-axis increment >=4 bits","status":"FROZEN_NOT_RUN","semantic_role":"UNASSIGNED"},
 {"prediction_id":"HPR2V3_P04","scope":"NEW_NON_PCH_FORMAL_FAMILY","prediction":"final PAGE_HOST character predicts renderer state across unseen cores and folios","failure":"final-character code fails to beat exact-host/backoff","status":"FROZEN_NOT_RUN","semantic_role":"UNASSIGNED"},
 {"prediction_id":"HPR2V3_P05","scope":"FRESH_EXTERNAL_EDGE_VARIANTS","prediction":"complete PAGE_HOST is more externally stable than PAGE_HOST-minus-final core","failure":"stripped core wins after matched folds and selector","status":"FROZEN_NOT_RUN","semantic_role":"UNASSIGNED"},
 {"prediction_id":"HPR2V3_P06","scope":"FRESH_RECORD_ARRAYS","prediction":"DY/RIGHT variation tracks relation/layout contrast while repeated full hosts preserve object axis","failure":"opposite channel decomposition or no within-array contrast","status":"FROZEN_NOT_RUN","semantic_role":"UNASSIGNED"},
 {"prediction_id":"HPR2V3_P07","scope":"NEW_PAGE_BLOCK_NON_F84","prediction":"page-local full PAGE_HOST inventory improves sequential address prediction beyond router/register","failure":"gain vanishes under leave-one-page influence deletion","status":"FROZEN_NOT_RUN","semantic_role":"UNASSIGNED"},
 ];write(PRED,preds,list(preds[0]));model={"schema":"GDT108_HPR2_COUPLED_ADDRESS_MODEL_V1","name":"HYBRID_COUPLED_CONTENT_ADDRESS_PLUS_RELATION_RENDERER","leading_theory":theories[0]["theory"],"grammar":{"MANUSCRIPT":"REGISTER_BLOCK+","PAGE":"PAGE_PROFILE ADDRESS_INVENTORY RECORD+","RECORD":"ENTRY_ROUTER? FIELD (RELATION_LINK FIELD)* B3_CLOSE?","FIELD":"OUTER_ROUTER? POSITION_FRAME? CONTENT_ADDRESS RENDERER?","CONTENT_ADDRESS":"coupled(BRANCH?, ADDRESS_FAMILY, EDGE_STATE)","EDGE_STATE":"final PAGE_HOST character; licenses BARE | DY | RIGHT | DY_RIGHT | B3","OUTER_ROUTER":{"q":"O_BRANCH_EARLY","d":"Y_BRANCH_LATE","ch_che_sh_s":"HOST_REGISTER_CONDITIONAL"},"POSITION_FRAME":"O | OT | NONE","RELATION_LINK":"DY","RENDERER":"RIGHT_FAMILY(register,address,edge)","B3":"PROVISIONAL_CONTENT_NEUTRAL_CLOSE"},"representative_formal_parses":[{"locus":"f104r.1","token":"qopchedy","parse":"q[OUTER_ROUTER] + opch[ADDRESS_FAMILY] + e[EDGE_STATE] + DY[RELATION_LINK]"},{"locus":"f104r.27","token":"pchedar","parse":"pch[ADDRESS_FAMILY] + d[EDGE_STATE] + ar[RIGHT_FAMILY]"},{"locus":"f40r.1","token":"pchey","parse":"pch[ADDRESS_FAMILY] + ey[COUPLED_EDGE_VARIANT] + BARE"},{"locus":"f105v.1","token":"ypcheddy","parse":"y+pch[COUPLED_ADDRESS] + ed[EDGE_VARIANT] + DY[RELATION_LINK]"},{"locus":"f105r.13","token":"dyteey","parse":"d[OUTER_ROUTER] + yteey[COUPLED_ADDRESS] + BARE"}],"semantic_assignments":[],"translation_readiness":"NOT_READY_REQUIRES_FRESH_TWO_CHANNEL_EXTERNAL_TRANSFER","f84r":"SEALED_NO_PREDICTION"};MODEL.write_text(json.dumps(model,indent=2,sort_keys=True)+"\n");status="HYBRID_COUPLED_CONTENT_ADDRESS_PLUS_RELATION_RENDERER_IS_LEADING_THEORY"
 REPORT.write_text(f"""# GDT108 — HPR2 coupled-address theory revision

## Leading theory

**{status}**

The best current generator is a hybrid technical content-address system with
abbreviation-like formal reuse and a record/relation compiler. It scores
{theories[0]['criteria_score']}/10 on the explicit abductive criteria, versus
{theories[1]['criteria_score']} and {theories[2]['criteria_score']} for the
alternatives. These are transparent theory scores, not posterior probabilities.

## Explicit generator

```
PAGE   := PAGE_PROFILE ADDRESS_INVENTORY RECORD+
RECORD := ENTRY_ROUTER? FIELD (RELATION_LINK FIELD)* B3_CLOSE?
FIELD  := OUTER_ROUTER? POSITION_FRAME? CONTENT_ADDRESS RENDERER?
CONTENT_ADDRESS := coupled(BRANCH?, ADDRESS_FAMILY, EDGE_STATE)
```

`q` routes an early O branch; `d` routes a late Y branch. The final PAGE_HOST
character is a universal EDGE_STATE that predicts the renderer, but GDT106 and
GDT107 show it cannot be discarded to expose a stable semantic core. DY and
RIGHT_FAMILY are the best relation/layout channels; B3 is the best neutral
close. `PCH` is a dense address family, not a meaning.

Representative formal parses include `qopchedy = q + opch + e + DY`,
`pchedar = pch + d + RIGHT(ar)`, and `ypcheddy = y+pch+ed + DY`. These parses
are generator states, not pronunciations, morphemes, or translations.

## What it explains

- page-conditioned inventories and line reset;
- free/bound reuse and split/join behavior without requiring ordinary spaces;
- productive q/O and d/Y routing;
- strong Currier/register rendering changes;
- exact right-edge licensing of DY/RIGHT/bare states;
- PCH's complete but frequency-dependent factor grid;
- PAGE_HOST object-axis lead versus DY/RIGHT relation-axis lead;
- repeated labels as repeated addresses rather than necessarily repeated words;
- failure of simple language/cipher mappings and GDT003's string ceiling.

## Awkward facts

No individual address has a stable transferable gloss. Exact-host visual
bundles fail broadly, edge-stripped cores do not preserve object tags, PCH's
visual lead is domain-confined, and archived external effects remain
postselected. The same formal architecture can still be generated by a highly
regular nonsemantic source process. Seven new non-f84 predictions are frozen;
f84r receives none and remains untouched.
""",encoding="utf-8")
 result={"schema":"GDT108_HPR2_COUPLED_ADDRESS_THEORY_RESULT_V1","status":status,"leading_theory":theories[0]["theory"],"theory_scores":{x["theory"]:x["criteria_score"] for x in theories},"components":len(components),"predictions":len(preds),"semantic_assignments":0,"interpretation":"Explicit hybrid coupled-address and relation-renderer generator; strongest current path toward eventual grounding, still without a dictionary.","claim_ceiling":"Exploratory generative theory only; no confirmed word, morpheme, POS, sound, language, plaintext, role, gloss, meaning, or translation.","f84r":{"opened":False,"retained":False,"queried":False,"joined":False,"scored":False,"targeted":False,"prediction_made":False},"inputs":{name:sha(ROOT/name) for name in INPUTS},"implementation":{Path(__file__).name:sha(Path(__file__))},"outputs":{COMP.name:sha(COMP),THEORY.name:sha(THEORY),PRED.name:sha(PRED),MODEL.name:sha(MODEL)},"documents":{METHOD.name:sha(METHOD),REPORT.name:sha(REPORT)}};result["result_content_sha256"]=csha(result);RESULT.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n");print(json.dumps({"status":status,"theories":result["theory_scores"],"components":len(components),"predictions":len(preds)},sort_keys=True))
if __name__=="__main__":main()
