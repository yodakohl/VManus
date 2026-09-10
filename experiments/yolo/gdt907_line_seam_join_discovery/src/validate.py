#!/usr/bin/env python3
"""Independent replay from guarded source caches; no primary runner imports."""
import collections
from fractions import Fraction
import hashlib
import json
from pathlib import Path
import random
import re

E=Path(__file__).resolve().parents[1]
ROOT=E.parents[2]
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def leaf(p):return re.match(r'f[0-9]+',p).group()
def pair(q):return [q.numerator,q.denominator]
def check_edition(ed,binding,spec,rng):
 p=ROOT/binding['path'];assert digest(p)==binding['sha256']
 source=json.loads(p.read_text()); cols=source['group_columns']; allowed=set(spec['allowed_selectors'])
 bypage=collections.defaultdict(dict); vocabulary=collections.defaultdict(list)
 starts=ends=0;plines=0
 for record in source['lines']:
  m=record['metadata'];page=m['page'];assert page in allowed and not page.startswith('f84') and m['edition']==ed
  if m['kind']!='P':continue
  plines+=1;starts+=m['paragraph_start']=='1';ends+=m['paragraph_end']=='1'
  groups=[dict(zip(cols,g)) for g in record['groups']]
  for g in groups:
   word=g['ivtff_group_raw']
   if re.fullmatch('[a-z]+',word):vocabulary[word].append([page,m['locus'],g['source_group_id']])
  match=re.fullmatch(re.escape(page)+r'\.([0-9]+)',m['locus'])
  if not match or not groups:continue
  indices=[int(g['source_group_index']) for g in groups]
  if indices!=list(range(1,len(groups)+1)) or int(m['source_group_count'])!=len(groups):continue
  number=int(match[1]);assert number not in bypage[page]
  bypage[page][number]=(m,groups)
 seams=[]
 for page in sorted(bypage):
  lines=bypage[page];runstart=None
  for number in sorted(lines):
   m,g=lines[number];prev=lines.get(number-1)
   linked=prev is not None and prev[0]['paragraph_end']!='1' and m['paragraph_start']!='1' and m['code'] in ('+P0','+P1') and all(prev[0][key]==m[key] for key in ('hand','section'))
   if not linked:runstart=number;continue
   assert runstart is not None
   a=prev[1][-1];b=g[0]
   if not re.fullmatch('[a-z]+',a['ivtff_group_raw']) or not re.fullmatch('[a-z]+',b['ivtff_group_raw']):continue
   seams.append(dict(A=a['ivtff_group_raw'],B=b['ivtff_group_raw'],id=prev[0]['locus']+'>'+m['locus'],leaf=leaf(page),left_code=prev[0]['code'],left_id=a['source_group_id'],left_locus=prev[0]['locus'],page=page,right_code=m['code'],right_id=b['source_group_id'],right_locus=m['locus'],run_start=runstart))
 strata=collections.defaultdict(list)
 for i,s in enumerate(seams):strata[(s['page'],s['run_start'],len(s['B']))].append(i)
 external={}
 def witnesses(word,home):
  k=(word,home)
  if k not in external:external[k]=sorted(w for w in vocabulary[word] if leaf(w[0])!=home)
  return external[k]
 matrices=[];hits=[];expected=Fraction();diagnostic=Fraction();observed=0;dobs=0;null=[0]*spec['randomizations']
 for key,indices in sorted(strata.items()):
  size=len(indices);matrix=[[int(bool(witnesses(seams[i]['A']+seams[j]['B'],seams[i]['leaf']))) for j in indices] for i in indices]
  exp=Fraction(sum(map(sum,matrix)),size);obs=sum(matrix[i][i] for i in range(size));expected+=exp;observed+=obs
  for i,si in enumerate(indices):
   if len(seams[si]['A'])>=2 and len(seams[si]['B'])>=2:
    diagnostic+=Fraction(sum(matrix[i]),size);dobs+=matrix[i][i]
  matrices.append(dict(bits=[''.join(map(str,r)) for r in matrix],expected=pair(exp),key=list(key),observed=obs,seam_indices=indices))
  for r in range(spec['randomizations']):
   perm=list(range(size));rng.shuffle(perm);null[r]+=sum(matrix[i][perm[i]] for i in range(size))
 for i,s in enumerate(seams):
  whole=s['A']+s['B'];w=witnesses(whole,s['leaf'])
  if w:hits.append(dict(external_witnesses=w,seam_index=i,whole=whole))
 assert observed==len(hits)
 result=dict(both_fragments_at_least_two=dict(expected=float(diagnostic),expected_fraction=pair(diagnostic),observed=dobs),distinct_hit_wholes=len({h['whole'] for h in hits}),eligible_seams=len(seams),excess=float(Fraction(observed)-expected),exchangeable_leaves=len({leaf(k[0]) for k,v in strata.items() if len(v)>1}),exchangeable_strata=sum(len(v)>1 for v in strata.values()),expected=float(expected),expected_fraction=pair(expected),hit_leaves=len({seams[h['seam_index']]['leaf'] for h in hits}),null_max=max(null),null_min=min(null),null_upper_tail=(1+sum(x>=observed for x in null))/(1+len(null)),observed=observed,physical_leaves=len({s['leaf'] for s in seams}),status='EXPLORATORY_SEAM_CENSUS_NO_HYPHENATION_OR_MEANING_IDENTIFICATION',strata=len(strata))
 artifact=E/'artifacts'/f'{ed}.json';actual=json.loads(artifact.read_text())
 for name,value in dict(seams=seams,matrices=matrices,hits=hits,null_scores=null,result=result).items():
  if name=='hits':actual[name]=sorted(actual[name],key=lambda x:x['seam_index'])
  if actual[name]!=value:
   if isinstance(value,list):
    mismatch=next(((i,a,b) for i,(a,b) in enumerate(zip(actual[name],value)) if a!=b),('length',len(actual[name]),len(value)))
   else:mismatch=(actual[name],value)
   raise AssertionError((ed,name,mismatch))
 print(json.dumps({'edition':ed,'status':'PASS','seams':len(seams),'hits':len(hits)}),flush=True)
 return {'edition':ed,'source_sha256':binding['sha256'],'artifact_sha256':digest(artifact),'seams':len(seams),'matrices':len(matrices),'all_null_scores_exact':len(null),'result':result,'kind_P_lines':plines,'paragraph_start_flags':starts,'paragraph_end_flags':ends},seams,hits

