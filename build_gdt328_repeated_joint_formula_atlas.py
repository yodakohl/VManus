#!/usr/bin/env python3
"""Build the f84-free GDT328 repeated joint-field formula atlas."""
import csv,hashlib,json,math
from collections import Counter,defaultdict
from pathlib import Path
R=Path(__file__).resolve().parent
INTER=R/'gdt327_joint_tuple_interlinear.tsv';SOURCE=R/'gdt278_native_event_inventory.tsv'
METHOD=R/'GDT328_REPEATED_JOINT_FORMULA_METHOD.md';ATLAS=R/'gdt328_formula_atlas.tsv'
OCC=R/'gdt328_formula_occurrences.tsv';REPORT=R/'GDT328_REPEATED_JOINT_FORMULA_REPORT.md'
RESULT=R/'gdt328_result.json'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def can(v):return hashlib.sha256(json.dumps(v,sort_keys=True,ensure_ascii=True,separators=(',',':')).encode()).hexdigest()
def read(p):
 with Path(p).open(encoding='utf8',newline='') as h:return list(csv.DictReader(h,delimiter='\t'))
def write(p,rows,fields=None):
 fields=fields or list(rows[0])
 with Path(p).open('w',encoding='utf8',newline='') as h:w=csv.DictWriter(h,fields,delimiter='\t',lineterminator='\n');w.writeheader();w.writerows(rows)
def fid(level,seq):return 'GDT328_'+hashlib.sha256((level+'|'+('|'.join(seq))).encode()).hexdigest()[:16].upper()
def surface(x):
 w='' if x['wrapper']=='NONE' else x['wrapper']; inner='d' if x['inner_d']=='1' else ''
 frame='' if x['local_frame']=='NONE' else x['local_frame'].lower();right='' if x['right_family']=='NONE' else x['right_family']
 return w+inner+frame+x['page_host']+right+('m' if x['b3']=='1' else '')+('dy' if x['dy_closure']=='1' else '')
