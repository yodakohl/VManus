#!/usr/bin/env python3
"""Build the post-GDT297 operational grammar revision."""
from __future__ import annotations
import csv,hashlib,json
from pathlib import Path
R=Path(__file__).resolve().parent;METHOD=R/'GDT298_LEXICALIZED_HYBRID_GRAMMAR_REVISION_METHOD.md';REPORT=R/'GDT298_LEXICALIZED_HYBRID_GRAMMAR_REVISION_REPORT.md';MODEL=R/'gdt298_operational_grammar_v2.json';PRED=R/'gdt298_prediction_audit.tsv';COMP=R/'gdt298_model_comparison.tsv';RESULT=R/'gdt298_result.json'
INPUTS=['gdt165_result.json','gdt169_result.json','gdt276_result.json','gdt278_result.json','gdt288_result.json','gdt289_result.json','gdt290_result.json','gdt292_result.json','gdt293_result.json','gdt294_result.json','gdt295_result.json','gdt296_result.json','gdt297_result.json']
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def ch(v):return hashlib.sha256(json.dumps(v,sort_keys=True,ensure_ascii=True,separators=(',',':')).encode()).hexdigest()
def rch(v):q=dict(v);q.pop('content_sha256',None);return ch(q)
def f84_safe(d):
 f=d.get('f84',d.get('f84r',{}))
 return all(not f.get(k,False) for k in ('opened','parsed','retained','joined','scored','tuned','used','image_access','retained_joined_scored_rows','source_f84r_rows'))
def write(p,rows):
 with Path(p).open('w',encoding='utf8',newline='') as h:w=csv.DictWriter(h,rows[0].keys(),delimiter='\t',lineterminator='\n');w.writeheader();w.writerows(rows)
