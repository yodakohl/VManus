#!/usr/bin/env python3
"""Freeze outcome-blind GDT303 matched-operation capacity."""
import csv,hashlib,itertools,json
from collections import Counter,defaultdict
from pathlib import Path
R=Path(__file__).resolve().parent;S=R/'gdt278_native_event_inventory.tsv';M=R/'GDT303_RENDERER_OPERATION_POSITION_DELTA_METHOD.md';C=R/'gdt303_capacity.tsv';D=R/'gdt303_design.json';F=R/'gdt303_freeze_manifest.tsv';FIELDS=['wrapper','local_frame','inner_d','right_family','dy_closure','b3'];ART=['gdt302_result.json','gdt301_result.json','gdt300_result.json','gdt299_result.json','gdt278_native_event_inventory.tsv']
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def can(v):return hashlib.sha256(json.dumps(v,sort_keys=True,ensure_ascii=True,separators=(',',':')).encode()).hexdigest()
def read(p):
 with Path(p).open(encoding='utf8',newline='') as h:return list(csv.DictReader(h,delimiter='\t'))
def write(p,rows):
 with Path(p).open('w',encoding='utf8',newline='') as h:w=csv.DictWriter(h,rows[0].keys(),delimiter='\t',lineterminator='\n');w.writeheader();w.writerows(rows)
def population(rows):
 b=[x for x in rows if x['control_id']=='VOYNICH_REFERENCE' and int(x['group_count'])>=2];hf=defaultdict(set);sf=defaultdict(set)
 for x in b:hf[x['page_host']].add(x['physical_folio']);sf[x['source_surface_sha256']].add(x['physical_folio'])
 return [x for x in b if len(hf[x['page_host']])>1 and len(sf[x['source_surface_sha256']])>1]
def enumerate_pairs(E):
 forms=defaultdict(lambda:defaultdict(list))
 for x in E:forms[x['page_host']][x['source_surface_sha256']].append(x)
 ans=[]
 for h,D in forms.items():
  ok=[]
  for s,v in D.items():
   if len(v)>=5 and len({x['physical_folio'] for x in v})>=3:ok.append((s,tuple(v[0][k] for k in FIELDS),v))
  for a,b in itertools.combinations(ok,2):
   q=[i for i,(x,y) in enumerate(zip(a[1],b[1])) if x!=y]
   if len(q)!=1:continue
   i=q[0];va,vb=a[1][i],b[1][i]
   if va in ('NONE','0') and vb not in ('NONE','0'):src,tgt=a,b
   elif vb in ('NONE','0') and va not in ('NONE','0'):src,tgt=b,a
   elif va<vb:src,tgt=a,b
   else:src,tgt=b,a
   ans.append({'operation':f'{FIELDS[i]}:{src[1][i]}>{tgt[1][i]}','field':FIELDS[i],'source_value':src[1][i],'target_value':tgt[1][i],'page_host':h,'source_surface_sha256':src[0],'target_surface_sha256':tgt[0],'source_events':len(src[2]),'target_events':len(tgt[2])})
 return ans
def main():
 rows=read(S);assert not any(x['page'].startswith('f84') or x['locus'].startswith('f84') for x in rows);P=enumerate_pairs(population(rows));c=Counter(x['operation'] for x in P);h=defaultdict(set)
 for x in P:h[x['operation']].add(x['page_host'])
 cap=[{'operation':o,'pairs':c[o],'hosts':len(h[o]),'capacity':'POWERED' if c[o]>=4 and len(h[o])>=4 else 'UNSCORED'} for o in sorted(c)];write(C,cap);write(F,[{'artifact':x,'frozen_sha256':sha(R/x)} for x in ART]);d={'schema':'GDT303_RENDERER_OPERATION_POSITION_DELTA_DESIGN_V1','status':'FROZEN_BEFORE_GDT303_POSITION_SCORING','population':'EXACT_GDT299_6844_EVENTS','renderer_fields':FIELDS,'form_min_events':5,'form_min_folios':3,'pair_difference_fields':1,'direction':'NEUTRAL_NONE_OR_0_TO_NONNEUTRAL_ELSE_LEXICAL','operation_min_pairs':4,'operation_min_hosts':4,'prediction':'LOHO_EQUAL_HOST_MEAN_THREE_ROLE_DELTA','baseline':'ZERO_DELTA','loss':'SUM_SQUARED_ERROR','null_worlds':4096,'null_seed':'GDT303_OPERATION_HOST_SIGN_REVERSAL_V1','null':'INDEPENDENT_OPERATION_HOST_VECTOR_SIGN_REVERSAL','decision':{'transfer':'TRANSFERRED_DELTA','weak':'WEAK_DELTA','fail':'FAILED_DELTA','minimum_direction_accuracy':.7,'max_family_p_le':.05},'semantic_assignments':0,'claim_ceiling':'Reusable renderer-field physical-position delta across opaque hosts only; no morpheme grammatical function semantic role sound language meaning plaintext or translation.','f84':{'input_files':0,'opened':False,'parsed':False,'retained':False,'joined':False,'scored':False},'capacity_sha256':sha(C),'freeze_manifest_sha256':sha(F),'method_sha256':sha(M),'implementation':{Path(__file__).name:sha(Path(__file__))}};d['content_sha256']=can(d);D.write_text(json.dumps(d,indent=2,sort_keys=True)+'\n');print(json.dumps({'status':d['status'],'pairs':len(P),'powered':sum(x['capacity']=='POWERED' for x in cap)},sort_keys=True))
if __name__=='__main__':main()