def main():
 specpath=E/'src/SPEC.json';spec=json.loads(specpath.read_text());assert len(set(spec['allowed_selectors']))==179 and set(spec['sealed_data'])=={'f84','f84r'}
 rng=random.Random(spec['seed']);checks=[];views={}
 for ed,binding in spec['sources'].items():
  check,seams,hits=check_edition(ed,binding,spec,rng);checks.append(check);views[ed]=(seams,hits)
 combined=json.loads((E/'artifacts/RESULT.json').read_text())
 assert combined['readings']=={r['edition']:r['result'] for r in checks}
 hit_maps={ed:{ss[h['seam_index']]['id']:(ss[h['seam_index']]['A'],ss[h['seam_index']]['B']) for h in hs} for ed,(ss,hs) in views.items()}
 common=set.intersection(*(set(m) for m in hit_maps.values()))
 identical=sorted(k for k in common if len({m[k] for m in hit_maps.values()})==1)
 assert combined['all_three_hit_locus_pairs']==sorted(common)
 assert combined['all_three_same_fragment_pairs']==identical
 out={'status':'PASS','validator_sha256':digest(Path(__file__)),'spec_sha256':digest(specpath),'editions':checks,'rng_serialization':'One Random(907); SPEC edition insertion order, sorted strata, then replicate; fresh index list including singleton strata.','claim_ceiling':'Exploratory dependence of concatenated raw strings across source-defined line runs only. Native gaps are not fully known; RF paragraph flags have different granularity. Neither hyphenation, word identity nor meaning is established.'}
 (E/'artifacts/VALIDATION.json').write_text(json.dumps(out,indent=2)+'\n')
if __name__=='__main__':main()
