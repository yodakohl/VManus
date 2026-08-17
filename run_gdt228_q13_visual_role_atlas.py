#!/usr/bin/env python3
"""Score two disclosed human-catalogue visual axes against abstract q13 roles."""
import csv,hashlib,itertools,json,math,random
from collections import defaultdict
from pathlib import Path
R=Path(__file__).resolve().parent;MAN=R/'gdt228_visual_feature_manifest.tsv';INTER=R/'gdt227_q13_abstract_interlinear.tsv';OLD=R/'gdt227_result.json';SOURCE=R/'experiments/semantic_assumptions/results/existing_human_page_annotations.tsv';METHOD=R/'GDT228_Q13_VISUAL_ROLE_ATLAS_METHOD.md';REPORT=R/'GDT228_Q13_VISUAL_ROLE_ATLAS_REPORT.md';PAGES=R/'gdt228_page_role_profiles.tsv';SCORES=R/'gdt228_visual_role_scores.tsv';NULL=R/'gdt228_null_results.tsv';COUNTER=R/'gdt228_counterexamples.tsv';RESULT=R/'gdt228_result.json';FEATURES=('multiple_bounded_regions','explicit_linear_path');ROLES=('INSTRUCTION_CLAUSE_LIKE','SHORT_ARGUMENT_LIKE','RECORD_CLOSER_LIKE')
def read(p):
 with p.open(encoding='utf8',newline='') as h:return list(csv.DictReader(h,delimiter='\t'))
def write(p,rows):
 with p.open('w',encoding='utf8',newline='') as h:w=csv.DictWriter(h,fieldnames=list(rows[0]),delimiter='\t',lineterminator='\n');w.writeheader();w.writerows(rows)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def csha(v):return hashlib.sha256(json.dumps(v,sort_keys=True,separators=(',',':'),ensure_ascii=True).encode()).hexdigest()
def effect(vals,state):
 a=[vals[p] for p in vals if state[p]];b=[vals[p] for p in vals if not state[p]];return sum(a)/len(a)-sum(b)/len(b)
