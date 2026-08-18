#!/usr/bin/env python3
"""Build the f84-free GDT332 joint-tuple portability atlas."""
import csv,hashlib,json
from collections import defaultdict
from pathlib import Path
R=Path(__file__).resolve().parent;INTER=R/'gdt327_joint_tuple_interlinear.tsv';METHOD=R/'GDT332_JOINT_TUPLE_PORTABILITY_METHOD.md';ATLAS=R/'gdt332_joint_tuple_portability.tsv';SUMMARY=R/'gdt332_layer_portability.tsv';REPORT=R/'GDT332_JOINT_TUPLE_PORTABILITY_REPORT.md';RESULT=R/'gdt332_result.json'
REGS={'HERBAL_A','HERBAL_B','OTHER_A','OTHER_B','STARS_RECIPE_B'}
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def can(v):return hashlib.sha256(json.dumps(v,sort_keys=True,ensure_ascii=True,separators=(',',':')).encode()).hexdigest()
def read(p):
 with Path(p).open(encoding='utf8',newline='') as h:return list(csv.DictReader(h,delimiter='\t'))
def write(p,rows):
 with Path(p).open('w',encoding='utf8',newline='') as h:w=csv.DictWriter(h,rows[0].keys(),delimiter='\t',lineterminator='\n');w.writeheader();w.writerows(rows)
def groups(rows,key):
 d=defaultdict(list)
 for x in rows:d[x[key]].append(x)
 return d
def layer(rows,key,name):
 d=groups(rows,key);n=len(rows)
 def q(pred):z=[v for v in d.values() if pred(v)];return len(z),sum(map(len,z))
 cf=q(lambda v:len({x['physical_folio'] for x in v})>=2);cr=q(lambda v:len({x['register'] for x in v})>=2);cs=q(lambda v:len({x['section'] for x in v})>=2);ch=q(lambda v:len({x['hand'] for x in v})>=2);all5=q(lambda v:{x['register'] for x in v}==REGS);private=q(lambda v:len({x['register'] for x in v})==1);single=q(lambda v:len(v)==1)
 return {'layer':name,'types':len(d),'events':n,'singleton_types':single[0],'singleton_event_mass':single[1],'cross_folio_types':cf[0],'cross_folio_event_mass':cf[1],'cross_folio_event_fraction':f'{cf[1]/n:.12f}','cross_register_types':cr[0],'cross_register_event_mass':cr[1],'cross_register_event_fraction':f'{cr[1]/n:.12f}','cross_section_types':cs[0],'cross_section_event_mass':cs[1],'cross_hand_types':ch[0],'cross_hand_event_mass':ch[1],'all_five_register_types':all5[0],'all_five_register_event_mass':all5[1],'register_private_types':private[0],'register_private_event_mass':private[1]}
def main():
 rows=read(INTER);assert len(rows)==8448 and {x['register'] for x in rows}==REGS and not any(x['page'].startswith('f84') or x['locus'].startswith('f84') for x in rows);d=groups(rows,'joint_tuple_id');atlas=[]
 for ident,v in sorted(d.items()):
  regs={x['register'] for x in v};atlas.append({'joint_tuple_id':ident,'host_id':v[0]['host_id'],'coordinate_id':v[0]['coordinate_id'],'events':len(v),'physical_folios':len({x['physical_folio'] for x in v}),'pages':len({x['page'] for x in v}),'sections':'|'.join(sorted({x['section'] for x in v})),'registers':'|'.join(sorted(regs)),'curriers':'|'.join(sorted({x['currier'] for x in v})),'hands':'|'.join(sorted({x['hand'] for x in v})),'renderer_state':v[0]['renderer_state'],'cross_folio':int(len({x['physical_folio'] for x in v})>=2),'cross_register':int(len(regs)>=2),'cross_section':int(len({x['section'] for x in v})>=2),'cross_hand':int(len({x['hand'] for x in v})>=2),'all_five_registers':int(regs==REGS),'register_private':int(len(regs)==1),'semantic_state':'UNASSIGNED','translation_state':'UNASSIGNED'})
 write(ATLAS,atlas);layers=[layer(rows,'joint_tuple_id','JOINT_TUPLE'),layer(rows,'host_id','PAGE_HOST'),layer(rows,'coordinate_id','COORDINATE')];write(SUMMARY,layers);j=layers[0];status='SHARED_CORE_WITH_REGISTER_LOCAL_TAIL'
 report=f'''# GDT332 — joint-tuple portability atlas

Status: **{status}**.

The f84-free interlinear has {j['types']:,} exact joint tuple identities.  Its type inventory is long-tailed: {j['singleton_types']:,} are singletons.  Event mass, however, is strongly portable:

- {j['cross_folio_event_mass']:,}/{j['events']:,} events ({100*float(j['cross_folio_event_fraction']):.1f}%) use a tuple seen on another physical folio;
- {j['cross_register_event_mass']:,}/{j['events']:,} ({100*float(j['cross_register_event_fraction']):.1f}%) use a tuple spanning at least two registers;
- {j['cross_hand_event_mass']:,}/{j['events']:,} ({100*int(j['cross_hand_event_mass'])/int(j['events']):.1f}%) use a tuple spanning hands;
- only {j['all_five_register_types']} identities occur in all five registers, but they carry {j['all_five_register_event_mass']:,} events ({100*int(j['all_five_register_event_mass'])/int(j['events']):.1f}%);
- {j['register_private_types']:,} identities are register-private, but carry only {j['register_private_event_mass']:,} events ({100*int(j['register_private_event_mass'])/int(j['events']):.1f}%).

This is a compact shared core plus a large low-frequency register-local tail.  It reconciles two earlier results: PAGE_HOSTs recur broadly, but GDT326 shows that unseen host×coordinate edges do not factor productively.  The shared object is therefore an exact joint code state, not an independently compositional host value.

The 53 all-register tuple identities are now the highest-capacity candidates for future external grounding at field/record scale.  Recurrence alone does not identify what any tuple denotes.

No word, morpheme, POS, sound, semantic role, meaning, language, plaintext, or translation is assigned.  No f84 row was opened, retained, joined, or scored.
''';REPORT.write_text(report)
 result={'schema':'GDT332_JOINT_TUPLE_PORTABILITY_RESULT_V1','status':status,'joint_tuple_summary':j,'layer_summaries':layers,'claim_ceiling':'Shared opaque joint codebook architecture only; no word semantic role meaning plaintext or translation.','f84':{'input_rows':0,'opened':False,'retained':False,'joined':False,'scored':False},'inputs':{INTER.name:sha(INTER),R.name if False else 'gdt327_result.json':sha(R/'gdt327_result.json'),R.name if False else 'gdt326_result.json':sha(R/'gdt326_result.json')},'documents':{METHOD.name:sha(METHOD),REPORT.name:sha(REPORT)},'implementation':{Path(__file__).name:sha(Path(__file__))},'outputs':{ATLAS.name:sha(ATLAS),SUMMARY.name:sha(SUMMARY)}};result['content_sha256']=can(result);RESULT.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n');print(json.dumps({'status':status,'summary':j},sort_keys=True))
if __name__=='__main__':main()