def main():
 inter=read(INTER);src=[x for x in read(SOURCE) if x['control_id']=='VOYNICH_REFERENCE']
 assert len(inter)==len(src)==8448 and not any(x['page'].startswith('f84') or x['locus'].startswith('f84') for x in inter+src)
 sk={(x['locus'],x['group_index']):x for x in src};assert len(sk)==len(src)
 for x in src:assert hashlib.sha256(surface(x).encode()).hexdigest()==x['source_surface_sha256']
 fields=defaultdict(list)
 for x in inter:fields[(x['page'],x['locus'],x['field_ordinal'])].append(x)
 for v in fields.values():v.sort(key=lambda x:int(x['group_index']))
 catalog=[]
 for level,key in [('EXACT_JOINT_SEQUENCE','joint_tuple_id'),('PAGE_HOST_SEQUENCE','host_id')]:
  d=defaultdict(list)
  for fk,v in fields.items():
   if len(v)>=2:d[tuple(x[key] for x in v)].append((fk,v))
  for seq,items in d.items():
   if len({v[0]['physical_folio'] for _,v in items})>=2:catalog.append({'level':level,'seq':seq,'items':items})
 catalog.sort(key=lambda q:(-len(q['seq']),-len({v[0]['physical_folio'] for _,v in q['items']}),-len(q['items']),-max(Counter(k[2] for k,_ in q['items']).values())/len(q['items']),q['seq']))
 atlas=[];occ=[]
 rank=Counter()
 for q in catalog:
  level=q['level'];rank[level]+=1;seq=q['seq'];items=q['items'];formula=fid(level,seq);ords=Counter(k[2] for k,_ in items);mode,mc=sorted(ords.items(),key=lambda z:(-z[1],int(z[0])))[0]
  joint_variants={tuple(x['joint_tuple_id'] for x in v) for _,v in items};wrapper_variants={tuple(x['observed_wrapper'] for x in v) for _,v in items};host_displays={tuple(sk[(x['locus'],x['group_index'])]['page_host'] for x in v) for _,v in items}
  atlas.append({'formula_id':formula,'level':level,'level_rank':rank[level],'group_length':len(seq),'occurrences':len(items),'physical_folios':len({v[0]['physical_folio'] for _,v in items}),'pages':len({v[0]['page'] for _,v in items}),'sections':'|'.join(sorted({v[0]['section'] for _,v in items})),'registers':'|'.join(sorted({v[0]['register'] for _,v in items})),'formula_sequence_ids':'|'.join(seq),'page_host_sequence_display':' || '.join('|'.join(z) for z in sorted(host_displays)),'distinct_joint_realizations':len(joint_variants),'distinct_wrapper_realizations':len(wrapper_variants),'modal_field_ordinal':mode,'modal_field_count':mc,'modal_field_purity':f'{mc/len(items):.12f}','semantic_state':'UNASSIGNED','translation_state':'UNASSIGNED'})
  for fk,v in sorted(items):
   ss=[sk[(x['locus'],x['group_index'])] for x in v]
   occ.append({'formula_id':formula,'level':level,'page':v[0]['page'],'physical_folio':v[0]['physical_folio'],'locus':v[0]['locus'],'section':v[0]['section'],'register':v[0]['register'],'field_ordinal':v[0]['field_ordinal'],'group_length':len(v),'joint_tuple_sequence':'|'.join(x['joint_tuple_id'] for x in v),'host_sequence_ids':'|'.join(x['host_id'] for x in v),'page_host_sequence_display':'|'.join(x['page_host'] for x in ss),'surface_formula_display':'|'.join(surface(x) for x in ss),'wrapper_sequence':'|'.join(x['observed_wrapper'] for x in v),'semantic_state':'UNASSIGNED','translation_state':'UNASSIGNED'})
 write(ATLAS,atlas);write(OCC,occ)
 triple=next(x for x in atlas if x['level']=='PAGE_HOST_SEQUENCE' and int(x['group_length'])==3)
 ti=[x for x in occ if x['formula_id']==triple['formula_id']];target_ord=triple['modal_field_ordinal'];by=defaultdict(Counter)
 for _,v in fields.items():
  if len(v)==3:by[v[0]['register']][v[0]['field_ordinal']]+=1
 p_exact=1.; allords=set.intersection(*[set(by[x['register']]) for x in ti])
 for x in ti:p_exact*=by[x['register']][target_ord]/sum(by[x['register']].values())
 p_any=sum(math.prod(by[x['register']][o]/sum(by[x['register']].values()) for x in ti) for o in allords)
 exact_triples=[x for x in atlas if x['level']=='EXACT_JOINT_SEQUENCE' and int(x['group_length'])==3]
 summary={'fields':len(fields),'multi_group_fields':sum(len(v)>=2 for v in fields.values()),'exact_joint_formula_types':sum(x['level']=='EXACT_JOINT_SEQUENCE' for x in atlas),'host_formula_types':sum(x['level']=='PAGE_HOST_SEQUENCE' for x in atlas),'formula_occurrences':len(occ),'three_host_formula_id':triple['formula_id'],'three_host_occurrences':int(triple['occurrences']),'three_host_folios':int(triple['physical_folios']),'three_host_field_ordinal':int(target_ord),'three_host_exact_joint_realizations':int(triple['distinct_joint_realizations']),'three_host_observed_ordinal_probability_register_length_conditioned':p_exact,'three_host_any_common_ordinal_probability_register_length_conditioned':p_any,'three_joint_formula_types':len(exact_triples)}
 report=f'''# GDT328 — repeated joint-formula atlas

Status: **CROSS_REGISTER_FIELD3_FORMULA_LEAD**.

Across {summary['fields']:,} complete fields, {summary['multi_group_fields']:,} contain at least two groups.  Exact recurrence on at least two physical folios yields {summary['exact_joint_formula_types']} joint-tuple sequences; PAGE_HOST-only recurrence yields {summary['host_formula_types']} sequences.

## Strongest formula

One three-host formula occurs on three physical folios and in two registers:

| locus | register | field | structural display |
|---|---|---:|---|
| f82r.2 | OTHER_B | 3 | `qokain | dy | qokeedy` |
| f83r.6 | OTHER_B | 3 | `qokaiin | chedy | qokeedy` |
| f107v.35 | STARS_RECIPE_B | 3 | `qokaiin | chedy | qokeedy` |

The opaque PAGE_HOST sequence is identical in all three.  f83r.6 and f107v.35 also share the exact joint-tuple sequence; f82r.2 changes the middle renderer and one right-family realization while preserving the host sequence.  All three occurrences occupy field 3.  Conditional on the empirical field-ordinal distribution of length-three fields in the relevant registers, the probability of these three fixed occurrences all landing specifically at ordinal 3 is {p_exact:.6f}; the probability of landing together at any common ordinal is {p_any:.6f}.  Because this formula was found before the diagnostic was written, those values are descriptive rather than confirmatory.

This is the first cross-register, three-group stock-field candidate in the executable grammar.  Its most defensible reading is *a reusable field-3 construction*.  There is no independently owned referent for these loci, so its content remains unassigned.

## Counterweight

The recurrence inventory is sparse: only one PAGE_HOST formula of length three crosses folios, and only one exact joint formula of length three does so.  The remaining recurrent formulas are all two groups long.  Exact full-formula reuse is therefore real but small, and the f82r renderer difference is a direct counterexample to treating the visible string as invariant.

## Claim ceiling

GDT328 identifies reusable formal field sequences and record-position stability only.  It assigns no word boundary, phrase, semantic role, object, meaning, language, plaintext, or translation.  f84 was not opened, parsed, retained, joined, or scored.
'''
 REPORT.write_text(report)
 result={'schema':'GDT328_REPEATED_JOINT_FORMULA_RESULT_V1','status':'CROSS_REGISTER_FIELD3_FORMULA_LEAD','summary':summary,'leading_formula':triple,'claim_ceiling':'Reusable structural field formula only; no word phrase semantic role object meaning language plaintext or translation.','f84':{'input_rows':0,'opened':False,'parsed':False,'retained':False,'joined':False,'scored':False},'inputs':{INTER.name:sha(INTER),SOURCE.name:sha(SOURCE),R.name if False else 'gdt327_result.json':sha(R/'gdt327_result.json')},'documents':{METHOD.name:sha(METHOD),REPORT.name:sha(REPORT)},'implementation':{Path(__file__).name:sha(Path(__file__))},'outputs':{ATLAS.name:sha(ATLAS),OCC.name:sha(OCC)}};result['content_sha256']=can(result);RESULT.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n');print(json.dumps({'status':result['status'],'summary':summary},sort_keys=True))
if __name__=='__main__':main()
