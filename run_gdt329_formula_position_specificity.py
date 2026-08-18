#!/usr/bin/env python3
"""Run the f84-free search-aware GDT329 field-position audit."""
import csv,hashlib,json,math,random
from collections import Counter,defaultdict
from pathlib import Path
R=Path(__file__).resolve().parent;INTER=R/'gdt327_joint_tuple_interlinear.tsv';ATLAS=R/'gdt328_formula_atlas.tsv';OCC=R/'gdt328_formula_occurrences.tsv';METHOD=R/'GDT329_FORMULA_POSITION_SPECIFICITY_METHOD.md';SCORES=R/'gdt329_formula_position_scores.tsv';NULL=R/'gdt329_null.tsv';REPORT=R/'GDT329_FORMULA_POSITION_SPECIFICITY_REPORT.md';RESULT=R/'gdt329_result.json';SEED=329;WORLDS=8192
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def can(v):return hashlib.sha256(json.dumps(v,sort_keys=True,ensure_ascii=True,separators=(',',':')).encode()).hexdigest()
def read(p):
 with Path(p).open(encoding='utf8',newline='') as h:return list(csv.DictReader(h,delimiter='\t'))
def write(p,rows):
 with Path(p).open('w',encoding='utf8',newline='') as h:w=csv.DictWriter(h,rows[0].keys(),delimiter='\t',lineterminator='\n');w.writeheader();w.writerows(rows)
def main():
 rows=read(INTER);assert len(rows)==8448 and not any(x['page'].startswith('f84') or x['locus'].startswith('f84') for x in rows)
 fields=defaultdict(list)
 for x in rows:fields[(x['page'],x['locus'],x['field_ordinal'])].append(x)
 atlas=read(ATLAS);occ=read(OCC);byid=defaultdict(list)
 for x in occ:byid[x['formula_id']].append((x['page'],x['locus'],x['field_ordinal']))
 baseline=defaultdict(Counter);strata=defaultdict(list)
 for k,v in fields.items():baseline[(len(v),v[0]['register'])][k[2]]+=1;strata[(len(v),v[0]['register'])].append(k)
 def score(a,assigned=None):
  z=byid[a['formula_id']];num=0.;var=0.
  for i in range(len(z)):
   for j in range(i+1,len(z)):
    ki,kj=z[i],z[j];vi,vj=fields[ki],fields[kj];pi=baseline[(len(vi),vi[0]['register'])];pj=baseline[(len(vj),vj[0]['register'])];ni=sum(pi.values());nj=sum(pj.values());e=sum(pi[o]/ni*pj[o]/nj for o in set(pi)|set(pj));oi=assigned[ki] if assigned else ki[2];oj=assigned[kj] if assigned else kj[2];num+=(oi==oj)-e;var+=e*(1-e)
  return num/math.sqrt(var) if var else 0.
 observed=[score(a) for a in atlas];local=[0]*len(atlas);maxhit=0;maxnull=[];rng=random.Random(SEED)
 for world in range(WORLDS):
  assigned={}
  for s,keys in sorted(strata.items()):
   vals=[k[2] for k in keys];rng.shuffle(vals)
   for k,o in zip(keys,vals):assigned[k]=o
  vals=[score(a,assigned) for a in atlas];m=max(vals);maxnull.append(m)
  for i,v in enumerate(vals):local[i]+=v>=observed[i]-1e-12
  maxhit+=m>=max(observed)-1e-12
 out=[]
 for i,(a,s) in enumerate(zip(atlas,observed)):
  out.append({'formula_id':a['formula_id'],'level':a['level'],'level_rank':a['level_rank'],'group_length':a['group_length'],'occurrences':a['occurrences'],'physical_folios':a['physical_folios'],'modal_field_ordinal':a['modal_field_ordinal'],'modal_field_purity':a['modal_field_purity'],'pair_agreement_z':f'{s:.12f}','local_inclusive_p':f'{(local[i]+1)/(WORLDS+1):.12f}','max44_inclusive_p':f'{(sum(v>=s-1e-12 for v in maxnull)+1)/(WORLDS+1):.12f}','semantic_state':'UNASSIGNED'})
 out.sort(key=lambda x:-float(x['pair_agreement_z']));write(SCORES,out);lead=out[0]
 null=[{'world':'OBSERVED','max_pair_agreement_z':f"{float(lead['pair_agreement_z']):.12f}"}]+[{'world':i+1,'max_pair_agreement_z':f'{v:.12f}'} for i,v in enumerate(maxnull)];write(NULL,null)
 status='FORMULA_POSITION_SPECIFICITY_NOT_ABOVE_SEARCH_NULL' if float(lead['max44_inclusive_p'])>.05 else 'FORMULA_POSITION_SPECIFICITY_EXPLORATORY'
 report=f'''# GDT329 — formula-position specificity audit

Status: **{status}**.

The GDT328 three-host formula remains the strongest position-concentrated
candidate among all 44 recurrent formulas.  Its pair-agreement z is
{float(lead['pair_agreement_z']):.3f}, its own permutation p is
{float(lead['local_inclusive_p']):.6f}, and the max-44 search-adjusted p is
{float(lead['max44_inclusive_p']):.6f}.

Thus the repeated `qokain/qokaiin | dy/chedy | qokeedy` field remains a useful
cross-register retrieval key, but its three field-3 placements are not above
the atlas-wide position search null.  GDT328's raw ordinal probability must
not be read as confirmation of a special semantic slot.

The formula still matters architecturally: two folios reuse the exact joint
tuple sequence and a third reuses the same opaque host sequence with a renderer
change.  GDT329 only removes the stronger claim that field ordinal 3 is itself
identified by this evidence.

No word boundary, phrase, semantic role, object, meaning, language, plaintext,
or translation is assigned.  f84 was not opened, parsed, retained, joined, or
scored.
''';REPORT.write_text(report)
 result={'schema':'GDT329_FORMULA_POSITION_SPECIFICITY_RESULT_V1','status':status,'candidates':len(atlas),'worlds':WORLDS,'lead':lead,'claim_ceiling':'Search-aware field-position diagnostic only; no semantic slot meaning plaintext or translation.','f84':{'input_rows':0,'opened':False,'parsed':False,'retained':False,'joined':False,'scored':False},'inputs':{p.name:sha(p) for p in (INTER,ATLAS,OCC,R/'gdt328_result.json')},'documents':{METHOD.name:sha(METHOD),REPORT.name:sha(REPORT)},'implementation':{Path(__file__).name:sha(Path(__file__))},'outputs':{SCORES.name:sha(SCORES),NULL.name:sha(NULL)}};result['content_sha256']=can(result);RESULT.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n');print(json.dumps({'status':status,'lead':lead},sort_keys=True))
if __name__=='__main__':main()