def main():
 man=read(MAN);assert len(man)==18 and not any(x['page'].startswith('f84') for x in man);state={f:{x['page']:int(x[f]) for x in man} for f in FEATURES};rows=read(INTER);assert not any(x['page'].startswith('f84') for x in rows);by=defaultdict(list)
 for x in rows:by[x['page']].append(x)
 assert set(by)=={x['page'] for x in man};profiles=[];vals={r:{} for r in ROLES}
 for x in man:
  p=x['page'];z=by[p];row={'page':p,'physical_folio':x['physical_folio'],'fields':len(z),**{f:x[f] for f in FEATURES}}
  for role in ROLES:
   v=sum(y['abstract_role_like']==role for y in z)/len(z);vals[role][p]=v;row[role.lower()+'_fraction']=f'{v:.12g}'
  profiles.append(row)
 pages=sorted(by);scores=[];worlds_by={};within={};lofo={}
 for f in FEATURES:
  k=sum(state[f].values());assign=[]
  for comb in itertools.combinations(pages,k):
   st={p:int(p in comb) for p in pages};assign.append(st)
  worlds_by[f]=assign
  disc=[]
  for folio in sorted({x['physical_folio'] for x in man}):
   pp=sorted(x['page'] for x in man if x['physical_folio']==folio)
   if len(pp)==2 and state[f][pp[0]]!=state[f][pp[1]]:disc.append(pp)
  for role in ROLES:
   obs=effect(vals[role],state[f]);ww=[effect(vals[role],s) for s in assign];p2=sum(abs(x)>=abs(obs)-1e-15 for x in ww)/len(ww)
   sw=[]
   for bits in itertools.product((0,1),repeat=len(disc)):
    st=dict(state[f])
    for pp,b in zip(disc,bits):st[pp[0]]=int(b==0);st[pp[1]]=int(b==1)
    sw.append(effect(vals[role],st))
   wp=sum(abs(x)>=abs(obs)-1e-15 for x in sw)/len(sw) if sw else 1
   hits=0
   for folio in sorted({x['physical_folio'] for x in man}):
    keep={p:v for p,v in vals[role].items() if not p.startswith(folio)};ss={p:state[f][p] for p in keep};hits+=effect(keep,ss)*obs>0
   scores.append({'visual_feature':f,'abstract_role':role,'positive_pages':k,'negative_pages':len(pages)-k,'observed_effect':f'{obs:.12g}','exact_page_worlds':len(ww),'exact_two_sided_p':f'{p2:.12g}','discordant_folios':len(disc),'within_folio_worlds':len(sw),'within_folio_two_sided_p':f'{wp:.12g}','lofo_same_direction':hits,'lofo_total':len({x["physical_folio"] for x in man})})
 # Deterministic familywise diagnostic over exactly the six disclosed tests.
 rng=random.Random(228);obs=[float(x['observed_effect']) for x in scores];samples=[[] for _ in scores]
 for _ in range(4096):
  pos={}
  for f in FEATURES:
   pp=pages[:];rng.shuffle(pp);pos[f]={p:int(p in set(pp[:sum(state[f].values())])) for p in pages}
  for i,x in enumerate(scores):samples[i].append(effect(vals[x['abstract_role']],pos[x['visual_feature']]))
 means=[sum(x)/len(x) for x in samples];sd=[(sum((v-m)**2 for v in x)/len(x))**.5 or 1 for x,m in zip(samples,means)];oz=[abs((v-m)/s) for v,m,s in zip(obs,means,sd)];mx=[]
 for j in range(4096):mx.append(max(abs((samples[i][j]-means[i])/sd[i]) for i in range(len(scores))))
 for i,x in enumerate(scores):x['max_six_p']=f'{sum(v>=oz[i]-1e-15 for v in mx)/len(mx):.12g}'
 null=[{'visual_feature':x['visual_feature'],'abstract_role':x['abstract_role'],'exact_page_worlds':x['exact_page_worlds'],'exact_two_sided_p':x['exact_two_sided_p'],'within_folio_worlds':x['within_folio_worlds'],'within_folio_two_sided_p':x['within_folio_two_sided_p'],'max_six_worlds':4096,'max_six_p':x['max_six_p']} for x in scores]
 top=max(scores,key=lambda x:abs(float(x['observed_effect'])));status='MULTI_REGION_SHORT_ARGUMENT_LEAD_POSTSELECTED_LOW_CAPACITY' if top['visual_feature']=='multiple_bounded_regions' and ((top['abstract_role']=='SHORT_ARGUMENT_LIKE' and float(top['observed_effect'])>0) or (top['abstract_role']=='INSTRUCTION_CLAUSE_LIKE' and float(top['observed_effect'])<0)) else 'NO_COHERENT_VISUAL_ROLE_LEAD'
 counter=[{'counterexample':'POSTSELECTED_AXES','value':'2_AXES_6_ENDPOINTS','detail':'Both axes and their scratch effects were inspected before the public method.'},{'counterexample':'LOCAL_NULL','value':f"{top['exact_two_sided_p']}",'detail':'The strongest lead does not reach a conventional two-sided local threshold.'},{'counterexample':'WITHIN_FOLIO_CAPACITY','value':f"{top['discordant_folios']}_DISCORDANT_FOLIOS_P_{top['within_folio_two_sided_p']}",'detail':'Only three folios distinguish the multiple-region state between recto and verso.'},{'counterexample':'ROLE_PROJECTION','value':'POSITION_LENGTH_ONLY','detail':'The endpoint is an abstract role likeness, not readable hydraulic text.'},{'counterexample':'PAGE_LEVEL_JOIN','value':'NO_FIELD_OWNERSHIP','detail':'A page-level visual state does not attach a role to any specific field.'},{'counterexample':'MULTIPLE_REGIONS_NOT_PROCESS','value':'VISIBLE_GEOMETRY_ONLY','detail':'Separate bounded regions need not be stages, ingredients, locations, or baths.'}]
 write(PAGES,profiles);write(SCORES,scores);write(NULL,null);write(COUNTER,counter)
 result={'schema':'GDT228_Q13_VISUAL_ROLE_ATLAS_RESULT_V1','status':status,'postselection':'FULLY_DISCLOSED_TWO_AXES_SIX_ENDPOINTS','pages':18,'physical_folios':9,'fields':len(rows),'top_lead':top,'interpretation':'Pages with multiple human-described bounded regions have a weak excess of short-argument-like fields; this is a page-level organization hypothesis only.','claim_ceiling':'Page-level visual geometry to abstract role-likeness association only; no field ownership host meaning word language plaintext or translation.','f84':{'public_metadata_previously_exposed':True,'manifest_rows':0,'source_or_formal_payload_retained':False,'joined':False,'scored':False,'future_access_authorized':False},'inputs':{str(p.relative_to(R)):sha(p) for p in (MAN,INTER,OLD,SOURCE)},'implementation':{Path(__file__).name:sha(Path(__file__))},'outputs':{p.name:sha(p) for p in (PAGES,SCORES,NULL,COUNTER)},'documents':{METHOD.name:sha(METHOD),REPORT.name:sha(REPORT)}};result['result_content_sha256']=csha(result);RESULT.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n');print(json.dumps({'status':status,'top':top},sort_keys=True))
if __name__=='__main__':main()