def main():
 data={x:json.loads((R/x).read_text()) for x in INPUTS};assert all(f84_safe(d) for d in data.values())
 predictions=[
 {'prediction_id':'GDT288_P01','original_prediction':'low-complexity position-conditioned wrapper rule transfers across held hosts','outcome':'FAILED','evidence':'GDT289 cross-host gain -0.1790; GDT290 K2/K4/K8 all negative','revision':'no compact universal or small latent renderer class'},
 {'prediction_id':'GDT288_P02','original_prediction':'RIGHT_FAMILY predicts closure after host and slot','outcome':'WEAK_OR_FAILED','evidence':'GDT292 absolute gain -0.00759 and smoothing sign change','revision':'right/closure association is local or lexicalized'},
 {'prediction_id':'GDT288_P03','original_prediction':'exact host improves same-group completion but not NEXT_HOST','outcome':'FORMAL_HALF_SUPPORTED_CAUSAL_READING_FAILED','evidence':'GDT293 +1.41487 bits/event and GDT165 NEXT_HOST negative; GDT297 59/59 within-host renderer/raw bijections','revision':'completion is high-capacity whole-form alternant memory, not independent host-to-renderer causation'},
 {'prediction_id':'GDT288_P04','original_prediction':'homologous referents preserve full tuple better than exact surface','outcome':'NOT_SUPPORTED_CURRENT_PANEL','evidence':'GDT169 no replicated tuple invariance and 0/5 owned exact host/tuple hits','revision':'requires genuinely new independent repeated referents'},
 {'prediction_id':'GDT288_P05','original_prediction':'historical technical shorthand approaches host-first contextual factorization','outcome':'NONUNIQUE','evidence':'GDT278 controls are order/matching sensitive; structured notation and Augsburg also prefer contextual host-first in GDT287','revision':'factorization does not identify historical architecture'},
 {'prediction_id':'GDT288_P06','original_prediction':'future key decodes latent payload while leaving compiler many-to-one','outcome':'UNTESTED','evidence':'zero admissible plaintext or repeated-referent key','revision':'retain only as a requirement on any future decipherment'}]
 comparisons=[
 {'rank':1,'world':'LEXICALIZED_HYBRID_RECORD_SHORTHAND','fit':'BEST_CURRENT_COHERENCE','explains':'physical record grammar; compiler-conditioned character form; whole-form alternants; register effects','fails_or_unknown':'latent payload and historical implementation unidentified'},
 {'rank':2,'world':'ABBREVIATION_HEAVY_NATURAL_LANGUAGE','fit':'PLAUSIBLE_COMPONENT','explains':'GDT276 character-form MDL lead and high-capacity surface lexicon','fails_or_unknown':'Voynich wrapper profile and record architecture not reproduced uniquely by diplomatic controls'},
 {'rank':3,'world':'NONSEMANTIC_STRING_STATISTICAL_PROCESS','fit':'STRONG_ADVERSARIAL_NULL','explains':'GDT003 no gain beyond string statistics and local form similarity','fails_or_unknown':'does not explain independently confirmed document/record organization as communicative content'},
 {'rank':4,'world':'COMPACT_FACTORIAL_TECHNICAL_NOTATION','fit':'WEAK','explains':'record boundaries and reusable compiler coordinates','fails_or_unknown':'GDT289/290 compact renderer classes fail; exact hosts remain high-capacity'},
 {'rank':5,'world':'FIXED_LOCAL_CODEBOOK','fit':'WEAK','explains':'opaque recurrent identities','fails_or_unknown':'NEXT_HOST/external referent transfer and page codebook models fail'}]
 model={'schema':'GDT298_OPERATIONAL_GRAMMAR_V2','status':'LEXICALIZED_HYBRID_RECORD_SHORTHAND_LEADING_THEORY','epistemic_status':'YOLO_ABDUCTIVE_HYPOTHESIS_NOT_CONFIRMATION','leading_world':'REGISTER_CONDITIONED_LEXICALIZED_HYBRID_RECORD_SHORTHAND','generation_order':['PAGE_REGISTER','RECORD_TEMPLATE_AND_LINE_ENTRY_STATE','FIELD_OPPORTUNITY_AND_COARSE_POSITION','LATENT_PAYLOAD_OR_FORM_ENTRY_UNIDENTIFIED','JOINT_PAGE_HOST_PLUS_RENDERER_ALTERNANT','SHARED_COMPILER_CONSTRAINTS_AND_BACKOFF','DY_B3_OR_PHYSICAL_LINE_CLOSURE','VISIBLE_SOURCE_GROUP'],'probability_factorization':['P(record_template | page,register)','P(field_opportunity | template,physical_position)','P(joint_host_renderer_form | register,field_opportunity,record_state)','P(visible_group | joint_form)=1'],'shared_low_capacity_constraints':{'OUTER_WRAPPER':'transferable onset-heavy form channel; exact function unknown','O_OT_FRAME':'placement/rendering contrast','RIGHT_FAMILY':'local/lexicalized completion tendency, not independent closure predictor','DY_B3':'field/record segmentation coordinates, not meanings','LINE_RESET':'robust physical record organization'},'high_capacity_layer':{'JOINT_HOST_RENDERER_FORM':'surface lexicon/backoff state','PAGE_HOST':'analytical projection of joint form; content status ungrounded','renderer_independence':'NOT_ESTABLISHED','next_host_transfer':'NEGATIVE'},'resolved_gdt288_predictions':{x['prediction_id']:x['outcome'] for x in predictions},'semantic_assignments':0,'lexical_glosses':0,'page_host_substrings_mined':0,'f84':{'opened':False,'parsed':False,'retained':False,'joined':False,'scored':False}}
 MODEL.write_text(json.dumps(model,indent=2,sort_keys=True)+'\n');write(PRED,predictions);write(COMP,comparisons)
 REPORT.write_text('''# GDT298 — lexicalized hybrid grammar revision

Status: **LEXICALIZED_HYBRID_RECORD_SHORTHAND_LEADING_THEORY**.

This is the current executable YOLO theory, not a decipherment claim and not a
new manuscript score.

## Revised generator

```text
PAGE / REGISTER
  -> RECORD TEMPLATE + LINE-ENTRY STATE
  -> FIELD OPPORTUNITY / COARSE POSITION
  -> UNKNOWN LATENT PAYLOAD OR FORM ENTRY
  -> JOINT (PAGE_HOST, RENDERER) SURFACE ALTERNANT
  -> SHARED WRAPPER / FRAME / EDGE / CLOSURE CONSTRAINTS AS BACKOFF
  -> VISIBLE SOURCE GROUP
```

The crucial change from GDT288 is that `PAGE_HOST -> renderer` is no longer a
claimed causal step. GDT297 shows a within-host bijection between every exact
renderer tuple and complete source form, while GDT289--290 fail to transfer a
compact renderer across unseen hosts. The safest executable representation is
therefore a high-capacity **joint form lexicon** constrained by reusable record
and graphematic tendencies.

## What remains genuinely reusable

- Physical lines, line reset, field chaining, and record/paragraph opportunity
  remain the strongest low-capacity architecture.
- The outer-wrapper channel transfers across folios, sections, hands, and
  unseen host buckets, but it is a formal onset constraint rather than a
  translated prefix.
- O/OT, RIGHT_FAMILY, DY, and B3 remain useful parser coordinates; none has an
  independently established meaning.
- Compiler-conditioned PAGE_HOST character form is the best held-folio MDL
  channel, but calibration does not distinguish language, abbreviation,
  notation, or code.
- Exact same-group completion is strong; immediate next-host and repeated-
  referent invariance are not.

## Theory ranking

| rank | world | current fit |
|---:|---|---|
| 1 | lexicalized hybrid record shorthand | best current coherence |
| 2 | abbreviation-heavy natural language | plausible payload/rendering component |
| 3 | nonsemantic string-statistical process | mandatory strong adversarial null |
| 4 | compact factorial technical notation | too low-capacity for observed host-specific rendering |
| 5 | fixed local codebook | transfer and referent failures |

## Translation consequence

A future translation attempt should not begin by assigning meanings to stripped
PAGE_HOSTs. It needs an independent repeated content endpoint and must compare
three units simultaneously: complete source form, parsed joint form state, and
PAGE_HOST projection. A meaning that follows only the stripped host is no
longer the default prediction.

The next decisive formal success would be a renderer alternant predicted for a
genuinely unseen host without character-substring tuning. The next decisive
semantic success would be an independently repeated referent whose joint form
distribution transfers across folios. Neither currently exists.

## Claim ceiling

This selects a formal working architecture only. It supplies no word,
morpheme, code value, sound, language, meaning, plaintext, translation,
authorship, or origin. No f84 material was accessed.
''')
 outputs=[MODEL,PRED,COMP,REPORT];result={'schema':'GDT298_LEXICALIZED_HYBRID_GRAMMAR_REVISION_RESULT_V1','status':model['status'],'leading_world':model['leading_world'],'resolved_predictions':len(predictions),'prediction_outcomes':{x['outcome']:sum(y['outcome']==x['outcome'] for y in predictions) for x in predictions},'worlds_ranked':len(comparisons),'new_manuscript_scores':0,'semantic_assignments':0,'lexical_glosses':0,'page_host_substrings_mined':0,'interpretation':'Shared record/compiler constraints plus a high-capacity joint host-renderer surface lexicon is the strongest current generator.','claim_ceiling':'Formal abductive architecture only; no word morpheme code value sound language meaning plaintext translation authorship or origin.','f84':model['f84'],'inputs':{x:sha(R/x) for x in INPUTS},'documents':{METHOD.name:sha(METHOD),REPORT.name:sha(REPORT)},'implementation':{Path(__file__).name:sha(Path(__file__))},'outputs':{x.name:sha(x) for x in outputs}};result['content_sha256']=rch(result);RESULT.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n');print(json.dumps({'status':result['status'],'predictions':len(predictions),'worlds':len(comparisons)},sort_keys=True))
if __name__=='__main__':main()
